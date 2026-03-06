from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional
from app.models.cover_letter import CoverLetter
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.services.ai.cover_letter_generator import CoverLetterGenerator
from app.services.nlp.resume_parser import ResumeParser
import os


class CoverLetterController:

    @staticmethod
    async def generate_cover_letter(
        job_id: UUID,
        resume_id: Optional[UUID],
        tone: str,
        user_id: UUID,
        db: Session
    ) -> CoverLetter:
        """Generate AI cover letter for a job"""
        
        # Get job
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if not job.description:
            raise HTTPException(status_code=400, detail="Job description is required to generate cover letter")
        
        # Get resume text
        resume_text = ""
        if resume_id:
            resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")
            
            # Extract text from resume file
            try:
                resume_text = ResumeParser.extract_text_from_file(resume.file_path)
            except Exception as e:
                print(f"Error reading resume: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Failed to read resume: {str(e)}")
        else:
            # Use a generic resume template if no resume provided
            resume_text = "Experienced professional with strong technical skills and proven track record."
        
        # Get user name
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.full_name if user else None
        
        # Generate cover letter using AI
        try:
            result = await CoverLetterGenerator.generate(
                resume_text=resume_text,
                job_title=job.title,
                company=job.company,
                job_description=job.description,
                tone=tone,
                user_name=user_name
            )
        except Exception as e:
            print(f"Error generating cover letter: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to generate cover letter: {str(e)}")
        
        # Save to database
        cover_letter = CoverLetter(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            content=result["content"],
            tone=tone.lower(),  # Pass lowercase string directly
            word_count=str(result["word_count"]),
            is_favorite="false"
        )
        
        db.add(cover_letter)
        db.commit()
        db.refresh(cover_letter)
        
        # Return with job details for frontend display
        return {
            "id": str(cover_letter.id),
            "job_id": str(cover_letter.job_id),
            "job_title": job.title,
            "company": job.company,
            "resume_id": str(cover_letter.resume_id) if cover_letter.resume_id else None,
            "content": cover_letter.content,
            "tone": str(cover_letter.tone) if cover_letter.tone else "professional",
            "word_count": cover_letter.word_count,
            "is_favorite": cover_letter.is_favorite,
            "created_at": cover_letter.created_at.isoformat() if cover_letter.created_at else None
        }

    @staticmethod
    def get_cover_letters(user_id: UUID, db: Session) -> list:
        """Get all cover letters for user with job details"""
        cover_letters = (
            db.query(CoverLetter, Job.title, Job.company)
            .join(Job, CoverLetter.job_id == Job.id)
            .filter(CoverLetter.user_id == user_id)
            .order_by(desc(CoverLetter.created_at))
            .all()
        )
        
        return [
            {
                "id": str(cl.id),
                "job_id": str(cl.job_id),
                "job_title": title,
                "company": company,
                "tone": str(cl.tone) if cl.tone else "professional",
                "word_count": cl.word_count,
                "is_favorite": cl.is_favorite,
                "created_at": cl.created_at.isoformat() if cl.created_at else None
            }
            for cl, title, company in cover_letters
        ]

    @staticmethod
    def get_cover_letter_by_id(cover_letter_id: UUID, user_id: UUID, db: Session) -> CoverLetter:
        """Get specific cover letter"""
        cover_letter = db.query(CoverLetter).filter(
            CoverLetter.id == cover_letter_id,
            CoverLetter.user_id == user_id
        ).first()
        
        if not cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not found")
        
        return cover_letter

    @staticmethod
    def get_cover_letters_by_job(job_id: UUID, user_id: UUID, db: Session) -> list:
        """Get all cover letters for a specific job"""
        cover_letters = db.query(CoverLetter).filter(
            CoverLetter.job_id == job_id,
            CoverLetter.user_id == user_id
        ).order_by(desc(CoverLetter.created_at)).all()
        
        return cover_letters

    @staticmethod
    def update_cover_letter(
        cover_letter_id: UUID,
        content: Optional[str],
        is_favorite: Optional[str],
        user_id: UUID,
        db: Session
    ) -> CoverLetter:
        """Update cover letter content or favorite status"""
        cover_letter = db.query(CoverLetter).filter(
            CoverLetter.id == cover_letter_id,
            CoverLetter.user_id == user_id
        ).first()
        
        if not cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not found")
        
        if content is not None:
            cover_letter.content = content
            cover_letter.word_count = str(len(content.split()))
        
        if is_favorite is not None:
            cover_letter.is_favorite = is_favorite
        
        db.commit()
        db.refresh(cover_letter)
        
        return cover_letter

    @staticmethod
    def delete_cover_letter(cover_letter_id: UUID, user_id: UUID, db: Session):
        """Delete cover letter"""
        cover_letter = db.query(CoverLetter).filter(
            CoverLetter.id == cover_letter_id,
            CoverLetter.user_id == user_id
        ).first()
        
        if not cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not found")
        
        db.delete(cover_letter)
        db.commit()
        
        return {"message": "Cover letter deleted successfully"}
