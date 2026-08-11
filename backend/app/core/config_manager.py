# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 配置管理服务

处理 API Key 等敏感配置的持久化
"""

import os
from typing import Dict, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器 - 处理 API Key 持久化"""

    def __init__(self, env_file: str = None):
        if env_file is None:
            # 默认使用 backend/.env
            self.env_file = Path(__file__).parent.parent.parent / ".env"
        else:
            self.env_file = Path(env_file)

        # 确保 .env 文件存在
        if not self.env_file.exists():
            self.env_file.touch()

    def get(self, key: str, default: str = None) -> Optional[str]:
        """读取配置"""
        return self._read_env().get(key, default)

    def set(self, key: str, value: str) -> bool:
        """保存配置到 .env 文件"""
        env_data = self._read_env()
        env_data[key] = value
        return self._write_env(env_data)

    def delete(self, key: str) -> bool:
        """删除配置"""
        env_data = self._read_env()
        if key in env_data:
            del env_data[key]
            return self._write_env(env_data)
        return True

    def _read_env(self) -> Dict[str, str]:
        """读取 .env 文件内容"""
        env_data = {}
        if self.env_file.exists():
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_data[key.strip()] = value.strip()
        return env_data

    def _write_env(self, env_data: Dict[str, str]) -> bool:
        """写入 .env 文件"""
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write("# Job3.0 配置文件\n")
                f.write("# 注意：请勿将此文件分享给他人或提交到版本控制\n\n")

                for key, value in env_data.items():
                    # 不写入注释行的 key
                    if key and value is not None:
                        f.write(f"{key}={value}\n")

            return True
        except Exception as e:
            print(f"写入配置失败: {e}")
            return False

    def get_api_key(self, provider: str = "deepseek") -> Optional[str]:
        """获取 API Key"""
        key_map = {
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY"
        }
        key_name = key_map.get(provider.lower(), provider.upper() + "_API_KEY")
        return self.get(key_name)

    def set_api_key(self, provider: str, api_key: str, model: str = None) -> bool:
        """保存 API Key"""
        key_map = {
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY"
        }
        key_name = key_map.get(provider.lower(), provider.upper() + "_API_KEY")

        success = self.set(key_name, api_key)

        # 同时保存模型名称
        if model and success:
            model_key = key_name.replace("API_KEY", "MODEL")
            self.set(model_key, model)

        return success


# 全局配置管理器实例
config_manager = ConfigManager()
