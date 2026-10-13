# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 投递记录 Schema（v2.0）

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    VIEWED = "viewed"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicationBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    salary: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    job_url: Optional[str] = Field(None, max_length=512)
    source: Optional[str] = Field(None, max_length=100)


class ApplicationCreate(ApplicationBase):
    resume_id: int
    status: ApplicationStatus = ApplicationStatus.PENDING


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    progress: Optional[str] = Field(None, max_length=255)
    progress_notes: Optional[str] = Field(None, max_length=10_000)
    notes: Optional[str] = Field(None, max_length=10_000)


class ApplicationResponse(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    resume_id: int
    status: str
    progress: Optional[str] = None
    progress_notes: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ApplicationWithResume(ApplicationResponse):
    model_config = ConfigDict(from_attributes=True)
    resume_category: Optional[str] = None
    resume_version_name: Optional[str] = None

class ApplicationBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company: str
    position: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
