---
slug: /
sidebar_position: 0
title: "Hermes Agent 文档"
description: "由 Nous Research 构建的自进化 AI Agent。内置学习循环，能够从经验中创建技能，在使用过程中不断改进，并跨会话记忆信息。"
hide_table_of_contents: true
---

# Hermes Agent

由 [Nous Research](https://nousresearch.com) 构建的自进化 AI Agent。这是唯一具备内置学习循环的 Agent——它能从经验中创建技能，在使用过程中不断改进，主动强化知识记忆，并随着会话的深入，构建起对你个人偏好的深度模型。

<div style={{display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap'}}>
  <a href="/getting-started/installation" style={{display: 'inline-block', padding: '0.6rem 1.2rem', backgroundColor: '#FFD700', color: '#07070d', borderRadius: '8px', fontWeight: 600, textDecoration: 'none'}}>快速开始 →</a>
  <a href="https://github.com/NousResearch/hermes-agent" style={{display: 'inline-block', padding: '0.6rem 1.2rem', border: '1px solid rgba(255,215,0,0.2)', borderRadius: '8px', textDecoration: 'none'}}>在 GitHub 上查看</a>
</div>

## 什么是 Hermes Agent？

它不是绑定在 IDE 里的编程助手，也不是套在单一 API 上的聊天机器人外壳。它是一个**自主 Agent**，运行时间越长，能力就越强。它可以部署在任何地方——5 美元的 VPS、GPU 集群，或是闲置时几乎零成本的无服务器基础设施（如 Daytona、Modal）。你无需亲自 SSH 登录云端虚拟机，只需通过 Telegram 即可与它交流。它不局限于你的笔记本电脑。

## 快速链接

| | |
|---|---|
| 🚀 **[安装](/getting-started/installation)** | 在 Linux、macOS 或 WSL2 上 60 秒内完成安装 |
| 📖 **[快速入门教程](/getting-started/quickstart)** | 你的首次对话及关键功能体验 |
| 🗺️ **[学习路径](/getting-started/learning-path)** | 根据你的经验水平找到合适的文档 |
| ⚙️ **[配置](/user-guide/configuration)** | 配置文件、提供商、模型及选项设置 |
| 💬 **[消息网关](/user-guide/messaging)** | 设置 Telegram、Discord、Slack 或 WhatsApp |
| 🔧 **[工具与工具集](/user-guide/features/tools)** | 47 种内置工具及其配置方法 |
| 🧠 **[记忆系统](/user-guide/features/memory)** | 可跨会话增长的持久化记忆 |
| 📚 **[技能系统](/user-guide/features/skills)** | Agent 自行创建并复用的程序化记忆 |
| 🔌 **[MCP 集成](/user-guide/features/mcp)** | 连接 MCP 服务器，过滤其工具，并安全地扩展 Hermes |
| 🧭 **[在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)** | 实用的 MCP 设置模式、示例和教程 |
| 🎙️ **[语音模式](/user-guide/features/voice-mode)** | 在 CLI、Telegram、Discord 和 Discord 语音频道中的实时语音交互 |
| 🗣️ **[在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)** | Hermes 语音工作流的动手设置与使用模式 |
| 🎭 **[个性与 SOUL.md](/user-guide/features/personality)** | 通过全局 SOUL.md 定义 Hermes 的默认语音风格 |
| 📄 **[上下文文件](/user-guide/features/context-files)** | 塑造每次对话的项目上下文文件 |
| 🔒 **[安全性](/user-guide/security)** | 命令审批、授权、容器隔离 |
| 💡 **[提示与最佳实践](/guides/tips)** | 充分利用 Hermes 的快速技巧 |
| 🏗️ **[架构](/developer-guide/architecture)** | 其底层工作原理 |
| ❓ **[常见问题与故障排除](/reference/faq)** | 常见问题及解决方案 |

## 核心功能

- **闭环学习** — 由 Agent 策划的记忆，包含定期强化、自主技能创建、使用过程中的技能自优化、基于 FTS5 的跨会话召回（带 LLM 摘要），以及 [Honcho](https://github.com/plastic-labs/honcho) 辩证用户建模。
- **随处运行，不限于笔记本** — 支持 6 种终端后端：local、Docker、SSH、Daytona、Singularity、Modal。Daytona 和 Modal 提供无服务器持久化——环境在闲置时会自动休眠，几乎零成本。
- **无处不在** — CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、Email、SMS、钉钉、飞书、企业微信、BlueBubbles、Home Assistant——通过一个网关即可连接 15+ 平台。
- **由模型训练专家打造** — 由 [Nous Research](https://nousresearch.com) 创建，该实验室也是 Hermes、Nomos 和 Psyche 背后的团队。支持 [Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)、OpenAI 或任何端点。
- **定时自动化** — 内置 cron 任务，可向任何平台发送通知。
- **委派与并行处理** — 生成隔离的子 Agent 以处理并行工作流。通过 `execute_code` 进行程序化工具调用，将多步流水线压缩为单次推理调用。
- **开放标准技能** — 兼容 [agentskills.io](https://agentskills.io)。技能具有可移植性、可共享性，并可通过 Skills Hub 进行社区贡献。
- **全面的 Web 控制** — 搜索、提取、浏览、视觉识别、图像生成、TTS（语音合成）。
- **MCP 支持** — 连接任何 MCP 服务器以获取扩展的工具能力。
- **研究就绪** — 批处理、轨迹导出、使用 Atropos 进行 RL（强化学习）训练。由 [Nous Research](https://nousresearch.com) 构建——该实验室也是 Hermes、Nomos 和 Psyche 模型背后的团队。
