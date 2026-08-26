# -*- coding: utf-8 -*-
"""
LLM 总结模块（分块 + 合并）
支持任意 OpenAI 兼容接口（OpenAI / DeepSeek / Ollama / 自定义）
"""
import json
import logging
import os
import time
from typing import List

from openai import OpenAI

from app.core.config import settings
from app.services.video.prompts import build_prompt, MERGE_PROMPT
from app.services.video.transcriber import TranscriptSegment

logger = logging.getLogger(__name__)

MAX_REQUEST_BYTES = int(os.getenv("VIDEO_LLM_MAX_BYTES", str(45 * 1024 * 1024)))


def resolve_llm_config():
    """按优先级返回 (api_key, base_url, model)。未配置任何 Key 时抛错。"""
    if settings.LLM_API_KEY:
        return (
            settings.LLM_API_KEY,
            settings.LLM_BASE_URL or "https://api.openai.com/v1",
            settings.LLM_MODEL or "gpt-4o-mini",
        )
    if settings.OPENAI_API_KEY:
        return settings.OPENAI_API_KEY, "https://api.openai.com/v1", settings.OPENAI_MODEL
    if settings.DEEPSEEK_API_KEY:
        return settings.DEEPSEEK_API_KEY, "https://api.deepseek.com/v1", settings.DEEPSEEK_MODEL
    if settings.OLLAMA_BASE_URL:
        return "ollama", f"{settings.OLLAMA_BASE_URL}/v1", settings.OLLAMA_MODEL
    raise ValueError("未配置任何 LLM（请在 .env 中设置 DEEPSEEK_API_KEY / OPENAI_API_KEY / LLM_API_KEY）")


def _fmt_time(seconds: float) -> str:
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _segment_text(segments: List[TranscriptSegment]) -> str:
    return "\n".join(f"{_fmt_time(s.start)} - {s.text.strip()}" for s in segments)


class VideoSummarizer:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=180)
        self.model = model

    # ---------- 分块 ----------
    def _chunk(self, segments: List[TranscriptSegment]) -> List[List[TranscriptSegment]]:
        chunks, current = [], []
        for seg in segments:
            candidate = current + [seg]
            if self._estimate(candidate) <= MAX_REQUEST_BYTES:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = [seg]
        if current:
            chunks.append(current)
        return chunks or [[]]

    @staticmethod
    def _estimate(segments: List[TranscriptSegment]) -> int:
        payload = json.dumps([{"text": s.text} for s in segments], ensure_ascii=False).encode("utf-8")
        return len(payload)

    # ---------- 调用 ----------
    def _chat(self, messages: list, max_retries: int = 2) -> str:
        last_err = None
        for attempt in range(max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                )
                return resp.choices[0].message.content or ""
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                logger.warning(f"LLM 调用失败(第{attempt + 1}次): {exc}")
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"LLM 调用失败: {last_err}")

    # ---------- 主流程 ----------
    def summarize(self, title: str, tags: str, segments: List[TranscriptSegment],
                  style: str = None, formats: list = None, extras: str = None) -> str:
        chunks = self._chunk(segments)
        partials = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"LLM 总结分块 {i}/{len(chunks)}（{len(chunk)} 段）")
            prompt = build_prompt(title, tags, _segment_text(chunk), style, formats, extras)
            partials.append(self._chat([{"role": "user", "content": prompt}]))

        if len(partials) == 1:
            return partials[0]
        merged = self._chat([{
            "role": "user",
            "content": MERGE_PROMPT + "\n\n" + "\n\n---\n\n".join(partials),
        }])
        return merged
