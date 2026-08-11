# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - Agent对话API

支持：
1. 多轮对话记忆（状态传递）
2. 上下文理解
3. 主动引导
4. 投递工作流
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.agent_service import AgentService

router = APIRouter()


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="对话历史")
    state: Optional[Dict[str, Any]] = Field(default=None, description="对话状态")


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="AI回复")
    suggested_actions: List[str] = Field(default_factory=list, description="建议操作")
    state: Optional[Dict[str, Any]] = Field(default=None, description="更新后的状态")
    context: Optional[str] = Field(default=None, description="上下文信息")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Agent对话

    支持：
    - 简历搜索：说"我的简历"自动搜索
    - JD分析：粘贴JD自动识别分析
    - 打招呼语生成：告诉公司名自动生成
    - 投递记录：查看、记录、追踪
    """
    state = request.state or {}
    if not state.get("resume_text"):
        from app.models.resume import Resume
        resume = db.query(Resume).filter(Resume.content.isnot(None), Resume.content != "").order_by(Resume.updated_at.desc()).first()
        if resume and resume.content:
            state = {**state, "resume_text": resume.content, "has_resume": True}

    service = AgentService(db)
    result = await service.chat(
        message=request.message,
        history=request.history,
        state=state
    )

    return ChatResponse(
        response=result.get("response", ""),
        suggested_actions=result.get("suggested_actions", []),
        state=result.get("state"),
        context=result.get("context")
    )


@router.get("/actions")
async def get_suggested_actions():
    """获取建议的操作"""
    return {
        "actions": [
            {"label": "📄 查看简历", "action": "search_resume"},
            {"label": "🔍 分析JD", "action": "analyze_jd"},
            {"label": "💬 生成打招呼语", "action": "greeting"},
            {"label": "📮 投递记录", "action": "view_applications"},
            {"label": "🎯 分析匹配度", "action": "match"},
            {"label": "📝 优化简历", "action": "optimize"},
        ]
    }


@router.get("/workflow")
async def get_workflow():
    """获取投递工作流状态"""
    return {
        "steps": [
            {"id": "resume", "name": "简历准备", "status": "ready"},
            {"id": "jd", "name": "JD分析", "status": "pending"},
            {"id": "greeting", "name": "打招呼语", "status": "pending"},
            {"id": "apply", "name": "确认投递", "status": "pending"},
            {"id": "track", "name": "投递追踪", "status": "pending"},
        ],
        "current": 0,
        "tips": [
            "上传简历后，我可以分析你与职位的匹配度",
            "粘贴JD，我帮你提取关键要求",
            "生成针对性的打招呼语，提高回复率",
            "记录投递后，我会帮你追踪面试进度"
        ]
    }
