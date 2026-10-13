# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 浏览器扩展桥接 API（海投助手本地桥 v1.0）

供本地 Edge/Chrome 扩展（content script -> background -> 本接口）调用：
- 投递去重：同一 job_url 只允许一条投递记录
- 落库：投递记录 + JD 原文快照（JobSnapshot）
- 打招呼：按 JD/简历模板生成打招呼文稿（纯规则模板，无 LLM 依赖）
- 记录管理：查询最近记录 / 删除误记记录

安全约定：
- 除 /health 外，所有接口要求请求头 X-Bridge-Token 与 settings.BRIDGE_TOKEN 一致
- 服务仅监听本机，扩展也只访问 http://localhost:8000
"""

import hmac
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.application import Application, ApplicationStatus
from app.models.job_snapshot import JobSnapshot
from app.models.resume import Resume
from app.schemas.bridge import BridgeJobRecordIn
from app.schemas.greeting import GreetingGenerateRequest
from app.services.greeting_service import GreetingService

router = APIRouter()
logger = logging.getLogger(__name__)


def _verify_token(x_bridge_token: Optional[str] = Header(default=None)) -> str:
    """校验扩展携带的 X-Bridge-Token 请求头"""
    token = x_bridge_token or ""
    expected = settings.BRIDGE_TOKEN
    if not hmac.compare_digest(token.encode("utf-8"), expected.encode("utf-8")):
        raise HTTPException(status_code=401, detail="X-Bridge-Token 无效")
    return token


@router.get("/health")
def bridge_health():
    """供扩展面板检测本地服务是否可用（无需 token）"""
    return {
        "ok": True,
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "service": "bridge",
    }


@router.get("/resumes", dependencies=[Depends(_verify_token)])
def bridge_list_resumes(db: Session = Depends(get_db)):
    """返回可选简历列表（含 content，用于生成打招呼语）"""
    resumes = (
        db.query(Resume)
        .order_by(Resume.is_active.desc(), Resume.id.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": r.id,
            "slot": r.slot,
            "filename": r.filename,
            "version_name": r.version_name,
            "category": r.category.value if r.category else None,
            "status": r.status.value if r.status else None,
            "is_active": r.is_active,
            "content": r.content,
        }
        for r in resumes
    ]


@router.get("/records", dependencies=[Depends(_verify_token)])
def bridge_list_records(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    """最近通过扩展记录的岗位（快照 + 投递状态）"""
    limit = max(1, min(limit, 200))
    rows = (
        db.query(JobSnapshot, Application)
        .outerjoin(Application, Application.id == JobSnapshot.application_id)
        .order_by(JobSnapshot.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "snapshot": s.to_dict(),
            "application": a.to_dict() if a else None,
        }
        for s, a in rows
    ]


@router.post("/job-record", dependencies=[Depends(_verify_token)])
async def bridge_create_job_record(data: BridgeJobRecordIn, db: Session = Depends(get_db)):
    """记录一次 BOSS 岗位投递（带去重 + JD 快照 + 打招呼生成）"""
    # 1. 去重：同一 job_url 已记录则直接返回已有记录
    if data.job_url:
        existing = (
            db.query(Application)
            .filter(Application.job_url == data.job_url)
            .order_by(Application.id.asc())
            .first()
        )
        if existing:
            snapshot = (
                db.query(JobSnapshot)
                .filter(JobSnapshot.application_id == existing.id)
                .order_by(JobSnapshot.id.desc())
                .first()
            )
            return {
                "ok": True,
                "duplicate": True,
                "application_id": existing.id,
                "snapshot_id": snapshot.id if snapshot else None,
                "greeting": snapshot.greeting if snapshot else None,
            }

    # 2. 简历校验：未传 resume_id 时自动选最近一份简历
    resume = None
    if data.resume_id is not None:
        resume = db.query(Resume).filter(Resume.id == data.resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail=f"简历 {data.resume_id} 不存在")
    else:
        resume = db.query(Resume).order_by(Resume.id.desc()).first()
    if not resume:
        raise HTTPException(
            status_code=400,
            detail="还没有可用简历，请先在工具箱创建简历后再记录投递",
        )

    # 3. 落库投递记录（默认 pending=已记录/待沟通；不自动改动简历状态）
    application = Application(
        resume_id=resume.id,
        company=data.company,
        position=data.position,
        salary=data.salary,
        location=data.location,
        job_url=data.job_url,
        source=data.source,
        status=ApplicationStatus.PENDING,
    )
    db.add(application)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(Application)
            .filter(Application.job_url == data.job_url)
            .order_by(Application.id.asc())
            .first()
        )
        if existing:
            snapshot = (
                db.query(JobSnapshot)
                .filter(JobSnapshot.application_id == existing.id)
                .order_by(JobSnapshot.id.desc())
                .first()
            )
            return {
                "ok": True,
                "duplicate": True,
                "application_id": existing.id,
                "snapshot_id": snapshot.id if snapshot else None,
                "greeting": snapshot.greeting if snapshot else None,
            }
        raise

    # 4. 打招呼文稿：优先扩展传入，否则按 JD 模板生成（失败不阻断记录）
    greeting = data.greeting
    if data.generate_greeting and not greeting and data.jd_text:
        try:
            service = GreetingService(db)
            result = await service.generate_greeting(
                GreetingGenerateRequest(
                    jd_content=data.jd_text,
                    resume_content=resume.content,
                )
            )
            greeting = result.greeting
        except Exception as exc:  # 生成打招呼失败不应影响投递记录
            logger.warning("bridge greeting generation failed", exc_info=exc)

    # 5. 落库 JD 快照
    snapshot = JobSnapshot(
        application_id=application.id,
        company=data.company,
        position=data.position,
        salary=data.salary,
        location=data.location,
        job_url=data.job_url,
        source=data.source,
        jd_text=data.jd_text,
        greeting=greeting,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(application)
    db.refresh(snapshot)

    return {
        "ok": True,
        "duplicate": False,
        "application_id": application.id,
        "snapshot_id": snapshot.id,
        "greeting": greeting,
    }


@router.delete("/records/{snapshot_id}", dependencies=[Depends(_verify_token)])
def bridge_delete_record(snapshot_id: int, db: Session = Depends(get_db)):
    """删除误记的快照及其投递记录"""
    snapshot = db.query(JobSnapshot).filter(JobSnapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="快照不存在")
    application_id = snapshot.application_id
    db.delete(snapshot)
    if application_id:
        db.query(Application).filter(Application.id == application_id).delete()
    db.commit()
    return {"ok": True, "deleted": True}
