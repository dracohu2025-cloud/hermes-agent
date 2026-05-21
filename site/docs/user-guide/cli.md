---
sidebar_position: 1
title: "CLI 界面"
description: "掌握 Hermes Agent 终端界面——命令、快捷键、角色设定等"
---

<a id="cli-interface"></a>
# CLI 界面

Hermes Agent 的 CLI 是一个完整的终端用户界面（TUI），而非 Web UI。它支持多行编辑、斜杠命令自动补全、对话历史、中断与重定向，以及流式工具输出。专为常驻终端的用户打造。

:::tip
Hermes 还提供了一套现代化的 TUI，包含模态覆盖层、鼠标选择和非阻塞输入。使用 `hermes --tui` 启动——详见 [TUI](tui.md) 指南。
:::

<a id="running-the-cli"></a>
## 运行 CLI

```bash
# 启动交互式会话（默认）
hermes

# 单次查询模式（非交互式）
hermes chat -q "你好"

# 指定模型
hermes chat --model "anthropic/claude-sonnet-4"

# 指定提供商
hermes chat --provider nous        # 使用 Nous Portal
hermes chat --provider openrouter  # 强制使用 OpenRouter

# 指定工具集
hermes chat --toolsets "web,terminal,skills"

# 预加载一个或多个技能启动
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -q "创建一个草稿 PR"

# 恢复之前的会话
hermes --continue             # 恢复最近的 CLI 会话（-c）
hermes --resume <session_id>  # 按 ID 恢复指定会话（-r）

# 详细模式（调试输出）
hermes chat --verbose

# 隔离的 Git 工作树（用于并行运行多个 Agent）
hermes -w                         # 在工作树中交互模式
hermes -w -q "修复问题 #123"     # 在工作树中单次查询
```

<a id="interface-layout"></a>
## 界面布局

<img className="docs-terminal-figure" src="/img/docs/cli-layout.svg" alt="Hermes CLI 布局的样式化预览，显示横幅、对话区域和固定输入提示。" />
<p className="docs-figure-caption">Hermes CLI 横幅、对话流和固定输入提示，以稳定的文档图形而非易碎的文本艺术呈现。</p>

欢迎横幅一目了然地显示你的模型、终端后端、工作目录、可用工具和已安装的技能。

<a id="status-bar"></a>
### 状态栏

输入区域上方有一个持久的状态栏，实时更新：

```
 ⚕ claude-sonnet-4-20250514 │ 12.4K/200K │ [██████░░░░] 6% │ $0.06 │ 15m
```

| 元素 | 描述 |
|---------|-------------|
| 模型名称 | 当前模型（超过 26 个字符时截断） |
| Token 计数 | 已使用的上下文 Token / 最大上下文窗口 |
| 上下文条 | 带颜色编码阈值的视觉填充指示器 |
| 费用 | 预估会话费用（未知/零价格模型显示 `n/a`） |
| 🗜️ N | **上下文压缩次数**——当前会话被自动压缩的次数。首次压缩触发后显示。 |
| ▶ N | **活跃后台任务数**——当前会话中仍在运行的 `/background` 提示数量。至少有一个任务在运行中时显示。 |
| 时长 | 已用会话时间 |
| ⚠ YOLO | **YOLO 模式警告**——当 `HERMES_YOLO_MODE` 开启时显示（启动时使用 `hermes --yolo`，或会话中通过 `/yolo` 切换）。与横幅行警告同步，确保你不会忘记处于自动批准模式。 |

状态栏会根据终端宽度自适应——≥ 76 列时显示完整布局，52–75 列时紧凑显示，低于 52 列时仅显示最小内容（模型 + 时长，以及 YOLO 徽章（如果激活））。
**上下文颜色编码：**

| 颜色 | 阈值 | 含义 |
|------|------|------|
| 绿色 | < 50% | 空间充足 |
| 黄色 | 50–80% | 逐渐占满 |
| 橙色 | 80–95% | 接近上限 |
| 红色 | ≥ 95% | 接近溢出 — 考虑使用 `/compress` |

使用 `/usage` 可查看更详细的分解，包括按类别（输入与输出 token）的成本。

<a id="session-resume-display"></a>
### 会话恢复显示

当恢复之前的会话时（`hermes -c` 或 `hermes --resume &lt;id&gt;`），横幅和输入提示之间会显示一个“之前的对话”面板，展示对话历史的紧凑摘要。有关详情和配置，请参阅 [会话 — 恢复时的对话摘要](sessions.md#conversation-recap-on-resume)。

<a id="keybindings"></a>
## 快捷键

| 按键 | 操作 |
|-----|------|
| `Enter` | 发送消息 |
| `Alt+Enter`、`Ctrl+J` 或 `Shift+Enter` | 换行（多行输入）。`Shift+Enter` 需要终端能将其与 `Enter` 区分开来 — 见下文。在 Windows Terminal 中，`Alt+Enter` 会被终端截获（全屏切换）；请改用 `Ctrl+Enter` 或 `Ctrl+J`。 |
| `Alt+V` | 在终端支持时从剪贴板粘贴图片 |
| `Ctrl+V` | 粘贴文本并尝试附加剪贴板中的图片 |
| `Ctrl+B` | 当语音模式启用时，开始/停止语音录制（`voice.record_key`，默认值：`ctrl+b`） |
| `Ctrl+G` | 在 `$EDITOR`（vim/nvim/nano/VS Code 等）中打开当前输入缓冲区。保存并退出可将编辑后的文本作为下一条提示发送 — 适合编写较长、多段的提示。 |
| `Ctrl+X Ctrl+E` | Emacs 风格的外部编辑器替代绑定（与 `Ctrl+G` 行为相同）。 |
| `Ctrl+C` | 中断 Agent（2 秒内连续按两次可强制退出） |
| `Ctrl+D` | 退出 |
| `Ctrl+Z` | 将 Hermes 挂起到后台（仅 Unix）。在 shell 中运行 `fg` 以恢复。 |
| `Tab` | 接受自动建议（幽灵文本）或自动补全斜杠命令 |

**多行粘贴预览。** 当粘贴多行文本块时，CLI 会显示一个紧凑的单行预览（`[已粘贴: 47 行, 1,842 字符 — 按 Enter 发送]`），而不是将整个内容倒入回滚缓冲区。完整内容仍会被实际发送；这仅仅是显示优化。

**最终响应中的 Markdown 清理。** CLI 会从 *最终* 的 Agent 回复中去除最冗长的 Markdown 围栏和 `**粗体**` / `*斜体*` 包裹，使其渲染为可读的终端散文，而非原始源码。代码块和列表会被保留。这不会影响网关平台或工具结果 —— 它们会保留 Markdown 用于原生渲染。

<a id="slash-commands"></a>
## 斜杠命令

输入 `/` 可看到自动补全下拉列表。Hermes 支持大量 CLI 斜杠命令、动态技能命令以及用户自定义快捷命令。

常见示例：

| 命令 | 描述 |
|------|------|
| `/help` | 显示命令帮助 |
| `/model` | 显示或更改当前模型 |
| `/tools` | 列出当前可用的工具 |
| `/skills browse` | 浏览技能中心及官方可选技能 |
| `/background &lt;prompt&gt;` | 在单独的后台会话中运行一个提示 |
| `/skin` | 显示或切换当前的 CLI 皮肤 |
| `/voice on` | 启用 CLI 语音模式（按 `Ctrl+B` 开始录制） |
| `/voice tts` | 切换 Hermes 回复的语音播放 |
| `/reasoning high` | 增加推理努力程度 |
| `/title My Session` | 为当前会话命名 |
| `/status` | 显示会话信息 — 模型/配置文件/token/持续时间 — 后跟一个本地 **会话摘要** 块（最近的轮次数量、使用最多的工具、接触过的文件、最新的用户提示 + 助手回复）。纯本地计算；不调用 LLM。 |
| `/sessions` | 在经典 CLI 中直接打开交互式会话选择器（与 TUI 使用的界面相同）。输入可过滤，方向键导航，Enter 恢复。 |
关于完整的内置 CLI 和消息列表，请参见 [斜杠命令参考](../reference/slash-commands.md)。

关于设置、提供商、静音调节以及消息/Discord 语音使用，请参见 [语音模式](features/voice-mode.md)。

:::tip
命令不区分大小写——`/HELP` 和 `/help` 效果相同。已安装的技能也会自动成为斜杠命令。
:::

<a id="quick-commands"></a>
## 快速命令

你可以定义自定义命令，这些命令会立即执行 shell 命令，无需调用 LLM。在 CLI 和消息平台（Telegram、Discord 等）中都可以使用。

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

然后在任意聊天中输入 `/status`、`/gpu` 或 `/restart`。更多示例请参见 [配置指南](/user-guide/configuration#quick-commands)。

<a id="preloading-skills-at-launch"></a>
## 启动时预加载技能

如果你已经知道想让哪些技能在当前会话中生效，可以在启动时传入它们：

```bash
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -s github-auth
```

Hermes 在开始第一轮对话之前，会将每个命名的技能加载到会话提示中。该标志在交互模式和单查询模式下都可使用。

<a id="skill-slash-commands"></a>
## 技能斜杠命令

`~/.hermes/skills/` 中的每个已安装技能都会自动注册为斜杠命令。技能名称就是命令：

```
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor

# 仅输入技能名称即可加载它，并让 Agent 询问你需要什么：
/excalidraw
```

<a id="personalities"></a>
## 个性

设置预定义的个性来改变 Agent 的语气：

```
/personality pirate
/personality kawaii
/personality concise
```

内置个性包括：`helpful`、`concise`、`technical`、`creative`、`teacher`、`kawaii`、`catgirl`、`pirate`、`shakespeare`、`surfer`、`noir`、`uwu`、`philosopher`、`hype`。

你也可以在 `~/.hermes/config.yaml` 中定义自定义个性：

```yaml
personalities:
  helpful: "你是一个乐于助人、友好的 AI 助手。"
  kawaii: "你是一个可爱的助手！使用可爱的表达方式..."
  pirate: "阿嚏！你在和 Hermes 船长说话..."
  # 添加你自己的！
```

<a id="multi-line-input"></a>
## 多行输入

有两种方式输入多行消息：

1. **`Alt+Enter`、`Ctrl+J` 或 `Shift+Enter`** —— 插入新行
2. **反斜杠续行** —— 以 `\` 结束一行以继续：

```
❯ 编写一个函数：\
  1. 接收一个数字列表\
  2. 返回它们的和
```

:::info
支持粘贴多行文本——可以使用上述任意换行键，或者直接粘贴内容。
:::

<a id="shift-enter-compatibility"></a>
### Shift+Enter 兼容性

大多数终端默认对 `Enter` 和 `Shift+Enter` 发送相同的字节序列，因此应用程序无法区分它们。只有当终端通过 [Kitty 键盘协议](https://sw.kovidgoyal.net/kitty/keyboard-protocol/) 或 xterm 的 `modifyOtherKeys` 模式发送不同的序列时，Hermes 才能识别 `Shift+Enter`。
| 终端 | 状态 |
|---|---|
| Kitty, foot, WezTerm, Ghostty | 默认启用独立的 `Shift+Enter` |
| iTerm2（新版）、Alacritty、VS Code 终端、Warp | 在设置中启用 Kitty 协议后支持 |
| Windows Terminal Preview 1.25+ | 在设置中启用 Kitty 协议后支持 |
| macOS Terminal.app、Windows Terminal 稳定版 | 不支持 — `Shift+Enter` 与 `Enter` 无法区分 |

当终端无法区分它们时，`Alt+Enter` 和 `Ctrl+J` 在所有地方仍然有效。**在 Windows Terminal 上，`Alt+Enter` 会被终端捕获（切换全屏），不会到达 Hermes — 请使用 `Ctrl+Enter`（会发送为 `Ctrl+J`）或直接使用 `Ctrl+J` 来换行。**

<a id="interrupting-the-agent"></a>
## 中断 Agent

你可以随时中断 agent：

- **在 agent 工作时输入新消息 + Enter** — 它会中断当前操作并处理你的新指令
- **`Ctrl+C`** — 中断当前操作（2 秒内按两次可强制退出）
- 正在进行的终端命令会立即被终止（先发 SIGTERM，1 秒后发 SIGKILL）
- 中断期间输入的多个消息会合并为一个提示

<a id="busy-input-mode"></a>
### 忙碌输入模式

`display.busy_input_mode` 配置键控制当 agent 工作时你按 Enter 会发生什么：

| 模式 | 行为 |
|------|----------|
| `"interrupt"`（默认） | 你的消息中断当前操作并立即被处理 |
| `"queue"` | 你的消息被静默排队，在 agent 完成后作为下一轮发送 |
| `"steer"` | 你的消息通过 `/steer` 注入到当前运行中，在下一个工具调用后到达 agent — 不会中断，也不会产生新轮次 |

```yaml
# ~/.hermes/config.yaml
display:
  busy_input_mode: "steer"   # 或 "queue" 或 "interrupt"（默认）
```

`"queue"` 模式在你想要准备后续消息而不意外取消正在进行的任务时很有用。`"steer"` 模式在你想要在不中断的情况下中途重定向 agent 时很有用 — 例如，在它还在编辑代码时说“实际上，也检查一下测试”。未知值会回退到 `"interrupt"`。

`"steer"` 有两个自动回退情况：如果 agent 尚未开始，或者附加了图片，消息会回退到 `"queue"` 行为，这样不会丢失任何内容。

你也可以在 CLI 内部更改它：

```text
/busy queue
/busy steer
/busy interrupt
/busy status
```

:::tip 首次提示
<a id="first-touch-hint"></a>
当你第一次在 Hermes 工作时按 Enter 时，Hermes 会打印一行提醒，解释 `/busy` 开关（“（提示）你的消息中断了当前运行…”）。它每个安装只会触发一次 — `config.yaml` 中 `onboarding.seen.busy_input_prompt` 下的一个标志会锁定它。删除该键可以再次看到提示。
:::

<a id="suspending-to-background"></a>
### 挂起到后台

在 Unix 系统上，按 **`Ctrl+Z`** 可以将 Hermes 挂起到后台 — 就像任何终端进程一样。Shell 会打印一条确认信息：

```
Hermes Agent 已被挂起。运行 `fg` 可将 Hermes Agent 带回前台。
```
在 shell 中输入 `fg` 即可从上次离开的地方精确恢复会话。此功能在 Windows 上不受支持。

<a id="tool-progress-display"></a>
## 工具进度显示

CLI 会在 Agent 工作时显示动画反馈：

**思考动画**（API 调用期间）：
```
  ◜ (｡•́︿•̀｡) 正在思考... (1.2s)
  ◠ (⊙_⊙) 正在沉思... (2.4s)
  ✧٩(ˊᗜˋ*)و✧ 搞定了！ (3.1s)
```

**工具执行信息流：**
```
  ┊ 💻 终端 `ls -la` (0.3s)
  ┊ 🔍 web_search (1.2s)
  ┊ 📄 web_extract (2.1s)
```

使用 `/verbose` 循环切换显示模式：`关闭 → 新 → 全部 → 详细`。此命令也可在消息平台启用——参见[配置](/user-guide/configuration#display-settings)。

<a id="tool-preview-length"></a>
### 工具预览长度

`display.tool_preview_length` 配置键控制工具调用预览行（例如文件路径、终端命令）中显示的最大字符数。默认值为 `0`，表示无限制——会显示完整路径和命令。

```yaml
# ~/.hermes/config.yaml
display:
  tool_preview_length: 80   # 将工具预览截断为 80 个字符（0 = 无限制）
```

这在窄终端或工具参数包含非常长的文件路径时很有用。

<a id="session-management"></a>
## 会话管理

<a id="resuming-sessions"></a>
### 恢复会话

当退出 CLI 会话时，会打印一条恢复命令：

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

在聊天中使用 `/title My Session Name` 为当前会话命名，或从命令行使用 `hermes sessions rename &lt;id&gt; &lt;title&gt;`。使用 `hermes sessions list` 浏览过去的会话。

<a id="session-storage"></a>
### 会话存储

CLI 会话存储在 Hermes 的 SQLite 状态数据库中，路径为 `~/.hermes/state.db`。该数据库保存：

- 会话元数据（ID、标题、时间戳、令牌计数器）
- 消息历史
- 跨压缩/恢复会话的谱系
- `session_search` 使用的全文搜索索引

某些消息适配器还会在数据库旁边保存平台特定的对话记录文件，但 CLI 本身是从 SQLite 会话存储中恢复的。

<a id="context-compression"></a>
### 上下文压缩

当接近上下文限制时，长对话会自动进行摘要：

```yaml
# 在 ~/.hermes/config.yaml 中
compression:
  enabled: true
  threshold: 0.50    # 默认在达到上下文限制的 50% 时进行压缩

# 在 auxiliary 下配置摘要模型：
auxiliary:
  compression:
    model: ""  # 留空则使用主聊天模型（默认）。或指定一个便宜快速的模型，例如 "google/gemini-3-flash-preview"。
```
当压缩触发时，中间轮次的对话会被总结，而前 3 轮和后 20 轮对话始终保留。

<a id="background-sessions"></a>
## 后台会话 {#background-sessions}

在继续使用 CLI 进行其他工作的同时，在独立的后台会话中运行一个提示：

```
/background 分析 /var/log 中的日志，并总结今天的所有错误
```

Hermes 会立即确认任务，并将提示返回给你：

```
🔄 后台任务 #1 已启动："分析 /var/log 中的日志并总结..."
   任务 ID: bg_143022_a1b2c3
```

<a id="how-it-works"></a>
### 工作原理

每个 `/background` 提示都会在一个守护线程中生成一个**完全独立的 Agent 会话**：

- **隔离的对话** — 后台 Agent 不知道你当前会话的历史记录。它只接收你提供的提示。
- **相同的配置** — 后台 Agent 会继承当前会话的模型、提供商、工具集、推理设置和备用模型。
- **非阻塞** — 你的前台会话始终保持完全交互。你可以聊天、运行命令，甚至启动更多后台任务。
- **多个任务** — 你可以同时运行多个后台任务。每个任务都会获得一个编号 ID。

<a id="results"></a>
### 结果

当后台任务完成时，结果会以面板形式显示在你的终端中：

```
╭─ ⚕ Hermes (后台 #1) ──────────────────────────────────╮
│ 在今天的系统日志中发现 3 个错误：                         │
│ 1. 03:22 触发了 OOM killer — 杀死了 nginx 进程          │
│ 2. 07:15 /dev/sda1 出现磁盘 I/O 错误                    │
│ 3. 14:30 来自 192.168.1.50 的 SSH 登录尝试失败          │
╰──────────────────────────────────────────────────────────╯
```

如果任务失败，你会看到错误通知。如果你的配置中启用了 `display.bell_on_complete`，任务完成时终端会发出提示音。

<a id="use-cases"></a>
### 使用场景

- **长时间运行的研究** — 在处理代码的同时，执行 "/background 研究量子纠错的最新进展"
- **文件处理** — 在继续对话的同时，执行 "/background 分析此仓库中的所有 Python 文件并列出任何安全问题"
- **并行调查** — 启动多个后台任务，同时探索不同角度

:::info
后台会话不会出现在你的主对话历史中。它们是独立的会话，拥有自己的任务 ID（例如 `bg_143022_a1b2c3`）。
:::

<a id="quiet-mode"></a>
## 静默模式

默认情况下，CLI 以静默模式运行，该模式会：
- 抑制来自工具的详细日志输出
- 启用可爱风格的动画反馈
- 保持输出简洁且用户友好

如需调试输出：
```bash
hermes chat --verbose
```
