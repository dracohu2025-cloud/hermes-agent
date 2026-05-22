---
sidebar_position: 2
title: "TUI"
description: "启动 Hermes 的现代化终端用户界面——支持鼠标操作、丰富的覆盖层和非阻塞输入。"
---

<a id="tui"></a>
# TUI

TUI 是 Hermes 的现代化前端——一个基于与 [经典 CLI](cli.md) 相同 Python 运行时的终端用户界面。相同的 Agent、相同的会话、相同的斜杠命令；一个更简洁、响应更快的交互界面。

这是交互式运行 Hermes 的推荐方式。

<a id="launch"></a>
## 启动

```bash
# 启动 TUI
hermes --tui

# 恢复最新的 TUI 会话（若不存在则回退到最新的经典会话）
hermes --tui -c
hermes --tui --continue

# 通过 ID 或标题恢复特定会话
hermes --tui -r 20260409_000000_aa11bb
hermes --tui --resume "my t0p session"

# 直接运行源代码——跳过预构建步骤（供 TUI 贡献者使用）
hermes --tui --dev
```

你也可以通过环境变量启用它：

```bash
export HERMES_TUI=1
hermes          # 现在使用 TUI
hermes chat     # 同上
```

经典 CLI 仍作为默认选项可用。[CLI 界面](cli.md) 中记录的所有内容——斜杠命令、快速命令、技能预加载、人格、多行输入、中断——在 TUI 中同样有效。

<a id="why-the-tui"></a>
## 为什么选择 TUI

- **即时首帧渲染**——横幅在应用完成加载前就已绘制，因此在 Hermes 启动时，终端永远不会感觉卡住。
- **非阻塞输入**——在会话准备就绪前即可输入并排队消息。你的第一条提示会在 Agent 上线时立即发送。
- **丰富的覆盖层**——模型选择器、会话选择器、批准和澄清提示都以模态面板形式呈现，而非内联流程。
- **实时会话面板**——工具和技能在初始化过程中逐步填充。
- **支持鼠标的选择**——拖动高亮文本时使用统一的背景色，而非 SGR 反色。使用终端的常规复制手势进行复制。
- **备用屏幕渲染**——差异更新意味着流式传输时无闪烁，退出后滚动历史记录无杂乱。
- **编辑器辅助功能**——长代码片段的内联粘贴折叠、`Cmd+V` / `Ctrl+V` 文本粘贴（带剪贴板图片回退）、括号粘贴安全机制，以及图片/文件路径附件规范化。

相同的 [皮肤](features/skins.md) 和 [人格](features/personality.md) 同样适用。在会话中使用 `/skin ares`、`/personality pirate` 切换，UI 会实时重绘。查看 [皮肤与主题](features/skins.md) 获取完整的可自定义键列表，以及哪些适用于经典 CLI 与 TUI——TUI 遵循横幅调色板、UI 颜色、提示符字形/颜色、会话显示、补全菜单、选择背景色、`tool_prefix` 和 `help_header`。

<a id="collapsible-banner-sections"></a>
### 可折叠的横幅区域

TUI 启动横幅将运行时信息分组到四个可折叠区域，每个区域标题旁都渲染有一个 `▸` / `▾` 箭头：

| 区域 | 默认状态 |
|---------|---------------|
| 工具 | 展开 |
| 技能 | 折叠 |
| 系统提示 | 折叠 |
| MCP 服务器 | 折叠 |

点击区域标题（或其箭头）的任何位置即可切换。工具列表默认展开，因为它是会话开始时最常检查的部分；技能、系统提示和 MCP 服务器默认折叠，这样即使你安装了数十个技能或连接了许多 MCP 服务器，横幅也能保持紧凑。状态是横幅实例本地的，因此下次启动会重置为默认值。

<a id="requirements"></a>
## 要求

- **Node.js** ≥ 20 —— TUI 作为从 Python CLI 启动的子进程运行。`hermes doctor` 会验证此项。
- **TTY** —— 与经典 CLI 一样，在非交互式环境中通过管道输入 stdin 或运行时会回退到单查询模式。

首次启动时，Hermes 会将 TUI 的 Node 依赖项安装到 `ui-tui/node_modules`（一次性，几秒钟）。后续启动很快。如果你拉取了新的 Hermes 版本，当源代码比分发版本新时，TUI 包会自动重建。

<a id="external-prebuild"></a>
### 外部预构建

分发预构建包的发行版（Nix、系统包）可以将 Hermes 指向它：

```bash
export HERMES_TUI_DIR=/path/to/prebuilt/ui-tui
hermes --tui
```

该目录必须包含 `dist/entry.js`。

<a id="keybindings"></a>
## 快捷键绑定

快捷键绑定与 [经典 CLI](cli.md#keybindings) 完全一致。唯一的行为差异：

- **鼠标拖动** 使用统一的选择背景色高亮文本。
- **`Cmd+V` / `Ctrl+V`** 首先尝试普通文本粘贴，然后回退到 OSC52/原生剪贴板读取，最后当剪贴板或粘贴的有效载荷解析为图片时附加图片。
- **`/terminal-setup`** 为本地 VS Code / Cursor / Windsurf 终端安装绑定，以便在 macOS 上获得更好的 `Cmd+Enter` 和撤销/重做对等性。
- **斜杠自动补全** 以带有描述的浮动面板形式打开，而非内联下拉菜单。
- **`Ctrl+X`** —— 当高亮显示一个已排队的消息（在 Agent 仍在运行时发送）时，将其从队列中删除。**`Esc`** 取消编辑并取消高亮而不删除。
- **`Ctrl+G` / `Ctrl+X Ctrl+E`** —— 在 `$EDITOR` 中打开当前输入缓冲区，用于多行/长提示符编辑；保存并退出会将内容作为提示符发送回来。

<a id="slash-commands"></a>
## 斜杠命令

所有斜杠命令功能不变。少数几个是 TUI 特有的——它们产生更丰富的输出或渲染为覆盖层而非内联面板：

| 命令 | TUI 行为 |
|---------|--------------|
| `/help` | 带有分类命令的覆盖层，支持箭头键导航 |
| `/sessions` | 模态会话选择器——预览、标题、令牌总数、内联恢复 |
| `/model` | 按提供商分组的模态模型选择器，带有成本提示 |
| `/skin` | 实时预览——浏览时应用主题更改 |
| `/details` | 切换详细工具调用详情（全局或按部分） |
| `/usage` | 丰富的令牌/成本/上下文面板 |
| `/agents` (别名 `/tasks`) | 可观测性覆盖层——实时子 Agent 树，带有终止/暂停控制、每分支成本/令牌/文件汇总、逐轮历史记录 |
| `/reload` | 将 `~/.hermes/.env` 重新读入正在运行的 TUI 进程，以便新添加的 API 密钥无需重启即可生效 |
| `/mouse [on\|off\|toggle\|wheel\|buttons\|all]` | 在运行时选择鼠标跟踪预设（同时持久化到 `config.yaml` 中的 `display.mouse_tracking`）。`wheel` (1000+1006) 保持滚轮滚动，而不会产生使 tmux 在提示行上刷屏“剪贴板中无图片”的悬停事件；`buttons` 添加拖动选择；`all` 是默认设置，带有悬停驱动的 UI。 |

其他所有斜杠命令（包括已安装的技能、快速命令和人格切换）与经典 CLI 的工作方式相同。参见 [斜杠命令参考](../reference/slash-commands.md)。

<a id="latex-math-rendering"></a>
## LaTeX 数学公式渲染

TUI 的 Markdown 流水线会内联渲染 LaTeX 数学公式：`$E = mc^2$` 和 `$$\frac{a}{b}$$` 会渲染为 Unicode 格式的数学公式，而非原始的 TeX 源代码。适用于内联和块级数学公式；不支持的语法会回退到显示包裹在代码片段中的字面 TeX，以便仍可复制。

此功能始终开启——无需配置。经典 CLI 保留原始 TeX。

<a id="light-terminal-detection"></a>
## 浅色终端检测

TUI 自动检测浅色终端并相应地切换到浅色主题。检测分三层进行：

1. `HERMES_TUI_THEME` 环境变量——最高优先级。值：`light`、`dark` 或原始的 6 字符背景十六进制值（例如 `ffffff`、`1a1a2e`）。
2. `COLORFGBG` 环境变量——经典的“我的背景色是什么？”提示，由 xterm 派生的终端使用。
3. 通过 OSC 11 进行的终端背景探测——适用于未设置 `COLORFGBG` 的现代终端（Ghostty、Warp、iTerm2、WezTerm、Kitty）。

如果你希望无论终端如何都永久使用浅色主题：

```bash
export HERMES_TUI_THEME=light
```

<a id="busy-indicator-styles"></a>
## 忙碌指示器样式

状态栏的忙碌指示器是可插拔的——默认在 Agent 工作时每 2.5 秒轮换 Hermes 的 kawaii 表情调色板。通过配置或 `/indicator` 斜杠命令选择不同的样式：

```yaml
display:
  tui_status_indicator: kaomoji   # kaomoji | emoji | unicode | ascii
```

或在会话中：`/indicator emoji`（等等）。样式附带匹配的字形宽度，因此状态栏的其余部分在轮换时不会抖动。

<a id="auto-resume"></a>
## 自动恢复

默认情况下，`hermes --tui` 每次启动都会创建一个新会话。要自动重新连接到最近的 TUI 会话（当你的终端或 SSH 连接意外断开时很有用），请选择启用：
```bash
export HERMES_TUI_RESUME=1          # 最近的 TUI 会话
# 或者：
export HERMES_TUI_RESUME=<session-id>   # 指定会话
```

取消设置该变量或在每次启动时显式传递 `--resume &lt;id&gt;` 来覆盖。

<a id="status-line"></a>
## 状态行

TUI 的状态行实时跟踪 Agent 状态：

| 状态 | 含义 |
|--------|---------|
| `starting agent…` | 会话 ID 已激活；工具和技能仍在启动中。你可以输入——消息会排队并在准备好时发送。 |
| `ready` | Agent 空闲，接受输入。 |
| `thinking…` / `running…` | Agent 正在推理或运行工具。 |
| `interrupted` | 当前回合被取消；按 Enter 键重新发送。 |
| `forging session…` / `resuming…` | 初始连接或 `--resume` 握手。 |

每个皮肤的状态栏颜色和阈值与经典 CLI 共享——自定义请参见 [皮肤](features/skins.md)。

状态行还显示：

- **工作目录与 git 分支** — `~/projects/hermes-agent (docs/two-week-gap-sweep)`。当你在侧边终端执行 `git checkout` 时，分支后缀会更新（基于修改时间缓存），因此 TUI 反映的是你实际的活动分支，而不是启动时的分支。
- **每个提示的耗时** — `⏱ 12s/3m 45s` 在回合运行时（实时），回合完成后冻结为 `⏲ 32s / 3m 45s`。第一个数字是自上次用户消息以来的时间；第二个是会话总时长。每次新提示时重置。
- **`🗜️ N`** — 运行会话已自动压缩的次数。首次压缩触发后出现。
- **`▶ N`** — 当前会话中正在运行的 `/background` 任务数量。只要有至少一个任务在执行，就会出现。
- **`⚠ YOLO`** — YOLO 模式开启时（`hermes --yolo`、`/yolo` 或 `HERMES_YOLO_MODE=1`）显示的警告。同样的徽章也会出现在启动横幅中，因此你不会无意中启动一个自动批准的会话。

<a id="configuration"></a>
## 配置

TUI 遵循所有 Hermes 标准配置：`~/.hermes/config.yaml`、配置文件、个性、皮肤、快捷命令、凭证池、记忆提供者、工具/技能启用。没有 TUI 专用的配置文件。

少数键专门调整 TUI 界面：

```yaml
display:
  skin: default              # 任何内置或自定义皮肤
  personality: helpful
  details_mode: collapsed    # hidden | collapsed | expanded — 全局折叠面板默认状态
  sections:                  # 可选：按面板覆盖（任何子集）
    thinking: expanded       # 始终展开
    tools: expanded          # 始终展开
    activity: collapsed      # 重新启用活动面板（默认隐藏）
  mouse_tracking: all        # off | wheel | buttons | all (或 true/false 向后兼容)。
                             #   wheel   — 1000+1006（滚动 + 点击；无拖拽，无悬停 —
                             #             在 tmux 内推荐使用，以避免悬停事件导致的提示行
                             #             “剪贴板中没有图像”的垃圾信息）
                             #   buttons — 添加 1002 用于终端侧的拖拽选择
                             #   all     — 添加 1003 用于悬停（滚动条悬停分页、
                             #             链接鼠标进入等）
```

运行时切换：

- `/details [hidden|collapsed|expanded|cycle]` — 设置全局模式
- `/details &lt;section&gt; [hidden|collapsed|expanded|reset]` — 覆盖一个面板
  （面板：`thinking`、`tools`、`subagents`、`activity`）

**默认可见性**

TUI 附带预设的按面板默认值，将回合作为实时转录流式显示，而不是一堆折叠符号：

- `thinking` — **展开**。推理流在模型输出时内联显示。
- `tools` — **展开**。工具调用及其结果以展开状态渲染。
- `subagents` — 遵循全局 `details_mode`（默认在折叠符号下折叠——保持安静直到实际发生委派）。
- `activity` — **隐藏**。环境元数据（网关提示、终端一致性提醒、后台通知）对于大多数日常使用来说是噪音。工具失败仍然在失败的工具行上内联渲染；当所有面板都隐藏时，环境错误/警告通过浮动警报兜底机制显示。

按面板覆盖优先于面板默认值和全局 `details_mode`。要重塑布局：

- `display.sections.thinking: collapsed` — 将推理恢复到折叠符号下
- `display.sections.tools: collapsed` — 将工具调用恢复到折叠符号下
- `display.sections.activity: collapsed` — 重新启用活动面板
- `/details &lt;section&gt; &lt;mode&gt;` 运行时

任何在 `display.sections` 中明确设置的内容都会覆盖默认值，因此现有配置可以保持不变地工作。

<a id="sessions"></a>
## 会话

会话在 TUI 和经典 CLI 之间共享——两者都写入同一个 `~/.hermes/state.db`。你可以在一个中启动会话，在另一个中恢复。会话选择器会显示来自两个源的会话，并带有源标签。

有关生命周期、搜索、压缩和导出，请参见 [会话](sessions.md)。

<a id="attaching-to-a-running-gateway"></a>
## 连接到正在运行的网关

默认情况下，TUI 会启动自己的进程内网关，因此每个 TUI 实例都是独立的。如果你已经有一个长期运行的网关（例如 tmux 中的 `hermes gateway run`，或 systemd / launchd 服务），你可以将 TUI 指向该网关——TUI 随后变成一个瘦客户端，并与连接到同一网关的所有其他界面（消息平台、Web 仪表板、其他 TUI 会话）共享状态。

在启动前通过环境变量设置 websocket URL：

```bash
export HERMES_TUI_GATEWAY_URL="ws://localhost:8765/api/ws?token=<auth-token>"
hermes --tui
```

令牌来自网关的 API 认证配置（参见 [API 服务器](features/api-server.md)）。当环境变量设置后，TUI：

- 完全跳过启动本地网关——没有重复的平台适配器，没有端口冲突。
- 通过 websocket 将每个操作（斜杠命令、图像附加、浏览器进度、语音事件……）路由到共享网关。
- 如果网关 URL 在请求之间轮换（新令牌），会自动重新连接。

这是 Web 仪表板嵌入式 TUI 使用的相同通道（参见 [Web 仪表板](features/web-dashboard.md#chat)）——一个网关，多个客户端。

<a id="reverting-to-the-classic-cli"></a>
## 恢复到经典 CLI

启动 `hermes`（不带 `--tui`）会保持在经典 CLI。要让机器优先使用 TUI，在你的 shell 配置文件中设置 `HERMES_TUI=1`。要恢复，取消设置它。

如果 TUI 启动失败（没有 Node、缺少捆绑包、TTY 问题），Hermes 会打印诊断信息并回退——而不是让你卡住。

<a id="see-also"></a>
## 另请参阅

- [CLI 界面](cli.md) — 完整的斜杠命令和键绑定参考（共享）
- [会话](sessions.md) — 恢复、分支和历史
- [皮肤与主题](features/skins.md) — 定制横幅、状态栏和覆盖层主题
- [语音模式](features/voice-mode.md) — 在两个界面中都可用
- [配置](configuration.md) — 所有配置键
