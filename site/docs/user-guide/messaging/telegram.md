---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

# Telegram 设置

Hermes Agent 作为一个功能齐全的对话机器人与 Telegram 集成。连接后，你可以在任何设备上与 Agent 聊天，发送语音备忘录并自动转录，接收定时任务结果，还能在群聊中使用 Agent。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/)，支持文本、语音、图片和文件附件。

## 第 1 步：通过 BotFather 创建机器人

每个 Telegram 机器人都需要由 Telegram 官方机器人管理工具 [@BotFather](https://t.me/BotFather) 颁发的 API 令牌。

1. 打开 Telegram，搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 选择一个 **显示名称**（例如 “Hermes Agent”）——可以随意取
4. 选择一个 **用户名** —— 必须唯一且以 `bot` 结尾（例如 `my_hermes_bot`）
5. BotFather 会回复你的 **API 令牌**，格式类似：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请妥善保管你的机器人令牌。任何拥有该令牌的人都能控制你的机器人。如果泄露，请立即通过 BotFather 发送 `/revoke` 撤销。
:::

## 第 2 步：自定义你的机器人（可选）

这些 BotFather 命令能提升用户体验。给 @BotFather 发送消息并使用：

| 命令 | 作用 |
|---------|---------|
| `/setdescription` | 在用户开始聊天前显示的“这个机器人能做什么？”文本 |
| `/setabouttext` | 机器人资料页上的简短介绍 |
| `/setuserpic` | 上传机器人的头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否能看到所有群消息（见第 3 步） |

:::tip
`/setcommands` 的一个实用起始命令集：

```
help - 显示帮助信息
new - 开始新对话
sethome - 设置此聊天为主频道
```
:::

## 第 3 步：隐私模式（群聊中至关重要）

Telegram 机器人默认启用 **隐私模式**。这是使用机器人在群聊中最常见的困惑来源。

**隐私模式开启时**，你的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人消息的回复
- 服务消息（成员加入/离开、置顶消息等）
- 机器人为管理员的频道中的消息

**隐私模式关闭时**，机器人能接收群里的所有消息。

### 如何关闭隐私模式

1. 给 **@BotFather** 发送消息
2. 发送 `/mybots`
3. 选择你的机器人
4. 进入 **机器人设置 → 群组隐私 → 关闭**

:::warning
**更改隐私设置后，必须将机器人从群组中移除再重新添加。** Telegram 会缓存机器人加入群组时的隐私状态，只有重新加入后才会更新。
:::

:::tip
关闭隐私模式的替代方案：将机器人提升为 **群管理员**。管理员机器人无论隐私设置如何都能接收所有消息，避免切换全局隐私模式。
:::

## 第 4 步：查找你的用户 ID

Hermes Agent 使用数字形式的 Telegram 用户 ID 来控制访问权限。你的用户 ID **不是**用户名，而是类似 `123456789` 的数字。

**方法 1（推荐）：** 给 [@userinfobot](https://t.me/userinfobot) 发送消息——它会立即回复你的用户 ID。

**方法 2：** 给 [@get_id_bot](https://t.me/get_id_bot) 发送消息——另一个可靠选项。

请保存这个数字，下一步会用到。

## 第 5 步：配置 Hermes

### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

提示时选择 **Telegram**。向导会询问你的机器人令牌和允许的用户 ID，然后帮你写入配置。

### 选项 B：手动配置

在 `~/.hermes/.env` 中添加：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # 多用户用逗号分隔
```

### 启动网关

```bash
hermes gateway
```

机器人应在几秒内上线。你可以在 Telegram 上给它发消息验证。

## Webhook 模式

默认情况下，Hermes 通过 **长轮询** 连接 Telegram——网关向 Telegram 服务器发起出站请求以获取新更新。这适合本地和持续运行的部署。

对于 **云端部署**（Fly.io、Railway、Render 等），**webhook 模式** 更节省成本。这些平台能在收到入站 HTTP 流量时自动唤醒休眠机器，但不能唤醒发起出站连接的机器。轮询是出站请求，轮询机器人永远不会休眠。Webhook 模式则相反——Telegram 会将更新推送到你的机器人 HTTPS URL，支持空闲时休眠的部署。

| | 轮询（默认） | Webhook |
|---|---|---|
| 方向 | 网关 → Telegram（出站） | Telegram → 网关（入站） |
| 适用场景 | 本地、持续运行服务器 | 支持自动唤醒的云平台 |
| 配置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲成本 | 机器必须持续运行 | 机器可在消息间休眠 |

### 配置

在 `~/.hermes/.env` 中添加：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认 8443
# TELEGRAM_WEBHOOK_SECRET=mysecret  # 可选，推荐使用
```

| 变量 | 是否必需 | 说明 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 发送更新的公共 HTTPS URL。路径会自动提取（例如上例中的 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | 本地 webhook 服务器监听端口（默认：`8443`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | 否 | 用于验证更新确实来自 Telegram 的密钥。**生产环境强烈推荐**。 |

设置了 `TELEGRAM_WEBHOOK_URL` 后，网关启动 HTTP webhook 服务器而非轮询。未设置时使用轮询模式——行为与之前版本一致。

### 云端部署示例（Fly.io）

1. 将环境变量添加到 Fly.io 应用密钥：

```bash
fly secrets set TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
fly secrets set TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)
```

2. 在 `fly.toml` 中暴露 webhook 端口：

```toml
[[services]]
  internal_port = 8443
  protocol = "tcp"

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

3. 部署：

```bash
fly deploy
```

网关日志应显示：`[telegram] Connected to Telegram (webhook mode)`。

## 主频道

在任何 Telegram 聊天（私聊或群聊）中使用 `/sethome` 命令，将其设为 **主频道**。定时任务（cron 作业）的结果会发送到该频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="My Notes"
```

:::tip
群聊 ID 是负数（例如 `-1001234567890`）。你的个人私聊 ID 与用户 ID 相同。
:::

## 语音消息

### 接收语音（语音转文本）

你在 Telegram 发送的语音消息会被 Hermes 配置的 STT 提供商自动转录，并作为文本注入对话中。

- `local` 使用运行 Hermes 的机器上的 `faster-whisper`，无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

### 发送语音（文本转语音）

当 Agent 生成音频时，会以 Telegram 原生的 **语音气泡** 形式发送——圆形、内联可播放。

- **OpenAI 和 ElevenLabs** 原生生成 Opus 格式，无需额外配置
- **Edge TTS**（默认免费提供商）输出 MP3，需要 **ffmpeg** 转码为 Opus：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

没有 ffmpeg 时，Edge TTS 音频会作为普通音频文件发送（仍可播放，但使用矩形播放器而非语音气泡）。

在 `config.yaml` 的 `tts.provider` 键下配置 TTS 提供商。

## 群聊使用

Hermes Agent 支持 Telegram 群聊，但需注意：

- **隐私模式** 决定机器人能看到哪些消息（见[第 3 步](#第-3-步隐私模式群聊中至关重要)）
- `TELEGRAM_ALLOWED_USERS` 依然生效——只有授权用户能触发机器人，即使在群里
- 你可以通过 `telegram.require_mention: true` 防止机器人响应普通群聊消息
- 设置 `telegram.require_mention: true` 后，群消息仅在以下情况被接受：
  - 斜杠命令
  - 回复机器人的消息
  - `@botusername` 提及
  - 匹配你配置的 `telegram.mention_patterns` 中的正则唤醒词
- 如果未设置或设置为 false，Hermes 保持之前的开放群聊行为，响应它能看到的普通群消息
### 示例群组触发配置

将以下内容添加到 `~/.hermes/config.yaml`：

```yaml
telegram:
  require_mention: true
  mention_patterns:
    - "^\\s*chompy\\b"
```

这个示例允许所有常规的直接触发消息，以及以 `chompy` 开头的消息，即使它们没有使用 `@mention`。

### 关于 `mention_patterns` 的说明

- 模式使用 Python 正则表达式
- 匹配不区分大小写
- 模式会同时匹配文本消息和媒体说明文字
- 无效的正则表达式模式会被忽略，并在网关日志中发出警告，而不会导致机器人崩溃
- 如果你希望模式只匹配消息开头，请用 `^` 进行锚定

## 私聊话题（Bot API 9.4） {#private-chat-topics-bot-api-94}

Telegram Bot API 9.4（2026年2月）引入了**私聊话题**——机器人可以直接在一对一私聊中创建论坛风格的话题线程，无需超级群组。这让你可以在现有的 Hermes 私聊中运行多个独立的工作空间。

### 使用场景

如果你同时处理多个长期项目，话题可以让它们的上下文保持独立：

- **话题“Website”** — 处理你的生产网站服务
- **话题“Research”** — 文献综述和论文探索
- **话题“General”** — 杂项任务和快速问题

每个话题都有自己的会话、历史和上下文，彼此完全隔离。

### 配置

在 `~/.hermes/config.yaml` 中的 `platforms.telegram.extra.dm_topics` 下添加话题：

```yaml
platforms:
  telegram:
    extra:
      dm_topics:
      - chat_id: 123456789        # 你的 Telegram 用户 ID
        topics:
        - name: General
          icon_color: 7322096
        - name: Website
          icon_color: 9367192
        - name: Research
          icon_color: 16766590
          skill: arxiv              # 在此话题自动加载一个 skill
```

**字段说明：**

| 字段 | 是否必填 | 说明 |
|-------|----------|-------------|
| `name` | 是 | 话题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 话题图标的自定义表情 ID |
| `skill` | 否 | 在此话题新会话时自动加载的 skill |
| `thread_id` | 否 | 话题创建后自动填充 — 不要手动设置 |

### 工作原理

1. 网关启动时，Hermes 会为每个还没有 `thread_id` 的话题调用 `createForumTopic`
2. `thread_id` 会自动保存回 `config.yaml`，后续重启时跳过 API 调用
3. 每个话题映射到一个独立的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4. 每个话题中的消息拥有独立的对话历史、记忆刷新和上下文窗口

### Skill 绑定

带有 `skill` 字段的话题会在新会话开始时自动加载该 skill。这和在对话开头输入 `/skill-name` 的效果一样——skill 内容会注入到第一条消息中，后续消息会在对话历史中看到它。

例如，带有 `skill: arxiv` 的话题在会话重置时（因空闲超时、每日重置或手动 `/reset`）会预加载 arxiv skill。

:::tip
通过配置外创建的话题（例如手动调用 Telegram API）会在收到 `forum_topic_created` 服务消息时自动被发现。你也可以在网关运行时添加话题到配置中——它们会在下一次缓存未命中时被加载。
:::

## 最近的 Bot API 功能

- **Bot API 9.4（2026年2月）：** 私聊话题——机器人可以通过 `createForumTopic` 在一对一私聊中创建论坛话题。详见上文 [私聊话题](#private-chat-topics-bot-api-94)。
- **隐私政策：** Telegram 现在要求机器人必须有隐私政策。通过 BotFather 使用 `/setprivacy_policy` 设置，否则 Telegram 可能自动生成占位符。对于公开机器人尤其重要。
- **消息流式传输：** Bot API 9.x 支持流式传输长回复，可以提升长回复的响应感知速度。

## Webhook 模式

默认情况下，Telegram 适配器通过**长轮询**连接——网关主动向 Telegram 服务器发起连接。这种方式适用所有环境，但会保持一个持久连接。

**Webhook 模式**是另一种方式，Telegram 会通过 HTTPS 主动推送更新到你的服务器。非常适合**无服务器和云部署**（如 Fly.io、Railway 等），可以通过入站 HTTP 唤醒休眠的机器。

### 配置

设置环境变量 `TELEGRAM_WEBHOOK_URL` 以启用 webhook 模式：

```bash
# 必填 — 你的公网 HTTPS 端点
TELEGRAM_WEBHOOK_URL=https://app.fly.dev/telegram

# 可选 — 本地监听端口（默认：8443）
TELEGRAM_WEBHOOK_PORT=8443

# 可选 — 用于更新验证的密钥令牌（未设置时自动生成）
TELEGRAM_WEBHOOK_SECRET=my-secret-token
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
telegram:
  webhook_mode: true
```

当设置了 `TELEGRAM_WEBHOOK_URL`，网关会启动一个监听 `0.0.0.0:<port>` 的 HTTP 服务器，并向 Telegram 注册 webhook URL。URL 路径从 webhook URL 中提取（默认是 `/telegram`）。

:::warning
Telegram 要求 webhook 端点必须有**有效的 TLS 证书**。自签名证书会被拒绝。请使用反向代理（nginx、Caddy）或提供 TLS 终止的云平台（Fly.io、Railway、Cloudflare Tunnel）。
:::

## DNS-over-HTTPS 备用 IP

在某些受限网络中，`api.telegram.org` 可能解析到无法访问的 IP。Telegram 适配器内置了**备用 IP**机制，会透明地尝试使用其他 IP 连接，同时保持正确的 TLS 主机名和 SNI。

### 工作原理

1. 如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2. 否则，适配器会自动通过 DNS-over-HTTPS（DoH）查询 Google DNS 和 Cloudflare DNS，获取 `api.telegram.org` 的备用 IP。
3. DoH 返回的、与系统 DNS 结果不同的 IP 会被用作备用。
4. 如果 DoH 也被屏蔽，则使用硬编码的种子 IP（`149.154.167.220`）作为最后手段。
5. 一旦某个备用 IP 连接成功，它会变成“粘性”的——后续请求直接使用该 IP，不再先尝试主路径。

### 配置

```bash
# 显式指定备用 IP（逗号分隔）
TELEGRAM_FALLBACK_IPS=149.154.167.220,149.154.167.221
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
platforms:
  telegram:
    extra:
      fallback_ips:
        - "149.154.167.220"
```

:::tip
通常不需要手动配置。DoH 自动发现机制能应对大多数受限网络场景。只有当你的网络也屏蔽了 DoH，才需要设置 `TELEGRAM_FALLBACK_IPS`。
:::

## 故障排查

| 问题 | 解决方案 |
|---------|----------|
| 机器人完全不响应 | 确认 `TELEGRAM_BOT_TOKEN` 是否正确。查看 `hermes gateway` 日志是否有错误。 |
| 机器人回复“unauthorized” | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。用 @userinfobot 再确认一次。 |
| 机器人忽略群组消息 | 可能是隐私模式开启了。关闭它（步骤3）或将机器人设为群管理员。**更改隐私设置后记得先移除再添加机器人。** |
| 语音消息未转录 | 确认 STT 可用：安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件而非气泡 | 安装 `ffmpeg`（Edge TTS Opus 转码需要）。 |
| 机器人令牌被撤销或无效 | 通过 BotFather 使用 `/revoke` 然后 `/newbot` 或 `/token` 生成新令牌。更新你的 `.env` 文件。 |
| Webhook 未接收更新 | 确认 `TELEGRAM_WEBHOOK_URL` 可公网访问（用 `curl` 测试）。确保你的平台或反向代理将该 URL 端口的 HTTPS 流量转发到本地监听端口（`TELEGRAM_WEBHOOK_PORT`，端口号可以不同）。确认 SSL/TLS 已启用——Telegram 只发送到 HTTPS URL。检查防火墙规则。 |

## 执行命令审批

当 Agent 试图执行潜在危险的命令时，会在聊天中请求你的批准：
> ⚠️ 该命令可能有危险（递归删除）。回复“yes”以确认执行。

回复“yes”/“y”确认，回复“no”/“n”拒绝。

## 安全

:::warning
务必设置 `TELEGRAM_ALLOWED_USERS` 来限制谁可以与你的 bot 交互。没有设置时，网关默认拒绝所有用户访问，以确保安全。
:::

切勿公开分享你的 bot token。如果泄露，请立即通过 BotFather 的 `/revoke` 命令撤销。

更多详情请参见[安全文档](/user-guide/security)。你也可以使用[私信配对](/user-guide/messaging#dm-pairing-alternative-to-allowlists)来实现更灵活的用户授权方式。
