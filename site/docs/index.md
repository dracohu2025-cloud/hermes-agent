---
slug: /
sidebar_position: 0
title: "Hermes Agent 文档"
description: "由 Nous Research 打造的自我进化 AI Agent。内置学习循环，能从经验中创建技能、在使用过程中持续优化，并在不同会话间保持记忆。"
hide_table_of_contents: true
displayed_sidebar: docs
---

# Hermes Agent {#hermes-agent}

由 [Nous Research](https://nousresearch.com) 打造的自我进化 AI Agent。唯一内置学习循环的 Agent —— 它能从经验中创建技能，在使用过程中不断优化，主动提醒自己持久化知识，并在多次会话中逐步加深对你的理解。

<div style={{display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap'}}>
  <a href="/getting-started/installation" style={{display: 'inline-block', padding: '0.6rem 1.2rem', backgroundColor: '#FFD700', color: '#07070d', borderRadius: '8px', fontWeight: 600, textDecoration: 'none'}}>开始使用 →</a>
  <a href="https://github.com/NousResearch/hermes-agent" style={{display: 'inline-block', padding: '0.6rem 1.2rem', border: '1px solid rgba(255,215,0,0.2)', borderRadius: '8px', textDecoration: 'none'}}>在 GitHub 上查看</a>
</div>

## Hermes Agent 是什么？ {#what-is-hermes-agent}

它不是拴在 IDE 上的编程助手，也不是套了个聊天壳的单一 API 封装。它是一个**自主 Agent**，运行越久能力越强。你可以把它放在任何地方 —— 5 美元的 VPS、GPU 集群，或者几乎空闲时不花钱的无服务器基础设施（Daytona、Modal）。它在云端 VM 上干活，你根本不用 SSH 进去，自己从 Telegram 跟它对话就行。它不绑在你的笔记本上。

## 快速链接 {#quick-links}

| | |
|---|---|
| 🚀 **[安装](/getting-started/installation)** | 60 秒内在 Linux、macOS 或 WSL2 上完成安装 |
| 📖 **[快速入门教程](/getting-started/quickstart)** | 第一次对话以及值得尝试的核心功能 |
| 🗺️ **[学习路径](/getting-started/learning-path)** | 根据你的经验水平找到合适的文档 |
| ⚙️ **[配置](/user-guide/configuration)** | 配置文件、提供商、模型和选项 |
| 💬 **[消息网关](/user-guide/messaging)** | 设置 Telegram、Discord、Slack 或 WhatsApp |
| 🔧 **[工具与工具集](/user-guide/features/tools)** | 47 个内置工具及配置方法 |
| 🧠 **[记忆系统](/user-guide/features/memory)** | 跨会话持续增长的持久化记忆 |
| 📚 **[技能系统](/user-guide/features/skills)** | Agent 自行创建并复用的程序性记忆 |
| 🔌 **[MCP 集成](/user-guide/features/mcp)** | 连接 MCP 服务器、筛选其工具，安全扩展 Hermes |
| 🧭 **[配合 Hermes 使用 MCP](/guides/use-mcp-with-hermes)** | 实用的 MCP 配置模式、示例和教程 |
| 🎙️ **[语音模式](/user-guide/features/voice-mode)** | 在 CLI、Telegram、Discord 及 Discord 语音频道中实时语音交互 |
| 🗣️ **[配合 Hermes 使用语音模式](/guides/use-voice-mode-with-hermes)** | Hermes 语音工作流的动手配置与使用模式 |
| 🎭 **[个性与 SOUL.md](/user-guide/features/personality)** | 通过全局 SOUL.md 定义 Hermes 的默认风格 |
| 📄 **[上下文文件](/user-guide/features/context-files)** | 塑造每次对话的项目上下文文件 |
| 🔒 **[安全](/user-guide/security)** | 命令审批、授权机制、容器隔离 |
| 💡 **[技巧与最佳实践](/guides/tips)** | 快速上手、充分发挥 Hermes 潜力的窍门 |
| 🏗️ **[架构](/developer-guide/architecture)** | 底层工作原理 |
| ❓ **[常见问题与故障排查](/reference/faq)** | 常见疑问与解决方案 |

## 核心特性 {#key-features}

- **闭环学习** —— Agent 自主管理的记忆，配合周期性提醒；自主创建技能、使用过程中自我优化；基于 FTS5 的跨会话召回结合 LLM 摘要；以及 [Honcho](https://github.com/plastic-labs/honcho) 辩证式用户建模
- **随处运行，不限于笔记本** —— 6 种终端后端：本地、Docker、SSH、Daytona、Singularity、Modal。Daytona 和 Modal 提供无服务器持久化 —— 空闲时环境休眠，几乎不产生费用
- **在你常驻的地方待命** —— CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、邮件、短信、钉钉、飞书、企业微信、BlueBubbles、Home Assistant —— 一个网关覆盖 15+ 平台
- **模型训练者打造** —— 由 [Nous Research](https://nousresearch.com) 创建，这家实验室打造了 Hermes、Nomos 和 Psyche。兼容 [Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)、OpenAI 或任意端点
- **定时自动化** —— 内置 cron，可向任意平台推送
- **委派与并行** —— 生成隔离的 sub-agent 实现并行工作流。通过 `execute_code` 进行程序化工具调用，将多步流水线压缩为单次推理调用
- **开放标准技能** —— 兼容 [agentskills.io](https://agentskills.io)。技能可移植、可分享，通过 Skills Hub 由社区贡献
- **完整的网页操控** —— 搜索、提取、浏览、视觉、图像生成、TTS
- **MCP 支持** —— 连接任意 MCP 服务器以扩展工具能力
- **为研究而生** —— 批处理、轨迹导出、使用 Atropos 进行 RL 训练。由 [Nous Research](https://nousresearch.com) 打造 —— Hermes、Nomos 和 Psyche 模型的幕后实验室
