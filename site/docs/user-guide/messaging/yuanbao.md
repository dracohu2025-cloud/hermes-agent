---
sidebar_position: 16
title: "Yuanbao"
description: "通过 WebSocket 网关将 Hermes Agent 连接到企业级消息平台 Yuanbao"
---

# Yuanbao {#yuanbao}

将 Hermes 连接到腾讯的企业级消息平台 [Yuanbao](https://yuanbao.tencent.com/)。该适配器使用 WebSocket 网关实现实时消息投递，并支持单聊（C2C）和群聊。

:::info
Yuanbao 是一个主要在企业内部和腾讯内部使用的企业级消息平台。它使用 WebSocket 进行实时通信，采用基于 HMAC 的身份验证，并支持图片、文件和语音消息等富媒体。
:::

## 前提条件 {#prerequisites}

- 一个具有机器人创建权限的 Yuanbao 账号
- Yuanbao 的 APP_ID 和 APP_SECRET（从平台管理员处获取）
- Python 包：`websockets` 和 `httpx`
- 如需媒体支持：`aiofiles`

安装所需依赖：

```bash
pip install websockets httpx aiofiles
```

## 设置 {#setup}

### 1. 在 Yuanbao 中创建机器人 {#1-create-a-bot-in-yuanbao}

1. 从 [https://yuanbao.tencent.com/](https://yuanbao.tencent.com/) 下载 Yuanbao 应用
2. 在应用中，进入 **PAI → 我的机器人** 并创建一个新机器人
3. 创建机器人后，复制 **APP_ID** 和 **APP_SECRET**

### 2. 运行设置向导 {#2-run-the-setup-wizard}

配置 Yuanbao 最简单的方式是通过交互式设置：

```bash
hermes gateway setup
```

在提示时选择 **Yuanbao**。向导将：

1. 询问你的 APP_ID
2. 询问你的 APP_SECRET
3. 自动保存配置

:::tip
WebSocket URL 和 API 域名已内置合理的默认值。你只需提供 APP_ID 和 APP_SECRET 即可开始使用。
:::

### 3. 配置环境变量 {#3-configure-environment-variables}

初始设置完成后，请验证 `~/.hermes/.env` 中的这些变量：

```bash
# 必填
YUANBAO_APP_ID=your-app-id
YUANBAO_APP_SECRET=your-app-secret
YUANBAO_WS_URL=wss://api.yuanbao.example.com/ws
YUANBAO_API_DOMAIN=https://api.yuanbao.example.com

# 可选：机器人账号 ID（通常从 sign-token 自动获取）
# YUANBAO_BOT_ID=your-bot-id

# 可选：内部路由环境（例如 test/staging/production）
# YUANBAO_ROUTE_ENV=production

# 可选：用于定时任务/通知的主频道（格式：direct:<账号> 或 group:<群组代码>）
YUANBAO_HOME_CHANNEL=direct:bot_account_id
YUANBAO_HOME_CHANNEL_NAME="机器人通知"

# 可选：限制访问（旧版，请参阅下面的访问控制以获取细粒度策略）
YUANBAO_ALLOWED_USERS=user_account_1,user_account_2
```

### 4. 启动网关 {#4-start-the-gateway}

```bash
hermes gateway
```

适配器将连接到 Yuanbao WebSocket 网关，使用 HMAC 签名进行身份验证，并开始处理消息。

## 功能特性 {#features}

- **WebSocket 网关** — 实时双向通信
- **HMAC 身份验证** — 使用 APP_ID/APP_SECRET 进行安全的请求签名
- **C2C 消息** — 用户与机器人之间的直接对话
- **群组消息** — 群聊中的对话
- **媒体支持** — 通过 COS（云对象存储）支持图片、文件和语音消息
- **Markdown 格式化** — 消息会自动分块以适应 Yuanbao 的大小限制
- **消息去重** — 防止同一消息被重复处理
- **心跳/保活** — 维持 WebSocket 连接稳定性
- **输入状态指示** — 在 Agent 处理时显示“正在输入…”状态
- **自动重连** — 处理 WebSocket 断开连接，并采用指数退避策略
- **群组信息查询** — 获取群组详情和成员列表
- **贴纸/表情支持** — 在对话中发送 TIMFaceElem 贴纸和表情
- **自动设置主频道** — 第一个向机器人发送消息的用户会被自动设置为主频道所有者
- **慢响应通知** — 当 Agent 处理时间超过预期时，发送等待消息
## Configuration Options {#configuration-options}

### Chat ID 格式 {#chat-id-formats}

Yuanbao 根据对话类型使用带前缀的标识符：

| 聊天类型 | 格式 | 示例 |
|-----------|--------|---------|
| 私聊 (C2C) | `direct:&lt;account&gt;` | `direct:user123` |
| 群聊 | `group:&lt;group_code&gt;` | `group:grp456` |

### 媒体上传 {#media-uploads}

Yuanbao 适配器会自动通过 COS（腾讯云对象存储）处理媒体上传：

- **图片**：支持 JPEG、PNG、GIF、WebP
- **文件**：支持所有常见文档类型
- **语音**：支持 WAV、MP3、OGG

媒体 URL 在上传前会自动验证并下载，以防止 SSRF 攻击。

## 首页频道 {#home-channel}

在任何 Yuanbao 聊天（私聊或群聊）中使用 `/sethome` 命令将其指定为**首页频道**。定时任务（cron 作业）会将结果投递到此频道。

:::tip 自动设置首页
如果没有配置首页频道，第一个与机器人发消息的用户将自动被设置为首页频道所有者。如果当前首页频道是群聊，第一次私聊将会将其升级为直接频道。
:::

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
YUANBAO_HOME_CHANNEL=direct:user_account_id
# 或用于群聊：
# YUANBAO_HOME_CHANNEL=group:group_code
<a id="auto-sethome"></a>
YUANBAO_HOME_CHANNEL_NAME="我的机器人更新"
```

### 示例：设置首页频道 {#example-set-home-channel}

1. 在 Yuanbao 中与机器人开始对话
2. 发送命令：`/sethome`
3. 机器人回复：“首页频道已设置为 [chat_name]，ID 为 [chat_id]。Cron 作业将投递到此位置。”
4. 未来的 cron 作业和通知将发送到此频道

### 示例：Cron 作业投递 {#example-cron-job-delivery}

创建一个 cron 作业：

```bash
/cron "0 9 * * *" Check server status
```

定时输出将在每天上午 9 点投递到你的 Yuanbao 首页频道。

## 使用提示 {#usage-tips}

### 开始对话 {#starting-a-conversation}

在 Yuanbao 中向机器人发送任意消息：

```
hello
```

机器人会在同一对话线程中回复。

### 可用命令 {#available-commands}

所有标准 Hermes 命令均可在 Yuanbao 上使用：

| 命令 | 描述 |
|---------|-------------|
| `/new` | 开始一次新的对话 |
| `/model [provider:model]` | 显示或更改模型 |
| `/sethome` | 将此聊天设置为首页频道 |
| `/status` | 显示会话信息 |
| `/help` | 显示可用命令 |

### 发送文件 {#sending-files}

要向机器人发送文件，只需在 Yuanbao 聊天中直接附加文件即可。机器人会自动下载并处理文件附件。

你也可以在附件中包含一条消息：

```
Please analyze this document
```

### 接收文件 {#receiving-files}

当你要求机器人创建或导出文件时，它会直接将文件发送到你的 Yuanbao 聊天中。

## 故障排除 {#troubleshooting}

### 机器人在线但未响应消息 {#bot-is-online-but-not-responding-to-messages}

**原因**：WebSocket 握手期间身份验证失败。

**解决方法**：
1. 确认 APP_ID 和 APP_SECRET 正确
2. 检查 WebSocket URL 是否可访问
3. 确保机器人账户具有适当的权限
4. 查看网关日志：`tail -f ~/.hermes/logs/gateway.log`

### "Connection refused" 错误 {#connection-refused-error}
**原因**：WebSocket URL 不可达或地址错误。

**修复方法**：
1. 确认 WebSocket URL 格式（应以 `wss://` 开头）
2. 检查到 Yuanbao API 域名的网络连通性
3. 确认防火墙允许 WebSocket 连接
4. 使用以下命令测试 URL：`curl -I https://[YUANBAO_API_DOMAIN]`

### 媒体上传失败 {#media-uploads-fail}

**原因**：COS 凭证无效或媒体服务器不可达。

**修复方法**：
1. 确认 API_DOMAIN 正确
2. 检查机器人是否已开启媒体上传权限
3. 确保媒体文件可访问且未损坏
4. 联系平台管理员检查 COS 存储桶配置

### 消息未送达 home 频道 {#messages-not-delivered-to-home-channel}

**原因**：Home 频道 ID 格式错误，或定时任务未触发。

**修复方法**：
1. 确认 YUANBAO_HOME_CHANNEL 格式正确
2. 使用 `/sethome` 命令自动检测正确格式
3. 使用 `/status` 检查定时任务计划
4. 确认机器人在目标群聊中有发送权限

### 频繁断连 {#frequent-disconnections}

**原因**：WebSocket 连接不稳定或网络不可靠。

**修复方法**：
1. 检查网关日志中的错误模式
2. 在连接设置中增加心跳超时时间
3. 确保与 Yuanbao API 的网络连接稳定
4. 可考虑启用详细日志：`HERMES_LOG_LEVEL=debug`

## 访问控制 {#access-control}

Yuanbao 支持对私聊和群聊进行精细的访问控制：

```bash
# DM 策略：open（默认）| allowlist | disabled
YUANBAO_DM_POLICY=open
# 允许 DM 机器人的用户 ID 列表（仅当 DM_POLICY=allowlist 时生效）
YUANBAO_DM_ALLOW_FROM=user_id_1,user_id_2

# 群聊策略：open（默认）| allowlist | disabled
YUANBAO_GROUP_POLICY=open
# 允许的群组 code 列表（仅当 GROUP_POLICY=allowlist 时生效）
YUANBAO_GROUP_ALLOW_FROM=group_code_1,group_code_2
```

也可以在 `config.yaml` 中设置：

```yaml
platforms:
  yuanbao:
    extra:
      dm_policy: allowlist
      dm_allow_from: "user1,user2"
      group_policy: open
      group_allow_from: ""
```

## 高级配置 {#advanced-configuration}

### 消息分块 {#message-chunking}

Yuanbao 有最大消息长度限制。Hermes 会自动对大响应进行分块，且在分块时能识别 Markdown 格式（会尊重代码块、表格和段落边界）。

### 连接参数 {#connection-parameters}

以下连接参数已内置到 adapter 中，并带有合理的默认值：

| 参数 | 默认值 | 说明 |
|-----------|---------------|-------------|
| WebSocket 连接超时 | 15 秒 | 等待 WS 握手完成的时间 |
| 心跳间隔 | 30 秒 | 保持连接活跃的 ping 频率 |
| 最大重连次数 | 100 | 最大重连尝试次数 |
| 重连回退 | 1 秒 → 60 秒（指数级） | 重连尝试之间的等待时间 |
| 回复心跳间隔 | 2 秒 | RUNNING 状态发送频率 |
| 发送超时 | 30 秒 | 出站 WS 消息的超时时间 |

:::note
这些值目前无法通过环境变量配置。它们已针对典型的 Yuanbao 部署进行了优化。
:::
### 详细日志 {#verbose-logging}

启用调试日志以排查连接问题：

```bash
HERMES_LOG_LEVEL=debug hermes gateway
```

## 与其他功能的集成 {#integration-with-other-features}

### 定时任务 {#cron-jobs}

在 Yuanbao 上调度运行的任务：

```
/cron "0 */4 * * *" 报告系统健康状态
```

结果会发送到你的主频道。

### 后台任务 {#background-tasks}

在不阻塞对话的情况下运行耗时操作：

```
/background 分析存档中的所有文件
```

### 跨平台消息 {#cross-platform-messages}

从 CLI 向 Yuanbao 发送消息：

```bash
hermes chat -q "Send 'Hello from CLI' to yuanbao:group:group_code"
```

## 相关文档 {#related-documentation}

- [消息网关概览](./index.md)
- [斜杠命令参考](/reference/slash-commands.md)
- [定时任务](/user-guide/features/cron.md)
- [后台会话](/user-guide/cli#background-sessions)