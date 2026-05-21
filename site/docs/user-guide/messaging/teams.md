---
sidebar_position: 5
title: "Microsoft Teams"
description: "将 Hermes Agent 配置为 Microsoft Teams 机器人"
---

<a id="microsoft-teams-setup"></a>
# Microsoft Teams 配置

将 Hermes Agent 以机器人形式接入 Microsoft Teams。与 Slack 的 Socket Mode 不同，Teams 通过调用 **公开的 HTTPS webhook** 来投递消息，因此你的实例需要有一个公网可访问的端点——可以是开发隧道（本地开发）或真实域名（生产环境）。

需要处理来自 Microsoft Graph 事件的会议摘要，而非普通的机器人对话？请使用专门的配置页面：[Teams Meetings](/user-guide/messaging/teams-meetings)。

<a id="how-the-bot-responds"></a>
## 机器人的响应方式

| 场景 | 行为 |
|---------|----------|
| **个人聊天（私信）** | 机器人回复每条消息，无需 @提及。 |
| **群组聊天** | 机器人仅在 @提及 时回复。 |
| **频道** | 机器人仅在 @提及 时回复。 |

Teams 会将 @提及 作为包含 `&lt;at&gt;BotName</at>` 标签的普通消息传递，Hermes 在处理前会自动剥离这些标签。

---

<a id="step-1-install-the-teams-cli"></a>
## 步骤 1：安装 Teams CLI

`@microsoft/teams.cli` 可自动完成机器人注册，无需 Azure 门户。

```bash
npm install -g @microsoft/teams.cli@preview
teams login
```
要验证登录并找到自己的 Azure AD 对象 ID（`TEAMS_ALLOWED_USERS` 所需）：

```bash
teams status --verbose
```

---

<a id="step-2-expose-the-webhook-port"></a>
## 第二步：暴露 Webhook 端口

Teams 无法向 `localhost` 发送消息。本地开发时，请使用任何隧道工具获取一个公共的 HTTPS URL。默认端口为 `3978` —— 如果必要，可通过 `TEAMS_PORT` 修改。

```bash
# devtunnel (Microsoft)
devtunnel create hermes-bot --allow-anonymous
devtunnel port create hermes-bot -p 3978 --protocol https  # 如已修改，请将 3978 替换为 TEAMS_PORT
devtunnel host hermes-bot

# ngrok
ngrok http 3978  # 如已修改，请将 3978 替换为 TEAMS_PORT

# cloudflared
cloudflared tunnel --url http://localhost:3978  # 如已修改，请将 3978 替换为 TEAMS_PORT
```

从输出中复制 `https://` 开头的 URL —— 下一步会用到。开发期间请保持隧道运行。

生产环境中，请将机器人的端点指向服务器的公共域名（参见[生产部署](#production-deployment)）。

---

<a id="step-3-create-the-bot"></a>
## 第三步：创建机器人
```bash
teams app create \
  --name "Hermes" \
  --endpoint "https://<你的隧道地址>/api/messages"
```

CLI 会输出你的 `CLIENT_ID`、`CLIENT_SECRET` 和 `TENANT_ID`，以及第 6 步所需的安装链接。请保存好客户端密钥——它只会显示一次。

---

<a id="step-4-configure-environment-variables"></a>
## 第 4 步：配置环境变量

在 `~/.hermes/.env` 中添加以下内容：

```bash
# 必填项
TEAMS_CLIENT_ID=<你的客户端ID>
TEAMS_CLIENT_SECRET=<你的客户端密钥>
TEAMS_TENANT_ID=<你的租户ID>

# 限制仅特定用户可访问（推荐）
# 使用 `teams status --verbose` 获取 AAD 对象 ID
TEAMS_ALLOWED_USERS=<你的AAD对象ID>
```

---

<a id="step-5-start-the-gateway"></a>
## 第 5 步：启动网关

```bash
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d gateway
```

这将启动网关。默认的 Webhook 端口是 `3978`（可通过 `TEAMS_PORT` 覆盖）。检查是否正常运行：

```bash
curl http://localhost:3978/health   # 应返回：ok
docker logs -f hermes
```

查看日志中是否出现：
```
[teams] Webhook 服务器正在监听 0.0.0.0:3978/api/messages
```

## 配置参考

### 环境变量

| 变量 | 说明 |
|----------|-------------|
| `TEAMS_CLIENT_ID` | Azure AD 应用（客户端）ID |
| `TEAMS_CLIENT_SECRET` | Azure AD 客户端密钥 |
| `TEAMS_TENANT_ID` | Azure AD 租户 ID |
| `TEAMS_ALLOWED_USERS` | 允许使用该机器人的 AAD 对象 ID（以逗号分隔） |
| `TEAMS_ALLOW_ALL_USERS` | 设为 `true` 可跳过白名单，允许任何人使用 |
| `TEAMS_HOME_CHANNEL` | 用于定时/主动消息投递的对话 ID |
| `TEAMS_HOME_CHANNEL_NAME` | 主频道的显示名称 |
| `TEAMS_PORT` | Webhook 端口（默认值：`3978`） |

### config.yaml

或者，通过 `~/.hermes/config.yaml` 进行配置：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      client_id: "your-client-id"
      client_secret: "your-secret"
      tenant_id: "your-tenant-id"
      port: 3978
```
---

<a id="features"></a>
## 功能特性

<a id="interactive-approval-cards"></a>
### 交互式审批卡片（Interactive Approval Cards）

当 Agent 需要执行一条可能有风险的命令时，它会发送一张带有四个按钮的 Adaptive Card，而不是要求你手动输入 `/approve`：

- **单次允许** — 批准本次特定命令
- **会话内允许** — 在当前会话中持续允许该模式
- **始终允许** — 永久允许该模式
- **拒绝** — 拒绝该命令

点击任一按钮即可直接完成审批，卡片会随即替换为决策结果。

<a id="meeting-summary-delivery-teams-meeting-pipeline"></a>
### 会议纪要投递（Teams Meeting Pipeline）

当启用了 [Teams 会议 Pipeline 插件](/user-guide/messaging/msgraph-webhook) 后，本适配器也负责会议纪要的出站投递——用一个 Teams 集成入口，而不是两个。会议转录内容被总结后，写手会将纪要发布到你指定的 Teams 目标。

Pipeline 纪要投递的配置位于 `teams` 平台条目下，与机器人配置一起：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      # 已有的机器人配置（client_id、client_secret、tenant_id、port）...

      # 会议纪要投递（仅在启用 teams_pipeline 插件时使用）
      delivery_mode: "graph"       # 或 "incoming_webhook"
      # 当 delivery_mode 为 graph 时——选择以下其一：
      chat_id: "19:meeting_..."    # 投递到 Teams 聊天
      # team_id: "..."             # 或投递到频道
      # channel_id: "..."
      # access_token: "..."        # 可选；如果未提供则使用 MSGRAPH_* 应用凭据
      # 当 delivery_mode 为 incoming_webhook 时：
      # incoming_webhook_url: "https://outlook.office.com/webhook/..."
```
| 模式 | 使用场景 | 权衡 |
|------|----------|-----------|
| `incoming_webhook` | 简单的“向此频道发布摘要”，使用静态 Teams 生成的 URL。 | 无回复线程，无反应，显示为 webhook 的配置身份。 |
| `graph` | 通过 Microsoft Graph 在机器人身份下发布线程频道帖子或 1:1/群聊帖子。 | 需要具有 `ChannelMessage.Send`（频道）或 `Chat.ReadWrite.All`（聊天）应用程序权限的 [Graph 应用注册](/guides/microsoft-graph-app-registration)。 |

如果 `teams_pipeline` 插件**没有**启用，这些设置是无效的——只有当管道运行时绑定到 Graph webhook 入口时才会生效。

---

<a id="production-deployment"></a>
## 生产部署 {#production-deployment}

对于永久服务器，跳过 devtunnel，并将机器人注册到服务器的公共 HTTPS 端点：

```bash
teams app create \
  --name "Hermes" \
  --endpoint "https://your-domain.com/api/messages"
```

如果已经创建了机器人并且只需要更新端点：
```bash
teams app update --id <teamsAppId> --endpoint "https://your-domain.com/api/messages"
```

请确保你配置的端口（`TEAMS_PORT`，默认 `3978`）可以从互联网访问，并且你的 TLS 证书是有效的——Teams 会拒绝自签名证书。

---

<a id="troubleshooting"></a>
## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `health` 端点正常，但机器人不响应 | 检查你的隧道是否仍在运行，并且机器人的消息端点是否与隧道 URL 匹配 |
| 日志中出现 `KeyError: 'teams'` | 重启容器——此问题已在当前版本中修复 |
| 机器人响应认证错误 | 确认 `TEAMS_CLIENT_ID`、`TEAMS_CLIENT_SECRET` 和 `TEAMS_TENANT_ID` 都已正确设置 |
| `未配置推理提供者` | 检查 `~/.hermes/.env` 中是否设置了 `ANTHROPIC_API_KEY`（或其他提供者的密钥） |
| 机器人收到消息但忽略它们 | 你的 AAD 对象 ID 可能不在 `TEAMS_ALLOWED_USERS` 中。运行 `teams status --verbose` 来查找它 |
| 隧道 URL 在重启后改变 | 如果你使用命名隧道（`devtunnel create hermes-bot`），devtunnel URL 是持久的。ngrok 和 cloudflared 每次运行都会生成新 URL，除非你有付费计划——当 URL 改变时，使用 `teams app update` 更新机器人端点 |
| Teams 显示“此机器人未响应” | Webhook 返回了错误。检查 `docker logs hermes` 中的回溯信息 |
| 日志中出现 `[teams] 连接失败` | SDK 认证失败。请仔细检查你的凭据，并确保租户 ID 与你用于 `teams login` 的账户匹配 |
<a id="security"></a>
## 安全性

:::warning
**务必设置 `TEAMS_ALLOWED_USERS`**，填入授权用户的 Azure AD 对象 ID。若不设置，任何能找到或安装你 Bot 的人都可以与之交互。

将 `TEAMS_CLIENT_SECRET` 视为密码——定期通过 Azure 门户或 Teams CLI 轮换。
:::

- 将凭据存储在 `~/.hermes/.env` 中，权限设为 `600`（`chmod 600 ~/.hermes/.env`）
- Bot 只接受 `TEAMS_ALLOWED_USERS` 中用户的消息；未经授权的消息会被静默丢弃
- 你的公共端点（`/api/messages`）由 Teams Bot Framework 进行身份验证——缺少有效 JWT 的请求会被拒绝

<a id="related-docs"></a>
## 相关文档

- [Teams Meetings](/user-guide/messaging/teams-meetings)
- [Operate the Teams Meeting Pipeline](/guides/operate-teams-meeting-pipeline)
