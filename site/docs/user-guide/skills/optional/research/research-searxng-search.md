---
title: "Searxng 搜索 — 通过 SearXNG 免费元搜索 — 聚合 70+ 搜索引擎结果"
sidebar_label: "Searxng 搜索"
description: "通过 SearXNG 免费元搜索 — 聚合 70+ 搜索引擎结果"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="searxng-search"></a>
# Searxng 搜索

通过 SearXNG 免费元搜索 — 聚合 70+ 搜索引擎结果。可自建托管或使用公共实例，无需 API 密钥。当 Web 搜索工具集不可用时自动回退。

<a id="skill-metadata"></a>
## 技能元信息

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/searxng-search` 安装 |
| 路径 | `optional-skills/research/searxng-search` |
| 版本 | `1.0.0` |
| 作者 | hermes-agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `search`, `searxng`, `meta-search`, `self-hosted`, `free`, `fallback` |
| 相关技能 | [`duckduckgo-search`](/user-guide/skills/optional/research/research-duckduckgo-search), [`domain-intel`](/user-guide/skills/optional/research/research-domain-intel) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时所看到的指令。
:::

# SearXNG 搜索

使用 [SearXNG](https://searxng.org/) 的免费元搜索 — 一个注重隐私、可自建托管的搜索聚合器，同时查询 70+ 搜索引擎。

**使用公共实例无需 API 密钥**。也可自建托管以实现完全控制。当主 Web 搜索工具集（`FIRECRAWL_API_KEY`）未配置时，会自动作为回退方案出现。

<a id="configuration"></a>
## 配置

SearXNG 需要一个指向你的 SearXNG 实例的 `SEARXNG_URL` 环境变量：

```bash
# 公共实例（无需配置）
SEARXNG_URL=https://searxng.example.com

# 自建托管 SearXNG
SEARXNG_URL=http://localhost:8888
```

如果未配置实例，该技能将不可用，Agent 会回退到其他搜索选项。

<a id="detection-flow"></a>
## 检测流程

在选择方法之前，先检查实际可用内容：

```bash
# 检查 SEARXNG_URL 是否设置且实例是否可达
curl -s --max-time 5 "${SEARXNG_URL}/search?q=test&format=json" | head -c 200
```

决策树：
1. 如果 `SEARXNG_URL` 已设置且实例正常响应，则使用 SearXNG
2. 如果 `SEARXNG_URL` 未设置或不可达，则回退到其他可用搜索工具
3. 如果用户明确需要 SearXNG，则帮助他们设置实例或查找公共实例

<a id="method-1-cli-via-curl-preferred"></a>
## 方法 1：通过 curl 的 CLI（首选）

通过 `terminal` 使用 `curl` 调用 SearXNG JSON API。这避免依赖任何特定的 Python 包。

```bash
# 文本搜索（JSON 输出）
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=python+async+programming&format=json&engines=google,bing&limit=10"

# 关闭安全搜索
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=example&format=json&safesearch=0"

# 特定类别（general、news、science 等）
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=AI+news&format=json&categories=news"
```

<a id="common-cli-flags"></a>
### 常用 CLI 参数

| 参数 | 描述 | 示例 |
|------|------|------|
| `q` | 查询字符串（URL 编码） | `q=python+async` |
| `format` | 输出格式：`json`、`csv`、`rss` | `format=json` |
| `engines` | 逗号分隔的引擎名称 | `engines=google,bing,ddg` |
| `limit` | 每个引擎的最大结果数（默认 10） | `limit=5` |
| `categories` | 按类别筛选 | `categories=news,science` |
| `safesearch` | 0=无，1=中等，2=严格 | `safesearch=0` |
| `time_range` | 筛选：`day`、`week`、`month`、`year` | `time_range=week` |
<a id="parsing-json-results"></a>
### 解析 JSON 结果

```bash
# 从 JSON 中提取标题和 URL
curl -s --max-time 10 "${SEARXNG_URL}/search?q=fastapi&format=json&limit=5" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data.get('results', []):
    print(r.get('title',''))
    print(r.get('url',''))
    print(r.get('content','')[:200])
    print()
"
```

每个结果返回：`title`、`url`、`content`（摘要）、`engine`、`parsed_url`、`img_src`、`thumbnail`、`author`、`published_date`

<a id="method-2-python-api-via-requests"></a>
## 方法 2：通过 `requests` 调用 Python API

直接从 Python 中使用 `requests` 库调用 SearXNG REST API：

```python
import os, requests, urllib.parse

base_url = os.environ.get("SEARXNG_URL", "")
if not base_url:
    raise RuntimeError("SEARXNG_URL 未设置")

query = "fastapi deployment guide"
params = {
    "q": query,
    "format": "json",
    "limit": 5,
    "engines": "google,bing",
}

resp = requests.get(f"{base_url}/search", params=params, timeout=10)
resp.raise_for_status()
data = resp.json()

for r in data.get("results", []):
    print(r["title"])
    print(r["url"])
    print(r.get("content", "")[:200])
    print()
```

<a id="method-3-searxng-data-python-package"></a>
## 方法 3：使用 searxng-data Python 包

如需更结构化的访问方式，安装 `searxng-data` 包：

```bash
pip install searxng-data
```

```python
from searxng_data import engines

# 列出可用的引擎
print(engines.list_engines())
```

注意：此包仅提供引擎元数据，不包含搜索 API 本身。

<a id="self-hosting-searxng"></a>
## 自托管 SearXNG

要运行你自己的 SearXNG 实例：

```bash
# 使用 Docker
docker run -d -p 8888:8080 \
  -v $(pwd)/searxng:/etc/searxng \
  searxng/searxng:latest

# 然后设置
SEARXNG_URL=http://localhost:8888
```

或者通过 pip 安装：
```bash
pip install searxng
# 编辑 /etc/searxng/settings.yml
searxng-run
```

公共 SearXNG 实例可通过以下地址访问：
- `https://searxng.example.com`（替换为任何公共实例）

<a id="workflow-search-then-extract"></a>
## 工作流程：先搜索再提取

SearXNG 返回的是标题、URL 和摘要，而不是完整页面内容。要获取完整的页面内容，建议先搜索，然后用 `web_extract`、浏览器工具或 `curl` 提取最相关的 URL。

```bash
# 搜索相关页面
curl -s "${SEARXNG_URL}/search?q=fastapi+deployment&format=json&limit=3"
# 输出：包含标题和 URL 的结果列表

# 然后用 web_extract 提取最佳 URL 的内容
```

<a id="limitations"></a>
## 限制

- **实例可用性**：如果 SearXNG 实例宕机或无法访问，搜索会失败。始终检查 `SEARXNG_URL` 是否设置且实例可访问。
- **不提取内容**：SearXNG 返回的是摘要，不是完整页面内容。请使用 `web_extract`、浏览器工具或 `curl` 获取完整文章。
- **速率限制**：某些公共实例会限制请求频率。自托管可以避免此问题。
- **引擎覆盖范围**：可用的引擎取决于 SearXNG 实例的配置，某些引擎可能被禁用。
- **结果新鲜度**：元搜索引擎聚合的是外部引擎的结果——结果的新鲜度取决于这些引擎。

<a id="troubleshooting"></a>
## 故障排除

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| `SEARXNG_URL` 未设置 | 未配置实例 | 使用公共 SearXNG 实例或自行搭建 |
| 连接被拒绝 | 实例未运行或 URL 错误 | 检查 URL 是否正确以及实例是否运行 |
| 结果为空 | 实例屏蔽了该查询 | 尝试其他实例或自托管 |
| 响应慢 | 公共实例负载过高 | 自托管或使用负载较低的公共实例 |
| `json` 格式不支持 | SearXNG 版本过旧 | 尝试 `format=rss` 或升级 SearXNG |
<a id="pitfalls"></a>
## 注意事项

- **务必设置 `SEARXNG_URL`**：没有该变量，此技能无法生效。
- **对查询进行 URL 编码**：在 curl 中，空格和特殊字符必须进行 URL 编码，或在 Python 中使用 `urllib.parse.quote()`。
- **使用 `format=json`**：默认格式可能无法被机器解析，务必显式请求 JSON。
- **设置超时**：始终使用 `--max-time` 或 `timeout=` 参数，避免因为实例不可达而导致请求挂死。
- **最好自建实例**：公共实例可能会宕机、限流或屏蔽请求。自建实例更可靠。

<a id="instance-discovery"></a>
## 实例发现

如果未设置 `SEARXNG_URL`，且用户询问 SearXNG，可协助用户选择以下之一：
1. 查找一个公共 SearXNG 实例（搜索 "public searxng instance"）
2. 通过 Docker 或 pip 自行搭建

公共实例列表请参见：https://searxng.org/
