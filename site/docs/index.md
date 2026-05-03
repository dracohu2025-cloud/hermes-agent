---
slug: /
sidebar_position: 0
title: "Hermes Agent 文档"
description: "Nous Research 构建的自我改进型 AI Agent。内置学习循环：从经验中创造技能，在使用中改进技能，跨会话记忆并持续积累。"
hide_table_of_contents: true
displayed_sidebar: docs
---

# Hermes Agent {#hermes-agent}

由 [Nous Research](https://nousresearch.com) 构建的自我改进型 AI Agent。唯一一个内置学习循环的 Agent——它从经验中创造技能，在使用中改进技能，自我驱动以持久化知识，并在多次会话中逐步构建对你的深度理解。

<div style={{display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap'}}>
  <a href="/getting-started/installation" style={{display: 'inline-block', padding: '0.6rem 1.2rem', backgroundColor: '#FFD700', color: '#07070d', borderRadius: '8px', fontWeight: 600, textDecoration: 'none'}}>快速开始 →</a>
  <a href="https://github.com/NousResearch/hermes-agent" style={{display: 'inline-block', padding: '0.6rem 1.2rem', border: '1px solid rgba(255,215,0,0.2)', borderRadius: '8px', textDecoration: 'none'}}>在 GitHub 上查看</a>
</div>

## Hermes Agent 是什么？ {#what-is-hermes-agent}

它不是绑定在 IDE 里的编码助手，也不是围绕单一 API 的聊天机器人封装。它是一个**自主 Agent**，运行时间越长，能力越强。它可以部署在任何地方——一台 5 美元的 VPS、一个 GPU 集群，或者空闲时几乎零成本的无服务器基础设施（Daytona、Modal）。当它在云端 VM 上工作时，你可以通过 Telegram 与它对话，而无需亲自 SSH 登录。它不依赖你的笔记本电脑。

## 快速链接 {#quick-links}

| | |
|---|---|
| 🚀 **[安装](/getting-started/installation)** | 在 Linux、macOS 或 WSL2 上 60 秒完成安装 |
| 📖 **[快速入门教程](/getting-started/quickstart)** | 你的第一次对话和值得尝试的关键功能 |
| 🗺️ **[学习路径](/getting-started/learning-path)** | 根据你的经验水平找到合适的文档 |
| ⚙️ **[配置](/user-guide/configuration)** | 配置文件、提供商、模型和选项 |
| 💬 **[消息网关](/user-guide/messaging)** | 设置 Telegram、Discord、Slack 或 WhatsApp |
| 🔧 **[工具与工具集](/user-guide/features/tools)** | 68 个内置工具及其配置方法 |
| 🧠 **[记忆系统](/user-guide/features/memory)** | 跨会话持续增长的持久记忆 |
| 📚 **[技能系统](/user-guide/features/skills)** | Agent 创建并复用的程序性记忆 |
| 🔌 **[MCP 集成](/user-guide/features/mcp)** | 连接 MCP 服务器、过滤其工具，并安全扩展 Hermes |
| 🧭 **[在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)** | 实用的 MCP 设置模式、示例和教程 |
| 🎙️ **[语音模式](/user-guide/features/voice-mode)** | 在 CLI、Telegram、Discord 和 Discord VC 中实现实时语音交互 |
| 🗣️ **[在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)** | Hermes 语音工作流的实际操作设置与使用模式 |
| 🎭 **[个性与 SOUL.md](/user-guide/features/personality)** | 通过全局 SOUL.md 定义 Hermes 的默认语气 |
| 📄 **[上下文文件](/user-guide/features/context-files)** | 影响每次对话的项目上下文文件 |
| 🔒 **[安全](/user-guide/security)** | 命令审批、授权、容器隔离 |
| 💡 **[提示与最佳实践](/guides/tips)** | 快速上手 Hermes 的小技巧 |
| 🏗️ **[架构](/developer-guide/architecture)** | 底层工作原理 |
| ❓ **[常见问题与故障排除](/reference/faq)** | 常见问题与解决方案 |
## 主要特性 {#key-features}

- **闭环学习** — Agent 管理的记忆，配合定期提示、自主技能创建、使用中的技能自我改进、基于 LLM 摘要的 FTS5 跨会话回忆，以及 [Honcho](https://github.com/plastic-labs/honcho) 辩证用户建模
- **随处运行，不限于笔记本** — 6 种终端后端：本地、Docker、SSH、Daytona、Singularity、Modal。Daytona 和 Modal 提供无服务器持久化——空闲时环境自动休眠，成本几乎为零
- **与你同在** — CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、Email、SMS、钉钉、飞书、企业微信、BlueBubbles、Home Assistant — 一个网关支持 15+ 平台
- **由模型训练者打造** — 由 [Nous Research](https://nousresearch.com) 创建，该实验室也是 Hermes、Nomos 和 Psyche 的幕后团队。兼容 [Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)、OpenAI 或任意端点
- **定时自动化** — 内置 cron，支持投递到任意平台
- **委派与并行** — 生成隔离的子 Agents 以并行处理工作流。通过 `execute_code` 进行编程式工具调用，将多步骤流水线压缩为单次推理调用
- **开放标准技能** — 兼容 [agentskills.io](https://agentskills.io)。技能可移植、可共享，并通过 Skills Hub 由社区贡献
- **完整的 Web 控制** — 搜索、提取、浏览、视觉、图像生成、TTS
- **MCP 支持** — 连接任意 MCP 服务器以扩展工具能力
- **研究就绪** — 批处理、轨迹导出、基于 Atropos 的 RL 训练。由 [Nous Research](https://nousresearch.com) 打造——Hermes、Nomos 和 Psyche 模型的幕后实验室

## 面向 LLM 和编码 Agent {#for-llms-and-coding-agents}

本文档的机器可读入口点：

- **[`/llms.txt`](/llms.txt)** — 所有文档页面的精选索引，附带简短描述。约 17 KB，可安全加载到 LLM 上下文中。
- **[`/llms-full.txt`](/llms-full.txt)** — 所有文档页面拼接成一个 Markdown 文件，便于一次性摄入。约 1.8 MB。

这两个文件也可通过 `/docs/llms.txt` 和 `/docs/llms-full.txt` 访问。每次部署时重新生成。
