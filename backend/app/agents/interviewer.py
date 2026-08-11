# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 面试题生成Agent
"""

from typing import Dict, List, Optional, Any
from app.agents.base import ai_service
from app.core.config import settings


class InterviewerAgent:
    """面试题生成Agent"""

    def __init__(self):
        self.system_prompt = """你是一个专业的面试官助手，帮助求职者准备面试。

你的职责：
1. 根据JD和简历生成针对性的技术面试题
2. 生成常见的行为面试题（STAR法则类型）
3. 提供面试技巧和注意事项

请以JSON格式输出面试题，格式如下：
{
    "technical_questions": [
        {
            "topic": "主题",
            "questions": ["问题1", "问题2", "问题3"]
        }
    ],
    "behavior_questions": [
        {
            "category": "类别",
            "questions": ["问题1", "问题2"]
        }
    ],
    "tips": ["技巧1", "技巧2"]
}"""

    async def generate(
        self,
        jd_content: str,
        resume_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成面试题"""
        if not ai_service.llm:
            return self._generate_fallback_questions(jd_content)

        try:
            # 构建用户提示
            user_prompt = self._build_prompt(jd_content, resume_text)

            # 调用AI
            response = await ai_service.chat([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ])

            # 解析响应
            return self._parse_response(response)
        except Exception as e:
            print(f"面试题生成失败: {e}")
            return self._generate_fallback_questions(jd_content)

    def _build_prompt(self, jd_content: str, resume_text: Optional[str]) -> str:
        """构建提示"""
        prompt = "请根据以下岗位描述生成面试题：\n\n## 岗位描述\n"
        prompt += jd_content

        if resume_text:
            prompt += "\n\n## 简历摘要\n"
            prompt += resume_text[:1000]  # 限制长度

        prompt += "\n\n请生成针对性的面试题，包括技术题和行为题。"
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            import json
            import re

            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"解析面试题响应失败: {e}")

        return self._generate_fallback_questions("")

    def _generate_fallback_questions(self, jd_content: str) -> Dict[str, Any]:
        """生成备用面试题（无AI时）"""
        # 提取技能关键词
        skills = []
        skill_keywords = ["Python", "Java", "JavaScript", "Go", "Rust", "Vue", "React", "Angular",
                         "MySQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes",
                         "Git", "Linux", "AWS", "API", "REST", "GraphQL", "AI", "ML"]

        jd_upper = jd_content.upper()
        for skill in skill_keywords:
            if skill.upper() in jd_upper:
                skills.append(skill)

        if not skills:
            skills = ["编程基础", "系统设计", "问题解决"]

        # 生成技术题
        technical_questions = []
        for skill in skills[:4]:
            technical_questions.append({
                "topic": skill,
                "questions": [
                    f"请介绍一下你使用{skill}的经验",
                    f"在{skill}项目中遇到的最大挑战是什么？",
                    f"如何优化{skill}相关的代码或系统？"
                ]
            })

        # 生成行为题
        behavior_questions = [
            {
                "category": "STAR法则",
                "questions": [
                    "请描述一个你成功交付重要项目的经历（Situation-Task-Action-Result）",
                    "请分享一次你主动解决团队问题的经历",
                    "描述一个你需要在高压下完成任务的经历"
                ]
            },
            {
                "category": "职业发展",
                "questions": [
                    "为什么想加入我们公司？",
                    "你对这个岗位的理解是什么？",
                    "未来3年你的职业规划是什么？"
                ]
            },
            {
                "category": "团队协作",
                "questions": [
                    "如何与意见不合的同事合作？",
                    "你通常如何给团队成员提供反馈？",
                    "请描述一次你帮助新人融入团队的经历"
                ]
            }
        ]

        # 生成技巧
        tips = [
            "技术问题：先思考10秒，梳理思路后再回答",
            "STAR法则：用具体数字量化成果（提升30%、节省2小时等）",
            "反问环节：准备2-3个有深度的问题展示思考",
            "紧张时：深呼吸，语速放慢，给自己思考时间"
        ]

        return {
            "technical_questions": technical_questions,
            "behavior_questions": behavior_questions,
            "tips": tips
        }
