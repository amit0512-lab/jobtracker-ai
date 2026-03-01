from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class ResumeResponse(BaseModel):
    id: UUID
    filename: str
    file_size: Optional[str]
    extracted_skills: list[Any]
    extracted_experience: list[Any]
    extracted_education: list[Any]
    keywords: list[Any]
    match_score: float
    nlp_summary: Optional[str]
    job_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeMatchRequest(BaseModel):
    job_id: UUID   # is job ki JD se resume match karo


class NLPAnalysisResponse(BaseModel):
    match_score: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    extracted_skills: list[str]
    suggestions: list[str]