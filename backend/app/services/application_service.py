# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 投递记录服务

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from app.models.application import Application, ApplicationStatus


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Application]:
        return self.db.query(Application).order_by(Application.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_id(self, app_id: int) -> Optional[Application]:
        return self.db.query(Application).filter(Application.id == app_id).first()

    def get_by_resume(self, resume_id: int) -> List[Application]:
        return self.db.query(Application).filter(Application.resume_id == resume_id).order_by(Application.created_at.desc()).all()

    def create(self, app_data: dict) -> Application:
        application = Application(**app_data)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def update_status(self, app_id: int, status: str) -> Optional[Application]:
        application = self.get_by_id(app_id)
        if application:
            application.status = status
            application.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(application)
        return application

    def delete(self, app_id: int) -> bool:
        application = self.get_by_id(app_id)
        if application:
            self.db.delete(application)
            self.db.commit()
            return True
        return False
