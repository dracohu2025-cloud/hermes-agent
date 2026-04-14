---
sidebar_position: 13
title: "委托与并行工作"
description: "何时以及如何使用子代理委托——并行研究、代码审查和多文件工作的模式"
---

# 委托与并行工作

Hermes 可以生成隔离的子代理来并行处理任务。每个子代理都有自己的对话、终端会话和工具集。只有最终的摘要会返回——中间的工具调用永远不会进入你的上下文窗口。

完整的功能参考，请参阅[子代理委托](/user-guide/features/delegation)。

---

## 何时进行委托

**适合委托的场景：**
- 推理密集的子任务（调试、代码审查、研究综合）
- 会产生大量中间数据、可能淹没你上下文的任务
- 并行独立的工作流（同时进行 A 和 B 研究）
- 需要全新上下文、希望代理不带偏见处理的任务

**使用其他方式：**
- 单一工具调用 → 直接使用工具
- 步骤间有逻辑的机械性多步工作 → `execute_code`
- 需要用户交互的任务 → 子代理无法使用 `clarify`
- 快速文件编辑 → 直接操作

---

## 模式：并行研究

同时研究三个主题并获取结构化摘要：

```
并行研究以下三个主题：
1. WebAssembly 在浏览器外的当前状态
2. 2025 年 RISC-V 服务器芯片的采用情况
3. 实用的量子计算应用

重点关注近期发展和关键参与者。
```

在幕后，Hermes 使用：

```python
delegate_task(tasks=[
    {
        "goal": "研究 2025 年浏览器外的 WebAssembly",
        "context": "重点关注：运行时（Wasmtime, Wasmer）、云/边缘用例、WASI 进展",
        "toolsets": ["web"]
    },
    {
        "goal": "研究 RISC-V 服务器芯片的采用情况",
        "context": "重点关注：已发布的服务器芯片、云提供商采用情况、软件生态系统",
        "toolsets": ["web"]
    },
    {
        "goal": "研究实用的量子计算应用",
        "context": "重点关注：纠错突破、实际用例、关键公司",
        "toolsets": ["web"]
    }
])
```

三者同时运行。每个子代理独立搜索网络并返回摘要。然后父代理将它们综合成一份连贯的简报。

---

## 模式：代码审查

将安全审查委托给一个拥有全新上下文的子代理，使其不带先入之见地审查代码：

```
审查 src/auth/ 下的身份验证模块是否存在安全问题。
检查 SQL 注入、JWT 验证问题、密码处理和会话管理。
修复发现的任何问题并运行测试。
```

关键在于 `context` 字段——它必须包含子代理所需的一切信息：

```python
delegate_task(
    goal="审查 src/auth/ 的安全问题并修复发现的任何问题",
    context="""项目位于 /home/user/webapp。Python 3.11, Flask, PyJWT, bcrypt。
    身份验证文件：src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py
    测试命令：pytest tests/auth/ -v
    重点关注：SQL 注入、JWT 验证、密码哈希、会话管理。
    修复发现的问题并验证测试通过。""",
    toolsets=["terminal", "file"]
)
```

:::warning 上下文问题
子代理对你的对话**一无所知**。它们完全从零开始。如果你委托“修复我们正在讨论的 bug”，子代理根本不知道你指的是哪个 bug。务必明确传递文件路径、错误信息、项目结构和约束条件。
:::

---

## 模式：比较备选方案

并行评估同一问题的多种方法，然后选择最佳方案：

```
我需要为我们的 Django 应用添加全文搜索。并行评估三种方法：
1. PostgreSQL tsvector（内置）
2. 通过 django-elasticsearch-dsl 使用 Elasticsearch
3. 通过 meilisearch-python 使用 Meilisearch

针对每种方法：评估设置复杂性、查询能力、资源需求和维护开销。
比较它们并推荐一种。
```

每个子代理独立研究一个选项。由于它们是隔离的，不存在交叉影响——每个评估都基于其自身优点。父代理获得所有三个摘要并进行比较。

---

## 模式：多文件重构

将大型重构任务拆分给并行子代理，每个子代理处理代码库的不同部分：

```python
delegate_task(tasks=[
    {
        "goal": "重构所有 API 端点处理程序以使用新的响应格式",
        "context": """项目位于 /home/user/api-server。
        文件：src/handlers/users.py, src/handlers/auth.py, src/handlers/billing.py
        旧格式：return {"data": result, "status": "ok"}
        新格式：return APIResponse(data=result, status=200).to_dict()
        导入：from src.responses import APIResponse
        之后运行测试：pytest tests/handlers/ -v""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "更新所有客户端 SDK 方法以处理新的响应格式",
        "context": """项目位于 /home/user/api-server。
        文件：sdk/python/client.py, sdk/python/models.py
        旧解析方式：result = response.json()["data"]
        新解析方式：result = response.json()["data"]（键相同，但添加状态码检查）
        同时更新 sdk/python/tests/test_client.py""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "更新 API 文档以反映新的响应格式",
        "context": """项目位于 /home/user/api-server。
        文档位于：docs/api/。格式：带代码示例的 Markdown。
        将所有响应示例从旧格式更新为新格式。
        在 docs/api/overview.md 中添加“响应格式”部分，解释模式。""",
        "toolsets": ["terminal", "file"]
    }
])
```

:::tip
每个子代理都有自己的终端会话。只要它们编辑的是不同的文件，它们就可以在同一个项目目录下工作而不会相互干扰。如果两个子代理可能触及同一个文件，请在并行工作完成后自己处理该文件。
:::

---

## 模式：收集然后分析

使用 `execute_code` 进行机械的数据收集，然后将推理密集的分析任务委托出去：

```python
# 步骤 1：机械收集（此处使用 execute_code 更好——无需推理）
execute_code("""
from hermes_tools import web_search, web_extract

results = []
for query in ["AI funding Q1 2026", "AI startup acquisitions 2026", "AI IPOs 2026"]:
    r = web_search(query, limit=5)
    for item in r["data"]["web"]:
        results.append({"title": item["title"], "url": item["url"], "desc": item["description"]})

# 从最相关的 5 个结果中提取完整内容
urls = [r["url"] for r in results[:5]]
content = web_extract(urls)

# 保存供分析步骤使用
import json
with open("/tmp/ai-funding-data.json", "w") as f:
    json.dump({"search_results": results, "extracted": content["results"]}, f)
print(f"收集了 {len(results)} 个结果，提取了 {len(content['results'])} 个页面")
""")

# 步骤 2：推理密集的分析（此处委托更好）
delegate_task(
    goal="分析 AI 融资数据并撰写市场报告",
    context="""原始数据位于 /tmp/ai-funding-data.json，包含关于 2026 年第一季度 AI 融资、收购和 IPO 的搜索结果和提取的网页。
    撰写一份结构化的市场报告：关键交易、趋势、重要参与者和展望。重点关注超过 1 亿美元的交易。""",
    toolsets=["terminal", "file"]
)
```

这通常是最有效的模式：`execute_code` 以低成本处理 10 多个顺序工具调用，然后子代理在一个干净的上下文中执行单个昂贵的高推理任务。

---

## 工具集选择

根据子代理的需求选择工具集：

| 任务类型 | 工具集 | 原因 |
|-----------|----------|-----|
| 网络研究 | `["web"]` | 仅 web_search + web_extract |
| 代码工作 | `["terminal", "file"]` | Shell 访问 + 文件操作 |
| 全栈工作 | `["terminal", "file", "web"]` | 除消息传递外的所有功能 |
| 只读分析 | `["file"]` | 只能读取文件，无 shell |

限制工具集可以保持子代理专注，并防止意外的副作用（例如研究子代理运行 shell 命令）。
---

## 约束条件

- **默认 3 个并行任务** — 批次默认使用 3 个并发子 Agent（可通过 config.yaml 中的 `delegation.max_concurrent_children` 配置）
- **不支持嵌套** — 子 Agent 不能调用 `delegate_task`、`clarify`、`memory`、`send_message` 或 `execute_code`
- **独立的终端** — 每个子 Agent 都拥有自己独立的终端会话，包含独立的工作目录和状态
- **无对话历史** — 子 Agent 只能看到你在 `goal` 和 `context` 中提供的信息
- **默认 50 次迭代** — 对于简单任务，可以设置较低的 `max_iterations` 以节省成本

---

## 技巧

**目标要具体。** “修复这个 bug” 太模糊了。“修复 api/handlers.py 第 47 行中 `process_request()` 从 `parse_body()` 接收到 None 导致的 TypeError” 这样的描述才能给子 Agent 足够的信息去处理。

**包含文件路径。** 子 Agent 不了解你的项目结构。务必包含相关文件的绝对路径、项目根目录以及测试命令。

**利用委派实现上下文隔离。** 有时你需要一个全新的视角。委派任务迫使你清晰地阐述问题，而子 Agent 会不带任何你在对话中积累的预设去处理它。

**检查结果。** 子 Agent 的总结仅仅是总结。如果子 Agent 说“已修复 bug 且测试通过”，请亲自运行测试或查看代码差异来验证。

---

*关于完整的委派参考——所有参数、ACP 集成和高级配置——请参阅 [子 Agent 委派](/user-guide/features/delegation)。*
