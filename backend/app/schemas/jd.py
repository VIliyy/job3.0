# -*- coding: utf-8 -*-
# Job3.0 求职系统 - JD分析 Schema（v2.0）

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class JDAnalysisBase(BaseModel):
    company: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=2048)
    raw_content: str = Field(..., min_length=1, max_length=100_000)


class JDAnalysisCreate(JDAnalysisBase):
    pass


class JDAnalysisUpdate(BaseModel):
    company: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=2048)
    analysis_result: Optional[Dict[str, Any]] = None
    requirements: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    fit_score: Optional[int] = None


class JDAnalysisResponse(JDAnalysisBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content_hash: Optional[str] = None
    analysis_result: Optional[Dict[str, Any]] = None
    requirements: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    fit_score: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class JDAnalysisBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company: Optional[str] = None
    position: Optional[str] = None
    fit_score: Optional[int] = None
    created_at: Optional[datetime] = None
