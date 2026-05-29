import os
import uuid
from pathlib import Path

from app.rag_pipeline import run_pipeline

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"


def save_resume(content: bytes, original_filename: str) -> tuple[str, Path]:
    resume_id = str(uuid.uuid4())
    dest = UPLOADS_DIR / f"{resume_id}.pdf"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return resume_id, dest


def get_resume_path(resume_id: str) -> Path:
    path = UPLOADS_DIR / f"{resume_id}.pdf"
    if not path.exists():
        raise FileNotFoundError(f"Resume not found: {resume_id}")
    return path


def extract_skills(resume_path: Path) -> list[str]:
    return run_pipeline(str(resume_path))
