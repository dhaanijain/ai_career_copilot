from pydantic import BaseModel
from typing import List, Dict, Optional


class SkillGapRequest(BaseModel):
    resume_id: str
    jd_text: Optional[str] = None
    resume_skills: Optional[List[str]] = None  # skip re-extraction if provided


class SemanticGapItem(BaseModel):
    resume_skill: str
    jd_skill: str
    similarity: float


class SkillGapResponse(BaseModel):
    resume_skills: List[str]
    missing_skills: List[str]
    semantic_gaps: List[SemanticGapItem]
    recommendations: List[str]
    category_tips: Dict[str, str]
    match_score: float
