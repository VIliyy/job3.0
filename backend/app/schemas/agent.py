# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - Agent Schema
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AgentRole(str, Enum):
    """Agent角色枚举"""
    PLANNER = "planner"
    RECRUITER = "recruiter"
    WRITER = "writer"
    CRITIC = "critic"
    INTERVIEWER = "interviewer"
    ADVISOR = "advisor"


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="历史消息")
    state: Optional[Dict[str, Any]] = Field(default=None, description="对话状态")


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="AI回复")
    suggested_actions: Optional[List[str]] = Field(default_factory=list, description="建议操作")
    state: Optional[Dict[str, Any]] = Field(default=None, description="对话状态")
    context: Optional[str] = Field(default=None, description="上下文")


class StreamRequest(BaseModel):
    """流式请求"""
    message: str = Field(..., min_length=1)
    history: Optional[List[ChatMessage]] = Field(default_factory=list)
    state: Optional[Dict[str, Any]] = None
    stream_thinking: bool = Field(default=False, description="是否流式输出思考过程")


class OptimizationRequest(BaseModel):
    """优化请求"""
    resume_text: str = Field(..., min_length=10, description="简历文本")
    jd_content: str = Field(..., min_length=10, description="JD内容")
    max_iterations: int = Field(default=5, ge=1, le=10, description="最大迭代次数")


class OptimizationResponse(BaseModel):
    """优化响应"""
    optimized_resume: str = Field(..., description="优化后的简历")
    score: int = Field(..., ge=0, le=100, description="匹配分数")
    iterations: int = Field(..., description="迭代次数")
    verdict: str = Field(..., description="评判结果")
    status: str = Field(..., description="状态")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Agent消息")


class MatchAnalysisRequest(BaseModel):
    """匹配分析请求"""
    resume_text: str = Field(..., min_length=10)
    jd_content: str = Field(..., min_length=10)
    use_ai: bool = Field(default=True, description="是否使用AI分析")


class MatchAnalysisResponse(BaseModel):
    """匹配分析响应"""
    score: int = Field(..., ge=0, le=100)
    match_points: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class AIStatusResponse(BaseModel):
    """AI状态响应"""
    enabled: bool
    provider: Optional[str] = None
    model: Optional[str] = None


class SetAPIKeyRequest(BaseModel):
    """设置API Key请求"""
    provider: str = Field(..., pattern="^(deepseek|openai)$")
    api_key: str = Field(..., min_length=10)
    model: Optional[str] = Field(None, description="模型名称")
