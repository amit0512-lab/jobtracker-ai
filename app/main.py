from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.logger_middleware import LoggerMiddleware
from app.api.routes import auth, jobs, resume, analytics

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # production mein docs band
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production mein specific origins dena
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger Middleware
app.add_middleware(LoggerMiddleware)

# ─── Routers ───────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


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
            "resume": "/api/v1/resume"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
