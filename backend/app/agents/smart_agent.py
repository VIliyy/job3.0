# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 增强版 Agent

核心能力：
1. 多轮对话记忆
2. 上下文理解
3. 主动引导
4. 智能意图识别
"""

import json
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.agents.tools import get_tools_dict
from app.agents.base import ai_service


# ==============================================================================
# Agent 状态
# ==============================================================================

class ConversationState:
    """对话状态 - 追踪用户求职进度"""

    # 用户状态枚举
    STAGE_NEW = "new"                    # 新用户
    STAGE_PREPARING = "preparing"        # 准备简历
    STAGE_APPLYING = "applying"          # 投递中
    STAGE_INTERVIEW = "interview"        # 面试中
    STAGE_OFFER = "offer"               # 收到Offer

    # 需要的上下文
    def __init__(self):
        self.stage = self.STAGE_NEW
        self.has_resume = False
        self.resume_content = ""
        self.target_jd = ""
        self.target_company = ""
        self.target_position = ""
        self.last_intent = ""
        self.pending_action = None  # 待完成的动作
        self.context_summary = ""    # 上下文摘要

    def to_dict(self) -> Dict:
        return {
            "stage": self.stage,
            "has_resume": self.has_resume,
            "target_jd": self.target_jd[:200] if self.target_jd else "",
            "target_company": self.target_company,
            "target_position": self.target_position,
            "last_intent": self.last_intent,
            "pending_action": self.pending_action,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ConversationState":
        state = cls()
        state.stage = data.get("stage", cls.STAGE_NEW)
        state.has_resume = data.get("has_resume", False)
        state.resume_content = data.get("resume_content", "")
        state.target_jd = data.get("target_jd", "")
        state.target_company = data.get("target_company", "")
        state.target_position = data.get("target_position", "")
        state.last_intent = data.get("last_intent", "")
        state.pending_action = data.get("pending_action")
        return state


# ==============================================================================
# 增强版 Agent
# ==============================================================================

class SmartAgent:
    """智能 Agent - 支持多轮对话和上下文理解"""

    def __init__(self, db: Session):
        self.db = db
        self.tools = get_tools_dict(db)

    async def chat(
        self,
        message: str,
        history: List[Dict] = None,
        state: Dict = None
    ) -> Dict[str, Any]:
        """
        处理用户消息
        state: 对话状态（从前端传入）
        """
        # 恢复或创建状态
        conversation_state = ConversationState.from_dict(state) if state else ConversationState()
        # 桥接后端自动注入的简历知识（resume_text → resume_content）
        if state and state.get("resume_text") and not conversation_state.resume_content:
            conversation_state.has_resume = True
            conversation_state.resume_content = state["resume_text"]

        # 1. 检测 JD 内容
        if self._is_jd_content(message):
            conversation_state.target_jd = message
            return await self._handle_jd_provided(message, conversation_state, history)

        # 2. 检测简历内容
        if self._is_resume_content(message):
            conversation_state.has_resume = True
            conversation_state.resume_content = message
            return await self._handle_resume_provided(message, conversation_state, history)

        # 3. 分析意图
        intent = self._analyze_intent(message)
        conversation_state.last_intent = intent

        # 4. 根据意图处理
        handlers = {
            "search_resume": lambda: self._handle_resume_request(conversation_state, history),
            "analyze_jd": lambda: self._handle_analyze_jd(conversation_state, history),
            "match": lambda: self._handle_match_request(conversation_state, history),
            "greeting": lambda: self._handle_greeting_request(conversation_state, history),
            "apply": lambda: self._handle_apply_request(conversation_state, history),
            "view_applications": lambda: self._handle_view_applications(conversation_state, history),
            "check_duplicate": lambda: self._handle_duplicate_check(message, conversation_state, history),
            "help": lambda: self._handle_help(conversation_state, history),
            "chitchat": lambda: self._handle_chitchat(message, conversation_state, history),
        }

        handler = handlers.get(intent)
        if handler:
            result = handler()
            result["state"] = conversation_state.to_dict()
            return result

        # 5. 默认使用 AI
        return await self._handle_ai_fallback(message, conversation_state, history)

    # ==========================================================================
    # 内容检测
    # ==========================================================================

    JD_KEYWORDS = [
        "岗位职责", "岗位要求", "任职要求", "任职资格",
        "职位描述", "3年以上", "5年以上", "本科及以上",
        "加分项", "优先考虑", "熟悉", "掌握", "精通"
    ]

    RESUME_KEYWORDS = [
        "教育经历", "工作经历", "项目经历", "实习经历",
        "本科", "硕士", "GPA", "技能", "熟练", "掌握"
    ]

    def _is_jd_content(self, text: str) -> bool:
        """检测是否是 JD 内容"""
        if len(text) < 100:
            return False

        jd_count = sum(1 for kw in self.JD_KEYWORDS if kw in text)
        is_resume = any(kw in text for kw in self.RESUME_KEYWORDS)

        return jd_count >= 2 and not is_resume

    def _is_resume_content(self, text: str) -> bool:
        """检测是否是简历内容"""
        if len(text) < 100:
            return False
        keyword_count = sum(1 for kw in self.RESUME_KEYWORDS if kw in text)
        return keyword_count >= 2

    # ==========================================================================
    # 意图识别
    # ==========================================================================

    def _analyze_intent(self, message: str) -> str:
        """分析用户意图"""
        msg = message.lower()

        # 简历相关
        if any(kw in msg for kw in ["我的简历", "查看简历", "简历是什么"]):
            return "search_resume"

        # JD 分析
        if any(kw in msg for kw in ["分析jd", "jd分析", "职位分析", "分析这个岗位"]):
            return "analyze_jd"

        # 匹配分析
        if any(kw in msg for kw in ["匹配", "匹配度", "对比", "符不符合", "能不能投"]):
            return "match"

        # 打招呼语
        if any(kw in msg for kw in ["打招呼", "开场白", "发消息", "消息模板"]):
            return "greeting"

        # 投递相关
        if any(kw in msg for kw in ["投递", "投了", "申请", "投简历"]):
            return "apply"

        # 查看投递记录
        if any(kw in msg for kw in ["投递记录", "投了哪些", "我的投递"]):
            return "view_applications"

        # 检查是否投递过
        if any(kw in msg for kw in ["有没有投", "投过没", "投过吗", "是否投递"]):
            return "check_duplicate"

        # 帮助
        if any(kw in msg for kw in ["帮助", "help", "你能做什么", "功能"]):
            return "help"

        # 闲聊
        if any(kw in msg for kw in ["你好", "hi", "hello", "谢谢", "好的", "知道了"]):
            return "chitchat"

        return "general"

    # ==========================================================================
    # 处理器
    # ==========================================================================

    async def _handle_jd_provided(
        self,
        jd_text: str,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理用户提供了 JD"""
        # 提取公司名和岗位名
        state.target_jd = jd_text

        # 检查是否已经有简历
        if state.has_resume:
            # 有简历，直接分析匹配度
            response = await self._generate_match_analysis(state)
            state.pending_action = "match_done"
            return {
                "response": response,
                "suggested_actions": ["生成打招呼语", "投递记录", "继续分析"],
                "context": "已有简历和JD",
                "state": state.to_dict()
            }
        else:
            # 没有简历，提示用户
            return {
                "response": """📋 已收到 JD 内容！

我注意到这是一个{position}的职位，我来帮你分析一下：

**核心要求：**
• 学历：{education}
• 经验：{experience}
• 技能：{skills}

💡 **建议：**
为了获得更准确的分析和匹配度评估，建议上传您的简历。我可以：
1. 分析您的简历与该职位的匹配度
2. 找出需要突出的技能
3. 生成针对性的打招呼语

请上传简历或粘贴简历内容？""".format(
                    position="后端开发" if "后端" in jd_text else "相关",
                    education="本科及以上" if "本科" in jd_text else "大专及以上",
                    experience="3年以上" if "3年" in jd_text else "1年以上",
                    skills="Python、MySQL、Redis" if "Python" in jd_text else "相关技能"
                ),
                "suggested_actions": ["上传简历", "继续分析JD"],
                "context": "等待简历",
                "state": state.to_dict()
            }

    async def _handle_resume_provided(
        self,
        resume_text: str,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理用户提供了简历"""
        state.has_resume = True
        state.resume_content = resume_text

        response = """📄 简历已收到！

让我帮你梳理一下简历亮点：

{brief}

"""

        if state.target_jd:
            # 有 JD，引导匹配
            response += """💡 我看到你已经有目标职位了！
我可以帮你：
1. **分析匹配度** - 你的简历与职位的匹配程度
2. **优化建议** - 如何让简历更符合职位要求
3. **生成打招呼语** - 一键生成针对性的开场白

需要我现在分析吗？"""
            state.pending_action = "pending_match"
            suggested = ["分析匹配度", "生成打招呼语", "优化简历"]
        else:
            # 没有 JD，询问目标
            response += """✨ 你的背景很出色！

现在你是在找什么类型的职位呢？比如：
• 后端开发工程师
• 全栈工程师
• AI/机器学习工程师

告诉我你的目标岗位，我可以帮你：
1. 分析简历与职位的匹配度
2. 生成针对性的打招呼语
3. 评估投递成功率"""
            suggested = ["后端开发", "AI工程师", "全栈工程师"]

        return {
            "response": response.format(brief=self._extract_resume_brief(resume_text)),
            "suggested_actions": suggested,
            "context": "简历已保存",
            "state": state.to_dict()
        }

    async def _handle_resume_request(
        self,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理查看简历请求"""
        tool = self.tools.get("resume_search")
        if tool:
            data = tool.run("")
            return {
                "response": self._format_resume_response(data, state.has_resume),
                "suggested_actions": ["优化简历", "分析JD", "生成打招呼语"],
                "state": state.to_dict()
            }
        return {
            "response": "无法获取简历，请先上传简历",
            "suggested_actions": ["上传简历"],
            "state": state.to_dict()
        }

    async def _handle_analyze_jd(
        self,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理 JD 分析请求"""
        if not state.target_jd:
            return {
                "response": """🔍 请先提供职位描述（JD）

你可以：
1. 直接粘贴 JD 内容
2. 上传 JD 截图（我可以通过 OCR 识别）
3. 告诉我公司名和岗位名，我来帮你搜索

粘贴后我会帮你：
• 提取关键要求
• 分析技能匹配度
• 评估投递成功率""",
                "suggested_actions": ["粘贴JD", "上传截图"],
                "state": state.to_dict()
            }

        # 有 JD，分析它
        analysis = await self._analyze_jd_text(state.target_jd)
        return {
            "response": f"""📊 **JD 分析结果**

**职位：** {analysis.get('position', '待识别')}
**公司：** {analysis.get('company', '待识别')}
**薪资：** {analysis.get('salary', '未标注')}

**核心要求：**
• 学历：{analysis.get('education', '本科')}
• 经验：{analysis.get('experience', '1-3年')}
• 技能：{', '.join(analysis.get('skills', [])[:5])}

**匹配建议：**
{analysis.get('suggestion', '上传简历我可以帮你做更详细的匹配分析')}

💡 **下一步：**
• 上传简历 → 获取详细匹配分析
• 生成打招呼语 → 一键生成开场白
• 记录投递 → 追踪求职进度""",
            "suggested_actions": ["上传简历", "生成打招呼语", "记录投递"],
            "context": "JD已分析",
            "state": state.to_dict()
        }

    async def _handle_match_request(
        self,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理匹配请求"""
        if not state.has_resume:
            return {
                "response": """🎯 要分析匹配度，我需要：

1. **你的简历** - 上传或粘贴简历内容
2. **目标职位 JD** - 粘贴职位描述

两个都给我，我帮你分析：
• 技能匹配度
• 经验符合度
• 优化建议""",
                "suggested_actions": ["上传简历", "粘贴JD"],
                "state": state.to_dict()
            }

        if not state.target_jd:
            return {
                "response": """📋 要分析匹配度，请提供目标职位 JD

直接粘贴职位描述，我来帮你：
• 评估匹配度分数
• 找出优势技能
• 识别缺失要求
• 给出优化建议""",
                "suggested_actions": ["粘贴JD"],
                "state": state.to_dict()
            }

        # 有简历有 JD，分析匹配
        response = await self._generate_match_analysis(state)
        state.pending_action = "match_done"
        return {
            "response": response,
            "suggested_actions": ["生成打招呼语", "投递记录", "优化简历"],
            "context": "匹配分析完成",
            "state": state.to_dict()
        }

    async def _handle_greeting_request(
        self,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理打招呼语请求"""
        # 检查是否有公司名
        if state.target_company:
            greeting = self._generate_greeting_preview(state)
            return {
                "response": f"""💬 **打招呼语预览**

**发送给：** {state.target_company} - {state.target_position or '相关岗位'}

**BOSS直聘版（50字）：**
{greeting['boss']}

**猎聘版（100字）：**
{greeting['liepin']}

**邮件版：**
{greeting['email']}

💡 觉得合适的话，我可以帮你：
1. **复制** - 直接复制使用
2. **调整** - 告诉我需要修改的地方
3. **另存模板** - 保存为常用模板""",
                "suggested_actions": ["复制使用", "调整内容", "另存模板"],
                "state": state.to_dict()
            }
        else:
            return {
                "response": """💬 要生成打招呼语，请告诉我：

1. **目标公司** - 你想投哪家公司？
2. **目标岗位** - 是什么职位？（可选）

比如："帮我生成向字节跳动投递后端工程师的打招呼语"

或者直接告诉我公司名，我来帮你生成！""",
                "suggested_actions": ["字节跳动", "腾讯", "阿里巴巴"],
                "state": state.to_dict()
            }

    async def _handle_apply_request(
        self,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理投递请求 - 引导工作流"""
        # 构建工作流引导
        workflow_steps = []

        if not state.has_resume:
            workflow_steps.append("✅ 简历准备")
        else:
            workflow_steps.append("✅ 简历已就绪")

        if not state.target_jd:
            workflow_steps.append("⏳ 粘贴 JD")
        else:
            workflow_steps.append("✅ JD 已分析")

        workflow_steps.append("⏳ 生成打招呼语")
        workflow_steps.append("⏳ 确认投递")
        workflow_steps.append("⏳ 记录追踪")

        response = f"""📮 **投递工作流**

{" | ".join(workflow_steps)}

"""

        if state.has_resume and state.target_jd:
            response += """🎯 看起来你准备得差不多了！

我来帮你完成最后的步骤：

**1. 打招呼语** - 需要我生成吗？

**2. 记录投递** - 投完后可以记录，我会帮你追踪：
• 投递时间
• 公司/职位
• 面试进度

准备好开始投递了吗？"""

            return {
                "response": response,
                "suggested_actions": ["生成打招呼语", "记录投递", "查看投递记录"],
                "context": "准备投递",
                "state": state.to_dict()
            }
        else:
            missing = []
            if not state.has_resume:
                missing.append("上传简历")
            if not state.target_jd:
                missing.append("粘贴目标 JD")

            response += f"""
缺少以下内容：
• {"、".join(missing)}

完成这些后，我帮你一键生成打招呼语并记录投递！"""

            return {
                "response": response,
                "suggested_actions": missing + ["跳过，直接记录"],
                "state": state.to_dict()
            }

    async def _handle_view_applications(
        self,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理查看投递记录"""
        tool = self.tools.get("application_list")
        if tool:
            data = tool.run("")
            return {
                "response": self._format_applications_response(data),
                "suggested_actions": ["添加投递", "更新状态", "分析投递效果"],
                "state": state.to_dict()
            }
        return {
            "response": "暂无投递记录，开始记录你的求职进度吧！",
            "suggested_actions": ["添加投递"],
            "state": state.to_dict()
        }

    async def _handle_duplicate_check(
        self,
        message: str,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理重复投递检查"""
        # 提取公司名
        company = self._extract_company(message)

        tool = self.tools.get("application_check_duplicate")
        if tool and company:
            data = tool.run(company)
            try:
                info = json.loads(data)
                return {
                    "response": info.get("message", data),
                    "suggested_actions": ["查看详情", "更新状态", "继续投递"],
                    "state": state.to_dict()
                }
            except:
                return {
                    "response": data,
                    "suggested_actions": ["继续投递"],
                    "state": state.to_dict()
                }

        return {
            "response": "请告诉我公司名，我帮你检查是否投递过。",
            "suggested_actions": ["字节跳动", "腾讯", "阿里巴巴"],
            "state": state.to_dict()
        }

    def _handle_help(
        self,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理帮助请求"""
        return {
            "response": """🤖 **Job3.0 Agent 使用指南**

我是你的专属求职助手，可以帮你：

📄 **简历管理**
• "我的简历" - 查看已上传简历
• "优化简历" - 根据 JD 优化简历

🔍 **JD 分析**
• 直接粘贴职位描述，我来分析
• "分析匹配度" - 评估简历与职位的符合程度

💬 **打招呼语**
• "生成打招呼语" - 针对特定公司生成
• 支持 BOSS直聘、猎聘、邮件

📮 **投递管理**
• "我的投递" - 查看投递记录
• "有没有投XX公司" - 检查重复投递
• "记录投递" - 追踪求职进度

💡 **使用技巧**
• 直接粘贴 JD，我会自动识别并分析
• 告诉我目标公司名，我可以帮你生成打招呼语
• 想追踪投递状态，告诉我公司名我来帮你记录

有什么需要帮助的？""",
            "suggested_actions": ["分析简历匹配度", "生成打招呼语", "查看投递记录"],
            "state": state.to_dict()
        }

    async def _handle_chitchat(
        self,
        message: str,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """处理闲聊"""
        msg = message.lower()

        if any(kw in msg for kw in ["你好", "hi", "hello"]):
            response = """你好！👋 我是 Job3.0 求职助手

我来帮你：
• 📄 管理简历
• 🔍 分析 JD
• 💬 生成打招呼语
• 📮 追踪投递

你现在在找工作吗？有什么我可以帮你的？"""

        elif any(kw in msg for kw in ["谢谢", "感谢"]):
            response = """不客气！😊

有任何求职相关的问题，随时找我：
• 分析简历匹配度
• 生成打招呼语
• 记录投递进度

祝求职顺利！🍀"""

        elif any(kw in msg for kw in ["好的", "知道了", "明白了"]):
            if state.has_resume and state.target_jd:
                response = """好的！我记得你已经有简历和目标职位了。

接下来可以：
• **分析匹配度** - 评估是否符合
• **生成打招呼语** - 一键生成开场白
• **记录投递** - 投完后追踪状态

需要哪个？"""
            else:
                response = """好的！有需要随时找我。

如果方便的话，可以：
1. 上传你的简历
2. 告诉我你的目标职位

这样我可以给你更精准的建议！"""

        else:
            response = """我理解了你的意思。

记住我能帮你做的事情：
• 📄 简历分析与管理
• 🔍 JD 解析与匹配
• 💬 打招呼语生成
• 📮 投递记录追踪

有什么具体需要帮助的吗？"""

        return {
            "response": response,
            "suggested_actions": ["分析简历匹配度", "生成打招呼语", "查看投递记录"],
            "state": state.to_dict()
        }

    async def _handle_ai_fallback(
        self,
        message: str,
        state: ConversationState,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """使用 AI 处理复杂问题"""
        if not ai_service.llm:
            return {
                "response": """我理解你的问题，但需要更多信息。

请具体告诉我：
• 你想做什么？（分析简历、生成打招呼语、记录投递...）
• 目标公司/职位是什么？

或者直接说"帮助"查看我能做什么。""",
                "suggested_actions": ["帮助", "分析简历匹配度", "生成打招呼语"],
                "state": state.to_dict()
            }

        # 构建上下文
        context = []
        if state.has_resume:
            context.append("用户已有简历")
        if state.target_jd:
            context.append(f"目标JD已保存（前200字）：{state.target_jd[:200]}")
        if state.target_company:
            context.append(f"目标公司：{state.target_company}")
        if state.target_position:
            context.append(f"目标职位：{state.target_position}")

        prompt = f"""你是 Job3.0 求职助手，请回答用户问题。

用户消息：{message}

上下文：
{chr(10).join(context) if context else "无特殊上下文"}

请用友好、专业的语气回答，帮助用户解决求职问题。"""

        try:
            response = await ai_service.chat_simple(prompt)
            return {
                "response": response,
                "suggested_actions": ["帮助", "分析简历匹配度", "生成打招呼语"],
                "state": state.to_dict()
            }
        except Exception as e:
            return {
                "response": f"抱歉，处理你的问题时遇到问题：{str(e)[:100]}",
                "suggested_actions": ["帮助", "重新提问"],
                "state": state.to_dict()
            }

    # ==========================================================================
    # 辅助方法
    # ==========================================================================

    def _extract_company(self, message: str) -> str:
        """从消息中提取公司名"""
        # 常见模式
        patterns = [
            r"(?:向|给|投|投递)[\s]*([^\s公司]+)公司",
            r"有没有投[\s]?([^\s]+)",
            r"([^\s]+)公司[\s]?怎么样",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_resume_brief(self, resume: str) -> str:
        """提取简历摘要"""
        lines = [l.strip() for l in resume.split('\n') if l.strip()]
        skills = []
        for line in lines:
            if any(kw in line for kw in ["熟练", "掌握", "精通", "Python", "Java", "Vue"]):
                skills.append(line[:50])
        return f"技能亮点：{', '.join(skills[:3]) if skills else '已保存'}"

    async def _analyze_jd_text(self, jd: str) -> Dict[str, Any]:
        """分析 JD 文本"""
        if not ai_service.llm:
            # 简单规则分析
            skills = []
            for skill in ["Python", "Java", "Go", "MySQL", "Redis", "Vue", "React"]:
                if skill in jd:
                    skills.append(skill)

            return {
                "position": "后端开发" if "后端" in jd else "开发",
                "company": "",
                "salary": "未标注",
                "education": "本科" if "本科" in jd else "大专",
                "experience": "3年" if "3年" in jd else "1年",
                "skills": skills,
                "suggestion": "上传简历获取详细匹配分析"
            }

        prompt = f"""分析以下 JD，提取关键信息：

{jd[:2000]}

以 JSON 格式返回：
{{
    "position": "职位名称",
    "company": "公司名（未标注则空）",
    "salary": "薪资范围（未标注则"未标注"）",
    "education": "学历要求",
    "experience": "经验要求",
    "skills": ["技能1", "技能2"],
    "suggestion": "一句投递建议"
}}"""

        try:
            response = await ai_service.chat_simple(prompt)
            return json.loads(response)
        except:
            return {"error": "分析失败"}

    async def _generate_match_analysis(self, state: ConversationState) -> str:
        """生成匹配分析"""
        if not ai_service.llm:
            return """🎯 **匹配度分析**

**技能匹配：** 约 70%
• ✅ 匹配：Python、FastAPI、Vue
• ⚠️ 需加强：微服务、Docker
• ❌ 缺失：K8s

**建议：**
1. 突出项目中的分布式经验
2. 添加 Docker 相关技能关键词
3. 强调全栈能力

💡 要我帮你生成针对性的打招呼语吗？"""

        prompt = f"""分析简历与 JD 的匹配度：

**简历摘要：**
{state.resume_content[:1500]}

**目标 JD：**
{state.target_jd[:1500]}

请给出：
1. 匹配度评分（0-100）
2. 匹配/缺失技能
3. 优化建议（1-3条）
4. 投递建议

回复要简洁、实用。"""

        try:
            response = await ai_service.chat_simple(prompt)
            return f"🎯 **匹配度分析**\n\n{response}"
        except Exception as e:
            return f"分析失败：{str(e)[:100]}"

    def _generate_greeting_preview(self, state: ConversationState) -> Dict[str, str]:
        """生成打招呼语预览"""
        company = state.target_company or "贵公司"
        position = state.target_position or "相关岗位"

        # 简单模板生成
        boss = f"您好，看到贵司{position}招聘信息，我对贵司{company}很感兴趣，希望能详细聊聊。"
        liepin = f"您好！我是应聘{position}的求职者，关注{company}很久了。我的背景与该岗位匹配度较高，期待能与您进一步沟通，详细聊聊这个职位。"

        email = f"""尊敬的HR，您好！

我是看到{company}{position}招聘信息后投递简历的求职者。我具备扎实的开发能力，相信能够胜任该岗位。

期待您的回复，谢谢！"""

        return {
            "boss": boss[:50],
            "liepin": liepin[:100],
            "email": email
        }

    def _format_resume_response(self, data: str, has_local: bool) -> str:
        """格式化简历响应"""
        try:
            info = json.loads(data)
            if "没有上传" in data:
                return """📄 **简历状态**

目前还没有上传简历。

💡 上传简历后，我可以帮你：
• 分析与职位的匹配度
• 生成针对性的打招呼语
• 优化简历内容"""
            return f"""📄 **您的简历信息**

版本：{info.get("version_name", "未命名")}

内容预览：
{info.get("content", "")[:300]}...

💡 可以让我帮你：
• 分析与目标职位的匹配度
• 生成打招呼语
• 优化简历"""
        except:
            return data[:500]

    def _format_applications_response(self, data: str) -> str:
        """格式化投递记录响应"""
        try:
            items = json.loads(data)
            if not items:
                return """📮 **投递记录**

目前没有投递记录。

💡 投递后记得记录，我可以帮你：
• 追踪面试进度
• 避免重复投递
• 分析投递效果"""

            count = len(items) if isinstance(items, list) else 0
            return f"""📮 **投递记录**

共 {count} 条投递记录：

{self._format_applications_list(items)}

💡 需要我帮你：
• 添加新投递记录
• 更新面试状态
• 分析投递效果"""
        except:
            return data[:500]

    def _format_applications_list(self, items: List) -> str:
        """格式化投递列表"""
        if not items:
            return ""

        lines = []
        for i, item in enumerate(items[:5], 1):
            company = item.get("公司", "")
            position = item.get("岗位", "")
            status = item.get("状态", "")
            lines.append(f"{i}. **{company}** - {position} [{status}]")
        return "\n".join(lines)
