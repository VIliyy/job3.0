# -*- coding: utf-8 -*-
"""
Job3.0 多Agent协作系统 - API端点
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio

from app.agents.langgraph_agent import run_optimization, AgentState

router = APIRouter()

# =============================================================================
# 请求/响应模型
# =============================================================================

class OptimizationRequest(BaseModel):
    resume_text: str
    jd_text: str
    slot: int = 1
    stream: bool = True

class AgentStatusResponse(BaseModel):
    agents: Dict[str, str]
    status: str
    queue_length: int

class OptimizationHistoryResponse(BaseModel):
    history: List[Dict[str, Any]]
    total: int

# =============================================================================
# SSE回调类
# =============================================================================

class SSEProgressCallback:
    """SSE进度回调"""
    
    def __init__(self):
        self.events = []
    
    async def on_agent_event(self, event: Dict[str, Any]):
        self.events.append(event)

# =============================================================================
# API端点
# =============================================================================

@router.post("/optimize")
async def optimize_resume(request: OptimizationRequest):
    """
    多Agent协作简历优化
    """
    try:
        # 创建SSE回调
        callback = SSEProgressCallback()
        
        # 运行优化流程
        result = await run_optimization(
            resume_text=request.resume_text,
            jd_text=request.jd_text,
            slot=request.slot,
            enable_stream=request.stream,
            callbacks=[callback]
        )
        
        # 返回结果
        return {
            "status": result.get("status", "unknown"),
            "optimized_resume": result.get("optimized_resume", request.resume_text),
            "score": result.get("match_score", 0),
            "iterations": result.get("iteration", 0),
            "verdict": result.get("verdict"),
            "all_outputs": {
                "planner": result.get("planner_output"),
                "recruiter": result.get("recruiter_output"),
                "critic": result.get("critic_output"),
                "interviewer": result.get("interviewer_output"),
                "advisor": result.get("advisor_output")
            },
            "errors": result.get("errors", []),
            "messages": result.get("messages", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-stream")
async def optimize_resume_stream(request: OptimizationRequest):
    """
    多Agent协作简历优化 - 流式版本
    """
    from sse_starlette.sse import EventSourceResponse
    
    async def event_generator():
        callback = SSEProgressCallback()
        
        try:
            # 异步启动优化
            task = asyncio.create_task(
                run_optimization(
                    resume_text=request.resume_text,
                    jd_text=request.jd_text,
                    slot=request.slot,
                    enable_stream=True,
                    callbacks=[callback]
                )
            )
            
            # 实时发送事件
            while not task.done():
                if callback.events:
                    event = callback.events.pop(0)
                    yield {
                        "event": event.get("type", "message"),
                        "data": str(event)
                    }
                await asyncio.sleep(0.1)
            
            # 发送最终结果
            result = await task
            yield {
                "event": "final",
                "data": str({
                    "status": result.get("status"),
                    "optimized_resume": result.get("optimized_resume"),
                    "score": result.get("match_score"),
                    "iterations": result.get("iteration")
                })
            }
            
        except Exception as e:
            yield {
                "event": "error",
                "data": str(e)
            }
    
    return EventSourceResponse(event_generator())

@router.get("/status")
async def get_agent_status():
    """
    获取Agent状态
    """
    return AgentStatusResponse(
        agents={
            "planner": "ready",
            "recruiter": "ready",
            "writer": "ready",
            "critic": "ready",
            "interviewer": "ready",
            "advisor": "ready"
        },
        status="ready",
        queue_length=0
    )

@router.get("/history")
async def get_optimization_history(limit: int = 10):
    """
    获取优化历史
    """
    # TODO: 从数据库查询历史记录
    return OptimizationHistoryResponse(
        history=[],
        total=0
    )
