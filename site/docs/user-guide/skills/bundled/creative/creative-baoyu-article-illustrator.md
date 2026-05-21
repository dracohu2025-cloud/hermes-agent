---
title: "宝玉文章插图 — 文章插图：类型 × 风格 × 配色统一"
sidebar_label: "宝玉文章插图"
description: "文章插图：类型 × 风格 × 配色统一"
---

{/* 此页面由 skills/creative/baoyu-article-illustrator/SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="baoyu-article-illustrator"></a>
# 宝玉文章插图

文章插图：类型 × 风格 × 配色统一。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/baoyu-article-illustrator` |
| 版本 | `1.57.0` |
| 作者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `article-illustration`, `creative`, `image-generation` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。技能激活后，Agent 会将其视为指令。
:::

<a id="article-illustrator"></a>
# 文章插图

改编自 [baoyu-article-illustrator](https://github.com/JimLiu/baoyu-skills)，适配 Hermes Agent 的工具生态。

分析文章，识别插图位置，生成符合 **类型 × 风格 × 配色** 统一的图片。

<a id="when-to-use"></a>
## 使用时机

当用户要求给文章配图、为内容添加图片、生成内容插图，或使用诸如“为文章配图”“illustrate article”“add images”等表述时，触发此技能。用户提供文章（文件路径或粘贴的内容），并可指定类型、风格、配色及密度。

<a id="three-dimensions"></a>
## 三个维度

| 维度 | 控制项 | 示例 |
|-----------|----------|----------|
| **类型** | 信息结构 | infographic, scene, flowchart, comparison, framework, timeline |
| **风格** | 渲染方式 | notion, warm, minimal, blueprint, watercolor, elegant |
| **配色** | 色彩方案（可选） | macaron, warm, neon — 覆盖风格的默认配色 |

可自由组合：`type=infographic, style=vector-illustration, palette=macaron`。

或使用预设：`edu-visual` → 类型 + 风格 + 配色一步到位。参见 [style-presets.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/style-presets.md)。

<a id="types"></a>
## 类型

| 类型 | 最佳适用场景 |
|------|----------|
| `infographic` | 数据、指标、技术 |
| `scene` | 叙事、情感 |
| `flowchart` | 流程、工作流 |
| `comparison` | 并列对比、选项 |
| `framework` | 模型、架构 |
| `timeline` | 历史、演变 |

<a id="styles"></a>
## 风格

关于核心风格、完整图片库以及类型 × 风格兼容性，请参见 [references/styles.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/styles.md)。

<a id="output-structure"></a>
## 输出结构

<!-- ascii-guard-ignore -->
```
{output-dir}/
├── source-{slug}.{ext}    # 仅针对粘贴的内容
├── outline.md
├── prompts/
│   └── NN-{type}-{slug}.md
└── NN-{type}-{slug}.png
```
<!-- ascii-guard-ignore-end -->

**默认输出目录**：

| 输入 | 输出目录 | Markdown 插入路径 |
|-------|------------------|----------------------|
| 文章文件路径 | `{article-dir}/imgs/` | `imgs/NN-{type}-{slug}.png` |
| 粘贴的内容 | `illustrations/{topic-slug}/` (cwd) | `illustrations/{topic-slug}/NN-{type}-{slug}.png` |
如果用户要求不同的布局（例如，图片放在文章旁边，或 `illustrations/` 子目录），请遵循。

**Slug**：2-4 个单词，kebab-case（短横线分隔）。**冲突**：追加 `-YYYYMMDD-HHMMSS`。

<a id="core-principles"></a>
## 核心原则

- **可视化概念，而非隐喻** —— 如果文章使用了隐喻（例如“电锯切西瓜”），请说明底层概念，而不是字面图像。
- **标签使用文章数据** —— 使用文章中的实际数字、术语和引用，而不是通用占位符。
- **提示文件是可复现性记录** —— 在生成任何图像之前，必须在 `prompts/` 下保存每个插图的提示文件。
- **去除敏感信息** —— 在将任何内容写入磁盘之前，扫描源内容中是否有 API 密钥、令牌或凭据。

<a id="workflow"></a>
## 工作流程

```
- [ ] 步骤 1：检测参考图像（如果提供）
- [ ] 步骤 2：分析内容
- [ ] 步骤 3：确认设置（每次一个问题澄清工具）
- [ ] 步骤 4：生成大纲
- [ ] 步骤 5：生成提示词
- [ ] 步骤 6：生成图片（image_generate）
- [ ] 步骤 7：定稿
```

<a id="step-1-detect-reference-images"></a>
### 步骤 1：检测参考图像

如果用户提供参考图像（内联粘贴的路径、附件或 URL）：

1. 对于每个参考图，使用 `vision_analyze` 并传入路径/URL 以及一个问题，询问风格、调色板、构图和主体。通过 `write_file` 将返回的描述记录到 `{output-dir}/references/NN-ref-{slug}.md`。
2. **不要**尝试通过 `write_file` / `read_file` 复制二进制文件——这些只支持文本。如果你想要一份本地副本作为记录，请使用 `terminal`（`cp "$src" "{output-dir}/references/NN-ref-{slug}.{ext}"`）。该技能本身从来不需要读取二进制文件；它基于视觉描述工作。
3. 由于 `image_generate` 不接受图像输入，因此在步骤 5 中，视觉描述会被嵌入到提示词中。

完整流程：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md#step-1-detect-reference-images)

<a id="step-2-analyze"></a>
### 步骤 2：分析

| 分析项 | 输出 |
|--------|------|
| 内容类型 | 技术 / 教程 / 方法论 / 故事 |
| 目的 | 信息传达 / 可视化 / 想象 |
| 核心论点 | 2-5 个要点 |
| 位置 | 插图在哪些地方增加价值 |

读取源文件（文件路径 → `read_file`，或者粘贴的文本），并通过 `write_file` 将分析结果写入 `{output-dir}/analysis.md`。

完整流程：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md#step-2-analyze)

<a id="step-3-confirm-settings"></a>
### 步骤 3：确认设置

使用 `clarify` 工具。由于 `clarify` 一次只处理一个问题，请先问最重要的问题。跳过任何答案已在用户请求中明确的问题。

| 顺序 | 问题 | 选项 |
|------|------|------|
| Q1 | **预设或类型** | [推荐预设], [备选预设], 或手动：信息图、场景、流程图、对比、框架、时间线、混合 |
| Q2 | **密度** | 最少（1-2 张）、平衡（3-5 张）、按章节（推荐）、丰富（6 张以上） |
| Q3 | **风格** *（如果在 Q1 中选择了预设则跳过）* | [推荐]、极简扁平、科幻、手绘、编辑风格、场景、海报 |
| Q4 | **调色板** *（可选）* | 默认（风格色）、马卡龙、暖色、霓虹 |
| Q5 | **语言** *（仅当文章语言不明确时）* | 文章语言 / 用户语言 |
不要连续问超过 2-3 个 `clarify` 问题。如果用户已经在请求中指定了这些内容，则直接跳过。

完整流程：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md#step-3-confirm-settings)

<a id="step-4-generate-outline-outline-md"></a>
### 第 4 步：生成大纲 → `outline.md`

使用 `write_file` 将 `{output-dir}/outline.md` 保存，包含 frontmatter（type、density、style、palette、image_count）以及每张插图的条目：

```yaml
## 插图 1
**位置**：[section/paragraph]
**目的**：[why]
**视觉内容**：[what to show]
**文件名**：01-infographic-concept-name.png
```

完整模板：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md#step-4-generate-outline)

<a id="step-5-generate-prompts"></a>
### 第 5 步：生成提示词

**阻塞项**：每张插图在生成任何图像之前，必须保存对应的提示词文件——提示词文件是复现性记录。

对于每张插图：

1. 按照 [references/prompt-construction.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/prompt-construction.md) 创建提示词文件。
2. 使用 `write_file` 保存到 `{output-dir}/prompts/NN-{type}-{slug}.md`，包含 YAML frontmatter。
3. 提示词必须使用类型特定的模板，包含结构化部分（ZONES / LABELS / COLORS / STYLE / ASPECT）。
4. LABELS 必须包含文章特定的数据：实际数字、术语、指标、引用。
5. 按提示词 frontmatter 处理参考（`direct`/`style`/`palette`）——对于 `direct` 用法，在提示词中嵌入参考的文本描述（因为 `image_generate` 不接受参考图像输入）。

<a id="step-6-generate-images"></a>
### 第 6 步：生成图像

对于每个提示词文件：

1. 调用 `image_generate(prompt=..., aspect_ratio=...)`。`image_generate` 返回包含图像 URL 的 JSON 结果；它不会写入磁盘，也不接受输出路径。
2. 将提示词的 `ASPECT` 映射到 `image_generate` 的枚举：`16:9` → `landscape`，`9:16` → `portrait`，`1:1` → `square`。自定义比例 → 最接近的命名宽高比。
3. 通过 `terminal`（例如 `curl -sSL -o "{output-dir}/NN-{type}-{slug}.png" "{url}"`）将返回的 URL 下载到 `{output-dir}/NN-{type}-{slug}.png`。
4. 如果生成失败，自动重试一次。

注意：底层的图像生成后端由用户配置（默认：FAL FLUX 2 Klein 9B），Agent 不能通过 `image_generate` 选择。不要在提示词中写入模型名称，期望它们被路由。

<a id="step-7-finalize"></a>
### 第 7 步：最终确定

在对应段落之后插入 `![description](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/{relative-path}/NN-{type}-{slug}.png)`。Alt 文本：使用文章语言的简洁描述。

报告：

```
文章插图完成！
文章：[path] | 类型：[type] | 密度：[level] | 风格：[style] | 调色板：[palette or default]
图像：X/N 已生成
```
<a id="modification"></a>
## 修改

| 操作 | 步骤 |
|--------|-------|
| 编辑 | 更新提示词 → 重新生成 → 更新引用 |
| 添加 | 定位 → 提示词 → 生成 → 更新大纲 → 插入 |
| 删除 | 删除文件 → 移除引用 → 更新大纲 |

<a id="references"></a>
## 参考资料

| 文件 | 内容 |
|------|---------|
| [references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/workflow.md) | 详细流程 |
| [references/usage.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/usage.md) | 调用示例 |
| [references/styles.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/styles.md) | 风格画廊 + 调色板画廊 |
| [references/style-presets.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/style-presets.md) | 预设快捷方式（类型 + 风格 + 调色板） |
| [references/prompt-construction.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-article-illustrator/references/prompt-construction.md) | 提示词模板 |

<a id="pitfalls"></a>
## 注意事项

1. **数据完整性至关重要** — 切勿对源统计数据进行总结、转述或更改。"73% 增长"就保持"73% 增长"。
2. **去除机密信息** — 在包含到任何输出文件之前，扫描源内容中的 API 密钥、令牌或凭据。
3. **不要按字面意思绘制比喻** — 可视化其背后的概念。
4. **提示词文件是必需的** — 没有保存的提示词文件就不能生成图像。该文件让你以后可以重新生成或切换后端。
5. **`image_generate` 宽高比** — 该工具支持 `landscape`（横向）、`portrait`（纵向）和 `square`（方形）。自定义比例会映射到最接近的选项。
6. **`image_generate` 返回的是 URL，不是本地文件** — 在将本地图像路径插入文章之前，务必通过 `terminal`（`curl`）下载。
7. **Agent 不负责选择后端** — `image_generate` 使用用户配置的任何模型（默认：FAL FLUX 2 Klein 9B）。不要在提示词中写"使用 `<模型>` 生成此内容"，期望它能路由到指定模型。
