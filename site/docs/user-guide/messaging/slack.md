---
sidebar_position: 4
title: "Slack"
description: "使用 Socket Mode 将 Hermes Agent 设置为 Slack 机器人"
---

# Slack 设置 {#slack-setup}

使用 Socket Mode 将 Hermes Agent 作为机器人连接到 Slack。Socket Mode 使用 WebSocket 而非公共 HTTP 端点，因此你的 Hermes 实例无需公开可访问——它可以在防火墙后、你的笔记本电脑上或私有服务器上工作。

:::warning 经典 Slack 应用已弃用
经典 Slack 应用（使用 RTM API）**已于 2025 年 3 月完全弃用**。Hermes 使用支持 Socket Mode 的现代 Bolt SDK。如果你有旧的经典应用，必须按照以下步骤创建一个新的。
:::

## 概述 {#overview}
<a id="classic-slack-apps-deprecated"></a>

| 组件 | 值 |
|-----------|-------|
| **库** | Python 的 `slack-bolt` / `slack_sdk`（Socket Mode） |
| **连接** | WebSocket —— 无需公共 URL |
| **所需认证令牌** | 机器人令牌 (`xoxb-`) + 应用级令牌 (`xapp-`) |
| **用户标识** | Slack 成员 ID（例如 `U01ABC2DEF3`） |

---

## 步骤 1：创建 Slack 应用 {#step-1-create-a-slack-app}

1.  访问 [https://api.slack.com/apps](https://api.slack.com/apps)
2.  点击 **Create New App**
3.  选择 **From scratch**
4.  输入应用名称（例如 "Hermes Agent"）并选择你的工作区
5.  点击 **Create App**

你将进入应用的 **Basic Information** 页面。

---

## 步骤 2：配置机器人令牌权限范围 {#step-2-configure-bot-token-scopes}

在侧边栏中导航到 **Features → OAuth & Permissions**。滚动到 **Scopes → Bot Token Scopes** 并添加以下权限：

| 权限范围 | 用途 |
|-------|---------|
| `chat:write` | 以机器人身份发送消息 |
| `app_mentions:read` | 检测在频道中被 @提及 |
| `channels:history` | 读取机器人所在公共频道中的消息 |
| `channels:read` | 列出和获取公共频道信息 |
| `groups:history` | 读取机器人被邀请加入的私密频道中的消息 |
| `im:history` | 读取直接消息历史记录 |
| `im:read` | 查看基本 DM 信息 |
| `im:write` | 打开和管理 DM |
| `users:read` | 查找用户信息 |
| `files:read` | 读取和下载附件，包括语音笔记/音频 |
| `files:write` | 上传文件（图像、音频、文档） |

:::caution 缺少权限范围 = 缺少功能
没有 `channels:history` 和 `groups:history`，机器人**将无法接收频道中的消息**——它只能在 DM 中工作。这些是最常被遗漏的权限范围。
:::
<a id="missing-scopes-missing-features"></a>

**可选权限范围：**

| 权限范围 | 用途 |
|-------|---------|
| `groups:read` | 列出和获取私密频道信息 |

---

## 步骤 3：启用 Socket Mode {#step-3-enable-socket-mode}

Socket Mode 允许机器人通过 WebSocket 连接，而无需公共 URL。

1.  在侧边栏中，转到 **Settings → Socket Mode**
2.  将 **Enable Socket Mode** 开关切换到 ON
3.  系统将提示你创建 **App-Level Token**：
   - 为其命名，例如 `hermes-socket`（名称无关紧要）
   - 添加 **`connections:write`** 权限范围
   - 点击 **Generate**
4.  **复制令牌**——它以 `xapp-` 开头。这就是你的 `SLACK_APP_TOKEN`

:::tip
你始终可以在 **Settings → Basic Information → App-Level Tokens** 下找到或重新生成应用级令牌。
:::

---

## 步骤 4：订阅事件 {#step-4-subscribe-to-events}

此步骤至关重要——它控制机器人可以接收哪些消息。

1.  在侧边栏中，转到 **Features → Event Subscriptions**
2.  将 **Enable Events** 开关切换到 ON
3.  展开 **Subscribe to bot events** 并添加：

| 事件 | 是否必需？ | 用途 |
|-------|-----------|---------|
| `message.im` | **是** | 机器人接收直接消息 |
| `message.channels` | **是** | 机器人接收其加入的**公共**频道中的消息 |
| `message.groups` | **推荐** | 机器人接收其被邀请加入的**私密**频道中的消息 |
| `app_mention` | **是** | 当机器人被 @提及时，防止 Bolt SDK 出错 |

4.  点击页面底部的 **Save Changes**

:::danger 缺少事件订阅是头号设置问题
<a id="missing-event-subscriptions-is-the-1-setup-issue"></a>
如果机器人在 DM 中工作但**在频道中不工作**，你几乎肯定是忘记了添加 `message.channels`（用于公共频道）和/或 `message.groups`（用于私密频道）。没有这些事件，Slack 根本不会向机器人传递频道消息。
:::

---

## 步骤 5：启用消息选项卡 {#step-5-enable-the-messages-tab}
这一步启用与机器人的直接消息功能。如果不做这一步，用户在尝试向机器人发送私信时会看到 **“向此应用发送消息功能已关闭”**。

1. 在侧边栏中，转到 **功能 → 应用主页**
2. 向下滚动至 **显示选项卡**
3. 将 **消息选项卡** 切换为 ON
4. 勾选 **“允许用户在消息选项卡中发送斜杠命令和消息”**

<a id="without-this-step-dms-are-completely-blocked"></a>
:::danger 不做这一步，私信将被完全阻止
即使所有权限范围和事件订阅都配置正确，除非消息选项卡被启用，Slack 将不允许用户向机器人发送直接消息。这是 Slack 平台的要求，不是 Hermes 配置问题。
:::

---

<a id="step-6-install-app-to-workspace"></a>
## 步骤 6：将应用安装到工作区 {#without-this-step-dms-are-completely-blocked}

1. 在侧边栏中，转到 **设置 → 安装应用**
2. 点击 **安装到工作区**
3. 查看权限并点击 **允许**
4. 授权后，你会看到一个以 `xoxb-` 开头的 **Bot User OAuth Token**
5. **复制这个令牌** — 这就是你的 `SLACK_BOT_TOKEN`

:::tip
如果你后续更改了权限范围或事件订阅，**必须重新安装应用**才能使更改生效。安装应用页面会显示横幅提示你这样做。
:::

---

## 步骤 7：为允许列表查找用户 ID {#step-7-find-user-ids-for-the-allowlist}

Hermes 使用 Slack **成员 ID**（而非用户名或显示名称）作为允许列表。

查找成员 ID 的方法：

1. 在 Slack 中，点击用户的姓名或头像
2. 点击 **查看完整资料**
3. 点击 **⋮** （更多）按钮
4. 选择 **复制成员 ID**

成员 ID 看起来像 `U01ABC2DEF3`。你至少需要你自己的成员 ID。

---

## 步骤 8：配置 Hermes {#step-8-configure-hermes}

在你的 `~/.hermes/.env` 文件中添加以下内容：

```bash
# 必填项
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_ALLOWED_USERS=U01ABC2DEF3              # 逗号分隔的成员 ID

# 可选项
SLACK_HOME_CHANNEL=C01234567890              # Cron/定时消息的默认频道
SLACK_HOME_CHANNEL_NAME=general              # 主频道的人类可读名称（可选）
```

或者运行交互式设置：

```bash
hermes gateway setup    # 提示时选择 Slack
```

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅 Linux：启动时系统服务
```

---

## 步骤 9：邀请机器人加入频道 {#step-9-invite-the-bot-to-channels}

启动网关后，你需要 **邀请机器人** 加入任何你希望它响应的频道：

```
/invite @Hermes Agent
```

机器人不会自动加入频道。你必须单独邀请它加入每个频道。

---

## 机器人的响应方式 {#how-the-bot-responds}

了解 Hermes 在不同上下文中的行为：

| 上下文 | 行为 |
|---------|----------|
| **私信** | 机器人响应每一条消息 — 无需 @提及 |
| **频道** | 机器人 **仅在 @提及时响应**（例如，`@Hermes Agent 现在几点？`）。在频道中，Hermes 会作为该消息的线程回复。 |
| **线程** | 如果你在现有线程内 @提及 Hermes，它会在同一个线程回复。一旦机器人在线程中激活了会话，**该线程内的后续回复无需 @提及** — 机器人会自然地跟随对话。 |

:::tip
在频道中，始终通过 @提及机器人来开启对话。一旦机器人在线程中激活，你可以在该线程内回复而无需提及它。在非线程上下文（即主频道）中，没有 @提及的消息会被忽略，以防止在繁忙的频道中产生噪音。
:::

---

## 配置选项 {#configuration-options}

除了步骤 8 中必需的环境变量，你还可以通过 `~/.hermes/config.yaml` 自定义 Slack 机器人行为。

### 线程和回复行为 {#thread-reply-behavior}

```yaml
platforms:
  slack:
    # 控制如何将多部分响应作为线程回复
    # "off"   — 从不将回复作为原消息的线程
    # "first" — 第一个块作为用户消息的线程（默认）
    # "all"   — 所有块都作为用户消息的线程
    reply_to_mode: "first"

    extra:
      # 是否在线程中回复（默认：true）。
      # 当为 false 时，频道消息会直接在频道中回复，
      # 而不是作为线程。已在现有线程内的消息仍会在线程内回复。
      reply_in_thread: true

      # 同时将线程回复发布到主频道
      # （Slack 的“同时发送到频道”功能）。
      # 只有第一个回复的第一个块会被广播。
      reply_broadcast: false
```
| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `platforms.slack.reply_to_mode` | `"first"` | 多部分消息的线程模式：`"off"`、`"first"` 或 `"all"` |
| `platforms.slack.extra.reply_in_thread` | `true` | 当为 `false` 时，频道消息会得到直接回复而非线程回复。现有线程内的消息仍会在线程内回复。 |
| `platforms.slack.extra.reply_broadcast` | `false` | 当为 `true` 时，线程回复也会发布到主频道。仅第一个消息块会被广播。 |

### 会话隔离 {#session-isolation}

```yaml
# 全局设置 — 适用于 Slack 及所有其他平台
group_sessions_per_user: true
```

当设置为 `true`（默认值）时，共享频道中的每个用户都拥有自己独立的对话会话。两个人在 `#general` 频道与 Hermes 交谈时，会有各自独立的历史记录和上下文。

如果希望整个频道共享一个对话会话的协作模式，请设置为 `false`。请注意，这意味着用户将共享上下文增长和令牌成本，并且一个用户的 `/reset` 命令会为所有人清除会话。

### 提及与触发行为 {#mention-trigger-behavior}

```yaml
slack:
  # 在频道中要求 @提及（这是默认行为；
  # Slack 适配器无论如何都会在频道中强制要求 @提及，
  # 但你可以显式设置此项以与其他平台保持一致）
  require_mention: true

  # 触发机器人的自定义提及模式
  # （除了默认的 @提及检测之外）
  mention_patterns:
    - "hey hermes"
    - "hermes,"

  # 在每个发出消息前添加的文本
  reply_prefix: ""
```

:::info
Slack 支持两种模式：默认情况下需要 `@提及` 来开始对话，但你可以通过 `SLACK_FREE_RESPONSE_CHANNELS`（逗号分隔的频道 ID）或 `config.yaml` 中的 `slack.free_response_channels` 来为特定频道选择退出此要求。一旦机器人在一个线程中拥有活跃会话，后续的线程回复就不再需要提及。在私信中，机器人总是无需提及即可回复。
:::

### 未授权用户处理 {#unauthorized-user-handling}

```yaml
slack:
  # 当未授权用户（不在 SLACK_ALLOWED_USERS 中）向机器人发送私信时的处理方式
  # "pair"   — 提示他们输入配对码（默认）
  # "ignore" — 静默丢弃消息
  unauthorized_dm_behavior: "pair"
```

你也可以为所有平台全局设置此选项：

```yaml
unauthorized_dm_behavior: "pair"
```

`slack:` 下的平台特定设置优先级高于全局设置。

### 语音转录 {#voice-transcription}

```yaml
# 全局设置 — 启用/禁用自动转录传入的语音消息
stt_enabled: true
```

当设置为 `true`（默认值）时，传入的音频消息在被 Agent 处理之前，会使用配置的 STT 提供商自动转录。

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

## 主频道 {#home-channel}

将 `SLACK_HOME_CHANNEL` 设置为一个频道 ID，Hermes 将向该频道发送计划消息、定时任务结果和其他主动通知。要查找频道 ID：

1.  在 Slack 中右键点击频道名称
2.  点击 **查看频道详情**
3.  滚动到底部 — 频道 ID 显示在那里

```bash
SLACK_HOME_CHANNEL=C01234567890
```

确保机器人**已被邀请到该频道**（`/invite @Hermes Agent`）。

---

## 多工作区支持 {#multi-workspace-support}

Hermes 可以通过单个网关实例同时连接到**多个 Slack 工作区**。每个工作区都使用其自己的机器人用户 ID 独立进行身份验证。

### 配置 {#configuration}

在 `SLACK_BOT_TOKEN` 中以**逗号分隔的列表**形式提供多个机器人令牌：

```bash
# 多个机器人令牌 — 每个工作区一个
SLACK_BOT_TOKEN=xoxb-workspace1-token,xoxb-workspace2-token,xoxb-workspace3-token

# 单个应用级令牌仍用于 Socket 模式
SLACK_APP_TOKEN=xapp-your-app-token
```
或者在 `~/.hermes/config.yaml` 中配置：

```yaml
platforms:
  slack:
    token: "xoxb-workspace1-token,xoxb-workspace2-token"
```

### OAuth 令牌文件 {#oauth-token-file}

除了环境变量或配置文件中的令牌，Hermes 还会从以下位置的 **OAuth 令牌文件** 加载令牌：

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

来自此文件的令牌会与通过 `SLACK_BOT_TOKEN` 指定的任何令牌合并。重复的令牌会自动去重。

### 工作原理 {#how-it-works}

- 列表中的 **第一个令牌** 是主令牌，用于 Socket Mode 连接（AsyncApp）。
- 每个令牌在启动时都会通过 `auth.test` 进行身份验证。网关将每个 `team_id` 映射到其自己的 `WebClient` 和 `bot_user_id`。
- 当消息到达时，Hermes 使用对应工作区的正确客户端进行响应。
- 主 `bot_user_id`（来自第一个令牌）用于向后兼容那些期望单一 bot 身份的功能。

---

## 语音消息 {#voice-messages}

Hermes 支持 Slack 上的语音功能：

- **接收：** 语音/音频消息会自动使用配置的 STT 提供商进行转录：本地 `faster-whisper`、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）
- **发送：** TTS 响应会作为音频文件附件发送

---

## 按频道提示 {#per-channel-prompts}

为特定的 Slack 频道分配临时的系统提示。该提示会在每次对话轮次运行时注入——永远不会持久化到对话历史记录中——因此更改会立即生效。

```yaml
slack:
  channel_prompts:
    "C01RESEARCH": |
      你是一个研究助手。专注于学术来源、引用和简洁的综述。
    "C02ENGINEERING": |
      代码审查模式。请精确关注边界情况和性能影响。
```

键是 Slack 频道 ID（可通过频道详情 → “关于” → 滚动到底部找到）。匹配频道中的所有消息都会获得该提示作为临时系统指令注入。

## 故障排除 {#troubleshooting}

| 问题 | 解决方案 |
|---------|----------|
| Bot 不回复私信 | 确认 `message.im` 在你的事件订阅中，并且应用已重新安装 |
| Bot 在私信中工作但在频道中不工作 | **最常见问题。** 将 `message.channels` 和 `message.groups` 添加到事件订阅，重新安装应用，并使用 `/invite @Hermes Agent` 邀请 bot 加入频道 |
| Bot 不响应频道中的 @提及 | 1) 检查 `message.channels` 事件是否已订阅。2) Bot 必须被邀请加入频道。3) 确保添加了 `channels:history` 权限范围。4) 在更改权限范围/事件后重新安装应用 |
| Bot 忽略私密频道中的消息 | 同时添加 `message.groups` 事件订阅和 `groups:history` 权限范围，然后重新安装应用并 `/invite` bot |
| 私信中显示“向此应用发送消息的功能已关闭” | 在 App Home 设置中启用 **消息选项卡**（参见步骤 5） |
| 出现“not_authed”或“invalid_auth”错误 | 重新生成你的 Bot Token 和 App Token，更新 `.env` 文件 |
| Bot 有响应但无法在频道中发帖 | 使用 `/invite @Hermes Agent` 邀请 bot 加入频道 |
| 出现“missing_scope”错误 | 在 OAuth & Permissions 中添加所需权限范围，然后 **重新安装** 应用 |
| Socket 频繁断开连接 | 检查你的网络；Bolt 会自动重连，但不稳定的连接会导致延迟 |
| 更改了权限范围/事件但无变化 | 在更改任何权限范围或事件订阅后，你 **必须重新安装** 应用到你的工作区 |

### 快速检查清单 {#quick-checklist}

如果 bot 在频道中不工作，请确认 **所有** 以下事项：

1. ✅ `message.channels` 事件已订阅（针对公开频道）
2. ✅ `message.groups` 事件已订阅（针对私密频道）
3. ✅ `app_mention` 事件已订阅
4. ✅ `channels:history` 权限范围已添加（针对公开频道）
5. ✅ `groups:history` 权限范围已添加（针对私密频道）
6. ✅ 添加权限范围/事件后，应用已 **重新安装**
7. ✅ Bot 已被 **邀请** 加入频道（`/invite @Hermes Agent`）
8. ✅ 你在消息中 **@提及** 了 bot
---

## 安全 {#security}

:::warning
**务必设置 `SLACK_ALLOWED_USERS`**，其值为授权用户的 Member ID。如果不设置此项，作为安全措施，网关将默认**拒绝所有消息**。切勿分享你的 bot token —— 应像对待密码一样保管它们。
:::

- Token 应存储在 `~/.hermes/.env` 中（文件权限设为 `600`）
- 定期通过 Slack 应用设置轮换 token
- 审计谁有权访问你的 Hermes 配置目录
- Socket Mode 意味着没有公开的端点暴露 —— 减少了一个攻击面
