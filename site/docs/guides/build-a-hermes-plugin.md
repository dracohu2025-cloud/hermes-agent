---
sidebar_position: 9
sidebar_label: "构建插件"
title: "构建 Hermes 插件"
description: "关于如何使用工具、钩子、数据文件和技能来构建完整 Hermes 插件的分步指南"
---

<a id="build-a-hermes-plugin"></a>
# 构建 Hermes 插件

本指南将带你从头开始构建一个完整的 Hermes 插件。完成本指南后，你将拥有一个包含多个工具、生命周期钩子、内置数据文件和打包技能的可运行插件——涵盖了插件系统支持的所有功能。

:::info 不确定你需要哪份指南？
<a id="not-sure-which-guide-you-need"></a>
Hermes 有多个不同的可插拔接口——有些使用 Python 的 `register_*` API，另一些则是配置驱动或基于目录放置的。请先使用此对照表：

| 如果你想添加… | 请阅读 |
|---|---|
| 自定义工具、钩子、斜杠命令、技能或 CLI 子命令 | **本指南**（通用插件接口） |
| 一个 **LLM / 推理后端**（新的提供商） | [模型提供商插件](/developer-guide/model-provider-plugin) |
| 一个 **网关通道**（Discord/Telegram/IRC/Teams 等） | [添加平台适配器](/developer-guide/adding-platform-adapters) |
| 一个 **记忆后端**（Honcho/Mem0/Supermemory 等） | [记忆提供商插件](/developer-guide/memory-provider-plugin) |
| 一个 **上下文压缩引擎** | [上下文引擎插件](/developer-guide/context-engine-plugin) |
| 一个 **图像生成后端** | [图像生成提供商插件](/developer-guide/image-gen-provider-plugin) |
| 一个 **视频生成后端** | [视频生成提供商插件](/developer-guide/video-gen-provider-plugin) |
| 一个 **TTS 后端**（任何 CLI——Piper、VoxCPM、Kokoro、语音克隆等） | [TTS 自定义命令提供商](/user-guide/features/tts#custom-command-providers)——配置驱动，无需 Python |
| 一个 **STT 后端**（自定义 whisper / ASR CLI） | [语音消息转录](/user-guide/features/tts#voice-message-transcription-stt)——将 `HERMES_LOCAL_STT_COMMAND` 设置为 shell 模板 |
| 通过 **MCP 的外部工具**（文件系统、GitHub、Linear、任何 MCP 服务器） | [MCP](/user-guide/features/mcp)——在 `config.yaml` 中声明 `mcp_servers.&lt;name&gt;` |
| **网关事件钩子**（在启动、会话事件、命令时触发） | [事件钩子](/user-guide/features/hooks#gateway-event-hooks)——将 `HOOK.yaml` + `handler.py` 放入 `~/.hermes/hooks/&lt;name&gt;/` |
| **Shell 钩子**（在事件时运行 shell 命令） | [Shell 钩子](/user-guide/features/hooks#shell-hooks)——在 `config.yaml` 的 `hooks:` 下声明 |
| **额外的技能来源**（自定义 GitHub 仓库、私有技能索引） | [技能](/user-guide/features/skills)——`hermes skills tap add &lt;repo&gt;` · [发布 tap](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| 一个一流的 **核心** 推理提供商（非插件） | [添加提供商](/developer-guide/adding-providers) |

请参阅完整的[可插拔接口表](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each)，以获取所有扩展接口的汇总视图，包括配置驱动（TTS、STT、MCP、shell 钩子）和目录放置（网关钩子）风格。
:::

<a id="what-you-re-building"></a>
## 你要构建的内容

一个包含两个工具的**计算器**插件：
- `calculate` — 计算数学表达式（`2**16`、`sqrt(144)`、`pi * 5**2`）
- `unit_convert` — 单位转换（`100 F → 37.78 C`、`5 km → 3.11 mi`）
加上一个记录每次工具调用的钩子，以及一个打包好的技能文件。

<a id="step-1-create-the-plugin-directory"></a>
## 第一步：创建插件目录

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

<a id="step-2-write-the-manifest"></a>
## 第二步：编写清单文件

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

这告诉 Hermes："我是一个名为 calculator 的插件，我提供工具和钩子。" `provides_tools` 和 `provides_hooks` 字段列出了插件注册的内容。

你可以添加的可选字段：
```yaml
author: Your Name
requires_env:          # 根据环境变量控制加载；安装时提示
  - SOME_API_KEY       # 简单格式 — 如果缺失则禁用插件
  - name: OTHER_KEY    # 丰富格式 — 安装时显示描述/URL
    description: "Other 服务的密钥"
    url: "https://other.com/keys"
    secret: true
```

<a id="step-3-write-the-tool-schemas"></a>
## 第三步：编写工具模式

创建 `schemas.py` — LLM 通过它来决定何时调用你的工具：

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
                "description": "要计算的数学表达式（例如：'2**10'、'sqrt(144)'）",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "在不同单位之间转换数值。支持长度 (m, km, mi, ft, in)、"
        "重量 (kg, lb, oz, g)、温度 (C, F, K)、数据 (B, KB, MB, GB, TB)"
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
                "description": "源单位（例如：'km'、'lb'、'F'、'GB'）",
            },
            "to_unit": {
                "type": "string",
                "description": "目标单位（例如：'mi'、'kg'、'C'、'MB'）",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**为什么模式很重要：** `description` 字段是 LLM 决定何时使用你的工具的依据。要具体说明它的功能和使用场景。`parameters` 定义了 LLM 会传递哪些参数。

<a id="step-4-write-the-tool-handlers"></a>
## 第四步：编写工具处理器

创建 `tools.py` — 这是 LLM 调用你的工具时实际执行的代码：

```python
"""工具处理器 — LLM 调用每个工具时运行的代码。"""

import json
import math

# 用于表达式求值的安全全局变量 — 没有文件/网络访问权限
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
    3. 返回 JSON 字符串 — 即使出错也始终返回
    4. 接受 **kwargs 以保持向前兼容
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
    # 归一化为摄氏度
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # 转换为目标单位
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """在单位之间进行转换。"""
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
2. **返回值：** 始终返回 JSON 字符串，成功和错误都如此。
3. **绝不抛出异常：** 捕获所有异常，改为返回错误 JSON。
4. **接受 `**kwargs`：** Hermes 未来可能会传递额外的上下文。

<a id="step-5-write-the-registration"></a>
## 第 5 步：编写注册逻辑

创建 `__init__.py` — 它将 schema 与处理器连接起来：

```python
"""计算器插件 — 注册。"""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# 通过钩子跟踪工具使用情况
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """钩子：每次工具调用后执行（不仅限于我们的工具）。"""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("工具已调用：%s（会话 %s）", tool_name, task_id)


def register(ctx):
    """将 schema 与处理器连接并注册钩子。"""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # 此钩子会为所有工具调用触发，不仅限于我们的
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的作用：**
- 在启动时仅调用一次
- `ctx.register_tool()` 将你的工具放入注册表 — 模型会立即看到它
- `ctx.register_hook()` 订阅生命周期事件
- `ctx.register_cli_command()` 注册一个 CLI 子命令（例如 `hermes my-plugin &lt;subcommand&gt;`）
- `ctx.register_command()` 注册一个会话内的斜杠命令（例如在 CLI/网关聊天中的 `/myplugin &lt;args&gt;`）— 请参阅下面的[注册斜杠命令](#register-slash-commands)
- `ctx.dispatch_tool(name, arguments)` — 调用任何其他工具（内置的或来自其他插件的），并自动连接父 Agent 的上下文（审批、凭据、task_id）。对于需要调用 `terminal`、`read_file` 或任何其他工具（就像模型直接调用它们一样）的斜杠命令处理器非常有用。
- 如果此函数崩溃，插件会被禁用，但 Hermes 会继续正常运行

**`dispatch_tool` 示例 — 一个运行工具的斜杠命令：**

```python
def handle_scan(ctx, argstr):
    """通过注册表调用 terminal 工具来实现 /scan。"""
    result = ctx.dispatch_tool("terminal", {"command": f"find . -name '{argstr}'"})
    return result  # 返回给调用者的聊天界面

def register(ctx):
    ctx.register_command("scan", handle_scan, help="查找匹配 glob 模式的文件")
```

被分发的工具会经过正常的审批、编辑和预算流程 — 这是一个真实的工具调用，而不是绕过它们的捷径。

<a id="step-6-test-it"></a>
## 第 6 步：测试

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
插件 (1):
  ✓ calculator v1.0.0 (2 个工具，1 个钩子)
```

<a id="debugging-plugin-discovery"></a>
### 调试插件发现

如果你的插件没有出现——或者出现了但无法加载——设置 `HERMES_PLUGINS_DEBUG=1` 来在 stderr 上输出详细的发现日志：

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```

你将看到，对于每个插件源（bundled、user、project、entry-points）：

- 扫描了哪些目录，每个目录产生了多少个清单
- 每个清单：解析的键、名称、类型、来源、磁盘路径
- 跳过原因：`disabled via config`、`not enabled in config`、`exclusive plugin`、`no plugin.yaml, depth cap reached`
- 加载时：正在导入的插件，以及 `register(ctx)` 注册的内容的摘要（工具、钩子、斜杠命令、CLI 命令）
- 解析失败时：异常的完整回溯（YAML 扫描器错误等）
- `register()` 失败时：指向你的 `__init__.py` 中抛出异常的行的完整回溯

当设置了环境变量时，同样的日志总是以 WARNING 级别（仅失败）和 DEBUG 级别（全部）写入 `~/.hermes/logs/agent.log`。因此，如果你无法在环境变量下运行（例如在网关内部），可以改为 tail 日志文件：

```bash
hermes logs --level WARNING | grep -i plugin
```

插件不出现的常见原因：

- **未在配置中启用** —— 插件是选择加入的。运行 `hermes plugins enable &lt;name&gt;`（名称来自 `plugins list` 的输出，对于嵌套布局，可以是 `&lt;category&gt;/&lt;plugin&gt;`）。
- **目录布局错误** —— 必须为 `~/.hermes/plugins/&lt;plugin-name&gt;/plugin.yaml`（扁平）或 `~/.hermes/plugins/&lt;category&gt;/&lt;plugin-name&gt;/plugin.yaml`（最多一层类别嵌套）。更深的目录会被忽略。
- **缺少 `__init__.py`** —— 插件目录需要同时包含 `plugin.yaml` 和带有 `register(ctx)` 函数的 `__init__.py`。
- **`kind` 错误** —— 网关适配器需要在清单中设置 `kind: platform`。内存提供者会被自动检测为 `kind: exclusive`，并通过 `memory.provider` 配置路由，而不是 `plugins.enabled`。

<a id="your-plugin-s-final-structure"></a>
## 你插件的最终结构

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # “我是计算器，我提供工具和钩子”
├── __init__.py      # 接线：模式 → 处理程序，注册钩子
├── schemas.py       # LLM 读取的内容（描述 + 参数规范）
└── tools.py         # 实际运行的内容（计算、单位转换函数）
```

四个文件，清晰分离：
- **清单** 声明了插件是什么
- **模式** 描述了 LLM 使用的工具
- **处理程序** 实现了实际逻辑
- **注册** 连接一切

<a id="what-else-can-plugins-do"></a>
## 插件还能做什么？

<a id="ship-data-files"></a>
### 携带数据文件

将任何文件放入你的插件目录，并在导入时读取：

```python
# In tools.py or __init__.py
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

<a id="bundle-skills"></a>
### 打包技能

插件可以附带技能文件，Agent 通过 `skill_view("plugin:skill")` 加载这些文件。在你的 `__init__.py` 中注册它们：
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

Agent 现在可以用带命名空间的名称加载你的 skill：

```python
skill_view("my-plugin:my-workflow")   # → plugin's version
skill_view("my-workflow")              # → built-in version (unchanged)
```

**关键特性：**
- 插件 skill 是**只读**的——它们不会进入 `~/.hermes/skills/`，也不能通过 `skill_manage` 编辑。
- 插件 skill **不会**出现在系统提示的 `&lt;available_skills&gt;` 索引中——它们是按需显式加载的。
- 裸 skill 名称不受影响——命名空间可以防止与内置 skill 冲突。
- 当 Agent 加载一个插件 skill 时，会前置一个捆绑上下文横幅，列出同一插件的同级 skill。

:::tip 旧版模式
旧的 `shutil.copy2` 模式（将 skill 复制到 `~/.hermes/skills/`）仍然有效，但会与内置 skill 产生名称冲突的风险。新插件请优先使用 `ctx.register_skill()`。
<a id="legacy-pattern"></a>
:::

<a id="gate-on-environment-variables"></a>
### 基于环境变量的开关控制

如果你的插件需要 API 密钥：

```yaml
# plugin.yaml — simple format (backwards-compatible)
requires_env:
  - WEATHER_API_KEY
```

如果 `WEATHER_API_KEY` 未设置，插件会被禁用并显示清晰的消息。不会崩溃，Agent 也不会报错——只会显示“Plugin weather disabled (missing: WEATHER_API_KEY)”。

当用户运行 `hermes plugins install` 时，系统会**交互式提示**任何缺失的 `requires_env` 变量。值会自动保存到 `.env` 文件。

为了更好的安装体验，请使用带有描述和注册 URL 的丰富格式：

```yaml
# plugin.yaml — rich format
requires_env:
  - name: WEATHER_API_KEY
    description: "API key for OpenWeather"
    url: "https://openweathermap.org/api"
    secret: true
```

| 字段 | 是否必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 环境变量名称 |
| `description` | 否 | 在安装提示时显示给用户 |
| `url` | 否 | 获取凭据的地址 |
| `secret` | 否 | 如果为 `true`，输入会被隐藏（类似密码字段） |

两种格式可以在同一个列表中混用。已设置的变量会被静默跳过。

<a id="lazy-install-optional-python-dependencies"></a>
### 延迟安装可选的 Python 依赖

如果你的插件封装了一个并非每个用户都会安装的 SDK（比如供应商 SDK、庞大的 ML 库、平台特定包），请不要在模块顶部 `import` 它。请在工具处理函数内部使用 `tools.lazy_deps.ensure(...)` 辅助函数——Hermes 会在首次使用时安装该包，并由用户的 `security.allow_lazy_installs` 配置控制。

```python
# tools.py
from tools.lazy_deps import ensure, FeatureUnavailable

def my_tool_handler(args, **kwargs):
    try:
        ensure("my-plugin.my-backend")   # key must be in LAZY_DEPS
    except FeatureUnavailable as exc:
        return {"error": str(exc)}

    import my_backend_sdk   # safe now
    ...
```
来自 `tools/lazy_deps.py` 安全模型的两条规则：

| 规则 | 原因 |
|---|---|
| 你的功能键必须出现在树内的 `LAZY_DEPS` 允许列表中 | 防止恶意配置诱使 Hermes 安装任意包——只有 Hermes 自身附带的规范才符合条件 |
| 规范仅限 PyPI 包名 | 不允许使用 `--index-url`、`git+https://` 或 `file:` 路径。在允许列表条目内使用 PEP 440（如 `"my-sdk>=1.2,<2"`）锁定版本 |

对于通过 pip 分发的第三方插件，请在自己的 `pyproject.toml` 中将可选依赖声明为 `[project.optional-dependencies]` 附加项，并告知用户 `pip install your-plugin[backend]`——这条路径不经过 `lazy_deps`。懒安装机制对**捆绑**插件最有用，因为如果每次安装都附带硬依赖，会膨胀 Hermes 的基础体积。

当全局设置了 `security.allow_lazy_installs: false` 时，`ensure()` 会立即抛出 `FeatureUnavailable` 并附带修复提示——你的插件应捕获该异常并优雅降级（返回错误结果，而不是让工具循环崩溃）。

<a id="conditional-tool-availability"></a>
### 条件性工具可用性

对于依赖可选库的工具：

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # False = 对模型隐藏该工具
)
```

<a id="overriding-a-built-in-tool"></a>
### 覆盖内置工具

要用你自己的实现替换内置工具（例如将默认浏览器工具替换为有头 Chrome CDP 后端，或将 `web_search` 替换为自定义企业索引），请传入 `override=True`：

```python
def register(ctx):
    ctx.register_tool(
        name="browser_navigate",             # 与内置工具同名
        toolset="plugin_my_browser",         # 你自己的工具集命名空间
        schema={...},
        handler=my_custom_navigate,
        override=True,                       # 显式选择启用
    )
```

如果没有 `override=True`，注册器会拒绝任何会覆盖其他工具集中已有工具的注册——这可以防止意外覆盖。覆盖操作会以 INFO 级别记录日志，因此可在 `~/.hermes/logs/agent.log` 中审计。插件在内置工具之后加载，因此注册顺序是正确的：你的处理器会替换内置的处理器。

<a id="register-multiple-hooks"></a>
### 注册多个钩子

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("pre_llm_call", inject_memory)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

<a id="hook-reference"></a>
### 钩子参考

每个钩子的完整文档请参阅 **[事件钩子参考](/user-guide/features/hooks#plugin-hooks)**——包括回调签名、参数表、触发时机和示例。以下是摘要：

| 钩子 | 触发时机 | 回调签名 | 返回值 |
|------|---------|---------|--------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 任何工具执行前 | `tool_name: str, args: dict, task_id: str` | 忽略 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 任何工具返回后 | `tool_name: str, args: dict, result: str, task_id: str, duration_ms: int` | 忽略 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮一次，在工具调用循环之前 | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [上下文注入](#pre_llm_call-context-injection) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮一次，在工具调用循环之后（仅成功轮次） | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | 忽略 |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 新会话创建时（仅第一轮） | `session_id: str, model: str, platform: str` | 忽略 |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次 `run_conversation` 调用结束时 + CLI 退出时 | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | 忽略 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/网关销毁活跃会话时 | `session_id: str \| None, platform: str` | 忽略 |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | 网关切换新会话键时（`/new`、`/reset`） | `session_id: str, platform: str` | 忽略 |
大多数钩子都是即发即忘的观察者——它们的返回值被忽略。唯一的例外是 `pre_llm_call`，它可以向对话注入上下文。

所有回调函数都应接受 `**kwargs` 以保证向前兼容。如果某个钩子回调崩溃，它会被记录并跳过，其他钩子和 Agent 继续正常运行。

<a id="prellmcall-context-injection"></a>
### `pre_llm_call` 上下文注入 {#pre_llm_call-context-injection}

这是唯一一个返回值有意义的钩子。当 `pre_llm_call` 回调返回一个包含 `"context"` 键的字典（或纯字符串）时，Hermes 会将那段文本注入到**当前轮次的用户消息**中。这是记忆插件、RAG 集成、安全护栏以及任何需要为模型提供额外上下文的插件所依赖的机制。

<a id="return-format"></a>
#### 返回格式

```python
# Dict with context key
return {"context": "Recalled memories:\n- User prefers dark mode\n- Last project: hermes-agent"}

# Plain string (equivalent to the dict form above)
return "Recalled memories:\n- User prefers dark mode"

# Return None or don't return → no injection (observer-only)
return None
```

任何非 `None`、非空且带有 `"context"` 键的返回值（或非空纯字符串）都会被收集并追加到当前轮次的用户消息中。

<a id="how-injection-works"></a>
#### 注入机制

被注入的上下文会追加到**用户消息**中，而不是系统提示语。这是经过深思熟虑的设计选择：

- **提示缓存保持**——系统提示语在各轮次之间保持不变。Anthropic 和 OpenRouter 会缓存系统提示语前缀，因此保持其稳定可以在多轮对话中节省 75% 以上的输入 token。如果插件修改了系统提示语，每一轮都会导致缓存未命中。
- **临时性**——注入仅在 API 调用时发生。对话历史中的原始用户消息永远不会被修改，也不会持久化到会话数据库。
- **系统提示语是 Hermes 的领地**——它包含模型特定的指导、工具执行规则、个性指令以及缓存的技能内容。插件贡献的上下文与用户输入并列，而不是通过修改 Agent 的核心指令来实现。

<a id="example-memory-recall-plugin"></a>
#### 示例：记忆召回插件

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

<a id="example-guardrails-plugin"></a>
#### 示例：护栏插件
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

<a id="example-observer-only-hook-no-injection"></a>
#### 示例：仅观察的 Hook（不注入内容）

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

<a id="multiple-plugins-returning-context"></a>
#### 多个插件返回上下文（context）

当多个插件从 `pre_llm_call` 返回上下文时，它们的输出会用双换行符连接，并一起追加到用户消息中。顺序遵循插件发现顺序（按插件目录名称的字母顺序）。

<a id="register-cli-commands"></a>
### 注册 CLI 命令

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

注册后，用户可以运行 `hermes my-plugin status`、`hermes my-plugin config` 等命令。

**内存提供者插件** 则采用基于约定的方式：在插件的 `cli.py` 文件中添加一个 `register_cli(subparser)` 函数。内存插件发现系统会自动找到它——无需调用 `ctx.register_cli_command()`。详情请参阅 [Memory Provider Plugin guide](/developer-guide/memory-provider-plugin#adding-cli-commands)。

**活动提供者筛选：** 内存插件的 CLI 命令仅在其提供者被配置为活跃的 `memory.provider` 时才会出现。如果用户尚未设置你的提供者，你的 CLI 命令不会在帮助输出中造成杂乱。

<a id="register-slash-commands"></a>
### 注册斜杠命令

插件可以注册会话内斜杠命令——用户在对话过程中输入的命令（如 `/lcm status` 或 `/ping`）。这些命令在 CLI 和网关（Telegram、Discord 等）中均可使用。
```python
def _handle_status(raw_args: str) -> str:
    """处理 /mystatus 的处理器——接收命令名之后的所有内容。"""
    if raw_args.strip() == "help":
        return "用法: /mystatus [help|check]"
    return "插件状态: 所有系统正常"

def register(ctx):
    ctx.register_command(
        "mystatus",
        handler=_handle_status,
        description="显示插件状态",
    )
```

注册后，用户可以在任何会话中键入 `/mystatus`。该命令会出现在自动补全、`/help` 输出以及 Telegram 机器人菜单中。

**签名：** `ctx.register_command(name: str, handler: Callable, description: str = "")`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | `str` | 命令名称，不含前导斜杠（例如 `"lcm"`、`"mystatus"`） |
| `handler` | `Callable[[str], str \| None]` | 使用原始参数字符串调用。也可以是 `async` 异步函数。 |
| `description` | `str` | 显示在 `/help`、自动补全和 Telegram 机器人菜单中 |

**与 `register_cli_command()` 的关键区别：**

| | `register_command()` | `register_cli_command()` |
|---|---|---|
| 调用方式 | 在会话中键入 `/name` | 在终端中键入 `hermes name` |
| 生效环境 | CLI 会话、Telegram、Discord 等 | 仅终端 |
| 处理器接收 | 原始参数字符串 | argparse `Namespace` |
| 使用场景 | 诊断、状态、快速操作 | 复杂子命令树、设置向导 |

**冲突保护：** 如果某个插件试图注册与内置命令（`help`、`model`、`new` 等）冲突的名称，注册会被静默拒绝并记录日志警告。内置命令始终优先。

**异步处理器：** 网关调度会自动检测并等待异步处理器，因此你可以使用同步或异步函数：

```python
async def _handle_check(raw_args: str) -> str:
    result = await some_async_operation()
    return f"检查结果: {result}"

def register(ctx):
    ctx.register_command("check", handler=_handle_check, description="运行异步检查")
```

<a id="dispatch-tools-from-slash-commands"></a>
### 从斜杠命令调度工具

需要编排工具（通过 `delegate_task` 生成子 Agent、调用 `file_edit` 等）的斜杠命令处理器应使用 `ctx.dispatch_tool()`，而不要直接访问框架内部。父 Agent 上下文（工作空间提示、spinner、模型继承）会自动连接。

```python
def register(ctx):
    def _handle_deliver(raw_args: str):
        result = ctx.dispatch_tool(
            "delegate_task",
            {
                "goal": raw_args,
                "toolsets": ["terminal", "file", "web"],
            },
        )
        return result

    ctx.register_command(
        "deliver",
        handler=_handle_deliver,
        description="将目标委托给子 Agent",
    )
```

**签名：** `ctx.dispatch_tool(name: str, args: dict, *, parent_agent=None) -> str`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | `str` | 工具注册表中的工具名称（例如 `"delegate_task"`、`"file_edit"`） |
| `args` | `dict` | 工具参数，与模型发送的格式相同 |
| `parent_agent` | `Agent \| None` | 可选覆盖。省略时，从当前 CLI Agent 解析（在网关模式下会优雅降级） |
**运行时行为：**

- **CLI 模式：** `parent_agent` 从当前活跃的 CLI Agent 中解析，因此工作区提示、加载动画和模型选择会按预期继承。
- **网关模式：** 没有 CLI Agent，因此工具会优雅降级——工作区从 `TERMINAL_CWD` 读取，且不显示加载动画。
- **显式覆盖：** 如果调用方显式传递了 `parent_agent=`，该值会被尊重且不会被覆盖。

这是从插件命令进行工具调度的公开、稳定接口。插件不应访问 `ctx._cli_ref.agent` 或类似的私有状态。

:::tip
本指南涵盖**通用插件**（工具、钩子、斜杠命令、CLI 命令）。以下各节简要介绍了每种专用插件类型的编写模式；每节都链接到其完整指南，供字段参考和示例使用。
:::

<a id="specialized-plugin-types"></a>
## 专用插件类型

除了通用接口外，Hermes 还有五种专用插件类型。每种类型都作为目录放在 `plugins/&lt;category&gt;/&lt;name&gt;/`（内置）或 `~/.hermes/plugins/&lt;category&gt;/&lt;name&gt;/`（用户）下。不同类别的约定不同——选择你需要的类型，然后阅读其完整指南。

<a id="model-provider-plugins-add-an-llm-backend"></a>
### 模型提供商插件——添加 LLM 后端

将配置文件放入 `plugins/model-providers/&lt;name&gt;/`：

```python
# plugins/model-providers/acme/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="acme",
    aliases=("acme-inference",),
    display_name="Acme Inference",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=("acme-large-v3", "acme-medium-v3"),
))
```

```yaml
# plugins/model-providers/acme/plugin.yaml
name: acme-provider
kind: model-provider
version: 1.0.0
description: Acme Inference — OpenAI-compatible direct API
```

在首次调用 `get_provider_profile()` 或 `list_providers()` 时延迟发现——`auth.py`、`config.py`、`doctor.py`、`models.py`、`runtime_provider.py` 以及 chat_completions 传输层会自动连接到它。用户插件会按名称覆盖内置插件。

**完整指南：** [模型提供商插件](/developer-guide/model-provider-plugin) — 字段参考、可覆盖的钩子（`prepare_messages`、`build_extra_body`、`build_api_kwargs_extras`、`fetch_models`）、api_mode 选择、认证类型、测试。

<a id="platform-plugins-add-a-gateway-channel"></a>
### 平台插件——添加网关通道

将适配器放入 `plugins/platforms/&lt;name&gt;/`：

```python
# plugins/platforms/myplatform/adapter.py
from gateway.platforms.base import BasePlatformAdapter

class MyPlatformAdapter(BasePlatformAdapter):
    async def connect(self): ...
    async def send(self, chat_id, text): ...
    async def disconnect(self): ...

def check_requirements():
    import os
    return bool(os.environ.get("MYPLATFORM_TOKEN"))

def _env_enablement():
    import os
    tok = os.getenv("MYPLATFORM_TOKEN", "").strip()
    if not tok:
        return None
    return {"token": tok}

def register(ctx):
    ctx.register_platform(
        name="myplatform",
        label="MyPlatform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        required_env=["MYPLATFORM_TOKEN"],
        # 从环境变量自动填充 PlatformConfig.extra，这样仅通过环境变量配置的设置
        # 无需实例化 SDK 即可在 `hermes gateway status` 中显示。
        env_enablement_fn=_env_enablement,
        # 选择加入 cron 投递：`deliver=myplatform` 路由到此变量。
        cron_deliver_env_var="MYPLATFORM_HOME_CHANNEL",
        emoji="💬",
        platform_hint="You are chatting via MyPlatform. Keep responses concise.",
    )
```
```yaml
# plugins/platforms/myplatform/plugin.yaml
name: myplatform-platform
label: MyPlatform
kind: platform
version: 1.0.0
description: MyPlatform 网关适配器
requires_env:
  - name: MYPLATFORM_TOKEN
    description: "来自 MyPlatform 控制台的机器人令牌"
    password: true
optional_env:
  - name: MYPLATFORM_HOME_CHANNEL
    description: "Cron 投递的默认频道"
    password: false
```

**完整指南：** [添加平台适配器](/developer-guide/adding-platform-adapters) — 完整的 `BasePlatformAdapter` 契约、消息路由、认证门控、设置向导集成。可参考 `plugins/platforms/irc/` 获取仅使用标准库的工作示例。

<a id="memory-provider-plugins-add-a-cross-session-knowledge-backend"></a>
### 记忆提供者（Memory Provider）插件 — 添加跨会话知识后端

将 `MemoryProvider` 的实现放入 `plugins/memory/&lt;name&gt;/`：

```python
# plugins/memory/my-memory/__init__.py
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-memory"

    def is_available(self) -> bool:
        import os
        return bool(os.environ.get("MY_MEMORY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        self._session_id = session_id

    def sync_turn(self, user_message, assistant_response, **kwargs) -> None:
        ...

    def prefetch(self, query: str, **kwargs) -> str | None:
        ...

def register(ctx):
    ctx.register_memory_provider(MyMemoryProvider())
```

记忆提供者是单选模式 —— 一次只激活一个，通过 `config.yaml` 中的 `memory.provider` 选择。

**完整指南：** [记忆提供者插件](/developer-guide/memory-provider-plugin) — 完整的 `MemoryProvider` 抽象基类、线程契约、配置文件隔离、通过 `cli.py` 注册 CLI 命令。

<a id="context-engine-plugins-replace-the-context-compressor"></a>
### 上下文引擎插件 — 替换上下文压缩器

```python
# plugins/context_engine/my-engine/__init__.py
from agent.context_engine import ContextEngine

class MyContextEngine(ContextEngine):
    @property
    def name(self) -> str:
        return "my-engine"

    def should_compress(self, messages, model) -> bool: ...
    def compress(self, messages, model) -> list[dict]: ...

def register(ctx):
    ctx.register_context_engine(MyContextEngine())
```

上下文引擎是单选模式 —— 通过 `config.yaml` 中的 `context.engine` 选择。

**完整指南：** [上下文引擎插件](/developer-guide/context-engine-plugin)。

<a id="image-generation-backends"></a>
### 图像生成后端

将提供者放入 `plugins/image_gen/&lt;name&gt;/`：

```python
# plugins/image_gen/my-imggen/__init__.py
from agent.image_gen_provider import ImageGenProvider

class MyImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        return "my-imggen"

    def is_available(self) -> bool: ...
    def generate(self, prompt: str, **kwargs) -> str: ...   # returns image path

def register(ctx):
    ctx.register_image_gen_provider(MyImageGenProvider())
```

```yaml
# plugins/image_gen/my-imggen/plugin.yaml
name: my-imggen
kind: backend
version: 1.0.0
description: 自定义图像生成后端
```
**完整指南：** [图像生成提供者插件](/developer-guide/image-gen-provider-plugin) — 完整的 `ImageGenProvider` 抽象基类、`list_models()` / `get_setup_schema()` 元数据、`success_response()`/`error_response()` 辅助函数、base64 与 URL 输出、用户覆盖、pip 分发。

**参考示例：** `plugins/image_gen/openai/`（通过 OpenAI SDK 的 DALL-E / GPT-Image）、`plugins/image_gen/openai-codex/`、`plugins/image_gen/xai/`（Grok 图像生成）。

<a id="non-python-extension-surfaces"></a>
## 非 Python 扩展面

Hermes 也接受完全不是 Python 插件的扩展。这些在[可插拔接口表](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each)中展示；以下各节简要概述了每种编写风格。

<a id="mcp-servers-register-external-tools"></a>
### MCP 服务器 — 注册外部工具

模型上下文协议（MCP）服务器无需任何 Python 插件即可将其自己的工具注册到 Hermes。在 `~/.hermes/config.yaml` 中声明它们：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    timeout: 120

  linear:
    url: "https://mcp.linear.app/sse"
    auth:
      type: "oauth"
```

Hermes 在启动时连接到每个服务器，列出其工具，并将它们与内置工具一起注册。LLM 看到它们就像看到任何其他工具一样。**完整指南：** [MCP](/user-guide/features/mcp)。

<a id="gateway-event-hooks-fire-on-lifecycle-events"></a>
### 网关事件钩子 — 在生命周期事件上触发

将清单 + 处理程序放入 `~/.hermes/hooks/&lt;name&gt;/`：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: 当长时间任务完成时发送推送通知
events:
  - agent:end
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
async def handle(event_type: str, context: dict) -> None:
    if context.get("duration_seconds", 0) > 120:
        # 发送通知 …
        pass
```

事件包括 `gateway:startup`、`session:start`、`session:end`、`session:reset`、`agent:start`、`agent:step`、`agent:end` 以及通配符 `command:*`。钩子中的错误会被捕获并记录 — 它们永远不会阻塞主流水线。

**完整指南：** [网关事件钩子](/user-guide/features/hooks#gateway-event-hooks)。

<a id="shell-hooks-run-a-shell-command-on-tool-calls"></a>
### Shell 钩子 — 在工具调用时运行 shell 命令

如果你只想在工具触发时运行一个脚本（通知、审计日志、桌面提醒、自动格式化器），请在 `config.yaml` 中使用 shell 钩子 — 无需 Python：

```yaml
hooks:
  - event: post_tool_call
    command: "notify-send '工具已运行：{tool_name}'"
    when:
      tools: [terminal, patch, write_file]
```

支持与 Python 插件钩子相同的所有事件（`pre_tool_call`、`post_tool_call`、`pre_llm_call`、`post_llm_call`、`on_session_start`、`on_session_end`、`pre_gateway_dispatch`），以及用于 `pre_tool_call` 阻塞决策的结构化 JSON 输出。

**完整指南：** [Shell 钩子](/user-guide/features/hooks#shell-hooks)。

<a id="skill-sources-add-a-custom-skill-registry"></a>
### 技能源 — 添加自定义技能注册表

如果你维护一个技能的 GitHub 仓库（或者想从内置源之外的社区索引中拉取），将其添加为一个 **tap**：
```bash
hermes skills tap add myorg/skills-repo
hermes skills search my-workflow --source myorg/skills-repo
hermes skills install myorg/skills-repo/my-workflow
```

发布自己的 tap 只需一个包含 `skills/&lt;skill-name&gt;/SKILL.md` 目录的 GitHub 仓库——无需服务器或注册中心。

**完整指南：** [技能中心](/user-guide/features/skills#skills-hub) · [发布自定义 tap](/user-guide/features/skills#publishing-a-custom-skill-tap)（仓库布局、最小示例、非默认路径、信任级别）。

<a id="tts-stt-via-command-templates"></a>
### 通过命令模板实现 TTS / STT

任何可读写音频或文本的 CLI 都可以通过 `config.yaml` 接入——无需 Python 代码：

```yaml
tts:
  provider: voxcpm
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      voice_compatible: true
```

对于 STT，将 `HERMES_LOCAL_STT_COMMAND` 指向一个 shell 模板。支持的占位符：`{input_path}`、`{output_path}`、`{format}`、`{voice}`、`{model}`、`{speed}`（TTS）；`{input_path}`、`{output_dir}`、`{language}`、`{model}`（STT）。任何与路径交互的 CLI 都会自动成为一个插件。

**完整指南：** [TTS 自定义命令提供者](/user-guide/features/tts#custom-command-providers) · [STT](/user-guide/features/tts#voice-message-transcription-stt)。

<a id="distribute-via-pip"></a>
## 通过 pip 分发

要公开发布插件，请在 Python 包中添加一个 entry point：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# 下次启动 hermes 时会自动发现插件
```

<a id="distribute-for-nixos"></a>
## 为 NixOS 分发

如果你提供一个包含 entry points 的 `pyproject.toml`，NixOS 用户可以声明式地安装你的插件：

**Entry-point 插件（推荐分发方式）：**
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

**目录插件（无需 `pyproject.toml`）：**
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

有关 overlay 用法和冲突检查的完整文档，请参阅 [Nix 安装指南](/getting-started/nix-setup#plugins)。

<a id="common-mistakes"></a>
## 常见错误

**Handler 没有返回 JSON 字符串：**
```python
# 错误 —— 返回了一个字典
def handler(args, **kwargs):
    return {"result": 42}

# 正确 —— 返回一个 JSON 字符串
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**Handler 签名中缺少 `**kwargs`：**
```python
# 错误 —— 如果 Hermes 传递额外上下文会出错
def handler(args):
    ...

# 正确
def handler(args, **kwargs):
    ...
```
**处理器抛出异常：**
```python
# 错误 — 异常会向上传播，工具调用失败
def handler(args, **kwargs):
    result = 1 / int(args["value"])  # ZeroDivisionError！
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
# 不好 — 模型不知道何时使用该工具
"description": "做某些事"

# 好 — 模型明确知道何时以及如何使用
"description": "计算数学表达式。用于算术、三角函数、对数运算。支持：+, -, *, /, **, sqrt, sin, cos, log, pi, e。"
```
