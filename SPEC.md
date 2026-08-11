# 多Agent协作系统 - 需求规格说明书 (SPEC.md)

**版本**: 1.0.0
**制定时间**: 2026-08-07
**目标**: 实现智能简历评估与职业规划的多Agent协作系统
**开发者**: 林育丞（AI团队）

---

## 1. 项目概述

### 1.1 项目名称
**Job3.0 Multi-Agent Orchestration System**
多Agent协作简历优化系统

### 1.2 项目目标
构建一个基于LangGraph的多Agent协作系统，实现简历智能解析、JD深度分析、自动化优化、面试准备和职业规划的全链路服务。

### 1.3 核心价值
- **智能化**: 多Agent协作，模拟真实招聘流程
- **自动化**: 从简历分析到优化建议全自动完成
- **透明化**: 流式输出每个Agent的思考过程
- **迭代化**: 多轮优化确保最优结果

---

## 2. 系统架构

### 2.1 整体架构图

`
用户交互层 (Vue 3)
  - 简历上传界面
  - 优化进度展示
  - Agent思考过程可视化

LangGraph 状态机编排层
  - StateGraph (主编排器)
  - Resume Analysis Node
  - JD Parse Node
  - Optimization Loop (最多5轮迭代)

多Agent协作层 (6个专业Agent)
  - Planner Agent (任务分解)
  - Recruiter Agent (HR视角)
  - Writer Agent (内容优化)
  - Interviewer Agent (面试准备)
  - Advisor Agent (职业规划)
  - Critic Agent (质量把关)

工具层
  - 简历解析工具
  - JD解析工具
  - 评分工具

AI服务层
  - GPT-4/4o (主要模型)
  - DeepSeek (备用模型)
`

### 2.2 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 前端 | Vue 3 + Vite | SPA应用 |
| 状态管理 | Pinia | 全局状态 |
| 后端 | FastAPI | 高性能API |
| Agent框架 | LangGraph | 状态机编排 |
| AI服务 | OpenAI SDK | LLM调用 |
| 数据库 | SQLite | 本地存储 |
| 流式输出 | SSE | Server-Sent Events |

---

## 3. Agent详细设计

### 3.1 Agent职责矩阵

| Agent | 核心职责 | 输入 | 输出 |
|-------|---------|------|------|
| PlannerAgent | 任务分解 | 简历+JD | 优化任务列表 |
| RecruiterAgent | HR视角评估 | JD内容 | 招聘要求清单 |
| WriterAgent | 内容优化 | 原始简历+任务 | 优化后简历 |
| InterviewerAgent | 面试题生成 | JD+简历 | 面试题库 |
| AdvisorAgent | 职业规划 | 用户画像 | 3-6-12月计划 |
| CriticAgent | 质量把关 | 优化结果 | 评估报告 |

### 3.2 PlannerAgent 详细规格

#### 功能描述
分析简历结构和JD要求，识别薄弱环节，生成具体的优化任务列表。

#### 输入示例
`json
{
  "resume_text": "简历全文...",
  "jd_text": "JD全文..."
}
`

#### 输出示例
`json
{
  "strengths": [
    {"skill": "Python", "level": "熟练", "evidence": "3年经验"}
  ],
  "weaknesses": [
    {"skill": "项目管理", "gap": "缺少PMP认证", "priority": "high"}
  ],
  "tasks": [
    {"id": 1, "task": "补充项目管理经验描述", "target_section": "工作经历", "priority": "high"}
  ]
}
`

### 3.3 CriticAgent 详细规格

#### 功能描述
对优化后的简历进行质量评估，判断是否达到发布标准。

#### 收敛判断逻辑
- MAX_ITERATIONS = 5 (最多迭代5轮)
- MIN_MATCH_SCORE = 80 (最低匹配分数)
- CONVERGENCE_PATIENCE = 2 (连续2轮改进小于5%则收敛)

#### 输出示例
`json
{
  "overall_score": 85,
  "score_breakdown": {
    "clarity": 90,
    "relevance": 85,
    "quantification": 80,
    "keywords": 85
  },
  "verdict": "PASS",
  "issues": [],
  "improvement": 15,
  "can_publish": true
}
`

---

## 4. 状态机设计 (LangGraph)

### 4.1 StateGraph 结构

`python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    resume_text: str
    jd_text: str
    iteration: int
    match_score: float
    planner_output: dict
    recruiter_output: dict
    writer_output: dict
    critic_output: dict
    messages: list
`

### 4.2 节点定义

| 节点名称 | 功能 | 条件边 |
|---------|------|--------|
| resume_analysis | 简历解析 | jd_parse |
| jd_parse | JD解析 | planner |
| planner | 任务分解 | recruiter |
| recruiter | HR评估 | writer |
| writer | 内容优化 | critic |
| critic | 质量评估 | writer / end |
| interviewer | 面试题生成 | (并行) |
| advisor | 职业规划 | (并行) |

### 4.3 状态流转

`
[简历上传] -> [简历分析] -> [JD解析] -> [Planner] -> [Recruiter]
                                                         |
                                                         v
                                                      [Writer]
                                                         |
                                                         v
                                                      [Critic]
                                                         |
                               +-------------------------+-------------------------+
                               |                         |                         |
                            [PASS]              [NEEDS_IMPROVEMENT]      [REVISION_REQUIRED]
                               |                         |                         |
                              END              [迭代次数++] -> [Writer]      [Writer]
                                                                                   |
                                                                                   v
                                                                                 END
                              
                              同时执行: [Interviewer] -> [面试题库]
                                        [Advisor] -> [职业规划]
`

---

## 5. 流式输出设计 (SSE)

### 5.1 SSE事件类型

| 事件类型 | 说明 |
|---------|------|
| thinking | Agent思考中 |
| output | Agent输出片段 |
| complete | Agent完成 |
| progress | 进度更新 |
| error | 错误信息 |
| final | 最终结果 |

---

## 6. API接口设计

### 6.1 核心接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/agent/optimize | 简历优化(流式) |
| POST | /api/agent/analyze | 简历分析 |
| POST | /api/agent/interview-questions | 面试题生成 |
| POST | /api/agent/career-plan | 职业规划 |
| GET | /api/agent/status | Agent状态查询 |
| GET | /api/agent/history | 优化历史 |

---

## 7. 数据库设计

### 7.1 新增表

- optimization_history (优化历史)
- agent_config (Agent配置)
- score_history (评分历史)

---

## 8. 错误处理与容错

### 8.1 错误分类

| 错误类型 | 处理策略 | 恢复机制 |
|---------|---------|---------|
| API超时 | 重试3次，指数退避 | 降级到简单模式 |
| Agent输出异常 | 跳过该Agent | 使用默认输出 |
| 迭代循环 | 检测死循环 | 强制收敛 |

---

## 9. 里程碑

| 阶段 | 交付内容 |
|------|---------|
| M1 | SPEC.md, 架构设计, LangGraph状态机 |
| M2 | PlannerAgent, CriticAgent, RecruiterAgent |
| M3 | WriterAgent, 集成测试 |
| M4 | 流式输出, 前端集成 |
| M5 | InterviewerAgent, AdvisorAgent |
| M6 | 文档完善, 最终测试, 部署 |

---

**文档版本**: 1.0.0
**制定日期**: 2026-08-07
