---
sidebar_position: 2
title: "安装"
description: "在 Linux、macOS、WSL2 或通过 Termux 在 Android 上安装 Hermes Agent"
---

<a id="installation"></a>
# 安装

使用一行命令安装程序，两分钟内即可启动并运行 Hermes Agent。

<a id="quick-install"></a>
## 快速安装

<a id="linux-macos-wsl2"></a>
### Linux / macOS / WSL2

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

<a id="android-termux"></a>
### Android / Termux

Hermes 现在也提供了一个适配 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

安装程序会自动检测 Termux 并切换到经过测试的 Android 流程：
- 使用 Termux 的 `pkg` 来安装系统依赖项（`git`、`python`、`nodejs`、`ripgrep`、`ffmpeg`、构建工具）
- 使用 `python -m venv` 创建虚拟环境
- 自动导出 `ANDROID_API_LEVEL` 以用于 Android wheel 构建
- 使用 `pip` 安装精选的 `.[termux]` 额外依赖项
- 默认跳过未经测试的浏览器 / WhatsApp 引导程序

如果你想使用完全明确的路径，请遵循专门的 [Termux 指南](./termux.md)。

:::warning Windows
**不支持**原生 Windows。请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) 并在其中运行 Hermes Agent。上面的安装命令在 WSL2 内有效。
:::

<a id="what-the-installer-does"></a>
### 安装程序做了什么

安装程序会自动处理所有事情——所有依赖项（Python、Node.js、ripgrep、ffmpeg）、仓库克隆、虚拟环境、全局 `hermes` 命令设置以及 LLM 提供商配置。完成后，你就可以开始聊天了。

<a id="after-installation"></a>
### 安装后

重新加载你的 shell 并开始聊天：

```bash
source ~/.bashrc   # 或者：source ~/.zshrc
hermes             # 开始聊天！
```

以后要重新配置单个设置，请使用专用命令：

```bash
hermes model          # 选择你的 LLM 提供商和模型
hermes tools          # 配置启用哪些工具
hermes gateway setup  # 设置消息传递平台
hermes config set     # 设置单个配置值
hermes setup          # 或者运行完整的设置向导，一次性配置所有内容
```

---

<a id="prerequisites"></a>
## 先决条件

唯一的先决条件是 **Git**。安装程序会自动处理其他所有事项：

- **uv**（快速的 Python 包管理器）
- **Python 3.11**（通过 uv 安装，无需 sudo）
- **Node.js v22**（用于浏览器自动化和 WhatsApp 桥接）
- **ripgrep**（快速文件搜索）
- **ffmpeg**（用于 TTS 的音频格式转换）

:::info
你**不需要**手动安装 Python、Node.js、ripgrep 或 ffmpeg。安装程序会检测缺少什么并为你安装。只需确保 `git` 可用即可（`git --version`）。
:::
:::tip Nix 用户
如果你使用 Nix（在 NixOS、macOS 或 Linux 上），我们提供了专门的设置路径，包含 Nix flake、声明式 NixOS 模块和可选的容器模式。请参阅 **[Nix & NixOS 设置](./nix-setup.md)** 指南。
<a id="nix-users"></a>
:::

---

<a id="manual-developer-installation"></a>
## 手动 / 开发者安装

如果你想克隆仓库并从源码安装——例如为了贡献代码、运行特定分支或完全控制虚拟环境——请参阅贡献指南中的 [开发环境设置](../developer-guide/contributing.md#development-setup) 部分。

---

<a id="troubleshooting"></a>
## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `hermes: command not found` | 重新加载你的 shell（`source ~/.bashrc`）或检查 PATH 环境变量 |
| `API key not set` | 运行 `hermes model` 来配置你的提供商，或运行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后配置丢失 | 运行 `hermes config check`，然后运行 `hermes config migrate` |

如需更多诊断信息，请运行 `hermes doctor` —— 它会准确地告诉你缺少什么以及如何修复。
