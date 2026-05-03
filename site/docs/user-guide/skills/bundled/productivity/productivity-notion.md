---
title: "Notion — 通过 curl 使用 Notion API：页面、数据库、块、搜索"
sidebar_label: "Notion"
description: "通过 curl 使用 Notion API：页面、数据库、块、搜索"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Notion {#notion}

通过 curl 使用 Notion API：页面、数据库、块、搜索。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/notion` |
| 版本 | `1.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 标签 | `Notion`、`生产力`、`笔记`、`数据库`、`API` |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Notion API {#notion-api}

通过 curl 使用 Notion API 来创建、读取、更新页面、数据库（数据源）和块。无需额外工具——只需 curl 和一个 Notion API 密钥。

## 前提条件 {#prerequisites}

1. 在 https://notion.so/my-integrations 创建一个集成
2. 复制 API 密钥（以 `ntn_` 或 `secret_` 开头）
3. 将其存储在 `~/.hermes/.env` 中：
   ```
   NOTION_API_KEY=ntn_your_key_here
   ```
4. **重要：** 在 Notion 中与你的集成共享目标页面/数据库（点击 "..." → "连接到" → 你的集成名称）

## API 基础 {#api-basics}

所有请求都使用此模式：

```bash
curl -s -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

`Notion-Version` 头部是必需的。此技能使用 `2025-09-03`（最新版本）。在此版本中，数据库在 API 中被称为“数据源”。

## 常用操作 {#common-operations}

### 搜索 {#search}

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'
```

### 获取页面 {#get-page}

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 获取页面内容（块） {#get-page-content-blocks}

```bash
curl -s "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 在数据库中创建页面 {#create-page-in-a-database}

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}}
    }
  }'
```

### 查询数据库 {#query-a-database}

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

### 创建数据库 {#create-a-database}

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "title": [{"text": {"content": "My Database"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
      "Date": {"date": {}}
    }
  }'
```
### 更新页面属性 {#update-page-properties}

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

### 向页面添加内容 {#add-content-to-a-page}

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello from Hermes!"}}]}}
    ]
  }'
```

## 属性类型 {#property-types}

数据库条目中常见的属性格式：

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

## API 版本 2025-09-03 的主要差异 {#key-differences-in-api-version-2025-09-03}

- **数据库 → 数据源：** 查询和检索使用 `/data_sources/` 端点
- **两个 ID：** 每个数据库同时拥有 `database_id` 和 `data_source_id`
  - 创建页面时使用 `database_id`（`parent: {"database_id": "..."}`）
  - 查询时使用 `data_source_id`（`POST /v1/data_sources/{id}/query`）
- **搜索结果：** 数据库以 `"object": "data_source"` 形式返回，并附带其 `data_source_id`

## 注意事项 {#notes}

- 页面/数据库 ID 是 UUID（带或不带连字符均可）
- 速率限制：约每秒 3 个请求
- API 无法设置数据库视图筛选条件——这仅限 UI 操作
- 创建数据源时使用 `is_inline: true` 可将其嵌入页面
- 在 curl 中添加 `-s` 标志可隐藏进度条（让 Hermes 输出更干净）
- 通过管道将输出传给 `jq` 可得到可读的 JSON：`... | jq '.results[0].properties'`
