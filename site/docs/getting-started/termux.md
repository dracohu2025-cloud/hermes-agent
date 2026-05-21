---
sidebar_position: 3
title: "Android / Termux"
description: "通过 Termux 在 Android 手机上直接运行 Hermes Agent"
---

<a id="hermes-on-android-with-termux"></a>
# 在 Android 上通过 Termux 使用 Hermes

这是经过验证的、通过 [Termux](https://termux.dev/) 在 Android 手机上直接运行 Hermes Agent 的路径。

它会在手机上提供一个可用的本地 CLI，以及当前已知能在 Android 上干净安装的核心扩展。

<a id="what-is-supported-in-the-tested-path"></a>
## 已验证路径支持哪些功能？

经过验证的 Termux 捆绑包会安装：
- Hermes CLI
- cron 支持
- PTY/后台终端支持
- Telegram 网关支持（手动 / 尽力运行后台）
- MCP 支持
- Honcho 内存支持
- ACP 支持

具体来说，它对应于：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

<a id="what-is-not-part-of-the-tested-path-yet"></a>
## 哪些功能还不属于已验证路径？

部分功能仍然依赖桌面/服务器风格的依赖项，这些依赖项要么没有针对 Android 发布，要么尚未在手机上验证：

- `.[all]` 目前在 Android 上不受支持
- `voice` 扩展被 `faster-whisper -> ctranslate2` 阻断，且 `ctranslate2` 不发布 Android wheel
- Termux 安装程序中会跳过自动浏览器 / Playwright 引导
- Termux 内部无法使用基于 Docker 的终端隔离
- Android 仍可能暂停 Termux 的后台任务，因此网关持久化是尽力而为，而非正常的托管服务

这并不妨碍 Hermes 作为手机原生 CLI Agent 正常工作——只是意味着推荐的移动端安装范围有意比桌面/服务器端安装更窄。

---

<a id="option-1-one-line-installer"></a>
## 选项 1：一行安装器

Hermes 目前提供适配 Termux 的安装路径：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

在 Termux 上，安装器会自动：
- 使用 `pkg` 安装系统包
- 通过 `python -m venv` 创建虚拟环境
- 首先尝试较大的 `.[termux-all]` 扩展，若失败则回退到较小的 `.[termux]` 扩展（再回退到基础安装）—— curl 安装器会自动按此顺序匹配
- 将 `hermes` 链接到 `$PREFIX/bin` 中，使其始终存在于 Termux 的 PATH 中
- 跳过未经验证的浏览器 / WhatsApp 引导

如果你需要显式命令或需要调试安装失败，请使用下面的手动安装路径。

---

<a id="option-2-manual-install-fully-explicit"></a>
## 选项 2：手动安装（完全显式）

<a id="1-update-termux-and-install-system-packages"></a>
### 1. 更新 Termux 并安装系统包

```bash
pkg update
pkg install -y git python clang rust make pkg-config libffi openssl nodejs ripgrep ffmpeg
```

为什么需要这些包？
- `python` — 运行时 + venv 支持
- `git` — 克隆/更新仓库
- `clang`, `rust`, `make`, `pkg-config`, `libffi`, `openssl` — 用于在 Android 上编译部分 Python 依赖
- `nodejs` — 可选，用于在核心测试路径之外进行 Node 运行时实验
- `ripgrep` — 快速文件搜索
- `ffmpeg` — 媒体 / TTS 转换

<a id="2-clone-hermes"></a>
### 2. 克隆 Hermes

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

如果已经克隆但没有子模块：

```bash
git submodule update --init --recursive
```

<a id="3-create-a-virtual-environment"></a>
### 3. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
```
`ANDROID_API_LEVEL` 对于基于 Rust / maturin 的包（例如 `jiter`）很重要。

<a id="4-install-the-tested-termux-bundle"></a>
### 4. 安装经过测试的 Termux 包

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

如果你只需要最简核心 Agent，也可以这样：

```bash
python -m pip install -e '.' -c constraints-termux.txt
```

<a id="5-put-hermes-on-your-termux-path"></a>
### 5. 将 `hermes` 添加到 Termux 的 PATH 中

```bash
ln -sf "$PWD/venv/bin/hermes" "$PREFIX/bin/hermes"
```

`$PREFIX/bin` 已经在 Termux 的 PATH 中，这样 `hermes` 命令就能在新 shell 中持续可用，无需每次都重新激活 venv。

<a id="6-verify-the-install"></a>
### 6. 验证安装

```bash
hermes version
hermes doctor
```

<a id="7-start-hermes"></a>
### 7. 启动 Hermes

```bash
hermes
```

---

<a id="recommended-follow-up-setup"></a>
## 推荐的后续设置

<a id="configure-a-model"></a>
### 配置模型

```bash
hermes model
```

或者直接在 `~/.hermes/.env` 中设置密钥。

<a id="re-run-the-full-interactive-setup-wizard-later"></a>
### 稍后重新运行完整的交互式设置向导

```bash
hermes setup
```

<a id="install-optional-node-dependencies-manually"></a>
### 手动安装可选的 Node 依赖

经过测试的 Termux 路径有意跳过了 Node/浏览器引导。如果你之后想尝试浏览器工具：

```bash
pkg install nodejs-lts
npm install
```

浏览器工具会自动将 Termux 目录（`/data/data/com.termux/files/usr/bin`）包含在其 PATH 搜索中，因此无需额外 PATH 配置即可发现 `agent-browser` 和 `npx`。

在另有文档说明之前，请将 Android 上的浏览器 / WhatsApp 工具视为实验性功能。

---

<a id="troubleshooting"></a>
## 故障排除

<a id="no-solution-found-when-installing-all"></a>
### 安装 `.[all]` 时出现 `No solution found`

请改用经过测试的 Termux 包：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

目前阻塞点在于 `voice` 附加组件：
- `voice` 会拉取 `faster-whisper`
- `faster-whisper` 依赖 `ctranslate2`
- `ctranslate2` 没有发布 Android 的 wheel 包

<a id="uv-pip-install-fails-on-android"></a>
### `uv pip install` 在 Android 上失败

请改用 Termux 路径，配合 stdlib venv + `pip`：

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

<a id="jiter-maturin-complains-about-androidapilevel"></a>
### `jiter` / `maturin` 报错 `ANDROID_API_LEVEL`

在安装前显式设置 API 级别：

```bash
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

<a id="hermes-doctor-says-ripgrep-or-node-is-missing"></a>
### `hermes doctor` 提示缺少 ripgrep 或 Node

使用 Termux 包管理器安装它们：

```bash
pkg install ripgrep nodejs
```

<a id="build-failures-while-installing-python-packages"></a>
### 安装 Python 包时构建失败

确保已安装构建工具链：

```bash
pkg install clang rust make pkg-config libffi openssl
```

然后重试：

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

---

<a id="known-limitations-on-phones"></a>
## 手机上的已知限制

- Docker 后端不可用
- 在测试路径中，通过 `faster-whisper` 进行的本地语音转录不可用
- 安装程序有意跳过了浏览器自动化设置
- 某些可选附加组件可能可以工作，但目前只有 `.[termux]` 和 `.[termux-all]` 被记录为经过测试的 Android 包
如果你遇到了新的 Android 特有（或特定于 Android）的问题，请在 GitHub 上提交 issue，并附上以下信息：
- 你的 Android 版本
- `termux-info`
- `python --version`
- `hermes doctor`
- 确切的安装命令和完整的错误输出
