---
title: "Claude Code — 将编码任务委托给 Claude Code CLI（功能、PR）"
sidebar_label: "Claude Code"
description: "将编码任务委托给 Claude Code CLI（功能、PR）"
---

{/* 本页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="claude-code"></a>
# Claude Code

将编码任务委托给 Claude Code CLI（功能、PR）。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/autonomous-ai-agents/claude-code` |
| 版本 | `2.2.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Coding-Agent`, `Claude`, `Anthropic`, `Code-Review`, `Refactoring`, `PTY`, `Automation` |
| 相关技能 | [`codex`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent), [`opencode`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-opencode) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下为 Hermes 在触发该技能时加载的完整技能定义。技能激活时，Agent 会将这些内容作为指令。
:::

<a id="claude-code-hermes-orchestration-guide"></a>
# Claude Code — Hermes 编排指南

通过 Hermes 终端将编码任务委托给 [Claude Code](https://code.claude.com/docs/en/cli-reference)（Anthropic 的自主编码 Agent CLI）。Claude Code v2.x 能够自主读取文件、编写代码、运行 shell 命令、生成子 Agent 以及管理 git 工作流程。

<a id="prerequisites"></a>
## 前提条件

- **安装：** `npm install -g @anthropic-ai/claude-code`
- **认证：** 运行 `claude` 一次以登录（Pro/Max 用户使用浏览器 OAuth，或设置 `ANTHROPIC_API_KEY`）
- **控制台认证：** `claude auth login --console` （使用 API key 计费）
- **SSO 认证：** `claude auth login --sso` （企业用户）
- **检查状态：** `claude auth status`（JSON 格式）或 `claude auth status --text`（人类可读格式）
- **健康检查：** `claude doctor` —— 检查自动更新器和安装健康情况
- **版本检查：** `claude --version`（需要 v2.x 或更高版本）
- **更新：** `claude update` 或 `claude upgrade`

<a id="two-orchestration-modes"></a>
## 两种编排模式

Hermes 以两种截然不同的方式与 Claude Code 交互。请根据任务选择合适的模式。

<a id="mode-1-print-mode-p-non-interactive-preferred-for-most-tasks"></a>
### 模式 1：打印模式（`-p`）—— 非交互（大多数任务的首选）

打印模式一次性执行任务，返回结果后退出。无需 PTY，无交互式提示。这是最干净的集成路径。

```
terminal(command="claude -p '为 src/ 中所有 API 调用添加错误处理' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**何时使用打印模式：**
- 一次性编码任务（修复 Bug、添加功能、重构）
- CI/CD 自动化和脚本编写
- 使用 `--json-schema` 进行结构化数据提取
- 管道输入处理（`cat file | claude -p "分析这个"`）
- 任何不需要多轮对话的任务

**打印模式会跳过所有交互式对话框** —— 不会出现工作区信任提示，也不会有权限确认。这使其非常适合自动化。

<a id="mode-2-interactive-pty-via-tmux-multi-turn-sessions"></a>
### 模式 2：通过 tmux 的交互式 PTY —— 多轮会话

交互模式提供一个完整的对话式 REPL，可以发送后续提示、使用斜杠命令，并实时观察 Claude 的工作。**需要 tmux 编排。**
```
# 启动一个 tmux 会话
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")

# 在会话中启动 Claude Code
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")

# 等待启动完成，然后发送你的任务
# （大约 3-5 秒后出现欢迎界面）
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Refactor the auth module to use JWT tokens' Enter")

# 通过捕获面板内容监控进度
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")

# 发送后续任务
terminal(command="tmux send-keys -t claude-work 'Now add unit tests for the new JWT code' Enter")

# 完成后退出
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

**何时使用交互模式：**
- 需要多轮迭代的工作（重构 → 审查 → 修复 → 测试循环）
- 需要人类参与决策的任务
- 探索性编码会话
- 当需要使用 Claude 的斜杠命令（`/compact`、`/review`、`/model`）

<a id="pty-dialog-handling-critical-for-interactive-mode"></a>
## PTY 对话框处理（交互模式关键）

Claude Code 在首次启动时最多会出现两个确认对话框。你必须通过 tmux send-keys 处理它们：

<a id="dialog-1-workspace-trust-first-visit-to-a-directory"></a>
### 对话框 1：工作区信任（首次访问目录）
```
❯ 1. 是，我信任此文件夹    ← 默认选项（直接按 Enter）
  2. 否，退出
```
**处理：** `tmux send-keys -t &lt;session&gt; Enter` — 默认选择是正确的。

<a id="dialog-2-bypass-permissions-warning-only-with-dangerously-skip-permissions"></a>
### 对话框 2：绕过权限警告（仅在使用 `--dangerously-skip-permissions` 时出现）
```
❯ 1. 否，退出                    ← 默认选项（错误的选择！）
  2. 是，我接受
```
**处理：** 必须先向下导航，然后按 Enter：
```
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

<a id="robust-dialog-handling-pattern"></a>
### 健壮的对话框处理模式
```
# 启动并跳过权限确认
terminal(command="tmux send-keys -t claude-work 'claude --dangerously-skip-permissions \"your task\"' Enter")

# 处理信任对话框（Enter 选择默认的“是”）
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")

# 处理权限对话框（先下移再 Enter 选择“是，我接受”）
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")

# 等待 Claude 开始工作
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -60")
```

**注意：** 一旦某个目录的信任被接受，信任对话框不会再次出现。只有权限对话框会在每次使用 `--dangerously-skip-permissions` 时重复出现。

<a id="cli-subcommands"></a>
## CLI 子命令

| 子命令 | 用途 |
|--------|------|
| `claude` | 启动交互式 REPL |
| `claude "query"` | 使用初始提示启动 REPL |
| `claude -p "query"` | 打印模式（非交互式，完成后退出） |
| `cat file \| claude -p "query"` | 将管道内容作为 stdin 上下文传递 |
| `claude -c` | 继续当前目录中最近的对话 |
| `claude -r "id"` | 按 ID 或名称恢复特定会话 |
| `claude auth login` | 登录（添加 `--console` 用于 API 计费，`--sso` 用于企业版） |
| `claude auth status` | 检查登录状态（返回 JSON；`--text` 可读格式） |
| `claude mcp add &lt;name&gt; -- &lt;cmd&gt;` | 添加一个 MCP 服务器 |
| `claude mcp list` | 列出已配置的 MCP 服务器 |
| `claude mcp remove &lt;name&gt;` | 移除一个 MCP 服务器 |
| `claude agents` | 列出已配置的 Agent |
| `claude doctor` | 对安装和自动更新程序运行健康检查 |
| `claude update` / `claude upgrade` | 将 Claude Code 更新到最新版本 |
| `claude remote-control` | 启动服务器以便从 claude.ai 或移动应用控制 Claude |
| `claude install [target]` | 安装原生构建（稳定版、最新版或特定版本） |
| `claude setup-token` | 设置长期有效的认证令牌（需要订阅） |
| `claude plugin` / `claude plugins` | 管理 Claude Code 插件 |
| `claude auto-mode` | 检查自动模式分类器配置 |
<a id="print-mode-deep-dive"></a>
## 打印模式深入解析

<a id="structured-json-output"></a>
### 结构化 JSON 输出
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

**关键字段：** `session_id` 用于恢复会话，`num_turns` 表示 Agent 循环次数，`total_cost_usd` 用于费用追踪，`subtype` 用于成功/错误检测（`success`、`error_max_turns`、`error_budget`）。

<a id="streaming-json-output"></a>
### 流式 JSON 输出
如需实时 token 流式输出，请使用 `stream-json` 配合 `--verbose`：
```
terminal(command="claude -p 'Write a summary' --output-format stream-json --verbose --include-partial-messages", timeout=60)
```

返回以换行符分隔的 JSON 事件。使用 jq 过滤实时文本：
```
claude -p "Explain X" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

流事件包含 `system/api_retry`，其中带有 `attempt`、`max_retries` 和 `error` 字段（例如 `rate_limit`、`billing_error`）。

<a id="bidirectional-streaming"></a>
### 双向流式传输
用于实时输入和输出流式传输：
```
claude -p "task" --input-format stream-json --output-format stream-json --replay-user-messages
```
`--replay-user-messages` 会在标准输出上重新输出用户消息以进行确认。

<a id="piped-input"></a>
### 管道输入
```
# 通过管道传入文件进行分析
terminal(command="cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1", timeout=60)

# 通过管道传入多个文件
terminal(command="cat src/*.py | claude -p 'Find all TODO comments' --max-turns 1", timeout=60)

# 通过管道传入命令输出
terminal(command="git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1", timeout=60)
```

<a id="json-schema-for-structured-extraction"></a>
### 用于结构化提取的 JSON Schema
```
terminal(command="claude -p 'List all functions in src/' --output-format json --json-schema '{\"type\":\"object\",\"properties\":{\"functions\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}},\"required\":[\"functions\"]}' --max-turns 5", workdir="/project", timeout=90)
```

从 JSON 结果中解析 `structured_output`。Claude 在返回结果前会根据 schema 验证输出。

<a id="session-continuation"></a>
### 会话延续
```
# 启动一个任务
terminal(command="claude -p 'Start refactoring the database layer' --output-format json --max-turns 10 > /tmp/session.json", workdir="/project", timeout=180)

# 使用会话 ID 恢复
terminal(command="claude -p 'Continue and add connection pooling' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"session_id\"])') --max-turns 5", workdir="/project", timeout=120)

# 或者恢复同一目录下最近的会话
terminal(command="claude -p 'What did you do last time?' --continue --max-turns 1", workdir="/project", timeout=30)

# 分叉会话（新 ID，保留历史记录）
terminal(command="claude -p 'Try a different approach' --resume <id> --fork-session --max-turns 10", workdir="/project", timeout=120)
```
<a id="bare-mode-for-ci-scripting"></a>
### CI/脚本场景下的 Bare 模式
```
terminal(command="claude --bare -p 'Run all tests and report failures' --allowedTools 'Read,Bash' --max-turns 10", workdir="/project", timeout=180)
```

`--bare` 会跳过钩子、插件、MCP 发现以及 CLAUDE.md 的加载。启动最快。需要设置 `ANTHROPIC_API_KEY`（跳过 OAuth）。

如果想在 bare 模式下选择性加载上下文：

| 加载内容 | 参数 |
|---------|------|
| 系统提示补充 | `--append-system-prompt "text"` 或 `--append-system-prompt-file path` |
| 设置 | `--settings &lt;file-or-json&gt;` |
| MCP 服务器 | `--mcp-config &lt;file-or-json&gt;` |
| 自定义 Agents | `--agents '&lt;json&gt;'` |

<a id="fallback-model-for-overload"></a>
### 过载时的回退模型
```
terminal(command="claude -p 'task' --fallback-model haiku --max-turns 5", timeout=90)
```
当默认模型过载时，自动回退到指定的模型（仅 print 模式）。

<a id="complete-cli-flags-reference"></a>
## 完整 CLI 参数参考

<a id="session-environment"></a>
### 会话与环境
| 参数 | 作用 |
|------|--------|
| `-p, --print` | 非交互式一次性模式（完成后退出） |
| `-c, --continue` | 恢复当前目录中最新的对话 |
| `-r, --resume &lt;id&gt;` | 按 ID 或名称恢复指定会话（未提供 ID 时弹出交互选择器） |
| `--fork-session` | 恢复时创建新会话 ID，而不是复用原始 ID |
| `--session-id &lt;uuid&gt;` | 为对话使用特定的 UUID |
| `--no-session-persistence` | 不将会话保存到磁盘（仅 print 模式） |
| `--add-dir &lt;paths...&gt;` | 授权 Claude 访问额外的工作目录 |
| `-w, --worktree [name]` | 在 `.claude/worktrees/&lt;name&gt;` 的隔离 git 工作树中运行 |
| `--tmux` | 为工作树创建一个 tmux 会话（需要 `--worktree`） |
| `--ide` | 启动时自动连接有效 IDE |
| `--chrome` / `--no-chrome` | 启用/禁用 Chrome 浏览器集成进行 Web 测试 |
| `--from-pr [number]` | 恢复与特定 GitHub PR 关联的会话 |
| `--file &lt;specs...&gt;` | 启动时下载的文件资源（格式：`file_id:relative_path`） |

<a id="model-performance"></a>
### 模型与性能
| 参数 | 作用 |
|------|--------|
| `--model &lt;alias&gt;` | 模型选择：`sonnet`、`opus`、`haiku`，或完整名称如 `claude-sonnet-4-6` |
| `--effort &lt;level&gt;` | 推理深度：`low`、`medium`、`high`、`max`、`auto` |
| `--max-turns &lt;n&gt;` | 限制 agentic loops（仅 print 模式，防止失控） |
| `--max-budget-usd &lt;n&gt;` | 按美元限制 API 花费上限（仅 print 模式） |
| `--fallback-model &lt;model&gt;` | 默认模型过载时自动回退（仅 print 模式） |
| `--betas &lt;betas...&gt;` | 包含在 API 请求中的 Beta 标头（仅 API 密钥用户） |

<a id="permission-safety"></a>
### 权限与安全
| 参数 | 作用 |
|------|--------|
| `--dangerously-skip-permissions` | 自动批准所有工具使用（文件写入、bash、网络等） |
| `--allow-dangerously-skip-permissions` | 将绕过权限作为*选项*启用，而非默认启用 |
| `--permission-mode &lt;mode&gt;` | `default`、`acceptEdits`、`plan`、`auto`、`dontAsk`、`bypassPermissions` |
| `--allowedTools &lt;tools...&gt;` | 白名单特定工具（逗号或空格分隔） |
| `--disallowedTools &lt;tools...&gt;` | 黑名单特定工具 |
| `--tools &lt;tools...&gt;` | 覆盖内置工具集（`""` = 无，`"default"` = 全部，或工具名称） |
<a id="output-input-format"></a>
### 输出与输入格式
| 标志 | 作用 |
|------|--------|
| `--output-format &lt;fmt&gt;` | `text`（默认）、`json`（单个结果对象）、`stream-json`（换行分隔） |
| `--input-format &lt;fmt&gt;` | `text`（默认）或 `stream-json`（实时流式输入） |
| `--json-schema &lt;schema&gt;` | 强制输出符合指定 schema 的结构化 JSON |
| `--verbose` | 完整输出每一步的交互内容 |
| `--include-partial-messages` | 包含到达时的部分消息块（stream-json + 打印） |
| `--replay-user-messages` | 在标准输出中重新输出用户消息（双向 stream-json） |

<a id="system-prompt-context"></a>
### 系统提示与上下文
| 标志 | 作用 |
|------|--------|
| `--append-system-prompt &lt;text&gt;` | **追加**到默认系统提示（保留内置能力） |
| `--append-system-prompt-file &lt;path&gt;` | **追加**文件内容到默认系统提示 |
| `--system-prompt &lt;text&gt;` | **替换**整个系统提示（通常建议用 --append） |
| `--system-prompt-file &lt;path&gt;` | **用文件内容替换**系统提示 |
| `--bare` | 跳过钩子、插件、MCP 发现、CLAUDE.md、OAuth（启动最快） |
| `--agents '&lt;json&gt;'` | 动态定义自定义子 Agents（JSON 格式） |
| `--mcp-config &lt;path&gt;` | 从 JSON 文件加载 MCP 服务器（可重复） |
| `--strict-mcp-config` | 仅使用 `--mcp-config` 中的 MCP 服务器，忽略所有其他 MCP 配置 |
| `--settings &lt;file-or-json&gt;` | 从 JSON 文件或内联 JSON 加载额外设置 |
| `--setting-sources &lt;sources&gt;` | 用逗号分隔要加载的来源：`user`、`project`、`local` |
| `--plugin-dir &lt;paths...&gt;` | 仅对本次会话从指定目录加载插件 |
| `--disable-slash-commands` | 禁用所有技能/斜杠命令 |

<a id="debugging"></a>
### 调试
| 标志 | 作用 |
|------|--------|
| `-d, --debug [filter]` | 启用调试日志，可选用类别过滤（例如 `"api,hooks"`、`"!1p,!file"`） |
| `--debug-file &lt;path&gt;` | 将调试日志写入文件（隐式启用调试模式） |

<a id="agent-teams"></a>
### Agent 团队
| 标志 | 作用 |
|------|--------|
| `--teammate-mode &lt;mode&gt;` | 设置 Agent 团队显示模式：`auto`、`in-process` 或 `tmux` |
| `--brief` | 启用 `SendUserMessage` 工具，用于 Agent 与用户之间的通信 |

<a id="tool-name-syntax-for-allowedtools-disallowedtools"></a>
### --allowedTools / --disallowedTools 的工具名语法
```
Read                    # 所有文件读取
Edit                    # 文件编辑（已有文件）
Write                   # 文件创建（新建文件）
Bash                    # 所有 shell 命令
Bash(git *)             # 仅 git 命令
Bash(git commit *)      # 仅 git commit 命令
Bash(npm run lint:*)    # 通配符模式匹配
WebSearch               # 网页搜索能力
WebFetch                # 网页抓取能力
mcp__<server>__<tool>   # 指定 MCP 工具
```

<a id="settings-configuration"></a>
## 设置与配置

<a id="settings-hierarchy-highest-to-lowest-priority"></a>
### 设置优先级（从高到低）
1. **CLI 标志** — 覆盖所有设置
2. **本地项目：** `.claude/settings.local.json`（个人配置，已加入 .gitignore）
3. **项目：** `.claude/settings.json`（共享配置，受 Git 跟踪）
4. **用户：** `~/.claude/settings.json`（全局配置）
<a id="permissions-in-settings"></a>
### 设置中的权限
```json
{
  "permissions": {
    "allow": ["Bash(npm run lint:*)", "WebSearch", "Read"],
    "ask": ["Write(*.ts)", "Bash(git push*)"],
    "deny": ["Read(.env)", "Bash(rm -rf *)"]
  }
}
```

<a id="memory-files-claude-md-hierarchy"></a>
### 记忆文件（CLAUDE.md）层级
1. **全局：** `~/.claude/CLAUDE.md` — 适用于所有项目
2. **项目：** `./CLAUDE.md` — 项目专属上下文（git 跟踪）
3. **本地：** `.claude/CLAUDE.local.md` — 个人项目覆盖（git 忽略）

在交互模式下使用 `#` 前缀可快速添加记忆：`#始终使用 2 空格缩进`。

<a id="interactive-session-slash-commands"></a>
## 交互式会话：斜杠命令

<a id="session-context"></a>
### 会话与上下文
| 命令 | 用途 |
|---------|---------|
| `/help` | 显示所有命令（包括自定义和 MCP 命令） |
| `/compact [focus]` | 压缩上下文以节省 token；CLAUDE.md 在压缩后保留。例如：`/compact focus on auth logic` |
| `/clear` | 清空对话历史，重新开始 |
| `/context` | 以彩色网格形式可视化上下文使用情况，并附带优化建议 |
| `/cost` | 查看 token 使用量，按模型和缓存命中细分 |
| `/resume` | 切换或恢复另一个会话 |
| `/rewind` | 回退到对话或代码中的上一个检查点 |
| `/btw &lt;question&gt;` | 提出一个附带问题，不增加上下文成本 |
| `/status` | 显示版本、连接和会话信息 |
| `/todos` | 列出对话中跟踪的待办事项 |
| `/exit` 或 `Ctrl+D` | 结束会话 |

<a id="development-review"></a>
### 开发与审查
| 命令 | 用途 |
|---------|---------|
| `/review` | 请求对当前更改进行代码审查 |
| `/security-review` | 对当前更改执行安全分析 |
| `/plan [description]` | 进入计划模式，自动启动任务规划 |
| `/loop [interval]` | 在会话中安排重复任务 |
| `/batch` | 为大型并行更改自动创建工作树（5-30 个工作树） |

<a id="configuration-tools"></a>
### 配置与工具
| 命令 | 用途 |
|---------|---------|
| `/model [model]` | 在会话中切换模型（使用方向键调整努力程度） |
| `/effort [level]` | 设置推理努力程度：`low`、`medium`、`high`、`max` 或 `auto` |
| `/init` | 为项目记忆创建 CLAUDE.md 文件 |
| `/memory` | 打开 CLAUDE.md 进行编辑 |
| `/config` | 打开交互式设置配置 |
| `/permissions` | 查看/更新工具权限 |
| `/agents` | 管理专门的子 Agent |
| `/mcp` | 交互式 UI 管理 MCP 服务器 |
| `/add-dir` | 添加额外的工作目录（适用于 monorepo） |
| `/usage` | 显示计划限制和速率限制状态 |
| `/voice` | 启用一键通话语音模式（20 种语言；按住空格录音，松开发送） |
| `/release-notes` | 交互式版本发布说明选择器 |

<a id="custom-slash-commands"></a>
### 自定义斜杠命令
创建 `.claude/commands/&lt;name&gt;.md`（项目共享）或 `~/.claude/commands/&lt;name&gt;.md`（个人）：

```markdown
# .claude/commands/deploy.md
Run the deploy pipeline:
1. Run all tests
2. Build the Docker image
3. Push to registry
4. Update the $ARGUMENTS environment (default: staging)
```
用法：`/deploy production` — `$ARGUMENTS` 会被替换为用户输入。

<a id="skills-natural-language-invocation"></a>
### 技能（自然语言调用）
与手动调用的斜杠命令不同，`.claude/skills/` 中的技能是 Markdown 指南，当任务匹配时，Claude 会通过自然语言自动调用：

```markdown
# .claude/skills/database-migration.md
当被要求创建或修改数据库迁移时：
1. 使用 Alembic 生成迁移
2. 始终创建回滚函数
3. 在本地数据库副本上测试迁移
```

<a id="interactive-session-keyboard-shortcuts"></a>
## 交互会话：键盘快捷键

<a id="general-controls"></a>
### 通用控制
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

<a id="mode-toggles"></a>
### 模式切换
| 按键 | 操作 |
|-----|--------|
| `Shift+Tab` | 循环切换权限模式（正常 → 自动接受 → 计划） |
| `Alt+P` | 切换模型 |
| `Alt+T` | 切换思考模式 |
| `Alt+O` | 切换快速模式 |

<a id="multiline-input"></a>
### 多行输入
| 按键 | 操作 |
|-----|--------|
| `\` + `Enter` | 快速换行 |
| `Shift+Enter` | 换行（备选） |
| `Ctrl+J` | 换行（备选） |

<a id="input-prefixes"></a>
### 输入前缀
| 前缀 | 操作 |
|--------|--------|
| `!` | 直接执行 bash，绕过 AI（例如 `!npm test`）。单独使用 `!` 可切换 shell 模式。 |
| `@` | 引用文件/目录，支持自动补全（例如 `@./src/api/`） |
| `#` | 快速添加到 CLAUDE.md 记忆（例如 `# 使用 2 空格缩进`） |
| `/` | 斜杠命令 |

<a id="pro-tip-ultrathink"></a>
### 专业技巧："ultrathink"
在提示中使用关键词 "ultrathink"，可在特定轮次中启用最大推理能力。无论当前 `/effort` 设置如何，这都会触发最深度的思考模式。

<a id="pr-review-pattern"></a>
## PR 审查模式

<a id="quick-review-print-mode"></a>
### 快速审查（打印模式）
```
terminal(command="cd /path/to/repo && git diff main...feature-branch | claude -p 'Review this diff for bugs, security issues, and style problems. Be thorough.' --max-turns 1", timeout=60)
```

<a id="deep-review-interactive-worktree"></a>
### 深度审查（交互式 + 工作树）
```
terminal(command="tmux new-session -d -s review -x 140 -y 40")
terminal(command="tmux send-keys -t review 'cd /path/to/repo && claude -w pr-review' Enter")
terminal(command="sleep 5 && tmux send-keys -t review Enter")  # 信任对话框
terminal(command="sleep 2 && tmux send-keys -t review 'Review all changes vs main. Check for bugs, security issues, race conditions, and missing tests.' Enter")
terminal(command="sleep 30 && tmux capture-pane -t review -p -S -60")
```

<a id="pr-review-from-number"></a>
### 通过编号审查 PR
```
terminal(command="claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10", workdir="/path/to/repo", timeout=120)
```

<a id="claude-worktree-with-tmux"></a>
### 使用 tmux 的 Claude 工作树
```
terminal(command="claude -w feature-x --tmux", workdir="/path/to/repo")
```
创建一个隔离的 git 工作树，位于 `.claude/worktrees/feature-x`，并为其创建一个 tmux 会话。可用时使用 iTerm2 原生窗格；添加 `--tmux=classic` 可使用传统 tmux。
<a id="parallel-claude-instances"></a>
## 并行 Claude 实例

同时运行多个独立的 Claude 任务：

```
# 任务 1：修复后端
terminal(command="tmux new-session -d -s task1 -x 140 -y 40 && tmux send-keys -t task1 'cd ~/project && claude -p \"修复 src/auth.py 中的认证 bug\" --allowedTools \"Read,Edit\" --max-turns 10' Enter")

# 任务 2：编写测试
terminal(command="tmux new-session -d -s task2 -x 140 -y 40 && tmux send-keys -t task2 'cd ~/project && claude -p \"为 API 端点编写集成测试\" --allowedTools \"Read,Write,Bash\" --max-turns 15' Enter")

# 任务 3：更新文档
terminal(command="tmux new-session -d -s task3 -x 140 -y 40 && tmux send-keys -t task3 'cd ~/project && claude -p \"用新的 API 端点更新 README.md\" --allowedTools \"Read,Edit\" --max-turns 5' Enter")

# 监控所有任务
terminal(command="sleep 30 && for s in task1 task2 task3; do echo '=== '$s' ==='; tmux capture-pane -t $s -p -S -5 2>/dev/null; done")
```

<a id="claude-md-project-context-file"></a>
## CLAUDE.md — 项目上下文文件

Claude Code 会自动从项目根目录加载 `CLAUDE.md`。用它来持久化项目上下文：

```markdown
# 项目：我的 API

## 架构
- 使用 SQLAlchemy ORM 的 FastAPI 后端
- PostgreSQL 数据库，Redis 缓存
- 使用 pytest 进行测试，目标覆盖率 90%

## 关键命令
- `make test` — 运行完整测试套件
- `make lint` — ruff + mypy
- `make dev` — 在 :8000 启动开发服务器

## 代码规范
- 所有公共函数需添加类型提示
- 使用 Google 风格的文档字符串
- YAML 使用 2 空格缩进，Python 使用 4 空格缩进
- 禁止通配符导入
```

**要具体。** 不要写“写好代码”，而是用“JS 使用 2 空格缩进”或“测试文件以 `.test.ts` 后缀命名”。具体的指令能减少修正次数。

<a id="rules-directory-modular-claude-md"></a>
### 规则目录（模块化 CLAUDE.md）
对于规则较多的项目，使用规则目录代替一个庞大的 CLAUDE.md：
- **项目规则：** `.claude/rules/*.md` — 团队共享，受 Git 跟踪
- **用户规则：** `~/.claude/rules/*.md` — 个人，全局生效

规则目录中的每个 `.md` 文件都会作为额外上下文加载。这比把所有内容塞进一个 CLAUDE.md 更清晰。

<a id="auto-memory"></a>
### 自动记忆
Claude 会自动将学到的项目上下文存储在 `~/.claude/projects/&lt;project&gt;/memory/` 中。
- **限制：** 每个项目 25KB 或 200 行
- 这与 CLAUDE.md 是分开的——它是 Claude 自己对项目的笔记，跨会话累积

<a id="custom-subagents"></a>
## 自定义子 Agent

在 `.claude/agents/`（项目级）、`~/.claude/agents/`（个人级）或通过 `--agents` CLI 标志（会话级）定义专门的 Agent：

<a id="agent-location-priority"></a>
### Agent 位置优先级
1. `.claude/agents/` — 项目级，团队共享
2. `--agents` CLI 标志 — 会话级，动态
3. `~/.claude/agents/` — 用户级，个人

<a id="creating-an-agent"></a>
### 创建 Agent
```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: 安全导向的代码审查
model: opus
tools: [Read, Bash]
---
你是一名资深安全工程师。审查代码时关注：
- 注入漏洞（SQL、XSS、命令注入）
- 认证/授权缺陷
- 代码中的密钥
- 不安全的反序列化
```
通过 `@security-reviewer review the auth module` 调用

<a id="dynamic-agents-via-cli"></a>
### 通过 CLI 使用动态 Agents
```
terminal(command="claude --agents '{\"reviewer\": {\"description\": \"Reviews code\", \"prompt\": \"You are a code reviewer focused on performance\"}}' -p 'Use @reviewer to check auth.py'", timeout=120)
```

Claude 可编排多个 Agents：“用 @db-expert 优化查询，然后用 @security 审计修改内容。”

<a id="hooks-automation-on-events"></a>
## Hooks — 自动化事件触发

在 `.claude/settings.json`（项目级）或 `~/.claude/settings.json`（全局级）中配置：

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

<a id="all-8-hook-types"></a>
### 全部 8 种 Hook 类型
| Hook | 触发时机 | 常见用途 |
|------|----------|----------|
| `UserPromptSubmit` | Claude 处理用户提示之前 | 输入验证、日志记录 |
| `PreToolUse` | 工具执行之前 | 安全门控，阻止危险命令（exit 2 表示阻止） |
| `PostToolUse` | 工具执行完成后 | 自动格式化代码、运行 linter |
| `Notification` | 权限请求或输入等待时 | 桌面通知、提醒 |
| `Stop` | Claude 完成一次回答后 | 完成日志记录、状态更新 |
| `SubagentStop` | 子 Agent 完成时 | Agent 编排 |
| `PreCompact` | 上下文内存被清除之前 | 备份会话记录 |
| `SessionStart` | 会话开始时 | 加载开发上下文（如 `git status`） |

<a id="hook-environment-variables"></a>
### Hook 环境变量
| 变量 | 内容 |
|------|------|
| `CLAUDE_PROJECT_DIR` | 当前项目路径 |
| `CLAUDE_FILE_PATHS` | 正在修改的文件 |
| `CLAUDE_TOOL_INPUT` | 工具参数（JSON 格式） |

<a id="security-hook-examples"></a>
### 安全 Hook 示例
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|git push.*--force|:(){ :|:& };:'; then echo 'Dangerous command blocked!' && exit 2; fi"}]
  }]
}
```

<a id="mcp-integration"></a>
## MCP 集成

为数据库、API 和服务添加外部工具服务器：

```
# GitHub 集成
terminal(command="claude mcp add -s user github -- npx @modelcontextprotocol/server-github", timeout=30)

# PostgreSQL 查询
terminal(command="claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres --connection-string postgresql://localhost/mydb", timeout=30)

# Puppeteer 用于网页测试
terminal(command="claude mcp add puppeteer -- npx @anthropic-ai/server-puppeteer", timeout=30)
```

<a id="mcp-scopes"></a>
### MCP 作用域
| 标志 | 作用域 | 存储位置 |
|------|--------|----------|
| `-s user` | 全局（所有项目） | `~/.claude.json` |
| `-s local` | 当前项目（个人） | `.claude/settings.local.json`（gitignored） |
| `-s project` | 当前项目（团队共享） | `.claude/settings.json`（git-tracked） |
<a id="mcp-in-print-ci-mode"></a>
### MCP 打印/CI 模式
```
terminal(command="claude --bare -p 'Query database' --mcp-config mcp-servers.json --strict-mcp-config", timeout=60)
```
`--strict-mcp-config` 会忽略除了 `--mcp-config` 指定的所有 MCP 服务器。

在聊天中引用 MCP 资源：`@github:issue://123`

<a id="mcp-limits-tuning"></a>
### MCP 限制与调优
- **工具描述：** 每个服务器的工具描述和服务器指令上限为 2KB
- **结果大小：** 默认有上限；使用 `maxResultSizeChars` 注解可允许大型输出达到 **500K** 字符
- **输出令牌：** `export MAX_MCP_OUTPUT_TOKENS=50000` — 限制 MCP 服务器的输出，防止上下文洪水
- **传输方式：** `stdio`（本地进程）、`http`（远程）、`sse`（服务器推送事件）

<a id="monitoring-interactive-sessions"></a>
## 监控交互会话

<a id="reading-the-tui-status"></a>
### 查看 TUI 状态
```
# 定期捕获，检查 Claude 是否仍在工作或等待输入
terminal(command="tmux capture-pane -t dev -p -S -10")
```

注意以下指示符：
- 底部的 `❯` = 等待你的输入（Claude 已完成或正在问问题）
- `●` 行 = Claude 正在积极使用工具（读、写、运行命令）
- `⏵⏵ bypass permissions on` = 状态栏显示权限模式
- `◐ medium · /effort` = 状态栏中的当前精力级别
- `ctrl+o to expand` = 工具输出被截断（可交互式展开）

<a id="context-window-health"></a>
### 上下文窗口健康
在交互模式下使用 `/context` 查看上下文的彩色网格。关键阈值：
- **< 70%** — 正常操作，高精度
- **70-85%** — 精度开始下降，考虑 `/compact`
- **> 85%** — 幻觉风险显著增加，使用 `/compact` 或 `/clear`

<a id="environment-variables"></a>
## 环境变量

| 变量 | 效果 |
|----------|--------|
| `ANTHROPIC_API_KEY` | 用于认证的 API 密钥（OAuth 的替代方案） |
| `CLAUDE_CODE_EFFORT_LEVEL` | 默认努力等级：`low`、`medium`、`high`、`max` 或 `auto` |
| `MAX_THINKING_TOKENS` | 限制思考令牌数（设为 `0` 可完全禁用思考） |
| `MAX_MCP_OUTPUT_TOKENS` | 限制 MCP 服务器的输出（默认值各异；可设为 `50000` 等） |
| `CLAUDE_CODE_NO_FLICKER=1` | 启用备用屏幕渲染，消除终端闪烁 |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | 从子进程中清除凭据以提高安全性 |

<a id="cost-performance-tips"></a>
## 成本与性能技巧

1. **在打印模式下使用 `--max-turns`** 防止失控循环。大部分任务从 5-10 开始。
2. **使用 `--max-budget-usd`** 设置成本上限。注意：系统提示缓存创建至少需要约 $0.05。
3. **简单任务使用 `--effort low`**（更快、更便宜）。复杂推理使用 `high` 或 `max`。
4. **CI/脚本使用 `--bare`** 跳过插件/钩子发现开销。
5. **使用 `--allowedTools`** 限制到仅需要的工具（例如，仅用于审查的 `Read`）。
6. **交互会话中上下文变大时使用 `/compact`**。
7. **管道输入** 而非让 Claude 读取文件，当你只需要对已知内容进行分析时。
8. **简单任务使用 `--model haiku`**（更便宜），复杂的多步骤工作使用 `--model opus`。
9. **在打印模式下使用 `--fallback-model haiku`** 以优雅处理模型过载。
10. **对不同的任务开启新会话** — 会话持续 5 小时；新鲜上下文更高效。
11. **CI 中使用 `--no-session-persistence`** 避免在磁盘上积累已保存的会话。
<a id="pitfalls-gotchas"></a>
## 陷阱与注意事项

1. **交互模式必须使用 tmux** — Claude Code 是完整的 TUI 应用。仅靠 Hermes 终端中的 `pty=true` 可以工作，但 tmux 提供了 `capture-pane` 用于监控，以及 `send-keys` 用于输入，这对于编排至关重要。
2. **`--dangerously-skip-permissions` 对话框默认选择“否，退出”** — 你必须先按 Down 键再按 Enter 键来接受。打印模式（`-p`）完全跳过此步骤。
3. **`--max-budget-usd` 的最小值约为 $0.05** — 仅系统提示缓存创建就需要这个费用。设置更低的值会立即报错。
4. **`--max-turns` 仅适用于打印模式** — 在交互会话中会被忽略。
5. **Claude 可能使用 `python` 而不是 `python3`** — 在没有 `python` 符号链接的系统上，Claude 的 bash 命令第一次会失败，但会自动修正。
6. **恢复会话需要相同目录** — `--continue` 会查找当前工作目录最近的会话。
7. **`--json-schema` 需要足够的 `--max-turns`** — Claude 必须先读取文件才能生成结构化输出，这需要多个回合。
8. **信任对话框每个目录只出现一次** — 仅在第一次出现，之后会缓存。
9. **后台 tmux 会话会持久存在** — 完成后务必使用 `tmux kill-session -t &lt;name&gt;` 清理。
10. **斜杠命令（如 `/commit`）仅在交互模式下有效** — 在 `-p` 模式下，改用自然语言描述任务。
11. **`--bare` 跳过 OAuth** — 需要设置 `ANTHROPIC_API_KEY` 环境变量或在配置中添加 `apiKeyHelper`。
12. **上下文衰减真实存在** — 当上下文窗口使用率超过 70% 时，AI 输出质量会明显下降。使用 `/context` 监控并使用 `/compact` 主动压缩。

<a id="rules-for-hermes-agents"></a>
## Hermes Agent 规则

1. **单次任务优先使用打印模式（`-p`）** — 更干净，无需处理对话框，自带结构化输出
2. **多回合交互工作使用 tmux** — 编排 TUI 唯一可靠的方式
3. **始终设置 `workdir`** — 让 Claude 专注于正确的项目目录
4. **在打印模式下设置 `--max-turns`** — 防止无限循环和失控费用
5. **监控 tmux 会话** — 使用 `tmux capture-pane -t &lt;session&gt; -p -S -50` 检查进度
6. **留意 `❯` 提示符** — 表示 Claude 正在等待输入（已完成或在提问）
7. **清理 tmux 会话** — 完成后杀掉它们以避免资源泄漏
8. **向用户报告结果** — 完成后总结 Claude 做了什么以及有什么变化
9. **不要强制结束慢速会话** — Claude 可能正在执行多步骤工作；改为检查进度
10. **使用 `--allowedTools`** — 限制能力为任务实际所需的工具
