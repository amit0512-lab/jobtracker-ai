from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum


class JobStatus(str, enum.Enum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"


class JobPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Job Details
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    job_url = Column(Text)
    description = Column(Text)          # JD yahan store hogi — NLP isme chalega

    # Tracking
    status = Column(Enum(JobStatus), default=JobStatus.SAVED, nullable=False)
    priority = Column(Enum(JobPriority), default=JobPriority.MEDIUM)
    notes = Column(Text)
    salary_min = Column(String(50))
    salary_max = Column(String(50))
    applied_at = Column(DateTime(timezone=True))
    interview_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="jobs")
    resumes = relationship("Resume", back_populates="job")

    def __repr__(self):
        return f"<Job {self.title} @ {self.company}>"