---
title: 视觉与图像粘贴
description: 将剪贴板中的图像粘贴到 Hermes CLI 中，进行多模态视觉分析。
sidebar_label: 视觉与图像粘贴
sidebar_position: 7
---

# 视觉与图像粘贴 {#vision-image-paste}

Hermes Agent 支持**多模态视觉**——你可以将剪贴板中的图像直接粘贴到 CLI 中，让 Agent 分析、描述或处理它们。图像会以 base64 编码的内容块形式发送给模型，因此任何支持视觉的模型都能处理。

## 工作原理 {#how-it-works}

1. 将图像复制到剪贴板（截图、浏览器图片等）
2. 使用以下方法之一附加图像
3. 输入你的问题并按回车
4. 图像会以 `[📎 Image #1]` 徽章的形式显示在输入框上方
5. 提交后，图像会作为视觉内容块发送给模型

你可以在发送前附加多张图像——每张图像都会获得自己的徽章。按 `Ctrl+C` 清除所有已附加的图像。

图像会以 PNG 文件形式保存到 `~/.hermes/images/`，文件名带有时间戳。

## 粘贴方法 {#paste-methods}

如何附加图像取决于你的终端环境。并非所有方法在所有地方都有效——以下是完整说明：

### `/paste` 命令 {#paste-command}

**最可靠的显式图像附加备用方案。**

```
/paste
```

输入 `/paste` 并按回车。Hermes 会检查你的剪贴板中是否有图像并将其附加。当你的终端重写了 `Cmd+V`/`Ctrl+V`，或者你只复制了图像且没有可检查的括号粘贴文本负载时，这是最安全的选择。

### Ctrl+V / Cmd+V {#ctrl-v-cmd-v}

Hermes 现在将粘贴视为分层流程：
- 首先处理普通文本粘贴
- 如果终端未能干净地传递文本，则使用原生剪贴板 / OSC52 文本备用方案
- 当剪贴板或粘贴负载解析为图像或图像路径时，附加图像

这意味着粘贴的 macOS 截图临时路径和 `file://...` 图像 URI 可以立即附加，而不会作为原始文本停留在编辑器中。

:::warning
如果你的剪贴板中**只有图像**（没有文本），终端仍然无法直接发送二进制图像字节。请使用 `/paste` 作为显式图像附加备用方案。
:::

### 针对 VS Code / Cursor / Windsurf 的 `/terminal-setup` {#terminal-setup-for-vs-code-cursor-windsurf}

如果你在 macOS 上的本地 VS Code 系列集成终端中运行 TUI，Hermes 可以安装推荐的 `workbench.action.terminal.sendSequence` 绑定，以获得更好的多行和撤销/重做一致性：

```text
/terminal-setup
```

当 `Cmd+Enter`、`Cmd+Z` 或 `Shift+Cmd+Z` 被 IDE 拦截时，这尤其有用。仅在本地机器上运行——不要在 SSH 会话中运行。

## 平台兼容性 {#platform-compatibility}

| 环境 | `/paste` | Cmd/Ctrl+V | `/terminal-setup` | 备注 |
|---|:---:|:---:|:---:|---|
| **macOS Terminal / iTerm2** | ✅ | ✅ | n/a | 最佳体验——原生剪贴板 + 截图路径恢复 |
| **Apple Terminal** | ✅ | ✅ | n/a | 如果 Cmd+←/→/⌫ 被重写，请使用 Ctrl+A / Ctrl+E / Ctrl+U 备用方案 |
| **Linux X11 桌面** | ✅ | ✅ | n/a | 需要 `xclip`（`apt install xclip`） |
| **Linux Wayland 桌面** | ✅ | ✅ | n/a | 需要 `wl-paste`（`apt install wl-clipboard`） |
| **WSL2（Windows Terminal）** | ✅ | ✅ | n/a | 使用 `powershell.exe`——无需额外安装 |
| **VS Code / Cursor / Windsurf（本地）** | ✅ | ✅ | ✅ | 推荐用于更好的 Cmd+Enter / 撤销 / 重做一致性 |
| **VS Code / Cursor / Windsurf（SSH）** | ❌² | ❌² | ❌³ | 改为在本地机器上运行 `/terminal-setup` |
| **SSH 终端（任意）** | ❌² | ❌² | n/a | 无法访问远程剪贴板 |
² 参见下方的 [SSH 与远程会话](#ssh--remote-sessions)  
³ 该命令写入本地 IDE 快捷键绑定，不应在远程主机上运行  

## 平台特定设置 {#platform-specific-setup}

### macOS {#macos}

**无需额外设置。** Hermes 使用 `osascript`（macOS 内置）读取剪贴板。如需更快的性能，可选择性安装 `pngpaste`：

```bash
brew install pngpaste
```

### Linux (X11) {#linux-x11}

安装 `xclip`：

```bash
# Ubuntu/Debian
sudo apt install xclip

# Fedora
sudo dnf install xclip

# Arch
sudo pacman -S xclip
```

### Linux (Wayland) {#linux-wayland}

现代 Linux 桌面（Ubuntu 22.04+、Fedora 34+）通常默认使用 Wayland。安装 `wl-clipboard`：

```bash
# Ubuntu/Debian
sudo apt install wl-clipboard

# Fedora
sudo dnf install wl-clipboard

# Arch
sudo pacman -S wl-clipboard
```

:::tip 如何检查你是否在使用 Wayland
```bash
echo $XDG_SESSION_TYPE
# "wayland" = Wayland, "x11" = X11, "tty" = 无显示服务器
<a id="how-to-check-if-you-re-on-wayland"></a>
```
:::

### WSL2 {#wsl2}

**无需额外设置。** Hermes 会自动检测 WSL2（通过 `/proc/version`），并使用 `powershell.exe` 通过 .NET 的 `System.Windows.Forms.Clipboard` 访问 Windows 剪贴板。这是 WSL2 的 Windows 互操作功能内置的——`powershell.exe` 默认可用。

剪贴板数据会以 base64 编码的 PNG 格式通过 stdout 传输，因此无需文件路径转换或临时文件。

:::info WSLg 说明
如果你正在运行 WSLg（带 GUI 支持的 WSL2），Hermes 会先尝试 PowerShell 路径，如果失败则回退到 `wl-paste`。WSLg 的剪贴板桥仅支持 BMP 格式的图片——Hermes 会自动使用 Pillow（如果已安装）或 ImageMagick 的 `convert` 命令将 BMP 转换为 PNG。
:::
<a id="wslg-note"></a>

#### 验证 WSL2 剪贴板访问 {#verify-wsl2-clipboard-access}

```bash
# 1. 检查 WSL 检测
grep -i microsoft /proc/version

# 2. 检查 PowerShell 是否可访问
which powershell.exe

# 3. 复制一张图片，然后检查
powershell.exe -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::ContainsImage()"
# 应输出 "True"
```

<a id="ssh-remote-sessions"></a>
## SSH 与远程会话 {#ssh--remote-sessions}

**通过 SSH 时，剪贴板图片粘贴无法完全正常工作。** 当你通过 SSH 连接到远程机器时，Hermes CLI 运行在远程主机上。剪贴板工具（`xclip`、`wl-paste`、`powershell.exe`、`osascript`）读取的是它们所在机器的剪贴板——也就是远程服务器，而不是你的本地机器。因此，远程端无法访问你本地的剪贴板图片。

文本有时仍可通过终端粘贴或 OSC52 桥接，但图片剪贴板访问和本地截图临时路径仍然绑定在运行 Hermes 的机器上。

### SSH 的替代方案 {#workarounds-for-ssh}

1. **上传图片文件**——将图片保存到本地，通过 `scp`、VSCode 的文件资源管理器（拖放）或任何文件传输方法上传到远程服务器。然后通过路径引用它。*（计划在未来的版本中增加 `/attach <文件路径>` 命令。）*

2. **使用 URL**——如果图片可以在线访问，只需在消息中粘贴 URL。Agent 可以直接使用 `vision_analyze` 查看任何图片 URL。

3. **X11 转发**——使用 `ssh -X` 连接以转发 X11。这允许远程机器上的 `xclip` 访问你本地的 X11 剪贴板。需要本地运行 X 服务器（macOS 上为 XQuartz，Linux X11 桌面内置）。对于大图片速度较慢。
4. **使用消息平台** — 通过 Telegram、Discord、Slack 或 WhatsApp 将图片发送给 Hermes。这些平台原生支持图片上传，不受剪贴板/终端限制的影响。

## 为什么终端无法粘贴图片 {#why-terminals-can-t-paste-images}

这是一个常见的困惑点，以下是技术解释：

终端是**基于文本**的界面。当你按下 Ctrl+V（或 Cmd+V）时，终端模拟器会：

1. 从剪贴板读取**文本内容**
2. 将其包裹在[括号粘贴](https://en.wikipedia.org/wiki/Bracketed-paste)转义序列中
3. 通过终端的文本流发送给应用程序

如果剪贴板只包含图片（没有文本），终端就没有内容可发送。没有标准的终端转义序列用于二进制图片数据。终端只会什么都不做。

这就是为什么 Hermes 使用单独的剪贴板检查 — 它不是通过终端粘贴事件接收图片数据，而是通过子进程直接调用操作系统级工具（`osascript`、`powershell.exe`、`xclip`、`wl-paste`）来独立读取剪贴板。

## 支持的模型 {#supported-models}

图片粘贴适用于任何支持视觉能力的模型。图片以 base64 编码的数据 URL 形式发送，采用 OpenAI 视觉内容格式：

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/png;base64,..."
  }
}
```

大多数现代模型都支持这种格式，包括 GPT-4 Vision、Claude（带视觉能力）、Gemini 以及通过 OpenRouter 提供的开源多模态模型。

## 图片路由（支持视觉 vs 纯文本模型） {#image-routing-vision-capable-vs-text-only-models}

当用户附加图片时 — 无论是来自 CLI 剪贴板、网关（Telegram/Discord 照片）还是其他入口点 — Hermes 会根据你当前使用的模型是否真正支持视觉能力来进行路由：

| 你的模型 | 图片的处理方式 |
|---|---|
| **支持视觉**（GPT-4V、带视觉的 Claude、Gemini、Qwen-VL、MiMo-VL 等） | 使用上述提供商的本地图片内容格式，作为**真实像素**发送。没有文本摘要层。 |
| **纯文本**（DeepSeek V3、较小的开源模型、较旧的纯聊天端点） | 通过 `vision_analyze` 辅助工具路由 — 一个辅助视觉模型描述图片，然后将文本描述注入对话中。 |

你不需要配置这个 — Hermes 会在提供商元数据中查找你当前模型的能力，并自动选择正确的路径。实际效果是：你可以在会话中切换视觉和非视觉模型，图片处理“自动生效”，无需更改工作流程。纯文本模型会获得关于图片的连贯上下文，而不是它们必须拒绝的损坏的多模态负载。

处理文本描述路径的辅助模型可在 `auxiliary.vision` 下配置 — 请参阅[辅助模型](/user-guide/configuration#auxiliary-models)。
