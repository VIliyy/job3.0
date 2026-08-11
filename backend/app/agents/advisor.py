# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 求职建议Agent
"""

from typing import Dict, Any, Optional

class CareerAdvisor:
    """职业规划建议Agent"""
    
    async def advise(
        self,
        user_profile: Dict[str, Any],
        resume_summary: str,
        market_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        提供求职建议
        
        Args:
            user_profile: 用户画像
                - stage: 当前阶段（应届生/社招/转行/实习生）
                - years_experience: 工作年限
                - current_position: 当前职位
                - target_position: 目标职位
                - target_city: 目标城市
                - salary_expectation: 薪资期望
                - education: 学历
                
            resume_summary: 简历摘要
            market_info: 市场行情（可选）
            
        Returns:
            求职建议
        """
        # 简化实现，直接返回建议
        return self._rule_based_advice(user_profile, resume_summary)
    
    def _rule_based_advice(
        self,
        user_profile: Dict[str, Any],
        resume_summary: str
    ) -> Dict[str, Any]:
        """基于规则的求职建议（无AI时）"""
        stage = user_profile.get("stage", "社招")
        target_position = user_profile.get("target_position", "")
        target_city = user_profile.get("target_city", "一线城市")
        
        # 通用策略
        strategy_map = {
            "应届生": "聚焦于学习机会和成长空间，不要过度关注薪资",
            "社招": "突出项目经验和实际成果，强调性价比",
            "转行": "强调可迁移技能，展示学习能力和热情",
            "实习生": "突出潜力和学习态度，表达长期发展意愿"
        }
        
        # 平台策略
        platform_strategy = {
            "boss": "BOSS直聘适合快速响应，建议每天刷新+主动沟通",
            "liepin": "猎聘适合中高端职位，完善简历+猎头推荐",
            "lagou": "拉勾适合互联网公司，关注公司动态+内推"
        }
        
        return {
            "overall_strategy": strategy_map.get(stage, "针对性投递"),
            "target_companies": {
                "type_a": [f"目标城市{target_city}的知名企业"],
                "type_b": ["快速成长的创业公司"],
                "avoid": ["负面新闻多的公司"]
            },
            "salary_guide": {
                "market_range": "待AI分析获取详细数据",
                "expectation_advice": "建议在市场水平的70-90%区间",
                "negotiation_tips": ["先了解公司薪资结构", "突出综合能力"]
            },
            "skill_priority": [
                {"skill": "待分析", "reason": "请配置AI服务获取个性化建议"}
            ],
            "action_plan": [
                {"week": "第1周", "actions": ["完善简历", "投递10家目标公司", "准备面试问题"]},
                {"week": "第2周", "actions": ["跟进投递状态", "复盘面试经验", "调整求职策略"]}
            ],
            "platform_strategy": platform_strategy,
            "interview_prep": {
                "common_questions": ["自我介绍", "项目经验", "离职原因", "职业规划"],
                "technical_focus": [f"{target_position}相关技术"],
                "behavioral_focus": ["团队协作", "解决问题能力"]
            },
            "risks": [
                {"risk": "海投导致精力分散", "mitigation": "聚焦目标岗位"},
                {"risk": "面试紧张影响发挥", "mitigation": "多模拟练习"}
            ]
        }
    
    def estimate_salary(
        self,
        position: str,
        city: str,
        experience_years: int
    ) -> Dict[str, Any]:
        """
        估算薪资范围
        
        Args:
            position: 职位
            city: 城市
            experience_years: 工作年限
            
        Returns:
            薪资估算结果
        """
        # 简化实现：基础薪资表
        base_salary = {
            "一线城市": {
                "1-3年": (15, 25),
                "3-5年": (25, 40),
                "5年以上": (40, 60)
            },
            "二线城市": {
                "1-3年": (10, 18),
                "3-5年": (18, 30),
                "5年以上": (30, 45)
            }
        }
        
        # 根据年限确定区间
        if experience_years <= 3:
            years_key = "1-3年"
        elif experience_years <= 5:
            years_key = "3-5年"
        else:
            years_key = "5年以上"
        
        city_type = "一线城市" if city in ["北京", "上海", "深圳", "广州", "杭州", "成都"] else "二线城市"
        
        salary_range = base_salary.get(city_type, {}).get(years_key, (10, 20))
        
        return {
            "salary_range": f"{salary_range[0]}k-{salary_range[1]}k",
            "median": f"{(salary_range[0] + salary_range[1]) / 2}k",
            "factors": ["城市", "经验", "技术栈", "公司规模"]
        }
