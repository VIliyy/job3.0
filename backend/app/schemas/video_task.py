# -*- coding: utf-8 -*-
"""视频笔记接口模型（小林工具箱）"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class VideoNoteCreate(BaseModel):
    video_url: str = Field(..., description="视频链接或本地文件路径")
    platform: str = Field("auto", description="auto/bilibili/douyin/local")
    style: str = "minimal"
    formats: List[str] = []
    extras: Optional[str] = None
    export_obsidian: bool = False


class VideoTaskBrief(BaseModel):
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

    class Config:
        from_attributes = True


class VideoTaskDetail(VideoTaskBrief):
    style: str = "minimal"
    formats: List[str] = []
    extras: Optional[str] = None
    export_obsidian: bool = False
    markdown: Optional[str] = None
    transcript: Optional[str] = None
    error: Optional[str] = None
    obsidian_message: Optional[str] = None


class VideoConfigIn(BaseModel):
    obsidian_vault_path: str = ""


class VideoConfigOut(BaseModel):
    obsidian_vault_path: str = ""
    obsidian_valid: bool = False
    obsidian_message: str = ""
    llm_configured: bool = False
    llm_provider: str = ""
    whisper_model: str = ""
