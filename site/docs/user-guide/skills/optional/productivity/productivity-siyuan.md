---
title: "Siyuan"
sidebar_label: "Siyuan"
description: "通过 curl 在自托管知识库中搜索、读取、创建和管理块与文档的 SiYuan 笔记 API"
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="siyuan"></a>
# Siyuan

通过 curl 在自托管知识库中搜索、读取、创建和管理块与文档的 SiYuan 笔记 API。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/siyuan` 安装 |
| 路径 | `optional-skills/productivity/siyuan` |
| 版本 | `1.0.0` |
| 作者 | FEUAZUR |
| 许可证 | MIT |
| 支持平台 | linux, macos, windows |
| 标签 | `SiYuan`, `Notes`, `Knowledge Base`, `PKM`, `API` |
| 相关技能 | [`obsidian`](/user-guide/skills/bundled/note-taking/note-taking-obsidian), [`notion`](/user-guide/skills/bundled/productivity/productivity-notion) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在该技能激活时看到的指令。
:::

<a id="siyuan-note-api"></a>
# SiYuan 笔记 API

通过 curl 使用 [SiYuan](https://github.com/siyuan-note/siyuan) 内核 API 在自托管知识库中搜索、读取、创建、更新和删除块与文档。无需额外工具——只需 curl 和一个 API 令牌。

<a id="prerequisites"></a>
## 先决条件

1. 安装并运行 SiYuan（桌面版或 Docker）
2. 获取你的 API 令牌：**设置 > 关于 > API 令牌**
3. 将其存储在 `~/.hermes/.env` 中：
   ```
   SIYUAN_TOKEN=your_token_here
   SIYUAN_URL=http://127.0.0.1:6806
   ```
   如果未设置，`SIYUAN_URL` 默认值为 `http://127.0.0.1:6806`。

<a id="api-basics"></a>
## API 基础

所有 SiYuan API 调用都是 **带有 JSON 请求体的 POST 请求**。每个请求遵循以下模式：

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/..." \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"param": "value"}'
```

响应为 JSON，结构如下：
```json
{"code": 0, "msg": "", "data": { ... }}
```
`code: 0` 表示成功。其他任何值都是错误——请查看 `msg` 了解详情。

**ID 格式：** SiYuan ID 看起来像 `20210808180117-6v0mkxr`（14 位时间戳 + 7 位字母数字字符）。

<a id="quick-reference"></a>
## 快速参考

| 操作 | 端点 |
|-----------|----------|
| 全文搜索 | `/api/search/fullTextSearchBlock` |
| SQL 查询 | `/api/query/sql` |
| 读取块 | `/api/block/getBlockKramdown` |
| 读取子块 | `/api/block/getChildBlocks` |
| 获取路径 | `/api/filetree/getHPathByID` |
| 获取属性 | `/api/attr/getBlockAttrs` |
| 列出笔记本 | `/api/notebook/lsNotebooks` |
| 列出文档 | `/api/filetree/listDocsByPath` |
| 创建笔记本 | `/api/notebook/createNotebook` |
| 创建文档 | `/api/filetree/createDocWithMd` |
| 追加块 | `/api/block/appendBlock` |
| 更新块 | `/api/block/updateBlock` |
| 重命名文档 | `/api/filetree/renameDocByID` |
| 设置属性 | `/api/attr/setBlockAttrs` |
| 删除块 | `/api/block/deleteBlock` |
| 删除文档 | `/api/filetree/removeDocByID` |
| 导出为 Markdown | `/api/export/exportMdContent` |
<a id="common-operations"></a>
## 常见操作

<a id="search-full-text"></a>
### 搜索（全文）

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/search/fullTextSearchBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "meeting notes", "page": 0}' | jq '.data.blocks[:5]'
```

<a id="search-sql"></a>
### 搜索（SQL）

直接查询块数据库。只有 SELECT 语句是安全的。

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/query/sql" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stmt": "SELECT id, content, type, box FROM blocks WHERE content LIKE '\''%keyword%'\'' AND type='\''p'\'' LIMIT 20"}' | jq '.data'
```

有用的列：`id`、`parent_id`、`root_id`、`box`（笔记本 ID）、`path`、`content`、`type`、`subtype`、`created`、`updated`。

<a id="read-block-content"></a>
### 读取块内容

以 Kramdown（类 Markdown 格式）返回块内容。

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/getBlockKramdown" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data.kramdown'
```

<a id="read-child-blocks"></a>
### 读取子块

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/getChildBlocks" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data'
```

<a id="get-human-readable-path"></a>
### 获取人类可读路径

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/getHPathByID" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data'
```

<a id="get-block-attributes"></a>
### 获取块属性

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/attr/getBlockAttrs" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data'
```

<a id="list-notebooks"></a>
### 列出笔记本

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/notebook/lsNotebooks" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.data.notebooks[] | {id, name, closed}'
```

<a id="list-documents-in-a-notebook"></a>
### 列出笔记本中的文档

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/listDocsByPath" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notebook": "NOTEBOOK_ID", "path": "/"}' | jq '.data.files[] | {id, name}'
```

<a id="create-a-document"></a>
### 创建文档

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/createDocWithMd" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook": "NOTEBOOK_ID",
    "path": "/Meeting Notes/2026-03-22",
    "markdown": "# Meeting Notes\n\n- Discussed project timeline\n- Assigned tasks"
  }' | jq '.data'
```

<a id="create-a-notebook"></a>
### 创建笔记本

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/notebook/createNotebook" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My New Notebook"}' | jq '.data.notebook.id'
```
<a id="append-block-to-document"></a>
### 在文档末尾追加块

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/appendBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parentID": "DOCUMENT_OR_BLOCK_ID",
    "data": "New paragraph added at the end.",
    "dataType": "markdown"
  }' | jq '.data'
```

另有：`/api/block/prependBlock`（参数相同，在开头插入）和 `/api/block/insertBlock`（使用 `previousID` 代替 `parentID`，在指定块之后插入）。

<a id="update-block-content"></a>
### 更新块内容

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/updateBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "BLOCK_ID",
    "data": "Updated content here.",
    "dataType": "markdown"
  }' | jq '.data'
```

<a id="rename-a-document"></a>
### 重命名文档

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/renameDocByID" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "DOCUMENT_ID", "title": "New Title"}'
```

<a id="set-block-attributes"></a>
### 设置块属性

自定义属性必须以 `custom-` 开头：

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/attr/setBlockAttrs" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "BLOCK_ID",
    "attrs": {
      "custom-status": "reviewed",
      "custom-priority": "high"
    }
  }'
```

<a id="delete-a-block"></a>
### 删除块

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/deleteBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "BLOCK_ID"}'
```

要删除整个文档：使用 `/api/filetree/removeDocByID`，参数为 `{"id": "DOC_ID"}`。
要删除笔记本：使用 `/api/notebook/removeNotebook`，参数为 `{"notebook": "NOTEBOOK_ID"}`。

<a id="export-document-as-markdown"></a>
### 将文档导出为 Markdown

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/export/exportMdContent" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "DOCUMENT_ID"}' | jq -r '.data.content'
```

<a id="block-types"></a>
## 块类型

SQL 查询中常见的 `type` 值：

| 类型 | 说明 |
|------|------|
| `d` | 文档（根块） |
| `p` | 段落 |
| `h` | 标题 |
| `l` | 列表 |
| `i` | 列表项 |
| `c` | 代码块 |
| `m` | 数学块 |
| `t` | 表格 |
| `b` | 引用块 |
| `s` | 超级块 |
| `html` | HTML 块 |

<a id="pitfalls"></a>
## 注意事项

- **所有端点都是 POST** —— 即使是只读操作也是如此。不要使用 GET。
- **SQL 安全**：只使用 SELECT 查询。INSERT/UPDATE/DELETE/DROP 有危险，绝不要发送。
- **ID 校验**：ID 符合模式 `YYYYMMDDHHmmss-xxxxxxx`。拒绝其他任何格式。
- **错误响应**：在处理 `data` 之前，始终检查响应中的 `code != 0`。
- **大型文档**：块内容和导出结果可能非常大。在 SQL 中使用 `LIMIT`，并通过 `jq` 管道只提取你需要的内容。
- **笔记本 ID**：当处理特定笔记本时，先通过 `lsNotebooks` 获取它的 ID。
<a id="alternative-mcp-server"></a>
## 备选方案：MCP Server

如果你更喜欢原生集成而非 curl，请安装 SiYuan MCP server：

```yaml
# In ~/.hermes/config.yaml under mcp_servers:
mcp_servers:
  siyuan:
    command: npx
    args: ["-y", "@porkll/siyuan-mcp"]
    env:
      SIYUAN_TOKEN: "your_token"
      SIYUAN_URL: "http://127.0.0.1:6806"
```
