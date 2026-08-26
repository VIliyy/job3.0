# -*- coding: utf-8 -*-
"""视频笔记任务模型（小林工具箱）"""
import json
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class VideoTask(Base):
    __tablename__ = "video_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(64), unique=True, index=True, nullable=False)
    platform = Column(String(32), default="auto")
    video_url = Column(String(1024), nullable=False)
    title = Column(String(512), nullable=True)
    style = Column(String(32), default="minimal")
    formats_json = Column(Text, default="[]")
    extras = Column(Text, nullable=True)
    export_obsidian = Column(Boolean, default=False)
    status = Column(String(32), default="PENDING", index=True)
    status_message = Column(String(512), default="")
    markdown = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    obsidian_exported = Column(Boolean, default=False)
    obsidian_path = Column(String(1024), nullable=True)
    obsidian_message = Column(String(512), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def set_formats(self, formats: list):
        self.formats_json = json.dumps(formats or [], ensure_ascii=False)

    def get_formats(self) -> list:
        try:
            return json.loads(self.formats_json or "[]")
        except Exception:
            return []
