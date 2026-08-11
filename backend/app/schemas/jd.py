# -*- coding: utf-8 -*-
# Job3.0 求职系统 - JD分析 Schema（v2.0）

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class JDAnalysisBase(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    source_url: Optional[str] = None
    raw_content: str


class JDAnalysisCreate(JDAnalysisBase):
    pass


class JDAnalysisUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    source_url: Optional[str] = None
    analysis_result: Optional[Dict[str, Any]] = None
    requirements: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    fit_score: Optional[int] = None


class JDAnalysisResponse(JDAnalysisBase):
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

    class Config:
        from_attributes = True


class JDAnalysisBrief(BaseModel):
    id: int
    company: Optional[str] = None
    position: Optional[str] = None
    fit_score: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
