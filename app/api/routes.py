import logging
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel
from app import database
from app.ai.ollama import status
from app.core.documents import DocumentError, extract_text, safe_name

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

class DocumentPreview(BaseModel):
    id: str
    name: str
    size_bytes: int
    text: str

@router.get("/health")
def health(request: Request):
    try:
        return {"status": "ok", "database": "ok", "counts": database.counts(request.app.state.db_path)}
    except Exception:
        logger.exception("Database health check failed")
        raise HTTPException(503, "Database is unavailable")

@router.get("/ollama")
async def ollama(request: Request):
    return await status(request.app.state.settings)

@router.post("/documents", response_model=DocumentPreview, status_code=201)
async def upload(request: Request, file: UploadFile = File(...)):
    name = safe_name(file.filename or "")
    suffix = Path(name).suffix.lower()
    if suffix not in {".pdf", ".txt"}:
        await file.close()
        raise HTTPException(415, "Only PDF and UTF-8 TXT files are supported.")
    allowed_types = {".pdf": {"application/pdf", "application/octet-stream"},
                     ".txt": {"text/plain", "application/octet-stream"}}
    if file.content_type not in allowed_types[suffix]:
        await file.close()
        raise HTTPException(415, "The document MIME type does not match its extension.")
    limit = request.app.state.settings.max_upload_bytes
    try:
        content = await file.read(limit + 1)
    finally:
        await file.close()
    if len(content) > limit:
        raise HTTPException(413, f"Document exceeds the {limit}-byte upload limit.")
    if not content:
        raise HTTPException(422, "The document is empty.")
    try:
        text = extract_text(content, suffix)
    except DocumentError as exc:
        raise HTTPException(422, str(exc)) from exc
    identifier = uuid4().hex
    stored_name = identifier + suffix
    target = request.app.state.settings.data_dir / "uploads" / stored_name
    try:
        with target.open("xb") as output:
            output.write(content)
        with database.connect(request.app.state.db_path) as connection:
            connection.execute("INSERT INTO documents(id,original_name,stored_name,media_type,size_bytes,text) VALUES(?,?,?,?,?,?)",
                (identifier, name, stored_name, file.content_type, len(content), text))
    except Exception:
        target.unlink(missing_ok=True)
        logger.exception("Document storage failed")
        raise HTTPException(500, "Could not save the document. Please try again.")
    return DocumentPreview(id=identifier, name=name, size_bytes=len(content), text=text)

@router.get("/documents/{identifier}", response_model=DocumentPreview)
def document(identifier: str, request: Request):
    with database.connect(request.app.state.db_path) as connection:
        row = connection.execute("SELECT * FROM documents WHERE id=?", (identifier,)).fetchone()
    if row is None:
        raise HTTPException(404, "Document not found.")
    return DocumentPreview(id=row["id"], name=row["original_name"], size_bytes=row["size_bytes"], text=row["text"])
