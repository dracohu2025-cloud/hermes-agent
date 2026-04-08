---
sidebar_position: 5
title: "将 Hermes 作为 Python 库使用"
description: "在你的 Python 脚本、Web 应用或自动化流水线中嵌入 AIAgent —— 无需 CLI"
---

# 将 Hermes 作为 Python 库使用

Hermes 不仅仅是一个 CLI 工具。你可以直接导入 `AIAgent`，并在你自己的 Python 脚本、Web 应用程序或自动化流水线中以编程方式使用它。本指南将向你展示如何操作。

---

## 安装

直接从仓库安装 Hermes：

```bash
pip install git+https://github.com/NousResearch/hermes-agent.git
```

或者使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv pip install git+https://github.com/NousResearch/hermes-agent.git
```

你也可以在 `requirements.txt` 中固定版本：

```text
hermes-agent @ git+https://github.com/NousResearch/hermes-agent.git
```

:::tip 提示
将 Hermes 作为库使用时，仍需要 CLI 所使用的相同环境变量。至少需要设置 `OPENROUTER_API_KEY`（如果直接使用模型提供商，则设置 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`）。
:::

---

## 基础用法

使用 Hermes 最简单的方法是 `chat()` 方法 —— 传入一条消息，返回一个字符串：

```python
from run_agent import AIAgent

agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
)
response = agent.chat("What is the capital of France?")
print(response)
```

`chat()` 会在内部处理完整的对话循环 —— 包括工具调用、重试等所有环节 —— 并仅返回最终的文本响应。

:::warning 警告
在自己的代码中嵌入 Hermes 时，请务必设置 `quiet_mode=True`。否则，Agent 会打印 CLI 加载动画、进度指示器和其他终端输出，这会弄乱你应用程序的输出内容。
:::

---

## 完整的对话控制

如果需要对对话进行更多控制，请直接使用 `run_conversation()`。它会返回一个包含完整响应、消息历史记录和元数据的字典：

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
- **`final_response`** — Agent 的最终文本回复
- **`messages`** — 完整的消息历史（系统、用户、助手、工具调用）
- **`task_id`** — 用于 VM 隔离的任务标识符

你还可以传递一个自定义系统消息，它会覆盖该次调用的临时系统提示词：

```python
result = agent.run_conversation(
    user_message="Explain quicksort",
    system_message="You are a computer science tutor. Use simple analogies.",
)
```

---

## 配置工具

使用 `enabled_toolsets` 或 `disabled_toolsets` 来控制 Agent 可以访问哪些工具集：

```python
# 仅启用 Web 工具（浏览、搜索）
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    enabled_toolsets=["web"],
    quiet_mode=True,
)

# 启用除终端访问以外的所有功能
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    disabled_toolsets=["terminal"],
    quiet_mode=True,
)
```

:::tip 提示
当你想要一个最小化、受限的 Agent（例如，仅用于研究机器人的 Web 搜索）时，请使用 `enabled_toolsets`。当你想要大部分功能但需要限制特定功能（例如，在共享环境中禁止终端访问）时，请使用 `disabled_toolsets`。
:::

---

## 多轮对话

通过将消息历史记录传回，可以在多轮对话中保持对话状态：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    quiet_mode=True,
)

# 第一轮
result1 = agent.run_conversation("My name is Alice")
history = result1["messages"]

# 第二轮 — Agent 记得上下文
result2 = agent.run_conversation(
    "What's my name?",
    conversation_history=history,
)
print(result2["final_response"])  # "Your name is Alice."
```

`conversation_history` 参数接收来自先前结果的 `messages` 列表。Agent 会在内部复制它，因此你的原始列表永远不会被修改。

---

## 保存轨迹 (Trajectories)

启用轨迹保存以 ShareGPT 格式捕获对话 —— 这对于生成训练数据或调试非常有用：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    save_trajectories=True,
    quiet_mode=True,
)

agent.chat("Write a Python function to sort a list")
# 以 ShareGPT 格式保存到 trajectory_samples.jsonl
```

每次对话都会作为一条 JSONL 行追加，方便从自动化运行中收集数据集。

---

## 自定义系统提示词

使用 `ephemeral_system_prompt` 设置自定义系统提示词来引导 Agent 的行为，但该提示词**不会**保存到轨迹文件中（保持训练数据的纯净）：

```python
agent = AIAgent(
    model="anthropic/claude-sonnet-4",
    ephemeral_system_prompt="You are a SQL expert. Only answer database questions.",
    quiet_mode=True,
)

response = agent.chat("How do I write a JOIN query?")
print(response)
```

这非常适合构建专用 Agent —— 代码审查员、文档撰写者、SQL 助手 —— 它们都使用相同的底层工具。

---

## 批量处理

为了并行运行多个提示词，Hermes 包含了 `batch_runner.py`。它管理具有适当资源隔离的并发 `AIAgent` 实例：

```bash
python batch_runner.py --input prompts.jsonl --output results.jsonl
```

每个提示词都有自己的 `task_id` 和隔离环境。如果你需要自定义批量逻辑，可以直接使用 `AIAgent` 构建：

```python
import concurrent.futures
from run_agent import AIAgent

prompts = [
    "Explain recursion",
    "What is a hash table?",
    "How does garbage collection work?",
]

def process_prompt(prompt):
    # 为每个任务创建一个新的 Agent 以确保线程安全
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

:::warning 警告
务必**为每个线程或任务创建一个新的 `AIAgent` 实例**。Agent 维护的内部状态（对话历史、工具会话、迭代计数器）不是线程安全的，不能共享。
:::

---

## 集成示例

### FastAPI 接口

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

### CI/CD 流水线步骤

```python
#!/usr/bin/env python3
"""CI 步骤：自动审查 PR diff。"""
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
    f"Review this PR diff for bugs, security issues, and style problems:\n\n{diff}"
)
print(review)
```

---

## 关键构造函数参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `model` | `str` | `"anthropic/claude-opus-4.6"` | OpenRouter 格式的模型名称 |
| `quiet_mode` | `bool` | `False` | 抑制 CLI 输出 |
| `enabled_toolsets` | `List[str]` | `None` | 白名单：启用特定工具集 |
| `disabled_toolsets` | `List[str]` | `None` | 黑名单：禁用特定工具集 |
| `save_trajectories` | `bool` | `False` | 将对话保存到 JSONL |
| `ephemeral_system_prompt` | `str` | `None` | 自定义系统提示词（不保存到轨迹） |
| `max_iterations` | `int` | `90` | 每次对话的最大工具调用迭代次数 |
| `skip_context_files` | `bool` | `False` | 跳过加载 AGENTS.md 文件 |
| `skip_memory` | `bool` | `False` | 禁用持久化记忆的读/写 |
| `api_key` | `str` | `None` | API 密钥（若未提供则回退到环境变量） |
| `base_url` | `str` | `None` | 自定义 API 端点 URL |
| `platform` | `str` | `None` | 平台提示（`"discord"`, `"telegram"` 等） |
---

## 重要说明

:::tip
- 如果你不希望将工作目录中的 `AGENTS.md` 文件加载到系统提示词（system prompt）中，请设置 **`skip_context_files=True`**。
- 设置 **`skip_memory=True`** 可以防止 Agent 读取或写入持久化记忆 —— 建议在无状态的 API 接口中使用。
- `platform` 参数（例如 `"discord"`、`"telegram"`）会注入特定平台的格式化提示，以便 Agent 调整其输出风格。
:::

:::warning
- **线程安全**：请为每个线程或任务创建一个独立的 `AIAgent` 实例。切勿在并发调用中共享同一个实例。
- **资源清理**：Agent 会在对话结束时自动清理资源（终端会话、浏览器实例）。如果你在长生命周期的进程中运行，请确保每次对话都能正常完成。
- **迭代限制**：默认的 `max_iterations=90` 比较宽松。对于简单的问答场景，建议调低该值（例如 `max_iterations=10`），以防止失控的工具调用循环并控制成本。
:::
