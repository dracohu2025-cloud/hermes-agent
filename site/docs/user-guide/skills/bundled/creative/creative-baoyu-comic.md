---
title: "Baoyu Comic — 知识漫画：教育、传记、教程"
sidebar_label: "Baoyu Comic"
description: "知识漫画：教育、传记、教程"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="baoyu-comic"></a>
# Baoyu Comic

知识漫画：教育、传记、教程。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/baoyu-comic` |
| 版本 | `1.56.1` |
| 作者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `comic`, `knowledge-comic`, `creative`, `image-generation` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是当该技能被触发时 Hermes 加载的完整技能定义。即技能激活时 Agent 看到的指令。
:::

<a id="knowledge-comic-creator"></a>
# 知识漫画创作者

改编自 [baoyu-comic](https://github.com/JimLiu/baoyu-skills)，适用于 Hermes Agent 的工具生态系统。

通过灵活的美术风格 × 基调组合，创作原创知识漫画。

<a id="when-to-use"></a>
## 何时使用

当用户要求创作知识/教育漫画、传记漫画、教程漫画，或使用“知识漫画”“教育漫画”“Logicomix 风格”等词语时，触发此技能。用户提供内容（文本、文件路径、URL 或主题），并可选地指定美术风格、基调、布局、宽高比或语言。

<a id="reference-images"></a>
## 参考图片

Hermes 的 `image_generate` 工具**仅接受文本提示**——它接收文本提示和宽高比，返回图片 URL。它**不接受**参考图片。当用户提供参考图片时，请使用它**提取文本形式的特征**，并嵌入到每个分页提示中：

**接收**：当用户提供文件路径时接受（或在对话中粘贴图片）。
- 文件路径 → 复制到 `refs/NN-ref-{slug}.{ext}`（与漫画输出放在一起，用于溯源）
- 粘贴的图片但没有路径 → 通过 `clarify` 询问用户路径，或者以文本形式口头提取风格特征（作为文本后备方案）
- 无参考 → 跳过此部分

**使用模式**（每个参考图片）：

| 使用模式 | 效果 |
|-------|--------|
| `style` | 提取风格特征（线条处理、纹理、氛围）并附加到每个分页提示正文 |
| `palette` | 提取十六进制颜色并附加到每个分页提示正文 |
| `scene` | 提取场景构图或主体说明并附加到相关分页 |

**当存在参考时**，在每个分页提示的前置元数据中记录：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-scene.png
    usage: style
    traits: "柔和的土色调、边缘柔和的墨染、低对比度背景"
```

角色一致性由 `characters/characters.md`（在步骤 3 中编写）中的**文本描述**驱动，这些描述会内联嵌入到每个分页提示中（步骤 5）。步骤 7.1 中生成的可选 PNG 角色表是供人审查的制品，而非 `image_generate` 的输入。

<a id="options"></a>
## 选项

<a id="visual-dimensions"></a>
### 视觉维度

| 选项 | 值 | 描述 |
|--------|--------|-------------|
| 美术风格 | ligne-claire（默认）、manga（漫画）、realistic（写实）、ink-brush（水墨）、chalk（粉笔）、minimalist（极简） | 美术风格/渲染技法 |
| 基调 | neutral（默认）、warm（温暖）、dramatic（戏剧）、romantic（浪漫）、energetic（活力）、vintage（复古）、action（动作） | 氛围/情绪 |
| 布局 | standard（默认）、cinematic（电影感）、dense（密集）、splash（跨页）、mixed（混合）、webtoon（条漫）、four-panel（四格） | 画面排列方式 |
| 宽高比 | 3:4（默认，竖版）、4:3（横版）、16:9（宽屏） | 页面宽高比 |
| 语言 | auto（默认）、zh（中文）、en（英文）、ja（日文）等 | 输出语言 |
| 参考图片 | 文件路径 | 用于提取风格/色调特征的参考图片（不会传递给图像模型）。请参见上方的[参考图片](#reference-images)。 |
<a id="partial-workflow-options"></a>
### 部分工作流选项

| 选项 | 说明 |
|--------|-------------|
| 仅分镜 | 仅生成分镜，跳过提示词和图片 |
| 仅提示词 | 生成分镜 + 提示词，跳过图片 |
| 仅图片 | 从已有提示词目录生成图片 |
| 重新生成 N | 仅重新生成指定页面（例如 `3` 或 `2,5,8`） |

详情：[references/partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/partial-workflows.md)

<a id="art-tone-preset-catalogue"></a>
### 艺术风格、基调与预设目录

- **艺术风格**（6种）：`ligne-claire`、`manga`、`realistic`、`ink-brush`、`chalk`、`minimalist`。完整定义见 `references/art-styles/&lt;style&gt;.md`。
- **基调**（7种）：`neutral`、`warm`、`dramatic`、`romantic`、`energetic`、`vintage`、`action`。完整定义见 `references/tones/&lt;tone&gt;.md`。
- **预设**（5种），具有超越纯艺术+基调的特殊规则：

  | 预设 | 等价组合 | 特色 |
  |--------|-----------|------|
  | `ohmsha` | manga + neutral | 视觉隐喻，无对话头像，设备揭秘 |
  | `wuxia` | ink-brush + action | 气功特效，战斗画面，氛围感 |
  | `shoujo` | manga + romantic | 装饰元素，眼部细节，浪漫节拍 |
  | `concept-story` | manga + warm | 视觉符号系统，成长弧线，对话与动作平衡 |
  | `four-panel` | minimalist + neutral + 四格布局 | 起承转合结构，黑白+点缀色，火柴人角色 |

  完整规则见 `references/presets/&lt;preset&gt;.md` — 选择预设时加载该文件。

- **兼容性矩阵**和**内容信号→预设**对照表位于 [references/auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/auto-selection.md)。在步骤 2 中推荐组合前请先阅读。

<a id="file-structure"></a>
## 文件结构

输出目录：`comic/{topic-slug}/`
- 短横线命名：从主题提取 2-4 个单词的短横线格式（例如 `alan-turing-bio`）
- 冲突处理：追加时间戳（例如 `turing-story-20260118-143052`）

**内容**：
| 文件 | 说明 |
|------|-------------|
| `source-{slug}.md` | 保存的源内容（短横线命名与输出目录一致） |
| `analysis.md` | 内容分析 |
| `storyboard.md` | 分镜及面板分解 |
| `characters/characters.md` | 角色定义 |
| `characters/characters.png` | 角色参考图（从 `image_generate` 下载） |
| `prompts/NN-{cover\|page}-[slug].md` | 生成提示词 |
| `NN-{cover\|page}-[slug].png` | 生成的图片（从 `image_generate` 下载） |
| `refs/NN-ref-{slug}.{ext}` | 用户提供的参考图片（可选，用于溯源） |

<a id="language-handling"></a>
## 语言处理

**检测优先级**：
1. 用户指定的语言（显式选项）
2. 用户的对话语言
3. 源内容语言

**规则**：所有交互均使用用户的输入语言：
- 分镜大纲和场景描述
- 图片生成提示词
- 用户选择选项和确认
- 进度更新、问题、错误、总结
Technical terms remain in English.

<a id="workflow"></a>
## 工作流程

<a id="progress-checklist"></a>
### 进度检查清单

```
漫画进度：
- [ ] 第 1 步：设置与分析
  - [ ] 1.1 分析内容
  - [ ] 1.2 检查已有目录
- [ ] 第 2 步：确认——风格与选项 ⚠️ 必选
- [ ] 第 3 步：生成分镜头脚本 + 角色
- [ ] 第 4 步：审查大纲（按需）
- [ ] 第 5 步：生成提示词
- [ ] 第 6 步：审查提示词（按需）
- [ ] 第 7 步：生成图片
  - [ ] 7.1 生成角色设定页（如需要）→ characters/characters.png
  - [ ] 7.2 生成页面（提示词中嵌入角色描述）
- [ ] 第 8 步：完成报告
```

<a id="flow"></a>
### 流程

```
输入 → 分析 → [检查已有?] → [确认：风格 + 审查] → 分镜头脚本 → [审查?] → 提示词 → [审查?] → 图片 → 完成
```

<a id="step-summary"></a>
### 步骤摘要

| 步骤 | 动作 | 关键输出 |
|------|------|----------|
| 1.1 | 分析内容 | `analysis.md`, `source-{slug}.md` |
| 1.2 | 检查已有目录 | 处理冲突 |
| 2 | 确认风格、重点、受众、审查 | 用户偏好 |
| 3 | 生成分镜头脚本 + 角色 | `storyboard.md`, `characters/` |
| 4 | 审查大纲（如要求） | 用户批准 |
| 5 | 生成提示词 | `prompts/*.md` |
| 6 | 审查提示词（如要求） | 用户批准 |
| 7.1 | 生成角色设定页（如需要） | `characters/characters.png` |
| 7.2 | 生成页面 | `*.png` 文件 |
| 8 | 完成报告 | 摘要 |

<a id="user-questions"></a>
### 用户问题

使用 `clarify` 工具确认选项。由于 `clarify` 一次只处理一个问题，请先询问最重要的问题，然后依次进行。完整的第 2 步问题集请参阅 [references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/workflow.md)。

**超时处理（关键）**：`clarify` 可能返回 `"The user did not provide a response within the time limit. Use your best judgement to make the choice and proceed."` —— 这**不代表**用户同意全部采用默认值。

- 仅将该超时视为 **针对当前这一个问题的默认行为**。继续依次询问剩下的 Step 2 问题；每个问题都是独立的同意点。
- **在下一条消息中向用户明确展示这个默认值**，以便用户有机会纠正：例如 `"风格：默认使用 ohmsha 预设（clarify 超时）。如需切换请随时告知。"` —— 未报告的默认值和从未询问过没有区别。
- 不要在一次超时后就将 Step 2 合并成一个“全部采用默认值”的步骤。如果用户真的是暂时缺席，那么五个问题他都会缺席——但他回来后可以纠正可见的默认值，而不可见的默认值则无法纠正。

<a id="step-7-image-generation"></a>
### 第 7 步：图片生成

使用 Hermes 内置的 `image_generate` 工具进行所有图片渲染。其 schema 只接受 `prompt` 和 `aspect_ratio`（`landscape` | `portrait` | `square`）；它 **返回一个 URL**，而不是本地文件。因此，每个生成的页面或角色设定页都必须下载到输出目录中。
**Prompt 文件要求（硬性）**：在调用 `image_generate` 之前，将每张图片的完整最终 Prompt 写入 `prompts/` 下的独立文件（命名格式：`NN-{type}-[slug].md`）。Prompt 文件是复现性记录。

**宽高比映射** — 故事板的 `aspect_ratio` 字段映射到 `image_generate` 的 `format` 如下：

| 故事板比例 | `image_generate` 格式 |
|------------------|-------------------------|
| `3:4`, `9:16`, `2:3` | `portrait` |
| `4:3`, `16:9`, `3:2` | `landscape` |
| `1:1` | `square` |

**下载步骤** — 每次 `image_generate` 调用后：
1. 从工具结果中读取 URL
2. 使用**绝对**输出路径获取图片字节，例如：
   `curl -fsSL "&lt;url&gt;" -o /abs/path/to/comic/&lt;slug&gt;/NN-page-&lt;slug&gt;.png`
3. 在继续下一页之前，验证该文件在该确切路径上存在且非空

**切勿依赖 shell CWD 持久性来定义 `-o` 路径。** 终端工具的持久 shell CWD 可能在批次之间发生变化（会话过期、`TERMINAL_LIFETIME_SECONDS`、失败的 `cd` 导致你留在错误目录）。`curl -o relative/path.png` 是一个无声的陷阱：如果 CWD 发生了偏移，文件会落到其他地方而没有任何错误。**始终向 `-o` 传递完全限定的绝对路径**，或者向终端工具传递 `workdir=<绝对路径>`。2026年4月事故：一个10页漫画的第06-09页落在了仓库根目录而不是 `comic/&lt;slug&gt;/` 下，因为第3批次从第2批次继承了过时的 CWD，并且 `curl -o 06-page-skills.png` 写到了错误的目录。随后 Agent 浪费了几个回合声称文件存在，但实际上它们并不存在。

**7.1 角色设定表** — 当漫画是多页且有重复角色时，生成它（保存为 `characters/characters.png`，宽高比为 `landscape`）。对于简单的预设（例如，四格极简风格）或单页漫画则跳过。在调用 `image_generate` 之前，必须存在 `characters/characters.md` 的 Prompt 文件。渲染的 PNG 是**供人工审阅的产物**（以便用户直观验证角色设计），也是后续重新生成或手动 Prompt 编辑的参考——它**不**驱动步骤 7.2。页面 Prompt 已经在步骤 5 中根据 `characters/characters.md` 中的**文本描述**编写完成；`image_generate` 不能接受图片作为视觉输入。

**7.2 页面** — 在调用 `image_generate` 之前，每个页面的 Prompt 必须已经存在于 `prompts/NN-{cover|page}-[slug].md`。因为 `image_generate` 只接受 Prompt，角色一致性是通过**在步骤 5 中将角色描述（来自 `characters/characters.md`）嵌入到每个页面 Prompt 中**来实现的。无论是否在 7.1 生成了 PNG 表，都会统一进行嵌入；PNG 仅作为审阅/重新生成的辅助工具。

**备份规则**：现有的 `prompts/…md` 和 `…png` 文件 → 在重新生成之前，使用 `-backup-YYYYMMDD-HHMMSS` 后缀重命名。

完整的逐步工作流程（分析、故事板、审阅关卡、重新生成变体）：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/workflow.md)。
<a id="references"></a>
## 参考资料

**核心模板**：
- [analysis-framework.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/analysis-framework.md) - 深度内容分析
- [character-template.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/character-template.md) - 角色定义格式
- [storyboard-template.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/storyboard-template.md) - 分镜结构
- [ohmsha-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/ohmsha-guide.md) - Ohmsha 漫画专用指南

**风格定义**：
- `references/art-styles/` - 美术风格（线条清晰、漫画、写实、水墨、粉笔、极简）
- `references/tones/` - 色调（中性、温暖、戏剧、浪漫、活力、复古、动作）
- `references/presets/` - 预设（含特殊规则：ohmsha、武侠、少女、概念故事、四格）
- `references/layouts/` - 布局（标准、电影感、密集、满版、混合、网漫、四格）

**工作流**：
- [workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/workflow.md) - 完整工作流详情
- [auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/auto-selection.md) - 内容信号分析
- [partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/partial-workflows.md) - 部分工作流选项

<a id="page-modification"></a>
## 页面修改

| 操作 | 步骤 |
|--------|-------|
| **编辑** | **先更新提示文件** → 重新生成图片 → 下载新 PNG |
| **添加** | 在指定位置创建提示 → 使用嵌入的角色描述生成 → 对后续页面重新编号 → 更新分镜 |
| **删除** | 删除文件 → 对后续页面重新编号 → 更新分镜 |

**重要**：更新页面时，务必**先**更新提示文件（`prompts/NN-{cover|page}-[slug].md`），然后再重新生成。这样可以确保修改有记录且可复现。

<a id="pitfalls"></a>
## 常见陷阱

- 图片生成：每页 10-30 秒；失败时自动重试一次
- **务必下载** `image_generate` 返回的 URL 到本地 PNG 文件——下游工具（以及用户审查）期望输出目录中存在文件，而非临时 URL
- **使用绝对路径配合 `curl -o`**——切勿依赖持久化 shell 的当前工作目录跨批次保持有效。这是一个无声的陷阱：文件会落到错误目录，导致后续对目标路径的 `ls` 显示为空。参见第 7 步“下载步骤”
- 对敏感公众人物使用风格化替代方案
- **第 2 步需要确认**——不可跳过
- **第 4/6 步为条件性操作**——仅在用户在第 2 步提出要求时才执行
- **第 7.1 步角色表**——多页漫画推荐使用，简单预设可选。PNG 是辅助审查/重新生成的工具；页面提示（第 5 步编写）使用 `characters/characters.md` 中的文本描述，而非 PNG。`image_generate` 不接受图片作为视觉输入
- **清除机密信息**——在写入任何输出文件之前，扫描源内容中是否有 API 密钥、令牌或凭证
