from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.api.controllers.analytics_controller import AnalyticsController

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Poora dashboard — stats, breakdown, weekly activity"""
    return await AnalyticsController.get_dashboard(current_user, db)


@router.get("/timeline")
async def get_timeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Job application timeline dekho"""
    return await AnalyticsController.get_job_timeline(current_user, db)