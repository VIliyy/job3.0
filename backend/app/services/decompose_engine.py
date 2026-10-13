# -*- coding: utf-8 -*-
"""
信息拆解引擎（契约：docs/拆解契约.md 第 5 章）

- LLM 优先：DeepSeek/OpenAI 生成结构化契约（facts + inferences + meta）
- 规则降级：未配置 API Key 或 LLM 输出解析失败时，用规则拆分保证流程可跑
- 铁律：拆不出的内容标 C1/data_gaps，不编造
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.agents.base import ai_service

# 是否使用 LLM（测试中可 monkeypatch 为 False）
USE_LLM: bool = True

CONTRACT_FIELDS = ("contract_name", "version", "status", "created_at", "facts", "inferences", "meta")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def parse_json_text(text: str) -> Optional[Dict[str, Any]]:
    """从 LLM 输出中提取 JSON 对象"""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.DOTALL)
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                return None
    return None


def _base_meta(source: Dict[str, Any], target_question: str, data_gaps: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "source_type": "text",
        "word_count": len(source.get("content") or ""),
        "target_question": target_question,
        "errors": [],
        "data_gaps": data_gaps or [],
    }


# =============================================================================
# 规则降级（移植自前端 mock，保证前后端一致）
# =============================================================================

def _split_sentences(content: str) -> List[str]:
    return [s.strip() for s in re.split(r"[。；;！!？?\n]", content) if len(s.strip()) >= 4]


def _kind_of(text: str) -> str:
    if re.search(r"要求|需|必须|具备|熟练|精通|优先", text):
        return "requirement"
    if re.search(r"\$|€|¥|元|价格|售价|单价|折扣", text):
        return "pricing"
    if re.search(r"https?://", text):
        return "link"
    if re.search(r"年|个月|天|周", text):
        return "duration"
    if re.search(r"评分|评论|评价|退货|差评", text):
        return "reputation"
    return "info"


def _shorten(text: str, max_len: int = 40) -> str:
    return text if len(text) <= max_len else text[:max_len] + "…"


def _group_kinds(facts: List[Dict[str, Any]]) -> str:
    counts: Dict[str, int] = {}
    for f in facts:
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    return " / ".join(f"{k}×{v}" for k, v in counts.items())


def rule_s0(source: Dict[str, Any]) -> Dict[str, Any]:
    content = source.get("content") or ""
    sentences = _split_sentences(content)
    return {
        "facts": [
            {
                "id": "F-000",
                "kind": "source_meta",
                "content": f"材料共 {len(content)} 字，约 {len(sentences)} 句，来源类型 text",
                "anchor": "整篇",
                "confidence": "C3",
            }
        ],
        "inferences": [
            {
                "id": "I-001",
                "type": "brief",
                "content": f"拆解目标：{source.get('target') or '提取关键信息并归纳结论'}",
                "evidence": ["F-000"],
                "confidence": "C2",
            }
        ],
        "meta": _base_meta(source, source.get("target") or "提取关键信息并归纳结论"),
    }


def rule_s1(source: Dict[str, Any], s0: Dict[str, Any]) -> Dict[str, Any]:
    sentences = _split_sentences(source.get("content") or "")
    facts = []
    for index, text in enumerate(sentences):
        facts.append(
            {
                "id": f"F-{index + 1:03d}",
                "kind": _kind_of(text),
                "content": text,
                "anchor": f"第 {index + 1} 句",
                "confidence": "C3",
            }
        )
    data_gaps = ["材料过短，未拆出有效事实，可补充更完整的材料重跑"] if not facts else []
    inferences = [
        {
            "id": "I-010",
            "type": "cluster",
            "content": f"共拆出 {len(facts)} 条事实，类型分布：{_group_kinds(facts)}",
            "evidence": [f["id"] for f in facts[:3]],
            "confidence": "C3",
        }
    ]
    return {
        "facts": facts,
        "inferences": inferences,
        "meta": _base_meta(source, s0["meta"]["target_question"], data_gaps),
    }


def rule_s2(source: Dict[str, Any], s1: Dict[str, Any]) -> Dict[str, Any]:
    facts = s1.get("facts") or []
    fallback_fact = facts[0] if facts else None

    def pick(kind: str) -> Optional[Dict[str, Any]]:
        return next((f for f in facts if f["kind"] == kind), None)

    def evidence_of(ids: List[str]) -> List[str]:
        valid = [i for i in ids if i]
        return valid or ([fallback_fact["id"]] if fallback_fact else [])

    requirement = pick("requirement") or fallback_fact
    pricing = pick("pricing")
    reputation = pick("reputation")
    info = pick("info") or requirement
    inferences: List[Dict[str, Any]] = []

    # usp 核心卖点 / 关键要求
    if requirement:
        inferences.append({
            "id": "I-101", "type": "usp",
            "content": f"核心卖点/关键要求：{_shorten(requirement['content'])}。这是材料最突出的抓手，应作为后续调研与验证的主线。",
            "evidence": evidence_of([requirement["id"]]), "confidence": "C3",
        })

    # pricing 定价与成本
    if pricing:
        inferences.append({
            "id": "I-102", "type": "pricing",
            "content": f"定价/成本：{_shorten(pricing['content'])}。可作为定价区间或成本对比锚点，建议与同类产品横向对比后确认合理性。",
            "evidence": evidence_of([pricing["id"]]), "confidence": "C3",
        })
    else:
        inferences.append({
            "id": "I-102", "type": "pricing",
            "content": "定价/成本：材料未提及，属于数据缺口，建议补充价格、成本或预算信息后再评估。",
            "evidence": evidence_of([]), "confidence": "C1",
        })

    # risk 风险与短板
    if reputation:
        inferences.append({
            "id": "I-103", "type": "risk",
            "content": f"风险与短板：{_shorten(reputation['content'])}。负面信号需要重点核实，必要时补充差评/退货来源交叉验证。",
            "evidence": evidence_of([reputation["id"]]), "confidence": "C2",
        })
    else:
        inferences.append({
            "id": "I-103", "type": "risk",
            "content": "风险与短板：材料未给出明显负面信号，但仍需对时效性、合规性等隐性风险保持警惕。",
            "evidence": evidence_of([]), "confidence": "C1",
        })

    # opportunity 机会与空间
    if info:
        inferences.append({
            "id": "I-104", "type": "opportunity",
            "content": f"机会与空间：{_shorten(info['content'])}。可围绕这一信息点展开进一步调研，评估扩展或优化的空间。",
            "evidence": evidence_of([info["id"]]), "confidence": "C2",
        })

    # audience 目标人群 / 适用场景
    audience_fact = next(
        (f for f in facts if re.search(r"面向|适合|针对|人群|用户|客户|玩家|学生|职场|宝妈|老人|儿童", f["content"])),
        None,
    )
    if audience_fact:
        inferences.append({
            "id": "I-105", "type": "audience",
            "content": f"目标人群/适用场景：{_shorten(audience_fact['content'])}。可进一步明确人群画像与核心场景，指导卖点排序。",
            "evidence": evidence_of([audience_fact["id"]]), "confidence": "C2",
        })
    else:
        inferences.append({
            "id": "I-105", "type": "audience",
            "content": "目标人群/适用场景：材料未明确，建议补充目标用户画像或使用场景信息。",
            "evidence": evidence_of([]), "confidence": "C1",
        })

    # action 行动建议
    if requirement:
        action_content = (
            "行动建议：优先验证 C1/C2 低置信度结论（补来源、补数据），再围绕「"
            + _shorten(requirement["content"], 20)
            + "」制定下一步方案并排期。"
        )
    else:
        action_content = "行动建议：优先补充材料缺口，再围绕核心卖点制定下一步方案并排期。"
    inferences.append({
        "id": "I-106", "type": "action",
        "content": action_content,
        "evidence": evidence_of([requirement["id"]] if requirement else []), "confidence": "C2",
    })

    return {
        "facts": [],
        "inferences": inferences,
        "meta": _base_meta(source, s1["meta"]["target_question"], s1["meta"].get("data_gaps") or []),
    }

# =============================================================================
# LLM 生成（带规则兜底）
# =============================================================================

async def _llm_json(messages: List[Dict[str, str]], fallback_fn, *args) -> Dict[str, Any]:
    """调用 LLM 并尝试解析 JSON；失败则规则兜底"""
    try:
        if USE_LLM and ai_service.llm is not None:
            response = await ai_service.chat(messages)
            parsed = parse_json_text(response)
            if parsed is not None:
                return parsed
            print(f"[decompose] LLM 输出解析失败，走规则兜底: {response[:120]}")
    except Exception as e:
        print(f"[decompose] LLM 调用失败，走规则兜底: {e}")
    return fallback_fn(*args)


async def generate_s0(source: Dict[str, Any]) -> Dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": (
                "你是信息拆解引擎的 S0 输入解析器。用户会提供原始材料，请输出 JSON：\n"
                '{"brief": "拆解目标（若用户给了目标则原样采用）", "source_meta": "材料概况一句话（字数/句数/类型）"}'
            ),
        },
        {
            "role": "user",
            "content": (
                f"拆解目标（可选）：{source.get('target') or '（未提供，请推断）'}\n\n"
                f"原始材料：\n{source.get('content') or ''}"
            ),
        },
    ]
    parsed = await _llm_json(messages, rule_s0, source)
    if "brief" in parsed or "source_meta" in parsed:
        facts = [{
            "id": "F-000",
            "kind": "source_meta",
            "content": parsed.get("source_meta") or f"材料共 {len(source.get('content') or '')} 字",
            "anchor": "整篇",
            "confidence": "C3",
        }]
        target = source.get("target") or parsed.get("brief") or "提取关键信息并归纳结论"
        inferences = [{
            "id": "I-001",
            "type": "brief",
            "content": f"拆解目标：{target}",
            "evidence": ["F-000"],
            "confidence": "C2",
        }]
        return {
            "facts": facts,
            "inferences": inferences,
            "meta": _base_meta(source, target),
        }
    return rule_s0(source)


async def generate_s1(source: Dict[str, Any], s0: Dict[str, Any]) -> Dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": (
                "你是信息拆解引擎的 S1 事实拆解器。把用户材料拆成客观事实条目，只输出 JSON：\n"
                '{"facts": [{"id": "F-001", "kind": "requirement|pricing|link|duration|reputation|info", '
                '"content": "事实内容（保持原文语义，不编造）", "anchor": "原文位置（如：第 3 句）", '
                '"confidence": "C3|C2"}], "data_gaps": ["拆不出的部分，没有则空数组"]}\n'
                "要求尽量全量拆解，覆盖材料所有要点，不要遗漏重要内容；拆不出的部分写入 data_gaps。铁律：原文没有的信息不得编造，无法确定的标 C2，直接命中的标 C3。"
            ),
        },
        {
            "role": "user",
            "content": f"拆解目标：{s0['meta']['target_question']}\n\n原始材料：\n{source.get('content') or ''}",
        },
    ]
    parsed = await _llm_json(messages, rule_s1, source, s0)
    facts = parsed.get("facts") if isinstance(parsed.get("facts"), list) else None
    if facts:
        normalized = []
        seen_ids = set()
        for index, item in enumerate(facts):
            if not isinstance(item, dict):
                continue
            fid = str(item.get("id") or f"F-{index + 1:03d}")
            while fid in seen_ids:
                fid = f"F-{index + 1:03d}"
            seen_ids.add(fid)
            normalized.append({
                "id": fid,
                "kind": str(item.get("kind") or "info"),
                "content": str(item.get("content") or "").strip(),
                "anchor": str(item.get("anchor") or f"第 {index + 1} 句"),
                "confidence": str(item.get("confidence") or "C2").upper()[:2],
            })
        normalized = [f for f in normalized if f["content"]]
        if normalized:
            data_gaps = parsed.get("data_gaps") if isinstance(parsed.get("data_gaps"), list) else []
            inferences = [{
                "id": "I-010",
                "type": "cluster",
                "content": f"共拆出 {len(normalized)} 条事实，类型分布：{_group_kinds(normalized)}",
                "evidence": [f["id"] for f in normalized[:3]],
                "confidence": "C3",
            }]
            return {
                "facts": normalized,
                "inferences": inferences,
                "meta": _base_meta(source, s0["meta"]["target_question"], [str(g) for g in data_gaps]),
            }
    return rule_s1(source, s0)


async def generate_s2(source: Dict[str, Any], s1: Dict[str, Any]) -> Dict[str, Any]:
    facts_json = json.dumps(s1.get("facts") or [], ensure_ascii=False)
    messages = [
        {
            "role": "system",
            "content": (
                "你是信息拆解引擎的 S2 洞察生成器。基于已确认事实，按固定六要点框架归纳洞察，只输出 JSON：\n"
                '{"inferences": [{"id": "I-101", "type": "usp|pricing|risk|opportunity|audience|action", '
                '"content": "每条 2-3 句：结论 + 依据 + 影响或建议", "evidence": ["F-001"], "confidence": "C3|C2|C1"}]}\n'
                "要求：\n"
                "1. 六个要点每个至少 1 条，总条数 6-12 条；要点类型=usp(核心卖点/关键要求)、pricing(定价与成本)、risk(风险与短板)、opportunity(机会与空间)、audience(目标人群/适用场景)、action(行动建议)\n"
                "2. 材料未覆盖的要点，content 写明「材料未提及，属于数据缺口」，confidence 用 C1，evidence 引用最相关的一条事实\n"
                "3. 每条必须引用至少一条事实 id；不做超出事实的猜测。"
            ),
        },
        {
            "role": "user",
            "content": f"拆解目标：{s1['meta']['target_question']}\n\n已确认事实：\n{facts_json}",
        },
    ]
    parsed = await _llm_json(messages, rule_s2, source, s1)
    raw = parsed.get("inferences") if isinstance(parsed.get("inferences"), list) else None
    if raw:
        normalized = []
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                continue
            evidence = item.get("evidence") or []
            if isinstance(evidence, str):
                evidence = [evidence]
            normalized.append({
                "id": str(item.get("id") or f"I-{101 + index}"),
                "type": str(item.get("type") or "info"),
                "content": str(item.get("content") or "").strip(),
                "evidence": [str(e) for e in evidence],
                "confidence": str(item.get("confidence") or "C2").upper()[:2],
            })
        normalized = [i for i in normalized if i["content"] and i["evidence"]]
        if normalized:
            return {
                "facts": [],
                "inferences": normalized,
                "meta": _base_meta(source, s1["meta"]["target_question"], s1["meta"].get("data_gaps") or []),
            }
    return rule_s2(source, s1)


# =============================================================================
# S3 报告合成（执行摘要 + 分要点 + 行动建议）
# =============================================================================

S3_TITLES = {
    "usp": "核心卖点 / 关键要求",
    "pricing": "定价与成本",
    "risk": "风险与短板",
    "opportunity": "机会与空间",
    "audience": "目标人群 / 适用场景",
    "action": "行动建议",
}


def rule_s3(source: Dict[str, Any], s2: Dict[str, Any], s1: Dict[str, Any]) -> Dict[str, Any]:
    """S3 规则兜底：从已确认结论分组出分要点报告 + 执行摘要 + 行动建议"""
    inferences = s2.get("inferences") or []
    facts = s1.get("facts") or []
    by_type: Dict[str, List[Dict[str, Any]]] = {}
    for inference in inferences:
        by_type.setdefault(inference.get("type") or "info", []).append(inference)

    sections = []
    for key, title in S3_TITLES.items():
        group = by_type.get(key)
        if not group:
            continue
        evidence: List[str] = []
        contents: List[str] = []
        for inference in group:
            contents.append(str(inference.get("content") or ""))
            for e in inference.get("evidence") or []:
                if e not in evidence:
                    evidence.append(str(e))
        sections.append({
            "type": key,
            "title": title,
            "content": "；".join(contents),
            "evidence": evidence[:5],
        })

    gaps = s2.get("meta", {}).get("data_gaps") or []
    summary_lines = [
        f"材料共 {len(source.get('content') or '')} 字，拆出 {len(facts)} 条事实、{len(inferences)} 条结论。",
        "核心结论：" + ("；".join(str(i.get("content") or "") for i in inferences[:2]) if inferences else "暂无结论。"),
    ]
    if gaps:
        summary_lines.append("主要缺口：" + "；".join(str(g) for g in gaps))

    meta = _base_meta(source, s2.get("meta", {}).get("target_question") or "提取关键信息并归纳结论", gaps)
    meta["exported_at"] = now_iso()
    meta["summary"] = " ".join(summary_lines)
    meta["sections"] = sections
    meta["actions"] = [
        "对 C1/C2 低置信度结论补充来源或数据验证后再引用",
        "按「行动建议」要点落实下一步，并复核风险与定价假设",
    ]
    return {"facts": [], "inferences": inferences, "meta": meta}


async def generate_s3(source: Dict[str, Any], s2: Dict[str, Any], s1: Dict[str, Any]) -> Dict[str, Any]:
    """S3 报告合成：LLM 生成执行摘要 + 分要点论证 + 行动建议，失败走规则兜底"""
    inferences_json = json.dumps(s2.get("inferences") or [], ensure_ascii=False)
    messages = [
        {
            "role": "system",
            "content": (
                "你是信息拆解引擎的 S3 报告合成器。基于已确认结论，生成一份可读报告内容，只输出 JSON：\n"
                '{"summary": "执行摘要（2-3 句：材料是什么 + 最重要的结论 + 主要风险/机会）", '
                '"sections": [{"type": "usp|pricing|risk|opportunity|audience|action", "title": "要点名", '
                '"content": "3-4 句综合论证（可引用事实编号 F-xxx）", "evidence": ["F-001"]}], '
                '"actions": ["下一步行动建议（2-4 条，每条一句）"]}\n'
                "要求：sections 覆盖材料实际涉及的要点；每条 evidence 引用该要点对应结论的事实 id；不编造。"
            ),
        },
        {
            "role": "user",
            "content": f"拆解目标：{s2.get('meta', {}).get('target_question') or '提取关键信息并归纳结论'}\n\n已确认结论：\n{inferences_json}",
        },
    ]
    parsed = await _llm_json(messages, rule_s3, source, s2, s1)
    summary = parsed.get("summary")
    sections = parsed.get("sections") if isinstance(parsed.get("sections"), list) else None
    actions = parsed.get("actions") if isinstance(parsed.get("actions"), list) else None
    if summary or sections or actions:
        inferences = s2.get("inferences") or []
        gaps = s2.get("meta", {}).get("data_gaps") or []
        meta = _base_meta(source, s2.get("meta", {}).get("target_question") or "提取关键信息并归纳结论", gaps)
        meta["exported_at"] = now_iso()
        meta["summary"] = str(summary) if summary else ""
        meta["sections"] = [
            {
                "type": str(s.get("type") or "info"),
                "title": str(s.get("title") or S3_TITLES.get(str(s.get("type") or ""), str(s.get("type") or "要点"))),
                "content": str(s.get("content") or ""),
                "evidence": [str(e) for e in (s.get("evidence") or [])],
            }
            for s in sections or []
        ]
        meta["actions"] = [str(a) for a in (actions or [])]
        return {"facts": [], "inferences": inferences, "meta": meta}
    return rule_s3(source, s2, s1)

def build_contract(contract_name: str, version: int, status: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """组装完整契约（与前端 mock 形状一致）"""
    contract = {
        "contract_name": contract_name,
        "version": version,
        "status": status,
        "created_at": now_iso(),
        "facts": body.get("facts") or [],
        "inferences": body.get("inferences") or [],
        "meta": body.get("meta") or _base_meta({}, ""),
    }
    return contract