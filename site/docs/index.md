---
slug: /
sidebar_position: 0
title: "Hermes Agent 文档"
description: "由 Nous Research 构建的自我改进 AI 智能体。内置学习循环，可从经验中创建技能，在使用中改进它们，并在不同会话间保持记忆。"
hide_table_of_contents: true
---

# Hermes Agent

由 [Nous Research](https://nousresearch.com) 构建的自我改进 AI 智能体。唯一内置学习循环的智能体——它从经验中创建技能，在使用中改进它们，推动自身持久化知识，并在不同会话间逐步构建关于你的深层模型。

<div style={{display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap'}}>
  <a href="/docs/getting-started/installation" style={{display: 'inline-block', padding: '0.6rem 1.2rem', backgroundColor: '#FFD700', color: '#07070d', borderRadius: '8px', fontWeight: 600, textDecoration: 'none'}}>开始使用 →</a>
  <a href="https://github.com/NousResearch/hermes-agent" style={{display: 'inline-block', padding: '0.6rem 1.2rem', border: '1px solid rgba(255,215,0,0.2)', borderRadius: '8px', textDecoration: 'none'}}>在 GitHub 上查看</a>
</div>

## 什么是 Hermes Agent？

它不是绑定在 IDE 上的编程助手，也不是围绕单一 API 的聊天机器人外壳。它是一个**自主智能体**，运行时间越长，能力越强。它可以部署在任何地方——5 美元的 VPS、GPU 集群，或是闲置时几乎不花钱的无服务器基础设施（Daytona、Modal）。当它在你从未亲自 SSH 登录的云虚拟机上工作时，你可以通过 Telegram 与它对话。它不绑定在你的笔记本电脑上。

## 快速链接

| | |
|---|---|
| 🚀 **[安装](/docs/getting-started/installation)** | 在 Linux、macOS 或 WSL2 上 60 秒内完成安装 |
| 📖 **[快速入门教程](/docs/getting-started/quickstart)** | 你的第一次对话及需要尝试的关键功能 |
| 🗺️ **[学习路径](/docs/getting-started/learning-path)** | 根据你的经验水平找到合适的文档 |
| ⚙️ **[配置](/docs/user-guide/configuration)** | 配置文件、提供商、模型和选项 |
| 💬 **[消息网关](/docs/user-guide/messaging)** | 设置 Telegram、Discord、Slack 或 WhatsApp |
| 🔧 **[工具与工具集](/docs/user-guide/features/tools)** | 40 多个内置工具及其配置方法 |
| 🧠 **[记忆系统](/docs/user-guide/features/memory)** | 跨会话增长的持久化记忆 |
| 📚 **[技能系统](/docs/user-guide/features/skills)** | 智能体创建并重用的程序性记忆 |
| 🔌 **[MCP 集成](/docs/user-guide/features/mcp)** | 连接到 MCP 服务器，过滤其工具，并安全地扩展 Hermes |
| 🧭 **[在 Hermes 中使用 MCP](/docs/guides/use-mcp-with-hermes)** | 实用的 MCP 设置模式、示例和教程 |
| 🎙️ **[语音模式](/docs/user-guide/features/voice-mode)** | 在 CLI、Telegram、Discord 和 Discord VC 中进行实时语音交互 |
| 🗣️ **[在 Hermes 中使用语音模式](/docs/guides/use-voice-mode-with-hermes)** | Hermes 语音工作流的实践设置和使用模式 |
| 🎭 **[个性与 SOUL.md](/docs/user-guide/features/personality)** | 通过全局 SOUL.md 定义 Hermes 的默认声音 |
| 📄 **[上下文文件](/docs/user-guide/features/context-files)** | 塑造每次对话的项目上下文文件 |
| 🔒 **[安全性](/docs/user-guide/security)** | 命令批准、授权、容器隔离 |
| 💡 **[技巧与最佳实践](/docs/guides/tips)** | 快速上手，充分利用 Hermes |
| 🏗️ **[架构](/docs/developer-guide/architecture)** | 底层工作原理 |
| ❓ **[常见问题与故障排除](/docs/reference/faq)** | 常见问题及解决方案 |

## 主要特性

- **闭环学习循环** — 智能体管理的记忆，带有周期性提示、自主技能创建、使用中的技能自我改进、基于 FTS5 的跨会话检索与 LLM 摘要，以及 [Honcho](https://github.com/plastic-labs/honcho) 辩证用户建模
- **随处运行，不限于你的笔记本电脑** — 6 种终端后端：本地、Docker、SSH、Daytona、Singularity、Modal。Daytona 和 Modal 提供无服务器持久化——你的环境在闲置时休眠，几乎不产生费用
- **与你同在** — CLI、Telegram、Discord、Slack、WhatsApp，全部通过一个网关接入
- **由模型训练者构建** — 由 [Nous Research](https://nousresearch.com) 创建，该实验室是 Hermes、Nomos 和 Psyche 模型背后的团队。支持 [Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)、OpenAI 或任何端点
- **计划任务自动化** — 内置 cron，可将结果发送到任何平台
- **委派与并行化** — 生成隔离的子智能体以处理并行工作流。通过 `execute_code` 的程序化工具调用可将多步骤流水线压缩为单次推理调用
- **开放标准技能** — 兼容 [agentskills.io](https://agentskills.io)。技能是可移植、可共享的，并通过技能中心由社区贡献
- **完整的网络控制** — 搜索、提取、浏览、视觉、图像生成、TTS
- **MCP 支持** — 连接到任何 MCP 服务器以扩展工具能力
- **为研究准备** — 批处理、轨迹导出、使用 Atropos 进行 RL 训练。由 [Nous Research](https://nousresearch.com) 构建——Hermes、Nomos 和 Psyche 模型背后的实验室
