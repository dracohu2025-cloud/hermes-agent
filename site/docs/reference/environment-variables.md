---
sidebar_position: 2
title: "环境变量"
description: "Hermes Agent 使用的所有环境变量完整参考"
---

# 环境变量参考

所有变量都保存在 `~/.hermes/.env` 中。你也可以通过 `hermes config set VAR value` 来设置它们。

## LLM 提供商

| 变量 | 描述 |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API 密钥（推荐使用，灵活性最高） |
| `OPENROUTER_BASE_URL` | 覆盖 OpenRouter 兼容的 Base URL |
| `AI_GATEWAY_API_KEY` | Vercel AI Gateway API 密钥 ([ai-gateway.vercel.sh](https://ai-gateway.vercel.sh)) |
| `AI_GATEWAY_BASE_URL` | 覆盖 AI Gateway Base URL（默认：`https://ai-gateway.vercel.sh/v1`） |
| `OPENAI_API_KEY` | 自定义 OpenAI 兼容端点的 API 密钥（与 `OPENAI_BASE_URL` 配合使用） |
| `OPENAI_BASE_URL` | 自定义端点的 Base URL（VLLM, SGLang 等） |
| `COPILOT_GITHUB_TOKEN` | GitHub Copilot API 令牌 —— 第一优先级（支持 OAuth `gho_*` 或 fine-grained PAT `github_pat_*`；**不支持** 经典 PAT `ghp_*`） |
| `GH_TOKEN` | GitHub 令牌 —— Copilot 的第二优先级（也被 `gh` CLI 使用） |
| `GITHUB_TOKEN` | GitHub 令牌 —— Copilot 的第三优先级 |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot ACP CLI 二进制路径（默认：`copilot`） |
| `COPILOT_CLI_PATH` | `HERMES_COPILOT_ACP_COMMAND` 的别名 |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 Copilot ACP 参数（默认：`--acp --stdio`） |
| `COPILOT_ACP_BASE_URL` | 覆盖 Copilot ACP Base URL |
| `GLM_API_KEY` | z.ai / 智谱 AI GLM API 密钥 ([z.ai](https://z.ai)) |
| `ZAI_API_KEY` | `GLM_API_KEY` 的别名 |
| `Z_AI_API_KEY` | `GLM_API_KEY` 的别名 |
| `GLM_BASE_URL` | 覆盖 z.ai Base URL（默认：`https://api.z.ai/api/paas/v4`） |
| `KIMI_API_KEY` | Kimi / Moonshot AI API 密钥 ([moonshot.ai](https://platform.moonshot.ai)) |
| `KIMI_BASE_URL` | 覆盖 Kimi Base URL（默认：`https://api.moonshot.ai/v1`） |
| `MINIMAX_API_KEY` | MiniMax API 密钥 —— 全球端点 ([minimax.io](https://www.minimax.io)) |
| `MINIMAX_BASE_URL` | 覆盖 MiniMax Base URL（默认：`https://api.minimax.io/v1`） |
| `MINIMAX_CN_API_KEY` | MiniMax API 密钥 —— 中国端点 ([minimaxi.com](https://www.minimaxi.com)) |
| `MINIMAX_CN_BASE_URL` | 覆盖 MiniMax 中国 Base URL（默认：`https://api.minimaxi.com/v1`） |
| `KILOCODE_API_KEY` | Kilo Code API 密钥 ([kilo.ai](https://kilo.ai)) |
| `KILOCODE_BASE_URL` | 覆盖 Kilo Code Base URL（默认：`https://api.kilo.ai/api/gateway`） |
| `HF_TOKEN` | Hugging Face 推理提供商令牌 ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)) |
| `HF_BASE_URL` | 覆盖 Hugging Face Base URL（默认：`https://router.huggingface.co/v1`） |
| `GOOGLE_API_KEY` | Google AI Studio API 密钥 ([aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)) |
| `GEMINI_API_KEY` | `GOOGLE_API_KEY` 的别名 |
| `GEMINI_BASE_URL` | 覆盖 Google AI Studio Base URL |
| `ANTHROPIC_API_KEY` | Anthropic Console API 密钥 ([console.anthropic.com](https://console.anthropic.com/)) |
| `ANTHROPIC_TOKEN` | 手动或旧版 Anthropic OAuth/setup-token 覆盖 |
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API 密钥，用于通义千问模型 ([modelstudio.console.alibabacloud.com](https://modelstudio.console.alibabacloud.com/)) |
| `DASHSCOPE_BASE_URL` | 自定义 DashScope Base URL（默认：`https://coding-intl.dashscope.aliyuncs.com/v1`） |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥，用于直接访问 DeepSeek ([platform.deepseek.com](https://platform.deepseek.com/api_keys)) |
| `DEEPSEEK_BASE_URL` | 自定义 DeepSeek API Base URL |
| `OPENCODE_ZEN_API_KEY` | OpenCode Zen API 密钥 —— 按量付费访问精选模型 ([opencode.ai](https://opencode.ai/auth)) |
| `OPENCODE_ZEN_BASE_URL` | 覆盖 OpenCode Zen Base URL |
| `OPENCODE_GO_API_KEY` | OpenCode Go API 密钥 —— 每月 10 美元订阅开放模型 ([opencode.ai](https://opencode.ai/auth)) |
| `OPENCODE_GO_BASE_URL` | 覆盖 OpenCode Go Base URL |
| `CLAUDE_CODE_OAUTH_TOKEN` | 如果你手动导出了 Claude Code 令牌，可在此显式覆盖 |
| `HERMES_MODEL` | 首选模型名称（在 `LLM_MODEL` 之前检查，由 gateway 使用） |
| `LLM_MODEL` | 默认模型名称（当 config.yaml 中未设置时的回退选项） |
| `VOICE_TOOLS_OPENAI_KEY` | 用于 OpenAI 语音转文本和文本转语音提供商的首选 OpenAI 密钥 |
| `HERMES_LOCAL_STT_COMMAND` | 可选的本地语音转文本命令模板。支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符 |
| `HERMES_LOCAL_STT_LANGUAGE` | 传递给 `HERMES_LOCAL_STT_COMMAND` 的默认语言，或自动检测的本地 `whisper` CLI 回退语言（默认：`en`） |
| `HERMES_HOME` | 覆盖 Hermes 配置目录（默认：`~/.hermes`）。同时会影响 gateway PID 文件和 systemd 服务名称，以便多个安装实例可以并发运行 |

## 提供商认证 (OAuth)

对于原生的 Anthropic 认证，如果存在 Claude Code 自身的凭据文件，Hermes 会优先使用它们，因为这些凭据可以自动刷新。诸如 `ANTHROPIC_TOKEN` 之类的环境变量仍可作为手动覆盖手段，但不再是 Claude Pro/Max 登录的首选路径。

| 变量 | 描述 |
|----------|-------------|
| `HERMES_INFERENCE_PROVIDER` | 覆盖提供商选择：`auto`, `openrouter`, `nous`, `openai-codex`, `copilot`, `copilot-acp`, `anthropic`, `huggingface`, `zai`, `kimi-coding`, `minimax`, `minimax-cn`, `kilocode`, `alibaba`, `deepseek`, `opencode-zen`, `opencode-go`, `ai-gateway`（默认：`auto`） |
| `HERMES_PORTAL_BASE_URL` | 覆盖 Nous Portal URL（用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 覆盖 Nous 推理 API URL |
| `HERMES_NOUS_MIN_KEY_TTL_SECONDS` | 重新生成 Agent 密钥前的最小 TTL（默认：1800 = 30分钟） |
| `HERMES_NOUS_TIMEOUT_SECONDS` | Nous 凭据 / 令牌流程的 HTTP 超时时间 |
| `HERMES_DUMP_REQUESTS` | 将 API 请求负载转储到日志文件（`true`/`false`） |
| `HERMES_PREFILL_MESSAGES_FILE` | 在 API 调用时注入的临时预填消息 JSON 文件的路径 |
| `HERMES_TIMEZONE` | IANA 时区覆盖（例如 `America/New_York`） |

## 工具 API

| 变量 | 描述 |
|----------|-------------|
| `PARALLEL_API_KEY` | AI 原生网络搜索 ([parallel.ai](https://parallel.ai/)) |
| `FIRECRAWL_API_KEY` | 网页抓取和云端浏览器 ([firecrawl.dev](https://firecrawl.dev/)) |
| `FIRECRAWL_API_URL` | 用于自托管实例的自定义 Firecrawl API 端点（可选） |
| `TAVILY_API_KEY` | Tavily API 密钥，用于 AI 原生网络搜索、提取和爬取 ([app.tavily.com](https://app.tavily.com/home)) |
| `EXA_API_KEY` | Exa API 密钥，用于 AI 原生网络搜索和内容获取 ([exa.ai](https://exa.ai/)) |
| `BROWSERBASE_API_KEY` | 浏览器自动化 ([browserbase.com](https://browserbase.com/)) |
| `BROWSERBASE_PROJECT_ID` | Browserbase 项目 ID |
| `BROWSER_USE_API_KEY` | Browser Use 云端浏览器 API 密钥 ([browser-use.com](https://browser-use.com/)) |
| `FIRECRAWL_BROWSER_TTL` | Firecrawl 浏览器会话 TTL，单位秒（默认：300） |
| `BROWSER_CDP_URL` | 本地浏览器的 Chrome DevTools Protocol URL（通过 `/browser connect` 设置，例如 `ws://localhost:9222`） |
| `CAMOFOX_URL` | Camofox 本地反检测浏览器 URL（默认：`http://localhost:9377`） |
| `BROWSER_INACTIVITY_TIMEOUT` | 浏览器会话空闲超时时间（秒） |
| `FAL_KEY` | 图像生成 ([fal.ai](https://fal.ai/)) |
| `GROQ_API_KEY` | Groq Whisper STT API 密钥 ([groq.com](https://groq.com/)) |
| `ELEVENLABS_API_KEY` | ElevenLabs 高级 TTS 语音 ([elevenlabs.io](https://elevenlabs.io/)) |
| `STT_GROQ_MODEL` | 覆盖 Groq STT 模型（默认：`whisper-large-v3-turbo`） |
| `GROQ_BASE_URL` | 覆盖 Groq OpenAI 兼容的 STT 端点 |
| `STT_OPENAI_MODEL` | 覆盖 OpenAI STT 模型（默认：`whisper-1`） |
| `STT_OPENAI_BASE_URL` | 覆盖 OpenAI 兼容的 STT 端点 |
| `GITHUB_TOKEN` | 用于 Skills Hub 的 GitHub 令牌（更高的 API 速率限制，技能发布） |
| `HONCHO_API_KEY` | 跨会话用户建模 ([honcho.dev](https://honcho.dev/)) |
| `HONCHO_BASE_URL` | 自托管 Honcho 实例的 Base URL（默认：Honcho 云端）。本地实例不需要 API 密钥 |
| `SUPERMEMORY_API_KEY` | 具有个人资料召回和会话摄取的语义长期记忆 ([supermemory.ai](https://supermemory.ai)) |
| `TINKER_API_KEY` | RL 训练 ([tinker-console.thinkingmachines.ai](https://tinker-console.thinkingmachines.ai/)) |
| `WANDB_API_KEY` | RL 训练指标 ([wandb.ai](https://wandb.ai/)) |
| `DAYTONA_API_KEY` | Daytona 云端沙箱 ([daytona.io](https://daytona.io/)) |
## Terminal 后端

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_ENV` | 后端类型：`local`, `docker`, `ssh`, `singularity`, `modal`, `daytona` |
| `TERMINAL_DOCKER_IMAGE` | Docker 镜像（默认：`nikolaik/python-nodejs:python3.11-nodejs20`） |
| `TERMINAL_DOCKER_FORWARD_ENV` | 要显式转发到 Docker terminal 会话的环境变量名称的 JSON 数组。注意：skill 声明的 `required_environment_variables` 会自动转发 —— 你只需要为未被任何 skill 声明的变量设置此项。 |
| `TERMINAL_DOCKER_VOLUMES` | 额外的 Docker 卷挂载（逗号分隔的 `host:container` 对） |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | 高级选项：将启动时的当前工作目录挂载到 Docker 的 `/workspace`（`true`/`false`，默认：`false`） |
| `TERMINAL_SINGULARITY_IMAGE` | Singularity 镜像或 `.sif` 路径 |
| `TERMINAL_MODAL_IMAGE` | Modal 容器镜像 |
| `TERMINAL_DAYTONA_IMAGE` | Daytona 沙箱镜像 |
| `TERMINAL_TIMEOUT` | 命令超时时间（秒） |
| `TERMINAL_LIFETIME_SECONDS` | terminal 会话的最大存活时间（秒） |
| `TERMINAL_CWD` | 所有 terminal 会话的工作目录 |
| `SUDO_PASSWORD` | 启用 sudo 而无需交互式提示 |

对于云沙箱后端，持久化是面向文件系统的。`TERMINAL_LIFETIME_SECONDS` 控制 Hermes 何时清理空闲的 terminal 会话，随后的恢复可能会重新创建沙箱，而不是保持相同的活动进程运行。

## SSH 后端

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_SSH_HOST` | 远程服务器主机名 |
| `TERMINAL_SSH_USER` | SSH 用户名 |
| `TERMINAL_SSH_PORT` | SSH 端口（默认：22） |
| `TERMINAL_SSH_KEY` | 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 的持久化 shell 设置（默认：遵循 `TERMINAL_PERSISTENT_SHELL`） |

## 容器资源 (Docker, Singularity, Modal, Daytona)

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_CONTAINER_CPU` | CPU 核心数（默认：1） |
| `TERMINAL_CONTAINER_MEMORY` | 内存大小，单位 MB（默认：5120） |
| `TERMINAL_CONTAINER_DISK` | 磁盘大小，单位 MB（默认：51200） |
| `TERMINAL_CONTAINER_PERSISTENT` | 跨会话持久化容器文件系统（默认：`true`） |
| `TERMINAL_SANDBOX_DIR` | 用于工作区和叠加层的宿主机目录（默认：`~/.hermes/sandboxes/`） |

## 持久化 Shell

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_PERSISTENT_SHELL` | 为非本地后端启用持久化 shell（默认：`true`）。也可通过 config.yaml 中的 `terminal.persistent_shell` 设置 |
| `TERMINAL_LOCAL_PERSISTENT` | 为本地后端启用持久化 shell（默认：`false`） |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 后端的持久化 shell 设置（默认：遵循 `TERMINAL_PERSISTENT_SHELL`） |

## 消息传递 (Messaging)

| 变量 | 描述 |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token（来自 @BotFather） |
| `TELEGRAM_ALLOWED_USERS` | 允许使用 bot 的用户 ID，逗号分隔 |
| `TELEGRAM_HOME_CHANNEL` | 用于定时任务（cron）投递的默认 Telegram 聊天/频道 |
| `TELEGRAM_HOME_CHANNEL_NAME` | Telegram 主频道的显示名称 |
| `TELEGRAM_WEBHOOK_URL` | Webhook 模式的公开 HTTPS URL（启用 Webhook 而非轮询） |
| `TELEGRAM_WEBHOOK_PORT` | Webhook 服务器的本地监听端口（默认：`8443`） |
| `TELEGRAM_WEBHOOK_SECRET` | 用于验证更新来自 Telegram 的密钥令牌 |
| `TELEGRAM_REACTIONS` | 在处理消息期间启用表情符号回应（默认：`false`） |
| `DISCORD_BOT_TOKEN` | Discord bot token |
| `DISCORD_ALLOWED_USERS` | 允许使用 bot 的 Discord 用户 ID，逗号分隔 |
| `DISCORD_HOME_CHANNEL` | 用于定时任务投递的默认 Discord 频道 |
| `DISCORD_HOME_CHANNEL_NAME` | Discord 主频道的显示名称 |
| `DISCORD_REQUIRE_MENTION` | 在服务器频道中响应前是否需要 @提及 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 不需要提及即可响应的频道 ID，逗号分隔 |
| `DISCORD_AUTO_THREAD` | 在支持时自动为长回复创建线程 |
| `DISCORD_REACTIONS` | 在处理消息期间启用表情符号回应（默认：`true`） |
| `DISCORD_IGNORED_CHANNELS` | Bot 永远不响应的频道 ID，逗号分隔 |
| `DISCORD_NO_THREAD_CHANNELS` | Bot 响应时不自动创建线程的频道 ID，逗号分隔 |
| `SLACK_BOT_TOKEN` | Slack bot token (`xoxb-...`) |
| `SLACK_APP_TOKEN` | Slack 应用级令牌（`xapp-...`，Socket Mode 必需） |
| `SLACK_ALLOWED_USERS` | 允许的 Slack 用户 ID，逗号分隔 |
| `SLACK_HOME_CHANNEL` | 用于定时任务投递的默认 Slack 频道 |
| `SLACK_HOME_CHANNEL_NAME` | Slack 主频道的显示名称 |
| `WHATSAPP_ENABLED` | 启用 WhatsApp 桥接（`true`/`false`） |
| `WHATSAPP_MODE` | `bot`（独立号码）或 `self-chat`（给自己发消息） |
| `WHATSAPP_ALLOWED_USERS` | 逗号分隔的电话号码（带国家代码，不带 `+`），或使用 `*` 允许所有发送者 |
| `WHATSAPP_ALLOW_ALL_USERS` | 允许所有 WhatsApp 发送者而无需白名单（`true`/`false`） |
| `WHATSAPP_DEBUG` | 在桥接器中记录原始消息事件以进行故障排除（`true`/`false`） |
| `SIGNAL_HTTP_URL` | signal-cli 守护进程 HTTP 端点（例如 `http://127.0.0.1:8080`） |
| `SIGNAL_ACCOUNT` | E.164 格式的 Bot 电话号码 |
| `SIGNAL_ALLOWED_USERS` | 逗号分隔的 E.164 电话号码或 UUID |
| `SIGNAL_GROUP_ALLOWED_USERS` | 逗号分隔的群组 ID，或使用 `*` 代表所有群组 |
| `SIGNAL_HOME_CHANNEL_NAME` | Signal 主频道的显示名称 |
| `SIGNAL_IGNORE_STORIES` | 忽略 Signal 动态/状态更新 |
| `SIGNAL_ALLOW_ALL_USERS` | 允许所有 Signal 用户而无需白名单 |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID（与电话 skill 共享） |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token（与电话 skill 共享） |
| `TWILIO_PHONE_NUMBER` | E.164 格式的 Twilio 电话号码（与电话 skill 共享） |
| `SMS_WEBHOOK_PORT` | 接收短信的 Webhook 监听端口（默认：`8080`） |
| `SMS_ALLOWED_USERS` | 允许聊天的 E.164 电话号码，逗号分隔 |
| `SMS_ALLOW_ALL_USERS` | 允许所有短信发送者而无需白名单 |
| `SMS_HOME_CHANNEL` | 用于定时任务/通知投递的电话号码 |
| `SMS_HOME_CHANNEL_NAME` | SMS 主频道的显示名称 |
| `EMAIL_ADDRESS` | 邮件网关适配器的电子邮件地址 |
| `EMAIL_PASSWORD` | 邮箱账号密码或应用专用密码 |
| `EMAIL_IMAP_HOST` | 邮件适配器的 IMAP 主机名 |
| `EMAIL_IMAP_PORT` | IMAP 端口 |
| `EMAIL_SMTP_HOST` | 邮件适配器的 SMTP 主机名 |
| `EMAIL_SMTP_PORT` | SMTP 端口 |
| `EMAIL_ALLOWED_USERS` | 允许给 bot 发消息的电子邮件地址，逗号分隔 |
| `EMAIL_HOME_ADDRESS` | 主动发送邮件的默认收件人 |
| `EMAIL_HOME_ADDRESS_NAME` | 邮件主目标的显示名称 |
| `EMAIL_POLL_INTERVAL` | 邮件轮询间隔（秒） |
| `EMAIL_ALLOW_ALL_USERS` | 允许所有入站邮件发送者 |
| `DINGTALK_CLIENT_ID` | 来自开发者后台 ([open.dingtalk.com](https://open.dingtalk.com)) 的钉钉 Bot AppKey |
| `DINGTALK_CLIENT_SECRET` | 钉钉 Bot AppSecret |
| `DINGTALK_ALLOWED_USERS` | 允许给 bot 发消息的钉钉用户 ID，逗号分隔 |
| `FEISHU_APP_ID` | 来自 [open.feishu.cn](https://open.feishu.cn/) 的飞书/Lark Bot App ID |
| `FEISHU_APP_SECRET` | 飞书/Lark Bot App Secret |
| `FEISHU_DOMAIN` | `feishu`（中国）或 `lark`（国际）。默认：`feishu` |
| `FEISHU_CONNECTION_MODE` | `websocket`（推荐）或 `webhook`。默认：`websocket` |
| `FEISHU_ENCRYPT_KEY` | Webhook 模式的可选加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | Webhook 模式的可选验证令牌 |
| `FEISHU_ALLOWED_USERS` | 允许给 bot 发消息的飞书用户 ID，逗号分隔 |
| `FEISHU_HOME_CHANNEL` | 用于定时任务投递和通知的飞书群聊 ID |
| `WECOM_BOT_ID` | 来自管理后台的企业微信 AI Bot ID |
| `WECOM_SECRET` | 企业微信 AI Bot secret |
| `WECOM_WEBSOCKET_URL` | 自定义 WebSocket URL（默认：`wss://openws.work.weixin.qq.com`） |
| `WECOM_ALLOWED_USERS` | 允许给 bot 发消息的企业微信用户 ID，逗号分隔 |
| `WECOM_HOME_CHANNEL` | 用于定时任务投递和通知的企业微信群聊 ID |
| `MATTERMOST_URL` | Mattermost 服务器 URL（例如 `https://mm.example.com`） |
| `MATTERMOST_TOKEN` | Mattermost 的 Bot 令牌或个人访问令牌 |
| `MATTERMOST_ALLOWED_USERS` | 允许给 bot 发消息的 Mattermost 用户 ID，逗号分隔 |
| `MATTERMOST_HOME_CHANNEL` | 用于主动消息投递（定时任务、通知）的频道 ID |
| `MATTERMOST_REQUIRE_MENTION` | 在频道中是否需要 `@提及`（默认：`true`）。设置为 `false` 以响应所有消息。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | Bot 无需 `@提及` 即可响应的频道 ID，逗号分隔 |
| `MATTERMOST_REPLY_MODE` | 回复样式：`thread`（线程回复）或 `off`（扁平消息，默认） |
| `MATRIX_HOMESERVER` | Matrix homeserver URL（例如 `https://matrix.org`） |
| `MATRIX_ACCESS_TOKEN` | 用于 Bot 身份验证的 Matrix 访问令牌 |
| `MATRIX_USER_ID` | Matrix 用户 ID（例如 `@hermes:matrix.org`） —— 密码登录必需，使用访问令牌时可选 |
| `MATRIX_PASSWORD` | Matrix 密码（访问令牌的替代方案） |
| `MATRIX_ALLOWED_USERS` | 允许给 bot 发消息的 Matrix 用户 ID，逗号分隔（例如 `@alice:matrix.org`） |
| `MATRIX_HOME_ROOM` | 用于主动消息投递的房间 ID（例如 `!abc123:matrix.org`） |
| `MATRIX_ENCRYPTION` | 启用端到端加密（`true`/`false`，默认：`false`） |
| `MATRIX_REQUIRE_MENTION` | 在房间中是否需要 `@提及`（默认：`true`）。设置为 `false` 以响应所有消息。 |
| `MATRIX_FREE_RESPONSE_ROOMS` | Bot 无需 `@提及` 即可响应的房间 ID，逗号分隔 |
| `MATRIX_AUTO_THREAD` | 为房间消息自动创建线程（默认：`true`） |
| `HASS_TOKEN` | Home Assistant 长期访问令牌（启用 HA 平台 + 工具） |
| `HASS_URL` | Home Assistant URL（默认：`http://homeassistant.local:8123`） |
| `WEBHOOK_ENABLED` | 启用 Webhook 平台适配器（`true`/`false`） |
| `WEBHOOK_PORT` | 接收 Webhook 的 HTTP 服务器端口（默认：`8644`） |
| `WEBHOOK_SECRET` | 用于 Webhook 签名验证的全局 HMAC 密钥（当路由未指定自己的密钥时作为备选） |
| `API_SERVER_ENABLED` | 启用兼容 OpenAI 的 API 服务器（`true`/`false`）。与其他平台并行运行。 |
| `API_SERVER_KEY` | API 服务器身份验证的 Bearer 令牌。强烈建议设置；对于任何可从网络访问的部署都是必需的。 |
| `API_SERVER_CORS_ORIGINS` | 允许直接调用 API 服务器的浏览器源，逗号分隔（例如 `http://localhost:3000,http://127.0.0.1:3000`）。默认：禁用。 |
| `API_SERVER_PORT` | API 服务器端口（默认：`8642`） |
| `API_SERVER_HOST` | API 服务器的主机/绑定地址（默认：`127.0.0.1`）。仅在设置了 `API_SERVER_KEY` 且配置了严格的 `API_SERVER_CORS_ORIGINS` 白名单时才使用 `0.0.0.0` 进行网络访问。 |
| `MESSAGING_CWD` | 消息模式下 terminal 命令的工作目录（默认：`~`） |
| `GATEWAY_ALLOWED_USERS` | 允许跨所有平台使用的用户 ID，逗号分隔 |
| `GATEWAY_ALLOW_ALL_USERS` | 允许所有用户而无需白名单（`true`/`false`，默认：`false`） |
## Agent 行为

| 变量 | 描述 |
|----------|-------------|
| `HERMES_MAX_ITERATIONS` | 每次对话中工具调用的最大迭代次数（默认值：90） |
| `HERMES_TOOL_PROGRESS` | 已弃用的工具进度显示兼容性变量。建议使用 `config.yaml` 中的 `display.tool_progress`。 |
| `HERMES_TOOL_PROGRESS_MODE` | 已弃用的工具进度模式兼容性变量。建议使用 `config.yaml` 中的 `display.tool_progress`。 |
| `HERMES_HUMAN_DELAY_MODE` | 响应节奏：`off`/`natural`/`custom` |
| `HERMES_HUMAN_DELAY_MIN_MS` | 自定义延迟范围最小值（毫秒） |
| `HERMES_HUMAN_DELAY_MAX_MS` | 自定义延迟范围最大值（毫秒） |
| `HERMES_QUIET` | 抑制非必要输出（`true`/`false`） |
| `HERMES_API_TIMEOUT` | LLM API 调用超时时间，单位为秒（默认值：`1800`） |
| `HERMES_EXEC_ASK` | 在 gateway 模式下启用执行确认提示（`true`/`false`） |
| `HERMES_ENABLE_PROJECT_PLUGINS` | 启用从 `./.hermes/plugins/` 自动发现仓库本地插件（`true`/`false`，默认值：`false`） |
| `HERMES_BACKGROUND_NOTIFICATIONS` | gateway 中后台进程的通知模式：`all`（默认）、`result`、`error`、`off` |
| `HERMES_EPHEMERAL_SYSTEM_PROMPT` | 在 API 调用时注入的临时系统提示词（不会持久化到会话中） |

## 会话设置

| 变量 | 描述 |
|----------|-------------|
| `SESSION_IDLE_MINUTES` | 在闲置 N 分钟后重置会话（默认值：1440） |
| `SESSION_RESET_HOUR` | 每日重置的小时数，采用 24 小时制（默认值：4 = 凌晨 4 点） |

## 上下文压缩（仅限 config.yaml）

上下文压缩仅通过 `config.yaml` 中的 `compression` 部分进行配置 —— 没有对应的环境变量。

```yaml
compression:
  enabled: true
  threshold: 0.50
  summary_model: ""                            # 为空 = 使用配置的主模型
  summary_provider: auto
  summary_base_url: null  # 用于摘要的自定义 OpenAI 兼容端点
```

## 辅助任务覆盖

| 变量 | 描述 |
|----------|-------------|
| `AUXILIARY_VISION_PROVIDER` | 覆盖视觉任务的 provider |
| `AUXILIARY_VISION_MODEL` | 覆盖视觉任务的模型 |
| `AUXILIARY_VISION_BASE_URL` | 视觉任务的直接 OpenAI 兼容端点 |
| `AUXILIARY_VISION_API_KEY` | 与 `AUXILIARY_VISION_BASE_URL` 配对的 API key |
| `AUXILIARY_WEB_EXTRACT_PROVIDER` | 覆盖网页提取/摘要任务的 provider |
| `AUXILIARY_WEB_EXTRACT_MODEL` | 覆盖网页提取/摘要任务的模型 |
| `AUXILIARY_WEB_EXTRACT_BASE_URL` | 网页提取/摘要任务的直接 OpenAI 兼容端点 |
| `AUXILIARY_WEB_EXTRACT_API_KEY` | 与 `AUXILIARY_WEB_EXTRACT_BASE_URL` 配对的 API key |

对于特定任务的直接端点，Hermes 会使用该任务配置的 API key 或 `OPENAI_API_KEY`。它不会在这些自定义端点上复用 `OPENROUTER_API_KEY`。

## 备用模型（仅限 config.yaml）

主模型备用方案仅通过 `config.yaml` 配置 —— 没有对应的环境变量。添加一个带有 `provider` 和 `model` 键的 `fallback_model` 部分，以便在主模型遇到错误时启用自动故障转移。

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

详情请参阅 [备用 Provider](/user-guide/features/fallback-providers)。

## Provider 路由（仅限 config.yaml）

这些配置位于 `~/.hermes/config.yaml` 的 `provider_routing` 部分：

| 键名 | 描述 |
|-----|-------------|
| `sort` | Provider 排序方式：`"price"`（默认）、`"throughput"` 或 `"latency"` |
| `only` | 允许使用的 provider 标识列表（例如 `["anthropic", "google"]`） |
| `ignore` | 要跳过的 provider 标识列表 |
| `order` | 按顺序尝试的 provider 标识列表 |
| `require_parameters` | 仅使用支持所有请求参数的 provider（`true`/`false`） |
| `data_collection` | `"allow"`（默认）或 `"deny"`（排除会存储数据的 provider） |

:::tip
使用 `hermes config set` 来设置环境变量 —— 它会自动将它们保存到正确的文件中（敏感信息存入 `.env`，其他内容存入 `config.yaml`）。
:::
