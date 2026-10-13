# -*- coding: utf-8 -*-
"""Immutable job posting snapshot captured by the browser bridge."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class JobSnapshot(Base):
    __tablename__ = "job_snapshots"

    __table_args__ = (
        Index("idx_job_snap_url", "job_url"),
        Index("idx_job_snap_company", "company"),
        Index("idx_job_snap_created", "created_at"),
        {"sqlite_autoincrement": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=True)
    company = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    salary = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    job_url = Column(String(512), nullable=True)
    source = Column(String(100), nullable=True)
    jd_text = Column(Text, nullable=True)
    greeting = Column(Text, nullable=True)
    extra = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "application_id": self.application_id,
            "company": self.company,
            "position": self.position,
            "salary": self.salary,
            "location": self.location,
            "job_url": self.job_url,
            "source": self.source,
            "jd_text": self.jd_text,
            "greeting": self.greeting,
            "extra": self.extra,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
