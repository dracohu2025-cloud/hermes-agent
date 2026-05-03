---
sidebar_position: 2
title: "ACP 内部机制"
description: "ACP 适配器的工作原理：生命周期、会话、事件桥接、审批和工具渲染"
---

# ACP 内部机制 {#acp-internals}

ACP 适配器将 Hermes 的同步 `AIAgent` 包装在一个异步 JSON-RPC stdio 服务器中。

关键实现文件：

- `acp_adapter/entry.py`
- `acp_adapter/server.py`
- `acp_adapter/session.py`
- `acp_adapter/events.py`
- `acp_adapter/permissions.py`
- `acp_adapter/tools.py`
- `acp_adapter/auth.py`
- `acp_registry/agent.json`

## 启动流程 {#boot-flow}

```text
hermes acp / hermes-acp / python -m acp_adapter
  -> acp_adapter.entry.main()
  -> load ~/.hermes/.env
  -> configure stderr logging
  -> construct HermesACPAgent
  -> acp.run_agent(agent, use_unstable_protocol=True)
```

Stdout 保留给 ACP JSON-RPC 传输。人类可读的日志输出到 stderr。

## 主要组件 {#major-components}

### `HermesACPAgent` {#hermesacpagent}

`acp_adapter/server.py` 实现了 ACP Agent 协议。

职责：

- 初始化 / 认证
- 新建/加载/恢复/分支/列出/取消会话方法
- 提示执行
- 会话模型切换
- 将同步 AIAgent 回调接入 ACP 异步通知

### `SessionManager` {#sessionmanager}

`acp_adapter/session.py` 跟踪活跃的 ACP 会话。

每个会话存储：

- `session_id`
- `agent`
- `cwd`
- `model`
- `history`
- `cancel_event`

管理器是线程安全的，支持：

- 创建
- 获取
- 移除
- 分支
- 列出
- 清理
- cwd 更新

### 事件桥接 {#event-bridge}

`acp_adapter/events.py` 将 AIAgent 回调转换为 ACP `session_update` 事件。

桥接的回调：

- `tool_progress_callback`
- `thinking_callback`
- `step_callback`
- `message_callback`

由于 `AIAgent` 在工作线程中运行，而 ACP I/O 位于主事件循环上，桥接使用：

```python
asyncio.run_coroutine_threadsafe(...)
```

### 权限桥接 {#permission-bridge}

`acp_adapter/permissions.py` 将危险的终端审批提示适配为 ACP 权限请求。

映射：

- `allow_once` -> Hermes `once`
- `allow_always` -> Hermes `always`
- 拒绝选项 -> Hermes `deny`

超时和桥接失败默认拒绝。

### 工具渲染辅助 {#tool-rendering-helpers}

`acp_adapter/tools.py` 将 Hermes 工具映射到 ACP 工具种类，并构建面向编辑器的内容。

示例：

- `patch` / `write_file` -> 文件差异
- `terminal` -> shell 命令文本
- `read_file` / `search_files` -> 文本预览
- 大型结果 -> 为 UI 安全截断的文本块

## 会话生命周期 {#session-lifecycle}

```text
new_session(cwd)
  -> create SessionState
  -> create AIAgent(platform="acp", enabled_toolsets=["hermes-acp"])
  -> bind task_id/session_id to cwd override

prompt(..., session_id)
  -> extract text from ACP content blocks
  -> reset cancel event
  -> install callbacks + approval bridge
  -> run AIAgent in ThreadPoolExecutor
  -> update session history
  -> emit final agent message chunk
```

### 取消 {#cancelation}

`cancel(session_id)`:

- 设置会话取消事件
- 在可用时调用 `agent.interrupt()`
- 导致提示响应返回 `stop_reason="cancelled"`

### 分支 {#forking}

`fork_session()` 将消息历史深度复制到一个新的活跃会话中，保留对话状态，同时为分支提供自己的会话 ID 和 cwd。

## 提供者/认证行为 {#provider-auth-behavior}
ACP 没有实现自己的认证存储。

而是复用了 Hermes 的运行时解析器：

- `acp_adapter/auth.py`
- `hermes_cli/runtime_provider.py`

因此，ACP 会通告并使用当前配置的 Hermes 提供者/凭据。

## 工作目录绑定 {#working-directory-binding}

ACP 会话携带编辑器的当前工作目录（cwd）。

会话管理器通过任务作用域的终端/文件覆盖，将该 cwd 绑定到 ACP 会话 ID，从而让文件和终端工具相对于编辑器工作空间进行操作。

## 重复的同名工具调用 {#duplicate-same-name-tool-calls}

事件桥按工具名称以 FIFO 顺序跟踪工具 ID，而不仅仅是每个名称一个 ID。这一点对于以下场景很重要：

- 并行的同名调用
- 同一步骤中重复的同名调用

如果没有 FIFO 队列，完成事件会附加到错误的工具调用上。

## 批准回调恢复 {#approval-callback-restoration}

ACP 在提示执行期间临时在终端工具上安装一个批准回调，之后恢复之前的回调。这避免了将 ACP 会话特定的批准处理程序永久全局安装。

## 当前限制 {#current-limitations}

- ACP 会话持久化到共享的 `~/.hermes/state.db`（SessionDB），并在进程重启后透明恢复；它们会出现在 `session_search` 中
- 非文本提示块目前被忽略，不用于请求文本提取
- 编辑器特定的用户体验因 ACP 客户端实现而异

## 相关文件 {#related-files}

- `tests/acp/` — ACP 测试套件
- `toolsets.py` — `hermes-acp` 工具集定义
- `hermes_cli/main.py` — `hermes acp` CLI 子命令
- `pyproject.toml` — `[acp]` 可选依赖 + `hermes-acp` 脚本
