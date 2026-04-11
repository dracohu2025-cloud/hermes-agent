---
sidebar_position: 3
title: "Android / Termux"
description: "在 Android 手机上通过 Termux 直接运行 Hermes Agent"
---

# 在 Android 上通过 Termux 使用 Hermes

这是目前在 Android 手机上通过 [Termux](https://termux.dev/) 直接运行 Hermes Agent 的已验证路径。

它为你提供了一个可在手机上运行的本地 CLI，以及目前已知能在 Android 上顺利安装的核心扩展功能。

## 已验证路径支持哪些功能？

已验证的 Termux 软件包安装内容包括：
- Hermes CLI
- cron 支持
- PTY/后台终端支持
- MCP 支持
- Honcho 内存支持
- ACP 支持

具体来说，它对应于：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

## 哪些功能尚不在已验证路径中？

部分功能仍需要桌面/服务器级的依赖项，这些依赖项尚未发布 Android 版本，或者尚未在手机上进行验证：

- 目前 Android 不支持 `.[all]`
- `voice` 扩展受限于 `faster-whisper -> ctranslate2`，而 `ctranslate2` 尚未发布 Android wheel 包
- Termux 安装程序跳过了自动浏览器 / Playwright 引导程序
- Termux 内部无法使用基于 Docker 的终端隔离

这并不妨碍 Hermes 作为手机原生 CLI Agent 良好运行——这只是意味着推荐的移动端安装范围有意比桌面/服务器端安装更精简。

---

## 选项 1：一键安装程序

Hermes 现在提供了一个支持 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

在 Termux 上，该安装程序会自动：
- 使用 `pkg` 安装系统软件包
- 使用 `python -m venv` 创建虚拟环境
- 使用 `pip` 安装 `.[termux]`
- 将 `hermes` 链接到 `$PREFIX/bin`，以便它保留在你的 Termux PATH 中
- 跳过未经测试的浏览器 / WhatsApp 引导程序

如果你需要明确的命令或需要调试安装失败的问题，请使用下方的手动安装路径。

---

## 选项 2：手动安装（完全显式）

### 1. 更新 Termux 并安装系统软件包

```bash
pkg update
pkg install -y git python clang rust make pkg-config libffi openssl nodejs ripgrep ffmpeg
```

为什么要安装这些软件包？
- `python` — 运行时 + venv 支持
- `git` — 克隆/更新仓库
- `clang`, `rust`, `make`, `pkg-config`, `libffi`, `openssl` — 在 Android 上构建某些 Python 依赖项所需
- `nodejs` — 可选的 Node 运行时，用于核心路径之外的实验性功能
- `ripgrep` — 快速文件搜索
- `ffmpeg` — 媒体 / TTS 转换

### 2. 克隆 Hermes

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

如果你之前克隆时没有包含子模块：

```bash
git submodule update --init --recursive
```

### 3. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
```

`ANDROID_API_LEVEL` 对于基于 Rust / maturin 的软件包（如 `jiter`）非常重要。

### 4. 安装已验证的 Termux 软件包

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

如果你只需要最小化的核心 Agent，也可以使用：

```bash
python -m pip install -e '.' -c constraints-termux.txt
```

### 5. 将 `hermes` 加入你的 Termux PATH

```bash
ln -sf "$PWD/venv/bin/hermes" "$PREFIX/bin/hermes"
```

`$PREFIX/bin` 在 Termux 中已包含在 PATH 中，因此这使得 `hermes` 命令在新的 shell 中持久有效，无需每次都重新激活 venv。

### 6. 验证安装

```bash
hermes version
hermes doctor
```

### 7. 启动 Hermes

```bash
hermes
```

---

## 推荐的后续设置

### 配置模型

```bash
hermes model
```

或者直接在 `~/.hermes/.env` 中设置密钥。

### 稍后重新运行完整的交互式设置向导

```bash
hermes setup
```

### 手动安装可选的 Node 依赖项

已验证的 Termux 路径特意跳过了 Node/浏览器引导程序。如果你以后想进行实验：

```bash
npm install
```

在有相关文档说明之前，请将 Android 上的浏览器 / WhatsApp 工具视为实验性功能。

---

## 故障排除

### 安装 `.[all]` 时提示 `No solution found`

请改用已验证的 Termux 软件包：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

目前的阻碍是 `voice` 扩展：
- `voice` 会拉取 `faster-whisper`
- `faster-whisper` 依赖于 `ctranslate2`
- `ctranslate2` 没有发布 Android wheel 包

### `uv pip install` 在 Android 上失败

请改用带有 stdlib venv + `pip` 的 Termux 路径：

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `jiter` / `maturin` 报错 `ANDROID_API_LEVEL`

在安装前显式设置 API 级别：

```bash
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `hermes doctor` 提示缺少 ripgrep 或 Node

使用 Termux 软件包安装它们：

```bash
pkg install ripgrep nodejs
```

### 安装 Python 软件包时构建失败

确保已安装构建工具链：

```bash
pkg install clang rust make pkg-config libffi openssl
```

然后重试：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

---

## 手机端的已知限制

- Docker 后端不可用
- 已验证路径中不支持通过 `faster-whisper` 进行本地语音转录
- 安装程序有意跳过了浏览器自动化设置
- 某些可选扩展可能可以使用，但目前仅记录了 `.[termux]` 作为已验证的 Android 软件包

如果你遇到了新的 Android 特定问题，请在 GitHub 上提交 issue，并提供：
- 你的 Android 版本
- `termux-info` 的输出
- `python --version` 的输出
- `hermes doctor` 的输出
- 确切的安装命令和完整的错误输出
