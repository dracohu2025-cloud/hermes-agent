---
sidebar_position: 7
title: "子Agent委派"
description: "通过 delegate_task 生成隔离的子Agent，用于并行工作流"
---

# 子Agent委派 {#subagent-delegation}

`delegate_task` 工具会生成独立的子 AIAgent 实例，每个实例拥有隔离的上下文、受限的工具集以及自己的终端会话。每个子 Agent 获得全新的对话并独立工作——只有其最终摘要会进入父 Agent 的上下文。

## 单个任务 {#single-task}

```python
delegate_task(
    goal="Debug why tests fail",
    context="Error: assertion in test_foo.py line 42",
    toolsets=["terminal", "file"]
)
```

## 并行批量 {#parallel-batch}

默认最多 3 个并发子 Agent（可配置，无硬上限）：

```python
delegate_task(tasks=[
    {"goal": "Research topic A", "toolsets": ["web"]},
    {"goal": "Research topic B", "toolsets": ["web"]},
    {"goal": "Fix the build", "toolsets": ["terminal", "file"]}
])
```

## 子Agent上下文如何工作 {#how-subagent-context-works}

:::warning 关键：子Agent一无所知
子Agent从**完全全新的对话**开始。它们对父 Agent 的对话历史、之前的工具调用或委派前讨论的任何内容一无所知。子Agent的唯一上下文来自父 Agent 在调用 `delegate_task` 时填充的 `goal` 和 `context` 字段。
:::
<a id="critical-subagents-know-nothing"></a>

这意味着父 Agent 必须在调用中传递子 Agent 所需的**所有内容**：

```python
# 不好 - 子Agent不知道"那个错误"是什么
delegate_task(goal="Fix the error")

# 好 - 子Agent拥有所需的所有上下文
delegate_task(
    goal="Fix the TypeError in api/handlers.py",
    context="""The file api/handlers.py has a TypeError on line 47:
    'NoneType' object has no attribute 'get'.
    The function process_request() receives a dict from parse_body(),
    but parse_body() returns None when Content-Type is missing.
    The project is at /home/user/myproject and uses Python 3.11."""
)
```

子Agent会收到一个聚焦的系统提示，该提示由你的 goal 和 context 构建而成，指示它完成任务并提供结构化摘要，说明它做了什么、发现了什么、修改了哪些文件以及遇到了哪些问题。

## 实际示例 {#practical-examples}

### 并行研究 {#parallel-research}

同时研究多个主题并收集摘要：

```python
delegate_task(tasks=[
    {
        "goal": "Research the current state of WebAssembly in 2025",
        "context": "Focus on: browser support, non-browser runtimes, language support",
        "toolsets": ["web"]
    },
    {
        "goal": "Research the current state of RISC-V adoption in 2025",
        "context": "Focus on: server chips, embedded systems, software ecosystem",
        "toolsets": ["web"]
    },
    {
        "goal": "Research quantum computing progress in 2025",
        "context": "Focus on: error correction breakthroughs, practical applications, key players",
        "toolsets": ["web"]
    }
])
```

### 代码审查 + 修复 {#code-review-fix}

将审查与修复工作流委派给全新的上下文：

```python
delegate_task(
    goal="Review the authentication module for security issues and fix any found",
    context="""Project at /home/user/webapp.
    Auth module files: src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py.
    The project uses Flask, PyJWT, and bcrypt.
    Focus on: SQL injection, JWT validation, password handling, session management.
    Fix any issues found and run the test suite (pytest tests/auth/).""",
    toolsets=["terminal", "file"]
)
```
### 多文件重构 {#multi-file-refactoring}

将可能撑爆父级上下文的大型重构任务委托出去：

```python
delegate_task(
    goal="将 src/ 下所有 Python 文件中的 print() 替换为合适的日志记录",
    context="""项目位于 /home/user/myproject。
    使用 'logging' 模块，logger = logging.getLogger(__name__)。
    将 print() 调用替换为对应的日志级别：
    - print(f"Error: ...") -> logger.error(...)
    - print(f"Warning: ...") -> logger.warning(...)
    - print(f"Debug: ...") -> logger.debug(...)
    - 其他 print -> logger.info(...)
    不要修改测试文件或 CLI 输出中的 print()。
    完成后运行 pytest 确保一切正常。""",
    toolsets=["terminal", "file"]
)
```

## 批量模式详情 {#batch-mode-details}

当你提供 `tasks` 数组时，子 Agent 会使用线程池**并行**运行：

- **最大并发数：** 默认 3 个任务（可通过 `delegation.max_concurrent_children` 或环境变量 `DELEGATION_MAX_CONCURRENT_CHILDREN` 配置；最小值为 1，无硬性上限）。超过限制的批次会返回工具错误，而不会静默截断。
- **线程池：** 使用 `ThreadPoolExecutor`，最大工作线程数等于配置的并发限制。
- **进度显示：** 在 CLI 模式下，树形视图会实时显示每个子 Agent 的工具调用，并附带每个任务的完成行。在网关模式下，进度会分批传递给父级的进度回调。
- **结果排序：** 结果按任务索引排序，以匹配输入顺序，无论完成顺序如何。
- **中断传播：** 中断父级（例如发送新消息）会中断所有活跃的子级。

单任务委托直接运行，没有线程池开销。

## 模型覆盖 {#model-override}

你可以通过 `config.yaml` 为子 Agent 配置不同的模型——适用于将简单任务委托给更便宜/更快的模型：

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  model: "google/gemini-flash-2.0"    # 子 Agent 使用更便宜的模型
  provider: "openrouter"              # 可选：将子 Agent 路由到不同的提供商
```

如果省略，子 Agent 将使用与父级相同的模型。

## 工具集选择建议 {#toolset-selection-tips}

`toolsets` 参数控制子 Agent 可以访问哪些工具。根据任务选择：

| 工具集模式 | 使用场景 |
|----------------|----------|
| `["terminal", "file"]` | 代码工作、调试、文件编辑、构建 |
| `["web"]` | 研究、事实核查、文档查阅 |
| `["terminal", "file", "web"]` | 全栈任务（默认） |
| `["file"]` | 只读分析、无需执行的代码审查 |
| `["terminal"]` | 系统管理、进程管理 |

无论你指定什么，某些工具集对子 Agent 是禁止的：
- `delegation` — 对叶子子 Agent 禁止（默认）。对于 `role="orchestrator"` 的子级保留，受 `max_spawn_depth` 限制——请参阅下面的[深度限制与嵌套编排](#depth-limit-and-nested-orchestration)。
- `clarify` — 子 Agent 不能与用户交互
- `memory` — 不能写入共享持久内存
- `code_execution` — 子级应逐步推理
- `send_message` — 不能产生跨平台副作用（例如发送 Telegram 消息）
## 最大迭代次数 {#max-iterations}

每个子 Agent 都有一个迭代次数限制（默认值：50），用于控制它可以执行多少轮工具调用：

```python
delegate_task(
    goal="Quick file check",
    context="Check if /etc/nginx/nginx.conf exists and print its first 10 lines",
    max_iterations=10  # 简单任务，不需要太多轮次
)
```

## 子任务超时 {#child-timeout}

如果子 Agent 在 `delegation.child_timeout_seconds` 配置的墙上时钟秒数内没有动静，就会被视为卡死并终止。默认值为 **600**（10 分钟）——相比早期版本的 300 秒有所增加，因为高推理模型在复杂研究任务时，可能会在思考中途被杀死。你可以按需调整：

```yaml
delegation:
  child_timeout_seconds: 600   # 默认值
```

对于快速的本地模型可以降低该值；对于处理难题的慢速推理模型可以调高。每次子任务发起 API 调用或工具调用时，计时器都会重置——只有真正空闲的工作者才会触发终止。

:::tip 零调用超时时的诊断转储
如果子 Agent 在 **零** API 调用的情况下超时（通常是：提供者不可达、认证失败或工具模式被拒绝），`delegate_task` 会向 `~/.hermes/logs/subagent-timeout-<会话ID>-<时间戳>.log` 写入一份结构化诊断信息，其中包含子 Agent 的配置快照、凭据解析轨迹以及任何早期错误消息。相比之前静默超时的行为，这更容易定位根因。
<a id="diagnostic-dump-on-zero-call-timeout"></a>
:::

## 监控运行中的子 Agent（`/agents`） {#monitoring-running-subagents-agents}

TUI 提供了一个 `/agents` 覆盖页面（别名 `/tasks`），将递归的 `delegate_task` 扇出行为转化为一流的审计界面：

- 运行中和刚完成的子 Agent 的实时树状视图，按父级分组
- 每个分支的成本、令牌数和访问文件汇总
- 终止和暂停控制——可以在飞行途中取消某个特定子 Agent，而不影响其兄弟任务
- 事后审查：即使在子 Agent 返回父级后，仍可逐步查看每个子 Agent 的逐轮历史记录

经典 CLI 只会将 `/agents` 打印为文本摘要；TUI 才是该覆盖大放异彩的地方。请参见 [TUI — 斜杠命令](/user-guide/tui#slash-commands)。

## 深度限制与嵌套编排 {#depth-limit-and-nested-orchestration}

默认情况下，委派是 **扁平** 的：父级（深度 0）生成子级（深度 1），这些子级不能进一步委派。这可以防止失控的递归委派。

对于多阶段工作流（研究 → 综合，或针对子问题的并行编排），父级可以生成 **编排器** 子 Agent，这些子 Agent *可以* 委派自己的工人：

```python
delegate_task(
    goal="Survey three code review approaches and recommend one",
    role="orchestrator",  # 允许此子级生成自己的工人
    context="...",
)
```

- `role="leaf"`（默认）：子级不能进一步委派——与扁平委派行为相同。
- `role="orchestrator"`：子级保留 `delegation` 工具集。受 `delegation.max_spawn_depth` 限制（默认 **1** = 扁平，因此在默认设置下 `role="orchestrator"` 是无效的）。将 `max_spawn_depth` 提高到 2，以允许编排器子级生成叶子孙级；提高到 3 则允许三级（上限）。
- `delegation.orchestrator_enabled: false`：全局开关，强制所有子级变为 `leaf`，忽略 `role` 参数。
**费用警告：** 当 `max_spawn_depth: 3` 且 `max_concurrent_children: 3` 时，树形结构最多可达 3×3×3 = 27 个并发叶子 Agent。每增加一层，费用都会成倍增长——请有意地调高 `max_spawn_depth`。

## 生命周期与持久性 {#lifetime-and-durability}

:::warning delegate_task 是同步的——不具备持久性
`delegate_task` 在**父节点的当前轮次内**执行。它会阻塞父节点，直到所有子节点完成（或被取消）。它**不是**后台任务队列：

<a id="delegatetask-is-synchronous-not-durable"></a>
- 如果父节点被中断（用户发送新消息、`/stop`、`/new`），所有活跃的子节点都会被取消，并返回 `status="interrupted"`。它们正在进行的工作会被丢弃。
- 子节点在父节点轮次结束后**不会**继续运行。
- 被取消的子节点会返回结构化结果（`status="interrupted"`，`exit_reason="interrupted"`），但由于父节点也被中断了，该结果通常永远不会出现在用户可见的回复中。

对于需要抵御中断或超出当前轮次的**持久性长时间运行工作**，请使用：

- `cronjob`（`action=create`）——调度一个独立的 Agent 运行；不受父节点轮次中断的影响。
- `terminal(background=True, notify_on_complete=True)`——长时间运行的 shell 命令，Agent 在干其他事的同时，命令会继续运行。
:::

## 关键特性 {#key-properties}

- 每个子 Agent 拥有**自己的终端会话**（与父节点独立）
- **嵌套委托是自愿的**——只有 `role="orchestrator"` 的子节点才能进一步委托，并且只有当 `max_spawn_depth` 从默认值 1（扁平）调高时才行。可通过 `orchestrator_enabled: false` 全局禁用。
- 叶子子 Agent **不能**调用：`delegate_task`、`clarify`、`memory`、`send_message`、`execute_code`。Orchestrator 子 Agent 保留 `delegate_task`，但仍不能使用其他四个。
- **中断传播**——中断父节点会中断所有活跃的子节点（包括 orchestrator 下的孙节点）
- 只有最终的摘要会进入父节点的上下文，从而高效使用 tokens
- 子 Agent 继承父节点的 **API key、provider 配置和凭据池**（支持在速率限制时进行 key 轮换）

## Delegation 与 execute_code 对比 {#delegation-vs-executecode}

| 因素 | delegate_task | execute_code |
|------|---------------|--------------|
| **推理** | 完整的 LLM 推理循环 | 仅 Python 代码执行 |
| **上下文** | 全新的隔离对话 | 无对话，仅脚本 |
| **工具访问** | 所有未被阻止的工具，带推理 | 通过 RPC 的 7 个工具，无推理 |
| **并行性** | 默认 3 个并发子 Agent（可配置） | 单个脚本 |
| **最佳用途** | 需要判断的复杂任务 | 机械化的多步骤流程 |
| **Token 成本** | 较高（完整的 LLM 循环） | 较低（仅返回 stdout） |
| **用户交互** | 无（子 Agent 无法澄清） | 无 |

**经验法则：** 当子任务需要推理、判断或多步骤问题解决时，使用 `delegate_task`。当需要机械化的数据处理或脚本化工作流时，使用 `execute_code`。

## 配置 {#configuration}

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  max_iterations: 50                        # 每个子节点的最大轮次（默认：50）
  # max_concurrent_children: 3              # 每批并行子节点数（默认：3）
  # max_spawn_depth: 1                      # 树深度（1-3，默认 1 = 扁平）。设为 2 可允许 orchestrator 子节点生成叶子；设为 3 为三层。
  # orchestrator_enabled: true              # 设为 false 强制所有子节点为叶子角色。
  model: "google/gemini-3-flash-preview"             # 可选的 provider/model 覆盖
  provider: "openrouter"                             # 可选的内置 provider

# 或者使用直接的自定义端点替代 provider：
delegation:
  model: "qwen2.5-coder"
  base_url: "http://localhost:1234/v1"
  api_key: "local-key"
```
:::tip
Agent 会根据任务复杂度自动处理委托。你无需明确要求它进行委托——当有必要时，它会自行处理。
:::
