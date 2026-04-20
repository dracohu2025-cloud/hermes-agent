---
title: "Integrations"
sidebar_label: "Overview"
sidebar_position: 0
---

# 集成 {#integrations}

Hermes Agent 可以连接外部系统，实现 AI 推理、工具服务器、IDE 工作流、编程式访问等功能。这些集成扩展了 Hermes 的能力和使用场景。

## AI 提供商与路由 {#ai-providers-routing}

Hermes 开箱即用地支持多种 AI 推理提供商。你可以用 `hermes model` 交互式配置，也可以在 `config.yaml` 中直接设置。

- **[AI 提供商](/user-guide/features/provider-routing)** — OpenRouter、Anthropic、OpenAI、Google，以及任何兼容 OpenAI 的端点。Hermes 会自动检测每个提供商是否支持视觉、流式传输、工具调用等能力。
- **[提供商路由](/user-guide/features/provider-routing)** — 精细控制哪些底层提供商处理你的 OpenRouter 请求。通过排序、白名单、黑名单和显式优先级来优化成本、速度或质量。
- **[备用提供商](/user-guide/features/fallback-providers)** — 当主模型出错时，自动故障转移到备用 LLM 提供商。包括主模型备用，以及针对视觉、压缩、网页提取等任务的独立辅助备用。

## 工具服务器（MCP） {#tool-servers-mcp}

- **[MCP 服务器](/user-guide/features/mcp)** — 通过 Model Context Protocol 将 Hermes 连接到外部工具服务器。无需编写原生 Hermes 工具，即可使用来自 GitHub、数据库、文件系统、浏览器栈、内部 API 等的工具。同时支持 stdio 和 SSE 传输，可按服务器过滤工具，并支持基于能力的资源/提示注册。

## 网页搜索后端 {#web-search-backends}

`web_search` 和 `web_extract` 工具支持四种后端提供商，可通过 `config.yaml` 或 `hermes tools` 配置：

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |

快速配置示例：

```yaml
web:
  backend: firecrawl    # firecrawl | parallel | tavily | exa
```

如果未设置 `web.backend`，系统会根据可用的 API key 自动检测后端。自托管 Firecrawl 也支持，通过 `FIRECRAWL_API_URL` 配置即可。

## 浏览器自动化 {#browser-automation}

Hermes 内置完整的浏览器自动化功能，提供多种后端选项来访问网站、填写表单和提取信息：

- **Browserbase** — 托管云浏览器，带反爬虫工具、CAPTCHA 自动破解和住宅代理
- **Browser Use** — 另一家云浏览器提供商
- **通过 CDP 连接本地 Chrome** — 使用 `/browser connect` 连接你正在运行的 Chrome 实例
- **本地 Chromium** — 通过 `agent-browser` CLI 使用无头本地浏览器

设置和用法详见[浏览器自动化](/user-guide/features/browser)。

## 语音与 TTS 提供商 {#voice-tts-providers}

所有消息平台均支持文本转语音和语音转文本：

| 提供商 | 质量 | 费用 | API Key |
||----------|---------|------|---------|
|| **Edge TTS**（默认） | 良好 | 免费 | 无需 |
|| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
|| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
|| **MiniMax** | 良好 | 付费 | `MINIMAX_API_KEY` |
|| **NeuTTS** | 良好 | 免费 | 无需 |

语音转文本支持三种提供商：本地 Whisper（免费，设备端运行）、Groq（快速云端）、OpenAI Whisper API。语音消息转录功能覆盖 Telegram、Discord、WhatsApp 及其他消息平台。详见[语音与 TTS](/user-guide/features/tts)和[语音模式](/user-guide/features/voice-mode)。

## IDE 与编辑器集成 {#ide-editor-integration}

- **[IDE 集成（ACP）](/user-guide/features/acp)** — 在兼容 ACP 的编辑器中使用 Hermes Agent，如 VS Code、Zed 和 JetBrains。Hermes 作为 ACP 服务器运行，在编辑器内渲染聊天消息、工具活动、文件差异和终端命令。

## 编程式访问 {#programmatic-access}

- **[API 服务器](/user-guide/features/api-server)** — 将 Hermes 暴露为兼容 OpenAI 的 HTTP 端点。任何使用 OpenAI 格式的前端 —— Open WebUI、LobeChat、LibreChat、NextChat、ChatBox —— 都可以连接并使用 Hermes 作为后端，享受完整的工具集。
## 记忆与个性化 {#memory-personalization}

- **[内置记忆](/user-guide/features/memory)** — 通过 `MEMORY.md` 和 `USER.md` 文件实现持久化、精心维护的记忆。Agent 会维护有限容量的个人笔记和用户画像数据，这些数据在会话结束后依然保留。
- **[记忆提供方](/user-guide/features/memory-providers)** — 接入外部记忆后端，实现更深度的个性化。支持七种提供方：Honcho（辩证推理）、OpenViking（分层检索）、Mem0（云端提取）、Hindsight（知识图谱）、Holographic（本地 SQLite）、RetainDB（混合搜索）和 ByteRover（基于 CLI）。

## 消息平台 {#messaging-platforms}

Hermes 作为网关机器人运行在 15+ 消息平台上，全部通过同一个 `gateway` 子系统配置：

- **[Telegram](/user-guide/messaging/telegram)**、**[Discord](/user-guide/messaging/discord)**、**[Slack](/user-guide/messaging/slack)**、**[WhatsApp](/user-guide/messaging/whatsapp)**、**[Signal](/user-guide/messaging/signal)**、**[Matrix](/user-guide/messaging/matrix)**、**[Mattermost](/user-guide/messaging/mattermost)**、**[Email](/user-guide/messaging/email)**、**[SMS](/user-guide/messaging/sms)**、**[DingTalk](/user-guide/messaging/dingtalk)**、**[Feishu/Lark](/user-guide/messaging/feishu)**、**[WeCom](/user-guide/messaging/wecom)**、**[WeCom Callback](/user-guide/messaging/wecom-callback)**、**[Weixin](/user-guide/messaging/weixin)**、**[BlueBubbles](/user-guide/messaging/bluebubbles)**、**[QQ Bot](/user-guide/messaging/qqbot)**、**[Home Assistant](/user-guide/messaging/homeassistant)**、**[Webhooks](/user-guide/messaging/webhooks)**

平台对比表和设置指南请参见 [消息网关概览](/user-guide/messaging)。

## 智能家居 {#home-automation}

- **[Home Assistant](/user-guide/messaging/homeassistant)** — 通过四个专用工具控制智能家居设备（`ha_list_entities`、`ha_get_state`、`ha_list_services`、`ha_call_service`）。配置好 `HASS_TOKEN` 后，Home Assistant 工具集会自动激活。

## 插件 {#plugins}

- **[插件系统](/user-guide/features/plugins)** — 无需修改核心代码，即可通过自定义工具、生命周期钩子和 CLI 命令扩展 Hermes。插件会从 `~/.hermes/plugins/`、项目本地 `.hermes/plugins/` 以及 pip 安装的 entry point 中自动发现。
- **[开发插件](/guides/build-a-hermes-plugin)** — 创建包含工具、钩子和 CLI 命令的 Hermes 插件的逐步指南。

## 训练与评估 {#training-evaluation}

- **[强化学习训练](/user-guide/features/rl-training)** — 从 Agent 会话中生成轨迹数据，用于强化学习和模型微调。支持 Atropos 环境，可自定义奖励函数。
- **[批处理](/user-guide/features/batch-processing)** — 并行运行 Agent 处理数百条提示，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。
