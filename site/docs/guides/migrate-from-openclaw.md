---
sidebar_position: 7
title: "从 OpenClaw 迁移"
description: "完整指南，教你如何将 OpenClaw / Clawdbot 设置迁移到 Hermes Agent —— 包括迁移内容、配置映射及迁移后检查事项。"
---

# 从 OpenClaw 迁移

`hermes claw migrate` 命令可以将你的 OpenClaw（或旧版 Clawdbot/Moldbot）设置导入到 Hermes。本指南详细说明了迁移内容、配置键映射以及迁移后需要核对的事项。

## 快速开始

```bash
# 预览将要发生的操作（不修改任何文件）
hermes claw migrate --dry-run

# 执行迁移（默认不包含密钥）
hermes claw migrate

# 完整迁移，包括 API 密钥
hermes claw migrate --preset full
```

迁移默认从 `~/.openclaw/` 目录读取。如果你还有旧版的 `~/.clawdbot/` 或 `~/.moldbot/` 目录，系统会自动检测。同样支持旧版配置文件名（如 `clawdbot.json`、`moldbot.json`）。

## 选项

| 选项 | 说明 |
|--------|-------------|
| `--dry-run` | 预览将迁移的内容，但不写入任何文件。 |
| `--preset <name>` | `full`（默认，包含密钥）或 `user-data`（不包含 API 密钥）。 |
| `--overwrite` | 遇到冲突时覆盖已有的 Hermes 文件（默认跳过）。 |
| `--migrate-secrets` | 包含 API 密钥（`--preset full` 时默认开启）。 |
| `--source <path>` | 自定义 OpenClaw 目录。 |
| `--workspace-target <path>` | 指定放置 `AGENTS.md` 的位置。 |
| `--skill-conflict <mode>` | 技能冲突处理方式：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

## 迁移内容

### 角色、记忆和指令

| 内容 | OpenClaw 来源 | Hermes 目标 | 备注 |
|------|----------------|-------------------|-------|
| 角色（Persona） | `workspace/SOUL.md` | `~/.hermes/SOUL.md` | 直接复制 |
| 工作区指令 | `workspace/AGENTS.md` | `--workspace-target` 指定路径下的 `AGENTS.md` | 需要 `--workspace-target` 参数 |
| 长期记忆 | `workspace/MEMORY.md` | `~/.hermes/memories/MEMORY.md` | 解析为条目，合并已有内容，去重。使用 `§` 分隔符。 |
| 用户档案 | `workspace/USER.md` | `~/.hermes/memories/USER.md` | 同长期记忆的条目合并逻辑。 |
| 每日记忆文件 | `workspace/memory/*.md` | 合并到 `~/.hermes/memories/MEMORY.md` | 所有每日文件合并到主记忆中。 |

所有工作区文件还会检查 `workspace.default/` 作为备用路径。

### 技能（4 个来源）

| 来源 | OpenClaw 位置 | Hermes 目标 |
|--------|------------------|-------------------|
| 工作区技能 | `workspace/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 托管/共享技能 | `~/.openclaw/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 个人跨项目技能 | `~/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 项目级共享技能 | `workspace/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |

技能冲突由 `--skill-conflict` 参数控制：`skip` 保留现有 Hermes 技能，`overwrite` 替换，`rename` 创建一个带 `-imported` 后缀的副本。

### 模型和提供商配置

| 内容 | OpenClaw 配置路径 | Hermes 目标 | 备注 |
|------|---------------------|-------------------|-------|
| 默认模型 | `agents.defaults.model` | `config.yaml` → `model` | 可以是字符串或 `{primary, fallbacks}` 对象 |
| 自定义提供商 | `models.providers.*` | `config.yaml` → `custom_providers` | 映射 `baseUrl`，`apiType`（"openai"→"chat_completions"，"anthropic"→"anthropic_messages"） |
| 提供商 API 密钥 | `models.providers.*.apiKey` | `~/.hermes/.env` | 需要 `--migrate-secrets`。详见下文 [API key resolution](#api-key-resolution)。 |

### Agent 行为

| 内容 | OpenClaw 配置路径 | Hermes 配置路径 | 映射规则 |
|------|---------------------|-------------------|---------|
| 最大对话轮数 | `agents.defaults.timeoutSeconds` | `agent.max_turns` | `timeoutSeconds / 10`，最大 200 |
| 详细模式 | `agents.defaults.verboseDefault` | `agent.verbose` | "off" / "on" / "full" |
| 推理强度 | `agents.defaults.thinkingDefault` | `agent.reasoning_effort` | "always"/"high" → "high"，"auto"/"medium" → "medium"，"off"/"low"/"none"/"minimal" → "low" |
| 压缩 | `agents.defaults.compaction.mode` | `compression.enabled` | "off" → false，其他均为 true |
| 压缩模型 | `agents.defaults.compaction.model` | `compression.summary_model` | 直接字符串复制 |
| 人类延迟模式 | `agents.defaults.humanDelay.mode` | `human_delay.mode` | "natural" / "custom" / "off" |
| 人类延迟时间 | `agents.defaults.humanDelay.minMs` / `.maxMs` | `human_delay.min_ms` / `.max_ms` | 直接复制 |
| 时区 | `agents.defaults.userTimezone` | `timezone` | 直接字符串复制 |
| 执行超时 | `tools.exec.timeoutSec` | `terminal.timeout` | 直接复制（字段名为 `timeoutSec`，非 `timeout`） |
| Docker 沙箱 | `agents.defaults.sandbox.backend` | `terminal.backend` | "docker" → "docker" |
| Docker 镜像 | `agents.defaults.sandbox.docker.image` | `terminal.docker_image` | 直接复制 |

### 会话重置策略

| OpenClaw 配置路径 | Hermes 配置路径 | 备注 |
|---------------------|-------------------|-------|
| `session.reset.mode` | `session_reset.mode` | "daily"、"idle" 或两者 |
| `session.reset.atHour` | `session_reset.at_hour` | 每日重置的小时（0–23） |
| `session.reset.idleMinutes` | `session_reset.idle_minutes` | 空闲分钟数 |

注意：OpenClaw 还有 `session.resetTriggers`（简单字符串数组，如 `["daily", "idle"]`）。如果没有结构化的 `session.reset`，迁移会从 `resetTriggers` 推断。

### MCP 服务器

| OpenClaw 字段 | Hermes 字段 | 备注 |
|----------------|-------------|-------|
| `mcp.servers.*.command` | `mcp_servers.*.command` | 标准输入输出传输 |
| `mcp.servers.*.args` | `mcp_servers.*.args` | |
| `mcp.servers.*.env` | `mcp_servers.*.env` | |
| `mcp.servers.*.cwd` | `mcp_servers.*.cwd` | |
| `mcp.servers.*.url` | `mcp_servers.*.url` | HTTP/SSE 传输 |
| `mcp.servers.*.tools.include` | `mcp_servers.*.tools.include` | 工具过滤 |
| `mcp.servers.*.tools.exclude` | `mcp_servers.*.tools.exclude` | |

### TTS（文本转语音）

TTS 设置从 OpenClaw 的**两个**配置位置读取，优先级如下：

1. `messages.tts.providers.{provider}.*`（规范位置）
2. 顶层 `talk.providers.{provider}.*`（备用）
3. 旧版扁平键 `messages.tts.{provider}.*`（最旧格式）

| 内容 | Hermes 目标 |
|------|-------------------|
| 提供商名称 | `config.yaml` → `tts.provider` |
| ElevenLabs 语音 ID | `config.yaml` → `tts.elevenlabs.voice_id` |
| ElevenLabs 模型 ID | `config.yaml` → `tts.elevenlabs.model_id` |
| OpenAI 模型 | `config.yaml` → `tts.openai.model` |
| OpenAI 语音 | `config.yaml` → `tts.openai.voice` |
| Edge TTS 语音 | `config.yaml` → `tts.edge.voice` |
| TTS 资源 | `~/.hermes/tts/`（文件复制） |

### 消息平台

| 平台 | OpenClaw 配置路径 | Hermes `.env` 变量 | 备注 |
|----------|---------------------|----------------------|-------|
| Telegram | `channels.telegram.botToken` | `TELEGRAM_BOT_TOKEN` | Token 可为字符串或 [SecretRef](#secretref-handling) |
| Telegram | `credentials/telegram-default-allowFrom.json` | `TELEGRAM_ALLOWED_USERS` | 从 `allowFrom[]` 数组以逗号连接 |
| Discord | `channels.discord.token` | `DISCORD_BOT_TOKEN` | |
| Discord | `channels.discord.allowFrom` | `DISCORD_ALLOWED_USERS` | |
| Slack | `channels.slack.botToken` | `SLACK_BOT_TOKEN` | |
| Slack | `channels.slack.appToken` | `SLACK_APP_TOKEN` | |
| Slack | `channels.slack.allowFrom` | `SLACK_ALLOWED_USERS` | |
| WhatsApp | `channels.whatsapp.allowFrom` | `WHATSAPP_ALLOWED_USERS` | 通过 Baileys QR 配对认证（非 token） |
| Signal | `channels.signal.account` | `SIGNAL_ACCOUNT` | |
| Signal | `channels.signal.httpUrl` | `SIGNAL_HTTP_URL` | |
| Signal | `channels.signal.allowFrom` | `SIGNAL_ALLOWED_USERS` | |
| Matrix | `channels.matrix.botToken` | `MATRIX_ACCESS_TOKEN` | 通过深度频道迁移 |
| Mattermost | `channels.mattermost.botToken` | `MATTERMOST_BOT_TOKEN` | 通过深度频道迁移 |

### 其他配置

| 内容 | OpenClaw 路径 | Hermes 路径 | 备注 |
|------|-------------|-------------|-------|
| 审批模式 | `approvals.exec.mode` | `config.yaml` → `approvals.mode` | "auto"→"off"，"always"→"manual"，"smart"→"smart" |
| 命令白名单 | `exec-approvals.json` | `config.yaml` → `command_allowlist` | 合并去重的模式列表 |
| 浏览器 CDP URL | `browser.cdpUrl` | `config.yaml` → `browser.cdp_url` | |
| 浏览器无头模式 | `browser.headless` | `config.yaml` → `browser.headless` | |
| Brave 搜索密钥 | `tools.web.search.brave.apiKey` | `.env` → `BRAVE_API_KEY` | 需要 `--migrate-secrets` |
| 网关认证令牌 | `gateway.auth.token` | `.env` → `HERMES_GATEWAY_TOKEN` | 需要 `--migrate-secrets` |
| 工作目录 | `agents.defaults.workspace` | `.env` → `MESSAGING_CWD` | |
### 已归档（无直接对应的 Hermes 配置）

这些内容已保存到 `~/.hermes/migration/openclaw/<timestamp>/archive/`，需要手动查看：

| 内容 | 归档文件 | 在 Hermes 中如何重建 |
|------|-------------|--------------------------|
| `IDENTITY.md` | `archive/workspace/IDENTITY.md` | 合并到 `SOUL.md` 中 |
| `TOOLS.md` | `archive/workspace/TOOLS.md` | Hermes 内置工具说明 |
| `HEARTBEAT.md` | `archive/workspace/HEARTBEAT.md` | 使用定时任务（cron jobs）执行周期性任务 |
| `BOOTSTRAP.md` | `archive/workspace/BOOTSTRAP.md` | 使用上下文文件或技能 |
| 定时任务（Cron jobs） | `archive/cron-config.json` | 使用 `hermes cron create` 重新创建 |
| 插件 | `archive/plugins-config.json` | 参见[插件指南](../user-guide/features/hooks.md) |
| Hooks / Webhooks | `archive/hooks-config.json` | 使用 `hermes webhook` 或网关 hooks |
| 内存后端 | `archive/memory-backend-config.json` | 通过 `hermes honcho` 配置 |
| 技能注册表 | `archive/skills-registry-config.json` | 使用 `hermes skills config` |
| UI / 身份 | `archive/ui-identity-config.json` | 使用 `/skin` 命令 |
| 日志 | `archive/logging-diagnostics-config.json` | 在 `config.yaml` 的 logging 部分设置 |
| 多 Agent 列表 | `archive/agents-list.json` | 使用 Hermes 配置文件 |
| 渠道绑定 | `archive/bindings.json` | 按平台手动设置 |
| 复杂渠道 | `archive/channels-deep-config.json` | 手动配置平台 |

## API 密钥解析 {#api-key-resolution}

启用 `--migrate-secrets` 时，API 密钥会从**三个来源**按优先级收集：

1. **配置值** — `models.providers.*.apiKey` 和 `openclaw.json` 中的 TTS 提供商密钥
2. **环境文件** — `~/.openclaw/.env`（如 `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` 等）
3. **认证配置文件** — `~/.openclaw/agents/main/agent/auth-profiles.json`（每个 Agent 的凭据）

配置值优先，`.env` 文件补充缺失部分，认证配置文件补充剩余部分。

### 支持的密钥目标

`OPENROUTER_API_KEY`、`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`DEEPSEEK_API_KEY`、`GEMINI_API_KEY`、`ZAI_API_KEY`、`MINIMAX_API_KEY`、`ELEVENLABS_API_KEY`、`TELEGRAM_BOT_TOKEN`、`VOICE_TOOLS_OPENAI_KEY`

不在此白名单中的密钥不会被复制。

## SecretRef 处理 {#secretref-handling}

OpenClaw 中的令牌和 API 密钥配置值有三种格式：

```json
// 纯字符串
"channels": { "telegram": { "botToken": "123456:ABC-DEF..." } }

// 环境变量模板
"channels": { "telegram": { "botToken": "${TELEGRAM_BOT_TOKEN}" } }

// SecretRef 对象
"channels": { "telegram": { "botToken": { "source": "env", "id": "TELEGRAM_BOT_TOKEN" } } }
```

迁移会解析这三种格式。对于环境变量模板和 `source: "env"` 的 SecretRef，会从 `~/.openclaw/.env` 中查找对应值。`source: "file"` 或 `source: "exec"` 的 SecretRef 无法自动解析，迁移后需要手动添加到 Hermes。

## 迁移后操作

1. **检查迁移报告** — 迁移完成时会打印已迁移、跳过和冲突项的统计。

2. **查看归档文件** — 需要手动处理 `~/.hermes/migration/openclaw/<timestamp>/archive/` 中的内容。

3. **验证 API 密钥** — 运行 `hermes status` 检查提供商认证状态。

4. **测试消息发送** — 如果迁移了平台令牌，重启网关：`systemctl --user restart hermes-gateway`

5. **检查会话策略** — 确认 `hermes config get session_reset` 符合预期。

6. **重新配对 WhatsApp** — WhatsApp 使用二维码配对（Baileys），不支持令牌迁移。运行 `hermes whatsapp` 进行配对。

## 故障排查

### “找不到 OpenClaw 目录”

迁移会依次检查 `~/.openclaw/`、`~/.clawdbot/`、`~/.moldbot/`。如果你的安装路径不同，请使用 `--source /path/to/your/openclaw` 指定。

### “未找到提供商 API 密钥”

密钥可能在 `.env` 文件中，而非 `openclaw.json`。迁移会检查两者，确保 `~/.openclaw/.env` 存在且包含密钥。如果密钥使用了 `source: "file"` 或 `source: "exec"` 的 SecretRef，无法自动解析。

### 迁移后技能未显示

导入的技能位于 `~/.hermes/skills/openclaw-imports/`。启动新会话使其生效，或运行 `/skills` 确认已加载。

### TTS 语音未迁移

OpenClaw 的 TTS 设置存储在两个位置：`messages.tts.providers.*` 和顶层的 `talk` 配置。迁移会检查两处。如果你的语音 ID 是通过 OpenClaw UI 设置（存储路径不同），可能需要手动设置：`hermes config set tts.elevenlabs.voice_id YOUR_VOICE_ID`。
