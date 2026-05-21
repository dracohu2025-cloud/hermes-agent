---
title: "功能概览"
sidebar_label: "概览"
sidebar_position: 1
---

<a id="features-overview"></a>
# 功能概览

Hermes Agent 提供了一组丰富的功能，远超基本的对话能力。从持久化记忆、文件感知上下文，到浏览器自动化和语音对话，这些功能协同工作，使 Hermes 成为强大的自主助手。

<a id="core"></a>
## 核心功能

- **[工具与工具集](tools.md)** — 工具是扩展 Agent 能力的函数。它们被组织成逻辑上的工具集，可以按平台启用或禁用，涵盖网络搜索、终端执行、文件编辑、记忆、委派等。
- **[技能系统](skills.md)** — 按需加载的知识文档，Agent 在需要时可调用。技能遵循渐进式披露模式以最小化 Token 消耗，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。
- **[持久化记忆](memory.md)** — 有边界、经过整理的跨会话持久化记忆。Hermes 通过 `MEMORY.md` 和 `USER.md` 记住你的偏好、项目、环境以及它已经学到的东西。
- **[上下文文件](context-files.md)** — Hermes 自动发现并加载项目上下文文件（`.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`SOUL.md`、`.cursorrules`），这些文件决定了它在项目中的行为方式。
- **[上下文引用](context-references.md)** — 输入 `@` 后跟引用，可以将文件、文件夹、Git diff 和 URL 直接注入到你的消息中。Hermes 会内联展开引用，并自动追加内容。
- **[检查点](../checkpoints-and-rollback.md)** — Hermes 在进行文件更改之前自动快照你的工作目录，为你提供安全网，如果出现错误可以使用 `/rollback` 回滚。

<a id="automation"></a>
## 自动化

- **[定时任务 (Cron)](cron.md)** — 使用自然语言或 cron 表达式自动运行任务。任务可以附加技能，将结果投递到任何平台，并支持暂停/恢复/编辑操作。
- **[子 Agent 委派](delegation.md)** — `delegate_task` 工具会生成上下文隔离、工具集受限且拥有独立终端会话的子 Agent 实例。默认情况下可以并发运行 3 个子 Agent（可配置），用于并行工作流。
- **[代码执行](code-execution.md)** — `execute_code` 工具允许 Agent 编写 Python 脚本，以编程方式调用 Hermes 工具，通过沙箱 RPC 执行将多步骤工作流压缩为单次 LLM 调用。
- **[事件钩子](hooks.md)** — 在关键生命周期节点运行自定义代码。网关钩子处理日志、告警和 webhook；插件钩子处理工具拦截、指标和防护。
- **[批量处理](batch-processing.md)** — 并行运行 Hermes Agent 处理数百或数千个提示，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。

<a id="media-web"></a>
## 媒体与 Web

- **[语音模式](voice-mode.md)** — 跨 CLI 和消息平台的完整语音交互。使用麦克风与 Agent 对话，收听语音回复，并在 Discord 语音频道中进行实时语音对话。
- **[浏览器自动化](browser.md)** — 完整的浏览器自动化，支持多种后端：Browserbase 云、Browser Use 云、本地 Chrome/Brave/Chromium/Edge（通过 CDP）或本地 Chromium。可以浏览网站、填写表单和提取信息。
- **[视觉与图片粘贴](vision.md)** — 多模态视觉支持。从剪贴板粘贴图片到 CLI，并要求 Agent 使用任何支持视觉的模型进行分析、描述或处理。
- **[图片生成](image-generation.md)** — 使用 FAL.ai 根据文本提示生成图片。支持九种模型（FLUX 2 Klein/Pro、GPT-Image 1.5/2、Nano Banana Pro、Ideogram V3、Recraft V4 Pro、Qwen、Z-Image Turbo）；通过 `hermes tools` 选择。
- **[语音与 TTS](tts.md)** — 文本转语音输出以及所有消息平台上的语音消息转录，提供十个原生提供商选项：Edge TTS（免费）、ElevenLabs、OpenAI TTS、MiniMax、Mistral Voxtral、Google Gemini、xAI、NeuTTS、KittenTTS 和 Piper——外加自定义命令提供商，用于任何本地 TTS CLI。
<a id="integrations"></a>
## 集成

- **[MCP 集成](mcp.md)** — 通过 stdio 或 HTTP 传输连接任何 MCP 服务器。可访问来自 GitHub、数据库、文件系统和内部 API 的外部工具，无需编写原生 Hermes 工具。支持按服务器进行工具过滤和采样。
- **[供应商路由](provider-routing.md)** — 精细控制哪些 AI 供应商处理你的请求。通过排序、白名单、黑名单和优先级顺序，优化成本、速度或质量。
- **[备用供应商](fallback-providers.md)** — 当主模型遇到错误时，自动故障转移到备用的 LLM 供应商，包括对视觉和压缩等辅助任务的独立备用机制。
- **[凭据池](credential-pools.md)** — 将 API 调用分配到同一供应商的多个密钥上。遇到速率限制或失败时自动轮换。
- **[提示缓存](../configuration#prompt-caching)** — 针对 Claude，在原生 Anthropic、OpenRouter 和 Nous Portal 上内置跨会话的 1 小时前缀缓存。始终开启，无需配置。
- **[记忆提供商](memory-providers.md)** — 插入外部记忆后端（Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover、Supermemory），在内置记忆系统之外实现跨会话的用户建模和个性化。
- **[API 服务器](api-server.md)** — 将 Hermes 暴露为兼容 OpenAI 的 HTTP 端点。连接任何支持 OpenAI 格式的前端——Open WebUI、LobeChat、LibreChat 等。
- **[IDE 集成 (ACP)](acp.md)** — 在兼容 ACP 的编辑器（如 VS Code、Zed 和 JetBrains）中使用 Hermes。聊天、工具活动、文件差异和终端命令都会在编辑器内渲染。
- **强化学习训练** — 官方文档已移除独立 RL 训练页面；如需相关能力，请参考开发者文档和最新发布说明。

<a id="customization"></a>
## 自定义

- **[个性与 SOUL.md](personality.md)** — 完全可定制的 agent 个性。`SOUL.md`是主要的身份文件——位于系统提示的最开头，并且你可以在每个会话中切换使用内置或自定义的 `/personality` 预设。
- **[皮肤与主题](skins.md)** — 自定义 CLI 的视觉呈现：横幅颜色、旋转动画类型和动词、响应框标签、品牌文本以及工具活动前缀。
- **[插件](plugins.md)** — 在不修改核心代码的情况下添加自定义工具、钩子和集成。三种插件类型：通用插件（工具/钩子）、记忆提供商（跨会话知识）和上下文引擎（替代上下文管理）。通过统一的 `hermes plugins` 交互式 UI 进行管理。
