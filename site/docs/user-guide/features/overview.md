---
title: "功能概览"
sidebar_label: "概览"
sidebar_position: 1
---

# 功能概览

Hermes Agent 拥有丰富的功能，远超基本聊天能力。从持久记忆和文件感知上下文，到浏览器自动化和语音对话，这些功能协同工作，使 Hermes 成为一个强大的自主助手。

## 核心功能

- **[工具与工具集](tools.md)** — 工具是扩展 Agent 功能的函数。它们被组织成逻辑工具集，可根据平台启用或禁用，涵盖网页搜索、终端执行、文件编辑、记忆、委派等。
- **[技能系统](skills.md)** — 按需加载的知识文档。技能遵循渐进披露模式，最大限度减少令牌使用，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。
- **[持久记忆](memory.md)** — 有界且经过策划的记忆，跨会话持久保存。Hermes 会通过 `MEMORY.md` 和 `USER.md` 记住你的偏好、项目、环境以及学到的内容。
- **[上下文文件](context-files.md)** — Hermes 会自动发现并加载项目上下文文件（如 `.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`SOUL.md`、`.cursorrules`），以塑造它在你项目中的行为。
- **[上下文引用](context-references.md)** — 输入 `@` 加引用，可将文件、文件夹、git 差异和 URL 直接注入消息中。Hermes 会内联展开引用并自动附加内容。
- **[检查点](../checkpoints-and-rollback.md)** — Hermes 会在修改文件前自动快照你的工作目录，提供安全保障，出现问题时可用 `/rollback` 回滚。

## 自动化

- **[定时任务（Cron）](cron.md)** — 使用自然语言或 cron 表达式自动调度任务。作业可附加技能，结果可发送到任意平台，支持暂停/恢复/编辑操作。
- **[子 Agent 委派](delegation.md)** — `delegate_task` 工具可启动上下文隔离、工具集受限、独立终端会话的子 Agent 实例。最多可并行运行 3 个子 Agent，支持多任务流。
- **[代码执行](code-execution.md)** — `execute_code` 工具允许 Agent 编写 Python 脚本，程序化调用 Hermes 工具，通过沙箱 RPC 执行将多步工作流合并为单次 LLM 交互。
- **[事件钩子](hooks.md)** — 在关键生命周期节点运行自定义代码。网关钩子处理日志、告警和 webhook；插件钩子处理工具拦截、指标和安全防护。
- **[批量处理](batch-processing.md)** — 并行运行 Hermes Agent 处理数百或数千条提示，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。

## 媒体与网络

- **[语音模式](voice-mode.md)** — 支持 CLI 和消息平台的全语音交互。通过麦克风与 Agent 对话，听取语音回复，并可在 Discord 语音频道进行实时语音会话。
- **[浏览器自动化](browser.md)** — 支持多种后端的完整浏览器自动化：Browserbase 云端、Browser Use 云端、本地 Chrome（CDP）或本地 Chromium。可浏览网站、填写表单、提取信息。
- **[视觉与图片粘贴](vision.md)** — 多模态视觉支持。可将剪贴板中的图片粘贴到 CLI，要求 Agent 使用任何支持视觉的模型进行分析、描述或处理。
- **[图像生成](image-generation.md)** — 使用 FAL.ai 的 FLUX 2 Pro 模型根据文本提示生成图像，并通过 Clarity Upscaler 自动进行 2 倍放大。
- **[语音与文本转语音](tts.md)** — 支持所有消息平台的文本转语音输出和语音消息转录，提供四种服务商选项：Edge TTS（免费）、ElevenLabs、OpenAI TTS 和 NeuTTS。

## 集成

- **[服务商路由](provider-routing.md)** — 精细控制由哪个 AI 服务商处理请求。通过排序、白名单、黑名单和优先级排序，优化成本、速度或质量。
- **[备用服务商](fallback-providers.md)** — 当主模型出错时自动切换到备用 LLM 服务商，包括对视觉和压缩等辅助任务的独立备用。
- **[API 服务器](api-server.md)** — 将 Hermes 作为兼容 OpenAI 的 HTTP 端点暴露。可连接任何支持 OpenAI 格式的前端——Open WebUI、LobeChat、LibreChat 等。
- **[IDE 集成（ACP）](acp.md)** — 在支持 ACP 的编辑器中使用 Hermes，如 VS Code、Zed 和 JetBrains。聊天、工具活动、文件差异和终端命令均在编辑器内呈现。
- **[Honcho 记忆](honcho.md)** — AI 原生的持久记忆，用于跨会话用户建模和个性化，通过辩证推理实现。
- **[强化学习训练](rl-training.md)** — 从 Agent 会话生成轨迹数据，用于强化学习和模型微调。

## 定制化

- **[个性与 SOUL.md](personality.md)** — 完全可定制的 Agent 个性。`SOUL.md` 是主要身份文件——系统提示中的第一部分，你可以每次会话切换内置或自定义的 `/personality` 预设。
- **[皮肤与主题](skins.md)** — 自定义 CLI 的视觉表现：横幅颜色、加载动画表情和动词、响应框标签、品牌文字和工具活动前缀。
- **[插件](plugins.md)** — 添加自定义工具、钩子和集成，无需修改核心代码。只需将包含 `plugin.yaml` 和 Python 代码的目录放入 `~/.hermes/plugins/`。
