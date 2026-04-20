---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

<a id="telegram-setup"></a>
# Telegram 设置

Hermes Agent 可以作为功能齐全的对话机器人集成到 Telegram。连接后，你可以从任何设备与你的 Agent 聊天、发送会自动转录的语音备忘录、接收定时任务结果，并在群聊中使用该 Agent。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/)，支持文本、语音、图片和文件附件。

<a id="step-1-create-a-bot-via-botfather"></a>
## 步骤 1：通过 BotFather 创建机器人

每个 Telegram 机器人都需要一个由 Telegram 官方机器人管理工具 [@BotFather](https://t.me/BotFather) 颁发的 API 令牌。

1.  打开 Telegram 并搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2.  发送 `/newbot`
3.  选择一个**显示名称**（例如，“Hermes Agent”）—— 可以是任何名称
4.  选择一个**用户名** —— 必须是唯一的且以 `bot` 结尾（例如，`my_hermes_bot`）
5.  BotFather 会回复你的 **API 令牌**。它看起来像这样：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请保管好你的机器人令牌。任何拥有此令牌的人都可以控制你的机器人。如果令牌泄露，请立即通过 BotFather 中的 `/revoke` 命令撤销它。
:::

<a id="step-2-customize-your-bot-optional"></a>
## 步骤 2：自定义你的机器人（可选）

这些 BotFather 命令可以改善用户体验。给 @BotFather 发消息并使用：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始聊天前显示的“这个机器人能做什么？”文本 |
| `/setabouttext` | 机器人个人资料页面上的简短文本 |
| `/setuserpic` | 为你的机器人上传头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否能看到所有群组消息（见步骤 3） |

:::tip
对于 `/setcommands`，一个有用的初始命令集：

```
help - 显示帮助信息
new - 开始新的对话
sethome - 将此聊天设置为主频道
```
:::

<a id="step-3-privacy-mode-critical-for-groups"></a>
## 步骤 3：隐私模式（对群组至关重要） {#step-3-privacy-mode-critical-for-groups}

Telegram 机器人有一个**隐私模式**，该模式**默认启用**。这是在群组中使用机器人时最常见的困惑来源。

**当隐私模式开启时**，你的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自己消息的回复
- 服务消息（成员加入/离开、置顶消息等）
- 机器人作为管理员的频道中的消息

**当隐私模式关闭时**，机器人会接收群组中的每一条消息。

<a id="how-to-disable-privacy-mode"></a>
### 如何禁用隐私模式

1.  给 **@BotFather** 发消息
2.  发送 `/mybots`
3.  选择你的机器人
4.  进入 **Bot Settings → Group Privacy → Turn off**

:::warning
**更改隐私设置后，你必须将机器人从任何群组中移除并重新添加。** Telegram 在机器人加入群组时会缓存隐私状态，除非移除并重新添加机器人，否则该状态不会更新。
:::
:::tip
另一种关闭隐私模式的方法：将机器人提升为**群组管理员**。管理员机器人无论隐私设置如何，都会收到所有消息，这样就无需切换全局隐私模式。
:::

<a id="step-4-find-your-user-id"></a>
## 步骤 4：查找您的用户 ID

Hermes Agent 使用数字形式的 Telegram 用户 ID 来控制访问权限。您的用户 ID **不是**您的用户名——它是一个像 `123456789` 这样的数字。

**方法 1（推荐）：** 给 [@userinfobot](https://t.me/userinfobot) 发消息——它会立即回复您的用户 ID。

**方法 2：** 给 [@get_id_bot](https://t.me/get_id_bot) 发消息——这是另一个可靠的选择。

保存这个数字；下一步您会用到它。

<a id="step-5-configure-hermes"></a>
## 步骤 5：配置 Hermes

<a id="option-a-interactive-setup-recommended"></a>
### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

出现提示时选择 **Telegram**。向导会询问您的机器人令牌和允许的用户 ID，然后为您写入配置。

<a id="option-b-manual-configuration"></a>
### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env` 文件中：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # 多个用户用逗号分隔
```

<a id="start-the-gateway"></a>
### 启动网关

```bash
hermes gateway
```

机器人应该在几秒钟内上线。在 Telegram 上给它发条消息来验证一下。

<a id="sending-generated-files-from-docker-backed-terminals"></a>
## 从基于 Docker 的终端发送生成的文件

如果您的终端后端是 `docker`，请注意 Telegram 附件是由**网关进程**发送的，而不是从容器内部发送的。这意味着最终的 `MEDIA:/...` 路径必须在运行网关的主机上可读。

常见的陷阱：

- Agent 在 Docker 内部将文件写入 `/workspace/report.txt`
- 模型发出 `MEDIA:/workspace/report.txt`
- Telegram 发送失败，因为 `/workspace/report.txt` 只存在于容器内部，而不在主机上

推荐的做法：

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/.hermes/cache/documents:/output"
```

然后：

- 在 Docker 内部将文件写入 `/output/...`
- 在 `MEDIA:` 中发出**主机可见**的路径，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`

如果您已经有一个 `docker_volumes:` 部分，请将新的挂载添加到同一个列表中。YAML 中的重复键会静默覆盖较早的键。

<a id="webhook-mode"></a>
## Webhook 模式

默认情况下，Hermes 使用**长轮询**连接到 Telegram——网关向 Telegram 的服务器发出出站请求来获取新更新。这对于本地和持续在线的部署效果很好。

对于**云部署**（Fly.io、Railway、Render 等），**Webhook 模式**更具成本效益。这些平台可以在入站 HTTP 流量时自动唤醒挂起的机器，但无法在出站连接时唤醒。由于轮询是出站的，一个轮询机器人永远无法休眠。Webhook 模式翻转了方向——Telegram 将更新推送到您机器人的 HTTPS URL，从而实现了空闲时休眠的部署方式。
| | 轮询（默认） | Webhook |
|---|---|---|
| 方向 | Gateway → Telegram（出站） | Telegram → Gateway（入站） |
| 最佳适用场景 | 本地、常开服务器 | 具有自动唤醒功能的云平台 |
| 配置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲成本 | 机器必须保持运行 | 机器可以在消息间隔期间休眠 |

<a id="configuration"></a>
### 配置

将以下内容添加到 `~/.hermes/.env` 文件中：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认 8443
# TELEGRAM_WEBHOOK_SECRET=mysecret  # 可选，建议设置
```

| 变量 | 必填 | 描述 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 发送更新信息的公共 HTTPS URL。URL 路径会自动提取（例如，从上面的示例中提取 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | Webhook 服务器监听的本地端口（默认：`8443`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | 否 | 用于验证更新信息是否确实来自 Telegram 的密钥令牌。**强烈建议**在生产部署中使用。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关会启动 HTTP webhook 服务器而不是轮询。当未设置时，则使用轮询模式 — 与先前版本的行为保持一致。

<a id="cloud-deployment-example-fly-io"></a>
### 云部署示例 (Fly.io)

1. 将环境变量添加到你的 Fly.io 应用密钥中：

```bash
fly secrets set TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
fly secrets set TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)
```

2. 在你的 `fly.toml` 中暴露 webhook 端口：

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

网关日志应该显示：`[telegram] Connected to Telegram (webhook mode)`。

<a id="proxy-support"></a>
## 代理支持

如果 Telegram 的 API 被屏蔽或者你需要通过代理路由流量，请设置 Telegram 专用的代理 URL。这会优先于通用的 `HTTPS_PROXY` / `HTTP_PROXY` 环境变量。

**选项 1: config.yaml（推荐）**

```yaml
telegram:
  proxy_url: "socks5://127.0.0.1:1080"
```

**选项 2: 环境变量**

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:1080
```

支持的协议：`http://`, `https://`, `socks5://`。

该代理同时应用于主要的 Telegram 连接和备用的 IP 传输。如果没有设置 Telegram 专用的代理，网关会回退使用 `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY`（或 macOS 系统代理自动检测）。

<a id="home-channel"></a>
## 主频道

在任何 Telegram 聊天（私聊或群组）中使用 `/sethome` 命令，将其指定为**主频道**。定时任务（cron 作业）会将结果发送到这个频道。
你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="我的笔记"
```

:::tip
群组聊天 ID 是负数（例如 `-1001234567890`）。你个人私聊的聊天 ID 则与你的用户 ID 相同。
:::

<a id="voice-messages"></a>
## 语音消息

<a id="incoming-voice-speech-to-text"></a>
### 接收语音（语音转文字）

你在 Telegram 上发送的语音消息会被 Hermes 配置的 STT 提供商自动转录，并以文本形式注入到对话中。

- `local` 使用运行 Hermes 的机器上的 `faster-whisper` —— 无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

<a id="outgoing-voice-text-to-speech"></a>
### 发送语音（文字转语音）

当 Agent 通过 TTS 生成音频时，它会以 Telegram 原生的**语音气泡**形式发送 —— 即那种圆形的、可内联播放的格式。

- **OpenAI 和 ElevenLabs** 原生生成 Opus 格式 —— 无需额外设置
- **Edge TTS**（默认的免费提供商）输出 MP3，需要 **ffmpeg** 来转换为 Opus：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

如果没有安装 ffmpeg，Edge TTS 生成的音频会作为普通音频文件发送（仍然可以播放，但使用的是矩形播放器，而不是语音气泡）。

你可以在 `config.yaml` 文件的 `tts.provider` 键下配置 TTS 提供商。

<a id="group-chat-usage"></a>
## 群组聊天使用

Hermes Agent 可以在 Telegram 群组聊天中工作，但需要注意以下几点：

- **隐私模式**决定了机器人能看到哪些消息（参见[步骤 3](#step-3-privacy-mode-critical-for-groups)）
- `TELEGRAM_ALLOWED_USERS` 仍然适用 —— 即使在群组中，也只有授权用户才能触发机器人
- 你可以通过设置 `telegram.require_mention: true` 来防止机器人响应普通的群聊消息
- 当 `telegram.require_mention: true` 时，群组消息在以下情况下会被接受：
  - 斜杠命令
  - 回复机器人消息
  - `@机器人用户名` 提及
  - 匹配你在 `telegram.mention_patterns` 中配置的正则表达式唤醒词
- 使用 `telegram.ignored_threads` 可以让 Hermes 在特定的 Telegram 论坛主题中保持静默，即使该群组在其他情况下允许自由响应或提及触发回复
- 如果 `telegram.require_mention` 未设置或为 false，Hermes 将保持之前的开放群组行为，并响应它能看到的普通群组消息

<a id="example-group-trigger-configuration"></a>
### 群组触发配置示例

将以下内容添加到 `~/.hermes/config.yaml`：

```yaml
telegram:
  require_mention: true
  mention_patterns:
    - "^\\s*chompy\\b"
  ignored_threads:
    - 31
    - "42"
```
这个示例允许所有常见的直接触发方式，以及以 `chompy` 开头的消息，即使它们没有使用 `@mention`。
在提及和自由回复检查运行之前，Telegram 话题 `31` 和 `42` 中的消息总是被忽略。

<a id="notes-on-mentionpatterns"></a>
### 关于 `mention_patterns` 的说明

- 模式使用 Python 正则表达式
- 匹配不区分大小写
- 模式会同时检查文本消息和媒体说明文字
- 无效的正则表达式模式会被忽略，并在网关日志中给出警告，而不是导致机器人崩溃
- 如果你希望一个模式仅在消息开头匹配，请使用 `^` 锚定

<a id="private-chat-topics-bot-api-9-4"></a>
## 私聊话题 (Bot API 9.4) {#private-chat-topics-bot-api-94}

Telegram Bot API 9.4 (2026年2月) 引入了**私聊话题** —— 机器人可以直接在 1 对 1 的私信聊天中创建论坛风格的话题线程，无需超级群组。这让你可以在与 Hermes 的现有私信中运行多个独立的工作空间。

<a id="use-case"></a>
### 使用场景

如果你同时处理多个长期项目，话题可以将它们的上下文分开：

- **话题 "网站"** —— 处理你的生产环境 Web 服务
- **话题 "研究"** —— 文献综述和论文探索
- **话题 "通用"** —— 杂项任务和快速问题

每个话题都有自己的对话会话、历史记录和上下文 —— 与其他话题完全隔离。

<a id="configuration"></a>
### 配置

在 `~/.hermes/config.yaml` 文件的 `platforms.telegram.extra.dm_topics` 下添加话题：

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
          skill: arxiv              # 在此话题中自动加载一个技能
```

**字段说明：**

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 话题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码 (整数) |
| `icon_custom_emoji_id` | 否 | 话题图标的自定义表情符号 ID |
| `skill` | 否 | 在此话题的新会话中自动加载的技能 |
| `thread_id` | 否 | 话题创建后自动填充 —— 不要手动设置 |

<a id="how-it-works"></a>
### 工作原理

1. 网关启动时，Hermes 会为每个尚未分配 `thread_id` 的话题调用 `createForumTopic`
2. `thread_id` 会自动保存回 `config.yaml` —— 后续重启将跳过 API 调用
3. 每个话题映射到一个独立的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4. 每个话题中的消息都有自己的对话历史记录、内存刷新和上下文窗口
<a id="skill-binding"></a>
### 技能绑定

带有 `skill` 字段的主题会在该主题中启动新会话时自动加载该技能。其效果与在对话开始时输入 `/技能名称` 完全一样 —— 技能内容会被注入到第一条消息中，后续消息会在对话历史中看到它。

例如，一个设置了 `skill: arxiv` 的主题，每当其会话重置时（由于空闲超时、每日重置或手动执行 `/reset`），都会预加载 arxiv 技能。

:::tip
在配置之外创建的主题（例如，通过手动调用 Telegram API）会在收到 `forum_topic_created` 服务消息时被自动发现。你也可以在网关运行时将主题添加到配置中 —— 它们会在下一次缓存未命中时被拾取。
:::

<a id="group-forum-topic-skill-binding"></a>
## 群组论坛主题技能绑定

启用了**主题模式**（也称为“论坛主题”）的超级群组已经实现了每个主题的会话隔离 —— 每个 `thread_id` 都映射到其自己的对话。但你可能希望在特定群组主题中收到消息时**自动加载一个技能**，就像私聊主题技能绑定的工作方式一样。

<a id="use-case"></a>
### 使用场景

一个为不同工作流设置了论坛主题的团队超级群组：

- **工程**主题 → 自动加载 `software-development` 技能
- **研究**主题 → 自动加载 `arxiv` 技能
- **通用**主题 → 无技能，通用助手

<a id="configuration"></a>
### 配置

在 `~/.hermes/config.yaml` 中的 `platforms.telegram.extra.group_topics` 下添加主题绑定：

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
          # No skill — general purpose
```

**字段说明：**

| 字段 | 是否必需 | 描述 |
|-------|----------|-------------|
| `chat_id` | 是 | 超级群组的数字 ID（以 `-100` 开头的负数） |
| `name` | 否 | 主题的可读标签（仅用于信息展示） |
| `thread_id` | 是 | Telegram 论坛主题 ID —— 在 `t.me/c/&lt;group_id&gt;/&lt;thread_id&gt;` 链接中可见 |
| `skill` | 否 | 在此主题的新会话中自动加载的技能 |

<a id="how-it-works"></a>
### 工作原理

1.  当消息到达已映射的群组主题时，Hermes 会在 `group_topics` 配置中查找 `chat_id` 和 `thread_id`
2.  如果匹配的条目有 `skill` 字段，则该技能会为该会话自动加载 —— 与私聊主题技能绑定完全相同
3.  没有 `skill` 键的主题仅获得会话隔离（现有行为，保持不变）
4.  未映射的 `thread_id` 值或 `chat_id` 值会被静默忽略 —— 不报错，不加载技能
<a id="differences-from-dm-topics"></a>
### 与私聊话题的区别

| | 私聊话题 | 群组话题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 话题创建 | 如果缺少 `thread_id`，Hermes 会通过 API 创建话题 | 管理员在 Telegram 界面中创建话题 |
| `thread_id` | 创建后自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（管理员控制外观） |
| 技能绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛话题已内置此功能） |

:::tip
要查找话题的 `thread_id`，请在 Telegram Web 或桌面版中打开该话题，查看 URL：`https://t.me/c/1234567890/5` — 最后一个数字 (`5`) 就是 `thread_id`。超级群的 `chat_id` 是群组 ID 前加上 `-100`（例如，群组 `1234567890` 变为 `-1001234567890`）。
:::

<a id="recent-bot-api-features"></a>
## 近期 Bot API 功能

- **Bot API 9.4 (2026年2月):** 私聊话题 — 机器人可以通过 `createForumTopic` 在一对一私聊中创建论坛话题。请参阅上文的[私聊话题](#private-chat-topics-bot-api-94)。
- **隐私政策:** Telegram 现在要求机器人必须有隐私政策。通过 BotFather 使用 `/setprivacy_policy` 设置，或者 Telegram 可能会自动生成一个占位符。如果你的机器人是公开的，这一点尤其重要。
- **消息流式传输:** Bot API 9.x 增加了对长响应流式传输的支持，这可以改善 Agent 回复较长内容时的感知延迟。

<a id="interactive-model-picker"></a>
## 交互式模型选择器

当你在 Telegram 聊天中发送不带参数的 `/model` 命令时，Hermes 会显示一个交互式内联键盘，用于切换模型：

1.  **提供商选择** — 显示每个可用提供商的按钮，并附带模型数量（例如，“OpenAI (15)”，当前提供商会显示为“✓ Anthropic (12)”）。
2.  **模型选择** — 分页显示的模型列表，带有 **上一页**/**下一页** 导航、返回提供商的 **返回** 按钮以及 **取消** 按钮。

当前模型和提供商显示在顶部。所有导航都是通过原地编辑同一条消息完成的（不会弄乱聊天记录）。

:::tip
如果你知道确切的模型名称，可以直接输入 `/model <名称>` 来跳过选择器。你也可以输入 `/model <名称> --global` 来使更改在所有会话中持久生效。
:::

<a id="dns-over-https-fallback-ips"></a>
## DNS-over-HTTPS 备用 IP

在某些受限网络中，`api.telegram.org` 可能解析到一个无法访问的 IP 地址。Telegram 适配器包含一个**备用 IP** 机制，该机制会透明地尝试连接到备用 IP，同时保留正确的 TLS 主机名和 SNI。

<a id="how-it-works"></a>
### 工作原理

1.  如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2.  否则，适配器会自动通过 DNS-over-HTTPS (DoH) 查询 **Google DNS** 和 **Cloudflare DNS**，以发现 `api.telegram.org` 的备用 IP。
3.  DoH 返回的、与系统 DNS 结果不同的 IP 将被用作备用 IP。
4.  如果 DoH 也被屏蔽，则使用一个硬编码的种子 IP (`149.154.167.220`) 作为最后手段。
5.  一旦某个备用 IP 连接成功，它就会变得“粘性” — 后续请求将直接使用它，而无需先重试主路径。
<a id="configuration"></a>
### 配置

```bash
# 显式指定备用 IP（逗号分隔）
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
通常你不需要手动配置这个。通过 DoH 的自动发现机制能处理大多数受限制网络的情况。只有在你的网络连 DoH 也被屏蔽时，才需要设置 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::

<a id="proxy-support"></a>
## 代理支持

如果你的网络需要通过 HTTP 代理才能访问互联网（在企业环境中很常见），Telegram 适配器会自动读取标准的代理环境变量，并通过该代理路由所有连接。

<a id="supported-variables"></a>
### 支持的变量

适配器按顺序检查以下环境变量，并使用第一个被设置的变量：

1. `HTTPS_PROXY`
2. `HTTP_PROXY`
3. `ALL_PROXY`
4. `https_proxy` / `http_proxy` / `all_proxy`（小写变体）

### 配置

在启动网关前，在你的环境中设置代理：

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

或者将其添加到 `~/.hermes/.env` 文件中：

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

该代理同时应用于主传输层和所有备用 IP 传输层。无需额外的 Hermes 配置——只要设置了环境变量，就会自动使用。

:::note
这涵盖了 Hermes 为 Telegram 连接使用的自定义备用传输层。其他地方使用的标准 `httpx` 客户端本身就已支持代理环境变量。
:::

<a id="message-reactions"></a>
## 消息回应

机器人可以为消息添加表情符号回应，作为视觉上的处理反馈：

- 👀 当机器人开始处理你的消息时
- ✅ 当响应成功送达时
- ❌ 如果在处理过程中发生错误

回应功能**默认是禁用的**。在 `config.yaml` 中启用它：

```yaml
telegram:
  reactions: true
```

或者通过环境变量启用：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（回应是叠加的）不同，Telegram 的 Bot API 在一次调用中会替换机器人的所有回应。从 👀 到 ✅/❌ 的转换是原子性的——你不会同时看到两个。
:::

:::tip
如果机器人在群组中没有添加回应的权限，回应调用会静默失败，消息处理会正常继续。
:::

<a id="per-channel-prompts"></a>
## 按频道提示

为特定的 Telegram 群组或论坛主题分配临时的系统提示。该提示在每次对话轮次运行时被注入——永远不会保存到对话历史记录中——因此更改会立即生效。
```yaml
telegram:
  channel_prompts:
    "-1001234567890": |
      你是一个研究助手。专注于学术来源、引用和简洁的综述。
    "42":  |
      本主题用于创意写作反馈。请保持热情并提供建设性意见。
```

键是聊天 ID（群组/超级群组）或论坛主题 ID。对于论坛群组，主题级别的提示会覆盖群组级别的提示：

- 在群组 `-1001234567890` 内的主题 `42` 中发送消息 → 使用主题 `42` 的提示
- 在主题 `99`（没有明确条目）中发送消息 → 回退到群组 `-1001234567890` 的提示
- 在没有条目的群组中发送消息 → 不应用任何频道提示

数字类型的 YAML 键会自动规范化为字符串。

<a id="troubleshooting"></a>
## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| Bot 完全不响应 | 验证 `TELEGRAM_BOT_TOKEN` 是否正确。检查 `hermes gateway` 日志中的错误。 |
| Bot 响应“未授权” | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 列表中。请使用 @userinfobot 仔细核对。 |
| Bot 忽略群组消息 | 隐私模式可能已开启。请禁用它（步骤 3）或将 bot 设为群组管理员。**注意：更改隐私设置后，需要移除并重新添加 bot。** |
| 语音消息未转录 | 验证 STT 是否可用：安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件，不是气泡 | 安装 `ffmpeg`（Edge TTS Opus 转换所需）。 |
| Bot token 被撤销/无效 | 通过 BotFather 的 `/revoke` 然后 `/newbot` 或 `/token` 命令生成新 token。更新你的 `.env` 文件。 |
| Webhook 未接收更新 | 验证 `TELEGRAM_WEBHOOK_URL` 是否可公开访问（用 `curl` 测试）。确保你的平台/反向代理将来自该 URL 端口的入站 HTTPS 流量路由到 `TELEGRAM_WEBHOOK_PORT` 配置的本地监听端口（这两个端口号不必相同）。确保 SSL/TLS 处于活动状态——Telegram 只向 HTTPS URL 发送数据。检查防火墙规则。 |

<a id="exec-approval"></a>
## 执行批准

当 Agent 尝试运行一个可能危险的命令时，它会在聊天中向你请求批准：

> ⚠️ 此命令可能具有危险性（递归删除）。回复 "yes" 以批准。

回复 "yes"/"y" 批准，或回复 "no"/"n" 拒绝。

<a id="security"></a>
## 安全

:::warning
务必设置 `TELEGRAM_ALLOWED_USERS` 以限制可以与你的 bot 交互的人员。如果不设置，网关作为安全措施会默认拒绝所有用户。
:::

切勿公开分享你的 bot token。如果 token 泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。
更多细节，请参阅[安全文档](/user-guide/security)。你也可以使用[私信配对](/user-guide/messaging#dm-pairing-alternative-to-allowlists)来实现更动态的用户授权方式。
