import asyncio
from fastapi import APIRouter, HTTPException

from backend_api.schemas.skill_gap import SkillGapRequest, SkillGapResponse, SemanticGapItem
from backend_api.services import resume_service, skill_gap_service

router = APIRouter()


@router.post("/skill-gap", response_model=SkillGapResponse)
async def skill_gap(body: SkillGapRequest):
    try:
        path = resume_service.get_resume_path(body.resume_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")

    try:
        data = await asyncio.to_thread(
            skill_gap_service.analyze, path, body.jd_text
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Skill gap analysis failed: {exc}")

    semantic_gaps = [
        SemanticGapItem(**sg)
        for sg in data.get("semantic_gaps", [])
        if isinstance(sg, dict)
    ]

    return SkillGapResponse(
        resume_skills=data.get("resume_skills", []),
        missing_skills=data.get("missing_skills", []),
        semantic_gaps=semantic_gaps,
        recommendations=data.get("recommendations", []),
        category_tips=data.get("category_tips", {}),
        match_score=float(data.get("match_score", 0)),
    )
