---
sidebar_position: 6
title: "官方可选技能目录"
description: "仓库中可用的官方可选技能目录"
---

# 官方可选技能目录

官方可选技能位于仓库的 `optional-skills/` 目录下。使用 `hermes skills install official/<category>/<skill>` 命令安装，或使用 `hermes skills browse --source official` 命令浏览。

## autonomous-ai-agents

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `blackbox` | 将编码任务委托给 Blackbox AI CLI 智能体。这是一个多模型智能体，内置评判机制，可通过多个 LLM 运行任务并选择最佳结果。需要 blackbox CLI 和 Blackbox AI API 密钥。 | `autonomous-ai-agents/blackbox` |

## blockchain

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `base` | 查询 Base（以太坊 L2）区块链数据，并提供美元计价信息 —— 包括钱包余额、代币信息、交易详情、Gas 分析和合约检查。 | `blockchain/base` |
| `solana` | 查询 Solana 区块链数据，并提供美元计价信息 —— 包括钱包余额、带估值的代币组合、交易详情、NFT、巨鲸检测和实时网络统计。使用 Solana RPC + CoinGecko。无需 API 密钥。 | `blockchain/solana` |

## creative

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `blender-mcp` | 通过 socket 连接到 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python 脚本。 | `creative/blender-mcp` |
| `meme-generation` | 通过选择模板并使用 Pillow 叠加文本来生成真实的梗图。生成实际的 .png 梗图文件。 | `creative/meme-generation` |

## email

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `agentmail` | 通过 AgentMail 为智能体提供其专属的电子邮件收件箱。使用智能体拥有的电子邮件地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理电子邮件。 | `email/agentmail` |

## health

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `neuroskill-bci` | 连接到正在运行的 NeuroSkill 实例，并将用户的实时认知和情绪状态（专注度、放松度、情绪、认知负荷、困倦度、心率、HRV、睡眠分期以及 40 多种衍生的 EXG 评分）整合到响应中。需要 BCI 可穿戴设备（Muse 2/S 或 Open… | `health/neuroskill-bci` |

## mcp

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `fastmcp` | 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。 | `mcp/fastmcp` |

## migration

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `openclaw-migration` | 将用户的 OpenClaw 自定义配置迁移到 Hermes Agent。从 ~/.openclaw 导入与 Hermes 兼容的记忆、SOUL.md、命令允许列表、用户技能和选定的工作空间资源，然后报告哪些内容无法迁移及其原因。 | `migration/openclaw-migration` |

## productivity

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `telephony` | 为 Hermes 提供电话功能 —— 配置 Twilio 号码、发送/接收 SMS/MMS、直接拨打电话，以及通过 Bland.ai 或 Vapi 进行 AI 驱动的外呼。 | `productivity/telephony` |

## research

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `bioinformatics` | 通往 bioSkills 和 ClawBio 提供的 400 多种生物信息学技能的入口。涵盖基因组学、转录组学、单细胞分析、变异检测、药物基因组学、宏基因组学、结构生物学。 | `research/bioinformatics` |
| `qmd` | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录 —— qmd 是一个混合检索引擎，结合了 BM25、向量搜索和 LLM 重排序。支持 CLI 和 MCP 集成。 | `research/qmd` |

## security

| 技能 | 描述 | 路径 |
|-------|-------------|------|
| `1password` | 设置和使用 1Password CLI (op)。用于安装 CLI、启用桌面应用集成、登录以及为命令读取/注入密钥。 | `security/1password` |
| `oss-forensics` | 为 GitHub 仓库提供供应链调查、证据恢复和取证分析。涵盖已删除提交的恢复、强制推送检测、IOC 提取。 | `security/oss-forensics` |
| `sherlock` | 在 400 多个社交网络上进行 OSINT 用户名搜索。通过用户名追踪社交媒体账户。 | `security/sherlock` |
