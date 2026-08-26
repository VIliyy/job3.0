# -*- coding: utf-8 -*-
"""
语音转写模块（faster-whisper）
把音频转成带时间戳的分段文本，供 LLM 总结使用

模型加载顺序：
1. 优先使用本地模型目录 <download_root>/faster-whisper-<size>/（含 model.bin）
2. 否则按 model_size 名称自动从 HuggingFace 下载（可配合 HF_ENDPOINT 镜像）
"""
import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptResult:
    language: Optional[str]
    full_text: str
    segments: List[TranscriptSegment] = field(default_factory=list)


def _resolve_device(requested: str) -> str:
    """auto 优先 cpu（Windows 上 CUDA 依赖 cuBLAS DLL，易缺失）；显式 cuda 时也先探测"""
    if requested == "cpu":
        return "cpu"
    if requested == "cuda":
        try:
            import ctranslate2
            if ctranslate2.get_cuda_device_count() > 0:
                return "cuda"
        except Exception:
            pass
        return "cpu"
    # auto
    return "cpu"


def resolve_model_path(model_size: str, download_root: Optional[str]) -> str:
    """优先返回本地模型目录路径，否则返回模型 size 名称交给 faster-whisper 在线下载"""
    if download_root:
        candidate = os.path.join(download_root, f"faster-whisper-{model_size}")
        if os.path.exists(os.path.join(candidate, "model.bin")):
            logger.info(f"使用本地模型: {candidate}")
            return candidate
    return model_size


class WhisperTranscriber:
    """基于 faster-whisper 的本地转写器（CUDA 加载失败自动回退 CPU）"""

    def __init__(self, model_size: str = "tiny", device: str = "auto", download_root: Optional[str] = None):
        self.model_size = model_size
        self.device = _resolve_device(device)
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        from faster_whisper import WhisperModel  # 延迟导入，避免后端启动变慢
        target = resolve_model_path(model_size, download_root)
        try:
            self.model = WhisperModel(
                model_size_or_path=target,
                device=self.device,
                compute_type=self.compute_type,
                download_root=download_root or None,
            )
        except Exception as exc:  # noqa: BLE001
            if self.device == "cuda":
                logger.warning(f"CUDA 加载失败（{exc}），自动回退 CPU")
                self.device = "cpu"
                self.compute_type = "int8"
                self.model = WhisperModel(
                    model_size_or_path=target,
                    device="cpu",
                    compute_type="int8",
                    download_root=download_root or None,
                )
            else:
                raise
        logger.info(f"WhisperTranscriber 就绪: model={model_size} device={self.device}")

    def transcribe(self, file_path: str) -> TranscriptResult:
        segments_raw, info = self.model.transcribe(file_path)
        segments = []
        full_text_parts = []
        for seg in segments_raw:
            text = (seg.text or "").strip()
            if not text:
                continue
            full_text_parts.append(text)
            segments.append(TranscriptSegment(start=float(seg.start), end=float(seg.end), text=text))
        return TranscriptResult(
            language=getattr(info, "language", None),
            full_text=" ".join(full_text_parts),
            segments=segments,
        )
