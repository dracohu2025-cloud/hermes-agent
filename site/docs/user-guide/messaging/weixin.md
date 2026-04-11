---
sidebar_position: 15
title: "微信 (WeChat)"
description: "通过 iLink Bot API 将 Hermes Agent 连接到个人微信账号"
---

# 微信 (WeChat)

将 Hermes 连接到腾讯的个人消息平台 [微信](https://weixin.qq.com/)。此适配器使用腾讯的 **iLink Bot API** 来支持个人微信账号——这与企业微信 (WeCom) 不同。消息通过长轮询 (long-polling) 传递，因此无需公共端点或 Webhook。

:::info
此适配器仅适用于**个人微信账号**。如果您需要企业微信，请参阅 [企业微信适配器](./wecom.md)。
:::

## 前置要求

- 一个个人微信账号
- Python 包：`aiohttp` 和 `cryptography`
- `qrcode` 包是可选的（用于设置期间在终端渲染二维码）

安装所需的依赖项：

```bash
pip install aiohttp cryptography
# 可选：用于在终端显示二维码
pip install qrcode
```

## 设置

### 1. 运行设置向导

连接微信账号最简单的方法是通过交互式设置：

```bash
hermes gateway setup
```

在提示时选择 **Weixin**。向导将执行以下操作：

1. 从 iLink Bot API 请求二维码
2. 在终端显示二维码（或提供 URL）
3. 等待您使用微信手机客户端扫描二维码
4. 提示您在手机上确认登录
5. 自动将账号凭据保存到 `~/.hermes/weixin/accounts/`

确认后，您将看到如下消息：

```
微信连接成功，account_id=your-account-id
```

向导会自动存储 `account_id`、`token` 和 `base_url`，因此您无需手动配置它们。

### 2. 配置环境变量

首次通过二维码登录后，请至少在 `~/.hermes/.env` 中设置账号 ID：

```bash
WEIXIN_ACCOUNT_ID=your-account-id

# 可选：覆盖 token（通常由二维码登录自动保存）
# WEIXIN_TOKEN=your-bot-token

# 可选：限制访问
WEIXIN_DM_POLICY=open
WEIXIN_ALLOWED_USERS=user_id_1,user_id_2

# 可选：用于定时任务/通知的主频道
WEIXIN_HOME_CHANNEL=chat_id
WEIXIN_HOME_CHANNEL_NAME=Home
```

### 3. 启动网关

```bash
hermes gateway
```

适配器将恢复已保存的凭据，连接到 iLink API，并开始对消息进行长轮询。

## 功能特性

- **长轮询传输** — 无需公共端点、Webhook 或 WebSocket
- **二维码登录** — 通过 `hermes gateway setup` 扫码连接
- **私聊和群聊** — 可配置的访问策略
- **媒体支持** — 图片、视频、文件和语音消息
- **AES-128-ECB 加密 CDN** — 所有媒体传输均自动加密/解密
- **上下文 Token 持久化** — 基于磁盘的回复连续性，重启后依然有效
- **Markdown 格式化** — 标题、表格和代码块会重新格式化以适配微信阅读
- **智能消息分段** — 长消息会在逻辑边界（段落、代码块）处拆分
- **输入状态指示** — 当 Agent 处理消息时，在微信客户端显示“对方正在输入...”状态
- **SSRF 防护** — 出站媒体 URL 在下载前会经过验证
- **消息去重** — 5 分钟滑动窗口防止重复处理
- **自动重试与退避** — 从瞬时 API 错误中自动恢复

## 配置选项

在 `config.yaml` 的 `platforms.weixin.extra` 下设置这些选项：

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `account_id` | — | iLink Bot 账号 ID（必填） |
| `token` | — | iLink Bot Token（必填，由二维码登录自动保存） |
| `base_url` | `https://ilinkai.weixin.qq.com` | iLink API 基础 URL |
| `cdn_base_url` | `https://novac2c.cdn.weixin.qq.com/c2c` | 媒体传输的 CDN 基础 URL |
| `dm_policy` | `open` | 私聊访问策略：`open`, `allowlist`, `disabled`, `pairing` |
| `group_policy` | `disabled` | 群聊访问策略：`open`, `allowlist`, `disabled` |
| `allow_from` | `[]` | 允许私聊的用户 ID（当 dm_policy=allowlist 时） |
| `group_allow_from` | `[]` | 允许的群组 ID（当 group_policy=allowlist 时） |

## 访问策略

### 私聊策略 (DM Policy)

控制谁可以向机器人发送私聊消息：

| 值 | 行为 |
|-------|----------|
| `open` | 任何人都可以私聊机器人（默认） |
| `allowlist` | 仅 `allow_from` 中的用户 ID 可以私聊 |
| `disabled` | 忽略所有私聊消息 |
| `pairing` | 配对模式（用于初始设置） |

```bash
WEIXIN_DM_POLICY=allowlist
WEIXIN_ALLOWED_USERS=user_id_1,user_id_2
```

### 群聊策略 (Group Policy)

控制机器人在哪些群组中响应：

| 值 | 行为 |
|-------|----------|
| `open` | 机器人在所有群组中响应 |
| `allowlist` | 机器人仅在 `group_allow_from` 列出的群组 ID 中响应 |
| `disabled` | 忽略所有群消息（默认） |

```bash
WEIXIN_GROUP_POLICY=allowlist
WEIXIN_GROUP_ALLOWED_USERS=group_id_1,group_id_2
```

:::note
微信的默认群聊策略是 `disabled`（与企业微信默认 `open` 不同）。这是有意为之，因为个人微信账号可能加入了很多群组。
:::

## 媒体支持

### 入站（接收）

适配器接收来自用户的媒体附件，从微信 CDN 下载它们，解密并缓存到本地供 Agent 处理：

| 类型 | 处理方式 |
|------|-----------------| 
| **图片** | 下载、AES 解密并缓存为 JPEG。 |
| **视频** | 下载、AES 解密并缓存为 MP4。 |
| **文件** | 下载、AES 解密并缓存。保留原始文件名。 |
| **语音** | 如果有文本转录，则提取为文本。否则下载并缓存音频（SILK 格式）。 |

**引用消息：** 引用（回复）消息中的媒体也会被提取，以便 Agent 了解用户正在回复的内容。

### AES-128-ECB 加密 CDN

微信媒体文件通过加密的 CDN 传输。适配器会透明地处理此过程：

- **入站：** 使用 `encrypted_query_param` URL 从 CDN 下载加密媒体，然后使用消息负载中提供的每个文件对应的密钥进行 AES-128-ECB 解密。
- **出站：** 文件在本地使用随机 AES-128-ECB 密钥加密，上传到 CDN，并将加密后的引用包含在出站消息中。
- AES 密钥为 16 字节（128 位）。密钥可能以原始 base64 或十六进制编码形式到达——适配器支持这两种格式。
- 这需要 `cryptography` Python 包。

无需任何配置——加密和解密会自动进行。

### 出站（发送）

| 方法 | 发送内容 |
|--------|--------------|
| `send` | 带有 Markdown 格式的文本消息 | 
| `send_image` / `send_image_file` | 原生图片消息（通过 CDN 上传） |
| `send_document` | 文件附件（通过 CDN 上传） |
| `send_video` | 视频消息（通过 CDN 上传） |

所有出站媒体都通过加密的 CDN 上传流程：

1. 生成一个随机 AES-128 密钥
2. 使用 AES-128-ECB + PKCS#7 填充加密文件
3. 从 iLink API 请求上传 URL (`getuploadurl`)
4. 将密文上传到 CDN
5. 发送带有加密媒体引用的消息

## 上下文 Token 持久化

iLink Bot API 要求针对特定对等方（peer）的每条出站消息回传一个 `context_token`。适配器维护了一个基于磁盘的上下文 Token 存储：

- Token 按账号+对等方保存到 `~/.hermes/weixin/accounts/<account_id>.context-tokens.json`
- 启动时，会恢复之前保存的 Token
- 每条入站消息都会更新该发送者的存储 Token
- 出站消息会自动包含最新的上下文 Token

这确保了即使在网关重启后，回复依然具有连续性。

## Markdown 格式化

微信个人聊天不支持原生渲染完整的 Markdown。适配器会重新格式化内容以提高可读性：

- **标题** (`# Title`) → 转换为 `【Title】`（一级标题）或 `**Title**`（二级及以上标题）
- **表格** → 重新格式化为带标签的键值列表（例如 `- 列名: 值`）
- **代码块** → 原样保留（微信对代码块的渲染效果尚可）
- **多余空行** → 合并为双换行

## 消息分段

长消息会为聊天发送进行智能拆分：

- 最大消息长度：**4000 字符**
- 拆分点优先选择段落边界和空行
- 代码块保持完整（绝不会在块中间拆分）
- 缩进的续行（重新格式化后的表格/列表中的子项）会与父项保持在一起
- 超大的单个块会回退到基础适配器的截断逻辑
## Typing Indicators

适配器会在微信客户端显示输入状态：

1. 当收到消息时，适配器通过 `getconfig` API 获取 `typing_ticket`
2. 每个用户的 typing ticket 会缓存 10 分钟
3. `send_typing` 发送“正在输入”信号；`stop_typing` 发送“停止输入”信号
4. 当 Agent 处理消息时，网关会自动触发输入状态指示

## Long-Poll Connection

适配器使用 HTTP 长轮询（而非 WebSocket）来接收消息：

### 工作原理

1. **连接：** 验证凭据并启动轮询循环
2. **轮询：** 调用 `getupdates` 并设置 35 秒超时；服务器会保持请求，直到收到消息或超时
3. **分发：** 入站消息通过 `asyncio.create_task` 并发分发
4. **同步缓冲区：** 持久化同步游标 (`get_updates_buf`) 会保存到磁盘，以便适配器在重启后从正确的位置恢复

### 重试行为

遇到 API 错误时，适配器采用简单的重试策略：

| 条件 | 行为 |
|-----------|----------|
| 瞬时错误（第 1-2 次） | 2 秒后重试 |
| 重复错误（3 次以上） | 退避 30 秒，然后重置计数器 |
| 会话过期 (`errcode=-14`) | 暂停 10 分钟（可能需要重新登录） |
| 超时 | 立即重新轮询（正常的长轮询行为） |

### 去重

入站消息使用消息 ID 进行去重，窗口期为 5 分钟。这可以防止在网络抖动或轮询响应重叠时出现重复处理。

### Token 锁

同一时间只能有一个微信网关实例使用给定的 token。适配器在启动时获取作用域锁，并在关闭时释放。如果另一个网关已经在占用该 token，启动将失败并显示提示信息。

## 所有环境变量

| 变量 | 必填 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `WEIXIN_ACCOUNT_ID` | ✅ | — | iLink Bot 账号 ID（通过扫码登录获取） |
| `WEIXIN_TOKEN` | ✅ | — | iLink Bot token（扫码登录后自动保存） |
| `WEIXIN_BASE_URL` | — | `https://ilinkai.weixin.qq.com` | iLink API 基础 URL |
| `WEIXIN_CDN_BASE_URL` | — | `https://novac2c.cdn.weixin.qq.com/c2c` | 用于媒体传输的 CDN 基础 URL |
| `WEIXIN_DM_POLICY` | — | `open` | 私聊访问策略：`open`, `allowlist`, `disabled`, `pairing` |
| `WEIXIN_GROUP_POLICY` | — | `disabled` | 群聊访问策略：`open`, `allowlist`, `disabled` |
| `WEIXIN_ALLOWED_USERS` | — | _(空)_ | 私聊白名单用户 ID（逗号分隔） |
| `WEIXIN_GROUP_ALLOWED_USERS` | — | _(空)_ | 群聊白名单群组 ID（逗号分隔） |
| `WEIXIN_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天 ID |
| `WEIXIN_HOME_CHANNEL_NAME` | — | `Home` | 主频道的显示名称 |
| `WEIXIN_ALLOW_ALL_USERS` | — | — | 网关级标志，允许所有用户（供设置向导使用） |

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `Weixin startup failed: aiohttp and cryptography are required` | 安装这两个库：`pip install aiohttp cryptography` |
| `Weixin startup failed: WEIXIN_TOKEN is required` | 运行 `hermes gateway setup` 完成扫码登录，或手动设置 `WEIXIN_TOKEN` |
| `Weixin startup failed: WEIXIN_ACCOUNT_ID is required` | 在 `.env` 中设置 `WEIXIN_ACCOUNT_ID` 或运行 `hermes gateway setup` |
| `Another local Hermes gateway is already using this Weixin token` | 先停止另一个网关实例 —— 每个 token 只允许一个轮询器 |
| 会话过期 (`errcode=-14`) | 登录会话已过期。重新运行 `hermes gateway setup` 扫描新二维码 |
| 设置期间二维码过期 | 二维码会自动刷新最多 3 次。如果持续过期，请检查网络连接 |
| Bot 不回复私聊 | 检查 `WEIXIN_DM_POLICY` —— 如果设置为 `allowlist`，发送者必须在 `WEIXIN_ALLOWED_USERS` 中 |
| Bot 忽略群消息 | 群策略默认为 `disabled`。请设置 `WEIXIN_GROUP_POLICY=open` 或 `allowlist` |
| 媒体上传/下载失败 | 确保已安装 `cryptography`。检查对 `novac2c.cdn.weixin.qq.com` 的网络访问权限 |
| `Blocked unsafe URL (SSRF protection)` | 出站媒体 URL 指向了私有/内部地址。仅允许使用公共 URL |
| 语音消息显示为文本 | 如果微信提供了转录文本，适配器会使用该文本。这是预期行为 |
| 消息出现重复 | 适配器通过消息 ID 进行去重。如果看到重复，请检查是否运行了多个网关实例 |
| `iLink POST ... HTTP 4xx/5xx` | iLink 服务的 API 错误。检查 token 有效性和网络连接 |
| 终端二维码无法显示 | 安装 `qrcode`：`pip install qrcode`。或者，打开二维码上方打印的 URL |
