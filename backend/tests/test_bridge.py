# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 浏览器扩展桥接 API 测试（海投助手本地桥）

from app.core.config import settings

TOKEN_HEADERS = {"X-Bridge-Token": settings.BRIDGE_TOKEN}


def _create_resume(client, slot=1, content=None):
    resp = client.post(
        "/api/resumes/",
        json={
            "slot": slot,
            "filename": f"resume{slot}.pdf",
            "filepath": f"/tmp/resume{slot}.pdf",
            "file_size": 100,
            "file_type": "pdf",
            "category": "tech",
            "version_name": "v1",
            "content": content or "张三 软件工程师\n- Python\n- 3年经验",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _record_payload(**overrides):
    payload = {
        "job_url": "https://www.zhipin.com/job_detail/abc123.html",
        "company": "测试公司",
        "position": "高级后端工程师",
        "salary": "20-40K",
        "location": "北京",
        "source": "boss-zhipin",
        "jd_text": "【测试公司】高级后端工程师\n职位描述: 负责核心系统开发\n要求: 3年以上经验",
    }
    payload.update(overrides)
    return payload


def test_bridge_health(client):
    resp = client.get("/api/bridge/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["service"] == "bridge"


def test_bridge_requires_token(client):
    resp = client.post("/api/bridge/job-record", json=_record_payload())
    assert resp.status_code == 401
    resp = client.get("/api/bridge/resumes")
    assert resp.status_code == 401


def test_bridge_job_record_requires_resume(client):
    resp = client.post(
        "/api/bridge/job-record",
        json=_record_payload(),
        headers=TOKEN_HEADERS,
    )
    assert resp.status_code == 400
    assert "简历" in resp.json()["detail"]


def test_bridge_job_record_create_and_duplicate(client, sample_jd):
    resume = _create_resume(client, slot=1)
    payload = _record_payload(jd_text=sample_jd)

    # 首次记录成功
    resp = client.post("/api/bridge/job-record", json=payload, headers=TOKEN_HEADERS)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["ok"] is True
    assert body["duplicate"] is False
    assert body["application_id"] > 0
    assert body["snapshot_id"] > 0
    assert body["greeting"] and "您好" in body["greeting"]

    # 投递记录落库，状态为 pending
    app_resp = client.get(f"/api/applications/{body['application_id']}")
    assert app_resp.status_code == 200
    app = app_resp.json()
    assert app["company"] == "测试公司"
    assert app["position"] == "高级后端工程师"
    assert app["job_url"] == payload["job_url"]
    assert app["source"] == "boss-zhipin"
    assert app["status"] == "pending"
    assert app["resume_id"] == resume["id"]

    # 同一 job_url 再次记录 => 去重命中，不产生新记录
    dup = client.post("/api/bridge/job-record", json=payload, headers=TOKEN_HEADERS)
    assert dup.status_code == 200
    dup_body = dup.json()
    assert dup_body["duplicate"] is True
    assert dup_body["application_id"] == body["application_id"]

    list_resp = client.get("/api/applications/?limit=50")
    assert list_resp.status_code == 200
    apps = [a for a in list_resp.json() if a["job_url"] == payload["job_url"]]
    assert len(apps) == 1


def test_bridge_records_list_and_delete(client, sample_jd):
    _create_resume(client, slot=1)
    payload = _record_payload(jd_text=sample_jd)

    first = client.post("/api/bridge/job-record", json=payload, headers=TOKEN_HEADERS).json()

    records = client.get("/api/bridge/records", headers=TOKEN_HEADERS)
    assert records.status_code == 200
    rows = records.json()
    assert len(rows) == 1
    assert rows[0]["snapshot"]["id"] == first["snapshot_id"]
    assert rows[0]["snapshot"]["jd_text"] == sample_jd
    assert rows[0]["application"]["company"] == "测试公司"

    # 删除记录后，同一 URL 可以重新记录
    del_resp = client.delete(f"/api/bridge/records/{first['snapshot_id']}", headers=TOKEN_HEADERS)
    assert del_resp.status_code == 200
    assert del_resp.json()["ok"] is True

    again = client.post("/api/bridge/job-record", json=payload, headers=TOKEN_HEADERS)
    assert again.status_code == 200
    assert again.json()["duplicate"] is False


def test_bridge_resumes_with_token(client):
    resume = _create_resume(client, slot=1)
    resp = client.get("/api/bridge/resumes", headers=TOKEN_HEADERS)
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.json()]
    assert resume["id"] in ids


def test_bridge_invalid_resume_id(client):
    resp = client.post(
        "/api/bridge/job-record",
        json=_record_payload(resume_id=9999),
        headers=TOKEN_HEADERS,
    )
    assert resp.status_code == 404


def test_bridge_delete_missing_record(client):
    resp = client.delete("/api/bridge/records/9999", headers=TOKEN_HEADERS)
    assert resp.status_code == 404