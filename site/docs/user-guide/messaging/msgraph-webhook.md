---
sidebar_position: 23
title: "Microsoft Graph Webhook Listener"
description: "在 Hermes 中接收 Microsoft Graph 变更通知（会议、日历、聊天等）"
---

<a id="microsoft-graph-webhook-listener"></a>
# Microsoft Graph Webhook 监听器

`msgraph_webhook` 网关平台是一个入站事件监听器。Hermes 通过它接收来自 Microsoft Graph 的**变更通知**——例如“某 Teams 会议已结束”、“某个聊天中收到新消息”、“某日历事件已更新”。与 `teams` 平台（用户向其输入消息的聊天机器人）不同，这个平台是 M365 主动告知 Hermes 发生了某事，而非由人发起。

当前的主要消费者是 Teams 会议摘要流水线：Graph 在会议生成转录时发送通知，流水线获取转录，然后 Hermes 将摘要发布回 Teams。其他 Graph 资源（`/chats/.../messages`、`/users/.../events`）使用相同的监听器——各流水线消费者通过各自的 PR 接入。

<a id="prerequisites"></a>
## 前提条件

- Microsoft Graph 应用程序凭据——[注册一个 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration)
- Microsoft Graph 可访问的**公共 HTTPS URL**（Graph 不会调用私有端点）。开发隧道可用于测试；生产环境需要一个真实域名和有效证书。
- 一个强度较高的共享密钥，用作 `clientState` 值。使用 `openssl rand -hex 32` 生成，并将其放入 `~/.hermes/.env` 中作为 `MSGRAPH_WEBHOOK_CLIENT_STATE`。

<a id="quick-start"></a>
## 快速开始

最小的 `~/.hermes/config.yaml`：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      port: 8646
      client_state: "replace-with-a-strong-secret"
      accepted_resources:
        - "communications/onlineMeetings"
```

或通过 `~/.hermes/.env` 环境变量（启动时自动合并）：

```bash
MSGRAPH_WEBHOOK_ENABLED=true
MSGRAPH_WEBHOOK_PORT=8646
MSGRAPH_WEBHOOK_CLIENT_STATE=<generate-with-openssl-rand-hex-32>
MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES=communications/onlineMeetings
```

启动网关：`hermes gateway run`。监听器暴露以下端点：

- `POST /msgraph/webhook` ——来自 Graph 的变更通知
- `GET /msgraph/webhook?validationToken=...` ——Graph 订阅验证握手
- `GET /health` ——健康检查端点，包含已接受/重复计数

将监听器公开暴露（反向代理、开发隧道、Ingress）。你的 Graph 订阅通知 URL 是你的公共 HTTPS 来源后跟 `/msgraph/webhook`：

```
https://ops.example.com/msgraph/webhook
```

<a id="configuration"></a>
## 配置

所有设置均位于 `platforms.msgraph_webhook.extra` 下：

| 设置 | 默认值 | 描述 |
|---------|---------|-------------|
| `host` | `0.0.0.0` | HTTP 监听器的绑定地址。 |
| `port` | `8646` | 绑定端口。 |
| `webhook_path` | `/msgraph/webhook` | Graph 发送 POST 请求的 URL 路径。 |
| `health_path` | `/health` | 就绪检查端点。 |
| `client_state` | — | Graph 在每次通知中回传的共享密钥。使用 `hmac.compare_digest` 进行比较——用 `openssl rand -hex 32` 生成。 |
| `accepted_resources` | `[]`（接受所有） | Graph 资源路径/模式的允许列表。末尾的 `*` 表示前缀匹配。允许前导 `/`。示例：`["communications/onlineMeetings", "chats/*/messages"]`。 |
| `max_seen_receipts` | `5000` | 用于通知 ID 去重的缓存大小。达到上限时淘汰最早条目。 |
| `allowed_source_cidrs` | `[]`（允许所有） | 可选的源 IP 允许列表。见下文。 |
每个设置也有对应的环境变量（`MSGRAPH_WEBHOOK_*`），会在网关启动时合并到配置中——请参阅[环境变量参考](/reference/environment-variables#microsoft-graph-teams-meetings)。

<a id="security-hardening"></a>
## 安全加固

<a id="clientstate-is-the-primary-auth-check"></a>
### clientState 是主要的身份验证检查

每条 Graph 通知都包含你订阅时注册的 `clientState` 字符串。监听器会使用时序安全比较，拒绝任何 `clientState` 不匹配的通知。这是微软官方文档中描述的机制——请将该值视为强共享密钥。

如果 `client_state` 未设置，监听器会接受所有格式正确的 POST 请求。**生产环境中切勿不设置该值运行。**

<a id="source-ip-allowlisting-production-deployments"></a>
### 源 IP 白名单（生产部署）

在生产环境中，将监听器限制为微软公布的 Graph Webhook 源 IP 范围。微软在 [Office 365 IP 地址和 URL Web 服务](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) 中记录了出口范围。配置方式如下：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      client_state: "..."
      allowed_source_cidrs:
        - "52.96.0.0/14"
        - "52.104.0.0/14"
        # ...添加当前的 Microsoft 365 "Common" + "Teams" 类别出口范围
```

或者使用环境变量：

```bash
MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS="52.96.0.0/14,52.104.0.0/14"
```

白名单为空 = 接受来自任何地方的请求（默认值；保留开发隧道工作流）。无效的 CIDR 字符串会记录警告并被忽略。**每季度检查一次微软 IP 列表**——它会变化。

<a id="https-termination"></a>
### HTTPS 终止

监听器使用纯 HTTP 协议。请在你的反向代理（Caddy、Nginx、Cloudflare Tunnel、AWS ALB）上终止 TLS，然后通过本地网络将请求代理到监听器。Graph 拒绝向非 HTTPS 端点投递通知，因此不存在未加密流量从 Graph 到达你的路径。

<a id="response-hygiene"></a>
### 响应规范

成功时，监听器返回 `202 Accepted` 状态码和空响应体——内部计数器不会出现在网络响应中。运维人员可以通过 `/health` 端点观察计数。

状态码表：

| 结果 | 状态码 |
|---------|--------|
| 通知被接受或去重 | 202 |
| 验证握手（带 `validationToken` 的 GET 请求） | 200（回显该令牌） |
| 批次中所有项均未通过 clientState 验证 | 403 |
| JSON 格式错误 / 缺少 `value` 数组 / 未知资源 | 400 |
| 源 IP 不在白名单中 | 403 |
| 不带 `validationToken` 的纯 GET 请求 | 400 |

<a id="troubleshooting"></a>
## 故障排查

| 问题 | 检查项 |
|---------|---------------|
| Graph 订阅验证失败 | 公共 URL 可访问，`/msgraph/webhook` 路径匹配，带 `validationToken` 的 GET 请求在 10 秒内以 `text/plain` 格式原样回显该令牌。 |
| 通知已 POST 但未摄入 | `client_state` 与你注册订阅时使用的值一致。如果值发生变化，重新运行 `openssl rand -hex 32` 并创建新订阅。检查 `accepted_resources` 是否包含 Graph 发送的资源路径。 |
| 每条通知都返回 403 | `clientState` 不匹配（伪造，或订阅注册时使用了不同的值）。使用 `hermes teams-pipeline subscribe --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE" ...`（随管道运行时 PR 提供）重新创建订阅。 |
| 监听器启动但 `curl http://localhost:8646/health` 挂起 | 端口绑定冲突。检查 `ss -tlnp | grep 8646`，如有需要更改 `port:`。 |
| 来自微软的真实 Graph 请求返回 403 | 源 IP 白名单范围过窄。临时移除 `allowed_source_cidrs`，确认流量正常，然后扩大列表以包含当前的微软出口范围。 |
<a id="related-docs"></a>
## 相关文档

- [注册 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration) — Azure 应用注册前提
- [环境变量 → Microsoft Graph](/reference/environment-variables#microsoft-graph-teams-meetings) — 完整环境变量列表
- [Microsoft Teams 机器人设置](/user-guide/messaging/teams) — 允许用户在 Teams 中与 Hermes 交谈的不同平台
