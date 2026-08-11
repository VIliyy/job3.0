# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - JD分析Agent
"""

from typing import Dict, Any
from app.agents.base import ai_service

class JDAnalyzer:
    """JD分析Agent"""
    
    async def analyze(self, jd_text: str) -> Dict[str, Any]:
        """
        分析JD文本，提取关键信息
        
        Args:
            jd_text: JD文本内容
            
        Returns:
            分析结果字典
        """
        return await ai_service.analyze_jd(jd_text)
    
    def quick_extract(self, jd_text: str) -> Dict[str, Any]:
        """
        快速提取JD基本信息（无需AI）
        
        Args:
            jd_text: JD文本内容
            
        Returns:
            简化版分析结果
        """
        import re
        
        # 提取公司名
        company_patterns = [
            r'【\s*公司\s*】\s*([^\n，,。]+)',
            r'公司[：:]\s*([^\n，,。]+)',
            r'([^\n，,。]*?公司)',
        ]
        company = None
        for pattern in company_patterns:
            match = re.search(pattern, jd_text)
            if match:
                company = match.group(1).strip()
                break
        
        # 提取职位
        position_patterns = [
            r'【\s*(岗位|职位)\s*】\s*([^\n，,。]+)',
            r'职位[：:]\s*([^\n，,。]+)',
            r'岗位[：:]\s*([^\n，,。]+)',
            r'([^\n，,。]*?工程师[^\n，,。]*?)',
        ]
        position = None
        for pattern in position_patterns:
            match = re.search(pattern, jd_text)
            if match:
                position = match.group(1).strip()
                break
        
        # 提取薪资
        salary_patterns = [
            r'([\d]+k?-[\d]+k)',
            r'([\d]+K-[\d]+K)',
            r'([\d]+-[\d]+[kK])',
        ]
        salary = None
        for pattern in salary_patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                salary = match.group(1).upper()
                break
        
        # 提取技能关键词
        tech_keywords = [
            "Python", "Java", "JavaScript", "Go", "Rust", "C++", "C#",
            "Vue", "React", "Angular", "Node.js", "Django", "Flask", "Spring",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "Git", "Linux", "TCP/IP", "HTTP", "REST", "GraphQL",
        ]
        skills = [kw for kw in tech_keywords if kw.lower() in jd_text.lower()]
        
        # 过滤占位符/无意义值（如 "未知"、"【岗位】xxx"），解析不到时返回 None
        def _clean_value(value):
            if not value:
                return None
            value = re.sub(r'^【[^】]*】?', '', value).strip(' :：,，。').strip()
            if not value:
                return None
            if re.fullmatch(r'(未知|待定|暂无|无|未填写|岗位|职位|n/?a)', value, re.IGNORECASE):
                return None
            return value

        company = _clean_value(company)
        position = _clean_value(position)

        return {
            "company": company,
            "position": position,
            "salary_range": salary or "面议",
            "core_skills": skills,
            "preferred_skills": [],
            "experience_requirement": "未知",
            "education_requirement": "未知",
            "jd_quality": "待AI分析" if skills else "低",
        }
