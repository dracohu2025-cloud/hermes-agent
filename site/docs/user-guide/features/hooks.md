---
sidebar_position: 6
title: "事件钩子"
description: "在关键生命周期节点运行自定义代码 —— 记录活动、发送警报、触发 Webhook"
---

# 事件钩子

Hermes 有两套钩子系统，可在关键生命周期节点运行自定义代码：

| 系统 | 注册方式 | 运行环境 | 使用场景 |
|--------|---------------|---------|----------|
| **[网关钩子](#网关事件钩子)** | 在 `~/.hermes/hooks/` 目录下创建 `HOOK.yaml` + `handler.py` | 仅网关 | 日志记录、警报、Webhook |
| **[插件钩子](#plugin-hooks)** | 在[插件](/user-guide/features/plugins)中使用 `ctx.register_hook()` | CLI + 网关 | 工具拦截、指标收集、防护规则 |

两套系统都是非阻塞的 —— 任何钩子中的错误都会被捕获并记录，永远不会导致代理崩溃。

## 网关事件钩子

网关钩子在网关（Telegram、Discord、Slack、WhatsApp）运行期间自动触发，不会阻塞主代理处理流程。

### 创建钩子

每个钩子是 `~/.hermes/hooks/` 下的一个目录，包含两个文件：

```text
~/.hermes/hooks/
└── my-hook/
    ├── HOOK.yaml      # 声明要监听哪些事件
    └── handler.py     # Python 处理函数
```

#### HOOK.yaml

```yaml
name: my-hook
description: 将所有代理活动记录到文件
events:
  - agent:start
  - agent:end
  - agent:step
```

`events` 列表决定了哪些事件会触发你的处理函数。你可以订阅任意组合的事件，包括通配符如 `command:*`。

#### handler.py

```python
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".hermes" / "hooks" / "my-hook" / "activity.log"

async def handle(event_type: str, context: dict):
    """为每个订阅的事件调用。必须命名为 'handle'。"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        **context,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**处理函数规则：**
- 必须命名为 `handle`
- 接收 `event_type` (字符串) 和 `context` (字典) 参数
- 可以是 `async def` 或普通 `def` —— 两者都行
- 错误会被捕获并记录，永远不会导致代理崩溃

### 可用事件

| 事件 | 触发时机 | 上下文键 |
|-------|---------------|--------------|
| `gateway:startup` | 网关进程启动时 | `platforms` (活跃平台名称列表) |
| `session:start` | 新消息会话创建时 | `platform`, `user_id`, `session_id`, `session_key` |
| `session:end` | 会话结束时（重置前） | `platform`, `user_id`, `session_key` |
| `session:reset` | 用户执行 `/new` 或 `/reset` 时 | `platform`, `user_id`, `session_key` |
| `agent:start` | 代理开始处理消息时 | `platform`, `user_id`, `session_id`, `message` |
| `agent:step` | 工具调用循环的每次迭代时 | `platform`, `user_id`, `session_id`, `iteration`, `tool_names` |
| `agent:end` | 代理完成处理时 | `platform`, `user_id`, `session_id`, `message`, `response` |
| `command:*` | 任何斜杠命令执行时 | `platform`, `user_id`, `command`, `args` |

#### 通配符匹配

注册了 `command:*` 的处理函数会为任何 `command:` 事件（`command:model`、`command:reset` 等）触发。通过一次订阅即可监控所有斜杠命令。

### 示例

#### 启动检查清单 (BOOT.md) —— 内置功能

网关附带一个内置的 `boot-md` 钩子，它会在每次启动时查找 `~/.hermes/BOOT.md`。如果文件存在，代理会在后台会话中运行其指令。无需安装 —— 只需创建文件。

**创建 `~/.hermes/BOOT.md`：**

```markdown
# 启动检查清单

1. 检查是否有定时任务在夜间失败 —— 运行 `hermes cron list`
2. 向 Discord #general 频道发送消息，内容为“网关已重启，一切正常”
3. 检查 /opt/app/deploy.log 在过去 24 小时内是否有错误
```

代理会在后台线程中运行这些指令，因此不会阻塞网关启动。如果无需关注任何事项，代理会回复 `[SILENT]`，并且不会发送任何消息。

:::tip
没有 BOOT.md？钩子会静默跳过 —— 零开销。需要启动自动化时创建文件，不需要时删除即可。
:::

#### 长任务 Telegram 警报

当代理执行超过 10 步时，给自己发送一条消息：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: 代理执行多步时发出警报
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

#### 命令使用记录器

跟踪哪些斜杠命令被使用：

```yaml
# ~/.hermes/hooks/command-logger/HOOK.yaml
name: command-logger
description: 记录斜杠命令使用情况
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
description: 新会话时通知外部服务
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

1.  网关启动时，`HookRegistry.discover_and_load()` 扫描 `~/.hermes/hooks/`
2.  每个包含 `HOOK.yaml` + `handler.py` 的子目录都会被动态加载
3.  处理函数为其声明的事件进行注册
4.  在每个生命周期节点，`hooks.emit()` 触发所有匹配的处理函数
5.  任何处理函数中的错误都会被捕获并记录 —— 损坏的钩子永远不会导致代理崩溃

:::info
网关钩子仅在**网关**（Telegram、Discord、Slack、WhatsApp）中触发。CLI 不会加载网关钩子。对于需要随处工作的钩子，请使用[插件钩子](#plugin-hooks)。
:::

## 插件钩子 {#plugin-hooks}

[插件](/user-guide/features/plugins)可以注册在 **CLI 和网关**会话中都触发的钩子。这些钩子通过插件 `register()` 函数中的 `ctx.register_hook()` 以编程方式注册。

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", my_callback)
    ctx.register_hook("post_tool_call", my_callback)
```

### 可用的插件钩子

| 钩子 | 触发时机 | 回调函数接收的参数 |
|------|-----------|-------------------|
| `pre_tool_call` | 任何工具执行前 | `tool_name`, `args`, `task_id` |
| `post_tool_call` | 任何工具返回后 | `tool_name`, `args`, `result`, `task_id` |
| `pre_llm_call` | LLM API 请求前 | `session_id`, `user_message`, `conversation_history`, `is_first_turn`, `model`, `platform` |
| `post_llm_call` | LLM API 响应后 | `session_id`, `user_message`, `assistant_response`, `conversation_history`, `model`, `platform` |
| `on_session_start` | 会话开始时 | `session_id`, `model`, `platform` |
| `on_session_end` | 会话结束时 | `session_id`, `completed`, `interrupted`, `model`, `platform` |

回调函数接收与上表列名匹配的关键字参数：

```python
def my_callback(**kwargs):
    tool = kwargs["tool_name"]
    args = kwargs["args"]
    # ...
```

### 示例：阻止危险工具

```python
# ~/.hermes/plugins/tool-guard/__init__.py
BLOCKED = {"terminal", "write_file"}

def guard(**kwargs):
    if kwargs["tool_name"] in BLOCKED:
        print(f"⚠ Blocked tool call: {kwargs['tool_name']}")

def register(ctx):
    ctx.register_hook("pre_tool_call", guard)
```

有关创建插件的完整细节，请参阅 **[插件指南](/user-guide/features/plugins)**。
