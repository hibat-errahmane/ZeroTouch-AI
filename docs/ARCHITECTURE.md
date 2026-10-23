# Architecture — Phase 1

Browser → FastAPI routes → document service / Ollama client → SQLite + local original files.

- `app/main.py`: application factory, lifespan initialization, static files and Jinja pages. Importing does not create runtime state.
- `app/config.py`: typed immutable settings from process environment. Paths resolve through pathlib; default runtime location is relative to the project, not the caller's working directory.
- `app/api/routes.py`: HTTP validation, Pydantic document response, storage orchestration, health and Ollama status.
- `app/core/documents.py`: document content validation and text extraction, independent of HTTP.
- `app/ai/ollama.py`: bounded local `/api/tags` call; connection failure is an explicit status, never a fabricated inference result. No learning or inference is implemented yet.
- `app/database.py`: SQLite schema and transaction context manager; explicit SQL avoids an unnecessary ORM at this scale. Demonstrations store ordered action JSON; workflows reference demonstrations; runs reference workflows; document results reference runs and original documents. These are initial persistence structures, not validated Phase 3 workflow schemas or public CRUD APIs.
- `templates` and `static`: server-rendered navigation, dependency-free JavaScript and CSS. User text is assigned through `textContent`, never interpreted as HTML.

## Upload integrity and boundaries

Allow only `.pdf` and `.txt` with compatible MIME types; MIME claims alone are insufficient, so contents are decoded/parsed. Limit file bytes (10 MiB by default), PDF pages (100), and resulting text (one million characters). Reject encrypted, corrupt, blank and image-only PDFs; no OCR is installed. TXT requires UTF-8. Generated UUID names and exclusive writes prevent path traversal and accidental replacement. Originals are saved byte-for-byte and never modified. Failed DB writes remove only the newly generated file. SQLite foreign keys are enabled on each connection.

This is a trusted single-user local application. Bind to loopback; do not expose it publicly. It has no authentication, malware scanning, OCR, sandboxed PDF worker, multiuser isolation or batch queue. The upload byte limit applies when reading the multipart file; multipart parsing may spool larger requests before route validation. A future network deployment requires a reverse-proxy request-body limit and authentication. Parsing is in-process and synchronous, appropriate for small local Phase 1 previews, not hostile high-volume input. Crash recovery for the small filesystem/DB transaction gap remains future work.

## AI and future safety

Phase 2 records meaningful semantic actions. Phase 3 must learn reusable instructions from demonstrations using Ollama and validate all JSON with strict Pydantic schemas. An explicit supported-action allowlist will drive execution; generated Python and shell commands must never execute. No invoice extraction pipeline is disguised as learned automation here.

## Data and configuration

`documents` stores original names, generated storage names, media type, size and preview text. Sensitive invoice text stays in the local runtime directory and is never included in logs intentionally. `.env.example` documents names only; configuration comes from the process environment and no `.env` file is auto-loaded. Runtime state is ignored by Git. Export directories exist but export logic belongs to Phase 6. `openpyxl` is installed for the specified stack but not used to imply working exports.

Tests use isolated temporary data directories and mocked Ollama HTTP calls. Synthetic PDF fixtures include separate ground truth; Phase 1 tests verify text preview, not field accuracy or model performance.
