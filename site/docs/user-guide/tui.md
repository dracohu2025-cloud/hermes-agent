---
sidebar_position: 2
title: "TUI"
description: "启动 Hermes 的现代终端界面——支持鼠标操作、丰富的覆盖层以及非阻塞输入。"
---

<a id="tui"></a>
# TUI

TUI 是 Hermes 的现代前端——一个基于终端界面的工具，与[经典 CLI](cli.md) 使用相同的 Python 运行时。相同的 Agent、相同的会话、相同的斜杠命令；但提供了更清晰、响应更快的交互界面。

这是以交互方式运行 Hermes 的推荐方式。

<a id="launch"></a>
## 启动

```bash
# 启动 TUI
hermes --tui

# 恢复最近的 TUI 会话（如果没有则回退到最近的经典会话）
hermes --tui -c
hermes --tui --continue

# 通过 ID 或标题恢复特定会话
hermes --tui -r 20260409_000000_aa11bb
hermes --tui --resume "my t0p session"

# 直接运行源码——跳过预构建步骤（适用于 TUI 贡献者）
hermes --tui --dev
```

你也可以通过环境变量启用它：

```bash
export HERMES_TUI=1
hermes          # 现在使用 TUI
hermes chat     # 同样
```

经典 CLI 仍然是默认选项。[CLI 接口](cli.md) 中记录的所有功能——斜杠命令、快速命令、技能预加载、个性设置、多行输入、中断——在 TUI 中的工作方式完全相同。

<a id="why-the-tui"></a>
## 为什么选择 TUI

- **即时首屏**——在应用完成加载之前，横幅就已经显示，因此 Hermes 启动时终端不会感觉卡顿。
- **非阻塞输入**——在会话准备就绪之前即可输入并排队消息。当 Agent 上线时，你的第一条提示会立即发送。
- **丰富的覆盖层**——模型选择器、会话选择器、审批和澄清提示都以模态面板形式呈现，而不是内联流程。
- **实时会话面板**——工具和技能在初始化过程中会逐步填充显示。
- **鼠标友好选择**——拖动以使用统一背景高亮，而不是 SGR 反色。使用终端的常规复制手势进行复制。
- **备用屏幕渲染**——差异更新意味着流式传输时无闪烁，退出后无回滚杂乱。
- **编辑器辅助功能**——长代码片段的内联粘贴折叠、`Cmd+V` / `Ctrl+V` 文本粘贴并支持剪贴板图片回退、括号粘贴安全保护，以及图片/文件路径附件规范化。

相同的[皮肤](features/skins.md)和[个性设置](features/personality.md)同样适用。在会话中通过 `/skin ares`、`/personality pirate` 切换，界面会实时重绘。请参阅[皮肤与主题](features/skins.md)获取完整的可自定义键列表，以及哪些适用于经典 CLI 与 TUI——TUI 支持横幅调色板、UI 颜色、提示符字形/颜色、会话显示、补全菜单、选择背景色、`tool_prefix` 和 `help_header`。

<a id="collapsible-banner-sections"></a>
### 可折叠的横幅区域

TUI 启动横幅将运行时信息分为四个可折叠区域，每个区域标题旁都有一个 `▸` / `▾` 箭头：

| 区域 | 默认状态 |
|---------|---------------|
| 工具 | 展开 |
| 技能 | 折叠 |
| 系统提示 | 折叠 |
| MCP 服务器 | 折叠 |

点击区域标题（或其箭头）上的任意位置即可切换。工具列表默认展开，因为它是会话开始时最常检查的区域；技能、系统提示和 MCP 服务器默认折叠，这样即使你安装了数十个技能或连接了许多 MCP 服务器，横幅也能保持紧凑。状态仅对当前横幅实例有效，因此下次启动时会重置为默认值。
<a id="requirements"></a>
## 系统要求

- **Node.js** ≥ 20 — TUI 作为 Python CLI 启动的子进程运行。`hermes doctor` 会验证此项。
- **TTY** — 与经典 CLI 类似，在管道输入 stdin 或非交互环境中运行时，会回退到单查询模式。

首次启动时，Hermes 会将 TUI 的 Node 依赖安装到 `ui-tui/node_modules`（一次性操作，耗时数秒）。后续启动会很快。如果你拉取了新版本的 Hermes，当源文件比 dist 更新时，TUI 包会自动重建。

<a id="external-prebuild"></a>
### 外部预构建

提供预构建包的分发版本（Nix、系统包）可以将 Hermes 指向该路径：

```bash
export HERMES_TUI_DIR=/path/to/prebuilt/ui-tui
hermes --tui
```

该目录必须包含 `dist/entry.js`。

<a id="keybindings"></a>
## 快捷键

快捷键与[经典 CLI](cli.md#keybindings) 完全一致。仅有的行为差异如下：

- **鼠标拖拽** 使用统一的选中背景高亮文本。
- **`Cmd+V` / `Ctrl+V`** 首先尝试普通文本粘贴，然后回退到 OSC52/原生剪贴板读取，最后当剪贴板或粘贴内容解析为图片时，会附加图片。
- **`/terminal-setup`** 安装本地 VS Code / Cursor / Windsurf 终端绑定，以在 macOS 上获得更好的 `Cmd+Enter` 和撤销/重做一致性。
- **斜杠自动补全** 以带描述的浮动面板形式打开，而非内联下拉菜单。
- **`Ctrl+X`** — 当队列中的消息被高亮时（在 Agent 仍在运行时发送的消息），将其从队列中删除。**`Esc`** 取消编辑并取消高亮，但不删除。
- **`Ctrl+G` / `Ctrl+X Ctrl+E`** — 在 `$EDITOR` 中打开当前输入缓冲区，用于多行/长提示词编写；保存并退出会将内容作为提示词发送回去。

<a id="slash-commands"></a>
## 斜杠命令

所有斜杠命令均保持不变。部分命令由 TUI 专属实现——它们会产生更丰富的输出，或渲染为覆盖层而非内联面板：

| 命令 | TUI 行为 |
|---------|--------------|
| `/help` | 覆盖层，显示分类命令，支持方向键导航 |
| `/sessions` | 模态会话选择器 — 预览、标题、Token 总数、内联恢复 |
| `/model` | 模态模型选择器，按提供商分组，附带成本提示 |
| `/skin` | 实时预览 — 浏览时主题更改即时生效 |
| `/details` | 切换详细工具调用信息（全局或按部分） |
| `/usage` | 丰富的 Token / 成本 / 上下文面板 |
| `/agents`（别名 `/tasks`） | 可观测性覆盖层 — 实时子 Agent 树，包含终止/暂停控制、每个分支的成本/Token/文件汇总、逐轮历史 |
| `/reload` | 重新读取 `~/.hermes/.env` 到正在运行的 TUI 进程，使新添加的 API 密钥无需重启即可生效 |
| `/mouse` | 运行时切换鼠标跟踪开关（也会持久化到 `config.yaml` 中的 `display.mouse_tracking`） |

所有其他斜杠命令（包括已安装的技能、快速命令和个性切换）与经典 CLI 完全相同。请参阅[斜杠命令参考](../reference/slash-commands.md)。

<a id="latex-math-rendering"></a>
## LaTeX 数学公式渲染

TUI 的 Markdown 管道支持内联渲染 LaTeX 数学公式：`$E = mc^2$` 和 `$$\frac{a}{b}$$` 会渲染为 Unicode 格式的数学公式，而非原始的 TeX 源码。支持内联和块级数学公式；不支持的语法会回退为显示包裹在代码跨度中的字面 TeX，以便保持可复制性。
这是始终开启的，无需任何配置。经典 CLI 会保留原始的 TeX。

<a id="light-terminal-detection"></a>
## 浅色终端检测

TUI 会自动检测浅色终端并切换到对应主题。检测分为三个层级：

1. `HERMES_TUI_THEME` 环境变量 —— 最高优先级。可选值：`light`、`dark`，或者一个 6 位背景色十六进制码（例如 `ffffff`、`1a1a2e`）。
2. `COLORFGBG` 环境变量 —— 经典的“我的背景色是什么？”提示，由 xterm 衍生终端使用。
3. 通过 OSC 11 探查终端背景色 —— 适用于未设置 `COLORFGBG` 的现代终端（Ghostty、Warp、iTerm2、WezTerm、Kitty）。

如果你希望无论终端如何都永久使用浅色主题：

```bash
export HERMES_TUI_THEME=light
```

<a id="busy-indicator-styles"></a>
## 忙碌指示器样式

状态栏的忙碌指示器是可插拔的 —— 默认在 Agent 工作期间每 2.5 秒轮换一次 Hermes 的可爱脸谱。你可以在配置中或通过 `/indicator` 斜杠命令选择其他样式：

```yaml
display:
  tui_status_indicator: kaomoji   # kaomoji | emoji | unicode | ascii
```

或在会话内：`/indicator emoji`（等等）。各个样式的字符宽度均已适配，因此状态栏其他部分在轮换时不会抖动。

<a id="auto-resume"></a>
## 自动恢复

默认情况下，`hermes --tui` 每次启动都会开启一个新会话。若要自动重新连接到最近的 TUI 会话（在终端或 SSH 连接意外断开时很有用），请选择启用：

```bash
export HERMES_TUI_RESUME=1          # 最近一次 TUI 会话
# 或：
export HERMES_TUI_RESUME=<会话 ID>   # 指定会话
```

取消设置该变量或显式传递 `--resume &lt;id&gt;` 可覆盖单次启动行为。

<a id="status-line"></a>
## 状态栏

TUI 的状态栏实时追踪 Agent 状态：

| 状态 | 含义 |
|--------|---------|
| `starting agent…` | 会话 ID 已生效，工具和技能仍在加载中。你可以输入 —— 消息会排队，并在就绪后发送。 |
| `ready` | Agent 空闲，正在接收输入。 |
| `thinking…` / `running…` | Agent 正在推理或执行工具。 |
| `interrupted` | 当前回合已取消；按回车键再次发送。 |
| `forging session…` / `resuming…` | 初始连接或 `--resume` 握手过程。 |

每套皮肤的状态栏颜色和阈值与经典 CLI 共用——具体定制请参见[皮肤](features/skins.md)文档。

状态栏还会显示：

- **当前工作目录及 git 分支** —— 例如 `~/projects/hermes-agent (docs/two-week-gap-sweep)`。当你在另一个终端执行 `git checkout` 时，分支后缀会更新（基于 mtime 缓存），因此 TUI 会反映你实际使用的分支，而不是启动时的分支。
- **每次提示的已用时间** —— 回合运行时显示 `⏱ 12s/3m 45s`（动态更新），回合结束后固定为 `⏲ 32s / 3m 45s`。第一个数字是距离上次用户消息以来的时间，第二个数字是会话总时长。每次新提示都会重置。
- **`🗜️ N`** —— 当前运行会话已被自动压缩的次数。首次压缩发生后出现。
- **`▶ N`** —— 此会话中当前正在运行的 `/background` 任务数量。当至少有一个任务进行中时出现。
- **`⚠ YOLO`** —— 当 YOLO 模式开启时（`hermes --yolo`、`/yolo` 或 `HERMES_YOLO_MODE=1`）显示的可见警告。该徽标也会出现在启动横幅中，确保你不会在未注意的情况下启动一个自动批准会话。
<a id="configuration"></a>
## 配置

TUI 遵守所有标准 Hermes 配置：`~/.hermes/config.yaml`、profiles、personalities、skins、quick commands、credential pools、memory providers、tool/skill enablement。没有 TUI 专用的配置文件。

少数几个键专用于调整 TUI 外观：

```yaml
display:
  skin: default              # any built-in or custom skin
  personality: helpful
  details_mode: collapsed    # hidden | collapsed | expanded — global accordion default
  sections:                  # optional: per-section overrides (any subset)
    thinking: expanded       # always open
    tools: expanded          # always open
    activity: collapsed      # opt back IN to the activity panel (hidden by default)
  mouse_tracking: true       # disable if your terminal conflicts with mouse reporting
```

运行时切换：

- `/details [hidden|collapsed|expanded|cycle]` — 设置全局模式
- `/details &lt;section&gt; [hidden|collapsed|expanded|reset]` — 覆盖某个节
  （节：`thinking`、`tools`、`subagents`、`activity`）

**默认可见性**

TUI 为各节设定了有主见的默认值，将回合流式呈现为实时转录，而不是一堆折叠箭头：

- `thinking` — **expanded**。模型发出推理时，推理内容直接内联流式显示。
- `tools` — **expanded**。工具调用及其结果直接展开显示。
- `subagents` — 降级到全局 `details_mode`（默认折叠在折叠箭头下——在真正发生委托之前保持安静）。
- `activity` — **hidden**。背景元信息（gateway 提示、终端一致性提醒、后台通知）在大多数日常使用中是干扰。工具失败仍会在失败工具行内渲染；背景错误/警告通过浮动警报后备机制呈现（当所有面板都隐藏时）。

按节覆盖优先于节默认值和全局 `details_mode`。要更改布局：

- `display.sections.thinking: collapsed` — 将思考放回折叠箭头下
- `display.sections.tools: collapsed` — 将工具调用放回折叠箭头下
- `display.sections.activity: collapsed` — 重新启用活动面板
- 运行时使用 `/details &lt;section&gt; &lt;mode&gt;`

任何在 `display.sections` 中显式设置的项都会覆盖默认值，因此现有配置无需更改即可继续使用。

<a id="sessions"></a>
## 会话

会话在 TUI 和经典 CLI 之间共享——两者都写入同一个 `~/.hermes/state.db`。你可以在一个中启动会话，在另一个中恢复。会话选择器会显示来自两个来源的会话，并带有来源标签。

关于生命周期、搜索、压缩和导出，请参见[会话](sessions.md)。

<a id="attaching-to-a-running-gateway"></a>
## 连接到正在运行的 gateway

默认情况下，TUI 会生成自己的进程内 gateway，因此每个 TUI 实例都是独立的。如果你已经有一个长时间运行的 gateway 在运行（例如在 tmux 中运行 `hermes gateway run`，或作为 systemd / launchd 服务），你可以让 TUI 指向那个 gateway——这样 TUI 就变成了一个瘦客户端，并与连接到同一个 gateway 的其他所有界面（消息平台、网页仪表盘、其他 TUI 会话）共享状态。
启动前通过环境变量设置 WebSocket URL：

```bash
export HERMES_TUI_GATEWAY_URL="ws://localhost:8765/api/ws?token=<auth-token>"
hermes --tui
```

token 来自网关的 API 认证配置（参见 [API 服务器](features/api-server.md)）。设置环境变量后，TUI 会：

- 完全跳过启动本地网关——不会重复加载平台适配器，也不会产生端口冲突。
- 将所有操作（斜杠命令、图片附件、浏览器进度、语音事件等）通过 WebSocket 路由到共享网关。
- 如果在请求之间网关 URL 发生变化（新 token），会自动重新连接。

这与 Web 仪表盘内嵌 TUI 使用的通道相同（参见 [Web 仪表盘](features/web-dashboard.md#chat)）——一个网关，多个客户端。

<a id="reverting-to-the-classic-cli"></a>
## 回退到经典 CLI

启动 `hermes`（不带 `--tui`）会停留在经典 CLI。如果希望某台机器优先使用 TUI，可以在 shell 配置文件中设置 `HERMES_TUI=1`。要恢复，取消设置即可。

如果 TUI 启动失败（没有 Node、缺少 bundle、TTY 问题），Hermes 会打印诊断信息并回退——而不是让你卡住。

<a id="see-also"></a>
## 另请参阅

- [CLI 界面](cli.md) —— 完整的斜杠命令和快捷键参考（共享）
- [会话](sessions.md) —— 恢复、分支和历史
- [皮肤与主题](features/skins.md) —— 自定义横幅、状态栏和覆盖层主题
- [语音模式](features/voice-mode.md) —— 两种界面均支持
- [配置](configuration.md) —— 所有配置项
