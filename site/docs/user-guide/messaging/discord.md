---
sidebar_position: 3
title: "Discord"
description: "将 Hermes Agent 设置为 Discord 机器人"
---

# Discord 设置

Hermes Agent 以机器人（bot）的形式集成到 Discord 中，让你能够通过私信或服务器频道与 AI 助手聊天。机器人接收你的消息，通过 Hermes Agent 流水线（包括工具使用、记忆和推理）进行处理，并实时做出响应。它支持文本、语音消息、文件附件和斜杠命令（slash commands）。

在开始设置之前，这里是大多数人最想了解的部分：Hermes 进入你的服务器后的行为逻辑。

## Hermes 的行为逻辑

| 场景 | 行为 |
|---------|----------|
| **私信 (DMs)** | Hermes 会响应每一条消息。不需要 `@mention`。每个私信都有独立的会话。 |
| **服务器频道** | 默认情况下，Hermes 仅在你 `@mention` 它时才会响应。如果你在频道中发布消息但未提及它，Hermes 会忽略该消息。 |
| **免提频道 (Free-response channels)** | 你可以通过 `DISCORD_FREE_RESPONSE_CHANNELS` 让特定频道无需提及即可响应，或者通过 `DISCORD_REQUIRE_MENTION=false` 全局禁用提及限制。 |
| **帖子 (Threads)** | Hermes 会在同一个帖子中回复。除非该帖子或其父频道被配置为免提频道，否则提及规则仍然适用。帖子与父频道的会话历史保持隔离。 |
| **多用户共享频道** | 为了安全和清晰，默认情况下，Hermes 会在频道内按用户隔离会话历史。除非你明确禁用此功能，否则在同一频道聊天的两个人不会共享同一个对话记录。 |
| **提及其他用户的消息** | 当 `DISCORD_IGNORE_NO_MENTION` 为 `true`（默认值）时，如果一条消息 @ 了其他用户但**没有** @ 机器人，Hermes 会保持沉默。这可以防止机器人介入针对他人的对话。如果你希望机器人响应所有消息（无论提到了谁），请将其设置为 `false`。这仅适用于服务器频道，不适用于私信。 |

:::tip
如果你想要一个常规的机器人帮助频道，让人们可以不用每次都 @ Hermes 就能与其交流，请将该频道添加到 `DISCORD_FREE_RESPONSE_CHANNELS` 中。
:::

### Discord Gateway 模型

Discord 上的 Hermes 不是一个无状态回复的 webhook。它通过完整的消息网关（messaging gateway）运行，这意味着每条进入的消息都会经过：

1. 鉴权 (`DISCORD_ALLOWED_USERS`)
2. 提及 / 免提检查
3. 会话查找
4. 会话记录加载
5. 正常的 Hermes Agent 执行，包括工具、记忆和斜杠命令
6. 将响应递送回 Discord

这一点很重要，因为在繁忙的服务器中，行为表现既取决于 Discord 的路由，也取决于 Hermes 的会话策略。

### Discord 中的会话模型

默认情况下：

- 每个私信拥有独立的会话
- 每个服务器帖子拥有独立的会话命名空间
- 共享频道中的每个用户在该频道内拥有独立的会话

因此，如果 Alice 和 Bob 都在 `#research` 频道中与 Hermes 交流，尽管他们使用的是同一个可见的 Discord 频道，Hermes 默认会将它们视为独立的对话。

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

只有当你明确希望整个房间共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作室很有用，但也意味着：

- 用户共享上下文增长和 Token 成本
- 某个人长时间的重度工具任务可能会撑大其他所有人的上下文
- 某个人正在进行的运行可能会中断同房间另一位用户的后续操作

### 中断与并发

Hermes 通过会话密钥跟踪运行中的 Agents。

在默认设置 `group_sessions_per_user: true` 下：

- Alice 中断自己正在进行的请求只会影响 Alice 在该频道中的会话
- Bob 可以继续在同一频道说话，而不会继承 Alice 的历史记录，也不会中断 Alice 的运行

在 `group_sessions_per_user: false` 下：

- 整个房间共享该频道/帖子的一个运行 Agent 插槽
- 来自不同人的后续消息可能会相互中断或排队等待

本指南将引导你完成完整的设置过程 —— 从在 Discord 开发者门户创建机器人到发送第一条消息。

## 第 1 步：创建 Discord 应用

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications) 并使用你的 Discord 账号登录。
2. 点击右上角的 **New Application**。
3. 输入应用名称（例如 "Hermes Agent"）并接受开发者服务条款。
4. 点击 **Create**。

你将进入 **General Information** 页面。请记下 **Application ID** —— 稍后构建邀请链接时会用到它。

## 第 2 步：创建机器人 (Bot)

1. 在左侧边栏中，点击 **Bot**。
2. Discord 会自动为你的应用创建一个机器人用户。你会看到机器人的用户名，你可以对其进行自定义。
3. 在 **Authorization Flow** 下：
   - 将 **Public Bot** 设置为 **ON** —— 这是使用 Discord 提供的邀请链接所必需的（推荐）。这允许 Installation 选项卡生成默认的授权 URL。
   - 保持 **Require OAuth2 Code Grant** 为 **OFF**。

:::tip
你可以在此页面为机器人设置自定义头像和横幅。这是用户在 Discord 中看到的形象。
:::

:::info[私有机器人替代方案]
如果你希望保持机器人私有（Public Bot = OFF），你**必须**在第 5 步中使用 **Manual URL** 方法，而不是 Installation 选项卡。Discord 提供的链接要求启用 Public Bot。
:::

## 第 3 步：启用特权网关意图 (Privileged Gateway Intents)

这是整个设置中最关键的一步。如果没有启用正确的意图，你的机器人虽然能连接到 Discord，但**将无法读取消息内容**。

在 **Bot** 页面，向下滚动到 **Privileged Gateway Intents**。你会看到三个开关：

| 意图 (Intent) | 用途 | 是否必选？ |
|--------|---------|-----------| 
| **Presence Intent** | 查看用户在线/离线状态 | 可选 |
| **Server Members Intent** | 访问成员列表，解析用户名 | **必选** |
| **Message Content Intent** | 读取消息的文本内容 | **必选** |

通过将开关切换为 **ON** 来**同时启用 Server Members Intent 和 Message Content Intent**。

- 如果没有 **Message Content Intent**，你的机器人会收到消息事件，但消息文本是空的 —— 机器人字面上看不见你输入了什么。
- 如果没有 **Server Members Intent**，机器人无法为允许用户列表解析用户名，并且可能无法识别是谁在给它发消息。

:::warning[这是 Discord 机器人无法工作的首要原因]
如果你的机器人在线但从不响应消息，几乎可以肯定是因为 **Message Content Intent** 被禁用了。请回到 [Developer Portal](https://discord.com/developers/applications)，选择你的应用 → Bot → Privileged Gateway Intents，确保 **Message Content Intent** 已开启。点击 **Save Changes**。
:::

**关于服务器数量：**
- 如果你的机器人加入的服务器**少于 100 个**，你可以自由地开启或关闭意图。
- 如果你的机器人加入的服务器达到 **100 个或更多**，Discord 要求你提交验证申请才能使用特权意图。对于个人使用，无需担心这一点。

点击页面底部的 **Save Changes**。

## 第 4 步：获取机器人令牌 (Bot Token)

机器人令牌是 Hermes Agent 用来登录机器人的凭据。仍在 **Bot** 页面：

1. 在 **Token** 部分下，点击 **Reset Token**。
2. 如果你的 Discord 账号启用了双重身份验证，请输入 2FA 代码。
3. Discord 将显示你的新令牌。**请立即复制它。**

:::warning[令牌仅显示一次]
令牌只显示一次。如果你丢失了它，你需要重置并生成一个新令牌。切勿公开分享你的令牌或将其提交到 Git —— 任何拥有此令牌的人都可以完全控制你的机器人。
:::

将令牌存储在安全的地方（例如密码管理器）。你将在第 8 步中用到它。

## 第 5 步：生成邀请链接

你需要一个 OAuth2 URL 来邀请机器人进入你的服务器。有两种方法可以做到这一点：

### 选项 A：使用 Installation 选项卡（推荐）

:::note[需要 Public Bot]
此方法要求在第 2 步中将 **Public Bot** 设置为 **ON**。如果你将 Public Bot 设置为 OFF，请改用下方的 Manual URL 方法。
:::
1. 在左侧边栏中，点击 **Installation**。
2. 在 **Installation Contexts** 下，启用 **Guild Install**。
3. 对于 **Install Link**，选择 **Discord Provided Link**。
4. 在 Guild Install 的 **Default Install Settings** 下：
   - **Scopes**：选择 `bot` 和 `applications.commands`
   - **Permissions**：选择下面列出的权限。

### 选项 B：手动构建 URL

你可以使用以下格式直接构建邀请 URL：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

将 `YOUR_APP_ID` 替换为步骤 1 中的 Application ID。

### 必要权限

以下是你的 bot 所需的最低权限：

- **View Channels** — 查看其有权访问的频道
- **Send Messages** — 回复你的消息
- **Embed Links** — 格式化富文本回复
- **Attach Files** — 发送图片、音频和文件输出
- **Read Message History** — 维持对话上下文

### 推荐的附加权限

- **Send Messages in Threads** — 在帖子（thread）对话中回复
- **Add Reactions** — 对消息添加表情回应以确认收到

### 权限整数（Permission Integers）

| 级别 | 权限整数 | 包含内容 |
|-------|-------------------|-----------------|
| 最低 (Minimal) | `117760` | View Channels, Send Messages, Read Message History, Attach Files |
| 推荐 (Recommended) | `274878286912` | 包含上述所有权限，外加 Embed Links, Send Messages in Threads, Add Reactions |

## 第 6 步：邀请至你的服务器

1. 在浏览器中打开邀请 URL（来自 Installation 选项卡或你手动构建的 URL）。
2. 在 **Add to Server** 下拉菜单中，选择你的服务器。
3. 点击 **Continue**，然后点击 **Authorize**。
4. 如果弹出提示，请完成验证码（CAPTCHA）。

:::info
你需要拥有 Discord 服务器的 **Manage Server** 权限才能邀请 bot。如果你在下拉菜单中没看到你的服务器，请让服务器管理员代为使用该邀请链接。
:::

授权后，bot 将出现在你服务器的成员列表中（在启动 Hermes gateway 之前，它会显示为离线状态）。

## 第 7 步：查找你的 Discord 用户 ID

Hermes Agent 使用你的 Discord 用户 ID 来控制谁可以与 bot 交互。查找方法如下：

1. 打开 Discord（桌面版或网页版）。
2. 前往 **Settings** → **Advanced** → 将 **Developer Mode** 切换为 **ON**。
3. 关闭设置。
4. 右键点击你自己的用户名（在消息中、成员列表或个人资料中均可）→ **Copy User ID**。

你的用户 ID 是一串长数字，例如 `284102345871466496`。

:::tip
开发者模式还允许你以同样的方式复制 **Channel ID** 和 **Server ID** —— 只需右键点击频道或服务器名称并选择 Copy ID。如果你想手动设置主频道（home channel），则需要 Channel ID。
:::

## 第 8 步：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在提示时选择 **Discord**，然后根据要求粘贴你的 bot token 和用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必填
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=284102345871466496

# 允许多个用户（用逗号分隔）
# DISCORD_ALLOWED_USERS=284102345871466496,198765432109876543
```

然后启动 gateway：

```bash
hermes gateway
```

bot 应该会在几秒钟内在 Discord 中上线。给它发一条消息（私聊或在它可见的频道中）进行测试。

:::tip
你可以将 `hermes gateway` 在后台运行，或将其作为 systemd 服务运行以实现持久化操作。详情请参阅部署文档。
:::

## 配置参考

Discord 的行为通过两个文件控制：**`~/.hermes/.env`** 用于凭据和环境变量级别的开关，**`~/.hermes/config.yaml`** 用于结构化设置。当两者都设置时，环境变量的优先级始终高于 config.yaml 中的值。

### 环境变量 (`.env`)

| 变量 | 必填 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | **是** | — | 来自 [Discord Developer Portal](https://discord.com/developers/applications) 的 Bot token。 |
| `DISCORD_ALLOWED_USERS` | **是** | — | 允许与 bot 交互的 Discord 用户 ID，多个 ID 用逗号分隔。如果不设置，gateway 将拒绝所有用户。 |
| `DISCORD_HOME_CHANNEL` | 否 | — | bot 发送主动消息（定时任务输出、提醒、通知）的频道 ID。 |
| `DISCORD_HOME_CHANNEL_NAME` | 否 | `"Home"` | 日志和状态输出中主频道的显示名称。 |
| `DISCORD_REQUIRE_MENTION` | 否 | `true` | 为 `true` 时，bot 仅在服务器频道中被 `@提及` 时才会响应。设为 `false` 则响应所有频道中的所有消息。 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 否 | — | 即使 `DISCORD_REQUIRE_MENTION` 为 `true`，bot 也会在这些频道 ID（逗号分隔）中无需 `@提及` 直接响应。 |
| `DISCORD_IGNORE_NO_MENTION` | 否 | `true` | 为 `true` 时，如果消息 `@提及` 了其他用户但**没有**提及 bot，bot 将保持沉默。防止 bot 介入针对他人的对话。仅适用于服务器频道，不适用于私聊。 |
| `DISCORD_AUTO_THREAD` | 否 | `true` | 为 `true` 时，自动为文本频道中的每个 `@提及` 创建新帖子（thread），使每个对话相互隔离（类似于 Slack 的行为）。已经在帖子内或私聊中的消息不受影响。 |
| `DISCORD_ALLOW_BOTS` | 否 | `"none"` | 控制 bot 如何处理来自其他 Discord bot 的消息。`"none"` — 忽略所有其他 bot；`"mentions"` — 仅接受 `@提及` 了 Hermes 的 bot 消息；`"all"` — 接受所有 bot 消息。 |
| `DISCORD_REACTIONS` | 否 | `true` | 为 `true` 时，bot 在处理消息期间会添加表情回应（开始时 👀，成功时 ✅，错误时 ❌）。设为 `false` 则完全禁用回应。 |
| `DISCORD_IGNORED_CHANNELS` | 否 | — | bot **永远不会**响应的频道 ID（逗号分隔），即使被 `@提及` 也不响应。优先级高于所有其他频道设置。 |
| `DISCORD_NO_THREAD_CHANNELS` | 否 | — | 即使 `DISCORD_AUTO_THREAD` 为 `true`，bot 也会在这些频道 ID（逗号分隔）中直接响应，而不创建帖子。 |

### 配置文件 (`config.yaml`)

`~/.hermes/config.yaml` 中的 `discord` 部分镜像了上述环境变量。Config.yaml 的设置作为默认值应用 —— 如果已设置等效的环境变量，则以环境变量为准。

```yaml
# Discord 特定设置
discord:
  require_mention: true           # 在服务器频道中需要 @提及
  free_response_channels: ""      # 逗号分隔的频道 ID（或 YAML 列表）
  auto_thread: true               # 在 @提及 时自动创建帖子
  reactions: true                 # 在处理过程中添加表情回应
  ignored_channels: []            # bot 永远不响应的频道 ID
  no_thread_channels: []          # bot 直接响应而不使用帖子的频道 ID

# 会话隔离（适用于所有 gateway 平台，不仅限于 Discord）
group_sessions_per_user: true     # 在共享频道中按用户隔离会话
```

#### `discord.require_mention`

**类型：** 布尔值 — **默认值：** `true`

启用后，bot 仅在服务器频道中被直接 `@提及` 时才会响应。无论此设置如何，私聊（DM）始终会得到响应。

#### `discord.free_response_channels`

**类型：** 字符串或列表 — **默认值：** `""`

bot 无需 `@提及` 即可响应所有消息的频道 ID。接受逗号分隔的字符串或 YAML 列表：

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

如果帖子的父频道在此列表中，则该帖子也会变为无需提及模式。

#### `discord.auto_thread`

**类型：** 布尔值 — **默认值：** `true`

启用后，普通文本频道中的每个 `@提及` 都会自动为该对话创建一个新帖子（thread）。这可以保持主频道整洁，并为每个对话提供独立的会话历史记录。帖子创建后，该帖子内的后续消息不需要再 `@提及` —— bot 知道它已经在参与对话了。
在现有线程或私信（DM）中发送的消息不受此设置影响。

#### `discord.reactions`

**类型：** boolean — **默认值：** `true`

控制机器人是否向消息添加表情符号（emoji）回应作为视觉反馈：
- 👀 当机器人开始处理你的消息时添加
- ✅ 当响应成功送达时添加
- ❌ 如果处理过程中发生错误时添加

如果你觉得这些回应干扰视线，或者机器人的角色没有 **添加反应（Add Reactions）** 权限，请禁用此项。

#### `discord.ignored_channels`

**类型：** string 或 list — **默认值：** `[]`

机器人**永远不会**响应的频道 ID，即使被直接 `@提到` 也是如此。此项具有最高优先级 —— 如果一个频道在此列表中，机器人将静默忽略该频道的所有消息，无论 `require_mention`、`free_response_channels` 或任何其他设置如何。

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

如果某个线程的父级频道在此列表中，该线程内的消息也会被忽略。

#### `discord.no_thread_channels`

**类型：** string 或 list — **默认值：** `[]`

机器人直接在频道内响应，而不是自动创建线程的频道 ID。这仅在 `auto_thread` 为 `true`（默认值）时生效。在这些频道中，机器人会像普通消息一样行内回复，而不是生成新线程。

```yaml
discord:
  no_thread_channels:
    - 1234567890  # 机器人在此处行内回复
```

适用于专门用于机器人交互的频道，在这些频道中开启线程会增加不必要的干扰。

#### `group_sessions_per_user`

**类型：** boolean — **默认值：** `true`

这是一个全局网关设置（非 Discord 专用），用于控制同一频道内的用户是否获得隔离的会话历史。

当为 `true` 时：Alice 和 Bob 在 `#research` 频道中交流时，各自拥有与 Hermes 独立的对话。当为 `false` 时：整个频道共享一个对话记录和一个运行中的 Agent 插槽。

```yaml
group_sessions_per_user: true
```

请参阅上文的 [Discord 中的会话模型](#session-model-in-discord) 章节，了解每种模式的完整影响。

#### `display.tool_progress`

**类型：** string — **默认值：** `"all"` — **可选值：** `off`, `new`, `all`, `verbose`

控制机器人是否在处理时在聊天中发送进度消息（例如：“正在读取文件...”、“正在运行终端命令...”）。这是一个适用于所有平台的全局网关设置。

```yaml
display:
  tool_progress: "all"    # off | new | all | verbose
```

- `off` — 不显示进度消息
- `new` — 每轮对话仅显示第一个工具调用
- `all` — 显示所有工具调用（在网关消息中缩短至 40 个字符）
- `verbose` — 显示完整的工具调用详情（可能会产生长消息）

#### `display.tool_progress_command`

**类型：** boolean — **默认值：** `false`

启用后，将在网关中提供 `/verbose` 斜杠命令，让你无需编辑 config.yaml 即可循环切换工具进度模式（`off → new → all → verbose → off`）。

```yaml
display:
  tool_progress_command: true
```

## 交互式模型选择器

在 Discord 频道中发送不带参数的 `/model` 命令，可打开基于下拉菜单的模型选择器：

1. **供应商选择** — 显示可用供应商的下拉菜单（最多 25 个）。
2. **模型选择** — 第二个下拉菜单，显示所选供应商的模型（最多 25 个）。

选择器在 120 秒后超时。只有授权用户（在 `DISCORD_ALLOWED_USERS` 中的用户）可以与其交互。如果你知道模型名称，可以直接输入 `/model <name>`。

## Skill 的原生斜杠命令

Hermes 会自动将安装的 Skill 注册为 **原生 Discord 应用命令（Application Commands）**。这意味着 Skill 会与内置命令一起出现在 Discord 的 `/` 自动补全菜单中。

- 每个 Skill 都会变成一个 Discord 斜杠命令（例如：`/code-review`，`/ascii-art`）
- Skill 接受一个可选的 `args` 字符串参数
- Discord 对每个机器人有 100 个应用命令的限制 —— 如果你的 Skill 数量超过了可用插槽，多出的 Skill 将被跳过，并在日志中显示警告
- Skill 在机器人启动时与 `/model`、`/reset` 和 `/background` 等内置命令一起注册

无需额外配置 —— 任何通过 `hermes skills install` 安装的 Skill 都会在下次网关重启时自动注册为 Discord 斜杠命令。

## 主频道 (Home Channel)

你可以指定一个“主频道”，机器人会在该频道发送主动消息（如定时任务输出、提醒和通知）。有两种设置方式：

### 使用斜杠命令

在机器人所在的任何 Discord 频道中输入 `/sethome`。该频道即成为主频道。

### 手动配置

将以下内容添加到你的 `~/.hermes/.env`：

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

将 ID 替换为实际的频道 ID（开启开发者模式后，右键点击频道 → 复制频道 ID）。

## 语音消息

Hermes Agent 支持 Discord 语音消息：

- **传入的语音消息**：使用配置的 STT 供应商自动转录：本地 `faster-whisper`（无需密钥）、Groq Whisper (`GROQ_API_KEY`) 或 OpenAI Whisper (`VOICE_TOOLS_OPENAI_KEY`)。
- **文本转语音**：使用 `/voice tts` 让机器人在回复文本的同时发送语音回复。
- **Discord 语音频道**：Hermes 还可以加入语音频道，听取用户说话并在频道中回话。

有关完整设置和操作指南，请参阅：
- [语音模式](/user-guide/features/voice-mode)
- [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)

## 故障排除

### 机器人在线但不响应消息

**原因**：消息内容意图（Message Content Intent）已禁用。

**修复**：前往 [Developer Portal](https://discord.com/developers/applications) → 你的应用 → Bot → Privileged Gateway Intents → 启用 **Message Content Intent** → 保存更改。重启网关。

### 启动时出现 "Disallowed Intents" 错误

**原因**：你的代码请求了在 Developer Portal 中未启用的意图。

**修复**：在 Bot 设置中启用所有三个特权网关意图（Presence、Server Members、Message Content），然后重启。

### 机器人看不到特定频道的消息

**原因**：机器人的角色没有查看该频道的权限。

**修复**：在 Discord 中，前往频道设置 → 权限 → 添加机器人的角色，并启用 **查看频道（View Channel）** 和 **阅读消息历史（Read Message History）**。

### 403 Forbidden 错误

**原因**：机器人缺少必要的权限。

**修复**：使用步骤 5 中的 URL 重新邀请机器人并赋予正确权限，或者在服务器设置 → 角色中手动调整机器人的角色权限。

### 机器人离线

**原因**：Hermes 网关未运行，或 Token 错误。

**修复**：检查 `hermes gateway` 是否正在运行。验证 `.env` 文件中的 `DISCORD_BOT_TOKEN`。如果你最近重置了 Token，请更新它。

### "User not allowed" / 机器人忽略你

**原因**：你的用户 ID 不在 `DISCORD_ALLOWED_USERS` 中。

**修复**：将你的用户 ID 添加到 `~/.hermes/.env` 中的 `DISCORD_ALLOWED_USERS` 并重启网关。

### 同一频道的人意外共享了上下文

**原因**：`group_sessions_per_user` 已禁用，或者平台无法为该上下文中的消息提供用户 ID。

**修复**：在 `~/.hermes/config.yaml` 中设置此项并重启网关：

```yaml
group_sessions_per_user: true
```

如果你确实想要共享聊天室对话，请保持关闭 —— 但要预料到会共享对话记录和中断行为。

## 安全性

:::warning 警告
务必设置 `DISCORD_ALLOWED_USERS` 以限制谁可以与机器人交互。如果没有设置，作为安全措施，网关默认会拒绝所有用户。仅添加你信任的人的用户 ID —— 授权用户拥有对 Agent 功能的完整访问权限，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署安全的更多信息，请参阅 [安全指南](../security.md)。
由于你没有在 `--- BEGIN DOCUMENT CHUNK ---` 和 `--- END DOCUMENT CHUNK ---` 之间提供具体的英文原文内容，我无法为你进行翻译。

请提供需要翻译的文档片段，我将立即按照你的要求（保留 Agent 术语、保持 Markdown 结构、面向开发者且通俗易懂）为你完成翻译。
