---
title: "1Password — 设置和使用 1Password CLI (op)"
sidebar_label: "1Password"
description: "设置和使用 1Password CLI (op)"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 1Password {#1password}

设置和使用 1Password CLI (op)。在安装 CLI、启用桌面应用集成、登录以及为命令读取/注入密钥时使用。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/security/1password` 安装 |
| 路径 | `optional-skills/security/1password` |
| 版本 | `1.0.0` |
| 作者 | arceus77-7，由 Hermes Agent 增强 |
| 许可证 | MIT |
| 标签 | `security`, `secrets`, `1password`, `op`, `cli` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 1Password CLI {#1password-cli}

当用户希望使用 1Password 管理密钥，而不是使用明文环境变量或文件时，使用此技能。

## 前提条件 {#requirements}

- 1Password 账户
- 已安装 1Password CLI (`op`)
- 以下之一：桌面应用集成、服务账户令牌 (`OP_SERVICE_ACCOUNT_TOKEN`) 或 Connect 服务器
- 在 Hermes 终端调用期间，`tmux` 可用于稳定的已认证会话（仅限桌面应用流程）

## 何时使用 {#when-to-use}

- 安装或配置 1Password CLI
- 使用 `op signin` 登录
- 读取类似 `op://Vault/Item/field` 的密钥引用
- 使用 `op inject` 将密钥注入配置/模板
- 通过 `op run` 运行带有密钥环境变量的命令

## 认证方法 {#authentication-methods}

### 服务账户（推荐用于 Hermes） {#service-account-recommended-for-hermes}

在 `~/.hermes/.env` 中设置 `OP_SERVICE_ACCOUNT_TOKEN`（技能会在首次加载时提示设置）。
无需桌面应用。支持 `op read`、`op inject`、`op run`。

```bash
export OP_SERVICE_ACCOUNT_TOKEN="your-token-here"
op whoami  # 验证 — 应显示 Type: SERVICE_ACCOUNT
```

### 桌面应用集成（交互式） {#desktop-app-integration-interactive}

1. 在 1Password 桌面应用中启用：设置 → 开发者 → 与 1Password CLI 集成
2. 确保应用已解锁
3. 运行 `op signin` 并批准生物识别提示

### Connect 服务器（自托管） {#connect-server-self-hosted}

```bash
export OP_CONNECT_HOST="http://localhost:8080"
export OP_CONNECT_TOKEN="your-connect-token"
```

## 设置 {#setup}

1. 安装 CLI：

```bash
# macOS
brew install 1password-cli

# Linux（官方包/安装文档）
# 有关特定发行版的链接，请参阅 references/get-started.md。

# Windows（winget）
winget install AgileBits.1Password.CLI
```

2. 验证：

```bash
op --version
```

3. 选择上述一种认证方法并进行配置。

## Hermes 执行模式（桌面应用流程） {#hermes-execution-pattern-desktop-app-flow}

Hermes 终端命令默认是非交互式的，并且可能在多次调用之间丢失认证上下文。
为了在桌面应用集成中可靠地使用 `op`，请在专用的 tmux 会话中运行登录和密钥操作。

注意：使用 `OP_SERVICE_ACCOUNT_TOKEN` 时**不需要**此操作——令牌会在终端调用之间自动持久化。

```bash
SOCKET_DIR="${TMPDIR:-/tmp}/hermes-tmux-sockets"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/hermes-op.sock"
SESSION="op-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell

# 登录（在提示时批准桌面应用）
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "eval \"\$(op signin --account my.1password.com)\"" Enter

# 验证认证
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op whoami" Enter

# 示例读取
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op read 'op://Private/Npmjs/one-time password?attribute=otp'" Enter

# 需要时捕获输出
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200

# 清理
tmux -S "$SOCKET" kill-session -t "$SESSION"
```
## 常见操作 {#common-operations}

### 读取密钥 {#read-a-secret}

```bash
op read "op://app-prod/db/password"
```

### 获取一次性密码（OTP） {#get-otp}

```bash
op read "op://app-prod/npm/one-time password?attribute=otp"
```

### 注入到模板中 {#inject-into-template}

```bash
echo "db_password: {{ op://app-prod/db/password }}" | op inject
```

### 使用密钥环境变量运行命令 {#run-a-command-with-secret-env-var}

```bash
export DB_PASSWORD="op://app-prod/db/password"
op run -- sh -c '[ -n "$DB_PASSWORD" ] && echo "DB_PASSWORD 已设置" || echo "DB_PASSWORD 缺失"'
```

## 安全防护 {#guardrails}

- 除非用户明确请求，否则切勿将原始密钥打印回给用户。
- 优先使用 `op run` / `op inject`，而不是将密钥写入文件。
- 如果命令因“账户未登录”而失败，请在同一个 tmux 会话中再次运行 `op signin`。
- 如果桌面应用集成不可用（无头环境/CI），请使用服务账户令牌流程。

## CI / 无头环境说明 {#ci-headless-note}

对于非交互式使用，请使用 `OP_SERVICE_ACCOUNT_TOKEN` 进行身份验证，并避免交互式 `op signin`。
服务账户需要 CLI v2.18.0+ 版本。

## 参考文档 {#references}

- `references/get-started.md`
- `references/cli-examples.md`
- https://developer.1password.com/docs/cli/
- https://developer.1password.com/docs/service-accounts/
