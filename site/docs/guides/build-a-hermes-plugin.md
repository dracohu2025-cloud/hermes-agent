---
sidebar_position: 9
sidebar_label: "Build a Plugin"
title: "Build a Hermes Plugin"
description: "从零开始构建完整 Hermes 插件的分步指南，包含工具、钩子、数据文件和技能"
---

# 构建 Hermes 插件 {#build-a-hermes-plugin}

本指南带你从零开始构建一个完整的 Hermes 插件。完成后，你将拥有一个包含多个工具、生命周期钩子、附带数据文件和打包技能的可用插件——涵盖插件系统支持的所有功能。

## 你要构建什么 {#what-you-re-building}

一个**计算器**插件，包含两个工具：
- `calculate` — 计算数学表达式（`2**16`、`sqrt(144)`、`pi * 5**2`）
- `unit_convert` — 单位换算（`100 F → 37.78 C`、`5 km → 3.11 mi`）

外加一个记录每次工具调用的钩子，以及一个打包的技能文件。

## 第 1 步：创建插件目录 {#step-1-create-the-plugin-directory}

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

## 第 2 步：编写清单文件 {#step-2-write-the-manifest}

创建 `plugin.yaml`：

```yaml
name: calculator
version: 1.0.0
description: Math calculator — evaluate expressions and convert units
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

这告诉 Hermes："我是一个叫 calculator 的插件，我提供工具和钩子。"`provides_tools` 和 `provides_hooks` 字段是插件注册内容的列表。

可选字段，你可以按需添加：
```yaml
author: Your Name
requires_env:          # 根据环境变量控制加载；安装时提示
  - SOME_API_KEY       # 简单格式 — 缺失则禁用插件
  - name: OTHER_KEY    # 丰富格式 — 安装时显示描述/链接
    description: "Key for the Other service"
    url: "https://other.com/keys"
    secret: true
```

## 第 3 步：编写工具 schema {#step-3-write-the-tool-schemas}

创建 `schemas.py` —— 这是 LLM 读取的内容，用于决定何时调用你的工具：

```python
"""Tool schemas — what the LLM sees."""

CALCULATE = {
    "name": "calculate",
    "description": (
        "Evaluate a mathematical expression and return the result. "
        "Supports arithmetic (+, -, *, /, **), functions (sqrt, sin, cos, "
        "log, abs, round, floor, ceil), and constants (pi, e). "
        "Use this for any math the user asks about."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate (e.g., '2**10', 'sqrt(144)')",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "Convert a value between units. Supports length (m, km, mi, ft, in), "
        "weight (kg, lb, oz, g), temperature (C, F, K), data (B, KB, MB, GB, TB), "
        "and time (s, min, hr, day)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "The numeric value to convert",
            },
            "from_unit": {
                "type": "string",
                "description": "Source unit (e.g., 'km', 'lb', 'F', 'GB')",
            },
            "to_unit": {
                "type": "string",
                "description": "Target unit (e.g., 'mi', 'kg', 'C', 'MB')",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**Schema 为什么重要：** `description` 字段是 LLM 决定何时使用你工具的依据。要具体说明工具做什么、什么时候用。`parameters` 定义 LLM 传递的参数。

## 第 4 步：编写工具处理函数 {#step-4-write-the-tool-handlers}

创建 `tools.py` —— 这是 LLM 调用工具时实际执行的代码：

```python
"""Tool handlers — the code that runs when the LLM calls each tool."""

import json
import math

# Safe globals for expression evaluation — no file/network access
_SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "log": math.log, "log2": math.log2, "log10": math.log10,
    "floor": math.floor, "ceil": math.ceil,
    "pi": math.pi, "e": math.e,
    "factorial": math.factorial,
}


def calculate(args: dict, **kwargs) -> str:
    """Evaluate a math expression safely.

    Rules for handlers:
    1. Receive args (dict) — the parameters the LLM passed
    2. Do the work
    3. Return a JSON string — ALWAYS, even on error
    4. Accept **kwargs for forward compatibility
    """
    expression = args.get("expression", "").strip()
    if not expression:
        return json.dumps({"error": "No expression provided"})

    try:
        result = eval(expression, {"__builtins__": {}}, _SAFE_MATH)
        return json.dumps({"expression": expression, "result": result})
    except ZeroDivisionError:
        return json.dumps({"expression": expression, "error": "Division by zero"})
    except Exception as e:
        return json.dumps({"expression": expression, "error": f"Invalid: {e}"})


# Conversion tables — values are in base units
_LENGTH = {"m": 1, "km": 1000, "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "cm": 0.01}
_WEIGHT = {"kg": 1, "g": 0.001, "lb": 0.453592, "oz": 0.0283495}
_DATA = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_TIME = {"s": 1, "ms": 0.001, "min": 60, "hr": 3600, "day": 86400}


def _convert_temp(value, from_u, to_u):
    # Normalize to Celsius
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # Convert to target
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """Convert between units."""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "Need value, from_unit, and to_unit"})

    try:
        # Temperature
        if from_unit.upper() in {"C","F","K"} and to_unit.upper() in {"C","F","K"}:
            result = _convert_temp(float(value), from_unit.upper(), to_unit.upper())
            return json.dumps({"input": f"{value} {from_unit}", "result": round(result, 4),
                             "output": f"{round(result, 4)} {to_unit}"})

        # Ratio-based conversions
        for table in (_LENGTH, _WEIGHT, _DATA, _TIME):
            lc = {k.lower(): v for k, v in table.items()}
            if from_unit.lower() in lc and to_unit.lower() in lc:
                result = float(value) * lc[from_unit.lower()] / lc[to_unit.lower()]
                return json.dumps({"input": f"{value} {from_unit}",
                                 "result": round(result, 6),
                                 "output": f"{round(result, 6)} {to_unit}"})

        return json.dumps({"error": f"Cannot convert {from_unit} → {to_unit}"})
    except Exception as e:
        return json.dumps({"error": f"Conversion failed: {e}"})
```
**Handler 的关键规则：**
1. **签名：** `def my_handler(args: dict, **kwargs) -> str`
2. **返回值：** 始终返回 JSON 字符串，成功和失败都一样。
3. **绝不抛出异常：** 捕获所有异常，改为返回错误 JSON。
4. **接受 `**kwargs`：** Hermes 未来可能会传入额外的上下文。

## 第 5 步：编写注册代码 {#step-5-write-the-registration}

创建 `__init__.py` —— 这里把 schema 和 handler 连接起来：

```python
"""Calculator plugin — registration."""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# 通过 hooks 追踪工具调用
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """Hook：每次工具调用后都会运行（不只是我们的工具）。"""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("Tool called: %s (session %s)", tool_name, task_id)


def register(ctx):
    """将 schema 和 handler 关联起来，并注册 hooks。"""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # 这个 hook 会对所有工具调用触发，不只是我们的
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的作用：**
- 在启动时只调用一次
- `ctx.register_tool()` 把你的工具放进注册表 —— 模型立刻就能看到它
- `ctx.register_hook()` 订阅生命周期事件
- `ctx.register_cli_command()` 注册 CLI 子命令（例如 `hermes my-plugin &lt;subcommand&gt;`）
- 如果这个函数崩溃了，插件会被禁用，但 Hermes 本身继续正常运行

## 第 6 步：测试 {#step-6-test-it}

启动 Hermes：

```bash
hermes
```

你应该能在 banner 的工具列表里看到 `calculator: calculate, unit_convert`。

试试这些提示：
```
What's 2 to the power of 16?
Convert 100 fahrenheit to celsius
What's the square root of 2 times pi?
How many gigabytes is 1.5 terabytes?
```

查看插件状态：
```
/plugins
```

输出：
```
Plugins (1):
  ✓ calculator v1.0.0 (2 tools, 1 hooks)
```

## 插件的最终结构 {#your-plugin-s-final-structure}

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # "我是 calculator，我提供 tools 和 hooks"
├── __init__.py      # 接线：schemas → handlers，注册 hooks
├── schemas.py       # LLM 读到的内容（描述 + 参数规格）
└── tools.py         # 实际运行的东西（calculate、unit_convert 函数）
```

四个文件，职责分明：
- **Manifest** 声明插件是什么
- **Schemas** 为 LLM 描述工具
- **Handlers** 实现实际逻辑
- **Registration** 把所有东西连接起来

## 插件还能做什么？ {#what-else-can-plugins-do}

### 附带数据文件 {#ship-data-files}

把任何文件放在插件目录里，然后在导入时读取：

```python
# 在 tools.py 或 __init__.py 中
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

### 打包 skills {#bundle-skills}

插件可以附带 skill 文件，Agent 通过 `skill_view("plugin:skill")` 来加载。在你的 `__init__.py` 里注册它们：

```
~/.hermes/plugins/my-plugin/
├── __init__.py
├── plugin.yaml
└── skills/
    ├── my-workflow/
    │   └── SKILL.md
    └── my-checklist/
        └── SKILL.md
```

```python
from pathlib import Path

def register(ctx):
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)
```

现在 Agent 可以用带命名空间的名字加载你的 skills：

```python
skill_view("my-plugin:my-workflow")   # → 插件版本
skill_view("my-workflow")              # → 内置版本（不受影响）
```

**关键特性：**
- 插件 skills 是**只读**的 —— 它们不会进入 `~/.hermes/skills/`，也不能通过 `skill_manage` 编辑。
- 插件 skills **不会**出现在系统提示的 `&lt;available_skills&gt;` 索引里 —— 它们是按需显式加载的。
- 裸 skill 名不受影响 —— 命名空间避免了与内置 skills 的冲突。
- 当 Agent 加载插件 skill 时，会在前面加上一个 bundle context banner，列出同一插件下的其他 skills。
:::tip 旧模式提示
旧的 `shutil.copy2` 模式（把 skill 复制到 `~/.hermes/skills/`）仍然可用，但会与内置 skill 产生命名冲突。新插件请优先使用 `ctx.register_skill()`。
:::

<a id="legacy-pattern"></a>
### 通过环境变量控制启用 {#gate-on-environment-variables}

如果你的插件需要 API key：

```yaml
# plugin.yaml — 简单格式（向后兼容）
requires_env:
  - WEATHER_API_KEY
```

如果 `WEATHER_API_KEY` 未设置，插件会被禁用，并给出明确提示。Agent 不会崩溃，也不会报错——只会显示 "Plugin weather disabled (missing: WEATHER_API_KEY)"。

用户运行 `hermes plugins install` 时，系统会**交互式提示**输入缺失的 `requires_env` 变量，数值会自动保存到 `.env`。

为了获得更好的安装体验，可以使用带描述和注册链接的完整格式：

```yaml
# plugin.yaml — 完整格式
requires_env:
  - name: WEATHER_API_KEY
    description: "API key for OpenWeather"
    url: "https://openweathermap.org/api"
    secret: true
```

| 字段 | 必填 | 说明 |
|-------|----------|-------------|
| `name` | 是 | 环境变量名称 |
| `description` | 否 | 安装提示时展示给用户 |
| `url` | 否 | 获取凭证的地址 |
| `secret` | 否 | 设为 `true` 时输入会被隐藏（类似密码框） |

两种格式可以在同一个列表里混用。已经设置好的变量会自动跳过。

### 条件性工具可用性 {#conditional-tool-availability}

针对依赖可选库的工具：

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # 返回 False 时工具对模型隐藏
)
```

### 注册多个 Hook {#register-multiple-hooks}

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("pre_llm_call", inject_memory)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

### Hook 参考 {#hook-reference}

每个 Hook 的完整文档见 **[Event Hooks 参考](/user-guide/features/hooks#plugin-hooks)** —— 包含回调签名、参数表、触发时机和示例。下面是汇总：

| Hook | 触发时机 | 回调签名 | 返回值 |
|------|-----------|-------------------|---------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 任意工具执行前 | `tool_name: str, args: dict, task_id: str` | 忽略 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 任意工具返回后 | `tool_name: str, args: dict, result: str, task_id: str` | 忽略 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮一次，在工具调用循环开始前 | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [上下文注入](#pre_llm_call-context-injection) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮一次，在工具调用循环结束后（仅成功轮次） | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | 忽略 |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 新会话创建时（仅首轮） | `session_id: str, model: str, platform: str` | 忽略 |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束 + CLI 退出时 | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | 忽略 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/gateway 销毁活跃会话时 | `session_id: str \| None, platform: str` | 忽略 |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | Gateway 切换新会话 key 时（`/new`, `/reset`） | `session_id: str, platform: str` | 忽略 |

大多数 Hook 都是即发即弃的观察者——返回值会被忽略。例外是 `pre_llm_call`，它可以向对话中注入上下文。
所有回调都应接受 `**kwargs`，以便向前兼容。如果某个 hook 回调崩溃了，会被记录并跳过，其他 hook 和 Agent 继续正常运行。

<a id="prellmcall-context-injection"></a>
### `pre_llm_call` 上下文注入 {#pre_llm_call-context-injection}

这是唯一一个返回值有意义的 hook。当 `pre_llm_call` 回调返回一个带有 `"context"` 键的字典（或一个普通字符串）时，Hermes 会将该文本注入到**当前轮次的用户消息**中。这是记忆插件、RAG 集成、护栏（guardrails）以及任何需要向模型提供额外上下文的插件的工作机制。

#### 返回格式 {#return-format}

```python
# 带 context 键的字典
return {"context": "Recalled memories:\n- User prefers dark mode\n- Last project: hermes-agent"}

# 普通字符串（与上面的字典形式等价）
return "Recalled memories:\n- User prefers dark mode"

# 返回 None 或不返回 → 不注入（仅观察）
return None
```

任何非 None、非空的返回值，只要带有 `"context"` 键（或是非空的普通字符串），都会被收集并追加到当前轮次的用户消息中。

#### 注入机制 {#how-injection-works}

注入的上下文会追加到**用户消息**，而不是系统提示（system prompt）。这是一个有意的设计选择：

- **保持提示缓存** — 系统提示在多轮对话中保持不变。Anthropic 和 OpenRouter 会缓存系统提示前缀，因此保持其稳定可在多轮对话中节省 75% 以上的输入 token。如果插件修改了系统提示，每一轮都会变成缓存未命中。
- **临时性** — 注入只在调用 API 时发生。对话历史中的原始用户消息不会被修改，也不会持久化到会话数据库中。
- **系统提示是 Hermes 的领地** — 它包含模型特定的指导、工具强制规则、人格指令和缓存的技能内容。插件在用户输入旁边提供上下文，而不是去修改 Agent 的核心指令。

#### 示例：记忆召回插件 {#example-memory-recall-plugin}

```python
"""Memory plugin — recalls relevant context from a vector store."""

import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall_context(session_id, user_message, is_first_turn, **kwargs):
    """Called before each LLM turn. Returns recalled memories."""
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None  # nothing to inject

        text = "Recalled context from previous sessions:\n"
        text += "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None  # fail silently, don't break the agent

def register(ctx):
    ctx.register_hook("pre_llm_call", recall_context)
```

#### 示例：护栏插件 {#example-guardrails-plugin}

```python
"""Guardrails plugin — enforces content policies."""

POLICY = """You MUST follow these content policies for this session:
- Never generate code that accesses the filesystem outside the working directory
- Always warn before executing destructive operations
- Refuse requests involving personal data extraction"""

def inject_guardrails(**kwargs):
    """Injects policy text into every turn."""
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", inject_guardrails)
```

#### 示例：纯观察 hook（不注入） {#example-observer-only-hook-no-injection}

```python
"""Analytics plugin — tracks turn metadata without injecting context."""

import logging
logger = logging.getLogger(__name__)

def log_turn(session_id, user_message, model, is_first_turn, **kwargs):
    """Fires before each LLM call. Returns None — no context injected."""
    logger.info("Turn: session=%s model=%s first=%s msg_len=%d",
                session_id, model, is_first_turn, len(user_message or ""))
    # No return → no injection

def register(ctx):
    ctx.register_hook("pre_llm_call", log_turn)
```

#### 多个插件返回上下文 {#multiple-plugins-returning-context}
当多个插件从 `pre_llm_call` 返回上下文时，它们的输出会用双换行符连接，并一起追加到用户消息末尾。顺序遵循插件发现顺序（按插件目录名字母顺序）。

### 注册 CLI 命令 {#register-cli-commands}

插件可以添加自己的 `hermes &lt;plugin&gt;` 子命令树：

```python
def _my_command(args):
    """Handler for hermes my-plugin <subcommand>."""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("All good!")
    elif sub == "config":
        print("Current config: ...")
    else:
        print("Usage: hermes my-plugin <status|config>")

def _setup_argparse(subparser):
    """Build the argparse tree for hermes my-plugin."""
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="Show plugin status")
    subs.add_parser("config", help="Show plugin config")
    subparser.set_defaults(func=_my_command)

def register(ctx):
    ctx.register_tool(...)
    ctx.register_cli_command(
        name="my-plugin",
        help="Manage my plugin",
        setup_fn=_setup_argparse,
        handler_fn=_my_command,
    )
```

注册完成后，用户就可以运行 `hermes my-plugin status`、`hermes my-plugin config` 等命令。

**Memory provider 插件**采用基于约定的方式：在插件的 `cli.py` 文件中添加 `register_cli(subparser)` 函数。Memory 插件发现系统会自动找到它——不需要调用 `ctx.register_cli_command()`。详情请参见 [Memory Provider Plugin 指南](/developer-guide/memory-provider-plugin#adding-cli-commands)。

**Active-provider 控制：** Memory 插件的 CLI 命令只在其 provider 是当前配置中的活跃 `memory.provider` 时才会显示。如果用户还没有配置你的 provider，你的 CLI 命令就不会挤占帮助输出。

### 注册 slash 命令 {#register-slash-commands}

插件可以注册会话内的 slash 命令——用户在对话过程中输入的命令（比如 `/lcm status` 或 `/ping`）。这些命令在 CLI 和 gateway（Telegram、Discord 等）中都能使用。

```python
def _handle_status(raw_args: str) -> str:
    """Handler for /mystatus — called with everything after the command name."""
    if raw_args.strip() == "help":
        return "Usage: /mystatus [help|check]"
    return "Plugin status: all systems nominal"

def register(ctx):
    ctx.register_command(
        "mystatus",
        handler=_handle_status,
        description="Show plugin status",
    )
```

注册完成后，用户可以在任何会话中输入 `/mystatus`。该命令会出现在自动补全、`/help` 输出以及 Telegram bot 菜单中。

**签名：** `ctx.register_command(name: str, handler: Callable, description: str = "")`

| 参数 | 类型 | 说明 |
|-----------|------|-------------|
| `name` | `str` | 不带前导斜杠的命令名（例如 `"lcm"`、`"mystatus"`） |
| `handler` | `Callable[[str], str \| None]` | 接收原始参数字符串。也可以是 `async`。 |
| `description` | `str` | 显示在 `/help`、自动补全和 Telegram bot 菜单中 |

**与 `register_cli_command()` 的关键区别：**

| | `register_command()` | `register_cli_command()` |
|---|---|---|
| 调用方式 | 在会话中输入 `/name` | 在终端中输入 `hermes name` |
| 适用范围 | CLI 会话、Telegram、Discord 等 | 仅终端 |
| Handler 接收 | 原始参数字符串 | argparse `Namespace` |
| 适用场景 | 诊断、状态查看、快速操作 | 复杂子命令树、设置向导 |

**冲突保护：** 如果插件尝试注册的名称与内置命令（`help`、`model`、`new` 等）冲突，注册会被静默拒绝并记录警告日志。内置命令始终优先。

**异步 handler：** Gateway 调度会自动检测并等待异步 handler，所以你可以使用同步或异步函数：

```python
async def _handle_check(raw_args: str) -> str:
    result = await some_async_operation()
    return f"Check result: {result}"

def register(ctx):
    ctx.register_command("check", handler=_handle_check, description="Run async check")
```
:::tip
本指南涵盖**通用插件**（工具、钩子、斜杠命令、CLI 命令）。如需了解专用插件类型，请参阅：
- [Memory Provider 插件](/developer-guide/memory-provider-plugin) — 跨会话知识后端
- [Context Engine 插件](/developer-guide/context-engine-plugin) — 替代上下文管理策略
:::

### 通过 pip 分发 {#distribute-via-pip}

如需公开分享插件，请在 Python 包中添加入口点：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# 下次启动 hermes 时自动发现插件
```

## 常见错误 {#common-mistakes}

**Handler 没有返回 JSON 字符串：**
```python
# 错误 — 返回的是 dict
def handler(args, **kwargs):
    return {"result": 42}

# 正确 — 返回 JSON 字符串
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**Handler 签名缺少 `**kwargs`：**
```python
# 错误 — 如果 Hermes 传入额外上下文会报错
def handler(args):
    ...

# 正确
def handler(args, **kwargs):
    ...
```

**Handler 抛出异常：**
```python
# 错误 — 异常向上传播，工具调用失败
def handler(args, **kwargs):
    result = 1 / int(args["value"])  # ZeroDivisionError!
    return json.dumps({"result": result})

# 正确 — 捕获异常并返回错误 JSON
def handler(args, **kwargs):
    try:
        result = 1 / int(args.get("value", 0))
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**Schema 描述过于模糊：**
```python
# 差 — 模型不知道何时使用该工具
"description": "Does stuff"

# 好 — 模型清楚知道何时以及如何使用
"description": "Evaluate a mathematical expression. Use for arithmetic, trig, logarithms. Supports: +, -, *, /, **, sqrt, sin, cos, log, pi, e."
```
