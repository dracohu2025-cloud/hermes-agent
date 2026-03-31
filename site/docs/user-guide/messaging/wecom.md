---
sidebar_position: 14
title: "WeCom (企业微信)"
description: "通过 AI Bot WebSocket 网关将 Hermes Agent 连接到 WeCom"
---

# WeCom (企业微信)

将 Hermes 连接到腾讯的企业通讯平台 [WeCom](https://work.weixin.qq.com/) (企业微信)。此适配器使用 WeCom 的 AI Bot WebSocket 网关进行实时双向通信，无需公网端点或 Webhook。

## 前提条件

- 一个 WeCom 组织账号
- 在 WeCom 管理后台创建的 AI Bot
- 来自机器人凭证页面的 Bot ID 和 Secret

## 设置

### 1. 创建 AI Bot

1.  登录 [WeCom 管理后台](https://work.weixin.qq.com/wework_admin/frame)
2.  导航至 **应用管理** → **创建应用** → **AI Bot**
3.  配置机器人名称和描述
4.  从凭证页面复制 **Bot ID** 和 **Secret**

### 2. 配置 Hermes

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

### 3. 启动网关

```bash
hermes gateway start
```

## 功能特性

- **WebSocket 传输** — 持久连接，无需公网端点
- **私聊和群聊** — 可配置的访问策略
- **媒体支持** — 图片、文件、语音、视频的上传和下载
- **AES 加密媒体** — 自动解密接收的附件
- **引用上下文** — 保留回复线程
- **Markdown 渲染** — 富文本响应
- **自动重连** — 连接断开时使用指数退避重试

## 配置选项

在 `config.yaml` 的 `platforms.wecom.extra` 下设置这些选项：

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `bot_id` | — | WeCom AI Bot ID (必需) |
| `secret` | — | WeCom AI Bot Secret (必需) |
| `websocket_url` | `wss://openws.work.weixin.qq.com` | WebSocket 网关 URL |
| `dm_policy` | `open` | 私聊访问策略：`open`, `allowlist`, `disabled`, `pairing` |
| `group_policy` | `open` | 群聊访问策略：`open`, `allowlist`, `disabled` |
| `allow_from` | `[]` | 允许私聊的用户 ID (当 dm_policy=allowlist 时) |
| `group_allow_from` | `[]` | 允许的群聊 ID (当 group_policy=allowlist 时) |

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| "WECOM_BOT_ID 和 WECOM_SECRET 是必需的" | 设置这两个环境变量或在设置向导中配置 |
| "invalid secret (errcode=40013)" | 确认 Secret 与你的机器人凭证匹配 |
| "Timed out waiting for subscribe acknowledgement" | 检查到 `openws.work.weixin.qq.com` 的网络连接 |
| 机器人在群聊中不响应 | 检查 `group_policy` 设置和群聊白名单 |
