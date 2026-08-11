# -*- coding: utf-8 -*-
import io
path = r"E:\job3.0\backend\tests\test_api.py"
src = io.open(path, encoding="utf-8").read()

anchor = '''        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data


class TestApplicationAPI:'''
addition = '''        assert response.status_code == status.HTTP_200_OK
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


class TestApplicationAPI:'''
assert anchor in src, "anchor not found"
src = src.replace(anchor, addition)
io.open(path, "w", encoding="utf-8", newline="\n").write(src)
print("TESTS ADDED")
