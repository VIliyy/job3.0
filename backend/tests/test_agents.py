# -*- coding: utf-8 -*-
"""
Job3.0 多Agent协作系统 - 单元测试
"""

import pytest
import asyncio

# 测试数据
SAMPLE_RESUME = """张三
工作经历：
2020-2023，某互联网公司，后端开发
- 负责用户系统开发
- 使用Python和Django

2018-2020，某创业公司，全栈开发
- 开发Web应用
- 使用React和Node.js

教育背景：
2014-2018，XX大学，计算机科学
"""

SAMPLE_JD = """招聘后端开发工程师

要求：
1. 3年以上Python开发经验
2. 熟悉Django或Flask
3. 有数据库设计经验
4. 了解微服务架构

加分项：
- 有大规模系统经验
- 熟悉Redis或MongoDB
"""

# =============================================================================
# 测试AgentState定义
# =============================================================================

def test_agent_state_structure():
    from app.agents.langgraph_agent import AgentState
    
    required_fields = [
        'resume_text', 'jd_text', 'slot',
        'resume_analysis', 'optimized_resume', 'original_resume', 'jd_analysis',
        'iteration', 'max_iterations',
        'match_score', 'status', 'errors', 'messages',
        'enable_stream', 'callbacks'
    ]
    
    state = AgentState(
        resume_text="test",
        jd_text="test",
        slot=1,
        resume_analysis=None,
        optimized_resume=None,
        original_resume=None,
        jd_analysis=None,
        planner_output=None,
        recruiter_output=None,
        writer_output=None,
        critic_output=None,
        iteration=0,
        max_iterations=5,
        match_score=0.0,
        status="pending",
        errors=[],
        messages=[],
        enable_stream=False,
        callbacks=[]
    )
    
    for field in required_fields:
        assert field in state, f"Missing field: {field}"

# =============================================================================
# 测试配置常量
# =============================================================================

def test_configuration_constants():
    from app.agents.langgraph_agent import MAX_ITERATIONS, MIN_MATCH_SCORE

    assert MAX_ITERATIONS == 5
    assert MIN_MATCH_SCORE == 80

# =============================================================================
# 测试JSON解析
# =============================================================================

def test_parse_json_response_valid():
    from app.agents.langgraph_agent import parse_json_response
    
    valid_json = '{\"name\": \"test\", \"value\": 123}'
    result = parse_json_response(valid_json)
    assert result == {"name": "test", "value": 123}

def test_parse_json_response_invalid():
    from app.agents.langgraph_agent import parse_json_response
    
    invalid_json = "This is not JSON"
    result = parse_json_response(invalid_json)
    assert "raw" in result

# =============================================================================
# 测试收敛判断
# =============================================================================

def test_should_continue_max_iterations():
    from app.agents.langgraph_agent import should_continue

    assert should_continue({"iteration": 5, "max_iterations": 5, "match_score": 70}) == "end"

def test_should_continue_target_score():
    from app.agents.langgraph_agent import should_continue

    assert should_continue({"iteration": 3, "max_iterations": 5, "match_score": 85}) == "end"

def test_should_continue_needs_improvement():
    from app.agents.langgraph_agent import should_continue

    assert should_continue({"iteration": 2, "max_iterations": 5, "match_score": 65}) == "writer"

# =============================================================================
# 测试状态创建
# =============================================================================

@pytest.mark.asyncio
async def test_create_initial_state():
    from app.agents.langgraph_agent import run_optimization

    state = await run_optimization(
        resume_text=SAMPLE_RESUME,
        jd_text=SAMPLE_JD,
        slot=1
    )

    assert state["resume_text"] == SAMPLE_RESUME
    assert state["jd_text"] == SAMPLE_JD
    assert state["slot"] == 1
    assert state["iteration"] == 0
    assert state["status"] == "completed"
    assert state["match_score"] >= 0

# =============================================================================
# 测试状态机构建
# =============================================================================

def test_build_optimization_graph():
    from app.agents.langgraph_agent import build_graph

    graph = build_graph()
    assert graph is not None
    assert hasattr(graph, 'nodes')
    # 编译后的图可直接调用
    assert hasattr(graph, 'ainvoke')

# =============================================================================
# 测试API端点
# =============================================================================

@pytest.mark.asyncio
async def test_optimize_endpoint_structure():
    from app.api.orchestration import OptimizationRequest
    
    request = OptimizationRequest(
        resume_text=SAMPLE_RESUME,
        jd_text=SAMPLE_JD,
        slot=1,
        stream=True
    )
    
    assert request.resume_text == SAMPLE_RESUME
    assert request.stream == True

def test_agent_status_response():
    from app.api.orchestration import AgentStatusResponse
    
    response = AgentStatusResponse(
        agents={"planner": "ready"},
        status="ready",
        queue_length=0
    )
    
    assert "planner" in response.agents
    assert response.status == "ready"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
