---
sidebar_position: 10
title: "教程：GitHub PR 审查 Agent"
description: "构建一个自动化的 AI 代码审查工具，监控你的仓库、审查拉取请求并交付反馈——全程无需人工干预"
---

# 教程：构建一个 GitHub PR 审查 Agent {#tutorial-build-a-github-pr-review-agent}

**问题：** 团队开 PR 的速度比你审查的速度还快。PR 堆积好几天没人看。初级开发者合入了有问题的代码，因为没人有时间检查。你每天早晨都在追着看 diff，而不是在写代码。

**解决方案：** 一个 AI Agent 全天候监控你的仓库，审查每一个新 PR 中的 bug、安全问题和代码质量，并给你发送摘要——这样你只需要花时间在那些真正需要人工判断的 PR 上。

**你将构建的内容：**

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│   Cron 定时器  ──▶  Hermes Agent  ──▶  GitHub API  ──▶  审查      │
│   (每 2 小时)      + gh CLI           (PR diffs)       交付       │
│                    + skill                             (Telegram, │
│                    + memory                            Discord,   │
│                                                        local)     │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

本指南使用 **cron 任务** 按计划轮询 PR——无需服务器或公共端点。可在 NAT 和防火墙后工作。

:::tip 想要实时审查？
如果你有可用的公共端点，请查看 [使用 Webhook 的自动化 GitHub PR 评论](./webhook-github-pr-review.md) —— 当 PR 被打开或更新时，GitHub 会立即向 Hermes 推送事件。
:::
<a id="want-real-time-reviews-instead"></a>

---

## 前提条件 {#prerequisites}

- **已安装 Hermes Agent** —— 请参阅 [安装指南](/getting-started/installation)
- **Gateway 正在运行** 以支持 cron 任务：
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
- **已配置消息服务**（可选）—— [Telegram](/user-guide/messaging/telegram) 或 [Discord](/user-guide/messaging/discord)

:::tip 没有消息服务？没问题
使用 `deliver: "local"` 将审查结果保存到 `~/.hermes/cron/output/`。在配置通知之前，非常适合用于测试。
<a id="no-messaging-no-problem"></a>
:::

---

## 第一步：验证设置 {#step-1-verify-the-setup}

确保 Hermes 可以访问 GitHub。启动一个对话：

```bash
hermes
```

用一个简单的命令测试：

```
运行：gh pr list --repo NousResearch/hermes-agent --state open --limit 3
```

你应该会看到一列打开的 PR。如果这能正常工作，你就准备好了。

---

## 第二步：尝试手动审查 {#step-2-try-a-manual-review}

仍在对话中，让 Hermes 审查一个真实的 PR：

```
审查这个拉取请求。阅读 diff，检查 bug、安全问题
和代码质量。要具体指出行号，并引用有问题的代码。

运行：gh pr diff 3888 --repo NousResearch/hermes-agent
```

Hermes 将：
1. 执行 `gh pr diff` 来获取代码变更
2. 通读整个 diff
3. 生成一份结构化的审查报告，包含具体的发现
如果你对质量满意，那就该把它自动化了。

---

## 第三步：创建审查技能 {#step-3-create-a-review-skill}

技能（Skill）能让 Hermes 拥有一致的审查准则，这些准则会在多次会话和定时任务中持续生效。没有技能的话，审查质量会参差不齐。

```bash
mkdir -p ~/.hermes/skills/code-review
```

创建 `~/.hermes/skills/code-review/SKILL.md`：

```markdown
---
name: code-review
description: 审查拉取请求中的错误、安全问题和代码质量
---

# 代码审查准则

审查拉取请求时：

## 检查内容
1. **错误** — 逻辑错误、差一错误、null/undefined 处理
2. **安全** — 注入、认证绕过、代码中的密钥、SSRF
3. **性能** — N+1 查询、无界循环、内存泄漏
4. **风格** — 命名规范、死代码、缺少错误处理
5. **测试** — 变更是否经过测试？测试是否覆盖了边界情况？

## 输出格式
对于每个发现：
- **文件:行号** — 精确位置
- **严重程度** — 严重 / 警告 / 建议
- **问题描述** — 一句话说明
- **修复方法** — 如何修复

## 规则
- 要具体。引用有问题的代码。
- 除非影响可读性，否则不要挑剔风格细节。
- 如果拉取请求看起来没问题，就直说。不要无中生有。
- 以以下内容结尾：APPROVE / REQUEST_CHANGES / COMMENT
```

验证技能已加载 — 启动 `hermes`，你应该会在启动时的技能列表中看到 `code-review`。

---

## 第四步：教它你的约定 {#step-4-teach-it-your-conventions}

这一步能让审查工具真正有用。启动一个会话，教 Hermes 你们团队的规范：

```
记住：在我们的后端仓库中，我们使用 Python 和 FastAPI。
所有端点必须有类型注解和 Pydantic 模型。
我们不允许使用原生 SQL — 只使用 SQLAlchemy ORM。
测试文件放在 tests/ 目录下，并且必须使用 pytest fixtures。
```

```
记住：在我们的前端仓库中，我们使用 TypeScript 和 React。
不允许使用 `any` 类型。所有组件必须有 props 接口。
我们使用 React Query 进行数据获取，绝不用 useEffect 来调用 API。
```

这些记忆会永久保存 — 审查工具会自动执行你的约定，无需每次都重新说明。

---

## 第五步：创建自动化定时任务 {#step-5-create-the-automated-cron-job}

现在把所有东西串联起来。创建一个每 2 小时运行一次的定时任务：

```bash
hermes cron create "0 */2 * * *" \
  "检查新的开放 PR 并进行审查。

要监控的仓库：
- myorg/backend-api
- myorg/frontend-app

步骤：
1. 运行：gh pr list --repo REPO --state open --limit 5 --json number,title,author,createdAt
2. 对于过去 4 小时内创建或更新的每个 PR：
   - 运行：gh pr diff NUMBER --repo REPO
   - 使用代码审查准则审查差异
3. 输出格式如下：

## PR 审查 — 今天

### [repo] #[number]: [title]
**作者：** [name] | **结论：** APPROVE/REQUEST_CHANGES/COMMENT
[发现的问题]

如果没有找到新的 PR，则输出：没有新的 PR 需要审查。" \
  --name "pr-review" \
  --deliver telegram \
  --skill code-review
```

验证任务已安排：

```bash
hermes cron list
```

### 其他有用的调度 {#other-useful-schedules}

| 调度表达式 | 执行时间 |
|----------|------|
| `0 */2 * * *` | 每 2 小时 |
| `0 9,13,17 * * 1-5` | 每天三次，仅工作日 |
| `0 9 * * 1` | 每周一早上汇总 |
| `30m` | 每 30 分钟（高流量仓库） |

## 更进一步

### 直接将评审发布到 GitHub

让 Agent 直接在 PR 上评论，而不是发送到 Telegram：

在 cron 提示词中添加以下内容：

```
评审完成后，请发布你的评审意见：
- 对于问题：gh pr review NUMBER --repo REPO --comment --body "YOUR_REVIEW"
- 对于严重问题：gh pr review NUMBER --repo REPO --request-changes --body "YOUR_REVIEW"
- 对于干净的 PR：gh pr review NUMBER --repo REPO --approve --body "Looks good"
```

:::caution
确保 `gh` 拥有包含 `repo` 作用域的令牌。评审将以 `gh` 当前认证的用户身份发布。
:::

### 每周 PR 仪表盘

创建一个周一早晨的仓库概览：

```bash
hermes cron create "0 9 * * 1" \
  "生成一份每周 PR 仪表盘：
- myorg/backend-api
- myorg/frontend-app
- myorg/infra

针对每个仓库展示：
1. 打开的 PR 数量及最旧 PR 的存续时间
2. 本周已合并的 PR
3. 过时的 PR（超过 5 天）
4. 未分配评审人的 PR

格式要求为简洁的摘要。" \
  --name "weekly-dashboard" \
  --deliver telegram
```

### 多仓库监控

通过在提示词中添加更多仓库来扩展规模。Agent 会按顺序处理它们——无需额外设置。

---

## 故障排除

### "gh: command not found"
网关运行在最小化环境中。请确保 `gh` 在系统 PATH 中，然后重启网关。

### 评审过于泛泛
1. 添加 `code-review` 技能（第三步）
2. 通过记忆功能教会 Hermes 你的代码规范（第四步）
3. Agent 对你技术栈的了解越多，评审质量就越高

### Cron 任务不运行
```bash
hermes gateway status    # 网关是否在运行？
hermes cron list         # 任务是否已启用？
```

### 速率限制
GitHub 允许已认证用户每小时发起 5,000 次 API 请求。每次 PR 评审大约消耗 3-5 次请求（列表 + diff + 可选评论）。即使每天评审 100 个 PR，也远在限制范围内。

---

## 下一步做什么？

- **[基于 Webhook 的 PR 评审](./webhook-github-pr-review.md)** — 当 PR 被打开时立即获得评审（需要公网端点）
- **[每日简报机器人](/guides/daily-briefing-bot)** — 将 PR 评审与你的早间新闻摘要结合起来
- **[构建一个插件](/guides/build-a-hermes-plugin)** — 将评审逻辑封装成可共享的插件
- **[配置文件](/user-guide/profiles)** — 运行一个拥有独立记忆和配置的专用评审人配置文件
- **[备用提供商](/user-guide/features/fallback-providers)** — 确保即使某个提供商宕机，评审也能照常进行
