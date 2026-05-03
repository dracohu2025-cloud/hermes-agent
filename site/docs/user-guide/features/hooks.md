---
sidebar_position: 6
title: "事件钩子"
description: "在关键生命周期点运行自定义代码——记录活动、发送告警、推送到 Webhook"
---

# 事件钩子 {#event-hooks}

Hermes 提供了三种钩子系统，用于在关键生命周期点运行自定义代码：

| 系统 | 注册方式 | 运行环境 | 使用场景 |
|------|----------|----------|----------|
| **[网关钩子](#gateway-event-hooks)** | `HOOK.yaml` + `handler.py` 位于 `~/.hermes/hooks/` | 仅限网关 | 日志记录、告警、Webhook |
| **[插件钩子](#plugin-hooks)** | 在[插件](/user-guide/features/plugins)中调用 `ctx.register_hook()` | CLI + 网关 | 工具拦截、指标收集、安全护栏 |
| **[Shell 钩子](#shell-hooks)** | `~/.hermes/config.yaml` 中的 `hooks:` 块指向 shell 脚本 | CLI + 网关 | 直接可用的脚本，用于阻断、自动格式化、上下文注入 |

三种系统均为非阻塞——任何钩子中的错误都会被捕获并记录，不会导致 Agent 崩溃。

## 网关事件钩子 {#gateway-event-hooks}

网关钩子在网关运行期间（Telegram、Discord、Slack、WhatsApp）自动触发，不会阻塞主 Agent 流水线。

### 创建钩子 {#creating-a-hook}

每个钩子是 `~/.hermes/hooks/` 下的一个目录，包含两个文件：

```text
~/.hermes/hooks/
└── my-hook/
    ├── HOOK.yaml      # 声明要监听的事件
    └── handler.py     # Python 处理函数
```

#### HOOK.yaml {#hook-yaml}

```yaml
name: my-hook
description: 将 Agent 所有活动记录到文件
events:
  - agent:start
  - agent:end
  - agent:step
```

`events` 列表决定哪些事件会触发你的处理函数。你可以订阅任意事件组合，包括通配符如 `command:*`。

#### handler.py {#handler-py}
```python
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".hermes" / "hooks" / "my-hook" / "activity.log"

async def handle(event_type: str, context: dict):
    """Called for each subscribed event. Must be named 'handle'."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        **context,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**处理程序规则：**
- 必须命名为 `handle`
- 接收 `event_type`（字符串）和 `context`（字典）
- 可以是 `async def` 或普通 `def`——两者都有效
- 错误会被捕获并记录，不会导致 Agent 崩溃

### 可用事件 {#available-events}

| 事件 | 触发时机 | 上下文键 |
|-------|---------------|--------------|
| `gateway:startup` | 网关进程启动时 | `platforms`（活跃平台名称列表） |
| `session:start` | 新消息会话创建时 | `platform`, `user_id`, `session_id`, `session_key` |
| `session:end` | 会话结束时（重置前） | `platform`, `user_id`, `session_key` |
| `session:reset` | 用户运行 `/new` 或 `/reset` 时 | `platform`, `user_id`, `session_key` |
| `agent:start` | Agent 开始处理消息时 | `platform`, `user_id`, `session_id`, `message` |
| `agent:step` | 工具调用循环的每次迭代 | `platform`, `user_id`, `session_id`, `iteration`, `tool_names` |
| `agent:end` | Agent 处理完成时 | `platform`, `user_id`, `session_id`, `message`, `response` |
| `command:*` | 执行任何斜杠命令时 | `platform`, `user_id`, `command`, `args` |
#### 通配符匹配 {#wildcard-matching}

为 `command:*` 注册的处理程序会响应任何 `command:` 事件（如 `command:model`、`command:reset` 等）。通过单个订阅即可监控所有斜杠命令。

### 示例 {#examples}

#### 长时间任务时发送 Telegram 提醒 {#telegram-alert-on-long-tasks}

当 Agent 执行超过 10 步时，给自己发送一条消息：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: Alert when agent is taking many steps
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
        text = f"⚠️ Agent has been running for {iteration} steps. Last tools: {tools}"
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": text},
            )
```

#### 命令使用日志记录 {#command-usage-logger}

追踪哪些斜杠命令被使用：

```yaml
# ~/.hermes/hooks/command-logger/HOOK.yaml
name: command-logger
description: Log slash command usage
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
#### 会话启动 Webhook {#session-start-webhook}

在新会话启动时向外部服务发送 POST 请求：

```yaml
# ~/.hermes/hooks/session-webhook/HOOK.yaml
name: session-webhook
description: 在新会话启动时通知外部服务
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

### 教程：BOOT.md — 每次网关启动时运行启动检查清单 {#tutorial-boot-md-run-a-startup-checklist-on-every-gateway-boot}

社区中一个流行的模式：在 `~/.hermes/BOOT.md` 中放置一个 Markdown 检查清单，让 Agent 在每次网关启动时运行一次。适用于“每次启动时，检查昨晚的 cron 任务是否失败，如果有失败则在 Discord 上通知我”，或者“总结过去 24 小时的 deploy.log 并发布到 Slack #ops 频道”。

本教程将展示如何通过用户自定义钩子自行构建此功能。Hermes 并未内置 BOOT.md 钩子——你需要自己配置所需的行为。

#### 我们要构建的内容 {#what-we-re-building}

1. 一个位于 `~/.hermes/BOOT.md` 的文件，包含自然语言的启动指令。
2. 一个网关钩子，在 `gateway:startup` 事件触发，生成一个一次性 Agent（使用你网关已解析的模型/凭据），并执行 BOOT.md 中的指令。
3. 一个 `[SILENT]` 约定，使得 Agent 在无内容可报告时可以选择不发送消息。
#### 步骤 1：编写你的检查清单 {#step-1-write-your-checklist}

创建 `~/.hermes/BOOT.md`。像给人类助手写指令一样编写它：

```markdown
# 启动检查清单

1. 运行 `hermes cron list`，检查是否有任何定时任务在夜间失败。
2. 如果有失败的任务，使用 `send_message` 工具将摘要发送到 Discord #ops 频道。
3. 检查 `/opt/app/deploy.log` 中过去 24 小时内是否有 ERROR 行。如果有，总结它们并包含在同一条 Discord 消息中。
4. 如果一切正常，只回复 `[SILENT]`，这样就不会发送任何消息。
```

Agent 会将其视为提示的一部分，因此任何可以用自然语言描述的内容都可以生效——工具调用、shell 命令、发送消息、总结文件。

#### 步骤 2：创建 Hook {#step-2-create-the-hook}

```text
~/.hermes/hooks/boot-md/
├── HOOK.yaml
└── handler.py
```

**`~/.hermes/hooks/boot-md/HOOK.yaml`**

```yaml
name: boot-md
description: Run ~/.hermes/BOOT.md on gateway startup
events:
  - gateway:startup
```

**`~/.hermes/hooks/boot-md/handler.py`**

```python
"""Run ~/.hermes/BOOT.md on every gateway startup."""

import logging
import threading
from pathlib import Path

logger = logging.getLogger("hooks.boot-md")

BOOT_FILE = Path.home() / ".hermes" / "BOOT.md"


def _build_prompt(content: str) -> str:
    return (
        "You are running a startup boot checklist. Follow the instructions "
        "below exactly.\n\n"
        "---\n"
        f"{content}\n"
        "---\n\n"
        "Execute each instruction. Use the send_message tool to deliver any "
        "messages to platforms like Discord or Slack.\n"
        "If nothing needs attention and there is nothing to report, reply "
        "with ONLY: [SILENT]"
    )


def _run_boot_agent(content: str) -> None:
    """Spawn a one-shot agent and execute the checklist.

    Uses the gateway's resolved model and runtime credentials so this works
    against custom endpoints, aggregators, and OAuth-based providers alike.
    """
    try:
        from gateway.run import _resolve_gateway_model, _resolve_runtime_agent_kwargs
        from run_agent import AIAgent

        agent = AIAgent(
            model=_resolve_gateway_model(),
            **_resolve_runtime_agent_kwargs(),
            platform="gateway",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            max_iterations=20,
        )
        result = agent.run_conversation(_build_prompt(content))
        response = result.get("final_response", "")
        if response and "[SILENT]" not in response:
            logger.info("boot-md completed: %s", response[:200])
        else:
            logger.info("boot-md completed (nothing to report)")
    except Exception as e:
        logger.error("boot-md agent failed: %s", e)


async def handle(event_type: str, context: dict) -> None:
    if not BOOT_FILE.exists():
        return
    content = BOOT_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return

    logger.info("Running BOOT.md (%d chars)", len(content))

    # Background thread so gateway startup isn't blocked on a full agent turn.
    thread = threading.Thread(
        target=_run_boot_agent,
        args=(content,),
        name="boot-md",
        daemon=True,
    )
    thread.start()
```
两个关键行：

- `_resolve_gateway_model()` 读取网关当前配置的模型。
- `_resolve_runtime_agent_kwargs()` 以与普通网关 turn 相同的方式解析 provider 凭证——包括 API 密钥、base URL、OAuth 令牌和凭证池。

如果没有这些，一个裸的 `AIAgent()` 会回退到内置默认值，并对任何非默认端点返回 401。

#### 第三步：测试 {#step-3-test-it}

重启网关：

```bash
hermes gateway restart
```

查看日志：

```bash
hermes logs --follow --level INFO | grep boot-md
```

你应该会看到 `Running BOOT.md (N chars)`，随后是 `boot-md completed: ...`（Agent 所做操作的摘要）或 `boot-md completed (nothing to report)`（当 Agent 回复 `[SILENT]` 时）。

删除 `~/.hermes/BOOT.md` 以禁用检查清单——钩子仍然保持加载状态，但当文件不存在时会静默跳过。

#### 扩展模式 {#extending-the-pattern}

- **定时检查清单：** 在 BOOT.md 的指令中使用 `datetime.now().weekday()` 作为判断依据（“如果是周一，还要检查每周部署日志”）。指令是自由格式文本，因此 Agent 能推理的任何内容都可以使用。
- **多个检查清单：** 将钩子指向不同的文件（`STARTUP.md`、`MORNING.md` 等），并为每个文件注册单独的钩子目录。
- **非 Agent 变体：** 如果你不需要完整的 Agent 循环，可以完全跳过 `AIAgent`，让处理程序通过 `httpx` 直接发布固定通知。更便宜、更快，且没有 provider 依赖。

#### 为什么这不是内置功能 {#why-this-isn-t-a-built-in}
Hermes 的早期版本将此功能作为内置钩子提供，并在每次网关启动时静默生成一个使用默认配置的 agent。这让拥有自定义端点的用户感到意外，也让不知道它在运行的用户无法察觉该功能。将其保留为一种有文档记录的模式——由你在 hooks 目录中自行构建——意味着你能清楚看到它的作用，并通过编写文件来选择启用。

### 工作原理 {#how-it-works}

1. 网关启动时，`HookRegistry.discover_and_load()` 扫描 `~/.hermes/hooks/`
2. 每个包含 `HOOK.yaml` + `handler.py` 的子目录会被动态加载
3. 处理器会注册到它们声明的事件上
4. 在每个生命周期节点，`hooks.emit()` 触发所有匹配的处理器
5. 任何处理器中的错误都会被捕获并记录——一个损坏的钩子永远不会导致 agent 崩溃

:::info
网关钩子仅在**网关**（Telegram、Discord、Slack、WhatsApp）中触发。CLI 不会加载网关钩子。如需在所有地方都能工作的钩子，请使用[插件钩子](#plugin-hooks)。
:::

## 插件钩子 {#plugin-hooks}

[插件](/user-guide/features/plugins)可以注册在 **CLI 和网关**会话中都能触发的钩子。这些钩子通过插件 `register()` 函数中的 `ctx.register_hook()` 以编程方式注册。

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

- 回调函数接收**关键字参数**。请始终接受 `**kwargs` 以保证向前兼容——未来版本可能新增参数，而不会破坏你的插件。
- 如果某个回调**崩溃**，它会被记录并跳过。其他钩子和 agent 会正常运行。一个行为异常的插件永远不会导致 agent 崩溃。
- 两个钩子的返回值会影响行为：[`pre_tool_call`](#pre_tool_call) 可以**阻止**工具执行，[`pre_llm_call`](#pre_llm_call) 可以**注入上下文**到 LLM 调用中。所有其他钩子都是“即发即忘”的观察者。

### 快速参考 {#quick-reference}

| 钩子 | 触发时机 | 返回值 |
|------|---------|-------|
| [`pre_tool_call`](#pre_tool_call) | 任何工具执行之前 | `{"action": "block", "message": str}` 用于否决调用 |
| [`post_tool_call`](#post_tool_call) | 任何工具返回之后 | 忽略 |
| [`pre_llm_call`](#pre_llm_call) | 每轮一次，在工具调用循环之前 | `{"context": str}` 用于在用户消息前追加上下文 |
| [`post_llm_call`](#post_llm_call) | 每轮一次，在工具调用循环之后 | 忽略 |
| [`on_session_start`](#on_session_start) | 新会话创建时（仅第一轮） | 忽略 |
| [`on_session_end`](#on_session_end) | 会话结束时 | 忽略 |
| [`on_session_finalize`](#on_session_finalize) | CLI/网关拆除活跃会话时（刷新、保存、统计） | 忽略 |
| [`on_session_reset`](#on_session_reset) | 网关换入新会话密钥时（例如 `/new`、`/reset`） | 忽略 |
| [`subagent_stop`](#subagent_stop) | `delegate_task` 子任务退出时 | 忽略 |
| [`pre_gateway_dispatch`](#pre_gateway_dispatch) | 网关收到用户消息后、认证+分发之前 | `{"action": "skip" \| "rewrite" \| "allow", ...}` 用于影响流程 |
| [`pre_approval_request`](#pre_approval_request) | 危险命令需要用户批准时，在发送提示/通知之前 | 忽略 |
| [`post_approval_response`](#post_approval_response) | 用户响应了批准提示（或超时）时 | 忽略 |
| [`transform_tool_result`](#transform_tool_result) | 任何工具返回之后、结果交回模型之前 | `str` 用于替换结果，`None` 表示不修改 |
| [`transform_terminal_output`](#transform_terminal_output) | 在 `terminal` 工具内部，截断/ANSI 剥离/脱敏之前 | `str` 用于替换原始输出，`None` 表示不修改 |
---

<a id="pretoolcall"></a>
### `pre_tool_call` {#pre_tool_call}

在每次工具执行（包括内置工具和插件工具）**之前立即**触发。

**回调签名：**

```python
def my_callback(tool_name: str, args: dict, task_id: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 即将执行的工具名称（例如 `"terminal"`、`"web_search"`、`"read_file"`） |
| `args` | `dict` | 模型传递给工具的参数 |
| `task_id` | `str` | 会话/任务标识符。如果未设置则为空字符串。 |

**触发时机：** 在 `model_tools.py` 的 `handle_function_call()` 内部，工具的处理程序运行之前。每次工具调用触发一次——如果模型并行调用 3 个工具，则触发 3 次。

**返回值——否决调用：**

```python
return {"action": "block", "message": "Reason the tool call was blocked"}
```

Agent 会以 `message` 作为返回给模型的错误信息，短路该工具。第一个匹配的阻止指令生效（Python 插件先注册，然后是 shell 钩子）。任何其他返回值都会被忽略，因此现有的仅观察者回调可以保持不变地继续工作。

**使用场景：** 日志记录、审计追踪、工具调用计数、阻止危险操作、速率限制、按用户执行策略。

**示例——工具调用审计日志：**

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
**示例 — 对危险工具发出警告：**

```python
DANGEROUS = {"terminal", "write_file", "patch"}

def warn_dangerous(tool_name, **kwargs):
    if tool_name in DANGEROUS:
        print(f"⚠ 正在执行潜在危险工具：{tool_name}")

def register(ctx):
    ctx.register_hook("pre_tool_call", warn_dangerous)
```

---

<a id="posttoolcall"></a>
### `post_tool_call` {#post_tool_call}

在每次工具执行返回后**立即**触发。

**回调签名：**

```python
def my_callback(tool_name: str, args: dict, result: str, task_id: str,
                duration_ms: int, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 刚刚执行的工具名称 |
| `args` | `dict` | 模型传递给工具的参数 |
| `result` | `str` | 工具的返回值（始终为 JSON 字符串） |
| `task_id` | `str` | 会话/任务标识符。如果未设置则为空字符串。 |
| `duration_ms` | `int` | 工具调度所花费的时间，以毫秒为单位（通过 `registry.dispatch()` 周围的 `time.monotonic()` 测量）。 |

**触发时机：** 在 `model_tools.py` 的 `handle_function_call()` 中，工具的处理程序返回之后触发。每次工具调用触发一次。如果工具引发了未处理的异常，则**不会**触发（该错误会被捕获并以错误 JSON 字符串的形式返回，而 `post_tool_call` 会以该错误字符串作为 `result` 触发）。

**返回值：** 忽略。

**使用场景：** 记录工具结果、指标收集、跟踪工具成功/失败率、延迟仪表板、按工具预算警报、在特定工具完成时发送通知。
**示例 — 追踪工具使用指标：**

```python
from collections import Counter, defaultdict
import json

_tool_counts = Counter()
_error_counts = Counter()
_latency_ms = defaultdict(list)

def track_metrics(tool_name, result, duration_ms=0, **kwargs):
    _tool_counts[tool_name] += 1
    _latency_ms[tool_name].append(duration_ms)
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

<a id="prellmcall"></a>
### `pre_llm_call` {#pre_llm_call}

**每轮触发一次**，在工具调用循环开始之前。这是**唯一一个返回值会被使用的钩子**——它可以向当前轮次的用户消息中注入上下文。

**回调签名：**

```python
def my_callback(session_id: str, user_message: str, conversation_history: list,
                is_first_turn: bool, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 本轮用户的原始消息（在任何技能注入之前） |
| `conversation_history` | `list` | 完整消息列表的副本（OpenAI 格式：`[{"role": "user", "content": "..."}]`） |
| `is_first_turn` | `bool` | 如果是新会话的第一轮则为 `True`，后续轮次为 `False` |
| `model` | `str` | 模型标识符（例如 `"anthropic/claude-sonnet-4.6"`） |
| `platform` | `str` | 会话运行平台：`"cli"`、`"telegram"`、`"discord"` 等 |
**触发时机：** 在 `run_agent.py` 的 `run_conversation()` 中，在上下文压缩之后、主 `while` 循环之前触发。每次调用 `run_conversation()`（即每个用户轮次）触发一次，而不是工具循环中的每次 API 调用都触发。

**返回值：** 如果回调函数返回含有 `"context"` 键的字典，或者返回一个非空字符串，则该文本会被附加到当前轮次的用户消息中。返回 `None` 则不注入任何内容。

```python
# 注入上下文
return {"context": "Recalled memories:\n- User likes Python\n- Working on hermes-agent"}

# 纯字符串（等价）
return "Recalled memories:\n- User likes Python"

# 不注入
return None
```

**上下文注入位置：** 始终是 **用户消息**，从不加入系统提示。这样可以保留提示缓存——系统提示在各轮次之间保持不变，因此缓存 token 会被重用。系统提示是 Hermes 的领地（模型引导、工具强制、个性、技能）。插件与用户输入一同贡献上下文。

所有注入的上下文都是 **临时的**——仅在 API 调用时添加。对话历史中的原始用户消息从未被修改，且不会持久化到会话数据库中。

当 **多个插件** 返回上下文时，它们的输出会按照插件发现顺序（按目录名称字母排序）以双换行符连接。

**使用场景：** 记忆召回、RAG 上下文注入、护栏、每轮分析。

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
        text = "Recalled context:\n" + "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None

def register(ctx):
    ctx.register_hook("pre_llm_call", recall)
```
**示例 — 护栏（guardrails）：**

```python
POLICY = "Never execute commands that delete files without explicit user confirmation."

def guardrails(**kwargs):
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", guardrails)
```

---

<a id="postllmcall"></a>
### `post_llm_call` {#post_llm_call}

**每轮触发一次**，在工具调用循环完成且 Agent 生成最终响应后触发。仅在**成功**的轮次中触发 — 如果该轮被中断，则不会触发。

**回调签名：**

```python
def my_callback(session_id: str, user_message: str, assistant_response: str,
                conversation_history: list, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 当前会话的唯一标识符 |
| `user_message` | `str` | 用户在该轮中的原始消息 |
| `assistant_response` | `str` | Agent 在该轮中的最终文本响应 |
| `conversation_history` | `list` | 该轮结束后完整消息列表的副本 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行所在的平台 |

**触发时机：** 在 `run_agent.py` 的 `run_conversation()` 中，当工具循环退出并产生最终响应后触发。受 `if final_response and not interrupted` 保护 — 因此当用户在轮次中中断或 Agent 达到迭代限制而未产生响应时，**不会**触发。

**返回值：** 忽略。

**使用场景：** 将会话数据同步到外部记忆系统、计算响应质量指标、记录轮次摘要、触发后续操作。
**示例 — 同步到外部存储：**

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
        pass  # 尽力而为

def register(ctx):
    ctx.register_hook("post_llm_call", sync_memory)
```

**示例 — 跟踪响应长度：**

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

<a id="onsessionstart"></a>
### `on_session_start` {#on_session_start}

在**全新**会话创建时**触发一次**。不会在会话延续（即用户在已有会话中发送第二条消息）时触发。

**回调签名：**

```python
def my_callback(session_id: str, model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的唯一标识符 |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行的位置 |

**触发时机：** 在 `run_agent.py` 的 `run_conversation()` 中，新会话的第一轮交互时触发——具体是在系统提示构建完成之后、工具循环开始之前。判断依据是 `if not conversation_history`（没有历史消息即为新会话）。
**返回值：** 忽略。

**使用场景：** 初始化会话级状态、预热缓存、在外部服务中注册会话、记录会话开始。

**示例——初始化会话缓存：**

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

<a id="onsessionend"></a>
### `on_session_end` {#on_session_end}

在每次 `run_conversation()` 调用的**最末尾**触发，无论结果如何。如果用户退出时 agent 正处于对话轮次中，也会从 CLI 的退出处理器触发。

**回调签名：**

```python
def my_callback(session_id: str, completed: bool, interrupted: bool,
                model: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 会话的唯一标识符 |
| `completed` | `bool` | 如果 agent 生成了最终响应则为 `True`，否则为 `False` |
| `interrupted` | `bool` | 如果该轮次被中断（用户发送新消息、`/stop` 或退出）则为 `True` |
| `model` | `str` | 模型标识符 |
| `platform` | `str` | 会话运行所在的平台 |

**触发位置：** 两处：
1. **`run_agent.py`** — 在每次 `run_conversation()` 调用结束时，所有清理工作完成后。即使该轮次出错也始终触发。
2. **`cli.py`** — 在 CLI 的 `atexit` 处理器中，但**仅当**退出发生时 agent 正处于轮次中（`_agent_running=True`）。这能捕获处理过程中的 Ctrl+C 和 `/exit`。在这种情况下，`completed=False` 且 `interrupted=True`。
**返回值：** 忽略。

**使用场景：** 刷新缓冲区、关闭连接、持久化会话状态、记录会话时长、清理在 `on_session_start` 中初始化的资源。

**示例 — 刷新与清理：**

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

**示例 — 会话时长跟踪：**

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

<a id="onsessionfinalize"></a>
### `on_session_finalize` {#on_session_finalize}

当 CLI 或网关**销毁**一个活动会话时触发——例如，用户运行 `/new`、网关 GC 回收了空闲会话、或 CLI 在有活跃 Agent 时退出。这是在其身份消失之前，刷新与即将关闭的会话关联状态的最后机会。
**回调签名：**

```python
def my_callback(session_id: str | None, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` 或 `None` | 即将结束的会话 ID。如果没有活跃会话，则可能为 `None`。 |
| `platform` | `str` | `"cli"` 或消息平台名称（`"telegram"`、`"discord"` 等）。 |

**触发时机：** 在 `cli.py`（`/new` / CLI 退出时）和 `gateway/run.py`（会话被重置或垃圾回收时）触发。在网关侧，始终与 `on_session_reset` 成对出现。

**返回值：** 忽略。

**使用场景：** 在会话 ID 被丢弃前持久化最终会话指标、关闭每个会话的资源、发送最终遥测事件、排空队列中的写入。

---

<a id="onsessionreset"></a>
### `on_session_reset` {#on_session_reset}

当网关为活跃聊天**换入新的会话键**时触发——用户调用了 `/new`、`/reset`、`/clear`，或者适配器在空闲窗口后选择了新会话。这让插件能够对会话状态已被清除这一事实做出反应，而无需等待下一次 `on_session_start`。

**回调签名：**

```python
def my_callback(session_id: str, platform: str, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `session_id` | `str` | 新会话的 ID（已轮换为新的值）。 |
| `platform` | `str` | 消息平台名称。 |

**触发时机：** 在 `gateway/run.py` 中，新会话键分配后、下一条入站消息处理前立即触发。在网关上，顺序为：`on_session_finalize(old_id)` → 交换 → `on_session_reset(new_id)` → 在第一个入站轮次中触发 `on_session_start(new_id)`。
**返回值：** 忽略。

**使用场景：** 重置以 `session_id` 为键的每会话缓存、发出“会话轮换”分析事件、为新的状态桶做准备。

---

有关工具模式、处理程序和高级钩子模式的完整演练，请参阅 **[构建插件指南](/guides/build-a-hermes-plugin)**。

---

<a id="subagentstop"></a>
### `subagent_stop` {#subagent_stop}

在 `delegate_task` 完成后，**每个子 Agent 触发一次**。无论你是委托单个任务还是三个任务批次，此钩子都会为每个子 Agent 触发一次，并在父线程上串行执行。

**回调签名：**

```python
def my_callback(parent_session_id: str, child_role: str | None,
                child_summary: str | None, child_status: str,
                duration_ms: int, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `parent_session_id` | `str` | 委托父 Agent 的会话 ID |
| `child_role` | `str \| None` | 在子 Agent 上设置的角色标签（如果未启用该功能则为 `None`） |
| `child_summary` | `str \| None` | 子 Agent 返回给父 Agent 的最终响应 |
| `child_status` | `str` | `"completed"`、`"failed"`、`"interrupted"` 或 `"error"` |
| `duration_ms` | `int` | 运行子 Agent 所花费的挂钟时间（毫秒） |

**触发时机：** 在 `tools/delegate_tool.py` 中，当 `ThreadPoolExecutor.as_completed()` 耗尽所有子 future 后触发。触发过程被编排到父线程，因此钩子作者无需考虑并发回调执行的问题。

**返回值：** 忽略。
**使用场景：** 记录编排活动、累计子任务耗时用于计费、编写委派后审计记录。

**示例 — 记录编排器活动：**

```python
import logging
logger = logging.getLogger(__name__)

def log_subagent(parent_session_id, child_role, child_status, duration_ms, **kwargs):
    logger.info(
        "SUBAGENT parent=%s role=%s status=%s duration_ms=%d",
        parent_session_id, child_role, child_status, duration_ms,
    )

def register(ctx):
    ctx.register_hook("subagent_stop", log_subagent)
```

:::info
在大量委派场景下（例如编排器角色 × 5 个叶子节点 × 嵌套深度），`subagent_stop` 会在每一轮中触发多次。请确保回调函数执行迅速；将耗时操作推入后台队列处理。
:::

---

<a id="pregatewaydispatch"></a>
### `pre_gateway_dispatch` {#pre_gateway_dispatch}

在网关中**针对每个传入的 `MessageEvent`** 触发一次，时机在内部事件守卫之后、**认证/配对和 Agent 分发之前**。这是网关层消息流策略（如仅监听窗口、人工交接、按对话路由等）的拦截点，这些策略无法干净地融入任何单一平台适配器。

**回调签名：**

```python
def my_callback(event, gateway, session_store, **kwargs):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `event` | `MessageEvent` | 标准化后的入站消息（包含 `.text`、`.source`、`.message_id`、`.internal` 等属性）。 |
| `gateway` | `GatewayRunner` | 当前活动的网关运行器，插件可通过 `gateway.adapters[platform].send(...)` 发送侧信道回复（如所有者通知等）。 |
| `session_store` | `SessionStore` | 用于通过 `session_store.append_to_transcript(...)` 静默记录对话内容。 |
**触发时机：** 在 `gateway/run.py` 的 `GatewayRunner._handle_message()` 中，计算完 `is_internal` 后立即触发。**内部事件完全跳过该钩子**（它们是系统生成的——后台进程完成等——不能被面向用户的策略门控）。

**返回值：** `None` 或一个字典。第一个被识别出的动作字典生效；其余插件的结果被忽略。插件回调中的异常会被捕获并记录；出现错误时，gateway 始终回退到正常分发。

| 返回值 | 效果 |
|--------|------|
| `{"action": "skip", "reason": "..."}` | 丢弃该消息——没有 Agent 回复、没有配对流程、没有认证。假定插件已处理该消息（例如静默摄入到对话记录中）。 |
| `{"action": "rewrite", "text": "new text"}` | 替换 `event.text`，然后继续使用修改后的事件进行正常分发。适用于将缓冲的环境消息合并到单个提示中。 |
| `{"action": "allow"}` / `None` | 正常分发——执行完整的认证/配对/Agent 循环链。 |

**使用场景：** 仅监听的群聊（仅在被@时回复；将环境消息缓冲到上下文中）；人工移交（静默摄入客户消息，同时所有者手动处理聊天）；基于配置文件的速率限制；策略驱动的路由。

**示例——静默丢弃未经授权的私信而不触发配对代码：**

```python
def deny_unauthorized_dms(event, **kwargs):
    src = event.source
    if src.chat_type == "dm" and not _is_approved_user(src.user_id):
        return {"action": "skip", "reason": "unauthorized-dm"}
    return None

def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", deny_unauthorized_dms)
```
**示例 —— 将 ambient 消息缓冲区重写为提到时的一个提示：**

```python
_buffers = {}

def buffer_or_rewrite(event, **kwargs):
    key = (event.source.platform, event.source.chat_id)
    buf = _buffers.setdefault(key, [])
    if _bot_mentioned(event.text):
        combined = "\n".join(buf + [event.text])
        buf.clear()
        return {"action": "rewrite", "text": combined}
    buf.append(event.text)
    return {"action": "skip", "reason": "ambient-buffered"}

def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", buffer_or_rewrite)
```

---

<a id="preapprovalrequest"></a>
### `pre_approval_request` {#pre_approval_request}

在向用户显示审批请求**之前立即触发** —— 涵盖所有表面：交互式 CLI、Ink TUI、网关平台（Telegram、Discord、Slack、WhatsApp、Matrix 等）以及 ACP 客户端（VS Code、Zed、JetBrains）。

这是接入自定义通知器的合适位置——例如，一个 macOS 菜单栏应用，弹出允许/拒绝通知；或者一个审计日志，记录每个带上下文的审批请求。

**回调签名：**

```python
def my_callback(
    command: str,
    description: str,
    pattern_key: str,
    pattern_keys: list[str],
    session_key: str,
    surface: str,
    **kwargs,
):
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `command` | `str` | 等待审批的 shell 命令 |
| `description` | `str` | 可读的命令被标记的原因（多个模式匹配时会合并） |
| `pattern_key` | `str` | 触发审批的主模式键（例如 `"rm_rf"`、`"sudo"`） |
| `pattern_keys` | `list[str]` | 所有匹配的模式键 |
| `session_key` | `str` | 会话标识符，用于按聊天范围限制通知 |
| `surface` | `str` | `"cli"` 表示交互式 CLI/TUI 提示，`"gateway"` 表示异步平台审批 |
**返回值：** 忽略。此处的钩子仅用于观察；它们不能否决或预先回答审批。请使用 [`pre_tool_call`](#pre_tool_call) 在工具到达审批系统之前阻止它。

**使用场景：** 桌面通知、推送提醒、审计日志、Slack Webhook、升级路由、指标。

**示例——macOS 上的桌面通知：**

```python
import subprocess

def notify_approval(command, description, session_key, **kwargs):
    title = "Hermes 需要审批"
    body = f"{description}: {command[:80]}"
    subprocess.Popen([
        "osascript", "-e",
        f'display notification "{body}" with title "{title}"',
    ])

def register(ctx):
    ctx.register_hook("pre_approval_request", notify_approval)
```

---

<a id="postapprovalresponse"></a>
### `post_approval_response` {#post_approval_response}

在**用户响应审批提示（或提示超时）之后**触发。

**回调签名：**

```python
def my_callback(
    command: str,
    description: str,
    pattern_key: str,
    pattern_keys: list[str],
    session_key: str,
    surface: str,
    choice: str,
    **kwargs,
):
```

与 `pre_approval_request` 相同的 kwargs，外加：

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `choice` | `str` | 取值之一：`"once"`、`"session"`、`"always"`、`"deny"` 或 `"timeout"` |

**返回值：** 忽略。

**使用场景：** 关闭匹配的桌面通知、在审计日志中记录最终决定、更新指标、推进速率限制器。

```python
def log_decision(command, choice, session_key, **kwargs):
    logger.info("审批 %s: %s 用于会话 %s", choice, command[:60], session_key)

def register(ctx):
    ctx.register_hook("post_approval_response", log_decision)
```
---

<a id="transformtoolresult"></a>
### `transform_tool_result` {#transform_tool_result}

在工具返回结果之后、结果被追加到对话之前触发。允许插件重写任意工具的结果字符串——不仅仅是终端输出——在模型看到结果之前。

**回调签名：**

```python
def my_callback(
    tool_name: str,
    arguments: dict,
    result: str,
    task_id: str | None,
    **kwargs,
) -> str | None:
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `tool_name` | `str` | 产生结果的工具（`read_file`、`web_extract`、`delegate_task` 等）。 |
| `arguments` | `dict` | 模型调用该工具时使用的参数。 |
| `result` | `str` | 工具的原始结果字符串，已截断并去除 ANSI 转义码。 |
| `task_id` | `str \| None` | 在 RL/基准测试环境中运行时的任务/会话 ID。 |

**返回值：** 返回 `str` 以替换结果（模型看到的就是返回的字符串），返回 `None` 则保持原样。

**使用场景：** 从 `web_extract` 输出中删除组织特定的 PII，将长 JSON 工具响应包装在摘要标题中，向 `read_file` 结果注入检索增强提示，将 `delegate_task` 子 Agent 报告重写为项目特定的格式。

```python
import re
SECRET = re.compile(r"sk-[A-Za-z0-9]{32,}")

def redact_secrets(tool_name, result, **kwargs):
    if SECRET.search(result):
        return SECRET.sub("[REDACTED]", result)
    return None

def register(ctx):
    ctx.register_hook("transform_tool_result", redact_secrets)
```
适用于所有工具。若仅需终端重写，请参见下方的 `transform_terminal_output`——它的作用范围更窄，且在流水线中更早执行（在截断和脱敏之前）。

---

<a id="transformterminaloutput"></a>
### `transform_terminal_output` {#transform_terminal_output}

在 `terminal` 工具的前台输出流水线中触发，**早于**默认的 50 KB 截断、ANSI 转义符剥离和机密信息脱敏。让插件能在任何下游处理接触原始输出之前，重写 shell 命令的原始 stdout/stderr。

**回调签名：**

```python
def my_callback(
    command: str,
    output: str,
    exit_code: int,
    cwd: str,
    task_id: str | None,
    **kwargs,
) -> str | None:
```

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `command` | `str` | 产生输出的 shell 命令。 |
| `output` | `str` | 合并后的原始 stdout/stderr（可能非常大——截断在钩子之后执行）。 |
| `exit_code` | `int` | 进程退出码。 |
| `cwd` | `str` | 命令运行的工作目录。 |

**返回值：** 返回 `str` 替换输出，返回 `None` 保持原样。

**使用场景：** 为产生大量输出的命令（`du -ah`、`find`、`tree`）注入摘要，用项目特定标记标记输出以便下游钩子知道如何处理，去除运行间波动并破坏提示缓存的计时噪声。

```python
def summarize_find(command, output, **kwargs):
    if command.startswith("find ") and len(output) > 50_000:
        lines = output.count("\n")
        head = "\n".join(output.splitlines()[:40])
        return f"{head}\n\n[summary: {lines} paths total, showing first 40]"
    return None

def register(ctx):
    ctx.register_hook("transform_terminal_output", summarize_find)
```
与 `transform_tool_result`（涵盖所有其他工具）配合良好。

---

## Shell 钩子 {#shell-hooks}

在 `cli-config.yaml` 中声明 shell 脚本钩子，当相应的插件钩子事件触发时，Hermes 会以子进程方式运行它们——无论是在 CLI 还是网关会话中。无需编写 Python 插件。

当你想要一个即插即用的单文件脚本（Bash、Python，以及任何带有 shebang 的语言）来实现以下功能时，请使用 shell 钩子：

- **拦截工具调用** —— 拒绝危险的 `terminal` 命令，强制执行按目录划分的策略，要求对破坏性的 `write_file` / `patch` 操作进行审批。
- **在工具调用后运行** —— 自动格式化 Agent 刚刚编写的 Python 或 TypeScript 文件，记录 API 调用，触发 CI 工作流。
- **向下一轮 LLM 注入上下文** —— 将 `git status` 输出、当前工作日或检索到的文档前置到用户消息中（参见 [`pre_llm_call`](#pre_llm_call)）。
- **观察生命周期事件** —— 当子 Agent 完成（`subagent_stop`）或会话启动（`on_session_start`）时写入日志行。

Shell 钩子通过在 CLI 启动时（`hermes_cli/main.py`）和网关启动时（`gateway/run.py`）调用 `agent.shell_hooks.register_from_config(cfg)` 来注册。它们与 Python 插件钩子自然组合——两者都通过同一个分发器流转。

### 快速对比 {#comparison-at-a-glance}

| 维度 | Shell 钩子 | [插件钩子](#plugin-hooks) | [网关钩子](#gateway-event-hooks) |
|-----------|-------------|-------------------------------|---------------------------------------|
| 声明位置 | `hooks:` 块（位于 `~/.hermes/config.yaml`） | `register()` 方法（位于 `plugin.yaml` 插件中） | `HOOK.yaml` + `handler.py` 目录 |
| 存放位置 | `~/.hermes/agent-hooks/`（约定俗成） | `~/.hermes/plugins/&lt;name&gt;/` | `~/.hermes/hooks/&lt;name&gt;/` |
| 语言 | 任意（Bash、Python、Go 二进制等） | 仅 Python | 仅 Python |
| 运行环境 | CLI + 网关 | CLI + 网关 | 仅网关 |
| 事件 | `VALID_HOOKS`（包括 `subagent_stop`） | `VALID_HOOKS` | 网关生命周期（`gateway:startup`、`agent:*`、`command:*`） |
| 能否拦截工具调用 | 是（`pre_tool_call`） | 是（`pre_tool_call`） | 否 |
| 能否注入 LLM 上下文 | 是（`pre_llm_call`） | 是（`pre_llm_call`） | 否 |
| 许可机制 | 按 `(事件, 命令)` 对首次使用提示 | 隐式（信任 Python 插件） | 隐式（信任目录） |
| 进程间隔离 | 是（子进程） | 否（进程内） | 否（进程内） |
### 配置模式 {#configuration-schema}

```yaml
hooks:
  <事件名称>:                    # 必须是 VALID_HOOKS 中的值
    - matcher: "<正则表达式>"     # 可选；仅用于 pre/post_tool_call
      command: "<shell 命令>"    # 必填；通过 shlex.split 执行，shell=False
      timeout: <秒数>            # 可选；默认 60，上限 300

hooks_auto_accept: false         # 参见下方的"同意模型"
```

事件名称必须是[插件钩子事件](#plugin-hooks)之一；拼写错误会显示"您是不是想用 X？"的警告并跳过。单个条目中的未知键会被忽略；缺少 `command` 会跳过并显示警告。`timeout > 300` 会被限制并显示警告。

### JSON 通信协议 {#json-wire-protocol}

每次事件触发时，Hermes 会为每个匹配的钩子（允许使用 matcher）生成一个子进程，通过 **stdin** 传入 JSON 数据，并从 **stdout** 读取 JSON 格式的响应。

**stdin — 脚本接收的数据：**

```json
{
  "hook_event_name": "pre_tool_call",
  "tool_name":       "terminal",
  "tool_input":      {"command": "rm -rf /"},
  "session_id":      "sess_abc123",
  "cwd":             "/home/user/project",
  "extra":           {"task_id": "...", "tool_call_id": "..."}
}
```

对于非工具事件（`pre_llm_call`、`subagent_stop`、会话生命周期），`tool_name` 和 `tool_input` 为 `null`。`extra` 字典包含所有事件特定的关键字参数（`user_message`、`conversation_history`、`child_role`、`duration_ms` 等）。无法序列化的值会被转为字符串而非省略。

**stdout — 可选响应：**
```jsonc
// Block a pre_tool_call (both shapes accepted; normalised internally):
{"decision": "block", "reason":  "Forbidden: rm -rf"}   // Claude-Code style
{"action":   "block", "message": "Forbidden: rm -rf"}   // Hermes-canonical

// Inject context for pre_llm_call:
{"context": "Today is Friday, 2026-04-17"}

// Silent no-op — any empty / non-matching output is fine:
```

格式错误的 JSON、非零退出码和超时会记录警告，但绝不会中止 agent loop。

### 实际示例 {#worked-examples}

#### 1. 每次写入后自动格式化 Python 文件 {#1-auto-format-python-files-after-every-write}

```yaml
# ~/.hermes/config.yaml
hooks:
  post_tool_call:
    - matcher: "write_file|patch"
      command: "~/.hermes/agent-hooks/auto-format.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/auto-format.sh
payload="$(cat -)"
path=$(echo "$payload" | jq -r '.tool_input.path // empty')
[[ "$path" == *.py ]] && command -v black >/dev/null && black "$path" 2>/dev/null
printf '{}\n'
```

Agent 在上下文中的文件视图**不会**自动重新读取——重新格式化仅影响磁盘上的文件。后续的 `read_file` 调用会获取格式化后的版本。

#### 2. 阻止破坏性的 `terminal` 命令 {#2-block-destructive-terminal-commands}

```yaml
hooks:
  pre_tool_call:
    - matcher: "terminal"
      command: "~/.hermes/agent-hooks/block-rm-rf.sh"
      timeout: 5
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/block-rm-rf.sh
payload="$(cat -)"
cmd=$(echo "$payload" | jq -r '.tool_input.command // empty')
if echo "$cmd" | grep -qE 'rm[[:space:]]+-rf?[[:space:]]+/'; then
  printf '{"decision": "block", "reason": "blocked: rm -rf / is not permitted"}\n'
else
  printf '{}\n'
fi
```
#### 3. 在每次交互中注入 `git status`（相当于 Claude-Code 的 `UserPromptSubmit`） {#3-inject-git-status-into-every-turn-claude-code-userpromptsubmit-equivalent}

```yaml
hooks:
  pre_llm_call:
    - command: "~/.hermes/agent-hooks/inject-cwd-context.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/inject-cwd-context.sh
cat - >/dev/null   # 丢弃标准输入的有效载荷
if status=$(git status --porcelain 2>/dev/null) && [[ -n "$status" ]]; then
  jq --null-input --arg s "$status" \
     '{context: ("Uncommitted changes in cwd:\n" + $s)}'
else
  printf '{}\n'
fi
```

Claude Code 的 `UserPromptSubmit` 事件并非 Hermes 的独立事件——`pre_llm_call` 在相同位置触发，并且已经支持上下文注入。这里直接使用它即可。

#### 4. 记录每个子 Agent 的完成情况 {#4-log-every-subagent-completion}

```yaml
hooks:
  subagent_stop:
    - command: "~/.hermes/agent-hooks/log-orchestration.sh"
```

```bash
#!/usr/bin/env bash
# ~/.hermes/agent-hooks/log-orchestration.sh
log=~/.hermes/logs/orchestration.log
jq -c '{ts: now, parent: .session_id, extra: .extra}' < /dev/stdin >> "$log"
printf '{}\n'
```

### 同意模型 {#consent-model}

每个唯一的 `(event, command)` 组合在 Hermes 首次遇到时会提示用户批准，然后将决定持久化到 `~/.hermes/shell-hooks-allowlist.json`。后续运行（CLI 或 gateway）会跳过提示。

以下三种方式可以绕过交互式提示——满足任意一种即可：

1. CLI 中的 `--accept-hooks` 标志（例如 `hermes --accept-hooks chat`）
2. `HERMES_ACCEPT_HOOKS=1` 环境变量
3. `cli-config.yaml` 中的 `hooks_auto_accept: true`
非 TTY 运行（gateway、cron、CI）需要这三种方式之一——否则任何新添加的 hook 会静默地保持未注册状态并记录一条警告。

**脚本编辑会被静默信任。** 允许列表的键基于确切的命令字符串，而非脚本的哈希值，因此在磁盘上编辑脚本不会使授权失效。`hermes hooks doctor` 会标记 mtime 漂移，以便你发现编辑并决定是否重新批准。

### `hermes hooks` CLI {#the-hermes-hooks-cli}

| 命令 | 作用 |
|---------|--------------|
| `hermes hooks list` | 导出已配置的 hook，包含匹配器、超时和授权状态 |
| `hermes hooks test &lt;event&gt; [--for-tool X] [--payload-file F]` | 针对一个合成负载触发所有匹配的 hook，并打印解析后的响应 |
| `hermes hooks revoke &lt;command&gt;` | 移除所有匹配 `&lt;command&gt;` 的允许列表条目（下次重启生效） |
| `hermes hooks doctor` | 对每个已配置的 hook：检查可执行位、允许列表状态、mtime 漂移、JSON 输出有效性以及大致执行时间 |

### 安全性 {#security}

Shell hook 会以**你的完整用户凭据**运行——与 cron 条目或 shell 别名具有相同的信任边界。将 `config.yaml` 中的 `hooks:` 块视为特权配置：

- 只引用你编写或完全审查过的脚本。
- 将脚本放在 `~/.hermes/agent-hooks/` 内，以便路径易于审计。
- 在拉取共享配置后重新运行 `hermes hooks doctor`，以便在新 hook 注册前发现它们。
- 如果你的 config.yaml 在团队中进行版本控制，请像审查 CI 配置一样审查修改 `hooks:` 部分的 PR。
### 排序与优先级 {#ordering-and-precedence}

Python 插件钩子和 Shell 钩子都通过同一个 `invoke_hook()` 分发器执行。Python 插件会先注册（通过 `discover_and_load()`），Shell 钩子后注册（通过 `register_from_config()`），因此在平局情况下，Python 的 `pre_tool_call` 块决策具有更高优先级。第一个有效的拦截块胜出——只要任意回调返回了包含非空消息的 `{"action": "block", "message": str}`，聚合器就会立即返回结果。
