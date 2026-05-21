---
sidebar_position: 2
title: "安装"
description: "在 Linux、macOS、WSL2、原生 Windows（早期 Beta）或 Android（通过 Termux）上安装 Hermes Agent"
---

<a id="installation"></a>
# 安装

使用一行命令安装器，在两分钟内让 Hermes Agent 运行起来。

<a id="quick-install"></a>
## 快速安装

<a id="one-line-installer-linux-macos-wsl2"></a>
### 一行命令安装器（Linux / macOS / WSL2）

基于 Git 的安装，跟踪 `main` 分支，让你立即获取最新变更：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

<a id="windows-native-powershell-early-beta"></a>
### Windows（原生，PowerShell）— 早期 Beta

<a id="early-beta"></a>
:::warning 早期 Beta
原生 Windows 支持处于 **早期 Beta** 阶段。它可以安装并在常见路径下工作，但尚未像我们的 POSIX 安装器那样经过广泛测试。如果你遇到问题，请[提交 issue](https://github.com/NousResearch/hermes-agent/issues)。目前，Windows 上最成熟的设置方案是使用上述 Linux/macOS 一行命令安装器，在 **WSL2** 中运行。
:::

打开 PowerShell 并运行：

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

安装器会处理**所有内容**: `uv`、Python 3.11、Node.js 22、`ripgrep`、`ffmpeg`，**以及可移植 Git Bash**（PortableGit——一个自包含的 Git-for-Windows 发行版，附带 `bash.exe` 和 Hermes 用于 shell 命令的完整 POSIX 工具链；在 32 位 Windows 上，安装器会回退到 MinGit，后者缺少 bash，并会禁用终端工具 / agent-browser 功能）。它会将仓库克隆到 `%LOCALAPPDATA%\hermes\hermes-agent`，创建虚拟环境，并将 `hermes` 添加到你的**用户 PATH**。安装完成后重新启动终端（或打开新的 PowerShell 窗口），以便 PATH 生效。

**Git 的处理方式：**
1. 如果 `git` 已经在你的 PATH 上，安装器会使用你现有的安装。
2. 否则，它会下载可移植的 **PortableGit**（约 50MB，来自官方 `git-for-windows` GitHub release）并解压到 `%LOCALAPPDATA%\hermes\git`。无需管理员权限。完全隔离——不会干扰任何系统 Git 安装（无论完好或损坏）。（在 32 位 Windows 上，它会回退到 MinGit，因为 PortableGit 只提供 64 位和 ARM64 版本；依赖 bash 的 Hermes 特性在 32 位主机上无法正常工作。）

**为什么不用 winget？** 早期的设计会通过 `winget install Git.Git` 自动安装 Git，但当系统 Git 安装处于部分或损坏状态时（这正是用户需要安装器正常工作的场景），winget 会严重失败。可移植 Git 的方式绕开了 winget、Windows 安装器注册表以及任何现有的系统 Git。如果 Hermes Git 安装本身出现问题，执行 `Remove-Item %LOCALAPPDATA%\hermes\git` 并重新运行安装器即可——不会影响系统，也无需卸载麻烦。

安装器还会将 `HERMES_GIT_BASH_PATH` 设置为找到的 `bash.exe` 路径，以便 Hermes 在新 shell 中确定地解析它。

如果你更喜欢 WSL2，上述 Linux 安装器可以在其中使用；原生安装和 WSL 安装可以共存，不会冲突（原生数据位于 `%LOCALAPPDATA%\hermes`，WSL 数据位于 `~/.hermes`）。

**桌面安装器（备选）：** 还提供了一个精简的 GUI 安装器——下载 Hermes Desktop，运行 `.exe`，首次启动时会在底层调用 `install.ps1` 来准备 Python（通过 `uv`）、Node、PortableGit 以及其他依赖。桌面应用和通过 PowerShell 安装的 CLI 共享相同的安装和数据目录，因此你可以选择两者之一或同时使用。详情请参见 [Windows（原生）指南](../user-guide/windows-native#desktop-installer-alternative)。
<a id="android-termux"></a>
### Android / Termux

Hermes 目前也提供了支持 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

安装程序会自动检测 Termux 环境，并切换到经过测试的 Android 流程：
- 使用 Termux 的 `pkg` 安装系统依赖（`git`、`python`、`nodejs`、`ripgrep`、`ffmpeg` 以及编译工具）
- 通过 `python -m venv` 创建虚拟环境
- 为 Android wheel 构建自动导出 `ANDROID_API_LEVEL`
- 优先尝试安装完整的 `.[termux-all]` 扩展包，如果首次编译失败，则回退到较小的 `.[termux]` 扩展包（最后还会尝试基础安装）
- 默认跳过未经测试的浏览器 / WhatsApp 引导脚本

如果你希望使用完全显式的路径，请参考专门的 [Termux 指南](./termux.md)。

:::note Windows 功能对等状态（早期 Beta）

原生 Windows 支持处于**早期 Beta**阶段。除基于浏览器的仪表盘聊天终端外，其它所有功能都可以在 Windows 上原生运行：
<a id="windows-feature-parity-early-beta"></a>
- **CLI（`hermes chat`、`hermes setup`、`hermes gateway` 等）** — 原生支持，使用默认终端
- **网关（Telegram、Discord、Slack 等）** — 原生支持，以 PowerShell 后台进程运行
- **Cron 调度器** — 原生支持
- **浏览器工具** — 原生支持（通过 Node.js 的 Chromium）
- **MCP 服务器** — 原生支持（stdio 和 HTTP 两种传输协议均可）
- **仪表盘 `/chat` 终端面板** — **仅 WSL2 支持**（使用 POSIX PTY；原生 Windows 没有等效实现）。仪表盘其余部分（会话、任务、指标）均可原生运行——只有嵌入式 PTY 终端标签页受限。

如果遇到编码相关的错误，可以在环境中设置 `HERMES_DISABLE_WINDOWS_UTF8=1`，以回退到传统的 cp1252 stdio 路径（有助于排查问题）。
:::

<a id="what-the-installer-does"></a>
### 安装程序做了什么

安装程序会自动处理所有事务——所有依赖（Python、Node.js、ripgrep、ffmpeg）、仓库克隆、虚拟环境、全局 `hermes` 命令设置以及 LLM 提供者配置。完成后你就可以直接开始聊天了。

<a id="install-layout"></a>
#### 安装布局

安装程序将文件放在哪里取决于你是以普通用户还是 root 身份安装：

| 安装方式 | 代码存放位置 | `hermes` 二进制文件 | 数据目录 |
|---|---|---|---|
| pip install | Python site-packages | `~/.local/bin/hermes`（console_scripts） | `~/.hermes/` |
| 每位用户（git 安装程序） | `~/.hermes/hermes-agent/` | `~/.local/bin/hermes`（符号链接） | `~/.hermes/` |
| root 模式（`sudo curl … \| sudo bash`） | `/usr/local/lib/hermes-agent/` | `/usr/local/bin/hermes` | `/root/.hermes/`（或 `$HERMES_HOME`） |

root 模式的 **FHS 布局**（`/usr/local/lib/…`、`/usr/local/bin/hermes`）与 Linux 上其他系统级开发者工具的安装位置一致。它适用于多用户共享机器的部署场景，一套系统安装即可服务所有用户。每位用户的配置（认证、技能、会话）仍然存放在各自用户的 `~/.hermes/` 或显式指定的 `HERMES_HOME` 中。

<a id="after-installation"></a>
### 安装之后

重新加载你的 shell 并开始聊天：

```bash
source ~/.bashrc   # 或者：source ~/.zshrc
hermes             # 开始聊天！
```
要稍后重新配置单个设置，请使用专门的命令：

```bash
hermes model          # 选择你的 LLM 提供商和模型
hermes tools          # 配置哪些工具已启用
hermes gateway setup  # 设置消息平台
hermes config set     # 设置单个配置值
hermes setup          # 或者运行完整的设置向导一次性配置所有内容
```

---

<a id="prerequisites"></a>
## 先决条件

**pip install：** 除了 Python 3.11+ 之外没有其他先决条件。其他一切自动处理。

**Git 安装程序：** 唯一的先决条件是 **Git**。安装程序会自动处理所有其他内容：

- **uv**（快速 Python 包管理器）
- **Python 3.11**（通过 uv，无需 sudo）
- **Node.js v22**（用于浏览器自动化和 WhatsApp 桥接）
- **ripgrep**（快速文件搜索）
- **ffmpeg**（用于 TTS 的音频格式转换）

:::info
你**不需要**手动安装 Python、Node.js、ripgrep 或 ffmpeg。安装程序会检测缺少什么并为你安装。只需确保已安装 `git` 并可用（`git --version`）。
:::

:::tip Nix 用户
如果你使用 Nix（在 NixOS、macOS 或 Linux 上），有一条专用的设置路径，包含 Nix flake、声明式 NixOS 模块和可选的容器模式。请参见 **[Nix & NixOS 设置](./nix-setup.md)** 指南。
<a id="nix-users"></a>
:::

---

<a id="manual-developer-installation"></a>
## 手动 / 开发者安装

如果你想克隆仓库并从源代码安装——用于贡献、从特定分支运行或完全控制虚拟环境——请参阅贡献指南中的[开发设置](../developer-guide/contributing.md#development-setup)部分。

---

<a id="non-sudo-system-service-user-installs"></a>
## 免 sudo / 系统服务用户安装

支持将 Hermes 作为专用的非特权用户运行（例如 `hermes` systemd 服务账户，或任何没有 `sudo` 访问权限的用户）。安装路径中唯一需要 root 权限的是 Playwright 的 `--with-deps` 步骤，该步骤通过 `apt` 安装 Chromium 使用的共享库（`libnss3`、`libxkbcommon` 等）。安装程序会检测 sudo 是否可用，并在其不可用时优雅地降级——它会将 Chromium 二进制安装到服务用户自己的 Playwright 缓存中，并打印管理员需要单独运行的确切命令。

**推荐的分步操作（Debian/Ubuntu）：**

1. **一次性的，由具有 sudo 权限的管理员用户**安装 Chromium 所需的系统库：
   ```bash
   sudo npx playwright install-deps chromium
   ```
   （你可以从任何位置运行此命令——`npx` 会动态获取 Playwright。）

2. **作为非特权服务用户**，运行常规安装程序。它将检测到缺少 sudo，跳过 `--with-deps`，并将 Chromium 安装到用户的本地 Playwright 缓存中：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   ```

   如果你想完全跳过 Playwright 步骤——例如因为你正在以无头模式运行且不需要浏览器自动化——请传递 `--skip-browser` 参数：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash -s -- --skip-browser
   ```
3. **让服务用户能在 shell 中使用 `hermes`。** 安装程序会将启动器写入 `~/.local/bin/hermes`。系统服务账户通常使用最小化的 PATH，不包含 `~/.local/bin`。你可以将其添加到用户环境，或者将启动器符号链接到系统目录：
   ```bash
   # 选项 A — 添加到服务用户的 profile
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

   # 选项 B — 系统级符号链接（以管理员身份运行）
   sudo ln -s /home/hermes/.hermes/hermes-agent/venv/bin/hermes /usr/local/bin/hermes
   ```

4. **验证：** 现在运行 `hermes doctor` 应该能正常执行。如果出现 `ModuleNotFoundError: No module named 'dotenv'`，说明你正在用系统 Python 调用仓库源码中的 `hermes` 文件（`~/.hermes/hermes-agent/hermes`），而不是 venv 启动器（`~/.hermes/hermes-agent/venv/bin/hermes`）—— 请修正第 3 步。

同样的模式也适用于 Arch（安装程序使用 pacman，并采用相同的 sudo 检测逻辑）、Fedora/RHEL 和 openSUSE —— 这些发行版完全不支持 `--with-deps`，因此管理员需要单独安装系统库。安装程序会打印出相应的 `dnf`/`zypper` 命令。

---

<a id="troubleshooting"></a>
## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `hermes: command not found` | 重新加载 shell（`source ~/.bashrc`）或检查 PATH |
| `API key not set` | 运行 `hermes model` 配置你的提供商，或运行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后配置丢失 | 运行 `hermes config check`，然后运行 `hermes config migrate` |

如需更多诊断信息，请运行 `hermes doctor` —— 它会准确告诉你缺少什么以及如何修复。

<a id="install-method-auto-detection"></a>
## 安装方法自动检测

Hermes 会自动检测它是通过 `pip`、git 安装程序、Homebrew 还是 NixOS 安装的，`hermes update` 会打印出对应路径的更新命令。无需设置环境变量 —— 检测基于安装布局（Python site-packages、`~/.hermes/hermes-agent/`、Homebrew 前缀或 Nix store 路径）。`hermes doctor` 也会在其环境摘要中显示检测到的方法。
