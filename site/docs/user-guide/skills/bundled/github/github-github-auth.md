---
title: "Github Auth — GitHub 认证设置：HTTPS 令牌、SSH 密钥、gh CLI 登录"
sidebar_label: "Github Auth"
description: "GitHub 认证设置：HTTPS 令牌、SSH 密钥、gh CLI 登录"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Github Auth {#github-auth}

GitHub 认证设置：HTTPS 令牌、SSH 密钥、gh CLI 登录。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/github-auth` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `GitHub`、`Authentication`、`Git`、`gh-cli`、`SSH`、`Setup` |
| 相关技能 | [`github-pr-workflow`](/user-guide/skills/bundled/github/github-github-pr-workflow)、[`github-code-review`](/user-guide/skills/bundled/github/github-github-code-review)、[`github-issues`](/user-guide/skills/bundled/github/github-github-issues)、[`github-repo-management`](/user-guide/skills/bundled/github/github-github-repo-management) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# GitHub 认证设置 {#github-authentication-setup}

本技能用于设置认证，使 Agent 能够与 GitHub 仓库、PR、Issue 和 CI 协作。它涵盖两种路径：

- **`git`（始终可用）** — 使用 HTTPS 个人访问令牌或 SSH 密钥
- **`gh` CLI（如果已安装）** — 通过更简单的认证流程提供更丰富的 GitHub API 访问

## 检测流程 {#detection-flow}

当用户要求你与 GitHub 协作时，请先运行此检查：

```bash
# 检查可用的工具
git --version
gh --version 2>/dev/null || echo "gh not installed"

# 检查是否已认证
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**决策树：**
1. 如果 `gh auth status` 显示已认证 → 没问题，所有操作都使用 `gh`
2. 如果 `gh` 已安装但未认证 → 使用下面的“gh auth”方法
3. 如果 `gh` 未安装 → 使用下面的“仅 git”方法（无需 sudo）

---

## 方法 1：仅 Git 认证（无 gh，无 sudo） {#method-1-git-only-authentication-no-gh-no-sudo}

此方法适用于任何安装了 `git` 的机器，无需 root 权限。

### 选项 A：使用个人访问令牌的 HTTPS（推荐） {#option-a-https-with-personal-access-token-recommended}

这是最便携的方法——随处可用，无需 SSH 配置。

**步骤 1：创建个人访问令牌**

告诉用户前往：**https://github.com/settings/tokens**

- 点击“Generate new token (classic)”
- 为其命名，例如“hermes-agent”
- 选择作用域：
  - `repo`（完整仓库访问——读取、写入、推送、PR）
  - `workflow`（触发和管理 GitHub Actions）
  - `read:org`（如果使用组织仓库）
- 设置过期时间（90 天是一个不错的默认值）
- 复制令牌——它不会再次显示

**步骤 2：配置 git 存储令牌**

```bash
# 设置凭据助手以缓存凭据
# "store" 将凭据以明文形式保存到 ~/.git-credentials（简单、持久）
git config --global credential.helper store

# 现在执行一个测试操作来触发认证——git 会提示输入凭据
# 用户名：<他们的 GitHub 用户名>
# 密码：<粘贴个人访问令牌，而不是他们的 GitHub 密码>
git ls-remote https://github.com/<他们的用户名>/<任意仓库>.git
```
输入一次凭据后，它们会被保存下来，并在后续所有操作中重复使用。

**替代方案：缓存助手（凭据在内存中过期）**

```bash
# 在内存中缓存 8 小时（28800 秒），而不是保存到磁盘
git config --global credential.helper 'cache --timeout=28800'
```

**替代方案：将令牌直接设置在远程 URL 中（每个仓库独立设置）**

```bash
# 将令牌嵌入远程 URL（完全避免凭据提示）
git remote set-url origin https://<用户名>:<令牌>@github.com/<所有者>/<仓库>.git
```

**第 3 步：配置 Git 身份信息**

```bash
# 提交时需要——设置姓名和邮箱
git config --global user.name "他们的姓名"
git config --global user.email "their-email@example.com"
```

**第 4 步：验证**

```bash
# 测试推送权限（现在应该无需任何提示即可工作）
git ls-remote https://github.com/<他们的用户名>/<任意仓库>.git

# 验证身份信息
git config --global user.name
git config --global user.email
```

### 选项 B：SSH 密钥认证 {#option-b-ssh-key-authentication}

适合偏好 SSH 或已设置好密钥的用户。

**第 1 步：检查现有 SSH 密钥**

```bash
ls -la ~/.ssh/id_*.pub 2>/dev/null || echo "未找到 SSH 密钥"
```

**第 2 步：如果需要，生成密钥**

```bash
# 生成 ed25519 密钥（现代、安全、快速）
ssh-keygen -t ed25519 -C "their-email@example.com" -f ~/.ssh/id_ed25519 -N ""

# 显示公钥，供用户添加到 GitHub
cat ~/.ssh/id_ed25519.pub
```

告诉用户将公钥添加到：**https://github.com/settings/keys**
- 点击“New SSH key”
- 粘贴公钥内容
- 为其添加一个标题，例如“hermes-agent-&lt;机器名&gt;”

**第 3 步：测试连接**

```bash
ssh -T git@github.com
# 预期输出："Hi <用户名>! You've successfully authenticated..."
```

**第 4 步：配置 Git 对 GitHub 使用 SSH**

```bash
# 自动将 HTTPS GitHub URL 重写为 SSH
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**第 5 步：配置 Git 身份信息**

```bash
git config --global user.name "他们的姓名"
git config --global user.email "their-email@example.com"
```

---

## 方法 2：gh CLI 认证 {#method-2-gh-cli-authentication}

如果已安装 `gh`，它可以在一步内同时处理 API 访问和 Git 凭据。

### 交互式浏览器登录（桌面端） {#interactive-browser-login-desktop}

```bash
gh auth login
# 选择：GitHub.com
# 选择：HTTPS
# 通过浏览器进行身份验证
```

### 基于令牌的登录（无头 / SSH 服务器） {#token-based-login-headless-ssh-servers}

```bash
echo "<他们的令牌>" | gh auth login --with-token

# 通过 gh 设置 Git 凭据
gh auth setup-git
```

### 验证 {#verify}

```bash
gh auth status
```

---

## 在没有 gh 的情况下使用 GitHub API {#using-the-github-api-without-gh}

当 `gh` 不可用时，你仍然可以使用 `curl` 配合个人访问令牌来访问完整的 GitHub API。其他 GitHub 技能就是通过这种方式实现其回退方案的。

### 为 API 调用设置令牌 {#setting-the-token-for-api-calls}

```bash
# 选项 1：导出为环境变量（推荐——避免令牌出现在命令中）
export GITHUB_TOKEN="<令牌>"

# 然后在 curl 调用中使用：
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```
### 从 Git 凭据中提取 Token {#extracting-the-token-from-git-credentials}

如果已通过 `credential.helper store` 配置了 Git 凭据，可以提取 Token：

```bash
# 从 git 凭据存储中读取
grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|'
```

### 辅助工具：检测认证方式 {#helper-detect-auth-method}

在任何 GitHub 工作流的开头使用此模式：

```bash
# 先尝试 gh，回退到 git + curl
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
  echo "Need to set up authentication first"
fi
```

---

## 故障排除 {#troubleshooting}

| 问题 | 解决方案 |
|---------|----------|
| `git push` 要求输入密码 | GitHub 已禁用密码认证。请使用个人访问令牌作为密码，或切换到 SSH |
| `remote: Permission to X denied` | Token 可能缺少 `repo` 权限范围——请使用正确的权限范围重新生成 |
| `fatal: Authentication failed` | 缓存的凭据可能已过期——运行 `git credential reject` 然后重新认证 |
| `ssh: connect to host github.com port 22: Connection refused` | 尝试通过 HTTPS 端口使用 SSH：在 `~/.ssh/config` 中添加 `Host github.com`，并设置 `Port 443` 和 `Hostname ssh.github.com` |
| 凭据未持久化 | 检查 `git config --global credential.helper`——必须为 `store` 或 `cache` |
| 多个 GitHub 账户 | 在 `~/.ssh/config` 中为每个主机别名使用不同的 SSH 密钥，或使用每个仓库的凭据 URL |
| `gh: command not found` + 没有 sudo 权限 | 使用上面仅限 git 的方法 1——无需安装 |
