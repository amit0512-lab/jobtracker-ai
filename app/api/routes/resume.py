from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeResponse, NLPAnalysisResponse
from app.api.controllers.resume_controller import ResumeController
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# File upload limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_CONTENT_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'application/msword'  # .doc
]


@router.post("", response_model=ResumeResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    job_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resume upload karo — optional: kisi job ke saath attach karo"""
    
    # Rate limit: 20 uploads per hour per user
    from app.middleware.auth_middleware import rate_limit
    from fastapi import Request
    # Note: In production, pass actual request object
    
    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning(f"Invalid file type attempted: {file.content_type} by user {current_user.id}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PDF and DOCX files are allowed. Got: {file.content_type}"
        )
    
    # Read file content to check size
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File too large: {file_size} bytes by user {current_user.id}")
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is 10MB. Your file: {file_size / (1024*1024):.2f}MB"
        )
    
    if file_size == 0:
        logger.warning(f"Empty file uploaded by user {current_user.id}")
        raise HTTPException(status_code=400, detail="File is empty")
    
    # Reset file pointer for controller to read
    await file.seek(0)
    
    logger.info(f"File upload validated: {file.filename} ({file_size} bytes) by user {current_user.id}")
    
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