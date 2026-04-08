---
title: 浏览器自动化
description: 通过多种供应商控制浏览器，包括通过 CDP 连接本地 Chrome 或使用云端浏览器进行网页交互、表单填写、抓取等。
sidebar_label: 浏览器
sidebar_position: 5
---

# 浏览器自动化

Hermes Agent 包含一套完整的浏览器自动化工具集，支持多种后端选项：

- **Browserbase 云端模式**：通过 [Browserbase](https://browserbase.com) 使用托管的云端浏览器和反爬虫工具。
- **Browser Use 云端模式**：通过 [Browser Use](https://browser-use.com) 作为替代的云端浏览器供应商。
- **Firecrawl 云端模式**：通过 [Firecrawl](https://firecrawl.dev) 使用内置抓取功能的云端浏览器。
- **Camofox 本地模式**：通过 [Camofox](https://github.com/jo-inc/camofox-browser) 进行本地反检测浏览（基于 Firefox 的指纹伪装）。
- **通过 CDP 连接本地 Chrome** — 使用 `/browser connect` 将浏览器工具连接到你自己的 Chrome 实例。
- **本地浏览器模式**：通过 `agent-browser` CLI 和本地安装的 Chromium 运行。

在所有模式下，Agent 都可以导航网页、与页面元素交互、填写表单并提取信息。

## 概览

页面被表示为 **可访问性树**（基于文本的快照），这非常适合 LLM Agent。交互元素会获得参考 ID（如 `@e1`、`@e2`），Agent 使用这些 ID 进行点击和输入。

核心能力：

- **多供应商云端执行** — 支持 Browserbase、Browser Use 或 Firecrawl — 无需本地浏览器。
- **本地 Chrome 集成** — 通过 CDP 挂载到你正在运行的 Chrome，进行实操浏览。
- **内置隐身功能** — 随机指纹、验证码识别、住宅代理（Browserbase）。
- **会话隔离** — 每个任务拥有独立的浏览器会话。
- **自动清理** — 闲置会话在超时后会自动关闭。
- **视觉分析** — 截图 + AI 分析，实现视觉理解。

## 配置

### Browserbase 云端模式

要使用 Browserbase 托管的云端浏览器，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSERBASE_API_KEY=***
BROWSERBASE_PROJECT_ID=your-project-id-here
```

在 [browserbase.com](https://browserbase.com) 获取你的凭据。

### Browser Use 云端模式

要使用 Browser Use 作为云端浏览器供应商，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSER_USE_API_KEY=***
```

在 [browser-use.com](https://browser-use.com) 获取你的 API Key。Browser Use 通过其 REST API 提供云端浏览器。如果同时设置了 Browserbase 和 Browser Use 凭据，Browserbase 优先。

### Firecrawl 云端模式

要使用 Firecrawl 作为云端浏览器供应商，请添加：

```bash
# 添加到 ~/.hermes/.env
FIRECRAWL_API_KEY=fc-***
```

在 [firecrawl.dev](https://firecrawl.dev) 获取你的 API Key。然后选择 Firecrawl 作为浏览器供应商：

```bash
hermes setup tools
# → Browser Automation → Firecrawl
```

可选设置：

```bash
# 自托管 Firecrawl 实例 (默认: https://api.firecrawl.dev)
FIRECRAWL_API_URL=http://localhost:3002

# 会话 TTL，单位为秒 (默认: 300)
FIRECRAWL_BROWSER_TTL=600
```

### Camofox 本地模式

[Camofox](https://github.com/jo-inc/camofox-browser) 是一个自托管的 Node.js 服务器，封装了 Camoufox（一个带有 C++ 指纹伪装功能的 Firefox 分支）。它提供本地反检测浏览，无需依赖云端。

```bash
# 安装并运行
git clone https://github.com/jo-inc/camofox-browser && cd camofox-browser
npm install && npm start   # 首次运行时会下载 Camoufox (~300MB)

# 或者通过 Docker 运行
docker run -d --network host -e CAMOFOX_PORT=9377 jo-inc/camofox-browser
```

然后在 `~/.hermes/.env` 中设置：

```bash
CAMOFOX_URL=http://localhost:9377
```

或者通过 `hermes tools` → Browser Automation → Camofox 进行配置。

当设置了 `CAMOFOX_URL` 后，所有浏览器工具将自动通过 Camofox 路由，而不是 Browserbase 或 agent-browser。

#### 持久化浏览器会话

默认情况下，每个 Camofox 会话都会获得一个随机身份 —— Cookie 和登录状态在 Agent 重启后不会保留。要启用持久化浏览器会话：

```yaml
# 在 ~/.hermes/config.yaml 中
browser:
  camofox:
    managed_persistence: true
```

启用后，Hermes 会向 Camofox 发送一个稳定的 Profile 作用域身份。Camofox 服务器将此身份映射到持久化的浏览器 Profile 目录，因此 Cookie、登录状态和 localStorage 在重启后依然存在。不同的 Hermes Profile 会获得不同的浏览器 Profile（Profile 隔离）。

:::note
Camofox 服务器端也必须配置 `CAMOFOX_PROFILE_DIR`，持久化功能才能生效。
:::

#### VNC 实时查看

当 Camofox 以有头模式（带有可见浏览器窗口）运行时，它会在健康检查响应中暴露一个 VNC 端口。Hermes 会自动发现该端口并在导航响应中包含 VNC URL，这样 Agent 就可以分享一个链接供你实时观看浏览器操作。

### 通过 CDP 连接本地 Chrome (`/browser connect`)

你可以通过 Chrome DevTools Protocol (CDP) 将 Hermes 浏览器工具挂载到你自己正在运行的 Chrome 实例上，而不是使用云端供应商。当你希望实时查看 Agent 的操作、与需要你自己的 Cookie/会话的页面交互，或避免云端浏览器费用时，这非常有用。

在 CLI 中使用：

```
/browser connect              # 连接到位于 ws://localhost:9222 的 Chrome
/browser connect ws://host:port  # 连接到特定的 CDP 端点
/browser status               # 检查当前连接状态
/browser disconnect            # 断开连接并返回云端/本地模式
```

如果 Chrome 尚未开启远程调试运行，Hermes 将尝试使用 `--remote-debugging-port=9222` 自动启动它。

:::tip
手动启动开启了 CDP 的 Chrome：
```bash
# Linux
google-chrome --remote-debugging-port=9222

# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
```
:::

通过 CDP 连接后，所有浏览器工具（`browser_navigate`、`browser_click` 等）都将在你的实时 Chrome 实例上操作，而不是启动云端会话。

### 本地浏览器模式

如果你**没有**设置任何云端凭据且不使用 `/browser connect`，Hermes 仍可以通过 `agent-browser` 驱动的本地 Chromium 安装来使用浏览器工具。

### 可选环境变量

```bash
# 住宅代理以获得更好的验证码解决能力 (默认: "true")
BROWSERBASE_PROXIES=true

# 使用自定义 Chromium 的高级隐身功能 — 需要 Scale 计划 (默认: "false")
BROWSERBASE_ADVANCED_STEALTH=false

# 断开连接后的会话重连 — 需要付费计划 (默认: "true")
BROWSERBASE_KEEP_ALIVE=true

# 自定义会话超时，单位为毫秒 (默认: 项目默认值)
# 示例: 600000 (10分钟), 1800000 (30分钟)
BROWSERBASE_SESSION_TIMEOUT=600000

# 自动清理前的闲置超时，单位为秒 (默认: 120)
BROWSER_INACTIVITY_TIMEOUT=120
```

### 安装 agent-browser CLI

```bash
npm install -g agent-browser
# 或者在仓库中本地安装：
npm install
```

:::info
`browser` 工具集必须包含在配置的 `toolsets` 列表中，或者通过 `hermes config set toolsets '["hermes-cli", "browser"]'` 启用。
:::

## 可用工具

### `browser_navigate`

导航到某个 URL。必须在调用任何其他浏览器工具之前调用。初始化 Browserbase 会话。

```
Navigate to https://github.com/NousResearch
```

:::tip
对于简单的信息检索，优先使用 `web_search` 或 `web_extract` —— 它们更快且更便宜。只有在需要与页面**交互**（点击按钮、填写表单、处理动态内容）时才使用浏览器工具。
:::

### `browser_snapshot`

获取当前页面可访问性树的文本快照。返回带有参考 ID（如 `@e1`、`@e2`）的交互元素，供 `browser_click` 和 `browser_type` 使用。

- **`full=false`** (默认): 仅显示交互元素的精简视图。
- **`full=true`**: 完整的页面内容。

超过 8000 字符的快照会自动由 LLM 进行总结。

### `browser_click`

点击快照中通过参考 ID 标识的元素。

```
Click @e5 to press the "Sign In" button
```

### `browser_type`

在输入框中输入文本。先清空字段，然后输入新文本。

```
Type "hermes agent" into the search field @e3
```

### `browser_scroll`

向上或向下滚动页面以显示更多内容。
```
向下滚动以查看更多结果
```

### `browser_press`

按下键盘按键。适用于提交表单或进行页面导航。

```
按下 Enter 键提交表单
```

支持的按键包括：`Enter`、`Tab`、`Escape`、`ArrowDown`、`ArrowUp` 等。

### `browser_back`

在浏览器历史记录中返回上一页。

### `browser_get_images`

列出当前页面上的所有图片及其 URL 和 alt 文本。适用于查找需要分析的图片。

### `browser_vision`

截取屏幕截图并使用视觉 AI 进行分析。当文本快照无法捕获重要的视觉信息时使用此功能——特别适用于验证码（CAPTCHA）、复杂布局或视觉验证挑战。

截图会被持久化保存，文件路径将随 AI 分析结果一同返回。在即时通讯平台（Telegram、Discord、Slack、WhatsApp）上，你可以要求 Agent 分享截图——它将通过 `MEDIA:` 机制作为原生照片附件发送。

```
这个页面上的图表显示了什么？
```

截图存储在 `~/.hermes/cache/screenshots/` 中，并在 24 小时后自动清理。

### `browser_console`

获取当前页面的浏览器控制台输出（log/warn/error 消息）和未捕获的 JavaScript 异常。这对于检测那些不会出现在无障碍树（accessibility tree）中的静默 JS 错误至关重要。

```
检查浏览器控制台是否有任何 JavaScript 错误
```

使用 `clear=True` 可以在读取后清除控制台，以便后续调用仅显示新消息。

## 实际案例

### 填写网页表单

```
用户：使用我的邮箱 john@example.com 在 example.com 上注册一个账号

Agent 工作流：
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → 看到带有 ref 标记的表单字段
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → 点击 "Create Account"
6. browser_snapshot()  → 确认成功
```

### 研究动态内容

```
用户：现在 GitHub 上最热门的仓库有哪些？

Agent 工作流：
1. browser_navigate("https://github.com/trending")
2. browser_snapshot(full=true)  → 读取热门仓库列表
3. 返回格式化后的结果
```

## 会话录制

自动将浏览器会话录制为 WebM 视频文件：

```yaml
browser:
  record_sessions: true  # 默认值：false
```

启用后，录制将在第一次执行 `browser_navigate` 时自动开始，并在会话关闭时保存到 `~/.hermes/browser_recordings/`。该功能在本地和云端（Browserbase）模式下均可使用。超过 72 小时的录制文件会被自动清理。

## 隐身特性

Browserbase 提供了自动隐身能力：

| 特性 | 默认状态 | 备注 |
|---------|---------|-------|
| 基础隐身 (Basic Stealth) | 始终开启 | 随机指纹、视口随机化、验证码自动识别 |
| 住宅代理 (Residential Proxies) | 开启 | 通过住宅 IP 路由以获得更好的访问权限 |
| 高级隐身 (Advanced Stealth) | 关闭 | 自定义 Chromium 构建，需要 Scale 方案 |
| 保持连接 (Keep Alive) | 开启 | 网络波动后的会话重连 |

:::note
如果你的方案中不包含付费特性，Hermes 会自动降级处理——首先禁用 `keepAlive`，然后禁用代理——因此在免费方案上浏览功能依然可用。
:::

## 会话管理

- 每个任务通过 Browserbase 获取一个隔离的浏览器会话。
- 会话在闲置后会自动清理（默认：2 分钟）。
- 后台线程每 30 秒检查一次过期会话。
- 进程退出时会运行紧急清理，以防止产生孤儿会话。
- 会话通过 Browserbase API 释放（`REQUEST_RELEASE` 状态）。

## 局限性

- **基于文本的交互** —— 依赖于无障碍树，而非像素坐标。
- **快照大小** —— 超长页面可能会被截断，或在 8000 字符处由 LLM 进行摘要处理。
- **会话超时** —— 云端会话的过期时间取决于你服务商的方案设置。
- **成本** —— 云端会话会消耗服务商额度；会话在对话结束或闲置后会自动清理。使用 `/browser connect` 可进行免费的本地浏览。
- **不支持文件下载** —— 无法从浏览器下载文件。
