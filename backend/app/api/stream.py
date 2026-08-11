# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - Agent流式对话API

支持 SSE 流式输出，展示 Agent 思考过程
"""

import json
import asyncio
import re
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.agents.base import ai_service

router = APIRouter()


class StreamChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict]] = Field(default_factory=list)
    state: Optional[Dict[str, Any]] = None
    stream_thinking: bool = True  # 是否流式输出思考过程


class StreamEvent:
    """SSE 事件类型"""
    THINKING = "thinking"      # 思考中
    AGENT_START = "agent_start"    # Agent 开始
    AGENT_END = "agent_end"        # Agent 结束
    CONTENT = "content"        # 内容片段
    ACTION = "action"          # 建议操作
    STATE = "state"            # 状态更新
    ERROR = "error"           # 错误
    DONE = "done"             # 完成


class AgentStreamService:
    """Agent 流式服务"""

    # 思考过程模板
    THINKING_TEMPLATES = {
        "analyzing": ["正在分析你的问题...", "正在理解你的意图...", "让我思考一下..."],
        "searching": ["正在搜索相关信息...", "查找简历数据...", "检索投递记录..."],
        "generating": ["正在生成回复...", "正在组织语言...", "整理答案中..."],
        "optimizing": ["正在分析简历...", "正在匹配JD...", "计算优化建议..."],
    }

    @staticmethod
    def _load_resume_text(db: Session) -> Optional[str]:
        """从数据库加载最新简历内容，作为助手知识"""
        try:
            from app.models.resume import Resume
            resume = (
                db.query(Resume)
                .filter(Resume.content.isnot(None), Resume.content != "")
                .order_by(Resume.updated_at.desc())
                .first()
            )
            if resume and resume.content and resume.content.strip():
                return resume.content
        except Exception as e:
            print(f"[stream] 加载简历失败: {e}")
        return None

    @classmethod
    async def stream_chat(
        cls,
        message: str,
        history: List[Dict] = None,
        state: Dict = None,
        stream_thinking: bool = True,
        db: Session = None
    ) -> AsyncGenerator[str, None]:
        """流式处理对话"""

        try:
            # 0. 注入简历知识（优先前端传入，其次数据库最新简历）
            state = dict(state or {})
            resume_text = state.get("resume_text")
            if not resume_text and db is not None:
                resume_text = cls._load_resume_text(db)
            if resume_text:
                state["resume_text"] = resume_text
                state["has_resume"] = True

            # 1. 意图识别阶段
            if stream_thinking:
                yield cls._event(StreamEvent.THINKING, {
                    "phase": "intent",
                    "text": "正在识别你的意图..."
                })
                await asyncio.sleep(0.3)

            intent = cls._analyze_intent(message)

            # 2. 根据意图执行不同流程
            if intent == "match":
                async for event in cls._stream_match(message, state):
                    yield event
            elif intent == "optimize":
                async for event in cls._stream_optimize(message, state):
                    yield event
            elif intent == "greeting":
                async for event in cls._stream_greeting(message, state):
                    yield event
            elif intent == "analyze_jd":
                async for event in cls._stream_jd_analysis(message, state):
                    yield event
            else:
                async for event in cls._stream_general(message, history, state):
                    yield event

        except Exception as e:
            yield cls._event(StreamEvent.ERROR, {"message": str(e)})
        finally:
            yield cls._event(StreamEvent.DONE, {})

    @classmethod
    def _event(cls, event_type: str, data: Dict) -> str:
        """生成 SSE 事件"""
        return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    @classmethod
    def _analyze_intent(cls, message: str) -> str:
        """分析意图"""
        msg = message.lower()
        if any(kw in msg for kw in ["匹配", "匹配度", "对比", "符不符合"]):
            return "match"
        if any(kw in msg for kw in ["优化", "优化简历"]):
            return "optimize"
        if any(kw in msg for kw in ["打招呼", "开场白"]):
            return "greeting"
        if any(kw in msg for kw in ["分析jd", "jd分析", "职位分析"]):
            return "analyze_jd"
        return "general"

    @classmethod
    async def _stream_match(cls, message: str, state: Dict) -> AsyncGenerator[str, None]:
        """流式匹配分析"""
        # 阶段1: 解析简历
        yield cls._event(StreamEvent.THINKING, {
            "phase": "parse_resume",
            "text": "正在解析简历内容...",
            "progress": 20
        })
        await asyncio.sleep(0.5)

        # 阶段2: 解析 JD
        yield cls._event(StreamEvent.THINKING, {
            "phase": "parse_jd",
            "text": "正在分析职位描述...",
            "progress": 40
        })
        await asyncio.sleep(0.5)

        # 阶段3: 提取关键词
        yield cls._event(StreamEvent.THINKING, {
            "phase": "extract_skills",
            "text": "正在提取关键技能要求...",
            "progress": 60
        })
        await asyncio.sleep(0.5)

        # 阶段4: 计算匹配度
        yield cls._event(StreamEvent.THINKING, {
            "phase": "calculate",
            "text": "正在计算匹配度分数...",
            "progress": 80
        })
        await asyncio.sleep(0.3)

        yield cls._event(StreamEvent.THINKING, {
            "phase": "generate",
            "text": "AI 正在计算匹配度并给出建议...",
            "progress": 80
        })
        await asyncio.sleep(0.3)

        # 基于简历 + JD 的真实 AI 分析
        resume_text = (state or {}).get("resume_text", "")
        prompt = f"""你是 Job3.0 求职助手，负责简历与 JD 的匹配度分析。

用户消息：{message}
用户简历：
{resume_text[:2000] if resume_text else '（用户暂未上传简历，请引导其上传）'}

请输出：
1. 综合匹配度评分（0-100）
2. 技能匹配清单（✅ 匹配 / ⚠️ 部分匹配 / ❌ 缺失）
3. 3 条最具体的优化建议（结合简历实际内容）

用 Markdown 友好排版。"""

        if ai_service.llm:
            try:
                response = await ai_service.chat_simple(prompt)
            except Exception as e:
                response = f"抱歉，匹配分析时遇到错误：{str(e)[:100]}"
        else:
            response = "（AI 未配置，暂时无法做深度匹配分析，请先到设置页配置 AI 服务）"

        for char in response:
            yield cls._event(StreamEvent.CONTENT, {"char": char})
            await asyncio.sleep(0.008)

        # 建议操作
        yield cls._event(StreamEvent.ACTION, {
            "actions": ["生成打招呼语", "优化简历", "查看投递记录"]
        })

    @classmethod
    async def _stream_optimize(cls, message: str, state: Dict) -> AsyncGenerator[str, None]:
        """流式简历优化"""
        yield cls._event(StreamEvent.THINKING, {
            "phase": "analyze_current",
            "text": "正在分析当前简历...",
            "progress": 25
        })
        await asyncio.sleep(0.5)

        yield cls._event(StreamEvent.THINKING, {
            "phase": "analyze_jd",
            "text": "正在理解目标职位要求...",
            "progress": 50
        })
        await asyncio.sleep(0.5)

        yield cls._event(StreamEvent.THINKING, {
            "phase": "optimize",
            "text": "正在优化简历内容...",
            "progress": 75
        })
        await asyncio.sleep(0.5)

        response = """📝 **简历优化建议**

根据目标职位，我为你提供以下优化方向：

**1. 技能描述优化**
原文：熟悉 Python 开发
优化：精通 Python Web 开发，熟悉 FastAPI、Django 框架

**2. 项目经历优化**
原文：负责后端开发
优化：独立设计并实现 RESTful API，日均处理请求 10 万+

**3. 量化成果**
建议为每个项目添加量化指标，如：
- 性能提升 XX%
- 用户增长 XX
- 代码复用率 XX%

💡 需要我帮你生成优化后的完整简历吗？"""

        for char in response:
            yield cls._event(StreamEvent.CONTENT, {"char": char})
            await asyncio.sleep(0.015)

        yield cls._event(StreamEvent.ACTION, {
            "actions": ["生成优化后简历", "调整优化方向", "保存当前版本"]
        })

    @classmethod
    async def _stream_greeting(cls, message: str, state: Dict) -> AsyncGenerator[str, None]:
        """流式打招呼语生成"""
        yield cls._event(StreamEvent.THINKING, {
            "phase": "extract_info",
            "text": "正在提取公司信息...",
            "progress": 30
        })
        await asyncio.sleep(0.4)

        yield cls._event(StreamEvent.THINKING, {
            "phase": "generate",
            "text": "正在生成打招呼语...",
            "progress": 70
        })
        await asyncio.sleep(0.5)

        # 提取公司名
        company_match = re.search(r'([^\s公司]+)公司', message)
        company = company_match.group(1) if company_match else "贵司"

        response = f"""💬 **打招呼语生成**

**发送给：** {company}

**BOSS直聘版（50字）：**
您好，看到贵司在招后端工程师，我对贵司的产品很感兴趣，希望能详细聊聊。

**猎聘版（100字）：**
您好！我是有着3年开发经验的工程师，看到贵司在招后端岗位。我的技能与该职位匹配度较高，期待能与您进一步沟通。

**邮件版：**
尊敬的HR，您好！
我是通过{company}招聘网站了解到贵司正在招聘后端工程师。我有扎实的Python开发经验，期待加入贵司发展。
"""

        for char in response:
            yield cls._event(StreamEvent.CONTENT, {"char": char})
            await asyncio.sleep(0.012)

        yield cls._event(StreamEvent.ACTION, {
            "actions": ["复制使用", "调整内容", "另存模板"]
        })

    @classmethod
    async def _stream_jd_analysis(cls, message: str, state: Dict) -> AsyncGenerator[str, None]:
        """流式 JD 分析"""
        yield cls._event(StreamEvent.THINKING, {
            "phase": "parse",
            "text": "正在解析JD内容...",
            "progress": 30
        })
        await asyncio.sleep(0.5)

        yield cls._event(StreamEvent.THINKING, {
            "phase": "extract",
            "text": "正在提取关键要求...",
            "progress": 60
        })
        await asyncio.sleep(0.5)

        # 简单分析
        skills = []
        for skill in ["Python", "Java", "Go", "MySQL", "Redis", "Vue", "React"]:
            if skill in message:
                skills.append(skill)

        response = f"""📊 **JD 分析结果**

**核心要求：**
• 学历：{"本科及以上" if "本科" in message else "大专及以上"}
• 经验：{"3-5年" if "3年" in message else "1-3年"}
• 技能：{', '.join(skills) if skills else '详见JD'}

**匹配建议：**
请上传简历，我可以为你做更详细的匹配分析，并生成针对性的优化建议。

💡 下一步可以：
• 上传简历 → 获取详细匹配分析
• 生成打招呼语 → 一键生成开场白
• 记录投递 → 追踪求职进度"""

        for char in response:
            yield cls._event(StreamEvent.CONTENT, {"char": char})
            await asyncio.sleep(0.01)

        yield cls._event(StreamEvent.ACTION, {
            "actions": ["上传简历", "生成打招呼语", "记录投递"]
        })

    @classmethod
    async def _stream_general(cls, message: str, history: List, state: Dict) -> AsyncGenerator[str, None]:
        """通用对话（使用AI）"""
        yield cls._event(StreamEvent.THINKING, {
            "phase": "understand",
            "text": "正在理解你的问题...",
            "progress": 30
        })

        # 构建上下文
        context = []
        if state:
            if state.get("has_resume"):
                context.append("用户已有简历")
            if state.get("resume_text"):
                context.append(f"用户简历内容如下（请基于它回答，引用其中的技能/项目/经历）:\n{state['resume_text'][:2000]}")
            if state.get("target_jd"):
                context.append(f"目标JD: {state['target_jd'][:100]}...")
            if state.get("target_company"):
                context.append(f"目标公司: {state['target_company']}")

        prompt = f"""你是 Job3.0 求职助手。请用友好、专业的语气回答用户问题。

用户消息：{message}
上下文：{chr(10).join(context) if context else "无"}

请简洁回答，直接给出有用信息。"""

        if ai_service.llm:
            yield cls._event(StreamEvent.THINKING, {
                "phase": "generate",
                "text": "正在生成回复...",
                "progress": 60
            })

            try:
                response = await ai_service.chat_simple(prompt)
                for char in response:
                    yield cls._event(StreamEvent.CONTENT, {"char": char})
                    await asyncio.sleep(0.008)
            except Exception as e:
                response = f"抱歉，处理问题时遇到错误：{str(e)[:100]}"
                for char in response:
                    yield cls._event(StreamEvent.CONTENT, {"char": char})
        else:
            # 无AI时的回复
            response = """我理解你的问题。作为求职助手，我可以帮你：

📄 **简历管理**
• 上传和解析简历
• 根据JD优化简历

🔍 **JD分析**
• 分析职位要求
• 计算匹配度

💬 **打招呼语**
• 生成各平台打招呼语

📮 **投递追踪**
• 记录投递进度
• 避免重复投递

请告诉我你想做什么？"""
            for char in response:
                yield cls._event(StreamEvent.CONTENT, {"char": char})
                await asyncio.sleep(0.01)

        yield cls._event(StreamEvent.ACTION, {
            "actions": ["帮助", "分析简历", "生成打招呼语"]
        })


@router.post("/stream")
async def stream_chat(request: StreamChatRequest, db: Session = Depends(get_db)):
    """
    流式对话接口

    使用 SSE 协议，支持：
    - 思考过程实时展示
    - Agent 状态可视化
    - 内容流式输出
    """
    return StreamingResponse(
        AgentStreamService.stream_chat(
            message=request.message,
            history=request.history,
            state=request.state,
            stream_thinking=request.stream_thinking,
            db=db
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/thinking-types")
async def get_thinking_types():
    """获取支持的思考过程类型"""
    return {
        "types": list(AgentStreamService.THINKING_TEMPLATES.keys()),
        "templates": AgentStreamService.THINKING_TEMPLATES
    }
