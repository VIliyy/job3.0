# -*- coding: utf-8 -*-
# 控制台聚合统计 API（2026-09-02 新增：替代前端逐简历 N+1 拉取）

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.application import Application, ApplicationStatus
from app.models.resume import Resume, ResumeVersion

router = APIRouter(prefix="/dashboard", tags=["控制台统计"])

_KNOWN_STATUSES = [
    ApplicationStatus.PENDING.value,
    ApplicationStatus.SUBMITTED.value,
    ApplicationStatus.VIEWED.value,
    ApplicationStatus.INTERVIEW.value,
    ApplicationStatus.OFFER.value,
    ApplicationStatus.REJECTED.value,
    ApplicationStatus.WITHDRAWN.value,
]


def _as_local(dt):
    """SQLite func.now() 存 UTC 无时区时间，统一转本机时区后按天归桶"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone()


def _status_value(status):
    """状态可能是枚举成员或字符串，统一返回小写 value"""
    if status is None:
        return None
    return getattr(status, "value", status)


@router.get("/stats")
def dashboard_stats(days: int = Query(7, ge=7, le=90), db: Session = Depends(get_db)):
    """控制台聚合：统计卡片 / 投递漏斗 / 最近列表 / 按日趋势（一次请求）"""
    now_local = datetime.now().astimezone()
    since_utc_naive = (now_local - timedelta(days=days)).astimezone(timezone.utc).replace(tzinfo=None)
    week_utc_naive = (now_local - timedelta(days=7)).astimezone(timezone.utc).replace(tzinfo=None)

    resume_count = db.query(func.count(Resume.id)).scalar() or 0
    application_count = db.query(func.count(Application.id)).scalar() or 0
    optimization_count = db.query(func.count(ResumeVersion.id)).scalar() or 0
    applications_this_week = (
        db.query(func.count(Application.id))
        .filter(Application.created_at >= week_utc_naive)
        .scalar() or 0
    )

    # 平均分口径：每份简历最新一次有分数的优化版本
    version_rows = (
        db.query(ResumeVersion.resume_id, ResumeVersion.optimization_score)
        .order_by(ResumeVersion.created_at.desc(), ResumeVersion.id.desc())
        .all()
    )
    seen_resumes = set()
    latest_scores = []
    for resume_id, score in version_rows:
        if resume_id in seen_resumes:
            continue
        seen_resumes.add(resume_id)
        if score is not None:
            latest_scores.append(score)
    avg_score = round(sum(latest_scores) / len(latest_scores)) if latest_scores else None

    # 投递漏斗（Python 计数，避免依赖枚举存储格式）
    funnel = {status: 0 for status in _KNOWN_STATUSES}
    for (status,) in db.query(Application.status).all():
        key = _status_value(status)
        if key:
            funnel[key] = funnel.get(key, 0) + 1

    # 最近优化：取简历展示名
    recent_versions = (
        db.query(ResumeVersion)
        .order_by(ResumeVersion.created_at.desc(), ResumeVersion.id.desc())
        .limit(5)
        .all()
    )
    resume_titles = {}
    if recent_versions:
        resume_ids = {v.resume_id for v in recent_versions}
        rows = db.query(Resume.id, Resume.version_name).filter(Resume.id.in_(resume_ids)).all()
        resume_titles = {resume_id: name for resume_id, name in rows}
    recent_optimizations = [
        {
            "version_id": v.id,
            "resume_id": v.resume_id,
            "version_number": v.version_number,
            "title": resume_titles.get(v.resume_id) or ("简历 " + str(v.resume_id)),
            "score": v.optimization_score,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in recent_versions
    ]

    # 最近投递
    recent_applications = [
        {
            "id": a.id,
            "resume_id": a.resume_id,
            "company": a.company,
            "position": a.position or "",
            "status": _status_value(a.status),
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in db.query(Application)
        .order_by(Application.created_at.desc(), Application.id.desc())
        .limit(5)
        .all()
    ]

    # 按日趋势（最近 days 个自然日，含 0 值占位）
    trend_counts = {}
    for (t,) in db.query(ResumeVersion.created_at).filter(ResumeVersion.created_at >= since_utc_naive).all():
        local_date = _as_local(t).date()
        trend_counts.setdefault(local_date, [0, 0])[0] += 1
    for (t,) in db.query(Application.created_at).filter(Application.created_at >= since_utc_naive).all():
        local_date = _as_local(t).date()
        trend_counts.setdefault(local_date, [0, 0])[1] += 1

    start_date = now_local.date() - timedelta(days=days - 1)
    trend = []
    for offset in range(days):
        day = start_date + timedelta(days=offset)
        opt_count, app_count = trend_counts.get(day, [0, 0])
        trend.append(
            {
                "date": day.isoformat(),
                "label": "%d/%d" % (day.month, day.day),
                "optimizations": opt_count,
                "applications": app_count,
            }
        )

    return {
        "generated_at": now_local.isoformat(),
        "days": days,
        "stats": {
            "resume_count": resume_count,
            "application_count": application_count,
            "applications_this_week": applications_this_week,
            "optimization_count": optimization_count,
            "avg_score": avg_score,
        },
        "funnel": funnel,
        "recent_optimizations": recent_optimizations,
        "recent_applications": recent_applications,
        "trend": trend,
    }