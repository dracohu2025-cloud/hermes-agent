---
sidebar_position: 2
title: "Adding Tools"
description: "如何为 Hermes Agent 添加新工具 —— 模式定义、处理器、注册与工具集"
---

# 添加工具 {#adding-tools}

在动手写工具之前，先问自己一句：**这个功能是不是更适合做成一个 [skill](creating-skills.md)？**

如果某项能力可以用指令 + shell 命令 + 现有工具来表达（比如 arXiv 搜索、git 工作流、Docker 管理、PDF 处理），那就做成 **Skill**。

如果需要端到端集成 API key、自定义处理逻辑、二进制数据处理或流式传输（比如浏览器自动化、TTS、视觉分析），那就做成 **Tool**。

## 概览 {#overview}

添加一个工具只需要改动 **2 个文件**：

1. **`tools/your_tool.py`** —— 处理器、模式定义、检查函数、`registry.register()` 调用
2. **`toolsets.py`** —— 把工具名加到 `_HERMES_CORE_TOOLS`（或某个特定工具集）

任何带有顶层 `registry.register()` 调用的 `tools/*.py` 文件都会在启动时自动发现——不需要手动维护导入列表。

## 步骤 1：创建工具文件 {#step-1-create-the-tool-file}

每个工具文件都遵循相同的结构：

```python
# tools/weather_tool.py
"""Weather Tool -- look up current weather for a location."""

import json
import os
import logging

logger = logging.getLogger(__name__)


# --- Availability check ---

def check_weather_requirements() -> bool:
    """Return True if the tool's dependencies are available."""
    return bool(os.getenv("WEATHER_API_KEY"))


# --- Handler ---

def weather_tool(location: str, units: str = "metric") -> str:
    """Fetch weather for a location. Returns JSON string."""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "WEATHER_API_KEY not configured"})
    try:
        # ... call weather API ...
        return json.dumps({"location": location, "temp": 22, "units": units})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Schema ---

WEATHER_SCHEMA = {
    "name": "weather",
    "description": "Get current weather for a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or coordinates (e.g. 'London' or '51.5,-0.1')"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "Temperature units (default: metric)",
                "default": "metric"
            }
        },
        "required": ["location"]
    }
}


# --- Registration ---

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

:::danger Important
- 处理器 **必须** 返回 JSON 字符串（通过 `json.dumps()`），绝不能返回原始 dict
- 错误 **必须** 以 `{"error": "message"}` 的形式返回，绝不能抛出异常
- `check_fn` 在构建工具定义时调用——如果返回 `False`，该工具会被静默排除
- `handler` 接收 `(args: dict, **kwargs)`，其中 `args` 是 LLM 的工具调用参数
:::

## 步骤 2：添加到工具集 {#step-2-add-to-a-toolset}

在 `toolsets.py` 中添加工具名称：

```python
# If it should be available on all platforms (CLI + messaging):
_HERMES_CORE_TOOLS = [
    ...
    "weather",  # <-- add here
]

# Or create a new standalone toolset:
"weather": {
    "description": "Weather lookup tools",
    "tools": ["weather"],
    "includes": []
},
```

## ~~步骤 3：添加发现导入~~（已不再需要） {#step-3-add-discovery-import-no-longer-needed}

带有顶层 `registry.register()` 调用的工具模块会被 `tools/registry.py` 中的 `discover_builtin_tools()` 自动发现。无需手动维护导入列表——只需在 `tools/` 目录下创建文件，启动时就会自动加载。

## 异步处理器 {#async-handlers}

如果你的处理器需要异步代码，加上 `is_async=True` 标记即可：

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
    is_async=True,  # registry calls _run_async() automatically
)
```
注册表会透明地处理异步桥接——你不需要自己调用 `asyncio.run()`。

## 需要 task_id 的 Handler {#handlers-that-need-taskid}

需要管理每会话状态的工具会通过 `**kwargs` 接收 `task_id`：

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

## Agent Loop 拦截的工具 {#agent-loop-intercepted-tools}

某些工具（`todo`、`memory`、`session_search`、`delegate_task`）需要访问每会话的 Agent 状态。这些工具会在到达注册表之前被 `run_agent.py` 拦截。注册表中仍然保存着它们的 schema，但如果绕过拦截直接调用 `dispatch()`，会返回一个降级错误。

## 可选：Setup Wizard 集成 {#optional-setup-wizard-integration}

如果你的工具需要 API key，请把它添加到 `hermes_cli/config.py`：

```python
OPTIONAL_ENV_VARS = {
    ...
    "WEATHER_API_KEY": {
        "description": "Weather API key for weather lookup",
        "prompt": "Weather API key",
        "url": "https://weatherapi.com/",
        "tools": ["weather"],
        "password": True,
    },
}
```

## 检查清单 {#checklist}

- [ ] 已创建工具文件，包含 handler、schema、check 函数和注册逻辑
- [ ] 已添加到 `toolsets.py` 中合适的工具集
- [ ] 已在 `model_tools.py` 中添加发现式导入
- [ ] Handler 返回 JSON 字符串，错误以 `{"error": "..."}` 形式返回
- [ ] 可选：已在 `hermes_cli/config.py` 的 `OPTIONAL_ENV_VARS` 中添加 API key
- [ ] 可选：已添加到 `toolset_distributions.py` 以支持批量处理
- [ ] 已使用 `hermes chat -q "Use the weather tool for London"` 进行测试
