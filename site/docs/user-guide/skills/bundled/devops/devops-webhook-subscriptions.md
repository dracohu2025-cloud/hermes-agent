---
title: "Webhook 订阅 — Webhook 订阅：事件驱动的 Agent 运行"
sidebar_label: "Webhook 订阅"
description: "Webhook 订阅：事件驱动的 Agent 运行"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Webhook 订阅 {#webhook-subscriptions}

Webhook 订阅：事件驱动的 Agent 运行。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/webhook-subscriptions` |
| 版本 | `1.1.0` |
| 标签 | `webhook`、`events`、`automation`、`integrations`、`notifications`、`push` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="webhook-subscriptions"></a>
# Webhook 订阅

创建动态 webhook 订阅，使外部服务（GitHub、GitLab、Stripe、CI/CD、IoT 传感器、监控工具）可以通过向 URL 发送 POST 事件来触发 Hermes Agent 运行。

## 设置（必须先完成） {#setup-required-first}

必须先启用 webhook 平台，然后才能创建订阅。使用以下命令检查：
```bash
hermes webhook list
```

如果显示“Webhook platform is not enabled”，请进行设置：

### 选项 1：设置向导 {#option-1-setup-wizard}
```bash
hermes gateway setup
```
按照提示启用 webhook、设置端口和全局 HMAC 密钥。

### 选项 2：手动配置 {#option-2-manual-config}
在 `~/.hermes/config.yaml` 中添加：
```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8644
      secret: "generate-a-strong-secret-here"
```

### 选项 3：环境变量 {#option-3-environment-variables}
在 `~/.hermes/.env` 中添加：
```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644
WEBHOOK_SECRET=generate-a-strong-secret-here
```

配置完成后，启动（或重启）网关：
```bash
hermes gateway run
# 或者如果使用 systemd：
systemctl --user restart hermes-gateway
```

验证是否正在运行：
```bash
curl http://localhost:8644/health
```

## 命令 {#commands}

所有管理操作均通过 `hermes webhook` CLI 命令完成：

### 创建订阅 {#create-a-subscription}
```bash
hermes webhook subscribe <name> \
  --prompt "Prompt template with {payload.fields}" \
  --events "event1,event2" \
  --description "What this does" \
  --skills "skill1,skill2" \
  --deliver telegram \
  --deliver-chat-id "12345" \
  --secret "optional-custom-secret"
```

返回 webhook URL 和 HMAC 密钥。用户配置其服务向该 URL 发送 POST 请求。

### 列出订阅 {#list-subscriptions}
```bash
hermes webhook list
```

### 删除订阅 {#remove-a-subscription}
```bash
hermes webhook remove <name>
```

### 测试订阅 {#test-a-subscription}
```bash
hermes webhook test <name>
hermes webhook test <name> --payload '{"key": "value"}'
```

## 提示模板 {#prompt-templates}

提示支持使用 `{dot.notation}` 访问嵌套的 payload 字段：

- `{issue.title}` — GitHub issue 标题
- `{pull_request.user.login}` — PR 作者
- `{data.object.amount}` — Stripe 支付金额
- `{sensor.temperature}` — IoT 传感器读数

如果未指定提示，则完整的 JSON payload 会被直接放入 Agent 提示中。

## 常见模式 {#common-patterns}

### GitHub：新 issue {#github-new-issues}
```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New GitHub issue #{issue.number}: {issue.title}\n\nAction: {action}\nAuthor: {issue.user.login}\nBody:\n{issue.body}\n\nPlease triage this issue." \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```
### GitHub: PR 审查 {#github-pr-reviews}
```bash
hermes webhook subscribe github-prs \
  --events "pull_request" \
  --prompt "PR #{pull_request.number} {action}: {pull_request.title}\nBy: {pull_request.user.login}\nBranch: {pull_request.head.ref}\n\n{pull_request.body}" \
  --skills "github-code-review" \
  --deliver github_comment
```

### Stripe：支付事件 {#stripe-payment-events}
```bash
hermes webhook subscribe stripe-payments \
  --events "payment_intent.succeeded,payment_intent.payment_failed" \
  --prompt "Payment {data.object.status}: {data.object.amount} cents from {data.object.receipt_email}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```

### CI/CD：构建通知 {#ci-cd-build-notifications}
```bash
hermes webhook subscribe ci-builds \
  --events "pipeline" \
  --prompt "Build {object_attributes.status} on {project.name} branch {object_attributes.ref}\nCommit: {commit.message}" \
  --deliver discord \
  --deliver-chat-id "1234567890"
```

### 通用监控告警 {#generic-monitoring-alert}
```bash
hermes webhook subscribe alerts \
  --prompt "Alert: {alert.name}\nSeverity: {alert.severity}\nMessage: {alert.message}\n\nPlease investigate and suggest remediation." \
  --deliver origin
```

### 直接投递（无 Agent，零 LLM 成本） {#direct-delivery-no-agent-zero-llm-cost}

对于你只是想推送一条通知到用户聊天窗口的场景——无需推理，无需 Agent 循环——只需添加 `--deliver-only` 参数。渲染后的 `--prompt` 模板将成为字面的消息体，直接发送到目标适配器。

使用场景：
- 外部服务推送通知（Supabase/Firebase webhooks → Telegram）
- 需要逐字转发的监控告警
- Agent 之间的 ping 消息，其中一个 Agent 告诉另一个 Agent 的用户某些信息
- 任何不需要 LLM 往返处理的 webhook

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 New match: {match.user_name} matched with you!" \
  --description "Antenna match notifications"
```

成功投递时 POST 返回 `200 OK`，目标失败时返回 `502`——这样上游服务可以智能重试。HMAC 认证、速率限制和幂等性依然适用。

要求 `--deliver` 必须是真实的目标（telegram、discord、slack、github_comment 等）——`--deliver log` 会被拒绝，因为仅日志输出直接投递毫无意义。

## 安全性 {#security}

- 每个订阅都会获得一个自动生成的 HMAC-SHA256 密钥（你也可以通过 `--secret` 自行提供）
- Webhook 适配器在每次收到的 POST 请求上验证签名
- `config.yaml` 中的静态路由无法被动态订阅覆盖
- 订阅会持久化到 `~/.hermes/webhook_subscriptions.json`

## 工作原理 {#how-it-works}

1. `hermes webhook subscribe` 将配置写入 `~/.hermes/webhook_subscriptions.json`
2. Webhook 适配器在每次收到请求时热重载该文件（基于修改时间，开销可忽略）
3. 当收到匹配路由的 POST 请求时，适配器格式化 prompt 并触发 Agent 运行
4. Agent 的响应被投递到配置的目标（Telegram、Discord、GitHub 评论等）
## 故障排查 {#troubleshooting}

如果 webhook 不工作：

1. **网关是否在运行？** 使用 `systemctl --user status hermes-gateway` 或 `ps aux | grep gateway` 检查
2. **webhook 服务器是否在监听？** `curl http://localhost:8644/health` 应返回 `{"status": "ok"}`
3. **检查网关日志：** `grep webhook ~/.hermes/logs/gateway.log | tail -20`
4. **签名不匹配？** 验证服务中的密钥与 `hermes webhook list` 中的密钥是否一致。GitHub 发送 `X-Hub-Signature-256`，GitLab 发送 `X-Gitlab-Token`。
5. **防火墙/NAT 问题？** webhook URL 必须能被服务访问。对于本地开发，请使用隧道（ngrok、cloudflared）。
6. **事件类型错误？** 检查 `--events` 过滤器是否与服务发送的事件匹配。使用 `hermes webhook test &lt;name&gt;` 验证路由是否正常工作。
