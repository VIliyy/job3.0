# -*- coding: utf-8 -*-
"""
视频笔记 API（小林工具箱）
POST /api/video-notes/generate        创建任务（后台线程执行）
GET  /api/video-notes/tasks           任务列表
GET  /api/video-notes/tasks/{task_id} 任务详情（含 Markdown）
POST /api/video-notes/upload          上传本地音视频
GET  /api/video-notes/config          读取配置（Obsidian 路径等）
POST /api/video-notes/config          保存配置
POST /api/video-notes/tasks/{task_id}/export-obsidian  导出到 Obsidian
"""
import logging
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, SessionLocal
from app.models.video_task import VideoTask
from app.schemas.video_task import (
    VideoNoteCreate, VideoTaskBrief, VideoTaskDetail, VideoConfigIn, VideoConfigOut,
)
from app.services.video.config_store import get_config, set_config
from app.services.video.downloader import detect_platform, LOCAL_MEDIA_EXTS
from app.services.video.generator import VideoNoteGenerator
from app.services.video.obsidian import validate_vault, ObsidianExporter
from app.services.video.summarizer import resolve_llm_config
from app.core.utils import resolve_within_directory, sanitize_filename, save_upload_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/video-notes", tags=["视频笔记"])

_executor = ThreadPoolExecutor(max_workers=max(1, settings.VIDEO_TASK_WORKERS))


def recover_incomplete_video_tasks() -> int:
    """Resubmit persisted video tasks that were interrupted by a restart."""
    db = SessionLocal()
    recovered = 0
    try:
        tasks = (
            db.query(VideoTask)
            .filter(VideoTask.status.in_(("PENDING", "PARSING", "DOWNLOADING", "TRANSCRIBING", "SUMMARIZING", "OBSIDIAN")))
            .all()
        )
        for task in tasks:
            _executor.submit(_run_generator, task.task_id)
            recovered += 1
        return recovered
    finally:
        db.close()


def _run_generator(task_id: str):
    db = SessionLocal()
    try:
        task = db.query(VideoTask).filter(VideoTask.task_id == task_id).first()
        if not task:
            return
        VideoNoteGenerator(db=db).generate(task)
    except Exception as exc:  # noqa: BLE001
        logger.exception("视频笔记后台任务异常")
        task = db.query(VideoTask).filter(VideoTask.task_id == task_id).first()
        if task:
            task.status = "FAILED"
            task.error = str(exc)[:500]
            task.status_message = "后台执行异常"
            db.commit()
    finally:
        db.close()


@router.post("/generate")
def generate_note(data: VideoNoteCreate, db: Session = Depends(get_db)):
    try:
        platform = data.platform
        if platform == "auto":
            platform = detect_platform(data.video_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if platform == "local":
        try:
            resolve_within_directory(data.video_url, settings.UPLOAD_DIR)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="本地媒体文件必须位于上传目录内") from exc

    task = VideoTask(
        task_id=uuid.uuid4().hex[:16],
        video_url=data.video_url,
        platform=platform,
        style=data.style or "minimal",
        extras=data.extras,
        export_obsidian=bool(data.export_obsidian),
        status="PENDING",
    )
    task.set_formats(data.formats or [])
    db.add(task)
    db.commit()
    db.refresh(task)

    _executor.submit(_run_generator, task.task_id)
    return VideoTaskBrief.model_validate(task)


@router.get("/tasks", response_model=list[VideoTaskBrief])
def list_tasks(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    tasks = db.query(VideoTask).order_by(VideoTask.id.desc()).limit(min(limit, 200)).all()
    return [VideoTaskBrief.model_validate(t) for t in tasks]


@router.get("/tasks/{task_id}", response_model=VideoTaskDetail)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(VideoTask).filter(VideoTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    detail = VideoTaskDetail.model_validate(task)
    detail.formats = task.get_formats()
    return detail


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(VideoTask).filter(VideoTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
    return {"ok": True}


@router.post("/upload")
async def upload_local(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in LOCAL_MEDIA_EXTS:
        raise HTTPException(status_code=400, detail=f"不支持的媒体格式: {ext or '未知'}")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = sanitize_filename(file.filename or "video")
    save_path = os.path.join(settings.UPLOAD_DIR, f"video_{uuid.uuid4().hex[:8]}_{safe_name}")
    try:
        file_size = await save_upload_file(file, save_path, settings.MAX_VIDEO_UPLOAD_SIZE)
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    return {"path": os.path.abspath(save_path), "url": f"/uploads/{os.path.basename(save_path)}", "size": file_size}


@router.get("/config", response_model=VideoConfigOut)
def read_config():
    cfg = get_config()
    vault = cfg.get("obsidian_vault_path", "")
    valid, msg = validate_vault(vault)
    llm_provider = ""
    llm_configured = False
    try:
        _, base_url, model = resolve_llm_config()
        llm_configured = True
        llm_provider = f"{base_url} ({model})"
    except Exception:  # noqa: BLE001
        pass
    return VideoConfigOut(
        obsidian_vault_path=vault,
        obsidian_valid=valid,
        obsidian_message=msg,
        llm_configured=llm_configured,
        llm_provider=llm_provider,
        whisper_model=settings.WHISPER_MODEL_SIZE,
    )


@router.post("/config")
def save_config(data: VideoConfigIn):
    vault = (data.obsidian_vault_path or "").strip().strip('"')
    if vault:
        valid, msg = validate_vault(vault)
        if not valid:
            raise HTTPException(status_code=400, detail=f"Obsidian 路径无效: {msg}")
    set_config({"obsidian_vault_path": vault})
    return {"ok": True, "obsidian_vault_path": vault}


@router.post("/tasks/{task_id}/export-obsidian")
def export_obsidian(task_id: str, db: Session = Depends(get_db)):
    task = db.query(VideoTask).filter(VideoTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if not task.markdown:
        raise HTTPException(status_code=400, detail="任务还没有生成 Markdown")
    cfg = get_config()
    vault = cfg.get("obsidian_vault_path", "")
    valid, msg = validate_vault(vault)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)
    path = ObsidianExporter(vault).export(task.markdown, task.title or task.task_id, task.platform, task.video_url)
    task.obsidian_path = path
    task.obsidian_exported = True
    task.obsidian_message = "已导出"
    db.commit()
    return {"ok": True, "path": path}
