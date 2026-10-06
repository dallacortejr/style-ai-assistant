"""Imagens sintéticas: persistência por conta, validação e remoção de metadados."""
import base64
import io
import sqlite3
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from backend import store, auth
from backend.app import app

PASSWORD = "senha-ficticia-para-imagens-2026"


def image_url(kind):
    buf = io.BytesIO()
    if kind == "photo":
        image = Image.new("RGB", (700, 550), "tan")
        exif = Image.Exif()
        exif[315] = "Metadado fictício que deve ser descartado"
        image.save(buf, format="JPEG", exif=exif)
        mime = "jpeg"
    else:
        exif = Image.Exif()
        exif[315] = "Metadado fictício da logo que deve ser descartado"
        Image.new("RGBA", (900, 600), (120, 70, 40, 0)).save(buf, format="PNG", exif=exif)
        mime = "png"
    return f"data:image/{mime};base64," + base64.b64encode(buf.getvalue()).decode()


@pytest.fixture
def clients(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB", tmp_path / "identity.sqlite3")
    result = []
    for name in ("a", "b"):
        c = TestClient(app)
        payload = {"name": "Consultor " + name, "email": name+"@example.invalid", "password": PASSWORD}
        if name == "a":
            payload.update(photo=image_url("photo"), logo=image_url("logo"))
        response = c.post("/auth/register", json=payload)
        assert response.status_code == 201
        c.headers["X-CSRF-Token"] = response.json()["csrf"]
        result.append(c)
    return result


def test_registration_images_survive_login_and_are_normalized(clients):
    a, _ = clients
    data = a.get("/auth/me").json()["consultant"]
    for kind, size in (("photo", 512), ("logo", 768)):
        raw = base64.b64decode(data[kind].split(",")[1])
        with Image.open(io.BytesIO(raw)) as image:
            assert max(image.size) <= size
            assert not image.getexif()
            if kind == "logo":
                assert image.mode == "RGBA" and image.getpixel((0, 0))[3] == 0
    assert data["photo"] != image_url("photo")
    response = a.post("/auth/login", json={"email": "a@example.invalid", "password": PASSWORD})
    assert response.status_code == 200
    assert response.json()["consultant"]["photo"] == data["photo"]
    assert response.json()["consultant"]["logo"] == data["logo"]


def test_profile_images_are_private_preserved_and_removable(clients):
    a, b = clients
    original = a.get("/auth/me").json()["consultant"]
    assert b.get("/auth/me").json()["consultant"]["photo"] is None
    assert b.get("/auth/me").json()["consultant"]["logo"] is None
    renamed = a.put("/auth/profile", json={"name": "Nome profissional novo"}).json()
    assert renamed["photo"] == original["photo"] and renamed["logo"] == original["logo"]
    cleared = a.put("/auth/profile", json={"name": renamed["name"], "photo": None, "logo": None}).json()
    assert cleared["photo"] is None and cleared["logo"] is None
    b.put("/auth/profile", json={"name": "Consultor B", "logo": image_url("logo")})
    assert a.get("/auth/me").json()["consultant"]["logo"] is None
    assert b.get("/auth/me").json()["consultant"]["logo"] is not None


def test_invalid_image_rejects_signup_and_atomic_profile_edit(clients):
    a, _ = clients
    invalid = "data:image/svg+xml;base64," + base64.b64encode(b'<svg></svg>').decode()
    original = a.get("/auth/me").json()["consultant"]
    r = a.put("/auth/profile", json={"name": "Alteração rejeitada", "photo": None, "logo": invalid})
    assert r.status_code == 422
    assert a.get("/auth/me").json()["consultant"] == original
    for value in (invalid, "data:image/png;base64,bm90LWFuLWltYWdl", "data:image/png;base64," + base64.b64encode(b'x'*3_000_001).decode()):
        r = a.post("/auth/register", json={"name": "Inválido", "email": "invalid@example.invalid", "password": PASSWORD, "photo": value})
        assert r.status_code == 422
    with auth.connect() as con:
        assert con.execute("SELECT COUNT(*) FROM consultants").fetchone()[0] == 2


def test_existing_accounts_receive_optional_images_without_data_loss(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB", tmp_path / "existing.sqlite3")
    hashed = auth.password_hash(PASSWORD)
    with sqlite3.connect(store.DB) as con:
        con.execute("CREATE TABLE consultants (id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, created TEXT NOT NULL, subscription TEXT NOT NULL)")
        con.execute("INSERT INTO consultants VALUES (?,?,?,?,?,?)", ("old-account", "Conta existente", "old@example.invalid", hashed, "2026-10-05", "pilot"))
    c = TestClient(app)
    r = c.post("/auth/login", json={"email": "old@example.invalid", "password": PASSWORD})
    assert r.status_code == 200
    profile = r.json()["consultant"]
    assert profile["id"] == "old-account" and profile["name"] == "Conta existente"
    assert profile["photo"] is None and profile["logo"] is None
    with auth.connect() as con:
        assert con.execute("SELECT password FROM consultants").fetchone()[0] == hashed
