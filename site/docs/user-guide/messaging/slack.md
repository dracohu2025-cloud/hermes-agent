---
sidebar_position: 4
title: "Slack"
description: "使用 Socket Mode 将 Hermes Agent 设置为 Slack 机器人"
---

# Slack 设置 {#slack-setup}

使用 Socket Mode 将 Hermes Agent 作为机器人连接到 Slack。Socket Mode 使用 WebSocket 而非
公共 HTTP 端点，因此你的 Hermes 实例无需公开访问——它可以在
防火墙后、你的笔记本电脑上或私有服务器上正常工作。

:::warning 经典 Slack 应用已弃用
<a id="classic-slack-apps-deprecated"></a>
经典 Slack 应用（使用 RTM API）已于 **2025 年 3 月完全弃用**。Hermes 使用现代的
Bolt SDK 和 Socket Mode。如果你有旧的经典应用，必须按照以下步骤创建一个新的。
:::

<a id="overview"></a>
## 概述 {#classic-slack-apps-deprecated}

| 组件 | 值 |
|-----------|-------|
| **库** | `slack-bolt` / `slack_sdk` for Python (Socket Mode) |
| **连接方式** | WebSocket — 无需公共 URL |
| **所需认证令牌** | Bot Token (`xoxb-`) + App-Level Token (`xapp-`) |
| **用户标识** | Slack 成员 ID（例如 `U01ABC2DEF3`） |

---

## 步骤 1：创建 Slack 应用 {#step-1-create-a-slack-app}

最快的方式是粘贴 Hermes 为你生成的清单。它
一次性声明了所有内置的斜杠命令（`/btw`、`/stop`、`/model`……）、
所有必需的 OAuth 作用域、所有事件订阅，并启用了 Socket
Mode。

### 选项 A：使用 Hermes 生成的清单（推荐） {#option-a-from-a-hermes-generated-manifest-recommended}

1. 生成清单：
   ```bash
   hermes slack manifest --write
   ```
   这会写入 `~/.hermes/slack-manifest.json` 并打印粘贴
   说明。
2. 前往 [https://api.slack.com/apps](https://api.slack.com/apps) →
   **创建新应用** → **从应用清单创建**
3. 选择你的工作区，粘贴 JSON 内容，检查后点击 **下一步**
   → **创建**
4. 直接跳到 **步骤 6：将应用安装到工作区**。清单已
   为你处理了作用域、事件和斜杠命令。

### 选项 B：从头开始（手动） {#option-b-from-scratch-manual}

1. 前往 [https://api.slack.com/apps](https://api.slack.com/apps)
2. 点击 **创建新应用**
3. 选择 **从头开始**
4. 输入应用名称（例如 "Hermes Agent"）并选择你的工作区
5. 点击 **创建应用**

你将进入应用的 **基本信息** 页面。继续执行下面的
步骤 2–6。

---

## 步骤 2：配置 Bot Token 作用域 {#step-2-configure-bot-token-scopes}

在侧边栏中导航到 **功能 → OAuth 与权限**。滚动到 **作用域 → Bot Token 作用域** 并添加以下内容：

| 作用域 | 用途 |
|-------|---------|
| `chat:write` | 以机器人身份发送消息 |
| `app_mentions:read` | 检测在频道中被 @提及 |
| `channels:history` | 读取机器人所在公共频道中的消息 |
| `channels:read` | 列出并获取公共频道的信息 |
| `groups:history` | 读取机器人被邀请的私有频道中的消息 |
| `im:history` | 读取直接消息历史 |
| `im:read` | 查看基本 DM 信息 |
| `im:write` | 打开并管理 DM |
| `users:read` | 查找用户信息 |
| `files:read` | 读取和下载附件文件，包括语音笔记/音频 |
| `files:write` | 上传文件（图片、音频、文档） |

<a id="missing-scopes-missing-features"></a>
:::caution 缺少作用域 = 缺少功能
如果没有 `channels:history` 和 `groups:history`，机器人 **将无法接收频道中的消息**——
它只能在 DM 中工作。如果没有 `files:read`，Hermes 可以聊天但 **无法可靠地读取用户上传的附件**。
这些是最常被遗漏的作用域。
:::
**可选作用域：**

| 作用域 | 用途 |
|-------|------|
| `groups:read` | 列出并获取私有频道的信息 |

---

## 第 3 步：启用 Socket 模式 {#step-3-enable-socket-mode}

Socket 模式让机器人通过 WebSocket 连接，无需公开 URL。

1. 在侧边栏中，进入 **Settings → Socket Mode**
2. 将 **Enable Socket Mode** 切换为 ON
3. 系统会提示你创建一个 **App-Level Token**：
   - 命名为类似 `hermes-socket`（名称不重要）
   - 添加 **`connections:write`** 作用域
   - 点击 **Generate**
4. **复制该令牌**——它以 `xapp-` 开头。这就是你的 `SLACK_APP_TOKEN`

:::tip
你随时可以在 **Settings → Basic Information → App-Level Tokens** 下找到或重新生成应用级令牌。
:::

---

## 第 4 步：订阅事件 {#step-4-subscribe-to-events}

这一步至关重要——它控制机器人能看到哪些消息。

1. 在侧边栏中，进入 **Features → Event Subscriptions**
2. 将 **Enable Events** 切换为 ON
3. 展开 **Subscribe to bot events** 并添加：

| 事件 | 是否必需 | 用途 |
|-------|----------|------|
| `message.im` | **是** | 机器人接收私信 |
| `message.channels` | **是** | 机器人接收它被加入的**公开**频道中的消息 |
| `message.groups` | **推荐** | 机器人接收它被邀请的**私有**频道中的消息 |
| `app_mention` | **是** | 防止机器人被 @提及时 Bolt SDK 报错 |

4. 点击页面底部的 **Save Changes**

:::danger 缺少事件订阅是 #1 设置问题
如果机器人在私信中正常，但在**频道中不工作**，你几乎肯定忘了添加 `message.channels`（公开频道）和/或 `message.groups`（私有频道）。没有这些事件，Slack 根本不会将频道消息传递给机器人。
:::
<a id="missing-event-subscriptions-is-the-1-setup-issue"></a>

---

## 第 5 步：启用消息选项卡 {#step-5-enable-the-messages-tab}

这一步启用与机器人的私信功能。没有它，用户尝试给机器人发私信时会看到 **“已关闭向此应用发送消息”**。

1. 在侧边栏中，进入 **Features → App Home**
2. 滚动到 **Show Tabs**
3. 将 **Messages Tab** 切换为 ON
4. 勾选 **“Allow users to send Slash commands and messages from the messages tab”**

:::danger 没有这一步，私信完全被阻止
即使拥有所有正确的作用域和事件订阅，Slack 也不会允许用户向机器人发送私信，除非消息选项卡已启用。这是 Slack 平台的要求，不是 Hermes 的配置问题。
<a id="without-this-step-dms-are-completely-blocked"></a>
:::

---

## 第 6 步：将应用安装到工作区 {#step-6-install-app-to-workspace}

1. 在侧边栏中，进入 **Settings → Install App**
2. 点击 **Install to Workspace**
3. 查看权限并点击 **Allow**
4. 授权后，你会看到一个以 `xoxb-` 开头的 **Bot User OAuth Token**
5. **复制此令牌**——这就是你的 `SLACK_BOT_TOKEN`

:::tip
如果你之后更改了作用域或事件订阅，**必须重新安装应用**才能使更改生效。Install App 页面会显示一个横幅提示你这样做。
:::

---

## 第 7 步：查找允许列表所需的用户 ID {#step-7-find-user-ids-for-the-allowlist}

Hermes 使用 Slack **成员 ID**（而非用户名或显示名称）作为允许列表。
要查找成员 ID：

1. 在 Slack 中，点击用户的姓名或头像
2. 点击 **查看完整资料**
3. 点击 **⋮**（更多）按钮
4. 选择 **复制成员 ID**

成员 ID 的格式类似 `U01ABC2DEF3`。你至少需要自己的成员 ID。

---

## 第 8 步：配置 Hermes {#step-8-configure-hermes}

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必填
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_ALLOWED_USERS=U01ABC2DEF3              # 用逗号分隔的成员 ID

# 可选
SLACK_HOME_CHANNEL=C01234567890              # 定时任务/计划消息的默认频道
SLACK_HOME_CHANNEL_NAME=general              # 主频道的可读名称（可选）
```

或者运行交互式设置：

```bash
hermes gateway setup    # 在提示时选择 Slack
```

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅限 Linux：开机自启系统服务
```

---

## 第 9 步：将机器人邀请到频道 {#step-9-invite-the-bot-to-channels}

启动网关后，你需要**邀请机器人**到你希望它响应的任何频道：

```
/invite @Hermes Agent
```

机器人**不会**自动加入频道。你必须逐个邀请它进入每个频道。

---

## 斜杠命令 {#slash-commands}

每个 Hermes 命令（`/btw`、`/stop`、`/new`、`/model`、`/help`……）
都是原生的 Slack 斜杠命令——与它们在 Telegram 和 Discord 上的工作方式完全相同。在 Slack 中输入 `/`，自动补全选择器会列出所有 Hermes 命令及其描述。

底层原理：Hermes 附带一个生成的 Slack 应用清单（参见第 1 步，选项 A），该清单将
[`COMMAND_REGISTRY`](https://github.com/NousResearch/hermes-agent/blob/main/hermes_cli/commands.py)
中的每个命令都声明为斜杠命令。在 Socket 模式下，Slack 会通过 WebSocket 路由命令事件，无论清单的 `url` 字段是什么。

### 更新后刷新斜杠命令 {#refreshing-slash-commands-after-updates}

当 Hermes 添加新命令时（例如在 `hermes update` 之后），重新生成清单并更新你的 Slack 应用：

```bash
hermes slack manifest --write
```

然后在 Slack 中：
1. 打开 [https://api.slack.com/apps](https://api.slack.com/apps) →
   你的 Hermes 应用
2. **功能 → 应用清单 → 编辑**
3. 粘贴 `~/.hermes/slack-manifest.json` 的新内容
4. **保存**。如果作用域或斜杠命令发生更改，Slack 会提示重新安装应用。

### 旧版 `/hermes <子命令>` 仍然有效 {#legacy-hermes-still-works}

为了向后兼容旧版清单，你仍然可以输入
`/hermes btw run the tests`——Hermes 会以与 `/btw
run the tests` 相同的方式路由它。自由提问也同样有效：`/hermes what's the
weather?` 会被视为普通消息。

### 高级：仅输出斜杠命令数组 {#advanced-emit-only-the-slash-commands-array}

如果你手动维护 Slack 清单，并且只需要斜杠命令列表：

```bash
hermes slack manifest --slashes-only > /tmp/slashes.json
```

将该数组粘贴到现有清单的 `features.slash_commands` 键中。
## 机器人如何响应 {#how-the-bot-responds}

了解 Hermes 在不同上下文中的行为：

| 上下文 | 行为 |
|---------|----------|
| **私信** | 机器人会响应每一条消息——无需 @提及 |
| **频道** | 机器人**仅在收到 @提及 时响应**（例如 `@Hermes Agent 现在几点？`）。在频道中，Hermes 会在该消息的线程中回复。 |
| **线程** | 如果你在现有线程中 @提及 Hermes，它会在同一线程中回复。一旦机器人在线程中有了活跃会话，**该线程中的后续回复无需 @提及**——机器人会自然地跟随对话。 |

:::tip
在频道中，始终 @提及 机器人以开始对话。一旦机器人在线程中活跃，你可以在该线程中回复而无需提及它。在线程之外，没有 @提及 的消息会被忽略，以避免在繁忙频道中产生噪音。
:::

---

## 配置选项 {#configuration-options}

除了第 8 步中必需的环境变量外，你还可以通过 `~/.hermes/config.yaml` 自定义 Slack 机器人行为。

### 线程与回复行为 {#thread-reply-behavior}

```yaml
platforms:
  slack:
    # 控制多段回复如何线程化
    # "off"   — 从不将回复线程化到原始消息
    # "first" — 第一段回复线程化到用户消息（默认）
    # "all"   — 所有段都线程化到用户消息
    reply_to_mode: "first"

    extra:
      # 是否在线程中回复（默认：true）。
      # 当为 false 时，频道消息会直接回复到频道，而不是线程。
      # 现有线程内的消息仍会在线程内回复。
      reply_in_thread: true

      # 同时将线程回复发布到主频道
      # （Slack 的“同时发送到频道”功能）。
      # 仅广播第一条回复的第一段。
      reply_broadcast: false
```

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `platforms.slack.reply_to_mode` | `"first"` | 多段消息的线程化模式：`"off"`、`"first"` 或 `"all"` |
| `platforms.slack.extra.reply_in_thread` | `true` | 当为 `false` 时，频道消息会直接回复而不是线程。现有线程内的消息仍会在线程内回复。 |
| `platforms.slack.extra.reply_broadcast` | `false` | 当为 `true` 时，线程回复也会发布到主频道。仅广播第一条回复的第一段。 |

### 会话隔离 {#session-isolation}

```yaml
# 全局设置——适用于 Slack 和所有其他平台
group_sessions_per_user: true
```

当为 `true`（默认值）时，共享频道中的每个用户都会获得自己独立的会话。两个人在 `#general` 中与 Hermes 对话将拥有不同的历史记录和上下文。

如果希望使用协作模式，即整个频道共享一个会话，则设置为 `false`。请注意，这意味着用户共享上下文增长和 token 成本，并且一个用户的 `/reset` 会清除所有人的会话。

### 提及与触发行为 {#mention-trigger-behavior}

```yaml
slack:
  # 在频道中要求 @提及（这是默认行为；
  # Slack 适配器无论如何都会在频道中强制 @提及 门控，
  # 但你可以显式设置此选项以与其他平台保持一致）
  require_mention: true

  # 阻止线程自动参与：仅回复包含显式 @提及 的频道消息。
  # 关闭此选项（默认）时，Slack 可以“自动参与”——
  # 记住线程中过去的提及，并跟进机器人消息的回复，
  # 无需新的提及即可恢复活跃会话。
  # 开启 strict_mention 时，每条新的频道消息必须 @提及 机器人，
  # Hermes 才会响应。
  strict_mention: false

  # 触发机器人的自定义提及模式
  # （除了默认的 @提及 检测之外）
  mention_patterns:
    - "hey hermes"
    - "hermes,"

  # 附加到每条传出消息前的文本
  reply_prefix: ""
```
:::tip 何时使用 `strict_mention`
在繁忙的工作区中，如果 Slack 默认的“机器人会记住这个线程”行为让用户感到意外，请将此选项设为 `true`——例如，在一个很长的技术支持线程中，机器人在开头提供了帮助，而你希望它保持沉默，除非再次被明确 @提及。私信和活跃的交互会话不受影响。
:::

:::info
Slack 支持两种模式：默认情况下需要 `@提及` 才能开始对话，但你可以通过 `SLACK_FREE_RESPONSE_CHANNELS`（逗号分隔的频道 ID）或 `config.yaml` 中的 `slack.free_response_channels` 为特定频道选择退出。一旦机器人在某个线程中拥有活跃会话，后续的线程回复就不需要提及。在私信中，机器人始终无需提及即可回复。
:::
<a id="when-to-use-strictmention"></a>

### 未授权用户处理 {#unauthorized-user-handling}

```yaml
slack:
  # 当未授权用户（不在 SLACK_ALLOWED_USERS 中）向机器人发送私信时发生什么
  # "pair"   — 提示他们输入配对码（默认）
  # "ignore" — 静默丢弃消息
  unauthorized_dm_behavior: "pair"
```

你也可以在所有平台上全局设置此选项：

```yaml
unauthorized_dm_behavior: "pair"
```

`slack:` 下的平台特定设置会覆盖全局设置。

### 语音转录 {#voice-transcription}

```yaml
# 全局设置 — 启用/禁用传入语音消息的自动转录
stt_enabled: true
```

当设为 `true`（默认值）时，传入的音频消息会在被 Agent 处理之前，使用配置的 STT 提供程序自动转录。

### 完整示例 {#full-example}

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


## 主页频道 {#home-channel}

将 `SLACK_HOME_CHANNEL` 设置为一个频道 ID，Hermes 将在此处投递定时消息、cron 任务结果以及其他主动通知。要查找频道 ID：

1. 在 Slack 中右键点击频道名称
2. 点击 **查看频道详情**
3. 滚动到底部 — 频道 ID 会显示在那里

```bash
SLACK_HOME_CHANNEL=C01234567890
```

确保机器人已被 **邀请到该频道**（`/invite @Hermes Agent`）。

---

## 多工作区支持 {#multi-workspace-support}

Hermes 可以使用单个网关实例同时连接到 **多个 Slack 工作区**。每个工作区使用自己的机器人用户 ID 独立进行身份验证。

### 配置 {#configuration}

在 `SLACK_BOT_TOKEN` 中提供多个机器人令牌，以 **逗号分隔列表** 的形式：

```bash
# 多个机器人令牌 — 每个工作区一个
SLACK_BOT_TOKEN=xoxb-workspace1-token,xoxb-workspace2-token,xoxb-workspace3-token

# 单个应用级令牌仍用于 Socket Mode
SLACK_APP_TOKEN=xapp-your-app-token
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
platforms:
  slack:
    token: "xoxb-workspace1-token,xoxb-workspace2-token"
```

### OAuth 令牌文件 {#oauth-token-file}
除了环境变量或配置文件中的令牌外，Hermes 还会从 **OAuth 令牌文件** 加载令牌，路径为：

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

### 工作原理 {#how-it-works}

- 列表中的**第一个令牌**是主令牌，用于 Socket Mode 连接（AsyncApp）。
- 启动时，每个令牌都会通过 `auth.test` 进行身份验证。网关将每个 `team_id` 映射到其自己的 `WebClient` 和 `bot_user_id`。
- 当消息到达时，Hermes 使用正确的工作区专属客户端进行响应。
- 主 `bot_user_id`（来自第一个令牌）用于向后兼容那些期望单一机器人身份的功能。

---

## 语音消息 {#voice-messages}

Hermes 支持 Slack 上的语音功能：

- **接收：** 语音/音频消息会自动使用配置的 STT 提供商进行转录：本地 `faster-whisper`、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）
- **发送：** TTS 响应会作为音频文件附件发送

---

## 按频道提示 {#per-channel-prompts}

为特定 Slack 频道分配临时系统提示。该提示在每次对话轮次中运行时注入——从不持久化到对话历史记录中——因此更改会立即生效。

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

键是 Slack 频道 ID（通过频道详情 → “关于” → 滚动到底部找到）。匹配频道中的所有消息都会将提示作为临时系统指令注入。

## 按频道技能绑定 {#per-channel-skill-bindings}

当特定频道或私聊中启动新会话时，自动加载一个技能。与按频道提示（每次对话轮次都注入）不同，技能绑定会在**会话启动时**将技能内容作为用户消息注入——它会成为对话历史的一部分，后续轮次无需重新加载。

这对于具有专用用途的私聊或频道（如闪卡、特定领域的问答机器人、支持分类频道等）非常理想，在这些场景中，你不希望模型自己的技能选择器在每次简短回复时都决定是否加载技能。

```yaml
slack:
  channel_skill_bindings:
    # 私聊频道——始终以“german-flashcards”模式运行
    - id: "D0ATH9TQ0G6"
      skills:
        - german-flashcards
    # 研究频道——按顺序预加载多个技能
    - id: "C01RESEARCH"
      skills:
        - arxiv
        - writing-plans
    # 简写形式：单个技能作为字符串
    - id: "C02SUPPORT"
      skill: hubspot-on-demand
```

注意：
- 绑定通过频道 ID 匹配。对于绑定频道中的线程消息，线程会继承父频道的绑定。
- 技能仅在会话启动时加载（新会话或自动重置后）。如果更改了绑定，请运行 `/new` 或等待会话自动重置以使其生效。
- 可与 `channel_prompts` 结合使用，在技能指令之上为每个频道设置语气/约束。
## 故障排除 {#troubleshooting}

| 问题 | 解决方案 |
|------|----------|
| Bot 不响应私信 | 确认 `message.im` 已在事件订阅中，并重新安装应用 |
| Bot 在私信中正常，但在频道中失效 | **最常见问题。** 在事件订阅中添加 `message.channels` 和 `message.groups`，重新安装应用，然后使用 `/invite @Hermes Agent` 将 bot 邀请到频道 |
| Bot 不响应频道中的 @提及 | 1) 检查是否订阅了 `message.channels` 事件。2) Bot 必须被邀请到频道。3) 确保添加了 `channels:history` 权限范围。4) 修改权限/事件后重新安装应用 |
| Bot 忽略私有频道中的消息 | 同时添加 `message.groups` 事件订阅和 `groups:history` 权限范围，然后重新安装应用并使用 `/invite` 邀请 bot |
| 私信中显示“已关闭向此应用发送消息” | 在 App Home 设置中启用**消息 Tab**（参见步骤 5） |
| 出现 "not_authed" 或 "invalid_auth" 错误 | 重新生成 Bot Token 和 App Token，更新 `.env` 文件 |
| Bot 能响应但无法在频道中发帖 | 使用 `/invite @Hermes Agent` 将 bot 邀请到频道 |
| Bot 可以对话但无法读取上传的图片/文件 | 添加 `files:read`，然后**重新安装**应用。当 Slack 返回作用域/授权/权限失败时，Hermes 现在会在聊天中显示附件访问诊断信息。 |
| `missing_scope` 错误 | 在 OAuth & Permissions 中添加所需的作用域，然后**重新安装**应用 |
| Socket 频繁断开 | 检查网络；Bolt 会自动重连，但不稳定的连接会导致延迟 |
| 更改了作用域/事件但没有任何变化 | 在修改作用域或事件订阅后，你**必须重新安装**应用到工作空间 |

### 快速检查清单 {#quick-checklist}

如果 bot 在频道中无法工作，请验证**所有**以下项目：

1. ✅ 已订阅 `message.channels` 事件（针对公开频道）
2. ✅ 已订阅 `message.groups` 事件（针对私有频道）
3. ✅ 已订阅 `app_mention` 事件
4. ✅ 已添加 `channels:history` 作用域（针对公开频道）
5. ✅ 已添加 `groups:history` 作用域（针对私有频道）
6. ✅ 添加作用域/事件后已**重新安装**应用
7. ✅ Bot 已被**邀请**到频道（`/invite @Hermes Agent`）
8. ✅ 在消息中使用了 **@提及** bot

---

## 安全 {#security}

:::warning
**始终使用授权用户的 Member ID 设置 `SLACK_ALLOWED_USERS`**。如果没有此设置，网关将默认**拒绝所有消息**作为安全措施。切勿共享你的 bot 令牌——像对待密码一样对待它们。
:::

- 令牌应存储在 `~/.hermes/.env` 中（文件权限 `600`）
- 定期通过 Slack 应用设置轮换令牌
- 审计哪些人可以访问你的 Hermes 配置目录
- Socket 模式意味着没有公开端点暴露——减少一个攻击面
