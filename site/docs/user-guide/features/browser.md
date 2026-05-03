---
title: 浏览器自动化
description: 通过多种提供商控制浏览器，支持通过 CDP 连接本地 Chrome 或使用云端浏览器进行网页交互、表单填写、数据抓取等操作。
sidebar_label: 浏览器
sidebar_position: 5
---

# 浏览器自动化 {#browser-automation}

Hermes Agent 包含一套完整的浏览器自动化工具集，支持多种后端选项：

- **Browserbase 云端模式** — 通过 [Browserbase](https://browserbase.com) 使用托管云端浏览器和反机器人工具
- **Browser Use 云端模式** — 通过 [Browser Use](https://browser-use.com) 作为替代的云端浏览器提供商
- **Firecrawl 云端模式** — 通过 [Firecrawl](https://firecrawl.dev) 使用内置抓取功能的云端浏览器
- **Camofox 本地模式** — 通过 [Camofox](https://github.com/jo-inc/camofox-browser) 进行本地反检测浏览（基于 Firefox 的指纹伪装）
- **通过 CDP 连接本地 Chrome** — 使用 `/browser connect` 将浏览器工具连接到您自己的 Chrome 实例
- **本地浏览器模式** — 通过 `agent-browser` CLI 和本地 Chromium 安装

在所有模式下，Agent 都可以浏览网站、与页面元素交互、填写表单以及提取信息。

## 概述 {#overview}

页面以**无障碍树**（基于文本的快照）的形式呈现，非常适合 LLM Agent。交互元素会获得 ref ID（如 `@e1`、`@e2`），Agent 使用这些 ID 进行点击和输入。

关键能力：

- **多提供商云端执行** — Browserbase、Browser Use 或 Firecrawl，无需本地浏览器
- **本地 Chrome 集成** — 通过 CDP 连接到正在运行的 Chrome，进行手动浏览
- **内置隐身功能** — 随机指纹、验证码解决、住宅代理（Browserbase）
- **会话隔离** — 每个任务拥有独立的浏览器会话
- **自动清理** — 超时后自动关闭不活跃的会话
- **视觉分析** — 截图 + AI 分析，实现视觉理解

## 设置 {#setup}

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，可以通过 **[Tool Gateway](tool-gateway.md)** 使用浏览器自动化，无需单独的 API 密钥。运行 `hermes model` 或 `hermes tools` 即可启用。
:::
<a id="nous-subscribers"></a>

### Browserbase 云端模式 {#browserbase-cloud-mode}

要使用 Browserbase 管理的云端浏览器，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSERBASE_API_KEY=***
BROWSERBASE_PROJECT_ID=your-project-id-here
```

在 [browserbase.com](https://browserbase.com) 获取您的凭证。

### Browser Use 云端模式 {#browser-use-cloud-mode}

要使用 Browser Use 作为云端浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSER_USE_API_KEY=***
```

在 [browser-use.com](https://browser-use.com) 获取您的 API 密钥。Browser Use 通过其 REST API 提供云端浏览器。如果同时设置了 Browserbase 和 Browser Use 的凭证，则 Browserbase 优先。

### Firecrawl 云端模式 {#firecrawl-cloud-mode}

要使用 Firecrawl 作为云端浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
FIRECRAWL_API_KEY=fc-***
```

在 [firecrawl.dev](https://firecrawl.dev) 获取您的 API 密钥。然后选择 Firecrawl 作为您的浏览器提供商：

```bash
hermes setup tools
# → 浏览器自动化 → Firecrawl
```

可选设置：

```bash
# 自托管 Firecrawl 实例（默认：https://api.firecrawl.dev）
FIRECRAWL_API_URL=http://localhost:3002

# 会话 TTL（秒，默认：300）
FIRECRAWL_BROWSER_TTL=600
```
### 混合路由：公共 URL 走云端，局域网/localhost 走本地 {#hybrid-routing-cloud-for-public-urls-local-for-lan-localhost}

当配置了云提供商后，Hermes 会自动为解析到私有/回环/局域网地址（`localhost`、`127.0.0.1`、`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`、`*.local`、`*.lan`、`*.internal`、IPv6 回环 `::1`、链路本地 `169.254.x.x`）的 URL 启动一个 **本地 Chromium sidecar**。公共 URL 在同一会话中继续使用云提供商。

这解决了常见的“我在本地开发但使用 Browserbase”的工作流——Agent 可以截图你的 `http://localhost:3000` 仪表盘，同时抓取 `https://github.com`，无需你切换提供商或禁用 SSRF 防护。云提供商永远不会看到私有 URL。

该功能**默认开启**。若要禁用它（所有 URL 都像以前一样走配置的云提供商）：

```yaml
# ~/.hermes/config.yaml
browser:
  cloud_provider: browserbase
  auto_local_for_private_urls: false
```

禁用自动路由后，私有 URL 会被拒绝并返回 `"Blocked: URL targets a private or internal address"`，除非你同时设置了 `browser.allow_private_urls: true`（这会让云提供商尝试访问它们——通常不会成功，因为 Browserbase 等无法到达你的局域网）。

要求：本地 sidecar 使用与纯本地模式相同的 `agent-browser` CLI，因此你需要安装它（`hermes setup tools → Browser Automation` 会自动安装）。从公共 URL 导航后重定向到私有地址仍会被阻止（你不能通过重定向到内部的技巧通过公共路径到达你的局域网）。

### Camofox 本地模式 {#camofox-local-mode}

[Camofox](https://github.com/jo-inc/camofox-browser) 是一个自托管的 Node.js 服务器，封装了 Camoufox（一个带有 C++ 指纹欺骗功能的 Firefox 分支）。它提供无需云依赖的本地反检测浏览。

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

当设置了 `CAMOFOX_URL` 后，所有浏览器工具会自动通过 Camofox 路由，而不是 Browserbase 或 agent-browser。

#### 持久化浏览器会话 {#persistent-browser-sessions}

默认情况下，每个 Camofox 会话都会获得一个随机身份——Cookie 和登录状态在 Agent 重启后不会保留。要启用持久化浏览器会话，请在 `~/.hermes/config.yaml` 中添加以下内容：

```yaml
browser:
  camofox:
    managed_persistence: true
```

然后完全重启 Hermes，以便新配置生效。

<a id="nested-path-matters"></a>
:::warning 嵌套路径很重要
Hermes 读取的是 `browser.camofox.managed_persistence`，**而不是**顶层的 `managed_persistence`。一个常见的错误是写成：

```yaml
# ❌ 错误——Hermes 会忽略这个
managed_persistence: true
```

如果标志放在了错误的路径下，Hermes 会静默地回退到一个随机的临时 `userId`，你的登录状态将在每次会话中丢失。
:::
##### Hermes 做了什么 {#what-hermes-does}
- 向 Camofox 发送一个确定性的、配置文件作用域的 `userId`，以便服务器在多个会话间复用同一个 Firefox 配置文件。
- 在清理时跳过服务器端上下文销毁，从而让 cookie 和登录状态在 Agent 任务之间得以保留。
- 将 `userId` 限定在当前 Hermes 配置文件范围内，这样不同的 Hermes 配置文件会获得不同的浏览器配置文件（配置文件隔离）。

##### Hermes 没有做什么 {#what-hermes-does-not-do}
- 它不会强制 Camofox 服务器进行持久化。Hermes 只发送一个稳定的 `userId`；服务器必须通过将该 `userId` 映射到一个持久的 Firefox 配置文件目录来遵循它。
- 如果你的 Camofox 服务器构建将每个请求视为临时性的（例如总是调用 `browser.newContext()` 而不加载已存储的配置文件），Hermes 无法让这些会话持久化。请确保你运行的 Camofox 构建实现了基于 userId 的配置文件持久化。

##### 验证是否生效 {#verify-it-s-working}

1. 启动 Hermes 和你的 Camofox 服务器。
2. 在浏览器任务中打开 Google（或任何登录站点）并手动登录。
3. 正常结束浏览器任务。
4. 启动一个新的浏览器任务。
5. 再次打开同一个站点——你应该仍然处于登录状态。

如果第 5 步让你退出登录，说明 Camofox 服务器没有遵循稳定的 `userId`。请仔细检查你的配置路径，确认在编辑 `config.yaml` 后完全重启了 Hermes，并验证你的 Camofox 服务器版本支持持久的每用户配置文件。

##### 状态存储位置 {#where-state-lives}

Hermes 从配置文件作用域的目录 `~/.hermes/browser_auth/camofox/`（或非默认配置文件下 `$HERMES_HOME` 中的对应目录）派生出稳定的 `userId`。实际的浏览器配置文件数据存储在 Camofox 服务器端，以该 `userId` 为键。要完全重置一个持久配置文件，请在 Camofox 服务器上清除它，并删除对应 Hermes 配置文件的状态目录。

#### VNC 实时视图 {#vnc-live-view}

当 Camofox 以有头模式运行（带有可见的浏览器窗口）时，它会在健康检查响应中暴露一个 VNC 端口。Hermes 会自动发现该端口，并将 VNC URL 包含在导航响应中，这样 Agent 就可以分享一个链接，让你实时观看浏览器。

### 通过 CDP 连接本地 Chrome（`/browser connect`） {#local-chrome-via-cdp-browser-connect}

除了使用云提供商，你还可以通过 Chrome DevTools 协议（CDP）将 Hermes 浏览器工具附加到你自己的运行中的 Chrome 实例上。当你希望实时查看 Agent 正在做什么、与需要你自己 cookie/会话的页面交互，或者避免云浏览器费用时，这非常有用。

:::note
`/browser connect` 是一个**交互式 CLI 斜杠命令**——它不由网关分发。如果你尝试在 WebUI、Telegram、Discord 或其他网关聊天中运行它，该消息将作为纯文本发送给 Agent，命令不会执行。请从终端启动 Hermes（`hermes` 或 `hermes chat`），然后在那里输入 `/browser connect`。
:::

在 CLI 中，使用：

```
/browser connect              # 连接到 ws://localhost:9222 上的 Chrome
/browser connect ws://host:port  # 连接到特定的 CDP 端点
/browser status               # 检查当前连接状态
/browser disconnect            # 断开连接并返回云/本地模式
```
如果 Chrome 尚未以远程调试模式运行，Hermes 将尝试使用 `--remote-debugging-port=9222` 自动启动它。

:::tip
要手动启动启用了 CDP 的 Chrome，请使用专用的用户数据目录（user-data-dir），这样即使 Chrome 已使用您的正常配置文件运行，调试端口也能正常启动：

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

**为什么需要 `--user-data-dir`？** 如果不使用它，在常规 Chrome 实例已经运行时启动 Chrome，通常会在现有进程上打开一个新窗口——而该现有进程并未以 `--remote-debugging-port` 启动，因此端口 9222 永远不会打开。专用的用户数据目录会强制启动一个新的 Chrome 进程，调试端口才能真正监听。`--no-first-run --no-default-browser-check` 会跳过新配置文件的首次启动向导。
:::

通过 CDP 连接后，所有浏览器工具（`browser_navigate`、`browser_click` 等）都会在您正在运行的 Chrome 实例上操作，而不会启动云会话。

### 本地浏览器模式 {#local-browser-mode}

如果您**没有**设置任何云凭证，也没有使用 `/browser connect`，Hermes 仍然可以通过由 `agent-browser` 驱动的本地 Chromium 安装来使用浏览器工具。

### 可选环境变量 {#optional-environment-variables}

```bash
# Residential proxies for better CAPTCHA solving (default: "true")
BROWSERBASE_PROXIES=true

# Advanced stealth with custom Chromium — requires Scale Plan (default: "false")
BROWSERBASE_ADVANCED_STEALTH=false

# Session reconnection after disconnects — requires paid plan (default: "true")
BROWSERBASE_KEEP_ALIVE=true

# Custom session timeout in milliseconds (default: project default)
# Examples: 600000 (10min), 1800000 (30min)
BROWSERBASE_SESSION_TIMEOUT=600000

# Inactivity timeout before auto-cleanup in seconds (default: 120)
BROWSER_INACTIVITY_TIMEOUT=120
```

### 安装 agent-browser CLI {#install-agent-browser-cli}

```bash
npm install -g agent-browser
# Or install locally in the repo:
npm install
```

:::info
`browser` 工具集必须包含在配置的 `toolsets` 列表中，或者通过 `hermes config set toolsets '["hermes-cli", "browser"]'` 启用。
:::

## 可用工具 {#available-tools}

### `browser_navigate` {#browsernavigate}

导航到 URL。必须在任何其他浏览器工具之前调用。初始化 Browserbase 会话。

```
Navigate to https://github.com/NousResearch
```

:::tip
对于简单的信息检索，建议使用 `web_search` 或 `web_extract`——它们更快且成本更低。当您需要**与页面交互**（点击按钮、填写表单、处理动态内容）时，再使用浏览器工具。
:::

### `browser_snapshot` {#browsersnapshot}

获取当前页面无障碍树的文本快照。返回带有引用 ID（如 `@e1`、`@e2`）的可交互元素，供 `browser_click` 和 `browser_type` 使用。
- **`full=false`**（默认）：紧凑视图，仅显示可交互元素
- **`full=true`**：完整页面内容

超过 8000 字符的快照会自动由 LLM 进行摘要。

### `browser_click` {#browserclick}

通过快照中的 ref ID 点击某个元素。

```
Click @e5 to press the "Sign In" button
```

### `browser_type` {#browsertype}

在输入字段中输入文本。会先清空字段，再输入新文本。

```
Type "hermes agent" into the search field @e3
```

### `browser_scroll` {#browserscroll}

向上或向下滚动页面以显示更多内容。

```
Scroll down to see more results
```

### `browser_press` {#browserpress}

按下键盘按键。适用于提交表单或导航。

```
Press Enter to submit the form
```

支持的按键：`Enter`、`Tab`、`Escape`、`ArrowDown`、`ArrowUp` 等。

### `browser_back` {#browserback}

在浏览器历史记录中导航回上一页。

### `browser_get_images` {#browsergetimages}

列出当前页面上所有图片及其 URL 和 alt 文本。适用于查找需要分析的图片。

### `browser_vision` {#browservision}

截取屏幕截图并使用视觉 AI 进行分析。当文本快照无法捕获重要的视觉信息时使用——尤其适用于验证码、复杂布局或视觉验证挑战。

截图会被持久保存，文件路径会与 AI 分析结果一起返回。在消息平台（Telegram、Discord、Slack、WhatsApp）上，你可以让 Agent 分享截图——它会通过 `MEDIA:` 机制以原生图片附件的形式发送。

```
What does the chart on this page show?
```

截图存储在 `~/.hermes/cache/screenshots/` 中，并在 24 小时后自动清理。

### `browser_console` {#browserconsole}

获取当前页面的浏览器控制台输出（log/warn/error 消息）以及未捕获的 JavaScript 异常。对于检测无障碍树中不显示的静默 JS 错误至关重要。

```
Check the browser console for any JavaScript errors
```

使用 `clear=True` 可在读取后清空控制台，这样后续调用只显示新消息。

### `browser_cdp` {#browsercdp}

原始 Chrome DevTools Protocol 透传——用于其他工具未覆盖的浏览器操作的逃生口。适用于原生对话框处理、iframe 作用域求值、cookie/网络控制，或 Agent 需要的任何 CDP 指令。

**仅在会话启动时 CDP 端点可达时可用**——即 `/browser connect` 已附加到正在运行的 Chrome，或 `config.yaml` 中设置了 `browser.cdp_url`。默认的本地 Agent 浏览器模式、Camofox 以及云提供商（Browserbase、Browser Use、Firecrawl）目前不向此工具暴露 CDP——云提供商有每会话的 CDP URL，但实时会话路由是后续功能。

**CDP 方法参考：** https://chromedevtools.github.io/devtools-protocol/ —— Agent 可以使用 `web_extract` 获取特定方法的页面来查找参数和返回结构。

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

# 获取所有 cookie
browser_cdp(method="Network.getAllCookies")
```
浏览器级别的方法（`Target.*`、`Browser.*`、`Storage.*`）省略了 `target_id`。页面级别的方法（`Page.*`、`Runtime.*`、`DOM.*`、`Emulation.*`）需要从 `Target.getTargets` 获取 `target_id`。每次无状态调用都是独立的——会话不会在调用之间持久化。

**跨域 iframe：** 传递 `frame_id`（来自 `browser_snapshot.frame_tree.children[]` 中 `is_oopif=true` 的项），以通过该 iframe 的 supervisor 实时会话路由 CDP 调用。这就是跨域 iframe 中的 `Runtime.evaluate` 在 Browserbase 上的工作方式——无状态 CDP 连接会遇到签名 URL 过期。示例：

```
browser_cdp(
  method="Runtime.evaluate",
  params={"expression": "document.title", "returnByValue": True},
  frame_id="<来自 browser_snapshot 的 frame_id>",
)
```

同源 iframe 不需要 `frame_id`——改用顶层 `Runtime.evaluate` 中的 `document.querySelector('iframe').contentDocument`。

<a id="browserdialog"></a>
### `browser_dialog` {#browser_dialog}

响应原生 JS 对话框（`alert` / `confirm` / `prompt` / `beforeunload`）。在此工具出现之前，对话框会静默阻塞页面的 JavaScript 线程，后续的 `browser_*` 调用会挂起或抛出异常；现在 Agent 可以在 `browser_snapshot` 输出中看到待处理的对话框，并显式响应。

**工作流程：**
1. 调用 `browser_snapshot`。如果对话框阻塞了页面，它会显示为 `pending_dialogs: [{"id": "d-1", "type": "alert", "message": "..."}]`。
2. 调用 `browser_dialog(action="accept")` 或 `browser_dialog(action="dismiss")`。对于 `prompt()` 对话框，传递 `prompt_text="..."` 以提供响应。
3. 重新快照——`pending_dialogs` 为空；页面的 JS 线程已恢复。

**检测是自动进行的**，通过一个持久的 CDP supervisor——每个任务一个 WebSocket，订阅 Page/Runtime/Target 事件。supervisor 还会在快照中填充 `frame_tree` 字段，以便 Agent 看到当前页面的 iframe 结构，包括跨域（OOPIF）iframe。

**可用性矩阵：**

| 后端 | 通过 `pending_dialogs` 检测 | 响应（`browser_dialog` 工具） |
|---|---|---|
| 通过 `/browser connect` 或 `browser.cdp_url` 连接的本地 Chrome | ✓ | ✓ 完整工作流 |
| Browserbase | ✓ | ✓ 完整工作流（通过注入的 XHR 桥接） |
| Camofox / 默认本地 agent-browser | ✗ | ✗（无 CDP 端点） |

**在 Browserbase 上的工作原理。** Browserbase 的 CDP 代理会在服务端约 10ms 内自动关闭真正的原生对话框，因此我们无法使用 `Page.handleJavaScriptDialog`。supervisor 通过 `Page.addScriptToEvaluateOnNewDocument` 注入一个小脚本，用同步 XHR 覆盖 `window.alert`/`confirm`/`prompt`。我们通过 `Fetch.enable` 拦截这些 XHR——页面的 JS 线程会一直阻塞在 XHR 上，直到我们使用 Agent 的响应调用 `Fetch.fulfillRequest`。`prompt()` 的返回值会原样往返回到页面 JS 中。

**对话框策略** 在 `config.yaml` 的 `browser.dialog_policy` 下配置：

| 策略 | 行为 |
|--------|----------|
| `must_respond`（默认） | 捕获，在快照中显示，等待显式的 `browser_dialog()` 调用。安全自动关闭超时时间为 `browser.dialog_timeout_s`（默认 300s），防止有问题的 Agent 永远卡住。 |
| `auto_dismiss` | 捕获，立即关闭。Agent 仍然会在 `browser_state` 历史中看到对话框，但无需操作。 |
| `auto_accept` | 捕获，立即接受。在浏览带有激进的 `beforeunload` 提示的页面时很有用。 |
**Frame tree** 位于 `browser_snapshot.frame_tree` 中，上限为 30 个 frame 和 OOPIF 深度 2，以控制广告密集页面的负载大小。当达到限制时，会显示 `truncated: true` 标志；需要完整树的 Agents 可以使用 `browser_cdp` 配合 `Page.getFrameTree`。

## 实用示例 {#practical-examples}

### 填写网页表单 {#filling-out-a-web-form}

```
用户：用我的邮箱 john@example.com 在 example.com 上注册一个账号

Agent 工作流程：
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → 看到带有 ref 的表单字段
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → 点击“创建账户”
6. browser_snapshot()  → 确认成功
```

### 研究动态内容 {#researching-dynamic-content}

```
用户：GitHub 上目前最热门的仓库有哪些？

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

启用后，录制会在首次 `browser_navigate` 时自动开始，并在会话关闭时保存到 `~/.hermes/browser_recordings/`。在本地和云端（Browserbase）模式下均可使用。超过 72 小时的录制文件会自动清理。

## 隐身功能 {#stealth-features}

Browserbase 提供自动隐身能力：

| 功能 | 默认值 | 说明 |
|---------|---------|-------|
| 基础隐身 | 始终开启 | 随机指纹、视口随机化、CAPTCHA 解决 |
| 住宅代理 | 开启 | 通过住宅 IP 路由以获得更好的访问 |
| 高级隐身 | 关闭 | 自定义 Chromium 构建，需要 Scale 计划 |
| 保持连接 | 开启 | 网络中断后重新连接会话 |

:::note
如果你的套餐中没有付费功能，Hermes 会自动降级——先禁用 `keepAlive`，再禁用代理——这样免费套餐仍可正常浏览。
:::

## 会话管理 {#session-management}

- 每个任务通过 Browserbase 获得一个独立的浏览器会话
- 会话在空闲后自动清理（默认：2 分钟）
- 后台线程每 30 秒检查一次过期会话
- 进程退出时执行紧急清理，防止孤儿会话
- 会话通过 Browserbase API（`REQUEST_RELEASE` 状态）释放

## 限制 {#limitations}

- **基于文本的交互** — 依赖无障碍树，而非像素坐标
- **快照大小** — 大页面可能被截断或由 LLM 在 8000 字符内总结
- **会话超时** — 云端会话根据你的提供商套餐设置过期
- **成本** — 云端会话消耗提供商积分；会话在对话结束或空闲后自动清理。使用 `/browser connect` 进行免费的本地浏览。
- **不支持文件下载** — 无法从浏览器下载文件
