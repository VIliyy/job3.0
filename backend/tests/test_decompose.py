# -*- coding: utf-8 -*-
"""
信息拆解 API 测试（规则引擎，不依赖 LLM）

覆盖：创建 → 闸门A/B/C 确认 → DONE → 导出 / 重生成版本+1 / 失败重试 / 非法操作
"""

import time

import pytest
from fastapi import status


def wait_until(client, task_id, target_state, timeout=8.0):
    """轮询任务直到到达目标状态（后台编排是异步任务）"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = client.get(f"/api/decompose/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        if data["state"] == target_state:
            return data
        if data["state"] == "FAILED":
            return data
        time.sleep(0.15)
    raise AssertionError(f"任务 {task_id} 未在 {timeout}s 内到达 {target_state}（当前 {data['state']}）")


class TestDecomposeAPI:
    """信息拆解 API 测试"""

    SAMPLE = "要求 3 年 Python 经验。价格 39.99 美元。评分 4.5 星。有海外仓。支持 7 天无理由退货。"

    def test_full_flow(self, client):
        """正常流程：创建 → 三道闸门 → DONE → 导出"""
        response = client.post("/api/decompose/tasks", json={
            "content": self.SAMPLE,
            "target": "评估产品可行性",
        })
        assert response.status_code == 201
        task = response.json()
        task_id = task["id"]

        # S0 → 闸门A
        task = wait_until(client, task_id, "BRIEF_REVIEW")
        s0 = task["contracts"]["S0"]
        assert s0["status"] == "needs_human"
        assert "评估产品可行性" in s0["inferences"][0]["content"]
        assert task["gates"]["A"]["state"] == "pending"

        # 确认闸门A → S1 → 闸门B
        response = client.post(f"/api/decompose/gates/{task_id}-A/decide", json={"action": "approve"})
        assert response.status_code == 200
        task = wait_until(client, task_id, "FACTS_REVIEW")
        s1 = task["contracts"]["S1"]
        assert len(s1["facts"]) > 0
        assert all(f["anchor"] for f in s1["facts"])
        assert task["gates"]["A"]["state"] == "approved"
        assert task["gates"]["B"]["state"] == "pending"

        # 确认闸门B → S2 → 闸门C
        response = client.post(f"/api/decompose/gates/{task_id}-B/decide", json={"action": "approve"})
        assert response.status_code == 200
        task = wait_until(client, task_id, "INSIGHT_REVIEW")
        s2 = task["contracts"]["S2"]
        assert len(s2["inferences"]) > 0
        # 结论必须引用事实
        usp = next(i for i in s2["inferences"] if i["type"] == "usp")
        assert usp["evidence"]

        # 确认闸门C → S3 → DONE
        response = client.post(f"/api/decompose/gates/{task_id}-C/decide", json={"action": "approve"})
        assert response.status_code == 200
        task = wait_until(client, task_id, "DONE")
        assert "S3" in task["contracts"]
        assert task["gates"]["C"]["state"] == "approved"

        # 导出
        response = client.post(f"/api/decompose/tasks/{task_id}/export")
        assert response.status_code == 200
        data = response.json()
        assert "信息拆解报告" in data["markdown"]
        assert "F-001" in data["markdown"]

    def test_regenerate_version_bump(self, client):
        """闸门B 重生成：任务 version+1，下游契约失效"""
        response = client.post("/api/decompose/tasks", json={"content": self.SAMPLE})
        task_id = response.json()["id"]

        task = wait_until(client, task_id, "BRIEF_REVIEW")
        client.post(f"/api/decompose/gates/{task_id}-A/decide", json={"action": "approve"})
        task = wait_until(client, task_id, "FACTS_REVIEW")
        version_before = task["version"]

        response = client.post(
            f"/api/decompose/gates/{task_id}-B/decide",
            json={"action": "regenerate", "note": "第三条事实不准确"},
        )
        assert response.status_code == 200
        task = wait_until(client, task_id, "FACTS_REVIEW")
        assert task["version"] == version_before + 1
        assert "S2" not in task["contracts"]  # 下游失效
        assert task["gates"]["B"]["note"] == "第三条事实不准确"

        # 重生成后可正常确认继续
        client.post(f"/api/decompose/gates/{task_id}-B/decide", json={"action": "approve"})
        task = wait_until(client, task_id, "INSIGHT_REVIEW")
        assert task["contracts"]["S2"]

    def test_fail_then_retry(self, client, monkeypatch):
        """失败场景：S1 报错 → FAILED → rerun 重试成功"""
        from app.services import decompose_service

        original_generate_s1 = decompose_service.engine.generate_s1
        calls = 0

        async def fail_once(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("test-injected transient failure")
            return await original_generate_s1(*args, **kwargs)

        monkeypatch.setattr(decompose_service.engine, "generate_s1", fail_once)
        response = client.post("/api/decompose/tasks", json={"content": "任意材料内容。"})
        task_id = response.json()["id"]

        task = wait_until(client, task_id, "BRIEF_REVIEW")
        client.post(f"/api/decompose/gates/{task_id}-A/decide", json={"action": "approve"})
        task = wait_until(client, task_id, "FAILED")
        assert "test-injected transient failure" in task["error"]

        response = client.post(f"/api/decompose/tasks/{task_id}/rerun", json={"from_stage": "S0"})
        assert response.status_code == 200
        task = wait_until(client, task_id, "BRIEF_REVIEW")
        client.post(f"/api/decompose/gates/{task_id}-A/decide", json={"action": "approve"})
        task = wait_until(client, task_id, "FACTS_REVIEW")
        assert task["state"] == "FACTS_REVIEW"

    def test_api_ignores_legacy_failure_demo_scenario(self, client):
        """旧版客户端传 scenario=fail 时，真实 API 不应注入故障。"""
        response = client.post("/api/decompose/tasks", json={
            "content": self.SAMPLE,
            "scenario": "fail",
        })
        assert response.status_code == 201
        task_id = response.json()["id"]
        task = wait_until(client, task_id, "BRIEF_REVIEW")
        assert task["source"].get("scenario") is None
        client.post(f"/api/decompose/gates/{task_id}-A/decide", json={"action": "approve"})
        task = wait_until(client, task_id, "FACTS_REVIEW")
        assert task["state"] == "FACTS_REVIEW"

    def test_sse_replay_event_for_pending_gate(self, client, db_session):
        """SSE 重连应能从当前持久化状态恢复待确认闸门。"""
        from app.models.decompose_task import DecomposeTask
        from app.services.decompose_service import replay_current_event

        response = client.post("/api/decompose/tasks", json={"content": self.SAMPLE})
        task_id = response.json()["id"]
        wait_until(client, task_id, "BRIEF_REVIEW")
        task = db_session.get(DecomposeTask, int(task_id))
        event = replay_current_event(task)

        assert event == {
            "type": "gate",
            "task_id": str(task_id),
            "gate": "A",
            "message": "请确认拆解目标",
        }

    def test_delete_task(self, client):
        """删除任务：删除成功 → 详情 404 → 重复删除 404"""
        response = client.post("/api/decompose/tasks", json={"content": self.SAMPLE})
        assert response.status_code == 201
        task_id = response.json()["id"]
        wait_until(client, task_id, "BRIEF_REVIEW")

        response = client.delete(f"/api/decompose/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["ok"] is True

        response = client.get(f"/api/decompose/tasks/{task_id}")
        assert response.status_code == 404

        response = client.delete(f"/api/decompose/tasks/{task_id}")
        assert response.status_code == 404

        # 任务列表已不含该任务
        response = client.get("/api/decompose/tasks")
        assert response.status_code == 200
        assert all(item["id"] != task_id for item in response.json())

    def test_invalid_operations(self, client):
        """非法操作：空内容 / 闸门不在待确认状态"""
        response = client.post("/api/decompose/tasks", json={"content": "  "})
        assert response.status_code == 400

        response = client.post("/api/decompose/tasks", json={"content": self.SAMPLE})
        task_id = response.json()["id"]
        wait_until(client, task_id, "BRIEF_REVIEW")

        # 闸门B 确认后，重复确认已过的闸门 → 400
        client.post(f"/api/decompose/gates/{task_id}-A/decide", json={"action": "approve"})
        task = wait_until(client, task_id, "FACTS_REVIEW")
        client.post(f"/api/decompose/gates/{task_id}-B/decide", json={"action": "approve"})
        task = wait_until(client, task_id, "INSIGHT_REVIEW")
        response = client.post(f"/api/decompose/gates/{task_id}-B/decide", json={"action": "approve"})
        assert response.status_code == 400

        # 无效闸门 ID
        response = client.post("/api/decompose/gates/999-X/decide", json={"action": "approve"})
        assert response.status_code == 400

        # 不存在的任务
        response = client.get("/api/decompose/tasks/99999")
        assert response.status_code == 404
