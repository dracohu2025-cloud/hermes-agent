---
sidebar_position: 13
title: "任务委派与并行工作"
description: "何时以及如何使用子 Agent 委派 —— 涵盖并行调研、代码审查和多文件协作的模式"
---

# 任务委派与并行工作

Hermes 可以生成独立的子 Agent 来并行处理任务。每个子 Agent 都有自己独立的对话、终端会话和工具集。只有最终的总结会返回给主 Agent —— 中间的工具调用过程永远不会进入你的上下文窗口。

有关完整的功能参考，请参阅 [子 Agent 委派](/user-guide/features/delegation)。

---

## 何时进行委派

**适合委派的场景：**
- 重推理的子任务（调试、代码审查、调研综述）
- 会产生大量中间数据并淹没上下文的任务
- 并行的独立工作流（同时进行调研 A 和 B）
- 需要“新鲜上下文”的任务，即你希望 Agent 在没有先入为主偏见的情况下处理任务

**建议使用其他方式的场景：**
- 单次工具调用 → 直接使用该工具即可
- 步骤间带有逻辑的机械性多步工作 → 使用 `execute_code`
- 需要用户交互的任务 → 子 Agent 无法使用 `clarify`
- 快速的文件编辑 → 直接进行编辑

---

## 模式：并行调研

同时调研三个主题并获取结构化的总结：

```
并行调研以下三个主题：
1. WebAssembly 在浏览器之外的现状
2. 2025 年 RISC-V 服务器芯片的采用情况
3. 实际的量子计算应用

重点关注最新进展和主要参与者。
```

在后台，Hermes 会使用：

```python
delegate_task(tasks=[
    {
        "goal": "调研 2025 年 WebAssembly 在浏览器之外的情况",
        "context": "重点关注：运行时（Wasmtime, Wasmer）、云/边缘计算用例、WASI 进展",
        "toolsets": ["web"]
    },
    {
        "goal": "调研 RISC-V 服务器芯片的采用情况",
        "context": "重点关注：已出货的服务器芯片、采用该技术的云服务商、软件生态系统",
        "toolsets": ["web"]
    },
    {
        "goal": "调研实际的量子计算应用",
        "context": "重点关注：纠错技术的突破、真实世界的用例、关键公司",
        "toolsets": ["web"]
    }
])
```

这三个任务会并发运行。每个子 Agent 独立搜索网页并返回总结。随后，父 Agent 会将它们整合为一份连贯的简报。

---

## 模式：代码审查

将安全审查委派给一个拥有新鲜上下文的子 Agent，使其在没有任何预设假设的情况下审视代码：

```
审查 src/auth/ 目录下的身份验证模块是否存在安全问题。
检查 SQL 注入、JWT 验证问题、密码处理和会话管理。
修复你发现的任何问题并运行测试。
```

关键在于 `context` 字段 —— 它必须包含子 Agent 所需的一切信息：

```python
delegate_task(
    goal="审查 src/auth/ 的安全问题并修复发现的任何问题",
    context="""项目路径：/home/user/webapp。技术栈：Python 3.11, Flask, PyJWT, bcrypt。
    认证相关文件：src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py
    测试命令：pytest tests/auth/ -v
    重点关注：SQL 注入、JWT 验证、密码哈希、会话管理。
    修复发现的问题并验证测试通过。""",
    toolsets=["terminal", "file"]
)
```

:::warning 上下文问题
子 Agent 对你的当前对话 **一无所知**。它们是从零开始的。如果你委派的任务是“修复我们刚才讨论的那个 bug”，子 Agent 根本不知道你在指哪个 bug。请务必显式地传递文件路径、错误信息、项目结构和约束条件。
:::

---

## 模式：方案对比

并行评估解决同一问题的多种方法，然后择优录取：

```
我需要为我们的 Django 应用添加全文搜索功能。请并行评估三种方案：
1. PostgreSQL tsvector (内置)
2. 通过 django-elasticsearch-dsl 使用 Elasticsearch
3. 通过 meilisearch-python 使用 Meilisearch

针对每种方案，评估：设置复杂度、查询能力、资源需求和维护成本。对比它们并推荐一个。
```

每个子 Agent 独立调研一个选项。由于它们是隔离的，因此不会产生交叉干扰 —— 每个评估都基于其自身的优缺点。父 Agent 获取所有三份总结并进行对比。

---

## 模式：多文件重构

将大型重构任务拆分给并行的子 Agent，每个 Agent 处理代码库的不同部分：

```python
delegate_task(tasks=[
    {
        "goal": "重构所有 API 接口处理程序以使用新的响应格式",
        "context": """项目路径：/home/user/api-server。
        文件：src/handlers/users.py, src/handlers/auth.py, src/handlers/billing.py
        旧格式：return {"data": result, "status": "ok"}
        新格式：return APIResponse(data=result, status=200).to_dict()
        导入语句：from src.responses import APIResponse
        完成后运行测试：pytest tests/handlers/ -v""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "更新所有客户端 SDK 方法以处理新的响应格式",
        "context": """项目路径：/home/user/api-server。
        文件：sdk/python/client.py, sdk/python/models.py
        旧解析逻辑：result = response.json()["data"]
        新解析逻辑：result = response.json()["data"] (键名相同，但需增加状态码检查)
        同时更新 sdk/python/tests/test_client.py""",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "更新 API 文档以反映新的响应格式",
        "context": """项目路径：/home/user/api-server。
        文档路径：docs/api/。格式：带有代码示例的 Markdown。
        将所有响应示例从旧格式更新为新格式。
        在 docs/api/overview.md 中添加一个“响应格式”章节来解释该 Schema。""",
        "toolsets": ["terminal", "file"]
    }
])
```

:::tip 提示
每个子 Agent 都有自己的终端会话。只要它们编辑的是不同的文件，就可以在同一个项目目录中工作而互不干扰。如果两个子 Agent 可能会触及同一个文件，请在并行工作完成后由你亲自处理该文件。
:::

---

## 模式：先收集后分析

使用 `execute_code` 进行机械性的数据收集，然后委派重推理的分析任务：

```python
# 步骤 1：机械性收集（这里用 execute_code 更好 —— 不需要推理）
execute_code("""
from hermes_tools import web_search, web_extract

results = []
for query in ["AI funding Q1 2026", "AI startup acquisitions 2026", "AI IPOs 2026"]:
    r = web_search(query, limit=5)
    for item in r["data"]["web"]:
        results.append({"title": item["title"], "url": item["url"], "desc": item["description"]})

# 从相关性最高的前 5 个结果中提取完整内容
urls = [r["url"] for r in results[:5]]
content = web_extract(urls)

# 保存以供分析步骤使用
import json
with open("/tmp/ai-funding-data.json", "w") as f:
    json.dump({"search_results": results, "extracted": content["results"]}, f)
print(f"Collected {len(results)} results, extracted {len(content['results'])} pages")
""")

# 步骤 2：重推理分析（这里用委派更好）
delegate_task(
    goal="分析 AI 融资数据并撰写一份市场报告",
    context="""位于 /tmp/ai-funding-data.json 的原始数据包含关于 2026 年第一季度 AI 融资、收购和 IPO 的搜索结果及提取的网页内容。
    撰写一份结构化的市场报告：关键交易、趋势、值得关注的参与者以及前景展望。重点关注超过 1 亿美元的交易。""",
    toolsets=["terminal", "file"]
)
```

这通常是最有效的模式：`execute_code` 以低成本处理 10 多个顺序工具调用，然后子 Agent 在干净的上下文中执行单次高成本的推理任务。

---

## 工具集选择

根据子 Agent 的需求选择工具集：

| 任务类型 | 工具集 | 原因 |
|-----------|----------|-----|
| 网页调研 | `["web"]` | 仅需 web_search + web_extract |
| 代码工作 | `["terminal", "file"]` | Shell 访问 + 文件操作 |
| 全栈任务 | `["terminal", "file", "web"]` | 除了消息传递外的一切工具 |
| 只读分析 | `["file"]` | 只能读取文件，无 Shell 权限 |

限制工具集可以使子 Agent 保持专注，并防止意外的副作用（例如调研子 Agent 运行 Shell 命令）。
---

## 限制条件 (Constraints)

- **最多 3 个并行任务** — 批处理上限为 3 个并发的 subagent。
- **禁止嵌套** — subagent 无法调用 `delegate_task`、`clarify`、`memory`、`send_message` 或 `execute_code`。
- **独立的终端** — 每个 subagent 拥有自己的终端会话，具有独立的运行目录和状态。
- **无对话历史** — subagent 只能看到你在 `goal` 和 `context` 中提供的内容。
- **默认 50 次迭代** — 对于简单任务，请将 `max_iterations` 设置得更低以节省成本。

---

## 技巧 (Tips)

**目标描述要具体。** “修复 bug” 太模糊了。“修复 api/handlers.py 第 47 行的 TypeError，即 process_request() 从 parse_body() 接收到了 None” 才能给 subagent 提供足够的操作依据。

**包含文件路径。** Subagent 并不了解你的项目结构。请务必包含相关文件、项目根目录的绝对路径以及测试命令。

**利用 Delegation 进行上下文隔离。** 有时你需要一个全新的视角。使用 Delegation 会迫使你清晰地阐述问题，而 subagent 在处理问题时不会带有你在当前对话中积累的先入为主的假设。

**检查结果。** Subagent 的总结仅仅是总结。如果一个 subagent 说“修复了 bug 且测试通过”，请务必亲自运行测试或阅读 diff 来进行验证。

---

*有关 Delegation 的完整参考资料（包括所有参数、ACP 集成和高级配置），请参阅 [Subagent Delegation](/user-guide/features/delegation)。*
