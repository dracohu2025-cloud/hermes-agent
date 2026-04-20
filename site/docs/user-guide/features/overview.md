---
title: "功能概览"
sidebar_label: "概览"
sidebar_position: 1
---

# 功能概览 {#features-overview}

Hermes Agent 包含一套丰富的功能，远不止基础的聊天。从持久记忆和文件感知上下文到浏览器自动化及语音对话，这些功能协同工作，使 Hermes 成为一个强大的自主助手。

## 核心功能 {#core}

- **[工具与工具集](tools.md)** — 工具是扩展 Agent 能力的函数。它们被组织成逻辑工具集，可按平台启用或禁用，涵盖网络搜索、终端执行、文件编辑、记忆、委托等功能。
- **[技能系统](skills.md)** — Agent 可以在需要时加载的按需知识文档。技能遵循渐进式披露模式，以最小化 token 使用，并与 [agentskills.io](https://agentskills.io/specification) 开放标准兼容。
- **[持久记忆](memory.md)** — 有限的、经过整理的跨会话记忆。Hermes 通过 `MEMORY.md` 和 `USER.md` 记住你的偏好、项目、环境以及它学到的东西。
- **[上下文文件](context-files.md)** — Hermes 自动发现并加载项目上下文文件（`.hermes.md`, `AGENTS.md`, `CLAUDE.md`, `SOUL.md`, `.cursorrules`），这些文件决定了它在你的项目中的行为方式。
- **[上下文引用](context-references.md)** — 输入 `@` 后跟一个引用，可将文件、文件夹、git diffs 和 URL 直接注入你的消息中。Hermes 会内联展开引用并自动追加内容。
- **[检查点](../checkpoints-and-rollback.md)** — Hermes 在修改文件前会自动对你的工作目录进行快照，如果出现问题，你可以通过 `/rollback` 命令回滚，提供一个安全网。

## 自动化 {#automation}

- **[定时任务 (Cron)](cron.md)** — 使用自然语言或 cron 表达式自动安排任务运行。任务可以附加技能，将结果发送到任何平台，并支持暂停/恢复/编辑操作。
- **[子 Agent 委托](delegation.md)** — `delegate_task` 工具会创建子 Agent 实例，它们拥有隔离的上下文、受限的工具集以及自己的终端会话。最多可同时运行 3 个子 Agent 进行并行工作流。
- **[代码执行](code-execution.md)** — `execute_code` 工具允许 Agent 编写 Python 脚本，以编程方式调用 Hermes 工具，通过沙箱化的 RPC 执行将多步骤工作流压缩到单一的 LLM 回合中。
- **[事件钩子](hooks.md)** — 在关键生命周期节点运行自定义代码。网关钩子处理日志记录、警报和 webhooks；插件钩子处理工具拦截、指标和护栏。
- **[批量处理](batch-processing.md)** — 并行运行 Hermes Agent 处理数百或数千个提示，生成 ShareGPT 格式的结构化轨迹数据，用于训练数据生成或评估。

## 媒体与网络 {#media-web}

- **[语音模式](voice-mode.md)** — 在 CLI 和消息平台上的完整语音交互。使用麦克风与 Agent 交谈，听取语音回复，并在 Discord 语音频道中进行实时语音对话。
- **[浏览器自动化](browser.md)** — 具有多个后端支持的完整浏览器自动化：Browserbase 云、Browser Use 云、通过 CDP 的本地 Chrome 或本地 Chromium。浏览网站、填写表单并提取信息。
- **[视觉与图片粘贴](vision.md)** — 支持多模态视觉。从剪贴板粘贴图片到 CLI，并要求 Agent 使用任何支持视觉的模型进行分析、描述或处理它们。
- **[图片生成](image-generation.md)** — 使用 FAL.ai 从文本提示生成图片。支持八种模型（FLUX 2 Klein/Pro, GPT-Image 1.5, Nano Banana Pro, Ideogram V3, Recraft V4 Pro, Qwen, Z-Image Turbo）；通过 `hermes tools` 选择一个。
- **[语音与 TTS](tts.md)** — 在所有消息平台上的文本到语音输出和语音消息转录，提供五种提供商选项：Edge TTS（免费）、ElevenLabs、OpenAI TTS、MiniMax 和 NeuTTS。

## 集成 {#integrations}

- **[MCP 集成](mcp.md)** — 通过 stdio 或 HTTP 传输连接到任何 MCP 服务器。无需编写原生 Hermes 工具即可访问来自 GitHub、数据库、文件系统和内部 API 的外部工具。包含按服务器过滤工具和采样支持。
- **[提供商路由](provider-routing.md)** — 对处理你请求的 AI 提供商进行细粒度控制。通过排序、白名单、黑名单和优先级排序来优化成本、速度或质量。
- **[备用提供商](fallback-providers.md)** — 当你的主要模型遇到错误时，自动故障转移到备用 LLM 提供商，包括视觉和压缩等辅助任务的独立备用。
- **[凭证池](credential-pools.md)** — 在同一提供商下跨多个密钥分发 API 调用。在遇到速率限制或失败时自动轮换。
- **[记忆提供商](memory-providers.md)** — 接入外部记忆后端（Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover），用于跨会话的用户建模和个性化，超越内置的记忆系统。
- **[API 服务器](api-server.md)** — 将 Hermes 作为兼容 OpenAI 的 HTTP 端点暴露。连接任何支持 OpenAI 格式的前端——Open WebUI、LobeChat、LibreChat 等。
- **[IDE 集成 (ACP)](acp.md)** — 在兼容 ACP 的编辑器（如 VS Code、Zed 和 JetBrains）中使用 Hermes。聊天、工具活动、文件差异和终端命令在你的编辑器内呈现。
- **[RL 训练](rl-training.md)** — 从 Agent 会话生成轨迹数据，用于强化学习和模型微调。
## 自定义 {#customization}

- **[个性与 SOUL.md](personality.md)** — 完全可定制的 Agent 个性。`SOUL.md` 是主要的身份文件，也是系统提示词的第一部分。你可以为每个会话切换使用内置的或自定义的 `/personality` 预设。
- **[皮肤与主题](skins.md)** — 自定义 CLI 的视觉呈现：横幅颜色、加载动画图标和动词、响应框标签、品牌文本以及工具活动前缀。
- **[插件](plugins.md)** — 无需修改核心代码即可添加自定义工具、钩子和集成。提供三种插件类型：通用插件（工具/钩子）、记忆提供者（跨会话知识）和上下文引擎（替代的上下文管理）。通过统一的 `hermes plugins` 交互式界面进行管理。
