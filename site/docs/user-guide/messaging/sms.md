---
sidebar_position: 8
sidebar_label: "SMS (Twilio)"
title: "SMS (Twilio)"
description: "通过 Twilio 设置 Hermes Agent 作为 SMS 聊天机器人"
---

# SMS 设置（Twilio）

Hermes 通过 [Twilio](https://www.twilio.com/) API 连接 SMS。用户向你的 Twilio 电话号码发送短信，Hermes 会回复 AI 生成的消息——体验和 Telegram 或 Discord 一样，只不过是通过普通短信实现的对话。

:::info 共享凭证
SMS 网关与可选的 [telephony skill](/reference/skills-catalog) 共享凭证。如果你已经为语音通话或单次 SMS 设置过 Twilio，网关使用相同的 `TWILIO_ACCOUNT_SID`、`TWILIO_AUTH_TOKEN` 和 `TWILIO_PHONE_NUMBER`。
:::

---

## 前提条件

- **Twilio 账号** — [在 twilio.com 注册](https://www.twilio.com/try-twilio)（提供免费试用）
- **支持 SMS 的 Twilio 电话号码**
- **公网可访问的服务器** — Twilio 会在收到短信时向你的服务器发送 webhook
- **aiohttp** — 运行 `pip install 'hermes-agent[sms]'`

---

## 第 1 步：获取 Twilio 凭证

1. 访问 [Twilio 控制台](https://console.twilio.com/)
2. 从仪表盘复制你的 **Account SID** 和 **Auth Token**
3. 进入 **Phone Numbers → Manage → Active Numbers**，记录你的电话号码（E.164 格式，例如 `+15551234567`）

---

## 第 2 步：配置 Hermes

### 交互式设置（推荐）

```bash
hermes gateway setup
```

从平台列表中选择 **SMS (Twilio)**，向导会提示你输入凭证。

### 手动设置

添加到 `~/.hermes/.env` 文件：

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567

# 安全：限制特定电话号码（推荐）
SMS_ALLOWED_USERS=+15559876543,+15551112222

# 可选：设置定时任务的主频道
SMS_HOME_CHANNEL=+15559876543
```

---

## 第 3 步：配置 Twilio Webhook

Twilio 需要知道接收短信时发送到哪里。在 [Twilio 控制台](https://console.twilio.com/)：

1. 进入 **Phone Numbers → Manage → Active Numbers**
2. 点击你的电话号码
3. 在 **Messaging → A MESSAGE COMES IN** 下设置：
   - **Webhook**：`https://your-server:8080/webhooks/twilio`
   - **HTTP Method**：`POST`

:::tip 暴露你的 Webhook
如果你在本地运行 Hermes，使用隧道工具暴露 webhook：

```bash
# 使用 cloudflared
cloudflared tunnel --url http://localhost:8080

# 使用 ngrok
ngrok http 8080
```

将生成的公网 URL 设置为 Twilio webhook。
:::

Webhook 默认监听端口为 `8080`。可通过以下方式覆盖：

```bash
SMS_WEBHOOK_PORT=3000
```

---

## 第 4 步：启动网关

```bash
hermes gateway
```

你应该看到：

```
[sms] Twilio webhook server listening on port 8080, from: +1555***4567
```

给你的 Twilio 号码发短信，Hermes 会通过 SMS 回复。

---

## 环境变量

| 变量 | 是否必需 | 说明 |
|----------|----------|-------------|
| `TWILIO_ACCOUNT_SID` | 是 | Twilio 账号 SID（以 `AC` 开头） |
| `TWILIO_AUTH_TOKEN` | 是 | Twilio 认证令牌 |
| `TWILIO_PHONE_NUMBER` | 是 | 你的 Twilio 电话号码（E.164 格式） |
| `SMS_WEBHOOK_PORT` | 否 | webhook 监听端口（默认：`8080`） |
| `SMS_ALLOWED_USERS` | 否 | 允许聊天的电话号码，逗号分隔，E.164 格式 |
| `SMS_ALLOW_ALL_USERS` | 否 | 设置为 `true` 允许所有人（不推荐） |
| `SMS_HOME_CHANNEL` | 否 | 定时任务/通知的电话号码 |
| `SMS_HOME_CHANNEL_NAME` | 否 | 主频道显示名称（默认：`Home`） |

---

## SMS 特有行为

- **仅支持纯文本** — 会自动去除 Markdown，因为 SMS 会把它当作普通字符显示
- **1600 字符限制** — 超长回复会在自然断点（换行符、空格）拆分成多条消息
- **防止回声** — 来自你自己 Twilio 号码的消息会被忽略，避免循环回复
- **电话号码脱敏** — 日志中会对电话号码进行脱敏保护隐私

---

## 安全性

**网关默认拒绝所有用户。** 请配置允许列表：

```bash
# 推荐：限制特定电话号码
SMS_ALLOWED_USERS=+15559876543,+15551112222

# 或允许所有（不推荐用于有终端访问的机器人）
SMS_ALLOW_ALL_USERS=true
```

:::warning
SMS 没有内置加密。除非你了解安全风险，否则不要用 SMS 处理敏感操作。敏感场景建议使用 Signal 或 Telegram。
:::

---

## 故障排查

### 消息未到达

1. 检查 Twilio webhook URL 是否正确且公网可访问
2. 确认 `TWILIO_ACCOUNT_SID` 和 `TWILIO_AUTH_TOKEN` 是否正确
3. 查看 Twilio 控制台 → **Monitor → Logs → Messaging** 是否有投递错误
4. 确认你的电话号码在 `SMS_ALLOWED_USERS` 中（或设置了 `SMS_ALLOW_ALL_USERS=true`）

### 回复未发送

1. 检查 `TWILIO_PHONE_NUMBER` 是否正确设置（E.164 格式，带 `+`）
2. 确认你的 Twilio 账号有支持 SMS 的号码
3. 查看 Hermes 网关日志是否有 Twilio API 错误

### Webhook 端口冲突

如果端口 8080 被占用，修改为：

```bash
SMS_WEBHOOK_PORT=3001
```

并在 Twilio 控制台更新 webhook URL 以匹配。

---
