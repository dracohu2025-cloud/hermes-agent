---
title: "Claude Code — 将编码任务委托给 Claude Code CLI（功能、PR）"
sidebar_label: "Claude Code"
description: "将编码任务委托给 Claude Code CLI（功能、PR）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Claude Code {#claude-code}

将编码任务委托给 Claude Code CLI（功能、PR）。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/autonomous-ai-agents/claude-code` |
| 版本 | `2.2.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 标签 | `Coding-Agent`, `Claude`, `Anthropic`, `Code-Review`, `Refactoring`, `PTY`, `Automation` |
| 相关技能 | [`codex`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent), [`opencode`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Claude Code — Hermes 编排指南 {#claude-code-hermes-orchestration-guide}

通过 Hermes 终端将编码任务委托给 [Claude Code](https://code.claude.com/docs/en/cli-reference)（Anthropic 的自主编码 Agent CLI）。Claude Code v2.x 可以自主读取文件、编写代码、运行 shell 命令、生成子 Agent 以及管理 git 工作流。

## 前提条件 {#prerequisites}

- **安装：** `npm install -g @anthropic-ai/claude-code`
- **认证：** 运行 `claude` 一次以登录（Pro/Max 使用浏览器 OAuth，或设置 `ANTHROPIC_API_KEY`）
- **控制台认证：** `claude auth login --console` 用于 API key 计费
- **SSO 认证：** `claude auth login --sso` 用于企业版
- **检查状态：** `claude auth status`（JSON）或 `claude auth status --text`（人类可读）
- **健康检查：** `claude doctor` — 检查自动更新器和安装健康状态
- **版本检查：** `claude --version`（需要 v2.x+）
- **更新：** `claude update` 或 `claude upgrade`

## 两种编排模式 {#two-orchestration-modes}

Hermes 以两种根本不同的方式与 Claude Code 交互。根据任务选择。

### 模式 1：打印模式（`-p`）— 非交互式（大多数任务的首选） {#mode-1-print-mode-p-non-interactive-preferred-for-most-tasks}

打印模式运行一次性任务，返回结果，然后退出。无需 PTY。无需交互提示。这是最简洁的集成路径。

```
terminal(command="claude -p '为 src/ 中所有 API 调用添加错误处理' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**何时使用打印模式：**
- 一次性编码任务（修复 bug、添加功能、重构）
- CI/CD 自动化和脚本编写
- 使用 `--json-schema` 进行结构化数据提取
- 管道输入处理（`cat file | claude -p "分析这个"`）
- 任何不需要多轮对话的任务

**打印模式会跳过所有交互式对话框** — 没有工作区信任提示，没有权限确认。这使其非常适合自动化。

### 模式 2：通过 tmux 的交互式 PTY — 多轮会话 {#mode-2-interactive-pty-via-tmux-multi-turn-sessions}

交互式模式提供一个完整的对话式 REPL，您可以在其中发送后续提示、使用斜杠命令，并实时观察 Claude 的工作。**需要 tmux 编排。**
```
# 启动一个 tmux 会话
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")

# 在会话中启动 Claude Code
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")

# 等待启动完成，然后发送你的任务
# （等待约 3-5 秒让欢迎界面出现）
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Refactor the auth module to use JWT tokens' Enter")

# 通过捕获窗格内容来监控进度
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")

# 发送后续任务
terminal(command="tmux send-keys -t claude-work 'Now add unit tests for the new JWT code' Enter")

# 完成后退出
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

**何时使用交互模式：**
- 多轮迭代工作（重构 → 审查 → 修复 → 测试循环）
- 需要人工参与决策的任务
- 探索性编码会话
- 当你需要使用 Claude 的斜杠命令（`/compact`、`/review`、`/model`）时

## PTY 对话框处理（交互模式的关键） {#pty-dialog-handling-critical-for-interactive-mode}

Claude Code 在首次启动时最多会弹出两个确认对话框。你必须通过 tmux send-keys 来处理它们：

### 对话框 1：工作区信任（首次访问某个目录） {#dialog-1-workspace-trust-first-visit-to-a-directory}
```
❯ 1. Yes, I trust this folder    ← 默认选项（直接按 Enter）
  2. No, exit
```
**处理方式：** `tmux send-keys -t &lt;session&gt; Enter` — 默认选择是正确的。

### 对话框 2：绕过权限警告（仅在使用 --dangerously-skip-permissions 时出现） {#dialog-2-bypass-permissions-warning-only-with-dangerously-skip-permissions}
```
❯ 1. No, exit                    ← 默认选项（错误的选择！）
  2. Yes, I accept
```
**处理方式：** 必须先向下导航，然后按 Enter：
```
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

### 稳健的对话框处理模式 {#robust-dialog-handling-pattern}
```
# 启动时绕过权限
terminal(command="tmux send-keys -t claude-work 'claude --dangerously-skip-permissions \"your task\"' Enter")

# 处理信任对话框（按 Enter 选择默认的 "Yes"）
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")

# 处理权限对话框（先按 Down 再按 Enter 选择 "Yes, I accept"）
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")

# 现在等待 Claude 工作
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -60")
```

**注意：** 首次信任某个目录后，信任对话框不会再出现。只有权限对话框会在每次使用 `--dangerously-skip-permissions` 时重复出现。

## CLI 子命令 {#cli-subcommands}

| 子命令 | 用途 |
|------------|---------|
| `claude` | 启动交互式 REPL |
| `claude "query"` | 启动 REPL 并附带初始提示 |
| `claude -p "query"` | 打印模式（非交互式，完成后退出） |
| `cat file \| claude -p "query"` | 将文件内容通过管道作为 stdin 上下文 |
| `claude -c` | 继续当前目录中最近的对话 |
| `claude -r "id"` | 通过 ID 或名称恢复特定会话 |
| `claude auth login` | 登录（添加 `--console` 用于 API 计费，`--sso` 用于企业版） |
| `claude auth status` | 检查登录状态（返回 JSON；`--text` 用于人类可读格式） |
| `claude mcp add &lt;name&gt; -- &lt;cmd&gt;` | 添加一个 MCP 服务器 |
| `claude mcp list` | 列出已配置的 MCP 服务器 |
| `claude mcp remove &lt;name&gt;` | 移除一个 MCP 服务器 |
| `claude agents` | 列出已配置的 Agents |
| `claude doctor` | 对安装和自动更新程序运行健康检查 |
| `claude update` / `claude upgrade` | 将 Claude Code 更新到最新版本 |
| `claude remote-control` | 启动服务器，以便从 claude.ai 或移动应用控制 Claude |
| `claude install [target]` | 安装原生构建（稳定版、最新版或特定版本） |
| `claude setup-token` | 设置长期有效的认证令牌（需要订阅） |
| `claude plugin` / `claude plugins` | 管理 Claude Code 插件 |
| `claude auto-mode` | 检查自动模式分类器配置 |
## 打印模式深入解析 {#print-mode-deep-dive}

### 结构化 JSON 输出 {#structured-json-output}
```
terminal(command="claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5", workdir="/project", timeout=120)
```

返回一个包含以下字段的 JSON 对象：
```json
{
  "type": "result",
  "subtype": "success",
  "result": "The analysis text...",
  "session_id": "75e2167f-...",
  "num_turns": 3,
  "total_cost_usd": 0.0787,
  "duration_ms": 10276,
  "stop_reason": "end_turn",
  "terminal_reason": "completed",
  "usage": { "input_tokens": 5, "output_tokens": 603, ... },
  "modelUsage": { "claude-sonnet-4-6": { "costUSD": 0.078, "contextWindow": 200000 } }
}
```

**关键字段：** `session_id`（用于恢复会话）、`num_turns`（Agent 循环次数）、`total_cost_usd`（费用追踪）、`subtype`（成功/错误检测，取值有 `success`、`error_max_turns`、`error_budget`）。

### 流式 JSON 输出 {#streaming-json-output}
对于实时 token 流，使用 `stream-json` 并带上 `--verbose`：
```
terminal(command="claude -p 'Write a summary' --output-format stream-json --verbose --include-partial-messages", timeout=60)
```

返回换行分隔的 JSON 事件。配合 jq 可以过滤实时文本：
```
claude -p "Explain X" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

流事件包含 `system/api_retry`，带有 `attempt`、`max_retries` 和 `error` 字段（例如 `rate_limit`、`billing_error`）。

### 双向流式传输 {#bidirectional-streaming}
对于实时输入和输出同时流式化：
```
claude -p "task" --input-format stream-json --output-format stream-json --replay-user-messages
```
`--replay-user-messages` 会在标准输出重新输出用户消息以作确认。

### 管道输入 {#piped-input}
```
# Pipe a file for analysis
terminal(command="cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1", timeout=60)

# Pipe multiple files
terminal(command="cat src/*.py | claude -p 'Find all TODO comments' --max-turns 1", timeout=60)

# Pipe command output
terminal(command="git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1", timeout=60)
```

### 用于结构化提取的 JSON Schema {#json-schema-for-structured-extraction}
```
terminal(command="claude -p 'List all functions in src/' --output-format json --json-schema '{\"type\":\"object\",\"properties\":{\"functions\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}},\"required\":[\"functions\"]}' --max-turns 5", workdir="/project", timeout=90)
```

从 JSON 结果中解析 `structured_output`。Claude 在返回前会根据 schema 校验输出。

### 会话续接 {#session-continuation}
```
# Start a task
terminal(command="claude -p 'Start refactoring the database layer' --output-format json --max-turns 10 > /tmp/session.json", workdir="/project", timeout=180)

# Resume with session ID
terminal(command="claude -p 'Continue and add connection pooling' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"session_id\"])') --max-turns 5", workdir="/project", timeout=120)

# Or resume the most recent session in the same directory
terminal(command="claude -p 'What did you do last time?' --continue --max-turns 1", workdir="/project", timeout=30)

# Fork a session (new ID, keeps history)
terminal(command="claude -p 'Try a different approach' --resume <id> --fork-session --max-turns 10", workdir="/project", timeout=120)
```
### 用于 CI/脚本的 Bare 模式 {#bare-mode-for-ci-scripting}
```
terminal(command="claude --bare -p 'Run all tests and report failures' --allowedTools 'Read,Bash' --max-turns 10", workdir="/project", timeout=180)
```

`--bare` 会跳过 hooks、plugins、MCP 发现以及 CLAUDE.md 加载。启动速度最快。需要 `ANTHROPIC_API_KEY`（跳过 OAuth）。

要在 bare 模式下选择性加载上下文：
| 要加载的内容 | 标志 |
|---------|------|
| 系统提示补充 | `--append-system-prompt "text"` 或 `--append-system-prompt-file path` |
| 设置 | `--settings &lt;file-or-json&gt;` |
| MCP 服务器 | `--mcp-config &lt;file-or-json&gt;` |
| 自定义 Agent | `--agents '&lt;json&gt;'` |

### 过载时的回退模型 {#fallback-model-for-overload}
```
terminal(command="claude -p 'task' --fallback-model haiku --max-turns 5", timeout=90)
```
当默认模型过载时，自动回退到指定模型（仅限 print 模式）。

## 完整 CLI 标志参考 {#complete-cli-flags-reference}

### 会话与环境 {#session-environment}
| 标志 | 作用 |
|------|--------|
| `-p, --print` | 非交互式一次性模式（完成后退出） |
| `-c, --continue` | 恢复当前目录中最近的对话 |
| `-r, --resume &lt;id&gt;` | 按 ID 或名称恢复特定会话（未提供 ID 时显示交互式选择器） |
| `--fork-session` | 恢复时创建新的会话 ID，而不是重用原始 ID |
| `--session-id &lt;uuid&gt;` | 为对话使用特定的 UUID |
| `--no-session-persistence` | 不将会话保存到磁盘（仅限 print 模式） |
| `--add-dir &lt;paths...&gt;` | 授予 Claude 对其他工作目录的访问权限 |
| `-w, --worktree [name]` | 在隔离的 git worktree 中运行，位于 `.claude/worktrees/&lt;name&gt;` |
| `--tmux` | 为 worktree 创建一个 tmux 会话（需要 `--worktree`） |
| `--ide` | 启动时自动连接到有效的 IDE |
| `--chrome` / `--no-chrome` | 启用/禁用 Chrome 浏览器集成以进行 Web 测试 |
| `--from-pr [number]` | 恢复与特定 GitHub PR 关联的会话 |
| `--file &lt;specs...&gt;` | 启动时要下载的文件资源（格式：`file_id:relative_path`） |

### 模型与性能 {#model-performance}
| 标志 | 作用 |
|------|--------|
| `--model &lt;alias&gt;` | 模型选择：`sonnet`、`opus`、`haiku`，或完整名称如 `claude-sonnet-4-6` |
| `--effort &lt;level&gt;` | 推理深度：`low`、`medium`、`high`、`max`、`auto` | 两者 |
| `--max-turns &lt;n&gt;` | 限制 Agent 循环次数（仅限 print 模式；防止失控） |
| `--max-budget-usd &lt;n&gt;` | 以美元为单位的 API 花费上限（仅限 print 模式） |
| `--fallback-model &lt;model&gt;` | 默认模型过载时自动回退（仅限 print 模式） |
| `--betas &lt;betas...&gt;` | 包含在 API 请求中的 Beta 标头（仅限 API 密钥用户） |

### 权限与安全 {#permission-safety}
| 标志 | 作用 |
|------|--------|
| `--dangerously-skip-permissions` | 自动批准所有工具使用（文件写入、bash、网络等） |
| `--allow-dangerously-skip-permissions` | 将绕过作为*选项*启用，但默认不启用 |
| `--permission-mode &lt;mode&gt;` | `default`、`acceptEdits`、`plan`、`auto`、`dontAsk`、`bypassPermissions` |
| `--allowedTools &lt;tools...&gt;` | 白名单特定工具（逗号或空格分隔） |
| `--disallowedTools &lt;tools...&gt;` | 黑名单特定工具 |
| `--tools &lt;tools...&gt;` | 覆盖内置工具集（`""` = 无，`"default"` = 全部，或工具名称） |
### 输出与输入格式 {#output-input-format}
| 标志 | 作用 |
|------|------|
| `--output-format &lt;fmt&gt;` | `text`（默认）、`json`（单个结果对象）、`stream-json`（换行分隔） |
| `--input-format &lt;fmt&gt;` | `text`（默认）或 `stream-json`（实时流式输入） |
| `--json-schema &lt;schema&gt;` | 强制输出符合指定 schema 的结构化 JSON |
| `--verbose` | 输出完整的逐轮交互信息 |
| `--include-partial-messages` | 包含到达的部分消息块（stream-json + 打印） |
| `--replay-user-messages` | 在标准输出上重新输出用户消息（stream-json 双向） |

### 系统提示与上下文 {#system-prompt-context}
| 标志 | 作用 |
|------|--------|
| `--append-system-prompt &lt;text&gt;` | **追加**到默认系统提示（保留内置能力） |
| `--append-system-prompt-file &lt;path&gt;` | **追加**文件内容到默认系统提示 |
| `--system-prompt &lt;text&gt;` | **替换**整个系统提示（通常建议使用 --append） |
| `--system-prompt-file &lt;path&gt;` | **替换**系统提示为文件内容 |
| `--bare` | 跳过钩子、插件、MCP 发现、CLAUDE.md、OAuth（最快启动） |
| `--agents '&lt;json&gt;'` | 动态定义自定义子 Agent，格式为 JSON |
| `--mcp-config &lt;path&gt;` | 从 JSON 文件加载 MCP 服务器（可重复使用） |
| `--strict-mcp-config` | 仅使用 `--mcp-config` 中的 MCP 服务器，忽略所有其他 MCP 配置 |
| `--settings &lt;file-or-json&gt;` | 从 JSON 文件或内联 JSON 加载额外设置 |
| `--setting-sources &lt;sources&gt;` | 逗号分隔的加载来源：`user`、`project`、`local` |
| `--plugin-dir &lt;paths...&gt;` | 仅在此会话中从指定目录加载插件 |
| `--disable-slash-commands` | 禁用所有技能/斜杠命令 |

### 调试 {#debugging}
| 标志 | 作用 |
|------|--------|
| `-d, --debug [filter]` | 启用调试日志，可附带可选类别过滤器（例如 `"api,hooks"`、`"!1p,!file"`） |
| `--debug-file &lt;path&gt;` | 将调试日志写入文件（隐式启用调试模式） |

### Agent 团队 {#agent-teams}
| 标志 | 作用 |
|------|--------|
| `--teammate-mode &lt;mode&gt;` | Agent 团队的显示方式：`auto`、`in-process` 或 `tmux` |
| `--brief` | 启用 `SendUserMessage` 工具，用于 Agent 与用户之间的通信 |

### --allowedTools / --disallowedTools 的工具名称语法 {#tool-name-syntax-for-allowedtools-disallowedtools}
```
Read                    # 所有文件读取
Edit                    # 文件编辑（已有文件）
Write                   # 文件创建（新文件）
Bash                    # 所有 shell 命令
Bash(git *)             # 仅 git 命令
Bash(git commit *)      # 仅 git commit 命令
Bash(npm run lint:*)    # 带通配符的模式匹配
WebSearch               # 网页搜索能力
WebFetch                # 网页抓取
mcp__<server>__<tool>   # 特定 MCP 工具
```

## 设置与配置 {#settings-configuration}

### 设置优先级（从高到低） {#settings-hierarchy-highest-to-lowest-priority}
1. **CLI 标志** — 覆盖所有其他设置
2. **本地项目：** `.claude/settings.local.json`（个人配置，被 git 忽略）
3. **项目：** `.claude/settings.json`（共享配置，被 git 跟踪）
4. **用户：** `~/.claude/settings.json`（全局配置）
### 设置中的权限 {#permissions-in-settings}
```json
{
  "permissions": {
    "allow": ["Bash(npm run lint:*)", "WebSearch", "Read"],
    "ask": ["Write(*.ts)", "Bash(git push*)"],
    "deny": ["Read(.env)", "Bash(rm -rf *)"]
  }
}
```

### 记忆文件（CLAUDE.md）层级 {#memory-files-claude-md-hierarchy}
1. **全局：** `~/.claude/CLAUDE.md` — 适用于所有项目
2. **项目：** `./CLAUDE.md` — 项目特定上下文（由 Git 跟踪）
3. **本地：** `.claude/CLAUDE.local.md` — 个人项目覆盖（被 Git 忽略）

在交互模式下使用 `#` 前缀可快速添加到记忆：`# 始终使用 2 空格缩进`。

## 交互式会话：斜杠命令 {#interactive-session-slash-commands}

### 会话与上下文 {#session-context}
| 命令 | 用途 |
|---------|---------|
| `/help` | 显示所有命令（包括自定义命令和 MCP 命令） |
| `/compact [focus]` | 压缩上下文以节省 token；CLAUDE.md 在压缩后保留。例如：`/compact focus on auth logic` |
| `/clear` | 清除对话历史，重新开始 |
| `/context` | 以彩色网格形式可视化上下文使用情况，并附带优化建议 |
| `/cost` | 查看 token 用量，按模型和缓存命中细分 |
| `/resume` | 切换到或恢复另一个会话 |
| `/rewind` | 回退到对话或代码中的上一个检查点 |
| `/btw &lt;question&gt;` | 提出一个附带问题，不增加上下文成本 |
| `/status` | 显示版本、连接状态和会话信息 |
| `/todos` | 列出对话中跟踪的待办事项 |
| `/exit` 或 `Ctrl+D` | 结束会话 |

### 开发与审查 {#development-review}
| 命令 | 用途 |
|---------|---------|
| `/review` | 请求对当前更改进行代码审查 |
| `/security-review` | 对当前更改执行安全分析 |
| `/plan [description]` | 进入计划模式，自动启动任务规划 |
| `/loop [interval]` | 在会话内安排重复任务 |
| `/batch` | 为大型并行更改自动创建工作树（5-30 个工作树） |

### 配置与工具 {#configuration-tools}
| 命令 | 用途 |
|---------|---------|
| `/model [model]` | 在会话中切换模型（使用箭头键调整努力程度） |
| `/effort [level]` | 设置推理努力程度：`low`、`medium`、`high`、`max` 或 `auto` |
| `/init` | 创建项目记忆的 CLAUDE.md 文件 |
| `/memory` | 打开 CLAUDE.md 进行编辑 |
| `/config` | 打开交互式设置配置 |
| `/permissions` | 查看/更新工具权限 |
| `/agents` | 管理专门的子 Agents |
| `/mcp` | 管理 MCP 服务器的交互式 UI |
| `/add-dir` | 添加额外的工作目录（适用于 monorepo） |
| `/usage` | 显示计划限制和速率限制状态 |
| `/voice` | 启用即按即说语音模式（20 种语言；按住空格录制，松开发送） |
| `/release-notes` | 版本发布说明的交互式选择器 |

### 自定义斜杠命令 {#custom-slash-commands}
创建 `.claude/commands/&lt;name&gt;.md`（项目共享）或 `~/.claude/commands/&lt;name&gt;.md`（个人）：

```markdown
# .claude/commands/deploy.md
运行部署流水线：
1. 运行所有测试
2. 构建 Docker 镜像
3. 推送到镜像仓库
4. 更新 $ARGUMENTS 环境（默认：staging）
```
用法：`/deploy production` — `$ARGUMENTS` 会被替换为用户输入的内容。

### 技能（自然语言调用） {#skills-natural-language-invocation}
与需要手动调用的斜杠命令不同，`.claude/skills/` 中的技能是 Markdown 指南，当任务匹配时，Claude 会通过自然语言自动调用：

```markdown
# .claude/skills/database-migration.md
当被要求创建或修改数据库迁移时：
1. 使用 Alembic 生成迁移
2. 始终创建回滚函数
3. 在本地数据库副本上测试迁移
```

## 交互会话：键盘快捷键 {#interactive-session-keyboard-shortcuts}

### 通用控制 {#general-controls}
| 按键 | 操作 |
|-----|--------|
| `Ctrl+C` | 取消当前输入或生成 |
| `Ctrl+D` | 退出会话 |
| `Ctrl+R` | 反向搜索命令历史 |
| `Ctrl+B` | 将正在运行的任务放入后台 |
| `Ctrl+V` | 将图片粘贴到对话中 |
| `Ctrl+O` | 转录模式 — 查看 Claude 的思考过程 |
| `Ctrl+G` 或 `Ctrl+X Ctrl+E` | 在外部编辑器中打开提示 |
| `Esc Esc` | 回退对话或代码状态 / 总结 |

### 模式切换 {#mode-toggles}
| 按键 | 操作 |
|-----|--------|
| `Shift+Tab` | 循环切换权限模式（正常 → 自动接受 → 计划） |
| `Alt+P` | 切换模型 |
| `Alt+T` | 切换思考模式 |
| `Alt+O` | 切换快速模式 |

### 多行输入 {#multiline-input}
| 按键 | 操作 |
|-----|--------|
| `\` + `Enter` | 快速换行 |
| `Shift+Enter` | 换行（替代方式） |
| `Ctrl+J` | 换行（替代方式） |

### 输入前缀 {#input-prefixes}
| 前缀 | 操作 |
|--------|--------|
| `!` | 直接执行 bash，绕过 AI（例如 `!npm test`）。单独使用 `!` 可切换 shell 模式。 |
| `@` | 引用文件/目录，带自动补全（例如 `@./src/api/`） |
| `#` | 快速添加到 CLAUDE.md 记忆（例如 `# 使用 2 空格缩进`） |
| `/` | 斜杠命令 |

### 专业技巧："ultrathink" {#pro-tip-ultrathink}
在提示词中使用关键词 "ultrathink"，可在特定轮次获得最大推理努力。这会触发最深层的思考模式，无论当前的 `/effort` 设置如何。

## PR 审查模式 {#pr-review-pattern}

### 快速审查（打印模式） {#quick-review-print-mode}
```
terminal(command="cd /path/to/repo && git diff main...feature-branch | claude -p 'Review this diff for bugs, security issues, and style problems. Be thorough.' --max-turns 1", timeout=60)
```

### 深度审查（交互式 + 工作树） {#deep-review-interactive-worktree}
```
terminal(command="tmux new-session -d -s review -x 140 -y 40")
terminal(command="tmux send-keys -t review 'cd /path/to/repo && claude -w pr-review' Enter")
terminal(command="sleep 5 && tmux send-keys -t review Enter")  # 信任对话框
terminal(command="sleep 2 && tmux send-keys -t review 'Review all changes vs main. Check for bugs, security issues, race conditions, and missing tests.' Enter")
terminal(command="sleep 30 && tmux capture-pane -t review -p -S -60")
```

### 根据编号进行 PR 审查 {#pr-review-from-number}
```
terminal(command="claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10", workdir="/path/to/repo", timeout=120)
```

### 使用 tmux 的 Claude 工作树 {#claude-worktree-with-tmux}
```
terminal(command="claude -w feature-x --tmux", workdir="/path/to/repo")
```
在 `.claude/worktrees/feature-x` 创建一个隔离的 git 工作树，并为其创建一个 tmux 会话。如果可用，会使用 iTerm2 原生窗格；添加 `--tmux=classic` 可使用传统 tmux。
## 并行运行多个 Claude 实例 {#parallel-claude-instances}

同时运行多个独立的 Claude 任务：

```
# Task 1: Fix backend
terminal(command="tmux new-session -d -s task1 -x 140 -y 40 && tmux send-keys -t task1 'cd ~/project && claude -p \"Fix the auth bug in src/auth.py\" --allowedTools \"Read,Edit\" --max-turns 10' Enter")

# Task 2: Write tests
terminal(command="tmux new-session -d -s task2 -x 140 -y 40 && tmux send-keys -t task2 'cd ~/project && claude -p \"Write integration tests for the API endpoints\" --allowedTools \"Read,Write,Bash\" --max-turns 15' Enter")

# Task 3: Update docs
terminal(command="tmux new-session -d -s task3 -x 140 -y 40 && tmux send-keys -t task3 'cd ~/project && claude -p \"Update README.md with the new API endpoints\" --allowedTools \"Read,Edit\" --max-turns 5' Enter")

# Monitor all
terminal(command="sleep 30 && for s in task1 task2 task3; do echo '=== '$s' ==='; tmux capture-pane -t $s -p -S -5 2>/dev/null; done")
```

## CLAUDE.md — 项目上下文文件 {#claude-md-project-context-file}

Claude Code 会自动从项目根目录加载 `CLAUDE.md`。用它来持久化项目上下文：

```markdown
# Project: My API

## Architecture
- FastAPI backend with SQLAlchemy ORM
- PostgreSQL database, Redis cache
- pytest for testing with 90% coverage target

## Key Commands
- `make test` — run full test suite
- `make lint` — ruff + mypy
- `make dev` — start dev server on :8000

## Code Standards
- Type hints on all public functions
- Docstrings in Google style
- 2-space indentation for YAML, 4-space for Python
- No wildcard imports
```

**要具体。** 不要写“写好代码”，而要用“JS 使用 2 空格缩进”或“测试文件以 `.test.ts` 后缀命名”。具体的指令能减少修正次数。

### 规则目录（模块化 CLAUDE.md） {#rules-directory-modular-claude-md}
对于规则较多的项目，使用规则目录代替一个庞大的 CLAUDE.md：
- **项目规则：** `.claude/rules/*.md` — 团队共享，受 Git 追踪
- **用户规则：** `~/.claude/rules/*.md` — 个人全局规则

规则目录中的每个 `.md` 文件都会作为额外上下文加载。这比把所有内容塞进一个 CLAUDE.md 更清晰。

### 自动记忆 {#auto-memory}
Claude 会自动将学到的项目上下文存储在 `~/.claude/projects/&lt;project&gt;/memory/` 中。
- **限制：** 每个项目 25KB 或 200 行
- 这与 CLAUDE.md 是分开的——它是 Claude 自己关于项目的笔记，跨会话累积

## 自定义子 Agent（Subagents） {#custom-subagents}

在 `.claude/agents/`（项目级）、`~/.claude/agents/`（个人级）或通过 `--agents` CLI 标志（会话级）定义专用 Agent：

### Agent 位置优先级 {#agent-location-priority}
1. `.claude/agents/` — 项目级，团队共享
2. `--agents` CLI 标志 — 会话级，动态
3. `~/.claude/agents/` — 用户级，个人

### 创建 Agent {#creating-an-agent}
```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Security-focused code review
model: opus
tools: [Read, Bash]
---
You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication/authorization flaws
- Secrets in code
- Unsafe deserialization
```
通过 `@security-reviewer review the auth module` 调用

### 通过 CLI 使用动态 Agent {#dynamic-agents-via-cli}
```
terminal(command="claude --agents '{\"reviewer\": {\"description\": \"Reviews code\", \"prompt\": \"You are a code reviewer focused on performance\"}}' -p 'Use @reviewer to check auth.py'", timeout=120)
```

Claude 可以编排多个 Agent："Use @db-expert to optimize queries, then @security to audit the changes."

## Hooks — 事件自动化 {#hooks-automation-on-events}

在 `.claude/settings.json`（项目级）或 `~/.claude/settings.json`（全局）中配置：

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{"type": "command", "command": "ruff check --fix $CLAUDE_FILE_PATHS"}]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -q 'rm -rf'; then echo 'Blocked!' && exit 2; fi"}]
    }],
    "Stop": [{
      "hooks": [{"type": "command", "command": "echo 'Claude finished a response' >> /tmp/claude-activity.log"}]
    }]
  }
}
```

### 全部 8 种 Hook 类型 {#all-8-hook-types}
| Hook | 触发时机 | 常见用途 |
|------|----------|----------|
| `UserPromptSubmit` | Claude 处理用户提示之前 | 输入验证、日志记录 |
| `PreToolUse` | 工具执行之前 | 安全门控，阻止危险命令（exit 2 = 阻止） |
| `PostToolUse` | 工具执行完成后 | 自动格式化代码、运行 linter |
| `Notification` | 权限请求或输入等待时 | 桌面通知、警报 |
| `Stop` | Claude 完成响应时 | 完成日志记录、状态更新 |
| `SubagentStop` | 子 Agent 完成时 | Agent 编排 |
| `PreCompact` | 上下文内存被清除前 | 备份会话记录 |
| `SessionStart` | 会话开始时 | 加载开发上下文（例如 `git status`） |

### Hook 环境变量 {#hook-environment-variables}
| 变量 | 内容 |
|------|------|
| `CLAUDE_PROJECT_DIR` | 当前项目路径 |
| `CLAUDE_FILE_PATHS` | 正在修改的文件 |
| `CLAUDE_TOOL_INPUT` | 工具参数（JSON 格式） |

### 安全 Hook 示例 {#security-hook-examples}
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|git push.*--force|:(){ :|:& };:'; then echo 'Dangerous command blocked!' && exit 2; fi"}]
  }]
}
```

## MCP 集成 {#mcp-integration}

为数据库、API 和服务添加外部工具服务器：

```
# GitHub 集成
terminal(command="claude mcp add -s user github -- npx @modelcontextprotocol/server-github", timeout=30)

# PostgreSQL 查询
terminal(command="claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres --connection-string postgresql://localhost/mydb", timeout=30)

# Puppeteer 用于 Web 测试
terminal(command="claude mcp add puppeteer -- npx @anthropic-ai/server-puppeteer", timeout=30)
```

### MCP 作用域 {#mcp-scopes}
| 标志 | 作用域 | 存储位置 |
|------|--------|----------|
| `-s user` | 全局（所有项目） | `~/.claude.json` |
| `-s local` | 当前项目（个人） | `.claude/settings.local.json`（被 gitignore） |
| `-s project` | 当前项目（团队共享） | `.claude/settings.json`（被 git 跟踪） |
### MCP 打印/CI 模式 {#mcp-in-print-ci-mode}
```
terminal(command="claude --bare -p 'Query database' --mcp-config mcp-servers.json --strict-mcp-config", timeout=60)
```
`--strict-mcp-config` 会忽略除 `--mcp-config` 指定的 MCP 服务器之外的所有服务器。

在聊天中引用 MCP 资源：`@github:issue://123`

### MCP 限制与调优 {#mcp-limits-tuning}
- **工具描述：** 每个服务器的工具描述和服务器指令上限为 2KB
- **结果大小：** 默认有上限；使用 `maxResultSizeChars` 注解可允许大型输出达到 **500K** 字符
- **输出 token：** `export MAX_MCP_OUTPUT_TOKENS=50000` — 限制 MCP 服务器的输出，防止上下文溢出
- **传输方式：** `stdio`（本地进程）、`http`（远程）、`sse`（服务器推送事件）

## 监控交互式会话 {#monitoring-interactive-sessions}

### 读取 TUI 状态 {#reading-the-tui-status}
```
# 定期捕获，检查 Claude 是否仍在工作或等待输入
terminal(command="tmux capture-pane -t dev -p -S -10")
```

查看以下指示：
- 底部的 `❯` = 等待你的输入（Claude 已完成或正在提问）
- `●` 行 = Claude 正在积极使用工具（读取、写入、运行命令）
- `⏵⏵ bypass permissions on` = 状态栏显示权限模式
- `◐ medium · /effort` = 状态栏中的当前努力级别
- `ctrl+o to expand` = 工具输出被截断（可交互展开）

### 上下文窗口健康度 {#context-window-health}
在交互模式下使用 `/context` 查看上下文使用情况的彩色网格。关键阈值：
- **&lt; 70%** — 正常运行，全精度
- **70-85%** — 精度开始下降，考虑使用 `/compact`
- **> 85%** — 幻觉风险显著增加，使用 `/compact` 或 `/clear`

## 环境变量 {#environment-variables}

| 变量 | 作用 |
|----------|--------|
| `ANTHROPIC_API_KEY` | 用于身份验证的 API 密钥（OAuth 的替代方案） |
| `CLAUDE_CODE_EFFORT_LEVEL` | 默认努力级别：`low`、`medium`、`high`、`max` 或 `auto` |
| `MAX_THINKING_TOKENS` | 限制思考 token（设为 `0` 可完全禁用思考） |
| `MAX_MCP_OUTPUT_TOKENS` | 限制 MCP 服务器的输出（默认值因情况而异；例如设为 `50000`） |
| `CLAUDE_CODE_NO_FLICKER=1` | 启用备用屏幕渲染以消除终端闪烁 |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | 从子进程中清除凭据以增强安全性 |

## 成本与性能提示 {#cost-performance-tips}

1. **在打印模式下使用 `--max-turns`** 防止无限循环。大多数任务从 5-10 开始。
2. **使用 `--max-budget-usd`** 设置成本上限。注意：系统提示缓存创建最低约 $0.05。
3. **简单任务使用 `--effort low`**（更快、更便宜）。复杂推理使用 `high` 或 `max`。
4. **CI/脚本使用 `--bare`** 跳过插件/钩子发现的开销。
5. **使用 `--allowedTools`** 限制仅使用所需工具（例如，仅 `Read` 用于审查）。
6. **交互式会话中上下文变大时使用 `/compact`**。
7. **当只需要分析已知内容时，通过管道输入**，而不是让 Claude 读取文件。
8. **简单任务使用 `--model haiku`**（更便宜），复杂多步骤工作使用 `--model opus`。
9. **在打印模式下使用 `--fallback-model haiku`** 优雅处理模型过载。
10. **为不同任务启动新会话** — 会话持续 5 小时；新上下文更高效。
11. **CI 中使用 `--no-session-persistence`** 避免在磁盘上累积保存的会话。
## 陷阱与注意事项 {#pitfalls-gotchas}

1. **交互模式必须使用 tmux** — Claude Code 是一个完整的 TUI 应用。在 Hermes 终端中单独使用 `pty=true` 也能工作，但 tmux 提供了 `capture-pane` 用于监控和 `send-keys` 用于输入，这对编排至关重要。
2. **`--dangerously-skip-permissions` 对话框默认选择“否，退出”** — 你必须发送 Down 然后 Enter 来接受。打印模式（`-p`）完全跳过这一步。
3. **`--max-budget-usd` 最小值约为 $0.05** — 仅系统提示缓存创建就需要这么多。设置更低会立即报错。
4. **`--max-turns` 仅适用于打印模式** — 在交互会话中被忽略。
5. **Claude 可能使用 `python` 而不是 `python3`** — 在没有 `python` 符号链接的系统上，Claude 的 bash 命令首次会失败，但会自动修正。
6. **恢复会话需要相同目录** — `--continue` 会查找当前工作目录最近的会话。
7. **`--json-schema` 需要足够的 `--max-turns`** — Claude 在生成结构化输出前必须读取文件，这需要多个回合。
8. **信任对话框每个目录只出现一次** — 仅首次出现，之后会缓存。
9. **后台 tmux 会话会持续存在** — 完成后务必使用 `tmux kill-session -t <名称>` 清理。
10. **斜杠命令（如 `/commit`）仅在交互模式下工作** — 在 `-p` 模式下，改用自然语言描述任务。
11. **`--bare` 跳过 OAuth** — 需要 `ANTHROPIC_API_KEY` 环境变量或设置中的 `apiKeyHelper`。
12. **上下文退化是真实存在的** — 当上下文窗口使用率超过 70% 时，AI 输出质量会明显下降。使用 `/context` 监控并主动使用 `/compact`。

## Hermes Agent 规则 {#rules-for-hermes-agents}

1. **单次任务优先使用打印模式（`-p`）** — 更干净，无需处理对话框，输出结构化
2. **多轮交互工作使用 tmux** — 编排 TUI 的唯一可靠方式
3. **始终设置 `workdir`** — 让 Claude 专注于正确的项目目录
4. **在打印模式下设置 `--max-turns`** — 防止无限循环和失控成本
5. **监控 tmux 会话** — 使用 `tmux capture-pane -t <会话> -p -S -50` 检查进度
6. **寻找 `❯` 提示符** — 表示 Claude 正在等待输入（已完成或正在提问）
7. **清理 tmux 会话** — 完成后终止它们以避免资源泄漏
8. **向用户报告结果** — 完成后，总结 Claude 做了什么以及发生了什么变化
9. **不要终止慢速会话** — Claude 可能正在进行多步工作；改为检查进度
10. **使用 `--allowedTools`** — 将能力限制在任务实际需要的范围内
