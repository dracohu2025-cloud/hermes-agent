---
slug: /
sidebar_position: 0
title: "Hermes Agent 文档"
description: "由 Nous Research 构建的具有自我进化能力的 AI Agent。内置学习闭环，能从经验中创造技能，在使用中不断改进，并实现跨会话记忆。"
hide_table_of_contents: true
---

# Hermes Agent

由 [Nous Research](https://nousresearch.com) 构建的具有自我进化能力的 AI Agent。它是唯一内置学习闭环的 Agent —— 它能从经验中创造技能，在使用过程中改进技能，提醒自己持久化知识，并在不同会话间构建一个关于“你是谁”的深度模型。

<div style={{display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap'}}>
  <a href="/getting-started/installation" style={{display: 'inline-block', padding: '0.6rem 1.2rem', backgroundColor: '#FFD700', color: '#07070d', borderRadius: '8px', fontWeight: 600, textDecoration: 'none'}}>立即开始 →</a>
  <a href="https://github.com/NousResearch/hermes-agent" style={{display: 'inline-block', padding: '0.6rem 1.2rem', border: '1px solid rgba(255,215,0,0.2)', borderRadius: '8px', textDecoration: 'none'}}>在 GitHub 上查看</a>
</div>

## 什么是 Hermes Agent？

它不是绑定在 IDE 上的编程副驾驶（copilot），也不是套壳单个 API 的聊天机器人。它是一个**自主 Agent**，运行时间越长，能力就越强。它可以部署在任何地方 —— 5 美元的 VPS、GPU 集群，或者几乎不产生闲置成本的无服务器基础设施（Daytona、Modal）。当它在云端虚拟机上工作时，你可以通过 Telegram 与它交流，而无需亲自 SSH 登录。它不依赖于你的笔记本电脑。

## 快速链接

| | |
|---|---|
| 🚀 **[安装指南](/getting-started/installation)** | 在 Linux、macOS 或 WSL2 上 60 秒完成安装 |
| 📖 **[快速上手教程](/getting-started/quickstart)** | 开启你的第一次对话并尝试核心功能 |
| 🗺️ **[学习路径](/getting-started/learning-path)** | 根据你的经验水平找到合适的文档 |
| ⚙️ **[配置说明](/user-guide/configuration)** | 配置文件、供应商、模型及选项设置 |
| 💬 **[消息网关](/user-guide/messaging)** | 设置 Telegram、Discord、Slack 或 WhatsApp |
| 🔧 **[工具与工具集](/user-guide/features/tools)** | 47 个内置工具及其配置方法 |
| 🧠 **[记忆系统](/user-guide/features/memory)** | 随会话增长的持久化记忆 |
| 📚 **[技能系统](/user-guide/features/skills)** | Agent 自行创建并复用的程序化记忆 |
| 🔌 **[MCP 集成](/user-guide/features/mcp)** | 连接 MCP 服务器，过滤工具并安全扩展 Hermes |
| 🧭 **[在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)** | 实际的 MCP 设置模式、示例和教程 |
| 🎙️ **[语音模式](/user-guide/features/voice-mode)** | 在 CLI、Telegram、Discord 及 Discord 语音频道中进行实时语音交互 |
| 🗣️ **[在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)** | Hermes 语音工作流的实操设置与使用模式 |
| 🎭 **[个性与 SOUL.md](/user-guide/features/personality)** | 通过全局 SOUL.md 定义 Hermes 的默认人设 |
| 📄 **[上下文文件](/user-guide/features/context-files)** | 影响每一次对话的项目上下文文件 |
| 🔒 **[安全机制](/user-guide/security)** | 命令审批、授权及容器隔离 |
| 💡 **[技巧与最佳实践](/guides/tips)** | 充分发挥 Hermes 效能的捷径 |
| 🏗️ **[架构设计](/developer-guide/architecture)** | 深入了解底层运行机制 |
| ❓ **[常见问题与排障](/reference/faq)** | 常见问题解答与解决方案 |

## 核心特性

- **闭环学习系统** —— Agent 策划的记忆并带有周期性提醒、自主技能创建、使用中的技能自我改进、基于 FTS5 的跨会话召回（配合 LLM 总结），以及基于 [Honcho](https://github.com/plastic-labs/honcho) 的辩证用户建模。
- **随处运行，不限于本地** —— 支持 6 种终端后端：local、Docker、SSH、Daytona、Singularity、Modal。Daytona 和 Modal 提供无服务器持久化 —— 你的环境在闲置时会休眠，几乎不产生费用。
- **融入你的生活** —— 支持 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、Email、SMS、钉钉、飞书、企业微信、Home Assistant —— 通过一个网关连接 14+ 个平台。
- **由模型训练专家打造** —— 由 [Nous Research](https://nousresearch.com) 开发，该实验室也是 Hermes、Nomos 和 Psyche 系列模型的幕后团队。支持 [Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)、OpenAI 或任何 API 端点。
- **定时自动化** —— 内置 cron 定时任务，可将结果推送到任何平台。
- **任务委派与并行** —— 派生隔离的 sub-agents 以处理并行工作流。通过 `execute_code` 进行程序化工具调用，将多步流水线压缩为单次推理调用。
- **开放标准技能** —— 兼容 [agentskills.io](https://agentskills.io)。技能具有可移植性，可分享，并可通过 Skills Hub 由社区贡献。
- **全面的 Web 控制** —— 搜索、提取、浏览、视觉识别、图像生成、TTS。
- **MCP 支持** —— 连接到任何 MCP 服务器以扩展工具能力。
- **研究就绪** —— 支持批处理、轨迹导出、使用 Atropos 进行 RL 训练。由 [Nous Research](https://nousresearch.com) 构建 —— 该实验室以 Hermes、Nomos 和 Psyche 模型闻名。
