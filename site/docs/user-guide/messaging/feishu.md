---
sidebar_position: 11
title: "飞书 / Lark"
description: "将 Hermes Agent 配置为飞书或 Lark 机器人"
---

<a id="feishu-lark-setup"></a>
# 飞书 / Lark 配置

Hermes Agent 与飞书和 Lark 集成，作为一个功能完备的机器人。连接后，你可以在私聊或群聊中与 Agent 对话，在家庭聊天中接收定时任务结果，并通过常规网关流程发送文本、图片、音频和文件附件。

集成支持两种连接模式：

- `websocket` — 推荐；Hermes 主动建立出站连接，你不需要公开的 webhook 端点
- `webhook` — 当你希望飞书/Lark 通过 HTTP 将事件推送到网关时使用

<a id="how-hermes-behaves"></a>
## Hermes 的行为表现

| 上下文 | 行为 |
|---------|------|
| 私聊 | Hermes 会响应每一条消息。 |
| 群聊 | 只有当机器人在聊天中被 @提及 时，Hermes 才会响应。 |
| 共享群聊 | 默认情况下，共享聊天中每个用户的会话历史是隔离的。 |

共享聊天行为由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

只有当你明确希望每个聊天只共享一个会话时，才将其设置为 `false`。

<a id="step-1-create-a-feishu-lark-app"></a>
## 第一步：创建飞书 / Lark 应用

<a id="recommended-scan-to-create-one-command"></a>
### 推荐：扫码创建（一条命令）

```bash
hermes gateway setup
```

选择 **飞书 / Lark**，然后用飞书或 Lark 手机应用扫描二维码。Hermes 会自动创建一个具有正确权限的机器人应用，并保存凭据。

<a id="alternative-manual-setup"></a>
### 备选：手动设置

如果无法使用扫码创建，向导会回退到手动输入：

1. 打开飞书或 Lark 开发者控制台：
   - 飞书：[https://open.feishu.cn/](https://open.feishu.cn/)
   - Lark：[https://open.larksuite.com/](https://open.larksuite.com/)
2. 创建一个新应用。
3. 在 **凭据与基本信息** 中，复制 **App ID** 和 **App Secret**。
4. 为应用启用 **机器人** 能力。
5. 运行 `hermes gateway setup`，选择 **飞书 / Lark**，然后根据提示输入凭据。

:::warning
请将 App Secret 保密。任何人拥有它都可以冒充你的应用。
:::

<a id="step-2-choose-a-connection-mode"></a>
## 第二步：选择连接模式

<a id="recommended-websocket-mode"></a>
### 推荐：WebSocket 模式

当 Hermes 运行在你的笔记本电脑、工作站或私有服务器上时，请使用 WebSocket 模式。无需公开 URL。官方 Lark SDK 会打开并维护一个持久化的出站 WebSocket 连接，并支持自动重连。

```bash
FEISHU_CONNECTION_MODE=websocket
```

**要求：** 必须安装 `websockets` Python 包。SDK 会在内部处理连接生命周期、心跳和自动重连。

**工作原理：** 适配器在后台执行线程中运行 Lark SDK 的 WebSocket 客户端。入站事件（消息、回复、卡片操作）被分发到主 asyncio 循环。断开连接时，SDK 将自动尝试重新连接。

<a id="optional-webhook-mode"></a>
### 可选：Webhook 模式

仅当你已经将 Hermes 运行在可达的 HTTP 端点之后时，才使用 webhook 模式。

```bash
FEISHU_CONNECTION_MODE=webhook
```

在 webhook 模式下，Hermes 启动一个 HTTP 服务器（通过 `aiohttp`），并在以下地址提供飞书端点：

```text
/feishu/webhook
```

**要求：** 必须安装 `aiohttp` Python 包。
你可以自定义 Webhook 服务器的绑定地址和路径：

```bash
FEISHU_WEBHOOK_HOST=127.0.0.1   # default: 127.0.0.1
FEISHU_WEBHOOK_PORT=8765         # default: 8765
FEISHU_WEBHOOK_PATH=/feishu/webhook  # default: /feishu/webhook
```

当飞书发送 URL 验证挑战（`type: url_verification`）时，Webhook 会自动响应，这样你就可以在飞书开发者后台完成订阅配置。

<a id="step-3-configure-hermes"></a>
## 第三步：配置 Hermes

<a id="option-a-interactive-setup"></a>
### 选项 A：交互式设置

```bash
hermes gateway setup
```

选择 **Feishu / Lark**，然后按照提示填写。

<a id="option-b-manual-configuration"></a>
### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret_xxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket

# 可选，但强烈建议设置
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
FEISHU_HOME_CHANNEL=oc_xxx
```

`FEISHU_DOMAIN` 接受以下值：

- `feishu` 用于飞书中国版
- `lark` 用于 Lark 国际版

<a id="step-4-start-the-gateway"></a>
## 第四步：启动网关

```bash
hermes gateway
```

然后在飞书/Lark 中给机器人发消息，确认连接是否正常。

<a id="home-chat"></a>
## 主聊天（Home Chat）

在飞书/Lark 聊天中使用 `/set-home` 将其标记为“主频道”，用于接收定时任务结果和跨平台通知。

你也可以预先配置它：

```bash
FEISHU_HOME_CHANNEL=oc_xxx
```

<a id="security"></a>
## 安全

<a id="user-allowlist"></a>
### 用户白名单

在生产环境中，设置飞书 Open ID 的白名单：

```bash
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
```

如果白名单为空，任何能接触到机器人的用户都可能使用它。在群聊中，消息处理前会根据发送者的 `open_id` 检查白名单。

<a id="webhook-encryption-key"></a>
### Webhook 加密密钥

在 Webhook 模式下运行时，设置加密密钥以启用对入站 Webhook 负载的签名验证：

```bash
FEISHU_ENCRYPT_KEY=your-encrypt-key
```

该密钥位于飞书应用配置的**事件订阅（Event Subscriptions）**部分。设置后，适配器会使用以下签名算法验证每个 Webhook 请求：

```
SHA256(timestamp + nonce + encrypt_key + body)
```

计算出的哈希值会与 `x-lark-signature` 请求头进行常量时间比较。签名无效或缺失的请求将返回 HTTP 401 被拒绝。

:::tip
在 WebSocket 模式下，签名验证由 SDK 本身处理，因此 `FEISHU_ENCRYPT_KEY` 是可选的。在 Webhook 模式下，强烈建议在生产环境中使用它。
:::

<a id="verification-token"></a>
### 验证令牌（Verification Token）

一种额外的身份验证层，用于检查 Webhook 负载内部的 `token` 字段：

```bash
FEISHU_VERIFICATION_TOKEN=your-verification-token
```

该令牌同样位于飞书应用配置的**事件订阅**部分。设置后，每个入站 Webhook 负载的 `header` 对象中必须包含一个匹配的 `token`。不匹配的令牌将返回 HTTP 401 被拒绝。

`FEISHU_ENCRYPT_KEY` 和 `FEISHU_VERIFICATION_TOKEN` 可以同时使用，实现纵深防御。

<a id="group-message-policy"></a>
## 群聊消息策略

`FEISHU_GROUP_POLICY` 环境变量控制 Hermes 在群聊中是否响应以及如何响应：
```bash
FEISHU_GROUP_POLICY=allowlist   # 默认值
```

| 值 | 行为 |
|-------|----------|
| `open` | Hermes 会响应任何群组中任何用户的 @提及。 |
| `allowlist` | Hermes 仅响应 `FEISHU_ALLOWED_USERS` 中列出的用户的 @提及。 |
| `disabled` | Hermes 完全忽略所有群组消息。 |

在所有模式下，机器人必须被明确 @提及（或 @all）后，消息才会被处理。私聊消息始终绕过此限制。

设置 `FEISHU_REQUIRE_MENTION=false` 可让 Hermes 读取所有群组消息而无需 @提及：

```bash
FEISHU_REQUIRE_MENTION=false
```

如需按聊天控制，可在 `group_rules` 条目中设置 `require_mention`——请参阅下面的[按群组访问控制](#per-group-access-control)。

<a id="bot-identity"></a>
### 机器人身份

Hermes 在启动时会自动检测机器人的 `open_id` 和显示名称。仅当自动检测无法访问飞书 API，或你的应用使用租户级用户 ID 时，才需要手动设置这些值：

```bash
FEISHU_BOT_OPEN_ID=ou_xxx     # 仅在自动检测失败时
FEISHU_BOT_USER_ID=xxx        # 如果你的应用使用 sender_id_type=user_id，则必须设置
FEISHU_BOT_NAME=MyBot         # 仅在自动检测失败时
```

<a id="bot-to-bot-messaging"></a>
## 机器人间消息传递

默认情况下，Hermes 会忽略其他机器人发送的消息。当你希望 Hermes 参与 A2A 编排或接收同一群组中其他机器人的通知时，可以启用机器人间消息传递。

```bash
FEISHU_ALLOW_BOTS=mentions   # 默认值：none
```

| 值 | 行为 |
|-------|----------|
| `none` | 忽略所有来自其他机器人的消息（默认）。 |
| `mentions` | 仅当对方机器人 @提及 Hermes 时接受。 |
| `all` | 接受所有对方机器人的消息。 |

也可以在 `config.yaml` 中配置为 `feishu.allow_bots`（两者都设置时，环境变量优先）。

对方机器人无需添加到 `FEISHU_ALLOWED_USERS`——该白名单仅适用于人类发送者。

授予 `application:bot.basic_info:read` 权限范围可显示对方机器人的名称；没有该权限时，对方机器人仍能正常路由，但会显示为它们的 `open_id`。

<a id="interactive-card-actions"></a>
## 交互式卡片操作

当用户点击按钮或与机器人发送的交互式卡片交互时，适配器会将这些操作路由为合成的 `/card` 命令事件：

- 按钮点击变为：`/card button {"key": "value", ...}`
- 卡片定义中的操作 `value` 负载会以 JSON 形式包含在内。
- 卡片操作会在 15 分钟内去重，以防止重复处理。

网关驱动的更新提示会使用原生的飞书“是”/“否”卡片，而不是回退为纯文本回复。当 `hermes update --gateway` 需要确认时，适配器会将所选答案记录在 Hermes 的 `.update_response` 文件中，并将卡片内联替换为已解决状态。

卡片操作事件以 `MessageType.COMMAND` 类型分发，因此它们会流经正常的命令处理管道。

这也是**命令审批**的工作方式——当 Agent 需要运行危险命令时，它会发送一个带有“允许一次”/“会话”/“始终”/“拒绝”按钮的交互式卡片。用户点击按钮后，卡片操作回调会将审批决定传回给 Agent。
<a id="required-feishu-app-configuration"></a>
### 必需飞书应用配置

交互式卡片需要在飞书开发者中心完成**三个**配置步骤。缺少任何一步，用户点击卡片按钮时都会报错 **200340**。

1. **订阅卡片操作事件：**
   在**事件订阅**中，将 `card.action.trigger` 添加到已订阅的事件中。

2. **开启交互式卡片能力：**
   在**应用功能 > 机器人**中，确保**交互式卡片**开关已启用。这告诉飞书你的应用可以接收卡片操作回调。

3. **配置卡片请求 URL（仅限 Webhook 模式）：**
   在**应用功能 > 机器人 > 消息卡片请求网址**中，将 URL 设置为与事件 Webhook 相同的端点（例如 `https://your-server:8765/feishu/webhook`）。在 WebSocket 模式下，SDK 会自动处理此步骤。

:::warning
如果未完成以上三个步骤，飞书可以成功*发送*交互式卡片（发送仅需 `im:message:send` 权限），但点击任何按钮都会返回错误 200340。卡片看起来是正常的——只有当用户与之交互时才会出现错误。
:::

<a id="document-comment-intelligent-reply"></a>
## 文档评论智能回复

除了聊天外，该适配器还可以回答**飞书/ Lark 文档**中的 `@` 提及。当用户在文档上评论（选中局部文本或对整个文档进行评论）并 @ 提及机器人时，Hermes 会读取文档及其评论上下文，并将 LLM 回复内联发布到该评论线程中。

该处理由 `drive.notice.comment_add_v1` 事件驱动，其执行以下操作：

- 并行获取文档内容和评论时间线（整个文档线程 20 条消息，局部选择线程 12 条消息）。
- 使用限定于该单一评论会话的 `feishu_doc` + `feishu_drive` 工具集运行 Agent。
- 将回复按 4000 字符分段，并作为线程回复发布。
- 每个文档的会话缓存 1 小时，最多 50 条消息，以便对同一文档的后续评论保持上下文。

<a id="3-tier-access-control"></a>
### 三级访问控制

文档评论回复采用**显式授权**模式——没有隐式的全部允许模式。权限按以下顺序解析（每个字段首匹配生效）：

1. **精确文档**——规则限定于特定的文档 token。
2. **通配符**——与文档模式匹配的规则。
3. **顶层**——工作区的默认规则。

每条规则有两个策略可供选择：

- **`allowlist`**——一个静态的用户/租户列表。
- **`pairing`**——静态列表 ∪ 运行时批准的存储。适用于需要审核员实时授予访问权限的推广场景。

规则位于 `~/.hermes/feishu_comment_rules.json`（配对授权位于 `~/.hermes/feishu_comment_pairing.json`），支持基于 mtime 缓存的 hot-reload——编辑会在下一个评论事件时立即生效，无需重启网关。

CLI:

```bash
# 查看当前规则和配对状态
python -m gateway.platforms.feishu_comment_rules status

# 模拟特定文档 + 用户的访问检查
python -m gateway.platforms.feishu_comment_rules check <fileType:fileToken> <user_open_id>

# 运行时管理配对授权
python -m gateway.platforms.feishu_comment_rules pairing list
python -m gateway.platforms.feishu_comment_rules pairing add <user_open_id>
python -m gateway.platforms.feishu_comment_rules pairing remove <user_open_id>
```
<a id="required-feishu-app-configuration"></a>
### 必需的飞书应用配置

在已授予的聊天/卡片权限基础上，添加文档评论事件：

- 在**事件订阅**中订阅 `drive.notice.comment_add_v1`。
- 授予 `docs:doc:readonly` 和 `drive:drive:readonly` 权限范围，以便处理器能够读取文档内容。

<a id="media-support"></a>
## 媒体支持

<a id="inbound-receiving"></a>
### 入站（接收）

适配器会接收并缓存来自用户的以下媒体类型：

| 类型 | 扩展名 | 处理方式 |
|------|--------|----------|
| **图片** | .jpg、.jpeg、.png、.gif、.webp、.bmp | 通过飞书 API 下载并缓存在本地 |
| **音频** | .ogg、.mp3、.wav、.m4a、.aac、.flac、.opus、.webm | 下载并缓存；小型文本文件会自动提取 |
| **视频** | .mp4、.mov、.avi、.mkv、.webm、.m4v、.3gp | 下载并缓存为文档 |
| **文件** | .pdf、.doc、.docx、.xls、.xlsx、.ppt、.pptx 等 | 下载并缓存为文档 |

富文本（post）消息中的媒体（包括内联图片和文件附件）也会被提取并缓存。

对于基于文本的小型文档（.txt、.md），文件内容会自动注入到消息文本中，以便 Agent 可以直接读取，无需使用工具。

<a id="outbound-sending"></a>
### 出站（发送）

| 方法 | 发送内容 |
|------|----------|
| `send` | 文本或富文本 post 消息（根据 markdown 内容自动检测） |
| `send_image` / `send_image_file` | 将图片上传到飞书，然后作为原生图片气泡发送（可附带说明文字） |
| `send_document` | 将文件上传到飞书 API，然后作为文件附件发送 |
| `send_voice` | 将音频文件作为飞书文件附件上传 |
| `send_video` | 上传视频并以原生媒体消息发送 |
| `send_animation` | GIF 降级为文件附件（飞书没有原生 GIF 气泡） |

文件上传路由根据扩展名自动判断：

- `.ogg`、`.opus` → 作为 `opus` 音频上传
- `.mp4`、`.mov`、`.avi`、`.m4v` → 作为 `mp4` 媒体上传
- `.pdf`、`.doc(x)`、`.xls(x)`、`.ppt(x)` → 按其文档类型上传
- 其他所有文件 → 作为通用流文件上传

<a id="markdown-rendering-and-post-fallback"></a>
## Markdown 渲染与 Post 回退

当出站文本包含 markdown 格式（标题、加粗、列表、代码块、链接等）时，适配器会自动将其作为飞书 **post** 消息发送（内嵌 `md` 标签），而非纯文本。这样可以在飞书客户端中实现富文本渲染。

如果飞书 API 拒绝了 post 载荷（例如由于不支持的 markdown 结构），适配器会自动回退为纯文本发送（去除 markdown）。这种两阶段回退机制确保消息始终能够送达。

纯文本消息（未检测到 markdown）将以简单的 `text` 消息类型发送。

<a id="processing-status-reactions"></a>
## 处理状态反应

当 Agent 正在工作时，机器人会在你的消息上显示一个 `Typing` 反应。回复到达时该反应会消失；如果处理失败，则会被替换为 `CrossMark`。

将 `FEISHU_REACTIONS=false` 设置为关闭此功能。

<a id="burst-protection-and-batching"></a>
## 突发保护与批处理
该适配器包含对快速消息突发的防抖处理，以避免对 Agent 造成过载：

<a id="text-batching"></a>
### 文本批处理

当用户在短时间内连续发送多条文本消息时，它们会被合并为单个事件后再分发：

| 设置项 | 环境变量 | 默认值 |
|---------|---------|---------|
| 静默期 | `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | 0.6s |
| 每批最大消息数 | `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | 8 |
| 每批最大字符数 | `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | 4000 |

<a id="media-batching"></a>
### 媒体批处理

用户在短时间内连续发送多个媒体附件（例如拖拽多张图片）时，会被合并为单个事件：

| 设置项 | 环境变量 | 默认值 |
|---------|---------|---------|
| 静默期 | `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | 0.8s |

<a id="per-chat-serialization"></a>
### 按会话串行化

同一会话内的消息会串行处理（一次一条），以保持对话连贯性。每个会话有自己的锁，因此不同会话中的消息可以并发处理。

<a id="rate-limiting-webhook-mode"></a>
## 速率限制（Webhook 模式）

在 webhook 模式下，适配器会按 IP 实施速率限制以防止滥用：

- **窗口：** 60 秒滑动窗口
- **限制：** 每个 (app_id, path, IP) 三元组在每个窗口内最多 120 个请求
- **跟踪上限：** 最多跟踪 4096 个唯一键（防止内存无限增长）

超出限制的请求将收到 HTTP 429（请求过多）响应。

<a id="webhook-anomaly-tracking"></a>
### Webhook 异常跟踪

适配器会跟踪每个 IP 地址的连续错误响应次数。如果在 6 小时内同一 IP 连续出现 25 次错误，则会记录一条警告。这有助于检测配置错误的客户端或探测尝试。

其他 Webhook 保护措施：
- **请求体大小限制：** 最大 1 MB
- **请求体读取超时：** 30 秒
- **Content-Type 强制：** 仅接受 `application/json`

<a id="websocket-tuning"></a>
## WebSocket 调优 {#websocket-tuning}

使用 `websocket` 模式时，可以自定义重连和 ping 行为：

```yaml
platforms:
  feishu:
    extra:
      ws_reconnect_interval: 120   # 重连尝试之间的等待秒数（默认：120）
      ws_ping_interval: 30         # WebSocket ping 间隔秒数（可选；未设置时使用 SDK 默认值）
```

| 设置项 | 配置键 | 默认值 | 描述 |
|---------|-----------|---------|-------------|
| 重连间隔 | `ws_reconnect_interval` | 120s | 重连尝试之间的等待时长 |
| Ping 间隔 | `ws_ping_interval` | _(SDK 默认值)_ | WebSocket 保活 ping 的频率 |

<a id="per-group-access-control"></a>
## 按群组访问控制

除了全局的 `FEISHU_GROUP_POLICY`，你还可以通过 config.yaml 中的 `group_rules` 为每个群聊设置更精细的规则：

```yaml
platforms:
  feishu:
    extra:
      default_group_policy: "open"     # 未在 group_rules 中指定的群组默认策略
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
        "oc_free_chat":
          policy: "open"
          require_mention: false       # 对该群聊覆盖 FEISHU_REQUIRE_MENTION 设置
```
| 策略 | 说明 |
|--------|-------------|
| `open` | 群组中任何人都可以使用机器人 |
| `allowlist` | 只有群组白名单中的用户可以使用机器人 |
| `blacklist` | 除群组黑名单中的用户外，其他人均可使用机器人 |
| `admin_only` | 只有全局管理员列表中的用户能在此群组中使用机器人 |
| `disabled` | 机器人忽略该群组的所有消息 |

在 `group_rules` 条目中设置 `require_mention: false`，可以跳过该特定聊天的 @提及要求。省略时，该聊天会继承全局的 `FEISHU_REQUIRE_MENTION` 值。

未在 `group_rules` 中列出的群组，将回退使用 `default_group_policy`（默认值为 `FEISHU_GROUP_POLICY` 的值）。

<a id="deduplication"></a>
## 去重

入站消息通过消息 ID 进行去重，TTL 为 24 小时。去重状态会在重启后持久化到 `~/.hermes/feishu_seen_message_ids.json` 文件中。

| 设置项 | 环境变量 | 默认值 |
|---------|---------|---------|
| 缓存大小 | `HERMES_FEISHU_DEDUP_CACHE_SIZE` | 2048 条 |

<a id="all-environment-variables"></a>
## 所有环境变量

| 变量 | 必须 | 默认值 | 说明 |
|----------|----------|---------|-------------|
| `FEISHU_APP_ID` | ✅ | — | 飞书 / Lark App ID |
| `FEISHU_APP_SECRET` | ✅ | — | 飞书 / Lark App Secret |
| `FEISHU_DOMAIN` | — | `feishu` | `feishu`（中国）或 `lark`（国际） |
| `FEISHU_CONNECTION_MODE` | — | `websocket` | `websocket` 或 `webhook` |
| `FEISHU_ALLOWED_USERS` | — | _(空)_ | 用户白名单，用逗号分隔的 open_id 列表 |
| `FEISHU_ALLOW_BOTS` | — | `none` | 接受来自其他机器人的消息：`none`、`mentions` 或 `all` |
| `FEISHU_REQUIRE_MENTION` | — | `true` | 群组消息是否需要 @提及机器人 |
| `FEISHU_HOME_CHANNEL` | — | — | 定时任务/通知输出的聊天 ID |
| `FEISHU_ENCRYPT_KEY` | — | _(空)_ | webhook 签名验证的加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | — | _(空)_ | webhook 负载认证的验证令牌 |
| `FEISHU_GROUP_POLICY` | — | `allowlist` | 群组消息策略：`open`、`allowlist`、`disabled` |
| `FEISHU_BOT_OPEN_ID` | — | _(空)_ | 机器人的 open_id（用于检测 @提及） |
| `FEISHU_BOT_USER_ID` | — | _(空)_ | 机器人的 user_id（用于检测 @提及） |
| `FEISHU_BOT_NAME` | — | _(空)_ | 机器人的显示名称（用于检测 @提及） |
| `FEISHU_WEBHOOK_HOST` | — | `127.0.0.1` | Webhook 服务器绑定地址 |
| `FEISHU_WEBHOOK_PORT` | — | `8765` | Webhook 服务器端口 |
| `FEISHU_WEBHOOK_PATH` | — | `/feishu/webhook` | Webhook 端点路径 |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | — | `2048` | 最多追踪的去重消息 ID 数量 |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | — | `0.6` | 文本突发防抖静默期 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | — | `8` | 每条文本批次最多合并的消息数 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | — | `4000` | 每条文本批次最多合并的字符数 |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | — | `0.8` | 媒体突发防抖静默期 |

WebSocket 和每个群组的 ACL 设置通过 `config.yaml` 的 `platforms.feishu.extra` 配置（参见上文 [WebSocket 调优](#websocket-tuning) 和 [每个群组的访问控制](#per-group-access-control)）。
<a id="troubleshooting"></a>
## 故障排除

| 问题 | 修复 |
|---------|-----|
| `lark-oapi not installed` | 安装 SDK：`pip install lark-oapi` |
| `websockets not installed; websocket mode unavailable` | 安装 websockets：`pip install websockets` |
| `aiohttp not installed; webhook mode unavailable` | 安装 aiohttp：`pip install aiohttp` |
| `FEISHU_APP_ID or FEISHU_APP_SECRET not set` | 设置这两个环境变量，或通过 `hermes gateway setup` 进行配置 |
| `Another local Hermes gateway is already using this Feishu app_id` | 同一时间只能有一个 Hermes 实例使用同一个 app_id。请先停止另一个网关。 |
| 机器人在群聊中无响应 | 确保机器人被 @ 提及，检查 `FEISHU_GROUP_POLICY`，如果策略为 `allowlist`，请验证发送者是否在 `FEISHU_ALLOWED_USERS` 中 |
| `Webhook rejected: invalid verification token` | 确保 `FEISHU_VERIFICATION_TOKEN` 与飞书应用事件订阅配置中的 token 一致 |
| `Webhook rejected: invalid signature` | 确保 `FEISHU_ENCRYPT_KEY` 与飞书应用配置中的加密密钥一致 |
| 发送的消息显示为纯文本 | 飞书 API 拒绝了 post 消息体；这是正常的降级行为。查看日志了解详情。 |
| 机器人未收到图片/文件 | 为飞书应用授予 `im:message` 和 `im:resource` 权限范围 |
| 机器人身份未自动检测 | 通常是访问飞书机器人信息接口时的临时网络问题。可手动设置 `FEISHU_BOT_OPEN_ID` 和 `FEISHU_BOT_NAME` 作为临时解决方案。 |
| 启用 `FEISHU_ALLOW_BOTS` 后，其他机器人的消息仍被忽略 | Hermes 尚无法识别自身——请设置 `FEISHU_BOT_OPEN_ID`（如果应用使用 `sender_id_type=user_id`，还需设置 `FEISHU_BOT_USER_ID`）。 |
| 其他机器人显示为 `ou_xxxxxx` 而非名称 | 授予 `application:bot.basic_info:read` 范围。 |
| 点击审批按钮时出现错误 200340 | 在飞书开发者控制台中启用**交互式卡片**能力并配置**卡片请求地址**。请参见上方的[飞书应用必需配置](#required-feishu-app-configuration)。 |
| `Webhook rate limit exceeded` | 同一 IP 每分钟超过 120 次请求。这通常是配置错误或循环导致的。 |

<a id="toolset"></a>
## 工具集

飞书 / Lark 使用 `hermes-feishu` 平台预设，该预设包含与 Telegram 及其他基于网关的消息平台相同的核心工具。
