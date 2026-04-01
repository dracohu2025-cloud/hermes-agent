---
sidebar_position: 13
title: "Webhook 事件接入"
description: "接收来自 GitHub、GitLab 及其他服务的事件，自动触发 Hermes agent 运行"
---

# Webhooks

接收来自外部服务（GitHub、GitLab、JIRA、Stripe 等）的事件，自动触发 Hermes agent 运行。Webhook 适配器运行一个 HTTP 服务器，接受 POST 请求，验证 HMAC 签名，将负载转换为 agent 提示，并将响应路由回源头或其他配置的平台。

Agent 处理事件后，可以通过在 PR 上发表评论、发送消息到 Telegram/Discord，或记录结果来响应。

---

## 快速开始

1. 通过 `hermes gateway setup` 或环境变量启用
2. 在 `config.yaml` 中定义路由 **或** 使用 `hermes webhook subscribe` 动态创建路由
3. 将你的服务指向 `http://your-server:8644/webhooks/<route-name>`

---

## 设置

启用 webhook 适配器有两种方式。

### 通过设置向导

```bash
hermes gateway setup
```

按照提示启用 webhooks，设置端口和全局 HMAC 密钥。

### 通过环境变量

添加到 `~/.hermes/.env`：

```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644        # 默认端口
WEBHOOK_SECRET=your-global-secret
```

### 验证服务器

网关启动后：

```bash
curl http://localhost:8644/health
```

预期响应：

```json
{"status": "ok", "platform": "webhook"}
```

---

## 配置路由 {#configuring-routes}

路由定义了如何处理不同的 webhook 来源。每个路由是 `config.yaml` 中 `platforms.webhook.extra.routes` 下的一个命名条目。

### 路由属性

| 属性 | 是否必需 | 说明 |
|----------|----------|-------------|
| `events` | 否 | 接受的事件类型列表（例如 `["pull_request"]`）。为空时接受所有事件。事件类型从 `X-GitHub-Event`、`X-GitLab-Event` 或负载中的 `event_type` 读取。 |
| `secret` | **是** | 用于签名验证的 HMAC 密钥。如果路由未设置，则回退使用全局 `secret`。仅测试时可设置为 `"INSECURE_NO_AUTH"`（跳过验证）。 |
| `prompt` | 否 | 使用点符号访问负载字段的模板字符串（例如 `{pull_request.title}`）。省略时，整个 JSON 负载会被放入提示中。 |
| `skills` | 否 | 运行 agent 时加载的技能名称列表。 |
| `deliver` | 否 | 响应发送目标：`github_comment`、`telegram`、`discord`、`slack`、`signal`、`sms` 或 `log`（默认）。 |
| `deliver_extra` | 否 | 额外的发送配置——键根据 `deliver` 类型不同（例如 `repo`、`pr_number`、`chat_id`）。值支持与 `prompt` 相同的 `{dot.notation}` 模板。 |

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

### 提示模板

提示使用点符号访问 webhook 负载中的嵌套字段：

- `{pull_request.title}` 解析为 `payload["pull_request"]["title"]`
- `{repository.full_name}` 解析为 `payload["repository"]["full_name"]`
- 缺失的键会保留为字面量 `{key}` 字符串（不会报错）
- 嵌套的字典和列表会被 JSON 序列化，并截断到 2000 字符

如果路由未配置 `prompt` 模板，则整个负载会以缩进的 JSON 格式输出（截断到 4000 字符）。

相同的点符号模板也适用于 `deliver_extra` 的值。
---

## GitHub PR 审查（逐步指导）{#github-pr-review}

本教程演示如何在每个拉取请求上设置自动代码审查。

### 1. 在 GitHub 创建 webhook

1. 进入你的仓库 → **Settings** → **Webhooks** → **Add webhook**
2. 将 **Payload URL** 设置为 `http://your-server:8644/webhooks/github-pr`
3. 将 **Content type** 设置为 `application/json`
4. 将 **Secret** 设置为与你的路由配置匹配（例如 `github-webhook-secret`）
5. 在 **Which events?** 中选择 **Let me select individual events**，并勾选 **Pull requests**
6. 点击 **Add webhook**

### 2. 添加路由配置

将 `github-pr` 路由添加到你的 `~/.hermes/config.yaml`，参考上面的示例。

### 3. 确保 `gh` CLI 已认证

`github_comment` 交付类型使用 GitHub CLI 来发布评论：

```bash
gh auth login
```

### 4. 测试

在仓库中打开一个拉取请求。webhook 会触发，Hermes 处理事件，并在 PR 上发布审查评论。

---

## GitLab Webhook 设置 {#gitlab-webhook-setup}

GitLab webhook 工作方式类似，但使用不同的认证机制。GitLab 通过普通的 `X-Gitlab-Token` 头部发送 secret（精确字符串匹配，不是 HMAC）。

### 1. 在 GitLab 创建 webhook

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

## 交付选项 {#delivery-options}

`deliver` 字段控制 Agent 处理 webhook 事件后，响应发送到哪里。

| 交付类型 | 描述 |
|-------------|-------------|
| `log` | 将响应记录到网关日志输出。这是默认选项，适合测试使用。 |
| `github_comment` | 通过 `gh` CLI 以 PR/issue 评论形式发布响应。需要 `deliver_extra.repo` 和 `deliver_extra.pr_number`。`gh` CLI 必须安装并在网关主机上认证（`gh auth login`）。 |
| `telegram` | 将响应发送到 Telegram。使用默认频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `discord` | 将响应发送到 Discord。使用默认频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `slack` | 将响应发送到 Slack。使用默认频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `signal` | 将响应发送到 Signal。使用默认频道，或在 `deliver_extra` 中指定 `chat_id`。 |
| `sms` | 通过 Twilio 将响应发送为短信。使用默认频道，或在 `deliver_extra` 中指定 `chat_id`。 |

对于跨平台交付（telegram、discord、slack、signal、sms），目标平台必须在网关中启用并连接。如果 `deliver_extra` 中未提供 `chat_id`，响应将发送到该平台配置的默认频道。

---

## 动态订阅（CLI）{#dynamic-subscriptions}

除了在 `config.yaml` 中配置静态路由外，你还可以使用 `hermes webhook` CLI 命令动态创建 webhook 订阅。这在 Agent 本身需要设置事件驱动触发器时特别有用。

### 创建订阅

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New issue #{issue.number}: {issue.title}\nBy: {issue.user.login}\n\n{issue.body}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789" \
  --description "Triage new GitHub issues"
```

该命令会返回 webhook URL 和自动生成的 HMAC secret。将你的服务配置为向该 URL 发送 POST 请求。

---
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

- 订阅信息存储在 `~/.hermes/webhook_subscriptions.json`
- webhook 适配器会在每次收到请求时热加载该文件（基于修改时间，开销极小）
- 来自 `config.yaml` 的静态路由总是优先于同名的动态路由
- 动态订阅使用与静态路由相同的格式和功能（事件、提示模板、技能、投递）
- 无需重启网关——订阅后立即生效

### 由 Agent 驱动的订阅

当通过 `webhook-subscriptions` 技能引导时，Agent 可以通过终端工具创建订阅。你可以让 Agent “为 GitHub issues 设置一个 webhook”，它会自动执行相应的 `hermes webhook subscribe` 命令。

---

## 安全 {#security}

webhook 适配器包含多层安全机制：

### HMAC 签名验证

适配器会根据不同来源使用相应方式验证传入的 webhook 签名：

- **GitHub**：`X-Hub-Signature-256` 头 — HMAC-SHA256 十六进制摘要，前缀为 `sha256=`
- **GitLab**：`X-Gitlab-Token` 头 — 纯文本密钥匹配
- **通用**：`X-Webhook-Signature` 头 — 原始 HMAC-SHA256 十六进制摘要

如果配置了密钥但没有检测到认可的签名头，请求会被拒绝。

### 必须设置密钥

每条路由都必须有密钥——要么直接在路由上设置，要么继承全局的 `secret`。没有密钥的路由会导致适配器启动失败并报错。仅在开发/测试时，可以将密钥设置为 `"INSECURE_NO_AUTH"` 来跳过验证。

### 速率限制

每条路由默认限制为**每分钟 30 次请求**（固定时间窗口）。可全局配置：

```yaml
platforms:
  webhook:
    extra:
      rate_limit: 60  # 每分钟请求数
```

超过限制的请求会返回 `429 Too Many Requests`。

### 幂等性

投递 ID（来自 `X-GitHub-Delivery`、`X-Request-ID`，或时间戳备选）会缓存 **1 小时**。重复投递（如 webhook 重试）会被静默跳过，返回 `200`，避免重复触发 Agent。

### 请求体大小限制

超过 **1 MB** 的负载会在读取请求体前被拒绝。可配置：

```yaml
platforms:
  webhook:
    extra:
      max_body_bytes: 2097152  # 2 MB
```

### 提示注入风险

:::warning
Webhook 负载包含攻击者可控的数据——PR 标题、提交信息、问题描述等都可能包含恶意指令。暴露在互联网时，请在沙箱环境（Docker、虚拟机）中运行网关。建议使用 Docker 或 SSH 终端后端进行隔离。
:::

---

## 故障排查 {#troubleshooting}

### Webhook 没有到达

- 确认端口已开放且可从 webhook 源访问
- 检查防火墙规则——端口 `8644`（或你配置的端口）必须开放
- 确认 URL 路径正确：`http://your-server:8644/webhooks/<route-name>`
- 使用 `/health` 端点确认服务器正在运行

### 签名验证失败

- 确保路由配置中的密钥与 webhook 源配置的密钥完全一致
- GitHub 使用基于 HMAC 的密钥——检查 `X-Hub-Signature-256`
- GitLab 使用纯文本令牌匹配——检查 `X-Gitlab-Token`
- 查看网关日志中的 `Invalid signature` 警告

### 事件被忽略

- 确认事件类型包含在路由的 `events` 列表中
- GitHub 事件示例：`pull_request`、`push`、`issues`（对应 `X-GitHub-Event` 头）
- GitLab 事件示例：`merge_request`、`push`（对应 `X-GitLab-Event` 头）
- 如果 `events` 为空或未设置，则接受所有事件

---
### Agent 无响应

- 在前台运行 gateway 以查看日志：`hermes gateway run`
- 检查提示模板是否正确渲染
- 确认投递目标已配置且已连接

### 重复响应

- 幂等缓存应能防止此类情况——检查 webhook 源是否发送了投递 ID 头（`X-GitHub-Delivery` 或 `X-Request-ID`）
- 投递 ID 会缓存 1 小时

### `gh` CLI 错误（GitHub 评论投递）

- 在 gateway 主机上运行 `gh auth login`
- 确保认证的 GitHub 用户对仓库有写权限
- 检查是否已安装 `gh` 并且在 PATH 中

---

## 环境变量 {#environment-variables}

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `WEBHOOK_ENABLED` | 启用 webhook 平台适配器 | `false` |
| `WEBHOOK_PORT` | 用于接收 webhook 的 HTTP 服务器端口 | `8644` |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥（当路由未指定时作为备用） | _(无)_ |
