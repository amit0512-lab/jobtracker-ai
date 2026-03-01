from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)  # optional — kisi specific job ke liye

    # File Info
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)      # local ya S3 path
    file_size = Column(String(50))

    # NLP Results — JSON mein store honge
    extracted_skills = Column(JSON, default=list)       # ["Python", "FastAPI", ...]
    extracted_experience = Column(JSON, default=list)   # parsed experience blocks
    extracted_education = Column(JSON, default=list)    # parsed education blocks
    keywords = Column(JSON, default=list)               # top keywords
    match_score = Column(Float, default=0.0)            # JD se match %
    nlp_summary = Column(Text)                          # overall summary

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    job = relationship("Job", back_populates="resumes")

    def __repr__(self):
        return f"<Resume {self.filename} score={self.match_score}>"