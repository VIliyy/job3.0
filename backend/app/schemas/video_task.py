# -*- coding: utf-8 -*-
"""Video notes API schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class VideoNoteCreate(BaseModel):
    video_url: str = Field(..., min_length=1, max_length=1024)
    platform: str = Field("auto", pattern="^(auto|bilibili|douyin|local)$")
    style: str = Field("minimal", max_length=32)
    formats: List[str] = Field(default_factory=list, max_length=20)
    extras: Optional[str] = Field(None, max_length=10_000)
    export_obsidian: bool = False


class VideoTaskBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: str
    platform: str
    video_url: str
    title: Optional[str] = None
    status: str
    status_message: str = ""
    obsidian_exported: bool = False
    obsidian_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class VideoTaskDetail(VideoTaskBrief):
    style: str = "minimal"
    formats: List[str] = Field(default_factory=list)
    extras: Optional[str] = None
    export_obsidian: bool = False
    markdown: Optional[str] = None
    transcript: Optional[str] = None
    error: Optional[str] = None
    obsidian_message: Optional[str] = None


class VideoConfigIn(BaseModel):
    obsidian_vault_path: str = Field("", max_length=1024)


class VideoConfigOut(BaseModel):
    obsidian_vault_path: str = ""
    obsidian_valid: bool = False
    obsidian_message: str = ""
    llm_configured: bool = False
    llm_provider: str = ""
    whisper_model: str = ""
