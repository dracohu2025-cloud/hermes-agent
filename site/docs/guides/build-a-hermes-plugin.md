---
sidebar_position: 9
sidebar_label: "构建插件"
title: "构建 Hermes 插件"
description: "一步步指导你构建一个完整的 Hermes 插件，包含工具、钩子、数据文件和技能"
---

# 构建 Hermes 插件 {#build-a-hermes-plugin}

本指南将带你从零开始构建一个完整的 Hermes 插件。最终你将得到一个包含多个工具、生命周期钩子、内置数据文件和打包技能的可用插件——涵盖了插件系统支持的所有功能。

## 你要构建的内容 {#what-you-re-building}

一个**计算器**插件，包含两个工具：
- `calculate` — 计算数学表达式（`2**16`、`sqrt(144)`、`pi * 5**2`）
- `unit_convert` — 单位换算（`100 F → 37.78 C`、`5 km → 3.11 mi`）

另外还有一个钩子，用于记录每次工具调用，以及一个打包的技能文件。

## 第一步：创建插件目录 {#step-1-create-the-plugin-directory}

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

## 第二步：编写清单文件 {#step-2-write-the-manifest}

创建 `plugin.yaml`：

```yaml
name: calculator
version: 1.0.0
description: 数学计算器 — 计算表达式和单位换算
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

这告诉 Hermes：“我是一个名为 calculator 的插件，我提供工具和钩子。” `provides_tools` 和 `provides_hooks` 字段是插件注册内容的列表。

你可以添加的可选字段：
```yaml
author: 你的名字
requires_env:          # 根据环境变量控制加载；安装时会提示
  - SOME_API_KEY       # 简单格式 — 缺少时插件被禁用
  - name: OTHER_KEY    # 丰富格式 — 安装时显示描述/链接
    description: "其他服务的密钥"
    url: "https://other.com/keys"
    secret: true
```

## 第三步：编写工具模式 {#step-3-write-the-tool-schemas}

创建 `schemas.py` — 这是 LLM 读取的内容，用于决定何时调用你的工具：

```python
"""工具模式 — LLM 看到的内容。"""

CALCULATE = {
    "name": "calculate",
    "description": (
        "计算一个数学表达式并返回结果。"
        "支持算术运算（+、-、*、/、**）、函数（sqrt、sin、cos、"
        "log、abs、round、floor、ceil）和常量（pi、e）。"
        "当用户询问任何数学问题时使用此工具。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式（例如 '2**10'、'sqrt(144)'）",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "在不同单位之间转换数值。支持长度（m、km、mi、ft、in）、"
        "重量（kg、lb、oz、g）、温度（C、F、K）、数据（B、KB、MB、GB、TB）"
        "和时间（s、min、hr、day）。"
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
                "description": "源单位（例如 'km'、'lb'、'F'、'GB'）",
            },
            "to_unit": {
                "type": "string",
                "description": "目标单位（例如 'mi'、'kg'、'C'、'MB'）",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```
**为什么模式很重要：** `description` 字段是 LLM 决定何时使用你的工具的依据。要具体说明它的作用以及何时使用。`parameters` 定义了 LLM 传递的参数。

## 第4步：编写工具处理程序 {#step-4-write-the-tool-handlers}

创建 `tools.py` —— 这是当 LLM 调用你的工具时实际执行的代码：

```python
"""工具处理程序——当 LLM 调用每个工具时运行的代码。"""

import json
import math

# 用于表达式求值的安全全局变量——无文件/网络访问
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

    处理程序的规则：
    1. 接收 args (dict) —— LLM 传递的参数
    2. 执行工作
    3. 返回 JSON 字符串 —— 始终如此，即使出错
    4. 接受 **kwargs 以保持向前兼容
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


# 转换表——值以基本单位表示
_LENGTH = {"m": 1, "km": 1000, "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "cm": 0.01}
_WEIGHT = {"kg": 1, "g": 0.001, "lb": 0.453592, "oz": 0.0283495}
_DATA = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_TIME = {"s": 1, "ms": 0.001, "min": 60, "hr": 3600, "day": 86400}


def _convert_temp(value, from_u, to_u):
    # 归一化到摄氏度
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # 转换到目标单位
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """在单位之间进行转换。"""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "Need value, from_unit, and to_unit"})

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

        return json.dumps({"error": f"Cannot convert {from_unit} → {to_unit}"})
    except Exception as e:
        return json.dumps({"error": f"Conversion failed: {e}"})
```
**处理函数的关键规则：**
1. **签名：** `def my_handler(args: dict, **kwargs) -> str`
2. **返回值：** 始终是 JSON 字符串。成功和错误都如此。
3. **绝不抛出异常：** 捕获所有异常，改为返回错误 JSON。
4. **接受 `**kwargs`：** Hermes 未来可能会传递额外的上下文。

## 第 5 步：编写注册代码 {#step-5-write-the-registration}

创建 `__init__.py` —— 它将模式与处理函数连接起来：

```python
"""计算器插件 — 注册。"""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# 通过钩子跟踪工具使用情况
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """钩子：每次工具调用后运行（不仅限于我们的工具）。"""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("工具被调用：%s（会话 %s）", tool_name, task_id)


def register(ctx):
    """将模式与处理函数连接起来并注册钩子。"""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # 此钩子会为所有工具调用触发，而不仅限于我们的工具
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的作用：**
- 在启动时恰好调用一次
- `ctx.register_tool()` 将你的工具放入注册表 —— 模型会立即看到它
- `ctx.register_hook()` 订阅生命周期事件
- `ctx.register_cli_command()` 注册一个 CLI 子命令（例如 `hermes my-plugin &lt;subcommand&gt;`）
- `ctx.register_command()` 注册一个会话内斜杠命令（例如在 CLI / 网关聊天中输入 `/myplugin &lt;args&gt;`）—— 请参阅下面的[注册斜杠命令](#register-slash-commands)
- `ctx.dispatch_tool(name, arguments)` —— 调用任何其他工具（内置的或来自其他插件的），并自动接入父 Agent 的上下文（审批、凭据、任务 ID）。在需要调用 `terminal`、`read_file` 或任何其他工具（就像模型直接调用它们一样）的斜杠命令处理函数中非常有用。
- 如果此函数崩溃，插件会被禁用，但 Hermes 会继续正常运行

**`dispatch_tool` 示例 —— 一个运行工具的斜杠命令：**

```python
def handle_scan(ctx, argstr):
    """通过注册表调用终端工具来实现 /scan。"""
    result = ctx.dispatch_tool("terminal", {"command": f"find . -name '{argstr}'"})
    return result  # 返回给调用者的聊天界面

def register(ctx):
    ctx.register_command("scan", handle_scan, help="查找匹配 glob 模式的文件")
```

被分发的工具会经过正常的审批、脱敏和预算管线 —— 这是一个真实的工具调用，而不是绕过它们的捷径。

## 第 6 步：测试 {#step-6-test-it}

启动 Hermes：

```bash
hermes
```

你应该会在横幅的工具列表中看到 `calculator: calculate, unit_convert`。

尝试以下提示：
```
2 的 16 次方是多少？
将 100 华氏度转换为摄氏度
2 乘以 π 的平方根是多少？
1.5 TB 是多少 GB？
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

## 插件的最终目录结构 {#your-plugin-s-final-structure}

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # “我是 calculator，我提供工具和钩子”
├── __init__.py      # 接线：schemas → handlers，注册 hooks
├── schemas.py       # LLM 读取的内容（描述 + 参数规格）
└── tools.py         # 运行时执行的代码（calculate、unit_convert 函数）
```

四个文件，职责清晰：
- **Manifest** 声明了插件是什么
- **Schemas** 为 LLM 描述工具
- **Handlers** 实现具体逻辑
- **Registration** 连接一切

## 插件还能做什么？ {#what-else-can-plugins-do}

### 附带数据文件 {#ship-data-files}

在插件目录中放入任意文件，并在导入时读取它们：

```python
# 在 tools.py 或 __init__.py 中
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

### 打包技能 {#bundle-skills}

插件可以附带技能文件，Agent 通过 `skill_view("plugin:skill")` 加载。在 `__init__.py` 中注册它们：

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

现在 Agent 可以用带命名空间的名字加载你的技能：

```python
skill_view("my-plugin:my-workflow")   # → 插件的版本
skill_view("my-workflow")              # → 内置版本（不变）
```

**关键属性：**
- 插件技能是 **只读的** —— 它们不会进入 `~/.hermes/skills/`，也不能通过 `skill_manage` 编辑。
- 插件技能 **不会** 在系统提示的 `&lt;available_skills&gt;` 索引中列出 —— 它们是按需显式加载的。
- 纯技能名称不受影响 —— 命名空间避免了与内置技能冲突。
- 当 Agent 加载插件技能时，会前置一个捆绑上下文横幅，列出同一插件中的兄弟技能。

:::tip 旧模式
<a id="legacy-pattern"></a>
旧的 `shutil.copy2` 模式（将技能复制到 `~/.hermes/skills/`）仍然可用，但会产生与内置技能名称冲突的风险。新插件请优先使用 `ctx.register_skill()`。
:::

### 基于环境变量做门控 {#gate-on-environment-variables}

如果你的插件需要 API 密钥：

```yaml
# plugin.yaml — 简单格式（向后兼容）
requires_env:
  - WEATHER_API_KEY
```

如果 `WEATHER_API_KEY` 未设置，插件会被禁用并显示一条明确的消息。不会崩溃，Agent 也不会报错 —— 只会显示“插件 weather 已禁用（缺少：WEATHER_API_KEY）”。

当用户运行 `hermes plugins install` 时，对于任何缺少的 `requires_env` 变量，系统会 **交互式提示** 用户输入。值会自动保存到 `.env` 文件中。

为获得更好的安装体验，请使用带有描述和注册链接的丰富格式：
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
| `description` | 否 | 安装提示时向用户显示的内容 |
| `url` | 否 | 获取凭证的地址 |
| `secret` | 否 | 如果为 `true`，输入内容会被隐藏（类似密码字段） |

两种格式可以在同一个列表中混用。已设置的变量会被静默跳过。

### 条件性工具可用性 {#conditional-tool-availability}

对于依赖可选库的工具：

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # 返回 False 则工具对模型隐藏
)
```

### 注册多个钩子 {#register-multiple-hooks}

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("pre_llm_call", inject_memory)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

### 钩子参考 {#hook-reference}

每个钩子的完整文档请参见 **[事件钩子参考](/user-guide/features/hooks#plugin-hooks)** —— 包括回调签名、参数表、触发时机和示例。以下是摘要：

| 钩子 | 触发时机 | 回调签名 | 返回值 |
|------|-----------|-------------------|---------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 任何工具执行之前 | `tool_name: str, args: dict, task_id: str` | 忽略 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 任何工具返回之后 | `tool_name: str, args: dict, result: str, task_id: str, duration_ms: int` | 忽略 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮一次，在工具调用循环之前 | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [上下文注入](#pre_llm_call-context-injection) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮一次，在工具调用循环之后（仅成功轮次） | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | 忽略 |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 新会话创建时（仅第一轮） | `session_id: str, model: str, platform: str` | 忽略 |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束 + CLI 退出时 | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | 忽略 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/网关销毁活跃会话时 | `session_id: str \| None, platform: str` | 忽略 |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | 网关切换新会话密钥时（`/new`、`/reset`） | `session_id: str, platform: str` | 忽略 |
大多数 hook 是即发即忘的观察者 —— 它们的返回值被忽略。例外是 `pre_llm_call`，它可以向对话中注入上下文。

所有回调都应接受 `**kwargs` 以保证向前兼容。如果某个 hook 回调崩溃，它会被记录并跳过。其他 hook 和 agent 继续正常运行。

<a id="prellmcall-context-injection"></a>
### `pre_llm_call` 上下文注入 {#pre_llm_call-context-injection}

这是唯一返回值被使用的 hook。当 `pre_llm_call` 回调返回一个包含 `"context"` 键的字典（或纯字符串）时，Hermes 会将那段文本注入到**当前轮次的用户消息**末尾。这是记忆插件、RAG 集成、护栏以及任何需要为模型提供额外上下文的插件所使用的机制。

#### 返回格式 {#return-format}

```python
# 返回包含 context 键的字典
return {"context": "Recalled memories:\n- User prefers dark mode\n- Last project: hermes-agent"}

# 也可以直接返回纯字符串（等价于上面的字典形式）
return "Recalled memories:\n- User prefers dark mode"

# 返回 None 或不返回 → 不注入（仅作为观察者）
return None
```

任何非 None、非空且带有 `"context"` 键的返回（或非空纯字符串）都会被收集并追加到当前轮次的用户消息中。

#### 注入机制 {#how-injection-works}

注入的上下文会被追加到**用户消息**中，而不是系统提示中。这是一个有意为之的设计选择：

- **保留 prompt 缓存** —— 系统提示在跨轮次中保持不变。Anthropic 和 OpenRouter 会缓存系统提示前缀，因此保持其稳定可在多轮对话中节省 75% 以上的输入 token。如果插件修改了系统提示，每一轮都会缓存未命中。
- **即时性** —— 注入仅在 API 调用时生效。对话历史中的原始用户消息永远不会被修改，也不会持久化到会话数据库中。
- **系统提示是 Hermes 的领地** —— 它包含模型特定的指导、工具执行规则、人格指令以及缓存的技能内容。插件在用户输入旁边贡献上下文，而不是更改 agent 的核心指令。

#### 示例：记忆召回插件 {#example-memory-recall-plugin}

```python
"""记忆插件 —— 从向量存储中召回相关上下文。"""

import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall_context(session_id, user_message, is_first_turn, **kwargs):
    """在每次 LLM 轮次前调用。返回召回的回忆内容。"""
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
        return None  # 静默失败，不破坏 agent

def register(ctx):
    ctx.register_hook("pre_llm_call", recall_context)
```

#### 示例：护栏插件 {#example-guardrails-plugin}
```python
"""Guardrails 插件 — 强制执行内容策略。"""

POLICY = """您必须遵守本次会话的以下内容策略：
- 绝不允许生成访问工作目录之外文件系统的代码
- 在执行破坏性操作前必须发出警告
- 拒绝涉及个人数据提取的请求"""

def inject_guardrails(**kwargs):
    """在每一轮对话中注入策略文本。"""
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", inject_guardrails)
```

#### 示例：仅观察钩子（无注入） {#example-observer-only-hook-no-injection}

```python
"""Analytics 插件 — 跟踪轮次元数据，不注入上下文。"""

import logging
logger = logging.getLogger(__name__)

def log_turn(session_id, user_message, model, is_first_turn, **kwargs):
    """在每次 LLM 调用前触发。返回 None — 不注入上下文。"""
    logger.info("轮次: session=%s model=%s first=%s msg_len=%d",
                session_id, model, is_first_turn, len(user_message or ""))
    # 无返回 → 不注入

def register(ctx):
    ctx.register_hook("pre_llm_call", log_turn)
```

#### 多个插件返回上下文 {#multiple-plugins-returning-context}

当多个插件从 `pre_llm_call` 返回上下文时，它们的输出会以双换行符连接，并一起附加到用户消息中。顺序遵循插件发现顺序（按插件目录名称的字母顺序）。

### 注册 CLI 命令 {#register-cli-commands}

插件可以添加自己的 `hermes &lt;plugin&gt;` 子命令树：

```python
def _my_command(args):
    """hermes my-plugin <subcommand> 的处理程序。"""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("一切正常！")
    elif sub == "config":
        print("当前配置: ...")
    else:
        print("用法: hermes my-plugin <status|config>")

def _setup_argparse(subparser):
    """构建 hermes my-plugin 的 argparse 树。"""
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="显示插件状态")
    subs.add_parser("config", help="显示插件配置")
    subparser.set_defaults(func=_my_command)

def register(ctx):
    ctx.register_tool(...)
    ctx.register_cli_command(
        name="my-plugin",
        help="管理我的插件",
        setup_fn=_setup_argparse,
        handler_fn=_my_command,
    )
```

注册后，用户可以运行 `hermes my-plugin status`、`hermes my-plugin config` 等命令。

**内存提供者插件** 采用基于约定的方式：只需在插件的 `cli.py` 文件中添加一个 `register_cli(subparser)` 函数。内存插件发现系统会自动找到它 — 无需调用 `ctx.register_cli_command()`。详情请参阅 [内存提供者插件指南](/developer-guide/memory-provider-plugin#adding-cli-commands)。

**活跃提供者门控：** 内存插件 CLI 命令仅在其提供者是配置中活跃的 `memory.provider` 时才会显示。如果用户尚未设置您的提供者，您的 CLI 命令不会使帮助输出变得杂乱。

### 注册斜杠命令 {#register-slash-commands}

插件可以注册会话内的斜杠命令 — 用户在对话过程中输入的命令（如 `/lcm status` 或 `/ping`）。这些命令在 CLI 和网关（Telegram、Discord 等）中均有效。
```python
def _handle_status(raw_args: str) -> str:
    """处理 /mystatus 的命令处理器——接收命令名称之后的所有内容。"""
    if raw_args.strip() == "help":
        return "用法：/mystatus [help|check]"
    return "插件状态：所有系统正常"

def register(ctx):
    ctx.register_command(
        "mystatus",
        handler=_handle_status,
        description="显示插件状态",
    )
```

注册后，用户可以在任何会话中输入 `/mystatus`。该命令会出现在自动补全、`/help` 输出以及 Telegram 机器人菜单中。

**签名：** `ctx.register_command(name: str, handler: Callable, description: str = "")`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | `str` | 命令名称，不带前导斜杠（例如 `"lcm"`、`"mystatus"`） |
| `handler` | `Callable[[str], str \| None]` | 接收原始参数字符串。也可以是 `async` 异步函数。 |
| `description` | `str` | 显示在 `/help`、自动补全和 Telegram 机器人菜单中 |

**与 `register_cli_command()` 的主要区别：**

| | `register_command()` | `register_cli_command()` |
|---|---|---|
| 调用方式 | 在会话中输入 `/name` | 在终端中输入 `hermes name` |
| 适用场景 | CLI 会话、Telegram、Discord 等 | 仅限终端 |
| 处理器接收 | 原始参数字符串 | argparse `Namespace` |
| 使用场景 | 诊断、状态、快速操作 | 复杂的子命令树、设置向导 |

**冲突保护：** 如果某个插件尝试注册与内置命令（`help`、`model`、`new` 等）冲突的名称，注册会被静默拒绝，并记录一条日志警告。内置命令始终优先。

**异步处理器：** 网关调度会自动检测并等待异步处理器，因此你可以使用同步或异步函数：

```python
async def _handle_check(raw_args: str) -> str:
    result = await some_async_operation()
    return f"检查结果：{result}"

def register(ctx):
    ctx.register_command("check", handler=_handle_check, description="运行异步检查")
```

:::tip
本指南涵盖**通用插件**（工具、钩子、斜杠命令、CLI 命令）。对于专门的插件类型，请参阅：
- [内存提供插件](/developer-guide/memory-provider-plugin) — 跨会话知识后端
- [上下文引擎插件](/developer-guide/context-engine-plugin) — 替代的上下文管理策略
:::

### 通过 pip 分发 {#distribute-via-pip}

若要公开分享插件，请在你的 Python 包中添加一个入口点：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# 下次启动 hermes 时插件会被自动发现
```

### 为 NixOS 分发 {#distribute-for-nixos}

如果你提供了带有入口点的 `pyproject.toml`，NixOS 用户可以声明式地安装你的插件：

**入口点插件**（推荐用于分发）：
```nix
# 用户的 configuration.nix
services.hermes-agent.extraPythonPackages = [
  (pkgs.python312Packages.buildPythonPackage {
    pname = "my-plugin";
    version = "1.0.0";
    src = pkgs.fetchFromGitHub {
      owner = "you";
      repo = "hermes-my-plugin";
      rev = "v1.0.0";
      hash = "sha256-...";  # nix-prefetch-url --unpack
    };
    format = "pyproject";
    build-system = [ pkgs.python312Packages.setuptools ];
  })
];
```
**目录插件**（无需 `pyproject.toml`）：
```nix
services.hermes-agent.extraPlugins = [
  (pkgs.fetchFromGitHub {
    owner = "you";
    repo = "hermes-my-plugin";
    rev = "v1.0.0";
    hash = "sha256-...";
  })
];
```

有关包括覆盖使用和冲突检查在内的完整文档，请参阅 [Nix 设置指南](/getting-started/nix-setup#plugins)。

## 常见错误 {#common-mistakes}

**Handler 未返回 JSON 字符串：**
```python
# 错误 — 返回了一个字典
def handler(args, **kwargs):
    return {"result": 42}

# 正确 — 返回一个 JSON 字符串
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**Handler 签名中缺少 `**kwargs`：**
```python
# 错误 — 如果 Hermes 传递了额外上下文，将会出错
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

**Schema 描述过于模糊：**
```python
# 不好 — 模型不知道何时使用它
"description": "做事情"

# 好 — 模型确切知道何时以及如何使用
"description": "计算数学表达式。用于算术、三角函数、对数。支持：+、-、*、/、**、sqrt、sin、cos、log、pi、e。"
```
