# -*- coding: utf-8 -*-
"""
信息拆解状态机服务（契约：docs/拆解契约.md 第 3/4/9 章）

- 状态机：DRAFT → BRIEF_REVIEW → DECOMPOSING → FACTS_REVIEW → INSIGHTING
          → INSIGHT_REVIEW → REPORTING → DONE（任意状态可 FAILED）
- 任务级互斥：同一任务同一时刻只有一个编排循环（asyncio.Lock）
- 闸门确认 = 写 decisions + 更新契约 status + 触发下游
- SSE 事件通过内存队列发布（thinking/output/gate/complete/error）
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.decompose_task import DecomposeTask, DecomposeContract, DecomposeDecision
from app.services import decompose_engine as engine

# 状态推进顺序
STATE_ORDER = [
    "DRAFT", "BRIEF_REVIEW", "DECOMPOSING", "FACTS_REVIEW",
    "INSIGHTING", "INSIGHT_REVIEW", "REPORTING", "DONE", "FAILED",
]

# 闸门 → 对应停靠状态 / 契约 / 触发段
GATE_DEFS = {
    "A": {"state": "BRIEF_REVIEW", "contract": "S0", "next": "S1"},
    "B": {"state": "FACTS_REVIEW", "contract": "S1", "next": "S2"},
    "C": {"state": "INSIGHT_REVIEW", "contract": "S2", "next": "S3"},
}


# =============================================================================
# 事件发布 / 订阅（SSE 内存队列）
# =============================================================================

_queues: Dict[int, Set[asyncio.Queue]] = {}
_locks: Dict[int, asyncio.Lock] = {}


def _get_lock(task_id: int) -> asyncio.Lock:
    if task_id not in _locks:
        _locks[task_id] = asyncio.Lock()
    return _locks[task_id]


def publish(task_id: int, event_type: str, **data: Any) -> None:
    event = {"type": event_type, "task_id": str(task_id), **data}
    for queue in list(_queues.get(task_id, set())):
        try:
            queue.put_nowait(event)
        except Exception:
            pass


def subscribe(task_id: int, queue: asyncio.Queue) -> None:
    _queues.setdefault(task_id, set()).add(queue)


def unsubscribe(task_id: int, queue: asyncio.Queue) -> None:
    queues = _queues.get(task_id)
    if queues:
        queues.discard(queue)
        if not queues:
            _queues.pop(task_id, None)


def replay_current_event(task: DecomposeTask) -> Optional[Dict[str, Any]]:
    """Build one replay event for a reconnecting SSE client."""
    task_id = str(task.id)
    if task.state == "DONE":
        return {"type": "complete", "task_id": task_id, "message": "拆解完成"}
    if task.state == "FAILED":
        return {"type": "error", "task_id": task_id, "message": task.error or "拆解失败"}
    gate_by_state = {
        "BRIEF_REVIEW": ("A", "请确认拆解目标"),
        "FACTS_REVIEW": ("B", "请确认事实清单，可标记错/缺"),
        "INSIGHT_REVIEW": ("C", "请确认结论"),
    }
    gate = gate_by_state.get(task.state)
    if gate:
        return {"type": "gate", "task_id": task_id, "gate": gate[0], "message": gate[1]}
    return None


# =============================================================================
# 序列化（与前端 mock 形状一致）
# =============================================================================

def _iso(dt) -> str:
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.isoformat(timespec="seconds")
    return str(dt)


def serialize_gates(task: DecomposeTask, decisions: List[DecomposeDecision]) -> Dict[str, Dict[str, Any]]:
    gates: Dict[str, Dict[str, Any]] = {}
    for key, definition in GATE_DEFS.items():
        idx_now = STATE_ORDER.index(task.state)
        idx_gate = STATE_ORDER.index(definition["state"])
        if task.state == definition["state"]:
            gate_state = "pending"
        elif idx_now > idx_gate and task.state != "FAILED":
            gate_state = "approved"
        else:
            gate_state = "idle"
        note = ""
        for decision in reversed(decisions):
            if decision.gate == key and decision.note:
                note = decision.note
                break
        gates[key] = {
            "id": f"{task.id}-{key}",
            "name": {"A": "Brief 确认", "B": "事实清单确认", "C": "结论确认"}[key],
            "state": gate_state,
            "decided_at": _iso(decisions[-1].decided_at) if decisions and decisions[-1].gate == key else None,
            "note": note,
        }
    return gates


def serialize_task(task: DecomposeTask) -> Dict[str, Any]:
    contracts: Dict[str, Dict[str, Any]] = {}
    for contract in task.contracts:
        try:
            body = json.loads(contract.body)
        except Exception:
            body = {"facts": [], "inferences": [], "meta": {}}
        body["contract_name"] = contract.contract_name
        body["version"] = contract.version
        body["status"] = contract.status
        body["created_at"] = _iso(contract.created_at)
        contracts[contract.contract_name] = body

    return {
        "id": str(task.id),
        "title": task.title,
        "state": task.state,
        "version": task.version,
        "created_at": _iso(task.created_at),
        "source": {
            "content": task.source_content,
            "target": task.source_target or "",
        },
        "contracts": contracts,
        "gates": serialize_gates(task, task.decisions),
        "error": task.error,
    }


# =============================================================================
# 编排循环（后台异步执行）
# =============================================================================

# 会话工厂（测试中可替换为内存库）
session_factory = SessionLocal


async def run_from(task_id: int, from_stage: str) -> None:
    lock = _get_lock(task_id)
    async with lock:
        db = session_factory()
        try:
            task = db.get(DecomposeTask, task_id)
            if task is None:
                return
            if from_stage == "S0":
                await _run_s0(db, task)
            elif from_stage == "S1":
                await _run_s1(db, task)
            elif from_stage == "S2":
                await _run_s2(db, task)
            elif from_stage == "S3":
                await _run_s3(db, task)
        except Exception as e:
            task.state = "FAILED"
            task.error = str(e)
            db.commit()
            publish(task_id, "error", message=str(e))
            print(f"[decompose] 任务 {task_id} 失败: {e}")
        finally:
            db.close()


async def _upsert_contract(db: Session, task_id: int, contract_name: str, contract: Dict[str, Any]) -> None:
    existing = (
        db.query(DecomposeContract)
        .filter(
            DecomposeContract.task_id == task_id,
            DecomposeContract.contract_name == contract_name,
        )
        .first()
    )
    body = {k: v for k, v in contract.items() if k in ("facts", "inferences", "meta")}
    if existing:
        existing.body = json.dumps(body, ensure_ascii=False)
        existing.version = contract["version"]
        existing.status = contract["status"]
    else:
        db.add(
            DecomposeContract(
                task_id=task_id,
                contract_name=contract_name,
                version=contract["version"],
                status=contract["status"],
                body=json.dumps(body, ensure_ascii=False),
            )
        )


async def _run_s0(db: Session, task: DecomposeTask) -> None:
    publish(task.id, "thinking", contract="S0", message="S0 输入解析：识别拆解目标与材料结构")
    source = {"content": task.source_content, "target": task.source_target or ""}
    body = await engine.generate_s0(source)
    contract = engine.build_contract("S0", task.version, "needs_human", body)
    await _upsert_contract(db, task.id, "S0", contract)
    task.state = "BRIEF_REVIEW"
    task.error = None
    db.commit()
    publish(task.id, "output", contract="S0", contract_body=contract)
    publish(task.id, "gate", gate="A", message="请确认拆解目标")


async def _run_s1(db: Session, task: DecomposeTask) -> None:
    task.state = "DECOMPOSING"
    task.error = None
    db.commit()
    publish(task.id, "thinking", contract="S1", message="S1 事实拆解：逐句拆解并标注原文锚点")

    source = {"content": task.source_content, "target": task.source_target or ""}
    s0_contract = next((c for c in task.contracts if c.contract_name == "S0"), None)
    s0 = json.loads(s0_contract.body) if s0_contract else {"meta": {"target_question": "提取关键信息"}}
    body = await engine.generate_s1(source, s0)
    contract = engine.build_contract("S1", task.version, "needs_human", body)
    await _upsert_contract(db, task.id, "S1", contract)
    task.state = "FACTS_REVIEW"
    db.commit()
    publish(task.id, "output", contract="S1", contract_body=contract)
    publish(task.id, "gate", gate="B", message="请确认事实清单，可标记错/缺")


async def _run_s2(db: Session, task: DecomposeTask) -> None:
    task.state = "INSIGHTING"
    task.error = None
    db.commit()
    publish(task.id, "thinking", contract="S2", message="S2 洞察生成：基于已确认事实归纳结论")

    source = {"content": task.source_content, "target": task.source_target or ""}
    s1_contract = next((c for c in task.contracts if c.contract_name == "S1"), None)
    if s1_contract is None:
        raise RuntimeError("缺少已确认的 S1 契约，无法生成洞察")
    s1 = json.loads(s1_contract.body)
    s1["meta"]["target_question"] = task.source_target or "提取关键信息"
    body = await engine.generate_s2(source, s1)
    contract = engine.build_contract("S2", task.version, "needs_human", body)
    await _upsert_contract(db, task.id, "S2", contract)
    task.state = "INSIGHT_REVIEW"
    db.commit()
    publish(task.id, "output", contract="S2", contract_body=contract)
    publish(task.id, "gate", gate="C", message="请确认结论")


async def _run_s3(db: Session, task: DecomposeTask) -> None:
    task.state = "REPORTING"
    task.error = None
    db.commit()
    publish(task.id, "thinking", contract="S3", message="S3 报告合成：生成执行摘要与分要点报告")

    s1_contract = next((c for c in task.contracts if c.contract_name == "S1"), None)
    s2_contract = next((c for c in task.contracts if c.contract_name == "S2"), None)
    if s2_contract is None:
        raise RuntimeError("缺少已确认的 S2 契约，无法合成报告")

    s1 = json.loads(s1_contract.body) if s1_contract is not None else {"facts": [], "meta": {}}
    s2 = json.loads(s2_contract.body)
    source = {"content": task.source_content, "target": task.source_target or ""}

    body = await engine.generate_s3(source, s2, s1)
    contract = engine.build_contract("S3", task.version, "auto_ok", body)
    await _upsert_contract(db, task.id, "S3", contract)
    task.state = "DONE"
    db.commit()
    publish(task.id, "output", contract="S3", contract_body=contract)
    publish(task.id, "complete", message="拆解完成")

# =============================================================================
# 对外操作
# =============================================================================

def create_task(db: Session, payload: Dict[str, Any]) -> DecomposeTask:
    content = (payload.get("content") or "").strip()
    if not content:
        raise ValueError("原始材料不能为空")
    task = DecomposeTask(
        title=content.split("\n")[0][:30] or "未命名拆解",
        state="DRAFT",
        source_content=content,
        source_target=(payload.get("target") or "").strip(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    asyncio.get_event_loop().create_task(run_from(task.id, "S0"))
    return task


def recover_incomplete_tasks() -> int:
    """Resume persisted decomposition tasks after a process restart."""
    db = session_factory()
    recovered = 0
    try:
        tasks = (
            db.query(DecomposeTask)
            .filter(DecomposeTask.state.in_(("DRAFT", "DECOMPOSING", "INSIGHTING", "REPORTING")))
            .all()
        )
        for task in tasks:
            stage = {
                "DRAFT": "S0",
                "DECOMPOSING": "S1",
                "INSIGHTING": "S2",
                "REPORTING": "S3",
            }[task.state]
            asyncio.get_event_loop().create_task(run_from(task.id, stage))
            recovered += 1
        return recovered
    finally:
        db.close()


def decide_gate(db: Session, gate_id: str, action: str, note: str = "") -> DecomposeTask:
    match = re_match_gate(gate_id)
    if not match:
        raise ValueError(f"无效闸门 ID: {gate_id}")
    task_id, gate_key = match
    task = db.get(DecomposeTask, int(task_id))
    if task is None:
        raise ValueError(f"任务不存在: {task_id}")
    definition = GATE_DEFS.get(gate_key)
    if definition is None:
        raise ValueError(f"无效闸门: {gate_key}")
    if task.state != definition["state"]:
        raise ValueError(f"闸门 {gate_key} 不在待确认状态（当前 {task.state}）")

    db.add(
        DecomposeDecision(
            task_id=task.id,
            gate=gate_key,
            action=action,
            note=(note or "")[:500],
        )
    )

    if action == "regenerate":
        task.version += 1
        _delete_downstream_contracts(db, task.id, definition["contract"])
        db.commit()
        asyncio.get_event_loop().create_task(run_from(task.id, definition["contract"]))
        return task

    if action != "approve":
        raise ValueError(f"无效动作: {action}")

    contract = next((c for c in task.contracts if c.contract_name == definition["contract"]), None)
    if contract is not None:
        contract.status = "human_approved"
    db.commit()
    asyncio.get_event_loop().create_task(run_from(task.id, definition["next"]))
    return task


def re_match_gate(gate_id: str):
    import re
    match = re.match(r"^(\d+)-([ABC])$", gate_id)
    return (match.group(1), match.group(2)) if match else None


def _delete_downstream_contracts(db: Session, task_id: int, from_contract: str) -> None:
    """删除 from_contract 及下游契约（重生成时下游失效）"""
    order = {"S0": ["S0", "S1", "S2", "S3"], "S1": ["S1", "S2", "S3"], "S2": ["S2", "S3"]}
    names = order.get(from_contract, [])
    if not names:
        return
    db.query(DecomposeContract).filter(
        DecomposeContract.task_id == task_id,
        DecomposeContract.contract_name.in_(names),
    ).delete(synchronize_session=False)


def rerun(db: Session, task_id: int, from_stage: str) -> DecomposeTask:
    task = db.get(DecomposeTask, task_id)
    if task is None:
        raise ValueError(f"任务不存在: {task_id}")
    contract = {"S0": "S0", "S1": "S1", "S2": "S2", "S3": "S3"}.get(from_stage, "S0")
    task.version += 1
    task.error = None
    _delete_downstream_contracts(db, task.id, contract)
    db.commit()
    asyncio.get_event_loop().create_task(run_from(task.id, contract))
    return task


def delete_task(db: Session, task_id: int) -> None:
    """删除任务（契约/决策级联删除），并清理内存中的队列与锁"""
    task = db.get(DecomposeTask, task_id)
    if task is None:
        raise ValueError(f"任务不存在: {task_id}")
    db.delete(task)
    db.commit()
    _queues.pop(task_id, None)
    _locks.pop(task_id, None)


def export_markdown(db: Session, task_id: int) -> str:
    task = db.get(DecomposeTask, task_id)
    if task is None:
        raise ValueError(f"任务不存在: {task_id}")
    s3 = next((c for c in task.contracts if c.contract_name == "S3"), None)
    s2 = next((c for c in task.contracts if c.contract_name == "S2"), None)
    s1 = next((c for c in task.contracts if c.contract_name == "S1"), None)

    s3_body = json.loads(s3.body) if s3 is not None else {}
    s3_meta = s3_body.get("meta") or {}
    s2_meta = {}
    if s2 is not None:
        s2_body = json.loads(s2.body)
        s2_meta = s2_body.get("meta") or {}

    inferences: List[Dict[str, Any]] = s3_body.get("inferences") or []
    if not inferences and s2 is not None:
        inferences = json.loads(s2.body).get("inferences") or []

    facts: List[Dict[str, Any]] = []
    if s1 is not None:
        facts = json.loads(s1.body).get("facts") or []

    summary = s3_meta.get("summary") or ""
    sections = s3_meta.get("sections") or []
    actions = s3_meta.get("actions") or []
    gaps = s3_meta.get("data_gaps") or s2_meta.get("data_gaps") or []

    lines = [
        f"# 信息拆解报告 · {task.title}",
        "",
        f"- 任务 ID: {task.id}  |  版本 v{task.version}  |  完成时间: {_iso(task.created_at)}",
        f"- 拆解目标: {task.source_target or '提取关键信息并归纳结论'}",
        f"- 材料规模: {len(task.source_content)} 字  |  事实 {len(facts)} 条  |  结论 {len(inferences)} 条",
        "",
        "## 执行摘要",
        "",
        summary or "（无）",
        "",
        "## 结论（按要点）",
        "",
    ]
    if sections:
        for section in sections:
            lines.append(f"### {section.get('title') or section.get('type')}")
            lines.append("")
            lines.append(section.get("content") or "（无）")
            evidence = section.get("evidence") or []
            if evidence:
                lines.extend(["", f"- 证据: {'、'.join(str(e) for e in evidence)}"])
            lines.append("")
    else:
        for inference in inferences:
            evidence = inference.get("evidence") or []
            lines.append(
                f"- [{inference.get('type')}] {inference.get('content')}"
                f"（置信度 {inference.get('confidence')}，证据 {'、'.join(str(e) for e in evidence) or '无'}）"
            )
        lines.append("")

    lines.extend(["## 结论明细", ""])
    for inference in inferences:
        evidence = inference.get("evidence") or []
        lines.append(
            f"- [{inference.get('type')}] {inference.get('content')}"
            f"（置信度 {inference.get('confidence')}，证据 {'、'.join(str(e) for e in evidence) or '无'}）"
        )
    lines.extend(["", "## 事实清单", ""])
    for fact in facts:
        lines.append(
            f"- {fact.get('id')}（{fact.get('kind')}）{fact.get('content')}  [锚点: {fact.get('anchor')}]"
        )
    lines.extend(["", "## 数据缺口", ""])
    if gaps:
        for gap in gaps:
            lines.append(f"- {gap}")
    else:
        lines.append("- 无")
    lines.extend(["", "## 闸门确认记录", ""])
    if task.decisions:
        for decision in task.decisions:
            note = f"（意见：{decision.note}）" if decision.note else ""
            lines.append(f"- 闸门 {decision.gate}：{decision.action}{note} @ {_iso(decision.decided_at)}")
    else:
        lines.append("- 无")
    lines.extend(["", "## 下一步建议", ""])
    if actions:
        for action in actions:
            lines.append(f"- {action}")
    else:
        lines.append("- 无")
    return "\n".join(lines)
