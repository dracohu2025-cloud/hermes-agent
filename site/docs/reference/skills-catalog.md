---
sidebar_position: 5
title: "内置 Skill 目录"
description: "Hermes Agent 随附的内置 Skill 目录"
---

# 内置 Skill 目录

Hermes 附带了一个庞大的内置 Skill 库，在安装时会复制到 `~/.hermes/skills/`。本页面列出了代码仓库中 `skills/` 目录下的内置 Skill。

## apple

Apple/macOS 专用 Skill —— 包含 iMessage、提醒事项、备忘录、查找（FindMy）以及 macOS 自动化。这些 Skill 仅在 macOS 系统上加载。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `apple-notes` | 在 macOS 上通过 memo CLI 管理 Apple Notes（创建、查看、搜索、编辑）。 | `apple/apple-notes` |
| `apple-reminders` | 通过 remindctl CLI 管理 Apple 提醒事项（列表、添加、完成、删除）。 | `apple/apple-reminders` |
| `findmy` | 在 macOS 上利用 AppleScript 和屏幕截图，通过“查找” App 追踪 Apple 设备和 AirTags。 | `apple/findmy` |
| `imessage` | 在 macOS 上通过 imsg CLI 发送和接收 iMessage/短信。 | `apple/imessage` |

## autonomous-ai-agents

用于生成和编排自主 AI 编程 Agent 以及多 Agent 工作流的 Skill —— 运行独立的 Agent 进程、委派任务并协调并行工作流。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `claude-code` | 将编程任务委派给 Claude Code（Anthropic 的 CLI Agent）。用于构建功能、重构、PR 审查和迭代编程。需要安装 claude CLI。 | `autonomous-ai-agents/claude-code` |
| `codex` | 将编程任务委派给 OpenAI Codex CLI Agent。用于构建功能、重构、PR 审查和批量修复 Issue。需要 codex CLI 和 git 仓库。 | `autonomous-ai-agents/codex` |
| `hermes-agent-spawning` | 生成额外的 Hermes Agent 实例作为自主子进程，用于处理独立的长期运行任务。支持非交互式单次模式 (-q) 和用于多轮协作的交互式 PTY 模式。与 delegate_task 不同 —— 这会运行一个完整的独立 hermes 进程。 | `autonomous-ai-agents/hermes-agent` |
| `opencode` | 将编程任务委派给 OpenCode CLI Agent，用于功能实现、重构、PR 审查和长期运行的自主会话。需要安装 OpenCode CLI 并完成认证。 | `autonomous-ai-agents/opencode` |

## data-science

用于数据科学工作流的 Skill —— 交互式探索、Jupyter notebook、数据分析和可视化。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `jupyter-live-kernel` | 通过 hamelnb 使用实时 Jupyter 内核进行有状态的、迭代式的 Python 执行。当任务涉及探索、迭代或检查中间结果时，请加载此 Skill。 | `data-science/jupyter-live-kernel` |

## creative

创意内容生成 —— ASCII 艺术、手绘风格图表和视觉设计工具。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `ascii-art` | 使用 pyfiglet（571 种字体）、cowsay、boxes、toilet、image-to-ascii、远程 API（asciified, ascii.co.uk）以及 LLM 兜底方案生成 ASCII 艺术。无需 API 密钥。 | `creative/ascii-art` |
| `ascii-video` | ASCII 艺术视频生产流水线 —— 支持任何格式。将视频/音频/图像/生成式输入转换为彩色 ASCII 字符视频输出（MP4、GIF、图像序列）。涵盖：视频转 ASCII、音频响应式音乐可视化、生成式 ASCII 艺术动画、混合模式等。 | `creative/ascii-video` |
| `excalidraw` | 使用 Excalidraw JSON 格式创建手绘风格图表。生成用于架构图、流程图、时序图、概念图等的 .excalidraw 文件。文件可在 excalidraw.com 打开或上传以获取分享链接。 | `creative/excalidraw` |
| `p5js` | 使用 p5.js 进行交互式和生成式视觉艺术的生产流水线。创建草图，通过无头浏览器将其渲染为图像/视频，并提供实时预览。支持画布动画、数据可视化和创意编程实验。 | `creative/p5js` |

## devops

DevOps 和基础设施自动化 Skill。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `webhook-subscriptions` | 创建和管理 Webhook 订阅，用于事件驱动的 Agent 激活。外部服务（GitHub、Stripe、CI/CD、IoT）通过 POST 事件触发 Agent 运行。需要启用 Webhook 平台。 | `devops/webhook-subscriptions` |

## dogfood

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `dogfood` | 对 Web 应用程序进行系统性的探索性 QA 测试 —— 发现 Bug、捕获证据并生成结构化报告。 | `dogfood/dogfood` |
| `hermes-agent-setup` | 帮助用户配置 Hermes Agent —— 包含 CLI 用法、设置向导、模型/供应商选择、工具、Skill、语音/STT/TTS、网关以及故障排除。 | `dogfood/hermes-agent-setup` |

## email

用于在终端发送、接收、搜索和管理电子邮件的 Skill。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `himalaya` | 通过 IMAP/SMTP 管理电子邮件的 CLI。使用 himalaya 在终端列出、阅读、编写、回复、转发、搜索和组织电子邮件。支持多账户和使用 MML (MIME Meta Language) 撰写邮件。 | `email/himalaya` |

## gaming

用于设置、配置和管理游戏服务器、模组包（modpacks）以及游戏相关基础设施的 Skill。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `minecraft-modpack-server` | 从 CurseForge/Modrinth 服务器包 zip 文件设置模组版 Minecraft 服务器。涵盖 NeoForge/Forge 安装、Java 版本、JVM 调优、防火墙、局域网配置、备份和启动脚本。 | `gaming/minecraft-modpack-server` |
| `pokemon-player` | 通过无头模拟器自主玩宝可梦游戏。启动游戏服务器，从 RAM 读取结构化游戏状态，做出战略决策并发送按键输入 —— 全部在终端完成。 | `gaming/pokemon-player` |

## github

GitHub 工作流 Skill，用于使用 gh CLI 和终端 git 管理仓库、拉取请求（PR）、代码审查、Issue 和 CI/CD 流水线。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `codebase-inspection` | 使用 pygount 检查和分析代码库，进行代码行数（LOC）统计、语言细分和代码与注释比例分析。当需要检查代码行数、仓库大小、语言组成或代码库统计数据时使用。 | `github/codebase-inspection` |
| `github-auth` | 使用 git（通用）或 gh CLI 为 Agent 设置 GitHub 身份验证。涵盖 HTTPS 令牌、SSH 密钥、凭据助手和 gh auth —— 具有自动选择正确方法的检测流程。 | `github/github-auth` |
| `github-code-review` | 通过分析 git diff 进行代码变更审查，在 PR 上留下行内评论，并执行彻底的推送前审查。支持 gh CLI，或回退到 git + 通过 curl 调用 GitHub REST API。 | `github/github-code-review` |
| `github-issues` | 创建、管理、分类和关闭 GitHub Issue。搜索现有 Issue、添加标签、指派人员并链接到 PR。支持 gh CLI，或回退到 git + 通过 curl 调用 GitHub REST API。 | `github/github-issues` |
| `github-pr-workflow` | 完整的拉取请求生命周期 —— 创建分支、提交变更、开启 PR、监控 CI 状态、自动修复失败项并合并。支持 gh CLI，或回退到 git + 通过 curl 调用 GitHub REST API。 | `github/github-pr-workflow` |
| `github-repo-management` | 克隆、创建、派生（fork）、配置和管理 GitHub 仓库。管理远程仓库、机密信息（secrets）、发布（releases）和工作流。支持 gh CLI，或回退到 git + 通过 curl 调用 GitHub REST API。 | `github/github-repo-management` |

## inference-sh

通过 inference.sh 云平台执行 AI 应用的 Skill。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `inference-sh-cli` | 通过 inference.sh CLI (infsh) 运行 150 多个 AI 应用 —— 包含图像生成、视频创建、LLM、搜索、3D、社交自动化。 | `inference-sh/cli` |

## leisure

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `find-nearby` | 使用 OpenStreetMap 查找附近地点（餐厅、咖啡馆、酒吧、药店等）。支持坐标、地址、城市、邮编或 Telegram 位置图钉。无需 API 密钥。 | `leisure/find-nearby` |
## mcp

用于处理 MCP (Model Context Protocol) 服务、工具和集成的技能。包括内置的原生 MCP 客户端（在 `config.yaml` 中配置服务器以实现自动工具发现）以及用于临时服务器交互的 `mcporter` CLI 桥接器。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `mcporter` | 使用 `mcporter` CLI 直接列出、配置、验证和调用 MCP 服务器/工具（通过 HTTP 或 stdio），包括临时服务器、配置编辑以及 CLI/类型生成。 | `mcp/mcporter` |
| `native-mcp` | 内置的 MCP (Model Context Protocol) 客户端，可连接到外部 MCP 服务器，发现其工具并将其注册为原生 Hermes Agent 工具。支持 stdio 和 HTTP 传输，具备自动重连、安全过滤和零配置工具注入功能。 | `mcp/native-mcp` |

## media

用于处理媒体内容的技能 —— 包括 YouTube 字幕提取、GIF 搜索、音乐生成和音频可视化。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `gif-search` | 使用 `curl` 从 Tenor 搜索并下载 GIF。除了 `curl` 和 `jq` 之外没有其他依赖。适用于寻找表情包 GIF、创建视觉内容以及在聊天中发送 GIF。 | `media/gif-search` |
| `heartmula` | 设置并运行 HeartMuLa，这是一个开源音乐生成模型家族（类似于 Suno）。支持多语言，可根据歌词 + 标签生成完整的歌曲。 | `media/heartmula` |
| `songsee` | 通过 CLI 从音频文件生成频谱图和音频特征可视化（mel、chroma、MFCC、tempogram 等）。适用于音频分析、音乐制作调试和视觉文档。 | `media/songsee` |
| `youtube-content` | 获取 YouTube 视频字幕并将其转换为结构化内容（章节、摘要、推文串、博客文章）。 | `media/youtube-content` |

## mlops

通用机器学习运维工具 —— 模型中心管理、数据集操作和工作流编排。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `huggingface-hub` | Hugging Face Hub CLI (hf) —— 搜索、下载和上传模型及数据集，管理仓库，部署推理端点。 | `mlops/huggingface-hub` |

## mlops/cloud

用于机器学习工作负载的 GPU 云提供商和无服务器计算平台。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `lambda-labs-gpu-cloud` | 用于机器学习训练和推理的预留及按需 GPU 云实例。当你需要具有简单 SSH 访问权限、持久文件系统或用于大规模训练的高性能多节点集群的专用 GPU 实例时使用。 | `mlops/cloud/lambda-labs` |
| `modal-serverless-gpu` | 用于运行机器学习工作负载的无服务器 GPU 云平台。当你需要无需基础设施管理的按需 GPU 访问、将机器学习模型部署为 API 或运行具有自动扩展功能的批处理作业时使用。 | `mlops/cloud/modal` |

## mlops/evaluation

模型评估基准、实验跟踪、数据整理、分词器（tokenizers）和可解释性工具。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `evaluating-llms-harness` | 在 60 多个学术基准（MMLU、HumanEval、GSM8K、TruthfulQA、HellaSwag）上评估 LLM。在衡量模型质量、对比模型、报告学术结果或跟踪训练进度时使用。这是 EleutherAI、HuggingFace 和各大实验室使用的行业标准。支持…… | `mlops/evaluation/lm-evaluation-harness` |
| `huggingface-tokenizers` | 为研究和生产优化的快速分词器。基于 Rust 的实现可在 20 秒内完成 1GB 数据的分词。支持 BPE、WordPiece 和 Unigram 算法。可训练自定义词汇表、跟踪对齐、处理填充/截断。与 `transformers` 无缝集成。使用…… | `mlops/evaluation/huggingface-tokenizers` |
| `nemo-curator` | 用于 LLM 训练的 GPU 加速数据整理工具。支持文本/图像/视频/音频。具有模糊去重（快 16 倍）、质量过滤（30 多种启发式方法）、语义去重、PII 脱敏、NSFW 检测等功能。可通过 RAPIDS 在多 GPU 间扩展。用于准备高质量的…… | `mlops/evaluation/nemo-curator` |
| `sparse-autoencoder-training` | 提供使用 SAELens 训练和分析稀疏自编码器 (SAE) 的指导，将神经网络激活分解为可解释的特征。在发现可解释特征、分析叠加（superposition）或研究语言模型中的单语义表示时使用。 | `mlops/evaluation/saelens` |
| `weights-and-biases` | 通过自动日志记录跟踪机器学习实验，实时可视化训练过程，通过 sweeps 优化超参数，并使用 W&B（协作式 MLOps 平台）管理模型注册表。 | `mlops/evaluation/weights-and-biases` |

## mlops/inference

模型服务、量化 (GGUF/GPTQ)、结构化输出、推理优化以及用于部署和运行 LLM 的模型手术工具。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `gguf-quantization` | GGUF 格式和 `llama.cpp` 量化，用于高效的 CPU/GPU 推理。在消费级硬件、Apple Silicon 上部署模型，或在没有 GPU 要求的情况下需要 2-8 bit 灵活量化时使用。 | `mlops/inference/gguf` |
| `guidance` | 使用正则表达式和语法控制 LLM 输出，保证生成有效的 JSON/XML/代码，强制执行结构化格式，并使用 Guidance（微软研究院的受限生成框架）构建多步骤工作流。 | `mlops/inference/guidance` |
| `instructor` | 通过 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，以类型安全的方式解析复杂的 JSON，并使用 Instructor（经过实战检验的结构化输出库）流式传输部分结果。 | `mlops/inference/instructor` |
| `llama-cpp` | 在没有 NVIDIA 硬件的情况下，在 CPU、Apple Silicon 和消费级 GPU 上运行 LLM 推理。用于边缘部署、M1/M2/M3 Mac、AMD/Intel GPU 或 CUDA 不可用时。支持 GGUF 量化（1.5-8 bit），相比 CPU 上的 PyTorch 可减少内存占用并提速 4-10 倍。 | `mlops/inference/llama-cpp` |
| `obliteratus` | 使用 OBLITERATUS 从开源权重 LLM 中移除拒绝行为 —— 采用机械可解释性技术（均值差、SVD、白化 SVD、LEACE、SAE 分解等）在保留推理能力的同时切除护栏。包含 9 种 CLI 方法、28 个分析模块、116 个模型预设…… | `mlops/inference/obliteratus` |
| `outlines` | 保证生成过程中有效的 JSON/XML/代码结构，使用 Pydantic 模型实现类型安全输出，支持本地模型（Transformers, vLLM），并使用 Outlines（dottxt.ai 的结构化生成库）最大化推理速度。 | `mlops/inference/outlines` |
| `serving-llms-vllm` | 使用 vLLM 的 PagedAttention 和连续批处理技术提供高吞吐量的 LLM 服务。在部署生产级 LLM API、优化推理延迟/吞吐量或在 GPU 显存有限的情况下提供模型服务时使用。支持 OpenAI 兼容端点、量化 (GPTQ/AWQ/FP8) 等。 | `mlops/inference/vllm` |
| `tensorrt-llm` | 使用 NVIDIA TensorRT 优化 LLM 推理，以获得最大吞吐量和最低延迟。用于 NVIDIA GPU (A100/H100) 上的生产部署，当你需要比 PyTorch 快 10-100 倍的推理速度，或需要通过量化 (FP8/INT4)、在途批处理（in-flight batching）和多……来提供模型服务时使用。 | `mlops/inference/tensorrt-llm` |

## mlops/models

特定的模型架构和工具 —— 计算机视觉 (CLIP, SAM, Stable Diffusion)、语音 (Whisper)、音频生成 (AudioCraft) 和多模态模型 (LLaVA)。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `audiocraft-audio-generation` | 用于音频生成的 PyTorch 库，包括文本转音乐 (MusicGen) 和文本转声音 (AudioGen)。当你需要根据文本描述生成音乐、创建音效或执行基于旋律引导的音乐生成时使用。 | `mlops/models/audiocraft` |
| `clip` | OpenAI 连接视觉和语言的模型。支持零样本图像分类、图文匹配和跨模态检索。在 4 亿对图文数据上训练而成。用于图像搜索、内容审核或无需微调的视觉语言任务。最适合通用目的…… | `mlops/models/clip` |
| `llava` | 大型语言与视觉助手（Large Language and Vision Assistant）。支持视觉指令微调和基于图像的对话。结合了 CLIP 视觉编码器与 Vicuna/LLaMA 语言模型。支持多轮图像对话、视觉问答和指令遵循。用于视觉语言对话…… | `mlops/models/llava` |
| `segment-anything-model` | 具有零样本迁移能力的图像分割基础模型。当你需要使用点、框或掩码作为提示来分割图像中的任何对象，或自动生成图像中所有对象的掩码时使用。 | `mlops/models/segment-anything` |
| `stable-diffusion-image-generation` | 通过 HuggingFace Diffusers 使用 Stable Diffusion 模型进行最先进的文本转图像生成。用于根据文本提示生成图像、执行图生图转换、局部重绘（inpainting）或构建自定义扩散流水线。 | `mlops/models/stable-diffusion` |
| `whisper` | OpenAI 的通用语音识别模型。支持 99 种语言、转录、翻译成英文以及语言识别。提供从 tiny (39M 参数) 到 large (1550M 参数) 的六种模型尺寸。用于语音转文本、播客转录或多语言音频处理…… | `mlops/models/whisper` |
## mlops/research

用于通过声明式编程构建和优化 AI 系统的 ML 研究框架。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `dspy` | 使用声明式编程构建复杂的 AI 系统，自动优化提示词（Prompt），利用 DSPy（斯坦福 NLP 推出的系统化 LM 编程框架）创建模块化 RAG 系统和 Agents | `mlops/research/dspy` |

## mlops/training

微调、RLHF/DPO/GRPO 训练、分布式训练框架，以及用于训练 LLM 和其他模型的优化工具。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `axolotl` | 使用 Axolotl 微调 LLM 的专家级指导——支持 YAML 配置、100 多种模型、LoRA/QLoRA、DPO/KTO/ORPO/GRPO 以及多模态支持 | `mlops/training/axolotl` |
| `distributed-llm-pretraining-torchtitan` | 提供使用 torchtitan 进行 PyTorch 原生分布式 LLM 预训练，支持 4D 并行（FSDP2、TP、PP、CP）。适用于在 8 到 512+ 个 GPU 规模上预训练 Llama 3.1、DeepSeek V3 或自定义模型，支持 Float8、torch.compile 和分布式检查点。 | `mlops/training/torchtitan` |
| `fine-tuning-with-trl` | 使用 TRL 通过强化学习微调 LLM——用于指令微调的 SFT、用于偏好对齐的 DPO、用于奖励优化的 PPO/GRPO 以及奖励模型训练。适用于需要 RLHF、使模型符合偏好或根据人类反馈进行训练的场景。兼容 HuggingFace Tr… | `mlops/training/trl-fine-tuning` |
| `grpo-rl-training` | 使用 TRL 进行 GRPO/RL 微调的专家级指导，用于推理和特定任务的模型训练 | `mlops/training/grpo-rl-training` |
| `hermes-atropos-environments` | 为 Atropos 训练构建、测试和调试 Hermes Agent RL 环境。涵盖 HermesAgentBaseEnv 接口、奖励函数、Agent loop 集成、工具评估、wandb 日志记录以及三种 CLI 模式（serve/process/evaluate）。适用于创建、审查或调… | `mlops/training/hermes-atropos-environments` |
| `huggingface-accelerate` | 最简单的分布式训练 API。只需 4 行代码即可为任何 PyTorch 脚本添加分布式支持。为 DeepSpeed/FSDP/Megatron/DDP 提供统一 API。支持自动设备分配、混合精度（FP16/BF16/FP8）。交互式配置，单条启动命令。HuggingFace 生态标准。 | `mlops/training/accelerate` |
| `optimizing-attention-flash` | 使用 Flash Attention 优化 Transformer 注意力机制，可实现 2-4 倍加速和 10-20 倍显存减少。适用于训练/运行长序列（>512 tokens）的 Transformer、遇到注意力机制导致的 GPU 显存问题或需要更快推理的场景。支持 PyTorch 原生 SDPA… | `mlops/training/flash-attention` |
| `peft-fine-tuning` | 使用 LoRA、QLoRA 等 25 种以上方法对 LLM 进行参数高效微调。适用于在 GPU 显存有限的情况下微调大模型（7B-70B）、需要以极小的精度损失训练 &lt;1% 参数的场景，或用于多适配器推理服务。HuggingFace 官方库… | `mlops/training/peft` |
| `pytorch-fsdp` | 使用 PyTorch FSDP 进行全参数分片数据并行训练的专家级指导——参数分片、混合精度、CPU 卸载、FSDP2 | `mlops/training/pytorch-fsdp` |
| `pytorch-lightning` | 高级 PyTorch 框架，包含 Trainer 类、自动分布式训练（DDP/FSDP/DeepSpeed）、回调系统和极简的样板代码。同一套代码可从笔记本电脑扩展到超级计算机。适用于希望拥有内置最佳实践的整洁训练循环的场景。 | `mlops/training/pytorch-lightning` |
| `simpo-training` | 用于 LLM 对齐的简单偏好优化（Simple Preference Optimization）。DPO 的无参考模型替代方案，性能更佳（AlpacaEval 2.0 提升 6.4 分）。无需参考模型，比 DPO 更高效。适用于追求比 DPO/PPO 更简单、更快速的偏好对齐训练。 | `mlops/training/simpo` |
| `slime-rl-training` | 提供使用 slime（一个 Megatron+SGLang 框架）进行 RL 后训练的指导。适用于训练 GLM 模型、实现自定义数据生成工作流，或在 RL 扩展中需要紧密的 Megatron-LM 集成的场景。 | `mlops/training/slime` |
| `unsloth` | 使用 Unsloth 进行快速微调的专家级指导——训练速度提升 2-5 倍，显存占用减少 50-80%，LoRA/QLoRA 优化 | `mlops/training/unsloth` |

## mlops/vector-databases

用于 RAG、语义搜索和 AI 应用后端的向量相似度搜索和嵌入数据库。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `chroma` | 面向 AI 应用的开源嵌入数据库。存储嵌入和元数据，执行向量和全文搜索，按元数据过滤。简单的 4 函数 API。可从笔记本电脑扩展到生产集群。用于语义搜索、RAG 应用或文档检索。最适合… | `mlops/vector-databases/chroma` |
| `faiss` | Facebook 开发的用于稠密向量高效相似度搜索和聚类的库。支持数十亿向量、GPU 加速和各种索引类型（Flat, IVF, HNSW）。用于快速 k-NN 搜索、大规模向量检索，或当你只需要纯粹的相似度搜索而不需要… | `mlops/vector-databases/faiss` |
| `pinecone` | 面向生产级 AI 应用的托管向量数据库。全托管、自动扩缩容，支持混合搜索（稠密 + 稀疏）、元数据过滤和命名空间。低延迟（&lt;100ms p95）。用于生产级 RAG、推荐系统或大规模语义搜索。最适合服务器… | `mlops/vector-databases/pinecone` |
| `qdrant-vector-search` | 用于 RAG 和语义搜索的高性能向量相似度搜索引擎。适用于构建需要快速最近邻搜索、带过滤的混合搜索或基于 Rust 性能的可扩展向量存储的生产级 RAG 系统。 | `mlops/vector-databases/qdrant` |

## note-taking

笔记技能，用于保存信息、辅助研究，以及在多会话规划和信息共享中进行协作。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `obsidian` | 在 Obsidian 库中读取、搜索和创建笔记。 | `note-taking/obsidian` |

## productivity

用于文档创建、演示文稿、电子表格和其他办公工作流的技能。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `google-workspace` | 通过 Python 集成 Gmail、日历、云端硬盘、联系人、表格和文档。使用 OAuth2 并支持自动令牌刷新。无需外部二进制文件——完全通过 Hermes 虚拟环境中的 Google Python 客户端库运行。 | `productivity/google-workspace` |
| `linear` | 通过 GraphQL API 管理 Linear 的议题（Issues）、项目和团队。创建、更新、搜索和组织议题。 | `productivity/linear` |
| `nano-pdf` | 使用 nano-pdf CLI 通过自然语言指令编辑 PDF。修改文本、修复拼写错误、更新标题，并对特定页面进行内容更改，无需手动编辑。 | `productivity/nano-pdf` |
| `notion` | 通过 curl 使用 Notion API 创建和管理页面、数据库和区块。直接从终端搜索、创建、更新和查询 Notion 工作区。 | `productivity/notion` |
| `ocr-and-documents` | 从 PDF 和扫描文档中提取文本。远程 URL 使用 web_extract，本地文本型 PDF 使用 pymupdf，扫描件/OCR 使用 marker-pdf。DOCX 使用 python-docx，PPTX 请参阅 powerpoint 技能。 | `productivity/ocr-and-documents` |
| `powerpoint` | 只要涉及 .pptx 文件（作为输入、输出或两者兼有），即可使用此技能。包括：创建幻灯片、路演包或演示文稿；从任何 .pptx 文件中读取、解析或提取文本（即使提取的内容将用于其他地方，如… | `productivity/powerpoint` |

## research

用于学术研究、论文发现、文献综述、领域侦察、市场数据、内容监控和科学知识检索的技能。

| Skill | 描述 | 路径 |
|-------|-------------|------|
| `arxiv` | 使用免费的 REST API 从 arXiv 搜索和检索学术论文。无需 API 密钥。按关键词、作者、类别或 ID 搜索。结合 web_extract 或 ocr-and-documents 技能可阅读论文全文。 | `research/arxiv` |
| `blogwatcher` | 使用 blogwatcher CLI 监控博客和 RSS/Atom 订阅源的更新。添加博客、扫描新文章并跟踪已读内容。 | `research/blogwatcher` |
| `llm-wiki` | Karpathy 的 LLM Wiki——构建并维护一个持久的、相互关联的 Markdown 知识库。摄取源数据、查询汇编的知识并进行一致性检查。与 RAG 不同，该 Wiki 一次性汇编知识并保持更新。可作为 Obsidian 库使用。可通过 `skills.config.wiki.path` 配置。 | `research/llm-wiki` |
| `domain-intel` | 使用 Python 标准库进行被动域名侦察。子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录、域名可用性检查以及批量多域名分析。无需 API 密钥。 | `research/domain-intel` |
| `duckduckgo-search` | 通过 DuckDuckGo 进行免费网页搜索——文本、新闻、图片、视频。无需 API 密钥。安装后优先使用 `ddgs` CLI；仅在确认当前运行时环境中可用时才使用 Python DDGS 库。 | `research/duckduckgo-search` |
| `ml-paper-writing` | 为 NeurIPS、ICML、ICLR、ACL、AAAI、COLM 撰写可发表的 ML/AI 论文。适用于根据研究仓库起草论文、构建论点、验证引用或准备最终提交稿。包含 LaTeX 模板、审稿人指南和引用验证… | `research/ml-paper-writing` |
| `polymarket` | 查询 Polymarket 预测市场数据——搜索市场、获取价格、订单簿和价格历史。通过公开 REST API 进行只读访问，无需 API 密钥。 | `research/polymarket` |
## red-teaming

用于 LLM 红队测试、越狱以及安全过滤器绕过研究的技能。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `godmode` | 使用 G0DM0D3 技术越狱通过 API 提供的 LLM —— 包括 Parseltongue 输入混淆（33 种技术）、GODMODE CLASSIC 系统提示词模板、ULTRAPLINIAN 多模型竞赛、编码升级以及 Hermes 原生 prefill/系统提示词集成。适用于任何可通过 API 访问的模型，包括闭源模型。 | `red-teaming/godmode` |

## smart-home

用于控制智能家居设备的技能 —— 灯光、开关、传感器和家庭自动化系统。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `openhue` | 通过 OpenHue CLI 控制 Philips Hue 灯光、房间和场景。开关灯光，调节亮度、颜色、色温，以及激活场景。 | `smart-home/openhue` |

## social-media

用于与社交平台交互的技能 —— 发布、阅读、监控和账号操作。

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `xitter` | 使用官方 X API 凭据，通过 x-cli 终端客户端与 X/Twitter 交互。 | `social-media/xitter` |

## software-development

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `code-review` | 执行侧重于安全和质量的彻底代码审查的指南。 | `software-development/code-review` |
| `plan` | Hermes 的计划模式 —— 检查上下文，在当前工作区/后端工作目录的 `.hermes/plans/` 中编写 markdown 计划，且不执行具体工作。 | `software-development/plan` |
| `requesting-code-review` | 在完成任务、实现重大功能或合并前使用。通过系统的审查流程验证工作是否符合要求。 | `software-development/requesting-code-review` |
| `subagent-driven-development` | 在执行包含独立任务的实施计划时使用。为每个任务分配全新的 delegate_task，并进行两阶段审查（先是规范合规性，然后是代码质量）。 | `software-development/subagent-driven-development` |
| `systematic-debugging` | 在遇到任何 bug、测试失败或意外行为时使用。进行 4 阶段根因调查 —— 在未完全理解问题前严禁修复。 | `software-development/systematic-debugging` |
| `test-driven-development` | 在编写实现代码之前，于实现任何功能或修复 bug 时使用。通过测试先行的方法强制执行“红-绿-重构”循环。 | `software-development/test-driven-development` |
| `writing-plans` | 当你拥有多步任务的规范或需求时使用。创建包含细分任务、准确文件路径和完整代码示例的全面实施计划。 | `software-development/writing-plans` |

---

# 可选技能 (Optional Skills)

可选技能随仓库附带在 `optional-skills/` 目录下，但**默认不激活**。它们涵盖了更重型或小众的使用场景。使用以下命令安装：

```bash
hermes skills install official/<category>/<skill>
```

## autonomous-ai-agents

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `blackbox` | 将编程任务委托给 Blackbox AI CLI Agent。这是一个内置裁判的多模型 Agent，它会在多个 LLM 上运行任务并挑选最佳结果。需要 blackbox CLI 和 Blackbox AI API 密钥。 | `autonomous-ai-agents/blackbox` |

## blockchain

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `base` | 查询带有美元计价的 Base (Ethereum L2) 区块链数据 —— 钱包余额、代币信息、交易详情、Gas 分析、合约检查、巨鲸检测和实时网络统计。使用 Base RPC + CoinGecko。无需 API 密钥。 | `blockchain/base` |
| `solana` | 查询带有美元计价的 Solana 区块链数据 —— 钱包余额、带价值的代币组合、交易详情、NFT、巨鲸检测和实时网络统计。使用 Solana RPC + CoinGecko。无需 API 密钥。 | `blockchain/solana` |

## creative

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `blender-mcp` | 通过 socket 连接到 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python (bpy) 代码。 | `creative/blender-mcp` |
| `meme-generation` | 通过选择模板并使用 Pillow 叠加文字来生成真实的表情包图片。生成实际的 .png 表情包文件。 | `creative/meme-generation` |

## devops

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `docker-management` | 管理 Docker 容器、镜像、数据卷、网络和 Compose 栈 —— 包括生命周期操作、调试、清理和 Dockerfile 优化。 | `devops/docker-management` |

## email

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `agentmail` | 通过 AgentMail 为 Agent 提供其专用的电子邮箱。使用 Agent 拥有的邮箱地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理电子邮件。 | `email/agentmail` |

## health

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `neuroskill-bci` | 连接到运行中的 NeuroSkill 实例，并将用户的实时认知和情感状态（专注度、放松度、情绪、认知负荷、困倦度、心率、HRV、睡眠分期以及 40 多项派生的 EXG 评分）整合到回复中。需要 BCI 可穿戴设备（Muse 2/S 或 OpenBCI）和 NeuroSkill 桌面应用。 | `health/neuroskill-bci` |

## mcp

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `fastmcp` | 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。在创建新的 MCP 服务器、将 API 或数据库包装为 MCP 工具、公开资源或提示词，或准备将 FastMCP 服务器进行 HTTP 部署时使用。 | `mcp/fastmcp` |

## migration

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `openclaw-migration` | 将用户的 OpenClaw 自定义数据迁移到 Hermes Agent。从 ~/.openclaw 导入兼容 Hermes 的记忆、SOUL.md、命令白名单、用户技能和选定的工作区资产，然后报告无法迁移的内容及其原因。 | `migration/openclaw-migration` |

## productivity

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `telephony` | 赋予 Hermes 电话功能 —— 配置并持久化 Twilio 号码，发送和接收 SMS/MMS，直接拨打电话，以及通过 Bland.ai 或 Vapi 进行 AI 驱动的自动外呼。 | `productivity/telephony` |

## research

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `bioinformatics` | 通往来自 bioSkills 和 ClawBio 的 400 多项生物信息学技能的网关。涵盖基因组学、转录组学、单细胞、变异调用、药物基因组学、宏基因组学、结构生物学等。 | `research/bioinformatics` |
| `qmd` | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录 —— 这是一个结合了 BM25、向量搜索和 LLM 重排序的混合检索引擎。支持 CLI 和 MCP 集成。 | `research/qmd` |

## security

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `1password` | 设置并使用 1Password CLI (op)。在安装 CLI、启用桌面应用集成、登录以及为命令读取/注入机密信息时使用。 | `security/1password` |
| `oss-forensics` | 针对 GitHub 仓库的供应链调查、证据恢复和取证分析。涵盖已删除提交恢复、强制推送检测、IOC 提取、多源证据收集和结构化取证报告。 | `security/oss-forensics` |
| `sherlock` | 在 400 多个社交网络中进行 OSINT 用户名搜索。通过用户名追踪社交媒体账号。 | `security/sherlock` |
