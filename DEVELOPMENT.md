# Job3.0 求职系统 - 项目规划

> 版本: v2.0.0
> 更新: 2026-08-05
> 开发者: 林育丞

---

## 📌 项目定位

**Job3.0 = 求职管理系统（简历 + JD分析 + 打招呼语 + 投递追踪 + AI Agent）**

帮助用户管理整个求职过程，有数据积累，越用越懂你。

---

## ✅ 已完成功能

### 核心功能

| 模块 | 功能 | 状态 |
|------|------|------|
| **简历管理** | 4个版本槽位上传/删除/切换 | ✅ |
| **JD处理** | 截图OCR识别 | ✅ |
| **打招呼语** | 模板管理 + 多平台生成 | ✅ |
| **投递记录** | CRUD + 状态追踪 | ✅ |
| **Agent对话** | 智能问答 + 自主搜索 | ✅ |

### Agent 能力 (v2.0)

- ✅ **多轮对话记忆** - 跨页面保持上下文
- ✅ **自动识别 JD** - 直接粘贴 JD 自动分析
- ✅ **自动搜索简历** - 说"我的简历"自动获取
- ✅ **智能打招呼语生成** - 告诉公司名自动生成
- ✅ **投递工作流引导** - 主动引导用户完成投递
- ✅ **意图识别** - 理解用户求职意图

### 技术栈

- **前端**: Vue 3 + Vite + Pinia
- **后端**: FastAPI + SQLAlchemy
- **数据库**: SQLite 本地存储
- **AI**: DeepSeek / OpenAI API

---

## 🚧 进行中

### 投递工作流增强

- [ ] JD → 打招呼语 → 投递记录 一键串联
- [ ] 投递状态自动更新提醒
- [ ] 投递效果统计分析

---

## 📋 待开发功能

### 高优先级 ⭐⭐⭐

#### 1. 简历-JD 匹配可视化

```
目标：直观展示匹配度

功能：
- 技能对比雷达图
- 匹配项 vs 缺失项可视化
- ATS 关键词覆盖率
- 改进建议排序
- 导出匹配报告 (PDF/Markdown)
```

#### 2. Agent 流式输出

```
目标：Agent 边想边说，更自然

功能：
- SSE 流式响应
- 打字机效果
- 思考过程可见
- 支持中断生成
```

#### 3. 数据导出与备份

```
目标：数据可迁移、可备份

功能：
- 一键导出所有数据 (JSON)
- 简历导出 (PDF/Word)
- 投递记录导出 (Excel)
- 数据导入恢复
```

### 中优先级 ⭐⭐

#### 4. 多语言简历

```
目标：支持外企求职

功能：
- 中译英自动翻译
- 英文简历模板
- 中英对照版本
- 针对 ATS 优化
```

#### 5. AI 模拟面试

```
目标：面试前练习

功能：
- 根据 JD 生成面试题
- AI 模拟面试官
- STAR 法则回答练习
- 回答评分与反馈
```

#### 6. 投递提醒系统

```
目标：不忘跟进

功能：
- 超时未回复提醒
- 面试时间提醒
- 重复投递检测
- 每日求职总结
```

### 低优先级 ⭐

#### 7. 简历评分系统

```
目标：量化简历质量

功能：
- 结构完整性评分
- 关键词覆盖率
- 量化成果占比
- 整体评分与排名
```

#### 8. 职位搜索聚合

```
目标：一站式搜索

功能：
- 聚合多平台职位
- 简历匹配度排序
- 一键申请追踪
```

---

## 🎨 设计规范

采用 **Cohere + Linear** 混合风格：

### 色彩系统

```
主色：#17171c (近黑)
背景：#ffffff (纯白)
暖灰：#eeece7 (soft-stone)
深绿：#003c33 (深绿技术带)
深蓝：#071829 (深蓝技术带)
珊瑚：#ff7759 (强调色)
```

### 组件风格

- **按钮**: Cohere pill 风格
- **卡片**: Linear 22px 大圆角
- **输入框**: Linear 聚焦蓝边框
- **标签**: 珊瑚色背景

详见: `frontend/DESIGN.md`

---

## 📁 项目结构

```
E:\job3.0\
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── api/               # API 调用
│   │   └── stores/            # Pinia 状态
│   └── DESIGN.md               # 设计规范
│
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── agents/            # AI Agent
│   │   ├── services/          # 业务逻辑
│   │   └── models/            # 数据库模型
│   └── job3.db                # SQLite 数据库
│
├── awesome-design-md/          # 设计参考库
└── README.md                   # 项目说明
```

---

## 🔧 开发指南

### 快速启动

```bash
# 后端
cd backend
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm run dev
```

### API 文档

- 后端: http://localhost:8000/docs
- 前端: http://localhost:5173

### 环境变量

```bash
# backend/.env
DEEPSEEK_API_KEY=sk-xxx        # DeepSeek API Key
DEEPSEEK_MODEL=deepseek-reasoner
```

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| `README.md` | 项目总览 |
| `frontend/DESIGN.md` | 前端设计规范 |
| `frontend/QUICKSTART.md` | 前端快速启动 |
| `backend/README.md` | 后端使用说明 |
| `backend/database_guide.md` | 数据库指南 |
| `backend/app/agents/README.md` | AI Agent 开发指南 |

---

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing`)
5. 创建 Pull Request

---

## 📄 License

MIT License

---

**祝开发顺利！ 🚀**
