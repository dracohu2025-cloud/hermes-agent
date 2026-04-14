---
sidebar_position: 15
title: "Web 仪表板"
description: "基于浏览器的仪表板，用于管理配置、API 密钥、会话、日志、分析、定时任务和技能"
---

# Web 仪表板

Web 仪表板是一个基于浏览器的用户界面，用于管理你的 Hermes Agent 安装。无需编辑 YAML 文件或运行 CLI 命令，你就可以通过一个简洁的 Web 界面来配置设置、管理 API 密钥和监控会话。

## 快速开始

```bash
hermes dashboard
```

这会启动一个本地 Web 服务器，并在你的浏览器中打开 `http://127.0.0.1:9119`。仪表板完全在你的机器上运行 —— 数据不会离开本地主机。

### 选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |

```bash
# 自定义端口
hermes dashboard --port 8080

# 绑定到所有网络接口（在共享网络上使用需谨慎）
hermes dashboard --host 0.0.0.0

# 启动时不打开浏览器
hermes dashboard --no-open
```

## 前提条件

Web 仪表板需要 FastAPI 和 Uvicorn。使用以下命令安装：

```bash
pip install hermes-agent[web]
```

如果你使用 `pip install hermes-agent[all]` 安装，则 Web 依赖项已包含在内。

当你运行 `hermes dashboard` 但缺少依赖项时，它会告诉你需要安装什么。如果前端尚未构建且 `npm` 可用，它会在首次启动时自动构建。

## 页面

### 状态

首页显示你安装的实时概览：

- **Agent 版本** 和发布日期
- **网关状态** —— 运行/停止、PID、连接的平台及其状态
- **活跃会话** —— 过去 5 分钟内活跃的会话数量
- **最近会话** —— 最近 20 个会话的列表，包含模型、消息数量、令牌使用情况以及对话预览

状态页面每 5 秒自动刷新一次。

### 配置

一个基于表单的 `config.yaml` 编辑器。所有 150 多个配置字段都从 `DEFAULT_CONFIG` 自动发现，并按选项卡分类组织：

- **model** —— 默认模型、提供商、基础 URL、推理设置
- **terminal** —— 后端（本地/docker/ssh/modal）、超时、Shell 偏好
- **display** —— 皮肤、工具进度、恢复显示、加载动画设置
- **agent** —— 最大迭代次数、网关超时、服务层级
- **delegation** —— 子 Agent 限制、推理工作量
- **memory** —— 提供商选择、上下文注入设置
- **approvals** —— 危险命令批准模式（询问/直接执行/拒绝）
- 以及更多 —— config.yaml 的每个部分都有对应的表单字段

具有已知有效值的字段（终端后端、皮肤、批准模式等）会渲染为下拉菜单。布尔值渲染为开关。其他所有内容都是文本输入框。

**操作：**

- **保存** —— 立即将更改写入 `config.yaml`
- **重置为默认值** —— 将所有字段恢复为其默认值（点击保存前不会实际保存）
- **导出** —— 将当前配置下载为 JSON 文件
- **导入** —— 上传 JSON 配置文件以替换当前值

:::tip
配置更改将在下一次 Agent 会话或网关重启时生效。Web 仪表板编辑的是与 `hermes config set` 和网关读取的同一个 `config.yaml` 文件。
:::

### API 密钥

管理存储 API 密钥和凭据的 `.env` 文件。密钥按类别分组：

- **LLM 提供商** —— OpenRouter、Anthropic、OpenAI、DeepSeek 等。
- **工具 API 密钥** —— Browserbase、Firecrawl、Tavily、ElevenLabs 等。
- **消息平台** —— Telegram、Discord、Slack 机器人令牌等。
- **Agent 设置** —— 非机密的环境变量，如 `API_SERVER_ENABLED`

每个密钥显示：
- 当前是否已设置（带有值的脱敏预览）
- 其用途的描述
- 指向提供商注册/密钥页面的链接
- 用于设置或更新值的输入字段
- 用于删除它的按钮

高级/不常用的密钥默认隐藏在切换开关后面。

### 会话

浏览和检查所有 Agent 会话。每一行显示会话标题、来源平台图标（CLI、Telegram、Discord、Slack、cron）、模型名称、消息数量、工具调用数量以及上次活跃时间。实时会话会用一个脉动徽章标记。

- **搜索** —— 使用 FTS5 在所有消息内容中进行全文搜索。结果显示高亮片段，展开时会自动滚动到第一条匹配的消息。
- **展开** —— 点击一个会话以加载其完整的消息历史记录。消息按角色（用户、助手、系统、工具）进行颜色编码，并以 Markdown 格式渲染并带有语法高亮。
- **工具调用** —— 包含工具调用的助手消息显示可折叠的块，其中包含函数名和 JSON 参数。
- **删除** —— 使用垃圾桶图标删除会话及其消息历史记录。

### 日志

查看 Agent、网关和错误日志文件，支持过滤和实时跟踪。

- **文件** —— 在 `agent`、`errors` 和 `gateway` 日志文件之间切换
- **级别** —— 按日志级别过滤：ALL、DEBUG、INFO、WARNING 或 ERROR
- **组件** —— 按来源组件过滤：all、gateway、agent、tools、cli 或 cron
- **行数** —— 选择显示多少行（50、100、200 或 500）
- **自动刷新** —— 切换实时跟踪，每 5 秒轮询新的日志行
- **颜色编码** —— 日志行按严重程度着色（错误为红色，警告为黄色，调试信息为灰色）

### 分析

根据会话历史记录计算的用量和成本分析。选择一个时间段（7、30 或 90 天）以查看：

- **摘要卡片** —— 总令牌数（输入/输出）、缓存命中率、总估计或实际成本、总会话数及日均值
- **每日令牌图表** —— 堆叠条形图，显示每天的输入和输出令牌使用情况，悬停提示显示细分和成本
- **每日细分表** —— 日期、会话数、输入令牌、输出令牌、缓存命中率和每日成本
- **按模型细分** —— 显示每个使用过的模型、其会话数、令牌使用量和估计成本的表格

### 定时任务

创建和管理按计划重复运行 Agent 提示的定时任务。

- **创建** —— 填写名称（可选）、提示、cron 表达式（例如 `0 9 * * *`）和交付目标（本地、Telegram、Discord、Slack 或电子邮件）
- **任务列表** —— 每个任务显示其名称、提示预览、计划表达式、状态徽章（启用/暂停/错误）、交付目标、上次运行时间和下次运行时间
- **暂停 / 恢复** —— 在活动状态和暂停状态之间切换任务
- **立即触发** —— 在正常计划之外立即执行任务
- **删除** —— 永久删除定时任务

### 技能

浏览、搜索和切换技能与工具集。技能从 `~/.hermes/skills/` 加载，并按类别分组。

- **搜索** —— 按名称、描述或类别过滤技能和工具集
- **类别过滤器** —— 点击类别标签以缩小列表范围（例如 MLOps、MCP、Red Teaming、AI）
- **切换** —— 使用开关启用或禁用单个技能。更改将在下一次会话时生效。
- **工具集** —— 一个单独的部分显示内置工具集（文件操作、网页浏览等），包含其活动/非活动状态、设置要求和包含的工具列表

:::warning 安全
Web 仪表板读取和写入你的 `.env` 文件，该文件包含 API 密钥和机密信息。它默认绑定到 `127.0.0.1` —— 只能从你的本地机器访问。如果你绑定到 `0.0.0.0`，你网络上的任何人都可以查看和修改你的凭据。仪表板本身没有身份验证功能。
:::

## `/reload` 斜杠命令

仪表板的 PR 还在交互式 CLI 中添加了一个 `/reload` 斜杠命令。通过 Web 仪表板（或直接编辑 `.env`）更改 API 密钥后，在活跃的 CLI 会话中使用 `/reload` 来获取更改而无需重启：

```
你 → /reload
  已重新加载 .env（更新了 3 个变量）
```

这将重新读取 `~/.hermes/.env` 到正在运行的进程环境中。当你通过仪表板添加了新的提供商密钥并希望立即使用时非常有用。

## REST API

Web 仪表板公开了一个前端使用的 REST API。你也可以直接调用这些端点以实现自动化：

### GET /api/status
返回 Agent 版本、网关状态、平台状态和活跃会话数量。

### GET /api/sessions

返回最近 20 个会话及其元数据（模型、token 数量、时间戳、预览）。

### GET /api/config

以 JSON 格式返回当前的 `config.yaml` 内容。

### GET /api/config/defaults

返回默认配置值。

### GET /api/config/schema

返回描述每个配置字段的模式 —— 类型、描述、类别以及适用的选项。前端使用此信息为每个字段渲染正确的输入控件。

### PUT /api/config

保存新配置。请求体：`{"config": {...}}`。

### GET /api/env

返回所有已知的环境变量及其设置/未设置状态、脱敏后的值、描述和类别。

### PUT /api/env

设置环境变量。请求体：`{"key": "VAR_NAME", "value": "secret"}`。

### DELETE /api/env

移除环境变量。请求体：`{"key": "VAR_NAME"}`。

### GET /api/sessions/\{session_id\}

返回单个会话的元数据。

### GET /api/sessions/\{session_id\}/messages

返回会话的完整消息历史，包括工具调用和时间戳。

### GET /api/sessions/search

跨消息内容进行全文搜索。查询参数：`q`。返回匹配的会话 ID 和高亮片段。

### DELETE /api/sessions/\{session_id\}

删除会话及其消息历史。

### GET /api/logs

返回日志行。查询参数：`file` (agent/errors/gateway), `lines` (数量), `level`, `component`。

### GET /api/analytics/usage

返回 token 使用量、成本和会话分析数据。查询参数：`days` (默认 30)。响应包含每日细分数据和按模型汇总的数据。

### GET /api/cron/jobs

返回所有已配置的 cron 作业及其状态、调度计划和运行历史。

### POST /api/cron/jobs

创建新的 cron 作业。请求体：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/\{job_id\}/pause

暂停一个 cron 作业。

### POST /api/cron/jobs/\{job_id\}/resume

恢复一个已暂停的 cron 作业。

### POST /api/cron/jobs/\{job_id\}/trigger

立即触发一个 cron 作业（不按调度计划）。

### DELETE /api/cron/jobs/\{job_id\}

删除一个 cron 作业。

### GET /api/skills

返回所有技能及其名称、描述、类别和启用状态。

### PUT /api/skills/toggle

启用或禁用一个技能。请求体：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有工具集及其标签、描述、工具列表和激活/配置状态。

## CORS

Web 服务器将 CORS 限制为仅允许 localhost 来源：

- `http://localhost:9119` / `http://127.0.0.1:9119` (生产环境)
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173` (Vite 开发服务器)

如果你在自定义端口上运行服务器，该来源会自动添加。

## 开发

如果你要为 Web 仪表盘前端做贡献：

```bash
# 终端 1：启动后端 API
hermes dashboard --no-open

# 终端 2：启动带 HMR 的 Vite 开发服务器
cd web/
npm install
npm run dev
```

位于 `http://localhost:5173` 的 Vite 开发服务器会将 `/api` 请求代理到位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端使用 React 19、TypeScript、Tailwind CSS v4 和 shadcn/ui 风格的组件构建。生产构建输出到 `hermes_cli/web_dist/` 目录，由 FastAPI 服务器作为静态单页应用 (SPA) 提供服务。

## 更新时自动构建

当你运行 `hermes update` 时，如果 `npm` 可用，Web 前端会自动重新构建。这确保了仪表盘与代码更新保持同步。如果未安装 `npm`，更新过程会跳过前端构建，`hermes dashboard` 将在首次启动时构建它。
