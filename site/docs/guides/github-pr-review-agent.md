---
sidebar_position: 10
title: "教程：GitHub PR 审查 Agent"
description: "构建一个自动化的 AI 代码审查器，监控你的代码仓库、审查拉取请求并交付反馈——全程无需手动操作"
---

<a id="tutorial-build-a-github-pr-review-agent"></a>
# 教程：构建一个 GitHub PR 审查 Agent

**问题所在：** 你的团队创建 PR 的速度比你审查的速度还快。PR 等待审查的时间长达数天。初级开发者合并了有问题的代码，因为没人有时间检查。你每天早晨都在追赶代码差异，而不是进行构建工作。

**解决方案：** 一个全天候监控你代码仓库的 AI Agent，它会审查每一个新 PR 的缺陷、安全问题和代码质量，并发送摘要给你——这样你只需将时间花在真正需要人工判断的 PR 上。

**你将构建的内容：**

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────────┐
│  定时任务    │────▶│  Hermes Agent │────▶│  GitHub API  │────▶│  审查结果    │
│  (每 2 小时) │     │  + gh CLI     │     │  (PR 差异)   │     │  发送到      │
│              │     │  + skill      │     │              │     │  Telegram/   │
│              │     │  + memory     │     │              │     │  Discord/    │
│              │     │               │     │              │     │  本地文件    │
└──────────────┘     └───────────────┘     └──────────────┘     └──────────────┘
```

本指南使用**定时任务**来按计划轮询 PR——无需服务器或公共端点。可在 NAT 和防火墙后工作。

:::tip 想要实时审查？
如果你有可用的公共端点，请查看[使用 Webhook 实现自动化的 GitHub PR 评论](./webhook-github-pr-review.md)——当 PR 被创建或更新时，GitHub 会立即将事件推送给 Hermes。
:::
<a id="want-real-time-reviews-instead"></a>

---

<a id="prerequisites"></a>
## 先决条件

- **已安装 Hermes Agent** — 参见[安装指南](/getting-started/installation)
- **运行 Gateway 以支持定时任务**：
  ```bash
  hermes gateway install   # 安装为服务
  # 或
  hermes gateway           # 在前台运行
  ```
- **已安装并认证 GitHub CLI (`gh`)**：
  ```bash
  # 安装
  brew install gh        # macOS
  sudo apt install gh    # Ubuntu/Debian

  # 认证
  gh auth login
  ```
- **已配置消息通知**（可选）— [Telegram](/user-guide/messaging/telegram) 或 [Discord](/user-guide/messaging/discord)

:::tip 没有消息通知？没关系
使用 `deliver: "local"` 将审查结果保存到 `~/.hermes/cron/output/`。这是在连接通知前进行测试的好方法。
<a id="no-messaging-no-problem"></a>
:::

---

<a id="step-1-verify-the-setup"></a>
## 步骤 1：验证设置

确保 Hermes 可以访问 GitHub。启动一个聊天会话：

```bash
hermes
```

用一个简单的命令测试：

```
Run: gh pr list --repo NousResearch/hermes-agent --state open --limit 3
```

你应该能看到一个打开的 PR 列表。如果这能正常工作，说明你已经准备就绪。

---

<a id="step-2-try-a-manual-review"></a>
## 步骤 2：尝试手动审查

仍在聊天会话中，让 Hermes 审查一个真实的 PR：
```
审查这个拉取请求。阅读差异，检查 bug、安全问题以及代码质量。具体说明行号并引用有问题的代码。

运行：gh pr diff 3888 --repo NousResearch/hermes-agent
```

Hermes 将会：
1. 执行 `gh pr diff` 来获取代码变更
2. 通读整个差异
3. 生成一份包含具体发现的结构化审查报告

如果你对质量满意，就可以开始自动化了。

---

<a id="step-3-create-a-review-skill"></a>
## 步骤 3：创建一个审查技能

技能为 Hermes 提供了跨会话和定时任务运行的一致审查指南。没有它，审查质量会参差不齐。

```bash
mkdir -p ~/.hermes/skills/code-review
```

创建 `~/.hermes/skills/code-review/SKILL.md`：

```markdown
---
name: code-review
description: 审查拉取请求中的 bug、安全问题和代码质量
---

# 代码审查指南

审查拉取请求时：

## 检查内容
1.  **Bug** — 逻辑错误、差一错误、空值/未定义处理
2.  **安全** — 注入、认证绕过、代码中的密钥、SSRF
3.  **性能** — N+1 查询、无限循环、内存泄漏
4.  **风格** — 命名规范、死代码、缺少错误处理
5.  **测试** — 变更是否经过测试？测试是否覆盖边界情况？

## 输出格式
对于每个发现：
-   **文件:行号** — 确切位置
-   **严重程度** — 严重 / 警告 / 建议
-   **问题** — 一句话描述
-   **修复** — 如何修复

## 规则
-   要具体。引用有问题的代码。
-   除非影响可读性，否则不要标记风格上的小问题。
-   如果 PR 看起来不错，就如实说明。不要无中生有。
-   以以下方式结尾：APPROVE / REQUEST_CHANGES / COMMENT
```

验证它是否已加载 — 启动 `hermes`，你应该能在启动时的技能列表中看到 `code-review`。

---

<a id="step-4-teach-it-your-conventions"></a>
## 步骤 4：教会它你的团队规范

这才是让审查者真正有用的地方。启动一个会话，教会 Hermes 你团队的标准：

```
记住：在我们的后端仓库中，我们使用 Python 和 FastAPI。
所有端点必须有类型注解和 Pydantic 模型。
我们不允许使用原始 SQL — 只允许使用 SQLAlchemy ORM。
测试文件放在 tests/ 目录下，并且必须使用 pytest fixtures。
```

```
记住：在我们的前端仓库中，我们使用 TypeScript 和 React。
不允许使用 `any` 类型。所有组件必须有 props 接口。
我们使用 React Query 进行数据获取，永远不要用 useEffect 来调用 API。
```

这些记忆会永久保存 — 审查者将强制执行你的规范，而无需每次都被告知。

---

<a id="step-5-create-the-automated-cron-job"></a>
## 步骤 5：创建自动化定时任务

现在把所有部分整合起来。创建一个每 2 小时运行一次的定时任务：
```bash
hermes cron create "0 */2 * * *" \
  "检查新开的 PR 并进行评审。

需要监控的仓库：
- myorg/backend-api
- myorg/frontend-app

步骤：
1. 运行：gh pr list --repo REPO --state open --limit 5 --json number,title,author,createdAt
2. 对于过去 4 小时内创建或更新的每个 PR：
   - 运行：gh pr diff NUMBER --repo REPO
   - 使用代码评审指南来评审差异
3. 按以下格式输出：

## PR 评审 — 今天

### [repo] #[number]: [title]
**作者：** [name] | **结论：** APPROVE/REQUEST_CHANGES/COMMENT
[评审发现]

如果没找到新 PR，请说：没有需要评审的新 PR。" \
  --name "pr-review" \
  --deliver telegram \
  --skill code-review
```

验证它是否已安排：

```bash
hermes cron list
```

<a id="other-useful-schedules"></a>
### 其他有用的时间表

| 时间表 | 何时执行 |
|----------|------|
| `0 */2 * * *` | 每 2 小时 |
| `0 9,13,17 * * 1-5` | 每天三次，仅限工作日 |
| `0 9 * * 1` | 每周一上午汇总 |
| `30m` | 每 30 分钟（适用于高流量仓库） |

---

<a id="step-6-run-it-on-demand"></a>
## 步骤 6：按需运行

不想等待计划时间？手动触发它：

```bash
hermes cron run pr-review
```

或者在聊天会话中：

```
/cron run pr-review
```

---

<a id="going-further"></a>
## 更进一步

<a id="post-reviews-directly-to-github"></a>
### 直接将评审发布到 GitHub

不让 Agent 将结果发送到 Telegram，而是让它直接在 PR 上评论：

将此添加到你的 cron 提示词中：

```
评审后，发布你的评审：
- 对于一般问题：gh pr review NUMBER --repo REPO --comment --body "YOUR_REVIEW"
- 对于严重问题：gh pr review NUMBER --repo REPO --request-changes --body "YOUR_REVIEW"
- 对于干净的 PR：gh pr review NUMBER --repo REPO --approve --body "Looks good"
```

:::caution
确保 `gh` 拥有 `repo` 范围的令牌。评论将以 `gh` 认证的用户身份发布。
:::

<a id="weekly-pr-dashboard"></a>
### 每周 PR 仪表板

创建一个周一上午的仓库概览：

```bash
hermes cron create "0 9 * * 1" \
  "生成每周 PR 仪表板：
- myorg/backend-api
- myorg/frontend-app
- myorg/infra

为每个仓库显示：
1. 打开的 PR 数量和最旧的 PR 存在时间
2. 本周合并的 PR
3. 陈旧的 PR（超过 5 天）
4. 没有分配评审者的 PR

格式化为清晰的摘要。" \
  --name "weekly-dashboard" \
  --deliver telegram
```

<a id="multi-repo-monitoring"></a>
### 多仓库监控

通过在提示词中添加更多仓库来扩大规模。Agent 会按顺序处理它们——无需额外设置。

---

<a id="troubleshooting"></a>
## 故障排除

<a id="gh-command-not-found"></a>
### "gh: command not found"
网关运行在最小化环境中。确保 `gh` 在系统 PATH 中，并重启网关。

<a id="reviews-are-too-generic"></a>
### 评审过于笼统
1. 添加 `code-review` 技能（步骤 3）
2. 通过记忆功能教 Hermes 你的约定（步骤 4）
3. 它对你的技术栈了解得越多，评审质量就越好
<a id="cron-job-doesn-t-run"></a>
### Cron 定时任务没有运行
```bash
hermes gateway status    # 网关是否在运行？
hermes cron list         # 任务是否已启用？
```

<a id="rate-limits"></a>
### 速率限制
GitHub 允许认证用户每小时进行 5,000 次 API 请求。每次 PR 审查会使用约 3-5 次请求（列出、差异对比、可选评论）。即使每天审查 100 个 PR，也远远不会超出限制。

---

<a id="what-s-next"></a>
## 下一步做什么？

- **[基于 Webhook 的 PR 审查](./webhook-github-pr-review.md)** — 在 PR 创建时立即获得审查（需要一个公共端点）
- **[每日简报机器人](/guides/daily-briefing-bot)** — 将 PR 审查与你的晨间新闻摘要相结合
- **[构建一个插件](/guides/build-a-hermes-plugin)** — 将审查逻辑封装成一个可共享的插件
- **[配置文件](/user-guide/profiles)** — 使用独立的记忆和配置运行一个专用的审查者配置文件
- **[备用提供商](/user-guide/features/fallback-providers)** — 确保即使一个提供商不可用时，审查也能运行
