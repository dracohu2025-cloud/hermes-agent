---
sidebar_position: 14
title: "WeCom（企业微信）"
description: "通过 AI Bot WebSocket 网关将 Hermes Agent 连接到 WeCom"
---

# WeCom（企业微信）

将 Hermes 连接到 [WeCom](https://work.weixin.qq.com/)（企业微信），腾讯的企业级消息平台。该适配器使用 WeCom 的 AI Bot WebSocket 网关实现实时双向通信——无需公开端点或 webhook。

## 前提条件

- 一个 WeCom 组织账号
- 在 WeCom 管理后台创建的 AI Bot
- Bot 凭证页面上的 Bot ID 和 Secret
- Python 包：`aiohttp` 和 `httpx`

## 设置

### 1. 创建 AI Bot

1. 登录 [WeCom 管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 进入 **应用管理** → **创建应用** → **AI Bot**
3. 配置机器人名称和描述
4. 从凭证页面复制 **Bot ID** 和 **Secret**

### 2. 配置 Hermes

运行交互式设置：

```bash
hermes gateway setup
```

选择 **WeCom**，然后输入你的 Bot ID 和 Secret。

或者在 `~/.hermes/.env` 中设置环境变量：

```bash
WECOM_BOT_ID=your-bot-id
WECOM_SECRET=your-secret

# 可选：限制访问用户
WECOM_ALLOWED_USERS=user_id_1,user_id_2

# 可选：cron/通知的默认频道
WECOM_HOME_CHANNEL=chat_id
```

### 3. 启动网关

```bash
hermes gateway start
```

## 功能

- **WebSocket 传输** — 持久连接，无需公开端点
- **私聊和群聊消息** — 可配置访问策略
- **每个群组的发送者白名单** — 精细控制谁能在群里互动
- **媒体支持** — 图片、文件、语音、视频的上传和下载
- **AES 加密媒体** — 自动解密接收的附件
- **引用上下文** — 保留回复的线程关系
- **Markdown 渲染** — 丰富文本回复
- **回复模式流式响应** — 将回复与收到的消息上下文关联
- **自动重连** — 连接断开时指数退避重连

## 配置选项

在 `config.yaml` 的 `platforms.wecom.extra` 下设置：

| 键名 | 默认值 | 说明 |
|-----|---------|-------------|
| `bot_id` | — | WeCom AI Bot ID（必填） |
| `secret` | — | WeCom AI Bot Secret（必填） |
| `websocket_url` | `wss://openws.work.weixin.qq.com` | WebSocket 网关地址 |
| `dm_policy` | `open` | 私聊访问策略：`open`、`allowlist`、`disabled`、`pairing` |
| `group_policy` | `open` | 群聊访问策略：`open`、`allowlist`、`disabled` |
| `allow_from` | `[]` | 允许私聊的用户 ID（当 dm_policy=allowlist 时） |
| `group_allow_from` | `[]` | 允许的群组 ID（当 group_policy=allowlist 时） |
| `groups` | `{}` | 每个群组的配置（见下文） |

## 访问策略

### 私聊策略

控制谁可以给机器人发私聊消息：

| 值 | 行为 |
|-------|----------|
| `open` | 任何人都可以私聊机器人（默认） |
| `allowlist` | 只有 `allow_from` 中的用户 ID 可以私聊 |
| `disabled` | 忽略所有私聊消息 |
| `pairing` | 配对模式（用于初始设置） |

```bash
WECOM_DM_POLICY=allowlist
```

### 群聊策略

控制机器人在哪些群组中响应：

| 值 | 行为 |
|-------|----------|
| `open` | 机器人响应所有群组（默认） |
| `allowlist` | 只响应 `group_allow_from` 中列出的群组 |
| `disabled` | 忽略所有群消息 |

```bash
WECOM_GROUP_POLICY=allowlist
```

### 每个群组的发送者白名单

为了更细粒度的控制，你可以限制哪些用户可以在特定群组中与机器人互动。配置示例如下，写在 `config.yaml` 中：

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

1. `group_policy` 和 `group_allow_from` 控制群组是否被允许。
2. 如果群组通过了顶层检查，`groups.<group_id>.allow_from`（如果存在）会进一步限制该群内哪些发送者可以与机器人互动。
3. 通配符 `"*"` 组条目作为未明确列出的群组的默认配置。
4. 白名单条目支持 `*` 通配符，允许所有用户，且条目不区分大小写。
5. 条目可以使用 `wecom:user:` 或 `wecom:group:` 前缀格式，前缀会被自动去除。

如果某个群组没有配置 `allow_from`，则默认允许该群组内所有用户（前提是该群组通过了顶层策略检查）。
### 重连行为

连接断开时，适配器会使用指数退避算法进行重连：

| 尝试次数 | 延迟时间 |
|---------|---------|
| 第1次重试 | 2秒 |
| 第2次重试 | 5秒 |
| 第3次重试 | 10秒 |
| 第4次重试 | 30秒 |
| 第5次及以后重试 | 60秒 |

每次成功重连后，退避计数器会重置为零。断开连接时，所有未完成的请求都会失败，避免调用方无限等待。

### 去重

入站消息通过消息 ID 进行去重，去重窗口为 5 分钟，最大缓存条目数为 1000。这样可以防止在重连或网络波动时消息被重复处理。

## 所有环境变量

| 变量 | 是否必需 | 默认值 | 说明 |
|----------|----------|---------|-------------|
| `WECOM_BOT_ID` | ✅ | — | WeCom AI Bot ID |
| `WECOM_SECRET` | ✅ | — | WeCom AI Bot Secret |
| `WECOM_ALLOWED_USERS` | — | _(空)_ | 以逗号分隔的用户 ID，网关级允许列表 |
| `WECOM_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天 ID |
| `WECOM_WEBSOCKET_URL` | — | `wss://openws.work.weixin.qq.com` | WebSocket 网关地址 |
| `WECOM_DM_POLICY` | — | `open` | 私聊访问策略 |
| `WECOM_GROUP_POLICY` | — | `open` | 群聊访问策略 |

## 故障排查

| 问题 | 解决方案 |
|---------|---------|
| `WECOM_BOT_ID 和 WECOM_SECRET 是必需的` | 设置这两个环境变量或在安装向导中配置 |
| `WeCom 启动失败：未安装 aiohttp` | 安装 aiohttp：`pip install aiohttp` |
| `WeCom 启动失败：未安装 httpx` | 安装 httpx：`pip install httpx` |
| `invalid secret (errcode=40013)` | 确认 secret 与你的 Bot 凭据匹配 |
| `等待订阅确认超时` | 检查与 `openws.work.weixin.qq.com` 的网络连接 |
| 机器人在群聊中无响应 | 检查 `group_policy` 设置，确保群 ID 在 `group_allow_from` 中 |
| 机器人忽略群内某些用户 | 检查 `groups` 配置中的每个群的 `allow_from` 列表 |
| 媒体解密失败 | 安装 `cryptography`：`pip install cryptography` |
| `cryptography 是 WeCom 媒体解密所必需的` | 入站媒体是 AES 加密的。安装：`pip install cryptography` |
| 语音消息以文件形式发送 | WeCom 仅支持 AMR 格式的原生语音，其他格式会自动降级为文件 |
| `文件过大` 错误 | WeCom 对所有文件上传限制为 20 MB。请压缩或拆分文件。 |
| 图片以文件形式发送 | 图片超过 10 MB 超出原生图片限制，会自动降级为文件附件。 |
| `发送消息到 WeCom 超时` | WebSocket 可能已断开。查看日志中的重连信息。 |
| `WeCom WebSocket 在认证时关闭` | 网络问题或凭据错误。确认 bot_id 和 secret 是否正确。 |
