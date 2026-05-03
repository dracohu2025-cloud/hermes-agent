---
sidebar_position: 9
title: "工具运行时"
description: "工具注册表、工具集、调度和终端环境的运行时行为"
---

# 工具运行时 {#tools-runtime}

Hermes 工具是自注册函数，它们被分组到工具集中，并通过一个中央注册/调度系统执行。

主要文件：

- `tools/registry.py`
- `model_tools.py`
- `toolsets.py`
- `tools/terminal_tool.py`
- `tools/environments/*`

## 工具注册模型 {#tool-registration-model}

每个工具模块在导入时都会调用 `registry.register(...)`。

`model_tools.py` 负责导入/发现工具模块，并构建模型使用的 schema 列表。

### `registry.register()` 的工作原理 {#how-registry-register-works}

`tools/` 中的每个工具文件都会在模块级别调用 `registry.register()` 来声明自身。函数签名如下：

```python
registry.register(
    name="terminal",               # 唯一的工具名称（在 API schema 中使用）
    toolset="terminal",            # 该工具所属的工具集
    schema={...},                  # OpenAI 函数调用 schema（描述、参数）
    handler=handle_terminal,       # 工具被调用时执行的函数
    check_fn=check_terminal,       # 可选：返回 True/False 表示可用性
    requires_env=["SOME_VAR"],     # 可选：所需的环境变量（用于 UI 显示）
    is_async=False,                # handler 是否为异步协程
    description="运行命令",        # 人类可读的描述
    emoji="💻",                    # 用于 spinner/进度显示的 Emoji
)
```

每次调用都会创建一个 `ToolEntry`，存储在单例 `ToolRegistry._tools` 字典中，以工具名称为键。如果不同工具集之间发生名称冲突，会记录一条警告，并且后注册的会覆盖先注册的。

### 发现：`discover_builtin_tools()` {#discovery-discoverbuiltintools}

当 `model_tools.py` 被导入时，它会从 `tools/registry.py` 调用 `discover_builtin_tools()`。此函数使用 AST 解析扫描每个 `tools/*.py` 文件，以查找包含顶层 `registry.register()` 调用的模块，然后导入它们：

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

这种自动发现意味着新的工具文件会被自动识别——无需手动维护列表。AST 检查仅匹配顶层的 `registry.register()` 调用（不匹配函数内部的调用），因此 `tools/` 中的辅助模块不会被导入。

每次导入都会触发该模块的 `registry.register()` 调用。可选工具中的错误（例如，图像生成缺少 `fal_client`）会被捕获并记录——它们不会阻止其他工具的加载。

在核心工具发现之后，MCP 工具和插件工具也会被发现：

1. **MCP 工具** — `tools.mcp_tool.discover_mcp_tools()` 读取 MCP 服务器配置，并从外部服务器注册工具。
2. **插件工具** — `hermes_cli.plugins.discover_plugins()` 加载可能注册额外工具的用户/项目/pip 插件。
## 工具可用性检查 (`check_fn`) {#tool-availability-checking-checkfn}

每个工具都可以提供一个 `check_fn` —— 一个可调用对象，当工具可用时返回 `True`，否则返回 `False`。典型的检查包括：

- **API 密钥是否存在** —— 例如，网络搜索的 `lambda: bool(os.environ.get("SERP_API_KEY"))`
- **服务是否运行** —— 例如，检查 Honcho 服务器是否已配置
- **二进制程序是否已安装** —— 例如，验证浏览器工具所需的 `playwright` 是否可用

当 `registry.get_definitions()` 为模型构建 schema 列表时，它会运行每个工具的 `check_fn()`：

```python
# 从 registry.py 简化而来
if entry.check_fn:
    try:
        available = bool(entry.check_fn())
    except Exception:
        available = False   # 异常 = 不可用
    if not available:
        continue            # 完全跳过该工具
```

关键行为：
- 检查结果**每次调用都会缓存** —— 如果多个工具共享同一个 `check_fn`，它只会运行一次。
- `check_fn()` 中的异常被视为"不可用"（故障安全）。
- `is_toolset_available()` 方法用于检查某个工具集的 `check_fn` 是否通过，用于 UI 显示和工具集解析。

## 工具集解析 {#toolset-resolution}

工具集是工具的命名集合。Hermes 通过以下方式解析它们：

- 显式启用/禁用的工具集列表
- 平台预设（`hermes-cli`、`hermes-telegram` 等）
- 动态 MCP 工具集
- 精选的特殊用途集合，如 `hermes-acp`

### `get_tool_definitions()` 如何过滤工具 {#how-gettooldefinitions-filters-tools}

主要入口点是 `model_tools.get_tool_definitions(enabled_toolsets, disabled_toolsets, quiet_mode)`：

1. **如果提供了 `enabled_toolsets`** —— 只包含来自这些工具集的工具。每个工具集名称通过 `resolve_toolset()` 解析，该函数将复合工具集展开为单个工具名称。

2. **如果提供了 `disabled_toolsets`** —— 从所有工具集开始，然后减去被禁用的工具集。

3. **如果两者都未提供** —— 包含所有已知工具集。

4. **注册表过滤** —— 解析后的工具名称集合被传递给 `registry.get_definitions()`，该函数应用 `check_fn` 过滤并返回 OpenAI 格式的 schema。

5. **动态 schema 修补** —— 过滤后，`execute_code` 和 `browser_navigate` 的 schema 会被动态调整，只引用实际通过过滤的工具（防止模型幻觉出不可用的工具）。

### 旧版工具集名称 {#legacy-toolset-names}

带有 `_tools` 后缀的旧工具集名称（例如 `web_tools`、`terminal_tools`）通过 `_LEGACY_TOOLSET_MAP` 映射到其现代工具名称，以保持向后兼容。

## 分发 {#dispatch}

在运行时，工具通过中央注册表进行分发，对于某些 Agent 级别的工具（如 memory/todo/session-search 处理），会有 agent-loop 异常处理。

### 分发流程：模型 tool_call → 处理器执行 {#dispatch-flow-model-toolcall-handler-execution}

当模型返回 `tool_call` 时，流程如下：

```
模型响应中包含 tool_call
    ↓
run_agent.py agent loop
    ↓
model_tools.handle_function_call(name, args, task_id, user_task)
    ↓
[Agent-loop 工具？] → 由 agent loop 直接处理（todo、memory、session_search、delegate_task）
    ↓
[插件前置钩子] → invoke_hook("pre_tool_call", ...)
    ↓
registry.dispatch(name, args, **kwargs)
    ↓
按名称查找 ToolEntry
    ↓
[异步处理器？] → 通过 _run_async() 桥接
[同步处理器？]  → 直接调用
    ↓
返回结果字符串（或 JSON 错误）
    ↓
[插件后置钩子] → invoke_hook("post_tool_call", ...)
```
### 错误包装 {#error-wrapping}

所有工具执行都在两个层级上进行了错误处理包装：

1. **`registry.dispatch()`** — 捕获处理程序抛出的任何异常，并以 JSON 格式返回 `{"error": "Tool execution failed: ExceptionType: message"}`。

2. **`handle_function_call()`** — 将整个调度过程包裹在第二层 try/except 中，返回 `{"error": "Error executing tool_name: message"}`。

这确保了模型始终收到格式正确的 JSON 字符串，而不会遇到未处理的异常。

### Agent 循环工具 {#agent-loop-tools}

有四个工具在注册表调度之前被拦截，因为它们需要 Agent 级别的状态（TodoStore、MemoryStore 等）：

- `todo` — 规划/任务跟踪
- `memory` — 持久化内存写入
- `session_search` — 跨会话回忆
- `delegate_task` — 生成子 Agent 会话

这些工具的 schema 仍然注册在注册表中（用于 `get_tool_definitions`），但如果调度直接到达它们，它们的处理程序会返回一个存根错误。

### 异步桥接 {#async-bridging}

当工具处理程序是异步时，`_run_async()` 将其桥接到同步调度路径：

- **CLI 路径（无运行中的事件循环）** — 使用持久化事件循环来保持缓存的异步客户端存活
- **Gateway 路径（有运行中的事件循环）** — 使用 `asyncio.run()` 启动一个一次性线程
- **工作线程（并行工具）** — 使用线程本地存储中存储的每线程持久化循环

## DANGEROUS_PATTERNS 审批流程 {#the-dangerouspatterns-approval-flow}

终端工具集成了一个危险命令审批系统，定义在 `tools/approval.py` 中：

1. **模式检测** — `DANGEROUS_PATTERNS` 是一个 `(regex, description)` 元组列表，覆盖破坏性操作：
   - 递归删除（`rm -rf`）
   - 文件系统格式化（`mkfs`、`dd`）
   - SQL 破坏性操作（`DROP TABLE`、不带 `WHERE` 的 `DELETE FROM`）
   - 系统配置覆盖（`> /etc/`）
   - 服务操作（`systemctl stop`）
   - 远程代码执行（`curl | sh`）
   - Fork 炸弹、进程杀死等

2. **检测** — 在执行任何终端命令之前，`detect_dangerous_command(command)` 会检查所有模式。

3. **审批提示** — 如果匹配到：
   - **CLI 模式** — 交互式提示要求用户批准、拒绝或永久允许
   - **Gateway 模式** — 异步审批回调将请求发送到消息平台
   - **智能审批** — 可选地，辅助 LLM 可以自动批准匹配模式但风险较低的命令（例如 `rm -rf node_modules/` 是安全的，但匹配“递归删除”）

4. **会话状态** — 审批按会话跟踪。一旦你批准了某个会话的“递归删除”，后续的 `rm -rf` 命令不会再次提示。

5. **永久允许列表** — “永久允许”选项将模式写入 `config.yaml` 的 `command_allowlist`，跨会话持久化。

## 终端/运行时环境 {#terminal-runtime-environments}

终端系统支持多种后端：

- local
- docker
- ssh
- singularity
- modal
- daytona
- vercel_sandbox

它还支持：

- 每个任务的 cwd 覆盖
- 后台进程管理
- PTY 模式
- 危险命令的审批回调
## 并发 {#concurrency}

工具调用可以顺序执行或并发执行，具体取决于工具组合和交互需求。

## 相关文档 {#related-docs}

- [工具集参考](../reference/toolsets-reference.md)
- [内置工具参考](../reference/tools-reference.md)
- [Agent 循环内部机制](./agent-loop.md)
- [ACP 内部机制](./acp-internals.md)
