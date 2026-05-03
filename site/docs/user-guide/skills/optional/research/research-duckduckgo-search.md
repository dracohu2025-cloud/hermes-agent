---
title: "Duckduckgo 搜索 — 通过 DuckDuckGo 免费搜索网页 — 文本、新闻、图片、视频"
sidebar_label: "Duckduckgo 搜索"
description: "通过 DuckDuckGo 免费搜索网页 — 文本、新闻、图片、视频"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Duckduckgo 搜索 {#duckduckgo-search}

通过 DuckDuckGo 免费搜索网页 — 文本、新闻、图片、视频。无需 API 密钥。优先使用 `ddgs` CLI（如果已安装）；仅在确认当前运行时环境中 `ddgs` 可用后，再使用 Python DDGS 库。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/duckduckgo-search` 安装 |
| 路径 | `optional-skills/research/duckduckgo-search` |
| 版本 | `1.3.0` |
| 作者 | gamedevCloudy |
| 许可证 | MIT |
| 标签 | `search`, `duckduckgo`, `web-search`, `free`, `fallback` |
| 相关技能 | [`arxiv`](/user-guide/skills/bundled/research/research-arxiv) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

<a id="duckduckgo-search"></a>
# DuckDuckGo 搜索

使用 DuckDuckGo 进行免费网页搜索。**无需 API 密钥。**

当 `web_search` 不可用或不适用时（例如未设置 `FIRECRAWL_API_KEY`）优先使用。当明确需要 DuckDuckGo 结果时，也可作为独立的搜索路径使用。

## 检测流程 {#detection-flow}

在选择方法之前，先检查实际可用的工具：

```bash
# 检查 CLI 是否可用
command -v ddgs >/dev/null && echo "DDGS_CLI=installed" || echo "DDGS_CLI=missing"
```

决策树：
1. 如果 `ddgs` CLI 已安装，优先使用 `terminal` + `ddgs`
2. 如果 `ddgs` CLI 缺失，不要假设 `execute_code` 可以导入 `ddgs`
3. 如果用户明确要求 DuckDuckGo，先在相关环境中安装 `ddgs`
4. 否则回退到内置的网页/浏览器工具

重要的运行时说明：
- Terminal 和 `execute_code` 是独立的运行时环境
- 在 shell 中成功安装并不保证 `execute_code` 可以导入 `ddgs`
- 永远不要假设第三方 Python 包已预装在 `execute_code` 中

## 安装 {#installation}

仅在明确需要 DuckDuckGo 搜索且运行时环境尚未提供 `ddgs` 时安装。

```bash
# Python 包 + CLI 入口点
pip install ddgs

# 验证 CLI
ddgs --help
```

如果工作流依赖 Python 导入，在使用 `from ddgs import DDGS` 之前，请先确认同一运行时环境可以导入 `ddgs`。

## 方法 1：CLI 搜索（推荐） {#method-1-cli-search-preferred}

当 `ddgs` 命令存在时，通过 `terminal` 使用它。这是推荐路径，因为它避免了假设 `execute_code` 沙箱中已安装 `ddgs` Python 包。

```bash
# 文本搜索
ddgs text -q "python async programming" -m 5

# 新闻搜索
ddgs news -q "artificial intelligence" -m 5

# 图片搜索
ddgs images -q "landscape photography" -m 10

# 视频搜索
ddgs videos -q "python tutorial" -m 5

# 带地区过滤
ddgs text -q "best restaurants" -m 5 -r us-en

# 仅最近结果（d=天, w=周, m=月, y=年）
ddgs text -q "latest AI news" -m 5 -t w

# JSON 输出以便解析
ddgs text -q "fastapi tutorial" -m 5 -o json
```
### CLI 标志 {#cli-flags}

| 标志 | 描述 | 示例 |
|------|------|------|
| `-q` | 查询 — **必填** | `-q "搜索词"` |
| `-m` | 最大结果数 | `-m 5` |
| `-r` | 区域 | `-r us-en` |
| `-t` | 时间限制 | `-t w`（周） |
| `-s` | 安全搜索 | `-s off` |
| `-o` | 输出格式 | `-o json` |

## 方法 2：Python API（仅验证后使用） {#method-2-python-api-only-after-verification}

仅在确认 `ddgs` 已安装后，才能在 `execute_code` 或其他 Python 运行时中使用 `DDGS` 类。不要假设 `execute_code` 默认包含第三方包。

安全表述：
- "在需要时安装或验证包后，使用 `execute_code` 配合 `ddgs`"

避免说：
- "`execute_code` 包含 `ddgs`"
- "DuckDuckGo 搜索在 `execute_code` 中默认可用"

**重要：** `max_results` 必须始终作为**关键字参数**传递——位置参数用法会在所有方法上引发错误。

### 文本搜索 {#text-search}

最适合：通用研究、公司、文档。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.text("python 异步编程", max_results=5):
        print(r["title"])
        print(r["href"])
        print(r.get("body", "")[:200])
        print()
```

返回：`title`、`href`、`body`

### 新闻搜索 {#news-search}

最适合：时事、突发新闻、最新动态。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.news("AI 监管 2026", max_results=5):
        print(r["date"], "-", r["title"])
        print(r.get("source", ""), "|", r["url"])
        print(r.get("body", "")[:200])
        print()
```

返回：`date`、`title`、`body`、`url`、`image`、`source`

### 图片搜索 {#image-search}

最适合：视觉参考、产品图片、图表。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.images("半导体芯片", max_results=5):
        print(r["title"])
        print(r["image"])
        print(r.get("thumbnail", ""))
        print(r.get("source", ""))
        print()
```

返回：`title`、`image`、`thumbnail`、`url`、`height`、`width`、`source`

### 视频搜索 {#video-search}

最适合：教程、演示、解说。

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.videos("FastAPI 教程", max_results=5):
        print(r["title"])
        print(r.get("content", ""))
        print(r.get("duration", ""))
        print(r.get("provider", ""))
        print(r.get("published", ""))
        print()
```

返回：`title`、`content`、`description`、`duration`、`provider`、`published`、`statistics`、`uploader`

### 快速参考 {#quick-reference}

| 方法 | 使用场景 | 关键字段 |
|--------|----------|------------|
| `text()` | 通用研究、公司 | title, href, body |
| `news()` | 时事、更新 | date, title, source, body, url |
| `images()` | 视觉、图表 | title, image, thumbnail, url |
| `videos()` | 教程、演示 | title, content, duration, provider |

## 工作流：先搜索再提取 {#workflow-search-then-extract}

DuckDuckGo 返回标题、URL 和摘要——而不是完整页面内容。要获取完整页面内容，请先搜索，然后使用 `web_extract`、浏览器工具或 curl 提取最相关的 URL。
CLI 示例：

```bash
ddgs text -q "fastapi deployment guide" -m 3 -o json
```

Python 示例，仅在确认该运行环境中已安装 `ddgs` 后使用：

```python
from ddgs import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text("fastapi deployment guide", max_results=3))
    for r in results:
        print(r["title"], "->", r["href"])
```

然后使用 `web_extract` 或其他内容检索工具提取最佳 URL。

## 局限性 {#limitations}

- **速率限制**：DuckDuckGo 在大量快速请求后可能会限流。如有需要，可在搜索之间添加短暂延迟。
- **无内容提取**：`ddgs` 返回的是摘要片段，而非完整页面内容。请使用 `web_extract`、浏览器工具或 curl 获取完整文章/页面。
- **结果质量**：总体不错，但可配置性不如 Firecrawl 的搜索。
- **可用性**：DuckDuckGo 可能会阻止来自某些云 IP 的请求。如果搜索返回空结果，请尝试不同的关键词或等待几秒钟。
- **字段可变性**：返回的字段可能因结果或 `ddgs` 版本而异。对可选字段使用 `.get()` 以避免 `KeyError`。
- **独立的运行环境**：在终端中成功安装 `ddgs` 并不自动意味着 `execute_code` 可以导入它。

## 故障排除 {#troubleshooting}

| 问题 | 可能原因 | 解决方法 |
|---------|--------------|------------|
| `ddgs: command not found` | CLI 未在 shell 环境中安装 | 安装 `ddgs`，或改用内置的 web/浏览器工具 |
| `ModuleNotFoundError: No module named 'ddgs'` | Python 运行环境未安装该包 | 在该运行环境准备好之前，不要使用 Python DDGS |
| 搜索返回空结果 | 临时速率限制或查询不佳 | 等待几秒钟，重试，或调整查询 |
| CLI 可用但 `execute_code` 导入失败 | 终端和 `execute_code` 是不同的运行环境 | 继续使用 CLI，或单独准备 Python 运行环境 |

## 常见陷阱 {#pitfalls}

- **`max_results` 是仅限关键字参数**：`ddgs.text("query", 5)` 会引发错误。请使用 `ddgs.text("query", max_results=5)`。
- **不要假设 CLI 存在**：在使用前检查 `command -v ddgs`。
- **不要假设 `execute_code` 可以导入 `ddgs`**：`from ddgs import DDGS` 可能会因 `ModuleNotFoundError` 而失败，除非该运行环境已单独准备。
- **包名**：该包名为 `ddgs`（之前为 `duckduckgo-search`）。使用 `pip install ddgs` 安装。
- **不要混淆 `-q` 和 `-m`**（CLI）：`-q` 用于查询，`-m` 用于最大结果数。
- **空结果**：如果 `ddgs` 返回空，可能是被限流了。等待几秒钟后重试。

## 已验证 {#validated-with}

已验证的示例基于 `ddgs==9.11.2` 的语义。技能指南现在将 CLI 可用性和 Python 导入可用性视为独立问题，因此文档化的工作流程与实际运行环境行为一致。
