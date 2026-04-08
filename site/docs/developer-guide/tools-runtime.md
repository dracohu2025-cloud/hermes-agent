---
sidebar_position: 9
title: "工具运行时 (Tools Runtime)"
description: "工具注册表、工具集、调度以及终端环境的运行时行为"
---

# 工具运行时 (Tools Runtime)

Hermes 工具是自注册的函数，按工具集（toolsets）分组，并通过中央注册/调度系统执行。

核心文件：

- `tools/registry.py`
- `model_tools.py`
- `toolsets.py`
- `tools/terminal_tool.py`
- `tools/environments/*`

## 工具注册模型

每个工具模块在导入时都会调用 `registry.register(...)`。

`model_tools.py` 负责导入/发现工具模块，并构建模型使用的 schema 列表。

### `registry.register()` 的工作原理

`tools/` 目录下的每个工具文件都会在模块层级调用 `registry.register()` 来声明自己。函数签名如下：

```python
registry.register(
    name="terminal",               # 唯一的工具名称（用于 API schemas）
    toolset="terminal",            # 该工具所属的工具集
    schema={...},                  # OpenAI 函数调用 schema（描述、参数）
    handler=handle_terminal,       # 工具被调用时执行的函数
    check_fn=check_terminal,       # 可选：返回 True/False 表示可用性
    requires_env=["SOME_VAR"],     # 可选：所需的环境变量（用于 UI 显示）
    is_async=False,                # handler 是否为异步协程
    description="Run commands",    # 人类可读的描述
    emoji="💻",                    # 用于 spinner/进度显示的表情符号
)
```

每次调用都会创建一个 `ToolEntry`，并存储在单例 `ToolRegistry._tools` 字典中，以工具名称作为键。如果跨工具集发生名称冲突，系统会记录警告，并以较晚注册的为准。

### 发现机制：`_discover_tools()`

当 `model_tools.py` 被导入时，它会调用 `_discover_tools()`，按顺序导入每个工具模块：

```python
_modules = [
    "tools.web_tools",
    "tools.terminal_tool",
    "tools.file_tools",
    "tools.vision_tools",
    "tools.mixture_of_agents_tool",
    "tools.image_generation_tool",
    "tools.skills_tool",
    "tools.skill_manager_tool",
    "tools.browser_tool",
    "tools.cronjob_tools",
    "tools.rl_training_tool",
    "tools.tts_tool",
    "tools.todo_tool",
    "tools.memory_tool",
    "tools.session_search_tool",
    "tools.clarify_tool",
    "tools.code_execution_tool",
    "tools.delegate_tool",
    "tools.process_registry",
    "tools.send_message_tool",
    # "tools.honcho_tools",  # 已移除 — Honcho 现在是 memory provider 插件
    "tools.homeassistant_tool",
]
```

每次导入都会触发该模块的 `registry.register()` 调用。可选工具中的错误（例如，图像生成缺少 `fal_client`）会被捕获并记录日志，不会阻止其他工具的加载。

在核心工具发现之后，MCP 工具和插件工具也会被发现：

1. **MCP 工具** — `tools.mcp_tool.discover_mcp_tools()` 读取 MCP 服务器配置并注册来自外部服务器的工具。
2. **插件工具** — `hermes_cli.plugins.discover_plugins()` 加载可能注册额外工具的用户/项目/pip 插件。

## 工具可用性检查 (`check_fn`)

每个工具都可以选择提供一个 `check_fn` —— 一个在工具可用时返回 `True`，否则返回 `False` 的可调用对象。典型的检查包括：

- **API 密钥是否存在** — 例如，网页搜索的 `lambda: bool(os.environ.get("SERP_API_KEY"))`
- **服务是否运行** — 例如，检查 Honcho 服务器是否已配置
- **二进制文件是否安装** — 例如，验证浏览器工具所需的 `playwright` 是否可用

当 `registry.get_definitions()` 为模型构建 schema 列表时，它会运行每个工具的 `check_fn()`：

```python
# 简化自 registry.py
if entry.check_fn:
    try:
        available = bool(entry.check_fn())
    except Exception:
        available = False   # 异常 = 不可用
    if not available:
        continue            # 完全跳过此工具
```

关键行为：
- 检查结果会**按调用进行缓存** — 如果多个工具共享同一个 `check_fn`，它只运行一次。
- `check_fn()` 中的异常被视为“不可用”（故障安全）。
- `is_toolset_available()` 方法检查工具集的 `check_fn` 是否通过，用于 UI 显示和工具集解析。

## 工具集解析

工具集是命名的工具捆绑包。Hermes 通过以下方式解析它们：

- 显式的启用/禁用工具集列表
- 平台预设（`hermes-cli`、`hermes-telegram` 等）
- 动态 MCP 工具集
- 精选的特殊用途集合，如 `hermes-acp`

### `get_tool_definitions()` 如何过滤工具

主要入口点是 `model_tools.get_tool_definitions(enabled_toolsets, disabled_toolsets, quiet_mode)`：

1. **如果提供了 `enabled_toolsets`** — 仅包含来自这些工具集的工具。每个工具集名称通过 `resolve_toolset()` 解析，该函数将复合工具集展开为单个工具名称。

2. **如果提供了 `disabled_toolsets`** — 从所有工具集开始，然后减去禁用的工具集。

3. **如果两者都未提供** — 包含所有已知的工具集。

4. **注册表过滤** — 解析后的工具名称集合被传递给 `registry.get_definitions()`，后者应用 `check_fn` 过滤并返回 OpenAI 格式的 schemas。

5. **动态 Schema 补丁** — 过滤后，`execute_code` 和 `browser_navigate` 的 schemas 会被动态调整，仅引用实际通过过滤的工具（防止模型对不可用工具产生幻觉）。

### 遗留工具集名称

带有 `_tools` 后缀的旧工具集名称（例如 `web_tools`、`terminal_tools`）通过 `_LEGACY_TOOLSET_MAP` 映射到现代工具名称，以保持向后兼容性。

## 调度 (Dispatch)

在运行时，工具通过中央注册表进行调度，但某些 Agent 级别的工具（如 memory/todo/session-search 处理）在 Agent 循环中会有例外处理。

### 调度流程：模型 tool_call → handler 执行

当模型返回 `tool_call` 时，流程如下：

```
模型响应包含 tool_call
    ↓
run_agent.py agent loop
    ↓
model_tools.handle_function_call(name, args, task_id, user_task)
    ↓
[Agent-loop 工具?] → 由 agent loop 直接处理 (todo, memory, session_search, delegate_task)
    ↓
[插件 pre-hook] → 调用 invoke_hook("pre_tool_call", ...)
    ↓
registry.dispatch(name, args, **kwargs)
    ↓
按名称查找 ToolEntry
    ↓
[异步 handler?] → 通过 _run_async() 桥接
[同步 handler?]  → 直接调用
    ↓
返回结果字符串 (或 JSON 错误)
    ↓
[插件 post-hook] → 调用 invoke_hook("post_tool_call", ...)
```

### 错误封装

所有工具执行都在两个层级进行错误处理封装：

1. **`registry.dispatch()`** — 捕获 handler 抛出的任何异常，并以 JSON 形式返回 `{"error": "Tool execution failed: ExceptionType: message"}`。

2. **`handle_function_call()`** — 将整个调度封装在二次 try/except 中，返回 `{"error": "Error executing tool_name: message"}`。

这确保了模型始终收到格式良好的 JSON 字符串，而不会收到未处理的异常。

### Agent-loop 工具

有四个工具在进入注册表调度之前会被拦截，因为它们需要 Agent 级别的状态（TodoStore、MemoryStore 等）：

- `todo` — 规划/任务跟踪
- `memory` — 持久化记忆写入
- `session_search` — 跨会话召回
- `delegate_task` — 启动 sub-agent 会话

这些工具的 schema 仍然在注册表中注册（用于 `get_tool_definitions`），但如果调度意外地直接到达它们，它们的 handler 会返回一个存根错误。

### 异步桥接

当工具 handler 是异步的时，`_run_async()` 会将其桥接到同步调度路径：

- **CLI 路径（无运行中的循环）** — 使用持久事件循环来保持缓存的异步客户端存活。
- **Gateway 路径（有运行中的循环）** — 使用 `asyncio.run()` 启动一个临时线程。
- **工作线程（并行工具）** — 使用存储在线程本地存储（thread-local storage）中的每线程持久循环。

## DANGEROUS_PATTERNS 审批流

终端工具集成了在 `tools/approval.py` 中定义的危险命令审批系统：

1. **模式检测** — `DANGEROUS_PATTERNS` 是一个 `(regex, description)` 元组列表，涵盖了破坏性操作：
   - 递归删除 (`rm -rf`)
   - 文件系统格式化 (`mkfs`, `dd`)
   - SQL 破坏性操作 (`DROP TABLE`, `DELETE FROM` 且不带 `WHERE`)
   - 系统配置覆盖 (`> /etc/`)
   - 服务操作 (`systemctl stop`)
   - 远程代码执行 (`curl | sh`)
   - Fork 炸弹、进程杀除等。
2. **检测** — 在执行任何终端命令之前，`detect_dangerous_command(command)` 会根据所有模式进行检查。

3. **审批提示** — 如果发现匹配项：
   - **CLI 模式** — 交互式提示符会询问用户批准、拒绝或永久允许。
   - **Gateway 模式** — 异步审批回调会将请求发送到消息平台。
   - **智能审批** — 可选功能，辅助 LLM 可以自动批准匹配模式但低风险的命令（例如，`rm -rf node_modules/` 是安全的，但它匹配“递归删除”模式）。

4. **会话状态** — 审批按会话进行跟踪。一旦你在某个会话中批准了“递归删除”，后续的 `rm -rf` 命令将不再重复提示。

5. **永久白名单** — “永久允许”选项会将模式写入 `config.yaml` 的 `command_allowlist` 中，从而跨会话持久化。

## 终端/运行时环境

终端系统支持多种后端：

- local
- docker
- ssh
- singularity
- modal
- daytona

它还支持：

- 针对每个任务的 cwd（当前工作目录）覆盖
- 后台进程管理
- PTY 模式
- 危险命令的审批回调

## 并发

根据工具组合和交互需求，工具调用可以顺序执行或并发执行。

## 相关文档

- [工具集参考](../reference/toolsets-reference.md)
- [内置工具参考](../reference/tools-reference.md)
- [Agent Loop 内部原理](./agent-loop.md)
- [ACP 内部原理](./acp-internals.md)
