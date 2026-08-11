# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - AI能力API（SSE流式输出）
"""

import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, AsyncGenerator

from app.core.database import get_db
from app.agents.analyzer import JDAnalyzer
from app.agents.matcher import ResumeMatcher
from app.agents.greeter import GreetingGenerator
from app.agents.advisor import CareerAdvisor
from app.agents.interviewer import InterviewerAgent
from app.agents.star_optimizer import STAROptimizerAgent, ResumeAnalyzer
from app.agents.base import ai_service

router = APIRouter()

# Agent实例
jd_analyzer = JDAnalyzer()
resume_matcher = ResumeMatcher()
greeting_generator = GreetingGenerator()
career_advisor = CareerAdvisor()
interviewer = InterviewerAgent()
star_optimizer = STAROptimizerAgent()
resume_analyzer = ResumeAnalyzer()

# ============================================================================
# SSE 流式输出辅助函数
# ============================================================================

async def sse_generator(events: AsyncGenerator[Dict, None]) -> AsyncGenerator[str, None]:
    """将事件转换为 SSE 格式"""
    async for event in events:
        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.01)  # 避免发送过快

def create_event(event_type: str, data: Any, done: bool = False) -> Dict:
    """创建 SSE 事件"""
    return {
        "type": event_type,
        "data": data,
        "done": done
    }

# ============================================================================
# JD分析API
# ============================================================================

class JDParseRequest(BaseModel):
    content: str
    url: Optional[str] = None

@router.post("/jd/analyze")
async def analyze_jd(request: JDParseRequest):
    """分析JD文本，提取关键信息"""
    result = await jd_analyzer.analyze(request.content)
    return {
        "status": "success",
        "data": result
    }

@router.post("/jd/quick-analyze")
async def quick_analyze_jd(request: JDParseRequest):
    """快速分析JD（无需AI）"""
    result = jd_analyzer.quick_extract(request.content)
    return {
        "status": "success",
        "data": result,
        "type": "quick"
    }

# ============================================================================
# JD深度分析（SSE流式）
# ============================================================================

@router.post("/jd/stream-analyze")
async def stream_analyze_jd(request: JDParseRequest):
    """流式分析JD，实时返回进度"""

    async def event_generator():
        try:
            # 1. 开始解析
            yield create_event("status", "正在解析JD内容...")
            await asyncio.sleep(0.3)

            # 2. 提取基本信息
            yield create_event("status", "提取基本信息...")
            basic_info = jd_analyzer.quick_extract(request.content)
            yield create_event("basic_info", basic_info)
            await asyncio.sleep(0.2)

            # 3. AI深度分析（如果有API Key）
            if ai_service.llm:
                yield create_event("status", "AI深度分析中...")
                try:
                    ai_result = await jd_analyzer.analyze(request.content)
                    yield create_event("ai_analysis", ai_result)
                except Exception as e:
                    yield create_event("error", f"AI分析失败: {str(e)}")
            else:
                yield create_event("status", "使用规则解析（未配置AI）")
                yield create_event("ai_analysis", basic_info)

            # 4. 完成
            yield create_event("status", "分析完成")
            yield create_event("done", True, done=True)

        except Exception as e:
            yield create_event("error", str(e))
            yield create_event("done", True, done=True)

    return StreamingResponse(
        sse_generator(event_generator()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================================
# 简历匹配API
# ============================================================================

class ResumeMatchRequest(BaseModel):
    resume_text: str
    jd_content: str
    use_ai: bool = True

@router.post("/resume/match")
async def match_resume_jd(request: ResumeMatchRequest):
    """分析简历与JD的匹配度"""
    if request.use_ai:
        result = await resume_matcher.match(request.resume_text, request.jd_content)
    else:
        # 快速匹配（无需AI）
        jd_info = jd_analyzer.quick_extract(request.jd_content)
        result = await resume_matcher.quick_match(request.resume_text, jd_info)

    return {
        "status": "success",
        "data": result
    }

# ============================================================================
# 简历匹配（SSE流式）
# ============================================================================

class StreamMatchRequest(BaseModel):
    resume_text: str
    jd_content: str

@router.post("/resume/stream-match")
async def stream_match_resume(request: StreamMatchRequest):
    """流式分析简历与JD匹配度"""

    async def event_generator():
        try:
            # 1. 解析简历
            yield create_event("status", "解析简历内容...")
            await asyncio.sleep(0.3)

            # 2. 解析JD
            yield create_event("status", "分析目标岗位...")
            jd_info = jd_analyzer.quick_extract(request.jd_content)
            yield create_event("jd_info", jd_info)
            await asyncio.sleep(0.2)

            # 3. 技能匹配
            yield create_event("status", "分析技能匹配度...")
            await asyncio.sleep(0.4)

            # 4. 计算总分
            yield create_event("status", "计算匹配分数...")
            await asyncio.sleep(0.3)

            # 5. 生成建议
            if ai_service.llm:
                yield create_event("status", "AI生成优化建议...")
                try:
                    match_result = await resume_matcher.match(request.resume_text, request.jd_content)
                    yield create_event("match_result", match_result)
                except Exception as e:
                    yield create_event("error", f"匹配分析失败: {str(e)}")
            else:
                match_result = await resume_matcher.quick_match(request.resume_text, jd_info)
                yield create_event("match_result", match_result)

            yield create_event("status", "匹配分析完成")
            yield create_event("done", True, done=True)

        except Exception as e:
            yield create_event("error", str(e))
            yield create_event("done", True, done=True)

    return StreamingResponse(
        sse_generator(event_generator()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================================
# 打招呼语生成API
# ============================================================================

class GreetingRequest(BaseModel):
    resume_id: Optional[int] = None
    resume_text: Optional[str] = None
    resume_info: Optional[Dict[str, Any]] = None
    jd_content: str
    template_id: Optional[int] = None
    company_info: Optional[Dict[str, Any]] = None

@router.post("/greeting/generate")
async def generate_greeting(request: GreetingRequest):
    """生成打招呼语"""
    # 获取简历信息
    if request.resume_info:
        resume_info = request.resume_info
    elif request.resume_text:
        # 从简历文本中提取基本信息（简化版）
        resume_info = {
            "name": "候选人",
            "experience_summary": "有相关工作经验",
            "skills": [],
            "achievements": []
        }
    else:
        raise HTTPException(status_code=400, detail="请提供简历信息或简历文本")

    # 分析JD
    jd_info = await jd_analyzer.analyze(request.jd_content)

    # 生成打招呼语
    greeting = await greeting_generator.generate(
        resume_info=resume_info,
        jd_info=jd_info,
        company_info=request.company_info
    )

    return {
        "status": "success",
        "data": {
            "greeting": greeting,
            "jd_analysis": jd_info,
            "platforms": {
                "boss": greeting.get("boss", ""),
                "liepin": greeting.get("liepin", ""),
                "email": greeting.get("email", "")
            }
        }
    }

# ============================================================================
# 打招呼语生成（SSE流式）
# ============================================================================

class StreamGreetingRequest(BaseModel):
    resume_text: Optional[str] = None
    jd_content: str
    company_name: Optional[str] = None
    position: Optional[str] = None

@router.post("/greeting/stream-generate")
async def stream_generate_greeting(request: StreamGreetingRequest):
    """流式生成打招呼语"""

    async def event_generator():
        try:
            # 1. 分析JD
            yield create_event("status", "分析目标岗位...")
            jd_info = await jd_analyzer.analyze(request.jd_content)
            yield create_event("jd_info", jd_info)
            await asyncio.sleep(0.2)

            # 2. 提取简历亮点
            yield create_event("status", "提取简历亮点...")
            resume_info = {
                "name": "候选人",
                "experience_summary": request.resume_text[:200] if request.resume_text else "有相关工作经验",
                "skills": jd_info.get("skills", [])[:5],
                "achievements": []
            }
            await asyncio.sleep(0.2)

            # 3. 生成打招呼语
            yield create_event("status", "生成打招呼语...")

            if ai_service.llm:
                try:
                    greeting = await greeting_generator.generate(
                        resume_info=resume_info,
                        jd_info=jd_info,
                        company_info={"name": request.company_name} if request.company_name else None
                    )
                except Exception as e:
                    # 回退到模板生成
                    greeting = generate_template_greeting(request.company_name, request.position, resume_info)
            else:
                greeting = generate_template_greeting(request.company_name, request.position, resume_info)

            yield create_event("greeting", greeting)
            await asyncio.sleep(0.2)

            # 4. 完成
            yield create_event("status", "生成完成")
            yield create_event("done", True, done=True)

        except Exception as e:
            yield create_event("error", str(e))
            yield create_event("done", True, done=True)

    return StreamingResponse(
        sse_generator(event_generator()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

def generate_template_greeting(company: str, position: str, resume_info: Dict) -> Dict:
    """模板方式生成打招呼语（无AI时使用）"""
    company = company or "贵公司"
    position = position or "相关岗位"
    highlight = resume_info.get("skills", ["相关技能"])[0] if resume_info.get("skills") else "相关经验"

    return {
        "boss": f"您好，我对{company}{position}很感兴趣，我有{highlight}经验，希望能和您详细聊聊。",
        "liepin": f"您好！看到贵司正在招聘{position}，我的背景与该岗位匹配度较高，期待能与您进一步沟通。",
        "email": f"尊敬的HR，您好！\n\n我是看到{company}{position}招聘信息后投递简历的求职者。我具备{highlight}经验，相信能够胜任该岗位。\n\n期待您的回复，谢谢！"
    }

# ============================================================================
# 面试题生成API（SSE流式）
# ============================================================================

class InterviewRequest(BaseModel):
    resume_text: Optional[str] = None
    jd_content: str

@router.post("/interview/stream-generate")
async def stream_generate_interview(request: InterviewRequest):
    """流式生成面试题"""

    async def event_generator():
        try:
            # 1. 分析JD
            yield create_event("status", "分析目标岗位要求...")
            jd_info = await jd_analyzer.analyze(request.jd_content)
            yield create_event("jd_info", jd_info)
            await asyncio.sleep(0.2)

            # 2. 生成技术题
            yield create_event("status", "生成技术面试题...")
            await asyncio.sleep(0.3)

            skills = jd_info.get("skills", [])
            tech_questions = []
            if skills:
                for i, skill in enumerate(skills[:3]):
                    tech_questions.append({
                        "skill": skill,
                        "questions": [
                            f"请介绍一下你在{skill}方面的工作经验",
                            f"如何用{skill}解决一个实际问题？",
                            f"{skill}的最佳实践是什么？"
                        ]
                    })
                    if i < 2:
                        await asyncio.sleep(0.2)

            yield create_event("tech_questions", tech_questions)

            # 3. 生成行为题
            yield create_event("status", "生成行为面试题...")
            await asyncio.sleep(0.3)

            behavior_questions = [
                {
                    "category": "STAR法则",
                    "questions": [
                        "请描述一个你成功解决复杂问题的案例（Situation-Task-Action-Result）",
                        "请分享一次你与团队成员产生分歧的经历，如何处理的？",
                        "描述一个你需要在有限时间内完成重要任务的经历"
                    ]
                },
                {
                    "category": "职业发展",
                    "questions": [
                        "你为什么对这个岗位/行业感兴趣？",
                        "未来3-5年的职业规划是什么？",
                        "你最大的优势和改进空间是什么？"
                    ]
                }
            ]

            yield create_event("behavior_questions", behavior_questions)

            # 4. AI增强（如果有API）
            if ai_service.llm:
                yield create_event("status", "AI增强面试题...")
                try:
                    ai_questions = await interviewer.generate(request.jd_content, request.resume_text)
                    yield create_event("ai_questions", ai_questions)
                except Exception as e:
                    yield create_event("error", f"AI增强失败: {str(e)}")

            yield create_event("status", "面试题生成完成")
            yield create_event("done", True, done=True)

        except Exception as e:
            yield create_event("error", str(e))
            yield create_event("done", True, done=True)

    return StreamingResponse(
        sse_generator(event_generator()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================================
# AI状态API（已迁移到上方 set-api-key 接口）
# ============================================================================

# 保留旧接口用于兼容

class TemplateValidationRequest(BaseModel):
    template: str
    variables: Dict[str, str]

@router.post("/greeting/validate-template")
async def validate_template(request: TemplateValidationRequest):
    """验证打招呼语模板"""
    result = greeting_generator.validate_template(
        request.template,
        request.variables
    )
    return result

# ============================================================================
# STAR法则简历优化API（SSE流式）
# ============================================================================

class STAROptimizeRequest(BaseModel):
    resume_text: str
    jd_content: Optional[str] = None
    section: Optional[str] = None  # 指定优化某个模块

@router.post("/resume/stream-star-optimize")
async def stream_star_optimize(request: STAROptimizeRequest):
    """流式STAR法则简历优化"""

    async def event_generator():
        try:
            # 1. 解析简历结构
            yield create_event("status", "解析简历结构...")
            sections = resume_analyzer.parse_resume(request.resume_text)
            yield create_event("sections", list(sections.keys()))
            await asyncio.sleep(0.2)

            # 2. 提取待优化项目
            yield create_event("status", "提取待优化内容...")
            items = resume_analyzer.extract_sections_for_optimization(request.resume_text)
            yield create_event("items_count", len(items))

            if not items:
                yield create_event("status", "未找到可优化的内容")
                yield create_event("done", True, done=True)
                return

            # 3. 逐项优化
            optimizations = []
            for i, item in enumerate(items):
                yield create_event("status", f"优化中 ({i+1}/{len(items)})...")
                yield create_event("progress", {
                    "current": i + 1,
                    "total": len(items),
                    "section": item.get("section", ""),
                    "title": item.get("title", "")[:30]
                })

                try:
                    if ai_service.llm:
                        optimized = await star_optimizer.optimize(
                            item["content"],
                            request.jd_content
                        )
                    else:
                        optimized = star_optimizer._generate_fallback_optimization(item["content"])

                    optimization = {
                        **item,
                        "optimized": optimized
                    }
                    optimizations.append(optimization)

                    yield create_event("optimization", {
                        "index": i,
                        "data": optimization
                    })
                except Exception as e:
                    yield create_event("error", f"优化第{i+1}项失败: {str(e)}")

                await asyncio.sleep(0.1)

            # 4. 完成
            yield create_event("status", "优化完成")
            yield create_event("optimizations", optimizations)
            yield create_event("done", True, done=True)

        except Exception as e:
            yield create_event("error", str(e))
            yield create_event("done", True, done=True)

    return StreamingResponse(
        sse_generator(event_generator()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================================================
# API Key 设置API
# ============================================================================

class SetAPIKeyRequest(BaseModel):
    """设置API Key请求"""
    provider: str
    api_key: str
    model: Optional[str] = None

@router.post("/set-api-key")
async def set_api_key(request: SetAPIKeyRequest):
    """设置AI API Key（动态生效，不保存到文件）"""
    try:
        ai_service.set_api_key(
            provider=request.provider,
            api_key=request.api_key,
            model=request.model
        )
        status = ai_service.get_status()
        return {
            "success": True,
            "message": f"已成功配置 {status['provider']} API",
            "status": status
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@router.get("/status")
async def get_ai_status():
    """获取AI服务状态"""
    status = ai_service.get_status()
    return {
        "ai_enabled": status["enabled"],
        "provider": status["provider"],
        "model": status["model"],
        "message": "AI服务已启用" if status["enabled"] else "请配置 API Key"
    }
