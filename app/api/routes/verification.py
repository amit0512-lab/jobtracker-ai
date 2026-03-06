"""
Email verification routes with OTP system
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.api.controllers.verification_controller import VerificationController

router = APIRouter()


class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


@router.post("/send-otp")
async def send_verification_otp(
    data: SendOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Send OTP to user's email for verification
    Rate limited to 3 requests per hour per email
    """
    return await VerificationController.send_verification_otp(data.email, db)


@router.post("/verify-otp")
async def verify_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and activate user account
    OTP is valid for 10 minutes
    """
    return await VerificationController.verify_otp(data.email, data.otp, db)


@router.post("/resend-otp")
async def resend_otp(
    data: SendOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Resend OTP to user's email
    Rate limited to 3 requests per hour per email
    """
    return await VerificationController.resend_otp(data.email, db)


@router.get("/status/{email}")
async def check_verification_status(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Check if user's email is verified
    """
    return await VerificationController.check_verification_status(email, db)
