# -*- coding: utf-8 -*-
"""
提示词工程（视频笔记模块）
参考 BiliNote 的 prompt 设计：基础提示词 + 格式指令 + 风格指令 + 合并指令
"""

BASE_PROMPT = """你是一个专业的笔记助手，擅长将视频转录内容整理成清晰、有条理且信息丰富的笔记。

语言要求：
- 笔记必须使用 **中文** 撰写。
- 专有名词、技术术语、品牌名称和人名应适当保留 **英文**。

视频标题：
{video_title}

视频标签：
{tags}

视频分段（格式：开始时间 - 内容）：
---
{segment_text}
---

你的任务：
根据上面的分段转录内容，生成结构化的 Markdown 笔记，遵循以下原则：
1. **完整信息**：记录尽可能多的相关细节，确保内容全面。
2. **去除无关内容**：省略广告、填充词、问候语和不相关的言论。
3. **保留关键细节**：保留重要事实、示例、结论和建议。
4. **可读布局**：必要时使用项目符号，并保持段落简短，增强可读性。
5. 视频中提及的数学公式必须保留，并以 LaTeX 语法形式呈现。
6. 仅返回 Markdown 内容，不要用代码块包裹输出，不要输出\"以下是笔记\"之类的开场白。

额外任务如下（每一个都必须严格完成）：
"""

STYLE_MAP = {
    "minimal": "1. **精简信息**: 仅记录最重要的内容，简洁明了。",
    "detailed": "2. **详细记录**: 包含完整的内容和每个部分的详细讨论，尽量详尽的笔记。",
    "tutorial": "3. **教程笔记**: 尽可能详细记录教程，特别是关键步骤、命令和重要结论。",
    "academic": "4. **学术风格**: 适合学术报告，正式且结构化。",
    "meeting_minutes": "5. **会议纪要**: 包含议题、结论和待办事项。",
    "xiaohongshu": "6. **小红书风格**: 活泼、有感染力，使用 emoji 和爆款标题写法，适合分享。",
    "summary": "7. **极简总结**: 只输出 200 字以内的核心要点，去掉细节。",
}

FORMAT_MAP = {
    "toc": "8. **目录**: 在笔记开头自动生成基于 `##` 级标题的目录。",
    "link": "9. **原片跳转**: 为每个主要章节标题追加起始时间戳，格式 `*Content-[mm:ss]`，标记放在标题之后。",
    "summary": "10. **AI总结**: 在笔记末尾加入简短的 AI 总结，使用二级标题 `## AI 总结`。",
}

MERGE_PROMPT = """你将收到多个来自同一视频的 Markdown 笔记片段，请合并成一份完整笔记：
- 只做合并与去重，不要发明新内容
- 保持原有标题层级与 Markdown 结构
- 保留所有 *Content-[mm:ss] 标记
- 保持中文输出，专有名词保留英文
- 不要使用代码块包裹输出
"""


def build_prompt(title: str, tags: str, segment_text: str, style: str = None,
                 formats: list = None, extras: str = None) -> str:
    prompt = BASE_PROMPT.format(video_title=title, tags=tags, segment_text=segment_text)
    if formats:
        prompt += "\n" + "\n".join(FORMAT_MAP.get(f, "") for f in formats if f in FORMAT_MAP)
    if style and style in STYLE_MAP:
        prompt += "\n" + STYLE_MAP[style]
    if extras and str(extras).strip():
        prompt += f"\n额外要求：{extras}"
    return prompt
