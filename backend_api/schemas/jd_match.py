from pydantic import BaseModel
from typing import List, Dict, Any


class JDMatchRequest(BaseModel):
    resume_id: str
    job_description: str


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
