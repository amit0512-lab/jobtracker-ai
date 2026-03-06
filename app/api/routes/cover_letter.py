from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user, rate_limit
from app.models.user import User
from app.schemas.cover_letter import (
    CoverLetterGenerate,
    CoverLetterUpdate,
    CoverLetterResponse,
    CoverLetterListResponse
)
from app.api.controllers.cover_letter_controller import CoverLetterController
import logging

router = APIRouter(tags=["Cover Letters"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=CoverLetterResponse, status_code=status.HTTP_201_CREATED)
async def generate_cover_letter(
    request: Request,
    data: CoverLetterGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered cover letter for a job
    
    - **job_id**: Job to generate cover letter for
    - **resume_id**: Optional resume to use (uses generic if not provided)
    - **tone**: professional, enthusiastic, creative, or formal
    
    Rate limit: 10 requests per hour (expensive OpenAI API calls)
    """
    # Rate limit: 10 generations per hour
    await rate_limit(request, max_requests=10, window=1)
    
    try:
        logger.info(f"Generating cover letter for user {current_user.id}, job {data.job_id}")
        result = await CoverLetterController.generate_cover_letter(
            job_id=data.job_id,
            resume_id=data.resume_id,
            tone=data.tone,
            user_id=current_user.id,
            db=db
        )
        logger.info(f"Successfully generated cover letter, ID: {result['id']}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cover letter generation failed: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate cover letter")


@router.get("", response_model=List[CoverLetterListResponse])
def get_all_cover_letters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all cover letters for current user"""
    return CoverLetterController.get_cover_letters(
        user_id=current_user.id,
        db=db
    )


@router.get("/{cover_letter_id}", response_model=CoverLetterResponse)
def get_cover_letter(
    cover_letter_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific cover letter by ID"""
    return CoverLetterController.get_cover_letter_by_id(
        cover_letter_id=cover_letter_id,
        user_id=current_user.id,
        db=db
    )


@router.get("/job/{job_id}", response_model=List[CoverLetterResponse])
def get_cover_letters_by_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all cover letters for a specific job"""
    return CoverLetterController.get_cover_letters_by_job(
        job_id=job_id,
        user_id=current_user.id,
        db=db
    )


@router.patch("/{cover_letter_id}", response_model=CoverLetterResponse)
def update_cover_letter(
    cover_letter_id: UUID,
    data: CoverLetterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cover letter content or mark as favorite"""
    return CoverLetterController.update_cover_letter(
        cover_letter_id=cover_letter_id,
        content=data.content,
        is_favorite=data.is_favorite,
        user_id=current_user.id,
        db=db
    )


@router.delete("/{cover_letter_id}", status_code=status.HTTP_200_OK)
def delete_cover_letter(
    cover_letter_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete cover letter"""
    return CoverLetterController.delete_cover_letter(
        cover_letter_id=cover_letter_id,
        user_id=current_user.id,
        db=db
    )
