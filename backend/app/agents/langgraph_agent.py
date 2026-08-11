# -*- coding: utf-8 -*-
"""
Job3.0 多Agent协作系统 - LangGraph状态机核心
"""

import json
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    resume_text: str
    jd_text: str
    slot: int
    resume_analysis: Optional[Dict[str, Any]]
    optimized_resume: Optional[str]
    original_resume: Optional[str]
    jd_analysis: Optional[Dict[str, Any]]
    planner_output: Optional[Dict[str, Any]]
    recruiter_output: Optional[Dict[str, Any]]
    writer_output: Optional[Dict[str, Any]]
    critic_output: Optional[Dict[str, Any]]
    iteration: int
    max_iterations: int
    match_score: float
    status: str
    errors: List[str]
    messages: List[Dict[str, Any]]


MAX_ITERATIONS = 5
MIN_MATCH_SCORE = 80


def parse_json_response(response: str) -> Dict[str, Any]:
    try:
        return json.loads(response)
    except:
        import re
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return {"raw": response}


async def emit_event(state: AgentState, event_type: str, data: Dict[str, Any]):
    if state.get("enable_stream") and state.get("callbacks"):
        message = {"type": event_type, "timestamp": datetime.now().isoformat(), **data}
        state["messages"].append(message)


async def analyzer_node(state: AgentState) -> AgentState:
    state["status"] = "running"
    state["current_agent"] = "analyzer"
    try:
        state["resume_analysis"] = {"word_count": len(state["resume_text"])}
        state["jd_analysis"] = {"word_count": len(state.get("jd_text", ""))}
    except Exception as e:
        state["errors"].append(str(e))
    return state


def should_continue(state: AgentState) -> str:
    if state["iteration"] >= state["max_iterations"]:
        return "end"
    if state["match_score"] >= MIN_MATCH_SCORE:
        return "end"
    return "writer"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("analyzer", analyzer_node)
    graph.set_entry_point("analyzer")
    graph.add_edge("analyzer", END)
    return graph.compile()


async def run_optimization(
    resume_text: str,
    jd_text: str,
    slot: int = 1
) -> AgentState:
    initial_state = AgentState(
        resume_text=resume_text,
        jd_text=jd_text,
        slot=slot,
        resume_analysis=None,
        optimized_resume=None,
        original_resume=resume_text,
        jd_analysis=None,
        planner_output=None,
        recruiter_output=None,
        writer_output=None,
        critic_output=None,
        iteration=0,
        max_iterations=MAX_ITERATIONS,
        match_score=0.0,
        status="pending",
        errors=[],
        messages=[],
        enable_stream=False,
        callbacks=[]
    )
    
    try:
        graph = build_graph()
        result = await graph.ainvoke(initial_state)
        result["status"] = "completed"
        return result
    except Exception as e:
        initial_state["status"] = "failed"
        initial_state["errors"].append(str(e))
        return initial_state