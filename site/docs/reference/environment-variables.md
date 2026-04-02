---
sidebar_position: 2
title: "环境变量"
description: "Hermes Agent 使用的所有环境变量完整参考"
---

# 环境变量参考

所有变量都写在 `~/.hermes/.env` 文件中。你也可以用 `hermes config set VAR value` 来设置它们。

## LLM 提供商

| 变量 | 说明 |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API 密钥（推荐用于灵活性） |
| `OPENROUTER_BASE_URL` | 覆盖 OpenRouter 兼容的基础 URL |
| `AI_GATEWAY_API_KEY` | Vercel AI Gateway API 密钥（[ai-gateway.vercel.sh](https://ai-gateway.vercel.sh)） |
| `AI_GATEWAY_BASE_URL` | 覆盖 AI Gateway 基础 URL（默认：`https://ai-gateway.vercel.sh/v1`） |
| `OPENAI_API_KEY` | 自定义 OpenAI 兼容端点的 API 密钥（与 `OPENAI_BASE_URL` 一起使用） |
| `OPENAI_BASE_URL` | 自定义端点的基础 URL（如 VLLM、SGLang 等） |
| `COPILOT_GITHUB_TOKEN` | Copilot API 的 GitHub 令牌 — 优先级最高（OAuth `gho_*` 或细粒度 PAT `github_pat_*`；经典 PAT `ghp_*` **不支持**） |
| `GH_TOKEN` | GitHub 令牌 — Copilot 的第二优先级（也被 `gh` CLI 使用） |
| `GITHUB_TOKEN` | GitHub 令牌 — Copilot 的第三优先级 |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot ACP CLI 二进制路径（默认：`copilot`） |
| `COPILOT_CLI_PATH` | `HERMES_COPILOT_ACP_COMMAND` 的别名 |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 Copilot ACP 参数（默认：`--acp --stdio`） |
| `COPILOT_ACP_BASE_URL` | 覆盖 Copilot ACP 基础 URL |
| `GLM_API_KEY` | z.ai / ZhipuAI GLM API 密钥（[z.ai](https://z.ai)） |
| `ZAI_API_KEY` | `GLM_API_KEY` 的别名 |
| `Z_AI_API_KEY` | `GLM_API_KEY` 的别名 |
| `GLM_BASE_URL` | 覆盖 z.ai 基础 URL（默认：`https://api.z.ai/api/paas/v4`） |
| `KIMI_API_KEY` | Kimi / Moonshot AI API 密钥（[moonshot.ai](https://platform.moonshot.ai)） |
| `KIMI_BASE_URL` | 覆盖 Kimi 基础 URL（默认：`https://api.moonshot.ai/v1`） |
| `MINIMAX_API_KEY` | MiniMax API 密钥 — 全球端点（[minimax.io](https://www.minimax.io)） |
| `MINIMAX_BASE_URL` | 覆盖 MiniMax 基础 URL（默认：`https://api.minimax.io/v1`） |
| `MINIMAX_CN_API_KEY` | MiniMax API 密钥 — 中国端点（[minimaxi.com](https://www.minimaxi.com)） |
| `MINIMAX_CN_BASE_URL` | 覆盖 MiniMax 中国基础 URL（默认：`https://api.minimaxi.com/v1`） |
| `KILOCODE_API_KEY` | Kilo Code API 密钥（[kilo.ai](https://kilo.ai)） |
| `KILOCODE_BASE_URL` | 覆盖 Kilo Code 基础 URL（默认：`https://api.kilo.ai/api/gateway`） |
| `HF_TOKEN` | Hugging Face 推理提供商令牌（[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)） |
| `HF_BASE_URL` | 覆盖 Hugging Face 基础 URL（默认：`https://router.huggingface.co/v1`） |
| `ANTHROPIC_API_KEY` | Anthropic Console API 密钥（[console.anthropic.com](https://console.anthropic.com/)） |
| `ANTHROPIC_TOKEN` | 手动或旧版 Anthropic OAuth/设置令牌覆盖 |
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API 密钥，用于 Qwen 模型（[modelstudio.console.alibabacloud.com](https://modelstudio.console.alibabacloud.com/)） |
| `DASHSCOPE_BASE_URL` | 自定义 DashScope 基础 URL（默认：`https://coding-intl.dashscope.aliyuncs.com/v1`） |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥，用于直接访问 DeepSeek（[platform.deepseek.com](https://platform.deepseek.com/api_keys)） |
| `DEEPSEEK_BASE_URL` | 自定义 DeepSeek API 基础 URL |
| `OPENCODE_ZEN_API_KEY` | OpenCode Zen API 密钥 — 按需付费访问精选模型（[opencode.ai](https://opencode.ai/auth)） |
| `OPENCODE_ZEN_BASE_URL` | 覆盖 OpenCode Zen 基础 URL |
| `OPENCODE_GO_API_KEY` | OpenCode Go API 密钥 — $10/月订阅开放模型（[opencode.ai](https://opencode.ai/auth)） |
| `OPENCODE_GO_BASE_URL` | 覆盖 OpenCode Go 基础 URL |
| `CLAUDE_CODE_OAUTH_TOKEN` | 如果手动导出，显式覆盖 Claude Code 令牌 |
| `HERMES_MODEL` | 优先使用的模型名称（在 `LLM_MODEL` 之前检查，由网关使用） |
| `LLM_MODEL` | 默认模型名称（当 config.yaml 中未设置时使用） |
| `VOICE_TOOLS_OPENAI_KEY` | OpenAI 语音转文本和文本转语音提供商的首选 OpenAI 密钥 |
| `HERMES_LOCAL_STT_COMMAND` | 可选的本地语音转文本命令模板。支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符 |
| `HERMES_LOCAL_STT_LANGUAGE` | 传递给 `HERMES_LOCAL_STT_COMMAND` 的默认语言，或自动检测的本地 `whisper` CLI 回退（默认：`en`） |
| `HERMES_HOME` | 覆盖 Hermes 配置目录（默认：`~/.hermes`）。也影响网关 PID 文件和 systemd 服务名，支持多实例并行运行 |

## 提供商认证（OAuth）

对于原生 Anthropic 认证，Hermes 优先使用 Claude Code 自带的凭证文件，因为这些凭证可以自动刷新。环境变量如 `ANTHROPIC_TOKEN` 仍然可用作手动覆盖，但不再是 Claude Pro/Max 登录的首选方式。

| 变量 | 说明 |
|----------|-------------|
| `HERMES_INFERENCE_PROVIDER` | 覆盖提供商选择：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`huggingface`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`、`kilocode`、`alibaba`、`deepseek`、`opencode-zen`、`opencode-go`、`ai-gateway`（默认：`auto`） |
| `HERMES_PORTAL_BASE_URL` | 覆盖 Nous Portal URL（用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 覆盖 Nous 推理 API URL |
| `HERMES_NOUS_MIN_KEY_TTL_SECONDS` | 重新生成 Agent 密钥前的最小 TTL（默认：1800 秒 = 30 分钟） |
| `HERMES_NOUS_TIMEOUT_SECONDS` | Nous 凭证/令牌流程的 HTTP 超时 |
| `HERMES_DUMP_REQUESTS` | 将 API 请求负载导出到日志文件（`true`/`false`） |
| `HERMES_PREFILL_MESSAGES_FILE` | 在调用 API 时注入的临时预填消息的 JSON 文件路径 |
| `HERMES_TIMEZONE` | IANA 时区覆盖（例如 `America/New_York`） |

## 工具 API

| 变量 | 说明 |
|----------|-------------|
| `PARALLEL_API_KEY` | AI 原生网页搜索（[parallel.ai](https://parallel.ai/)） |
| `FIRECRAWL_API_KEY` | 网页爬取（[firecrawl.dev](https://firecrawl.dev/)） |
| `FIRECRAWL_API_URL` | 自托管实例的自定义 Firecrawl API 端点（可选） |
| `TAVILY_API_KEY` | Tavily API 密钥，用于 AI 原生网页搜索、提取和爬取（[app.tavily.com](https://app.tavily.com/home)） |
| `EXA_API_KEY` | Exa API 密钥，用于 AI 原生网页搜索和内容（[exa.ai](https://exa.ai/)） |
| `BROWSERBASE_API_KEY` | 浏览器自动化（[browserbase.com](https://browserbase.com/)） |
| `BROWSERBASE_PROJECT_ID` | Browserbase 项目 ID |
| `BROWSER_USE_API_KEY` | Browser Use 云浏览器 API 密钥（[browser-use.com](https://browser-use.com/)） |
| `BROWSER_CDP_URL` | 本地浏览器的 Chrome DevTools 协议 URL（通过 `/browser connect` 设置，例如 `ws://localhost:9222`） |
| `BROWSER_INACTIVITY_TIMEOUT` | 浏览器会话无操作超时时间（秒） |
| `FAL_KEY` | 图像生成（[fal.ai](https://fal.ai/)） |
| `GROQ_API_KEY` | Groq Whisper 语音转文本 API 密钥（[groq.com](https://groq.com/)） |
| `ELEVENLABS_API_KEY` | ElevenLabs 高级 TTS 语音（[elevenlabs.io](https://elevenlabs.io/)） |
| `STT_GROQ_MODEL` | 覆盖 Groq 语音转文本模型（默认：`whisper-large-v3-turbo`） |
| `GROQ_BASE_URL` | 覆盖 Groq OpenAI 兼容的语音转文本端点 |
| `STT_OPENAI_MODEL` | 覆盖 OpenAI 语音转文本模型（默认：`whisper-1`） |
| `STT_OPENAI_BASE_URL` | 覆盖 OpenAI 兼容的语音转文本端点 |
| `GITHUB_TOKEN` | Skills Hub 的 GitHub 令牌（更高的 API 速率限制，技能发布） |
| `HONCHO_API_KEY` | 跨会话用户建模（[honcho.dev](https://honcho.dev/)） |
| `HONCHO_BASE_URL` | 自托管 Honcho 实例的基础 URL（默认：Honcho 云）。本地实例不需要 API 密钥 |
| `TINKER_API_KEY` | 强化学习训练（[tinker-console.thinkingmachines.ai](https://tinker-console.thinkingmachines.ai/)） |
| `WANDB_API_KEY` | 强化学习训练指标（[wandb.ai](https://wandb.ai/)） |
| `DAYTONA_API_KEY` | Daytona 云沙箱（[daytona.io](https://daytona.io/)） |

## 终端后端

| 变量 | 说明 |
|----------|-------------|
| `TERMINAL_ENV` | 后端类型：`local`、`docker`、`ssh`、`singularity`、`modal`、`daytona` |
| `TERMINAL_DOCKER_IMAGE` | Docker 镜像（默认：`python:3.11`） |
| `TERMINAL_DOCKER_FORWARD_ENV` | JSON 数组，显式转发到 Docker 终端会话的环境变量名。注意：技能声明的 `required_environment_variables` 会自动转发 — 只有未被任何技能声明的变量才需要这里配置。 |
| `TERMINAL_DOCKER_VOLUMES` | 额外的 Docker 卷挂载（逗号分隔的 `host:container` 对） |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | 高级选项：将启动时的当前工作目录挂载到 Docker 的 `/workspace`（`true`/`false`，默认：`false`） |
| `TERMINAL_SINGULARITY_IMAGE` | Singularity 镜像或 `.sif` 路径 |
| `TERMINAL_MODAL_IMAGE` | Modal 容器镜像 |
| `TERMINAL_DAYTONA_IMAGE` | Daytona 沙箱镜像 |
| `TERMINAL_TIMEOUT` | 命令超时时间（秒） |
| `TERMINAL_LIFETIME_SECONDS` | 终端会话最大存活时间（秒） |
| `TERMINAL_CWD` | 所有终端会话的工作目录 |
| `SUDO_PASSWORD` | 启用 sudo 无需交互式提示 |
## SSH 后端

| 变量 | 说明 |
|----------|-------------|
| `TERMINAL_SSH_HOST` | 远程服务器主机名 |
| `TERMINAL_SSH_USER` | SSH 用户名 |
| `TERMINAL_SSH_PORT` | SSH 端口（默认：22） |
| `TERMINAL_SSH_KEY` | 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 的持久 shell 设置（默认：跟随 `TERMINAL_PERSISTENT_SHELL`） |

## 容器资源（Docker、Singularity、Modal、Daytona）

| 变量 | 说明 |
|----------|-------------|
| `TERMINAL_CONTAINER_CPU` | CPU 核心数（默认：1） |
| `TERMINAL_CONTAINER_MEMORY` | 内存大小，单位 MB（默认：5120） |
| `TERMINAL_CONTAINER_DISK` | 磁盘大小，单位 MB（默认：51200） |
| `TERMINAL_CONTAINER_PERSISTENT` | 跨会话持久化容器文件系统（默认：`true`） |
| `TERMINAL_SANDBOX_DIR` | 主机上用于工作区和覆盖层的目录（默认：`~/.hermes/sandboxes/`） |

## 持久 Shell

| 变量 | 说明 |
|----------|-------------|
| `TERMINAL_PERSISTENT_SHELL` | 为非本地后端启用持久 shell（默认：`true`）。也可以通过 config.yaml 中的 `terminal.persistent_shell` 设置 |
| `TERMINAL_LOCAL_PERSISTENT` | 为本地后端启用持久 shell（默认：`false`） |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 后端的持久 shell 设置（默认：跟随 `TERMINAL_PERSISTENT_SHELL`） |

## 消息传递

| 变量 | 说明 |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram 机器人令牌（来自 @BotFather） |
| `TELEGRAM_ALLOWED_USERS` | 允许使用机器人的用户 ID，逗号分隔 |
| `TELEGRAM_HOME_CHANNEL` | 默认的 Telegram 聊天/频道，用于定时任务推送 |
| `TELEGRAM_HOME_CHANNEL_NAME` | Telegram 主页频道的显示名称 |
| `TELEGRAM_WEBHOOK_URL` | 公共 HTTPS URL，用于 webhook 模式（启用 webhook 替代轮询） |
| `TELEGRAM_WEBHOOK_PORT` | webhook 服务器本地监听端口（默认：`8443`） |
| `TELEGRAM_WEBHOOK_SECRET` | 用于验证更新来自 Telegram 的密钥 |
| `DISCORD_BOT_TOKEN` | Discord 机器人令牌 |
| `DISCORD_ALLOWED_USERS` | 允许使用机器人的 Discord 用户 ID，逗号分隔 |
| `DISCORD_HOME_CHANNEL` | 默认的 Discord 频道，用于定时任务推送 |
| `DISCORD_HOME_CHANNEL_NAME` | Discord 主页频道的显示名称 |
| `DISCORD_REQUIRE_MENTION` | 在服务器频道中回复前是否需要 @提及 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 不需要 @提及即可回复的频道 ID，逗号分隔 |
| `DISCORD_AUTO_THREAD` | 支持时自动为长回复创建线程 |
| `SLACK_BOT_TOKEN` | Slack 机器人令牌（`xoxb-...`） |
| `SLACK_APP_TOKEN` | Slack 应用级令牌（`xapp-...`，Socket 模式必需） |
| `SLACK_ALLOWED_USERS` | 允许使用机器人的 Slack 用户 ID，逗号分隔 |
| `SLACK_HOME_CHANNEL` | 默认的 Slack 频道，用于定时任务推送 |
| `SLACK_HOME_CHANNEL_NAME` | Slack 主页频道的显示名称 |
| `WHATSAPP_ENABLED` | 启用 WhatsApp 桥接（`true`/`false`） |
| `WHATSAPP_MODE` | `bot`（独立号码）或 `self-chat`（自聊模式） |
| `WHATSAPP_ALLOWED_USERS` | 允许的电话号码（带国家码，无 `+`），逗号分隔，或 `*` 允许所有发送者 |
| `WHATSAPP_ALLOW_ALL_USERS` | 允许所有 WhatsApp 发送者，无需白名单（`true`/`false`） |
| `WHATSAPP_DEBUG` | 在桥接中记录原始消息事件以便调试（`true`/`false`） |
| `SIGNAL_HTTP_URL` | signal-cli 守护进程 HTTP 端点（例如 `http://127.0.0.1:8080`） |
| `SIGNAL_ACCOUNT` | 机器人电话号码，E.164 格式 |
| `SIGNAL_ALLOWED_USERS` | 允许的 E.164 电话号码或 UUID，逗号分隔 |
| `SIGNAL_GROUP_ALLOWED_USERS` | 允许的群组 ID，逗号分隔，或 `*` 表示所有群组 |
| `SIGNAL_HOME_CHANNEL_NAME` | Signal 主页频道的显示名称 |
| `SIGNAL_IGNORE_STORIES` | 忽略 Signal 的故事/状态更新 |
| `SIGNAL_ALLOW_ALL_USERS` | 允许所有 Signal 用户，无需白名单 |
| `TWILIO_ACCOUNT_SID` | Twilio 账户 SID（与电话技能共享） |
| `TWILIO_AUTH_TOKEN` | Twilio 认证令牌（与电话技能共享） |
| `TWILIO_PHONE_NUMBER` | Twilio 电话号码，E.164 格式（与电话技能共享） |
| `SMS_WEBHOOK_PORT` | 用于接收短信的 webhook 监听端口（默认：`8080`） |
| `SMS_ALLOWED_USERS` | 允许聊天的 E.164 电话号码，逗号分隔 |
| `SMS_ALLOW_ALL_USERS` | 允许所有短信发送者，无需白名单 |
| `SMS_HOME_CHANNEL` | 用于定时任务/通知推送的电话号码 |
| `SMS_HOME_CHANNEL_NAME` | SMS 主页频道的显示名称 |
| `EMAIL_ADDRESS` | 邮件网关适配器的邮箱地址 |
| `EMAIL_PASSWORD` | 邮箱密码或应用专用密码 |
| `EMAIL_IMAP_HOST` | 邮件适配器的 IMAP 主机名 |
| `EMAIL_IMAP_PORT` | IMAP 端口 |
| `EMAIL_SMTP_HOST` | 邮件适配器的 SMTP 主机名 |
| `EMAIL_SMTP_PORT` | SMTP 端口 |
| `EMAIL_ALLOWED_USERS` | 允许给机器人发邮件的邮箱地址，逗号分隔 |
| `EMAIL_HOME_ADDRESS` | 主动邮件发送的默认收件人 |
| `EMAIL_HOME_ADDRESS_NAME` | 邮件主页目标的显示名称 |
| `EMAIL_POLL_INTERVAL` | 邮件轮询间隔，单位秒 |
| `EMAIL_ALLOW_ALL_USERS` | 允许所有入站邮件发送者 |
| `DINGTALK_CLIENT_ID` | 钉钉机器人 AppKey，来自开发者门户 ([open.dingtalk.com](https://open.dingtalk.com)) |
| `DINGTALK_CLIENT_SECRET` | 钉钉机器人 AppSecret，来自开发者门户 |
| `DINGTALK_ALLOWED_USERS` | 允许给机器人发消息的钉钉用户 ID，逗号分隔 |
| `FEISHU_APP_ID` | 飞书/Lark 机器人 App ID，来自 [open.feishu.cn](https://open.feishu.cn/) |
| `FEISHU_APP_SECRET` | 飞书/Lark 机器人 App Secret |
| `FEISHU_DOMAIN` | `feishu`（中国）或 `lark`（国际），默认：`feishu` |
| `FEISHU_CONNECTION_MODE` | `websocket`（推荐）或 `webhook`，默认：`websocket` |
| `FEISHU_ENCRYPT_KEY` | webhook 模式下的可选加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | webhook 模式下的可选验证令牌 |
| `FEISHU_ALLOWED_USERS` | 允许给机器人发消息的飞书用户 ID，逗号分隔 |
| `FEISHU_HOME_CHANNEL` | 飞书聊天 ID，用于定时任务和通知 |
| `WECOM_BOT_ID` | 企业微信 AI 机器人 ID，来自管理后台 |
| `WECOM_SECRET` | 企业微信 AI 机器人密钥 |
| `WECOM_WEBSOCKET_URL` | 自定义 WebSocket URL（默认：`wss://openws.work.weixin.qq.com`） |
| `WECOM_ALLOWED_USERS` | 允许给机器人发消息的企业微信用户 ID，逗号分隔 |
| `WECOM_HOME_CHANNEL` | 企业微信聊天 ID，用于定时任务和通知 |
| `MATTERMOST_URL` | Mattermost 服务器 URL（例如 `https://mm.example.com`） |
| `MATTERMOST_TOKEN` | Mattermost 机器人令牌或个人访问令牌 |
| `MATTERMOST_ALLOWED_USERS` | 允许给机器人发消息的 Mattermost 用户 ID，逗号分隔 |
| `MATTERMOST_HOME_CHANNEL` | 用于主动消息推送（定时任务、通知）的频道 ID |
| `MATTERMOST_REQUIRE_MENTION` | 频道中是否需要 `@提及` 才回复（默认：`true`）。设置为 `false` 则回复所有消息。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | 不需要 `@提及` 即可回复的频道 ID，逗号分隔 |
| `MATTERMOST_REPLY_MODE` | 回复样式：`thread`（线程回复）或 `off`（平铺消息，默认） |
| `MATRIX_HOMESERVER` | Matrix homeserver URL（例如 `https://matrix.org`） |
| `MATRIX_ACCESS_TOKEN` | Matrix 机器人认证用访问令牌 |
| `MATRIX_USER_ID` | Matrix 用户 ID（例如 `@hermes:matrix.org`）— 密码登录必需，使用访问令牌时可选 |
| `MATRIX_PASSWORD` | Matrix 密码（作为访问令牌的替代） |
| `MATRIX_ALLOWED_USERS` | 允许给机器人发消息的 Matrix 用户 ID，逗号分隔（例如 `@alice:matrix.org`） |
| `MATRIX_HOME_ROOM` | 用于主动消息推送的房间 ID（例如 `!abc123:matrix.org`） |
| `MATRIX_ENCRYPTION` | 是否启用端到端加密（`true`/`false`，默认：`false`） |
| `HASS_TOKEN` | Home Assistant 长期访问令牌（启用 HA 平台和工具） |
| `HASS_URL` | Home Assistant URL（默认：`http://homeassistant.local:8123`） |
| `WEBHOOK_ENABLED` | 启用 webhook 平台适配器（`true`/`false`） |
| `WEBHOOK_PORT` | 接收 webhook 的 HTTP 服务器端口（默认：`8644`） |
| `WEBHOOK_SECRET` | 用于 webhook 签名验证的全局 HMAC 密钥（当路由未指定时作为备用） |
| `API_SERVER_ENABLED` | 启用兼容 OpenAI 的 API 服务器（`true`/`false`）。与其他平台并行运行。 |
| `API_SERVER_KEY` | API 服务器认证用 Bearer 令牌。强烈推荐；任何网络可访问部署必需。 |
| `API_SERVER_CORS_ORIGINS` | 允许直接调用 API 服务器的浏览器来源，逗号分隔（例如 `http://localhost:3000,http://127.0.0.1:3000`）。默认禁用。 |
| `API_SERVER_PORT` | API 服务器端口（默认：`8642`） |
| `API_SERVER_HOST` | API 服务器绑定地址（默认：`127.0.0.1`）。仅在配合 `API_SERVER_KEY` 和严格的 `API_SERVER_CORS_ORIGINS` 白名单时，使用 `0.0.0.0` 以允许网络访问。 |
| `MESSAGING_CWD` | 消息模式下终端命令的工作目录（默认：`~`） |
| `GATEWAY_ALLOWED_USERS` | 允许跨所有平台使用的用户 ID，逗号分隔 |
| `GATEWAY_ALLOW_ALL_USERS` | 允许所有用户，无需白名单（`true`/`false`，默认：`false`） |
## Agent 行为

| 变量 | 说明 |
|----------|-------------|
| `HERMES_MAX_ITERATIONS` | 每次对话最大调用工具次数（默认：90） |
| `HERMES_TOOL_PROGRESS` | 已废弃的工具进度显示兼容变量。建议使用 `config.yaml` 中的 `display.tool_progress`。 |
| `HERMES_TOOL_PROGRESS_MODE` | 已废弃的工具进度模式兼容变量。建议使用 `config.yaml` 中的 `display.tool_progress`。 |
| `HERMES_HUMAN_DELAY_MODE` | 响应节奏：`off`/`natural`/`custom` |
| `HERMES_HUMAN_DELAY_MIN_MS` | 自定义延迟范围最小值（毫秒） |
| `HERMES_HUMAN_DELAY_MAX_MS` | 自定义延迟范围最大值（毫秒） |
| `HERMES_QUIET` | 抑制非必要输出（`true`/`false`） |
| `HERMES_API_TIMEOUT` | LLM API 调用超时时间，单位秒（默认：`900`） |
| `HERMES_EXEC_ASK` | 网关模式下启用执行确认提示（`true`/`false`） |
| `HERMES_ENABLE_PROJECT_PLUGINS` | 启用自动发现仓库本地插件，路径为 `./.hermes/plugins/`（`true`/`false`，默认：`false`） |
| `HERMES_BACKGROUND_NOTIFICATIONS` | 网关后台进程通知模式：`all`（默认）、`result`、`error`、`off` |
| `HERMES_EPHEMERAL_SYSTEM_PROMPT` | 在 API 调用时注入的临时系统提示（不会持久化到会话） |

## 会话设置

| 变量 | 说明 |
|----------|-------------|
| `SESSION_IDLE_MINUTES` | 会话空闲多少分钟后重置（默认：1440） |
| `SESSION_RESET_HOUR` | 每日重置时间，24 小时制（默认：4，即凌晨4点） |

## 上下文压缩（仅限 config.yaml）

上下文压缩仅通过 `config.yaml` 中的 `compression` 部分配置——没有对应的环境变量。

```yaml
compression:
  enabled: true
  threshold: 0.50
  summary_model: google/gemini-3-flash-preview
  summary_provider: auto
  summary_base_url: null  # 自定义兼容 OpenAI 的摘要端点
```

## 辅助任务覆盖

| 变量 | 说明 |
|----------|-------------|
| `AUXILIARY_VISION_PROVIDER` | 视觉任务覆盖提供商 |
| `AUXILIARY_VISION_MODEL` | 视觉任务覆盖模型 |
| `AUXILIARY_VISION_BASE_URL` | 视觉任务直接使用的兼容 OpenAI 端点 |
| `AUXILIARY_VISION_API_KEY` | 与 `AUXILIARY_VISION_BASE_URL` 配套的 API 密钥 |
| `AUXILIARY_WEB_EXTRACT_PROVIDER` | 网页提取/摘要任务覆盖提供商 |
| `AUXILIARY_WEB_EXTRACT_MODEL` | 网页提取/摘要任务覆盖模型 |
| `AUXILIARY_WEB_EXTRACT_BASE_URL` | 网页提取/摘要任务直接使用的兼容 OpenAI 端点 |
| `AUXILIARY_WEB_EXTRACT_API_KEY` | 与 `AUXILIARY_WEB_EXTRACT_BASE_URL` 配套的 API 密钥 |

对于任务专用的直接端点，Hermes 会使用任务配置的 API 密钥或 `OPENAI_API_KEY`，不会复用 `OPENROUTER_API_KEY`。

## 备用模型（仅限 config.yaml）

主模型的备用配置仅通过 `config.yaml` 设置——没有对应环境变量。添加 `fallback_model` 部分，包含 `provider` 和 `model` 键，即可在主模型出错时自动切换。

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

完整详情请参见 [Fallback Providers](/user-guide/features/fallback-providers)。

## 提供商路由（仅限 config.yaml）

这些配置放在 `~/.hermes/config.yaml` 的 `provider_routing` 部分：

| 键 | 说明 |
|-----|-------------|
| `sort` | 提供商排序方式：`"price"`（默认）、`"throughput"` 或 `"latency"` |
| `only` | 允许的提供商 slug 列表（例如：`["anthropic", "google"]`） |
| `ignore` | 忽略的提供商 slug 列表 |
| `order` | 按顺序尝试的提供商 slug 列表 |
| `require_parameters` | 仅使用支持所有请求参数的提供商（`true`/`false`） |
| `data_collection` | `"allow"`（默认）或 `"deny"`，排除存储数据的提供商 |

:::tip
使用 `hermes config set` 来设置环境变量——它会自动保存到正确的文件（机密保存到 `.env`，其他配置保存到 `config.yaml`）。
:::
