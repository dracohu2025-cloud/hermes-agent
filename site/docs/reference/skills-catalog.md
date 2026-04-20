---
sidebar_position: 5
title: "捆绑技能目录"
description: "Hermes Agent 随附的捆绑技能目录"
---

<a id="bundled-skills-catalog"></a>
# 捆绑技能目录

Hermes 附带一个大型内置技能库，在安装时会复制到 `~/.hermes/skills/` 目录下。本页列出了存在于 `skills/` 仓库中的捆绑技能。

<a id="apple"></a>
## apple

针对 Apple/macOS 的技能 —— iMessage、Reminders、Notes、FindMy 和 macOS 自动化。这些技能仅在 macOS 系统上加载。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `apple-notes` | 在 macOS 上通过 memo CLI 管理 Apple Notes（创建、查看、搜索、编辑）。 | `apple/apple-notes` |
| `apple-reminders` | 在 macOS 上通过 remindctl CLI 管理 Apple Reminders（列出、添加、完成、删除）。 | `apple/apple-reminders` |
| `findmy` | 在 macOS 上使用 AppleScript 和屏幕截图通过 FindMy.app 追踪 Apple 设备和 AirTags。 | `apple/findmy` |
| `imessage` | 在 macOS 上通过 imsg CLI 发送和接收 iMessages/SMS。 | `apple/imessage` |

<a id="autonomous-ai-agents"></a>
## autonomous-ai-agents

用于启动和编排自主 AI 编码 Agent 和多 Agent 工作流的技能 —— 运行独立的 Agent 进程、委派任务和协调并行工作流。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `claude-code` | 将编码任务委派给 Claude Code（Anthropic 的 CLI Agent）。用于构建功能、重构、PR 审查和迭代式编码。需要安装 claude CLI。 | `autonomous-ai-agents/claude-code` |
| `codex` | 将编码任务委派给 OpenAI Codex CLI Agent。用于构建功能、重构、PR 审查和批量修复问题。需要 codex CLI 和一个 git 仓库。 | `autonomous-ai-agents/codex` |
| `hermes-agent` | 关于使用和扩展 Hermes Agent 的完整指南 —— CLI 使用、设置、配置、启动额外 Agent、网关平台、技能、语音、工具、配置文件以及一份简洁的贡献者参考。在帮助用户配置 Hermes、排查问题、...时加载此技能。 | `autonomous-ai-agents/hermes-agent` |
| `opencode` | 将编码任务委派给 OpenCode CLI Agent，用于功能实现、重构、PR 审查和长时间运行的自主会话。需要安装并认证 opencode CLI。 | `autonomous-ai-agents/opencode` |

<a id="creative"></a>
## creative

创意内容生成 —— ASCII 艺术、手绘图表、动画、音乐和视觉设计工具。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `architecture-diagram` | 生成暗色调风格的软件系统和云基础设施 SVG 图表，作为独立的 HTML 文件，包含内联 SVG 图形。语义化组件颜色（cyan=前端，emerald=后端，violet=数据库，amber=云/AWS，rose=安全，orange=消息总线），JetBrains Mono 字体... | `creative/architecture-diagram` |
| `ascii-art` | 使用 pyfiglet（571 种字体）、cowsay、boxes、toilet、image-to-ascii、远程 API（asciified，ascii.co.uk）以及 LLM 后备方案生成 ASCII 艺术。无需 API 密钥。 | `creative/ascii-art` |
| `ascii-video` | ASCII 艺术视频的生产流水线 —— 支持任何格式。将视频/音频/图像/生成输入转换为彩色 ASCII 字符视频输出（MP4、GIF、图像序列）。涵盖：视频到 ASCII 转换、音频响应式音乐可视化工具、生成式 ASCII 艺术动画、混合... | `creative/ascii-video` |
| `excalidraw` | 使用 Excalidraw JSON 格式创建手绘风格图表。生成 .excalidraw 文件用于架构图、流程图、序列图、概念图等。文件可在 excalidraw.com 打开或上传以获得可共享链接。 | `creative/excalidraw` |
| `ideation` | 通过创意约束生成项目想法。当用户说"我想构建点什么"，"给我一个项目点子"，"我很无聊"，"我应该做什么"，"启发我"，或者任何"我有工具但没有方向"的变体时使用。适用于代码、艺术、硬件、写作、工具... | `creative/creative-ideation` |
| `manim-video` | 使用 Manim Community Edition 制作数学和技术动画的生产流水线。创建 3Blue1Brown 风格的讲解视频、算法可视化、方程推导、架构图和数据故事。当用户请求：动画解释、数学...时使用。 | `creative/manim-video` |
| `p5js` | 使用 p5.js 制作交互式和生成式视觉艺术的生产流水线。创建基于浏览器的草图、生成艺术、数据可视化、交互体验、3D 场景、音频响应式视觉和动态图形 —— 导出为 HTML、PNG、GIF、MP4 或 SVG。涵盖：2D... | `creative/p5js` |
| `popular-web-designs` | 从真实网站提取的 54 个生产级设计系统。加载模板以生成与 Stripe、Linear、Vercel、Notion、Airbnb 等网站视觉标识匹配的 HTML/CSS。每个模板包括颜色、字体、组件、布局规则和真... | `creative/popular-web-designs` |
| `songwriting-and-ai-music` | 歌曲创作技巧、AI 音乐生成提示（以 Suno 为重点）、模仿/改编技术、语音技巧和经验教训。这些都是工具和想法，不是规则。当艺术需要时，可以打破任何一条。 | `creative/songwriting-and-ai-music` |
<a id="data-science"></a>
## data-science

用于数据科学工作流的技能——交互式探索、Jupyter 笔记本、数据分析和可视化。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `jupyter-live-kernel` | 通过 hamelnb 使用实时 Jupyter 内核进行有状态的、迭代式的 Python 执行。当任务涉及探索、迭代或检查中间结果时加载此技能——例如数据科学、机器学习实验、API 探索或逐步构建复杂代码。使用… | `data-science/jupyter-live-kernel` |

<a id="devops"></a>
## devops

DevOps 和基础设施自动化技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `webhook-subscriptions` | 为事件驱动的 Agent 激活创建和管理 webhook 订阅。当用户希望外部服务自动触发 Agent 运行时使用。 | `devops/webhook-subscriptions` |

<a id="dogfood"></a>
## dogfood

用于测试 Hermes Agent 本身的内部自用和 QA 技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `dogfood` | 对 Web 应用程序进行系统性的探索性 QA 测试——发现错误、捕获证据并生成结构化报告 | `dogfood` |

<a id="email"></a>
## email

用于从终端发送、接收、搜索和管理电子邮件的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `himalaya` | 通过 IMAP/SMTP 管理电子邮件的 CLI。使用 himalaya 从终端列出、读取、撰写、回复、转发、搜索和组织电子邮件。支持多个账户和使用 MML（MIME 元语言）撰写消息。 | `email/himalaya` |

<a id="gaming"></a>
## gaming

用于设置、配置和管理游戏服务器、模组包以及游戏相关基础设施的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `minecraft-modpack-server` | 从 CurseForge/Modrinth 服务器包 zip 文件设置一个模组化的 Minecraft 服务器。涵盖 NeoForge/Forge 安装、Java 版本、JVM 调优、防火墙、局域网配置、备份和启动脚本。 | `gaming/minecraft-modpack-server` |
| `pokemon-player` | 通过无头模拟自动玩宝可梦游戏。启动游戏服务器，从 RAM 读取结构化游戏状态，做出策略决策，并发送按钮输入——全部在终端中完成。 | `gaming/pokemon-player` |

<a id="github"></a>
## github

用于管理仓库、拉取请求、代码审查、问题和 CI/CD 流水线的 GitHub 工作流技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `codebase-inspection` | 使用 pygount 检查和分析代码库，进行代码行数统计、语言细分以及代码与注释比例计算。当被要求检查代码行数、仓库大小、语言构成或代码库统计信息时使用。 | `github/codebase-inspection` |
| `github-auth` | 使用 git（普遍可用）或 gh CLI 为 Agent 设置 GitHub 身份验证。涵盖 HTTPS 令牌、SSH 密钥、凭据助手和 gh auth——带有一个检测流程来自动选择正确的方法。 | `github/github-auth` |
| `github-code-review` | 通过分析 git 差异、在 PR 上留下行内评论以及执行彻底的推送前审查来审查代码变更。可与 gh CLI 配合使用，或回退到通过 curl 使用 git + GitHub REST API。 | `github/github-code-review` |
| `github-issues` | 创建、管理、分类和关闭 GitHub 问题。搜索现有问题、添加标签、分配人员并链接到 PR。可与 gh CLI 配合使用，或回退到通过 curl 使用 git + GitHub REST API。 | `github/github-issues` |
| `github-pr-workflow` | 完整的拉取请求生命周期——创建分支、提交变更、打开 PR、监控 CI 状态、自动修复失败并合并。可与 gh CLI 配合使用，或回退到通过 curl 使用 git + GitHub REST API。 | `github/github-pr-workflow` |
| `github-repo-management` | 克隆、创建、分叉、配置和管理 GitHub 仓库。管理远程仓库、密钥、发布和工作流。可与 gh CLI 配合使用，或回退到通过 curl 使用 git + GitHub REST API。 | `github/github-repo-management` |
<a id="mcp"></a>
## mcp

用于处理 MCP（Model Context Protocol）服务器、工具和集成的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `native-mcp` | 内置的 MCP（Model Context Protocol）客户端，用于连接外部 MCP 服务器，发现其工具，并将它们注册为 Hermes Agent 的原生工具。支持 stdio 和 HTTP 传输，具备自动重连、安全过滤和零配置工具注入功能。 | `mcp/native-mcp` |

<a id="media"></a>
## media

用于处理媒体内容的技能 —— YouTube 字幕、GIF 搜索、音乐生成和音频可视化。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `gif-search` | 使用 curl 从 Tenor 搜索和下载 GIF。除了 curl 和 jq 外没有其他依赖。适用于寻找反应 GIF、创建视觉内容以及在聊天中发送 GIF。 | `media/gif-search` |
| `heartmula` | 设置并运行 HeartMuLa，这是一个开源的音乐生成模型系列（类似 Suno）。根据歌词和标签生成完整的歌曲，支持多语言。 | `media/heartmula` |
| `songsee` | 通过 CLI 从音频文件生成频谱图和音频特征可视化（梅尔频谱、色度、MFCC、节奏图等）。适用于音频分析、音乐制作调试和视觉文档记录。 | `media/songsee` |
| `youtube-content` | 获取 YouTube 视频字幕并将其转换为结构化内容（章节、摘要、线程、博客文章）。当用户分享 YouTube URL 或视频链接、要求总结视频、请求字幕或希望从任何 YouTube 视频中提取并重新格式化内容时使用。 | `media/youtube-content` |

<a id="mlops"></a>
## mlops

通用的 ML 运维工具 —— 模型中心管理、数据集操作和工作流编排。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `huggingface-hub` | Hugging Face Hub CLI (hf) —— 搜索、下载和上传模型与数据集，管理仓库，使用 SQL 查询数据集，部署推理端点，管理 Spaces 和存储桶。 | `mlops/huggingface-hub` |

<a id="mlops-evaluation"></a>
## mlops/evaluation

模型评估基准、实验跟踪和可解释性工具。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `evaluating-llms-harness` | 在 60 多个学术基准（MMLU、HumanEval、GSM8K、TruthfulQA、HellaSwag）上评估 LLM。适用于对模型质量进行基准测试、比较模型、报告学术结果或跟踪训练进度。这是 EleutherAI、HuggingFace 和主要实验室使用的行业标准。 | `mlops/evaluation/lm-evaluation-harness` |
| `weights-and-biases` | 使用自动日志记录跟踪 ML 实验，实时可视化训练过程，通过扫描优化超参数，并使用 W&B（一个协作式 MLOps 平台）管理模型注册表。 | `mlops/evaluation/weights-and-biases` |
## mlops/inference {#mlops-inference}

模型服务、量化（GGUF/GPTQ）、结构化输出、推理优化以及模型手术工具，用于部署和运行 LLM。

| Skill | Description | Path |
|-------|-------------|------|
| `llama-cpp` | 使用 llama.cpp 在 CPU、Apple Silicon、AMD/Intel GPU 或 NVIDIA 上运行 LLM 推理，外加 GGUF 模型转换和量化（2-8 位，支持 K-quants 和 imatrix）。涵盖 CLI、Python 绑定、OpenAI 兼容服务器以及 Ollama/LM Studio 集成。适用于边缘部署… | `mlops/inference/llama-cpp` |
| `obliteratus` | 使用 OBLITERATUS 移除开源权重 LLM 中的拒绝行为——这是一种基于机制可解释性技术（均值差分、SVD、白化 SVD、LEACE、SAE 分解等）的方法，可在保留推理能力的同时剔除护栏。提供 9 种 CLI 方法、28 个分析模块、116 个模型预设… | `mlops/inference/obliteratus` |
| `outlines` | 在生成过程中保证有效的 JSON/XML/代码结构，使用 Pydantic 模型实现类型安全的输出，支持本地模型（Transformers, vLLM），并通过 Outlines - dottxt.ai 的结构化生成库最大化推理速度 | `mlops/inference/outlines` |
| `serving-llms-vllm` | 使用 vLLM 的分页注意力（PagedAttention）和连续批处理技术，以高吞吐量服务 LLM。适用于部署生产级 LLM API、优化推理延迟/吞吐量，或在 GPU 内存有限的情况下服务模型。支持 OpenAI 兼容端点、量化（GPTQ/AWQ/FP8）… | `mlops/inference/vllm` |

<a id="mlops-models"></a>
## mlops/models

特定模型架构——图像分割（SAM）和音频生成（AudioCraft / MusicGen）。其他模型技能（CLIP、Stable Diffusion、Whisper、LLaVA）作为可选技能提供。

| Skill | Description | Path |
|-------|-------------|------|
| `audiocraft-audio-generation` | 用于音频生成的 PyTorch 库，包括文本到音乐（MusicGen）和文本到声音（AudioGen）。当你需要根据文本描述生成音乐、创建音效或进行旋律条件音乐生成时使用。 | `mlops/models/audiocraft` |
| `segment-anything-model` | 用于图像分割的基础模型，具有零样本迁移能力。当你需要使用点、框或掩码作为提示来分割图像中的任何对象，或自动生成图像中所有对象的掩码时使用。 | `mlops/models/segment-anything` |

<a id="mlops-research"></a>
## mlops/research

用于通过声明式编程构建和优化 AI 系统的 ML 研究框架。

| Skill | Description | Path |
|-------|-------------|------|
| `dspy` | 使用声明式编程构建复杂的 AI 系统，自动优化提示，创建模块化的 RAG 系统和 Agent——DSPy 是斯坦福 NLP 用于系统性语言模型编程的框架 | `mlops/research/dspy` |
<a id="mlops-training"></a>
## mlops/training

微调、RLHF/DPO/GRPO 训练、分布式训练框架和优化工具。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `axolotl` | 使用 Axolotl 微调 LLM 的专家指导 - YAML 配置、支持 100+ 模型、LoRA/QLoRA、DPO/KTO/ORPO/GRPO、多模态支持 | `mlops/training/axolotl` |
| `fine-tuning-with-trl` | 使用 TRL 通过强化学习微调 LLM - 用于指令调优的 SFT、用于偏好对齐的 DPO、用于奖励优化的 PPO/GRPO，以及奖励模型训练。当需要 RLHF、使模型与偏好对齐或从人类反馈中训练时使用。与 HuggingFace … 配合使用 | `mlops/training/trl-fine-tuning` |
| `unsloth` | 使用 Unsloth 进行快速微调的专家指导 - 训练速度提升 2-5 倍，内存占用减少 50-80%，LoRA/QLoRA 优化 | `mlops/training/unsloth` |

<a id="note-taking"></a>
## note-taking

笔记技能，用于保存信息、协助研究以及在多会话规划中进行协作。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `obsidian` | 在 Obsidian 知识库中读取、搜索和创建笔记。 | `note-taking/obsidian` |

<a id="productivity"></a>
## productivity

用于文档创建、演示文稿、电子表格和其他生产力工作流的技能。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `google-workspace` | Hermes 的 Gmail、日历、云端硬盘、联系人、表格和文档集成。使用 Hermes 管理的 OAuth2 设置，优先使用 Google Workspace CLI (`gws`) 以获得更广泛的 API 覆盖范围，否则回退到 Python 客户端库。 | `productivity/google-workspace` |
| `linear` | 通过 GraphQL API 管理 Linear 问题、项目和团队。创建、更新、搜索和组织问题。使用 API 密钥认证（无需 OAuth）。所有操作均通过 curl 进行 — 无依赖项。 | `productivity/linear` |
| `maps` | 位置智能 — 地理编码、反向地理编码、附近 POI 搜索（44 个类别，通过 `--near` 指定坐标或地址）、驾驶/步行/骑行距离 + 时间、逐向导航、时区、边界框 + 面积、矩形区域内的 POI 搜索。使用 OpenStreetMap + Overpass + OSRM。无需 API 密钥。支持 Telegram 位置图钉。 | `productivity/maps` |
| `nano-pdf` | 使用 nano-pdf CLI 通过自然语言指令编辑 PDF。修改文本、修复拼写错误、更新标题，并对特定页面进行内容更改，无需手动编辑。 | `productivity/nano-pdf` |
| `notion` | 用于通过 curl 创建和管理页面、数据库和块的 Notion API。直接从终端搜索、创建、更新和查询 Notion 工作区。 | `productivity/notion` |
| `ocr-and-documents` | 从 PDF 和扫描文档中提取文本。对远程 URL 使用 web_extract，对本地基于文本的 PDF 使用 pymupdf，对 OCR/扫描文档使用 marker-pdf。对于 DOCX 使用 python-docx，对于 PPTX 请参阅 powerpoint 技能。 | `productivity/ocr-and-documents` |
| `powerpoint` | 任何涉及 .pptx 文件的方式 — 作为输入、输出或两者 — 时，请使用此技能。这包括：创建幻灯片、演示文稿或推介材料；读取、解析或从任何 .pptx 文件中提取文本（即使提取的内容将用于其他地方，例如在 … | `productivity/powerpoint` |
<a id="red-teaming"></a>
## red-teaming

用于 LLM 红队测试、越狱和安全过滤器绕过研究的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `godmode` | 使用 G0DM0D3 技术越狱 API 服务的 LLM —— Parseltongue 输入混淆（33 种技术）、GODMODE CLASSIC 系统提示模板、ULTRAPLINIAN 多模型竞速、编码升级，以及 Hermes 原生的预填充/系统提示集成。当用户想要绕过…时使用。 | `red-teaming/godmode` |

<a id="research"></a>
## research

用于学术研究、论文发现、文献综述、市场数据、内容监控和科学知识检索的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `arxiv` | 使用其免费的 REST API 从 arXiv 搜索和检索学术论文。无需 API 密钥。可按关键词、作者、类别或 ID 搜索。与 web_extract 或 ocr-and-documents 技能结合以阅读完整论文内容。 | `research/arxiv` |
| `blogwatcher` | 使用 blogwatcher-cli 工具监控博客和 RSS/Atom 源的更新。添加博客、扫描新文章、跟踪阅读状态并按类别筛选。 | `research/blogwatcher` |
| `llm-wiki` | Karpathy 的 LLM Wiki —— 构建和维护一个持久化、相互链接的 Markdown 知识库。摄取来源、查询编译后的知识并进行一致性检查。 | `research/llm-wiki` |
| `polymarket` | 查询 Polymarket 预测市场数据 —— 搜索市场、获取价格、订单簿和价格历史。通过公共 REST API 只读访问，无需 API 密钥。 | `research/polymarket` |
| `research-paper-writing` | 用于撰写 ML/AI 研究论文的端到端流程 —— 从实验设计到分析、起草、修订和提交。涵盖 NeurIPS、ICML、ICLR、ACL、AAAI、COLM。集成了自动化实验监控、统计分析、迭代写作和引用验证… | `research/research-paper-writing` |

<a id="smart-home"></a>
## smart-home

用于控制智能家居设备 —— 灯光、开关、传感器和家庭自动化系统的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `openhue` | 通过 OpenHue CLI 控制飞利浦 Hue 灯光、房间和场景。开关灯、调整亮度、颜色、色温以及激活场景。 | `smart-home/openhue` |

<a id="social-media"></a>
## social-media

用于与社交平台交互 —— 发帖、阅读、监控和账户操作的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `xurl` | 通过 xurl（官方 X API CLI）与 X/Twitter 交互。用于发帖、回复、引用、搜索、时间线、提及、点赞、转发、书签、关注、私信、媒体上传和原始 v2 端点访问。 | `social-media/xurl` |
<a id="software-development"></a>
## software-development

通用软件工程技能 —— 规划、评审、调试和测试驱动开发。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `plan` | Hermes 的规划模式 —— 检查上下文，将 Markdown 计划写入当前工作区的 `.hermes/plans/` 目录，但不执行具体工作。 | `software-development/plan` |
| `requesting-code-review` | 预提交验证流水线 —— 静态安全扫描、基于基线的质量门禁、独立的评审子 Agent 以及自动修复循环。在代码变更后、提交、推送或开启 PR 前使用。 | `software-development/requesting-code-review` |
| `subagent-driven-development` | 在执行包含独立任务的实施计划时使用。为每个任务分派新的 `delegate_task`，并进行两阶段评审（先规范符合性，再代码质量）。 | `software-development/subagent-driven-development` |
| `systematic-debugging` | 在遇到任何错误、测试失败或意外行为时使用。四阶段根本原因调查 —— 在理解问题之前，不进行任何修复。 | `software-development/systematic-debugging` |
| `test-driven-development` | 在实现任何功能或修复错误时，在编写实现代码之前使用。强制执行 RED-GREEN-REFACTOR 循环，采用测试优先的方法。 | `software-development/test-driven-development` |
| `writing-plans` | 当你有一个多步骤任务的规范或需求时使用。创建包含可拆分任务、确切文件路径和完整代码示例的综合实施计划。 | `software-development/writing-plans` |


---

<a id="optional-skills"></a>
# 可选技能

可选技能随仓库提供，位于 `optional-skills/` 目录下，但**默认不激活**。它们涵盖较重或小众的用例。通过以下命令安装：

```bash
hermes skills install official/<category>/<skill>
```

<a id="autonomous-ai-agents"></a>
## autonomous-ai-agents

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `blackbox` | 将编码任务委托给 Blackbox AI CLI Agent。这是一个多模型 Agent，内置评判器，通过多个 LLM 运行任务并选取最佳结果。需要 blackbox CLI 和 Blackbox AI API 密钥。 | `autonomous-ai-agents/blackbox` |

<a id="blockchain"></a>
## blockchain

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `base` | 查询 Base（以太坊 L2）区块链数据，附带美元计价 —— 钱包余额、代币信息、交易详情、Gas 分析、合约检查、巨鲸检测和实时网络统计。使用 Base RPC + CoinGecko。无需 API 密钥。 | `blockchain/base` |
| `solana` | 查询 Solana 区块链数据，附带美元计价 —— 钱包余额、带估值的代币投资组合、交易详情、NFT、巨鲸检测和实时网络统计。使用 Solana RPC + CoinGecko。无需 API 密钥。 | `blockchain/solana` |
<a id="creative"></a>
## creative

| Skill | Description | Path |
|-------|-------------|------|
| `blender-mcp` | 通过 socket 连接 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python (bpy) 代码。 | `creative/blender-mcp` |
| `meme-generation` | 通过选择模板并使用 Pillow 叠加文本来生成真实的 meme 图片。生成实际的 .png meme 文件。 | `creative/meme-generation` |
| `touchdesigner-mcp` | 通过 twozero MCP 插件控制正在运行的 TouchDesigner 实例 — 创建操作器、设置参数、连接线路、执行 Python 代码，构建实时音频响应视觉效果和 GLSL 网络。包含 36 个原生工具。 | `creative/touchdesigner-mcp` |

<a id="devops"></a>
## devops

| Skill | Description | Path |
|-------|-------------|------|
| `docker-management` | 管理 Docker 容器、镜像、卷、网络和 Compose 堆栈 — 生命周期操作、调试、清理和 Dockerfile 优化。 | `devops/docker-management` |

<a id="email"></a>
## email

| Skill | Description | Path |
|-------|-------------|------|
| `agentmail` | 通过 AgentMail 为 Agent 提供其专属的电子邮件收件箱。使用 Agent 拥有的电子邮件地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理电子邮件。 | `email/agentmail` |

<a id="health"></a>
## health

| Skill | Description | Path |
|-------|-------------|------|
| `neuroskill-bci` | 连接到正在运行的 NeuroSkill 实例，并将用户的实时认知和情绪状态（专注度、放松度、情绪、认知负荷、困倦度、心率、心率变异性、睡眠分期以及 40 多种衍生的 EXG 评分）纳入响应中。需要 BCI 可穿戴设备（Muse 2/S 或 OpenBCI）和 NeuroSkill 桌面应用程序。 | `health/neuroskill-bci` |

<a id="mcp"></a>
## mcp

| Skill | Description | Path |
|-------|-------------|------|
| `fastmcp` | 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。适用于创建新的 MCP 服务器、将 API 或数据库包装为 MCP 工具、暴露资源或提示，或为 HTTP 部署准备 FastMCP 服务器。 | `mcp/fastmcp` |

<a id="migration"></a>
## migration

| Skill | Description | Path |
|-------|-------------|------|
| `openclaw-migration` | 将用户的 OpenClaw 自定义配置迁移到 Hermes Agent。从 ~/.openclaw 导入与 Hermes 兼容的记忆、SOUL.md、命令白名单、用户技能和选定的工作空间资产，然后报告无法迁移的内容及原因。 | `migration/openclaw-migration` |

<a id="productivity"></a>
## productivity

| Skill | Description | Path |
|-------|-------------|------|
| `telephony` | 为 Hermes 提供电话功能 — 配置并持久化一个 Twilio 号码，发送和接收短信/彩信，直接拨打电话，并通过 Bland.ai 或 Vapi 进行 AI 驱动的外呼。 | `productivity/telephony` |
<a id="research"></a>
## research

| Skill | Description | Path |
|-------|-------------|------|
| `bioinformatics` | 通往来自 bioSkills 和 ClawBio 的 400 多种生物信息学技能的网关。涵盖基因组学、转录组学、单细胞、变异检测、药物基因组学、宏基因组学、结构生物学等领域。 | `research/bioinformatics` |
| `qmd` | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录。qmd 是一个混合检索引擎，结合了 BM25、向量搜索和 LLM 重排序。支持 CLI 和 MCP 集成。 | `research/qmd` |

<a id="security"></a>
## security

| Skill | Description | Path |
|-------|-------------|------|
| `1password` | 设置和使用 1Password CLI (op)。适用于安装 CLI、启用桌面应用集成、登录以及为命令读取/注入密钥时。 | `security/1password` |
| `oss-forensics` | 针对 GitHub 仓库的供应链调查、证据恢复和取证分析。涵盖已删除提交的恢复、强制推送检测、IOC 提取、多源证据收集和结构化取证报告。 | `security/oss-forensics` |
| `sherlock` | 在 400 多个社交网络上进行 OSINT 用户名搜索。通过用户名追踪社交媒体账户。 | `security/sherlock` |
