---
sidebar_position: 5
title: "Microsoft Teams"
description: "将 Hermes Agent 设置为 Microsoft Teams 机器人"
---

# Microsoft Teams 设置 {#microsoft-teams-setup}

将 Hermes Agent 作为机器人连接到 Microsoft Teams。与 Slack 的 Socket Mode 不同，Teams 通过调用 **公共 HTTPS webhook** 来传递消息，因此你的实例需要一个可公开访问的端点——可以是开发隧道（本地开发）或真实域名（生产环境）。

## 机器人如何响应 {#how-the-bot-responds}

| 场景 | 行为 |
|---------|----------|
| **个人聊天（私信）** | 机器人会响应每条消息，无需 @提及。 |
| **群聊** | 机器人仅在被 @提及 时响应。 |
| **频道** | 机器人仅在被 @提及 时响应。 |

Teams 将 @提及 作为带有 `&lt;at&gt;BotName</at>` 标签的普通消息传递，Hermes 会在处理前自动去除这些标签。

---

## 第一步：安装 Teams CLI {#step-1-install-the-teams-cli}

`@microsoft/teams.cli` 可自动完成机器人注册——无需 Azure 门户。

```bash
npm install -g @microsoft/teams.cli@preview
teams login
```

要验证登录并找到你自己的 AAD 对象 ID（用于 `TEAMS_ALLOWED_USERS`）：

```bash
teams status --verbose
```

---

## 第二步：暴露 Webhook 端口 {#step-2-expose-the-webhook-port}

Teams 无法向 `localhost` 传递消息。对于本地开发，请使用任何隧道工具获取公共 HTTPS URL。默认端口为 `3978`——如有需要，可通过 `TEAMS_PORT` 更改。

```bash
# devtunnel（Microsoft）
devtunnel create hermes-bot --allow-anonymous
devtunnel port create hermes-bot -p 3978 --protocol https  # 如果更改了，请将 3978 替换为 TEAMS_PORT
devtunnel host hermes-bot

# ngrok
ngrok http 3978  # 如果更改了，请将 3978 替换为 TEAMS_PORT

# cloudflared
cloudflared tunnel --url http://localhost:3978  # 如果更改了，请将 3978 替换为 TEAMS_PORT
```

从输出中复制 `https://` URL——你将在下一步中使用它。开发期间请保持隧道运行。

对于生产环境，请将机器人的端点指向服务器的公共域名（参见[生产部署](#production-deployment)）。

---

## 第三步：创建机器人 {#step-3-create-the-bot}

```bash
teams app create \
  --name "Hermes" \
  --endpoint "https://<你的隧道URL>/api/messages"
```

CLI 会输出你的 `CLIENT_ID`、`CLIENT_SECRET` 和 `TENANT_ID`，以及第六步的安装链接。请保存客户端密钥——它不会再次显示。

---

## 第四步：配置环境变量 {#step-4-configure-environment-variables}

添加到 `~/.hermes/.env`：

```bash
# 必填
TEAMS_CLIENT_ID=<你的客户端ID>
TEAMS_CLIENT_SECRET=<你的客户端密钥>
TEAMS_TENANT_ID=<你的租户ID>

# 限制特定用户访问（推荐）
# 使用 `teams status --verbose` 中的 AAD 对象 ID
TEAMS_ALLOWED_USERS=<你的AAD对象ID>
```

---

## 第五步：启动网关 {#step-5-start-the-gateway}

```bash
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d gateway
```

这将启动网关。默认 webhook 端口为 `3978`（可通过 `TEAMS_PORT` 覆盖）。检查它是否正在运行：

```bash
curl http://localhost:3978/health   # 应返回：ok
docker logs -f hermes
```

查找：
```
[teams] Webhook server listening on 0.0.0.0:3978/api/messages
```

---

## 第六步：在 Teams 中安装应用 {#step-6-install-the-app-in-teams}

```bash
teams app get <teamsAppId> --install-link
```

在浏览器中打开打印的链接——它会直接在 Teams 客户端中打开。安装后，向你的机器人发送一条直接消息——它已准备就绪。

## 功能

### 交互式审批卡片

当 Agent 需要执行潜在危险命令时，它会发送一张包含四个按钮的自适应卡片，而不是要求你输入 `/approve`：

- **Allow Once** — 批准本次特定命令
- **Allow Session** — 在当前会话中批准该模式
- **Always Allow** — 永久批准该模式
- **Deny** — 拒绝该命令

点击按钮即可内联完成审批，并将卡片替换为决策结果。

---

## 生产部署 {#production-deployment}

对于永久服务器，请跳过 devtunnel，将你的机器人注册到服务器的公共 HTTPS 端点：

```bash
teams app create \
  --name "Hermes" \
  --endpoint "https://your-domain.com/api/messages"
```

如果你已经创建了机器人，只需更新端点：

```bash
teams app update --id <teamsAppId> --endpoint "https://your-domain.com/api/messages"
```

确保你配置的端口（`TEAMS_PORT`，默认 `3978`）可从互联网访问，并且 TLS 证书有效——Teams 会拒绝自签名证书。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `health` 端点正常，但机器人无响应 | 检查你的隧道是否仍在运行，以及机器人的消息端点是否与隧道 URL 匹配 |
| 日志中出现 `KeyError: 'teams'` | 重启容器——当前版本已修复此问题 |
| 机器人返回认证错误 | 确认 `TEAMS_CLIENT_ID`、`TEAMS_CLIENT_SECRET` 和 `TEAMS_TENANT_ID` 均已正确设置 |
| `No inference provider configured` | 检查 `~/.hermes/.env` 中是否设置了 `ANTHROPIC_API_KEY`（或其他提供商的密钥） |
| 机器人收到消息但忽略它们 | 你的 AAD 对象 ID 可能不在 `TEAMS_ALLOWED_USERS` 中。运行 `teams status --verbose` 查找它 |
| 重启后隧道 URL 发生变化 | 如果使用命名隧道（`devtunnel create hermes-bot`），devtunnel URL 是持久的。ngrok 和 cloudflared 每次运行都会生成新 URL（除非你有付费计划）——当 URL 变化时，使用 `teams app update` 更新机器人端点 |
| Teams 显示“此机器人未响应” | Webhook 返回了错误。检查 `docker logs hermes` 中的回溯信息 |
| 日志中出现 `[teams] Failed to connect` | SDK 认证失败。请仔细检查你的凭据，并确保租户 ID 与你用于 `teams login` 的账户匹配 |
---

## 安全性 {#security}

:::warning
**务必使用授权用户的 AAD 对象 ID 设置 `TEAMS_ALLOWED_USERS`**。否则，任何能找到或安装你机器人的人都可以与之交互。

请将 `TEAMS_CLIENT_SECRET` 视为密码——通过 Azure 门户或 Teams CLI 定期轮换。
:::

- 将凭据存储在 `~/.hermes/.env` 中，权限设置为 `600`（`chmod 600 ~/.hermes/.env`）
- 机器人只接受来自 `TEAMS_ALLOWED_USERS` 中用户的消息；未经授权的消息会被静默丢弃
- 你的公共端点（`/api/messages`）由 Teams Bot Framework 进行身份验证——没有有效 JWT 的请求将被拒绝
