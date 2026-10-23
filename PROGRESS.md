# Progress

## Phase 1 — implemented

- [x] Modular FastAPI application factory, typed settings, lifespan startup.
- [x] SQLite schema for demonstrations, workflows, execution runs, documents and document results; transactions and foreign keys.
- [x] Health and bounded Ollama status endpoints; unavailable model/service states.
- [x] PDF/TXT upload validation and text preview; persisted preview retrieval; unique original storage.
- [x] Responsive dark dashboard, sidebar, five working navigation destinations; functional upload/loading/errors; labeled future-phase screens.
- [x] Three reproducible fictional invoice PDF layouts, TXT sample and separate ground truth.
- [x] Windows PowerShell installation/start commands, architecture, full seven-phase plan and safe Git ignores.
- [x] Automated tests and real HTTP smoke validation.

## Actual validation — 2026-10-23

Python 3.12.14, Linux cloud environment:

- `.venv/bin/python -m pytest -q`: **31 passed**, six upstream deprecation warnings from PyMuPDF SWIG bindings and the Starlette/AnyIO test adapter; no failing tests.
- `.venv/bin/python -m pip check`: dependency consistency verified.
- Uvicorn startup: completed successfully.
- Real HTTP: all five pages and both static assets returned 200; health reported a functioning database.
- Real HTTP multipart PDF and TXT uploads: 201, expected text, persisted retrieval matches the upload response.
- Ollama live status: unavailable, correctly reported without disrupting document preview.
- Tests also cover all three layouts, byte-for-byte original preservation, restart persistence, duplicate filenames, path sanitization, malformed/empty/binary/oversized files, encrypted/blank/too-many-page PDFs, failed-storage cleanup, model discovery/error mocks and byte-identical fixture regeneration.

## Remaining work / limitations

- Phases 2–7 remain unimplemented; no workflow learning, semantic extraction, execution, review, benchmark or export claims.
- No external blocker for Phase 1. Ollama and model weights are not installed in this cloud instance; real inference is not a Phase 1 requirement and was not tested.
- Native Windows execution and visual/interactive testing in a real browser were not available; Windows-compatible commands and responsive CSS were authored, HTTP-rendered pages and APIs were tested. Manual browser/Windows verification remains recommended.
- Image-only PDFs require OCR, intentionally outside Phase 1.
- Trusted local single-user app only; no authentication or public-deployment hardening. The multipart parser may spool a request before the route's file-size check; see architecture for boundaries.
- The UI states the default upload limit; a custom byte limit is enforced by the API and reported on errors.
- A process crash between file storage and database commit can leave an unreferenced original; automatic cleanup is not implemented.
- Initial SQL persistence schemas exist; semantic action schemas and CRUD arrive in their corresponding phases.

## Next task

Phase 2: define a typed, allowlisted demonstration-action schema and record a selected text span with its semantic field label, source document ID and offsets; persist and reload the ordered timeline. Then add undo/remove and desired-output preview.
