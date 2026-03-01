from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest,
    TokenResponse, RefreshRequest, UserResponse
)
from app.api.controllers.auth_controller import AuthController
from app.middleware.auth_middleware import get_current_user, rate_limit
from app.models.user import User

router = APIRouter()
bearer_scheme = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Naya account banao"""
    return await AuthController.register(data, db)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login karo — access + refresh token milega"""
    # Rate limit: 5 login attempts per minute
    await rate_limit(request, max_requests=5, window=60)
    return await AuthController.login(data, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):
    """Access token expire hone pe refresh karo"""
    return await AuthController.refresh_token(data.refresh_token, db)


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user)
):
    """Logout — token blacklist ho jayega"""
    return await AuthController.logout(credentials.credentials, current_user)


@router.get("/me", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Apna profile dekho"""
    return await AuthController.get_profile(current_user)