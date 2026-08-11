# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 简历模型（v2.0 重构版）

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ResumeCategory(str, enum.Enum):
    TECH = "tech"
    PRODUCT = "product"
    OPERATIONS = "ops"
    MARKETING = "marketing"
    OTHER = "other"


class ResumeStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    OPTIMIZED = "optimized"
    APPLIED = "applied"
    ARCHIVED = "archived"


class Resume(Base):
    __tablename__ = "resumes"
    
    __table_args__ = (
        Index("idx_resume_slot_active", "slot", "is_active"),
        Index("idx_resume_updated", "updated_at"),
        Index("idx_resume_category", "category"),
        Index("idx_resume_status", "status"),
        {"sqlite_autoincrement": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    slot = Column(Integer, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    content = Column(Text, nullable=True)
    file_size = Column(Integer, default=0)
    file_type = Column(String(20), nullable=True)
    category = Column(SQLEnum(ResumeCategory), default=ResumeCategory.OTHER)
    status = Column(SQLEnum(ResumeStatus), default=ResumeStatus.DRAFT)
    version_name = Column(String(100), nullable=True)
    current_jd_id = Column(Integer, ForeignKey("jd_analyses.id", ondelete="SET NULL"), nullable=True)
    latest_optimized_version_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="resume", cascade="all, delete-orphan")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    
    __table_args__ = (
        Index("idx_version_resume_id", "resume_id", "version_number"),
        Index("idx_version_created", "created_at"),
        {"sqlite_autoincrement": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, default=1)
    version_name = Column(String(100), nullable=True)
    original_content = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)
    jd_id = Column(Integer, ForeignKey("jd_analyses.id", ondelete="SET NULL"), nullable=True)
    optimization_score = Column(Integer, nullable=True)
    original_score = Column(Integer, nullable=True)
    change_summary = Column(Text, nullable=True)
    diff_highlights = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="versions")
