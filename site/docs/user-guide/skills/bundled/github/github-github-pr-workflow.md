---
title: "Github Pr Workflow — GitHub PR 生命周期：分支、提交、打开、CI、合并"
sidebar_label: "Github Pr Workflow"
description: "GitHub PR 生命周期：分支、提交、打开、CI、合并"
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Github Pr Workflow {#github-pr-workflow}

GitHub PR 生命周期：分支、提交、打开、CI、合并。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/github-pr-workflow` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `GitHub`, `Pull-Requests`, `CI/CD`, `Git`, `自动化`, `合并` |
| 相关技能 | [`github-auth`](/user-guide/skills/bundled/github/github-github-auth), [`github-code-review`](/user-guide/skills/bundled/github/github-github-code-review) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# GitHub Pull Request 工作流 {#github-pull-request-workflow}

管理 PR 生命周期的完整指南。每个部分先展示 `gh` 方式，再展示没有 `gh` 时使用 `git` + `curl` 的备用方式。

## 前置条件 {#prerequisites}

- 已通过 GitHub 认证（参见 `github-auth` 技能）
- 位于带有 GitHub 远程仓库的 git 仓库内

### 快速认证检测 {#quick-auth-detection}

```bash
# 确定在整个工作流中使用哪种方法
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # 确保我们有用于 API 调用的令牌
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"
```

### 从 Git 远程仓库提取 Owner/Repo {#extracting-owner-repo-from-the-git-remote}

许多 `curl` 命令需要 `owner/repo`。从 git 远程仓库中提取：

```bash
# 适用于 HTTPS 和 SSH 远程 URL
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

## 1. 创建分支 {#1-branch-creation}

这部分是纯 `git` 操作——两种方式相同：

```bash
# 确保你处于最新状态
git fetch origin
git checkout main && git pull origin main

# 创建并切换到新分支
git checkout -b feat/add-user-authentication
```

分支命名约定：
- `feat/description` — 新功能
- `fix/description` — 错误修复
- `refactor/description` — 代码重构
- `docs/description` — 文档
- `ci/description` — CI/CD 变更

## 2. 提交更改 {#2-making-commits}

使用 Agent 的文件工具（`write_file`、`patch`）进行更改，然后提交：

```bash
# 暂存特定文件
git add src/auth.py src/models/user.py tests/test_auth.py

# 使用约定式提交信息进行提交
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```
提交信息格式（约定式提交）：
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

类型：`feat`、`fix`、`refactor`、`docs`、`test`、`ci`、`chore`、`perf`

## 3. 推送和创建 PR {#3-pushing-and-creating-a-pr}

### 推送分支（两种方式相同） {#push-the-branch-same-either-way}

```bash
git push -u origin HEAD
```

### 创建 PR {#create-the-pr}

**使用 gh：**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

可选参数：`--draft`、`--reviewer user1,user2`、`--label "enhancement"`、`--base develop`

**使用 git + curl：**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

返回的 JSON 中包含 PR 的 `number` —— 请保存它，后续命令会用到。

若要创建草稿 PR，可在 JSON 中添加 `"draft": true`。

## 4. 监控 CI 状态 {#4-monitoring-ci-status}

### 检查 CI 状态 {#check-ci-status}

**使用 gh：**

```bash
# 一次性检查
gh pr checks

# 持续观察直至所有检查完成（每 10 秒轮询一次）
gh pr checks --watch
```

**使用 git + curl：**

```bash
# 获取当前分支上最新提交的 SHA
SHA=$(git rev-parse HEAD)

# 查询整体状态
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Overall: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"

# 同时检查 GitHub Actions 的检查运行（独立端点）
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cr in data.get('check_runs', []):
    print(f\"  {cr['name']}: {cr['status']} / {cr['conclusion'] or 'pending'}\")"
```

### 轮询直至完成（git + curl） {#poll-until-complete-git-curl}

```bash
# 简单的轮询循环 —— 每 30 秒检查一次，最多持续 10 分钟
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "Check $i: $STATUS"
  if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  sleep 30
done
```

## 5. 自动修复 CI 失败 {#5-auto-fixing-ci-failures}

当 CI 失败时，进行诊断并修复。此循环适用于两种认证方式。

### 步骤 1：获取失败详情 {#step-1-get-failure-details}

**使用 gh：**

```bash
# 列出该分支最近的 workflow 运行
gh run list --branch $(git branch --show-current) --limit 5

# 查看失败的日志
gh run view <RUN_ID> --log-failed
```
**使用 git + curl：**

```bash
BRANCH=$(git branch --show-current)

# 列出此分支上的工作流运行记录
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f\"运行 {r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# 获取失败任务的日志（下载为 zip，解压，读取）
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

### 步骤 2：修复并推送 {#step-2-fix-and-push}

确定问题后，使用文件工具（`patch`、`write_file`）进行修复：

```bash
git add <fixed_files>
git commit -m "fix: 解决 <check_name> 中的 CI 失败"
git push
```

### 步骤 3：验证 {#step-3-verify}

使用上面第 4 节中的命令重新检查 CI 状态。

### 自动修复循环模式 {#auto-fix-loop-pattern}

当要求自动修复 CI 时，遵循以下循环：

1. 检查 CI 状态 → 识别失败项
2. 读取失败日志 → 理解错误
3. 使用 `read_file` + `patch`/`write_file` → 修复代码
4. `git add . && git commit -m "fix: ..." && git push`
5. 等待 CI → 重新检查状态
6. 如果仍然失败则重复（最多尝试 3 次，然后询问用户）

## 6. 合并 {#6-merging}

**使用 gh：**

```bash
# 压缩合并 + 删除分支（功能分支最干净的做法）
gh pr merge --squash --delete-branch

# 启用自动合并（所有检查通过后合并）
gh pr merge --auto --squash --delete-branch
```

**使用 git + curl：**

```bash
PR_NUMBER=<number>

# 通过 API 合并 PR（压缩合并）
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# 合并后删除远程分支
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# 本地切回 main
git checkout main && git pull origin main
git branch -d $BRANCH
```

合并方式：`"merge"`（合并提交）、`"squash"`（压缩）、`"rebase"`（变基）

### 启用自动合并（curl） {#enable-auto-merge-curl}

```bash
# 自动合并需要仓库在设置中启用该功能。
# 这里使用 GraphQL API，因为 REST 不支持自动合并。
PR_NODE_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d "{\"query\": \"mutation { enablePullRequestAutoMerge(input: {pullRequestId: \\\"$PR_NODE_ID\\\", mergeMethod: SQUASH}) { clientMutationId } }\"}"
```

## 7. 完整工作流示例 {#7-complete-workflow-example}

```bash
# 1. 从干净的 main 开始
git checkout main && git pull origin main

# 2. 创建分支
git checkout -b fix/login-redirect-bug

# 3. （Agent 使用文件工具修改代码）

# 4. 提交
git add src/auth/login.py tests/test_login.py
git commit -m "fix: 修复登录后的重定向 URL

保留 ?next= 参数，而不是始终重定向到 /dashboard。"

# 5. 推送
git push -u origin HEAD

# 6. 创建 PR（根据可用工具选择 gh 或 curl）
# ...（参见第 3 节）

# 7. 监控 CI（参见第 4 节）

# 8. 通过后合并（参见第 6 节）
```
## 常用 PR 命令参考 {#useful-pr-commands-reference}

| 操作 | gh | git + curl |
|--------|-----|-----------|
| 列出我的 PR | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| 查看 PR 差异 | `gh pr diff` | `git diff main...HEAD` (本地) 或 `curl -H "Accept: application/vnd.github.diff" ...` |
| 添加评论 | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| 请求审查 | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` |
| 关闭 PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |
| 检出他人的 PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |
