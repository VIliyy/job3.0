# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 简历服务 (v2.0)

import re
import json
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from typing import Optional, Dict, Any, List

from app.models.resume import Resume, ResumeVersion, ResumeStatus, ResumeCategory
from app.core.config import settings


def get_ai_service():
    """获取全局 AI 服务实例（复用 agents/base.py 的真实实现）"""
    from app.agents.base import ai_service
    return ai_service


class ResumeParser:
    @classmethod
    def parse(cls, text: str) -> Dict[str, Any]:
        if not text or len(text) < 50:
            return cls._empty_result()
        text = cls._clean_text(text)
        return {
            "raw_text": text[:500],
            "basic_info": cls._extract_basic_info(text),
            "skills": cls._extract_skills(text),
        }

    @classmethod
    def _clean_text(cls, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @classmethod
    def _empty_result(cls) -> Dict[str, Any]:
        return {"raw_text": "", "basic_info": {}, "skills": {"technical": [], "soft": []}}

    @classmethod
    def _extract_basic_info(cls, text: str) -> Dict[str, str]:
        info = {"phone": "", "email": ""}
        match = re.search(r'(1[3-9]\d{9})', text)
        if match: info["phone"] = match.group(1)
        match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        if match: info["email"] = match.group(0)
        return info

    @classmethod
    def _extract_skills(cls, text: str) -> Dict[str, List[str]]:
        keywords = ['Python', 'Java', 'JavaScript', 'Go', 'React', 'Vue', 'MySQL', 'Docker', 'AWS']
        text_lower = text.lower()
        found = [kw for kw in keywords if kw.lower() in text_lower]
        return {"technical": found, "soft": []}

    @classmethod
    async def parse_with_ai(cls, content: str) -> Dict[str, Any]:
        try:
            ai = get_ai_service()
            if ai and ai.llm:
                prompt = f"解析简历: {content[:1000]}\n返回JSON"
                response = await ai.chat_simple(prompt)
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
        except Exception as e:
            print(f"AI解析失败: {e}")
        return cls.parse(content)


class ResumeService:
    def __init__(self, db: Session):
        self.db = db

    async def parse_resume(self, filepath: str, file_type: str) -> str:
        if file_type == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    async def save_resume_v2(self, slot: int, filename: str, filepath: str, content: str, file_type: str, file_size: int, category: str = 'other', version_name: str = None) -> Resume:
        existing = self.db.query(Resume).filter(Resume.slot == slot).first()
        if existing:
            existing.filename = filename
            existing.filepath = filepath
            existing.content = content
            existing.file_type = file_type
            existing.file_size = file_size
            existing.category = category
            existing.version_name = version_name
            existing.updated_at = datetime.now()
            resume = existing
        else:
            resume = Resume(slot=slot, filename=filename, filepath=filepath, content=content, file_type=file_type, file_size=file_size, category=category, version_name=version_name, status=ResumeStatus.DRAFT)
            self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    async def get_all_resumes(self) -> List[Resume]:
        return self.db.query(Resume).order_by(Resume.slot).all()

    async def get_resume_by_slot(self, slot: int) -> Optional[Resume]:
        return self.db.query(Resume).filter(Resume.slot == slot).first()

    async def delete_resume(self, slot: int) -> bool:
        import os
        resume = await self.get_resume_by_slot(slot)
        if resume:
            if os.path.exists(resume.filepath):
                os.remove(resume.filepath)
            self.db.delete(resume)
            self.db.commit()
            return True
        return False

    async def optimize_resume_full(self, resume_content: str, jd_content: str, optimization_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        ai = get_ai_service()
        if ai and ai.llm:
            try:
                return await self._optimize_with_ai(resume_content, jd_content, optimization_rules)
            except Exception as e:
                print(f"[WARN] AI优化失败，降级为规则优化: {e}")
        return self._optimize_simple(resume_content, jd_content)

    def _optimize_simple(self, resume: str, jd: str) -> Dict[str, Any]:
        jd_keywords = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z+#]{2,20}', jd.lower()))
        resume_keywords = set(re.findall(r'[\u4e00-\u9fa5a-zA-Z+#]{2,20}', resume.lower()))
        matched = jd_keywords & resume_keywords
        match_rate = len(matched) / max(len(jd_keywords), 1) * 100
        missing = jd_keywords - resume_keywords
        original_score = int(min(match_rate * 0.6 + 30, 85))
        suggestions = [f"建议添加: {', '.join(list(missing)[:5])}"] if missing else ["匹配度较高"]
        diff_highlights = [{"section": "技能", "type": "added", "content": kw} for kw in list(missing)[:5]]
        return {"original_score": original_score, "optimized_score": original_score + 10, "optimized_content": resume + "\n\n## 优化建议\n" + "\n".join(suggestions), "change_summary": f"匹配度提升 {len(matched)} 个关键词", "diff_highlights": diff_highlights}

    async def _optimize_with_ai(self, resume: str, jd: str, optimization_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            ai = get_ai_service()
            prompt = f"根据JD优化简历。\nJD: {jd[:1500]}\n简历: {resume[:1500]}\n返回JSON: {{\"original_score\": 60, \"optimized_score\": 85, \"optimized_content\": \"...\", \"change_summary\": \"...\", \"diff_highlights\": []}}"
            response = await ai.chat_simple(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                result.setdefault('original_score', 60)
                result.setdefault('optimized_score', 80)
                result.setdefault('optimized_content', resume)
                result.setdefault('change_summary', 'AI优化完成')
                result.setdefault('diff_highlights', [])
                return result
        except Exception as e:
            print(f"AI优化失败: {e}")
        return self._optimize_simple(resume, jd)
