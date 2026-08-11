# -*- coding: utf-8 -*-
"""
Resume API 测试
"""

import pytest
from fastapi import status


class TestResumeAPI:
    """简历API测试"""

    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"

    def test_list_resumes_empty(self, client):
        """测试获取简历列表（空）"""
        response = client.get("/api/resumes")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_resume_not_found(self, client):
        """测试获取不存在的简历"""
        response = client.get("/api/resumes/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_resume_optimize_validation(self, client, sample_resume, sample_jd):
        """测试优化不存在的简历返回404"""
        response = client.post(
            "/api/optimize/full",
            json={
                "resume_id": 9999,
                "jd_content": sample_jd
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_resume_analyze(self, client, sample_jd):
        """测试JD分析"""
        response = client.post(
            "/api/optimize/analyze-jd",
            json={"raw_content": sample_jd}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data

    def test_save_text_category_normalization(self, client, sample_resume):
        """中文分类标签归一化为枚举值，非法值回退 other"""
        resp = client.post(
            "/api/resumes/save-text",
            json={"slot": 3, "content": sample_resume, "category": "技术", "version_name": "中文分类"}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["category"] == "tech"

        resp2 = client.post(
            "/api/resumes/save-text",
            json={"slot": 4, "content": sample_resume, "category": "不存在的分类"}
        )
        assert resp2.status_code == status.HTTP_200_OK
        assert resp2.json()["category"] == "other"

    def test_save_text_slot_out_of_range(self, client, sample_resume):
        """slot 超出 1-4 应返回 422"""
        resp = client.post(
            "/api/resumes/save-text",
            json={"slot": 0, "content": sample_resume, "category": "tech"}
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_resumes_filter_chinese_category(self, client, sample_resume):
        """列表按中文分类过滤不应 500，返回归一化枚举值"""
        client.post(
            "/api/resumes/save-text",
            json={"slot": 3, "content": sample_resume, "category": "产品"}
        )
        resp = client.get("/api/resumes", params={"category": "产品"})
        assert resp.status_code == status.HTTP_200_OK
        assert all(item["category"] == "product" for item in resp.json())


class TestApplicationAPI:
    """投递记录API测试"""

    def test_list_applications_empty(self, client):
        """测试获取投递列表（空）"""
        response = client.get("/api/applications")
        assert response.status_code == status.HTTP_200_OK

    def test_create_application(self, client, sample_resume):
        """测试创建投递记录（需关联简历）"""
        resume_resp = client.post(
            "/api/resumes/save-text",
            params={"slot": 1},
            json={"content": sample_resume, "category": "tech", "version_name": "测试简历"}
        )
        assert resume_resp.status_code == status.HTTP_200_OK
        resume_id = resume_resp.json()["id"]

        response = client.post(
            "/api/applications",
            json={
                "resume_id": resume_id,
                "company": "字节跳动",
                "position": "后端工程师",
                "status": "pending"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["company"] == "字节跳动"

    def test_create_application_validation(self, client):
        """测试创建投递记录验证"""
        # 缺少必填字段
        response = client.post(
            "/api/applications",
            json={"company": ""}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_applications_by_resume(self, client, sample_resume):
        """按简历查询投递记录"""
        resume_resp = client.post(
            "/api/resumes/save-text",
            params={"slot": 2},
            json={"content": sample_resume, "category": "tech", "version_name": "测试简历2"}
        )
        resume_id = resume_resp.json()["id"]
        client.post(
            "/api/applications",
            json={"resume_id": resume_id, "company": "测试公司", "position": "测试岗位", "status": "pending"}
        )
        response = client.get(f"/api/applications/by-resume/{resume_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1


class TestJDAPI:
    """JD分析API测试"""

    def test_parse_jd(self, client, sample_jd):
        """测试JD解析（v2）"""
        response = client.post(
            "/api/jd/",
            json={"raw_content": sample_jd}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data

    def test_parse_jd_validation(self, client):
        """测试JD解析验证（缺少必填字段）"""
        response = client.post(
            "/api/jd/",
            json={}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAgentAPI:
    """Agent API测试"""

    def test_chat_validation(self, client):
        """测试聊天验证"""
        response = client.post(
            "/api/agent/chat",
            json={"message": ""}  # 空消息
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_ai_status(self, client):
        """测试获取AI状态"""
        response = client.get("/api/ai/status")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "ai_enabled" in data
        assert "provider" in data
        assert "model" in data


class TestMatchAPI:
    """匹配分析API测试"""

    def test_match_analysis(self, client, sample_resume, sample_jd):
        """测试匹配分析"""
        response = client.post(
            "/api/match/analyze",
            json={
                "resume_text": sample_resume,
                "jd_content": sample_jd,
                "use_ai": False  # 不用AI加速测试
            }
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST
        ]

class TestOptimizeAPI:
    """一体化优化 v2.0 测试（AI 降级为规则优化，保证测试快速稳定）"""

    def _create_resume(self, client, slot, content, version_name="测试简历"):
        response = client.post(
            "/api/resumes/save-text",
            params={"slot": slot},
            json={"content": content, "category": "tech", "version_name": version_name}
        )
        assert response.status_code == status.HTTP_200_OK
        return response.json()["id"]

    def test_full_optimization_creates_version(self, client, sample_resume, sample_jd, monkeypatch):
        """一体化优化：应创建版本并更新简历状态"""
        from app.agents.base import ai_service
        monkeypatch.setattr(ai_service, "llm", None)  # 走规则降级，避免真实 AI 调用

        resume_id = self._create_resume(client, 3, sample_resume)
        response = client.post(
            "/api/optimize/full",
            json={"resume_id": resume_id, "jd_content": sample_jd, "company": "测试公司", "position": "后端工程师"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["version_id"] > 0
        assert data["version_number"] >= 1
        assert data["optimized_content"]
        assert data["original_score"] >= 0
        assert data["optimized_score"] >= data["original_score"]
        assert data["jd_analysis"]["company"] == "测试公司"
        assert data["jd_analysis"]["position"] == "后端工程师"

        # 简历状态应变为 optimized，且关联最新版本
        resume_resp = client.get(f"/api/resumes/{resume_id}")
        assert resume_resp.status_code == status.HTTP_200_OK
        resume = resume_resp.json()
        assert resume["status"] == "optimized"
        assert resume["latest_optimized_version_id"] == data["version_id"]

    def test_full_optimization_empty_content(self, client, sample_jd):
        """简历内容为空时返回 400"""
        resume_id = self._create_resume(client, 4, "", "空简历")
        response = client.post(
            "/api/optimize/full",
            json={"resume_id": resume_id, "jd_content": sample_jd}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_analyze_jd_returns_skills(self, client, sample_jd):
        """JD 分析应返回技能关键词"""
        response = client.post(
            "/api/optimize/analyze-jd",
            json={"raw_content": sample_jd}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "skills" in data

    def test_compare_after_optimization(self, client, sample_resume, sample_jd, monkeypatch):
        """优化后对比：原始内容应保留在版本中，对比有效"""
        from app.agents.base import ai_service
        monkeypatch.setattr(ai_service, "llm", None)

        resume_id = self._create_resume(client, 5, sample_resume)
        resp = client.post(
            "/api/optimize/full",
            json={"resume_id": resume_id, "jd_content": sample_jd}
        )
        assert resp.status_code == status.HTTP_200_OK
        version_id = resp.json()["version_id"]

        compare_resp = client.get(f"/api/optimize/compare/{resume_id}")
        assert compare_resp.status_code == status.HTTP_200_OK
        compare = compare_resp.json()
        assert compare["current_content"] == sample_resume
        assert compare["optimized_content"]
        assert compare["version_number"] == resp.json()["version_number"]

        # 指定版本对比
        compare2 = client.get(f"/api/optimize/compare/{resume_id}", params={"version_id": version_id})
        assert compare2.status_code == status.HTTP_200_OK
        assert compare2.json()["current_content"] == sample_resume

    def test_version_history(self, client, sample_resume, sample_jd, monkeypatch):
        """版本历史应包含优化记录"""
        from app.agents.base import ai_service
        monkeypatch.setattr(ai_service, "llm", None)

        resume_id = self._create_resume(client, 6, sample_resume)
        client.post("/api/optimize/full", json={"resume_id": resume_id, "jd_content": sample_jd})
        client.post("/api/optimize/full", json={"resume_id": resume_id, "jd_content": sample_jd})

        response = client.get(f"/api/optimize/versions/{resume_id}")
        assert response.status_code == status.HTTP_200_OK
        versions = response.json()["versions"]
        assert len(versions) == 2
        assert versions[0]["version_number"] == 2
