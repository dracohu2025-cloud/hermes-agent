---
title: "宝玉信息图 — 信息图：21 种布局 × 21 种风格 (信息图, 可视化)"
sidebar_label: "宝玉信息图"
description: "信息图：21 种布局 × 21 种风格 (信息图, 可视化)"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉信息图 {#baoyu-infographic}

信息图：21 种布局 × 21 种风格 (信息图, 可视化)。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/baoyu-infographic` |
| 版本 | `1.56.1` |
| 作者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 标签 | `infographic`, `visual-summary`, `creative`, `image-generation` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 agent 在技能激活时看到的指令。
:::

# 信息图生成器 {#infographic-generator}

改编自 [baoyu-infographic](https://github.com/JimLiu/baoyu-skills)，适用于 Hermes Agent 的工具生态。

两个维度：**布局**（信息结构）× **风格**（视觉美学）。可自由组合任意布局与任意风格。

## 何时使用 {#when-to-use}

当用户要求创建信息图、视觉摘要、信息图形，或使用“信息图”、“可视化”、“高密度信息大图”等术语时，触发此技能。用户提供内容（文本、文件路径、URL 或主题），并可选择指定布局、风格、宽高比或语言。

## 选项 {#options}

| 选项 | 取值 |
|--------|--------|
| 布局 | 21 种（参见布局画廊），默认：bento-grid |
| 风格 | 21 种（参见风格画廊），默认：craft-handmade |
| 宽高比 | 命名：landscape (16:9), portrait (9:16), square (1:1)。自定义：任意 W:H 比例（如 3:4, 4:3, 2.35:1） |
| 语言 | en, zh, ja 等 |

## 布局画廊 {#layout-gallery}

| 布局 | 最佳用途 |
|--------|----------|
| `linear-progression` | 时间线、流程、教程 |
| `binary-comparison` | A vs B、前后对比、优缺点 |
| `comparison-matrix` | 多因素比较 |
| `hierarchical-layers` | 金字塔、优先级层级 |
| `tree-branching` | 分类、分类法 |
| `hub-spoke` | 中心概念与相关项目 |
| `structural-breakdown` | 分解视图、剖面图 |
| `bento-grid` | 多主题、概览（默认） |
| `iceberg` | 表面 vs 隐藏方面 |
| `bridge` | 问题-解决方案 |
| `funnel` | 转化、筛选 |
| `isometric-map` | 空间关系 |
| `dashboard` | 指标、KPI |
| `periodic-table` | 分类集合 |
| `comic-strip` | 叙事、序列 |
| `story-mountain` | 情节结构、张力弧线 |
| `jigsaw` | 相互关联的部分 |
| `venn-diagram` | 重叠概念 |
| `winding-roadmap` | 旅程、里程碑 |
| `circular-flow` | 循环、重复过程 |
| `dense-modules` | 高密度模块、数据丰富的指南 |

完整定义：`references/layouts/&lt;layout&gt;.md`

## 风格画廊 {#style-gallery}

| 风格 | 描述 |
|-------|-------------|
| `craft-handmade` | 手绘、纸艺（默认） |
| `claymation` | 3D 黏土人物、定格动画 |
| `kawaii` | 日式可爱、柔和色彩 |
| `storybook-watercolor` | 柔和绘画、奇幻风格 |
| `chalkboard` | 黑板粉笔 |
| `cyberpunk-neon` | 霓虹光效、未来主义 |
| `bold-graphic` | 漫画风格、半色调 |
| `aged-academia` | 复古科学、棕褐色 |
| `corporate-memphis` | 扁平矢量、鲜艳 |
| `technical-schematic` | 蓝图、工程 |
| `origami` | 折纸、几何 |
| `pixel-art` | 复古 8 位 |
| `ui-wireframe` | 灰度界面线框图 |
| `subway-map` | 地铁线路图 |
| `ikea-manual` | 极简线条画 |
| `knolling` | 整齐平铺 |
| `lego-brick` | 乐高积木搭建 |
| `pop-laboratory` | 蓝图网格、坐标标记、实验室精度 |
| `morandi-journal` | 手绘涂鸦、温暖莫兰迪色调 |
| `retro-pop-grid` | 1970 年代复古波普艺术、瑞士网格、粗轮廓线 |
| `hand-drawn-edu` | 马卡龙柔和色、手绘抖动、火柴人 |
完整定义：`references/styles/&lt;style&gt;.md`

## 推荐组合 {#recommended-combinations}

| 内容类型 | 布局 + 风格 |
|--------------|----------------|
| 时间线/历史 | `linear-progression` + `craft-handmade` |
| 分步骤 | `linear-progression` + `ikea-manual` |
| A vs B | `binary-comparison` + `corporate-memphis` |
| 层级结构 | `hierarchical-layers` + `craft-handmade` |
| 重叠关系 | `venn-diagram` + `craft-handmade` |
| 转化流程 | `funnel` + `corporate-memphis` |
| 循环 | `circular-flow` + `craft-handmade` |
| 技术类 | `structural-breakdown` + `technical-schematic` |
| 指标 | `dashboard` + `corporate-memphis` |
| 教育类 | `bento-grid` + `chalkboard` |
| 旅程 | `winding-roadmap` + `storybook-watercolor` |
| 分类 | `periodic-table` + `bold-graphic` |
| 产品指南 | `dense-modules` + `morandi-journal` |
| 技术指南 | `dense-modules` + `pop-laboratory` |
| 潮流指南 | `dense-modules` + `retro-pop-grid` |
| 教育图解 | `hub-spoke` + `hand-drawn-edu` |
| 操作教程 | `linear-progression` + `hand-drawn-edu` |

默认：`bento-grid` + `craft-handmade`

## 关键词快捷方式 {#keyword-shortcuts}

当用户输入包含以下关键词时，**自动选择**对应的布局，并在第3步中将关联风格作为首要推荐。对于匹配的关键词，跳过基于内容的布局推断。

如果某个快捷方式带有 **Prompt Notes**，则将其追加到第5步生成的提示中，作为额外的风格指令。

| 用户关键词 | 布局 | 推荐风格 | 默认宽高比 | Prompt Notes |
|--------------|--------|--------------------|----------------|--------------|
| 高密度信息大图 / high-density-info | `dense-modules` | `morandi-journal`, `pop-laboratory`, `retro-pop-grid` | portrait | — |
| 信息图 / infographic | `bento-grid` | `craft-handmade` | landscape | 极简风格：干净的画布、充足的留白、无复杂背景纹理。仅使用简单的卡通元素和图标。 |

## 输出结构 {#output-structure}

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

Slug：基于主题的2-4个单词的kebab-case。冲突时追加 `-YYYYMMDD-HHMMSS`。

## 核心原则 {#core-principles}

- 忠实保留源数据——不进行总结或改写（但在输出前**必须剔除任何凭证、API密钥、令牌或秘密**）
- 在组织内容前先定义学习目标
- 以视觉传达方式组织内容（标题、标签、视觉元素）

## 工作流程 {#workflow}

### 第一步：分析内容 {#step-1-analyze-content}

**加载参考文件**：读取本技能中的 `references/analysis-framework.md`。

1. 保存源内容（文件路径或粘贴 → 使用 `write_file` 保存为 `source.md`）
   - **备份规则**：如果 `source.md` 已存在，重命名为 `source-backup-YYYYMMDD-HHMMSS.md`
2. 分析：主题、数据类型、复杂度、语气、受众
3. 检测源语言和用户语言
4. 从用户输入中提取设计指令
5. 将分析结果保存到 `analysis.md`
   - **备份规则**：如果 `analysis.md` 已存在，重命名为 `analysis-backup-YYYYMMDD-HHMMSS.md`
See `references/analysis-framework.md` 了解详细格式。

### 步骤 2：生成结构化内容 → `structured-content.md` {#step-2-generate-structured-content-structured-content-md}

将内容转换为信息图结构：
1. 标题与学习目标
2. 章节包含：核心概念、内容（原文）、视觉元素、文本标签
3. 数据点（所有统计/引用需完全照搬）
4. 用户提供的设计说明

**规则**：仅使用 Markdown。不添加新信息。忠实保留数据。从输出中去除任何凭证或密钥。

详见 `references/structured-content-template.md` 了解详细格式。

### 步骤 3：推荐组合 {#step-3-recommend-combinations}

**3.1 先检查关键词快捷方式**：如果用户输入匹配 **关键词快捷方式** 表中的某个关键词，则自动选择关联的布局，并将关联样式作为首选推荐。跳过基于内容的布局推断。

**3.2 否则**，根据以下条件推荐 3-5 种布局×样式组合：
- 数据结构 → 匹配布局
- 内容基调 → 匹配样式
- 受众预期
- 用户设计说明

### 步骤 4：确认选项 {#step-4-confirm-options}

使用 `clarify` 工具与用户确认选项。由于 `clarify` 一次只处理一个问题，请先问最重要的问题：

**Q1 — 组合**：展示 3 种以上布局×样式组合并附上理由。请用户选择一种。

**Q2 — 宽高比**：询问宽高比偏好（横版/竖版/正方形或自定义 W:H）。

**Q3 — 语言**（仅当源语言 ≠ 用户语言时）：询问文本内容应使用哪种语言。

### 步骤 5：生成提示词 → `prompts/infographic.md` {#step-5-generate-prompt-prompts-infographic-md}

**备份规则**：如果 `prompts/infographic.md` 已存在，则将其重命名为 `prompts/infographic-backup-YYYYMMDD-HHMMSS.md`

**加载参考**：从 `references/layouts/&lt;layout&gt;.md` 读取所选布局，从 `references/styles/&lt;style&gt;.md` 读取所选样式。

组合：
1. 来自 `references/layouts/&lt;layout&gt;.md` 的布局定义
2. 来自 `references/styles/&lt;style&gt;.md` 的样式定义
3. 来自 `references/base-prompt.md` 的基础模板
4. 步骤 2 中的结构化内容
5. 所有文本使用已确认的语言

`{{ASPECT_RATIO}}` 的宽高比解析：
- 命名预设 → 比例字符串：landscape→`16:9`，portrait→`9:16`，square→`1:1`
- 自定义 W:H 比例 → 原样使用（例如 `3:4`、`4:3`、`2.35:1`）

使用 `write_file` 将组装好的提示词保存到 `prompts/infographic.md`。

### 步骤 6：生成图像 {#step-6-generate-image}

使用步骤 5 中组装好的提示词，调用 `image_generate` 工具。

- 将宽高比映射为 image_generate 的格式：`16:9` → `landscape`，`9:16` → `portrait`，`1:1` → `square`
- 对于自定义比例，选择最接近的命名宽高比
- 失败时自动重试一次
- 将生成的图像 URL/路径保存到输出目录

### 步骤 7：输出摘要 {#step-7-output-summary}

报告：主题、布局、样式、宽高比、语言、输出路径、创建的文件。

## 参考 {#references}

- `references/analysis-framework.md` — 分析方法论
- `references/structured-content-template.md` — 内容格式
- `references/base-prompt.md` — 提示词模板
- `references/layouts/&lt;layout&gt;.md` — 21 种布局定义
- `references/styles/&lt;style&gt;.md` — 21 种样式定义
## 常见陷阱 {#pitfalls}

1. **数据完整性至关重要** — 切勿对源统计数据做摘要、改写或修改。"73% increase" 必须保持为 "73% increase"，不能写成 "significant increase"。
2. **清除机密信息** — 在将源内容包含到任何输出文件之前，务必扫描其中是否含有 API 密钥、令牌或凭据。
3. **每个部分只传达一个信息** — 信息图的每个部分应传达一个清晰的概念。内容过载会降低可读性。
4. **风格一致性** — 必须将参考文件中的风格定义一致地应用于整张信息图。不要混用风格。
5. **image_generate 宽高比** — 该工具仅支持 `landscape`、`portrait` 和 `square`。自定义比例（如 `3:4`）应映射到最接近的选项（此处为 portrait）。
