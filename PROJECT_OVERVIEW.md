# 🎉 Job3.0 求职系统 - 项目概览

**版本**: v1.0.0  
**技术栈**: Vue 3 + FastAPI + SQLite  
**设计风格**: Cohere + Linear  
**更新**: 2026-08-04 14:39  
**开发者**: 林育丞  

---

## 🎯 项目定位

`
AI-Resume-Agent = 单次简历优化工具
Job3.0 = 求职管理系统（简历+投递+打招呼语+Agent）

定位：
  • 帮助用户管理整个求职过程
  • 不只是一次性工具，而是持续使用的系统
  • 有数据积累，越用越懂你
`

---

## 🏗️ 技术架构

`
┌─────────────────────────────────────────────────────────┐
│                      前端 (Vue 3)                        │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│   │Dashboard│  │ Resume  │  │ JD分析  │  │ Agent   │ │
│   │ 仪表盘   │  │ 简历管理 │  │ 上传分析 │  │ 对话    │ │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    后端 (FastAPI)                         │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│   │ Resume  │  │   JD    │  │Greeting │  │ Agent   │ │
│   │ 简历API │  │ JD处理  │  │打招呼语 │  │ 对话API │ │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   数据库 (SQLite)                         │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│   │ Resumes │  │   Apps  │  │Greetings│              │
│   │ 简历表  │  │投递记录 │  │模板表   │              │
│   └─────────┘  └─────────┘  └─────────┘              │
└─────────────────────────────────────────────────────────┘
`

---

## 📦 功能清单

### ✅ 核心功能

| 模块 | 功能 | 说明 |
|------|------|------|
| **简历管理** | 4个版本槽位 | 上传/删除/切换 |
| **JD处理** | 截图OCR识别 | 基础解析 |
| | JD深度分析 | AI能力 |
| | 公司安全性查询 | 简化版 |
| **简历优化** | JD匹配分析 | AI能力 |
| | 优化建议 | AI能力 |
| **打招呼语** | 模板管理 | CRUD |
| | 智能生成 | AI能力（Boss/猎聘/邮件） |
| **投递记录** | 记录管理 | CRUD |
| | 重复检测 | 模糊匹配 |
| **Agent对话** | 智能问答 | AI能力 |
| | 求职建议 | AI能力 |

### 🔧 技术亮点

- **Cohere + Linear混合风格**：专业+温暖+科技感
- **6色Agent系统**：深色背景更醒目
- **SQLite本地存储**：无需安装数据库
- **AI能力集成**：OpenAI API支持

---

## 🗂️ 项目结构

`
E:\job3.0\
│
├── frontend/                              # Vue 3 前端
│   ├── src/
│   │   ├── assets/styles/
│   │   │   ├── variables.css        # CSS变量（设计规范）
│   │   │   ├── base.css             # 基础样式
│   │   │   └── animations.css       # 动画定义
│   │   │
│   │   ├── components/
│   │   │   ├── common/              # 通用组件
│   │   │   │   ├── BaseButton.vue  # Cohere pill按钮
│   │   │   │   ├── BaseCard.vue     # 22px大圆角卡片
│   │   │   │   ├── BaseInput.vue    # Linear聚焦输入
│   │   │   │   ├── BaseTag.vue      # 珊瑚色标签
│   │   │   │   └── AppLayout.vue   # Cohere白色导航
│   │   │   │
│   │   │   ├── resume/             # 简历组件
│   │   │   └── agent/               # Agent组件
│   │   │
│   │   ├── views/                  # 页面
│   │   ├── stores/                 # Pinia状态
│   │   ├── api/                    # API调用
│   │   └── router/                 # 路由配置
│   │
│   ├── DESIGN.md                    # 设计规范 ⭐
│   ├── QUICKSTART.md               # 快速启动 ⭐
│   ├── bad.md                      # 错误预警 ⭐
│   └── package.json
│
├── backend/                              # Python FastAPI 后端
│   ├── app/
│   │   ├── api/                      # API路由
│   │   │   ├── ai.py                # AI能力API ⭐
│   │   │   ├── resume.py            # 简历管理
│   │   │   ├── application.py       # 投递记录
│   │   │   ├── greeting.py          # 打招呼语
│   │   │   └── ...
│   │   │
│   │   ├── agents/                   # AI Agent ⭐
│   │   │   ├── prompts.py          # Prompt模板
│   │   │   ├── base.py             # AI服务基类
│   │   │   ├── analyzer.py        # JD分析
│   │   │   ├── matcher.py         # 简历匹配
│   │   │   ├── greeter.py         # 打招呼语
│   │   │   ├── advisor.py         # 求职建议
│   │   │   ├── README.md         # 开发指南
│   │   │   └── bad.md            # 错误预警
│   │   │
│   │   ├── models/                  # 数据库模型
│   │   ├── schemas/                 # Pydantic模型
│   │   ├── services/               # 业务逻辑
│   │   └── core/                   # 核心配置
│   │
│   ├── job3.db                      # SQLite数据库 ⭐
│   ├── db_manager.py               # 数据库管理工具 ⭐
│   ├── start.bat                    # Windows启动脚本 ⭐
│   ├── start.sh                    # Linux启动脚本
│   ├── requirements.txt             # Python依赖
│   ├── QUICKSTART.md               # 快速启动
│   ├── database_guide.md           # 数据库指南
│   └── README.md                   # 后端说明
│
├── QUICKSTART.md                    # 项目总览 ⭐
├── START_NOW.md                    # 快速启动 ⭐
├── README.md                       # 项目总览
└── bad.md                          # 项目错误预警
`

---

## 🚀 快速启动

### Windows

`powershell
# 1. 后端
cd E:\job3.0\backend
.\start.bat

# 2. 前端（新终端）
cd E:\job3.0\frontend
npm install
npm run dev
`

### 访问

`
前端：http://localhost:5173
后端：http://localhost:8000/docs
`

---

## 🎨 设计风格

### Cohere企业AI风

`
温暖友好：soft-stone暖灰背景
专业可信：企业级AI平台形象
独特视觉：6色Agent系统
`

### Linear技术细节

`
极简阴影：Level 1-4阴影系统
精致细节：负字间距Display标题
聚焦蓝：输入框聚焦状态
`

### 色彩系统

`
主色：#17171c (近黑)
背景：#ffffff (纯白)
暖灰：#eeece7 (soft-stone)
深绿：#003c33 (深绿技术带)
深蓝：#071829 (深蓝技术带)
珊瑚：#ff7759 (强调色)
`

---

## 🤖 AI Agent能力

### 打招呼语生成

`
输入：简历信息 + JD内容
输出：
  • BOSS直聘版（50字）
  • 猎聘版（100字）
  • 邮件版（150字）
`

### JD深度分析

`
输入：JD文本
输出：
  • 公司/职位/薪资
  • 核心技能 + 加分技能
  • 风险提示（加班/裁员）
  • JD质量评估
`

### 简历智能匹配

`
输入：简历文本 + JD文本
输出：
  • 匹配分数（0-100）
  • 匹配/缺失技能
  • 优化建议
  • ATS关键词优化
`

### 求职建议

`
输入：用户画像
输出：
  • 求职策略
  • 目标公司类型
  • 薪资行情
  • 行动计划
`

---

## 📚 文档索引

### 前端

| 文档 | 说明 |
|------|------|
| rontend/DESIGN.md | 设计规范（颜色/圆角/字体/组件） |
| rontend/QUICKSTART.md | 快速启动 |
| rontend/bad.md | 错误预警 |

### 后端

| 文档 | 说明 |
|------|------|
| ackend/README.md | 后端使用说明 |
| ackend/QUICKSTART.md | 后端快速启动 |
| ackend/database_guide.md | 数据库指南 |
| ackend/app/agents/README.md | AI Agent开发指南 |
| ackend/app/agents/bad.md | AI错误预警 |

### 项目

| 文档 | 说明 |
|------|------|
| QUICKSTART.md | 项目总览 |
| START_NOW.md | 快速启动 |
| README.md | 项目说明 |
| ad.md | 项目错误预警 |

---

## ⚙️ 配置

### 数据库

`
数据库：SQLite（本地存储）
文件：E:\job3.0\backend\job3.db
管理：python backend/db_manager.py
`

### AI能力（可选）

`ash
# Windows
set OPENAI_API_KEY=sk-your-key

# Linux/macOS
export OPENAI_API_KEY=sk-your-key
`

---

## 🎯 开发路线图

### Phase 1：核心功能 ✅ 已完成
- [x] 后端API搭建
- [x] 数据库模型
- [x] AI Agent基础
- [x] 前端设计规范

### Phase 2：前端完善 🔧 进行中
- [ ] ResumeManager页面
- [ ] Applications页面
- [ ] GreetingTemplates页面

### Phase 3：AI增强 📋 待开发
- [ ] SSE流式输出
- [ ] DeepSeek模型
- [ ] 百度OCR集成

---

## 🎉 项目亮点

1. **设计独特**：Cohere+Linear混合风格
2. **技术先进**：Vue 3 + FastAPI + AI
3. **数据本地**：SQLite无需安装
4. **功能完整**：简历+投递+打招呼语+Agent
5. **易于上手**：详细文档+快速启动

---

## 📞 联系方式

如有问题，请查阅文档或联系开发者。

---

**祝开发顺利！ 🚀**

**版本**: v1.0.0  
**更新**: 2026-08-04 14:39
