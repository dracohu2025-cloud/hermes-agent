---
sidebar_position: 3
title: "Discord"
description: "将 Hermes Agent 设置为 Discord 机器人"
---

# Discord 设置

Hermes Agent 可以作为机器人集成到 Discord 中，让你通过私信或服务器频道与你的 AI 助手聊天。机器人接收你的消息，通过 Hermes Agent 的处理流程（包括工具使用、记忆和推理）进行处理，并实时回复。它支持文本、语音消息、文件附件和斜杠命令。

在开始设置之前，这里先介绍一下大多数人最想知道的部分：Hermes 加入你的服务器后会如何表现。

## Hermes 的行为表现

| 场景 | 行为 |
|---------|----------|
| **私信** | Hermes 会回复每一条消息。不需要 `@提及`。每条私信都有独立的会话。 |
| **服务器频道** | 默认情况下，Hermes 只在你 `@提及` 它时才会回复。如果你在频道中发消息但没有提及它，Hermes 会忽略该消息。 |
| **自由回复频道** | 你可以通过 `DISCORD_FREE_RESPONSE_CHANNELS` 将特定频道设为免提及，或者通过 `DISCORD_REQUIRE_MENTION=false` 全局禁用提及要求。 |
| **帖子/讨论串** | Hermes 会在同一个讨论串内回复。提及规则仍然适用，除非该讨论串或其父频道被配置为自由回复频道。讨论串的会话历史与父频道是隔离的。 |
| **多用户共享的频道** | 默认情况下，为了安全和清晰，Hermes 会在频道内为每个用户隔离会话历史。两个人在同一个频道中交谈，除非你明确禁用此功能，否则不会共享一个对话记录。 |
| **提及其他用户的消息** | 当 `DISCORD_IGNORE_NO_MENTION` 为 `true`（默认值）时，如果一条消息 @提及了其他用户但**没有**提及机器人，Hermes 会保持沉默。这可以防止机器人跳入针对其他人的对话。如果你希望机器人响应所有消息，无论提及了谁，请将其设置为 `false`。此设置仅适用于服务器频道，不适用于私信。 |

:::tip
如果你想要一个普通的机器人帮助频道，让人们无需每次都标记就能与 Hermes 交谈，请将该频道添加到 `DISCORD_FREE_RESPONSE_CHANNELS` 中。
:::

### Discord 网关模型

Discord 上的 Hermes 不是一个无状态回复的 Webhook。它通过完整的消息网关运行，这意味着每条传入消息都会经过：

1.  授权 (`DISCORD_ALLOWED_USERS`)
2.  提及 / 自由回复检查
3.  会话查找
4.  会话记录加载
5.  正常的 Hermes Agent 执行，包括工具、记忆和斜杠命令
6.  将响应发送回 Discord

这一点很重要，因为在繁忙服务器中的行为取决于 Discord 的路由和 Hermes 的会话策略。

### Discord 中的会话模型

默认情况下：

-   每条私信都有自己的会话
-   每个服务器讨论串都有自己的会话命名空间
-   共享频道中的每个用户在该频道内都有自己的会话

因此，如果 Alice 和 Bob 都在 `#research` 频道中与 Hermes 交谈，即使他们使用的是同一个可见的 Discord 频道，Hermes 默认也会将其视为独立的对话。

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个房间共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间可能有用，但也意味着：

-   用户共享上下文增长和令牌成本
-   一个人冗长且大量使用工具的任务可能会使其他人的上下文膨胀
-   一个人正在运行的任务可能会中断另一个人在同一房间内的后续操作

### 中断与并发

Hermes 通过会话键来跟踪正在运行的 Agent。

使用默认的 `group_sessions_per_user: true`：

-   Alice 中断她自己正在运行的请求只会影响她在该频道中的会话
-   Bob 可以在同一频道中继续交谈，而不会继承 Alice 的历史记录或中断 Alice 的运行

使用 `group_sessions_per_user: false`：

-   整个房间共享该频道/讨论串的一个运行中 Agent 槽位
-   来自不同用户的后续消息可能会相互中断或排队

本指南将引导你完成完整的设置过程——从在 Discord 开发者门户创建机器人到发送第一条消息。

## 步骤 1：创建 Discord 应用

1.  前往 [Discord 开发者门户](https://discord.com/developers/applications)，使用你的 Discord 账户登录。
2.  点击右上角的 **New Application**。
3.  为你的应用输入一个名称（例如，“Hermes Agent”）并接受开发者服务条款。
4.  点击 **Create**。

你将进入 **General Information** 页面。记下 **Application ID** —— 稍后构建邀请链接时会用到它。

## 步骤 2：创建机器人

1.  在左侧边栏中，点击 **Bot**。
2.  Discord 会自动为你的应用创建一个机器人用户。你会看到机器人的用户名，你可以自定义它。
3.  在 **Authorization Flow** 下：
    -   将 **Public Bot** 设置为 **ON** —— 这是使用 Discord 提供的邀请链接（推荐）所必需的。这允许 Installation 选项卡生成默认的授权 URL。
    -   将 **Require OAuth2 Code Grant** 保持为 **OFF**。

:::tip
你可以在此页面为你的机器人设置自定义头像和横幅。这将是用户在 Discord 中看到的样子。
:::

:::info[私有机器人替代方案]
如果你希望保持机器人私有（Public Bot = OFF），你**必须**在步骤 5 中使用 **Manual URL** 方法，而不是 Installation 选项卡。Discord 提供的链接要求启用 Public Bot。
:::

## 步骤 3：启用特权网关意图

这是整个设置中最关键的一步。如果没有启用正确的意图，你的机器人将连接到 Discord，但**无法读取消息内容**。

在 **Bot** 页面，向下滚动到 **Privileged Gateway Intents**。你会看到三个开关：

| 意图 | 用途 | 是否必需？ |
|--------|---------|-----------|
| **Presence Intent** | 查看用户在线/离线状态 | 可选 |
| **Server Members Intent** | 访问成员列表，解析用户名 | **必需** |
| **Message Content Intent** | 读取消息的文本内容 | **必需** |

通过将开关切换到 **ON** 来**同时启用 Server Members Intent 和 Message Content Intent**。

-   没有 **Message Content Intent**，你的机器人会收到消息事件，但消息文本是空的——机器人根本看不到你输入的内容。
-   没有 **Server Members Intent**，机器人无法为允许的用户列表解析用户名，并且可能无法识别是谁在给它发消息。

:::warning[这是 Discord 机器人不工作的首要原因]
如果你的机器人已在线但从不回复消息，**Message Content Intent** 几乎肯定是禁用的。返回 [开发者门户](https://discord.com/developers/applications)，选择你的应用 → Bot → Privileged Gateway Intents，确保 **Message Content Intent** 开关已打开。点击 **Save Changes**。
:::

**关于服务器数量：**
-   如果你的机器人在**少于 100 个服务器**中，你可以自由地开关意图。
-   如果你的机器人在**100 个或更多服务器**中，Discord 要求你提交验证申请才能使用特权意图。对于个人使用，这通常不是问题。

点击页面底部的 **Save Changes**。

## 步骤 4：获取机器人令牌

机器人令牌是 Hermes Agent 用来以你的机器人身份登录的凭证。仍在 **Bot** 页面：

1.  在 **Token** 部分下，点击 **Reset Token**。
2.  如果你的 Discord 账户启用了双重身份验证，请输入你的 2FA 代码。
3.  Discord 将显示你的新令牌。**立即复制它。**

:::warning[令牌仅显示一次]
令牌只显示一次。如果你丢失了它，需要重置并生成一个新的。切勿公开分享你的令牌或将其提交到 Git —— 任何拥有此令牌的人都可以完全控制你的机器人。
:::

将令牌安全地存储在某处（例如密码管理器）。你将在步骤 8 中用到它。

## 步骤 5：生成邀请 URL

你需要一个 OAuth2 URL 来邀请机器人加入你的服务器。有两种方法可以做到这一点：

### 选项 A：使用 Installation 选项卡（推荐）

:::note[需要公共机器人]
此方法要求**在步骤 2 中将 Public Bot 设置为 ON**。如果你将 Public Bot 设置为 OFF，请改用下面的手动 URL 方法。
:::
1. 在左侧边栏，点击 **Installation**。
2. 在 **Installation Contexts** 下，启用 **Guild Install**。
3. 对于 **Install Link**，选择 **Discord Provided Link**。
4. 在 **Default Install Settings** 下的 Guild Install 部分：
   - **Scopes**：选择 `bot` 和 `applications.commands`
   - **Permissions**：选择下面列出的权限。

### 选项 B：手动构造 URL

你可以直接使用以下格式构造邀请链接：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

将 `YOUR_APP_ID` 替换为第 1 步中的 Application ID。

### 所需权限

这是你的机器人所需的最低权限：

- **查看频道** — 查看它有权限访问的频道
- **发送消息** — 回复你的消息
- **嵌入链接** — 格式化富文本回复
- **附加文件** — 发送图片、音频和文件输出
- **读取消息历史** — 维持对话上下文

### 推荐的额外权限

- **在线程中发送消息** — 在线程对话中回复
- **添加反应** — 对消息做出反应以示确认

### 权限整数值

| 级别 | 权限整数值 | 包含内容 |
|-------|-------------------|-----------------|
| 最低 | `117760` | 查看频道、发送消息、读取消息历史、附加文件 |
| 推荐 | `274878286912` | 以上所有权限，外加嵌入链接、在线程中发送消息、添加反应 |

## 第 6 步：邀请到你的服务器

1. 在浏览器中打开邀请链接（来自 Installation 标签页或你手动构造的 URL）。
2. 在 **Add to Server** 下拉菜单中，选择你的服务器。
3. 点击 **Continue**，然后点击 **Authorize**。
4. 如果提示，请完成验证码。

:::info
你需要拥有 Discord 服务器的 **管理服务器** 权限才能邀请机器人。如果在下拉菜单中看不到你的服务器，请让服务器管理员使用邀请链接。
:::

授权后，机器人将出现在你服务器的成员列表中（在启动 Hermes 网关之前，它会显示为离线状态）。

## 第 7 步：找到你的 Discord 用户 ID

Hermes Agent 使用你的 Discord 用户 ID 来控制谁可以与机器人交互。查找方法如下：

1. 打开 Discord（桌面版或网页版）。
2. 进入 **设置** → **高级** → 将 **开发者模式** 切换为 **开启**。
3. 关闭设置。
4. 右键点击你自己的用户名（在消息、成员列表或你的个人资料中）→ **复制用户 ID**。

你的用户 ID 是一个长数字，例如 `284102345871466496`。

:::tip
开发者模式也允许你以同样的方式复制 **频道 ID** 和 **服务器 ID** — 右键点击频道或服务器名称，然后选择“复制 ID”。如果你想手动设置主频道，将需要频道 ID。
:::

## 第 8 步：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

提示时选择 **Discord**，然后在被询问时粘贴你的机器人令牌和用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=284102345871466496

# 多个允许的用户（逗号分隔）
# DISCORD_ALLOWED_USERS=284102345871466496,198765432109876543

# 可选：无需 @提及即可回复（默认：true = 需要提及）
# DISCORD_REQUIRE_MENTION=false

# 可选：机器人无需 @提及即可回复的频道（逗号分隔的频道 ID）
# DISCORD_FREE_RESPONSE_CHANNELS=1234567890,9876543210

# 可选：忽略 @提及了其他用户但未提及机器人的消息（默认：true）
# DISCORD_IGNORE_NO_MENTION=true
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
discord:
  require_mention: true

group_sessions_per_user: true
```

- `discord.require_mention: true` 使 Hermes 在正常的服务器流量中保持静默，除非被提及
- `group_sessions_per_user: true` 在共享频道和线程中隔离每个参与者的上下文

### 启动网关

配置完成后，启动 Discord 网关：

```bash
hermes gateway
```

机器人应在几秒内在 Discord 中上线。发送一条消息给它（可以是私信，也可以是它能看到的频道）进行测试。

:::tip
你可以将 `hermes gateway` 在后台运行或作为 systemd 服务运行以实现持久化操作。详情请参阅部署文档。
:::

## 主频道

你可以指定一个“主频道”，机器人会在此发送主动消息（例如定时任务输出、提醒和通知）。有两种设置方法：

### 使用斜杠命令

在机器人所在的任何 Discord 频道中输入 `/sethome`。该频道将成为主频道。

### 手动配置

将这些添加到你的 `~/.hermes/.env` 中：

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

将 ID 替换为实际的频道 ID（右键点击 → 在开发者模式开启时复制频道 ID）。

## 语音消息

Hermes Agent 支持 Discord 语音消息：

- **传入的语音消息** 会自动使用配置的 STT 提供商进行转录：本地 `faster-whisper`（无需密钥）、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）。
- **文本转语音**：使用 `/voice tts` 让机器人在发送文本回复的同时发送语音音频回复。
- **Discord 语音频道**：Hermes 也可以加入语音频道，听取用户说话，并在频道中回复。

完整的设置和操作指南，请参阅：
- [语音模式](/user-guide/features/voice-mode)
- [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)

## 故障排除

### 机器人已上线但不回复消息

**原因**：消息内容意图被禁用。

**解决方法**：前往 [开发者门户](https://discord.com/developers/applications) → 你的应用 → Bot → Privileged Gateway Intents → 启用 **Message Content Intent** → 保存更改。重启网关。

### 启动时出现“Disallowed Intents”错误

**原因**：你的代码请求了在开发者门户中未启用的意图。

**解决方法**：在 Bot 设置中启用所有三个 Privileged Gateway Intents（Presence、Server Members、Message Content），然后重启。

### 机器人在特定频道中看不到消息

**原因**：机器人的角色没有查看该频道的权限。

**解决方法**：在 Discord 中，进入该频道的设置 → 权限 → 添加机器人的角色，并启用 **查看频道** 和 **读取消息历史**。

### 403 禁止错误

**原因**：机器人缺少所需权限。

**解决方法**：使用第 5 步中的 URL 重新邀请机器人并授予正确的权限，或者在服务器设置 → 角色中手动调整机器人的角色权限。

### 机器人离线

**原因**：Hermes 网关未运行，或者令牌不正确。

**解决方法**：检查 `hermes gateway` 是否正在运行。验证 `.env` 文件中的 `DISCORD_BOT_TOKEN`。如果最近重置了令牌，请更新它。

### “用户不被允许” / 机器人忽略你

**原因**：你的用户 ID 不在 `DISCORD_ALLOWED_USERS` 中。

**解决方法**：将你的用户 ID 添加到 `~/.hermes/.env` 中的 `DISCORD_ALLOWED_USERS`，然后重启网关。

### 同一频道中的人意外地共享了上下文

**原因**：`group_sessions_per_user` 被禁用，或者平台无法为该上下文中的消息提供用户 ID。

**解决方法**：在 `~/.hermes/config.yaml` 中设置此项并重启网关：

```yaml
group_sessions_per_user: true
```

如果你有意想要一个共享房间的对话，请保持关闭 — 只需预期会共享转录历史和共享中断行为。

## 安全

:::warning
务必设置 `DISCORD_ALLOWED_USERS` 以限制可以与机器人交互的人员。如果不设置，作为安全措施，网关默认会拒绝所有用户。只添加你信任的人员的用户 ID — 授权用户可以完全访问 Agent 的能力，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅 [安全指南](../security.md)。
