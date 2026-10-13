# -*- coding: utf-8 -*-
"""LangGraph multi-agent optimization workflow with bounded convergence."""

import inspect
import re
from typing import Any, Dict, List, Literal, Optional, TypedDict
from langgraph.graph import END, StateGraph

MAX_ITERATIONS = 5
MIN_MATCH_SCORE = 80


class AgentState(TypedDict, total=False):
    resume_text: str
    jd_text: str
    slot: int
    resume_analysis: Optional[Dict[str, Any]]
    jd_analysis: Optional[Dict[str, Any]]
    planner_output: Optional[Dict[str, Any]]
    recruiter_output: Optional[Dict[str, Any]]
    writer_output: Optional[Dict[str, Any]]
    critic_output: Optional[Dict[str, Any]]
    optimized_resume: Optional[str]
    original_resume: Optional[str]
    iteration: int
    max_iterations: int
    match_score: float
    status: str
    errors: List[str]
    messages: List[Dict[str, Any]]
    enable_stream: bool
    callbacks: List[Any]


def _safe_text(value: Any) -> str:
    return value if isinstance(value, str) else ""


TECH_KEYWORDS = (
    "Python",
    "Django",
    "Flask",
    "FastAPI",
    "React",
    "Vue",
    "Node.js",
    "Java",
    "Go",
    "C++",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "微服务",
    "数据库",
    "大规模系统",
)


def _extract_keywords(text: str) -> List[str]:
    """Extract a small, explainable set of technical requirements."""
    normalized = _safe_text(text).lower()
    matches = [keyword for keyword in TECH_KEYWORDS if keyword.lower() in normalized]
    if matches:
        return matches

    # Keep a useful fallback for JDs that use technologies outside the curated list.
    fallback = re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{1,}", text)
    stopwords = {"and", "the", "with", "for", "from", "years", "experience"}
    return list(dict.fromkeys(word for word in fallback if word.lower() not in stopwords))[:10]


def _keyword_contexts(jd: str) -> Dict[str, str]:
    contexts: Dict[str, str] = {}
    for line in jd.splitlines():
        for keyword in _extract_keywords(line):
            contexts.setdefault(keyword, line.strip())
    return contexts


async def _emit_callbacks(callbacks: List[Any], event: Dict[str, Any]) -> None:
    for callback in callbacks:
        handler = getattr(callback, "on_agent_event", callback)
        if not callable(handler):
            continue
        result = handler(event)
        if inspect.isawaitable(result):
            await result




def parse_json_response(response: str) -> Dict[str, Any]:
    import json, re
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"raw": response}


def should_continue(state: AgentState) -> str:
    if state.get("iteration", 0) >= state.get("max_iterations", MAX_ITERATIONS):
        return "end"
    if state.get("match_score", 0.0) >= MIN_MATCH_SCORE:
        return "end"
    return "writer"

def analyzer_node(state: AgentState) -> AgentState:
    resume = _safe_text(state.get("resume_text"))
    jd = _safe_text(state.get("jd_text"))
    state["resume_analysis"] = {
        "word_count": len(resume),
        "sections": resume.count("\n") + 1 if resume else 0,
        "keywords": _extract_keywords(resume),
    }
    state["jd_analysis"] = {
        "word_count": len(jd),
        "requirements": [line.strip() for line in jd.splitlines() if line.strip()],
        "keywords": _extract_keywords(jd),
    }
    state["status"] = "running"
    return state


def planner_node(state: AgentState) -> AgentState:
    resume = _safe_text(state.get("resume_text"))
    jd = _safe_text(state.get("jd_text"))
    resume_keywords = set(_extract_keywords(resume))
    jd_keywords = _extract_keywords(jd)
    contexts = _keyword_contexts(jd)
    tasks = [
        {
            "requirement": keyword,
            "priority": "medium" if "加分" in contexts.get(keyword, "") else "high",
            "reason": f"JD requires {keyword}; direct evidence was not found in the resume.",
        }
        for keyword in jd_keywords
        if keyword not in resume_keywords
    ]
    if not tasks:
        tasks = [
            {
                "requirement": "evidence review",
                "priority": "medium",
                "reason": "All extracted keywords are present; verify that each claim has measurable evidence.",
            }
        ]
    state["planner_output"] = {
        "tasks": tasks,
        "resume_chars": len(resume),
        "jd_chars": len(jd),
        "requirements": jd_keywords,
    }
    return state


def recruiter_node(state: AgentState) -> AgentState:
    resume = _safe_text(state.get("resume_text"))
    jd = _safe_text(state.get("jd_text"))
    keywords = _extract_keywords(jd)
    resume_keywords = set(_extract_keywords(resume))
    matched = [keyword for keyword in keywords if keyword in resume_keywords]
    missing = [keyword for keyword in keywords if keyword not in resume_keywords]
    state["recruiter_output"] = {
        "keywords": keywords,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "coverage": round(len(matched) / len(keywords) * 100, 2) if keywords else 100.0,
        "requirements_count": len(state.get("jd_analysis", {}).get("requirements", [])),
    }
    return state


def writer_node(state: AgentState) -> AgentState:
    resume = _safe_text(state.get("original_resume") or state.get("resume_text"))
    tasks = state.get("planner_output", {}).get("tasks", [])
    state["writer_output"] = {
        "content": resume,
        "mode": "suggestions_only",
        "generated": False,
        "requested_changes": [
            task.get("requirement", "") for task in tasks if isinstance(task, dict)
        ],
        "preserved_facts": True,
        "warnings": [
            task.get("reason", "") for task in tasks if isinstance(task, dict) and task.get("reason")
        ],
    }
    state["optimized_resume"] = resume
    return state


def critic_node(state: AgentState) -> AgentState:
    resume = _safe_text(state.get("optimized_resume"))
    recruiter = state.get("recruiter_output") or {}
    jd_terms = recruiter.get("keywords", [])
    resume_keywords = set(_extract_keywords(resume))
    matched_keywords = [term for term in jd_terms if term in resume_keywords]
    missing_keywords = [term for term in jd_terms if term not in resume_keywords]
    score = 100.0 if not jd_terms else round(len(matched_keywords) / len(jd_terms) * 100, 2)
    state["match_score"] = score
    state["critic_output"] = {
        "overall_score": score,
        "verdict": "PASS" if score >= MIN_MATCH_SCORE else "NEEDS_IMPROVEMENT",
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "issues": [] if not missing_keywords else [
            f"Missing direct resume evidence for: {', '.join(missing_keywords)}"
        ],
    }
    state["iteration"] = state.get("iteration", 0) + 1
    return state


def critic_route(state: AgentState) -> Literal["writer", "end"]:
    critic = state.get("critic_output") or {}
    if state.get("iteration", 0) >= state.get("max_iterations", MAX_ITERATIONS):
        return "end"
    if state.get("optimized_resume") == state.get("original_resume"):
        return "end"
    return "end" if critic.get("verdict") == "PASS" else "writer"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("planner", planner_node)
    graph.add_node("recruiter", recruiter_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)
    graph.set_entry_point("analyzer")
    graph.add_edge("analyzer", "planner")
    graph.add_edge("planner", "recruiter")
    graph.add_edge("recruiter", "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges("critic", critic_route, {"writer": "writer", "end": END})
    return graph.compile()


async def run_optimization(
    resume_text: str,
    jd_text: str,
    slot: int = 1,
    enable_stream: bool = False,
    callbacks: Optional[List[Any]] = None,
) -> AgentState:
    callback_list = list(callbacks or [])
    state: AgentState = {
        "resume_text": resume_text, "jd_text": jd_text, "slot": slot,
        "original_resume": resume_text, "iteration": 0, "max_iterations": MAX_ITERATIONS,
        "match_score": 0.0, "status": "pending", "errors": [], "messages": [],
        "enable_stream": enable_stream, "callbacks": callback_list,
    }
    try:
        result = dict(state)
        async for update in build_graph().astream(state, stream_mode="updates"):
            for agent, node_output in update.items():
                result.update(node_output)
                if enable_stream:
                    if agent == "analyzer":
                        output = {
                            "resume_analysis": node_output.get("resume_analysis"),
                            "jd_analysis": node_output.get("jd_analysis"),
                        }
                    else:
                        output = node_output.get(f"{agent}_output") or {}
                    await _emit_callbacks(
                        callback_list,
                        {"type": "agent", "agent": agent, "status": "completed", "output": output},
                    )
        result["status"] = "completed"
        return result
    except Exception as exc:
        state["status"] = "failed"
        state["errors"].append(str(exc))
        await _emit_callbacks(callback_list, {"type": "error", "agent": "workflow", "error": str(exc)})
        return state
