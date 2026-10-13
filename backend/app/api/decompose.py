# -*- coding: utf-8 -*-
"""
信息拆解 API（契约：docs/拆解契约.md 第 6 章）

POST   /api/decompose/tasks                    新建任务
GET    /api/decompose/tasks                    任务列表
GET    /api/decompose/tasks/{id}               任务详情
GET    /api/decompose/tasks/{id}/events        SSE 进度订阅
GET    /api/decompose/tasks/{id}/gates         待确认闸门列表
POST   /api/decompose/gates/{gate_id}/decide   闸门确认 / 重生成
POST   /api/decompose/tasks/{id}/rerun         从指定段重跑（version+1）
POST   /api/decompose/tasks/{id}/export        导出 Markdown 报告
"""

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.decompose_task import DecomposeTask
from app.services import decompose_service as service

router = APIRouter()


# =============================================================================
# 请求模型
# =============================================================================

class CreateTaskRequest(BaseModel):
    content: str
    target: Optional[str] = None


class DecideRequest(BaseModel):
    action: str  # approve / regenerate
    note: Optional[str] = None


class RerunRequest(BaseModel):
    from_stage: Optional[str] = "S0"


def _get_task_or_404(db: Session, task_id: int) -> DecomposeTask:
    task = db.get(DecomposeTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    return task


# =============================================================================
# 任务类
# =============================================================================

@router.post("/tasks", status_code=201)
async def create_task(payload: CreateTaskRequest, db: Session = Depends(get_db)):
    try:
        task = service.create_task(db, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.refresh(task)
    return service.serialize_task(task)


@router.get("/tasks")
async def list_tasks(
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(DecomposeTask).order_by(DecomposeTask.created_at.desc())
    if state:
        query = query.filter(DecomposeTask.state == state)
    tasks = query.limit(100).all()
    return [
        {
            "id": str(t.id),
            "title": t.title,
            "state": t.state,
            "version": t.version,
            "created_at": service._iso(t.created_at),
            "error": t.error,
            "gates": service.serialize_gates(t, t.decisions),
        }
        for t in tasks
    ]


@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_task_or_404(db, task_id)
    return service.serialize_task(task)


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除任务（级联删除契约与闸门决策记录），任务不存在返回 404"""
    try:
        service.delete_task(db, task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"ok": True, "id": str(task_id)}


@router.get("/tasks/{task_id}/gates")
async def get_gates(task_id: int, db: Session = Depends(get_db)):
    task = _get_task_or_404(db, task_id)
    return list(service.serialize_gates(task, task.decisions).values())


# =============================================================================
# SSE 进度订阅
# =============================================================================

@router.get("/tasks/{task_id}/events")
async def stream_events(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = _get_task_or_404(db, task_id)
    queue: asyncio.Queue = asyncio.Queue()
    service.subscribe(task.id, queue)

    # 重连时立即回放当前可观察状态，避免客户端错过闸门/终态事件。
    replay = service.replay_current_event(task)
    if replay:
        queue.put_nowait(replay)

    async def event_stream():
        try:
            yield ": connected\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                payload = json.dumps(event, ensure_ascii=False)
                yield f"event: {event['type']}\ndata: {payload}\n\n"
                if event["type"] in ("complete", "error"):
                    break
        finally:
            service.unsubscribe(task.id, queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# =============================================================================
# 闸门类
# =============================================================================

@router.post("/gates/{gate_id}/decide")
async def decide_gate(gate_id: str, payload: DecideRequest, db: Session = Depends(get_db)):
    try:
        task = service.decide_gate(db, gate_id, payload.action, payload.note or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.refresh(task)
    return service.serialize_task(task)


# =============================================================================
# 动作类
# =============================================================================

@router.post("/tasks/{task_id}/rerun")
async def rerun_task(task_id: int, payload: RerunRequest, db: Session = Depends(get_db)):
    try:
        task = service.rerun(db, task_id, payload.from_stage or "S0")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": str(task.id), "state": task.state, "version": task.version}


@router.post("/tasks/{task_id}/export")
async def export_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_task_or_404(db, task_id)
    if task.state not in ("DONE", "INSIGHT_REVIEW"):
        raise HTTPException(status_code=400, detail="任务尚未完成，无法导出")
    markdown = service.export_markdown(db, task_id)
    return {"markdown": markdown, "filename": f"拆解报告_{task.id}.md"}
