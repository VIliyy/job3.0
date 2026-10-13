# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 性能监控中间件
"""

import time
import logging
import json
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        response = await call_next(request)
        
        # 计算耗时
        process_time = (time.time() - start_time) * 1000  # 毫秒
        status_code = response.status_code
        
        # 日志记录
        log_data = {
            "method": method,
            "path": path,
            "status": status_code,
            "time_ms": round(process_time, 2),
            "client": client_host
        }
        
        if process_time > 1000:  # 超过1秒
            logger.warning(f"Slow request: {log_data}")
        else:
            logger.info(f"{method} {path} - {status_code} - {process_time:.2f}ms")
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        incoming_id = request.headers.get("X-Request-ID", "").strip()
        request_id = incoming_id[:128] if incoming_id else str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始
        logger.info(json.dumps({
            "event": "request_started",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        }, ensure_ascii=False))
        
        try:
            response = await call_next(request)
            
            # 记录请求完成
            logger.info(json.dumps({
                "event": "request_completed",
                "request_id": request_id,
                "status": response.status_code,
            }, ensure_ascii=False))
            
            # 添加request_id到响应头
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            logger.exception("request_failed", extra={"request_id": request_id})
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add conservative browser security headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject oversized JSON requests before FastAPI parses their body."""

    def __init__(self, app, max_json_bytes: int):
        super().__init__(app)
        self.max_json_bytes = max_json_bytes

    async def dispatch(self, request: Request, call_next):
        content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        content_length = request.headers.get("content-length")
        if content_type.endswith("/json") or content_type.endswith("+json"):
            try:
                declared_length = int(content_length or 0)
            except ValueError:
                declared_length = 0
            if declared_length > self.max_json_bytes:
                return JSONResponse(status_code=413, content={"detail": "request body is too large"})
        return await call_next(request)
