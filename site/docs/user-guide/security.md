---
sidebar_position: 8
title: "安全"
description: "安全模型、危险命令审批、用户授权、容器隔离及生产部署最佳实践"
---

<a id="security"></a>
# 安全

Hermes Agent 采用纵深防御安全模型设计。本文介绍所有安全边界——从命令审批到容器隔离，再到消息平台上的用户授权。

<a id="overview"></a>
## 概述

安全模型共有七个层次：

1. **用户授权** — 谁能与 Agent 对话（白名单、私信配对）
2. **危险命令审批** — 破坏性操作需要人工参与
3. **容器隔离** — 使用强化设置的 Docker/Singularity/Modal 沙箱
4. **MCP 凭据过滤** — MCP 子进程的环境变量隔离
5. **上下文文件扫描** — 检测项目文件中的提示注入
6. **跨会话隔离** — 会话间无法访问彼此的数据或状态；cron 任务存储路径已加固，可抵御路径遍历攻击
7. **输入清理** — 终端工具后端的工作目录参数需经过白名单验证，以防止 Shell 注入

<a id="dangerous-command-approval"></a>
## 危险命令审批

在执行任何命令之前，Hermes 会将其与一份精心维护的危险模式列表进行比对。如果匹配到危险模式，用户必须明确批准才能执行。

<a id="approval-modes"></a>
### 审批模式

审批系统支持三种模式，通过 `~/.hermes/config.yaml` 中的 `approvals.mode` 配置：

```yaml
approvals:
  mode: manual    # manual | smart | off
  timeout: 60     # 等待用户响应的秒数（默认：60）
```

| 模式 | 行为 |
|------|------|
| **manual**（默认） | 对危险命令始终提示用户审批 |
| **smart** | 使用辅助 LLM 评估风险。低风险命令（例如 `python -c "print('hello')"`）自动批准；真正危险的命令自动拒绝；不确定的情况升级为手动提示。 |
| **off** | 禁用所有审批检查——等同于使用 `--yolo` 运行。所有命令无需提示即可执行。 |

:::warning
将 `approvals.mode` 设置为 `off` 会禁用所有安全提示。仅在受信任环境中使用（CI/CD、容器等）。
:::

<a id="yolo-mode"></a>
### YOLO 模式

YOLO 模式会绕过当前会话中所有危险命令的审批提示。可通过三种方式激活：

1. **CLI 标志**：使用 `hermes --yolo` 或 `hermes chat --yolo` 启动会话
2. **斜杠命令**：在会话中输入 `/yolo` 来开关
3. **环境变量**：设置 `HERMES_YOLO_MODE=1`

`/yolo` 命令是一个**开关**——每次使用都会翻转模式：

```
> /yolo
  ⚡ YOLO 模式已开启——所有命令自动批准。请谨慎使用。

> /yolo
  ⚠ YOLO 模式已关闭——危险命令需要审批。
```

YOLO 模式在 CLI 和网关会话中均可使用。内部实现上，它设置了 `HERMES_YOLO_MODE` 环境变量，每次执行命令前都会检查该变量。

当 YOLO 激活时，Hermes 会显示两个持续的视觉提醒，提醒用户审批提示已被绕过：

- 会话启动时若 YOLO 已激活，会显示红色横幅行：`⚠ YOLO 模式 — 所有审批提示已被绕过`。当 YOLO 关闭时该横幅隐藏，保持默认横幅简洁。
- 在所有宽度等级的状态栏中显示 `⚠ YOLO` 片段，当您开启或关闭 YOLO 时实时更新（富文本渲染器及纯文本回退均支持）。
:::danger
YOLO 模式会在当前会话中禁用**所有**危险命令的安全检查——但**硬线阻止列表**（见下文）除外。仅在你完全信任所生成的命令时使用（例如，在一次性环境中经过充分测试的自动化脚本）。
:::

对于破坏性的会话斜杠命令（`/clear`、`/new`、`/reset`、`/undo`、`/exit --delete`），CLI 也会在执行前弹出确认提示。请参考[斜杠命令——破坏性命令的确认提示](../reference/slash-commands.md#confirmation-prompts-for-destructive-commands)。

<a id="hardline-blocklist-always-on-floor"></a>
### 硬线阻止列表（始终开启的底线）

有些命令过于灾难性——不可恢复的文件系统擦除、fork 炸弹、直接块设备写入——无论以下设置如何，Hermes 都**拒绝**执行：

- 开启 `--yolo` / `/yolo`
- `approvals.mode: off`
- Cron 任务在无头 `approve` 模式下运行
- 用户明确点击“始终允许”

阻止列表是 `--yolo` 之下的底线。它会在审批层看到命令**之前**触发，并且没有覆盖标志。当前覆盖的模式（并非详尽列表；与 `tools/approval.py::UNRECOVERABLE_BLOCKLIST` 保持同步）：

| 模式 | 为什么是硬底线 |
|---|---|
| `rm -rf /` 及明显的变体 | 擦除文件系统根目录 |
| `rm -rf --no-preserve-root /` | 明确“是的，我就是要根目录”的变体 |
| `:(){ :\|:& };:`（bash fork 炸弹）| 使主机卡死直到重启 |
| 在已挂载的根设备上执行 `mkfs.*` | 格式化正在运行的系统 |
| `dd if=/dev/zero of=/dev/sd*` | 将物理磁盘写零 |
| 在根文件系统顶层将不受信任的 URL 通过管道传给 `sh` | 远程代码执行攻击向量过于宽泛，无法批准 |

如果触发了阻止列表，工具调用会向 Agent 返回一条解释性错误，并且什么也不会执行。如果某个合法的工作流程需要这些命令之一（例如，你是擦除并重新安装管道的操作员），请在 Agent 外部执行它。

<a id="approval-timeout"></a>
### 审批超时

当出现危险命令提示时，用户有一定的时间来响应。如果在超时时间内没有给出响应，则默认**拒绝**该命令（故障关闭）。

在 `~/.hermes/config.yaml` 中配置超时：

```yaml
approvals:
  timeout: 60  # 秒（默认：60）
```

<a id="what-triggers-approval"></a>
### 什么会触发审批

以下模式会触发审批提示（定义在 `tools/approval.py` 中）：

| 模式 | 描述 |
|---------|-------------|
| `rm -r` / `rm --recursive` | 递归删除 |
| `rm ... /` | 在根路径中删除 |
| `chmod 777/666` / `o+w` / `a+w` | 世界/其他用户可写权限 |
| `chmod --recursive` 加上不安全的权限 | 递归的世界/其他用户可写（长标志） |
| `chown -R root` / `chown --recursive root` | 递归地将所有权改为 root |
| `mkfs` | 格式化文件系统 |
| `dd if=` | 磁盘复制 |
| `> /dev/sd` | 写入块设备 |
| `DROP TABLE/DATABASE` | SQL DROP |
| `DELETE FROM`（没有 WHERE）| SQL 不带 WHERE 的 DELETE |
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
| `tee` 写入 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过 tee 覆盖敏感文件 |
| `>` / `>>` 重定向到 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过重定向覆盖敏感文件 |
| `xargs rm` | xargs 搭配 rm |
| `find -exec rm` / `find -delete` | find 搭配破坏性操作 |
| `cp`/`mv`/`install` 到 `/etc/` | 复制/移动文件到系统配置 |
| `sed -i` / `sed --in-place` 对 `/etc/` | 原地编辑系统配置 |
| `pkill`/`killall` hermes/gateway | 防止自终止 |
| `gateway run` 带有 `&`/`disown`/`nohup`/`setsid` | 阻止在服务管理器之外启动 gateway |
:::info
**容器绕过**：当使用 `docker`、`singularity`、`modal`、`daytona` 或 `vercel_sandbox` 后端运行时，危险命令检查会被**跳过**，因为容器本身就是安全边界。容器内部的破坏性命令无法危害宿主机。
:::

<a id="approval-flow-cli"></a>
### 批准流程（CLI）

在交互式 CLI 中，危险命令会显示一个内联批准提示框：

```
  ⚠️  DANGEROUS COMMAND: recursive delete
      rm -rf /tmp/old-project

      [o]nce  |  [s]ession  |  [a]lways  |  [d]eny

      Choice [o/s/a/D]:
```

四个选项：

- **once**（一次）—— 允许本次单次执行
- **session**（会话）—— 允许当前会话内继续执行该模式
- **always**（总是）—— 加入永久允许列表（保存到 `config.yaml`）
- **deny**（拒绝，默认）—— 阻止该命令

<a id="approval-flow-gateway-messaging"></a>
### 批准流程（网关/消息平台）

在消息平台上，Agent 会将危险命令详情发送到聊天中，等待用户回复：

- 回复 **yes**、**y**、**approve**、**ok** 或 **go** 表示批准
- 回复 **no**、**n**、**deny** 或 **cancel** 表示拒绝

运行网关时，`HERMES_EXEC_ASK=1` 环境变量会被自动设置。

<a id="permanent-allowlist"></a>
### 永久允许列表

通过“always”选项批准的命令会保存到 `~/.hermes/config.yaml`：

```yaml
# 永久允许的危险命令模式
command_allowlist:
  - rm
  - systemctl
```

这些模式会在启动时加载，并在后续所有会话中静默批准。

:::tip
使用 `hermes config edit` 可以查看或从永久允许列表中移除模式。
:::

<a id="user-authorization-gateway"></a>
## 用户授权（网关）

在运行消息网关时，Hermes 通过分层授权系统控制谁能与机器人交互。

<a id="authorization-check-order"></a>
### 授权检查顺序

`_is_user_authorized()` 方法按以下顺序检查：

1. **特定平台的全局允许标志**（例如 `DISCORD_ALLOW_ALL_USERS=true`）
2. **私信配对批准列表**（通过配对码批准的用户）
3. **平台特定的允许列表**（例如 `TELEGRAM_ALLOWED_USERS=12345,67890`）
4. **全局允许列表**（`GATEWAY_ALLOWED_USERS=12345,67890`）
5. **全局允许全部**（`GATEWAY_ALLOW_ALL_USERS=true`）
6. **默认：拒绝**

<a id="platform-allowlists"></a>
### 平台允许列表

在 `~/.hermes/.env` 中以逗号分隔的值设置允许的用户 ID：

```bash
# 平台特定的允许列表
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=111222333444555666
WHATSAPP_ALLOWED_USERS=15551234567
SLACK_ALLOWED_USERS=U01ABC123

# 跨平台允许列表（所有平台均检查）
GATEWAY_ALLOWED_USERS=123456789

# 特定平台允许全部（谨慎使用）
DISCORD_ALLOW_ALL_USERS=true

# 全局允许全部（极其谨慎使用）
GATEWAY_ALLOW_ALL_USERS=true
```

:::warning
如果**未配置任何允许列表**且未设置 `GATEWAY_ALLOW_ALL_USERS`，则**所有用户都会被拒绝**。网关会在启动时记录警告：

```
No user allowlists configured. All unauthorized users will be denied.
Set GATEWAY_ALLOW_ALL_USERS=true in ~/.hermes/.env to allow open access,
or configure platform allowlists (e.g., TELEGRAM_ALLOWED_USERS=your_id).
```
:::
<a id="dm-pairing-system"></a>
### DM 配对系统 {#dm-pairing-system}

为了实现更灵活的授权，Hermes 包含了一个基于代码的配对系统。不需要预先提供用户ID，未知用户会收到一次性的配对码，机器人所有者通过 CLI 批准该配对码。

**工作原理：**

1. 未知用户给机器人发送一条私信
2. 机器人回复一个 8 字符的配对码
3. 机器人所有者在 CLI 上运行 `hermes pairing approve &lt;platform&gt; &lt;code&gt;`
4. 该用户在该平台上被永久批准

在 `~/.hermes/config.yaml` 中控制如何处理未经授权的私信：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认行为。未经授权的私信会收到配对码回复。
- `ignore` 会静默丢弃未经授权的私信。
- 平台配置段会覆盖全局默认值，因此你可以保持 Telegram 进行配对，同时让 WhatsApp 保持静默。

**安全特性**（基于 OWASP + NIST SP 800-63-4 指南）：

| 特性 | 详情 |
|---------|---------|
| 代码格式 | 从32字符无歧义字母表中取8字符（不含0/O/1/I） |
| 随机性 | 密码学安全（`secrets.choice()`） |
| 代码有效期 | 1小时过期 |
| 速率限制 | 每个用户每10分钟1次请求 |
| 待处理限制 | 每个平台最多3个待处理代码 |
| 锁定 | 5次批准失败尝试 → 锁定1小时 |
| 文件安全 | 对所有配对数据文件设置 `chmod 0600` |
| 日志记录 | 代码永远不会记录到标准输出 |

**配对 CLI 命令：**

```bash
# 列出待处理和已批准的用户
hermes pairing list

# 批准一个配对码
hermes pairing approve telegram ABC12DEF

# 撤销用户访问权限
hermes pairing revoke telegram 123456789

# 清除所有待处理代码
hermes pairing clear-pending
```

**存储：** 配对数据存储在 `~/.hermes/pairing/` 中，包含每个平台的 JSON 文件：
- `{platform}-pending.json` — 待处理的配对请求
- `{platform}-approved.json` — 已批准的用户
- `_rate_limits.json` — 速率限制和锁定追踪

<a id="container-isolation"></a>
## 容器隔离

当使用 `docker` 终端后端时，Hermes 对每个容器应用严格的安全加固。

<a id="docker-security-flags"></a>
### Docker 安全标志

每个容器都使用以下标志运行（定义在 `tools/environments/docker.py` 中）：

```python
_SECURITY_ARGS = [
    "--cap-drop", "ALL",                          # 丢弃所有 Linux 能力
    "--cap-add", "DAC_OVERRIDE",                  # Root 可以写入绑定挂载的目录
    "--cap-add", "CHOWN",                         # 包管理器需要文件所有权
    "--cap-add", "FOWNER",                        # 包管理器需要文件所有权
    "--security-opt", "no-new-privileges",         # 阻止权限提升
    "--pids-limit", "256",                         # 限制进程数量
    "--tmpfs", "/tmp:rw,nosuid,size=512m",         # 大小限制的 /tmp
    "--tmpfs", "/var/tmp:rw,noexec,nosuid,size=256m",  # 不可执行的 /var/tmp
    "--tmpfs", "/run:rw,noexec,nosuid,size=64m",   # 不可执行的 /run
]
```

<a id="resource-limits"></a>
### 资源限制

容器资源可以在 `~/.hermes/config.yaml` 中配置：
```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_forward_env: []  # 仅显式白名单；空的列表将密钥排除在容器之外
  container_cpu: 1        # CPU 核心数
  container_memory: 5120  # MB（默认5GB）
  container_disk: 51200   # MB（默认50GB，需要 XFS 上的 overlay2）
  container_persistent: true  # 跨会话持久化文件系统
```

<a id="filesystem-persistence"></a>
### 文件系统持久性

- **持久模式**（`container_persistent: true`）：将 `/workspace` 和 `/root` 从 `~/.hermes/sandboxes/docker/&lt;task_id&gt;/` 绑定挂载
- **临时模式**（`container_persistent: false`）：对工作区使用 tmpfs —— 清理后所有内容都将丢失

:::tip
对于生产环境的网关部署，请使用 `docker`、`modal`、`daytona` 或 `vercel_sandbox` 后端，将 Agent 命令与主机系统隔离。这完全消除了危险命令审批的必要性。
:::

:::warning
如果你将名称添加到 `terminal.docker_forward_env`，这些变量会被有意注入到容器中供终端命令使用。这对于 `GITHUB_TOKEN` 等特定任务的凭据很有用，但这也意味着容器中运行的代码可以读取并泄露它们。
:::

<a id="terminal-backend-security-comparison"></a>
## 终端后端安全对比

| 后端 | 隔离级别 | 危险命令检查 | 适用场景 |
|---------|-----------|-------------------|----------|
| **local** | 无 — 在宿主机上运行 | ✅ 是 | 开发、受信任用户 |
| **ssh** | 远程机器 | ✅ 是 | 在独立服务器上运行 |
| **docker** | 容器 | ❌ 跳过（容器即边界） | 生产网关 |
| **singularity** | 容器 | ❌ 跳过 | HPC 环境 |
| **modal** | 云端沙箱 | ❌ 跳过 | 可扩展的云端隔离 |
| **daytona** | 云端沙箱 | ❌ 跳过 | 持久化的云端工作区 |
| **vercel_sandbox** | 云端微虚拟机 | ❌ 跳过 | 带有快照持久化的云端执行 |

## 环境变量透传 {#environment-variable-passthrough}

`execute_code` 和 `terminal` 都会从子进程中剥离敏感的环境变量，以防止 LLM 生成的代码泄露凭据。然而，声明了 `required_environment_variables` 的技能需要合法访问这些变量。

<a id="how-it-works"></a>
### 工作原理

两种机制允许特定变量通过沙箱过滤器：

**1. 技能级透传（自动）**

当加载一个技能（通过 `skill_view` 或 `/skill` 命令）且该技能声明了 `required_environment_variables` 时，其中实际在环境中设置的变量会自动注册为透传。缺失的变量（仍处于需要设置状态）**不会**被注册。

```yaml
# 在技能的 SKILL.md 前置元数据中
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API 密钥
    help: 从 https://developers.google.com/tenor 获取密钥
```

加载此技能后，`TENOR_API_KEY` 会透传到 `execute_code`、`terminal`（本地）**以及远程后端（Docker、Modal）** —— 无需手动配置。
:::info Docker 和 Modal
在 v0.5.1 之前，Docker 的 `forward_env` 是一个与技能传递（skill passthrough）分离的系统。现在它们已经合并——技能声明的环境变量会自动转发到 Docker 容器和 Modal 沙箱中，无需手动添加到 `docker_forward_env`。
:::

**2. 基于配置的传递（手动方式）**

对于未被任何技能声明的环境变量，在 `config.yaml` 的 `terminal.env_passthrough` 中添加它们：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

### 凭据文件传递（OAuth 令牌等）{#credential-file-passthrough}

某些技能需要在沙箱中用到**文件**（而不仅仅是环境变量）——例如，Google Workspace 将 OAuth 令牌存储为当前活动配置文件下 `HERMES_HOME` 中的 `google_token.json`。技能在 frontmatter 中声明这些文件：

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 令牌（由设置脚本生成）
  - path: google_client_secret.json
    description: Google OAuth2 客户端凭据
```

加载时，Hermes 会检查这些文件是否存在于活动配置文件的 `HERMES_HOME` 中，并注册它们以便挂载：

- **Docker**：只读绑定挂载（`-v host:container:ro`）
- **Modal**：在创建沙箱时挂载，并在每个命令执行前同步（处理会话期间的 OAuth 设置）
- **本地**：无需操作（文件已可访问）

你也可以在 `config.yaml` 中手动列出凭据文件：

```yaml
terminal:
  credential_files:
    - google_token.json
    - my_custom_oauth_token.json
```

路径相对于 `~/.hermes/`。文件会被挂载到容器内的 `/root/.hermes/`。

<a id="what-each-sandbox-filters"></a>
### 各沙箱过滤的内容

| 沙箱 | 默认过滤规则 | 传递覆盖 |
|---------|---------------|---------------------|
| **execute_code** | 阻止名称包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD`、`AUTH` 的变量；只允许安全前缀变量通过 | ✅ 传递变量绕过两种检查 |
| **terminal**（本地） | 阻止显式的 Hermes 基础设施变量（提供商密钥、网关令牌、工具 API 密钥） | ✅ 传递变量绕过黑名单 |
| **terminal**（Docker） | 默认不传递任何主机环境变量 | ✅ 传递变量 + `docker_forward_env` 通过 `-e` 转发 |
| **terminal**（Modal） | 默认不传递任何主机环境变量/文件 | ✅ 凭据文件被挂载；环境变量通过同步传递 |
| **MCP** | 阻止除安全系统变量 + 显式配置的 `env` 之外的所有内容 | ❌ 不受传递影响（改用 MCP `env` 配置） |

<a id="security-considerations"></a>
### 安全注意事项

- 传递仅影响你或你的技能显式声明的变量——对于任意 LLM 生成的代码，默认安全状态不变
- 凭据文件以**只读**方式挂载到 Docker 容器中
- Skills Guard 会在安装前扫描技能内容中可疑的环境变量访问模式
- 缺失/未设置的变量永远不会被注册（你无法泄露不存在的东西）
- Hermes 基础设施机密（提供商 API 密钥、网关令牌）绝不应添加到 `env_passthrough` 中——它们有专门的机制
<a id="mcp-credential-handling"></a>
## MCP 凭据处理

MCP（模型上下文协议）服务端子进程会接收一个**经过过滤的环境**，以防止意外泄漏凭据。

<a id="safe-environment-variables"></a>
### 安全环境变量

只有以下变量会从主机传递给 MCP stdio 子进程：

```
PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR
```

以及所有 `XDG_*` 变量。其他所有环境变量（API 密钥、令牌、机密）都会被**剥离**。

在 MCP 服务器的 `env` 配置中显式定义的变量会直接传递：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."  # 只有这个会被传递
```

<a id="credential-redaction"></a>
### 凭据脱敏

MCP 工具返回的错误消息会在返回给 LLM 之前被清理。以下模式会被替换为 `[已脱敏]`：

- GitHub PAT（`ghp_...`）
- 类 OpenAI 密钥（`sk-...`）
- Bearer 令牌
- `token=`、`key=`、`API_KEY=`、`password=`、`secret=` 参数

<a id="website-access-policy"></a>
### 网站访问策略

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

当请求被阻止的 URL 时，工具会返回一个错误，说明该域名已被策略阻止。此黑名单适用于 `web_search`、`web_extract`、`browser_navigate` 以及所有支持 URL 的工具。

详细信息请参阅配置指南中的[网站黑名单](/user-guide/configuration#website-blocklist)。

<a id="ssrf-protection"></a>
### SSRF 防护

所有支持 URL 的工具（网页搜索、网页提取、视觉、浏览器）在获取 URL 之前都会进行验证，以防止服务器端请求伪造（SSRF）攻击。被阻止的地址包括：

- **私有网络**（RFC 1918）：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- **环回地址**：`127.0.0.0/8`、`::1`
- **链路本地地址**：`169.254.0.0/16`（包括 `169.254.169.254` 上的云元数据）
- **CGNAT / 共享地址空间**（RFC 6598）：`100.64.0.0/10`（Tailscale、WireGuard VPN）
- **云元数据主机名**：`metadata.google.internal`、`metadata.goog`
- **保留、组播和未指定地址**

对于面向公网的使用场景，SSRF 防护始终处于激活状态，DNS 解析失败也会被视为被阻止（故障关闭）。重定向链中的每一跳都会重新验证，以防止基于重定向的绕过。

<a id="intentionally-allowing-private-urls"></a>
#### 有意允许私有 URL

某些场景需要合法的私有/内部 URL 访问——例如将 `home.arpa` 解析到 RFC 1918 地址的家庭网络、仅限局域网的 Ollama/llama.cpp 端点、内部 Wiki、云元数据调试等。针对这些情况，有一个全局退出选项：

```yaml
security:
  allow_private_urls: true   # 默认：false
```

开启后，网页工具、浏览器、视觉 URL 获取以及网关媒体下载将不再拒绝 RFC 1918 / 环回 / 链路本地 / CGNAT / 云元数据目标。**这是一个刻意的信任边界**——请仅在允许 Agent 在本地网络上运行任意提示注入 URL 且风险可接受的机器上启用。面向公网的网关应保持其关闭。
主机子串保护（即使在底层IP是公开的情况下，也能拦截伪装Unicode域名的技巧）不受此设置影响，始终开启。

<a id="tirith-pre-exec-security-scanning"></a>
### Tirith 预执行安全扫描

Hermes 集成了 [tirith](https://github.com/sheeki03/tirith)，用于在执行前对命令进行内容级扫描。Tirith 能检测出单纯模式匹配无法发现的威胁：

- 同形字 URL 欺骗（国际化域名攻击）
- 通过管道送入解释器的模式（`curl | bash`、`wget | sh`）
- 终端注入攻击

Tirith 会在首次使用时从 GitHub releases 自动安装，并附带 SHA-256 校验和验证（如果 cosign 可用，还会进行 cosign 来源验证）。

```yaml
# 在 ~/.hermes/config.yaml 中
security:
  tirith_enabled: true       # 启用/禁用 tirith 扫描（默认值：true）
  tirith_path: "tirith"      # tirith 二进制文件的路径（默认值：查找 PATH）
  tirith_timeout: 5          # 子进程超时时间（秒）
  tirith_fail_open: true     # 当 tirith 不可用时是否允许执行（默认值：true）
```

当 `tirith_fail_open` 为 `true`（默认值）时，如果 tirith 未安装或超时，命令仍会继续执行。在安全要求高的环境中，应将其设为 `false`，以在 tirith 不可用时阻止命令执行。

Tirith 提供适用于 Linux（x86_64 / aarch64）和 macOS（x86_64 / arm64）的预编译二进制文件。在没有预编译二进制文件的平台（Windows 等）上，tirith 会被静默跳过——模式匹配防护仍会运行，CLI 也不会显示“不可用”的提示。要在 Windows 上使用 tirith，请在 WSL 下运行 Hermes。

Tirith 的判定结果会与审批流程集成：安全的命令直接通过，而可疑和已阻止的命令会触发用户审批，并显示完整的 tirith 分析结果（严重程度、标题、描述、更安全的替代方案）。用户可以批准或拒绝——默认选项是拒绝，以确保无人值守场景的安全。

<a id="context-file-injection-protection"></a>
### 上下文文件注入保护

上下文文件（AGENTS.md、.cursorrules、SOUL.md）在纳入系统提示之前，会进行提示注入扫描。扫描器会检查以下内容：

- 要求忽略/无视先前指令的指令
- 带有可疑关键词的隐藏 HTML 注释
- 尝试读取机密信息（`.env`、`credentials`、`.netrc`）
- 通过 `curl` 泄露凭证
- 不可见的 Unicode 字符（零宽空格、双向覆盖）

被阻止的文件会显示警告：

```
[已阻止：AGENTS.md 包含潜在的提示注入 (prompt_injection)。内容未加载。]
```

<a id="best-practices-for-production-deployment"></a>
## 生产部署最佳实践

<a id="gateway-deployment-checklist"></a>
### 网关部署清单

1. **设置显式的允许列表** —— 在生产中切勿使用 `GATEWAY_ALLOW_ALL_USERS=true`
2. **使用容器后端** —— 在 config.yaml 中设置 `terminal.backend: docker`
3. **限制资源用量** —— 设置适当的 CPU、内存和磁盘限制
4. **安全存储密钥** —— 将 API 密钥保存在 `~/.hermes/.env` 中，并设置正确的文件权限
5. **启用 DM 配对** —— 尽可能使用配对码而非硬编码用户 ID
6. **审查命令允许列表** —— 定期审计 config.yaml 中的 `command_allowlist`
7. **设置 `MESSAGING_CWD`** —— 不要让 Agent 在敏感目录下运行
8. **以非 root 用户运行** —— 切勿以 root 身份运行网关
9. **监控日志** —— 检查 `~/.hermes/logs/` 中的未授权访问尝试
10. **保持更新** —— 定期运行 `hermes update` 获取安全补丁
<a id="securing-api-keys"></a>
### 保护 API 密钥

```bash
# 对 .env 文件设置合适的权限
chmod 600 ~/.hermes/.env

# 不同服务使用独立的密钥
# 切勿将 .env 文件提交到版本控制
```

<a id="network-isolation"></a>
### 网络隔离

为了最高安全性，请在单独的机器或虚拟机上运行网关。在 `config.yaml` 中设置 `terminal.backend: ssh`，然后通过 `~/.hermes/.env` 中的环境变量提供主机信息：

```yaml
# ~/.hermes/config.yaml
terminal:
  backend: ssh
```

```bash
# ~/.hermes/.env
TERMINAL_SSH_HOST=agent-worker.local
TERMINAL_SSH_USER=hermes
TERMINAL_SSH_KEY=~/.ssh/hermes_agent_key
```

SSH 连接详情存放在 `.env`（而非 `config.yaml`）中，这样就不会随配置文件导出而被检入或共享。这保证了网关的消息连接与 Agent 的命令执行相互隔离。

<a id="supply-chain-advisory-checking"></a>
## 供应链安全建议检查

Hermes 内置了一个安全建议扫描器，用于标记当前 venv 中与已知已被攻破版本（例如 2026 年 5 月 `mistralai 2.4.6` 投毒事件这类供应链蠕虫）匹配的 Python 包。实现位于 `hermes_cli/security_advisories.py`。

运行方式：

- **CLI 启动横幅。** 如果有任何建议匹配，会打印一行警告，并提示运行 `hermes doctor` 查看完整的修复方案。
- **`hermes doctor`。** 显示每条活跃的建议，包含版本详情和 2-4 步的修复说明。
- **网关启动。** 记录到 `gateway.log`；第一条交互消息会显示一个简短的操作员横幅。

每条建议都有一个稳定的 ID。阅读并处理完成后，可以永久忽略它：

```bash
hermes doctor --ack <advisory-id>
```

确认信息会持久化到 `config.security.acked_advisories`，重启后依然有效。旧的建议故意**不会**从目录中移除——保留它们可以让新安装的用户仍然能收到历史上曾被投毒版本的警告，因为这些版本可能缓存在私有镜像中。

该检查仅依赖标准库，每条建议只执行一次 `importlib.metadata.version()` 查找，因此可以在每次启动时安全运行。

<a id="lazy-install-of-optional-dependencies"></a>
### 可选依赖的懒安装

许多功能（Mistral TTS、ElevenLabs、Honcho 记忆、Bedrock、Slack、Matrix 等）依赖 Python 包，但并非所有用户都需要。Hermes 在首次使用时**懒安装**这些包，而不是在 `hermes-agent[all]` 中立即安装。实现位于 `tools/lazy_deps.py`。

此设计解决以下权衡：

- **脆弱性。** 当某个额外功能的传递依赖在 PyPI 上不可用（因恶意软件被隔离、撤回、上传损坏）时，整个 `[all]` 解析会失败，新安装将静默地回退到精简层级——同时丢失 10 多个无关的额外功能。懒安装将每个后端隔离开来，因此一个被污染的依赖不会破坏其他不相关的功能。
- **臃肿。** 只与一个提供商交互的用户不再需要拉取数百个永远不会导入的包。

工作方式：

1. 后端模块在首次导入路径的顶部调用 `ensure("feature.name")`。
2. 如果依赖缺失，`ensure` 会检查 `config.yaml` 中的 `security.allow_lazy_installs`（默认 `true`），并针对允许列表中的规格运行 venv 范围内的 `pip install`。
3. 如果安装失败或用户已禁用懒安装，该调用会抛出 `FeatureUnavailable`，附带实际的 pip stderr 以及指向 `hermes tools` 的提示。
`tools/lazy_deps.py` 强制执行的安全保障：

| 保障措施 | 含义 |
|---|---|
| 仅限虚拟环境作用域 | 仅在当前激活的 venv 中安装目标 `sys.executable` —— 绝不会影响系统 Python |
| 仅按名称从 PyPI 安装 | 规范接受 `"package>=1.0,<2"` 语法。不支持 `--index-url`、`git+https://` 或 `file:` 路径 —— 恶意的 `config.yaml` 无法重定向安装 |
| 白名单机制 | 只有出现在项目内 `LAZY_DEPS` 映射表中的规范才能通过此路径安装。功能名称拼写错误不会获得“安装任意内容”的语义 |
| 可选择退出 | 设置 `security.allow_lazy_installs: false` 可完全禁用运行时安装。适用于受限网络或严格安全策略 |
| 无静默重试 | 失败时会显示 `FeatureUnavailable` —— 不会缓存错误状态，也不会引发重试风暴 |

要禁用运行时安装：

```yaml
# ~/.hermes/config.yaml
security:
  allow_lazy_installs: false
```

禁用后，需要可选依赖的后端会提示用户手动运行安装（`pip install …`），或通过 `hermes tools` 选择其他后端。
