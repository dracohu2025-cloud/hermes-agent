---
title: "功能概览"
sidebar_label: "概览"
sidebar_position: 1
---

# 功能概览

Hermes Agent 包含一套丰富的功能集，其能力远超基础聊天。从持久化记忆、文件感知上下文到浏览器自动化和语音对话，这些功能协同工作，使 Hermes 成为一个强大的自主助手。

## 核心功能

- **[工具与工具集 (Tools & Toolsets)](tools.md)** — 工具是扩展 Agent 能力的函数。它们被组织成逻辑工具集，可以按平台启用或禁用，涵盖网络搜索、终端执行、文件编辑、记忆、任务委派等。
- **[技能系统 (Skills System)](skills.md)** — Agent 在需要时可以加载的按需知识文档。技能遵循渐进式披露模式以最小化 Token 消耗，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。
- **[持久化记忆 (Persistent Memory)](memory.md)** — 跨会话持久存在的有界、精选记忆。Hermes 会通过 `MEMORY.md` 和 `USER.md` 记住你的偏好、项目、环境以及它学到的东西。
- **[上下文文件 (Context Files)](context-files.md)** — Hermes 会自动发现并加载项目上下文文件（`.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`SOUL.md`、`.cursorrules`），这些文件决定了它在项目中的行为方式。
- **[上下文引用 (Context References)](context-references.md)** — 输入 `@` 后跟引用内容，可直接将文件、文件夹、git diff 和 URL 注入到消息中。Hermes 会在行内展开引用并自动附加内容。
- **[检查点 (Checkpoints)](../checkpoints-and-rollback.md)** — Hermes 在修改文件前会自动对工作目录进行快照，如果出现问题，你可以通过 `/rollback` 进行回滚，为你提供安全保障。

## 自动化

- **[定时任务 (Cron)](cron.md)** — 使用自然语言或 cron 表达式安排任务自动运行。任务可以附加技能，将结果交付到任何平台，并支持暂停/恢复/编辑操作。
- **[子 Agent 委派 (Subagent Delegation)](delegation.md)** — `delegate_task` 工具可以生成具有隔离上下文、受限工具集和独立终端会话的子 Agent 实例。最多可同时运行 3 个并发子 Agent 以处理并行工作流。
- **[代码执行 (Code Execution)](code-execution.md)** — `execute_code` 工具允许 Agent 编写 Python 脚本，通过程序化方式调用 Hermes 工具，通过沙箱化的 RPC 执行将多步工作流压缩到单个 LLM 轮次中。
- **[事件钩子 (Event Hooks)](hooks.md)** — 在关键生命周期节点运行自定义代码。网关钩子（Gateway hooks）处理日志、警报和 Webhook；插件钩子（Plugin hooks）处理工具拦截、指标和护栏。
- **[批处理 (Batch Processing)](batch-processing.md)** — 在成百上千个 Prompt 中并行运行 Hermes Agent，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。

## 多媒体与网络

- **[语音模式 (Voice Mode)](voice-mode.md)** — 跨 CLI 和消息平台的完整语音交互。使用麦克风与 Agent 交谈，听取语音回复，并在 Discord 语音频道中进行实时语音对话。
- **[浏览器自动化 (Browser Automation)](browser.md)** — 支持多种后端的完整浏览器自动化：Browserbase 云端、Browser Use 云端、通过 CDP 连接的本地 Chrome 或本地 Chromium。导航网站、填写表单并提取信息。
- **[视觉与图片粘贴 (Vision & Image Paste)](vision.md)** — 多模态视觉支持。将剪贴板中的图片粘贴到 CLI 中，并要求 Agent 使用任何具备视觉能力的模型对其进行分析、描述或处理。
- **[图像生成 (Image Generation)](image-generation.md)** — 使用 FAL.ai 的 FLUX 2 Pro 模型根据文本提示生成图像，并通过 Clarity Upscaler 自动进行 2 倍超分辨率放大。
- **[语音与 TTS (Voice & TTS)](tts.md)** — 跨所有消息平台的文本转语音输出和语音消息转录，提供五个供应商选项：Edge TTS（免费）、ElevenLabs、OpenAI TTS、MiniMax 和 NeuTTS。

## 集成

- **[MCP 集成](mcp.md)** — 通过 stdio 或 HTTP 传输连接到任何 MCP 服务器。无需编写原生 Hermes 工具即可访问来自 GitHub、数据库、文件系统和内部 API 的外部工具。支持按服务器进行工具过滤和采样。
- **[供应商路由 (Provider Routing)](provider-routing.md)** — 精细控制由哪些 AI 供应商处理你的请求。通过排序、白名单、黑名单和优先级排序，针对成本、速度或质量进行优化。
- **[备用供应商 (Fallback Providers)](fallback-providers.md)** — 当主模型遇到错误时，自动故障转移到备用 LLM 供应商，包括为视觉和压缩等辅助任务提供独立的备用方案。
- **[凭据池 (Credential Pools)](credential-pools.md)** — 将 API 调用分配到同一供应商的多个 Key 上。在达到速率限制或发生故障时自动轮换。
- **[记忆供应商 (Memory Providers)](memory-providers.md)** — 接入外部记忆后端（Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover），实现超出内置记忆系统的跨会话用户建模和个性化。
- **[API 服务器 (API Server)](api-server.md)** — 将 Hermes 作为兼容 OpenAI 的 HTTP 端点暴露。连接任何支持 OpenAI 格式的前端 —— Open WebUI、LobeChat、LibreChat 等。
- **[IDE 集成 (ACP)](acp.md)** — 在兼容 ACP 的编辑器（如 VS Code、Zed 和 JetBrains）中使用 Hermes。聊天、工具活动、文件 diff 和终端命令都会在编辑器内渲染。
- **[强化学习训练 (RL Training)](rl-training.md)** — 从 Agent 会话中生成轨迹数据，用于强化学习和模型微调。

## 自定义

- **[人格与 SOUL.md (Personality & SOUL.md)](personality.md)** — 完全可定制的 Agent 人格。`SOUL.md` 是核心身份文件 —— 系统提示词中的第一项内容 —— 你可以在每个会话中切换内置或自定义的 `/personality` 预设。
- **[皮肤与主题 (Skins & Themes)](skins.md)** — 自定义 CLI 的视觉呈现：横幅颜色、加载动画（spinner）样式和动词、响应框标签、品牌文本以及工具活动前缀。
- **[插件 (Plugins)](plugins.md)** — 无需修改核心代码即可添加自定义工具、钩子和集成。只需将包含 `plugin.yaml` 和 Python 代码的目录放入 `~/.hermes/plugins/` 即可。
