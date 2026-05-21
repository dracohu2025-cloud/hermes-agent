---
title: "Codex — 将编码任务委托给 OpenAI Codex CLI（功能、PR）"
sidebar_label: "Codex"
description: "将编码任务委托给 OpenAI Codex CLI（功能、PR）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="codex"></a>
# Codex

将编码任务委托给 OpenAI Codex CLI（功能、PR）。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/autonomous-ai-agents/codex` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `Codex`, `OpenAI`, `Code-Review`, `Refactoring` |
| 相关技能 | [`claude-code`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="codex-cli"></a>
# Codex CLI

通过 Hermes 终端将编码任务委托给 [Codex](https://github.com/openai/codex)。Codex 是 OpenAI 的自主编码 Agent CLI。

<a id="when-to-use"></a>
## 何时使用

- 构建功能
- 重构
- PR 审查
- 批量修复问题

需要安装 codex CLI 并拥有一个 git 仓库。

<a id="prerequisites"></a>
## 前置条件

- 已安装 Codex：`npm install -g @openai/codex`
- 已配置 OpenAI 认证：`OPENAI_API_KEY` 或来自 Codex CLI 登录流程的 Codex OAuth 凭据
- **必须在 git 仓库内运行** — Codex 拒绝在仓库外运行
- 在终端调用中使用 `pty=true` — Codex 是一个交互式终端应用

对于 Hermes 自身，`model.provider: openai-codex` 使用 Hermes 管理的 Codex OAuth（来自 `~/.hermes/auth.json`，通过 `hermes auth add openai-codex` 配置）。对于独立的 Codex CLI，有效的 CLI OAuth 会话可能位于 `~/.codex/auth.json`；不要仅凭缺少 `OPENAI_API_KEY` 就断定 Codex 认证缺失。

<a id="one-shot-tasks"></a>
## 一次性任务

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

用于临时工作（Codex 需要 git 仓库）：
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

<a id="background-mode-long-tasks"></a>
## 后台模式（长时间任务）

```
# 在后台启动，使用 PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# 返回 session_id

# 监控进度
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 如果 Codex 提问，发送输入
process(action="submit", session_id="<id>", data="yes")

# 如果需要，终止
process(action="kill", session_id="<id>")
```

<a id="key-flags"></a>
## 关键标志

| 标志 | 效果 |
|------|------|
| `exec "prompt"` | 一次性执行，完成后退出 |
| `--full-auto` | 沙箱化，但自动批准工作区中的文件更改 |
| `--yolo` | 无沙箱，无批准（最快，最危险） |

<a id="pr-reviews"></a>
## PR 审查

克隆到临时目录进行安全审查：

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```
<a id="parallel-issue-fixing-with-worktrees"></a>
## 使用工作树并行修复问题

```
# 创建工作树
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# 在每个工作树中启动 Codex
terminal(command="codex --yolo exec '修复问题 #78：<描述>。完成后提交。'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec '修复问题 #99：<描述>。完成后提交。'", workdir="/tmp/issue-99", background=true, pty=true)

# 监控
process(action="list")

# 完成后，推送并创建 PR
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title '修复: ...' --body '...'")

# 清理
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

<a id="batch-pr-reviews"></a>
## 批量 PR 审核

```
# 获取所有 PR 引用
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# 并行审核多个 PR
terminal(command="codex exec '审核 PR #86。git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec '审核 PR #87。git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# 发布结果
terminal(command="gh pr comment 86 --body '<审核结果>'", workdir="~/project")
```

<a id="rules"></a>
## 规则

1. **始终使用 `pty=true`** — Codex 是交互式终端应用，没有 PTY 会挂起
2. **需要 Git 仓库** — Codex 不会在 Git 目录外运行。临时目录用 `mktemp -d && git init`
3. **一次性任务用 `exec`** — `codex exec "提示"` 运行并正常退出
4. **构建时用 `--full-auto`** — 自动批准沙箱内的更改
5. **长时间任务用后台** — 使用 `background=true` 并用 `process` 工具监控
6. **不要干扰** — 用 `poll`/`log` 监控，对长时间运行的任务保持耐心
7. **并行没问题** — 可同时运行多个 Codex 进程以批量处理
