---
sidebar_position: 14
title: "API 服务器"
description: "将 Hermes Agent 以 OpenAI 兼容 API 的形式暴露给任何前端"
---

<a id="api-server"></a>
# API 服务器

API 服务器将 Hermes Agent 以 OpenAI 兼容的 HTTP 端点形式暴露出来。任何支持 OpenAI 格式的前端——Open WebUI、LobeChat、LibreChat、NextChat、ChatBox 以及数百个其他应用——都可以连接到 Hermes Agent 并将其用作后端。

你的 Agent 会使用其完整的工具集（终端、文件操作、网络搜索、记忆、技能）来处理请求，并返回最终响应。在流式传输时，工具进度指示器会内联显示，让前端能够看到 Agent 正在做什么。

<a id="quick-start"></a>
## 快速开始

<a id="1-enable-the-api-server"></a>
### 1. 启用 API 服务器

在 `~/.hermes/.env` 中添加：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=change-me-local-dev
# 可选：仅当浏览器需要直接调用 Hermes 时才需要
# API_SERVER_CORS_ORIGINS=http://localhost:3000
```

<a id="2-start-the-gateway"></a>
### 2. 启动网关

```bash
hermes gateway
```

你会看到：

```
[API Server] API server listening on http://127.0.0.1:8642
```

<a id="3-connect-a-frontend"></a>
### 3. 连接前端

将任何兼容 OpenAI 的客户端指向 `http://localhost:8642/v1`：

```bash
# 使用 curl 测试
curl http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer change-me-local-dev" \
  -H "Content-Type: application/json" \
  -d '{"model": "hermes-agent", "messages": [{"role": "user", "content": "Hello!"}]}'
```

或者连接 Open WebUI、LobeChat 或任何其他前端——请参阅 [Open WebUI 集成指南](/user-guide/messaging/open-webui) 获取分步说明。

<a id="endpoints"></a>
## 端点

<a id="post-v1-chat-completions"></a>
### POST /v1/chat/completions

标准的 OpenAI Chat Completions 格式。无状态——完整的对话通过 `messages` 数组包含在每个请求中。

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
    "message": {"role": "assistant", "content": "这是一个斐波那契函数..."},
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

**流式传输**（`"stream": true`）：返回服务器发送事件（SSE），包含逐 token 的响应块。对于 **Chat Completions**，流使用标准的 `chat.completion.chunk` 事件以及 Hermes 自定义的 `hermes.tool.progress` 事件，用于工具启动的用户体验。对于 **Responses**，流使用 OpenAI Responses 事件类型，例如 `response.created`、`response.output_text.delta`、`response.output_item.added`、`response.output_item.done` 和 `response.completed`。
**流式工具进度**：
- **聊天补全（Chat Completions）**：Hermes 发送 `event: hermes.tool.progress`，用于显示工具启动状态，而不会污染已持久的助手文本。
- **响应（Responses）**：Hermes 在 SSE 流中发送符合规范的原生 `function_call` 和 `function_call_output` 输出项，使客户端能够实时渲染结构化的工具界面。

<a id="post-v1-responses"></a>
### POST /v1/responses

OpenAI Responses API 格式。通过 `previous_response_id` 支持服务端会话状态——服务端存储完整的对话历史（包括工具调用及其结果），因此无需客户端管理即可保持多轮对话的上下文。

**请求：**
```json
{
  "model": "hermes-agent",
  "input": "What files are in my project?",
  "instructions": "You are a helpful coding assistant.",
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
    {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Your project has..."}]}
  ],
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

**内联图片输入：** `input[].content` 可以包含 `input_text` 和 `input_image` 部分。远程 URL 和 `data:image/...` URL 均受支持：

```json
{
  "model": "hermes-agent",
  "input": [
    {
      "role": "user",
      "content": [
        {"type": "input_text", "text": "Describe this screenshot."},
        {"type": "input_image", "image_url": "data:image/png;base64,iVBORw0K..."}
      ]
    }
  ]
}
```

上传的文件（`input_file` / `file_id`）和非图片的 `data:` URL 会返回 `400 unsupported_content_type`。

<a id="multi-turn-with-previousresponseid"></a>
#### 通过 previous_response_id 实现多轮对话

通过链式响应来保持跨轮次的完整上下文（包括工具调用）：

```json
{
  "input": "Now show me the README",
  "previous_response_id": "resp_abc123"
}
```

服务端会从已存储的响应链中重建完整的对话——所有之前的工具调用及其结果都会被保留。链式请求还共享同一个会话，因此多轮对话在仪表盘和会话历史中会显示为单个条目。

<a id="named-conversations"></a>
#### 命名对话

使用 `conversation` 参数代替追踪响应 ID：

```json
{"input": "Hello", "conversation": "my-project"}
{"input": "What's in src/?", "conversation": "my-project"}
{"input": "Run the tests", "conversation": "my-project"}
```

服务端会自动链接到该对话中的最新响应。类似于网关会话的 `/title` 命令。

<a id="get-v1-responses-id"></a>
### GET /v1/responses/\{id\}

根据 ID 获取之前存储的响应。

<a id="delete-v1-responses-id"></a>
### DELETE /v1/responses/\{id\}

删除一个已存储的响应。

<a id="get-v1-models"></a>
### GET /v1/models

将 Agent 列为一个可用的模型。公布的模型名称默认为[配置文件](/user-guide/profiles)名称（对于默认配置文件，则为 `hermes-agent`）。大多数前端在发现模型时都需要这个接口。
<a id="get-v1-capabilities"></a>
### GET /v1/capabilities

返回对外部 UI、编排器和插件桥可读的 API 服务器稳定接口描述。

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

集成仪表盘、浏览器 UI 或控制平面时，使用此端点让它们能够发现当前运行的 Hermes 版本是否支持 runs、流式传输、取消和会话连续性，而无需依赖私有 Python 内部逻辑。

<a id="get-health"></a>
### GET /health

健康检查。返回 `{"status": "ok"}`。对于期望 `/v1` 前缀的 OpenAI 兼容客户端，也可以通过 **GET /v1/health** 访问。

<a id="get-health-detailed"></a>
### GET /health/detailed

扩展健康检查，额外报告活跃会话、正在运行的 Agent 和资源使用情况。适用于监控/可观测性工具。

<a id="runs-api-streaming-friendly-alternative"></a>
## Runs API（流式友好的替代方案）

除了 `/v1/chat/completions` 和 `/v1/responses` 之外，服务器还公开了一个 **runs** API，用于长时间会话，客户端可以订阅进度事件，而无需自行管理流式传输。

<a id="post-v1-runs"></a>
### POST /v1/runs

创建新的 Agent 运行。返回一个 `run_id`，可用于订阅进度事件。

```json
{
  "run_id": "run_abc123",
  "status": "started"
}
```

Runs 接受简单的 `input` 字符串，以及可选的 `session_id`、`instructions`、`conversation_history` 或 `previous_response_id`。当提供 `session_id` 时，Hermes 会在运行状态中显示它，以便外部 UI 可以将 runs 与其自己的会话 ID 关联起来。

<a id="get-v1-runs-runid"></a>
### GET /v1/runs/\{run_id\}

轮询当前运行状态。这对于不需要保持 SSE 连接即可获取状态的仪表盘，或在导航后重新连接的 UI 非常有用。

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

终端状态（`completed`、`failed` 或 `cancelled`）后的状态会短暂保留，以便轮询和 UI 协调。

<a id="get-v1-runs-runid-events"></a>
### GET /v1/runs/\{run_id\}/events

服务端推送事件（SSE）流，包含运行的 tool-call 进度、token 增量和生命周期事件。适用于希望在不丢失状态的情况下附加/分离的仪表盘和重型客户端。

<a id="post-v1-runs-runid-stop"></a>
### POST /v1/runs/\{run_id\}/stop

中断正在运行的 Agent 回合。该端点会立即返回 `{"status": "stopping"}`，同时 Hermes 会要求活跃的 Agent 在下一个安全中断点停止。

<a id="jobs-api-background-scheduled-work"></a>
## Jobs API（后台定时任务）

服务器公开了一个轻量级的 jobs CRUD 接口，用于从远程客户端管理定时/后台 Agent 运行。所有端点都受相同的 bearer 令牌认证保护。

<a id="get-api-jobs"></a>
### GET /api/jobs
列出所有预定任务。

<a id="post-api-jobs"></a>
### POST /api/jobs

创建一个新的定时任务。请求体结构与 `hermes cron` 相同——prompt、schedule、skills、provider override、delivery target。

<a id="get-api-jobs-jobid"></a>
### GET /api/jobs/\{job_id\}

获取单个任务的定义及其最近一次运行的狀態。

<a id="patch-api-jobs-jobid"></a>
### PATCH /api/jobs/\{job_id\}

更新现有任务的字段（如 prompt、schedule 等）。部分更新会自动合并。

<a id="delete-api-jobs-jobid"></a>
### DELETE /api/jobs/\{job_id\}

删除一个任务。同时会取消任何正在进行的运行。

<a id="post-api-jobs-jobid-pause"></a>
### POST /api/jobs/\{job_id\}/pause

暂停一个任务而不删除它。下一次计划运行的时间戳将被挂起，直到恢复。

<a id="post-api-jobs-jobid-resume"></a>
### POST /api/jobs/\{job_id\}/resume

恢复一个之前暂停的任务。

<a id="post-api-jobs-jobid-run"></a>
### POST /api/jobs/\{job_id\}/run

立即触发任务运行，不受计划影响。

<a id="system-prompt-handling"></a>
## 系统提示处理

当前端发送 `system` 消息（Chat Completions）或 `instructions` 字段（Responses API）时，hermes-agent **在其核心系统提示之上叠加** 这些内容。你的 Agent 保留所有工具、记忆和技能——前端的系统提示只添加额外指令。

这意味着你可以为每个前端定制行为，而不丢失能力：
- Open WebUI 系统提示："你是 Python 专家。始终包含类型注解。"
- Agent 仍然拥有终端、文件工具、网络搜索、记忆等功能。

<a id="authentication"></a>
## 身份认证

通过 `Authorization` 头进行 Bearer token 认证：

```
Authorization: Bearer ***
```

通过 `API_SERVER_KEY` 环境变量配置密钥。如果需要浏览器直接调用 Hermes，还要将 `API_SERVER_CORS_ORIGINS` 设置为显式允许列表。

:::warning 安全
API 服务器提供对 hermes-agent 工具集的完全访问权限，**包括终端命令**。当绑定到非回环地址（如 `0.0.0.0`）时，**必须**设置 `API_SERVER_KEY`。同时保持 `API_SERVER_CORS_ORIGINS` 范围狭窄，以控制浏览器访问。

默认绑定地址（`127.0.0.1`）仅用于本地使用。浏览器访问默认禁用；仅在明确的可信来源下启用。
:::
<a id="security"></a>

<a id="configuration"></a>
## 配置

<a id="environment-variables"></a>
### 环境变量

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `API_SERVER_ENABLED` | `false` | 启用 API 服务器 |
| `API_SERVER_PORT` | `8642` | HTTP 服务器端口 |
| `API_SERVER_HOST` | `127.0.0.1` | 绑定地址（默认仅本地） |
| `API_SERVER_KEY` | _(无)_ | 用于认证的 Bearer token |
| `API_SERVER_CORS_ORIGINS` | _(无)_ | 逗号分隔的允许浏览器来源 |
| `API_SERVER_MODEL_NAME` | _(配置文件名称)_ | `/v1/models` 上的模型名称。默认为配置文件名称，或使用默认配置文件时为 `hermes-agent`。 |

<a id="config-yaml"></a>
### config.yaml

```yaml
# 暂不支持——请使用环境变量。
# config.yaml 支持将在未来版本中提供。
```

<a id="security-headers"></a>
## 安全头部

所有响应包含安全头部：
- `X-Content-Type-Options: nosniff` — 防止 MIME 类型嗅探
- `Referrer-Policy: no-referrer` — 防止 Referrer 泄露

<a id="cors"></a>
## CORS

API 服务器**默认不启用**浏览器 CORS。

如需直接浏览器访问，请设置显式允许列表：
```bash
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

启用 CORS 时：
- **预检响应** 包含 `Access-Control-Max-Age: 600`（10 分钟缓存）
- **SSE 流式响应** 包含 CORS 头部，确保浏览器 EventSource 客户端正常工作
- **`Idempotency-Key`** 是一个允许的请求头——客户端可以发送它来实现去重（响应按 key 缓存 5 分钟）

大多数文档中提到的前端（如 Open WebUI）是服务器到服务器连接，完全不需要 CORS。

<a id="compatible-frontends"></a>
## 兼容的前端

任何支持 OpenAI API 格式的前端都能工作。已测试/有文档的集成方式：

| 前端 | Stars | 连接方式 |
|----------|-------|------------|
| [Open WebUI](/user-guide/messaging/open-webui) | 126k | 提供完整指南 |
| LobeChat | 73k | 自定义 provider 端点 |
| LibreChat | 34k | 在 librechat.yaml 中自定义端点 |
| AnythingLLM | 56k | 通用 OpenAI provider |
| NextChat | 87k | BASE_URL 环境变量 |
| ChatBox | 39k | API 主机设置 |
| Jan | 26k | 远程模型配置 |
| HF Chat-UI | 8k | OPENAI_BASE_URL |
| big-AGI | 7k | 自定义端点 |
| OpenAI Python SDK | — | `OpenAI(base_url="http://localhost:8642/v1")` |
| curl | — | 直接 HTTP 请求 |

<a id="multi-user-setup-with-profiles"></a>
## 使用 Profile 的多用户设置

要为多个用户提供各自隔离的 Hermes 实例（独立的配置、记忆、技能），请使用 [profiles](/user-guide/profiles)：

```bash
# 为每个用户创建一个 profile
hermes profile create alice
hermes profile create bob

# 在每个 profile 的不同端口上配置 API 服务器。API_SERVER_* 是环境变量
# （不是 config.yaml 的键），因此需要将其写入每个 profile 的 .env：
cat >> ~/.hermes/profiles/alice/.env <<EOF
API_SERVER_ENABLED=true
API_SERVER_PORT=8643
API_SERVER_KEY=alice-secret
EOF

cat >> ~/.hermes/profiles/bob/.env <<EOF
API_SERVER_ENABLED=true
API_SERVER_PORT=8644
API_SERVER_KEY=bob-secret
EOF

# 启动每个 profile 的 gateway
hermes -p alice gateway &
hermes -p bob gateway &
```

每个 profile 的 API 服务器会自动将 profile 名称作为模型 ID 进行广播：

- `http://localhost:8643/v1/models` → 模型 `alice`
- `http://localhost:8644/v1/models` → 模型 `bob`

在 Open WebUI 中，将每个连接作为独立连接添加。模型下拉菜单会显示 `alice` 和 `bob` 作为不同的模型，各自由完全隔离的 Hermes 实例提供支持。详情请参阅 [Open WebUI 指南](/user-guide/messaging/open-webui#multi-user-setup-with-profiles) 。

<a id="limitations"></a>
## 限制

- **响应存储** — 存储的响应（用于 `previous_response_id`）持久化在 SQLite 中，在 gateway 重启后仍然保留。最多存储 100 条响应（LRU 淘汰策略）。
- **不支持文件上传** — `/v1/chat/completions` 和 `/v1/responses` 都支持内联图片，但上传文件（`file`、`input_file`、`file_id`）和非图片文档输入不支持通过 API 进行。
- **模型字段仅为展示** — 请求中的 `model` 字段会被接受，但实际使用的 LLM 模型在服务器端的 config.yaml 中配置。

<a id="proxy-mode"></a>
## 代理模式

API 服务器也作为 **gateway 代理模式** 的后端。当另一个 Hermes gateway 实例配置了指向此 API 服务器的 `GATEWAY_PROXY_URL` 时，它会将所有消息转发到此服务器，而不是运行自己的 agent。这使得可以实现分离部署——例如，一个处理 Matrix E2EE 的 Docker 容器将消息中继到宿主侧的 agent。
请参阅 [Matrix 代理模式](/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos) 以获取完整设置指南。
