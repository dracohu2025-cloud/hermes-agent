---
title: "功能概览"
sidebar_label: "概览"
sidebar_position: 1
---

# 功能概览 {#features-overview}

Hermes Agent 拥有一套丰富的功能，远不止基础聊天。从持久记忆、文件感知上下文，到浏览器自动化和语音对话，这些功能协同工作，使 Hermes 成为一个强大的自主助手。

## 核心 {#core}

- **[工具与工具集](tools.md)** — 工具是扩展 Agent 能力的函数。它们被组织成逻辑上的工具集，可按平台启用或禁用，涵盖网页搜索、终端执行、文件编辑、记忆、委派等。
- **[技能系统](skills.md)** — 按需加载的知识文档，Agent 可在需要时使用。技能遵循渐进式披露模式以最小化 token 消耗，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。
- **[持久记忆](memory.md)** — 有界、精选的记忆，跨会话持久保存。Hermes 通过 `MEMORY.md` 和 `USER.md` 记住你的偏好、项目、环境以及它学到的东西。
- **[上下文文件](context-files.md)** — Hermes 自动发现并加载项目上下文文件（`.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`SOUL.md`、`.cursorrules`），这些文件决定了它在你的项目中的行为方式。
- **[上下文引用](context-references.md)** — 输入 `@` 后跟引用，可将文件、文件夹、git diff 和 URL 直接注入到你的消息中。Hermes 会内联展开引用并自动追加内容。
- **[检查点](../checkpoints-and-rollback.md)** — Hermes 在修改文件前会自动快照你的工作目录，为你提供安全网，如果出现问题，可以使用 `/rollback` 回滚。

## 自动化 {#automation}

- **[定时任务（Cron）](cron.md)** — 使用自然语言或 cron 表达式安排自动运行的任务。任务可以附加技能、将结果投递到任何平台，并支持暂停/恢复/编辑操作。
- **[子 Agent 委派](delegation.md)** — `delegate_task` 工具会生成子 Agent 实例，每个实例拥有独立的上下文、受限的工具集和自己的终端会话。默认可同时运行 3 个子 Agent（可配置），用于并行工作流。
- **[代码执行](code-execution.md)** — `execute_code` 工具让 Agent 编写 Python 脚本，以编程方式调用 Hermes 工具，通过沙箱 RPC 执行将多步骤工作流压缩为单个 LLM 轮次。
- **[事件钩子](hooks.md)** — 在关键生命周期点运行自定义代码。网关钩子处理日志、告警和 webhook；插件钩子处理工具拦截、指标和护栏。
- **[批量处理](batch-processing.md)** — 在数百或数千个提示上并行运行 Hermes Agent，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。

## 媒体与网页 {#media-web}

- **[语音模式](voice-mode.md)** — 在 CLI 和消息平台上实现完整的语音交互。使用麦克风与 Agent 对话，收听语音回复，并在 Discord 语音频道中进行实时语音对话。
- **[浏览器自动化](browser.md)** — 完整的浏览器自动化，支持多种后端：Browserbase 云、Browser Use 云、通过 CDP 的本地 Chrome，或本地 Chromium。浏览网站、填写表单、提取信息。
- **[视觉与图片粘贴](vision.md)** — 多模态视觉支持。从剪贴板粘贴图片到 CLI，让 Agent 使用任何支持视觉的模型进行分析、描述或处理。
- **[图片生成](image-generation.md)** — 使用 FAL.ai 根据文本提示生成图片。支持九种模型（FLUX 2 Klein/Pro、GPT-Image 1.5/2、Nano Banana Pro、Ideogram V3、Recraft V4 Pro、Qwen、Z-Image Turbo）；通过 `hermes tools` 选择。
- **[语音与 TTS](tts.md)** — 文本转语音输出和语音消息转录，支持所有消息平台，提供十种原生提供商选项：Edge TTS（免费）、ElevenLabs、OpenAI TTS、MiniMax、Mistral Voxtral、Google Gemini、xAI、NeuTTS、KittenTTS 和 Piper——此外还支持自定义命令提供商，用于任何本地 TTS CLI。
## 集成 {#integrations}

- **[MCP 集成](mcp.md)** — 通过 stdio 或 HTTP 传输连接到任意 MCP 服务器。无需编写原生 Hermes 工具即可访问来自 GitHub、数据库、文件系统和内部 API 的外部工具。支持按服务器进行工具过滤和采样。
- **[Provider 路由](provider-routing.md)** — 精细控制哪些 AI Provider 处理你的请求。通过排序、白名单、黑名单和优先级排序来优化成本、速度或质量。
- **[Fallback Provider](fallback-providers.md)** — 当主模型遇到错误时，自动切换到备用 LLM Provider，包括对视觉、压缩等辅助任务的独立回退。
- **[凭据池](credential-pools.md)** — 将 API 调用分散到同一 Provider 的多个密钥上。在遇到速率限制或失败时自动轮换。
- **[记忆 Provider](memory-providers.md)** — 接入外部记忆后端（Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover、Supermemory），实现跨会话的用户建模和个性化，超越内置记忆系统。
- **[API 服务器](api-server.md)** — 将 Hermes 暴露为兼容 OpenAI 的 HTTP 端点。连接任何支持 OpenAI 格式的前端——Open WebUI、LobeChat、LibreChat 等。
- **[IDE 集成 (ACP)](acp.md)** — 在兼容 ACP 的编辑器（如 VS Code、Zed、JetBrains）中使用 Hermes。聊天、工具活动、文件差异和终端命令会在编辑器内渲染。
- **[RL 训练](rl-training.md)** — 从 Agent 会话中生成轨迹数据，用于强化学习和模型微调。

## 自定义 {#customization}

- **[个性与 SOUL.md](personality.md)** — 完全可定制的 Agent 个性。`SOUL.md` 是主要的身份文件——位于系统提示的最前面——你可以按会话切换内置或自定义的 `/personality` 预设。
- **[皮肤与主题](skins.md)** — 自定义 CLI 的视觉呈现：横幅颜色、旋转动画图标和动词、响应框标签、品牌文本以及工具活动前缀。
- **[插件](plugins.md)** — 无需修改核心代码即可添加自定义工具、钩子和集成。三种插件类型：通用插件（工具/钩子）、记忆 Provider（跨会话知识）和上下文引擎（替代上下文管理）。通过统一的 `hermes plugins` 交互式 UI 进行管理。
