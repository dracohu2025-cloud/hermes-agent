---
title: Browser Automation
description: 使用多种提供商控制浏览器——通过 CDP 控制本地 Chromium 系列浏览器，或使用云端浏览器进行网页交互、表单填写、数据抓取等操作。
sidebar_label: Browser
sidebar_position: 5
---

<a id="browser-automation"></a>
# 浏览器自动化

Hermes Agent 包含一套完整的浏览器自动化工具集，支持多种后端选项：

- **Browserbase 云端模式** —— 通过 [Browserbase](https://browserbase.com) 使用托管云端浏览器及反机器人工具
- **Browser Use 云端模式** —— 通过 [Browser Use](https://browser-use.com) 作为备选云端浏览器提供商
- **Firecrawl 云端模式** —— 通过 [Firecrawl](https://firecrawl.dev) 使用内建抓取功能的云端浏览器
- **Camofox 本地模式** —— 通过 [Camofox](https://github.com/jo-inc/camofox-browser) 实现本地反检测浏览（基于 Firefox 指纹伪装）
- **本地 Chromium 系列 CDP** —— 使用 `/browser connect` 将浏览器工具连接到您自己的 Chrome、Brave、Chromium 或 Edge 实例
- **本地浏览器模式** —— 通过 `agent-browser` CLI 和本地 Chromium 安装使用

在所有模式下，Agent 都可以浏览网站、与页面元素交互、填写表单以及提取信息。

<a id="overview"></a>
## 概述

页面被表示为**无障碍树**（基于文本的快照），非常适合 LLM Agent。交互元素会获得 ref ID（如 `@e1`、`@e2`），Agent 使用这些 ID 进行点击和输入。

关键能力：

- **多提供商云端执行** —— Browserbase、Browser Use 或 Firecrawl，无需本地浏览器
- **本地 Chromium 系列集成** —— 通过 CDP 附加到正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器，进行实机浏览
- **内置隐身机制** —— 随机指纹、CAPTCHA 识别、住宅代理（Browserbase）
- **会话隔离** —— 每个任务拥有独立的浏览器会话
- **自动清理** —— 不活动的会话会在超时后关闭
- **视觉分析** —— 截图 + AI 分析，实现视觉理解

<a id="setup"></a>
## 设置

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，可以通过 **[Tool Gateway](tool-gateway.md)** 使用浏览器自动化，无需额外 API 密钥。运行 `hermes model` 或 `hermes tools` 即可启用。
:::
<a id="nous-subscribers"></a>

<a id="browserbase-cloud-mode"></a>
### Browserbase 云端模式

要使用 Browserbase 托管的云端浏览器，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSERBASE_API_KEY=***
BROWSERBASE_PROJECT_ID=your-project-id-here
```

在 [browserbase.com](https://browserbase.com) 获取您的凭证。

<a id="browser-use-cloud-mode"></a>
### Browser Use 云端模式

要使用 Browser Use 作为云端浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSER_USE_API_KEY=***
```

在 [browser-use.com](https://browser-use.com) 获取您的 API 密钥。Browser Use 通过其 REST API 提供云端浏览器。如果同时设置了 Browserbase 和 Browser Use 的凭证，则 Browserbase 优先。

<a id="firecrawl-cloud-mode"></a>
### Firecrawl 云端模式

要使用 Firecrawl 作为云端浏览器提供商，请添加：

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
# 自托管 Firecrawl 实例（默认：https://api.firecrawl.dev）
FIRECRAWL_API_URL=http://localhost:3002

# 会话 TTL（秒，默认：300）
FIRECRAWL_BROWSER_TTL=600
```
<a id="hybrid-routing-cloud-for-public-urls-local-for-lan-localhost"></a>
### 混合路由：公开 URL 走云服务，本地 / localhost 走本地

配置了云服务提供商后，Hermes 会自动为解析到私有/回环/LAN 地址的 URL 启动一个**本地 Chromium sidecar**（地址包括 `localhost`、`127.0.0.1`、`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`、`*.local`、`*.lan`、`*.internal`、IPv6 回环 `::1`、链路本地 `169.254.x.x`）。在同一轮对话中，公有 URL 继续使用云服务提供商。

这解决了常见的“我本地开发但用了 Browserbase”工作流——Agent 可以截取你在 `http://localhost:3000` 上的仪表盘，同时爬取 `https://github.com`，你不用切换提供商也不必关闭 SSRF 保护。云服务提供商永远看不到私有 URL。

该功能**默认开启**。要禁用它（所有 URL 像以前一样都发给配置好的云服务提供商）：

```yaml
# ~/.hermes/config.yaml
browser:
  cloud_provider: browserbase
  auto_local_for_private_urls: false
```

关闭自动路由后，私有 URL 会被拒绝并返回 `"Blocked: URL targets a private or internal address"`，除非你同时设置了 `browser.allow_private_urls: true`（这会让云服务提供商去尝试访问它们——通常不会成功，因为 Browserbase 等服务无法访问你的局域网）。

要求：本地 sidecar 使用与纯本地模式相同的 `agent-browser` CLI，因此你需要安装它（`hermes setup tools → Browser Automation` 会自动安装）。从公有 URL 导航后重定向到私有地址仍会被拦截（你无法通过“重定向到内部地址”这种技巧从公有路径进入你的局域网）。

<a id="camofox-local-mode"></a>
### Camofox 本地模式

[Camofox](https://github.com/jo-inc/camofox-browser) 是一个自托管的 Node.js 服务，它封装了 Camoufox（一个带有 C++ 指纹伪造功能的 Firefox 分支）。它提供无需云依赖的本地反检测浏览。

```bash
# 先克隆 Camofox 浏览器服务
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser

# 使用默认容器设置构建并启动 Docker
# （自动检测架构：M1/M2 上为 aarch64，Intel 上为 x86_64）
make up

# 停止并移除默认容器
make down

# 强制干净重建（例如，升级 VERSION/RELEASE 后）
make reset

# 仅下载二进制文件，不构建
make fetch

# 显式覆盖架构或版本
make up ARCH=x86_64
make up VERSION=135.0.1 RELEASE=beta.24
```

`make up` 会立即启动默认容器。如果你想要自定义运行时设置，例如更大的 Node 堆、VNC 或持久化配置文件目录，请先构建镜像，然后自行运行：

```bash
# 构建镜像，但不启动默认容器
make build

# 使用持久化、VNC 实时查看和更大的 Node 堆启动
mkdir -p ~/.camofox-docker
docker run -d \
  --name camofox-browser \
  --restart unless-stopped \
  -p 9377:9377 \
  -p 6080:6080 \
  -p 5901:5900 \
  -e CAMOFOX_PORT=9377 \
  -e ENABLE_VNC=1 \
  -e VNC_BIND=0.0.0.0 \
  -e VNC_RESOLUTION=1920x1080 \
  -e MAX_OLD_SPACE_SIZE=2048 \
  -v ~/.camofox-docker:/root/.camofox \
  camofox-browser:135.0.1-aarch64
```
启用 VNC 后，浏览器以有头模式运行，可在 `http://localhost:6080`（noVNC）实时观看。你也可以使用原生 VNC 客户端连接到 `localhost:5901`。

如果你已经运行过 `make up`，请先停止并移除默认容器，再启动自定义容器：

```bash
make down
# 然后运行上面的自定义 docker run 命令
```

然后在 `~/.hermes/.env` 中设置：

```bash
CAMOFOX_URL=http://localhost:9377
```

或者通过 `hermes tools` → Browser Automation → Camofox 进行配置。

一旦设置了 `CAMOFOX_URL`，所有浏览器工具都会自动路由到 Camofox，而不是 Browserbase 或 agent-browser。

<a id="persistent-browser-sessions"></a>
#### 持久化浏览器会话

默认情况下，每个 Camofox 会话都会获得一个随机身份——重启 Agent 后，cookies 和登录状态不会保留。要启用持久化浏览器会话，请在 `~/.hermes/config.yaml` 中添加以下内容：

```yaml
browser:
  camofox:
    managed_persistence: true
```

然后完全重启 Hermes，使新配置生效。

:::warning 路径层级很重要
Hermes 读取的是 `browser.camofox.managed_persistence`，**而不是**顶层的 `managed_persistence`。一个常见的错误是写成：

```yaml
<a id="nested-path-matters"></a>
# ❌ 错误——Hermes 会忽略这个
managed_persistence: true
```

如果该标志放在了错误的位置，Hermes 会静默地回退到一个随机的临时 `userId`，你的登录状态将在每次会话中丢失。
:::

<a id="what-hermes-does"></a>
##### Hermes 做了什么
- 向 Camofox 发送一个基于 profile 的确定性 `userId`，使服务器可以在不同会话间复用同一个 Firefox profile。
- 清理时跳过服务器端上下文销毁，因此 cookies 和登录状态能在 Agent 任务之间保留。
- 将 `userId` 限定在当前 Hermes profile 范围内，不同 Hermes profile 会获得不同的浏览器 profile（profile 隔离）。

<a id="what-hermes-does-not-do"></a>
##### Hermes 没有做什么
- 它不会强制 Camofox 服务器开启持久化。Hermes 仅发送一个稳定的 `userId`；服务器必须通过将该 `userId` 映射到持久的 Firefox profile 目录来遵守该设置。
- 如果你的 Camofox 服务器构建将每个请求视为临时请求（例如始终调用 `browser.newContext()` 而不加载已存储的 profile），Hermes 无法使这些会话持久化。请确保你运行的是实现了基于 userId 的 profile 持久化的 Camofox 构建版本。

<a id="verify-it-s-working"></a>
##### 验证是否生效

1. 启动 Hermes 和你的 Camofox 服务器。
2. 在浏览器任务中打开 Google（或任何登录站点）并手动登录。
3. 正常结束该浏览器任务。
4. 启动一个新的浏览器任务。
5. 再次打开同一站点——你应该仍然处于登录状态。

如果第 5 步让你退出登录，说明 Camofox 服务器没有遵守稳定的 `userId`。请仔细检查你的配置路径，确认在编辑 `config.yaml` 后完全重启了 Hermes，并验证你的 Camofox 服务器版本支持每个用户持久的 profile。

<a id="where-state-lives"></a>
##### 状态存储在何处

Hermes 从 profile 作用域的目录 `~/.hermes/browser_auth/camofox/`（或非默认 profile 下对应的 `$HERMES_HOME` 目录）派生稳定的 `userId`。实际的浏览器 profile 数据存储在 Camofox 服务器端，以该 `userId` 为键。要完全重置一个持久化 profile，请在 Camofox 服务器上清除它，并移除相应的 Hermes profile 状态目录。
<a id="externally-managed-camofox-sessions"></a>
#### 外部管理的 Camofox 会话

当另一个应用驱动可见的 Camofox 浏览器（比如桌面助手、自定义集成、另一个 Agent）时，配置 Hermes 使用同一个身份，而不是生成它自己的独立配置文件。

三个设置项控制这一行为：

| Setting | Env var | Effect |
|---------|---------|--------|
| `browser.camofox.user_id` | `CAMOFOX_USER_ID` | Camofox `userId` Hermes 在创建标签页时使用。设置此项将会话加入"外部管理"模式。 |
| `browser.camofox.session_key` | `CAMOFOX_SESSION_KEY` | 在创建标签页时发送的 `sessionKey`（即 `listItemId`）。用于在采纳（adopt）期间匹配现有标签页。如果未设置，则默认为每个任务一个值。 |
| `browser.camofox.adopt_existing_tab` | `CAMOFOX_ADOPT_EXISTING_TAB` | 若为 true，Hermes 在首次使用时调用 `GET /tabs?userId=&lt;user_id&gt;`，并在创建新标签页之前重用现有标签页。 |

环境变量优先于 `config.yaml`。两种形式都可以：

```yaml
browser:
  camofox:
    user_id: shared-camofox
    session_key: visible-tab
    adopt_existing_tab: true
```

```bash
CAMOFOX_USER_ID=shared-camofox
CAMOFOX_SESSION_KEY=visible-tab
CAMOFOX_ADOPT_EXISTING_TAB=true
```

**设置 `user_id` 后的变化：**

- Hermes 在任务结束时跳过破坏性清理（与 `managed_persistence: true` 相同）。其他应用的标签页/cookie/配置文件将保留。
- Hermes **不会**调用 `DELETE /sessions/&lt;user_id&gt;`——该端点会清除所有用户数据，因此如果调用将破坏外部应用的会话。

**标签采纳的工作方式（当 `adopt_existing_tab: true` 时）：**

1. 在进程启动后的第一次浏览器工具调用时，Hermes 发出 `GET /tabs?userId=&lt;user_id&gt;`（5秒超时）。
2. 如果响应中的任何标签页的 `listItemId == session_key`，Hermes 采纳该组中最近创建的标签页。
3. 否则，Hermes 采纳该用户最近创建的标签页（任意 `listItemId`）。
4. 如果没有标签页存在或请求失败，Hermes 回退到在下一次操作时创建一个新标签页。

采纳仅在会话的 `tab_id` 被填充之前触发。如果外部应用在运行中关闭了已采纳的标签页，下一次浏览器工具调用将返回一个 Camofox 错误——Hermes 不会在每次调用时重新轮询新标签页。

**选择 `session_key`：** 如果你希望 Hermes 可靠地附加到*特定*的现有标签页，将 `session_key` 设置为外部应用在创建该标签页时使用的 `listItemId`。如果你不设置 `session_key` 而只设置 `user_id`，Hermes 会生成一个任务级别的 `session_key`（`task_&lt;id&gt;`）——Hermes 会与外部应用共享 cookie 和配置文件，但会打开自己的标签页，而不是重用一个。

**并发说明：** 外部应用和 Hermes 可以同时驱动同一个 Camofox `userId`，但 Camofox 不协调客户端之间的每个标签页焦点。请在应用层协调所有权（例如，在 Hermes 运行时外部应用暂停）。

<a id="vnc-live-view"></a>
#### VNC 实时查看

当 Camofox 以有头模式（带有可见的浏览器窗口）运行时，它会在健康检查响应中暴露一个 VNC 端口。Hermes 会自动发现该端口，并将 VNC URL 包含在导航响应中，这样 Agent 可以分享一个链接供你实时观看浏览器。
<a id="local-chromium-family-browser-via-cdp-browser-connect"></a>
### 通过 CDP 连接本地 Chromium 系列浏览器（`/browser connect`）

你可以不依赖云提供商，而是通过 Chrome DevTools 协议（CDP）将 Hermes 浏览器工具附加到自己正在运行的 Chrome、Brave、Chromium 或 Edge 实例上。当你想要实时观察 Agent 的操作、与需要你自己 Cookie/会话的页面交互，或者想避免云浏览器成本时，这非常有用。

:::note
`/browser connect` 是一个 **交互式 CLI 斜杠命令** —— 它不会被网关调度。如果你尝试在 WebUI、Telegram、Discord 或其他网关聊天中运行它，该消息会作为纯文本发送给 Agent，命令不会执行。请从终端启动 Hermes（`hermes` 或 `hermes chat`），然后在其中输入 `/browser connect`。
:::

在 CLI 中，使用：

```
/browser connect                 # Auto-launch/connect to a local Chromium-family browser at http://127.0.0.1:9222
/browser connect ws://host:port  # Connect to a specific CDP endpoint
/browser status                  # Check current connection
/browser disconnect              # Detach and return to cloud/local mode
```

如果浏览器尚未以远程调试模式运行，Hermes 将尝试自动启动一个支持的 Chromium 系列浏览器，并附带 `--remote-debugging-port=9222` 参数。检测范围包括 Brave、Google Chrome、Chromium 和 Microsoft Edge，常见的 Linux 安装路径如 `/opt/brave-bin/brave` 和 `/snap/bin/brave`。

:::tip
要手动启动一个启用了 CDP 的 Chromium 系列浏览器，请使用专用的用户数据目录（user-data-dir），这样即使浏览器已用正常配置文件运行，调试端口也能成功开启：

```bash
# Linux — Brave
brave-browser \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.hermes/chrome-debug \
  --no-first-run \
  --no-default-browser-check &

# Linux — Google Chrome
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.hermes/chrome-debug \
  --no-first-run \
  --no-default-browser-check &

# macOS — Brave
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check &

# macOS — Google Chrome
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check &
```

然后启动 Hermes CLI 并运行 `/browser connect`。

**为什么需要 `--user-data-dir`？** 如果不指定，当浏览器常规实例已在运行时，启动 Chromium 系列浏览器通常会在已有进程上打开一个新窗口 —— 而那个已有进程启动时没有加 `--remote-debugging-port` 参数，所以端口 9222 永远不会开放。使用专用的用户数据目录会强制启动一个新的浏览器进程，从而使调试端口真正监听。`--no-first-run --no-default-browser-check` 用于跳过新配置文件的首次启动向导。
:::

当通过 CDP 连接后，所有浏览器工具（`browser_navigate`、`browser_click` 等）都会在你实际的浏览器实例上运行，而不会再启动云会话。
<a id="wsl2-windows-chrome-prefer-mcp-over-browser-connect"></a>
### WSL2 + Windows Chrome：优先使用 MCP 而非 `/browser connect`

如果 Hermes 运行在 WSL2 内部，但你要控制的 Chrome 窗口运行在 Windows 宿主机上，那么 `/browser connect` 通常不是最佳方案。

原因如下：

- `/browser connect` 要求 Hermes 自己能访问到一个可用的 CDP 端点
- 现代 Chrome 的实时调试会话通常暴露一个仅宿主机本地可访问的端点，而无法像传统的 `9222` 端口那样从 WSL 直接访问
- 即使 Windows 上的 Chrome 可调试，最干净的集成方式往往是让 Windows 端的浏览器 MCP 服务器连接到 Chrome，然后让 Hermes 与该 MCP 服务器通信

对于这种场景，建议通过 Hermes 的 MCP 支持优先使用 `chrome-devtools-mcp`。

具体配置请参见 MCP 指南：

- [在 Hermes 中使用 MCP](../../guides/use-mcp-with-hermes.md#wsl2-bridge-hermes-in-wsl-to-windows-chrome)

<a id="local-browser-mode"></a>
### 本地浏览器模式

如果你**没有**设置任何云凭证，也没有使用 `/browser connect`，Hermes 仍然可以通过由 `agent-browser` 驱动的本地 Chromium 安装来使用浏览器工具。

<a id="optional-environment-variables"></a>
### 可选环境变量

```bash
# 住宅代理，用于更好地解决 CAPTCHA（默认: "true"）
BROWSERBASE_PROXIES=true

# 高级隐身，搭配自定义 Chromium —— 需要 Scale 计划（默认: "false"）
BROWSERBASE_ADVANCED_STEALTH=false

# 断开连接后会话重连 —— 需要付费计划（默认: "true"）
BROWSERBASE_KEEP_ALIVE=true

# 自定义会话超时时间（毫秒）（默认: 项目默认值）
# 示例: 600000 (10分钟), 1800000 (30分钟)
BROWSERBASE_SESSION_TIMEOUT=600000

# 自动清理前的不活动超时时间（秒）（默认: 120）
BROWSER_INACTIVITY_TIMEOUT=120

# 额外的 Chromium 启动标志（逗号或换行分隔）。当 Hermes 检测到 root 或 AppArmor 限制的非特权用户命名空间
#（Ubuntu 23.10+、DGX Spark、许多容器镜像）时，会自动注入 `--no-sandbox,--disable-dev-shm-usage`，
# 因此大多数用户不需要设置此项。仅在你需要一个 Hermes 不会自动添加的标志时手动设置；设置此项会禁用自动注入。
AGENT_BROWSER_ARGS=--no-sandbox
```

<a id="install-agent-browser-cli"></a>
### 安装 agent-browser CLI

```bash
npm install -g agent-browser
# 或者在本仓库中本地安装：
npm install
```

:::info
`browser` 工具集必须包含在你的配置的 `toolsets` 列表中，或者通过 `hermes config set toolsets '["hermes-cli", "browser"]'` 启用。
:::

<a id="available-tools"></a>
## 可用工具

<a id="browsernavigate"></a>
### `browser_navigate`

导航到一个 URL。必须在任何其他浏览器工具之前调用。初始化 Browserbase 会话。

```
导航到 https://github.com/NousResearch
```

:::tip
对于简单的信息检索，优先使用 `web_search` 或 `web_extract` —— 它们更快且更便宜。当你需要**与页面交互**（点击按钮、填写表单、处理动态内容）时，才使用浏览器工具。
:::

<a id="browsersnapshot"></a>
### `browser_snapshot`

获取当前页面的无障碍树文本快照。返回带有引用 ID（如 `@e1`、`@e2`）的可交互元素，以便与 `browser_click` 和 `browser_type` 配合使用。

- **`full=false`**（默认）：紧凑视图，仅显示可交互元素
- **`full=true`**：完整页面内容
超过8000字符的快照会自动由大语言模型总结。

<a id="browserclick"></a>
### `browser_click`

根据快照中的引用 ID 点击元素。

```
点击 @e5 以按下 "Sign In" 按钮
```

<a id="browsertype"></a>
### `browser_type`

在输入框中输入文本。会先清空字段，再输入新文本。

```
在搜索字段 @e3 中输入 "hermes agent"
```

<a id="browserscroll"></a>
### `browser_scroll`

上下滚动页面以显示更多内容。

```
向下滚动以查看更多结果
```

<a id="browserpress"></a>
### `browser_press`

按下键盘按键。适合用于提交表单或导航。

```
按 Enter 提交表单
```

支持的按键：`Enter`、`Tab`、`Escape`、`ArrowDown`、`ArrowUp` 等。

<a id="browserback"></a>
### `browser_back`

在浏览器历史记录中返回上一页。

<a id="browsergetimages"></a>
### `browser_get_images`

列出当前页面上所有图片的 URL 和替代文本。适合用于查找需要分析的图片。

<a id="browservision"></a>
### `browser_vision`

截取屏幕截图并用视觉 AI 分析。当文本快照未能捕捉到重要的视觉信息时使用——尤其适用于验证码、复杂布局或视觉验证挑战。

截图会被持久保存，文件路径会随 AI 分析结果一起返回。在消息平台（Telegram、Discord、Slack、WhatsApp）上，你可以要求 Agent 分享截图——它会通过 `MEDIA:` 机制以原生图片附件的形式发送。

```
此页面上的图表显示了什么？
```

截图存储在 `~/.hermes/cache/screenshots/` 中，24 小时后会自动清理。

<a id="browserconsole"></a>
### `browser_console`

获取当前页面的浏览器控制台输出（log/warn/error 消息）以及未捕获的 JavaScript 异常。对于检测不会出现在无障碍树中的静默 JS 错误至关重要。

```
检查浏览器控制台是否有任何 JavaScript 错误
```

使用 `clear=True` 可以在读取后清空控制台，这样后续调用只显示新消息。

`browser_console` 在使用 `expression` 参数调用时也会执行 JavaScript——与 DevTools 控制台的用法相同，结果会以解析后的形式返回（JSON 序列化的对象会变成字典；原始值保持原始类型）。

```
browser_console(expression="document.querySelector('h1').textContent")
browser_console(expression="JSON.stringify(performance.timing)")
```

如果当前会话激活了 CDP 主管（任何针对支持 CDP 的后端运行了 `browser_navigate` 的会话通常都会），则会在主管的持久 WebSocket 上执行计算——没有子进程启动开销。否则会回退到标准的 agent-browser CLI 路径。两种方式行为相同；只有延迟会变化。

<a id="browsercdp"></a>
### `browser_cdp`

原始 Chrome DevTools 协议透传——用于处理其他工具未涵盖的浏览器操作。用于原生对话框处理、iframe 作用域计算、cookie/网络控制或 Agent 需要的任何 CDP 指令。

**仅当在会话开始时可以访问到 CDP 端点时才可用**——这意味着 `/browser connect` 已附加到正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器，或者 `config.yaml` 中设置了 `browser.cdp_url`。默认的本机 agent-browser 模式、Camofox 以及云提供商（Browserbase、Browser Use、Firecrawl）目前不向此工具暴露 CDP——云提供商有按会话分配的 CDP URL，但实时会话路由是后续跟进。
**CDP 方法参考：** https://chromedevtools.github.io/devtools-protocol/ — Agent 可以通过 `web_extract` 提取某个具体方法的页面，来查看参数和返回结构。

常见模式：

```
# 列出标签页（浏览器级别，无需 target_id）
browser_cdp(method="Target.getTargets")

# 处理标签页上的原生 JS 对话框
browser_cdp(method="Page.handleJavaScriptDialog",
            params={"accept": true, "promptText": ""},
            target_id="<tabId>")

# 在指定标签页中执行 JS
browser_cdp(method="Runtime.evaluate",
            params={"expression": "document.title", "returnByValue": true},
            target_id="<tabId>")

# 获取所有 Cookie
browser_cdp(method="Network.getAllCookies")
```

浏览器级别的方法（`Target.*`、`Browser.*`、`Storage.*`）不需要 `target_id`。页面级别的方法（`Page.*`、`Runtime.*`、`DOM.*`、`Emulation.*`）需要从 `Target.getTargets` 获取 `target_id`。每次无状态调用都是独立的——会话不会在调用之间持久化。

**跨域 iframe：** 传入 `frame_id`（来自 `browser_snapshot.frame_tree.children[]` 中 `is_oopif=true` 的项），将 CDP 调用路由到该 iframe 的 supervisor 实时会话。这就是在 Browserbase 上跨域 iframe 内 `Runtime.evaluate` 的工作原理，因为无状态 CDP 连接会遇到签名 URL 过期的问题。示例：

```
browser_cdp(
  method="Runtime.evaluate",
  params={"expression": "document.title", "returnByValue": True},
  frame_id="<来自 browser_snapshot 的 frame_id>",
)
```

同源 iframe 不需要 `frame_id`——可以直接在顶层 `Runtime.evaluate` 中使用 `document.querySelector('iframe').contentDocument` 来访问。

<a id="browserdialog"></a>
### `browser_dialog` {#browser_dialog}

响应原生 JS 对话框（`alert` / `confirm` / `prompt` / `beforeunload`）。在这个工具出现之前，对话框会静默阻塞页面的 JavaScript 线程，后续的 `browser_*` 调用会挂起或抛出异常；现在 Agent 可以在 `browser_snapshot` 输出中看到待处理的对话框，并显式响应。

**工作流程：**
1. 调用 `browser_snapshot`。如果有对话框阻塞页面，它会显示为 `pending_dialogs: [{"id": "d-1", "type": "alert", "message": "..."}]`。
2. 调用 `browser_dialog(action="accept")` 或 `browser_dialog(action="dismiss")`。对于 `prompt()` 对话框，传入 `prompt_text="..."` 来提供输入内容。
3. 重新快照——`pending_dialogs` 为空；页面的 JS 线程已恢复。

**检测是自动完成的**，通过一个持久的 CDP supervisor——每个任务一个 WebSocket，订阅 Page/Runtime/Target 事件。supervisor 还会在快照中填充 `frame_tree` 字段，以便 Agent 查看当前页面的 iframe 结构，包括跨域（OOPIF）iframe。

**可用性矩阵：**

| 后端 | 通过 `pending_dialogs` 检测 | 响应（`browser_dialog` 工具） |
|---|---|---|
| 通过 `/browser connect` 或 `browser.cdp_url` 连接的本地 Chrome | ✓ | ✓ 完整工作流程 |
| Browserbase | ✓ | ✓ 完整工作流程（通过注入的 XHR 桥接） |
| Camofox / 默认本地 agent-browser | ✗ | ✗（无 CDP 端点） |
**在 Browserbase 上的工作原理。** Browserbase 的 CDP 代理会在服务端约 10ms 内自动关闭真实原生对话框，因此我们无法使用 `Page.handleJavaScriptDialog`。主管通过 `Page.addScriptToEvaluateOnNewDocument` 注入一个小脚本，用同步 XHR 覆盖 `window.alert`/`confirm`/`prompt`。我们通过 `Fetch.enable` 拦截这些 XHR——页面的 JS 线程会一直阻塞在 XHR 上，直到我们调用 `Fetch.fulfillRequest` 返回 Agent 的响应。`prompt()` 的返回值会原样往返回到页面的 JS 中。

**对话框策略** 在 `config.yaml` 的 `browser.dialog_policy` 下配置：

| 策略 | 行为 |
|--------|------|
| `must_respond`（默认） | 捕获，在快照中展示，等待显式的 `browser_dialog()` 调用。安全意识超时后自动关闭（`browser.dialog_timeout_s`，默认 300 秒），防止有问题的 Agent 无限卡住。 |
| `auto_dismiss` | 捕获，立即关闭。Agent 仍然可以在 `browser_state` 历史中看到该对话框，但无需采取行动。 |
| `auto_accept` | 捕获，立即接受。适用于导航到带有激进的 `beforeunload` 提示的页面。 |

**帧树** 在 `browser_snapshot.frame_tree` 中限制为最多 30 帧，OOPIF 深度 2，以控制广告密集页面上的负载大小。当达到限制时，会显示 `truncated: true` 标志；需要完整树的 Agent 可以使用带 `Page.getFrameTree` 的 `browser_cdp`。

<a id="practical-examples"></a>
## 实际示例

<a id="filling-out-a-web-form"></a>
### 填写 Web 表单

```
用户：用我的邮箱 john@example.com 在 example.com 上注册账户

Agent 工作流：
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → 看到带引用标识的表单字段
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → 点击“创建账户”
6. browser_snapshot()  → 确认成功
```

<a id="researching-dynamic-content"></a>
### 研究动态内容

```
用户：GitHub 上目前最热门的仓库是什么？

Agent 工作流：
1. browser_navigate("https://github.com/trending")
2. browser_snapshot(full=true)  → 读取热门仓库列表
3. 返回格式化结果
```

<a id="session-recording"></a>
## 会话录制

自动将浏览器会话录制为 WebM 视频文件：

```yaml
browser:
  record_sessions: true  # 默认：false
```

启用后，录制会在第一次 `browser_navigate` 时自动开始，并在会话关闭时保存到 `~/.hermes/browser_recordings/`。本地和云端（Browserbase）模式下均可工作。超过 72 小时的录制文件会自动清理。

<a id="stealth-features"></a>
## 隐身特性

Browserbase 提供自动隐身能力：

| 特性 | 默认 | 说明 |
|---------|-------|------|
| 基本隐身 | 始终开启 | 随机指纹、视口随机化、CAPTCHA 解决 |
| 住宅代理 | 开启 | 通过住宅 IP 路由以获得更好的访问能力 |
| 高级隐身 | 关闭 | 自定义 Chromium 构建，需要 Scale 计划 |
| 保持在线 | 开启 | 网络故障后会话重连 |

:::note
如果你的计划中没有包含付费功能，Hermes 会自动降级——先禁用 `keepAlive`，然后是代理——这样免费计划下浏览仍然可用。
:::
<a id="session-management"></a>
## 会话管理

- 每个任务通过 Browserbase 获得一个独立的浏览器会话
- 会话在无操作后会自动清理（默认：2 分钟）
- 后台线程每 30 秒检查是否有过期的会话
- 进程退出时执行紧急清理，以防止产生孤儿会话
- 会话通过 Browserbase API 释放（`REQUEST_RELEASE` 状态）

<a id="limitations"></a>
## 限制

- **基于文本的交互** — 依赖无障碍树，而非像素坐标
- **快照大小** — 大型页面可能被截断，或由 LLM 在 8000 字符以内进行摘要
- **会话超时** — 云会话会根据你所用服务商的套餐设置过期
- **费用** — 云会话会消耗服务商的积分；对话结束或闲置后会话自动清理。使用 `/browser connect` 可免费进行本地浏览
- **不支持文件下载** — 无法从浏览器下载文件
