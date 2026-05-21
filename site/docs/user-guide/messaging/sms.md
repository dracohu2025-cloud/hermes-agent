---
sidebar_position: 8
sidebar_label: "SMS（Twilio）"
title: "SMS（Twilio）"
description: "通过 Twilio 将 Hermes Agent 配置为短信聊天机器人"
---

<a id="sms-setup-twilio"></a>
# SMS 配置（Twilio）

Hermes 通过 [Twilio](https://www.twilio.com/) API 连接短信服务。用户给您的 Twilio 电话号码发短信后，会收到 AI 回复——和 Telegram 或 Discord 一样的对话体验，只不过用的是普通短信。

:::info 共享凭据
短信网关与可选的 [telephony 技能](/reference/skills-catalog) 共享凭据。如果您已经为语音通话或一次性短信设置了 Twilio，那么网关会使用相同的 `TWILIO_ACCOUNT_SID`、`TWILIO_AUTH_TOKEN` 和 `TWILIO_PHONE_NUMBER`。
:::

---

<a id="prerequisites"></a>
<a id="shared-credentials"></a>
## 前提条件

- **Twilio 账户** — [在 twilio.com 注册](https://www.twilio.com/try-twilio)（提供免费试用）
- **一个支持 SMS 的 Twilio 电话号码**
- **一个公网可访问的服务器** — Twilio 在收到短信时会向您的服务器发送 webhook
- **aiohttp** — `pip install 'hermes-agent[sms]'`

---

<a id="step-1-get-your-twilio-credentials"></a>
## 步骤 1：获取您的 Twilio 凭据

1. 进入 [Twilio 控制台](https://console.twilio.com/)
2. 从仪表盘复制您的 **Account SID** 和 **Auth Token**
3. 进入 **Phone Numbers → Manage → Active Numbers** — 记下您的电话号码（使用 E.164 格式，例如 `+15551234567`）

---

<a id="step-2-configure-hermes"></a>
## 步骤 2：配置 Hermes

<a id="interactive-setup-recommended"></a>
### 交互式配置（推荐）

```bash
hermes gateway setup
```

选择平台列表中的 **SMS（Twilio）**。向导会提示您输入凭据。

<a id="manual-setup"></a>
### 手动配置

添加到 `~/.hermes/.env`：

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567

# 安全性：限制特定电话号码（推荐）
SMS_ALLOWED_USERS=+15559876543,+15551112222

# 可选：为 cron 任务投递设置家庭频道
SMS_HOME_CHANNEL=+15559876543
```

---

<a id="step-3-configure-twilio-webhook"></a>
## 步骤 3：配置 Twilio Webhook

Twilio 需要知道往哪里发送收到的消息。在 [Twilio 控制台](https://console.twilio.com/) 中：

1. 进入 **Phone Numbers → Manage → Active Numbers**
2. 点击您的电话号码
3. 在 **Messaging → A MESSAGE COMES IN** 下，设置：
   - **Webhook**：`https://your-server:8080/webhooks/twilio`
   - **HTTP 方法**：`POST`

:::tip 暴露您的 Webhook
<a id="exposing-your-webhook"></a>
如果您在本地运行 Hermes，请使用隧道来暴露 webhook：

```bash
# 使用 cloudflared
cloudflared tunnel --url http://localhost:8080

# 使用 ngrok
ngrok http 8080
```

将生成的公网 URL 设置为您的 Twilio webhook。
:::

**将 `SMS_WEBHOOK_URL` 设置为您在 Twilio 中配置的同一 URL。** 这是 Twilio 签名验证所必需的——适配器没有它就无法启动：

```bash
# 必须与您的 Twilio 控制台中的 webhook URL 一致
SMS_WEBHOOK_URL=https://your-server:8080/webhooks/twilio
```

Webhook 端口默认为 `8080`。可通过以下方式覆盖：

```bash
SMS_WEBHOOK_PORT=3000
```

---

<a id="step-4-start-the-gateway"></a>
## 步骤 4：启动网关

```bash
hermes gateway
```

您应该会看到：

```
[sms] Twilio webhook server listening on 127.0.0.1:8080, from: +1555***4567
```

如果您看到 `Refusing to start: SMS_WEBHOOK_URL is required`，请将 `SMS_WEBHOOK_URL` 设置为在 Twilio 控制台中配置的公网 URL（参见步骤 3）。
给您的 Twilio 号码发短信 — Hermes 会通过 SMS 回复。

---

<a id="environment-variables"></a>
## 环境变量

| 变量 | 必填 | 说明 |
|----------|----------|-------------|
| `TWILIO_ACCOUNT_SID` | 是 | Twilio 账户 SID（以 `AC` 开头） |
| `TWILIO_AUTH_TOKEN` | 是 | Twilio 认证令牌（也用于 webhook 签名验证） |
| `TWILIO_PHONE_NUMBER` | 是 | 您的 Twilio 电话号码（E.164 格式） |
| `SMS_WEBHOOK_URL` | 是 | 用于 Twilio 签名验证的公共 URL — 必须与 Twilio 控制台中的 webhook URL 一致 |
| `SMS_WEBHOOK_PORT` | 否 | Webhook 监听端口（默认：`8080`） |
| `SMS_WEBHOOK_HOST` | 否 | Webhook 绑定地址（默认：`0.0.0.0`） |
| `SMS_INSECURE_NO_SIGNATURE` | 否 | 设置为 `true` 可禁用签名验证（仅限本地开发 — **不可用于生产环境**） |
| `SMS_ALLOWED_USERS` | 否 | 允许聊天的 E.164 格式电话号码，用逗号分隔 |
| `SMS_ALLOW_ALL_USERS` | 否 | 设置为 `true` 允许任何人（不推荐） |
| `SMS_HOME_CHANNEL` | 否 | 用于定时任务/通知推送的电话号码 |
| `SMS_HOME_CHANNEL_NAME` | 否 | 主频道的显示名称（默认：`Home`） |

---

<a id="sms-specific-behavior"></a>
## SMS 特有行为

- **仅纯文本** — Markdown 会被自动去除，因为 SMS 会将其渲染为字面字符
- **1600 字符限制** — 较长的回复会在自然断点（换行符，然后是空格）处拆分为多条消息
- **回声预防** — 来自您自己 Twilio 号码的消息会被忽略，以防止循环
- **电话号码脱敏** — 日志中的电话号码会被脱敏以保护隐私

---

<a id="security"></a>
## 安全性

<a id="webhook-signature-validation"></a>
### Webhook 签名验证

Hermes 通过验证 `X-Twilio-Signature` 标头（HMAC-SHA1）来确认入站 webhook 确实来自 Twilio。这可以防止攻击者注入伪造消息。

**`SMS_WEBHOOK_URL` 是必填项。** 将其设置为在 Twilio 控制台中配置的公共 URL。如果没有它，适配器将拒绝启动。

对于没有公共 URL 的本地开发，您可以禁用验证：

```bash
# 仅限本地开发 — 不可用于生产环境
SMS_INSECURE_NO_SIGNATURE=true
```

<a id="user-allowlists"></a>
### 用户白名单

**网关默认拒绝所有用户。** 配置一个白名单：

```bash
# 推荐：限制为特定电话号码
SMS_ALLOWED_USERS=+15559876543,+15551112222

# 或者允许所有人（不推荐用于具有终端访问权限的机器人）
SMS_ALLOW_ALL_USERS=true
```

:::warning
SMS 没有内置加密。除非您了解安全影响，否则不要将 SMS 用于敏感操作。对于敏感用例，请优先使用 Signal 或 Telegram。
:::

---

<a id="troubleshooting"></a>
## 故障排除

<a id="messages-not-arriving"></a>
### 消息未到达

1. 检查您的 Twilio webhook URL 是否正确且可公开访问
2. 验证 `TWILIO_ACCOUNT_SID` 和 `TWILIO_AUTH_TOKEN` 是否正确
3. 在 Twilio 控制台 → **监控 → 日志 → 消息** 中检查投递错误
4. 确保您的电话号码在 `SMS_ALLOWED_USERS` 中（或设置了 `SMS_ALLOW_ALL_USERS=true`）

<a id="replies-not-sending"></a>
### 回复未发送

1. 检查 `TWILIO_PHONE_NUMBER` 是否设置正确（E.164 格式，带 `+`）
2. 验证您的 Twilio 账户是否拥有支持 SMS 的号码
3. 检查 Hermes 网关日志中是否有 Twilio API 错误
<a id="webhook-port-conflicts"></a>
### Webhook 端口冲突

如果 8080 端口已被占用，请更换端口：

```bash
SMS_WEBHOOK_PORT=3001
```

同时更新 Twilio Console 中的 Webhook URL，使其与新的端口一致。
