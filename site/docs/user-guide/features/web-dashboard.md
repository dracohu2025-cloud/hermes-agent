---
sidebar_position: 15
title: "Web 仪表盘"
description: "基于浏览器的仪表盘，用于管理配置、API 密钥、会话、日志、分析、定时任务和技能"
---

# Web 仪表盘 {#web-dashboard}

Web 仪表盘是一个基于浏览器的 UI，用于管理你的 Hermes Agent 安装。无需编辑 YAML 文件或运行 CLI 命令，你可以通过一个简洁的 Web 界面来配置设置、管理 API 密钥以及监控会话。

## 快速开始 {#quick-start}

```bash
hermes dashboard
```

这会启动一个本地 Web 服务器，并在浏览器中打开 `http://127.0.0.1:9119`。仪表盘完全在你的机器上运行——不会有任何数据离开 localhost。

### 选项 {#options}

| 标志 | 默认值 | 描述 |
|------|--------|------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--insecure` | off | 允许绑定到非 localhost 的主机（**危险**——会在网络上暴露 API 密钥；请配合防火墙和强认证使用） |
| `--tui` | off | 暴露浏览器内的聊天标签页（通过 PTY/WebSocket 嵌入的 `hermes --tui`）。也可以设置 `HERMES_DASHBOARD_TUI=1`。 |

```bash
# 自定义端口
hermes dashboard --port 8080

# 绑定到所有接口（在共享网络上请谨慎使用）
hermes dashboard --host 0.0.0.0

# 启动时不打开浏览器
hermes dashboard --no-open
```

## 前提条件 {#prerequisites}

默认的 `hermes-agent` 安装不包含 HTTP 栈或 PTY 辅助程序——这些是可选的附加组件。**Web 仪表盘**需要 FastAPI 和 Uvicorn（`web` 附加组件）。**聊天**标签页还需要 `ptyprocess` 来在伪终端后面生成嵌入的 TUI（POSIX 上的 `pty` 附加组件）。同时安装两者：

```bash
pip install 'hermes-agent[web,pty]'
```

`web` 附加组件会拉取 FastAPI/Uvicorn；`pty` 会拉取 `ptyprocess`（POSIX）或 `pywinpty`（原生 Windows——注意嵌入的 TUI 本身仍然需要 WSL）。`pip install hermes-agent[all]` 包含这两个附加组件，如果你还需要消息/语音等功能，这是最简单的路径。

当你运行 `hermes dashboard` 但缺少依赖时，它会告诉你需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

## 页面 {#pages}

### 状态 {#status}

首页显示你的安装的实时概览：

- **Agent 版本**和发布日期
- **网关状态**——运行/停止、PID、已连接的平台及其状态
- **活跃会话**——过去 5 分钟内活跃的会话数
- **最近会话**——最近 20 个会话的列表，包含模型、消息数、Token 用量以及对话预览

状态页面每 5 秒自动刷新一次。

### 聊天 {#chat}

**聊天**标签页将完整的 Hermes TUI（与 `hermes --tui` 获得的界面相同）直接嵌入到浏览器中。你在终端 TUI 中能做的一切——斜杠命令、模型选择器、工具调用卡片、Markdown 流式输出、clarify/sudo/approval 提示、皮肤主题——在这里都能以相同的方式工作，因为仪表盘正在运行真正的 TUI 二进制文件，并通过 [xterm.js](https://xtermjs.org/) 及其 WebGL 渲染器渲染其 ANSI 输出，实现像素级完美的单元格布局。

**工作原理：**

- `/api/pty` 打开一个经过仪表盘会话 Token 认证的 WebSocket
- 服务器在 POSIX 伪终端后面生成 `hermes --tui`
- 按键传输到 PTY；ANSI 输出流回浏览器
- xterm.js 的 WebGL 渲染器将每个单元格绘制到整数像素网格上；鼠标跟踪（SGR 1006）、宽字符（Unicode 11）和制表符绘制字形都能原生渲染
- 调整浏览器窗口大小会通过 `@xterm/addon-fit` 插件调整 TUI 的大小
**恢复已有会话：** 在 **Sessions** 标签页中，点击任意会话旁边的播放图标 (▶)。这会跳转到 `/chat?resume=&lt;id&gt;`，并使用 `--resume` 启动 TUI，加载完整历史记录。

**前置条件：**

- Node.js（与 `hermes --tui` 要求相同；TUI 包在首次启动时构建）
- `ptyprocess` — 通过 `pty` 附加组件安装（`pip install 'hermes-agent[web,pty]'`，或使用 `[all]` 同时安装两者）
- POSIX 内核（Linux、macOS 或 WSL）。原生 Windows Python 不受支持 — 请使用 WSL。

关闭浏览器标签页后，PTY 会在服务器端被干净地回收。重新打开时会生成一个新的会话。

### 配置 {#config}

一个基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都会从 `DEFAULT_CONFIG` 自动发现，并按标签页分类组织：

- **model** — 默认模型、提供商、基础 URL、推理设置
- **terminal** — 后端（local/docker/ssh/modal）、超时时间、Shell 偏好
- **display** — 皮肤、工具进度、恢复显示、旋转动画设置
- **agent** — 最大迭代次数、网关超时、服务层级
- **delegation** — 子 Agent 限制、推理努力程度
- **memory** — 提供商选择、上下文注入设置
- **approvals** — 危险命令审批模式（ask/yolo/deny）
- 更多 — config.yaml 的每个部分都有对应的表单字段

已知有效值的字段（终端后端、皮肤、审批模式等）会渲染为下拉菜单。布尔值渲染为开关。其他所有字段都是文本输入框。

**操作：**

- **Save** — 立即将更改写入 `config.yaml`
- **Reset to defaults** — 将所有字段恢复为默认值（直到点击 Save 才会保存）
- **Export** — 将当前配置下载为 JSON
- **Import** — 上传一个 JSON 配置文件以替换当前值

:::tip
配置更改会在下一次 Agent 会话或网关重启时生效。Web 仪表盘编辑的是与 `hermes config set` 和网关读取的同一个 `config.yaml` 文件。
:::

### API 密钥 {#api-keys}

管理存储 API 密钥和凭据的 `.env` 文件。密钥按类别分组：

- **LLM 提供商** — OpenRouter、Anthropic、OpenAI、DeepSeek 等
- **工具 API 密钥** — Browserbase、Firecrawl、Tavily、ElevenLabs 等
- **消息平台** — Telegram、Discord、Slack 机器人令牌等
- **Agent 设置** — 非机密的环境变量，如 `API_SERVER_ENABLED`

每个密钥显示：
- 当前是否已设置（带遮盖预览的值）
- 用途说明
- 指向提供商注册/密钥页面的链接
- 用于设置或更新值的输入框
- 用于删除的按钮

高级/不常用的密钥默认隐藏，可通过开关显示。

### 会话 {#sessions}

浏览并检查所有 Agent 会话。每一行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、cron）、模型名称、消息数量、工具调用次数以及上次活跃时间。活跃会话会带有脉冲徽章标记。

- **搜索** — 使用 FTS5 对所有消息内容进行全文搜索。结果会显示高亮片段，展开时自动滚动到第一条匹配消息。
- **展开** — 点击会话以加载其完整消息历史。消息按角色（用户、助手、系统、工具）进行颜色编码，并渲染为带语法高亮的 Markdown。
- **工具调用** — 包含工具调用的助手消息会显示可折叠的区块，其中包含函数名称和 JSON 参数。
- **删除** — 使用垃圾桶图标删除会话及其消息历史。
### 日志 {#logs}

查看 Agent、网关和错误日志文件，支持过滤和实时追踪。

- **文件** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** — 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** — 按来源组件过滤：全部、gateway、agent、tools、cli 或 cron
- **行数** — 选择显示多少行（50、100、200 或 500）
- **自动刷新** — 开启实时追踪，每 5 秒轮询一次新日志行
- **颜色标记** — 日志行按严重程度着色（红色表示错误，黄色表示警告，灰色表示调试）

### 分析 {#analytics}

基于会话历史计算的使用量和成本分析。选择一个时间段（7、30 或 90 天）即可查看：

- **摘要卡片** — 总 token 数（输入/输出）、缓存命中率、总预估或实际成本、总会话数及日均值
- **每日 token 图表** — 堆叠柱状图，显示每天的输入和输出 token 使用量，悬停时显示详细分解和成本
- **每日明细表** — 每天对应的日期、会话数、输入 token、输出 token、缓存命中率和成本
- **按模型分解** — 表格显示每个使用的模型、其会话数、token 使用量和预估成本

### 定时任务 {#cron}

创建和管理按计划重复运行 Agent 提示词的定时 cron 任务。

- **创建** — 填写名称（可选）、提示词、cron 表达式（例如 `0 9 * * *`）和投递目标（本地、Telegram、Discord、Slack 或邮件）
- **任务列表** — 每个任务显示其名称、提示词预览、调度表达式、状态徽章（已启用/已暂停/错误）、投递目标、上次运行时间和下次运行时间
- **暂停 / 恢复** — 在活动状态和暂停状态之间切换任务
- **立即触发** — 在正常调度之外立即执行一个任务
- **删除** — 永久移除一个 cron 任务

### 技能 {#skills}

浏览、搜索并启用/禁用技能和工具集。技能从 `~/.hermes/skills/` 加载，并按类别分组。

- **搜索** — 按名称、描述或类别过滤技能和工具集
- **类别筛选** — 点击类别标签以缩小列表范围（例如 MLOps、MCP、红队测试、AI）
- **开关** — 使用开关启用或禁用单个技能。更改将在下一次会话生效。
- **工具集** — 一个独立区域显示内置工具集（文件操作、网页浏览等），包含其启用/停用状态、设置要求以及包含的工具列表

:::warning 安全警告
<a id="security"></a>
Web 仪表盘会读写你的 `.env` 文件，其中包含 API 密钥和机密信息。默认情况下，它绑定到 `127.0.0.1` —— 仅能从你的本地机器访问。如果你绑定到 `0.0.0.0`，你网络上的任何人都可以查看和修改你的凭据。该仪表盘本身没有身份验证机制。
:::

## `/reload` 斜杠命令 {#reload-slash-command}

仪表盘 PR 还在交互式 CLI 中添加了一个 `/reload` 斜杠命令。通过 Web 仪表盘（或直接编辑 `.env`）更改 API 密钥后，在活动的 CLI 会话中使用 `/reload` 即可应用更改，无需重启：
```
You → /reload
  Reloaded .env (3 var(s) updated)
```

这会重新读取 `~/.hermes/.env` 并注入到当前运行进程的环境中。当你通过仪表盘添加了新的提供商密钥并希望立即使用时，这个功能非常有用。

## REST API {#rest-api}

Web 仪表盘暴露了一套 REST API，供前端使用。你也可以直接调用这些端点来实现自动化：

### GET /api/status {#get-api-status}

返回 Agent 版本、网关状态、平台状态以及活跃会话数量。

### GET /api/sessions {#get-api-sessions}

返回最近 20 个会话及其元数据（模型、Token 数量、时间戳、预览）。

### GET /api/config {#get-api-config}

以 JSON 格式返回当前 `config.yaml` 的内容。

### GET /api/config/defaults {#get-api-config-defaults}

返回默认配置值。

### GET /api/config/schema {#get-api-config-schema}

返回描述每个配置字段的 schema —— 包括类型、描述、类别以及可用的选择选项。前端利用此信息为每个字段渲染正确的输入控件。

### PUT /api/config {#put-api-config}

保存新配置。请求体：`{"config": {...}}`。

### GET /api/env {#get-api-env}

返回所有已知的环境变量及其设置/未设置状态、脱敏后的值、描述和类别。

### PUT /api/env {#put-api-env}

设置一个环境变量。请求体：`{"key": "VAR_NAME", "value": "secret"}`。

### DELETE /api/env {#delete-api-env}

删除一个环境变量。请求体：`{"key": "VAR_NAME"}`。

### GET /api/sessions/\{session_id\} {#get-api-sessions-sessionid}

返回单个会话的元数据。

### GET /api/sessions/\{session_id\}/messages {#get-api-sessions-sessionid-messages}

返回会话的完整消息历史，包括工具调用和时间戳。

### GET /api/sessions/search {#get-api-sessions-search}

对消息内容进行全文搜索。查询参数：`q`。返回匹配的会话 ID 及高亮片段。

### DELETE /api/sessions/\{session_id\} {#delete-api-sessions-sessionid}

删除一个会话及其消息历史。

### GET /api/logs {#get-api-logs}

返回日志行。查询参数：`file`（agent/errors/gateway）、`lines`（数量）、`level`、`component`。

### GET /api/analytics/usage {#get-api-analytics-usage}

返回 Token 用量、成本及会话分析。查询参数：`days`（默认 30 天）。响应包含每日细分和按模型汇总的数据。

### GET /api/cron/jobs {#get-api-cron-jobs}

返回所有已配置的定时任务及其状态、调度计划和运行历史。

### POST /api/cron/jobs {#post-api-cron-jobs}

创建一个新的定时任务。请求体：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/\{job_id\}/pause {#post-api-cron-jobs-jobid-pause}

暂停一个定时任务。

### POST /api/cron/jobs/\{job_id\}/resume {#post-api-cron-jobs-jobid-resume}

恢复一个已暂停的定时任务。

### POST /api/cron/jobs/\{job_id\}/trigger {#post-api-cron-jobs-jobid-trigger}

立即触发一个定时任务（不按原计划执行）。

### DELETE /api/cron/jobs/\{job_id\} {#delete-api-cron-jobs-jobid}

删除一个定时任务。

### GET /api/skills {#get-api-skills}

返回所有技能及其名称、描述、类别和启用状态。

### PUT /api/skills/toggle {#put-api-skills-toggle}

启用或禁用某个技能。请求体：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets {#get-api-tools-toolsets}

返回所有工具集及其标签、描述、工具列表以及活动/配置状态。

## CORS {#cors}

Web 服务器将 CORS 限制为仅允许 localhost 来源：
- `http://localhost:9119` / `http://127.0.0.1:9119`（生产环境）
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173`（Vite 开发服务器）

如果你在自定义端口上运行服务器，该源地址会自动添加。

## 开发 {#development}

如果你正在为 Web Dashboard 前端做贡献：

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

## 更新时自动构建 {#automatic-build-on-update}

当你运行 `hermes update` 时，如果 `npm` 可用，Web 前端会自动重新构建。这使 Dashboard 与代码更新保持同步。如果未安装 `npm`，更新会跳过前端构建，`hermes dashboard` 会在首次启动时构建它。

## 主题与插件 {#themes-plugins}

Dashboard 内置了六个主题，并且可以通过用户自定义主题、插件标签页和后端 API 路由进行扩展——全部即插即用，无需克隆仓库。

**实时切换主题**：点击顶部栏中语言切换器旁边的调色板图标。选择会持久化到 `config.yaml` 的 `dashboard.theme` 下，并在页面加载时恢复。

内置主题：

| 主题 | 特点 |
|-------|-----------|
| **Hermes Teal**（`default`） | 深青色 + 奶油色，系统字体，舒适的间距 |
| **Midnight**（`midnight`） | 深蓝紫色，Inter + JetBrains Mono |
| **Ember**（`ember`） | 暖红 + 古铜色，Spectral 衬线体 + IBM Plex Mono |
| **Mono**（`mono`） | 灰度，IBM Plex，紧凑 |
| **Cyberpunk**（`cyberpunk`） | 黑色背景上的霓虹绿，Share Tech Mono |
| **Rosé**（`rose`） | 粉色 + 象牙白，Fraunces 衬线体，宽敞 |

要构建自己的主题、添加插件标签页、注入到 Shell 插槽或暴露插件特定的 REST 端点，请参阅 **[扩展 Dashboard](./extending-the-dashboard)**——完整指南涵盖：

- 主题 YAML 模式——调色板、排版、布局、资源、组件样式、颜色覆盖、自定义 CSS
- 布局变体——`standard`、`cockpit`、`tiled`
- 插件清单、SDK、Shell 插槽、页面级插槽（在不覆盖内置页面的情况下向内置页面注入小部件）、后端 FastAPI 路由
- 一个完整的主题加插件组合演练（Strike Freedom 驾驶舱演示）
- 发现、重新加载和故障排除
