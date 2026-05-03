---
sidebar_position: 2
title: "添加工具"
description: "如何向 Hermes Agent 添加新工具——模式、处理器、注册与工具集"
---

# 添加工具 {#adding-tools}

在编写工具之前，先问自己：**这个功能是否应该做成 [技能](creating-skills.md)？**

如果能力可以通过指令 + shell 命令 + 现有工具（arXiv 搜索、git 工作流、Docker 管理、PDF 处理）来表达，就做成**技能**。

如果它需要与 API 密钥进行端到端集成、自定义处理逻辑、二进制数据处理或流式传输（浏览器自动化、TTS、视觉分析），就做成**工具**。

## 概述 {#overview}

添加一个工具涉及 **2 个文件**：

1. **`tools/your_tool.py`** — 处理器、模式、检查函数、`registry.register()` 调用
2. **`toolsets.py`** — 将工具名称添加到 `_HERMES_CORE_TOOLS`（或特定的工具集）

任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会在启动时自动发现——无需手动导入列表。

## 第一步：创建工具文件 {#step-1-create-the-tool-file}

每个工具文件都遵循相同的结构：

```python
# tools/weather_tool.py
"""天气工具——查询某个地点的当前天气。"""

import json
import os
import logging

logger = logging.getLogger(__name__)


# --- 可用性检查 ---

def check_weather_requirements() -> bool:
    """如果工具的依赖项可用，返回 True。"""
    return bool(os.getenv("WEATHER_API_KEY"))


# --- 处理器 ---

def weather_tool(location: str, units: str = "metric") -> str:
    """获取某个地点的天气。返回 JSON 字符串。"""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "WEATHER_API_KEY 未配置"})
    try:
        # ... 调用天气 API ...
        return json.dumps({"location": location, "temp": 22, "units": units})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- 模式 ---

WEATHER_SCHEMA = {
    "name": "weather",
    "description": "获取某个地点的当前天气。",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "城市名称或坐标（例如 'London' 或 '51.5,-0.1'）"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "温度单位（默认：metric）",
                "default": "metric"
            }
        },
        "required": ["location"]
    }
}


# --- 注册 ---

from tools.registry import registry

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool(
        location=args.get("location", ""),
        units=args.get("units", "metric")),
    check_fn=check_weather_requirements,
    requires_env=["WEATHER_API_KEY"],
)
```

### 关键规则 {#key-rules}

<a id="important"></a>
:::danger 重要
- 处理器**必须**返回 JSON 字符串（通过 `json.dumps()`），绝不能返回原始字典
- 错误**必须**以 `{"error": "message"}` 的形式返回，绝不能作为异常抛出
- `check_fn` 在构建工具定义时被调用——如果返回 `False`，该工具会被静默排除
- `handler` 接收 `(args: dict, **kwargs)`，其中 `args` 是 LLM 的工具调用参数
:::
## 第二步：添加到工具集 {#step-2-add-to-a-toolset}

在 `toolsets.py` 中添加工具名称：

```python
# 如果该工具应在所有平台（CLI + 消息）上可用：
_HERMES_CORE_TOOLS = [
    ...
    "weather",  # <-- 在这里添加
]

# 或者创建一个新的独立工具集：
"weather": {
    "description": "天气查询工具",
    "tools": ["weather"],
    "includes": []
},
```

## ~~第三步：添加发现导入~~（不再需要） {#step-3-add-discovery-import-no-longer-needed}

带有顶层 `registry.register()` 调用的工具模块会被 `tools/registry.py` 中的 `discover_builtin_tools()` 自动发现。无需手动维护导入列表——只需在 `tools/` 中创建文件，启动时就会自动加载。

## 异步处理器 {#async-handlers}

如果你的处理器需要异步代码，请使用 `is_async=True` 标记：

```python
async def weather_tool_async(location: str) -> str:
    async with aiohttp.ClientSession() as session:
        ...
    return json.dumps(result)

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool_async(args.get("location", "")),
    check_fn=check_weather_requirements,
    is_async=True,  # registry 会自动调用 _run_async()
)
```

注册表会透明地处理异步桥接——你永远不需要自己调用 `asyncio.run()`。

## 需要 task_id 的处理器 {#handlers-that-need-taskid}

管理会话状态的工具通过 `**kwargs` 接收 `task_id`：

```python
def _handle_weather(args, **kw):
    task_id = kw.get("task_id")
    return weather_tool(args.get("location", ""), task_id=task_id)

registry.register(
    name="weather",
    ...
    handler=_handle_weather,
)
```

## Agent 循环拦截工具 {#agent-loop-intercepted-tools}

某些工具（`todo`、`memory`、`session_search`、`delegate_task`）需要访问会话级别的 Agent 状态。这些工具在到达注册表之前会被 `run_agent.py` 拦截。注册表仍然保存它们的模式，但如果拦截被绕过，`dispatch()` 会返回一个回退错误。

## 可选：设置向导集成 {#optional-setup-wizard-integration}

如果你的工具需要 API 密钥，请将其添加到 `hermes_cli/config.py`：

```python
OPTIONAL_ENV_VARS = {
    ...
    "WEATHER_API_KEY": {
        "description": "用于天气查询的 Weather API 密钥",
        "prompt": "Weather API 密钥",
        "url": "https://weatherapi.com/",
        "tools": ["weather"],
        "password": True,
    },
}
```

## 检查清单 {#checklist}

- [ ] 创建了包含处理器、模式、检查函数和注册信息的工具文件
- [ ] 已添加到 `toolsets.py` 中的相应工具集
- [ ] 处理器返回 JSON 字符串，错误以 `{"error": "..."}` 形式返回
- [ ] 可选：API 密钥已添加到 `hermes_cli/config.py` 的 `OPTIONAL_ENV_VARS` 中
- [ ] 可选：已添加到 `toolset_distributions.py` 以支持批量处理
- [ ] 已使用 `hermes chat -q "Use the weather tool for London"` 进行测试
