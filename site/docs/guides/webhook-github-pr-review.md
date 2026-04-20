---
sidebar_position: 11
sidebar_label: "通过 Webhook 进行 GitHub PR 评审"
title: "使用 Webhook 实现自动化 GitHub PR 评论"
description: "将 Hermes 连接到 GitHub，使其能自动获取 PR 差异、审查代码变更并发布评论——由 webhook 触发，无需手动操作"
---

<a id="automated-github-pr-comments-with-webhooks"></a>
# 使用 Webhook 实现自动化 GitHub PR 评论

本指南将引导你将 Hermes Agent 连接到 GitHub，使其能自动获取拉取请求的差异、分析代码变更并发布评论——由 webhook 事件触发，无需手动操作。

当 PR 被打开或更新时，GitHub 会向你的 Hermes 实例发送一个 webhook POST 请求。Hermes 会运行 Agent，并附带一个提示，指示其通过 `gh` CLI 获取差异，然后将响应发布回 PR 讨论串。

:::tip 想要更简单的设置，无需公共端点？
如果你没有公共 URL 或者只是想快速开始，请查看[构建 GitHub PR 评审 Agent](./github-pr-review-agent.md)——它使用定时任务按计划轮询 PR，可在 NAT 和防火墙后工作。
<a id="want-a-simpler-setup-without-a-public-endpoint"></a>
:::

:::info 参考文档
有关完整的 webhook 平台参考（所有配置选项、交付类型、动态订阅、安全模型），请参阅 [Webhooks](/user-guide/messaging/webhooks)。
<a id="reference-docs"></a>
:::

:::warning 提示注入风险
Webhook 负载包含攻击者控制的数据——PR 标题、提交信息和描述可能包含恶意指令。当你的 webhook 端点暴露在互联网上时，请在沙盒环境（Docker、SSH 后端）中运行网关。请参阅下面的[安全注意事项](#security-notes)。
<a id="prompt-injection-risk"></a>
:::

---

<a id="prerequisites"></a>
## 先决条件

- 已安装并运行 Hermes Agent (`hermes gateway`)
- 网关主机上已安装并认证 [`gh` CLI](https://cli.github.com/) (`gh auth login`)
- 你的 Hermes 实例有一个可公开访问的 URL（如果在本地运行，请参阅[使用 ngrok 进行本地测试](#local-testing-with-ngrok)）
- 对 GitHub 仓库拥有管理员访问权限（管理 webhook 所需）

---

<a id="step-1-enable-the-webhook-platform"></a>
## 步骤 1 — 启用 webhook 平台

将以下内容添加到你的 `~/.hermes/config.yaml` 中：

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644          # 默认值；如果其他服务占用此端口，请更改
      rate_limit: 30      # 每个路由每分钟的最大请求数（非全局限制）

      routes:
        github-pr-review:
          secret: "your-webhook-secret-here"   # 必须与 GitHub webhook 密钥完全匹配
          events:
            - pull_request

          # Agent 被指示在评审前获取实际的差异。
          # {number} 和 {repository.full_name} 从 GitHub 负载中解析。
          prompt: |
            A pull request event was received (action: {action}).

            PR #{number}: {pull_request.title}
            Author: {pull_request.user.login}
            Branch: {pull_request.head.ref} → {pull_request.base.ref}
            Description: {pull_request.body}
            URL: {pull_request.html_url}

            If the action is "closed" or "labeled", stop here and do not post a comment.

            Otherwise:
            1. Run: gh pr diff {number} --repo {repository.full_name}
            2. Review the code changes for correctness, security issues, and clarity.
            3. Write a concise, actionable review comment and post it.

          deliver: github_comment
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{number}"
```
**关键字段：**

| 字段 | 描述 |
|---|---|
| `secret` (路由级别) | 此路由的 HMAC 密钥。如果省略，则回退到全局的 `extra.secret`。 |
| `events` | 要接受的 `X-GitHub-Event` 头部值列表。空列表 = 接受所有事件。 |
| `prompt` | 模板；`{field}` 和 `{nested.field}` 从 GitHub 负载中解析。 |
| `deliver` | `github_comment` 通过 `gh pr comment` 发布评论。`log` 仅写入网关日志。 |
| `deliver_extra.repo` | 从负载中解析为例如 `org/repo`。 |
| `deliver_extra.pr_number` | 从负载中解析为 PR 编号。 |

:::note 负载不包含代码
GitHub webhook 负载包含 PR 元数据（标题、描述、分支名、URL），但**不包含差异**。上面的提示词指示 Agent 运行 `gh pr diff` 来获取实际的变更。`terminal` 工具已包含在默认的 `hermes-webhook` 工具集中，因此无需额外配置。
:::

<a id="the-payload-does-not-contain-code"></a>
---

<a id="step-2-start-the-gateway"></a>
## 步骤 2 — 启动网关

```bash
hermes gateway
```

你应该会看到：

```
[webhook] Listening on 0.0.0.0:8644 — routes: github-pr-review
```

验证它是否在运行：

```bash
curl http://localhost:8644/health
# {"status": "ok", "platform": "webhook"}
```

---

<a id="step-3-register-the-webhook-on-github"></a>
## 步骤 3 — 在 GitHub 上注册 webhook

1.  进入你的仓库 → **Settings** → **Webhooks** → **Add webhook**
2.  填写：
    -   **Payload URL:** `https://your-public-url.example.com/webhooks/github-pr-review`
    -   **Content type:** `application/json`
    -   **Secret:** 与你在路由配置中为 `secret` 设置的值相同
    -   **Which events?** → Select individual events → 勾选 **Pull requests**
3.  点击 **Add webhook**

GitHub 会立即发送一个 `ping` 事件来确认连接。该事件会被安全地忽略 — `ping` 不在你的 `events` 列表中 — 并返回 `{"status": "ignored", "event": "ping"}`。它仅在 DEBUG 级别记录，因此在默认日志级别下不会出现在控制台中。

---

<a id="step-4-open-a-test-pr"></a>
## 步骤 4 — 打开一个测试 PR

创建一个分支，推送一个更改，并打开一个 PR。在 30–90 秒内（取决于 PR 大小和模型），Hermes 应该会发布一条审查评论。

要实时跟踪 Agent 的进度：

```bash
tail -f "${HERMES_HOME:-$HOME/.hermes}/logs/gateway.log"
```

---

## 使用 ngrok 进行本地测试 {#local-testing-with-ngrok}

如果 Hermes 在你的笔记本电脑上运行，使用 [ngrok](https://ngrok.com/) 来暴露它：

```bash
ngrok http 8644
```

复制 `https://...ngrok-free.app` URL 并将其用作你的 GitHub Payload URL。在免费的 ngrok 套餐中，每次 ngrok 重启时 URL 都会改变 — 每次会话都需要更新你的 GitHub webhook。付费的 ngrok 账户可以获得静态域名。
你可以直接用 `curl` 对静态路由进行冒烟测试——不需要 GitHub 账号或真实的 PR。

:::tip 本地测试时使用 `deliver: log`
<a id="use-deliver-log-when-testing-locally"></a>
在测试时，请将配置中的 `deliver: github_comment` 改为 `deliver: log`。否则，Agent 会尝试向测试负载中的假 `org/repo#99` 仓库发布评论，这将导致失败。当你对提示词输出满意后，再切换回 `deliver: github_comment`。
:::

```bash
SECRET="your-webhook-secret-here"
BODY='{"action":"opened","number":99,"pull_request":{"title":"Test PR","body":"Adds a feature.","user":{"login":"testuser"},"head":{"ref":"feat/x"},"base":{"ref":"main"},"html_url":"https://github.com/org/repo/pull/99"},"repository":{"full_name":"org/repo"}}'
SIG=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -hex | awk '{print "sha256="$2}')

curl -s -X POST http://localhost:8644/webhooks/github-pr-review \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: $SIG" \
  -d "$BODY"
# Expected: {"status":"accepted","route":"github-pr-review","event":"pull_request","delivery_id":"..."}
```

然后观察 Agent 运行：
```bash
tail -f "${HERMES_HOME:-$HOME/.hermes}/logs/gateway.log"
```

:::note
`hermes webhook test &lt;name&gt;` 仅适用于通过 `hermes webhook subscribe` 创建的**动态订阅**。它不会读取 `config.yaml` 中的路由。
:::

---

<a id="filtering-to-specific-actions"></a>
## 筛选特定操作

GitHub 会为许多操作发送 `pull_request` 事件：`opened`、`synchronize`、`reopened`、`closed`、`labeled` 等。`events` 列表仅通过 `X-GitHub-Event` 头部值进行筛选——它无法在路由级别按操作子类型进行过滤。

步骤 1 中的提示词已经通过指示 Agent 对 `closed` 和 `labeled` 事件提前停止来处理这个问题。

<a id="the-agent-still-runs-and-consumes-tokens"></a>
:::warning Agent 仍会运行并消耗 Token
“在此停止”的指令阻止了有意义的审查，但无论是什么操作，Agent 仍会为每个 `pull_request` 事件运行至完成。GitHub webhook 只能按事件类型（`pull_request`、`push`、`issues` 等）筛选——不能按操作子类型（`opened`、`closed`、`labeled`）筛选。没有针对子操作的路由级过滤器。对于高流量的仓库，要么接受这个成本，要么使用 GitHub Actions 工作流在上游进行条件筛选，再调用你的 webhook URL。
:::

> 没有 Jinja2 或条件模板语法。`{field}` 和 `{nested.field}` 是唯一支持的替换方式。其他任何内容都会原样传递给 Agent。

## 将响应发送到 Slack 或 Discord

将路由中的 `deliver` 和 `deliver_extra` 字段替换为目标平台：

```yaml
# 在 platforms.webhook.extra.routes.<route-name> 内部：

# Slack
deliver: slack
deliver_extra:
  chat_id: "C0123456789"   # Slack 频道 ID（省略则使用配置的主频道）

# Discord
deliver: discord
deliver_extra:
  chat_id: "987654321012345678"  # Discord 频道 ID（省略则使用主频道）
```

目标平台也必须在网关中启用并连接。如果省略 `chat_id`，响应将被发送到该平台配置的主频道。

有效的 `deliver` 值：`log` · `github_comment` · `telegram` · `discord` · `slack` · `signal` · `sms`

---

## GitLab 支持

同一个适配器也适用于 GitLab。GitLab 使用 `X-Gitlab-Token` 进行身份验证（纯字符串匹配，非 HMAC）—— Hermes 会自动处理这两种方式。

对于事件过滤，GitLab 将 `X-GitLab-Event` 设置为诸如 `Merge Request Hook`、`Push Hook`、`Pipeline Hook` 等值。在 `events` 中使用确切的头部值：

```yaml
events:
  - Merge Request Hook
```

GitLab 的有效负载字段与 GitHub 不同——例如，MR 标题使用 `{object_attributes.title}`，MR 编号使用 `{object_attributes.iid}`。发现完整有效负载结构最简单的方法是使用 GitLab 网页钩子设置中的 **Test** 按钮，结合 **Recent Deliveries** 日志。或者，在路由配置中省略 `prompt` —— Hermes 随后会将完整的有效负载作为格式化 JSON 直接传递给 Agent，而 Agent 的响应（在网关日志中通过 `deliver: log` 可见）将描述其结构。

---

## 安全注意事项 {#security-notes}

将 webhook 暴露到互联网时，应把所有负载字段视为不可信输入。最少需要做到：

- 在隔离环境中运行网关，例如 Docker、SSH 后端或受限主机。
- 为路由配置强随机 `secret`，并定期轮换。
- 仅启用完成任务所需的最小工具集。
- 不要把 PR 标题、描述和提交消息当作可信指令。

对于高流量仓库，建议在 GitHub Actions 或其他上游自动化层先过滤事件，再把真正需要处理的请求转发到 Hermes。

## 故障排除

| 现象 | 检查项 |
|---|---|
| `401 Invalid signature` | config.yaml 中的密钥与 GitHub webhook 密钥不匹配 |
| `404 Unknown route` | URL 中的路由名称与 `routes:` 中的键不匹配 |
| `429 Rate limit exceeded` | 每个路由每分钟 30 次请求的限制被超出 — 从 GitHub UI 重新投递测试事件时常见；等待一分钟或提高 `extra.rate_limit` |
| 未发布评论 | `gh` 未安装、不在 PATH 中或未认证（`gh auth login`） |
| Agent 运行但无评论 | 检查网关日志 — 如果 Agent 输出为空或仅为 "SKIP"，仍会尝试投递 |
| 端口已被占用 | 更改 config.yaml 中的 `extra.port` |
| Agent 运行但只审查 PR 描述 | 提示词未包含 `gh pr diff` 指令 — 差异内容不在 webhook 负载中 |
| 看不到 ping 事件 | 被忽略的事件仅在 DEBUG 日志级别返回 `{"status":"ignored","event":"ping"}` — 检查 GitHub 的投递日志（仓库 → Settings → Webhooks → 你的 webhook → Recent Deliveries） |

**GitHub 的 Recent Deliveries 标签页**（仓库 → Settings → Webhooks → 你的 webhook）显示了每次投递的确切请求头、负载、HTTP 状态码和响应体。这是在不接触服务器日志的情况下诊断故障的最快方法。

---

## 完整配置参考

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"         # 绑定地址 (默认: 0.0.0.0)
      port: 8644               # 监听端口 (默认: 8644)
      secret: ""               # 可选的全局备用密钥
      rate_limit: 30           # 每个路由每分钟请求数
      max_body_bytes: 1048576  # 负载大小限制，单位字节 (默认: 1 MB)

      routes:
        <route-name>:
          secret: "required-per-route"
          events: []            # [] = 接受所有；否则列出 X-GitHub-Event 值
          prompt: ""            # {field} / {nested.field} 从负载中解析
          skills: []            # 加载第一个匹配的技能（仅一个）
          deliver: "log"        # log | github_comment | telegram | discord | slack | signal | sms
          deliver_extra: {}     # github_comment 需要 repo + pr_number；其他需要 chat_id
```
---

<a id="what-s-next"></a>
## 下一步？

- **[基于 Cron 的 PR 审查](./github-pr-review-agent.md)** — 按计划轮询 PR，无需公共端点
- **[Webhook 参考文档](/user-guide/messaging/webhooks)** — webhook 平台的完整配置参考
- **[构建一个插件](/guides/build-a-hermes-plugin)** — 将审查逻辑打包成可共享的插件
- **[配置文件](/user-guide/profiles)** — 使用具有独立内存和配置的专用审查者配置文件运行
