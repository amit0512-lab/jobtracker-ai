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
from app.services.email_service import EmailService
from app.core.redis import get_redis
import logging

logger = logging.getLogger(__name__)


class AuthController:

    # ─── Register ─────────────────────────────────────────────

    @staticmethod
    async def register(data: RegisterRequest, db: Session) -> dict:

        # Check if email already exists
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists"
            )

        # Create user (DEVELOPMENT MODE: auto-verified)
        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            is_verified=True  # DEVELOPMENT: Skip email verification
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # DEVELOPMENT MODE: OTP verification disabled
        # Uncomment below for production email verification
        
        # # Generate and send OTP
        # otp = EmailService.generate_otp()
        # 
        # # Store OTP in Redis (10 minutes expiry)
        # r = get_redis()
        # otp_key = f"otp:{user.email}"
        # await r.set(otp_key, otp, ex=600)
        # 
        # # Send OTP email
        # try:
        #     await EmailService.send_verification_otp(user.email, otp, user.full_name)
        #     logger.info(f"Registration successful for {user.email}. OTP sent.")
        # except Exception as e:
        #     logger.error(f"Failed to send OTP email: {str(e)}")
        #     # Don't fail registration - user can request OTP again

        return {
            "message": "Registration successful! You can now login.",
            "email": user.email,
            "is_verified": True,
            "user": UserResponse.model_validate(user)
        }

    # ─── Login ────────────────────────────────────────────────

    @staticmethod
    async def login(data: LoginRequest, db: Session) -> TokenResponse:

        # Fetch user from database
        user = db.query(User).filter(User.email == data.email).first()

        # Check email and password
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # DEVELOPMENT MODE: Email verification check disabled
        # Uncomment below for production email verification
        
        # # Check if email is verified
        # if not user.is_verified:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Email not verified. Please verify your email first."
        #     )

        # Create tokens
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

        # Check if blacklisted
        if await is_token_blacklisted(refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid, please login again"
            )

        # Decode token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Check if user exists
        from uuid import UUID
        user = db.query(User).filter(User.id == UUID(payload["sub"])).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Blacklist old refresh token
        exp = payload.get("exp")
        remaining = exp - int(datetime.now(timezone.utc).timestamp())
        if remaining > 0:
            await blacklist_token(refresh_token, remaining)

        # Create new tokens
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
                await blacklist_token(token, remaining)  # Blacklist the token

        return {"message": f"{user.full_name}, you have been logged out successfully"}

    # ─── Me (Profile) ─────────────────────────────────────────

    @staticmethod
    async def get_profile(user: User) -> UserResponse:
        return UserResponse.model_validate(user)