# -*- coding: utf-8 -*-
# Job3.0 求职系统 - JD服务

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import hashlib

from app.models.jd import JDAnalysis


class JDService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[JDAnalysis]:
        return self.db.query(JDAnalysis).order_by(JDAnalysis.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_id(self, jd_id: int) -> Optional[JDAnalysis]:
        return self.db.query(JDAnalysis).filter(JDAnalysis.id == jd_id).first()

    def create(self, jd_data: dict) -> JDAnalysis:
        content_hash = hashlib.md5(jd_data.get("raw_content", "").encode()).hexdigest()
        jd_data["content_hash"] = content_hash
        jd = JDAnalysis(**jd_data)
        self.db.add(jd)
        self.db.commit()
        self.db.refresh(jd)
        return jd

    def update(self, jd_id: int, update_data: dict) -> Optional[JDAnalysis]:
        jd = self.get_by_id(jd_id)
        if jd:
            for key, value in update_data.items():
                if value is not None:
                    setattr(jd, key, value)
            jd.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(jd)
        return jd

    def delete(self, jd_id: int) -> bool:
        jd = self.get_by_id(jd_id)
        if jd:
            self.db.delete(jd)
            self.db.commit()
            return True
        return False
