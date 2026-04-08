---
sidebar_position: 10
title: "从 OpenClaw 迁移"
description: "将您的 OpenClaw / Clawdbot 配置迁移到 Hermes Agent 的完整指南 —— 包括迁移内容、配置映射以及迁移后的检查事项。"
---

# 从 OpenClaw 迁移

`hermes claw migrate` 命令可以将您的 OpenClaw（或旧版的 Clawdbot/Moldbot）配置导入到 Hermes 中。本指南详细介绍了具体迁移的内容、配置项的映射关系以及迁移后的校验步骤。

## 快速开始

```bash
# 预览迁移效果（不修改任何文件）
hermes claw migrate --dry-run

# 执行迁移（默认不包含密钥 secrets）
hermes claw migrate

# 完整迁移，包括 API 密钥
hermes claw migrate --preset full
```

迁移程序默认从 `~/.openclaw/` 读取数据。如果您仍保留有旧版的 `~/.clawdbot/` 或 `~/.moldbot/` 目录，程序会自动检测。旧版的配置文件名（`clawdbot.json`，`moldbot.json`）同样会被自动识别。

## 选项

| 选项 | 描述 |
|--------|-------------|
| `--dry-run` | 预览将要迁移的内容，不执行写入操作。 |
| `--preset <name>` | `full`（默认，包含密钥）或 `user-data`（排除 API 密钥）。 |
| `--overwrite` | 发生冲突时覆盖现有的 Hermes 文件（默认：跳过）。 |
| `--migrate-secrets` | 包含 API 密钥（使用 `--preset full` 时默认开启）。 |
| `--source <path>` | 自定义 OpenClaw 目录路径。 |
| `--workspace-target <path>` | `AGENTS.md` 的存放位置。 |
| `--skill-conflict <mode>` | 技能冲突处理模式：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

## 迁移内容

### 人格 (Persona)、记忆与指令

| 内容 | OpenClaw 源 | Hermes 目标 | 备注 |
|------|----------------|-------------------|-------|
| 人格 (Persona) | `workspace/SOUL.md` | `~/.hermes/SOUL.md` | 直接复制 |
| 工作区指令 | `workspace/AGENTS.md` | `--workspace-target` 指定目录下的 `AGENTS.md` | 需要配合 `--workspace-target` 标志使用 |
| 长期记忆 | `workspace/MEMORY.md` | `~/.hermes/memories/MEMORY.md` | 解析为条目，与现有内容合并并去重。使用 `§` 分隔符。 |
| 用户画像 | `workspace/USER.md` | `~/.hermes/memories/USER.md` | 使用与记忆相同的条目合并逻辑。 |
| 每日记忆文件 | `workspace/memory/*.md` | `~/.hermes/memories/MEMORY.md` | 所有每日文件都会合并到主记忆文件中。 |

所有工作区文件都会尝试检查 `workspace.default/` 作为回退路径。

### 技能 (Skills)（4 个来源）

| 来源 | OpenClaw 位置 | Hermes 目标 |
|--------|------------------|-------------------|
| 工作区技能 | `workspace/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 托管/共享技能 | `~/.openclaw/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 个人跨项目技能 | `~/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 项目级共享技能 | `workspace/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |

技能冲突由 `--skill-conflict` 处理：`skip` 保留现有 Hermes 技能，`overwrite` 替换，`rename` 创建一个带有 `-imported` 后缀的副本。

### 模型与供应商配置

| 内容 | OpenClaw 配置路径 | Hermes 目标 | 备注 |
|------|---------------------|-------------------|-------|
| 默认模型 | `agents.defaults.model` | `config.yaml` → `model` | 可以是字符串或 `{primary, fallbacks}` 对象 |
| 自定义供应商 | `models.providers.*` | `config.yaml` → `custom_providers` | 映射 `baseUrl`, `apiType` ("openai"→"chat_completions", "anthropic"→"anthropic_messages") |
| 供应商 API 密钥 | `models.providers.*.apiKey` | `~/.hermes/.env` | 需要 `--migrate-secrets`。参见下文的 [API 密钥解析](#api-key-resolution)。 |

### Agent 行为

| 内容 | OpenClaw 配置路径 | Hermes 配置路径 | 映射关系 |
|------|---------------------|-------------------|---------|
| 最大轮次 | `agents.defaults.timeoutSeconds` | `agent.max_turns` | `timeoutSeconds / 10`，上限 200 |
| 详细模式 | `agents.defaults.verboseDefault` | `agent.verbose` | "off" / "on" / "full" |
| 推理力度 | `agents.defaults.thinkingDefault` | `agent.reasoning_effort` | "always"/"high" → "high", "auto"/"medium" → "medium", "off"/"low"/"none"/"minimal" → "low" |
| 压缩 | `agents.defaults.compaction.mode` | `compression.enabled` | "off" → false, 其他值 → true |
| 压缩模型 | `agents.defaults.compaction.model` | `compression.summary_model` | 字符串直接复制 |
| 人为延迟 | `agents.defaults.humanDelay.mode` | `human_delay.mode` | "natural" / "custom" / "off" |
| 人为延迟时长 | `agents.defaults.humanDelay.minMs` / `.maxMs` | `human_delay.min_ms` / `.max_ms` | 直接复制 |
| 时区 | `agents.defaults.userTimezone` | `timezone` | 字符串直接复制 |
| 执行超时 | `tools.exec.timeoutSec` | `terminal.timeout` | 直接复制（字段名为 `timeoutSec` 而非 `timeout`） |
| Docker 沙箱 | `agents.defaults.sandbox.backend` | `terminal.backend` | "docker" → "docker" |
| Docker 镜像 | `agents.defaults.sandbox.docker.image` | `terminal.docker_image` | 直接复制 |

### 会话重置策略

| OpenClaw 配置路径 | Hermes 配置路径 | 备注 |
|---------------------|-------------------|-------|
| `session.reset.mode` | `session_reset.mode` | "daily", "idle", 或两者都有 |
| `session.reset.atHour` | `session_reset.at_hour` | 每日重置的小时数 (0–23) |
| `session.reset.idleMinutes` | `session_reset.idle_minutes` | 无活动重置的分钟数 |

注意：OpenClaw 还有一个 `session.resetTriggers`（简单的字符串数组，如 `["daily", "idle"]`）。如果结构化的 `session.reset` 不存在，迁移程序会回退到从 `resetTriggers` 推断。

### MCP 服务器

| OpenClaw 字段 | Hermes 字段 | 备注 |
|----------------|-------------|-------|
| `mcp.servers.*.command` | `mcp_servers.*.command` | Stdio 传输 |
| `mcp.servers.*.args` | `mcp_servers.*.args` | |
| `mcp.servers.*.env` | `mcp_servers.*.env` | |
| `mcp.servers.*.cwd` | `mcp_servers.*.cwd` | |
| `mcp.servers.*.url` | `mcp_servers.*.url` | HTTP/SSE 传输 |
| `mcp.servers.*.tools.include` | `mcp_servers.*.tools.include` | 工具过滤 |
| `mcp.servers.*.tools.exclude` | `mcp_servers.*.tools.exclude` | |

### TTS (文字转语音)

TTS 设置会从 OpenClaw 配置的**两个**位置读取，优先级如下：

1. `messages.tts.providers.{provider}.*`（规范位置）
2. 顶层 `talk.providers.{provider}.*`（回退位置）
3. 旧版扁平化键名 `messages.tts.{provider}.*`（最旧格式）

| 内容 | Hermes 目标 |
|------|-------------------|
| 供应商名称 | `config.yaml` → `tts.provider` |
| ElevenLabs 声音 ID | `config.yaml` → `tts.elevenlabs.voice_id` |
| ElevenLabs 模型 ID | `config.yaml` → `tts.elevenlabs.model_id` |
| OpenAI 模型 | `config.yaml` → `tts.openai.model` |
| OpenAI 声音 | `config.yaml` → `tts.openai.voice` |
| Edge TTS 声音 | `config.yaml` → `tts.edge.voice` |
| TTS 资源 | `~/.hermes/tts/`（文件复制） |

### 消息平台

| 平台 | OpenClaw 配置路径 | Hermes `.env` 变量 | 备注 |
|----------|---------------------|----------------------|-------|
| Telegram | `channels.telegram.botToken` | `TELEGRAM_BOT_TOKEN` | Token 可以是字符串或 [SecretRef](#secretref-handling) |
| Telegram | `credentials/telegram-default-allowFrom.json` | `TELEGRAM_ALLOWED_USERS` | 从 `allowFrom[]` 数组合并为逗号分隔符 |
| Discord | `channels.discord.token` | `DISCORD_BOT_TOKEN` | |
| Discord | `channels.discord.allowFrom` | `DISCORD_ALLOWED_USERS` | |
| Slack | `channels.slack.botToken` | `SLACK_BOT_TOKEN` | |
| Slack | `channels.slack.appToken` | `SLACK_APP_TOKEN` | |
| Slack | `channels.slack.allowFrom` | `SLACK_ALLOWED_USERS` | |
| WhatsApp | `channels.whatsapp.allowFrom` | `WHATSAPP_ALLOWED_USERS` | 通过 Baileys QR 配对认证（非 Token） |
| Signal | `channels.signal.account` | `SIGNAL_ACCOUNT` | |
| Signal | `channels.signal.httpUrl` | `SIGNAL_HTTP_URL` | |
| Signal | `channels.signal.allowFrom` | `SIGNAL_ALLOWED_USERS` | |
| Matrix | `channels.matrix.botToken` | `MATRIX_ACCESS_TOKEN` | 通过 deep-channels 迁移 |
| Mattermost | `channels.mattermost.botToken` | `MATTERMOST_BOT_TOKEN` | 通过 deep-channels 迁移 |

### 其他配置

| 内容 | OpenClaw 路径 | Hermes 路径 | 备注 |
|------|-------------|-------------|-------|
| 审批模式 | `approvals.exec.mode` | `config.yaml` → `approvals.mode` | "auto"→"off", "always"→"manual", "smart"→"smart" |
| 命令白名单 | `exec-approvals.json` | `config.yaml` → `command_allowlist` | 模式合并并去重 |
| 浏览器 CDP URL | `browser.cdpUrl` | `config.yaml` → `browser.cdp_url` | |
| 浏览器无头模式 | `browser.headless` | `config.yaml` → `browser.headless` | |
| Brave 搜索密钥 | `tools.web.search.brave.apiKey` | `.env` → `BRAVE_API_KEY` | 需要 `--migrate-secrets` |
| 网关认证 Token | `gateway.auth.token` | `.env` → `HERMES_GATEWAY_TOKEN` | 需要 `--migrate-secrets` |
| 工作目录 | `agents.defaults.workspace` | `.env` → `MESSAGING_CWD` | |
### 已归档内容（无直接 Hermes 对应项）

这些内容会被保存到 `~/.hermes/migration/openclaw/<timestamp>/archive/` 以供手动查看：

| 内容 | 归档文件 | 如何在 Hermes 中重建 |
|------|-------------|--------------------------|
| `IDENTITY.md` | `archive/workspace/IDENTITY.md` | 合并入 `SOUL.md` |
| `TOOLS.md` | `archive/workspace/TOOLS.md` | Hermes 拥有内置的工具指令 |
| `HEARTBEAT.md` | `archive/workspace/HEARTBEAT.md` | 使用 cron 任务处理周期性任务 |
| `BOOTSTRAP.md` | `archive/workspace/BOOTSTRAP.md` | 使用 context 文件或 skills |
| Cron 任务 | `archive/cron-config.json` | 使用 `hermes cron create` 重建 |
| 插件 (Plugins) | `archive/plugins-config.json` | 参见 [插件指南](/user-guide/features/hooks) |
| Hooks/webhooks | `archive/hooks-config.json` | 使用 `hermes webhook` 或 gateway hooks |
| 记忆后端 | `archive/memory-backend-config.json` | 通过 `hermes honcho` 配置 |
| Skills 注册表 | `archive/skills-registry-config.json` | 使用 `hermes skills config` |
| UI/身份标识 | `archive/ui-identity-config.json` | 使用 `/skin` 命令 |
| 日志 | `archive/logging-diagnostics-config.json` | 在 `config.yaml` 的 logging 部分设置 |
| 多 Agent 列表 | `archive/agents-list.json` | 使用 Hermes profiles |
| 频道绑定 | `archive/bindings.json` | 针对每个平台手动设置 |
| 复杂频道配置 | `archive/channels-deep-config.json` | 手动进行平台配置 |

## API Key 解析

当启用 `--migrate-secrets` 时，API Key 会按优先级从以下**三个来源**收集：

1. **配置值** — `openclaw.json` 中的 `models.providers.*.apiKey` 和 TTS 提供商密钥。
2. **环境文件** — `~/.openclaw/.env`（如 `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` 等密钥）。
3. **认证配置文件** — `~/.openclaw/agents/main/agent/auth-profiles.json`（每个 Agent 的凭据）。

配置值的优先级最高。`.env` 用于填补空缺，认证配置文件用于填补剩余部分。

### 支持的密钥目标

`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`, `ZAI_API_KEY`, `MINIMAX_API_KEY`, `ELEVENLABS_API_KEY`, `TELEGRAM_BOT_TOKEN`, `VOICE_TOOLS_OPENAI_KEY`

不在该白名单中的密钥绝不会被复制。

## SecretRef 处理

OpenClaw 中用于 token 和 API Key 的配置值可以有三种格式：

```json
// 普通字符串
"channels": { "telegram": { "botToken": "123456:ABC-DEF..." } }

// 环境变量模板
"channels": { "telegram": { "botToken": "${TELEGRAM_BOT_TOKEN}" } }

// SecretRef 对象
"channels": { "telegram": { "botToken": { "source": "env", "id": "TELEGRAM_BOT_TOKEN" } } }
```

迁移程序会解析所有这三种格式。对于环境变量模板和 `source: "env"` 的 SecretRef 对象，它会在 `~/.openclaw/.env` 中查找对应值。`source: "file"` 或 `source: "exec"` 的 SecretRef 对象无法自动解析 —— 这些值必须在迁移后手动添加到 Hermes。

## 迁移后操作

1. **检查迁移报告** — 迁移完成时会打印报告，包含已迁移、已跳过和冲突项的数量。

2. **查看归档文件** — `~/.hermes/migration/openclaw/<timestamp>/archive/` 中的任何内容都需要手动处理。

3. **验证 API Key** — 运行 `hermes status` 检查模型提供商的认证状态。

4. **测试消息收发** — 如果你迁移了平台 token，请重启 gateway：`systemctl --user restart hermes-gateway`

5. **检查会话策略** — 验证 `hermes config get session_reset` 是否符合你的预期。

6. **重新配对 WhatsApp** — WhatsApp 使用二维码配对（Baileys），而不是 token 迁移。运行 `hermes whatsapp` 进行配对。

## 故障排除

### "OpenClaw directory not found"（未找到 OpenClaw 目录）

迁移程序会依次检查 `~/.openclaw/`、`~/.clawdbot/` 和 `~/.moldbot/`。如果你的安装路径在别处，请使用 `--source /path/to/your/openclaw`。

### "No provider API keys found"（未找到提供商 API Key）

密钥可能在你的 `.env` 文件中，而不是在 `openclaw.json` 里。迁移程序会同时检查两者 —— 请确保 `~/.openclaw/.env` 存在且包含密钥。如果密钥使用了 `source: "file"` 或 `source: "exec"` 的 SecretRefs，则无法自动解析。

### 迁移后 Skills 未出现

导入的 skills 会存放在 `~/.hermes/skills/openclaw-imports/`。开启一个新会话以使它们生效，或运行 `/skills` 验证它们是否已加载。

### TTS 语音未迁移

OpenClaw 在两个地方存储 TTS 设置：`messages.tts.providers.*` 和顶层的 `talk` 配置。迁移程序会同时检查这两处。如果你的 voice ID 是通过 OpenClaw UI 设置的（存储在不同的路径下），你可能需要手动设置：`hermes config set tts.elevenlabs.voice_id YOUR_VOICE_ID`。
