---
title: "宝玉漫画 — 知识漫画：教育、传记、教程"
sidebar_label: "宝玉漫画"
description: "知识漫画：教育、传记、教程"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 宝玉漫画 {#baoyu-comic}

知识漫画：教育、传记、教程。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/baoyu-comic` |
| 版本 | `1.56.1` |
| 作者 | 宝玉 (JimLiu) |
| 许可证 | MIT |
| 标签 | `comic`, `knowledge-comic`, `creative`, `image-generation` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# 知识漫画创作者 {#knowledge-comic-creator}

改编自 [baoyu-comic](https://github.com/JimLiu/baoyu-skills)，适用于 Hermes Agent 的工具生态系统。

通过灵活的艺术风格 × 基调组合，创作原创知识漫画。

## 何时使用 {#when-to-use}

当用户要求创建知识/教育漫画、传记漫画、教程漫画，或使用“知识漫画”、“教育漫画”、“Logicomix 风格”等术语时，触发此技能。用户提供内容（文本、文件路径、URL 或主题），并可选择指定艺术风格、基调、布局、宽高比或语言。

## 参考图像 {#reference-images}

Hermes 的 `image_generate` 工具**仅支持提示词**——它接受文本提示和宽高比，并返回图像 URL。它**不**接受参考图像。当用户提供参考图像时，请使用它**以文本形式提取特征**，并将其嵌入每个页面的提示词中：

**接收**：当用户提供文件路径（或在对话中粘贴图像）时，接受文件路径。
- 文件路径 → 复制到 `refs/NN-ref-{slug}.{ext}`，与漫画输出一起保存以追溯来源
- 粘贴的图像但没有路径 → 通过 `clarify` 询问用户路径，或口头提取风格特征作为文本回退
- 无参考 → 跳过此部分

**使用模式**（每个参考）：

| 用法 | 效果 |
|------|------|
| `style` | 提取风格特征（线条处理、纹理、氛围）并附加到每个页面的提示词正文 |
| `palette` | 提取十六进制颜色并附加到每个页面的提示词正文 |
| `scene` | 提取场景构图或主题说明，并附加到相关页面 |

**当存在参考时，在每个页面的提示词 frontmatter 中记录**：

```yaml
references:
  - ref_id: 01
    filename: 01-ref-scene.png
    usage: style
    traits: "muted earth tones, soft-edged ink wash, low-contrast backgrounds"
```

角色一致性由 `characters/characters.md` 中的**文本描述**驱动（在第 3 步编写），这些描述会内联嵌入到每个页面提示词中（第 5 步）。第 7.1 步生成的可选 PNG 角色表是面向人工审阅的产物，而非 `image_generate` 的输入。

## 选项 {#options}

### 视觉维度 {#visual-dimensions}

| 选项 | 值 | 描述 |
|------|----|------|
| 艺术风格 | ligne-claire（默认）、manga、realistic、ink-brush、chalk、minimalist | 艺术风格/渲染技法 |
| 基调 | neutral（默认）、warm、dramatic、romantic、energetic、vintage、action | 情绪/氛围 |
| 布局 | standard（默认）、cinematic、dense、splash、mixed、webtoon、four-panel | 面板排列 |
| 宽高比 | 3:4（默认，竖屏）、4:3（横屏）、16:9（宽屏） | 页面宽高比 |
| 语言 | auto（默认）、zh、en、ja 等 | 输出语言 |
| 参考 | 文件路径 | 用于提取风格/调色板特征的参考图像（不会传递给图像模型）。请参见上面的[参考图像](#reference-images)。 |
### 部分工作流选项 {#partial-workflow-options}

| 选项 | 说明 |
|--------|-------------|
| 仅分镜 | 仅生成分镜，跳过提示词和图像 |
| 仅提示词 | 生成分镜 + 提示词，跳过图像 |
| 仅图像 | 从现有提示词目录生成图像 |
| 重新生成 N | 仅重新生成指定页面（例如 `3` 或 `2,5,8`） |

详情：[references/partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/partial-workflows.md)

### 艺术风格、基调与预设目录 {#art-tone-preset-catalogue}

- **艺术风格**（6种）：`ligne-claire`、`manga`、`realistic`、`ink-brush`、`chalk`、`minimalist`。完整定义见 `references/art-styles/&lt;style&gt;.md`。
- **基调**（7种）：`neutral`、`warm`、`dramatic`、`romantic`、`energetic`、`vintage`、`action`。完整定义见 `references/tones/&lt;tone&gt;.md`。
- **预设**（5种），具有超越纯艺术+基调的特殊规则：

  | 预设 | 等价组合 | 特色 |
  |--------|-----------|------|
  | `ohmsha` | manga + neutral | 视觉隐喻，无对话头像，设备展示 |
  | `wuxia` | ink-brush + action | 气功特效，战斗画面，氛围感 |
  | `shoujo` | manga + romantic | 装饰元素，眼部细节，浪漫节拍 |
  | `concept-story` | manga + warm | 视觉符号系统，成长弧线，对话与动作平衡 |
  | `four-panel` | minimalist + neutral + 四格布局 | 起承转合结构，黑白+点缀色，火柴人角色 |

  完整规则见 `references/presets/&lt;preset&gt;.md` — 选择预设时加载该文件。

- **兼容性矩阵**和**内容信号→预设**对照表位于 [references/auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/auto-selection.md)。在步骤2中推荐组合前请先阅读。

## 文件结构 {#file-structure}

输出目录：`comic/{topic-slug}/`
- 短横线命名：从主题中提取2-4个单词的短横线格式（例如 `alan-turing-bio`）
- 冲突处理：追加时间戳（例如 `turing-story-20260118-143052`）

**内容**：
| 文件 | 说明 |
|------|-------------|
| `source-{slug}.md` | 保存的源内容（短横线命名与输出目录一致） |
| `analysis.md` | 内容分析 |
| `storyboard.md` | 分镜（含面板分解） |
| `characters/characters.md` | 角色定义 |
| `characters/characters.png` | 角色参考图（从 `image_generate` 下载） |
| `prompts/NN-{cover\|page}-[slug].md` | 生成提示词 |
| `NN-{cover\|page}-[slug].png` | 生成的图像（从 `image_generate` 下载） |
| `refs/NN-ref-{slug}.{ext}` | 用户提供的参考图像（可选，用于溯源） |

## 语言处理 {#language-handling}

**检测优先级**：
1. 用户指定的语言（显式选项）
2. 用户的对话语言
3. 源内容语言

**规则**：所有交互均使用用户的输入语言：
- 分镜大纲和场景描述
- 图像生成提示词
- 用户选择选项和确认
- 进度更新、问题、错误、总结
技术术语保留英文。

## 工作流程 {#workflow}

### 进度清单 {#progress-checklist}

```
漫画进度：
- [ ] 步骤 1：设置与分析
  - [ ] 1.1 分析内容
  - [ ] 1.2 检查现有目录
- [ ] 步骤 2：确认 - 风格与选项 ⚠️ 必选
- [ ] 步骤 3：生成分镜 + 角色
- [ ] 步骤 4：审核大纲（按需）
- [ ] 步骤 5：生成提示词
- [ ] 步骤 6：审核提示词（按需）
- [ ] 步骤 7：生成图像
  - [ ] 7.1 生成角色表（如需）→ characters/characters.png
  - [ ] 7.2 生成页面（提示词中嵌入角色描述）
- [ ] 步骤 8：完成报告
```

### 流程 {#flow}

```
输入 → 分析 → [检查现有？] → [确认：风格 + 审核] → 分镜 → [审核？] → 提示词 → [审核？] → 图像 → 完成
```

### 步骤摘要 {#step-summary}

| 步骤 | 操作 | 关键输出 |
|------|------|----------|
| 1.1 | 分析内容 | `analysis.md`, `source-{slug}.md` |
| 1.2 | 检查现有目录 | 处理冲突 |
| 2 | 确认风格、重点、受众、审核 | 用户偏好 |
| 3 | 生成分镜 + 角色 | `storyboard.md`, `characters/` |
| 4 | 审核大纲（如要求） | 用户批准 |
| 5 | 生成提示词 | `prompts/*.md` |
| 6 | 审核提示词（如要求） | 用户批准 |
| 7.1 | 生成角色表（如需） | `characters/characters.png` |
| 7.2 | 生成页面 | `*.png` 文件 |
| 8 | 完成报告 | 摘要 |

### 用户提问 {#user-questions}

使用 `clarify` 工具确认选项。由于 `clarify` 一次只处理一个问题，请先问最重要的问题，然后依次进行。完整的步骤 2 问题集请参见 [references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/workflow.md)。

**超时处理（关键）**：`clarify` 可能返回 `"用户未在时限内提供响应。请根据你的最佳判断做出选择并继续。"` —— 这**不代表**用户同意所有默认选项。

- 将其视为**仅针对该问题**的默认选择。继续依次询问步骤 2 的其余问题；每个问题都是独立的同意点。
- **在下一条消息中向用户明确展示默认选择**，以便他们有机会纠正：例如 `"风格：默认使用 ohmsha 预设（clarify 超时）。如需切换请告知。"` —— 未报告的默认选择与从未询问过无异。
- 不要在单次超时后就将步骤 2 合并为一次“全部使用默认值”的通过。如果用户确实不在，他们同样不会回答所有五个问题——但他们回来后可以纠正可见的默认值，而无法纠正不可见的默认值。

### 步骤 7：图像生成 {#step-7-image-generation}

使用 Hermes 内置的 `image_generate` 工具进行所有图像渲染。其模式仅接受 `prompt` 和 `aspect_ratio`（`landscape` | `portrait` | `square`）；它**返回一个 URL**，而不是本地文件。因此，每个生成的页面或角色表都必须下载到输出目录。
**Prompt 文件要求（硬性）**：在调用 `image_generate` 之前，将每张图片的完整最终 prompt 写入 `prompts/` 下的独立文件（命名格式：`NN-{type}-[slug].md`）。prompt 文件是复现记录。

**宽高比映射** — 故事板的 `aspect_ratio` 字段映射到 `image_generate` 的 `format` 参数如下：

| 故事板比例 | `image_generate` 的 `format` |
|------------|------------------------------|
| `3:4`, `9:16`, `2:3` | `portrait` |
| `4:3`, `16:9`, `3:2` | `landscape` |
| `1:1` | `square` |

**下载步骤** — 每次调用 `image_generate` 后：
1. 从工具结果中读取 URL
2. 使用**绝对**输出路径获取图片字节，例如：
   `curl -fsSL "&lt;url&gt;" -o /abs/path/to/comic/&lt;slug&gt;/NN-page-&lt;slug&gt;.png`
3. 在继续下一页之前，验证该确切路径下文件存在且非空

**切勿依赖 shell CWD 持久性来指定 `-o` 路径。** 终端工具的持久 shell CWD 可能在批次之间发生变化（会话过期、`TERMINAL_LIFETIME_SECONDS`、失败的 `cd` 导致你留在错误目录）。`curl -o relative/path.png` 是一个无声的陷阱：如果 CWD 发生了漂移，文件会落到其他地方且不报错。**始终向 `-o` 传递完全限定的绝对路径**，或者向终端工具传递 `workdir=<绝对路径>`。2026 年 4 月事故：一个 10 页漫画的第 06-09 页落到了仓库根目录而不是 `comic/&lt;slug&gt;/` 下，因为第 3 批次继承了第 2 批次的过期 CWD，并且 `curl -o 06-page-skills.png` 写入了错误目录。随后 Agent 花费了好几轮声称文件存在，但实际上并不存在。

**7.1 角色表** — 当漫画是多页且包含重复角色时，生成角色表（到 `characters/characters.png`，宽高比 `landscape`）。对于简单预设（例如四格极简风格）或单页漫画，跳过此步骤。在调用 `image_generate` 之前，`characters/characters.md` 的 prompt 文件必须存在。渲染出的 PNG 是**面向人类的审查产物**（以便用户直观验证角色设计），也是后续重新生成或手动编辑 prompt 的参考——它**不**驱动步骤 7.2。页面 prompt 已经在步骤 5 中根据 `characters/characters.md` 中的**文本描述**编写完成；`image_generate` 不能接受图片作为视觉输入。

**7.2 页面** — 在调用 `image_generate` 之前，每个页面的 prompt 必须已经存在于 `prompts/NN-{cover|page}-[slug].md` 中。由于 `image_generate` 仅接受 prompt，角色一致性通过在步骤 5 中将角色描述（来自 `characters/characters.md`）**内联嵌入**到每个页面 prompt 中来保证。无论 7.1 中是否生成了 PNG 角色表，嵌入方式都是统一的；PNG 仅作为审查/重新生成的辅助工具。

**备份规则**：现有的 `prompts/…md` 和 `…png` 文件 → 在重新生成前，用 `-backup-YYYYMMDD-HHMMSS` 后缀重命名。

完整的分步工作流程（分析、故事板、审查关卡、重新生成变体）：[references/workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/workflow.md)。
## 参考资料 {#references}

**核心模板**：
- [analysis-framework.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/analysis-framework.md) — 深度内容分析
- [character-template.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/character-template.md) — 角色定义格式
- [storyboard-template.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/storyboard-template.md) — 分镜结构
- [ohmsha-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/ohmsha-guide.md) — Ohmsha 漫画细节

**风格定义**：
- `references/art-styles/` — 艺术风格（线条清晰、漫画、写实、水墨、粉笔、极简）
- `references/tones/` — 色调（中性、温暖、戏剧、浪漫、活力、复古、动作）
- `references/presets/` — 预设（含特殊规则：ohmsha、武侠、少女、概念故事、四格）
- `references/layouts/` — 布局（标准、电影感、密集、跨页、混合、条漫、四格）

**工作流程**：
- [workflow.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/workflow.md) — 完整工作流程细节
- [auto-selection.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/auto-selection.md) — 内容信号分析
- [partial-workflows.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/baoyu-comic/references/partial-workflows.md) — 部分工作流程选项

## 页面修改 {#page-modification}

| 操作 | 步骤 |
|--------|-------|
| **编辑** | **先更新提示文件** → 重新生成图像 → 下载新的 PNG |
| **添加** | 在指定位置创建提示 → 生成时嵌入角色描述 → 重新编号后续页面 → 更新分镜 |
| **删除** | 删除文件 → 重新编号后续页面 → 更新分镜 |

**重要**：更新页面时，务必**先**更新提示文件（`prompts/NN-{cover|page}-[slug].md`），然后再重新生成。这样可以确保更改被记录并可复现。

## 常见陷阱 {#pitfalls}

- 图像生成：每页 10-30 秒；失败后自动重试一次
- **务必下载** `image_generate` 返回的 URL 到本地 PNG 文件——下游工具（以及用户审查）期望输出目录中有文件，而不是临时 URL
- **对 `curl -o` 使用绝对路径**——不要依赖持久化 shell 的当前工作目录跨批次生效。无声陷阱：文件会落到错误目录，后续在预期路径上执行 `ls` 会显示为空。参见步骤 7“下载步骤”
- 对敏感公众人物使用风格化替代方案
- **步骤 2 需要确认**——不可跳过
- **步骤 4/6 为条件性**——仅当用户在步骤 2 中要求时才执行
- **步骤 7.1 角色表**——多页漫画推荐使用，简单预设可选。PNG 是审查/重新生成的辅助工具；页面提示（在步骤 5 中编写）使用 `characters/characters.md` 中的文本描述，而非 PNG。`image_generate` 不接受图像作为视觉输入
- **清除机密**——在写入任何输出文件之前，扫描源内容中的 API 密钥、令牌或凭据
