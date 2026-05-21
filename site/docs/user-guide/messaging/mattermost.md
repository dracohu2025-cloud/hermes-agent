---
sidebar_position: 8
title: "Mattermost"
description: "将 Hermes Agent 设置为 Mattermost 机器人"
---

<a id="mattermost-setup"></a>
# Mattermost 设置

Hermes Agent 以机器人的形式与 Mattermost 集成，让您可以通过私信或团队频道与 AI 助手聊天。Mattermost 是一个自托管的开源 Slack 替代方案——您可以将其部署在自己的基础设施上，完全掌控数据。该机器人通过 Mattermost 的 REST API（v4）和 WebSocket 连接以获取实时事件，通过 Hermes Agent 管道（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图片和斜杠命令。

不需要额外的 Mattermost 库——适配器使用了 `aiohttp`，它已经是 Hermes 的依赖项。

在开始设置之前，这里是大多数人最想了解的部分：Hermes 在您的 Mattermost 实例中的行为表现。

<a id="how-hermes-behaves"></a>
## Hermes 的行为方式

| 上下文 | 行为 |
|---------|------|
| **私信** | Hermes 会响应每一条消息。不需要 `@提及`。每条私信拥有独立的会话。 |
| **公开/私有频道** | 当您 `@提及` 时，Hermes 才会响应。没有提及，Hermes 会忽略消息。 |
| **线程** | 如果设置了 `MATTERMOST_REPLY_MODE=thread`，Hermes 会在您的消息下以线程形式回复。线程上下文与父频道隔离。 |
| **多用户共享频道** | 默认情况下，Hermes 会为频道内的每个用户隔离会话历史。两个人在同一频道中对话不会共享同一份转录，除非您明确禁用此功能。 |

:::tip
如果您希望 Hermes 以线程对话（嵌套在原消息下）的方式回复，请设置 `MATTERMOST_REPLY_MODE=thread`。默认值为 `off`，此时会在频道中发送平铺消息。
:::

<a id="session-model-in-mattermost"></a>
### Mattermost 中的会话模型

默认情况下：

- 每条私信拥有自己的会话
- 每个线程拥有自己的会话命名空间
- 共享频道中的每个用户在该频道内拥有自己的会话

此行为由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当您明确希望整个频道共享同一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作频道可能有用，但同时也意味着：

- 用户之间共享上下文增长和 token 成本
- 某个人执行长时间大量工具任务可能会膨胀其他人的上下文
- 某个人正在进行的执行可能会打断同频道内另一个人的后续操作

本指南将引导您完成完整的设置过程——从在 Mattermost 上创建机器人到发送第一条消息。

<a id="step-1-enable-bot-accounts"></a>
## 步骤 1：启用机器人账户

在创建机器人账户之前，必须在您的 Mattermost 服务器上启用该功能。

1. 以**系统管理员**身份登录 Mattermost。
2. 转到**系统控制台** → **集成** → **机器人账户**。
3. 将**启用机器人账户创建**设置为 **true**。
4. 点击**保存**。

:::info
如果您没有系统管理员权限，请让您的 Mattermost 管理员启用机器人账户，并为您创建一个。
:::

<a id="step-2-create-a-bot-account"></a>
## 步骤 2：创建机器人账户

1. 在 Mattermost 中，点击 **☰** 菜单（左上角）→ **集成** → **机器人账户**。
2. 点击**添加机器人账户**。
3. 填写详细信息：
   - **用户名**：例如 `hermes`
   - **显示名称**：例如 `Hermes Agent`
   - **描述**：可选
   - **角色**：`Member` 足够
4. 点击**创建机器人账户**。
5. Mattermost 会显示**机器人令牌**。**请立即复制它。**
:::warning[仅一次性显示令牌]
机器人令牌仅在创建机器人账户时显示一次。如果丢失，需要在机器人账户设置中重新生成。切勿公开分享令牌或将其提交到 Git——任何拥有该令牌的人都能完全控制机器人。
:::

将令牌保存在安全的位置（例如密码管理器）。你在第 5 步中会用到它。

:::tip
你也可以使用**个人访问令牌**来代替机器人账户。前往**个人资料** → **安全** → **个人访问令牌** → **创建令牌**。如果你想以个人用户身份而非独立机器人用户发布消息，这会很有用。
:::

<a id="step-3-add-the-bot-to-channels"></a>
## 第 3 步：将机器人添加到频道

机器人需要是你希望它响应的每个频道的成员：

1. 打开你想添加机器人的频道。
2. 点击频道名称 → **添加成员**。
3. 搜索你的机器人用户名（例如 `hermes`）并添加。

对于私信，直接与机器人打开私聊即可——它将能够立即响应。

<a id="step-4-find-your-mattermost-user-id"></a>
## 第 4 步：找到你的 Mattermost 用户 ID

Hermes Agent 使用你的 Mattermost 用户 ID 来控制可以与机器人交互的对象。要找到它：

1. 点击你的**头像**（左上角） → **个人资料**。
2. 你的用户 ID 会显示在个人资料对话框中——点击即可复制。

你的用户 ID 是一个 26 位字母数字字符串，例如 `3uo8dkh1p7g1mfk49ear5fzs5c`。

:::warning
你的用户 ID **不是** 你的用户名。用户名是 `@` 后面的内容（例如 `@alice`）。用户 ID 是 Mattermost 内部使用的一长串字母数字标识符。
:::

**替代方法**：你也可以通过 API 获取用户 ID：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-mattermost-server/api/v4/users/me | jq .id
```

:::tip
要获取**频道 ID**：点击频道名称 → **查看信息**。频道 ID 会显示在信息面板中。如果你想手动设置主频道，就需要用到它。
:::

<a id="step-5-configure-hermes-agent"></a>
## 第 5 步：配置 Hermes Agent

<a id="option-a-interactive-setup-recommended"></a>
### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

按提示选择 **Mattermost**，然后粘贴你的服务器 URL、机器人令牌和用户 ID。

<a id="option-b-manual-configuration"></a>
### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
MATTERMOST_URL=https://mm.example.com
MATTERMOST_TOKEN=***
MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c

# 允许多个用户（逗号分隔）
# MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c,8fk2jd9s0a7bncm1xqw4tp6r3e

# 可选：回复模式（thread 或 off，默认 off）
# MATTERMOST_REPLY_MODE=thread

# 可选：不需要 @提及 即可响应（默认 true，即需要提及）
# MATTERMOST_REQUIRE_MENTION=false

# 可选：不需要 @提及 即可响应的频道（逗号分隔的频道 ID）
# MATTERMOST_FREE_RESPONSE_CHANNELS=channel_id_1,channel_id_2
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 会在共享频道和线程中隔离每个参与者的上下文。
<a id="start-the-gateway"></a>
### 启动网关

配置完成后，启动 Mattermost 网关：

```bash
hermes gateway
```

机器人应在几秒钟内连接到你的 Mattermost 服务器。发送一条消息（可以是私信或机器人已加入的频道消息）进行测试。

:::tip
你可以让 `hermes gateway` 在后台运行，或将其配置为 systemd 服务以实现持久运行。详情请参见部署文档。
:::

<a id="home-channel"></a>
## 主页频道

你可以指定一个“主页频道”，机器人会在此频道发送主动消息（例如 cron 任务输出、提醒和通知）。设置方式有两种：

<a id="using-the-slash-command"></a>
### 使用斜杠命令

在机器人所在的任意 Mattermost 频道中输入 `/sethome`，该频道即成为主页频道。

<a id="manual-configuration"></a>
### 手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
MATTERMOST_HOME_CHANNEL=abc123def456ghi789jkl012mn
```

将 ID 替换为实际的频道 ID（点击频道名称 → 查看信息 → 复制 ID）。

<a id="reply-mode"></a>
## 回复模式

`MATTERMOST_REPLY_MODE` 设置控制 Hermes 如何发布回复：

| 模式 | 行为 |
|------|----------|
| `off`（默认） | Hermes 在频道中直接发送扁平消息，如同普通用户。 |
| `thread` | Hermes 在你的原始消息下以线程形式回复。当来回对话较多时，可保持频道整洁。 |

在 `~/.hermes/.env` 中设置：

```bash
MATTERMOST_REPLY_MODE=thread
```

<a id="mention-behavior"></a>
## @提及行为

默认情况下，机器人仅在频道中被 `@提及` 时才会回复。你可以修改此行为：

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `MATTERMOST_REQUIRE_MENTION` | `true` | 设为 `false` 则回复频道中的所有消息（私信始终有效）。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | （无） | 以逗号分隔的频道 ID 列表，在此列表中的频道里，即使 `require_mention` 为 `true`，机器人也会在没有 `@提及` 时回复。 |

在 Mattermost 中查找频道 ID：打开频道，点击频道名称标题，在 URL 或频道详情中查找 ID。

当机器人被 `@提及` 时，处理消息前会自动去除提及内容。

<a id="channel-allowlist-allowedchannels"></a>
## 频道白名单（`allowed_channels`）

将机器人限制在一组固定的 Mattermost 频道中。设置后，机器人**仅**回复其 ID 出现在列表中的频道消息——来自其他任何频道的消息都会被静默忽略，即使机器人被 `@提及` 也不例外。

**私信不受此过滤器限制**，因此授权用户始终可以通过私信联系到机器人。

```yaml
mattermost:
  allowed_channels:
    - "abc123def456ghi789jkl012mno"   # #ops
    - "xyz987uvw654rst321opq098nml"   # #incident-response
```

或通过环境变量（以逗号分隔）：

```bash
MATTERMOST_ALLOWED_CHANNELS="abc123def456ghi789jkl012mno,xyz987uvw654rst321opq098nml"
```

行为说明：

- 为空 / 未设置 → 无限制（完全向后兼容）。
- 非空 → 频道 ID 必须在列表中，否则消息会在任何其他门控（如提及要求、`MATTERMOST_FREE_RESPONSE_CHANNELS` 等）执行之前被丢弃。
- 通过 Mattermost UI → 频道头部 → “查看信息”查找频道 ID，或从频道 URL 中读取。
参见：[管理员/用户斜杠命令拆分](../../reference/slash-commands.md#permissions-and-adminuser-split)。

<a id="troubleshooting"></a>
## 故障排除

<a id="bot-is-not-responding-to-messages"></a>
### Bot 不响应消息

**原因**：Bot 不是该频道的成员，或者 `MATTERMOST_ALLOWED_USERS` 中没有包含你的用户 ID。

**修复**：将 Bot 添加到频道（频道名称 → 添加成员 → 搜索 Bot）。确认你的用户 ID 在 `MATTERMOST_ALLOWED_USERS` 中。重启网关。

<a id="403-forbidden-errors"></a>
### 403 禁止访问错误

**原因**：Bot 令牌无效，或者 Bot 没有在该频道发帖的权限。

**修复**：检查 `.env` 文件中的 `MATTERMOST_TOKEN` 是否正确。确保 Bot 账户未被停用。确认 Bot 已被添加到频道。如果使用个人访问令牌，请确保你的账户拥有所需权限。

<a id="websocket-disconnects-reconnection-loops"></a>
### WebSocket 断开 / 重连循环

**原因**：网络不稳定、Mattermost 服务器重启，或 WebSocket 连接的防火墙/代理问题。

**修复**：适配器会自动以指数退避（2 秒 → 60 秒）重新连接。检查服务器的 WebSocket 配置——反向代理（nginx、Apache）需要配置 WebSocket 升级头。确认没有防火墙阻止与 Mattermost 服务器的 WebSocket 连接。

对于 nginx，请确保配置包含以下内容：

```nginx
location /api/v4/websocket {
    proxy_pass http://mattermost-backend;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 600s;
}
```

<a id="failed-to-authenticate-on-startup"></a>
### 启动时出现“身份验证失败”

**原因**：令牌或服务器 URL 不正确。

**修复**：确认 `MATTERMOST_URL` 指向你的 Mattermost 服务器（包含 `https://`，末尾无斜杠）。检查 `MATTERMOST_TOKEN` 是否有效——尝试使用 curl：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/api/v4/users/me
```

如果返回你的 Bot 用户信息，则令牌有效。如果返回错误，请重新生成令牌。

<a id="bot-is-offline"></a>
### Bot 离线

**原因**：Hermes 网关未运行，或连接失败。

**修复**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误消息。常见问题：URL 错误、令牌过期、Mattermost 服务器不可达。

<a id="user-not-allowed-bot-ignores-you"></a>
### “用户不被允许” / Bot 忽略你

**原因**：你的用户 ID 不在 `MATTERMOST_ALLOWED_USERS` 中。

**修复**：将你的用户 ID 添加到 `~/.hermes/.env` 中的 `MATTERMOST_ALLOWED_USERS` 中，然后重启网关。请记住：用户 ID 是一个 26 个字符的字母数字字符串，而不是你的 `@用户名`。

<a id="per-channel-prompts"></a>
## 按频道提示

为特定的 Mattermost 频道分配临时系统提示。该提示在每次轮次运行时注入——不会持久化到对话历史记录中——因此更改会立即生效。

```yaml
mattermost:
  channel_prompts:
    "channel_id_abc123": |
      你是一名研究助手。专注于学术来源、
      引用和简洁的总结。
    "channel_id_def456": |
      代码审查模式。对边界情况和
      性能影响要精确。
```
Keys 是 Mattermost 频道的 ID（可在频道 URL 或通过 API 获取）。匹配频道中的所有消息都会注入该提示作为临时系统指令。

<a id="security"></a>
## 安全性

:::warning
请始终设置 `MATTERMOST_ALLOWED_USERS`，以限制哪些人可以与机器人交互。若未设置，网关默认拒绝所有用户，作为安全措施。仅添加您信任的用户 ID — 授权用户将拥有对该 Agent 能力的完全访问权限，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

<a id="notes"></a>
## 备注

- **支持自托管**：可与任何自托管的 Mattermost 实例配合使用。无需 Mattermost Cloud 账户或订阅。
- **无额外依赖**：该适配器使用 Hermes Agent 已包含的 `aiohttp` 进行 HTTP 和 WebSocket 通信。
- **兼容团队版**：同时支持 Mattermost 团队版（免费）和企业版。
