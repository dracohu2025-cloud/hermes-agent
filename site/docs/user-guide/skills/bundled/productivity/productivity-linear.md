---
title: "Linear — Linear：通过 GraphQL + curl 管理问题、项目、团队"
sidebar_label: "Linear"
description: "Linear：通过 GraphQL + curl 管理问题、项目、团队"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="linear"></a>
# Linear

Linear：通过 GraphQL + curl 管理问题、项目、团队。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/linear` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Linear`, `Project Management`, `Issues`, `GraphQL`, `API`, `Productivity` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会看到这些指令。
:::

<a id="linear-issue-project-management"></a>
# Linear — 问题与项目管理

直接通过 GraphQL API 使用 `curl` 管理 Linear 的问题、项目和团队。无需 MCP 服务器、OAuth 流程或额外依赖。

<a id="setup"></a>
## 设置

1. 从 **Linear 设置 > 账户 > 安全与访问 > 个人 API 密钥**（URL：https://linear.app/settings/account/security）获取个人 API 密钥。注意：组织级别的 *设置 > API* 页面只显示 OAuth 应用和工作区成员密钥，不显示个人密钥。
2. 在环境中设置 `LINEAR_API_KEY`（通过 `hermes setup` 或你的环境配置）。

<a id="api-basics"></a>
## API 基础

- **端点：** `https://api.linear.app/graphql`（POST）
- **认证头：** `Authorization: $LINEAR_API_KEY`（API 密钥不需要 "Bearer" 前缀）
- **所有请求均为 POST**，附带 `Content-Type: application/json`
- **UUID 和短标识符**（如 `ENG-123`）均可用于 `issue(id:)`

基础 curl 模式：
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name } }"}' | python3 -m json.tool
```

<a id="python-helper-script-ergonomic-alternative"></a>
## Python 辅助脚本（更便捷的替代方案）

为了快速编写一行命令而无需手写 GraphQL，本技能附带了一个基于标准库的 Python CLI `scripts/linear_api.py`。零依赖。使用相同的认证（读取 `LINEAR_API_KEY`）。

```bash
SCRIPT=$(dirname "$(find ~/.hermes -path '*skills/productivity/linear/scripts/linear_api.py' 2>/dev/null | head -1)")/linear_api.py

python3 "$SCRIPT" whoami
python3 "$SCRIPT" list-teams
python3 "$SCRIPT" get-issue ENG-42
python3 "$SCRIPT" get-document 38359beef67c      # 通过 URL 中的 slugId 获取文档
python3 "$SCRIPT" raw 'query { viewer { name } }'
```

所有子命令：`whoami`、`list-teams`、`list-projects`、`list-states`、`list-issues`、`get-issue`、`search-issues`、`create-issue`、`update-issue`、`update-status`、`add-comment`、`list-documents`、`get-document`、`search-documents`、`raw`。使用 `--help` 查看参数。

在以下情况使用脚本：你想快速得到答案，无需构造 GraphQL。在以下情况使用 curl：你需要执行脚本未封装的查询，或者想内联组合过滤器。

<a id="workflow-states"></a>
## 工作流状态

Linear 使用包含 `type` 字段的 `WorkflowState` 对象。**6 种状态类型：**

| 类型 | 描述 |
|------|------|
| `triage` | 待审核的入库问题 |
| `backlog` | 已确认但尚未规划 |
| `unstarted` | 已规划/就绪但未开始 |
| `started` | 正在积极处理 |
| `completed` | 已完成 |
| `canceled` | 不会执行 |
每个团队都有自己的命名状态（例如，"In Progress" 对应类型 `started`）。要更改 issue 的状态，你需要目标状态的 `stateId`（UUID）——请先查询工作流状态。

**优先级值：** 0 = 无，1 = 紧急，2 = 高，3 = 中，4 = 低

<a id="common-queries"></a>
## 常用查询

<a id="get-current-user"></a>
### 获取当前用户
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email } }"}' | python3 -m json.tool
```

<a id="list-teams"></a>
### 列出团队
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { id name key } } }"}' | python3 -m json.tool
```

<a id="list-workflow-states-for-a-team"></a>
### 列出团队的工作流状态
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ workflowStates(filter: { team: { key: { eq: \"ENG\" } } }) { nodes { id name type } } }"}' | python3 -m json.tool
```

<a id="list-issues-first-20"></a>
### 列出 issue（前 20 条）
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 20) { nodes { identifier title priority state { name type } assignee { name } team { key } url } pageInfo { hasNextPage endCursor } } }"}' | python3 -m json.tool
```

<a id="list-my-assigned-issues"></a>
### 列出分配给我的 issue
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { assignedIssues(first: 25) { nodes { identifier title state { name type } priority url } } } }"}' | python3 -m json.tool
```

<a id="get-a-single-issue-by-identifier-like-eng-123"></a>
### 获取单个 issue（通过标识符，如 ENG-123）
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issue(id: \"ENG-123\") { id identifier title description priority state { id name type } assignee { id name } team { key } project { name } labels { nodes { name } } comments { nodes { body user { name } createdAt } } url } }"}' | python3 -m json.tool
```

<a id="search-issues-by-text"></a>
### 按文本搜索 issue
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issueSearch(query: \"bug login\", first: 10) { nodes { identifier title state { name } assignee { name } url } } }"}' | python3 -m json.tool
```

<a id="filter-issues-by-state-type"></a>
### 按状态类型筛选 issue
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(filter: { state: { type: { in: [\"started\"] } } }, first: 20) { nodes { identifier title state { name } assignee { name } } } }"}' | python3 -m json.tool
```

<a id="filter-by-team-and-assignee"></a>
### 按团队和负责人筛选
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(filter: { team: { key: { eq: \"ENG\" } }, assignee: { email: { eq: \"user@example.com\" } } }, first: 20) { nodes { identifier title state { name } priority } } }"}' | python3 -m json.tool
```
<a id="list-projects"></a>
### 列出项目
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ projects(first: 20) { nodes { id name description progress lead { name } teams { nodes { key } } url } } }"}' | python3 -m json.tool
```

<a id="list-team-members"></a>
### 列出团队成员
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ users { nodes { id name email active } } }"}' | python3 -m json.tool
```

<a id="list-labels"></a>
### 列出标签
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issueLabels { nodes { id name color } } }"}' | python3 -m json.tool
```

<a id="common-mutations"></a>
## 常用变更操作

<a id="create-an-issue"></a>
### 创建 issue
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($input: IssueCreateInput!) { issueCreate(input: $input) { success issue { id identifier title url } } }",
    "variables": {
      "input": {
        "teamId": "TEAM_UUID",
        "title": "Fix login bug",
        "description": "Users cannot login with SSO",
        "priority": 2
      }
    }
  }' | python3 -m json.tool
```

<a id="update-issue-status"></a>
### 更新 issue 状态
首先从上面的工作流状态查询中获取目标状态 UUID，然后：
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { stateId: \"STATE_UUID\" }) { success issue { identifier state { name type } } } }"}' | python3 -m json.tool
```

<a id="assign-an-issue"></a>
### 分配 issue
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { assigneeId: \"USER_UUID\" }) { success issue { identifier assignee { name } } } }"}' | python3 -m json.tool
```

<a id="set-priority"></a>
### 设置优先级
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { priority: 1 }) { success issue { identifier priority } } }"}' | python3 -m json.tool
```

<a id="add-a-comment"></a>
### 添加评论
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { commentCreate(input: { issueId: \"ISSUE_UUID\", body: \"Investigated. Root cause is X.\" }) { success comment { id body } } }"}' | python3 -m json.tool
```

<a id="set-due-date"></a>
### 设置截止日期
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { dueDate: \"2026-04-01\" }) { success issue { identifier dueDate } } }"}' | python3 -m json.tool
```
<a id="add-labels-to-an-issue"></a>
### 给 Issues 添加标签
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { labelIds: [\"LABEL_UUID_1\", \"LABEL_UUID_2\"] }) { success issue { identifier labels { nodes { name } } } } }"}' | python3 -m json.tool
```

<a id="add-issue-to-a-project"></a>
### 将 Issue 添加到项目
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { projectId: \"PROJECT_UUID\" }) { success issue { identifier project { name } } } }"}' | python3 -m json.tool
```

<a id="create-a-project"></a>
### 创建项目
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($input: ProjectCreateInput!) { projectCreate(input: $input) { success project { id name url } } }",
    "variables": {
      "input": {
        "name": "Q2 Auth Overhaul",
        "description": "Replace legacy auth with OAuth2 and PKCE",
        "teamIds": ["TEAM_UUID"]
      }
    }
  }' | python3 -m json.tool
```

<a id="documents"></a>
## 文档

Linear **文档**是与 Issues 一起存储的散文式文档（RFC、规格说明、笔记）。它们有自己的 `documents` 根查询和 `document(id:)` 单次获取。

<a id="document-urls-and-slugid"></a>
### 文档 URL 与 `slugId`

文档 URL 看起来像这样：
```
https://linear.app/<workspace>/document/<slug>-<hexSlugId>
```

末尾的十六进制段就是 `slugId`。例如：`https://linear.app/nousresearch/document/rfc-hermes-permission-gateway-discord-38359beef67c` → `slugId` 是 `38359beef67c`。

**重要的模式细节：** Markdown 正文位于 `content` 字段。ProseMirror JSON 位于 `contentState`（而不是 `contentData`——该字段不存在，API 会返回 400）。

<a id="fetch-a-document-by-slugid"></a>
### 通过 slugId 获取文档

`document(id:)` 只接受 UUID。要通过 URL 的十六进制 slug 获取，需要对集合进行过滤：

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "query($s: String!) { documents(filter: { slugId: { eq: $s } }, first: 1) { nodes { id title content contentState slugId url creator { name } project { name } updatedAt } } }", "variables": {"s": "38359beef67c"}}' \
  | python3 -m json.tool
```

或者通过 Python 辅助脚本：
```bash
python3 scripts/linear_api.py get-document 38359beef67c
```

<a id="fetch-a-document-by-uuid"></a>
### 通过 UUID 获取文档

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ document(id: \"11700cff-b514-4db3-afcc-3ed1afacba1c\") { title content url } }"}' \
  | python3 -m json.tool
```

<a id="list-recent-documents"></a>
### 列出近期文档

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ documents(first: 25, orderBy: updatedAt) { nodes { id title slugId url updatedAt project { name } } } }"}' \
  | python3 -m json.tool
```
<a id="search-documents-by-title"></a>
### 按标题搜索文档

Linear 的 schema 中没有 `searchDocuments` 根字段。改用标题子字符串过滤：

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ documents(filter: { title: { containsIgnoreCase: \"RFC\" } }, first: 25) { nodes { title slugId url } } }"}' \
  | python3 -m json.tool
```

<a id="pagination"></a>
## 分页

Linear 使用 Relay 风格的游标分页：

```bash
# 第一页
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 20) { nodes { identifier title } pageInfo { hasNextPage endCursor } } }"}' | python3 -m json.tool

# 下一页 —— 使用上一次响应中的 endCursor
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 20, after: \"CURSOR_FROM_PREVIOUS\") { nodes { identifier title } pageInfo { hasNextPage endCursor } } }"}' | python3 -m json.tool
```

默认分页大小：50。最大：250。始终使用 `first: N` 来限制结果数量。

<a id="filtering-reference"></a>
## 筛选参考

比较运算符：`eq`、`neq`、`in`、`nin`、`lt`、`lte`、`gt`、`gte`、`contains`、`startsWith`、`containsIgnoreCase`

通过 `or: [...]` 组合多个筛选条件实现 OR 逻辑（在同一筛选对象内默认为 AND）。

<a id="typical-workflow"></a>
## 典型工作流程

1. **查询团队** 获取团队 ID 和 key
2. **查询工作流状态** 针对目标团队获取状态 UUID
3. **列出或搜索问题** 找到需要处理的内容
4. **创建问题** 使用团队 ID、标题、描述、优先级
5. **更新状态** 将 `stateId` 设置为目标工作流状态
6. **添加评论** 跟踪进展
7. **标记完成** 将 `stateId` 设置为团队的“已完成”类型状态

<a id="rate-limits"></a>
## 速率限制

- 每个 API key 每小时 5,000 次请求
- 每小时 3,000,000 复杂度积分
- 使用 `first: N` 限制结果以减少复杂度开销
- 监控响应头 `X-RateLimit-Requests-Remaining`

<a id="important-notes"></a>
## 重要注意事项

- 始终使用 `terminal` 工具配合 `curl` 调用 API —— 不要使用 `web_extract` 或 `browser`
- 始终检查 GraphQL 响应中的 `errors` 数组 —— HTTP 200 仍可能包含错误
- 若创建问题时省略 `stateId`，Linear 默认为第一个 backlog 状态
- `description` 字段支持 Markdown
- 使用 `python3 -m json.tool` 或 `jq` 格式化 JSON 响应以便阅读
