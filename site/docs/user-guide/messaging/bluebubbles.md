# BlueBubbles (iMessage) {#bluebubbles-imessage}

通过 [BlueBubbles](https://bluebubbles.app/) 将 Hermes 连接到 Apple iMessage——这是一个免费、开源的 macOS 服务器，能将 iMessage 桥接到任何设备。

## 前提条件 {#prerequisites}

- 一台 **Mac**（始终保持开机）并运行 [BlueBubbles Server](https://bluebubbles.app/)
- 在该 Mac 的 Messages.app 中登录了 Apple ID
- BlueBubbles Server v1.0.0 或更高版本（Webhook 需要此版本）
- Hermes 与 BlueBubbles 服务器之间的网络连通性

## 设置 {#setup}

### 1. 安装 BlueBubbles Server {#1-install-bluebubbles-server}

从 [bluebubbles.app](https://bluebubbles.app/) 下载并安装。完成设置向导——使用你的 Apple ID 登录，并配置连接方式（本地网络、Ngrok、Cloudflare 或动态 DNS）。

### 2. 获取服务器 URL 和密码 {#2-get-your-server-url-and-password}

在 BlueBubbles Server → **设置 → API** 中，记下：
- **服务器 URL**（例如 `http://192.168.1.10:1234`）
- **服务器密码**

### 3. 配置 Hermes {#3-configure-hermes}

运行设置向导：

```bash
hermes gateway setup
```

选择 **BlueBubbles (iMessage)** 并输入你的服务器 URL 和密码。

或者直接在 `~/.hermes/.env` 中设置环境变量：

```bash
BLUEBUBBLES_SERVER_URL=http://192.168.1.10:1234
BLUEBUBBLES_PASSWORD=your-server-password
```

### 4. 授权用户 {#4-authorize-users}

选择一种方式：

**DM 配对（推荐）：**
当有人给你的 iMessage 发消息时，Hermes 会自动向他们发送一个配对码。使用以下命令批准：
```bash
hermes pairing approve bluebubbles <CODE>
```
使用 `hermes pairing list` 查看待处理的配对码和已批准的用户。

**预授权特定用户**（在 `~/.hermes/.env` 中）：
```bash
BLUEBUBBLES_ALLOWED_USERS=user@icloud.com,+15551234567
```

**开放访问**（在 `~/.hermes/.env` 中）：
```bash
BLUEBUBBLES_ALLOW_ALL_USERS=true
```

### 5. 启动网关 {#5-start-the-gateway}

```bash
hermes gateway run
```

Hermes 将连接到你的 BlueBubbles 服务器，注册一个 Webhook，并开始监听 iMessage 消息。

## 工作原理 {#how-it-works}

```
iMessage → Messages.app → BlueBubbles Server → Webhook → Hermes
Hermes → BlueBubbles REST API → Messages.app → iMessage
```

- **入站：** 当新消息到达时，BlueBubbles 将 Webhook 事件发送到本地监听器。无需轮询——即时送达。
- **出站：** Hermes 通过 BlueBubbles REST API 发送消息。
- **媒体：** 支持双向传输图片、语音消息、视频和文档。入站附件会被下载并本地缓存，供 Agent 处理。

## 环境变量 {#environment-variables}

| 变量 | 必填 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `BLUEBUBBLES_SERVER_URL` | 是 | — | BlueBubbles 服务器 URL |
| `BLUEBUBBLES_PASSWORD` | 是 | — | 服务器密码 |
| `BLUEBUBBLES_WEBHOOK_HOST` | 否 | `127.0.0.1` | Webhook 监听器绑定地址 |
| `BLUEBUBBLES_WEBHOOK_PORT` | 否 | `8645` | Webhook 监听器端口 |
| `BLUEBUBBLES_WEBHOOK_PATH` | 否 | `/bluebubbles-webhook` | Webhook URL 路径 |
| `BLUEBUBBLES_HOME_CHANNEL` | 否 | — | 用于定时投递的电话/邮箱 |
| `BLUEBUBBLES_ALLOWED_USERS` | 否 | — | 逗号分隔的已授权用户 |
| `BLUEBUBBLES_ALLOW_ALL_USERS` | 否 | `false` | 允许所有用户 |
自动标记已读消息由 `~/.hermes/config.yaml` 中 `platforms.bluebubbles.extra` 下的 `send_read_receipts` 键控制（默认值：`true`）。没有对应的环境变量。

## 功能特性 {#features}

### 文本消息 {#text-messaging}
发送和接收 iMessage。Markdown 格式会被自动去除，以纯文本形式清晰投递。

### 富媒体 {#rich-media}
- **图片：** 照片会原生显示在 iMessage 对话中
- **语音消息：** 音频文件作为 iMessage 语音消息发送
- **视频：** 视频附件
- **文档：** 文件作为 iMessage 附件发送

### Tapback 反应 {#tapback-reactions}
支持喜欢、点赞、不喜欢、大笑、强调和疑问等反应。需要 BlueBubbles [Private API 助手](https://docs.bluebubbles.app/helper-bundle/installation)。

### 输入指示器 {#typing-indicators}
在 Agent 处理消息时，iMessage 对话中会显示“正在输入...”。需要 Private API。

### 已读回执 {#read-receipts}
处理消息后自动标记为已读。需要 Private API。

### 聊天地址 {#chat-addressing}
你可以通过邮箱或手机号来指定聊天对象——Hermes 会自动将其解析为 BlueBubbles 的聊天 GUID。无需使用原始的 GUID 格式。

## Private API {#private-api}

部分功能需要 BlueBubbles [Private API 助手](https://docs.bluebubbles.app/helper-bundle/installation)：
- Tapback 反应
- 输入指示器
- 已读回执
- 通过地址创建新聊天

没有 Private API 时，基本的文本消息和媒体功能仍然可用。

## 故障排除 {#troubleshooting}

### “无法连接服务器” {#cannot-reach-server}
- 确认服务器 URL 正确且 Mac 已开机
- 检查 BlueBubbles 服务器是否正在运行
- 确保网络连接正常（防火墙、端口转发）

### 消息未到达 {#messages-not-arriving}
- 检查 webhook 是否已在 BlueBubbles 服务器 → 设置 → API → Webhooks 中注册
- 确认 Mac 可以访问 webhook URL
- 运行 `hermes logs gateway` 查看 webhook 错误（或使用 `hermes logs -f` 实时跟踪）

### “Private API 助手未连接” {#private-api-helper-not-connected}
- 安装 Private API 助手：[docs.bluebubbles.app](https://docs.bluebubbles.app/helper-bundle/installation)
- 没有它，基本消息功能仍可正常使用——只有反应、输入指示器和已读回执需要它
