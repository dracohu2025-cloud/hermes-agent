---
sidebar_position: 9
title: "可选技能目录"
description: "Hermes Agent 附带的官方可选技能 — 通过 hermes skills install official/<category>/<skill> 安装"
---

<a id="optional-skills-catalog"></a>
# 可选技能目录

可选技能随 Hermes Agent 一起提供，位于 `optional-skills/` 目录下，但**默认不激活**。需要显式安装它们：

```bash
hermes skills install official/<category>/<skill>
```

例如：

```bash
hermes skills install official/blockchain/solana
hermes skills install official/mlops/flash-attention
```

下面的每个技能都链接到一个专用页面，包含完整的定义、设置和使用说明。

卸载方法：

```bash
hermes skills uninstall <skill-name>
```

<a id="autonomous-ai-agents"></a>
## autonomous-ai-agents

| 技能 | 描述 |
|-------|-------------|
| [**blackbox**](/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-blackbox) | 将编码任务委托给 Blackbox AI CLI agent。多模型 agent，内置评判器，可通过多个 LLM 运行任务并选择最佳结果。需要 blackbox CLI 和 Blackbox AI API 密钥。 |
| [**honcho**](/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-honcho) | 配置 Hermes 并使用 Honcho 记忆——跨会话用户建模、多配置文件隔离、观察配置、辩证推理、会话摘要和上下文预算强制执行。在设置 Honcho、排查... 时使用。 |

<a id="blockchain"></a>
## blockchain

| 技能 | 描述 |
|-------|-------------|
| [**evm**](/user-guide/skills/optional/blockchain/blockchain-evm) | 只读 EVM 客户端：钱包、代币、Gas（支持 8 条链）。 |
| [**hyperliquid**](/user-guide/skills/optional/blockchain/blockchain-hyperliquid) | Hyperliquid 市场数据、账户历史、交易回顾。 |
| [**solana**](/user-guide/skills/optional/blockchain/blockchain-solana) | 查询 Solana 区块链数据及美元定价——钱包余额、带估值的代币组合、交易详情、NFT、巨鲸检测和实时网络统计。使用 Solana RPC + CoinGecko。无需 API 密钥。 |

<a id="communication"></a>
## communication

| 技能 | 描述 |
|-------|-------------|
| [**one-three-one-rule**](/user-guide/skills/optional/communication/communication-one-three-one-rule) | 技术提案和权衡分析的结构化决策框架。当用户在多个方案之间做出选择（架构决策、工具选择、重构策略、迁移路径）时，此技能会... |

<a id="creative"></a>
## creative

| 技能 | 描述 |
|-------|-------------|
| [**blender-mcp**](/user-guide/skills/optional/creative/creative-blender-mcp) | 通过 socket 连接到 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python (bpy) 代码。在用户想要在 Blender 中创建或修改任何内容时使用。 |
| [**concept-diagrams**](/user-guide/skills/optional/creative/creative-concept-diagrams) | 生成扁平、极简、自适应亮暗的 SVG 图形，输出为独立 HTML 文件。使用统一的教育视觉语言，包含 9 个语义色阶、首字母大写排版和自动暗色模式。最适合教育和笔记... |
| [**hyperframes**](/user-guide/skills/optional/creative/creative-hyperframes) | 使用 HyperFrames 创建基于 HTML 的视频合成、动画标题卡、社交覆盖层、带字幕的讲话人头视频、音频响应式视觉效果和着色器过渡。HTML 是视频的最终来源。当用户想要... 时使用。 |
| [**kanban-video-orchestrator**](/user-guide/skills/optional/creative/creative-kanban-video-orchestrator) | 规划、设置并监控由 Hermes Kanban 支持的多 Agent 视频制作流程。当用户想要制作任何视频时使用——叙事电影、产品/营销、音乐视频、解说、ASCII/终端艺术、抽象/生成式作品... |
| [**meme-generation**](/user-guide/skills/optional/creative/creative-meme-generation) | 通过选择模板并使用 Pillow 叠加文字，生成真实的梗图。生成实际的 .png 梗图文件。 |
<a id="devops"></a>
## devops

| 技能 | 描述 |
|-------|-------------|
| [**inference-sh-cli**](/user-guide/skills/optional/devops/devops-cli) | 通过 inference.sh CLI（infsh）运行 150 多个 AI 应用——图像生成、视频创建、LLM、搜索、3D、社交自动化。使用终端工具。触发词：inference.sh、infsh、ai apps、flux、veo、图片生成、视频生成、seedrea... |
| [**docker-management**](/user-guide/skills/optional/devops/devops-docker-management) | 管理 Docker 容器、镜像、卷、网络和 Compose 堆栈——生命周期操作、调试、清理和 Dockerfile 优化。 |
| [**pinggy-tunnel**](/user-guide/skills/optional/devops/devops-pinggy-tunnel) | 通过 Pinggy 实现零安装的 SSH 本地主机隧道。 |
| [**watchers**](/user-guide/skills/optional/devops/devops-watchers) | 轮询 RSS、JSON API 和 GitHub，并附带水印去重。 |

<a id="dogfood"></a>
## dogfood

| 技能 | 描述 |
|-------|-------------|
| [**adversarial-ux-test**](/user-guide/skills/optional/dogfood/dogfood-adversarial-ux-test) | 为你的产品扮演最难缠、最抵触技术的用户角色。以该角色身份浏览应用，找出所有 UX 痛点，然后通过实用主义过滤层筛选投诉，区分真正的问题与噪音。创建可操作的票... |

<a id="email"></a>
## email

| 技能 | 描述 |
|-------|-------------|
| [**agentmail**](/user-guide/skills/optional/email/email-agentmail) | 通过 AgentMail 为 Agent 配备专用邮箱。使用 Agent 拥有的电子邮件地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理邮件。 |

<a id="finance"></a>
## finance

| 技能 | 描述 |
|-------|-------------|
| [**3-statement-model**](/user-guide/skills/optional/finance/finance-3-statement-model) | 在 Excel 中构建完全集成的三表模型（利润表、资产负债表、现金流量表），包含营运资金计划、折旧摊销滚转、债务计划，以及使现金和留存收益勾稽的平衡项。与 excel-author 配合使用。 |
| [**comps-analysis**](/user-guide/skills/optional/finance/finance-comps-analysis) | 在 Excel 中构建可比公司分析——运营指标、估值倍数、与同行组的统计基准对比。与 excel-author 配合使用。适用于上市公司估值、IPO定价、行业基准对标或异常值检测。 |
| [**dcf-model**](/user-guide/skills/optional/finance/finance-dcf-model) | 在 Excel 中构建机构级 DCF 估值模型——收入预测、自由现金流构建、WACC、终值、熊/基/牛情景、5x5 敏感性表格。与 excel-author 配合使用。适用于内在价值股权分析。 |
| [**excel-author**](/user-guide/skills/optional/finance/finance-excel-author) | 使用 openpyxl 在无头模式下构建可审计的 Excel 工作簿——蓝/黑/绿色单元格约定、公式优先于硬编码、命名区域、平衡检查、敏感性表格。适用于财务建模、审计输出、对账。 |
| [**lbo-model**](/user-guide/skills/optional/finance/finance-lbo-model) | 在 Excel 中构建杠杆收购模型——资金来源与用途、债务计划、现金扫除、退出倍数、IRR/MOIC 敏感性。与 excel-author 配合使用。适用于私募筛选、赞助商案例估值，或演示材料中的说明性 LBO。 |
| [**merger-model**](/user-guide/skills/optional/finance/finance-merger-model) | 在 Excel 中构建增厚/稀释（合并）模型——备考损益表、协同效应、融资组合、每股收益影响。与 excel-author 配合使用。适用于并购演示、董事会材料或交易评估。 |
| [**pptx-author**](/user-guide/skills/optional/finance/finance-pptx-author) | 使用 python-pptx 在无头模式下构建 PowerPoint 演示文稿。与 excel-author 配合使用，创建以模型为支撑的演示文稿，其中每个数字都追溯到工作簿的某个单元格。适用于路演演示、投资委员会备忘录、财报纪要。 |
| [**stocks**](/user-guide/skills/optional/finance/finance-stocks) | 通过 Yahoo 获取股票报价、历史数据、搜索、对比、加密货币。 |
<a id="health"></a>
## health

| 技能 | 描述 |
|-------|-------------|
| [**fitness-nutrition**](/user-guide/skills/optional/health/health-fitness-nutrition) | 健身房训练计划制定与营养追踪。通过 wger 按肌肉群、器械或类别搜索 690+ 种训练动作。通过 USDA FoodData Central 查询 380,000+ 种食物的宏量和卡路里。计算 BMI、TDEE、单次最大重量、宏量营养素分配和身体... |
| [**neuroskill-bci**](/user-guide/skills/optional/health/health-neuroskill-bci) | 连接到正在运行的 NeuroSkill 实例，将用户的实时认知和情绪状态（专注度、放松度、情绪、认知负荷、困倦程度、心率、心率变异性、睡眠分期以及 40+ 个衍生 EXG 分数）融入回复中。... |

<a id="mcp"></a>
## mcp

| 技能 | 描述 |
|-------|-------------|
| [**fastmcp**](/user-guide/skills/optional/mcp/mcp-fastmcp) | 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。适用于创建新的 MCP 服务器、将 API 或数据库封装为 MCP 工具、暴露资源或提示词，或为 Claude Code、Cur... 准备 FastMCP 服务器。 |
| [**mcporter**](/user-guide/skills/optional/mcp/mcp-mcporter) | 使用 mcporter CLI 直接（通过 HTTP 或 stdio）列出、配置、认证和调用 MCP 服务器/工具，包括临时服务器、配置编辑和 CLI/类型生成。 |

<a id="migration"></a>
## migration

| 技能 | 描述 |
|-------|-------------|
| [**openclaw-migration**](/user-guide/skills/optional/migration/migration-openclaw-migration) | 将用户的 OpenClaw 自定义配置迁移到 Hermes Agent。从 ~/.openclaw 导入兼容 Hermes 的记忆、SOUL.md、命令白名单、用户技能和选定的工作区资产，然后报告哪些内容无法迁移。... |

<a id="mlops"></a>
## mlops

| 技能 | 描述 |
|-------|-------------|
| [**huggingface-accelerate**](/user-guide/skills/optional/mlops/mlops-accelerate) | 最简单的分布式训练 API。仅需 4 行代码即可为任何 PyTorch 脚本添加分布式支持。为 DeepSpeed/FSDP/Megatron/DDP 提供统一 API。自动设备分配、混合精度（FP16/BF16/FP8）。交互式配置、单一启动命令... |
| [**axolotl**](/user-guide/skills/optional/mlops/mlops-training-axolotl) | Axolotl：基于 YAML 的 LLM 微调（LoRA、DPO、GRPO）。 |
| [**chroma**](/user-guide/skills/optional/mlops/mlops-chroma) | 面向 AI 应用的开源嵌入数据库。存储嵌入向量和元数据，执行向量和全文搜索，按元数据过滤。简单的 4 函数 API。可从笔记本扩展到生产集群。适用于语义搜索、RAG... |
| [**clip**](/user-guide/skills/optional/mlops/mlops-clip) | OpenAI 连接视觉和语言的模型。支持零样本图像分类、图像-文本匹配和跨模态检索。在 4 亿图像-文本对上训练。适用于图像搜索、内容审核或视觉-语言任务... |
| [**faiss**](/user-guide/skills/optional/mlops/mlops-faiss) | Facebook 的高效相似度搜索和稠密向量聚类库。支持数十亿向量、GPU 加速和多种索引类型（Flat、IVF、HNSW）。适用于快速 k-NN 搜索、大规模向量检索，或... |
| [**optimizing-attention-flash**](/user-guide/skills/optional/mlops/mlops-flash-attention) | 使用 Flash Attention 优化 Transformer 注意力机制，实现 2-4 倍加速和 10-20 倍内存减少。适用于训练/运行长序列（>512 tokens）的 Transformer、遇到注意力机制 GPU 内存问题，或需要更快的推理... |
| [**guidance**](/user-guide/skills/optional/mlops/mlops-guidance) | 使用正则表达式和语法控制 LLM 输出，保证生成有效的 JSON/XML/代码，强制结构化格式，并使用 Guidance（微软研究院的约束生成框架）构建多步骤工作流。 |
| [**huggingface-tokenizers**](/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) | 为研究和生产优化的快速分词器。基于 Rust 的实现可在 &lt;20 秒内处理 1GB 文本。支持 BPE、WordPiece 和 Unigram 算法。训练自定义词表、跟踪对齐、处理填充/截断。集成... |
| [**instructor**](/user-guide/skills/optional/mlops/mlops-instructor) | 使用 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，安全地解析复杂 JSON，并使用 Instructor（久经考验的结构化输出库）流式传输部分结果。 |
| [**lambda-labs-gpu-cloud**](/user-guide/skills/optional/mlops/mlops-lambda-labs) | 用于 ML 训练和推理的预留和按需 GPU 云实例。适用于需要专用 GPU 实例、简单 SSH 访问、持久文件系统或用于大规模训练的高性能多节点集群。 |
| [**llava**](/user-guide/skills/optional/mlops/mlops-llava) | 大型语言与视觉助手。支持视觉指令微调和基于图像的对话。结合了 CLIP 视觉编码器与 Vicuna/LLaMA 语言模型。支持多轮图像聊天、视觉问答和指令... |
| [**modal-serverless-gpu**](/user-guide/skills/optional/mlops/mlops-modal) | 用于运行 ML 工作负载的无服务器 GPU 云平台。适用于需要按需 GPU 访问而无需管理基础设施、将 ML 模型部署为 API，或运行具有自动扩展能力的批处理作业。 |
| [**nemo-curator**](/user-guide/skills/optional/mlops/mlops-nemo-curator) | 用于 LLM 训练的 GPU 加速数据整理。支持文本/图像/视频/音频。功能包括模糊去重（快 16 倍）、质量过滤（30+ 启发式规则）、语义去重、PII 编辑、NSFW 检测。可在 GPU 上扩展... |
| [**outlines**](/user-guide/skills/optional/mlops/mlops-inference-outlines) | Outlines：结构化 JSON/正则表达式/Pydantic LLM 生成。 |
| [**peft-fine-tuning**](/user-guide/skills/optional/mlops/mlops-peft) | 使用 LoRA、QLoRA 和 25+ 种方法对 LLM 进行参数高效微调。适用于在有限 GPU 内存下微调大型模型（7B-70B），需要训练 &lt;1% 参数且精度损失最小，或用于多适配器服务... |
| [**pinecone**](/user-guide/skills/optional/mlops/mlops-pinecone) | 用于生产级 AI 应用的托管向量数据库。完全托管、自动扩展，支持混合搜索（稠密+稀疏）、元数据过滤和命名空间。低延迟（&lt;100ms p95）。适用于生产级 RAG、推荐系统或语义... |
| [**pytorch-fsdp**](/user-guide/skills/optional/mlops/mlops-pytorch-fsdp) | 使用 PyTorch FSDP 进行全分片数据并行训练的专业指导 - 参数分片、混合精度、CPU 卸载、FSDP2。 |
| [**pytorch-lightning**](/user-guide/skills/optional/mlops/mlops-pytorch-lightning) | 高级 PyTorch 框架，包含 Trainer 类、自动分布式训练（DDP/FSDP/DeepSpeed）、回调系统和最少的样板代码。使用相同代码即可从笔记本扩展到超级计算机。适用于需要简洁训练循环... |
| [**qdrant-vector-search**](/user-guide/skills/optional/mlops/mlops-qdrant) | 用于 RAG 和语义搜索的高性能向量相似度搜索引擎。适用于构建需要快速最近邻搜索、带过滤的混合搜索，或需要基于 Rust 的高性能可扩展向量存储的生产级 RAG 系统。 |
| [**sparse-autoencoder-training**](/user-guide/skills/optional/mlops/mlops-saelens) | 提供使用 SAELens 训练和分析稀疏自编码器（SAE）的指导，以将神经网络激活分解为可解释的特征。适用于发现可解释特征、分析叠加或研究... |
| [**simpo-training**](/user-guide/skills/optional/mlops/mlops-simpo) | 用于 LLM 对齐的简单偏好优化。DPO 的无参考替代方案，性能更优（在 AlpacaEval 2.0 上 +6.4 分）。无需参考模型，比 DPO 更高效。适用于希望简化... 的偏好对齐。 |
| [**slime-rl-training**](/user-guide/skills/optional/mlops/mlops-slime) | 提供使用 slime（一个 Megatron+SGLang 框架）进行 LLM 后训练 RL 的指导。适用于训练 GLM 模型、实现自定义数据生成工作流，或需要紧密集成 Megatron-LM 进行 RL 扩展。 |
| [**stable-diffusion-image-generation**](/user-guide/skills/optional/mlops/mlops-stable-diffusion) | 使用 HuggingFace Diffusers 和 Stable Diffusion 模型进行最先进的文本到图像生成。适用于从文本提示生成图像、执行图像到图像转换、图像修复或构建自定义扩散管道。 |
| [**tensorrt-llm**](/user-guide/skills/optional/mlops/mlops-tensorrt-llm) | 使用 NVIDIA TensorRT 优化 LLM 推理，实现最大吞吐量和最低延迟。适用于在 NVIDIA GPU（A100/H100）上进行生产部署，需要比 PyTorch 快 10-100 倍的推理速度，或使用量化... 服务模型。 |
| [**distributed-llm-pretraining-torchtitan**](/user-guide/skills/optional/mlops/mlops-torchtitan) | 使用 torchtitan 和 4D 并行（FSDP2、TP、PP、CP）进行 PyTorch 原生的分布式 LLM 预训练。适用于在 8 到 512+ GPU 上使用 Float8、torch.compile 和分布式... 预训练 Llama 3.1、DeepSeek V3 或自定义模型。 |
| [**fine-tuning-with-trl**](/user-guide/skills/optional/mlops/mlops-training-trl-fine-tuning) | TRL：用于 LLM RLHF 的 SFT、DPO、PPO、GRPO、奖励建模。 |
| [**unsloth**](/user-guide/skills/optional/mlops/mlops-training-unsloth) | Unsloth：2-5 倍更快的 LoRA/QLoRA 微调，更少的 VRAM。 |
| [**whisper**](/user-guide/skills/optional/mlops/mlops-whisper) | OpenAI 的通用语音识别模型。支持 99 种语言、转录、翻译成英语和语言识别。六种模型大小，从 tiny（3900 万参数）到 large（15.5 亿参数）。适用于语音转文本、播客... |
<a id="productivity"></a>
## productivity

| 技能 | 描述 |
|-------|-------------|
| [**canvas**](/user-guide/skills/optional/productivity/productivity-canvas) | Canvas LMS 集成 — 使用 API 令牌认证获取已注册课程和作业。 |
| [**here.now**](/user-guide/skills/optional/productivity/productivity-here-now) | 将静态站点发布到 &#123;slug&#125;.here.now，并在云端 Drive 中存储私有文件，用于 Agent 之间的交接。 |
| [**memento-flashcards**](/user-guide/skills/optional/productivity/productivity-memento-flashcards) | 间隔重复记忆卡片系统。从事实或文本创建卡片，使用由 Agent 评分的自由文本答案与卡片对话，从 YouTube 转录生成测验，通过自适应调度复习到期卡片，并支持导出/导入... |
| [**shop-app**](/user-guide/skills/optional/productivity/productivity-shop-app) | Shop.app：商品搜索、订单追踪、退货、重新下单。 |
| [**shopify**](/user-guide/skills/optional/productivity/productivity-shopify) | 通过 curl 调用 Shopify 管理后台和 Storefront GraphQL API。涵盖商品、订单、客户、库存、元字段。 |
| [**siyuan**](/user-guide/skills/optional/productivity/productivity-siyuan) | 思源笔记 API，用于通过 curl 在自托管知识库中搜索、读取、创建和管理块与文档。 |
| [**telephony**](/user-guide/skills/optional/productivity/productivity-telephony) | 无需修改核心工具即可为 Hermes 提供电话能力。配置并持久化一个 Twilio 号码，发送和接收 SMS/MMS，拨打电话，并通过 Bland.ai 或 Vapi 发起 AI 驱动的外呼。 |

<a id="research"></a>
## research

| 技能 | 描述 |
|-------|-------------|
| [**bioinformatics**](/user-guide/skills/optional/research/research-bioinformatics) | 来自 bioSkills 和 ClawBio 的 400 多项生物信息学技能入口。涵盖基因组学、转录组学、单细胞、变异检测、药物基因组学、宏基因组学、结构生物学等。获取领域特定的参考资料... |
| [**darwinian-evolver**](/user-guide/skills/optional/research/research-darwinian-evolver) | 使用 Imbue 的进化循环来进化提示词/正则表达式/SQL/代码。 |
| [**domain-intel**](/user-guide/skills/optional/research/research-domain-intel) | 使用 Python 标准库进行被动域名侦察。子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录、域名可用性检查以及批量多域名分析。无需 API 密钥。 |
| [**drug-discovery**](/user-guide/skills/optional/research/research-drug-discovery) | 用于药物发现流程的制药研究助手。在 ChEMBL 上搜索生物活性化合物，计算类药性（Lipinski Ro5、QED、TPSA、合成可及性），通过 OpenFDA 查询药物相互作用，解读 ADMET... |
| [**duckduckgo-search**](/user-guide/skills/optional/research/research-duckduckgo-search) | 通过 DuckDuckGo 进行免费网络搜索 — 文本、新闻、图片、视频。无需 API 密钥。优先使用已安装的 `ddgs` CLI；仅在确认当前运行环境中 `ddgs` 可用后，再使用 Python DDGS 库。 |
| [**gitnexus-explorer**](/user-guide/skills/optional/research/research-gitnexus-explorer) | 使用 GitNexus 索引代码库，并通过 Web UI + Cloudflare 隧道提供交互式知识图谱服务。 |
| [**osint-investigation**](/user-guide/skills/optional/research/research-osint-investigation) | 公开记录 OSINT 调查框架 — SEC EDGAR 文件、USAspending 合同、参议院游说、OFAC 制裁、ICIJ 离岸泄露、纽约房产记录 (ACRIS)、OpenCorporates 注册信息、CourtListener 法庭记录、Wayback... |
| [**parallel-cli**](/user-guide/skills/optional/research/research-parallel-cli) | Parallel CLI 的可选供应商技能 — Agent 原生网络搜索、提取、深度研究、数据丰富、FindAll 和监控。优先使用 JSON 输出和非交互式流程。 |
| [**qmd**](/user-guide/skills/optional/research/research-qmd) | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录 — 一个结合 BM25、向量搜索和 LLM 重排序的混合检索引擎。支持 CLI 和 MCP 集成。 |
| [**scrapling**](/user-guide/skills/optional/research/research-scrapling) | 使用 Scrapling 进行网页抓取 — 通过 CLI 和 Python 实现 HTTP 获取、隐身浏览器自动化、Cloudflare 绕过和爬虫抓取。 |
| [**searxng-search**](/user-guide/skills/optional/research/research-searxng-search) | 通过 SearXNG 进行免费元搜索 — 聚合来自 70 多个搜索引擎的结果。可自托管或使用公共实例。无需 API 密钥。当网络搜索工具集不可用时自动回退。 |
<a id="security"></a>
## security

| 技能 | 描述 |
|-------|-------------|
| [**1password**](/user-guide/skills/optional/security/security-1password) | 设置并使用 1Password CLI (op)。适用于安装 CLI、启用桌面应用集成、登录以及为命令读取/注入密钥等场景。 |
| [**oss-forensics**](/user-guide/skills/optional/security/security-oss-forensics) | 针对 GitHub 仓库的供应链调查、证据恢复和取证分析。涵盖已删除提交恢复、强制推送检测、IOC 提取、多源证据收集、假设形成/验证以及... |
| [**sherlock**](/user-guide/skills/optional/security/security-sherlock) | 在 400 多个社交网络上进行 OSINT 用户名搜索。通过用户名追踪社交媒体账号。 |

<a id="software-development"></a>
## software-development

| 技能 | 描述 |
|-------|-------------|
| [**rest-graphql-debug**](/user-guide/skills/optional/software-development/software-development-rest-graphql-debug) | 调试 REST/GraphQL API：状态码、认证、模式、复现。 |

<a id="web-development"></a>
## web-development

| 技能 | 描述 |
|-------|-------------|
| [**page-agent**](/user-guide/skills/optional/web-development/web-development-page-agent) | 将 alibaba/page-agent 嵌入到你的 Web 应用中——这是一个纯 JavaScript 的页面内 GUI Agent，以单个 &lt;script&gt; 标签或 npm 包形式分发，让你的网站最终用户能够通过自然语言驱动界面（例如“点击登录，填写用户名... |

---

<a id="contributing-optional-skills"></a>
## 贡献可选技能

要向仓库添加新的可选技能：

1. 在 `optional-skills/&lt;category&gt;/&lt;skill-name&gt;/` 下创建一个目录
2. 添加一个包含标准 frontmatter（名称、描述、版本、作者）的 `SKILL.md` 文件
3. 在 `references/`、`templates/` 或 `scripts/` 子目录中包含任何支持文件
4. 提交一个拉取请求——该技能将出现在此目录中，并在合并后获得自己的文档页面
