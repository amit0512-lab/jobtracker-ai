from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeResponse, NLPAnalysisResponse
from app.api.controllers.resume_controller import ResumeController

router = APIRouter()


@router.post("", response_model=ResumeResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    job_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resume upload karo — optional: kisi job ke saath attach karo"""
    return await ResumeController.upload_resume(file, job_id, current_user, db)


@router.get("", response_model=list[ResumeResponse])
async def get_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apne saare resumes dekho"""
    return await ResumeController.get_resumes(current_user, db)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ek resume ki detail dekho"""
    return await ResumeController.get_resume(resume_id, current_user, db)


@router.get("/{resume_id}/analyze", response_model=NLPAnalysisResponse)
async def analyze_resume(
    resume_id: UUID,
    job_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resume ko JD se match karo — score + suggestions milega"""
    return await ResumeController.analyze_resume(resume_id, job_id, current_user, db)


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resume delete karo"""
    return await ResumeController.delete_resume(resume_id, current_user, db)