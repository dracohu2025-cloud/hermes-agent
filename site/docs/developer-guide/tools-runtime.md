---
sidebar_position: 9
title: "Tools Runtime"
description: "工具注册表、工具集、调度与终端环境的运行时行为"
---

# Tools Runtime {#tools-runtime}

Hermes 工具是自注册函数，按工具集分组，通过中央注册表/调度系统执行。

主要文件：

- `tools/registry.py`
- `model_tools.py`
- `toolsets.py`
- `tools/terminal_tool.py`
- `tools/environments/*`

## 工具注册模型 {#tool-registration-model}

每个工具模块在导入时调用 `registry.register(...)`。

`model_tools.py` 负责导入/发现工具模块，并构建模型使用的 schema 列表。

### `registry.register()` 的工作原理 {#how-registry-register-works}

`tools/` 下的每个工具文件都在模块级别调用 `registry.register()` 来声明自身。函数签名如下：

```python
registry.register(
    name="terminal",               # 唯一工具名（用于 API schema）
    toolset="terminal",            # 该工具所属的工具集
    schema={...},                  # OpenAI 函数调用 schema（description、parameters）
    handler=handle_terminal,       # 工具被调用时执行的函数
    check_fn=check_terminal,       # 可选：返回 True/False 表示是否可用
    requires_env=["SOME_VAR"],     # 可选：所需环境变量（用于 UI 展示）
    is_async=False,                # handler 是否为异步协程
    description="Run commands",    # 人类可读描述
    emoji="💻",                    # 用于 spinner/进度展示的 emoji
)
```

每次调用都会创建一个 `ToolEntry`，存储在单例 `ToolRegistry._tools` 字典中，以工具名作为键。如果不同工具集之间发生名称冲突，会记录警告，后注册的工具胜出。

### 发现机制：`discover_builtin_tools()` {#discovery-discoverbuiltintools}

`model_tools.py` 被导入时，会调用 `tools/registry.py` 中的 `discover_builtin_tools()`。该函数使用 AST 解析扫描每个 `tools/*.py` 文件，查找包含顶层 `registry.register()` 调用的模块，然后导入它们：

```python
# tools/registry.py（简化版）
def discover_builtin_tools(tools_dir=None):
    tools_path = Path(tools_dir) if tools_dir else Path(__file__).parent
    for path in sorted(tools_path.glob("*.py")):
        if path.name in {"__init__.py", "registry.py", "mcp_tool.py"}:
            continue
        if _module_registers_tools(path):  # AST 检查顶层 registry.register()
            importlib.import_module(f"tools.{path.stem}")
```

这种自动发现意味着新工具文件会被自动识别——无需手动维护列表。AST 检查只匹配顶层的 `registry.register()` 调用（函数内部的调用不匹配），因此 `tools/` 中的辅助模块不会被导入。

每次导入都会触发模块中的 `registry.register()` 调用。可选工具中的错误（例如图像生成缺少 `fal_client`）会被捕获并记录——不会阻止其他工具加载。

核心工具发现完成后，还会发现 MCP 工具和插件工具：

1. **MCP 工具** — `tools.mcp_tool.discover_mcp_tools()` 读取 MCP 服务器配置，并从外部服务器注册工具。
2. **插件工具** — `hermes_cli.plugins.discover_plugins()` 加载用户/项目/pip 插件，这些插件可能会注册额外的工具。

## 工具可用性检查（`check_fn`） {#tool-availability-checking-checkfn}

每个工具可以选填一个 `check_fn`——一个可调用对象，工具可用时返回 `True`，否则返回 `False`。典型的检查包括：

- **API key 是否存在** — 例如网页搜索使用 `lambda: bool(os.environ.get("SERP_API_KEY"))`
- **服务是否运行中** — 例如检查 Honcho 服务器是否已配置
- **二进制文件是否已安装** — 例如验证浏览器工具所需的 `playwright` 是否可用

`registry.get_definitions()` 为模型构建 schema 列表时，会运行每个工具的 `check_fn()`：

```python
# 简化自 registry.py
if entry.check_fn:
    try:
        available = bool(entry.check_fn())
    except Exception:
        available = False   # 异常 = 不可用
    if not available:
        continue            # 完全跳过该工具
```

关键行为：
- 检查结果**按调用缓存**——如果多个工具共享同一个 `check_fn`，只运行一次。
- `check_fn()` 中的异常被视为"不可用"（故障安全）。
- `is_toolset_available()` 方法检查某个工具集的 `check_fn` 是否通过，用于 UI 展示和工具集解析。
## Toolset 解析 {#toolset-resolution}

Toolset 是工具的命名组合。Hermes 通过以下方式解析它们：

- 显式启用/禁用的 toolset 列表
- 平台预设（`hermes-cli`、`hermes-telegram` 等）
- 动态 MCP toolset
- 精选的特殊用途集合，如 `hermes-acp`

### `get_tool_definitions()` 如何过滤工具 {#how-gettooldefinitions-filters-tools}

主入口是 `model_tools.get_tool_definitions(enabled_toolsets, disabled_toolsets, quiet_mode)`：

1. **如果提供了 `enabled_toolsets`** — 只包含这些 toolset 中的工具。每个 toolset 名称通过 `resolve_toolset()` 解析，后者将复合 toolset 展开为单个工具名称。

2. **如果提供了 `disabled_toolsets`** — 从所有 toolset 开始，然后减去被禁用的那些。

3. **如果两者都没提供** — 包含所有已知的 toolset。

4. **注册表过滤** — 解析后的工具名称集合被传递给 `registry.get_definitions()`，后者应用 `check_fn` 过滤并返回 OpenAI 格式的 schema。

5. **动态 schema 修补** — 过滤完成后，`execute_code` 和 `browser_navigate` 的 schema 会被动态调整，只引用实际通过过滤的工具（防止模型幻觉出不可用的工具）。

### 旧版 toolset 名称 {#legacy-toolset-names}

带有 `_tools` 后缀的旧版 toolset 名称（例如 `web_tools`、`terminal_tools`）通过 `_LEGACY_TOOLSET_MAP` 映射到现代工具名称，以保持向后兼容。

## 调度 {#dispatch}

运行时，工具通过中央注册表进行调度，但部分 Agent 级别的工具（如 memory/todo/session-search 处理）会在 Agent loop 中做例外处理。

### 调度流程：模型 tool_call → 处理器执行 {#dispatch-flow-model-toolcall-handler-execution}

当模型返回 `tool_call` 时，流程如下：

```
Model response with tool_call
    ↓
run_agent.py agent loop
    ↓
model_tools.handle_function_call(name, args, task_id, user_task)
    ↓
[Agent-loop tools?] → handled directly by agent loop (todo, memory, session_search, delegate_task)
    ↓
[Plugin pre-hook] → invoke_hook("pre_tool_call", ...)
    ↓
registry.dispatch(name, args, **kwargs)
    ↓
Look up ToolEntry by name
    ↓
[Async handler?] → bridge via _run_async()
[Sync handler?]  → call directly
    ↓
Return result string (or JSON error)
    ↓
[Plugin post-hook] → invoke_hook("post_tool_call", ...)
```

### 错误包装 {#error-wrapping}

所有工具执行都在两个层级上做了错误处理包装：

1. **`registry.dispatch()`** — 捕获处理器抛出的任何异常，返回 JSON 格式的 `{"error": "Tool execution failed: ExceptionType: message"}`。

2. **`handle_function_call()`** — 用第二层 try/except 包装整个调度过程，返回 `{"error": "Error executing tool_name: message"}`。

这确保模型始终收到格式良好的 JSON 字符串，永远不会收到未处理的异常。

### Agent-loop 工具 {#agent-loop-tools}

有四个工具会在注册表调度前被拦截，因为它们需要 Agent 级别的状态（TodoStore、MemoryStore 等）：

- `todo` — 规划/任务跟踪
- `memory` — 持久化记忆写入
- `session_search` — 跨会话回忆
- `delegate_task` — 生成子 Agent 会话

这些工具的 schema 仍在注册表中注册（供 `get_tool_definitions` 使用），但如果调度意外直接到达它们，其处理器会返回一个 stub 错误。

### 异步桥接 {#async-bridging}

当工具处理器是异步时，`_run_async()` 将其桥接到同步调度路径：

- **CLI 路径（无运行中的 loop）** — 使用持久化事件循环，保持缓存的异步客户端存活
- **Gateway 路径（有运行中的 loop）** — 启动一个一次性线程，内部使用 `asyncio.run()`
- **工作线程（并行工具）** — 使用存储在线程本地存储中的、每个线程独立的持久化 loop

## DANGEROUS_PATTERNS 审批流程 {#the-dangerouspatterns-approval-flow}

终端工具集成了危险命令审批系统，定义在 `tools/approval.py` 中：

1. **模式检测** — `DANGEROUS_PATTERNS` 是一个 `(regex, description)` 元组列表，涵盖破坏性操作：
   - 递归删除（`rm -rf`）
   - 文件系统格式化（`mkfs`、`dd`）
   - SQL 破坏性操作（`DROP TABLE`、不带 `WHERE` 的 `DELETE FROM`）
   - 系统配置覆盖（`> /etc/`）
   - 服务操作（`systemctl stop`）
   - 远程代码执行（`curl | sh`）
   - Fork 炸弹、进程终止等
2. **检测** — 在执行任何终端命令之前，`detect_dangerous_command(command)` 会检查所有模式。

3. **审批提示** — 如果匹配成功：
   - **CLI 模式** — 交互式提示询问用户批准、拒绝或永久允许
   - **Gateway 模式** — 异步审批回调将请求发送到消息平台
   - **智能审批** — 可选地，辅助 LLM 可以自动批准匹配模式的低风险命令（例如，`rm -rf node_modules/` 是安全的，但匹配"递归删除"）

4. **会话状态** — 审批按会话跟踪。一旦你在某个会话中批准了"递归删除"，后续的 `rm -rf` 命令就不会再提示。

5. **永久允许列表** — "永久允许"选项会将模式写入 `config.yaml` 的 `command_allowlist`，跨会话持久保存。

## 终端/运行环境 {#terminal-runtime-environments}

终端系统支持多种后端：

- local
- docker
- ssh
- singularity
- modal
- daytona

还支持：

- 按任务覆盖 cwd
- 后台进程管理
- PTY 模式
- 危险命令的审批回调

## 并发 {#concurrency}

工具调用可能按顺序或并发执行，具体取决于工具组合和交互需求。

## 相关文档 {#related-docs}

- [Toolsets 参考](../reference/toolsets-reference.md)
- [内置工具参考](../reference/tools-reference.md)
- [Agent Loop 内部机制](./agent-loop.md)
- [ACP 内部机制](./acp-internals.md)
