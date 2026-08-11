# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - STAR法则简历优化Agent
"""

from typing import Dict, List, Optional, Any
from app.agents.base import ai_service


class STAROptimizerAgent:
    """STAR法则简历优化Agent"""

    def __init__(self):
        self.system_prompt = """你是一个专业的简历优化顾问，擅长使用STAR法则帮助求职者优化简历内容。

STAR法则：
- Situation (情境): 事情是在什么情况下发生的
- Task (任务): 你需要完成什么任务
- Action (行动): 你采取了什么具体的行动
- Result (结果): 取得了什么结果（尽量量化）

你的职责：
1. 将平淡的简历描述转化为STAR格式
2. 量化成果（使用具体数字）
3. 突出个人贡献和影响力
4. 保持简洁专业

请以JSON格式输出优化结果：
{
    "original": "原始描述",
    "optimized": "STAR格式优化后的描述",
    "analysis": {
        "situation": "情境说明",
        "task": "任务说明",
        "action": "行动说明",
        "result": "结果说明（带数字）"
    },
    "tips": ["优化建议1", "优化建议2"]
}"""

    async def optimize(self, resume_text: str, jd_content: Optional[str] = None) -> Dict[str, Any]:
        """优化简历内容"""
        if not ai_service.llm:
            return self._generate_fallback_optimization(resume_text)

        try:
            # 构建提示
            user_prompt = self._build_prompt(resume_text, jd_content)

            # 调用AI
            response = await ai_service.chat([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ])

            # 解析响应
            return self._parse_response(response, resume_text)
        except Exception as e:
            print(f"简历优化失败: {e}")
            return self._generate_fallback_optimization(resume_text)

    async def optimize_batch(self, items: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """批量优化简历项目"""
        results = []
        for item in items:
            result = await self.optimize(item.get("content", ""), item.get("jd_content"))
            results.append({
                "section": item.get("section", ""),
                "title": item.get("title", ""),
                **result
            })
        return results

    def _build_prompt(self, resume_text: str, jd_content: Optional[str]) -> str:
        """构建提示"""
        prompt = "请优化以下简历内容，使用STAR法则重构：\n\n## 简历内容\n"
        prompt += resume_text

        if jd_content:
            prompt += "\n\n## 目标岗位\n"
            prompt += jd_content[:500]

        prompt += "\n\n请逐条优化，每个项目输出：原始描述、STAR优化版本、分析要点。"
        return prompt

    def _parse_response(self, response: str, original: str) -> Dict[str, Any]:
        """解析AI响应"""
        import json
        import re

        try:
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"解析优化响应失败: {e}")

        return self._generate_fallback_optimization(original)

    def _generate_fallback_optimization(self, resume_text: str) -> Dict[str, Any]:
        """生成备用优化（无AI时使用规则）"""

        # 提取每行作为独立项目
        lines = [l.strip() for l in resume_text.split('\n') if l.strip()]

        optimizations = []
        for line in lines:
            if len(line) > 10:  # 过滤太短的
                optimized = self._optimize_line(line)
                optimizations.append({
                    "original": line,
                    "optimized": optimized,
                    "analysis": {
                        "situation": "在项目/工作中",
                        "task": "需要完成相关任务",
                        "action": optimized.split('。')[0] if '。' in optimized else optimized[:50],
                        "result": "取得了积极成果"
                    },
                    "tips": [
                        "添加具体的数字指标",
                        "突出个人贡献",
                        "使用强动词开头"
                    ]
                })

        if not optimizations:
            return {
                "original": resume_text,
                "optimized": resume_text,
                "analysis": {},
                "tips": ["请提供更详细的简历内容"]
            }

        return {
            "original": resume_text,
            "optimized": "\n\n".join([o["optimized"] for o in optimizations]),
            "item_count": len(optimizations),
            "items": optimizations
        }

    def _optimize_line(self, line: str) -> str:
        """使用规则优化单行内容"""

        # 移除常见弱词
        weak_words = ["负责", "参与", "协助", "做了", "进行了", "完成"]
        strong_words = {
            "负责": "主导",
            "参与": "协同完成",
            "协助": "独立承担",
            "做了": "成功实施",
            "进行了": "系统推进",
            "完成": "高效完成"
        }

        result = line
        for weak, strong in strong_words.items():
            result = result.replace(weak, strong)

        # 添加量化占位符
        if any(word in result for word in ["提升了", "改善了", "优化了"]):
            if "XX%" not in result and "xxx%" not in result.lower():
                result = result.replace("了", "了XX%")
        elif any(word in result for word in ["开发了", "构建了", "设计了"]):
            if "系统" in result or "平台" in result or "应用" in result:
                result += "，提升效率30%+"

        return result


class ResumeAnalyzer:
    """简历分析器 - 提取简历模块"""

    def parse_resume(self, text: str) -> Dict[str, List[Dict]]:
        """解析简历结构"""
        sections = {
            "基本信息": [],
            "教育经历": [],
            "工作经历": [],
            "项目经历": [],
            "技能特长": [],
            "其他": []
        }

        current_section = "其他"
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测章节标题
            section_keywords = {
                "基本信息": ["个人信息", "基本信息", "profile"],
                "教育经历": ["教育", "学历", "education"],
                "工作经历": ["工作", "经历", "经验", "employment", "work"],
                "项目经历": ["项目", "project"],
                "技能特长": ["技能", "技术", "skills", "专长"],
            }

            detected = False
            for section, keywords in section_keywords.items():
                if any(kw in line.lower() for kw in keywords):
                    current_section = section
                    detected = True
                    break

            # 分配内容
            if not detected and len(line) > 5:
                entry = {
                    "content": line,
                    "optimized": None
                }
                sections[current_section].append(entry)

        return sections

    def extract_sections_for_optimization(self, text: str) -> List[Dict]:
        """提取需要优化的简历项目"""
        sections = self.parse_resume(text)
        items = []

        # 优先优化工作经历和项目经历
        for section in ["工作经历", "项目经历", "教育经历", "其他"]:
            for entry in sections.get(section, []):
                if len(entry["content"]) > 15:  # 过滤太短的
                    items.append({
                        "section": section,
                        "title": entry["content"][:50],
                        "content": entry["content"]
                    })

        return items
