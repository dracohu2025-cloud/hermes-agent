---
sidebar_position: 12
title: "Web 搜索提供者插件"
description: "如何为 Hermes Agent 构建一个 Web 搜索/提取/爬取的后端插件"
---

<a id="building-a-web-search-provider-plugin"></a>
# 构建 Web 搜索提供者插件

Web 搜索提供者插件会注册一个后端，用于处理 `web_search`、`web_extract` 以及（可选）深度爬取工具调用。内置的提供者——Firecrawl、SearXNG、Tavily、Exa、Parallel、Brave Search（免费版）和 DDGS——都以插件形式放在 `plugins/web/<名称>/` 目录下。你可以在它们旁边新建一个目录来添加新插件，或者覆盖已有的插件。

:::tip
Web 搜索是 Hermes 支持的几种**后端插件**之一。其他插件（各有自己的抽象基类）包括[图像生成提供者插件](/developer-guide/image-gen-provider-plugin)、[视频生成提供者插件](/developer-guide/video-gen-provider-plugin)、[记忆提供者插件](/developer-guide/memory-provider-plugin)、[上下文引擎插件](/developer-guide/context-engine-plugin)和[模型提供者插件](/developer-guide/model-provider-plugin)。通用的工具/钩子/CLI 插件请参考[构建 Hermes 插件](/guides/build-a-hermes-plugin)。
:::

<a id="how-discovery-works"></a>
## 发现机制

Hermes 会在三个位置扫描 Web 搜索后端：

1. **内置** — `<仓库>/plugins/web/<名称>/`（自动加载，`kind: backend`，始终可用）
2. **用户** — `~/.hermes/plugins/web/<名称>/`（通过 `plugins.enabled` 或 `hermes plugins enable <名称>` 选择启用）
3. **Pip** — 声明了 `hermes_agent.plugins` 入口点的包

每个插件的 `register(ctx)` 函数会调用 `ctx.register_web_search_provider(...)`——这会将实例注册到 `agent/web_search_registry.py` 的注册表中。每个能力使用的活跃提供者由配置决定：

| 能力 | 配置键 | 回退到 |
|---|---|---|
| `web_search` | `web.search_backend` | `web.backend` |
| `web_extract` | `web.extract_backend` | `web.backend` |
| `web_extract` 内部的深度爬取模式 | `web.extract_backend` | `web.backend` |

当两个键都未设置时，Hermes 会根据环境中存在的 API 密钥/URL 自动检测后端。`hermes tools` 会引导用户完成选择。

<a id="directory-structure"></a>
## 目录结构

```
plugins/web/my-backend/
├── __init__.py     # register() 入口点
├── provider.py     # WebSearchProvider 子类
└── plugin.yaml     # 清单文件，包含 kind: backend 和 provides_web_providers
```

`brave_free/` 和 `ddgs/` 是树内最小的参考实现——`brave_free` 是一个需要 API 密钥的纯搜索提供者，`ddgs` 是一个无需密钥的提供者，会惰性安装其 SDK。

<a id="the-websearchprovider-abc"></a>
## WebSearchProvider 抽象基类

继承 `agent.web_search_provider.WebSearchProvider`。唯一必需的成员是 `name`、`is_available()`，以及你实现的 `search()` / `extract()` / `crawl()` 中的任意方法。

```python
# plugins/web/my-backend/provider.py
from __future__ import annotations

import os
from typing import Any, Dict, List

from agent.web_search_provider import WebSearchProvider


class MyBackendWebSearchProvider(WebSearchProvider):
    """针对 My Backend HTTP API 的最小化纯搜索提供者。"""

    @property
    def name(self) -> str:
        # 用于 web.search_backend / web.extract_backend / web.backend
        # 配置键的稳定标识符。小写，无空格；允许使用连字符。
        return "my-backend"

    @property
    def display_name(self) -> str:
        # 在 `hermes tools` 中显示的人类可读标签。默认为 `name`。
        return "My Backend"

    def is_available(self) -> bool:
        # 轻量检查——环境变量是否存在、可选依赖是否可导入等。
        # 禁止发起网络调用（每次 `hermes tools` 渲染时都会运行）。
        return bool(os.getenv("MY_BACKEND_API_KEY", "").strip())

    def supports_search(self) -> bool:
        return True

    def supports_extract(self) -> bool:
        return False

    def supports_crawl(self) -> bool:
        return False

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        import httpx

        api_key = os.environ["MY_BACKEND_API_KEY"]
        try:
            resp = httpx.get(
                "https://api.example.com/search",
                params={"q": query, "count": max(1, min(int(limit), 20))},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            return {"success": False, "error": str(exc)}

        # 响应格式是固定的——请参考下面的“响应格式”。
        return {
            "success": True,
            "data": {
                "web": [
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("snippet", ""),
                        "position": idx + 1,
                    }
                    for idx, item in enumerate(data.get("results", []))
                ],
            },
        }
```
```python
# plugins/web/my-backend/__init__.py
from plugins.web.my_backend.provider import MyBackendWebSearchProvider


def register(ctx) -> None:
    """插件入口点——在加载时调用一次。"""
    ctx.register_web_search_provider(MyBackendWebSearchProvider())
```

<a id="plugin-yaml"></a>
## plugin.yaml

```yaml
name: web-my-backend
version: 1.0.0
description: "My Backend 网络搜索 — Bearer 认证 REST API"
author: Your Name
kind: backend
provides_web_providers:
  - my-backend
requires_env:
  - MY_BACKEND_API_KEY
```

| 键 | 用途 |
|---|---|
| `kind: backend` | 将插件路由到后端加载路径 |
| `provides_web_providers` | 此插件注册的 provider `name` 列表——加载器用它来在 `register()` 运行之前，就在 `hermes tools` 中宣传该插件 |
| `requires_env` | 在 `hermes plugins install` 期间交互式提示输入凭据（有关完整格式，请参见[构建 Hermes 插件](/guides/build-a-hermes-plugin#gate-on-environment-variables)） |

<a id="abc-reference"></a>
## ABC 参考

完整契约在 `agent/web_search_provider.py` 中。你可以重写以下方法：

| 成员 | 必需 | 默认值 | 用途 |
|---|---|---|---|
| `name` | ✅ | — | 在 `web.*_backend` 配置中使用的稳定 ID |
| `display_name` | — | `name` | 在 `hermes tools` 中显示的标签 |
| `is_available()` | ✅ | — | 廉价可用性检查——环境变量、可选依赖 |
| `supports_search()` | — | `True` | 用于 `web_search` 路由的能力标志 |
| `supports_extract()` | — | `False` | 用于 `web_extract` 路由的能力标志 |
| `supports_crawl()` | — | `False` | 用于深度爬取模式的能力标志 |
| `search(query, limit)` | 条件性 | 抛出异常 | 当 `supports_search()` 返回 `True` 时必需 |
| `extract(urls, **kwargs)` | 条件性 | 抛出异常 | 当 `supports_extract()` 返回 `True` 时必需 |
| `crawl(url, **kwargs)` | 条件性 | 抛出异常 | 当 `supports_crawl()` 返回 `True` 时必需 |

Provider 可以在单个类中声明多种能力——Firecrawl、Tavily、Exa 和 Parallel 都实现了搜索/提取/爬取全部三种功能。Brave Search 和 DDGS 仅支持搜索；SearXNG 仅支持搜索，并附带一个文档化的“请为我搭配一个提取 provider”工作流。

<a id="response-shape"></a>
## 响应格式

工具包装器期望一个固定的信封结构，这样它就不需要在不同后端之间进行转换。

**搜索成功：**

```python
{
    "success": True,
    "data": {
        "web": [
            {"title": str, "url": str, "description": str, "position": int},
            ...
        ],
    },
}
```

**提取成功：**

```python
{
    "success": True,
    "data": [
        {
            "url": str,
            "title": str,
            "content": str,
            "raw_content": str,
            "metadata": dict,    # 可选
            "error": str,        # 可选，仅在单个 URL 失败时出现
        },
        ...
    ],
}
```

**任一能力，失败时：**

```python
{"success": False, "error": "人类可读的消息"}
```

`search()` 和 `extract()` 都可以是 `async def`——调度器通过 `inspect.iscoroutinefunction` 检测协程函数并相应地等待。对于小型后端，执行阻塞 I/O（HTTP、SDK 调用）的同步实现也是可以的；调度器会处理线程问题。
<a id="capability-flags"></a>
## 能力标志

Hermes 根据 `supports_*` 标志将调用路由到正确的提供者。一个常见的多提供者配置：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "brave-free"     # search-only, fast, free 2k/mo
  extract_backend: "firecrawl"     # extract + crawl, paid quota
```

当 `web.search_backend` 或 `web.extract_backend` 未设置时，两者都会回退到 `web.backend`。如果也未设置，Hermes 会根据环境变量的存在情况，选择第一个支持所需能力的可用提供者。

如果你的提供者只支持一种能力，将其他标志保留为默认值（`False`），注册中心会为该工具跳过它——当用户仅将 X 用于搜索并要求 Agent 进行提取时，不会看到误导性的"provider X 失败"错误。

<a id="how-hermes-wires-it-into-the-tools"></a>
## Hermes 如何将其接入工具

`web_search` 和 `web_extract` 工具位于 `tools/web_tools.py` 中。在调用时，它们：

1. 读取相关配置键（`web_search` 使用 `web.search_backend`，`web_extract` 使用 `web.extract_backend`）
2. 向注册中心请求具有该 `name` 的提供者
3. 检查 `is_available()` 和对应的 `supports_*()` 标志
4. 分派到 `search()` / `extract()` / `crawl()`，如果方法是协程则等待
5. 将响应信封 JSON 序列化并交回给 LLM

错误作为工具结果呈现；LLM 决定如何解释它们。如果没有注册任何提供者（或所有可用的都未能通过能力门槛），该工具会返回一个指向 `hermes tools` 的有帮助的错误。

<a id="lazy-installing-optional-dependencies"></a>
## 懒安装可选依赖

如果你的提供者封装了第三方 SDK（如 DDGS 封装了 `ddgs` 包），不要在模块顶层进行 `import`。在 `is_available()` 或 `search()` 内部使用 `tools.lazy_deps.ensure(...)`——Hermes 会在首次使用时安装该包，并由 `security.allow_lazy_installs` 控制。见 [构建 Hermes 插件 → 懒安装](/guides/build-a-hermes-plugin#lazy-install-optional-python-dependencies) 了解安全模型。

<a id="reference-implementations"></a>
## 参考实现

- **`plugins/web/brave_free/`** — 小型、API 密钥保护、仅搜索的 HTTP 提供者。不错的入门模板。
- **`plugins/web/ddgs/`** — 无需密钥的提供者，懒安装其 SDK。对于封装了 Python 包的后端很有用的模式。
- **`plugins/web/firecrawl/`** — 完整的多能力提供者（搜索 + 提取 + 爬取），支持多种格式模式。
- **`plugins/web/searxng/`** — 自托管、URL 配置的后端，无需认证。
- **`plugins/web/xai/`** — 通过 Grok 服务端 `web_search` 工具的 LLM 支持的搜索。展示了如何重用现有的 OAuth/环境变量凭证接口（`tools/xai_http.py`）而不添加新的环境变量，以及如何编写一个遵守无网络契约的轻量 `is_available()`。

<a id="distribute-via-pip"></a>
## 通过 pip 发布

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-backend-web = "my_backend_web_package"
```

`my_backend_web_package` 必须暴露一个顶层 `register` 函数。有关完整设置，请参阅通用插件指南中的 [通过 pip 发布](/guides/build-a-hermes-plugin#distribute-via-pip)。
<a id="related-pages"></a>
## 相关页面

- [Web Search](/user-guide/features/web-search) — 面向用户的功能文档和各后端配置说明
- [Plugins overview](/user-guide/features/plugins) — 所有插件类型一览
- [Build a Hermes Plugin](/guides/build-a-hermes-plugin) — 一般工具/钩子/斜杠命令指南
