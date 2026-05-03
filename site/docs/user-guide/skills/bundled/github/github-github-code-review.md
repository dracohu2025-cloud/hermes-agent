---
title: "Github Code Review — 通过 gh 或 REST 审查 PR：差异与行内评论"
sidebar_label: "Github Code Review"
description: "审查 PR：通过 gh 或 REST 查看差异与行内评论"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Github Code Review {#github-code-review}

审查 PR：通过 gh 或 REST 查看差异与行内评论。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/github-code-review` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `GitHub`, `Code-Review`, `Pull-Requests`, `Git`, `Quality` |
| 相关技能 | [`github-auth`](/user-guide/skills/bundled/github/github-github-auth), [`github-pr-workflow`](/user-guide/skills/bundled/github/github-github-pr-workflow) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="github-code-review"></a>
# GitHub Code Review

在推送前对本地更改进行代码审查，或审查 GitHub 上的开放 PR。此技能大部分使用纯 `git` —— `gh`/`curl` 的分支仅在 PR 级别的交互中起作用。

## 前置条件 {#prerequisites}

- 已通过 GitHub 认证（参见 `github-auth` 技能）
- 位于 git 仓库内

### 设置（用于 PR 交互） {#setup-for-pr-interactions}

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

## 1. 审查本地更改（推送前） {#1-reviewing-local-changes-pre-push}

这是纯 `git` 操作 —— 随处可用，无需 API。

### 获取差异 {#get-the-diff}

```bash
# 已暂存的更改（即将提交的内容）
git diff --staged

# 与 main 分支相比的所有更改（PR 将包含的内容）
git diff main...HEAD

# 仅文件名
git diff main...HEAD --name-only

# 统计摘要（每个文件的插入/删除行数）
git diff main...HEAD --stat
```

### 审查策略 {#review-strategy}

1. **先获取整体概览：**

```bash
git diff main...HEAD --stat
git log main..HEAD --oneline
```

2. **逐个文件审查** —— 使用 `read_file` 查看更改文件的完整上下文，并通过差异了解具体变化：

```bash
git diff main...HEAD -- src/auth/login.py
```

3. **检查常见问题：**

```bash
# 遗留的调试语句、TODO、console.log
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME\|HACK\|XXX\|debugger"

# 意外暂存的大文件
git diff main...HEAD --stat | sort -t'|' -k2 -rn | head -10

# 密钥或凭据模式
git diff main...HEAD | grep -in "password\|secret\|api_key\|token.*=\|private_key"

# 合并冲突标记
git diff main...HEAD | grep -n "<<<<<<\|>>>>>>\|======="
```
4. **向用户呈现结构化的反馈**。

### 审查输出格式 {#review-output-format}

审查本地变更时，请按以下结构呈现发现：

```
## 代码审查总结

### 严重问题
- **src/auth.py:45** — SQL 注入：用户输入直接传入查询。
  建议：使用参数化查询。

### 警告
- **src/models/user.py:23** — 密码以明文存储。请使用 bcrypt 或 argon2。
- **src/api/routes.py:112** — 登录端点未设置速率限制。

### 建议
- **src/utils/helpers.py:8** — 与 `src/core/utils.py:34` 逻辑重复。请合并。
- **tests/test_auth.py** — 缺少边界情况：过期令牌测试。

### 表现良好
- 中间件层职责分离清晰
- 正常路径的测试覆盖良好
```

---

## 2. 在 GitHub 上审查 Pull Request {#2-reviewing-a-pull-request-on-github}

### 查看 PR 详情 {#view-pr-details}

**使用 gh：**

```bash
gh pr view 123
gh pr diff 123
gh pr diff 123 --name-only
```

**使用 git + curl：**

```bash
PR_NUMBER=123

# 获取 PR 详情
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "
import sys, json
pr = json.load(sys.stdin)
print(f\"Title: {pr['title']}\")
print(f\"Author: {pr['user']['login']}\")
print(f\"Branch: {pr['head']['ref']} -> {pr['base']['ref']}\")
print(f\"State: {pr['state']}\")
print(f\"Body:\n{pr['body']}\")"

# 列出变更文件
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/files \
  | python3 -c "
import sys, json
for f in json.load(sys.stdin):
    print(f\"{f['status']:10} +{f['additions']:-4} -{f['deletions']:-4}  {f['filename']}\")"
```

### 在本地签出 PR 进行完整审查 {#check-out-pr-locally-for-full-review}

这仅需纯 `git` 即可完成，无需 `gh`：

```bash
# 获取 PR 分支并签出
git fetch origin pull/123/head:pr-123
git checkout pr-123

# 现在你可以使用 read_file、search_files、运行测试等

# 查看与基础分支的差异
git diff main...pr-123
```

**使用 gh（快捷方式）：**

```bash
gh pr checkout 123
```

### 在 PR 上留下评论 {#leave-comments-on-a-pr}

**通用 PR 评论 — 使用 gh：**

```bash
gh pr comment 123 --body "整体看起来不错，下面有一些建议。"
```

**通用 PR 评论 — 使用 curl：**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments \
  -d '{"body": "整体看起来不错，下面有一些建议。"}'
```

### 留下内联审查评论 {#leave-inline-review-comments}

**单条内联评论 — 使用 gh（通过 API）：**

```bash
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')

gh api repos/$OWNER/$REPO/pulls/123/comments \
  --method POST \
  -f body="这可以用列表推导式简化。" \
  -f path="src/auth/login.py" \
  -f commit_id="$HEAD_SHA" \
  -f line=45 \
  -f side="RIGHT"
```

**单条内联评论 — 使用 curl：**

```bash
# 获取 head commit 的 SHA
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments \
  -d "{
    \"body\": \"这可以用列表推导式简化。\",
    \"path\": \"src/auth/login.py\",
    \"commit_id\": \"$HEAD_SHA\",
    \"line\": 45,
    \"side\": \"RIGHT\"
  }"
```
### 提交正式审查（批准 / 请求变更） {#submit-a-formal-review-approve-request-changes}

**使用 gh：**

```bash
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
gh pr review 123 --comment --body "Some suggestions, nothing blocking."
```

**使用 curl — 以原子方式提交多条评论的审查：**

```bash
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"COMMENT\",
    \"body\": \"Code review from Hermes Agent\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"Use parameterized queries to prevent SQL injection.\"},
      {\"path\": \"src/models/user.py\", \"line\": 23, \"body\": \"Hash passwords with bcrypt before storing.\"},
      {\"path\": \"tests/test_auth.py\", \"line\": 1, \"body\": \"Add test for expired token edge case.\"}
    ]
  }"
```

事件值：`"APPROVE"`、`"REQUEST_CHANGES"`、`"COMMENT"`

`line` 字段指的是文件*新版本*中的行号。对于已删除的行，请使用 `"side": "LEFT"`。

---

## 3. 审查清单 {#3-review-checklist}

执行代码审查（本地或 PR）时，请系统性地检查以下内容：

### 正确性 {#correctness}
- 代码是否实现了它声称的功能？
- 是否处理了边界情况（空输入、null、大数据、并发访问）？
- 错误路径是否被优雅地处理？

### 安全性 {#security}
- 没有硬编码的密钥、凭据或 API 密钥
- 对面向用户的输入进行输入验证
- 没有 SQL 注入、XSS 或路径遍历
- 在需要的地方进行身份验证/授权检查

### 代码质量 {#code-quality}
- 命名清晰（变量、函数、类）
- 没有不必要的复杂性或过早抽象
- DRY — 没有应该提取的重复逻辑
- 函数职责单一（单一职责）

### 测试 {#testing}
- 新的代码路径是否被测试？
- 快乐路径和错误情况是否覆盖？
- 测试是否可读且可维护？

### 性能 {#performance}
- 没有 N+1 查询或不必要的循环
- 在有益的地方使用适当的缓存
- 异步代码路径中没有阻塞操作

### 文档 {#documentation}
- 公共 API 有文档
- 非显而易见的逻辑有注释解释“为什么”
- 如果行为发生变化，README 已更新

---

## 4. 推送前审查工作流 {#4-pre-push-review-workflow}

当用户要求你“审查代码”或“推送前检查”时：

1. `git diff main...HEAD --stat` — 查看变更范围
2. `git diff main...HEAD` — 阅读完整差异
3. 对于每个变更的文件，如果需要更多上下文，使用 `read_file`
4. 应用上述清单
5. 以结构化格式呈现发现（严重问题 / 警告 / 建议 / 看起来不错）
6. 如果发现严重问题，主动提出在用户推送前修复它们

---

## 5. PR 审查工作流（端到端） {#5-pr-review-workflow-end-to-end}

当用户要求你“审查 PR #N”、“看看这个 PR”或给你一个 PR URL 时，请遵循以下步骤：
### 步骤 1：设置环境 {#step-1-set-up-environment}

```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"
# 或者运行本技能顶部的内联设置块
```

### 步骤 2：收集 PR 上下文 {#step-2-gather-pr-context}

在深入代码之前，先获取 PR 的元数据、描述和变更文件列表，以了解整体范围。

**使用 gh：**
```bash
gh pr view 123
gh pr diff 123 --name-only
gh pr checks 123
```

**使用 curl：**
```bash
PR_NUMBER=123

# PR 详情（标题、作者、描述、分支）
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER

# 变更文件及行数
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/files
```

### 步骤 3：在本地检出 PR {#step-3-check-out-the-pr-locally}

这样你就可以完全访问 `read_file`、`search_files`，并且能够运行测试。

```bash
git fetch origin pull/$PR_NUMBER/head:pr-$PR_NUMBER
git checkout pr-$PR_NUMBER
```

### 步骤 4：阅读 diff 并理解变更 {#step-4-read-the-diff-and-understand-changes}

```bash
# 与基础分支的完整 diff
git diff main...HEAD

# 对于大型 PR，可以逐个文件查看
git diff main...HEAD --name-only
# 然后针对每个文件：
git diff main...HEAD -- path/to/file.py
```

对于每个变更文件，使用 `read_file` 查看变更周围的完整上下文——仅靠 diff 可能会遗漏只有结合周围代码才能发现的问题。

### 步骤 5：在本地运行自动化检查（如适用） {#step-5-run-automated-checks-locally-if-applicable}

```bash
# 如果有测试套件，运行测试
python -m pytest 2>&1 | tail -20
# 或：npm test, cargo test, go test ./..., 等。

# 如果配置了 linter，运行它
ruff check . 2>&1 | head -30
# 或：eslint, clippy, 等。
```

### 步骤 6：应用审查清单（第 3 节） {#step-6-apply-the-review-checklist-section-3}

逐一检查每个类别：正确性、安全性、代码质量、测试、性能、文档。

### 步骤 7：将审查结果发布到 GitHub {#step-7-post-the-review-to-github}

收集你的发现，并以带有内联评论的正式审查形式提交。

**使用 gh：**
```bash
# 如果没有问题——批准
gh pr review $PR_NUMBER --approve --body "由 Hermes Agent 审查。代码看起来干净——测试覆盖良好，无安全问题。"

# 如果发现问题——请求变更并附带内联评论
gh pr review $PR_NUMBER --request-changes --body "发现几个问题——请查看内联评论。"
```

**使用 curl——带有多个内联评论的原子化审查：**
```bash
HEAD_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

# 构建审查 JSON——事件为 APPROVE、REQUEST_CHANGES 或 COMMENT
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"REQUEST_CHANGES\",
    \"body\": \"## Hermes Agent 审查\n\n发现 2 个问题，1 个建议。请查看内联评论。\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"🔴 **严重：** 用户输入直接传递给 SQL 查询——请使用参数化查询。\"},
      {\"path\": \"src/models.py\", \"line\": 23, \"body\": \"⚠️ **警告：** 密码未经过哈希处理即存储。\"},
      {\"path\": \"src/utils.py\", \"line\": 8, \"body\": \"💡 **建议：** 此逻辑与 core/utils.py:34 重复。\"}
    ]
  }"
```
### 步骤 8：同时发布一条总结评论 {#step-8-also-post-a-summary-comment}

除了行内评论外，再添加一条顶层总结，让 PR 作者一眼就能看到全貌。使用 `references/review-output-template.md` 中的审查输出格式。

**使用 gh：**
```bash
gh pr comment $PR_NUMBER --body "$(cat <<'EOF'
## Code Review Summary

**Verdict: Changes Requested** (2 issues, 1 suggestion)

### 🔴 Critical
- **src/auth.py:45** — SQL injection vulnerability

### ⚠️ Warnings
- **src/models.py:23** — Plaintext password storage

### 💡 Suggestions
- **src/utils.py:8** — Duplicated logic, consider consolidating

### ✅ Looks Good
- Clean API design
- Good error handling in the middleware layer

---
*Reviewed by Hermes Agent*
EOF
)"
```

### 步骤 9：清理 {#step-9-clean-up}

```bash
git checkout main
git branch -D pr-$PR_NUMBER
```

### 决策：批准 vs 请求修改 vs 评论 {#decision-approve-vs-request-changes-vs-comment}

- **批准** — 没有严重或警告级别的问题，只有轻微建议或一切正常
- **请求修改** — 存在任何应在合并前修复的严重或警告级别问题
- **评论** — 提出观察和建议，但无阻塞项（当你不确定或 PR 为草稿时使用）
