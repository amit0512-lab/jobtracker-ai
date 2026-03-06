"""
Email service for sending verification OTPs and notifications
Supports SMTP (Gmail, SendGrid, etc.) with fallback to console logging
"""
import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service with OTP generation and sending"""
    
    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    async def send_verification_otp(email: str, otp: str, user_name: str) -> bool:
        """
        Send OTP verification email
        
        Args:
            email: Recipient email address
            otp: 6-digit OTP code
            user_name: User's full name
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        subject = "Verify Your JobTracker Account - OTP Code"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-box {{ background: white; border: 2px dashed #6366f1; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #6366f1; letter-spacing: 8px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
                .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>◈ JobTracker</h1>
                    <p>Email Verification</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name}!</h2>
                    <p>Thank you for registering with JobTracker. To complete your registration and verify your email address, please use the OTP code below:</p>
                    
                    <div class="otp-box">
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">Your OTP Code</p>
                        <div class="otp-code">{otp}</div>
                        <p style="margin: 10px 0 0 0; color: #6b7280; font-size: 12px;">Valid for 10 minutes</p>
                    </div>
                    
                    <p>Enter this code on the verification page to activate your account.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong> Never share this OTP with anyone. JobTracker will never ask for your OTP via phone or email.
                    </div>
                    
                    <p>If you didn't request this verification, please ignore this email or contact support if you have concerns.</p>
                    
                    <p>Best regards,<br>The JobTracker Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply.</p>
                    <p>&copy; 2026 JobTracker. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        JobTracker - Email Verification
        
        Hello {user_name}!
        
        Thank you for registering with JobTracker. To complete your registration, please use the OTP code below:
        
        Your OTP Code: {otp}
        (Valid for 10 minutes)
        
        Enter this code on the verification page to activate your account.
        
        Security Notice: Never share this OTP with anyone.
        
        If you didn't request this verification, please ignore this email.
        
        Best regards,
        The JobTracker Team
        """
        
        return await EmailService._send_email(email, subject, html_body, text_body)
    
    @staticmethod
    async def send_welcome_email(email: str, user_name: str) -> bool:
        """Send welcome email after successful verification"""
        subject = "Welcome to JobTracker! 🎉"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #6366f1; }}
                .cta {{ text-align: center; margin: 30px 0; }}
                .button {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>◈ Welcome to JobTracker!</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name}! 🎉</h2>
                    <p>Your email has been verified successfully! You're all set to start tracking your job applications.</p>
                    
                    <h3>What you can do with JobTracker:</h3>
                    
                    <div class="feature">
                        <strong>📋 Track Job Applications</strong><br>
                        Keep all your job applications organized in one place
                    </div>
                    
                    <div class="feature">
                        <strong>📄 Analyze Resumes</strong><br>
                        Upload your resume and match it against job descriptions
                    </div>
                    
                    <div class="feature">
                        <strong>✍️ Generate Cover Letters</strong><br>
                        Create personalized cover letters for each application
                    </div>
                    
                    <div class="feature">
                        <strong>📊 View Analytics</strong><br>
                        Track your application progress with visual dashboards
                    </div>
                    
                    <div class="cta">
                        <a href="http://localhost:3000/dashboard" class="button">Go to Dashboard</a>
                    </div>
                    
                    <p>If you have any questions or need help, feel free to reach out to our support team.</p>
                    
                    <p>Happy job hunting!<br>The JobTracker Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to JobTracker!
        
        Hi {user_name}!
        
        Your email has been verified successfully! You're all set to start tracking your job applications.
        
        What you can do with JobTracker:
        - Track Job Applications
        - Analyze Resumes
        - Generate Cover Letters
        - View Analytics
        
        Visit: http://localhost:3000/dashboard
        
        Happy job hunting!
        The JobTracker Team
        """
        
        return await EmailService._send_email(email, subject, html_body, text_body)
    
    @staticmethod
    async def _send_email(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """
        Internal method to send email via SMTP or log to console
        
        Environment variables needed:
        - SMTP_HOST: SMTP server (e.g., smtp.gmail.com)
        - SMTP_PORT: SMTP port (e.g., 587)
        - SMTP_USER: SMTP username/email
        - SMTP_PASSWORD: SMTP password/app password
        - SMTP_FROM_EMAIL: From email address
        - SMTP_FROM_NAME: From name
        """
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("SMTP_FROM_EMAIL", smtp_user)
        from_name = os.getenv("SMTP_FROM_NAME", "JobTracker")
        
        # If SMTP not configured, log to console (development mode)
        if not all([smtp_host, smtp_user, smtp_password]):
            logger.warning("SMTP not configured. Logging email to console:")
            logger.info(f"To: {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body:\n{text_body}")
            print("\n" + "="*60)
            print(f"📧 EMAIL (Development Mode)")
            print("="*60)
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"\n{text_body}")
            print("="*60 + "\n")
            return True
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{from_name} <{from_email}>"
            message["To"] = to_email
            
            # Attach both text and HTML versions
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            # Fallback to console logging
            print(f"\n⚠️ Email sending failed. Logging to console:")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"\n{text_body}\n")
            return False
