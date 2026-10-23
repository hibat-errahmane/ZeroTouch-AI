# ZeroTouch AI — Seven-phase plan

Scope now: Phase 1 only. Later work is planned, not implemented.

## Phase 1 — Foundation and application skeleton

Functionality: Modular FastAPI/Jinja application, responsive dashboard/navigation, SQLite schemas, PDF/TXT upload and preview, health/Ollama status, reproducible fictional fixtures, configuration, docs and tests.

Acceptance: Application starts; all five pages render; valid documents persist unchanged and preview correctly; invalid files are rejected; unavailable Ollama does not break preview; deterministic tests pass.

Status: Implemented; see PROGRESS.md for validation.

## Phase 2 — Human demonstration recorder

Functionality: Select source values and semantic labels; record extraction, normalization, naming and export actions; ordered timeline; undo/remove; save/load/name demonstrations; desired-output preview; persisted action logs.

Acceptance: A user can record, undo, save and reload an ordered demonstration with source references and desired output, without OS mouse recording.

Status: Not started.

## Phase 3 — AI workflow learning

Functionality: Ollama interpretation of demonstrations; generalized extraction instructions; strict structured JSON schemas; date/money normalization; supported-action allowlist; inspection/editing; invalid response and model-error handling.

Acceptance: A demonstrated task produces an inspected reusable workflow; malformed or unsupported actions are rejected; tests verify learning prompts and validation; different layouts exercise genuine model generalization.

Status: Not started.

## Phase 4 — Autonomous workflow execution

Functionality: Choose learned workflow; upload batch; AI extraction driven by learned instructions; normalization/validation/export steps; progress/status; document isolation; bounded recoverable retries; persisted history.

Acceptance: A batch applies the selected learned workflow to new inputs; one failure does not discard other documents; retries terminate; history and results survive restart.

Status: Not started.

## Phase 5 — Validation and human review

Functionality: Required/date/numeric/money validation; arithmetic checks; duplicate detection; uncertainty flags; correction and approval UI; original preservation; audit trail.

Acceptance: Missing, inconsistent and duplicate invoices are flagged; users correct and approve records; originals and a traceable correction audit survive restart.

Status: Not started.

## Phase 6 — Results, metrics and user experience

Functionality: Execution dashboard, logs/timeline, completed/failed/review counts, CSV/XLSX and approved-document ZIP, actual timing, ground-truth accuracy evaluation, labeled manual baseline, before/after view, loading/error/empty states and reproducible demo mode.

Acceptance: Exports match approved data; measured timings and accuracy are reproducible; manual baseline is clearly identified; no invented scores or savings; end-to-end demo works.

Status: Not started.

## Phase 7 — Documentation and submission

Functionality: GitHub-ready README, architecture, install/troubleshooting, reproducible demo, tests/results, video storyboard, local/open-weight AI explanation, English DEV article following verified official challenge rules.

Acceptance: A new user follows the documented demo; submission claims match actual results and current official requirements; documentation and article are reviewed before publication.

Status: Not started.
