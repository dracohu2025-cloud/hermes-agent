---
sidebar_position: 4
title: "Slack"
description: "将 Hermes Agent 设置为使用 Socket 模式的 Slack 机器人"
---

<a id="slack-setup"></a>
# Slack 设置

使用 Socket 模式将 Hermes Agent 作为机器人连接到 Slack。Socket 模式使用 WebSocket 而非公共 HTTP 端点，因此你的 Hermes 实例无需公开访问——它可以在防火墙后面、你的笔记本电脑上或私有服务器上正常工作。

:::warning 经典 Slack 应用已弃用
经典 Slack 应用（使用 RTM API）已于 **2025 年 3 月完全弃用**。Hermes 使用现代的 Bolt SDK 及 Socket 模式。如果你有旧的经典应用，必须按照以下步骤创建一个新应用。
:::

<a id="overview"></a>
<a id="classic-slack-apps-deprecated"></a>
## 概览

| 组件 | 值 |
|-----------|-------|
| **库** | `slack-bolt` / `slack_sdk`（Python，Socket 模式） |
| **连接方式** | WebSocket — 无需公共 URL |
| **需要的认证令牌** | 机器人令牌（`xoxb-`）+ 应用级令牌（`xapp-`） |
| **用户标识** | Slack 成员 ID（例如 `U01ABC2DEF3`） |

---

<a id="step-1-create-a-slack-app"></a>
## 第一步：创建 Slack 应用

最快的方法是粘贴 Hermes 为你生成的清单。该清单一次性声明了所有内置的斜杠命令（`/btw`、`/stop`、`/model` 等）、所有必需的 OAuth 作用域、所有事件订阅，并启用了 Socket 模式。

<a id="option-a-from-a-hermes-generated-manifest-recommended"></a>
### 选项 A：使用 Hermes 生成的清单（推荐）

1. 生成清单：
   ```bash
   hermes slack manifest --write
   ```
   这会将清单写入 `~/.hermes/slack-manifest.json` 并打印粘贴说明。
2. 前往 [https://api.slack.com/apps](https://api.slack.com/apps) → **创建新应用** → **从应用清单创建**
3. 选择你的工作区，粘贴 JSON 内容，检查后点击 **下一步** → **创建**
4. 直接跳到 **第六步：安装应用到工作区**。清单已经为你处理了作用域、事件和斜杠命令。

<a id="option-b-from-scratch-manual"></a>
### 选项 B：从头手动创建

1. 前往 [https://api.slack.com/apps](https://api.slack.com/apps)
2. 点击 **创建新应用**
3. 选择 **从头开始**
4. 输入应用名称（例如 "Hermes Agent"）并选择你的工作区
5. 点击 **创建应用**

你会进入应用的 **基本信息** 页面。继续执行下面的第 2–6 步。

---

<a id="step-2-configure-bot-token-scopes"></a>
## 第二步：配置机器人令牌作用域

在侧边栏中导航到 **功能 → OAuth 与权限**。滚动到 **作用域 → 机器人令牌作用域** 并添加以下内容：

| 作用域 | 用途 |
|-------|---------|
| `chat:write` | 以机器人身份发送消息 |
| `app_mentions:read` | 检测在频道中被 @提及 |
| `channels:history` | 读取机器人所在公共频道中的消息 |
| `channels:read` | 列出并获取公共频道信息 |
| `groups:history` | 读取机器人被邀请的私有频道中的消息 |
| `im:history` | 读取直接消息历史 |
| `im:read` | 查看基本的 DM 信息 |
| `im:write` | 打开并管理直接消息 |
| `users:read` | 查找用户信息 |
| `files:read` | 读取并下载附件文件，包括语音笔记/音频 |
| `files:write` | 上传文件（图片、音频、文档） |

<a id="missing-scopes-missing-features"></a>
:::caution 缺少作用域 = 功能缺失
没有 `channels:history` 和 `groups:history`，机器人 **将不会在频道中接收消息** —— 它只能在直接消息中工作。没有 `files:read`，Hermes 可以聊天，但 **无法可靠地读取用户上传的附件**。这些是最常被遗漏的作用域。
:::
**可选作用域（scopes）：**

| Scope | 用途 |
|-------|------|
| `groups:read` | 列出并获取私有频道的信息 |

---

<a id="step-3-enable-socket-mode"></a>
## 第三步：启用 Socket Mode

Socket Mode 让 Bot 通过 WebSocket 而非公开 URL 进行连接。

1. 在侧边栏中，进入 **Settings → Socket Mode**
2. 将 **Enable Socket Mode** 切换到 ON
3. 系统会提示您创建一个 **App-Level Token**：
   - 命名为类似 `hermes-socket`（名称无关紧要）
   - 添加 **`connections:write`** 作用域
   - 点击 **Generate**
4. **复制 token** — 它以 `xapp-` 开头。这就是您的 `SLACK_APP_TOKEN`

:::tip
您随时可以在 **Settings → Basic Information → App-Level Tokens** 下找到或重新生成应用级 token。
:::

---

<a id="step-4-subscribe-to-events"></a>
## 第四步：订阅事件

这一步至关重要——它控制 Bot 能看到哪些消息。

1. 在侧边栏中，进入 **Features → Event Subscriptions**
2. 将 **Enable Events** 切换到 ON
3. 展开 **Subscribe to bot events** 并添加：

| 事件 | 是否必需？ | 用途 |
|------|------------|------|
| `message.im` | **是** | Bot 接收私聊消息 |
| `message.channels` | **是** | Bot 接收它被加入的 **公开** 频道中的消息 |
| `message.groups` | **推荐** | Bot 接收它被邀请的 **私有** 频道中的消息 |
| `app_mention` | **是** | 防止 Bot 被 @ 时 Bolt SDK 报错 |

4. 点击页面底部的 **Save Changes**

:::danger 缺少事件订阅是 #1 排查问题
如果 Bot 能正常处理私聊但 **无法在频道中工作**，您几乎肯定忘记了添加
`message.channels`（用于公开频道）和/或 `message.groups`（用于私有频道）。
<a id="missing-event-subscriptions-is-the-1-setup-issue"></a>
如果没有这些事件，Slack 根本不会将频道消息传递给 Bot。
:::

---

<a id="step-5-enable-the-messages-tab"></a>
## 第五步：启用消息选项卡

这一步启用与 Bot 的私聊。如果不做，用户尝试发送私聊时会看到 **"Sending messages to this app has been turned off"**。

1. 在侧边栏中，进入 **Features → App Home**
2. 滚动到 **Show Tabs**
3. 将 **Messages Tab** 切换到 ON
4. 勾选 **"Allow users to send Slash commands and messages from the messages tab"**

:::danger 不做这一步，私聊将完全被屏蔽
即使拥有所有正确的作用域和事件订阅，Slack 也不会允许用户向 Bot 发送私聊消息，除非启用了消息选项卡。这是 Slack 平台的要求，而非 Hermes 配置问题。
<a id="without-this-step-dms-are-completely-blocked"></a>
:::

---

<a id="step-6-install-app-to-workspace"></a>
## 第六步：安装应用到工作区

1. 在侧边栏中，进入 **Settings → Install App**
2. 点击 **Install to Workspace**
3. 检查权限并点击 **Allow**
4. 授权后，您会看到一个以 `xoxb-` 开头的 **Bot User OAuth Token**
5. **复制这个 token** — 这就是您的 `SLACK_BOT_TOKEN`

:::tip
如果之后修改了作用域或事件订阅，您**必须重新安装应用**才能使更改生效。Install App 页面会显示一个横幅提示您这样做。
:::

---

<a id="step-7-find-user-ids-for-the-allowlist"></a>
## 第七步：查找白名单所需的用户 ID

Hermes 使用 Slack 的 **Member ID**（而非用户名或显示名称）作为白名单依据。
要查找成员 ID：

1. 在 Slack 中，点击用户的名称或头像
2. 点击 **查看完整资料**
3. 点击 **⋮**（更多）按钮
4. 选择 **复制成员 ID**

成员 ID 的格式类似 `U01ABC2DEF3`。你至少需要自己的成员 ID。

---

<a id="step-8-configure-hermes"></a>
## 第 8 步：配置 Hermes

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_ALLOWED_USERS=U01ABC2DEF3              # 逗号分隔的成员 ID

# 可选
SLACK_HOME_CHANNEL=C01234567890              # 定时任务/计划消息的默认频道
SLACK_HOME_CHANNEL_NAME=general              # 首页频道的人类可读名称（可选）
```

或者运行交互式设置：

```bash
hermes gateway setup    # 在提示时选择 Slack
```

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅 Linux：开机系统服务
```

---

<a id="step-9-invite-the-bot-to-channels"></a>
## 第 9 步：邀请机器人加入频道

启动网关后，你需要**邀请机器人**到你希望它响应的任何频道：

```
/invite @Hermes Agent
```

机器人**不会**自动加入频道。你必须逐一邀请它进入每个频道。

---

<a id="slash-commands"></a>
## 斜杠命令

每个 Hermes 命令（`/btw`、`/stop`、`/new`、`/model`、`/help`……）都是原生 Slack 斜杠命令——与在 Telegram 和 Discord 上的工作方式完全相同。在 Slack 中输入 `/`，自动补全选择器会列出每个 Hermes 命令及其描述。

底层原理：Hermes 附带一个生成的 Slack 应用清单（参见第 1 步，选项 A），该清单将 [`COMMAND_REGISTRY`](https://github.com/NousResearch/hermes-agent/blob/main/hermes_cli/commands.py) 中的每个命令声明为斜杠命令。在 Socket 模式下，Slack 通过 WebSocket 路由命令事件，无论清单的 `url` 字段如何设置。

<a id="refreshing-slash-commands-after-updates"></a>
### 更新后刷新斜杠命令

当 Hermes 添加新命令时（例如在 `hermes update` 之后），重新生成清单并更新你的 Slack 应用：

```bash
hermes slack manifest --write
```

然后在 Slack 中：
1. 打开 [https://api.slack.com/apps](https://api.slack.com/apps) → 你的 Hermes 应用
2. **功能 → 应用清单 → 编辑**
3. 粘贴 `~/.hermes/slack-manifest.json` 的新内容
4. **保存**。如果作用域或斜杠命令发生更改，Slack 会提示重新安装应用。

<a id="legacy-hermes-still-works"></a>
### 旧版 `/hermes <子命令>` 仍然可用

为了向后兼容旧版清单，你仍然可以输入 `/hermes btw run the tests`——Hermes 会以与 `/btw run the tests` 相同的方式路由它。自由提问也同样有效：`/hermes what's the weather?` 会被当作普通消息处理。

<a id="using-commands-inside-threads-the-cmd-prefix"></a>
### 在线程中使用命令（`!cmd` 前缀）

Slack 本身会阻止在线程回复中使用原生斜杠命令——尝试在线程中输入 `/queue`，Slack 会回复“/queue 在线程中不受支持。抱歉！”没有应用端设置可以重新启用它们；Slack 永远不会将它们传递给 Hermes。
作为变通方案，Hermes 识别以 `!` 开头的命令前缀，该前缀在线程（以及任何其他位置）中均有效。直接在线程回复中键入 `!queue`、`!stop`、`!model gpt-5.4` 等命令——Hermes 会像处理斜杠命令一样处理它，并在同一线程中回复。

仅检查第一个 token 是否匹配已知命令列表，因此像 `!nice work` 这样的随意消息会原样传递给 Agent。

<a id="advanced-emit-only-the-slash-commands-array"></a>
### 高级：仅输出斜杠命令数组

如果您手动维护 Slack manifest 且只需要斜杠命令列表：

```bash
hermes slack manifest --slashes-only > /tmp/slashes.json
```

将该数组粘贴到现有 manifest 的 `features.slash_commands` 键中。

---

<a id="how-the-bot-responds"></a>
## 机器人如何响应

了解 Hermes 在不同上下文中的行为：

| 上下文 | 行为 |
|---------|----------|
| **私聊** | 机器人回复每条消息——无需 @提及 |
| **频道** | 机器人**仅在 @提及 时回复**（例如 `@Hermes Agent 现在几点了？`）。在频道中，Hermes 会在该消息的线程中回复。 |
| **线程** | 如果在现有线程中 @提及 Hermes，它会在同一线程中回复。一旦机器人在线程中拥有活跃会话，**该线程中的后续回复无需 @提及**——机器人会自然地跟随对话。 |

:::tip
在频道中，始终通过 @提及 机器人来开始对话。一旦机器人在线程中活跃，您可以在该线程中回复而无需提及它。在线程之外，未被 @提及 的消息将被忽略，以避免在繁忙频道中产生干扰。
:::

---

<a id="configuration-options"></a>
## 配置选项

除了第 8 步中必需的环境变量外，您还可以通过 `~/.hermes/config.yaml` 自定义 Slack 机器人行为。

<a id="thread-reply-behavior"></a>
### 线程与回复行为

```yaml
platforms:
  slack:
    # 控制多部分回复的线程化方式
    # "off"   — 从不将回复线程化到原始消息
    # "first" — 第一个分块线程化到用户消息（默认）
    # "all"   — 所有分块线程化到用户消息
    reply_to_mode: "first"

    extra:
      # 是否在线程中回复（默认：true）。
      # 为 false 时，频道消息会获得直接频道回复而非线程。
      # 已有线程中的消息仍在线程内回复。
      reply_in_thread: true

      # 同时将线程回复发布到主频道
      #（Slack 的“同时发送到频道”功能）。
      # 仅广播第一个回复的第一个分块。
      reply_broadcast: false
```

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `platforms.slack.reply_to_mode` | `"first"` | 多部分消息的线程模式：`"off"`、`"first"` 或 `"all"` |
| `platforms.slack.extra.reply_in_thread` | `true` | 为 `false` 时，频道消息获得直接回复而非线程。已有线程中的消息仍在线程内回复。 |
| `platforms.slack.extra.reply_broadcast` | `false` | 为 `true` 时，线程回复也会发布到主频道。仅广播第一个分块。 |
<a id="session-isolation"></a>
### 会话隔离

```yaml
# 全局设置 — 适用于 Slack 及所有其他平台
group_sessions_per_user: true
```

当设置为 `true`（默认值）时，共享频道中的每个用户都会获得独立的会话。两个用户在 `#general` 中与 Hermes 对话时，会拥有各自独立的历史记录和上下文。

如果希望启用协作模式，让整个频道共享同一个会话，请设置为 `false`。请注意，这意味着用户之间会共享上下文增长和 token 成本，并且某个用户执行 `/reset` 会清除所有人的会话。

<a id="mention-trigger-behavior"></a>
### @提及与触发行为

```yaml
slack:
  # 在频道中要求 @提及（这是默认行为；
  # Slack 适配器会强制在频道中要求 @提及，
  # 但你可以显式设置此项以与其他平台保持一致）
  require_mention: true

  # 禁止线程自动参与：仅回复包含显式 @提及的频道消息。
  # 关闭此选项（默认）时，Slack 会“自动参与”——
  # 记住线程中过去的提及，并跟进机器人消息的回复，
  # 无需新的提及即可恢复活跃会话。
  # 开启 strict_mention 后，每条新的频道消息都必须 @提及机器人，
  # Hermes 才会响应。
  strict_mention: false

  # 触发机器人的自定义提及模式
  # （除了默认的 @提及检测之外）
  mention_patterns:
    - "hey hermes"
    - "hermes,"

  # 附加到每条外发消息前的文本
  reply_prefix: ""
```

:::tip 何时使用 `strict_mention`
<a id="when-to-use-strictmention"></a>
在繁忙的工作区中，如果 Slack 默认的“机器人记住了这个线程”行为让用户感到意外，请将此选项设置为 `true`。例如，在一个很长的技术支持线程中，机器人在开始时提供了帮助，而你希望它保持沉默，除非再次被显式 @提及。私信和活跃的交互式会话不受影响。
:::

:::info
Slack 支持两种模式：默认情况下需要 `@提及` 才能开始对话，但你可以通过 `SLACK_FREE_RESPONSE_CHANNELS`（逗号分隔的频道 ID）或 `config.yaml` 中的 `slack.free_response_channels` 将特定频道排除在外。一旦机器人在某个线程中拥有活跃会话，后续的线程回复就不需要提及。在私信中，机器人始终无需提及即可响应。
:::

<a id="channel-allowlist-allowedchannels"></a>
### 频道白名单（`allowed_channels`）

将机器人限制在一组固定的 Slack 频道中——当机器人被邀请到许多频道但只应在少数频道中响应时很有用。设置后，来自**不在**此列表中的频道的消息会被**静默忽略**，即使机器人被 `@提及` 也是如此。

**私信不受此过滤器限制**，因此授权用户始终可以通过私信联系到机器人。

```yaml
slack:
  allowed_channels:
    - "C0123456789"   # #ops
    - "C0987654321"   # #incident-response
```

或者通过环境变量（逗号分隔）：

```bash
SLACK_ALLOWED_CHANNELS="C0123456789,C0987654321"
```

行为：

- 空/未设置 → 无限制（完全向后兼容）。
- 非空 → 频道 ID 必须在列表中，否则消息会在任何其他门控（提及要求、`free_response_channels` 等）运行之前被丢弃。
- Slack 频道 ID 以 `C`（公开）、`G`（私密）或 `D`（私信）开头。可以通过 Slack UI 的“打开频道详情”→“关于”面板或通过 API 查找。
参见：[admin/user 斜杠命令分离](../../reference/slash-commands.md#permissions-and-adminuser-split)。

<a id="unauthorized-user-handling"></a>
### 未授权用户处理

```yaml
slack:
  # 当未授权用户（不在 SLACK_ALLOWED_USERS 中）私信机器人时的行为
  # "pair"   — 提示输入配对码（默认）
  # "ignore" — 静默丢弃消息
  unauthorized_dm_behavior: "pair"
```

你也可以在所有平台全局设置此选项：

```yaml
unauthorized_dm_behavior: "pair"
```

`slack:` 下的平台特定设置会覆盖全局设置。

<a id="voice-transcription"></a>
### 语音转录

```yaml
# 全局设置 — 启用/禁用自动转录收到的语音消息
stt_enabled: true
```

当设为 `true`（默认值）时，收到的音频消息在被 Agent 处理之前，会使用配置的 STT 提供商自动转录。

<a id="full-example"></a>
### 完整示例

```yaml
# 全局网关设置
group_sessions_per_user: true
unauthorized_dm_behavior: "pair"
stt_enabled: true

# Slack 特定设置
slack:
  require_mention: true
  unauthorized_dm_behavior: "pair"

# 平台配置
platforms:
  slack:
    reply_to_mode: "first"
    extra:
      reply_in_thread: true
      reply_broadcast: false
```

---

<a id="home-channel"></a>
## 主频道

将 `SLACK_HOME_CHANNEL` 设置为一个频道 ID，Hermes 会将定时消息、定时任务结果以及其他主动通知发送到这里。要查找频道 ID：

1. 在 Slack 中右键点击频道名称
2. 点击 **查看频道详情**
3. 滚动到底部 — 频道 ID 会显示在那里

```bash
SLACK_HOME_CHANNEL=C01234567890
```

确保机器人已被**邀请到频道**（`/invite @Hermes Agent`）。

---

<a id="multi-workspace-support"></a>
## 多工作区支持

Hermes 可以使用单个网关实例**同时连接到多个 Slack 工作区**。每个工作区使用自己的机器人用户 ID 独立进行身份验证。

<a id="configuration"></a>
### 配置

在 `SLACK_BOT_TOKEN` 中以**逗号分隔的列表**形式提供多个机器人令牌：

```bash
# 多个机器人令牌 — 每个工作区一个
SLACK_BOT_TOKEN=xoxb-workspace1-token,xoxb-workspace2-token,xoxb-workspace3-token

# 仍然使用单个应用级令牌用于 Socket Mode
SLACK_APP_TOKEN=xapp-your-app-token
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
platforms:
  slack:
    token: "xoxb-workspace1-token,xoxb-workspace2-token"
```

<a id="oauth-token-file"></a>
### OAuth 令牌文件

除了环境变量或配置文件中的令牌，Hermes 还会从 **OAuth 令牌文件**加载令牌，路径为：

```
~/.hermes/slack_tokens.json
```

该文件是一个 JSON 对象，将团队 ID 映射到令牌条目：

```json
{
  "T01ABC2DEF3": {
    "token": "xoxb-workspace-token-here",
    "team_name": "My Workspace"
  }
}
```

此文件中的令牌会与通过 `SLACK_BOT_TOKEN` 指定的任何令牌合并。重复的令牌会自动去重。

<a id="how-it-works"></a>
### 工作原理

- 列表中的**第一个令牌**是主令牌，用于 Socket Mode 连接（AsyncApp）。
- 启动时，每个令牌都会通过 `auth.test` 进行身份验证。网关将每个 `team_id` 映射到自己的 `WebClient` 和 `bot_user_id`。
- 当消息到达时，Hermes 使用对应工作区的客户端进行回复。
- 主 `bot_user_id`（来自第一个令牌）用于向后兼容那些期望单一机器人身份的功能。
<a id="voice-messages"></a>
## 语音消息

Hermes 在 Slack 上支持语音功能：

- **接收：** 语音/音频消息会自动使用配置的 STT 提供商转录：本地 `faster-whisper`、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）
- **发送：** TTS 响应会以音频文件附件的形式发送

---

<a id="per-channel-prompts"></a>
## 按频道提示词

为特定 Slack 频道分配临时的系统提示词。该提示词会在每次对话时注入，但不会持久化到对话历史记录中——因此更改后立即生效。

```yaml
slack:
  channel_prompts:
    "C01RESEARCH": |
      You are a research assistant. Focus on academic sources,
      citations, and concise synthesis.
    "C02ENGINEERING": |
      Code review mode. Be precise about edge cases and
      performance implications.
```

键值是 Slack 频道 ID（可通过频道详情 →“关于” → 滚动到底部找到）。该频道中的所有消息都会注入该提示词作为临时系统指令。

<a id="per-channel-skill-bindings"></a>
## 按频道技能绑定

当在特定频道或私聊中开始新会话时，自动加载某个技能。与按频道提示词（每次对话注入）不同，技能绑定会在**会话开始**时将技能内容作为用户消息注入——它会成为对话历史的一部分，后续轮次无需重新加载。

这对于有明确用途的私聊或频道（如闪卡、特定领域的问答机器人、支持分类频道等）非常理想，因为你不想让模型自身的技能选择器在每次简短回复时决定是否加载技能。

```yaml
slack:
  channel_skill_bindings:
    # 私聊频道 —— 始终以“german-flashcards”模式运行
    - id: "D0ATH9TQ0G6"
      skills:
        - german-flashcards
    # 研究频道 —— 按顺序预加载多个技能
    - id: "C01RESEARCH"
      skills:
        - arxiv
        - writing-plans
    # 简写形式：单个技能以字符串形式给出
    - id: "C02SUPPORT"
      skill: hubspot-on-demand
```

注意：
- 绑定通过频道 ID 匹配。对于绑定频道中的线程消息，该线程会继承父频道的绑定。
- 技能仅在会话开始时加载（新会话或自动重置后）。如果更改了绑定，请运行 `/new` 或等待会话自动重置以使其生效。
- 可与 `channel_prompts` 结合使用，在技能指令之上添加按频道的语气/约束。

<a id="troubleshooting"></a>
## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 机器人不响应私聊 | 确认 `message.im` 已在事件订阅中，并且已重新安装应用 |
| 机器人在私聊中正常工作，但在频道中不行 | **最常见的问题。** 将 `message.channels` 和 `message.groups` 添加到事件订阅，重新安装应用，并通过 `/invite @Hermes Agent` 将机器人邀请到频道中 |
| 机器人在频道中不响应 @提及 | 1) 检查是否已订阅 `message.channels` 事件。2) 机器人必须被邀请到频道。3) 确保已添加 `channels:history` 范围。4) 更改范围/事件后重新安装应用 |
| 机器人忽略私有频道中的消息 | 同时添加 `message.groups` 事件订阅和 `groups:history` 范围，然后重新安装应用并 `/invite` 机器人 |
| 私聊中显示“已关闭向此应用发送消息” | 在应用首页设置中启用**消息选项卡**（参见步骤 5） |
| “not_authed”或“invalid_auth”错误 | 重新生成机器人令牌和应用令牌，更新 `.env` |
| 机器人能响应但无法在频道中发帖 | 通过 `/invite @Hermes Agent` 将机器人邀请到频道 |
| 机器人能对话但无法读取上传的图片/文件 | 添加 `files:read`，然后**重新安装**应用。当 Slack 返回范围/认证/权限失败时，Hermes 现会在聊天中显示附件访问诊断信息。 |
| `missing_scope` 错误 | 在 OAuth 和权限设置中添加所需范围，然后**重新安装**应用 |
| Socket 频繁断开 | 检查你的网络；Bolt 会自动重连，但不稳定的连接会导致延迟 |
| 更改了范围/事件但没有任何变化 | 在更改任何范围或事件订阅后，你**必须重新安装**应用到工作区 |
<a id="quick-checklist"></a>
### 快速检查清单

如果机器人在频道中无法正常工作，请**逐一**确认以下所有项：

1. ✅ 已订阅 `message.channels` 事件（针对公开频道）
2. ✅ 已订阅 `message.groups` 事件（针对私密频道）
3. ✅ 已订阅 `app_mention` 事件
4. ✅ 已添加 `channels:history` 权限范围（针对公开频道）
5. ✅ 已添加 `groups:history` 权限范围（针对私密频道）
6. ✅ 添加权限范围/事件后已**重新安装**应用
7. ✅ 已将机器人**邀请**到频道中（`/invite @Hermes Agent`）
8. ✅ 在消息中**@提及**了机器人

---

<a id="security"></a>
## 安全性

:::warning
**务必使用授权用户的成员 ID 设置 `SLACK_ALLOWED_USERS`**。如果没有此设置，网关默认会**拒绝所有消息**作为安全措施。切勿泄露你的机器人令牌——请像对待密码一样对待它们。
:::

- 令牌应存储在 `~/.hermes/.env` 文件中（文件权限设为 `600`）
- 通过 Slack 应用设置定期轮换令牌
- 审计哪些人可以访问你的 Hermes 配置目录
- Socket 模式意味着没有公开端点暴露——减少了一个攻击面
