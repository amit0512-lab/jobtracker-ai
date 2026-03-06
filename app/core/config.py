from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "JobTracker"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Storage
    USE_LOCAL_STORAGE: bool = True
    LOCAL_STORAGE_PATH: str = "local_storage"
    AWS_ACCESS_KEY_ID: str = "mock"
    AWS_SECRET_ACCESS_KEY: str = "mock"
    AWS_BUCKET_NAME: str = "jobtracker-bucket"
    AWS_REGION: str = "ap-south-1"

    # AI
    OPENAI_API_KEY: str = "your-openai-api-key-here"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()  # ek baar load hoga, bar bar .env nahi padha jayega
def get_settings() -> Settings:
    return Settings()


settings = get_settings()