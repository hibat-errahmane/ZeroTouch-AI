import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("ZEROTOUCH_DATA_DIR", str(ROOT / "data/runtime"))).resolve())
    ollama_url: str = field(default_factory=lambda: os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2:3b"))
    max_upload_bytes: int = field(default_factory=lambda: int(os.getenv("ZEROTOUCH_MAX_UPLOAD_BYTES", "10485760")))

    def __post_init__(self):
        if self.max_upload_bytes < 1:
            raise ValueError("Upload limit must be positive")
