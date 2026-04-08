---
sidebar_position: 9
title: "可选技能目录"
description: "hermes-agent 官方提供的可选技能 — 通过 hermes skills install official/<category>/<skill> 进行安装"
---

# 可选技能目录

官方可选技能随 hermes-agent 仓库一同发布，位于 `optional-skills/` 目录下，但**默认不激活**。你需要显式安装它们：

```bash
hermes skills install official/<category>/<skill>
```

例如：

```bash
hermes skills install official/blockchain/solana
hermes skills install official/mlops/flash-attention
```

安装完成后，该技能将出现在 Agent 的技能列表中，并在检测到相关任务时自动加载。

卸载命令：

```bash
hermes skills uninstall <skill-name>
```

---

## 自主 AI Agent (Autonomous AI Agents)

| 技能 | 描述 |
|-------|-------------|
| **blackbox** | 将编码任务委托给 Blackbox AI CLI Agent。这是一个多模型 Agent，内置裁判机制，可通过多个 LLM 运行任务并挑选最佳结果。 |
| **honcho** | 在 Hermes 中配置并使用 Honcho 记忆 — 实现跨会话用户建模、多配置文件的同级隔离、观察配置以及辩证推理。 |

## 区块链 (Blockchain)

| 技能 | 描述 |
|-------|-------------|
| **base** | 查询 Base (Ethereum L2) 区块链数据并提供美元计价 — 包括钱包余额、代币信息、交易详情、Gas 分析、合约检查、巨鲸检测和实时网络统计。无需 API 密钥。 |
| **solana** | 查询 Solana 区块链数据并提供美元计价 — 包括钱包余额、代币组合、交易详情、NFT、巨鲸检测和实时网络统计。无需 API 密钥。 |

## 沟通 (Communication)

| 技能 | 描述 |
|-------|-------------|
| **one-three-one-rule** | 用于提案和决策的结构化沟通框架。 |

## 创意 (Creative)

| 技能 | 描述 |
|-------|-------------|
| **blender-mcp** | 通过 socket 连接到 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python (bpy) 代码。 |
| **meme-generation** | 生成真实的表情包图片。通过选择模板并使用 Pillow 叠加文字，生成实际的 `.png` 表情包文件。 |

## 运维 (DevOps)

| 技能 | 描述 |
|-------|-------------|
| **cli** | 通过 inference.sh CLI (infsh) 运行 150 多个 AI 应用 — 涵盖图像生成、视频创建、LLM、搜索、3D 和社交自动化。 |
| **docker-management** | 管理 Docker 容器、镜像、数据卷、网络和 Compose 堆栈 — 包括生命周期操作、调试、清理和 Dockerfile 优化。 |

## 电子邮件 (Email)

| 技能 | 描述 |
|-------|-------------|
| **agentmail** | 通过 AgentMail 为 Agent 提供专用的电子邮箱。使用 Agent 拥有的邮箱地址自主发送、接收和管理电子邮件。 |

## 健康 (Health)

| 技能 | 描述 |
|-------|-------------|
| **neuroskill-bci** | 用于神经科学研究工作流的脑机接口 (BCI) 集成。 |

## MCP

| 技能 | 描述 |
|-------|-------------|
| **fastmcp** | 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。涵盖将 API 或数据库包装为 MCP 工具、暴露资源或提示词以及部署。 |

## 迁移 (Migration)

| 技能 | 描述 |
|-------|-------------|
| **openclaw-migration** | 将用户的 OpenClaw 自定义数据迁移到 Hermes Agent。导入记忆、SOUL.md、命令白名单、用户技能和选定的工作区资产。 |

## MLOps

最大的可选类别 — 涵盖从数据清洗到生产推理的完整 ML 流水线。

| 技能 | 描述 |
|-------|-------------|
| **accelerate** | 最简单的分布式训练 API。只需 4 行代码即可为任何 PyTorch 脚本添加分布式支持。为 DeepSpeed/FSDP/Megatron/DDP 提供统一 API。 |
| **chroma** | 开源嵌入 (embedding) 数据库。存储嵌入和元数据，执行向量和全文搜索。为 RAG 和语义搜索提供简单的 4 函数 API。 |
| **faiss** | Facebook 的库，用于密集向量的高效相似性搜索和聚类。支持数十亿个向量、GPU 加速和各种索引类型 (Flat, IVF, HNSW)。 |
| **flash-attention** | 使用 Flash Attention 优化 Transformer 注意力机制，实现 2-4 倍加速和 10-20 倍显存减少。支持 PyTorch SDPA、flash-attn 库、H100 FP8 和滑动窗口。 |
| **hermes-atropos-environments** | 为 Atropos 训练构建、测试和调试 Hermes Agent 强化学习 (RL) 环境。涵盖 HermesAgentBaseEnv 接口、奖励函数、Agent 循环集成和评估。 |
| **huggingface-tokenizers** | 基于 Rust 的快速分词器，适用于研究和生产。20 秒内可处理 1GB 数据。支持 BPE、WordPiece 和 Unigram 算法。 |
| **instructor** | 从 LLM 响应中提取结构化数据，支持 Pydantic 验证、自动重试失败的提取并流式传输部分结果。 |
| **lambda-labs** | 用于 ML 训练和推理的预留及按需 GPU 云实例。提供 SSH 访问、持久文件系统和多节点集群。 |
| **llava** | 大型语言与视觉助手 (Large Language and Vision Assistant) — 结合 CLIP 视觉与 LLaMA 语言模型，实现视觉指令微调和基于图像的对话。 |
| **nemo-curator** | 用于 LLM 训练的 GPU 加速数据清洗。模糊去重（快 16 倍）、质量过滤（30 多个启发式算法）、语义去重、PII 脱敏。支持通过 RAPIDS 扩展。 |
| **pinecone** | 适用于生产级 AI 的托管向量数据库。支持自动扩缩容、混合搜索（密集 + 稀疏）、元数据过滤和低延迟（p95 低于 100ms）。 |
| **pytorch-lightning** | 高级 PyTorch 框架，包含 Trainer 类、自动分布式训练 (DDP/FSDP/DeepSpeed)、回调函数和极简的样板代码。 |
| **qdrant** | 高性能向量相似性搜索引擎。由 Rust 驱动，具有快速的最近邻搜索、带过滤的混合搜索和可扩展的向量存储。 |
| **saelens** | 使用 SAELens 训练和分析稀疏自编码器 (SAE)，将神经网络激活分解为可解释的特征。 |
| **simpo** | 简单偏好优化 (Simple Preference Optimization) — DPO 的无参考模型替代方案，性能更佳（在 AlpacaEval 2.0 上提升 6.4 分）。无需参考模型。 |
| **slime** | 使用 Megatron+SGLang 框架通过强化学习 (RL) 进行 LLM 后训练。支持自定义数据生成工作流和紧密的 Megatron-LM 集成以实现 RL 扩展。 |
| **tensorrt-llm** | 使用 NVIDIA TensorRT 优化 LLM 推理以获得最大吞吐量。在 A100/H100 上通过量化 (FP8/INT4) 和 In-flight Batching 比 PyTorch 快 10-100 倍。 |
| **torchtitan** | PyTorch 原生分布式 LLM 预训练，支持 4D 并行 (FSDP2, TP, PP, CP)。利用 Float8 和 torch.compile 可从 8 个 GPU 扩展至 512 个以上。 |

## 生产力 (Productivity)

| 技能 | 描述 |
|-------|-------------|
| **canvas** | Canvas LMS 集成 — 使用 API 令牌身份验证获取已注册的课程和作业。 |
| **memento-flashcards** | 用于学习和知识巩固的间隔重复抽认卡系统。 |
| **siyuan** | 思源笔记 (SiYuan Note) API，用于在自托管知识库中搜索、阅读、创建和管理块与文档。 |
| **telephony** | 赋予 Hermes 电话功能 — 配置 Twilio 号码、收发短信/彩信、拨打电话，并通过 Bland.ai 或 Vapi 进行 AI 驱动的自动外呼。 |

## 研究 (Research)

| 技能 | 描述 |
|-------|-------------|
| **bioinformatics** | 通往 bioSkills 和 ClawBio 中 400 多个生物信息学技能的网关。涵盖基因组学、转录组学、单细胞、变异调用、药物基因组学、宏基因组学和结构生物学。 |
| **domain-intel** | 使用 Python 标准库进行被动域名侦察。子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录以及批量多域名分析。无需 API 密钥。 |
| **duckduckgo-search** | 通过 DuckDuckGo 进行免费网页搜索 — 文本、新闻、图片、视频。无需 API 密钥。 |
| **gitnexus-explorer** | 使用 GitNexus 为代码库建立索引，并通过 Web UI 和 Cloudflare 隧道提供交互式知识图谱。 |
| **parallel-cli** | Parallel CLI 的厂商技能 — 提供 Agent 原生的网页搜索、提取、深度研究、富化和监控。 |
| **qmd** | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录 — 这是一个结合了 BM25、向量搜索和 LLM 重排序的混合检索引擎。 |
| **scrapling** | 使用 Scrapling 进行网页抓取 — 支持 HTTP 获取、隐身浏览器自动化、绕过 Cloudflare，以及通过 CLI 和 Python 进行爬虫抓取。 |
## Security

| Skill | Description |
|-------|-------------|
| **1password** | 设置并使用 1Password CLI (op)。安装 CLI、启用桌面应用集成、登录，以及为命令读取/注入 secrets。 |
| **oss-forensics** | 开源软件取证 —— 分析软件包、依赖项和供应链风险。 |
| **sherlock** | 跨 400 多个社交网络的 OSINT 用户名搜索。通过用户名追踪社交媒体账号。 |

---

## Contributing Optional Skills

若要向仓库添加新的可选技能：

1. 在 `optional-skills/<category>/<skill-name>/` 下创建一个目录
2. 添加一个带有标准 frontmatter（name, description, version, author）的 `SKILL.md` 文件
3. 在 `references/`、`templates/` 或 `scripts/` 子目录中包含任何支持文件
4. 提交 Pull Request —— 合并后，该技能将出现在此目录中
