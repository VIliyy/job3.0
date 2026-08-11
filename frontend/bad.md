# 🚨 Job3.0 前端 - Cohere+Linear风格错误预警清单

**记录时间**: 2026-08-04 15:20  
**前端框架**: Vue 3 + Vite + Pinia  
**设计风格**: Cohere企业AI风 + Linear技术细节  
**版本**: v2.1  
**开发者**: 林育丞  

---

## 一、⚠️ 高优先级预警

### 1.1 文件编码预警 🔴

#### 🔴 预警：Vue文件必须使用UTF-8编码

**风险**：
- 中文显示为乱码
- 用户界面无法正常显示
- SEO和可访问性问题

**排查步骤**：
```powershell
# 检查文件编码
Get-Content "src/views/Resumes.vue" -Encoding UTF8

# 批量检查所有Vue文件
Get-ChildItem -Path "src" -Filter "*.vue" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match '[\u4e00-\u9fa5]') {
        Write-Host "✓ $($_.FullName) - 包含中文"
    }
}
```

**解决**：
```powershell
# 重写文件使用UTF-8编码
$content = Get-Content "path/to/file.vue" -Raw
$content | Out-File -FilePath "path/to/file.vue" -Encoding UTF8
```

**PowerShell脚本批量修复**：
```powershell
Get-ChildItem -Path "src/views" -Filter "*.vue" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content) {
        $content | Out-File -FilePath $_.FullName -Encoding UTF8
        Write-Host "✓ 已修复: $($_.Name)"
    }
}
```

**VS Code设置**：
```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": true
}
```

---

### 1.2 API集成预警 🔴

#### 🔴 预警：API基础URL配置

**风险**：
- 无法连接后端服务
- 所有API调用失败

**检查**：
```javascript
// src/api/index.js
const API_BASE_URL = '\''.env.VITE_API_BASE_URL || '\''http://localhost:8000/api'\''

// 检查.env文件
VITE_API_BASE_URL=http://localhost:8000/api
```

**CORS配置**（后端需要）：
```javascript
// 后端CORS中间件配置
app.use(cors({
  origin: '\''http://localhost:5173'\'', // 前端地址
  credentials: true
}))
```

---

### 1.3 状态管理预警 🔴

#### 🔴 预警：Pinia Store未正确导入

**风险**：
- 状态无法共享
- 数据丢失
- 组件间通信失败

**检查main.js**：
```javascript
// src/main.js
import { createApp } from '\''vue'\''
import App from '\''./App.vue'\''
import pinia from '\''./stores'\'' // ⭐ 必须导入

createApp(App)
  .use(pinia)  // ⭐ 必须使用
  .mount('\''#app'\'')
```

**组件中使用Store**：
```javascript
// 在组件中
import { useResumeStore } from '\''@/stores'\''
import { storeToRefs } from '\''pinia'\''

const resumeStore = useResumeStore()
const { resumes, activeSlot } = storeToRefs(resumeStore)

// 调用actions
resumeStore.addResume(1, { name: '\''简历1'\'', fileType: '\''PDF'\'' })
```

---

## 二、⚠️ 中优先级预警

### 2.1 设计规范一致性预警

#### 🟡 预警：CSS变量使用规范

**风险**：
- 颜色不一致
- 深色/浅色主题切换失效
- 样式混乱

**必须使用的CSS变量**：
```css
/* 主色调 */
color: var(--color-primary);           /* #17171c */
background: var(--color-canvas);        /* #ffffff */
background: var(--color-soft-stone);    /* #eeece7 */

/* 行动色 */
color: var(--color-action-blue);         /* #1863dc */
color: var(--color-coral);              /* #ff7759 */

/* 状态色 */
color: var(--color-success);            /* #22c55e */
color: var(--color-error);              /* #b30000 */
color: var(--color-warning);            /* #f59e0b */

/* Agent色 */
color: var(--agent-planner);            /* #8B5CF6 */
color: var(--agent-writer);             /* #10B981 */
```

**禁止硬编码**：
```css
/* ❌ 禁止 */
color: #17171c;
background: #ffffff;

/* ✅ 必须 */
color: var(--color-primary);
background: var(--color-canvas);
```

---

### 2.2 组件使用预警

#### 🟡 预警：BaseCard变体使用

**正确用法**：
```vue
<!-- 白色背景（Dashboard、简历管理） -->
<BaseCard>内容</BaseCard>

<!-- 暖灰背景（优化建议、模板编辑） -->
<BaseCard variant="stone">内容</BaseCard>

<!-- 深绿背景（Agent协作、对话） -->
<BaseCard variant="deep-green">内容</BaseCard>

<!-- 深蓝背景（数据展示、评分） -->
<BaseCard variant="dark-navy">内容</BaseCard>
```

---

#### 🟡 预警：BaseButton类型

**正确用法**：
```vue
<!-- 主要操作（提交、开始等） -->
<BaseButton type="primary">开始分析</BaseButton>

<!-- 次要操作（取消、返回等） -->
<BaseButton type="secondary">取消</BaseButton>

<!-- 辅助操作（查看详情等） -->
<BaseButton type="ghost">查看</BaseButton>

<!-- 危险操作（删除等） -->
<BaseButton type="danger">删除</BaseButton>
```

---

### 2.3 圆角系统预警

#### 🟡 预警：圆角使用不规范

**Cohere圆角规范**：
```css
/* 小按钮、标签：4px */
border-radius: var(--radius-xs);

/* 输入框、次要按钮：8px */
border-radius: var(--radius-sm);

/* 中等卡片：16px */
border-radius: var(--radius-md);

/* 大卡片：22px（品牌特色） */
border-radius: var(--radius-lg);

/* CTA按钮：32px（pill形状） */
border-radius: var(--radius-pill);
```

---

### 2.4 字体系统预警

#### 🟡 预警：字号使用不规范

**Linear字体规范（负字间距）**：
```css
/* Display层级 - 使用负字间距 */
h1 {
  font-size: var(--font-size-display-xl);  /* 48px */
  letter-spacing: var(--letter-spacing-display-xl);  /* -1.44px */
}

/* 正文 - 不使用负字间距 */
p, span, div {
  font-size: var(--font-size-body);  /* 16px */
  letter-spacing: 0;
}
```

---

## 三、⚠️ 低优先级预警

### 3.1 动画性能预警

#### 🟢 优化建议

```css
/* ✅ 推荐：使用transform和opacity */
transition: transform var(--transition-fast), opacity var(--transition-fast);

/* ⚠️ 避免：动画性能差 */
transition: all var(--transition-normal);

/* ✅ 使用CSS Containment */
.card {
  contain: layout style paint;
}
```

---

## 四、页面布局规范

### 4.1 页面背景分配

| 页面 | 背景 | 说明 |
|------|------|------|
| **Dashboard** | #ffffff + #eeece7 | 温暖友好 |
| **简历管理** | #ffffff | 简洁专注 |
| **Upload** | #ffffff | 简洁专注 |
| **Results** | #071829 + #eeece7 | 数据专业+建议温暖 |
| **AgentChat** | #003c33 + #071829 | 深色专属 |
| **投递记录** | #ffffff | 列表展示 |
| **打招呼语** | #ffffff | 模板编辑 |

### 4.2 页面最大宽度

```css
.page {
  max-width: 1200px;  /* 标准页面 */
  margin: 0 auto;
  padding: 32px;
}

.chat-container {
  max-width: 900px;  /* 聊天页面 */
}
```

---

## 五、Store使用指南

### 5.1 ResumeStore（简历管理）

```javascript
import { useResumeStore } from '\''@/stores'\''

const store = useResumeStore()

// State
store.resumes        // 简历列表 {1: {...}, 2: {...}}
store.activeSlot      // 当前激活的槽位
store.loading         // 加载状态

// Getters
store.activeResume    // 当前激活的简历
store.resumeCount     // 简历数量
store.hasResume       // 是否有简历

// Actions
store.setActiveSlot(1)           // 设置激活槽位
store.addResume(1, {...})        // 添加简历
store.updateResume(1, {...})     // 更新简历
store.deleteResume(1)             // 删除简历
```

### 5.2 ApplicationStore（投递记录）

```javascript
import { useApplicationStore } from '\''@/stores'\''

const store = useApplicationStore()

// State
store.applications    // 投递列表

// Getters
store.totalCount      // 总投递数
store.interviewCount  // 面试中数量
store.offerCount      // Offer数量

// Actions
store.addApplication({...})      // 添加投递
store.updateStatus(id, status)    // 更新状态
store.deleteApplication(id)       // 删除记录
```

### 5.3 GreetingStore（打招呼语）

```javascript
import { useGreetingStore } from '\''@/stores'\''

const store = useGreetingStore()

// State
store.templates       // 模板列表
store.activeTemplateId // 当前激活模板

// Getters
store.activeTemplate  // 当前模板
store.defaultTemplate // 默认模板

// Actions
store.addTemplate({...})           // 添加模板
store.generateGreeting(\'\''公司'\'', '\'\'岗位'\'', '\'\''亮点'\'') // 生成打招呼语
```

---

## 六、API调用模式

### 6.1 正确的API调用

```javascript
import { resumeApi, applicationApi, jdApi } from '\''@/api'\''

// 简历上传
try {
  const response = await resumeApi.upload(file, slot)
  console.log('\''上传成功:'\'', response)
} catch (error) {
  console.error('\''上传失败:'\'', error.message)
  alert(error.message)
}

// 简历列表
const list = await resumeApi.list()

// JD解析
const analysis = await jdApi.parse(jdContent)
```

### 6.2 错误处理

```javascript
// 组件中
const loading = ref(false)
const error = ref(null)

const uploadFile = async () => {
  loading.value = true
  error.value = null
  
  try {
    await resumeApi.upload(file, slot)
    alert('\''上传成功'\'')
  } catch (err) {
    error.value = err.message
    console.error(err)
  } finally {
    loading.value = false
  }
}
```

---

## 七、响应式布局规范

### 7.1 网格系统

```css
/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

/* 简历槽位网格 */
.resume-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

/* 快捷入口网格 */
.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
```

### 7.2 移动端适配

```css
/* 平板 */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }
  
  .page-header h1 {
    font-size: 32px;
  }
}

/* 手机 */
@media (max-width: 480px) {
  .add-form {
    flex-direction: column;
  }
  
  .filter-bar {
    overflow-x: auto;
  }
}
```

---

## 八、常见错误排查

### 8.1 样式不生效

| 检查项 | 命令 |
|--------|------|
| CSS文件导入 | `rg '\''import.*variables.css'\'' src/` |
| 变量名拼写 | `rg '\''var\(--color'\'' src/` |
| 组件scoped | 检查是否有style scoped |

### 8.2 API调用失败

| 检查项 | 命令 |
|--------|------|
| 后端服务 | 检查http://localhost:8000是否运行 |
| CORS配置 | 检查浏览器控制台是否有CORS错误 |
| API URL | 检查vite.config.js代理配置 |

### 8.3 Store数据不共享

| 检查项 | 命令 |
|--------|------|
| Pinia导入 | 检查main.js是否.use(pinia) |
| Store定义 | 检查stores/index.js是否正确定义 |
| 响应式 | 检查是否使用storeToRefs |

---

## 九、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.1 | 2026-08-04 15:20 | 添加编码预警、API集成、Store使用指南 |
| v2.0 | 2026-08-04 14:36 | Cohere+Linear混合风格更新 |
| v1.0 | 2026-08-04 | 初始版本 |

---

**文档状态**: ✅ 错误预警清单已更新  
**设计风格**: Cohere企业AI风 + Linear技术细节  
**版本**: 2.1.0  
**下次更新**: 添加更多业务逻辑示例

---

## 十、⚠️ PowerShell文件写入注意事项 🔴

### 10.1 PowerShell编码问题

#### 🔴 预警：Vue文件中的单引号字符串

**错误示例（PowerShell中）**：
`ue
<!-- ❌ 错误：PowerShell单引号转义 -->
@click="activeTab = '\''resume'\''"
:class="{ active: activeTab === '\''resume'\'' }"
`

**正确写法**：
`ue
<!-- ✅ 正确：Vue模板中直接使用单引号 -->
@click="activeTab = 'resume'"
:class="{ active: activeTab === 'resume' }"
`

**原因**：
PowerShell的单引号字符串是字面量，不需要也不能用\'转义
应该使用Node.js或Python脚本写入Vue文件，避免PowerShell转义问题

### 10.2 推荐的文件写入方式

#### 🟢 使用Node.js写入Vue文件
`javascript
const fs = require('fs');
const content = <template>...</template>;
fs.writeFileSync('path/to/file.vue', content, 'utf8');
`

#### 🟢 使用Python写入Vue文件
`python
# -*- coding: utf-8 -*-
import codecs

content = """<template>...</template>"""
with codecs.open('path/to/file.vue', 'w', 'utf-8') as f:
    f.write(content)
`

**注意**：避免在PowerShell中使用复杂的字符串操作来创建包含特殊字符的文件


---

## 十一、⚠️ API文件常见错误 🔴

### 11.1 乱码导致的语法错误

#### 🔴 预警：PowerShell编码问题导致API文件乱码

**问题现象**：
`
[plugin:vite:import-analysis] Failed to parse source for import analysis
E:/job3.0/frontend/src/api/index.js:29:5
`

**常见错误模式**：
`javascript
// ❌ 错误：乱码字符
const API_BASE_URL = 'http://localhost:8000/api'
// 閸╄櫣顢呴柊宥囩枂
const apiClient = axios.create({

// ❌ 错误：错误的模板字符串
return apiClient.get(\/resume/\)

// ❌ 错误：错误的转义
config.headers.Authorization = \Bearer \
`

**正确写法**：
`javascript
// ✅ 正确：标准字符串
const API_BASE_URL = 'http://localhost:8000/api'

// ✅ 正确：模板字符串
return apiClient.get(/resume/)

// ✅ 正确：标准注释
// API基础URL配置

// ✅ 正确：带转义的字符串
config.headers.Authorization = Bearer 
`

**检查工具**：
`ash
# 使用Node.js检查文件
node -e "const fs = require('fs'); 
const content = fs.readFileSync('E:/job3.0/frontend/src/api/index.js', 'utf8');
console.log('包含乱码:', content.includes('閸') || content.includes('濮'));"
`

### 11.2 axios配置错误

#### 🟡 常见API配置问题

**CORS错误**：
`javascript
// 如果遇到CORS错误，确保后端配置正确
// 后端应该设置：
app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}))
`

**请求超时**：
`javascript
// 确保timeout设置合理
const apiClient = axios.create({
  timeout: 30000, // 30秒超时
})
`

**Token认证**：
`javascript
// 取消注释并正确实现
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = Bearer 
  }
  return config
})
`

