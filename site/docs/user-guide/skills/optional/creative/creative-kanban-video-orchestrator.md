---
title: "Kanban 视频编排器 — 借助 Hermes Kanban 规划、搭建并监控多 Agent 视频制作流水线"
sidebar_label: "Kanban 视频编排器"
description: "借助 Hermes Kanban 规划、搭建并监控多 Agent 视频制作流水线"
---

{/* 此页面由网站脚本 generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="kanban-video-orchestrator"></a>
# Kanban 视频编排器

借助 Hermes Kanban 规划、搭建并监控多 Agent 视频制作流水线。当用户想要制作任何类型的视频时——包括剧情片、产品/营销视频、音乐视频、解说视频、ASCII/终端艺术、抽象/生成循环、漫画、3D 作品、实时/装置艺术——并且该工作适合拆解为专业化角色（编剧、设计师、动画师、渲染师、配音、剪辑师等），通过看板进行协调时，即可使用此技能。它会进行自适应的需求发现以圈定任务范围，针对所需风格设计合适的团队，生成用于创建 Hermes 配置文件及初始看板任务的设置脚本，然后在执行过程中进行监控，并在任务卡住或失败时进行干预。它会将各个场景路由到适合该节拍的 Hermes 渲染/音频/设计技能（`ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`blender-mcp`、`pixel-art`、`baoyu-comic`、`claude-design`、`excalidraw`、`songsee`、`heartmula` …），并在需要时借助外部 API 进行 TTS、图像生成和图像转视频。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/kanban-video-orchestrator` 安装 |
| 路径 | `optional-skills/creative/kanban-video-orchestrator` |
| 版本 | `1.0.0` |
| 作者 | ['SHL0MS', 'alt-glitch'] |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `video`, `kanban`, `multi-agent`, `orchestration`, `production-pipeline` |
| 相关技能 | [`kanban-orchestrator`](/user-guide/skills/bundled/devops/devops-kanban-orchestrator)、[`kanban-worker`](/user-guide/skills/bundled/devops/devops-kanban-worker)、[`ascii-video`](/user-guide/skills/bundled/creative/creative-ascii-video)、[`manim-video`](/user-guide/skills/bundled/creative/creative-manim-video)、[`p5js`](/user-guide/skills/bundled/creative/creative-p5js)、[`comfyui`](/user-guide/skills/bundled/creative/creative-comfyui)、[`touchdesigner-mcp`](/user-guide/skills/bundled/creative/creative-touchdesigner-mcp)、[`blender-mcp`](/user-guide/skills/optional/creative/creative-blender-mcp)、[`pixel-art`](/user-guide/skills/bundled/creative/creative-pixel-art)、[`ascii-art`](/user-guide/skills/bundled/creative/creative-ascii-art)、[`songwriting-and-ai-music`](/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music)、[`heartmula`](/user-guide/skills/bundled/media/media-heartmula)、[`songsee`](/user-guide/skills/bundled/media/media-songsee)、[`spotify`](/user-guide/skills/bundled/media/media-spotify)、[`youtube-content`](/user-guide/skills/bundled/media/media-youtube-content)、[`claude-design`](/user-guide/skills/bundled/creative/creative-claude-design)、[`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw)、[`architecture-diagram`](/user-guide/skills/bundled/creative/creative-architecture-diagram)、[`concept-diagrams`](/user-guide/skills/optional/creative/creative-concept-diagrams)、[`baoyu-comic`](/user-guide/skills/bundled/creative/creative-baoyu-comic)、[`baoyu-infographic`](/user-guide/skills/bundled/creative/creative-baoyu-infographic)、[`humanizer`](/user-guide/skills/bundled/creative/creative-humanizer)、[`gif-search`](/user-guide/skills/bundled/media/media-gif-search)、[`meme-generation`](/user-guide/skills/optional/creative/creative-meme-generation) |
<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是在该技能被触发时 Hermes 加载的完整技能定义。技能激活后，Agent 会将其作为指令来遵循。
:::

<a id="kanban-video-orchestrator"></a>
# Kanban Video Orchestrator

将任何视频需求——从 15 秒的产品预告片到 5 分钟的叙事短片、音乐视频，再到 ASCII 循环动画——封装到一个 Hermes Kanban 流水线中，该流水线会将工作分解给专门的 Agent 角色。

本技能 **不** 执行任何实际的渲染工作。它是一个元流水线，负责：

1. **界定范围** ——通过有针对性的探索来明确需求
2. **设计团队** ——根据风格确定合适的角色组合以及每个角色对应的工具
3. **生成设置脚本** ——创建 Hermes 角色配置、项目工作区以及初始的看板任务
4. **交接给导演角色** ——由该角色通过看板进行任务分解
5. **监控执行** ——在任务停滞或失败时协助干预

实际的渲染工作会在看板运行后，通过适配场景的现有技能和工具来完成——例如 `ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`blender-mcp`、`songwriting-and-ai-music`、`heartmula`、外部 API，或是纯 Python 配合 PIL 和 ffmpeg。

<a id="when-not-to-use-this-skill"></a>
## 何时不应使用此技能

- 视频是一个连续的程序化项目，不需要专家分工。直接写代码即可。
- 用户希望快速完成一次性转换（例如“把这个 mp4 转成 GIF”）——直接使用 ffmpeg。
- 输出是静态图片、GIF 或纯音频产物——请使用对应的专项技能（`ascii-art`、`gifs`、`meme-generation`、`songwriting-and-ai-music`）。
- 工作完全适合某个现有技能（例如纯 ASCII 视频——直接用 `ascii-video`）。

<a id="workflow"></a>
## 工作流

```
探索 → 简报 → 团队设计 → 搭建 → 执行 → 监控
```

<a id="step-1-discover-ask-the-right-questions"></a>
### 第一步 —— 探索（提出正确的问题）

探索过程是 **自适应的**：只询问实际需要的信息。始终从三个问题开始，以确定大致轮廓：

- **视频内容是什么？**（一句话简述）
- **时长多少？**（5-30秒预告片 / 30-90秒短片 / 90秒-3分钟讲解 / 3-10分钟影片 / 更长）
- **宽高比和目标平台？**（1:1 / 9:16 / 16:9；X、Instagram、YouTube、内部使用等）

根据回答，归类风格类别。风格决定了后续要问的问题。**不要一次性问完所有问题。** 每次问 2-4 个，听取回答后再继续。当用户隐晦地给出答案时，做出合理的假设。

完整的采集模式和各风格问题库请参阅：
**[references/intake.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/intake.md)**

<a id="step-2-brief"></a>
### 第二步 —— 简报

在掌握足够信息后，使用 `assets/brief.md.tmpl` 模板生成结构化的 `brief.md` 文件。阶段如下：

1. **概念** —— 一句话介绍 + 情感核心
2. **范围** —— 时长、宽高比、平台、截止日期
3. **风格** —— 视觉参考、品牌约束、基调
4. **场景** —— 逐节分解（时长、内容、目标工具）
5. **音频** —— 旁白 / 音乐 / 音效 / 静音（可根据场景分别指定）
6. **交付物** —— 文件格式、分辨率、可选的替代版本（竖版裁剪、GIF 等）
在设计团队之前，先将概要展示给用户确认。**概要是合同** —— 所有下游任务都以它为准。

<a id="step-3-team-design"></a>
### 第 3 步 —— 团队设计

从角色库中挑选适合该视频的角色原型。**组合，而非克隆**。大多数视频需要 4–7 个角色档案。导演始终在场；其余角色根据概要的实际需求来选。

关于角色库和按风格划分的团队组成，请参阅  
**[references/role-archetypes.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/role-archetypes.md)**。

关于角色映射到哪些 Hermes 技能和工具集，请参阅  
**[references/tool-matrix.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/tool-matrix.md)**。

<a id="step-4-setup"></a>
### 第 4 步 —— 环境搭建

生成一个安装脚本 (`setup.sh`) 并运行它。该脚本会：

1.  创建工作空间 (`~/projects/video-pipeline/&lt;slug&gt;/`)
2.  将提供的任何素材复制到 `taste/`、`audio/`、`assets/` 目录下
3.  通过 `hermes profile create --clone` 创建每个 Hermes 角色档案
4.  为每个档案写入 `SOUL.md`（个性 + 角色定义）
5.  配置档案 YAML（工具集、always_load 技能、当前工作目录）
6.  写入 `brief.md`、`TEAM.md` 和 `taste/` 目录下的内容
7.  触发初始的 `hermes kanban create` 任务，分配给导演

使用 `scripts/bootstrap_pipeline.py` 从概要 + 团队设计 JSON 生成 setup.sh。关于安装脚本结构、角色配置模式以及关键的“共享工作空间”规则，请参阅 **[references/kanban-setup.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/kanban-setup.md)**。

<a id="step-5-execute"></a>
### 第 5 步 —— 执行

运行 `setup.sh`。然后向用户提供监控命令：

```bash
hermes kanban watch --tenant <project-tenant>     # 实时事件
hermes kanban list  --tenant <project-tenant>     # 看板快照
hermes dashboard                                   # 可视化看板界面
```

导演角色负责从这里接手，分解工作任务并通过看板工具集将任务路由给专业角色。

<a id="step-6-monitor-and-intervene"></a>
### 第 6 步 —— 监控与干预

保持参与 —— 看板会自动运行，但遇到卡住的任务或不良输出时，需要人类（或 AI）的判断。

监控模式：定期轮询 `kanban list`，用 `kanban show &lt;id&gt;` 检查任何运行时间超过预期时长的 RUNNING 任务，并检查心跳。当某个工人的输出未通过审查时，标准干预措施包括：

1.  在工人的任务上添加具体反馈评论（`kanban_comment`）
2.  创建一个重做任务，将原任务作为父任务
3.  调整概要的范围，让导演重新分解任务

关于诊断模式、干预方法以及“任务卡住”的应对方案，请参阅 **[references/monitoring.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/monitoring.md)**。

<a id="reference-worked-examples"></a>
## 参考：实际示例
六个具体的流水线示例覆盖了风格截然不同的视频类型——叙事电影、产品/营销、音乐视频、数学/算法讲解、ASCII 视频、实时装置——展示了相同的工作流程如何产生截然不同的团队和任务图。请参阅 **[references/examples.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/examples.md)**。

<a id="critical-rules"></a>
## 关键规则

1. **先探索，后行动。** 在未至少提出三个基线问题之前，绝不开始生成简报或组建团队。一份糟糕的简报会像多米诺骨牌一样影响整个流水线。

2. **团队与视频类型匹配。** 不要为每个任务复用同一套 4 人配置。一个没有节拍分析配置的音乐视频会运行失调。一个没有编剧配置的叙事电影会产生不连贯的场景。请参阅 `references/role-archetypes.md`。

3. **每个项目一个工作区。** 同一条视频的所有配置共享同一个 `dir:` 工作区。任务通过共享文件系统和结构化交接传递产物。**每一次** `kanban_create` 调用都必须传递 `workspace_kind="dir"` + `workspace_path="<绝对项目路径>"`。

4. **每个项目租户隔离。** 使用项目特定的租户（`--tenant <项目slug>`）。保持仪表盘范围隔离，防止与其他正在进行的 kanban 交叉污染。

5. **尊重已有技能。** 当某个场景适用于已有的技能时，相关渲染器应通过在其任务上使用 `--skill <名称>` 或在配置中使用 `always_load` 来加载该技能。不要重新推导某个技能已经提供的内容。

6. **导演绝不亲自动手。** 即使拥有完整的 `kanban + terminal + file` 工具集，导演的 `SOUL.md` 规则也禁止它自己执行工作。它只负责分解和路由——每一个具体的任务都变成对专家配置的一次 `hermes kanban create` 调用。`kanban-orchestrator` 技能对此做了进一步说明。

7. **不要过度分解。** 一段 30 秒的产品视频**不需要** 20 个任务。力求最小的任务图，同时仍能很好地并行化并暴露正确的人工审核关卡。

8. **在开火前验证 API 密钥。** 外部 API（TTS、图像生成、图像转视频）需要在 `~/.hermes/.env` 或用户的密钥存储中有密钥。一个因缺少密钥而出错的 worker 会浪费一个任务槽位。设置脚本中的 `check_key` 帮助函数会在缺少必需密钥时干净地中止。

<a id="file-map"></a>
## 文件映射

```
SKILL.md                            ← 本文件（工作流程 + 规则）
references/
  intake.md                         ← 按风格分类的发现问答库
  role-archetypes.md                ← 角色库（编剧、设计师、动画师……）
  tool-matrix.md                    ← 按角色划分的技能 + 工具集映射
  kanban-setup.md                   ← 设置脚本结构与配置配置
  monitoring.md                     ← 观察 + 干预模式
  examples.md                       ← 六个已完成的流水线示例
assets/
  brief.md.tmpl                     ← 简报模板
  setup.sh.tmpl                     ← 设置脚本模板
  soul.md.tmpl                      ← 配置个性模板
scripts/
  bootstrap_pipeline.py             ← 从简报 + 团队 JSON 生成 setup.sh
  monitor.py                        ← 轮询 + 干预帮助函数
```
