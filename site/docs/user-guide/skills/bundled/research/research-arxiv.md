---
title: "Arxiv — 通过关键词、作者、分类或 ID 搜索 arXiv 论文"
sidebar_label: "Arxiv"
description: "通过关键词、作者、分类或 ID 搜索 arXiv 论文"
---

{/* 此页面由网站/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Arxiv {#arxiv}

通过关键词、作者、分类或 ID 搜索 arXiv 论文。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/research/arxiv` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `Research`, `Arxiv`, `Papers`, `Academic`, `Science`, `API` |
| 相关技能 | [`ocr-and-documents`](/user-guide/skills/bundled/productivity/productivity-ocr-and-documents) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# arXiv 研究 {#arxiv-research}

通过 arXiv 的免费 REST API 搜索和获取学术论文。无需 API 密钥，无需依赖——只需 curl。

## 快速参考 {#quick-reference}

| 操作 | 命令 |
|--------|---------|
| 搜索论文 | `curl "https://export.arxiv.org/api/query?search_query=all:QUERY&max_results=5"` |
| 获取特定论文 | `curl "https://export.arxiv.org/api/query?id_list=2402.03300"` |
| 阅读摘要（网页） | `web_extract(urls=["https://arxiv.org/abs/2402.03300"])` |
| 阅读全文（PDF） | `web_extract(urls=["https://arxiv.org/pdf/2402.03300"])` |

## 搜索论文 {#searching-papers}

API 返回 Atom XML。使用 `grep`/`sed` 解析，或通过 `python3` 管道输出整洁结果。

### 基本搜索 {#basic-search}

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5"
```

### 整洁输出（将 XML 解析为可读格式） {#clean-output-parse-xml-to-readable-format}

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5&sortBy=submittedDate&sortOrder=descending" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for i, entry in enumerate(root.findall('a:entry', ns)):
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    published = entry.find('a:published', ns).text[:10]
    authors = ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))
    summary = entry.find('a:summary', ns).text.strip()[:200]
    cats = ', '.join(c.get('term') for c in entry.findall('a:category', ns))
    print(f'{i+1}. [{arxiv_id}] {title}')
    print(f'   Authors: {authors}')
    print(f'   Published: {published} | Categories: {cats}')
    print(f'   Abstract: {summary}...')
    print(f'   PDF: https://arxiv.org/pdf/{arxiv_id}')
    print()
"
```

## 搜索查询语法 {#search-query-syntax}

| 前缀 | 搜索范围 | 示例 |
|--------|----------|---------|
| `all:` | 所有字段 | `all:transformer+attention` |
| `ti:` | 标题 | `ti:large+language+models` |
| `au:` | 作者 | `au:vaswani` |
| `abs:` | 摘要 | `abs:reinforcement+learning` |
| `cat:` | 分类 | `cat:cs.AI` |
| `co:` | 评论 | `co:accepted+NeurIPS` |
### 布尔运算符 {#boolean-operators}

```
# AND（使用 + 时默认）
search_query=all:transformer+attention

# OR
search_query=all:GPT+OR+all:BERT

# AND NOT
search_query=all:language+model+ANDNOT+all:vision

# 精确短语
search_query=ti:"chain+of+thought"

# 组合
search_query=au:hinton+AND+cat:cs.LG
```

## 排序与分页 {#sort-and-pagination}

| 参数 | 选项 |
|-----------|---------|
| `sortBy` | `relevance`（相关性）、`lastUpdatedDate`（最后更新日期）、`submittedDate`（提交日期） |
| `sortOrder` | `ascending`（升序）、`descending`（降序） |
| `start` | 结果偏移量（从 0 开始） |
| `max_results` | 结果数量（默认 10，最大 30000） |

```bash
# cs.AI 类别中最新 10 篇论文
curl -s "https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=10"
```

## 获取特定论文 {#fetching-specific-papers}

```bash
# 按 arXiv ID 获取
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300"

# 多篇论文
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300,2401.12345,2403.00001"
```

## 生成 BibTeX {#bibtex-generation}

获取论文元数据后，生成 BibTeX 条目：

&#123;% raw %&#125;
```bash
curl -s "https://export.arxiv.org/api/query?id_list=1706.03762" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
root = ET.parse(sys.stdin).getroot()
entry = root.find('a:entry', ns)
if entry is None: sys.exit('Paper not found')
title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
authors = ' and '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))
year = entry.find('a:published', ns).text[:4]
raw_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
cat = entry.find('arxiv:primary_category', ns)
primary = cat.get('term') if cat is not None else 'cs.LG'
last_name = entry.find('a:author', ns).find('a:name', ns).text.split()[-1]
print(f'@article{{{last_name}{year}_{raw_id.replace(\".\", \"\")},')
print(f'  title     = {{{title}}},')
print(f'  author    = {{{authors}}},')
print(f'  year      = {{{year}}},')
print(f'  eprint    = {{{raw_id}}},')
print(f'  archivePrefix = {{arXiv}},')
print(f'  primaryClass  = {{{primary}}},')
print(f'  url       = {{https://arxiv.org/abs/{raw_id}}}')
print('}')
"
```
&#123;% endraw %&#125;

## 阅读论文内容 {#reading-paper-content}

找到论文后，阅读它：

```
# 摘要页面（快速，包含元数据和摘要）
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# 完整论文（PDF → 通过 Firecrawl 转换为 Markdown）
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
```

如需处理本地 PDF，请参见 `ocr-and-documents` 技能。

## 常见类别 {#common-categories}

| 类别 | 领域 |
|----------|-------|
| `cs.AI` | 人工智能 |
| `cs.CL` | 计算与语言（自然语言处理） |
| `cs.CV` | 计算机视觉 |
| `cs.LG` | 机器学习 |
| `cs.CR` | 密码学与安全 |
| `stat.ML` | 机器学习（统计学） |
| `math.OC` | 优化与控制 |
| `physics.comp-ph` | 计算物理 |

完整列表：https://arxiv.org/category_taxonomy
## 辅助脚本 {#helper-script}

`scripts/search_arxiv.py` 脚本负责解析 XML 并输出整洁的结果：

```bash
python scripts/search_arxiv.py "GRPO reinforcement learning"
python scripts/search_arxiv.py "transformer attention" --max 10 --sort date
python scripts/search_arxiv.py --author "Yann LeCun" --max 5
python scripts/search_arxiv.py --category cs.AI --sort date
python scripts/search_arxiv.py --id 2402.03300
python scripts/search_arxiv.py --id 2402.03300,2401.12345
```

无需额外依赖——仅使用 Python 标准库。

---

## Semantic Scholar（引用、相关论文、作者简介） {#semantic-scholar-citations-related-papers-author-profiles}

arXiv 不提供引用数据或推荐。请使用 **Semantic Scholar API** 来获取这些信息——免费，基础使用无需密钥（1 次请求/秒），返回 JSON 格式。

### 获取论文详情 + 引用数 {#get-paper-details-citations}

```bash
# 通过 arXiv ID 查询
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,authors,citationCount,referenceCount,influentialCitationCount,year,abstract" | python3 -m json.tool

# 通过 Semantic Scholar 论文 ID 或 DOI 查询
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1234/example?fields=title,citationCount"
```

### 获取某篇论文的被引情况（谁引用了它） {#get-citations-of-a-paper-who-cited-it}

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/citations?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

### 获取某篇论文的参考文献（它引用了哪些） {#get-references-from-a-paper-what-it-cites}

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/references?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

### 搜索论文（arXiv 搜索的替代方案，返回 JSON） {#search-papers-alternative-to-arxiv-search-returns-json}

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=GRPO+reinforcement+learning&limit=5&fields=title,authors,year,citationCount,externalIds" | python3 -m json.tool
```

### 获取论文推荐 {#get-paper-recommendations}

```bash
curl -s -X POST "https://api.semanticscholar.org/recommendations/v1/papers/" \
  -H "Content-Type: application/json" \
  -d '{"positivePaperIds": ["arXiv:2402.03300"], "negativePaperIds": []}' | python3 -m json.tool
```

### 作者简介 {#author-profile}

```bash
curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=Yann+LeCun&fields=name,hIndex,citationCount,paperCount" | python3 -m json.tool
```

### 常用的 Semantic Scholar 字段 {#useful-semantic-scholar-fields}

`title`、`authors`、`year`、`abstract`、`citationCount`、`referenceCount`、`influentialCitationCount`、`isOpenAccess`、`openAccessPdf`、`fieldsOfStudy`、`publicationVenue`、`externalIds`（包含 arXiv ID、DOI 等）

---

## 完整研究流程 {#complete-research-workflow}

1. **发现**：`python scripts/search_arxiv.py "你的主题" --sort date --max 10`
2. **评估影响力**：`curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID?fields=citationCount,influentialCitationCount"`
3. **阅读摘要**：`web_extract(urls=["https://arxiv.org/abs/ID"])`
4. **阅读全文**：`web_extract(urls=["https://arxiv.org/pdf/ID"])`
5. **查找相关工作**：`curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID/references?fields=title,citationCount&limit=20"`
6. **获取推荐**：向 Semantic Scholar 推荐端点发送 POST 请求
7. **追踪作者**：`curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=NAME"`
## 速率限制 {#rate-limits}

| API | 速率 | 认证 |
|-----|------|------|
| arXiv | 约 1 次请求 / 3 秒 | 无需 |
| Semantic Scholar | 1 次请求 / 秒 | 无需（有 API 密钥可提升至 100 次/秒） |

## 备注 {#notes}

- arXiv 返回 Atom XML 格式——可使用辅助脚本或解析代码片段来获取干净输出
- Semantic Scholar 返回 JSON 格式——可通过 `python3 -m json.tool` 管道输出以提高可读性
- arXiv ID：旧格式（`hep-th/0601001`）与新格式（`2402.03300`）
- PDF：`https://arxiv.org/pdf/{id}` —— 摘要：`https://arxiv.org/abs/{id}`
- HTML（如有）：`https://arxiv.org/html/{id}`
- 如需本地处理 PDF，请参见 `ocr-and-documents` 技能

## ID 版本管理 {#id-versioning}

- `arxiv.org/abs/1706.03762` 始终解析为**最新**版本
- `arxiv.org/abs/1706.03762v1` 指向**特定**的不可变版本
- 生成引用时，请保留您实际阅读的版本后缀，以防止引用漂移（后续版本可能大幅更改内容）
- API 的 `&lt;id&gt;` 字段返回带版本的 URL（例如 `http://arxiv.org/abs/1706.03762v7`）

## 已撤回论文 {#withdrawn-papers}

论文可能在提交后被撤回。发生这种情况时：
- `&lt;summary&gt;` 字段包含撤回通知（查找 "withdrawn" 或 "retracted"）
- 元数据字段可能不完整
- 在将结果视为有效论文之前，务必检查摘要
