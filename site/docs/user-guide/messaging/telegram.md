---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

# Telegram 设置

Hermes Agent 可以作为功能完备的对话机器人集成到 Telegram 中。连接后，你可以从任何设备与你的 Agent 聊天、发送会自动转录的语音备忘录、接收定时任务结果，并在群聊中使用该 Agent。此集成基于 [python-telegram-bot](https://python-telegram-bot.org/) 构建，支持文本、语音、图片和文件附件。

## 第 1 步：通过 BotFather 创建机器人

每个 Telegram 机器人都需要一个由 [@BotFather](https://t.me/BotFather)（Telegram 官方机器人管理工具）颁发的 API token。

1. 打开 Telegram 并搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 选择一个**显示名称**（例如 "Hermes Agent"）——可以是任何名称
4. 选择一个**用户名**——必须是唯一的，且以 `bot` 结尾（例如 `my_hermes_bot`）
5. BotFather 会回复你的 **API token**。它看起来像这样：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请妥善保管你的机器人 token。任何拥有此 token 的人都可以控制你的机器人。如果发生泄露，请立即通过 BotFather 发送 `/revoke` 进行撤销。
:::

## 第 2 步：自定义你的机器人（可选）

这些 BotFather 命令可以改善用户体验。给 @BotFather 发送消息并使用：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始聊天前显示的“此机器人能做什么？”文本 |
| `/setabouttext` | 机器人个人资料页面上的简短文本 |
| `/setuserpic` | 为你的机器人上传头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否查看所有群组消息（见第 3 步） |

:::tip
对于 `/setcommands`，一套实用的初始命令如下：

```
help - 显示帮助信息
new - 开始新对话
sethome - 将此聊天设置为家庭频道
```
:::

## 第 3 步：隐私模式（群组关键设置） {#step-3-privacy-mode-critical-for-groups}

Telegram 机器人有一个**默认开启**的**隐私模式**。这是在群组中使用机器人时最常见的困惑来源。

**当隐私模式开启时**，你的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自身消息的内容
- 服务消息（成员加入/离开、置顶消息等）
- 机器人在其中拥有管理员权限的频道中的消息

**当隐私模式关闭时**，机器人会接收群组中的每一条消息。

### 如何关闭隐私模式

1. 给 **@BotFather** 发送消息
2. 发送 `/mybots`
3. 选择你的机器人
4. 进入 **Bot Settings → Group Privacy → Turn off**

:::warning
更改隐私设置后，**你必须将机器人从所有群组中移除并重新添加**。Telegram 会在机器人加入群组时缓存隐私状态，除非移除并重新添加，否则状态不会更新。
:::

:::tip
关闭隐私模式的替代方案：将机器人提升为**群组管理员**。管理员机器人无论隐私设置如何，始终能接收所有消息，这样就无需切换全局隐私模式。
:::

## 第 4 步：查找你的用户 ID

Hermes Agent 使用数字形式的 Telegram 用户 ID 来控制访问权限。你的用户 ID **不是**你的用户名——它是一个类似 `123456789` 的数字。

**方法 1（推荐）：** 给 [@userinfobot](https://t.me/userinfobot) 发送消息——它会立即回复你的用户 ID。

**方法 2：** 给 [@get_id_bot](https://t.me/get_id_bot) 发送消息——这是另一个可靠的选择。

请保存此数字；下一步配置时会用到。

## 第 5 步：配置 Hermes

### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

在提示时选择 **Telegram**。设置向导会询问你的机器人 token 和允许的用户 ID，然后为你写入配置文件。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # 多个用户请用逗号分隔
```

### 启动网关

```bash
hermes gateway
```

机器人应在几秒钟内上线。在 Telegram 上给它发送一条消息以进行验证。

## Webhook 模式

默认情况下，Hermes 使用**长轮询 (long polling)** 连接到 Telegram——网关会向 Telegram 服务器发起出站请求以获取新更新。这适用于本地和始终在线的部署环境。
对于**云端部署**（如 Fly.io、Railway、Render 等），**Webhook 模式**更具成本效益。这些平台可以在接收到入站 HTTP 流量时自动唤醒挂起的机器，但无法通过出站连接唤醒。由于轮询（Polling）属于出站连接，使用轮询的机器人将无法进入休眠状态。Webhook 模式则改变了方向——由 Telegram 将更新推送到你机器人的 HTTPS URL，从而实现“闲置时休眠”的部署方式。

| | 轮询 (默认) | Webhook |
|---|---|---|
| 方向 | 网关 → Telegram (出站) | Telegram → 网关 (入站) |
| 适用场景 | 本地、始终在线的服务器 | 支持自动唤醒的云平台 |
| 设置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 闲置成本 | 机器必须保持运行 | 消息间隙机器可休眠 |

### 配置

将以下内容添加到 `~/.hermes/.env` 中：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认为 8443
# TELEGRAM_WEBHOOK_SECRET=mysecret  # 可选，强烈推荐
```

| 变量 | 必填 | 描述 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 发送更新的公共 HTTPS URL。URL 路径会自动提取（例如上述示例中的 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | Webhook 服务器监听的本地端口（默认：`8443`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | 否 | 用于验证更新确实来自 Telegram 的密钥令牌。生产环境部署**强烈推荐**使用。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 后，网关将启动 HTTP Webhook 服务器，而不是进行轮询。如果不设置，则使用轮询模式——与之前版本的行为保持一致。

### 云端部署示例 (Fly.io)

1. 将环境变量添加到你的 Fly.io 应用密钥中：

```bash
fly secrets set TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
fly secrets set TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)
```

2. 在你的 `fly.toml` 中暴露 Webhook 端口：

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

## 主频道 (Home Channel)

在任何 Telegram 聊天（私聊或群组）中使用 `/sethome` 命令，将其指定为**主频道**。定时任务（cron jobs）会将结果发送到此频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="My Notes"
```

:::tip
群组聊天 ID 是负数（例如 `-1001234567890`）。你的个人私聊 ID 与你的用户 ID 相同。
:::

## 语音消息

### 传入语音 (语音转文字)

你在 Telegram 上发送的语音消息会自动由 Hermes 配置的 STT 提供商进行转录，并作为文本注入到对话中。

- `local` 使用运行 Hermes 的机器上的 `faster-whisper` —— 无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

### 传出语音 (文字转语音)

当 Agent 通过 TTS 生成音频时，它会以原生的 Telegram **语音气泡**形式发送——即那种圆形的、可直接在对话中播放的格式。

- **OpenAI 和 ElevenLabs** 原生生成 Opus 格式 —— 无需额外设置
- **Edge TTS**（默认免费提供商）输出 MP3 格式，需要 **ffmpeg** 转换为 Opus：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

如果没有 ffmpeg，Edge TTS 音频将作为普通音频文件发送（仍然可以播放，但会使用矩形播放器而不是语音气泡）。

在 `config.yaml` 的 `tts.provider` 键下配置 TTS 提供商。

## 群组聊天使用

Hermes Agent 在 Telegram 群组聊天中工作时需要注意以下几点：

- **隐私模式**决定了机器人能看到哪些消息（参见 [步骤 3](#step-3-privacy-mode-critical-for-groups)）
- `TELEGRAM_ALLOWED_USERS` 依然有效 —— 即使在群组中，也只有授权用户才能触发机器人
- 你可以通过 `telegram.require_mention: true` 防止机器人响应普通的群组闲聊
- 设置 `telegram.require_mention: true` 后，群组消息仅在以下情况被接受：
  - 斜杠命令
  - 回复机器人的某条消息
  - `@botusername` 提及
  - 匹配你在 `telegram.mention_patterns` 中配置的正则表达式唤醒词
- 如果未设置 `telegram.require_mention` 或设为 false，Hermes 将保持之前的开放群组行为，并响应它能看到的普通群组消息
### 群组触发器配置示例

将以下内容添加到 `~/.hermes/config.yaml` 中：

```yaml
telegram:
  require_mention: true
  mention_patterns:
    - "^\\s*chompy\\b"
```

此示例允许所有常规的直接触发方式，以及以 `chompy` 开头的消息，即使它们没有使用 `@mention`。

### 关于 `mention_patterns` 的说明

- 模式使用 Python 正则表达式
- 匹配不区分大小写
- 模式会同时针对文本消息和媒体说明文字进行检查
- 无效的正则表达式会被忽略，并在网关日志中记录警告，而不会导致机器人崩溃
- 如果希望模式仅在消息开头匹配，请使用 `^` 进行锚定

## 私聊话题 (Bot API 9.4) {#private-chat-topics-bot-api-94}

Telegram Bot API 9.4（2026 年 2 月）引入了**私聊话题 (Private Chat Topics)** —— 机器人可以直接在一对一私聊中创建论坛式的话题线程，无需超级群组。这让你可以在现有的 Hermes 私聊中运行多个隔离的工作区。

### 使用场景

如果你同时处理多个长期项目，话题可以将它们的上下文分开：

- **“网站”话题** — 处理生产环境的 Web 服务
- **“研究”话题** — 文献综述和论文探索
- **“常规”话题** — 杂项任务和快速提问

每个话题都有自己的对话会话、历史记录和上下文，与其他话题完全隔离。

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
          skill: arxiv              # 在此话题中自动加载技能
```

**字段说明：**

| 字段 | 必填 | 说明 |
|-------|----------|-------------|
| `name` | 是 | 话题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 话题图标的自定义表情 ID |
| `skill` | 否 | 在此话题的新会话中自动加载的技能 |
| `thread_id` | 否 | 话题创建后自动填充 — 请勿手动设置 |

### 工作原理

1. 网关启动时，Hermes 会为每个尚未拥有 `thread_id` 的话题调用 `createForumTopic`
2. `thread_id` 会自动保存回 `config.yaml` — 后续重启将跳过此 API 调用
3. 每个话题映射到一个隔离的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4. 每个话题的消息都有自己的对话历史、内存刷新和上下文窗口

### 技能绑定

带有 `skill` 字段的话题会在该话题开始新会话时自动加载相应技能。这与在对话开始时输入 `/skill-name` 的效果完全相同 —— 技能内容会被注入到第一条消息中，后续消息会在对话历史中看到它。

例如，带有 `skill: arxiv` 的话题在会话重置（由于空闲超时、每日重置或手动 `/reset`）时，会自动预加载 arxiv 技能。

:::tip
在配置之外创建的话题（例如通过手动调用 Telegram API 创建）会在收到 `forum_topic_created` 服务消息时被自动发现。你也可以在网关运行时向配置中添加话题 —— 它们会在下一次缓存未命中时被加载。
:::

## 群组论坛话题技能绑定

启用了**话题模式**（也称为“论坛话题”）的超级群组已经实现了按话题进行会话隔离 —— 每个 `thread_id` 映射到其自己的对话。但你可能希望在特定群组话题中收到消息时**自动加载技能**，就像私聊话题技能绑定那样。

### 使用场景

一个拥有不同工作流论坛话题的团队超级群组：

- **工程**话题 → 自动加载 `software-development` 技能
- **研究**话题 → 自动加载 `arxiv` 技能
- **常规**话题 → 无技能，通用助手

### 配置
在 `~/.hermes/config.yaml` 中的 `platforms.telegram.extra.group_topics` 下添加话题绑定：

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
| `name` | 否 | 话题的人类可读标签（仅供参考） |
| `thread_id` | 是 | Telegram 论坛话题 ID — 可在 `t.me/c/<group_id>/<thread_id>` 链接中看到 |
| `skill` | 否 | 在此话题中开启新会话时自动加载的 Skill |

### 工作原理

1. 当消息到达已映射的群组话题时，Hermes 会在 `group_topics` 配置中查找对应的 `chat_id` 和 `thread_id`。
2. 如果匹配的条目包含 `skill` 字段，该 Skill 会自动加载到会话中 — 这与私聊（DM）话题的 Skill 绑定逻辑一致。
3. 没有 `skill` 键的话题仅实现会话隔离（保持原有行为，无变化）。
4. 未映射的 `thread_id` 或 `chat_id` 值会被静默忽略 — 不报错，也不加载 Skill。

### 与私聊（DM）话题的区别

| | 私聊（DM）话题 | 群组话题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 话题创建 | 若缺少 `thread_id`，Hermes 会通过 API 创建 | 管理员在 Telegram UI 中创建 |
| `thread_id` | 创建后自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（外观由管理员控制） |
| Skill 绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛话题自带功能） |

:::tip
要查找话题的 `thread_id`，请在 Telegram Web 或桌面端打开该话题并查看 URL：`https://t.me/c/1234567890/5` — 最后一个数字 (`5`) 即为 `thread_id`。超级群组的 `chat_id` 是群组 ID 前面加上 `-100`（例如，群组 `1234567890` 变为 `-1001234567890`）。
:::

## Bot API 近期功能

- **Bot API 9.4 (2026年2月):** 私聊话题 — 机器人可以通过 `createForumTopic` 在一对一私聊中创建论坛话题。请参阅上方的 [私聊话题 (Bot API 9.4)](#private-chat-topics-bot-api-94)。
- **隐私政策:** Telegram 现在要求机器人必须具备隐私政策。请通过 BotFather 使用 `/setprivacy_policy` 进行设置，否则 Telegram 可能会自动生成一个占位符。如果你的机器人是面向公众的，这一点尤为重要。
- **消息流式传输:** Bot API 9.x 增加了对流式传输长响应的支持，这可以改善长 Agent 回复的感知延迟。

## 交互式模型选择器

当你在 Telegram 聊天中发送不带参数的 `/model` 命令时，Hermes 会显示一个交互式内联键盘，用于切换模型：

1. **提供商选择** — 显示每个可用提供商及其模型数量的按钮（例如，当前提供商显示为“✓ Anthropic (12)”，其他显示为“OpenAI (15)”）。
2. **模型选择** — 分页的模型列表，带有 **Prev**（上一页）/**Next**（下一页）导航，以及用于返回提供商列表的 **Back**（返回）按钮和 **Cancel**（取消）。

当前模型和提供商显示在顶部。所有导航操作均通过原地编辑同一条消息完成（不会造成聊天刷屏）。

:::tip
如果你知道确切的模型名称，可以直接输入 `/model <name>` 跳过选择器。你也可以输入 `/model <name> --global` 将更改持久化到所有会话中。
:::

## Webhook 模式

默认情况下，Telegram 适配器通过 **长轮询 (long polling)** 连接 — 网关主动向 Telegram 服务器发起出站连接。这种方式适用于所有环境，但会保持一个持久连接。

**Webhook 模式** 是另一种选择，Telegram 会通过 HTTPS 将更新推送到你的服务器。这非常适合 **Serverless 和云部署**（如 Fly.io、Railway 等），因为入站 HTTP 请求可以唤醒处于挂起状态的机器。

### 配置

设置 `TELEGRAM_WEBHOOK_URL` 环境变量以启用 Webhook 模式：
```bash
# 必需 — 你的公共 HTTPS 端点
TELEGRAM_WEBHOOK_URL=https://app.fly.dev/telegram

# 可选 — 本地监听端口（默认为 8443）
TELEGRAM_WEBHOOK_PORT=8443

# 可选 — 用于更新验证的密钥令牌（若未设置则自动生成）
TELEGRAM_WEBHOOK_SECRET=my-secret-token
```

或者在 `~/.hermes/config.yaml` 中配置：

```yaml
telegram:
  webhook_mode: true
```

当设置了 `TELEGRAM_WEBHOOK_URL` 后，网关会启动一个监听 `0.0.0.0:<port>` 的 HTTP 服务器，并向 Telegram 注册该 Webhook URL。URL 路径会从 Webhook URL 中提取（默认为 `/telegram`）。

:::warning
Telegram 要求 Webhook 端点必须拥有**有效的 TLS 证书**。自签名证书将被拒绝。请使用反向代理（如 nginx、Caddy）或提供 TLS 终止服务的平台（如 Fly.io、Railway、Cloudflare Tunnel）。
:::

## DNS-over-HTTPS 后备 IP

在某些受限网络中，`api.telegram.org` 可能解析到无法访问的 IP。Telegram 适配器包含一套**后备 IP** 机制，它会在保留正确 TLS 主机名和 SNI 的前提下，透明地尝试通过备用 IP 进行连接。

### 工作原理

1. 如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2. 否则，适配器会自动通过 DNS-over-HTTPS (DoH) 查询 **Google DNS** 和 **Cloudflare DNS**，以发现 `api.telegram.org` 的备用 IP。
3. 将 DoH 返回的、且与系统 DNS 结果不同的 IP 用作后备。
4. 如果 DoH 也被屏蔽，则将硬编码的种子 IP (`149.154.167.220`) 作为最后手段。
5. 一旦某个后备 IP 连接成功，它就会变得“粘性（sticky）”——后续请求将直接使用该 IP，而无需先尝试主路径。

### 配置

```bash
# 显式指定后备 IP（以逗号分隔）
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

:::tip
通常你不需要手动配置此项。通过 DoH 进行的自动发现功能可以处理大多数受限网络场景。只有当你的网络也屏蔽了 DoH 时，才需要使用 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::

## 代理支持

如果你的网络需要通过 HTTP 代理才能访问互联网（在企业环境中很常见），Telegram 适配器会自动读取标准的代理环境变量，并将所有连接通过代理路由。

### 支持的变量

适配器会按顺序检查以下环境变量，并使用第一个被设置的变量：

1. `HTTPS_PROXY`
2. `HTTP_PROXY`
3. `ALL_PROXY`
4. `https_proxy` / `http_proxy` / `all_proxy`（小写变体）

### 配置

在启动网关之前，在你的环境中设置代理：

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

或者将其添加到 `~/.hermes/.env` 中：

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

该代理设置同时适用于主传输层和所有后备 IP 传输层。无需额外的 Hermes 配置——只要设置了环境变量，它就会自动生效。

:::note
这涵盖了 Hermes 为 Telegram 连接使用的自定义后备传输层。其他地方使用的标准 `httpx` 客户端本身就已经遵循代理环境变量。
:::

## 消息反应 (Message Reactions)

机器人可以为消息添加 emoji 反应，作为视觉上的处理反馈：

- 👀 当机器人开始处理你的消息时
- ✅ 当响应成功送达时
- ❌ 如果处理过程中发生错误

反应功能**默认禁用**。请在 `config.yaml` 中启用：

```yaml
telegram:
  reactions: true
```

或者通过环境变量启用：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（反应是累加的）不同，Telegram 的 Bot API 在单次调用中会替换掉机器人所有的反应。从 👀 到 ✅/❌ 的转换是原子性的——你不会同时看到这两个图标。
:::

:::tip
如果机器人在群组中没有添加反应的权限，反应调用会静默失败，消息处理将照常进行。
:::
## 故障排查

| 问题 | 解决方案 |
|---------|----------|
| Bot 完全没有响应 | 验证 `TELEGRAM_BOT_TOKEN` 是否正确。检查 `hermes gateway` 日志以查看错误信息。 |
| Bot 回复 "unauthorized" | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。请通过 @userinfobot 再次确认。 |
| Bot 忽略群组消息 | 可能是开启了隐私模式。请禁用它（参考第 3 步）或将 Bot 设为群管理员。**注意：更改隐私设置后，请务必将 Bot 移除并重新添加。** |
| 语音消息无法转录 | 验证 STT 是否可用：安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复显示为文件而非气泡 | 安装 `ffmpeg`（Edge TTS Opus 转换所需）。 |
| Bot token 被撤销或无效 | 通过 BotFather 使用 `/revoke` 然后 `/newbot` 或 `/token` 生成新 token。更新你的 `.env` 文件。 |
| Webhook 未收到更新 | 验证 `TELEGRAM_WEBHOOK_URL` 是否可从公网访问（使用 `curl` 测试）。确保你的平台/反向代理将来自该 URL 端口的入站 HTTPS 流量路由到 `TELEGRAM_WEBHOOK_PORT` 配置的本地监听端口（两者端口号无需一致）。确保 SSL/TLS 已启用——Telegram 仅向 HTTPS URL 发送数据。检查防火墙规则。 |

## 执行审批

当 Agent 尝试运行潜在的危险命令时，它会在聊天中请求你的审批：

> ⚠️ 此命令具有潜在危险（递归删除）。回复 "yes" 以批准。

回复 "yes"/"y" 表示批准，或回复 "no"/"n" 表示拒绝。

## 安全性

:::warning
请务必设置 `TELEGRAM_ALLOWED_USERS` 以限制谁可以与你的 Bot 交互。作为安全措施，如果不设置，网关默认会拒绝所有用户。
:::

切勿公开分享你的 Bot token。如果 token 泄露，请立即通过 BotFather 的 `/revoke` 命令将其撤销。

更多详细信息，请参阅 [安全文档](/user-guide/security)。你也可以使用 [私聊配对 (DM pairing)](/user-guide/messaging#dm-pairing-alternative-to-allowlists) 来实现更灵活的用户授权方式。
