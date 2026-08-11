# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - AI Agent模块

设计思路参考AI-Resume-Agent，但针对求职管理系统优化：
- 打招呼语生成
- JD分析
- 简历匹配
- 求职建议
- LangChain Agent自主搜索
"""

from app.agents.analyzer import JDAnalyzer
from app.agents.matcher import ResumeMatcher
from app.agents.greeter import GreetingGenerator
from app.agents.advisor import CareerAdvisor
from app.agents.langchain_agent import create_agent, SimpleAgent, LangChainAgent
from app.agents.tools import get_all_tools, get_tools_dict

__all__ = [
    # 核心 Agent
    "JDAnalyzer",
    "ResumeMatcher",
    "GreetingGenerator",
    "CareerAdvisor",
    # LangChain Agent
    "create_agent",
    "SimpleAgent",
    "LangChainAgent",
    # 工具集
    "get_all_tools",
    "get_tools_dict",
]
