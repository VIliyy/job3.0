# Job3.0 多Agent协作系统

## 概述

Job3.0 多Agent协作系统是一个基于LangGraph的智能简历优化平台，通过多个专业Agent的协作，实现简历智能解析、JD深度分析、自动化优化、面试准备和职业规划的全链路服务。

## 核心特性

### 🤖 多Agent协作架构

系统包含6个专业Agent：

| Agent | 功能 | 描述 |
|-------|------|------|
| **PlannerAgent** | 任务分解 | 分析简历薄弱环节，生成优化任务列表 |
| **RecruiterAgent** | HR视角评估 | 模拟资深HR，评估简历与职位的匹配度 |
| **WriterAgent** | 内容优化 | 基于STAR法则优化简历内容 |
| **CriticAgent** | 质量把关 | 严格评估优化结果，判断是否达标 |
| **InterviewerAgent** | 面试题生成 | 生成个性化的技术题和行为题 |
| **AdvisorAgent** | 职业规划 | 制定3-6-12月的职业发展计划 |

### 📊 状态机编排

使用LangGraph实现状态机编排，支持：
- 条件边：CriticAgent决定是否继续迭代
- 并行执行：Interviewer和Advisor可并行运行
- 状态共享：所有Agent共享统一的状态
- 迭代控制：自动收敛，避免无限循环

### ⚡ 流式输出

支持SSE实时流式输出，用户可以：
- 实时查看每个Agent的思考过程
- 看到优化进度的动态更新
- 第一时间获取优化结果

### 🎯 智能收敛

内置智能收敛机制：
- **最大迭代次数**：5轮（可配置）
- **目标分数阈值**：80分
- **收敛耐心度**：连续2轮改进小于5%则收敛

## 技术栈

### 后端
- **FastAPI**: 高性能API框架
- **LangGraph**: Agent状态机编排
- **OpenAI/DeepSeek**: LLM服务
- **SQLite**: 本地数据库

### 前端
- **Vue 3**: SPA应用
- **Pinia**: 状态管理
- **SSE**: 流式输出
- **Vite**: 构建工具

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

requirements.txt 包含：
```
langchain==0.1.0
langgraph==0.0.15
sse-starlette==1.8.2
```

### 2. 配置API Key

在 `backend/.env` 中配置：
```
OPENAI_API_KEY=sk-your-key
DEEPSEEK_API_KEY=sk-your-key
API_PROVIDER=deepseek
```

### 3. 启动服务

**后端**：
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**前端**：
```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用

- 前端：http://localhost:5173
- 后端API：http://localhost:8000/docs
- 优化页面：http://localhost:5173/#/optimize

## API接口

### 简历优化（非流式）

```http
POST /api/orchestration/optimize
Content-Type: application/json

{
  "resume_text": "简历内容...",
  "jd_text": "JD内容...",
  "slot": 1,
  "stream": true
}
```

### 简历优化（流式）

```http
POST /api/orchestration/optimize-stream
```

使用SSE协议，实时推送优化进度。

### Agent状态查询

```http
GET /api/orchestration/status
```

返回示例：
```json
{
  "agents": {
    "planner": "ready",
    "recruiter": "ready",
    "writer": "ready",
    "critic": "ready",
    "interviewer": "ready",
    "advisor": "ready"
  },
  "status": "ready",
  "queue_length": 0
}
```

## 工作流程

```
[简历上传] 
    ↓
[简历分析 Node] → 分析简历结构、提取关键信息
    ↓
[JD解析 Node] → 解析职位描述、提取技能要求
    ↓
[Planner Agent] → 识别薄弱环节、生成优化任务
    ↓
[Recruiter Agent] → HR视角评估、招聘要求匹配
    ↓
[Writer Agent] → 基于STAR法则优化内容
    ↓
[Critic Agent] → 质量评估、判断是否继续迭代
    ↓
  ┌────┴────┐
  ↓         ↓
[继续迭代] [并行分支]
  ↓         ├→ [Interviewer Agent] → 生成面试题库
  └─────────┴→ [Advisor Agent] → 制定职业规划
                    ↓
                [优化完成]
```

## 配置参数

### 迭代参数

在 `backend/app/agents/langgraph_agent.py` 中配置：

```python
MAX_ITERATIONS = 5  # 最大迭代次数
MIN_MATCH_SCORE = 80  # 目标分数
CONVERGENCE_PATIENCE = 2  # 收敛耐心度
MIN_IMPROVEMENT_THRESHOLD = 5  # 最小改进阈值
```

### Agent参数

```python
AGENT_CONFIGS = {
    "planner": {"temperature": 0.3, "max_tokens": 2000},
    "recruiter": {"temperature": 0.5, "max_tokens": 2000},
    "writer": {"temperature": 0.7, "max_tokens": 3000},
    "critic": {"temperature": 0.2, "max_tokens": 2000},
    "interviewer": {"temperature": 0.6, "max_tokens": 3000},
    "advisor": {"temperature": 0.5, "max_tokens": 2500}
}
```

## 错误处理

系统内置完善的错误处理机制：

1. **API超时**: 自动重试3次，指数退避
2. **Agent失败**: 降级到简单模式，继续执行
3. **迭代死循环**: 强制收敛，保护资源
4. **Token超限**: 智能截断，保留关键信息

详细错误信息请参考 `bad.md`。

## 前端集成

### 使用composable

```javascript
import { useAgentOrchestration } from '@/composables/useAgentOrchestration.js'

const {
  steps,
  messages,
  isRunning,
  error,
  optimizationResult,
  progress,
  runOptimization
} = useAgentOrchestration()

// 开始优化
await runOptimization(resumeText, jdText)
```

### 使用组件

在路由 `/optimize` 下使用 `Optimization.vue` 组件。

## 测试

### 运行测试

```bash
cd backend
pytest tests/ -v
```

### 测试覆盖

- Agent单元测试
- API集成测试
- LangGraph状态机测试
- SSE流式输出测试

## 性能优化

### 并行化策略

- Agent并行：Interviewer和Advisor在Critic之后并行执行
- Token并行：多个短prompt可以合并调用
- 缓存优化：相同简历+JD的结果缓存

### 资源限制

每个Agent的最大资源：
- max_tokens: 2000-3000
- timeout: 30秒
- cache_ttl: 3600秒

## 部署建议

### 开发环境

```
前端: localhost:5173
后端: localhost:8000
数据库: SQLite (本地文件)
```

### 生产环境

```
前端: Nginx (静态文件)
后端: Uvicorn (多进程)
数据库: PostgreSQL (可选)
缓存: Redis (可选)
AI服务: OpenAI API / DeepSeek API
```

## 常见问题

### Q: 如何调整优化强度？

A: 修改 `MAX_ITERATIONS` 和 `MIN_MATCH_SCORE` 参数。

### Q: 如何添加新的Agent？

A: 
1. 在 `langgraph_agent.py` 中创建节点函数
2. 添加Prompt模板
3. 在StateGraph中添加节点和边
4. 更新前端Agent名称映射

### Q: 流式输出中断怎么办？

A: 后端会保持执行，前端重连后可获取结果。

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 版本历史

- **v1.0.0** (2026-08-07)
  - 初始版本
  - 6个专业Agent
  - LangGraph状态机
  - SSE流式输出

---

**开发者**: 林育丞
**项目**: Job3.0 智能求职管理系统
**文档版本**: 1.0.0
