---
sidebar_position: 9
title: "工具运行时"
description: "工具注册表、工具集、分发和终端环境的运行时行为"
---

# 工具运行时

Hermes 工具是自注册的函数，它们被分组到工具集中，并通过一个中央注册表/分发系统执行。

主要文件：

- `tools/registry.py`
- `model_tools.py`
- `toolsets.py`
- `tools/terminal_tool.py`
- `tools/environments/*`

## 工具注册模型

每个工具模块在导入时都会调用 `registry.register(...)`。

`model_tools.py` 负责导入/发现工具模块，并构建模型使用的模式列表。

### `registry.register()` 的工作原理

`tools/` 目录下的每个工具文件都在模块级别调用 `registry.register()` 来声明自身。函数签名如下：

```python
registry.register(
    name="terminal",               # 唯一的工具名称（用于 API 模式）
    toolset="terminal",            # 此工具所属的工具集
    schema={...},                  # OpenAI 函数调用模式（描述、参数）
    handler=handle_terminal,       # 调用工具时执行的函数
    check_fn=check_terminal,       # 可选：返回 True/False 表示可用性
    requires_env=["SOME_VAR"],     # 可选：所需的环境变量（用于 UI 显示）
    is_async=False,                # 处理程序是否为异步协程
    description="运行命令",        # 人类可读的描述
    emoji="💻",                    # 用于微调器/进度显示的 emoji
)
```

每次调用都会创建一个 `ToolEntry`，存储在单例 `ToolRegistry._tools` 字典中，以工具名称为键。如果不同工具集之间发生名称冲突，会记录警告，后注册的覆盖先注册的。

### 发现：`_discover_tools()`

当 `model_tools.py` 被导入时，它会调用 `_discover_tools()`，该函数按顺序导入每个工具模块：

```python
_modules = [
    "tools.web_tools",
    "tools.terminal_tool",
    "tools.file_tools",
    "tools.vision_tools",
    "tools.mixture_of_agents_tool",
    "tools.image_generation_tool",
    "tools.skills_tool",
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
    "tools.honcho_tools",
    "tools.homeassistant_tool",
]
```

每次导入都会触发模块的 `registry.register()` 调用。可选工具中的错误（例如，图像生成缺少 `fal_client`）会被捕获并记录——它们不会阻止其他工具加载。

核心工具发现之后，还会发现 MCP 工具和插件工具：

1.  **MCP 工具** — `tools.mcp_tool.discover_mcp_tools()` 读取 MCP 服务器配置，并从外部服务器注册工具。
2.  **插件工具** — `hermes_cli.plugins.discover_plugins()` 加载用户/项目/pip 插件，这些插件可能会注册额外的工具。

## 工具可用性检查 (`check_fn`)

每个工具可以选择性地提供一个 `check_fn` —— 一个可调用对象，当工具可用时返回 `True`，否则返回 `False`。典型的检查包括：

-   **API 密钥存在** — 例如，对于网络搜索：`lambda: bool(os.environ.get("SERP_API_KEY"))`
-   **服务正在运行** — 例如，检查 Honcho 服务器是否已配置
-   **二进制文件已安装** — 例如，验证 `playwright` 是否可用于浏览器工具

当 `registry.get_definitions()` 为模型构建模式列表时，它会运行每个工具的 `check_fn()`：

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

-   检查结果**按调用缓存** —— 如果多个工具共享同一个 `check_fn`，它只运行一次。
-   `check_fn()` 中的异常被视为“不可用”（故障安全）。
-   `is_toolset_available()` 方法检查工具集的 `check_fn` 是否通过，用于 UI 显示和工具集解析。

## 工具集解析

工具集是命名的工具包。Hermes 通过以下方式解析它们：

-   显式启用/禁用的工具集列表
-   平台预设（`hermes-cli`、`hermes-telegram` 等）
-   动态 MCP 工具集
-   精心策划的特殊用途集合，如 `hermes-acp`

### `get_tool_definitions()` 如何过滤工具

主要入口点是 `model_tools.get_tool_definitions(enabled_toolsets, disabled_toolsets, quiet_mode)`：

1.  **如果提供了 `enabled_toolsets`** —— 只包含来自这些工具集的工具。每个工具集名称通过 `resolve_toolset()` 解析，该函数将复合工具集扩展为单个工具名称。

2.  **如果提供了 `disabled_toolsets`** —— 从所有工具集开始，然后减去禁用的那些。

3.  **如果两者都未提供** —— 包含所有已知工具集。

4.  **注册表过滤** —— 解析后的工具名称集合传递给 `registry.get_definitions()`，该函数应用 `check_fn` 过滤并返回 OpenAI 格式的模式。

5.  **动态模式修补** —— 过滤之后，`execute_code` 和 `browser_navigate` 模式会被动态调整，仅引用实际通过过滤的工具（防止模型对不可用工具产生幻觉）。

### 遗留工具集名称

带有 `_tools` 后缀的旧工具集名称（例如 `web_tools`、`terminal_tools`）通过 `_LEGACY_TOOLSET_MAP` 映射到其现代工具名称，以保持向后兼容性。

## 分发

在运行时，工具通过中央注册表分发，但某些 Agent 级别的工具（如内存/待办事项/会话搜索处理）存在 Agent 循环例外。

### 分发流程：模型 tool_call → 处理程序执行

当模型返回一个 `tool_call` 时，流程如下：

```
模型响应附带 tool_call
    ↓
run_agent.py agent 循环
    ↓
model_tools.handle_function_call(name, args, task_id, user_task)
    ↓
[Agent 循环工具？] → 由 agent 循环直接处理 (todo, memory, session_search, delegate_task)
    ↓
[插件前置钩子] → invoke_hook("pre_tool_call", ...)
    ↓
registry.dispatch(name, args, **kwargs)
    ↓
按名称查找 ToolEntry
    ↓
[异步处理程序？] → 通过 _run_async() 桥接
[同步处理程序？] → 直接调用
    ↓
返回结果字符串（或 JSON 错误）
    ↓
[插件后置钩子] → invoke_hook("post_tool_call", ...)
```

### 错误包装

所有工具执行都在两个级别上进行了错误处理包装：

1.  **`registry.dispatch()`** —— 捕获来自处理程序的任何异常，并返回 `{"error": "Tool execution failed: ExceptionType: message"}` 作为 JSON。

2.  **`handle_function_call()`** —— 将整个分发包装在第二个 try/except 中，返回 `{"error": "Error executing tool_name: message"}`。

这确保了模型始终接收到格式良好的 JSON 字符串，而不是未处理的异常。

### Agent 循环工具

有四个工具在注册表分发之前被拦截，因为它们需要 Agent 级别的状态（TodoStore、MemoryStore 等）：

-   `todo` —— 计划/任务跟踪
-   `memory` —— 持久化内存写入
-   `session_search` —— 跨会话召回
-   `delegate_task` —— 生成子 Agent 会话

这些工具的模式仍然在注册表中注册（用于 `get_tool_definitions`），但如果分发以某种方式直接到达它们，它们的处理程序会返回一个存根错误。

### 异步桥接

当工具处理程序是异步时，`_run_async()` 将其桥接到同步分发路径：

-   **CLI 路径（无运行循环）** —— 使用持久事件循环来保持缓存的异步客户端存活
-   **网关路径（运行循环）** —— 使用 `asyncio.run()` 启动一个一次性线程
-   **工作线程（并行工具）** —— 使用存储在线程本地存储中的每个线程的持久循环

## DANGEROUS_PATTERNS 审批流程

终端工具集成了 `tools/approval.py` 中定义的危险命令审批系统：

1.  **模式检测** —— `DANGEROUS_PATTERNS` 是一个 `(regex, description)` 元组列表，涵盖破坏性操作：
    -   递归删除 (`rm -rf`)
    -   文件系统格式化 (`mkfs`, `dd`)
    -   SQL 破坏性操作 (`DROP TABLE`, 不带 `WHERE` 的 `DELETE FROM`)
    -   系统配置覆盖 (`> /etc/`)
    -   服务操作 (`systemctl stop`)
    -   远程代码执行 (`curl | sh`)
    -   Fork 炸弹、进程终止等。
2. **检测** — 在执行任何终端命令之前，`detect_dangerous_command(command)` 会对照所有模式进行检查。

3. **批准提示** — 如果发现匹配：
   - **CLI 模式** — 一个交互式提示会询问用户是批准、拒绝还是永久允许
   - **Gateway 模式** — 一个异步批准回调会将请求发送到消息平台
   - **智能批准** — 可选地，一个辅助 LLM 可以自动批准符合模式的低风险命令（例如 `rm -rf node_modules/` 是安全的，但匹配了“递归删除”模式）

4. **会话状态** — 批准是按会话追踪的。一旦你在某个会话中批准了“递归删除”，后续的 `rm -rf` 命令就不会再次提示。

5. **永久允许列表** — “永久允许”选项会将模式写入 `config.yaml` 的 `command_allowlist`，并跨会话持久化。

## 终端/运行时环境

终端系统支持多种后端：

- 本地
- docker
- ssh
- singularity
- modal
- daytona

它还支持：

- 每个任务的 cwd 覆盖
- 后台进程管理
- PTY 模式
- 危险命令的批准回调

## 并发

工具调用可能会顺序执行或并发执行，这取决于工具组合和交互需求。

## 相关文档

- [工具集参考](../reference/toolsets-reference.md)
- [内置工具参考](../reference/tools-reference.md)
- [Agent 循环内部机制](./agent-loop.md)
- [ACP 内部机制](./acp-internals.md)
