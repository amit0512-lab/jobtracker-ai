from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Engine - PostgreSQL se connection
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # connection alive hai ya nahi check karta hai
    pool_size=10,            # max 10 connections pool mein
    max_overflow=20,         # pool full hone pe 20 extra allowed
    echo=settings.DEBUG,     # DEBUG mode mein SQL queries print hongi
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class - saare models isse inherit karenge
class Base(DeclarativeBase):
    pass


# Dependency - FastAPI routes mein inject hoga
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()