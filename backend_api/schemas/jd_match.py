from pydantic import BaseModel, Field
from typing import List, Dict, Any


class JDMatchRequest(BaseModel):
    resume_id: str = Field(
        ...,
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        description="UUID of the previously uploaded resume",
    )
    job_description: str = Field(
        ..., min_length=50, max_length=20_000, description="Raw job description text"
    )


class SemanticMatchItem(BaseModel):
    resume_skill: str
    jd_skill: str
    similarity: float


class JDMatchResponse(BaseModel):
    match_score: float
    confidence: str
    total_jd_skills: int
    matching_skills: List[str]
    semantic_matches: List[SemanticMatchItem]
    missing_skills: List[str]
    recommendations: List[str]
    category_tips: Dict[str, Any]
