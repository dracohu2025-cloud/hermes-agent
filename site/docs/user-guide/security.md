---
sidebar_position: 8
title: "安全"
description: "安全模型、危险命令审批、用户授权、容器隔离及生产部署最佳实践"
---

# 安全

Hermes Agent 采用了纵深防御的安全模型。本页涵盖了所有安全边界——从命令审批到容器隔离，再到消息平台上的用户授权。

## 概述

安全模型包含五个层面：

1. **用户授权** — 谁可以与 Agent 交互（白名单、私信配对）
2. **危险命令审批** — 破坏性操作需人工介入确认
3. **容器隔离** — 使用 Docker/Singularity/Modal 沙箱及强化配置
4. **MCP 凭证过滤** — MCP 子进程的环境变量隔离
5. **上下文文件扫描** — 项目文件中的提示注入检测

## 危险命令审批

在执行任何命令前，Hermes 会将其与精心维护的危险模式列表进行匹配。如果匹配成功，用户必须明确批准该命令。

### 审批模式

审批系统支持三种模式，通过 `~/.hermes/config.yaml` 中的 `approvals.mode` 配置：

```yaml
approvals:
  mode: manual    # manual | smart | off
  timeout: 60     # 等待用户响应的秒数（默认：60）
```

| 模式 | 行为 |
|------|----------|
| **manual**（默认） | 对危险命令始终提示用户审批 |
| **smart** | 使用辅助 LLM 评估风险。低风险命令（如 `python -c "print('hello')"`）自动批准。真正危险的命令自动拒绝。不确定的情况则转为手动审批。 |
| **off** | 关闭所有审批检查——等同于使用 `--yolo` 运行。所有命令无提示直接执行。 |

:::warning
设置 `approvals.mode: off` 会关闭所有安全提示。仅在可信环境（CI/CD、容器等）中使用。
:::

### YOLO 模式

YOLO 模式会绕过当前会话中**所有**危险命令审批提示。可通过三种方式启用：

1. **CLI 参数**：使用 `hermes --yolo` 或 `hermes chat --yolo` 启动会话
2. **斜杠命令**：会话中输入 `/yolo` 切换开关
3. **环境变量**：设置 `HERMES_YOLO_MODE=1`

`/yolo` 命令是一个**切换开关**——每次使用都会切换模式开关：

```
> /yolo
  ⚡ YOLO 模式开启 — 所有命令自动批准。请谨慎使用。

> /yolo
  ⚠ YOLO 模式关闭 — 危险命令将需要审批。
```

YOLO 模式在 CLI 和网关会话中均可用。内部通过设置 `HERMES_YOLO_MODE` 环境变量，在每次命令执行前检查。

:::danger
YOLO 模式会关闭当前会话中**所有**危险命令安全检查。仅在完全信任生成命令的情况下使用（例如在可丢弃环境中运行经过充分测试的自动化脚本）。
:::

### 审批超时

当出现危险命令审批提示时，用户有一个可配置的时间窗口进行响应。如果超时未响应，命令默认**拒绝**（失败即关闭）。

在 `~/.hermes/config.yaml` 中配置超时时间：

```yaml
approvals:
  timeout: 60  # 秒（默认：60）
```

### 触发审批的命令模式

以下模式会触发审批提示（定义于 `tools/approval.py`）：

| 模式 | 描述 |
|---------|-------------|
| `rm -r` / `rm --recursive` | 递归删除 |
| `rm ... /` | 根路径删除 |
| `chmod 777/666` / `o+w` / `a+w` | 允许所有用户写权限 |
| `chmod --recursive` 带不安全权限 | 递归设置所有用户写权限（长参数） |
| `chown -R root` / `chown --recursive root` | 递归更改所有权为 root |
| `mkfs` | 格式化文件系统 |
| `dd if=` | 磁盘复制 |
| `> /dev/sd` | 写入块设备 |
| `DROP TABLE/DATABASE` | SQL 删除表/数据库 |
| `DELETE FROM`（无 WHERE） | SQL 无条件删除 |
| `TRUNCATE TABLE` | SQL 截断表 |
| `> /etc/` | 覆盖系统配置 |
| `systemctl stop/disable/mask` | 停止/禁用系统服务 |
| `kill -9 -1` | 杀死所有进程 |
| `pkill -9` | 强制杀死进程 |
| Fork bomb 模式 | 叉炸弹 |
| `bash -c` / `sh -c` / `zsh -c` / `ksh -c` | 通过 `-c` 参数执行 shell 命令（包括组合参数如 `-lc`） |
| `python -e` / `perl -e` / `ruby -e` / `node -c` | 通过 `-e`/`-c` 参数执行脚本 |
| `curl ... \| sh` / `wget ... \| sh` | 远程内容管道传给 shell |
| `bash <(curl ...)` / `sh <(wget ...)` | 通过进程替换执行远程脚本 |
| `tee` 写入 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过 tee 覆盖敏感文件 |
| `>` / `>>` 写入 `/etc/`、`~/.ssh/`、`~/.hermes/.env` | 通过重定向覆盖敏感文件 |
| `xargs rm` | xargs 配合 rm |
| `find -exec rm` / `find -delete` | find 执行破坏性操作 |
| `cp`/`mv`/`install` 到 `/etc/` | 复制/移动文件到系统配置 |
| `sed -i` / `sed --in-place` 修改 `/etc/` | 系统配置文件就地编辑 |
| `pkill`/`killall` hermes/gateway | 防止自杀式终止 |
| `gateway run` 带 `&`/`disown`/`nohup`/`setsid` | 防止在服务管理器外启动 gateway |

:::info
**容器绕过**：在 `docker`、`singularity`、`modal` 或 `daytona` 后端运行时，危险命令检查会**跳过**，因为容器本身就是安全边界。容器内的破坏性命令无法影响宿主机。
:::

### 审批流程（CLI）

在交互式 CLI 中，危险命令会显示内联审批提示：

```
  ⚠️  危险命令：递归删除
      rm -rf /tmp/old-project

      [o]nce  |  [s]ession  |  [a]lways  |  [d]eny

      选择 [o/s/a/D]:
```

四个选项：

- **once** — 允许本次执行
- **session** — 本会话内允许该模式
- **always** — 永久加入白名单（保存到 `config.yaml`）
- **deny**（默认） — 阻止命令

### 审批流程（网关/消息平台）

在消息平台上，Agent 会发送危险命令详情到聊天窗口，等待用户回复：

- 回复 **yes**、**y**、**approve**、**ok** 或 **go** 表示批准
- 回复 **no**、**n**、**deny** 或 **cancel** 表示拒绝

运行网关时会自动设置环境变量 `HERMES_EXEC_ASK=1`。

### 永久白名单

选择“always”批准的命令会保存到 `~/.hermes/config.yaml`：

```yaml
# 永久允许的危险命令模式
command_allowlist:
  - rm
  - systemctl
```

这些模式在启动时加载，未来所有会话中自动批准。

:::tip
使用 `hermes config edit` 查看或移除永久白名单中的模式。
:::

## 用户授权（网关）

运行消息网关时，Hermes 通过分层授权系统控制谁能与机器人交互。

### 授权检查顺序

`_is_user_authorized()` 方法按以下顺序检查：

1. **平台级允许所有标志**（如 `DISCORD_ALLOW_ALL_USERS=true`）
2. **私信配对批准列表**（通过配对码批准的用户）
3. **平台特定白名单**（如 `TELEGRAM_ALLOWED_USERS=12345,67890`）
4. **全局白名单**（`GATEWAY_ALLOWED_USERS=12345,67890`）
5. **全局允许所有**（`GATEWAY_ALLOW_ALL_USERS=true`）
6. **默认：拒绝**

### 平台白名单

在 `~/.hermes/.env` 中以逗号分隔设置允许的用户 ID：

```bash
# 平台特定白名单
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=111222333444555666
WHATSAPP_ALLOWED_USERS=15551234567
SLACK_ALLOWED_USERS=U01ABC123

# 跨平台白名单（所有平台均检查）
GATEWAY_ALLOWED_USERS=123456789

# 平台级允许所有（谨慎使用）
DISCORD_ALLOW_ALL_USERS=true

# 全局允许所有（极度谨慎使用）
GATEWAY_ALLOW_ALL_USERS=true
```

:::warning
如果**未配置任何白名单**且未设置 `GATEWAY_ALLOW_ALL_USERS`，**所有用户都会被拒绝**。网关启动时会记录警告：

```
未配置用户白名单。所有未授权用户将被拒绝。
请在 ~/.hermes/.env 中设置 GATEWAY_ALLOW_ALL_USERS=true 以开放访问，
或配置平台白名单（如 TELEGRAM_ALLOWED_USERS=你的ID）。
```
:::

### 私信配对系统 {#dm-pairing-system}

为了更灵活的授权，Hermes 提供基于代码的配对系统。未知用户无需预先提供用户 ID，而是会收到一次性配对码，机器人所有者通过 CLI 批准后生效。
**工作原理：**

1. 一个未知用户向机器人发送私信（DM）
2. 机器人回复一个8字符的配对码
3. 机器人所有者在命令行运行 `hermes pairing approve <platform> <code>`
4. 该用户永久获得该平台的访问权限

在 `~/.hermes/config.yaml` 中控制未授权私信的处理方式：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。未授权的私信会收到配对码回复。
- `ignore` 会静默丢弃未授权的私信。
- 各平台配置会覆盖全局默认值，因此你可以让 Telegram 保持配对，而 WhatsApp 则静默处理。

**安全特性**（基于 OWASP + NIST SP 800-63-4 指南）：

| 特性 | 详情 |
|---------|---------|
| 代码格式 | 8字符，来自32字符无歧义字母表（无0/O/1/I） |
| 随机性 | 加密级别（`secrets.choice()`） |
| 代码有效期 | 1小时过期 |
| 速率限制 | 每用户每10分钟1次请求 |
| 待处理限制 | 每个平台最多3个待处理代码 |
| 锁定机制 | 5次失败审批尝试 → 1小时锁定 |
| 文件安全 | 所有配对数据文件权限为 `chmod 0600` |
| 日志记录 | 代码绝不记录到标准输出 |

**配对 CLI 命令：**

```bash
# 列出待处理和已批准用户
hermes pairing list

# 批准一个配对码
hermes pairing approve telegram ABC12DEF

# 撤销用户访问权限
hermes pairing revoke telegram 123456789

# 清除所有待处理代码
hermes pairing clear-pending
```

**存储：** 配对数据存储在 `~/.hermes/pairing/`，每个平台对应一个 JSON 文件：
- `{platform}-pending.json` — 待处理配对请求
- `{platform}-approved.json` — 已批准用户
- `_rate_limits.json` — 速率限制和锁定跟踪

## 容器隔离

使用 `docker` 终端后端时，Hermes 会对每个容器应用严格的安全加固。

### Docker 安全标志

每个容器都带有以下标志（定义在 `tools/environments/docker.py`）：

```python
_SECURITY_ARGS = [
    "--cap-drop", "ALL",                          # 丢弃所有 Linux 能力
    "--security-opt", "no-new-privileges",         # 阻止权限提升
    "--pids-limit", "256",                         # 限制进程数量
    "--tmpfs", "/tmp:rw,nosuid,size=512m",         # 限制大小的 /tmp
    "--tmpfs", "/var/tmp:rw,noexec,nosuid,size=256m",  # 禁止执行的 /var/tmp
    "--tmpfs", "/run:rw,noexec,nosuid,size=64m",   # 禁止执行的 /run
]
```

### 资源限制

容器资源可在 `~/.hermes/config.yaml` 中配置：

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_forward_env: []  # 仅显式允许列表；空列表防止秘密泄露到容器
  container_cpu: 1        # CPU 核数
  container_memory: 5120  # MB（默认5GB）
  container_disk: 51200   # MB（默认50GB，需XFS上的overlay2）
  container_persistent: true  # 会话间持久化文件系统
```

### 文件系统持久化

- **持久模式**（`container_persistent: true`）：将 `/workspace` 和 `/root` 绑定挂载自 `~/.hermes/sandboxes/docker/<task_id>/`
- **临时模式**（`container_persistent: false`）：使用 tmpfs 作为工作区，清理时所有数据丢失

:::tip
生产环境的网关部署建议使用 `docker`、`modal` 或 `daytona` 后端，将 Agent 命令与主机系统隔离，完全避免危险命令审批的需求。
:::

:::warning
如果你在 `terminal.docker_forward_env` 中添加了变量名，这些变量会被有意注入容器用于终端命令。这对任务专用凭证（如 `GITHUB_TOKEN`）很有用，但也意味着容器内运行的代码可以读取并外泄这些变量。
:::

## 终端后端安全对比

| 后端 | 隔离方式 | 危险命令检查 | 适用场景 |
|---------|-----------|-------------------|----------|
| **local** | 无 — 直接运行在主机 | ✅ 有 | 开发，可信用户 |
| **ssh** | 远程机器 | ✅ 有 | 运行在独立服务器 |
| **docker** | 容器 | ❌ 跳过（容器即边界） | 生产网关 |
| **singularity** | 容器 | ❌ 跳过 | HPC 环境 |
| **modal** | 云沙箱 | ❌ 跳过 | 可扩展云隔离 |
| **daytona** | 云沙箱 | ❌ 跳过 | 持久云工作区 |

## 环境变量透传 {#environment-variable-passthrough}

`execute_code` 和 `terminal` 会剥离子进程中的敏感环境变量，防止 LLM 生成的代码窃取凭证。但声明了 `required_environment_variables` 的技能需要合法访问这些变量。

### 工作机制

有两种机制允许特定变量通过沙箱过滤：

**1. 技能范围透传（自动）**

当技能被加载（通过 `skill_view` 或 `/skill` 命令）且声明了 `required_environment_variables`，环境中实际设置的这些变量会自动注册为透传。未设置的变量（仍处于需配置状态）不会注册。

```yaml
# 在技能的 SKILL.md frontmatter 中
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: 从 https://developers.google.com/tenor 获取密钥
```

加载该技能后，`TENOR_API_KEY` 会透传给 `execute_code`、`terminal`（本地）以及远程后端（Docker、Modal）——无需手动配置。

:::info Docker & Modal
v0.5.1 之前，Docker 的 `forward_env` 与技能透传是两个独立系统。现在已合并——技能声明的环境变量会自动转发到 Docker 容器和 Modal 沙箱，无需手动添加到 `docker_forward_env`。
:::

**2. 配置透传（手动）**

对于未被任何技能声明的环境变量，可在 `config.yaml` 的 `terminal.env_passthrough` 中添加：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

### 凭证文件透传（OAuth 令牌等） {#credential-file-passthrough}

某些技能需要在沙箱中使用**文件**（不仅是环境变量），例如 Google Workspace 将 OAuth 令牌存储为 `google_token.json` 在 `~/.hermes/`。技能在 frontmatter 中声明：

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 令牌（由安装脚本创建）
  - path: google_client_secret.json
    description: Google OAuth2 客户端凭证
```

加载时，Hermes 会检查这些文件是否存在于 `~/.hermes/` 并注册挂载：

- **Docker**：只读绑定挂载（`-v host:container:ro`）
- **Modal**：沙箱创建时挂载，且每次命令前同步（支持会话中 OAuth 设置）
- **本地**：无需操作（文件已可访问）

你也可以在 `config.yaml` 中手动列出凭证文件：

```yaml
terminal:
  credential_files:
    - google_token.json
    - my_custom_oauth_token.json
```

路径相对于 `~/.hermes/`，文件挂载到容器内的 `/root/.hermes/`。

### 各沙箱过滤规则

| 沙箱 | 默认过滤 | 透传覆盖 |
|---------|---------------|---------------------|
| **execute_code** | 阻止名称中含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD`、`AUTH` 的变量；只允许安全前缀变量 | ✅ 透传变量绕过所有检查 |
| **terminal**（本地） | 阻止明确的 Hermes 基础设施变量（提供者密钥、网关令牌、工具 API 密钥） | ✅ 透传变量绕过黑名单 |
| **terminal**（Docker） | 默认不传递主机环境变量 | ✅ 透传变量 + `docker_forward_env` 通过 `-e` 转发 |
| **terminal**（Modal） | 默认不传递主机环境变量/文件 | ✅ 挂载凭证文件；环境变量透传通过同步实现 |
| **MCP** | 阻止所有变量，除安全系统变量和显式配置的 `env` | ❌ 不受透传影响（请使用 MCP 的 `env` 配置） |

### 安全注意事项

- 透传只影响你或技能明确声明的变量，默认安全策略对任意 LLM 生成代码不变
- 凭证文件以**只读**方式挂载到 Docker 容器
- Skills Guard 会在安装前扫描技能内容，检测可疑环境访问模式
- 未设置或缺失的变量不会注册（不存在的变量无法泄露）
- Hermes 基础设施密钥（提供者 API 密钥、网关令牌）绝不应加入 `env_passthrough`，它们有专门的管理机制
## MCP 凭证处理

MCP（Model Context Protocol）服务器子进程会接收一个**过滤后的环境变量**，以防止凭证意外泄露。

### 安全的环境变量

只有以下变量会从主机传递给 MCP 标准输入输出子进程：

```
PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR
```

以及任何 `XDG_*` 变量。所有其他环境变量（API 密钥、令牌、秘密）都会被**剥离**。

MCP 服务器 `env` 配置中显式定义的变量会被传递：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."  # 只有这个会被传递
```

### 凭证脱敏

MCP 工具返回给 LLM 的错误信息会经过清理。以下模式会被替换为 `[REDACTED]`：

- GitHub PAT（`ghp_...`）
- OpenAI 风格的密钥（`sk-...`）
- Bearer 令牌
- `token=`, `key=`, `API_KEY=`, `password=`, `secret=` 参数

### 网站访问策略

你可以限制 Agent 通过其网页和浏览器工具访问的网站。这对于防止 Agent 访问内部服务、管理面板或其他敏感 URL 非常有用。

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

当请求被阻止的 URL 时，工具会返回一个错误，说明该域名被策略阻止。该阻止列表会在 `web_search`、`web_extract`、`browser_navigate` 以及所有支持 URL 的工具中生效。

完整细节请参见配置指南中的[网站阻止列表](/user-guide/configuration#website-blocklist)。

### SSRF 保护

所有支持 URL 的工具（网页搜索、网页提取、视觉、浏览器）在抓取前都会验证 URL，以防止服务器端请求伪造（SSRF）攻击。被阻止的地址包括：

- **私有网络**（RFC 1918）：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- **回环地址**：`127.0.0.0/8`、`::1`
- **链路本地地址**：`169.254.0.0/16`（包括云元数据地址 `169.254.169.254`）
- **CGNAT / 共享地址空间**（RFC 6598）：`100.64.0.0/10`（Tailscale、WireGuard VPN）
- **云元数据主机名**：`metadata.google.internal`、`metadata.goog`
- **保留、多播和未指定地址**

SSRF 保护始终开启且无法关闭。DNS 解析失败视为阻止（失败即关闭）。重定向链在每个跳转点都会重新验证，以防止通过重定向绕过。

### Tirith 执行前安全扫描

Hermes 集成了 [tirith](https://github.com/sheeki03/tirith) 进行内容级命令扫描，防止执行前的安全风险。Tirith 能检测出仅靠模式匹配难以发现的威胁：

- 同形异义 URL 欺骗（国际化域名攻击）
- 管道到解释器的模式（`curl | bash`、`wget | sh`）
- 终端注入攻击

Tirith 会在首次使用时自动从 GitHub 发布版安装，并进行 SHA-256 校验（如果可用，还会进行 cosign 来源验证）。

```yaml
# 在 ~/.hermes/config.yaml 中
security:
  tirith_enabled: true       # 启用/禁用 tirith 扫描（默认：true）
  tirith_path: "tirith"      # tirith 二进制路径（默认：PATH 查找）
  tirith_timeout: 5          # 子进程超时时间（秒）
  tirith_fail_open: true     # tirith 不可用时是否允许执行（默认：true）
```

当 `tirith_fail_open` 为 `true`（默认）时，如果 tirith 未安装或超时，命令仍会继续执行。在高安全环境下可设置为 `false`，以在 tirith 不可用时阻止命令执行。

Tirith 的判定结果会与审批流程集成：安全命令直接通过，疑似和阻止命令会触发用户审批，显示完整的 tirith 发现（严重性、标题、描述、更安全的替代方案）。用户可以批准或拒绝——默认拒绝以保证无人值守场景的安全。

### 上下文文件注入防护

上下文文件（AGENTS.md、.cursorrules、SOUL.md）在被包含进系统提示前会进行提示注入扫描。扫描内容包括：

- 忽略/无视之前指令的指令
- 含有可疑关键词的隐藏 HTML 注释
- 试图读取秘密文件（`.env`、`credentials`、`.netrc`）
- 通过 `curl` 进行凭证外泄
- 隐形 Unicode 字符（零宽空格、双向覆盖符）

被阻止的文件会显示警告：

```
[BLOCKED: AGENTS.md contained potential prompt injection (prompt_injection). Content not loaded.]
```

## 生产环境部署最佳实践

### 网关部署清单

1. **设置明确的允许列表** — 生产环境绝不要使用 `GATEWAY_ALLOW_ALL_USERS=true`
2. **使用容器后端** — 在 config.yaml 中设置 `terminal.backend: docker`
3. **限制资源使用** — 设置合适的 CPU、内存和磁盘限制
4. **安全存储密钥** — 将 API 密钥保存在 `~/.hermes/.env` 并设置合适的文件权限
5. **启用 DM 配对** — 尽量使用配对码代替硬编码用户 ID
6. **审查命令允许列表** — 定期检查 config.yaml 中的 `command_allowlist`
7. **设置 `MESSAGING_CWD`** — 不要让 Agent 在敏感目录下操作
8. **非 root 运行** — 绝不要以 root 身份运行网关
9. **监控日志** — 检查 `~/.hermes/logs/` 以发现未授权访问尝试
10. **保持更新** — 定期运行 `hermes update` 以获取安全补丁

### API 密钥安全

```bash
# 设置 .env 文件的正确权限
chmod 600 ~/.hermes/.env

# 为不同服务使用不同密钥
# 绝不要将 .env 文件提交到版本控制
```

### 网络隔离

为了最大安全性，建议在独立机器或虚拟机上运行网关：

```yaml
terminal:
  backend: ssh
  ssh_host: "agent-worker.local"
  ssh_user: "hermes"
  ssh_key: "~/.ssh/hermes_agent_key"
```

这样可以将网关的消息连接与 Agent 的命令执行隔离开来。
