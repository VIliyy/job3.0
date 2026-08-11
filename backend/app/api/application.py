# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 投递记录 API（v2.0）

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.database import get_db
from app.models.application import Application, ApplicationStatus
from app.models.resume import Resume, ResumeStatus
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationWithResume, ApplicationBrief

router = APIRouter(prefix="/applications", tags=["投递记录 v2.0"])


@router.post("/", response_model=ApplicationResponse, status_code=201)
def create_application(app_data: ApplicationCreate, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == app_data.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail=f"简历 {app_data.resume_id} 不存在")
    
    application = Application(
        resume_id=app_data.resume_id,
        company=app_data.company,
        position=app_data.position,
        status=app_data.status,
        salary=app_data.salary,
        location=app_data.location,
        job_url=app_data.job_url,
        source=app_data.source
    )
    
    db.add(application)
    resume.status = ResumeStatus.APPLIED
    db.commit()
    db.refresh(application)
    return application


@router.get("/", response_model=List[ApplicationWithResume])
def list_applications(resume_id: Optional[int] = None, status: Optional[str] = None, company: Optional[str] = None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Application).options(joinedload(Application.resume))
    
    if resume_id:
        query = query.filter(Application.resume_id == resume_id)
    if status:
        query = query.filter(Application.status == status)
    if company:
        query = query.filter(Application.company.contains(company))
    
    applications = query.order_by(Application.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for app in applications:
        app_dict = app.to_dict()
        if app.resume:
            app_dict["resume_category"] = app.resume.category.value if app.resume.category else None
            app_dict["resume_version_name"] = app.resume.version_name
        result.append(app_dict)
    
    return result


@router.get("/by-resume/{resume_id}", response_model=List[ApplicationBrief])
def get_applications_by_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    applications = db.query(Application).filter(Application.resume_id == resume_id).order_by(Application.created_at.desc()).all()
    return applications


@router.get("/{app_id}", response_model=ApplicationWithResume)
def get_application(app_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).options(joinedload(Application.resume)).filter(Application.id == app_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    
    app_dict = application.to_dict()
    if application.resume:
        app_dict["resume_category"] = application.resume.category.value if application.resume.category else None
        app_dict["resume_version_name"] = application.resume.version_name
    
    return app_dict


@router.put("/{app_id}", response_model=ApplicationResponse)
def update_application(app_id: int, update_data: ApplicationUpdate, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == app_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == app_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    
    db.delete(application)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{app_id}/status")
def update_application_status(app_id: int, status: str, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == app_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    
    application.status = status
    db.commit()
    return {"message": f"状态已更新为 {status}"}
