---
title: "Linear — Linear：通过 GraphQL + curl 管理问题、项目、团队"
sidebar_label: "Linear"
description: "Linear：通过 GraphQL + curl 管理问题、项目、团队"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Linear {#linear}

Linear：通过 GraphQL + curl 管理问题、项目、团队。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/linear` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `Linear`, `Project Management`, `Issues`, `GraphQL`, `API`, `Productivity` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Linear — 问题与项目管理 {#linear-issue-project-management}

通过 `curl` 直接使用 GraphQL API 管理 Linear 的问题、项目和团队。无需 MCP 服务器，无需 OAuth 流程，无需额外依赖。

## 设置 {#setup}

1. 从 **Linear Settings > API > Personal API keys** 获取个人 API 密钥
2. 在环境中设置 `LINEAR_API_KEY`（通过 `hermes setup` 或你的环境配置）

## API 基础 {#api-basics}

- **端点：** `https://api.linear.app/graphql` (POST)
- **认证头：** `Authorization: $LINEAR_API_KEY`（API 密钥无需 "Bearer" 前缀）
- **所有请求均为 POST**，带有 `Content-Type: application/json`
- **UUID 和短标识符**（例如 `ENG-123`）均可用于 `issue(id:)`

基础 curl 模式：
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name } }"}' | python3 -m json.tool
```

## 工作流状态 {#workflow-states}

Linear 使用带有 `type` 字段的 `WorkflowState` 对象。**6 种状态类型：**

| 类型 | 描述 |
|------|------|
| `triage` | 待审阅的传入问题 |
| `backlog` | 已确认但尚未规划 |
| `unstarted` | 已规划/就绪但未开始 |
| `started` | 正在积极处理中 |
| `completed` | 已完成 |
| `canceled` | 不会执行 |

每个团队都有自己的命名状态（例如 "In Progress" 是类型 `started`）。要更改问题的状态，你需要目标状态的 `stateId`（UUID）—— 先查询工作流状态。

**优先级值：** 0 = 无，1 = 紧急，2 = 高，3 = 中，4 = 低

## 常用查询 {#common-queries}

### 获取当前用户 {#get-current-user}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email } }"}' | python3 -m json.tool
```

### 列出团队 {#list-teams}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { id name key } } }"}' | python3 -m json.tool
```

### 列出团队的工作流状态 {#list-workflow-states-for-a-team}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ workflowStates(filter: { team: { key: { eq: \"ENG\" } } }) { nodes { id name type } } }"}' | python3 -m json.tool
```
### 列出问题（前 20 条） {#list-issues-first-20}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 20) { nodes { identifier title priority state { name type } assignee { name } team { key } url } pageInfo { hasNextPage endCursor } } }"}' | python3 -m json.tool
```

### 列出分配给我的问题 {#list-my-assigned-issues}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { assignedIssues(first: 25) { nodes { identifier title state { name type } priority url } } } }"}' | python3 -m json.tool
```

### 获取单个问题（通过标识符，如 ENG-123） {#get-a-single-issue-by-identifier-like-eng-123}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issue(id: \"ENG-123\") { id identifier title description priority state { id name type } assignee { id name } team { key } project { name } labels { nodes { name } } comments { nodes { body user { name } createdAt } } url } }"}' | python3 -m json.tool
```

### 按文本搜索问题 {#search-issues-by-text}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issueSearch(query: \"bug login\", first: 10) { nodes { identifier title state { name } assignee { name } url } } }"}' | python3 -m json.tool
```

### 按状态类型筛选问题 {#filter-issues-by-state-type}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(filter: { state: { type: { in: [\"started\"] } } }, first: 20) { nodes { identifier title state { name } assignee { name } } } }"}' | python3 -m json.tool
```

### 按团队和负责人筛选 {#filter-by-team-and-assignee}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(filter: { team: { key: { eq: \"ENG\" } }, assignee: { email: { eq: \"user@example.com\" } } }, first: 20) { nodes { identifier title state { name } priority } } }"}' | python3 -m json.tool
```

### 列出项目 {#list-projects}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ projects(first: 20) { nodes { id name description progress lead { name } teams { nodes { key } } url } } }"}' | python3 -m json.tool
```

### 列出团队成员 {#list-team-members}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ users { nodes { id name email active } } }"}' | python3 -m json.tool
```

### 列出标签 {#list-labels}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issueLabels { nodes { id name color } } }"}' | python3 -m json.tool
```
## 常见变更操作 {#common-mutations}

### 创建 Issue {#create-an-issue}
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

### 更新 Issue 状态 {#update-issue-status}
先从上面的工作流状态查询中获取目标状态的 UUID，然后：
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { stateId: \"STATE_UUID\" }) { success issue { identifier state { name type } } } }"}' | python3 -m json.tool
```

### 分配 Issue {#assign-an-issue}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { assigneeId: \"USER_UUID\" }) { success issue { identifier assignee { name } } } }"}' | python3 -m json.tool
```

### 设置优先级 {#set-priority}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { priority: 1 }) { success issue { identifier priority } } }"}' | python3 -m json.tool
```

### 添加评论 {#add-a-comment}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { commentCreate(input: { issueId: \"ISSUE_UUID\", body: \"Investigated. Root cause is X.\" }) { success comment { id body } } }"}' | python3 -m json.tool
```

### 设置截止日期 {#set-due-date}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { dueDate: \"2026-04-01\" }) { success issue { identifier dueDate } } }"}' | python3 -m json.tool
```

### 为 Issue 添加标签 {#add-labels-to-an-issue}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { labelIds: [\"LABEL_UUID_1\", \"LABEL_UUID_2\"] }) { success issue { identifier labels { nodes { name } } } } }"}' | python3 -m json.tool
```

### 将 Issue 添加到项目 {#add-issue-to-a-project}
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { projectId: \"PROJECT_UUID\" }) { success issue { identifier project { name } } } }"}' | python3 -m json.tool
```

### 创建项目 {#create-a-project}
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
## 分页 {#pagination}

Linear 使用 Relay 风格的光标分页：

```bash
# 第一页
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 20) { nodes { identifier title } pageInfo { hasNextPage endCursor } } }"}' | python3 -m json.tool

# 下一页 — 使用上一次响应中的 endCursor
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issues(first: 20, after: \"CURSOR_FROM_PREVIOUS\") { nodes { identifier title } pageInfo { hasNextPage endCursor } } }"}' | python3 -m json.tool
```

默认每页大小：50。最大：250。始终使用 `first: N` 来限制结果数量。

## 过滤参考 {#filtering-reference}

比较运算符：`eq`、`neq`、`in`、`nin`、`lt`、`lte`、`gt`、`gte`、`contains`、`startsWith`、`containsIgnoreCase`

使用 `or: [...]` 组合过滤器实现 OR 逻辑（过滤器对象内部默认为 AND）。

## 典型工作流程 {#typical-workflow}

1. **查询团队** 获取团队 ID 和标识符
2. **查询工作流状态** 获取目标团队的状态 UUID
3. **列出或搜索问题** 找到需要处理的内容
4. **创建问题** 包含团队 ID、标题、描述、优先级
5. **更新状态** 将 `stateId` 设置为目标工作流状态
6. **添加评论** 跟踪进度
7. **标记完成** 将 `stateId` 设置为团队的"已完成"类型状态

## 速率限制 {#rate-limits}

- 每个 API 密钥每小时 5,000 次请求
- 每小时 3,000,000 复杂度点数
- 使用 `first: N` 限制结果数量并降低复杂度成本
- 监控 `X-RateLimit-Requests-Remaining` 响应头

## 重要说明 {#important-notes}

- 始终使用 `terminal` 工具配合 `curl` 进行 API 调用 — 不要使用 `web_extract` 或 `browser`
- 始终检查 GraphQL 响应中的 `errors` 数组 — HTTP 200 仍可能包含错误
- 创建问题时如果省略 `stateId`，Linear 默认使用第一个待办状态
- `description` 字段支持 Markdown
- 使用 `python3 -m json.tool` 或 `jq` 格式化 JSON 响应以便阅读
