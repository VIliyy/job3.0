# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - Agent对话服务
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.schemas.agent import ChatMessage
from app.agents.smart_agent import SmartAgent


class AgentService:
    """Agent对话服务"""

    def __init__(self, db: Session):
        self.db = db
        self.smart_agent = SmartAgent(db)

    async def chat(
        self,
        message: str,
        history: List[ChatMessage] = None,
        state: Dict = None
    ) -> Dict[str, Any]:
        """处理用户消息"""
        try:
            result = await self.smart_agent.chat(
                message=message,
                history=[h.dict() if hasattr(h, "dict") else h for h in history] if history else None,
                state=state
            )

            return {
                "response": result.get("response", ""),
                "suggested_actions": result.get("suggested_actions", []),
                "state": result.get("state", {}),
                "context": "smart_agent"
            }
        except Exception as e:
            print(f"Agent 处理失败: {e}")
            return {
                "response": f"抱歉，处理请求时出现错误: {str(e)[:200]}",
                "suggested_actions": ["帮助", "重试"],
                "state": {},
                "context": "error"
            }