---
sidebar_position: 3
title: "Discord"
description: "将 Hermes Agent 设置为 Discord 机器人"
---

<a id="discord-setup"></a>
# Discord 设置

Hermes Agent 会以 Discord 机器人的形式集成，让你可以通过私信或服务器频道与你的 AI 助手聊天。机器人接收你的消息，通过 Hermes Agent 管道（包括工具使用、记忆和推理）进行处理，并实时回复。它支持文本、语音消息、文件附件和斜杠命令。

在开始设置之前，这里大部分人都想知道：Hermes 进入你的服务器后会有什么表现。

<a id="how-hermes-behaves"></a>
## Hermes 的行为表现

| 上下文 | 行为 |
|---------|----------|
| **私信（DM）** | Hermes 会回复每一条消息。无需 `@提及`。每条私信有独立的会话。 |
| **服务器频道** | 默认情况下，只有当你在消息中 `@提及` Hermes 时，它才会回复。如果你在频道中发消息但没有提及它，Hermes 会忽略该消息。 |
| **自由回复频道** | 你可以通过 `DISCORD_FREE_RESPONSE_CHANNELS` 设置特定频道为无需提及，或者全局禁用提及（`DISCORD_REQUIRE_MENTION=false`）。这些频道中的消息会以内联方式回复——跳过自动创建子线程，从而保持频道的轻量聊天体验。 |
| **线程** | Hermes 会在同一线程中回复。提及规则仍然适用，除非该线程或其父频道被设置为自由回复。线程的会话历史与父频道隔离。 |
| **多用户共享频道** | 默认情况下，Hermes 会在频道内针对每个用户隔离会话历史，以保证安全和清晰。两个人在同一频道中聊天时，不会共享同一份对话记录，除非你明确禁用了此功能。 |
| **提及其他用户的消息** | 当 `DISCORD_IGNORE_NO_MENTION` 为 `true`（默认值）时，如果一条消息 @提及了其他用户但**没有**提及机器人，Hermes 会保持沉默。这可以防止机器人介入针对其他人的对话。如果你希望机器人回复所有消息（无论提及了谁），请将该值设为 `false`。此设置仅适用于服务器频道，不适用于私信。 |

:::tip
如果你希望有一个普通的机器人帮助频道，人们可以在其中与 Hermes 交流而不必每次都 @提及它，请将该频道添加到 `DISCORD_FREE_RESPONSE_CHANNELS` 中。
:::

<a id="discord-gateway-model"></a>
### Discord 网关模型

Discord 上的 Hermes 并非无状态回复的 Webhook。它通过完整的消息网关运行，这意味着每条传入的消息都会经过：

1. 授权（`DISCORD_ALLOWED_USERS`）
2. 提及/自由回复检查
3. 会话查找
4. 会话记录加载
5. 正常的 Hermes Agent 执行，包括工具、记忆和斜杠命令
6. 将回复发送回 Discord

这点很重要，因为在繁忙服务器中的行为取决于 Discord 路由和 Hermes 会话策略两方面。

<a id="session-model-in-discord"></a>
### Discord 中的会话模型 {#session-model-in-discord}

默认情况下：

- 每条私信都有自己独立的会话
- 每个服务器线程都有自己独立的会话命名空间
- 共享频道中的每个用户在该频道内都有自己独立的会话

因此，如果 Alice 和 Bob 都在 `#research` 频道中与 Hermes 交谈，默认情况下 Hermes 会将它们视为独立的对话，尽管他们使用的是同一个可见的 Discord 频道。
这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个房间共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间可能有用，但同时也意味着：

- 用户共享上下文增长和 token 成本
- 一个人的长工具密集型任务可能会膨胀其他人的上下文
- 一个人正在进行的运行可能会打断同房间另一个人的后续操作

<a id="interrupts-and-concurrency"></a>
### 中断与并发

Hermes 通过会话键跟踪正在运行的 Agent。

使用默认的 `group_sessions_per_user: true`：

- Alice 打断自己正在进行的请求只会影响 Alice 在该频道中的会话
- Bob 可以在同一频道中继续说话，而不会继承 Alice 的历史记录或打断 Alice 的运行

使用 `group_sessions_per_user: false`：

- 整个房间共享该频道/线程的一个运行中 Agent 槽位
- 来自不同人的后续消息可能会相互打断或在彼此之后排队

本指南将带你完成完整的设置过程——从在 Discord 开发者门户创建机器人到发送第一条消息。

<a id="step-1-create-a-discord-application"></a>
## 第一步：创建 Discord 应用

1. 前往 [Discord 开发者门户](https://discord.com/developers/applications) 并使用你的 Discord 账户登录。
2. 点击右上角的 **New Application**。
3. 为你的应用输入一个名称（例如 "Hermes Agent"），并接受开发者服务条款。
4. 点击 **Create**。

你将进入 **General Information** 页面。记下 **Application ID**——稍后你需要它来构建邀请链接。

<a id="step-2-create-the-bot"></a>
## 第二步：创建机器人

1. 在左侧边栏中，点击 **Bot**。
2. Discord 会自动为你的应用创建一个机器人用户。你会看到机器人的用户名，你可以自定义它。
3. 在 **Authorization Flow** 下：
   - 将 **Public Bot** 设置为 **ON**——这是使用 Discord 提供的邀请链接所必需的（推荐）。这允许安装选项卡生成一个默认的授权 URL。
   - 将 **Require OAuth2 Code Grant** 保持为 **OFF**。

:::tip
你可以在此页面上为你的机器人设置自定义头像和横幅。这就是用户在 Discord 中看到的内容。
:::

:::info[私有机器人替代方案]
如果你希望保持机器人私有（Public Bot = OFF），你**必须**在第五步中使用 **Manual URL** 方法，而不是使用安装选项卡。Discord 提供的链接需要启用 Public Bot。
:::

<a id="step-3-enable-privileged-gateway-intents"></a>
## 第三步：启用特权网关意图

这是整个设置中最关键的一步。如果没有启用正确的意图，你的机器人将连接到 Discord，但**将无法读取消息内容**。

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
如果你的机器人在线但从不回复消息，那么 **Message Content Intent** 几乎肯定被禁用了。回到 [开发者门户](https://discord.com/developers/applications)，选择你的应用 → Bot → Privileged Gateway Intents，确保 **Message Content Intent** 已切换为 ON。点击 **Save Changes**。
:::

**关于服务器数量：**
- 如果你的机器人位于 **少于 100 个服务器** 中，你可以自由地开关这些意图。
- 如果你的机器人位于 **100 个或更多服务器** 中，Discord 要求你提交验证申请才能使用特权意图。个人使用无需担心。

点击页面底部的 **Save Changes**。

<a id="step-4-get-the-bot-token"></a>
## 第 4 步：获取机器人令牌

机器人令牌是 Hermes Agent 用来以你的机器人身份登录的凭证。仍在 **Bot** 页面：

1. 在 **Token** 部分下，点击 **Reset Token**。
2. 如果你在 Discord 账户上启用了双重身份验证，请输入你的 2FA 代码。
3. Discord 会显示你的新令牌。**立即复制它。**

:::warning[令牌仅显示一次]
令牌只显示一次。如果你丢失了它，你需要重置并生成一个新令牌。切勿公开分享你的令牌或将其提交到 Git——任何拥有此令牌的人都可以完全控制你的机器人。
:::

将令牌存放在安全的地方（例如密码管理器）。你将在第 8 步中用到它。

<a id="step-5-generate-the-invite-url"></a>
## 第 5 步：生成邀请链接

你需要一个 OAuth2 URL 来将机器人邀请到你的服务器。有两种方法：

<a id="option-a-using-the-installation-tab-recommended"></a>
### 选项 A：使用安装标签页（推荐）

:::note[需要公开机器人]
此方法要求第 2 步中的 **Public Bot** 设置为 **ON**。如果你将 Public Bot 设置为 OFF，请改用下面的手动 URL 方法。
:::

1. 在左侧边栏中，点击 **Installation**。
2. 在 **Installation Contexts** 下，启用 **Guild Install**。
3. 对于 **Install Link**，选择 **Discord Provided Link**。
4. 在 **Default Install Settings** 的 Guild Install 下：
   - **Scopes**：选择 `bot` 和 `applications.commands`
   - **Permissions**：选择下面列出的权限。

<a id="option-b-manual-url"></a>
### 选项 B：手动 URL

你可以直接使用以下格式构建邀请链接：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

将 `YOUR_APP_ID` 替换为第 1 步中的应用程序 ID。

<a id="required-permissions"></a>
### 所需权限

这些是你的机器人所需的最低权限：

- **View Channels** — 查看它可以访问的频道
- **Send Messages** — 回复你的消息
- **Embed Links** — 格式化富文本回复
- **Attach Files** — 发送图片、音频和文件输出
- **Read Message History** — 维护对话上下文
<a id="recommended-additional-permissions"></a>
### 推荐的额外权限

- **在帖子中发送消息**—在帖子对话中回复
- **添加反应**—对消息添加表情反应以表示确认

<a id="permission-integers"></a>
### 权限整数

| 级别 | 权限整数 | 包含内容 |
|-------|-------------------|-----------------|
| 最低 | `117760` | 查看频道、发送消息、阅读消息历史、附加文件 |
| 推荐 | `274878286912` | 以上全部内容，外加嵌入链接、在帖子中发送消息、添加反应 |

<a id="step-6-invite-to-your-server"></a>
## 第 6 步：邀请到你的服务器

1. 在浏览器中打开邀请链接（来自安装选项卡或你手动构建的链接）。
2. 在**添加到服务器**下拉菜单中选择你的服务器。
3. 点击**继续**，然后点击**授权**。
4. 如果提示，完成验证码。

:::info
你需要在 Discord 服务器上拥有**管理服务器**权限才能邀请机器人。如果下拉列表中没有你的服务器，请让服务器管理员使用邀请链接。
:::

授权后，机器人将出现在你的服务器成员列表中（它将以离线状态显示，直到你启动 Hermes gateway）。

<a id="step-7-find-your-discord-user-id"></a>
## 第 7 步：查找你的 Discord 用户 ID

Hermes Agent 使用你的 Discord 用户 ID 来控制谁能与机器人交互。查找方法如下：

1. 打开 Discord（桌面端或网页版）。
2. 进入**设置** → **高级** → 将**开发者模式**开关打开。
3. 关闭设置。
4. 右键点击你自己的用户名（在消息、成员列表或你的个人资料中）→ **复制用户 ID**。

你的用户 ID 是一个长数字，例如 `284102345871466496`。

:::tip
开发者模式还可以让你以同样的方式复制**频道 ID** 和**服务器 ID**——右键频道名或服务器名，选择“复制 ID”。如果你想手动设置一个主频道，会需要频道 ID。
:::

<a id="step-8-configure-hermes-agent"></a>
## 第 8 步：配置 Hermes Agent

<a id="option-a-interactive-setup-recommended"></a>
### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在提示时选择 **Discord**，然后在询问时粘贴你的机器人令牌和用户 ID。

<a id="option-b-manual-configuration"></a>
### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env` 文件中：

```bash
# 必填
DISCORD_BOT_TOKEN=你的机器人令牌
DISCORD_ALLOWED_USERS=284102345871466496

# 多个允许的用户（逗号分隔）
# DISCORD_ALLOWED_USERS=284102345871466496,198765432109876543
```

然后启动 gateway：

```bash
hermes gateway
```

机器人应在几秒钟内上线 Discord。发送一条消息给它——可以是直接消息或在它能看到的频道中发送——来进行测试。

:::tip
你可以将 `hermes gateway` 在后台运行或设为 systemd 服务以实现持久运行。详见部署文档。
:::

<a id="configuration-reference"></a>
## 配置参考

Discord 的行为通过两个文件控制：**`~/.hermes/.env`** 用于存储凭证和环境级别开关，**`~/.hermes/config.yaml`** 用于结构化设置。当两者同时设置时，环境变量总是优先于 config.yaml 中的值。

<a id="environment-variables-env"></a>
### 环境变量（`.env`）

| 变量 | 是否必填 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | **是** | — | 来自 [Discord 开发者门户](https://discord.com/developers/applications) 的机器人令牌。 |
| `DISCORD_ALLOWED_USERS` | **是** | — | 允许与机器人交互的 Discord 用户 ID（逗号分隔）。如果没有此项**或** `DISCORD_ALLOWED_ROLES`，gateway 将拒绝所有用户。 |
| `DISCORD_ALLOWED_ROLES` | 否 | — | 逗号分隔的 Discord 角色 ID。拥有这些角色之一的成员将被授权 — 和 `DISCORD_ALLOWED_USERS` 是“或”逻辑。连接时自动启用**服务器成员意图**。当审核团队人员变动时非常有用：新成员一旦获得角色即可获得访问权限，无需推送配置。 |
| `DISCORD_HOME_CHANNEL` | 否 | — | 机器人发送主动消息（cron 输出、提醒、通知）的频道 ID。 |
| `DISCORD_HOME_CHANNEL_NAME` | 否 | `"Home"` | 主频道在日志和状态输出中的显示名称。 |
| `DISCORD_COMMAND_SYNC_POLICY` | 否 | `"safe"` | 控制原生斜杠命令启动同步。`"safe"` 会对比现有全局命令，只更新有变化的部分；当 Discord 元数据变更无法通过补丁应用时，会重新创建命令。`"bulk"` 保留旧的 `tree.sync()` 行为。`"off"` 完全跳过启动同步。 |
| `DISCORD_REQUIRE_MENTION` | 否 | `true` | 当为 `true` 时，机器人仅在服务器频道中被 `@提及` 时才响应。设为 `false` 则响应所有频道中的每条消息。 |
| `DISCORD_THREAD_REQUIRE_MENTION` | 否 | `false` | 当为 `true` 时，禁用帖子的 @提及 快捷方式——帖子的门槛和频道一样，即使在机器人已经参与的情况下也要求 `@提及`。当多个机器人共享一个帖子且你希望每个机器人只在被明确 `@提及` 时触发时使用。 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 否 | — | 逗号分隔的频道 ID，在这些频道中机器人无需 `@提及` 即可响应，即使 `DISCORD_REQUIRE_MENTION` 为 `true`。 |
| `DISCORD_IGNORE_NO_MENTION` | 否 | `true` | 当为 `true` 时，如果一条消息 `@提及` 了其他用户但**没有**提及机器人，机器人保持静默。避免机器人介入针对他人的对话。仅适用于服务器频道，不适用于直接消息。 |
| `DISCORD_AUTO_THREAD` | 否 | `true` | 当为 `true` 时，自动为文本频道中的每条 `@提及` 创建新帖子，使每个对话独立（类似 Slack 的行为）。已存在于帖子或直接消息中的消息不受影响。 |
| `DISCORD_ALLOW_BOTS` | 否 | `"none"` | 控制机器人如何处理来自其他 Discord 机器人的消息。`"none"` — 忽略所有其他机器人。`"mentions"` — 只接受 @提及 Hermes 的机器人消息。`"all"` — 接受所有机器人消息。 |
| `DISCORD_REACTIONS` | 否 | `true` | 当为 `true` 时，机器人在处理消息期间添加表情反应（👀 开始处理时，✅ 成功时，❌ 错误时）。设为 `false` 完全禁用反应。 |
| `DISCORD_IGNORED_CHANNELS` | 否 | — | 逗号分隔的频道 ID，机器人**绝不**在这些频道中响应，即使被 `@提及`。优先级高于所有其他频道设置。 |
| `DISCORD_ALLOWED_CHANNELS` | 否 | — | 逗号分隔的频道 ID。设置后，机器人**仅**在这些频道中响应（加上直接消息如果允许）。覆盖 `config.yaml` 中的 `discord.allowed_channels`。可与 `DISCORD_IGNORED_CHANNELS` 结合使用以表达允许/拒绝规则。 |
| `DISCORD_NO_THREAD_CHANNELS` | 否 | — | 逗号分隔的频道 ID，在这些频道中机器人直接在频道中响应而不是创建帖子。仅当 `DISCORD_AUTO_THREAD` 为 `true` 时有效。 |
| `DISCORD_HISTORY_BACKFILL` | 否 | `true` | 当为 `true` 时，在机器人被 @提及 时，将频道中最近的滚动记录（自机器人上次响应以来）附在用户消息之前。用于恢复机器人因 `require_mention` 而错过的上下文。在直接消息和自由响应频道中跳过。设为 `false` 禁用。 |
| `DISCORD_HISTORY_BACKFILL_LIMIT` | 否 | `50` | 在组装回填块时最多向后扫描的消息数量。实际扫描通常会更早停止——停在机器人在频道中自己最后一条消息处。 |
| `DISCORD_REPLY_TO_MODE` | 否 | `"first"` | 控制回复引用行为：`"off"` — 从不回复原始消息，`"first"` — 仅在第一个消息块中回复引用（默认），`"all"` — 在每个消息块中都回复引用。 |
| `DISCORD_ALLOW_MENTION_EVERYONE` | 否 | `false` | 当为 `false`（默认）时，即使机器人的响应中包含这些标记，也无法 @提及 `@everyone` 或 `@here`。设为 `true` 启用。见下方[提及控制](#mention-control)。 |
| `DISCORD_ALLOW_MENTION_ROLES` | 否 | `false` | 当为 `false`（默认）时，机器人无法 @提及 `@role`。设为 `true` 允许。 |
| `DISCORD_ALLOW_MENTION_USERS` | 否 | `true` | 当为 `true`（默认）时，机器人可以通过 ID @提及单个用户。 |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | 否 | `true` | 当为 `true`（默认）时，回复消息会 @提及原始作者。 |
| `DISCORD_PROXY` | 否 | — | Discord 连接的代理 URL（HTTP、WebSocket、REST）。覆盖 `HTTPS_PROXY`/`ALL_PROXY`。支持 `http://`、`https://` 和 `socks5://` 协议。 |
| `DISCORD_ALLOW_ANY_ATTACHMENT` | 否 | `false` | 当为 `true` 时，机器人接受任何文件类型的附件（不仅限于内置的 PDF/文本/压缩包/Office 允许列表）。未知类型会缓存到磁盘，并以 `application/octet-stream` MIME 类型呈现给 agent 作为本地路径，以便 agent 使用 `terminal` / `read_file` / `ffprobe` 等进行检查。 |
| `DISCORD_MAX_ATTACHMENT_BYTES` | 否 | `33554432` | gateway 将下载和缓存的每个附件的最大字节数。默认 32 MiB。设为 `0` 表示无上限（附件在写入时保留在内存中，因此无上限会带来实际的内存开销）。 |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | 否 | `0.6` | 适配器在刷新排队的文本块之前等待的宽限时间窗口。用于平滑流式输出。 |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 否 | `2.0` | 当单条消息超过 Discord 长度限制时，拆分块之间的延迟时间。 |
<a id="config-file-config-yaml"></a>
### 配置文件 (`config.yaml`)

`~/.hermes/config.yaml` 中的 `discord` 部分与上述环境变量对应。Config.yaml 中的设置会作为默认值应用——如果已设置等效的环境变量，则环境变量优先。

```yaml
# Discord 特定设置
discord:
  require_mention: true           # 在服务器频道中需要 @提及
  thread_require_mention: false   # 如果为 true，则在子线程中也要求 @提及（多 Agent 子线程）
  free_response_channels: ""      # 逗号分隔的频道 ID（或 YAML 列表）
  auto_thread: true               # 在 @提及 时自动创建子线程
  reactions: true                 # 处理过程中添加表情符号反应
  ignored_channels: []            # 机器人永不响应的频道 ID
  no_thread_channels: []          # 机器人响应但不创建子线程的频道 ID
  history_backfill: true          # 在提及前追加最近的频道滚动历史（默认：true）
  history_backfill_limit: 50      # 向后扫描的最大消息数（默认：50）
  channel_prompts: {}             # 每个频道的临时系统提示
  allow_mentions:                 # 机器人允许 @提及 的内容（安全默认值）
    everyone: false               # @everyone / @here 提及（默认：false）
    roles: false                  # @角色 提及（默认：false）
    users: true                   # @用户 提及（默认：true）
    replied_user: true            # 回复引用会 @提及 原作者（默认：true）

# 会话隔离（适用于所有网关平台，不仅限于 Discord）
group_sessions_per_user: true     # 在共享频道中按用户隔离会话
```

<a id="discord-requiremention"></a>
#### `discord.require_mention`

**类型：** 布尔值 — **默认值：** `true`

启用后，机器人仅在服务器频道中被直接 `@提及` 时才会响应。无论此设置如何，私信始终会得到响应。

<a id="discord-threadrequiremention"></a>
#### `discord.thread_require_mention`

**类型：** 布尔值 — **默认值：** `false`

默认情况下，一旦机器人参与了一个子线程（在 `@提及` 时自动创建，或回复过一次），它就会继续响应该子线程中的每条后续消息，而无需再次被 `@提及`。对于一对一对话来说，这是正确的默认行为。

在**多 Agent 子线程**中，用户每轮只与一个 Agent 对话，这个默认行为就会成为一个隐患——子线程中的其他每个 Agent 也会对每条消息做出响应，既消耗额度又刷屏。设置 `thread_require_mention: true` 可以禁用子线程中的快捷方式，让子线程的触发方式与频道一致。显式的 `@提及` 仍然像以前一样工作。

```yaml
discord:
  require_mention: true
  thread_require_mention: true    # 多 Agent 设置
```

<a id="discord-freeresponsechannels"></a>
#### `discord.free_response_channels`

**类型：** 字符串或列表 — **默认值：** `""`

机器人无需 `@提及` 即可响应所有消息的频道 ID。接受逗号分隔的字符串或 YAML 列表：

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
如果某个线程的父频道在此列表中，则该线程也会变为免提及（mention-free）。

自由回复频道还会**跳过自动创建线程**——机器人会以内联方式回复，而不是为每条消息新建一个线程。这有助于保持频道作为轻量级聊天界面的可用性。如果你需要线程行为，就不要将频道列为自由回复频道（而是使用正常的 `@提及` 流程）。

<a id="discord-autothread"></a>
#### `discord.auto_thread`

**类型：** boolean — **默认值：** `true`

启用时，普通文本频道中的每一条 `@提及` 会自动为该对话创建一个新线程。这可以使主频道保持整洁，并为每个对话提供独立的会话历史。线程创建后，在该线程中后续的消息不需要再次 `@提及`——机器人知道它已经在参与对话。对于多机器人设置，若要在线程内禁用此快捷方式，请将 [`thread_require_mention`](#discordthread_require_mention) 设为 `true`。

在现有线程或私信（DM）中发送的消息不受此设置影响。`discord.free_response_channels` 或 `discord.no_thread_channels` 中列出的频道也会跳过自动创建线程，而采用内联回复。

<a id="discord-reactions"></a>
#### `discord.reactions`

**类型：** boolean — **默认值：** `true`

控制机器人是否向消息添加表情符号反应作为视觉反馈：
- 👀 当机器人开始处理你的消息时添加
- ✅ 当响应成功发送时添加
- ❌ 如果处理过程中发生错误则添加

如果你觉得这些反应会分散注意力，或者机器人角色没有 **添加反应** 权限，可以禁用此功能。

<a id="discord-ignoredchannels"></a>
#### `discord.ignored_channels`

**类型：** string 或 list — **默认值：** `[]`

机器人**永不**回复的频道 ID，即使直接 `@提及` 也不响应。此设置优先级最高——如果某个频道在此列表中，机器人会静默忽略该频道的所有消息，无论 `require_mention`、`free_response_channels` 或其他任何设置如何。

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

<a id="discord-nothreadchannels"></a>
#### `discord.no_thread_channels`

**类型：** string 或 list — **默认值：** `[]`

机器人会在此频道 ID 列表中直接回复，而不是自动创建线程。该设置仅在 `auto_thread` 为 `true`（默认值）时生效。在这些频道中，机器人像普通消息一样以内联方式回复，而不是生成新线程。

```yaml
discord:
  no_thread_channels:
    - 1234567890  # 机器人在这里内联回复
```

适用于专用于机器人交互的频道，在这些频道中，线程只会增加不必要的噪音。

<a id="discord-channelprompts"></a>
#### `discord.channel_prompts`

**类型：** mapping — **默认值：** `{}`

针对每个频道的临时系统提示，在匹配的 Discord 频道或线程的每一轮交互中注入，但不会持久保存到对话记录中。

```yaml
discord:
  channel_prompts:
    "1234567890": |
      此频道用于研究任务。偏好深入比较、
      引用和简洁的综合。
    "9876543210": |
      此论坛用于治疗式支持。请保持温暖、接地气
      且不评判。
```
行为：
- 精确的线程/频道 ID 匹配优先。
- 如果消息到达线程或论坛帖子内部，且该线程没有显式条目，Hermes 会回退到父频道/论坛 ID。
- 提示在运行时临时生效，因此更改提示会立即影响未来的轮次，而无需重写过去的会话历史。

<a id="discord-historybackfill"></a>
#### `discord.history_backfill`

**类型：** boolean — **默认值：** `true`

启用后，机器人会在每次 `@提及` 时恢复错过的频道消息。当 `require_mention: true` 时，机器人只处理直接 @ 它的消息——频道中的其他所有内容对会话记录都是不可见的。历史回填会在触发时向后扫描最近的频道历史，收集机器人上次回复与当前提及之间的消息，并将其作为上下文包含进来。

按场景的行为：

- **服务器频道**（使用 `require_mention: true`）：回填从机器人上次回复后开始扫描频道。当其他参与者在机器人未被 @ 时发布了消息时，此功能很有用。
- **线程**：回填只扫描线程本身——在线程上调用 Discord 的 `channel.history()` 只返回该线程的消息，而不是父频道的。这是正确的范围，因为线程通常是自包含的对话。
- **私信**：跳过。每条私信消息都会触发机器人，因此会话记录已经完整——没有提及间隙需要填补。
- **自由回复频道**和**机器人自身自动创建的线程**：同样跳过——没有提及门控意味着没有间隙。

按用户隔离会话（`group_sessions_per_user: true`，默认值）也同样受益：用户的会话缺少其他频道参与者发布的上下文，以及用户自己在 @ 机器人之前的消息。回填会填补这两个间隙。

```yaml
discord:
  history_backfill: true   # 默认
```

若要关闭：

```yaml
discord:
  history_backfill: false
```

> **注意：** 在机器人处理过程中（触发与回复之间）到达的消息不会被捕获。这是一个可接受的简化——用户可以重新发送或再次 @。

<a id="discord-historybackfilllimit"></a>
#### `discord.history_backfill_limit`

**类型：** integer — **默认值：** `50`

恢复频道上下文时向后扫描的最大消息数。实际扫描通常会更早停止——在频道中机器人自己的最后一条消息处，这是轮次之间的自然边界。此限制是针对冷启动和近期历史中没有机器人之前消息的长间隙的安全上限。

```yaml
discord:
  history_backfill: true
  history_backfill_limit: 50
```

<a id="groupsessionsperuser"></a>
#### `group_sessions_per_user`

**类型：** boolean — **默认值：** `true`

这是一个全局网关设置（非 Discord 专属），用于控制同一频道中的用户是否拥有独立的会话历史。

当为 `true` 时：在 `#research` 中聊天的 Alice 和 Bob 各自与 Hermes 有独立的对话。当为 `false` 时：整个频道共享一个对话记录和一个正在运行的 Agent 槽位。

```yaml
group_sessions_per_user: true
```
每种模式的完整含义请参见上方的[会话模型](#session-model-in-discord)一节。

<a id="display-toolprogress"></a>
#### `display.tool_progress`

**类型：** string — **默认值：** `"all"` — **可选值：** `off`, `new`, `all`, `verbose`

控制机器人在处理时是否在聊天中发送进度消息（例如“正在读取文件...”、“正在运行终端命令...”）。这是一个全局网关设置，适用于所有平台。

```yaml
display:
  tool_progress: "all"    # off | new | all | verbose
```

- `off` — 不显示进度消息
- `new` — 仅显示每轮第一个工具调用
- `all` — 显示所有工具调用（网关消息中截断至40个字符）
- `verbose` — 显示完整的工具调用详情（可能产生长消息）

<a id="display-toolprogresscommand"></a>
#### `display.tool_progress_command`

**类型：** boolean — **默认值：** `false`

启用后，会在网关上提供 `/verbose` 斜杠命令，允许你在不修改 config.yaml 的情况下循环切换工具进度显示模式（`off → new → all → verbose → off`）。

```yaml
display:
  tool_progress_command: true
```

<a id="slash-command-access-control"></a>
## 斜杠命令访问控制

默认情况下，每个被允许的用户都可以运行所有斜杠命令。如果你想将允许列表分为**管理员**（拥有所有斜杠命令访问权限）和**普通用户**（仅可运行你明确启用的命令），请在 Discord 平台的 `extra` 块中添加 `allow_admin_from` 和 `user_allowed_commands`：

```yaml
gateway:
  platforms:
    discord:
      extra:
        # 现有用户允许列表（不变）
        allow_from:
          - "123456789012345678"  # 管理员用户 ID
          - "999888777666555444"  # 普通用户 ID

        # 新增 — 管理员拥有所有斜杠命令（内置 + 插件）
        allow_admin_from:
          - "123456789012345678"

        # 新增 — 非管理员用户只能运行这些斜杠命令。
        # /help 和 /whoami 始终允许，以便用户查看自己的权限。
        user_allowed_commands:
          - status
          - model
          - history

        # 可选：为服务器频道设置单独的管理员/命令列表
        group_allow_admin_from:
          - "123456789012345678"
        group_user_allowed_commands:
          - status
```

**行为说明：**

- 某个范围（私聊或服务器频道）中位于 `allow_admin_from` 的用户可以通过实时命令注册表运行**每一个**注册的斜杠命令——包括内置和插件注册的命令。
- 不在 `allow_admin_from` 中的用户只能运行 `user_allowed_commands` 中列出的命令，外加始终允许的基础命令：`/help` 和 `/whoami`。
- 普通聊天（非斜杠消息）不受影响。非管理员用户仍可正常与 agent 对话；只是无法触发任意命令。
- **向后兼容：** 如果某范围没有设置 `allow_admin_from`，则该范围的斜杠命令限制被禁用。现有安装无需改动即可继续工作。
- 私聊中的管理员身份不意味着服务器频道中的管理员身份。每个范围都有自己的管理员列表。

使用 `/whoami` 查看当前活动范围、你的身份层级（admin / user / unrestricted）以及你可以运行的斜杠命令。
<a id="interactive-model-picker"></a>
## 交互式模型选择器

在 Discord 频道中发送不带参数的 `/model` 命令，即可打开一个基于下拉菜单的模型选择器：

1. **提供商选择** — 一个下拉选择框，显示可用的提供商（最多 25 个）。
2. **模型选择** — 第二个下拉框，显示所选提供商下的模型（最多 25 个）。

选择器在 120 秒后超时。只有授权用户（在 `DISCORD_ALLOWED_USERS` 中的用户）才能与之交互。如果你知道模型名称，可以直接输入 `/model <名称>`。

<a id="native-slash-commands-for-skills"></a>
## 技能的原生斜杠命令

Hermes 会自动将已安装的技能注册为 **原生 Discord 应用命令**。这意味着技能会出现在 Discord 的自动补全 `/` 菜单中，与内置命令并列。

- 每个技能都会成为一个 Discord 斜杠命令（例如 `/code-review`、`/ascii-art`）
- 技能接受一个可选的 `args` 字符串参数
- Discord 对每个机器人有 100 个应用命令的限制——如果你的技能数量超过可用槽位，多余的技能会被跳过，并在日志中显示警告
- 技能在机器人启动时与内置命令（如 `/model`、`/reset` 和 `/background`）一起注册

无需额外配置——任何通过 `hermes skills install` 安装的技能都会在下次网关重启时自动注册为 Discord 斜杠命令。

<a id="disabling-slash-command-registration"></a>
### 禁用斜杠命令注册

如果你针对同一个 Discord 应用运行多个 Hermes 网关（例如预发布环境 + 生产环境），则只有一个网关应拥有全局斜杠命令的注册权——否则最后启动的网关会覆盖之前的注册，导致注册信息反复变动。在"从属"网关上关闭斜杠注册：

```yaml
gateway:
  platforms:
    discord:
      extra:
        slash_commands: false   # 默认值: true
```

在"主"网关上保留 `true` 可保持正常行为——内置命令和已安装技能都会出现在全局 `/` 菜单中。

<a id="sending-media-sendmessage-media-tags"></a>
## 发送媒体（`send_message` + `MEDIA:` 标签）

Discord 适配器通过 `send_message` 工具和 Agent 发出的行内 `MEDIA:/path/to/file` 标签，支持对每种常见媒体类型进行原生文件上传：

| 类型 | 发送方式 |
|---|---|
| 图片（PNG/JPG/WebP） | 原生 Discord 图片附件，带行内预览 |
| 动画 GIF | `send_animation` 以上传 `animation.gif` 的方式发送，Discord 会将其作为行内动画播放（而非静态缩略图） |
| 视频（MP4/MOV） | `send_video` — 原生视频播放器 |
| 音频 / 语音 | `send_voice` — 尽可能发送原生语音消息，否则以文件附件形式发送 |
| 文档（PDF/ZIP/docx 等） | `send_document` — 原生附件，带下载按钮 |

Discord 的单次上传大小限制取决于服务器的加速等级（免费用户 25 MB，最高 500 MB）。如果 Hermes 收到 HTTP 413 错误，适配器会回退到指向本地缓存路径的链接，而不是静默失败。

<a id="receiving-arbitrary-file-types"></a>
## 接收任意文件类型

默认情况下，机器人会缓存与内置允许列表匹配的上传文件——包括图片、音频、视频、PDF、文本/markdown/csv/log、JSON/XML/YAML/TOML、zip、docx/xlsx/pptx。其他任何文件（如 `.wav`、`.bin`、自定义扩展名的转储文件）都会被记录为 `不支持的文档类型` 并在 Agent 看到之前丢弃。
要接受任意文件类型，请启用 `discord.allow_any_attachment`：

```yaml
discord:
  allow_any_attachment: true
  # 可选 — 提高/禁用单个文件大小上限。默认值为 32 MiB。
  # 整个文件在缓存期间会保留在内存中，因此无限制上传会带来实际的内存成本。
  max_attachment_bytes: 33554432   # 字节；0 = 无限制
```

启用该标志后，任何上传的文件都会被下载，缓存到 `~/.hermes/cache/documents/`，并以 `application/octet-stream` MIME 类型的 `DOCUMENT` 消息事件呈现给 Agent。Agent 会收到一条上下文注释，指向本地路径（通过 `to_agent_visible_cache_path` 为 Docker/Modal 沙箱终端自动转换），并可以使用 `terminal`（`ffprobe`、`unzip`、`file`、`strings` 等）或 `read_file` 检查文件。文件内容**不会**内联到提示词中——只有路径——因此二进制上传不会撑爆上下文窗口。

已在允许列表中的已知文本格式（`.txt`、`.md`、`.log`）仍会自动注入内容，最多 100 KiB；启用该标志时，此行为保持不变。

等效的环境变量：`DISCORD_ALLOW_ANY_ATTACHMENT=true` 和 `DISCORD_MAX_ATTACHMENT_BYTES=33554432`（或 `0` 表示无限制）。

:::warning 无限制的内存成本
禁用大小上限（`max_attachment_bytes: 0`）意味着用户可以给机器人上传数 GB 的文件，而网关会在缓存到磁盘的同时忠实地通过内存缓冲区处理。仅在受信任的单用户安装中设置此选项。对于共享机器人，请保留默认的 32 MiB 或保守地提高上限。
:::

<a id="memory-cost-of-unlimited"></a>
<a id="interactive-prompts-clarify"></a>
## 交互式提示（澄清）

当 Agent 调用 `clarify` 工具时——例如询问你偏好哪种方法、获取任务后反馈，或在重要决策前确认——Discord 会为每个选项显示**一个按钮**：

> 我应该为仪表盘使用哪个框架？
>
> [1. Next.js] [2. Remix] [3. Astro] [其他 (输入答案)]

点击编号按钮进行回答，或点击**其他**以便输入自由格式的回复（你之后在该频道发送的下一条消息即为答案）。无预设选项的开放式 `clarify` 调用会跳过按钮，直接捕获你的下一条消息。

一旦做出选择，按钮便会禁用，以防止重复点击导致提示被双重解析。通过 `~/.hermes/config.yaml` 中的 `agent.clarify_timeout` 配置响应超时时间（默认 `600` 秒）。如果超时未响应，Agent 会发送一条哨兵消息并继续执行，而不是挂起。

<a id="home-channel"></a>
## 主页频道

你可以指定一个“主页频道”，机器人会在其中发送主动消息（如定时任务输出、提醒和通知）。设置方法有两种：

<a id="using-the-slash-command"></a>
### 使用斜杠命令

在机器人所在任意 Discord 频道中输入 `/sethome`。该频道将成为主页频道。

<a id="manual-configuration"></a>
### 手动配置

将以下内容添加到你的 `~/.hermes/.env`：

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

将 ID 替换为实际的频道 ID（在开发者模式下右键单击 → 复制频道 ID）。
<a id="voice-messages"></a>
## 语音消息

Hermes Agent 支持 Discord 语音消息：

- **收到的语音消息** 会自动使用配置的 STT 服务进行转写：本地 `faster-whisper`（无需密钥）、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）。
- **文字转语音**：使用 `/voice tts` 让机器人在文字回复的同时发送语音回复。
- **Discord 语音频道**：Hermes 还可以加入语音频道，听取用户说话，并在频道中回复。

完整设置和操作指南，请参阅：
- [语音模式](/user-guide/features/voice-mode)
- [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)

<a id="forum-channels"></a>
## 论坛频道

Discord 论坛频道（类型 15）不接受直接消息——论坛中的每个帖子都必须是一个线程。Hermes 会自动检测论坛频道，并在需要发送消息时创建一个新的线程帖子，因此 `send_message`、TTS、图片、语音消息和文件附件都可以正常工作，无需 Agent 进行特殊处理。

- **线程名称** 取自消息的第一行（去除 Markdown 标题前缀，最多 100 个字符）。当消息仅包含附件时，文件名将作为备选线程名称。
- **附件** 会随新线程的起始消息一起发送——无需单独的上传步骤，也不会部分发送。
- **一次调用，一个线程**：每次向论坛发送都会创建一个新线程。因此，连续向同一论坛发送消息会产生不同的线程。
- **检测分为三层**：首先是频道目录缓存，其次是进程本地探测缓存，最后是实时的 `GET /channels/{id}` 探测（其结果会在进程生命周期内被记忆）。

刷新目录（在支持该功能的平台上使用 `/channels refresh`，或重启网关）会将机器人启动后创建的任何论坛频道填充到缓存中。

<a id="troubleshooting"></a>
## 故障排除

<a id="bot-is-online-but-not-responding-to-messages"></a>
### 机器人在线但不响应消息

**原因**：消息内容意图（Message Content Intent）未启用。

**解决方法**：前往 [开发者门户](https://discord.com/developers/applications) → 你的应用 → Bot → 特权网关意图（Privileged Gateway Intents）→ 启用 **Message Content Intent** → 保存更改。重启网关。

<a id="disallowed-intents-error-on-startup"></a>
### 启动时出现 "Disallowed Intents" 错误

**原因**：你的代码请求了开发者门户中未启用的意图。

**解决方法**：在 Bot 设置中启用所有三个特权网关意图（Presence、Server Members、Message Content），然后重启。

<a id="bot-can-t-see-messages-in-a-specific-channel"></a>
### 机器人无法看到特定频道中的消息

**原因**：机器人的角色没有查看该频道的权限。

**解决方法**：在 Discord 中，进入频道的设置 → 权限 → 添加机器人的角色，并启用 **View Channel** 和 **Read Message History**。

<a id="403-forbidden-errors"></a>
### 403 Forbidden 错误

**原因**：机器人缺少必要的权限。

**解决方法**：使用步骤 5 中的 URL 重新邀请机器人并赋予正确权限，或者在服务器设置 → 角色中手动调整机器人的角色权限。

<a id="bot-is-offline"></a>
### 机器人离线

**原因**：Hermes 网关未运行，或令牌不正确。
**修复**：检查 `hermes gateway` 是否正在运行。验证 `.env` 文件中的 `DISCORD_BOT_TOKEN`。如果最近重置了令牌，请更新它。

<a id="user-not-allowed-bot-ignores-you"></a>
### "User not allowed" / Bot 忽略你

**原因**：你的用户 ID 不在 `DISCORD_ALLOWED_USERS` 中。

**修复**：将你的用户 ID 添加到 `~/.hermes/.env` 中的 `DISCORD_ALLOWED_USERS`，然后重启 gateway。

<a id="people-in-the-same-channel-are-sharing-context-unexpectedly"></a>
### 同一频道的人意外共享上下文

**原因**：`group_sessions_per_user` 被禁用，或者平台无法为该上下文中的消息提供用户 ID。

**修复**：在 `~/.hermes/config.yaml` 中设置此项，然后重启 gateway：

```yaml
group_sessions_per_user: true
```

如果你有意想要一个共享房间式的对话，请保持关闭——只是要预期共享的对话历史记录和共享的中断行为。

<a id="security"></a>
## 安全

:::warning
始终设置 `DISCORD_ALLOWED_USERS`（或 `DISCORD_ALLOWED_ROLES`）来限制可以与 bot 交互的人员。如果没有设置两者，gateway 默认会拒绝所有用户，作为一种安全措施。只授权你信任的人——授权用户拥有对 Agent 能力的完全访问权限，包括工具使用和系统访问。
:::

<a id="role-based-access-control"></a>
### 基于角色的访问控制

对于通过角色而非单个用户列表（如版主团队、支持人员、内部工具）管理访问权限的服务器，请使用 `DISCORD_ALLOWED_ROLES`——一个以逗号分隔的角色 ID 列表。拥有其中任何一个角色的成员都会被授权。

```bash
# ~/.hermes/.env — 可与 DISCORD_ALLOWED_USERS 一起使用或替代它
DISCORD_ALLOWED_ROLES=987654321098765432,876543210987654321
```

语义说明：

- **与用户白名单是“或”关系。** 如果用户的 ID 在 `DISCORD_ALLOWED_USERS` 中，**或**用户拥有 `DISCORD_ALLOWED_ROLES` 中的任何一个角色，则该用户被授权。
- **自动启用服务器成员意图。** 当设置了 `DISCORD_ALLOWED_ROLES` 时，bot 在连接时会启用成员意图——Discord 需要此意图才能随成员记录发送角色信息。
- **使用角色 ID，而非名称。** 从 Discord 获取：**用户设置 → 高级 → 打开开发者模式**，然后右键点击任意角色 → **复制角色 ID**。
- **DM 中的回退策略。** 在私信中，角色检查会扫描共同所在的服务器；如果用户在任何一个共享服务器中拥有允许的角色，那么在私信中也会被授权。

当管理团队人员更替频繁时，这是推荐的模式——新版主一旦被授予角色就能立即获得访问权限，无需编辑 `.env` 文件或重启 gateway。

<a id="mention-control"></a>
### 提及控制

默认情况下，Hermes 会阻止 bot 发送 `@everyone`、`@here` 和角色提及的 @消息，即使 bot 的回复中包含这些令牌也是如此。这可以防止措辞不当的提示或回显的用户内容污染整个服务器。单个 `@用户` 提及和回复引用提及（即显示“正在回复……”的小标签）保持启用，以便正常的对话仍能工作。

你可以通过环境变量或 `config.yaml` 来放宽这些默认设置：

```yaml
# ~/.hermes/config.yaml
discord:
  allow_mentions:
    everyone: false      # 允许 bot 发送 @everyone / @here 的 @消息
    roles: false         # 允许 bot 发送 @角色 的 @消息
    users: true          # 允许 bot 发送 @单个用户 的 @消息
    replied_user: true   # 回复消息时 @消息的作者
```
```bash
# ~/.hermes/.env — 环境变量会覆盖 config.yaml 中的设置
DISCORD_ALLOW_MENTION_EVERYONE=false
DISCORD_ALLOW_MENTION_ROLES=false
DISCORD_ALLOW_MENTION_USERS=true
DISCORD_ALLOW_MENTION_REPLIED_USER=true
```

:::tip
除非你确切知道为什么需要，否则请将 `everyone` 和 `roles` 保持为 `false`。LLM 很容易在看似正常的回复中生成 `@everyone` 字符串；如果没有这个保护，就会通知你服务器上的每个成员。
:::

关于如何保护你的 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。
