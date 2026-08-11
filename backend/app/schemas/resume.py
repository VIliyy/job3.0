# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 简历 Schema（v2.0）

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ResumeCategory(str):
    TECH = "tech"
    PRODUCT = "product"
    OPERATIONS = "ops"
    MARKETING = "marketing"
    OTHER = "other"


class ResumeStatus(str):
    DRAFT = "draft"
    PROCESSING = "processing"
    OPTIMIZED = "optimized"
    APPLIED = "applied"
    ARCHIVED = "archived"


class ResumeBase(BaseModel):
    filename: str
    content: Optional[str] = None
    category: Optional[str] = "other"
    version_name: Optional[str] = None


class ResumeCreate(ResumeBase):
    slot: int = Field(..., ge=1, le=4)
    filepath: str
    file_size: Optional[int] = 0
    file_type: Optional[str] = None


class ResumeUpdate(BaseModel):
    category: Optional[str] = None
    status: Optional[str] = None
    version_name: Optional[str] = None
    current_jd_id: Optional[int] = None
    latest_optimized_version_id: Optional[int] = None
    content: Optional[str] = None


class ResumeResponse(ResumeBase):
    id: int
    slot: int
    is_active: bool
    filepath: str
    file_size: int
    file_type: Optional[str] = None
    status: str
    current_jd_id: Optional[int] = None
    latest_optimized_version_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResumeBrief(BaseModel):
    id: int
    slot: int
    filename: str
    category: str
    status: str
    version_name: Optional[str] = None
    content: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = 0
    is_active: bool = False
    current_jd_id: Optional[int] = None
    latest_optimized_version_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResumeVersionResponse(BaseModel):
    id: int
    resume_id: int
    version_number: int
    version_name: Optional[str] = None
    original_content: Optional[str] = None
    content: Optional[str] = None
    jd_id: Optional[int] = None
    optimization_score: Optional[int] = None
    original_score: Optional[int] = None
    change_summary: Optional[str] = None
    diff_highlights: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResumeWithVersions(ResumeResponse):
    versions: List[ResumeVersionResponse] = []
    application_count: int = 0

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    slots: List[Optional[ResumeResponse]]
    total: int
    active_count: int
