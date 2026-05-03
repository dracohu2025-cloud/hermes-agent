---
sidebar_position: 3
title: "Discord"
description: "将 Hermes Agent 设置为一个 Discord 机器人"
---

# Discord 设置 {#discord-setup}

Hermes Agent 以机器人与 Discord 集成，让你能够通过私信或服务器频道与你的 AI 助手对话。机器人接收你的消息，通过 Hermes Agent 流水线（包括工具使用、记忆和推理）处理，然后实时回复。它支持文本、语音消息、文件附件和斜杠命令。

在开始设置之前，这里先讲一下大家最关心的部分：Hermes 进入你的服务器后的行为表现。

## Hermes 的行为方式 {#how-hermes-behaves}

| 上下文 | 行为 |
|---------|----------|
| **私信（DMs）** | Hermes 回复每一条消息，不需要 `@提及`。每条私信拥有独立的会话。 |
| **服务器频道** | 默认情况下，Hermes 只在你 `@提及` 它时才会回复。如果你在频道发了消息但没有提及它，Hermes 会忽略该消息。 |
| **自由回复频道** | 你可以通过 `DISCORD_FREE_RESPONSE_CHANNELS` 让特定频道不需要提及即可回复，或者通过 `DISCORD_REQUIRE_MENTION=false` 全局禁用提及要求。这些频道中的消息会被内联回复——跳过自动创建线程，以保持频道作为轻量级聊天。 |
| **线程** | Hermes 在同一线程中回复。提及规则仍然适用，除非该线程或它的父频道被配置为自由回复。线程在会话历史方面与父频道隔离。 |
| **多用户共享频道** | 默认情况下，Hermes 会在频道内按用户隔离会话历史，以保证安全和清晰。两个人在同一频道中说话，默认不会共享同一份对话记录，除非你显式禁用该功能。 |
| **提及了其他用户的消息** | 当 `DISCORD_IGNORE_NO_MENTION` 为 `true`（默认值）时，如果一条消息 @提及了其他用户但**没有**提及机器人，Hermes 会保持沉默。这可以防止机器人插嘴对别人的对话。如果你希望机器人无论提及了谁，都回复所有消息，请将该值设为 `false`。此规则仅适用于服务器频道，不适用于私信。 |

:::tip
如果你想要一个常规的机器人帮助频道，让用户每次与 Hermes 对话时无需 @提及它，请将该频道加入 `DISCORD_FREE_RESPONSE_CHANNELS`。
:::

### Discord 网关模型 {#discord-gateway-model}

在 Discord 上的 Hermes 并不是一个无状态回复的 Webhook。它运行完整的消息网关，这意味着每条进入的消息都会经过：

1. 授权检查（`DISCORD_ALLOWED_USERS`）
2. 提及/自由回复检查
3. 会话查找
4. 会话对话记录加载
5. 正常的 Hermes Agent 执行，包括工具、记忆和斜杠命令
6. 将回复发送回 Discord

这点很重要，因为在一个繁忙的服务器中，行为取决于 Discord 路由和 Hermes 会话策略两者的共同作用。

### Discord 中的会话模型 {#session-model-in-discord}

默认情况下：

- 每条私信拥有独立的会话
- 每个服务器线程拥有独立的会话命名空间
- 每个共享频道中的用户在该频道内拥有自己的会话

因此，如果 Alice 和 Bob 都在 `#research` 频道与 Hermes 交谈，即使他们使用的是同一个可见的 Discord 频道，Hermes 也会默认将它们视为独立的会话。
这是由 `config.yaml` 控制的：

```yaml
group_sessions_per_user: true
```

只有在明确希望整个房间共享同一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话在协作房间中可能有用，但同时也意味着：

- 所有用户共享上下文增长和 token 成本
- 一个人的大量工具型长任务会膨胀其他人的上下文
- 一个人正在运行的任务可能打断同房间另一个人后续的对话

### 中断与并发 {#interrupts-and-concurrency}

Hermes 通过会话键来跟踪正在运行的 Agent。

在默认的 `group_sessions_per_user: true` 下：

- Alice 中断自己正在进行的请求，只影响 Alice 在该频道中的会话
- Bob 可以在同一频道继续发言，而不会继承 Alice 的历史记录或打断 Alice 的运行

在 `group_sessions_per_user: false` 下：

- 整个房间共享该频道/线程的一个运行中 Agent 槽位
- 不同人的后续消息可能会相互打断或排队等待

本指南将带你完成完整的配置流程——从在 Discord 开发者门户创建机器人到发送第一条消息。

## 步骤 1：创建 Discord 应用 {#step-1-create-a-discord-application}

1. 前往 [Discord 开发者门户](https://discord.com/developers/applications)并使用你的 Discord 账号登录。
2. 点击右上角的 **New Application**。
3. 为你的应用输入一个名称（例如 "Hermes Agent"），并接受开发者服务条款。
4. 点击 **Create**。

你将进入 **General Information** 页面。记下 **Application ID**——稍后构建邀请链接时会用到它。

## 步骤 2：创建机器人 {#step-2-create-the-bot}

1. 在左侧边栏中，点击 **Bot**。
2. Discord 会自动为你的应用创建一个机器人用户。你会看到机器人的用户名，可以自定义。
3. 在 **Authorization Flow** 下：
   - 将 **Public Bot** 设置为 **ON**——这是使用 Discord 提供的邀请链接所必需的（推荐）。这样 "Installation" 标签页会生成一个默认的授权 URL。
   - 将 **Require OAuth2 Code Grant** 保持为 **OFF**。

:::tip
你可以在此页面为机器人设置自定义头像和横幅。用户在 Discord 中看到的将是这些设置。
:::

:::info[私有机器人替代方案]
如果你希望保持机器人私有（Public Bot = OFF），则**必须**在步骤 5 中使用 **Manual URL** 方法，而不是 "Installation" 标签页。Discord 提供的链接要求启用 Public Bot。
:::

## 步骤 3：启用特权网关意图 {#step-3-enable-privileged-gateway-intents}

这是整个设置中最关键的一步。如果没有启用正确的意图，你的机器人可以连接到 Discord，但**将无法读取消息内容**。

在 **Bot** 页面，向下滚动到 **Privileged Gateway Intents**。你会看到三个开关：

| 意图 | 用途 | 是否必需？ |
|--------|---------|-----------| 
| **Presence Intent** | 查看用户在线/离线状态 | 可选 |
| **Server Members Intent** | 访问成员列表，解析用户名 | **必需** |
| **Message Content Intent** | 读取消息的文本内容 | **必需** |
**同时启用 Server Members Intent 和 Message Content Intent**，将它们切换为 **ON**。

- 如果没有 **Message Content Intent**，你的机器人会收到消息事件，但消息文本是空的——机器人实际上看不到你输入的内容。
- 如果没有 **Server Members Intent**，机器人无法解析允许用户列表中的用户名，可能无法识别谁在给它发消息。

:::warning[这是 Discord 机器人无法工作的首要原因]
如果你的机器人在线但从不回复消息，**Message Content Intent** 几乎肯定被禁用了。回到 [开发者门户](https://discord.com/developers/applications)，选择你的应用 → Bot → Privileged Gateway Intents，确保 **Message Content Intent** 已切换为 ON。点击 **Save Changes**。
:::

**关于服务器数量：**
- 如果你的机器人位于 **少于 100 个服务器** 中，你可以自由地开关这些意图。
- 如果你的机器人位于 **100 个或更多服务器** 中，Discord 要求你提交验证申请才能使用特权意图。对于个人使用，这无需担心。

点击页面底部的 **Save Changes**。

## 第 4 步：获取机器人令牌 {#step-4-get-the-bot-token}

机器人令牌是 Hermes Agent 用来以你的机器人身份登录的凭证。仍在 **Bot** 页面：

1. 在 **Token** 部分下，点击 **Reset Token**。
2. 如果你在 Discord 账户上启用了双重身份验证，请输入你的 2FA 代码。
3. Discord 会显示你的新令牌。**立即复制它。**

:::warning[令牌仅显示一次]
令牌只显示一次。如果你丢失了它，你需要重置并生成一个新令牌。切勿公开分享你的令牌或将其提交到 Git——任何拥有此令牌的人都可以完全控制你的机器人。
:::

将令牌存放在安全的地方（例如密码管理器）。你将在第 8 步中用到它。

## 第 5 步：生成邀请链接 {#step-5-generate-the-invite-url}

你需要一个 OAuth2 URL 来将机器人邀请到你的服务器。有两种方法可以做到这一点：

### 选项 A：使用安装标签页（推荐） {#option-a-using-the-installation-tab-recommended}

:::note[需要公开机器人]
此方法要求 **Public Bot** 在第 2 步中设置为 **ON**。如果你将 Public Bot 设置为 OFF，请改用下面的手动 URL 方法。
:::

1. 在左侧边栏中，点击 **Installation**。
2. 在 **Installation Contexts** 下，启用 **Guild Install**。
3. 对于 **Install Link**，选择 **Discord Provided Link**。
4. 在 **Default Install Settings** 下的 Guild Install 中：
   - **Scopes**：选择 `bot` 和 `applications.commands`
   - **Permissions**：选择下面列出的权限。

### 选项 B：手动 URL {#option-b-manual-url}

你可以直接使用以下格式构建邀请 URL：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

将 `YOUR_APP_ID` 替换为第 1 步中的应用程序 ID。

### 所需权限 {#required-permissions}

这些是你的机器人所需的最低权限：

- **View Channels** — 查看它可以访问的频道
- **Send Messages** — 回复你的消息
- **Embed Links** — 格式化富文本回复
- **Attach Files** — 发送图片、音频和文件输出
- **Read Message History** — 维护对话上下文
### 推荐附加权限 {#recommended-additional-permissions}

- **在帖子中发送消息** — 在帖子对话中回复
- **添加反应** — 对消息添加表情反应以表示确认

### 权限整数 {#permission-integers}

| 级别 | 权限整数 | 包含内容 |
|-------|-------------------|-----------------|
| 最小 | `117760` | 查看频道、发送消息、读取消息历史、附加文件 |
| 推荐 | `274878286912` | 以上所有权限，外加嵌入链接、在帖子中发送消息、添加反应 |

## 第 6 步：邀请到你的服务器 {#step-6-invite-to-your-server}

1. 在浏览器中打开邀请链接（来自“安装”标签页或你手动构建的 URL）。
2. 在 **添加到服务器** 下拉菜单中，选择你的服务器。
3. 点击 **继续**，然后 **授权**。
4. 如果提示，完成验证码。

:::info
你需要在 Discord 服务器上拥有 **管理服务器** 权限才能邀请机器人。如果下拉菜单中没有显示你的服务器，请让服务器管理员使用邀请链接。
:::

授权后，机器人会出现在服务器的成员列表中（在启动 Hermes 网关之前，它会显示为离线状态）。

## 第 7 步：查找你的 Discord 用户 ID {#step-7-find-your-discord-user-id}

Hermes Agent 使用你的 Discord 用户 ID 来控制谁可以与机器人交互。查找方法：

1. 打开 Discord（桌面版或网页版）。
2. 进入 **设置** → **高级** → 将 **开发者模式** 切换为 **开启**。
3. 关闭设置。
4. 右键点击你自己的用户名（在消息、成员列表或你的个人资料中）→ **复制用户 ID**。

你的用户 ID 是一个长数字，例如 `284102345871466496`。

:::tip
开发者模式还允许你以同样的方式复制 **频道 ID** 和 **服务器 ID**——右键点击频道或服务器名称，然后选择“复制 ID”。如果你想手动设置一个主频道，就需要频道 ID。
:::

## 第 8 步：配置 Hermes Agent {#step-8-configure-hermes-agent}

### 选项 A：交互式设置（推荐） {#option-a-interactive-setup-recommended}

运行引导式设置命令：

```bash
hermes gateway setup
```

根据提示选择 **Discord**，然后粘贴你的机器人令牌和用户 ID。

### 选项 B：手动配置 {#option-b-manual-configuration}

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
DISCORD_BOT_TOKEN=你的机器人令牌
DISCORD_ALLOWED_USERS=284102345871466496

# 多个允许的用户（逗号分隔）
# DISCORD_ALLOWED_USERS=284102345871466496,198765432109876543
```

然后启动网关：

```bash
hermes gateway
```

机器人应该在几秒钟内上线 Discord。给它发送一条消息——无论是私信还是它能看到的频道中的消息——来测试。

:::tip
你可以将 `hermes gateway` 作为后台进程或 systemd 服务运行，以实现持久运行。详情请参阅部署文档。
:::

## 配置参考 {#configuration-reference}

Discord 的行为通过两个文件控制：**`~/.hermes/.env`** 用于凭据和环境级开关，**`~/.hermes/config.yaml`** 用于结构化设置。当两者都设置时，环境变量始终优先于 config.yaml 中的值。

### 环境变量（`.env`） {#environment-variables-env}

| 变量 | 必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | **是** | — | 来自 [Discord 开发者门户](https://discord.com/developers/applications) 的机器人令牌。 |
| `DISCORD_ALLOWED_USERS` | **是** | — | 允许与机器人交互的 Discord 用户 ID（逗号分隔）。如果没有此项 **或** `DISCORD_ALLOWED_ROLES`，网关将拒绝所有用户。 |
| `DISCORD_ALLOWED_ROLES` | 否 | — | 逗号分隔的 Discord 角色 ID。拥有这些角色之一的成员将被授权——与 `DISCORD_ALLOWED_USERS` 是“或”语义。连接时自动启用 **服务器成员意图**。当管理团队人员变动时很有用：新管理员一旦获得角色即可访问，无需推送配置。 |
| `DISCORD_HOME_CHANNEL` | 否 | — | 机器人发送主动消息（定时任务输出、提醒、通知）的频道 ID。 |
| `DISCORD_HOME_CHANNEL_NAME` | 否 | `"Home"` | 主频道在日志和状态输出中的显示名称。 |
| `DISCORD_COMMAND_SYNC_POLICY` | 否 | `"safe"` | 控制原生斜杠命令的启动同步。`"safe"` 会对比现有的全局命令，仅更新有变化的部分，当 Discord 元数据变更无法通过补丁应用时重新创建命令。`"bulk"` 保留旧的 `tree.sync()` 行为。`"off"` 完全跳过启动同步。 |
| `DISCORD_REQUIRE_MENTION` | 否 | `true` | 当为 `true` 时，机器人仅在服务器频道中被 `@提及` 时才会响应。设为 `false` 则响应所有频道中的所有消息。 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 否 | — | 逗号分隔的频道 ID，在这些频道中机器人无需 `@提及` 即可响应，即使 `DISCORD_REQUIRE_MENTION` 为 `true` 时也生效。 |
| `DISCORD_IGNORE_NO_MENTION` | 否 | `true` | 当为 `true` 时，如果一条消息 `@提及` 了其他用户但 **没有** 提及机器人，机器人将保持沉默。防止机器人介入针对其他人的对话。仅适用于服务器频道，不适用于私信。 |
| `DISCORD_AUTO_THREAD` | 否 | `true` | 当为 `true` 时，自动为文本频道中的每次 `@提及` 创建一个新帖子，使每个对话独立（类似于 Slack 的行为）。已在帖子或私信中的消息不受影响。 |
| `DISCORD_ALLOW_BOTS` | 否 | `"none"` | 控制机器人如何处理来自其他 Discord 机器人的消息。`"none"` — 忽略所有其他机器人。`"mentions"` — 仅接受那些 `@提及` Hermes 的机器人消息。`"all"` — 接受所有机器人消息。 |
| `DISCORD_REACTIONS` | 否 | `true` | 当为 `true` 时，机器人在处理消息时会添加表情反应（开始处理时 👀，成功时 ✅，出错时 ❌）。设为 `false` 则完全禁用反应。 |
| `DISCORD_IGNORED_CHANNELS` | 否 | — | 逗号分隔的频道 ID，机器人 **绝不** 在这些频道中响应，即使被 `@提及` 也不响应。优先级高于所有其他频道设置。 |
| `DISCORD_ALLOWED_CHANNELS` | 否 | — | 逗号分隔的频道 ID。设置后，机器人 **仅** 在这些频道中响应（如果允许，还包括私信）。覆盖 `config.yaml` 中的 `discord.allowed_channels`。可与 `DISCORD_IGNORED_CHANNELS` 结合使用，表达允许/拒绝规则。 |
| `DISCORD_NO_THREAD_CHANNELS` | 否 | — | 逗号分隔的频道 ID，在这些频道中机器人直接在频道内响应，而不是创建帖子。仅在 `DISCORD_AUTO_THREAD` 为 `true` 时相关。 |
| `DISCORD_REPLY_TO_MODE` | 否 | `"first"` | 控制回复引用行为：`"off"` — 从不回复原始消息，`"first"` — 仅对第一条消息块进行回复引用（默认），`"all"` — 对每个消息块都进行回复引用。 |
| `DISCORD_ALLOW_MENTION_EVERYONE` | 否 | `false` | 当为 `false`（默认）时，即使机器人的响应中包含 `@everyone` 或 `@here` 标记，它也不会发出这些提及。设为 `true` 以重新启用。请参阅下面的 [提及控制](#mention-control)。 |
| `DISCORD_ALLOW_MENTION_ROLES` | 否 | `false` | 当为 `false`（默认）时，机器人不能发出 `@角色` 提及。设为 `true` 以允许。 |
| `DISCORD_ALLOW_MENTION_USERS` | 否 | `true` | 当为 `true`（默认）时，机器人可以通过 ID 提及单个用户。 |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | 否 | `true` | 当为 `true`（默认）时，回复消息会提及原始作者。 |
| `DISCORD_PROXY` | 否 | — | Discord 连接的代理 URL（HTTP、WebSocket、REST）。覆盖 `HTTPS_PROXY`/`ALL_PROXY`。支持 `http://`、`https://` 和 `socks5://` 协议。 |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | 否 | `0.6` | 适配器在刷新排队的文本块之前等待的宽限窗口。用于平滑流式输出。 |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 否 | `2.0` | 当单条消息超过 Discord 长度限制时，分割块之间的延迟。 |
### 配置文件（`config.yaml`） {#config-file-config-yaml}

`~/.hermes/config.yaml` 中的 `discord` 部分与上述环境变量对应。Config.yaml 中的设置会作为默认值应用——如果对应的环境变量已经设置，则环境变量优先。

```yaml
# Discord 专用设置
discord:
  require_mention: true           # 在服务器频道中需要 @提及
  free_response_channels: ""      # 逗号分隔的频道 ID（或 YAML 列表）
  auto_thread: true               # 收到 @提及时自动创建子线程
  reactions: true                 # 处理过程中添加表情反应
  ignored_channels: []            # 机器人永不响应的频道 ID
  no_thread_channels: []          # 机器人回复时不创建子线程的频道 ID
  channel_prompts: {}             # 每个频道的临时系统提示
  allow_mentions:                 # 机器人允许 @提及的对象（安全默认值）
    everyone: false               # @everyone / @here 提及（默认：false）
    roles: false                  # @角色 提及（默认：false）
    users: true                   # @用户 提及（默认：true）
    replied_user: true            # 回复引用时 @原作者（默认：true）

# 会话隔离（适用于所有网关平台，不仅限于 Discord）
group_sessions_per_user: true     # 在共享频道中按用户隔离会话
```

#### `discord.require_mention` {#discord-requiremention}

**类型：** 布尔值 — **默认值：** `true`

启用后，机器人仅在服务器频道中被直接 `@提及` 时才会响应。无论此设置如何，私信始终会得到响应。

#### `discord.free_response_channels` {#discord-freeresponsechannels}

**类型：** 字符串或列表 — **默认值：** `""`

在此处列出的频道 ID 中，机器人会响应所有消息，无需 `@提及`。可以接受逗号分隔的字符串或 YAML 列表：

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

如果某个子线程的父频道在此列表中，该子线程也会变成免提及模式。

自由响应频道还会**跳过自动创建子线程**——机器人会直接内联回复，而不是为每条消息新建一个子线程。这样可以让频道保持轻量聊天界面的可用性。如果你需要子线程行为，请不要将频道列为自由响应（改用正常的 `@提及` 流程）。

#### `discord.auto_thread` {#discord-autothread}

**类型：** 布尔值 — **默认值：** `true`

启用后，在普通文本频道中每次 `@提及` 都会自动为对话创建一个新的子线程。这可以保持主频道整洁，并为每个对话提供独立的会话历史。一旦创建了子线程，该子线程中的后续消息就不需要 `@提及`——机器人知道它已经在参与对话了。

在已有子线程或私信中发送的消息不受此设置影响。列在 `discord.free_response_channels` 或 `discord.no_thread_channels` 中的频道也会绕过自动创建子线程，改为内联回复。

#### `discord.reactions` {#discord-reactions}

**类型：** 布尔值 — **默认值：** `true`
控制机器人是否在消息上添加表情符号作为视觉反馈：
- 👀 当机器人开始处理你的消息时添加
- ✅ 当响应成功送达时添加
- ❌ 如果处理过程中发生错误则添加

如果你觉得这些反应会分散注意力，或者机器人的角色没有 **添加反应** 权限，可以禁用此功能。

#### `discord.ignored_channels` {#discord-ignoredchannels}

**类型：** 字符串或列表 — **默认值：** `[]`

机器人**绝不**响应的频道 ID，即使被直接 `@提及` 也不会响应。此设置优先级最高——如果某个频道在此列表中，机器人会静默忽略该频道的所有消息，无论 `require_mention`、`free_response_channels` 或其他任何设置如何。

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

#### `discord.no_thread_channels` {#discord-nothreadchannels}

**类型：** 字符串或列表 — **默认值：** `[]`

机器人直接在该频道中响应，而不是自动创建线程的频道 ID。此设置仅在 `auto_thread` 为 `true`（默认值）时生效。在这些频道中，机器人会像普通消息一样内联响应，而不会创建新线程。

```yaml
discord:
  no_thread_channels:
    - 1234567890  # 机器人在这里内联响应
```

适用于专门用于机器人交互的频道，在这些频道中创建线程会带来不必要的干扰。

#### `discord.channel_prompts` {#discord-channelprompts}

**类型：** 映射 — **默认值：** `{}`

每个频道的临时系统提示，会在匹配的 Discord 频道或线程的每一轮对话中注入，但不会持久化到对话记录中。

```yaml
discord:
  channel_prompts:
    "1234567890": |
      此频道用于研究任务。偏好深度比较、引用和简洁的综合。
    "9876543210": |
      此论坛用于治疗式支持。要温暖、接地气且不带评判。
```

行为：
- 精确的线程/频道 ID 匹配优先。
- 如果消息到达线程或论坛帖子内部，且该线程没有显式条目，Hermes 会回退到父频道/论坛 ID。
- 提示在运行时临时应用，因此更改它们会立即影响未来的对话轮次，而无需重写过去的会话历史。

#### `group_sessions_per_user` {#groupsessionsperuser}

**类型：** 布尔值 — **默认值：** `true`

这是一个全局网关设置（非 Discord 专用），控制同一频道中的用户是否获得隔离的会话历史。

当为 `true` 时：在 `#research` 频道中聊天的 Alice 和 Bob 各自拥有与 Hermes 的独立对话。当为 `false` 时：整个频道共享一个对话记录和一个正在运行的 Agent 槽位。

```yaml
group_sessions_per_user: true
```

有关每种模式的完整含义，请参阅上面的[会话模型](#session-model-in-discord)部分。

#### `display.tool_progress` {#display-toolprogress}

**类型：** 字符串 — **默认值：** `"all"` — **可选值：** `off`、`new`、`all`、`verbose`

控制机器人在处理过程中是否在聊天中发送进度消息（例如“正在读取文件...”、“正在运行终端命令...”）。这是一个适用于所有平台的全局网关设置。
```yaml
display:
  tool_progress: "all"    # off | new | all | verbose
```

- `off` — 不显示进度消息
- `new` — 仅显示每轮的第一个工具调用
- `all` — 显示所有工具调用（在网关消息中截断为 40 个字符）
- `verbose` — 显示完整的工具调用详情（可能产生长消息）

#### `display.tool_progress_command` {#display-toolprogresscommand}

**类型：** 布尔值 — **默认值：** `false`

启用后，网关中会提供 `/verbose` 斜杠命令，让你可以循环切换工具进度模式（`off → new → all → verbose → off`），而无需编辑 config.yaml。

```yaml
display:
  tool_progress_command: true
```

## 交互式模型选择器 {#interactive-model-picker}

在 Discord 频道中发送不带参数的 `/model`，即可打开一个基于下拉菜单的模型选择器：

1. **提供商选择** — 一个显示可用提供商的下拉菜单（最多 25 个）。
2. **模型选择** — 第二个下拉菜单，显示所选提供商的模型（最多 25 个）。

选择器在 120 秒后超时。只有授权用户（`DISCORD_ALLOWED_USERS` 中的用户）才能与其交互。如果你知道模型名称，可以直接输入 `/model <名称>`。

## 技能的本地斜杠命令 {#native-slash-commands-for-skills}

Hermes 会自动将已安装的技能注册为 **原生 Discord 应用命令**。这意味着技能会出现在 Discord 的自动补全 `/` 菜单中，与内置命令并列。

- 每个技能都会成为一个 Discord 斜杠命令（例如 `/code-review`、`/ascii-art`）
- 技能接受一个可选的 `args` 字符串参数
- Discord 对每个机器人有 100 个应用命令的限制——如果你的技能数量超过可用槽位，多余的技能会被跳过，并在日志中显示警告
- 技能在机器人启动时与 `/model`、`/reset` 和 `/background` 等内置命令一起注册

无需额外配置——任何通过 `hermes skills install` 安装的技能都会在下次网关重启时自动注册为 Discord 斜杠命令。

### 禁用斜杠命令注册 {#disabling-slash-command-registration}

如果你针对同一个 Discord 应用运行多个 Hermes 网关（例如，预发布环境 + 生产环境），则只有一个网关应拥有全局斜杠命令的注册权——否则，最后一次启动的网关会覆盖之前的注册，导致注册状态不稳定。在“从属”网关上关闭斜杠注册：

```yaml
gateway:
  platforms:
    discord:
      extra:
        slash_commands: false   # 默认值：true
```

在“主”网关上保留此设置为 `true`，可保持正常行为——内置命令和已安装技能会出现在全局 `/` 菜单中。

## 发送媒体（`send_message` + `MEDIA:` 标签） {#sending-media-sendmessage-media-tags}

Discord 适配器通过 `send_message` 工具和 Agent 发出的内联 `MEDIA:/path/to/file` 标签，支持所有常见媒体类型的原生文件上传：

| 类型 | 发送方式 |
|---|---|
| 图片（PNG/JPG/WebP） | 原生 Discord 图片附件，带有内联预览 |
| 动画 GIF | `send_animation` 以上传为 `animation.gif` 的方式发送，Discord 会内联播放（而不是显示为静态缩略图） |
| 视频（MP4/MOV） | `send_video` — 原生视频播放器 |
| 音频 / 语音 | `send_voice` — 尽可能发送原生语音消息，否则以文件附件形式发送 |
| 文档（PDF/ZIP/docx 等） | `send_document` — 原生附件，带有下载按钮 |
Discord 的上传大小限制取决于服务器的加速等级（免费版 25 MB，最高 500 MB）。如果 Hermes 收到 HTTP 413 错误，适配器会回退到指向本地缓存路径的链接，而不是静默失败。

## 家庭频道 {#home-channel}

你可以指定一个“家庭频道”，机器人会将主动消息（例如 cron 任务输出、提醒和通知）发送到这里。有两种设置方法：

### 使用斜杠命令 {#using-the-slash-command}

在机器人所在的任意 Discord 频道中输入 `/sethome`。该频道即成为家庭频道。

### 手动配置 {#manual-configuration}

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

将 ID 替换为实际的频道 ID（右键 → 在开发者模式下复制频道 ID）。

## 语音消息 {#voice-messages}

Hermes Agent 支持 Discord 语音消息：

- **收到的语音消息** 会自动使用已配置的 STT（语音转文字）服务商进行转录：本地 `faster-whisper`（无需密钥）、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）。
- **文字转语音**：使用 `/voice tts` 让机器人在回复文本的同时发送语音音频回复。
- **Discord 语音频道**：Hermes 还可以加入语音频道，聆听用户说话，并在频道中回话。

完整的设置和操作指南，请参阅：
- [语音模式](/user-guide/features/voice-mode)
- [将语音模式与 Hermes 结合使用](/guides/use-voice-mode-with-hermes)

## 论坛频道 {#forum-channels}

Discord 论坛频道（类型 15）不接受直接消息——论坛中的每个帖子都必须是一个线程。Hermes 会自动检测论坛频道，并在需要向那里发送消息时创建一个新的线程帖子。因此，`send_message`、TTS、图片、语音消息和文件附件等功能都能正常工作，无需 Agent 进行特殊处理。

- **线程名称** 来源于消息的第一行（去除 Markdown 标题前缀，最多截取 100 个字符）。当消息仅包含附件时，文件名将作为后备的线程名称。
- **附件** 会随新线程的起始消息一起发送——无需单独的上传步骤，也不会部分发送。
- **一次调用，一个线程**：每次向论坛发送都会创建一个新线程。因此，连续向同一个论坛发送消息会产生多个独立的线程。
- **检测机制有三层**：首先检查频道目录缓存，然后是进程本地探针缓存，最后作为最后手段进行实时的 `GET /channels/{id}` 探针（其结果会在进程生命周期内被记忆化）。

刷新目录（在支持该功能的平台上使用 `/channels refresh` 命令，或重启网关）会填充缓存，包括机器人启动后创建的任何论坛频道。

## 故障排除 {#troubleshooting}

### 机器人显示在线，但不响应消息 {#bot-is-online-but-not-responding-to-messages}

**原因**：消息内容意图被禁用。

**解决方法**：前往 [开发者门户](https://discord.com/developers/applications) → 你的应用 → Bot → 特权网关意图 → 启用 **消息内容意图** → 保存更改。然后重启网关。

### 启动时出现“不允许的意图”错误 {#disallowed-intents-error-on-startup}
**原因**：你的代码请求了开发者门户中未启用的意图。

**解决方法**：在 Bot 设置中启用所有三个特权网关意图（Presence、Server Members、Message Content），然后重启。

### Bot 无法看到特定频道中的消息 {#bot-can-t-see-messages-in-a-specific-channel}

**原因**：Bot 的角色没有查看该频道的权限。

**解决方法**：在 Discord 中，进入频道设置 → 权限 → 添加 Bot 的角色，并启用 **查看频道** 和 **读取消息历史**。

### 403 Forbidden 错误 {#403-forbidden-errors}

**原因**：Bot 缺少所需权限。

**解决方法**：使用步骤 5 中的 URL 重新邀请 Bot 并赋予正确权限，或者在服务器设置 → 角色中手动调整 Bot 的角色权限。

### Bot 离线 {#bot-is-offline}

**原因**：Hermes 网关未运行，或 token 不正确。

**解决方法**：检查 `hermes gateway` 是否正在运行。验证 `.env` 文件中的 `DISCORD_BOT_TOKEN`。如果你最近重置了 token，请更新它。

### "User not allowed" / Bot 忽略你 {#user-not-allowed-bot-ignores-you}

**原因**：你的用户 ID 不在 `DISCORD_ALLOWED_USERS` 中。

**解决方法**：将你的用户 ID 添加到 `~/.hermes/.env` 的 `DISCORD_ALLOWED_USERS` 中，然后重启网关。

### 同一频道中的人意外共享上下文 {#people-in-the-same-channel-are-sharing-context-unexpectedly}

**原因**：`group_sessions_per_user` 被禁用，或者平台无法为该上下文中的消息提供用户 ID。

**解决方法**：在 `~/.hermes/config.yaml` 中设置以下内容，然后重启网关：

```yaml
group_sessions_per_user: true
```

如果你有意想要共享房间对话，可以保持关闭——但要注意会共享对话历史记录和共享中断行为。

## 安全 {#security}

:::warning
始终设置 `DISCORD_ALLOWED_USERS`（或 `DISCORD_ALLOWED_ROLES`）来限制谁可以与 Bot 交互。如果没有设置，网关默认会拒绝所有用户，这是一种安全措施。只授权你信任的人——授权用户拥有对 Agent 能力的完全访问权限，包括工具使用和系统访问。
:::

### 基于角色的访问控制 {#role-based-access-control}

对于通过角色（而非单个用户列表）管理访问权限的服务器（如版主团队、支持人员、内部工具），请使用 `DISCORD_ALLOWED_ROLES`——一个以逗号分隔的角色 ID 列表。拥有这些角色之一的任何成员都将被授权。

```bash
# ~/.hermes/.env — 可与 DISCORD_ALLOWED_USERS 一起使用，或替代它
DISCORD_ALLOWED_ROLES=987654321098765432,876543210987654321
```

语义说明：

- **与用户白名单取或关系。** 如果用户的 ID 在 `DISCORD_ALLOWED_USERS` 中，**或者**他们拥有 `DISCORD_ALLOWED_ROLES` 中的任何角色，则该用户被授权。
- **自动启用服务器成员意图。** 当设置了 `DISCORD_ALLOWED_ROLES` 时，Bot 在连接时会自动启用 Members 意图——Discord 需要此意图才能随成员记录发送角色信息。
- **使用角色 ID，而非角色名称。** 从 Discord 获取：**用户设置 → 高级 → 开启开发者模式**，然后右键点击任意角色 → **复制角色 ID**。
- **私信回退。** 在私信中，角色检查会扫描共同服务器；如果用户在任何一个共享服务器中拥有允许的角色，则在私信中也会被授权。
这是管理团队人员流动时的首选模式——新管理员在获得角色后即可立即访问，无需编辑 `.env` 或重启网关。

### 提及控制 {#mention-control}

默认情况下，Hermes 会阻止机器人发送 `@everyone`、`@here` 和角色提及，即使其回复中包含这些标记。这可以防止措辞不当的提示或回显的用户内容向整个服务器发送垃圾信息。单个 `@用户` 提醒和回复引用提醒（那个小小的“回复……”标签）保持启用，以便正常对话仍能进行。

你可以通过环境变量或 `config.yaml` 来放宽这些默认设置：

```yaml
# ~/.hermes/config.yaml
discord:
  allow_mentions:
    everyone: false      # 允许机器人发送 @everyone / @here
    roles: false         # 允许机器人发送 @角色 提及
    users: true          # 允许机器人发送单个 @用户 提及
    replied_user: true   # 回复消息时提醒作者
```

```bash
# ~/.hermes/.env — 环境变量优先级高于 config.yaml
DISCORD_ALLOW_MENTION_EVERYONE=false
DISCORD_ALLOW_MENTION_ROLES=false
DISCORD_ALLOW_MENTION_USERS=true
DISCORD_ALLOW_MENTION_REPLIED_USER=true
```

:::tip
除非你确切知道为什么需要，否则请将 `everyone` 和 `roles` 保持为 `false`。LLM 很容易在看似正常的回复中生成字符串 `@everyone`；如果没有此保护，那将通知你服务器中的每个成员。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。
