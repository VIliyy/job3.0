# -*- coding: utf-8 -*-
"""
小林工具箱 - 核心配置
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置"""

    # 项目基础
    APP_NAME: str = "小林工具箱"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # 数据库 - 使用SQLite（本地存储）
    DATABASE_URL: str = "sqlite:///./job3.db"

    # 文件上传
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"pdf", "doc", "docx", "mp4", "mp3", "m4a", "wav", "flv", "mov", "mkv", "webm", "aac", "flac"}

    # JWT认证（可选）
    # 生产环境请在 .env 文件中设置随机密钥
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE-THIS-IN-PRODUCTION-USE-RANDOM-KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # DeepSeek API
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # OpenAI API（可选）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # Ollama 本地模型（可选）
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # ============ 视频笔记模块 ============
    # 视频下载/转写产物输出目录（留空自动使用 backend/data/video_notes）
    VIDEO_NOTE_DATA_DIR: str = ""
    # Whisper 模型大小: tiny / base / small / medium / large-v3（越小越快越省内存）
    WHISPER_MODEL_SIZE: str = "tiny"
    # 转写设备: auto / cpu / cuda
    WHISPER_DEVICE: str = "cpu"
    # 视频笔记使用的 LLM（优先级: LLM_* 显式配置 > OPENAI > DEEPSEEK > Ollama）
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: Optional[str] = None
    # 视频笔记任务并发数
    VIDEO_TASK_WORKERS: int = 2

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5175",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

