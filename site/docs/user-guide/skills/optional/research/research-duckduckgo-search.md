---
title: "Duckduckgo 搜索 — 通过 DuckDuckGo 进行免费网页搜索 — 文本、新闻、图片、视频"
sidebar_label: "Duckduckgo 搜索"
description: "通过 DuckDuckGo 进行免费网页搜索 — 文本、新闻、图片、视频"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能中的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="duckduckgo-search"></a>
# Duckduckgo 搜索

通过 DuckDuckGo 进行免费网页搜索 — 文本、新闻、图片、视频。无需 API 密钥。当安装了 `ddgs` CLI 时优先使用它；仅当确认 `ddgs` 在当前运行时可用后，再使用 Python DDGS 库。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/duckduckgo-search` 安装 |
| 路径 | `optional-skills/research/duckduckgo-search` |
| 版本 | `1.3.0` |
| 作者 | gamedevCloudy |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `search`, `duckduckgo`, `web-search`, `free`, `fallback` |
| 相关技能 | [`arxiv`](/user-guide/skills/bundled/research/research-arxiv) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在该技能激活时看到的指令。
:::

# DuckDuckGo 搜索

使用 DuckDuckGo 进行免费网页搜索。**无需 API 密钥。**

当 `web_search` 不可用或不适用时（例如未设置 `FIRECRAWL_API_KEY`）优先使用。当明确需要 DuckDuckGo 结果时，也可以作为独立的搜索路径使用。

<a id="detection-flow"></a>
## 检测流程

在选择方法之前，检查实际可用的工具：

```bash
# 检查 CLI 是否可用
command -v ddgs >/dev/null && echo "DDGS_CLI=installed" || echo "DDGS_CLI=missing"
```

决策树：
1. 如果安装了 `ddgs` CLI，则优先使用 `terminal` + `ddgs`
2. 如果缺少 `ddgs` CLI，不要假设 `execute_code` 能导入 `ddgs`
3. 如果用户明确需要 DuckDuckGo，先在相关环境中安装 `ddgs`
4. 否则回退到内置的 web/浏览器工具

重要的运行时说明：
- Terminal 和 `execute_code` 是独立的运行时
- 在 shell 中成功安装并不保证 `execute_code` 能导入 `ddgs`
- 永远不要假设第三方 Python 包在 `execute_code` 中已预装

<a id="installation"></a>
## 安装

仅当明确需要 DuckDuckGo 搜索且当前运行时未提供 `ddgs` 时，才安装它。

```bash
# Python 包 + CLI 入口点
pip install ddgs

# 验证 CLI
ddgs --help
```

如果工作流依赖 Python 导入，请在使用 `from ddgs import DDGS` 之前确认同一运行时可以导入 `ddgs`。

<a id="method-1-cli-search-preferred"></a>
## 方式 1：CLI 搜索（推荐）

当 `ddgs` 命令存在时，通过 `terminal` 使用它。这是推荐路径，因为它避免了假设 `execute_code` 沙盒已安装 `ddgs` Python 包。

```bash
# 文本搜索
ddgs text -q "python async programming" -m 5

# 新闻搜索
ddgs news -q "artificial intelligence" -m 5

# 图片搜索
ddgs images -q "landscape photography" -m 10

# 视频搜索
ddgs videos -q "python tutorial" -m 5

# 带地域筛选
ddgs text -q "best restaurants" -m 5 -r us-en

# 仅最近结果（d=天，w=周，m=月，y=年）
ddgs text -q "latest AI news" -m 5 -t w

# JSON 输出以便解析
ddgs text -q "fastapi tutorial" -m 5 -o json
```
<a id="cli-flags"></a>
### CLI 标志

| 标志 | 描述 | 示例 |
|------|------|------|
| `-q` | 查询 — **必填** | `-q "搜索词"` |
| `-m` | 最大结果数 | `-m 5` |
| `-r` | 区域 | `-r us-en` |
| `-t` | 时间限制 | `-t w` (周) |
| `-s` | 安全搜索 | `-s off` |
| `-o` | 输出格式 | `-o json` |

<a id="method-2-python-api-only-after-verification"></a>
## 方法 2：Python API（仅验证后使用）

只有在确认已安装 `ddgs` 的情况下，才在 `execute_code` 或其他 Python 运行时中使用 `DDGS` 类。不要假设 `execute_code` 默认包含第三方包。

安全的表述：
- "如果需要，在安装或验证包后，使用带有 `ddgs` 的 `execute_code`"

应避免的表述：
- "`execute_code` 包含 `ddgs`"
- "DuckDuckGo 搜索在 `execute_code` 中默认可用"

**重要：** `max_results` 必须始终作为 **关键字参数** 传递——位置参数用法会在所有方法中引发错误。

<a id="text-search"></a>
### 文本搜索

最适合：常规调研、公司、文档。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.text("python async programming", max_results=5):
        print(r["title"])
        print(r["href"])
        print(r.get("body", "")[:200])
        print()
```

返回：`title`、`href`、`body`

<a id="news-search"></a>
### 新闻搜索

最适合：时事、突发新闻、最新动态。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.news("AI regulation 2026", max_results=5):
        print(r["date"], "-", r["title"])
        print(r.get("source", ""), "|", r["url"])
        print(r.get("body", "")[:200])
        print()
```

返回：`date`、`title`、`body`、`url`、`image`、`source`

<a id="image-search"></a>
### 图片搜索

最适合：视觉参考、产品图片、图表。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.images("semiconductor chip", max_results=5):
        print(r["title"])
        print(r["image"])
        print(r.get("thumbnail", ""))
        print(r.get("source", ""))
        print()
```

返回：`title`、`image`、`thumbnail`、`url`、`height`、`width`、`source`

<a id="video-search"></a>
### 视频搜索

最适合：教程、演示、解释性内容。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.videos("FastAPI tutorial", max_results=5):
        print(r["title"])
        print(r.get("content", ""))
        print(r.get("duration", ""))
        print(r.get("provider", ""))
        print(r.get("published", ""))
        print()
```

返回：`title`、`content`、`description`、`duration`、`provider`、`published`、`statistics`、`uploader`

<a id="quick-reference"></a>
### 快速参考

| 方法 | 适用场景 | 关键字段 |
|--------|----------|------------|
| `text()` | 常规调研、公司 | title、href、body |
| `news()` | 时事、动态更新 | date、title、source、body、url |
| `images()` | 视觉内容、图表 | title、image、thumbnail、url |
| `videos()` | 教程、演示 | title、content、duration、provider |

<a id="workflow-search-then-extract"></a>
## 工作流程：搜索后提取

DuckDuckGo 返回标题、URL 和摘要——而不是完整的页面内容。要获取完整的页面内容，请先搜索，然后使用 `web_extract`、浏览器工具或 curl 提取最相关的 URL。
CLI 示例：

```bash
ddgs text -q "fastapi deployment guide" -m 3 -o json
```

Python 示例（仅在确认 `ddgs` 已安装在该运行时后使用）：

```python
from ddgs import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text("fastapi deployment guide", max_results=3))
    for r in results:
        print(r["title"], "->", r["href"])
```

然后使用 `web_extract` 或其他内容检索工具提取最佳的 URL。

<a id="limitations"></a>
## 局限性

- **速率限制**：DuckDuckGo 在收到大量快速请求后可能会限制频率。如有需要，可在查询之间添加短暂延迟。
- **无内容提取**：`ddgs` 返回的是摘要片段，而非完整页面内容。请使用 `web_extract`、浏览器工具或 curl 获取完整的文章/页面。
- **结果质量**：总体不错，但相比 Firecrawl 的搜索可配置性较低。
- **可用性**：DuckDuckGo 可能会拦截来自某些云 IP 的请求。如果搜索返回空结果，请尝试不同的关键词或等待几秒后重试。
- **字段可变性**：返回的字段可能因结果或 `ddgs` 版本而异。对于可选字段请使用 `.get()` 以避免 `KeyError`。
- **独立运行时**：在终端中成功安装 `ddgs` 并不意味着 `execute_code` 能导入它。

<a id="troubleshooting"></a>
## 故障排除

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| `ddgs: command not found` | CLI 未安装在 shell 环境中 | 安装 `ddgs`，或改用内置的 web/浏览器工具 |
| `ModuleNotFoundError: No module named 'ddgs'` | Python 运行时未安装该包 | 在该运行时未准备好之前，不要使用 Python DDGS |
| 搜索没有返回任何结果 | 临时速率限制或查询不当 | 等待几秒后重试，或调整查询词 |
| CLI 能运行，但 `execute_code` 导入失败 | 终端和 `execute_code` 是不同的运行时 | 继续使用 CLI，或单独准备好 Python 运行时 |

<a id="pitfalls"></a>
## 常见陷阱

- **`max_results` 是仅限关键词参数**：`ddgs.text("query", 5)` 会引发错误。请使用 `ddgs.text("query", max_results=5)`。
- **不要假设 CLI 存在**：使用前请先检查 `command -v ddgs`。
- **不要假设 `execute_code` 可以导入 `ddgs`**：`from ddgs import DDGS` 可能会因 `ModuleNotFoundError` 而失败，除非该运行时已单独准备好。
- **包名**：包名是 `ddgs`（之前是 `duckduckgo-search`）。使用 `pip install ddgs` 安装。
- **不要混淆 `-q` 和 `-m`**（CLI）：`-q` 用于查询词，`-m` 用于最大结果数量。
- **空结果**：如果 `ddgs` 返回空，可能是被限速了。等待几秒后重试。

<a id="validated-with"></a>
## 验证依据

验证示例基于 `ddgs==9.11.2` 的语义。技能指南现在将 CLI 可用性和 Python 导入可用性视为独立的问题，使得记录的工作流程与实际运行时行为一致。
