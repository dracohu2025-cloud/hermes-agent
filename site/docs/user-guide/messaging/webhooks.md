---
sidebar_position: 13
title: "Webhooks"
description: "接收来自 GitHub、GitLab 及其他服务的事件，以触发 Hermes agent 运行"
---

# Webhooks

接收来自外部服务（GitHub、GitLab、JIRA、Stripe 等）的事件，并自动触发 Hermes agent 运行。Webhook 适配器会运行一个 HTTP 服务器，用于接收 POST 请求、验证 HMAC 签名、将负载（payload）转换为 agent 提示词（prompt），并将响应路由回源头或转发到其他已配置的平台。

Agent 会处理该事件，并通过在 PR 上发表评论、向 Telegram/Discord 发送消息或记录结果来做出响应。

---

## 快速开始

1. 通过 `hermes gateway setup` 或环境变量启用
2. 在 `config.yaml` 中定义路由，**或者**使用 `hermes webhook subscribe` 动态创建路由
3. 将你的服务指向 `http://your-server:8644/webhooks/<route-name>`

---

## 设置

有两种启用 Webhook 适配器的方法。

### 通过设置向导

```bash
hermes gateway setup
```

按照提示启用 Webhook、设置端口并设置全局 HMAC 密钥。

### 通过环境变量

添加到 `~/.hermes/.env`：

```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644        # 默认值
WEBHOOK_SECRET=your-global-secret
```

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

路由定义了如何处理不同的 Webhook 源。每个路由都是 `config.yaml` 中 `platforms.webhook.extra.routes` 下的一个命名条目。

### 路由属性

| 属性 | 必填 | 描述 |
|----------|----------|-------------|
| `events` | 否 | 接受的事件类型列表（例如 `["pull_request"]`）。如果为空，则接受所有事件。事件类型从 `X-GitHub-Event`、`X-GitLab-Event` 或负载中的 `event_type` 读取。 |
| `secret` | **是** | 用于签名验证的 HMAC 密钥。如果路由上未设置，则回退到全局 `secret`。仅在测试时设置为 `"INSECURE_NO_AUTH"`（将跳过验证）。 |
| `prompt` | 否 | 带有点号表示法（dot-notation）负载访问权限的模板字符串（例如 `{pull_request.title}`）。如果省略，完整的 JSON 负载将被转储到提示词中。 |
| `skills` | 否 | 为 agent 运行加载的技能名称列表。 |
| `deliver` | 否 | 响应的发送目的地：`github_comment`、`telegram`、`discord`、`slack`、`signal`、`sms`、`whatsapp`、`matrix`、`mattermost`、`homeassistant`、`email`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles` 或 `log`（默认）。 |
| `deliver_extra` | 否 | 额外的发送配置 —— 键取决于 `deliver` 类型（例如 `repo`、`pr_number`、`chat_id`）。值支持与 `prompt` 相同的 `{dot.notation}` 模板。 |

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

提示词使用点号表示法来访问 Webhook 负载中的嵌套字段：

- `{pull_request.title}` 解析为 `payload["pull_request"]["title"]`
- `{repository.full_name}` 解析为 `payload["repository"]["full_name"]`
- `{__raw__}` — 特殊标记，将**整个负载**以缩进 JSON 格式转储（截断为 4000 个字符）。对于监控警报或 agent 需要完整上下文的通用 Webhook 非常有用。
- 缺失的键将保留为字面量 `{key}` 字符串（不会报错）
- 嵌套的字典和列表会被 JSON 序列化并截断为 2000 个字符

你可以将 `{__raw__}` 与常规模板变量混合使用：

```yaml
prompt: "PR #{pull_request.number} by {pull_request.user.login}: {__raw__}"
```

如果路由未配置 `prompt` 模板，则整个负载将以缩进 JSON 格式转储（截断为 4000 个字符）。

相同的点号表示法模板也适用于 `deliver_extra` 的值。

### 论坛主题发送

当向 Telegram 发送 Webhook 响应时，你可以通过在 `deliver_extra` 中包含 `message_thread_id`（或 `thread_id`）来指定特定的论坛主题：

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

如果 `deliver_extra` 中未提供 `chat_id`，则发送将回退到为目标平台配置的主频道。

---

## GitHub PR 代码审查（分步指南） {#github-pr-review}

本指南将设置针对每个 Pull Request 的自动代码审查。

### 1. 在 GitHub 中创建 Webhook

1. 进入你的仓库 → **Settings** → **Webhooks** → **Add webhook**
2. 将 **Payload URL** 设置为 `http://your-server:8644/webhooks/github-pr`
3. 将 **Content type** 设置为 `application/json`
4. 将 **Secret** 设置为与你的路由配置匹配（例如 `github-webhook-secret`）
5. 在 **Which events?** 下，选择 **Let me select individual events** 并勾选 **Pull requests**
6. 点击 **Add webhook**

### 2. 添加路由配置

按照上面的示例，将 `github-pr` 路由添加到你的 `~/.hermes/config.yaml` 中。

### 3. 确保 `gh` CLI 已认证

`github_comment` 发送类型使用 GitHub CLI 来发表评论：

```bash
gh auth login
```

### 4. 测试

在仓库中打开一个 Pull Request。Webhook 将被触发，Hermes 处理该事件，并在 PR 上发表审查评论。

---

## GitLab Webhook 设置 {#gitlab-webhook-setup}

GitLab Webhook 的工作方式类似，但使用不同的认证机制。GitLab 将密钥作为纯文本 `X-Gitlab-Token` 请求头发送（精确字符串匹配，而非 HMAC）。

### 1. 在 GitLab 中创建 Webhook

1. 进入你的项目 → **Settings** → **Webhooks**
2. 将 **URL** 设置为 `http://your-server:8644/webhooks/gitlab-mr`
3. 输入你的 **Secret token**
4. 选择 **Merge request events**（以及你需要的其他事件）
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

## 发送选项 {#delivery-options}

`deliver` 字段控制 agent 在处理完 Webhook 事件后，响应发送到哪里。

| 发送类型 | 描述 |
|-------------|-------------|
| `log` | 将响应记录到网关日志输出中。这是默认设置，适用于测试。 |
| `github_comment` | 通过 `gh` CLI 将响应作为 PR/Issue 评论发布。需要 `deliver_extra.repo` 和 `deliver_extra.pr_number`。必须在网关主机上安装并认证 `gh` CLI (`gh auth login`)。 |
| `telegram` | 将响应路由到 Telegram。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `discord` | 将响应路由到 Discord。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `slack` | 将响应路由到 Slack。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `signal` | 将响应路由到 Signal。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `sms` | 通过 Twilio 将响应路由到 SMS。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `whatsapp` | 将响应路由到 WhatsApp。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `matrix` | 将响应路由到 Matrix。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `mattermost` | 将响应路由到 Mattermost。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `homeassistant` | 将响应路由到 Home Assistant。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `email` | 将响应路由到电子邮件。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `dingtalk` | 将响应路由到钉钉。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `feishu` | 将响应路由到飞书/Lark。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `wecom` | 将响应路由到企业微信。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `weixin` | 将响应路由到微信。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `bluebubbles` | 将响应路由到 BlueBubbles (iMessage)。使用主频道，或在 `deliver_extra` 中指定 `chat_id`。 |
若要进行跨平台投递，目标平台也必须在网关中启用并连接。如果 `deliver_extra` 中未提供 `chat_id`，响应将发送到该平台配置的主频道。

---

## 动态订阅 (CLI) {#dynamic-subscriptions}

除了 `config.yaml` 中的静态路由外，你还可以使用 `hermes webhook` CLI 命令动态创建 webhook 订阅。当 Agent 本身需要设置事件驱动的触发器时，这尤其有用。

### 创建订阅

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New issue #{issue.number}: {issue.title}\nBy: {issue.user.login}\n\n{issue.body}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789" \
  --description "Triage new GitHub issues"
```

此命令会返回 webhook URL 和自动生成的 HMAC 密钥。请将你的服务配置为向该 URL 发送 POST 请求。

### 列出订阅

```bash
hermes webhook list
```

### 删除订阅

```bash
hermes webhook remove github-issues
```

### 测试订阅

```bash
hermes webhook test github-issues
hermes webhook test github-issues --payload '{"issue": {"number": 42, "title": "Test"}}'
```

### 动态订阅的工作原理

- 订阅存储在 `~/.hermes/webhook_subscriptions.json` 中
- Webhook 适配器会在每次收到请求时热重载此文件（基于 mtime 检查，开销可忽略不计）
- `config.yaml` 中的静态路由优先级始终高于同名的动态路由
- 动态订阅使用与静态路由相同的路由格式和功能（事件、提示词模板、技能、投递）
- 无需重启网关 — 订阅后立即生效

### Agent 驱动的订阅

当受到 `webhook-subscriptions` 技能引导时，Agent 可以通过终端工具创建订阅。让 Agent “为 GitHub issues 设置一个 webhook”，它就会运行相应的 `hermes webhook subscribe` 命令。

---

## 安全性 {#security}

Webhook 适配器包含多层安全防护：

### HMAC 签名验证

适配器会针对每个来源使用相应的方法验证传入的 webhook 签名：

- **GitHub**: `X-Hub-Signature-256` 请求头 — HMAC-SHA256 十六进制摘要，前缀为 `sha256=`
- **GitLab**: `X-Gitlab-Token` 请求头 — 纯文本密钥匹配
- **通用**: `X-Webhook-Signature` 请求头 — 原始 HMAC-SHA256 十六进制摘要

如果配置了密钥但未提供可识别的签名请求头，请求将被拒绝。

### 必须配置密钥

每条路由都必须拥有一个密钥 — 可以直接在路由上设置，也可以从全局 `secret` 继承。没有密钥的路由会导致适配器在启动时报错并失败。仅供开发/测试使用时，你可以将密钥设置为 `"INSECURE_NO_AUTH"` 以完全跳过验证。

### 速率限制

默认情况下，每条路由的速率限制为 **每分钟 30 个请求**（固定窗口）。你可以在全局进行配置：

```yaml
platforms:
  webhook:
    extra:
      rate_limit: 60  # 每分钟请求数
```

超过限制的请求将收到 `429 Too Many Requests` 响应。

### 幂等性

投递 ID（来自 `X-GitHub-Delivery`、`X-Request-ID` 或时间戳回退）会缓存 **1 小时**。重复的投递（例如 webhook 重试）会被静默跳过并返回 `200` 响应，从而防止 Agent 重复运行。

### 请求体大小限制

超过 **1 MB** 的负载会在读取请求体之前被拒绝。你可以这样配置：

```yaml
platforms:
  webhook:
    extra:
      max_body_bytes: 2097152  # 2 MB
```

### 提示词注入风险

:::warning
Webhook 负载包含攻击者可控的数据 — PR 标题、提交信息、Issue 描述等都可能包含恶意指令。当暴露在互联网上时，请在沙盒环境（Docker、虚拟机）中运行网关。建议使用 Docker 或 SSH 终端后端进行隔离。
:::

---

## 故障排查 {#troubleshooting}

### Webhook 未送达

- 确认端口已暴露并可从 webhook 源访问
- 检查防火墙规则 — 必须开放端口 `8644`（或你配置的端口）
- 验证 URL 路径是否匹配：`http://your-server:8644/webhooks/<route-name>`
- 使用 `/health` 端点确认服务器正在运行

### 签名验证失败

- 确保路由配置中的密钥与 webhook 源中配置的密钥完全一致
- 对于 GitHub，密钥基于 HMAC — 请检查 `X-Hub-Signature-256`
- 对于 GitLab，密钥是纯文本匹配 — 请检查 `X-GitLab-Token`
- 检查网关日志中是否有 `Invalid signature` 警告

### 事件被忽略

- 检查事件类型是否在路由的 `events` 列表中
- GitHub 事件使用如 `pull_request`、`push`、`issues` 等值（即 `X-GitHub-Event` 请求头的值）
- GitLab 事件使用如 `merge_request`、`push` 等值（即 `X-GitLab-Event` 请求头的值）
- 如果 `events` 为空或未设置，则接受所有事件

### Agent 无响应

- 在前台运行网关以查看日志：`hermes gateway run`
- 检查提示词模板是否渲染正确
- 验证投递目标是否已配置并连接

### 重复响应

- 幂等性缓存应该可以防止这种情况 — 检查 webhook 源是否发送了投递 ID 请求头（`X-GitHub-Delivery` 或 `X-Request-ID`）
- 投递 ID 缓存时间为 1 小时

### `gh` CLI 错误（GitHub 评论投递）

- 在网关主机上运行 `gh auth login`
- 确保已认证的 GitHub 用户对仓库拥有写入权限
- 检查 `gh` 是否已安装并位于 PATH 环境变量中

---

## 环境变量 {#environment-variables}

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `WEBHOOK_ENABLED` | 启用 webhook 平台适配器 | `false` |
| `WEBHOOK_PORT` | 用于接收 webhook 的 HTTP 服务器端口 | `8644` |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥（当路由未指定密钥时作为回退使用） | _(无)_ |
