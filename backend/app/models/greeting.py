# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 打招呼语模板模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class GreetingTemplate(Base):
    """打招呼语模板模型"""
    __tablename__ = "greeting_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 模板名称，如"技术岗版"
    content = Column(Text, nullable=False)  # 模板内容，包含{变量}
    is_default = Column(Boolean, default=False)  # 是否为默认模板
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<GreetingTemplate(name={self.name}, is_default={self.is_default})>"
