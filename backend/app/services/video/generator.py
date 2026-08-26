# -*- coding: utf-8 -*-
"""
视频笔记生成器：下载 → 转写 → LLM 总结 →（可选）导出 Obsidian
"""
import logging
import os
from typing import Optional

from app.core.config import settings
from app.models.video_task import VideoTask
from app.services.video.config_store import get_config
from app.services.video.downloader import VideoDownloader, detect_platform
from app.services.video.obsidian import ObsidianExporter, validate_vault
from app.services.video.summarizer import VideoSummarizer, resolve_llm_config
from app.services.video.transcriber import WhisperTranscriber

logger = logging.getLogger(__name__)


def get_data_dir() -> str:
    if settings.VIDEO_NOTE_DATA_DIR:
        base = settings.VIDEO_NOTE_DATA_DIR
    else:
        base = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            "data", "video_notes",
        )
    os.makedirs(base, exist_ok=True)
    return base


class VideoNoteGenerator:
    """串行执行完整流水线，每步更新 VideoTask 状态并落库"""

    def __init__(self, db=None):
        self.db = db

    def _set_status(self, task: VideoTask, status: str, message: str = ""):
        task.status = status
        task.status_message = message
        if self.db is not None:
            self.db.commit()

    def generate(self, task: VideoTask) -> dict:
        data_dir = get_data_dir()
        try:
            # 1. 解析平台
            platform = task.platform or "auto"
            if platform == "auto":
                platform = detect_platform(task.video_url)
            self._set_status(task, "PARSING", "解析链接")

            # 2. 下载（有字幕平台优先抓字幕是后续增强项；MVP 统一走音频）
            self._set_status(task, "DOWNLOADING", "下载音频中")
            downloader = VideoDownloader(os.path.join(data_dir, "audio"))
            result = downloader.download(task.video_url, platform)
            task.platform = platform
            task.title = result.title

            # 3. 转写
            self._set_status(task, "TRANSCRIBING", f"语音转写中（{result.title}）")
            transcriber = WhisperTranscriber(
                model_size=settings.WHISPER_MODEL_SIZE,
                device=settings.WHISPER_DEVICE,
                download_root=os.path.join(data_dir, "models"),
            )
            transcript = transcriber.transcribe(result.file_path)
            task.transcript = transcript.full_text
            if not transcript.segments:
                raise RuntimeError("转写结果为空（音频可能无人声或无有效内容）")

            # 4. LLM 总结
            self._set_status(task, "SUMMARIZING", "AI 总结中")
            api_key, base_url, model = resolve_llm_config()
            summarizer = VideoSummarizer(api_key, base_url, model)
            tags = ""
            try:
                raw_tags = result.raw_info.get("tags") or []
                tags = "、".join(raw_tags) if isinstance(raw_tags, list) else str(raw_tags or "")
            except Exception:  # noqa: BLE001
                tags = ""
            markdown = summarizer.summarize(
                title=result.title,
                tags=tags,
                segments=transcript.segments,
                style=task.style or None,
                formats=task.get_formats(),
                extras=task.extras or None,
            )
            task.markdown = markdown

            # 5. 导出 Obsidian（可选）
            if task.export_obsidian:
                self._set_status(task, "OBSIDIAN", "导出到 Obsidian 知识库")
                cfg = get_config()
                vault = cfg.get("obsidian_vault_path", "")
                valid, msg = validate_vault(vault)
                if not valid:
                    logger.warning(f"Obsidian 导出跳过: {msg}")
                    task.obsidian_message = msg
                else:
                    path = ObsidianExporter(vault).export(markdown, result.title, platform, task.video_url)
                    task.obsidian_path = path
                    task.obsidian_exported = True
                    task.obsidian_message = "已导出"

            self._set_status(task, "SUCCESS", "完成")
            return {"task_id": task.task_id, "status": task.status}
        except Exception as exc:  # noqa: BLE001
            logger.exception("视频笔记生成失败")
            task.error = str(exc)
            self._set_status(task, "FAILED", str(exc)[:500])
            return {"task_id": task.task_id, "status": task.status}
