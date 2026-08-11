# -*- coding: utf-8 -*-
import io
path = r"E:\job3.0\bad.md"
src = io.open(path, encoding="utf-8").read()
append = '''

# 八、2026-08-09 演示实测发现的问题（v2.2 加固）

## 8.1 本次修复的问题（现象 → 根因 → 修复）

| # | 现象 | 根因 | 修复 |
|---|------|------|------|
| 1 | `POST /api/resumes/save-text` 传中文分类（如 category="技术"）时 500 | `Resume.category` 是 SQLAlchemy Enum（tech/product/ops/marketing/other），接口层直接透传任意字符串，`db.refresh()` 时 `LookupError: '技术' is not among the defined enum values`；且 INSERT 已提交、refresh 才炸，脏数据落库 | 新增 `normalize_category()`/`normalize_status()`：中文标签、大小写差异、非法值统一映射为枚举值（非法默认 OTHER/DRAFT），应用于 create/list/update/upload/save-text 全链路 |
| 2 | `save-text` 传 slot=0 时 500 且脏数据落库 | `SaveTextRequest.slot` 无 ge/le 校验（ResumeCreate 有但 save-text 漏了） | `slot: int = Field(1, ge=1, le=4)` |
| 3 | 脏数据行（category=中文）在 DB 中，连 `GET /api/resumes` 读列表都会炸 | 枚举值非法时读行同样抛 LookupError | 清理 2 条脏数据 + 对应 uploads 文件；同时修复写入路径杜绝再次产生 |

## 8.2 新增操作预警（合并到 7.2 一并遵守）

1. **枚举字段（category/status）入库前必须归一化**：模型层 Enum 校验在 commit/refresh 时才触发，非法值会"先写坏数据、后抛 500"，且读列表也会连带崩溃。新增接口一律走 normalize 函数。
2. **save-text / upload 等"写文件 + 写库"的接口先做参数范围校验**（slot 1-4 等），否则 500 会留下孤儿文件与脏行。
3. **重启后端时务必重定向日志**：`Start-Process python ... -RedirectStandardOutput/-RedirectStandardError`，否则 500 traceback 无处可查（本次靠 TestClient 本地复现）。
4. **复现 API 错误优先用 TestClient 脚本**（`E:\\job3.0\\_tmp_repro.py` 模式），可拿到完整 SQLAlchemy traceback。
5. **演示前先跑一遍"写路径"自测**：save-text（中文 category + 合法 slot）→ GET 列表，确认无 500 再演示。

## 8.3 当前状态

- 后端：pytest 需补跑（新增归一化不影响既有用例）
- 前端：未改动
- 演示进行中：resumes → optimize（真实 AI）→ agent chat（SSE）
'''
io.open(path, "a", encoding="utf-8", newline="\n").write(append)
print("BAD.MD UPDATED")
