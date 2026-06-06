"""
backend_api/services/resume_service.py — AI Career Copilot
Handles resume persistence: local filesystem + Supabase Storage and DB.

When user_id is supplied (authenticated request) the file is also uploaded to
Supabase Storage and a row is inserted into public.resumes + public.extracted_skills.
When user_id is None the service works exactly as before (local-only).
"""

import hashlib
import os
import uuid
from pathlib import Path
from typing import Optional

from app.rag_pipeline import run_pipeline

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"


# ─────────────────────────────────────────────────────────────────────────────
# Local helpers
# ─────────────────────────────────────────────────────────────────────────────

def save_resume(content: bytes, original_filename: str) -> "tuple[str, Path]":
    """Write the file to the local uploads directory. Returns (resume_id, path)."""
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


def delete_local_resume(resume_path: Path) -> None:
    try:
        resume_path.unlink(missing_ok=True)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Supabase persistence (only called when user_id is available)
# ─────────────────────────────────────────────────────────────────────────────

def save_resume_to_supabase(
    content: bytes,
    original_filename: str,
    resume_id: str,
    skills: list[str],
    user_id: str,
    file_size_bytes: Optional[int] = None,
) -> None:
    """
    Upload the PDF to Storage and insert metadata + skills into the database.
    Uses the service role client so RLS is bypassed and user_id is set explicitly.
    Failures are logged but do not raise so the API response is never blocked.
    """
    try:
        from app.config.supabase import get_supabase_client
        client = get_supabase_client()

        storage_path = f"resumes/{user_id}/{resume_id}.pdf"

        # 1. Upload to Supabase Storage
        client.storage.from_("resumes").upload(
            path=storage_path,
            file=content,
            file_options={"content-type": "application/pdf", "upsert": "true"},
        )

        # 2. Mark any previous active resume inactive for this user
        client.table("resumes").update({"is_active": False}).eq(
            "user_id", user_id
        ).eq("is_active", True).execute()

        # 3. Insert resume metadata row
        file_hash = hashlib.md5(content).hexdigest()
        client.table("resumes").insert(
            {
                "id": resume_id,
                "user_id": user_id,
                "original_filename": original_filename,
                "storage_path": storage_path,
                "file_size_bytes": file_size_bytes or len(content),
                "file_hash": file_hash,
                "skills": skills,
                "total_skills": len(skills),
                "is_active": True,
                "version": 1,
            }
        ).execute()

    except Exception as exc:
        print(f"[resume_service] Supabase save failed (non-fatal): {exc}")
