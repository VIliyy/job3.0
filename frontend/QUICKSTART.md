# 🚀 Job3.0 前端 - 快速启动指南

**版本**: v2.0  
**设计风格**: Cohere + Linear  
**更新**: 2026-08-04 14:38  
**开发者**: 林育丞  

---

## 🎯 快速启动（1分钟）

### 1. 安装依赖

`powershell
cd E:\job3.0\frontend
npm install
`

### 2. 启动开发服务器

`powershell
npm run dev
`

### 3. 访问

`
http://localhost:5173
`

---

## 📦 项目结构

`
frontend/
├── src/
│   ├── assets/
│   │   └── styles/
│   │       ├── variables.css    # CSS变量（Cohere+Linear）
│   │       ├── base.css         # 基础样式
│   │       └── animations.css   # 动画定义
│   │
│   ├── components/
│   │   ├── common/              # 通用组件
│   │   │   ├── BaseButton.vue   # Cohere pill按钮
│   │   │   ├── BaseCard.vue     # 22px大圆角卡片
│   │   │   ├── BaseInput.vue    # Linear聚焦输入
│   │   │   ├── BaseTag.vue      # 珊瑚色标签
│   │   │   └── AppLayout.vue   # Cohere白色导航
│   │   │
│   │   ├── resume/              # 简历组件
│   │   └── agent/               # Agent组件
│   │
│   ├── views/                   # 页面
│   ├── stores/                 # Pinia状态
│   ├── api/                    # API调用
│   └── router/                 # 路由
│
├── package.json
├── vite.config.js
├── DESIGN.md                   # 设计规范
└── bad.md                     # 错误预警
`

---

## 🎨 设计风格速查

### 颜色速查

`
主色：var(--color-primary)         #17171c (近黑)
背景：var(--color-canvas)           #ffffff (纯白)
暖灰：var(--color-soft-stone)      #eeece7
深绿：var(--color-deep-green)      #003c33 (Agent)
深蓝：var(--color-dark-navy)      #071829 (数据)
蓝：var(--color-action-blue)       #1863dc
珊瑚：var(--color-coral)          #ff7759
`

### 圆角速查

`
4px  ：小按钮、标签
8px  ：输入框
16px ：中等卡片
22px ：大卡片（品牌特色）
32px ：CTA按钮（品牌特色）
`

### 间距速查

`
8px  基础单位
12px 小间距
16px 中间距
24px 大间距
32px 更大间距
`

---

## 🔧 常用组件

### 1. BaseButton

`ue
<BaseButton type=\"primary\" size=\"md\">开始</BaseButton>
<BaseButton type=\"secondary\">取消</BaseButton>
<BaseButton type=\"ghost\">查看</BaseButton>
<BaseButton type=\"danger\">删除</BaseButton>
<BaseButton :loading=\"true\">加载中</BaseButton>
`

### 2. BaseCard

`ue
<!-- 默认白色 -->
<BaseCard>内容</BaseCard>

<!-- 暖灰背景 -->
<BaseCard variant=\"stone\">内容</BaseCard>

<!-- 深绿背景（Agent） -->
<BaseCard variant=\"deep-green\">内容</BaseCard>

<!-- 深蓝背景（数据） -->
<BaseCard variant=\"dark-navy\">内容</BaseCard>

<!-- 带阴影 -->
<BaseCard :shadow=\"true\">内容</BaseCard>
`

### 3. BaseInput

`ue
<!-- 文本输入 -->
<BaseInput v-model=\"value\" label=\"用户名\" placeholder=\"请输入\" />

<!-- 多行文本 -->
<BaseInput type=\"textarea\" v-model=\"value\" :rows=\"6\" />

<!-- 错误提示 -->
<BaseInput v-model=\"value\" :error=\"'输入错误'\" />
`

### 4. BaseTag

`ue
<BaseTag>默认</BaseTag>
<BaseTag type=\"success\">成功</BaseTag>
<BaseTag type=\"warning\">警告</BaseTag>
<BaseTag type=\"error\">错误</BaseTag>
<BaseTag type=\"coral\">珊瑚</BaseTag>
`

---

## 📝 页面布局对照

### Dashboard（首页）

`
背景：白色 + soft-stone暖灰
卡片：BaseCard（默认白色）
强调：soft-stone暖灰区块
`

### Results（结果页）

`
背景：深蓝评分区 + soft-stone建议区
评分：BaseCard variant=\"dark-navy\"
建议：BaseCard variant=\"stone\"
`

### AgentChat（Agent对话）

`
背景：深绿 + 深蓝技术带
卡片：BaseCard variant=\"deep-green\"
对话：BaseCard variant=\"dark-navy\"
`

---

## 🚀 开发命令

`ash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产
npm run build

# 预览构建
npm run preview

# 代码检查
npm run lint
`

---

## ⚠️ 重要提示

### 1. CSS变量

`css
/* ❌ 禁止硬编码 */
color: #17171c;
background: #ffffff;

/* ✅ 必须使用 */
color: var(--color-primary);
background: var(--color-canvas);
`

### 2. 圆角

`css
/* ❌ 禁止 */
border-radius: 10px;

/* ✅ 必须 */
border-radius: var(--radius-lg);  /* 22px */
`

### 3. 间距

`css
/* ❌ 禁止 */
margin: 20px;
padding: 15px;

/* ✅ 必须 */
margin: var(--spacing-lg);  /* 24px */
`

---

## 📚 详细文档

| 文档 | 路径 | 说明 |
|------|------|------|
| **设计规范** | DESIGN.md | 完整设计系统 |
| **错误预警** | ad.md | 常见错误排查 |
| **CSS变量** | src/assets/styles/variables.css | 所有CSS变量 |

---

## 🎨 快速参考卡

`
┌─────────────────────────────────────┐
│  Cohere + Linear 设计速查           │
├─────────────────────────────────────┤
│  主色：#17171c                       │
│  背景：#ffffff                       │
│  暖灰：#eeece7                       │
│  深绿：#003c33 (Agent)              │
│  深蓝：#071829 (数据)               │
│  珊瑚：#ff7759                       │
├─────────────────────────────────────┤
│  圆角：4/8/16/22/32px               │
│  间距：8px倍数                       │
│  阴影：Level 1-4                    │
├─────────────────────────────────────┤
│  Display：48/36/28px + 负字间距      │
│  正文：16px                          │
├─────────────────────────────────────┤
│  Agent色：紫/粉/绿/橙/青/红         │
└─────────────────────────────────────┘
`

---

## 🎉 启动成功！

`
前端：http://localhost:5173
后端：http://localhost:8000/docs
`

---

**有问题？查看详细文档：**
- DESIGN.md - 设计规范
- ad.md - 错误预警
