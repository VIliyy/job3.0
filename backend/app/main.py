# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - FastAPI入口文件
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from sqlalchemy import text

from app.core.database import init_db, SessionLocal
from app.api import api_router
from app.core.middleware import (
    PerformanceMiddleware,
    RequestLoggingMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("starting %s %s", settings.APP_NAME, settings.APP_VERSION)
    init_db()
    if settings.ENABLE_TASK_RECOVERY:
        try:
            from app.services.decompose_service import recover_incomplete_tasks
            recover_incomplete_tasks()
        except Exception:
            logger.exception("failed to recover decomposition tasks")
        try:
            from app.api.video_notes import recover_incomplete_video_tasks
            recover_incomplete_video_tasks()
        except Exception:
            logger.exception("failed to recover video tasks")
    yield

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智能简历评价与职业规划 Agent 系统",
    docs_url="/docs" if settings.ENVIRONMENT.lower() not in {"prod", "production"} else None,
    redoc_url="/redoc" if settings.ENVIRONMENT.lower() not in {"prod", "production"} else None,
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_json_bytes=settings.MAX_JSON_BODY_SIZE)
app.add_middleware(PerformanceMiddleware)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
if settings.PUBLIC_UPLOADS and os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册API路由
app.include_router(api_router, prefix="/api")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return a safe error envelope while preserving the correlation ID."""
    request_id = getattr(request.state, "request_id", None)
    logger.error(
        "unhandled request error",
        exc_info=(type(exc), exc, exc.__traceback__),
        extra={"request_id": request_id},
    )
    payload = {"detail": "internal server error"}
    if request_id:
        payload["request_id"] = request_id
    response = JSONResponse(status_code=500, content=payload)
    if request_id:
        response.headers["X-Request-ID"] = request_id
    return response

# 健康检查
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.ENVIRONMENT.lower() not in {"prod", "production"} else None,
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check():
    """Return 200 only when the database is reachable."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("readiness check failed: %s", exc)
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ready", "database": "ok"}

# 运行服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
