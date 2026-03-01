import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from app.models.job import Job, JobStatus, JobPriority
from app.models.user import User
from app.schemas.job import JobCreateRequest, JobUpdateRequest, JobResponse, JobListResponse
from app.core.redis import get_redis


# Cache key helper
def _cache_key(user_id: str, page: int, per_page: int, status: str = None) -> str:
    return f"jobs:{user_id}:page={page}:per={per_page}:status={status or 'all'}"


class JobController:

    # ─── Create Job ───────────────────────────────────────────

    @staticmethod
    async def create_job(data: JobCreateRequest, user: User, db: Session) -> JobResponse:
        job = Job(
            user_id=user.id,
            title=data.title,
            company=data.company,
            location=data.location,
            job_url=data.job_url,
            description=data.description,
            priority=data.priority,
            notes=data.notes,
            salary_min=data.salary_min,
            salary_max=data.salary_max,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Cache invalidate karo — naya job aaya hai
        await JobController._invalidate_cache(str(user.id))

        return JobResponse.model_validate(job)

    # ─── Get All Jobs (Paginated + Filtered) ──────────────────

    @staticmethod
    async def get_jobs(
        user: User,
        db: Session,
        page: int = 1,
        per_page: int = 10,
        status: JobStatus = None,
        priority: JobPriority = None,
        search: str = None
    ) -> JobListResponse:

        # Redis cache check karo (sirf simple queries ke liye)
        if not search and not priority:
            cache_key = _cache_key(str(user.id), page, per_page, status)
            r = get_redis()
            cached = await r.get(cache_key)
            if cached:
                return JobListResponse(**json.loads(cached))

        # DB query build karo
        query = db.query(Job).filter(Job.user_id == user.id)

        # Filters
        if status:
            query = query.filter(Job.status == status)
        if priority:
            query = query.filter(Job.priority == priority)
        if search:
            query = query.filter(
                Job.title.ilike(f"%{search}%") |
                Job.company.ilike(f"%{search}%")
            )

        # Total count
        total = query.count()

        # Pagination
        jobs = (
            query
            .order_by(Job.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        result = JobListResponse(
            total=total,
            page=page,
            per_page=per_page,
            jobs=[JobResponse.model_validate(j) for j in jobs]
        )

        # Cache mein save karo — 5 min ke liye
        if not search and not priority:
            r = get_redis()
            await r.set(cache_key, result.model_dump_json(), ex=300)

        return result

    # ─── Get Single Job ───────────────────────────────────────

    @staticmethod
    async def get_job(job_id: UUID, user: User, db: Session) -> JobResponse:
        job = db.query(Job).filter(
            and_(Job.id == job_id, Job.user_id == user.id)
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job nahi mili"
            )

        return JobResponse.model_validate(job)

    # ─── Update Job ───────────────────────────────────────────

    @staticmethod
    async def update_job(
        job_id: UUID,
        data: JobUpdateRequest,
        user: User,
        db: Session
    ) -> JobResponse:

        job = db.query(Job).filter(
            and_(Job.id == job_id, Job.user_id == user.id)
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job nahi mili"
            )

        # Sirf wahi fields update karo jo aaye hain
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        db.commit()
        db.refresh(job)

        # Cache invalidate karo
        await JobController._invalidate_cache(str(user.id))

        return JobResponse.model_validate(job)

    # ─── Update Status Only ───────────────────────────────────

    @staticmethod
    async def update_status(
        job_id: UUID,
        new_status: JobStatus,
        user: User,
        db: Session
    ) -> JobResponse:

        job = db.query(Job).filter(
            and_(Job.id == job_id, Job.user_id == user.id)
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job nahi mili"
            )

        job.status = new_status

        # Applied hone pe timestamp set karo
        if new_status == JobStatus.APPLIED:
            from datetime import datetime, timezone
            job.applied_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(job)
        await JobController._invalidate_cache(str(user.id))

        return JobResponse.model_validate(job)

    # ─── Delete Job ───────────────────────────────────────────

    @staticmethod
    async def delete_job(job_id: UUID, user: User, db: Session) -> dict:
        job = db.query(Job).filter(
            and_(Job.id == job_id, Job.user_id == user.id)
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job nahi mili"
            )

        db.delete(job)
        db.commit()
        await JobController._invalidate_cache(str(user.id))

        return {"message": "Job delete ho gayi"}

    # ─── Cache Invalidation ───────────────────────────────────

    @staticmethod
    async def _invalidate_cache(user_id: str):
        """User ke saare job cache keys delete karo"""
        r = get_redis()
        # Pattern se saare keys dhundho aur delete karo
        keys = await r.keys(f"jobs:{user_id}:*")
        if keys:
            await r.delete(*keys)