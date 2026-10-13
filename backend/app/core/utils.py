"""Shared input validation helpers used by upload and text APIs."""

import re
import os
from pathlib import Path


ALLOWED_FILE_TYPES = {
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_EXTENSIONS = set(ALLOWED_FILE_TYPES)
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_file_type(filename: str | None) -> bool:
    if not filename:
        return False
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return extension in ALLOWED_EXTENSIONS


def validate_file_size(size: int) -> bool:
    return 0 < size <= MAX_FILE_SIZE


def sanitize_filename(filename: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00]', "", filename).strip()
    cleaned = cleaned.strip(".")
    if not cleaned:
        return "upload"
    if len(cleaned) > 255:
        name, extension = cleaned.rsplit(".", 1) if "." in cleaned else (cleaned, "")
        cleaned = name[: 255 - len(extension) - 1] + "." + extension if extension else name[:255]
    return cleaned


def validate_slot(slot: int) -> bool:
    return 1 <= slot <= 4


def validate_content_length(content: str, max_length: int = 50000) -> bool:
    return len(content) <= max_length


def resolve_within_directory(path: str, directory: str) -> Path:
    """Resolve a user-provided path and require it to stay below a root."""
    root = Path(directory).expanduser().resolve()
    candidate = Path(path).expanduser().resolve(strict=False)
    if candidate == root or root not in candidate.parents:
        raise ValueError("path must stay inside the configured directory")
    return candidate


async def save_upload_file(upload_file, destination: str, max_size: int, chunk_size: int = 1024 * 1024) -> int:
    """Stream an UploadFile to disk and atomically publish it after size checks."""
    if max_size <= 0:
        raise ValueError("max_size must be positive")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.part")
    total = 0
    try:
        with temporary.open("wb") as output:
            while True:
                chunk = await upload_file.read(chunk_size)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_size:
                    raise ValueError("uploaded file exceeds the configured size limit")
                output.write(chunk)
        os.replace(temporary, target)
        return total
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        finally:
            raise
