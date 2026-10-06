"""API HTTP. Execute `python -m uvicorn backend.app:app --host 127.0.0.1`.

Uso acadêmico local, um consultor, somente clientes fictícios. Não publicar esta
API sem autenticação por usuário e isolamento de dados (ver docs/SEGURANCA.md).
"""
import io
import json
import os
import zipfile
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from academic import pacotes
from . import intelligence, store
from .guards import anonymize, check_input
from .models import SessionInput, FichaInput, PageInput, ApprovalInput, ChatInput, ImportInput, PhotoInput, ReferenceInput
from . import photos, library
from .models import EditorialInput

app = FastAPI(title="Copiloto de Consultoria de Imagem", version="0.2.0")
app.add_middleware(CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_methods=["GET", "POST", "PUT"], allow_headers=["Content-Type"], allow_credentials=False)


@app.exception_handler(KeyError)
async def missing(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"detail": "Atendimento não encontrado."})


@app.exception_handler(ValueError)
async def invalid(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(RuntimeError)
async def conflict(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/health")
def health():
    return {"status": "ok", "modo": "academico-local", "llm_provider": os.getenv("LLM_PROVIDER", "ollama"),
            "rag_mode": os.getenv("RAG_MODE", "lexical"), "versao": "0.2.0"}


@app.get("/catalog")
def catalog():
    return {"pacotes": [{"id": k, "nome": pacotes.nome(k), "formato": v[1], "paginas": list(pacotes.paginas(k))}
                        for k, v in pacotes.PACOTES.items()]}


@app.get("/sessions")
def sessions():
    return store.list_sessions()


@app.post("/sessions", status_code=201)
def create_session(body: SessionInput):
    return store.create(body.identificador, body.modo, body.pacote, check_input(body.objetivo))


@app.get("/sessions/{sid}")
def session(sid: str):
    return store.get(sid)


@app.put("/sessions/{sid}/ficha")
def ficha(sid: str, body: FichaInput):
    if len(json.dumps(body.model_dump())) > 50000:
        raise ValueError("Ficha muito extensa.")
    if any(len(v) > 3000 for v in body.questionario.values()):
        raise ValueError("Campo do questionário muito extenso.")
    q = {k: check_input(v) for k, v in body.questionario.items()}
    a = {k: {field: check_input(value) if isinstance(value, str) else value for field, value in values.items()}
         for k, values in body.avaliacao.items()}
    return store.save_ficha(sid, body.revision, q, a)


@app.put("/sessions/{sid}/pages/{page}")
def page_text(sid: str, page: str, body: PageInput):
    return store.save_page(sid, body.revision, page, anonymize(body.texto))


@app.post("/sessions/{sid}/pages/{page}/decision")
def decision(sid: str, page: str, body: ApprovalInput):
    return store.approve(sid, body.revision, page, body.decisao)


@app.post("/sessions/{sid}/pages/{page}/draft")
def suggest(sid: str, page: str):
    try:
        return intelligence.draft(sid, page)
    except (ValueError, RuntimeError, KeyError):
        raise
    except Exception as exc:
        raise HTTPException(503, "IA indisponível. Verifique o provedor e a indexação; a edição manual continua disponível.") from exc


@app.post("/chat")
def chat(body: ChatInput):
    check_input(body.pergunta)
    if body.sessao_id:
        store.get(body.sessao_id)
    def events():
        try:
            for event in intelligence.consult_stream(body.pergunta, body.sessao_id):
                if event["tipo"] == "final" and body.sessao_id:
                    event["session"] = store.save_chat(body.sessao_id, body.pergunta, event["resultado"])
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception as exc:
            detail = str(exc) if isinstance(exc, (ValueError, RuntimeError)) else "IA indisponível. Verifique o servidor e tente novamente."
            yield json.dumps({"tipo": "erro", "mensagem": detail}, ensure_ascii=False) + "\n"
    return StreamingResponse(events(), media_type="application/x-ndjson", headers={"Cache-Control": "no-store"})


@app.post("/history")
def history(body: ChatInput):
    try:
        return intelligence.consult(body.pergunta, history=True)
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        raise HTTPException(503, "Consulta indisponível. Verifique o provedor de IA.") from exc


@app.get("/knowledge")
def knowledge(q: str = "",):
    if q:
        passages, mode = intelligence.retrieve(q)
        return {"trechos": passages, "modo": mode}
    return {"documentos": [{"arquivo": p.name, "titulo": p.stem[3:].replace("_", " "),
                            "conteudo": p.read_text(encoding="utf-8")} for p in sorted(intelligence.knowledge_index.KNOWLEDGE.glob("[0-9][0-9]_*.md"))]}


@app.get("/sessions/{sid}/export")
def export(sid: str):
    s = store.get(sid)
    ficha = {"versao": 3, "sessao_id": sid, "cliente": s["identificador"], "pacote": s["pacote"],
             "questionario": s["questionario"], "avaliacao": s["avaliacao"], "modo": s["modo"],
             "salvo_em": store.now(), "paginas": {p: v["texto"] for p, v in s["paginas"].items()},
             "aprovadas": [p for p, v in s["paginas"].items() if v["aprovada"]], "audit": s["audit"],
             "chat": s["chat"], "fontes": {p: v["fontes"] for p, v in s["paginas"].items()},
             "fotos": {p: [photo["nome"] for photo in items] for p, items in s["fotos"].items()},
             "referencias": s.get("referencias", [])}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("ficha.json", json.dumps(ficha, ensure_ascii=False, indent=2))
        import base64
        for i, p in enumerate(pacotes.paginas(s["pacote"])):
            for photo in s["fotos"].get(p, []):
                z.writestr(f'fotos/{i+1:02d}/{photo["nome"]}', base64.b64decode(photo["data_url"].split(",", 1)[1]))
    return Response(buf.getvalue(), media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="pasta_{sid}.zip"'})


@app.post("/import", status_code=201)
async def import_folder(request: Request):
    # Limit streaming reads; never extract paths from untrusted ZIPs.
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > 15_000_000:
            raise HTTPException(413, "Pasta maior que 15 MB.")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            if any(info.file_size > 10_000_000 for info in z.infolist()) or sum(i.file_size for i in z.infolist()) > 30_000_000:
                raise ValueError("Pasta expandida muito grande.")
            raw = json.loads(z.read("ficha.json"))
            imported_photos = {}
            pages = list(pacotes.paginas(raw.get("pacote", "pacote_1")))
            import base64
            for info in z.infolist():
                parts = info.filename.split("/")
                if info.filename == "ficha.json" or info.is_dir():
                    continue
                if len(parts) != 3 or parts[0] != "fotos" or not parts[1].isdigit() or not 1 <= int(parts[1]) <= len(pages):
                    raise ValueError("A pasta contém um caminho de imagem inválido.")
                mime = "image/png" if Path(parts[2]).suffix.lower() == ".png" else "image/jpeg"
                data_url = f"data:{mime};base64," + base64.b64encode(z.read(info)).decode()
                photos.validate(data_url)
                page = pages[int(parts[1]) - 1]
                imported_photos.setdefault(page, []).append({"nome": photos.safe_name(parts[2]), "data_url": data_url})
        # Legacy fields are read deliberately; approvals are never trusted from imports.
        fields = {k: raw[k] for k in ImportInput.model_fields if k in raw}
        body = ImportInput.model_validate(fields)
        client = SessionInput(identificador=body.cliente, pacote=body.pacote, modo=raw.get("modo", "feminino"))
        if any(p not in pacotes.paginas(client.pacote) for p in body.paginas):
            raise ValueError("A pasta contém páginas fora do pacote.")
        if any(len(t) > 20000 for t in body.paginas.values()):
            raise ValueError("Texto importado muito extenso.")
        q = {k: check_input(v) for k, v in body.questionario.items()}
        a = {k: {field: check_input(value) if isinstance(value, str) else value for field, value in values.items()} for k, values in body.avaliacao.items()}
        references = raw.get("referencias", [])
        if len(references) > 100:
            raise ValueError("A pasta contém referências demais.")
        validated = [ReferenceInput(revision=0, **{k: v for k, v in r.items() if k in ReferenceInput.model_fields and k != "revision"}).model_dump(exclude={"revision"}) for r in references]
        from uuid import uuid4
        restored = [{**{k: check_input(v) for k, v in r.items()}, "id": uuid4().hex, "quando": store.now()} for r in validated]
        if any(len(items) > 6 for items in imported_photos.values()):
            raise ValueError("Limite de seis imagens por página.")
        for ref in restored:
            if ref["link"] and not ref["link"].startswith(("https://", "http://")):
                raise ValueError("Link importado inválido.")
        return store.import_session(client, q, a, {p: anonymize(t) for p, t in body.paginas.items()}, imported_photos, restored)
    except (zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
        raise ValueError("Arquivo inválido: envie a pasta ZIP com ficha.json.") from exc


@app.get("/traces")
def traces():
    p = intelligence.ROOT / "runtime" / "traces.jsonl"
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()[-100:]][::-1] if p.exists() else []


@app.post("/sessions/{sid}/pages/{page}/photos")
def add_photo(sid: str, page: str, body: PhotoInput):
    photos.validate(body.data_url)
    name = photos.safe_name(body.nome)
    def change(s):
        store.valid_page(s, page)
        items = s["fotos"].setdefault(page, [])
        if len(items) >= 6:
            raise ValueError("Limite de seis imagens por página.")
        items.append({"nome": name, "data_url": body.data_url})
        if page in s["paginas"]:
            s["paginas"][page]["aprovada"] = False
            s["paginas"][page]["aprovada_em"] = None
    return store.mutate(sid, body.revision, "referencia_visual_adicionada", change)


@app.post("/sessions/{sid}/vision")
def vision(sid: str, body: PhotoInput):
    """Reaproveita a pré-análise anterior sem alterar a avaliação profissional."""
    data = photos.validate(body.data_url)
    store.get(sid)
    try:
        import tempfile
        from .vision import analisar_foto
        suffix = ".png" if body.data_url.startswith("data:image/png") else ".jpg"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / ("foto" + suffix)
            path.write_bytes(data)
            result = analisar_foto(path)
        result["status_revisao"] = "NAO_VALIDADA"
        return store.mutate(sid, body.revision, "hipotese_visagismo", lambda s: s.update(hipotese_visagismo=result), "copiloto")
    except (ImportError, FileNotFoundError) as exc:
        raise HTTPException(503, "Pré-análise opcional indisponível. Instale as dependências de visão e disponibilize o modelo local.") from exc


@app.post("/sessions/{sid}/references")
def add_reference(sid: str, body: ReferenceInput):
    from uuid import uuid4
    if body.link and not body.link.startswith(("https://", "http://")):
        raise ValueError("Use uma URL HTTP ou HTTPS para a referência.")
    record = {k: check_input(v) for k, v in body.model_dump(exclude={"revision"}).items()}
    record.update(id=uuid4().hex, quando=store.now())
    def change(s):
        refs = s.setdefault("referencias", [])
        if len(refs) >= 100:
            raise ValueError("Limite de cem referências neste atendimento.")
        refs.append(record)
        for p in s["paginas"].values():
            p["aprovada"], p["aprovada_em"] = False, None
    return store.mutate(sid, body.revision, "referencia_personalizada_adicionada", change)


@app.get("/sessions/{sid}/references")
def references(sid: str, q: str = ""):
    return store.search_references(sid, q) if q else store.get(sid).get("referencias", [])


@app.get("/library")
def editorial_library():
    return {"trechos": library.records(), "status": library.status()}


@app.post("/sessions/{sid}/pages/{page}/library", status_code=201)
def authorize_pattern(sid: str, page: str, body: EditorialInput):
    return library.publish(sid, page, body)


@app.post("/library/{rid}/revoke")
def revoke_pattern(rid: str):
    return library.revoke(rid)


@app.post("/library/train")
def train_editorial_model():
    return library.train()


@app.get("/library/search")
def search_patterns(q: str):
    if not 3 <= len(q) <= 2000:
        raise ValueError("A consulta deve ter de 3 a 2000 caracteres.")
    return library.search(q)


@app.get("/library/dataset")
def editorial_dataset():
    rows = library.active()
    return {"versao": 1, "origem": "Padrões autorizados pelo consultor", "status": library.status(),
            "registros": [{k: r[k] for k in ("id", "titulo", "tema", "texto", "hash")} for r in rows]}
