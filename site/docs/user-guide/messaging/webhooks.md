---
sidebar_position: 13
title: "Webhooks"
description: "接收来自 GitHub、GitLab 及其他服务的事件，触发 Hermes Agent 运行"
---

# Webhooks {#webhooks}

接收来自外部服务（GitHub、GitLab、JIRA、Stripe 等）的事件，并自动触发 Hermes Agent 运行。Webhook 适配器运行一个 HTTP 服务器，接受 POST 请求，验证 HMAC 签名，将负载转换为 Agent 提示词，并将响应路由回源平台或其他已配置的平台。

Agent 处理事件后，可以通过在 PR 上发布评论、向 Telegram/Discord 发送消息或记录结果来做出响应。

## 视频教程 {#video-tutorial}

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

## 快速开始 {#quick-start}

1. 通过 `hermes gateway setup` 或环境变量启用
2. 在 `config.yaml` 中定义路由，**或**使用 `hermes webhook subscribe` 动态创建路由
3. 将你的服务指向 `http://your-server:8644/webhooks/&lt;route-name&gt;`

---

## 设置 {#setup}

有两种方式启用 webhook 适配器。

### 通过设置向导 {#via-setup-wizard}

```bash
hermes gateway setup
```

按照提示启用 webhook、设置端口以及全局 HMAC 密钥。

### 通过环境变量 {#via-environment-variables}

添加到 `~/.hermes/.env`：

```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644        # 默认端口
WEBHOOK_SECRET=your-global-secret
```

### 验证服务器 {#verify-the-server}

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

路由定义了如何处理不同的 webhook 来源。每条路由是 `config.yaml` 中 `platforms.webhook.extra.routes` 下的一个命名条目。

### 路由属性 {#route-properties}

| 属性 | 是否必需 | 描述 |
|----------|----------|-------------|
| `events` | 否 | 接受的事件类型列表（例如 `["pull_request"]`）。如果为空，则接受所有事件。事件类型从 `X-GitHub-Event`、`X-GitLab-Event` 或负载中的 `event_type` 读取。 |
| `secret` | **是** | 用于签名验证的 HMAC 密钥。如果路由未设置，则回退到全局 `secret`。仅用于测试时可设为 `"INSECURE_NO_AUTH"`（跳过验证）。 |
| `prompt` | 否 | 模板字符串，支持点号表示法访问负载（例如 `{pull_request.title}`）。如果省略，则完整的 JSON 负载会被转储到提示词中。 |
| `skills` | 否 | 要为 Agent 运行加载的技能名称列表。 |
| `deliver` | 否 | 响应发送目标：`github_comment`、`telegram`、`discord`、`slack`、`signal`、`sms`、`whatsapp`、`matrix`、`mattermost`、`homeassistant`、`email`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot` 或 `log`（默认）。 |
| `deliver_extra` | 否 | 额外的投递配置——键取决于 `deliver` 类型（例如 `repo`、`pr_number`、`chat_id`）。值支持与 `prompt` 相同的 `{dot.notation}` 模板。 |
| `deliver_only` | 否 | 如果为 `true`，则完全跳过 Agent——渲染后的 `prompt` 模板直接作为要投递的文字消息。零 LLM 成本，亚秒级投递。用例见[直接投递模式](#direct-delivery-mode)。要求 `deliver` 是一个真实的目标（不能是 `log`）。 |
### 完整示例 {#full-example}

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
            审查此拉取请求：
            仓库：{repository.full_name}
            PR #{number}：{pull_request.title}
            作者：{pull_request.user.login}
            URL：{pull_request.html_url}
            Diff URL：{pull_request.diff_url}
            操作：{action}
          skills: ["github-code-review"]
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{number}"
        deploy-notify:
          events: ["push"]
          secret: "deploy-secret"
          prompt: "新推送至 {repository.full_name} 分支 {ref}：{head_commit.message}"
          deliver: "telegram"
```

### 提示模板 {#prompt-templates}

提示使用点号表示法来访问 webhook 负载中的嵌套字段：

- `{pull_request.title}` 解析为 `payload["pull_request"]["title"]`
- `{repository.full_name}` 解析为 `payload["repository"]["full_name"]`
- `{__raw__}` — 特殊标记，将**整个负载**以缩进 JSON 格式输出（超过 4000 字符时截断）。适用于监控告警或通用 webhook，Agent 需要完整上下文时很有用。
- 缺失的键会保留为字面量 `{key}` 字符串（不会报错）
- 嵌套字典和列表会以 JSON 序列化，并在超过 2000 字符时截断

你可以将 `{__raw__}` 与常规模板变量混合使用：

```yaml
prompt: "PR #{pull_request.number} 由 {pull_request.user.login} 提交：{__raw__}"
```

如果某个路由没有配置 `prompt` 模板，整个负载会以缩进 JSON 格式输出（超过 4000 字符时截断）。

同样的点号表示法模板也适用于 `deliver_extra` 的值。

### 论坛主题投递 {#forum-topic-delivery}

当将 webhook 响应投递到 Telegram 时，你可以通过在 `deliver_extra` 中包含 `message_thread_id`（或 `thread_id`）来指定特定的论坛主题：

```yaml
webhooks:
  routes:
    alerts:
      events: ["alert"]
      prompt: "告警：{__raw__}"
      deliver: "telegram"
      deliver_extra:
        chat_id: "-1001234567890"
        message_thread_id: "42"
```

如果 `deliver_extra` 中没有提供 `chat_id`，投递会回退到目标平台配置的主频道。

---

## GitHub PR 审查（分步指南） {#github-pr-review}

本教程将设置每次拉取请求的自动代码审查。

### 1. 在 GitHub 中创建 webhook {#1-create-the-webhook-in-github}

1. 进入你的仓库 → **设置** → **Webhooks** → **添加 webhook**
2. 将 **Payload URL** 设置为 `http://your-server:8644/webhooks/github-pr`
3. 将 **Content type** 设置为 `application/json`
4. 将 **Secret** 设置为与你的路由配置匹配（例如 `github-webhook-secret`）
5. 在 **Which events?** 下，选择 **Let me select individual events** 并勾选 **Pull requests**
6. 点击 **Add webhook**

### 2. 添加路由配置 {#2-add-the-route-config}

按照上面的示例，将 `github-pr` 路由添加到你的 `~/.hermes/config.yaml` 中。
### 3. 确保 `gh` CLI 已通过身份验证 {#3-ensure-gh-cli-is-authenticated}

`github_comment` 投递类型使用 GitHub CLI 来发布评论：

```bash
gh auth login
```

### 4. 测试 {#4-test-it}

在仓库上打开一个拉取请求。Webhook 触发，Hermes 处理事件，并在 PR 上发布一条审查评论。

---

## GitLab Webhook 设置 {#gitlab-webhook-setup}

GitLab webhook 的工作方式类似，但使用不同的身份验证机制。GitLab 将密钥作为纯文本的 `X-Gitlab-Token` 标头发送（精确字符串匹配，而非 HMAC）。

### 1. 在 GitLab 中创建 webhook {#1-create-the-webhook-in-gitlab}

1. 进入你的项目 → **设置** → **Webhooks**
2. 将 **URL** 设置为 `http://your-server:8644/webhooks/gitlab-mr`
3. 输入你的 **Secret token**
4. 选择 **合并请求事件**（以及你需要的其他事件）
5. 点击 **添加 webhook**

### 2. 添加路由配置 {#2-add-the-route-config}

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

## 投递选项 {#delivery-options}

`deliver` 字段控制处理 webhook 事件后 Agent 的响应发送到哪里。

| 投递类型 | 描述 |
|-------------|-------------|
| `log` | 将响应记录到网关日志输出。这是默认选项，适用于测试。 |
| `github_comment` | 通过 `gh` CLI 将响应发布为 PR/issue 评论。需要在 `deliver_extra` 中指定 `repo` 和 `pr_number`。`gh` CLI 必须在网关主机上安装并通过身份验证（`gh auth login`）。 |
| `telegram` | 将响应路由到 Telegram。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `discord` | 将响应路由到 Discord。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `slack` | 将响应路由到 Slack。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `signal` | 将响应路由到 Signal。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `sms` | 通过 Twilio 将响应路由到短信。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `whatsapp` | 将响应路由到 WhatsApp。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `matrix` | 将响应路由到 Matrix。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `mattermost` | 将响应路由到 Mattermost。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `homeassistant` | 将响应路由到 Home Assistant。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `email` | 将响应路由到电子邮件。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `dingtalk` | 将响应路由到钉钉。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `feishu` | 将响应路由到飞书/Lark。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `wecom` | 将响应路由到企业微信。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `weixin` | 将响应路由到微信。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `bluebubbles` | 将响应路由到 BlueBubbles（iMessage）。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
对于跨平台投递，目标平台也必须在网关中启用并连接。如果在 `deliver_extra` 中未提供 `chat_id`，则响应会发送到该平台配置的默认频道。

---

## 直接投递模式 {#direct-delivery-mode}

默认情况下，每个 webhook POST 都会触发一次 Agent 运行——负载成为提示词，Agent 处理它，然后 Agent 的响应被投递。这会在每次事件中消耗 LLM token。

对于你只想**推送一条纯通知**的场景——无需推理、无需 Agent 循环，只需投递消息——可以在路由上设置 `deliver_only: true`。渲染后的 `prompt` 模板成为字面消息体，适配器直接将其分派到配置的投递目标。

### 何时使用直接投递 {#when-to-use-direct-delivery}

- **外部服务推送**——Supabase/Firebase webhook 在数据库变更时触发 → 立即通知 Telegram 用户
- **监控告警**——Datadog/Grafana 告警 webhook → 推送到 Discord 频道
- **Agent 间 ping**——Agent A 通知 Agent B 的用户某个长时间运行的任务已完成
- **后台任务完成**——Cron 任务完成 → 将结果发布到 Slack

优势：

- **零 LLM token**——从不调用 Agent
- **亚秒级投递**——单次适配器调用，无推理循环
- **与 Agent 模式相同的安全性**——HMAC 认证、速率限制、幂等性和消息体大小限制仍然适用
- **同步响应**——投递成功后 POST 返回 `200 OK`，如果目标拒绝则返回 `502`，这样上游服务可以智能重试

### 示例：从 Supabase 推送到 Telegram {#example-telegram-push-from-supabase}

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
          prompt: "🎉 New match: {match.user_name} matched with you!"
          deliver_extra:
            chat_id: "{match.telegram_chat_id}"
```

你的 Supabase Edge Function 使用 HMAC-SHA256 对负载签名，并 POST 到 `https://your-server:8644/webhooks/antenna-matches`。Webhook 适配器验证签名，从负载渲染模板，投递到 Telegram，然后返回 `200 OK`。

### 示例：通过 CLI 动态订阅 {#example-dynamic-subscription-via-cli}

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 New match: {match.user_name} matched with you!" \
  --description "Antenna match notifications"
```

### 响应码 {#response-codes}

| 状态码 | 含义 |
|--------|------|
| `200 OK` | 投递成功。响应体：`{"status": "delivered", "route": "...", "target": "...", "delivery_id": "..."}` |
| `200 OK` (status=duplicate) | 在幂等 TTL（1 小时）内出现重复的 `X-GitHub-Delivery` ID。不会重新投递。 |
| `401 Unauthorized` | HMAC 签名无效或缺失。 |
| `400 Bad Request` | JSON 消息体格式错误。 |
| `404 Not Found` | 未知的路由名称。 |
| `413 Payload Too Large` | 消息体超过 `max_body_bytes`。 |
| `429 Too Many Requests` | 路由速率限制已超。 |
| `502 Bad Gateway` | 目标适配器拒绝消息或抛出异常。错误记录在服务端；响应体为通用 `Delivery failed`，以避免泄露适配器内部信息。 |
### 配置陷阱 {#configuration-gotchas}

- `deliver_only: true` 要求 `deliver` 必须是真实目标。`deliver: log`（或省略 `deliver`）会在启动时被拒绝——如果发现路由配置错误，适配器会拒绝启动。
- `skills` 字段在直接投递模式下会被忽略（没有 Agent 运行，因此无从注入技能）。
- 模板渲染使用与 Agent 模式相同的 `{dot.notation}` 语法，包括 `{__raw__}` 令牌。
- 幂等性使用相同的 `X-GitHub-Delivery` / `X-Request-ID` 头——使用相同 ID 重试会返回 `status=duplicate` 且**不会**重新投递。

---

## 动态订阅 (CLI) {#dynamic-subscriptions}

除了 `config.yaml` 中的静态路由，你还可以使用 `hermes webhook` CLI 命令动态创建 webhook 订阅。当 Agent 本身需要设置事件驱动的触发器时，这尤其有用。

### 创建订阅 {#create-a-subscription}

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New issue #{issue.number}: {issue.title}\nBy: {issue.user.login}\n\n{issue.body}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789" \
  --description "Triage new GitHub issues"
```

这将返回 webhook URL 和一个自动生成的 HMAC 密钥。请配置你的服务以向该 URL 发送 POST 请求。

### 列出订阅 {#list-subscriptions}

```bash
hermes webhook list
```

### 删除订阅 {#remove-a-subscription}

```bash
hermes webhook remove github-issues
```

### 测试订阅 {#test-a-subscription}

```bash
hermes webhook test github-issues
hermes webhook test github-issues --payload '{"issue": {"number": 42, "title": "Test"}}'
```

### 动态订阅的工作原理 {#how-dynamic-subscriptions-work}

- 订阅存储在 `~/.hermes/webhook_subscriptions.json` 文件中
- webhook 适配器会在每次收到请求时热重载该文件（基于修改时间控制，开销可忽略）
- `config.yaml` 中的静态路由始终优先于同名的动态路由
- 动态订阅使用与静态路由相同的路由格式和能力（事件、提示模板、技能、投递）
- 无需重启网关——订阅后立即生效

### Agent 驱动的订阅 {#agent-driven-subscriptions}

Agent 可以在 `webhook-subscriptions` 技能的指引下，通过终端工具创建订阅。让 Agent“为 GitHub issues 设置一个 webhook”，它就会执行相应的 `hermes webhook subscribe` 命令。

---

## 安全措施 {#security}

webhook 适配器包含多层安全措施：

### HMAC 签名验证 {#hmac-signature-validation}

适配器会根据每种来源使用相应的方法验证传入的 webhook 签名：

- **GitHub**：`X-Hub-Signature-256` 头 —— 以 `sha256=` 为前缀的 HMAC-SHA256 十六进制摘要
- **GitLab**：`X-Gitlab-Token` 头 —— 纯文本密钥字符串匹配
- **通用**：`X-Webhook-Signature` 头 —— 原始 HMAC-SHA256 十六进制摘要

如果配置了密钥但未识别到签名头，该请求会被拒绝。

### 密钥是必需的 {#secret-is-required}

每条路由都必须有密钥——要么直接在路由上设置，要么继承自全局 `secret`。没有密钥的路由会导致适配器在启动时失败并报错。仅限开发/测试时，你可以将密钥设为 `"INSECURE_NO_AUTH"` 以完全跳过验证。
### 速率限制 {#rate-limiting}

每个路由默认按固定窗口限制为**每分钟 30 次请求**。可通过以下配置全局修改：

```yaml
platforms:
  webhook:
    extra:
      rate_limit: 60  # 每分钟请求数
```

超出限制的请求会收到 `429 Too Many Requests` 响应。

### 幂等性 {#idempotency}

投递 ID（来自 `X-GitHub-Delivery`、`X-Request-ID` 或时间戳回退）会被缓存 **1 小时**。重复的投递（例如 webhook 重试）会被静默跳过并返回 `200` 响应，从而避免重复触发 Agent 运行。

### 请求体大小限制 {#body-size-limits}

超过 **1 MB** 的负载会在读取请求体之前被拒绝。可通过以下配置修改：

```yaml
platforms:
  webhook:
    extra:
      max_body_bytes: 2097152  # 2 MB
```

### 提示注入风险 {#prompt-injection-risk}

:::warning
Webhook 负载中包含攻击者可控制的数据——PR 标题、提交信息、Issue 描述等都可能包含恶意指令。当网关暴露在互联网上时，请将其运行在沙箱环境（Docker、VM）中。建议使用 Docker 或 SSH 终端后端进行隔离。
:::

---

## 故障排除 {#troubleshooting}

### Webhook 未到达 {#webhook-not-arriving}

- 确认端口已暴露且可从 webhook 源访问
- 检查防火墙规则——端口 `8644`（或你配置的端口）必须开放
- 确认 URL 路径匹配：`http://your-server:8644/webhooks/&lt;route-name&gt;`
- 使用 `/health` 端点确认服务器正在运行

### 签名验证失败 {#signature-validation-failing}

- 确保路由配置中的密钥与 webhook 源配置的密钥完全一致
- 对于 GitHub，密钥基于 HMAC——检查 `X-Hub-Signature-256`
- 对于 GitLab，密钥是明文令牌匹配——检查 `X-Gitlab-Token`
- 检查网关日志中是否有 `Invalid signature` 警告

### 事件被忽略 {#event-being-ignored}

- 确认事件类型在路由的 `events` 列表中
- GitHub 事件使用 `pull_request`、`push`、`issues` 等值（`X-GitHub-Event` 请求头的值）
- GitLab 事件使用 `merge_request`、`push` 等值（`X-GitLab-Event` 请求头的值）
- 如果 `events` 为空或未设置，则接受所有事件

### Agent 无响应 {#agent-not-responding}

- 在前台运行网关以查看日志：`hermes gateway run`
- 检查提示模板是否正确渲染
- 确认投递目标已配置并连接

### 重复响应 {#duplicate-responses}

- 幂等性缓存应能防止此问题——检查 webhook 源是否发送了投递 ID 请求头（`X-GitHub-Delivery` 或 `X-Request-ID`）
- 投递 ID 会被缓存 1 小时

### `gh` CLI 错误（GitHub 评论投递） {#gh-cli-errors-github-comment-delivery}

- 在网关主机上运行 `gh auth login`
- 确保已认证的 GitHub 用户对仓库有写入权限
- 确认 `gh` 已安装且在 PATH 中

---

## 环境变量 {#environment-variables}

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `WEBHOOK_ENABLED` | 启用 webhook 平台适配器 | `false` |
| `WEBHOOK_PORT` | 接收 webhook 的 HTTP 服务器端口 | `8644` |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥（当路由未指定自己的密钥时作为回退使用） | _(无)_ |
