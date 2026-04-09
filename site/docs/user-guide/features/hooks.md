---
sidebar_position: 6
title: "事件钩子 (Event Hooks)"
description: "在关键生命周期节点运行自定义代码 —— 记录日志、发送警报、推送 Webhooks"
---

# 事件钩子 (Event Hooks)

Hermes 拥有两套钩子系统，用于在关键生命周期节点运行自定义代码：

| 系统 | 注册方式 | 运行环境 | 使用场景 |
|--------|---------------|---------|----------|
| **[Gateway 钩子](#gateway-event-hooks)** | `~/.hermes/hooks/` 下的 `HOOK.yaml` + `handler.py` | 仅限 Gateway | 日志记录、警报、Webhooks |
| **[Plugin 钩子](#plugin-hooks)** | [Plugin](/user-guide/features/plugins) 中的 `ctx.register_hook()` | CLI + Gateway | 工具拦截、指标统计、护栏 (Guardrails) |

这两套系统都是非阻塞的 —— 任何钩子中的错误都会被捕获并记录日志，绝不会导致 Agent 崩溃。

## Gateway 事件钩子 {#gateway-event-hooks}

Gateway 钩子在 Gateway 运行期间（Telegram、Discord、Slack、WhatsApp）自动触发，且不会阻塞 Agent 的主流水线。

### 创建钩子

每个钩子都是 `~/.hermes/hooks/` 下的一个目录，包含两个文件：

```text
~/.hermes/hooks/
└── my-hook/
    ├── HOOK.yaml      # 声明要监听哪些事件
    └── handler.py     # Python 处理函数
```

#### HOOK.yaml

```yaml
name: my-hook
description: 将所有 Agent 活动记录到文件
events:
  - agent:start
  - agent:end
  - agent:step
```

`events` 列表决定了哪些事件会触发你的处理器。你可以订阅任何事件组合，包括像 `command:*` 这样的通配符。

#### handler.py

```python
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".hermes" / "hooks" / "my-hook" / "activity.log"

async def handle(event_type: str, context: dict):
    """每个订阅的事件都会调用此函数。必须命名为 'handle'。"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        **context,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**处理器规则：**
- 必须命名为 `handle`
- 接收 `event_type` (字符串) 和 `context` (字典)
- 可以是 `async def` 或普通的 `def` —— 两者均可工作
- 错误会被捕获并记录，绝不会导致 Agent 崩溃

### 可用事件

| 事件 | 触发时机 | Context 键名 |
|-------|---------------|--------------|
| `gateway:startup` | Gateway 进程启动 | `platforms` (活跃平台名称列表) |
| `session:start` | 创建新的消息会话 | `platform`, `user_id`, `session_id`, `session_key` |
| `session:end` | 会话结束（重置前） | `platform`, `user_id`, `session_key` |
| `session:reset` | 用户运行了 `/new` 或 `/reset` | `platform`, `user_id`, `session_key` |
| `agent:start` | Agent 开始处理消息 | `platform`, `user_id`, `session_id`, `message` |
| `agent:step` | 工具调用循环的每一次迭代 | `platform`, `user_id`, `session_id`, `iteration`, `tool_names` |
| `agent:end` | Agent 完成处理 | `platform`, `user_id`, `session_id`, `message`, `response` |
| `command:*` | 执行任何斜杠命令 | `platform`, `user_id`, `command`, `args` |

#### 通配符匹配

注册为 `command:*` 的处理器会针对任何 `command:` 事件（如 `command:model`、`command:reset` 等）触发。只需一次订阅即可监控所有斜杠命令。

### 示例

#### 启动检查清单 (BOOT.md) —— 内置功能

Gateway 自带一个内置的 `boot-md` 钩子，每次启动时都会查找 `~/.hermes/BOOT.md`。如果该文件存在，Agent 会在后台会话中执行其中的指令。无需安装 —— 只需创建文件即可。

**创建 `~/.hermes/BOOT.md`：**

```markdown
# 启动检查清单

1. 检查昨晚是否有 cron 任务失败 —— 运行 `hermes cron list`
2. 向 Discord 的 #general 频道发送消息 "Gateway 已重启，所有系统正常运行"
3. 检查 /opt/app/deploy.log 在过去 24 小时内是否有任何错误
```

Agent 会在后台线程运行这些指令，因此不会阻塞 Gateway 的启动。如果没有需要注意的事项，Agent 会回复 `[SILENT]`，且不会发送任何消息。

:::tip
没有 BOOT.md？钩子会静默跳过 —— 零开销。当你需要启动自动化时随时创建该文件，不需要时删除即可。
:::

#### 长任务 Telegram 提醒

当 Agent 执行超过 10 个步骤时给自己发条消息：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: 当 Agent 步骤过多时发出警报
events:
  - agent:step
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
import os
import httpx

THRESHOLD = 10
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_HOME_CHANNEL")

async def handle(event_type: str, context: dict):
    iteration = context.get("iteration", 0)
    if iteration == THRESHOLD and BOT_TOKEN and CHAT_ID:
        tools = ", ".join(context.get("tool_names", []))
        text = f"⚠️ Agent 已运行 {iteration} 个步骤。最近使用的工具: {tools}"
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": text},
            )
```

#### 命令使用日志记录器

追踪使用了哪些斜杠命令：

```yaml
# ~/.hermes/hooks/command-logger/HOOK.yaml
name: command-logger
description: 记录斜杠命令的使用情况
events:
  - command:*
```

```python
# ~/.hermes/hooks/command-logger/handler.py
import json
from datetime import datetime
from pathlib import Path

LOG = Path.home() / ".hermes" / "logs" / "command_usage.jsonl"

def handle(event_type: str, context: dict):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "command": context.get("command"),
        "args": context.get("args"),
        "platform": context.get("platform"),
        "user": context.get("user_id"),
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

#### 会话启动 Webhook

在新会话开始时向外部服务发送 POST 请求：

```yaml
# ~/.hermes/hooks/session-webhook/HOOK.yaml
name: session-webhook
description: 在新会话开始时通知外部服务
events:
  - session:start
  - session:reset
```

```python
# ~/.hermes/hooks/session-webhook/handler.py
import httpx

WEBHOOK_URL = "https://your-service.example.com/hermes-events"

async def handle(event_type: str, context: dict):
    async with httpx.AsyncClient() as client:
        await client.post(WEBHOOK_URL, json={
            "event": event_type,
            **context,
        }, timeout=5)
```

### 工作原理

1. 在 Gateway 启动时，`HookRegistry.discover_and_load()` 会扫描 `~/.hermes/hooks/`。
2. 每个包含 `HOOK.yaml` + `handler.py` 的子目录都会被动态加载。
3. 处理器会根据其声明的事件进行注册。
4. 在每个生命周期节点，`hooks.emit()` 会触发所有匹配的处理器。
5. 任何处理器中的错误都会被捕获并记录 —— 损坏的钩子永远不会导致 Agent 崩溃。

:::info
Gateway 钩子仅在 **Gateway**（Telegram、Discord、Slack、WhatsApp）中触发。CLI 不会加载 Gateway 钩子。对于需要在所有环境下运行的钩子，请使用 [Plugin 钩子](#plugin-hooks)。
:::

## Plugin 钩子 {#plugin-hooks}
<a id="pre_api_request"></a>
<a id="post_api_request"></a>

[Plugins](/user-guide/features/plugins) 可以注册在 **CLI 和 Gateway** 会话中都能触发的钩子。这些钩子是通过 Plugin 的 `register()` 函数中的 `ctx.register_hook()` 以编程方式注册的。

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", my_tool_observer)
    ctx.register_hook("post_tool_call", my_tool_logger)
    ctx.register_hook("pre_llm_call", my_memory_callback)
    ctx.register_hook("post_llm_call", my_sync_callback)
    ctx.register_hook("on_session_start", my_init_callback)
    ctx.register_hook("on_session_end", my_cleanup_callback)
```

**所有钩子的通用规则：**

- 回调函数接收 **关键字参数 (keyword arguments)**。请务必接收 `**kwargs` 以保证向前兼容性 —— 未来版本可能会添加新参数而不会破坏你的 Plugin。
- 如果回调函数 **崩溃**，它会被记录并跳过。其他钩子和 Agent 将继续正常运行。行为异常的 Plugin 永远不会破坏 Agent。
- 所有钩子都是 **“发后即忘”的观察者**，其返回值会被忽略 —— 只有 `pre_llm_call` 除外，它可以[注入上下文](#pre_llm_call)。
### 快速参考

| Hook 钩子 | 触发时机 | 返回值 |
|------|-----------|---------|
| [`pre_tool_call`](#pre_tool_call) | 任何工具执行前 | 忽略 |
| [`post_tool_call`](#post_tool_call) | 任何工具返回后 | 忽略 |
| [`pre_llm_call`](#pre_llm_call) | 每轮对话一次，在工具调用循环之前 | 上下文注入 |
| [`post_llm_call`](#post_llm_call) | 每轮对话一次，在工具调用循环之后 | 忽略 |
| [`on_session_start`](#on_session_start) | 新会话创建时（仅限第一轮） | 忽略 |
| [`on_session_end`](#on_session_end) | 会话结束时 | 忽略 |

---

### `pre_tool_call`

在每次工具执行**之前立即**触发 —— 无论是内置工具还是插件工具。

**回调签名：**

```python
def my_callback(tool_name: str, args: dict, task_id: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 即将执行的工具名称（例如 `"terminal"`, `"web_search"`, `"read_file"`） |
| `args` | `dict` | 模型传递给工具的参数 |
| `task_id` | `str` | 会话/任务标识符。如果未设置则为空字符串。 |

**触发位置：** 在 `model_tools.py` 的 `handle_function_call()` 内部，工具处理器运行之前。每次工具调用触发一次 —— 如果模型并行调用了 3 个工具，则此钩子触发 3 次。

**返回值：** 忽略。

**使用场景：** 日志记录、审计追踪、工具调用计数、拦截危险操作（打印警告）、速率限制。

**示例 —— 工具调用审计日志：**

```python
import json, logging
from datetime import datetime

logger = logging.getLogger(__name__)

def audit_tool_call(tool_name, args, task_id, **kwargs):
    logger.info("TOOL_CALL session=%s tool=%s args=%s",
                task_id, tool_name, json.dumps(args)[:200])

def register(ctx):
    ctx.register_hook("pre_tool_call", audit_tool_call)
```

**示例 —— 危险工具警告：**

```python
DANGEROUS = {"terminal", "write_file", "patch"}

def warn_dangerous(tool_name, **kwargs):
    if tool_name in DANGEROUS:
        print(f"⚠ 正在执行潜在的危险工具: {tool_name}")

def register(ctx):
    ctx.register_hook("pre_tool_call", warn_dangerous)
```

---

### `post_tool_call`

在每次工具执行返回后**立即**触发。

**回调签名：**

```python
def my_callback(tool_name: str, args: dict, result: str, task_id: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 刚刚执行完毕的工具名称 |
| `args` | `dict` | 模型传递给工具的参数 |
| `result` | `str` | 工具的返回值（始终为 JSON 字符串） |
| `task_id` | `str` | 会话/任务标识符。如果未设置则为空字符串。 |

**触发位置：** 在 `model_tools.py` 的 `handle_function_call()` 内部，工具处理器返回之后。每次工具调用触发一次。如果工具抛出了未处理的异常，则**不会**触发（错误会被捕获并作为错误 JSON 字符串返回，此时 `post_tool_call` 会以该错误字符串作为 `result` 触发）。

**返回值：** 忽略。

**使用场景：** 记录工具结果、指标收集、追踪工具成功/失败率、在特定工具完成时发送通知。

**示例 —— 追踪工具使用指标：**

```python
from collections import Counter
import json

_tool_counts = Counter()
_error_counts = Counter()

def track_metrics(tool_name, result, **kwargs):
    _tool_counts[tool_name] += 1
    try:
        parsed = json.loads(result)
        if "error" in parsed:
            _error_counts[tool_name] += 1
    except (json.JSONDecodeError, TypeError):
        pass

def register(ctx):
    ctx.register_hook("post_tool_call", track_metrics)
```

---

### `pre_llm_call`

**每轮对话触发一次**，在工具调用循环开始之前。这是**唯一一个返回值会被使用**的钩子 —— 它可以向当前轮次的用户消息中注入上下文。

**回调签名：**

```python
def my_callback(session_id: str, user_message: str, conversation_history: list,
                is_first_turn: bool, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 用户在本轮的原始消息（在任何技能注入之前） |
| `conversation_history` | `list` | 完整消息列表的副本（OpenAI 格式：`[{"role": "user", "content": "..."}]`） |
| `is_first_turn` | `bool` | 如果是新会话的第一轮则为 `True`，后续轮次为 `False` |
| `model` | `str` | 模型标识符（例如 `"anthropic/claude-sonnet-4.6"`） |
| `platform` | `str` | 会话运行的平台：`"cli"`, `"telegram"`, `"discord"` 等 |

**触发位置：** 在 `run_agent.py` 的 `run_conversation()` 内部，上下文压缩之后但在主 `while` 循环之前。每次 `run_conversation()` 调用触发一次（即每个用户轮次一次），而不是在工具循环内的每次 API 调用都触发。

**返回值：** 如果回调返回一个包含 `"context"` 键的字典，或者一个非空的普通字符串，该文本将被追加到当前轮次的用户消息中。返回 `None` 则不注入。

```python
# 注入上下文
return {"context": "召回的记忆：\n- 用户喜欢 Python\n- 正在开发 hermes-agent"}

# 普通字符串（等效）
return "召回的记忆：\n- 用户喜欢 Python"

# 不注入
return None
```

**上下文注入位置：** 始终注入到**用户消息**中，绝不会注入到系统提示词（system prompt）。这样可以保护提示词缓存（prompt cache）—— 系统提示词在不同轮次间保持一致，从而复用缓存的 token。系统提示词是 Hermes 的领地（模型引导、工具强制执行、性格、技能）。插件则在用户输入旁提供补充上下文。

所有注入的上下文都是**临时性的** —— 仅在 API 调用时添加。对话历史中的原始用户消息永远不会被修改，也不会持久化到会话数据库中。

当**多个插件**返回上下文时，它们的输出将按插件发现顺序（按目录名字母顺序）用双换行符连接。

**使用场景：** 记忆召回、RAG 上下文注入、护栏（guardrails）、每轮分析。

**示例 —— 记忆召回：**

```python
import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall(session_id, user_message, is_first_turn, **kwargs):
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None
        text = "召回的上下文：\n" + "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None

def register(ctx):
    ctx.register_hook("pre_llm_call", recall)
```

**示例 —— 护栏：**

```python
POLICY = "未经用户明确确认，严禁执行删除文件的命令。"

def guardrails(**kwargs):
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", guardrails)
```

---

### `post_llm_call`

**每轮对话触发一次**，在工具调用循环完成且 Agent 生成最终响应之后。仅在**成功**的轮次触发 —— 如果轮次被中断则不会触发。

**回调签名：**

```python
def my_callback(session_id: str, user_message: str, assistant_response: str,
                conversation_history: list, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 用户在本轮的原始消息 |
| `assistant_response` | `str` | Agent 在本轮的最终文本响应 |
| `conversation_history` | `list` | 轮次完成后完整消息列表的副本 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的平台 |
**触发时机：** 在 `run_agent.py` 的 `run_conversation()` 函数中，当工具循环（tool loop）结束并获得最终回复后触发。受 `if final_response and not interrupted` 条件保护 —— 因此，当用户在中途打断或 Agent 达到迭代上限且未生成回复时，该钩子**不会**触发。

**返回值：** 忽略。

**使用场景：** 将对话数据同步到外部记忆系统、计算回复质量指标、记录轮次摘要、触发后续动作。

**示例 —— 同步到外部记忆：**

```python
import httpx

MEMORY_API = "https://your-memory-api.example.com"

def sync_memory(session_id, user_message, assistant_response, **kwargs):
    try:
        httpx.post(f"{MEMORY_API}/store", json={
            "session_id": session_id,
            "user": user_message,
            "assistant": assistant_response,
        }, timeout=5)
    except Exception:
        pass  # 尽力而为，忽略错误
```

**示例 —— 追踪回复长度：**

```python
import logging
logger = logging.getLogger(__name__)

def log_response_length(session_id, assistant_response, model, **kwargs):
    logger.info("RESPONSE session=%s model=%s chars=%d",
                session_id, model, len(assistant_response or ""))

def register(ctx):
    ctx.register_hook("post_llm_call", log_response_length)
```

---

### `on_session_start`

在一个全新的会话（session）创建时触发**一次**。在会话持续过程中（即用户在现有会话中发送后续消息时）**不会**触发。

**回调签名：**

```python
def my_callback(session_id: str, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的唯一标识符 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的平台 |

**触发时机：** 在 `run_agent.py` 的 `run_conversation()` 中，新会话的第一轮对话期间触发 —— 具体是在系统提示词（system prompt）构建之后、工具循环开始之前。检查条件为 `if not conversation_history`（无历史消息 = 新会话）。

**返回值：** 忽略。

**使用场景：** 初始化会话作用域的状态、预热缓存、在外部服务中注册会话、记录会话启动日志。

**示例 —— 初始化会话缓存：**

```python
_session_caches = {}

def init_session(session_id, model, platform, **kwargs):
    _session_caches[session_id] = {
        "model": model,
        "platform": platform,
        "tool_calls": 0,
        "started": __import__("datetime").datetime.now().isoformat(),
    }

def register(ctx):
    ctx.register_hook("on_session_start", init_session)
```

---

### `on_session_end`

在每次 `run_conversation()` 调用结束时触发，无论结果如何。如果用户在 Agent 运行中途退出，CLI 的退出处理器也会触发此钩子。

**回调签名：**

```python
def my_callback(session_id: str, completed: bool, interrupted: bool,
                model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 会话的唯一标识符 |
| `completed` | `bool` | 如果 Agent 生成了最终回复则为 `True`，否则为 `False` |
| `interrupted` | `bool` | 如果该轮对话被中断（用户发送新消息、输入 `/stop` 或退出）则为 `True` |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的平台 |

**触发时机：** 共有两处：
1. **`run_agent.py`** —— 在每次 `run_conversation()` 调用结束、完成所有清理工作后。无论该轮对话是否报错，都会触发。
2. **`cli.py`** —— 在 CLI 的 atexit 处理器中，但**仅当**退出发生时 Agent 正在运行中（`_agent_running=True`）。这会捕获处理过程中的 Ctrl+C 和 `/exit`。在这种情况下，`completed=False` 且 `interrupted=True`。

**返回值：** 忽略。

**使用场景：** 刷新缓冲区、关闭连接、持久化会话状态、记录会话时长、清理在 `on_session_start` 中初始化的资源。

**示例 —— 刷新并清理：**

```python
_session_caches = {}

def cleanup_session(session_id, completed, interrupted, **kwargs):
    cache = _session_caches.pop(session_id, None)
    if cache:
        # 将累积的数据刷新到磁盘或外部服务
        status = "completed" if completed else ("interrupted" if interrupted else "failed")
        print(f"Session {session_id} ended: {status}, {cache['tool_calls']} tool calls")

def register(ctx):
    ctx.register_hook("on_session_end", cleanup_session)
```

**示例 —— 会话时长追踪：**

```python
import time, logging
logger = logging.getLogger(__name__)

_start_times = {}

def on_start(session_id, **kwargs):
    _start_times[session_id] = time.time()

def on_end(session_id, completed, interrupted, **kwargs):
    start = _start_times.pop(session_id, None)
    if start:
        duration = time.time() - start
        logger.info("SESSION_DURATION session=%s seconds=%.1f completed=%s interrupted=%s",
                     session_id, duration, completed, interrupted)

def register(ctx):
    ctx.register_hook("on_session_start", on_start)
    ctx.register_hook("on_session_end", on_end)
```

---

请参阅 **[构建 Plugin 指南](/guides/build-a-hermes-plugin)** 以获取完整教程，包括工具 Schema、处理器以及高级 Hook 模式。
