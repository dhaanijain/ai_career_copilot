import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException

from backend_api.schemas.resume import ResumeUploadResponse
from backend_api.services import resume_service

router = APIRouter()


@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        resume_id, path = await asyncio.to_thread(
            resume_service.save_resume, content, file.filename
        )
        skills = await asyncio.to_thread(resume_service.extract_skills, path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")

    return ResumeUploadResponse(
        resume_id=resume_id,
        skills=skills,
        total_skills=len(skills),
    )
