# 🚨 前端修改预警清单 - Job3.0 求职系统

**记录时间**: 2026-08-04 14:08  
**项目**: 智能简历评估与职业规划 Agent 系统  
**版本**: v2.0 → v3.0（功能扩展）  
**开发者**: 林育丞  

---

## 一、本次修改核心变更

### 1.1 功能范围调整

#### ❌ 移除功能
- ~~多Agent协作流程可视化~~（保留核心分析，但简化流程）
- ~~职业规划模块~~（暂不需要）
- ~~导出PDF功能~~（用户说不需要）

#### ✅ 新增功能
- **简历版本管理**：4个槽位，支持随机切换
- **打招呼语模板**：4个模板，根据JD定制
- **JD截图OCR识别**：上传截图自动提取文本
- **公司安全性查询**：查询社保、风险等信息
- **投递记录管理**：记录公司、重复提醒
- **Agent对话功能**：智能问答、辅助操作

### 1.2 页面结构调整

| 原页面 | 新页面 | 变更说明 |
|--------|--------|----------|
| Dashboard | Dashboard | 保留，新增投递统计、版本入口 |
| Upload | Upload | 保留，新增OCR截图功能 |
| Analysis | ~~Analysis~~ | 移除多Agent流程展示，简化为加载动画 |
| Results | Results | 保留，新增打招呼语、公司安全报告 |
| History | History | 保留 |
| Settings | Settings | 保留 |
| ❌ | ResumeManager | **新增**：简历版本管理 |
| ❌ | GreetingTemplates | **新增**：打招呼语模板管理 |
| ❌ | Applications | **新增**：投递记录管理 |
| ❌ | AgentChat | **新增**：Agent对话界面 |

---

## 二、⚠️ 高优先级预警

### 2.1 设计风格一致性预警

#### 🔴 预警：新增页面需遵循Cohere+Linear风格

**风险**：
- 新增页面可能与现有Cohere+Linear风格不一致
- 深色/浅色区域分配需要统一
- 圆角、间距、字体系统需要复用

**缓解措施**：
`
✅ 必须使用DESIGN.md中的CSS变量
✅ 必须使用BaseCard、BaseButton、BaseInput等基础组件
✅ 必须遵循22px大圆角卡片规范
✅ 必须使用负字间距标题（Display层级）
✅ 深色背景区域仅限于AgentChat和Results的公司安全报告

❌ 禁止硬编码颜色值
❌ 禁止使用非基础组件（除非新增common组件）
❌ 禁止修改基础组件的props接口
`

#### 🔴 预警：组件变体管理复杂度

**风险**：
- BaseCard已有4种变体（default/stone/deep-green/dark-navy）
- 新增页面可能需要更多变体
- 变体增加会导致样式管理困难

**缓解措施**：
`
✅ 优先使用现有4种变体
✅ 新增变体需要同步更新DESIGN.md
✅ 变体命名遵循：default / stone / deep-green / dark-navy / [new]
✅ 深色变体的文字颜色使用专用变量：--color-on-[variant]
`

### 2.2 功能逻辑预警

#### 🔴 预警：简历版本管理的数据结构

**风险**：
- 4个版本槽位需要明确的数据结构
- 版本切换不能丢失数据
- 多版本同时编辑需要状态管理

**必须实现**：
`javascript
// 数据结构
interface Resume {
  id: string
  slot: 1 | 2 | 3 | 4  // 版本槽位
  file: File
  content: string       // 解析后的文本
  updatedAt: Date
  isActive: boolean     // 是否正在使用
}

// 状态管理（Pinia）
interface ResumeStore {
  slots: [Resume?, Resume?, Resume?, Resume?]  // 固定4个槽位
  activeSlot: 1 | 2 | 3 | 4 | null
  
  // 方法
  uploadToSlot(slot: number, file: File): Promise<void>
  switchToSlot(slot: number): void
  deleteSlot(slot: number): void
  getResumeBySlot(slot: number): Resume | null
}
`

**预警清单**：
- [ ] 版本切换时需要更新activeSlot状态
- [ ] 上传前需要检查文件格式（.pdf/.doc/.docx）
- [ ] 上传后需要解析文件内容
- [ ] 删除版本需要确认提示
- [ ] 版本为空时需要显示占位符

#### 🔴 预警：打招呼语模板变量解析

**风险**：
- 模板中的变量需要正确解析
- 变量来源需要明确（JD提取 / 用户输入）
- 变量缺失时需要降级处理

**必须实现**：
`javascript
// 模板变量定义
const TEMPLATE_VARIABLES = {
  '{岗位}': 'jobTitle',      // JD提取
  '{公司}': 'companyName',    // JD提取
  '{年限}': 'experience',     // 简历提取
  '{技能}': 'skills',         // JD+简历提取
  '{方向}': 'direction',      // 用户输入（可能为空）
}

// 变量提取流程
1. JD文本 → 正则提取公司名、岗位名
2. 简历文本 → 提取工作年限、技能列表
3. 用户输入 → 补充缺失变量（如{方向}）
4. 模板替换 → 生成最终打招呼语
`

**预警清单**：
- [ ] 变量解析需要处理边界情况（公司名提取失败等）
- [ ] 变量为空时使用占位符或忽略
- [ ] 模板编辑需要实时预览
- [ ] 模板需要支持富文本格式

#### 🔴 预警：投递记录重复检测

**风险**：
- 公司名格式不一致（"字节跳动" vs "字节跳动有限公司"）
- 重复检测需要模糊匹配
- 重复提醒需要用户确认

**必须实现**：
`javascript
// 重复检测逻辑
function checkDuplicate(newCompany: string, existingList: Application[]): Application | null {
  // 1. 精确匹配
  const exact = existingList.find(app => app.company === newCompany)
  if (exact) return exact
  
  // 2. 模糊匹配（包含关系）
  const fuzzy = existingList.find(app => 
    newCompany.includes(app.company) || app.company.includes(newCompany)
  )
  if (fuzzy) return fuzzy
  
  // 3. 简称匹配（去"有限公司"等后缀）
  const shortName = normalizeCompanyName(newCompany)
  const normalized = existingList.find(app => 
    normalizeCompanyName(app.company) === shortName
  )
  if (normalized) return normalized
  
  return null
}

// 公司名标准化
function normalizeCompanyName(name: string): string {
  return name
    .replace(/有限公司|股份|集团|Co.,Ltd|Ltd./gi, '')
    .trim()
    .toLowerCase()
}
`

**预警清单**：
- [ ] 重复检测需要考虑中英文混合
- [ ] 重复时需要显示历史记录
- [ ] 用户可选择"继续添加"或"取消"
- [ ] 列表需要按时间排序

---

## 三、⚠️ 中优先级预警

### 3.1 API接口预警

#### 🟡 预警：新增API接口需要统一管理

**风险**：
- 新增功能需要后端API支持
- 接口需要统一管理（axios封装）
- 接口需要错误处理

**必须实现**：
`javascript
// src/api/index.js 新增接口

// 简历相关
export const resumeApi = {
  upload: (file, slot) => { /* ... */ },
  list: () => { /* ... */ },
  delete: (id) => { /* ... */ },
  optimize: (resumeId, jdId) => { /* ... */ },
}

// JD相关
export const jdApi = {
  parse: (text) => { /* ... */ },
  ocr: (image) => { /* ... */ },  // 新增
  checkCompany: (companyName) => { /* ... */ },  // 新增
}

// 打招呼语相关
export const greetingApi = {
  list: () => { /* ... */ },
  create: (template) => { /* ... */ },
  update: (id, template) => { /* ... */ },
  delete: (id) => { /* ... */ },
  generate: (templateId, jdId) => { /* ... */ },  // 新增
}

// 投递记录相关
export const applicationApi = {
  list: () => { /* ... */ },
  add: (company, position) => { /* ... */ },  // 新增
  update: (id, status) => { /* ... */ },
  delete: (id) => { /* ... */ },
  checkDuplicate: (company) => { /* ... */ },  // 新增
}
`

**预警清单**：
- [ ] 所有API需要统一错误处理
- [ ] 需要loading状态管理
- [ ] 需要Token认证（如果后端需要）
- [ ] 需要请求取消（如果支持中断）

#### 🟡 预警：OCR识别方案选择

**风险**：
- 截图OCR识别需要第三方服务
- 免费额度有限制
- 准确率可能有误差

**推荐方案**：
`
方案1：百度OCR（推荐）
  ✅ 免费额度：50000次/天
  ✅ 准确率高（印刷体>95%）
  ✅ API简单
  ❌ 需要申请AppID/Secret

方案2：腾讯OCR
  ✅ 免费额度：1000次/月
  ✅ 准确率高
  ❌ 免费额度较少

方案3：前端本地识别（轻量级）
  ✅ 不需要后端
  ✅ 免费
  ❌ 准确率低
  ❌ 不支持手写体
`

**预警清单**：
- [ ] 需要准备OCR服务的API Key
- [ ] 需要处理OCR识别失败的情况
- [ ] 需要用户授权上传截图
- [ ] 需要考虑OCR服务的成本

### 3.2 状态管理预警

#### 🟡 预警：Pinia Store需要重构

**风险**：
- 现有Store可能不够用
- 新增功能需要新Store
- Store之间可能有依赖

**必须实现**：
`javascript
// src/stores/index.js

// 简历Store
export const useResumeStore = defineStore('resume', {
  state: () => ({
    slots: [null, null, null, null],
    activeSlot: null,
    loading: false,
  }),
  getters: {
    activeResume: (state) => state.slots[state.activeSlot],
    hasResume: (state) => state.slots.some(s => s !== null),
  },
  actions: {
    async uploadToSlot(slot, file) { /* ... */ },
    async deleteSlot(slot) { /* ... */ },
    switchSlot(slot) { /* ... */ },
  }
})

// 打招呼语Store
export const useGreetingStore = defineStore('greeting', {
  state: () => ({
    templates: [],
    defaultTemplateId: null,
  }),
  actions: {
    async fetchTemplates() { /* ... */ },
    async createTemplate(template) { /* ... */ },
    async updateTemplate(id, template) { /* ... */ },
    async setDefault(id) { /* ... */ },
    generateGreeting(templateId, jdId) { /* ... */ },
  }
})

// 投递记录Store
export const useApplicationStore = defineStore('application', {
  state: () => ({
    list: [],
    loading: false,
  }),
  getters: {
    pendingApplications: (state) => 
      state.list.filter(a => a.status === 'pending'),
    totalCount: (state) => state.list.length,
  },
  actions: {
    async fetchList() { /* ... */ },
    async add(company, position) { /* ... */ },
    async delete(id) { /* ... */ },
    checkDuplicate(company) { /* ... */ },
  }
})
`

**预警清单**：
- [ ] Store需要持久化（localStorage）
- [ ] Store需要重置方法
- [ ] Store之间需要解耦
- [ ] 异步action需要错误处理

---

## 四、⚠️ 低优先级预警

### 4.1 性能优化预警

#### 🟢 预警：简历文件处理

**风险**：
- 简历文件可能很大（10MB+）
- 文件解析可能有性能问题
- 大文件上传可能超时

**缓解措施**：
`
✅ 文件大小限制：最大10MB
✅ 上传时显示进度条
✅ 大文件异步处理
✅ 简历内容缓存（避免重复解析）
`

#### 🟢 预警：Agent对话性能

**风险**：
- 流式输出需要WebSocket支持
- 长对话可能导致内存泄漏
- 历史消息存储问题

**缓解措施**：
`
✅ 消息列表虚拟滚动（如果超过100条）
✅ 历史消息分页加载
✅ 定期清理旧消息
✅ 打字机效果优化
`

### 4.2 移动端适配预警

#### 🟢 预警：AgentChat移动端布局

**风险**：
- 侧边栏+主聊天区的布局在移动端不适用
- 需要切换为全屏聊天模式
- Agent选择器需要重新设计

**移动端适配方案**：
`css
/* 桌面端：侧边栏 + 主聊天区 */
.agent-chat {
  display: grid;
  grid-template-columns: 250px 1fr;
}

/* 移动端：全屏聊天 + 底部导航 */
@media (max-width: 768px) {
  .agent-chat {
    grid-template-columns: 1fr;
  }
  
  .chat-sidebar {
    display: none;  /* 改为抽屉或底部导航 */
  }
}
`

**预警清单**：
- [ ] 移动端Agent选择器设计
- [ ] 移动端键盘适配（输入框不被遮挡）
- [ ] 移动端消息气泡样式
- [ ] 移动端深色模式测试

---

## 五、设计规范遵守清单

### 5.1 必须遵守的规范

#### ✅ 颜色使用
`css
/* 禁止硬编码颜色 */
❌ color: #17171c;  /* 改用 var(--color-primary) */
❌ background: #ffffff;  /* 改用 var(--color-canvas) */

/* 必须使用CSS变量 */
✅ color: var(--color-primary);
✅ background: var(--color-canvas);
✅ background: var(--color-soft-stone);
`

#### ✅ 圆角使用
`css
/* 禁止随意使用圆角 */
❌ border-radius: 10px;  /* 除非明确设计需要 */

/* 必须使用规范圆角 */
✅ border-radius: var(--radius-sm);   /* 8px - 输入框 */
✅ border-radius: var(--radius-md);   /* 16px - 中等卡片 */
✅ border-radius: var(--radius-lg);   /* 22px - 大卡片 */
✅ border-radius: var(--radius-pill);  /* 32px - CTA按钮 */
`

#### ✅ 间距使用
`css
/* 禁止随意使用间距 */
❌ margin: 20px;
❌ padding: 15px;

/* 必须使用8px倍数间距 */
✅ margin: var(--spacing-md);   /* 16px */
✅ padding: var(--spacing-xl);  /* 24px */
✅ padding: var(--spacing-xxl); /* 32px */
`

#### ✅ 字体使用
`css
/* 禁止随意使用字号 */
❌ font-size: 20px;
❌ font-weight: 600;

/* 必须使用规范字号 */
✅ font-size: var(--font-size-display-xl);  /* 48px */
✅ font-size: var(--font-size-heading-lg);   /* 22px */
✅ font-size: var(--font-size-body);         /* 16px */
✅ font-weight: var(--font-weight-medium);     /* 500 */
`

#### ✅ 阴影使用
`css
/* 禁止随意使用阴影 */
❌ box-shadow: 0 2px 8px rgba(0,0,0,0.1);

/* 必须使用规范阴影 */
✅ box-shadow: var(--shadow-level-1);
✅ box-shadow: var(--shadow-level-2);
`

### 5.2 深色/浅色区域分配

| 页面 | 背景色 | 说明 |
|------|--------|------|
| Dashboard | 白色 + soft-stone | 温暖友好 |
| ResumeManager | 白色 | 简洁专注 |
| Upload | 白色 + soft-stone | 左侧白右侧灰 |
| Results | 深蓝 + soft-stone | 数据展示专业 + 公司安全报告 |
| GreetingTemplates | 白色 | 简洁编辑 |
| Applications | 白色 | 列表展示 |
| AgentChat | 深绿 + 深蓝 | Agent专属氛围 + 对话区域 |

---

## 六、测试清单

### 6.1 功能测试

#### 简历管理
- [ ] 上传4个不同版本的简历
- [ ] 切换不同版本
- [ ] 删除版本并确认
- [ ] 版本为空时显示占位符
- [ ] 文件格式验证（仅pdf/doc/docx）

#### JD处理
- [ ] 粘贴文本JD并解析
- [ ] 上传截图OCR识别
- [ ] OCR识别失败的处理
- [ ] 公司安全性查询
- [ ] 公司安全性显示（正常/异常）

#### 打招呼语
- [ ] 创建4个模板
- [ ] 编辑模板内容
- [ ] 变量实时预览
- [ ] 根据JD生成打招呼语
- [ ] 复制打招呼语
- [ ] 重新生成打招呼语

#### 投递记录
- [ ] 添加投递记录
- [ ] 重复投递检测
- [ ] 重复时显示历史
- [ ] 删除投递记录
- [ ] 列表按时间排序

#### Agent对话
- [ ] 发送消息
- [ ] 接收回复（流式）
- [ ] Agent选择
- [ ] 历史消息加载
- [ ] 长对话性能

### 6.2 UI测试

- [ ] 页面加载速度
- [ ] 深色/浅色区域正确显示
- [ ] 响应式布局（桌面/平板/手机）
- [ ] 动画流畅度
- [ ] 字体渲染（负字间距）
- [ ] 移动端触摸区域（≥44px）

### 6.3 兼容性测试

- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Edge 90+
- [ ] Windows / macOS / Linux

---

## 七、开发顺序建议

### Phase 1：核心数据层（高优先级）

1. **Pinia Store重构**
   - ResumeStore
   - GreetingStore
   - ApplicationStore

2. **API接口封装**
   - resumeApi
   - jdApi
   - greetingApi
   - applicationApi

### Phase 2：核心页面（中优先级）

3. **ResumeManager.vue**
   - 4个版本槽位
   - 上传/删除/切换

4. **Applications.vue**
   - 投递列表
   - 重复检测
   - 添加/删除

5. **GreetingTemplates.vue**
   - 模板列表
   - 编辑/预览
   - 变量解析

### Phase 3：功能增强（低优先级）

6. **JD截图OCR**
   - 截图上传
   - OCR识别
   - 结果展示

7. **公司安全性查询**
   - 天眼查API集成
   - 安全评分展示
   - 风险提示

8. **AgentChat.vue**
   - 对话界面
   - 流式输出
   - 历史记录

### Phase 4：UI优化（持续）

9. **Dashboard优化**
   - 新增统计卡片
   - 版本入口

10. **Results.vue优化**
    - 新增打招呼语
    - 新增公司安全报告

11. **AppLayout.vue优化**
    - 新增导航菜单
    - Agent悬浮按钮

---

## 八、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v3.0 | 2026-08-04 | 功能扩展：简历版本、打招呼语、投递记录、Agent对话 |
| v2.0 | 2026-08-04 | Cohere+Linear混合风格全面更新 |
| v1.0 | 2026-08-04 | 初始版本，现代科技风 |

---

**文档状态**: 🚨 预警清单完成，待开始Phase 1开发  
**下次审查**: 2026-08-05（每日审查）  
**版本**: 3.0.0

