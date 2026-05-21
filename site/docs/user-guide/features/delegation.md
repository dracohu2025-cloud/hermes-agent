---
sidebar_position: 7
title: "子 Agent 委托"
description: "使用 delegate_task 生成隔离的子 Agent，用于并行工作流"
---

<a id="subagent-delegation"></a>
# 子 Agent 委托

`delegate_task` 工具会生成独立的子 AIAgent 实例，这些实例拥有隔离的上下文、受限的工具集以及各自的终端会话。每个子 Agent 都从一个全新的对话开始，独立工作——只有最终的摘要会进入父 Agent 的上下文。

<a id="single-task"></a>
## 单任务

```python
delegate_task(
    goal="Debug why tests fail",
    context="Error: assertion in test_foo.py line 42",
    toolsets=["terminal", "file"]
)
```

<a id="parallel-batch"></a>
## 并行批处理

默认最多同时运行 3 个子 Agent（可配置，无硬性上限）：

```python
delegate_task(tasks=[
    {"goal": "Research topic A", "toolsets": ["web"]},
    {"goal": "Research topic B", "toolsets": ["web"]},
    {"goal": "Fix the build", "toolsets": ["terminal", "file"]}
])
```

<a id="how-subagent-context-works"></a>
## 子 Agent 上下文的工作原理

:::warning 关键点：子 Agent 一无所知
子 Agent 从一个**完全全新的对话**开始。它们对父 Agent 的对话历史、之前的工具调用或委托前讨论的任何内容都毫不知情。子 Agent 的唯一上下文来自父 Agent 在调用 `delegate_task` 时填入的 `goal` 和 `context` 字段。
:::
<a id="critical-subagents-know-nothing"></a>

这意味着父 Agent 必须将子 Agent 所需的**一切**都传给调用：

```python
# 不好——子 Agent 不知道“那个错误”是什么
delegate_task(goal="Fix the error")

# 好——子 Agent 拥有它需要的所有上下文
delegate_task(
    goal="Fix the TypeError in api/handlers.py",
    context="""文件 api/handlers.py 第 47 行有一个 TypeError：
    'NoneType' object has no attribute 'get'。
    函数 process_request() 从 parse_body() 接收到一个字典，
    但 parse_body() 在 Content-Type 缺失时返回 None。
    项目位于 /home/user/myproject，使用 Python 3.11。"""
)
```

子 Agent 会收到一个聚焦的系统提示，该提示由你的 goal 和 context 构建，指示它完成任务，并提供一个结构化的摘要，说明它做了什么、发现了什么、修改了哪些文件以及遇到了哪些问题。

<a id="practical-examples"></a>
## 实用示例

<a id="parallel-research"></a>
### 并行研究

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

<a id="code-review-fix"></a>
### 代码审查 + 修复

将审查和修复工作流委托给一个全新的上下文：

```python
delegate_task(
    goal="Review the authentication module for security issues and fix any found",
    context="""项目位于 /home/user/webapp。
    Auth 模块文件：src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py。
    项目使用 Flask、PyJWT 和 bcrypt。
    重点关注：SQL 注入、JWT 验证、密码处理、会话管理。
    修复发现的任何问题并运行测试套件（pytest tests/auth/）。""",
    toolsets=["terminal", "file"]
)
```
<a id="multi-file-refactoring"></a>
### 多文件重构

将大型重构任务委托给子 Agent，避免撑爆父 Agent 的上下文：

```python
delegate_task(
    goal="重构 src/ 下所有 Python 文件，用适当的日志记录替换 print()",
    context="""项目位于 /home/user/myproject。
    使用 'logging' 模块，logger = logging.getLogger(__name__)。
    用适当的日志级别替换 print() 调用：
    - print(f"Error: ...") -> logger.error(...)
    - print(f"Warning: ...") -> logger.warning(...)
    - print(f"Debug: ...") -> logger.debug(...)
    - 其他 print -> logger.info(...)
    不要修改测试文件或 CLI 输出中的 print()。
    运行 pytest 确保一切正常。""",
    toolsets=["terminal", "file"]
)
```

<a id="batch-mode-details"></a>
## 批处理模式详情

当你提供 `tasks` 数组时，多个子 Agent 会通过线程池**并行**运行：

- **最大并发数：** 默认 3 个任务（可通过 `delegation.max_concurrent_children` 配置项或 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量调整；最小值为 1，无硬性上限）。超过限制的批次会返回工具错误，而不是静默截断。
- **线程池：** 使用 `ThreadPoolExecutor`，以配置的并发限制作为最大工作线程数。
- **进度显示：** CLI 模式下，树状视图会实时显示每个子 Agent 的工具调用，并附带每个任务的完成行。网关模式下，进度会分批发送给父 Agent 的进度回调。
- **结果排序：** 结果按任务索引排序，以匹配输入顺序，与完成顺序无关。
- **中断传播：** 中断父 Agent（例如发送新消息）会中断所有活跃的子 Agent。

单任务委托直接运行，无线程池开销。

<a id="model-override"></a>
## 模型覆盖

你可以在 `config.yaml` 中为子 Agent 配置不同的模型——适用于将简单任务委托给更便宜、更快的模型：

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  model: "google/gemini-flash-2.0"    # 子 Agent 使用更便宜的模型
  provider: "openrouter"              # 可选：将子 Agent 路由到不同的提供商
```

如果省略，子 Agent 使用与父 Agent 相同的模型。

<a id="toolset-selection-tips"></a>
## 工具集选择技巧

`toolsets` 参数控制子 Agent 可使用的工具。根据任务进行选择：

| 工具集模式 | 使用场景 |
|----------------|----------|
| `["terminal", "file"]` | 代码工作、调试、文件编辑、构建 |
| `["web"]` | 研究、事实核查、查阅文档 |
| `["terminal", "file", "web"]` | 全栈任务（默认） |
| `["file"]` | 只读分析、不执行代码的代码审查 |
| `["terminal"]` | 系统管理、进程管理 |

无论你指定什么，某些工具集对子 Agent 都会被阻止：
- `delegation` — 对叶子子 Agent 阻止（默认）。对于 `role="orchestrator"` 的子 Agent 保留，受 `max_spawn_depth` 限制——参见下面的[深度限制与嵌套编排](#depth-limit-and-nested-orchestration)。
- `clarify` — 子 Agent 无法与用户交互。
- `memory` — 不允许写入共享持久记忆。
- `code_execution` — 子 Agent 应逐步推理。
- `send_message` — 不允许跨平台副作用（例如发送 Telegram 消息）。
<a id="max-iterations"></a>
## 最大迭代次数 (Max Iterations)

每个子 Agent 都有迭代次数限制（默认：50），用于控制它可以进行的工具调用轮数：

```python
delegate_task(
    goal="Quick file check",
    context="Check if /etc/nginx/nginx.conf exists and print its first 10 lines",
    max_iterations=10  # Simple task, don't need many turns
)
```

<a id="child-timeout"></a>
## 子任务超时 (Child Timeout)

如果子 Agent 在超过 `delegation.child_timeout_seconds` 的挂钟秒数内没有响应，它会被当作停滞而杀死。默认值为 **600**（10分钟）——相比早期版本的 300 秒有所增加，因为高推理模型在处理非平凡研究任务时可能会在思考中途被杀死。可根据具体安装环境进行调整：

```yaml
delegation:
  child_timeout_seconds: 600   # default
```

对于快速本地模型，可以调低这个值；对于解决难题的慢速推理模型，可以调高。计时器会在子 Agent 每次进行 API 调用或工具调用时重置——只有真正空闲的工作者才会触发终止。

:::tip 零调用超时的诊断转储
如果一个子 Agent 在进行了**零次** API 调用的情况下超时（通常原因：提供者不可达、认证失败、或工具模式被拒绝），`delegate_task` 会向 `~/.hermes/logs/subagent-timeout-&lt;session&gt;-&lt;timestamp&gt;.log` 写入结构化的诊断信息，包含子 Agent 的配置快照、凭证解析追踪以及任何早期错误信息。相比之前静默超时的行为，这大大简化了根因分析。
<a id="diagnostic-dump-on-zero-call-timeout"></a>
:::

<a id="monitoring-running-subagents-agents"></a>
## 监控运行中的子 Agent (`/agents`)

TUI 提供了一个 `/agents` 覆盖层（别名 `/tasks`），将递归的 `delegate_task` 展开转化为一等审计界面：

- 分组在父级下的、正在运行的和最近完成的子 Agent 的实时树状视图
- 每个分支的成本、令牌和接触文件汇总
- 杀死和暂停控制——在不中断其他子任务的情况下中途取消特定子 Agent
- 事后审查：即使子 Agent 已返回父级，也可以逐步查看其每一轮的完整历史

经典 CLI 只是将 `/agents` 打印为文本摘要；覆盖层在 TUI 中才大放异彩。参见 [TUI — 斜杠命令](/user-guide/tui#slash-commands)。

<a id="depth-limit-and-nested-orchestration"></a>
## 深度限制与嵌套编排

默认情况下，委托是**扁平的**：父级（深度 0）生成子级（深度 1），而这些子级不能再进一步委托。这可以防止失控的递归委托。

对于多阶段工作流（研究 → 综合，或针对子问题的并行编排），父级可以生成**编排者**子 Agent，它们*可以*委托自己的工作者：

```python
delegate_task(
    goal="Survey three code review approaches and recommend one",
    role="orchestrator",  # 允许这个子 Agent 生成自己的工作者
    context="...",
)
```

- `role="leaf"`（默认）：子 Agent 不能再进一步委托——与扁平委托行为相同。
- `role="orchestrator"`：子 Agent 保留 `delegation` 工具集。受 `delegation.max_spawn_depth` 限制（默认 **1** = 扁平，因此 `role="orchestrator"` 在默认情况下不生效）。将 `max_spawn_depth` 提高到 2，可允许编排者子 Agent 生成叶子级孙 Agent；提高到 3 则开启三级深度（上限）。
- `delegation.orchestrator_enabled: false`：全局禁用开关，强制所有子 Agent 为 `leaf`，无论 `role` 参数如何设置。
**成本警告：** 当 `max_spawn_depth: 3` 且 `max_concurrent_children: 3` 时，树状结构最多可达 3×3×3 = 27 个并发叶子 Agent。每增加一层，开销都会成倍增长——请审慎调高 `max_spawn_depth`。

<a id="lifetime-and-durability"></a>
## 生命周期与持久性

:::warning delegate_task 是同步的，非持久性
`delegate_task` 在**父节点当前轮次**内运行。它会阻塞父节点，直到所有子节点完成（或被取消）。它**不是**后台任务队列：

<a id="delegatetask-is-synchronous-not-durable"></a>
- 如果父节点被中断（用户发送新消息、`/stop`、`/new`），所有活跃的子节点都会被取消，并返回 `status="interrupted"`。它们正在进行的工作将被丢弃。
- 子节点在父节点轮次结束后**不会**继续运行。
- 被取消的子节点会返回结构化结果（`status="interrupted"`，`exit_reason="interrupted"`），但由于父节点也已中断，该结果通常不会出现在用户可见的回复中。

对于**需要持久运行且能抵抗中断或超越当前轮次的长时工作**，请使用：

- `cronjob`（action=`create`）—— 调度一个独立的 Agent 运行；不受父节点轮次中断的影响。
- `terminal(background=True, notify_on_complete=True)` —— 后台运行的 shell 命令，在 Agent 执行其他任务时持续运行。
:::

<a id="key-properties"></a>
## 关键特性

- 每个子 Agent 拥有**独立的终端会话**（与父节点隔离）
- **嵌套委派为可选** —— 只有 `role="orchestrator"` 的子节点才能进一步委派，并且仅当 `max_spawn_depth` 从默认值 1（扁平）被调高时生效。可通过 `orchestrator_enabled: false` 全局禁用。
- 叶子子 Agent **不能**调用：`delegate_task`、`clarify`、`memory`、`send_message`、`execute_code`。Orchestrator 子 Agent 保留 `delegate_task`，但仍不能使用其他四个。
- **中断传播** —— 中断父节点会中断所有活跃的子节点（包括 orchestrator 下的孙节点）
- 只有最终摘要会进入父节点的上下文，从而高效使用 token
- 子 Agent 继承父节点的 **API 密钥、provider 配置和凭据池**（支持在限流时轮换密钥）

<a id="delegation-vs-executecode"></a>
## Delegation 与 execute_code 对比

| 因素 | delegate_task | execute_code |
|------|--------------|-------------|
| **推理能力** | 完整的 LLM 推理循环 | 仅 Python 代码执行 |
| **上下文** | 全新的独立对话 | 无对话，只有脚本 |
| **工具访问** | 所有未被阻止的工具，伴随推理 | 通过 RPC 使用 7 个工具，无推理 |
| **并行性** | 默认 3 个并发子 Agent（可配置） | 单个脚本 |
| **适用场景** | 需要判断的复杂任务 | 机械化的多步骤流水线 |
| **Token 成本** | 较高（完整的 LLM 循环） | 较低（仅返回 stdout） |
| **用户交互** | 无（子 Agent 无法澄清） | 无 |

**经验法则：** 当子任务需要推理、判断或多步骤问题解决时，使用 `delegate_task`。当需要机械化的数据处理或脚本化工作流时，使用 `execute_code`。

<a id="configuration"></a>
## 配置

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  max_iterations: 50                        # 每个子节点的最大轮次（默认：50）
  # max_concurrent_children: 3              # 每批并行子节点数（默认：3）
  # max_spawn_depth: 1                      # 树深度（1-3，默认 1 = 扁平）。设为 2 可允许 orchestrator 子节点生成叶子节点；设为 3 则为三层。
  # orchestrator_enabled: true              # 设为 false 可强制所有子节点为叶子角色。
  model: "google/gemini-3-flash-preview"             # 可选的 provider/模型覆盖
  provider: "openrouter"                             # 可选的内置 provider
  api_mode: anthropic_messages                       # 可选；对于 anthropic_messages 端点，会从 base_url 自动检测

# 或者使用直接的自定义端点替代 provider：
delegation:
  model: "qwen2.5-coder"
  base_url: "http://localhost:1234/v1"
  api_key: "local-key"
  # api_mode: "anthropic_messages"  # 可选。针对 base_url 的 Wire 协议覆盖（"chat_completions"、"codex_responses" 或 "anthropic_messages"）。留空 = 从 URL 自动检测（例如 /anthropic 后缀）。对于启发式方法无法分类的端点（Azure AI Foundry、MiniMax、智谱 GLM、LiteLLM 代理等），请显式设置。
```
当 `base_url` 指向一个兼容 Anthropic 的端点时——例如路径以 `/anthropic` 结尾、Azure Foundry Claude 路由或 MiniMax 的 `/anthropic` 代理——`api_mode` 会被自动检测为 `anthropic_messages`，因此子 Agent 无需你额外设置就能使用正确的传输格式。当自动检测结果有误时（这种情况很少见），请显式设置 `api_mode`。

:::tip
Agent 会根据任务复杂度自动处理委派。你无需明确要求它进行委派——它会在合适的时候自行决定。
:::
