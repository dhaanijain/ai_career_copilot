from pydantic import BaseModel
from typing import List, Optional


class RecommendJobsRequest(BaseModel):
    resume_id: str
    query: Optional[str] = "software engineer machine learning"
    location: Optional[str] = ""
    top_n: Optional[int] = 10
    resume_skills: Optional[List[str]] = None  # skip re-extraction if provided


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
