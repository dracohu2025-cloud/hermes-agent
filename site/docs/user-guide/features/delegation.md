---
sidebar_position: 7
title: "Subagent 任务委派"
description: "使用 delegate_task 生成隔离的子 Agent 以处理并行工作流"
---

# Subagent 任务委派 {#subagent-delegation}

`delegate_task` 工具可以生成具有隔离上下文、受限工具集和独立终端会话的子 AIAgent 实例。每个子 Agent 都会开启一段全新的对话并独立工作 —— 只有其最终生成的总结会进入父 Agent 的上下文。

## 单个任务 {#single-task}

```python
delegate_task(
    goal="排查测试失败的原因",
    context="错误信息：test_foo.py 第 42 行断言失败",
    toolsets=["terminal", "file"]
)
```

## 并行批处理 {#parallel-batch}

最多支持 3 个并发运行的 Subagent：

```python
delegate_task(tasks=[
    {"goal": "研究主题 A", "toolsets": ["web"]},
    {"goal": "研究主题 B", "toolsets": ["web"]},
    {"goal": "修复构建错误", "toolsets": ["terminal", "file"]}
])
```

## Subagent 上下文工作原理 {#how-subagent-context-works}

:::warning 重要提示：Subagent 没有任何先验知识
Subagent 启动时使用的是**完全全新的对话**。它们对父 Agent 的对话历史、之前的工具调用或委派前讨论的任何内容一无所知。Subagent 唯一的上下文来源是你提供的 `goal` 和 `context` 字段。
:::

这意味着你必须传递 Subagent 所需的**所有信息**：

```python
# 错误做法 - Subagent 不知道“那个错误”是什么
delegate_task(goal="修复那个错误")

# 正确做法 - Subagent 拥有所需的全部上下文
delegate_task(
<a id="critical-subagents-know-nothing"></a>
    goal="修复 api/handlers.py 中的 TypeError",
    context="""文件 api/handlers.py 第 47 行出现 TypeError：
    'NoneType' object has no attribute 'get'。
    process_request() 函数从 parse_body() 接收一个字典，
    但当 Content-Type 缺失时，parse_body() 会返回 None。
    项目路径为 /home/user/myproject，使用 Python 3.11。"""
)
```

Subagent 会收到一个根据你的目标和上下文构建的专注型系统提示词，指示其完成任务并提供一份结构化的总结，内容包括：做了什么、发现了什么、修改了哪些文件以及遇到了哪些问题。

## 实际案例 {#practical-examples}

### 并行研究 {#parallel-research}

同时研究多个主题并收集总结：

```python
delegate_task(tasks=[
    {
        "goal": "研究 2025 年 WebAssembly 的现状",
        "context": "重点关注：浏览器支持、非浏览器运行时、语言支持",
        "toolsets": ["web"]
    },
    {
        "goal": "研究 2025 年 RISC-V 的采用现状",
        "context": "重点关注：服务器芯片、嵌入式系统、软件生态系统",
        "toolsets": ["web"]
    },
    {
        "goal": "研究 2025 年量子计算的进展",
        "context": "重点关注：纠错技术的突破、实际应用、主要参与者",
        "toolsets": ["web"]
    }
])
```

### 代码审查 + 修复 {#code-review-fix}

将“审查并修复”工作流委派给一个全新的上下文：

```python
delegate_task(
    goal="审查身份验证模块的安全问题并修复发现的任何漏洞",
    context="""项目路径：/home/user/webapp。
    认证模块文件：src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py。
    项目使用 Flask, PyJWT 和 bcrypt。
    重点关注：SQL 注入、JWT 验证、密码处理、会话管理。
    修复发现的所有问题并运行测试套件 (pytest tests/auth/)。""",
    toolsets=["terminal", "file"]
)
```

### 多文件重构 {#multi-file-refactoring}

委派一个大型重构任务，避免其产生的日志淹没父 Agent 的上下文：

```python
delegate_task(
    goal="重构 src/ 下的所有 Python 文件，将 print() 替换为正式的 logging",
    context="""项目路径：/home/user/myproject。
    使用 'logging' 模块，定义为 logger = logging.getLogger(__name__)。
    将 print() 调用替换为相应的日志级别：
    - print(f"Error: ...") -> logger.error(...)
    - print(f"Warning: ...") -> logger.warning(...)
    - print(f"Debug: ...") -> logger.debug(...)
    - 其他 print -> logger.info(...)
    不要更改测试文件或 CLI 输出中的 print()。
    完成后运行 pytest 以验证功能正常。""",
    toolsets=["terminal", "file"]
)
```

## 批处理模式详情 {#batch-mode-details}

当你提供 `tasks` 数组时，Subagent 会通过线程池**并行**运行：

- **最大并发数：** 3 个任务（如果数组更长，`tasks` 数组将被截断为 3 个）
- **线程池：** 使用 `ThreadPoolExecutor`，配置 `MAX_CONCURRENT_CHILDREN = 3` 个工作线程
- **进度显示：** 在 CLI 模式下，树状视图会实时显示每个 Subagent 的工具调用情况，并带有每个任务的完成状态行。在 Gateway 模式下，进度会被批量处理并转发给父 Agent 的进度回调函数
- **结果排序：** 结果按任务索引排序，以确保无论完成顺序如何，都能与输入顺序匹配
- **中断传播：** 中断父 Agent（例如发送新消息）会同时中断所有活跃的子 Agent

单任务委派直接运行，没有线程池开销。

## 模型覆盖 (Model Override) {#model-override}

你可以通过 `config.yaml` 为 Subagent 配置不同的模型 —— 这对于将简单任务委派给更便宜/更快的模型非常有用：

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  model: "google/gemini-flash-2.0"    # 为 Subagent 使用更便宜的模型
  provider: "openrouter"              # 可选：将 Subagent 路由到不同的供应商
```

如果省略此配置，Subagent 将使用与父 Agent 相同的模型。

## 工具集选择建议 {#toolset-selection-tips}

`toolsets` 参数控制 Subagent 可以访问哪些工具。请根据任务进行选择：

| 工具集模式 | 使用场景 |
|----------------|----------|
| `["terminal", "file"]` | 代码工作、调试、文件编辑、构建 |
| `["web"]` | 研究、事实核查、查阅文档 |
| `["terminal", "file", "web"]` | 全栈任务（默认） |
| `["file"]` | 只读分析、无需执行的代码审查 |
| `["terminal"]` | 系统管理、进程管理 |

无论你如何指定，某些工具集对 Subagent 始终是**屏蔽**的：
- `delegation` — 禁止递归委派（防止无限生成）
- `clarify` — Subagent 无法与用户交互
- `memory` — 禁止写入共享的持久化记忆
- `code_execution` — 子 Agent 应该进行逐步推理
- `send_message` — 禁止跨平台副作用（例如发送 Telegram 消息）

## 最大迭代次数 (Max Iterations) {#max-iterations}

每个 Subagent 都有一个迭代限制（默认：50），控制其可以进行的工具调用轮数：

```python
delegate_task(
    goal="快速文件检查",
    context="检查 /etc/nginx/nginx.conf 是否存在并打印其前 10 行",
    max_iterations=10  # 简单任务，不需要太多轮次
)
```

## 层级深度限制 {#depth-limit}

委派具有 **2 层的深度限制** —— 父 Agent（深度 0）可以生成子 Agent（深度 1），但子 Agent 不能进一步委派。这可以防止失控的递归委派链。

## 核心特性 {#key-properties}

- 每个 Subagent 拥有**自己的终端会话**（与父 Agent 隔离）
- **禁止嵌套委派** —— 子 Agent 不能进一步委派（没有孙子 Agent）
- Subagent **不能**调用：`delegate_task`、`clarify`、`memory`、`send_message`、`execute_code`
- **中断传播** —— 中断父 Agent 会中断所有活跃的子 Agent
- 只有最终总结会进入父 Agent 的上下文，保持 Token 使用的高效性
- Subagent 继承父 Agent 的 **API 密钥、供应商配置和凭据池**（支持在触发速率限制时进行密钥轮换）

## Delegation vs execute_code {#delegation-vs-executecode}

| 维度 | delegate_task | execute_code |
|--------|--------------|-------------|
| **推理能力** | 完整的 LLM 推理循环 | 仅 Python 代码执行 |
| **上下文** | 全新隔离的对话 | 无对话，仅脚本 |
| **工具访问** | 带有推理能力的所有非屏蔽工具 | 通过 RPC 访问 7 个工具，无推理 |
| **并行性** | 最多 3 个并发 Subagent | 单个脚本 |
| **适用场景** | 需要判断力的复杂任务 | 机械化的多步骤流水线 |
| **Token 成本** | 较高（完整的 LLM 循环） | 较低（仅返回标准输出） |
| **用户交互** | 无（Subagent 无法澄清问题） | 无 |

**经验法则：** 当子任务需要推理、判断或多步骤解决问题时，使用 `delegate_task`。当你需要机械化的数据处理或脚本化工作流时，使用 `execute_code`。

## 配置项 {#configuration}

```yaml
# 在 ~/.hermes/config.yaml 中
delegation:
  max_iterations: 50                        # 每个子 Agent 的最大轮次（默认：50）
  default_toolsets: ["terminal", "file", "web"]  # 默认工具集
  model: "google/gemini-3-flash-preview"             # 可选：覆盖供应商/模型
  provider: "openrouter"                             # 可选：内置供应商

# 或者直接使用自定义端点而非供应商：
delegation:
  model: "qwen2.5-coder"
  base_url: "http://localhost:1234/v1"
  api_key: "local-key"
```
:::tip
Agent 会根据任务的复杂程度自动处理任务委派。你不需要显式地要求它进行委派 —— 当它认为有必要时，会自动执行此操作。
:::
