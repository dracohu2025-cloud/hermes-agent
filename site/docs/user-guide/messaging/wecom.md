---
sidebar_position: 14
title: "WeCom (企业微信)"
description: "通过 AI Bot WebSocket 网关将 Hermes Agent 连接到企业微信"
---

# WeCom (企业微信) {#wecom-enterprise-wechat}

将 Hermes 连接到 [企业微信](https://work.weixin.qq.com/) (WeCom)，这是腾讯推出的企业级通讯平台。该适配器使用企业微信的 AI Bot WebSocket 网关进行实时双向通信 —— 无需公网端点或 Webhook。

## 前置条件 {#prerequisites}

- 一个企业微信组织账号
- 在企业微信管理后台创建一个 AI Bot
- 来自机器人凭据页面的 Bot ID 和 Secret
- Python 包：`aiohttp` 和 `httpx`

## 设置 {#setup}

### 1. 创建 AI Bot {#1-create-an-ai-bot}

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 导航至 **应用管理** → **创建应用** → **AI Bot**
3. 配置机器人名称和描述
4. 从凭据页面复制 **Bot ID** 和 **Secret**

### 2. 配置 Hermes {#2-configure-hermes}

运行交互式设置：

```bash
hermes gateway setup
```

选择 **WeCom** 并输入你的 Bot ID 和 Secret。

或者在 `~/.hermes/.env` 中设置环境变量：

```bash
WECOM_BOT_ID=your-bot-id
WECOM_SECRET=your-secret

# 可选：限制访问
WECOM_ALLOWED_USERS=user_id_1,user_id_2

# 可选：用于定时任务/通知的主频道
WECOM_HOME_CHANNEL=chat_id
```

### 3. 启动网关 {#3-start-the-gateway}

```bash
hermes gateway
```

## 功能特性 {#features}

- **WebSocket 传输** —— 持久连接，无需公网端点
- **私聊和群聊消息** —— 可配置的访问策略
- **分群组发送者白名单** —— 精细控制每个群组中谁可以进行交互
- **媒体支持** —— 图片、文件、语音、视频的上传和下载
- **AES 加密媒体** —— 自动解密入站附件
- **引用上下文** —— 保留回复线程
- **Markdown 渲染** —— 富文本响应
- **回复模式流式传输** —— 将响应与入站消息上下文关联
- **自动重连** —— 连接断开时采用指数退避机制

## 配置选项 {#configuration-options}

在 `config.yaml` 的 `platforms.wecom.extra` 下设置这些选项：

| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `bot_id` | — | 企业微信 AI Bot ID (必填) |
| `secret` | — | 企业微信 AI Bot Secret (必填) |
| `websocket_url` | `wss://openws.work.weixin.qq.com` | WebSocket 网关 URL |
| `dm_policy` | `open` | 私聊访问策略：`open`, `allowlist`, `disabled`, `pairing` |
| `group_policy` | `open` | 群聊访问策略：`open`, `allowlist`, `disabled` |
| `allow_from` | `[]` | 允许私聊的用户 ID (当 dm_policy=allowlist 时) |
| `group_allow_from` | `[]` | 允许的群组 ID (当 group_policy=allowlist 时) |
| `groups` | `{}` | 特定群组配置 (见下文) |

## 访问策略 {#access-policies}

### 私聊策略 (DM Policy) {#dm-policy}

控制谁可以向 Agent 发送私聊消息：

| 值 | 行为 |
|-------|----------|
| `open` | 任何人都可以私聊 Agent (默认) |
| `allowlist` | 只有 `allow_from` 中的用户 ID 可以私聊 |
| `disabled` | 忽略所有私聊消息 |
| `pairing` | 配对模式 (用于初始设置) |

```bash
WECOM_DM_POLICY=allowlist
```

### 群聊策略 (Group Policy) {#group-policy}

控制 Agent 在哪些群组中做出响应：

| 值 | 行为 |
|-------|----------|
| `open` | Agent 在所有群组中响应 (默认) |
| `allowlist` | Agent 仅在 `group_allow_from` 列出的群组 ID 中响应 |
| `disabled` | 忽略所有群组消息 |

```bash
WECOM_GROUP_POLICY=allowlist
```

### 分群组发送者白名单 {#per-group-sender-allowlists}

为了实现精细化控制，你可以限制特定群组内允许与 Agent 交互的用户。这在 `config.yaml` 中配置：

```yaml
platforms:
  wecom:
    enabled: true
    extra:
      bot_id: "your-bot-id"
      secret: "your-secret"
      group_policy: "allowlist"
      group_allow_from:
        - "group_id_1"
        - "group_id_2"
      groups:
        group_id_1:
          allow_from:
            - "user_alice"
            - "user_bob"
        group_id_2:
          allow_from:
            - "user_charlie"
        "*":
          allow_from:
            - "user_admin"
```

**工作原理：**

1. `group_policy` 和 `group_allow_from` 控制决定了该群组是否被允许访问。
2. 如果群组通过了顶级检查，`groups.<group_id>.allow_from` 列表（如果存在）将进一步限制该群组内哪些发送者可以与 Agent 交互。
3. 通配符 `"*"` 群组条目作为未明确列出的群组的默认设置。
4. 白名单条目支持 `*` 通配符以允许所有用户，且条目不区分大小写。
5. 条目可以可选地使用 `wecom:user:` 或 `wecom:group:` 前缀格式 —— 前缀会被自动剥离。

如果群组未配置 `allow_from`，则该群组中的所有用户都被允许（前提是群组本身通过了顶级策略检查）。

## 媒体支持 {#media-support}

### 入站 (接收) {#inbound-receiving}

适配器接收来自用户的媒体附件并将其缓存在本地供 Agent 处理：

| 类型 | 处理方式 |
|------|-----------------|
| **图片** | 下载并缓存在本地。支持基于 URL 和 base64 编码的图片。 |
| **文件** | 下载并缓存。保留原始消息中的文件名。 |
| **语音** | 如果可用，将提取语音消息的文本转写。 |
| **混合消息** | 企业微信混合类型消息（文本 + 图片）会被解析并提取所有组件。 |

**引用消息：** 被引用（回复）的消息中的媒体也会被提取，因此 Agent 拥有关于用户回复内容的上下文。

### AES 加密媒体解密 {#aes-encrypted-media-decryption}

企业微信使用 AES-256-CBC 加密某些入站媒体附件。适配器会自动处理：

- 当入站媒体项包含 `aeskey` 字段时，适配器会下载加密字节并使用带 PKCS#7 填充的 AES-256-CBC 进行解密。
- AES 密钥是 `aeskey` 字段的 base64 解码值（必须恰好为 32 字节）。
- IV 派生自密钥的前 16 个字节。
- 这需要安装 `cryptography` Python 包 (`pip install cryptography`)。

无需配置 —— 收到加密媒体时会自动进行透明解密。

### 出站 (发送) {#outbound-sending}

| 方法 | 发送内容 | 大小限制 |
|--------|--------------|------------|
| `send` | Markdown 文本消息 | 4000 字符 |
| `send_image` / `send_image_file` | 原生图片消息 | 10 MB |
| `send_document` | 文件附件 | 20 MB |
| `send_voice` | 语音消息 (原生语音仅限 AMR 格式) | 2 MB |
| `send_video` | 视频消息 | 10 MB |

**分块上传：** 文件通过三步协议（初始化 → 分块 → 完成）以 512 KB 的分块进行上传。适配器会自动处理此过程。

**自动降级：** 当媒体超过原生类型的限制但在 20 MB 的绝对文件限制内时，它会自动作为通用文件附件发送：

- 图片 > 10 MB → 作为文件发送
- 视频 > 10 MB → 作为文件发送
- 语音 > 2 MB → 作为文件发送
- 非 AMR 音频 → 作为文件发送 (企业微信原生语音仅支持 AMR)

超过 20 MB 绝对限制的文件将被拒绝，并向聊天窗口发送一条提示消息。

## 回复模式流式响应 {#reply-mode-stream-responses}

当 Agent 通过企业微信回调接收到消息时，适配器会记住入站请求 ID。如果在请求上下文仍处于活动状态时发送响应，适配器将使用企业微信的回复模式 (`aibot_respond_msg`) 并配合流式传输，将响应直接与入站消息关联。这在企业微信客户端中提供了更自然的对话体验。

如果入站请求上下文已过期或不可用，适配器将回退到通过 `aibot_send_msg` 主动发送消息。

回复模式也适用于媒体：上传的媒体可以作为对原始消息的回复发送。

## 连接与重连 {#connection-and-reconnection}

适配器维持一个到企业微信网关 `wss://openws.work.weixin.qq.com` 的持久 WebSocket 连接。

### 连接生命周期 {#connection-lifecycle}

1. **连接：** 开启 WebSocket 连接并发送包含 bot_id 和 secret 的 `aibot_subscribe` 认证帧。
2. **心跳：** 每 30 秒发送一次应用级 ping 帧以保持连接活跃。
3. **监听：** 持续读取入站帧并分发消息回调。
### 重连行为 {#reconnection-behavior}

当连接断开时，适配器会使用指数退避算法进行重连：

| 尝试次数 | 延迟时间 |
|---------|-------|
| 第 1 次重试 | 2 秒 |
| 第 2 次重试 | 5 秒 |
| 第 3 次重试 | 10 秒 |
| 第 4 次重试 | 30 秒 |
| 第 5 次及以后 | 60 秒 |

每次重连成功后，退避计数器都会重置为零。连接断开时，所有挂起的请求（futures）都会被标记为失败，以防止调用方无限期挂起。

### 去重机制 {#deduplication}

入站消息会根据消息 ID 进行去重，去重窗口为 5 分钟，缓存条目上限为 1000 条。这可以防止在重连或网络波动期间重复处理消息。

## 所有环境变量 {#all-environment-variables}

| 变量名 | 必填 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `WECOM_BOT_ID` | ✅ | — | 企业微信 AI Bot ID |
| `WECOM_SECRET` | ✅ | — | 企业微信 AI Bot Secret |
| `WECOM_ALLOWED_USERS` | — | _(空)_ | 网关级白名单，使用逗号分隔的用户 ID |
| `WECOM_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的会话 ID |
| `WECOM_WEBSOCKET_URL` | — | `wss://openws.work.weixin.qq.com` | WebSocket 网关 URL |
| `WECOM_DM_POLICY` | — | `open` | 私聊访问策略 |
| `WECOM_GROUP_POLICY` | — | `open` | 群聊访问策略 |

## 故障排除 {#troubleshooting}

| 问题 | 解决方法 |
|---------|-----|
| `WECOM_BOT_ID and WECOM_SECRET are required` | 设置这两个环境变量，或在设置向导中进行配置 |
| `WeCom startup failed: aiohttp not installed` | 安装 aiohttp：`pip install aiohttp` |
| `WeCom startup failed: httpx not installed` | 安装 httpx：`pip install httpx` |
| `invalid secret (errcode=40013)` | 验证 secret 是否与你的 Bot 凭据匹配 |
| `Timed out waiting for subscribe acknowledgement` | 检查到 `openws.work.weixin.qq.com` 的网络连接 |
| Agent 在群聊中不响应 | 检查 `group_policy` 设置，并确保群组 ID 在 `group_allow_from` 中 |
| Agent 在群聊中忽略某些用户 | 检查 `groups` 配置部分中每个群组对应的 `allow_from` 列表 |
| 媒体文件解密失败 | 安装 `cryptography`：`pip install cryptography` |
| `cryptography is required for WeCom media decryption` | 入站媒体文件经过 AES 加密。请安装：`pip install cryptography` |
| 语音消息以文件形式发送 | 企业微信原生语音仅支持 AMR 格式。其他格式会自动降级为文件发送。 |
| `File too large` 错误 | 企业微信对所有文件上传有 20 MB 的硬性限制。请压缩或拆分文件。 |
| 图片以文件形式发送 | 大于 10 MB 的图片超过了原生图片限制，会自动降级为文件附件发送。 |
| `Timeout sending message to WeCom` | WebSocket 可能已断开。请检查日志中的重连消息。 |
| `WeCom websocket closed during authentication` | 网络问题或凭据错误。请验证 bot_id 和 secret。 |
