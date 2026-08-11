# Job3.0 前端专业版 - 用户界面设计规范

**版本**: 2.0.0
**更新时间**: 2026-08-07
**设计理念**: 简约、专业、高效

---

## 1. 设计原则

### 1.1 核心原则
- **简约至上**: 去除冗余元素，突出核心内容
- **专业导向**: 去掉emoji表情，使用专业图标和布局
- **高效导航**: 清晰的信息架构，快速触达功能
- **一致体验**: 统一的视觉语言和交互模式

### 1.2 设计风格
- **配色方案**: 基于公司品牌色的专业配色
- **排版规范**: 8px网格系统，统一的间距和尺寸
- **交互模式**: 简洁的反馈和过渡动效
- **响应式设计**: 适配多种屏幕尺寸

---

## 2. 页面结构

### 2.1 控制台 (Dashboard)
**入口**: 首页，展示系统概览

**内容**:
- 统计数据卡片（简历版本、投递记录、优化次数、平均分数）
- 最近优化列表
- 投递动态
- 优化趋势图表
- 智能提示建议
- 快捷功能入口

**特点**:
- 数据可视化，直观展示关键指标
- 卡片式布局，模块化信息
- 统一的数据展示风格

### 2.2 简历优化 (Optimization)
**入口**: /optimize

**流程**:
1. 输入简历内容和目标JD
2. 触发多Agent协作优化
3. 实时展示优化进度
4. 查看优化结果和建议

**特点**:
- 清晰的步骤指示器
- 流式输出展示
- 专业的评分展示
- 详细的Agent输出

### 2.3 简历对比 (Compare)
**入口**: /compare

**功能**:
- 多版本选择对比
- 并排显示差异
- 差异高亮标注
- 统计信息展示

**特点**:
- 左右对比布局
- 颜色区分新增/删除/修改
- 实时版本切换

### 2.4 简历管理 (Resumes)
**入口**: /resumes

**功能**:
- 4个版本槽位管理
- 版本切换
- 内容编辑
- 文件上传

### 2.5 投递记录 (Applications)
**入口**: /applications

**功能**:
- 投递进度追踪
- 状态管理
- 统计分析

### 2.6 JD分析 (Analyze)
**入口**: /analyze

**功能**:
- JD深度解析
- 关键信息提取
- 匹配度分析

---

## 3. 组件规范

### 3.1 按钮
**Primary Button**
```css
.btn-primary {
  padding: 12px 24px;
  background: var(--color-action-blue);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
}
```

**Secondary Button**
```css
.btn-secondary {
  padding: 12px 24px;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
}
```

**状态**:
- Default: 默认样式
- Hover: 轻微背景变化
- Active: 按下效果
- Disabled: 降低透明度

### 3.2 输入框
```css
.input-field {
  padding: 12px 16px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: 14px;
  transition: border-color 200ms;
}

.input-field:focus {
  outline: none;
  border-color: var(--color-action-blue);
  box-shadow: 0 0 0 3px rgba(24, 99, 220, 0.1);
}
```

### 3.3 卡片
```css
.card {
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-level-1);
}
```

### 3.4 进度条
```css
.progress-bar {
  height: 8px;
  background: var(--surface-stone);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-action-blue), var(--color-focus-blue));
  transition: width 300ms ease;
}
```

### 3.5 徽章
```css
.badge {
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: var(--radius-xs);
}

.badge.success {
  background: var(--color-success-soft);
  color: var(--color-success);
}

.badge.warning {
  background: var(--color-warning-soft);
  color: var(--color-warning);
}

.badge.error {
  background: var(--color-error-soft);
  color: var(--color-error);
}
```

---

## 4. 配色系统

### 4.1 主色
- **Primary**: #1863dc (Action Blue)
- **Primary Hover**: #4c6ee6 (Focus Blue)

### 4.2 语义色
- **Success**: #16a34a (Green)
- **Warning**: #ea580c (Orange)
- **Error**: #dc2626 (Red)
- **Info**: #1863dc (Blue)

### 4.3 中性色
- **Primary Text**: #17171c
- **Secondary Text**: #3f3f46
- **Muted Text**: #93939f
- **Border**: #e5e7eb

### 4.4 背景色
- **Canvas**: #ffffff
- **Default**: #fafaf9
- **Elevated**: #ffffff
- **Stone**: #eeece7

---

## 5. 排版规范

### 5.1 字体
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

### 5.2 字号
- **Display XL**: 48px / 56px line-height
- **Display LG**: 36px / 44px line-height
- **Display MD**: 28px / 36px line-height
- **Heading LG**: 22px / 28px line-height
- **Heading MD**: 18px / 24px line-height
- **Body**: 16px / 24px line-height
- **Body SM**: 14px / 20px line-height
- **Micro**: 12px / 16px line-height

### 5.3 字重
- **Regular**: 400
- **Medium**: 500
- **Semibold**: 600
- **Bold**: 700

---

## 6. 间距系统

### 6.1 基础单位
基于 8px 网格系统

### 6.2 间距等级
- **XXS**: 4px
- **XS**: 8px
- **SM**: 12px
- **MD**: 16px
- **LG**: 24px
- **XL**: 32px
- **XXL**: 48px
- **Section**: 64px

---

## 7. 圆角系统

- **2XS**: 2px
- **XS**: 4px
- **SM**: 8px
- **MD**: 12px
- **LG**: 16px
- **XL**: 22px
- **Pill**: 9999px

---

## 8. 阴影系统

### 8.1 5级阴影
- **Level 1**: 轻微抬起，适合卡片
- **Level 2**: 中等抬起，适合下拉菜单
- **Level 3**: 强抬起，适合模态框
- **Level 4**: 最高抬起，适合浮层
- **Level 5**: 极度抬起，适合特殊场景

---

## 9. 动效规范

### 9.1 过渡时长
- **Fast**: 150ms
- **Base**: 220ms
- **Slow**: 320ms

### 9.2 缓动曲线
```css
--ease-out-quart: cubic-bezier(0.16, 1, 0.3, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

### 9.3 使用场景
- 按钮悬停: 150ms ease
- 卡片展开: 220ms ease
- 页面切换: 320ms ease
- 加载动画: 循环使用

---

## 10. 响应式断点

### 10.1 断点
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px - 1440px
- **Large Desktop**: > 1440px

### 10.2 布局策略
- **Mobile**: 单列布局，堆叠排列
- **Tablet**: 双列布局
- **Desktop**: 多列布局
- **Large Desktop**: 最大宽度限制，居中显示

---

## 11. 暗色模式

### 11.1 切换方式
- 侧边栏底部主题切换按钮
- 本地存储记住用户偏好

### 11.2 配色调整
- **Surface**: 深色背景，白色文字
- **Border**: 调整对比度
- **Shadow**: 增加黑色比例

### 11.3 CSS变量
```css
:root.dark {
  --surface-canvas: #1a1a1f;
  --text-primary: #f4f4f5;
  --border-default: #3f3f46;
}
```

---

## 12. 图标使用

### 12.1 图标原则
- 使用简洁的线性图标
- 统一的大小和粗细
- 合理的颜色透明度

### 12.2 图标大小
- **Small**: 16px (inline)
- **Medium**: 20px (navigation)
- **Large**: 24px (feature icons)

### 12.3 状态指示
- 纯色表示状态
- 透明度表示层次
- 颜色区分语义

---

## 13. 无障碍设计

### 13.1 色彩对比
- 文本与背景: 至少 4.5:1
- 大文本: 至少 3:1
- UI组件: 至少 3:1

### 13.2 焦点管理
- 清晰的焦点样式
- 合理的焦点顺序
- 焦点陷阱在模态框中

### 13.3 屏幕阅读器
- 语义化的HTML
- ARIA标签
- 替代文本

---

## 14. 页面模板

### 14.1 列表页模板
```
┌─────────────────────────────────┐
│ Header                          │
│ Title              Actions      │
├─────────────────────────────────┤
│ Filter / Search                │
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │ Item Card                   │ │
│ │ Title    Meta    Actions    │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ Item Card                   │ │
│ │ Title    Meta    Actions    │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ Pagination                     │
└─────────────────────────────────┘
```

### 14.2 详情页模板
```
┌─────────────────────────────────┐
│ Header                          │
│ Back           Title Actions    │
├─────────────────────────────────┤
│                                 │
│ ┌──────────────┐ ┌────────────┐  │
│ │ Main Content│ │ Sidebar    │  │
│ │             │ │ Actions    │  │
│ │             │ │ Related    │  │
│ └──────────────┘ └────────────┘  │
│                                 │
└─────────────────────────────────┘
```

### 14.3 表单页模板
```
┌─────────────────────────────────┐
│ Header                          │
│ Title              Info         │
├─────────────────────────────────┤
│                                 │
│ ┌─────────────────────────────┐  │
│ │ Form Section 1              │  │
│ │ Field Label                 │  │
│ │ Input Field                 │  │
│ │ Helper Text                 │  │
│ └─────────────────────────────┘  │
│                                 │
│ ┌─────────────────────────────┐  │
│ │ Form Section 2              │  │
│ └─────────────────────────────┘  │
│                                 │
├─────────────────────────────────┤
│ Footer                          │
│ Cancel              Submit      │
└─────────────────────────────────┘
```

---

## 15. 性能优化

### 15.1 代码分割
- 按路由懒加载
- 组件动态导入

### 15.2 资源优化
- 图片压缩
- CSS压缩
- JS Tree Shaking

### 15.3 缓存策略
- 组件缓存
- API响应缓存
- 本地存储

---

## 16. 测试清单

### 16.1 视觉测试
- [ ] 布局一致性
- [ ] 配色正确性
- [ ] 字体加载
- [ ] 图标显示
- [ ] 响应式布局

### 16.2 交互测试
- [ ] 按钮点击
- [ ] 表单验证
- [ ] 动画流畅
- [ ] 键盘导航
- [ ] 主题切换

### 16.3 兼容性测试
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] 移动浏览器

---

## 17. 最佳实践

### 17.1 代码组织
```
src/
├── assets/
│   └── styles/
│       ├── variables.css    # CSS变量
│       ├── base.css         # 基础样式
│       └── components.css   # 组件样式
├── components/
│   ├── common/             # 通用组件
│   └── features/           # 业务组件
├── composables/             # 组合式函数
├── views/                   # 页面组件
└── router/                  # 路由配置
```

### 17.2 命名规范
- CSS类: kebab-case (btn-primary)
- 组件名: PascalCase (AppLayout)
- 文件名: kebab-case (app-layout.vue)

### 17.3 代码风格
- 组件保持简洁
- Props类型定义
- 注释关键逻辑
- 统一代码格式

---

## 18. 文档

- [变量规范](./variables.css)
- [组件文档](../components/)
- [API文档](../api/)
- [设计资源](../assets/)

---

**版本**: 2.0.0
**更新**: 2026-08-07
**维护**: 林育丞
