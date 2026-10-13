# -*- coding: utf-8 -*-
# Job3.0 API 路由 v2.0

from fastapi import APIRouter
from app.api import (
    resume, 
    application, 
    greeting, 
    jd, 
    agent, 
    ai, 
    stream, 
    match, 
    orchestration,
    optimize,
    export
)

api_router = APIRouter()

# v2.0 API 路由
api_router.include_router(resume.router, tags=["简历 v2.0"])
api_router.include_router(application.router, tags=["投递记录"])
api_router.include_router(jd.router, tags=["JD 解析 v2.0"])
api_router.include_router(optimize.router, tags=["简历优化 v2.0"])
api_router.include_router(export.router, tags=["导出"])

# 旧版与扩展 API 路由
api_router.include_router(greeting.router, prefix="/greeting", tags=["打招呼"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent 问答"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI 设置"])
api_router.include_router(stream.router, prefix="/stream", tags=["流式输出"])
api_router.include_router(match.router, prefix="/match", tags=["JD 匹配"])
api_router.include_router(orchestration.router, prefix="/orchestration", tags=["多 Agent 编排"])


# 视频笔记模块（小林工具箱）
from app.api.video_notes import router as video_notes_router
api_router.include_router(video_notes_router)

# 信息拆解模块
from app.api.decompose import router as decompose_router
api_router.include_router(decompose_router, prefix="/decompose", tags=["信息拆解"])

# 求职助手聊天历史模块
from app.api.agent_history import router as agent_history_router
api_router.include_router(agent_history_router)

# 浏览器扩展桥接（海投助手本地桥）
from app.api.bridge import router as bridge_router
api_router.include_router(bridge_router, prefix="/bridge", tags=["海投桥接"])
# 控制台统计聚合
from app.api.dashboard import router as dashboard_router
api_router.include_router(dashboard_router)
