---
sidebar_position: 14
title: "API Server"
description: "将 hermes-agent 作为兼容 OpenAI 的 API 暴露给任何前端使用"
---

# API Server

API Server 将 hermes-agent 暴露为一个兼容 OpenAI 的 HTTP 端点。任何支持 OpenAI 格式的前端——如 Open WebUI、LobeChat、LibreChat、NextChat、ChatBox 以及其他数百种工具——都可以连接到 hermes-agent 并将其作为后端使用。

你的 Agent 会利用其完整的工具集（终端、文件操作、网页搜索、记忆、技能）来处理请求并返回最终响应。在流式传输时，工具进度指示器会内联显示，以便前端能够展示 Agent 正在执行的操作。

## 快速开始

### 1. 启用 API Server

在 `~/.hermes/.env` 中添加：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=change-me-local-dev
# 可选：仅当浏览器必须直接调用 Hermes 时设置
# API_SERVER_CORS_ORIGINS=http://localhost:3000
```

### 2. 启动 Gateway

```bash
hermes gateway
```

你会看到：

```
[API Server] API server listening on http://127.0.0.1:8642
```

### 3. 连接前端

将任何兼容 OpenAI 的客户端指向 `http://localhost:8642/v1`：

```bash
# 使用 curl 测试
curl http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer change-me-local-dev" \
  -H "Content-Type: application/json" \
  -d '{"model": "hermes-agent", "messages": [{"role": "user", "content": "Hello!"}]}'
```

或者连接 Open WebUI、LobeChat 或任何其他前端 —— 请参阅 [Open WebUI 集成指南](/user-guide/messaging/open-webui) 获取分步说明。

## 端点 (Endpoints)

### POST /v1/chat/completions

标准的 OpenAI Chat Completions 格式。无状态 —— 完整的对话通过 `messages` 数组包含在每个请求中。

**请求：**
```json
{
  "model": "hermes-agent",
  "messages": [
    {"role": "system", "content": "You are a Python expert."},
    {"role": "user", "content": "Write a fibonacci function"}
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
    "message": {"role": "assistant", "content": "Here's a fibonacci function..."},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 50, "completion_tokens": 200, "total_tokens": 250}
}
```

**流式传输** (`"stream": true`)：返回带有逐 token 响应块的服务器发送事件 (SSE)。当配置中启用流式传输时，token 会在 LLM 生成时实时发出。禁用时，完整响应将作为单个 SSE 块发送。

**流中的工具进度**：当 Agent 在流式请求期间调用工具时，简短的进度指示器会在工具开始执行时注入到内容流中（例如 `` `💻 pwd` ``, `` `🔍 Python docs` ``）。这些内容以行内 Markdown 形式出现在 Agent 的响应文本之前，让 Open WebUI 等前端能够实时看到工具的执行情况。

### POST /v1/responses

OpenAI Responses API 格式。通过 `previous_response_id` 支持服务器端对话状态 —— 服务器存储完整的对话历史（包括工具调用和结果），因此无需客户端管理即可保留多轮上下文。

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

#### 使用 previous_response_id 进行多轮对话

链接响应以在多轮对话中保持完整上下文（包括工具调用）：

```json
{
  "input": "Now show me the README",
  "previous_response_id": "resp_abc123"
}
```

服务器从存储的响应链中重建完整对话 —— 所有之前的工具调用和结果都会被保留。

#### 命名对话

使用 `conversation` 参数而不是跟踪响应 ID：

```json
{"input": "Hello", "conversation": "my-project"}
{"input": "What's in src/?", "conversation": "my-project"}
{"input": "Run the tests", "conversation": "my-project"}
```

服务器会自动链接到该对话中的最新响应。类似于 Gateway 会话的 `/title` 命令。

### GET /v1/responses/\{id\}

通过 ID 检索之前存储的响应。

### DELETE /v1/responses/\{id\}

删除存储的响应。

### GET /v1/models

将 `hermes-agent` 列为可用模型。大多数前端进行模型发现时需要此接口。

### GET /health

健康检查。返回 `{"status": "ok"}`。对于期望 `/v1/` 前缀的 OpenAI 兼容客户端，也可以通过 **GET /v1/health** 访问。

## 系统提示词 (System Prompt) 处理

当前端发送 `system` 消息（Chat Completions）或 `instructions` 字段（Responses API）时，hermes-agent 会将其**叠加**在核心系统提示词之上。你的 Agent 仍保留其所有工具、记忆和技能 —— 前端的系统提示词只是添加了额外的指令。

这意味着你可以针对每个前端自定义行为，而不会丢失能力：
- Open WebUI 系统提示词："You are a Python expert. Always include type hints."
- Agent 仍然拥有终端、文件工具、网页搜索、记忆等功能。

## 身份验证

通过 `Authorization` 标头进行 Bearer 令牌认证：

```
Authorization: Bearer ***
```

通过 `API_SERVER_KEY` 环境变量配置密钥。如果你需要浏览器直接调用 Hermes，还需将 `API_SERVER_CORS_ORIGINS` 设置为明确的允许列表。

:::warning 安全提示
API Server 提供了对 hermes-agent 工具集的完整访问权限，**包括终端命令**。如果你将绑定地址更改为 `0.0.0.0`（网络可访问），**请务必设置 `API_SERVER_KEY`** 并严格限制 `API_SERVER_CORS_ORIGINS` —— 否则，远程调用者可能能够在你的机器上执行任意命令。

默认绑定地址 (`127.0.0.1`) 仅供本地使用。浏览器访问默认禁用；仅为明确信任的源启用它。
:::

## 配置

### 环境变量

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `API_SERVER_ENABLED` | `false` | 启用 API Server |
| `API_SERVER_PORT` | `8642` | HTTP 服务端口 |
| `API_SERVER_HOST` | `127.0.0.1` | 绑定地址（默认仅限 localhost） |
| `API_SERVER_KEY` | _(无)_ | 用于认证的 Bearer 令牌 |
| `API_SERVER_CORS_ORIGINS` | _(无)_ | 逗号分隔的允许浏览器访问的源 |

### config.yaml

```yaml
# 暂不支持 —— 请使用环境变量。
# config.yaml 支持将在未来版本中推出。
```

## 安全标头

所有响应都包含安全标头：
- `X-Content-Type-Options: nosniff` —— 防止 MIME 类型嗅探
- `Referrer-Policy: no-referrer` —— 防止来源泄露

## CORS

API Server 默认**不**启用浏览器 CORS。

如需浏览器直接访问，请设置明确的允许列表：

```bash
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

启用 CORS 后：
- **预检请求 (Preflight) 响应** 包含 `Access-Control-Max-Age: 600`（10 分钟缓存）
- **SSE 流式响应** 包含 CORS 标头，以便浏览器的 EventSource 客户端正常工作
- **`Idempotency-Key`** 是允许的请求标头 —— 客户端可以发送它进行去重（响应按 Key 缓存 5 分钟）

大多数文档中提到的前端（如 Open WebUI）通过服务器到服务器的方式连接，完全不需要 CORS。

## 兼容的前端

任何支持 OpenAI API 格式的前端都可以工作。已测试/记录的集成：

| 前端 | Stars | 连接方式 |
|----------|-------|------------|
| [Open WebUI](/user-guide/messaging/open-webui) | 126k | 提供完整指南 |
| LobeChat | 73k | 自定义提供商端点 |
| LibreChat | 34k | librechat.yaml 中的自定义端点 |
| AnythingLLM | 56k | 通用 OpenAI 提供商 |
| NextChat | 87k | BASE_URL 环境变量 |
| ChatBox | 39k | API Host 设置 |
| Jan | 26k | 远程模型配置 |
| HF Chat-UI | 8k | OPENAI_BASE_URL |
| big-AGI | 7k | 自定义端点 |
| OpenAI Python SDK | — | `OpenAI(base_url="http://localhost:8642/v1")` |
| curl | — | 直接 HTTP 请求 |
## 限制

- **响应存储** — 已存储的响应（用于 `previous_response_id`）持久化在 SQLite 中，在网关重启后依然存在。最多存储 100 条响应（采用 LRU 淘汰算法）。
- **不支持文件上传** — 目前 API 尚未支持通过上传文件进行视觉或文档分析。
- **Model 字段仅供参考** — 请求中的 `model` 字段会被接收，但实际使用的 LLM 模型是在服务器端的 config.yaml 中配置的。
