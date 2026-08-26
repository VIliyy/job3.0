# -*- coding: utf-8 -*-
"""
视频下载模块（小林工具箱 - 视频笔记）
支持平台: bilibili / douyin / local（本地文件）
核心工具: yt-dlp（下载 + FFmpeg 抽音频）
"""
import logging
import os
from dataclasses import dataclass, field
from typing import Optional

import yt_dlp

logger = logging.getLogger(__name__)

SUPPORTED_PLATFORMS = {"bilibili", "douyin", "local"}

# 本地音视频扩展名（上传本地文件时用于识别）
LOCAL_MEDIA_EXTS = {".mp4", ".mkv", ".flv", ".mov", ".avi", ".webm", ".mp3", ".m4a", ".wav", ".aac", ".flac", ".ogg"}


@dataclass
class DownloadResult:
    """下载结果"""
    file_path: str                 # 音频文件路径（mp3）
    video_id: str                  # 视频 ID（本地文件为文件名）
    title: str                     # 视频标题
    duration: float                # 时长（秒）
    cover_url: Optional[str] = None
    platform: str = ""
    raw_info: dict = field(default_factory=dict)
    video_path: Optional[str] = None  # 完整视频路径（暂无使用）


def detect_platform(url: str) -> str:
    """根据 URL/路径自动识别平台: bilibili / douyin / local"""
    url = str(url).strip()
    if not url:
        return "local"
    lower = url.lower()
    if lower.startswith(("http://", "https://")):
        if "bilibili.com" in lower or "b23.tv" in lower:
            return "bilibili"
        if "douyin.com" in lower or "iesdouyin.com" in lower:
            return "douyin"
        raise ValueError(f"暂不支持的链接平台: {url}")
    if os.path.exists(url) and os.path.splitext(url)[1].lower() in LOCAL_MEDIA_EXTS:
        return "local"
    raise ValueError(f"无法识别的视频地址: {url}")


class VideoDownloader:
    """统一下载器：bilibili / douyin 走 yt-dlp，local 直接使用本地文件"""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def download(self, url: str, platform: str) -> DownloadResult:
        if platform == "local":
            return self._download_local(url)
        return self._download_network(url, platform)

    # ---------- 本地文件 ----------
    def _download_local(self, file_path: str) -> DownloadResult:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"本地文件不存在: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in LOCAL_MEDIA_EXTS:
            raise ValueError(f"不支持的本地媒体格式: {ext}")
        name = os.path.basename(file_path)
        title = os.path.splitext(name)[0]
        return DownloadResult(
            file_path=os.path.abspath(file_path),
            video_id=title,
            title=title,
            duration=0.0,
            platform="local",
        )

    # ---------- 网络视频 ----------
    def _download_network(self, url: str, platform: str) -> DownloadResult:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(self.output_dir, "%(id)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "64",
                }
            ],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }
        if platform == "bilibili":
            ydl_opts["http_headers"] = {"Referer": "https://www.bilibili.com"}
        elif platform == "douyin":
            ydl_opts["http_headers"] = {"Referer": "https://www.douyin.com/"}
        # TODO(增强): B站 412 / 抖音风控时，支持配置 Cookie 后重试

        info = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True) or {}
            video_id = str(info.get("id") or "")
            title = info.get("title") or video_id
            duration = float(info.get("duration") or 0.0)
            cover_url = info.get("thumbnail")
            audio_path = os.path.join(self.output_dir, f"{video_id}.mp3")
            if not os.path.exists(audio_path):
                # 兜底：找输出目录里刚生成的文件
                candidates = [f for f in os.listdir(self.output_dir)
                              if f.startswith(str(video_id)) and f.endswith((".mp3", ".m4a", ".wav"))]
                if candidates:
                    audio_path = os.path.join(self.output_dir, sorted(candidates)[-1])
        return DownloadResult(
            file_path=audio_path,
            video_id=video_id,
            title=title,
            duration=duration,
            cover_url=cover_url,
            platform=platform,
            raw_info=info,
        )
