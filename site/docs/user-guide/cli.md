---
sidebar_position: 1
title: "CLI 界面"
description: "掌握 Hermes Agent 终端界面 —— 命令、快捷键、人格设定等"
---

# CLI 界面

Hermes Agent 的 CLI 是一个完整的终端用户界面 (TUI) —— 而非 Web UI。它具备多行编辑、斜杠命令自动补全、对话历史记录、中断并重定向以及工具输出流式展示等功能。专为生活在终端里的开发者打造。

## 运行 CLI

```bash
# 启动交互式会话（默认）
hermes

# 单次查询模式（非交互式）
hermes chat -q "Hello"

# 使用特定模型
hermes chat --model "anthropic/claude-sonnet-4"

# 使用特定提供商
hermes chat --provider nous        # 使用 Nous Portal
hermes chat --provider openrouter  # 强制使用 OpenRouter

# 使用特定工具集
hermes chat --toolsets "web,terminal,skills"

# 启动时预加载一个或多个技能
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -q "open a draft PR"

# 恢复之前的会话
hermes --continue             # 恢复最近一次 CLI 会话 (-c)
hermes --resume <session_id>  # 通过 ID 恢复特定会话 (-r)

# 详细模式（调试输出）
hermes chat --verbose

# 隔离的 git worktree（用于并行运行多个 Agent）
hermes -w                         # 在 worktree 中开启交互模式
hermes -w -q "Fix issue #123"     # 在 worktree 中进行单次查询
```

## 界面布局

<img className="docs-terminal-figure" src="/img/docs/cli-layout.svg" alt="Hermes CLI 布局的风格化预览，展示了横幅、对话区域和固定输入提示符。" />
<p className="docs-figure-caption">Hermes CLI 横幅、对话流和固定输入提示符（渲染为稳定的文档插图，而非脆弱的文本艺术字）。</p>

欢迎横幅让你一眼就能看到当前模型、终端后端、工作目录、可用工具以及已安装的技能。

### 状态栏

输入区域上方有一个常驻状态栏，实时更新：

```
 ⚕ claude-sonnet-4-20250514 │ 12.4K/200K │ [██████░░░░] 6% │ $0.06 │ 15m
```

| 元素 | 描述 |
|---------|-------------|
| 模型名称 | 当前模型（超过 26 个字符会被截断） |
| Token 计数 | 已用上下文 Token / 最大上下文窗口 |
| 上下文进度条 | 带有颜色编码阈值的视觉填充指示器 |
| 费用 | 预估会话费用（对于未知或免费模型显示为 `n/a`） |
| 时长 | 会话已持续时间 |

状态栏会根据终端宽度自适应 —— 宽度 ≥ 76 列时显示完整布局，52–75 列时显示紧凑布局，低于 52 列时显示最小布局（仅模型 + 时长）。

**上下文颜色编码：**

| 颜色 | 阈值 | 含义 |
|-------|-----------|---------|
| 绿色 | < 50% | 空间充裕 |
| 黄色 | 50–80% | 逐渐填满 |
| 橙色 | 80–95% | 接近限制 |
| 红色 | ≥ 95% | 接近溢出 —— 考虑使用 `/compress` |

使用 `/usage` 查看详细明细，包括按类别分类的费用（输入 vs 输出 Token）。

### 会话恢复显示

当恢复之前的会话（使用 `hermes -c` 或 `hermes --resume <id>`）时，横幅和输入提示符之间会出现一个“Previous Conversation”面板，显示对话历史的简要回顾。详见 [会话 —— 恢复时的对话回顾](sessions.md#conversation-recap-on-resume) 以了解细节和配置。

## 快捷键

| 按键 | 动作 |
|-----|--------|
| `Enter` | 发送消息 |
| `Alt+Enter` 或 `Ctrl+J` | 换行（多行输入） |
| `Alt+V` | 从剪贴板粘贴图片（需终端支持） |
| `Ctrl+V` | 粘贴文本并尝试附加剪贴板中的图片 |
| `Ctrl+B` | 启用语音模式时开始/停止录音 (`voice.record_key`，默认：`ctrl+b`) |
| `Ctrl+C` | 中断 Agent（2秒内连按两次强制退出） |
| `Ctrl+D` | 退出 |
| `Ctrl+Z` | 将 Hermes 挂起到后台（仅限 Unix）。在 shell 中运行 `fg` 恢复。 |
| `Tab` | 接受自动建议（虚影文字）或补全斜杠命令 |

## 斜杠命令

输入 `/` 即可看到自动补全下拉列表。Hermes 支持大量的 CLI 斜杠命令、动态技能命令以及用户定义的快速命令。

常见示例：

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示命令帮助 |
| `/model` | 查看或更改当前模型 |
| `/tools` | 列出当前可用工具 |
| `/skills browse` | 浏览技能中心和官方可选技能 |
| `/background <prompt>` | 在独立的后台会话中运行提示词 |
| `/skin` | 查看或切换当前的 CLI 皮肤 |
| `/voice on` | 开启 CLI 语音模式（按 `Ctrl+B` 录音） |
| `/voice tts` | 切换 Hermes 回复的语音播放开关 |
| `/reasoning high` | 增加推理力度 (Reasoning effort) |
| `/title My Session` | 为当前会话命名 |

有关完整的内置 CLI 和消息列表，请参阅 [斜杠命令参考](../reference/slash-commands.md)。

有关设置、提供商、静音调节以及在消息平台/Discord 语音中的使用，请参阅 [语音模式](features/voice-mode.md)。

:::tip
命令不区分大小写 —— `/HELP` 与 `/help` 效果相同。安装的技能也会自动变成斜杠命令。
:::

## 快速命令 (Quick Commands)

你可以定义自定义命令，以便立即运行 shell 命令而无需调用 LLM。这些命令在 CLI 和消息平台（Telegram、Discord 等）中均有效。

```yaml
# ~/.hermes/config.yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
```

然后在任何聊天中输入 `/status` 或 `/gpu` 即可。更多示例请参考 [配置指南](/user-guide/configuration#quick-commands)。

## 启动时预加载技能

如果你已经知道会话中需要哪些技能，可以在启动时传入：

```bash
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -s github-auth
```

Hermes 会在第一轮对话开始前将每个指定的技能加载到会话提示词中。该标志在交互模式和单次查询模式下均有效。

## 技能斜杠命令

`~/.hermes/skills/` 中安装的每个技能都会自动注册为斜杠命令。技能名称即为命令：

```
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor

# 仅输入技能名称会加载该技能，并让 Agent 询问你的需求：
/excalidraw
```

## 人格设定 (Personalities)

设置预定义的人格来改变 Agent 的语气：

```
/personality pirate
/personality kawaii
/personality concise
```

内置人格包括：`helpful` (乐于助人), `concise` (简洁), `technical` (技术型), `creative` (创意型), `teacher` (教师), `kawaii` (可爱), `catgirl` (猫娘), `pirate` (海盗), `shakespeare` (莎士比亚), `surfer` (冲浪者), `noir` (黑色电影), `uwu`, `philosopher` (哲学家), `hype` (气氛组)。

你也可以在 `~/.hermes/config.yaml` 中定义自定义人格：

```yaml
personalities:
  helpful: "You are a helpful, friendly AI assistant."
  kawaii: "You are a kawaii assistant! Use cute expressions..."
  pirate: "Arrr! Ye be talkin' to Captain Hermes..."
  # 添加你自己的！
```

## 多行输入

有两种方式输入多行消息：

1. **`Alt+Enter` 或 `Ctrl+J`** —— 插入新行
2. **反斜杠续行** —— 在行尾使用 `\` 继续：

```
❯ Write a function that:\
  1. Takes a list of numbers\
  2. Returns the sum
```

:::info
支持粘贴多行文本 —— 使用 `Alt+Enter` 或 `Ctrl+J` 插入换行符，或者直接粘贴内容。
:::

## 中断 Agent

你可以在任何时候中断 Agent：

- **在 Agent 工作时输入新消息 + Enter** —— 它会中断当前操作并处理你的新指令
- **`Ctrl+C`** —— 中断当前操作（2秒内连按两次强制退出）
- 正在运行的终端命令会被立即终止（先发送 SIGTERM，1秒后发送 SIGKILL）
- 在中断期间输入的多个消息会被合并为一个提示词

### 忙碌输入模式 (Busy Input Mode)

`display.busy_input_mode` 配置项控制当你按下 Enter 且 Agent 正在工作时的行为：

| 模式 | 行为 |
|------|----------|
| `"interrupt"` (默认) | 你的消息会中断当前操作并立即被处理 |
| `"queue"` | 你的消息会被静默排队，并在 Agent 完成当前任务后作为下一轮对话发送 |
```yaml
# ~/.hermes/config.yaml
display:
  busy_input_mode: "queue"   # 或 "interrupt" (默认)
```

当你想要准备后续消息而不意外取消正在进行的工作时，队列模式（Queue mode）非常有用。未知值将回退到 `"interrupt"`。

### 挂起到后台

在 Unix 系统上，按下 **`Ctrl+Z`** 可以将 Hermes 挂起到后台 —— 就像任何终端进程一样。Shell 会打印确认信息：

```
Hermes Agent has been suspended. Run `fg` to bring Hermes Agent back.
```

在 Shell 中输入 `fg` 即可在上次离开的地方恢复会话。Windows 系统不支持此功能。

## 工具进度显示

CLI 在 Agent 工作时会显示动画反馈：

**思考动画**（API 调用期间）：
```
  ◜ (｡•́︿•̀｡) pondering... (1.2s)
  ◠ (⊙_⊙) contemplating... (2.4s)
  ✧٩(ˊᗜˋ*)و✧ got it! (3.1s)
```

**工具执行流：**
```
  ┊ 💻 terminal `ls -la` (0.3s)
  ┊ 🔍 web_search (1.2s)
  ┊ 📄 web_extract (2.1s)
```

使用 `/verbose` 命令可以循环切换显示模式：`off → new → all → verbose`。该命令也可以在消息平台（如 Slack/Discord）中启用 —— 详见 [配置文档](/user-guide/configuration#display-settings)。

### 工具预览长度

`display.tool_preview_length` 配置项控制工具调用预览行（例如文件路径、终端命令）中显示的最大字符数。默认值为 `0`，表示不限制 —— 将显示完整路径和命令。

```yaml
# ~/.hermes/config.yaml
display:
  tool_preview_length: 80   # 将工具预览截断为 80 个字符 (0 = 不限制)
```

这在窄屏终端或工具参数包含极长文件路径时非常有用。

## 会话管理

### 恢复会话

当你退出 CLI 会话时，会打印一条恢复命令：

```
Resume this session with:
  hermes --resume 20260225_143052_a1b2c3

Session:        20260225_143052_a1b2c3
Duration:       12m 34s
Messages:       28 (5 user, 18 tool calls)
```

恢复选项：

```bash
hermes --continue                          # 恢复最近一次 CLI 会话
hermes -c                                  # 简写形式
hermes -c "my project"                     # 恢复指定名称的会话（该谱系中的最新会话）
hermes --resume 20260225_143052_a1b2c3     # 通过 ID 恢复特定会话
hermes --resume "refactoring auth"         # 通过标题恢复
hermes -r 20260225_143052_a1b2c3           # 简写形式
```

恢复操作会从 SQLite 中还原完整的对话历史。Agent 会看到所有之前的消息、工具调用和响应 —— 就像你从未离开过一样。

在聊天中使用 `/title My Session Name` 为当前会话命名，或者在命令行中使用 `hermes sessions rename <id> <title>`。使用 `hermes sessions list` 可以浏览过去的会话。

### 会话存储

CLI 会话存储在 Hermes 的 SQLite 状态数据库中，路径为 `~/.hermes/state.db`。数据库保存以下内容：

- 会话元数据（ID、标题、时间戳、Token 计数器）
- 消息历史
- 压缩/恢复会话之间的谱系关系
- `session_search` 使用的全文本搜索索引

某些消息适配器还会在数据库旁保留各平台的转录文件，但 CLI 本身是从 SQLite 会话存储中恢复的。

### 上下文压缩

当接近上下文限制时，长对话会自动进行摘要：

```yaml
# 在 ~/.hermes/config.yaml 中
compression:
  enabled: true
  threshold: 0.50    # 默认在达到上下文限制的 50% 时进行压缩
  summary_model: "google/gemini-3-flash-preview"  # 用于生成摘要的模型
```

触发压缩时，中间的轮次会被摘要，而前 3 轮和最后 4 轮对话始终会被保留。

## 后台会话 {#background-sessions}

在独立的后台会话中运行 Prompt，同时继续使用 CLI 处理其他工作：

```
/background Analyze the logs in /var/log and summarize any errors from today
```

Hermes 会立即确认任务并把 Prompt 输入框交还给你：

```
🔄 Background task #1 started: "Analyze the logs in /var/log and summarize..."
   Task ID: bg_143022_a1b2c3
```

### 工作原理

每个 `/background` Prompt 都会在一个守护线程中生成一个**完全独立的 Agent 会话**：

- **隔离的对话** —— 后台 Agent 不了解你当前会话的历史记录。它只接收你提供的 Prompt。
- **相同的配置** —— 后台 Agent 会继承当前会话的模型、Provider、工具集、推理设置和备用模型。
- **非阻塞** —— 你的前台会话保持完全可交互。你可以聊天、运行命令，甚至启动更多后台任务。
- **多任务** —— 你可以同时运行多个后台任务。每个任务都会分配一个数字 ID。

### 结果展示

当后台任务完成时，结果会以面板形式出现在终端中：

```
╭─ ⚕ Hermes (background #1) ──────────────────────────────────╮
│ Found 3 errors in syslog from today:                         │
│ 1. OOM killer invoked at 03:22 — killed process nginx        │
│ 2. Disk I/O error on /dev/sda1 at 07:15                      │
│ 3. Failed SSH login attempts from 192.168.1.50 at 14:30      │
╰──────────────────────────────────────────────────────────────╯
```

如果任务失败，你会看到错误通知。如果在配置中启用了 `display.bell_on_complete`，任务完成时终端会发出提示音。

### 使用场景

- **耗时研究** —— 在你编写代码时，执行 "/background research the latest developments in quantum error correction"
- **文件处理** —— 在你继续对话时，执行 "/background analyze all Python files in this repo and list any security issues"
- **并行调查** —— 同时启动多个后台任务，从不同角度探索问题

:::info
后台会话不会出现在你的主对话历史中。它们是带有独立任务 ID（例如 `bg_143022_a1b2c3`）的独立会话。
:::

## 静默模式

默认情况下，CLI 以静默模式运行，该模式会：
- 抑制工具产生的冗长日志
- 启用可爱风格（kawaii-style）的动画反馈
- 保持输出整洁且用户友好

如需查看调试输出：
```bash
hermes chat --verbose
```
