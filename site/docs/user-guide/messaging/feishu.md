---
sidebar_position: 11
title: "飞书 / Lark"
description: "将 Hermes Agent 设置为飞书或 Lark 机器人"
---

# 飞书 / Lark 配置

Hermes Agent 可以作为一个功能完备的机器人集成到飞书（Feishu）和 Lark 中。连接成功后，你可以在私聊或群聊中与 Agent 对话，在主聊天窗口接收定时任务（cron job）结果，并通过标准网关流程发送文本、图片、音频和文件附件。

该集成支持两种连接模式：

- `websocket` — 推荐方式；由 Hermes 发起出站连接，你不需要公网 Webhook 端点。
- `webhook` — 当你希望飞书/Lark 通过 HTTP 将事件推送到你的网关时使用。

## Hermes 的行为逻辑

| 场景 | 行为 |
|---------|----------|
| 私聊 | Hermes 会响应每一条消息。 |
| 群聊 | 只有当机器人在群组中被 @ 时，Hermes 才会响应。 |
| 共享群聊 | 默认情况下，共享聊天中的会话历史按用户隔离。 |

这种共享聊天行为由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

只有当你明确希望每个群聊共用一个会话时，才将其设置为 `false`。

## 第 1 步：创建飞书 / Lark 应用

1. 打开飞书或 Lark 开发者后台：
   - 飞书：[https://open.feishu.cn/](https://open.feishu.cn/)
   - Lark：[https://open.larksuite.com/](https://open.larksuite.com/)
2. 创建一个新应用。
3. 在 **凭证与基础信息** 中，复制 **App ID** 和 **App Secret**。
4. 为应用启用 **机器人** 能力。

:::warning
请务必保护好 App Secret。任何拥有它的人都可以冒充你的应用。
:::

## 第 2 步：选择连接模式

### 推荐：WebSocket 模式

当 Hermes 运行在你的笔记本电脑、工作站或私有服务器上时，请使用 WebSocket 模式。不需要公网 URL。官方 Lark SDK 会开启并维护一个持久的出站 WebSocket 连接，并支持自动重连。

```bash
FEISHU_CONNECTION_MODE=websocket
```

**要求：** 必须安装 `websockets` Python 包。SDK 会在内部处理连接生命周期、心跳和自动重连。

**工作原理：** 适配器在后台执行器线程中运行 Lark SDK 的 WebSocket 客户端。入站事件（消息、表情回复、卡片操作）会被分发到主 asyncio 循环。断开连接时，SDK 会尝试自动重连。

### 可选：Webhook 模式

仅当你已经在可访问的 HTTP 端点后运行 Hermes 时，才使用 Webhook 模式。

```bash
FEISHU_CONNECTION_MODE=webhook
```

在 Webhook 模式下，Hermes 会启动一个 HTTP 服务器（通过 `aiohttp`）并在以下路径提供飞书端点：

```text
/feishu/webhook
```

**要求：** 必须安装 `aiohttp` Python 包。

你可以自定义 Webhook 服务器的绑定地址和路径：

```bash
FEISHU_WEBHOOK_HOST=127.0.0.1   # 默认: 127.0.0.1
FEISHU_WEBHOOK_PORT=8765         # 默认: 8765
FEISHU_WEBHOOK_PATH=/feishu/webhook  # 默认: /feishu/webhook
```

当飞书发送 URL 验证挑战（`type: url_verification`）时，Webhook 会自动响应，以便你在飞书开发者后台完成订阅设置。

## 第 3 步：配置 Hermes

### 选项 A：交互式设置

```bash
hermes gateway setup
```

选择 **Feishu / Lark** 并根据提示填写。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret_xxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket

# 可选但强烈建议配置
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
FEISHU_HOME_CHANNEL=oc_xxx
```

`FEISHU_DOMAIN` 接受：

- `feishu` 对应飞书（中国版）
- `lark` 对应 Lark（国际版）

## 第 4 步：启动网关

```bash
hermes gateway
```

然后在飞书/Lark 中给机器人发消息，确认连接已激活。

## 主聊天 (Home Chat)

在飞书/Lark 聊天中使用 `/set-home` 命令，将其标记为主频道，用于接收定时任务结果和跨平台通知。

你也可以预先配置它：

```bash
FEISHU_HOME_CHANNEL=oc_xxx
```

## 安全性

### 用户白名单

为了在生产环境中使用，请设置飞书 Open ID 白名单：

```bash
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
```

如果白名单为空，任何能接触到机器人的人都可能使用它。在群聊中，处理消息前会根据发送者的 open_id 检查白名单。

### Webhook 加密密钥 (Encryption Key)

在 Webhook 模式下运行时，设置加密密钥以启用入站 Webhook 负载的签名验证：

```bash
FEISHU_ENCRYPT_KEY=your-encrypt-key
```

该密钥可以在飞书应用配置的 **事件订阅** 部分找到。设置后，适配器会使用签名算法验证每个 Webhook 请求：

```
SHA256(timestamp + nonce + encrypt_key + body)
```

计算出的哈希值将与 `x-lark-signature` 请求头进行计时安全（timing-safe）比较。签名无效或缺失的请求将被拒绝并返回 HTTP 401。

:::tip
在 WebSocket 模式下，签名验证由 SDK 自身处理，因此 `FEISHU_ENCRYPT_KEY` 是可选的。在 Webhook 模式下，强烈建议在生产环境中开启。
:::

### 验证令牌 (Verification Token)

另一种身份验证层，用于检查 Webhook 负载中的 `token` 字段：

```bash
FEISHU_VERIFICATION_TOKEN=your-verification-token
```

该令牌同样可以在飞书应用的 **事件订阅** 部分找到。设置后，每个入站 Webhook 负载的 `header` 对象中必须包含匹配的 `token`。不匹配的令牌将被拒绝并返回 HTTP 401。

`FEISHU_ENCRYPT_KEY` 和 `FEISHU_VERIFICATION_TOKEN` 可以结合使用以实现深度防御。

## 群消息策略

`FEISHU_GROUP_POLICY` 环境变量控制 Hermes 在群聊中是否响应以及如何响应：

```bash
FEISHU_GROUP_POLICY=allowlist   # 默认值
```

| 取值 | 行为 |
|-------|----------|
| `open` | Hermes 会响应任何群组中任何用户的 @ 提及。 |
| `allowlist` | Hermes 仅响应 `FEISHU_ALLOWED_USERS` 列表中用户的 @ 提及。 |
| `disabled` | Hermes 完全忽略所有群消息。 |

在所有模式下，消息被处理前必须在群组中明确 @ 机器人（或 @所有人）。私聊消息不受此限制。

### 用于 @ 提及过滤的机器人身份

为了在群组中精确检测 @ 提及，适配器需要知道机器人的身份。可以显式提供：

```bash
FEISHU_BOT_OPEN_ID=ou_xxx
FEISHU_BOT_USER_ID=xxx
FEISHU_BOT_NAME=MyBot
```

如果均未设置，适配器将在启动时尝试通过 Application Info API 自动获取机器人名称。为此，需要授予 `admin:app.info:readonly` 或 `application:application:self_manage` 权限范围。

## 交互式卡片操作

当用户点击按钮或与机器人发送的交互式卡片交互时，适配器会将这些操作路由为合成的 `/card` 命令事件：

- 按钮点击变为：`/card button {"key": "value", ...}`
- 卡片定义中 action 的 `value` 负载将以 JSON 形式包含在内。
- 卡片操作在 15 分钟窗口内进行去重，以防止重复处理。

卡片操作事件以 `MessageType.COMMAND` 类型分发，因此它们会流经正常的命令处理管道。

要使用此功能，请在飞书应用的事件订阅中启用 **交互卡片** 事件（`card.action.trigger`）。

## 媒体支持

### 入站（接收）

适配器接收并缓存来自用户的以下媒体类型：

| 类型 | 扩展名 | 处理方式 |
|------|-----------|-------------------|
| **图片** | .jpg, .jpeg, .png, .gif, .webp, .bmp | 通过飞书 API 下载并缓存在本地 |
| **音频** | .ogg, .mp3, .wav, .m4a, .aac, .flac, .opus, .webm | 下载并缓存；小型文本文件会自动提取 |
| **视频** | .mp4, .mov, .avi, .mkv, .webm, .m4v, .3gp | 作为文档下载并缓存 |
| **文件** | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx 等 | 作为文档下载并缓存 |

来自富文本（post）消息的媒体，包括内联图片和文件附件，也会被提取并缓存。

对于小型文本类文档（.txt, .md），文件内容会自动注入到消息文本中，以便 Agent 可以直接读取而无需使用工具。
### 出站（发送）

| 方法 | 发送内容 |
|--------|--------------|
| `send` | 文本或富文本消息（根据 markdown 内容自动检测） |
| `send_image` / `send_image_file` | 上传图片到飞书，然后以原生图片气泡发送（可选包含标题） |
| `send_document` | 上传文件到飞书 API，然后以文件附件形式发送 |
| `send_voice` | 将音频文件作为飞书文件附件上传 |
| `send_video` | 上传视频并以原生媒体消息发送 |
| `send_animation` | GIF 会降级为文件附件（飞书没有原生的 GIF 气泡） |

文件上传路由根据扩展名自动选择：

- `.ogg`, `.opus` → 作为 `opus` 音频上传
- `.mp4`, `.mov`, `.avi`, `.m4v` → 作为 `mp4` 媒体上传
- `.pdf`, `.doc(x)`, `.xls(x)`, `.ppt(x)` → 按其文档类型上传
- 其他所有格式 → 作为通用流文件上传

## Markdown 渲染与富文本回退

当出站文本包含 markdown 格式（标题、加粗、列表、代码块、链接等）时，适配器会自动将其作为带有嵌入式 `md` 标签的飞书**富文本（post）**消息发送，而不是纯文本。这使得在飞书客户端中可以实现丰富的渲染效果。

如果飞书 API 拒绝了富文本负载（例如，由于不支持的 markdown 结构），适配器会自动回退到去除 markdown 格式后的纯文本发送。这种两阶段回退确保了消息总能送达。

纯文本消息（未检测到 markdown）则以简单的 `text` 消息类型发送。

## ACK 表情回复（Reaction）

当适配器收到入站消息时，它会立即添加一个 ✅ (OK) 表情回复，以信号告知消息已收到并正在处理。这在 Agent 完成响应之前提供了视觉反馈。

该回复是持久的 —— 在响应发送后它仍会保留在消息上，作为已处理的标记。

用户在机器人消息上的表情回复也会被追踪。如果用户在机器人发送的消息上添加或移除表情回复，它会被路由为一个合成文本事件（`reaction:added:EMOJI_TYPE` 或 `reaction:removed:EMOJI_TYPE`），以便 Agent 能够对反馈做出响应。

## 爆发保护与分批处理

适配器包含防抖功能，用于处理快速爆发的消息，避免 Agent 过载：

### 文本分批

当用户在短时间内连续发送多条文本消息时，它们会在分发前被合并为一个单一事件：

| 设置 | 环境变量 | 默认值 |
|---------|---------|---------|
| 静默期 | `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | 0.6s |
| 每批最大消息数 | `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | 8 |
| 每批最大字符数 | `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | 4000 |

### 媒体分批

短时间内发送的多个媒体附件（例如，拖入多张图片）会被合并为一个单一事件：

| 设置 | 环境变量 | 默认值 |
|---------|---------|---------|
| 静默期 | `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | 0.8s |

### 逐会话串行化

同一聊天会话内的消息会按顺序串行处理（一次处理一条），以保持对话的连贯性。每个聊天都有自己的锁，因此不同聊天中的消息是并发处理的。

## 速率限制（Webhook 模式）

在 webhook 模式下，适配器强制执行基于 IP 的速率限制以防止滥用：

- **窗口：** 60 秒滑动窗口
- **限制：** 每个 (app_id, path, IP) 三元组每窗口 120 次请求
- **追踪上限：** 最多追踪 4096 个唯一键（防止内存无限制增长）

超过限制的请求将收到 HTTP 429 (Too Many Requests)。

### Webhook 异常追踪

适配器会追踪每个 IP 地址的连续错误响应。如果在 6 小时窗口内来自同一 IP 的连续错误达到 25 次，将记录一条警告。这有助于检测配置错误的客户端或探测尝试。

额外的 webhook 保护：
- **Body 大小限制：** 最大 1 MB
- **Body 读取超时：** 30 秒
- **Content-Type 强制：** 仅接受 `application/json`

## WebSocket 调优 {#websocket-tuning}

使用 `websocket` 模式时，你可以自定义重连和 ping 行为：

```yaml
platforms:
  feishu:
    extra:
      ws_reconnect_interval: 120   # 重连尝试之间的秒数（默认：120）
      ws_ping_interval: 30         # WebSocket ping 之间的秒数（可选；未设置则使用 SDK 默认值）
```

| 设置 | 配置键 | 默认值 | 描述 |
|---------|-----------|---------|-------------|
| 重连间隔 | `ws_reconnect_interval` | 120s | 两次重连尝试之间等待的时间 |
| Ping 间隔 | `ws_ping_interval` | _(SDK 默认)_ | WebSocket 保活 ping 的频率 |

## 逐群组访问控制 {#per-group-access-control}

除了全局的 `FEISHU_GROUP_POLICY` 之外，你还可以使用 `config.yaml` 中的 `group_rules` 为每个群聊设置精细的规则：

```yaml
platforms:
  feishu:
    extra:
      default_group_policy: "open"     # 不在 group_rules 中的群组默认策略
      admins:                          # 可以管理机器人设置的用户
        - "ou_admin_open_id"
      group_rules:
        "oc_group_chat_id_1":
          policy: "allowlist"          # open | allowlist | blacklist | admin_only | disabled
          allowlist:
            - "ou_user_open_id_1"
            - "ou_user_open_id_2"
        "oc_group_chat_id_2":
          policy: "admin_only"
        "oc_group_chat_id_3":
          policy: "blacklist"
          blacklist:
            - "ou_blocked_user"
```

| 策略 | 描述 |
|--------|-------------|
| `open` | 群组中的任何人都可以使用机器人 |
| `allowlist` | 只有群组 `allowlist` 中的用户可以使用机器人 |
| `blacklist` | 除了群组 `blacklist` 中的用户外，所有人都可以使用机器人 |
| `admin_only` | 只有全局 `admins` 列表中的用户可以在此群组中使用机器人 |
| `disabled` | 机器人忽略此群组中的所有消息 |

未在 `group_rules` 中列出的群组将回退到 `default_group_policy`（默认为 `FEISHU_GROUP_POLICY` 的值）。

## 去重

入站消息使用消息 ID 进行去重，TTL 为 24 小时。去重状态会持久化到 `~/.hermes/feishu_seen_message_ids.json`，即使重启也能保持。

| 设置 | 环境变量 | 默认值 |
|---------|---------|---------|
| 缓存大小 | `HERMES_FEISHU_DEDUP_CACHE_SIZE` | 2048 条记录 |

## 所有环境变量

| 变量 | 必填 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `FEISHU_APP_ID` | ✅ | — | 飞书/Lark App ID |
| `FEISHU_APP_SECRET` | ✅ | — | 飞书/Lark App Secret |
| `FEISHU_DOMAIN` | — | `feishu` | `feishu` (国内) 或 `lark` (国际) |
| `FEISHU_CONNECTION_MODE` | — | `websocket` | `websocket` 或 `webhook` |
| `FEISHU_ALLOWED_USERS` | — | _(空)_ | 用户白名单的 open_id 列表（逗号分隔） |
| `FEISHU_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天 ID |
| `FEISHU_ENCRYPT_KEY` | — | _(空)_ | 用于 webhook 签名验证的加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | — | _(空)_ | 用于 webhook 负载认证的验证令牌 |
| `FEISHU_GROUP_POLICY` | — | `allowlist` | 群组消息策略：`open`, `allowlist`, `disabled` |
| `FEISHU_BOT_OPEN_ID` | — | _(空)_ | 机器人的 open_id（用于 @mention 检测） |
| `FEISHU_BOT_USER_ID` | — | _(空)_ | 机器人的 user_id（用于 @mention 检测） |
| `FEISHU_BOT_NAME` | — | _(空)_ | 机器人的显示名称（用于 @mention 检测） |
| `FEISHU_WEBHOOK_HOST` | — | `127.0.0.1` | Webhook 服务器绑定地址 |
| `FEISHU_WEBHOOK_PORT` | — | `8765` | Webhook 服务器端口 |
| `FEISHU_WEBHOOK_PATH` | — | `/feishu/webhook` | Webhook 端点路径 |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | — | `2048` | 追踪去重消息 ID 的最大数量 |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | — | `0.6` | 文本爆发防抖静默期 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | — | `8` | 每个文本批次合并的最大消息数 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | — | `4000` | 每个文本批次合并的最大字符数 |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | — | `0.8` | 媒体爆发防抖静默期 |

WebSocket 和逐群组 ACL 设置通过 `config.yaml` 中的 `platforms.feishu.extra` 进行配置（参见上文的 [WebSocket 调优](#websocket-tuning) 和 [逐群组访问控制](#per-group-access-control)）。
## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `lark-oapi not installed` | 安装 SDK：`pip install lark-oapi` |
| `websockets not installed; websocket mode unavailable` | 安装 websockets：`pip install websockets` |
| `aiohttp not installed; webhook mode unavailable` | 安装 aiohttp：`pip install aiohttp` |
| `FEISHU_APP_ID or FEISHU_APP_SECRET not set` | 设置这两个环境变量，或通过 `hermes gateway setup` 进行配置 |
| `Another local Hermes gateway is already using this Feishu app_id` | 同一时间只能有一个 Hermes 实例使用同一个 `app_id`。请先停止另一个 gateway。 |
| Bot 在群聊中没有响应 | 确保 Bot 被 @ 提及，检查 `FEISHU_GROUP_POLICY`，如果策略是 `allowlist`，请确认发送者在 `FEISHU_ALLOWED_USERS` 中 |
| `Webhook rejected: invalid verification token` | 确保 `FEISHU_VERIFICATION_TOKEN` 与飞书应用“事件订阅”配置中的 Token 一致 |
| `Webhook rejected: invalid signature` | 确保 `FEISHU_ENCRYPT_KEY` 与飞书应用配置中的 Encrypt Key 一致 |
| 富文本消息显示为纯文本 | 飞书 API 拒绝了 post 负载；这是正常的降级行为。请检查日志了解详情。 |
| Bot 无法接收图片/文件 | 为你的飞书应用授予 `im:message` 和 `im:resource` 权限范围 |
| 无法自动检测 Bot 身份 | 授予 `admin:app.info:readonly` 权限，或手动设置 `FEISHU_BOT_OPEN_ID` / `FEISHU_BOT_NAME` |
| `Webhook rate limit exceeded` | 来自同一 IP 的请求超过 120 次/分钟。这通常是配置错误或死循环导致的。 |

## 工具集

飞书 / Lark 使用 `hermes-feishu` 平台预设，其中包含了与 Telegram 及其他基于 gateway 的消息平台相同的核心工具。
