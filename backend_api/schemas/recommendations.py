from pydantic import BaseModel, Field
from typing import List, Optional


class RecommendJobsRequest(BaseModel):
    resume_id: str = Field(
        ...,
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        description="UUID of the previously uploaded resume",
    )
    query: Optional[str] = Field(
        "software engineer machine learning",
        max_length=200,
        description="Job search query sent to Adzuna",
    )
    location: Optional[str] = Field(
        "", max_length=100, description="Location filter (city, country, etc.)"
    )
    top_n: Optional[int] = Field(
        10, ge=1, le=50, description="Number of job recommendations to return (1–50)"
    )
    resume_skills: Optional[List[str]] = Field(
        None, description="Pre-extracted skills — skips re-running the ML pipeline"
    )


class SemanticMatchItem(BaseModel):
    resume_skill: str
    jd_skill: str
    similarity: float


class JobRecommendation(BaseModel):
    title: str
    company: str
    location: str
    match_score: float
    matching_skills: List[str]
    semantic_matches: List[SemanticMatchItem]
    missing_skills: List[str]
    recommendations: List[str]
    redirect_url: str


class RecommendationsResponse(BaseModel):
    jobs: List[JobRecommendation]
    total_jobs: int
    resume_skills: List[str]
