---
sidebar_position: 2
title: "安装"
description: "在 Linux、macOS、WSL2 或 Android (通过 Termux) 上安装 Hermes Agent"
---

# 安装

使用一行安装命令，不到两分钟即可运行 Hermes Agent，或者按照手动步骤进行完全控制。

## 快速安装

### Linux / macOS / WSL2

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Android / Termux

Hermes 现在也提供了适配 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

安装程序会自动检测 Termux 并切换到经过测试的 Android 流程：
- 使用 Termux 的 `pkg` 安装系统依赖（`git`、`python`、`nodejs`、`ripgrep`、`ffmpeg`、构建工具）
- 使用 `python -m venv` 创建虚拟环境
- 自动为 Android wheel 构建导出 `ANDROID_API_LEVEL`
- 使用 `pip` 安装精选的 `.[termux]` 扩展包
- 默认跳过未经测试的浏览器 / WhatsApp 引导程序

如果您需要完全明确的安装路径，请参考专门的 [Termux 指南](./termux.md)。

:::warning Windows
不支持原生 Windows。请安装 [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) 并在其中运行 Hermes Agent。上述安装命令在 WSL2 中可以正常工作。
:::

### 安装程序做了什么

安装程序会自动处理一切——包括所有依赖项（Python、Node.js、ripgrep、ffmpeg）、仓库克隆、虚拟环境、全局 `hermes` 命令设置以及 LLM 提供商配置。完成后，您就可以直接开始对话了。

### 安装后

重新加载您的 shell 并开始对话：

```bash
source ~/.bashrc   # 或者: source ~/.zshrc
hermes             # 开始对话！
```

若要稍后重新配置各项设置，请使用专用命令：

```bash
hermes model          # 选择您的 LLM 提供商和模型
hermes tools          # 配置启用的工具
hermes gateway setup  # 设置消息平台
hermes config set     # 设置单个配置值
hermes setup          # 或者运行完整的设置向导来一次性配置所有内容
```

---

## 先决条件

唯一的先决条件是 **Git**。安装程序会自动处理其他所有内容：

- **uv**（快速 Python 包管理器）
- **Python 3.11**（通过 uv 安装，无需 sudo）
- **Node.js v22**（用于浏览器自动化和 WhatsApp 桥接）
- **ripgrep**（快速文件搜索）
- **ffmpeg**（用于 TTS 的音频格式转换）

:::info
您**无需**手动安装 Python、Node.js、ripgrep 或 ffmpeg。安装程序会检测缺失的内容并为您安装。只需确保系统中有 `git` 即可（运行 `git --version` 检查）。
:::

:::tip Nix 用户
如果您使用 Nix（在 NixOS、macOS 或 Linux 上），我们提供了专门的设置路径，包含 Nix flake、声明式 NixOS 模块以及可选的容器模式。请参阅 **[Nix & NixOS 设置](./nix-setup.md)** 指南。
:::

---

## 手动安装

如果您希望完全控制安装过程，请按照以下步骤操作。

### 第 1 步：克隆仓库

使用 `--recurse-submodules` 克隆以拉取所需的子模块：

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

如果您之前克隆时没有使用 `--recurse-submodules`：
```bash
git submodule update --init --recursive
```

### 第 2 步：安装 uv 并创建虚拟环境

```bash
# 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用 Python 3.11 创建 venv (如果不存在，uv 会自动下载 — 无需 sudo)
uv venv venv --python 3.11
```

:::tip
您**无需**激活 venv 即可使用 `hermes`。入口点有一个硬编码的 shebang 指向 venv 中的 Python，因此一旦创建软链接，它就可以全局运行。
:::

### 第 3 步：安装 Python 依赖

```bash
# 告诉 uv 安装到哪个 venv
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有扩展包
uv pip install -e ".[all]"
```

如果您只需要核心 Agent（不需要 Telegram/Discord/cron 支持）：
```bash
uv pip install -e "."
```

<details>
<summary><strong>可选扩展包说明</strong></summary>

| 扩展包 | 添加的功能 | 安装命令 |
|-------|-------------|-----------------|
| `all` | 包含下方所有内容 | `uv pip install -e ".[all]"` |
| `messaging` | Telegram 和 Discord 网关 | `uv pip install -e ".[messaging]"` |
| `cron` | 用于定时任务的 Cron 表达式解析 | `uv pip install -e ".[cron]"` |
| `cli` | 设置向导的终端菜单 UI | `uv pip install -e ".[cli]"` |
| `modal` | Modal 云执行后端 | `uv pip install -e ".[modal]"` |
| `tts-premium` | ElevenLabs 高级语音 | `uv pip install -e ".[tts-premium]"` |
| `voice` | CLI 麦克风输入 + 音频播放 | `uv pip install -e ".[voice]"` |
| `pty` | PTY 终端支持 | `uv pip install -e ".[pty]"` |
| `termux` | 经过测试的 Android / Termux 包 (`cron`, `cli`, `pty`, `mcp`, `honcho`, `acp`) | `python -m pip install -e ".[termux]" -c constraints-termux.txt` |
| `honcho` | AI 原生记忆 (Honcho 集成) | `uv pip install -e ".[honcho]"` |
| `mcp` | Model Context Protocol 支持 | `uv pip install -e ".[mcp]"` |
| `homeassistant` | Home Assistant 集成 | `uv pip install -e ".[homeassistant]"` |
| `acp` | ACP 编辑器集成支持 | `uv pip install -e ".[acp]"` |
| `slack` | Slack 消息 | `uv pip install -e ".[slack]"` |
| `dev` | pytest 和测试工具 | `uv pip install -e ".[dev]"` |

您可以组合使用扩展包：`uv pip install -e ".[messaging,cron]"`

:::tip Termux 用户
`.[all]` 目前在 Android 上不可用，因为 `voice` 扩展包依赖 `faster-whisper`，而它依赖的 `ctranslate2` wheel 未发布 Android 版本。请使用 `.[termux]` 进行经过测试的移动端安装，然后根据需要添加个别扩展包。
:::

</details>

### 第 4 步：安装可选子模块（如果需要）

```bash
# RL 训练后端 (可选)
uv pip install -e "./tinker-atropos"
```

两者都是可选的——如果您跳过它们，相应的工具集将无法使用。

### 第 5 步：安装 Node.js 依赖（可选）

仅在需要**浏览器自动化**（由 Browserbase 提供支持）和 **WhatsApp 桥接**时才需要：

```bash
npm install
```

### 第 6 步：创建配置目录

```bash
# 创建目录结构
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,image_cache,audio_cache,whatsapp/session}

# 复制示例配置文件
cp cli-config.yaml.example ~/.hermes/config.yaml

# 为 API 密钥创建一个空的 .env 文件
touch ~/.hermes/.env
```

### 第 7 步：添加您的 API 密钥

打开 `~/.hermes/.env` 并至少添加一个 LLM 提供商密钥：

```bash
# 必需 — 至少一个 LLM 提供商：
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# 可选 — 启用其他工具：
FIRECRAWL_API_KEY=fc-your-key          # 网络搜索与抓取 (或自托管，请参阅文档)
FAL_KEY=your-fal-key                   # 图像生成 (FLUX)
```

或者通过 CLI 设置：
```bash
hermes config set OPENROUTER_API_KEY sk-or-v1-your-key-here
```

### 第 8 步：将 `hermes` 添加到您的 PATH

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
```

如果 `~/.local/bin` 不在您的 PATH 中，请将其添加到 shell 配置中：

```bash
# Bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc

# Zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

# Fish
fish_add_path $HOME/.local/bin
```

### 第 9 步：配置您的提供商

```bash
hermes model       # 选择您的 LLM 提供商和模型
```

### 第 10 步：验证安装

```bash
hermes version    # 检查命令是否可用
hermes doctor     # 运行诊断以验证一切是否正常
hermes status     # 检查您的配置
hermes chat -q "Hello! What tools do you have available?"
```

---

## 快速参考：手动安装（精简版）

对于只需要命令的用户：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆并进入目录
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 使用 Python 3.11 创建 venv
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有内容
uv pip install -e ".[all]"
uv pip install -e "./tinker-atropos"
npm install  # 可选，用于浏览器工具和 WhatsApp

# 配置
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,image_cache,audio_cache,whatsapp/session}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' >> ~/.hermes/.env

# 使 hermes 全局可用
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes

# 验证
hermes doctor
hermes
```
---

## 故障排查

| 问题 | 解决方案 |
|---------|----------|
| `hermes: command not found` | 重新加载你的 shell（执行 `source ~/.bashrc`）或检查 PATH 环境变量 |
| `API key not set` | 运行 `hermes model` 来配置你的提供商，或运行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后配置丢失 | 运行 `hermes config check`，然后运行 `hermes config migrate` |

如需更多诊断信息，请运行 `hermes doctor` —— 它会准确告诉你缺少什么以及如何修复。
