---
slug: /
sidebar_position: 0
title: "Hermes Agent 文档"
description: "由 Nous Research 构建的自我改进型 AI Agent。内置学习循环，能从经验中创造技能，在使用中改进技能，并在会话间保持记忆。"
hide_table_of_contents: true
displayed_sidebar: docs
---

<a id="hermes-agent"></a>
# Hermes Agent

由 [Nous Research](https://nousresearch.com) 构建的自我改进型 AI Agent。唯一一个内置学习循环的 Agent——它能从经验中创造技能，在使用中改进技能，主动保持知识持久化，并在多次会话中逐步构建对你的深入理解。

<div style={{display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap'}}>
  <a href="/getting-started/installation" style={{display: 'inline-block', padding: '0.6rem 1.2rem', backgroundColor: '#FFD700', color: '#07070d', borderRadius: '8px', fontWeight: 600, textDecoration: 'none'}}>快速开始 →</a>
  <a href="https://github.com/NousResearch/hermes-agent" style={{display: 'inline-block', padding: '0.6rem 1.2rem', border: '1px solid rgba(255,215,0,0.2)', borderRadius: '8px', textDecoration: 'none'}}>在 GitHub 上查看</a>
</div>

<a id="install"></a>
## 安装

**Linux / macOS / WSL2**

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

**Windows（原生，PowerShell）** — *早期测试版，[详情 →](/user-guide/windows-native)*

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

**Android（Termux）** — 与 Linux 相同的 curl 单行命令；安装程序会自动检测 Termux。

有关安装程序的具体操作、单用户与 root 布局的区别以及 Windows 专属说明，请参阅完整的 **[安装指南](/getting-started/installation)**。

<a id="what-is-hermes-agent"></a>
## Hermes Agent 是什么？

它不是绑定在 IDE 里的编码助手，也不是围绕单个 API 的聊天机器人封装。它是一个**自主 Agent**，运行时间越长，能力越强。它可以部署在任何地方——一台 5 美元的 VPS、一个 GPU 集群，或者空闲时几乎不花钱的无服务器基础设施（Daytona、Modal）。当它在云端 VM 上工作时，你可以通过 Telegram 与它对话，而无需自己 SSH 登录。它不依赖于你的笔记本电脑。

<a id="quick-links"></a>
## 快速链接

| | |
|---|---|
| 🚀 **[安装](/getting-started/installation)** | 在 Linux、macOS、WSL2 或原生 Windows（早期测试版）上 60 秒完成安装 |
| 📖 **[快速入门教程](/getting-started/quickstart)** | 你的第一次对话以及值得尝试的关键功能 |
| 🗺️ **[学习路径](/getting-started/learning-path)** | 根据你的经验水平找到合适的文档 |
| ⚙️ **[配置](/user-guide/configuration)** | 配置文件、提供商、模型和选项 |
| 💬 **[消息网关](/user-guide/messaging)** | 设置 Telegram、Discord、Slack、WhatsApp、Teams 等 |
| 🔧 **[工具与工具集](/user-guide/features/tools)** | 70 多个内置工具及其配置方法 |
| 🧠 **[记忆系统](/user-guide/features/memory)** | 跨会话增长的持久化记忆 |
| 📚 **[技能系统](/user-guide/features/skills)** | Agent 创建并复用的程序化记忆 |
| 🔌 **[MCP 集成](/user-guide/features/mcp)** | 连接 MCP 服务器、过滤其工具，并安全扩展 Hermes |
| 🧭 **[将 MCP 与 Hermes 结合使用](/guides/use-mcp-with-hermes)** | 实用的 MCP 设置模式、示例和教程 |
| 🎙️ **[语音模式](/user-guide/features/voice-mode)** | 在 CLI、Telegram、Discord 和 Discord VC 中实现实时语音交互 |
| 🗣️ **[将语音模式与 Hermes 结合使用](/guides/use-voice-mode-with-hermes)** | Hermes 语音工作流的实操设置与使用模式 |
| 🎭 **[个性与 SOUL.md](/user-guide/features/personality)** | 通过全局 SOUL.md 定义 Hermes 的默认语气 |
| 📄 **[上下文文件](/user-guide/features/context-files)** | 影响每次对话的项目上下文文件 |
| 🔒 **[安全](/user-guide/security)** | 命令审批、授权、容器隔离 |
| 💡 **[提示与最佳实践](/guides/tips)** | 快速上手，充分发挥 Hermes 的能力 |
| 🏗️ **[架构](/developer-guide/architecture)** | 底层工作原理 |
| ❓ **[常见问题与故障排除](/reference/faq)** | 常见问题与解决方案 |
<a id="key-features"></a>
## 主要特点

- **闭环学习**——Agent 管理的记忆机制，包含周期性提示、自主技能创建、使用中技能自我改进、基于 FTS5 的跨会话召回（附带 LLM 摘要），以及 [Honcho](https://github.com/plastic-labs/honcho) 辩证用户建模
- **随处运行，不止于笔记本**——6 种终端后端：本地、Docker、SSH、Daytona、Singularity、Modal。Daytona 和 Modal 提供无服务器持久化——闲置时环境进入休眠，几乎零成本
- **与你同驻**——CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、Email、SMS、钉钉、飞书、企业微信、微信、QQ 机器人、元宝、BlueBubbles、Home Assistant、Microsoft Teams、Google Chat 等——单一网关覆盖 20+ 平台
- **由模型训练者打造**——由 [Nous Research](https://nousresearch.com) 创建，该实验室也是 Hermes、Nomos 和 Psyche 模型的幕后团队。可与 [Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)、OpenAI 或任意端点配合使用
- **计划自动化**——内置 cron，支持投递到任何平台
- **委派与并行**——生成隔离的子 Agents 以并行处理工作流。通过 `execute_code` 进行程序化工具调用，将多步骤流程压缩为单次推理调用
- **开放式标准技能**——兼容 [agentskills.io](https://agentskills.io)。技能可移植、可共享，并通过 Skills Hub 由社区贡献
- **完整的 Web 控制**——搜索、提取、浏览、视觉、图像生成、TTS
- **MCP 支持**——连接任意 MCP 服务器以扩展工具能力
- **可投入研究**——批量处理、轨迹导出、基于 Atropos 的强化学习训练。由 [Nous Research](https://nousresearch.com) 构建——该实验室也打造了 Hermes、Nomos 和 Psyche 模型

<a id="for-llms-and-coding-agents"></a>
## 面向 LLM 和编码 Agent

本文档的机器可读入口点：

- **[`/llms.txt`](/llms.txt)** —— 所有文档页面的精选索引，含简短描述。约 17 KB，可安全加载到 LLM 上下文中。
- **[`/llms-full.txt`](/llms-full.txt)** —— 所有文档页面拼接成单个 Markdown 文件，便于一次性摄入。约 1.8 MB。

这两个文件在 `/docs/llms.txt` 和 `/docs/llms-full.txt` 也可访问。每次部署时重新生成。
