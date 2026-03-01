from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import timezone, datetime, timedelta
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    blacklist_token,
    is_token_blacklisted
)
from app.core.config import settings


class AuthController:

    # ─── Register ─────────────────────────────────────────────

    @staticmethod
    async def register(data: RegisterRequest, db: Session) -> UserResponse:

        # Email already exist karta hai?
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Is email se account pehle se exist karta hai"
            )

        # User banao
        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return UserResponse.model_validate(user)

    # ─── Login ────────────────────────────────────────────────

    @staticmethod
    async def login(data: LoginRequest, db: Session) -> TokenResponse:

        # User fetch karo
        user = db.query(User).filter(User.email == data.email).first()

        # Email ya password galat
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ya password galat hai"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account deactivated hai"
            )

        # Tokens banao
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    # ─── Refresh Token ────────────────────────────────────────

    @staticmethod
    async def refresh_token(refresh_token: str, db: Session) -> TokenResponse:

        # Blacklisted hai?
        if await is_token_blacklisted(refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalid hai, dobara login karo"
            )

        # Decode karo
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # User exist karta hai?
        from uuid import UUID
        user = db.query(User).filter(User.id == UUID(payload["sub"])).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User nahi mila"
            )

        # Purana refresh token blacklist karo
        exp = payload.get("exp")
        remaining = exp - int(datetime.now(timezone.utc).timestamp())
        if remaining > 0:
            await blacklist_token(refresh_token, remaining)

        # Naye tokens banao
        token_data = {"sub": str(user.id), "email": user.email}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data)
        )

    # ─── Logout ───────────────────────────────────────────────

    @staticmethod
    async def logout(token: str, user: User) -> dict:
        payload = decode_token(token)
        if payload:
            exp = payload.get("exp")
            remaining = exp - int(datetime.now(timezone.utc).timestamp())
            if remaining > 0:
                await blacklist_token(token, remaining)  # token blacklist ho gaya

        return {"message": f"{user.full_name}, aap logout ho gaye hain"}

    # ─── Me (Profile) ─────────────────────────────────────────

    @staticmethod
    async def get_profile(user: User) -> UserResponse:
        return UserResponse.model_validate(user)