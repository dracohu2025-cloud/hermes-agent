---
sidebar_position: 8
sidebar_label: "SMS (Twilio)"
title: "SMS (Twilio)"
description: "通过 Twilio 将 Hermes Agent 设置为 SMS 聊天机器人"
---

# SMS 设置 (Twilio)

Hermes 通过 [Twilio](https://www.twilio.com/) API 连接到 SMS。人们向你的 Twilio 电话号码发送短信，即可收到 AI 的回复 —— 这种对话体验与 Telegram 或 Discord 相同，但使用的是标准手机短信。

:::info 凭据共享
SMS 网关与可选的 [telephony skill](/reference/skills-catalog) 共享凭据。如果你已经为语音通话或单次 SMS 发送设置了 Twilio，该网关可以直接使用相同的 `TWILIO_ACCOUNT_SID`、`TWILIO_AUTH_TOKEN` 和 `TWILIO_PHONE_NUMBER`。
:::

---

## 前提条件

- **Twilio 账号** — [在 twilio.com 注册](https://www.twilio.com/try-twilio)（提供免费试用）
- **具有 SMS 功能的 Twilio 电话号码**
- **一个可公开访问的服务器** — 当短信到达时，Twilio 会向你的服务器发送 webhook
- **aiohttp** — `pip install 'hermes-agent[sms]'`

---

## 第 1 步：获取你的 Twilio 凭据

1. 登录 [Twilio 控制台](https://console.twilio.com/)
2. 从仪表板复制你的 **Account SID** 和 **Auth Token**
3. 前往 **Phone Numbers → Manage → Active Numbers** — 记录下你的 E.164 格式电话号码（例如：`+15551234567`）

---

## 第 2 步：配置 Hermes

### 交互式设置（推荐）

```bash
hermes gateway setup
```

从平台列表中选择 **SMS (Twilio)**。向导会提示你输入凭据。

### 手动设置

添加到 `~/.hermes/.env`：

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567

# 安全：限制特定的电话号码（推荐）
SMS_ALLOWED_USERS=+15559876543,+15551112222

# 可选：为 cron 任务交付设置主频道
SMS_HOME_CHANNEL=+15559876543
```

---

## 第 3 步：配置 Twilio Webhook

Twilio 需要知道将传入的消息发送到哪里。在 [Twilio 控制台](https://console.twilio.com/)中：

1. 前往 **Phone Numbers → Manage → Active Numbers**
2. 点击你的电话号码
3. 在 **Messaging → A MESSAGE COMES IN** 下，设置：
   - **Webhook**: `https://your-server:8080/webhooks/twilio`
   - **HTTP Method**: `POST`

:::tip 暴露你的 Webhook
如果你在本地运行 Hermes，请使用隧道工具暴露 webhook：

```bash
# 使用 cloudflared
cloudflared tunnel --url http://localhost:8080

# 使用 ngrok
ngrok http 8080
```

将生成的公网 URL 设置为你的 Twilio webhook。
:::

Webhook 端口默认为 `8080`。如需覆盖请使用：

```bash
SMS_WEBHOOK_PORT=3000
```

---

## 第 4 步：启动网关

```bash
hermes gateway
```

你应该会看到：

```
[sms] Twilio webhook server listening on port 8080, from: +1555***4567
```

给你的 Twilio 号码发短信 —— Hermes 将通过 SMS 进行回复。

---

## 环境变量

| 变量 | 必填 | 描述 |
|----------|----------|-------------|
| `TWILIO_ACCOUNT_SID` | 是 | Twilio Account SID（以 `AC` 开头） |
| `TWILIO_AUTH_TOKEN` | 是 | Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | 是 | 你的 Twilio 电话号码（E.164 格式） |
| `SMS_WEBHOOK_PORT` | 否 | Webhook 监听端口（默认：`8080`） |
| `SMS_ALLOWED_USERS` | 否 | 允许聊天的 E.164 电话号码列表（逗号分隔） |
| `SMS_ALLOW_ALL_USERS` | 否 | 设置为 `true` 以允许任何人（不推荐） |
| `SMS_HOME_CHANNEL` | 否 | 用于 cron 任务 / 通知推送的电话号码 |
| `SMS_HOME_CHANNEL_NAME` | 否 | 主频道的显示名称（默认：`Home`） |

---

## SMS 特定行为

- **仅限纯文本** — Markdown 会被自动剥离，因为 SMS 会将其渲染为字面字符。
- **1600 字符限制** — 较长的回复会在自然边界（先换行符，后空格）处拆分为多条消息。
- **回声防止** — 来自你自己的 Twilio 号码的消息将被忽略，以防止死循环。
- **电话号码脱敏** — 为了隐私，日志中的电话号码会被脱敏处理。

---

## 安全性

**网关默认拒绝所有用户。** 请配置允许列表：

```bash
# 推荐：限制特定的电话号码
SMS_ALLOWED_USERS=+15559876543,+15551112222

# 或者允许所有人（对于具有终端访问权限的 bot，不推荐这样做）
SMS_ALLOW_ALL_USERS=true
```

:::warning
SMS 没有内置加密。除非你了解安全后果，否则请勿将 SMS 用于敏感操作。对于敏感用例，建议优先选择 Signal 或 Telegram。
:::

---

## 故障排除

### 消息未送达

1. 检查你的 Twilio webhook URL 是否正确且可从公网访问。
2. 验证 `TWILIO_ACCOUNT_SID` 和 `TWILIO_AUTH_TOKEN` 是否正确。
3. 检查 Twilio 控制台 → **Monitor → Logs → Messaging** 查看投递错误。
4. 确保你的电话号码在 `SMS_ALLOWED_USERS` 中（或设置了 `SMS_ALLOW_ALL_USERS=true`）。

### 回复未发送

1. 检查 `TWILIO_PHONE_NUMBER` 设置是否正确（带 `+` 的 E.164 格式）。
2. 验证你的 Twilio 账号拥有具备 SMS 功能的号码。
3. 检查 Hermes 网关日志中的 Twilio API 错误。

### Webhook 端口冲突

如果 8080 端口已被占用，请更改它：

```bash
SMS_WEBHOOK_PORT=3001
```

并同步更新 Twilio 控制台中的 webhook URL。
