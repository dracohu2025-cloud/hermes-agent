---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

<a id="telegram-setup"></a>
# Telegram 设置

Hermes Agent 以全功能对话机器人的方式与 Telegram 集成。连接后，你可以从任何设备与你的 Agent 聊天、发送会被自动转写的语音消息、接收定时任务结果，以及在群聊中使用 Agent。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/)，支持文本、语音、图片和文件附件。

<a id="step-1-create-a-bot-via-botfather"></a>
## 步骤 1：通过 BotFather 创建机器人

每个 Telegram 机器人都需要由 Telegram 官方机器人管理工具 [@BotFather](https://t.me/BotFather) 颁发的 API 令牌。

1. 打开 Telegram，搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 选择一个**显示名称**（例如 "Hermes Agent"）—— 可以任意填写
4. 选择一个**用户名** —— 必须唯一且以 `bot` 结尾（例如 `my_hermes_bot`）
5. BotFather 会回复你的 **API 令牌**。它看起来像这样：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请保管好你的机器人令牌。任何拥有此令牌的人都能控制你的机器人。如果泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。
:::

<a id="step-2-customize-your-bot-optional"></a>
## 步骤 2：自定义你的机器人（可选）

以下 BotFather 命令可以改善用户体验。向 @BotFather 发送消息并使用：

| 命令 | 用途 |
|------|------|
| `/setdescription` | 用户开始聊天前显示的“这个机器人能做什么？”文本 |
| `/setabouttext` | 机器人资料页上的简短介绍 |
| `/setuserpic` | 为机器上传头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否能看到所有群聊消息（见步骤 3） |

:::tip
对于 `/setcommands`，一个实用的初始集合：

```
help - 显示帮助信息
new - 开始新对话
sethome - 将此聊天设置为家庭频道
```
:::

<a id="step-3-privacy-mode-critical-for-groups"></a>
## 步骤 3：隐私模式（群聊关键）

Telegram 机器人有一个**默认开启的隐私模式**。这是在群聊中使用机器人时最常见的困惑来源。

**启用隐私模式时**，你的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自己消息的回复
- 服务消息（成员加入/离开、置顶消息等）
- 机器人作为管理员的频道中的消息

**关闭隐私模式时**，机器人能收到群聊中的每一条消息。

<a id="how-to-disable-privacy-mode"></a>
### 如何关闭隐私模式

1. 向 **@BotFather** 发送消息
2. 发送 `/mybots`
3. 选择你的机器人
4. 进入 **Bot Settings → Group Privacy → Turn off**

:::warning
**更改隐私设置后，必须将机器人从所有群聊中移除并重新添加**。Telegram 会在机器人加入群聊时缓存隐私状态，除非移除并重新添加机器人，否则不会更新。
:::

:::tip
关闭隐私模式的另一种方法是：将机器人提升为**群管理员**。管理员机器人无论隐私设置如何都能接收所有消息，这样可以避免切换全局隐私模式。
:::

<a id="step-4-find-your-user-id"></a>
## 步骤 4：找到你的用户 ID

Hermes Agent 使用数字形式的 Telegram 用户 ID 来控制访问。你的用户 ID **不是** 你的用户名 —— 它是一个像 `123456789` 这样的数字。
**方法1（推荐）：** 向 [@userinfobot](https://t.me/userinfobot) 发送消息 —— 它会立即回复你的用户 ID。  
**方法2：** 向 [@get_id_bot](https://t.me/get_id_bot) 发送消息 —— 另一个可靠的选择。

保存这个号码；下一步会用到。

<a id="step-5-configure-hermes"></a>
## 第5步：配置 Hermes

<a id="option-a-interactive-setup-recommended"></a>
### 选项A：交互式设置（推荐）

```bash
hermes gateway setup
```

根据提示选择 **Telegram**。向导会询问你的机器人令牌和允许的用户ID，然后自动写入配置。

<a id="option-b-manual-configuration"></a>
### 选项B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # Comma-separated for multiple users
```

<a id="start-the-gateway"></a>
### 启动网关

```bash
hermes gateway
```

机器人应在数秒内上线。在 Telegram 上给它发条消息以验证。

<a id="sending-generated-files-from-docker-backed-terminals"></a>
## 从 Docker 支撑的终端发送生成的文件

如果你的终端后端是 `docker`，请注意 Telegram 附件是由 **gateway 进程** 发送的，而不是从容器内部发送的。这意味着最终的 `MEDIA:/...` 路径必须在运行 gateway 的主机上可读。

常见陷阱：

- Agent 在 Docker 内部将文件写入 `/workspace/report.txt`
- 模型输出 `MEDIA:/workspace/report.txt`
- Telegram 投递失败，因为 `/workspace/report.txt` 仅存在于容器内部，不在主机上

推荐模式：

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/.hermes/cache/documents:/output"
```

然后：

- 在 Docker 内部将文件写入 `/output/...`
- 在 `MEDIA:` 中输出 **主机可见** 路径，例如：  
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`

如果你已经有 `docker_volumes:` 部分，将新的挂载添加到同一个列表中。YAML 重复键会静默覆盖前面的。

<a id="supported-media-file-extensions"></a>
### 支持的 `MEDIA:` 文件扩展名

Gateway 从 Agent 回复中提取 `MEDIA:/path/to/file` 标签，并将引用的文件作为平台原生附件发送。所有 gateway 平台支持的扩展名：

| 分类 | 扩展名 |
|---|---|
| 图片 | `png`, `jpg`, `jpeg`, `gif`, `webp`, `bmp`, `tiff`, `svg` |
| 音频 | `mp3`, `wav`, `ogg`, `m4a`, `opus`, `flac`, `aac` |
| 视频 | `mp4`, `mov`, `webm`, `mkv`, `avi` |
| **文档** | `pdf`, `txt`, `md`, `csv`, `json`, `xml`, `html`, `yaml`, `yml`, `log` |
| **办公** | `docx`, `xlsx`, `pptx`, `odt`, `ods`, `odp` |
| **压缩包** | `zip`, `rar`, `7z`, `tar`, `gz`, `bz2` |
| **电子书/安装包** | `epub`, `apk`, `ipa` |

此列表中的所有内容在支持原生附件的平台（Telegram、Discord、Signal、Slack、WhatsApp、飞书、Matrix 等）上都会作为原生附件发送；在不支持原生附件的平台上，则回退为链接或纯文本指示。**加粗**分类是在最近几个版本中添加的 —— 如果你之前依赖模型输出 `here is the file: /path/to/report.docx` 这样的文本，请改用 `MEDIA:/path/to/report.docx` 以获取原生投递。

<a id="webhook-mode"></a>
## Webhook 模式
默认情况下，Hermes 使用**长轮询**连接 Telegram——网关会向 Telegram 的服务器发出出站请求以获取新的更新。这种方式适用于本地和始终在线的部署。

对于**云部署**（Fly.io、Railway、Render 等），**Webhook 模式**更具成本效益。这些平台可以在入站 HTTP 流量到来时自动唤醒已休眠的机器，但无法通过出站连接唤醒。由于轮询是出站的，轮询机器人永远无法休眠。Webhook 模式颠倒了方向——Telegram 将更新推送到你的机器人的 HTTPS URL，从而支持空闲时休眠的部署。

| | 轮询（默认） | Webhook |
|---|---|---|
| 方向 | 网关 → Telegram（出站） | Telegram → 网关（入站） |
| 最适用于 | 本地、始终在线的服务器 | 支持自动唤醒的云平台 |
| 配置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲成本 | 机器必须保持运行 | 机器可在消息间隔期间休眠 |

<a id="configuration"></a>
### 配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
TELEGRAM_WEBHOOK_SECRET="$(openssl rand -hex 32)"  # 必填
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认 8443
```

| 变量 | 必填 | 说明 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 用于发送更新的公共 HTTPS URL。URL 路径会自动提取（例如上例中的 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | **是**（当设置了 `TELEGRAM_WEBHOOK_URL` 时） | 用于验证的密钥令牌，Telegram 会在每个 webhook 请求中回传此令牌。没有此令牌网关将拒绝启动——参见 [GHSA-3vpc-7q5r-276h](https://github.com/NousResearch/hermes-agent/security/advisories/GHSA-3vpc-7q5r-276h)。使用 `openssl rand -hex 32` 生成。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | Webhook 服务器监听的本地端口（默认值：`8443`）。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关会启动一个 HTTP webhook 服务器而非使用轮询。当未设置时，使用轮询模式——行为与之前版本相同。

<a id="cloud-deployment-example-fly-io"></a>
### 云部署示例（Fly.io）

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

<a id="proxy-support"></a>
## 代理支持

如果 Telegram 的 API 被屏蔽，或者你需要通过代理路由流量，可以设置一个专用于 Telegram 的代理 URL。该设置优先于通用的 `HTTPS_PROXY` / `HTTP_PROXY` 环境变量。

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
代理同时适用于主 Telegram 连接和备选 IP 传输。如果没有设置特定 Telegram 的代理，网关会回退到 `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY`（或 macOS 系统代理自动检测）。

<a id="home-channel"></a>
## 主频道

在任意 Telegram 聊天（私聊或群组）中使用 `/sethome` 命令，将其设为**主频道**。定时任务（cron job）的结果会投递到该频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="我的笔记"
```

:::tip
群组聊天 ID 为负数（例如 `-1001234567890`）。你的个人私聊聊天 ID 与用户 ID 相同。
:::

<a id="cron-deliveries-in-topic-mode"></a>
### 话题模式下的定时任务投递

如果你在机器人私聊中启用了话题模式，定时任务消息投递到根聊天时，会落在系统专用大厅——在那里回复不会开启会话，你会看到“主聊天保留给系统命令”的提示。创建一个专门的论坛话题（例如 `Cron`），然后设置：

```bash
TELEGRAM_CRON_THREAD_ID=<话题线程ID>
```

`TELEGRAM_CRON_THREAD_ID` 仅对定时任务投递覆盖 `TELEGRAM_HOME_CHANNEL_THREAD_ID`。在该话题中回复会继续该话题现有的会话。

<a id="voice-messages"></a>
## 语音消息

<a id="incoming-voice-speech-to-text"></a>
### 接收语音（语音转文字）

你在 Telegram 上发送的语音消息会被 Hermes 配置的 STT 提供程序自动转写，并以文本形式注入到对话中。

- `local` 使用运行 Hermes 机器上的 `faster-whisper`——无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

<a id="skipping-stt-pass-the-raw-audio-file-to-the-agent"></a>
#### 跳过 STT：将原始音频文件传给 Agent

如果你希望**Agent 自己**处理音频——例如用于说话人分离、自定义转写工具，或者只是存档录音——请在 `~/.hermes/config.yaml` 中设置 `stt.enabled: false`：

```yaml
stt:
  enabled: false
```

STT 禁用后，网关仍会将语音/音频附件下载到 Hermes 的音频缓存中，但**不会对其进行转写**。Agent 会收到类似以下标记的消息：

```
[用户发送了一条语音消息：/home/<user>/.hermes/cache/audio/<hash>.ogg]
```

你的工具或技能可以直接读取该路径（例如，将其交给本地的说话人分离流水线、更强大的转写模型，或上传到长期存储）。文件扩展名反映了 Telegram 传递的原始格式（语音笔记为 `.ogg`，音频附件为 `.mp3`/`.m4a` 等）。

这种方式与下面的[本地 Bot API 服务器](#large-files-20mb--via-local-bot-api-server)部分自然结合，后者将 Telegram 的 20MB getFile 上限提升到 2GB——当你需要处理的录音时长超过几分钟时非常有用。

<a id="outgoing-voice-text-to-speech"></a>
### 发送语音（文字转语音）

当 Agent 通过 TTS 生成音频时，会以原生 Telegram **语音气泡**（圆形、可内联播放的那种）形式投递。

- **OpenAI 和 ElevenLabs** 原生输出 Opus——无需额外设置
- **Edge TTS**（默认免费提供程序）输出 MP3，需要 **ffmpeg** 将其转换为 Opus：
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

没有 ffmpeg 的情况下，Edge TTS 音频会以普通音频文件的形式发送（仍可播放，但使用矩形播放器而非气泡样式）。

在 `config.yaml` 的 `tts.provider` 键下配置 TTS 提供程序。

<a id="large-files-20mb-via-local-bot-api-server"></a>
## 大文件（>20MB）通过本地 Bot API 服务器

Telegram 的 **公开** Bot API 将 `getFile` 下载限制在 **20 MB**，因此任何超过该大小的语音消息、音频文件、视频或文档都会被 Hermes 静默拒绝，并回复 "too large"。官方文档给出的解决方法是运行一个 **本地** [telegram-bot-api](https://github.com/tdlib/telegram-bot-api) 守护进程——它与 Telegram 使用的服务器软件相同，但运行在你的网络上。本地服务器将文件上限提高到 **2 GB**，当 Hermes 检测到配置了自定义 `base_url` 时，它会自动调高内部限制。

这解锁了如下工作流：

- 向机器人发送长语音备忘录（45分钟的会议、播客等）
- 上传用于视觉工具处理的大视频
- 归档原始音频，用于离线流水线，如说话人分离、对齐或训练数据

<a id="step-1-obtain-telegram-api-credentials"></a>
### 第 1 步：获取 Telegram API 凭证

本地服务器直接与 Telegram 的 MTProto 层通信（而非公开 Bot API），因此它需要 **MTProto 凭证**：

1. 访问 [my.telegram.org/apps](https://my.telegram.org/apps)，使用你的 Telegram 账户登录。
2. 创建一个新应用（任意名称和简短描述均可）。
3. 复制 `api_id` 和 `api_hash`——两者都需要。

<a id="step-2-run-the-telegram-bot-api-server"></a>
### 第 2 步：运行 telegram-bot-api 服务器

社区维护的 [`aiogram/telegram-bot-api`](https://hub.docker.com/r/aiogram/telegram-bot-api) Docker 镜像是最简单的方式。一个极简的 `docker-compose.yaml`（使用 `--local` 模式启用更高的限制）：

```yaml
services:
  tg-bot-api:
    image: aiogram/telegram-bot-api:latest
    container_name: tg-bot-api
    restart: unless-stopped
    ports:
      - "127.0.0.1:8081:8081"   # 仅绑定到回环地址；参见安全说明
    environment:
      TELEGRAM_API_ID: "12345"           # 第 1 步中获取的 api_id
      TELEGRAM_API_HASH: "abcdef..."     # 第 1 步中获取的 api_hash
      TELEGRAM_LOCAL: "1"                # 启用 --local 模式（将 20MB 提升至 2GB）
    volumes:
      - ./tg-bot-api-data:/var/lib/telegram-bot-api
```

启动它：

```bash
docker compose up -d tg-bot-api
docker logs --tail 20 tg-bot-api
```

:::warning 安全警告
<a id="security"></a>
本地 Bot API 服务器在 URL 路径中接收你的机器人令牌（例如 `/bot&lt;TOKEN&gt;/getMe`），**且无需额外认证**。任何能访问该端口的人都可以完全控制你的机器人——读取它能看到的每条消息、以机器人身份发送消息等。请将容器绑定到 `127.0.0.1`，和/或在私有网络前使用反向代理。**切勿将端口 8081 暴露给公共互联网。**
:::

<a id="step-3-log-the-bot-out-of-the-public-api-one-time"></a>
### 第 3 步：将机器人从公开 API 注销（一次性操作）

一个机器人一次只能在一个 Bot API 服务器上保持活跃。如果机器人已经在 `api.telegram.org` 上运行（这几乎是肯定的），你必须先显式将其从那里注销，然后本地服务器才能接受它：
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/logOut"
# 预期响应：{"ok":true,"result":true}
```

这是一次性的迁移步骤——每次重启时不需要重复执行。Telegram 会将 `logOut` 之后收到的所有消息通过新服务器投递。

确认本地服务器能够代表该 Bot 与 Telegram 通信：

```bash
curl "http://127.0.0.1:8081/bot<YOUR_BOT_TOKEN>/getMe"
# 预期响应：{"ok":true,"result":{"id":...,"is_bot":true,...}}
```

<a id="step-4-point-hermes-at-the-local-server"></a>
### 第 4 步：将 Hermes 指向本地服务器

在 `~/.hermes/config.yaml` 的 `platforms.telegram.extra` 下添加以下 URL：

```yaml
platforms:
  telegram:
    extra:
      base_url: "http://127.0.0.1:8081/bot"
      base_file_url: "http://127.0.0.1:8081/file/bot"
      local_mode: true        # 参见下面的第 5 步——仅当 Hermes 进程可读取 Bot 的数据目录时才设置此项
```

:::caution 使用 `platforms.telegram.extra`，而非 `telegram.extra`
<a id="use-platforms-telegram-extra-not-telegram-extra"></a>
目前只有 `platforms.&lt;name&gt;.extra` 这种形式才会被深度合并到平台配置中。直接放置在最顶层 `telegram.extra` 块下的键会被静默丢弃。
:::

当设置了 `base_url` 时，Hermes 将：

- 基于本地服务器构建 python-telegram-bot 客户端
- 自动将其内部的文档/音频大小限制从 20 MB 提升至 2 GB
- 在“文件过大”的错误消息中报告当前限制（`最大：2048 MB`），让您能清楚知道当前处于哪种模式

重启网关并查看确认日志行：

```bash
hermes gateway restart
grep -E "Using custom Telegram base_url|Using Telegram local_mode" ~/.hermes/logs/gateway.log | tail
```

<a id="step-5-localmode-file-access-on-disk"></a>
### 第 5 步：`local_mode` —— 从磁盘访问文件

本地服务器提供文件的 **两种方式**：

1. **不带 `--local`**（默认）：文件通过 HTTP 在 `/file/bot&lt;TOKEN&gt;/&lt;path&gt;` 提供，与公共 Bot API 相同。20 MB 上限仍然有效。仅作为网络修复时有用（例如 `api.telegram.org` 不可达但可以自托管时）；如果要突破大小限制，这不是您要的。
2. **带 `--local`**（通过上面的 `TELEGRAM_LOCAL=1` 设置）：文件写入服务器的文件系统，`getFile` 返回的是 **绝对路径** 而非 HTTP URL。20 MB 上限被解除。此时 Hermes 必须 **从磁盘** 读取字节，而不是通过 HTTP。

要使磁盘读取路径生效，请在上方配置中设置 `local_mode: true`，**并**确保 Hermes 进程可以读取服务器返回的路径。有两种场景：

- **同一台机器** —— telegram-bot-api 和 Hermes 运行在同一主机上。将数据卷绑定挂载到 Hermes 可读的目录（例如 `/var/lib/telegram-bot-api`），并确保文件所有权匹配。容器会降权为其内部的 `telegram-bot-api` 用户（UID 因镜像而异）；最简单的修复方式是在 compose 服务中添加 `user: "&lt;UID&gt;:&lt;GID&gt;"`，使文件的所有权与 Hermes 运行时的 UID 一致。
- **不同机器** —— Bot 服务器运行在一台主机上（例如 NAS、单独的虚拟机），Hermes 在另一台主机上。服务器的数据目录必须通过 **与服务器报告的绝对路径相同**（通常是 `/var/lib/telegram-bot-api`）的方式共享给 Hermes 机器。NFS 对此效果很好；如果您不想处理文件系统级别的 UID 不匹配，CIFS/SMB 配合 `uid=` 挂载重映射会更友好。
如果设置了 `local_mode: true`，但 Hermes 无法 `stat` 返回的文件路径（权限或挂载问题），python-telegram-bot 会静默回退到向本地服务器发起 HTTP `getFile` 请求——而在 `--local` 模式下，本地服务器会响应 `404 Not Found`。该症状会出现在 `gateway.log` 中：

```
[Telegram] Failed to cache voice: Not Found
telegram.error.InvalidToken: Not Found
```

如果看到这个错误，说明能力提升（cap-lift）生效了，但文件共享（file-share）没有。在 Hermes 宿主上，用 gateway 运行时的用户身份执行 `ls -la /var/lib/telegram-bot-api/&lt;TOKEN&gt;/voice/`，并确认单个文件可以用 `cat` 查看，且无权限错误。

<a id="step-6-test-it"></a>
### 步骤 6：测试

给机器人发送一条大于 20 MB 的语音消息或音频文件。实时查看 gateway 日志：

```bash
tail -f ~/.hermes/logs/gateway.log | grep -iE "telegram|cache"
```

你应该会看到类似 `[Telegram] Cached user voice at /home/&lt;user&gt;/.hermes/cache/audio/...` 这样的日志行，并且**没有** "too large" 的拒绝信息。结合上面的 `stt.enabled: false`，原始音频文件的路径会进入 Agent 的入站消息，用于后续处理。

<a id="group-chat-usage"></a>
## 群聊使用

Hermes Agent 在 Telegram 群聊中工作时，需要注意以下几点：

- **隐私模式**决定了机器人能看到哪些消息（参见[步骤 3](#step-3-privacy-mode-critical-for-groups)）
- `TELEGRAM_ALLOWED_USERS` 仍然适用——即使在群聊中，也只有授权用户才能触发机器人
- 你可以通过设置 `telegram.require_mention: true` 来阻止机器人响应普通的群聊消息
- 当 `telegram.require_mention: true` 时，群聊消息在以下情况下会被接受：
  - 是对机器人某条消息的回复
  - 提及了 `@botusername`
  - 使用了 `/command@botusername`（Telegram 的机器人菜单命令格式，包含机器人名称）
  - 与你在 `telegram.mention_patterns` 中配置的某个正则唤醒词匹配
- 在有多个 Hermes 机器人的群组中，`telegram.exclusive_bot_mentions` 可以保持路由确定性。当一条消息明确提及一个或多个 Telegram 机器人用户名时，只有被提及的 bot 配置文件会处理它；其他 Hermes 机器人在执行回复和唤醒词回退之前就会忽略该消息。此选项默认启用。
- 使用 `telegram.ignored_threads` 可以让 Hermes 在特定的 Telegram 论坛主题中保持静默，即使该群组在其他情况下允许自由回复或提及触发的回复
- 如果 `telegram.require_mention` 未设置或设为 false，Hermes 会保持原有的开放群组行为，并响应它能看到的普通群消息

<a id="multiple-hermes-bots-in-one-group"></a>
### 一个群组中有多个 Hermes 机器人

如果你在同一个 Telegram 群组中运行多个 Hermes 配置文件，请为每个配置文件创建一个 Telegram bot token，并为每个配置文件启动一个 gateway。不要在多个运行中的 gateway 里重复使用同一个 bot token；Telegram 会拒绝同一 token 的并发轮询。

推荐的群组配置：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns: []
```

使用此配置后，类似 `@research_bot @ops_bot summarize this` 这样的群聊消息将仅由 `research_bot` 和 `ops_bot` 处理。群组中的其他 Hermes 机器人保持静默，即使该消息是对其中某个机器人早期消息的回复，或者其他情况下会匹配共享的唤醒词。
仅在显式提及不应覆盖回复和唤醒词触发的遗留群组中，才将 `exclusive_bot_mentions` 设为 `false`。

要操作多个配置文件，请为每个配置文件运行一次 gateway 命令。例如：

```bash
# default profile
hermes gateway start
hermes gateway status
hermes gateway stop

# named profiles
hermes -p research gateway start
hermes -p research gateway status
hermes -p research gateway stop
```

对于小型固定设备群，使用 shell 循环或脚本来为默认配置文件调用 `hermes gateway &lt;action&gt;`，并为每个命名配置文件调用 `hermes -p &lt;profile&gt; gateway &lt;action&gt;`。这比假设单个进程级命令能在所有服务管理器上控制每个命名配置文件要更可靠。

<a id="troubleshooting-works-in-dms-but-not-groups"></a>
### 故障排除：在私聊中有效，但在群组中无效

如果机器人在私聊中能回复，但在群组中保持静默，请按顺序检查以下门控：

1. **Telegram 投递：** 关闭 BotFather 的隐私模式，将机器人提升为管理员，或直接提及机器人。Hermes 无法响应用户从未投递给机器人的群组消息。
2. **更改隐私后重新加入：** 从群组中移除机器人，在更改 BotFather 隐私设置后重新添加。Telegram 可能对现有成员保留旧的投递行为。
3. **Hermes 授权：** 确保发送者被列入 `TELEGRAM_ALLOWED_USERS` 或 `TELEGRAM_GROUP_ALLOWED_USERS`，或者通过 `TELEGRAM_GROUP_ALLOWED_CHATS` 允许该群聊。
4. **提及过滤器：** 如果设置了 `telegram.require_mention: true`，则常规群组闲聊会被忽略，除非消息是斜杠命令、回复机器人、`@botusername` 提及，或与配置的 `mention_patterns` 匹配。
5. **多机器人路由：** 如果群组中包含多个机器人，请确保每个 Hermes 配置文件使用唯一的机器人 token，并保持 `exclusive_bot_mentions` 启用，除非你故意想要传统的共享触发行为。

负数的聊天 ID 对于 Telegram 群组和超级群组是正常的。如果你使用聊天范围授权，请将这些 ID 放入 `TELEGRAM_GROUP_ALLOWED_CHATS` 中，而不是发送者用户白名单。

<a id="example-group-trigger-configuration"></a>
### 示例群组触发配置

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

此示例允许所有常见的直接触发，以及以 `chompy` 开头的消息，即使它们没有使用 `@mention`。
在提及和自由响应检查运行之前，会始终忽略 Telegram 话题 `31` 和 `42` 中的消息。

<a id="notes-on-mentionpatterns"></a>
### 关于 `mention_patterns` 的说明

- 模式使用 Python 正则表达式
- 匹配时不区分大小写
- 模式会同时检查文本消息和媒体说明
- 无效的正则表达式模式会被忽略，并在 gateway 日志中显示警告，而不会导致机器人崩溃
- 如果你希望模式仅在消息开头匹配，请使用 `^` 锚定

<a id="private-chat-topics-bot-api-9-4"></a>
## 私聊话题（Bot API 9.4） {#private-chat-topics-bot-api-94}

Telegram Bot API 9.4（2026年2月）引入了**私聊话题（Private Chat Topics）**——机器人可以直接在 1 对 1 私聊中创建论坛式话题线程，无需超级群组。这样你就可以在现有的与 Hermes 的私聊中运行多个独立的工作空间。
<a id="use-case"></a>
### 使用场景

如果你同时参与多个长期项目，话题能让每个项目的上下文保持独立：

- **话题“网站”** — 处理你的线上 Web 服务
- **话题“研究”** — 文献综述与论文探索
- **话题“通用”** — 杂项任务与快速提问

每个话题拥有独立的对话会话、历史记录和上下文，完全与其他话题隔离。

<a id="configuration"></a>
### 配置

:::caution 前提条件
在将话题添加到配置之前，用户必须**在机器人的私聊中启用话题模式**：

<a id="prerequisites"></a>
1. 在 Telegram 中打开与 Hermes 机器人的私聊
2. 点击顶部的机器人名称，进入聊天信息页面
3. 启用**话题**（将聊天切换为论坛模式的开关）

如果没有启用，Hermes 会在启动时记录 `The chat is not a forum` 并跳过话题创建。这是 Telegram 客户端侧的设置，机器人无法通过编程方式启用。
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
          skill: arxiv              # 在该话题中自动加载技能
```

**字段说明：**

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 话题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 话题图标的自定义表情 ID |
| `skill` | 否 | 在该话题中新建会话时自动加载的技能 |
| `thread_id` | 否 | 话题创建后自动填充，请勿手动设置 |

<a id="how-it-works"></a>
### 工作原理

1. 网关启动时，Hermes 对每个尚未拥有 `thread_id` 的话题调用 `createForumTopic`
2. `thread_id` 会自动写回 `config.yaml`，后续重启跳过该 API 调用
3. 每个话题映射到一个独立的会话密钥：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4. 每个话题内的消息拥有自己的对话历史、内存刷新和上下文窗口

<a id="root-dm-handling"></a>
### 根私聊处理

默认情况下，发送到根私聊（话题之外）的消息会正常处理。设置 `ignore_root_dm: true` 可将根私聊变为大厅模式——对于已配置 DM 话题的用户，普通消息会被静默忽略，而系统命令（`/start`、`/help`、`/status` 等）仍然有效。

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

该检查是**按聊天进行的**：只有那些在 `dm_topics` 中至少有一条记录的用户，其根私聊才会被影响。没有配置话题的用户不受影响。

<a id="skill-binding"></a>
### 技能绑定

带有 `skill` 字段的话题会在该话题中启动新会话时自动加载对应技能。这与在对话开始时输入 `/skill-name` 效果相同——技能内容会被注入到第一条消息中，后续消息能在对话历史中看到它。
例如，一个带有 `skill: arxiv` 的主题会在其会话重置时（由于空闲超时、每日重置或手动 `/reset`）预加载 arxiv 技能。

:::tip
配置之外创建的主题（例如，通过手动调用 Telegram API）会在收到 `forum_topic_created` 服务消息时自动发现。你也可以在网关运行时向配置中添加主题——它们会在下一次缓存未命中时被捕获。
:::

<a id="multi-session-dm-mode-topic"></a>
## 多会话 DM 模式（`/topic`）

ChatGPT 风格的多会话 DM——一个机器人，多个并行对话。与上面由操作员管理的 `extra.dm_topics` 不同，此模式是**用户驱动的**：无需配置，无需预先声明主题名称。最终用户通过 `/topic` 开启它，然后点击 Telegram **+** 按钮创建任意数量的主题，每个主题都是一个完全独立的 Hermes 会话。

<a id="topic-subcommands"></a>
### `/topic` 子命令

| 形式 | 上下文 | 效果 |
|------|--------|------|
| `/topic` | 根 DM，尚未启用 | 检查 BotFather 能力，启用多会话模式，创建固定的系统主题 |
| `/topic` | 根 DM，已启用 | 显示状态：可恢复的未链接会话 |
| `/topic` | 在主题内部 | 显示当前主题的会话绑定 |
| `/topic help` | 任意位置 | 内联用法 |
| `/topic off` | 根 DM | 禁用多会话模式并清除该聊天的所有主题绑定 |
| `/topic &lt;session-id&gt;` | 在主题内部 | 将之前的 Telegram 会话恢复到当前主题 |

只有授权用户（通过 `TELEGRAM_ALLOWED_USERS` / 平台认证配置的白名单）才能运行 `/topic`。未授权的发送者会收到拒绝消息而非激活。

<a id="dm-topics-vs-multi-session-dm-mode"></a>
### DM 主题 vs 多会话 DM 模式

| | `extra.dm_topics`（配置驱动） | `/topic`（用户驱动） |
|---|---|---|
| 谁激活它 | 操作员，在 `config.yaml` 中 | 最终用户，通过发送 `/topic` |
| 主题列表 | 配置中声明的固定集合 | 用户自由创建/删除主题 |
| 主题名称 | 由操作员选择 | 由用户选择；自动重命名为匹配 Hermes 会话标题 |
| 根 DM 行为 | 普通聊天（若 `ignore_root_dm: true` 则为大厅） | 变为系统大厅（拒绝非命令消息） |
| 主要用例 | 带有可选技能绑定的永久工作区 | 临时并行会话 |
| 持久化 | 配置中的 `extra.dm_topics` | `telegram_dm_topic_mode` + `telegram_dm_topic_bindings` SQLite 表 |

这两个功能可以在同一个机器人上共存——你可以在用户的 DM 中运行 `/topic`，而 `extra.dm_topics` 继续管理其他聊天的操作员声明主题。

<a id="prerequisites"></a>
### 先决条件

在 **@BotFather** 中，打开你的机器人 → **Bot Settings → Threads Settings**：

1. 打开 **Threaded Mode**（启用 `has_topics_enabled`）
2. **不要**禁止用户创建主题（保持 `allows_users_to_create_topics` 开启）

当用户首次运行 `/topic` 时，Hermes 会调用 `getMe` 验证这两个标志。如果任何一个关闭，Hermes 会发送 BotFather 线程设置页面的截图，并说明需要切换哪些选项——在满足先决条件之前不会激活。
<a id="activation-flow"></a>
### 激活流程

在根 DM 中发送：

```
/topic
```

Hermes 将：

1. 检查 `getMe().has_topics_enabled` 和 `allows_users_to_create_topics`
2. 如果两者都为 true，则为该 DM 启用多会话话题模式
3. 创建并置顶一个 **系统** 话题，用于状态 / 命令（尽力而为）
4. 回复一个列表，列出用户之前未关联的 Telegram 会话，可供用户恢复

激活后，**根 DM 成为一个大厅**：正常提示会被拒绝，并给出指向 **所有消息** 的引导。系统命令（`/status`、`/sessions`、`/usage`、`/help` 等）在根 DM 中仍然有效。

<a id="creating-a-new-topic-end-user-flow"></a>
### 创建新话题（最终用户流程）

1. 在 Telegram 中打开机器人 DM
2. 点击机器人界面顶部的 **所有消息**，然后发送任意消息
3. Telegram 为该消息创建一个新话题
4. Hermes 在该话题内回复——该话题现在成为一个独立的会话

每个话题都有自己独立的对话历史、模型状态、工具执行和会话 ID。隔离键为 `agent:main:telegram:dm:{chat_id}:{thread_id}`——与配置驱动的 DM 话题隔离方式相同。

<a id="auto-renamed-topics"></a>
### 自动重命名话题

当 Hermes 为某个话题生成会话标题时（通过自动标题管道，在第一次交互之后），Telegram 话题本身也会被重命名以匹配——例如，"New Topic" 变成 "Database migration plan"。重命名是尽力而为的：失败会被记录日志，但不会中断会话。

要禁用此功能并保持手动选择的话题名称不变，请设置：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_topic_auto_rename: true
```

当此标志开启时，Hermes 仍会生成内部会话标题（用于 `hermes sessions`、TUI 等），但不会编辑 Telegram 话题名称。当你手动在 BotFather 线程模式下组织话题，并且不希望每次第一次回复都覆盖标题时，这很有用。

<a id="new-inside-a-topic"></a>
### 话题内的 `/new`

重置当前话题的会话（新会话 ID、全新历史记录），而不影响其他话题。Hermes 会回复一条提示：对于并行工作，通常应该通过 **所有消息** 创建另一个话题。

<a id="restoring-a-previous-session"></a>
### 恢复之前的会话

在话题内发送：

```
/topic <session-id>
```

这会将当前话题绑定到一个现有的 Hermes 会话，而不是从头开始。对于继续在话题模式启用之前开始的对话很有用。限制条件：

- 目标会话必须属于同一个 Telegram 用户
- 目标会话必须尚未绑定到其他话题

Hermes 会确认会话标题并重放最后一条助手消息以提供上下文。

要查找会话 ID，请在根 DM 中发送 `/topic`（无参数）——Hermes 会列出该用户未关联的 Telegram 会话。

<a id="topic-inside-a-topic-no-argument"></a>
### 话题内的 `/topic`（无参数）

显示当前话题的绑定：会话标题、会话 ID，以及关于 `/new` 与创建另一个话题的提示。

<a id="under-the-hood"></a>
### 底层原理

- 激活持久化到 `state.db` 中的 `telegram_dm_topic_mode(chat_id, user_id, enabled, ...)`
- 每个话题绑定持久化到 `telegram_dm_topic_bindings(chat_id, thread_id, session_id, ...)`，其中 `session_id` 上设置了 `ON DELETE CASCADE`——删除会话会自动清除其话题绑定
- 话题模式的 SQLite 迁移是 **选择性加入** 的：它在第一次调用 `/topic` 时运行，不会在网关启动时运行。直到用户在此配置文件中运行 `/topic`，`state.db` 才会发生变化
- 每个入站 DM 消息都会查找其 `(chat_id, thread_id)` 绑定。如果存在绑定，则通过 `SessionStore.switch_session()` 将消息路由到绑定的会话，使得会话键到会话 ID 的映射在磁盘上保持一致
- 话题内的 `/new` 会重写绑定行，指向新的会话 ID，因此下一条消息将保留在新会话中
- 在 `extra.dm_topics` 中声明的话题 **永远不会自动重命名**——即使启用了多会话模式，操作员选择的名称也会保留
- 设置 `extra.disable_topic_auto_rename: true` 可以关闭聊天中 **所有** 话题的自动重命名（包括通过线程模式创建的临时话题）
- 在支持论坛的 DM 中，置顶的 General（通用）话题被视为根大厅，无论 Telegram 传递其消息时是使用 `message_thread_id=1` 还是没有 thread_id
- 根大厅提醒消息的速率限制为每个聊天每 30 秒一条——如果用户忘记已启用话题模式并在根大厅中输入了十条提示，不会收到十条回复
- BotFather 设置截图的速率限制为每个聊天每 5 分钟发送一次——在线程设置仍被禁用时重复尝试 `/topic` 不会再次上传同一张图片
- 在话题内启动的 `/background &lt;prompt&gt;` 会将其结果送回同一话题；后台会话不会触发所属话题的自动重命名
- `/topic` 本身受机器人用户授权检查的约束——未授权的 DM 会收到拒绝消息，而不是激活
<a id="disabling-multi-session-mode"></a>
### 禁用多会话模式

在根 DM 中发送 `/topic off`。Hermes 会关闭该行的启用状态，清除聊天中的 `(thread_id → session_id)` 绑定，根 DM 恢复为普通的 Hermes 聊天。Telegram 中已有的话题（Topics）不会被删除——只是不再作为独立会话进行管控。稍后重新运行 `/topic` 即可再次开启。

如果需要手动清理（例如对多个聊天进行批量重置），可直接删除对应行：

```bash
sqlite3 ~/.hermes/state.db \
  "UPDATE telegram_dm_topic_mode SET enabled = 0 WHERE chat_id = '<your_chat_id>'; \
   DELETE FROM telegram_dm_topic_bindings WHERE chat_id = '<your_chat_id>';"
```

<a id="downgrading-hermes"></a>
### 降级 Hermes

如果降级到不支持 `/topic` 的 Hermes 版本，该功能会直接停止工作——`telegram_dm_topic_mode` 和 `telegram_dm_topic_bindings` 表仍然留在 `state.db` 中，但旧版本代码会忽略它们。DM 会回退到原生的按线程隔离（每个 `message_thread_id` 仍然通过 `build_session_key` 拥有自己的会话），因此你现有的 Telegram 话题仍然可以作为并行会话继续工作。根 DM 不再是“大厅”——其中的消息会像过去一样直接进入 Agent。重新升级后，多会话模式会恢复到你之前设置的样子。

<a id="group-forum-topic-skill-binding"></a>
## 群组论坛话题技能绑定

启用了**话题模式**（Topics mode）的超级群组（也叫“论坛话题”）本身就已实现了按话题隔离——每个 `thread_id` 映射到自己的会话。但你可能会希望在特定群组话题的消息到达时**自动加载某个技能**，就像 DM 话题技能绑定一样。

<a id="use-case"></a>
### 使用场景

一个团队超级群组，使用论坛话题管理不同的工作流：

- **工程**话题 → 自动加载 `software-development` 技能
- **研究**话题 → 自动加载 `arxiv` 技能
- **通用**话题 → 无技能，作为通用助手

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
          # 无技能 — 通用用途
```

**字段说明：**

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `chat_id` | 是 | 超级群组的数字 ID（以 `-100` 开头的负数） |
| `name` | 否 | 话题的可读标签（仅用于展示） |
| `thread_id` | 是 | Telegram 论坛话题 ID — 可见于 `t.me/c/&lt;group_id&gt;/&lt;thread_id&gt;` 链接 |
| `skill` | 否 | 在该话题的新会话中自动加载的技能 |

<a id="how-it-works"></a>
### 工作原理

1. 当消息到达一个被映射的群组话题时，Hermes 会在 `group_topics` 配置中查找对应的 `chat_id` 和 `thread_id`
2. 如果找到的条目包含 `skill` 字段，则该技能会被自动加载到会话中——与 DM 话题技能绑定方式一致
3. 没有 `skill` 键的话题只享受会话隔离（保持既有行为，不变）
4. 未映射的 `thread_id` 或 `chat_id` 会被静默忽略——不会报错，也不加载技能
<a id="differences-from-dm-topics"></a>
### 与私聊主题的差异

| | 私聊主题 | 群组主题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 主题创建 | 若 `thread_id` 缺失，Hermes 通过 API 创建主题 | 管理员在 Telegram 界面中创建主题 |
| `thread_id` | 创建后自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（由管理员控制外观） |
| 技能绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛主题自带该功能） |

:::tip
要找到某个主题的 `thread_id`，请在 Telegram Web 或桌面端打开该主题，查看 URL：`https://t.me/c/1234567890/5` — 最后一个数字（`5`）就是 `thread_id`。超级群组的 `chat_id` 是群组 ID 前面加上 `-100`（例如，群组 `1234567890` 变为 `-1001234567890`）。
:::

<a id="recent-bot-api-features"></a>
## 近期 Bot API 功能

- **Bot API 9.4（2026 年 2 月）：** 私聊主题 — 机器人可以通过 `createForumTopic` 在一对一私聊中创建论坛主题。Hermes 利用此功能实现了两个不同的特性：由运营者策划的[私聊主题](#private-chat-topics-bot-api-94)（配置驱动，固定主题列表）和由用户驱动的[多会话私聊模式](#multi-session-dm-mode-topic)（通过 `/topic` 激活，用户可创建无限数量的主题）。
- **隐私政策：** Telegram 现在要求机器人拥有隐私政策。通过 BotFather 使用 `/setprivacy_policy` 设置，否则 Telegram 可能会自动生成一个占位符。如果你的机器人面向公众，这一点尤其重要。
- **Bot API 9.5（2026 年 3 月）：** 通过 `sendMessageDraft` 实现原生流式传输。Hermes 支持 Telegram 的原生流式草稿 API，作为私聊的可选传输方式。默认仍沿用传统的 `editMessageText` 路径，因为在某些 Telegram 客户端上，草稿预览会出现明显的折叠和重新渲染现象。

<a id="streaming-transport-gateway-streaming-transport"></a>
### 流式传输（`gateway.streaming.transport`）

当启用了流式传输（`gateway.streaming.enabled: true`）时，Hermes 会选择以下四种传输方式之一：

| 值 | 行为 |
|---|---|
| `auto` | 在支持的聊天中（目前为 Telegram 私聊）使用原生草稿流式传输；否则使用传统的基于编辑的方式。如果草稿帧失败，会优雅降级。 |
| `draft` | 强制使用原生草稿。如果聊天不支持草稿（例如群组/主题），则记录降级信息并回退到编辑方式。 |
| `edit`（默认） | 对所有聊天类型使用传统的渐进式 `editMessageText` 轮询。 |
| `off` | 完全禁用流式传输（仅返回最终回复，无渐进更新）。 |

在 `~/.hermes/config.yaml` 中：

```yaml
gateway:
  streaming:
    enabled: true
    transport: edit    # edit | auto | draft | off
```

**使用 `edit`（默认）时在私聊中看到的效果** — 网关会发送一条正常的预览消息，并通过 `editMessageText` 逐步更新，避免 Telegram 草稿预览的折叠/回滚效应。

**使用 `auto` 或 `draft` 时在私聊中看到的效果** — Telegram 会显示一个逐 token 更新的动态草稿预览。当回复完成时，它会以常规消息的形式发送，草稿预览在客户端上自然清除。草稿没有消息 ID，因此最终答案会保留在你的聊天记录中。
**那群组、超级群组、论坛主题呢？** Telegram 将 `sendMessageDraft` 限制为私聊（私信）。对于其他所有情况，网关会透明地回退到基于编辑的路径——与之前相同的用户体验。

**如果草稿帧失败会怎样？** 任何失败（临时网络错误、服务端拒绝、较旧的 python-telegram-bot 安装）都会将该响应切换回基于编辑的路径，以完成流的剩余部分。下一条响应会重新尝试。

<a id="rendering-tables-and-link-previews"></a>
## 渲染：表格与链接预览

Telegram 的 MarkdownV2 没有原生的表格语法——如果直接传递，管道表格会渲染成转义后的噪声。Hermes 会自动规范化 Markdown 表格：

- **小表格** 会被扁平化为 **行分组列表** ——每行在列标题下变成一个可读的列表项。适用于 2–4 列和短单元格。
- **较大或较宽的表格** 会回退到 **围栏代码块**，带对齐的列，这样不会丢失内容。会添加一行提示，让 Agent 在 Telegram 上倾向于使用叙述性后续内容，而不是更多表格。

无需配置——适配器会根据每条消息选择合适的回退方式。如果你想要旧式的“总是代码块”行为，可以通过在 `config.yaml` 中设置 `telegram.pretty_tables: false` 来禁用表格规范化（默认值：`true`）。

**链接预览。** Telegram 会自动为机器人消息中的 URL 生成链接预览。如果你希望关闭这些预览（例如长的 `/tools` 输出、Agent 回复中提及十个链接等情况）：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_link_previews: true
```

启用后，Hermes 会为每条外发消息附加 Telegram 的 `LinkPreviewOptions(is_disabled=True)`，并在较旧的 `python-telegram-bot` 版本上回退到旧的 `disable_web_page_preview` 参数。

<a id="group-allowlisting"></a>
## 群组白名单

Telegram 群组和论坛聊天有两个独立可配置的开关：

- **发送者用户 ID**（`group_allow_from` / `TELEGRAM_GROUP_ALLOWED_USERS`）—— 仅适用于群组/论坛消息的发送者范围白名单。当你希望特定用户能够在群组中调用机器人，而又不想将他们添加到 `TELEGRAM_ALLOWED_USERS`（这也会授予他们私信访问权限）时使用此选项。
- **聊天 ID**（`group_allowed_chats` / `TELEGRAM_GROUP_ALLOWED_CHATS`）—— 聊天范围白名单。这些群组/论坛的任何成员都可以与机器人交互。适用于团队/支持机器人，其中群组成员身份本身就是访问信号。

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # 全局访问（私信 + 群组）。这里的用户始终可以调用机器人。
        allow_from:
          - "123456789"
        # 仅在群组/论坛中允许的发送者 ID。不授予私信访问权限。
        group_allow_from:
          - "987654321"
        # 整个群组/论坛——任何成员都被授权。
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

- `TELEGRAM_ALLOWED_USERS` 适用于所有聊天类型（私聊、群组、论坛）。
- `TELEGRAM_GROUP_ALLOWED_USERS` 仅授权在群组/论坛中列出的发送者。除非在 `TELEGRAM_ALLOWED_USERS` 中也列出，否则他们仍无法向机器人发送私聊消息。
- `TELEGRAM_GROUP_ALLOWED_CHATS` 中的聊天会授权该聊天的所有成员，无论发送者是谁。
- 在这些变量中使用 `*` 可允许任何发送者/聊天。
- 此权限叠加在现有的提及/模式触发规则以及 `group_topics` + `ignored_threads` 之上。

<a id="migration-from-before-pr-17686"></a>
### 从 PR #17686 之前的版本迁移

在此拆分之前，`TELEGRAM_GROUP_ALLOWED_USERS` 是唯一的控制开关，用户在其中填写的是 **聊天 ID**。为了向后兼容，`TELEGRAM_GROUP_ALLOWED_USERS` 中形如聊天 ID（以 `-` 开头）的值仍然会被当作聊天 ID 处理，并记录一次弃用警告。迁移方法：

```bash
# 旧方式（仍然可用，但已弃用）
TELEGRAM_GROUP_ALLOWED_USERS="-1001234567890"

# 新方式
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

<a id="guest-mention-bypass-guestmode"></a>
### 访客 @提及 绕过（`guest_mode`）

在典型设置中，`group_allowed_chats` 是一个硬性门槛：来自未授权群组的消息会被静默丢弃，即使某个成员明确用 @提及 了机器人。对于支持/团队机器人来说，这是合适的默认行为。

对于更随意的场景——比如好友群聊中你希望机器人**大部分时间保持沉默**，但**偶尔在显式的 @ 时可用**——可以启用 `guest_mode`：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        group_allowed_chats:
          - "-1001234567890"   # 你主要的授权群组
        guest_mode: true       # 非授权群组：仅在 @提及 时允许
```

等效环境变量：

```bash
TELEGRAM_GUEST_MODE=true
```

默认值：`false`。

在 `guest_mode: true` 的情况下，来自非授权群组的消息**仅当**它明确 @提及 了机器人时才会被处理。每一轮对话都需要 @提及 —— 访客交互没有会话粘性，因此机器人永远不会在没有被 @ 的情况下自动加入好友群聊的讨论。

私聊和授权群组的行为与之前完全一致。

<a id="slash-command-access-control"></a>
## 斜杠命令访问控制

默认情况下，每个允许的用户都可以执行所有斜杠命令。为了将你的允许列表分为**管理员**（拥有完整的斜杠命令访问权限）和**普通用户**（只能运行你明确启用的命令），请在平台 `extra` 块中添加 `allow_admin_from` 和 `user_allowed_commands`：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # 现有的允许列表（不变）
        allow_from:
          - "123456789"     # 管理员
          - "555555555"     # 普通用户
          - "777777777"     # 普通用户

        # 新增 —— 管理员拥有所有斜杠命令（内置 + 插件）
        allow_admin_from:
          - "123456789"

        # 新增 —— 非管理员允许用户只能运行这些斜杠命令。
        # /help 和 /whoami 始终允许，以便用户查看自己的权限。
        user_allowed_commands:
          - status
          - model
          - history

        # 可选：为群组分别设置管理员/命令列表
        group_allow_admin_from:
          - "123456789"
        group_user_allowed_commands:
          - status
```
**行为：**

-   在某个范围（私聊或群组）的 `allow_admin_from` 中列出的用户，可以通过实时注册表运行 **每个** 已注册的斜杠命令 —— 包括内置命令和插件注册的命令。
-   在 `allow_from` 中但 **不在** `allow_admin_from` 中的用户，只能运行 `user_allowed_commands` 中列出的命令，以及始终允许的基础命令：`/help` 和 `/whoami`。
-   纯聊天消息（非斜杠命令）不受影响。非管理员用户仍然可以正常与 Agent 对话，只是无法触发任意命令。
-   **向后兼容：** 如果某个范围未设置 `allow_admin_from`，则该范围的斜杠命令门控功能被禁用。现有安装无需任何更改即可正常工作。
-   私聊管理员身份不代表群组管理员身份。每个范围都有自己的管理员列表。
-   如果仅设置了 `group_allow_admin_from`，则私聊范围保持在无限制（向后兼容）模式。

使用 `/whoami` 查看当前范围、你的身份（管理员/用户/无限制）以及你可以运行的斜杠命令。

<a id="interactive-model-picker"></a>
## 交互式模型选择器

当你在 Telegram 聊天中发送不带参数的 `/model` 时，Hermes 会显示一个交互式内联键盘，用于切换模型：

1.  **提供商选择** —— 按钮显示每个可用提供商及其模型数量（例如，当前提供商显示为“OpenAI (15)”、“✓ Anthropic (12)”）。
2.  **模型选择** —— 分页模型列表，带有 **上一页**/**下一页** 导航、返回提供商的 **返回** 按钮，以及 **取消**。

当前模型和提供商显示在顶部。所有导航均通过原地编辑同一条消息进行（无聊天杂乱信息）。

:::tip
如果你知道确切的模型名称，直接输入 `/model <名称>` 即可跳过选择器。你也可以输入 `/model <名称> --global` 来使更改跨会话持久化。
:::

<a id="dns-over-https-fallback-ips"></a>
## DNS-over-HTTPS 备用 IP

在某些受限网络中，`api.telegram.org` 可能解析到一个无法访问的 IP。Telegram 适配器包含一个 **备用 IP** 机制，该机制会在保持正确的 TLS 主机名和 SNI 的同时，透明地重试连接替代 IP。

<a id="how-it-works"></a>
### 工作原理

1.  如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2.  否则，适配器会自动通过 DNS-over-HTTPS (DoH) 查询 **Google DNS** 和 **Cloudflare DNS**，以发现 `api.telegram.org` 的替代 IP。
3.  通过 DoH 返回的、与系统 DNS 结果不同的 IP 将作为备用 IP 使用。
4.  如果 DoH 也被屏蔽，则使用硬编码的种子 IP（`149.154.167.220`）作为最后手段。
5.  一旦某个备用 IP 连接成功，它就会变为“粘性”——后续请求直接使用该 IP，无需先重试主路径。

<a id="configuration"></a>
### 配置

```bash
# 显式备用 IP（逗号分隔）
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
通常你无需手动配置。通过 DoH 的自动发现机制可以处理大多数受限网络场景。只有当你的网络也屏蔽了 DoH 时，才需要设置 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::
<a id="proxy-support"></a>
## 代理支持

如果你的网络需要通过 HTTP 代理才能访问互联网（这在企业环境中很常见），Telegram 适配器会自动读取标准代理环境变量，并将所有连接通过该代理路由。

<a id="supported-variables"></a>
### 支持的变量

适配器会按顺序检查以下环境变量，使用第一个已设置的值：

1. `HTTPS_PROXY`
2. `HTTP_PROXY`
3. `ALL_PROXY`
4. `https_proxy` / `http_proxy` / `all_proxy` (小写变体)

<a id="configuration"></a>
### 配置

在启动网关之前，在环境中设置代理：

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

或者将其添加到 `~/.hermes/.env`：

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

代理适用于主传输和所有备用 IP 传输。无需额外的 Hermes 配置——只要设置了环境变量，就会自动使用。

:::note
这涵盖了 Hermes 用于 Telegram 连接的自定义备用传输层。其他地方使用的标准 `httpx` 客户端本身已经原生支持代理环境变量。
:::

<a id="message-reactions"></a>
## 消息反应

机器人可以为消息添加表情符号反应，作为视觉处理反馈：

- 👀 当机器人开始处理你的消息时
- ✅ 当响应成功送达时
- ❌ 如果处理过程中发生错误

反应**默认是禁用的**。在 `config.yaml` 中启用：

```yaml
telegram:
  reactions: true
```

或者通过环境变量：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（反应是累加的）不同，Telegram 的 Bot API 在单个调用中替换所有机器人反应。从 👀 到 ✅/❌ 的转换是原子性的——你不会同时看到两者。
:::

:::tip
如果机器人没有在群组中添加反应的权限，反应调用会静默失败，消息处理会正常继续。
:::

<a id="per-channel-prompts"></a>
## 按频道提示

为特定的 Telegram 群组或论坛话题分配临时的系统提示。该提示在每次轮次的运行时注入——不会持久化到记录历史中——因此更改会立即生效。

```yaml
telegram:
  channel_prompts:
    "-1001234567890": |
      You are a research assistant. Focus on academic sources,
      citations, and concise synthesis.
    "42":  |
      This topic is for creative writing feedback. Be warm and
      constructive.
```

键是聊天 ID（群组/超级群组）或论坛话题 ID。对于论坛群组，话题级别的提示会覆盖群组级别的提示：

- 群组 `-1001234567890` 中话题 `42` 的消息 → 使用话题 `42` 的提示
- 话题 `99` 的消息（没有显式条目）→ 回退到群组 `-1001234567890` 的提示
- 在没有任何条目的群组中的消息 → 不应用频道提示

数字形式的 YAML 键会自动规范化为字符串。

<a id="troubleshooting"></a>
## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 机器人完全无响应 | 验证 `TELEGRAM_BOT_TOKEN` 是否正确。检查 `hermes gateway` 日志中的错误。 |
| 机器人回复“未经授权” | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。使用 @userinfobot 再次确认。 |
| 机器人忽略群组消息 | 隐私模式可能已开启。禁用它（第3步）或将机器人设为群组管理员。**更改隐私设置后，记得移除并重新添加机器人。** |
| 语音消息未转录 | 验证 STT 可用：安装 `faster-whisper` 用于本地转录，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件而不是气泡 | 安装 `ffmpeg`（Edge TTS Opus 转换所需）。 |
| 机器人令牌已吊销/无效 | 通过 BotFather 中的 `/revoke` 然后 `/newbot` 或 `/token` 生成新令牌。更新你的 `.env` 文件。 |
| Webhook 未接收更新 | 验证 `TELEGRAM_WEBHOOK_URL` 可公开访问（使用 `curl` 测试）。确保你的平台/反向代理将来自 URL 端口的入站 HTTPS 流量路由到由 `TELEGRAM_WEBHOOK_PORT` 配置的本地监听端口（它们不需要相同）。确保 SSL/TLS 已启用——Telegram 只发送到 HTTPS URL。检查防火墙规则。 |
<a id="exec-approval"></a>
## 执行审批

当 Agent 试图运行一条可能有危险的命令时，它会在聊天中请求你的批准：

> ⚠️ 此命令具有潜在危险（递归删除）。回复 "yes" 以批准。

回复 "yes"/"y" 表示批准，"no"/"n" 表示拒绝。

<a id="interactive-prompts-clarify"></a>
## 交互式提示（clarify）

当 Agent 调用 `clarify` 工具时——用于询问你更倾向于哪种方案、获取任务后的反馈，或在做出重要决策前检查确认——Telegram 会通过**内联键盘按钮**呈现问题：

> ❓ 我应该为仪表盘使用哪个框架？
>
> [1. Next.js] [2. Remix] [3. Astro]
> [✏️ 其他（输入答案）]

点击按钮进行回答，或者点击**其他**来输入自由文本回复（你发送的下一条消息将成为答案）。不提供预设选项的开放式 `clarify` 调用会跳过按钮，直接捕获你的下一条消息。

通过 `~/.hermes/config.yaml` 中的 `agent.clarify_timeout` 配置响应超时时间（默认 `600` 秒）。如果在超时内没有响应，Agent 会发送一条哨兵消息来解除阻塞，并自适应处理，而非挂起。

<a id="push-notification-volume"></a>
## 推送通知频率

Telegram 会在机器人发送的每条消息上触发推送通知。对于长时间运行的 Agent 轮次，它会发出工具进度气泡、流式更新和状态回调，这会很快变得嘈杂。Telegram 适配器有两种通知模式：

| 模式 | 行为 |
|------|------|
| `important`（默认） | 仅针对**最终回复**、**审批提示**和**斜杠命令确认**发出通知。工具进度、流式片段和状态消息以 `disable_notification=true` 方式发送。 |
| `all` | 每一条发出的消息都会触发推送通知。旧版行为；如果你确实希望听到每一次工具调用，可以选择此模式。 |

在 `~/.hermes/config.yaml` 中配置：

```yaml
display:
  platforms:
    telegram:
      notifications: important   # 或 "all"
```

环境变量覆盖（便于快速 A/B 测试）：

```bash
HERMES_TELEGRAM_NOTIFICATIONS=all
```

未知值会记录警告并回退到 `important`。

<a id="security"></a>
## 安全

:::warning
始终设置 `TELEGRAM_ALLOWED_USERS` 来限制谁能与你的机器人交互。如果没有设置，网关默认会拒绝所有用户，作为安全措施。
:::

切勿公开分享你的机器人令牌。如果泄露，立即通过 BotFather 的 `/revoke` 命令撤销它。

更多详情，请参阅[安全文档](/user-guide/security)。你也可以使用[私信配对](/user-guide/messaging#dm-pairing-alternative-to-allowlists)来实现更动态的用户授权方式。
