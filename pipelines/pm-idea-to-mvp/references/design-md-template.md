# DESIGN.md — 设计系统文档

> 来源：基于 [Google Stitch DESIGN.md](https://stitch.withgoogle.com/docs/design-md/overview/) 格式
> 用途：Spec 阶段产出，为 MVP 阶段提供设计约束

## 1. 视觉主题（Visual Theme）

**品牌定位**：[描述产品的品牌定位和目标用户]

**设计语言**：[选择设计语言：Material / Fluent / Carbon / Polaris / Atlassian / Primer / GOV.UK / USWDS / Bootstrap / Radix / shadcn / Tailwind / Native CSS]

**整体风格**：[极简 / 专业 / 活泼 / 企业级 / 消费级]

## 2. 颜色（Colors）

### 主色（Primary）
- **主色**：`#XXXXXX` — [用途说明]
- **主色深色**：`#XXXXXX` — hover/active 状态
- **主色浅色**：`#XXXXXX` — 背景/高亮

### 中性色（Neutrals）
- **文字主色**：`#XXXXXX` — 主要文字
- **文字次色**：`#XXXXXX` — 次要文字/说明
- **边框**：`#XXXXXX` — 分割线/边框
- **背景**：`#XXXXXX` — 页面背景
- **卡片背景**：`#XXXXXX` — 卡片/容器背景

### 语义色（Semantic）
- **成功**：`#XXXXXX`
- **警告**：`#XXXXXX`
- **错误**：`#XXXXXX`
- **信息**：`#XXXXXX`

### 暗色模式（Dark Mode）
- [ ] 需要暗色模式
- [ ] 不需要暗色模式

如需暗色模式，请提供对应的暗色色值。

## 3. 字体（Typography）

### 字体族（Font Family）
- **主字体**：[字体名称，如 Inter / System UI / Noto Sans SC]
- **等宽字体**：[字体名称，如 JetBrains Mono / Fira Code]

### 字体规模（Type Scale）
使用 [模块化比例 / 固定值]：

| 级别 | 大小 | 行高 | 字重 | 用途 |
|------|------|------|------|------|
| Display | 48px | 56px | 700 | 页面标题 |
| H1 | 32px | 40px | 700 | 章节标题 |
| H2 | 24px | 32px | 600 | 子章节 |
| H3 | 20px | 28px | 600 | 卡片标题 |
| Body Large | 18px | 28px | 400 | 引言/强调 |
| Body | 16px | 24px | 400 | 正文 |
| Body Small | 14px | 20px | 400 | 辅助文字 |
| Caption | 12px | 16px | 400 | 标签/注释 |

## 4. 布局与间距（Layout & Spacing）

### 间距系统（Spacing Scale）
基于 [4px / 8px] 网格：

| Token | 值 | 用途 |
|-------|-----|------|
| `space-xs` | 4px | 紧凑间距 |
| `space-sm` | 8px | 元素内间距 |
| `space-md` | 16px | 元素间间距 |
| `space-lg` | 24px | 区块间距 |
| `space-xl` | 32px | 大区块间距 |
| `space-2xl` | 48px | 页面级间距 |

### 布局约束
- **最大宽度**：[1280px / 1440px / 无限制]
- **内容区宽度**：[1024px / 1200px]
- **侧边栏宽度**：[240px / 280px]（如适用）

## 5. 圆角与阴影（Shapes & Elevation）

### 圆角（Border Radius）
| Token | 值 | 用途 |
|-------|-----|------|
| `radius-sm` | 4px | 按钮/输入框 |
| `radius-md` | 8px | 卡片 |
| `radius-lg` | 12px | 大卡片/模态框 |
| `radius-full` | 9999px | 头像/标签 |

### 阴影（Elevation）
| Token | 值 | 用途 |
|-------|-----|------|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | 微凸起 |
| `shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | 卡片 |
| `shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | 模态框/下拉 |
| `shadow-xl` | `0 20px 25px rgba(0,0,0,0.15)` | 悬浮层 |

## 6. 组件（Components）

### 按钮（Button）
- **高度**：[32px / 40px / 48px]
- **内间距**：水平 [16px]，垂直 [8px]
- **字重**：[500 / 600]
- **变体**：Primary / Secondary / Ghost / Danger

### 输入框（Input）
- **高度**：[40px]
- **内间距**：水平 [12px]
- **边框**：[1px solid `#XXXXXX`]
- **焦点状态**：[边框颜色变化 / 阴影]

### 卡片（Card）
- **内间距**：[24px]
- **边框**：[1px solid `#XXXXXX` / 无]
- **圆角**：[`radius-md`]
- **阴影**：[`shadow-md`]

## 7. 动效（Motion）

### 缓动函数（Easing）
- **标准**：`cubic-bezier(0.4, 0, 0.2, 1)` — 大部分过渡
- **减速**：`cubic-bezier(0, 0, 0.2, 1)` — 进入动画
- **加速**：`cubic-bezier(0.4, 0, 1, 1)` — 离开动画

### 时长（Duration）
| Token | 值 | 用途 |
|-------|-----|------|
| `duration-fast` | 150ms | hover/焦点 |
| `duration-normal` | 250ms | 状态切换 |
| `duration-slow` | 350ms | 页面过渡 |

### 减少动效（Reduced Motion）
- [x] 尊重 `prefers-reduced-motion`
- 当用户启用减少动效时，所有动画时长设为 0 或仅使用淡入淡出

## 8. 响应式（Responsive）

### 断点（Breakpoints）
| Token | 值 | 用途 |
|-------|-----|------|
| `sm` | 640px | 手机横屏 |
| `md` | 768px | 平板 |
| `lg` | 1024px | 小桌面 |
| `xl` | 1280px | 大桌面 |
| `2xl` | 1536px | 超大桌面 |

### 移动端适配
- **触摸目标最小尺寸**：44x44px
- **字体最小尺寸**：16px（防止 iOS 缩放）
- **视口**：`width=device-width, initial-scale=1`

## 9. 设计规则（Do's and Don'ts）

### Do's
- [ ] 使用设计系统中的颜色 token，而非硬编码色值
- [ ] 遵循间距系统，保持视觉节奏一致
- [ ] 为所有交互元素提供 hover/focus/active 状态
- [ ] 确保文字对比度符合 WCAG AA 标准（≥4.5:1）
- [ ] 为图片提供 alt 文本
- [ ] 表单字段提供清晰的标签和错误提示

### Don'ts
- [ ] 不使用纯黑（#000000）作为文字颜色
- [ ] 不使用纯白（#FFFFFF）作为背景（使用略带色调的白色）
- [ ] 不使用超过 3 种主色变体
- [ ] 不在同一页面混用多种圆角风格
- [ ] 不使用默认的系统字体（除非 intentionally）
- [ ] 不忽略暗色模式（如果支持）

## 10. 参考（References）

### 灵感来源
- [链接 1] — [说明]
- [链接 2] — [说明]

### 竞品参考
- [竞品 1] — [值得借鉴的点]
- [竞品 2] — [值得借鉴的点]

---

**版本**：1.0.0  
**最后更新**：[日期]  
**维护者**：[姓名/团队]
