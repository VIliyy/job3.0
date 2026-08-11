# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 安全API路由示例
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.security import (
    limiter,
    validate_file_type,
    validate_file_size,
    sanitize_filename,
    validate_slot,
    validate_content_length
)
from app.schemas.resume import ResumeUploadResponse


router = APIRouter(prefix="/api/secure", tags=["安全示例"])


def get_limiter() -> Limiter:
    return limiter


@router.post("/upload-resume")
@limiter.limit("10/minute")  # 每分钟10次
async def secure_upload_resume(
    request: Request,
    file: UploadFile = File(...),
    slot: int = Form(..., ge=1, le=4),
    version_name: str = Form(None, max_length=100),
    limiter: Limiter = Depends(get_limiter)
):
    """
    安全的上传简历接口
    
    安全措施:
    - 请求限流: 10次/分钟
    - 文件类型验证
    - 文件大小验证
    - 文件名清理
    - 槽位验证
    """
    # 验证文件类型
    if not validate_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型，仅支持 PDF、DOC、DOCX"
        )
    
    # 验证文件大小
    content = await file.read()
    if not validate_file_size(len(content)):
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制，最大 {10}MB"
        )
    
    # 验证槽位
    if not validate_slot(slot):
        raise HTTPException(
            status_code=400,
            detail="槽位编号必须为1-4"
        )
    
    # 清理文件名
    safe_filename = sanitize_filename(file.filename)
    
    # 保存文件（实际实现需要调用service）
    return {
        "slot": slot,
        "filename": safe_filename,
        "version_name": version_name,
        "file_size": len(content)
    }


@router.post("/analyze-jd")
@limiter.limit("20/minute")
async def secure_analyze_jd(
    request: Request,
    content: str = Form(...),
    limiter: Limiter = Depends(get_limiter)
):
    """
    安全的JD分析接口
    
    安全措施:
    - 请求限流: 20次/分钟
    - 内容长度验证
    """
    # 验证内容长度
    if not validate_content_length(content, max_length=50000):
        raise HTTPException(
            status_code=400,
            detail="内容过长，最大50000字符"
        )
    
    # 分析处理（实际实现需要调用AI服务）
    return {
        "status": "success",
        "content_length": len(content)
    }
