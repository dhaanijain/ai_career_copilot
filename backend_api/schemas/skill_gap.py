from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class SkillGapRequest(BaseModel):
    resume_id: str = Field(
        ...,
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        description="UUID of the previously uploaded resume",
    )
    jd_text: Optional[str] = Field(
        None, max_length=20_000, description="Optional job description for targeted gap analysis"
    )
    resume_skills: Optional[List[str]] = Field(
        None, description="Pre-extracted skills — skips re-running the ML pipeline"
    )


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
