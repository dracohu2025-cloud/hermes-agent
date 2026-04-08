---
sidebar_position: 9
sidebar_label: "构建插件"
title: "构建 Hermes 插件"
description: "逐步指导如何构建一个包含工具、钩子、数据文件和技能的完整 Hermes 插件"
---

# 构建 Hermes 插件

本指南将带你从零开始构建一个完整的 Hermes 插件。完成后，你将拥有一个包含多个工具、生命周期钩子、附带数据文件以及捆绑技能的可用插件 —— 涵盖了插件系统支持的所有功能。

## 你将要构建的内容

一个包含两个工具的 **计算器 (calculator)** 插件：
- `calculate` — 计算数学表达式（如 `2**16`, `sqrt(144)`, `pi * 5**2`）
- `unit_convert` — 进行单位换算（如 `100 F → 37.78 C`, `5 km → 3.11 mi`）

此外还包含一个记录每次工具调用的钩子，以及一个捆绑的技能文件。

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
description: 数学计算器 — 计算表达式并转换单位
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

这告诉 Hermes：“我是一个名为 calculator 的插件，我提供工具和钩子。” `provides_tools` 和 `provides_hooks` 字段是该插件注册内容的列表。

你可以添加的可选字段：
```yaml
author: Your Name
requires_env:          # 根据环境变量决定是否加载；安装时会提示
  - SOME_API_KEY       # 简单格式 — 如果缺失则禁用插件
  - name: OTHER_KEY    # 丰富格式 — 安装时显示描述/链接
    description: "Other 服务的密钥"
    url: "https://other.com/keys"
    secret: true
```

## 第 3 步：编写工具 Schema

创建 `schemas.py` — 这是 LLM 用来决定何时调用你的工具的依据：

```python
"""工具 Schema — LLM 看到的内容。"""

CALCULATE = {
    "name": "calculate",
    "description": (
        "计算数学表达式并返回结果。"
        "支持算术运算 (+, -, *, /, **)、函数 (sqrt, sin, cos, "
        "log, abs, round, floor, ceil) 以及常量 (pi, e)。"
        "用于处理用户询问的任何数学计算。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "待计算的数学表达式 (例如 '2**10', 'sqrt(144)')",
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
        "以及时间 (s, min, hr, day)。"
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
                "description": "源单位 (例如 'km', 'lb', 'F', 'GB')",
            },
            "to_unit": {
                "type": "string",
                "description": "目标单位 (例如 'mi', 'kg', 'C', 'MB')",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**为什么 Schema 很重要：** `description` 字段是 LLM 决定何时使用你的工具的关键。请务必详细说明它的功能和使用场景。`parameters` 定义了 LLM 传递的参数。

## 第 4 步：编写工具处理器 (Handlers)

创建 `tools.py` — 这是 LLM 调用工具时实际执行的代码：

```python
"""工具处理器 — LLM 调用每个工具时运行的代码。"""

import json
import math

# 用于表达式计算的安全全局变量 — 禁止文件/网络访问
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

    处理器规则：
    1. 接收 args (dict) — LLM 传递的参数
    2. 执行工作
    3. 返回 JSON 字符串 — 始终如此，即使报错也是
    4. 接收 **kwargs 以保证向前兼容性
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


# 换算表 — 数值为相对于基本单位的比例
_LENGTH = {"m": 1, "km": 1000, "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "cm": 0.01}
_WEIGHT = {"kg": 1, "g": 0.001, "lb": 0.453592, "oz": 0.0283495}
_DATA = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_TIME = {"s": 1, "ms": 0.001, "min": 60, "hr": 3600, "day": 86400}


def _convert_temp(value, from_u, to_u):
    # 归一化到摄氏度
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # 转换为目标单位
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """在单位之间转换。"""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "Need value, from_unit, and to_unit"})

    try:
        # 温度转换
        if from_unit.upper() in {"C","F","K"} and to_unit.upper() in {"C","F","K"}:
            result = _convert_temp(float(value), from_unit.upper(), to_unit.upper())
            return json.dumps({"input": f"{value} {from_unit}", "result": round(result, 4),
                             "output": f"{round(result, 4)} {to_unit}"})

        # 基于比例的转换
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

**处理器的关键规则：**
1. **函数签名：** `def my_handler(args: dict, **kwargs) -> str`
2. **返回值：** 始终是 JSON 字符串。成功和错误皆然。
3. **严禁抛出异常：** 捕获所有异常，改为返回错误 JSON。
4. **接收 `**kwargs`：** Hermes 未来可能会传递额外的上下文信息。

## 第 5 步：编写注册逻辑

创建 `__init__.py` — 这将 Schema 与处理器连接起来：

```python
"""计算器插件 — 注册。"""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# 通过钩子跟踪工具使用情况
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """钩子：在每次工具调用后运行（不仅限于我们自己的工具）。"""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("Tool called: %s (session %s)", tool_name, task_id)


def register(ctx):
    """将 Schema 连接到处理器并注册钩子。"""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # 此钩子对所有工具调用生效，而不仅仅是我们自己的工具
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```
**`register()` 的作用：**
- 在启动时仅调用一次
- `ctx.register_tool()` 将你的工具放入注册表 —— 模型会立即看到它
- `ctx.register_hook()` 订阅生命周期事件
- `ctx.register_cli_command()` 注册 CLI 子命令（例如 `hermes my-plugin <subcommand>`）
- 如果此函数崩溃，该插件将被禁用，但 Hermes 仍能正常运行

## 第 6 步：测试

启动 Hermes：

```bash
hermes
```

你应该能在横幅的工具列表中看到 `calculator: calculate, unit_convert`。

尝试这些提示词：
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

## 插件的最终结构

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # “我是 calculator，我提供工具和钩子”
├── __init__.py      # 连线：schemas → handlers，注册钩子
├── schemas.py       # LLM 读取的内容（描述 + 参数规范）
└── tools.py         # 运行的内容（calculate, unit_convert 函数）
```

四个文件，职责分离清晰：
- **Manifest (清单)** 声明插件是什么
- **Schemas (模式)** 为 LLM 描述工具
- **Handlers (处理器)** 实现实际逻辑
- **Registration (注册)** 连接一切

## 插件还能做什么？

### 携带数据文件

将任何文件放在插件目录中，并在导入时读取它们：

```python
# 在 tools.py 或 __init__.py 中
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

### 捆绑 Skill (技能)

包含一个 `skill.md` 文件并在注册期间安装它：

```python
import shutil
from pathlib import Path

def _install_skill():
    """首次加载时将我们的 skill 复制到 ~/.hermes/skills/。"""
    try:
        from hermes_cli.config import get_hermes_home
        dest = get_hermes_home() / "skills" / "my-plugin" / "SKILL.md"
    except Exception:
        dest = Path.home() / ".hermes" / "skills" / "my-plugin" / "SKILL.md"

    if dest.exists():
        return  # 不要覆盖用户的修改

    source = Path(__file__).parent / "skill.md"
    if source.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

def register(ctx):
    ctx.register_tool(...)
    _install_skill()
```

### 环境变量门控

如果你的插件需要 API 密钥：

```yaml
# plugin.yaml — 简单格式（向后兼容）
requires_env:
  - WEATHER_API_KEY
```

如果未设置 `WEATHER_API_KEY`，插件将被禁用并显示清晰的消息。不会崩溃，Agent 中也不会报错 —— 只会显示 "Plugin weather disabled (missing: WEATHER_API_KEY)"。

当用户运行 `hermes plugins install` 时，系统会**交互式地提示**用户输入任何缺失的 `requires_env` 变量。数值会自动保存到 `.env` 中。

为了获得更好的安装体验，可以使用带有描述和注册 URL 的丰富格式：

```yaml
# plugin.yaml — 丰富格式
requires_env:
  - name: WEATHER_API_KEY
    description: "OpenWeather 的 API 密钥"
    url: "https://openweathermap.org/api"
    secret: true
```

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 环境变量名称 |
| `description` | 否 | 安装提示期间显示给用户的内容 |
| `url` | 否 | 获取凭据的地址 |
| `secret` | 否 | 如果为 `true`，输入内容将被隐藏（类似密码字段） |

两种格式可以在同一个列表中混合使用。已经设置过的变量将被静默跳过。

### 条件化工具可用性

对于依赖可选库的工具：

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # False = 工具对模型隐藏
)
```

### 注册多个钩子 (Hooks)

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("pre_llm_call", inject_memory)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

### 钩子参考

每个钩子在 **[事件钩子参考](/user-guide/features/hooks#plugin-hooks)** 中都有完整文档 —— 包括回调签名、参数表、确切的触发时间以及示例。以下是摘要：

| 钩子 | 触发时机 | 回调签名 | 返回值 |
|------|-----------|-------------------|---------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 任何工具执行前 | `tool_name: str, args: dict, task_id: str` | 忽略 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 任何工具返回后 | `tool_name: str, args: dict, result: str, task_id: str` | 忽略 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮对话一次，在工具调用循环之前 | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [上下文注入](#pre_llm_call-context-injection) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮对话一次，在工具调用循环之后（仅限成功的轮次） | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | 忽略 |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 创建新会话（仅限首轮） | `session_id: str, model: str, platform: str` | 忽略 |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束 + CLI 退出 | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | 忽略 |
| [`pre_api_request`](/user-guide/features/hooks#pre_api_request) | 每次向 LLM 提供商发送 HTTP 请求前 | `method: str, url: str, headers: dict, body: dict` | 忽略 |
| [`post_api_request`](/user-guide/features/hooks#post_api_request) | 每次收到 LLM 提供商的 HTTP 响应后 | `method: str, url: str, status_code: int, response: dict` | 忽略 |

大多数钩子都是“触发即忘”的观察者 —— 它们的返回值会被忽略。唯一的例外是 `pre_llm_call`，它可以向对话中注入上下文。

为了向前兼容，所有回调都应接受 `**kwargs`。如果钩子回调崩溃，系统会记录日志并跳过它。其他钩子和 Agent 将继续正常运行。

### `pre_llm_call` 上下文注入

这是唯一一个返回值有意义的钩子。当 `pre_llm_call` 回调返回一个带有 `"context"` 键的字典（或一个纯字符串）时，Hermes 会将该文本注入到**当前轮次的用户消息**中。这是内存插件、RAG 集成、护栏（guardrails）以及任何需要为模型提供额外上下文的插件的实现机制。

#### 返回格式

```python
# 带有 context 键的字典
return {"context": "召回的记忆：\n- 用户偏好深色模式\n- 最近的项目：hermes-agent"}

# 纯字符串（等同于上面的字典形式）
return "召回的记忆：\n- 用户偏好深色模式"

# 返回 None 或不返回 → 不注入（仅作为观察者）
return None
```

任何非 None、非空的返回，只要包含 `"context"` 键（或者是纯非空字符串），都会被收集并附加到当前轮次的用户消息中。

#### 注入工作原理

注入的上下文被附加到**用户消息**中，而不是系统提示词（system prompt）。这是一个深思熟虑的设计选择：

- **保留提示词缓存 (Prompt cache preservation)** —— 系统提示词在各轮对话中保持一致。Anthropic 和 OpenRouter 会缓存系统提示词前缀，因此保持其稳定可以在多轮对话中节省 75% 以上的输入 Token。如果插件修改了系统提示词，每一轮都会导致缓存失效。
- **临时性** —— 注入仅在 API 调用时发生。对话历史中的原始用户消息永远不会被更改，也不会持久化到会话数据库中。
- **系统提示词是 Hermes 的领地** —— 它包含模型特定的引导、工具执行规则、性格指令和缓存的技能内容。插件通过在用户输入旁提供上下文来做出贡献，而不是通过修改 Agent 的核心指令。
#### 示例：记忆召回插件

```python
"""Memory 插件 — 从向量数据库中召回相关的上下文。"""

import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall_context(session_id, user_message, is_first_turn, **kwargs):
    """在每次 LLM 轮次之前调用。返回召回的记忆。"""
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None  # 没有可注入的内容

        text = "Recalled context from previous sessions:\n"
        text += "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None  # 静默失败，不要中断 Agent
        
def register(ctx):
    ctx.register_hook("pre_llm_call", recall_context)
```

#### 示例：护栏（Guardrails）插件

```python
"""Guardrails 插件 — 强制执行内容策略。"""

POLICY = """You MUST follow these content policies for this session:
- Never generate code that accesses the filesystem outside the working directory
- Always warn before executing destructive operations
- Refuse requests involving personal data extraction"""

def inject_guardrails(**kwargs):
    """在每一轮对话中注入策略文本。"""
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", inject_guardrails)
```

#### 示例：仅观察钩子（不注入内容）

```python
"""Analytics 插件 — 追踪对话轮次的元数据，不注入上下文。"""

import logging
logger = logging.getLogger(__name__)

def log_turn(session_id, user_message, model, is_first_turn, **kwargs):
    """在每次 LLM 调用前触发。返回 None — 不注入上下文。"""
    logger.info("Turn: session=%s model=%s first=%s msg_len=%d",
                session_id, model, is_first_turn, len(user_message or ""))
    # 没有 return → 不注入

def register(ctx):
    ctx.register_hook("pre_llm_call", log_turn)
```

#### 多个插件返回上下文

当多个插件从 `pre_llm_call` 返回上下文时，它们的输出将通过双换行符连接，并一起附加到用户消息中。顺序遵循插件发现顺序（按插件目录名称的字母顺序）。

### 注册 CLI 命令

插件可以添加自己的 `hermes <plugin>` 子命令树：

```python
def _my_command(args):
    """hermes my-plugin <subcommand> 的处理器。"""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("All good!")
    elif sub == "config":
        print("Current config: ...")
    else:
        print("Usage: hermes my-plugin <status|config>")

def _setup_argparse(subparser):
    """为 hermes my-plugin 构建 argparse 树。"""
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

注册后，用户可以运行 `hermes my-plugin status`、`hermes my-plugin config` 等。

**Memory provider 插件** 则采用基于约定的方法：在插件的 `cli.py` 文件中添加一个 `register_cli(subparser)` 函数。Memory 插件发现系统会自动找到它 —— 不需要调用 `ctx.register_cli_command()`。详情请参阅 [Memory Provider 插件指南](/developer-guide/memory-provider-plugin#adding-cli-commands)。

**活动提供商门控（Active-provider gating）：** Memory 插件的 CLI 命令仅在其提供商是配置中活动的 `memory.provider` 时才会显示。如果用户没有设置你的提供商，你的 CLI 命令就不会干扰帮助输出。

### 通过 pip 分发

如需公开分享插件，请在你的 Python 包中添加一个 entry point：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# 插件将在下次 hermes 启动时自动被发现
```

## 常见错误

**处理器未返回 JSON 字符串：**
```python
# 错误 — 返回了一个字典
def handler(args, **kwargs):
    return {"result": 42}

# 正确 — 返回一个 JSON 字符串
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**处理器签名中缺少 `**kwargs`：**
```python
# 错误 — 如果 Hermes 传递额外的上下文，将会报错
def handler(args):
    ...

# 正确
def handler(args, **kwargs):
    ...
```

**处理器抛出异常：**
```python
# 错误 — 异常会传播，导致工具调用失败
def handler(args, **kwargs):
    result = 1 / int(args["value"])  # ZeroDivisionError!
    return json.dumps({"result": result})

# 正确 — 捕获并返回错误 JSON
def handler(args, **kwargs):
    try:
        result = 1 / int(args.get("value", 0))
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**Schema 描述太模糊：**
```python
# 差 — 模型不知道什么时候该使用它
"description": "Does stuff"

# 好 — 模型清楚地知道何时以及如何使用
"description": "Evaluate a mathematical expression. Use for arithmetic, trig, logarithms. Supports: +, -, *, /, **, sqrt, sin, cos, log, pi, e."
```
