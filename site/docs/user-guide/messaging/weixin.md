---
sidebar_position: 15
title: "微信"
description: "通过 iLink Bot API 将 Hermes Agent 连接到个人微信账号"
---

# 微信 {#weixin-wechat}

将 Hermes 连接到 Tencent 的个人消息平台 [微信](https://weixin.qq.com/)。该适配器使用 Tencent 的 **iLink Bot API** 连接个人微信账号 —— 这与 WeCom（企业微信）不同。消息通过长轮询传递，因此无需公共端点或 webhook。

:::info
此适配器适用于**个人微信账号**（微信）。如果你需要企业/公司微信，请查看 [WeCom 适配器](./wecom.md)。
:::

:::warning iLink 机器人身份——普通微信群可能无法工作
通过二维码登录会将 Hermes 连接到一个 **iLink 机器人身份**（例如 `a5ace6fd482e@im.bot`），**而不是**一个完全可编程的普通个人微信账号。后果如下：

- iLink 机器人身份通常**无法像普通联系人那样被邀请进普通微信群**。
<a id="ilink-bot-identity-ordinary-wechat-groups-may-not-work"></a>
- iLink 通常**不会向网关发送普通微信群事件**（包括对用于二维码登录的个人账号的 `@` 提及），对大多数机器人类型的账号来说。
- **@提及**扫描二维码的个人微信账号**不等同于** @提及 iLink 机器人 —— 机器人是一个独立的身份。
- 下面的 `WEIXIN_GROUP_POLICY` / `WEIXIN_GROUP_ALLOWED_USERS` 设置仅在 iLink 实际返回你账号类型的群事件时才生效。如果它不返回，无论策略如何，群消息都不会到达 Hermes。

实践中，大多数部署只能让 iLink 机器人的私聊消息可靠工作。如果配置后群消息仍然无法送达，那是 iLink 端的限制，而不是 Hermes 的问题。当 `WEIXIN_GROUP_POLICY` 设置为非 `disabled` 的值时，网关会在启动时记录一条 `WARNING` 日志。
:::

## 前提条件 {#prerequisites}

- 一个个人微信账号
- Python 包：`aiohttp` 和 `cryptography`
- 如果 Hermes 安装时使用了 `messaging` 扩展，则包含终端二维码渲染功能

安装所需依赖：

```bash
pip install aiohttp cryptography
# 可选：用于终端二维码显示
pip install hermes-agent[messaging]
```

## 设置 {#setup}

### 1. 运行设置向导 {#1-run-the-setup-wizard}

连接微信账号最简单的方式是通过交互式设置：

```bash
hermes gateway setup
```

在提示时选择 **Weixin**。向导将：

1. 向 iLink Bot API 请求一个二维码
2. 在终端显示二维码（或提供 URL）
3. 等待你用微信手机应用扫描二维码
4. 提示你在手机上确认登录
5. 自动将账号凭据保存到 `~/.hermes/weixin/accounts/`

确认后，你将看到类似这样的消息：

```
微信连接成功，account_id=your-account-id
```

向导会保存 `account_id`、`token` 和 `base_url`，因此你无需手动配置它们。

### 2. 配置环境变量 {#2-configure-environment-variables}

初始二维码登录后，至少在 `~/.hermes/.env` 中设置账号 ID：

```bash
WEIXIN_ACCOUNT_ID=your-account-id

# 可选：覆盖 token（通常从二维码登录自动保存）
# WEIXIN_TOKEN=your-bot-token

# 可选：限制访问
WEIXIN_DM_POLICY=open
WEIXIN_ALLOWED_USERS=user_id_1,user_id_2

# 可选：恢复旧版多行拆分行为
# WEIXIN_SPLIT_MULTILINE_MESSAGES=true

# 可选：用于 cron/通知的家庭频道
WEIXIN_HOME_CHANNEL=chat_id
WEIXIN_HOME_CHANNEL_NAME=Home
```
### 3. 启动网关 {#3-start-the-gateway}

```bash
hermes gateway
```

适配器会恢复已保存的凭证，连接到 iLink API，并开始长轮询消息。

## 功能特性 {#features}

- **长轮询传输** — 无需公共端点、Webhook 或 WebSocket
- **二维码登录** — 通过 `hermes gateway setup` 扫码连接
- **私聊消息** — 可配置的访问策略；群聊消息取决于 iLink 是否实际为已连接的身份传递群事件（iLink 机器人账号通常不会传递群事件——请参见上面的警告）
- **媒体支持** — 图片、视频、文件和语音消息
- **AES-128-ECB 加密 CDN** — 所有媒体传输自动加密/解密
- **上下文令牌持久化** — 重启后基于磁盘的回复连续性
- **Markdown 格式** — 保留 Markdown，包括标题、表格和代码块，因此支持 Markdown 的微信客户端可以原生渲染
- **智能消息分块** — 消息在限制长度内保持为单个气泡；仅超长内容在逻辑边界处拆分
- **输入状态指示** — 在 Agent 处理时，微信客户端显示“正在输入…”状态
- **SSRF 防护** — 出站媒体 URL 在下载前经过验证
- **消息去重** — 5 分钟滑动窗口防止重复处理
- **自动重试与退避** — 从临时 API 错误中恢复

## 配置选项 {#configuration-options}

在 `config.yaml` 的 `platforms.weixin.extra` 下设置：

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `account_id` | — | iLink Bot 账号 ID（必填） |
| `token` | — | iLink Bot 令牌（必填，从二维码登录自动保存） |
| `base_url` | `https://ilinkai.weixin.qq.com` | iLink API 基础 URL |
| `cdn_base_url` | `https://novac2c.cdn.weixin.qq.com/c2c` | 媒体传输的 CDN 基础 URL |
| `dm_policy` | `open` | 私聊访问：`open`、`allowlist`、`disabled`、`pairing` |
| `group_policy` | `disabled` | 群聊访问：`open`、`allowlist`、`disabled` |
| `allow_from` | `[]` | 允许私聊的用户 ID（当 dm_policy=allowlist 时） |
| `group_allow_from` | `[]` | 允许的群 ID（当 group_policy=allowlist 时） |
| `split_multiline_messages` | `false` | 当为 `true` 时，将多行回复拆分为多条聊天消息（旧行为）。当为 `false` 时，除非超过长度限制，否则将多行回复保留为一条消息。 |

## 访问策略 {#access-policies}

### 私聊策略 {#dm-policy}

控制谁可以向机器人发送私聊消息：

| 值 | 行为 |
|-------|----------|
| `open` | 任何人都可以向机器人发送私聊（默认） |
| `allowlist` | 只有 `allow_from` 中的用户 ID 可以发送私聊 |
| `disabled` | 忽略所有私聊 |
| `pairing` | 配对模式（用于初始设置） |

```bash
WEIXIN_DM_POLICY=allowlist
WEIXIN_ALLOWED_USERS=user_id_1,user_id_2
```

### 群聊策略 {#group-policy}

控制当 iLink 为已连接的身份传递群事件时，机器人在哪些群中响应。对于通过二维码登录的 iLink 机器人身份（例如 `...@im.bot`），群事件通常根本不会传递，因此此策略可能无效——请参见页面顶部的 iLink 机器人限制警告。
| 值 | 行为 |
|-------|----------|
| `open` | 机器人在所有群组中响应（如果事件被投递） |
| `allowlist` | 机器人仅响应 `group_allow_from` 中列出的群组 ID（如果事件被投递） |
| `disabled` | 忽略所有群消息（默认） |

```bash
WEIXIN_GROUP_POLICY=allowlist
# 注意：这是一个以逗号分隔的群聊 ID 列表，不是成员用户 ID，
# 尽管变量名中包含 "USERS"。配置时请牢记这一点。
WEIXIN_GROUP_ALLOWED_USERS=group_id_1,group_id_2
```

:::note
微信的默认群组策略是 `disabled`（与企业微信不同，后者默认为 `open`）。这是有意为之——个人微信账号可能加入许多群组，而 iLink 机器人身份通常根本无法接收普通微信群消息。如果你将 `WEIXIN_GROUP_POLICY` 设置为 `disabled` 以外的任何值，网关会在启动时记录一条 `WARNING` 日志。
:::

## 媒体支持 {#media-support}

### 入站（接收） {#inbound-receiving}

适配器从用户处接收媒体附件，从微信 CDN 下载，解密，并本地缓存以供 Agent 处理：

| 类型 | 处理方式 |
|------|-----------------| 
| **图片** | 下载，AES 解密，并缓存为 JPEG 格式。 |
| **视频** | 下载，AES 解密，并缓存为 MP4 格式。 |
| **文件** | 下载，AES 解密，并缓存。保留原始文件名。 |
| **语音** | 如果有文本转录，则提取为文本。否则，下载并缓存音频（SILK 格式）。 |

**引用消息：** 也会提取来自引用（回复）消息的媒体，以便 Agent 了解用户正在回复的上下文。

### AES-128-ECB 加密 CDN {#aes-128-ecb-encrypted-cdn}

微信媒体文件通过加密 CDN 传输。适配器透明地处理此过程：

- **入站：** 使用 `encrypted_query_param` URL 从 CDN 下载加密媒体，然后使用消息负载中提供的每个文件密钥，通过 AES-128-ECB 解密。
- **出站：** 使用随机 AES-128-ECB 密钥在本地加密文件，上传到 CDN，并将加密引用包含在出站消息中。
- AES 密钥为 16 字节（128 位）。密钥可能以原始 base64 或十六进制编码形式到达——适配器支持两种格式。
- 这需要 `cryptography` Python 包。

无需配置——加密和解密自动进行。

### 出站（发送） {#outbound-sending}

| 方法 | 发送内容 |
|--------|--------------|
| `send` | 带有 Markdown 格式的文本消息 | 
| `send_image` / `send_image_file` | 原生图片消息（通过 CDN 上传） |
| `send_document` | 文件附件（通过 CDN 上传） |
| `send_video` | 视频消息（通过 CDN 上传） |

所有出站媒体都经过加密 CDN 上传流程：

1. 生成一个随机的 AES-128 密钥
2. 使用 AES-128-ECB + PKCS#7 填充加密文件
3. 从 iLink API 请求上传 URL（`getuploadurl`）
4. 将密文上传到 CDN
5. 使用加密媒体引用发送消息

## 上下文令牌持久化 {#context-token-persistence}
iLink Bot API 要求每条发给特定对端的出站消息都回传一个 `context_token`。适配器维护了一个基于磁盘的上下文令牌存储：

- 令牌按账户+对端保存到 `~/.hermes/weixin/accounts/&lt;account_id&gt;.context-tokens.json`
- 启动时，恢复之前保存的令牌
- 每条入站消息都会更新该发送者的存储令牌
- 出站消息自动包含最新的上下文令牌

这确保了即使网关重启也能保持回复连续性。

## Markdown 格式 {#markdown-formatting}

通过 iLink Bot API 连接的微信客户端可以直接渲染 Markdown，因此适配器保留 Markdown 而不重写它：

- **标题**保持为 Markdown 标题（`#`、`##`……）
- **表格**保持为 Markdown 表格
- **代码围栏**保持为围栏代码块
- **过多的空行**在围栏代码块外部被折叠为双换行

## 消息分块 {#message-chunking}

只要消息在平台限制内，就会作为单条聊天消息发送。只有超大的负载才会被拆分发送：

- 最大消息长度：**4000 字符**
- 低于限制的消息即使包含多个段落或换行也保持完整
- 超大消息在逻辑边界（段落、空行、代码围栏）处拆分
- 代码围栏尽可能保持完整（除非围栏本身超出限制，否则绝不从中间拆分）
- 超大的单个块回退到基础适配器的截断逻辑
- 发送多个分块时，0.3 秒的分块间延迟可防止微信速率限制丢消息

## 输入状态指示 {#typing-indicators}

适配器在微信客户端中显示输入状态：

1. 当消息到达时，适配器通过 `getconfig` API 获取一个 `typing_ticket`
2. 每个用户的输入票据缓存 10 分钟
3. `send_typing` 发送开始输入信号；`stop_typing` 发送停止输入信号
4. 网关在 Agent 处理消息时自动触发输入状态指示

## 长轮询连接 {#long-poll-connection}

适配器使用 HTTP 长轮询（而非 WebSocket）接收消息：

### 工作原理 {#how-it-works}

1. **连接：** 验证凭据并启动轮询循环
2. **轮询：** 调用 `getupdates`，超时时间为 35 秒；服务器保持请求直到消息到达或超时到期
3. **分发：** 入站消息通过 `asyncio.create_task` 并发分发
4. **同步缓冲区：** 持久化的同步游标（`get_updates_buf`）保存到磁盘，以便适配器重启后从正确位置恢复

### 重试行为 {#retry-behavior}

遇到 API 错误时，适配器使用简单的重试策略：

| 条件 | 行为 |
|-----------|----------|
| 临时错误（第1-2次） | 2秒后重试 |
| 重复错误（第3次及以上） | 退避30秒，然后重置计数器 |
| 会话过期（`errcode=-14`） | 暂停10分钟（可能需要重新登录） |
| 超时 | 立即重新轮询（正常长轮询行为） |

### 去重 {#deduplication}

入站消息使用消息 ID 进行去重，窗口为 5 分钟。这可以防止在网络波动或轮询响应重叠时重复处理。
### Token Lock（令牌锁定） {#token-lock}

同一时间，只有一个微信网关实例能使用指定的令牌。适配器启动时会获取一个范围内锁，并在关闭时释放。如果另一个网关已经在使用同一个令牌，启动将失败，并显示明确的错误信息。

## 所有环境变量 {#all-environment-variables}

| 变量 | 必填 | 默认值 | 说明 |
|----------|---------|-------------|---------|
| `WEIXIN_ACCOUNT_ID` | ✅ | — | iLink Bot 账户 ID（来自扫码登录） |
| `WEIXIN_TOKEN` | ✅ | — | iLink Bot 令牌（扫码登录后自动保存） |
| `WEIXIN_BASE_URL` | — | `https://ilinkai.weixin.qq.com` | iLink API 基础 URL |
| `WEIXIN_CDN_BASE_URL` | — | `https://novac2c.cdn.weixin.qq.com/c2c` | 媒体传输的 CDN 基础 URL |
| `WEIXIN_DM_POLICY` | — | `open` | 私信访问策略：`open`、`allowlist`、`disabled`、`pairing` |
| `WEIXIN_GROUP_POLICY` | — | `disabled` | 群组访问策略：`open`、`allowlist`、`disabled` |
| `WEIXIN_ALLOWED_USERS` | — | _(空)_ | 私信白名单中用逗号分隔的用户 ID |
| `WEIXIN_GROUP_ALLOWED_USERS` | — | _(空)_ | 群组白名单中用逗号分隔的**群聊 ID**（不是成员用户 ID）。变量名称是历史遗留——它期望的是群组 ID，而不是用户 ID。 |
| `WEIXIN_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天 ID |
| `WEIXIN_HOME_CHANNEL_NAME` | — | `Home` | 主页频道的显示名称 |
| `WEIXIN_ALLOW_ALL_USERS` | — | — | 网关级标志，允许所有用户（由设置向导使用） |

## 故障排除 {#troubleshooting}

| 问题 | 解决 |
|---------|-----|
| `Weixin startup failed: aiohttp and cryptography are required` | 安装这两个包：`pip install aiohttp cryptography` |
| `Weixin startup failed: WEIXIN_TOKEN is required` | 运行 `hermes gateway setup` 完成扫码登录，或手动设置 `WEIXIN_TOKEN` |
| `Weixin startup failed: WEIXIN_ACCOUNT_ID is required` | 在 `.env` 中设置 `WEIXIN_ACCOUNT_ID`，或运行 `hermes gateway setup` |
| `Another local Hermes gateway is already using this Weixin token` | 先停止另一个网关实例——每个令牌只允许一个轮询器 |
| 会话过期 (`errcode=-14`) | 你的登录会话已过期。重新运行 `hermes gateway setup` 扫描新的二维码 |
| 设置期间二维码过期 | 二维码最多自动刷新 3 次。如果仍然过期，请检查你的网络连接 |
| Bot 不回复私信 | 检查 `WEIXIN_DM_POLICY`——如果设置为 `allowlist`，发送者必须位于 `WEIXIN_ALLOWED_USERS` 中 |
| Bot 忽略群消息 | 群组策略默认为 `disabled`。请设置 `WEIXIN_GROUP_POLICY=open` 或 `allowlist`——但请注意，通过扫码登录的 iLink bot 身份标识（`...@im.bot`）通常根本无法接收普通的微信群消息。如果网关日志显示没有原始的群消息入站事件，则限制在 iLink 侧，而非 Hermes。 |
| 媒体下载/上传失败 | 确保已安装 `cryptography`。检查对 `novac2c.cdn.weixin.qq.com` 的网络访问 |
| `Blocked unsafe URL (SSRF protection)` | 出站媒体 URL 指向私有/内部地址。只允许公共 URL |
| 语音消息显示为文本 | 如果微信提供了转写文本，适配器会使用文本。这是预期行为 |
| 消息出现重复 | 适配器按消息 ID 去重。如果看到重复，请检查是否有多个网关实例在运行 |
| `iLink POST ... HTTP 4xx/5xx` | iLink 服务返回的 API 错误。检查你的令牌有效性和网络连接 |
| 终端二维码无法渲染 | 通过 messaging extra 重新安装：`pip install hermes-agent[messaging]`。或者，打开二维码上方打印的 URL |
