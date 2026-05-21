---
title: "Windows (WSL2) 指南"
description: "通过 WSL2 在 Windows 上运行 Hermes Agent — 设置、Windows 与 Linux 之间的文件系统访问、网络以及常见陷阱"
sidebar_label: "Windows (WSL2)"
sidebar_position: 2
---

<a id="windows-wsl2-guide"></a>
# Windows (WSL2) 指南

Hermes Agent 现已**同时**支持原生 Windows 和 WSL2。本页介绍 WSL2 方案；原生 PowerShell 安装请参见专用 **[Windows（原生）指南](./windows-native.md)**。

**何时优先选择 WSL2 而非原生：**
- 你想使用仪表盘的嵌入式终端（`/chat` 标签页）——该面板需要 POSIX PTY，且仅支持 WSL2。
- 你正在进行重度 POSIX 开发工作，并希望 Hermes 会话与你的开发工具共享同一文件系统/路径。
- 你已经拥有 WSL2 环境，不想再维护第二套安装。

**何时原生即可（甚至更优）：**
- 交互式聊天、网关（Telegram/Discord 等）、定时调度器、浏览器工具、MCP 服务器以及大多数 Hermes 功能均可在 Windows 上原生运行。
- 你不想每次引用文件或打开 URL 时都要考虑 WSL↔Windows 之间的边界。

在 WSL2 中，实际上有两台计算机在运作：你的 Windows 主机，以及由 WSL 管理的 Linux 虚拟机。大部分困惑都来自不确定自己当前处于哪一侧。

本指南涵盖了这一分离中与 Hermes 特别相关的部分：安装 WSL2、在 Windows 和 Linux 之间传输文件、双向网络配置，以及人们实际遇到的陷阱。

:::info 简体中文
本页面维护了最小安装路径的中文版操作指南——通过右上角的**语言**菜单切换并选择**简体中文**即可。
:::

<a id="why-wsl2-vs-native-windows"></a>
## 为什么选择 WSL2（对比原生 Windows）

原生 Windows 安装直接在 Windows 中运行：你的 Windows 终端（PowerShell、Windows Terminal 等）、Windows 文件系统路径（`C:\Users\…`）和 Windows 进程。Hermes 使用 Git Bash 来执行 Shell 命令，这也是 Claude Code 和其他 Agent 目前在 Windows 上的做法——它绕过了 POSIX 与 Windows 的差异，而无需完整重写。

WSL2 在一个轻量级虚拟机中运行真正的 Linux 内核，因此其内部的 Hermes 本质上与在 Ubuntu 上运行无异。当你需要真实的 POSIX 环境时，这非常有价值：`fork`、`/tmp`、UNIX 套接字、信号语义、基于 PTY 的终端、`bash`/`zsh` 等 Shell，以及 `rg`、`git`、`ffmpeg` 等行为与 Linux 上一致的工具。

WSL2 的实际影响：

- Hermes CLI、网关、会话、记忆、技能和工具运行时都位于 Linux 虚拟机内部。
- Windows 程序（浏览器、原生应用、已登录个人资料的 Chrome）位于其外部。
- 每次你需要两者通信——共享文件、打开 URL、控制 Chrome、访问本地模型服务器、将 Hermes 网关暴露给手机——都需要跨越一个边界。这些边界正是本指南要讲解的内容。

<a id="install-wsl2"></a>
## 安装 WSL2

从**管理员 PowerShell** 或 Windows Terminal 运行：

```powershell
wsl --install
```

在全新的 Windows 10 22H2+ 或 Windows 11 机器上，此命令会安装 WSL2 内核、虚拟机平台功能以及默认的 Ubuntu 发行版。按提示重启。重启后 Ubuntu 将打开并询问 Linux 用户名 + 密码——这是一个**新的 Linux 用户**，与你的 Windows 账户无关。
确认你确实在使用 WSL2（而非旧版 WSL1）：

```powershell
wsl --list --verbose
```

你应该会看到 `VERSION  2`。如果某个发行版显示 `VERSION  1`，请将其转换：

```powershell
wsl --set-version Ubuntu 2
wsl --set-default-version 2
```

Hermes 在 WSL1 上无法稳定运行——WSL1 会实时转换 Linux 系统调用，某些行为（如 procfs、信号、网络）与真正的 Linux 存在差异。

<a id="distro-choice"></a>
### 发行版选择

我们主要测试的是 Ubuntu（LTS）。Debian 也能用。Arch 和 NixOS 对想用的人也可以，但一键安装脚本默认使用基于 Debian 的 `apt` 系统——如果要用 Nix，请参考 [Nix 安装指南](/getting-started/nix-setup)。

<a id="enable-systemd-recommended"></a>
### 启用 systemd（推荐）

使用 systemd 管理 Hermes 网关（以及任何你想保持运行的程序）会更方便。在较新的 WSL 上，只需在发行版内启用一次：

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true

[interop]
enabled=true
appendWindowsPath=true

[automount]
options = "metadata,umask=22,fmask=11"
EOF
```

然后在 PowerShell 中执行：

```powershell
wsl --shutdown
```

重新打开你的 WSL 终端。执行 `ps -p 1 -o comm=` 应该会输出 `systemd`。

上面的 `metadata` 挂载选项很重要——没有它，`/mnt/c/...` 下的文件就无法存储真正的 Linux 权限位，这会导致 Windows 路径下的脚本无法正常使用 `chmod +x` 等操作。

<a id="install-hermes-inside-wsl"></a>
### 在 WSL 中安装 Hermes

打开 WSL2 终端后，执行：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc
hermes
```

安装程序会将 WSL2 视为普通 Linux——不需要任何 WSL 特定的操作。完整布局请参考[安装指南](/getting-started/installation)。

<a id="filesystem-crossing-the-windows-wsl2-boundary"></a>
## 文件系统：跨越 Windows ↔ WSL2 边界

这部分最容易让人困惑。这里有**两个文件系统**，你把文件放在哪里很重要——这关系到性能、正确性以及工具能否正常访问。

<a id="the-two-directions"></a>
### 两个方向

| 方向 | 内部路径 | 你使用的路径 |
|---|---|---|
| 从 WSL 访问 Windows 磁盘 | `C:\Users\you\Documents` | `/mnt/c/Users/you/Documents` |
| 从 Windows 访问 WSL 磁盘 | `/home/you/code` | `\\wsl$\Ubuntu\home\you\code`（或新版中的 `\\wsl.localhost\Ubuntu\...`） |

两者都是真实的，都能用，但它们**不是同一个文件系统**——底层通过 9P 网络协议桥接。这会对性能和语义产生实际影响。

<a id="where-to-put-hermes-and-your-projects"></a>
### 把 Hermes 和你的项目放在哪里

**经验法则：把所有 Linux 相关的内容都放在 Linux 文件系统内。**

- 你的 Hermes 安装目录（`~/.hermes/`）——放在 Linux 侧。安装程序已经这么做了。
- 你在 WSL 中使用的 git 仓库——放在 Linux 侧（`~/code/...`、`~/projects/...`）。
- 你的模型、数据集、虚拟环境——都放在 Linux 侧。

遵循这条规则的好处：

- **I/O 速度快。** 对 `/mnt/c/...` 的操作会经过 9P，速度比原生 ext4 慢 10–100 倍。一个包含 1 万个文件的仓库，在 `~/code` 下执行 `git status` 几乎瞬间完成，但在 `/mnt/c` 下可能需要 15 秒以上。
- **权限正确。** `/mnt/c` 下的 Linux 权限位只是尽力模拟。常见问题包括 `ssh` 因“权限错误”拒绝密钥，或 `chmod +x` 静默失败。
- **文件监视器可靠。** 跨 9P 的 inotify 不稳定——文件监视器（如开发服务器、测试运行器）经常漏掉 `/mnt/c` 上的文件变更。
- **没有大小写敏感问题。** Windows 路径默认不区分大小写，而 Linux 区分大小写。如果一个项目同时包含 `Readme.md` 和 `README.md`，在不同侧的行为会不同。
仅当**需要**文件存于 Windows 侧时才将东西放到 `/mnt/c` — 例如，你想从 Windows GUI 应用打开它，或者 Windows Chrome 的 DevTools MCP 需要当前目录是一个 Windows 可访问的路径。

<a id="getting-files-back-and-forth"></a>
### 来回传输文件

**从 Windows → 进入 WSL：** 最简单的方式是打开资源管理器并在地址栏输入 `\\wsl.localhost\Ubuntu`。然后你可以拖放到 `\home\<你>\...`。或者从 PowerShell：

```powershell
wsl cp /mnt/c/Users/you/Downloads/file.pdf ~/incoming/
```

**从 WSL → 进入 Windows：** 复制到 `/mnt/c/Users/<你>/...`，它会立即出现在 Windows 资源管理器中：

```bash
cp ~/reports/output.pdf /mnt/c/Users/you/Desktop/
```

**在 Windows 应用中打开 WSL 文件**（GUI 编辑器、浏览器等）：使用 `explorer.exe` 或 `wslview`：

```bash
sudo apt install wslu     # 一次安装 — 提供 wslview、wslpath、wslopen 等工具
wslview ~/reports/output.pdf    # 使用 Windows 默认处理程序打开
explorer.exe .                  # 在 Windows 资源管理器中打开当前 WSL 目录
```

**在两个世界间转换路径：**

```bash
wslpath -w ~/code/project        # → \\wsl.localhost\Ubuntu\home\you\code\project
wslpath -u 'C:\Users\you'        # → /mnt/c/Users/you
```

<a id="line-endings-boms-and-git"></a>
### 行尾、BOM 和 git

如果使用 Windows 编辑器在 Windows 侧编辑文件，它们可能会获得 `CRLF` 行尾。当 Linux 侧的 bash 或 Python 读取它们时，shell 脚本会报错 `bad interpreter: /bin/bash^M`，Python 可能会因带有 BOM 的 `.env` 文件而失败。

解决方法是在 WSL 内部（而不是在 Windows 上）设置合理的 git 配置：

```bash
git config --global core.autocrlf input
git config --global core.eol lf
```

对于已经包含 CRLF 的文件：

```bash
sudo apt install dos2unix
dos2unix path/to/script.sh
```

<a id="clone-inside-wsl-or-on-mnt-c"></a>
### "在 WSL 内部还是 `/mnt/c` 上克隆？"

在 WSL 内部克隆。如果没有特别理由，永远这样做。典型的 Hermes 工作流（`hermes chat`、调用 `rg`/`ripgrep` 搜索仓库的工具调用、文件监控器、后台 gateway）在 `~/code/myrepo` 上比在 `/mnt/c/Users/you/myrepo` 上要快得多，也可靠得多。

一个例外：**启动 Windows 二进制文件的 MCP 桥接。** 如果你通过 `cmd.exe` 使用 `chrome-devtools-mcp`（参见 [MCP 指南：WSL → Windows Chrome](/guides/use-mcp-with-hermes#wsl2-bridge-hermes-in-wsl-to-windows-chrome)），当 Hermes 的当前工作目录是 `~` 时，Windows 可能会弹出 `UNC` 警告。在这种情况下，从 `/mnt/c/` 下的某个位置启动 Hermes，以便 Windows 进程有一个盘符 cwd。

<a id="networking-wsl-windows"></a>
## 网络：WSL ↔ Windows

WSL2 运行在一个轻量级虚拟机中，拥有自己的网络栈。这意味着 WSL 内部的 `localhost` **不同于** Windows 上的 `localhost` — 从网络角度来看，它们是两个独立的主机。你需要为每个服务决定流量流向哪个方向，并选择合适的桥接。

两种常见情况如下。

<a id="case-1-hermes-in-wsl-talks-to-a-service-on-windows"></a>
### 情况 1 — WSL 中的 Hermes 与 Windows 上的服务通信

最常见的情况：你在 Windows 上运行 **Ollama、LM Studio 或 llama-server**，而 Hermes（在 WSL 内部）需要访问它。
实现此功能的标准方法请参考提供商指南：**[WSL2 本地模型网络配置（面向 Windows 用户）→](/integrations/providers#wsl2-networking-windows-users)**

简要说明：

- **Windows 11 22H2+：** 开启镜像网络模式（在 `%USERPROFILE%\.wslconfig` 中设置 `networkingMode=mirrored`，然后执行 `wsl --shutdown`）。之后 `localhost` 在双向都可用。
- **Windows 10 或更早版本：** 使用 Windows 主机的 IP（WSL 虚拟网络的默认网关），并确保 Windows 上的服务绑定到 `0.0.0.0`，而不仅仅是 `127.0.0.1`。Windows 防火墙通常还需要为该端口添加规则。

完整的表格（Ollama / LM Studio / vLLM / SGLang 绑定地址、防火墙规则单行命令、动态 IP 辅助工具、Hyper-V 防火墙变通方案）请点击上方链接查看，此处不再重复。

<a id="case-2-something-on-windows-or-your-lan-talks-to-hermes-in-wsl"></a>
### 场景 2 — Windows 上（或你的局域网内）的设备与 WSL 中的 Hermes 通信

这是反向场景，在其他文档中较少提及，但以下场景会用到：

- 在 Windows 浏览器中使用 Hermes **Web 面板**。
- 在 Windows 端工具中使用 **兼容 OpenAI 的 API 服务器**（由 `hermes gateway` 在 `API_SERVER_ENABLED=true` 时暴露）。请参见 [API 服务器功能页面](/user-guide/features/api-server)。
- 测试**消息网关**（Telegram、Discord 等），平台会向本地 webhook URL 发送请求 —— 通常应使用 `cloudflared`/`ngrok` 而非直接端口转发。

<a id="subcase-2a-from-the-windows-host-itself"></a>
#### 子场景 2a：从 Windows 主机本身访问

在 **已开启镜像模式的 Windows 11 22H2+** 上，无需任何操作。WSL 中绑定到 `0.0.0.0:8080`（甚至 `127.0.0.1:8080`）的进程，可以通过 Windows 浏览器中的 `http://localhost:8080` 访问。WSL 会自动将绑定发布回主机。

在 **NAT 模式**（Windows 10 / 较旧版 Windows 11）下，WSL2 默认的“localhost 转发”通常会将 Linux 端 `127.0.0.1` 的绑定转发到 Windows 的 `localhost`，因此使用 `--host 127.0.0.1` 启动的 Hermes 服务通常可以在 Windows 上通过 `http://localhost:PORT` 访问。如果无法访问：

- 在 WSL 内显式绑定到 `0.0.0.0`。
- 用 `ip -4 addr show eth0 | grep inet` 找到 WSL 虚拟机的 IP，然后在 Windows 上访问该 IP。

<a id="subcase-2b-from-another-device-on-your-lan-phone-tablet-another-pc"></a>
#### 子场景 2b：从局域网内的其他设备访问（手机、平板、另一台 PC）

这是最麻烦的情况。流量路径为 **局域网设备 → Windows 主机 → WSL 虚拟机**，你需要设置两跳：

1. **在 WSL 内绑定所有接口。** 监听在 `127.0.0.1` 上的进程永远无法从虚拟机外部访问。请使用 `0.0.0.0`。

2. **端口转发：Windows → WSL 虚拟机。** 镜像模式下自动完成。NAT 模式下需要自行按端口设置，在管理员 PowerShell 中运行：

   ```powershell
   # 获取 WSL 虚拟机的当前 IP（NAT 模式下每次重启 WSL 都会变化）
   $wslIp = (wsl hostname -I).Trim().Split(' ')[0]

   # 将 Windows 端口 8080 转发到 WSL:8080
   netsh interface portproxy add v4tov4 `
     listenaddress=0.0.0.0 listenport=8080 `
     connectaddress=$wslIp connectport=8080

   # 允许通过 Windows 防火墙
   New-NetFirewallRule -DisplayName "Hermes WSL 8080" `
     -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
   ```
之后可以用 `netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8080` 移除。

3. **将局域网设备指向 `http://&lt;windows-lan-ip&gt;:8080`。**

由于 WSL VM 的 IP 在 NAT 模式下每次重启都会漂移，单次规则只能持续到下一次 `wsl --shutdown`。若要持久化，要么使用镜像模式，要么将端口代理步骤放入 Windows 登录时运行的脚本中。

对于来自云消息服务商的 webhook（Telegram `setWebhook`、Slack 事件等），不要折腾端口转发——使用 `cloudflared` 隧道。参见 [webhooks 指南](/user-guide/messaging/webhooks)。

<a id="running-hermes-services-long-term-on-windows"></a>
## 在 Windows 上长期运行 Hermes 服务

Hermes [Tool Gateway](/user-guide/features/tool-gateway) 和 API 服务器是长期运行的进程。在 WSL2 中，你有几种方式让它们保持运行。

<a id="inside-wsl-with-systemd-recommended"></a>
### 在 WSL 内使用 systemd（推荐）

如果你按照上述设置部分启用了 systemd，`hermes gateway` 和 API 服务器的工作方式与在任何 Linux 机器上相同。使用网关设置向导：

```bash
hermes gateway setup
```

它会提供安装一个 systemd 用户单元，以便在 WSL 启动时自动启动网关。

<a id="making-wsl-itself-start-on-windows-login"></a>
### 让 WSL 在 Windows 登录时自动启动

WSL 的虚拟机仅在有人使用时才保持活跃。要让你的网关在没有终端窗口打开的情况下也能被访问，通过任务计划程序在 Windows 登录时启动一个 WSL 进程：

- **触发器：** 登录时（你的用户）。
- **操作：** 启动程序
  - 程序：`C:\Windows\System32\wsl.exe`
  - 参数：`-d Ubuntu --exec /bin/sh -c "sleep infinity"`

这会让虚拟机保持运行，从而使 systemd 管理的网关持续运行。在 Windows 11 上，较新的 `wsl --install --no-launch` + 自动启动流程也可用；`sleep infinity` 技巧是便携版本。

<a id="gpu-passthrough-local-models"></a>
## GPU 直通（本地模型）

WSL2 从 WSL 内核 5.10.43+ 开始原生支持 **NVIDIA** GPU——在 Windows 上安装标准 NVIDIA 驱动程序（**不要**在 WSL 内安装 Linux NVIDIA 驱动程序），然后 WSL 内的 `nvidia-smi` 就能看到 GPU。之后，CUDA 工具集、`torch`、`vllm`、`sglang` 和 `llama-server` 可以像往常一样基于真实 GPU 构建。

AMD ROCm 和 Intel Arc 在 WSL2 内的支持仍在演进中，不在 Hermes 的测试范围内——在当前驱动下可能能用，但我们没有可推荐的方案。

如果你正在运行一个 **Windows 原生**的本地模型服务器（Ollama for Windows、LM Studio），它已经通过 Windows 驱动使用你的 GPU，那么你完全不需要 WSL GPU 直通——只需按照上面的情况 1，从 WSL 通过网络访问它即可。

<a id="common-pitfalls"></a>
## 常见陷阱

**"Connection refused" 连接到你的 Windows 托管的 Ollama / LM Studio。**
参见 [WSL2 网络](/integrations/providers#wsl2-networking-windows-users)。90% 的情况下服务器绑定到了 `127.0.0.1`，需要改为 `0.0.0.0`（Ollama：`OLLAMA_HOST=0.0.0.0`），或者你缺少防火墙规则。

**在仓库中 `git status` / `hermes chat` 极其缓慢。**
你可能在 `/mnt/c/...` 下工作。将仓库移动到 `~/code/...`（Linux 侧）。速度提升一个数量级。
**`bad interpreter: /bin/bash^M` 脚本报错。**
Windows 编辑器导致的 CRLF 换行符。运行 `dos2unix script.sh`，并在 WSL git 配置中设置 `core.autocrlf input`。

**通过 MCP 启动的 Windows 二进制程序报 "UNC paths are not supported" 警告。**
Hermes 的当前工作目录位于 Linux 文件系统中，而 Windows 的 `cmd.exe` 无法识别该路径。请从 `/mnt/c/...` 路径启动 Hermes，或使用一个包装脚本，在调用 Windows 可执行文件前先 `cd` 到一个 Windows 可访问的目录。

**休眠/睡眠后出现时钟漂移。**
主机从睡眠状态恢复后，WSL2 的时钟可能滞后数分钟，这会破坏任何基于证书的认证（OAuth、HTTPS API）。按需修复：

```bash
sudo hwclock -s
```

或者安装 `ntpdate` 并在登录时运行。

**启用镜像模式或连接 VPN 后 DNS 停止工作。**
镜像模式会将主机的网络设置代理到 WSL 中——如果 Windows DNS 出现问题（VPN 分流隧道、企业解析器），WSL 会继承这些问题。临时解决方案：手动覆盖 `resolv.conf`（在 `/etc/wsl.conf` 中设置 `generateResolvConf=false`，然后编写你自己的 `/etc/resolv.conf`，填入 `1.1.1.1` 或你的 VPN 的 DNS）。

**运行安装程序后找不到 `hermes` 命令。**
安装程序通过 `~/.bashrc` 将 `~/.local/bin` 添加到 shell 的 PATH 中。你需要执行 `source ~/.bashrc`（或打开一个新终端）才能在当前会话中生效。

**Windows Defender 在 WSL 文件上运行缓慢。**
当从 Windows 访问时，Defender 会通过 9P 桥扫描文件，这会加剧 `/mnt/c` 这类跨边界访问的缓慢问题。如果你只在 WSL 内部操作 WSL 文件，则无需担心。如果你经常使用 Windows 工具访问 `\\wsl$\...` 路径，可以考虑将 WSL 发行版路径从实时扫描中排除。

**磁盘空间不足。**
WSL2 将其虚拟机磁盘存储为 `%LOCALAPPDATA%\Packages\...` 下的稀疏 VHDX 文件。它会增长，但删除文件后不会自动收缩。要回收空间：执行 `wsl --shutdown`，然后从管理员 PowerShell 运行 `Optimize-VHD -Path &lt;path-to-ext4.vhdx&gt; -Mode Full`（需要 Hyper-V 工具）——或者使用 WSL 文档中更简单的 `diskpart` 方法。

<a id="where-to-go-next"></a>
## 下一步

- **[安装](/getting-started/installation)** — 实际安装步骤（Linux/WSL2/Termux 均使用相同的安装程序）。
- **[集成 → 提供商 → WSL2 网络](/integrations/providers#wsl2-networking-windows-users)** — 关于本地模型服务器的权威网络深度解析。
- **[MCP 指南 → WSL → Windows Chrome](/guides/use-mcp-with-hermes#wsl2-bridge-hermes-in-wsl-to-windows-chrome)** — 从 WSL 中的 Hermes 控制已登录的 Windows Chrome。
- **[工具网关](/user-guide/features/tool-gateway)** 和 **[Web 仪表盘](/user-guide/features/web-dashboard)** — 你最常需要从 WSL 暴露到网络中其他设备的长时运行服务。
