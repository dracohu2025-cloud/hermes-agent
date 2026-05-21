---
title: "Scrapling"
sidebar_label: "Scrapling"
description: "使用 Scrapling 进行网页抓取——HTTP 请求、隐身浏览器自动化、Cloudflare 绕过，以及通过 CLI 和 Python 实现爬虫抓取"
---

{/* 此页面由 skills 源目录中的 SKILL.md 经 website/scripts/generate-skill-docs.py 自动生成。请编辑源 SKILL.md，而不是本页面。 */}

<a id="scrapling"></a>
# Scrapling

使用 Scrapling 进行网页抓取——HTTP 请求、隐身浏览器自动化、Cloudflare 绕过，以及通过 CLI 和 Python 实现爬虫抓取。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/scrapling` 安装 |
| 路径 | `optional-skills/research/scrapling` |
| 版本 | `1.0.0` |
| 作者 | FEUAZUR |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Web Scraping`, `Browser`, `Cloudflare`, `Stealth`, `Crawling`, `Spider` |
| 相关技能 | [`duckduckgo-search`](/user-guide/skills/optional/research/research-duckduckgo-search), [`domain-intel`](/user-guide/skills/optional/research/research-domain-intel) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能激活时 Hermes 加载的完整技能定义。这是 Agent 在技能生效时看到的指令。
:::

# Scrapling

[Scrapling](https://github.com/D4Vinci/Scrapling) 是一个网页抓取框架，具备反机器人绕过、隐身浏览器自动化以及爬虫框架功能。它提供了三种抓取策略（HTTP、动态 JS、隐身/Cloudflare）以及完整的 CLI。

**此技能仅供教育和研究用途。** 用户必须遵守当地/国际数据抓取法律，并尊重网站的《服务条款》。

<a id="when-to-use"></a>
## 何时使用

- 抓取静态 HTML 页面（比浏览器工具更快）
- 抓取需要真实浏览器的 JS 渲染页面
- 绕过 Cloudflare Turnstile 或机器人检测
- 使用爬虫抓取多个页面
- 当内置的 `web_extract` 工具无法返回所需数据时

<a id="installation"></a>
## 安装

```bash
pip install "scrapling[all]"
scrapling install
```

最小化安装（仅 HTTP，无浏览器）：
```bash
pip install scrapling
```

仅包含浏览器自动化：
```bash
pip install "scrapling[fetchers]"
scrapling install
```

<a id="quick-reference"></a>
## 快速参考

| 方法 | 类 | 适用场景 |
|----------|-------|----------|
| HTTP | `Fetcher` / `FetcherSession` | 静态页面、API、快速批量请求 |
| 动态 | `DynamicFetcher` / `DynamicSession` | JS 渲染内容、单页应用 |
| 隐身 | `StealthyFetcher` / `StealthySession` | Cloudflare、反机器人保护网站 |
| 爬虫 | `Spider` | 多页面抓取，跟随链接 |

<a id="cli-usage"></a>
## CLI 用法

<a id="extract-static-page"></a>
### 提取静态页面

```bash
scrapling extract get 'https://example.com' output.md
```

使用 CSS 选择器和浏览器伪装：

```bash
scrapling extract get 'https://example.com' output.md \
  --css-selector '.content' \
  --impersonate 'chrome'
```

<a id="extract-js-rendered-page"></a>
### 提取 JS 渲染页面

```bash
scrapling extract fetch 'https://example.com' output.md \
  --css-selector '.dynamic-content' \
  --disable-resources \
  --network-idle
```

<a id="extract-cloudflare-protected-page"></a>
### 提取受 Cloudflare 保护的页面

```bash
scrapling extract stealthy-fetch 'https://protected-site.com' output.html \
  --solve-cloudflare \
  --block-webrtc \
  --hide-canvas
```
<a id="post-request"></a>
### POST 请求

```bash
scrapling extract post 'https://example.com/api' output.json \
  --json '{"query": "search term"}'
```

<a id="output-formats"></a>
### 输出格式

输出格式由文件扩展名决定：
- `.html` -- 原始 HTML
- `.md` -- 转换为 Markdown
- `.txt` -- 纯文本
- `.json` / `.jsonl` -- JSON

<a id="python-http-scraping"></a>
## Python：HTTP 数据采集

<a id="single-request"></a>
### 单次请求

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
for q in quotes:
    print(q)
```

<a id="session-persistent-cookies"></a>
### 会话（持久化 Cookie）

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://example.com/', stealthy_headers=True)
    links = page.css('a::attr(href)').getall()
    for link in links[:5]:
        sub = session.get(link)
        print(sub.css('h1::text').get())
```

<a id="post-put-delete"></a>
### POST / PUT / DELETE

```python
page = Fetcher.post('https://api.example.com/data', json={"key": "value"})
page = Fetcher.put('https://api.example.com/item/1', data={"name": "updated"})
page = Fetcher.delete('https://api.example.com/item/1')
```

<a id="with-proxy"></a>
### 使用代理

```python
page = Fetcher.get('https://example.com', proxy='http://user:pass@proxy:8080')
```

<a id="python-dynamic-pages-js-rendered"></a>
## Python：动态页面（JS 渲染）

对于需要执行 JavaScript 的页面（SPA、惰性加载内容）：

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://example.com', headless=True)
data = page.css('.js-loaded-content::text').getall()
```

<a id="wait-for-specific-element"></a>
### 等待特定元素

```python
page = DynamicFetcher.fetch(
    'https://example.com',
    wait_selector=('.results', 'visible'),
    network_idle=True,
)
```

<a id="disable-resources-for-speed"></a>
### 禁用资源以提高速度

阻止字体、图片、媒体、样式表（速度提升约 25%）：

```python
from scrapling.fetchers import DynamicSession

with DynamicSession(headless=True, disable_resources=True, network_idle=True) as session:
    page = session.fetch('https://example.com')
    items = page.css('.item::text').getall()
```

<a id="custom-page-automation"></a>
### 自定义页面自动化

```python
from playwright.sync_api import Page
from scrapling.fetchers import DynamicFetcher

def scroll_and_click(page: Page):
    page.mouse.wheel(0, 3000)
    page.wait_for_timeout(1000)
    page.click('button.load-more')
    page.wait_for_selector('.extra-results')

page = DynamicFetcher.fetch('https://example.com', page_action=scroll_and_click)
results = page.css('.extra-results .item::text').getall()
```

<a id="python-stealth-mode-anti-bot-bypass"></a>
## Python：隐身模式（反爬虫绕过）

适用于受 Cloudflare 保护或具有高度指纹识别的网站：

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True,
    block_webrtc=True,
    hide_canvas=True,
)
content = page.css('.protected-content::text').getall()
```

<a id="stealth-session"></a>
### 隐身会话

```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page1 = session.fetch('https://protected-site.com/page1')
    page2 = session.fetch('https://protected-site.com/page2')
```
<a id="element-selection"></a>
## 元素选择

所有抓取器都会返回一个 `Selector` 对象，包含以下方法：

<a id="css-selectors"></a>
### CSS 选择器

```python
page.css('h1::text').get()              # 第一个 h1 文本
page.css('a::attr(href)').getall()      # 所有链接的 href 属性
page.css('.quote .text::text').getall() # 嵌套选择
```

<a id="xpath"></a>
### XPath

```python
page.xpath('//div[@class="content"]/text()').getall()
page.xpath('//a/@href').getall()
```

<a id="find-methods"></a>
### 查找方法

```python
page.find_all('div', class_='quote')       # 按标签 + 属性
page.find_by_text('Read more', tag='a')    # 按文本内容
page.find_by_regex(r'\$\d+\.\d{2}')       # 按正则表达式
```

<a id="similar-elements"></a>
### 相似元素

查找结构相似的元素（适用于产品列表等场景）：

```python
first_product = page.css('.product')[0]
all_similar = first_product.find_similar()
```

<a id="navigation"></a>
### 导航

```python
el = page.css('.target')[0]
el.parent                # 父元素
el.children              # 子元素
el.next_sibling          # 下一个兄弟元素
el.prev_sibling          # 上一个兄弟元素
```

<a id="python-spider-framework"></a>
## Python：Spider 框架

用于多页面爬取和链接跟踪：

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10
    download_delay = 1

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
                "tags": quote.css('.tag::text').getall(),
            }

        next_page = response.css('.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

result = QuotesSpider().start()
print(f"Scraped {len(result.items)} quotes")
result.items.to_json("quotes.json")
```

<a id="multi-session-spider"></a>
### 多会话 Spider

将请求路由到不同的抓取器类型：

```python
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class SmartSpider(Spider):
    name = "smart"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)
```

<a id="pause-resume-crawling"></a>
### 暂停/恢复爬取

```python
spider = QuotesSpider(crawldir="./crawl_checkpoint")
spider.start()  # 按 Ctrl+C 暂停，重新运行即可从检查点恢复
```

<a id="pitfalls"></a>
## 常见陷阱

- **需要安装浏览器**：在 pip install 之后运行 `scrapling install`——如果不做这一步，`DynamicFetcher` 和 `StealthyFetcher` 会失败
- **超时设置**：DynamicFetcher / StealthyFetcher 的超时单位为**毫秒**（默认 30000），Fetcher 的超时单位为**秒**
- **Cloudflare 绕过**：`solve_cloudflare=True` 会为获取增加 5-15 秒时间——只在需要时开启
- **资源占用**：StealthyFetcher 会运行一个真实的浏览器——请限制并发使用
- **法律问题**：爬取前务必检查 robots.txt 和网站的 ToS。本库仅用于教育及研究目的
- **Python 版本**：需要 Python 3.10 及以上版本
