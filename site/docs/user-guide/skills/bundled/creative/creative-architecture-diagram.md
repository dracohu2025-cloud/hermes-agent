---
title: "架构图 — 深色主题的 SVG 架构/云/基础设施图，输出为 HTML"
sidebar_label: "架构图"
description: "深色主题的 SVG 架构/云/基础设施图，输出为 HTML"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="architecture-diagram"></a>
# 架构图

深色主题的 SVG 架构/云/基础设施图，输出为 HTML。

<a id="skill-metadata"></a>
## 技能元信息

| | |
|---|---|
| 来源 | 捆绑包（默认安装） |
| 路径 | `skills/creative/architecture-diagram` |
| 版本 | `1.0.0` |
| 作者 | Cocoon AI (hello@cocoon-ai.com)，由 Hermes Agent 移植 |
| 许可证 | MIT |
| 支持平台 | linux, macos, windows |
| 标签 | `架构`, `图`, `SVG`, `HTML`, `可视化`, `基础设施`, `云` |
| 相关技能 | [`concept-diagrams`](/user-guide/skills/optional/creative/creative-concept-diagrams), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是此技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="architecture-diagram-skill"></a>
# 架构图技能

生成专业的、深色主题的技术架构图，作为独立的 HTML 文件，包含内联 SVG 图形。无需外部工具、无需 API 密钥、无需渲染库——只需编写 HTML 文件，然后在浏览器中打开即可。

<a id="scope"></a>
## 适用范围

**最适合用于：**
- 软件系统架构（前端/后端/数据库层）
- 云基础设施（VPC、区域、子网、托管服务）
- 微服务/服务网格拓扑
- 数据库 + API 映射、部署图
- 任何与基础设施相关的技术主题，且适合深色网格背景的视觉风格

**如果遇到以下情况，请优先考虑其他技能：**
- 物理、化学、数学、生物学或其他科学主题
- 实物对象（车辆、硬件、解剖图、剖面图）
- 平面图、叙事路径、教育/教科书风格的插图
- 手绘白板草图（请考虑 `excalidraw`）
- 动态解说视频（请考虑动画技能）

如果存在更专业的技能适用于该主题，请优先使用它们。如果没有合适的技能，本技能也可作为通用的 SVG 图回退方案——输出将带有下面描述的深色技术美学风格。

基于 [Cocoon AI 的 architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT)。

<a id="workflow"></a>
## 工作流程

1. 用户描述其系统架构（组件、连接、技术）
2. 按照下列设计系统生成 HTML 文件
3. 使用 `write_file` 保存为 `.html` 文件（例如 `~/architecture-diagram.html`）
4. 用户在任意浏览器中打开——离线可用，无依赖

<a id="output-location"></a>
### 输出位置

将图保存到用户指定的路径，或默认保存到当前工作目录：
```
./[项目名]-architecture.html
```

<a id="preview"></a>
### 预览

保存后，建议用户使用以下命令打开：
```bash
# macOS
open ./my-architecture.html
# Linux
xdg-open ./my-architecture.html
```

<a id="design-system-visual-language"></a>
## 设计系统与视觉语言

<a id="color-palette-semantic-mapping"></a>
### 颜色调色板（语义映射）

使用特定的 `rgba` 填充色和十六进制描边色对组件进行分类：
| 组件类型 | 填充 (rgba) | 描边 (Hex) |
| :--- | :--- | :--- |
| **前端** | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (青色-400) |
| **后端** | `rgba(6, 78, 59, 0.4)` | `#34d399` (翡翠绿-400) |
| **数据库** | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (紫罗兰-400) |
| **AWS/云** | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (琥珀-400) |
| **安全** | `rgba(136, 19, 55, 0.4)` | `#fb7185` (玫瑰红-400) |
| **消息总线** | `rgba(251, 146, 60, 0.3)` | `#fb923c` (橙色-400) |
| **外部** | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (石板灰-400) |

<a id="typography-background"></a>
### 排版与背景
- **字体:** JetBrains Mono (等宽字体)，从 Google Fonts 加载
- **字号:** 12px (名称)、9px (子标签)、8px (注释)、7px (极小标签)
- **背景:** Slate-950 (`#020617`)，带 40px 的微妙网格图案

```svg
<!-- 背景网格图案 -->
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

<a id="technical-implementation-details"></a>
## 技术实现细节

<a id="component-rendering"></a>
### 组件渲染
组件为圆角矩形 (`rx="6"`)，描边粗细 1.5px。为防止箭头透过半透明填充显示，采用 **双矩形遮罩技术**：
1. 绘制不透明的背景矩形 (`#0f172a`)
2. 在其上方绘制半透明样式的矩形

<a id="connection-rules"></a>
### 连接规则
- **Z 轴顺序:** 在 SVG 中 *尽早* 绘制箭头（在网格之后），使其渲染在组件框的后面
- **箭头:** 通过 SVG marker 定义
- **安全数据流:** 使用玫瑰色虚线 (`#fb7185`)
- **边界:**
  - *安全组:* 虚线 (`4,4`)，玫瑰色
  - *区域:* 大虚线 (`8,4`)，琥珀色，`rx="12"`

<a id="spacing-layout-logic"></a>
### 间距与布局逻辑
- **标准高度:** 60px (服务)；80-120px (大型组件)
- **垂直间距:** 组件之间最小 40px
- **消息总线:** 必须放置于服务之间的 *空隙* 中，不能重叠
- **图例位置:** **关键。** 必须放置在所有边界框之外。计算所有边界的最低 Y 坐标，并将图例放置在该坐标至少 20px 以下的位置。

<a id="document-structure"></a>
## 文档结构

生成的 HTML 文件采用四部分布局：
1. **页头:** 标题（带脉冲圆点指示器）和副标题
2. **主 SVG:** 包含在圆角边框卡片中的图表
3. **摘要卡片:** 图表下方显示三个卡片网格，用于高层级细节
4. **页脚:** 极简元数据

<a id="info-card-pattern"></a>
### 信息卡片模板
```html
<div class="card">
  <div class="card-header">
    <div class="card-dot cyan"></div>
    <h3>标题</h3>
  </div>
  <ul>
    <li>• 第一项</li>
    <li>• 第二项</li>
  </ul>
</div>
```

<a id="output-requirements"></a>
## 输出要求
- **单文件:** 一个自包含的 `.html` 文件
- **无外部依赖:** 所有 CSS 和 SVG 必须内联（Google Fonts 除外）
- **无 JavaScript:** 任何动画（如脉冲圆点）都应仅使用纯 CSS
- **兼容性:** 必须在所有现代浏览器中正确渲染

<a id="template-reference"></a>
## 模板参考

加载完整的 HTML 模板，以获取精确的结构、CSS 和 SVG 组件示例：
```
skill_view(name="architecture-diagram", file_path="templates/template.html")
```

该模板包含了每种组件类型（前端、后端、数据库、云、安全）的工作示例、箭头样式（标准、虚线、曲线）、安全组、区域边界和图例——在生成架构图时，请将其作为结构参考。
