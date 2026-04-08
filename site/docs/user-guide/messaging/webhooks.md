---
sidebar_position: 13
title: "Webhooks"
description: "接收来自 GitHub、GitLab 和其他服务的事件，以触发 Hermes Agent 运行"
---

# Webhooks

接收来自外部服务（GitHub、GitLab、JIRA、Stripe 等）的事件并自动触发 Hermes Agent 运行。Webhook 适配器运行一个 HTTP 服务器，负责接收 POST 请求、验证 HMAC 签名、将 Payload 转换为 Agent 提示词（Prompt），并将响应路由回源端或其他配置好的平台。

Agent 处理事件后，可以通过在 PR 上发表评论、向 Telegram/Discord 发送消息或记录日志来进行响应。

---

## 快速开始

1. 通过 `hermes gateway setup` 或环境变量启用
2. 在 `config.yaml` 中定义路由，**或者**使用 `hermes webhook subscribe` 动态创建路由
3. 将您的服务指向 `http://your-server:8644/webhooks/<route-name>`

---

## 安装设置

有两种方式可以启用 Webhook 适配器。

### 通过设置向导

```bash
hermes gateway setup
```

按照提示启用 Webhook，设置端口，并设置全局 HMAC 密钥（Secret）。

### 通过环境变量

添加到 `~/.hermes/.env`：

```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644        # 默认值
WEBHOOK_SECRET=your-global-secret
```

### 验证服务器

Gateway 运行后：

```bash
curl http://localhost:8644/health
```

预期响应：

```json
{"status": "ok", "platform": "webhook"}
```

---

## 配置路由 {#configuring-routes}

路由定义了如何处理不同的 Webhook 源。每个路由都是 `config.yaml` 中 `platforms.webhook.extra.routes` 下的一个命名条目。

### 路由属性

| 属性 | 必填 | 描述 |
|----------|----------|-------------|
| `events` | 否 | 允许接收的事件类型列表（例如 `["pull_request"]`）。如果为空，则接收所有事件。事件类型从 Payload 中的 `X-GitHub-Event`、`X-GitLab-Event` 或 `event_type` 读取。 |
| `secret` | **是** | 用于签名验证的 HMAC 密钥。如果路由未设置，则回退到全局 `secret`。仅用于测试时可设置为 `"INSECURE_NO_AUTH"`（跳过验证）。 |
| `prompt` | 否 | 使用点分隔符访问 Payload 的模板字符串（例如 `{pull_request.title}`）。如果省略，完整的 JSON Payload 将被直接放入提示词中。 |
| `skills` | 否 | 为该 Agent 运行加载的技能名称列表。 |
| `deliver` | 否 | 响应发送目的地：`github_comment`、`telegram`、`discord`、`slack`、`signal`、`matrix`、`mattermost`、`email`、`sms`、`dingtalk`、`feishu`、`wecom` 或 `log`（默认）。 |
| `deliver_extra` | 否 | 额外的投递配置 —— 键名取决于 `deliver` 类型（例如 `repo`、`pr_number`、`chat_id`）。值支持与 `prompt` 相同的 `{dot.notation}` 模板。 |

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

### 提示词模板

提示词使用点分隔符（dot-notation）来访问 Webhook Payload 中的嵌套字段：

- `{pull_request.title}` 解析为 `payload["pull_request"]["title"]`
- `{repository.full_name}` 解析为 `payload["repository"]["full_name"]`
- `{__raw__}` —— 特殊标记，将**整个 Payload** 导出为带缩进的 JSON（截断至 4000 字符）。适用于监控告警或 Agent 需要完整上下文的通用 Webhook。
- 缺失的键将保留为原始的 `{key}` 字符串（不会报错）
- 嵌套的字典和列表将被 JSON 序列化并截断至 2000 字符

您可以将 `{__raw__}` 与常规模板变量混合使用：

```yaml
prompt: "PR #{pull_request.number} by {pull_request.user.login}: {__raw__}"
```

如果路由未配置 `prompt` 模板，整个 Payload 将作为带缩进的 JSON 导出（截断至 4000 字符）。

同样的点分隔符模板也适用于 `deliver_extra` 的值。

### 论坛话题投递

当向 Telegram 投递 Webhook 响应时，您可以通过在 `deliver_extra` 中包含 `message_thread_id`（或 `thread_id`）来指定特定的论坛话题（Topic）：

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

如果 `deliver_extra` 中未提供 `chat_id`，投递将回退到目标平台配置的主频道。

---

## GitHub PR 评审（分步指南） {#github-pr-review}

本教程将设置在每个 Pull Request 上自动进行代码评审。

### 1. 在 GitHub 中创建 Webhook

1. 进入您的仓库 → **Settings** → **Webhooks** → **Add webhook**
2. 将 **Payload URL** 设置为 `http://your-server:8644/webhooks/github-pr`
3. 将 **Content type** 设置为 `application/json`
4. 设置 **Secret** 以匹配您的路由配置（例如 `github-webhook-secret`）
5. 在 **Which events?** 下，选择 **Let me select individual events** 并勾选 **Pull requests**
6. 点击 **Add webhook**

### 2. 添加路由配置

按照上面的示例，将 `github-pr` 路由添加到您的 `~/.hermes/config.yaml` 中。

### 3. 确保 `gh` CLI 已认证

`github_comment` 投递类型使用 GitHub CLI 来发布评论：

```bash
gh auth login
```

### 4. 测试

在仓库中开启一个 Pull Request。Webhook 会触发，Hermes 处理该事件，并在 PR 上发布评审评论。

---

## GitLab Webhook 设置 {#gitlab-webhook-setup}

GitLab Webhook 的工作方式类似，但使用不同的认证机制。GitLab 将密钥作为纯文本的 `X-Gitlab-Token` 请求头发送（精确字符串匹配，而非 HMAC）。

### 1. 在 GitLab 中创建 Webhook

1. 进入您的项目 → **Settings** → **Webhooks**
2. 将 **URL** 设置为 `http://your-server:8644/webhooks/gitlab-mr`
3. 输入您的 **Secret token**
4. 选择 **Merge request events**（以及任何您想要的其他事件）
5. 点击 **Add webhook**

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

## 投递选项 {#delivery-options}

`deliver` 字段控制 Agent 在处理完 Webhook 事件后将响应发送到何处。

| 投递类型 | 描述 |
|-------------|-------------|
| `log` | 将响应记录到 Gateway 日志输出中。这是默认值，对测试很有用。 |
| `github_comment` | 通过 `gh` CLI 将响应发布为 PR/Issue 评论。需要 `deliver_extra.repo` 和 `deliver_extra.pr_number`。必须在 Gateway 主机上安装并认证 `gh` CLI (`gh auth login`)。 |
| `telegram` | 将响应路由到 Telegram。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `discord` | 将响应路由到 Discord。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `slack` | 将响应路由到 Slack。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `signal` | 将响应路由到 Signal。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `sms` | 通过 Twilio 将响应路由到短信。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
对于跨平台推送（telegram、discord、slack、signal、sms），目标平台必须已在 gateway 中启用并连接。如果在 `deliver_extra` 中没有提供 `chat_id`，响应将发送到该平台配置的主频道（home channel）。

---

## 动态订阅 (CLI) {#dynamic-subscriptions}

除了在 `config.yaml` 中配置静态路由外，你还可以使用 `hermes webhook` CLI 命令动态创建 webhook 订阅。当 Agent 自身需要设置事件驱动的触发器时，这非常有用。

### 创建订阅

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New issue #{issue.number}: {issue.title}\nBy: {issue.user.login}\n\n{issue.body}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789" \
  --description "Triage new GitHub issues"
```

执行后会返回 webhook URL 和一个自动生成的 HMAC 密钥。请将你的服务配置为向该 URL 发送 POST 请求。

### 列出订阅

```bash
hermes webhook list
```

### 移除订阅

```bash
hermes webhook remove github-issues
```

### 测试订阅

```bash
hermes webhook test github-issues
hermes webhook test github-issues --payload '{"issue": {"number": 42, "title": "Test"}}'
```

### 动态订阅的工作原理

- 订阅信息存储在 `~/.hermes/webhook_subscriptions.json` 中。
- Webhook 适配器在每次收到请求时都会热加载此文件（基于修改时间 mtime 判定，开销极小）。
- `config.yaml` 中的静态路由优先级始终高于同名的动态路由。
- 动态订阅使用与静态路由相同的路由格式和功能（事件、Prompt 模板、技能、推送）。
- 无需重启 gateway —— 订阅后立即生效。

### Agent 驱动的订阅

在 `webhook-subscriptions` 技能的引导下，Agent 可以通过终端工具创建订阅。你可以要求 Agent “为 GitHub issues 设置一个 webhook”，它将运行相应的 `hermes webhook subscribe` 命令。

---

## 安全性 {#security}

Webhook 适配器包含多层安全防护：

### HMAC 签名验证

适配器会根据每个来源的相应方法验证传入的 webhook 签名：

- **GitHub**: `X-Hub-Signature-256` 请求头 —— 以 `sha256=` 为前缀的 HMAC-SHA256 十六进制摘要。
- **GitLab**: `X-Gitlab-Token` 请求头 —— 纯文本密钥匹配。
- **通用**: `X-Webhook-Signature` 请求头 —— 原始 HMAC-SHA256 十六进制摘要。

如果配置了密钥但没有识别到签名请求头，请求将被拒绝。

### 必须配置密钥

每个路由都必须有一个密钥 —— 可以直接在路由上设置，也可以继承自全局 `secret`。没有密钥的路由会导致适配器在启动时报错失败。仅在开发/测试时，你可以将密钥设置为 `"INSECURE_NO_AUTH"` 以完全跳过验证。

### 速率限制

默认情况下，每个路由的速率限制为 **每分钟 30 次请求**（固定窗口）。可以进行全局配置：

```yaml
platforms:
  webhook:
    extra:
      rate_limit: 60  # 每分钟请求数
```

超过限制的请求将收到 `429 Too Many Requests` 响应。

### 幂等性

推送 ID（来自 `X-GitHub-Delivery`、`X-Request-ID` 或时间戳备选项）会被缓存 **1 小时**。重复的推送（例如 webhook 重试）将被静默跳过并返回 `200` 响应，从而防止 Agent 重复运行。

### Body 大小限制

超过 **1 MB** 的 Payload 会在读取正文前被拒绝。可以这样配置：

```yaml
platforms:
  webhook:
    extra:
      max_body_bytes: 2097152  # 2 MB
```

### Prompt 注入风险

:::warning
Webhook Payload 包含攻击者可控的数据 —— PR 标题、提交信息、issue 描述等都可能包含恶意指令。当暴露在互联网上时，请在沙箱环境（Docker、VM）中运行 gateway。考虑使用 Docker 或 SSH 终端后端进行隔离。
:::

---

## 故障排除 {#troubleshooting}

### Webhook 未送达

- 确认端口已暴露且可从 webhook 源访问。
- 检查防火墙规则 —— 端口 `8644`（或你配置的端口）必须开放。
- 确认 URL 路径匹配：`http://your-server:8644/webhooks/<route-name>`。
- 使用 `/health` 端点确认服务器正在运行。

### 签名验证失败

- 确保路由配置中的密钥与 webhook 源中配置的密钥完全一致。
- 对于 GitHub，密钥是基于 HMAC 的 —— 检查 `X-Hub-Signature-256`。
- 对于 GitLab，密钥是纯令牌匹配 —— 检查 `X-Gitlab-Token`。
- 检查 gateway 日志中的 `Invalid signature` 警告。

### 事件被忽略

- 检查事件类型是否在路由的 `events` 列表中。
- GitHub 事件使用类似 `pull_request`、`push`、`issues` 的值（即 `X-GitHub-Event` 请求头的值）。
- GitLab 事件使用类似 `merge_request`、`push` 的值（即 `X-GitLab-Event` 请求头的值）。
- 如果 `events` 为空或未设置，则接受所有事件。

### Agent 没有响应

- 在前台运行 gateway 以查看日志：`hermes gateway run`。
- 检查 Prompt 模板是否正确渲染。
- 验证推送目标已配置并连接。

### 重复响应

- 幂等性缓存应该能防止这种情况 —— 检查 webhook 源是否发送了推送 ID 请求头（`X-GitHub-Delivery` 或 `X-Request-ID`）。
- 推送 ID 会被缓存 1 小时。

### `gh` CLI 错误（GitHub 评论推送）

- 在 gateway 宿主机上运行 `gh auth login`。
- 确保经过身份验证的 GitHub 用户对该仓库具有写权限。
- 检查 `gh` 是否已安装并包含在 PATH 中。

---

## 环境变量 {#environment-variables}

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `WEBHOOK_ENABLED` | 启用 webhook 平台适配器 | `false` |
| `WEBHOOK_PORT` | 接收 webhook 的 HTTP 服务器端口 | `8644` |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥（当路由未指定自己的密钥时作为备选） | _(无)_ |
