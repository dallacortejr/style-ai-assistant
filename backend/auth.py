"""Contas locais, sessões opacas e isolamento. Sem cobrança simulada.

Senhas: scrypt N=2**17, r=8, p=1, salt aleatório. Cookie guarda apenas um
token opaco; SQLite guarda seu hash. CSRF é devolvido ao cliente autenticado
e permanece em memória. Não usar HTTP fora do desenvolvimento local.
"""
import hashlib
import hmac
import os
import re
import secrets
import time
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from . import store

router = APIRouter()
COOKIE = "consultoria_session"


def connect():
    con = store.connect()
    con.execute("CREATE TABLE IF NOT EXISTS consultants (id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, created TEXT NOT NULL, subscription TEXT NOT NULL)")
    con.execute("CREATE TABLE IF NOT EXISTS auth_sessions (token TEXT PRIMARY KEY, owner TEXT NOT NULL, csrf TEXT NOT NULL, expires REAL NOT NULL)")
    con.execute("CREATE TABLE IF NOT EXISTS auth_attempts (ip TEXT NOT NULL, moment REAL NOT NULL)")
    return con


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    derived = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**17, r=8, p=1, maxmem=256*1024*1024).hex()
    return f"scrypt$131072$8$1${salt}${derived}"


def verify(password, encoded):
    try:
        salt = encoded.split("$")[4]
        return hmac.compare_digest(password_hash(password, salt), encoded)
    except (ValueError, IndexError):
        return False


DUMMY_PASSWORD = password_hash("dummy-password-never-used", "00"*16)


def profile(row):
    return {"id": row[0], "name": row[1], "email": row[2], "created": row[4],
            "subscription": {"status": row[5], "cycle": "monthly", "provider": None,
                             "checkout_available": False, "price": None}}


class Login(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=128)


class Registration(Login):
    name: str = Field(min_length=2, max_length=100)


class ProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=100)


def email(value):
    value = value.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        raise HTTPException(422, "Informe um e-mail válido.")
    return value


def new_session(row, response, previous=None):
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with connect() as con:
        con.execute("DELETE FROM auth_sessions WHERE expires < ?", (time.time(),))
        if previous:
            con.execute("DELETE FROM auth_sessions WHERE token=?", (digest(previous),))
        con.execute("INSERT INTO auth_sessions VALUES (?,?,?,?)", (digest(token), row[0], csrf, time.time()+28800))
    response.set_cookie(COOKIE, token, max_age=28800, httponly=True,
                        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true", samesite="strict", path="/")
    response.headers["Cache-Control"] = "no-store"
    return {"consultant": profile(row), "csrf": csrf}


def throttle(request):
    ip = request.client.host if request.client else "unknown"
    moment = time.time()
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        con.execute("DELETE FROM auth_attempts WHERE moment<?", (moment-900,))
        if con.execute("SELECT COUNT(*) FROM auth_attempts WHERE ip=?", (ip,)).fetchone()[0] >= 15:
            raise HTTPException(429, "Muitas tentativas. Aguarde 15 minutos e tente novamente.")
        con.execute("INSERT INTO auth_attempts VALUES (?,?)", (ip, moment))


@router.post("/auth/register", status_code=201)
def register(body: Registration, request: Request, response: Response):
    throttle(request)
    address, name = email(body.email), body.name.strip()
    if len(name) < 2:
        raise HTTPException(422, "Informe seu nome profissional.")
    hashed = password_hash(body.password)
    import sqlite3
    try:
        with connect() as con:
            con.execute("INSERT INTO consultants VALUES (?,?,?,?,?,?)", (uuid4().hex, name, address, hashed, store.now(), "pilot"))
            row = con.execute("SELECT * FROM consultants WHERE email=?", (address,)).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "Este e-mail já possui cadastro. Entre com sua senha.") from exc
    return new_session(row, response, request.cookies.get(COOKIE))


@router.post("/auth/login")
def login(body: Login, request: Request, response: Response):
    throttle(request)
    with connect() as con:
        row = con.execute("SELECT * FROM consultants WHERE email=?", (email(body.email),)).fetchone()
    # Mesmo custo de derivação para conta inexistente.
    encoded = row[3] if row else DUMMY_PASSWORD
    valid = verify(body.password, encoded)
    if not row or not valid:
        raise HTTPException(401, "E-mail ou senha incorretos.")
    return new_session(row, response, request.cookies.get(COOKIE))


@router.get("/auth/me")
def me(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return {"consultant": request.state.consultant, "csrf": request.state.csrf}


@router.put("/auth/profile")
def update_profile(body: ProfileInput):
    name = body.name.strip()
    if len(name) < 2:
        raise HTTPException(422, "Informe seu nome profissional.")
    with connect() as con:
        con.execute("UPDATE consultants SET name=? WHERE id=?", (name, store.owner()))
        return profile(con.execute("SELECT * FROM consultants WHERE id=?", (store.owner(),)).fetchone())


@router.post("/auth/logout")
def logout(request: Request, response: Response):
    with connect() as con:
        con.execute("DELETE FROM auth_sessions WHERE token=?", (digest(request.cookies.get(COOKIE, "")),))
    response.delete_cookie(COOKIE, path="/", httponly=True, samesite="strict",
                           secure=os.getenv("COOKIE_SECURE", "false").lower() == "true")
    response.headers["Cache-Control"] = "no-store"
    return {"ok": True}


@router.post("/billing/checkout")
def checkout():
    raise HTTPException(503, "Pagamento mensal ainda não configurado. Nenhuma cobrança foi realizada.")


class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request = Request(scope)
        public = scope["path"] in ("/health", "/docs", "/openapi.json", "/redoc", "/auth/login", "/auth/register")
        origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173").split(",")
        if request.method == "OPTIONS":
            return await self.app(scope, receive, send)
        if request.method not in ("GET", "HEAD") and request.headers.get("origin") and request.headers["origin"] not in origins:
            return await JSONResponse({"detail": "Origem não autorizada."}, status_code=403)(scope, receive, send)
        if public:
            return await self.app(scope, receive, send)
        token = request.cookies.get(COOKIE, "")
        with connect() as con:
            session = con.execute("SELECT owner,csrf FROM auth_sessions WHERE token=? AND expires>?", (digest(token), time.time())).fetchone()
            row = con.execute("SELECT * FROM consultants WHERE id=?", (session[0],)).fetchone() if session else None
        if not row:
            return await JSONResponse({"detail": "Entre com sua conta para continuar."}, status_code=401, headers={"Cache-Control": "no-store"})(scope, receive, send)
        if request.method not in ("GET", "HEAD") and not hmac.compare_digest(request.headers.get("x-csrf-token", ""), session[1]):
            return await JSONResponse({"detail": "Sessão inválida. Atualize a página."}, status_code=403)(scope, receive, send)
        if os.getenv("SAAS_ENFORCE_SUBSCRIPTION", "false").lower() == "true" and row[5] != "active" and not scope["path"].startswith(("/auth/", "/billing/")):
            return await JSONResponse({"detail": "A assinatura precisa estar ativa para acessar os atendimentos."}, status_code=402)(scope, receive, send)
        scope.setdefault("state", {}).update(consultant=profile(row), csrf=session[1])
        context = store.tenant.set(row[0])
        async def private_send(message):
            if message["type"] == "http.response.start":
                headers = [(k, v) for k, v in message.get("headers", []) if k.lower() != b"cache-control"]
                message["headers"] = headers + [(b"cache-control", b"no-store")]
            await send(message)
        try:
            return await self.app(scope, receive, private_send)
        finally:
            store.tenant.reset(context)
