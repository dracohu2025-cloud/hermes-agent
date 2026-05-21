---
sidebar_position: 8
title: "程序化集成"
description: "从外部程序驱动 hermes-agent 的三种协议：ACP、TUI 网关 JSON-RPC 以及兼容 OpenAI 的 HTTP API"
---

<a id="programmatic-integration"></a>
# 程序化集成

Hermes 提供了三种协议，用于从外部程序（如 IDE 插件、自定义 UI、CI 流水线、嵌入式子 Agent）驱动 Agent。请根据你的传输方式和消费者选择最合适的协议。

| 协议 | 传输方式 | 最佳适用场景 | 定义位置 |
|----------|-----------|----------|------------|
| **ACP** | 基于 stdio 的 JSON-RPC | 已支持 [Agent Client Protocol](https://github.com/zed-industries/agent-client-protocol) 的 IDE 客户端（VS Code、Zed、JetBrains） | `acp_adapter/` |
| **TUI 网关** | 基于 stdio（或 WebSocket）的 JSON-RPC | 希望对会话、斜杠命令、审批和流式事件进行精细控制的自定义宿主 | `tui_gateway/server.py` |
| **API 服务器** | HTTP + 服务器推送事件 | 兼容 OpenAI 的前端（Open WebUI、LobeChat、LibreChat…）以及语言无关的 Web 客户端 | `gateway/platforms/api_server.py` |

这三种协议都驱动同一个 `AIAgent` 核心。它们的区别仅在于传输格式和暴露的功能集。

---

<a id="acp-agent-client-protocol"></a>
## ACP（Agent Client Protocol）

`hermes acp` 启动一个基于 stdio 的 JSON-RPC 服务器，使用 ACP 协议通信。在生产环境中，VS Code（Zed Industries 的 ACP 扩展）、Zed 以及任何安装了 ACP 插件的 JetBrains IDE 都在使用它。

暴露的能力：会话创建、提示提交、流式 Agent 消息块、工具调用事件、权限请求、会话分支、取消和身份验证。工具输出会被渲染成 IDE 能理解的 ACP `Diff`/`ToolCall` 内容块。

完整的生命周期、事件桥接和审批流程：[ACP 内部机制](./acp-internals)。

```bash
hermes acp                  # 在 stdio 上提供 ACP 服务
hermes acp --bootstrap      # 为支持 ACP 的 IDE 打印安装片段
```

---

<a id="tui-gateway-json-rpc"></a>
## TUI 网关 JSON-RPC

`tui_gateway/server.py` 是 Ink TUI（`hermes --tui`）和嵌入式仪表盘 PTY 桥接器所使用的协议。任何外部宿主都可以通过 stdio（或通过 `tui_gateway/ws.py` 的 WebSocket）使用相同的协议进行通信。

<a id="method-catalog-selected"></a>
### 方法目录（精选）

```
prompt.submit           prompt.background       session.steer
session.create          session.list            session.interrupt
session.history         session.compress        session.branch
session.title           session.usage           session.status
clarify.respond         sudo.respond            secret.respond
approval.respond        config.set / config.get commands.catalog
command.resolve         command.dispatch        cli.exec
reload.mcp              reload.env              process.stop
delegation.status       subagent.interrupt      spawn_tree.save / list / load
terminal.resize         clipboard.paste         image.attach
```

<a id="events-streamed-back"></a>
### 流式返回的事件

`message.delta`、`message.complete`、`tool.start`、`tool.progress`、`tool.complete`、`approval.request`、`clarify.request`、`sudo.request`、`secret.request`、`gateway.ready`，以及会话生命周期和错误事件。

<a id="pi-style-rpc-mapping"></a>
### Pi 风格的 RPC 映射

Pi-mono RPC 规范（[issue #360](https://github.com/NousResearch/hermes-agent/issues/360)）中的每个命令都有对应的 TUI 网关实现：
| Pi 命令 | Hermes 对应 |
|---------|-------------|
| `prompt` | `prompt.submit` (或 ACP `session/prompt`) |
| `steer` | `session.steer` |
| `follow_up` | `prompt.submit` 在当前轮次后排队 |
| `abort` | `session.interrupt` |
| `set_model` | `command.dispatch`，用于 `/model &lt;provider:model&gt;`（会话中，持久化） |
| `compact` | `session.compress` |
| `get_state` | `session.status` |
| `get_messages` | `session.history` |
| `switch_session` | `session.resume` |
| `fork` | `session.branch` |
| `ui_request` / `ui_response` | `clarify.respond` / `sudo.respond` / `secret.respond` / `approval.respond` |

---

<a id="openai-compatible-api-server"></a>
## 兼容 OpenAI 的 API 服务器

`gateway/platforms/api_server.py` 将 hermes 通过 HTTP 暴露出来，供任何已支持 OpenAI 格式的客户端使用。当你需要一个 Web 前端、一个基于 curl 的 CI 运行器，或一个非 Python 使用者时，这非常有用。

端点：

```
POST /v1/chat/completions        OpenAI Chat Completions（通过 SSE 流式传输）
POST /v1/responses               OpenAI Responses API（有状态）
POST /v1/runs                    启动一个运行，返回 run_id（202）
GET  /v1/runs/{id}               运行状态
GET  /v1/runs/{id}/events        生命周期事件的 SSE 流
POST /v1/runs/{id}/approval      解决待处理的审批
POST /v1/runs/{id}/stop          中断运行
GET  /v1/capabilities            机器可读的功能标志
GET  /v1/models                  列出 hermes-agent
GET  /health, /health/detailed
```

设置、请求头（`X-Hermes-Session-Id`、`X-Hermes-Session-Key`）以及前端配置：[API Server](../user-guide/features/api-server)。

---

<a id="which-one-should-i-use"></a>
## 我应该使用哪一个？

- **你正在编写一个 IDE 插件，并且该 IDE 已经支持 ACP** → 使用 ACP。IDE 端无需任何协议工作。
- **你正在编写一个自定义桌面 / Web / TUI 主机，并希望使用所有 Hermes 功能**（斜杠命令、审批、澄清、多 Agent、会话分支） → 使用 TUI gateway JSON-RPC。
- **你想要任何兼容 OpenAI 的前端、与语言无关的 HTTP 客户端，或基于 curl 的自动化** → 使用 API 服务器。
- **你希望在进程内嵌入 Python 而无需子进程** → 直接导入 `run_agent.AIAgent`。参见 [Agent Loop](./agent-loop)。

---

<a id="model-hot-swapping"></a>
## 模型热切换

会话中的模型切换在所有界面上都能工作——底层使用 `/model` 斜杠命令。

- **CLI / TUI:** `/model claude-sonnet-4` 或 `/model openrouter:anthropic/claude-sonnet-4.6`
- **TUI gateway RPC:** `command.dispatch` 配合 `{"command": "/model claude-sonnet-4"}`
- **ACP:** IDE 将斜杠命令作为提示发送；Agent 分发它
- **API 服务器:** 在请求体中加入 `model` 字段，或设置 `X-Hermes-Model`

内置了 Provider 感知的解析功能（同一个模型名称会自动为当前使用的 Provider 选择正确的格式）。参见 `hermes_cli/model_switch.py`。

---

<a id="a-note-on-mode-rpc"></a>
## 关于 `--mode rpc` 的说明

Hermes 没有 `--mode rpc` 标志。上述三种协议已经覆盖了各种使用场景——ACP 用于 IDE 协议客户端，TUI gateway 用于 stdio JSON-RPC 主机，API 服务器用于 HTTP。如果你发现真的存在某个空白未被覆盖，请打开一个 issue，并说明你正在构建的具体消费者。
