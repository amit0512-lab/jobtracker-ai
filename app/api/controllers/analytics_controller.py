import json
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timezone, timedelta
from app.models.job import Job, JobStatus, JobPriority
from app.models.resume import Resume
from app.models.user import User
from app.core.redis import get_redis


class AnalyticsController:

    # ─── Main Dashboard ───────────────────────────────────────

    @staticmethod
    async def get_dashboard(user: User, db: Session) -> dict:
        """
        Poora dashboard ek call mein — Redis cached
        """
        cache_key = f"dashboard:{user.id}"
        r = get_redis()

        # Cache check
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

        # ── Job Stats ──
        total_jobs = db.query(Job).filter(Job.user_id == user.id).count()

        # Status wise breakdown
        status_counts = (
            db.query(Job.status, func.count(Job.id))
            .filter(Job.user_id == user.id)
            .group_by(Job.status)
            .all()
        )
        status_breakdown = {s.value: c for s, c in status_counts}

        # Priority wise breakdown
        priority_counts = (
            db.query(Job.priority, func.count(Job.id))
            .filter(Job.user_id == user.id)
            .group_by(Job.priority)
            .all()
        )
        priority_breakdown = {p.value: c for p, c in priority_counts}

        # ── Top Companies ──
        top_companies = (
            db.query(Job.company, func.count(Job.id).label("count"))
            .filter(Job.user_id == user.id)
            .group_by(Job.company)
            .order_by(func.count(Job.id).desc())
            .limit(5)
            .all()
        )

        # ── Application Rate (last 30 days) ──
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_applications = (
            db.query(Job)
            .filter(
                and_(
                    Job.user_id == user.id,
                    Job.applied_at >= thirty_days_ago
                )
            )
            .count()
        )

        # ── Resume Stats ──
        total_resumes = db.query(Resume).filter(Resume.user_id == user.id).count()

        avg_match_score = (
            db.query(func.avg(Resume.match_score))
            .filter(
                and_(
                    Resume.user_id == user.id,
                    Resume.match_score > 0
                )
            )
            .scalar()
        )

        best_resume = (
            db.query(Resume)
            .filter(Resume.user_id == user.id)
            .order_by(Resume.match_score.desc())
            .first()
        )

        # ── Weekly Activity (last 7 days) ──
        weekly_data = []
        for i in range(6, -1, -1):
            day = datetime.now(timezone.utc) - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59)

            count = (
                db.query(Job)
                .filter(
                    and_(
                        Job.user_id == user.id,
                        Job.created_at >= day_start,
                        Job.created_at <= day_end
                    )
                )
                .count()
            )
            weekly_data.append({
                "date": day.strftime("%a %d %b"),
                "jobs_added": count
            })

        # ── Conversion Rates ──
        applied = status_breakdown.get("applied", 0)
        interview = status_breakdown.get("interview", 0)
        offer = status_breakdown.get("offer", 0)

        apply_rate = round((applied / total_jobs * 100), 1) if total_jobs else 0
        interview_rate = round((interview / applied * 100), 1) if applied else 0
        offer_rate = round((offer / interview * 100), 1) if interview else 0

        result = {
            "summary": {
                "total_jobs": total_jobs,
                "total_resumes": total_resumes,
                "recent_applications_30d": recent_applications,
                "avg_resume_match_score": round(avg_match_score or 0, 1),
                "best_resume_score": round(best_resume.match_score if best_resume else 0, 1)
            },
            "status_breakdown": status_breakdown,
            "priority_breakdown": priority_breakdown,
            "conversion_rates": {
                "applied_rate": apply_rate,
                "interview_rate": interview_rate,
                "offer_rate": offer_rate
            },
            "top_companies": [
                {"company": c, "count": count}
                for c, count in top_companies
            ],
            "weekly_activity": weekly_data,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        # Cache mein save karo — 15 min
        await r.set(cache_key, json.dumps(result), ex=900)

        return result

    # ─── Invalidate Dashboard Cache ───────────────────────────

    @staticmethod
    async def invalidate_dashboard_cache(user_id: str):
        r = get_redis()
        await r.delete(f"dashboard:{user_id}")

    # ─── Job Timeline ─────────────────────────────────────────

    @staticmethod
    async def get_job_timeline(user: User, db: Session) -> list[dict]:
        """Status changes ka timeline"""
        jobs = (
            db.query(Job)
            .filter(
                and_(
                    Job.user_id == user.id,
                    Job.applied_at.isnot(None)
                )
            )
            .order_by(Job.applied_at.desc())
            .limit(20)
            .all()
        )

        timeline = []
        for job in jobs:
            timeline.append({
                "job_id": str(job.id),
                "title": job.title,
                "company": job.company,
                "status": job.status.value,
                "applied_at": job.applied_at.isoformat() if job.applied_at else None,
                "interview_at": job.interview_at.isoformat() if job.interview_at else None,
            })

        return timeline