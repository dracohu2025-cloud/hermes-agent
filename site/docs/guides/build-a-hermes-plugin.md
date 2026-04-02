---
sidebar_position: 8
sidebar_label: "构建插件"
title: "构建 Hermes 插件"
description: "逐步指导如何构建一个完整的 Hermes 插件，包含工具、钩子、数据文件和技能"
---

# 构建 Hermes 插件

本指南将带你从零开始构建一个完整的 Hermes 插件。完成后，你将拥有一个包含多个工具、生命周期钩子、内置数据文件和打包技能的可用插件——涵盖插件系统支持的所有内容。

## 你将构建的内容

一个带有两个工具的**计算器**插件：
- `calculate` — 计算数学表达式（如 `2**16`、`sqrt(144)`、`pi * 5**2`）
- `unit_convert` — 单位转换（如 `100 F → 37.78 C`、`5 km → 3.11 mi`）

此外，还有一个记录每次工具调用的钩子，以及一个打包的技能文件。

## 第 1 步：创建插件目录

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

## 第 2 步：编写清单文件

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

这告诉 Hermes：“我是一个名为 calculator 的插件，我提供工具和钩子。” `provides_tools` 和 `provides_hooks` 字段列出了插件注册的内容。

你还可以添加的可选字段：
```yaml
author: Your Name
requires_env:          # 根据环境变量决定是否加载
  - SOME_API_KEY       # 如果缺失则禁用插件
```

## 第 3 步：编写工具的 schema

创建 `schemas.py` — 这是 LLM 用来判断何时调用你的工具的描述：

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

**为什么 schema 很重要：** `description` 字段决定了 LLM 何时使用你的工具。要具体说明工具的功能和使用场景。`parameters` 定义了 LLM 传递的参数。

## 第 4 步：编写工具处理函数

创建 `tools.py` — 这里是 LLM 调用工具时实际执行的代码：

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

**处理函数的关键规则：**
1. **函数签名：** `def my_handler(args: dict, **kwargs) -> str`
2. **返回值：** 始终返回 JSON 字符串，成功和错误都一样。
3. **绝不抛异常：** 捕获所有异常，返回错误 JSON。
4. **接受 `**kwargs`：** Hermes 未来可能传入额外上下文。

## 第 5 步：编写注册代码

创建 `__init__.py` — 这里将 schema 和处理函数连接起来：

```python
"""Calculator plugin — registration."""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# Track tool usage via hooks
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """Hook: runs after every tool call (not just ours)."""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("Tool called: %s (session %s)", tool_name, task_id)


def register(ctx):
    """Wire schemas to handlers and register hooks."""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # This hook fires for ALL tool calls, not just ours
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的作用：**
- 启动时调用一次
- `ctx.register_tool()` 把你的工具放进注册表，模型立刻能看到
- `ctx.register_hook()` 订阅生命周期事件
- `ctx.register_command()` — _计划中，尚未实现_
- 如果此函数崩溃，插件会被禁用，但 Hermes 仍能正常运行
## 第6步：测试插件

启动 Hermes：

```bash
hermes
```

你应该能在横幅的工具列表中看到 `calculator: calculate, unit_convert`。

试试这些提示：
```
What's 2 to the power of 16?
Convert 100 fahrenheit to celsius
What's the square root of 2 times pi?
How many gigabytes is 1.5 terabytes?
```

检查插件状态：
```
/plugins
```

输出：
```
Plugins (1):
  ✓ calculator v1.0.0 (2 tools, 1 hooks)
```

## 你的插件最终结构

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # "我是 calculator，提供工具和 hooks"
├── __init__.py      # 连接：schemas → handlers，注册 hooks
├── schemas.py       # LLM 读取内容（描述 + 参数规范）
└── tools.py         # 运行逻辑（calculate、unit_convert 函数）
```

四个文件，职责清晰：
- **Manifest** 声明插件是什么
- **Schemas** 描述给 LLM 的工具
- **Handlers** 实现具体逻辑
- **Registration** 连接所有部分

## 插件还能做什么？

### 携带数据文件

把任何文件放到插件目录，导入时读取：

```python
# 在 tools.py 或 __init__.py 中
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

### 打包一个技能

包含一个 `skill.md` 文件，并在注册时安装：

```python
import shutil
from pathlib import Path

def _install_skill():
    """首次加载时复制技能到 ~/.hermes/skills/。"""
    try:
        from hermes_cli.config import get_hermes_home
        dest = get_hermes_home() / "skills" / "my-plugin" / "SKILL.md"
    except Exception:
        dest = Path.home() / ".hermes" / "skills" / "my-plugin" / "SKILL.md"

    if dest.exists():
        return  # 不覆盖用户修改

    source = Path(__file__).parent / "skill.md"
    if source.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

def register(ctx):
    ctx.register_tool(...)
    _install_skill()
```

### 根据环境变量控制

如果插件需要 API key：

```yaml
# plugin.yaml
requires_env:
  - WEATHER_API_KEY
```

如果没设置 `WEATHER_API_KEY`，插件会被禁用并显示清晰提示。不会崩溃，也不会在 Agent 里报错——只会显示“Plugin weather disabled (missing: WEATHER_API_KEY)”。

### 条件性工具可用性

对于依赖可选库的工具：

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # False = 工具对模型隐藏
)
```

### 注册多个 hooks

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

可用的 hooks：

| Hook | 触发时机 | 参数 | 返回值 |
|------|----------|------|--------|
| `pre_tool_call` | 任何工具运行前 | `tool_name`, `args`, `task_id` | — |
| `post_tool_call` | 任何工具返回后 | `tool_name`, `args`, `result`, `task_id` | — |
| `pre_llm_call` | 每轮一次，LLM 循环前 | `session_id`, `user_message`, `conversation_history`, `is_first_turn`, `model`, `platform` | `{"context": "..."}` |
| `post_llm_call` | 每轮一次，LLM 循环后 | `session_id`, `user_message`, `assistant_response`, `conversation_history`, `model`, `platform` | — |
| `on_session_start` | 新会话创建（仅首轮） | `session_id`, `model`, `platform` | — |
| `on_session_end` | 每次 `run_conversation` 结束时 | `session_id`, `completed`, `interrupted`, `model`, `platform` | — |

大多数 hooks 是“触发即忘”观察者。例外是 `pre_llm_call`：如果回调返回带 `"context"` 键的字典（或纯字符串），该值会被追加到当前轮的临时系统提示中。这样内存插件可以注入回忆上下文，而无需改动核心代码。

如果某个 hook 出错，会被记录并跳过，其他 hooks 和 Agent 会正常继续。

### 通过 pip 发布

想公开分享插件，可以在 Python 包里添加入口点：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# 下次启动 hermes 时自动发现插件
```

## 常见错误

**Handler 没返回 JSON 字符串：**
```python
# 错误 — 返回了 dict
def handler(args, **kwargs):
    return {"result": 42}

# 正确 — 返回 JSON 字符串
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**Handler 函数签名缺少 `**kwargs`：**
```python
# 错误 — Hermes 传额外上下文时会崩溃
def handler(args):
    ...

# 正确
def handler(args, **kwargs):
    ...
```

**Handler 抛出异常：**
```python
# 错误 — 异常会传播，工具调用失败
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

**Schema 描述太模糊：**
```python
# 不好 — 模型不知道什么时候用
"description": "Does stuff"

# 好 — 模型明确知道何时如何使用
"description": "Evaluate a mathematical expression. Use for arithmetic, trig, logarithms. Supports: +, -, *, /, **, sqrt, sin, cos, log, pi, e."
```
