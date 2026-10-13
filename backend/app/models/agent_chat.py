# -*- coding: utf-8 -*-
"""求职助手聊天历史模型（小林工具箱）"""
import json
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class AgentChat(Base):
    __tablename__ = "agent_chats"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(128), nullable=True)
    messages_json = Column(Text, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def get_messages(self) -> list:
        try:
            return json.loads(self.messages_json or "[]")
        except Exception:
            return []