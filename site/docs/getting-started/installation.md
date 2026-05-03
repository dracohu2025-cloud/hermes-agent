---
sidebar_position: 2
title: "安装"
description: "在 Linux、macOS、WSL2 或 Android（通过 Termux）上安装 Hermes Agent"
---

# 安装 {#installation}

使用一行命令安装程序，两分钟即可让 Hermes Agent 运行起来。

## 快速安装 {#quick-install}

### Linux / macOS / WSL2 {#linux-macos-wsl2}

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Android / Termux {#android-termux}

Hermes 现在也提供了支持 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

安装程序会自动检测 Termux 并切换到经过测试的 Android 流程：
- 使用 Termux 的 `pkg` 安装系统依赖（`git`、`python`、`nodejs`、`ripgrep`、`ffmpeg`、编译工具）
- 通过 `python -m venv` 创建虚拟环境
- 自动导出 `ANDROID_API_LEVEL` 以用于 Android wheel 构建
- 使用 `pip` 安装精选的 `.[termux]` 附加包
- 默认跳过未经测试的浏览器 / WhatsApp 引导

如果你想要最明确的路径，请参照专用的 [Termux 指南](./termux.md)。

:::warning Windows
**不支持**原生 Windows 系统。请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) 并在其中运行 Hermes Agent。上述安装命令在 WSL2 内部有效。
:::

### 安装程序会做什么 {#what-the-installer-does}

安装程序会自动处理所有事情——所有依赖项（Python、Node.js、ripgrep、ffmpeg）、仓库克隆、虚拟环境、全局 `hermes` 命令设置以及 LLM 提供商配置。完成后，你就可以开始聊天了。

#### 安装布局 {#install-layout}

安装程序放置文件的位置取决于你是以普通用户还是 root 身份安装：

| 安装方式 | 代码位置 | `hermes` 二进制文件 | 数据目录 |
|---|---|---|---|
| 用户级（普通用户） | `~/.hermes/hermes-agent/` | `~/.local/bin/hermes`（符号链接） | `~/.hermes/` |
| root 模式（`sudo curl … \| sudo bash`） | `/usr/local/lib/hermes-agent/` | `/usr/local/bin/hermes` | `/root/.hermes/`（或 `$HERMES_HOME`） |

root 模式使用 **FHS 布局**（`/usr/local/lib/…`、`/usr/local/bin/hermes`），与 Linux 上其他系统级开发者工具的安装位置一致。这对于需要为所有用户安装一个系统级部署的共享机器非常有用。用户级配置（认证、技能、会话）仍然位于每个用户的 `~/.hermes/` 或显式指定的 `HERMES_HOME` 下。

### 安装完成后 {#after-installation}

重新加载你的 shell 并开始聊天：

```bash
source ~/.bashrc   # 或：source ~/.zshrc
hermes             # 开始聊天！
```

后续要重新配置单个设置，请使用专用命令：

```bash
hermes model          # 选择你的 LLM 提供商和模型
hermes tools          # 配置启用哪些工具
hermes gateway setup  # 设置消息平台
hermes config set     # 设置单个配置项
hermes setup          # 或者运行完整的设置向导一次性配置所有内容
```

---

## 前置要求 {#prerequisites}

唯一的前置要求是 **Git**。安装程序会自动处理所有其他内容：

- **uv**（快速的 Python 包管理器）
- **Python 3.11**（通过 uv，无需 sudo）
- **Node.js v22**（用于浏览器自动化和 WhatsApp 桥接）
- **ripgrep**（快速文件搜索）
- **ffmpeg**（用于 TTS 的音频格式转换）
:::info
你**不需要**手动安装 Python、Node.js、ripgrep 或 ffmpeg。安装程序会自动检测缺失项并为你安装。只需确保 `git` 可用即可（`git --version`）。
:::

:::tip Nix 用户
如果你使用 Nix（在 NixOS、macOS 或 Linux 上），有专门的设置路径，包含 Nix flake、声明式 NixOS 模块和可选的容器模式。请参阅 **[Nix 与 NixOS 设置指南](./nix-setup.md)**。
<a id="nix-users"></a>
:::

---

## 手动 / 开发者安装 {#manual-developer-installation}

如果你想克隆仓库并从源码安装——用于贡献、从特定分支运行或完全控制虚拟环境——请参阅贡献指南中的[开发环境设置](../developer-guide/contributing.md#development-setup)部分。

---

## 故障排除 {#troubleshooting}

| 问题 | 解决方案 |
|------|----------|
| `hermes: command not found` | 重新加载 shell（`source ~/.bashrc`）或检查 PATH |
| `API key not set` | 运行 `hermes model` 配置你的提供商，或运行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后配置缺失 | 先运行 `hermes config check`，再运行 `hermes config migrate` |

如需更多诊断信息，请运行 `hermes doctor`——它会准确告诉你缺失了什么以及如何修复。
