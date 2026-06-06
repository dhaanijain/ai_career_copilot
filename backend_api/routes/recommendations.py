import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from backend_api.middleware.auth import optional_user
from backend_api.schemas.recommendations import (
    JobRecommendation,
    RecommendJobsRequest,
    RecommendationsResponse,
    SemanticMatchItem,
)
from backend_api.services import recommendation_service, resume_service

router = APIRouter()


@router.post(
    "/recommend-jobs",
    response_model=RecommendationsResponse,
    summary="Fetch live job recommendations ranked by resume match",
    description=(
        "Fetches live jobs from the Adzuna API, scores each against your resume skills "
        "using semantic matching, and returns them ranked by match score. "
        "Pass `resume_skills` from a previous upload response to skip re-running the ML pipeline."
    ),
    responses={
        404: {"description": "Resume not found — upload first"},
        422: {"description": "Validation error (invalid UUID, top_n out of range, etc.)"},
        500: {"description": "Job fetching or ranking failed"},
    },
)
async def recommend_jobs(
    body: RecommendJobsRequest,
    user_id: Optional[str] = Depends(optional_user),
):
    try:
        path = resume_service.get_resume_path(body.resume_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")

    query = body.query or "software engineer machine learning"
    location = body.location or ""
    top_n = body.top_n or 10

    try:
        data = await asyncio.to_thread(
            recommendation_service.get_recommendations,
            path,
            query,
            location,
            top_n,
            body.resume_skills,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {exc}")

    if user_id:
        await asyncio.to_thread(
            recommendation_service.save_recommendations_to_supabase,
            data,
            body.resume_id,
            user_id,
            query,
            location,
            top_n,
        )

    jobs = []
    for job in data.get("jobs", []):
        semantic = [
            SemanticMatchItem(**sm)
            for sm in job.get("semantic_matches", [])
            if isinstance(sm, dict)
        ]
        jobs.append(
            JobRecommendation(
                title=job.get("title", ""),
                company=job.get("company", ""),
                location=job.get("location", ""),
                match_score=float(job.get("match_score", 0)),
                matching_skills=job.get("matching_skills", []),
                semantic_matches=semantic,
                missing_skills=job.get("missing_skills", []),
                recommendations=job.get("recommendations", []),
                redirect_url=job.get("redirect_url", ""),
            )
        )

    return RecommendationsResponse(
        jobs=jobs,
        total_jobs=len(jobs),
        resume_skills=data.get("resume_skills", []),
    )
