# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 打招呼语模板Schema
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GreetingTemplateCreate(BaseModel):
    """创建打招呼语模板Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    content: str = Field(..., min_length=1, description="模板内容")
    is_default: bool = Field(False, description="是否为默认模板")

class GreetingTemplateUpdate(BaseModel):
    """更新打招呼语模板Schema"""
    name: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None
    is_default: Optional[bool] = None

class GreetingTemplateResponse(BaseModel):
    """打招呼语模板响应Schema"""
    id: int
    name: str
    content: str
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class GreetingGenerateRequest(BaseModel):
    """生成打招呼语请求Schema"""
    template_id: Optional[int] = Field(None, description="模板ID，不传则使用默认模板")
    jd_content: str = Field(..., description="JD内容")
    resume_content: Optional[str] = Field(None, description="简历内容（用于提取变量）")

class GreetingGenerateResponse(BaseModel):
    """生成打招呼语响应Schema"""
    greeting: str
    template_name: str
    variables_used: dict
