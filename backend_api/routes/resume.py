import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend_api.middleware.auth import optional_user
from backend_api.schemas.resume import ResumeUploadResponse
from backend_api.services import resume_service

router = APIRouter()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB
PDF_MAGIC = b"%PDF"


@router.post(
    "/upload-resume",
    response_model=ResumeUploadResponse,
    summary="Upload and parse a resume PDF",
    description=(
        "Accepts a PDF resume (≤ 5 MB), extracts technical skills via the RAG pipeline, "
        "and returns a `resume_id` UUID used by all other endpoints. "
        "If a valid JWT is provided the resume is also persisted to Supabase Storage."
    ),
    responses={
        400: {"description": "Invalid file (not PDF, too large, or empty)"},
        500: {"description": "Skill extraction failed"},
    },
)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: Optional[str] = Depends(optional_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum allowed size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
        )

    if not content.startswith(PDF_MAGIC):
        raise HTTPException(
            status_code=400,
            detail="File does not appear to be a valid PDF (magic bytes mismatch).",
        )

    try:
        resume_id, path = await asyncio.to_thread(
            resume_service.save_resume, content, file.filename
        )
        skills = await asyncio.to_thread(resume_service.extract_skills, path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")
    # File is intentionally kept on disk so skill-gap and job-recommendation
    # endpoints can re-use it without requiring a second upload.
    # Old resumes are cleaned up when the user uploads a new one (see below).

    if user_id:
        await asyncio.to_thread(
            resume_service.save_resume_to_supabase,
            content,
            file.filename,
            resume_id,
            skills,
            user_id,
            len(content),
        )

    return ResumeUploadResponse(
        resume_id=resume_id,
        skills=skills,
        total_skills=len(skills),
    )
