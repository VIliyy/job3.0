# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 打招呼语API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.greeting import (
    GreetingTemplateCreate, GreetingTemplateUpdate, GreetingTemplateResponse,
    GreetingGenerateRequest, GreetingGenerateResponse
)
from app.services.greeting_service import GreetingService

router = APIRouter()

@router.get("/templates", response_model=List[GreetingTemplateResponse])
async def list_templates(db: Session = Depends(get_db)):
    """获取打招呼语模板列表"""
    service = GreetingService(db)
    return await service.list_templates()

@router.post("/templates", response_model=GreetingTemplateResponse)
async def create_template(
    template_data: GreetingTemplateCreate,
    db: Session = Depends(get_db)
):
    """创建打招呼语模板"""
    service = GreetingService(db)
    return await service.create_template(template_data)

@router.put("/templates/{template_id}", response_model=GreetingTemplateResponse)
async def update_template(
    template_id: int,
    update_data: GreetingTemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新打招呼语模板"""
    service = GreetingService(db)
    template = await service.update_template(template_id, update_data)
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return template

@router.delete("/templates/{template_id}")
async def delete_template(template_id: int, db: Session = Depends(get_db)):
    """删除打招呼语模板"""
    service = GreetingService(db)
    success = await service.delete_template(template_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return {"message": "删除成功"}

@router.post("/generate", response_model=GreetingGenerateResponse)
async def generate_greeting(
    request: GreetingGenerateRequest,
    db: Session = Depends(get_db)
):
    """根据JD生成打招呼语"""
    service = GreetingService(db)
    return await service.generate_greeting(request)
