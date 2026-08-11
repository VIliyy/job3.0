# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 简历匹配Agent
"""

from typing import Dict, Any
from app.agents.base import ai_service

class ResumeMatcher:
    """简历匹配Agent"""
    
    async def match(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        分析简历与JD的匹配度
        
        Args:
            resume_text: 简历文本
            jd_text: JD文本
            
        Returns:
            匹配分析结果
        """
        return await ai_service.match_resume_jd(resume_text, jd_text)
    
    async def quick_match(self, resume_text: str, jd_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        快速匹配（基于提取的信息，无需AI）
        
        Args:
            resume_text: 简历文本
            jd_info: JD分析结果
            
        Returns:
            简化版匹配结果
        """
        import re
        
        resume_lower = resume_text.lower()
        
        # 技能匹配
        core_skills = jd_info.get("core_skills", [])
        matched_skills = [s for s in core_skills if s.lower() in resume_lower]
        missing_skills = [s for s in core_skills if s.lower() not in resume_lower]
        
        # 计算匹配分数
        if core_skills:
            score = int(len(matched_skills) / len(core_skills) * 100)
        else:
            score = 0
        
        return {
            "match_score": score,
            "match_level": self._get_match_level(score),
            "skill_analysis": {
                "matched_skills": matched_skills,
                "partial_skills": [],
                "missing_skills": missing_skills
            },
            "experience_analysis": {
                "relevance_score": score,
                "highlights": [],
                "gaps": "建议对比JD要求详细分析"
            },
            "overall_suggestions": self._generate_suggestions(matched_skills, missing_skills),
            "ats_optimization": {
                "missing_keywords": missing_skills,
                "suggestions": [f"在简历中加入{', '.join(missing_skills[:3])}相关描述"]
            }
        }
    
    def _get_match_level(self, score: int) -> str:
        """根据分数判断匹配等级"""
        if score >= 90:
            return "高度匹配"
        elif score >= 70:
            return "基本匹配"
        elif score >= 50:
            return "勉强匹配"
        else:
            return "不匹配"
    
    def _generate_suggestions(self, matched: list, missing: list) -> list:
        """生成优化建议"""
        suggestions = []
        
        if missing:
            suggestions.append({
                "priority": "high",
                "suggestion": f"简历中缺少以下关键词：{', '.join(missing[:3])}，建议补充"
            })
        
        if matched:
            suggestions.append({
                "priority": "medium",
                "suggestion": f"已匹配的技能：{', '.join(matched[:5])}，在简历中突出展示"
            })
        
        suggestions.append({
            "priority": "low",
            "suggestion": "建议使用AI深度分析以获得更精准的优化建议"
        })
        
        return suggestions
