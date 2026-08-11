# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 投递记录 Schema（v2.0）

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ApplicationStatus(str):
    PENDING = "pending"
    SUBMITTED = "submitted"
    VIEWED = "viewed"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicationBase(BaseModel):
    company: str
    position: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None
    source: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    resume_id: int
    status: str = "pending"


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[str] = None
    progress_notes: Optional[str] = None
    notes: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: int
    resume_id: int
    status: str
    progress: Optional[str] = None
    progress_notes: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplicationWithResume(ApplicationResponse):
    resume_category: Optional[str] = None
    resume_version_name: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicationBrief(BaseModel):
    id: int
    company: str
    position: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
