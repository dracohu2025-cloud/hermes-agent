---
title: "Github Auth — GitHub 认证设置：HTTPS 令牌、SSH 密钥、gh CLI 登录"
sidebar_label: "Github Auth"
description: "GitHub 认证设置：HTTPS 令牌、SSH 密钥、gh CLI 登录"
---

{/* 此页面是通过 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成的。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="github-auth"></a>
# Github Auth

GitHub 认证设置：HTTPS 令牌、SSH 密钥、gh CLI 登录。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/github-auth` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `GitHub`、`Authentication`、`Git`、`gh-cli`、`SSH`、`Setup` |
| 相关技能 | [`github-pr-workflow`](/user-guide/skills/bundled/github/github-github-pr-workflow)、[`github-code-review`](/user-guide/skills/bundled/github/github-github-code-review)、[`github-issues`](/user-guide/skills/bundled/github/github-github-issues)、[`github-repo-management`](/user-guide/skills/bundled/github/github-github-repo-management) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在此技能触发时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="github-authentication-setup"></a>
# GitHub 认证设置

此技能用于设置认证，使 Agent 能够操作 GitHub 仓库、PR、Issue 和 CI。涵盖两条路径：

- **`git`（始终可用）** — 使用 HTTPS 个人访问令牌或 SSH 密钥
- **`gh` CLI（如果已安装）** — 更丰富的 GitHub API 访问，认证流程更简单

<a id="detection-flow"></a>
## 检测流程

当用户要求你操作 GitHub 时，先运行此检查：

```bash
# 检查可用工具
git --version
gh --version 2>/dev/null || echo "gh 未安装"

# 检查是否已认证
gh auth status 2>/dev/null || echo "gh 未认证"
git config --global credential.helper 2>/dev/null || echo "git 凭据助手不存在"
```

**决策树：**
1. 如果 `gh auth status` 显示已认证 → 搞定，使用 `gh` 处理一切
2. 如果 `gh` 已安装但未认证 → 使用下面的“gh auth”方法
3. 如果 `gh` 未安装 → 使用下面的“仅 git”方法（无需 sudo）

---

<a id="method-1-git-only-authentication-no-gh-no-sudo"></a>
## 方法 1：仅使用 Git 认证（无 gh，无 sudo）

适用于任何安装了 `git` 的机器。无需 root 权限。

<a id="option-a-https-with-personal-access-token-recommended"></a>
### 选项 A：使用 HTTPS 和个人访问令牌（推荐）

这是最通用的方法——随处可用，无需配置 SSH。

**第 1 步：创建个人访问令牌**

让用户前往：**https://github.com/settings/tokens**

- 点击“Generate new token (classic)”
- 为其命名，例如“hermes-agent”
- 选择作用域：
  - `repo`（完整的仓库访问权限—读取、写入、推送、PR）
  - `workflow`（触发和管理 GitHub Actions）
  - `read:org`（如果操作组织仓库）
- 设置过期时间（90 天是一个不错的默认值）
- 复制令牌——它不会再显示

**第 2 步：配置 git 存储令牌**

```bash
# 设置凭据助手以缓存凭据
# "store" 将凭据以明文保存到 ~/.git-credentials（简单、持久）
git config --global credential.helper store

# 现在执行一个触发认证的测试操作——git 会提示输入凭据
# 用户名：<他们的 GitHub 用户名>
# 密码：<粘贴个人访问令牌，而不是他们的 GitHub 密码>
git ls-remote https://github.com/<他们的用户名>/<任意仓库>.git
```
输入一次凭据后，它们会被保存下来，并在后续所有操作中重复使用。

**替代方案：缓存辅助工具（凭据在内存中过期）**

```bash
# 在内存中缓存 8 小时（28800 秒），而不是保存到磁盘
git config --global credential.helper 'cache --timeout=28800'
```

**替代方案：将令牌直接设置在远程 URL 中（每个仓库独立设置）**

```bash
# 将令牌嵌入远程 URL（完全避免凭据提示）
git remote set-url origin https://<username>:<token>@github.com/<owner>/<repo>.git
```

**步骤 3：配置 Git 身份**

```bash
# 提交时需要——设置姓名和邮箱
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

**步骤 4：验证**

```bash
# 测试推送权限（现在应该无需任何提示即可工作）
git ls-remote https://github.com/<their-username>/<any-repo>.git

# 验证身份
git config --global user.name
git config --global user.email
```

<a id="option-b-ssh-key-authentication"></a>
### 选项 B：SSH 密钥认证

适合偏好 SSH 或已配置好密钥的用户。

**步骤 1：检查现有 SSH 密钥**

```bash
ls -la ~/.ssh/id_*.pub 2>/dev/null || echo "未找到 SSH 密钥"
```

**步骤 2：如果需要，生成一个密钥**

```bash
# 生成 ed25519 密钥（现代、安全、快速）
ssh-keygen -t ed25519 -C "their-email@example.com" -f ~/.ssh/id_ed25519 -N ""

# 显示公钥，供用户添加到 GitHub
cat ~/.ssh/id_ed25519.pub
```

告诉用户将公钥添加到：**https://github.com/settings/keys**
- 点击“New SSH key”
- 粘贴公钥内容
- 为其添加一个标题，例如“hermes-agent-&lt;machine-name>”

**步骤 3：测试连接**

```bash
ssh -T git@github.com
# 预期输出："Hi <username>! You've successfully authenticated..."
```

**步骤 4：配置 Git 对 GitHub 使用 SSH**

```bash
# 自动将 HTTPS GitHub URL 重写为 SSH
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**步骤 5：配置 Git 身份**

```bash
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

---

<a id="method-2-gh-cli-authentication"></a>
## 方法 2：gh CLI 认证

如果已安装 `gh`，它可以在一步中同时处理 API 访问和 Git 凭据。

<a id="interactive-browser-login-desktop"></a>
### 交互式浏览器登录（桌面环境）

```bash
gh auth login
# 选择：GitHub.com
# 选择：HTTPS
# 通过浏览器进行身份验证
```

<a id="token-based-login-headless-ssh-servers"></a>
### 基于令牌的登录（无头环境 / SSH 服务器）

```bash
echo "<THEIR_TOKEN>" | gh auth login --with-token

# 通过 gh 设置 Git 凭据
gh auth setup-git
```

<a id="verify"></a>
### 验证

```bash
gh auth status
```

---

<a id="using-the-github-api-without-gh"></a>
## 在没有 gh 的情况下使用 GitHub API

当 `gh` 不可用时，你仍然可以使用个人访问令牌通过 `curl` 访问完整的 GitHub API。其他 GitHub 技能就是通过这种方式实现其回退方案的。

<a id="setting-the-token-for-api-calls"></a>
### 为 API 调用设置令牌

```bash
# 选项 1：导出为环境变量（推荐——避免令牌出现在命令中）
export GITHUB_TOKEN="<token>"

# 然后在 curl 调用中使用：
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```
<a id="extracting-the-token-from-git-credentials"></a>
### 从 Git 凭据中提取 Token

如果已经通过 `credential.helper store` 配置了 Git 凭据，可以按以下方式提取 Token：

```bash
# 从 git 凭据存储中读取
grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|'
```

<a id="helper-detect-auth-method"></a>
### 辅助功能：检测认证方式

在任何 GitHub 工作流的开头使用以下模式：

```bash
# 优先尝试 gh，如果不可用则回退到 git + curl
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH_METHOD=gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "AUTH_METHOD=curl"
elif [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
  echo "AUTH_METHOD=curl"
elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
  export GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  echo "AUTH_METHOD=curl"
else
  echo "AUTH_METHOD=none"
  echo "需要先配置认证方式"
fi
```

---

<a id="troubleshooting"></a>
## 故障排查

| 问题 | 解决方案 |
|---------|----------|
| `git push` 要求输入密码 | GitHub 已禁用密码认证。请使用个人访问令牌作为密码，或切换到 SSH |
| `remote: Permission to X denied` | Token 可能缺少 `repo` 权限范围 — 请用正确的权限范围重新生成 |
| `fatal: Authentication failed` | 缓存的凭据可能已过期 — 运行 `git credential reject` 然后重新认证 |
| `ssh: connect to host github.com port 22: Connection refused` | 尝试通过 HTTPS 端口使用 SSH：在 `~/.ssh/config` 中添加 `Host github.com`，并设置 `Port 443` 和 `Hostname ssh.github.com` |
| 凭据未持久化 | 检查 `git config --global credential.helper` — 必须为 `store` 或 `cache` |
| 多个 GitHub 账号 | 在 `~/.ssh/config` 中使用不同密钥对应不同的主机别名，或使用每个仓库独立的凭据 URL |
| `gh: command not found` 且没有 sudo 权限 | 使用上面的纯 Git 方法 1 — 无需安装其他工具 |
