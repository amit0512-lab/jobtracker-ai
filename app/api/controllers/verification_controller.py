"""
Email verification controller with OTP system
Handles OTP generation, sending, verification, and resending
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.email_service import EmailService
from app.core.redis import get_redis
import logging

logger = logging.getLogger(__name__)


class VerificationController:
    """Handle email verification with OTP"""
    
    # OTP expiration time (10 minutes)
    OTP_EXPIRY_SECONDS = 600
    
    # Rate limiting (max 3 OTP requests per hour per email)
    MAX_OTP_REQUESTS_PER_HOUR = 3
    RATE_LIMIT_WINDOW = 3600
    
    @staticmethod
    async def send_verification_otp(email: str, db: Session) -> dict:
        """
        Generate and send OTP to user's email
        
        Args:
            email: User's email address
            db: Database session
            
        Returns:
            dict with success message
            
        Raises:
            HTTPException: If user not found, already verified, or rate limited
        """
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already verified
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Rate limiting check
        r = get_redis()
        rate_limit_key = f"otp_rate_limit:{email}"
        request_count = await r.get(rate_limit_key)
        
        if request_count and int(request_count) >= VerificationController.MAX_OTP_REQUESTS_PER_HOUR:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests. Please try again after 1 hour."
            )
        
        # Generate OTP
        otp = EmailService.generate_otp()
        
        # Store OTP in Redis with expiration
        otp_key = f"otp:{email}"
        await r.set(otp_key, otp, ex=VerificationController.OTP_EXPIRY_SECONDS)
        
        # Increment rate limit counter
        if request_count:
            await r.incr(rate_limit_key)
        else:
            await r.set(rate_limit_key, 1, ex=VerificationController.RATE_LIMIT_WINDOW)
        
        # Send OTP email
        try:
            await EmailService.send_verification_otp(email, otp, user.full_name)
            logger.info(f"OTP sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send OTP email: {str(e)}")
            # Don't fail the request - OTP is still in Redis
        
        return {
            "message": "OTP sent to your email. Please check your inbox.",
            "expires_in_seconds": VerificationController.OTP_EXPIRY_SECONDS
        }
    
    @staticmethod
    async def verify_otp(email: str, otp: str, db: Session) -> dict:
        """
        Verify OTP and activate user account
        
        Args:
            email: User's email address
            otp: 6-digit OTP code
            db: Database session
            
        Returns:
            dict with success message
            
        Raises:
            HTTPException: If OTP invalid, expired, or user not found
        """
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already verified
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Get OTP from Redis
        r = get_redis()
        otp_key = f"otp:{email}"
        stored_otp = await r.get(otp_key)
        
        if not stored_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired or not found. Please request a new one."
            )
        
        # Verify OTP
        if stored_otp != otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP. Please check and try again."
            )
        
        # Mark user as verified
        user.is_verified = True
        db.commit()
        
        # Delete OTP from Redis
        await r.delete(otp_key)
        
        # Clear rate limit counter
        rate_limit_key = f"otp_rate_limit:{email}"
        await r.delete(rate_limit_key)
        
        # Send welcome email
        try:
            await EmailService.send_welcome_email(email, user.full_name)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
        
        logger.info(f"Email verified successfully for {email}")
        
        return {
            "message": "Email verified successfully! You can now login.",
            "is_verified": True
        }
    
    @staticmethod
    async def resend_otp(email: str, db: Session) -> dict:
        """
        Resend OTP to user's email
        Same as send_verification_otp but with different message
        """
        result = await VerificationController.send_verification_otp(email, db)
        result["message"] = "OTP resent to your email. Please check your inbox."
        return result
    
    @staticmethod
    async def check_verification_status(email: str, db: Session) -> dict:
        """
        Check if user's email is verified
        
        Args:
            email: User's email address
            db: Database session
            
        Returns:
            dict with verification status
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "email": email,
            "is_verified": user.is_verified
        }
