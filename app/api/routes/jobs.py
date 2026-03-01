from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.models.job import JobStatus, JobPriority
from app.schemas.job import (
    JobCreateRequest, JobUpdateRequest,
    JobResponse, JobListResponse
)
from app.api.controllers.job_controller import JobController

router = APIRouter()


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(
    data: JobCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Naya job add karo tracking ke liye"""
    return await JobController.create_job(data, current_user, db)


@router.get("", response_model=JobListResponse)
async def get_jobs(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=50),
    status: Optional[JobStatus] = Query(default=None),
    priority: Optional[JobPriority] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apni saari jobs dekho — filter, search, pagination ke saath"""
    return await JobController.get_jobs(
        current_user, db, page, per_page, status, priority, search
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ek specific job ki detail dekho"""
    return await JobController.get_job(job_id, current_user, db)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    data: JobUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Job details update karo"""
    return await JobController.update_job(job_id, data, current_user, db)


@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_status(
    job_id: UUID,
    new_status: JobStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sirf status update karo — saved/applied/interview/offer/rejected"""
    return await JobController.update_status(job_id, new_status, current_user, db)


@router.delete("/{job_id}")
async def delete_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Job delete karo"""
    return await JobController.delete_job(job_id, current_user, db)