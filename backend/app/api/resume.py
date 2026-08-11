# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 简历管理API（v2.0）

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel, Field
import os
import uuid
import hashlib

from app.core.database import get_db
from app.core.config import settings
from app.models.resume import Resume, ResumeVersion, ResumeCategory, ResumeStatus
from app.schemas.resume import ResumeResponse, ResumeCreate, ResumeUpdate, ResumeBrief, ResumeWithVersions, ResumeVersionResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["简历管理 v2.0"])


# 兼容中文标签 / 大小写差异 / 非法值，统一映射为枚举值，避免 SQLAlchemy Enum 校验崩溃
_CATEGORY_ALIASES = {
    "tech": ResumeCategory.TECH, "技术": ResumeCategory.TECH,
    "product": ResumeCategory.PRODUCT, "产品": ResumeCategory.PRODUCT,
    "ops": ResumeCategory.OPERATIONS, "运营": ResumeCategory.OPERATIONS,
    "marketing": ResumeCategory.MARKETING, "市场": ResumeCategory.MARKETING,
    "other": ResumeCategory.OTHER, "其他": ResumeCategory.OTHER,
}
_STATUS_ALIASES = {
    "draft": ResumeStatus.DRAFT, "草稿": ResumeStatus.DRAFT,
    "processing": ResumeStatus.PROCESSING, "处理中": ResumeStatus.PROCESSING,
    "optimized": ResumeStatus.OPTIMIZED, "已优化": ResumeStatus.OPTIMIZED,
    "applied": ResumeStatus.APPLIED, "已投递": ResumeStatus.APPLIED,
    "archived": ResumeStatus.ARCHIVED, "已归档": ResumeStatus.ARCHIVED,
}


def normalize_category(category) -> ResumeCategory:
    if isinstance(category, ResumeCategory):
        return category
    key = str(category or "").strip().lower()
    return _CATEGORY_ALIASES.get(key, ResumeCategory.OTHER)


def normalize_status(status) -> ResumeStatus:
    if isinstance(status, ResumeStatus):
        return status
    key = str(status or "").strip().lower()
    return _STATUS_ALIASES.get(key, ResumeStatus.DRAFT)


@router.post("/", response_model=ResumeResponse, status_code=201)
async def create_resume(resume_data: ResumeCreate, db: Session = Depends(get_db)):
    existing = db.query(Resume).filter(Resume.slot == resume_data.slot).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"槽位 {resume_data.slot} 已被占用")
    
    resume = Resume(
        slot=resume_data.slot,
        filename=resume_data.filename,
        filepath=resume_data.filepath,
        content=resume_data.content,
        file_size=resume_data.file_size,
        file_type=resume_data.file_type,
        category=normalize_category(resume_data.category),
        version_name=resume_data.version_name,
        status=ResumeStatus.DRAFT
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/", response_model=List[ResumeBrief])
def list_resumes(category: Optional[str] = None, status: Optional[str] = None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Resume)
    if category:
        query = query.filter(Resume.category == normalize_category(category))
    if status:
        query = query.filter(Resume.status == normalize_status(status))
    return query.order_by(Resume.updated_at.desc()).offset(skip).limit(limit).all()


@router.get("/{resume_id}", response_model=ResumeWithVersions)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).options(joinedload(Resume.versions)).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    application_count = len(resume.applications) if hasattr(resume, 'applications') else 0
    return {**resume.__dict__, "versions": resume.versions, "application_count": application_count}


@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(resume_id: int, update_data: ResumeUpdate, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    update_dict = update_data.model_dump(exclude_unset=True)
    if "category" in update_dict:
        update_dict["category"] = normalize_category(update_dict["category"])
    if "status" in update_dict:
        update_dict["status"] = normalize_status(update_dict["status"])
    for field, value in update_dict.items():
        setattr(resume, field, value)
    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    import os
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    if os.path.exists(resume.filepath):
        os.remove(resume.filepath)
    db.delete(resume)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{resume_id}/versions", response_model=List[ResumeVersionResponse])
def get_resume_versions(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    versions = db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id).order_by(ResumeVersion.version_number.desc()).all()
    return versions


@router.post("/{resume_id}/versions", response_model=ResumeVersionResponse)
def create_resume_version(resume_id: int, version_data: dict, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    latest = db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id).order_by(ResumeVersion.version_number.desc()).first()
    new_version_number = (latest.version_number + 1) if latest else 1
    
    version = ResumeVersion(
        resume_id=resume_id,
        version_number=new_version_number,
        version_name=version_data.get("version_name"),
        content=version_data.get("content"),
        content_hash=hashlib.md5(version_data.get("content", "").encode()).hexdigest() if version_data.get("content") else None,
        jd_id=version_data.get("jd_id"),
        optimization_score=version_data.get("optimization_score"),
        original_score=version_data.get("original_score"),
        change_summary=version_data.get("change_summary"),
        diff_highlights=version_data.get("diff_highlights")
    )
    
    db.add(version)
    resume.status = ResumeStatus.OPTIMIZED
    resume.latest_optimized_version_id = version.id
    resume.content = version.content
    
    db.commit()
    db.refresh(version)
    return version


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(file: UploadFile = File(...), slot: int = Query(1, ge=1, le=4), category: str = "other", version_name: Optional[str] = None, db: Session = Depends(get_db)):
    if file.filename:
        ext = file.filename.split(".")[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式")
    
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
    
    filename = f"resume_{slot}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    service = ResumeService(db)
    content_text = await service.parse_resume(filepath, ext)
    
    resume = await service.save_resume_v2(
        slot=slot, filename=file.filename or filename, filepath=filepath,
        content=content_text, file_type=ext, file_size=len(content),
        category=normalize_category(category), version_name=version_name
    )
    return resume


class SaveTextRequest(BaseModel):
    slot: int = Field(1, ge=1, le=4)
    content: str
    category: str = "other"
    version_name: Optional[str] = None


@router.post("/save-text", response_model=ResumeResponse)
async def save_resume_text(request: SaveTextRequest, db: Session = Depends(get_db)):
    slot = request.slot
    content = request.content
    category = request.category
    version_name = request.version_name
    filename = f"resume_text_{slot}.txt"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    service = ResumeService(db)
    resume = await service.save_resume_v2(
        slot=slot, filename=filename, filepath=filepath,
        content=content, file_type="txt", file_size=len(content.encode()),
        category=normalize_category(category), version_name=version_name
    )
    return resume
