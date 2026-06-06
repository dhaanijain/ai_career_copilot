import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from backend_api.middleware.auth import optional_user
from backend_api.schemas.skill_gap import SemanticGapItem, SkillGapRequest, SkillGapResponse
from backend_api.services import resume_service, skill_gap_service

router = APIRouter()


@router.post("/skill-gap", response_model=SkillGapResponse)
async def skill_gap(
    body: SkillGapRequest,
    user_id: Optional[str] = Depends(optional_user),
):
    try:
        path = resume_service.get_resume_path(body.resume_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")

    try:
        data = await asyncio.to_thread(
            skill_gap_service.analyze, path, body.jd_text, body.resume_skills
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Skill gap analysis failed: {exc}")

    if user_id:
        await asyncio.to_thread(
            skill_gap_service.save_skill_gap_to_supabase,
            data,
            body.resume_id,
            user_id,
            body.jd_text,
        )

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
