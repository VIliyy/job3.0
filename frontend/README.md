# Job3.0 前端项目

**版本**: v2.1  
**更新日期**: 2026-08-04  
**开发者**: 林育丞

---

## 📋 项目概述

Job3.0 是一个智能求职辅助平台的前端应用，采用 Vue 3 + Vite + Pinia 技术栈，设计风格融合了 Cohere 企业AI风格和 Linear 技术细节。

### 核心功能

- **简历管理**: 支持4个简历版本槽位，上传、编辑、删除、切换使用
- **投递记录**: 追踪求职进度，状态管理，重复投递检测
- **打招呼语**: 模板管理，AI生成多平台版本（BOSS直聘、猎聘、邮件）
- **上传分析**: 简历和JD上传/粘贴，AI智能分析，匹配度评分
- **AI助手**: 智能问答，求职建议，简历优化指导

---

## 🚀 快速开始

### 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0 或 yarn >= 1.22.0

### 安装依赖

```bash
cd frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

---

## 📁 项目结构

```
frontend/
├── src/
│   ├── api/                 # API接口定义
│   │   └── index.js        # API客户端配置
│   ├── assets/
│   │   └── styles/         # 全局样式
│   │       ├── variables.css  # CSS变量定义
│   │       ├── base.css      # 基础样式
│   │       └── animations.css # 动画定义
│   ├── components/          # 公共组件
│   │   ├── common/         # 通用组件
│   │   ├── agent/          # Agent相关组件
│   │   └── resume/         # 简历相关组件
│   ├── router/             # 路由配置
│   ├── stores/             # Pinia状态管理
│   │   └── index.js        # Store定义
│   ├── views/              # 页面组件
│   │   ├── Dashboard.vue   # 首页/仪表盘
│   │   ├── Resumes.vue     # 简历管理
│   │   ├── Applications.vue # 投递记录
│   │   ├── Greetings.vue   # 打招呼语
│   │   ├── Upload.vue       # 上传分析
│   │   ├── Agent.vue       # AI助手
│   │   ├── History.vue     # 历史记录
│   │   └── Settings.vue    # 设置
│   ├── App.vue             # 根组件
│   └── main.js             # 入口文件
├── public/                 # 静态资源
├── index.html             # HTML模板
├── vite.config.js         # Vite配置
├── package.json           # 项目依赖
└── bad.md                 # 错误预警清单 ⚠️ 必读
```

---

## 🎨 设计规范

### 设计风格

- **主色调**: Cohere企业AI风格（#17171c）
- **行动色**: Linear技术蓝（#1863dc）
- **圆角系统**: 4px / 8px / 16px / 22px / 32px
- **字体**: 系统字体栈，Display层级使用负字间距

### CSS变量使用

所有样式必须使用CSS变量，禁止硬编码颜色值：

```css
/* ✅ 正确 */
color: var(--color-primary);
background: var(--color-canvas);

/* ❌ 错误 */
color: #17171c;
background: #ffffff;
```

### 页面布局

| 页面 | 最大宽度 | 背景色 |
|------|---------|--------|
| Dashboard | 1200px | #ffffff |
| 简历管理 | 1200px | #ffffff |
| 上传分析 | 1000px | #ffffff |
| AI助手 | 900px | #003c33（深色） |
| 投递记录 | 1000px | #ffffff |

---

## 🔌 API集成

### 后端服务

确保后端服务运行在 http://localhost:8000

### API端点

```javascript
// 简历管理
POST   /api/resume/upload      # 上传简历
GET    /api/resume/list        # 获取简历列表
GET    /api/resume/{slot}      # 获取指定槽位简历
PUT    /api/resume/{slot}      # 更新简历
DELETE /api/resume/{slot}      # 删除简历

// 投递记录
GET    /api/applications       # 获取投递列表
POST   /api/applications       # 添加投递
PUT    /api/applications/{id}  # 更新投递
DELETE /api/applications/{id}  # 删除投递

// JD解析
POST   /api/jd/parse           # 解析JD
POST   /api/jd/ocr             # OCR识别

// AI助手
POST   /api/agent/chat         # AI对话
```

### CORS配置

后端需要配置CORS允许前端访问：

```javascript
app.use(cors({
  origin: '\''http://localhost:5173'\'',
  credentials: true
}))
```

---

## 📊 状态管理

使用 Pinia 进行状态管理，主要Store包括：

### ResumeStore（简历管理）

```javascript
import { useResumeStore } from '\''@/stores'\''

const store = useResumeStore()

// 获取简历
store.resumes
store.activeSlot

// 操作
store.addResume(1, { name: '\''简历1'\'', fileType: '\''PDF'\'' })
store.setActiveSlot(2)
store.deleteResume(1)
```

### ApplicationStore（投递记录）

```javascript
import { useApplicationStore } from '\''@/stores'\''

const store = useApplicationStore()

// 获取统计数据
store.totalCount
store.interviewCount
store.offerCount

// 操作
store.addApplication({ company: '\''公司'\'', position: '\''岗位'\'' })
store.updateStatus(id, '\''面试中'\'')
```

### GreetingStore（打招呼语）

```javascript
import { useGreetingStore } from '\''@/stores'\''

const store = useGreetingStore()

// 生成打招呼语
const greeting = store.generateGreeting('\''公司'\'', '\'\'岗位'\'', '\'\''亮点'\'')
console.log(greeting.boss)    // BOSS直聘版
console.log(greeting.liepin)  // 猎聘版
console.log(greeting.email)   // 邮件版
```

---

## ⚠️ 重要提醒

### 1. 文件编码

所有 .vue 文件必须使用 **UTF-8** 编码，否则中文会显示为乱码。

**VS Code设置**：
```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": true
}
```

### 2. 错误预警清单

在开发过程中遇到任何问题，请先查阅 `bad.md` 文件，其中包含了：

- 🔴 高优先级预警（编码、API、状态管理）
- 🟡 中优先级预警（设计规范、组件使用）
- 🟢 低优先级预警（性能优化）

### 3. 样式规范

- 使用CSS变量而非硬编码值
- 遵循圆角系统（4/8/16/22/32px）
- 使用规范间距（8px倍数）
- Display层级使用负字间距

---

## 🛠️ 开发工具

### 推荐VS Code扩展

- **Volar**: Vue 3 官方支持
- **ESLint**: 代码检查
- **Prettier**: 代码格式化
- **Vue - Official**: Vue组件支持

### 代码检查

```bash
# 运行ESLint
npm run lint

# 修复可自动修复的问题
npm run lint -- --fix
```

---

## 📝 更新日志

### v2.1 (2026-08-04)

**新增功能**:
- ✨ Upload页面完整功能：简历上传、JD上传/粘贴、AI分析
- ✨ 状态管理系统：完整的Pinia Store配置
- ✨ 错误预警文档：详细的编码、API、状态管理预警

**修复问题**:
- 🔧 修复所有Vue文件中文乱码问题
- 🔧 完善各模块功能和交互

**改进**:
- 🎨 优化UI细节和用户体验
- 📚 完善文档和注释

### v2.0 (2026-08-04)

- 🎨 Cohere+Linear混合设计风格
- 🔄 完整的前端框架搭建

### v1.0 (2026-08-04)

- 🚀 项目初始化
- 📄 基础页面结构

---

## 📞 联系方式

- **开发者**: 林育丞
- **版本**: v2.1
- **更新**: 2026-08-04

---

**Happy Coding! 🎉**
