from pathlib import Path
import hashlib
import httpx
import pymupdf
import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app
from app.database import connect, initialize
from scripts.generate_samples import generate

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(Settings(data_dir=tmp_path / "runtime", max_upload_bytes=20000))) as client:
        yield client

@pytest.fixture
def samples(tmp_path):
    directory = tmp_path / "samples"
    generate(directory)
    return directory

def test_startup_health_and_schema(client):
    result = client.get("/api/health")
    assert result.status_code == 200
    assert result.json()["status"] == "ok"
    assert result.json()["counts"] == dict(documents=0, demonstrations=0, workflows=0, execution_runs=0)
    path = client.app.state.db_path
    initialize(path)
    with connect(path) as database:
        tables = {row[0] for row in database.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"demonstrations", "workflows", "execution_runs", "document_results", "documents"} <= tables
        assert database.execute("PRAGMA foreign_keys").fetchone()[0] == 1

@pytest.mark.parametrize("page", ["/", "/teach", "/workflows", "/run", "/results"])
def test_navigation(client, page):
    result = client.get(page)
    assert result.status_code == 200
    assert 'aria-current="page"' in result.text
    assert "ZeroTouch" in result.text
    if page not in ["/", "/teach"]:
        assert "COMING IN PHASE" in result.text

def test_txt_upload_preserves_and_persists(client):
    raw = b"Invoice: DEMO-1\nTotal: USD 12.00"
    response = client.post("/api/documents", files={"file": ("../../invoice.txt", raw, "text/plain")})
    assert response.status_code == 201
    item = response.json()
    assert item["name"] == "invoice.txt"
    assert item["text"] == raw.decode()
    assert client.get(f"/api/documents/{item['id']}").json() == item
    stored = list((client.app.state.settings.data_dir / "uploads").iterdir())
    assert len(stored) == 1 and stored[0].read_bytes() == raw
    with TestClient(create_app(client.app.state.settings)) as restarted:
        assert restarted.get(f"/api/documents/{item['id']}").json() == item
    assert client.get("/api/health").json()["counts"]["documents"] == 1

@pytest.mark.parametrize("index", [1, 2, 3])
def test_pdf_layouts(client, samples, index):
    raw = (samples / f"invoice_{index}.pdf").read_bytes()
    response = client.post("/api/documents", files={"file": (f"invoice_{index}.pdf", raw, "application/pdf")})
    assert response.status_code == 201
    assert f"SYN-2026-{index:03}" in response.json()["text"]
    assert "120.00" in response.json()["text"]
    assert next((client.app.state.settings.data_dir / "uploads").iterdir()).read_bytes() == raw

@pytest.mark.parametrize("name,content,mime,status", [
    ("bad.exe", b"binary", "application/octet-stream", 415),
    ("bad.txt", b"text", "application/pdf", 415),
    ("bad.pdf", b"not pdf", "application/pdf", 422),
    ("broken.pdf", b"%PDF-1.7 broken", "application/pdf", 422),
    ("empty.txt", b"", "text/plain", 422),
    ("white.txt", b"   ", "text/plain", 422),
    ("binary.txt", b"\x00text", "text/plain", 422),
    ("encoding.txt", b"\xff\xfe", "text/plain", 422),
    ("big.txt", b"x" * 20001, "text/plain", 413),
])
def test_rejected_uploads_leave_no_files(client, name, content, mime, status):
    response = client.post("/api/documents", files={"file": (name, content, mime)})
    assert response.status_code == status
    assert isinstance(response.json()["detail"], str)
    assert not list((client.app.state.settings.data_dir / "uploads").iterdir())
    assert client.get("/api/health").json()["counts"]["documents"] == 0

def test_blank_pdf(client):
    with pymupdf.open() as document:
        document.new_page()
        content = document.tobytes()
    response = client.post("/api/documents", files={"file": ("scan.pdf", content, "application/pdf")})
    assert response.status_code == 422
    assert "OCR" in response.json()["detail"]

def test_same_filename_never_overwrites(client):
    for text in [b"first invoice", b"second invoice"]:
        assert client.post("/api/documents", files={"file": ("same.txt", text, "text/plain")}).status_code == 201
    files = list((client.app.state.settings.data_dir / "uploads").iterdir())
    assert {file.read_bytes() for file in files} == {b"first invoice", b"second invoice"}

def test_ollama_unavailable(client, monkeypatch):
    async def unavailable(self, url):
        raise httpx.ConnectError("offline")
    monkeypatch.setattr(httpx.AsyncClient, "get", unavailable)
    response = client.get("/api/ollama")
    assert response.status_code == 200
    assert response.json()["available"] is False
    assert client.get("/api/health").json()["status"] == "ok"

@pytest.mark.parametrize("payload,available,installed", [
    ({"models": [{"name": "llama3.2:3b"}]}, True, True),
    ({"models": []}, True, False),
    ({"unexpected": []}, False, False),
    ({"models": [{"name": 123}]}, False, False),
])
def test_ollama_status(client, monkeypatch, payload, available, installed):
    async def response(self, url):
        return httpx.Response(200, json=payload, request=httpx.Request("GET", url))
    monkeypatch.setattr(httpx.AsyncClient, "get", response)
    data = client.get("/api/ollama").json()
    assert data["available"] is available
    assert data["model_installed"] is installed

def test_missing_document(client):
    assert client.get("/api/documents/unknown").status_code == 404

def test_fixture_generation_is_reproducible(tmp_path):
    generate(tmp_path)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.iterdir()}
    generate(tmp_path)
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.iterdir()}
    assert before == after


def test_pdf_page_limit(client):
    with pymupdf.open() as document:
        for _ in range(101):
            document.new_page()
        content = document.tobytes(garbage=4, deflate=True)
    with TestClient(create_app(Settings(data_dir=client.app.state.settings.data_dir, max_upload_bytes=1000000))) as larger:
        response = larger.post('/api/documents', files={'file': ('long.pdf', content, 'application/pdf')})
    assert response.status_code == 422
    assert '100 pages' in response.json()['detail']


def test_encrypted_pdf(client):
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((40, 40), 'Private fictional invoice')
        content = document.tobytes(encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw='owner', user_pw='demo')
    response = client.post('/api/documents', files={'file': ('locked.pdf', content, 'application/pdf')})
    assert response.status_code == 422
    assert 'Password-protected' in response.json()['detail']


def test_database_failure_rolls_back_file(client, monkeypatch):
    from app.api import routes
    def fail(_):
        raise OSError('simulated storage failure')
    monkeypatch.setattr(routes.database, 'connect', fail)
    response = client.post('/api/documents', files={'file': ('invoice.txt', b'fictional invoice', 'text/plain')})
    assert response.status_code == 500
    assert not list((client.app.state.settings.data_dir / 'uploads').iterdir())
