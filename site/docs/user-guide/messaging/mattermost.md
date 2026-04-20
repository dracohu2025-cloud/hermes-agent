---
sidebar_position: 8
title: "Mattermost"
description: "将 Hermes Agent 设置为 Mattermost 机器人"
---

# Mattermost 设置 {#mattermost-setup}

Hermes Agent 可作为机器人集成到 Mattermost 中，让你能够通过直接消息或团队频道与你的 AI 助手聊天。Mattermost 是一个自托管、开源的 Slack 替代方案——你可以在自己的基础设施上运行它，完全掌控自己的数据。该机器人通过 Mattermost 的 REST API (v4) 和 WebSocket 连接以获取实时事件，通过 Hermes Agent 的处理管道（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图片和斜杠命令。

无需外部 Mattermost 库——适配器使用 `aiohttp`，它已经是 Hermes 的依赖项。

在开始设置之前，以下是大多数人最想了解的部分：Hermes 在你的 Mattermost 实例中运行后的行为方式。

## Hermes 的行为方式 {#how-hermes-behaves}

| 场景 | 行为 |
|---------|----------|
| **直接消息 (DMs)** | Hermes 会响应每一条消息。不需要 `@提及`。每个 DM 都有其独立的会话。 |
| **公开/私密频道** | 当你 `@提及` Hermes 时，它才会响应。没有提及，Hermes 会忽略消息。 |
| **线程** | 如果 `MATTERMOST_REPLY_MODE=thread`，Hermes 会在你的消息下以线程形式回复。线程上下文与父频道保持隔离。 |
| **多用户共享频道** | 默认情况下，Hermes 会在频道内为每个用户隔离会话历史记录。两个人在同一频道中交谈不会共享一个对话记录，除非你明确禁用此功能。 |

:::tip
如果你希望 Hermes 以线程对话的形式回复（嵌套在你的原始消息下），请设置 `MATTERMOST_REPLY_MODE=thread`。默认值为 `off`，即在频道中发送平铺的消息。
:::

### Mattermost 中的会话模型 {#session-model-in-mattermost}

默认情况下：

- 每个 DM 拥有独立的会话
- 每个线程拥有独立的会话命名空间
- 共享频道中的每个用户在该频道内拥有自己的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个频道共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作频道可能有用，但也意味着：

- 用户共享上下文增长和令牌成本
- 一个人冗长且大量使用工具的任务可能会使其他人的上下文膨胀
- 一个人正在运行的任务可能会中断另一个人在同一频道中的后续操作

本指南将引导你完成完整的设置过程——从在 Mattermost 上创建机器人到发送第一条消息。

## 步骤 1：启用机器人账户 {#step-1-enable-bot-accounts}

在创建机器人之前，必须在你的 Mattermost 服务器上启用机器人账户。

1. 以 **系统管理员** 身份登录 Mattermost。
2. 进入 **系统控制台** → **集成** → **机器人账户**。
3. 将 **启用机器人账户创建** 设置为 **true**。
4. 点击 **保存**。

:::info
如果你没有系统管理员权限，请让你的 Mattermost 管理员启用机器人账户并为你创建一个。
:::

## 步骤 2：创建机器人账户 {#step-2-create-a-bot-account}

1. 在 Mattermost 中，点击 **☰** 菜单（左上角）→ **集成** → **机器人账户**。
2. 点击 **添加机器人账户**。
3. 填写详细信息：
   - **用户名**：例如，`hermes`
   - **显示名称**：例如，`Hermes Agent`
   - **描述**：可选
   - **角色**：`成员` 即可
4. 点击 **创建机器人账户**。
5. Mattermost 将显示 **机器人令牌**。**立即复制它。**

:::warning[令牌仅显示一次]
机器人令牌仅在创建机器人账户时显示一次。如果丢失，你需要从机器人账户设置中重新生成。切勿公开分享你的令牌或将其提交到 Git——任何拥有此令牌的人都可以完全控制该机器人。
:::

将令牌安全地存储在某处（例如密码管理器）。你将在步骤 5 中需要它。

:::tip
你也可以使用 **个人访问令牌** 代替机器人账户。进入 **个人资料** → **安全** → **个人访问令牌** → **创建令牌**。如果你希望 Hermes 以你自己的用户身份发帖，而不是作为一个独立的机器人用户，这会很有用。
:::

## 步骤 3：将机器人添加到频道 {#step-3-add-the-bot-to-channels}
机器人需要成为你希望它响应的任何频道的成员：

1.  打开你希望机器人加入的频道。
2.  点击频道名称 → **添加成员**。
3.  搜索你的机器人用户名（例如，`hermes`）并添加它。

对于私信，只需与机器人开启一个直接消息会话 —— 它将能够立即响应。

## 步骤 4：查找你的 Mattermost 用户 ID {#step-4-find-your-mattermost-user-id}

Hermes Agent 使用你的 Mattermost 用户 ID 来控制谁可以与机器人交互。查找方法如下：

1.  点击你的**头像**（左上角）→ **个人资料**。
2.  你的用户 ID 会显示在个人资料对话框中 —— 点击它进行复制。

你的用户 ID 是一个 26 位的字母数字字符串，例如 `3uo8dkh1p7g1mfk49ear5fzs5c`。

:::warning
你的用户 ID **不是**你的用户名。用户名是 `@` 后面的内容（例如，`@alice`）。用户 ID 是 Mattermost 内部使用的长字母数字标识符。
:::

**替代方法**：你也可以通过 API 获取你的用户 ID：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-mattermost-server/api/v4/users/me | jq .id
```

:::tip
要获取**频道 ID**：点击频道名称 → **查看信息**。频道 ID 会显示在信息面板中。如果你想手动设置一个主频道，会需要这个 ID。
:::

## 步骤 5：配置 Hermes Agent {#step-5-configure-hermes-agent}

### 选项 A：交互式设置（推荐） {#option-a-interactive-setup-recommended}

运行引导式设置命令：

```bash
hermes gateway setup
```

提示时选择 **Mattermost**，然后按要求粘贴你的服务器 URL、机器人令牌和用户 ID。

### 选项 B：手动配置 {#option-b-manual-configuration}

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
MATTERMOST_URL=https://mm.example.com
MATTERMOST_TOKEN=***
MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c

# 多个允许的用户（逗号分隔）
# MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c,8fk2jd9s0a7bncm1xqw4tp6r3e

# 可选：回复模式（thread 或 off，默认：off）
# MATTERMOST_REPLY_MODE=thread

# 可选：无需 @提及即可响应（默认：true = 需要提及）
# MATTERMOST_REQUIRE_MENTION=false

# 可选：机器人无需 @提及即可响应的频道（逗号分隔的频道 ID）
# MATTERMOST_FREE_RESPONSE_CHANNELS=channel_id_1,channel_id_2
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 在共享频道和线程中保持每个参与者的上下文隔离。

### 启动网关 {#start-the-gateway}

配置完成后，启动 Mattermost 网关：

```bash
hermes gateway
```

机器人应在几秒钟内连接到你的 Mattermost 服务器。发送一条消息给它 —— 可以是私信，也可以是在它已加入的频道中 —— 进行测试。

:::tip
你可以将 `hermes gateway` 在后台运行或作为 systemd 服务运行以实现持久化操作。详情请参阅部署文档。
:::

## 主频道 {#home-channel}

你可以指定一个“主频道”，机器人会向该频道发送主动消息（例如定时任务输出、提醒和通知）。有两种设置方法：

### 使用斜杠命令 {#using-the-slash-command}

在机器人所在的任何 Mattermost 频道中输入 `/sethome`。该频道将成为主频道。

### 手动配置 {#manual-configuration}

将此添加到你的 `~/.hermes/.env`：

```bash
MATTERMOST_HOME_CHANNEL=abc123def456ghi789jkl012mn
```

将 ID 替换为实际的频道 ID（点击频道名称 → 查看信息 → 复制 ID）。

## 回复模式 {#reply-mode}

`MATTERMOST_REPLY_MODE` 设置控制 Hermes 发布回复的方式：

| 模式 | 行为 |
|------|----------|
| `off` (默认) | Hermes 在频道中发布普通消息，就像普通用户一样。 |
| `thread` | Hermes 在你的原始消息下以线程形式回复。在有很多来回对话时保持频道整洁。 |

在你的 `~/.hermes/.env` 中设置：

```bash
MATTERMOST_REPLY_MODE=thread
```

## 提及行为 {#mention-behavior}

默认情况下，机器人仅在频道中被 `@提及` 时才会响应。你可以更改此行为：

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `MATTERMOST_REQUIRE_MENTION` | `true` | 设置为 `false` 以响应频道中的所有消息（私信始终有效）。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | _(无)_ | 逗号分隔的频道 ID 列表，即使 require_mention 为 true，机器人在这些频道中也可以无需 `@提及` 就响应。 |
在 Mattermost 中查找频道 ID：打开频道，点击频道名称标题，在 URL 或频道详情中查找 ID。

当机器人被 `@提及` 时，在处理消息前，提及会自动从消息中剥离。

## 故障排除 {#troubleshooting}

### 机器人不响应消息 {#bot-is-not-responding-to-messages}

**原因**：机器人不是频道成员，或者 `MATTERMOST_ALLOWED_USERS` 不包含您的用户 ID。

**解决方法**：将机器人添加到频道（频道名称 → 添加成员 → 搜索机器人）。确认您的用户 ID 在 `MATTERMOST_ALLOWED_USERS` 中。重启网关。

### 403 禁止错误 {#403-forbidden-errors}

**原因**：机器人令牌无效，或者机器人没有在频道中发帖的权限。

**解决方法**：检查 `.env` 文件中的 `MATTERMOST_TOKEN` 是否正确。确保机器人账户未被停用。确认机器人已被添加到频道。如果使用个人访问令牌，请确保您的账户具有所需权限。

### WebSocket 断开连接 / 重连循环 {#websocket-disconnects-reconnection-loops}

**原因**：网络不稳定、Mattermost 服务器重启，或者防火墙/代理对 WebSocket 连接造成问题。

**解决方法**：适配器会自动使用指数退避策略重连（2秒 → 60秒）。检查服务器的 WebSocket 配置 —— 反向代理（nginx、Apache）需要配置 WebSocket 升级头。确认没有防火墙在 Mattermost 服务器上阻止 WebSocket 连接。

对于 nginx，请确保配置中包含：

```nginx
location /api/v4/websocket {
    proxy_pass http://mattermost-backend;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 600s;
}
```

### 启动时出现“身份验证失败” {#failed-to-authenticate-on-startup}

**原因**：令牌或服务器 URL 不正确。

**解决方法**：验证 `MATTERMOST_URL` 指向您的 Mattermost 服务器（包含 `https://`，末尾没有斜杠）。检查 `MATTERMOST_TOKEN` 是否有效 —— 尝试用 curl 测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/api/v4/users/me
```

如果返回您的机器人用户信息，则令牌有效。如果返回错误，请重新生成令牌。

### 机器人离线 {#bot-is-offline}

**原因**：Hermes 网关未运行，或者连接失败。

**解决方法**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误信息。常见问题：URL 错误、令牌过期、Mattermost 服务器无法访问。

### “用户不允许” / 机器人忽略您 {#user-not-allowed-bot-ignores-you}

**原因**：您的用户 ID 不在 `MATTERMOST_ALLOWED_USERS` 中。

**解决方法**：将您的用户 ID 添加到 `~/.hermes/.env` 中的 `MATTERMOST_ALLOWED_USERS` 并重启网关。记住：用户 ID 是一个 26 位的字母数字字符串，不是您的 `@用户名`。

## 按频道提示 {#per-channel-prompts}

为特定的 Mattermost 频道分配临时的系统提示。该提示在每次对话轮次运行时注入 —— 永远不会持久化到对话历史中 —— 因此更改会立即生效。

```yaml
mattermost:
  channel_prompts:
    "channel_id_abc123": |
      你是一个研究助手。专注于学术来源、引用和简洁的综述。
    "channel_id_def456": |
      代码审查模式。请精确关注边界情况和性能影响。
```

键是 Mattermost 频道 ID（在频道 URL 或通过 API 查找）。匹配频道中的所有消息都会获得该提示作为临时的系统指令注入。

## 安全 {#security}

:::warning
始终设置 `MATTERMOST_ALLOWED_USERS` 以限制谁可以与机器人交互。如果没有设置，网关默认会拒绝所有用户作为安全措施。只添加您信任的人员的用户 ID —— 授权用户可以完全访问 Agent 的能力，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 说明 {#notes}

- **自托管友好**：适用于任何自托管的 Mattermost 实例。无需 Mattermost Cloud 账户或订阅。
- **无需额外依赖**：适配器使用 `aiohttp` 处理 HTTP 和 WebSocket，Hermes Agent 已包含此库。
- **兼容团队版**：适用于 Mattermost 团队版（免费）和企业版。
