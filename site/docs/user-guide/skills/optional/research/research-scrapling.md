---
title: "Scrapling"
sidebar_label: "Scrapling"
description: "使用 Scrapling 进行网页抓取 - HTTP 获取、隐身浏览器自动化、Cloudflare 绕过，以及通过 CLI 和 Python 进行爬虫抓取"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Scrapling {#scrapling}

使用 Scrapling 进行网页抓取 - HTTP 获取、隐身浏览器自动化、Cloudflare 绕过，以及通过 CLI 和 Python 进行爬虫抓取。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/scrapling` 安装 |
| 路径 | `optional-skills/research/scrapling` |
| 版本 | `1.0.0` |
| 作者 | FEUAZUR |
| 许可证 | MIT |
| 标签 | `Web Scraping`, `Browser`, `Cloudflare`, `Stealth`, `Crawling`, `Spider` |
| 相关技能 | [`duckduckgo-search`](/user-guide/skills/optional/research/research-duckduckgo-search), [`domain-intel`](/user-guide/skills/optional/research/research-domain-intel) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会看到这些指令。
:::

<a id="scrapling"></a>
# Scrapling

[Scrapling](https://github.com/D4Vinci/Scrapling) 是一个网页抓取框架，具备反机器人绕过、隐身浏览器自动化和爬虫框架功能。它提供三种获取策略（HTTP、动态 JS、隐身/Cloudflare）以及完整的 CLI。

**本技能仅用于教育和研究目的。** 用户必须遵守当地/国际数据抓取法律，并尊重网站的《服务条款》。

## 何时使用 {#when-to-use}

- 抓取静态 HTML 页面（比浏览器工具更快）
- 抓取需要真实浏览器的 JS 渲染页面
- 绕过 Cloudflare Turnstile 或机器人检测
- 使用爬虫抓取多个页面
- 当内置的 `web_extract` 工具无法返回所需数据时

## 安装 {#installation}

```bash
pip install "scrapling[all]"
scrapling install
```

最小安装（仅 HTTP，无浏览器）：
```bash
pip install scrapling
```

仅带浏览器自动化：
```bash
pip install "scrapling[fetchers]"
scrapling install
```

## 快速参考 {#quick-reference}

| 方式 | 类 | 使用场景 |
|----------|-------|----------|
| HTTP | `Fetcher` / `FetcherSession` | 静态页面、API、快速批量请求 |
| 动态 | `DynamicFetcher` / `DynamicSession` | JS 渲染内容、SPA |
| 隐身 | `StealthyFetcher` / `StealthySession` | Cloudflare、反机器人保护站点 |
| 爬虫 | `Spider` | 多页面抓取，支持链接跟踪 |

## CLI 用法 {#cli-usage}

### 提取静态页面 {#extract-static-page}

```bash
scrapling extract get 'https://example.com' output.md
```

带 CSS 选择器和浏览器模拟：

```bash
scrapling extract get 'https://example.com' output.md \
  --css-selector '.content' \
  --impersonate 'chrome'
```

### 提取 JS 渲染页面 {#extract-js-rendered-page}

```bash
scrapling extract fetch 'https://example.com' output.md \
  --css-selector '.dynamic-content' \
  --disable-resources \
  --network-idle
```

### 提取 Cloudflare 保护页面 {#extract-cloudflare-protected-page}

```bash
scrapling extract stealthy-fetch 'https://protected-site.com' output.html \
  --solve-cloudflare \
  --block-webrtc \
  --hide-canvas
```
### POST 请求 {#post-request}

```bash
scrapling extract post 'https://example.com/api' output.json \
  --json '{"query": "search term"}'
```

### 输出格式 {#output-formats}

输出格式由文件扩展名决定：
- `.html` — 原始 HTML
- `.md` — 转换为 Markdown
- `.txt` — 纯文本
- `.json` / `.jsonl` — JSON

## Python：HTTP 抓取 {#python-http-scraping}

### 单次请求 {#single-request}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
for q in quotes:
    print(q)
```

### 会话（持久化 Cookie） {#session-persistent-cookies}

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://example.com/', stealthy_headers=True)
    links = page.css('a::attr(href)').getall()
    for link in links[:5]:
        sub = session.get(link)
        print(sub.css('h1::text').get())
```

### POST / PUT / DELETE {#post-put-delete}

```python
page = Fetcher.post('https://api.example.com/data', json={"key": "value"})
page = Fetcher.put('https://api.example.com/item/1', data={"name": "updated"})
page = Fetcher.delete('https://api.example.com/item/1')
```

### 使用代理 {#with-proxy}

```python
page = Fetcher.get('https://example.com', proxy='http://user:pass@proxy:8080')
```

## Python：动态页面（JS 渲染） {#python-dynamic-pages-js-rendered}

对于需要执行 JavaScript 的页面（SPA、懒加载内容）：

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://example.com', headless=True)
data = page.css('.js-loaded-content::text').getall()
```

### 等待特定元素 {#wait-for-specific-element}

```python
page = DynamicFetcher.fetch(
    'https://example.com',
    wait_selector=('.results', 'visible'),
    network_idle=True,
)
```

### 禁用资源以提升速度 {#disable-resources-for-speed}

阻止字体、图片、媒体、样式表（约快 25%）：

```python
from scrapling.fetchers import DynamicSession

with DynamicSession(headless=True, disable_resources=True, network_idle=True) as session:
    page = session.fetch('https://example.com')
    items = page.css('.item::text').getall()
```

### 自定义页面自动化 {#custom-page-automation}

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

## Python：隐身模式（反爬虫绕过） {#python-stealth-mode-anti-bot-bypass}

针对受 Cloudflare 保护或指纹检测严格的网站：

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

### 隐身会话 {#stealth-session}

```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page1 = session.fetch('https://protected-site.com/page1')
    page2 = session.fetch('https://protected-site.com/page2')
```
## 元素选择 {#element-selection}

所有 fetcher 都会返回一个 `Selector` 对象，该对象包含以下方法：

### CSS 选择器 {#css-selectors}

```python
page.css('h1::text').get()              # 第一个 h1 文本
page.css('a::attr(href)').getall()      # 所有链接的 href
page.css('.quote .text::text').getall() # 嵌套选择
```

### XPath {#xpath}

```python
page.xpath('//div[@class="content"]/text()').getall()
page.xpath('//a/@href').getall()
```

### 查找方法 {#find-methods}

```python
page.find_all('div', class_='quote')       # 按标签 + 属性
page.find_by_text('Read more', tag='a')    # 按文本内容
page.find_by_regex(r'\$\d+\.\d{2}')       # 按正则表达式模式
```

### 相似元素 {#similar-elements}

查找结构相似的元素（适用于产品列表等）：

```python
first_product = page.css('.product')[0]
all_similar = first_product.find_similar()
```

### 导航 {#navigation}

```python
el = page.css('.target')[0]
el.parent                # 父元素
el.children              # 子元素
el.next_sibling          # 下一个兄弟元素
el.prev_sibling          # 上一个兄弟元素
```

## Python：爬虫框架 {#python-spider-framework}

用于多页面爬取并跟随链接：

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

### 多会话爬虫 {#multi-session-spider}

将请求路由到不同的 fetcher 类型：

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

### 暂停/恢复爬取 {#pause-resume-crawling}

```python
spider = QuotesSpider(crawldir="./crawl_checkpoint")
spider.start()  # Ctrl+C 暂停，重新运行则从检查点恢复
```

## 注意事项 {#pitfalls}

- **需要安装浏览器**：pip install 后运行 `scrapling install` —— 否则 `DynamicFetcher` 和 `StealthyFetcher` 会失败
- **超时设置**：DynamicFetcher/StealthyFetcher 的超时时间以**毫秒**为单位（默认 30000），Fetcher 的超时时间以**秒**为单位
- **绕过 Cloudflare**：`solve_cloudflare=True` 会使抓取时间增加 5-15 秒 —— 仅在需要时启用
- **资源占用**：StealthyFetcher 会运行一个真实浏览器 —— 请限制并发使用
- **法律合规**：抓取前务必检查 robots.txt 和网站服务条款。本库仅用于教育和研究目的
- **Python 版本**：需要 Python 3.10+
