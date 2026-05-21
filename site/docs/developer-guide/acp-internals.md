---
sidebar_position: 2
title: "ACP 内部机制"
description: "ACP 适配器的工作原理：生命周期、会话、事件桥接、审批和工具渲染"
---

<a id="acp-internals"></a>
# ACP 内部机制

ACP 适配器将 Hermes 的同步 `AIAgent` 封装在一个异步 JSON-RPC stdio 服务器中。

关键实现文件：

- `acp_adapter/entry.py`
- `acp_adapter/server.py`
- `acp_adapter/session.py`
- `acp_adapter/events.py`
- `acp_adapter/permissions.py`
- `acp_adapter/tools.py`
- `acp_adapter/auth.py`
- `acp_registry/agent.json`

<a id="boot-flow"></a>
## 启动流程

```text
hermes acp / hermes-acp / python -m acp_adapter
  -> acp_adapter.entry.main()
  -> 在服务器启动前解析 --version / --check / --setup
  -> 加载 ~/.hermes/.env
  -> 配置 stderr 日志
  -> 构造 HermesACPAgent
  -> acp.run_agent(agent, use_unstable_protocol=True)
```

Zed ACP Registry 路径通过 `uvx --from 'hermes-agent[acp]==&lt;version&gt;' hermes-acp` 启动相同的适配器，指向 `hermes-agent` PyPI 发布版本。

标准输出保留给 ACP JSON-RPC 传输。人类可读的日志输出到 stderr。

<a id="major-components"></a>
## 主要组件

<a id="hermesacpagent"></a>
### `HermesACPAgent`

`acp_adapter/server.py` 实现了 ACP Agent 协议。

职责：

- 初始化 / 认证
- 新建/加载/恢复/分支/列出/取消会话方法
- 提示词执行
- 会话模型切换
- 将同步 AIAgent 回调接入 ACP 异步通知

<a id="sessionmanager"></a>
### `SessionManager`

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

<a id="event-bridge"></a>
### 事件桥接

`acp_adapter/events.py` 将 AIAgent 回调转换为 ACP `session_update` 事件。

已桥接的回调：

- `tool_progress_callback`
- `thinking_callback`（当前在 ACP 桥接中设置为 `None` —— 推理通过 `step_callback` 转发）
- `step_callback`

由于 `AIAgent` 在工作线程中运行，而 ACP I/O 在主事件循环上，桥接使用：

```python
asyncio.run_coroutine_threadsafe(...)
```

<a id="permission-bridge"></a>
### 权限桥接

`acp_adapter/permissions.py` 将危险的终端审批提示适配为 ACP 权限请求。

映射关系：

- `allow_once` -> Hermes `once`
- `allow_always` -> Hermes `always`
- 拒绝选项 -> Hermes `deny`

超时和桥接失败默认拒绝。

<a id="tool-rendering-helpers"></a>
### 工具渲染辅助函数

`acp_adapter/tools.py` 将 Hermes 工具映射到 ACP 工具类型，并构建面向编辑器的内容。

示例：

- `patch` / `write_file` -> 文件差异
- `terminal` -> shell 命令文本
- `read_file` / `search_files` -> 文本预览
- 大型结果 -> 为 UI 安全截断的文本块

<a id="session-lifecycle"></a>
## 会话生命周期

```text
new_session(cwd)
  -> 创建 SessionState
  -> 创建 AIAgent(platform="acp", enabled_toolsets=["hermes-acp"])
  -> 将 task_id/session_id 绑定到 cwd 覆盖

prompt(..., session_id)
  -> 从 ACP 内容块中提取文本
  -> 重置取消事件
  -> 安装回调 + 审批桥接
  -> 在 ThreadPoolExecutor 中运行 AIAgent
  -> 更新会话历史
  -> 发送最终 Agent 消息块
```

<a id="cancelation"></a>
### 取消

`cancel(session_id)`：

- 设置会话取消事件
- 在可用时调用 `agent.interrupt()`
- 导致提示响应返回 `stop_reason="cancelled"`
<a id="forking"></a>
### Forking

`fork_session()` 会将消息历史深度复制到一个新的实时会话中，保留对话状态，同时为分支分配独立的会话 ID 和 cwd。

<a id="provider-auth-behavior"></a>
## Provider/认证行为

ACP 不实现自己的认证存储。

它复用 Hermes 的运行时解析器：

- `acp_adapter/auth.py`
- `hermes_cli/runtime_provider.py`

因此 ACP 会通告并使用当前配置的 Hermes 提供者/凭据。它还会始终通告一个终端设置认证方法（`hermes-setup`，参数 `--setup`），以便首次运行的注册客户端在开始正常 ACP 会话之前，可以打开 Hermes 的交互式模型/提供者配置。

<a id="working-directory-binding"></a>
## 工作目录绑定

ACP 会话携带编辑器的 cwd。

会话管理器通过任务作用域的终端/文件覆盖，将该 cwd 绑定到 ACP 会话 ID，因此文件和终端工具会相对于编辑器工作区进行操作。

<a id="duplicate-same-name-tool-calls"></a>
## 重复的同名工具调用

事件桥按工具名称以 FIFO 顺序跟踪工具 ID，而不仅仅是每个名称一个 ID。这一点对于以下情况很重要：

- 并行的同名调用
- 单步中重复的同名调用

如果没有 FIFO 队列，完成事件会附加到错误的工具调用上。

<a id="approval-callback-restoration"></a>
## 审批回调恢复

ACP 在提示执行期间会临时在终端工具上安装一个审批回调，执行完成后恢复之前的回调。这样可以避免 ACP 会话特定的审批处理程序永久全局安装。

<a id="current-limitations"></a>
## 当前限制

- ACP 会话持久化到共享的 `~/.hermes/state.db`（SessionDB），并在进程重启后透明恢复；它们会出现在 `session_search` 中
- 非文本提示块当前在请求文本提取中被忽略
- 编辑器特定的用户体验因 ACP 客户端实现而异

<a id="related-files"></a>
## 相关文件

- `tests/acp/` — ACP 测试套件
- `toolsets.py` — `hermes-acp` 工具集定义
- `hermes_cli/main.py` — `hermes acp` CLI 子命令
- `pyproject.toml` — `[acp]` 可选依赖 + `hermes-acp` 脚本
