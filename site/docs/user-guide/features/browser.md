---
title: 浏览器自动化
description: 通过多种提供商控制浏览器，包括通过 CDP 连接本地 Chrome 或使用云浏览器，实现网页交互、表单填写、数据抓取等功能。
sidebar_label: 浏览器
sidebar_position: 5
---

# 浏览器自动化

Hermes Agent 包含一套完整的浏览器自动化工具集，提供多种后端选项：

- **Browserbase 云模式**：通过 [Browserbase](https://browserbase.com) 使用托管的云浏览器和反机器人工具
- **Browser Use 云模式**：通过 [Browser Use](https://browser-use.com) 作为替代的云浏览器提供商
- **通过 CDP 连接本地 Chrome** — 使用 `/browser connect` 将浏览器工具连接到您自己的 Chrome 实例
- **本地浏览器模式** — 通过 `agent-browser` CLI 和本地安装的 Chromium 运行

在所有模式下，Agent 都可以导航网站、与页面元素交互、填写表单以及提取信息。

## 概述

页面被表示为**无障碍功能树**（基于文本的快照），这使其非常适合 LLM Agent。交互元素会获得引用 ID（如 `@e1`、`@e2`），Agent 使用这些 ID 进行点击和输入。

核心功能：

- **多提供商云执行** — 使用 Browserbase 或 Browser Use，无需本地浏览器
- **本地 Chrome 集成** — 通过 CDP 附加到您正在运行的 Chrome 实例，进行手动浏览
- **内置隐身功能** — 随机指纹、验证码解决、住宅代理（Browserbase）
- **会话隔离** — 每个任务都有自己独立的浏览器会话
- **自动清理** — 不活动的会话在超时后会自动关闭
- **视觉分析** — 截图 + AI 分析，用于视觉理解

## 设置

### Browserbase 云模式

要使用 Browserbase 托管的云浏览器，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSERBASE_API_KEY=***
BROWSERBASE_PROJECT_ID=your-project-id-here
```

在 [browserbase.com](https://browserbase.com) 获取您的凭证。

### Browser Use 云模式

要使用 Browser Use 作为您的云浏览器提供商，请添加：

```bash
# 添加到 ~/.hermes/.env
BROWSER_USE_API_KEY=***
```

在 [browser-use.com](https://browser-use.com) 获取您的 API 密钥。Browser Use 通过其 REST API 提供云浏览器。如果同时设置了 Browserbase 和 Browser Use 的凭证，Browserbase 将优先使用。

### 通过 CDP 连接本地 Chrome (`/browser connect`)

您可以选择不使用云提供商，而是通过 Chrome DevTools 协议 (CDP) 将 Hermes 浏览器工具附加到您自己正在运行的 Chrome 实例。这在您想实时查看 Agent 的操作、与需要您自己的 Cookie/会话的页面交互，或避免云浏览器成本时非常有用。

在 CLI 中，使用：

```
/browser connect              # 连接到 ws://localhost:9222 的 Chrome
/browser connect ws://host:port  # 连接到特定的 CDP 端点
/browser status               # 检查当前连接状态
/browser disconnect            # 断开连接并返回云/本地模式
```

如果 Chrome 尚未以远程调试模式运行，Hermes 将尝试使用 `--remote-debugging-port=9222` 参数自动启动它。

:::tip
手动启动启用 CDP 的 Chrome：
```bash
# Linux
google-chrome --remote-debugging-port=9222

# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
```
:::

通过 CDP 连接后，所有浏览器工具（`browser_navigate`、`browser_click` 等）都将在您实时的 Chrome 实例上操作，而不是启动云会话。

### 本地浏览器模式

如果您**没有**设置任何云凭证，并且不使用 `/browser connect`，Hermes 仍然可以通过 `agent-browser` 驱动的本地 Chromium 安装来使用浏览器工具。

### 可选环境变量

```bash
# 用于更好解决验证码的住宅代理（默认："true"）
BROWSERBASE_PROXIES=true

# 使用自定义 Chromium 的高级隐身功能 — 需要 Scale 计划（默认："false"）
BROWSERBASE_ADVANCED_STEALTH=false

# 断开连接后重新连接会话 — 需要付费计划（默认："true"）
BROWSERBASE_KEEP_ALIVE=true

# 自定义会话超时时间（毫秒）（默认：项目默认值）
# 示例：600000 (10分钟), 1800000 (30分钟)
BROWSERBASE_SESSION_TIMEOUT=600000

# 自动清理前的不活动超时时间（秒）（默认：300）
BROWSER_INACTIVITY_TIMEOUT=300
```

### 安装 agent-browser CLI

```bash
npm install -g agent-browser
# 或者在仓库中本地安装：
npm install
```

:::info
`browser` 工具集必须包含在您配置的 `toolsets` 列表中，或通过 `hermes config set toolsets '["hermes-cli", "browser"]'` 启用。
:::

## 可用工具

### `browser_navigate`

导航到一个 URL。必须在调用任何其他浏览器工具之前调用。初始化 Browserbase 会话。

```
Navigate to https://github.com/NousResearch
```

:::tip
对于简单的信息检索，建议优先使用 `web_search` 或 `web_extract` — 它们更快、更便宜。当您需要与页面**交互**时（点击按钮、填写表单、处理动态内容），再使用浏览器工具。
:::

### `browser_snapshot`

获取当前页面无障碍功能树的基于文本的快照。返回带有引用 ID（如 `@e1`、`@e2`）的交互元素，供 `browser_click` 和 `browser_type` 使用。

- **`full=false`** (默认)：紧凑视图，仅显示交互元素
- **`full=true`**：完整的页面内容

超过 8000 个字符的快照会自动由 LLM 进行摘要。

### `browser_click`

点击快照中通过其引用 ID 标识的元素。

```
Click @e5 to press the "Sign In" button
```

### `browser_type`

在输入字段中输入文本。首先清除字段，然后输入新文本。

```
Type "hermes agent" into the search field @e3
```

### `browser_scroll`

向上或向下滚动页面以显示更多内容。

```
Scroll down to see more results
```

### `browser_press`

按下键盘按键。适用于提交表单或导航。

```
Press Enter to submit the form
```

支持的按键：`Enter`、`Tab`、`Escape`、`ArrowDown`、`ArrowUp` 等。

### `browser_back`

在浏览器历史记录中导航回上一页。

### `browser_get_images`

列出当前页面上的所有图片及其 URL 和替代文本。适用于查找要分析的图片。

### `browser_vision`

截图并使用视觉 AI 进行分析。当文本快照无法捕捉重要的视觉信息时使用此工具 — 对于验证码、复杂布局或视觉验证挑战尤其有用。

截图会被持久保存，文件路径会与 AI 分析结果一起返回。在消息平台（Telegram、Discord、Slack、WhatsApp）上，您可以要求 Agent 分享截图 — 它将通过 `MEDIA:` 机制作为原生照片附件发送。

```
What does the chart on this page show?
```

截图存储在 `~/.hermes/browser_screenshots/` 目录中，并在 24 小时后自动清理。

### `browser_console`

获取浏览器控制台输出（日志/警告/错误消息）以及当前页面未捕获的 JavaScript 异常。对于检测无障碍功能树中不显示的静默 JS 错误至关重要。

```
Check the browser console for any JavaScript errors
```

使用 `clear=True` 在读取后清除控制台，这样后续调用只显示新消息。

### `browser_close`

关闭浏览器会话并释放资源。完成后调用此工具以释放 Browserbase 会话配额。

## 实际示例

### 填写网页表单

```
用户：在 example.com 上用我的邮箱 john@example.com 注册一个账户

Agent 工作流程：
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → 看到带有引用的表单字段
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → 点击 "Create Account"
6. browser_snapshot()  → 确认成功
7. browser_close()
```

### 研究动态内容

```
用户：GitHub 上当前最热门的仓库是什么？

Agent 工作流程：
1. browser_navigate("https://github.com/trending")
2. browser_snapshot(full=true)  → 读取热门仓库列表
3. 返回格式化的结果
4. browser_close()
```

## 会话录制

自动将浏览器会话录制为 WebM 视频文件：

```yaml
browser:
  record_sessions: true  # 默认：false
```

启用后，录制会在第一次 `browser_navigate` 时自动开始，并在会话关闭时保存到 `~/.hermes/browser_recordings/`。在本地和云（Browserbase）模式下均可工作。超过 72 小时的录制文件会自动清理。

## 隐身功能

Browserbase 提供自动隐身功能：

| 功能 | 默认 | 说明 |
|---------|---------|-------|
| 基础隐身 | 始终开启 | 随机指纹、视口随机化、验证码解决 |
| 住宅代理 | 开启 | 通过住宅 IP 路由以获得更好的访问效果 |
| 高级隐身 | 关闭 | 自定义 Chromium 构建，需要 Scale 计划 |
| 保持连接 | 开启 | 网络中断后重新连接会话 |

:::note
如果您的计划中没有付费功能，Hermes 会自动回退 — 首先禁用 `keepAlive`，然后是代理 — 因此在免费计划上浏览仍然有效。
:::

## 会话管理

- 每个任务通过 Browserbase 获得一个隔离的浏览器会话
- 会话在不活动后会自动清理（默认：5 分钟）
- 后台线程每 30 秒检查一次过期的会话
- 进程退出时运行紧急清理，以防止会话残留
- 通过 Browserbase API（`REQUEST_RELEASE` 状态）释放会话

## 限制

- **基于文本的交互** — 依赖于无障碍功能树，而非像素坐标
- **快照大小** — 大型页面可能在 8000 个字符处被截断或由 LLM 摘要
- **会话超时** — 云会话根据您的提供商计划设置过期
- **成本** — 云会话消耗提供商积分；完成后请使用 `browser_close`。使用 `/browser connect` 进行免费的本地浏览。
- **不支持文件下载** — 无法从浏览器下载文件
