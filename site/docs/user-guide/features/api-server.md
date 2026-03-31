---
sidebar_position: 14
title: "API 服务器"
description: "将 hermes-agent 作为 OpenAI 兼容的 API 暴露给任何前端使用"
---

# API 服务器

API 服务器将 hermes-agent 暴露为一个 OpenAI 兼容的 HTTP 端点。任何支持 OpenAI 格式的前端 —— 如 Open WebUI、LobeChat、LibreChat、NextChat、ChatBox 以及数百种其他应用 —— 都可以连接到 hermes-agent 并将其用作后端。

你的智能体将使用其完整的工具集（终端、文件操作、网络搜索、记忆、技能）处理请求，并返回最终响应。工具调用在服务器端不可见地执行。

## 快速开始

### 1. 启用 API 服务器

添加到 `~/.hermes/.env`：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=change-me-local-dev
# 可选：仅在浏览器必须直接调用 Hermes 时设置
# API_SERVER_CORS_ORIGINS=http://localhost:3000
```

### 2. 启动网关

```bash
hermes gateway
```

你将看到：

```
[API Server] API server listening on http://127.0.0.1:8642
```

### 3. 连接前端

将任何 OpenAI 兼容的客户端指向 `http://localhost:8642/v1`：

```bash
# 使用 curl 测试
curl http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer change-me-local-dev" \
  -H "Content-Type: application/json" \
  -d '{"model": "hermes-agent", "messages": [{"role": "user", "content": "Hello!"}]}'
```

或者连接 Open WebUI、LobeChat 或任何其他前端 —— 请参阅 [Open WebUI 集成指南](/docs/user-guide/messaging/open-webui) 获取分步说明。

## 端点

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

**流式传输** (`"stream": true`)：返回服务器发送事件（SSE），包含逐词元的响应块。当在配置中启用流式传输时，词元会在 LLM 生成时实时发出。当禁用时，完整响应将作为单个 SSE 块发送。

### POST /v1/responses

OpenAI Responses API 格式。通过 `previous_response_id` 支持服务器端对话状态 —— 服务器存储完整的对话历史（包括工具调用和结果），因此多轮上下文得以保留，无需客户端管理。

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

链接响应以在多个轮次中保持完整上下文（包括工具调用）：

```json
{
  "input": "Now show me the README",
  "previous_response_id": "resp_abc123"
}
```

服务器从存储的响应链重建完整对话 —— 所有之前的工具调用和结果都被保留。

#### 命名对话

使用 `conversation` 参数，而不是跟踪响应 ID：

```json
{"input": "Hello", "conversation": "my-project"}
{"input": "What's in src/?", "conversation": "my-project"}
{"input": "Run the tests", "conversation": "my-project"}
```

服务器会自动链接到该对话中的最新响应。类似于网关会话的 `/title` 命令。

### GET /v1/responses/\{id\}

按 ID 检索先前存储的响应。

### DELETE /v1/responses/\{id\}

删除存储的响应。

### GET /v1/models

将 `hermes-agent` 列为可用模型。大多数前端需要此端点进行模型发现。

### GET /health

健康检查。返回 `{"status": "ok"}`。也可在 **GET /v1/health** 访问，以兼容期望 `/v1/` 前缀的 OpenAI 兼容客户端。

## 系统提示处理

当前端发送 `system` 消息（Chat Completions）或 `instructions` 字段（Responses API）时，hermes-agent **会将其叠加在**其核心系统提示之上。你的智能体保留其所有工具、记忆和技能 —— 前端的系统提示添加了额外的指令。

这意味着你可以按前端定制行为而不丢失能力：
- Open WebUI 系统提示："You are a Python expert. Always include type hints."
- 智能体仍然拥有终端、文件工具、网络搜索、记忆等。

## 认证

通过 `Authorization` 头进行 Bearer 令牌认证：

```
Authorization: Bearer ***
```

通过 `API_SERVER_KEY` 环境变量配置密钥。如果你需要浏览器直接调用 Hermes，还需将 `API_SERVER_CORS_ORIGINS` 设置为明确的允许列表。

:::warning 安全
API 服务器授予对 hermes-agent 工具集的完全访问权限，**包括终端命令**。如果你将绑定地址更改为 `0.0.0.0`（可从网络访问），**务必设置 `API_SERVER_KEY`** 并保持 `API_SERVER_CORS_ORIGINS` 范围狭窄 —— 否则，远程调用者可能能够在你的机器上执行任意命令。

默认绑定地址（`127.0.0.1`）仅用于本地访问。默认情况下浏览器访问被禁用；仅对明确信任的来源启用。
:::

## 配置

### 环境变量

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `API_SERVER_ENABLED` | `false` | 启用 API 服务器 |
| `API_SERVER_PORT` | `8642` | HTTP 服务器端口 |
| `API_SERVER_HOST` | `127.0.0.1` | 绑定地址（默认仅限 localhost） |
| `API_SERVER_KEY` | _(无)_ | 用于认证的 Bearer 令牌 |
| `API_SERVER_CORS_ORIGINS` | _(无)_ | 逗号分隔的允许的浏览器来源 |

### config.yaml

```yaml
# 暂不支持 —— 请使用环境变量。
# config.yaml 支持将在未来版本中提供。
```

## 安全头

所有响应都包含安全头：
- `X-Content-Type-Options: nosniff` —— 防止 MIME 类型嗅探
- `Referrer-Policy: no-referrer` —— 防止引用来源泄漏

## CORS

API 服务器默认**不**启用浏览器 CORS。

对于直接浏览器访问，设置明确的允许列表：

```bash
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

启用 CORS 时：
- **预检响应** 包含 `Access-Control-Max-Age: 600`（10 分钟缓存）
- **SSE 流式响应** 包含 CORS 头，以便浏览器 EventSource 客户端正常工作
- **`Idempotency-Key`** 是允许的请求头 —— 客户端可以发送它以进行去重（响应按密钥缓存 5 分钟）

大多数有文档记录的前端（如 Open WebUI）是服务器到服务器连接，完全不需要 CORS。

## 兼容的前端

任何支持 OpenAI API 格式的前端都适用。已测试/有文档记录的集成：

| 前端 | Stars | 连接方式 |
|----------|-------|------------|
| [Open WebUI](/docs/user-guide/messaging/open-webui) | 126k | 提供完整指南 |
| LobeChat | 73k | 自定义提供者端点 |
| LibreChat | 34k | librechat.yaml 中的自定义端点 |
| AnythingLLM | 56k | 通用 OpenAI 提供者 |
| NextChat | 87k | BASE_URL 环境变量 |
| ChatBox | 39k | API Host 设置 |
| Jan | 26k | 远程模型配置 |
| HF Chat-UI | 8k | OPENAI_BASE_URL |
| big-AGI | 7k | 自定义端点 |
| OpenAI Python SDK | — | `OpenAI(base_url="http://localhost:8642/v1")` |
| curl | — | 直接 HTTP 请求 |

## 限制

- **响应存储** —— 存储的响应（用于 `previous_response_id`）保存在 SQLite 中，并在网关重启后保留。最多存储 100 个响应（LRU 淘汰）。
- **不支持文件上传** —— 通过上传文件进行的视觉/文档分析尚不支持通过 API 进行。
- **模型字段仅为装饰性** —— 请求中的 `model` 字段被接受，但实际使用的 LLM 模型是在服务器端的 config.yaml 中配置的。
