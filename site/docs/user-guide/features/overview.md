---
title: "功能概览"
sidebar_label: "概览"
sidebar_position: 1
---

# 功能概览

Hermes Agent 包含一套丰富的功能，其能力远超基础聊天。从持久化记忆和具备文件感知能力的上下文，到浏览器自动化和语音对话，这些功能协同工作，使 Hermes 成为强大的自主助手。

## 核心功能

- **[工具与工具集](tools.md)** — 工具是扩展 Agent 能力的函数。它们被组织成逻辑工具集，可以按平台启用或禁用，涵盖网页搜索、终端执行、文件编辑、记忆、任务委派等。
- **[技能系统](skills.md)** — Agent 可在需要时按需加载的知识文档。技能遵循渐进式披露模式以最小化 Token 使用，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。
- **[持久化记忆](memory.md)** — 跨会话持久存在的、有边界的精选记忆。Hermes 会通过 `MEMORY.md` 和 `USER.md` 记住你的偏好、项目、环境以及它所学到的内容。
- **[上下文文件](context-files.md)** — Hermes 会自动发现并加载项目上下文文件（`.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`SOUL.md`、`.cursorrules`），这些文件决定了它在你的项目中的行为方式。
- **[上下文引用](context-references.md)** — 输入 `@` 后跟引用内容，即可将文件、文件夹、git diff 和 URL 直接注入到你的消息中。Hermes 会自动展开引用并附加内容。
- **[检查点](../checkpoints-and-rollback.md)** — Hermes 在进行文件更改前会自动对工作目录进行快照，为你提供安全保障，如果出现问题，可以使用 `/rollback` 进行回滚。

## 自动化

- **[定时任务 (Cron)](cron.md)** — 使用自然语言或 cron 表达式安排自动运行的任务。任务可以附加技能、将结果发送到任何平台，并支持暂停、恢复和编辑操作。
- **[子 Agent 委派](delegation.md)** — `delegate_task` 工具可以生成具有隔离上下文、受限工具集和独立终端会话的子 Agent 实例。最多可同时运行 3 个子 Agent 进行并行工作流处理。
- **[代码执行](code-execution.md)** — `execute_code` 工具允许 Agent 编写 Python 脚本以编程方式调用 Hermes 工具，通过沙箱 RPC 执行，将多步工作流压缩为单次 LLM 交互。
- **[事件钩子](hooks.md)** — 在关键生命周期节点运行自定义代码。网关钩子处理日志记录、警报和 Webhook；插件钩子处理工具拦截、指标和防护措施。
- **[批量处理](batch-processing.md)** — 在成百上千个提示词上并行运行 Hermes Agent，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。

## 媒体与网页

- **[语音模式](voice-mode.md)** — 跨 CLI 和消息平台的完整语音交互。使用麦克风与 Agent 对话、收听语音回复，并在 Discord 语音频道中进行实时语音交流。
- **[浏览器自动化](browser.md)** — 具备多种后端的完整浏览器自动化：Browserbase 云、Browser Use 云、通过 CDP 连接的本地 Chrome 或本地 Chromium。可以浏览网站、填写表单并提取信息。
- **[视觉与图片粘贴](vision.md)** — 多模态视觉支持。将剪贴板中的图片粘贴到 CLI 中，并要求 Agent 使用任何具备视觉能力的模型进行分析、描述或处理。
- **[图像生成](image-generation.md)** — 使用 FAL.ai 的 FLUX 2 Pro 模型，通过 Clarity Upscaler 自动进行 2 倍放大，根据文本提示生成图像。
- **[语音与 TTS](tts.md)** — 跨所有消息平台的文本转语音输出和语音消息转录，提供五种选项：Edge TTS（免费）、ElevenLabs、OpenAI TTS、MiniMax 和 NeuTTS。

## 集成

- **[MCP 集成](mcp.md)** — 通过 stdio 或 HTTP 传输连接到任何 MCP 服务器。无需编写原生 Hermes 工具即可访问来自 GitHub、数据库、文件系统和内部 API 的外部工具。包含针对每个服务器的工具过滤和采样支持。
- **[提供商路由](provider-routing.md)** — 对处理请求的 AI 提供商进行精细化控制。通过排序、白名单、黑名单和优先级设置，优化成本、速度或质量。
- **[回退提供商](fallback-providers.md)** — 当主模型遇到错误时，自动故障转移到备用 LLM 提供商，包括针对视觉和压缩等辅助任务的独立回退机制。
- **[凭据池](credential-pools.md)** — 将 API 调用分发到同一提供商的多个密钥上。在达到速率限制或发生故障时自动轮换。
- **[记忆提供商](memory-providers.md)** — 接入外部记忆后端（Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover），实现超越内置记忆系统的跨会话用户建模和个性化。
- **[API 服务器](api-server.md)** — 将 Hermes 暴露为兼容 OpenAI 的 HTTP 端点。连接任何支持 OpenAI 格式的前端，如 Open WebUI、LobeChat、LibreChat 等。
- **[IDE 集成 (ACP)](acp.md)** — 在兼容 ACP 的编辑器（如 VS Code、Zed 和 JetBrains）中使用 Hermes。聊天记录、工具活动、文件差异和终端命令都会在编辑器内渲染。
- **[强化学习训练](rl-training.md)** — 从 Agent 会话中生成轨迹数据，用于强化学习和模型微调。

## 自定义

- **[个性化与 SOUL.md](personality.md)** — 完全可自定义的 Agent 个性。`SOUL.md` 是主要的身份文件（系统提示词的第一部分），你可以在每个会话中切换内置或自定义的 `/personality` 预设。
- **[皮肤与主题](skins.md)** — 自定义 CLI 的视觉呈现：横幅颜色、加载动画图标和动词、响应框标签、品牌文本以及工具活动前缀。
- **[插件](plugins.md)** — 在不修改核心代码的情况下添加自定义工具、钩子和集成。三种插件类型：通用插件（工具/钩子）、记忆提供商（跨会话知识）和上下文引擎（替代上下文管理）。通过统一的 `hermes plugins` 交互式 UI 进行管理。
