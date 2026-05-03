---
sidebar_position: 9
title: "可选技能目录"
description: "Hermes Agent 官方附带的可选技能 — 通过 hermes skills install official/<category>/<skill> 安装"
---

# 可选技能目录 {#optional-skills-catalog}

可选技能随 hermes-agent 一起提供，位于 `optional-skills/` 目录下，但**默认不启用**。需要显式安装：

```bash
hermes skills install official/<category>/<skill>
```

例如：

```bash
hermes skills install official/blockchain/solana
hermes skills install official/mlops/flash-attention
```

下方每个技能都链接到对应的专用页面，其中包含完整的定义、设置和使用说明。

卸载技能：

```bash
hermes skills uninstall <skill-name>
```

## autonomous-ai-agents {#autonomous-ai-agents}

| 技能 | 描述 |
|------|------|
| [**blackbox**](/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-blackbox) | 将编码任务委托给 Blackbox AI CLI agent。这是一个多模型 agent，内置评判机制，通过多个 LLM 运行任务并选出最佳结果。需要 blackbox CLI 和 Blackbox AI API 密钥。 |
| [**honcho**](/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-honcho) | 配置并使用 Honcho 记忆与 Hermes 集成——跨会话用户建模、多配置文件对等隔离、观察配置、辩证推理、会话摘要和上下文预算控制。适用于设置 Honcho、排查问题…… |

## blockchain {#blockchain}

| 技能 | 描述 |
|------|------|
| [**base**](/user-guide/skills/optional/blockchain/blockchain-base) | 查询 Base（以太坊 L2）区块链数据，支持美元计价——钱包余额、代币信息、交易详情、Gas 分析、合约检查、巨鲸检测和实时网络状态。使用 Base RPC + CoinGecko，无需 API 密钥。 |
| [**solana**](/user-guide/skills/optional/blockchain/blockchain-solana) | 查询 Solana 区块链数据，支持美元计价——钱包余额、代币投资组合及价值、交易详情、NFT、巨鲸检测和实时网络状态。使用 Solana RPC + CoinGecko，无需 API 密钥。 |

## communication {#communication}

| 技能 | 描述 |
|------|------|
| [**one-three-one-rule**](/user-guide/skills/optional/communication/communication-one-three-one-rule) | 用于技术方案和权衡分析的结构化决策框架。当用户在多个方案之间做选择时（架构决策、工具选择、重构策略、迁移路径等），该技能会…… |

## creative {#creative}

| 技能 | 描述 |
|------|------|
| [**blender-mcp**](/user-guide/skills/optional/creative/creative-blender-mcp) | 通过 socket 连接 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python（bpy）代码。适用于用户想要在 Blender 中创建或修改任何内容时。 |
| [**concept-diagrams**](/user-guide/skills/optional/creative/creative-concept-diagrams) | 生成扁平、极简、支持明暗模式的 SVG 图表，作为独立 HTML 文件。使用统一的教育视觉语言，包含 9 种语义色阶、句子式排版和自动暗色模式。最适合教育和概念说明…… |
| [**meme-generation**](/user-guide/skills/optional/creative/creative-meme-generation) | 通过选择模板并使用 Pillow 叠加文字，生成真实的梗图。输出实际的 .png 梗图文件。 |
## devops {#devops}

| 技能 | 描述 |
|-------|-------------|
| [**inference-sh-cli**](/user-guide/skills/optional/devops/devops-cli) | 通过 inference.sh CLI (infsh) 运行 150+ 个 AI 应用 — 图像生成、视频创作、LLM、搜索、3D、社交自动化。使用终端工具。触发词：inference.sh, infsh, ai apps, flux, veo, image generation, video generation, seedrea... |
| [**docker-management**](/user-guide/skills/optional/devops/devops-docker-management) | 管理 Docker 容器、镜像、卷、网络和 Compose 堆栈 — 生命周期操作、调试、清理和 Dockerfile 优化。 |

## dogfood {#dogfood}

| 技能 | 描述 |
|-------|-------------|
| [**adversarial-ux-test**](/user-guide/skills/optional/dogfood/dogfood-adversarial-ux-test) | 扮演你产品中最难缠、最抗拒技术的用户。以该角色浏览应用，找出所有 UX 痛点，然后通过实用主义层过滤投诉，将真正的问题与噪音区分开。生成可操作的工单... |

## email {#email}

| 技能 | 描述 |
|-------|-------------|
| [**agentmail**](/user-guide/skills/optional/email/email-agentmail) | 通过 AgentMail 为 Agent 提供其专用的电子邮件收件箱。使用 Agent 拥有的电子邮件地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理电子邮件。 |

## health {#health}

| 技能 | 描述 |
|-------|-------------|
| [**fitness-nutrition**](/user-guide/skills/optional/health/health-fitness-nutrition) | 健身房锻炼计划制定和营养追踪。通过 wger 按肌肉、设备或类别搜索 690+ 种练习。通过 USDA FoodData Central 查询 380,000+ 种食物的宏量和卡路里。计算 BMI、TDEE、单次最大重量、宏量营养素分配和身体... |
| [**neuroskill-bci**](/user-guide/skills/optional/health/health-neuroskill-bci) | 连接到正在运行的 NeuroSkill 实例，并将用户的实时认知和情绪状态（专注度、放松度、情绪、认知负荷、困倦度、心率、HRV、睡眠分期以及 40+ 个衍生 EXG 分数）融入响应中。... |

## mcp {#mcp}

| 技能 | 描述 |
|-------|-------------|
| [**fastmcp**](/user-guide/skills/optional/mcp/mcp-fastmcp) | 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。在创建新的 MCP 服务器、将 API 或数据库包装为 MCP 工具、暴露资源或提示，或为 Claude Code、Cur... 准备 FastMCP 服务器时使用。 |
| [**mcporter**](/user-guide/skills/optional/mcp/mcp-mcporter) | 使用 mcporter CLI 直接列出、配置、认证和调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑和 CLI/类型生成。 |

## migration {#migration}

| 技能 | 描述 |
|-------|-------------|
| [**openclaw-migration**](/user-guide/skills/optional/migration/migration-openclaw-migration) | 将用户的 OpenClaw 自定义配置迁移到 Hermes Agent。从 ~/.openclaw 导入与 Hermes 兼容的记忆、SOUL.md、命令白名单、用户技能和选定的工作区资产，然后报告哪些内容无法迁移... |
## mlops {#mlops}

| 技能 | 描述 |
|-------|-------------|
| [**huggingface-accelerate**](/user-guide/skills/optional/mlops/mlops-accelerate) | 最简单的分布式训练 API。只需 4 行代码即可为任何 PyTorch 脚本添加分布式支持。为 DeepSpeed/FSDP/Megatron/DDP 提供统一 API。自动设备放置、混合精度（FP16/BF16/FP8）。交互式配置，单次启动命令... |
| [**chroma**](/user-guide/skills/optional/mlops/mlops-chroma) | 面向 AI 应用的开源嵌入数据库。存储嵌入向量和元数据，执行向量和全文搜索，按元数据过滤。简单的 4 函数 API。可从笔记本扩展到生产集群。用于语义搜索、RAG... |
| [**clip**](/user-guide/skills/optional/mlops/mlops-clip) | OpenAI 连接视觉和语言的模型。支持零样本图像分类、图像-文本匹配和跨模态检索。在 4 亿图像-文本对上训练。用于图像搜索、内容审核或视觉-语言任务... |
| [**faiss**](/user-guide/skills/optional/mlops/mlops-faiss) | Facebook 的高效稠密向量相似性搜索和聚类库。支持数十亿向量、GPU 加速以及多种索引类型（Flat、IVF、HNSW）。用于快速 k-NN 搜索、大规模向量检索，或当... |
| [**optimizing-attention-flash**](/user-guide/skills/optional/mlops/mlops-flash-attention) | 使用 Flash Attention 优化 Transformer 注意力机制，实现 2-4 倍加速和 10-20 倍内存减少。在训练/运行长序列（>512 tokens）的 Transformer、遇到注意力机制的 GPU 内存问题，或需要更快的推... |
| [**guidance**](/user-guide/skills/optional/mlops/mlops-guidance) | 使用正则表达式和语法控制 LLM 输出，保证生成有效的 JSON/XML/代码，强制执行结构化格式，并通过 Guidance（微软研究院的约束生成框架）构建多步骤工作流 |
| [**hermes-atropos-environments**](/user-guide/skills/optional/mlops/mlops-hermes-atropos-environments) | 构建、测试和调试用于 Atropos 训练的 Hermes Agent RL 环境。涵盖 HermesAgentBaseEnv 接口、奖励函数、agent loop 集成、使用工具进行评估、wandb 日志记录以及三种 CLI 模式（serve/process/eva... |
| [**huggingface-tokenizers**](/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) | 为研究和生产优化的快速分词器。基于 Rust 的实现可在 &lt;20 秒内处理 1GB 数据。支持 BPE、WordPiece 和 Unigram 算法。训练自定义词汇表、跟踪对齐、处理填充/截断。集成... |
| [**instructor**](/user-guide/skills/optional/mlops/mlops-instructor) | 使用 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，安全地解析复杂 JSON，并流式传输部分结果——经过实战检验的结构化输出库 |
| [**lambda-labs-gpu-cloud**](/user-guide/skills/optional/mlops/mlops-lambda-labs) | 用于 ML 训练和推理的预留和按需 GPU 云实例。当你需要具有简单 SSH 访问、持久文件系统或用于大规模训练的高性能多节点集群的专用 GPU 实例时使用。 |
| [**llava**](/user-guide/skills/optional/mlops/mlops-llava) | 大型语言与视觉助手。支持视觉指令微调和基于图像的对话。结合 CLIP 视觉编码器与 Vicuna/LLaMA 语言模型。支持多轮图像聊天、视觉问答和指令... |
| [**modal-serverless-gpu**](/user-guide/skills/optional/mlops/mlops-modal) | 用于运行 ML 工作负载的无服务器 GPU 云平台。当你需要按需 GPU 访问而无需管理基础设施、将 ML 模型部署为 API，或运行具有自动扩展的批处理作业时使用。 |
| [**nemo-curator**](/user-guide/skills/optional/mlops/mlops-nemo-curator) | 用于 LLM 训练的 GPU 加速数据整理。支持文本/图像/视频/音频。特性包括模糊去重（快 16 倍）、质量过滤（30+ 启发式）、语义去重、PII 编辑、NSFW 检测。跨 GPU 扩展... |
| [**peft-fine-tuning**](/user-guide/skills/optional/mlops/mlops-peft) | 使用 LoRA、QLoRA 和 25+ 种方法对 LLM 进行参数高效微调。当在有限 GPU 内存下微调大型模型（7B-70B）、需要训练 &lt;1% 的参数且精度损失最小，或用于多适配器服务... |
| [**pinecone**](/user-guide/skills/optional/mlops/mlops-pinecone) | 用于生产 AI 应用的托管向量数据库。完全托管、自动扩展，支持混合搜索（稠密 + 稀疏）、元数据过滤和命名空间。低延迟（&lt;100ms p95）。用于生产 RAG、推荐系统或... |
| [**pytorch-fsdp**](/user-guide/skills/optional/mlops/mlops-pytorch-fsdp) | 使用 PyTorch FSDP 进行全分片数据并行训练的专家指导——参数分片、混合精度、CPU 卸载、FSDP2 |
| [**pytorch-lightning**](/user-guide/skills/optional/mlops/mlops-pytorch-lightning) | 高级 PyTorch 框架，包含 Trainer 类、自动分布式训练（DDP/FSDP/DeepSpeed）、回调系统和最少的样板代码。使用相同代码可从笔记本电脑扩展到超级计算机。当你想要简洁的训练循环... |
| [**qdrant-vector-search**](/user-guide/skills/optional/mlops/mlops-qdrant) | 用于 RAG 和语义搜索的高性能向量相似性搜索引擎。当构建需要快速最近邻搜索、带过滤的混合搜索或具有 Rust 驱动性能的可扩展向量存储的生产 RAG 系统时使用... |
| [**sparse-autoencoder-training**](/user-guide/skills/optional/mlops/mlops-saelens) | 提供使用 SAELens 训练和分析稀疏自编码器（SAE）的指导，以将神经网络激活分解为可解释的特征。当发现可解释特征、分析叠加或研究...时使用 |
| [**simpo-training**](/user-guide/skills/optional/mlops/mlops-simpo) | 用于 LLM 对齐的简单偏好优化。DPO 的无参考替代方案，性能更优（在 AlpacaEval 2.0 上 +6.4 分）。无需参考模型，比 DPO 更高效。当想要简单的偏好对齐...时使用 |
| [**slime-rl-training**](/user-guide/skills/optional/mlops/mlops-slime) | 提供使用 slime（一个 Megatron+SGLang 框架）通过 RL 进行 LLM 后训练的指导。当训练 GLM 模型、实现自定义数据生成工作流，或需要紧密的 Megatron-LM 集成进行 RL 扩展时使用。 |
| [**stable-diffusion-image-generation**](/user-guide/skills/optional/mlops/mlops-stable-diffusion) | 使用 HuggingFace Diffusers 通过 Stable Diffusion 模型进行最先进的文本到图像生成。当从文本提示生成图像、执行图像到图像转换、修复或构建自定义扩散管道时使用。 |
| [**tensorrt-llm**](/user-guide/skills/optional/mlops/mlops-tensorrt-llm) | 使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟。用于 NVIDIA GPU（A100/H100）上的生产部署，当你需要比 PyTorch 快 10-100 倍的推理速度，或用于提供量化模型服务... |
| [**distributed-llm-pretraining-torchtitan**](/user-guide/skills/optional/mlops/mlops-torchtitan) | 使用 torchtitan 进行 PyTorch 原生分布式 LLM 预训练，支持 4D 并行（FSDP2、TP、PP、CP）。当在 8 到 512+ GPU 上大规模预训练 Llama 3.1、DeepSeek V3 或自定义模型时使用，支持 Float8、torch.compile 和分布式... |
| [**whisper**](/user-guide/skills/optional/mlops/mlops-whisper) | OpenAI 的通用语音识别模型。支持 99 种语言、转录、翻译成英语以及语言识别。六种模型大小，从 tiny（3900 万参数）到 large（15.5 亿参数）。用于语音转文本、播客... |
## productivity {#productivity}

| 技能 | 描述 |
|-------|-------------|
| [**canvas**](/user-guide/skills/optional/productivity/productivity-canvas) | Canvas LMS 集成 — 使用 API 令牌认证获取已注册课程和作业。 |
| [**here.now**](/user-guide/skills/optional/productivity/productivity-here-now) | 将静态站点发布到 &#123;slug&#125;.here.now，并在云端 Drive 中存储私有文件，用于 Agent 之间的交接。 |
| [**memento-flashcards**](/user-guide/skills/optional/productivity/productivity-memento-flashcards) | 间隔重复记忆卡片系统。从事实或文本创建卡片，使用由 Agent 评分的自由文本答案与卡片对话，从 YouTube 转录生成测验，通过自适应调度复习到期卡片，并支持导出/导入…… |
| [**shopify**](/user-guide/skills/optional/productivity/productivity-shopify) | 通过 curl 调用 Shopify Admin & Storefront GraphQL API。管理产品、订单、客户、库存、元字段。 |
| [**siyuan**](/user-guide/skills/optional/productivity/productivity-siyuan) | 通过 curl 调用 SiYuan Note API，在自托管知识库中搜索、读取、创建和管理块与文档。 |
| [**telephony**](/user-guide/skills/optional/productivity/productivity-telephony) | 无需修改核心工具即可为 Hermes 提供电话能力。配置并持久化一个 Twilio 号码，发送和接收 SMS/MMS，拨打电话，并通过 Bland.ai 或 Vapi 发起 AI 驱动的外呼。 |

## research {#research}

| 技能 | 描述 |
|-------|-------------|
| [**bioinformatics**](/user-guide/skills/optional/research/research-bioinformatics) | 通过 bioSkills 和 ClawBio 接入 400 多项生物信息学技能。涵盖基因组学、转录组学、单细胞、变异检测、药物基因组学、宏基因组学、结构生物学等。获取领域特定的参考资料…… |
| [**domain-intel**](/user-guide/skills/optional/research/research-domain-intel) | 使用 Python 标准库进行被动域名侦察。子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录、域名可用性检查以及批量多域名分析。无需 API 密钥。 |
| [**drug-discovery**](/user-guide/skills/optional/research/research-drug-discovery) | 药物发现工作流的药物研究助手。在 ChEMBL 上搜索生物活性化合物，计算类药性（Lipinski Ro5、QED、TPSA、合成可及性），通过 OpenFDA 查询药物相互作用，解读 ADMET…… |
| [**duckduckgo-search**](/user-guide/skills/optional/research/research-duckduckgo-search) | 通过 DuckDuckGo 进行免费网页搜索 — 文本、新闻、图片、视频。无需 API 密钥。优先使用已安装的 `ddgs` CLI；仅在确认当前运行时中 `ddgs` 可用时，才使用 Python DDGS 库。 |
| [**gitnexus-explorer**](/user-guide/skills/optional/research/research-gitnexus-explorer) | 使用 GitNexus 索引代码库，并通过 Web UI + Cloudflare 隧道提供交互式知识图谱。 |
| [**parallel-cli**](/user-guide/skills/optional/research/research-parallel-cli) | Parallel CLI 的可选供应商技能 — Agent 原生网页搜索、提取、深度研究、丰富化、FindAll 和监控。优先使用 JSON 输出和非交互式流程。 |
| [**qmd**](/user-guide/skills/optional/research/research-qmd) | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议转录 — 一种混合检索引擎，结合 BM25、向量搜索和 LLM 重排序。支持 CLI 和 MCP 集成。 |
| [**scrapling**](/user-guide/skills/optional/research/research-scrapling) | 使用 Scrapling 进行网页抓取 — HTTP 获取、隐身浏览器自动化、Cloudflare 绕过，以及通过 CLI 和 Python 的爬虫抓取。 |
## security {#security}

| 技能 | 描述 |
|------|------|
| [**1password**](/user-guide/skills/optional/security/security-1password) | 安装并使用 1Password CLI（op）。适用于安装 CLI、启用桌面应用集成、登录以及读取/注入命令密钥等场景。 |
| [**oss-forensics**](/user-guide/skills/optional/security/security-oss-forensics) | 针对 GitHub 仓库的供应链调查、证据恢复和取证分析。涵盖已删除提交恢复、强制推送检测、IOC 提取、多源证据收集、假设形成/验证以及 st... |
| [**sherlock**](/user-guide/skills/optional/security/security-sherlock) | 在 400+ 社交网络中进行 OSINT 用户名搜索。通过用户名追踪社交媒体账号。 |

## web-development {#web-development}

| 技能 | 描述 |
|------|------|
| [**page-agent**](/user-guide/skills/optional/web-development/web-development-page-agent) | 将 alibaba/page-agent 嵌入到你的 Web 应用中——这是一个纯 JavaScript 的页面内 GUI Agent，以单个 &lt;script&gt; 标签或 npm 包形式发布，让网站最终用户通过自然语言驱动 UI（例如“点击登录，填写用户名...”）。 |

---

## 贡献可选技能 {#contributing-optional-skills}

要向仓库添加新的可选技能：

1. 在 `optional-skills/&lt;category&gt;/&lt;skill-name&gt;/` 下创建一个目录
2. 添加一个 `SKILL.md` 文件，包含标准 frontmatter（name、description、version、author）
3. 将任何支持文件放入 `references/`、`templates/` 或 `scripts/` 子目录中
4. 提交一个 pull request——该技能将出现在此目录中，合并后会自动生成对应的文档页面
