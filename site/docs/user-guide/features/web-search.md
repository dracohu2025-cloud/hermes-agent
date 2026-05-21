---
title: Web Search & Extract
description: 搜索网页、提取页面内容，并通过多个后端提供商进行网站爬取——包括免费的自行托管的 SearXNG。
sidebar_label: 网页搜索
sidebar_position: 6
---

<a id="web-search-extract"></a>
# 网页搜索与提取

Hermes Agent 包含两个由多个后端驱动的、可供模型调用的网页工具：

- **`web_search`** — 搜索网页并返回排序结果
- **`web_extract`** — 从一个或多个 URL 获取并提取可读内容（当后端支持时，内置深度爬取功能）

两者通过同一个后端选择进行配置。提供商通过 `hermes tools` 选择，或直接在 `config.yaml` 中设置。递归爬取能力（Firecrawl/Tavily）通过 `web_extract` 暴露，而非作为独立的 `web_crawl` 工具。

<a id="backends"></a>
## 后端

| 提供商 | 环境变量 | 搜索 | 提取 | 爬取 | 免费层 |
|----------|---------|--------|---------|-------|-----------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ | 500 积分/月 |
| **SearXNG** | `SEARXNG_URL` | ✔ | — | — | ✔ 免费（自行托管） |
| **Brave Search（免费层）** | `BRAVE_SEARCH_API_KEY` | ✔ | — | — | 2000 次查询/月 |
| **DDGS（DuckDuckGo）** | —（无需密钥） | ✔ | — | — | ✔ 免费 |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ | 1000 次搜索/月 |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — | 1000 次搜索/月 |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — | 付费 |
| **xAI（Grok）** | `XAI_API_KEY` 或 `hermes auth login xai-oauth` | ✔ | — | — | 付费（SuperGrok 或按 token 计费） |
Brave Search、DDGS 和 xAI 是纯 **搜索** 能力——当你还需要 `web_extract` 时，需要将它们与 Firecrawl/Tavily/Exa/Parallel 中的任意一个搭配使用。DDGS 底层使用 [`ddgs` Python 包](https://pypi.org/project/ddgs/)；如果尚未安装，请运行 `pip install ddgs`（或者让 Hermes 在首次使用时惰性安装）。xAI 在 Responses API 上使用 Grok 服务端的 `web_search` 工具——结果是 LLM 生成的，而非索引支持，因此标题、描述和 URL 选择都是模型输出（请参阅下方的 [信任模型说明](#xai-grok)）。

**按能力拆分：** 你可以为搜索和提取独立使用不同的提供商——例如搜索用 SearXNG（免费），提取用 Firecrawl。请参阅下方的 [按能力配置](#per-capability-configuration)。

<a id="nous-subscribers"></a>
:::tip Nous 订阅者
如果你拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，则可通过 **[工具网关](tool-gateway.md)** 经由托管的 Firecrawl 使用网页搜索和提取——无需 API 密钥。运行 `hermes tools` 即可启用。
:::
---

<a id="how-webextract-handles-long-pages"></a>
## `web_extract` 如何处理长页面

后端返回的原始页面 Markdown 可能非常庞大（比如论坛帖子、文档站点、带有嵌入式评论的新闻文章）。为了让上下文窗口保持可用并控制成本，`web_extract` 在将内容交给 agent 之前，会先通过 **`web_extract` 辅助模型**对返回的内容进行处理。其行为完全由页面大小决定：

| 页面大小（字符数） | 处理方式 |
|------------------------|--------------|
| 5 000 以下 | 原样返回 — 不调用 LLM，完整的 Markdown 会到达 agent |
| 5 000 – 500 000 | 通过 `web_extract` 辅助模型进行单次摘要总结，输出上限约为 5 000 字符 |
| 500 000 – 2 000 000 | 分块处理：将页面分割成 100k 字符的块，并行总结每一块，然后合成最终摘要（约 5 000 字符） |
| 超过 2 000 000 | 拒绝处理，并提示使用 `web_crawl` 配合聚焦的提取指令或更具体的来源 |

摘要会保留引文、代码块和关键事实的原始格式——它是一个内容压缩器，而非改写器。如果摘要失败或超时，Hermes 会回退使用原始内容的前约 5 000 字符，而不是返回一个无用的错误。
<a id="which-model-does-the-summarizing"></a>
### 由哪个模型来做摘要？

这由 `web_extract` 辅助任务决定。默认情况下（`auxiliary.web_extract.provider: "auto"`），它会使用你的**主聊天模型**——提供商和模型都与 `hermes model` 相同。这对大多数配置来说没问题，但如果使用昂贵的推理模型（Opus、MiniMax M2.7 等），每次提取长页面都会显著增加成本。

要绕过主模型，改用便宜、快速的模型来做提取摘要，可以这样配置：

```yaml
# ~/.hermes/config.yaml
auxiliary:
  web_extract:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 360       # 秒；如果遇到摘要超时可酌情调大
```

也可以交互式选择：`hermes model` → **Configure auxiliary models** → `web_extract`。

完整的参考说明和按任务覆盖的模式请参见[辅助模型](/user-guide/configuration#auxiliary-models)。

<a id="when-summarization-gets-in-the-way"></a>
### 当摘要反而碍事时

如果你需要的是原始、未经摘要的页面内容——例如，你在抓取一个结构化页面，而 LLM 摘要会丢失重要字段——那么请改用 `browser_navigate` + `browser_snapshot`。浏览器工具会返回实时的无障碍树，不受辅助模型的重写影响（但超大页面有 8 000 字符的快照上限）。

### Firecrawl（默认）

功能齐全的搜索、提取与爬取。推荐大多数用户使用。

```bash
# ~/.hermes/.env
FIRECRAWL_API_KEY=fc-your-key-here
```

在 [firecrawl.dev](https://firecrawl.dev) 获取密钥。免费版包含每月 500 次配额。

**自托管 Firecrawl：** 指向你自己的实例，而非云 API：

```bash
# ~/.hermes/.env
FIRECRAWL_API_URL=http://localhost:3002
```

当设置了 `FIRECRAWL_API_URL` 时，API 密钥为可选项（可通过 `USE_DB_AUTHENTICATION=false` 禁用服务端认证）。

---

### SearXNG（免费、自托管）

SearXNG 是一个尊重隐私的开源元搜索引擎，聚合了 70 多个搜索引擎的结果。**无需 API 密钥**——只需让 Hermes 指向一个正在运行的 SearXNG 实例即可。

SearXNG **仅支持搜索**——`web_extract`（包括其爬取模式）需要单独的提取提供商。
<a id="option-a-self-host-with-docker-recommended"></a>
#### 选项 A — 使用 Docker 自托管（推荐）

这样你就能拥有一个无速率限制的私有实例。

**1. 创建工作目录：**

```bash
mkdir -p ~/searxng/searxng
cd ~/searxng
```

**2. 编写 `docker-compose.yml`：**

```yaml
# ~/searxng/docker-compose.yml
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "8888:8080"
    volumes:
      - ./searxng:/etc/searxng:rw
    environment:
      - SEARXNG_BASE_URL=http://localhost:8888/
    restart: unless-stopped
```

**3. 启动容器：**

```bash
docker compose up -d
```

**4. 启用 JSON API 格式：**

SearXNG 默认禁用了 JSON 输出。复制生成的配置文件并启用它：

```bash
# 从容器中复制自动生成的配置
docker cp searxng:/etc/searxng/settings.yml ~/searxng/searxng/settings.yml
```

打开 `~/searxng/searxng/settings.yml`，找到 `formats` 块（大约在第 84 行）：

```yaml
# Before (default — JSON disabled):
formats:
  - html

# After (enable JSON for Hermes):
formats:
  - html
  - json
```
**5. 重启以生效：**

```bash
docker cp ~/searxng/searxng/settings.yml searxng:/etc/searxng/settings.yml
docker restart searxng
```

**6. 验证是否正常：**

```bash
curl -s "http://localhost:8888/search?q=test&format=json" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"results\"])} results')"
```

你应该会看到类似 `10 results` 的输出。如果遇到 `403 Forbidden`，表示 JSON 格式仍未启用 —— 请重新检查第 4 步。

**7. 配置 Hermes：**

```bash
# ~/.hermes/.env
SEARXNG_URL=http://localhost:8888
```

然后在 `~/.hermes/config.yaml` 中选择 SearXNG 作为搜索后端：

```yaml
web:
  search_backend: "searxng"
```

或者通过 `hermes tools` → Web Search & Extract → SearXNG 进行设置。

---

<a id="option-b-use-a-public-instance"></a>
#### 方案 B — 使用公共实例

公共 SearXNG 实例列表请参见 [searx.space](https://searx.space/)。筛选出已启用 **JSON 格式**（表中会标明）的实例。

```bash
# ~/.hermes/.env
SEARXNG_URL=https://searx.example.com
```

<a id="public-instances"></a>
:::caution 公共实例注意事项
公共实例存在访问频率限制、可用性不稳定，并且可能随时禁用 JSON 格式。生产环境强烈建议自行部署。
:::

### Tavily

AI 优化的搜索、提取和抓取，提供慷慨的免费套餐。

```bash
# ~/.hermes/.env
TAVILY_API_KEY=tvly-your-key-here
```

在 [app.tavily.com](https://app.tavily.com/home) 获取密钥。免费套餐包含每月 1 000 次搜索。

---

### Exa

具备语义理解的神经搜索，适合研究和查找概念相关的内容。

```bash
# ~/.hermes/.env
EXA_API_KEY=your-exa-key-here
```

在 [exa.ai](https://exa.ai) 获取密钥。免费套餐包含每月 1 000 次搜索。

---

### Parallel

---
AI 原生的搜索与提取能力，具备深度研究功能。

```bash
# ~/.hermes/.env
PARALLEL_API_KEY=your-parallel-key-here
```

在 [parallel.ai](https://parallel.ai) 获取访问权限。

---

### xAI (Grok) {#xai-grok}

通过 Grok 在 Responses API 上的服务端 [web_search 工具](https://docs.x.ai/developers/tools/web-search) 来路由 `web_search`。Grok 执行实际的搜索，并将最相关的结果以结构化 JSON 返回。

支持两种凭证方式——无需新的环境变量，也无需新的设置向导：

```bash
# ~/.hermes/.env (env-var path)
XAI_API_KEY=sk-xai-your-key-here
```

或者对于 SuperGrok 订阅用户：

```bash
hermes auth login xai-oauth
```

然后选择 xAI 作为搜索后端：

```yaml
# ~/.hermes/config.yaml
web:
  backend: "xai"
```

**可选参数：**

```yaml
web:
  backend: "xai"
  xai:
    model: grok-4.3              # reasoning model required by web_search (default)
    allowed_domains:             # optional, max 5 — mutex with excluded_domains
      - arxiv.org
    excluded_domains:            # optional, max 5
      - example-spam.com
    timeout: 90                  # seconds (default)
```
**仅搜索** — 如果还需要 `web_extract`，可搭配 Firecrawl / Tavily / Exa / Parallel 使用。当返回 401 时，提供商会强制执行一次 OAuth 令牌刷新并重试（能够处理窗口期内的吊销以及主动过期检查无法解码的不透明令牌）；环境变量凭据则跳过重试。

:::caution 信任模型
与按原样返回搜索引擎结果的索引型后端（Brave、Tavily、Exa）不同，xAI 本身是一个大语言模型，它自行决定显示哪些 URL，并自行编写标题与描述。查询的*内容*会影响其输出，因此恶意构造的查询（例如通过 Agent 从不可信的上游输入中获取的注入内容）原则上可以引导 Grok 输出攻击者选择的 URL。请像对待任何模型生成的链接一样对待返回的 URL——在抓取前进行验证，特别是当查询源自不可信输入时。
<a id="trust-model"></a>
:::

---

<a id="configuration"></a>
## 配置

<a id="single-backend"></a>
### 单一后端

为所有 Web 能力设置一个提供者：

```yaml
# ~/.hermes/config.yaml
web:
  backend: "searxng"   # firecrawl | searxng | brave-free | ddgs | tavily | exa | parallel | xai
```
<a id="per-capability-configuration"></a>
### 按能力配置

为搜索和提取使用不同的提供商。这样可以让你将免费的搜索（SearXNG）与付费的提取提供商结合使用，反之亦然：

```yaml
# ~/.hermes/config.yaml
web:
  search_backend: "searxng"     # 由 web_search 使用
  extract_backend: "firecrawl"  # 由 web_extract（及其深度爬取模式）使用
```

当按能力的键为空时，两者都会回退到 `web.backend`。当 `web.backend` 也为空时，后端会根据已有的 API 密钥/URL 自动检测。

**优先级顺序（按能力）：**
1. `web.search_backend` / `web.extract_backend`（显式按能力指定）
2. `web.backend`（共享回退）
3. 从环境变量自动检测

<a id="auto-detection"></a>
### 自动检测

如果没有显式配置后端，Hermes 会根据已设置的凭证选择第一个可用的后端：

| 提供的凭证 | 自动选择的后端 |
|--------------------|-----------------------|
| `FIRECRAWL_API_KEY` 或 `FIRECRAWL_API_URL` | firecrawl |
| `PARALLEL_API_KEY` | parallel |
| `TAVILY_API_KEY` | tavily |
| `EXA_API_KEY` | exa |
| `SEARXNG_URL` | searxng |
xAI Web Search **不**在自动检测链中——即使设置了 `XAI_API_KEY`（或通过 xAI Grok OAuth 登录），也不会自动将网络流量路由至 xAI，因为这些凭证还用于推理 / TTS / 图像生成，用户可能希望为 Web 使用不同的后端。请通过 `web.backend: "xai"` 明确选择启用。

---

<a id="verify-your-setup"></a>
## 验证您的设置

运行 `hermes setup` 查看检测到的 Web 后端：

```
✅ Web Search & Extract (searxng)
```

或者通过 CLI 检查：

```bash
# Activate the venv and run the web tools module directly
source ~/.hermes/hermes-agent/.venv/bin/activate
python -m tools.web_tools
```

这会打印出活跃的后端及其状态：

```
✅ Web backend: searxng
   Using SearXNG (search only): http://localhost:8888
```

---

<a id="troubleshooting"></a>
## 故障排除

<a id="websearch-returns-success-false"></a>
### `web_search` 返回 `{"success": false}`

- 检查 `SEARXNG_URL` 是否可达：`curl -s "http://localhost:8888/search?q=test&format=json"`
- 如果遇到 HTTP 403，说明 JSON 格式被禁用——将 `json` 添加到 `settings.yml` 的 `formats` 列表中，然后重启
- 如果遇到连接错误，容器可能没有运行：`docker ps | grep searxng`
<a id="webextract-says-search-only-backend"></a>
### `web_extract` 提示"仅搜索后端"

SearXNG 无法提取 URL 内容。将 `web.extract_backend` 设为支持提取的提供方：

```yaml
web:
  search_backend: "searxng"
  extract_backend: "firecrawl"  # 或 tavily / exa / parallel
```

<a id="searxng-returns-0-results"></a>
### SearXNG 返回 0 条结果

某些公共实例禁用了部分搜索引擎或类别。请尝试：
- 不同的查询
- 从 [searx.space](https://searx.space/) 选择不同的公共实例
- 自建实例以获得可靠结果

<a id="rate-limited-on-a-public-instance"></a>
### 公共实例上的速率限制

切换为自建实例（参见上文的[方案 A](#option-a--self-host-with-docker-recommended)）。使用 Docker 时，自己的实例没有速率限制。

<a id="webextract-returns-truncated-content-with-a-summarization-timed-out-note"></a>
### `web_extract` 返回截断的内容，并附有"摘要超时"提示

辅助模型未在配置的超时时间内完成摘要。请执行以下任一操作：

- 在 `config.yaml` 中提高 `auxiliary.web_extract.timeout`（新安装默认 360 秒，若缺少该键则默认 30 秒）
- 将 `web_extract` 辅助任务切换为更快的模型（例如 `google/gemini-3-flash-preview`）——参见[`web_extract` 如何处理长页面](#how-web_extract-handles-long-pages)
- 对于不适合用摘要处理的页面，改用 `browser_navigate`
---

<a id="optional-skill-searxng-search"></a>
## 可选技能：`searxng-search`

对于需要通过 `curl` 直接使用 SearXNG 的 Agent（例如当 Web 工具集不可用时作为回退方案），可以安装 `searxng-search` 可选技能：

```bash
hermes skills install official/research/searxng-search
```

该技能教会 Agent 如何：
- 通过 `curl` 或 Python 调用 SearXNG JSON API
- 按类别（`general`、`news`、`science` 等）进行过滤
- 处理分页和错误情况
- 在 SearXNG 不可用时优雅降级
