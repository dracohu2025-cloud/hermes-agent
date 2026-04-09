---
sidebar_position: 3
title: "Discord"
description: "将 Hermes Agent 设置为 Discord 机器人"
---

# Discord 设置

Hermes Agent 可以作为机器人集成到 Discord 中，让你通过私信或服务器频道与 AI 助手进行对话。机器人会接收你的消息，通过 Hermes Agent 流水线（包括工具使用、记忆和推理）进行处理，并实时回复。它支持文本、语音消息、文件附件和斜杠命令。

在设置之前，先了解一下大多数人最关心的问题：Hermes 进入服务器后的行为表现。

## Hermes 的行为表现

| 上下文 | 行为 |
|---------|----------|
| **私信 (DMs)** | Hermes 会回复每一条消息。无需 `@mention`。每个私信都有独立的会话。 |
| **服务器频道** | 默认情况下，Hermes 仅在被 `@mention` 时才会回复。如果你在频道中发消息而没有提及它，Hermes 会忽略该消息。 |
| **自由回复频道** | 你可以通过 `DISCORD_FREE_RESPONSE_CHANNELS` 将特定频道设置为无需提及即可回复，或者通过 `DISCORD_REQUIRE_MENTION=false` 全局禁用提及要求。 |
| **线程 (Threads)** | Hermes 会在同一线程中回复。除非该线程或其父频道被配置为自由回复模式，否则提及规则依然适用。线程的会话历史与父频道是隔离的。 |
| **多用户共享频道** | 出于安全和清晰度考虑，默认情况下，Hermes 会在频道内按用户隔离会话历史。除非你明确禁用此功能，否则在同一频道中交谈的两个人不会共享同一个对话记录。 |
| **提及其他用户的消息** | 当 `DISCORD_IGNORE_NO_MENTION` 为 `true`（默认值）时，如果消息 `@mention` 了其他人但没有提及机器人，Hermes 将保持沉默。这可以防止机器人介入针对其他人的对话。如果你希望机器人响应所有消息（无论提及了谁），请将其设置为 `false`。此设置仅适用于服务器频道，不适用于私信。 |

:::tip
如果你想要一个普通的机器人帮助频道，让人们无需每次都标记即可与 Hermes 对话，请将该频道添加到 `DISCORD_FREE_RESPONSE_CHANNELS` 中。
:::

### Discord 网关模型

Discord 上的 Hermes 并不是一个无状态回复的 Webhook。它通过完整的消息网关运行，这意味着每条传入的消息都会经过以下流程：

1. 授权检查 (`DISCORD_ALLOWED_USERS`)
2. 提及 / 自由回复检查
3. 会话查找
4. 会话记录加载
5. 正常的 Hermes Agent 执行，包括工具、记忆和斜杠命令
6. 将响应传回 Discord

这一点很重要，因为在繁忙的服务器中，行为表现取决于 Discord 路由和 Hermes 会话策略。

### Discord 中的会话模型 {#session-model-in-discord}

默认情况下：

- 每个私信都有自己的会话
- 每个服务器线程都有自己的会话命名空间
- 共享频道中的每个用户在频道内都有自己的会话

因此，如果 Alice 和 Bob 都在 `#research` 频道中与 Hermes 对话，即使他们使用的是同一个可见的 Discord 频道，Hermes 默认也会将这些视为独立的对话。

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

只有当你明确希望整个房间共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话在协作房间中很有用，但也意味着：

- 用户共享上下文增长和 Token 成本
- 某个人长时间使用工具的任务可能会占用其他人的上下文
- 某个人正在进行的任务可能会中断同一房间内另一个人的后续操作

### 中断与并发

Hermes 通过会话键跟踪正在运行的 Agent。

在默认的 `group_sessions_per_user: true` 设置下：

- Alice 中断她自己正在进行的请求只会影响她在该频道中的会话
- Bob 可以继续在同一频道中交谈，而不会继承 Alice 的历史记录或中断 Alice 的运行

在 `group_sessions_per_user: false` 设置下：

- 整个房间共享该频道/线程的一个运行中 Agent 插槽
- 来自不同人的后续消息可能会相互中断或排队等待

本指南将引导你完成整个设置过程——从在 Discord 开发者门户创建机器人到发送第一条消息。

## 第 1 步：创建 Discord 应用程序

1. 前往 [Discord 开发者门户](https://discord.com/developers/applications) 并使用你的 Discord 账号登录。
2. 点击右上角的 **New Application**。
3. 输入应用程序名称（例如 "Hermes Agent"）并接受开发者服务条款。
4. 点击 **Create**。

你将进入 **General Information** 页面。记下 **Application ID** ——稍后构建邀请链接时会用到它。

## 第 2 步：创建机器人

1. 在左侧边栏中，点击 **Bot**。
2. Discord 会自动为你的应用程序创建一个机器人用户。你将看到机器人的用户名，你可以对其进行自定义。
3. 在 **Authorization Flow** 下：
   - 将 **Public Bot** 设置为 **ON** ——这是使用 Discord 提供的邀请链接（推荐）所必需的。这允许 Installation 选项卡生成默认的授权 URL。
   - 将 **Require OAuth2 Code Grant** 保持为 **OFF**。

:::tip
你可以在此页面为你的机器人设置自定义头像和横幅。这就是用户在 Discord 中看到的样子。
:::

:::info[私有机器人替代方案]
如果你希望保持机器人私有（Public Bot = OFF），你**必须**在第 5 步中使用“手动 URL”方法，而不是使用 Installation 选项卡。Discord 提供的链接要求启用 Public Bot。
:::

## 第 3 步：启用特权网关意图 (Privileged Gateway Intents)

这是整个设置中最关键的一步。如果没有启用正确的意图，你的机器人将连接到 Discord，但**无法读取消息内容**。

在 **Bot** 页面，向下滚动到 **Privileged Gateway Intents**。你会看到三个开关：

| 意图 | 用途 | 是否必需？ |
|--------|---------|-----------| 
| **Presence Intent** | 查看用户在线/离线状态 | 可选 |
| **Server Members Intent** | 访问成员列表，解析用户名 | **必需** |
| **Message Content Intent** | 读取消息的文本内容 | **必需** |

通过将开关切换为 **ON**，**启用 Server Members Intent 和 Message Content Intent**。

- 如果没有 **Message Content Intent**，你的机器人会收到消息事件，但消息文本为空——机器人实际上无法看到你输入的内容。
- 如果没有 **Server Members Intent**，机器人无法为允许用户列表解析用户名，可能无法识别是谁在给它发消息。

:::warning[这是 Discord 机器人无法工作的首要原因]
如果你的机器人在线但从不回复消息，几乎可以肯定是因为 **Message Content Intent** 被禁用了。回到 [开发者门户](https://discord.com/developers/applications)，选择你的应用程序 → Bot → Privileged Gateway Intents，确保 **Message Content Intent** 已切换为 ON。点击 **Save Changes**。
:::

**关于服务器数量：**
- 如果你的机器人所在的服务器**少于 100 个**，你可以自由切换意图。
- 如果你的机器人所在的服务器**达到 100 个或更多**，Discord 要求你提交验证申请才能使用特权意图。对于个人使用，无需担心这一点。

点击页面底部的 **Save Changes**。

## 第 4 步：获取机器人 Token

机器人 Token 是 Hermes Agent 用来以你的机器人身份登录的凭据。仍在 **Bot** 页面：

1. 在 **Token** 部分，点击 **Reset Token**。
2. 如果你的 Discord 账号启用了双重身份验证 (2FA)，请输入你的 2FA 代码。
3. Discord 将显示你的新 Token。**请立即复制它。**

:::warning[Token 仅显示一次]
Token 只会显示一次。如果你丢失了它，你需要重置并生成一个新的。切勿公开分享你的 Token 或将其提交到 Git——任何拥有此 Token 的人都可以完全控制你的机器人。
:::

将 Token 存放在安全的地方（例如密码管理器）。你将在第 8 步中用到它。

## 第 5 步：生成邀请 URL

你需要一个 OAuth2 URL 来邀请机器人进入你的服务器。有两种方法可以做到这一点：

### 选项 A：使用 Installation 选项卡（推荐）

:::note[需要 Public Bot]
此方法要求在第 2 步中将 **Public Bot** 设置为 **ON**。如果你将 Public Bot 设置为 OFF，请改用下面的“手动 URL”方法。
:::
1. 在左侧边栏中，点击 **Installation**。
2. 在 **Installation Contexts** 下，启用 **Guild Install**。
3. 对于 **Install Link**，选择 **Discord Provided Link**。
4. 在 Guild Install 的 **Default Install Settings** 下：
   - **Scopes**：选择 `bot` 和 `applications.commands`
   - **Permissions**：选择下方列出的权限。

### 选项 B：手动 URL

你可以使用以下格式直接构建邀请 URL：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

将 `YOUR_APP_ID` 替换为第 1 步中的应用程序 ID。

### 所需权限

这些是你的 bot 所需的最低权限：

- **View Channels** — 查看它有权访问的频道
- **Send Messages** — 回复你的消息
- **Embed Links** — 格式化富文本响应
- **Attach Files** — 发送图片、音频和文件输出
- **Read Message History** — 维护对话上下文

### 推荐的额外权限

- **Send Messages in Threads** — 在话题对话中回复
- **Add Reactions** — 通过反应来确认消息

### 权限整数

| 级别 | 权限整数 | 包含内容 |
|-------|-------------------|-----------------|
| 最小化 | `117760` | View Channels, Send Messages, Read Message History, Attach Files |
| 推荐 | `274878286912` | 以上所有内容，外加 Embed Links, Send Messages in Threads, Add Reactions |

## 第 6 步：邀请到你的服务器

1. 在浏览器中打开邀请 URL（来自 Installation 选项卡或你手动构建的 URL）。
2. 在 **Add to Server** 下拉菜单中，选择你的服务器。
3. 点击 **Continue**，然后点击 **Authorize**。
4. 如果出现提示，请完成 CAPTCHA 验证。

:::info
你需要在 Discord 服务器上拥有 **Manage Server** 权限才能邀请 bot。如果你在下拉菜单中没有看到你的服务器，请让服务器管理员改用邀请链接。
:::

授权后，bot 将出现在你的服务器成员列表中（在你启动 Hermes 网关之前，它会显示为离线状态）。

## 第 7 步：查找你的 Discord 用户 ID

Hermes Agent 使用你的 Discord 用户 ID 来控制谁可以与 bot 交互。查找方法如下：

1. 打开 Discord（桌面版或网页版）。
2. 进入 **Settings** → **Advanced** → 将 **Developer Mode** 切换为 **ON**。
3. 关闭设置。
4. 右键点击你自己的用户名（在消息、成员列表或你的个人资料中）→ **Copy User ID**。

你的用户 ID 是一个长数字，例如 `284102345871466496`。

:::tip
开发者模式还可以让你以同样的方式复制 **Channel IDs** 和 **Server IDs** —— 右键点击频道或服务器名称并选择 Copy ID。如果你想手动设置主页频道，就需要用到频道 ID。
:::

## 第 8 步：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

出现提示时选择 **Discord**，然后在询问时粘贴你的 bot token 和用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=284102345871466496

# 多个允许的用户（以逗号分隔）
# DISCORD_ALLOWED_USERS=284102345871466496,198765432109876543
```

然后启动网关：

```bash
hermes gateway
```

bot 应该会在几秒钟内上线 Discord。发送一条消息（私信或在它可见的频道中）进行测试。

:::tip
你可以将 `hermes gateway` 在后台运行，或作为 systemd 服务运行以实现持久化操作。详情请参阅部署文档。
:::

## 配置参考

Discord 的行为通过两个文件控制：**`~/.hermes/.env`** 用于凭据和环境变量级别的开关，**`~/.hermes/config.yaml`** 用于结构化设置。当两者都设置时，环境变量始终优先于 config.yaml 中的值。

### 环境变量 (`.env`)

| 变量 | 必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | **是** | — | 来自 [Discord Developer Portal](https://discord.com/developers/applications) 的 bot token。 |
| `DISCORD_ALLOWED_USERS` | **是** | — | 允许与 bot 交互的 Discord 用户 ID，以逗号分隔。没有此项，网关将拒绝所有用户。 |
| `DISCORD_HOME_CHANNEL` | 否 | — | bot 发送主动消息（定时任务输出、提醒、通知）的频道 ID。 |
| `DISCORD_HOME_CHANNEL_NAME` | 否 | `"Home"` | 日志和状态输出中主页频道的显示名称。 |
| `DISCORD_REQUIRE_MENTION` | 否 | `true` | 为 `true` 时，bot 仅在服务器频道中被 `@提及` 时才会响应。设为 `false` 则响应每个频道中的所有消息。 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 否 | — | 以逗号分隔的频道 ID，bot 在这些频道中无需 `@提及` 即可响应，即使 `DISCORD_REQUIRE_MENTION` 为 `true`。 |
| `DISCORD_IGNORE_NO_MENTION` | 否 | `true` | 为 `true` 时，如果消息 `@提及` 了其他用户但**没有**提及 bot，bot 将保持沉默。防止 bot 加入针对其他人的对话。仅适用于服务器频道，不适用于私信。 |
| `DISCORD_AUTO_THREAD` | 否 | `true` | 为 `true` 时，自动为文本频道中的每次 `@提及` 创建一个新话题，以便隔离对话（类似于 Slack 的行为）。已经在话题内或私信中的消息不受影响。 |
| `DISCORD_ALLOW_BOTS` | 否 | `"none"` | 控制 bot 如何处理来自其他 Discord bot 的消息。`"none"` — 忽略所有其他 bot。`"mentions"` — 仅接受 `@提及` Hermes 的 bot 消息。`"all"` — 接受所有 bot 消息。 |
| `DISCORD_REACTIONS` | 否 | `true` | 为 `true` 时，bot 在处理过程中会向消息添加表情反应（开始时为 👀，成功时为 ✅，出错时为 ❌）。设为 `false` 可完全禁用反应。 |
| `DISCORD_IGNORED_CHANNELS` | 否 | — | 以逗号分隔的频道 ID，bot **从不**在这些频道中响应，即使被 `@提及`。优先级高于所有其他频道设置。 |
| `DISCORD_NO_THREAD_CHANNELS` | 否 | — | 以逗号分隔的频道 ID，bot 在这些频道中直接回复，而不是创建话题。仅在 `DISCORD_AUTO_THREAD` 为 `true` 时有效。 |
| `DISCORD_REPLY_TO_MODE` | 否 | `"first"` | 控制回复引用行为：`"off"` — 从不回复原始消息，`"first"` — 仅在第一条消息块上回复引用（默认），`"all"` — 在每个块上回复引用。 |

### 配置文件 (`config.yaml`)

`~/.hermes/config.yaml` 中的 `discord` 部分反映了上述环境变量。Config.yaml 设置作为默认值应用 —— 如果已设置相应的环境变量，则以环境变量为准。

```yaml
# Discord 特定设置
discord:
  require_mention: true           # 在服务器频道中需要 @提及
  free_response_channels: ""      # 以逗号分隔的频道 ID（或 YAML 列表）
  auto_thread: true               # @提及后自动创建话题
  reactions: true                 # 处理过程中添加表情反应
  ignored_channels: []            # bot 从不响应的频道 ID
  no_thread_channels: []          # bot 不使用话题直接响应的频道 ID

# 会话隔离（适用于所有网关平台，不仅限于 Discord）
group_sessions_per_user: true     # 在共享频道中按用户隔离会话
```

#### `discord.require_mention`

**类型：** 布尔值 — **默认值：** `true`

启用后，bot 仅在服务器频道中被直接 `@提及` 时才会响应。无论此设置如何，私信始终会得到响应。

#### `discord.free_response_channels`

**类型：** 字符串或列表 — **默认值：** `""`

bot 响应所有消息而无需 `@提及` 的频道 ID。接受以逗号分隔的字符串或 YAML 列表：

```yaml
# 字符串格式
discord:
  free_response_channels: "1234567890,9876543210"

# 列表格式
discord:
  free_response_channels:
    - 1234567890
    - 9876543210
```

如果话题的父频道在此列表中，该话题也将变为无需提及即可响应。

#### `discord.auto_thread`
**类型：** boolean — **默认值：** `true`

启用后，常规文本频道中的每一条 `@mention` 都会自动为该对话创建一个新线程。这能保持主频道的整洁，并为每个对话提供独立的会话历史记录。一旦创建了线程，后续在该线程中的消息就不再需要 `@mention` —— Bot 会知道它已经参与其中。

在现有线程或私信（DM）中发送的消息不受此设置影响。

#### `discord.reactions`

**类型：** boolean — **默认值：** `true`

控制 Bot 是否通过添加表情符号反应来提供视觉反馈：
- 👀 当 Bot 开始处理你的消息时添加
- ✅ 当响应成功送达时添加
- ❌ 如果处理过程中发生错误时添加

如果你觉得这些反应会造成干扰，或者 Bot 的角色没有 **添加反应 (Add Reactions)** 权限，请禁用此项。

#### `discord.ignored_channels`

**类型：** string 或 list — **默认值：** `[]`

Bot **永远不会**响应的频道 ID，即使被直接 `@mentioned` 也是如此。此设置具有最高优先级 —— 如果某个频道在此列表中，Bot 会静默忽略其中的所有消息，无论 `require_mention`、`free_response_channels` 或任何其他设置如何。

```yaml
# 字符串格式
discord:
  ignored_channels: "1234567890,9876543210"

# 列表格式
discord:
  ignored_channels:
    - 1234567890
    - 9876543210
```

如果某个线程的父频道在此列表中，该线程中的消息也会被忽略。

#### `discord.no_thread_channels`

**类型：** string 或 list — **默认值：** `[]`

Bot 会直接在频道内响应，而不是自动创建线程的频道 ID。此设置仅在 `auto_thread` 为 `true`（默认值）时生效。在这些频道中，Bot 会像普通消息一样内联响应，而不会生成新线程。

```yaml
discord:
  no_thread_channels:
    - 1234567890  # Bot 在此处内联响应
```

适用于专门用于与 Bot 交互的频道，在这些频道中创建线程会产生不必要的干扰。

#### `group_sessions_per_user`

**类型：** boolean — **默认值：** `true`

这是一个全局网关设置（非 Discord 专用），用于控制同一频道内的用户是否拥有独立的会话历史记录。

当设为 `true` 时：Alice 和 Bob 在 `#research` 频道中交谈时，每个人都与 Hermes 进行各自独立的对话。当设为 `false` 时：整个频道共享一个对话记录和一个运行中的 Agent 插槽。

```yaml
group_sessions_per_user: true
```

有关每种模式的完整含义，请参阅上方的 [Session Model](#session-model-in-discord) 部分。

#### `display.tool_progress`

**类型：** string — **默认值：** `"all"` — **可选值：** `off`, `new`, `all`, `verbose`

控制 Bot 在处理过程中是否在聊天中发送进度消息（例如：“正在读取文件...”、“正在运行终端命令...”）。这是一个适用于所有平台的全局网关设置。

```yaml
display:
  tool_progress: "all"    # off | new | all | verbose
```

- `off` — 不发送进度消息
- `new` — 仅显示每轮对话中的第一个工具调用
- `all` — 显示所有工具调用（在网关消息中截断为 40 个字符）
- `verbose` — 显示完整的工具调用详情（可能会产生较长的消息）

#### `display.tool_progress_command`

**类型：** boolean — **默认值：** `false`

启用后，网关将提供 `/verbose` 斜杠命令，让你无需编辑 `config.yaml` 即可循环切换工具进度模式（`off → new → all → verbose → off`）。

```yaml
display:
  tool_progress_command: true
```

## 交互式模型选择器

在 Discord 频道中发送不带参数的 `/model` 命令，即可打开基于下拉菜单的模型选择器：

1. **提供商选择** — 显示可用提供商的下拉菜单（最多 25 个）。
2. **模型选择** — 显示所选提供商对应模型的第二个下拉菜单（最多 25 个）。

选择器会在 120 秒后超时。只有授权用户（在 `DISCORD_ALLOWED_USERS` 中的用户）才能与其交互。如果你知道模型名称，可以直接输入 `/model <name>`。

## 技能原生斜杠命令

Hermes 会自动将已安装的技能注册为 **Discord 原生应用命令**。这意味着技能会与内置命令一起出现在 Discord 的 `/` 自动补全菜单中。

- 每个技能都会成为一个 Discord 斜杠命令（例如 `/code-review`、`/ascii-art`）
- 技能接受一个可选的 `args` 字符串参数
- Discord 每个 Bot 最多支持 100 个应用命令 —— 如果你的技能数量超过可用槽位，多出的技能将被跳过，并在日志中显示警告
- 技能会在 Bot 启动时与 `/model`、`/reset` 和 `/background` 等内置命令一起注册

无需额外配置 —— 任何通过 `hermes skills install` 安装的技能都会在下次网关重启时自动注册为 Discord 斜杠命令。

## 主频道 (Home Channel)

你可以指定一个“主频道”，Bot 会在该频道发送主动消息（例如 cron 任务输出、提醒和通知）。有两种设置方法：

### 使用斜杠命令

在 Bot 所在的任何 Discord 频道中输入 `/sethome`。该频道即成为主频道。

### 手动配置

将以下内容添加到你的 `~/.hermes/.env` 中：

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

将 ID 替换为实际的频道 ID（开启开发者模式后，右键点击频道 -> 复制频道 ID）。

## 语音消息

Hermes Agent 支持 Discord 语音消息：

- **传入的语音消息**：使用配置的 STT 提供商自动转录：本地 `faster-whisper`（无需密钥）、Groq Whisper (`GROQ_API_KEY`) 或 OpenAI Whisper (`VOICE_TOOLS_OPENAI_KEY`)。
- **文本转语音 (TTS)**：使用 `/voice tts` 让 Bot 在发送文本回复的同时发送语音音频回复。
- **Discord 语音频道**：Hermes 也可以加入语音频道，收听用户发言，并在频道内进行语音回复。

有关完整的设置和操作指南，请参阅：
- [语音模式](/user-guide/features/voice-mode)
- [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)

## 故障排除

### Bot 在线但不响应消息

**原因**：未启用 Message Content Intent。

**解决方法**：前往 [开发者门户](https://discord.com/developers/applications) → 你的应用 → Bot → Privileged Gateway Intents → 启用 **Message Content Intent** → 保存更改。重启网关。

### 启动时出现 "Disallowed Intents" 错误

**原因**：你的代码请求了未在开发者门户中启用的 Intents。

**解决方法**：在 Bot 设置中启用所有三个 Privileged Gateway Intents（Presence、Server Members、Message Content），然后重启。

### Bot 无法查看特定频道中的消息

**原因**：Bot 的角色没有查看该频道的权限。

**解决方法**：在 Discord 中，进入频道设置 → 权限 → 添加 Bot 的角色，并启用 **查看频道 (View Channel)** 和 **读取消息历史记录 (Read Message History)**。

### 403 Forbidden 错误

**原因**：Bot 缺少必要的权限。

**解决方法**：使用第 5 步中的 URL 重新邀请 Bot 并赋予正确权限，或者在“服务器设置”→“角色”中手动调整 Bot 的角色权限。

### Bot 离线

**原因**：Hermes 网关未运行，或者 Token 不正确。

**解决方法**：检查 `hermes gateway` 是否正在运行。验证 `.env` 文件中的 `DISCORD_BOT_TOKEN`。如果你最近重置了 Token，请更新它。

### "User not allowed" / Bot 忽略你

**原因**：你的用户 ID 不在 `DISCORD_ALLOWED_USERS` 中。

**解决方法**：将你的用户 ID 添加到 `~/.hermes/.env` 中的 `DISCORD_ALLOWED_USERS`，然后重启网关。

### 同一频道中的人意外共享了上下文

**原因**：`group_sessions_per_user` 被禁用，或者平台无法为该上下文中的消息提供用户 ID。

**解决方法**：在 `~/.hermes/config.yaml` 中设置以下内容并重启网关：

```yaml
group_sessions_per_user: true
```

如果你有意想要共享房间对话，可以保持关闭 —— 但请注意，这会导致共享对话记录和共享中断行为。

## 安全性

:::warning
请务必设置 `DISCORD_ALLOWED_USERS` 以限制谁可以与 Bot 交互。如果不设置，作为安全措施，网关默认会拒绝所有用户。请仅添加你信任的人的用户 ID —— 授权用户拥有 Agent 功能的完全访问权限，包括工具使用和系统访问权限。
:::
有关保护 Hermes Agent 部署的更多信息，请参阅 [安全指南](../security.md)。
