---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

# Telegram 设置 {#telegram-setup}

Hermes Agent 与 Telegram 集成，作为一个功能完整的对话机器人。连接后，你可以从任何设备与你的 Agent 聊天，发送自动转写的语音备忘录，接收定时任务结果，并在群聊中使用 Agent。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/)，支持文本、语音、图片和文件附件。

## 第一步：通过 BotFather 创建机器人 {#step-1-create-a-bot-via-botfather}

每个 Telegram 机器人都需要由 Telegram 官方机器人管理工具 [@BotFather](https://t.me/BotFather) 颁发的 API 令牌。

1. 打开 Telegram，搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 选择一个**显示名称**（例如 "Hermes Agent"）—— 可以是任意内容
4. 选择一个**用户名** —— 必须唯一且以 `bot` 结尾（例如 `my_hermes_bot`）
5. BotFather 会回复你的 **API 令牌**。它看起来像这样：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请保管好你的机器人令牌。任何拥有此令牌的人都可以控制你的机器人。如果泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。
:::

## 第二步：自定义你的机器人（可选） {#step-2-customize-your-bot-optional}

以下 BotFather 命令可以改善用户体验。向 @BotFather 发送消息并使用：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始聊天前显示的“这个机器人能做什么？”文本 |
| `/setabouttext` | 机器人个人资料页面上的简短介绍 |
| `/setuserpic` | 为你的机器人上传头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否能看到所有群消息（参见第三步） |

:::tip
对于 `/setcommands`，一个有用的初始命令集：

```
help - 显示帮助信息
new - 开始新对话
sethome - 将此聊天设置为默认频道
```
:::

## 第三步：隐私模式（群聊中至关重要） {#step-3-privacy-mode-critical-for-groups}

Telegram 机器人有一个**隐私模式**，**默认开启**。这是在群聊中使用机器人时最常见的困惑来源。

**隐私模式开启时**，你的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自己消息的回复
- 服务消息（成员加入/离开、置顶消息等）
- 机器人是管理员的频道中的消息

**隐私模式关闭时**，机器人会收到群聊中的每一条消息。

### 如何关闭隐私模式 {#how-to-disable-privacy-mode}

1. 向 **@BotFather** 发送消息
2. 发送 `/mybots`
3. 选择你的机器人
4. 进入 **Bot Settings → Group Privacy → Turn off**

:::warning
**更改隐私设置后，你必须将机器人从群聊中移除并重新添加**。Telegram 会在机器人加入群聊时缓存隐私状态，除非移除并重新添加机器人，否则不会更新。
:::

:::tip
关闭隐私模式的另一种方法：将机器人提升为**群管理员**。管理员机器人无论隐私设置如何，始终接收所有消息，这样就不需要切换全局隐私模式。
:::

## 第四步：找到你的用户 ID {#step-4-find-your-user-id}

Hermes Agent 使用数字形式的 Telegram 用户 ID 来控制访问权限。你的用户 ID **不是**你的用户名——它是一个像 `123456789` 这样的数字。
**方法 1（推荐）：** 给 [@userinfobot](https://t.me/userinfobot) 发消息 — 它会立即回复你的用户 ID。

**方法 2：** 给 [@get_id_bot](https://t.me/get_id_bot) 发消息 — 另一个可靠的选择。

保存好这个数字；下一步你会用到它。

## 第 5 步：配置 Hermes {#step-5-configure-hermes}

### 选项 A：交互式设置（推荐） {#option-a-interactive-setup-recommended}

```bash
hermes gateway setup
```

在提示时选择 **Telegram**。向导会询问你的机器人令牌和允许的用户 ID，然后为你写入配置。

### 选项 B：手动配置 {#option-b-manual-configuration}

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # 多个用户用逗号分隔
```

### 启动网关 {#start-the-gateway}

```bash
hermes gateway
```

机器人应该在几秒钟内上线。在 Telegram 上给它发一条消息来验证。

## 从 Docker 后端终端发送生成的文件 {#sending-generated-files-from-docker-backed-terminals}

如果你的终端后端是 `docker`，请记住 Telegram 附件是由 **网关进程** 发送的，而不是从容器内部发送的。这意味着最终的 `MEDIA:/...` 路径必须在运行网关的主机上可读。

常见陷阱：

- Agent 在 Docker 内部将文件写入 `/workspace/report.txt`
- 模型输出 `MEDIA:/workspace/report.txt`
- Telegram 发送失败，因为 `/workspace/report.txt` 只存在于容器内部，而不存在于主机上

推荐模式：

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/.hermes/cache/documents:/output"
```

然后：

- 在 Docker 内部将文件写入 `/output/...`
- 在 `MEDIA:` 中输出 **主机可见** 的路径，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`

如果你已经有 `docker_volumes:` 部分，将新的挂载添加到同一个列表中。YAML 重复键会静默覆盖前面的键。

### 支持的 `MEDIA:` 文件扩展名 {#supported-media-file-extensions}

网关从 Agent 回复中提取 `MEDIA:/path/to/file` 标签，并将引用的文件作为平台原生附件发送。所有网关平台支持的扩展名：

| 类别 | 扩展名 |
|---|---|
| 图片 | `png`, `jpg`, `jpeg`, `gif`, `webp`, `bmp`, `tiff`, `svg` |
| 音频 | `mp3`, `wav`, `ogg`, `m4a`, `opus`, `flac`, `aac` |
| 视频 | `mp4`, `mov`, `webm`, `mkv`, `avi` |
| **文档** | `pdf`, `txt`, `md`, `csv`, `json`, `xml`, `html`, `yaml`, `yml`, `log` |
| **办公文件** | `docx`, `xlsx`, `pptx`, `odt`, `ods`, `odp` |
| **压缩包** | `zip`, `rar`, `7z`, `tar`, `gz`, `bz2` |
| **电子书 / 安装包** | `epub`, `apk`, `ipa` |

此列表中的任何内容都会在支持它的平台（Telegram、Discord、Signal、Slack、WhatsApp、飞书、Matrix 等）上作为原生附件发送；在不支持原生附件的平台上，它会回退为链接或纯文本指示。**加粗** 的类别是在最近几个版本中添加的——如果你之前依赖模型说 `here is the file: /path/to/report.docx` 这种方式，请改用 `MEDIA:/path/to/report.docx` 以实现原生发送。

## Webhook 模式 {#webhook-mode}
默认情况下，Hermes 使用 **长轮询** 连接 Telegram —— 网关向 Telegram 服务器发起出站请求以获取新更新。这种方式适用于本地和常驻部署。

对于 **云部署**（Fly.io、Railway、Render 等），**Webhook 模式** 更具成本效益。这些平台可以在入站 HTTP 流量到达时自动唤醒已休眠的机器，但无法通过出站连接唤醒。由于轮询是出站行为，轮询机器人永远无法休眠。Webhook 模式反转了方向 —— Telegram 将更新推送到你的机器人 HTTPS URL，从而实现空闲时休眠的部署。

| | 轮询（默认） | Webhook |
|---|---|---|
| 方向 | 网关 → Telegram（出站） | Telegram → 网关（入站） |
| 最佳场景 | 本地、常驻服务器 | 支持自动唤醒的云平台 |
| 配置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲成本 | 机器必须保持运行 | 机器可在消息间隔休眠 |

### 配置 {#configuration}

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
TELEGRAM_WEBHOOK_SECRET="$(openssl rand -hex 32)"  # 必填
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认 8443
```

| 变量 | 是否必填 | 说明 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 将向其发送更新的公共 HTTPS URL。URL 路径会被自动提取（例如，从上面的示例中提取 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | **是**（当设置了 `TELEGRAM_WEBHOOK_URL` 时） | 用于验证的密钥令牌，Telegram 会在每个 webhook 请求中回传该令牌。没有它网关将拒绝启动 —— 参见 [GHSA-3vpc-7q5r-276h](https://github.com/NousResearch/hermes-agent/security/advisories/GHSA-3vpc-7q5r-276h)。使用 `openssl rand -hex 32` 生成。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | Webhook 服务器监听的本地端口（默认：`8443`）。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关会启动一个 HTTP webhook 服务器，而不是使用轮询。未设置时，则使用轮询模式 —— 行为与之前版本相同。

### 云部署示例（Fly.io） {#cloud-deployment-example-fly-io}

1. 将环境变量添加到你的 Fly.io 应用密钥中：

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

## 代理支持 {#proxy-support}

如果 Telegram 的 API 被屏蔽，或者你需要通过代理路由流量，可以设置一个 Telegram 专用的代理 URL。该设置优先级高于通用的 `HTTPS_PROXY` / `HTTP_PROXY` 环境变量。

**选项 1：config.yaml（推荐）**

```yaml
telegram:
  proxy_url: "socks5://127.0.0.1:1080"
```

**选项 2：环境变量**

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:1080
```

支持的协议：`http://`、`https://`、`socks5://`。
该代理同时适用于主 Telegram 连接和备用 IP 传输。如果未设置 Telegram 专属代理，网关会回退到 `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY`（或 macOS 系统代理自动检测）。

## 主频道 {#home-channel}

在任意 Telegram 聊天（私聊或群聊）中使用 `/sethome` 命令，将其指定为**主频道**。定时任务（cron 作业）的结果会发送到此频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="My Notes"
```

:::tip
群聊 ID 是负数（例如 `-1001234567890`）。你的个人私聊 ID 与你的用户 ID 相同。
:::

## 语音消息 {#voice-messages}

### 接收语音（语音转文字） {#incoming-voice-speech-to-text}

你在 Telegram 上发送的语音消息会被 Hermes 配置的 STT 提供程序自动转录，并以文本形式注入对话中。

- `local` 使用运行 Hermes 的机器上的 `faster-whisper` — 无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

### 发送语音（文字转语音） {#outgoing-voice-text-to-speech}

当 Agent 通过 TTS 生成音频时，会以原生 Telegram **语音气泡**（圆形、可内联播放的那种）形式发送。

- **OpenAI 和 ElevenLabs** 原生输出 Opus 格式 — 无需额外设置
- **Edge TTS**（默认免费提供程序）输出 MP3，需要 **ffmpeg** 转换为 Opus：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

如果没有 ffmpeg，Edge TTS 音频会作为普通音频文件发送（仍可播放，但会使用矩形播放器而非语音气泡）。

在 `config.yaml` 的 `tts.provider` 键下配置 TTS 提供程序。

## 群聊使用 {#group-chat-usage}

Hermes Agent 在 Telegram 群聊中工作时需注意以下几点：

- **隐私模式**决定了机器人能看到哪些消息（参见[步骤 3](#step-3-privacy-mode-critical-for-groups)）
- `TELEGRAM_ALLOWED_USERS` 仍然适用 — 只有授权用户才能触发机器人，即使在群聊中也是如此
- 你可以通过 `telegram.require_mention: true` 让机器人不响应普通群聊消息
- 当 `telegram.require_mention: true` 时，以下群聊消息会被接受：
  - 斜杠命令
  - 对机器人某条消息的回复
  - `@botusername` 提及
  - 与 `telegram.mention_patterns` 中配置的正则唤醒词匹配的消息
- 使用 `telegram.ignored_threads` 让 Hermes 在特定的 Telegram 论坛主题中保持静默，即使该群聊允许自由回复或提及触发回复
- 如果 `telegram.require_mention` 未设置或为 false，Hermes 会保持之前的开放群聊行为，并响应它能看到的普通群聊消息

### 群聊触发配置示例 {#example-group-trigger-configuration}

将此内容添加到 `~/.hermes/config.yaml`：

```yaml
telegram:
  require_mention: true
  mention_patterns:
    - "^\\s*chompy\\b"
  ignored_threads:
    - 31
    - "42"
```

此示例允许所有常规的直接触发方式，以及以 `chompy` 开头的消息（即使没有使用 `@mention`）。
在提及和自由响应检查之前，Telegram 主题 `31` 和 `42` 中的消息始终被忽略。
### `mention_patterns` 的注意事项 {#notes-on-mentionpatterns}

- 模式使用 Python 正则表达式
- 匹配不区分大小写
- 模式会同时检查文本消息和媒体说明
- 无效的正则表达式模式会被忽略，并在网关日志中给出警告，而不会导致机器人崩溃
- 如果希望模式仅在消息开头匹配，请使用 `^` 进行锚定

<a id="private-chat-topics-bot-api-9-4"></a>
## 私聊话题（Bot API 9.4） {#private-chat-topics-bot-api-94}

Telegram Bot API 9.4（2026 年 2 月）引入了**私聊话题**——机器人可以直接在 1 对 1 私聊中创建论坛式话题线程，无需超级群组。这让你可以在与 Hermes 的现有私聊中运行多个独立的工作空间。

### 使用场景 {#use-case}

如果你同时处理多个长期项目，话题可以保持各自的上下文独立：

- **话题“网站”**——处理你的生产 Web 服务
- **话题“研究”**——文献综述和论文探索
- **话题“通用”**——杂项任务和快速提问

每个话题都有自己的对话会话、历史记录和上下文——完全与其他话题隔离。

### 配置 {#configuration}

:::caution 前提条件
在将话题添加到配置之前，用户必须**在机器人的私聊中启用话题模式**：
<a id="prerequisites"></a>

1. 在 Telegram 中打开与 Hermes 机器人的私聊
2. 点击顶部的机器人名称以打开聊天信息
3. 启用**话题**（将聊天转换为论坛的开关）

如果没有此操作，Hermes 将在启动时记录 `The chat is not a forum` 并跳过话题创建。这是 Telegram 客户端设置——机器人无法通过编程方式启用它。
:::

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
          skill: arxiv              # 在此话题中自动加载技能
```

**字段说明：**

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 话题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 话题图标的自定义表情符号 ID |
| `skill` | 否 | 在此话题的新会话中自动加载的技能 |
| `thread_id` | 否 | 话题创建后自动填充——请勿手动设置 |

### 工作原理 {#how-it-works}

1. 网关启动时，Hermes 为每个尚未拥有 `thread_id` 的话题调用 `createForumTopic`
2. `thread_id` 会自动保存回 `config.yaml`——后续重启会跳过 API 调用
3. 每个话题映射到一个独立的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4. 每个话题中的消息拥有自己的对话历史、内存刷新和上下文窗口

### 技能绑定 {#skill-binding}

带有 `skill` 字段的话题会在该话题中启动新会话时自动加载该技能。这完全等同于在对话开始时输入 `/skill-name`——技能内容会被注入到第一条消息中，后续消息会在对话历史中看到它。
例如，一个带有 `skill: arxiv` 的话题，在其会话重置时（由于空闲超时、每日重置或手动 `/reset`），会预加载 arxiv 技能。

:::tip
在配置之外创建的话题（例如通过手动调用 Telegram API），当收到 `forum_topic_created` 服务消息时会自动被发现。你也可以在网关运行时向配置中添加话题——它们会在下一次缓存未命中时被拾取。
:::

## 群组话题技能绑定 {#group-forum-topic-skill-binding}

启用了**话题模式**的超级群组（也称为“论坛话题”）已经为每个话题提供了会话隔离——每个 `thread_id` 对应一个独立的对话。但你可能希望当消息到达特定群组话题时**自动加载技能**，就像私聊话题技能绑定那样。

### 使用场景 {#use-case}

一个团队超级群组，为不同工作流设置了论坛话题：

- **工程**话题 → 自动加载 `software-development` 技能
- **研究**话题 → 自动加载 `arxiv` 技能
- **通用**话题 → 无技能，通用助手

<a id="configuration"></a>
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
          # 无技能 — 通用
```

**字段说明：**

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `chat_id` | 是 | 超级群组的数字 ID（以 `-100` 开头的负数） |
| `name` | 否 | 话题的人类可读标签（仅用于信息展示） |
| `thread_id` | 是 | Telegram 论坛话题 ID — 可在 `t.me/c/&lt;group_id&gt;/&lt;thread_id&gt;` 链接中看到 |
| `skill` | 否 | 在该话题的新会话中自动加载的技能 |

### 工作原理 {#how-it-works}

1. 当消息到达一个已映射的群组话题时，Hermes 会在 `group_topics` 配置中查找 `chat_id` 和 `thread_id`
2. 如果匹配的条目包含 `skill` 字段，该技能会自动加载到会话中——与私聊话题技能绑定相同
3. 没有 `skill` 键的话题仅获得会话隔离（已有行为，未改变）
4. 未映射的 `thread_id` 或 `chat_id` 值会静默忽略——不会报错，也不会加载技能

### 与私聊话题的区别 {#differences-from-dm-topics}

| | 私聊话题 | 群组话题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 话题创建 | Hermes 通过 API 创建话题（如果缺少 `thread_id`） | 管理员在 Telegram UI 中创建话题 |
| `thread_id` | 创建后自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（管理员控制外观） |
| 技能绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛话题已内置） |

:::tip
要找到话题的 `thread_id`，在 Telegram Web 或桌面版中打开该话题，查看 URL：`https://t.me/c/1234567890/5` — 最后一个数字（`5`）就是 `thread_id`。超级群组的 `chat_id` 是群组 ID 加上 `-100` 前缀（例如群组 `1234567890` 变为 `-1001234567890`）。
:::
## 近期 Bot API 特性 {#recent-bot-api-features}

- **Bot API 9.4（2026 年 2 月）：** 私聊话题——机器人可以通过 `createForumTopic` 在一对一私聊中创建论坛话题。详见上文 [私聊话题](#private-chat-topics-bot-api-94)。
- **隐私政策：** Telegram 现在要求机器人提供隐私政策。通过 BotFather 使用 `/setprivacy_policy` 设置，否则 Telegram 可能会自动生成占位符。如果你的机器人面向公众，这一点尤为重要。
- **消息流式输出：** Bot API 9.x 支持流式输出长回复，可以改善冗长 Agent 回复的感知延迟。

## 渲染：表格与链接预览 {#rendering-tables-and-link-previews}

Telegram 的 MarkdownV2 没有原生表格语法——管道表格如果直接传递，会显示为反斜杠转义的乱码。Hermes 会自动标准化 Markdown 表格：

- **小型表格**会被展平为**行分组列表**——每一行在列标题下变成可读的项目符号列表。适合 2-4 列且单元格内容简短的情况。
- **较大或较宽的表格**会回退到**围栏代码块**，列保持对齐，不会散乱。同时会添加一行简短的提示，让 Agent 知道在 Telegram 上更推荐用文字说明而非更多表格。

无需配置——适配器会根据每条消息自动选择合适的回退方式。如果你希望使用旧版“始终使用代码块”的行为，可以在 `config.yaml` 中设置 `telegram.pretty_tables: false` 来禁用表格标准化（默认值：`true`）。

**链接预览。** Telegram 会自动为机器人消息中的 URL 生成链接预览。如果你希望禁止这些预览（例如 `/tools` 输出过长、Agent 回复中提及十个链接等）：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_link_previews: true
```

启用后，Hermes 会在每条发出的消息中附加 Telegram 的 `LinkPreviewOptions(is_disabled=True)`，并在较旧的 `python-telegram-bot` 版本上回退到传统的 `disable_web_page_preview` 参数。

## 群组白名单 {#group-allowlisting}

Telegram 群组和论坛聊天有两个独立的开关可供配置：

- **发送者用户 ID**（`group_allow_from` / `TELEGRAM_GROUP_ALLOWED_USERS`）——仅应用于群组/论坛消息的发送者作用域白名单。当你希望特定用户能够在群组中调用机器人，但又不想将他们添加到 `TELEGRAM_ALLOWED_USERS`（那样也会赋予私聊权限）时，可使用此项。
- **聊天 ID**（`group_allowed_chats` / `TELEGRAM_GROUP_ALLOWED_CHATS`）——聊天作用域白名单。这些群组/论坛中的任何成员都可以与机器人交互。适用于团队/客服机器人等场景，其中群组成员身份本身就是访问信号。

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # 全局访问（私聊 + 群组）。在此列出的用户始终可以调用机器人。
        allow_from:
          - "123456789"
        # 仅在群组/论坛中允许的发送者 ID。不会授予私聊访问权限。
        group_allow_from:
          - "987654321"
        # 整个群组/论坛——任何成员都被授权。
        group_allowed_chats:
          - "-1001234567890"
```
对应的环境变量：

```bash
TELEGRAM_ALLOWED_USERS="123456789"
TELEGRAM_GROUP_ALLOWED_USERS="987654321"
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

行为说明：

- `TELEGRAM_ALLOWED_USERS` 适用于所有聊天类型（私聊、群组、论坛）。
- `TELEGRAM_GROUP_ALLOWED_USERS` 仅授权群组/论坛中列出的发送者。除非同时列在 `TELEGRAM_ALLOWED_USERS` 中，否则他们仍然无法向机器人发送私聊消息。
- 列在 `TELEGRAM_GROUP_ALLOWED_CHATS` 中的聊天，其所有成员都会被授权，无论发送者是谁。
- 在上述任意变量中使用 `*` 可允许任意发送者/聊天。
- 此机制叠加在现有的提及/模式触发规则以及 `group_topics` + `ignored_threads` 之上。

### 从 PR #17686 之前的版本迁移 {#migration-from-before-pr-17686}

在此拆分之前，`TELEGRAM_GROUP_ALLOWED_USERS` 是唯一的控制项，用户在其中填写的是**聊天 ID**。为了向后兼容，`TELEGRAM_GROUP_ALLOWED_USERS` 中形如聊天 ID（以 `-` 开头）的值仍会被当作聊天 ID 处理，并会记录一次弃用警告。迁移方式：

```bash
# 旧方式（仍可工作，但已弃用）
TELEGRAM_GROUP_ALLOWED_USERS="-1001234567890"

# 新方式
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

## 交互式模型选择器 {#interactive-model-picker}

当你在 Telegram 聊天中发送不带参数的 `/model` 时，Hermes 会显示一个交互式内联键盘，用于切换模型：

1. **提供商选择** — 显示每个可用提供商的按钮，并附带模型数量（例如，当前提供商会显示 "OpenAI (15)"、"✓ Anthropic (12)"）。
2. **模型选择** — 分页的模型列表，带有 **上一页**/**下一页** 导航、返回提供商的 **返回** 按钮，以及 **取消**。

当前模型和提供商显示在顶部。所有导航均通过原地编辑同一条消息完成（不会造成聊天混乱）。

:::tip
如果你知道确切的模型名称，直接输入 `/model <名称>` 即可跳过选择器。你也可以输入 `/model <名称> --global` 来跨会话持久化更改。
:::

## DNS-over-HTTPS 备用 IP {#dns-over-https-fallback-ips}

在某些受限网络中，`api.telegram.org` 可能解析到一个无法访问的 IP。Telegram 适配器包含一个**备用 IP** 机制，该机制会在保持正确 TLS 主机名和 SNI 的同时，透明地重试连接到备用 IP。

<a id="how-it-works"></a>
### 工作原理

1. 如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2. 否则，适配器会自动通过 DNS-over-HTTPS (DoH) 查询 **Google DNS** 和 **Cloudflare DNS**，以发现 `api.telegram.org` 的备用 IP。
3. DoH 返回的、与系统 DNS 结果不同的 IP 会被用作备用。
4. 如果 DoH 也被屏蔽，则最后会使用一个硬编码的种子 IP（`149.154.167.220`）。
5. 一旦某个备用 IP 连接成功，它就会成为“粘性”IP——后续请求会直接使用它，而不会先重试主路径。

<a id="configuration"></a>
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
通常你不需要手动配置。通过 DoH 的自动发现机制已经能处理大多数受限网络场景。只有当你的网络连 DoH 也被封锁时，才需要用到 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::

## 代理支持 {#proxy-support}

如果你的网络需要通过 HTTP 代理才能访问互联网（常见于企业环境），Telegram 适配器会自动读取标准的代理环境变量，并将所有连接通过该代理路由。

### 支持的变量 {#supported-variables}

适配器会按顺序检查以下环境变量，使用第一个被设置的变量：

1. `HTTPS_PROXY`
2. `HTTP_PROXY`
3. `ALL_PROXY`
4. `https_proxy` / `http_proxy` / `all_proxy`（小写变体）

<a id="configuration"></a>
### 配置

在启动网关之前，先在环境中设置代理：

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

或者将其添加到 `~/.hermes/.env` 中：

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

该代理同时适用于主传输通道和所有备用 IP 传输通道。无需额外的 Hermes 配置——只要设置了环境变量，就会自动使用。

:::note
这涵盖了 Hermes 用于 Telegram 连接的自定义备用传输层。其他地方使用的标准 `httpx` 客户端本身已经原生支持代理环境变量。
:::

## 消息反应 {#message-reactions}

机器人可以在消息上添加表情反应，作为视觉处理反馈：

- 👀 当机器人开始处理你的消息时
- ✅ 当响应成功送达时
- ❌ 如果处理过程中发生错误

反应**默认是禁用的**。在 `config.yaml` 中启用它们：

```yaml
telegram:
  reactions: true
```

或者通过环境变量：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（反应是累加的）不同，Telegram 的 Bot API 会在一次调用中替换所有机器人反应。从 👀 到 ✅/❌ 的切换是原子性的——你不会同时看到两者。
:::

:::tip
如果机器人没有在群组中添加反应的权限，反应调用会静默失败，消息处理会正常继续。
:::

## 按频道提示词 {#per-channel-prompts}

为特定的 Telegram 群组或论坛主题分配临时系统提示词。该提示词在每次对话时运行时注入——不会持久化到对话记录中——因此更改会立即生效。

```yaml
telegram:
  channel_prompts:
    "-1001234567890": |
      你是一名研究助手。专注于学术来源、
      引用和简洁的总结。
    "42":  |
      此主题用于创意写作反馈。请保持温暖和
      建设性。
```

键是聊天 ID（群组/超级群组）或论坛主题 ID。对于论坛群组，主题级别的提示词会覆盖群组级别的提示词：

- 在群组 `-1001234567890` 内的主题 `42` 中发送消息 → 使用主题 `42` 的提示词
- 在主题 `99` 中发送消息（没有显式条目）→ 回退到群组 `-1001234567890` 的提示词
- 在没有条目的群组中发送消息 → 不应用频道提示词

数字类型的 YAML 键会自动规范化为字符串。
## 故障排除 {#troubleshooting}

| 问题 | 解决方案 |
|------|----------|
| Bot 完全没有响应 | 确认 `TELEGRAM_BOT_TOKEN` 正确。检查 `hermes gateway` 日志中的错误。 |
| Bot 回复“未授权” | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。用 @userinfobot 再次确认。 |
| Bot 忽略群聊消息 | 隐私模式可能已开启。关闭它（步骤 3）或让 bot 成为群管理员。**更改隐私设置后，请务必移除并重新添加 bot。** |
| 语音消息未转写 | 确认 STT 可用：安装 `faster-whisper` 进行本地转写，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件而非气泡 | 安装 `ffmpeg`（Edge TTS Opus 转换需要）。 |
| Bot token 被撤销/无效 | 在 BotFather 中通过 `/revoke` 然后 `/newbot` 或 `/token` 生成新 token。更新你的 `.env` 文件。 |
| Webhook 未收到更新 | 确认 `TELEGRAM_WEBHOOK_URL` 可公开访问（用 `curl` 测试）。确保你的平台/反向代理将来自该 URL 端口的入站 HTTPS 流量路由到 `TELEGRAM_WEBHOOK_PORT` 配置的本地监听端口（两者端口号不必相同）。确保 SSL/TLS 已启用——Telegram 只向 HTTPS URL 发送请求。检查防火墙规则。 |

## 执行审批 {#exec-approval}

当 Agent 尝试运行可能危险的命令时，它会在聊天中向你请求批准：

> ⚠️ 此命令具有潜在危险（递归删除）。回复“yes”以批准。

回复“yes”/“y”批准，或“no”/“n”拒绝。

## 安全 {#security}

:::warning
始终设置 `TELEGRAM_ALLOWED_USERS` 以限制谁可以与你的 bot 交互。如果没有设置，网关默认会拒绝所有用户，作为安全措施。
:::

切勿公开分享你的 bot token。如果泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。

更多详情，请参阅[安全文档](/user-guide/security)。你也可以使用[DM 配对](/user-guide/messaging#dm-pairing-alternative-to-allowlists)来实现更动态的用户授权方式。
