---
sidebar_position: 11
title: "飞书 / Lark"
description: "将 Hermes Agent 设置为飞书或 Lark 机器人"
---

# 飞书 / Lark 设置

Hermes Agent 作为功能齐全的机器人集成了飞书和 Lark。连接后，你可以在私聊或群聊中与 Agent 对话，在主页聊天中接收定时任务结果，并通过普通网关流程发送文本、图片、音频和文件附件。

该集成支持两种连接模式：

- `websocket` — 推荐使用；Hermes 主动发起连接，无需公开的 webhook 端点
- `webhook` — 适用于你希望飞书/Lark 通过 HTTP 向你的网关推送事件的场景

## Hermes 的行为表现

| 场景 | 行为 |
|---------|----------|
| 私聊 | Hermes 会回复每条消息。 |
| 群聊 | 只有当机器人在聊天中被 @提及时，Hermes 才会回复。 |
| 共享群聊 | 默认情况下，共享群聊内的会话历史是按用户隔离的。 |

这种共享群聊行为由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

只有当你明确希望每个群聊只有一个共享会话时，才将其设置为 `false`。

## 第 1 步：创建飞书 / Lark 应用

1. 打开飞书或 Lark 开发者控制台：
   - 飞书: [https://open.feishu.cn/](https://open.feishu.cn/)
   - Lark: [https://open.larksuite.com/](https://open.larksuite.com/)
2. 创建一个新应用。
3. 在 **凭证与基础信息** 中，复制 **App ID** 和 **App Secret**。
4. 启用应用的 **机器人** 功能。

:::warning
请妥善保管 App Secret，任何拥有它的人都可以冒充你的应用。
:::

## 第 2 步：选择连接模式

### 推荐：WebSocket 模式

当 Hermes 运行在你的笔记本、工作站或私有服务器上时，使用 WebSocket 模式。无需公开 URL。官方 Lark SDK 会打开并维护一个持久的出站 WebSocket 连接，并自动重连。

```bash
FEISHU_CONNECTION_MODE=websocket
```

**要求：** 需要安装 `websockets` Python 包。SDK 内部处理连接生命周期、心跳和自动重连。

**工作原理：** 适配器在后台执行器线程中运行 Lark SDK 的 WebSocket 客户端。入站事件（消息、表情、卡片操作）会分发到主 asyncio 循环。断开连接时，SDK 会自动尝试重连。

### 可选：Webhook 模式

仅当你已经在可访问的 HTTP 端点后运行 Hermes 时，才使用 webhook 模式。

```bash
FEISHU_CONNECTION_MODE=webhook
```

在 webhook 模式下，Hermes 会启动一个 HTTP 服务器（通过 `aiohttp`），并提供一个飞书端点：

```text
/feishu/webhook
```

**要求：** 需要安装 `aiohttp` Python 包。

你可以自定义 webhook 服务器的绑定地址和路径：

```bash
FEISHU_WEBHOOK_HOST=127.0.0.1   # 默认: 127.0.0.1
FEISHU_WEBHOOK_PORT=8765         # 默认: 8765
FEISHU_WEBHOOK_PATH=/feishu/webhook  # 默认: /feishu/webhook
```

当飞书发送 URL 验证挑战（`type: url_verification`）时，webhook 会自动响应，方便你在飞书开发者控制台完成订阅设置。

## 第 3 步：配置 Hermes

### 选项 A：交互式设置

```bash
hermes gateway setup
```

选择 **飞书 / Lark** 并填写提示信息。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret_xxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket

# 可选但强烈推荐
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
FEISHU_HOME_CHANNEL=oc_xxx
```

`FEISHU_DOMAIN` 可选值：

- `feishu` 表示飞书中国区
- `lark` 表示 Lark 国际版

## 第 4 步：启动网关

```bash
hermes gateway
```

然后从飞书/Lark 给机器人发消息，确认连接已生效。

## 主页聊天

在飞书/Lark 聊天中使用 `/set-home` 命令，将该聊天标记为定时任务结果和跨平台通知的主页频道。

你也可以预先配置：

```bash
FEISHU_HOME_CHANNEL=oc_xxx
```

## 安全性

### 用户白名单

生产环境中，建议设置飞书 Open ID 的白名单：

```bash
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
```

如果白名单为空，任何能访问机器人的人都可能使用它。在群聊中，白名单会在消息处理前检查发送者的 open_id。

### Webhook 加密密钥

在 webhook 模式下，设置加密密钥以启用入站 webhook 负载的签名验证：

```bash
FEISHU_ENCRYPT_KEY=your-encrypt-key
```

该密钥可在飞书应用配置的 **事件订阅** 部分找到。设置后，适配器会使用以下签名算法验证每个 webhook 请求：

```
SHA256(timestamp + nonce + encrypt_key + body)
```

计算出的哈希值会与 `x-lark-signature` 头部进行定时安全比较。签名无效或缺失的请求会被拒绝，返回 HTTP 401。

:::tip
WebSocket 模式下，签名验证由 SDK 自行处理，因此 `FEISHU_ENCRYPT_KEY` 是可选的。Webhook 模式下，生产环境强烈建议启用。
:::

### 验证令牌

另一层身份验证，检查 webhook 负载中的 `token` 字段：

```bash
FEISHU_VERIFICATION_TOKEN=your-verification-token
```

该令牌同样在飞书应用的 **事件订阅** 部分找到。设置后，每个入站 webhook 负载必须在其 `header` 对象中包含匹配的 `token`。令牌不匹配的请求会被拒绝，返回 HTTP 401。

`FEISHU_ENCRYPT_KEY` 和 `FEISHU_VERIFICATION_TOKEN` 可以同时使用，增强安全防护。

## 群消息策略

`FEISHU_GROUP_POLICY` 环境变量控制 Hermes 在群聊中的响应策略：

```bash
FEISHU_GROUP_POLICY=allowlist   # 默认值
```

| 值 | 行为 |
|-------|----------|
| `open` | Hermes 会回复任何用户在任何群组中对机器人的 @提及。 |
| `allowlist` | Hermes 只回复 `FEISHU_ALLOWED_USERS` 白名单中的用户对机器人的 @提及。 |
| `disabled` | Hermes 完全忽略所有群消息。 |

所有模式下，机器人必须被明确 @提及（或 @all）后，消息才会被处理。私聊则绕过此限制。

### 用于 @提及门控的机器人身份

为了准确检测群聊中的 @提及，适配器需要知道机器人的身份。可以显式提供：

```bash
FEISHU_BOT_OPEN_ID=ou_xxx
FEISHU_BOT_USER_ID=xxx
FEISHU_BOT_NAME=MyBot
```

如果未设置，适配器会在启动时通过应用信息 API 尝试自动发现机器人名称。为此，需要授予 `admin:app.info:readonly` 或 `application:application:self_manage` 权限范围。

## 交互式卡片操作

当用户点击机器人发送的按钮或与交互式卡片互动时，适配器会将这些操作路由为合成的 `/card` 命令事件：

- 按钮点击变为：`/card button {"key": "value", ...}`
- 卡片定义中的 `value` 负载会作为 JSON 一并传递。
- 卡片操作有 15 分钟的去重窗口，防止重复处理。

卡片操作事件以 `MessageType.COMMAND` 形式分发，走正常的命令处理流程。

要使用此功能，请在飞书应用的事件订阅中启用 **交互式卡片** 事件（`card.action.trigger`）。

## 媒体支持

### 入站（接收）

适配器接收并缓存用户发送的以下媒体类型：

| 类型 | 扩展名 | 处理方式 |
|------|-----------|-------------------|
| **图片** | .jpg, .jpeg, .png, .gif, .webp, .bmp | 通过飞书 API 下载并本地缓存 |
| **音频** | .ogg, .mp3, .wav, .m4a, .aac, .flac, .opus, .webm | 下载并缓存；小型文本文件会自动提取内容 |
| **视频** | .mp4, .mov, .avi, .mkv, .webm, .m4v, .3gp | 作为文档下载并缓存 |
| **文件** | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx 等 | 作为文档下载并缓存 |

富文本（post）消息中的媒体，包括内嵌图片和文件附件，也会被提取并缓存。

对于小型文本类文档（.txt、.md），文件内容会自动注入消息文本中，Agent 可以直接读取，无需额外工具。
### 出站（发送）

| 方法 | 发送内容 |
|--------|--------------|
| `send` | 文本或富文本消息（根据 markdown 内容自动识别） |
| `send_image` / `send_image_file` | 上传图片到 Feishu，然后以原生图片气泡形式发送（可选带标题） |
| `send_document` | 上传文件到 Feishu API，然后作为文件附件发送 |
| `send_voice` | 上传音频文件作为 Feishu 文件附件 |
| `send_video` | 上传视频并作为原生媒体消息发送 |
| `send_animation` | GIF 会降级为文件附件（Feishu 不支持原生 GIF 气泡） |

文件上传会根据扩展名自动路由：

- `.ogg`、`.opus` → 作为 `opus` 音频上传
- `.mp4`、`.mov`、`.avi`、`.m4v` → 作为 `mp4` 媒体上传
- `.pdf`、`.doc(x)`、`.xls(x)`、`.ppt(x)` → 以对应文档类型上传
- 其他所有文件 → 作为通用流文件上传

## Markdown 渲染与 Post 回退

当出站文本包含 markdown 格式（标题、加粗、列表、代码块、链接等）时，适配器会自动将其作为 Feishu **post** 消息发送，内嵌 `md` 标签，而非纯文本。这能让 Feishu 客户端实现富文本渲染。

如果 Feishu API 拒绝 post 负载（例如因不支持的 markdown 结构），适配器会自动回退为纯文本发送，且去除 markdown 格式。这个两阶段回退机制确保消息总能送达。

纯文本消息（未检测到 markdown）则作为简单的 `text` 消息类型发送。

## 确认表情反应（ACK Emoji Reactions）

当适配器收到入站消息时，会立即添加一个 ✅（OK）表情反应，表示消息已收到并正在处理。这为用户提供了视觉反馈，表明 Agent 正在响应。

该反应是持久的——响应发送后仍保留在消息上，作为收条标记。

用户对机器人消息的表情反应也会被跟踪。如果用户对机器人发送的消息添加或移除表情反应，会被路由为合成文本事件（`reaction:added:EMOJI_TYPE` 或 `reaction:removed:EMOJI_TYPE`），方便 Agent 对反馈做出响应。

## 突发保护与批量处理

适配器对快速消息突发进行了防抖处理，避免 Agent 负载过重：

### 文本批量处理

当用户快速连续发送多条文本消息时，会合并成一个事件再分发：

| 设置 | 环境变量 | 默认值 |
|---------|---------|---------|
| 静默期 | `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | 0.6秒 |
| 每批最大消息数 | `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | 8 |
| 每批最大字符数 | `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | 4000 |

### 媒体批量处理

快速连续发送的多条媒体附件（例如拖拽多张图片）会合并成一个事件：

| 设置 | 环境变量 | 默认值 |
|---------|---------|---------|
| 静默期 | `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | 0.8秒 |

### 每聊天序列化

同一聊天内的消息会串行处理（一次处理一条），以保持对话连贯。每个聊天有独立锁，不同聊天间消息可并发处理。

## 速率限制（Webhook 模式）

在 webhook 模式下，适配器对每个 IP 实施速率限制以防滥用：

- **时间窗口：** 60秒滑动窗口
- **限制：** 每个 (app_id, path, IP) 三元组每窗口最多 120 次请求
- **跟踪上限：** 最多跟踪 4096 个唯一键（防止内存无限增长）

超出限制的请求会返回 HTTP 429（请求过多）。

### Webhook 异常跟踪

适配器会跟踪每个 IP 的连续错误响应次数。在 6 小时内同一 IP 连续 25 次错误后，会记录警告日志，帮助发现配置错误或探测行为。

其他 webhook 保护措施：
- **请求体大小限制：** 最大 1 MB
- **请求体读取超时：** 30 秒
- **Content-Type 强制：** 只接受 `application/json`

## 去重

入站消息通过消息 ID 进行去重，TTL 为 24 小时。去重状态会持久化到 `~/.hermes/feishu_seen_message_ids.json`，重启后依然有效。

| 设置 | 环境变量 | 默认值 |
|---------|---------|---------|
| 缓存大小 | `HERMES_FEISHU_DEDUP_CACHE_SIZE` | 2048 条目 |

## 所有环境变量

| 变量 | 是否必需 | 默认值 | 说明 |
|----------|----------|---------|-------------|
| `FEISHU_APP_ID` | ✅ | — | Feishu/Lark 应用 ID |
| `FEISHU_APP_SECRET` | ✅ | — | Feishu/Lark 应用密钥 |
| `FEISHU_DOMAIN` | — | `feishu` | `feishu`（中国区）或 `lark`（国际区） |
| `FEISHU_CONNECTION_MODE` | — | `websocket` | `websocket` 或 `webhook` |
| `FEISHU_ALLOWED_USERS` | — | _(空)_ | 逗号分隔的 open_id 用户白名单 |
| `FEISHU_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天 ID |
| `FEISHU_ENCRYPT_KEY` | — | _(空)_ | webhook 签名验证的加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | — | _(空)_ | webhook 负载认证的验证令牌 |
| `FEISHU_GROUP_POLICY` | — | `allowlist` | 群消息策略：`open`、`allowlist`、`disabled` |
| `FEISHU_BOT_OPEN_ID` | — | _(空)_ | 机器人 open_id（用于 @提及检测） |
| `FEISHU_BOT_USER_ID` | — | _(空)_ | 机器人 user_id（用于 @提及检测） |
| `FEISHU_BOT_NAME` | — | _(空)_ | 机器人显示名称（用于 @提及检测） |
| `FEISHU_WEBHOOK_HOST` | — | `127.0.0.1` | webhook 服务器绑定地址 |
| `FEISHU_WEBHOOK_PORT` | — | `8765` | webhook 服务器端口 |
| `FEISHU_WEBHOOK_PATH` | — | `/feishu/webhook` | webhook 端点路径 |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | — | `2048` | 最大去重消息 ID 数量 |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | — | `0.6` | 文本突发防抖静默期 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | — | `8` | 每批合并的最大消息数 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | — | `4000` | 每批合并的最大字符数 |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | — | `0.8` | 媒体突发防抖静默期 |

## 故障排查

| 问题 | 解决方案 |
|---------|-----|
| `lark-oapi not installed` | 安装 SDK：`pip install lark-oapi` |
| `websockets not installed; websocket mode unavailable` | 安装 websockets：`pip install websockets` |
| `aiohttp not installed; webhook mode unavailable` | 安装 aiohttp：`pip install aiohttp` |
| `FEISHU_APP_ID or FEISHU_APP_SECRET not set` | 设置这两个环境变量，或通过 `hermes gateway setup` 配置 |
| `Another local Hermes gateway is already using this Feishu app_id` | 同一时间只能有一个 Hermes 实例使用相同 app_id，先停止其他实例 |
| 机器人在群组不响应 | 确保机器人被 @提及，检查 `FEISHU_GROUP_POLICY`，若为 `allowlist`，确认发送者在 `FEISHU_ALLOWED_USERS` 中 |
| `Webhook rejected: invalid verification token` | 确认 `FEISHU_VERIFICATION_TOKEN` 与 Feishu 应用事件订阅配置中的令牌一致 |
| `Webhook rejected: invalid signature` | 确认 `FEISHU_ENCRYPT_KEY` 与 Feishu 应用配置中的加密密钥一致 |
| Post 消息显示为纯文本 | Feishu API 拒绝了 post 负载，这是正常的回退行为。查看日志了解详情。 |
| 图片/文件未被机器人接收 | 给 Feishu 应用授权 `im:message` 和 `im:resource` 权限范围 |
| 机器人身份未自动识别 | 授权 `admin:app.info:readonly` 权限，或手动设置 `FEISHU_BOT_OPEN_ID` / `FEISHU_BOT_NAME` |
| `Webhook rate limit exceeded` | 同一 IP 超过每分钟 120 次请求，通常是配置错误或循环请求导致 |

## 工具集

Feishu / Lark 使用 `hermes-feishu` 平台预设，包含与 Telegram 及其他基于网关的消息平台相同的核心工具。
