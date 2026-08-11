# -*- coding: utf-8 -*-
# Job3.0 求职系统 - JD分析 API（v2.0）

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import hashlib

from app.core.database import get_db
from app.models.jd import JDAnalysis
from app.schemas.jd import JDAnalysisCreate, JDAnalysisUpdate, JDAnalysisResponse, JDAnalysisBrief

router = APIRouter(prefix="/jd", tags=["JD分析 v2.0"])


def compute_content_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


@router.post("/", response_model=JDAnalysisResponse, status_code=201)
def create_jd_analysis(jd_data: JDAnalysisCreate, db: Session = Depends(get_db)):
    content_hash = compute_content_hash(jd_data.raw_content)
    existing = db.query(JDAnalysis).filter(JDAnalysis.content_hash == content_hash).first()
    
    if existing:
        return existing
    
    db_jd = JDAnalysis(
        company=jd_data.company,
        position=jd_data.position,
        source_url=jd_data.source_url,
        raw_content=jd_data.raw_content,
        content_hash=content_hash
    )
    
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd


@router.get("/", response_model=List[JDAnalysisBrief])
def list_jd_analyses(skip: int = 0, limit: int = 20, company: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(JDAnalysis)
    if company:
        query = query.filter(JDAnalysis.company.contains(company))
    return query.order_by(JDAnalysis.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{jd_id}", response_model=JDAnalysisResponse)
def get_jd_analysis(jd_id: int, db: Session = Depends(get_db)):
    jd = db.query(JDAnalysis).filter(JDAnalysis.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail=f"JD分析记录 {jd_id} 不存在")
    return jd


@router.put("/{jd_id}", response_model=JDAnalysisResponse)
def update_jd_analysis(jd_id: int, jd_data: JDAnalysisUpdate, db: Session = Depends(get_db)):
    jd = db.query(JDAnalysis).filter(JDAnalysis.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail=f"JD分析记录 {jd_id} 不存在")
    
    update_data = jd_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(jd, field, value)
    
    db.commit()
    db.refresh(jd)
    return jd


@router.delete("/{jd_id}")
def delete_jd_analysis(jd_id: int, db: Session = Depends(get_db)):
    jd = db.query(JDAnalysis).filter(JDAnalysis.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail=f"JD分析记录 {jd_id} 不存在")
    
    db.delete(jd)
    db.commit()


@router.post("/analyze", response_model=JDAnalysisResponse)
async def analyze_jd_with_ai(jd_data: JDAnalysisCreate, db: Session = Depends(get_db)):
    content_hash = compute_content_hash(jd_data.raw_content)
    jd = db.query(JDAnalysis).filter(JDAnalysis.content_hash == content_hash).first()
    
    if not jd:
        jd = JDAnalysis(
            company=jd_data.company,
            position=jd_data.position,
            source_url=jd_data.source_url,
            raw_content=jd_data.raw_content,
            content_hash=content_hash
        )
        db.add(jd)
        db.commit()
        db.refresh(jd)
    
    return jd
