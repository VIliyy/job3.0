# -*- coding: utf-8 -*-
"""Job3.0 后端补丁：名称/内容/对比/删除/助手简历知识 相关修复"""
import io

def read(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return f.read()

def write(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)

def replace_once(p, old, new, cnt=1):
    s = read(p)
    assert s.count(old) == cnt, "%s pattern count=%d (expect %d): %r" % (p, s.count(old), cnt, old[:60])
    write(p, s.replace(old, new))
    print("OK:", p, "-", old[:50].replace("\n", "\\n"))

# ---------- 1. analyzer.py: quick_extract 占位符清理 ----------
p = r"E:\job3.0\backend\app\agents\analyzer.py"
s = read(p)
old = """        return {
            "company": company or "未知",
            "position": position or "未知",
            "salary_range": salary or "面议","""
new = """        # 过滤占位符/无意义值（如 "未知"、"【岗位】xxx"），解析不到时返回 None
        def _clean_value(value):
            if not value:
                return None
            value = re.sub(r'^【[^】]*】', '', value).strip(' :：,，。').strip()
            if not value:
                return None
            if re.fullmatch(r'(未知|待定|暂无|无|未填写|岗位|职位|n/?a)', value, re.IGNORECASE):
                return None
            return value

        company = _clean_value(company)
        position = _clean_value(position)

        return {
            "company": company,
            "position": position,
            "salary_range": salary or "面议","""
assert s.count(old) == 1, "analyzer pattern"
write(p, s.replace(old, new))
print("OK: analyzer.py")

# ---------- 2. optimize.py: version_name 不再写"JD-岗位"占位 ----------
p = r"E:\job3.0\backend\app\api\optimize.py"
s = read(p)
old = """        resume.version_name = f"{jd_company or 'JD'}-{jd_position or '岗位'}\""""
new = """        if jd_company and jd_position:
            resume.version_name = f"{jd_company}-{jd_position}"
        else:
            resume.version_name = resume.version_name or resume.filename"""
assert s.count(old) == 1, "optimize pattern"
write(p, s.replace(old, new))
print("OK: optimize.py")

# ---------- 3. schemas/resume.py: 列表接口补全字段 ----------
p = r"E:\job3.0\backend\app\schemas\resume.py"
s = read(p)
old = """class ResumeBrief(BaseModel):
    id: int
    slot: int
    filename: str
    category: str
    status: str
    version_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True"""
new = """class ResumeBrief(BaseModel):
    id: int
    slot: int
    filename: str
    category: str
    status: str
    version_name: Optional[str] = None
    content: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = 0
    is_active: bool = False
    current_jd_id: Optional[int] = None
    latest_optimized_version_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True"""
assert s.count(old) == 1, "brief pattern"
write(p, s.replace(old, new))
print("OK: ResumeBrief")

old = """class ResumeVersionResponse(BaseModel):
    id: int
    resume_id: int
    version_number: int
    version_name: Optional[str] = None
    content: Optional[str] = None"""
new = """class ResumeVersionResponse(BaseModel):
    id: int
    resume_id: int
    version_number: int
    version_name: Optional[str] = None
    original_content: Optional[str] = None
    content: Optional[str] = None"""
assert s.count(old) == 1, "version pattern"
write(p, s.replace(old, new))
print("OK: ResumeVersionResponse")

# ---------- 4. stream.py: 自动加载简历知识 ----------
p = r"E:\job3.0\backend\app\api\stream.py"
s = read(p)
old = """    @classmethod
    async def stream_chat(
        cls,
        message: str,
        history: List[Dict] = None,
        state: Dict = None,
        stream_thinking: bool = True
    ) -> AsyncGenerator[str, None]:
        \"\"\"流式处理对话\"\"\"

        try:
            # 1. 意图识别阶段"""
new = """    @staticmethod
    def _load_resume_text(db: Session) -> Optional[str]:
        \"\"\"从数据库加载最新简历内容，作为助手知识\"\"\"
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
        \"\"\"流式处理对话\"\"\"

        try:
            # 0. 注入简历知识（优先前端传入，其次数据库最新简历）
            state = dict(state or {})
            resume_text = state.get("resume_text")
            if not resume_text and db is not None:
                resume_text = cls._load_resume_text(db)
            if resume_text:
                state["resume_text"] = resume_text
                state["has_resume"] = True

            # 1. 意图识别阶段"""
assert s.count(old) == 1, "stream_chat pattern"
write(p, s.replace(old, new))
print("OK: stream_chat cls")

old = """        context = []
        if state:
            if state.get("has_resume"):
                context.append("用户已有简历")
            if state.get("target_jd"):"""
new = """        context = []
        if state:
            if state.get("has_resume"):
                context.append("用户已有简历")
            if state.get("resume_text"):
                context.append(f"用户简历内容如下（请基于它回答，引用其中的技能/项目/经历）:\\n{state['resume_text'][:2000]}")
            if state.get("target_jd"):"""
assert s.count(old) == 1, "general context pattern"
write(p, s.replace(old, new))
print("OK: _stream_general context")

# _stream_match 替换为真实 AI 分析
old = """        # 生成结果
        response = \"\"\"🎯 **匹配度分析结果**

**技能匹配：** 约 75%
- ✅ 匹配：Python、FastAPI、Vue、MySQL
- ⚠️ 需加强：微服务架构、Docker
- ❌ 缺失：K8s 经验

**建议：**
1. 突出项目中的分布式经验
2. 强调全栈能力
3. 补充 Docker 相关描述

💡 要我帮你生成针对性的打招呼语吗？\"\"\"

        # 流式输出内容
        for char in response:
            yield cls._event(StreamEvent.CONTENT, {"char": char})
            await asyncio.sleep(0.01)

        # 建议操作
        yield cls._event(StreamEvent.ACTION, {
            "actions": ["生成打招呼语", "优化简历", "查看投递记录"]
        })"""
new = """        yield cls._event(StreamEvent.THINKING, {
            "phase": "generate",
            "text": "AI 正在计算匹配度并给出建议...",
            "progress": 80
        })
        await asyncio.sleep(0.3)

        # 基于简历 + JD 的真实 AI 分析
        resume_text = (state or {}).get("resume_text", "")
        prompt = f\"\"\"你是 Job3.0 求职助手，负责简历与 JD 的匹配度分析。

用户消息：{message}
用户简历：
{resume_text[:2000] if resume_text else '（用户暂未上传简历，请引导其上传）'}

请输出：
1. 综合匹配度评分（0-100）
2. 技能匹配清单（✅ 匹配 / ⚠️ 部分匹配 / ❌ 缺失）
3. 3 条最具体的优化建议（结合简历实际内容）

用 Markdown 友好排版。\"\"\"

        if ai_service.llm:
            try:
                response = await ai_service.chat_simple(prompt)
            except Exception as e:
                response = f\"抱歉，匹配分析时遇到错误：{str(e)[:100]}\"
        else:
            response = "（AI 未配置，暂时无法做深度匹配分析，请先到设置页配置 AI 服务）"

        for char in response:
            yield cls._event(StreamEvent.CONTENT, {"char": char})
            await asyncio.sleep(0.008)

        # 建议操作
        yield cls._event(StreamEvent.ACTION, {
            "actions": ["生成打招呼语", "优化简历", "查看投递记录"]
        })"""
assert s.count(old) == 1, "match body pattern"
write(p, s.replace(old, new))
print("OK: _stream_match AI")

old = """@router.post("/stream")
async def stream_chat(request: StreamChatRequest):
    \"\"\"
    流式对话接口

    使用 SSE 协议，支持：
    - 思考过程实时展示
    - Agent 状态可视化
    - 内容流式输出
    \"\"\"
    return StreamingResponse(
        AgentStreamService.stream_chat(
            message=request.message,
            history=request.history,
            state=request.state,
            stream_thinking=request.stream_thinking
        ),"""
new = """@router.post("/stream")
async def stream_chat(request: StreamChatRequest, db: Session = Depends(get_db)):
    \"\"\"
    流式对话接口

    使用 SSE 协议，支持：
    - 思考过程实时展示
    - Agent 状态可视化
    - 内容流式输出
    \"\"\"
    return StreamingResponse(
        AgentStreamService.stream_chat(
            message=request.message,
            history=request.history,
            state=request.state,
            stream_thinking=request.stream_thinking,
            db=db
        ),"""
assert s.count(old) == 1, "route pattern"
write(p, s.replace(old, new))
print("OK: /stream route")

# ---------- 5. agent.py: fallback 也注入简历知识 ----------
p = r"E:\job3.0\backend\app\api\agent.py"
s = read(p)
old = """    service = AgentService(db)
    result = await service.chat(
        message=request.message,
        history=request.history,
        state=request.state
    )"""
new = """    state = request.state or {}
    if not state.get("resume_text"):
        from app.models.resume import Resume
        resume = db.query(Resume).filter(Resume.content.isnot(None), Resume.content != "").order_by(Resume.updated_at.desc()).first()
        if resume and resume.content:
            state = {**state, "resume_text": resume.content, "has_resume": True}

    service = AgentService(db)
    result = await service.chat(
        message=request.message,
        history=request.history,
        state=state
    )"""
assert s.count(old) == 1, "agent chat pattern"
write(p, s.replace(old, new))
print("OK: agent.py chat")

# ---------- 6. smart_agent.py: 桥接 resume_text -> resume_content ----------
p = r"E:\job3.0\backend\app\agents\smart_agent.py"
s = read(p)
old = """        conversation_state = ConversationState.from_dict(state) if state else ConversationState()"""
new = """        conversation_state = ConversationState.from_dict(state) if state else ConversationState()
        # 桥接后端自动注入的简历知识（resume_text → resume_content）
        if state and state.get("resume_text") and not conversation_state.resume_content:
            conversation_state.has_resume = True
            conversation_state.resume_content = state["resume_text"]"""
assert s.count(old) == 1, "smart_agent pattern"
write(p, s.replace(old, new))
print("OK: smart_agent.py")

print("\nALL BACKEND PATCHES DONE")
