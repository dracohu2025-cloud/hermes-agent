---
title: "Notion — Notion API + ntn CLI：页面、数据库、Markdown、Workers"
sidebar_label: "Notion"
description: "Notion API + ntn CLI：页面、数据库、Markdown、Workers"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="notion"></a>
# Notion

Notion API + ntn CLI：页面、数据库、Markdown、Workers。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内建（默认安装） |
| 路径 | `skills/productivity/notion` |
| 版本 | `2.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Notion`, `Productivity`, `Notes`, `Database`, `API`, `CLI`, `Workers` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Notion

通过两种方式与 Notion 交互。同一集成令牌对两者都有效——根据可用工具选择。

◆ **`ntn` CLI** — Notion 的官方 CLI。语法更简短，支持单行文件上传，Workers 必需。截至 2026 年 5 月仅适用于 macOS + Linux（Windows 支持“即将推出”）。**默认使用（如果已安装）。**
◆ **HTTP + curl** — 适用于所有平台，包括 Windows。**默认回退方案**（当 `ntn` 未安装时）。

<a id="setup"></a>
## 设置

<a id="1-get-an-integration-token-required-for-both-paths"></a>
### 1. 获取集成令牌（两种方式都需要）

1. 在 https://notion.so/my-integrations 创建一个集成
2. 复制 API 密钥（以 `ntn_` 或 `secret_` 开头）
3. 存储在 `~/.hermes/.env` 中：
   ```
   NOTION_API_KEY=ntn_your_key_here
   ```
4. **在 Notion 中将目标页面/数据库共享给该集成**：页面菜单 `...` → `连接到` → 你的集成名称。若不操作，API 将对该页面返回 404（即使页面实际存在）。

<a id="2-install-ntn-preferred-path-on-macos-linux"></a>
### 2. 安装 `ntn`（macOS / Linux 上的首选方式）

```bash
# 推荐
curl -fsSL https://ntn.dev | bash

# 或者通过 npm（需要 Node 22+，npm 10+）
npm install --global ntn

ntn --version    # 验证
```

**跳过 `ntn login`——直接使用集成令牌。** 这种方式无需浏览器，可无头运行：
```bash
export NOTION_API_TOKEN=$NOTION_API_KEY      # ntn 读取 NOTION_API_TOKEN
export NOTION_KEYRING=0                       # 不要尝试使用系统钥匙串
```

将这些导出添加到你的 shell 配置文件中（或者添加到 `~/.hermes/.env`），以便每个会话都能继承它们。

<a id="3-choose-path-at-runtime"></a>
### 3. 运行时选择方式

```bash
if command -v ntn >/dev/null 2>&1; then
  # 使用 ntn
else
  # 回退到 curl
fi
```

Windows 用户：在原生 `ntn` 发布之前，完全跳过第 2 步——方式 B 可以正常工作。如果现在就想用 CLI 的便利性，可以在 WSL2 中安装 `ntn`。

<a id="api-basics"></a>
## API 基础

所有 HTTP 请求必须携带 `Notion-Version: 2025-09-03`。`ntn` 会自动处理这个。在此版本中，用户通常称为“数据库”的东西，在 API 中被称为**数据源**。

<a id="path-a-ntn-cli-preferred-macos-linux"></a>
## 路径 A — `ntn` CLI（首选，macOS / Linux）

<a id="raw-api-calls-shorthand-for-curl"></a>
### 原始 API 调用（curl 的简写）
```bash
ntn api v1/users                                  # GET
ntn api v1/pages parent[page_id]=abc123 \         # POST，内联 body
  properties[title][0][text][content]="Notes"
ntn api v1/pages/abc123 -X PATCH archived:=true   # PATCH；`:=` 表示非字符串（布尔/数字/null）
```

语法说明：
- `key=value` — 字符串字段
- `key[nested]=value` — 嵌套对象字段
- `key:=value` — 类型赋值（布尔值、数字、null、数组）
<a id="search"></a>
### 搜索
```bash
ntn api v1/search query="page title"
```

<a id="read-page-metadata"></a>
### 读取页面元数据
```bash
ntn api v1/pages/{page_id}
```

<a id="read-page-as-markdown-agent-friendly"></a>
### 以 Markdown 格式读取页面（对 Agent 友好）
```bash
ntn api v1/pages/{page_id}/markdown
```

<a id="read-page-content-as-blocks"></a>
### 以块形式读取页面内容
```bash
ntn api v1/blocks/{page_id}/children
```

<a id="create-page-from-markdown"></a>
### 从 Markdown 创建页面
```bash
ntn api v1/pages \
  parent[page_id]=xxx \
  properties[title][0][text][content]="会议笔记" \
  markdown="# 议程

- Q3 路线图
- 招聘"
```

<a id="patch-a-page-with-markdown"></a>
### 用 Markdown 更新页面
```bash
ntn api v1/pages/{page_id}/markdown -X PATCH \
  markdown="## 更新

原型已发布。"
```

<a id="query-a-database-data-source"></a>
### 查询数据库（数据源）
```bash
ntn api v1/data_sources/{data_source_id}/query -X POST \
  filter[property]=状态 filter[select][equals]=活跃
```

对于包含 `sorts`、多个过滤子句或复合逻辑的复杂查询，可以通过管道传入 JSON：
```bash
echo '{"filter": {"property": "状态", "select": {"equals": "活跃"}}, "sorts": [{"property": "日期", "direction": "降序"}]}' | \
  ntn api v1/data_sources/{data_source_id}/query -X POST --json -
```

<a id="file-uploads-one-liner-biggest-cli-win"></a>
### 文件上传（一行命令 — CLI 最大优势）
```bash
ntn files create < photo.png
ntn files create --external-url https://example.com/photo.png
ntn files list
```

对比传统的三步 HTTP 流程（创建上传 → PUT 字节 → 引用）。

<a id="useful-env-vars"></a>
### 有用的环境变量
| 变量 | 作用 |
|---|---|
| `NOTION_API_TOKEN` | 认证令牌（覆盖钥匙串）— 设置为你的集成令牌 |
| `NOTION_KEYRING=0` | 使用 `~/.config/notion/auth.json` 中的文件凭据，而非系统钥匙串 |
| `NOTION_WORKSPACE_ID` | 跳过工作区选择提示 |

<a id="path-b-http-curl-cross-platform-default-on-windows"></a>
## 路径 B — HTTP + curl（跨平台，Windows 默认）

所有请求都遵循此模式：

```bash
curl -s -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

在 Windows 上，Windows 10+ 自带的 `curl` 可直接使用。PowerShell 用户也可以使用 `Invoke-RestMethod`。

### 搜索
```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'
```

### 读取页面元数据
```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 以 Markdown 格式读取页面（对 Agent 友好）

比块 JSON 更容易喂给模型。

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

<a id="read-page-content-as-blocks-when-you-need-structure"></a>
### 以块形式读取页面内容（需要结构时）
```bash
curl -s "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 从 Markdown 创建页面

`POST /v1/pages` 接受 `markdown` 主体参数。

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "properties": {"title": [{"text": {"content": "会议笔记"}}]},
    "markdown": "# 议程\n\n- Q3 路线图\n- 招聘\n\n## 决定\n- 周五发布 MVP"
  }'
```
<a id="patch-a-page-with-markdown"></a>
### 用 Markdown 更新页面
```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"markdown": "## 更新\n\n原型已发货。"}'
```

<a id="create-page-in-a-database-typed-properties"></a>
### 在数据库中创建页面（带类型属性）
```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "新项目"}}]},
      "Status": {"select": {"name": "待办"}}
    }
  }'
```

<a id="query-a-database-data-source"></a>
### 查询数据库（数据源）
```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'
```

<a id="create-a-database"></a>
### 创建数据库
```bash
curl -s -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "title": [{"text": {"content": "我的数据库"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "待办"}, {"name": "已完成"}]}},
      "Date": {"date": {}}
    }
  }'
```

<a id="update-page-properties"></a>
### 更新页面属性
```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "已完成"}}}}'
```

<a id="append-blocks-to-a-page"></a>
### 向页面追加块
```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "来自 Hermes 的问候！"}}]}}
    ]
  }'
```

<a id="file-uploads-3-step-flow"></a>
### 文件上传（三步流程）
```bash
# 1. 创建上传
curl -s -X POST "https://api.notion.com/v1/file_uploads" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"filename": "photo.png", "content_type": "image/png"}'

# 2. 将字节 PUT 到上面返回的 upload_url
curl -s -X PUT "{upload_url}" --data-binary @photo.png

# 3. 在页面/块载荷中引用 {file_upload_id}
```

<a id="property-types"></a>
## 属性类型

数据库条目的常见属性格式：

- **标题：** `{"title": [{"text": {"content": "..."}}]}`
- **富文本：** `{"rich_text": [{"text": {"content": "..."}}]}`
- **单选：** `{"select": {"name": "Option"}}`
- **多选：** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **日期：** `{"date": {"start": "2026-01-15", "end": "2026-01-16"}}`
- **复选框：** `{"checkbox": true}`
- **数字：** `{"number": 42}`
- **URL：** `{"url": "https://..."}`
- **邮箱：** `{"email": "user@example.com"}`
- **关联：** `{"relation": [{"id": "page_id"}]}`
<a id="api-version-2025-09-03-databases-vs-data-sources"></a>
## API 版本 2025-09-03 — 数据库与数据源

- **数据库现已变为数据源。** 请使用 `/data_sources/` 端点进行查询和检索。
- **每个数据库包含两个 ID：** `database_id` 和 `data_source_id`。
  - `database_id` 用于创建页面：`parent: {"database_id": "..."}`
  - `data_source_id` 用于查询：`POST /v1/data_sources/{id}/query`
- 搜索返回的数据库对象为 `"object": "data_source"`，其中包含 `data_source_id` 字段。

<a id="notion-workers-advanced-requires-ntn"></a>
## Notion Workers（高级功能，需要 `ntn`）

Workers 是 Notion 为你托管的 TypeScript 程序。一个 Worker 可以暴露任意组合的以下功能：
- **同步（Syncs）** — 按计划（默认 30 分钟）从外部 API 拉取数据到 Notion 数据库。
- **工具（Tools）** — 作为可调用的工具出现在 Notion 的 Custom Agents 中。
- **Webhooks** — 接收来自外部服务（GitHub、Stripe 等）的 HTTP 事件并在 Notion 中执行操作。

**方案 / 平台限制：**
- CLI 在所有方案上均可使用。**部署 Workers 需要 Business 或 Enterprise 方案。**
- 截至 2026 年 5 月，`ntn` 仅支持 macOS/Linux。Windows 用户需要使用 WSL2 或等待原生支持。
- 至 2026 年 8 月 11 日免费；之后按 Notion 积分计费。

<a id="minimal-worker"></a>
### 最小 Worker

```bash
ntn workers new my-worker      # scaffold
cd my-worker
# Edit src/index.ts
ntn workers deploy --name my-worker
```

`src/index.ts`:
```typescript
import { Worker } from "@notionhq/workers";

const worker = new Worker();
export default worker;

worker.tool("greet", {
  title: "Greet a User",
  description: "Returns a friendly greeting",
  inputSchema: { type: "object", properties: { name: { type: "string" } }, required: ["name"] },
  execute: async ({ name }) => `Hello, ${name}!`,
});
```

<a id="webhook-capability"></a>
### Webhook 能力

```typescript
worker.webhook("onGithubPush", {
  title: "GitHub Push Handler",
  execute: async (events, { notion }) => {
    for (const event of events) {
      // event.body, event.rawBody (for signature verification), event.headers
      console.log("got delivery", event.deliveryId);
    }
  },
});
```

部署后：`ntn workers webhooks list` 会显示 Notion 生成的 URL。请将该 URL 视为机密 — 除非你添加了签名验证，否则任何知道该 URL 的人都可以 POST 事件。

<a id="worker-lifecycle-commands"></a>
### Worker 生命周期命令

```bash
ntn workers deploy
ntn workers list
ntn workers exec <capability-key> -d '{"name": "world"}'
ntn workers sync trigger <key>            # 立即运行同步
ntn workers sync pause <key>
ntn workers env set GITHUB_WEBHOOK_SECRET=...
ntn workers runs list                     # 最近的调用记录
ntn workers runs logs <run-id>
ntn workers webhooks list
```

当需要构建一个 Worker 时，请使用 `ntn workers new` 进行脚手架搭建，在 `src/index.ts` 中编写代码，使用 `ntn workers env set` 设置机密，然后部署。Notion 的文档（https://developers.notion.com/workers）涵盖了完整的 API。

<a id="notion-flavored-markdown-used-by-markdown-endpoints"></a>
## Notion 风格的 Markdown（由 `/markdown` 端点使用）

标准 CommonMark 加上类 XML 标签以支持 Notion 特定的块。使用**制表符**进行缩进。

**CommonMark 之外的块：**
```
<callout icon="🎯" color="blue_bg">
	在 **周五** 之前交付 MVP。
</callout>

<details color="gray">
<summary>切换标题</summary>
	子内容缩进一个制表符
</details>

<columns>
	<column>左侧</column>
	<column>右侧</column>
</columns>

<table_of_contents color="gray"/>
```
**内联元素：**
- 提及：`&lt;mention-user url="..."/&gt;`、`&lt;mention-page url="..."&gt;标题</mention-page>`、`&lt;mention-date start="2026-05-15"/&gt;`
- 下划线：`&lt;span underline="true"&gt;文本</span>`
- 颜色：`&lt;span color="blue"&gt;文本</span>`，或在首行使用块级 `{color="blue"}`
- 数学公式：行内 `$x^2$`，块级 `$$ ... $$`
- 引用：`[^https://example.com]`

**颜色：** `gray brown orange yellow green blue purple pink red`，以及作为背景色的 `*_bg` 变体。

标题 5/6 级会折叠为 H4。多个 `>` 行会渲染为独立的引用块——如需多行引用，请在单个 `>` 内使用 `&lt;br&gt;`。

<a id="choosing-the-right-path"></a>
## 选择正确的路径

| 任务 | mac / Linux | Windows |
|---|---|---|
| 读写页面、搜索、查询数据库 | `ntn api ...` | curl |
| 读取页面供 Agent 总结 | `ntn api v1/pages/{id}/markdown` | curl `/markdown` 端点 |
| 上传文件 | `ntn files create < 文件` | 3 步 HTTP 流程 |
| 一次性 API 探索 | `ntn api ...` | curl |
| 构建由 Notion 托管的同步 / webhook / Agent 工具 | `ntn workers ...` | WSL2 + `ntn workers ...` |

<a id="notes"></a>
## 说明

- 页面/数据库 ID 是 UUID（带或不带连字符均可）。
- 速率限制：平均约 3 次请求/秒。CLI 不受此限制。
- API 无法设置数据库**视图**过滤器——这只能在 UI 中完成。
- 创建数据源以嵌入页面时，使用 `"is_inline": true`。
- 使用 curl 时始终加 `-s` 以隐藏进度条（使 Agent 输出更干净）。
- 读取时通过 `jq` 管道处理 JSON：`... | jq '.results[0].properties'`。
- Notion 现在还提供了一个 MCP 服务器（`Notion MCP`，在数据库操作上比旧版本节省约 91% 的 token）——如果你希望从会话内部流式访问 Notion，可以通过 Hermes 的 MCP 支持来连接它，但上述路径对于大多数一次性任务已经足够。
