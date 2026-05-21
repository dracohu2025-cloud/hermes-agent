---
title: "1Password — 安装和使用 1Password CLI (op)"
sidebar_label: "1Password"
description: "安装和使用 1Password CLI (op)"
---

{/* 本页面是从技能的 SKILL.md 由 website/scripts/generate-skill-docs.py 自动生成的。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="1password"></a>
# 1Password

安装和使用 1Password CLI (op)。在安装 CLI、启用桌面应用集成、登录以及读取/注入命令所需机密时使用。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/security/1password` 安装 |
| 路径 | `optional-skills/security/1password` |
| 版本 | `1.0.0` |
| 作者 | arceus77-7, enhanced by Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `security`, `secrets`, `1password`, `op`, `cli` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是在此技能被触发时 Hermes 加载的完整技能定义。这是技能激活后 Agent 看到的指令。
:::

<a id="1password-cli"></a>
# 1Password CLI

当用户希望通过 1Password 管理机密，而不是使用明文环境变量或文件时，使用此技能。

<a id="requirements"></a>
## 前提条件

- 1Password 账户
- 已安装 1Password CLI (`op`)
- 以下其中一种：桌面应用集成、服务账户令牌 (`OP_SERVICE_ACCOUNT_TOKEN`) 或 Connect 服务器
- 在 Hermes 终端调用期间需要 `tmux` 以支持稳定的已认证会话（仅限桌面应用流程）

<a id="when-to-use"></a>
## 何时使用

- 安装或配置 1Password CLI
- 使用 `op signin` 登录
- 读取如 `op://Vault/Item/field` 这样的机密引用
- 通过 `op inject` 将机密注入配置/模板
- 通过 `op run` 运行包含机密环境变量的命令

<a id="authentication-methods"></a>
## 认证方式

<a id="service-account-recommended-for-hermes"></a>
### 服务账户（推荐用于 Hermes）

在 `~/.hermes/.env` 中设置 `OP_SERVICE_ACCOUNT_TOKEN`（该技能会在首次加载时提示输入）。
无需桌面应用。支持 `op read`、`op inject`、`op run`。

```bash
export OP_SERVICE_ACCOUNT_TOKEN="your-token-here"
op whoami  # 验证 — 应显示 Type: SERVICE_ACCOUNT
```

<a id="desktop-app-integration-interactive"></a>
### 桌面应用集成（交互式）

1. 在 1Password 桌面应用中启用：设置 → 开发者 → 集成 1Password CLI
2. 确保应用已解锁
3. 运行 `op signin` 并批准生物识别提示

<a id="connect-server-self-hosted"></a>
### Connect 服务器（自托管）

```bash
export OP_CONNECT_HOST="http://localhost:8080"
export OP_CONNECT_TOKEN="your-connect-token"
```

<a id="setup"></a>
## 安装

1. 安装 CLI：

```bash
# macOS
brew install 1password-cli

# Linux（官方包/安装文档）
# 参见 references/get-started.md 获取各发行版的具体链接。

# Windows（winget）
winget install AgileBits.1Password.CLI
```

2. 验证：

```bash
op --version
```

3. 选择上述一种认证方式并配置。

<a id="hermes-execution-pattern-desktop-app-flow"></a>
## Hermes 执行模式（桌面应用流程）

Hermes 终端命令默认是非交互式的，并且可能在多次调用之间丢失认证上下文。
为了在桌面应用集成下可靠使用 `op`，可以在专用的 tmux 会话中执行登录和机密操作。

注意：使用 `OP_SERVICE_ACCOUNT_TOKEN` 时不需要此操作 — 令牌会在终端调用之间自动持久化。

```bash
SOCKET_DIR="${TMPDIR:-/tmp}/hermes-tmux-sockets"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/hermes-op.sock"
SESSION="op-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell

# 登录（在提示时批准桌面应用中的请求）
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "eval \"\$(op signin --account my.1password.com)\"" Enter

# 验证认证状态
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op whoami" Enter

# 示例读取
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op read 'op://Private/Npmjs/one-time password?attribute=otp'" Enter

# 在需要时捕获输出
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200

# 清理
tmux -S "$SOCKET" kill-session -t "$SESSION"
```
<a id="common-operations"></a>
## 常见操作

<a id="read-a-secret"></a>
### 读取密钥

```bash
op read "op://app-prod/db/password"
```

<a id="get-otp"></a>
### 获取一次性密码（OTP）

```bash
op read "op://app-prod/npm/one-time password?attribute=otp"
```

<a id="inject-into-template"></a>
### 注入到模板中

```bash
echo "db_password: {{ op://app-prod/db/password }}" | op inject
```

<a id="run-a-command-with-secret-env-var"></a>
### 使用密钥环境变量运行命令

```bash
export DB_PASSWORD="op://app-prod/db/password"
op run -- sh -c '[ -n "$DB_PASSWORD" ] && echo "DB_PASSWORD is set" || echo "DB_PASSWORD missing"'
```

<a id="guardrails"></a>
## 安全注意事项

- 除非用户明确请求，否则切勿直接将原始密钥内容打印给用户。
- 优先使用 `op run` / `op inject`，而不是将密钥写入文件。
- 如果命令失败并提示 "account is not signed in"，在同一 tmux 会话中重新运行 `op signin`。
- 如果桌面应用集成不可用（无头环境/CI），请使用服务账户令牌流程。

<a id="ci-headless-note"></a>
## CI / 无头环境说明

对于非交互式使用，请使用 `OP_SERVICE_ACCOUNT_TOKEN` 进行身份验证，避免交互式 `op signin`。
服务账户需要 CLI v2.18.0 或更高版本。

<a id="references"></a>
## 参考文献

- `references/get-started.md`
- `references/cli-examples.md`
- https://developer.1password.com/docs/cli/
- https://developer.1password.com/docs/service-accounts/
