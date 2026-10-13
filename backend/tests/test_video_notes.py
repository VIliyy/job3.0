# -*- coding: utf-8 -*-
"""
视频笔记 API 测试（删除任务）
"""

from fastapi import status

from app.models.video_task import VideoTask


class TestVideoNotesDeleteAPI:
    """视频笔记删除任务 API 测试"""

    def test_delete_task_ok(self, client, db_session):
        """删除存在的任务"""
        db_session.add(VideoTask(
            task_id="test_delete_001",
            video_url="https://example.com/video.mp4",
            status="SUCCESS",
        ))
        db_session.commit()

        resp = client.delete("/api/video-notes/tasks/test_delete_001")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["ok"] is True

        resp = client.delete("/api/video-notes/tasks/test_delete_001")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_not_found(self, client):
        """删除不存在的任务返回 404"""
        resp = client.delete("/api/video-notes/tasks/no_such_task")
        assert resp.status_code == status.HTTP_404_NOT_FOUND