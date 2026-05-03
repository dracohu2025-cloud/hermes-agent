---
title: "Airtable — 通过 curl 使用 Airtable REST API"
sidebar_label: "Airtable"
description: "通过 curl 使用 Airtable REST API"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Airtable {#airtable}

通过 curl 使用 Airtable REST API。支持记录的增删改查、过滤、upsert 操作。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/airtable` |
| 版本 | `1.1.0` |
| 作者 | community |
| 许可证 | MIT |
| 标签 | `Airtable`, `Productivity`, `Database`, `API` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会看到这些指令。
:::

# Airtable — 基础、表格与记录 {#airtable-bases-tables-records}

通过 `terminal` 工具直接使用 `curl` 操作 Airtable 的 REST API。无需 MCP 服务器、无需 OAuth 流程、无需 Python SDK——只需 `curl` 和一个个人访问令牌。

## 前置条件 {#prerequisites}

1. 在 https://airtable.com/create/tokens 创建一个**个人访问令牌 (PAT)**（令牌以 `pat...` 开头）。
2. 授予以下权限（最低要求）：
   - `data.records:read` — 读取行
   - `data.records:write` — 创建/更新/删除行
   - `schema.bases:read` — 列出 base 和 table
3. **重要：** 在同一令牌界面中，将你要访问的每个 base 添加到令牌的**访问**列表中。PAT 是按 base 限定的——有效的令牌如果用在错误的 base 上会返回 `403`。
4. 将令牌存储在 `~/.hermes/.env` 中（或通过 `hermes setup` 设置）：
   ```
   AIRTABLE_API_KEY=pat_your_token_here
   ```

> 注意：旧的 `key...` API 密钥已于 2024 年 2 月弃用。现在只支持 PAT 和 OAuth 令牌。

## API 基础 {#api-basics}

- **端点：** `https://api.airtable.com/v0`
- **认证头：** `Authorization: Bearer $AIRTABLE_API_KEY`
- **所有请求** 使用 JSON（任何 POST/PATCH/PUT 请求体都需要 `Content-Type: application/json`）。
- **对象 ID：** base 为 `app...`，table 为 `tbl...`，记录为 `rec...`，字段为 `fld...`。ID 永远不会改变，名称可以改变。在自动化中优先使用 ID。
- **速率限制：** 每个 base 每秒 5 个请求。收到 `429` 时请退避。对单个 base 的突发请求会被限流。

基础 curl 模式：
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=5" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

`-s` 用于抑制 curl 的进度条——每次调用都保持此设置，以便工具输出对 Hermes 保持整洁。通过 `python3 -m json.tool`（始终可用）或 `jq`（如果已安装）管道输出，以获得可读的 JSON。

## 字段类型（请求体格式） {#field-types-request-body-shapes}

| 字段类型 | 写入格式 |
|---|---|
| Single line text | `"Name": "hello"` |
| Long text | `"Notes": "multi\nline"` |
| Number | `"Score": 42` |
| Checkbox | `"Done": true` |
| Single select | `"Status": "Todo"`（除非 `typecast: true`，否则名称必须已存在） |
| Multi-select | `"Tags": ["urgent", "bug"]` |
| Date | `"Due": "2026-04-01"` |
| DateTime (UTC) | `"At": "2026-04-01T14:30:00.000Z"` |
| URL / Email / Phone | `"Link": "https://…"` |
| Attachment | `"Files": [{"url": "https://…"}]`（Airtable 会抓取并重新托管） |
| Linked record | `"Owner": ["recXXXXXXXXXXXXXX"]`（记录 ID 数组） |
| User | `"AssignedTo": {"id": "usrXXXXXXXXXXXXXX"}` |
在 create/update 请求体的顶层传入 `"typecast": true`，可让 Airtable 自动转换值的类型（例如动态创建新的选项，或将 `"42"` 转换为 `42`）。

## 常见查询 {#common-queries}

### 列出 token 可访问的 bases {#list-bases-the-token-can-see}
```bash
curl -s "https://api.airtable.com/v0/meta/bases" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 列出某个 base 的表和 schema {#list-tables-schema-for-a-base}
```bash
curl -s "https://api.airtable.com/v0/meta/bases/$BASE_ID/tables" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
在修改数据前使用此命令——可确认确切的字段名和 ID，显示选择字段的 `options.choices`，并展示主字段名称。

### 列出记录（前 10 条） {#list-records-first-10}
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=10" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 获取单条记录 {#get-a-single-record}
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 过滤记录（filterByFormula） {#filter-records-filterbyformula}
Airtable 公式必须进行 URL 编码。使用 Python 标准库进行编码——切勿手动编码：
```bash
FORMULA="{Status}='Todo'"
ENC=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$FORMULA")
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?filterByFormula=$ENC&maxRecords=20" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

常用公式模式：
- 精确匹配：`{Email}='user@example.com'`
- 包含：`FIND('bug', LOWER({Title}))`
- 多条件：`AND({Status}='Todo', {Priority}='High')`
- 或：`OR({Owner}='alice', {Owner}='bob')`
- 非空：`NOT({Assignee}='')`
- 日期比较：`IS_AFTER({Due}, TODAY())`

### 排序 + 选择特定字段 {#sort-select-specific-fields}
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?sort%5B0%5D%5Bfield%5D=Priority&sort%5B0%5D%5Bdirection%5D=asc&fields%5B%5D=Name&fields%5B%5D=Status" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
查询参数中的方括号必须进行 URL 编码（`%5B` / `%5D`）。

### 使用命名视图 {#use-a-named-view}
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?view=Grid%20view&maxRecords=50" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
视图会在服务端应用其保存的过滤和排序条件。

## 常见变更操作 {#common-mutations}

### 创建一条记录 {#create-a-record}
```bash
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Name":"New task","Status":"Todo","Priority":"High"}}' | python3 -m json.tool
```

### 一次调用创建最多 10 条记录 {#create-up-to-10-records-in-one-call}
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
批量端点每次请求最多 **10 条记录**。如需插入更多数据，请以 10 条为一组循环，并在每组之间短暂休眠，以遵守每秒 5 次请求 / base 的限制。
### 更新记录（PATCH — 合并，保留未更改的字段） {#update-a-record-patch-merges-preserves-unchanged-fields}
```bash
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Status":"Done"}}' | python3 -m json.tool
```

### 通过合并字段进行 Upsert（无需 ID） {#upsert-by-a-merge-field-no-id-needed}
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
`performUpsert` 会创建那些合并字段值为新值的记录，并更新那些合并字段值已存在的记录。非常适合幂等同步。

### 删除一条记录 {#delete-a-record}
```bash
curl -s -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 一次调用删除最多 10 条记录 {#delete-up-to-10-records-in-one-call}
```bash
curl -s -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE?records%5B%5D=rec1&records%5B%5D=rec2" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

## 分页 {#pagination}

列表端点每次最多返回 **100 条记录**。如果响应中包含 `"offset": "..."`，则在下次调用时传回。循环直到该字段不存在：

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

## 典型 Hermes 工作流程 {#typical-hermes-workflow}

1. **确认认证。** `curl -s -o /dev/null -w "%{http_code}\n" https://api.airtable.com/v0/meta/bases -H "Authorization: Bearer $AIRTABLE_API_KEY"` — 期望 `200`。
2. **找到 base。** 列出 bases（如上一步），或者如果 token 缺少 `schema.bases:read` 权限，直接让用户提供 `app...` ID。
3. **检查 schema。** `GET /v0/meta/bases/$BASE_ID/tables` — 在进行任何修改之前，将会话中确切的字段名和主字段名缓存到本地。
4. **读取后再写入。** 对于“更新满足 Y 的 X”，先使用 `filterByFormula` 解析出 `rec...` ID，然后 `PATCH /v0/$BASE_ID/$TABLE/$RECORD_ID`。切勿猜测记录 ID。
5. **批量写入。** 将相关的创建操作合并到一个最多 10 条记录的 POST 中，以保持在 5 次/秒的预算之内。
6. **破坏性操作。** 删除操作无法通过 API 撤销。如果用户说“删除所有 X”，先回显过滤条件和记录数，确认后再执行。

## 常见陷阱 {#pitfalls}

- **`filterByFormula` 必须进行 URL 编码。** 包含空格或非 ASCII 字符的字段名也需要编码（`{My Field}` → `%7BMy%20Field%7D`）。使用 Python 标准库（如上模式）——切勿手动转义。
- **响应中会省略空字段。** 缺少 `"Assignee"` 键并不意味着该字段不存在——只是表示该记录的值为空。在断定字段缺失之前，请检查 schema（步骤 3）。
- **PATCH 与 PUT 的区别。** `PATCH` 将提供的字段合并到记录中。`PUT` 完全替换记录，并清除你未包含的任何字段。默认使用 `PATCH`。
- **单选选项必须存在。** 如果字段的选项列表中没有 `Shipping`，写入 `"Status": "Shipping"` 会报错 `INVALID_MULTIPLE_CHOICE_OPTIONS`，除非你传递 `"typecast": true`（这会自动创建该选项）。
- **基于 base 的 token 作用域。** 如果某个 base 返回 `403` 而其他 base 正常，说明该 token 的访问列表不包含该 base——这不是作用域或认证问题。引导用户前往 https://airtable.com/create/tokens 授予权限。
- **速率限制是基于 base 的，而非基于 token。** 对 `baseA` 每秒 5 次请求，同时对 `baseB` 每秒 5 次请求是可以的；但单独对 `baseA` 每秒 6 次请求会被限流。监控 `429` 响应中的 `Retry-After` 头部。
## 给 Hermes 的重要提示 {#important-notes-for-hermes}

- **始终使用带 `curl` 的 `terminal` 工具。** 不要使用 `web_extract`（它无法发送认证头）或 `browser_navigate`（需要 UI 认证且速度慢）。
- **当此技能加载后，`AIRTABLE_API_KEY` 会自动从 `~/.hermes/.env` 流入子进程** —— 无需在每次 `curl` 调用前重新导出。
- **小心转义公式中的花括号。** 在 heredoc 主体中，`{Status}` 是字面量。在 shell 参数中，`{Status}` 在 `{...}` 花括号展开上下文之外是安全的 —— 但在拼接到 URL 之前，请通过 `python3 urllib.parse.quote` 传递动态字符串。
- **使用 `python3 -m json.tool`（始终存在）进行漂亮打印**，而不是 `jq`（可选）。仅当需要过滤/投影时才使用 `jq`。
- **分页是按页的，不是全局的。** Airtable 的 100 条记录上限是硬限制；没有办法提高它。使用 `offset` 循环，直到该字段不存在。
- **读取非 2xx 响应中的 `errors` 数组** —— Airtable 会返回结构化的错误代码，如 `AUTHENTICATION_REQUIRED`、`INVALID_PERMISSIONS`、`MODEL_ID_NOT_FOUND`、`INVALID_MULTIPLE_CHOICE_OPTIONS`，这些代码能准确告诉你问题所在。
