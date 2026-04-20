---
title: 浏览器自动化
description: 通过多种提供商控制浏览器，使用本地 Chrome（通过 CDP）或云浏览器进行网页交互、表单填写、数据抓取等操作。
sidebar_label: 浏览器
sidebar_position: 5
---

# 浏览器自动化 {#browser-automation}

Hermes Agent 包含一套完整的浏览器自动化工具集，提供多种后端选项：

- **Browserbase 云模式**：通过 [Browserbase](https://browserbase.com) 使用托管的云浏览器和反机器人工具
- **Browser Use 云模式**：通过 [Browser Use](https://browser-use.com) 作为替代的云浏览器提供商
- **Firecrawl 云模式**：通过 [Firecrawl](https://firecrawl.dev) 使用内置抓取功能的云浏览器
- **Camofox 本地模式**：通过 [Camofox](https://github.com/jo-inc/camofox-browser) 进行本地反检测浏览（基于 Firefox 的指纹欺骗）
- **通过 CDP 连接本地 Chrome** — 使用 `/browser connect` 将浏览器工具连接到您自己的 Chrome 实例
- **本地浏览器模式**：通过 `agent-browser` CLI 和本地安装的 Chromium

在所有模式下，Agent 都可以导航网站、与页面元素交互、填写表单以及提取信息。

## 概述 {#overview}

页面被表示为**无障碍功能树**（基于文本的快照），这使其非常适合 LLM Agent。交互式元素会获得引用 ID（如 `@e1`、`@e2`），Agent 使用这些 ID 进行点击和输入。

核心功能：

- **多提供商云执行** — Browserbase、Browser Use 或 Firecrawl — 无需本地浏览器
- **本地 Chrome 集成** — 通过 CDP 连接到您正在运行的 Chrome 进行手动浏览
- **内置隐身功能** — 随机指纹、验证码解决、住宅代理（Browserbase）
- **会话隔离** — 每个任务都有自己的浏览器会话
- **自动清理** — 不活动的会话在超时后会被关闭
- **视觉分析** — 截图 + AI 分析，用于视觉理解

## 设置 {#setup}

<a id="nous-subscribers"></a>
:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，您可以通过 **[工具网关](tool-gateway.md)** 使用浏览器自动化功能，无需任何单独的 API 密钥。运行 `hermes model` 或 `hermes tools` 来启用它。
:::

<a id="browserbase-cloud-mode"></a>
### Browserbase 云模式 {#nous-subscribers}

要使用 Browserbase 托管的云浏览器，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSERBASE_API_KEY=***
BROWSERBASE_PROJECT_ID=your-project-id-here
```

在 [browserbase.com](https://browserbase.com) 获取您的凭证。

### Browser Use 云模式 {#browser-use-cloud-mode}

要使用 Browser Use 作为您的云浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSER_USE_API_KEY=***
```

在 [browser-use.com](https://browser-use.com) 获取您的 API 密钥。Browser Use 通过其 REST API 提供云浏览器。如果同时设置了 Browserbase 和 Browser Use 的凭证，则 Browserbase 优先。

### Firecrawl 云模式 {#firecrawl-cloud-mode}

要使用 Firecrawl 作为您的云浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
FIRECRAWL_API_KEY=fc-***
```

在 [firecrawl.dev](https://firecrawl.dev) 获取您的 API 密钥。然后选择 Firecrawl 作为您的浏览器提供商：

```bash
hermes setup tools
# → Browser Automation → Firecrawl
```

可选设置：

```bash
# 自托管的 Firecrawl 实例（默认：https://api.firecrawl.dev）
FIRECRAWL_API_URL=http://localhost:3002

# 会话 TTL，单位秒（默认：300）
FIRECRAWL_BROWSER_TTL=600
```

### Camofox 本地模式 {#camofox-local-mode}

[Camofox](https://github.com/jo-inc/camofox-browser) 是一个自托管的 Node.js 服务器，封装了 Camoufox（一个具有 C++ 指纹欺骗功能的 Firefox 分支）。它提供本地反检测浏览，无需依赖云服务。

```bash
# 安装并运行
git clone https://github.com/jo-inc/camofox-browser && cd camofox-browser
npm install && npm start   # 首次运行会下载 Camoufox（约 300MB）

# 或通过 Docker
docker run -d --network host -e CAMOFOX_PORT=9377 jo-inc/camofox-browser
```

然后在 `~/.hermes/.env` 中设置：

```bash
CAMOFOX_URL=http://localhost:9377
```

或者通过 `hermes tools` → Browser Automation → Camofox 进行配置。

当设置了 `CAMOFOX_URL` 时，所有浏览器工具都会自动通过 Camofox 路由，而不是 Browserbase 或 agent-browser。

#### 持久化浏览器会话 {#persistent-browser-sessions}

默认情况下，每个 Camofox 会话都有一个随机身份 — Cookie 和登录状态在 Agent 重启后不会保留。要启用持久化浏览器会话，请将以下内容添加到 `~/.hermes/config.yaml`：
```yaml
browser:
  camofox:
    managed_persistence: true
```

然后完全重启 Hermes，以便新配置生效。

:::warning 注意嵌套路径
Hermes 读取的是 `browser.camofox.managed_persistence`，**而不是**顶层的 `managed_persistence`。一个常见的错误是写成：

```yaml
# ❌ 错误 — Hermes 会忽略这个
managed_persistence: true
<a id="nested-path-matters"></a>
```

如果这个标志被放在了错误的路径下，Hermes 会静默地回退到一个随机的临时 `userId`，你的登录状态将在每次会话中丢失。
:::

##### Hermes 做了什么 {#what-hermes-does}
- 向 Camofox 发送一个确定性的、限定于配置文件的 `userId`，以便服务器可以在不同会话间复用同一个 Firefox 配置文件。
- 在清理时跳过服务器端的上下文销毁，因此 Cookie 和登录状态可以在 Agent 任务之间保留。
- 将 `userId` 限定在活动的 Hermes 配置文件范围内，因此不同的 Hermes 配置文件会获得不同的浏览器配置文件（配置文件隔离）。

##### Hermes 不做什么 {#what-hermes-does-not-do}
- 它不会强制 Camofox 服务器持久化。Hermes 只发送一个稳定的 `userId`；服务器必须通过将该 `userId` 映射到一个持久的 Firefox 配置文件目录来遵守它。
- 如果你的 Camofox 服务器构建将每个请求都视为临时的（例如，总是调用 `browser.newContext()` 而不加载存储的配置文件），Hermes 无法使这些会话持久化。请确保你运行的 Camofox 构建实现了基于 userId 的配置文件持久化。

##### 验证是否生效 {#verify-it-s-working}

1.  启动 Hermes 和你的 Camofox 服务器。
2.  在浏览器任务中打开 Google（或任何登录网站）并手动登录。
3.  正常结束浏览器任务。
4.  启动一个新的浏览器任务。
5.  再次打开同一个网站 — 你应该仍然处于登录状态。

如果第 5 步让你退出了登录，说明 Camofox 服务器没有遵守稳定的 `userId`。请仔细检查你的配置路径，确认在编辑 `config.yaml` 后完全重启了 Hermes，并验证你的 Camofox 服务器版本支持每个用户的持久化配置文件。

##### 状态存储在哪里 {#where-state-lives}

Hermes 从配置文件作用域的目录 `~/.hermes/browser_auth/camofox/`（对于非默认配置文件，则是 `$HERMES_HOME` 下的等效目录）派生出稳定的 `userId`。实际的浏览器配置文件数据存储在 Camofox 服务器端，以该 `userId` 为键。要完全重置一个持久化配置文件，请在 Camofox 服务器上清除它，并删除 Hermes 配置文件中对应的状态目录。

#### VNC 实时视图 {#vnc-live-view}

当 Camofox 在 headed 模式（带有可见的浏览器窗口）下运行时，它会在其健康检查响应中暴露一个 VNC 端口。Hermes 会自动发现这一点，并在导航响应中包含 VNC URL，因此 Agent 可以分享一个链接，让你实时观看浏览器操作。

### 通过 CDP 连接本地 Chrome (`/browser connect`) {#local-chrome-via-cdp-browser-connect}

除了云服务提供商，你还可以通过 Chrome DevTools Protocol (CDP) 将 Hermes 浏览器工具附加到你自己的正在运行的 Chrome 实例上。当你想实时查看 Agent 在做什么、与需要你自己的 Cookie/会话的页面交互，或者避免云浏览器成本时，这很有用。

:::note
`/browser connect` 是一个**交互式 CLI 斜杠命令** — 它不由网关分发。如果你尝试在 WebUI、Telegram、Discord 或其他网关聊天中运行它，该消息将作为纯文本发送给 Agent，命令不会执行。请从终端启动 Hermes (`hermes` 或 `hermes chat`)，并在那里输入 `/browser connect`。
:::

在 CLI 中，使用：

```
/browser connect              # 连接到 ws://localhost:9222 的 Chrome
/browser connect ws://host:port  # 连接到特定的 CDP 端点
/browser status               # 检查当前连接状态
/browser disconnect            # 断开连接并返回云/本地模式
```

如果 Chrome 尚未以远程调试模式运行，Hermes 将尝试使用 `--remote-debugging-port=9222` 参数自动启动它。

:::tip
要手动启动启用了 CDP 的 Chrome，请使用一个专用的用户数据目录，这样即使 Chrome 已经用你的正常配置文件在运行，调试端口也能正常启动：

```bash
# Linux
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.hermes/chrome-debug \
  --no-first-run \
  --no-default-browser-check &

# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check &
```
然后启动 Hermes CLI 并运行 `/browser connect`。

**为什么需要 `--user-data-dir`？** 如果没有它，在常规 Chrome 实例已经在运行时启动 Chrome，通常会打开一个属于现有进程的新窗口——而该现有进程启动时没有 `--remote-debugging-port`，所以端口 9222 永远不会打开。指定一个专用的 user-data-dir 会强制启动一个全新的 Chrome 进程，调试端口才能实际监听。`--no-first-run --no-default-browser-check` 则是跳过新配置文件的首次启动向导。
:::

通过 CDP 连接后，所有浏览器工具（`browser_navigate`、`browser_click` 等）都将操作你的实时 Chrome 实例，而不是启动云端会话。

### 本地浏览器模式 {#local-browser-mode}

如果你**不**设置任何云凭证，并且不使用 `/browser connect`，Hermes 仍然可以通过 `agent-browser` 驱动的本地 Chromium 安装来使用浏览器工具。

### 可选环境变量 {#optional-environment-variables}

```bash
# 用于更好解决验证码的住宅代理（默认："true"）
BROWSERBASE_PROXIES=true

# 使用自定义 Chromium 的高级隐身模式 — 需要 Scale 计划（默认："false"）
BROWSERBASE_ADVANCED_STEALTH=false

# 断开连接后的会话重连 — 需要付费计划（默认："true"）
BROWSERBASE_KEEP_ALIVE=true

# 自定义会话超时时间（毫秒）（默认：项目默认值）
# 示例：600000 (10分钟), 1800000 (30分钟)
BROWSERBASE_SESSION_TIMEOUT=600000

# 自动清理前的无活动超时（秒）（默认：120）
BROWSER_INACTIVITY_TIMEOUT=120
```

### 安装 agent-browser CLI {#install-agent-browser-cli}

```bash
npm install -g agent-browser
# 或者在仓库中本地安装：
npm install
```

:::info
`browser` 工具集必须包含在你配置文件的 `toolsets` 列表中，或者通过 `hermes config set toolsets '["hermes-cli", "browser"]'` 启用。
:::

## 可用工具 {#available-tools}

### `browser_navigate` {#browsernavigate}

导航到某个 URL。必须在调用任何其他浏览器工具之前调用。用于初始化 Browserbase 会话。

```
Navigate to https://github.com/NousResearch
```

:::tip
对于简单的信息检索，优先使用 `web_search` 或 `web_extract` — 它们更快、更便宜。当你需要**与**页面**交互**时（点击按钮、填写表单、处理动态内容），才使用浏览器工具。
:::

### `browser_snapshot` {#browsersnapshot}

获取当前页面的无障碍树文本快照。返回带有引用 ID（如 `@e1`、`@e2`）的可交互元素，以便与 `browser_click` 和 `browser_type` 一起使用。

- **`full=false`** (默认)：仅显示可交互元素的精简视图
- **`full=true`**：完整的页面内容

超过 8000 个字符的快照会自动由 LLM 进行总结。

### `browser_click` {#browserclick}

点击快照中由其引用 ID 标识的元素。

```
Click @e5 to press the "Sign In" button
```

### `browser_type` {#browsertype}

在输入字段中输入文本。先清空字段，然后输入新文本。

```
Type "hermes agent" into the search field @e3
```

### `browser_scroll` {#browserscroll}

向上或向下滚动页面以显示更多内容。

```
Scroll down to see more results
```

### `browser_press` {#browserpress}

按下一个键盘按键。用于提交表单或导航。

```
Press Enter to submit the form
```

支持的按键：`Enter`、`Tab`、`Escape`、`ArrowDown`、`ArrowUp` 等。

### `browser_back` {#browserback}

在浏览器历史记录中导航回上一页。

### `browser_get_images` {#browsergetimages}

列出当前页面上的所有图片及其 URL 和 alt 文本。用于查找需要分析的图片。

### `browser_vision` {#browservision}

截取屏幕截图并使用视觉 AI 进行分析。当文本快照无法捕获重要的视觉信息时使用此工具——尤其适用于验证码、复杂布局或视觉验证挑战。

屏幕截图会持久保存，文件路径将与 AI 分析结果一起返回。在消息平台（Telegram、Discord、Slack、WhatsApp）上，你可以要求 Agent 分享截图——它将通过 `MEDIA:` 机制以原生照片附件的形式发送。

```
What does the chart on this page show?
```

屏幕截图存储在 `~/.hermes/cache/screenshots/` 目录下，并在 24 小时后自动清理。
### `browser_console` {#browserconsole}

获取浏览器控制台输出（日志/警告/错误信息）以及当前页面未捕获的 JavaScript 异常。对于检测在无障碍树中不显示的静默 JS 错误至关重要。

```
检查浏览器控制台是否有任何 JavaScript 错误
```

使用 `clear=True` 可在读取后清空控制台，这样后续调用就只显示新消息。

### `browser_cdp` {#browsercdp}

原始 Chrome DevTools 协议透传 —— 这是用于处理其他工具未涵盖的浏览器操作的逃生通道。可用于处理原生对话框、iframe 作用域内的代码执行、Cookie/网络控制，或 Agent 需要的任何 CDP 指令。

**仅在会话开始时能访问到 CDP 端点时才可用** —— 这意味着 `/browser connect` 已连接到正在运行的 Chrome，或者在 `config.yaml` 中设置了 `browser.cdp_url`。默认的本地 Agent-浏览器模式、Camofox 以及云服务提供商（Browserbase、Browser Use、Firecrawl）目前未向此工具暴露 CDP —— 云提供商有每个会话的 CDP URL，但实时会话路由是后续功能。

**CDP 方法参考：** https://chromedevtools.github.io/devtools-protocol/ —— Agent 可以 `web_extract` 特定方法的页面来查找参数和返回结构。

常见模式：

```
# 列出标签页（浏览器级别，无需 target_id）
browser_cdp(method="Target.getTargets")

# 处理标签页上的原生 JS 对话框
browser_cdp(method="Page.handleJavaScriptDialog",
            params={"accept": true, "promptText": ""},
            target_id="<tabId>")

# 在特定标签页中执行 JS
browser_cdp(method="Runtime.evaluate",
            params={"expression": "document.title", "returnByValue": true},
            target_id="<tabId>")

# 获取所有 Cookie
browser_cdp(method="Network.getAllCookies")
```

浏览器级别的方法（`Target.*`、`Browser.*`、`Storage.*`）省略 `target_id`。页面级别的方法（`Page.*`、`Runtime.*`、`DOM.*`、`Emulation.*`）需要来自 `Target.getTargets` 的 `target_id`。每次调用都是独立的 —— 会话不会在调用之间保持。

## 实践示例 {#practical-examples}

### 填写网页表单 {#filling-out-a-web-form}

```
用户：用我的邮箱 john@example.com 在 example.com 上注册一个账户

Agent 工作流程：
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → 看到带有 refs 的表单字段
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → 点击“创建账户”
6. browser_snapshot()  → 确认成功
```

### 研究动态内容 {#researching-dynamic-content}

```
用户：GitHub 上当前最热门的仓库是哪些？

Agent 工作流程：
1. browser_navigate("https://github.com/trending")
2. browser_snapshot(full=true)  → 读取热门仓库列表
3. 返回格式化结果
```

## 会话录制 {#session-recording}

自动将浏览器会话录制为 WebM 视频文件：

```yaml
browser:
  record_sessions: true  # 默认值：false
```

启用后，录制会在第一次 `browser_navigate` 时自动开始，并在会话关闭时保存到 `~/.hermes/browser_recordings/`。在本地和云端（Browserbase）模式下均可工作。超过 72 小时的录制文件会自动清理。

## 隐身功能 {#stealth-features}

Browserbase 提供自动隐身能力：

| 功能 | 默认状态 | 说明 |
|---------|---------|-------|
| 基础隐身 | 始终开启 | 随机指纹、视口随机化、验证码破解 |
| 住宅代理 | 开启 | 通过住宅 IP 路由以获得更好的访问效果 |
| 高级隐身 | 关闭 | 自定义 Chromium 构建，需要 Scale 计划 |
| 保持连接 | 开启 | 网络波动后重新连接会话 |

:::note
如果你的订阅计划不包含付费功能，Hermes 会自动回退 —— 先禁用 `keepAlive`，然后是代理 —— 这样即使在免费计划上浏览功能也能工作。
:::

## 会话管理 {#session-management}

- 每个任务通过 Browserbase 获得一个隔离的浏览器会话
- 会话在无活动后自动清理（默认：2 分钟）
- 后台线程每 30 秒检查一次过期会话
- 进程退出时会运行紧急清理，防止会话残留
- 会话通过 Browserbase API（`REQUEST_RELEASE` 状态）释放
## 限制 {#limitations}

- **基于文本的交互** —— 依赖无障碍树，而非像素坐标
- **快照大小** —— 大页面可能被截断或在 8000 字符处由 LLM 进行总结
- **会话超时** —— 云会话过期取决于你的提供商套餐设置
- **成本** —— 云会话消耗提供商额度；会话在对话结束或空闲后自动清理。使用 `/browser connect` 可免费进行本地浏览。
- **无法下载文件** —— 不能从浏览器下载文件
