---
title: "Github Code Review — 通过 gh 或 REST 审查 PR：差异、内联评论"
sidebar_label: "Github Code Review"
description: "通过 gh 或 REST 审查 PR：差异、内联评论"
---

{/* 本页面由脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="github-code-review"></a>
# Github Code Review

通过 gh 或 REST 审查 PR：差异、内联评论。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/github-code-review` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `GitHub`, `Code-Review`, `Pull-Requests`, `Git`, `Quality` |
| 相关技能 | [`github-auth`](/user-guide/skills/bundled/github/github-github-auth), [`github-pr-workflow`](/user-guide/skills/bundled/github/github-github-pr-workflow) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是此技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# GitHub Code Review

在推送前对本地更改执行代码审查，或在 GitHub 上审查打开的 PR。本技能大部分使用普通的 `git` — `gh`/`curl` 的区分仅对 PR 级别的交互有意义。

<a id="prerequisites"></a>
## 前置条件

- 已通过 GitHub 身份验证（参见 `github-auth` 技能）
- 位于 git 仓库内

<a id="setup-for-pr-interactions"></a>
### 设置（用于 PR 交互）

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

<a id="1-reviewing-local-changes-pre-push"></a>
## 1. 审查本地更改（推送前）

这部分纯靠 `git` — 无需 API，随处可用。

<a id="get-the-diff"></a>
### 获取差异

```bash
# 已暂存的更改（将要提交的内容）
git diff --staged

# 与 main 分支的所有更改（PR 会包含的内容）
git diff main...HEAD

# 仅文件名
git diff main...HEAD --name-only

# 统计摘要（每个文件的插入/删除行数）
git diff main...HEAD --stat
```

<a id="review-strategy"></a>
### 审查策略

1. **先看全局：**

```bash
git diff main...HEAD --stat
git log main..HEAD --oneline
```

2. **逐个文件审查** — 用 `read_file` 查看变更文件的完整上下文，用 diff 查看具体变化：

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
4. **向用户提供结构化的反馈**。

<a id="review-output-format"></a>
### 审查输出格式

当审查本地变更时，按以下结构呈现发现结果：

```
## 代码审查总结

### 关键问题
- **src/auth.py:45** — SQL 注入：用户输入直接传入查询。
  建议：使用参数化查询。

### 警告
- **src/models/user.py:23** — 密码以明文存储。请使用 bcrypt 或 argon2。
- **src/api/routes.py:112** — 登录端点无速率限制。

### 建议
- **src/utils/helpers.py:8** — 与 `src/core/utils.py:34` 逻辑重复。建议合并。
- **tests/test_auth.py** — 缺少边界情况：过期令牌测试。

### 看起来不错
- 中间件层职责清晰分离
- 正向路径的测试覆盖率良好
```

---

<a id="2-reviewing-a-pull-request-on-github"></a>
## 2. 在 GitHub 上审查 Pull Request

<a id="view-pr-details"></a>
### 查看 PR 详情

**使用 gh：**

```bash
gh pr view 123
gh pr diff 123
gh pr diff 123 --name-only
```

**使用 git + curl：**

```bash
PR_NUMBER=123

# Get PR details
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

# List changed files
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/files \
  | python3 -c "
import sys, json
for f in json.load(sys.stdin):
    print(f\"{f['status']:10} +{f['additions']:-4} -{f['deletions']:-4}  {f['filename']}\")"
```

<a id="check-out-pr-locally-for-full-review"></a>
### 在本地检出 PR 进行完整审查

这与纯 `git` 配合使用——无需 `gh`：

```bash
# Fetch the PR branch and check it out
git fetch origin pull/123/head:pr-123
git checkout pr-123

# Now you can use read_file, search_files, run tests, etc.

# View diff against the base branch
git diff main...pr-123
```

**使用 gh（快捷方式）：**

```bash
gh pr checkout 123
```

<a id="leave-comments-on-a-pr"></a>
### 在 PR 上留言

**通用 PR 评论——使用 gh：**

```bash
gh pr comment 123 --body "Overall looks good, a few suggestions below."
```

**通用 PR 评论——使用 curl：**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments \
  -d '{"body": "Overall looks good, a few suggestions below."}'
```

<a id="leave-inline-review-comments"></a>
### 发表内联审查评论

**单条内联评论——使用 gh（通过 API）：**

```bash
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')

gh api repos/$OWNER/$REPO/pulls/123/comments \
  --method POST \
  -f body="This could be simplified with a list comprehension." \
  -f path="src/auth/login.py" \
  -f commit_id="$HEAD_SHA" \
  -f line=45 \
  -f side="RIGHT"
```

**单条内联评论——使用 curl：**

```bash
# Get the head commit SHA
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments \
  -d "{
    \"body\": \"This could be simplified with a list comprehension.\",
    \"path\": \"src/auth/login.py\",
    \"commit_id\": \"$HEAD_SHA\",
    \"line\": 45,
    \"side\": \"RIGHT\"
  }"
```
<a id="submit-a-formal-review-approve-request-changes"></a>
### 提交正式审查（批准 / 请求变更）

**使用 gh：**

```bash
gh pr review 123 --approve --body "LGTM！"
gh pr review 123 --request-changes --body "请查看行内评论。"
gh pr review 123 --comment --body "一些建议，不影响合并。"
```

**使用 curl —— 以原子方式提交多条评论的审查：**

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
    \"body\": \"来自 Hermes Agent 的代码审查\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"使用参数化查询以防止 SQL 注入。\"},
      {\"path\": \"src/models/user.py\", \"line\": 23, \"body\": \"在存储前使用 bcrypt 对密码进行哈希处理。\"},
      {\"path\": \"tests/test_auth.py\", \"line\": 1, \"body\": \"添加对过期令牌边缘情况的测试。\"}
    ]
  }"
```

事件取值：`"APPROVE"`、`"REQUEST_CHANGES"`、`"COMMENT"`

`line` 字段指文件*新版本*中的行号。对于已删除的行，请使用 `"side": "LEFT"`。

---

<a id="3-review-checklist"></a>
## 3. 审查清单

执行代码审查（本地或 PR 时），请系统性地检查以下方面：

<a id="correctness"></a>
### 正确性
- 代码是否实现了它声称的功能？
- 是否考虑了边缘情况（空输入、null、大数据、并发访问）？
- 错误路径是否得到妥善处理？

<a id="security"></a>
### 安全性
- 没有硬编码的密钥、凭据或 API 密钥
- 对面向用户的输入进行输入验证
- 没有 SQL 注入、XSS 或路径遍历
- 必要时进行身份验证/授权检查

<a id="code-quality"></a>
### 代码质量
- 命名清晰（变量、函数、类）
- 没有不必要的复杂性或过早的抽象
- 遵循 DRY 原则——不应有应被提取的重复逻辑
- 函数职责单一（单一职责原则）

<a id="testing"></a>
### 测试
- 新的代码路径是否已测试？
- 是否覆盖了正常路径和错误情况？
- 测试是否可读且可维护？

<a id="performance"></a>
### 性能
- 没有 N+1 查询或不必要的循环
- 在有益的地方使用了合适的缓存
- 异步代码路径中没有阻塞操作

<a id="documentation"></a>
### 文档
- 公共 API 是否已文档化
- 非显而易见的逻辑是否有注释解释“为什么”
- 如果行为发生变化，README 已更新

---

<a id="4-pre-push-review-workflow"></a>
## 4. 推送前审查工作流

当用户要求你“审查代码”或“推送前检查”时：

1. `git diff main...HEAD --stat` —— 查看变更范围
2. `git diff main...HEAD` —— 阅读完整差异
3. 对于每个变更的文件，如需更多上下文，使用 `read_file`
4. 应用上述审查清单
5. 按结构化格式呈现发现（严重问题 / 警告 / 建议 / 看起来不错）
6. 如果发现严重问题，主动在用户推送前修复它们

---

<a id="5-pr-review-workflow-end-to-end"></a>
## 5. PR 审查工作流（端到端）

当用户要求你“审查 PR #N”、“看看这个 PR”，或给你一个 PR 链接时，请遵循以下步骤：
<a id="step-1-set-up-environment"></a>
### 第 1 步：设置环境

```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"
# 或者运行本技能顶部的内联配置块
```

<a id="step-2-gather-pr-context"></a>
### 第 2 步：收集 PR 上下文

获取 PR 的元数据、描述和变更文件列表，以便在深入代码前了解范围。

**使用 `gh`：**
```bash
gh pr view 123
gh pr diff 123 --name-only
gh pr checks 123
```

**使用 `curl`：**
```bash
PR_NUMBER=123

# PR 详情（标题、作者、描述、分支）
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER

# 变更文件及行数
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls/$PR_NUMBER/files
```

<a id="step-3-check-out-the-pr-locally"></a>
### 第 3 步：在本地检出 PR

这样你就可以完整使用 `read_file`、`search_files`，并能够运行测试。

```bash
git fetch origin pull/$PR_NUMBER/head:pr-$PR_NUMBER
git checkout pr-$PR_NUMBER
```

<a id="step-4-read-the-diff-and-understand-changes"></a>
### 第 4 步：阅读 diff 并理解改动

```bash
# 与基础分支的完整 diff
git diff main...HEAD

# 或针对大型 PR 按文件逐个查看
git diff main...HEAD --name-only
# 然后对每个文件：
git diff main...HEAD -- path/to/file.py
```

对于每个变更文件，使用 `read_file` 查看变更周围的完整上下文——仅凭 diff 可能会遗漏只有结合周围代码才能发现的问题。

<a id="step-5-run-automated-checks-locally-if-applicable"></a>
### 第 5 步：在本地运行自动检查（如适用）

```bash
# 如果有测试套件则运行测试
python -m pytest 2>&1 | tail -20
# 或：npm test、cargo test、go test ./... 等

# 如果配置了 linter 则运行
ruff check . 2>&1 | head -30
# 或：eslint、clippy 等
```

<a id="step-6-apply-the-review-checklist-section-3"></a>
### 第 6 步：应用审查清单（第 3 节）

逐一检查每个类别：正确性、安全性、代码质量、测试、性能、文档。

<a id="step-7-post-the-review-to-github"></a>
### 第 7 步：将审查结果发布到 GitHub

整理你的发现，并将其作为正式的审查提交（包含行内评论）。

**使用 `gh`：**
```bash
# 如果没有问题——批准
gh pr review $PR_NUMBER --approve --body "Hermes Agent 已审查。代码看起来干净——测试覆盖良好，无安全顾虑。"

# 如果发现问题——要求修改并附带行内评论
gh pr review $PR_NUMBER --request-changes --body "发现几个问题——请参见行内评论。"
```

**使用 `curl`——包含多条行内评论的原子审查：**
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
    \"body\": \"## Hermes Agent 审查\n\n发现 2 个问题，1 个建议。请参见行内评论。\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"🔴 **严重：** 用户输入直接传递到 SQL 查询——请使用参数化查询。\"},
      {\"path\": \"src/models.py\", \"line\": 23, \"body\": \"⚠️ **警告：** 密码未经过哈希存储。\"},
      {\"path\": \"src/utils.py\", \"line\": 8, \"body\": \"💡 **建议：** 此逻辑与 core/utils.py:34 重复。\"}
    ]
  }"
```
<a id="step-8-also-post-a-summary-comment"></a>
### 步骤 8：同时发布总结评论

除了行内评论外，还要在顶层发布一条总结评论，让 PR 作者一眼就能看到全貌。请使用 `references/review-output-template.md` 中的审查输出格式。

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

<a id="step-9-clean-up"></a>
### 步骤 9：清理

```bash
git checkout main
git branch -D pr-$PR_NUMBER
```

<a id="decision-approve-vs-request-changes-vs-comment"></a>
### 决策：批准 vs 请求变更 vs 评论

- **批准** — 没有严重或警告级别的问题，只有轻微建议或全部通过
- **请求变更** — 存在任何应在合并前修复的严重或警告级别问题
- **评论** — 提出观察和建议，但无阻塞性问题（当你不确定或 PR 为草稿时使用）
