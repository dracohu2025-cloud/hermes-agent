---
title: "Opencode — 将编码委托给 OpenCode CLI（功能、PR 审查）"
sidebar_label: "Opencode"
description: "将编码委托给 OpenCode CLI（功能、PR 审查）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="opencode"></a>
# Opencode

将编码委托给 OpenCode CLI（功能、PR 审查）。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/autonomous-ai-agents/opencode` |
| 版本 | `1.2.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `OpenCode`, `Autonomous`, `Refactoring`, `Code-Review` |
| 相关技能 | [`claude-code`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code), [`codex`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。当技能激活时，Agent 会将这些内容视为指令。
:::

<a id="opencode-cli"></a>
# OpenCode CLI

将 [OpenCode](https://opencode.ai) 用作由 Hermes 终端/进程工具编排的自主编码 worker。OpenCode 是一个与提供商无关的开源 AI 编码 Agent，具有 TUI 和 CLI。

<a id="when-to-use"></a>
## 何时使用

- 用户明确要求使用 OpenCode
- 你需要外部编码 Agent 来实现/重构/审查代码
- 你需要需要进度检查的长时间编码会话
- 你希望在隔离的工作目录/worktrees 中并行执行任务

<a id="prerequisites"></a>
## 先决条件

- 已安装 OpenCode：`npm i -g opencode-ai@latest` 或 `brew install anomalyco/tap/opencode`
- 已配置认证：`opencode auth login` 或设置提供商环境变量（OPENROUTER_API_KEY 等）
- 验证：`opencode auth list` 应至少显示一个提供商
- 用于编码任务的 Git 仓库（推荐）
- 交互式 TUI 会话需要 `pty=true`

<a id="binary-resolution-important"></a>
## 二进制解析（重要）

Shell 环境可能解析到不同的 OpenCode 二进制文件。如果终端和 Hermes 的行为不同，请检查：

```
terminal(command="which -a opencode")
terminal(command="opencode --version")
```

如果需要，可以指定明确的二进制路径：

```
terminal(command="$HOME/.opencode/bin/opencode run '...'", workdir="~/project", pty=true)
```

<a id="one-shot-tasks"></a>
## 一次性任务

使用 `opencode run` 执行有边界、非交互的任务：

```
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

使用 `-f` 附加上下文文件：

```
terminal(command="opencode run 'Review this config for security issues' -f config.yaml -f .env.example", workdir="~/project")
```

使用 `--thinking` 显示模型思考过程：

```
terminal(command="opencode run 'Debug why tests fail in CI' --thinking", workdir="~/project")
```

强制使用特定模型：

```
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

<a id="interactive-sessions-background"></a>
## 交互式会话（后台运行）

对于需要多次交互的迭代工作，在后台启动 TUI：
```
terminal(command="opencode", workdir="~/project", background=true, pty=true)
# 返回 session_id

# 发送提示词
process(action="submit", session_id="<id>", data="实现 OAuth 刷新流程并添加测试")

# 监控进度
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 发送后续输入
process(action="submit", session_id="<id>", data="现在为 token 过期添加错误处理")

# 干净退出 — Ctrl+C
process(action="write", session_id="<id>", data="\x03")
# 或者直接终止进程
process(action="kill", session_id="<id>")
```

**重要提示：** 不要使用 `/exit` —— 它不是有效的 OpenCode 命令，反而会打开 Agent 选择对话框。请使用 Ctrl+C（`\x03`）或 `process(action="kill")` 来退出。

<a id="tui-keybindings"></a>
### TUI 快捷键

| 按键 | 操作 |
|-----|--------|
| `Enter` | 提交消息（如需可连按两次） |
| `Tab` | 在 Agent 之间切换（build/plan） |
| `Ctrl+P` | 打开命令面板 |
| `Ctrl+X L` | 切换会话 |
| `Ctrl+X M` | 切换模型 |
| `Ctrl+X N` | 新建会话 |
| `Ctrl+X E` | 打开编辑器 |
| `Ctrl+C` | 退出 OpenCode |

<a id="resuming-sessions"></a>
### 恢复会话

退出后，OpenCode 会打印一个会话 ID。可通过以下方式恢复：

```
terminal(command="opencode -c", workdir="~/project", background=true, pty=true)  # 继续上次会话
terminal(command="opencode -s ses_abc123", workdir="~/project", background=true, pty=true)  # 指定会话
```

<a id="common-flags"></a>
## 常用标志

| 标志 | 用途 |
|------|------|
| `run 'prompt'` | 一次性执行并退出 |
| `--continue` / `-c` | 继续上次的 OpenCode 会话 |
| `--session &lt;id&gt;` / `-s` | 继续指定会话 |
| `--agent &lt;name&gt;` | 选择 OpenCode Agent（build 或 plan） |
| `--model provider/model` | 强制指定模型 |
| `--format json` | 机器可读的输出/事件 |
| `--file &lt;path&gt;` / `-f` | 将文件附加到消息中 |
| `--thinking` | 显示模型思考过程 |
| `--variant &lt;level&gt;` | 推理力度（high、max、minimal） |
| `--title &lt;name&gt;` | 为会话命名 |
| `--attach &lt;url&gt;` | 连接到正在运行的 opencode 服务器 |

<a id="procedure"></a>
## 操作步骤

1. 验证工具就绪：
   - `terminal(command="opencode --version")`
   - `terminal(command="opencode auth list")`
2. 对于有明确边界的任务，使用 `opencode run '...'`（无需 pty）。
3. 对于迭代式任务，使用 `background=true, pty=true` 启动 `opencode`。
4. 使用 `process(action="poll"|"log")` 监控长时间运行的任务。
5. 如果 OpenCode 要求输入，通过 `process(action="submit", ...)` 响应。
6. 使用 `process(action="write", data="\x03")` 或 `process(action="kill")` 退出。
7. 向用户总结文件变更、测试结果和后续步骤。

<a id="pr-review-workflow"></a>
## PR 审查工作流

OpenCode 内置了 PR 命令：

```
terminal(command="opencode pr 42", workdir="~/project", pty=true)
```

或者为了隔离审查，在临时克隆中进行：

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.' -f $(git diff origin/main --name-only | head -20 | tr '\n' ' ')", pty=true)
```
<a id="parallel-work-pattern"></a>
## 并行工作模式

使用独立的工作目录/工作树来避免冲突：

```
terminal(command="opencode run '修复 issue #101 并提交'", workdir="/tmp/issue-101", background=true, pty=true)
terminal(command="opencode run '添加解析器回归测试并提交'", workdir="/tmp/issue-102", background=true, pty=true)
process(action="list")
```

<a id="session-cost-management"></a>
## 会话与成本管理

列出历史会话：

```
terminal(command="opencode session list")
```

查看 Token 用量和成本：

```
terminal(command="opencode stats")
terminal(command="opencode stats --days 7 --models anthropic/claude-sonnet-4")
```

<a id="pitfalls"></a>
## 常见陷阱

- 交互式 `opencode`（TUI）会话需要设置 `pty=true`。`opencode run` 命令**不需要** pty。
- `/exit` **不是**有效命令——它会打开 Agent 选择器。请使用 Ctrl+C 退出 TUI。
- PATH 不匹配可能导致选错 OpenCode 二进制文件或模型配置。
- 如果 OpenCode 卡住，先检查日志再终止：
  - `process(action="log", session_id="&lt;id&gt;")`
- 避免在多个并行的 OpenCode 会话中共享同一个工作目录。
- 在 TUI 中可能需要按两次回车才能提交（第一次确认文本，第二次发送）。

<a id="verification"></a>
## 验证

冒烟测试：

```
terminal(command="opencode run '请只回复：OPENCODE_SMOKE_OK'")
```

成功标准：
- 输出包含 `OPENCODE_SMOKE_OK`
- 命令正常退出，无提供商/模型错误
- 对于代码任务：预期文件已变更且测试通过

<a id="rules"></a>
## 规则

1. 优先使用 `opencode run` 进行一次性自动化——它更简单且不需要 pty。
2. 仅在需要迭代时使用交互式后台模式。
3. 始终将 OpenCode 会话限定在单个仓库/工作目录范围内。
4. 对于耗时任务，通过 `process` 日志提供进度更新。
5. 报告具体结果（变更的文件、测试情况、剩余风险）。
6. 使用 Ctrl+C 或 kill 退出交互式会话，切勿使用 `/exit`。
