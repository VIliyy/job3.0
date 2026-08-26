# -*- coding: utf-8 -*-
"""
Obsidian 知识库输出模块
把精炼后的 Markdown 笔记写入本地 Obsidian Vault
"""
import logging
import os
import re
from datetime import datetime

logger = logging.getLogger(__name__)

DEFAULT_NOTE_FOLDER = "视频笔记"


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', "_", name or "").strip()
    name = re.sub(r"\s+", " ", name)
    return name[:80] or "未命名笔记"


def validate_vault(vault_path: str):
    """校验路径是否为 Obsidian 库：目录存在且包含 .obsidian 目录（弱校验）"""
    if not vault_path or not vault_path.strip():
        return False, "未配置 Obsidian 知识库路径"
    path = vault_path.strip().strip('"')
    if not os.path.isdir(path):
        return False, f"路径不存在: {path}"
    return True, "OK"


class ObsidianExporter:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path.strip().strip('"')

    def export(self, markdown: str, title: str, platform: str, video_url: str) -> str:
        valid, msg = validate_vault(self.vault_path)
        if not valid:
            raise ValueError(msg)
        folder = os.path.join(self.vault_path, DEFAULT_NOTE_FOLDER)
        os.makedirs(folder, exist_ok=True)
        now = datetime.now()
        filename = f"{now:%Y%m%d-%H%M%S} {sanitize_filename(title)}.md"
        filepath = os.path.join(folder, filename)
        frontmatter = (
            "---\n"
            f"来源: {video_url}\n"
            f"平台: {platform}\n"
            f"日期: {now:%Y-%m-%d %H:%M}\n"
            "tags: [视频笔记]\n"
            "---\n\n"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter + markdown)
        logger.info(f"已导出到 Obsidian: {filepath}")
        return filepath
