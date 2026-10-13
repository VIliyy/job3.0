# -*- coding: utf-8 -*-
"""Regression tests for backend hardening and operational guarantees."""

import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError


def test_video_downloader_module_is_importable_without_optional_yt_dlp():
    """Optional video dependencies must not prevent the API app from importing."""
    code = (
        "import sys; "
        "sys.modules['yt_dlp'] = None; "
        "import app.services.video.downloader"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_production_settings_reject_weak_or_missing_secrets(monkeypatch):
    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="change-this-to-a-random-secret-key",
            BRIDGE_TOKEN="job3-bridge-local-2026",
        )


def test_development_settings_keep_local_bridge_compatibility():
    from app.core.config import Settings

    settings = Settings(_env_file=None, ENVIRONMENT="development")
    assert settings.BRIDGE_TOKEN
    assert settings.cors_origins


def test_upload_filename_sanitization_never_returns_empty_name():
    from app.core.utils import sanitize_filename

    assert sanitize_filename("../../") == "upload"
    assert sanitize_filename("<>:\\") == "upload"


def test_resume_version_sets_latest_version_id(client):
    resume = client.post(
        "/api/resumes/save-text",
        params={"slot": 1},
        json={"content": "a" * 80, "category": "tech"},
    )
    assert resume.status_code == 200, resume.text
    resume_id = resume.json()["id"]

    version = client.post(
        f"/api/resumes/{resume_id}/versions",
        json={"content": "optimized content"},
    )
    assert version.status_code == 200, version.text

    detail = client.get(f"/api/resumes/{resume_id}")
    assert detail.status_code == 200, detail.text
    assert detail.json()["latest_optimized_version_id"] == version.json()["id"]


def test_security_headers_and_request_id(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_application_status_and_pagination_are_bounded(client):
    assert client.get("/api/resumes/", params={"limit": 0}).status_code == 422
    assert client.get("/api/resumes/", params={"limit": 101}).status_code == 422

    resume = client.post(
        "/api/resumes/save-text",
        params={"slot": 1},
        json={"content": "a" * 80, "category": "tech"},
    )
    assert resume.status_code == 200
    payload = {
        "resume_id": resume.json()["id"],
        "company": "测试公司",
        "position": "后端工程师",
        "status": "not-a-status",
    }
    assert client.post("/api/applications/", json=payload).status_code == 422


def test_text_payloads_have_size_limits(client):
    too_long = "x" * 100_001
    assert client.post(
        "/api/resumes/save-text",
        json={"slot": 1, "content": too_long, "category": "tech"},
    ).status_code == 422
    assert client.post(
        "/api/jd/",
        json={"raw_content": too_long},
    ).status_code == 422


def test_json_request_body_size_is_bounded(client):
    response = client.post(
        "/api/health/does-not-exist",
        content="{" + "x" * (2 * 1024 * 1024) + "}",
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 413


def test_local_video_paths_cannot_escape_upload_directory(client, tmp_path, monkeypatch):
    from app.api import video_notes

    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"not a real video")
    monkeypatch.setattr(video_notes.settings, "UPLOAD_DIR", str(tmp_path / "uploads"))
    response = client.post(
        "/api/video-notes/generate",
        json={"video_url": str(outside), "platform": "local"},
    )
    assert response.status_code == 400


def test_delete_resume_does_not_remove_file_outside_upload_directory(client, tmp_path, monkeypatch):
    from app.api import resume as resume_api

    upload_dir = tmp_path / "uploads"
    outside = tmp_path / "outside.txt"
    outside.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(resume_api.settings, "UPLOAD_DIR", str(upload_dir))

    created = client.post(
        "/api/resumes/",
        json={
            "slot": 1,
            "filename": "legacy.txt",
            "filepath": str(outside),
            "file_size": outside.stat().st_size,
            "file_type": "txt",
            "content": "legacy content",
        },
    )
    assert created.status_code == 201, created.text
    deleted = client.delete(f"/api/resumes/{created.json()['id']}")
    assert deleted.status_code == 200, deleted.text
    assert outside.exists()


def test_duplicate_application_job_url_returns_conflict(client):
    resume = client.post(
        "/api/resumes/save-text",
        params={"slot": 1},
        json={"content": "a" * 80, "category": "tech"},
    )
    assert resume.status_code == 200
    payload = {
        "resume_id": resume.json()["id"],
        "company": "测试公司",
        "position": "后端工程师",
        "job_url": "https://example.com/jobs/duplicate",
    }
    assert client.post("/api/applications/", json=payload).status_code == 201
    duplicate = client.post("/api/applications/", json=payload)
    assert duplicate.status_code == 409
