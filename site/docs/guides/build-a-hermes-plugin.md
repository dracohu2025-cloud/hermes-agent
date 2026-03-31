---
sidebar_position: 10
---

# 构建 Hermes 插件

本指南将从头开始构建一个完整的 Hermes 插件。最终你将得到一个包含多个工具、生命周期钩子、附带数据文件和捆绑技能的可用插件——涵盖插件系统支持的所有功能。

## 你将构建什么

一个**计算器**插件，包含两个工具：
- `calculate` — 计算数学表达式 (`2**16`, `sqrt(144)`, `pi * 5**2`)
- `unit_convert` — 单位转换 (`100 F → 37.78 C`, `5 km → 3.11 mi`)

外加一个记录每次工具调用的钩子，以及一个捆绑的技能文件。

## 步骤 1：创建插件目录

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

## 步骤 2：编写清单文件

创建 `plugin.yaml`：

```yaml
name: calculator
version: 1.0.0
description: 数学计算器 — 计算表达式和转换单位
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

这告诉 Hermes：“我是一个名为 calculator 的插件，我提供工具和钩子。” `provides_tools` 和 `provides_hooks` 字段列出了插件注册的内容。

你可以添加的可选字段：
```yaml
author: Your Name
requires_env:          # 根据环境变量控制加载
  - SOME_API_KEY       # 如果缺失则插件被禁用
```

## 步骤 3：编写工具模式

创建 `schemas.py` — 这是 LLM 用来决定何时调用你的工具的内容：

```python
"""工具模式 — LLM 看到的内容。"""

CALCULATE = {
    "name": "calculate",
    "description": (
        "计算数学表达式并返回结果。"
        "支持算术运算 (+, -, *, /, **)、函数 (sqrt, sin, cos, "
        "log, abs, round, floor, ceil) 和常量 (pi, e)。"
        "当用户询问任何数学问题时使用此工具。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式（例如 '2**10', 'sqrt(144)'）",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "在单位之间转换数值。支持长度 (m, km, mi, ft, in)、"
        "重量 (kg, lb, oz, g)、温度 (C, F, K)、数据 (B, KB, MB, GB, TB)、"
        "和时间 (s, min, hr, day)。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "要转换的数值",
            },
            "from_unit": {
                "type": "string",
                "description": "源单位（例如 'km', 'lb', 'F', 'GB'）",
            },
            "to_unit": {
                "type": "string",
                "description": "目标单位（例如 'mi', 'kg', 'C', 'MB'）",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**为什么模式很重要：** `description` 字段是 LLM 决定何时使用你的工具的依据。要具体说明它的功能和适用场景。`parameters` 定义了 LLM 传递的参数。

## 步骤 4：编写工具处理器

创建 `tools.py` — 这是当 LLM 调用你的工具时实际执行的代码：

```python
"""工具处理器 — 当 LLM 调用每个工具时运行的代码。"""

import json
import math

# 用于表达式求值的安全全局变量 — 无文件/网络访问权限
_SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "log": math.log, "log2": math.log2, "log10": math.log10,
    "floor": math.floor, "ceil": math.ceil,
    "pi": math.pi, "e": math.e,
    "factorial": math.factorial,
}


def calculate(args: dict, **kwargs) -> str:
    """安全地计算数学表达式。

    处理器的规则：
    1. 接收 args (dict) — LLM 传递的参数
    2. 执行工作
    3. 返回一个 JSON 字符串 — 总是如此，即使出错
    4. 接受 **kwargs 以保持向前兼容性
    """
    expression = args.get("expression", "").strip()
    if not expression:
        return json.dumps({"error": "未提供表达式"})

    try:
        result = eval(expression, {"__builtins__": {}}, _SAFE_MATH)
        return json.dumps({"expression": expression, "result": result})
    except ZeroDivisionError:
        return json.dumps({"expression": expression, "error": "除以零"})
    except Exception as e:
        return json.dumps({"expression": expression, "error": f"无效: {e}"})


# 转换表 — 值以基本单位表示
_LENGTH = {"m": 1, "km": 1000, "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "cm": 0.01}
_WEIGHT = {"kg": 1, "g": 0.001, "lb": 0.453592, "oz": 0.0283495}
_DATA = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_TIME = {"s": 1, "ms": 0.001, "min": 60, "hr": 3600, "day": 86400}


def _convert_temp(value, from_u, to_u):
    # 标准化为摄氏度
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # 转换为目标单位
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """在单位之间转换。"""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "需要 value、from_unit 和 to_unit"})

    try:
        # 温度
        if from_unit.upper() in {"C","F","K"} and to_unit.upper() in {"C","F","K"}:
            result = _convert_temp(float(value), from_unit.upper(), to_unit.upper())
            return json.dumps({"input": f"{value} {from_unit}", "result": round(result, 4),
                             "output": f"{round(result, 4)} {to_unit}"})

        # 基于比率的转换
        for table in (_LENGTH, _WEIGHT, _DATA, _TIME):
            lc = {k.lower(): v for k, v in table.items()}
            if from_unit.lower() in lc and to_unit.lower() in lc:
                result = float(value) * lc[from_unit.lower()] / lc[to_unit.lower()]
                return json.dumps({"input": f"{value} {from_unit}",
                                 "result": round(result, 6),
                                 "output": f"{round(result, 6)} {to_unit}"})

        return json.dumps({"error": f"无法转换 {from_unit} → {to_unit}"})
    except Exception as e:
        return json.dumps({"error": f"转换失败: {e}"})
```

**处理器的关键规则：**
1. **签名：** `def my_handler(args: dict, **kwargs) -> str`
2. **返回：** 始终是一个 JSON 字符串。成功和错误都一样。
3. **永不抛出异常：** 捕获所有异常，改为返回错误 JSON。
4. **接受 `**kwargs`：** Hermes 未来可能会传递额外的上下文。

## 步骤 5：编写注册代码

创建 `__init__.py` — 这负责将模式连接到处理器：

```python
"""计算器插件 — 注册。"""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# 通过钩子跟踪工具使用情况
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """钩子：在每次工具调用后运行（不仅限于我们的工具）。"""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("工具调用: %s (会话 %s)", tool_name, task_id)


def register(ctx):
    """将模式连接到处理器并注册钩子。"""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # 此钩子会为所有工具调用触发，不仅限于我们的
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的作用：**
- 在启动时仅调用一次
- `ctx.register_tool()` 将你的工具放入注册表 — 模型立即就能看到它
- `ctx.register_hook()` 订阅生命周期事件
- `ctx.register_command()` — _计划中但尚未实现_
- 如果此函数崩溃，插件将被禁用，但 Hermes 会继续正常运行

## 步骤 6：测试它

启动 Hermes：

```bash
hermes
```

你应该在横幅的工具列表中看到 `calculator: calculate, unit_convert`。

尝试以下提示：
```
2 的 16 次方是多少？
将 100 华氏度转换为摄氏度
2 的平方根乘以 pi 是多少？
1.5 太字节是多少吉字节？
```

检查插件状态：
```
/plugins
```

输出：
```
插件 (1):
  ✓ calculator v1.0.0 (2 个工具, 1 个钩子)
```

## 你的插件最终结构

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # “我是 calculator，我提供工具和钩子”
├── __init__.py      # 连接：模式 → 处理器，注册钩子
├── schemas.py       # LLM 读取的内容（描述 + 参数规范）
└── tools.py         # 运行的内容（calculate, unit_convert 函数）
```

四个文件，职责清晰：
- **清单** 声明插件是什么
- **模式** 为 LLM 描述工具
- **处理器** 实现实际逻辑
- **注册** 连接一切

## 插件还能做什么？

### 附带数据文件

将任何文件放入你的插件目录，并在导入时读取它们：

```python
# 在 tools.py 或 __init__.py 中
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

### 捆绑技能

包含一个 `skill.md` 文件，并在注册期间安装它：

```python
import shutil
from pathlib import Path

def _install_skill():
    """在首次加载时将我们的技能复制到 ~/.hermes/skills/。"""
    try:
        from hermes_cli.config import get_hermes_home
        dest = get_hermes_home() / "skills" / "my-plugin" / "SKILL.md"
    except Exception:
        dest = Path.home() / ".hermes" / "skills" / "my-plugin" / "SKILL.md"

    if dest.exists():
        return  # 不覆盖用户编辑的内容

    source = Path(__file__).parent / "skill.md"
    if source.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

def register(ctx):
    ctx.register_tool(...)
    _install_skill()
```

### 根据环境变量控制

如果你的插件需要 API 密钥：

```yaml
# plugin.yaml
requires_env:
  - WEATHER_API_KEY
```

如果 `WEATHER_API_KEY` 未设置，插件将被禁用并显示明确消息。不会崩溃，代理中不会出错 — 只是“Plugin weather disabled (missing: WEATHER_API_KEY)”。

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

### 注册多个钩子

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

可用的钩子：

| 钩子 | 触发时机 | 参数 | 返回值 |
|------|------|-----------|--------|
| `pre_tool_call` | 任何工具运行前 | `tool_name`, `args`, `task_id` | — |
| `post_tool_call` | 任何工具返回后 | `tool_name`, `args`, `result`, `task_id` | — |
| `pre_llm_call` | 每轮一次，在 LLM 循环前 | `session_id`, `user_message`, `conversation_history`, `is_first_turn`, `model`, `platform` | `{"context": "..."}` |
| `post_llm_call` | 每轮一次，在 LLM 循环后 | `session_id`, `user_message`, `assistant_response`, `conversation_history`, `model`, `platform` | — |
| `on_session_start` | 新会话创建时（仅第一轮） | `session_id`, `model`, `platform` | — |
| `on_session_end` | 每次 `run_conversation` 调用结束时 | `session_id`, `completed`, `interrupted`, `model`, `platform` | — |

大多数钩子是触发即忘的观察者。例外是 `pre_llm_call`：如果回调返回一个包含 `"context"` 键的字典（或纯字符串），该值将被附加到当前轮次的临时系统提示中。这允许记忆插件在不触及核心代码的情况下注入回忆的上下文。
如果钩子函数崩溃，会被记录日志并跳过；其他钩子和代理会继续正常运行。

### 通过 pip 分发

要公开分享插件，请在你的 Python 包中添加一个入口点：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# 插件将在下次 Hermes 启动时自动被发现
```

## 常见错误

**处理函数没有返回 JSON 字符串：**
```python
# 错误 — 返回了字典
def handler(args, **kwargs):
    return {"result": 42}

# 正确 — 返回 JSON 字符串
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**处理函数签名中缺少 `**kwargs`：**
```python
# 错误 — 如果 Hermes 传递了额外的上下文会出错
def handler(args):
    ...

# 正确
def handler(args, **kwargs):
    ...
```

**处理函数抛出异常：**
```python
# 错误 — 异常会向上传播，导致工具调用失败
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

**模式描述过于模糊：**
```python
# 不好 — 模型不知道何时使用它
"description": "Does stuff"

# 好 — 模型确切知道何时以及如何使用
"description": "计算数学表达式。用于算术、三角函数、对数。支持：+, -, *, /, **, sqrt, sin, cos, log, pi, e。"
```
