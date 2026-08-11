# -*- coding: utf-8 -*-
"""Job3.0 后端补丁 v2：同文件累积替换，幂等"""
import io

def read(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return f.read()

def write(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)

def apply(p, pairs):
    s = read(p)
    for i, (old, new) in enumerate(pairs):
        if old in s:
            assert s.count(old) == 1, "%s #%d count=%d" % (p, i, s.count(old))
            s = s.replace(old, new)
            print("  applied", i, "->", old[:40].replace("\n", "\\n"))
        elif new in s:
            print("  skip(already)", i)
        else:
            raise SystemExit("PATTERN MISSING in %s #%d: %r" % (p, i, old[:80]))
    write(p, s)
    print("OK:", p)

# ---------- schemas/resume.py ----------
apply(r"E:\job3.0\backend\app\schemas\resume.py", [
    ("""class ResumeBrief(BaseModel):
    id: int
    slot: int
    filename: str
    category: str
    status: str
    version_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True""",
     """class ResumeBrief(BaseModel):
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
        from_attributes = True"""),
])

# ---------- stream.py ----------
apply(r"E:\job3.0\backend\app\api\stream.py", [
    ("""    @classmethod
    async def stream_chat(
        cls,
        message: str,
        history: List[Dict] = None,
        state: Dict = None,
        stream_thinking: bool = True
    ) -> AsyncGenerator[str, None]:
        \"\"\"流式处理对话\"\"\"

        try:
            # 1. 意图识别阶段""",
     """    @staticmethod
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

            # 1. 意图识别阶段"""),
    ("""        context = []
        if state:
            if state.get("has_resume"):
                context.append("用户已有简历")
            if state.get("target_jd"):""",
     """        context = []
        if state:
            if state.get("has_resume"):
                context.append("用户已有简历")
            if state.get("resume_text"):
                context.append(f"用户简历内容如下（请基于它回答，引用其中的技能/项目/经历）:\\n{state['resume_text'][:2000]}")
            if state.get("target_jd"):"""),
])

# ---------- stream.py: _stream_match 替换为真实 AI ----------
p = r"E:\job3.0\backend\app\api\stream.py"
s = read(p)
old_match = """        # 生成结果
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
new_match = """        yield cls._event(StreamEvent.THINKING, {
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
if old_match in s:
    assert s.count(old_match) == 1
    write(p, s.replace(old_match, new_match))
    print("OK: _stream_match AI")
elif new_match in s:
    print("skip(already): _stream_match AI")
else:
    raise SystemExit("PATTERN MISSING: _stream_match")

print("\nPATCH v2 DONE")
