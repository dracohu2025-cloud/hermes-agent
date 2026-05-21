---
title: "Windows（原生）指南 — 早期 Beta"
description: "早期 BETA：在 Windows 10 / 11 上原生运行 Hermes Agent — 安装、功能矩阵、UTF-8 控制台、Git Bash、作为计划任务的网关、编辑器处理、PATH、卸载和常见陷阱"
sidebar_label: "Windows（原生）— Beta"
sidebar_position: 3
---

<a id="windows-native-guide-early-beta"></a>
# Windows（原生）指南 — 早期 Beta

:::warning 早期 BETA
原生 Windows 支持目前处于**早期 beta** 阶段。它可以安装、运行，并且通过了我们的 Windows-footgun lint 检查，但尚未像 Linux/macOS/WSL2 路径那样经过大规模实际测试。预计会存在一些粗糙边缘——尤其是在子进程处理、路径怪癖和非 ASCII 控制台输出方面。遇到问题时，请附上复现步骤[提交 issue](https://github.com/NousResearch/hermes-agent/issues)。如果你现在想要一个经过实战检验的配置，请改用 [WSL2 下的 Linux/macOS 安装程序](./windows-wsl-quickstart.md)。
<a id="early-beta"></a>
:::

Hermes 可以在 Windows 10 和 Windows 11 上原生运行——无需 WSL、无需 Cygwin、无需 Docker。本页是深度指南：哪些功能原生可用，哪些只有 WSL 才支持，安装程序实际做了什么，以及你可能需要调整的 Windows 专属旋钮。

如果你只想安装，[首页](/)或[安装页面](../getting-started/installation#windows-native-powershell--early-beta)上的一行命令就足够了。当遇到意外情况时，再回到这里查看。

:::tip 想要使用 WSL？
如果你更喜欢真正的 POSIX 环境（用于仪表板的嵌入式终端、`fork` 语义、Linux 风格的文件监视器等），请参阅 **[Windows（WSL2）指南](./windows-wsl-quickstart.md)**。两者可以干净地共存：原生数据位于 `%LOCALAPPDATA%\hermes`，WSL 数据位于 `~/.hermes`。
<a id="want-wsl-instead"></a>
:::

<a id="quick-install"></a>
## 快速安装

打开 **PowerShell**（或 Windows Terminal）并运行：

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

无需管理员权限。安装程序会安装到 `%LOCALAPPDATA%\hermes\` 目录，并将 `hermes` 添加到你的**用户 PATH** 中——完成后打开一个新终端。

**安装程序选项**（需要脚本块形式来传递参数）：

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1))) -NoVenv -SkipSetup -Branch main
```

| 参数 | 默认值 | 用途 |
|---|---|---|
| `-Branch` | `main` | 克隆特定分支（用于测试 PR 时有用） |
| `-Commit` | 未设置 | 固定安装到特定的提交 SHA（覆盖 `-Branch`） |
| `-Tag` | 未设置 | 固定安装到特定的 git 标签（例如 `v0.14.0`） |
| `-NoVenv` | 关闭 | 跳过虚拟环境创建（高级——你自行管理 Python） |
| `-SkipSetup` | 关闭 | 跳过安装后的 `hermes setup` 向导 |
| `-HermesHome` | `%LOCALAPPDATA%\hermes` | 覆盖数据目录 |
| `-InstallDir` | `%LOCALAPPDATA%\hermes\hermes-agent` | 覆盖代码位置 |

安装程序会自动重试不稳定的 git 拉取操作，并去除任何下载的 `install.ps1` 负载中的 BOM，这样通过 HTTP 传输时产生的 UTF-8 BOM 就不会再破坏 `[scriptblock]::Create((irm ...))` 形式。

<a id="desktop-installer-alternative"></a>
### 桌面安装程序（备选）

此外还提供了一个轻量级的 GUI 安装程序——如果你更愿意双击 `.exe` 而不是打开 PowerShell，这会很方便。下载 Hermes Desktop，运行安装程序，首次启动时 GUI 会在后台调用 `install.ps1` 来准备 Python（通过 `uv`）、Node、PortableGit 以及下面描述的其他依赖引导程序。首次运行后，桌面应用和通过 PowerShell 安装的 `hermes` CLI 共享同一个 `%LOCALAPPDATA%\hermes\hermes-agent` 安装目录和 `%USERPROFILE%\.hermes` 数据目录——你可以在 GUI 和 CLI 之间自由切换。
当你想要使用熟悉的 Windows 安装体验，或者将 Hermes 交给非开发者使用时，请使用桌面安装程序；如果你已经在终端中，请使用 PowerShell 一行命令。

<a id="dependency-bootstrap-depensure"></a>
### 依赖引导（`dep_ensure`）

首次启动时（以及在检测到缺少工具时按需运行），Hermes 会运行一个小型的 Python 引导脚本——`hermes_cli/dep_ensure.py`——它会检查并延迟安装所需的非 Python 依赖项。在 Windows 上，相关的依赖项如下：

| 依赖项 | Hermes 为什么需要它 |
|---|---|
| **PortableGit** | 为终端工具提供 `bash.exe`，并为会话内的克隆操作提供 `git`。在安装时预置，不由 `dep_ensure` 处理。 |
| **Node.js 22** | 浏览器工具（`agent-browser`）、TUI 的 Web 桥接以及 WhatsApp 桥接所需。 |
| **ffmpeg** | 用于 TTS / 语音消息的音频格式转换。 |
| **ripgrep** | 快速文件搜索——如果不可用则回退到 `grep`。 |
| **npm 包** | `agent-browser`、Playwright Chromium 以及每个工具集所需的 Node 依赖项，在首次使用浏览器工具时一次性安装。 |

每个依赖项都有一个 `shutil.which(...)` 风格的检查；如果某个二进制文件缺失且运行环境为交互式，`dep_ensure` 会提供安装选项（实际安装逻辑委托给 `scripts\install.ps1 -ensure &lt;dep&gt;`）。非交互式运行（网关、定时任务、无头桌面启动）会跳过提示，并给出清晰的错误信息：“此功能需要 `<dep>`”。

<a id="what-the-installer-actually-does"></a>
## 安装程序实际执行的操作

自上而下，按顺序进行：

1. **引导 `uv`** —— Astral 的快速 Python 管理器。安装到 `%USERPROFILE%\.local\bin`。
2. **通过 `uv` 安装 Python 3.11**。无需已有 Python。
3. **安装 Node.js 22**（如果可用则使用 winget，否则在 `%LOCALAPPDATA%\hermes\node` 下解压便携版 Node tarball）。用于浏览器工具和 WhatsApp 桥接。
4. **安装便携版 Git** —— 如果 `git` 已在 PATH 中，安装程序会直接使用它；否则会从官方的 `git-for-windows` 发布版下载一个精简的自包含 **PortableGit**（约 45 MB）到 `%LOCALAPPDATA%\hermes\git`。无需管理员权限，不写入 Windows 安装程序注册表，不会干扰系统上的其他任何东西。
5. **克隆仓库**到 `%LOCALAPPDATA%\hermes\hermes-agent` 并在其中创建虚拟环境。
6. **分层 `uv pip install`** —— 首先尝试 `.[all]`，如果某个 `git+https` 依赖因 GitHub 限速而失败，则逐步回退到较小的集合（`[messaging,dashboard,ext]` → `[messaging]` → `.`）。防止“单个依赖失败导致整个安装降级”的故障模式。
7. **根据 `.env` 文件自动安装消息 SDK** —— 如果存在 `TELEGRAM_BOT_TOKEN` / `DISCORD_BOT_TOKEN` / `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` / `WHATSAPP_ENABLED`，则运行 `python -m ensurepip --upgrade` 并执行针对性的 `pip install` 调用，以确保各平台的 SDK 可以实际导入。
8. **设置 `HERMES_GIT_BASH_PATH`** 为已解析的 `bash.exe` 路径，这样 Hermes 在新的 shell 中也能确定性地找到它。
9. **将 `%LOCALAPPDATA%\hermes\bin` 添加到用户 PATH** —— 在新终端打开后即可使用 `hermes` 命令。
10. **运行 `hermes setup`** —— 常规首次启动向导（模型、提供商、工具集）。使用 `-SkipSetup` 可跳过。
<a id="feature-matrix"></a>
## 功能矩阵

除了仪表盘的嵌入式终端面板外，所有功能均能在 Windows 上原生运行。

| 功能 | 原生 Windows | WSL2 |
|---|---|---|
| CLI（`hermes chat`、`hermes setup`、`hermes gateway` 等） | ✓ | ✓ |
| 交互式 TUI（`hermes --tui`） | ✓ | ✓ |
| 消息网关（Telegram、Discord、Slack、WhatsApp 等 15+ 平台） | ✓ | ✓ |
| Cron 调度器 | ✓ | ✓ |
| 浏览器工具（通过 Node 使用 Chromium） | ✓ | ✓ |
| MCP 服务器（stdio 和 HTTP） | ✓ | ✓ |
| 本地 Ollama / LM Studio / llama-server | ✓ | ✓（通过 WSL 网络） |
| Web 仪表盘（会话、任务、指标、配置） | ✓ | ✓ |
| 仪表盘 `/chat` 嵌入式终端面板 | ✗（需要 POSIX PTY） | ✓ |
| 登录时自动启动 | ✓（schtasks） | ✓（systemd） |

仪表盘的 `/chat` 选项卡通过 POSIX PTY（`ptyprocess`）嵌入了一个真实终端。原生 Windows 没有对应的底层机制；Python 的 `pywinpty` / Windows ConPTY 虽然能用，但需要单独实现——这里先列为未来工作。**其余仪表盘功能均能原生运行**——只有那个选项卡会显示“对此功能请使用 WSL2”的提示。

<a id="how-hermes-runs-shell-commands-on-windows"></a>
## Hermes 如何在 Windows 上运行 shell 命令

Hermes 的终端工具通过 **Git Bash** 运行命令，与 Claude Code 采用的策略相同。这绕过了 POSIX 与 Windows 之间的差异，无需重写每个工具。

`bash.exe` 的查找顺序：

1. 若设置了环境变量 `HERMES_GIT_BASH_PATH`，则直接使用。
2. `%LOCALAPPDATA%\hermes\git\usr\bin\bash.exe`（安装程序管理的 PortableGit）。
3. `%LOCALAPPDATA%\hermes\git\bin\bash.exe`（旧版 Git for Windows 布局）。
4. 系统安装的 Git for Windows（`%ProgramFiles%\Git\bin\bash.exe` 等路径）。
5. 最后尝试 MSYS2、Cygwin 或 PATH 上的任意 `bash.exe`。

安装程序会显式设置 `HERMES_GIT_BASH_PATH`，这样新建的 PowerShell 会话就不必重新查找。如果你想指定 Hermes 使用某个特定的 bash（例如系统 Git Bash，或通过符号链接指向 WSL 中的 bash），可以覆盖该变量。

**注意：** MinGit 的布局与完整版 Git for Windows 安装程序不同——bash 位于 `usr\bin\bash.exe`，而非 `bin\bash.exe`。Hermes 会同时检查这两个位置。如果你手动解压 MinGit zip，请确保选择 **非 busybox** 的版本（`MinGit-*-64-bit.zip`，而不是 `MinGit-*-busybox*.zip`）——busybox 版本内置的是 `ash` 而非 `bash`，并且大部分 coreutils 都不存在。

<a id="utf-8-console-on-windows"></a>
## Windows 上的 UTF-8 控制台

Python 在 Windows 上的默认 stdio 使用控制台的活动代码页（通常是 cp1252 或 cp437）。Hermes 的横幅、斜杠命令列表、工具输出、Rich 面板以及技能描述中均包含 Unicode。如果不做处理，任何这类输出都会崩溃，报错 `UnicodeEncodeError: 'charmap' codec can't encode character…`。

解决方案在 `hermes_cli/stdio.py::configure_windows_stdio()` 中，它在每个入口点（`cli.py::main`、`hermes_cli/main.py::main`、`gateway/run.py::main`）的早期阶段被调用。该函数：

1. 通过 `kernel32.SetConsoleCP` / `SetConsoleOutputCP` 将控制台代码页切换为 CP_UTF8（65001）。
2. 将 `sys.stdout` / `sys.stderr` / `sys.stdin` 重新配置为 UTF-8，并设置 `errors='replace'`。
3. 设置 `PYTHONIOENCODING=utf-8` 和 `PYTHONUTF8=1`（通过 `setdefault`，因此用户显式设置的值会优先），让子 Python 进程继承 UTF-8。
4. 如果既未设置 `EDITOR` 也未设置 `VISUAL`，则将 `EDITOR` 设为 `notepad`（参见下面的“编辑器”章节）。
幂等。在非 Windows 系统上无操作。

**选择退出：** 环境变量 `HERMES_DISABLE_WINDOWS_UTF8=1` 会回退到传统的 cp1252 stdio 路径。用于二分定位编码问题；正常操作下不太可能需要此设置。

<a id="the-editor-ctrl-x-ctrl-e-edit"></a>
## 编辑器（`Ctrl-X Ctrl-E`、`/edit`）

在 #21561 之前，在 Windows 上按 `Ctrl-X Ctrl-E` 或输入 `/edit` 会静默无反应。prompt_toolkit 有一个硬编码的 POSIX 绝对路径回退列表（`/usr/bin/nano`、`/usr/bin/pico`、`/usr/bin/vi` 等），该列表在 Windows 上永远无法解析——即使安装了完整的 Git for Windows 也是如此。

Hermes 的 Windows stdio 垫片现在默认设置 `EDITOR=notepad`。记事本随每个 Windows 安装附带，并且可以作为阻塞编辑器工作——`subprocess.call(["notepad", file])` 会阻塞直到窗口关闭。

**用户覆盖仍然优先**（它们会在设置默认值之前被检查）：

| 编辑器 | PowerShell 命令 |
|---|---|
| VS Code | `$env:EDITOR = "code --wait"` |
| Notepad++ | `$env:EDITOR = "'C:\Program Files\Notepad++\notepad++.exe' -multiInst -nosession"` |
| Neovim | `$env:EDITOR = "nvim"` |
| Helix | `$env:EDITOR = "hx"` |

VS Code 的 `--wait` 标志至关重要——没有它，编辑器会立即返回，Hermes 会得到一个空缓冲区。

在您的 PowerShell 配置文件中永久设置：

```powershell
# In $PROFILE
$env:EDITOR = "code --wait"
```

或者作为系统设置中的用户环境变量，以便每个新的 shell 都能读取它。

<a id="ctrl-enter-for-newline-in-the-cli"></a>
## CLI 中的 `Ctrl+Enter` 换行

Windows Terminal 将 `Ctrl+Enter` 作为专用键序列传递。Hermes 将其绑定为“插入换行”，这样您就可以在 CLI 中编写多行提示，而无需退回到先按 `Esc` 再按 `Enter`。适用于 Windows Terminal、VS Code 集成终端以及任何支持 VT 转义序列的现代 Windows 控制台主机。

在传统的 `cmd.exe` 控制台中，`Ctrl+Enter` 等同于普通 `Enter`——请改用 `Esc Enter`，或升级到 Windows Terminal（它免费且在 Windows 11 上默认安装）。

<a id="running-the-gateway-at-windows-login"></a>
## 在 Windows 登录时运行网关

在 Windows 上，`hermes gateway install` 使用**计划任务**，并回退到启动文件夹——无需管理员权限。

<a id="install"></a>
### Install

```powershell
hermes gateway install
```

幕后发生了什么：

1. `schtasks /Create /SC ONLOGON /RL LIMITED /TN HermesGateway` — 注册一个在登录时以标准（非提权）权限运行的任务。不会弹出 UAC 提示。
2. 如果 schtasks 被组策略阻止，则回退到将 `start /min cmd.exe /d /c &lt;wrapper&gt;` 快捷方式写入 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`。效果相同，但略微粗糙。
3. 通过 `pythonw.exe` **分离式**启动网关——而不是 `python.exe`。`pythonw.exe` 没有附加控制台，这使其免受来自兄弟进程的 `CTRL_C_EVENT` 广播影响（这是一个真实问题，曾经当你在同一进程组中 Ctrl+C 任何内容时都会杀死网关）。

启动时使用的标志：`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB`。

<a id="manage"></a>
### Manage

```powershell
hermes gateway status      # Merged view: schtasks + Startup folder + running PID
hermes gateway start       # Starts the scheduled task now
hermes gateway stop        # Graceful SIGTERM equivalent (TerminateProcess via psutil)
hermes gateway restart
hermes gateway uninstall   # Removes schtasks entry, Startup shortcut, pid file
```
`hermes gateway status` 是幂等的——连续调用一千次也不会意外杀死网关。（在 PR #21561 之前，它会通过 `os.kill(pid, 0)` 在 C 层面与 `CTRL_C_EVENT` 冲突而静默执行此操作——如果你关心背后的故事，请参阅下面的“进程管理内部机制”。）

<a id="why-not-a-windows-service"></a>
### 为什么不用 Windows 服务？

服务需要管理员权限才能安装，并且会将网关的生命周期绑定到机器启动，而不是用户登录。典型的 Hermes 用户想要的是：登录 → 网关可用，注销 → 网关消失。计划任务无需提权即可实现这一点。如果你真的想要一个服务，可以手动使用 `nssm` 或 `sc create`——但你可能并不需要。

<a id="data-layout"></a>
## 数据布局

| 路径 | 内容 |
|---|---|
| `%LOCALAPPDATA%\hermes\hermes-agent\` | Git 检出 + 虚拟环境。可以安全地 `Remove-Item -Recurse` 并重新安装。 |
| `%LOCALAPPDATA%\hermes\git\` | 便携版 Git（仅当安装程序配置了它时）。 |
| `%LOCALAPPDATA%\hermes\node\` | 便携版 Node.js（仅当安装程序配置了它时）。 |
| `%LOCALAPPDATA%\hermes\bin\` | `hermes.cmd` 存根，已添加到用户 PATH。 |
| `%USERPROFILE%\.hermes\` | 你的配置、认证、技能、会话、日志。**在重新安装后仍然保留。** |

这种分离是有意为之：`%LOCALAPPDATA%\hermes` 是可丢弃的基础设施（你可以删除它，然后通过一行命令恢复）。`%USERPROFILE%\.hermes` 是你的数据——配置、记忆、技能、会话历史——其结构与 Linux 安装完全相同。在机器之间同步它，你的 Hermes 就会随你移动。

**覆盖 `HERMES_HOME`：** 设置环境变量指向不同的数据目录。与 Linux 上的工作方式相同。

<a id="browser-tool"></a>
## 浏览器工具

浏览器工具使用 `agent-browser`（一个 Node 辅助程序）来驱动 Chromium。在 Windows 上：

- 安装程序通过 npm 将 `agent-browser` 添加到 PATH。
- `shutil.which("agent-browser", path=...)` 会自动找到 `.cmd` 存根——`CreateProcessW` 无法执行没有扩展名的 shebang，因此 Hermes 始终解析为 `.CMD` 包装器。不要手动调用 shebang 脚本；始终通过 `.cmd` 来使用。
- Playwright Chromium 在首次运行时自动安装（`npx playwright install chromium`）。如果安装失败，`hermes doctor` 会显示问题并给出修复提示。

<a id="running-hermes-on-windows-practical-notes"></a>
## 在 Windows 上运行 Hermes — 实用说明

<a id="path-after-install"></a>
### 安装后的 PATH

安装程序通过 `[Environment]::SetEnvironmentVariable` 将 `%LOCALAPPDATA%\hermes\bin` 添加到你的**用户 PATH**。现有的终端不会获取到这个更改——安装后请打开一个新的 PowerShell 窗口（或 Windows Terminal 标签页）。关闭并重新打开，除非你清楚自己在做什么，否则不要手动执行 `$env:PATH += …`。

验证：

```powershell
Get-Command hermes        # 应输出 C:\Users\<你>\AppData\Local\hermes\bin\hermes.cmd
hermes --version
```

<a id="environment-variables"></a>
### 环境变量

Hermes 同时支持 `$env:X`（进程作用域）和用户环境变量（永久设置，在“系统属性”→“环境变量”中设置）。在 `%USERPROFILE%\.hermes\.env` 中设置 API 密钥是常规方式——与 Linux 相同：

```
OPENROUTER_API_KEY=sk-or-...
TELEGRAM_BOT_TOKEN=...
```
不要将机密信息存放在用户环境变量中，除非你明确希望所有 Windows 进程都能看到它们（这通常不是你想要的）。

<a id="windows-specific-env-vars"></a>
### Windows 特有的环境变量

以下变量仅影响本机 Windows 安装：

| 变量 | 作用 |
|---|---|
| `HERMES_GIT_BASH_PATH` | 覆盖 bash.exe 的发现路径。可指向任意 bash —— 完整的 Git for Windows、通过符号链接指向的 WSL bash、MSYS2、Cygwin。安装程序会自动设置此变量。 |
| `HERMES_DISABLE_WINDOWS_UTF8` | 设为 `1` 可禁用 UTF-8 stdio 垫片，回退使用区域设置代码页。用于排查编码相关 Bug。 |
| `EDITOR` / `VISUAL` | 用于 `/edit` 和 `Ctrl-X Ctrl-E` 的编辑器。若两者均未设置，Hermes 默认使用 `notepad`。 |

<a id="uninstall"></a>
## 卸载

在 PowerShell 中执行：

```powershell
hermes uninstall
```

这是干净卸载路径 —— 会移除计划任务条目、启动文件夹快捷方式、`hermes.cmd` 垫片，删除 `%LOCALAPPDATA%\hermes\hermes-agent\`，并清理用户 PATH。保留 `%USERPROFILE%\.hermes\`（你的配置、认证信息、技能、会话、日志），便于重新安装。

若要彻底清除所有内容：

```powershell
hermes uninstall
Remove-Item -Recurse -Force "$env:USERPROFILE\.hermes"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes"
```

`hermes uninstall` CLI 子命令也能处理计划任务条目以不同任务名称注册的情况（老版本安装）—— 它通过安装路径而非硬编码的任务名称进行搜索。

<a id="process-management-internals"></a>
## 进程管理内部机制

以下为背景资料 —— 除非你在调试“自我杀死”这类诡异问题，否则可跳过。

在 Linux 和 macOS 上，POSIX 习惯用法 `os.kill(pid, 0)` 是一个无操作权限检查：“该 PID 是否存活且我能向其发送信号？” 在 Windows 上，Python 的 `os.kill` 将 `sig=0` 映射为 `CTRL_C_EVENT` —— 它们在整数值 0 处冲突 —— 并通过 `GenerateConsoleCtrlEvent(0, pid)` 路由，该函数会向包含目标 PID 的**整个控制台进程组**广播 Ctrl+C。这是 [bpo-14484](https://bugs.python.org/issue14484)，自 2012 年以来一直未关闭。它不会被修复，因为更改它会破坏依赖当前行为的脚本。

后果：任何在 Windows 上通过 `os.kill(pid, 0)` “检查此 PID 是否存活”的代码路径都会静默杀死目标。Hermes 已将每个这样的位置（11 个文件中的 14 处）迁移到 `gateway.status._pid_exists()`，该函数使用 `psutil.pid_exists()`（后者在 Windows 上使用 `OpenProcess + GetExitCodeProcess` —— 不涉及信号）。如果你在编写插件或补丁，请直接使用 `psutil.pid_exists()` 或 `gateway.status._pid_exists()` —— 永远不要用 `os.kill(pid, 0)`。

`scripts/check-windows-footguns.py` 在 CI 中强制实施：任何新的 `os.kill(pid, 0)` 调用都会导致 `Windows footguns (blocking)` 检查失败，除非该行带有 `# windows-footgun: ok — &lt;reason&gt;` 标记。

<a id="common-pitfalls"></a>
## 常见陷阱

**安装后立即出现 `hermes: command not found`。**
打开一个新的 PowerShell 窗口。安装程序已将 `%LOCALAPPDATA%\hermes\bin` 添加到用户 PATH，但已存在的 shell 需要重启才能生效。在此期间你可以运行 `& "$env:LOCALAPPDATA\hermes\bin\hermes.cmd"`。
**`WinError 193: %1 不是有效的 Win32 应用程序`（运行工具时出现）**
你遇到了一个绕过 `.cmd` 垫片的 shebang 脚本调用。Hermes 通过 `shutil.which(cmd, path=local_bin)` 解析命令，因此 PATHEXT 会识别 `.CMD` 文件——如果你是通过硬编码路径调用工具，请改用 `.cmd` 变体（例如 `npx.cmd`，而不是 `npx`）。

**`[scriptblock]::Create(...)` 失败，提示 `The assignment expression is not valid`。**
你下载的 `install.ps1` 包含了 UTF-8 BOM。`irm | iex` 形式会自动去除 BOM；而 `[scriptblock]::Create((irm ...))` 不会。请改用简单的 `irm | iex` 形式重新运行，或者手动下载脚本并通过 `[IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false))` 保存为无 BOM 的文件。

**重启后 Gateway 无法保持运行。**
检查 `hermes gateway status`——它会合并 schtasks 条目、启动文件夹快捷方式（如果使用）以及实时 PID。如果 schtasks 已注册但未运行，可能是组策略阻止了 `ONLOGON` 触发器。运行 `schtasks /Query /TN HermesGateway /V /FO LIST` 查看任务的失败原因，或者通过设置 `HERMES_GATEWAY_FORCE_STARTUP=1` 卸载并重新安装，回退到启动文件夹路径。

**设置 `$env:EDITOR` 后 `/edit` 仍然无效。**
你只在当前进程中设置了该变量；请关闭并重新打开 shell，或者在系统属性 → 环境变量中设置为用户级别。在新的 PowerShell 窗口中用 `echo $env:EDITOR` 验证。

**浏览器工具启动但工具超时。**
Chromium 会在首次运行时自动安装。如果安装失败（GitHub 限速、Playwright CDN 故障），请运行 `hermes doctor`——它会提示缺少 Chromium，并打印出修复所需的 `npx playwright install chromium` 命令。

**`agent-browser` 因奇怪的 Node 版本错误而失败。**
安装程序会在 `%LOCALAPPDATA%\hermes\node` 中提供 Node 22，但你的 PATH 可能优先指向了较旧的系统 Node 18。要么将 Hermes 的 node 目录移到 PATH 更靠前的位置，要么如果你在其他地方不使用 Node，则删除系统安装。

**CLI 中中文/日文/阿拉伯字符显示为 `?`。**
UTF-8 stdio 垫片未激活。检查 `HERMES_DISABLE_WINDOWS_UTF8` 是否未设置（`Get-ChildItem env:HERMES_DISABLE_WINDOWS_UTF8`）。如果该变量为空且仍看到 `?`，则控制台主机（非常旧的 `cmd.exe`）可能根本不支持 UTF-8——请切换到 Windows Terminal。

**Gateway 无法发送 Telegram 图片——"`BadRequest: payload contains invalid characters`"。**
这与 Windows 无关，但有时会首先在此处出现。通常意味着你的文件路径在 JSON 正文中包含未转义的反斜杠。Telegram 应该接收 Hermes 规范化的路径，而不是原始的 Windows 路径——如果你在自定义插件中看到此问题，请确保传递的是 Hermes 提供的路径，而不是来自用户输入的 `str(Path(...))`。

**`git pull` 后出现"在其他机器上正常"的编码异常。**
如果你在 Windows 上使用非 UTF-8 编辑器（旧版 Windows 上的记事本、某些中文输入法）编辑了 Hermes 配置或技能，文件可能已保存为带 BOM 的格式。Hermes 在大多数配置读取中能容忍 `utf-8-sig`，但折叠 YAML 标量（`description: >`）内部的 BOM 会静默破坏 YAML 解析。请将文件重新保存为不带 BOM 的纯 UTF-8 格式。
<a id="where-to-go-next"></a>
## 下一步去哪里

- **[安装](../getting-started/installation.md)** — 完整安装页面，包含 Linux/macOS/WSL2/Termux。
- **[Windows (WSL2) 指南](./windows-wsl-quickstart.md)** — 如需 POSIX 语义或仪表盘终端面板。
- **[CLI 参考](../reference/cli-commands.md)** — 所有 `hermes` 子命令。
- **[常见问题](../reference/faq.md)** — 常见非 Windows 特定问题。
- **[消息网关](./messaging/index.md)** — 在 Windows 上运行 Telegram/Discord/Slack。
