---
sidebar_position: 14
title: "API 服务器"
description: "将 hermes-agent 以 OpenAI 兼容 API 的形式暴露给任何前端"
---

# API 服务器 {#api-server}

API 服务器将 hermes-agent 以 OpenAI 兼容的 HTTP 端点形式暴露出来。任何支持 OpenAI 格式的前端——Open WebUI、LobeChat、LibreChat、NextChat、ChatBox 以及数百个其他应用——都可以连接到 hermes-agent 并将其用作后端。

你的 Agent 会使用其完整的工具集（终端、文件操作、网络搜索、记忆、技能）处理请求，并返回最终响应。在流式传输时，工具进度指示器会内联显示，让前端能够看到 Agent 正在做什么。

## 快速开始 {#quick-start}

### 1. 启用 API 服务器 {#1-enable-the-api-server}

在 `~/.hermes/.env` 中添加：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=change-me-local-dev
# 可选：仅当浏览器需要直接调用 Hermes 时才需要
# API_SERVER_CORS_ORIGINS=http://localhost:3000
```

### 2. 启动网关 {#2-start-the-gateway}

```bash
hermes gateway
```

你会看到：

```
[API Server] API server listening on http://127.0.0.1:8642
```

### 3. 连接前端 {#3-connect-a-frontend}

将任何兼容 OpenAI 的客户端指向 `http://localhost:8642/v1`：

```bash
# 使用 curl 测试
curl http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer change-me-local-dev" \
  -H "Content-Type: application/json" \
  -d '{"model": "hermes-agent", "messages": [{"role": "user", "content": "Hello!"}]}'
```

或者连接 Open WebUI、LobeChat 或任何其他前端——请参阅 [Open WebUI 集成指南](/user-guide/messaging/open-webui) 获取分步说明。

## 端点 {#endpoints}

### POST /v1/chat/completions {#post-v1-chat-completions}

标准的 OpenAI Chat Completions 格式。无状态——每次请求中通过 `messages` 数组包含完整的对话。

**请求：**
```json
{
  "model": "hermes-agent",
  "messages": [
    {"role": "system", "content": "你是一位 Python 专家。"},
    {"role": "user", "content": "写一个斐波那契函数"}
  ],
  "stream": false
}
```

**响应：**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "hermes-agent",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "这是一个斐波那契函数……"},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 50, "completion_tokens": 200, "total_tokens": 250}
}
```

**内联图片输入：** 用户消息可以将 `content` 作为 `text` 和 `image_url` 部分的数组发送。支持远程 `http(s)` URL 和 `data:image/...` URL：

```json
{
  "model": "hermes-agent",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "这张图片里有什么？"},
        {"type": "image_url", "image_url": {"url": "https://example.com/cat.png", "detail": "high"}}
      ]
    }
  ]
}
```

上传的文件（`file` / `input_file` / `file_id`）和非图片的 `data:` URL 会返回 `400 unsupported_content_type`。

**流式传输**（`"stream": true`）：返回服务器发送事件（SSE），包含逐 token 的响应块。对于 **Chat Completions**，流使用标准的 `chat.completion.chunk` 事件，外加 Hermes 自定义的 `hermes.tool.progress` 事件，用于工具启动的用户体验。对于 **Responses**，流使用 OpenAI Responses 事件类型，例如 `response.created`、`response.output_text.delta`、`response.output_item.added`、`response.output_item.done` 和 `response.completed`。
**流式传输中的工具进度**：
- **Chat Completions**：Hermes 会发出 `event: hermes.tool.progress` 事件，用于在工具启动时提供可见性，而不会污染已持久化的助手文本。
- **Responses**：Hermes 会在 SSE 流中发出规范原生的 `function_call` 和 `function_call_output` 输出项，因此客户端可以实时渲染结构化的工具 UI。

### POST /v1/responses {#post-v1-responses}

OpenAI Responses API 格式。通过 `previous_response_id` 支持服务端会话状态——服务器会存储完整的对话历史（包括工具调用及其结果），因此多轮对话的上下文得以保留，无需客户端自行管理。

**请求：**
```json
{
  "model": "hermes-agent",
  "input": "我的项目里有哪些文件？",
  "instructions": "你是一个有用的编程助手。",
  "store": true
}
```

**响应：**
```json
{
  "id": "resp_abc123",
  "object": "response",
  "status": "completed",
  "model": "hermes-agent",
  "output": [
    {"type": "function_call", "name": "terminal", "arguments": "{\"command\": \"ls\"}", "call_id": "call_1"},
    {"type": "function_call_output", "call_id": "call_1", "output": "README.md src/ tests/"},
    {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "你的项目里有..."}]}
  ],
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

**内联图片输入：** `input[].content` 可以包含 `input_text` 和 `input_image` 部分。远程 URL 和 `data:image/...` URL 都支持：

```json
{
  "model": "hermes-agent",
  "input": [
    {
      "role": "user",
      "content": [
        {"type": "input_text", "text": "描述一下这个截图。"},
        {"type": "input_image", "image_url": "data:image/png;base64,iVBORw0K..."}
      ]
    }
  ]
}
```

上传的文件（`input_file` / `file_id`）和非图片的 `data:` URL 会返回 `400 unsupported_content_type`。

#### 使用 previous_response_id 进行多轮对话 {#multi-turn-with-previousresponseid}

通过链式响应来保持跨轮次的完整上下文（包括工具调用）：

```json
{
  "input": "现在给我看看 README",
  "previous_response_id": "resp_abc123"
}
```

服务器会从存储的响应链中重建完整的对话——所有之前的工具调用及其结果都会被保留。链式请求还共享同一个会话，因此多轮对话在仪表盘和会话历史中会显示为单一条目。

#### 命名对话 {#named-conversations}

使用 `conversation` 参数，无需追踪响应 ID：

```json
{"input": "你好", "conversation": "my-project"}
{"input": "src/ 里有什么？", "conversation": "my-project"}
{"input": "运行测试", "conversation": "my-project"}
```

服务器会自动链接到该对话中的最新响应。类似于网关会话的 `/title` 命令。

### GET /v1/responses/\{id\} {#get-v1-responses-id}

根据 ID 检索之前存储的响应。

### DELETE /v1/responses/\{id\} {#delete-v1-responses-id}

删除一个已存储的响应。

### GET /v1/models {#get-v1-models}

将 Agent 列为一个可用的模型。公布的模型名称默认为[配置文件](/user-guide/profiles)名称（对于默认配置文件，则为 `hermes-agent`）。大多数前端在发现模型时都需要此接口。
### GET /v1/capabilities {#get-v1-capabilities}

返回 API 服务器稳定接口的机器可读描述，供外部 UI、编排器和插件桥使用。

```json
{
  "object": "hermes.api_server.capabilities",
  "platform": "hermes-agent",
  "model": "hermes-agent",
  "auth": {"type": "bearer", "required": true},
  "features": {
    "chat_completions": true,
    "responses_api": true,
    "run_submission": true,
    "run_status": true,
    "run_events_sse": true,
    "run_stop": true
  }
}
```

在集成仪表盘、浏览器 UI 或控制平面时使用此端点，以便它们能够发现当前运行的 Hermes 版本是否支持运行、流式传输、取消和会话连续性，而无需依赖私有的 Python 内部实现。

### GET /health {#get-health}

健康检查。返回 `{"status": "ok"}`。同时也可通过 **GET /v1/health** 访问，以兼容期望 `/v1/` 前缀的 OpenAI 客户端。

### GET /health/detailed {#get-health-detailed}

扩展健康检查，还会报告活跃会话、正在运行的 Agent 以及资源使用情况。适用于监控/可观测性工具。

## Runs API（流式友好替代方案） {#runs-api-streaming-friendly-alternative}

除了 `/v1/chat/completions` 和 `/v1/responses` 之外，服务器还公开了一个 **runs** API，用于长时间会话，客户端可以订阅进度事件，而无需自行管理流式传输。

### POST /v1/runs {#post-v1-runs}

创建新的 Agent 运行。返回一个 `run_id`，可用于订阅进度事件。

```json
{
  "run_id": "run_abc123",
  "status": "started"
}
```

Runs 接受简单的 `input` 字符串以及可选的 `session_id`、`instructions`、`conversation_history` 或 `previous_response_id`。当提供 `session_id` 时，Hermes 会在运行状态中显示它，以便外部 UI 可以将运行与其自己的会话 ID 关联起来。

### GET /v1/runs/\{run_id\} {#get-v1-runs-runid}

轮询当前运行状态。这对于需要状态但不想保持 SSE 连接打开的仪表盘，或者在导航后重新连接的 UI 非常有用。

```json
{
  "object": "hermes.run",
  "run_id": "run_abc123",
  "status": "completed",
  "session_id": "space-session",
  "model": "hermes-agent",
  "output": "Done.",
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

状态在终端状态（`completed`、`failed` 或 `cancelled`）后会短暂保留，以便轮询和 UI 协调。

### GET /v1/runs/\{run_id\}/events {#get-v1-runs-runid-events}

服务器推送事件流，包含运行的工具调用进度、令牌增量以及生命周期事件。专为希望在不丢失状态的情况下连接/断开的仪表盘和胖客户端设计。

### POST /v1/runs/\{run_id\}/stop {#post-v1-runs-runid-stop}

中断正在运行的 Agent 轮次。端点立即返回 `{"status": "stopping"}`，同时 Hermes 会要求活跃 Agent 在下一个安全中断点停止。

## Jobs API（后台定时任务） {#jobs-api-background-scheduled-work}

服务器公开了一个轻量级的 jobs CRUD 接口，用于从远程客户端管理定时/后台 Agent 运行。所有端点都受相同的 bearer 认证保护。

### GET /api/jobs {#get-api-jobs}
列出所有已调度的任务。

### POST /api/jobs {#post-api-jobs}

创建一个新的调度任务。请求体接受与 `hermes cron` 相同的结构——prompt、schedule、skills、provider override、delivery target。

### GET /api/jobs/\{job_id\} {#get-api-jobs-jobid}

获取单个任务的定义和上次运行状态。

### PATCH /api/jobs/\{job_id\} {#patch-api-jobs-jobid}

更新现有任务的字段（prompt、schedule 等）。支持部分更新合并。

### DELETE /api/jobs/\{job_id\} {#delete-api-jobs-jobid}

删除一个任务。同时会取消任何正在进行的运行。

### POST /api/jobs/\{job_id\}/pause {#post-api-jobs-jobid-pause}

暂停一个任务而不删除它。下次调度运行的时间戳会被挂起，直到恢复。

### POST /api/jobs/\{job_id\}/resume {#post-api-jobs-jobid-resume}

恢复之前暂停的任务。

### POST /api/jobs/\{job_id\}/run {#post-api-jobs-jobid-run}

立即触发任务运行，不受调度时间限制。

## 系统提示处理 {#system-prompt-handling}

当前端发送 `system` 消息（Chat Completions）或 `instructions` 字段（Responses API）时，hermes-agent 会将其**叠加**在核心系统提示之上。你的 Agent 会保留所有工具、记忆和技能——前端的系统提示只是添加额外指令。

这意味着你可以为每个前端定制行为，而不会丢失能力：
- Open WebUI 系统提示："你是一个 Python 专家。始终包含类型提示。"
- Agent 仍然拥有终端、文件工具、网络搜索、记忆等。

## 身份验证 {#authentication}

通过 `Authorization` 头使用 Bearer token 进行身份验证：

```
Authorization: Bearer ***
```

通过 `API_SERVER_KEY` 环境变量配置密钥。如果需要浏览器直接调用 Hermes，还需要将 `API_SERVER_CORS_ORIGINS` 设置为明确的允许列表。

:::warning 安全
API 服务器提供对 hermes-agent 工具集的完全访问权限，**包括终端命令**。当绑定到非回环地址（如 `0.0.0.0`）时，**必须**设置 `API_SERVER_KEY`。同时，保持 `API_SERVER_CORS_ORIGINS` 范围狭窄，以控制浏览器访问。

默认绑定地址（`127.0.0.1`）仅限本地使用。默认禁用浏览器访问；仅对明确信任的来源启用。
:::
<a id="security"></a>

## 配置 {#configuration}

### 环境变量 {#environment-variables}

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `API_SERVER_ENABLED` | `false` | 启用 API 服务器 |
| `API_SERVER_PORT` | `8642` | HTTP 服务器端口 |
| `API_SERVER_HOST` | `127.0.0.1` | 绑定地址（默认仅限本地） |
| `API_SERVER_KEY` | _(无)_ | 用于身份验证的 Bearer token |
| `API_SERVER_CORS_ORIGINS` | _(无)_ | 逗号分隔的允许浏览器来源 |
| `API_SERVER_MODEL_NAME` | _(配置文件名称)_ | `/v1/models` 上的模型名称。默认为配置文件名称，对于默认配置文件则为 `hermes-agent`。 |

### config.yaml {#config-yaml}

```yaml
# 暂不支持——请使用环境变量。
# config.yaml 支持将在未来版本中提供。
```

## 安全头 {#security-headers}

所有响应都包含安全头：
- `X-Content-Type-Options: nosniff` — 防止 MIME 类型嗅探
- `Referrer-Policy: no-referrer` — 防止 referrer 泄露

## CORS {#cors}

API 服务器默认**不**启用浏览器 CORS。

如需直接浏览器访问，请设置明确的允许列表：
```bash
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

启用 CORS 时：
- **预检响应** 包含 `Access-Control-Max-Age: 600`（10 分钟缓存）
- **SSE 流式响应** 包含 CORS 头，确保浏览器 EventSource 客户端正常工作
- **`Idempotency-Key`** 是允许的请求头——客户端可发送它进行去重（响应按 key 缓存 5 分钟）

大多数文档化的前端（如 Open WebUI）采用服务器到服务器连接，完全不需要 CORS。

## 兼容的前端 {#compatible-frontends}

任何支持 OpenAI API 格式的前端均可使用。已测试/文档化的集成：

| 前端 | Stars | 连接方式 |
|----------|-------|------------|
| [Open WebUI](/user-guide/messaging/open-webui) | 126k | 提供完整指南 |
| LobeChat | 73k | 自定义 provider 端点 |
| LibreChat | 34k | 在 librechat.yaml 中配置自定义端点 |
| AnythingLLM | 56k | 通用 OpenAI provider |
| NextChat | 87k | BASE_URL 环境变量 |
| ChatBox | 39k | API Host 设置 |
| Jan | 26k | 远程模型配置 |
| HF Chat-UI | 8k | OPENAI_BASE_URL |
| big-AGI | 7k | 自定义端点 |
| OpenAI Python SDK | — | `OpenAI(base_url="http://localhost:8642/v1")` |
| curl | — | 直接 HTTP 请求 |

## 使用 Profiles 的多用户设置 {#multi-user-setup-with-profiles}

要为多个用户提供各自独立的 Hermes 实例（独立的配置、记忆、技能），请使用 [profiles](/user-guide/profiles)：

```bash
# 为每个用户创建一个 profile
hermes profile create alice
hermes profile create bob

# 为每个 profile 的 API 服务器配置不同端口
hermes -p alice config set API_SERVER_ENABLED true
hermes -p alice config set API_SERVER_PORT 8643
hermes -p alice config set API_SERVER_KEY alice-secret

hermes -p bob config set API_SERVER_ENABLED true
hermes -p bob config set API_SERVER_PORT 8644
hermes -p bob config set API_SERVER_KEY bob-secret

# 启动每个 profile 的 gateway
hermes -p alice gateway &
hermes -p bob gateway &
```

每个 profile 的 API 服务器会自动将 profile 名称作为模型 ID 进行广播：

- `http://localhost:8643/v1/models` → 模型 `alice`
- `http://localhost:8644/v1/models` → 模型 `bob`

在 Open WebUI 中，将每个连接添加为独立连接。模型下拉菜单会显示 `alice` 和 `bob` 作为不同的模型，每个模型背后都是一个完全隔离的 Hermes 实例。详情请参阅 [Open WebUI 指南](/user-guide/messaging/open-webui#multi-user-setup-with-profiles)。

## 限制 {#limitations}

- **响应存储** — 存储的响应（用于 `previous_response_id`）持久化在 SQLite 中，gateway 重启后仍然存在。最多存储 100 条响应（LRU 淘汰）。
- **不支持文件上传** — `/v1/chat/completions` 和 `/v1/responses` 均支持内联图片，但通过 API 不支持上传文件（`file`、`input_file`、`file_id`）和非图片文档输入。
- **模型字段仅作展示** — 请求中的 `model` 字段会被接受，但实际使用的 LLM 模型是在服务端 config.yaml 中配置的。

## 代理模式 {#proxy-mode}

API 服务器也作为 **gateway 代理模式** 的后端。当另一个 Hermes gateway 实例配置了指向此 API 服务器的 `GATEWAY_PROXY_URL` 时，它会将所有消息转发到这里，而不是运行自己的 Agent。这实现了拆分部署——例如，一个 Docker 容器处理 Matrix E2EE，然后将消息中继到主机端的 Agent。
请参阅 [Matrix 代理模式](/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos) 了解完整设置指南。
