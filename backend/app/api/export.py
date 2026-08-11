# -*- coding: utf-8 -*-
"""
Job3.0 ???? - ???? API
?? JSON ??
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import io

from app.core.database import get_db
from app.models.resume import Resume, ResumeVersion
from app.models.application import Application

router = APIRouter(prefix="/export", tags=["????"])


class ExportData(BaseModel):
    resumes: List[dict]
    applications: List[dict]
    export_time: str
    version: str = "2.1.0"


@router.get("/all")
async def export_all_data(db: Session = Depends(get_db)):
    """
    ??????? JSON
    
    ???????????????
    """
    # ??????
    resumes = db.query(Resume).all()
    resume_list = []
    for r in resumes:
        versions = db.query(ResumeVersion).filter(
            ResumeVersion.resume_id == r.id
        ).order_by(ResumeVersion.version_number.desc()).all()
        
        resume_list.append({
            "id": r.id,
            "slot": r.slot,
            "filename": r.filename,
            "version_name": r.version_name,
            "category": r.category.value if r.category else None,
            "status": r.status.value if r.status else None,
            "content": r.content,
            "file_type": r.file_type,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            "versions": [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "version_name": v.version_name,
                    "content": v.content,
                    "original_content": v.original_content,
                    "optimization_score": v.optimization_score,
                    "original_score": v.original_score,
                    "change_summary": v.change_summary,
                    "created_at": v.created_at.isoformat() if v.created_at else None
                }
                for v in versions
            ]
        })
    
    # ????????
    applications = db.query(Application).all()
    app_list = [
        {
            "id": a.id,
            "resume_id": a.resume_id,
            "company": a.company,
            "position": a.position,
            "location": a.location,
            "salary": a.salary,
            "status": a.status.value if a.status else None,
            "job_url": a.job_url,
            "notes": a.notes,
            "progress": a.progress,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None
        }
        for a in applications
    ]
    
    export_data = ExportData(
        resumes=resume_list,
        applications=app_list,
        export_time=datetime.now().isoformat()
    )
    
    return export_data


@router.get("/resume/{resume_id}")
async def export_single_resume(resume_id: int, include_versions: bool = True, db: Session = Depends(get_db)):
    """
    ???????????????
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="?????")
    
    data = {
        "id": resume.id,
        "slot": resume.slot,
        "filename": resume.filename,
        "version_name": resume.version_name,
        "category": resume.category.value if resume.category else None,
        "status": resume.status.value if resume.status else None,
        "content": resume.content,
        "file_type": resume.file_type,
        "created_at": resume.created_at.isoformat() if resume.created_at else None,
        "updated_at": resume.updated_at.isoformat() if resume.updated_at else None
    }
    
    if include_versions:
        versions = db.query(ResumeVersion).filter(
            ResumeVersion.resume_id == resume_id
        ).order_by(ResumeVersion.version_number.desc()).all()
        data["versions"] = [
            {
                "version_number": v.version_number,
                "content": v.content,
                "optimization_score": v.optimization_score,
                "created_at": v.created_at.isoformat() if v.created_at else None
            }
            for v in versions
        ]
    
    return data


@router.get("/resume-text/{resume_id}")
async def export_resume_text(resume_id: int, db: Session = Depends(get_db)):
    """
    ???????????????
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="?????")
    
    return {
        "content": resume.content,
        "filename": resume.version_name or resume.filename or "??"
    }


@router.get("/applications")
async def export_applications(
    status: Optional[str] = None,
    company: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    ????????????
    """
    query = db.query(Application)
    
    if status:
        query = query.filter(Application.status == status)
    if company:
        query = query.filter(Application.company.contains(company))
    
    applications = query.order_by(Application.created_at.desc()).all()
    
    return {
        "count": len(applications),
        "applications": [
            {
                "id": a.id,
                "company": a.company,
                "position": a.position,
                "location": a.location,
                "salary": a.salary,
                "status": a.status.value if a.status else None,
                "job_url": a.job_url,
                "notes": a.notes,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in applications
        ],
        "export_time": datetime.now().isoformat()
    }


@router.get("/backup")
async def create_backup(db: Session = Depends(get_db)):
    """
    ????????????????
    """
    export_data = await export_all_data(db)
    
    # ?????
    filename = f"job3_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # ??? JSON bytes
    json_str = json.dumps(export_data.model_dump(), ensure_ascii=False, indent=2)
    json_bytes = json_str.encode('utf-8')
    
    return StreamingResponse(
        io.BytesIO(json_bytes),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )
