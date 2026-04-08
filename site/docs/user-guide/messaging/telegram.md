---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

# Telegram 设置

Hermes Agent 作为一个功能全备的对话机器人与 Telegram 集成。连接后，你可以从任何设备与你的 Agent 聊天、发送会自动转录的语音备忘录、接收定时任务结果，并在群聊中使用 Agent。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/) 构建，支持文本、语音、图像和文件附件。

## 第 1 步：通过 BotFather 创建机器人

每个 Telegram 机器人（bot）都需要一个由 [@BotFather](https://t.me/BotFather) 颁发的 API 令牌（token），它是 Telegram 官方的机器人管理工具。

1. 打开 Telegram 并搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 选择一个 **显示名称**（例如 "Hermes Agent"）——这可以是任何名字
4. 选择一个 **用户名** —— 这必须是唯一的且以 `bot` 结尾（例如 `my_hermes_bot`）
5. BotFather 会回复你的 **API 令牌**。它看起来像这样：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请务必保密你的机器人令牌。任何拥有此令牌的人都可以控制你的机器人。如果泄露，请立即通过 BotFather 中的 `/revoke` 命令撤销。
:::

## 第 2 步：自定义你的机器人（可选）

这些 BotFather 命令可以提升用户体验。向 @BotFather 发送消息并使用：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始聊天前显示的“这个机器人能做什么？”文本 |
| `/setabouttext` | 机器人个人资料页上的简短介绍 |
| `/setuserpic` | 为你的机器人上传头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否能看到所有群组消息（见第 3 步） |

:::tip
对于 `/setcommands`，一组有用的初始设置如下：

```
help - 显示帮助信息
new - 开始新对话
sethome - 将此聊天设置为家庭频道
```
:::

## 第 3 步：隐私模式（对群组至关重要）

Telegram 机器人有一个**默认开启**的**隐私模式（privacy mode）**。这是在群组中使用机器人时最常见的困惑来源。

**当隐私模式开启（ON）时**，你的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自己消息的回包
- 服务消息（成员加入/离开、置顶消息等）
- 机器人作为管理员的频道中的消息

**当隐私模式关闭（OFF）时**，机器人会接收群组中的每一条消息。

### 如何禁用隐私模式

1. 给 **@BotFather** 发消息
2. 发送 `/mybots`
3. 选择你的机器人
4. 进入 **Bot Settings → Group Privacy → Turn off**

:::warning
更改隐私设置后，**你必须将机器人从所有群组中移除并重新添加**。Telegram 会在机器人加入群组时缓存隐私状态，在移除并重新添加之前，该状态不会更新。
:::

:::tip
禁用隐私模式的另一种方法：将机器人提升为**群组管理员**。管理员机器人总是能接收所有消息，无论隐私设置如何，这样可以避免切换全局隐私模式。
:::

## 第 4 步：查找你的用户 ID

Hermes Agent 使用数字形式的 Telegram 用户 ID 来控制访问权限。你的用户 ID **不是**你的用户名 —— 它是一个像 `123456789` 这样的数字。

**方法 1（推荐）：** 给 [@userinfobot](https://t.me/userinfobot) 发消息 —— 它会立即回复你的用户 ID。

**方法 2：** 给 [@get_id_bot](https://t.me/get_id_bot) 发消息 —— 另一个可靠的选择。

保存这个数字；下一步你会用到它。

## 第 5 步：配置 Hermes

### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

在提示时选择 **Telegram**。向导会询问你的机器人令牌和允许的用户 ID，然后为你编写配置。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # 多个用户用逗号分隔
```

### 启动网关

```bash
hermes gateway
```

机器人应该会在几秒钟内上线。在 Telegram 上给它发条消息来验证。

## Webhook 模式

默认情况下，Hermes 使用 **长轮询（long polling）** 连接到 Telegram —— 网关向 Telegram 服务器发起出站请求以获取新更新。这对于本地和常开的部署非常有效。

对于**云端部署**（Fly.io、Railway、Render 等），**Webhook 模式**更具成本效益。这些平台可以在有入站 HTTP 流量时自动唤醒挂起的机器，但出站连接则不行。由于轮询是出站的，轮询机器人永远无法休眠。Webhook 模式反转了方向 —— Telegram 将更新推送到机器人的 HTTPS URL，从而实现“闲时休眠”部署。

| | 轮询 (默认) | Webhook |
|---|---|---|
| 方向 | 网关 → Telegram (出站) | Telegram → 网关 (入站) |
| 适用场景 | 本地、常开服务器 | 具有自动唤醒功能的云平台 |
| 设置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 闲置成本 | 机器必须保持运行 | 机器可以在消息间隔期间休眠 |

### 配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认 8443
# TELEGRAM_WEBHOOK_SECRET=mysecret  # 可选，推荐设置
```

| 变量 | 必填 | 描述 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 发送更新的公开 HTTPS URL。URL 路径会自动提取（例如从上面的示例中提取 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | Webhook 服务器监听的本地端口（默认：`8443`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | 否 | 用于验证更新确实来自 Telegram 的密钥令牌。**强烈建议**在生产部署中使用。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关会启动 HTTP Webhook 服务器而不是轮询。未设置时，将使用轮询模式 —— 与之前版本的行为一致。

### 云部署示例 (Fly.io)

1. 将环境变量添加到你的 Fly.io 应用密钥中：

```bash
fly secrets set TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
fly secrets set TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)
```

2. 在 `fly.toml` 中暴露 Webhook 端口：

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

## 家庭频道

在任何 Telegram 聊天（私聊或群组）中使用 `/sethome` 命令将其指定为**家庭频道（home channel）**。定时任务（cron jobs）会将结果发送到此频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="我的笔记"
```

:::tip
群聊 ID 是负数（例如 `-1001234567890`）。你的个人私聊 ID 与你的用户 ID 相同。
:::

## 语音消息

### 传入语音（语音转文本）

你在 Telegram 上发送的语音消息会自动由 Hermes 配置的 STT 提供商进行转录，并作为文本注入到对话中。

- `local` 在运行 Hermes 的机器上使用 `faster-whisper` —— 不需要 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

### 传出语音（文本转语音）

当 Agent 通过 TTS 生成音频时，它会以 Telegram 原生**语音气泡**的形式发送 —— 即圆形的、可内联播放的那种。

- **OpenAI 和 ElevenLabs** 原生生成 Opus 格式 —— 无需额外设置
- **Edge TTS**（默认的免费提供商）输出 MP3，需要 **ffmpeg** 转换为 Opus：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

如果没有 ffmpeg，Edge TTS 音频将作为普通音频文件发送（仍然可以播放，但使用矩形播放器而不是语音气泡）。

在 `config.yaml` 的 `tts.provider` 键下配置 TTS 提供商。

## 群聊使用

Hermes Agent 在 Telegram 群聊中工作时有几点注意事项：

- **隐私模式**决定了机器人能看到哪些消息（见[第 3 步](#第-3-步隐私模式对群组至关重要)）
- `TELEGRAM_ALLOWED_USERS` 仍然适用 —— 即使在群组中，也只有授权用户才能触发机器人
- 你可以通过 `telegram.require_mention: true` 防止机器人响应普通的群组闲聊
- 开启 `telegram.require_mention: true` 后，只有满足以下条件的群组消息才会被接受：
  - 斜杠命令（slash commands）
  - 对机器人消息的回复
  - `@botusername` 提及
  - 匹配你在 `telegram.mention_patterns` 中配置的正则表达式唤醒词
- 如果 `telegram.require_mention` 未设置或为 false，Hermes 将保持之前的开放群组行为，响应它能看到的正常群组消息。
### 示例群组触发配置

将以下内容添加到 `~/.hermes/config.yaml`：

```yaml
telegram:
  require_mention: true
  mention_patterns:
    - "^\\s*chompy\\b"
```

此示例允许所有常规的直接触发方式，此外，即使没有使用 `@mention`，以 `chompy` 开头的消息也会触发。

### 关于 `mention_patterns` 的说明

- 模式使用 Python 正则表达式
- 匹配不区分大小写
- 模式会同时针对文本消息和媒体说明（captions）进行检查
- 无效的正则模式将被忽略，并在 gateway 日志中发出警告，而不会导致 Bot 崩溃
- 如果你希望模式仅在消息开头匹配，请使用 `^` 进行锚定

## 私聊话题 (Bot API 9.4)

Telegram Bot API 9.4（2026 年 2 月）引入了 **Private Chat Topics**（私聊话题）—— Bot 可以直接在 1 对 1 的私聊（DM）中创建论坛式的话题线程，无需超级群组。这让你可以在现有的 Hermes 私聊界面中运行多个相互隔离的工作空间。

### 使用场景

如果你同时进行多个长期项目，话题可以保持它们的上下文相互独立：

- **话题 "Website"** —— 处理你的生产环境 Web 服务
- **话题 "Research"** —— 文献综述和论文探索
- **话题 "General"** —— 杂项任务和快速提问

每个话题都有自己独立的对话会话、历史记录和上下文 —— 与其他话题完全隔离。

### 配置

在 `~/.hermes/config.yaml` 的 `platforms.telegram.extra.dm_topics` 下添加话题：

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
          skill: arxiv              # 在此话题中自动加载一个 skill
```

**字段说明：**

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 话题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 话题图标的自定义表情 ID |
| `skill` | 否 | 在此话题的新会话中自动加载的 Skill |
| `thread_id` | 否 | 话题创建后自动填充 —— 请勿手动设置 |

### 工作原理

1. 在 gateway 启动时，Hermes 会为每个还没有 `thread_id` 的话题调用 `createForumTopic`。
2. `thread_id` 会自动保存回 `config.yaml` —— 后续重启将跳过该 API 调用。
3. 每个话题映射到一个独立的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`。
4. 每个话题中的消息都有自己的对话历史、内存刷新和上下文窗口。

### Skill 绑定

带有 `skill` 字段的话题在该话题开启新会话时会自动加载该 Skill。这与在对话开始时输入 `/skill-name` 的效果完全一致 —— Skill 内容会被注入到第一条消息中，后续消息可以在对话历史中看到它。

例如，一个带有 `skill: arxiv` 的话题，每当其会话重置（由于空闲超时、每日重置或手动 `/reset`）时，都会预加载 arxiv skill。

:::tip
在配置之外创建的话题（例如通过手动调用 Telegram API 创建）会在 `forum_topic_created` 服务消息到达时被自动发现。你也可以在 gateway 运行时向配置中添加话题 —— 它们将在下一次缓存失效时被加载。
:::

## 群组论坛话题 Skill 绑定

启用了 **Topics mode**（也称为“论坛话题”）的超级群组已经实现了按话题的会话隔离 —— 每个 `thread_id` 映射到其自身的对话。但你可能希望在消息到达特定群组话题时 **自动加载一个 skill**，就像私聊话题的 Skill 绑定一样。

### 使用场景

一个拥有不同工作流论坛话题的团队超级群组：

- **Engineering** 话题 → 自动加载 `software-development` skill
- **Research** 话题 → 自动加载 `arxiv` skill
- **General** 话题 → 不加载 skill，作为通用助手

### 配置

在 `~/.hermes/config.yaml` 的 `platforms.telegram.extra.group_topics` 下添加话题绑定：

```yaml
platforms:
  telegram:
    extra:
      group_topics:
      - chat_id: -1001234567890       # 超级群组 ID
        topics:
        - name: Engineering
          thread_id: 5
          skill: software-development
        - name: Research
          thread_id: 12
          skill: arxiv
        - name: General
          thread_id: 1
          # 无 skill — 通用用途
```

**字段说明：**

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `chat_id` | 是 | 超级群组的数字 ID（以 `-100` 开头的负数） |
| `name` | 否 | 话题的可读标签（仅供参考） |
| `thread_id` | 是 | Telegram 论坛话题 ID —— 在 `t.me/c/<group_id>/<thread_id>` 链接中可见 |
| `skill` | 否 | 在此话题的新会话中自动加载的 Skill |

### 工作原理

1. 当消息到达已映射的群组话题时，Hermes 会在 `group_topics` 配置中查找 `chat_id` 和 `thread_id`。
2. 如果匹配的条目包含 `skill` 字段，该 Skill 将为该会话自动加载 —— 与私聊话题的 Skill 绑定逻辑相同。
3. 没有 `skill` 键的话题仅保持会话隔离（现有行为，保持不变）。
4. 未映射的 `thread_id` 或 `chat_id` 值将静默跳过 —— 无错误，不加载 Skill。

### 与私聊话题的区别

| | 私聊话题 (DM Topics) | 群组话题 (Group Topics) |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 话题创建 | 如果缺少 `thread_id`，Hermes 通过 API 创建话题 | 管理员在 Telegram UI 中创建话题 |
| `thread_id` | 创建后自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（管理员控制外观） |
| Skill 绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛话题原生内置） |

:::tip
要查找话题的 `thread_id`，请在 Telegram 网页版或桌面版中打开该话题并查看 URL：`https://t.me/c/1234567890/5` —— 最后一个数字 (`5`) 就是 `thread_id`。超级群组的 `chat_id` 是以 `-100` 为前缀的群组 ID（例如，群组 `1234567890` 变为 `-1001234567890`）。
:::

## 近期 Bot API 特性

- **Bot API 9.4 (2026 年 2 月):** 私聊话题 —— Bot 可以通过 `createForumTopic` 在 1 对 1 私聊中创建论坛话题。参见上文的 [私聊话题](#private-chat-topics-bot-api-94)。
- **隐私政策:** Telegram 现在要求 Bot 必须拥有隐私政策。通过 BotFather 使用 `/setprivacy_policy` 进行设置，否则 Telegram 可能会自动生成一个占位符。如果你的 Bot 是面向公众的，这一点尤为重要。
- **消息流式传输:** Bot API 9.x 增加了对长响应流式传输的支持，这可以改善 Agent 回复较长内容时的感知延迟。

## 交互式模型选择器

当你在 Telegram 聊天中发送不带参数的 `/model` 时，Hermes 会显示一个用于切换模型的交互式内联键盘：

1. **供应商选择** —— 按钮显示每个可用的供应商及其模型数量（例如，“OpenAI (15)”，“✓ Anthropic (12)” 表示当前供应商）。
2. **模型选择** —— 带有 **上一页**/**下一页** 导航的分页模型列表，以及返回供应商列表的 **返回** 按钮和 **取消** 按钮。

当前模型和供应商显示在顶部。所有导航操作都通过原地编辑同一条消息完成（不会弄乱聊天记录）。

:::tip
如果你知道确切的模型名称，直接输入 `/model <name>` 即可跳过选择器。你还可以输入 `/model <name> --global` 来跨会话持久化更改。
:::

## Webhook 模式

默认情况下，Telegram 适配器通过 **长轮询 (long polling)** 连接 —— gateway 向 Telegram 服务器发起出站连接。这种方式在任何地方都有效，但需要保持一个持久连接。

**Webhook 模式** 是一种替代方案，Telegram 通过 HTTPS 将更新推送到你的服务器。这对于 **无服务器 (serverless) 和云部署**（如 Fly.io、Railway 等）非常理想，因为入站 HTTP 请求可以唤醒挂起的机器。

### 配置

设置 `TELEGRAM_WEBHOOK_URL` 环境变量以启用 Webhook 模式：
```bash
# 必填 — 你的公网 HTTPS 端点
TELEGRAM_WEBHOOK_URL=https://app.fly.dev/telegram

# 选填 — 本地监听端口（默认：8443）
TELEGRAM_WEBHOOK_PORT=8443

# 选填 — 用于更新验证的密钥令牌（如果不设置则自动生成）
TELEGRAM_WEBHOOK_SECRET=my-secret-token
```

或者在 `~/.hermes/config.yaml` 中配置：

```yaml
telegram:
  webhook_mode: true
```

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关会启动一个监听在 `0.0.0.0:<port>` 的 HTTP 服务器，并向 Telegram 注册该 Webhook URL。URL 路径会从 Webhook URL 中提取（默认为 `/telegram`）。

:::warning 警告
Telegram 要求 Webhook 端点必须拥有**有效的 TLS 证书**。自签名证书将被拒绝。请使用反向代理（如 nginx、Caddy）或提供 TLS 终止的平台（如 Fly.io、Railway、Cloudflare Tunnel）。
:::

## DNS-over-HTTPS 备用 IP

在某些受限网络中，`api.telegram.org` 可能会解析到一个无法访问的 IP。Telegram 适配器包含一个**备用 IP** 机制，它可以在保留正确的 TLS 主机名和 SNI 的同时，透明地尝试连接备用 IP。

### 工作原理

1. 如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2. 否则，适配器会自动通过 DNS-over-HTTPS (DoH) 查询 **Google DNS** 和 **Cloudflare DNS**，以发现 `api.telegram.org` 的其他备用 IP。
3. DoH 返回的与系统 DNS 结果不同的 IP 将被用作备用。
4. 如果 DoH 也被屏蔽，将使用硬编码的种子 IP (`149.154.167.220`) 作为最后手段。
5. 一旦某个备用 IP 连接成功，它就会变为“粘性”状态 —— 后续请求将直接使用它，而不再尝试首选路径。

### 配置

```bash
# 明确指定备用 IP（逗号分隔）
TELEGRAM_FALLBACK_IPS=149.154.167.220,149.154.167.221
```

或者在 `~/.hermes/config.yaml` 中配置：

```yaml
platforms:
  telegram:
    extra:
      fallback_ips:
        - "149.154.167.220"
```

:::tip 提示
通常你不需要手动配置此项。通过 DoH 的自动发现机制可以处理大多数受限网络场景。只有当你的网络也屏蔽了 DoH 时，才需要设置 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::

## 消息回应 (Reactions)

Bot 可以向消息添加 Emoji 回应，作为处理进度的视觉反馈：

- 👀 当 Bot 开始处理你的消息时
- ✅ 当响应成功送达时
- ❌ 如果处理过程中发生错误

回应功能**默认禁用**。可以在 `config.yaml` 中开启：

```yaml
telegram:
  reactions: true
```

或者通过环境变量开启：

```bash
TELEGRAM_REACTIONS=true
```

:::note 注意
与 Discord（回应是累加的）不同，Telegram 的 Bot API 在单次调用中会替换所有 Bot 回应。从 👀 到 ✅/❌ 的转换是原子性的 —— 你不会同时看到两个图标。
:::

:::tip 提示
如果 Bot 在群组中没有添加回应的权限，回应调用会静默失败，消息处理将正常继续。
:::

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| Bot 完全没有响应 | 验证 `TELEGRAM_BOT_TOKEN` 是否正确。检查 `hermes gateway` 日志中的错误信息。 |
| Bot 响应 "unauthorized" | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。请通过 @userinfobot 再次核对。 |
| Bot 忽略群组消息 | 隐私模式（Privacy mode）可能已开启。请关闭它（步骤 3）或将 Bot 设为群组管理员。**更改隐私设置后，记得将 Bot 移出群组并重新添加。** |
| 语音消息未转录 | 验证 STT 是否可用：安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件而不是气泡 | 安装 `ffmpeg`（Edge TTS 进行 Opus 转换时需要）。 |
| Bot 令牌被撤销/无效 | 在 BotFather 中通过 `/revoke` 然后 `/newbot` 或 `/token` 生成新令牌。更新你的 `.env` 文件。 |
| Webhook 未收到更新 | 验证 `TELEGRAM_WEBHOOK_URL` 是否可从公网访问（用 `curl` 测试）。确保你的平台/反向代理将来自该 URL 端口的入站 HTTPS 流量转发到 `TELEGRAM_WEBHOOK_PORT` 配置的本地监听端口（两者端口号不必相同）。确保 SSL/TLS 已启用 —— Telegram 只向 HTTPS URL 发送数据。检查防火墙规则。 |

## 执行审批 (Exec Approval)

当 Agent 尝试运行潜在危险的命令时，它会在聊天中请求你的批准：

> ⚠️ This command is potentially dangerous (recursive delete). Reply "yes" to approve.

回复 "yes"/"y" 批准，或回复 "no"/"n" 拒绝。

## 安全性

:::warning 警告
务必设置 `TELEGRAM_ALLOWED_USERS` 以限制谁可以与你的 Bot 交互。如果没有设置，作为安全措施，网关默认会拒绝所有用户。
:::

切勿公开分享你的 Bot 令牌。如果泄露，请立即通过 BotFather 的 `/revoke` 命令撤销。

更多详情请参阅 [安全性文档](/user-guide/security)。你也可以使用 [私聊配对](/user-guide/messaging#dm-pairing-alternative-to-allowlists) 来实现更动态的用户授权方式。
