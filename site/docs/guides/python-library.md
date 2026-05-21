---
sidebar_position: 5
title: "将 Hermes 作为 Python 库使用"
description: "在你的 Python 脚本、Web 应用或自动化流程中嵌入 AIAgent —— 无需 CLI"
---

<a id="using-hermes-as-a-python-library"></a>
# 将 Hermes 作为 Python 库使用

Hermes 不只是一个 CLI 工具。你可以直接导入 `AIAgent`，并在自己的 Python 脚本、Web 应用或自动化流水线中以编程方式使用它。本指南将向你展示如何操作。

---

<a id="installation"></a>
## 安装

从仓库直接安装 Hermes：

```bash
pip install git+https://github.com/NousResearch/hermes-agent.git
```

或者使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv pip install git+https://github.com/NousResearch/hermes-agent.git
```

你也可以将其固定在 `requirements.txt` 中：

```text
hermes-agent @ git+https://github.com/NousResearch/hermes-agent.git
```

:::tip
将 Hermes 作为库使用时，同样需要设置 CLI 所需的环境变量。至少需要设置 `OPENROUTER_API_KEY`（若直接使用提供商访问，则设置 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`）。
:::

---

<a id="basic-usage"></a>
## 基本用法

使用 Hermes 的最简方式是通过 `chat()` 方法 —— 传入消息，返回字符串：

```python
from run_agent import AIAgent

agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
)
response = agent.chat("What is the capital of France?")
print(response)
```

`chat()` 内部处理完整的对话循环 —— 工具调用、重试等 —— 并仅返回最终的文本回复。

:::warning
当你将 Hermes 嵌入自己的代码时，务必设置 `quiet_mode=True`。否则 Agent 会打印 CLI 旋转标识、进度指示器以及其他终端输出，这些内容会让你的应用程序输出变得杂乱。
:::

---

<a id="full-conversation-control"></a>
## 完全控制对话

如需对对话拥有更多控制，可以直接使用 `run_conversation()`。它会返回一个字典，包含完整的回复、消息历史记录和元数据：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
)

result = agent.run_conversation(
    user_message="Search for recent Python 3.13 features",
    task_id="my-task-1",
)

print(result["final_response"])
print(f"Messages exchanged: {len(result['messages'])}")
```

返回的字典包含：
- **`final_response`** —— Agent 的最终文本回复
- **`messages`** —— 完整的消息历史记录（系统、用户、助手、工具调用）

（你传入的 `task_id` 会存储在 Agent 实例上用于 VM 隔离，但不会在返回的字典中回传。）

你也可以传入自定义系统消息，覆盖该次调用中的临时系统提示：

```python
result = agent.run_conversation(
    user_message="Explain quicksort",
    system_message="You are a computer science tutor. Use simple analogies.",
)
```

---

<a id="configuring-tools"></a>
## 配置工具

通过 `enabled_toolsets` 或 `disabled_toolsets` 控制 Agent 可以访问哪些工具集：

```python
# 仅启用 Web 工具（浏览、搜索）
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    enabled_toolsets=["web"],
    quiet_mode=True,
)

# 启用所有工具，除了终端访问
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    disabled_toolsets=["terminal"],
    quiet_mode=True,
)
```
:::tip
当你想要一个最小化、锁定功能的 Agent 时（例如，只允许研究机器人进行网络搜索），请使用 `enabled_toolsets`。当你想要大部分功能但需要限制某些特定功能时（例如，在共享环境中禁止终端访问），请使用 `disabled_toolsets`。
:::

---

<a id="multi-turn-conversations"></a>
## 多轮对话

通过将消息历史记录传回，可以在多轮对话中维持对话状态：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
)

# 第一轮
result1 = agent.run_conversation("My name is Alice")
history = result1["messages"]

# 第二轮 — Agent 会记住上下文
result2 = agent.run_conversation(
    "What's my name?",
    conversation_history=history,
)
print(result2["final_response"])  # "Your name is Alice."
```

`conversation_history` 参数接受上一次结果中的 `messages` 列表。Agent 会在内部复制它，因此你的原始列表永远不会被修改。

---

<a id="saving-trajectories"></a>
## 保存轨迹

启用轨迹保存功能，以 ShareGPT 格式捕获对话——这对于生成训练数据或调试非常有用：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    save_trajectories=True,
    quiet_mode=True,
)

agent.chat("Write a Python function to sort a list")
# 以 ShareGPT 格式保存到 trajectory_samples.jsonl
```

每次对话都会作为一行 JSONL 追加，方便从自动化运行中收集数据集。

---

<a id="custom-system-prompts"></a>
## 自定义系统提示

使用 `ephemeral_system_prompt` 设置自定义系统提示，以指导 Agent 的行为，但**不会**保存到轨迹文件中（保持训练数据干净）：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    ephemeral_system_prompt="You are a SQL expert. Only answer database questions.",
    quiet_mode=True,
)

response = agent.chat("How do I write a JOIN query?")
print(response)
```

这对于构建专用 Agent 非常理想——代码审查员、文档编写员、SQL 助手——所有这些都使用相同的底层工具。

---

<a id="batch-processing"></a>
## 批量处理

为了并行运行大量提示，Hermes 包含了 `batch_runner.py`。它管理并发的 `AIAgent` 实例，并具有适当的资源隔离：

```bash
python batch_runner.py --input prompts.jsonl --output results.jsonl
```

每个提示都有自己的 `task_id` 和隔离的环境。如果你需要自定义批量逻辑，可以直接使用 `AIAgent` 构建自己的方案：

```python
import concurrent.futures
from run_agent import AIAgent

prompts = [
    "Explain recursion",
    "What is a hash table?",
    "How does garbage collection work?",
]

def process_prompt(prompt):
    # 为每个任务创建一个全新的 Agent，以确保线程安全
    agent = AIAgent(
        model="anthropic/claude-sonnet-4",
        quiet_mode=True,
        skip_memory=True,
    )
    return agent.chat(prompt)

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_prompt, prompts))

for prompt, result in zip(prompts, results):
    print(f"Q: {prompt}\nA: {result}\n")
```
:::warning
务必为每个线程或任务创建一个 **新的 `AIAgent` 实例**。Agent 会维护内部状态（对话历史、工具会话、迭代计数器），这些状态不是线程安全的，不能共享。
:::

---

<a id="integration-examples"></a>
## 集成示例

<a id="fastapi-endpoint"></a>
### FastAPI 端点

```python
from fastapi import FastAPI
from pydantic import BaseModel
from run_agent import AIAgent

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    model: str = "anthropic/claude-sonnet-4"

@app.post("/chat")
async def chat(request: ChatRequest):
    agent = AIAgent(
        model=request.model,
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
    )
    response = agent.chat(request.message)
    return {"response": response}
```

<a id="discord-bot"></a>
### Discord 机器人

```python
import discord
from run_agent import AIAgent

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!hermes "):
        query = message.content[8:]
        agent = AIAgent(
            model="anthropic/claude-sonnet-4",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            platform="discord",
        )
        response = agent.chat(query)
        await message.channel.send(response[:2000])

client.run("YOUR_DISCORD_TOKEN")
```

<a id="ci-cd-pipeline-step"></a>
### CI/CD 流水线步骤

```python
#!/usr/bin/env python3
"""CI 步骤：自动审查 PR 的差异。"""
import subprocess
from run_agent import AIAgent

diff = subprocess.check_output(["git", "diff", "main...HEAD"]).decode()

agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
    skip_context_files=True,
    skip_memory=True,
    disabled_toolsets=["terminal", "browser"],
)

review = agent.chat(
    f"审查此 PR 差异中的 Bug、安全问题以及代码风格问题：\n\n{diff}"
)
print(review)
```

---

<a id="key-constructor-parameters"></a>
## 关键构造函数参数

| 参数 | 类型 | 默认值 | 说明 |
|-----------|------|---------|-------------|
| `model` | `str` | `"anthropic/claude-opus-4.6"` | OpenRouter 格式的模型名称 |
| `quiet_mode` | `bool` | `False` | 抑制 CLI 输出 |
| `enabled_toolsets` | `List[str]` | `None` | 白名单指定的工具集 |
| `disabled_toolsets` | `List[str]` | `None` | 黑名单指定的工具集 |
| `save_trajectories` | `bool` | `False` | 将对话保存为 JSONL |
| `ephemeral_system_prompt` | `str` | `None` | 自定义系统提示（不会保存到轨迹中） |
| `max_iterations` | `int` | `90` | 每次对话中工具调用的最大迭代次数 |
| `skip_context_files` | `bool` | `False` | 跳过加载 AGENTS.md 文件 |
| `skip_memory` | `bool` | `False` | 禁用持久化内存的读写 |
| `api_key` | `str` | `None` | API 密钥（可选，会回退到环境变量） |
| `base_url` | `str` | `None` | 自定义 API 端点 URL |
| `platform` | `str` | `None` | 平台提示（如 `"discord"`、`"telegram"` 等） |

---

<a id="important-notes"></a>
## 重要说明

:::tip
- 设置 **`skip_context_files=True`**，可以避免将工作目录下的 `AGENTS.md` 文件加载到系统提示中。
- 设置 **`skip_memory=True`** 可以阻止 Agent 读取或写入持久化内存 —— 对于无状态 API 端点建议启用。
- `platform` 参数（例如 `"discord"`、`"telegram"`）会注入平台特定的格式提示，让 Agent 调整输出风格。
:::
:::warning
- **线程安全**：请为每个线程或任务创建一个 `AIAgent` 实例。切勿在并发调用中共享同一个实例。
- **资源清理**：对话结束时，Agent 会自动清理资源（终端会话、浏览器实例）。如果你在长期运行的进程中执行操作，请确保每个对话都能正常结束。
- **迭代限制**：默认的 `max_iterations=90` 是一个比较宽松的上限。对于简单的问答场景，建议降低该值（例如 `max_iterations=10`），以防止工具调用循环失控并控制成本。
:::
