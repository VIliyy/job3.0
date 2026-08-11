# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 安全模块
"""

import re
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


# 创建限流器
limiter = Limiter(key_func=get_remote_address)


# 允许的文件类型
ALLOWED_FILE_TYPES = {
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

ALLOWED_EXTENSIONS = set(ALLOWED_FILE_TYPES.keys())

# 最大文件大小 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_file_type(filename: str) -> bool:
    """验证文件类型"""
    if not filename:
        return False
    
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS


def validate_file_size(size: int) -> bool:
    """验证文件大小"""
    return 0 < size <= MAX_FILE_SIZE


def sanitize_filename(filename: str) -> str:
    """清理文件名"""
    # 移除危险字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 限制长度
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:255-len(ext)-1] + "." + ext
    return filename


def validate_slot(slot: int) -> bool:
    """验证槽位编号"""
    return 1 <= slot <= 4


def validate_content_length(content: str, max_length: int = 50000) -> bool:
    """验证内容长度"""
    return len(content) <= max_length


class SecurityHeaders:
    """安全响应头"""
    
    @staticmethod
    def add_headers(response):
        """添加安全响应头"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src '\''self'\''"
        return response


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """限流超限处理器"""
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "请求过于频繁，请稍后再试",
                "suggestion": "建议减少API调用频率"
            }
        }
    )


def validate_api_key(api_key: str) -> bool:
    """验证API Key格式"""
    if not api_key:
        return False
    
    # DeepSeek API Key格式: sk-xxx
    if api_key.startswith("sk-"):
        return len(api_key) >= 30
    
    # OpenAI API Key格式: sk-xxx
    if api_key.startswith("sk-"):
        return len(api_key) >= 40
    
    return False


def mask_api_key(api_key: str) -> str:
    """脱敏API Key"""
    if not api_key or len(api_key) < 10:
        return "***"
    
    return api_key[:5] + "***" + api_key[-4:]
