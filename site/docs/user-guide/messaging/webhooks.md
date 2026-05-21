---
sidebar_position: 13
title: "Webhooks"
description: "接收来自 GitHub、GitLab 及其他服务的事件，触发 Hermes Agent 运行"
---

<a id="webhooks"></a>
# Webhooks

接收来自外部服务（GitHub、GitLab、JIRA、Stripe 等）的事件，并自动触发 Hermes Agent 运行。Webhook 适配器运行一个 HTTP 服务器，该服务器接受 POST 请求、验证 HMAC 签名、将负载转换为 Agent 提示词，并将响应路由回源平台或另一个已配置的平台。

Agent 处理事件后，可以通过在 PR 上发布评论、向 Telegram/Discord 发送消息或记录结果来做出响应。

<a id="video-tutorial"></a>
## 视频教程

<div style={{position: 'relative', width: '100%', aspectRatio: '16 / 9', marginBottom: '1.5rem'}}>
  <iframe
    src="https://www.youtube.com/embed/WNYe5mD4fY8"
    title="Hermes Agent — Webhooks 教程"
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0}}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

---

<a id="quick-start"></a>
## 快速开始

1. 通过 `hermes gateway setup` 或环境变量启用
2. 在 `config.yaml` 中定义路由，**或**使用 `hermes webhook subscribe` 动态创建路由
3. 将你的服务指向 `http://your-server:8644/webhooks/&lt;route-name&gt;`

---

<a id="setup"></a>
## 设置

有两种方式可以启用 webhook 适配器。

<a id="via-setup-wizard"></a>
### 通过设置向导

```bash
hermes gateway setup
```

按照提示启用 webhooks、设置端口以及设置全局 HMAC 密钥。

<a id="via-environment-variables"></a>
### 通过环境变量

添加到 `~/.hermes/.env`：

```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644        # 默认端口
WEBHOOK_SECRET=your-global-secret
```

<a id="verify-the-server"></a>
### 验证服务器

网关运行后：

```bash
curl http://localhost:8644/health
```

预期响应：

```json
{"status": "ok", "platform": "webhook"}
```

---

## 配置路由 {#configuring-routes}

路由定义了如何处理不同的 webhook 来源。每个路由都是 `config.yaml` 中 `platforms.webhook.extra.routes` 下的一个命名条目。

<a id="route-properties"></a>
### 路由属性

| 属性 | 是否必需 | 描述 |
|----------|----------|-------------|
| `events` | 否 | 要接受的事件类型列表（例如 `["pull_request"]`）。如果为空，则接受所有事件。事件类型从 `X-GitHub-Event`、`X-GitLab-Event` 或负载中的 `event_type` 读取。 |
| `secret` | **是** | 用于签名验证的 HMAC 密钥。如果路由上未设置，则回退到全局 `secret`。仅用于测试时设置为 `"INSECURE_NO_AUTH"`（跳过验证）。 |
| `prompt` | 否 | 模板字符串，支持点号表示法访问负载（例如 `{pull_request.title}`）。如果省略，完整的 JSON 负载将被转储到提示词中。 |
| `skills` | 否 | 要为 Agent 运行加载的技能名称列表。 |
| `deliver` | 否 | 响应发送目标：`github_comment`、`telegram`、`discord`、`slack`、`signal`、`sms`、`whatsapp`、`matrix`、`mattermost`、`homeassistant`、`email`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot` 或 `log`（默认）。 |
| `deliver_extra` | 否 | 额外的投递配置——键值取决于 `deliver` 类型（例如 `repo`、`pr_number`、`chat_id`）。值支持与 `prompt` 相同的 `{dot.notation}` 模板。 |
| `deliver_only` | 否 | 如果为 `true`，则完全跳过 Agent——渲染后的 `prompt` 模板将成为直接投递的文字消息。零 LLM 成本，亚秒级投递。用例请参见[直接投递模式](#direct-delivery-mode)。要求 `deliver` 是一个真实的目标（不能是 `log`）。 |
<a id="full-example"></a>
### 完整示例

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "global-fallback-secret"
      routes:
        github-pr:
          events: ["pull_request"]
          secret: "github-webhook-secret"
          prompt: |
            Review this pull request:
            Repository: {repository.full_name}
            PR #{number}: {pull_request.title}
            Author: {pull_request.user.login}
            URL: {pull_request.html_url}
            Diff URL: {pull_request.diff_url}
            Action: {action}
          skills: ["github-code-review"]
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{number}"
        deploy-notify:
          events: ["push"]
          secret: "deploy-secret"
          prompt: "New push to {repository.full_name} branch {ref}: {head_commit.message}"
          deliver: "telegram"
```

<a id="prompt-templates"></a>
### 提示模板

提示使用点号表示法来访问 webhook 负载中的嵌套字段：

- `{pull_request.title}` 解析为 `payload["pull_request"]["title"]`
- `{repository.full_name}` 解析为 `payload["repository"]["full_name"]`
- `{__raw__}` — 特殊令牌，将**整个负载**转储为缩进 JSON（截断至 4000 个字符）。适用于监控告警或通用 webhook，此时 Agent 需要获取完整上下文。
- 缺失的键会原样保留为 `{key}` 字符串（不会报错）
- 嵌套字典和列表会被序列化为 JSON 并截断至 2000 个字符

你可以将 `{__raw__}` 与常规模板变量混合使用：

```yaml
prompt: "PR #{pull_request.number} by {pull_request.user.login}: {__raw__}"
```

如果某个路由未配置 `prompt` 模板，则整个负载会被转储为缩进 JSON（截断至 4000 个字符）。

同样的点号表示法模板也适用于 `deliver_extra` 的值。

<a id="forum-topic-delivery"></a>
### 论坛主题投递

将 webhook 响应投递到 Telegram 时，你可以在 `deliver_extra` 中包含 `message_thread_id`（或 `thread_id`）来指定具体的论坛主题：

```yaml
webhooks:
  routes:
    alerts:
      events: ["alert"]
      prompt: "Alert: {__raw__}"
      deliver: "telegram"
      deliver_extra:
        chat_id: "-1001234567890"
        message_thread_id: "42"
```

如果 `deliver_extra` 中未提供 `chat_id`，则投递会回退到目标平台配置的主频道。

---

## GitHub PR 审查（分步指南） {#github-pr-review}

本教程将设置每次拉取请求的自动代码审查。

<a id="1-create-the-webhook-in-github"></a>
### 1. 在 GitHub 中创建 webhook

1. 进入你的仓库 → **Settings** → **Webhooks** → **Add webhook**
2. 将 **Payload URL** 设置为 `http://your-server:8644/webhooks/github-pr`
3. 将 **Content type** 设置为 `application/json`
4. 将 **Secret** 设置为与你的路由配置匹配（例如 `github-webhook-secret`）
5. 在 **Which events?** 下，选择 **Let me select individual events** 并勾选 **Pull requests**
6. 点击 **Add webhook**

<a id="2-add-the-route-config"></a>
### 2. 添加路由配置

按上方示例，将 `github-pr` 路由添加到 `~/.hermes/config.yaml` 中。
<a id="3-ensure-gh-cli-is-authenticated"></a>
### 3. 确保 `gh` CLI 已认证

`github_comment` 交付类型使用 GitHub CLI 发表评论：

```bash
gh auth login
```

<a id="4-test-it"></a>
### 4. 测试

在仓库中打开一个 Pull Request。Webhook 被触发，Hermes 处理事件，并在 PR 上发布一条审查评论。

---

## GitLab Webhook 设置 {#gitlab-webhook-setup}

GitLab 的 webhook 工作方式类似，但使用不同的认证机制。GitLab 将密钥作为纯文本的 `X-Gitlab-Token` 头部发送（精确字符串匹配，不是 HMAC）。

<a id="1-create-the-webhook-in-gitlab"></a>
### 1. 在 GitLab 中创建 webhook

1. 进入项目 → **Settings** → **Webhooks**
2. 将 **URL** 设置为 `http://your-server:8644/webhooks/gitlab-mr`
3. 输入你的 **Secret token**
4. 选择 **Merge request events**（以及任何你想要的其他事件）
5. 点击 **Add webhook**

<a id="2-add-the-route-config"></a>
### 2. 添加路由配置

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        gitlab-mr:
          events: ["merge_request"]
          secret: "your-gitlab-secret-token"
          prompt: |
            Review this merge request:
            Project: {project.path_with_namespace}
            MR !{object_attributes.iid}: {object_attributes.title}
            Author: {object_attributes.last_commit.author.name}
            URL: {object_attributes.url}
            Action: {object_attributes.action}
          deliver: "log"
```

---

## 交付选项 {#delivery-options}

`deliver` 字段控制 Agent 处理 webhook 事件后，响应的去向。

| 交付类型 | 描述 |
|-------------|-------------|
| `log` | 将响应记录到网关日志输出。这是默认选项，适合测试。 |
| `github_comment` | 通过 `gh` CLI 将响应作为 PR/Issue 评论发布。需要在 `deliver_extra` 中指定 `repo` 和 `pr_number`。网关主机上必须安装并认证 `gh` CLI（`gh auth login`）。 |
| `telegram` | 将响应路由到 Telegram。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `discord` | 将响应路由到 Discord。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `slack` | 将响应路由到 Slack。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `signal` | 将响应路由到 Signal。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `sms` | 通过 Twilio 将响应路由到短信。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `whatsapp` | 将响应路由到 WhatsApp。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `matrix` | 将响应路由到 Matrix。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `mattermost` | 将响应路由到 Mattermost。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `homeassistant` | 将响应路由到 Home Assistant。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `email` | 将响应路由到电子邮件。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `dingtalk` | 将响应路由到钉钉。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `feishu` | 将响应路由到飞书 / Lark。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `wecom` | 将响应路由到企业微信。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `weixin` | 将响应路由到微信。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `bluebubbles` | 将响应路由到 BlueBubbles（iMessage）。默认使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
为了实现跨平台投递，目标平台也必须在网关中启用并连接。如果在 `deliver_extra` 中没有提供 `chat_id`，则响应会发送到该平台配置的默认频道。

---

## 直接投递模式 {#direct-delivery-mode}

默认情况下，每次 webhook POST 都会触发一次 Agent 运行——请求体成为提示词，Agent 处理它，然后 Agent 的响应被投递。这会在每次事件中消耗 LLM token。

对于你只想**推送一条纯通知**的场景——不需要推理、不需要 Agent 循环，只需投递消息——可以在路由上设置 `deliver_only: true`。渲染后的 `prompt` 模板会成为字面消息体，适配器会直接将其分派到配置的投递目标。

<a id="when-to-use-direct-delivery"></a>
### 何时使用直接投递

- **外部服务推送** — Supabase/Firebase webhook 在数据库变更时触发 → 立即通知 Telegram 用户
- **监控告警** — Datadog/Grafana 告警 webhook → 推送到 Discord 频道
- **Agent 间 ping** — Agent A 通知 Agent B 的用户某个长时间运行的任务已完成
- **后台任务完成** — Cron 任务完成 → 将结果发布到 Slack

优势：

- **零 LLM token 消耗** — 从不调用 Agent
- **亚秒级投递** — 单次适配器调用，无推理循环
- **与 Agent 模式相同的安全性** — HMAC 认证、速率限制、幂等性和消息体大小限制仍然适用
- **同步响应** — 投递成功后 POST 返回 `200 OK`，如果目标拒绝则返回 `502`，这样上游服务可以智能重试

<a id="example-telegram-push-from-supabase"></a>
### 示例：从 Supabase 推送到 Telegram

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "global-secret"
      routes:
        antenna-matches:
          secret: "antenna-webhook-secret"
          deliver: "telegram"
          deliver_only: true
          prompt: "🎉 新匹配：{match.user_name} 与您匹配成功！"
          deliver_extra:
            chat_id: "{match.telegram_chat_id}"
```

你的 Supabase 边缘函数使用 HMAC-SHA256 对请求体签名，并 POST 到 `https://your-server:8644/webhooks/antenna-matches`。Webhook 适配器验证签名，从请求体中渲染模板，投递到 Telegram，然后返回 `200 OK`。

<a id="example-dynamic-subscription-via-cli"></a>
### 示例：通过 CLI 动态订阅

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 新匹配：{match.user_name} 与您匹配成功！" \
  --description "Antenna 匹配通知"
```

<a id="response-codes"></a>
### 响应码

| 状态码 | 含义 |
|--------|---------|
| `200 OK` | 投递成功。响应体：`{"status": "delivered", "route": "...", "target": "...", "delivery_id": "..."}` |
| `200 OK` (status=duplicate) | 在幂等性 TTL（1 小时）内出现重复的 `X-GitHub-Delivery` ID。不会重新投递。 |
| `401 Unauthorized` | HMAC 签名无效或缺失。 |
| `400 Bad Request` | JSON 请求体格式错误。 |
| `404 Not Found` | 未知的路由名称。 |
| `413 Payload Too Large` | 请求体超过 `max_body_bytes`。 |
| `429 Too Many Requests` | 路由速率限制已超。 |
| `502 Bad Gateway` | 目标适配器拒绝消息或抛出异常。错误会在服务端记录；响应体为通用的 `Delivery failed`，以避免泄露适配器内部信息。 |
<a id="configuration-gotchas"></a>
### 配置注意事项

- `deliver_only: true` 要求 `deliver` 必须是一个真实的目标。如果设置为 `deliver: log`（或省略 `deliver`），启动时会被拒绝——适配器在发现路由配置错误时会拒绝启动。
- 在直接投递模式下，`skills` 字段会被忽略（因为没有 Agent 运行，所以没有地方注入技能）。
- 模板渲染使用与 Agent 模式相同的 `{dot.notation}` 语法，包括 `{__raw__}` 令牌。
- 幂等性使用相同的 `X-GitHub-Delivery` / `X-Request-ID` 头部——使用相同 ID 重试会返回 `status=duplicate`，并且**不会**重新投递。

---

## 动态订阅 (CLI) {#dynamic-subscriptions}

除了 `config.yaml` 中的静态路由，你还可以使用 `hermes webhook` CLI 命令动态创建 webhook 订阅。当 Agent 本身需要设置事件驱动的触发器时，这尤其有用。

<a id="create-a-subscription"></a>
### 创建订阅

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New issue #{issue.number}: {issue.title}\nBy: {issue.user.login}\n\n{issue.body}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789" \
  --description "Triage new GitHub issues"
```

这会返回 webhook URL 和一个自动生成的 HMAC 密钥。请配置你的服务向该 URL 发送 POST 请求。

<a id="list-subscriptions"></a>
### 列出订阅

```bash
hermes webhook list
```

<a id="remove-a-subscription"></a>
### 删除订阅

```bash
hermes webhook remove github-issues
```

<a id="test-a-subscription"></a>
### 测试订阅

```bash
hermes webhook test github-issues
hermes webhook test github-issues --payload '{"issue": {"number": 42, "title": "Test"}}'
```

<a id="how-dynamic-subscriptions-work"></a>
### 动态订阅的工作原理

- 订阅信息存储在 `~/.hermes/webhook_subscriptions.json` 文件中
- webhook 适配器会在每次收到请求时热重载该文件（基于 mtime 检查，开销可忽略）
- `config.yaml` 中的静态路由始终优先于同名的动态路由
- 动态订阅使用与静态路由相同的路由格式和能力（事件、提示模板、技能、投递）
- 无需重启网关——订阅后立即生效

<a id="agent-driven-subscriptions"></a>
### Agent 驱动的订阅

当 `webhook-subscriptions` 技能被引导时，Agent 可以通过终端工具创建订阅。让 Agent "为 GitHub issues 设置一个 webhook"，它就会执行相应的 `hermes webhook subscribe` 命令。

---

## 安全性 {#security}

webhook 适配器包含多层安全机制：

<a id="hmac-signature-validation"></a>
### HMAC 签名验证

适配器会根据每个来源使用相应的方法验证传入的 webhook 签名：

- **GitHub**：`X-Hub-Signature-256` 头部——以 `sha256=` 为前缀的 HMAC-SHA256 十六进制摘要
- **GitLab**：`X-Gitlab-Token` 头部——纯文本密钥字符串匹配
- **通用**：`X-Webhook-Signature` 头部——原始 HMAC-SHA256 十六进制摘要

如果配置了密钥但未检测到可识别的签名头部，请求将被拒绝。

<a id="secret-is-required"></a>
### 密钥是必需的

每个路由都必须有一个密钥——要么直接在路由上设置，要么从全局 `secret` 继承。没有密钥的路由会导致适配器在启动时失败并报错。仅用于开发/测试时，你可以将密钥设置为 `"INSECURE_NO_AUTH"` 以完全跳过验证。
`INSECURE_NO_AUTH` 仅在网关绑定到回环地址（`127.0.0.1`、`localhost`、`::1`）时被接受。如果与非回环绑定（如 `0.0.0.0` 或局域网 IP）一起使用，适配器将拒绝启动——这可以防止意外地在公共接口暴露未经认证的端点。

<a id="rate-limiting"></a>
### 速率限制

默认情况下，每个路由的速率限制为每分钟 **30 次请求**（固定窗口）。全局配置方式如下：

```yaml
platforms:
  webhook:
    extra:
      rate_limit: 60  # 每分钟请求数
```

超出限制的请求将收到 `429 Too Many Requests` 响应。

<a id="idempotency"></a>
### 幂等性

投递 ID（来自 `X-GitHub-Delivery`、`X-Request-ID` 或时间戳兜底）会被缓存 **1 小时**。重复投递（例如 webhook 重试）将被静默跳过，返回 `200` 响应，从而避免重复运行 Agent。

<a id="body-size-limits"></a>
### 请求体大小限制

超过 **1 MB** 的请求体会在读取之前被拒绝。配置方式如下：

```yaml
platforms:
  webhook:
    extra:
      max_body_bytes: 2097152  # 2 MB
```

<a id="prompt-injection-risk"></a>
### 提示注入风险

:::warning
Webhook 请求体包含攻击者可控的数据——PR 标题、提交信息、Issue 描述等都可能包含恶意指令。当网关暴露在互联网上时，请在沙箱环境（Docker、VM）中运行。建议使用 Docker 或 SSH 终端后端进行隔离。
:::

---

## 故障排除 {#troubleshooting}

<a id="webhook-not-arriving"></a>
### Webhook 未送达

- 确认端口已暴露且 webhook 来源可以访问
- 检查防火墙规则——端口 `8644`（或你配置的端口）必须开放
- 确认 URL 路径匹配：`http://your-server:8644/webhooks/&lt;route-name&gt;`
- 使用 `/health` 端点确认服务器正在运行

<a id="signature-validation-failing"></a>
### 签名验证失败

- 确保路由配置中的 secret 与 webhook 来源配置的 secret 完全一致
- 对于 GitHub，secret 是基于 HMAC 的——检查 `X-Hub-Signature-256`
- 对于 GitLab，secret 是纯令牌匹配——检查 `X-Gitlab-Token`
- 检查网关日志中的 `Invalid signature` 警告

<a id="event-being-ignored"></a>
### 事件被忽略

- 确认事件类型在路由的 `events` 列表中
- GitHub 事件使用类似 `pull_request`、`push`、`issues` 的值（`X-GitHub-Event` 头字段值）
- GitLab 事件使用类似 `merge_request`、`push` 的值（`X-GitLab-Event` 头字段值）
- 如果 `events` 为空或未设置，则接受所有事件

<a id="agent-not-responding"></a>
### Agent 无响应

- 在前台运行网关以查看日志：`hermes gateway run`
- 检查提示模板是否渲染正确
- 确认投递目标已配置且已连接

<a id="duplicate-responses"></a>
### 重复响应

- 幂等缓存应能防止此问题——检查 webhook 来源是否发送了投递 ID 头（`X-GitHub-Delivery` 或 `X-Request-ID`）
- 投递 ID 会被缓存 1 小时

<a id="gh-cli-errors-github-comment-delivery"></a>
### `gh` CLI 错误（GitHub 评论投递）

- 在网关主机上运行 `gh auth login`
- 确保经过身份验证的 GitHub 用户对仓库具有写入权限
- 确认已安装 `gh` 且位于 PATH 中
---

## 环境变量 {#environment-variables}

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `WEBHOOK_ENABLED` | 启用 webhook 平台适配器 | `false` |
| `WEBHOOK_PORT` | 接收 webhook 的 HTTP 服务器端口 | `8644` |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥（当路由未指定自己的密钥时作为备用） | _（无）_ |
