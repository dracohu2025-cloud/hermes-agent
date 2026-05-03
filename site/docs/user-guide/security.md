---
sidebar_position: 8
title: "安全"
description: "安全模型、危险命令审批、用户授权、容器隔离以及生产环境部署最佳实践"
---

# 安全 {#security}

Hermes Agent 采用纵深防御安全模型设计。本文涵盖所有安全边界——从命令审批到容器隔离，再到消息平台上的用户授权。

## 概述 {#overview}

安全模型包含七个层级：

1. **用户授权** — 谁可以与 Agent 对话（白名单、私信配对）
2. **危险命令审批** — 破坏性操作需要人工介入
3. **容器隔离** — 使用强化设置的 Docker/Singularity/Modal 沙箱
4. **MCP 凭据过滤** — MCP 子进程的环境变量隔离
5. **上下文文件扫描** — 项目文件中的提示注入检测
6. **跨会话隔离** — 会话之间无法访问彼此的数据或状态；cron 任务存储路径经过强化，可防御路径遍历攻击
7. **输入清理** — 终端工具后端的工作目录参数会通过白名单进行验证，防止 shell 注入

## 危险命令审批 {#dangerous-command-approval}

在执行任何命令之前，Hermes 会将其与精心整理的危险模式列表进行比对。如果匹配，用户必须明确批准才能执行。

### 审批模式 {#approval-modes}

审批系统支持三种模式，通过 `~/.hermes/config.yaml` 中的 `approvals.mode` 配置：

```yaml
approvals:
  mode: manual    # manual | smart | off
  timeout: 60     # 等待用户响应的秒数（默认：60）
```

| 模式 | 行为 |
|------|----------|
| **manual**（默认） | 遇到危险命令时始终提示用户审批 |
| **smart** | 使用辅助 LLM 评估风险。低风险命令（例如 `python -c "print('hello')"`）自动批准。真正危险的命令自动拒绝。不确定的情况则升级为手动提示。 |
| **off** | 禁用所有审批检查——相当于使用 `--yolo` 运行。所有命令无需提示即可执行。 |

:::warning
将 `approvals.mode` 设置为 `off` 会禁用所有安全提示。仅在受信任的环境（CI/CD、容器等）中使用。
:::

### YOLO 模式 {#yolo-mode}

YOLO 模式会绕过当前会话中**所有**危险命令的审批提示。可以通过三种方式激活：

1. **CLI 标志**：使用 `hermes --yolo` 或 `hermes chat --yolo` 启动会话
2. **斜杠命令**：在会话中输入 `/yolo` 来切换开关
3. **环境变量**：设置 `HERMES_YOLO_MODE=1`

`/yolo` 命令是一个**开关**——每次使用都会切换模式：

```
> /yolo
  ⚡ YOLO 模式已开启——所有命令自动批准。请谨慎使用。

> /yolo
  ⚠ YOLO 模式已关闭——危险命令需要审批。
```

YOLO 模式在 CLI 和网关会话中均可使用。内部实现上，它会设置 `HERMES_YOLO_MODE` 环境变量，该变量在每次执行命令前都会被检查。

:::danger
YOLO 模式会禁用会话中**所有**危险命令的安全检查——**但**硬性黑名单（见下文）除外。仅在你完全信任所生成的命令时使用（例如，在一次性环境中运行经过充分测试的自动化脚本）。
:::
### 硬性黑名单（始终生效的底线） {#hardline-blocklist-always-on-floor}

有些命令的破坏性极大——不可逆的文件系统擦除、fork 炸弹、直接块设备写入——Hermes **无论**在以下哪种情况下都拒绝执行：

- 开启了 `--yolo` / `/yolo`
- `approvals.mode: off`
- Cron 任务在无头 `approve` 模式下运行
- 用户明确点击“始终允许”

黑名单是 `--yolo` 之下的底线。它在审批层甚至看到命令之前就会**触发**，并且没有覆盖标志。当前覆盖的模式（非穷举，与 `tools/approval.py::UNRECOVERABLE_BLOCKLIST` 保持同步）：

| 模式 | 为什么是硬性 |
|---|---|
| `rm -rf /` 及明显变体 | 擦除文件系统根目录 |
| `rm -rf --no-preserve-root /` | 明确“我就是要根目录”的变体 |
| `:(){ :\|:& };:`（bash fork 炸弹） | 使主机卡死直到重启 |
| 在已挂载的根设备上执行 `mkfs.*` | 格式化正在运行的系统 |
| `dd if=/dev/zero of=/dev/sd*` | 将物理磁盘清零 |
| 在根文件系统顶层将不受信任的 URL 通过管道传给 `sh` | 远程代码执行攻击面太广，无法批准 |

如果触发了黑名单，工具调用会向 Agent 返回一条解释性错误，并且什么也不会执行。如果某个合法工作流确实需要这些命令之一（例如你是擦除并重新安装管线的操作员），请在 Agent 外部运行。

### 审批超时 {#approval-timeout}

当出现危险命令提示时，用户有可配置的响应时间。如果在超时内没有响应，命令默认被**拒绝**（故障安全关闭）。

在 `~/.hermes/config.yaml` 中配置超时：

```yaml
approvals:
  timeout: 60  # 秒（默认：60）
```

### 什么会触发审批 {#what-triggers-approval}

以下模式会触发审批提示（定义在 `tools/approval.py` 中）：

| 模式 | 描述 |
|---------|-------------|
| `rm -r` / `rm --recursive` | 递归删除 |
| `rm ... /` | 在根路径下删除 |
| `chmod 777/666` / `o+w` / `a+w` | 全局/其他用户可写权限 |
| `chmod --recursive` 配合不安全权限 | 递归全局/其他用户可写（长标志） |
| `chown -R root` / `chown --recursive root` | 递归将所有者改为 root |
| `mkfs` | 格式化文件系统 |
| `dd if=` | 磁盘复制 |
| `> /dev/sd` | 写入块设备 |
| `DROP TABLE/DATABASE` | SQL DROP |
| `DELETE FROM`（不带 WHERE） | SQL DELETE 不带 WHERE |
| `TRUNCATE TABLE` | SQL TRUNCATE |
| `> /etc/` | 覆盖系统配置 |
| `systemctl stop/restart/disable/mask` | 停止/重启/禁用/屏蔽系统服务 |
| `kill -9 -1` | 杀死所有进程 |
| `pkill -9` | 强制杀死进程 |
| Fork 炸弹模式 | Fork 炸弹 |
| `bash -c` / `sh -c` / `zsh -c` / `ksh -c` | 通过 `-c` 标志执行 shell 命令（包括组合标志如 `-lc`） |
| `python -e` / `perl -e` / `ruby -e` / `node -c` | 通过 `-e`/`-c` 标志执行脚本 |
| `curl ... \| sh` / `wget ... \| sh` | 将远程内容通过管道传给 shell |
| `bash <(curl ...)` / `sh <(wget ...)` | 通过进程替换执行远程脚本 |
| `tee` 到 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过 tee 覆盖敏感文件 |
| `>` / `>>` 到 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过重定向覆盖敏感文件 |
| `xargs rm` | xargs 配合 rm |
| `find -exec rm` / `find -delete` | 带破坏性操作的 find |
| `cp`/`mv`/`install` 到 `/etc/` | 复制/移动文件到系统配置 |
| `sed -i` / `sed --in-place` 作用于 `/etc/` | 原地编辑系统配置 |
| `pkill`/`killall` hermes/gateway | 防止自我终止 |
| `gateway run` 配合 `&`/`disown`/`nohup`/`setsid` | 防止在服务管理器之外启动 gateway |
:::info
**容器绕过**：当使用 `docker`、`singularity`、`modal`、`daytona` 或 `vercel_sandbox` 后端运行时，危险命令检查会被**跳过**，因为容器本身就是安全边界。容器内的破坏性命令不会影响宿主机。
:::

### 审批流程（CLI） {#approval-flow-cli}

在交互式 CLI 中，危险命令会显示一个内联审批提示：

```
  ⚠️  危险命令：递归删除
      rm -rf /tmp/old-project

      [o]一次  |  [s]会话  |  [a]始终  |  [d]拒绝

      选择 [o/s/a/D]：
```

四个选项：

- **once（一次）** — 允许本次执行
- **session（会话）** — 允许本次会话中继续使用该模式
- **always（始终）** — 添加到永久白名单（保存到 `config.yaml`）
- **deny（拒绝）**（默认）— 阻止该命令

### 审批流程（网关/消息平台） {#approval-flow-gateway-messaging}

在消息平台上，Agent 会将危险命令的详细信息发送到聊天中，等待用户回复：

- 回复 **yes**、**y**、**approve**、**ok** 或 **go** 表示批准
- 回复 **no**、**n**、**deny** 或 **cancel** 表示拒绝

运行网关时，`HERMES_EXEC_ASK=1` 环境变量会自动设置。

### 永久白名单 {#permanent-allowlist}

通过“始终”选项批准的命令会保存到 `~/.hermes/config.yaml`：

```yaml
# 永久允许的危险命令模式
command_allowlist:
  - rm
  - systemctl
```

这些模式会在启动时加载，并在所有后续会话中静默批准。

:::tip
使用 `hermes config edit` 查看或从永久白名单中移除模式。
:::

## 用户授权（网关） {#user-authorization-gateway}

运行消息网关时，Hermes 通过分层授权系统控制谁能与机器人交互。

### 授权检查顺序 {#authorization-check-order}

`_is_user_authorized()` 方法按以下顺序检查：

1. **平台级全部允许标志**（例如 `DISCORD_ALLOW_ALL_USERS=true`）
2. **DM 配对批准列表**（通过配对码批准的用户）
3. **平台特定白名单**（例如 `TELEGRAM_ALLOWED_USERS=12345,67890`）
4. **全局白名单**（`GATEWAY_ALLOWED_USERS=12345,67890`）
5. **全局全部允许**（`GATEWAY_ALLOW_ALL_USERS=true`）
6. **默认：拒绝**

### 平台白名单 {#platform-allowlists}

在 `~/.hermes/.env` 中以逗号分隔的值设置允许的用户 ID：

```bash
# 平台特定白名单
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=111222333444555666
WHATSAPP_ALLOWED_USERS=15551234567
SLACK_ALLOWED_USERS=U01ABC123

# 跨平台白名单（所有平台都会检查）
GATEWAY_ALLOWED_USERS=123456789

# 平台级全部允许（谨慎使用）
DISCORD_ALLOW_ALL_USERS=true

# 全局全部允许（极其谨慎使用）
GATEWAY_ALLOW_ALL_USERS=true
```

:::warning
如果**没有配置任何白名单**且未设置 `GATEWAY_ALLOW_ALL_USERS`，则**所有用户都会被拒绝**。网关会在启动时记录一条警告：

```
未配置用户白名单。所有未授权的用户将被拒绝。
请在 ~/.hermes/.env 中设置 GATEWAY_ALLOW_ALL_USERS=true 以允许开放访问，
或配置平台白名单（例如 TELEGRAM_ALLOWED_USERS=your_id）。
```
:::
### DM 配对系统 {#dm-pairing-system}

为了实现更灵活的授权，Hermes 包含一个基于代码的配对系统。无需预先提供用户 ID，未知用户会收到一个一次性配对代码，机器人所有者通过 CLI 批准该代码。

**工作原理：**

1. 未知用户向机器人发送私信
2. 机器人回复一个 8 字符的配对代码
3. 机器人所有者在 CLI 上运行 `hermes pairing approve &lt;platform&gt; &lt;code&gt;`
4. 该用户在该平台上被永久批准

在 `~/.hermes/config.yaml` 中控制如何处理未授权的私信：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。未授权的私信会收到配对代码回复。
- `ignore` 静默丢弃未授权的私信。
- 平台部分会覆盖全局默认值，因此你可以在 Telegram 上保持配对，同时让 WhatsApp 保持静默。

**安全特性**（基于 OWASP + NIST SP 800-63-4 指南）：

| 特性 | 详情 |
|---------|---------|
| 代码格式 | 8 字符，来自 32 字符无歧义字母表（不含 0/O/1/I） |
| 随机性 | 加密随机（`secrets.choice()`） |
| 代码有效期 | 1 小时过期 |
| 速率限制 | 每用户每 10 分钟 1 次请求 |
| 待处理限制 | 每平台最多 3 个待处理代码 |
| 锁定 | 5 次批准失败 → 1 小时锁定 |
| 文件安全 | 所有配对数据文件设置 `chmod 0600` |
| 日志记录 | 代码从不记录到 stdout |

**配对 CLI 命令：**

```bash
# 列出待处理和已批准的用户
hermes pairing list

# 批准配对代码
hermes pairing approve telegram ABC12DEF

# 撤销用户访问权限
hermes pairing revoke telegram 123456789

# 清除所有待处理代码
hermes pairing clear-pending
```

**存储：** 配对数据存储在 `~/.hermes/pairing/` 中，每个平台有独立的 JSON 文件：
- `{platform}-pending.json` — 待处理的配对请求
- `{platform}-approved.json` — 已批准的用户
- `_rate_limits.json` — 速率限制和锁定跟踪

## 容器隔离 {#container-isolation}

当使用 `docker` 终端后端时，Hermes 会对每个容器应用严格的安全加固。

### Docker 安全标志 {#docker-security-flags}

每个容器都使用以下标志运行（定义在 `tools/environments/docker.py` 中）：

```python
_SECURITY_ARGS = [
    "--cap-drop", "ALL",                          # 丢弃所有 Linux 能力
    "--cap-add", "DAC_OVERRIDE",                  # root 可以写入绑定挂载的目录
    "--cap-add", "CHOWN",                         # 包管理器需要文件所有权
    "--cap-add", "FOWNER",                        # 包管理器需要文件所有权
    "--security-opt", "no-new-privileges",         # 阻止权限提升
    "--pids-limit", "256",                         # 限制进程数量
    "--tmpfs", "/tmp:rw,nosuid,size=512m",         # 大小受限的 /tmp
    "--tmpfs", "/var/tmp:rw,noexec,nosuid,size=256m",  # 不可执行的 /var/tmp
    "--tmpfs", "/run:rw,noexec,nosuid,size=64m",   # 不可执行的 /run
]
```

### 资源限制 {#resource-limits}

容器资源可在 `~/.hermes/config.yaml` 中配置：
```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_forward_env: []  # 仅显式白名单；空列表可将密钥排除在容器之外
  container_cpu: 1        # CPU 核心数
  container_memory: 5120  # MB（默认 5GB）
  container_disk: 51200   # MB（默认 50GB，需要 XFS 上的 overlay2）
  container_persistent: true  # 跨会话持久化文件系统
```

### 文件系统持久化 {#filesystem-persistence}

- **持久化模式**（`container_persistent: true`）：将 `~/.hermes/sandboxes/docker/&lt;task_id&gt;/` 中的 `/workspace` 和 `/root` 绑定挂载到容器
- **临时模式**（`container_persistent: false`）：工作区使用 tmpfs——清理时所有数据都会丢失

:::tip
对于生产环境的网关部署，请使用 `docker`、`modal`、`daytona` 或 `vercel_sandbox` 后端，将 Agent 命令与主机系统隔离。这样完全不需要危险命令审批。
:::

:::warning
如果你向 `terminal.docker_forward_env` 添加了名称，这些变量会被有意注入到容器中供终端命令使用。这对于任务特定的凭据（如 `GITHUB_TOKEN`）很有用，但也意味着容器中运行的代码可以读取并泄露它们。
:::

## 终端后端安全性对比 {#terminal-backend-security-comparison}

| 后端 | 隔离性 | 危险命令检查 | 最佳适用场景 |
|---------|-----------|-------------------|----------|
| **local** | 无——在主机上运行 | ✅ 是 | 开发、受信任的用户 |
| **ssh** | 远程机器 | ✅ 是 | 在独立服务器上运行 |
| **docker** | 容器 | ❌ 跳过（容器本身就是边界） | 生产网关 |
| **singularity** | 容器 | ❌ 跳过 | HPC 环境 |
| **modal** | 云沙箱 | ❌ 跳过 | 可扩展的云隔离 |
| **daytona** | 云沙箱 | ❌ 跳过 | 持久化云工作区 |
| **vercel_sandbox** | 云微VM | ❌ 跳过 | 支持快照持久化的云执行 |

## 环境变量透传 {#environment-variable-passthrough}

`execute_code` 和 `terminal` 都会从子进程中剥离敏感的环境变量，以防止 LLM 生成的代码窃取凭据。但是，声明了 `required_environment_variables` 的技能确实需要合法地访问这些变量。

### 工作原理 {#how-it-works}

两种机制允许特定变量通过沙箱过滤器：

**1. 技能作用域透传（自动）**

当加载一个技能（通过 `skill_view` 或 `/skill` 命令）并且该技能声明了 `required_environment_variables` 时，环境中实际已设置的变量会自动注册为透传变量。尚未设置的变量（仍处于需要设置的状态）**不会**被注册。

```yaml
# 在技能的 SKILL.md frontmatter 中
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API 密钥
    help: 从 https://developers.google.com/tenor 获取密钥
```

加载此技能后，`TENOR_API_KEY` 会透传到 `execute_code`、`terminal`（本地）**以及远程后端（Docker、Modal）**——无需手动配置。
:::info Docker 和 Modal
在 v0.5.1 版本之前，Docker 的 `forward_env` 与技能透传是两套独立的系统。现在它们已合并——技能声明的环境变量会自动转发到 Docker 容器和 Modal 沙箱中，无需再手动添加到 `docker_forward_env`。
:::

**2. 基于配置的透传（手动方式）**

对于未由任何技能声明的环境变量，请将其添加到 `config.yaml` 的 `terminal.env_passthrough` 中：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

### 凭据文件透传（OAuth 令牌等）{#credential-file-passthrough}

某些技能需要在沙箱中使用**文件**（而不仅仅是环境变量）——例如，Google Workspace 将 OAuth 令牌存储为当前配置文件的 `HERMES_HOME` 目录下的 `google_token.json`。技能在 frontmatter 中声明这些文件：

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 令牌（由设置脚本创建）
  - path: google_client_secret.json
    description: Google OAuth2 客户端凭据
```

加载时，Hermes 会检查这些文件是否存在于当前配置文件的 `HERMES_HOME` 目录中，并注册它们以供挂载：

- **Docker**：只读绑定挂载（`-v host:container:ro`）
- **Modal**：在沙箱创建时挂载，并在每条命令执行前同步（处理会话中的 OAuth 设置）
- **本地**：无需操作（文件已可访问）

你也可以在 `config.yaml` 中手动列出凭据文件：

```yaml
terminal:
  credential_files:
    - google_token.json
    - my_custom_oauth_token.json
```

路径相对于 `~/.hermes/`。文件会挂载到容器内的 `/root/.hermes/` 目录。

### 各沙箱的过滤规则 {#what-each-sandbox-filters}

| 沙箱 | 默认过滤规则 | 透传覆盖 |
|---------|---------------|---------------------|
| **execute_code** | 阻止名称中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD`、`AUTH` 的变量；仅允许安全前缀变量通过 | ✅ 透传变量绕过两项检查 |
| **terminal**（本地） | 阻止显式的 Hermes 基础设施变量（提供商密钥、网关令牌、工具 API 密钥） | ✅ 透传变量绕过黑名单 |
| **terminal**（Docker） | 默认不传递主机环境变量 | ✅ 透传变量 + `docker_forward_env` 通过 `-e` 转发 |
| **terminal**（Modal） | 默认不传递主机环境/文件 | ✅ 凭据文件已挂载；环境变量通过同步透传 |
| **MCP** | 阻止除安全系统变量和显式配置的 `env` 之外的所有内容 | ❌ 不受透传影响（请改用 MCP `env` 配置） |

### 安全注意事项 {#security-considerations}

- 透传仅影响你或你的技能显式声明的变量——对于任意 LLM 生成的代码，默认安全策略保持不变
- 凭据文件以**只读**方式挂载到 Docker 容器中
- Skills Guard 在安装前会扫描技能内容，检查是否存在可疑的环境变量访问模式
- 缺失/未设置的变量永远不会被注册（不存在的东西无法泄露）
- Hermes 基础设施密钥（提供商 API 密钥、网关令牌）绝不应添加到 `env_passthrough` 中——它们有专用的机制
## MCP 凭据处理 {#mcp-credential-handling}

MCP（模型上下文协议）服务器子进程会接收一个**经过过滤的环境变量**，以防止意外泄露凭据。

### 安全环境变量 {#safe-environment-variables}

只有以下变量会从宿主机传递给 MCP stdio 子进程：

```
PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR
```

以及所有 `XDG_*` 变量。其他所有环境变量（API 密钥、令牌、机密信息）都会被**剥离**。

在 MCP 服务器的 `env` 配置中显式定义的变量会被传递：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."  # 只有这个会被传递
```

### 凭据脱敏 {#credential-redaction}

来自 MCP 工具的错误消息在返回给 LLM 之前会经过清理。以下模式会被替换为 `[REDACTED]`：

- GitHub PAT（`ghp_...`）
- OpenAI 风格的密钥（`sk-...`）
- Bearer 令牌
- `token=`、`key=`、`API_KEY=`、`password=`、`secret=` 参数

### 网站访问策略 {#website-access-policy}

你可以限制 Agent 通过其网页和浏览器工具访问哪些网站。这对于防止 Agent 访问内部服务、管理面板或其他敏感 URL 非常有用。

```yaml
# 在 ~/.hermes/config.yaml 中
security:
  website_blocklist:
    enabled: true
    domains:
      - "*.internal.company.com"
      - "admin.example.com"
    shared_files:
      - "/etc/hermes/blocked-sites.txt"
```

当请求被阻止的 URL 时，工具会返回一个错误，说明该域名已被策略阻止。此阻止列表适用于 `web_search`、`web_extract`、`browser_navigate` 以及所有支持 URL 的工具。

有关完整详情，请参阅配置指南中的[网站阻止列表](/user-guide/configuration#website-blocklist)。

### SSRF 保护 {#ssrf-protection}

所有支持 URL 的工具（网页搜索、网页提取、视觉、浏览器）在获取 URL 之前都会进行验证，以防止服务器端请求伪造（SSRF）攻击。被阻止的地址包括：

- **私有网络**（RFC 1918）：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- **回环地址**：`127.0.0.0/8`、`::1`
- **链路本地地址**：`169.254.0.0/16`（包括 `169.254.169.254` 上的云元数据）
- **CGNAT / 共享地址空间**（RFC 6598）：`100.64.0.0/10`（Tailscale、WireGuard VPN）
- **云元数据主机名**：`metadata.google.internal`、`metadata.goog`
- **保留地址、组播地址和未指定地址**

SSRF 保护在面向互联网使用时始终处于激活状态，DNS 失败会被视为被阻止（故障关闭）。重定向链会在每一步重新验证，以防止基于重定向的绕过。

#### 有意允许私有 URL {#intentionally-allowing-private-urls}

某些场景下确实需要私有/内部 URL 访问——例如将 `home.arpa` 解析到 RFC 1918 地址空间的家用网络、仅限局域网使用的 Ollama/llama.cpp 端点、内部 Wiki、云元数据调试等。针对这些情况，有一个全局退出选项：

```yaml
security:
  allow_private_urls: true   # 默认值：false
```

启用后，网页工具、浏览器、视觉 URL 获取以及网关媒体下载将不再拒绝 RFC 1918 / 回环 / 链路本地 / CGNAT / 云元数据目标。**这是一个有意的信任边界**——仅在你认为 Agent 对本地网络运行任意提示注入的 URL 是可接受风险的机器上启用。面向公众的网关应保持关闭此选项。
主机子串防护（即使底层 IP 是公网 IP，也能阻止形似 Unicode 域名的攻击）不受此设置影响，始终开启。

### Tirith 预执行安全扫描 {#tirith-pre-exec-security-scanning}

Hermes 集成了 [tirith](https://github.com/sheeki03/tirith)，用于在命令执行前进行内容级扫描。Tirith 能检测出纯模式匹配无法发现的威胁：

- 同形字 URL 欺骗（国际化域名攻击）
- 管道到解释器模式（`curl | bash`、`wget | sh`）
- 终端注入攻击

Tirith 会在首次使用时从 GitHub 发布版自动安装，并附带 SHA-256 校验和验证（如果 cosign 可用，还会进行 cosign 来源验证）。

```yaml
# 在 ~/.hermes/config.yaml 中
security:
  tirith_enabled: true       # 启用/禁用 tirith 扫描（默认：true）
  tirith_path: "tirith"      # tirith 二进制文件路径（默认：在 PATH 中查找）
  tirith_timeout: 5          # 子进程超时时间（秒）
  tirith_fail_open: true     # 当 tirith 不可用时允许执行（默认：true）
```

当 `tirith_fail_open` 为 `true`（默认值）时，如果 tirith 未安装或超时，命令仍会继续执行。在高安全环境中，请将其设为 `false`，以便在 tirith 不可用时阻止命令执行。

Tirith 的判定结果会集成到审批流程中：安全命令直接通过，而可疑和已阻止的命令会触发用户审批，并显示完整的 tirith 发现结果（严重程度、标题、描述、更安全的替代方案）。用户可以批准或拒绝——默认选择是拒绝，以确保无人值守场景的安全。

### 上下文文件注入保护 {#context-file-injection-protection}

上下文文件（AGENTS.md、.cursorrules、SOUL.md）在纳入系统提示之前会进行提示注入扫描。扫描器会检查：

- 要求忽略/无视先前指令的指令
- 包含可疑关键词的隐藏 HTML 注释
- 尝试读取机密（`.env`、`credentials`、`.netrc`）
- 通过 `curl` 泄露凭据
- 不可见 Unicode 字符（零宽空格、双向覆盖）

被阻止的文件会显示警告：

```
[已阻止：AGENTS.md 包含潜在的提示注入（prompt_injection）。内容未加载。]
```

## 生产部署最佳实践 {#best-practices-for-production-deployment}

### 网关部署检查清单 {#gateway-deployment-checklist}

1. **设置显式白名单**——切勿在生产环境中使用 `GATEWAY_ALLOW_ALL_USERS=true`
2. **使用容器后端**——在 config.yaml 中设置 `terminal.backend: docker`
3. **限制资源上限**——设置合适的 CPU、内存和磁盘限制
4. **安全存储机密**——将 API 密钥保存在 `~/.hermes/.env` 中，并设置正确的文件权限
5. **启用 DM 配对**——尽可能使用配对码代替硬编码用户 ID
6. **审查命令白名单**——定期审计 config.yaml 中的 `command_allowlist`
7. **设置 `MESSAGING_CWD`**——不要让 Agent 从敏感目录操作
8. **以非 root 用户运行**——切勿以 root 身份运行网关
9. **监控日志**——检查 `~/.hermes/logs/` 中的未授权访问尝试
10. **保持更新**——定期运行 `hermes update` 以获取安全补丁
### 保护 API 密钥 {#securing-api-keys}

```bash
# 为 .env 文件设置正确的权限
chmod 600 ~/.hermes/.env

# 为不同服务使用独立的密钥
# 切勿将 .env 文件提交到版本控制
```

### 网络隔离 {#network-isolation}

为了最大程度保障安全，请将网关运行在独立的机器或虚拟机上：

```yaml
terminal:
  backend: ssh
  ssh_host: "agent-worker.local"
  ssh_user: "hermes"
  ssh_key: "~/.ssh/hermes_agent_key"
```

这样可以将网关的消息连接与 Agent 的命令执行隔离开来。
