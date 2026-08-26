# -*- coding: utf-8 -*-
"""
工具箱配置存储（JSON 文件）
目前存储: Obsidian 知识库路径、视频笔记默认选项
"""
import json
import logging
import os

logger = logging.getLogger(__name__)

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# backend/data/toolbox_config.json
CONFIG_PATH = os.path.join(_BASE_DIR, "data", "toolbox_config.json")

DEFAULT_CONFIG = {
    "obsidian_vault_path": "",
    "default_style": "minimal",
    "default_export_obsidian": False,
}


def _save(data: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        _save(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"读取配置失败，使用默认值: {exc}")
        data = {}
    merged = dict(DEFAULT_CONFIG)
    merged.update(data or {})
    return merged


def set_config(patch: dict) -> dict:
    cfg = get_config()
    cfg.update(patch or {})
    _save(cfg)
    return cfg
