from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class CoverLetterGenerate(BaseModel):
    job_id: UUID
    resume_id: Optional[UUID] = None
    tone: str = Field(default="professional", pattern="^(professional|enthusiastic|creative|formal)$")


class CoverLetterUpdate(BaseModel):
    content: Optional[str] = None
    is_favorite: Optional[str] = None


class CoverLetterResponse(BaseModel):
    id: UUID
    user_id: UUID
    job_id: UUID
    resume_id: Optional[UUID]
    content: str
    tone: str
    word_count: str
    is_favorite: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CoverLetterListResponse(BaseModel):
    id: UUID
    job_id: UUID
    job_title: str
    company: str
    tone: str
    word_count: str
    is_favorite: str
    created_at: datetime

    class Config:
        from_attributes = True
