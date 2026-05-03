---
sidebar_position: 2
title: "TUI"
description: "启动 Hermes 的现代终端界面——支持鼠标操作、丰富的浮层面板以及非阻塞输入。"
---

# TUI {#tui}

TUI 是 Hermes 的现代前端——一个基于终端界面的 UI，底层使用与[经典 CLI](cli.md) 相同的 Python 运行时。相同的 Agent、相同的会话、相同的斜杠命令；只是提供了一个更干净、响应更快的交互界面。

这是以交互方式运行 Hermes 的推荐方式。

## 启动 {#launch}

```bash
# 启动 TUI
hermes --tui

# 恢复最近的 TUI 会话（如果不存在则回退到最近的经典会话）
hermes --tui -c
hermes --tui --continue

# 按 ID 或标题恢复指定会话
hermes --tui -r 20260409_000000_aa11bb
hermes --tui --resume "my t0p session"

# 直接运行源码——跳过预构建步骤（适用于 TUI 贡献者）
hermes --tui --dev
```

你也可以通过环境变量启用：

```bash
export HERMES_TUI=1
hermes          # 现在使用 TUI
hermes chat     # 同上
```

经典 CLI 仍然是默认选项。[CLI 接口](cli.md) 中记录的所有功能——斜杠命令、快速命令、技能预加载、人格设定、多行输入、中断——在 TUI 中完全一致。

## 为什么选择 TUI {#why-the-tui}

- **即时首帧** —— 应用加载完成前横幅就已渲染，因此 Hermes 启动时终端不会感觉卡住。
- **非阻塞输入** —— 在会话就绪前即可输入并排队消息。Agent 上线的那一刻，你的第一条提示就会立即发送。
- **丰富的浮层面板** —— 模型选择器、会话选择器、审批和澄清提示都以模态面板形式呈现，而非内联流程。
- **实时会话面板** —— 工具和技能在初始化过程中逐步填充显示。
- **鼠标友好选择** —— 拖拽高亮时使用统一背景色，而非 SGR 反色。使用终端正常的复制手势即可复制。
- **备用屏幕渲染** —— 差分更新意味着流式输出时无闪烁，退出后无回滚杂乱。
- **编辑器辅助功能** —— 长代码片段的内联粘贴折叠、`Cmd+V` / `Ctrl+V` 文本粘贴并支持剪贴板图片回退、括号粘贴安全保护，以及图片/文件路径附件规范化。

同样的[皮肤](features/skins.md)和[人格设定](features/personality.md)也适用。在会话中通过 `/skin ares`、`/personality pirate` 切换，UI 会实时重绘。可自定义的键及其在经典 CLI 与 TUI 中的适用情况，请参见[皮肤与主题](features/skins.md)——TUI 支持横幅调色板、UI 颜色、提示符字形/颜色、会话显示、补全菜单、选中背景色、`tool_prefix` 和 `help_header`。

## 系统要求 {#requirements}

- **Node.js** ≥ 20 —— TUI 作为 Python CLI 启动的子进程运行。`hermes doctor` 会验证此项。
- **TTY** —— 与经典 CLI 一样，如果 stdin 被管道化或在非交互环境中运行，将回退到单查询模式。

首次启动时，Hermes 会将 TUI 的 Node 依赖安装到 `ui-tui/node_modules`（一次性操作，耗时数秒）。后续启动会很快。如果你拉取了新版本的 Hermes，当源码比 dist 更新时，TUI 包会自动重新构建。

### 外部预构建 {#external-prebuild}
提供预构建包的分发版（Nix、系统包）可以将 Hermes 指向该路径：

```bash
export HERMES_TUI_DIR=/path/to/prebuilt/ui-tui
hermes --tui
```

该目录必须包含 `dist/entry.js` 和最新的 `node_modules`。

## 快捷键 {#keybindings}

快捷键与[经典 CLI](cli.md#keybindings) 完全一致。仅有的行为差异：

- **鼠标拖拽** 使用统一的选中背景高亮文本。
- **`Cmd+V` / `Ctrl+V`** 首先尝试普通文本粘贴，然后回退到 OSC52/原生剪贴板读取，最后当剪贴板或粘贴内容解析为图片时进行图片附加。
- **`/terminal-setup`** 安装本地 VS Code / Cursor / Windsurf 终端绑定，在 macOS 上实现更好的 `Cmd+Enter` 和撤销/重做一致性。
- **斜杠自动补全** 以浮动面板形式打开并显示描述，而非内联下拉菜单。
- **`Ctrl+X`** — 当队列中的消息被高亮时（在 Agent 仍在运行时发送），将其从队列中删除。**`Esc`** 取消编辑并取消高亮，但不删除。
- **`Ctrl+G` / `Ctrl+X Ctrl+E`** — 在 `$EDITOR` 中打开当前输入缓冲区，用于多行/长提示词编写；保存并退出会将内容作为提示词发送回去。

## 斜杠命令 {#slash-commands}

所有斜杠命令均保持不变。部分命令由 TUI 专属实现——它们会生成更丰富的输出，或以覆盖层形式呈现而非内联面板：

| 命令 | TUI 行为 |
|---------|--------------|
| `/help` | 覆盖层，显示分类命令，支持方向键导航 |
| `/sessions` | 模态会话选择器——预览、标题、Token 总数、内联恢复 |
| `/model` | 模态模型选择器，按提供商分组，附带成本提示 |
| `/skin` | 实时预览——浏览时主题更改即时生效 |
| `/details` | 切换详细工具调用详情（全局或按部分） |
| `/usage` | 丰富的 Token/成本/上下文面板 |
| `/agents`（别名 `/tasks`） | 可观测性覆盖层——实时子 Agent 树，带终止/暂停控制、按分支的成本/Token/文件汇总、逐轮历史 |
| `/reload` | 重新读取 `~/.hermes/.env` 到运行中的 TUI 进程，使新添加的 API 密钥无需重启即可生效 |
| `/mouse` | 运行时切换鼠标跟踪开关（也会持久化到 `config.yaml` 的 `display.mouse_tracking` 中） |

所有其他斜杠命令（包括已安装的技能、快速命令和个性切换）与经典 CLI 完全相同。请参阅[斜杠命令参考](../reference/slash-commands.md)。

## LaTeX 数学渲染 {#latex-math-rendering}

TUI 的 Markdown 管道内联渲染 LaTeX 数学公式：`$E = mc^2$` 和 `$$\frac{a}{b}$$` 会渲染为 Unicode 格式的数学公式，而非原始 TeX 源码。支持内联和块级数学公式；不支持的语法会回退为显示包裹在代码跨度中的字面 TeX，以便保持可复制性。

此功能始终开启——无需配置。经典 CLI 保留原始 TeX。

## 浅色终端检测 {#light-terminal-detection}

TUI 自动检测浅色终端并相应切换到浅色主题。检测分三层进行：

1. `HERMES_TUI_THEME` 环境变量——最高优先级。值：`light`、`dark`，或原始 6 字符背景十六进制值（例如 `ffffff`、`1a1a2e`）。
2. `COLORFGBG` 环境变量——xterm 衍生终端使用的经典“我的背景颜色是什么？”提示。
3. 通过 OSC 11 进行终端背景探测——适用于未设置 `COLORFGBG` 的现代终端（Ghostty、Warp、iTerm2、WezTerm、Kitty）。
如果你希望无论终端设置如何都永久使用浅色主题：

```bash
export HERMES_TUI_THEME=light
```

## 忙碌指示器样式 {#busy-indicator-styles}

状态栏的 FaceTicker 是可插拔的——默认情况下，在 Agent 工作期间，每 2.5 秒轮换一次 Hermes 的可爱表情调色板。通过配置选择不同的样式（或使用 `none` 显示最小圆点）：

```yaml
display:
  busy_indicator:
    style: kawaii     # kawaii | minimal | dots | wings | none
```

每种样式都配有匹配的字符宽度，这样状态栏的其余部分在轮换时不会抖动。

## 自动恢复 {#auto-resume}

默认情况下，`hermes --tui` 每次启动都会创建一个新会话。要自动重新连接到最近的 TUI 会话（当终端或 SSH 连接意外断开时很有用），请选择启用：

```bash
export HERMES_TUI_RESUME=1          # 最近的 TUI 会话
# 或者：
export HERMES_TUI_RESUME=<session-id>   # 指定会话
```

取消设置该变量或显式传递 `--resume &lt;id&gt;` 以在每次启动时覆盖。

## 状态行 {#status-line}

TUI 的状态行实时跟踪 Agent 状态：

| 状态 | 含义 |
|--------|---------|
| `starting agent…` | 会话 ID 已激活；工具和技能仍在加载中。你可以输入——消息会排队并在就绪时发送。 |
| `ready` | Agent 空闲，接受输入。 |
| `thinking…` / `running…` | Agent 正在推理或运行工具。 |
| `interrupted` | 当前轮次已取消；按 Enter 重新发送。 |
| `forging session…` / `resuming…` | 初始连接或 `--resume` 握手。 |

每种皮肤的状态栏颜色和阈值与经典 CLI 共享——请参阅 [Skins](features/skins.md) 了解自定义设置。

状态行还显示：

- **带 git 分支的工作目录** — `~/projects/hermes-agent (docs/two-week-gap-sweep)`。当你在侧边终端执行 `git checkout` 时，分支后缀会更新（基于 mtime 缓存），因此 TUI 反映的是你实际活动的分支，而不是启动时的分支。
- **每次提示的已用时间** — 轮次运行时（实时）显示 `⏱ 12s/3m 45s`，轮次完成后冻结为 `⏲ 32s / 3m 45s`。第一个数字是自上次用户消息以来的时间；第二个是会话总持续时间。每次新提示都会重置。

## 配置 {#configuration}

TUI 遵循所有标准 Hermes 配置：`~/.hermes/config.yaml`、配置文件、个性、皮肤、快速命令、凭据池、记忆提供者、工具/技能启用。不存在 TUI 特定的配置文件。

一些键专门调整 TUI 界面：

```yaml
display:
  skin: default              # 任何内置或自定义皮肤
  personality: helpful
  details_mode: collapsed    # hidden | collapsed | expanded — 全局手风琴默认值
  sections:                  # 可选：按部分覆盖（任意子集）
    thinking: expanded       # 始终展开
    tools: expanded          # 始终展开
    activity: collapsed      # 重新启用活动面板（默认隐藏）
  mouse_tracking: true       # 如果终端与鼠标报告冲突，请禁用
```

运行时切换：

- `/details [hidden|collapsed|expanded|cycle]` — 设置全局模式
- `/details &lt;section&gt; [hidden|collapsed|expanded|reset]` — 覆盖某个部分
  （部分：`thinking`、`tools`、`subagents`、`activity`）
**默认可见性**

TUI 为每个区域预设了默认的可见性，将对话过程以实时转录的形式呈现，而不是一堵箭头墙：

- `thinking` — **展开**。模型输出推理过程时，会以内联方式实时显示。
- `tools` — **展开**。工具调用及其结果会以展开状态显示。
- `subagents` — 回退到全局 `details_mode`（默认情况下折叠在箭头下——在真正发生委派之前保持静默）。
- `activity` — **隐藏**。环境元信息（网关提示、终端一致性提醒、后台通知）对大多数日常使用来说是噪音。工具失败时仍会在出错的工具行内联显示；当所有面板都隐藏时，环境错误/警告会通过浮动警报兜底机制呈现。

每个区域的单独设置优先级高于该区域的默认设置和全局 `details_mode`。要调整布局：

- `display.sections.thinking: collapsed` — 将思考过程放回箭头下
- `display.sections.tools: collapsed` — 将工具调用放回箭头下
- `display.sections.activity: collapsed` — 重新启用活动面板
- 运行时使用 `/details &lt;section&gt; &lt;mode&gt;`

任何在 `display.sections` 中显式设置的值都会覆盖默认值，因此现有配置可以保持不变地继续工作。

## 会话 {#sessions}

会话在 TUI 和经典 CLI 之间共享——两者都写入同一个 `~/.hermes/state.db` 文件。你可以在一个界面中启动会话，在另一个界面中恢复。会话选择器会显示来自两个来源的会话，并带有来源标签。

有关生命周期、搜索、压缩和导出，请参阅[会话](sessions.md)。

## 回退到经典 CLI {#reverting-to-the-classic-cli}

启动 `hermes`（不带 `--tui`）会停留在经典 CLI。要让某台机器优先使用 TUI，请在 shell 配置文件中设置 `HERMES_TUI=1`。要恢复，取消设置即可。

如果 TUI 启动失败（没有 Node、缺少 bundle、TTY 问题），Hermes 会打印诊断信息并回退——而不是让你卡住。

## 另请参阅 {#see-also}

- [CLI 界面](cli.md) — 完整的斜杠命令和快捷键参考（共享）
- [会话](sessions.md) — 恢复、分支和历史
- [皮肤与主题](features/skins.md) — 自定义横幅、状态栏和主题
- [语音模式](features/voice-mode.md) — 在两个界面中均可使用
- [配置](configuration.md) — 所有配置键
