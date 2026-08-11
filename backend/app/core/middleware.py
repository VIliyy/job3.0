# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 性能监控中间件
"""

import time
import logging
from fastapi import Request
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
        request_id = f"{int(time.time() * 1000)}"
        
        # 记录请求开始
        logger.info(f"[{request_id}] {request.method} {request.url.path} started")
        
        try:
            response = await call_next(request)
            
            # 记录请求完成
            logger.info(f"[{request_id}] Completed with {response.status_code}")
            
            # 添加request_id到响应头
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            logger.error(f"[{request_id}] Error: {str(e)}")
            raise
