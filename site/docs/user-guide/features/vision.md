---
title: 视觉与图片粘贴
description: 将剪贴板中的图片粘贴到 Hermes CLI 中，进行多模态视觉分析。
sidebar_label: 视觉与图片粘贴
sidebar_position: 7
---

<a id="vision-image-paste"></a>
# 视觉与图片粘贴

Hermes Agent 支持**多模态视觉**——你可以将剪贴板中的图片直接粘贴到 CLI 中，让 Agent 进行分析、描述或处理。图片会以 base64 编码的内容块形式发送给模型，因此任何支持视觉能力的模型都能处理它们。

<a id="how-it-works"></a>
## 工作原理

1. 将图片复制到剪贴板（截图、浏览器图片等）
2. 使用以下方法之一附加图片
3. 输入你的问题并按回车
4. 图片会以 `[📎 图片 #1]` 徽章的形式显示在输入框上方
5. 提交后，图片会作为视觉内容块发送给模型

你可以在发送前附加多张图片——每张图片都会获得自己的徽章。按 `Ctrl+C` 可清除所有已附加的图片。

图片会以 PNG 文件形式保存到 `~/.hermes/images/` 目录，文件名带有时间戳。

<a id="paste-methods"></a>
## 粘贴方法

如何附加图片取决于你的终端环境。并非所有方法在所有地方都有效——以下是完整说明：

<a id="paste-command"></a>
### `/paste` 命令

**最可靠的显式图片附加备用方案。**

```
/paste
```

输入 `/paste` 并按回车。Hermes 会检查你的剪贴板中是否有图片并将其附加。当你的终端重写了 `Cmd+V`/`Ctrl+V`，或者你只复制了图片且没有可检查的括号粘贴文本负载时，这是最安全的选择。

<a id="ctrl-v-cmd-v"></a>
### Ctrl+V / Cmd+V

Hermes 现在将粘贴视为分层流程：
- 首先处理普通文本粘贴
- 如果终端未能干净地传递文本，则使用原生剪贴板 / OSC52 文本备用方案
- 当剪贴板或粘贴的负载解析为图片或图片路径时，自动附加图片

这意味着粘贴的 macOS 截图临时路径和 `file://...` 图片 URI 可以立即附加，而不会作为原始文本停留在编辑器中。

:::warning
如果你的剪贴板中**只有图片**（没有文本），终端仍然无法直接发送二进制图片字节。请使用 `/paste` 作为显式的图片附加备用方案。
:::

<a id="terminal-setup-for-vs-code-cursor-windsurf"></a>
### 针对 VS Code / Cursor / Windsurf 的 `/terminal-setup`

如果你在 macOS 上的本地 VS Code 系列集成终端中运行 TUI，Hermes 可以安装推荐的 `workbench.action.terminal.sendSequence` 绑定，以获得更好的多行和撤销/重做支持：

```text
/terminal-setup
```

当 `Cmd+Enter`、`Cmd+Z` 或 `Shift+Cmd+Z` 被 IDE 拦截时，这尤其有用。仅在本地机器上运行——不要在 SSH 会话中运行。

<a id="platform-compatibility"></a>
## 平台兼容性

| 环境 | `/paste` | Cmd/Ctrl+V | `/terminal-setup` | 备注 |
|---|:---:|:---:|:---:|---|
| **macOS 终端 / iTerm2** | ✅ | ✅ | 不适用 | 最佳体验——原生剪贴板 + 截图路径恢复 |
| **Apple 终端** | ✅ | ✅ | 不适用 | 如果 Cmd+←/→/⌫ 被重写，请使用 Ctrl+A / Ctrl+E / Ctrl+U 备用方案 |
| **Linux X11 桌面** | ✅ | ✅ | 不适用 | 需要 `xclip`（`apt install xclip`） |
| **Linux Wayland 桌面** | ✅ | ✅ | 不适用 | 需要 `wl-paste`（`apt install wl-clipboard`） |
| **WSL2（Windows 终端）** | ✅ | ✅ | 不适用 | 使用 `powershell.exe`——无需额外安装 |
| **VS Code / Cursor / Windsurf（本地）** | ✅ | ✅ | ✅ | 推荐用于更好的 Cmd+Enter / 撤销 / 重做支持 |
| **VS Code / Cursor / Windsurf（SSH）** | ❌² | ❌² | ❌³ | 改为在本地机器上运行 `/terminal-setup` |
| **SSH 终端（任意）** | ❌² | ❌² | 不适用 | 远程剪贴板不可访问 |
² 参考下面的 [SSH 和远程会话](#ssh--remote-sessions)
³ 该命令写入本地 IDE 按键绑定，不应在远程主机上运行

<a id="platform-specific-setup"></a>
## 平台特定设置

<a id="macos"></a>
### macOS

**无需额外设置。** Hermes 使用 macOS 内置的 `osascript` 来读取剪贴板。如果想获得更快的性能，可选择性安装 `pngpaste`：

```bash
brew install pngpaste
```

<a id="linux-x11"></a>
### Linux (X11)

安装 `xclip`：

```bash
# Ubuntu/Debian
sudo apt install xclip

# Fedora
sudo dnf install xclip

# Arch
sudo pacman -S xclip
```

<a id="linux-wayland"></a>
### Linux (Wayland)

较新的 Linux 桌面环境（Ubuntu 22.04+、Fedora 34+）通常默认使用 Wayland。安装 `wl-clipboard`：

```bash
# Ubuntu/Debian
sudo apt install wl-clipboard

# Fedora
sudo dnf install wl-clipboard

# Arch
sudo pacman -S wl-clipboard
```

:::tip 如何检查是否正在使用 Wayland
```bash
echo $XDG_SESSION_TYPE
# "wayland" = Wayland, "x11" = X11, "tty" = 无显示服务器
<a id="how-to-check-if-you-re-on-wayland"></a>
```
:::

<a id="wsl2"></a>
### WSL2

**无需额外设置。** Hermes 会自动检测 WSL2（通过 `/proc/version`），并使用 `powershell.exe` 通过 .NET 的 `System.Windows.Forms.Clipboard` 访问 Windows 剪贴板。这是 WSL2 与 Windows 交互的内置功能——默认情况下即可使用 `powershell.exe`。

剪贴板数据会以 base64 编码的 PNG 格式通过 stdout 传输，因此无需转换文件路径或创建临时文件。

:::info WSLg 说明
如果你在运行 WSLg（支持图形界面的 WSL2），Hermes 会首先尝试 PowerShell 路径，然后回退到 `wl-paste`。WSLg 的剪贴板桥仅支持 BMP 格式的图片——Hermes 会自动使用 Pillow（如果已安装）或 ImageMagick 的 `convert` 命令将 BMP 转换为 PNG。
:::
<a id="wslg-note"></a>

<a id="verify-wsl2-clipboard-access"></a>
#### 验证 WSL2 剪贴板访问

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
## SSH 和远程会话

**通过 SSH 粘贴剪贴板图片无法完全正常工作。** 当你 SSH 到远程机器时，Hermes CLI 运行在远程主机上。剪贴板工具（`xclip`、`wl-paste`、`powershell.exe`、`osascript`）读取的是它们所在机器的剪贴板——也就是远程服务器，而不是你的本地机器。因此，远程侧无法访问你的本地剪贴板图片。

文本有时仍可通过终端粘贴或 OSC52 进行桥接，但剪贴板图片的访问和本地截图临时路径仍然与运行 Hermes 的机器绑定。

<a id="workarounds-for-ssh"></a>
### SSH 的替代方案

1. **上传图片文件**——在本地保存图片，通过 `scp`、VSCode 的文件资源管理器（拖放）或任何文件传输方法将其上传到远程服务器。然后通过路径引用。*（计划在未来的版本中增加 `/attach &lt;filepath&gt;` 命令。）*

2. **使用 URL**——如果图片可以在线访问，只需在消息中粘贴 URL。Agent 可以直接使用 `vision_analyze` 查看任何图片 URL。

3. **X11 转发**——使用 `ssh -X` 连接以转发 X11。这样远程机器上的 `xclip` 就能访问你本地的 X11 剪贴板。需要在本地运行 X 服务器（macOS 上的 XQuartz，Linux X11 桌面内置）。对于大图片来说速度较慢。
4. **使用消息平台** — 通过 Telegram、Discord、Slack 或 WhatsApp 将图片发送给 Hermes。这些平台原生支持图片上传，不受剪贴板/终端限制的影响。

<a id="why-terminals-can-t-paste-images"></a>
## 为什么终端无法粘贴图片

这是一个常见的困惑点，以下是技术解释：

终端是**基于文本**的界面。当你按下 Ctrl+V（或 Cmd+V）时，终端模拟器会：

1. 从剪贴板读取**文本内容**
2. 将其包裹在[括号粘贴](https://en.wikipedia.org/wiki/Bracketed-paste)转义序列中
3. 通过终端的文本流发送给应用程序

如果剪贴板中只有图片（没有文本），终端就没什么可发送的。没有标准的终端转义序列用于二进制图片数据。终端什么都不做。

这就是为什么 Hermes 使用单独的剪贴板检查——它不是通过终端的粘贴事件接收图片数据，而是直接通过子进程调用操作系统级工具（`osascript`、`powershell.exe`、`xclip`、`wl-paste`）独立读取剪贴板。

<a id="supported-models"></a>
## 支持的模型

图片粘贴适用于任何支持视觉的模型。图片以 base64 编码的数据 URL 形式发送，格式为 OpenAI 视觉内容格式：

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/png;base64,..."
  }
}
```

大多数现代模型都支持此格式，包括 GPT-4 Vision、Claude（视觉版）、Gemini，以及通过 OpenRouter 提供的开源多模态模型。

<a id="image-routing-vision-capable-vs-text-only-models"></a>
## 图片路由（支持视觉 vs 纯文本模型）

当用户附加图片时（无论是来自 CLI 剪贴板、网关（Telegram/Discord 照片）还是其他入口点），Hermes 会根据你当前的模型是否支持视觉来路由它：

| 你的模型 | 图片处理方式 |
|---|---|
| **支持视觉**（GPT-4V、Claude 视觉版、Gemini、Qwen-VL、MiMo-VL 等） | 作为**真实像素**，使用上述提供商的本地图片内容格式发送。没有文本摘要层。 |
| **纯文本**（DeepSeek V3、小型开源模型、旧版纯聊天端点） | 通过 `vision_analyze` 辅助工具路由——一个辅助视觉模型描述图片，然后将文本描述注入对话。 |

你不需要配置这个——Hermes 会在提供商元数据中查找你当前模型的能力，并自动选择正确的路径。实际效果是：你可以在会话中随时切换视觉和非视觉模型，图片处理“无缝工作”，无需更改工作流程。纯文本模型会获得关于图片的连贯上下文，而不是它们必须拒绝的损坏的多模态负载。

哪个辅助模型处理文本描述路径，可以在 `auxiliary.vision` 下配置——参见[辅助模型](/user-guide/configuration#auxiliary-models)。

<a id="visionanalyze-has-the-same-dual-behavior"></a>
### `vision_analyze` 也有相同的双重行为

`vision_analyze` 工具本身遵循相同的路由。当活跃的主模型支持视觉**并且**其提供商支持在工具结果中包含图片内容时（目前是 Anthropic、OpenAI、Azure-OpenAI 和 Gemini 3.x 系列），`vision_analyze` 会绕过辅助描述器，并以多模态工具结果信封的形式返回原始图片像素。主模型在下一轮中会原生看到图片——无需辅助调用，没有文本摘要信息丢失，没有额外延迟。
对于纯文本的主模型（或工具结果通道不携带图像的提供商），`vision_analyze` 会回退到传统路径：它要求配置的辅助视觉模型描述图像，并将描述作为纯文本返回。无论哪种方式，调用工具的签名都是相同的——工具在运行时根据当前激活的模型决定走哪条路径。
