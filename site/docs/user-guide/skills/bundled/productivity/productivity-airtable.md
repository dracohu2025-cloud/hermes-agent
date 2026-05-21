---
title: "Airtable — 通过 curl 使用 Airtable REST API"
sidebar_label: "Airtable"
description: "通过 curl 使用 Airtable REST API"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="airtable"></a>
# Airtable

通过 curl 使用 Airtable REST API。支持记录的增删改查、过滤和更新插入。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/airtable` |
| 版本 | `1.1.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Airtable`, `Productivity`, `Database`, `API` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="airtable-bases-tables-records"></a>
# Airtable — 数据表、表格与记录

通过 `terminal` 工具，使用 `curl` 直接与 Airtable 的 REST API 交互。无需 MCP 服务器、无需 OAuth 流程、无需 Python SDK——只需要 `curl` 和一个个人访问令牌。

<a id="prerequisites"></a>
## 前置条件

1. 在 https://airtable.com/create/tokens 创建一个**个人访问令牌（PAT）**（令牌以 `pat...` 开头）。
2. 授予以下最小权限范围：
   - `data.records:read` — 读取行
   - `data.records:write` — 创建/更新/删除行
   - `schema.bases:read` — 列出数据表和表格
3. **重要：** 在同一令牌 UI 中，将你要访问的每个数据表添加到令牌的**访问**列表中。PAT 是按数据表划分范围的——一个有效的令牌在错误的数据表上会返回 `403`。
4. 将令牌存储在 `~/.hermes/.env` 中（或通过 `hermes setup` 设置）：
   ```
   AIRTABLE_API_KEY=pat_your_token_here
   ```

> 注意：旧的 `key...` API 密钥已于 2024 年 2 月弃用。现在只支持 PAT 和 OAuth 令牌。

<a id="api-basics"></a>
## API 基础

- **端点：** `https://api.airtable.com/v0`
- **认证头：** `Authorization: Bearer $AIRTABLE_API_KEY`
- **所有请求** 使用 JSON（任何 POST/PATCH/PUT 请求体都需要 `Content-Type: application/json`）。
- **对象 ID：** 数据表 `app...`，表格 `tbl...`，记录 `rec...`，字段 `fld...`。ID 永远不会改变；名称可以。在自动化中优先使用 ID。
- **速率限制：** 每个数据表每秒 5 个请求。收到 `429` 响应 → 退避。对单个数据表的突发请求会被限流。

基础 curl 模式：
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=5" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

`-s` 参数会抑制 curl 的进度条——每次调用都保持此设置，以便工具输出对 Hermes 保持整洁。通过 `python3 -m json.tool`（始终可用）或 `jq`（如果已安装）管道输出，以获得可读的 JSON。

<a id="field-types-request-body-shapes"></a>
## 字段类型（请求体格式）

| 字段类型 | 写入格式 |
|---|---|
| 单行文本 | `"Name": "hello"` |
| 多行文本 | `"Notes": "multi\nline"` |
| 数字 | `"Score": 42` |
| 复选框 | `"Done": true` |
| 单选 | `"Status": "Todo"`（除非 `typecast: true`，否则名称必须已存在） |
| 多选 | `"Tags": ["urgent", "bug"]` |
| 日期 | `"Due": "2026-04-01"` |
| 日期时间（UTC） | `"At": "2026-04-01T14:30:00.000Z"` |
| URL / 邮箱 / 电话 | `"Link": "https://…"` |
| 附件 | `"Files": [{"url": "https://…"}]`（Airtable 会抓取并重新托管） |
| 关联记录 | `"Owner": ["recXXXXXXXXXXXXXX"]`（记录 ID 数组） |
| 用户 | `"AssignedTo": {"id": "usrXXXXXXXXXXXXXX"}` |
在 create/update 请求体的顶层传递 `"typecast": true`，可以让 Airtable 自动转换值（例如，动态创建新的选择选项，将 `"42"` 转换为 `42`）。

<a id="common-queries"></a>
## 常见查询

<a id="list-bases-the-token-can-see"></a>
### 列出 token 可见的 bases
```bash
curl -s "https://api.airtable.com/v0/meta/bases" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

<a id="list-tables-schema-for-a-base"></a>
### 列出某个 base 的表格和 schema
```bash
curl -s "https://api.airtable.com/v0/meta/bases/$BASE_ID/tables" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
在修改数据前使用此命令——可以确认确切的字段名和 ID，显示选择字段的 `options.choices`，并展示主字段名称。

<a id="list-records-first-10"></a>
### 列出记录（前 10 条）
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=10" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

<a id="get-a-single-record"></a>
### 获取单条记录
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

<a id="filter-records-filterbyformula"></a>
### 过滤记录（filterByFormula）
Airtable 公式必须进行 URL 编码。让 Python 标准库来做——永远不要手动编码：
```bash
FORMULA="{Status}='Todo'"
ENC=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$FORMULA")
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?filterByFormula=$ENC&maxRecords=20" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

有用的公式模式：
- 精确匹配：`{Email}='user@example.com'`
- 包含：`FIND('bug', LOWER({Title}))`
- 多条件：`AND({Status}='Todo', {Priority}='High')`
- 或条件：`OR({Owner}='alice', {Owner}='bob')`
- 非空：`NOT({Assignee}='')`
- 日期比较：`IS_AFTER({Due}, TODAY())`

<a id="sort-select-specific-fields"></a>
### 排序 + 选择特定字段
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?sort%5B0%5D%5Bfield%5D=Priority&sort%5B0%5D%5Bdirection%5D=asc&fields%5B%5D=Name&fields%5B%5D=Status" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
查询参数中的方括号必须进行 URL 编码（`%5B` / `%5D`）。

<a id="use-a-named-view"></a>
### 使用命名视图
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?view=Grid%20view&maxRecords=50" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
视图会在服务端应用其保存的过滤和排序条件。

<a id="common-mutations"></a>
## 常见修改操作

<a id="create-a-record"></a>
### 创建一条记录
```bash
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Name":"New task","Status":"Todo","Priority":"High"}}' | python3 -m json.tool
```

<a id="create-up-to-10-records-in-one-call"></a>
### 一次调用创建最多 10 条记录
```bash
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "typecast": true,
    "records": [
      {"fields": {"Name": "Task A", "Status": "Todo"}},
      {"fields": {"Name": "Task B", "Status": "In progress"}}
    ]
  }' | python3 -m json.tool
```
批量端点每次请求最多 **10 条记录**。对于更大的插入操作，请以 10 条为一批进行循环，并短暂休眠以遵守 5 次请求/秒/base 的限制。
<a id="update-a-record-patch-merges-preserves-unchanged-fields"></a>
### 更新一条记录（PATCH — 合并，保留未修改的字段）
```bash
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Status":"Done"}}' | python3 -m json.tool
```

<a id="upsert-by-a-merge-field-no-id-needed"></a>
### 按合并字段进行 Upsert（无需 ID）
```bash
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "performUpsert": {"fieldsToMergeOn": ["Email"]},
    "records": [
      {"fields": {"Email": "user@example.com", "Status": "Active"}}
    ]
  }' | python3 -m json.tool
```
`performUpsert` 会为合并字段值不存在的新记录创建记录，并对合并字段值已存在的记录执行 PATCH 操作。非常适合幂等同步场景。

<a id="delete-a-record"></a>
### 删除一条记录
```bash
curl -s -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

<a id="delete-up-to-10-records-in-one-call"></a>
### 一次调用删除最多 10 条记录
```bash
curl -s -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE?records%5B%5D=rec1&records%5B%5D=rec2" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

<a id="pagination"></a>
## 分页

列表端点每次最多返回 **100 条记录**。如果响应中包含 `"offset": "..."`，则在下次调用时传回该值。循环请求直到 offset 字段消失：

```bash
OFFSET=""
while :; do
  URL="https://api.airtable.com/v0/$BASE_ID/$TABLE?pageSize=100"
  [ -n "$OFFSET" ] && URL="$URL&offset=$OFFSET"
  RESP=$(curl -s "$URL" -H "Authorization: Bearer $AIRTABLE_API_KEY")
  echo "$RESP" | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(r["id"], r["fields"].get("Name","")) for r in d["records"]]'
  OFFSET=$(echo "$RESP" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("offset",""))')
  [ -z "$OFFSET" ] && break
done
```

<a id="typical-hermes-workflow"></a>
## 典型的 Hermes Workflow

1. **确认认证。** `curl -s -o /dev/null -w "%{http_code}\n" https://api.airtable.com/v0/meta/bases -H "Authorization: Bearer $AIRTABLE_API_KEY"` — 预期返回 `200`。
2. **找到 Base。** 列出所有 Base（使用上一步的命令）或者如果 token 缺少 `schema.bases:read` 权限，直接向用户询问 `app...` ID。
3. **检查 Schema。** `GET /v0/meta/bases/$BASE_ID/tables` — 在对数据进行任何修改之前，在会话中本地缓存准确的字段名和主字段名。
4. **先读取再写入。** 对于“更新 X 当 Y 条件满足”的情况，先用 `filterByFormula` 解析出 `rec...` ID，然后再执行 `PATCH /v0/$BASE_ID/$TABLE/$RECORD_ID`。永远不要猜测记录 ID。
5. **批量写入。** 将相关的创建操作合并到一次最多 10 条记录的 POST 中，以保持在 5 req/sec 的配额内。
6. **破坏性操作。** 删除操作无法通过 API 撤销。如果用户说“删除所有 X”，先输出过滤条件 + 记录数量，得到确认后再执行。

<a id="pitfalls"></a>
## 注意事项

- **`filterByFormula` 必须进行 URL 编码。** 包含空格或非 ASCII 字符的字段名也需要编码（`{My Field}` → `%7BMy%20Field%7D`）。使用 Python 标准库（参考上面的模式）——永远不要手动转义。
- **空字段不会出现在响应中。** 缺少 `"Assignee"` 键并不表示该字段不存在——而是表示该记录的该字段为空。在断定字段缺失之前，请先检查 Schema（步骤 3）。
- **PATCH vs PUT。** `PATCH` 将提供的字段合并到记录中。`PUT` 会完全替换记录，并清除你没有包含的任何字段。默认使用 `PATCH`。
- **单选选项必须已经存在。** 当 `Shipping` 不在选项列表中时写入 `"Status": "Shipping"` 会报错 `INVALID_MULTIPLE_CHOICE_OPTIONS`，除非你传递了 `"typecast": true`（此时会自动创建该选项）。
- **按 Base 分配 Token 作用域。** 如果某个 Base 返回 `403`，而其他 Base 正常工作，说明该 token 的访问列表不包含该 Base——不是作用域或认证问题。让用户前往 https://airtable.com/create/tokens 添加权限。
- **速率限制是按 Base 而非按 Token 的。** `baseA` 上 5 req/sec 和 `baseB` 上 5 req/sec 是没问题的；但仅在 `baseA` 上达到 6 req/sec 就会被限流。注意在 `429` 响应中检查 `Retry-After` 头部。
<a id="important-notes-for-hermes"></a>
## Hermes 的重要注意事项

- **务必使用 `terminal` 工具配合 `curl`。** 不要使用 `web_extract`（它无法发送认证头）或 `browser_navigate`（需要 UI 认证且速度慢）。
- **当此技能加载后，`AIRTABLE_API_KEY` 会自动从 `~/.hermes/.env` 流入子进程** —— 无需在每个 `curl` 调用前重新导出。
- **小心转义公式中的花括号。** 在 heredoc 主体中，`{Status}` 是字面量。在 shell 参数中，`{Status}` 在 `{...}` 花括号展开上下文之外是安全的——但在将动态字符串拼接到 URL 之前，先通过 `python3 urllib.parse.quote` 传递。
- **使用 `python3 -m json.tool`（始终可用）进行美化输出**，而不是 `jq`（可选）。只有当需要过滤/投影时才使用 `jq`。
- **分页是按页的，不是全局的。** Airtable 的 100 条记录上限是硬限制，无法提高。循环使用 `offset` 直到该字段消失。
- **读取非 2xx 响应中的 `errors` 数组**——Airtable 会返回结构化的错误码，如 `AUTHENTICATION_REQUIRED`、`INVALID_PERMISSIONS`、`MODEL_ID_NOT_FOUND`、`INVALID_MULTIPLE_CHOICE_OPTIONS`，这些能准确告诉你问题所在。
