# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 简历 Schema（v2.0）

from pydantic import BaseModel, ConfigDict, Field
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
    filename: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = Field(None, max_length=100_000)
    category: Optional[str] = Field("other", max_length=32)
    version_name: Optional[str] = Field(None, max_length=255)


class ResumeCreate(ResumeBase):
    slot: int = Field(..., ge=1, le=4)
    filepath: str = Field(..., max_length=1024)
    file_size: Optional[int] = Field(0, ge=0)
    file_type: Optional[str] = Field(None, max_length=32)


class ResumeUpdate(BaseModel):
    category: Optional[str] = Field(None, max_length=32)
    status: Optional[str] = Field(None, max_length=32)
    version_name: Optional[str] = Field(None, max_length=255)
    current_jd_id: Optional[int] = None
    latest_optimized_version_id: Optional[int] = None
    content: Optional[str] = Field(None, max_length=100_000)


class ResumeResponse(ResumeBase):
    model_config = ConfigDict(from_attributes=True)
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

class ResumeBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
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

class ResumeVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
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

class ResumeWithVersions(ResumeResponse):
    model_config = ConfigDict(from_attributes=True)
    versions: List[ResumeVersionResponse] = Field(default_factory=list)
    application_count: int = 0


class ResumeListResponse(BaseModel):
    slots: List[Optional[ResumeResponse]]
    total: int
    active_count: int
