# -*- coding: utf-8 -*-
# Job3.0 求职系统 - JD职位描述模型

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base


class JDAnalysis(Base):
    __tablename__ = "jd_analyses"
    
    __table_args__ = (
        Index("idx_jd_company", "company"),
        Index("idx_jd_position", "position"),
        Index("idx_jd_created", "created_at"),
        {"sqlite_autoincrement": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    source_url = Column(String(512), nullable=True)
    raw_content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)
    analysis_result = Column(JSON, nullable=True)
    requirements = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    responsibilities = Column(JSON, nullable=True)
    fit_score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "position": self.position,
            "source_url": self.source_url,
            "raw_content": self.raw_content,
            "requirements": self.requirements,
            "skills": self.skills,
            "keywords": self.keywords,
            "responsibilities": self.responsibilities,
            "fit_score": self.fit_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
