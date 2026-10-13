# -*- coding: utf-8 -*-
"""
控制台聚合统计 API 测试（2026-09-02）
"""

from datetime import date, datetime, timedelta, timezone


def _today_local():
    return datetime.now().astimezone().date()


def _create_resume(client, slot, version_name="测试简历"):
    resp = client.post(
        "/api/resumes/save-text",
        params={"slot": slot},
        json={"content": "测试内容", "category": "tech", "version_name": version_name},
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def _create_version(client, resume_id, score):
    resp = client.post(
        f"/api/resumes/{resume_id}/versions",
        json={"content": "优化后内容", "optimization_score": score},
    )
    assert resp.status_code == 200
    return resp.json()


def _create_application(client, resume_id, company, position, status="pending"):
    resp = client.post(
        "/api/applications",
        json={"resume_id": resume_id, "company": company, "position": position, "status": status},
    )
    assert resp.status_code == 201
    return resp.json()


class TestDashboardStats:
    def test_stats_empty_db(self, client):
        """空库返回零值结构与完整趋势占位"""
        resp = client.get("/api/dashboard/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["resume_count"] == 0
        assert data["stats"]["application_count"] == 0
        assert data["stats"]["optimization_count"] == 0
        assert data["stats"]["avg_score"] is None
        assert data["funnel"]["pending"] == 0
        assert len(data["trend"]) == 7
        assert data["recent_optimizations"] == []
        assert data["recent_applications"] == []

    def test_stats_aggregates_and_funnel(self, client, sample_resume):
        """简历/版本/投递聚合到统计卡片与漏斗"""
        resume_id = _create_resume(client, 1, "前端简历")
        _create_version(client, resume_id, 88)
        _create_version(client, resume_id, 75)
        _create_application(client, resume_id, "字节跳动", "前端工程师", "pending")
        _create_application(client, resume_id, "腾讯", "前端工程师", "interview")

        resp = client.get("/api/dashboard/stats")
        assert resp.status_code == 200
        data = resp.json()
        stats = data["stats"]
        assert stats["resume_count"] == 1
        assert stats["application_count"] == 2
        assert stats["applications_this_week"] == 2
        assert stats["optimization_count"] == 2
        # 平均分只取最新一次有分数的版本（同秒插入时按 id 倒序取 75）
        assert stats["avg_score"] == 75
        assert data["funnel"]["pending"] == 1
        assert data["funnel"]["interview"] == 1
        assert data["funnel"]["offer"] == 0

    def test_stats_recent_lists_and_trend(self, client):
        """最近列表排序 + 趋势按日归桶"""
        resume_id = _create_resume(client, 1, "后端简历")
        _create_version(client, resume_id, 90)
        _create_application(client, resume_id, "测试公司", "后端岗位", "offer")

        resp = client.get("/api/dashboard/stats", params={"days": 30})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["trend"]) == 30
        assert len(data["recent_optimizations"]) == 1
        assert data["recent_optimizations"][0]["title"] == "后端简历"
        assert data["recent_optimizations"][0]["score"] == 90
        assert data["recent_applications"][0]["company"] == "测试公司"
        assert data["recent_applications"][0]["status"] == "offer"

        today = _today_local().isoformat()
        today_entry = next(item for item in data["trend"] if item["date"] == today)
        assert today_entry["optimizations"] == 1
        assert today_entry["applications"] == 1

    def test_stats_days_validation(self, client):
        """days 超出 7-90 应 422"""
        resp = client.get("/api/dashboard/stats", params={"days": 6})
        assert resp.status_code == 422
        resp = client.get("/api/dashboard/stats", params={"days": 91})
        assert resp.status_code == 422