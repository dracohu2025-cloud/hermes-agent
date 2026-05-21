---
title: "Webhook 订阅 — Webhook 订阅：事件驱动的 Agent 运行"
sidebar_label: "Webhook 订阅"
description: "Webhook 订阅：事件驱动的 Agent 运行"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="webhook-subscriptions"></a>
# Webhook 订阅

Webhook 订阅：事件驱动的 Agent 运行。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/webhook-subscriptions` |
| 版本 | `1.1.0` |
| 平台 | linux, macos, windows |
| 标签 | `webhook`、`events`、`automation`、`integrations`、`notifications`、`push` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Webhook 订阅

创建动态 webhook 订阅，使外部服务（GitHub、GitLab、Stripe、CI/CD、物联网传感器、监控工具）能够通过向 URL 发送 POST 事件来触发 Hermes Agent 运行。

<a id="setup-required-first"></a>
## 设置（必须先完成）

必须先启用 webhook 平台，才能创建订阅。通过以下命令检查：
```bash
hermes webhook list
```

如果显示“Webhook platform is not enabled”，请进行设置：

<a id="option-1-setup-wizard"></a>
### 选项 1：设置向导
```bash
hermes gateway setup
```
按照提示启用 webhook、设置端口和全局 HMAC 密钥。

<a id="option-2-manual-config"></a>
### 选项 2：手动配置
添加到 `~/.hermes/config.yaml`：
```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8644
      secret: "generate-a-strong-secret-here"
```

<a id="option-3-environment-variables"></a>
### 选项 3：环境变量
添加到 `~/.hermes/.env`：
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

<a id="commands"></a>
## 命令

所有管理操作均通过 `hermes webhook` CLI 命令完成：

<a id="create-a-subscription"></a>
### 创建订阅
```bash
hermes webhook subscribe <name> \
  --prompt "包含 {payload.fields} 的提示模板" \
  --events "event1,event2" \
  --description "此订阅的作用" \
  --skills "skill1,skill2" \
  --deliver telegram \
  --deliver-chat-id "12345" \
  --secret "可选的自定义密钥"
```

返回 webhook URL 和 HMAC 密钥。用户需配置其服务向该 URL 发送 POST 请求。

<a id="list-subscriptions"></a>
### 列出订阅
```bash
hermes webhook list
```

<a id="remove-a-subscription"></a>
### 删除订阅
```bash
hermes webhook remove <name>
```

<a id="test-a-subscription"></a>
### 测试订阅
```bash
hermes webhook test <name>
hermes webhook test <name> --payload '{"key": "value"}'
```

<a id="prompt-templates"></a>
## 提示模板

提示支持使用 `{dot.notation}` 来访问嵌套的 payload 字段：

- `{issue.title}` — GitHub 问题标题
- `{pull_request.user.login}` — PR 作者
- `{data.object.amount}` — Stripe 支付金额
- `{sensor.temperature}` — 物联网传感器读数

如果未指定提示，完整的 JSON payload 将被转储到 Agent 提示中。

<a id="common-patterns"></a>
## 常见模式

<a id="github-new-issues"></a>
### GitHub：新问题
```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "新的 GitHub 问题 #{issue.number}：{issue.title}\n\n操作：{action}\n作者：{issue.user.login}\n正文：\n{issue.body}\n\n请对此问题进行分类。" \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```
然后在 GitHub 仓库 Settings → Webhooks → Add webhook 中：
- Payload URL：返回的 webhook_url
- Content type：application/json
- Secret：返回的 secret
- Events："Issues"

<a id="github-pr-reviews"></a>
### GitHub：PR 审查
```bash
hermes webhook subscribe github-prs \
  --events "pull_request" \
  --prompt "PR #{pull_request.number} {action}: {pull_request.title}\nBy: {pull_request.user.login}\nBranch: {pull_request.head.ref}\n\n{pull_request.body}" \
  --skills "github-code-review" \
  --deliver github_comment
```

<a id="stripe-payment-events"></a>
### Stripe：支付事件
```bash
hermes webhook subscribe stripe-payments \
  --events "payment_intent.succeeded,payment_intent.payment_failed" \
  --prompt "Payment {data.object.status}: {data.object.amount} cents from {data.object.receipt_email}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```

<a id="ci-cd-build-notifications"></a>
### CI/CD：构建通知
```bash
hermes webhook subscribe ci-builds \
  --events "pipeline" \
  --prompt "Build {object_attributes.status} on {project.name} branch {object_attributes.ref}\nCommit: {commit.message}" \
  --deliver discord \
  --deliver-chat-id "1234567890"
```

<a id="generic-monitoring-alert"></a>
### 通用监控告警
```bash
hermes webhook subscribe alerts \
  --prompt "Alert: {alert.name}\nSeverity: {alert.severity}\nMessage: {alert.message}\n\nPlease investigate and suggest remediation." \
  --deliver origin
```

<a id="direct-delivery-no-agent-zero-llm-cost"></a>
### 直接投递（无需 Agent，零 LLM 成本）

对于只需要将通知推送到用户聊天界面的场景——无需推理，无需 Agent 循环——添加 `--deliver-only` 参数。渲染后的 `--prompt` 模板将作为字面消息正文直接发送到目标适配器。

用于以下场景：
- 外部服务推送通知（Supabase/Firebase webhooks → Telegram）
- 需要原样转发的监控告警
- Agent 之间的通知：一个 Agent 向另一个 Agent 的用户发送消息
- 任何使用 LLM 往返会浪费资源的 webhook

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 New match: {match.user_name} matched with you!" \
  --description "Antenna match notifications"
```

POST 请求在投递成功时返回 `200 OK`，目标失败时返回 `502`——这样上游服务可以智能地重试。HMAC 认证、速率限制和幂等性仍然适用。

需要 `--deliver` 指定一个真实的目标（telegram、discord、slack、github_comment 等）——`--deliver log` 会被拒绝，因为仅日志的直接投递毫无意义。

<a id="security"></a>
## 安全性

- 每个订阅都会自动生成一个 HMAC-SHA256 密钥（或通过 `--secret` 自行提供）
- webhook 适配器在每个传入的 POST 请求上验证签名
- `config.yaml` 中的静态路由不能被动态订阅覆盖
- 订阅持久化存储到 `~/.hermes/webhook_subscriptions.json`

<a id="how-it-works"></a>
## 工作原理

1. `hermes webhook subscribe` 将订阅写入 `~/.hermes/webhook_subscriptions.json`
2. webhook 适配器在每个传入请求时热重载该文件（基于 mtime 检查，开销可忽略）
3. 当匹配路由的 POST 请求到达时，适配器格式化 prompt 并触发 Agent 运行
4. Agent 的响应投递到配置的目标（Telegram、Discord、GitHub 评论等）
<a id="troubleshooting"></a>
## 故障排查

如果 Webhook 不工作：

1. **网关是否在运行？** 用 `systemctl --user status hermes-gateway` 或 `ps aux | grep gateway` 检查。
2. **Webhook 服务器是否在监听？** `curl http://localhost:8644/health` 应该返回 `{"status": "ok"}`。
3. **检查网关日志：** `grep webhook ~/.hermes/logs/gateway.log | tail -20`
4. **签名不匹配？** 确认你的服务中使用的密钥与 `hermes webhook list` 中的一致。GitHub 发送 `X-Hub-Signature-256`，GitLab 发送 `X-Gitlab-Token`。
5. **防火墙 / NAT 问题？** Webhook URL 必须能被服务访问到。本地开发时，可使用隧道（ngrok、cloudflared）。
6. **事件类型错误？** 检查 `--events` 过滤器是否与服务发送的事件匹配。使用 `hermes webhook test &lt;name&gt;` 验证路由是否正常。
