# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 投递记录模型（v2.0 重构版）

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    VIEWED = "viewed"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"
    
    __table_args__ = (
        Index("idx_app_resume_id", "resume_id"),
        Index("idx_app_status", "status"),
        Index("idx_app_company", "company"),
        Index("idx_app_created", "created_at"),
        {"sqlite_autoincrement": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    company = Column(String(255), nullable=False)
    company_normalized = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    salary = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    job_url = Column(String(512), nullable=True)
    source = Column(String(100), nullable=True)
    progress = Column(String(255), nullable=True)
    progress_notes = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    resume = relationship("Resume", back_populates="applications")

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "company": self.company,
            "position": self.position,
            "status": self.status.value if self.status else None,
            "salary": self.salary,
            "location": self.location,
            "job_url": self.job_url,
            "source": self.source,
            "progress": self.progress,
            "progress_notes": self.progress_notes,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
