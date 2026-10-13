# -*- coding: utf-8 -*-
"""
求职助手聊天历史 API 测试
"""

from fastapi import status


class TestAgentHistoryAPI:
    """求职助手聊天历史 API 测试"""

    def test_save_and_get_chat(self, client):
        """新建会话并读取"""
        resp = client.post("/api/agent/history", json={
            "title": "分析 JD",
            "messages": [
                {"role": "user", "content": "帮我分析 JD", "time": "10:00:00", "actions": []},
                {"role": "bot", "content": "好的", "time": "10:00:01", "actions": ["继续"]},
            ],
        })
        assert resp.status_code == status.HTTP_200_OK
        chat = resp.json()
        assert chat["chat_id"]
        assert chat["message_count"] == 2

        detail = client.get("/api/agent/history/" + chat["chat_id"])
        assert detail.status_code == status.HTTP_200_OK
        data = detail.json()
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "帮我分析 JD"

    def test_save_updates_existing_chat(self, client):
        """同 chat_id 保存是更新而非新增"""
        resp = client.post("/api/agent/history", json={
            "chat_id": "chat_fixed_001",
            "messages": [{"role": "user", "content": "a"}],
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["message_count"] == 1

        resp = client.post("/api/agent/history", json={
            "chat_id": "chat_fixed_001",
            "messages": [{"role": "user", "content": "a"}, {"role": "bot", "content": "b"}],
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["message_count"] == 2

        lst = client.get("/api/agent/history").json()
        assert len(lst) == 1

    def test_list_and_clear(self, client):
        """列表与清空全部"""
        client.post("/api/agent/history", json={"messages": [{"role": "user", "content": "x"}]})
        lst = client.get("/api/agent/history").json()
        assert len(lst) == 1
        assert lst[0]["message_count"] == 1

        resp = client.delete("/api/agent/history")
        assert resp.status_code == status.HTTP_200_OK
        assert client.get("/api/agent/history").json() == []

    def test_delete_single_chat(self, client):
        """删除单个会话"""
        chat = client.post("/api/agent/history", json={
            "messages": [{"role": "user", "content": "x"}]
        }).json()
        resp = client.delete("/api/agent/history/" + chat["chat_id"])
        assert resp.status_code == status.HTTP_200_OK

        resp = client.delete("/api/agent/history/" + chat["chat_id"])
        assert resp.status_code == status.HTTP_404_NOT_FOUND