from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.job import JobStatus, JobPriority


class JobCreateRequest(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    job_url: Optional[str] = None
    description: Optional[str] = None
    priority: JobPriority = JobPriority.MEDIUM
    notes: Optional[str] = None
    salary_min: Optional[str] = None
    salary_max: Optional[str] = None


class JobUpdateRequest(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    priority: Optional[JobPriority] = None
    notes: Optional[str] = None
    salary_min: Optional[str] = None
    salary_max: Optional[str] = None
    applied_at: Optional[datetime] = None
    interview_at: Optional[datetime] = None


class JobResponse(BaseModel):
    id: UUID
    title: str
    company: str
    location: Optional[str]
    job_url: Optional[str]
    description: Optional[str]
    status: JobStatus
    priority: JobPriority
    notes: Optional[str]
    salary_min: Optional[str]
    salary_max: Optional[str]
    applied_at: Optional[datetime]
    interview_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    jobs: list[JobResponse]