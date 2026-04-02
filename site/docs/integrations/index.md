---
title: "集成"
sidebar_label: "概览"
sidebar_position: 0
---

# 集成

Hermes Agent 连接到外部系统，用于 AI 推理、工具服务器、IDE 工作流、编程访问等。这些集成扩展了 Hermes 的功能和运行场景。

## AI 提供商与路由

Hermes 开箱即支持多个 AI 推理提供商。可以使用 `hermes model` 进行交互式配置，或在 `config.yaml` 中设置。

- **[AI 提供商](/user-guide/features/provider-routing)** — 包括 OpenRouter、Anthropic、OpenAI、Google 以及任何兼容 OpenAI 的端点。Hermes 会自动检测各提供商的视觉、流式传输和工具使用等能力。
- **[提供商路由](/user-guide/features/provider-routing)** — 细粒度控制底层提供商处理 OpenRouter 请求的方式。通过排序、白名单、黑名单和显式优先级排序，实现成本、速度或质量的优化。
- **[备用提供商](/user-guide/features/fallback-providers)** — 当主模型出现错误时，自动切换到备用 LLM 提供商。包括主模型的回退和视觉、压缩、网页提取等辅助任务的独立回退。

## 工具服务器（MCP）

- **[MCP 服务器](/user-guide/features/mcp)** — 通过模型上下文协议连接 Hermes 到外部工具服务器。无需编写原生 Hermes 工具即可访问 GitHub、数据库、文件系统、浏览器堆栈、内部 API 等工具。支持 stdio 和 SSE 传输方式，支持按服务器过滤工具，以及基于能力的资源/提示注册。

## 网络搜索后端

`web_search`、`web_extract` 和 `web_crawl` 工具支持四个后端提供商，通过 `config.yaml` 或 `hermes tools` 配置：

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |

快速设置示例：

```yaml
web:
  backend: firecrawl    # firecrawl | parallel | tavily | exa
```

如果未设置 `web.backend`，则会根据可用的 API 密钥自动检测后端。也支持通过 `FIRECRAWL_API_URL` 使用自托管的 Firecrawl。

## 浏览器自动化

Hermes 包含完整的浏览器自动化，支持多种后端选项，用于浏览网站、填写表单和提取信息：

- **Browserbase** — 托管云浏览器，带有反机器人工具、验证码破解和住宅代理
- **Browser Use** — 另一种云浏览器提供商
- **通过 CDP 连接本地 Chrome** — 使用 `/browser connect` 连接正在运行的 Chrome 实例
- **本地 Chromium** — 通过 `agent-browser` CLI 运行的无头本地浏览器

详见 [浏览器自动化](/user-guide/features/browser) 的设置和使用说明。

## 语音与 TTS 提供商

支持所有消息平台的文本转语音和语音转文本：

| 提供商 | 质量 | 费用 | API 密钥 |
|----------|---------|------|---------|
| **Edge TTS**（默认） | 良好 | 免费 | 无需 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **NeuTTS** | 良好 | 免费 | 无需 |

语音转文本使用 Whisper 进行 Telegram、Discord 和 WhatsApp 的语音消息转录。详情见 [语音与 TTS](/user-guide/features/tts) 和 [语音模式](/user-guide/features/voice-mode)。

## IDE 与编辑器集成

- **[IDE 集成（ACP）](/user-guide/features/acp)** — 在支持 ACP 的编辑器中使用 Hermes Agent，如 VS Code、Zed 和 JetBrains。Hermes 作为 ACP 服务器运行，在编辑器内渲染聊天消息、工具活动、文件差异和终端命令。

## 编程访问

- **[API 服务器](/user-guide/features/api-server)** — 将 Hermes 作为兼容 OpenAI 的 HTTP 端点暴露。任何支持 OpenAI 格式的前端——Open WebUI、LobeChat、LibreChat、NextChat、ChatBox——都可以连接并使用 Hermes 及其完整工具集作为后端。

## 记忆与个性化

- **[Honcho 记忆](/user-guide/features/honcho)** — AI 原生的持久记忆，用于跨会话的用户建模和个性化。Honcho 在 Hermes 内置记忆系统基础上，通过辩证推理实现深度用户建模。

## 训练与评估

- **[强化学习训练](/user-guide/features/rl-training)** — 从 Agent 会话生成轨迹数据，用于强化学习和模型微调。
- **[批量处理](/user-guide/features/batch-processing)** — 并行运行 Agent 处理数百个提示，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或评估。
