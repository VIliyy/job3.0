# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - AI服务基类

支持：
1. DeepSeek API（推荐，便宜且支持思考链）
2. OpenAI API
3. 本地模型（待实现）
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from app.core.config_manager import config_manager


class LLMService(ABC):
    """大语言模型服务基类"""

    @abstractmethod
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求"""
        pass


class DeepSeekLLMService(LLMService):
    """DeepSeek API服务（推荐）"""

    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model
        self.base_url = "https://api.deepseek.com"

    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求"""
        if not self.api_key:
            raise ValueError("DeepSeek API Key未配置")

        try:
            import httpx

            # DeepSeek V4 (deepseek-reasoner) 使用不同的API格式
            is_reasoner = "reasoner" in self.model

            async with httpx.AsyncClient(timeout=180.0) as client:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7) if not is_reasoner else 1.0,
                    "max_tokens": kwargs.get("max_tokens", 4000),
                    "stream": False
                }

                # V4 reasoner 模型不支持 temperature 参数
                if is_reasoner:
                    payload.pop("temperature", None)

                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

                if response.status_code != 200:
                    error_msg = response.json().get("error", {}).get("message", "Unknown error")
                    raise Exception(f"DeepSeek API错误: {error_msg}")

                result = response.json()

                # V4 reasoner 模型返回格式不同
                if is_reasoner:
                    return result["choices"][0]["message"]["content"]
                return result["choices"][0]["message"]["content"]

        except ImportError:
            raise Exception("请安装 httpx: pip install httpx")
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")


class OpenAILLMService(LLMService):
    """OpenAI API服务"""

    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求"""
        if not self.api_key:
            raise ValueError("OpenAI API Key未配置")

        try:
            import httpx

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 4000)
                    }
                )

                if response.status_code != 200:
                    error_msg = response.json().get("error", {}).get("message", "Unknown error")
                    raise Exception(f"OpenAI API错误: {error_msg}")

                result = response.json()
                return result["choices"][0]["message"]["content"]

        except ImportError:
            raise Exception("请安装 httpx: pip install httpx")
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")


class AIService:
    """AI能力服务（整合多个LLM）"""

    def __init__(self):
        self.llm: Optional[LLMService] = None
        self.provider: str = "none"  # deepseek, openai, none
        self._init_llm()

    def _init_llm(self):
        """初始化LLM服务（从配置文件读取已保存的 API Key）"""
        from app.core.config import settings

        # 1. 优先使用 DeepSeek V4
        deepseek_key = os.getenv("DEEPSEEK_API_KEY") or settings.DEEPSEEK_API_KEY
        if not deepseek_key:
            # 尝试从持久化配置读取
            deepseek_key = config_manager.get("DEEPSEEK_API_KEY")

        if deepseek_key:
            model = os.getenv("DEEPSEEK_MODEL") or settings.DEEPSEEK_MODEL
            if not model or model == "deepseek-reasoner":
                model = config_manager.get("DEEPSEEK_MODEL") or "deepseek-reasoner"
            self.llm = DeepSeekLLMService(api_key=deepseek_key, model=model)
            self.provider = "deepseek"
            print(f"[OK] AI服务已初始化（DeepSeek {model}）")
            return

        # 2. 其次使用 OpenAI
        openai_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        if not openai_key:
            openai_key = config_manager.get("OPENAI_API_KEY")

        if openai_key:
            model = os.getenv("OPENAI_MODEL") or settings.OPENAI_MODEL
            if not model:
                model = config_manager.get("OPENAI_MODEL") or "gpt-3.5-turbo"
            self.llm = OpenAILLMService(api_key=openai_key, model=model)
            self.provider = "openai"
            print(f"[OK] AI服务已初始化（OpenAI {model}）")
            return

        print("[WARN] 警告：未配置任何AI API Key，AI能力受限")

    def set_api_key(self, provider: str, api_key: str, model: str = None):
        """动态设置API Key（同时持久化到 .env 文件）"""
        if provider == "deepseek":
            self.llm = DeepSeekLLMService(
                api_key=api_key,
                model=model or "deepseek-reasoner"  # 默认使用 V4
            )
            self.provider = "deepseek"
            # 持久化保存
            config_manager.set_api_key("deepseek", api_key, model or "deepseek-reasoner")
            print("[OK] DeepSeek API Key 已保存（重启后仍然有效）")
        elif provider == "openai":
            self.llm = OpenAILLMService(
                api_key=api_key,
                model=model or "gpt-3.5-turbo"
            )
            self.provider = "openai"
            # 持久化保存
            config_manager.set_api_key("openai", api_key, model or "gpt-3.5-turbo")
            print("[OK] OpenAI API Key 已保存（重启后仍然有效）")
        else:
            self.llm = None
            self.provider = "none"

    def get_status(self) -> Dict:
        """获取AI服务状态"""
        return {
            "enabled": self.llm is not None,
            "provider": self.provider,
            "model": getattr(self.llm, 'model', None) if self.llm else None
        }

    async def chat(self, messages: List[Dict]) -> str:
        """通用对话接口"""
        if not self.llm:
            return "请配置 DeepSeek 或 OpenAI API Key 以启用AI能力"

        try:
            return await self.llm.chat(messages)
        except Exception as e:
            return f"AI服务调用失败: {str(e)}"

    async def chat_simple(self, prompt: str, system: str = None) -> str:
        """简单对话接口"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages)

    # ========================================================================
    # JD 分析
    # ========================================================================

    async def analyze_jd(self, jd_text: str) -> Dict[str, Any]:
        """分析JD文本"""
        if not self.llm:
            return {"error": "请配置 API Key"}

        prompt = f"""请分析以下职位描述，提取关键信息：

{jd_text}

请以JSON格式返回分析结果，包含以下字段：
- company: 公司名称
- position: 职位名称
- salary_range: 薪资范围
- core_skills: 核心技能要求（数组）
- preferred_skills: 加分技能（数组）
- experience_requirement: 经验要求
- education_requirement: 学历要求
- job_summary: 岗位简介"""

        try:
            response = await self.chat_simple(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            return {"error": str(e)}

    # ========================================================================
    # 简历-JD 匹配
    # ========================================================================

    async def match_resume_jd(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """分析简历与JD匹配度"""
        if not self.llm:
            return {"error": "请配置 API Key"}

        prompt = f"""请分析以下简历与职位描述的匹配度：

## 简历内容：
{resume_text[:2000]}

## 职位描述：
{jd_text[:2000]}

请以JSON格式返回分析结果，包含：
- match_score: 匹配分数（0-100）
- match_level: 匹配等级（高度匹配/基本匹配/勉强匹配/不匹配）
- skill_analysis: 技能分析
  - matched_skills: 匹配的技能
  - partial_skills: 部分匹配的技能
  - missing_skills: 缺失的技能
- experience_analysis: 经验分析
- overall_suggestions: 优化建议（数组）
- ats_optimization: ATS优化建议"""

        try:
            response = await self.chat_simple(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            return {"error": str(e)}

    # ========================================================================
    # 打招呼语生成
    # ========================================================================

    async def generate_greeting(
        self,
        resume_info: Dict[str, Any],
        jd_info: Dict[str, Any],
        company_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成打招呼语"""
        if not self.llm:
            return {"error": "请配置 API Key"}

        company = jd_info.get("company", "贵公司")
        position = jd_info.get("position", "相关岗位")
        skills = ", ".join(jd_info.get("core_skills", [])[:5])

        prompt = f"""请根据以下信息生成打招呼语：

## 候选人信息：
- 姓名：{resume_info.get('name', '候选人')}
- 经验：{resume_info.get('experience_summary', '相关工作经验')}
- 技能：{', '.join(resume_info.get('skills', [])[:5])}

## 目标岗位：
- 公司：{company}
- 岗位：{position}
- 核心技能：{skills}

请生成3种平台的开场白：
1. BOSS直聘（50字以内，简短直接）
2. 猎聘（100字以内，专业正式）
3. 邮件（150字以内，正式完整）

请以JSON格式返回：
{{
    "boss": "BOSS直聘版本",
    "liepin": "猎聘版本",
    "email": "邮件版本"
}}"""

        try:
            response = await self.chat_simple(prompt)
            result = self._parse_json_response(response)
            return {
                "boss": result.get("boss", ""),
                "liepin": result.get("liepin", ""),
                "email": result.get("email", "")
            }
        except Exception as e:
            return {"error": str(e)}

    # ========================================================================
    # 工具方法
    # ========================================================================

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析JSON响应"""
        try:
            # 尝试直接解析
            return json.loads(response)
        except:
            pass

        try:
            # 尝试提取JSON块
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"JSON解析失败: {e}")

        return {"raw": response}


# 全局AI服务实例
ai_service = AIService()
