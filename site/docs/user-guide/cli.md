---
sidebar_position: 1
title: "CLI 界面"
description: "掌握 Hermes Agent 终端界面 —— 命令、快捷键、个性设置等"
---

# CLI 界面

Hermes Agent 的 CLI 是一个完整的终端用户界面 (TUI) —— 不是 Web UI。它具备多行编辑、斜杠命令自动补全、对话历史、中断与重定向以及流式工具输出等功能。专为生活在终端中的人打造。

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
hermes --continue             # 恢复最近的 CLI 会话 (-c)
hermes --resume <session_id>  # 按 ID 恢复特定会话 (-r)

# 详细模式（调试输出）
hermes chat --verbose

# 隔离的 git 工作树（用于并行运行多个 Agent）
hermes -w                         # 工作树中的交互模式
hermes -w -q "Fix issue #123"     # 工作树中的单次查询
```

## 界面布局

<img className="docs-terminal-figure" src="/img/docs/cli-layout.svg" alt="Hermes CLI 布局的样式化预览，展示了横幅、对话区域和固定的输入提示符。" />
<p className="docs-figure-caption">Hermes CLI 横幅、对话流和固定输入提示符，渲染为稳定的文档图形而非脆弱的文本艺术。</p>

欢迎横幅一目了然地显示您的模型、终端后端、工作目录、可用工具和已安装技能。

### 状态栏

一个持久的状态栏位于输入区域上方，实时更新：

```
 ⚕ claude-sonnet-4-20250514 │ 12.4K/200K │ [██████░░░░] 6% │ $0.06 │ 15m
```

| 元素 | 描述 |
|---------|-------------|
| 模型名称 | 当前模型（如果超过 26 个字符则截断） |
| 令牌计数 | 已使用的上下文令牌数 / 最大上下文窗口 |
| 上下文条 | 带有颜色编码阈值的视觉填充指示器 |
| 成本 | 预估的会话成本（对于未知/零价格模型显示 `n/a`） |
| 持续时间 | 已用会话时间 |

状态栏会根据终端宽度自适应 —— 在 ≥ 76 列时显示完整布局，52–75 列时显示紧凑布局，低于 52 列时显示最小布局（仅模型 + 持续时间）。

**上下文颜色编码：**

| 颜色 | 阈值 | 含义 |
|-------|-----------|---------|
| 绿色 | < 50% | 空间充足 |
| 黄色 | 50–80% | 即将填满 |
| 橙色 | 80–95% | 接近限制 |
| 红色 | ≥ 95% | 即将溢出 —— 考虑使用 `/compress` |

使用 `/usage` 获取详细分类，包括每类成本（输入与输出令牌）。

### 会话恢复显示

当恢复之前的会话（`hermes -c` 或 `hermes --resume <id>`）时，一个“先前对话”面板会出现在横幅和输入提示符之间，显示对话历史的紧凑摘要。详情和配置请参阅 [会话 — 恢复时的对话摘要](sessions.md#conversation-recap-on-resume)。

## 快捷键

| 按键 | 操作 |
|-----|--------|
| `Enter` | 发送消息 |
| `Alt+Enter` 或 `Ctrl+J` | 新行（多行输入） |
| `Alt+V` | 当终端支持时，从剪贴板粘贴图像 |
| `Ctrl+V` | 粘贴文本并视情况附加剪贴板图像 |
| `Ctrl+B` | 当语音模式启用时，开始/停止语音录制 (`voice.record_key`, 默认: `ctrl+b`) |
| `Ctrl+C` | 中断 Agent（2 秒内按两次强制退出） |
| `Ctrl+D` | 退出 |
| `Tab` | 接受自动建议（幽灵文本）或自动补全斜杠命令 |

## 斜杠命令

输入 `/` 查看自动补全下拉菜单。Hermes 支持大量 CLI 斜杠命令、动态技能命令和用户定义的快捷命令。

常见示例：

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示命令帮助 |
| `/model` | 显示或更改当前模型 |
| `/tools` | 列出当前可用工具 |
| `/skills browse` | 浏览技能中心和官方可选技能 |
| `/background <prompt>` | 在单独的背景会话中运行提示 |
| `/skin` | 显示或切换活动的 CLI 皮肤 |
| `/voice on` | 启用 CLI 语音模式（按 `Ctrl+B` 录制） |
| `/voice tts` | 切换 Hermes 回复的语音播放 |
| `/reasoning high` | 增加推理力度 |
| `/title My Session` | 为当前会话命名 |

完整的 CLI 和消息内置命令列表，请参阅 [斜杠命令参考](../reference/slash-commands.md)。

关于设置、提供商、静音调优以及消息平台/Discord 语音使用，请参阅 [语音模式](features/voice-mode.md)。

:::tip
命令不区分大小写 —— `/HELP` 和 `/help` 效果相同。已安装的技能也会自动成为斜杠命令。
:::

## 快捷命令

您可以定义自定义命令，无需调用 LLM 即可立即运行 shell 命令。这些命令在 CLI 和消息平台（Telegram、Discord 等）中均可使用。

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

然后在任何聊天中输入 `/status` 或 `/gpu`。更多示例请参阅 [配置指南](/user-guide/configuration#quick-commands)。

## 启动时预加载技能

如果您已经知道本次会话要激活哪些技能，可以在启动时传入：

```bash
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -s github-auth
```

Hermes 会在第一轮对话前将每个命名的技能加载到会话提示中。该标志在交互模式和单次查询模式下都有效。

## 技能斜杠命令

`~/.hermes/skills/` 目录下的每个已安装技能都会自动注册为斜杠命令。技能名称即成为命令：

```
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor

# 仅输入技能名称会加载它，并让 Agent 询问您的需求：
/excalidraw
```

## 个性设置

设置预定义的个性来改变 Agent 的语气：

```
/personality pirate
/personality kawaii
/personality concise
```

内置个性包括：`helpful`、`concise`、`technical`、`creative`、`teacher`、`kawaii`、`catgirl`、`pirate`、`shakespeare`、`surfer`、`noir`、`uwu`、`philosopher`、`hype`。

您也可以在 `~/.hermes/config.yaml` 中定义自定义个性：

```yaml
personalities:
  helpful: "你是一个乐于助人、友好的 AI 助手。"
  kawaii: "你是一个可爱的助手！使用可爱的表达方式..."
  pirate: "Arrr！你在和 Hermes 船长说话..."
  # 添加你自己的！
```

## 多行输入

有两种方式输入多行消息：

1. **`Alt+Enter` 或 `Ctrl+J`** —— 插入新行
2. **反斜杠续行** —— 在行尾使用 `\` 来续行：

```
❯ 写一个函数，它：\
  1. 接受一个数字列表\
  2. 返回总和
```

:::info
支持粘贴多行文本 —— 使用 `Alt+Enter` 或 `Ctrl+J` 插入换行符，或者直接粘贴内容。
:::

## 中断 Agent

您可以随时中断 Agent：

- 在 Agent 工作时**输入新消息 + Enter** —— 它会中断并处理您的新指令
- **`Ctrl+C`** —— 中断当前操作（2 秒内按两次强制退出）
- 正在运行的终端命令会立即终止（SIGTERM，1 秒后 SIGKILL）
- 中断期间输入的多个消息会合并为一个提示

## 工具进度显示

CLI 会在 Agent 工作时显示动画反馈：

**思考动画**（在 API 调用期间）：
```
  ◜ (｡•́︿•̀｡) 思考中... (1.2s)
  ◠ (⊙_⊙) 沉思中... (2.4s)
  ✧٩(ˊᗜˋ*)و✧ 搞定！ (3.1s)
```

**工具执行反馈：**
```
  ┊ 💻 terminal `ls -la` (0.3s)
  ┊ 🔍 web_search (1.2s)
  ┊ 📄 web_extract (2.1s)
```

使用 `/verbose` 循环切换显示模式：`off → new → all → verbose`。此命令也可为消息平台启用 —— 请参阅 [配置](/user-guide/configuration#display-settings)。

## 会话管理

### 恢复会话

当您退出 CLI 会话时，会打印一条恢复命令：

```
使用以下命令恢复此会话：
  hermes --resume 20260225_143052_a1b2c3

会话：        20260225_143052_a1b2c3
持续时间：       12m 34s
消息数：       28 (5 条用户，18 条工具调用)
```

恢复选项：

```bash
hermes --continue                          # 恢复最近的 CLI 会话
hermes -c                                  # 简写形式
hermes -c "my project"                     # 恢复一个命名会话（谱系中最新的）
hermes --resume 20260225_143052_a1b2c3     # 按 ID 恢复特定会话
hermes --resume "refactoring auth"         # 按标题恢复
hermes -r 20260225_143052_a1b2c3           # 简写形式
```

恢复操作会从 SQLite 中还原完整的对话历史。Agent 会看到所有先前的消息、工具调用和响应 —— 就像您从未离开过一样。

在聊天中使用 `/title My Session Name` 为当前会话命名，或从命令行使用 `hermes sessions rename <id> <title>`。使用 `hermes sessions list` 浏览过去的会话。

### 会话存储

CLI 会话存储在 Hermes 的 SQLite 状态数据库中，位于 `~/.hermes/state.db`。数据库保存：

- 会话元数据（ID、标题、时间戳、令牌计数器）
- 消息历史
- 压缩/恢复会话之间的谱系关系
- `session_search` 使用的全文搜索索引

一些消息适配器也会在数据库旁边保留每个平台的转录文件，但 CLI 本身是从 SQLite 会话存储中恢复的。

### 上下文压缩

长对话在接近上下文限制时会自动总结：

```yaml
# 在 ~/.hermes/config.yaml 中
compression:
  enabled: true
  threshold: 0.50    # 默认在达到上下文限制的 50% 时压缩
  summary_model: "google/gemini-3-flash-preview"  # 用于总结的模型
```

当压缩触发时，中间的对话轮次会被总结，而前 3 轮和后 4 轮总是被保留。

## 背景会话 {#background-sessions}

在单独的背景会话中运行提示，同时继续使用 CLI 进行其他工作：

```
/background 分析 /var/log 中的日志并总结今天的任何错误
```

Hermes 会立即确认任务并返回提示符给您：

```
🔄 背景任务 #1 已启动："分析 /var/log 中的日志并总结..."
   任务 ID：bg_143022_a1b2c3
```

### 工作原理

每个 `/background` 提示都会在守护线程中生成一个**完全独立的 Agent 会话**：

- **隔离的对话** —— 背景 Agent 不知道您当前会话的历史。它只接收您提供的提示。
- **相同的配置** —— 背景 Agent 继承您当前会话的模型、提供商、工具集、推理设置和回退模型。
- **非阻塞** —— 您的前台会话保持完全交互性。您可以聊天、运行命令，甚至启动更多背景任务。
- **多任务** —— 您可以同时运行多个背景任务。每个任务都会获得一个编号 ID。

### 结果

当背景任务完成时，结果会以面板形式出现在您的终端中：

```
╭─ ⚕ Hermes (background #1) ──────────────────────────────────╮
│ 在今天 syslog 中发现 3 个错误：                         │
│ 1. OOM killer 在 03:22 被调用 —— 杀死了进程 nginx        │
│ 2. 在 07:15 时 /dev/sda1 出现磁盘 I/O 错误                      │
│ 3. 在 14:30 时来自 192.168.1.50 的失败 SSH 登录尝试      │
╰──────────────────────────────────────────────────────────────╯
```

如果任务失败，您会看到错误通知。如果您的配置中启用了 `display.bell_on_complete`，任务完成时终端会响铃。

### 使用场景

- **长时间运行的研究** —— 当您编写代码时，执行“/background 研究量子纠错的最新进展”
- **文件处理** —— 当您继续对话时，执行“/background 分析此仓库中的所有 Python 文件并列出任何安全问题”
- **并行调查** —— 启动多个背景任务以同时探索不同角度
:::info
后台会话不会出现在主对话历史中。它们是独立的会话，拥有自己的任务 ID（例如 `bg_143022_a1b2c3`）。
:::

## 静默模式

默认情况下，CLI 在静默模式下运行，该模式会：
- 抑制来自工具的详细日志输出
- 启用可爱风格的动画反馈
- 保持输出简洁且用户友好

如需调试输出，请使用：
```bash
hermes chat --verbose
```
