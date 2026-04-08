---
title: "集成"
sidebar_label: "概览"
sidebar_position: 0
---

# 集成 (Integrations)

Hermes Agent 可以连接到外部系统，用于 AI 推理、工具服务器、IDE 工作流、程序化访问等。这些集成扩展了 Hermes 的功能边界和运行环境。

## AI 提供商与路由

Hermes 开箱即用支持多个 AI 推理提供商。你可以使用 `hermes model` 进行交互式配置，或者在 `config.yaml` 中进行设置。

- **[AI 提供商](/user-guide/features/provider-routing)** — 支持 OpenRouter、Anthropic、OpenAI、Google 以及任何兼容 OpenAI 接口的端点。Hermes 会自动检测每个提供商的能力，如视觉、流式传输和工具调用（tool use）。
- **[提供商路由](/user-guide/features/provider-routing)** — 精细控制由哪些底层提供商处理你的 OpenRouter 请求。通过排序、白名单、黑名单和显式优先级设置，针对成本、速度或质量进行优化。
- **[备用提供商 (Fallback Providers)](/user-guide/features/fallback-providers)** — 当主模型遇到错误时，自动切换到备用 LLM 提供商。包括主模型备用，以及针对视觉、压缩和网页提取等任务的独立辅助任务备用。

## 工具服务器 (MCP)

- **[MCP 服务器](/user-guide/features/mcp)** — 通过 Model Context Protocol（模型上下文协议）将 Hermes 连接到外部工具服务器。无需编写原生 Hermes 工具，即可访问来自 GitHub、数据库、文件系统、浏览器栈、内部 API 等的工具。支持 stdio 和 SSE 传输协议、单服务器工具过滤，以及具备感知能力的资源/提示词注册。

## 网页搜索后端

`web_search` 和 `web_extract` 工具支持四个后端提供商，可通过 `config.yaml` 或 `hermes tools` 配置：

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl** (默认) | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |

快速设置示例：

```yaml
web:
  backend: firecrawl    # 可选：firecrawl | parallel | tavily | exa
```

如果未设置 `web.backend`，系统将根据可用的 API Key 自动检测后端。通过 `FIRECRAWL_API_URL` 也支持私有部署的 Firecrawl。

## 浏览器自动化

Hermes 内置了完整的浏览器自动化功能，提供多种后端选项用于浏览网站、填写表单和提取信息：

- **Browserbase** — 托管云端浏览器，具备反爬工具、验证码识别和住宅代理功能。
- **Browser Use** — 另一种云端浏览器提供商。
- **通过 CDP 连接本地 Chrome** — 使用 `/browser connect` 连接到你正在运行的 Chrome 实例。
- **本地 Chromium** — 通过 `agent-browser` CLI 运行的无头（headless）本地浏览器。

详见 [浏览器自动化](/user-guide/features/browser) 了解设置与用法。

## 语音与 TTS 提供商

支持所有消息平台的文字转语音（TTS）和语音转文字（STT）：

| 提供商 | 质量 | 成本 | API Key |
||----------|---------|------|---------|
|| **Edge TTS** (默认) | 良好 | 免费 | 无需 |
|| **ElevenLabs** | 极佳 | 付费 | `ELEVENLABS_API_KEY` |
|| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
|| **MiniMax** | 良好 | 付费 | `MINIMAX_API_KEY` |
|| **NeuTTS** | 良好 | 免费 | 无需 |

语音转文字支持三个提供商：本地 Whisper（免费，在设备上运行）、Groq（快速云端）和 OpenAI Whisper API。语音消息转录功能可在 Telegram、Discord、WhatsApp 和其他消息平台使用。详见 [语音与 TTS](/user-guide/features/tts) 和 [语音模式](/user-guide/features/voice-mode)。

## IDE 与编辑器集成

- **[IDE 集成 (ACP)](/user-guide/features/acp)** — 在支持 ACP 的编辑器（如 VS Code、Zed 和 JetBrains）中使用 Hermes Agent。Hermes 作为 ACP 服务器运行，在编辑器内部渲染聊天消息、工具活动、文件差异（diff）和终端命令。

## 程序化访问

- **[API 服务器](/user-guide/features/api-server)** — 将 Hermes 作为兼容 OpenAI 的 HTTP 端点暴露。任何支持 OpenAI 格式的前端（如 Open WebUI、LobeChat、LibreChat、NextChat、ChatBox）都可以连接并将 Hermes 及其全套工具集作为后端使用。

## 记忆与个性化

- **[内置记忆](/user-guide/features/memory)** — 通过 `MEMORY.md` 和 `USER.md` 文件实现持久化、精选的记忆。Agent 会维护个人笔记和用户画像数据的有限存储，这些数据可以跨会话保存。
- **[记忆提供商](/user-guide/features/memory-providers)** — 接入外部记忆后端以实现更深层次的个性化。支持七个提供商：Honcho（辩证推理）、OpenViking（分层检索）、Mem0（云端提取）、Hindsight（知识图谱）、Holographic（本地 SQLite）、RetainDB（混合搜索）和 ByteRover（基于 CLI）。

## 消息平台

Hermes 可以作为网关机器人运行在 14 个以上的消息平台上，全部通过同一个 `gateway` 子系统配置：

- **[Telegram](/user-guide/messaging/telegram)**, **[Discord](/user-guide/messaging/discord)**, **[Slack](/user-guide/messaging/slack)**, **[WhatsApp](/user-guide/messaging/whatsapp)**, **[Signal](/user-guide/messaging/signal)**, **[Matrix](/user-guide/messaging/matrix)**, **[Mattermost](/user-guide/messaging/mattermost)**, **[Email](/user-guide/messaging/email)**, **[SMS](/user-guide/messaging/sms)**, **[钉钉](/user-guide/messaging/dingtalk)**, **[飞书](/user-guide/messaging/feishu)**, **[企业微信](/user-guide/messaging/wecom)**, **[Home Assistant](/user-guide/messaging/homeassistant)**, **[Webhooks](/user-guide/messaging/webhooks)**

请参阅 [消息网关概览](/user-guide/messaging) 查看平台对比表和设置指南。

## 家庭自动化

- **[Home Assistant](/user-guide/messaging/homeassistant)** — 通过四个专用工具（`ha_list_entities`、`ha_get_state`、`ha_list_services`、`ha_call_service`）控制智能家居设备。配置 `HASS_TOKEN` 后，Home Assistant 工具集会自动激活。

## 插件

- **[插件系统](/user-guide/features/plugins)** — 无需修改核心代码，即可通过自定义工具、生命周期钩子（hooks）和 CLI 命令扩展 Hermes。插件可从 `~/.hermes/plugins/`、项目本地的 `.hermes/plugins/` 以及通过 pip 安装的入口点中自动发现。
- **[开发插件](/guides/build-a-hermes-plugin)** — 创建包含工具、钩子和 CLI 命令的 Hermes 插件的分步指南。

## 训练与评估

- **[RL 训练](/user-guide/features/rl-training)** — 从 Agent 会话中生成轨迹数据，用于强化学习和模型微调。支持带有可自定义奖励函数的 Atropos 环境。
- **[批量处理](/user-guide/features/batch-processing)** — 并行运行 Agent 处理数百个提示词，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。
