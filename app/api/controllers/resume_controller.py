import json
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from app.models.resume import Resume
from app.models.job import Job
from app.models.user import User
from app.schemas.resume import ResumeResponse, NLPAnalysisResponse
from app.services.storage.s3_service import StorageService
from app.services.nlp.resume_parser import ResumeParser
from app.services.nlp.jd_matcher import JDMatcher
from app.core.redis import get_redis


class ResumeController:

    # ─── Upload Resume ────────────────────────────────────────

    @staticmethod
    async def upload_resume(
        file: UploadFile,
        job_id: UUID = None,
        user: User = None,
        db: Session = None
    ) -> ResumeResponse:

        # File upload karo
        upload_result = await StorageService.upload_file(file)

        # NLP parse karo
        try:
            parsed = ResumeParser.parse_resume(upload_result["file_path"])
        except Exception as e:
            parsed = {
                "skills": [], "keywords": [],
                "experience": [], "education": [], "raw_text": ""
            }

        # Job ki JD se match score nikalo agar job_id diya
        match_score = 0.0
        if job_id:
            job = db.query(Job).filter(
                and_(Job.id == job_id, Job.user_id == user.id)
            ).first()
            if job and job.description:
                match_result = JDMatcher.calculate_match_score(
                    parsed["raw_text"], job.description
                )
                match_score = match_result["match_score"]

        # DB mein save karo
        resume = Resume(
            user_id=user.id,
            job_id=job_id,
            filename=upload_result["filename"],
            file_path=upload_result["file_path"],
            file_size=upload_result["file_size"],
            extracted_skills=parsed["skills"],
            extracted_experience=parsed["experience"],
            extracted_education=parsed["education"],
            keywords=parsed["keywords"],
            match_score=match_score,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        return ResumeResponse.model_validate(resume)

    # ─── Get All Resumes ──────────────────────────────────────

    @staticmethod
    async def get_resumes(user: User, db: Session) -> list[ResumeResponse]:
        resumes = db.query(Resume).filter(Resume.user_id == user.id)\
            .order_by(Resume.created_at.desc()).all()
        return [ResumeResponse.model_validate(r) for r in resumes]

    # ─── Get Single Resume ────────────────────────────────────

    @staticmethod
    async def get_resume(resume_id: UUID, user: User, db: Session) -> ResumeResponse:
        resume = db.query(Resume).filter(
            and_(Resume.id == resume_id, Resume.user_id == user.id)
        ).first()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume nahi mila"
            )

        return ResumeResponse.model_validate(resume)

    # ─── Analyze Resume vs JD ─────────────────────────────────

    @staticmethod
    async def analyze_resume(
        resume_id: UUID,
        job_id: UUID,
        user: User,
        db: Session
    ) -> NLPAnalysisResponse:

        # Redis cache check
        cache_key = f"analysis:{resume_id}:{job_id}"
        r = get_redis()
        cached = await r.get(cache_key)
        if cached:
            return NLPAnalysisResponse(**json.loads(cached))

        # Resume aur Job fetch karo
        resume = db.query(Resume).filter(
            and_(Resume.id == resume_id, Resume.user_id == user.id)
        ).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume nahi mila")

        job = db.query(Job).filter(
            and_(Job.id == job_id, Job.user_id == user.id)
        ).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job nahi mili")

        if not job.description:
            raise HTTPException(
                status_code=400,
                detail="Is job mein description nahi hai — pehle JD add karo"
            )

        # Resume text dobara nikalo
        try:
            resume_text = ResumeParser.extract_text_from_file(resume.file_path)
        except Exception:
            resume_text = " ".join(resume.extracted_skills + resume.keywords)

        # Match calculate karo
        match_result = JDMatcher.calculate_match_score(resume_text, job.description)

        # DB update karo
        resume.match_score = match_result["match_score"]
        db.commit()

        result = NLPAnalysisResponse(
            match_score=match_result["match_score"],
            matched_keywords=match_result["matched_keywords"],
            missing_keywords=match_result["missing_keywords"],
            extracted_skills=resume.extracted_skills,
            suggestions=match_result["suggestions"]
        )

        # Cache mein save karo — 10 min
        await r.set(cache_key, result.model_dump_json(), ex=600)

        return result

    # ─── Delete Resume ────────────────────────────────────────

    @staticmethod
    async def delete_resume(resume_id: UUID, user: User, db: Session) -> dict:
        resume = db.query(Resume).filter(
            and_(Resume.id == resume_id, Resume.user_id == user.id)
        ).first()

        if not resume:
            raise HTTPException(status_code=404, detail="Resume nahi mila")

        # File bhi delete karo
        await StorageService.delete_file(resume.file_path)

        db.delete(resume)
        db.commit()

        return {"message": "Resume delete ho gaya"}