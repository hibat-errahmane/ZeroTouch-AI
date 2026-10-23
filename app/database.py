"""SQLite persistence boundary. JSON columns hold future validated domain payloads."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS demonstrations (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, actions_json TEXT NOT NULL DEFAULT '[]',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS workflows (
 id TEXT PRIMARY KEY, demonstration_id TEXT REFERENCES demonstrations(id),
 name TEXT NOT NULL, definition_json TEXT NOT NULL DEFAULT '{}',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS execution_runs (
 id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL REFERENCES workflows(id),
 status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS documents (
 id TEXT PRIMARY KEY, original_name TEXT NOT NULL, stored_name TEXT NOT NULL UNIQUE,
 media_type TEXT NOT NULL, size_bytes INTEGER NOT NULL, text TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS document_results (
 id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES execution_runs(id),
 document_id TEXT NOT NULL REFERENCES documents(id), status TEXT NOT NULL DEFAULT 'pending',
 result_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
"""

@contextmanager
def connect(path: Path):
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()

def initialize(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as connection:
        connection.executescript(SCHEMA)

def counts(path: Path) -> dict[str, int]:
    with connect(path) as connection:
        return {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("documents", "demonstrations", "workflows", "execution_runs")}
