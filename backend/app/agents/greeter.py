# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 打招呼语生成Agent
"""

from typing import Dict, Any, Optional
from app.agents.base import ai_service

class GreetingGenerator:
    """打招呼语生成Agent"""
    
    async def generate(
        self,
        resume_info: Dict[str, Any],
        jd_info: Dict[str, Any],
        company_info: Optional[Dict[str, Any]] = None,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成打招呼语
        
        Args:
            resume_info: 简历信息
                - name: 姓名
                - experience_summary: 经验摘要
                - skills: 技能列表
                - achievements: 成就列表
            
            jd_info: JD分析结果
                - company: 公司名
                - position: 岗位名
                - core_skills: 核心技能
            
            company_info: 公司安全信息（可选）
            template: 自定义模板（可选）
            
        Returns:
            生成的打招呼语字典
        """
        # 如果有AI服务，使用AI生成
        return await ai_service.generate_greeting(resume_info, jd_info, company_info)
    
    async def generate_with_template(
        self,
        template: str,
        variables: Dict[str, str]
    ) -> str:
        """
        使用模板生成打招呼语
        
        Args:
            template: 模板内容
            variables: 变量字典
            
        Returns:
            填充后的打招呼语
        """
        greeting = template
        for key, value in variables.items():
            greeting = greeting.replace(f"{{{key}}}", value)
        return greeting
    
    def extract_template_variables(self, template: str) -> list:
        """
        提取模板中的变量
        
        Args:
            template: 模板内容
            
        Returns:
            变量列表
        """
        import re
        pattern = r'\{(\w+)\}'
        return re.findall(pattern, template)
    
    def validate_template(self, template: str, variables: Dict[str, str]) -> Dict[str, Any]:
        """
        验证模板是否有效
        
        Args:
            template: 模板内容
            variables: 提供的变量
            
        Returns:
            验证结果
        """
        required_vars = self.extract_template_variables(template)
        missing_vars = [v for v in required_vars if v not in variables]
        
        return {
            "valid": len(missing_vars) == 0,
            "missing_variables": missing_vars,
            "provided_variables": list(variables.keys())
        }
    
    async def optimize_greeting(
        self,
        greeting: str,
        platform: str = "boss"
    ) -> str:
        """
        优化打招呼语（平台适配）
        
        Args:
            greeting: 原打招呼语
            platform: 目标平台 (boss/liepin/email)
            
        Returns:
            优化后的打招呼语
        """
        max_lengths = {
            "boss": 50,
            "liepin": 100,
            "email": 150
        }
        
        max_length = max_lengths.get(platform, 100)
        
        # 如果超过长度限制，简单截断
        if len(greeting) > max_length:
            greeting = greeting[:max_length - 3] + "..."
        
        return greeting
