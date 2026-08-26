# -*- coding: utf-8 -*-
"""
Whisper 模型下载脚本（小林工具箱）
- 下载前自动检索本机是否已有模型缓存，有则跳过
- 默认从 Modelscope（国内快）下载，可切换到 hf-mirror

用法：
  python download_whisper_model.py              # 下载默认 tiny
  python download_whisper_model.py --size base   # 下载 base
  python download_whisper_model.py --mirror hf   # 使用 hf-mirror
"""
import argparse
import os
import subprocess
import sys

SIZES = ["tiny", "base", "small", "medium", "large-v3"]
MODEL_FILES = ["model.bin", "config.json", "tokenizer.json", "vocabulary.txt"]

# 常见本机缓存位置（按顺序检索）
SEARCH_DIRS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "video_notes", "models"),
    os.path.expanduser("~/.cache/huggingface/hub"),
    os.path.expanduser("~/.cache/modelscope/hub"),
    os.path.expanduser("~/.whisper"),
]


def find_local_model(size: str):
    """在常见目录中检索是否已有该 size 的模型（含 model.bin 即视为完整）"""
    for base in SEARCH_DIRS:
        for name in (f"faster-whisper-{size}", f"whisper-{size}", f"Systran--faster-whisper-{size}"):
            candidate = os.path.join(base, name)
            if os.path.exists(os.path.join(candidate, "model.bin")):
                return candidate
    return None


def main():
    parser = argparse.ArgumentParser(description="下载 faster-whisper 模型")
    parser.add_argument("--size", default="tiny", choices=SIZES)
    parser.add_argument("--mirror", default="modelscope", choices=["modelscope", "hf"])
    parser.add_argument("--out", default=SEARCH_DIRS[0], help="模型输出目录")
    args = parser.parse_args()

    out_dir = os.path.join(args.out, f"faster-whisper-{args.size}")

    # 1. 检索本机已有模型
    existing = find_local_model(args.size)
    if existing:
        print(f"[OK] 本机已存在模型，跳过下载: {existing}")
        return 0
    if os.path.exists(os.path.join(out_dir, "model.bin")):
        print(f"[OK] 目标目录已有完整模型: {out_dir}")
        return 0

    os.makedirs(out_dir, exist_ok=True)
    if args.mirror == "modelscope":
        base = f"https://modelscope.cn/models/Systran/faster-whisper-{args.size}/resolve/master"
    else:
        base = f"https://hf-mirror.com/Systran/faster-whisper-{args.size}/resolve/main"

    for f in MODEL_FILES:
        url = f"{base}/{f}"
        target = os.path.join(out_dir, f)
        if os.path.exists(target) and os.path.getsize(target) > 0:
            print(f"[skip] {f} 已存在")
            continue
        print(f"[download] {url}")
        ret = subprocess.run(["curl", "-sL", "-o", target, url], check=False)
        if ret.returncode != 0 or not os.path.exists(target):
            print(f"[ERROR] 下载失败: {f}")
            return 1
        print(f"[OK] {f} ({os.path.getsize(target)} bytes)")

    print(f"\n[完成] 模型已就绪: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
