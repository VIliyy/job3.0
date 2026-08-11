# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 简历-JD匹配分析API
提供详细的匹配度分析和可视化数据
"""

import asyncio
import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.agents.base import ai_service
from app.agents.analyzer import JDAnalyzer

router = APIRouter()

# 实例
jd_analyzer = JDAnalyzer()


# ============================================================================
# 请求/响应模型
# ============================================================================

class MatchAnalysisRequest(BaseModel):
    resume_text: str
    jd_content: str
    use_ai: bool = True


# ============================================================================
# 辅助函数
# ============================================================================

def extract_keywords(text: str) -> set:
    """提取文本中的关键词"""
    skill_patterns = [
        'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++',
        'react', 'vue', 'angular', 'node.js', 'django', 'flask', 'spring',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'linux', 'git',
        'sql', 'mongodb', 'redis', 'elasticsearch', 'kafka',
        'machine learning', 'deep learning', 'tensorflow', 'pytorch',
        'agile', 'scrum', 'devops', 'ci/cd', 'tdd', 'microservices',
        'api', 'rest', 'graphql', 'grpc',
    ]

    keywords = set()
    text_lower = text.lower()

    for pattern in skill_patterns:
        if pattern in text_lower:
            keywords.add(pattern)

    return keywords


def categorize_skills(skills: List[str]) -> Dict[str, Dict[str, Any]]:
    """将技能分类"""
    categories = {
        "编程语言": ["python", "java", "javascript", "typescript", "go", "rust", "c++", "c#"],
        "前端框架": ["react", "vue", "angular", "html", "css"],
        "后端框架": ["node.js", "django", "flask", "spring", "fastapi", "express"],
        "数据库": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch"],
        "云服务": ["aws", "azure", "gcp", "docker", "kubernetes"],
        "AI/ML": ["machine learning", "deep learning", "tensorflow", "pytorch", "ai"],
        "DevOps": ["devops", "ci/cd", "linux", "git", "agile", "scrum"],
    }

    result = {}
    for category, keywords in categories.items():
        matched = [s for s in skills if s.lower() in keywords]
        if matched:
            result[category] = {"skills": matched, "count": len(matched)}

    return result


def get_match_level(score: int) -> tuple:
    """根据分数判断匹配等级"""
    if score >= 85:
        return "高度匹配", "#10b981"
    elif score >= 70:
        return "基本匹配", "#3b82f6"
    elif score >= 50:
        return "勉强匹配", "#f59e0b"
    else:
        return "不匹配", "#ef4444"


def calculate_ats_score(text: str, keywords: List[str]) -> int:
    """计算ATS关键词覆盖率"""
    if not keywords:
        return 0

    text_lower = text.lower()
    matched = sum(1 for kw in keywords if kw.lower() in text_lower)
    return int(matched / len(keywords) * 100)


# ============================================================================
# API 端点
# ============================================================================

@router.post("/analyze")
async def analyze_match(request: MatchAnalysisRequest):
    """
    详细分析简历与JD的匹配度，返回可视化所需的所有数据
    """
    if not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="请提供简历内容")

    if not request.jd_content.strip():
        raise HTTPException(status_code=400, detail="请提供JD内容")

    # 1. 解析JD
    jd_info = await jd_analyzer.analyze(request.jd_content)

    # 2. 提取技能
    jd_skills = extract_keywords(request.jd_content)
    resume_skills = extract_keywords(request.resume_text)

    # JD要求的技能（从分析结果中也提取）
    for skill in jd_info.get("core_skills", []):
        jd_skills.add(skill.lower())
    for skill in jd_info.get("preferred_skills", []):
        jd_skills.add(skill.lower())

    # 3. 计算匹配度
    matched = list(jd_skills & resume_skills)
    missing = list(jd_skills - resume_skills)

    if jd_skills:
        base_score = int(len(matched) / len(jd_skills) * 100)
    else:
        base_score = 50

    # 4. AI深度分析
    suggestions = []
    experience = {"relevance_score": base_score, "highlights": [], "gaps": []}
    ats_data = {"required": list(jd_skills), "recommended": []}

    if request.use_ai and ai_service.llm:
        try:
            prompt = f"""请分析以下简历与职位描述的匹配度：

## 简历内容：
{request.resume_text[:2000]}

## 职位描述：
{request.jd_content[:2000]}

请以JSON格式返回分析结果，包含：
- match_score: 匹配分数（0-100）
- skill_analysis: {{matched_skills: [], missing_skills: []}}
- overall_suggestions: [{{priority: "high/medium/low", suggestion: "..."}}]
- experience_analysis: {{relevance_score: 0-100, highlights: [], gaps: []}}

只返回JSON。"""

            response = await ai_service.chat_simple(prompt)
            ai_result = ai_service._parse_json_response(response)

            if "match_score" in ai_result:
                ai_score = ai_result.get("match_score", base_score)
                final_score = int(ai_score * 0.6 + base_score * 0.4)
            else:
                final_score = base_score

            if "skill_analysis" in ai_result:
                if ai_result["skill_analysis"].get("matched_skills"):
                    matched = ai_result["skill_analysis"]["matched_skills"]
                if ai_result["skill_analysis"].get("missing_skills"):
                    missing = ai_result["skill_analysis"]["missing_skills"]

            suggestions = ai_result.get("overall_suggestions", [])
            experience = ai_result.get("experience_analysis", experience)
            ats_data = ai_result.get("ats_keywords", ats_data)
        except Exception as e:
            final_score = base_score
            suggestions = [{"priority": "medium", "suggestion": "AI分析失败，使用基础分析"}]
    else:
        final_score = base_score
        suggestions = [
            {"priority": "high", "suggestion": f"简历中缺少关键技能：{', '.join(missing[:5])}" if missing else "技能匹配良好"},
            {"priority": "medium", "suggestion": "建议针对JD优化简历关键词"},
            {"priority": "low", "suggestion": "配置AI获取更精准的分析"},
        ]
        experience = {"relevance_score": final_score, "highlights": matched[:3], "gaps": missing[:3]}

    # 5. 构建技能评分列表（用于雷达图）
    all_skills = list(set(matched + missing))
    skills_for_radar = []
    for skill in all_skills:
        skills_for_radar.append({
            "name": skill.title() if len(skill) > 3 else skill.upper(),
            "score": 100 if skill in matched else 0,
            "matched": skill in matched
        })

    # 6. ATS分析
    ats_score = calculate_ats_score(request.resume_text, list(jd_skills))

    # 7. 技能分类
    categorized = categorize_skills(all_skills)

    # 8. 生成报告文本
    match_level, level_color = get_match_level(final_score)
    report_parts = [
        f"# 简历-JD 匹配分析报告",
        f"",
        f"## 总体评分：{final_score}/100（{match_level}）",
        f"",
        f"## JD信息",
        f"- 公司：{jd_info.get('company', '未识别')}",
        f"- 职位：{jd_info.get('position', '未识别')}",
        f"- 薪资：{jd_info.get('salary_range', '未提供')}",
        f"",
        f"## 技能匹配分析",
        f"- 匹配技能（{len(matched)}个）：{', '.join(matched[:10])}{'...' if len(matched) > 10 else ''}",
        f"- 缺失技能（{len(missing)}个）：{', '.join(missing[:10])}{'...' if len(missing) > 10 else ''}",
        f"",
        f"## ATS关键词覆盖率：{ats_score}%",
        f"",
        f"## 优化建议",
    ]
    for i, s in enumerate(suggestions[:5], 1):
        report_parts.append(f"{i}. [{s.get('priority', 'medium').upper()}] {s.get('suggestion', '')}")

    report_text = "\n".join(report_parts)

    # 9. 返回字典而不是 Pydantic 模型
    return {
        "status": "success",
        "data": {
            "overall_score": final_score,
            "match_level": match_level,
            "match_level_color": level_color,
            "jd_info": {
                "company": jd_info.get("company", "未提供"),
                "position": jd_info.get("position", "未提供"),
                "salary_range": jd_info.get("salary_range", "未提供"),
                "core_skills": jd_info.get("core_skills", []),
                "preferred_skills": jd_info.get("preferred_skills", []),
            },
            "skills": skills_for_radar,
            "skill_categories": categorized,
            "ats_score": ats_score,
            "ats_keywords": ats_data,
            "experience_match": experience,
            "suggestions": suggestions,
            "report_text": report_text
        }
    }
