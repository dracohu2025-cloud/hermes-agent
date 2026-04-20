---
sidebar_position: 3
title: "Android / Termux"
description: "通过 Termux 在 Android 手机上直接运行 Hermes Agent"
---

# 通过 Termux 在 Android 上运行 Hermes {#hermes-on-android-with-termux}

这是经过测试的、通过 [Termux](https://termux.dev/) 在 Android 手机上直接运行 Hermes Agent 的路径。

它能让你在手机上获得一个可用的本地 CLI，以及目前已知能在 Android 上干净安装的核心扩展功能。

## 测试路径支持哪些功能？ {#what-is-supported-in-the-tested-path}

经过测试的 Termux 捆绑包会安装：
- Hermes CLI
- cron 支持
- PTY/后台终端支持
- Telegram gateway 支持（手动/尽力而为的后台运行）
- MCP 支持
- Honcho 记忆支持
- ACP 支持

具体对应：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

## 测试路径尚未包含哪些功能？ {#what-is-not-part-of-the-tested-path-yet}

部分功能仍需要桌面/服务器风格的依赖，而这些依赖尚未发布 Android 版本，或尚未在手机上验证：

- `.[all]` 目前不支持 Android
- `voice` 扩展被 `faster-whisper -> ctranslate2` 阻塞，`ctranslate2` 不发布 Android wheel
- Termux 安装程序会自动跳过浏览器 / Playwright 的自动配置
- Termux 内无法使用基于 Docker 的终端隔离
- Android 仍可能挂起 Termux 后台任务，因此 gateway 持久化是尽力而为，而非正常的托管服务

这并不妨碍 Hermes 作为手机原生 CLI Agent 良好运行——只是说明推荐的移动安装有意比桌面/服务器安装更精简。

---

## 方案一：一行命令安装 {#option-1-one-line-installer}

Hermes 现在提供 Termux 感知的一键安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

在 Termux 上，安装程序会自动：
- 使用 `pkg` 安装系统包
- 用 `python -m venv` 创建虚拟环境
- 用 `pip` 安装 `.[termux]`
- 将 `hermes` 链接到 `$PREFIX/bin`，使其保持在 Termux PATH 中
- 跳过未经测试的浏览器 / WhatsApp 自动配置

如果你需要显式命令或排查安装失败，请使用下面的手动路径。

---

## 方案二：手动安装（完全显式） {#option-2-manual-install-fully-explicit}

### 1. 更新 Termux 并安装系统包 {#1-update-termux-and-install-system-packages}

```bash
pkg update
pkg install -y git python clang rust make pkg-config libffi openssl nodejs ripgrep ffmpeg
```

为什么需要这些包？
- `python` — 运行时 + venv 支持
- `git` — 克隆/更新仓库
- `clang`、`rust`、`make`、`pkg-config`、`libffi`、`openssl` — 在 Android 上构建部分 Python 依赖所需
- `nodejs` — 可选的 Node 运行时，用于测试核心路径之外的实验
- `ripgrep` — 快速文件搜索
- `ffmpeg` — 媒体 / TTS 转换

### 2. 克隆 Hermes {#2-clone-hermes}

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

如果你之前克隆时没拉子模块：

```bash
git submodule update --init --recursive
```

### 3. 创建虚拟环境 {#3-create-a-virtual-environment}

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
```

`ANDROID_API_LEVEL` 对基于 Rust / maturin 的包（如 `jiter`）很重要。

### 4. 安装经过测试的 Termux 捆绑包 {#4-install-the-tested-termux-bundle}

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

如果你只想要最小化的核心 Agent，这条也可以：

```bash
python -m pip install -e '.' -c constraints-termux.txt
```

### 5. 将 `hermes` 放到 Termux PATH 中 {#5-put-hermes-on-your-termux-path}

```bash
ln -sf "$PWD/venv/bin/hermes" "$PREFIX/bin/hermes"
```

`$PREFIX/bin` 已经在 Termux 的 PATH 中，这样 `hermes` 命令就能在新 shell 中持久可用，无需每次重新激活 venv。

### 6. 验证安装 {#6-verify-the-install}

```bash
hermes version
hermes doctor
```

### 7. 启动 Hermes {#7-start-hermes}

```bash
hermes
```

---

## 推荐的后续设置 {#recommended-follow-up-setup}

### 配置模型 {#configure-a-model}

```bash
hermes model
```

或直接在 `~/.hermes/.env` 中设置密钥。

### 稍后重新运行完整的交互式设置向导 {#re-run-the-full-interactive-setup-wizard-later}

```bash
hermes setup
```

### 手动安装可选的 Node 依赖 {#install-optional-node-dependencies-manually}

经过测试的 Termux 路径有意跳过 Node/浏览器自动配置。如果你之后想尝试浏览器工具：
```bash
pkg install nodejs-lts
npm install
```

浏览器工具会自动将 Termux 目录（`/data/data/com.termux/files/usr/bin`）纳入 PATH 搜索，因此无需额外配置 PATH 就能找到 `agent-browser` 和 `npx`。

在另有文档说明之前，请把 Android 上的浏览器 / WhatsApp 工具视为实验性功能。

---

## 故障排查 {#troubleshooting}

### 安装 `.[all]` 时出现 `No solution found` {#no-solution-found-when-installing-all}

请改用经过测试的 Termux 依赖包：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

目前的阻塞点是 `voice` 额外依赖：
- `voice` 会拉取 `faster-whisper`
- `faster-whisper` 依赖 `ctranslate2`
- `ctranslate2` 没有发布 Android  wheel 包

### `uv pip install` 在 Android 上失败 {#uv-pip-install-fails-on-android}

改用 Termux 路径下的标准库 venv + `pip`：

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `jiter` / `maturin` 提示缺少 `ANDROID_API_LEVEL` {#jiter-maturin-complains-about-androidapilevel}

在安装前显式设置 API 级别：

```bash
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

### `hermes doctor` 提示缺少 ripgrep 或 Node {#hermes-doctor-says-ripgrep-or-node-is-missing}

通过 Termux 包管理器安装：

```bash
pkg install ripgrep nodejs
```

### 安装 Python 包时构建失败 {#build-failures-while-installing-python-packages}

确保已安装构建工具链：

```bash
pkg install clang rust make pkg-config libffi openssl
```

然后重试：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

---

## 手机上的已知限制 {#known-limitations-on-phones}

- Docker 后端不可用
- 通过 `faster-whisper` 进行本地语音转写在当前测试路径下不可用
- 浏览器自动化安装被安装程序有意跳过
- 部分可选额外依赖可能能用，但目前只有 `.[termux]` 是经过测试并文档化的 Android 依赖包

如果你遇到新的 Android 专属问题，请提交 GitHub issue，并附上：
- 你的 Android 版本
- `termux-info` 输出
- `python --version` 输出
- `hermes doctor` 输出
- 确切的安装命令和完整的错误输出
