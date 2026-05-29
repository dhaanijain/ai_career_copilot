import asyncio
from fastapi import APIRouter, HTTPException

from backend_api.schemas.jd_match import JDMatchRequest, JDMatchResponse, SemanticMatchItem
from backend_api.services import resume_service, jd_service

router = APIRouter()


@router.post("/match-jd", response_model=JDMatchResponse)
async def match_jd(body: JDMatchRequest):
    if not body.job_description.strip():
        raise HTTPException(status_code=400, detail="job_description cannot be empty")

    try:
        path = resume_service.get_resume_path(body.resume_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")

    try:
        data = await asyncio.to_thread(jd_service.match, path, body.job_description)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Matching failed: {exc}")

    semantic = [
        SemanticMatchItem(**sm)
        for sm in data.get("semantic_matches", [])
        if isinstance(sm, dict)
    ]

    return JDMatchResponse(
        match_score=float(data.get("match_score", 0)),
        confidence=data.get("confidence", "low"),
        total_jd_skills=int(data.get("total_jd_skills", 0)),
        matching_skills=data.get("matching_skills", []),
        semantic_matches=semantic,
        missing_skills=data.get("missing_skills", []),
        recommendations=data.get("recommendations", []),
        category_tips=data.get("category_tips", {}),
    )
