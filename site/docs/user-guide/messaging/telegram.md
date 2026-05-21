---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

<a id="telegram-setup"></a>
# Telegram 设置

Hermes Agent 与 Telegram 集成，成为一个功能齐全的对话机器人。连接后，你可以从任何设备与你的 Agent 聊天、发送自动转录的语音备忘录、接收计划任务结果，并在群聊中使用该 Agent。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/)，支持文本、语音、图片和文件附件。

<a id="step-1-create-a-bot-via-botfather"></a>
## 步骤 1：通过 BotFather 创建机器人

每个 Telegram 机器人都需要一个由 Telegram 官方机器人管理工具 [@BotFather](https://t.me/BotFather) 颁发的 API 令牌。

1.  打开 Telegram，搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2.  发送 `/newbot`
3.  选择一个**显示名称**（例如 "Hermes Agent"）—— 可以是任何名称
4.  选择一个**用户名** —— 必须是唯一的，并以 `bot` 结尾（例如 `my_hermes_bot`）
5.  BotFather 会回复你的 **API 令牌**。它看起来像这样：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请妥善保管你的机器人令牌。任何拥有此令牌的人都可以控制你的机器人。如果泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。
:::

<a id="step-2-customize-your-bot-optional"></a>
## 步骤 2：自定义你的机器人（可选）

这些 BotFather 命令可以改善用户体验。给 @BotFather 发消息并使用：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始聊天前显示的“这个机器人能做什么？”文本 |
| `/setabouttext` | 机器人资料页上的简短介绍文本 |
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

Telegram 机器人有一个**隐私模式**，**默认是启用的**。这是在群组中使用机器人时最常见的困惑来源。

**当隐私模式开启时**，你的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自己消息的消息
- 服务消息（成员加入/离开、置顶消息等）
- 机器人是管理员的频道中的消息

**当隐私模式关闭时**，机器人会收到群组中的每一条消息。

<a id="how-to-disable-privacy-mode"></a>
### 如何禁用隐私模式

1.  给 **@BotFather** 发消息
2.  发送 `/mybots`
3.  选择你的机器人
4.  进入 **Bot Settings → Group Privacy → Turn off**

:::warning
**更改隐私设置后，你必须从任何群组中移除并重新添加机器人**。Telegram 在机器人加入群组时会缓存隐私状态，除非移除并重新添加，否则不会更新。
:::

:::tip
禁用隐私模式的替代方案：将机器人提升为**群组管理员**。管理员机器人无论隐私设置如何，始终会收到所有消息，这样就无需切换全局隐私模式。
:::

<a id="observe-group-chatter-without-auto-replying"></a>
### 观察群聊而不自动回复

对于 OpenClaw/Yuanbao 风格的群组行为，配置 Telegram 使机器人能够**看到**普通群组消息，但仅在直接触发时才**回复**：

```yaml
telegram:
  allowed_chats:
    - "-1001234567890"
  group_allowed_chats:
    - "-1001234567890"
  require_mention: true
  observe_unmentioned_group_messages: true
```

启用此模式后，来自明确允许列表中的聊天/主题的、未被提及的群组消息会作为观察到的上下文附加到共享的聊天/主题会话记录中，但它们不会触发 Agent 响应。`allowed_chats` 控制机器人响应的位置；`group_allowed_chats` 授权用于观察上下文的共享群组会话，因此在此模式下使用相同的聊天 ID。之后在同一允许列表中的聊天/主题中，`@botname` 提及、回复机器人或配置的提及模式可以使用该观察到的上下文。被触发的消息也会被标记为 `[昵称|用户ID]`，并收到每轮的安全提示，以便模型将之前观察到的行视为上下文，而不是针对机器人的指令。

等效的环境变量：

```bash
TELEGRAM_ALLOWED_CHATS=-1001234567890
TELEGRAM_GROUP_ALLOWED_CHATS=-1001234567890
TELEGRAM_OBSERVE_UNMENTIONED_GROUP_MESSAGES=true
```

这要求 Telegram 将普通群组消息传递给网关，因此需要按照上述方法禁用 BotFather 的隐私模式或将机器人提升为群组管理员。

<a id="step-4-find-your-user-id"></a>
## 步骤 4：查找你的用户 ID

Hermes Agent 使用数字形式的 Telegram 用户 ID 来控制访问权限。你的用户 ID **不是**你的用户名 —— 它是一个像 `123456789` 这样的数字。

**方法 1（推荐）：** 给 [@userinfobot](https://t.me/userinfobot) 发消息 —— 它会立即回复你的用户 ID。

**方法 2：** 给 [@get_id_bot](https://t.me/get_id_bot) 发消息 —— 另一个可靠的选择。

保存这个数字；下一步你会用到它。

<a id="step-5-configure-hermes"></a>
## 步骤 5：配置 Hermes

<a id="option-a-interactive-setup-recommended"></a>
### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

提示时选择 **Telegram**。向导会询问你的机器人令牌和允许的用户 ID，然后为你写入配置。

<a id="option-b-manual-configuration"></a>
### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # 多个用户用逗号分隔
```

<a id="start-the-gateway"></a>
### 启动网关

```bash
hermes gateway
```

机器人应该在几秒钟内上线。在 Telegram 上给它发条消息验证一下。

<a id="sending-generated-files-from-docker-backed-terminals"></a>
## 从 Docker 后端终端发送生成的文件

如果你的终端后端是 `docker`，请注意 Telegram 附件是由**网关进程**发送的，而不是从容器内部发送的。这意味着最终的 `MEDIA:/...` 路径必须在运行网关的主机上可读。

常见的陷阱：

- Agent 在 Docker 内部将文件写入 `/workspace/report.txt`
- 模型输出 `MEDIA:/workspace/report.txt`
- Telegram 发送失败，因为 `/workspace/report.txt` 只存在于容器内部，而不在主机上

推荐模式：

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

如果你已经有一个 `docker_volumes:` 部分，请将新的挂载添加到同一个列表中。YAML 中重复的键会静默覆盖较早的键。

<a id="supported-media-file-extensions"></a>
### 支持的 `MEDIA:` 文件扩展名

网关从 Agent 回复中提取 `MEDIA:/path/to/file` 标签，并将引用的文件作为平台原生附件发送。所有网关平台支持的扩展名：

| 类别 | 扩展名 |
|---|---|
| 图片 | `png`, `jpg`, `jpeg`, `gif`, `webp`, `bmp`, `tiff`, `svg` |
| 音频 | `mp3`, `wav`, `ogg`, `m4a`, `opus`, `flac`, `aac` |
| 视频 | `mp4`, `mov`, `webm`, `mkv`, `avi` |
| **文档** | `pdf`, `txt`, `md`, `csv`, `json`, `xml`, `html`, `yaml`, `yml`, `log` |
| **办公** | `docx`, `xlsx`, `pptx`, `odt`, `ods`, `odp` |
| **压缩包** | `zip`, `rar`, `7z`, `tar`, `gz`, `bz2` |
| **书籍 / 安装包** | `epub`, `apk`, `ipa` |

此列表中的任何文件在支持它的平台（Telegram、Discord、Signal、Slack、WhatsApp、飞书、Matrix 等）上都会作为原生附件发送；在不支持原生附件的平台上，它会回退为链接或纯文本指示器。**粗体**的类别是在最近几个版本中添加的 —— 如果你之前依赖模型说 `here is the file: /path/to/report.docx`，请改用 `MEDIA:/path/to/report.docx` 以获得原生发送。

<a id="webhook-mode"></a>
## Webhook 模式

默认情况下，Hermes 使用**长轮询**连接到 Telegram —— 网关向 Telegram 的服务器发出出站请求以获取新更新。这对于本地和始终在线的部署效果很好。

对于**云部署**（Fly.io、Railway、Render 等），**Webhook 模式**更具成本效益。这些平台可以在入站 HTTP 流量时自动唤醒挂起的机器，但不能在出站连接时唤醒。由于轮询是出站的，轮询机器人永远无法休眠。Webhook 模式翻转了方向 —— Telegram 将更新推送到你机器人的 HTTPS URL，从而实现了空闲时休眠的部署。
| | 轮询（默认） | Webhook |
|---|---|---|
| 方向 | 网关 → Telegram（出站） | Telegram → 网关（入站） |
| 适用场景 | 本地、常开服务器 | 支持自动唤醒的云平台 |
| 设置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲成本 | 机器必须保持运行 | 机器可以在消息间隙休眠 |

<a id="configuration"></a>
### 配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
TELEGRAM_WEBHOOK_SECRET="$(openssl rand -hex 32)"  # 必需
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认 8443
```

| 变量 | 必需 | 描述 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 发送更新的公开 HTTPS URL。URL 路径会自动提取（例如，从上面的例子中提取 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | **是**（当设置了 `TELEGRAM_WEBHOOK_URL` 时） | Telegram 在每个 webhook 请求中回显用于验证的密钥令牌。没有它网关将拒绝启动 — 参见 [GHSA-3vpc-7q5r-276h](https://github.com/NousResearch/hermes-agent/security/advisories/GHSA-3vpc-7q5r-276h)。使用 `openssl rand -hex 32` 生成。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | Webhook 服务器监听的本地端口（默认：`8443`）。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关会启动一个 HTTP webhook 服务器而不是轮询。当未设置时，使用轮询模式 — 与之前版本的行为没有变化。

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

网关日志应显示：`[telegram] Connected to Telegram (webhook mode)`。

<a id="proxy-support"></a>
## 代理支持

如果 Telegram 的 API 被屏蔽，或者你需要通过代理路由流量，请设置一个 Telegram 专用的代理 URL。这会优先于通用的 `HTTPS_PROXY` / `HTTP_PROXY` 环境变量。

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

该代理同时适用于主要的 Telegram 连接和备用 IP 传输。如果没有设置 Telegram 专用代理，网关将回退到 `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY`（或 macOS 系统代理自动检测）。

<a id="home-channel"></a>
## 主频道

在任何 Telegram 聊天（私聊或群组）中使用 `/sethome` 命令，将其指定为**主频道**。计划任务（cron 作业）会将结果发送到此频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="我的笔记"
```

:::tip
群组聊天 ID 是负数（例如 `-1001234567890`）。你的个人私聊 ID 与你的用户 ID 相同。
:::

<a id="cron-deliveries-in-topic-mode"></a>
### 话题模式下的 Cron 投递

如果你的机器人私聊启用了话题模式，投递到根聊天的 cron 消息会落在仅限系统的公共区域 — 在那里回复不会开启会话，并且你会看到“主聊天保留给系统命令使用”的提示。创建一个专门的论坛话题（例如 `Cron`）并设置：

```bash
TELEGRAM_CRON_THREAD_ID=<话题线程ID>
```

`TELEGRAM_CRON_THREAD_ID` 仅针对 cron 投递覆盖 `TELEGRAM_HOME_CHANNEL_THREAD_ID`。在该话题中的回复会继续该话题的现有会话。

<a id="voice-messages"></a>
## 语音消息

<a id="incoming-voice-speech-to-text"></a>
### 接收语音（语音转文本）

你在 Telegram 上发送的语音消息会被 Hermes 配置的 STT 提供商自动转录，并以文本形式注入到对话中。

- `local` 在运行 Hermes 的机器上使用 `faster-whisper` — 无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

<a id="skipping-stt-pass-the-raw-audio-file-to-the-agent"></a>
#### 跳过 STT：将原始音频文件传递给 Agent

如果你更希望**Agent 本身**来处理音频 — 用于说话人分离、自定义转录工具，或者仅仅是存档录音 — 请在 `~/.hermes/config.yaml` 中设置 `stt.enabled: false`：

```yaml
stt:
  enabled: false
```

禁用 STT 后，网关仍会将语音/音频附件下载到 Hermes 的音频缓存中，但**不会转录它**。Agent 会收到一条带有如下标记的消息：

```
[用户发送了一条语音消息：/home/<用户>/.hermes/cache/audio/<哈希>.ogg]
```

然后，你的工具或技能可以直接读取该路径（例如，将其交给本地说话人分离流程、更丰富的转录模型，或上传到长期存储）。文件扩展名反映了 Telegram 传递的原始格式（语音笔记为 `.ogg`，音频附件为 `.mp3`/`.m4a`/等）。

这自然与下面的[本地 Bot API 服务器](#large-files-20mb--via-local-bot-api-server)部分搭配使用，该部分将 Telegram 的 20MB getFile 上限提升到 2GB — 当你想处理的录音超过几分钟时长时非常有用。

<a id="outgoing-voice-text-to-speech"></a>
### 发送语音（文本转语音）

当 Agent 通过 TTS 生成音频时，它会以原生 Telegram **语音气泡**的形式投递 — 那种圆形的、可内联播放的类型。

- **OpenAI 和 ElevenLabs** 原生生成 Opus — 无需额外设置
- **Edge TTS**（默认的免费提供商）输出 MP3，需要 **ffmpeg** 来转换为 Opus：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

没有 ffmpeg 时，Edge TTS 音频会作为普通音频文件发送（仍然可播放，但使用矩形播放器而不是语音气泡）。

在你的 `config.yaml` 中的 `tts.provider` 键下配置 TTS 提供商。

<a id="large-files-20mb-via-local-bot-api-server"></a>
## 通过本地 Bot API 服务器处理大文件（>20MB）

Telegram 的**公共** Bot API 将 `getFile` 下载限制在 **20 MB**，因此任何超过此大小的语音笔记、音频文件、视频或文档都会被 Hermes 静默拒绝，并回复“文件过大”。解决此问题的文档化方法是运行一个**本地**的 [telegram-bot-api](https://github.com/tdlib/telegram-bot-api) 守护进程 — 这是 Telegram 使用的相同服务器软件，但在你的网络上运行。本地服务器将文件上限提高到 **2 GB**，并且当 Hermes 检测到配置了自定义 `base_url` 时，会自动解除其内部限制。

这解锁了以下工作流：

- 向机器人发送长语音备忘录（45 分钟的会议、播客）
- 上传大视频供视觉工具处理
- 存档原始音频用于离线流程，如说话人分离、对齐或训练数据

<a id="step-1-obtain-telegram-api-credentials"></a>
### 步骤 1：获取 Telegram API 凭证

本地服务器直接与 Telegram 的 MTProto 层通信（而非公共 Bot API），因此需要 **MTProto 凭证**：

1. 访问 [my.telegram.org/apps](https://my.telegram.org/apps) 并使用你的 Telegram 账户登录。
2. 创建一个新应用程序（任何名称和简短描述都可以）。
3. 复制 `api_id` 和 `api_hash` — 两者都是必需的。

<a id="step-2-run-the-telegram-bot-api-server"></a>
### 步骤 2：运行 telegram-bot-api 服务器

社区维护的 [`aiogram/telegram-bot-api`](https://hub.docker.com/r/aiogram/telegram-bot-api) Docker 镜像是最简单的方法。一个最小的 `docker-compose.yaml`（使用 `--local` 模式以启用更高的限制）：

```yaml
services:
  tg-bot-api:
    image: aiogram/telegram-bot-api:latest
    container_name: tg-bot-api
    restart: unless-stopped
    ports:
      - "127.0.0.1:8081:8081"   # 仅绑定到环回地址；参见安全说明
    environment:
      TELEGRAM_API_ID: "12345"           # 来自步骤 1 的 api_id
      TELEGRAM_API_HASH: "abcdef..."     # 来自步骤 1 的 api_hash
      TELEGRAM_LOCAL: "1"                # 启用 --local 模式（将 20MB 提升至 2GB）
    volumes:
      - ./tg-bot-api-data:/var/lib/telegram-bot-api
```

启动它：

```bash
docker compose up -d tg-bot-api
docker logs --tail 20 tg-bot-api
```

<a id="security"></a>
:::warning 安全警告
本地 Bot API 服务器在 URL 路径中接收你的机器人令牌（例如 `/bot&lt;TOKEN&gt;/getMe`），**没有额外的身份验证**。任何能访问该端口的人都可以完全控制你的机器人 — 读取它能看到的每条消息、以它的身份发送消息等。请将容器绑定到 `127.0.0.1` 和/或在私有网络前放置反向代理。**切勿将 8081 端口暴露给公共互联网。**
:::
<a id="step-3-log-the-bot-out-of-the-public-api-one-time"></a>
### 步骤 3：将机器人从公共 API 登出（一次性操作）

一个机器人同一时间只能在 **一个** Bot API 服务器上处于活动状态。如果你的机器人之前已经在使用 `api.telegram.org`（几乎可以肯定是的），你必须在本地服务器接受它之前，明确地将其从那里登出：

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/logOut"
# 预期响应：{"ok":true,"result":true}
```

这是一个一次性的迁移步骤——不需要在每次重启时重复。Telegram 会将 `logOut` 之后收到的任何消息通过新服务器传递。

验证本地服务器可以代表机器人向 Telegram 通信：

```bash
curl "http://127.0.0.1:8081/bot<YOUR_BOT_TOKEN>/getMe"
# 预期响应：{"ok":true,"result":{"id":...,"is_bot":true,...}}
```

<a id="step-4-point-hermes-at-the-local-server"></a>
### 步骤 4：将 Hermes 指向本地服务器

在 `~/.hermes/config.yaml` 中的 `platforms.telegram.extra` 下添加 URL：

```yaml
platforms:
  telegram:
    extra:
      base_url: "http://127.0.0.1:8081/bot"
      base_file_url: "http://127.0.0.1:8081/file/bot"
      local_mode: true        # 参见下面的步骤 5 — 仅当机器人数据目录对 Hermes 进程可读时才设置此项
```

:::caution 使用 `platforms.telegram.extra`，而不是 `telegram.extra`
目前只有 `platforms.&lt;name&gt;.extra` 这种形式会被深度合并到平台配置中。直接放在顶级 `telegram.extra` 块下的键会被静默丢弃。
:::

当设置了 `base_url` 时，Hermes 会：
<a id="use-platforms-telegram-extra-not-telegram-extra"></a>

- 针对本地服务器构建 python-telegram-bot 客户端
- 自动将其内部文档/音频大小上限从 20 MB 提升至 2 GB
- 在“文件过大”错误消息中报告当前生效的限制（`Maximum: 2048 MB.`），这样你就能清楚知道处于哪种模式

重启网关并查找确认日志行：

```bash
hermes gateway restart
grep -E "Using custom Telegram base_url|Using Telegram local_mode" ~/.hermes/logs/gateway.log | tail
```

<a id="step-5-localmode-file-access-on-disk"></a>
### 步骤 5：`local_mode` — 磁盘文件访问

本地服务器有 **两种方式** 来提供文件：

1.  **不使用 `--local`**（默认）：文件通过 HTTP 在 `/file/bot&lt;TOKEN&gt;/&lt;path&gt;` 提供，与公共 Bot API 相同。20MB 的上限仍然有效。仅适用于网络修复（例如当 `api.telegram.org` 无法访问但你可以自托管时）；这不是你为了提升大小限制想要的模式。
2.  **使用 `--local`**（通过上面的 `TELEGRAM_LOCAL=1` 设置）：文件被写入服务器的文件系统，并且 `getFile` 响应返回一个 **绝对路径** 而不是 HTTP URL。20MB 的上限被解除。然后 Hermes 必须 **从磁盘** 读取字节，而不是通过 HTTP。

要使磁盘读取路径正常工作，需要在上述配置中设置 `local_mode: true` **并且** 确保 Hermes 进程可以读取服务器返回的路径。有两种场景：

-   **同一台机器** — telegram-bot-api 和 Hermes 运行在同一台主机上。将数据卷绑定挂载到 Hermes 可以读取的目录（例如，`/var/lib/telegram-bot-api`），并确保文件所有权匹配。容器会将其权限降级到其内部的 `telegram-bot-api` 用户（uid 因镜像而异）；最简单的解决方法是向 compose 服务添加 `user: "&lt;UID&gt;:&lt;GID&gt;"`，使文件归 Hermes 已经运行的 uid 所有。
-   **不同机器** — 机器人服务器运行在一台主机上（例如，NAS、单独的 VM），而 Hermes 运行在另一台主机上。服务器的数据目录必须与 Hermes 机器共享，且共享路径必须是服务器报告的 **相同绝对路径**（通常是 `/var/lib/telegram-bot-api`）。NFS 对此很有效；如果你不想在文件系统层面处理 uid 不匹配问题，使用带 `uid=` 挂载重新映射的 CIFS/SMB 会更友好。

如果设置了 `local_mode: true` 但 Hermes 无法 `stat` 返回的文件路径（权限问题或挂载错误），python-telegram-bot 会静默回退到针对本地服务器的 HTTP `getFile` 请求——而在 `--local` 模式下，服务器会响应 `404 Not Found`。症状会在 `gateway.log` 中显示为：

```
[Telegram] Failed to cache voice: Not Found
telegram.error.InvalidToken: Not Found
```

如果你看到这个，说明上限提升正在工作，但文件共享没有。请以网关运行用户的身份，从 Hermes 主机验证 `ls -la /var/lib/telegram-bot-api/&lt;TOKEN&gt;/voice/`，并确认单个文件可以 `cat` 读取而没有权限错误。

<a id="step-6-test-it"></a>
### 步骤 6：测试

向机器人发送一个大于 20 MB 的语音消息或音频文件。跟踪网关日志：

```bash
tail -f ~/.hermes/logs/gateway.log | grep -iE "telegram|cache"
```

你应该会看到一行 `[Telegram] Cached user voice at /home/&lt;user&gt;/.hermes/cache/audio/...` 并且 **没有** “文件过大”的拒绝信息。结合 `stt.enabled: false`（上文），原始音频文件的路径随后会进入 Agent 的入站消息中，供下游处理。

<a id="group-chat-usage"></a>
## 群聊使用

Hermes Agent 可以在 Telegram 群聊中工作，但需要注意以下几点：

-   **隐私模式** 决定了机器人能看到哪些消息（参见[步骤 3](#step-3-privacy-mode-critical-for-groups)）
-   `TELEGRAM_ALLOWED_USERS` 仍然适用——即使在群组中，也只有授权用户才能触发机器人
-   你可以通过 `telegram.require_mention: true` 来防止机器人响应普通的群聊消息
-   当 `telegram.require_mention: true` 时，群组消息在以下情况下会被接受：
    -   回复机器人发送的消息
    -   `@botusername` 提及
    -   `/command@botusername`（Telegram 的包含机器人名称的菜单命令形式）
    -   匹配你在 `telegram.mention_patterns` 中配置的正则唤醒词
-   在拥有多个 Hermes 机器人的群组中，`telegram.exclusive_bot_mentions` 可以保持路由确定性。当一条消息明确提及一个或多个 Telegram 机器人用户名时，只有被提及的机器人配置文件会处理它；其他 Hermes 机器人在回复和唤醒词回退逻辑运行之前会忽略它。此功能默认启用。
-   使用 `telegram.ignored_threads` 可以让 Hermes 在特定的 Telegram 论坛话题中保持静默，即使群组在其他情况下允许自由回复或提及触发的回复
-   如果 `telegram.require_mention` 未设置或设为 false，Hermes 将保持之前的开放群组行为，并响应它能看到的普通群组消息

<a id="multiple-hermes-bots-in-one-group"></a>
### 一个群组中的多个 Hermes 机器人

如果你在同一个 Telegram 群组中运行多个 Hermes 配置文件，请为每个配置文件创建一个 Telegram 机器人令牌，并为每个配置文件启动一个网关。不要在多个运行的网关中重复使用同一个机器人令牌；Telegram 会拒绝对同一令牌的并发轮询。

推荐的群组配置：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns: []
```

在这种设置下，像 `@research_bot @ops_bot summarize this` 这样的群组消息只会被 `research_bot` 和 `ops_bot` 处理。群组中的其他 Hermes 机器人将保持静默，即使该消息是对它们之前消息的回复，或者在其他情况下匹配了共享的唤醒词。

仅在需要旧版共享触发行为的遗留群组中，才将 `exclusive_bot_mentions` 设置为 `false`。

要操作多个配置文件，请为每个配置文件运行一次网关命令。例如：

```bash
# 默认配置文件
hermes gateway start
hermes gateway status
hermes gateway stop

# 命名配置文件
hermes -p research gateway start
hermes -p research gateway status
hermes -p research gateway stop
```

对于小型固定集合，可以使用 shell 循环或脚本，为默认配置文件调用 `hermes gateway &lt;action&gt;`，为每个命名配置文件调用 `hermes -p &lt;profile&gt; gateway &lt;action&gt;`。这比假设单个进程级命令可以控制每个服务管理器上的每个命名配置文件更可靠。

<a id="troubleshooting-works-in-dms-but-not-groups"></a>
### 故障排除：私聊有效但群聊无效

如果机器人在私聊中能响应但在群聊中保持静默，请按顺序检查以下关卡：

1.  **Telegram 消息投递：** 关闭 BotFather 隐私模式，将机器人提升为管理员，或直接提及机器人。如果 Telegram 从未将群组消息投递给机器人，Hermes 就无法响应。
2.  **更改隐私设置后重新加入：** 更改 BotFather 隐私设置后，将机器人从群组中移除并重新添加。Telegram 可能会为现有的群组成员关系保留旧的投递行为。
3.  **Hermes 授权：** 确保发送者列在 `TELEGRAM_ALLOWED_USERS` 或 `TELEGRAM_GROUP_ALLOWED_USERS` 中，或者使用 `TELEGRAM_GROUP_ALLOWED_CHATS` 允许该群组聊天。
4.  **提及过滤器：** 如果设置了 `telegram.require_mention: true`，普通的群聊消息会被忽略，除非该消息是斜杠命令、回复机器人、`@botusername` 提及，或者匹配配置的 `mention_patterns`。
5.  **多机器人路由：** 如果群组包含多个机器人，请确保每个 Hermes 配置文件使用唯一的机器人令牌，并保持 `exclusive_bot_mentions` 启用，除非你特意需要旧版共享触发行为。
负数的聊天 ID 在 Telegram 群组和超级群组中是正常的。如果你使用聊天范围授权，请将这些 ID 放入 `TELEGRAM_GROUP_ALLOWED_CHATS`，而不是发送者用户的允许列表中。

<a id="example-group-trigger-configuration"></a>
### 群组触发配置示例

将此添加到 `~/.hermes/config.yaml`：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns:
    - "^\\s*chompy\\b"
  ignored_threads:
    - 31
    - "42"
```

此示例允许所有常规的直接触发方式，以及以 `chompy` 开头的消息，即使它们没有使用 `@mention`。
在提及和自由响应检查运行之前，Telegram 话题 `31` 和 `42` 中的消息总是被忽略。

<a id="notes-on-mentionpatterns"></a>
### 关于 `mention_patterns` 的说明

- 模式使用 Python 正则表达式
- 匹配不区分大小写
- 模式会同时检查文本消息和媒体说明文字
- 无效的正则表达式模式会被忽略，并在网关日志中发出警告，而不是导致机器人崩溃
- 如果你希望模式仅在消息开头匹配，请使用 `^` 锚定

<a id="private-chat-topics-bot-api-9-4"></a>
## 私聊话题 (Bot API 9.4) {#private-chat-topics-bot-api-94}

Telegram Bot API 9.4 (2026年2月) 引入了**私聊话题** —— 机器人可以直接在 1 对 1 私聊中创建论坛式的话题线程，无需超级群组。这让你可以在与 Hermes 的现有私聊中运行多个独立的工作空间。

<a id="use-case"></a>
### 使用场景

如果你同时进行多个长期项目，话题可以将它们的上下文分开：

- **话题 "Website"** —— 处理你的生产环境 Web 服务
- **话题 "Research"** —— 文献综述和论文探索
- **话题 "General"** —— 杂项任务和快速提问

每个话题都有自己的对话会话、历史记录和上下文 —— 与其他话题完全隔离。

<a id="configuration"></a>
### 配置

:::caution 前提条件
在配置中添加话题之前，用户必须**在与机器人的私聊中启用话题模式**：

1. 在 Telegram 中打开与 Hermes 机器人的私聊
2. 点击顶部的机器人名称以打开聊天信息
3. 启用**话题**（将聊天切换为论坛的开关）

如果没有启用，Hermes 将在启动时记录 `The chat is not a forum` 并跳过话题创建。这是 Telegram 客户端的设置 —— 机器人无法通过编程方式启用它。
:::

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
          skill: arxiv              # 在此话题中自动加载一个技能
```

**字段说明：**

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 话题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 话题图标的自定义表情符号 ID |
| `skill` | 否 | 在此话题的新会话中自动加载的技能 |
| `thread_id` | 否 | 话题创建后自动填充 —— 不要手动设置 |

<a id="how-it-works"></a>
### 工作原理

1. 网关启动时，Hermes 为每个尚未分配 `thread_id` 的话题调用 `createForumTopic`
2. `thread_id` 会自动保存回 `config.yaml` —— 后续重启将跳过 API 调用
3. 每个话题映射到一个独立的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4. 每个话题中的消息都有自己的对话历史记录、内存刷新和上下文窗口

<a id="root-dm-handling"></a>
### 根私聊处理

默认情况下，发送到根私聊（在任何话题之外）的消息会正常处理。设置 `ignore_root_dm: true` 可将根私聊变为一个大厅 —— 对于配置了私聊话题的用户，普通消息会被静默忽略，而系统命令（`/start`、`/help`、`/status` 等）仍然有效。

```yaml
platforms:
  telegram:
    extra:
      ignore_root_dm: true
      dm_topics:
        - chat_id: 123456789
          topics:
            - name: General
```

此检查是**按聊天进行的**：只有 `dm_topics` 中至少有一条记录的用户，其根私聊才会受到影响。未配置话题的用户不受影响。

<a id="skill-binding"></a>
### 技能绑定

带有 `skill` 字段的话题会在该话题中启动新会话时自动加载该技能。这就像在对话开始时输入 `/skill-name` 一样 —— 技能内容被注入到第一条消息中，后续消息会在对话历史记录中看到它。

例如，一个带有 `skill: arxiv` 的话题，每当其会话重置时（由于空闲超时、每日重置或手动 `/reset`），都会预加载 arxiv 技能。

:::tip
在配置之外创建的话题（例如，通过手动调用 Telegram API）会在收到 `forum_topic_created` 服务消息时自动被发现。你也可以在网关运行时将话题添加到配置中 —— 它们会在下一次缓存未命中时被拾取。
:::

<a id="multi-session-dm-mode-topic"></a>
## 多会话私聊模式 (`/topic`)

一种 ChatGPT 风格的多会话私聊 —— 一个机器人，多个并行对话。与上面操作员配置的 `extra.dm_topics` 不同，此模式是**用户驱动的**：无需配置，无需预先声明话题名称。最终用户通过 `/topic` 开启它，然后点击 Telegram 的 **+** 按钮创建任意数量的话题，每个话题都是一个完全独立的 Hermes 会话。

<a id="topic-subcommands"></a>
### `/topic` 子命令

| 形式 | 上下文 | 效果 |
|------|---------|--------|
| `/topic` | 根私聊，尚未启用 | 检查 BotFather 功能，启用多会话模式，创建置顶的系统话题 |
| `/topic` | 根私聊，已启用 | 显示状态：可恢复的未链接会话 |
| `/topic` | 在话题内部 | 显示当前话题的会话绑定 |
| `/topic help` | 任意 | 内联用法说明 |
| `/topic off` | 根私聊 | 禁用多会话模式并清除此聊天的所有话题绑定 |
| `/topic &lt;session-id&gt;` | 在话题内部 | 将之前的 Telegram 会话恢复到当前话题 |

只有授权用户（通过 `TELEGRAM_ALLOWED_USERS` / 平台授权配置允许列表）可以运行 `/topic`。未经授权的发送者会收到拒绝提示，而不是激活。

<a id="dm-topics-vs-multi-session-dm-mode"></a>
### 私聊话题 vs 多会话私聊模式

| | `extra.dm_topics` (配置驱动) | `/topic` (用户驱动) |
|---|---|---|
| 谁激活它 | 操作员，在 `config.yaml` 中 | 最终用户，通过发送 `/topic` |
| 话题列表 | 配置中声明的固定集合 | 用户自由创建/删除话题 |
| 话题名称 | 由操作员选择 | 由用户选择；自动重命名以匹配 Hermes 会话标题 |
| 根私聊行为 | 正常聊天（如果 `ignore_root_dm: true` 则为大厅） | 变为系统大厅（非命令消息被拒绝） |
| 主要用例 | 带有可选技能绑定的永久工作空间 | 临时并行会话 |
| 持久化 | 配置中的 `extra.dm_topics` | `telegram_dm_topic_mode` + `telegram_dm_topic_bindings` SQLite 表 |

这两个功能可以在同一个机器人上共存 —— 你可以从用户的私聊运行 `/topic`，而 `extra.dm_topics` 继续为其他聊天管理操作员声明的话题。

<a id="prerequisites"></a>
### 前提条件

在 **@BotFather** 中，打开你的机器人 → **Bot Settings → Threads Settings**：

1. 开启 **Threaded Mode**（启用 `has_topics_enabled`）
2. **不要**禁止用户创建话题（保持 `allows_users_to_create_topics` 开启）

当用户首次运行 `/topic` 时，Hermes 会调用 `getMe` 来验证这两个标志。如果任何一个关闭，Hermes 会发送 BotFather Threads Settings 页面的截图并解释需要切换什么 —— 在满足前提条件之前不会激活。

<a id="activation-flow"></a>
### 激活流程

从根私聊发送：

```
/topic
```

Hermes 将：

1. 检查 `getMe().has_topics_enabled` 和 `allows_users_to_create_topics`
2. 如果两者都为真，则为此私聊启用多会话话题模式
3. 创建并置顶一个**系统**话题用于状态/命令（尽力而为）
4. 回复一个用户可以恢复的先前未链接的 Telegram 会话列表

激活后，**根私聊变为一个大厅**：普通提示会被拒绝，并给出指向**所有消息**的指引。系统命令（`/status`、`/sessions`、`/usage`、`/help` 等）在根私聊中仍然有效。
<a id="creating-a-new-topic-end-user-flow"></a>
### 创建新主题（最终用户流程）

1. 在 Telegram 中打开与机器人的私聊
2. 点击机器人界面顶部的 **所有消息**，然后发送任意消息
3. Telegram 会为该消息创建一个新主题
4. Hermes 在该主题内回复 —— 该主题现在是一个独立的会话

每个主题都有自己的对话历史、模型状态、工具执行和会话 ID。隔离键为 `agent:main:telegram:dm:{chat_id}:{thread_id}` —— 与配置驱动的私聊主题隔离方式相同。

<a id="auto-renamed-topics"></a>
### 自动重命名主题

当 Hermes 为某个主题生成会话标题时（通过自动标题流程，在首次交互后），Telegram 主题本身也会被重命名以匹配 —— 例如，“新主题” 会变成 “数据库迁移计划”。重命名是尽力而为的：失败会被记录，但不会中断会话。

要禁用此功能并保留您手动选择的主题名称，请设置：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_topic_auto_rename: true
```

当此标志开启时，Hermes 仍会生成内部会话标题（供 `hermes sessions`、TUI 等使用），但绝不会编辑 Telegram 主题名称。当您在 BotFather 的线程模式下手动组织主题，并且不希望每次首次回复都覆盖标题时，这很有用。

<a id="new-inside-a-topic"></a>
### 在主题内使用 `/new`

重置当前主题的会话（新的会话 ID，全新的历史记录），而不影响其他主题。Hermes 会回复一个提醒，说明对于并行工作，通常您需要的是创建另一个主题（通过 **所有消息**）。

<a id="restoring-a-previous-session"></a>
### 恢复之前的会话

在主题内发送：

```
/topic <session-id>
```

这会将当前主题绑定到一个现有的 Hermes 会话，而不是重新开始。对于继续在启用主题模式之前开始的对话很有用。限制条件：

- 目标会话必须属于同一个 Telegram 用户
- 目标会话必须尚未绑定到另一个主题

Hermes 会确认会话标题并重播最后一条助手消息以提供上下文。

要查找会话 ID，请在根私聊中发送 `/topic`（不带参数）—— Hermes 会列出该用户未链接的 Telegram 会话。

<a id="topic-inside-a-topic-no-argument"></a>
### 在主题内使用 `/topic`（不带参数）

显示当前主题的绑定信息：会话标题、会话 ID，以及关于 `/new` 与创建另一个主题的提示。

<a id="under-the-hood"></a>
### 底层原理

- 激活状态会持久化到 `state.db` 中的 `telegram_dm_topic_mode(chat_id, user_id, enabled, ...)`
- 每个主题绑定会持久化到 `telegram_dm_topic_bindings(chat_id, thread_id, session_id, ...)`，并在 `session_id` 上设置 `ON DELETE CASCADE` —— 清理会话会自动清除其主题绑定
- 主题模式的 SQLite 迁移是**可选的**：它在首次调用 `/topic` 时运行，绝不会在网关启动时运行。在此配置文件中用户运行 `/topic` 之前，`state.db` 保持不变
- 每条传入的私聊消息都会查找其 `(chat_id, thread_id)` 绑定。如果存在，查找会通过 `SessionStore.switch_session()` 将消息路由到绑定的会话，从而保持磁盘上会话键到会话 ID 的映射一致性
- 在主题内使用 `/new` 会重写绑定行，使其指向新的会话 ID，因此下一条消息会保持在新的会话上
- 在 `extra.dm_topics` 中声明的主题**永远不会被自动重命名** —— 即使启用了多会话模式，操作员选择的名称也会被保留
- 设置 `extra.disable_topic_auto_rename: true` 可以关闭聊天中**所有**主题的自动重命名（包括通过线程模式创建的临时主题）
- 在启用论坛功能的私聊中，General（置顶）主题被视为根大厅，无论 Telegram 传递其消息时是否带有 `message_thread_id=1` 或没有 thread_id
- 根大厅的提醒消息被限制为每聊天每 30 秒一条消息 —— 忘记主题模式已开启并在根大厅输入十条提示的用户不会收到十条回复
- BotFather 设置截图被限制为每聊天每 5 分钟发送一次 —— 在“线程设置”仍被禁用时重复尝试 `/topic` 不会重新上传同一张图片
- 在主题内启动的 `/background &lt;prompt&gt;` 会将其结果发送回同一主题；后台会话不会触发所属主题的自动重命名
- `/topic` 命令本身受机器人的用户授权检查控制 —— 未授权的私聊会收到拒绝信息，而不是激活功能

<a id="disabling-multi-session-mode"></a>
### 禁用多会话模式

在根私聊中发送 `/topic off`。Hermes 会将对应行关闭，清除该聊天的 `(thread_id → session_id)` 绑定，并且根私聊会恢复为普通的 Hermes 聊天。Telegram 中现有的主题不会被删除 —— 它们只是不再被作为独立会话进行隔离。稍后重新运行 `/topic` 可以重新开启。

如果您需要手动清理（例如，跨多个聊天进行批量重置），请直接删除行：

```bash
sqlite3 ~/.hermes/state.db \
  "UPDATE telegram_dm_topic_mode SET enabled = 0 WHERE chat_id = '<your_chat_id>'; \
   DELETE FROM telegram_dm_topic_bindings WHERE chat_id = '<your_chat_id>';"
```

<a id="downgrading-hermes"></a>
### 降级 Hermes

如果您降级到早于 `/topic` 功能的 Hermes 版本，该功能将停止工作 —— `telegram_dm_topic_mode` 和 `telegram_dm_topic_bindings` 表仍保留在 `state.db` 中，但会被旧代码忽略。私聊将恢复为原生的每线程隔离（每个 `message_thread_id` 仍然通过 `build_session_key` 获得自己的会话），因此您现有的 Telegram 主题将继续作为并行会话工作。根私聊不再是根大厅 —— 那里的消息会像以前一样进入 Agent。重新升级会完全恢复之前的多会话模式。

<a id="group-forum-topic-skill-binding"></a>
## 群组论坛主题技能绑定

启用了**主题模式**（也称为“论坛主题”）的超级群组已经实现了每个主题的会话隔离 —— 每个 `thread_id` 映射到自己的对话。但您可能希望在消息到达特定群组主题时**自动加载一个技能**，就像私聊主题技能绑定一样。

<a id="use-case"></a>
### 使用场景

一个拥有不同工作流论坛主题的团队超级群组：

- **Engineering** 主题 → 自动加载 `software-development` 技能
- **Research** 主题 → 自动加载 `arxiv` 技能
- **General** 主题 → 无技能，通用助手

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
          # 无技能 —— 通用目的
```

**字段说明：**

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `chat_id` | 是 | 超级群组的数字 ID（以 `-100` 开头的负数） |
| `name` | 否 | 主题的人类可读标签（仅用于信息） |
| `thread_id` | 是 | Telegram 论坛主题 ID —— 在 `t.me/c/&lt;group_id&gt;/&lt;thread_id&gt;` 链接中可见 |
| `skill` | 否 | 在此主题的新会话中自动加载的技能 |

<a id="how-it-works"></a>
### 工作原理

1. 当消息到达映射的群组主题时，Hermes 会在 `group_topics` 配置中查找 `chat_id` 和 `thread_id`
2. 如果匹配的条目有 `skill` 字段，则该技能会自动加载到会话中 —— 与私聊主题技能绑定相同
3. 没有 `skill` 键的主题仅获得会话隔离（现有行为，未改变）
4. 未映射的 `thread_id` 值或 `chat_id` 值会静默跳过 —— 无错误，无技能

<a id="differences-from-dm-topics"></a>
### 与私聊主题的区别

| | 私聊主题 | 群组主题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 主题创建 | 如果 `thread_id` 缺失，Hermes 通过 API 创建主题 | 管理员在 Telegram UI 中创建主题 |
| `thread_id` | 创建后自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（管理员控制外观） |
| 技能绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛主题已内置） |

:::tip
要查找主题的 `thread_id`，请在 Telegram Web 或 Desktop 中打开该主题并查看 URL：`https://t.me/c/1234567890/5` —— 最后一个数字 (`5`) 就是 `thread_id`。超级群组的 `chat_id` 是群组 ID 加上前缀 `-100`（例如，群组 `1234567890` 变为 `-1001234567890`）。
:::
<a id="recent-bot-api-features"></a>
## 近期 Bot API 特性

- **Bot API 9.4 (2026年2月)：** 私聊话题 — bot 可以通过 `createForumTopic` 在一对一私聊中创建论坛话题。Hermes 将此用于两个不同的功能：由操作者管理的 [私聊话题](#private-chat-topics-bot-api-94)（由配置驱动，固定话题列表）和由用户驱动的 [多会话私聊模式](#multi-session-dm-mode-topic)（通过 `/topic` 激活，用户可无限创建话题）。
- **隐私政策：** Telegram 现在要求 bot 拥有隐私政策。通过 BotFather 使用 `/setprivacy_policy` 进行设置，或者 Telegram 可能会自动生成一个占位符。如果你的 bot 是面向公众的，这一点尤为重要。
- **Bot API 9.5 (2026年3月)：** 通过 `sendMessageDraft` 进行原生流式传输。Hermes 支持 Telegram 的原生流式草案 API，作为私聊的可选传输方式。默认仍采用传统的 `editMessageText` 路径，因为草案预览在某些 Telegram 客户端上会出现明显的折叠和重新渲染。

<a id="streaming-transport-gateway-streaming-transport"></a>
### 流式传输方式 (`gateway.streaming.transport`)

当启用流式传输 (`gateway.streaming.enabled: true`) 时，Hermes 会选择以下四种传输方式之一：

| 值 | 行为 |
|---|---|
| `auto` | 在支持的聊天中使用原生草案流式传输（目前为 Telegram 私聊）；否则使用基于编辑的传统路径。如果草案帧失败，会优雅降级。 |
| `draft` | 强制使用原生草案。如果聊天不支持草案（例如群组/话题），会记录降级日志并回退到编辑方式。 |
| `edit` (默认) | 对所有聊天类型使用传统的渐进式 `editMessageText` 轮询。 |
| `off` | 完全禁用流式传输（仅发送最终回复，无渐进更新）。 |

在 `~/.hermes/config.yaml` 中：

```yaml
gateway:
  streaming:
    enabled: true
    transport: edit    # edit | auto | draft | off
```

**在私聊中使用 `edit` (默认) 时的效果** — 网关发送一条正常的预览消息，并通过 `editMessageText` 渐进更新，避免 Telegram 草案预览的折叠/回退效应。

**在私聊中使用 `auto` 或 `draft` 时的效果** — Telegram 显示一个动画草案预览，逐令牌更新。当回复完成时，它会作为常规消息发送，草案预览在客户端自然清除。草案没有消息 ID，所以最终的答案是留在你聊天历史中的内容。

**群组、超级群组、论坛话题呢？** Telegram 将 `sendMessageDraft` 限制在私聊中。网关会透明地为其他所有情况回退到基于编辑的路径 — 用户体验与之前相同。

**如果草案帧失败怎么办？** 任何失败（临时网络错误、服务器端拒绝、旧的 python-telegram-bot 安装）都会将该响应的其余部分切换回基于编辑的路径。下一次响应会获得新的尝试。

<a id="rendering-tables-and-link-previews"></a>
## 渲染：表格与链接预览

Telegram 的 MarkdownV2 没有原生表格语法 — 如果直接传递，管道表格会渲染成反斜杠转义的噪音。Hermes 会自动规范化 Markdown 表格：

- **小型表格** 被扁平化为 **按行分组的项目符号** — 每一行在列标题下变成一个可读的项目符号列表。适用于 2–4 列和短单元格。
- **更大或更宽的表格** 回退为 **围栏代码块**，并保持列对齐，避免内容折叠。会添加一行提示信息，让 Agent 知道在 Telegram 上更倾向于使用文本后续说明而非更多表格。

无需配置 — 适配器会根据每条消息选择合适的回退方案。如果你想要传统的“总是使用代码块”行为，可以在 `config.yaml` 中通过设置 `telegram.pretty_tables: false` 来禁用表格规范化（默认：`true`）。

**链接预览。** Telegram 会自动为 bot 消息中的 URL 生成链接预览。如果你想抑制这些预览（冗长的 `/tools` 输出、Agent 回复中提到十个链接等）：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_link_previews: true
```

当启用时，Hermes 会为每条外发消息附加 Telegram 的 `LinkPreviewOptions(is_disabled=True)`，并在较旧的 `python-telegram-bot` 版本上回退到传统的 `disable_web_page_preview` 参数。

<a id="group-allowlisting"></a>
## 群组白名单

Telegram 群组和论坛聊天有两个独立的门控配置：

- **发送者用户 ID** (`group_allow_from` / `TELEGRAM_GROUP_ALLOWED_USERS`) — 发送者级别的白名单，仅适用于群组/论坛消息。当你想让特定用户能够在群组中调用 bot，而不将他们添加到 `TELEGRAM_ALLOWED_USERS` 时（那也会授予他们私聊访问权限），使用此项。
- **聊天 ID** (`group_allowed_chats` / `TELEGRAM_GROUP_ALLOWED_CHATS`) — 聊天级别的白名单。这些群组/论坛的任何成员都可以与 bot 交互。适用于团队/支持型 bot，其中群组成员身份本身就是访问信号。

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # 全局访问权限 (私聊 + 群组)。这里的用户始终可以调用 bot。
        allow_from:
          - "123456789"
        # 仅在群组/论坛中允许的发送者 ID。**不**授予私聊访问权限。
        group_allow_from:
          - "987654321"
        # 整个群组/论坛 — 任何成员都被授权。
        group_allowed_chats:
          - "-1001234567890"
```

等效的环境变量：

```bash
TELEGRAM_ALLOWED_USERS="123456789"
TELEGRAM_GROUP_ALLOWED_USERS="987654321"
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

行为：

- `TELEGRAM_ALLOWED_USERS` 涵盖所有聊天类型（私聊、群组、论坛）。
- `TELEGRAM_GROUP_ALLOWED_USERS` 仅在群组/论坛中授权所列的发送者。除非被列入 `TELEGRAM_ALLOWED_USERS`，他们仍然不能私聊 bot。
- `TELEGRAM_GROUP_ALLOWED_CHATS` 中的聊天授权该聊天的每一个成员，无论发送者是谁。
- 在这些列表中使用 `*` 允许任何发送者/聊天。
- 这层控制叠加在现有的提及/模式触发器之上，也叠加在 `group_topics` + `ignored_threads` 之上。

<a id="migration-from-before-pr-17686"></a>
### 从 PR #17686 之前的版本迁移

在此拆分之前，`TELEGRAM_GROUP_ALLOWED_USERS` 是唯一的控制项，用户在其中放置的是 **聊天 ID**。为了向后兼容，`TELEGRAM_GROUP_ALLOWED_USERS` 中聊天 ID 形状的值（以 `-` 开头）仍被视为聊天 ID 并得到支持，但会记录一次弃用警告。迁移方法：

```bash
# 旧方式 (仍然有效，但已弃用)
TELEGRAM_GROUP_ALLOWED_USERS="-1001234567890"

# 新方式
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

<a id="guest-mention-bypass-guestmode"></a>
### 访客 @mention 绕过 (`guest_mode`)

在典型的设置中，`group_allowed_chats` 是一个硬性门控：来自该列表之外群组的消息会被静默丢弃，即使有成员明确 @mention 了 bot。这对于支持/团队型 bot 是正确的默认行为。

对于更随意的设置 — 朋友群聊中你希望 bot **大部分保持沉默** 但 **偶尔在明确提及时可用** — 启用 `guest_mode`：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        group_allowed_chats:
          - "-1001234567890"   # 你的主要白名单群组
        guest_mode: true       # 非白名单群组：仅在 @mention 时允许
```

环境变量等效：

```bash
TELEGRAM_GUEST_MODE=true
```

默认值：`false`。

当 `guest_mode: true` 时，来自非白名单群组的消息**仅在**明确 @mention bot 时才会被处理。每次交互都需要提及 — 访客交互没有会话粘性，所以 bot 永远不会在未被提及的朋友群聊线程中自动参与。

私聊和白名单群组的行为与之前完全相同。

<a id="slash-command-access-control"></a>
## 斜杠命令访问控制

默认情况下，每个允许的用户都可以运行每个斜杠命令。要将你的白名单分割为 **管理员**（拥有全部斜杠命令访问权限）和 **常规用户**（仅能运行你明确启用的命令），请在平台的 `extra` 块中添加 `allow_admin_from` 和 `user_allowed_commands`：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # 现有的白名单 (不变)
        allow_from:
          - "123456789"     # 管理员
          - "555555555"     # 常规用户
          - "777777777"     # 常规用户

        # 新增 — 管理员获得所有斜杠命令 (内置 + 插件)
        allow_admin_from:
          - "123456789"

        # 新增 — 非管理员允许的用户只能运行这些斜杠命令。
        # /help 和 /whoami 始终允许，以便用户可以查看他们的访问权限。
        user_allowed_commands:
          - status
          - model
          - history

        # 可选：为群组单独设置管理员/命令列表
        group_allow_admin_from:
          - "123456789"
        group_user_allowed_commands:
          - status
```
**行为：**

- 在某个作用域（私聊或群组）的 `allow_admin_from` 列表中的用户，可以通过实时注册表运行**所有**已注册的斜杠命令——包括内置命令和插件注册的命令。
- 在 `allow_from` 列表中但**不在** `allow_admin_from` 列表中的用户，只能运行 `user_allowed_commands` 中列出的命令，外加始终允许的基础命令：`/help` 和 `/whoami`。
- 普通聊天（非斜杠消息）不受影响。非管理员用户仍然可以正常与 Agent 对话，只是不能随意触发命令。
- **向后兼容：** 如果某个作用域未设置 `allow_admin_from`，则该作用域的斜杠命令门控将被禁用。现有安装无需更改即可继续工作。
- 私聊管理员状态不意味着群组管理员状态。每个作用域都有自己的管理员列表。
- 如果只设置了 `group_allow_admin_from`，则私聊作用域将保持无限制（向后兼容）模式。

使用 `/whoami` 查看当前作用域、你的层级（管理员 / 用户 / 无限制）以及你可以运行哪些斜杠命令。

<a id="interactive-model-picker"></a>
## 交互式模型选择器

当你在 Telegram 聊天中发送不带参数的 `/model` 命令时，Hermes 会显示一个交互式内联键盘，用于切换模型：

1.  **提供商选择** — 显示每个可用提供商及其模型数量的按钮（例如，“OpenAI (15)”、“✓ Anthropic (12)”表示当前提供商）。
2.  **模型选择** — 分页显示的模型列表，带有 **Prev**/**Next** 导航按钮、一个返回提供商的 **Back** 按钮以及 **Cancel** 按钮。

当前模型和提供商会显示在顶部。所有导航操作都是通过原地编辑同一条消息完成的（不会弄乱聊天记录）。

:::tip
如果你知道确切的模型名称，可以直接输入 `/model &lt;name&gt;` 来跳过选择器。你也可以输入 `/model &lt;name&gt; --global` 来使更改在会话间持久化。
:::

<a id="dns-over-https-fallback-ips"></a>
## DNS-over-HTTPS 备用 IP

在某些受限网络中，`api.telegram.org` 可能解析到一个无法访问的 IP 地址。Telegram 适配器包含一个**备用 IP** 机制，该机制会在保持正确的 TLS 主机名和 SNI 的同时，透明地重试连接到备用 IP。

<a id="how-it-works"></a>
### 工作原理

1.  如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2.  否则，适配器会自动通过 DNS-over-HTTPS (DoH) 查询 **Google DNS** 和 **Cloudflare DNS**，以发现 `api.telegram.org` 的备用 IP。
3.  DoH 返回的、与系统 DNS 结果不同的 IP 将被用作备用 IP。
4.  如果 DoH 也被屏蔽，则使用一个硬编码的种子 IP (`149.154.167.220`) 作为最后手段。
5.  一旦某个备用 IP 成功，它就会变得“粘性”——后续请求会直接使用它，而无需先重试主路径。

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
通常你不需要手动配置这个。通过 DoH 的自动发现机制可以处理大多数受限网络场景。只有在你的网络也屏蔽了 DoH 时，才需要设置 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::

<a id="proxy-support"></a>
## 代理支持

如果你的网络需要通过 HTTP 代理才能访问互联网（在企业环境中很常见），Telegram 适配器会自动读取标准的代理环境变量，并通过该代理路由所有连接。

<a id="supported-variables"></a>
### 支持的变量

适配器按顺序检查以下环境变量，使用第一个已设置的变量：

1.  `HTTPS_PROXY`
2.  `HTTP_PROXY`
3.  `ALL_PROXY`
4.  `https_proxy` / `http_proxy` / `all_proxy`（小写变体）

### 配置

在启动网关之前，在你的环境中设置代理：

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

或者将其添加到 `~/.hermes/.env`：

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

该代理同时适用于主传输层和所有备用 IP 传输层。无需额外的 Hermes 配置——只要设置了环境变量，就会自动使用。

:::note
这涵盖了 Hermes 用于 Telegram 连接的自定义备用传输层。其他地方使用的标准 `httpx` 客户端本身已经支持代理环境变量。
:::

<a id="message-reactions"></a>
## 消息反应

机器人可以给消息添加表情符号反应，作为视觉处理反馈：

-   👀 当机器人开始处理你的消息时
-   ✅ 当响应成功送达时
-   ❌ 如果在处理过程中发生错误

反应功能**默认是禁用的**。在 `config.yaml` 中启用：

```yaml
telegram:
  reactions: true
```

或者通过环境变量：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（反应是叠加的）不同，Telegram 的 Bot API 在一次调用中会替换所有机器人的反应。从 👀 到 ✅/❌ 的转换是原子性的——你不会同时看到两者。
:::

:::tip
如果机器人在群组中没有添加反应的权限，反应调用会静默失败，消息处理会正常继续。
:::

<a id="per-channel-prompts"></a>
## 按频道提示

为特定的 Telegram 群组或论坛主题分配临时的系统提示。该提示在每次对话轮次运行时注入——永远不会持久化到对话历史记录中——因此更改会立即生效。

```yaml
telegram:
  channel_prompts:
    "-1001234567890": |
      你是一个研究助手。专注于学术来源、引用和简洁的综述。
    "42":  |
      这个主题用于创意写作反馈。请保持热情并给出建设性意见。
```

键是聊天 ID（群组/超级群组）或论坛主题 ID。对于论坛群组，主题级别的提示会覆盖群组级别的提示：

-   在群组 `-1001234567890` 内的主题 `42` 中的消息 → 使用主题 `42` 的提示
-   在主题 `99`（没有明确条目）中的消息 → 回退到群组 `-1001234567890` 的提示
-   在没有条目的群组中的消息 → 不应用频道提示

数字类型的 YAML 键会自动规范化为字符串。

<a id="troubleshooting"></a>
## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 机器人完全不响应 | 验证 `TELEGRAM_BOT_TOKEN` 是否正确。检查 `hermes gateway` 日志中的错误。 |
| 机器人响应“未授权” | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。使用 @userinfobot 仔细检查。 |
| 机器人忽略群组消息 | 隐私模式可能已开启。禁用它（步骤 3）或将机器人设为群组管理员。**更改隐私设置后，记得移除并重新添加机器人。** |
| 语音消息未转录 | 验证 STT 是否可用：安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件，不是气泡 | 安装 `ffmpeg`（Edge TTS Opus 转换需要）。 |
| 机器人令牌被撤销/无效 | 通过 BotFather 中的 `/revoke` 然后 `/newbot` 或 `/token` 生成新令牌。更新你的 `.env` 文件。 |
| Webhook 未接收更新 | 验证 `TELEGRAM_WEBHOOK_URL` 是否可公开访问（用 `curl` 测试）。确保你的平台/反向代理将来自该 URL 端口的入站 HTTPS 流量路由到由 `TELEGRAM_WEBHOOK_PORT` 配置的本地监听端口（它们不需要是相同的数字）。确保 SSL/TLS 已启用——Telegram 只发送到 HTTPS URL。检查防火墙规则。 |

<a id="exec-approval"></a>
## 执行批准

当 Agent 尝试运行一个可能危险的命令时，它会在聊天中向你请求批准：

> ⚠️ 此命令可能具有危险性（递归删除）。回复“yes”以批准。

回复“yes”/“y”批准，或回复“no”/“n”拒绝。

<a id="interactive-prompts-clarify"></a>
## 交互式提示（澄清）

当 Agent 调用 `clarify` 工具时——例如询问你更喜欢哪种方法、获取任务后反馈或在做出非平凡决定前确认——Telegram 会使用**内联键盘按钮**来呈现问题：

> ❓ 我应该为仪表板使用哪个框架？
>
> [1. Next.js] [2. Remix] [3. Astro]
> [✏️ 其他（输入答案）]

点击按钮回答，或点击**其他**以输入自由格式的响应（你发送的下一条消息将成为答案）。开放式的 `clarify` 调用（没有预设选项）会跳过按钮，直接捕获你的下一条消息。

通过 `~/.hermes/config.yaml` 中的 `agent.clarify_timeout` 配置响应超时（默认为 `600` 秒）。如果你在超时时间内没有响应，Agent 会解除阻塞并发送一个哨兵消息，然后进行调整，而不是一直挂起。
<a id="push-notification-volume"></a>
## 推送通知音量

Telegram 会在机器人发送每条消息时触发推送通知。对于较长的 Agent 回合，如果发送了工具进度气泡、流式更新和状态回调，通知很快就会变得嘈杂。Telegram 适配器有两种通知模式：

| 模式 | 行为 |
|------|----------|
| `important` (默认) | 只有 **最终响应**、**审批提示** 和 **斜杠命令确认** 会响铃。工具进度、流式数据块和状态消息会以 `disable_notification=true` 的方式发送。 |
| `all` | 每条发出的消息都会触发推送通知。这是旧版行为；如果你确实想听到每个工具调用，可以选择启用。 |

在 `~/.hermes/config.yaml` 中配置：

```yaml
display:
  platforms:
    telegram:
      notifications: important   # 或 "all"
```

环境变量覆盖（便于快速进行 A/B 测试）：

```bash
HERMES_TELEGRAM_NOTIFICATIONS=all
```

未知的值会记录警告并回退到 `important` 模式。

<a id="security"></a>
## 安全性

:::warning
务必设置 `TELEGRAM_ALLOWED_USERS` 来限制谁可以与你的机器人交互。如果不设置，网关作为安全措施会默认拒绝所有用户。
:::

切勿公开分享你的机器人令牌。如果令牌泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。

更多详细信息，请参阅 [安全性文档](/user-guide/security)。你也可以使用 [DM 配对](/user-guide/messaging#dm-pairing-alternative-to-allowlists) 来实现更动态的用户授权方式。
