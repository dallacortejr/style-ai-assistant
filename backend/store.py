"""Persistência local e transacional. IA não possui função de aprovação."""
import csv
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from contextvars import ContextVar
from academic import pacotes

ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.getenv("APP_DB", str(ROOT / "runtime" / "atendimentos.sqlite3")))
tenant = ContextVar("consultant_id", default=None)


def owner():
    value = tenant.get()
    if not value:
        raise RuntimeError("Uma conta autenticada é necessária.")
    return value


def now():
    return datetime.now(timezone.utc).isoformat()


def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB, timeout=10)
    con.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, body TEXT NOT NULL, consultant_id TEXT)")
    if "consultant_id" not in {r[1] for r in con.execute("PRAGMA table_info(sessions)")}:
        con.execute("ALTER TABLE sessions ADD COLUMN consultant_id TEXT")
    con.execute("CREATE INDEX IF NOT EXISTS sessions_owner ON sessions(consultant_id)")
    return con


def seeds():
    def read(name):
        with (ROOT / "academic" / "data" / f"{name}.csv").open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    clients = {c["cliente_id"]: c for c in read("clientes")}
    tables = {t: {r["sessao_id"]: r for r in read(t)} for t in
              ("temperamento", "visagismo", "medidas", "teste_coloracao", "coloracao")}
    result = []
    for row in read("sessoes"):
        c = clients[row["cliente_id"]]
        result.append(new_session(row["sessao_id"], c["identificador"], c["modo"], row["pacote"],
                                  c["objetivo_imagem"], row["data_sessao"],
                                  {t: {k: v for k, v in rows[row["sessao_id"]].items() if k != "sessao_id"}
                                   for t, rows in tables.items()}))
    return result


def new_session(sid, identificador, modo, pacote, objetivo, data=None, avaliacao=None):
    if pacote not in pacotes.PACOTES:
        raise ValueError("Pacote desconhecido.")
    return {"id": sid, "identificador": identificador, "modo": modo, "pacote": pacote,
            "data": data or now()[:10], "revision": 0, "questionario": {"objetivo": objetivo},
            "avaliacao": avaliacao or {}, "paginas": {}, "chat": [], "audit": [], "fotos": {}, "referencias": []}


def initialize():
    """Exemplos são opcionais e pertencem somente à conta que os solicita."""
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        if not con.execute("SELECT COUNT(*) FROM sessions WHERE consultant_id=?", (owner(),)).fetchone()[0]:
            for s in seeds():
                s["id"] = owner() + "-" + s["id"]
                con.execute("INSERT INTO sessions VALUES (?,?,?)", (s["id"], json.dumps(s), owner()))


def list_sessions():
    with connect() as con:
        return [json.loads(r[0]) for r in con.execute("SELECT body FROM sessions WHERE consultant_id=? ORDER BY json_extract(body, '$.identificador'),id", (owner(),))]


def get(sid):
    with connect() as con:
        row = con.execute("SELECT body FROM sessions WHERE id=? AND consultant_id=?", (sid, owner())).fetchone()
    if not row:
        raise KeyError(sid)
    result = json.loads(row[0])
    result.setdefault("referencias", [])
    return result


def search_references(sid, query):
    """Busca apenas no material selecionado pelo consultor para esta sessão."""
    from academic.knowledge_index import keywords
    refs = get(sid).get("referencias", [])
    words = keywords(query)
    ranked = [(len(words & keywords(" ".join(str(v) for k, v in r.items() if k not in ("id", "quando")))), r) for r in refs]
    return [r for score, r in sorted(ranked, key=lambda pair: pair[0], reverse=True) if score][:10]


def create(identificador, modo, pacote, objetivo):
    s = new_session("S" + uuid4().hex[:10], identificador, modo, pacote, objetivo)
    with connect() as con:
        con.execute("INSERT INTO sessions VALUES (?,?,?)", (s["id"], json.dumps(s), owner()))
    return s


def import_session(client, questionario, avaliacao, paginas, fotos, referencias):
    """Uma única escrita: arquivo inválido não deixa atendimento parcial."""
    s = new_session("S" + uuid4().hex[:10], client.identificador, client.modo, client.pacote, "")
    s.update(questionario=questionario, avaliacao=avaliacao, fotos=fotos, referencias=referencias)
    s["paginas"] = {p: {"texto": t, "aprovada": False, "aprovada_em": None, "origem": "importacao", "fontes": [], "atualizada_em": now()} for p, t in paginas.items()}
    s["revision"] = 1
    s["audit"] = [{"evento": "pasta_importada", "ator": "consultor", "quando": now(), "revision": 1}]
    with connect() as con:
        con.execute("INSERT INTO sessions VALUES (?,?,?)", (s["id"], json.dumps(s), owner()))
    return s


def mutate(sid, revision, action, change, actor="consultor"):
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT body FROM sessions WHERE id=? AND consultant_id=?", (sid, owner())).fetchone()
        if not row:
            raise KeyError(sid)
        s = json.loads(row[0])
        if s["revision"] != revision:
            raise RuntimeError("O atendimento foi alterado. Atualize a tela antes de salvar.")
        change(s)
        s["revision"] += 1
        s["audit"].append({"evento": action, "ator": actor, "quando": now(), "revision": s["revision"]})
        con.execute("UPDATE sessions SET body=? WHERE id=? AND consultant_id=?", (json.dumps(s), sid, owner()))
    return s


def save_ficha(sid, revision, questionario, avaliacao):
    def change(s):
        if s["questionario"] != questionario or s["avaliacao"] != avaliacao:
            for page in s["paginas"].values():
                page["aprovada"] = False
                page["aprovada_em"] = None
        s["questionario"], s["avaliacao"] = questionario, avaliacao
    return mutate(sid, revision, "ficha_atualizada", change)


def valid_page(s, page):
    if page not in pacotes.paginas(s["pacote"]):
        raise ValueError("Página fora do pacote contratado.")


def save_page(sid, revision, page, texto, fontes=None, actor="consultor"):
    def change(s):
        valid_page(s, page)
        previous = s["paginas"].get(page, {})
        s["paginas"][page] = {"texto": texto, "aprovada": False, "aprovada_em": None,
                              "origem": actor, "fontes": fontes if fontes is not None else previous.get("fontes", []), "atualizada_em": now()}
    return mutate(sid, revision, "rascunho_atualizado", change, actor)


def approve(sid, revision, page, decisao):
    def change(s):
        valid_page(s, page)
        p = s["paginas"].get(page)
        if not p or not p["texto"].strip():
            raise ValueError("Escreva ou salve um texto antes de aprovar.")
        p["aprovada"] = decisao == "aprovar"
        p["aprovada_em"] = now() if p["aprovada"] else None
    return mutate(sid, revision, "pagina_" + decisao, change)


def save_chat(sid, question, result):
    def change(s):
        s["chat"].extend([{"role": "user", "content": question},
                          {"role": "assistant", "content": result["texto"], "fontes": result["fontes"],
                           "agentes": result["agentes"], "trace_id": result["trace_id"]}])
        s["chat"] = s["chat"][-100:]
    return mutate(sid, get(sid)["revision"], "consulta_copiloto", change, "copiloto")
