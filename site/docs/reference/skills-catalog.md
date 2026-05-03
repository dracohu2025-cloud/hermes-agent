---
sidebar_position: 5
title: "内置技能目录"
description: "Hermes Agent 附带的内置技能目录"
---

# 内置技能目录 {#bundled-skills-catalog}

Hermes 附带了一个庞大的内置技能库，安装时会复制到 `~/.hermes/skills/` 目录下。下面的每个技能都链接到对应的专用页面，其中包含完整的定义、设置和使用说明。

如果某个技能在此列表中缺失但存在于仓库中，则目录由 `website/scripts/generate-skill-docs.py` 重新生成。

## apple {#apple}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`apple-notes`](/user-guide/skills/bundled/apple/apple-apple-notes) | 通过 memo CLI 管理 Apple Notes：创建、搜索、编辑。 | `apple/apple-notes` |
| [`apple-reminders`](/user-guide/skills/bundled/apple/apple-apple-reminders) | 通过 remindctl 管理 Apple Reminders：添加、列出、完成。 | `apple/reminders` |
| [`findmy`](/user-guide/skills/bundled/apple/apple-findmy) | 通过 macOS 上的 FindMy.app 追踪 Apple 设备/AirTags。 | `apple/findmy` |
| [`imessage`](/user-guide/skills/bundled/apple/apple-imessage) | 通过 macOS 上的 imsg CLI 发送和接收 iMessages/SMS。 | `apple/imessage` |

## autonomous-ai-agents {#autonomous-ai-agents}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`claude-code`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code) | 将编码任务委托给 Claude Code CLI（功能、PR）。 | `autonomous-ai-agents/claude-code` |
| [`codex`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex) | 将编码任务委托给 OpenAI Codex CLI（功能、PR）。 | `autonomous-ai-agents/codex` |
| [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) | 配置、扩展或贡献 Hermes Agent。 | `autonomous-ai-agents/hermes-agent` |
| [`opencode`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) | 将编码任务委托给 OpenCode CLI（功能、PR 审查）。 | `autonomous-ai-agents/opencode` |

## creative {#creative}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`architecture-diagram`](/user-guide/skills/bundled/creative/creative-architecture-diagram) | 深色主题的 SVG 架构/云/基础设施图，以 HTML 形式呈现。 | `creative/architecture-diagram` |
| [`ascii-art`](/user-guide/skills/bundled/creative/creative-ascii-art) | ASCII 艺术：pyfiglet、cowsay、boxes、图片转 ASCII。 | `creative/ascii-art` |
| [`ascii-video`](/user-guide/skills/bundled/creative/creative-ascii-video) | ASCII 视频：将视频/音频转换为彩色 ASCII MP4/GIF。 | `creative/ascii-video` |
| [`baoyu-comic`](/user-guide/skills/bundled/creative/creative-baoyu-comic) | 知识漫画：教育、传记、教程。 | `creative/baoyu-comic` |
| [`baoyu-infographic`](/user-guide/skills/bundled/creative/creative-baoyu-infographic) | 信息图：21 种布局 × 21 种风格。 | `creative/baoyu-infographic` |
| [`claude-design`](/user-guide/skills/bundled/creative/creative-claude-design) | 设计一次性 HTML 作品（落地页、演示文稿、原型）。 | `creative/claude-design` |
| [`comfyui`](/user-guide/skills/bundled/creative/creative-comfyui) | 使用 ComfyUI 生成图像、视频和音频——安装、启动、管理节点/模型、运行带参数注入的工作流。使用官方 comfy-cli 进行生命周期管理，并通过直接 REST/WebSocket API 执行。 | `creative/comfyui` |
| [`ideation`](/user-guide/skills/bundled/creative/creative-creative-ideation) | 通过创意约束生成项目想法。 | `creative/creative-ideation` |
| [`design-md`](/user-guide/skills/bundled/creative/creative-design-md) | 编写/验证/导出 Google 的 DESIGN.md 令牌规范文件。 | `creative/design-md` |
| [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw) | 手绘风格的 Excalidraw JSON 图表（架构图、流程图、时序图）。 | `creative/excalidraw` |
| [`humanizer`](/user-guide/skills/bundled/creative/creative-humanizer) | 人性化文本：去除 AI 痕迹，增添真实语气。 | `creative/humanizer` |
| [`manim-video`](/user-guide/skills/bundled/creative/creative-manim-video) | Manim CE 动画：3Blue1Brown 风格的数学/算法视频。 | `creative/manim-video` |
| [`p5js`](/user-guide/skills/bundled/creative/creative-p5js) | p5.js 草图：生成艺术、着色器、交互式、3D。 | `creative/p5js` |
| [`pixel-art`](/user-guide/skills/bundled/creative/creative-pixel-art) | 使用复古调色板（NES、Game Boy、PICO-8）的像素艺术。 | `creative/pixel-art` |
| [`popular-web-designs`](/user-guide/skills/bundled/creative/creative-popular-web-designs) | 54 个真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS 实现。 | `creative/popular-web-designs` |
| [`pretext`](/user-guide/skills/bundled/creative/creative-pretext) | 当使用 @chenglou/pretext 构建创意浏览器演示时使用——无 DOM 的文本布局，用于 ASCII 艺术、绕障碍物的排版流、文本即几何的游戏、动态排版以及文本驱动的生成艺术。生成单文件 HT... | `creative/pretext` |
| [`sketch`](/user-guide/skills/bundled/creative/creative-sketch) | 一次性 HTML 模型：2-3 个设计变体供比较。 | `creative/sketch` |
| [`songwriting-and-ai-music`](/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music) | 歌曲创作技巧和 Suno AI 音乐提示。 | `creative/songwriting-and-ai-music` |
| [`touchdesigner-mcp`](/user-guide/skills/bundled/creative/creative-touchdesigner-mcp) | 通过 twozero MCP 控制正在运行的 TouchDesigner 实例——创建算子、设置参数、连接节点、执行 Python、构建实时视觉效果。包含 36 个原生工具。 | `creative/touchdesigner-mcp` |
## data-science {#data-science}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`jupyter-live-kernel`](/user-guide/skills/bundled/data-science/data-science-jupyter-live-kernel) | 通过实时 Jupyter 内核（hamelnb）进行迭代式 Python 开发。 | `data-science/jupyter-live-kernel` |

## devops {#devops}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`kanban-orchestrator`](/user-guide/skills/bundled/devops/devops-kanban-orchestrator) | 分解剧本 + 专家名册约定 + 针对通过看板路由工作的编排器配置文件的防诱惑规则。“不要自己做”规则和基本生命周期会自动注入到每个看板工作... | `devops/kanban-orchestrator` |
| [`kanban-worker`](/user-guide/skills/bundled/devops/devops-kanban-worker) | Hermes Kanban 工作者的陷阱、示例和边界情况。生命周期本身会作为 KANBAN_GUIDANCE（来自 agent/prompt_builder.py）自动注入到每个工作者的系统提示中；当你需要更深入的细节时，可以加载此技能... | `devops/kanban-worker` |
| [`webhook-subscriptions`](/user-guide/skills/bundled/devops/devops-webhook-subscriptions) | Webhook 订阅：事件驱动的 Agent 运行。 | `devops/webhook-subscriptions` |

## dogfood {#dogfood}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`dogfood`](/user-guide/skills/bundled/dogfood/dogfood-dogfood) | Web 应用的探索性 QA：查找 Bug、证据、报告。 | `dogfood` |

## email {#email}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`himalaya`](/user-guide/skills/bundled/email/email-himalaya) | Himalaya CLI：从终端使用 IMAP/SMTP 电子邮件。 | `email/himalaya` |

## gaming {#gaming}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`minecraft-modpack-server`](/user-guide/skills/bundled/gaming/gaming-minecraft-modpack-server) | 托管模组版 Minecraft 服务器（CurseForge、Modrinth）。 | `gaming/minecraft-modpack-server` |
| [`pokemon-player`](/user-guide/skills/bundled/gaming/gaming-pokemon-player) | 通过无头模拟器 + RAM 读取玩宝可梦。 | `gaming/pokemon-player` |

## github {#github}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`codebase-inspection`](/user-guide/skills/bundled/github/github-codebase-inspection) | 使用 pygount 检查代码库：代码行数、语言、比例。 | `github/codebase-inspection` |
| [`github-auth`](/user-guide/skills/bundled/github/github-github-auth) | GitHub 认证设置：HTTPS 令牌、SSH 密钥、gh CLI 登录。 | `github/github-auth` |
| [`github-code-review`](/user-guide/skills/bundled/github/github-github-code-review) | 审查 PR：通过 gh 或 REST 查看差异、内联评论。 | `github/github-code-review` |
| [`github-issues`](/user-guide/skills/bundled/github/github-github-issues) | 通过 gh 或 REST 创建、分类、标记、分配 GitHub Issue。 | `github/github-issues` |
| [`github-pr-workflow`](/user-guide/skills/bundled/github/github-github-pr-workflow) | GitHub PR 生命周期：分支、提交、打开、CI、合并。 | `github/github-pr-workflow` |
| [`github-repo-management`](/user-guide/skills/bundled/github/github-github-repo-management) | 克隆/创建/复刻仓库；管理远程仓库、发布。 | `github/github-repo-management` |
## mcp {#mcp}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`native-mcp`](/user-guide/skills/bundled/mcp/mcp-native-mcp) | MCP 客户端：连接服务器，注册工具（stdio/HTTP）。 | `mcp/native-mcp` |

## media {#media}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`gif-search`](/user-guide/skills/bundled/media/media-gif-search) | 通过 curl + jq 从 Tenor 搜索/下载 GIF。 | `media/gif-search` |
| [`heartmula`](/user-guide/skills/bundled/media/media-heartmula) | HeartMuLa：根据歌词和标签生成类似 Suno 的歌曲。 | `media/heartmula` |
| [`songsee`](/user-guide/skills/bundled/media/media-songsee) | 通过 CLI 获取音频频谱图/特征（mel、chroma、MFCC）。 | `media/songsee` |
| [`spotify`](/user-guide/skills/bundled/media/media-spotify) | Spotify：播放、搜索、排队、管理播放列表和设备。 | `media/spotify` |
| [`youtube-content`](/user-guide/skills/bundled/media/media-youtube-content) | 将 YouTube 转录内容转换为摘要、帖子、博客。 | `media/youtube-content` |

## mlops {#mlops}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`audiocraft-audio-generation`](/user-guide/skills/bundled/mlops/mlops-models-audiocraft) | AudioCraft：MusicGen 文本转音乐，AudioGen 文本转声音。 | `mlops/models/audiocraft` |
| [`axolotl`](/user-guide/skills/bundled/mlops/mlops-training-axolotl) | Axolotl：YAML 格式的 LLM 微调（LoRA、DPO、GRPO）。 | `mlops/training/axolotl` |
| [`dspy`](/user-guide/skills/bundled/mlops/mlops-research-dspy) | DSPy：声明式 LM 程序，自动优化提示，RAG。 | `mlops/research/dspy` |
| [`huggingface-hub`](/user-guide/skills/bundled/mlops/mlops-huggingface-hub) | HuggingFace hf CLI：搜索/下载/上传模型、数据集。 | `mlops/huggingface-hub` |
| [`llama-cpp`](/user-guide/skills/bundled/mlops/mlops-inference-llama-cpp) | llama.cpp 本地 GGUF 推理 + HF Hub 模型发现。 | `mlops/inference/llama-cpp` |
| [`evaluating-llms-harness`](/user-guide/skills/bundled/mlops/mlops-evaluation-lm-evaluation-harness) | lm-eval-harness：对 LLM 进行基准测试（MMLU、GSM8K 等）。 | `mlops/evaluation/lm-evaluation-harness` |
| [`obliteratus`](/user-guide/skills/bundled/mlops/mlops-inference-obliteratus) | OBLITERATUS：通过 diff-in-means 消除 LLM 的拒绝行为。 | `mlops/inference/obliteratus` |
| [`outlines`](/user-guide/skills/bundled/mlops/mlops-inference-outlines) | Outlines：结构化 JSON/regex/Pydantic 的 LLM 生成。 | `mlops/inference/outlines` |
| [`segment-anything-model`](/user-guide/skills/bundled/mlops/mlops-models-segment-anything) | SAM：通过点、框、掩码进行零样本图像分割。 | `mlops/models/segment-anything` |
| [`fine-tuning-with-trl`](/user-guide/skills/bundled/mlops/mlops-training-trl-fine-tuning) | TRL：用于 LLM RLHF 的 SFT、DPO、PPO、GRPO、奖励建模。 | `mlops/training/trl-fine-tuning` |
| [`unsloth`](/user-guide/skills/bundled/mlops/mlops-training-unsloth) | Unsloth：2-5 倍更快的 LoRA/QLoRA 微调，更少显存。 | `mlops/training/unsloth` |
| [`serving-llms-vllm`](/user-guide/skills/bundled/mlops/mlops-inference-vllm) | vLLM：高吞吐量 LLM 服务，OpenAI API，量化。 | `mlops/inference/vllm` |
| [`weights-and-biases`](/user-guide/skills/bundled/mlops/mlops-evaluation-weights-and-biases) | W&B：记录 ML 实验、超参数搜索、模型注册、仪表板。 | `mlops/evaluation/weights-and-biases` |
## note-taking {#note-taking}

| Skill | Description | Path |
|-------|-------------|------|
| [`obsidian`](/user-guide/skills/bundled/note-taking/note-taking-obsidian) | 在 Obsidian 仓库中读取、搜索和创建笔记。 | `note-taking/obsidian` |

## productivity {#productivity}

| Skill | Description | Path |
|-------|-------------|------|
| [`airtable`](/user-guide/skills/bundled/productivity/productivity-airtable) | 通过 curl 调用 Airtable REST API。支持记录的增删改查、过滤和更新插入。 | `productivity/airtable` |
| [`google-workspace`](/user-guide/skills/bundled/productivity/productivity-google-workspace) | 通过 gws CLI 或 Python 操作 Gmail、日历、云端硬盘、文档和表格。 | `productivity/google-workspace` |
| [`linear`](/user-guide/skills/bundled/productivity/productivity-linear) | Linear：通过 GraphQL + curl 管理问题、项目和团队。 | `productivity/linear` |
| [`maps`](/user-guide/skills/bundled/productivity/productivity-maps) | 通过 OpenStreetMap/OSRM 进行地理编码、查询兴趣点、路线和时区。 | `productivity/maps` |
| [`nano-pdf`](/user-guide/skills/bundled/productivity/productivity-nano-pdf) | 通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本、错别字和标题。 | `productivity/nano-pdf` |
| [`notion`](/user-guide/skills/bundled/productivity/productivity-notion) | 通过 curl 调用 Notion API：页面、数据库、块、搜索。 | `productivity/notion` |
| [`ocr-and-documents`](/user-guide/skills/bundled/productivity/productivity-ocr-and-documents) | 从 PDF/扫描件中提取文本（使用 pymupdf、marker-pdf）。 | `productivity/ocr-and-documents` |
| [`powerpoint`](/user-guide/skills/bundled/productivity/productivity-powerpoint) | 创建、读取、编辑 .pptx 演示文稿、幻灯片、备注和模板。 | `productivity/powerpoint` |

## red-teaming {#red-teaming}

| Skill | Description | Path |
|-------|-------------|------|
| [`godmode`](/user-guide/skills/bundled/red-teaming/red-teaming-godmode) | 越狱大语言模型：Parseltongue、GODMODE、ULTRAPLINIAN。 | `red-teaming/godmode` |

## research {#research}

| Skill | Description | Path |
|-------|-------------|------|
| [`arxiv`](/user-guide/skills/bundled/research/research-arxiv) | 按关键词、作者、类别或 ID 搜索 arXiv 论文。 | `research/arxiv` |
| [`blogwatcher`](/user-guide/skills/bundled/research/research-blogwatcher) | 通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源。 | `research/blogwatcher` |
| [`llm-wiki`](/user-guide/skills/bundled/research/research-llm-wiki) | Karpathy 的 LLM Wiki：构建/查询相互链接的 Markdown 知识库。 | `research/llm-wiki` |
| [`polymarket`](/user-guide/skills/bundled/research/research-polymarket) | 查询 Polymarket：市场、价格、订单簿、历史记录。 | `research/polymarket` |
| [`research-paper-writing`](/user-guide/skills/bundled/research/research-research-paper-writing) | 为 NeurIPS/ICML/ICLR 撰写机器学习论文：从设计到提交。 | `research/research-paper-writing` |

## smart-home {#smart-home}

| Skill | Description | Path |
|-------|-------------|------|
| [`openhue`](/user-guide/skills/bundled/smart-home/smart-home-openhue) | 通过 OpenHue CLI 控制飞利浦 Hue 灯、场景和房间。 | `smart-home/openhue` |
## social-media {#social-media}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`xurl`](/user-guide/skills/bundled/social-media/social-media-xurl) | 通过 xurl CLI 使用 X/Twitter：发帖、搜索、私信、媒体、v2 API。 | `social-media/xurl` |

## software-development {#software-development}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`debugging-hermes-tui-commands`](/user-guide/skills/bundled/software-development/software-development-debugging-hermes-tui-commands) | 调试 Hermes TUI 斜杠命令：Python、网关、Ink UI。 | `software-development/debugging-hermes-tui-commands` |
| [`hermes-agent-skill-authoring`](/user-guide/skills/bundled/software-development/software-development-hermes-agent-skill-authoring) | 编写仓库内 SKILL.md：frontmatter、验证器、结构。 | `software-development/hermes-agent-skill-authoring` |
| [`node-inspect-debugger`](/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger) | 通过 --inspect + Chrome DevTools 协议 CLI 调试 Node.js。 | `software-development/node-inspect-debugger` |
| [`plan`](/user-guide/skills/bundled/software-development/software-development-plan) | 计划模式：将 Markdown 计划写入 .hermes/plans/，不执行。 | `software-development/plan` |
| [`python-debugpy`](/user-guide/skills/bundled/software-development/software-development-python-debugpy) | 调试 Python：pdb REPL + debugpy 远程（DAP）。 | `software-development/python-debugpy` |
| [`requesting-code-review`](/user-guide/skills/bundled/software-development/software-development-requesting-code-review) | 提交前审查：安全扫描、质量门禁、自动修复。 | `software-development/requesting-code-review` |
| [`spike`](/user-guide/skills/bundled/software-development/software-development-spike) | 一次性实验，在构建前验证想法。 | `software-development/spike` |
| [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) | 通过 delegate_task subagents 执行计划（两阶段审查）。 | `software-development/subagent-driven-development` |
| [`systematic-debugging`](/user-guide/skills/bundled/software-development/software-development-systematic-debugging) | 四阶段根因调试：先理解 bug，再修复。 | `software-development/systematic-debugging` |
| [`test-driven-development`](/user-guide/skills/bundled/software-development/software-development-test-driven-development) | TDD：强制 RED-GREEN-REFACTOR，先写测试再写代码。 | `software-development/test-driven-development` |
| [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans) | 编写实现计划：小任务、路径、代码。 | `software-development/writing-plans` |

## yuanbao {#yuanbao}

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| [`yuanbao`](/user-guide/skills/bundled/yuanbao/yuanbao-yuanbao) | 元宝群组：@提及用户、查询信息/成员。 | `yuanbao` |
