---
title: "GitHub Issues — 通过 gh 或 REST 创建、分类、标记、分配 GitHub Issue"
sidebar_label: "GitHub Issues"
description: "通过 gh 或 REST 创建、分类、标记、分配 GitHub Issue"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# GitHub Issues {#github-issues}

通过 gh 或 REST 创建、分类、标记、分配 GitHub Issue。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/github-issues` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `GitHub`、`Issues`、`Project-Management`、`Bug-Tracking`、`Triage` |
| 相关技能 | [`github-auth`](/user-guide/skills/bundled/github/github-github-auth)、[`github-pr-workflow`](/user-guide/skills/bundled/github/github-github-pr-workflow) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# GitHub Issues 管理 {#github-issues-management}

创建、搜索、分类和管理 GitHub Issue。每个部分先展示 `gh` 命令，再展示 `curl` 备用方案。

## 前置条件 {#prerequisites}

- 已通过 GitHub 认证（参见 `github-auth` 技能）
- 位于带有 GitHub 远程仓库的 git 仓库内，或显式指定仓库

### 设置 {#setup}

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. 查看 Issue {#1-viewing-issues}

**使用 gh：**

```bash
gh issue list
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue list --search "authentication error" --state all
gh issue view 42
```

**使用 curl：**

```bash
# 列出打开的 Issue
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:  # GitHub API 在 /issues 中也会返回 PR
        labels = ', '.join(l['name'] for l in i['labels'])
        print(f\"#{i['number']:5}  {i['state']:6}  {labels:30}  {i['title']}\")"

# 按标签过滤
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&labels=bug&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:
        print(f\"#{i['number']}  {i['title']}\")"

# 查看特定 Issue
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  | python3 -c "
import sys, json
i = json.load(sys.stdin)
labels = ', '.join(l['name'] for l in i['labels'])
assignees = ', '.join(a['login'] for a in i['assignees'])
print(f\"#{i['number']}: {i['title']}\")
print(f\"State: {i['state']}  Labels: {labels}  Assignees: {assignees}\")
print(f\"Author: {i['user']['login']}  Created: {i['created_at']}\")
print(f\"\n{i['body']}\")"

# 搜索 Issue
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/search/issues?q=authentication+error+repo:$OWNER/$REPO" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin)['items']:
    print(f\"#{i['number']}  {i['state']:6}  {i['title']}\")"
```
## 2. 创建 Issue {#2-creating-issues}

**使用 gh：**

```bash
gh issue create \
  --title "Login redirect ignores ?next= parameter" \
  --body "## Description
After logging in, users always land on /dashboard.

## Steps to Reproduce
1. Navigate to /settings while logged out
2. Get redirected to /login?next=/settings
3. Log in
4. Actual: redirected to /dashboard (should go to /settings)

## Expected Behavior
Respect the ?next= query parameter." \
  --label "bug,backend" \
  --assignee "username"
```

**使用 curl：**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues \
  -d '{
    "title": "Login redirect ignores ?next= parameter",
    "body": "## Description\nAfter logging in, users always land on /dashboard.\n\n## Steps to Reproduce\n1. Navigate to /settings while logged out\n2. Get redirected to /login?next=/settings\n3. Log in\n4. Actual: redirected to /dashboard\n\n## Expected Behavior\nRespect the ?next= query parameter.",
    "labels": ["bug", "backend"],
    "assignees": ["username"]
  }'
```

### Bug 报告模板 {#bug-report-template}

```
## Bug 描述
<发生了什么>

## 重现步骤
1. <步骤>
2. <步骤>

## 期望行为
<应该发生什么>

## 实际行为
<实际发生了什么>

## 环境
- 操作系统：<操作系统>
- 版本：<版本>
```

### 功能请求模板 {#feature-request-template}

```
## 功能描述
<你想要什么>

## 动机
<为什么这个有用>

## 提议的解决方案
<它如何实现>

## 考虑过的替代方案
<其他思路>
```

## 3. 管理 Issue {#3-managing-issues}

### 添加/移除标签 {#add-remove-labels}

**使用 gh：**

```bash
gh issue edit 42 --add-label "priority:high,bug"
gh issue edit 42 --remove-label "needs-triage"
```

**使用 curl：**

```bash
# 添加标签
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels \
  -d '{"labels": ["priority:high", "bug"]}'

# 移除标签
curl -s -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels/needs-triage

# 列出仓库中可用的标签
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/labels \
  | python3 -c "
import sys, json
for l in json.load(sys.stdin):
    print(f\"  {l['name']:30}  {l.get('description', '')}\")"
```

### 分配 {#assignment}

**使用 gh：**

```bash
gh issue edit 42 --add-assignee username
gh issue edit 42 --add-assignee @me
```

**使用 curl：**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/assignees \
  -d '{"assignees": ["username"]}'
```

### 评论 {#commenting}

**使用 gh：**

```bash
gh issue comment 42 --body "Investigated — root cause is in auth middleware. Working on a fix."
```

**使用 curl：**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/comments \
  -d '{"body": "Investigated — root cause is in auth middleware. Working on a fix."}'
```
### 关闭与重新打开 {#closing-and-reopening}

**使用 gh：**

```bash
gh issue close 42
gh issue close 42 --reason "not planned"
gh issue reopen 42
```

**使用 curl：**

```bash
# 关闭
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  -d '{"state": "closed", "state_reason": "completed"}'

# 重新打开
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  -d '{"state": "open"}'
```

### 将 Issue 链接到 PR {#linking-issues-to-prs}

当 PR 合并时，如果其正文中包含以下关键词，关联的 Issue 会自动关闭：

```
Closes #42
Fixes #42
Resolves #42
```

从 Issue 创建分支：

**使用 gh：**

```bash
gh issue develop 42 --checkout
```

**使用 git（手动等效操作）：**

```bash
git checkout main && git pull origin main
git checkout -b fix/issue-42-login-redirect
```

## 4. Issue 分类工作流 {#4-issue-triage-workflow}

当被要求对 Issue 进行分类时：

1. **列出未分类的 Issue：**

```bash
# 使用 gh
gh issue list --label "needs-triage" --state open

# 使用 curl
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?labels=needs-triage&state=open" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:
        print(f\"#{i['number']}  {i['title']}\")"
```

2. **阅读并分类**每个 Issue（查看详情，理解是 Bug 还是功能需求）

3. **应用标签和优先级**（参见上面的“管理 Issue”）

4. **分配负责人**（如果明确的话）

5. **如有需要，添加分类备注评论**

## 5. 批量操作 {#5-bulk-operations}

对于批量操作，可以将 API 调用与 shell 脚本结合使用：

**使用 gh：**

```bash
# 关闭所有带有特定标签的 Issue
gh issue list --label "wontfix" --json number --jq '.[].number' | \
  xargs -I {} gh issue close {} --reason "not planned"
```

**使用 curl：**

```bash
# 列出带有特定标签的 Issue 编号，然后逐个关闭
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?labels=wontfix&state=open" \
  | python3 -c "import sys,json; [print(i['number']) for i in json.load(sys.stdin)]" \
  | while read num; do
    curl -s -X PATCH \
      -H "Authorization: token $GITHUB_TOKEN" \
      https://api.github.com/repos/$OWNER/$REPO/issues/$num \
      -d '{"state": "closed", "state_reason": "not_planned"}'
    echo "已关闭 #$num"
  done
```

## 快速参考表 {#quick-reference-table}

| 操作 | gh | curl 端点 |
|--------|-----|--------------|
| 列出 Issue | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| 查看 Issue | `gh issue view N` | `GET /repos/{o}/{r}/issues/N` |
| 创建 Issue | `gh issue create ...` | `POST /repos/{o}/{r}/issues` |
| 添加标签 | `gh issue edit N --add-label ...` | `POST /repos/{o}/{r}/issues/N/labels` |
| 分配负责人 | `gh issue edit N --add-assignee ...` | `POST /repos/{o}/{r}/issues/N/assignees` |
| 评论 | `gh issue comment N --body ...` | `POST /repos/{o}/{r}/issues/N/comments` |
| 关闭 | `gh issue close N` | `PATCH /repos/{o}/{r}/issues/N` |
| 搜索 | `gh issue list --search "..."` | `GET /search/issues?q=...` |
