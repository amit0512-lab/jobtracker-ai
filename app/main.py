from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.logger_middleware import LoggerMiddleware
from app.api.routes import auth, jobs, resume, analytics, cover_letter, verification
from app.core.logging_config import app_logger
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # production mein docs band
)

logger.info(f"Starting {settings.APP_NAME} v1.0.0")
logger.info(f"Environment: {settings.APP_ENV}")
logger.info(f"Debug mode: {settings.DEBUG}")

# CORS - IMPORTANT: Update for production!
# For development: allows localhost
# For production: MUST change to your actual domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # Backend
        # TODO: Add your production frontend URL here
        # "https://yourdomain.com",
        # "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Logger Middleware
app.add_middleware(LoggerMiddleware)

# ─── Routers ───────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(verification.router, prefix="/api/v1/verification", tags=["Verification"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(cover_letter.router, prefix="/api/v1/cover-letter", tags=["Cover Letters"])


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/api/v1/auth",
            "jobs": "/api/v1/jobs",
            "resume": "/api/v1/resume",
            "cover_letter": "/api/v1/cover-letter"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/test-cover-letter")
async def test_cover_letter():
    """Test endpoint to verify cover letter imports work"""
    try:
        from app.models.cover_letter import CoverLetter
        from app.api.controllers.cover_letter_controller import CoverLetterController
        return {"status": "ok", "message": "Cover letter imports successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
