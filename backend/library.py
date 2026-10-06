"""Memória editorial curada: padrões autorizados, nunca prontuários completos.

TF-IDF aprende o vocabulário/IDF dos trechos selecionados pelo consultor. Não
altera pesos da LLM. Treinar é uma ação explícita; corpus alterado exige treino
novo antes de voltar ao copiloto. SQLite mantém proveniência e revogação.
"""
import hashlib
import json
import re
from functools import lru_cache
from uuid import uuid4
from . import store
from .guards import anonymize, check_input, plain

THEMES = ("perfil", "visagismo", "coloracao", "proporcoes", "metodologia")


def connect():
    con = store.connect()
    con.execute("CREATE TABLE IF NOT EXISTS editorial (id TEXT PRIMARY KEY, body TEXT NOT NULL, consultant_id TEXT)")
    if "consultant_id" not in {r[1] for r in con.execute("PRAGMA table_info(editorial)")}:
        con.execute("ALTER TABLE editorial ADD COLUMN consultant_id TEXT")
    con.execute("CREATE TABLE IF NOT EXISTS editorial_models (consultant_id TEXT PRIMARY KEY, body TEXT NOT NULL)")
    return con


def records():
    with connect() as con:
        return [json.loads(r[0]) for r in con.execute("SELECT body FROM editorial WHERE consultant_id=? ORDER BY id", (store.owner(),))]


def active():
    return [r for r in records() if r["ativa"]]


def publish(sid, page, body):
    if not body.confirmo_padrao_sem_dados_pessoais:
        raise ValueError("Confirme a revisão do padrão e a retirada dos dados pessoais.")
    if body.tema not in THEMES:
        raise ValueError("Tema editorial desconhecido.")
    text, title = body.texto.strip(), body.titulo.strip()
    if not title or len(text) < 30:
        raise ValueError("Escreva um título e um padrão com pelo menos 30 caracteres.")
    # A remoção automática de PII é parcial; exigir correção, não publicar silenciosamente.
    if anonymize(text) != text or anonymize(title) != title or re.search(r"\b(cliente\s+[a-z0-9]|\[cpf\]|\[email\]|\[telefone\])", plain(title + " " + text)):
        raise ValueError("Retire identificadores e dados pessoais antes de autorizar o padrão.")
    check_input(text)
    check_input(title)
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT body FROM sessions WHERE id=? AND consultant_id=?", (sid, store.owner())).fetchone()
        if not row:
            raise KeyError(sid)
        s = json.loads(row[0])
        if s["revision"] != body.revision:
            raise RuntimeError("O atendimento mudou. Atualize antes de autorizar uma referência.")
        store.valid_page(s, page)
        original = s["paginas"].get(page)
        if not original or not original["aprovada"]:
            raise ValueError("A origem deve ser uma página salva e aprovada pelo consultor.")
        digest = hashlib.sha256(text.encode()).hexdigest()
        existing = [json.loads(r[0]) for r in con.execute("SELECT body FROM editorial WHERE consultant_id=?", (store.owner(),))]
        if any(r["ativa"] and r["hash"] == digest for r in existing):
            raise ValueError("Este padrão já está na biblioteca.")
        record = {"id": uuid4().hex, "titulo": title, "tema": body.tema, "texto": text,
                  "ativa": True, "quando": store.now(), "ator": "consultor", "hash": digest,
                  "origem": {"sessao_id": sid, "pagina": page, "revision": s["revision"],
                             "hash_pagina": hashlib.sha256(original["texto"].encode()).hexdigest()},
                  "audit": [{"evento": "padrao_autorizado", "quando": store.now(), "ator": "consultor"}]}
        con.execute("INSERT INTO editorial VALUES (?,?,?)", (record["id"], json.dumps(record), store.owner()))
    return record


def revoke(rid):
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT body FROM editorial WHERE id=? AND consultant_id=?", (rid, store.owner())).fetchone()
        if not row:
            raise KeyError(rid)
        r = json.loads(row[0])
        r["ativa"] = False
        r["audit"].append({"evento": "padrao_retirado", "quando": store.now(), "ator": "consultor"})
        con.execute("UPDATE editorial SET body=? WHERE id=? AND consultant_id=?", (json.dumps(r), rid, store.owner()))
    return r


def corpus(rows):
    # IDs e textos autorizados. Nenhum identificador de cliente entra no modelo.
    return tuple(sorted((r["id"], r["texto"]) for r in rows))


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, ensure_ascii=False).encode()).hexdigest()


@lru_cache(maxsize=4)
def fit(data):
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(strip_accents="unicode", ngram_range=(1, 2), sublinear_tf=True)
    matrix = vectorizer.fit_transform([text for _, text in data])
    return vectorizer, matrix


def status():
    rows = active()
    with connect() as con:
        saved = con.execute("SELECT body FROM editorial_models WHERE consultant_id=?", (store.owner(),)).fetchone()
    model = json.loads(saved[0]) if saved else None
    stale = bool(model and model["corpus_hash"] != fingerprint(corpus(rows)))
    return {"trechos_autorizados": len(rows), "modelo": model, "desatualizado": stale,
            "pronto": bool(model and not stale)}


def train():
    rows = active()
    data = corpus(rows)
    if len(data) < 2:
        raise ValueError("Autorize pelo menos dois padrões distintos antes de treinar a recuperação ML.")
    vectorizer, _ = fit(data)
    import sklearn
    model = {"algoritmo": "TF-IDF + similaridade cosseno", "versao": hashlib.sha256(("tfidf-editorial-v1|" + sklearn.__version__ + "|" + fingerprint(data)).encode()).hexdigest()[:16],
             "corpus_hash": fingerprint(data), "trechos": len(data), "vocabulario": len(vectorizer.vocabulary_),
             "treinado_em": store.now(), "sklearn": sklearn.__version__, "metricas_validacao": None}
    with connect() as con:
        con.execute("INSERT OR REPLACE INTO editorial_models VALUES (?,?)", (store.owner(), json.dumps(model)))
    return status()


def search(query, limit=3):
    check_input(query)
    model = status()
    if not model["pronto"]:
        return {"trechos": [], "status": model}
    rows = active()
    data = corpus(rows)
    # Mudança concorrente: jamais usar o snapshot anterior à retirada de um trecho.
    if fingerprint(data) != model["modelo"]["corpus_hash"]:
        return {"trechos": [], "status": status()}
    vectorizer, matrix = fit(data)
    scores = (matrix @ vectorizer.transform([query]).T).toarray().ravel()
    lookup = {r["id"]: r for r in rows}
    result = []
    for i in scores.argsort()[::-1][:limit]:
        if scores[i] < 0.12:
            continue
        r = lookup[data[i][0]]
        # Sem prontuário/proveniência de cliente no contexto da LLM.
        result.append({"id": r["id"], "titulo": r["titulo"], "tema": r["tema"], "texto": r["texto"],
                       "similaridade": round(float(scores[i]), 4), "modelo": model["modelo"]["versao"]})
    return {"trechos": result, "status": model}
