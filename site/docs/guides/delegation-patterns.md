---
sidebar_position: 13
title: "委托与并行工作"
description: "何时以及如何使用子 Agent 委托——并行研究、代码审查和多文件工作的模式"
---

# 委托与并行工作 {#delegation-parallel-work}

Hermes 可以生成独立的子 Agent 来并行处理任务。每个子 Agent 拥有自己的对话、终端会话和工具集。只有最终的摘要会返回——中间的工具调用不会进入你的上下文窗口。

完整功能参考，请参见 [子 Agent 委托](/user-guide/features/delegation)。

---

## 何时委托 {#when-to-delegate}

**适合委托的场景：**
- 需要大量推理的子任务（调试、代码审查、研究综合）
- 会让你的上下文被中间数据淹没的任务
- 并行独立的工作流（同时进行研究 A 和研究 B）
- 需要 Agent 不带偏见地处理的全新上下文任务

**应使用其他方式的情况：**
- 单个工具调用 → 直接使用工具
- 步骤间有逻辑的机械式多步工作 → `execute_code`
- 需要用户交互的任务 → 子 Agent 无法使用 `clarify`
- 快速文件编辑 → 直接操作
- 需要持久运行且必须跨越当前轮次的长期任务 → `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。`delegate_task` 是**同步**的：如果父轮次被中断，正在运行的子任务会被取消，其工作也会被丢弃。

---

## 模式：并行研究 {#pattern-parallel-research}

同时研究三个主题，并获取结构化的摘要：

```
并行研究以下三个主题：
1. 浏览器外 WebAssembly 的当前状态
2. 2025 年 RISC-V 服务器芯片的采用情况
3. 实用的量子计算应用

重点关注近期发展和关键参与者。
```

在幕后，Hermes 使用：

```python
delegate_task(tasks=[
    {
        "goal": "研究 2025 年浏览器外的 WebAssembly",
        "context": "重点关注：运行时（Wasmtime、Wasmer）、云/边缘用例、WASI 进展",
        "toolsets": ["web"]
    },
    {
        "goal": "研究 RISC-V 服务器芯片的采用情况",
        "context": "重点关注：已出货的服务器芯片、云服务商的采用、软件生态",
        "toolsets": ["web"]
    },
    {
        "goal": "研究实用的量子计算应用",
        "context": "重点关注：纠错突破、实际用例、关键公司",
        "toolsets": ["web"]
    }
])
```

三个任务同时运行。每个子 Agent 独立搜索网络并返回摘要。父 Agent 随后将它们综合成一份连贯的简报。

---

## 模式：代码审查 {#pattern-code-review}

将安全审查委托给一个全新上下文的子 Agent，让它不带先入之见地审查代码：

```
审查 src/auth/ 中的认证模块，查找安全问题。
检查 SQL 注入、JWT 验证问题、密码处理
和会话管理。修复你发现的任何问题并运行测试。
```

关键在于 `context` 字段——它必须包含子 Agent 所需的一切：

```python
delegate_task(
    goal="审查 src/auth/ 的安全问题并修复发现的问题",
    context="""项目位于 /home/user/webapp。Python 3.11、Flask、PyJWT、bcrypt。
    认证文件：src/auth/login.py、src/auth/jwt.py、src/auth/middleware.py
    测试命令：pytest tests/auth/ -v
    重点关注：SQL 注入、JWT 验证、密码哈希、会话管理。
    修复发现的问题并验证测试通过。""",
    toolsets=["terminal", "file"]
)
```
:::warning 上下文问题
Subagent 对你的对话**一无所知**。它们会从完全空白的状态开始。如果你委托“修复我们刚才讨论的那个 bug”，subagent 根本不知道你说的是哪个 bug。务必显式地传递文件路径、错误消息、项目结构和约束条件。
:::
<a id="the-context-problem"></a>

---

## 模式：比较多种方案 {#pattern-compare-alternatives}

并行评估同一问题的多种方案，然后选出最佳：

```
I need to add full-text search to our Django app. Evaluate three approaches
in parallel:
1. PostgreSQL tsvector (built-in)
2. Elasticsearch via django-elasticsearch-dsl
3. Meilisearch via meilisearch-python

For each: setup complexity, query capabilities, resource requirements,
and maintenance overhead. Compare them and recommend one.
```

每个 subagent 独立研究一个选项。由于它们之间相互隔离，因此不会发生交叉干扰——每个评估都基于自身的优点。父 Agent 获取全部三个摘要，然后进行比较。

---

## 模式：多文件重构 {#pattern-multi-file-refactoring}

将一个大型重构任务拆分给并行的 subagent，每个 subagent 处理代码库的不同部分：

```python
delegate_task(tasks=[
    {
        "goal": "Refactor all API endpoint handlers to use the new response format",
        "context": """Project at /home/user/api-server.
        Files: src/handlers/users.py, src/handlers/auth.py, src/handlers/billing.py
        Old format: return {"data": result, "status": "ok"}
        New format: return APIResponse(data=result, status=200).to_dict()
        Import: from src.responses import APIResponse
        Run tests after: pytest tests/handlers/ -v""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "Update all client SDK methods to handle the new response format",
        "context": """Project at /home/user/api-server.
        Files: sdk/python/client.py, sdk/python/models.py
        Old parsing: result = response.json()["data"]
        New parsing: result = response.json()["data"] (same key, but add status code checking)
        Also update sdk/python/tests/test_client.py""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "Update API documentation to reflect the new response format",
        "context": """Project at /home/user/api-server.
        Docs at: docs/api/. Format: Markdown with code examples.
        Update all response examples from old format to new format.
        Add a 'Response Format' section to docs/api/overview.md explaining the schema.""",
        "toolsets": ["terminal", "file"]
    }
])
```

:::tip
每个 subagent 都有自己的终端会话。只要它们编辑的是不同文件，就可以在同一项目目录下工作而不会互相干扰。如果两个 subagent 可能操作同一个文件，请在并行工作完成后手动处理该文件。
:::

---

## 模式：先收集再分析 {#pattern-gather-then-analyze}

使用 `execute_code` 进行机械式的数据收集，然后将推理密集型分析委托出去：

```python
# Step 1: Mechanical gathering (execute_code is better here — no reasoning needed)
execute_code("""
from hermes_tools import web_search, web_extract

results = []
for query in ["AI funding Q1 2026", "AI startup acquisitions 2026", "AI IPOs 2026"]:
    r = web_search(query, limit=5)
    for item in r["data"]["web"]:
        results.append({"title": item["title"], "url": item["url"], "desc": item["description"]})

# Extract full content from top 5 most relevant
urls = [r["url"] for r in results[:5]]
content = web_extract(urls)

# Save for the analysis step
import json
with open("/tmp/ai-funding-data.json", "w") as f:
    json.dump({"search_results": results, "extracted": content["results"]}, f)
print(f"Collected {len(results)} results, extracted {len(content['results'])} pages")
""")

# Step 2: Reasoning-heavy analysis (delegation is better here)
delegate_task(
    goal="Analyze AI funding data and write a market report",
    context="""Raw data at /tmp/ai-funding-data.json contains search results and
    extracted web pages about AI funding, acquisitions, and IPOs in Q1 2026.
    Write a structured market report: key deals, trends, notable players,
    and outlook. Focus on deals over $100M.""",
    toolsets=["terminal", "file"]
)
```
这通常是最高效的模式：`execute_code` 廉价地处理 10 多个顺序工具调用，然后子 Agent 在干净的上下文中执行一次昂贵的推理任务。

---

## 工具集选择 {#toolset-selection}

根据子 Agent 的需求选择工具集：

| 任务类型 | 工具集 | 原因 |
|-----------|----------|------|
| 网络研究 | `["web"]` | 仅 web_search + web_extract |
| 代码工作 | `["terminal", "file"]` | Shell 访问 + 文件操作 |
| 全栈 | `["terminal", "file", "web"]` | 除消息外的一切 |
| 只读分析 | `["file"]` | 只能读取文件，无 shell |

限制工具集能让子 Agent 保持专注，并防止意外副作用（例如研究子 Agent 运行 shell 命令）。

---

## 约束 {#constraints}

- **默认 3 个并行任务**：批次默认最多 3 个并发子 Agent（可通过 config.yaml 中的 `delegation.max_concurrent_children` 配置，无硬上限，仅下限为 1）
- **嵌套委派为可选加入**：叶子子 Agent（默认）不能调用 `delegate_task`、`clarify`、`memory`、`send_message` 或 `execute_code`。编排子 Agent（`role="orchestrator"`）保留 `delegate_task` 以进行进一步委派，但仅当 `delegation.max_spawn_depth` 提高到默认值 1 以上时（支持 1-3）；其余四个仍被阻止。通过 `delegation.orchestrator_enabled: false` 全局禁用。

### 调整并发与深度 {#tuning-concurrency-and-depth}

| 配置项 | 默认值 | 范围 | 效果 |
|--------|---------|-------|--------|
| `max_concurrent_children` | 3 | >=1 | 每次 `delegate_task` 调用的并行批次大小 |
| `max_spawn_depth` | 1 | 1-3 | 委派层级可以继续生成多少层 |

示例：运行 30 个并行工作器并嵌套子 Agent：

```yaml
delegation:
  max_concurrent_children: 30
  max_spawn_depth: 2
```

- **独立的终端**——每个子 Agent 拥有自己的终端会话，具有独立的工作目录和状态
- **无对话历史**——子 Agent 只能看到父 Agent 在调用 `delegate_task` 时传递的 `goal` 和 `context`
- **默认 50 次迭代**——对于简单任务，将 `max_iterations` 设低以节省成本
- **非持久**——`delegate_task` 是同步的，在父轮次内运行。如果父轮次被中断（新用户消息、`/stop`、`/new`），所有活跃的子任务将被取消（`status="interrupted"`），其工作被丢弃。对于需要跨越当前轮次的工作，请使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。

---

## 提示 {#tips}

**目标要具体。**“修复 bug”太模糊。“修复 api/handlers.py 第 47 行的 TypeError，其中 process_request() 从 parse_body() 收到 None”给了子 Agent 足够的信息。

**包含文件路径。**子 Agent 不知道你的项目结构。始终包含相关文件的绝对路径、项目根目录和测试命令。

**利用委派实现上下文隔离。**有时你需要一个全新的视角。委派迫使你清晰地阐述问题，而子 Agent 在不受你对话中积累的假设影响的情况下处理它。
**检查结果。** Subagent 摘要只是摘要而已。如果某个 subagent 说“已修复 bug，测试通过”，请通过自己运行测试或阅读 diff 来验证。

---

*有关完整的委托参考——所有参数、ACP 集成和高级配置——请参阅 [Subagent 委托](/user-guide/features/delegation)。*
