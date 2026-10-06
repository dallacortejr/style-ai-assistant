"""Fronteiras reais HTTP de contas, cookies, CSRF e material de consultoria."""
import json
import sqlite3
import time
from urllib.parse import quote
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend import store, intelligence, auth

PASSWORD = "senha-ficticia-para-testes-2026"


@pytest.fixture
def accounts(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB", tmp_path / "saas.sqlite3")
    monkeypatch.setattr(intelligence, "ROOT", tmp_path)
    monkeypatch.setenv("SAAS_ENFORCE_SUBSCRIPTION", "false")
    clients = []
    for name in ("A", "B"):
        c = TestClient(app)
        r = c.post("/auth/register", json={"name": "Consultor " + name, "email": name.lower()+"@example.invalid", "password": PASSWORD})
        assert r.status_code == 201
        c.headers["X-CSRF-Token"] = r.json()["csrf"]
        clients.append(c)
    return clients


def seeded(c):
    assert c.post("/demo/seeds").status_code == 200
    return c.get("/sessions").json()[0]


def approved(c):
    s = seeded(c)
    url = f'/sessions/{s["id"]}/pages/' + quote("Perfil e objetivo de imagem")
    s = c.put(url, json={"revision": 0, "texto": "Texto fictício revisado pelo profissional."}).json()
    s = c.post(url+"/decision", json={"revision": s["revision"], "decisao": "aprovar"}).json()
    r = c.post(url+"/library", json={"revision": s["revision"], "titulo": "Exemplo editorial", "tema": "visagismo", "texto": "Linhas curvas e angulares ajudam a explicar o equilíbrio visual do rosto.", "confirmo_padrao_sem_dados_pessoais": True})
    assert r.status_code == 201
    return s, url, r.json()


def test_anonymous_cannot_access_data(accounts):
    c = TestClient(app)
    for path in ("/sessions", "/catalog", "/library", "/library/dataset", "/traces", "/knowledge", "/auth/me"):
        assert c.get(path).status_code == 401
    assert c.post("/demo/seeds").status_code == 401
    assert c.get("/health").status_code == 200


def test_empty_accounts_and_optional_demo(accounts):
    a, b = accounts
    assert a.get("/sessions").json() == b.get("/sessions").json() == []
    seeded(a)
    assert len(a.get("/sessions").json()) == 8
    assert b.get("/sessions").json() == []
    a.post("/demo/seeds")
    assert len(a.get("/sessions").json()) == 8


def test_password_and_cookie_storage(accounts):
    a, _ = accounts
    r = a.post("/auth/login", json={"email": " A@EXAMPLE.INVALID ", "password": PASSWORD})
    assert r.status_code == 200
    cookie = r.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie
    with auth.connect() as con:
        encoded = con.execute("SELECT password FROM consultants LIMIT 1").fetchone()[0]
        tokens = [r[0] for r in con.execute("SELECT token FROM auth_sessions")]
    assert PASSWORD not in encoded and encoded.startswith("scrypt$131072$8$1$")
    assert a.cookies.get(auth.COOKIE) not in tokens
    assert "password" not in r.json()["consultant"]
    assert "token" not in r.json()


def test_bad_login_duplicate_and_session_rotation(accounts):
    a, _ = accounts
    old_cookie = a.cookies.get(auth.COOKIE)
    assert a.post("/auth/login", json={"email": "a@example.invalid", "password": "incorreta-ficticia"}).status_code == 401
    assert a.post("/auth/register", json={"name": "Duplicado", "email": "A@example.invalid", "password": PASSWORD}).status_code == 409
    r = a.post("/auth/login", json={"email": "a@example.invalid", "password": PASSWORD})
    a.headers["X-CSRF-Token"] = r.json()["csrf"]
    old = TestClient(app)
    old.cookies.set(auth.COOKIE, old_cookie)
    assert old.get("/sessions").status_code == 401
    assert a.post("/auth/logout").status_code == 200
    assert a.get("/auth/me").status_code == 401


def test_csrf_and_forged_origin(accounts):
    a, _ = accounts
    csrf = a.headers.pop("X-CSRF-Token")
    assert a.post("/demo/seeds").status_code == 403
    a.headers["X-CSRF-Token"] = csrf
    assert a.post("/demo/seeds", headers={"Origin": "https://evil.invalid"}).status_code == 403
    assert a.post("/auth/login", headers={"Origin": "https://evil.invalid"}, json={"email": "a@example.invalid", "password": PASSWORD}).status_code == 403
    assert a.post("/demo/seeds", headers={"Origin": "http://127.0.0.1:3000"}).status_code == 200


def test_expired_session(accounts):
    a, _ = accounts
    with auth.connect() as con:
        con.execute("UPDATE auth_sessions SET expires=? WHERE token=?", (time.time()-1, auth.digest(a.cookies.get(auth.COOKIE))))
    assert a.get("/sessions").status_code == 401


def test_tenant_cannot_read_write_export_or_chat(accounts):
    a, b = accounts
    s, url, _ = approved(a)
    sid = s["id"]
    for path in (f"/sessions/{sid}", f"/sessions/{sid}/references", f"/sessions/{sid}/export"):
        assert b.get(path).status_code == 404
    assert b.put(url, json={"revision": s["revision"], "texto": "Tentativa"}).status_code == 404
    assert b.post(url+"/decision", json={"revision": s["revision"], "decisao": "aprovar"}).status_code == 404
    assert b.post("/chat", json={"pergunta": "Como organizar o dossiê?", "sessao_id": sid}).status_code == 404
    assert a.get(f"/sessions/{sid}").json()["revision"] == s["revision"]


def test_library_dataset_model_and_revocation_are_private(accounts):
    a, b = accounts
    s, url, record = approved(a)
    assert len(a.get("/library").json()["trechos"]) == 1
    assert b.get("/library").json()["trechos"] == []
    assert b.get("/library/dataset").json()["registros"] == []
    assert b.get("/library").json()["status"]["modelo"] is None
    assert b.post(f'/library/{record["id"]}/revoke').status_code == 404
    assert a.get("/library").json()["trechos"][0]["ativa"]
    assert b.post(url+"/library", json={"revision": s["revision"], "titulo": "Outra", "tema": "visagismo", "texto": "Um padrão editorial suficientemente longo para revisão do profissional.", "confirmo_padrao_sem_dados_pessoais": True}).status_code == 404


def test_profiles_subscription_and_no_simulated_checkout(accounts, monkeypatch):
    a, b = accounts
    assert a.put("/auth/profile", json={"name": "Novo nome profissional"}).status_code == 200
    assert a.get("/auth/me").json()["consultant"]["name"] == "Novo nome profissional"
    assert b.get("/auth/me").json()["consultant"]["name"] == "Consultor B"
    assert a.put("/auth/profile", json={"name": "Teste", "subscription": "active"}).status_code == 422
    assert a.post("/billing/checkout").status_code == 503
    assert a.get("/auth/me").json()["consultant"]["subscription"]["status"] == "pilot"
    monkeypatch.setenv("SAAS_ENFORCE_SUBSCRIPTION", "true")
    assert a.get("/sessions").status_code == 402
    assert a.get("/auth/me").status_code == 200
    assert a.post("/auth/logout").status_code == 200


def test_legacy_rows_are_preserved_without_public_claim(accounts):
    a, b = accounts
    legacy = {"id": "OLD", "identificador": "Cliente LEGADO", "paginas": {"privado": "Texto anterior"}}
    with store.connect() as con:
        con.execute("INSERT INTO sessions VALUES (?,?,NULL)", ("OLD", json.dumps(legacy)))
    assert a.get("/sessions/OLD").status_code == b.get("/sessions/OLD").status_code == 404
    with store.connect() as con:
        assert json.loads(con.execute("SELECT body FROM sessions WHERE id='OLD'").fetchone()[0]) == legacy


def test_rate_limit_is_enforced(accounts):
    a, _ = accounts
    with auth.connect() as con:
        con.executemany("INSERT INTO auth_attempts VALUES (?,?)", [("testclient", time.time())]*15)
    assert a.post("/auth/login", json={"email": "a@example.invalid", "password": PASSWORD}).status_code == 429


def test_trace_files_are_private(accounts, tmp_path):
    a, b = accounts
    owner = a.get("/auth/me").json()["consultant"]["id"]
    path = tmp_path / "runtime" / "tenants" / owner / "traces.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"id": "trace-private"})+"\n")
    assert a.get("/traces").json()[0]["id"] == "trace-private"
    assert b.get("/traces").json() == []


def test_trained_models_and_identical_patterns_are_scoped(accounts):
    a, b = accounts
    s, url, _ = approved(a)
    # A mesma referência autorizada também pode existir em outro estúdio.
    approved(b)
    second = a.post(url+"/library", json={"revision": s["revision"], "titulo": "Paleta e contraste", "tema": "coloracao", "texto": "Contraste e temperatura organizam a seleção de uma paleta de cores coerente.", "confirmo_padrao_sem_dados_pessoais": True})
    assert second.status_code == 201
    assert a.post("/library/train").json()["pronto"]
    assert b.get("/library").json()["status"]["modelo"] is None
    assert b.get("/library/search?q=contraste").json()["trechos"] == []
    assert a.get("/library/search?q=contraste").json()["trechos"]


def test_simultaneous_requests_preserve_owner_context(accounts):
    from concurrent.futures import ThreadPoolExecutor
    a, b = accounts
    with ThreadPoolExecutor(max_workers=2) as executor:
        jobs = [executor.submit(c.post, "/sessions", json={"identificador": "Cliente " + name, "modo": "feminino", "pacote": "pacote_1", "objetivo": "Objetivo exclusivo."}) for c, name in ((a, "A"), (b, "B"))]
        assert all(job.result().status_code == 201 for job in jobs)
    assert [s["identificador"] for s in a.get("/sessions").json()] == ["Cliente A"]
    assert [s["identificador"] for s in b.get("/sessions").json()] == ["Cliente B"]


def test_previous_schema_migrates_without_assigning_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB", tmp_path / "old.sqlite3")
    with sqlite3.connect(store.DB) as con:
        con.execute("CREATE TABLE sessions (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
        con.execute("INSERT INTO sessions VALUES ('OLD',?)", (json.dumps({"id": "OLD", "texto": "preservado"}),))
        con.execute("CREATE TABLE editorial (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
        con.execute("INSERT INTO editorial VALUES ('OLDREF',?)", (json.dumps({"id": "OLDREF", "texto": "preservado"}),))
    c = TestClient(app)
    r = c.post("/auth/register", json={"name": "Nova conta", "email": "nova@example.invalid", "password": PASSWORD})
    assert r.status_code == 201
    assert c.get("/sessions").json() == []
    assert c.get("/library").json()["trechos"] == []
    with store.connect() as con:
        assert con.execute("SELECT consultant_id FROM sessions WHERE id='OLD'").fetchone()[0] is None
        assert json.loads(con.execute("SELECT body FROM editorial WHERE id='OLDREF'").fetchone()[0])["texto"] == "preservado"


def test_administrative_transfer_requires_apply_and_preserves_other_owner(accounts):
    import os
    import subprocess
    import sys
    from pathlib import Path
    a, b = accounts
    other = seeded(b)
    with store.connect() as con:
        con.execute("INSERT INTO sessions VALUES (?,?,NULL)", ("LEGACY", json.dumps({"id": "LEGACY", "identificador": "Cliente LEGADO"})))
    script = Path(__file__).resolve().parents[1] / "scripts" / "migrate-legacy.py"
    env = dict(os.environ, APP_DB=str(store.DB))
    dry = subprocess.run([sys.executable, str(script), "--email", "a@example.invalid"], env=env, capture_output=True, text=True)
    assert dry.returncode == 0, dry.stderr
    assert a.get("/sessions/LEGACY").status_code == 404
    applied = subprocess.run([sys.executable, str(script), "--email", "a@example.invalid", "--apply"], env=env, capture_output=True, text=True)
    assert applied.returncode == 0, applied.stderr
    assert a.get("/sessions/LEGACY").status_code == 200
    assert b.get("/sessions/LEGACY").status_code == 404
    assert b.get(f'/sessions/{other["id"]}').status_code == 200
    assert a.get(f'/sessions/{other["id"]}').status_code == 404
