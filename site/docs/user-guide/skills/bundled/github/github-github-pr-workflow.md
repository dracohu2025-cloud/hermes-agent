---
title: "GitHub PR 工作流 — GitHub PR 生命周期：分支、提交、开启、CI、合并"
sidebar_label: "GitHub PR 工作流"
description: "GitHub PR 生命周期：分支、提交、开启、CI、合并"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能目录下的 SKILL.md 自动生成。请编辑源文件 SKILL.md，不要编辑本页面。 */}

<a id="github-pr-workflow"></a>
# GitHub PR 工作流

GitHub PR 生命周期：分支、提交、开启、CI、合并。

<a id="skill-metadata"></a>
## 技能元信息

| 项目 | 内容 |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/github/github-pr-workflow` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux, macos, windows |
| 标签 | `GitHub`, `Pull-Requests`, `CI/CD`, `Git`, `Automation`, `Merge` |
| 相关技能 | [`github-auth`](/user-guide/skills/bundled/github/github-github-auth), [`github-code-review`](/user-guide/skills/bundled/github/github-github-code-review) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在该技能被触发时加载的完整技能定义。这就是 agent 在技能激活时看到的指令内容。
:::

<a id="github-pull-request-workflow"></a>
# GitHub Pull Request 工作流

管理 PR 生命周期完整指南。每个小节首先展示 `gh` 的方式，然后展示没有 `gh` 时使用 `git` + `curl` 的备用方式。

<a id="prerequisites"></a>
## 前置条件

- 已通过 GitHub 认证（参见 `github-auth` 技能）
- 位于一个带有 GitHub 远程仓库的 git 仓库中

<a id="quick-auth-detection"></a>
### 快速认证检测

```bash
# 确定整个工作流使用哪种方法
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # 确保有用于 API 调用的 token
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

<a id="extracting-owner-repo-from-the-git-remote"></a>
### 从 Git 远程仓库提取 Owner/Repo

许多 `curl` 命令需要 `owner/repo`。从 git 远程仓库中提取：

```bash
# 同时适用于 HTTPS 和 SSH 远程 URL
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

<a id="1-branch-creation"></a>
## 1. 创建分支

这部分是纯 `git` — 无论采用哪种方式都是一样的：

```bash
# 确保你处于最新状态
git fetch origin
git checkout main && git pull origin main

# 创建并切换到新分支
git checkout -b feat/add-user-authentication
```

分支命名规范：
- `feat/description` — 新功能
- `fix/description` — 缺陷修复
- `refactor/description` — 代码重构
- `docs/description` — 文档
- `ci/description` — CI/CD 变更

<a id="2-making-commits"></a>
## 2. 提交代码

使用 agent 的文件工具（`write_file`、`patch`）做修改，然后提交：

```bash
# 暂存特定文件
git add src/auth.py src/models/user.py tests/test_auth.py

# 使用规范提交信息进行提交
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```
提交信息格式（Conventional Commits）：
```
type(scope): 简短描述

如果需要，可以加更长的说明。每行不超过72个字符。
```

类型：`feat`、`fix`、`refactor`、`docs`、`test`、`ci`、`chore`、`perf`

<a id="3-pushing-and-creating-a-pr"></a>
## 3. 推送并创建 PR

<a id="push-the-branch-same-either-way"></a>
### 推送分支（两种方式相同）

```bash
git push -u origin HEAD
```

<a id="create-the-pr"></a>
### 创建 PR

**使用 gh：**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## 摘要
- 添加登录和注册 API 端点
- JWT 令牌生成与验证

## 测试计划
- [ ] 单元测试通过

关闭 #42"
```

选项：`--draft`、`--reviewer user1,user2`、`--label "enhancement"`、`--base develop`

**使用 git + curl：**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## 摘要\n添加登录和注册 API 端点。\n\n关闭 #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

响应 JSON 中包含 PR 的 `number`——请保存下来供后续命令使用。

若要创建草稿 PR，在 JSON 正文中添加 `"draft": true`。

<a id="4-monitoring-ci-status"></a>
## 4. 监控 CI 状态

<a id="check-ci-status"></a>
### 检查 CI 状态

**使用 gh：**

```bash
# 一次性检查
gh pr checks

# 持续观察直到所有检查完成（每 10 秒轮询一次）
gh pr checks --watch
```

**使用 git + curl：**

```bash
# 获取当前分支最新的提交 SHA
SHA=$(git rev-parse HEAD)

# 查询合并状态
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"总体状态: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"

# 同时检查 GitHub Actions 的检查运行（单独的端点）
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cr in data.get('check_runs', []):
    print(f\"  {cr['name']}: {cr['status']} / {cr['conclusion'] or 'pending'}\")"
```

<a id="poll-until-complete-git-curl"></a>
### 轮询直到完成（git + curl）

```bash
# 简单的轮询循环——每 30 秒检查一次，最多持续 10 分钟
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "第 $i 次检查: $STATUS"
  if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  sleep 30
done
```

<a id="5-auto-fixing-ci-failures"></a>
## 5. 自动修复 CI 失败

当 CI 失败时，诊断并修复。此循环适用于两种认证方式。

<a id="step-1-get-failure-details"></a>
### 步骤 1：获取失败详情

**使用 gh：**

```bash
# 列出该分支上最近的工作流运行
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
    print(f\"运行 #{r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# 获取失败任务的日志（下载为 zip，解压，读取）
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

<a id="step-2-fix-and-push"></a>
### 步骤 2：修复并推送

发现问题后，使用文件工具（`patch`、`write_file`）进行修复：

```bash
git add <fixed_files>
git commit -m "fix: 解决 <check_name> 中的 CI 失败"
git push
```

<a id="step-3-verify"></a>
### 步骤 3：验证

使用上面第 4 节中的命令重新检查 CI 状态。

<a id="auto-fix-loop-pattern"></a>
### 自动修复循环模式

当要求自动修复 CI 时，请按以下循环执行：

1. 检查 CI 状态 → 识别失败项
2. 读取失败日志 → 理解错误
3. 使用 `read_file` + `patch`/`write_file` → 修复代码
4. `git add . && git commit -m "fix: ..." && git push`
5. 等待 CI → 重新检查状态
6. 如果仍然失败则重复（最多尝试 3 次，然后询问用户）

<a id="6-merging"></a>
## 6. 合并

**使用 gh：**

```bash
# Squash 合并 + 删除分支（对于功能分支最干净）
gh pr merge --squash --delete-branch

# 启用自动合并（所有检查通过后合并）
gh pr merge --auto --squash --delete-branch
```

**使用 git + curl：**

```bash
PR_NUMBER=<number>

# 通过 API 合并 PR（squash 方式）
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: 添加用户认证 (#$PR_NUMBER)\"
  }"

# 合并后删除远程分支
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# 在本地切回 main
git checkout main && git pull origin main
git branch -d $BRANCH
```

合并方式：`"merge"`（合并提交）、`"squash"`、`"rebase"`

<a id="enable-auto-merge-curl"></a>
### 启用自动合并（curl）

```bash
# 自动合并要求仓库已在设置中启用该功能。
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

<a id="7-complete-workflow-example"></a>
## 7. 完整工作流示例

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
# ...（见第 3 节）

# 7. 监控 CI（见第 4 节）

# 8. 绿色后合并（见第 6 节）
```
<a id="useful-pr-commands-reference"></a>
## 常用 PR 命令参考

| 操作 | gh | git + curl |
|--------|-----|-----------|
| 列出我的 PR | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| 查看 PR 差异 | `gh pr diff` | `git diff main...HEAD` (本地) 或 `curl -H "Accept: application/vnd.github.diff" ...` |
| 添加评论 | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| 请求评审 | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` |
| 关闭 PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |
| 签出他人的 PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |
