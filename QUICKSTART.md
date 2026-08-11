# 🚀 Job3.0 求职系统 - 快速启动指南

**版本**: v1.0.0（前后端完整版 + AI Agent）  
**更新时间**: 2026-08-04 14:27  
**开发者**: 林育丞  

---

## 🎯 快速启动（3分钟）

### 1. 启动后端

`powershell
cd E:\job3.0\backend

# 安装依赖
pip install -r requirements.txt

# 配置AI（可选）
\ = \"sk-your-key\"

# 启动服务
uvicorn app.main:app --reload --port 8000
`

### 2. 启动前端

`powershell
cd E:\job3.0\frontend

# 安装依赖
npm install

# 启动服务
npm run dev
`

### 3. 访问应用

`
前端：http://localhost:5173
后端：http://localhost:8000
API文档：http://localhost:8000/docs
`

---

## 📋 项目完整功能清单

### ✅ 已实现

| 模块 | 功能 | 状态 | 说明 |
|------|------|------|------|
| **简历管理** | 4个版本槽位 | ✅ | 上传/删除/切换 |
| **JD处理** | 截图OCR识别 | ✅ | 基础解析 |
| | JD深度分析 | ✅ | AI能力 |
| | 公司安全性查询 | ✅ | 简化版 |
| **简历优化** | JD匹配分析 | ✅ | AI能力 |
| | 优化建议 | ✅ | AI能力 |
| **打招呼语** | 模板管理 | ✅ | CRUD |
| | 智能生成 | ✅ | AI能力 |
| | 平台适配 | ✅ | BOSS/猎聘/邮件 |
| **投递记录** | 记录管理 | ✅ | CRUD |
| | 重复检测 | ✅ | 模糊匹配 |
| **Agent对话** | 智能问答 | ✅ | AI能力 |
| | 求职建议 | ✅ | AI能力 |

### 🔧 待实现

| 模块 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| **前端** | ResumeManager | 高 | 简历版本管理页面 |
| | Applications | 高 | 投递记录页面 |
| | GreetingTemplates | 中 | 打招呼语管理 |
| | AgentChat | 中 | Agent对话界面 |
| **数据库** | MySQL连接 | 高 | 配置数据库 |
| **AI** | DeepSeek集成 | 中 | 可选国产模型 |
| | 百度OCR | 低 | 截图识别 |

---

## 🗂️ 项目文件清单

`
E:\job3.0\
├── frontend/                              # Vue 3 前端
│   ├── src/
│   │   ├── api/
│   │   │   └── index.js                # API调用（已对接后端）
│   │   ├── views/                       # 6个页面
│   │   ├── components/                  # 组件库
│   │   └── stores/                     # Pinia状态
│   ├── DESIGN.md                        # 设计规范
│   ├── bad.md                          # 错误预警
│   └── modification-plan.md             # 修改计划
│
├── backend/                              # Python FastAPI 后端
│   ├── app/
│   │   ├── api/                        # API路由
│   │   │   ├── resume.py              # 简历管理
│   │   │   ├── application.py         # 投递记录
│   │   │   ├── greeting.py            # 打招呼语
│   │   │   ├── jd.py                  # JD处理
│   │   │   ├── agent.py                # Agent对话
│   │   │   └── ai.py                   # AI能力 ⭐新增
│   │   │
│   │   ├── agents/                     # AI Agent ⭐新增
│   │   │   ├── prompts.py             # Prompt模板
│   │   │   ├── base.py                # AI服务基类
│   │   │   ├── analyzer.py            # JD分析
│   │   │   ├── matcher.py             # 简历匹配
│   │   │   ├── greeter.py            # 打招呼语生成
│   │   │   ├── advisor.py             # 求职建议
│   │   │   ├── README.md              # 开发指南
│   │   │   └── bad.md                 # 错误预警
│   │   │
│   │   ├── models/                    # 数据库模型
│   │   ├── schemas/                   # Pydantic模型
│   │   ├── services/                  # 业务逻辑
│   │   └── core/                      # 核心配置
│   │
│   ├── requirements.txt                 # Python依赖
│   └── README.md                       # 使用说明
│
├── README.md                            # 项目总览
└── bad.md                              # 项目错误预警
`

---

## 🤖 AI Agent 模块详解

### 核心功能

`
打招呼语生成（BOSS/猎聘/邮件）
    ↓
JD深度分析（提取关键信息+风险识别）
    ↓
简历智能匹配（技能+经验+差距）
    ↓
求职建议（策略+公司推荐+薪资估算）
`

### Prompt设计

参考AI-Resume-Agent的架构，我们自研了4套Prompt：

1. **GREETING_PROMPT** - 打招呼语生成
2. **JD_ANALYSIS_PROMPT** - JD分析
3. **RESUME_MATCHING_PROMPT** - 简历匹配
4. **CAREER_ADVICE_PROMPT** - 求职建议

详见：[AI Agent开发指南](backend/app/agents/README.md)

---

## 📦 依赖清单

### 前端
`json
{
  \"vue\": \"^3.4.0\",
  \"vue-router\": \"^4.2.0\",
  \"pinia\": \"^2.1.0\",
  \"axios\": \"^1.6.0\"
}
`

### 后端
`
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
pydantic==2.5.2
openai==1.3.7  # AI能力
python-docx==1.1.0
pdfplumber==0.10.3
`

---

## ⚠️ 重要预警

### 1. 数据库未配置

**必须**：创建MySQL数据库

`sql
CREATE DATABASE job3_db CHARACTER SET utf8mb4;
`

**配置**：修改 ackend/app/core/config.py

`python
DATABASE_URL = \"mysql+pymysql://root:123456@localhost:3306/job3_db\"
`

### 2. AI能力未启用

**可选**：配置OpenAI API Key

`ash
\ = \"sk-your-key\"
`

**无Key时**：使用规则匹配（功能受限）

### 3. 常见错误

详见：
- [前端错误预警](frontend/bad.md)
- [后端错误预警](backend/bad.md)
- [AI Agent错误预警](backend/app/agents/bad.md)

---

## 🚀 开发路线图

### Phase 1：核心功能 ✅ 已完成
- [x] 后端API搭建
- [x] 数据库模型
- [x] AI Agent基础

### Phase 2：前端完善 🔧 进行中
- [ ] ResumeManager页面
- [ ] Applications页面
- [ ] GreetingTemplates页面

### Phase 3：AI增强 📋 待开发
- [ ] SSE流式输出
- [ ] DeepSeek模型
- [ ] 百度OCR集成

---

## 📞 联系方式

如有问题，请查阅文档或联系开发者。

---

**祝开发顺利！ 🚀**
