---
title: "集成"
sidebar_label: "概览"
sidebar_position: 0
---

# 集成

Hermes Agent 可以连接到外部系统，以实现 AI 推理、工具服务器、IDE 工作流、程序化访问等功能。这些集成扩展了 Hermes 的能力及其运行环境。

## AI 提供商与路由

Hermes 开箱即支持多种 AI 推理提供商。你可以使用 `hermes model` 进行交互式配置，或在 `config.yaml` 中进行设置。

- **[AI 提供商](/user-guide/features/provider-routing)** — 支持 OpenRouter、Anthropic、OpenAI、Google 以及任何兼容 OpenAI 的端点。Hermes 会自动检测每个提供商的视觉、流式传输和工具调用等能力。
- **[提供商路由](/user-guide/features/provider-routing)** — 对处理 OpenRouter 请求的底层提供商进行精细化控制。通过排序、白名单、黑名单和显式优先级排序，优化成本、速度或质量。
- **[备用提供商](/user-guide/features/fallback-providers)** — 当主模型遇到错误时，自动故障转移到备用 LLM 提供商。包括主模型回退，以及针对视觉、压缩和网页提取的独立辅助任务回退。

## 工具服务器 (MCP)

- **[MCP 服务器](/user-guide/features/mcp)** — 通过 Model Context Protocol 将 Hermes 连接到外部工具服务器。无需编写原生的 Hermes 工具，即可访问来自 GitHub、数据库、文件系统、浏览器堆栈、内部 API 等的工具。支持 stdio 和 SSE 传输、按服务器进行工具过滤，以及具备能力感知功能的资源/提示词注册。

## 网页搜索后端

`web_search` 和 `web_extract` 工具支持四种后端提供商，可通过 `config.yaml` 或 `hermes tools` 进行配置：

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl** (默认) | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |

快速设置示例：

```yaml
web:
  backend: firecrawl    # firecrawl | parallel | tavily | exa
```

如果未设置 `web.backend`，系统将根据可用的 API 密钥自动检测后端。同时也支持通过 `FIRECRAWL_API_URL` 使用自托管的 Firecrawl。

## 浏览器自动化

Hermes 包含完整的浏览器自动化功能，提供多种后端选项，用于浏览网站、填写表单和提取信息：

- **Browserbase** — 托管云浏览器，具备反机器人工具、验证码破解和住宅代理功能
- **Browser Use** — 替代性云浏览器提供商
- **Local Chrome via CDP** — 使用 `/browser connect` 连接到你正在运行的 Chrome 实例
- **Local Chromium** — 通过 `agent-browser` CLI 使用本地无头浏览器

请参阅 [浏览器自动化](/user-guide/features/browser) 获取设置和使用说明。

## 语音与 TTS 提供商

支持跨所有消息平台的语音转文字 (STT) 和文字转语音 (TTS)：

| 提供商 | 质量 | 成本 | API 密钥 |
||----------|---------|------|---------|
|| **Edge TTS** (默认) | 良好 | 免费 | 无需 |
|| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
|| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
|| **MiniMax** | 良好 | 付费 | `MINIMAX_API_KEY` |
|| **NeuTTS** | 良好 | 免费 | 无需 |

语音转文字支持三种提供商：本地 Whisper（免费，在设备上运行）、Groq（快速云端）和 OpenAI Whisper API。语音消息转录功能适用于 Telegram、Discord、WhatsApp 及其他消息平台。详情请参阅 [语音与 TTS](/user-guide/features/tts) 和 [语音模式](/user-guide/features/voice-mode)。

## IDE 与编辑器集成

- **[IDE 集成 (ACP)](/user-guide/features/acp)** — 在 VS Code、Zed 和 JetBrains 等兼容 ACP 的编辑器中使用 Hermes Agent。Hermes 作为 ACP 服务器运行，在编辑器内渲染聊天消息、工具活动、文件差异和终端命令。

## 程序化访问

- **[API 服务器](/user-guide/features/api-server)** — 将 Hermes 暴露为兼容 OpenAI 的 HTTP 端点。任何支持 OpenAI 格式的前端（如 Open WebUI、LobeChat、LibreChat、NextChat、ChatBox）都可以连接并使用 Hermes 作为后端，并调用其全套工具。

## 记忆与个性化

- **[内置记忆](/user-guide/features/memory)** — 通过 `MEMORY.md` 和 `USER.md` 文件实现持久化、精选的记忆。Agent 会维护个人笔记和用户配置数据的有界存储，这些数据在不同会话间保持有效。
- **[记忆提供商](/user-guide/features/memory-providers)** — 接入外部记忆后端以实现更深度的个性化。支持七种提供商：Honcho（辩证推理）、OpenViking（分层检索）、Mem0（云端提取）、Hindsight（知识图谱）、Holographic（本地 SQLite）、RetainDB（混合搜索）和 ByteRover（基于 CLI）。

## 消息平台

Hermes 作为网关机器人运行在 15 个以上的消息平台上，所有平台均通过同一个 `gateway` 子系统进行配置：

- **[Telegram](/user-guide/messaging/telegram)**, **[Discord](/user-guide/messaging/discord)**, **[Slack](/user-guide/messaging/slack)**, **[WhatsApp](/user-guide/messaging/whatsapp)**, **[Signal](/user-guide/messaging/signal)**, **[Matrix](/user-guide/messaging/matrix)**, **[Mattermost](/user-guide/messaging/mattermost)**, **[Email](/user-guide/messaging/email)**, **[SMS](/user-guide/messaging/sms)**, **[钉钉](/user-guide/messaging/dingtalk)**, **[飞书/Lark](/user-guide/messaging/feishu)**, **[企业微信](/user-guide/messaging/wecom)**, **[微信](/user-guide/messaging/weixin)**, **[BlueBubbles](/user-guide/messaging/bluebubbles)**, **[Home Assistant](/user-guide/messaging/homeassistant)**, **[Webhooks](/user-guide/messaging/webhooks)**

请参阅 [消息网关概览](/user-guide/messaging) 查看平台对比表和设置指南。

## 家庭自动化

- **[Home Assistant](/user-guide/messaging/homeassistant)** — 通过四个专用工具（`ha_list_entities`、`ha_get_state`、`ha_list_services`、`ha_call_service`）控制智能家居设备。当配置了 `HASS_TOKEN` 后，Home Assistant 工具集会自动激活。

## 插件

- **[插件系统](/user-guide/features/plugins)** — 在不修改核心代码的情况下，通过自定义工具、生命周期钩子和 CLI 命令扩展 Hermes。插件会从 `~/.hermes/plugins/`、项目本地的 `.hermes/plugins/` 以及 pip 安装的入口点中被发现。
- **[构建插件](/guides/build-a-hermes-plugin)** — 创建包含工具、钩子和 CLI 命令的 Hermes 插件的分步指南。

## 训练与评估

- **[RL 训练](/user-guide/features/rl-training)** — 从 Agent 会话中生成轨迹数据，用于强化学习和模型微调。支持带有可自定义奖励函数的 Atropos 环境。
- **[批处理](/user-guide/features/batch-processing)** — 并行运行数百个提示词，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。
