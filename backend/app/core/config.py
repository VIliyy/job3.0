# -*- coding: utf-8 -*-
"""
小林工具箱 - 核心配置
"""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
import secrets

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )
    """应用配置"""

    # 项目基础
    APP_NAME: str = "小林工具箱"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # 数据库 - 使用SQLite（本地存储）
    DATABASE_URL: str = "sqlite:///./job3.db"

    # 文件上传
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"pdf", "doc", "docx", "mp4", "mp3", "m4a", "wav", "flv", "mov", "mkv", "webm", "aac", "flac"}

    # JWT认证（可选）
    # 生产环境请在 .env 文件中设置随机密钥
    SECRET_KEY: str = "dev-only-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 浏览器扩展桥接 Token（海投助手本地桥）：扩展请求头 X-Bridge-Token 需与之一致
    BRIDGE_TOKEN: str = "job3-bridge-local-2026"
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
    PUBLIC_UPLOADS: bool = True
    MAX_TEXT_LENGTH: int = 100_000
    MAX_JSON_BODY_SIZE: int = 1 * 1024 * 1024
    MAX_VIDEO_UPLOAD_SIZE: int = 512 * 1024 * 1024
    ENABLE_TASK_RECOVERY: bool = False

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:5174,http://localhost:5175,"
        "http://localhost:5176,http://localhost:5177,http://localhost:5178,"
        "http://localhost:5179,http://localhost:3000,"
        "http://127.0.0.1:5173,http://127.0.0.1:5175"
    )

    @property
    def cors_origins(self) -> list[str]:
        """Return the comma-separated CORS allowlist as normalized origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_runtime_security(self):
        environment = self.ENVIRONMENT.strip().lower()
        if environment in {"prod", "production"}:
            if self.DEBUG:
                raise ValueError("DEBUG must be false in production")
            if len(self.SECRET_KEY) < 32 or self.SECRET_KEY.startswith("dev-"):
                raise ValueError("SECRET_KEY must be a random value of at least 32 characters")
            if len(self.BRIDGE_TOKEN) < 24 or self.BRIDGE_TOKEN == "job3-bridge-local-2026":
                raise ValueError("BRIDGE_TOKEN must be explicitly configured in production")
            self.PUBLIC_UPLOADS = False
            self.ENABLE_TASK_RECOVERY = True
        elif not self.SECRET_KEY:
            self.SECRET_KEY = secrets.token_urlsafe(32)
        return self

settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

