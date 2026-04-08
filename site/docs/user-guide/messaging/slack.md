---
sidebar_position: 4
title: "Slack"
description: "使用 Socket 模式将 Hermes Agent 设置为 Slack 机器人"
---

# Slack 设置

通过 Socket 模式将 Hermes Agent 作为机器人连接到 Slack。Socket 模式使用 WebSockets 而不是公共 HTTP 端点，因此你的 Hermes 实例不需要公开访问权限 —— 它可以在防火墙后、笔记本电脑上或私有服务器上运行。

:::warning 经典 Slack 应用已弃用
经典 Slack 应用（使用 RTM API）已于 **2025 年 3 月完全弃用**。Hermes 使用现代的 Bolt SDK 和 Socket 模式。如果你有一个旧的经典应用，必须按照以下步骤创建一个新应用。
:::

## 概览

| 组件 | 值 |
|-----------|-------|
| **库** | Python 版 `slack-bolt` / `slack_sdk` (Socket 模式) |
| **连接方式** | WebSocket — 无需公共 URL |
| **所需认证令牌** | Bot Token (`xoxb-`) + App-Level Token (`xapp-`) |
| **用户识别** | Slack Member ID (例如 `U01ABC2DEF3`) |

---

## 第 1 步：创建 Slack 应用

1. 访问 [https://api.slack.com/apps](https://api.slack.com/apps)
2. 点击 **Create New App**
3. 选择 **From scratch**
4. 输入应用名称（例如 "Hermes Agent"）并选择你的工作区 (workspace)
5. 点击 **Create App**

你将进入应用的 **Basic Information** 页面。

---

## 第 2 步：配置 Bot Token 权限范围 (Scopes)

在侧边栏导航至 **Features → OAuth & Permissions**。滚动到 **Scopes → Bot Token Scopes** 并添加以下内容：

| 权限范围 (Scope) | 用途 |
|-------|---------|
| `chat:write` | 以机器人身份发送消息 |
| `app_mentions:read` | 检测频道中何时被 @提及 |
| `channels:history` | 读取机器人所在公共频道的消息 |
| `channels:read` | 列出并获取公共频道的信息 |
| `groups:history` | 读取机器人被邀请加入的私有频道的消息 |
| `im:history` | 读取直接消息 (DM) 历史记录 |
| `im:read` | 查看基本的 DM 信息 |
| `im:write` | 开启并管理 DM |
| `users:read` | 查询用户信息 |
| `files:write` | 上传文件（图片、音频、文档） |

:::caution 缺少权限 = 功能缺失
如果没有 `channels:history` 和 `groups:history`，机器人将**无法接收频道中的消息** —— 它只能在 DM 中工作。这些是最容易被遗漏的权限。
:::

**可选权限：**

| 权限范围 (Scope) | 用途 |
|-------|---------|
| `groups:read` | 列出并获取私有频道的信息 |

---

## 第 3 步：启用 Socket 模式

Socket 模式允许机器人通过 WebSocket 连接，而不需要公共 URL。

1. 在侧边栏中，前往 **Settings → Socket Mode**
2. 将 **Enable Socket Mode** 切换为 ON
3. 系统会提示你创建一个 **App-Level Token**：
   - 将其命名为类似 `hermes-socket` 的名称（名称不重要）
   - 添加 **`connections:write`** 权限范围
   - 点击 **Generate**
4. **复制该令牌** —— 它以 `xapp-` 开头。这就是你的 `SLACK_APP_TOKEN`

:::tip
你随时可以在 **Settings → Basic Information → App-Level Tokens** 下找到或重新生成应用级令牌。
:::

---

## 第 4 步：订阅事件 (Events)

这一步至关重要 —— 它决定了机器人可以看到哪些消息。

1. 在侧边栏中，前往 **Features → Event Subscriptions**
2. 将 **Enable Events** 切换为 ON
3. 展开 **Subscribe to bot events** 并添加：

| 事件 | 必选？ | 用途 |
|-------|-----------|---------|
| `message.im` | **是** | 机器人接收直接消息 (DM) |
| `message.channels` | **是** | 机器人接收其加入的**公共**频道中的消息 |
| `message.groups` | **推荐** | 机器人接收其被邀请加入的**私有**频道中的消息 |
| `app_mention` | **是** | 防止机器人在被 @提及 时出现 Bolt SDK 错误 |

4. 点击页面底部的 **Save Changes**

:::danger 遗漏事件订阅是排名第一的设置问题
如果机器人在 DM 中工作但在**频道中不工作**，你几乎肯定忘记了添加 `message.channels`（针对公共频道）和/或 `message.groups`（针对私有频道）。如果没有这些事件，Slack 根本不会将频道消息推送给机器人。
:::

---

## 第 5 步：启用 Messages 标签页

这一步允许用户向机器人发送直接消息。如果不开启，用户在尝试给机器人发私信时会看到 **"Sending messages to this app has been turned off"**。

1. 在侧边栏中，前往 **Features → App Home**
2. 滚动到 **Show Tabs**
3. 将 **Messages Tab** 切换为 ON
4. 勾选 **"Allow users to send Slash commands and messages from the messages tab"**

:::danger 不做这一步，DM 将被完全阻断
即使拥有所有正确的权限范围和事件订阅，除非启用了 Messages 标签页，否则 Slack 不允许用户向机器人发送直接消息。这是 Slack 平台的要求，不是 Hermes 的配置问题。
:::

---

## 第 6 步：将应用安装到工作区

1. 在侧边栏中，前往 **Settings → Install App**
2. 点击 **Install to Workspace**
3. 检查权限并点击 **Allow**
4. 授权后，你将看到一个以 `xoxb-` 开头的 **Bot User OAuth Token**
5. **复制该令牌** —— 这就是你的 `SLACK_BOT_TOKEN`

:::tip
如果你以后更改了权限范围或事件订阅，**必须重新安装应用**才能使更改生效。安装应用页面会显示一个横幅提示你执行此操作。
:::

---

## 第 7 步：查找允许列表的 User ID

Hermes 使用 Slack **Member ID**（不是用户名或显示名称）作为允许列表。

查找 Member ID 的方法：

1. 在 Slack 中，点击用户的姓名或头像
2. 点击 **View full profile**
3. 点击 **⋮** (更多) 按钮
4. 选择 **Copy member ID**

Member ID 看起来像 `U01ABC2DEF3`。你至少需要自己的 Member ID。

---

## 第 8 步：配置 Hermes

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必填
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_ALLOWED_USERS=U01ABC2DEF3              # 逗号分隔的 Member ID

# 选填
SLACK_HOME_CHANNEL=C01234567890              # 用于 cron/定时消息的默认频道
SLACK_HOME_CHANNEL_NAME=general              # 主频道的易读名称（可选）
```

或者运行交互式设置：

```bash
hermes gateway setup    # 在提示时选择 Slack
```

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 作为用户服务安装
sudo hermes gateway install --system   # 仅限 Linux：开机自启系统服务
```

---

## 第 9 步：邀请机器人进入频道

启动网关后，你需要将**机器人邀请**到任何你希望它响应的频道：

```
/invite @Hermes Agent
```

机器人**不会**自动加入频道。你必须手动将它邀请到每个频道。

---

## 机器人如何响应

了解 Hermes 在不同场景下的行为：

| 场景 | 行为 |
|---------|----------|
| **直接消息 (DM)** | 机器人响应每一条消息 —— 无需 @提及 |
| **频道 (Channels)** | 机器人**仅在被 @提及 时响应**（例如 `@Hermes Agent 现在几点了？`）。在频道中，Hermes 会在该消息下方的线程 (thread) 中回复。 |
| **线程 (Threads)** | 如果你在现有线程中 @提及 Hermes，它会在同一线程中回复。一旦 Agent 在线程中有了活动会话，**该线程中的后续回复不需要 @提及** —— Agent 会自然地跟随对话。 |

:::tip
在频道中，请始终通过 @提及 机器人来开始对话。一旦机器人进入线程，你就可以在不提及它的情况下进行回复。在线程之外，没有 @提及 的消息将被忽略，以防止干扰繁忙的频道。
:::

---

## 配置选项

除了第 8 步中必需的环境变量外，你还可以通过 `~/.hermes/config.yaml` 自定义 Slack 机器人的行为。

### 线程与回复行为

```yaml
platforms:
  slack:
    # 控制多部分响应如何形成线程
    # "off"   — 永远不将回复挂载到原始消息的线程下
    # "first" — 只有第一块回复挂载到用户消息的线程下（默认）
    # "all"   — 所有回复块都挂载到用户消息的线程下
    reply_to_mode: "first"

    extra:
      # 是否在线程中回复（默认：true）。
      # 为 false 时，频道消息将直接在频道中回复，而不是开启线程。
      # 已经在现有线程内的消息仍会在线程内回复。
      reply_in_thread: true

      # 同时将线程回复发布到主频道
      # (Slack 的 "Also send to channel" 功能)。
      # 只有第一次回复的第一块内容会被广播。
      reply_broadcast: false
```
| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `platforms.slack.reply_to_mode` | `"first"` | 多部分消息的回复模式：`"off"`（关闭）、`"first"`（仅回复第一部分）或 `"all"`（全部回复） |
| `platforms.slack.extra.reply_in_thread` | `true` | 当为 `false` 时，频道消息将直接回复而非开启线程。已在线程内的消息仍会在线程内回复。 |
| `platforms.slack.extra.reply_broadcast` | `false` | 当为 `true` 时，线程回复也会同步发布到主频道。仅第一部分内容会被广播。 |

### 会话隔离 (Session Isolation)

```yaml
# 全局设置 — 适用于 Slack 及所有其他平台
group_sessions_per_user: true
```

当设置为 `true`（默认值）时，共享频道中的每个用户都拥有自己独立的对话会话。在 `#general` 频道中与 Hermes 交流的两个人将拥有各自独立的上下文和历史记录。

如果你希望开启协作模式，让整个频道共享同一个对话会话，请将其设置为 `false`。请注意，这意味着用户将共享上下文长度和 Token 成本，且任何一名用户执行 `/reset` 都会清除所有人的会话。

### 提及与触发行为 (Mention & Trigger Behavior)

```yaml
slack:
  # 在频道中是否需要 @mention（这是默认行为；
  # Slack 适配器在频道中强制执行 @mention 门控，
  # 但你可以显式设置此项以保持与其他平台的一致性）
  require_mention: true

  # 触发 Agent 的自定义提及模式
  # （除了默认的 @mention 检测之外）
  mention_patterns:
    - "hey hermes"
    - "hermes,"

  # 附加在每条回复消息前的文本前缀
  reply_prefix: ""
```

:::info
与 Discord 和 Telegram 不同，Slack 没有等效的 `free_response_channels` 设置。Slack 适配器要求在频道中必须通过 `@mention` 来开启对话。不过，一旦 Agent 在某个线程中有了活跃会话，后续的线程回复则不需要提及。在私聊（DM）中，Agent 始终会直接响应，无需提及。
:::

### 未授权用户处理

```yaml
slack:
  # 当未授权用户（不在 SLACK_ALLOWED_USERS 中）给 Agent 发私聊时如何处理
  # "pair"   — 提示他们输入配对码（默认）
  # "ignore" — 静默丢弃消息
  unauthorized_dm_behavior: "pair"
```

你也可以为所有平台进行全局设置：

```yaml
unauthorized_dm_behavior: "pair"
```

`slack:` 下的平台特定设置优先级高于全局设置。

### 语音转文字 (Voice Transcription)

```yaml
# 全局设置 — 启用/禁用对传入语音消息的自动转录
stt_enabled: true
```

当设置为 `true`（默认值）时，传入的音频消息在由 Agent 处理之前，将使用配置的 STT 服务商自动转录为文字。

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

## Home 频道

设置 `SLACK_HOME_CHANNEL` 为一个频道 ID，Hermes 将在该频道发送定时消息、Cron 任务结果和其他主动通知。获取频道 ID 的方法：

1. 在 Slack 中右键点击频道名称
2. 点击 **查看频道详情 (View channel details)**
3. 滚动到底部 — 频道 ID (Channel ID) 显示在那里

```bash
SLACK_HOME_CHANNEL=C01234567890
```

请确保已将 Agent **邀请至该频道** (`/invite @Hermes Agent`)。

---

## 多工作区支持 (Multi-Workspace Support)

Hermes 可以使用单个网关实例同时连接到**多个 Slack 工作区**。每个工作区都使用其独立的 Bot Token 进行身份验证。

### 配置

在 `SLACK_BOT_TOKEN` 中提供多个以**逗号分隔**的 Bot Token：

```bash
# 多个 Bot Token — 每个工作区一个
SLACK_BOT_TOKEN=xoxb-workspace1-token,xoxb-workspace2-token,xoxb-workspace3-token

# Socket 模式仍使用单个 App-level Token
SLACK_APP_TOKEN=xapp-your-app-token
```

或者在 `~/.hermes/config.yaml` 中配置：

```yaml
platforms:
  slack:
    token: "xoxb-workspace1-token,xoxb-workspace2-token"
```

### OAuth Token 文件

除了环境变量或配置文件中的 Token，Hermes 还会从以下路径的 **OAuth Token 文件**中加载 Token：

```
~/.hermes/slack_tokens.json
```

该文件是一个将 Team ID 映射到 Token 条目的 JSON 对象：

```json
{
  "T01ABC2DEF3": {
    "token": "xoxb-workspace-token-here",
    "team_name": "My Workspace"
  }
}
```

此文件中的 Token 会与 `SLACK_BOT_TOKEN` 指定的 Token 合并。重复的 Token 会被自动去重。

### 工作原理

- 列表中的**第一个 Token** 是主 Token，用于 Socket 模式连接 (AsyncApp)。
- 启动时，每个 Token 都会通过 `auth.test` 进行验证。网关会将每个 `team_id` 映射到其专属的 `WebClient` 和 `bot_user_id`。
- 当消息到达时，Hermes 会使用对应工作区的客户端进行回复。
- 主 `bot_user_id`（来自第一个 Token）用于向后兼容那些预期单一 Bot 身份的功能。

---

## 语音消息

Hermes 在 Slack 上支持语音功能：

- **接收：** 语音/音频消息将使用配置的 STT 服务商自动转录：本地 `faster-whisper`、Groq Whisper (`GROQ_API_KEY`) 或 OpenAI Whisper (`VOICE_TOOLS_OPENAI_KEY`)。
- **发送：** TTS 回复将作为音频文件附件发送。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| Agent 不回复私聊 (DM) | 确认事件订阅中包含 `message.im` 且应用已重新安装 |
| Agent 在私聊中正常但在频道中无效 | **最常见的问题。** 在事件订阅中添加 `message.channels` 和 `message.groups`，重新安装应用，并使用 `/invite @Hermes Agent` 邀请 Agent 进入频道 |
| Agent 不响应频道中的 @mentions | 1) 检查是否订阅了 `message.channels` 事件。2) Agent 必须被邀请进频道。3) 确保添加了 `channels:history` 权限范围。4) 修改权限或事件后必须重新安装应用 |
| Agent 忽略私有频道中的消息 | 同时添加 `message.groups` 事件订阅和 `groups:history` 权限范围，然后重新安装应用并 `/invite` Agent |
| 私聊中显示 "Sending messages to this app has been turned off" | 在 App Home 设置中启用 **Messages Tab**（参见步骤 5） |
| "not_authed" 或 "invalid_auth" 错误 | 重新生成 Bot Token 和 App Token，并更新 `.env` |
| Agent 有响应但无法在频道发帖 | 使用 `/invite @Hermes Agent` 将 Agent 邀请进频道 |
| "missing_scope" 错误 | 在 OAuth & Permissions 中添加所需的权限范围，然后**重新安装**应用 |
| Socket 频繁断开 | 检查网络；Bolt 会自动重连，但连接不稳定会导致延迟 |
| 修改了权限范围/事件但没生效 | 在任何权限范围或事件订阅更改后，你**必须重新安装**应用到工作区 |

### 快速检查清单

如果 Agent 在频道中无法工作，请核对以下**所有**事项：

1. ✅ 已订阅 `message.channels` 事件（用于公开频道）
2. ✅ 已订阅 `message.groups` 事件（用于私有频道）
3. ✅ 已订阅 `app_mention` 事件
4. ✅ 已添加 `channels:history` 权限范围（用于公开频道）
5. ✅ 已添加 `groups:history` 权限范围（用于私有频道）
6. ✅ 添加权限/事件后已**重新安装**应用
7. ✅ 已将 Agent **邀请**进频道 (`/invite @Hermes Agent`)
8. ✅ 你在消息中 **@提及** 了 Agent

---

## 安全性

:::warning
**务必设置 `SLACK_ALLOWED_USERS`**，填入授权用户的 Member ID。如果没有此设置，作为安全措施，网关默认会**拒绝所有消息**。切勿分享你的 Bot Token —— 请像对待密码一样对待它们。
:::

- Token 应存储在 `~/.hermes/.env` 中（文件权限设为 `600`）
- 定期通过 Slack 应用设置轮换 Token
- 审计谁有权访问你的 Hermes 配置目录
- Socket 模式意味着不需要暴露公网端点 —— 减少了一个攻击面
