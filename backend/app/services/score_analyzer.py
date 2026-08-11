# -*- coding: utf-8 -*-
# 增强评分分析 API

import re

def analyze_resume_score(resume_content: str, jd_content: str) -> dict:
    """
    深度分析简历评分（结构、关键词、成果量化、格式、ATS友好度）
    返回详细的评分数据和优化建议
    """
    if not resume_content:
        return {
            "scores": [0, 0, 0, 0, 0],
            "labels": ["结构完整性", "关键词覆盖", "成果量化", "格式规范", "ATS友好度"],
            "matched_keywords": [],
            "missing_keywords": [],
            "suggestions": []
        }
    
    content = resume_content.lower()
    jd_lower = jd_content.lower()
    
    # 1. 结构完整性评分（20分）
    structure_score = _score_structure(resume_content)
    
    # 2. 关键词覆盖率评分（20分）
    keywords = _extract_keywords(jd_content)
    matched, missing = _match_keywords(resume_content, keywords)
    keyword_score = _score_keyword_coverage(matched, keywords)
    
    # 3. 成果量化评分（20分）
    quantify_score = _score_quantification(resume_content)
    
    # 4. 格式规范评分（20分）
    format_score = _score_format(resume_content)
    
    # 5. ATS友好度评分（20分）
    ats_score = _score_ats_friendly(resume_content)
    
    total = structure_score + keyword_score + quantify_score + format_score + ats_score
    
    # 生成优化建议
    suggestions = _generate_suggestions(
        structure_score, keyword_score, quantify_score, format_score, ats_score,
        matched, missing
    )
    
    return {
        "scores": [
            round(structure_score * 5),   # 转换为0-100
            round(keyword_score * 5),
            round(quantify_score * 5),
            round(format_score * 5),
            round(ats_score * 5)
        ],
        "total_score": round(total * 5),
        "labels": ["结构完整性", "关键词覆盖", "成果量化", "格式规范", "ATS友好度"],
        "matched_keywords": matched[:15],
        "missing_keywords": missing[:15],
        "suggestions": suggestions[:5]
    }


def _score_structure(content: str) -> float:
    """结构完整性：检查必要模块是否存在"""
    score = 0.0
    modules = {
        "个人信息": ["姓名", "联系方式", "电话", "邮箱", "email", "phone"],
        "教育背景": ["教育", "学历", "学校", " university", "college", "education"],
        "工作经历": ["工作", "经历", "经验", "职位", "工作经历", "experience", "job"],
        "项目经验": ["项目", "project"],
        "技能证书": ["技能", "证书", "skill", "certificate"],
    }
    
    for module, keywords in modules.items():
        if any(kw in content.lower() for kw in keywords):
            score += 1.0
    
    return min(score / len(modules) * 4, 4.0)  # 满分4分，转换为20分制


def _extract_keywords(text: str) -> set:
    """提取JD关键词"""
    # 提取2-20字符的中文或英文词组
    chinese = re.findall(r'[\u4e00-\u9fa5]{2,20}', text)
    english = re.findall(r'[a-zA-Z]{3,20}', text)
    # 过滤常见无意义词
    stop_words = {'有限公司', '公司', '职位', '岗位', '负责', '要求', '任职', '能力', '经验'}
    keywords = set()
    for kw in chinese:
        if kw not in stop_words and len(kw) >= 2:
            keywords.add(kw)
    for kw in english:
        if kw.lower() not in {'and', 'the', 'for', 'with', 'you', 'will', 'need', 'must', 'should', 'could'}:
            keywords.add(kw.lower())
    return keywords


def _match_keywords(resume: str, jd_keywords: set) -> tuple:
    """匹配关键词"""
    resume_keywords = _extract_keywords(resume)
    matched = list(jd_keywords & resume_keywords)
    missing = list(jd_keywords - resume_keywords)
    return matched, missing


def _score_keyword_coverage(matched: list, all_keywords: set) -> float:
    """关键词覆盖率评分"""
    if not all_keywords:
        return 4.0
    coverage = len(matched) / len(all_keywords)
    return min(coverage * 4, 4.0)


def _score_quantification(content: str) -> float:
    """成果量化评分：检查是否使用数字、百分比"""
    # 数字模式：百分比、带单位的数字、范围
    patterns = [
        r'\d+%',           # 百分比
        r'\d+万',          # 薪资
        r'\d+人',          # 团队规模
        r'\d+个',          # 项目数量
        r'\d+万\+?',       # 业绩
        r'\d+/\d+',        # 分数
        r'\d+x',           # 倍数
        r'\d+\.\d+',       # 小数
    ]
    
    score = 0.0
    content_lower = content.lower()
    
    # 检查数字使用
    has_numbers = any(re.search(p, content_lower) for p in patterns)
    if has_numbers:
        score += 1.5
    
    # 检查是否有明确的成果描述
    achievement_keywords = ['提升', '增长', '减少', '提高', '优化', '完成', '达成', '增加', 'improve', 'increase', 'achieve', 'complete', 'reduce']
    if any(kw in content_lower for kw in achievement_keywords):
        score += 1.0
    
    # 检查动词使用（主动语态）
    action_keywords = ['主导', '负责', '推动', '实现', '完成', '领导', 'lead', 'drive', 'achieve', 'deliver']
    if any(kw in content_lower for kw in action_keywords):
        score += 1.5
    
    return min(score, 4.0)


def _score_format(content: str) -> float:
    """格式规范评分"""
    score = 0.0
    
    # 检查是否有清晰的段落分隔
    lines = content.split('\n')
    if len(lines) > 5:
        score += 1.0
    
    # 检查是否使用列表格式
    if any(marker in content for marker in ['•', '-', '*', '·', '1.', '2.', '3.']):
        score += 1.5
    
    # 检查长度适中（500-3000字）
    char_count = len(content)
    if 500 <= char_count <= 3000:
        score += 1.5
    elif 300 <= char_count <= 5000:
        score += 0.75
    
    return min(score, 4.0)


def _score_ats_friendly(content: str) -> float:
    """ATS友好度评分"""
    score = 0.0
    content_lower = content.lower()
    
    # 检查是否包含常见ATS关键词
    good_keywords = ['技能', '经验', '项目', '业绩', '成就', 'skill', 'experience', 'project', 'achievement']
    if any(kw in content_lower for kw in good_keywords):
        score += 1.0
    
    # 检查是否有联系方式
    contact_keywords = ['@', 'phone', 'tel', '邮箱', 'email']
    if any(kw in content_lower for kw in contact_keywords):
        score += 1.0
    
    # 避免使用表格、图片（纯文本友好）
    if '┌' not in content and '│' not in content and '━' not in content:
        score += 1.0
    
    # 检查是否使用标准标题
    standard_titles = ['工作经历', '教育背景', '项目经验', '技能', '个人总结', 'experience', 'education', 'skills', 'summary']
    if any(title in content_lower for title in standard_titles):
        score += 1.0
    
    return min(score, 4.0)


def _generate_suggestions(s_structure, s_keyword, s_quantify, s_format, s_ats, matched, missing) -> list:
    """生成优化建议"""
    suggestions = []
    
    if s_structure < 3:
        suggestions.append({
            "priority": "high",
            "text": "简历结构不完整，建议补充个人信息、教育背景、工作经历等必要模块"
        })
    
    if s_keyword < 3 and missing:
        top_missing = missing[:5]
        suggestions.append({
            "priority": "high",
            "text": f"建议在简历中加入以下关键词：{', '.join(top_missing)}"
        })
    
    if s_quantify < 2:
        suggestions.append({
            "priority": "high",
            "text": "建议为工作成果添加具体数字，如：提升效率30%、管理10人团队"
        })
    
    if s_format < 3:
        suggestions.append({
            "priority": "medium",
            "text": "建议使用清晰的列表格式分隔内容，避免大段文字"
        })
    
    if s_ats < 3:
        suggestions.append({
            "priority": "medium",
            "text": "建议使用标准职位标题，避免使用特殊字符和表格"
        })
    
    if not suggestions:
        suggestions.append({
            "priority": "low",
            "text": "简历整体质量良好，可以针对具体JD做进一步优化"
        })
    
    return suggestions
