# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - LangChain Agent 编排

使用 LangGraph 实现多 Agent 协作系统
"""

import json
from typing import Dict, Any, List, Literal, TypedDict, Annotated, Sequence
from sqlalchemy.orm import Session
import operator

# 延迟导入避免循环依赖
def get_ai_service():
    from app.agents.base import ai_service
    return ai_service

# LangGraph 相关导入
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


# ==============================================================================
# Agent 系统提示词
# ==============================================================================

AGENT_SYSTEM_PROMPT = """你是一个专业的求职助手「Job3.0 Agent」，帮助用户管理整个求职过程。

你的核心能力：
1. 简历管理 - 搜索和分析用户的简历内容
2. 投递追踪 - 查看和管理求职投递记录
3. JD分析 - 解析职位描述，提取关键信息
4. 匹配分析 - 分析简历与职位的匹配度
5. 打招呼语 - 生成专业的求职开场白

当用户询问与简历、投递、JD、求职相关的问题时，你应该：
1. 首先使用相关工具获取必要信息
2. 基于获取的数据进行分析和建议
3. 给出具体、可操作的建议

重要原则：
- 如果用户提到"我的简历"、"简历内容"等，先用 resume_search 工具获取简历
- 如果用户提到投递记录、公司状态等，先用 application_list 或 application_search 工具
- 如果用户问是否投递过某公司，用 application_check_duplicate 工具检查
- 始终基于实际数据回答，不要编造信息

回复风格：
- 友好、专业、有帮助
- 使用 Emoji 增加可读性
- 关键信息用列表或表格呈现
- 适当追问以获取更多信息
"""


# ==============================================================================
# 简历检测关键词
# ==============================================================================
RESUME_KEYWORDS = [
    "教育经历", "工作经历", "项目经历", "实习经历",
    "本科", "硕士", "博士", "专业", "GPA",
    "技能", "技术栈", "熟练", "掌握",
    "独立开发", "主导", "从0到1",
    "林育丞", "张三", "李四",  # 常见姓名
]

# JD 检测关键词
JD_KEYWORDS = [
    "岗位职责", "岗位要求", "任职要求", "任职资格",
    "职位描述", "职位要求", "岗位描述",
    "3年以上", "5年以上", "1年以上",
    "熟悉", "掌握", "精通",
    "本科及以上", "大专以上",
    "加分项", "优先考虑",
]

# JD 内容特征（长文本 + 职位相关）
JD_INDICATORS = [
    "后端", "前端", "开发", "工程师", "设计师", "产品经理",
    "Python", "Java", "Go", "JavaScript", "React", "Vue",
    "数据库", "MySQL", "Redis", "MongoDB",
    "微服务", "分布式", "云服务", "Docker", "K8s",
]


# ==============================================================================
# 工具函数封装
# ==============================================================================

def create_langchain_tools(db: Session) -> List:
    """创建 LangChain 格式的工具"""
    if not LANGCHAIN_AVAILABLE:
        return []

    tools_dict = get_tools_dict(db)

    langchain_tools = []
    for name, tool in tools_dict.items():
        # 创建 LangChain Tool
        lc_tool = Tool(
            name=tool.name,
            description=tool.description,
            func=lambda x, t=tool: t.run(x) if hasattr(t, 'run') else str(t),
        )
        langchain_tools.append(lc_tool)

    return langchain_tools


# ==============================================================================
# 简化版 Agent（无 LangChain 时使用）
# ==============================================================================

class SimpleAgent:
    """简化版 Agent - 支持 JD 自动识别和分析"""

    def __init__(self, db: Session):
        self.db = db
        self.tools = get_tools_dict(db)

    async def chat(self, message: str, history: List[Dict] = None) -> Dict[str, Any]:
        """处理用户消息"""

        # 1. 检测是否是 JD（长文本 + JD 特征）
        if self._is_jd_content(message):
            return await self._handle_jd(message)

        # 2. 检测是否是简历内容
        if self._is_resume_content(message):
            return await self._handle_resume(message)

        # 3. 分析用户意图
        intent = self._analyze_intent(message.lower())

        # 根据意图调用工具
        if intent == "search_resume":
            result = self._search_resume(message)
            return {"response": result, "tool_used": "resume_search"}

        elif intent == "list_resume":
            result = self._list_resume()
            return {"response": result, "tool_used": "resume_list"}

        elif intent == "list_applications":
            result = self._list_applications()
            return {"response": result, "tool_used": "application_list"}

        elif intent == "search_application":
            company = self._extract_company(message)
            result = self._search_application(company)
            return {"response": result, "tool_used": "application_search"}

        elif intent == "check_duplicate":
            company = self._extract_company(message)
            result = self._check_duplicate(company)
            return {"response": result, "tool_used": "application_check_duplicate"}

        elif intent == "greeting_templates":
            result = self._list_greeting_templates()
            return {"response": result, "tool_used": "greeting_template_list"}

        elif intent == "help":
            return {"response": self._get_help(), "tool_used": None}

        else:
            # 使用 AI 生成回复
            return await self._ai_chat(message, history)

    def _is_jd_content(self, text: str) -> bool:
        """检测是否是 JD 内容"""
        if len(text) < 100:
            return False

        # 检查 JD 关键词数量
        jd_keyword_count = sum(1 for kw in JD_KEYWORDS if kw in text)

        # 检查 JD 指标词
        indicator_count = sum(1 for ind in JD_INDICATORS if ind in text)

        # 排除简历特征
        is_resume = any(kw in text for kw in ["教育经历", "项目经历", "工作经历"])

        # JD: 长文本 + 多个 JD 关键词 + 多个指标词 + 不是简历
        return (jd_keyword_count >= 2 or indicator_count >= 3) and not is_resume

    def _is_resume_content(self, text: str) -> bool:
        """检测是否是简历内容"""
        if len(text) < 100:
            return False

        # 检查简历关键词
        keyword_count = sum(1 for kw in RESUME_KEYWORDS if kw in text)

        return keyword_count >= 2

    async def _handle_jd(self, jd_text: str) -> Dict[str, Any]:
        """处理 JD 内容 - 自动分析并匹配简历"""
        try:
            # 1. 先获取用户简历
            resume_tool = self.tools.get("resume_search")
            resume_data = resume_tool.run("") if resume_tool else None

            # 2. 使用 AI 分析 JD 并匹配
            analysis = await self._analyze_jd_with_ai(jd_text, resume_data)

            return {
                "response": analysis,
                "tool_used": "jd_analyze"
            }
        except Exception as e:
            return {
                "response": f"分析 JD 时出错: {str(e)}",
                "tool_used": "error"
            }

    async def _analyze_jd_with_ai(self, jd_text: str, resume_data: str = None) -> str:
        """使用 AI 分析 JD"""
        if not get_ai_service().llm:
            # 无 AI 时使用规则分析
            return self._rule_based_jd_analysis(jd_text, resume_data)

        prompt = f"""你是一个专业的 HR 助手，请分析以下职位描述，提取关键信息，并用友好的方式呈现给用户。

职位描述：
{jd_text[:3000]}

{"用户简历摘要（用于匹配分析）：" + resume_data[:500] if resume_data else ""}

请按以下格式回复（用中文）：

📋 **职位信息**
• 公司：{{从JD中提取}}
• 岗位：{{从JD中提取}}
• 薪资：{{从JD中提取，标注"未标注"如果没找到}}
• 地点：{{从JD中提取}}

📌 **核心要求**
• 学历：{{从JD中提取}}
• 经验：{{从JD中提取}}
• 技能：{{列出3-5个核心技能}}

🎯 **匹配分析**
{{如果有简历，分析匹配度和建议；如果没有简历，提示用户可以上传简历获取个性化分析}}

💡 **建议**
{{给出1-2条实用建议}}"""

        try:
            response = await get_ai_service().chat_simple(prompt)
            return response
        except Exception as e:
            return self._rule_based_jd_analysis(jd_text, resume_data)

    def _rule_based_jd_analysis(self, jd_text: str, resume_data: str = None) -> str:
        """基于规则的 JD 分析（无 AI 时使用）"""
        lines = jd_text.split('\n')
        result = ["📋 **职位分析结果**\n"]

        # 提取关键信息
        skills = []
        requirements = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 提取技能关键词
            skill_keywords = ["Python", "Java", "Go", "MySQL", "Redis", "Docker",
                            "FastAPI", "Django", "Flask", "Vue", "React", "MongoDB"]
            for skill in skill_keywords:
                if skill in line and skill not in skills:
                    skills.append(skill)

            # 提取要求
            if any(kw in line for kw in ["年以上", "以上", "优先", "熟悉", "掌握"]):
                requirements.append(line[:100])

        if skills:
            result.append("**🔧 核心技能：** " + ", ".join(skills[:8]))

        if requirements:
            result.append("\n**📌 关键要求：**")
            for req in requirements[:5]:
                result.append(f"• {req}")

        if resume_data:
            result.append("\n\n💡 **提示：** 我已获取您的简历，可以为您做更详细的匹配分析。请说「分析匹配度」或「优化简历」。")
        else:
            result.append("\n\n💡 **提示：** 上传您的简历，我可以帮您分析与这个职位的匹配度并给出优化建议！")

        return "\n".join(result)

    async def _handle_resume(self, resume_text: str) -> Dict[str, Any]:
        """处理简历内容"""
        return {
            "response": "📄 已收到您的简历内容！\n\n您可以：\n• 说「分析这个JD」让我对比分析\n• 说「优化简历」获取优化建议\n• 说「生成打招呼语」生成开场白\n\n请提供目标职位描述，我可以给您更针对性的建议！",
            "tool_used": "resume_receive"
        }

    def _analyze_intent(self, message: str) -> str:
        """分析用户意图"""
        # 简历相关
        if any(kw in message for kw in ["我的简历", "简历内容", "工作经历", "技能", "项目经验", "看看简历", "查看简历", "简历是什么"]):
            return "search_resume"
        if any(kw in message for kw in ["有哪些简历", "简历列表", "所有简历", "简历版本"]):
            return "list_resume"

        # 投递相关
        if any(kw in message for kw in ["投递记录", "投了哪些", "投递情况", "投了", "投递列表"]):
            return "list_applications"
        if any(kw in message for kw in ["有没有投", "投过", "是否投递", "投递过", "投了没"]):
            return "check_duplicate"

        # 打招呼语相关
        if any(kw in message for kw in ["打招呼", "开场白", "模板", "打招呼语"]):
            return "greeting_templates"

        # 帮助
        if any(kw in message for kw in ["帮助", "help", "怎么用", "功能", "能干", "有什么"]):
            return "help"

        return "general"

    def _extract_company(self, message: str) -> str:
        """提取公司名"""
        keywords = ["有没有投", "投过", "是否投递", "投递过", "向"]
        for kw in keywords:
            if kw in message:
                idx = message.find(kw) + len(kw)
                rest = message[idx:].strip()
                for end in ["吗", "过", "没", "吗？", "？", "吗？"]:
                    if end in rest:
                        rest = rest[:rest.find(end)]
                return rest.strip()
        return message.replace("有没有投", "").replace("投过", "").replace("是否投递", "").strip()

    def _search_resume(self, message: str) -> str:
        """搜索简历"""
        query = ""
        keywords = ["我的简历", "简历内容", "工作经历"]
        for kw in keywords:
            if kw in message:
                query = message[message.find(kw) + len(kw):].strip()
                break

        tool = self.tools.get("resume_search")
        if tool:
            data = tool.run(query)
            return self._format_resume_response(data)
        return "简历工具不可用"

    def _list_resume(self) -> str:
        """列出简历"""
        tool = self.tools.get("resume_list")
        if tool:
            data = tool.run()
            return self._format_list_response(data)
        return "简历工具不可用"

    def _format_resume_response(self, data: str) -> str:
        """格式化简历响应为友好文本"""
        try:
            # 尝试解析 JSON
            info = json.loads(data)

            if "没有上传" in data or "没有找到" in data:
                return "📄 **您的简历状态**\n\n目前还没有上传任何简历。\n\n💡 请先在「简历管理」页面上传您的简历，上传后我就能帮您分析啦！"

            # 格式化输出
            result = ["📄 **您的简历信息**\n"]

            version_name = info.get("version_name", info.get("filename", "未命名"))
            result.append(f"• 版本：{version_name}")

            content = info.get("content", "")
            if content:
                # 提取关键信息
                lines = content.split('\n')[:30]  # 只取前30行
                result.append("\n**📝 内容预览：**")
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 2:
                        result.append(f"• {line[:80]}{'...' if len(line) > 80 else ''}")

                if len(content) > 500:
                    result.append(f"\n_（简历完整内容 {len(content)} 字符，已保存）_")

            return "\n".join(result)
        except json.JSONDecodeError:
            # 如果不是 JSON，直接返回
            if "没有" in data:
                return "📄 **您的简历状态**\n\n目前还没有上传任何简历。\n\n💡 请先在「简历管理」页面上传您的简历！"
            return f"📄 **简历信息**\n\n{data}"

    def _format_list_response(self, data: str) -> str:
        """格式化列表响应"""
        try:
            items = json.loads(data)

            if not items or (isinstance(items, list) and len(items) == 0):
                return "📋 **简历列表**\n\n目前没有上传任何简历。"

            result = ["📋 **您的简历列表**\n"]

            for item in items:
                if isinstance(item, dict):
                    slot = item.get("槽位", "")
                    name = item.get("版本名", item.get("文件名", ""))
                    date = item.get("更新时间", "")
                    active = item.get("是否使用中", "")

                    result.append(f"**{slot}** - {name}")
                    if date:
                        result.append(f"   更新于 {date}")
                    if active:
                        result.append(f"   {active} ✓")
                    result.append("")

            return "\n".join(result).strip()
        except:
            if "没有" in data:
                return "📋 **简历列表**\n\n目前没有上传任何简历。"
            return f"📋 **简历列表**\n\n{data}"

    def _list_applications(self) -> str:
        """列出投递记录"""
        tool = self.tools.get("application_list")
        if tool:
            data = tool.run()
            return self._format_applications_response(data)
        return "投递工具不可用"

    def _format_applications_response(self, data: str) -> str:
        """格式化投递记录响应"""
        try:
            items = json.loads(data)

            if not items:
                return "📮 **投递记录**\n\n目前没有投递记录。\n\n💡 投递后记得在这里记录，我会帮您追踪状态！"

            result = ["📮 **您的投递记录**\n"]

            for item in items:
                company = item.get("公司", "")
                position = item.get("岗位", "")
                status = item.get("状态", "")
                salary = item.get("薪资", "")

                # 状态 Emoji
                status_emoji = {
                    "pending": "⏳", "applied": "📤", "interview": "🎯",
                    "offer": "🎉", "rejected": "❌", "hired": "✅"
                }.get(status.lower(), "📋")

                result.append(f"{status_emoji} **{company}** - {position}")
                if salary and salary != "未填写":
                    result.append(f"   薪资：{salary}")
                result.append(f"   状态：{status}")
                result.append("")

            return "\n".join(result).strip()
        except:
            if "没有" in data:
                return "📮 **投递记录**\n\n目前没有投递记录。"
            return f"📮 **投递记录**\n\n{data}"

    def _search_application(self, company: str) -> str:
        """搜索投递记录"""
        tool = self.tools.get("application_search")
        if tool:
            data = tool.run(company)
            return data  # 已经是格式化的
        return "投递工具不可用"

    def _check_duplicate(self, company: str) -> str:
        """检查重复投递"""
        tool = self.tools.get("application_check_duplicate")
        if tool:
            data = tool.run(company)
            try:
                info = json.loads(data)
                return info.get("message", data)
            except:
                return data
        return "投递工具不可用"

    def _list_greeting_templates(self) -> str:
        """列出打招呼语模板"""
        tool = self.tools.get("greeting_template_list")
        if tool:
            data = tool.run()
            try:
                items = json.loads(data)
                if not items:
                    return "💬 **打招呼语模板**\n\n目前没有模板。\n\n💡 可以创建一个通用模板，我会根据不同公司生成！"

                result = ["💬 **您的打招呼语模板**\n"]
                for item in items:
                    name = item.get("名称", "")
                    preview = item.get("内容预览", "")[:50]
                    result.append(f"• **{name}**")
                    result.append(f"  {preview}...")
                    result.append("")

                return "\n".join(result).strip()
            except:
                return f"💬 **打招呼语模板**\n\n{data}"
        return "打招呼语工具不可用"

    async def _ai_chat(self, message: str, history: List[Dict] = None) -> Dict[str, Any]:
        """使用 AI 生成回复"""
        if not get_ai_service().llm:
            return {
                "response": self._get_help(),
                "tool_used": None
            }

        prompt = f"""{AGENT_SYSTEM_PROMPT}

用户问题：{message}

请给出有帮助的回复。"""

        try:
            response = await get_ai_service().chat_simple(prompt)
            return {"response": response, "tool_used": "ai"}
        except Exception as e:
            return {
                "response": self._get_help(),
                "tool_used": "error"
            }

    def _get_help(self) -> str:
        """获取帮助信息"""
        return """🤖 **Job3.0 Agent 使用指南**

我可以帮您：

📄 **简历相关**
• "我的简历是什么" - 查看简历内容
• "有哪些简历" - 查看简历列表

💼 **投递相关**
• "我的投递记录" - 查看所有投递
• "有没有投XX公司" - 检查是否投递过

💬 **打招呼语**
• "打招呼语模板" - 查看可用模板

🔍 **JD 分析**
• 直接粘贴职位描述，我来帮您分析！

📝 **简历优化**
• 提供简历 + 目标 JD，我来评估匹配度

请告诉我您想做什么？"""


# ==============================================================================
# LangChain Agent（需要安装 langchain）
# ==============================================================================

class LangChainAgent:
    """LangChain Agent - 使用 OpenAI Functions Agent"""

    def __init__(self, db: Session):
        self.db = db
        self.tools = create_langchain_tools(db)
        self.agent = None
        self.memory = None
        self._init_agent()

    def _init_agent(self):
        """初始化 Agent"""
        if not LANGCHAIN_AVAILABLE:
            print("[WARN] LangChain 未安装，使用简化版 Agent")
            return

        if not self.tools:
            print("[WARN] 没有可用工具，Agent 功能受限")
            return

        # 获取 LLM
        llm = self._get_llm()
        if not llm:
            print("[WARN] 没有可用的 LLM，Agent 功能受限")
            return

        try:
            # 使用 OpenAI Functions Agent
            self.agent = initialize_agent(
                tools=self.tools,
                llm=llm,
                agent=AgentType.OPENAI_FUNCTIONS,
                verbose=True,
                prompt=AGENT_SYSTEM_PROMPT,
                handle_parsing_errors=True
            )
            print("[OK] LangChain Agent 初始化成功")
        except Exception as e:
            print(f"[ERROR] LangChain Agent 初始化失败: {e}")

    def _get_llm(self):
        """获取 LangChain LLM"""
        if not LANGCHAIN_AVAILABLE:
            return None

        try:
            from langchain.chat_models import ChatOpenAI

            # 优先使用 DeepSeek
            api_key = os.getenv("DEEPSEEK_API_KEY") or settings.DEEPSEEK_API_KEY
            base_url = "https://api.deepseek.com/v1"

            if api_key:
                return ChatOpenAI(
                    model="deepseek-chat",
                    api_key=api_key,
                    base_url=base_url,
                    temperature=0.7
                )

            # 其次使用 OpenAI
            api_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
            if api_key:
                return ChatOpenAI(
                    model="gpt-3.5-turbo",
                    api_key=api_key,
                    temperature=0.7
                )
        except Exception as e:
            print(f"[ERROR] 获取 LLM 失败: {e}")

        return None

    async def chat(self, message: str, history: List[Dict] = None) -> Dict[str, Any]:
        """处理用户消息"""
        if not self.agent:
            # 回退到简化版
            simple = SimpleAgent(self.db)
            return await simple.chat(message, history)

        try:
            response = self.agent.run(message)
            return {"response": str(response), "tool_used": "langchain"}
        except Exception as e:
            print(f"[ERROR] Agent 运行出错: {e}")
            # 回退到简化版
            simple = SimpleAgent(self.db)
            return await simple.chat(message, history)


# ==============================================================================
# Agent 工厂
# ==============================================================================

def create_agent(db: Session):
    """创建 Agent 实例"""
    if LANGCHAIN_AVAILABLE:
        return LangChainAgent(db)
    return SimpleAgent(db)


# ==============================================================================
# 全局 Agent 实例（按需创建）
# ==============================================================================

def get_agent(db: Session) -> SimpleAgent:
    """获取 Agent 实例"""
    return SimpleAgent(db)
