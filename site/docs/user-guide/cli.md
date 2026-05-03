---
sidebar_position: 1
title: "CLI 界面"
description: "掌握 Hermes Agent 终端界面——命令、快捷键、人格设定等"
---

# CLI 界面 {#cli-interface}

Hermes Agent 的 CLI 是一个完整的终端用户界面（TUI），而非 Web UI。它支持多行编辑、斜杠命令自动补全、对话历史、中断与重定向，以及流式工具输出。专为常驻终端的用户打造。

:::tip
Hermes 还提供了一套现代化的 TUI，包含模态覆盖层、鼠标选择和非阻塞输入。使用 `hermes --tui` 启动——详见 [TUI](tui.md) 指南。
:::

## 运行 CLI {#running-the-cli}

```bash
# 启动交互式会话（默认）
hermes

# 单次查询模式（非交互式）
hermes chat -q "你好"

# 使用特定模型
hermes chat --model "anthropic/claude-sonnet-4"

# 使用特定提供商
hermes chat --provider nous        # 使用 Nous Portal
hermes chat --provider openrouter  # 强制使用 OpenRouter

# 使用特定工具集
hermes chat --toolsets "web,terminal,skills"

# 启动时预加载一个或多个技能
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -q "创建一个草稿 PR"

# 恢复之前的会话
hermes --continue             # 恢复最近的 CLI 会话（-c）
hermes --resume <session_id>  # 按 ID 恢复指定会话（-r）

# 详细模式（调试输出）
hermes chat --verbose

# 隔离的 git 工作树（用于并行运行多个 Agent）
hermes -w                         # 在工作树中交互模式
hermes -w -q "修复问题 #123"     # 在工作树中单次查询
```

## 界面布局 {#interface-layout}

<img className="docs-terminal-figure" src="/img/docs/cli-layout.svg" alt="Hermes CLI 布局的样式化预览，显示横幅、对话区域和固定输入提示。" />
<p className="docs-figure-caption">Hermes CLI 横幅、对话流和固定输入提示，以稳定的文档图形而非脆弱的文本艺术呈现。</p>

欢迎横幅一目了然地显示你的模型、终端后端、工作目录、可用工具和已安装的技能。

### 状态栏 {#status-bar}

输入区域上方有一个持久的状态栏，实时更新：

```
 ⚕ claude-sonnet-4-20250514 │ 12.4K/200K │ [██████░░░░] 6% │ $0.06 │ 15m
```

| 元素 | 描述 |
|---------|-------------|
| 模型名称 | 当前模型（超过 26 个字符时截断） |
| Token 计数 | 已使用的上下文 Token / 最大上下文窗口 |
| 上下文条 | 视觉填充指示器，带有颜色编码阈值 |
| 费用 | 预估会话费用（未知/零价格模型显示 `n/a`） |
| 时长 | 已用会话时间 |

状态栏会根据终端宽度自适应——≥ 76 列时显示完整布局，52–75 列时紧凑显示，低于 52 列时仅显示最小内容（模型 + 时长）。

**上下文颜色编码：**

| 颜色 | 阈值 | 含义 |
|-------|-----------|---------|
| 绿色 | < 50% | 空间充足 |
| 黄色 | 50–80% | 逐渐填满 |
| 橙色 | 80–95% | 接近上限 |
| 红色 | ≥ 95% | 接近溢出——考虑使用 `/compress` |

使用 `/usage` 查看详细分解，包括按类别划分的费用（输入 vs 输出 Token）。

### 会话恢复显示 {#session-resume-display}

当恢复之前的会话时（`hermes -c` 或 `hermes --resume &lt;id&gt;`），横幅和输入提示之间会出现一个“之前的对话”面板，显示对话历史的紧凑摘要。详情和配置请参见 [会话——恢复时的对话摘要](sessions.md#conversation-recap-on-resume)。
## 快捷键 {#keybindings}

| 按键 | 操作 |
|-----|--------|
| `Enter` | 发送消息 |
| `Alt+Enter` 或 `Ctrl+J` | 换行（多行输入） |
| `Alt+V` | 在终端支持时从剪贴板粘贴图片 |
| `Ctrl+V` | 粘贴文本并尝试附加剪贴板中的图片 |
| `Ctrl+B` | 启用语音模式时开始/停止录音（`voice.record_key`，默认：`ctrl+b`） |
| `Ctrl+G` | 在 `$EDITOR`（vim/nvim/nano/VS Code 等）中打开当前输入缓冲区。保存并退出后，编辑后的文本将作为下一条提示发送——适合编写长段落或多段提示。 |
| `Ctrl+X Ctrl+E` | Emacs 风格的外部编辑器备用绑定（行为与 `Ctrl+G` 相同）。 |
| `Ctrl+C` | 中断 Agent（2 秒内双击强制退出） |
| `Ctrl+D` | 退出 |
| `Ctrl+Z` | 将 Hermes 挂起到后台（仅 Unix）。在 shell 中运行 `fg` 恢复。 |
| `Tab` | 接受自动建议（幽灵文本）或自动补全斜杠命令 |

**多行粘贴预览。** 当粘贴多行文本块时，CLI 会回显一个紧凑的单行预览（`[pasted: 47 lines, 1,842 chars — press Enter to send]`），而不是将整个内容倾泻到回滚缓冲区中。实际发送的仍然是完整内容；这只是显示上的优化。

**最终回复中的 Markdown 剥离。** CLI 会从 *最终* Agent 回复中剥离最冗长的 Markdown 代码块标记以及 `**粗体**` / `*斜体*` 包裹符，使其在终端中呈现为可读的纯文本，而非原始源码。代码块和列表会被保留。这不会影响网关平台或工具结果——它们会保留 Markdown 以便原生渲染。

## 斜杠命令 {#slash-commands}

输入 `/` 即可看到自动补全下拉列表。Hermes 支持大量 CLI 斜杠命令、动态技能命令以及用户自定义的快速命令。

常见示例：

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示命令帮助 |
| `/model` | 显示或更改当前模型 |
| `/tools` | 列出当前可用的工具 |
| `/skills browse` | 浏览技能中心及官方可选技能 |
| `/background &lt;prompt&gt;` | 在独立的后台会话中运行提示 |
| `/skin` | 显示或切换当前 CLI 皮肤 |
| `/voice on` | 启用 CLI 语音模式（按 `Ctrl+B` 录音） |
| `/voice tts` | 切换 Hermes 回复的语音播放 |
| `/reasoning high` | 提高推理强度 |
| `/title My Session` | 为当前会话命名 |

完整的 CLI 内置命令和消息列表，请参见 [斜杠命令参考](../reference/slash-commands.md)。

关于设置、提供商、静音调节以及消息/Discord 语音使用，请参见 [语音模式](features/voice-mode.md)。

:::tip
命令不区分大小写——`/HELP` 与 `/help` 效果相同。已安装的技能也会自动成为斜杠命令。
:::

## 快速命令 {#quick-commands}

你可以定义自定义命令，在不调用 LLM 的情况下立即执行 shell 命令。这些命令在 CLI 和消息平台（Telegram、Discord 等）中均可使用。

```yaml
# ~/.hermes/config.yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
  restart:
    type: alias
    target: /gateway restart
```
在任意聊天中输入 `/status`、`/gpu` 或 `/restart`。更多示例请参阅[配置指南](/user-guide/configuration#quick-commands)。

## 启动时预加载技能 {#preloading-skills-at-launch}

如果你已经知道本次会话需要启用哪些技能，可以在启动时传入：

```bash
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -s github-auth
```

Hermes 会在第一轮对话前将每个命名的技能加载到会话提示中。该标志在交互模式和单次查询模式下均有效。

## 技能斜杠命令 {#skill-slash-commands}

`~/.hermes/skills/` 目录下安装的每个技能都会自动注册为斜杠命令。技能名称即命令名：

```
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor

# 仅输入技能名称即可加载它，让 Agent 询问你的需求：
/excalidraw
```

## 人格设定 {#personalities}

设置预定义人格来改变 Agent 的语气：

```
/personality pirate
/personality kawaii
/personality concise
```

内置人格包括：`helpful`、`concise`、`technical`、`creative`、`teacher`、`kawaii`、`catgirl`、`pirate`、`shakespeare`、`surfer`、`noir`、`uwu`、`philosopher`、`hype`。

你也可以在 `~/.hermes/config.yaml` 中定义自定义人格：

```yaml
personalities:
  helpful: "You are a helpful, friendly AI assistant."
  kawaii: "You are a kawaii assistant! Use cute expressions..."
  pirate: "Arrr! Ye be talkin' to Captain Hermes..."
  # 添加你自己的！
```

## 多行输入 {#multi-line-input}

有两种方式输入多行消息：

1. **`Alt+Enter` 或 `Ctrl+J`** — 插入新行
2. **反斜杠续行** — 以 `\` 结尾的行会继续：

```
❯ Write a function that:\
  1. Takes a list of numbers\
  2. Returns the sum
```

:::info
支持粘贴多行文本 — 使用 `Alt+Enter` 或 `Ctrl+J` 插入换行，或直接粘贴内容。
:::

## 中断 Agent {#interrupting-the-agent}

你可以随时中断 Agent：

- **在 Agent 工作时输入新消息 + Enter** — 会中断当前操作并处理你的新指令
- **`Ctrl+C`** — 中断当前操作（2 秒内按两次强制退出）
- 正在进行的终端命令会立即被终止（先发 SIGTERM，1 秒后发 SIGKILL）
- 中断期间输入的多个消息会合并为一个提示

### 忙碌输入模式 {#busy-input-mode}

`display.busy_input_mode` 配置键控制当 Agent 工作时按 Enter 键的行为：

| 模式 | 行为 |
|------|----------|
| `"interrupt"`（默认） | 你的消息会中断当前操作并立即处理 |
| `"queue"` | 你的消息会被静默排队，在 Agent 完成后作为下一轮发送 |
| `"steer"` | 你的消息通过 `/steer` 注入到当前运行中，在下次工具调用后到达 Agent — 不会中断，也不会产生新轮次 |

```yaml
# ~/.hermes/config.yaml
display:
  busy_input_mode: "steer"   # 或 "queue" 或 "interrupt"（默认）
```

`"queue"` 模式在你想要准备后续消息而不意外取消进行中的工作时非常有用。`"steer"` 模式在你想要在不中断的情况下中途重定向 Agent 时非常有用 — 例如，在它仍在编辑代码时说"实际上，也检查一下测试"。未知值会回退到 `"interrupt"`。
`"steer"` 有两种自动回退行为：如果 Agent 尚未启动，或者附带了图片，消息会回退到 `"queue"` 行为，从而不会丢失任何内容。

你也可以在 CLI 中更改它：

```text
/busy queue
/busy steer
/busy interrupt
/busy status
```

<a id="first-touch-hint"></a>
:::tip 首次提示
当 Hermes 正在工作时，你第一次按下 Enter 键，Hermes 会打印一行提示，提醒你 `/busy` 这个开关（`"(tip) 你的消息打断了当前运行……"`）。每个安装只会触发一次——`config.yaml` 中 `onboarding.seen.busy_input_prompt` 下的一个标志会锁定它。删除该键即可再次看到提示。
:::

### 挂起到后台 {#suspending-to-background}

在 Unix 系统上，按 **`Ctrl+Z`** 可将 Hermes 挂起到后台——就像任何终端进程一样。Shell 会打印一条确认信息：

```
Hermes Agent 已被挂起。运行 `fg` 可将 Hermes Agent 带回前台。
```

在 shell 中输入 `fg` 即可从你离开的地方精确恢复会话。Windows 上不支持此功能。

## 工具进度显示 {#tool-progress-display}

CLI 会在 Agent 工作时显示动画反馈：

**思考动画**（API 调用期间）：
```
  ◜ (｡•́︿•̀｡) 思考中... (1.2s)
  ◠ (⊙_⊙) 沉思中... (2.4s)
  ✧٩(ˊᗜˋ*)و✧ 搞定！ (3.1s)
```

**工具执行流：**
```
  ┊ 💻 终端 `ls -la` (0.3s)
  ┊ 🔍 web_search (1.2s)
  ┊ 📄 web_extract (2.1s)
```

使用 `/verbose` 循环切换显示模式：`off → new → all → verbose`。此命令也可在消息平台上启用——参见[配置](/user-guide/configuration#display-settings)。

### 工具预览长度 {#tool-preview-length}

`display.tool_preview_length` 配置键控制工具调用预览行中显示的最大字符数（例如文件路径、终端命令）。默认值为 `0`，表示无限制——显示完整路径和命令。

```yaml
# ~/.hermes/config.yaml
display:
  tool_preview_length: 80   # 将工具预览截断为 80 个字符（0 = 无限制）
```

这在窄终端或工具参数包含非常长的文件路径时很有用。

## 会话管理 {#session-management}

### 恢复会话 {#resuming-sessions}

当你退出 CLI 会话时，会打印一条恢复命令：

```
使用以下命令恢复此会话：
  hermes --resume 20260225_143052_a1b2c3

会话：        20260225_143052_a1b2c3
持续时间：    12m 34s
消息数：      28（5 条用户消息，18 次工具调用）
```

恢复选项：

```bash
hermes --continue                          # 恢复最近的 CLI 会话
hermes -c                                  # 短格式
hermes -c "my project"                     # 恢复指定名称的会话（同一系列中最新的）
hermes --resume 20260225_143052_a1b2c3     # 按 ID 恢复特定会话
hermes --resume "refactoring auth"         # 按标题恢复
hermes -r 20260225_143052_a1b2c3           # 短格式
```

恢复操作会从 SQLite 中还原完整的对话历史。Agent 可以看到所有先前的消息、工具调用和响应——就像你从未离开过一样。

在聊天中使用 `/title My Session Name` 为当前会话命名，或者从命令行使用 `hermes sessions rename &lt;id&gt; &lt;title&gt;`。使用 `hermes sessions list` 浏览过去的会话。
### 会话存储 {#session-storage}

CLI 会话存储在 Hermes 的 SQLite 状态数据库中，路径为 `~/.hermes/state.db`。该数据库保存：

- 会话元数据（ID、标题、时间戳、令牌计数器）
- 消息历史
- 跨压缩/恢复会话的谱系
- `session_search` 使用的全文搜索索引

某些消息适配器还会在数据库旁边保存按平台划分的转录文件，但 CLI 本身是从 SQLite 会话存储中恢复的。

### 上下文压缩 {#context-compression}

当接近上下文限制时，长对话会自动进行摘要：

```yaml
# 在 ~/.hermes/config.yaml 中
compression:
  enabled: true
  threshold: 0.50    # 默认在上下文限制的 50% 时进行压缩

# 在 auxiliary 下配置摘要模型：
auxiliary:
  compression:
    model: "google/gemini-3-flash-preview"  # 用于摘要的模型
```

当触发压缩时，中间轮次会被摘要，而前 3 轮和后 20 轮始终保留。

## 后台会话 {#background-sessions}

在单独的后台会话中运行提示，同时继续使用 CLI 进行其他工作：

```
/background 分析 /var/log 中的日志，并总结今天的所有错误
```

Hermes 会立即确认任务，并返回提示：

```
🔄 后台任务 #1 已启动："分析 /var/log 中的日志并总结..."
   任务 ID: bg_143022_a1b2c3
```

### 工作原理 {#how-it-works}

每个 `/background` 提示都会在守护线程中生成一个**完全独立的 Agent 会话**：

- **隔离的对话** — 后台 Agent 不知道当前会话的历史。它只接收你提供的提示。
- **相同的配置** — 后台 Agent 继承当前会话的模型、提供商、工具集、推理设置和备用模型。
- **非阻塞** — 前台会话保持完全交互。你可以聊天、运行命令，甚至启动更多后台任务。
- **多个任务** — 你可以同时运行多个后台任务。每个任务都有一个编号 ID。

### 结果 {#results}

当后台任务完成时，结果会以面板形式显示在终端中：

```
╭─ ⚕ Hermes (后台 #1) ──────────────────────────────────╮
│ 从今天的系统日志中发现 3 个错误：                         │
│ 1. OOM killer 在 03:22 被调用 — 杀死了进程 nginx        │
│ 2. 07:15 在 /dev/sda1 上发生磁盘 I/O 错误               │
│ 3. 14:30 来自 192.168.1.50 的 SSH 登录尝试失败          │
╰──────────────────────────────────────────────────────────╯
```

如果任务失败，你会看到错误通知。如果配置中启用了 `display.bell_on_complete`，任务完成时终端会响铃。

### 使用场景 {#use-cases}

- **长时间运行的研究** — 在处理代码时使用 "/background 研究量子纠错的最新进展"
- **文件处理** — 在继续对话时使用 "/background 分析此仓库中的所有 Python 文件并列出任何安全问题"
- **并行调查** — 启动多个后台任务，同时探索不同角度
:::info
后台会话不会出现在您的主对话历史中。它们是独立的会话，拥有自己的任务 ID（例如 `bg_143022_a1b2c3`）。
:::

## 静默模式 {#quiet-mode}

默认情况下，CLI 以静默模式运行，该模式会：
- 抑制工具产生的详细日志
- 启用 kawaii 风格动画反馈
- 保持输出简洁且用户友好

如需调试输出：
```bash
hermes chat --verbose
```
