# -*- coding: utf-8 -*-
import sys, traceback, json
sys.path.insert(0, r"E:\job3.0\backend")
from fastapi.testclient import TestClient
from app.main import app
content = open(r"E:\job3.0\_tmp_resume.txt", encoding="utf-8").read()
client = TestClient(app)
try:
    r = client.post("/api/resumes/save-text", json={"slot": 1, "content": content, "category": "技术", "version_name": "v1 原始版"})
    print("STATUS", r.status_code)
    print(r.text[:1000])
except Exception:
    traceback.print_exc()
