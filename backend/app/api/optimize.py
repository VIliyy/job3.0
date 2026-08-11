# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 一体化优化 API（v2.0 核心）

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import hashlib
import json

from app.core.database import get_db
from app.models.resume import Resume, ResumeVersion, ResumeStatus
from app.models.jd import JDAnalysis
from app.services.resume_service import ResumeService
from app.agents.analyzer import JDAnalyzer


def _extract_jd_info(jd_text: str) -> dict:
    """规则提取 JD 关键信息（快速、无需 AI）"""
    try:
        return JDAnalyzer().quick_extract(jd_text)
    except Exception:
        return {}


def _normalize_diff_highlights(diffs) -> list:
    """规范化 AI 返回的差异高亮：兼容字符串数组 / dict / 混合格式"""
    normalized = []
    if not diffs:
        return normalized
    if isinstance(diffs, dict):
        diffs = [diffs]
    if not isinstance(diffs, (list, tuple)):
        return normalized
    for d in diffs:
        if isinstance(d, str):
            normalized.append({"type": "modified", "content": d})
        elif isinstance(d, dict):
            item = dict(d)
            item.setdefault("type", "modified")
            content = item.get("content") or item.get("new_content") or item.get("description") or ""
            item["content"] = content
            normalized.append(item)
    return normalized


def _calc_fit_score(resume_content: str, jd_content: str) -> int:
    """基于关键词交集的匹配度（0-100）"""
    import re
    def keywords(text: str):
        return set(re.findall(r'[\u4e00-\u9fa5A-Za-z+#]{2,20}', text.lower()))
    jd_kw = keywords(jd_content)
    resume_kw = keywords(resume_content or "")
    if not jd_kw:
        return 0
    matched = jd_kw & resume_kw
    return int(min(len(matched) / len(jd_kw) * 100, 100))

router = APIRouter(prefix="/optimize", tags=["一体化优化 v2.0"])


class JDAnalysisRequest(BaseModel):
    raw_content: str
    company: Optional[str] = None
    position: Optional[str] = None
    source_url: Optional[str] = None


class OptimizationRequest(BaseModel):
    resume_id: int
    jd_content: str
    company: Optional[str] = None
    position: Optional[str] = None
    source_url: Optional[str] = None
    optimization_rules: Optional[Dict[str, Any]] = None


class OptimizationResult(BaseModel):
    version_id: int
    version_number: int
    optimized_content: str
    original_score: int
    optimized_score: int
    change_summary: str
    diff_highlights: List[Dict]
    jd_analysis: Optional[Dict[str, Any]] = None


@router.post("/full", response_model=OptimizationResult)
async def full_optimization(request: OptimizationRequest, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    if not resume.content or not resume.content.strip():
        raise HTTPException(status_code=400, detail="该简历没有可优化的内容，请先编辑或上传简历内容")

    resume.status = ResumeStatus.PROCESSING
    db.commit()
    
    try:
        content_hash = hashlib.md5(request.jd_content.encode()).hexdigest()
        jd = db.query(JDAnalysis).filter(JDAnalysis.content_hash == content_hash).first()
        
        # JD 规则提取（快速、无需 AI，保证反馈及时）
        quick_info = _extract_jd_info(request.jd_content)
        jd_company = request.company or quick_info.get("company")
        jd_position = request.position or quick_info.get("position")
        jd_skills = quick_info.get("core_skills") or []
        
        if not jd:
            jd = JDAnalysis(
                company=jd_company,
                position=jd_position,
                source_url=request.source_url,
                raw_content=request.jd_content,
                content_hash=content_hash,
                skills=jd_skills,
                keywords=jd_skills,
                requirements=quick_info.get("preferred_skills") or [],
                fit_score=_calc_fit_score(resume.content, request.jd_content)
            )
            db.add(jd)
            db.commit()
            db.refresh(jd)
        else:
            # 补充缺失的提取信息
            changed = False
            if not jd.company and jd_company:
                jd.company = jd_company; changed = True
            if not jd.position and jd_position:
                jd.position = jd_position; changed = True
            if not jd.skills and jd_skills:
                jd.skills = jd_skills; changed = True
            if not jd.keywords and jd_skills:
                jd.keywords = jd_skills; changed = True
            if jd.fit_score is None:
                jd.fit_score = _calc_fit_score(resume.content, request.jd_content); changed = True
            if changed:
                db.commit()
        
        service = ResumeService(db)
        optimization_result = await service.optimize_resume_full(
            resume.content,
            request.jd_content,
            optimization_rules=request.optimization_rules
        )
        
        original_score = optimization_result.get("original_score", 60)
        optimized_score = optimization_result.get("optimized_score", 85)
        diff_highlights = _normalize_diff_highlights(optimization_result.get("diff_highlights"))
        
        latest_version = db.query(ResumeVersion).filter(
            ResumeVersion.resume_id == resume.id
        ).order_by(ResumeVersion.version_number.desc()).first()
        
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        original_content = resume.content
        version = ResumeVersion(
            resume_id=resume.id,
            version_number=new_version_number,
            version_name=f"v{new_version_number}",
            original_content=original_content,
            content=optimization_result.get("optimized_content"),
            content_hash=hashlib.md5(optimization_result.get("optimized_content", "").encode()).hexdigest(),
            jd_id=jd.id,
            optimization_score=optimized_score,
            original_score=original_score,
            change_summary=optimization_result.get("change_summary"),
            diff_highlights=json.dumps(diff_highlights, ensure_ascii=False)
        )
        
        db.add(version)
        db.flush()  # 先 flush 拿到 version.id，避免 latest_optimized_version_id 存成 None
        resume.status = ResumeStatus.OPTIMIZED
        resume.content = optimization_result.get("optimized_content") or original_content
        resume.current_jd_id = jd.id
        resume.latest_optimized_version_id = version.id
        if jd_company and jd_position:
            resume.version_name = f"{jd_company}-{jd_position}"
        else:
            resume.version_name = resume.version_name or resume.filename
        
        db.commit()
        db.refresh(version)
        
        return OptimizationResult(
            version_id=version.id,
            version_number=version.version_number,
            optimized_content=version.content,
            original_score=original_score,
            optimized_score=optimized_score,
            change_summary=version.change_summary or "",
            diff_highlights=diff_highlights,
            jd_analysis={"id": jd.id, "company": jd.company, "position": jd.position, "fit_score": jd.fit_score, "skills": jd.skills or [], "keywords": jd.keywords or []} if jd else None
        )
        
    except Exception as e:
        resume.status = ResumeStatus.DRAFT
        db.commit()
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")


@router.post("/analyze-jd")
async def analyze_jd(request: JDAnalysisRequest, db: Session = Depends(get_db)):
    content_hash = hashlib.md5(request.raw_content.encode()).hexdigest()
    
    existing = db.query(JDAnalysis).filter(JDAnalysis.content_hash == content_hash).first()
    if existing:
        return existing.to_dict()
    
    quick_info = _extract_jd_info(request.raw_content)
    skills = quick_info.get("core_skills") or []
    jd = JDAnalysis(
        company=request.company or quick_info.get("company"),
        position=request.position or quick_info.get("position"),
        source_url=request.source_url,
        raw_content=request.raw_content,
        content_hash=content_hash,
        skills=skills,
        keywords=skills,
        requirements=quick_info.get("preferred_skills") or []
    )
    
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return jd.to_dict()


@router.get("/compare/{resume_id}")
def get_optimization_compare(resume_id: int, version_id: Optional[int] = None, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    current_content = resume.content
    
    if version_id:
        target_version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id, ResumeVersion.resume_id == resume_id).first()
    else:
        target_version = db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id).order_by(ResumeVersion.version_number.desc()).first()
    
    if not target_version:
        raise HTTPException(status_code=404, detail="没有找到优化版本")

    # 对比基准：优先使用该版本的优化前内容（避免被后续优化覆盖导致对比无效）
    if target_version.original_content:
        current_content = target_version.original_content
    
    jd_info = None
    if target_version.jd_id:
        jd = db.query(JDAnalysis).filter(JDAnalysis.id == target_version.jd_id).first()
        if jd:
            jd_info = {"id": jd.id, "company": jd.company, "position": jd.position, "fit_score": jd.fit_score}
    
    diff_highlights = []
    if target_version.diff_highlights:
        try:
            diff_highlights = json.loads(target_version.diff_highlights)
        except:
            pass
    
    return {
        "resume_id": resume_id,
        "current_content": current_content,
        "optimized_content": target_version.content,
        "original_score": target_version.original_score,
        "optimized_score": target_version.optimization_score,
        "change_summary": target_version.change_summary,
        "diff_highlights": diff_highlights,
        "version_number": target_version.version_number,
        "jd_info": jd_info
    }


@router.get("/versions/{resume_id}")
def get_version_comparison(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    versions = db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id).order_by(ResumeVersion.version_number.desc()).all()
    
    result = []
    for v in versions:
        jd_info = None
        if v.jd_id:
            jd = db.query(JDAnalysis).filter(JDAnalysis.id == v.jd_id).first()
            if jd:
                jd_info = {"company": jd.company, "position": jd.position}
        
        result.append({
            "version_id": v.id,
            "version_number": v.version_number,
            "version_name": v.version_name,
            "original_score": v.original_score,
            "optimized_score": v.optimization_score,
            "change_summary": v.change_summary,
            "jd_info": jd_info,
            "created_at": v.created_at.isoformat() if v.created_at else None
        })
    
    return {"resume_id": resume_id, "current_content": resume.content, "versions": result}


# ============ ???? API ============

class ScoreAnalysisRequest(BaseModel):
    resume_content: str
    jd_content: str


class ScoreAnalysisResult(BaseModel):
    scores: List[int]
    total_score: int
    labels: List[str]
    matched_keywords: List[str]
    missing_keywords: List[str]
    suggestions: List[Dict[str, Any]]


@router.post("/analyze-score", response_model=ScoreAnalysisResult)
async def analyze_score(request: ScoreAnalysisRequest):
    """
    ????????
    
    ??5?????
    - ??????20??
    - ??????20??
    - ?????20??
    - ?????20??
    - ATS????20??
    """
    from app.services.score_analyzer import analyze_resume_score
    
    result = analyze_resume_score(
        resume_content=request.resume_content,
        jd_content=request.jd_content
    )
    
    return ScoreAnalysisResult(**result)
