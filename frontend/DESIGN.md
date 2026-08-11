# 🎨 Job3.0 求职系统 - 前端设计规范 v2.0

**版本**: v2.0  
**设计风格**: Cohere企业AI风 + Linear技术细节  
**更新**: 2026-08-04  
**开发者**: 林育丞  

---

## 一、设计理念

### 1.1 核心理念

`
专业可信：企业级AI平台形象，传达可信赖感
温暖友好：soft-stone暖灰背景适合求职场景
智能布局：深色技术带用于Agent可视化，白色用于主要内容
独特视觉：6色Agent系统在深色背景上更醒目
`

### 1.2 设计关键词

- **企业AI**: Cohere风格的专业感
- **温暖求职**: soft-stone暖灰传递关怀
- **技术可视化**: Linear风格的Agent流程展示
- **现代精致**: 大圆角卡片、负字间距标题

---

## 二、色彩系统

### 2.1 主色系统

| 变量名 | 色值 | 用途 |
|--------|------|------|
| --color-primary | #17171c | 近黑主色 |
| --color-canvas | #ffffff | 纯白画布 |
| --color-soft-stone | #eeece7 | 暖灰辅助 |
| --color-soft-stone-strong | #e5e2db | 更深暖灰 |

### 2.2 深色技术带

| 变量名 | 色值 | 用途 |
|--------|------|------|
| --color-deep-green | #003c33 | Agent协作区域 |
| --color-dark-navy | #071829 | 评分/数据展示 |
| --color-ink | #212121 | 近黑文字 |

### 2.3 强调色

| 变量名 | 色值 | 用途 |
|--------|------|------|
| --color-action-blue | #1863dc | 链接/次要操作 |
| --color-focus-blue | #4c6ee6 | 输入聚焦 |
| --color-coral | #ff7759 | 标签/点缀 |

### 2.4 Agent专属色

| Agent | 变量名 | 色值 | 用途 |
|-------|--------|------|------|
| Planner | --agent-planner | #8B5CF6 | 紫色-任务规划 |
| Recruiter | --agent-recruiter | #EC4899 | 粉色-HR视角 |
| Writer | --agent-writer | #10B981 | 绿色-内容优化 |
| Interviewer | --agent-interviewer | #F59E0B | 橙色-面试准备 |
| Advisor | --agent-advisor | #06B6D4 | 青色-职业规划 |
| Critic | --agent-critic | #EF4444 | 红色-质量把控 |

---

## 三、字体系统

### 3.1 Display层级（负字间距 - Linear特色）

`css
h1 {
  font-size: 48px;      /* var(--font-size-display-xl) */
  letter-spacing: -1.44px;  /* var(--letter-spacing-display-xl) */
}

h2 {
  font-size: 36px;      /* var(--font-size-display-lg) */
  letter-spacing: -0.72px;  /* var(--letter-spacing-display-lg) */
}

h3 {
  font-size: 28px;      /* var(--font-size-display-md) */
  letter-spacing: -0.42px;  /* var(--letter-spacing-display-md) */
}
`

### 3.2 正文层级

`css
p, div, span {
  font-size: 16px;  /* var(--font-size-body) */
  letter-spacing: 0;  /* 正文不使用负字间距 */
}
`

---

## 四、圆角系统（Cohere规格）

| 变量名 | 值 | 用途 |
|--------|------|------|
| --radius-xs | 4px | 小按钮、标签 |
| --radius-sm | 8px | 输入框、次要按钮 |
| --radius-md | 16px | 中等卡片 |
| --radius-lg | 22px | **大卡片（品牌特色）** |
| --radius-pill | 32px | **CTA按钮（品牌特色）** |

---

## 五、间距系统（8px倍数）

`css
--spacing-xxs: 4px;
--spacing-xs: 8px;
--spacing-sm: 12px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-xxl: 48px;
--spacing-section: 64px;
`

---

## 六、阴影系统（Linear极简）

`css
--shadow-level-1: 0 1px 2px rgba(0, 0, 0, 0.05);   /* 轻微 */
--shadow-level-2: 0 2px 8px rgba(0, 0, 0, 0.08);    /* 中等 */
--shadow-level-3: 0 4px 16px rgba(0, 0, 0, 0.10);  /* 强 */
--shadow-level-4: 0 8px 32px rgba(0, 0, 0, 0.12);  /* 强烈 */
`

---

## 七、页面布局策略

### 7.1 深色/浅色分配

| 页面 | 背景 | 原因 |
|------|------|------|
| Dashboard | 白色 + soft-stone | 温暖友好，快速开始 |
| 简历管理 | 白色 | 简洁专注内容 |
| Upload | 白色 + soft-stone | 左侧白右侧灰 |
| Analysis | 深绿/深蓝技术带 | Agent可视化更醒目 |
| Results | 深蓝评分区 + soft-stone建议区 | 数据专业+层次分明 |
| AgentChat | 深绿 + 深蓝 | Agent专属氛围 |
| 投递记录 | 白色 | 列表展示 |
| 打招呼语 | 白色 | 模板编辑 |

### 7.2 组件变体对照

`ue
<!-- 白色背景 -->
<BaseCard>内容</BaseCard>

<!-- 暖灰背景（优化建议等） -->
<BaseCard variant=\"stone\">内容</BaseCard>

<!-- 深绿背景（Agent协作） -->
<BaseCard variant=\"deep-green\">内容</BaseCard>

<!-- 深蓝背景（数据展示） -->
<BaseCard variant=\"dark-navy\">内容</BaseCard>
`

---

## 八、组件规范

### 8.1 BaseButton

`ue
<!-- Primary（主要操作） -->
<BaseButton type=\"primary\">提交</BaseButton>

<!-- Secondary（次要操作） -->
<BaseButton type=\"secondary\">取消</BaseButton>

<!-- Ghost（辅助操作） -->
<BaseButton type=\"ghost\">查看</BaseButton>

<!-- Danger（危险操作） -->
<BaseButton type=\"danger\">删除</BaseButton>

<!-- 尺寸 -->
<BaseButton size=\"sm\">小</BaseButton>
<BaseButton size=\"md\">中</BaseButton>
<BaseButton size=\"lg\">大</BaseButton>
<BaseButton size=\"xl\">特大</BaseButton>

<!-- Loading -->
<BaseButton :loading=\"true\">加载中</BaseButton>
`

**特点**：
- Cohere: pill形状（32px圆角）
- Linear: 轻微抬起效果

### 8.2 BaseCard

`ue
<!-- 默认卡片 -->
<BaseCard>内容</BaseCard>

<!-- 带阴影 -->
<BaseCard :shadow=\"true\">内容</BaseCard>

<!-- 可交互 -->
<BaseCard :interactive=\"true\">可点击</BaseCard>

<!-- 暖灰变体 -->
<BaseCard variant=\"stone\">内容</BaseCard>

<!-- 深色变体 -->
<BaseCard variant=\"deep-green\">内容</BaseCard>
<BaseCard variant=\"dark-navy\">内容</BaseCard>
`

**特点**：
- Cohere: 22px大圆角
- 多种变体适应不同场景

### 8.3 BaseInput

`ue
<!-- 文本输入 -->
<BaseInput v-model=\"value\" label=\"用户名\" placeholder=\"请输入\" />

<!-- 密码输入 -->
<BaseInput type=\"password\" v-model=\"value\" label=\"密码\" />

<!-- 多行文本 -->
<BaseInput type=\"textarea\" v-model=\"value\" :rows=\"6\" label=\"描述\" />

<!-- 错误状态 -->
<BaseInput v-model=\"value\" :error=\"'输入错误'\" />

<!-- 前缀图标 -->
<BaseInput v-model=\"value\">
  <template #prefix>🔍</template>
</BaseInput>
`

**特点**：
- Linear: 聚焦蓝边框
- 8px小圆角

### 8.4 BaseTag

`ue
<!-- 类型 -->
<BaseTag>默认</BaseTag>
<BaseTag type=\"primary\">主要</BaseTag>
<BaseTag type=\"success\">成功</BaseTag>
<BaseTag type=\"warning\">警告</BaseTag>
<BaseTag type=\"error\">错误</BaseTag>
<BaseTag type=\"stone\">石头</BaseTag>
<BaseTag type=\"coral\">珊瑚</BaseTag>

<!-- 尺寸 -->
<BaseTag size=\"sm\">小</BaseTag>
<BaseTag size=\"md\">中</BaseTag>
<BaseTag size=\"lg\">大</BaseTag>
`

---

## 九、动画系统

### 9.1 过渡时长

`css
--transition-fast: 150ms;   /* 微交互 */
--transition-normal: 250ms;  /* 一般过渡 */
--transition-slow: 350ms;    /* 页面切换 */
`

### 9.2 Agent动画

`css
/* 思考中 - 呼吸灯 */
.agent-thinking {
  animation: breathe 1.5s ease-in-out infinite;
}

/* 处理中 - 进度条 */
.agent-processing::after {
  animation: shimmer 1.5s infinite;
}

/* 完成 - 打勾 */
.agent-complete {
  animation: scaleIn 350ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 错误 - 抖动 */
.agent-error {
  animation: shake 0.5s;
}
`

---

## 十、快速参考

### 10.1 常用CSS变量

`css
/* 颜色 */
color: var(--color-primary);
background: var(--color-canvas);

/* 圆角 */
border-radius: var(--radius-lg);  /* 22px */
border-radius: var(--radius-pill);  /* 32px */

/* 间距 */
margin: var(--spacing-lg);  /* 24px */
padding: var(--spacing-xl);  /* 32px */

/* 阴影 */
box-shadow: var(--shadow-level-2);

/* 文字 */
font-size: var(--font-size-display-md);  /* 28px */
letter-spacing: var(--letter-spacing-display-md);  /* -0.42px */
`

### 10.2 深色/浅色切换

`ue
<!-- 深色背景页面 -->
<div style=\"background: var(--color-dark-navy);\">
  <h1 style=\"color: var(--color-on-dark-navy);\">标题</h1>
</div>

<!-- 使用变体 -->
<BaseCard variant=\"dark-navy\">
  <!-- 文字颜色已自动处理 -->
</BaseCard>
`

---

## 十一、代码示例

### 11.1 创建新组件

`ue
<template>
  <div class=\"my-component\">
    <BaseCard variant=\"stone\">
      <h3>标题</h3>
      <p>内容</p>
      <BaseButton type=\"primary\" size=\"lg\">开始</BaseButton>
    </BaseCard>
  </div>
</template>

<script setup>
// 使用CSS变量，不要硬编码
</script>

<style scoped>
.my-component {
  padding: var(--spacing-xl);
  background: var(--color-canvas);
  border-radius: var(--radius-lg);
}
</style>
`

### 11.2 深色页面示例

`ue
<template>
  <div class=\"analysis-page\" style=\"background: var(--color-dark-navy);\">
    <BaseCard variant=\"dark-navy\" :shadow=\"true\">
      <template #header>
        <h3 style=\"color: var(--color-on-dark-navy);\">Agent协作</h3>
      </template>
      
      <div class=\"agent-list\">
        <div v-for=\"agent in agents\" :key=\"agent.id\" class=\"agent-item\">
          <span :style=\"{ color: agent.color }\">{{ agent.icon }}</span>
          <span style=\"color: var(--color-on-dark-navy);\">{{ agent.name }}</span>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
`

---

## 十二、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-08-04 | Cohere+Linear混合风格 |
| v1.0 | 2026-08-04 | 初始版本 |

---

**文档状态**: ✅ 设计规范完成  
**版本**: 2.0.0
