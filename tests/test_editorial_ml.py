"""Corpus fictício mínimo para testar o fluxo, não medir qualidade do modelo."""
from urllib.parse import quote
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend import store, intelligence, library


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB", tmp_path / "library.sqlite3")
    monkeypatch.setattr(intelligence, "ROOT", tmp_path)
    monkeypatch.setenv("RAG_MODE", "lexical")
    c = TestClient(app)
    result = c.post("/auth/register", json={"name": "Consultor Fictício", "email": "teste@example.invalid", "password": "senha-ficticia-testes-2026"}).json()
    c.headers["X-CSRF-Token"] = result["csrf"]
    c.post("/demo/seeds")
    context = store.tenant.set(result["consultant"]["id"])
    try:
        yield c
    finally:
        store.tenant.reset(context)


def prepare(client):
    s = client.get("/sessions").json()[0]
    url = f'/sessions/{s["id"]}/pages/' + quote("Perfil e objetivo de imagem")
    s = client.put(url, json={"revision": s["revision"], "texto": "Texto final fictício revisado para testar o fluxo."}).json()
    s = client.post(url + "/decision", json={"revision": s["revision"], "decisao": "aprovar"}).json()
    return s, url


def payload(s, text="Linhas curvas e angulares ajudam a explicar o equilíbrio visual do rosto no visagismo."):
    return {"revision": s["revision"], "titulo": "Equilíbrio visual", "tema": "visagismo", "texto": text,
            "confirmo_padrao_sem_dados_pessoais": True}


def populate(client):
    s, url = prepare(client)
    a = client.post(url + "/library", json=payload(s)).json()
    p = payload(s, "A intenção de imagem deve refletir os objetivos profissionais, a rotina e a mensagem que se deseja comunicar.")
    p.update(titulo="Intenção de imagem", tema="perfil")
    b = client.post(url + "/library", json=p).json()
    assert "id" in a and "id" in b
    return a, b


def test_library_starts_empty_and_untrained(client):
    assert client.get("/library").json()["trechos"] == []
    assert not client.get("/library").json()["status"]["pronto"]
    assert client.post("/library/train").status_code == 422


def test_pattern_requires_approved_page_and_explicit_review(client):
    s = client.get("/sessions").json()[0]
    url = f'/sessions/{s["id"]}/pages/' + quote("Perfil e objetivo de imagem")
    assert client.post(url + "/library", json=payload(s)).status_code == 422
    s, url = prepare(client)
    p = payload(s); p["confirmo_padrao_sem_dados_pessoais"] = False
    assert client.post(url + "/library", json=p).status_code == 422


@pytest.mark.parametrize("private", ["Cliente A prefere estas linhas para seu novo rosto.", "Contato: pessoa@example.com para explicar as linhas do rosto.", "CPF 123.456.789-10 registrado neste padrão de análise facial."])
def test_identifiers_rejected_in_reusable_library(client, private):
    s, url = prepare(client)
    assert client.post(url + "/library", json=payload(s, private)).status_code == 422
    assert client.get("/library").json()["trechos"] == []


def test_training_and_ml_ranking_exclude_origin_and_irrelevant_query(client):
    a, b = populate(client)
    assert client.get("/library/search", params={"q": "linhas rosto visagismo"}).json()["trechos"] == []
    status = client.post("/library/train").json()
    assert status["pronto"] and status["modelo"]["trechos"] == 2
    assert status["modelo"]["metricas_validacao"] is None
    hits = client.get("/library/search", params={"q": "linhas rosto visagismo"}).json()["trechos"]
    assert hits[0]["id"] == a["id"]
    assert "origem" not in hits[0] and "sessao_id" not in str(hits)
    assert client.get("/library/search", params={"q": "astronomia orbitas planetas"}).json()["trechos"] == []
    assert "origem" not in str(client.get("/library/dataset").json()["registros"])


def test_revocation_immediately_prevents_stale_model_reuse(client):
    a, _ = populate(client)
    client.post("/library/train")
    client.post(f'/library/{a["id"]}/revoke')
    result = client.get("/library/search", params={"q": "linhas rosto visagismo"}).json()
    assert result["status"]["desatualizado"] and not result["status"]["pronto"]
    assert result["trechos"] == []


def test_curated_pattern_is_used_in_chat_as_reference_not_client_record(client, monkeypatch):
    a, _ = populate(client)
    client.post("/library/train")
    prompts = []
    def fake(prompt):
        prompts.append(prompt)
        return "Rascunho para revisão profissional.", {"input": 10, "output": 6}
    monkeypatch.setattr(intelligence, "llm", fake)
    s = client.get("/sessions").json()[1]
    result = intelligence.consult("Explique linhas do rosto no visagismo", s["id"])
    assert any(a["id"] in source["fonte"] for source in result["fontes"])
    assert a["texto"] in prompts[0]
    assert a["origem"]["sessao_id"] not in prompts[0]
    assert not any(p["aprovada"] for p in store.get(s["id"])["paginas"].values())
