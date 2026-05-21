---
sidebar_position: 2
title: "添加工具"
description: "如何向 Hermes Agent 添加新工具——模式、处理器、注册与工具集"
---

<a id="adding-tools"></a>
# 添加工具

在动手编写工具之前，先问问自己：**这个功能更适合写成[技能](creating-skills.md)吗？**

:::warning 仅限内置核心工具
本文档介绍的是向仓库本身添加一个 **内置 Hermes 工具**。
<a id="built-in-core-tools-only"></a>
如果你想要添加个人、项目本地或自定义工具，且不修改 Hermes 核心，请改用插件方式：

- [插件](/user-guide/features/plugins)
- [构建 Hermes 插件](/guides/build-a-hermes-plugin)

大多数自定义工具都推荐使用插件。只有在你想明确地将一个新内置工具发布到 `tools/` 和 `toolsets.py` 中时，才按照本文操作。
:::

如果功能可以通过指令 + Shell 命令 + 现有工具（如 arXiv 搜索、Git 工作流、Docker 管理、PDF 处理）来实现，那就应该做成**技能**。

如果功能需要端到端集成 API 密钥、自定义处理逻辑、二进制数据处理或流式传输（如浏览器自动化、TTS、视觉分析），那就应该做成**工具**。

<a id="overview"></a>
## 概览

添加一个工具涉及 **2 个文件**：

1. **`tools/your_tool.py`** — 处理器、模式、检查函数、`registry.register()` 调用
2. **`toolsets.py`** — 将工具名称添加到 `_HERMES_CORE_TOOLS`（或某个特定工具集）

任何在顶层调用了 `registry.register()` 的 `tools/*.py` 文件都会在启动时自动被发现——无需手动导入列表。

<a id="step-1-create-the-built-in-tool-file"></a>
## 第一步：创建内置工具文件

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
    """如果工具的依赖项可用则返回 True。"""
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
                "description": "城市名或坐标（例如 'London' 或 '51.5,-0.1'）"
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
<a id="key-rules"></a>
### 关键规则

:::danger 重要
- 处理器**必须**返回 JSON 字符串（通过 `json.dumps()`），绝不能返回原始 dict
- 错误**必须**以 `{"error": "message"}` 的形式返回，绝不能作为异常抛出
- `check_fn` 在构建工具定义时被调用——如果返回 `False`，该工具会被静默排除
- `handler` 接收 `(args: dict, **kwargs)`，其中 `args` 是 LLM 工具调用的参数
:::

<a id="important"></a>
<a id="step-2-add-the-built-in-tool-to-a-toolset"></a>
## 第二步：将内置工具添加到工具集

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

<a id="step-3-add-discovery-import-no-longer-needed"></a>
## ~~第三步：添加发现导入~~（不再需要）

包含顶层 `registry.register()` 调用的工具模块会被 `tools/registry.py` 中的 `discover_builtin_tools()` 自动发现。无需维护手动导入列表——只需在 `tools/` 目录下创建文件，启动时即可自动加载。

<a id="async-handlers"></a>
## 异步处理器

如果你的处理器需要异步代码，使用 `is_async=True` 标记：

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

注册中心会自动处理异步桥接——你永远不需要自己调用 `asyncio.run()`。

<a id="handlers-that-need-taskid"></a>
## 需要 task_id 的处理器

管理每个会话状态的工具通过 `**kwargs` 接收 `task_id`：

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

<a id="agent-loop-intercepted-tools"></a>
## Agent-Loop 拦截的工具

一些工具（`todo`、`memory`、`session_search`、`delegate_task`）需要访问每个会话的 Agent 状态。这些工具在到达注册中心之前会被 `run_agent.py` 拦截。注册中心仍然持有它们的 schema，但如果绕过拦截，`dispatch()` 会返回一个回退错误。

<a id="optional-setup-wizard-integration"></a>
## 可选：设置向导集成

如果你的工具需要 API 密钥，将其添加到 `hermes_cli/config.py` 中：

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

<a id="checklist"></a>
## 检查清单

- [ ] 创建了包含处理器、schema、检查函数和注册的工具文件
- [ ] 已添加到 `toolsets.py` 中的相应工具集
- [ ] 确认这确实应该是一个内置/核心工具，而不是插件
- [ ] 处理器返回 JSON 字符串，错误以 `{"error": "..."}` 形式返回
- [ ] 可选：在 `hermes_cli/config.py` 的 `OPTIONAL_ENV_VARS` 中添加了 API 密钥
- [ ] 可选：已添加到 `toolset_distributions.py` 以支持批量处理
- [ ] 使用 `hermes chat -q "Use the weather tool for London"` 进行了测试
