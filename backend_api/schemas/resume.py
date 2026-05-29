from pydantic import BaseModel
from typing import List


class ResumeUploadResponse(BaseModel):
    resume_id: str
    skills: List[str]
    total_skills: int
