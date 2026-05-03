---
sidebar_position: 10
title: "从 OpenClaw 迁移"
description: "将 OpenClaw / Clawdbot 配置迁移到 Hermes Agent 的完整指南——哪些内容会被迁移、配置映射关系以及迁移后需要检查什么。"
---

# 从 OpenClaw 迁移 {#migrate-from-openclaw}

`hermes claw migrate` 命令可将你的 OpenClaw（或旧版 Clawdbot/Moldbot）配置导入到 Hermes。本指南详细说明迁移的具体内容、配置键的映射关系以及迁移后需要验证的事项。

## 快速开始 {#quick-start}

```bash
# 预览后再迁移（始终先显示预览，然后询问确认）
hermes claw migrate

# 仅预览，不做任何更改
hermes claw migrate --dry-run

# 完整迁移（包含 API 密钥），跳过确认
hermes claw migrate --preset full --migrate-secrets --yes
```

迁移过程始终会在执行任何更改前显示完整的预览。查看列表后，确认即可继续。

默认读取 `~/.openclaw/` 目录。旧版 `~/.clawdbot/` 或 `~/.moltbot/` 目录会被自动检测。旧版配置文件名称（`clawdbot.json`、`moltbot.json`）同样会被自动识别。

## 选项 {#options}

| 选项 | 描述 |
|--------|------|
| `--dry-run` | 仅预览——显示将要迁移的内容后停止。 |
| `--preset &lt;name&gt;` | `full`（所有兼容设置）或 `user-data`（排除基础设施配置）。两种预设默认都不导入密钥——需要显式传递 `--migrate-secrets`。 |
| `--overwrite` | 冲突时覆盖现有 Hermes 文件（默认：当计划存在冲突时拒绝执行）。 |
| `--migrate-secrets` | 包含 API 密钥。即使在 `--preset full` 下也需要此选项——没有预设会静默导入密钥。 |
| `--no-backup` | 跳过迁移前对 `~/.hermes/` 的 zip 快照（默认情况下，在应用前会写入一个恢复点归档，位于 `~/.hermes/backups/pre-migration-*.zip`；可通过 `hermes import` 恢复）。 |
| `--source &lt;path&gt;` | 自定义 OpenClaw 目录。 |
| `--workspace-target &lt;path&gt;` | 放置 `AGENTS.md` 的目标路径。 |
| `--skill-conflict &lt;mode&gt;` | `skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 预览后跳过确认提示。 |

## 迁移内容 {#what-gets-migrated}

### 角色、记忆和指令 {#persona-memory-and-instructions}

| 内容 | OpenClaw 源位置 | Hermes 目标位置 | 备注 |
|------|----------------|-------------------|-------|
| 角色 | `workspace/SOUL.md` | `~/.hermes/SOUL.md` | 直接复制 |
| 工作区指令 | `workspace/AGENTS.md` | `--workspace-target` 指定的 `AGENTS.md` | 需要 `--workspace-target` 标志 |
| 长期记忆 | `workspace/MEMORY.md` | `~/.hermes/memories/MEMORY.md` | 解析为条目，与现有内容合并，去重。使用 `§` 分隔符。 |
| 用户档案 | `workspace/USER.md` | `~/.hermes/memories/USER.md` | 与记忆相同的条目合并逻辑。 |
| 每日记忆文件 | `workspace/memory/*.md` | `~/.hermes/memories/MEMORY.md` | 所有每日文件合并到主记忆文件中。 |

工作区文件也会在 `workspace.default/` 和 `workspace-main/` 中检查作为备选路径（OpenClaw 在最近版本中将 `workspace/` 重命名为 `workspace-main/`，并在多 Agent 设置中使用 `workspace-{agentId}`）。

### 技能（4 个来源） {#skills-4-sources}

| 来源 | OpenClaw 位置 | Hermes 目标位置 |
|--------|------------------|-------------------|
| 工作区技能 | `workspace/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 托管/共享技能 | `~/.openclaw/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 个人跨项目技能 | `~/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 项目级共享技能 | `workspace/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |
技能冲突由 `--skill-conflict` 处理：`skip` 保留已有的 Hermes 技能，`overwrite` 替换它，`rename` 则创建一个 `-imported` 副本。

### 模型与提供商配置 {#model-and-provider-configuration}

| 配置项 | OpenClaw 配置路径 | Hermes 目标位置 | 说明 |
|------|---------------------|-------------------|-------|
| 默认模型 | `agents.defaults.model` | `config.yaml` → `model` | 可以是字符串或 `{primary, fallbacks}` 对象 |
| 自定义提供商 | `models.providers.*` | `config.yaml` → `custom_providers` | 映射 `baseUrl`、`apiType`/`api` — 同时处理短名称（"openai"、"anthropic"）和带连字符的值（"openai-completions"、"anthropic-messages"、"google-generative-ai"） |
| 提供商 API 密钥 | `models.providers.*.apiKey` | `~/.hermes/.env` | 需要 `--migrate-secrets`。参见下方的 [API 密钥解析](#api-key-resolution)。 |

### Agent 行为 {#agent-behavior}

| 配置项 | OpenClaw 配置路径 | Hermes 配置路径 | 映射关系 |
|------|---------------------|-------------------|---------|
| 最大轮数 | `agents.defaults.timeoutSeconds` | `agent.max_turns` | `timeoutSeconds / 10`，上限 200 |
| 详细模式 | `agents.defaults.verboseDefault` | `agent.verbose` | "off" / "on" / "full" |
| 推理力度 | `agents.defaults.thinkingDefault` | `agent.reasoning_effort` | "always"/"high"/"xhigh" → "high"，"auto"/"medium"/"adaptive" → "medium"，"off"/"low"/"none"/"minimal" → "low" |
| 压缩 | `agents.defaults.compaction.mode` | `compression.enabled` | "off" → false，其他值 → true |
| 压缩模型 | `agents.defaults.compaction.model` | `compression.summary_model` | 直接复制字符串 |
| 人工延迟 | `agents.defaults.humanDelay.mode` | `human_delay.mode` | "natural" / "custom" / "off" |
| 人工延迟时间 | `agents.defaults.humanDelay.minMs` / `.maxMs` | `human_delay.min_ms` / `.max_ms` | 直接复制 |
| 时区 | `agents.defaults.userTimezone` | `timezone` | 直接复制字符串 |
| 执行超时 | `tools.exec.timeoutSec` | `terminal.timeout` | 直接复制（字段名为 `timeoutSec`，不是 `timeout`） |
| Docker 沙箱 | `agents.defaults.sandbox.backend` | `terminal.backend` | "docker" → "docker" |
| Docker 镜像 | `agents.defaults.sandbox.docker.image` | `terminal.docker_image` | 直接复制 |

### 会话重置策略 {#session-reset-policies}

| OpenClaw 配置路径 | Hermes 配置路径 | 说明 |
|---------------------|-------------------|-------|
| `session.reset.mode` | `session_reset.mode` | "daily"、"idle" 或两者 |
| `session.reset.atHour` | `session_reset.at_hour` | 每日重置的小时数（0–23） |
| `session.reset.idleMinutes` | `session_reset.idle_minutes` | 空闲分钟数 |

注意：OpenClaw 还有 `session.resetTriggers`（一个简单的字符串数组，如 `["daily", "idle"]`）。如果结构化的 `session.reset` 不存在，迁移会回退到从 `resetTriggers` 推断。

### MCP 服务器 {#mcp-servers}

| OpenClaw 字段 | Hermes 字段 | 说明 |
|----------------|-------------|-------|
| `mcp.servers.*.command` | `mcp_servers.*.command` | Stdio 传输 |
| `mcp.servers.*.args` | `mcp_servers.*.args` | |
| `mcp.servers.*.env` | `mcp_servers.*.env` | |
| `mcp.servers.*.cwd` | `mcp_servers.*.cwd` | |
| `mcp.servers.*.url` | `mcp_servers.*.url` | HTTP/SSE 传输 |
| `mcp.servers.*.tools.include` | `mcp_servers.*.tools.include` | 工具过滤 |
| `mcp.servers.*.tools.exclude` | `mcp_servers.*.tools.exclude` | |
### TTS（文本转语音） {#tts-text-to-speech}

TTS 设置从 **两个** OpenClaw 配置位置读取，优先级如下：

1. `messages.tts.providers.{provider}.*`（标准位置）
2. 顶层 `talk.providers.{provider}.*`（回退）
3. 旧式扁平键 `messages.tts.{provider}.*`（最旧格式）

| 配置项 | Hermes 目标位置 |
|------|-------------------|
| 提供商名称 | `config.yaml` → `tts.provider` |
| ElevenLabs 语音 ID | `config.yaml` → `tts.elevenlabs.voice_id` |
| ElevenLabs 模型 ID | `config.yaml` → `tts.elevenlabs.model_id` |
| OpenAI 模型 | `config.yaml` → `tts.openai.model` |
| OpenAI 语音 | `config.yaml` → `tts.openai.voice` |
| Edge TTS 语音 | `config.yaml` → `tts.edge.voice`（OpenClaw 将 "edge" 重命名为 "microsoft"——两者均被识别） |
| TTS 资源文件 | `~/.hermes/tts/`（文件复制） |

### 消息平台 {#messaging-platforms}

| 平台 | OpenClaw 配置路径 | Hermes `.env` 变量 | 备注 |
|----------|---------------------|----------------------|-------|
| Telegram | `channels.telegram.botToken` 或 `.accounts.default.botToken` | `TELEGRAM_BOT_TOKEN` | Token 可以是字符串或 [SecretRef](#secretref-handling)。支持扁平布局和 accounts 布局。 |
| Telegram | `credentials/telegram-default-allowFrom.json` | `TELEGRAM_ALLOWED_USERS` | 从 `allowFrom[]` 数组以逗号拼接 |
| Discord | `channels.discord.token` 或 `.accounts.default.token` | `DISCORD_BOT_TOKEN` | |
| Discord | `channels.discord.allowFrom` 或 `.accounts.default.allowFrom` | `DISCORD_ALLOWED_USERS` | |
| Slack | `channels.slack.botToken` 或 `.accounts.default.botToken` | `SLACK_BOT_TOKEN` | |
| Slack | `channels.slack.appToken` 或 `.accounts.default.appToken` | `SLACK_APP_TOKEN` | |
| Slack | `channels.slack.allowFrom` 或 `.accounts.default.allowFrom` | `SLACK_ALLOWED_USERS` | |
| WhatsApp | `channels.whatsapp.allowFrom` 或 `.accounts.default.allowFrom` | `WHATSAPP_ALLOWED_USERS` | 通过 Baileys QR 配对进行认证——迁移后需要重新配对 |
| Signal | `channels.signal.account` 或 `.accounts.default.account` | `SIGNAL_ACCOUNT` | |
| Signal | `channels.signal.httpUrl` 或 `.accounts.default.httpUrl` | `SIGNAL_HTTP_URL` | |
| Signal | `channels.signal.allowFrom` 或 `.accounts.default.allowFrom` | `SIGNAL_ALLOWED_USERS` | |
| Matrix | `channels.matrix.accessToken` 或 `.accounts.default.accessToken` | `MATRIX_ACCESS_TOKEN` | 使用 `accessToken`（而非 `botToken`） |
| Mattermost | `channels.mattermost.botToken` 或 `.accounts.default.botToken` | `MATTERMOST_BOT_TOKEN` | |

### 其他配置 {#other-config}

| 配置项 | OpenClaw 路径 | Hermes 路径 | 备注 |
|------|-------------|-------------|-------|
| 审批模式 | `approvals.exec.mode` | `config.yaml` → `approvals.mode` | "auto"→"off", "always"→"manual", "smart"→"smart" |
| 命令白名单 | `exec-approvals.json` | `config.yaml` → `command_allowlist` | 模式合并并去重 |
| 浏览器 CDP URL | `browser.cdpUrl` | `config.yaml` → `browser.cdp_url` | |
| 浏览器无头模式 | `browser.headless` | `config.yaml` → `browser.headless` | |
| Brave 搜索密钥 | `tools.web.search.brave.apiKey` | `.env` → `BRAVE_API_KEY` | 需要 `--migrate-secrets` |
| Gateway 认证令牌 | `gateway.auth.token` | `.env` → `HERMES_GATEWAY_TOKEN` | 需要 `--migrate-secrets` |
| 工作目录 | `agents.defaults.workspace` | `.env` → `MESSAGING_CWD` | |
### 已归档（无直接 Hermes 等价项） {#archived-no-direct-hermes-equivalent}

这些文件被保存到 `~/.hermes/migration/openclaw/&lt;timestamp&gt;/archive/` 中，供手动审查：

| 内容 | 归档文件 | 如何在 Hermes 中重建 |
|------|-------------|--------------------------|
| `IDENTITY.md` | `archive/workspace/IDENTITY.md` | 合并到 `SOUL.md` |
| `TOOLS.md` | `archive/workspace/TOOLS.md` | Hermes 内置了工具指令 |
| `HEARTBEAT.md` | `archive/workspace/HEARTBEAT.md` | 使用 cron 任务处理周期性任务 |
| `BOOTSTRAP.md` | `archive/workspace/BOOTSTRAP.md` | 使用上下文文件或技能 |
| Cron 任务 | `archive/cron-config.json` | 用 `hermes cron create` 重新创建 |
| 插件 | `archive/plugins-config.json` | 参见[插件指南](/user-guide/features/hooks) |
| Hooks/Webhooks | `archive/hooks-config.json` | 使用 `hermes webhook` 或网关 hooks |
| 记忆后端 | `archive/memory-backend-config.json` | 通过 `hermes honcho` 配置 |
| 技能注册表 | `archive/skills-registry-config.json` | 使用 `hermes skills config` |
| UI/身份 | `archive/ui-identity-config.json` | 使用 `/skin` 命令 |
| 日志 | `archive/logging-diagnostics-config.json` | 在 `config.yaml` 的 logging 部分设置 |
| 多 Agent 列表 | `archive/agents-list.json` | 使用 Hermes 配置文件 |
| 渠道绑定 | `archive/bindings.json` | 按平台手动设置 |
| 复杂渠道 | `archive/channels-deep-config.json` | 手动配置平台 |

## API 密钥解析 {#api-key-resolution}

当启用 `--migrate-secrets` 时，API 密钥会按优先级从**四个来源**收集：

1. **配置值** — `openclaw.json` 中的 `models.providers.*.apiKey` 和 TTS 提供商密钥
2. **环境文件** — `~/.openclaw/.env`（密钥如 `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` 等）
3. **配置 env 子对象** — `openclaw.json` → `"env"` 或 `"env"."vars"`（某些配置将密钥存储在此处，而非单独的 `.env` 文件）
4. **认证配置文件** — `~/.openclaw/agents/main/agent/auth-profiles.json`（每个 Agent 的凭据）

配置值优先级最高。后续每个来源会填补剩余的空缺。

### 支持的密钥目标 {#supported-key-targets}

`OPENROUTER_API_KEY`、`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`DEEPSEEK_API_KEY`、`GEMINI_API_KEY`、`ZAI_API_KEY`、`MINIMAX_API_KEY`、`ELEVENLABS_API_KEY`、`TELEGRAM_BOT_TOKEN`、`VOICE_TOOLS_OPENAI_KEY`

不在该允许列表中的密钥不会被复制。

## SecretRef 处理 {#secretref-handling}

OpenClaw 配置中的令牌和 API 密钥值可以有三种格式：

```json
// 纯字符串
"channels": { "telegram": { "botToken": "123456:ABC-DEF..." } }

// 环境变量模板
"channels": { "telegram": { "botToken": "${TELEGRAM_BOT_TOKEN}" } }

// SecretRef 对象
"channels": { "telegram": { "botToken": { "source": "env", "id": "TELEGRAM_BOT_TOKEN" } } }
```

迁移过程会解析所有三种格式。对于环境变量模板和 `source: "env"` 的 SecretRef 对象，会在 `~/.openclaw/.env` 和 `openclaw.json` 的 env 子对象中查找值。`source: "file"` 或 `source: "exec"` 的 SecretRef 对象无法自动解析——迁移过程会对此发出警告，这些值必须通过 `hermes config set` 手动添加到 Hermes 中。
## 迁移之后 {#after-migration}

1. **检查迁移报告** — 迁移完成后会打印报告，包含已迁移、已跳过和冲突项的数量。

2. **审查归档文件** — `~/.hermes/migration/openclaw/&lt;timestamp&gt;/archive/` 中的任何内容都需要手动处理。

3. **启动新会话** — 导入的技能和记忆条目在新会话中生效，而非当前会话。

4. **验证 API 密钥** — 运行 `hermes status` 检查提供商认证状态。

5. **测试消息功能** — 如果你迁移了平台令牌，请重启网关：`systemctl --user restart hermes-gateway`

6. **检查会话策略** — 确认 `hermes config get session_reset` 符合你的预期。

7. **重新配对 WhatsApp** — WhatsApp 使用二维码配对（Baileys），不支持令牌迁移。运行 `hermes whatsapp` 进行配对。

8. **清理归档** — 确认一切正常后，运行 `hermes claw cleanup` 将剩余的 OpenClaw 目录重命名为 `.pre-migration/`（防止状态混淆）。

## 故障排除 {#troubleshooting}

### "未找到 OpenClaw 目录" {#openclaw-directory-not-found}

迁移会依次检查 `~/.openclaw/`、`~/.clawdbot/` 和 `~/.moltbot/`。如果你的安装在其他位置，请使用 `--source /path/to/your/openclaw`。

### "未找到提供商 API 密钥" {#no-provider-api-keys-found}

密钥可能存储在多个位置，具体取决于你的 OpenClaw 版本：内联在 `openclaw.json` 的 `models.providers.*.apiKey` 中、`~/.openclaw/.env` 中、`openclaw.json` 的 `"env"` 子对象中，或 `agents/main/agent/auth-profiles.json` 中。迁移会检查所有四个位置。如果密钥使用了 `source: "file"` 或 `source: "exec"` 的 SecretRef，则无法自动解析——请通过 `hermes config set` 手动添加。

### 迁移后技能未出现 {#skills-not-appearing-after-migration}

导入的技能位于 `~/.hermes/skills/openclaw-imports/`。启动新会话使其生效，或运行 `/skills` 确认它们已加载。

### TTS 语音未迁移 {#tts-voice-not-migrated}

OpenClaw 将 TTS 设置存储在两个位置：`messages.tts.providers.*` 和顶层 `talk` 配置。迁移会检查这两个位置。如果你的语音 ID 是通过 OpenClaw UI 设置的（存储在不同路径），你可能需要手动设置：`hermes config set tts.elevenlabs.voice_id YOUR_VOICE_ID`。
