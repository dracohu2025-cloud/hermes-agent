---
title: "宝玉信息图 — 信息图：21种布局 × 21种风格 (信息图, 可视化)"
sidebar_label: "宝玉信息图"
description: "信息图：21种布局 × 21种风格 (信息图, 可视化)"
---

{/* 此页面由网站/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="baoyu-infographic"></a>
# 宝玉信息图

信息图：21种布局 × 21种风格 (信息图, 可视化)。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/baoyu-infographic` |
| 版本 | `1.56.1` |
| 作者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `infographic`, `visual-summary`, `creative`, `image-generation` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是此技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="infographic-generator"></a>
# 信息图生成器

改编自 [baoyu-infographic](https://github.com/JimLiu/baoyu-skills)，适用于 Hermes Agent 的工具生态。

两个维度：**布局**（信息结构）× **风格**（视觉美学）。可自由组合任意布局与任意风格。

<a id="when-to-use"></a>
## 何时使用

当用户要求创建信息图、视觉摘要、信息图形，或使用“信息图”、“可视化”、“高密度信息大图”等词语时，触发此技能。用户提供内容（文本、文件路径、URL 或主题），并可指定布局、风格、宽高比或语言。

<a id="options"></a>
## 选项

| 选项 | 取值 |
|--------|--------|
| 布局 | 21种选项（见布局画廊），默认：bento-grid |
| 风格 | 21种选项（见风格画廊），默认：craft-handmade |
| 宽高比 | 命名：landscape（16:9），portrait（9:16），square（1:1）。自定义：任意宽:高比（例如 3:4、4:3、2.35:1） |
| 语言 | en、zh、ja 等 |

<a id="layout-gallery"></a>
## 布局画廊

| 布局 | 最佳用途 |
|--------|----------|
| `linear-progression` | 时间线、流程、教程 |
| `binary-comparison` | A vs B、前后对比、优缺点 |
| `comparison-matrix` | 多因素比较 |
| `hierarchical-layers` | 金字塔、优先级层级 |
| `tree-branching` | 分类、分类法 |
| `hub-spoke` | 中心概念与相关项目 |
| `structural-breakdown` | 分解视图、截面图 |
| `bento-grid` | 多主题、概览（默认） |
| `iceberg` | 表面与隐藏层面 |
| `bridge` | 问题-解决方案 |
| `funnel` | 转化、过滤 |
| `isometric-map` | 空间关系 |
| `dashboard` | 指标、KPI |
| `periodic-table` | 分类集合 |
| `comic-strip` | 叙述、序列 |
| `story-mountain` | 情节结构、张力弧线 |
| `jigsaw` | 相互连接的部分 |
| `venn-diagram` | 重叠概念 |
| `winding-roadmap` | 旅程、里程碑 |
| `circular-flow` | 循环、重复过程 |
| `dense-modules` | 高密度模块、数据丰富的指南 |

完整定义：`references/layouts/&lt;layout&gt;.md`

<a id="style-gallery"></a>
## 风格画廊

| 风格 | 描述 |
|-------|-------------|
| `craft-handmade` | 手绘、纸艺（默认） |
| `claymation` | 3D 泥塑、定格动画 |
| `kawaii` | 日本可爱、粉彩 |
| `storybook-watercolor` | 柔和手绘、奇幻风格 |
| `chalkboard` | 黑板粉笔 |
| `cyberpunk-neon` | 霓虹发光、未来风格 |
| `bold-graphic` | 漫画风格、半色调 |
| `aged-academia` | 复古科学、棕褐色 |
| `corporate-memphis` | 扁平矢量、鲜艳配色 |
| `technical-schematic` | 蓝图、工程 |
| `origami` | 折纸、几何 |
| `pixel-art` | 复古 8-bit |
| `ui-wireframe` | 灰度界面原型 |
| `subway-map` | 地铁线路图 |
| `ikea-manual` | 极简线条画 |
| `knolling` | 整齐平铺 |
| `lego-brick` | 积木搭建 |
| `pop-laboratory` | 蓝图网格、坐标标记、实验室精度 |
| `morandi-journal` | 手绘涂鸦、温暖莫兰迪色调 |
| `retro-pop-grid` | 1970年代复古波普艺术、瑞士网格、粗轮廓 |
| `hand-drawn-edu` | 马卡龙粉彩、手绘抖动、火柴人 |
完整定义：`references/styles/&lt;style&gt;.md`

<a id="recommended-combinations"></a>
## 推荐组合

| 内容类型 | 布局 + 样式 |
|--------------|----------------|
| 时间线/历史 | `linear-progression` + `craft-handmade` |
| 分步指南 | `linear-progression` + `ikea-manual` |
| A vs B | `binary-comparison` + `corporate-memphis` |
| 层级结构 | `hierarchical-layers` + `craft-handmade` |
| 重叠关系 | `venn-diagram` + `craft-handmade` |
| 转化漏斗 | `funnel` + `corporate-memphis` |
| 循环流程 | `circular-flow` + `craft-handmade` |
| 技术结构 | `structural-breakdown` + `technical-schematic` |
| 指标 | `dashboard` + `corporate-memphis` |
| 教育内容 | `bento-grid` + `chalkboard` |
| 旅程 | `winding-roadmap` + `storybook-watercolor` |
| 分类 | `periodic-table` + `bold-graphic` |
| 产品指南 | `dense-modules` + `morandi-journal` |
| 技术指南 | `dense-modules` + `pop-laboratory` |
| 潮流指南 | `dense-modules` + `retro-pop-grid` |
| 教育图表 | `hub-spoke` + `hand-drawn-edu` |
| 流程教程 | `linear-progression` + `hand-drawn-edu` |

默认：`bento-grid` + `craft-handmade`

<a id="keyword-shortcuts"></a>
## 关键词快捷方式

当用户输入包含这些关键词时，**自动选择**关联的布局，并在步骤 3 中将关联样式作为首选推荐提供。跳过匹配关键词时的基于内容布局推断。

如果某个快捷方式包含 **提示备注**，则将其作为额外样式说明附加到生成的提示（步骤 5）中。

| 用户关键词 | 布局 | 推荐样式 | 默认宽高比 | 提示备注 |
|--------------|--------|--------------------|----------------|--------------|
| 高密度信息大图 / high-density-info | `dense-modules` | `morandi-journal`, `pop-laboratory`, `retro-pop-grid` | 纵向 | — |
| 信息图 / infographic | `bento-grid` | `craft-handmade` | 横向 | 极简风格：干净画布，充足的留白，无复杂背景纹理。仅限简单卡通元素和图标。 |

<a id="output-structure"></a>
## 输出结构

<!-- ascii-guard-ignore -->
```
infographic/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── structured-content.md
├── prompts/infographic.md
└── infographic.png
```
<!-- ascii-guard-ignore-end -->

Slug：从主题中提取的小写 kebab-case 词（2-4 个）。冲突：追加 `-YYYYMMDD-HHMMSS`。

<a id="core-principles"></a>
## 核心原则

- 忠实保留源数据——不进行摘要或改写（但在输出之前**去除任何凭证、API 密钥、令牌或机密**）
- 在组织内容之前定义学习目标
- 为视觉传达而组织（标题、标签、视觉元素）

<a id="workflow"></a>
## 工作流程

<a id="step-1-analyze-content"></a>
### 步骤 1：分析内容

**加载参考**：读取本技能中的 `references/analysis-framework.md`。

1. 保存源内容（文件路径或粘贴 → 使用 `write_file` 写入 `source.md`）
   - **备份规则**：如果 `source.md` 已存在，则重命名为 `source-backup-YYYYMMDD-HHMMSS.md`
2. 分析：主题、数据类型、复杂度、语气、受众
3. 检测源语言和用户语言
4. 从用户输入中提取设计指令
5. 将分析保存到 `analysis.md`
   - **备份规则**：如果 `analysis.md` 已存在，则重命名为 `analysis-backup-YYYYMMDD-HHMMSS.md`
请参考 `references/analysis-framework.md` 了解详细格式。

<a id="step-2-generate-structured-content-structured-content-md"></a>
### 第 2 步：生成结构化内容 → `structured-content.md`

将内容转换为信息图结构：
1. 标题和学习目标
2. 章节包含：核心概念、内容（逐字）、视觉元素、文本标签
3. 数据点（所有统计/引述完全复制）
4. 用户的设计指示

**规则**：仅限 Markdown。不添加新信息。忠实保留数据。从输出中去除任何凭证或密钥。

请参考 `references/structured-content-template.md` 了解详细格式。

<a id="step-3-recommend-combinations"></a>
### 第 3 步：推荐组合

**3.1 先检查关键词快捷键**：如果用户输入与**关键词快捷键**表中的某个关键词匹配，则自动选择关联布局，并优先推荐关联样式。跳过基于内容的布局推断。

**3.2 否则**，基于以下内容推荐 3-5 种布局×样式组合：
- 数据结构 → 匹配布局
- 内容基调 → 匹配样式
- 受众预期
- 用户设计指示

<a id="step-4-confirm-options"></a>
### 第 4 步：确认选项

使用 `clarify` 工具与用户确认选项。由于 `clarify` 一次只能处理一个问题，请先问最重要的问题：

**Q1 — 组合**：呈现 3 种以上布局×样式组合，并给出理由。请用户选择一种。

**Q2 — 宽高比**：询问宽高比偏好（横版/竖版/方形或自定义 W:H）。

**Q3 — 语言**（仅当源语言 ≠ 用户语言时）：询问文本内容应使用哪种语言。

<a id="step-5-generate-prompt-prompts-infographic-md"></a>
### 第 5 步：生成提示词 → `prompts/infographic.md`

**备份规则**：如果 `prompts/infographic.md` 已存在，则重命名为 `prompts/infographic-backup-YYYYMMDD-HHMMSS.md`

**加载参考**：从 `references/layouts/&lt;layout&gt;.md` 读取所选布局，从 `references/styles/&lt;style&gt;.md` 读取所选样式。

组合：
1. 来自 `references/layouts/&lt;layout&gt;.md` 的布局定义
2. 来自 `references/styles/&lt;style&gt;.md` 的样式定义
3. 来自 `references/base-prompt.md` 的基础模板
4. 第 2 步的结构化内容
5. 确认的语言中的所有文本

**宽高比解析**用于 `{{ASPECT_RATIO}}`：
- 命名预设 → 比例字符串：landscape→`16:9`，portrait→`9:16`，square→`1:1`
- 自定义 W:H 比例 → 原样使用（例如 `3:4`、`4:3`、`2.35:1`）

使用 `write_file` 将组装好的提示词保存到 `prompts/infographic.md`。

<a id="step-6-generate-image"></a>
### 第 6 步：生成图像

使用第 5 步组装好的提示词，调用 `image_generate` 工具。

- 将宽高比映射为 `image_generate` 的格式：`16:9` → `landscape`，`9:16` → `portrait`，`1:1` → `square`
- 对于自定义比例，选择最接近的命名宽高比
- 失败时自动重试一次
- 将生成的图像 URL/路径保存到输出目录

<a id="step-7-output-summary"></a>
### 第 7 步：输出摘要

报告：主题、布局、样式、宽高比、语言、输出路径、创建的文件。

<a id="references"></a>
## 参考文献

- `references/analysis-framework.md` — 分析方法
- `references/structured-content-template.md` — 内容格式
- `references/base-prompt.md` — 提示词模板
- `references/layouts/&lt;layout&gt;.md` — 21 种布局定义
- `references/styles/&lt;style&gt;.md` — 21 种样式定义
<a id="pitfalls"></a>
## 常见陷阱

1. **数据完整性至关重要** — 切勿对源统计数据做摘要、改写或篡改。"73% increase"必须保持为"73% increase"，不能写成"significant increase"。
2. **清除敏感信息** — 在将来源内容写入任何输出文件之前，始终检查其中是否包含 API 密钥、令牌或凭证。
3. **每个版块只传达一条信息** — 信息图的每个版块应传达一个清晰的概念。版块信息过载会降低可读性。
4. **风格一致性** — 来自参考文件的风格定义必须在整个信息图中一致应用。不要混用风格。
5. **image_generate 宽高比** — 该工具仅支持 `landscape`、`portrait` 和 `square`。像 `3:4` 这样的自定义比例应映射到最接近的选项（此例中为 portrait）。
