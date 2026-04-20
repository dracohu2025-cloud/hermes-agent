---
sidebar_position: 8
title: "安全"
description: "安全模型、危险命令审批、用户授权、容器隔离以及生产部署最佳实践"
---

# 安全 {#security}

Hermes Agent 采用纵深防御安全模型设计。本页面涵盖了从命令审批到容器隔离，再到即时通讯平台用户授权的每一个安全边界。

## 概览 {#overview}

该安全模型包含七层防护：

1. **用户授权** —— 谁可以与 Agent 对话（白名单、私聊配对）
2. **危险命令审批** —— 针对破坏性操作的人机回环（human-in-the-loop）
3. **容器隔离** —— 具有加固设置的 Docker/Singularity/Modal 沙箱
4. **MCP 凭据过滤** —— MCP 子进程的环境变量隔离
5. **上下文文件扫描** —— 项目文件中的提示词注入检测
6. **跨会话隔离** —— 会话之间无法访问彼此的数据或状态；定时任务（cron job）存储路径经过加固，防止路径遍历攻击
7. **输入清理** —— 终端工具后端的当前工作目录参数会根据白名单进行验证，以防止 Shell 注入

## 危险命令审批 {#dangerous-command-approval}

在执行任何命令之前，Hermes 会根据一份精心挑选的危险模式列表进行检查。如果发现匹配项，用户必须明确批准。

### 审批模式 {#approval-modes}

审批系统支持三种模式，通过 `~/.hermes/config.yaml` 中的 `approvals.mode` 进行配置：

```yaml
approvals:
  mode: manual    # manual | smart | off
  timeout: 60     # 等待用户响应的秒数（默认：60）
```

| 模式 | 行为 |
|------|----------|
| **manual** (默认) | 遇到危险命令时始终提示用户审批 |
| **smart** | 使用辅助 LLM 评估风险。低风险命令（如 `python -c "print('hello')"`）自动批准。真正危险的命令自动拒绝。不确定的情况转为手动提示。 |
| **off** | 禁用所有审批检查 —— 相当于带 `--yolo` 参数运行。所有命令无需提示直接执行。 |

:::warning
将 `approvals.mode: off` 会禁用所有安全提示。请仅在受信任的环境（CI/CD、容器等）中使用。
:::

### YOLO 模式 {#yolo-mode}

YOLO 模式会绕过当前会话的**所有**危险命令审批提示。可以通过三种方式激活：

1. **CLI 标志**：使用 `hermes --yolo` 或 `hermes chat --yolo` 启动会话
2. **斜杠命令**：在会话期间输入 `/yolo` 来切换开启/关闭
3. **环境变量**：设置 `HERMES_YOLO_MODE=1`

`/yolo` 命令是一个**开关** —— 每次使用都会切换模式：

```
> /yolo
  ⚡ YOLO 模式开启 — 所有命令将自动批准。请谨慎使用。

> /yolo
  ⚠ YOLO 模式关闭 — 危险命令将需要审批。
```

YOLO 模式在 CLI 和 Gateway 会话中均可用。在内部，它会设置 `HERMES_YOLO_MODE` 环境变量，该变量在每次命令执行前都会被检查。

:::danger
YOLO 模式会禁用该会话的所有危险命令安全检查。请仅在您完全信任生成的命令时使用（例如，在一次性环境中使用经过充分测试的自动化脚本）。
:::

### 审批超时 {#approval-timeout}

当出现危险命令提示时，用户有可配置的时间进行响应。如果在超时时间内未给出响应，命令默认会被**拒绝**（故障关闭/fail-closed）。

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
| `rm ... /` | 在根路径删除 |
| `chmod 777/666` / `o+w` / `a+w` | 所有人/其他用户可写权限 |
| `chmod --recursive` 配合不安全权限 | 递归设置所有人/其他用户可写（长标志） |
| `chown -R root` / `chown --recursive root` | 递归更改所有者为 root |
| `mkfs` | 格式化文件系统 |
| `dd if=` | 磁盘复制 |
| `> /dev/sd` | 写入块设备 |
| `DROP TABLE/DATABASE` | SQL DROP 操作 |
| `DELETE FROM` (不带 WHERE) | 不带 WHERE 条件的 SQL DELETE |
| `TRUNCATE TABLE` | SQL TRUNCATE 操作 |
| `> /etc/` | 覆盖系统配置 |
| `systemctl stop/disable/mask` | 停止/禁用系统服务 |
| `kill -9 -1` | 杀死所有进程 |
| `pkill -9` | 强制杀死进程 |
| Fork 炸弹模式 | Fork 炸弹 |
| `bash -c` / `sh -c` / `zsh -c` / `ksh -c` | 通过 `-c` 标志执行 Shell 命令（包括 `-lc` 等组合标志） |
| `python -e` / `perl -e` / `ruby -e` / `node -c` | 通过 `-e`/`-c` 标志执行脚本 |
| `curl ... \| sh` / `wget ... \| sh` | 将远程内容通过管道传给 Shell |
| `bash <(curl ...)` / `sh <(wget ...)` | 通过进程替换执行远程脚本 |
| `tee` 写入 `/etc/`, `~/.ssh/`, `~/.hermes/.env` | 通过 tee 覆盖敏感文件 |
| `>` / `>>` 写入 `/etc/`, `~/.ssh/`, `~/.hermes/.env` | 通过重定向覆盖敏感文件 |
| `xargs rm` | xargs 配合 rm |
| `find -exec rm` / `find -delete` | find 配合破坏性操作 |
| `cp`/`mv`/`install` 到 `/etc/` | 复制/移动文件到系统配置目录 |
| `sed -i` / `sed --in-place` 操作 `/etc/` | 就地编辑系统配置 |
| `pkill`/`killall` hermes/gateway | 防止自我终止 |
| `gateway run` 配合 `&`/`disown`/`nohup`/`setsid` | 防止在服务管理器之外启动 Gateway |

:::info
**容器绕过**：当在 `docker`、`singularity`、`modal` 或 `daytona` 后端运行时，危险命令检查会被**跳过**，因为容器本身就是安全边界。容器内的破坏性命令无法伤害宿主机。
:::

### 审批流程 (CLI) {#approval-flow-cli}

在交互式 CLI 中，危险命令会显示行内审批提示：

```
  ⚠️  危险命令：递归删除
      rm -rf /tmp/old-project

      [o]nce (一次) | [s]ession (会话) | [a]lways (始终) | [d]eny (拒绝)

      选择 [o/s/a/D]:
```

四个选项：

- **once** — 允许执行这一次
- **session** — 在本次会话的剩余时间内允许此模式
- **always** — 添加到永久白名单（保存到 `config.yaml`）
- **deny** (默认) — 拦截该命令

### 审批流程 (Gateway/即时通讯) {#approval-flow-gateway-messaging}

在即时通讯平台上，Agent 会将危险命令详情发送到聊天中并等待用户回复：

- 回复 **yes**、**y**、**approve**、**ok** 或 **go** 表示批准
- 回复 **no**、**n**、**deny** 或 **cancel** 表示拒绝

运行 Gateway 时会自动设置 `HERMES_EXEC_ASK=1` 环境变量。

### 永久白名单 {#permanent-allowlist}

使用 "always" 批准的命令会保存到 `~/.hermes/config.yaml`：

```yaml
# 永久允许的危险命令模式
command_allowlist:
  - rm
  - systemctl
```

这些模式在启动时加载，并在未来的所有会话中静默批准。

:::tip
使用 `hermes config edit` 来查看或从永久白名单中删除模式。
:::

## 用户授权 (Gateway) {#user-authorization-gateway}

运行即时通讯 Gateway 时，Hermes 通过分层授权系统控制谁可以与机器人交互。

### 授权检查顺序 {#authorization-check-order}

`_is_user_authorized()` 方法按以下顺序检查：

1. **平台级全员允许标志**（例如 `DISCORD_ALLOW_ALL_USERS=true`）
2. **私聊配对批准列表**（通过配对码批准的用户）
3. **平台特定白名单**（例如 `TELEGRAM_ALLOWED_USERS=12345,67890`）
4. **全局白名单** (`GATEWAY_ALLOWED_USERS=12345,67890`)
5. **全局全员允许** (`GATEWAY_ALLOW_ALL_USERS=true`)
6. **默认：拒绝**

### 平台白名单 {#platform-allowlists}

在 `~/.hermes/.env` 中以逗号分隔的值设置允许的用户 ID：

```bash
# 平台特定白名单
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=111222333444555666
WHATSAPP_ALLOWED_USERS=15551234567
SLACK_ALLOWED_USERS=U01ABC123

# 跨平台白名单（对所有平台生效）
GATEWAY_ALLOWED_USERS=123456789

# 平台级全员允许（请谨慎使用）
DISCORD_ALLOW_ALL_USERS=true

# 全局全员允许（请极端谨慎使用）
GATEWAY_ALLOW_ALL_USERS=true
```

:::warning
如果**未配置任何白名单**且未设置 `GATEWAY_ALLOW_ALL_USERS`，**所有用户都将被拒绝**。Gateway 在启动时会记录一条警告：

```
No user allowlists configured. All unauthorized users will be denied.
Set GATEWAY_ALLOW_ALL_USERS=true in ~/.hermes/.env to allow open access,
or configure platform allowlists (e.g., TELEGRAM_ALLOWED_USERS=your_id).
```
:::
### DM 配对系统 {#dm-pairing-system}

为了提供更灵活的授权方式，Hermes 包含了一个基于代码的配对系统。无需预先要求用户 ID，未知用户会收到一个一次性配对码，Bot 所有者可以通过 CLI 批准该代码。

**工作原理：**

1. 未知用户向 Bot 发送私信（DM）
2. Bot 回复一个 8 位字符的配对码
3. Bot 所有者在 CLI 上运行 `hermes pairing approve <platform> <code>`
4. 该用户在该平台上获得永久批准

在 `~/.hermes/config.yaml` 中可以控制如何处理未经授权的私信：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。未经授权的私信会收到配对码回复。
- `ignore` 会静默丢弃未经授权的私信。
- 平台特定配置会覆盖全局默认设置，因此你可以保持 Telegram 开启配对，同时让 WhatsApp 保持静默。

**安全特性**（基于 OWASP + NIST SP 800-63-4 指南）：

| 特性 | 详情 |
|---------|---------|
| 代码格式 | 8 位字符，取自 32 位无歧义字母表（不含 0/O/1/I） |
| 随机性 | 加密级随机 (`secrets.choice()`) |
| 代码有效期 (TTL) | 1 小时过期 |
| 速率限制 | 每个用户每 10 分钟 1 次请求 |
| 待处理限制 | 每个平台最多 3 个待处理代码 |
| 锁定机制 | 5 次批准尝试失败 → 锁定 1 小时 |
| 文件安全 | 对所有配对数据文件执行 `chmod 0600` |
| 日志记录 | 代码永远不会记录到标准输出 (stdout) |

**配对 CLI 命令：**

```bash
# 列出待处理和已批准的用户
hermes pairing list

# 批准一个配对码
hermes pairing approve telegram ABC12DEF

# 撤销用户的访问权限
hermes pairing revoke telegram 123456789

# 清除所有待处理的代码
hermes pairing clear-pending
```

**存储：** 配对数据存储在 `~/.hermes/pairing/` 目录下，按平台划分为 JSON 文件：
- `{platform}-pending.json` — 待处理的配对请求
- `{platform}-approved.json` — 已批准的用户
- `_rate_limits.json` — 速率限制和锁定跟踪

## 容器隔离 {#container-isolation}

当使用 `docker` 终端后端时，Hermes 会对每个容器应用严格的安全加固。

### Docker 安全标志 {#docker-security-flags}

每个容器运行时都带有以下标志（定义在 `tools/environments/docker.py` 中）：

```python
_SECURITY_ARGS = [
    "--cap-drop", "ALL",                          # 丢弃所有 Linux 能力
    "--cap-add", "DAC_OVERRIDE",                  # 允许 Root 写入绑定挂载的目录
    "--cap-add", "CHOWN",                         # 包管理器需要文件所有权权限
    "--cap-add", "FOWNER",                        # 包管理器需要文件所有权权限
    "--security-opt", "no-new-privileges",         # 阻止权限提升
    "--pids-limit", "256",                         # 限制进程数量
    "--tmpfs", "/tmp:rw,nosuid,size=512m",         # 限制大小的 /tmp
    "--tmpfs", "/var/tmp:rw,noexec,nosuid,size=256m",  # 禁止执行的 /var/tmp
    "--tmpfs", "/run:rw,noexec,nosuid,size=64m",   # 禁止执行的 /run
]
```

### 资源限制 {#resource-limits}

容器资源可在 `~/.hermes/config.yaml` 中配置：

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_forward_env: []  # 仅限显式允许列表；为空则防止 Secret 进入容器
  container_cpu: 1        # CPU 核心数
  container_memory: 5120  # MB (默认 5GB)
  container_disk: 51200   # MB (默认 50GB，需要在 XFS 上开启 overlay2)
  container_persistent: true  # 跨会话持久化文件系统
```

### 文件系统持久化 {#filesystem-persistence}

- **持久模式** (`container_persistent: true`): 将 `~/.hermes/sandboxes/docker/<task_id>/` 中的 `/workspace` 和 `/root` 进行绑定挂载。
- **临时模式** (`container_persistent: false`): 为工作区使用 tmpfs —— 清理时所有内容都会丢失。

:::tip
对于生产环境的网关部署，请使用 `docker`、`modal` 或 `daytona` 后端，将 Agent 命令与宿主系统隔离。这样可以完全不需要危险命令批准流程。
:::

:::warning
如果你在 `terminal.docker_forward_env` 中添加了变量名，这些变量会被有意注入到容器中供终端命令使用。这对于 `GITHUB_TOKEN` 等任务特定的凭据很有用，但也意味着容器中运行的代码可以读取并外泄这些变量。
:::

## 终端后端安全对比 {#terminal-backend-security-comparison}

| 后端 | 隔离性 | 危险命令检查 | 最适合场景 |
|---------|-----------|-------------------|----------|
| **local** | 无 — 在宿主机运行 | ✅ 是 | 开发环境、受信任用户 |
| **ssh** | 远程机器 | ✅ 是 | 在独立服务器上运行 |
| **docker** | 容器 | ❌ 跳过（容器即边界） | 生产网关 |
| **singularity** | 容器 | ❌ 跳过 | HPC 环境 |
| **modal** | 云端沙箱 | ❌ 跳过 | 可扩展的云端隔离 |
| **daytona** | 云端沙箱 | ❌ 跳过 | 持久化云端工作区 |

## 环境变量透传 {#environment-variable-passthrough}

`execute_code` 和 `terminal` 都会从子进程中剥离敏感环境变量，以防止 LLM 生成的代码外泄凭据。然而，声明了 `required_environment_variables` 的 Skill 确实需要访问这些变量。

### 工作原理 {#how-it-works}

有两种机制允许特定变量通过沙箱过滤器：

**1. Skill 作用域透传（自动）**

当加载一个 Skill（通过 `skill_view` 或 `/skill` 命令）且该 Skill 声明了 `required_environment_variables` 时，环境中实际设置的任何此类变量都会自动注册为透传。缺失的变量（仍处于“需要设置”状态）**不会**被注册。

```yaml
# 在 Skill 的 SKILL.md frontmatter 中
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: 从 https://developers.google.com/tenor 获取 Key
```

加载此 Skill 后，`TENOR_API_KEY` 将透传至 `execute_code`、`terminal`（本地）**以及远程后端（Docker, Modal）** —— 无需手动配置。

:::info Docker & Modal
在 v0.5.1 之前，Docker 的 `forward_env` 与 Skill 透传是独立的系统。现在它们已合并 —— Skill 声明的环境变量会自动转发到 Docker 容器和 Modal 沙箱中，无需再手动添加到 `docker_forward_env`。
:::

**2. 基于配置的透传（手动）**

对于未被任何 Skill 声明的环境变量，请将其添加到 `config.yaml` 中的 `terminal.env_passthrough`：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

### 凭据文件透传（OAuth 令牌等） {#credential-file-passthrough}

某些 Skill 需要沙箱中的**文件**（不仅仅是环境变量）—— 例如，Google Workspace 将 OAuth 令牌存储为当前 Profile 的 `HERMES_HOME` 下的 `google_token.json`。Skill 在 frontmatter 中声明这些文件：

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 令牌（由设置脚本创建）
  - path: google_client_secret.json
    description: Google OAuth2 客户端凭据
```

加载时，Hermes 会检查这些文件是否存在于当前 Profile 的 `HERMES_HOME` 中，并注册它们以进行挂载：

- **Docker**: 只读绑定挂载 (`-v host:container:ro`)
- **Modal**: 在沙箱创建时挂载，并在每个命令前同步（处理会话中途的 OAuth 设置）
- **Local**: 无需操作（文件已可访问）

你也可以在 `config.yaml` 中手动列出凭据文件：

```yaml
terminal:
  credential_files:
    - google_token.json
    - my_custom_oauth_token.json
```

路径相对于 `~/.hermes/`。文件会被挂载到容器内的 `/root/.hermes/`。

### 各沙箱的过滤规则 {#what-each-sandbox-filters}

| 沙箱 | 默认过滤器 | 透传覆盖 |
|---------|---------------|---------------------|
| **execute_code** | 拦截名称中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD`、`AUTH` 的变量；仅允许带安全前缀的变量通过 | ✅ 透传变量会绕过这两项检查 |
| **terminal** (local) | 拦截显式的 Hermes 基础设施变量（Provider Key、网关 Token、工具 API Key） | ✅ 透传变量会绕过黑名单 |
| **terminal** (Docker) | 默认不透传宿主环境变量 | ✅ 透传变量 + `docker_forward_env` 通过 `-e` 转发 |
| **terminal** (Modal) | 默认不透传宿主环境/文件 | ✅ 挂载凭据文件；通过同步透传环境变量 |
| **MCP** | 拦截除安全系统变量和显式配置的 `env` 之外的所有内容 | ❌ 不受透传影响（请改用 MCP 的 `env` 配置） |
### 安全注意事项 {#security-considerations}

- 透传（passthrough）仅影响你或你的 Skill 明确声明的变量 —— 对于 LLM 生成的任意代码，默认安全态势保持不变。
- 凭据文件以**只读**方式挂载到 Docker 容器中。
- Skills Guard 会在安装前扫描 Skill 内容，检查是否存在可疑的环境变量访问模式。
- 缺失或未设置的变量永远不会被注册（你无法泄露不存在的东西）。
- Hermes 基础设施机密（Provider API 密钥、Gateway 令牌）绝不应添加到 `env_passthrough` 中 —— 它们有专门的存储机制。

## MCP 凭据处理 {#mcp-credential-handling}

MCP（Model Context Protocol）服务器子进程会接收到一个**经过过滤的环境**，以防止意外的凭据泄露。

### 安全环境变量 {#safe-environment-variables}

只有以下变量会从宿主机传递给 MCP stdio 子进程：

```
PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR
```

以及任何 `XDG_*` 变量。所有其他环境变量（API 密钥、令牌、机密）都会被**剥离**。

在 MCP 服务器的 `env` 配置中明确定义的变量会被透传：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."  # 只有这个会被传递
```

### 凭据脱敏 {#credential-redaction}

来自 MCP 工具的错误消息在返回给 LLM 之前会进行清理。以下模式将被替换为 `[REDACTED]`：

- GitHub PATs (`ghp_...`)
- OpenAI 风格的密钥 (`sk-...`)
- Bearer 令牌
- `token=`, `key=`, `API_KEY=`, `password=`, `secret=` 等参数

<a id="website-access-policy"></a>
### 网站访问策略 {#website-blocklist}

你可以限制 Agent 通过其 Web 和浏览器工具访问哪些网站。这对于防止 Agent 访问内部服务、管理面板或其他敏感 URL 非常有用。

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

当请求被拦截的 URL 时，工具会返回一个错误，说明该域名已被策略拦截。该黑名单在 `web_search`、`web_extract`、`browser_navigate` 以及所有具备 URL 处理能力的工具中强制执行。

详见配置指南中的 [网站黑名单](/user-guide/configuration#website-blocklist)。

### SSRF 防护 {#ssrf-protection}

所有具备 URL 处理能力的工具（Web 搜索、Web 提取、视觉、浏览器）在获取 URL 之前都会进行验证，以防止服务端请求伪造（SSRF）攻击。被拦截的地址包括：

- **私有网络** (RFC 1918): `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
- **回环地址**: `127.0.0.0/8`, `::1`
- **链路本地地址**: `169.254.0.0/16`（包括位于 `169.254.169.254` 的云元数据）
- **CGNAT / 共享地址空间** (RFC 6598): `100.64.0.0/10`（Tailscale, WireGuard VPNs）
- **云元数据主机名**: `metadata.google.internal`, `metadata.goog`
- **保留、组播及未指定地址**

SSRF 防护始终处于开启状态且无法禁用。DNS 解析失败将被视为拦截（故障关闭）。重定向链在每一跳都会重新验证，以防止基于重定向的绕过。

### Tirith 执行前安全扫描 {#tirith-pre-exec-security-scanning}

Hermes 集成了 [tirith](https://github.com/sheeki03/tirith)，用于在执行前对命令进行内容级扫描。Tirith 可以检测到仅靠模式匹配会遗漏的威胁：

- 同形异义词 URL 欺骗（国际化域名攻击）
- 管道传输至解释器模式（`curl | bash`, `wget | sh`）
- 终端注入攻击

Tirith 在首次使用时会从 GitHub releases 自动安装，并进行 SHA-256 校验和验证（如果 cosign 可用，还会进行 cosign 来源验证）。

```yaml
# 在 ~/.hermes/config.yaml 中
security:
  tirith_enabled: true       # 启用/禁用 tirith 扫描（默认：true）
  tirith_path: "tirith"      # tirith 二进制文件路径（默认：在 PATH 中查找）
  tirith_timeout: 5          # 子进程超时秒数
  tirith_fail_open: true     # 当 tirith 不可用时是否允许执行（默认：true）
```

当 `tirith_fail_open` 为 `true`（默认值）时，如果 tirith 未安装或超时，命令将继续执行。在高度安全的场景中，请将其设置为 `false`，以便在 tirith 不可用时拦截命令。

Tirith 的判定结果会集成到审批流中：安全的命令直接通过，而可疑和被拦截的命令都会触发用户审批，并显示完整的 tirith 发现项（严重程度、标题、描述、更安全的替代方案）。用户可以选择批准或拒绝 —— 默认选择为拒绝，以确保无人值守场景下的安全。

### 上下文文件注入防护 {#context-file-injection-protection}

上下文文件（AGENTS.md, .cursorrules, SOUL.md）在包含进系统提示词（System Prompt）之前，会进行提示词注入（Prompt Injection）扫描。扫描器会检查：

- 忽略/无视之前指令的指示
- 带有可疑关键词的隐藏 HTML 注释
- 尝试读取机密信息（`.env`, `credentials`, `.netrc`）
- 通过 `curl` 窃取凭据
- 不可见的 Unicode 字符（零宽空格、双向覆盖字符）

被拦截的文件会显示警告：

```
[BLOCKED: AGENTS.md contained potential prompt injection (prompt_injection). Content not loaded.]
```

## 生产环境部署最佳实践 {#best-practices-for-production-deployment}

### Gateway 部署检查清单 {#gateway-deployment-checklist}

1. **设置明确的允许列表** —— 生产环境中绝不要使用 `GATEWAY_ALLOW_ALL_USERS=true`
2. **使用容器后端** —— 在 config.yaml 中设置 `terminal.backend: docker`
3. **限制资源配额** —— 设置合理的 CPU、内存和磁盘限制
4. **安全存储机密** —— 将 API 密钥保存在 `~/.hermes/.env` 中并设置正确的权限
5. **启用 DM 配对** —— 尽可能使用配对码，而不是硬编码用户 ID
6. **审查命令允许列表** —— 定期审计 config.yaml 中的 `command_allowlist`
7. **设置 `MESSAGING_CWD`** —— 不要让 Agent 在敏感目录下操作
8. **以非 root 用户运行** —— 绝不要以 root 身份运行 Gateway
9. **监控日志** —— 检查 `~/.hermes/logs/` 是否有未经授权的访问尝试
10. **保持更新** —— 定期运行 `hermes update` 以获取安全补丁

### 保护 API 密钥 {#securing-api-keys}

```bash
# 为 .env 文件设置正确的权限
chmod 600 ~/.hermes/.env

# 为不同服务保留独立的密钥
# 绝不要将 .env 文件提交到版本控制系统
```

### 网络隔离 {#network-isolation}

为了获得最高安全性，请在独立的机器或虚拟机上运行 Gateway：

```yaml
terminal:
  backend: ssh
  ssh_host: "agent-worker.local"
  ssh_user: "hermes"
  ssh_key: "~/.ssh/hermes_agent_key"
```

这可以将 Gateway 的消息连接与 Agent 的命令执行环境隔离开来。
