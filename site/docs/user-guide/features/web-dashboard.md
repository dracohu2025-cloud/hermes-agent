---
sidebar_position: 15
title: "Web Dashboard"
description: "基于浏览器的仪表盘，用于管理配置、API 密钥、会话、日志、分析、定时任务和技能"
---

<a id="web-dashboard"></a>
# Web Dashboard

Web Dashboard 是一个基于浏览器的 UI，用于管理你的 Hermes Agent 安装。无需编辑 YAML 文件或运行 CLI 命令，你可以通过一个简洁的 Web 界面来配置设置、管理 API 密钥以及监控会话。

<a id="quick-start"></a>
## 快速开始

```bash
hermes dashboard
```

这条命令会启动一个本地 Web 服务器，并在浏览器中打开 `http://127.0.0.1:9119`。仪表盘完全在你的机器上运行——不会有数据离开本地主机。

<a id="options"></a>
### 选项

| 标志 | 默认值 | 描述 |
|------|--------|------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--insecure` | off | 允许绑定到非本地主机地址（**危险**——会在网络上暴露 API 密钥；需配合防火墙和强认证） |
| `--tui` | off | 暴露浏览器内的 Chat 标签页（通过 PTY/WebSocket 内嵌的 `hermes --tui`）。也可以设置 `HERMES_DASHBOARD_TUI=1`。 |

```bash
# 自定义端口
hermes dashboard --port 8080

# 绑定到所有网络接口（在共享网络上请谨慎使用）
hermes dashboard --host 0.0.0.0

# 启动时不打开浏览器
hermes dashboard --no-open

# 启用浏览器内的 Chat 标签页
hermes dashboard --tui
```

<a id="prerequisites"></a>
## 前置条件

默认的 `hermes-agent` 安装不包含 HTTP 栈或 PTY 辅助程序——它们是可选的附加组件。**Web Dashboard** 需要 FastAPI 和 Uvicorn（`web` 附加组件）。**Chat** 标签页还需要 `ptyprocess` 来在伪终端后面生成内嵌的 TUI（POSIX 系统上的 `pty` 附加组件）。同时安装两者：

```bash
pip install 'hermes-agent[web,pty]'
```

`web` 附加组件会安装 FastAPI/Uvicorn；`pty` 会安装 `ptyprocess`（POSIX）或 `pywinpty`（原生 Windows——注意内嵌的 TUI 本身仍需 WSL）。`pip install hermes-agent[all]` 会包含这两个附加组件，如果你也想要消息/语音等功能，这是最简单的路径。

当你在没有依赖的情况下运行 `hermes dashboard` 时，它会告诉你需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

在普通的 `hermes dashboard` 启动中，Chat 标签页默认是关闭的。若想启用内嵌的浏览器聊天面板，请使用 `hermes dashboard --tui` 启动仪表盘，或设置 `HERMES_DASHBOARD_TUI=1`。

<a id="pages"></a>
## 页面

<a id="status"></a>
### 状态

着陆页面显示你的安装的实时概览：

- **Agent 版本** 和发布日期
- **网关状态** —— 运行/停止、PID、已连接的平台及其状态
- **活跃会话** —— 过去 5 分钟内活跃的会话数
- **最近会话** —— 最近 20 个会话的列表，包含模型、消息数量、Token 用量以及对话预览

状态页面每 5 秒自动刷新一次。

<a id="chat"></a>
### Chat

**Chat** 标签页将完整的 Hermes TUI（与你从 `hermes --tui` 获得的界面相同）直接嵌入到浏览器中。你在终端 TUI 中能做的一切——斜杠命令、模型选择器、工具调用卡片、Markdown 流式输出、clarify/sudo/approval 提示、皮肤主题——在这里都能以相同的方式工作，因为仪表盘运行的是真正的 TUI 二进制文件，并通过 [xterm.js](https://xtermjs.org/) 及其 WebGL 渲染器来渲染其 ANSI 输出，实现像素级的精确单元格布局。
**工作原理：**

- `/api/pty` 打开一个通过仪表盘会话令牌认证的 WebSocket
- 服务器在 POSIX 伪终端背后启动 `hermes --tui`
- 按键输入传送到 PTY；ANSI 输出流回浏览器
- xterm.js 的 WebGL 渲染器将每个单元格绘制到整数像素网格上；鼠标追踪（SGR 1006）、宽字符（Unicode 11）和制表符图形均原生渲染
- 调整浏览器窗口大小会通过 `@xterm/addon-fit` 插件调整 TUI 大小

**恢复现有会话：** 在 **会话** 标签页中，点击任何会话旁边的播放图标（▶）。这将跳转到 `/chat?resume=&lt;id&gt;` 并使用 `--resume` 启动 TUI，加载完整历史记录。

**前提条件：**

- Node.js（与 `hermes --tui` 要求相同；TUI 包在首次启动时构建）
- `ptyprocess`——由 `pty` 附加包安装（`pip install 'hermes-agent[web,pty]'`，或者 `[all]` 同时包含两者）
- POSIX 内核（Linux、macOS 或 WSL2）。`/chat` 终端面板特别需要 POSIX PTY——原生 Windows Python 没有等效项，因此在原生 Windows 安装中，仪表盘的其余部分（会话、作业、指标、配置编辑器）正常工作，但 `/chat` 标签页会显示一条横幅，提示您使用 WSL2 来使用该功能。

关闭浏览器标签页后，PTY 会在服务器端被干净地回收。重新打开会生成一个新会话。

<a id="config"></a>
### 配置

一个基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都从 `DEFAULT_CONFIG` 自动发现，并组织到带标签的分类中：

- **model** — 默认模型、提供商、基础 URL、推理设置
- **terminal** — 后端（local/docker/ssh/modal）、超时时间、shell 偏好
- **display** — 皮肤、工具进度、恢复显示、旋转指示器设置
- **agent** — 最大迭代次数、网关超时、服务层级
- **delegation** — 子 Agent 限制、推理努力程度
- **memory** — 提供商选择、上下文注入设置
- **approvals** — 危险命令批准模式（ask/yolo/deny）
- 更多 — config.yaml 的每一部分都有对应的表单字段

具有已知有效值的字段（终端后端、皮肤、批准模式等）呈现为下拉列表。布尔值呈现为开关。其他所有内容都是文本输入框。

**操作：**

- **保存** — 立即将更改写入 `config.yaml`
- **重置为默认值** — 将所有字段恢复为默认值（在单击保存之前不会保存）
- **导出** — 将当前配置下载为 JSON
- **导入** — 上传一个 JSON 配置文件以替换当前值

:::tip
配置更改将在下一个 Agent 会话或网关重启时生效。Web 仪表盘编辑的是与 `hermes config set` 和网关读取的同一个 `config.yaml` 文件。
:::

<a id="api-keys"></a>
### API 密钥

管理存储 API 密钥和凭据的 `.env` 文件。密钥按类别分组：

- **LLM 提供商** — OpenRouter、Anthropic、OpenAI、DeepSeek 等。
- **工具 API 密钥** — Browserbase、Firecrawl、Tavily、ElevenLabs 等。
- **消息平台** — Telegram、Discord、Slack 机器人令牌等。
- **Agent 设置** — 非秘密环境变量，如 `API_SERVER_ENABLED`
每个键都显示：
- 当前是否已设置（附带经过脱敏处理的值预览）
- 用途说明
- 指向提供商注册/获取密钥页面的链接
- 用于设置或更新值的输入框
- 用于删除的删除按钮

高级/不常用的键默认隐藏在切换开关后方。

<a id="sessions"></a>
### 会话 (Sessions)

浏览并检查所有 Agent 会话。每一行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、Cron）、模型名称、消息数量、工具调用次数以及上次活跃至今的时间。活跃会话会带有脉动徽章标记。

- **搜索** — 使用 FTS5 对所有消息内容进行全文搜索。搜索结果会高亮显示片段，展开时自动滚动到第一条匹配消息。
- **展开** — 点击某个会话可加载完整的消息历史。消息按角色（用户、助手、系统、工具）以不同颜色标识，并以 Markdown 格式呈现，附带语法高亮。
- **工具调用** — 包含工具调用的助手消息会显示可折叠的区块，其中包含函数名称和 JSON 参数。
- **删除** — 使用垃圾桶图标删除会话及其消息历史。

<a id="logs"></a>
### 日志 (Logs)

查看 Agent、Gateway 和错误日志文件，支持过滤和实时跟踪。

- **文件** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** — 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** — 按来源组件过滤：全部、gateway、agent、tools、cli 或 cron
- **行数** — 选择显示的行数（50、100、200 或 500）
- **自动刷新** — 开启实时跟踪，每 5 秒轮询一次新的日志行
- **颜色标识** — 日志行按严重程度着色（红色表示错误，黄色表示警告，灰暗表示调试）

<a id="analytics"></a>
### 分析 (Analytics)

基于会话历史计算的使用量和成本分析。选择一个时间范围（7 天、30 天或 90 天）以查看：

- **摘要卡片** — 总 Token 数（输入/输出）、缓存命中率、总预估或实际成本、总会话数及日均会话数
- **每日 Token 图** — 堆叠柱状图，显示每日输入和输出 Token 的使用情况，悬停时显示明细和成本
- **每日明细表** — 每天的数据：日期、会话数、输入 Token、输出 Token、缓存命中率、成本
- **按模型明细** — 显示每个使用过的模型、其会话数、Token 使用量及预估成本

<a id="cron"></a>
### 定时任务 (Cron)

创建和管理按计划重复运行 Agent Prompt 的定时任务。

- **创建** — 填写名称（可选）、Prompt、Cron 表达式（例如 `0 9 * * *`）和投递目标（本地、Telegram、Discord、Slack 或 Email）
- **任务列表** — 每个任务显示其名称、Prompt 预览、调度表达式、状态徽章（已启用/已暂停/错误）、投递目标、上次运行时间和下次运行时间
- **暂停 / 恢复** — 在活跃和暂停状态间切换任务
- **立即触发** — 立即执行一次任务，不受常规调度影响
- **删除** — 永久删除一个定时任务

<a id="skills"></a>
### 技能 (Skills)

浏览、搜索和启用/禁用技能与工具集。技能从 `~/.hermes/skills/` 加载，并按类别分组。
- **搜索（Search）** — 按名称、描述或类别筛选技能和工具集
- **类别筛选（Category filter）** — 点击类别标签来缩小列表范围（例如 MLOps、MCP、红队测试、AI）
- **开关（Toggle）** — 使用开关启用或禁用单个技能。更改将在下一次会话中生效。
- **工具集（Toolsets）** — 一个独立的部分显示内置工具集（文件操作、网页浏览等），包括它们的启用/禁用状态、设置要求以及包含的工具列表

:::warning 安全提醒
网页面板会读取和写入你的 `.env` 文件，其中包含 API 密钥和机密信息。默认情况下它绑定到 `127.0.0.1` —— 只能从本地机器访问。如果你绑定到 `0.0.0.0`，网络中的任何人都可以查看和修改你的凭据。该面板本身没有身份认证。
:::

<a id="reload-slash-command"></a>
## `/reload` 斜杠命令

该面板 PR 还为交互式 CLI 添加了一个 `/reload` 斜杠命令。在通过网页面板（或直接编辑 `.env`）更改 API 密钥后，在活跃的 CLI 会话中使用 `/reload` 即可加载更改，无需重启：

```
You → /reload
  Reloaded .env (3 var(s) updated)
```

这将把 `~/.hermes/.env` 重新读取到当前进程的环境中。当你通过面板添加了一个新的提供商密钥并希望立即使用时，这个功能非常有用。

<a id="rest-api"></a>
<a id="security"></a>
## REST API

网页面板暴露了一个 REST API，供前端使用。你也可以直接调用这些端点以实现自动化：

<a id="get-api-status"></a>
### GET /api/status

返回 Agent 版本、网关状态、平台状态以及活跃会话数。

<a id="get-api-sessions"></a>
### GET /api/sessions

返回最近 20 个会话及其元数据（模型、token 数、时间戳、预览）。

<a id="get-api-config"></a>
### GET /api/config

以 JSON 形式返回当前的 `config.yaml` 内容。

<a id="get-api-config-defaults"></a>
### GET /api/config/defaults

返回默认配置值。

<a id="get-api-config-schema"></a>
### GET /api/config/schema

返回描述每个配置字段的模式 —— 类型、描述、类别以及可选项（如果适用）。前端利用此模式为每个字段渲染正确的输入控件。

<a id="put-api-config"></a>
### PUT /api/config

保存新配置。请求体：`{"config": {...}}`。

<a id="get-api-env"></a>
### GET /api/env

返回所有已知的环境变量及其设置/未设置状态、脱敏后的值、描述和类别。

<a id="put-api-env"></a>
### PUT /api/env

设置一个环境变量。请求体：`{"key": "VAR_NAME", "value": "secret"}`。

<a id="delete-api-env"></a>
### DELETE /api/env

移除一个环境变量。请求体：`{"key": "VAR_NAME"}`。

<a id="get-api-sessions-sessionid"></a>
### GET /api/sessions/\{session_id\}

返回单个会话的元数据。

<a id="get-api-sessions-sessionid-messages"></a>
### GET /api/sessions/\{session_id\}/messages

返回一个会话的完整消息历史，包括工具调用和时间戳。

<a id="get-api-sessions-search"></a>
### GET /api/sessions/search

对消息内容进行全文搜索。查询参数：`q`。返回匹配的会话 ID 以及高亮的片段。

<a id="delete-api-sessions-sessionid"></a>
### DELETE /api/sessions/\{session_id\}

删除一个会话及其消息历史。

<a id="get-api-logs"></a>
### GET /api/logs

返回日志行。查询参数：`file` (agent/errors/gateway)、`lines` (数量)、`level`、`component`。

<a id="get-api-analytics-usage"></a>
### GET /api/analytics/usage
返回 token 用量、费用和会话分析。查询参数：`days`（默认 30）。响应包含每日细分和按模型汇总的数据。

<a id="get-api-cron-jobs"></a>
### GET /api/cron/jobs

返回所有已配置的 cron 任务及其状态、调度计划和运行历史。

<a id="post-api-cron-jobs"></a>
### POST /api/cron/jobs

创建新的 cron 任务。请求体：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

<a id="post-api-cron-jobs-jobid-pause"></a>
### POST /api/cron/jobs/\{job_id\}/pause

暂停一个 cron 任务。

<a id="post-api-cron-jobs-jobid-resume"></a>
### POST /api/cron/jobs/\{job_id\}/resume

恢复一个已暂停的 cron 任务。

<a id="post-api-cron-jobs-jobid-trigger"></a>
### POST /api/cron/jobs/\{job_id\}/trigger

立即触发一个 cron 任务（不按原调度计划执行）。

<a id="delete-api-cron-jobs-jobid"></a>
### DELETE /api/cron/jobs/\{job_id\}

删除一个 cron 任务。

<a id="get-api-skills"></a>
### GET /api/skills

返回所有技能及其名称、描述、分类和启用状态。

<a id="put-api-skills-toggle"></a>
### PUT /api/skills/toggle

启用或禁用某个技能。请求体：`{"name": "skill-name", "enabled": true}`。

<a id="get-api-tools-toolsets"></a>
### GET /api/tools/toolsets

返回所有工具集及其标签、描述、工具列表以及激活/配置状态。

<a id="cors"></a>
## CORS

Web 服务器将 CORS 限制为仅允许 localhost 来源：

- `http://localhost:9119` / `http://127.0.0.1:9119`（生产环境）
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173`（Vite 开发服务器）

如果你在自定义端口上运行服务器，该来源会自动添加。

<a id="development"></a>
## 开发

如果你正在为 Web 仪表盘前端做贡献：

```bash
# 终端 1：启动后端 API
hermes dashboard --no-open

# 终端 2：启动带 HMR 的 Vite 开发服务器
cd web/
npm install
npm run dev
```

位于 `http://localhost:5173` 的 Vite 开发服务器会将 `/api` 请求代理到 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端使用 React 19、TypeScript、Tailwind CSS v4 和 shadcn/ui 风格组件构建。生产构建输出到 `hermes_cli/web_dist/`，FastAPI 服务器将其作为静态 SPA 提供服务。

<a id="automatic-build-on-update"></a>
## 更新时自动构建

当你运行 `hermes update` 时，如果系统中有 `npm`，Web 前端会自动重新构建。这可以保持仪表盘与代码更新同步。如果没有安装 `npm`，更新会跳过前端构建，`hermes dashboard` 会在首次启动时构建它。

<a id="themes-plugins"></a>
## 主题与插件

仪表盘内置了六个主题，并且可以通过用户自定义主题、插件标签页和后端 API 路由进行扩展——全部即插即用，无需克隆仓库。

**实时切换主题**：点击顶部栏中语言切换器旁边的调色板图标。选择会持久化到 `config.yaml` 的 `dashboard.theme` 字段，并在页面加载时恢复。

内置主题：

| 主题 | 特点 |
|-------|-----------|
| **Hermes Teal**（`default`） | 深青绿 + 奶油色，系统字体，舒适的间距 |
| **Hermes Teal（大号）**（`default-large`） | 与默认相同，但文字 18px，间距更宽松 |
| **Midnight**（`midnight`） | 深蓝紫色，Inter + JetBrains Mono |
| **Ember**（`ember`） | 暖红 + 古铜色，Spectral 衬线体 + IBM Plex Mono |
| **Mono**（`mono`） | 灰度，IBM Plex，紧凑 |
| **Cyberpunk**（`cyberpunk`） | 黑色背景上的霓虹绿，Share Tech Mono |
| **Rosé**（`rose`） | 粉色 + 象牙色，Fraunces 衬线体，宽敞 |
要构建你自己的主题、添加插件选项卡、注入到 Shell 插槽中或暴露插件专属的 REST 端点，请参阅 **[扩展仪表盘](./extending-the-dashboard)**——完整指南包含：

- 主题 YAML 结构 —— 调色板、排版、布局、资源、组件样式、颜色覆盖、自定义 CSS
- 布局变体 —— `standard`、`cockpit`、`tiled`
- 插件清单、SDK、Shell 插槽、页面级插槽（将小部件注入内置页面而不覆盖它们）、后端 FastAPI 路由
- 一个完整的主题+插件组合演练（Strike Freedom cockpit 演示）
- 发现、重载与故障排除
