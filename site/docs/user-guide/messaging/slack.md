---
sidebar_position: 4
title: "Slack"
description: "使用 Socket Mode 将 Hermes Agent 设置为 Slack 机器人"
---

# Slack 设置

通过 Socket Mode 将 Hermes Agent 连接为 Slack 机器人。Socket Mode 使用 WebSocket 而非公开的 HTTP 端点，因此你的 Hermes 实例无需公开访问——它可以在防火墙后、你的笔记本电脑或私有服务器上运行。

:::warning 经典 Slack 应用已弃用
经典 Slack 应用（使用 RTM API）已于 **2025 年 3 月完全弃用**。Hermes 使用现代的 Bolt SDK 和 Socket Mode。如果你有旧的经典应用，必须按照以下步骤创建一个新的应用。
:::

## 概览

| 组件 | 说明 |
|-----------|-------|
| **库** | Python 的 `slack-bolt` / `slack_sdk`（Socket Mode） |
| **连接方式** | WebSocket — 无需公开 URL |
| **所需认证令牌** | 机器人令牌（`xoxb-`）+ 应用级令牌（`xapp-`） |
| **用户识别** | Slack 成员 ID（例如 `U01ABC2DEF3`） |

---

## 第 1 步：创建 Slack 应用

1. 访问 [https://api.slack.com/apps](https://api.slack.com/apps)
2. 点击 **Create New App**
3. 选择 **From scratch**
4. 输入应用名称（例如 “Hermes Agent”）并选择你的工作区
5. 点击 **Create App**

你将进入应用的 **Basic Information** 页面。

---

## 第 2 步：配置机器人令牌权限范围

在侧边栏中导航到 **Features → OAuth & Permissions**。滚动到 **Scopes → Bot Token Scopes** 并添加以下权限：

| 权限范围 | 作用 |
|-------|---------|
| `chat:write` | 以机器人身份发送消息 |
| `app_mentions:read` | 监听频道中的 @提及 |
| `channels:history` | 读取机器人所在的公共频道消息 |
| `channels:read` | 列出并获取公共频道信息 |
| `groups:history` | 读取机器人被邀请的私有频道消息 |
| `im:history` | 读取直接消息历史 |
| `im:read` | 查看基本的直接消息信息 |
| `im:write` | 打开和管理直接消息 |
| `users:read` | 查询用户信息 |
| `files:write` | 上传文件（图片、音频、文档） |

:::caution 缺少权限范围 = 缺少功能
如果没有 `channels:history` 和 `groups:history`，机器人**无法接收频道消息**——只能在直接消息中工作。这是最常被遗漏的权限。
:::

**可选权限范围：**

| 权限范围 | 作用 |
|-------|---------|
| `groups:read` | 列出并获取私有频道信息 |

---

## 第 3 步：启用 Socket Mode

Socket Mode 允许机器人通过 WebSocket 连接，而不需要公开 URL。

1. 在侧边栏，进入 **Settings → Socket Mode**
2. 将 **Enable Socket Mode** 切换为开启
3. 系统会提示你创建一个 **App-Level Token**：
   - 给它起个名字，比如 `hermes-socket`（名字无关紧要）
   - 添加 **`connections:write`** 权限范围
   - 点击 **Generate**
4. **复制令牌** — 它以 `xapp-` 开头。这就是你的 `SLACK_APP_TOKEN`

:::tip
你可以随时在 **Settings → Basic Information → App-Level Tokens** 找到或重新生成应用级令牌。
:::

---

## 第 4 步：订阅事件

这一步非常关键——它决定机器人能看到哪些消息。

1. 在侧边栏，进入 **Features → Event Subscriptions**
2. 将 **Enable Events** 切换为开启
3. 展开 **Subscribe to bot events** 并添加：

| 事件 | 是否必需 | 作用 |
|-------|-----------|---------|
| `message.im` | **是** | 机器人接收直接消息 |
| `message.channels` | **是** | 机器人接收它加入的**公共**频道消息 |
| `message.groups` | **推荐** | 机器人接收它被邀请的**私有**频道消息 |
| `app_mention` | **是** | 防止 Bolt SDK 在机器人被 @提及时出错 |

4. 点击页面底部的 **Save Changes**

:::danger 缺少事件订阅是最常见的设置问题
如果机器人能在直接消息中工作，但**无法在频道中响应**，几乎肯定是忘了添加
`message.channels`（公共频道）和/或 `message.groups`（私有频道）。
没有这些事件，Slack 根本不会把频道消息发送给机器人。
:::

---

## 第 5 步：启用消息标签页

这一步允许用户给机器人发送直接消息。否则，用户尝试私信机器人时会看到 **“Sending messages to this app has been turned off”**。

1. 在侧边栏，进入 **Features → App Home**
2. 滚动到 **Show Tabs**
3. 将 **Messages Tab** 切换为开启
4. 勾选 **"Allow users to send Slash commands and messages from the messages tab"**

:::danger 如果不做这一步，直接消息会被完全阻止
即使权限和事件订阅都正确，Slack 也不会允许用户给机器人发直接消息，除非启用了消息标签页。这是 Slack 平台的要求，不是 Hermes 的配置问题。
:::

---

## 第 6 步：安装应用到工作区

1. 在侧边栏，进入 **Settings → Install App**
2. 点击 **Install to Workspace**
3. 审核权限后点击 **Allow**
4. 授权完成后，你会看到一个以 `xoxb-` 开头的 **Bot User OAuth Token**
5. **复制该令牌** — 这就是你的 `SLACK_BOT_TOKEN`

:::tip
如果之后更改了权限或事件订阅，**必须重新安装应用**才能生效。安装页面会显示提示横幅提醒你操作。
:::

---

## 第 7 步：查找允许列表的用户 ID

Hermes 使用 Slack **成员 ID**（不是用户名或显示名）作为允许列表。

查找成员 ID 的方法：

1. 在 Slack 中点击用户的名字或头像
2. 点击 **View full profile**
3. 点击 **⋮**（更多）按钮
4. 选择 **Copy member ID**

成员 ID 形如 `U01ABC2DEF3`。至少需要你自己的成员 ID。

---

## 第 8 步：配置 Hermes

将以下内容添加到你的 `~/.hermes/.env` 文件：

```bash
# 必填
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_ALLOWED_USERS=U01ABC2DEF3              # 逗号分隔的成员 ID 列表

# 可选
SLACK_HOME_CHANNEL=C01234567890              # 定时任务/计划消息的默认频道
SLACK_HOME_CHANNEL_NAME=general              # 频道的可读名称（可选）
```

或者运行交互式设置：

```bash
hermes gateway setup    # 提示时选择 Slack
```

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅限 Linux：开机启动的系统服务
```

---

## 第 9 步：邀请机器人加入频道

启动网关后，你需要**邀请机器人**加入你希望它响应的频道：

```
/invite @Hermes Agent
```

机器人**不会自动加入频道**，必须逐个频道邀请。

---

## 机器人如何响应

了解 Hermes 在不同场景下的行为：

| 场景 | 行为 |
|---------|----------|
| **直接消息** | 机器人响应所有消息——无需 @提及 |
| **频道** | 机器人**只在被 @提及时响应**（例如 `@Hermes Agent 现在几点了？`）。在频道中，Hermes 会在该消息的线程中回复。 |
| **线程** | 如果你在已有线程中 @提及 Hermes，它会在同一线程回复。 |

:::tip
在频道中，务必 @提及机器人。直接发消息不提及会被忽略。
这是故意设计的，避免机器人在繁忙频道中对每条消息都响应。
:::

---

## 主页频道

设置 `SLACK_HOME_CHANNEL` 为 Hermes 发送定时消息、cron 任务结果和其他主动通知的频道 ID。查找频道 ID：

1. 在 Slack 中右键点击频道名称
2. 点击 **View channel details**
3. 滚动到底部，频道 ID 会显示在那里

```bash
SLACK_HOME_CHANNEL=C01234567890
```

确保机器人已**被邀请加入该频道**（`/invite @Hermes Agent`）。

---

## 多工作区支持

Hermes 可以通过单个网关实例同时连接多个 Slack 工作区。每个工作区独立认证，拥有自己的机器人用户 ID。

### 配置

在 `SLACK_BOT_TOKEN` 中以**逗号分隔**提供多个机器人令牌：

```bash
# 多个机器人令牌——每个工作区一个
SLACK_BOT_TOKEN=xoxb-workspace1-token,xoxb-workspace2-token,xoxb-workspace3-token

# Socket Mode 仍然使用单个应用级令牌
SLACK_APP_TOKEN=xapp-your-app-token
```

---
或者在 `~/.hermes/config.yaml` 中：

```yaml
platforms:
  slack:
    token: "xoxb-workspace1-token,xoxb-workspace2-token"
```

### OAuth Token 文件

除了环境变量或配置中的 token，Hermes 还会从以下路径加载一个 **OAuth token 文件**：

```
~/.hermes/platforms/slack/slack_tokens.json
```

该文件是一个 JSON 对象，将团队 ID 映射到 token 条目：

```json
{
  "T01ABC2DEF3": {
    "token": "xoxb-workspace-token-here",
    "team_name": "My Workspace"
  }
}
```

该文件中的 token 会与通过 `SLACK_BOT_TOKEN` 指定的 token 合并。重复的 token 会自动去重。

### 工作原理

- 列表中的**第一个 token**是主 token，用于 Socket Mode 连接（AsyncApp）。
- 每个 token 在启动时都会通过 `auth.test` 进行认证。网关会将每个 `team_id` 映射到对应的 `WebClient` 和 `bot_user_id`。
- 当收到消息时，Hermes 会使用对应工作区的客户端进行回复。
- 主 `bot_user_id`（来自第一个 token）用于向后兼容那些只支持单一 bot 身份的功能。

---

## 语音消息

Hermes 支持 Slack 上的语音功能：

- **接收：** 语音/音频消息会自动使用配置的 STT 提供者转录：本地的 `faster-whisper`、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）
- **发送：** TTS 回复会以音频文件附件的形式发送

---

## 故障排查

| 问题 | 解决方案 |
|---------|----------|
| 机器人不回复私信 | 确认事件订阅中包含 `message.im`，并重新安装应用 |
| 机器人在私信中正常，但频道中不工作 | **最常见问题。** 在事件订阅中添加 `message.channels` 和 `message.groups`，重新安装应用，并用 `/invite @Hermes Agent` 邀请机器人加入频道 |
| 机器人不回复频道中的 @提及 | 1) 确认订阅了 `message.channels` 事件。2) 机器人必须被邀请进频道。3) 确保添加了 `channels:history` 权限。4) 修改权限或事件后重新安装应用 |
| 机器人忽略私密频道消息 | 添加 `message.groups` 事件订阅和 `groups:history` 权限，重新安装应用并用 `/invite` 邀请机器人 |
| 私信中显示“Sending messages to this app has been turned off” | 在 App Home 设置中启用 **Messages Tab**（见步骤 5） |
| 出现 "not_authed" 或 "invalid_auth" 错误 | 重新生成 Bot Token 和 App Token，更新 `.env` 文件 |
| 机器人能回复但无法在频道发消息 | 用 `/invite @Hermes Agent` 邀请机器人加入频道 |
| 出现 "missing_scope" 错误 | 在 OAuth & Permissions 中添加所需权限，然后**重新安装**应用 |
| Socket 频繁断开连接 | 检查网络状况；Bolt 会自动重连，但不稳定的网络会导致延迟 |
| 修改权限/事件后无变化 | 修改权限或事件订阅后，**必须重新安装**应用到工作区 |

### 快速检查清单

如果机器人在频道中不工作，请确认以下所有项：

1. ✅ 订阅了 `message.channels` 事件（针对公共频道）
2. ✅ 订阅了 `message.groups` 事件（针对私密频道）
3. ✅ 订阅了 `app_mention` 事件
4. ✅ 添加了 `channels:history` 权限（针对公共频道）
5. ✅ 添加了 `groups:history` 权限（针对私密频道）
6. ✅ 添加权限/事件后**重新安装**了应用
7. ✅ 用 `/invite @Hermes Agent` 邀请机器人加入频道
8. ✅ 你在消息中**@提及**了机器人

---

## 安全

:::warning
**务必设置 `SLACK_ALLOWED_USERS`**，填写授权用户的成员 ID。没有这个设置时，网关默认会**拒绝所有消息**，以保证安全。切勿泄露你的 bot token —— 它们就像密码一样重要。
:::

- token 应存放在 `~/.hermes/.env`（文件权限设置为 `600`）
- 定期通过 Slack 应用设置轮换 token
- 审计谁有权限访问你的 Hermes 配置目录
- Socket Mode 不会暴露公共端点，减少攻击面

---
