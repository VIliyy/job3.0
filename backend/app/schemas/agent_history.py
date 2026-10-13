# -*- coding: utf-8 -*-
"""求职助手聊天历史接口模型（小林工具箱）"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    role: str
    content: str = ""
    time: Optional[str] = ""
    actions: List[str] = Field(default_factory=list)


class AgentChatIn(BaseModel):
    chat_id: Optional[str] = None
    title: Optional[str] = None
    messages: List[AgentMessage] = Field(default_factory=list)


class AgentChatBrief(BaseModel):
    chat_id: str
    title: Optional[str] = ""
    message_count: int = 0
    updated_at: Optional[datetime] = None


class AgentChatDetail(AgentChatBrief):
    messages: List[AgentMessage] = Field(default_factory=list)