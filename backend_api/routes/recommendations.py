import asyncio
from fastapi import APIRouter, HTTPException

from backend_api.schemas.recommendations import (
    RecommendJobsRequest,
    RecommendationsResponse,
    JobRecommendation,
    SemanticMatchItem,
)
from backend_api.services import resume_service, recommendation_service

router = APIRouter()


@router.post("/recommend-jobs", response_model=RecommendationsResponse)
async def recommend_jobs(body: RecommendJobsRequest):
    try:
        path = resume_service.get_resume_path(body.resume_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")

    try:
        data = await asyncio.to_thread(
            recommendation_service.get_recommendations,
            path,
            body.query or "software engineer machine learning",
            body.location or "",
            body.top_n or 10,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {exc}")

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
