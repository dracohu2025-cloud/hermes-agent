---
sidebar_position: 2
title: "配置"
description: "配置 Hermes Agent — config.yaml、提供商、模型、API 密钥等"
---

# 配置 {#configuration}

所有设置都存储在 `~/.hermes/` 目录中，方便访问。

## 目录结构 {#directory-structure}

```text
~/.hermes/
├── config.yaml     # 设置（模型、终端、TTS、压缩等）
├── .env            # API 密钥和机密信息
├── auth.json       # OAuth 提供商凭据（Nous Portal 等）
├── SOUL.md         # 主要 Agent 身份（系统提示中的第 1 个插槽）
├── memories/       # 持久记忆（MEMORY.md、USER.md）
├── skills/         # Agent 创建的技能（通过 skill_manage 工具管理）
├── cron/           # 定时任务
├── sessions/       # 网关会话
└── logs/           # 日志（errors.log、gateway.log — 机密信息自动隐藏）
```

## 管理配置 {#managing-configuration}

```bash
hermes config              # 查看当前配置
hermes config edit         # 在编辑器中打开 config.yaml
hermes config set KEY VAL  # 设置特定值
hermes config check        # 检查缺失的选项（更新后）
hermes config migrate      # 交互式添加缺失的选项

# 示例：
hermes config set model anthropic/claude-opus-4
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...  # 保存到 .env
```

:::tip
`hermes config set` 命令会自动将值路由到正确的文件 — API 密钥保存到 `.env`，其他所有内容保存到 `config.yaml`。
:::

## 配置优先级 {#configuration-precedence}

设置按以下顺序解析（优先级从高到低）：

1. **CLI 参数** — 例如 `hermes chat --model anthropic/claude-sonnet-4`（每次调用的覆盖）
2. **`~/.hermes/config.yaml`** — 所有非机密设置的主要配置文件
3. **`~/.hermes/.env`** — 环境变量的后备；**必需**用于机密信息（API 密钥、令牌、密码）
4. **内置默认值** — 当没有其他设置时使用的硬编码安全默认值

:::info 经验法则
机密信息（API 密钥、机器人令牌、密码）放在 `.env` 中。其他所有内容（模型、终端后端、压缩设置、内存限制、工具集）放在 `config.yaml` 中。当两者都设置时，对于非机密设置，`config.yaml` 优先。
<a id="rule-of-thumb"></a>
:::

## 环境变量替换 {#environment-variable-substitution}

你可以使用 `${VAR_NAME}` 语法在 `config.yaml` 中引用环境变量：

```yaml
auxiliary:
  vision:
    api_key: ${GOOGLE_API_KEY}
    base_url: ${CUSTOM_VISION_URL}

delegation:
  api_key: ${DELEGATION_KEY}
```

单个值中支持多个引用：`url: "${HOST}:${PORT}"`。如果引用的变量未设置，占位符将原样保留（`${UNDEFINED_VAR}` 保持不变）。仅支持 `${VAR}` 语法 — 裸的 `$VAR` 不会被展开。

关于 AI 提供商设置（OpenRouter、Anthropic、Copilot、自定义端点、自托管 LLM、后备模型等），请参阅 [AI 提供商](/integrations/providers)。

### 提供商超时 {#provider-timeouts}

你可以设置 `providers.&lt;id&gt;.request_timeout_seconds` 作为提供商级别的请求超时，以及 `providers.&lt;id&gt;.models.&lt;model&gt;.timeout_seconds` 作为模型特定的覆盖。这适用于每个传输（OpenAI-wire、原生 Anthropic、Anthropic 兼容）上的主轮次客户端、后备链、凭据轮换后的重建，以及（对于 OpenAI-wire）每个请求的超时 kwarg — 因此配置的值优先于旧的 `HERMES_API_TIMEOUT` 环境变量。
你还可以为非流式过期调用检测器设置 `providers.&lt;id&gt;.stale_timeout_seconds`，以及为特定模型覆盖设置 `providers.&lt;id&gt;.models.&lt;model&gt;.stale_timeout_seconds`。这些设置会覆盖旧的 `HERMES_API_CALL_STALE_TIMEOUT` 环境变量。

如果不设置这些，将保留旧的默认值（`HERMES_API_TIMEOUT=1800`秒，`HERMES_API_CALL_STALE_TIMEOUT=300`秒，原生 Anthropic 900秒）。目前尚未适配 AWS Bedrock（`bedrock_converse` 和 AnthropicBedrock SDK 路径都使用 boto3，其自带超时配置）。请参阅 [`cli-config.yaml.example`](https://github.com/NousResearch/hermes-agent/blob/main/cli-config.yaml.example) 中的注释示例。

## 终端后端配置 {#terminal-backend-configuration}

Hermes 支持七种终端后端。每种后端决定了 Agent 的 shell 命令实际执行的位置——你的本地机器、Docker 容器、通过 SSH 连接的远程服务器、Modal 云沙箱、Daytona 工作区、Vercel Sandbox 或 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | vercel_sandbox | singularity
  cwd: "."          # Working directory ("." = current dir for local, "/root" for containers)
  timeout: 180      # Per-command timeout in seconds
  env_passthrough: []  # Env var names to forward to sandboxed execution (terminal + execute_code)
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Container image for Singularity backend
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Container image for Modal backend
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Container image for Daytona backend
```

对于 Modal、Daytona 和 Vercel Sandbox 等云沙箱，`container_persistent: true` 表示 Hermes 会尝试在沙箱重建时保留文件系统状态。但这并不保证相同的活跃沙箱、PID 空间或后台进程之后仍然在运行。

### 后端概览 {#backend-overview}

| 后端 | 命令运行位置 | 隔离性 | 最佳用途 |
|---------|-------------------|-----------|----------|
| **local** | 直接在你的机器上 | 无 | 开发、个人使用 |
| **docker** | Docker 容器 | 完全（命名空间、cap-drop） | 安全沙箱、CI/CD |
| **ssh** | 通过 SSH 的远程服务器 | 网络边界 | 远程开发、强大硬件 |
| **modal** | Modal 云沙箱 | 完全（云虚拟机） | 临时云计算、评估 |
| **daytona** | Daytona 工作区 | 完全（云容器） | 托管云开发环境 |
| **vercel_sandbox** | Vercel Sandbox | 完全（云微虚拟机） | 基于快照文件系统持久化的云执行 |
| **singularity** | Singularity/Apptainer 容器 | 命名空间（--containall） | HPC 集群、共享机器 |

### 本地后端 {#local-backend}

默认选项。命令直接在你的机器上运行，无隔离。无需特殊设置。

```yaml
terminal:
  backend: local
```

:::warning
Agent 拥有与你用户账户相同的文件系统访问权限。使用 `hermes tools` 禁用你不想要的工具，或切换到 Docker 进行沙箱隔离。
:::
### Docker 后端 {#docker-backend}

在 Docker 容器内运行命令，并进行了安全加固（丢弃所有能力、禁止权限提升、PID 限制）。

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # Mount launch dir into /workspace
  docker_run_as_host_user: false   # See "Running container as host user" below
  docker_forward_env:              # Env vars to forward into container
    - "GITHUB_TOKEN"
  docker_volumes:                  # Host directory mounts
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"   # :ro for read-only

  # Resource limits
  container_cpu: 1                 # CPU cores (0 = unlimited)
  container_memory: 5120           # MB (0 = unlimited)
  container_disk: 51200            # MB (requires overlay2 on XFS+pquota)
  container_persistent: true       # Persist /workspace and /root across sessions
```

**要求：** 需要安装并运行 Docker Desktop 或 Docker Engine。Hermes 会探测 `$PATH` 以及常见的 macOS 安装位置（`/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用包）。Podman 开箱即用：当两者都安装时，设置 `HERMES_DOCKER_BINARY=podman`（或完整路径）可强制使用 Podman。

**容器生命周期：** Hermes 会为每次终端和文件工具调用复用同一个长期运行的容器（`docker run -d ... sleep 2h`），该容器跨会话、`/new`、`/reset` 以及 `delegate_task` 子 Agent 使用，贯穿 Hermes 进程的整个生命周期。命令通过 `docker exec` 配合登录 shell 运行，因此工作目录变更、已安装的包以及 `/workspace` 中的文件都会在工具调用之间持久保留。Hermes 关闭时（或空闲回收机制回收时）会停止并移除该容器。

通过 `delegate_task(tasks=[...])` 生成的并行子 Agent 共享这一个容器——并发的 `cd`、环境变量修改以及对同一路径的写入会发生冲突。如果某个子 Agent 需要隔离沙箱，它必须通过 `register_task_env_overrides()` 注册每个任务专用的镜像覆盖，RL 和基准测试环境（TerminalBench2、HermesSweEnv 等）会自动为其每个任务的 Docker 镜像执行此操作。

**安全加固：**
- `--cap-drop ALL`，仅恢复 `DAC_OVERRIDE`、`CHOWN`、`FOWNER`
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- 为 `/tmp`（512MB）、`/var/tmp`（256MB）、`/run`（64MB）设置大小受限的 tmpfs

**凭据转发：** `docker_forward_env` 中列出的环境变量会首先从你的 shell 环境中解析，然后从 `~/.hermes/.env` 中解析。技能也可以声明 `required_environment_variables`，这些变量会自动合并。

### SSH 后端 {#ssh-backend}

通过 SSH 在远程服务器上运行命令。使用 ControlMaster 实现连接复用（空闲保持 5 分钟）。默认启用持久 shell——状态（cwd、环境变量）在命令之间持续存在。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # Keep a long-lived bash session (default: true)
```
**必需的环境变量：**

```bash
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=ubuntu
```

**可选配置：**

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `TERMINAL_SSH_PORT` | `22` | SSH 端口 |
| `TERMINAL_SSH_KEY` | (系统默认) | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | `true` | 启用持久化 Shell |

**工作原理：** 在初始化时使用 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 进行连接。持久化 Shell 会在远程主机上保持一个 `bash -l` 进程存活，通过临时文件进行通信。需要 `stdin_data` 或 `sudo` 的命令会自动回退到一次性模式。

### Modal 后端 {#modal-backend}

在 [Modal](https://modal.com) 云沙箱中运行命令。每个任务会获得一个独立的虚拟机，可配置 CPU、内存和磁盘。文件系统可以在会话之间进行快照/恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB (5GB)
  container_disk: 51200            # MB (50GB)
  container_persistent: true       # 快照/恢复文件系统
```

**必需：** 要么设置 `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` 环境变量，要么提供 `~/.modal.toml` 配置文件。

**持久化：** 启用后，沙箱文件系统会在清理时进行快照，并在下次会话时恢复。快照记录在 `~/.hermes/modal_snapshots.json` 中。这保存的是文件系统状态，而不是活动进程、PID 空间或后台任务。

**凭证文件：** 自动从 `~/.hermes/` 挂载（OAuth 令牌等），并在每条命令执行前同步。

### Daytona 后端 {#daytona-backend}

在 [Daytona](https://daytona.io) 管理的工作区中运行命令。支持停止/恢复以实现持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB → 转换为 GiB
  container_disk: 10240            # MB → 转换为 GiB（最大 10 GiB）
  container_persistent: true       # 停止/恢复而非删除
```

**必需：** `DAYTONA_API_KEY` 环境变量。

**持久化：** 启用后，沙箱在清理时会被停止（而非删除），并在下次会话时恢复。沙箱名称遵循 `hermes-{task_id}` 的命名模式。

**磁盘限制：** Daytona 强制限制最大 10 GiB。超出此限制的请求会被截断并发出警告。

### Vercel Sandbox 后端 {#vercel-sandbox-backend}

在 [Vercel Sandbox](https://vercel.com/docs/vercel-sandbox) 云微虚拟机中运行命令。Hermes 使用常规的终端和文件工具接口；没有面向模型的 Vercel 专用工具。

```yaml
terminal:
  backend: vercel_sandbox
  vercel_runtime: node24          # node24 | node22 | python3.13
  cwd: /vercel/sandbox            # 默认工作区根目录
  container_persistent: true      # 快照/恢复文件系统
  container_disk: 51200           # 仅共享默认值；不支持自定义磁盘
```

**必需安装：** 安装可选的 SDK 扩展：

```bash
pip install 'hermes-agent[vercel]'
```

**必需认证：** 使用 `VERCEL_TOKEN`、`VERCEL_PROJECT_ID` 和 `VERCEL_TEAM_ID` 这三个配置访问令牌认证。这是针对 Render、Railway、Docker 及类似主机上的部署和常规长时间运行的 Hermes 进程所支持的设置。
对于一次性本地开发，Hermes 也接受短期的 Vercel OIDC 令牌：

```bash
VERCEL_OIDC_TOKEN="$(vc project token <project-name>)" hermes chat
```

在已关联的 Vercel 项目目录中，可以省略项目名称：

```bash
VERCEL_OIDC_TOKEN="$(vc project token)" hermes chat
```

OIDC 令牌是短期的，不应作为文档中描述的部署路径使用。

**运行时：** `terminal.vercel_runtime` 支持 `node24`、`node22` 和 `python3.13`。如果未设置，Hermes 默认使用 `node24`。

**持久化：** 当 `container_persistent: true` 时，Hermes 会在清理期间对沙箱文件系统进行快照，并在后续为同一任务恢复沙箱时使用该快照。快照内容可以包括复制到沙箱中的 Hermes 同步凭据、技能和缓存文件。这只保留文件系统状态；不保留实时沙箱身份、PID 空间、shell 状态或正在运行的后台进程。

**后台命令：** `terminal(background=true)` 使用 Hermes 通用的非本地后台进程流程。在沙箱存活期间，您可以通过常规进程工具生成、轮询、等待、查看日志和终止进程。Hermes 在清理或重启后不提供原生的 Vercel 分离进程恢复功能。

**磁盘大小：** Vercel Sandbox 目前不支持 Hermes 的 `container_disk` 资源旋钮。请保持 `container_disk` 未设置或使用共享默认值 `51200`；非默认值会导致诊断和后台创建失败，而不是被静默忽略。

### Singularity/Apptainer 后端 {#singularity-apptainer-backend}

在 [Singularity/Apptainer](https://apptainer.org) 容器中运行命令。专为没有 Docker 的 HPC 集群和共享机器设计。

```yaml
terminal:
  backend: singularity
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB
  container_persistent: true       # 可写覆盖层在会话间持久化
```

**要求：** `$PATH` 中存在 `apptainer` 或 `singularity` 二进制文件。

**镜像处理：** Docker URL（`docker://...`）会自动转换为 SIF 文件并缓存。现有的 `.sif` 文件会直接使用。

**临时目录：** 按以下顺序解析：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent`（HPC 约定） → `~/.hermes/sandboxes/singularity`。

**隔离性：** 使用 `--containall --no-home` 实现完整的命名空间隔离，不挂载主机 home 目录。

### 常见终端后端问题 {#common-terminal-backend-issues}

如果终端命令立即失败，或者终端工具报告为已禁用：

- **Local** — 无特殊要求。入门时最安全的默认选项。
- **Docker** — 运行 `docker version` 验证 Docker 是否正常工作。如果失败，修复 Docker 或执行 `hermes config set terminal.backend local`。
- **SSH** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER`。如果缺少任一变量，Hermes 会记录清晰的错误。
- **Modal** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml`。运行 `hermes doctor` 检查。
- **Daytona** — 需要 `DAYTONA_API_KEY`。Daytona SDK 处理服务器 URL 配置。
- **Singularity** — 需要在 `$PATH` 中有 `apptainer` 或 `singularity`。常见于 HPC 集群。
如果不确定，请先将 `terminal.backend` 设回 `local`，并确认命令能在本地正常执行。

### 关闭时远程到主机的文件同步 {#remote-to-host-file-sync-on-teardown}

对于 **SSH**、**Modal** 和 **Daytona** 后端（即 Agent 的工作目录所在机器与运行 Hermes 的主机不同的情况），Hermes 会跟踪 Agent 在远程沙箱中操作过的文件，并在会话关闭/沙箱清理时，**将修改过的文件同步回主机**，存放在 `~/.hermes/cache/remote-syncs/&lt;session-id&gt;/` 目录下。

- 触发时机：会话关闭、`/new`、`/reset`、网关消息超时、`delegate_task` 子 Agent 完成（且子 Agent 使用了远程后端）。
- 覆盖 Agent 修改过的整个目录树，而不仅仅是它显式打开的文件。新增、编辑和删除操作都会被捕获。
- 当你去查看时，远程沙箱可能已被销毁；本地的 `~/.hermes/cache/remote-syncs/…` 副本是 Agent 所做更改的权威记录。
- 大型二进制输出（如模型检查点、原始数据集）有大小限制——同步会跳过超过 `file_sync_max_mb`（默认 `100`）的文件。如果你预期会有更大的产物需要回传，可以调高这个值。

```yaml
terminal:
  file_sync_max_mb: 100     # 默认值——同步每个最大 100 MB 的文件
  file_sync_enabled: true   # 默认值——设为 false 可完全跳过同步
```

这样，你就能从会话结束后即被销毁的临时云沙箱中恢复结果，而无需让 Agent 显式地对每个产物执行 `scp` 或 `modal volume put`。

### Docker 卷挂载 {#docker-volume-mounts}

使用 Docker 后端时，`docker_volumes` 允许你将主机目录共享给容器。每个条目使用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # 读写（默认）
    - "/home/user/datasets:/data:ro"              # 只读
    - "/home/user/.hermes/cache/documents:/output" # 网关可见的导出目录
```

这在以下场景中非常有用：
- **向 Agent 提供文件**（数据集、配置、参考代码）
- **从 Agent 接收文件**（生成的代码、报告、导出文件）
- **共享工作区**，你和 Agent 可以访问相同的文件

如果你使用消息网关，并希望 Agent 通过 `MEDIA:/...` 发送生成的文件，建议使用一个专用的、主机可见的导出挂载点，例如 `/home/user/.hermes/cache/documents:/output`。

- 在 Docker 内部将文件写入 `/output/...`
- 在 `MEDIA:` 中发出**主机路径**，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`
- **不要**发出 `/workspace/...` 或 `/output/...`，除非主机上的网关进程也存在完全相同的路径

:::warning
YAML 中重复的键会静默覆盖前面的键。如果你已经有一个 `docker_volumes:` 块，请将新的挂载点合并到同一个列表中，而不是在文件后面再添加一个 `docker_volumes:` 键。
:::

也可以通过环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组）。
### Docker 凭据转发 {#docker-credential-forwarding}

默认情况下，Docker 终端会话不会继承宿主机的任意凭据。如果你需要在容器内使用特定的令牌，请将其添加到 `terminal.docker_forward_env` 中。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 会先从当前 shell 中解析每个列出的变量，如果该变量已通过 `hermes config set` 保存到 `~/.hermes/.env`，则会回退到该文件。

:::warning
`docker_forward_env` 中列出的任何内容都会对容器内运行的命令可见。请仅转发你愿意暴露给终端会话的凭据。
:::

### 以宿主机用户身份运行容器 {#running-the-container-as-your-host-user}

默认情况下，Docker 容器以 `root`（UID 0）身份运行。在 `/workspace` 或其他绑定挂载目录中创建的文件最终会归宿主机上的 root 所有，因此会话结束后，你需要先执行 `sudo chown` 才能从宿主机编辑器编辑这些文件。`terminal.docker_run_as_host_user` 标志可以解决这个问题：

```yaml
terminal:
  backend: docker
  docker_run_as_host_user: true   # 默认值: false
```

启用后，Hermes 会在 `docker run` 命令后追加 `--user $(id -u):$(id -g)`，这样写入绑定挂载目录（`/workspace`、`/root`、`docker_volumes` 中的任何目录）的文件将归宿主机用户所有，而非 root。代价是：容器将无法执行 `apt install` 或写入 root 拥有的路径（如 `/root/.npm`）——如果你两者都需要，请使用 `HOME` 目录归非 root 用户所有的基础镜像（或在构建镜像时添加所需的工具）。

保持 `false`（默认值）可获得向后兼容的行为。如果你的工作流主要是“编辑挂载的宿主机文件”并且厌倦了 `sudo chown -R`，请启用此选项。

### 可选：将启动目录挂载到 `/workspace` {#optional-mount-the-launch-directory-into-workspace}

默认情况下，Docker 沙箱保持隔离。Hermes **不会**将你当前的宿主机工作目录传入容器，除非你明确选择启用。

在 `config.yaml` 中启用：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用后：
- 如果你从 `~/projects/my-app` 启动 Hermes，该宿主机目录会被绑定挂载到 `/workspace`
- Docker 后端会在 `/workspace` 中启动
- 文件工具和终端命令都能看到同一个挂载的项目

禁用时，`/workspace` 保持沙箱所有，除非你通过 `docker_volumes` 显式挂载某些内容。

安全权衡：
- `false` 保留沙箱边界
- `true` 让沙箱直接访问你启动 Hermes 的目录

仅当你确实希望容器处理宿主机上的实时文件时，才选择启用。

### 持久化 Shell {#persistent-shell}

默认情况下，每个终端命令都在自己的子进程中运行——工作目录、环境变量和 shell 变量会在命令之间重置。当启用**持久化 shell** 时，会保持一个长期运行的 bash 进程，跨 `execute()` 调用存活，从而使状态在命令之间得以保留。

这对于 **SSH 后端**最为有用，因为它还消除了每个命令的连接开销。持久化 shell 在 SSH 后端**默认启用**，在本地后端则禁用。
```yaml
terminal:
  persistent_shell: true   # 默认值 — 启用持久化 shell 以便通过 SSH 使用
```

要禁用它：

```bash
hermes config set terminal.persistent_shell false
```

**跨命令保留的内容：**
- 工作目录（`cd /tmp` 在下一个命令中仍然生效）
- 导出的环境变量（`export FOO=bar`）
- Shell 变量（`MY_VAR=hello`）

**优先级：**

| 级别 | 变量 | 默认值 |
|-------|----------|---------|
| 配置 | `terminal.persistent_shell` | `true` |
| SSH 覆盖 | `TERMINAL_SSH_PERSISTENT` | 跟随配置 |
| 本地覆盖 | `TERMINAL_LOCAL_PERSISTENT` | `false` |

每个后端的环境变量具有最高优先级。如果你也想在本地后端上使用持久化 shell：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
需要 `stdin_data` 或 sudo 的命令会自动回退到一次性模式，因为持久化 shell 的 stdin 已被 IPC 协议占用。
:::

有关每个后端的详细信息，请参阅[代码执行](features/code-execution.md)和 [README 的终端部分](features/tools.md)。

## 技能设置 {#skill-settings}

技能可以通过其 SKILL.md 的 frontmatter 声明自己的配置设置。这些是非机密值（路径、偏好、域设置），存储在 `config.yaml` 的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    myplugin:
      path: ~/myplugin-data   # 示例 — 每个技能定义自己的键
```

**技能设置的工作方式：**

- `hermes config migrate` 扫描所有已启用的技能，找到未配置的设置，并提示你进行配置
- `hermes config show` 在“技能设置”下显示所有技能设置及其所属技能
- 当技能加载时，其解析后的配置值会自动注入到技能上下文中

**手动设置值：**

```bash
hermes config set skills.config.myplugin.path ~/myplugin-data
```

有关在你自己技能中声明配置设置的详细信息，请参阅[创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

### 监控 agent 创建的技能写入 {#guard-on-agent-created-skill-writes}

当 agent 使用 `skill_manage` 创建、编辑、补丁或删除技能时，Hermes 可以选择性地扫描新增/更新的内容，查找危险关键词模式（凭据收集、明显的提示注入、数据泄露指令）。扫描器默认**关闭**——因为那些合法处理 `~/.ssh/` 或提及 `$OPENAI_API_KEY` 的真实 agent 工作流过于频繁地触发了启发式规则。如果你希望在 agent 的技能写入生效前由扫描器提示你，请重新启用：

```yaml
skills:
  guard_agent_created: true   # 默认值: false
```

启用后，任何被标记的 `skill_manage` 写入操作都会显示为一个审批提示，并附带扫描器的理由。接受的写入会生效；拒绝的写入会向 agent 返回一个包含说明的错误。

## 内存配置 {#memory-configuration}

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # 约 800 个 token
  user_char_limit: 1375     # 约 500 个 token
```
## File Read Safety {#file-read-safety}

控制单次 `read_file` 调用能返回多少内容。超过限制的读取会被拒绝，并返回错误提示 Agent 使用 `offset` 和 `limit` 来缩小范围。这可以防止一次性读取压缩后的 JS 包或大型数据文件导致上下文窗口被淹没。

```yaml
file_read_max_chars: 100000  # default — ~25-35K tokens
```

如果你的模型拥有较大的上下文窗口且经常读取大文件，可以调高此值。对于小上下文模型，则调低以保持读取效率：

```yaml
# Large context model (200K+)
file_read_max_chars: 200000

# Small local model (16K context)
file_read_max_chars: 30000
```

Agent 还会自动对文件读取进行去重——如果同一文件区域被读取两次且文件未发生变化，则返回一个轻量级存根，而不是重新发送内容。在上下文压缩时会重置此机制，以便 Agent 在内容被摘要化后可以重新读取文件。

## Tool Output Truncation Limits {#tool-output-truncation-limits}

三个相关的上限控制着工具在 Hermes 截断之前可以返回的原始输出量：

```yaml
tool_output:
  max_bytes: 50000        # terminal output cap (chars)
  max_lines: 2000         # read_file pagination cap
  max_line_length: 2000   # per-line cap in read_file's line-numbered view
```

- **`max_bytes`** — 当 `terminal` 命令产生的 stdout/stderr 合并字符数超过此值时，Hermes 会保留前 40% 和后 60%，并在中间插入一条 `[OUTPUT TRUNCATED]` 提示。默认值 `50000`（在典型分词器下约 12-15K tokens）。
- **`max_lines`** — 单次 `read_file` 调用中 `limit` 参数的上限。超过此值的请求会被截断，以防止单次读取淹没上下文窗口。默认值 `2000`。
- **`max_line_length`** — 当 `read_file` 输出带行号的视图时，每行的长度上限。超过此长度的行会被截断为这么多字符，后跟 `... [truncated]`。默认值 `2000`。

对于拥有较大上下文窗口、能够承受每次调用更多原始输出的模型，可以调高这些限制。对于小上下文模型，则调低以保持工具结果紧凑：

```yaml
# Large context model (200K+)
tool_output:
  max_bytes: 150000
  max_lines: 5000

# Small local model (16K context)
tool_output:
  max_bytes: 20000
  max_lines: 500
```

## Global Toolset Disable {#global-toolset-disable}

要一次性在 CLI 和所有网关平台上禁用特定工具集，请在 `agent.disabled_toolsets` 下列出它们的名称：

```yaml
agent:
  disabled_toolsets:
    - memory       # hide memory tools + MEMORY_GUIDANCE injection
    - web          # no web_search / web_extract anywhere
```

此设置**在**每个平台的工具配置（由 `hermes tools` 写入的 `platform_toolsets`）之后生效，因此此处列出的工具集始终会被移除——即使某个平台保存的配置中仍然列出了它。当你想要一个统一的开关来“在所有地方关闭 X”，而不是在 `hermes tools` UI 中编辑 15 个以上的平台行时，可以使用此设置。

将列表留空或省略该键，则不会产生任何效果。
## Git 工作树隔离 {#git-worktree-isolation}

启用隔离的 Git 工作树，以便在同一仓库上并行运行多个 Agent：

```yaml
worktree: true    # 始终创建工作树（等同于 hermes -w）
# worktree: false # 默认行为——仅在传递 -w 标志时创建
```

启用后，每个 CLI 会话会在 `.worktrees/` 下创建一个全新的工作树，并附带独立的分支。Agent 可以编辑文件、提交、推送和创建 PR，而不会相互干扰。干净的工作树会在退出时自动删除；脏工作树则会保留，供手动恢复。

你也可以在仓库根目录下通过 `.worktreeinclude` 文件列出需要复制到工作树中的 gitignore 文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩 {#context-compression}

Hermes 会自动压缩长对话，使其保持在模型的上下文窗口内。压缩摘要器是一个独立的 LLM 调用——你可以将其指向任何提供商或端点。

所有压缩设置都位于 `config.yaml` 中（无环境变量）。

### 完整参考 {#full-reference}

```yaml
compression:
  enabled: true                                     # 开启/关闭压缩
  threshold: 0.50                                   # 达到上下文限制的此百分比时触发压缩
  target_ratio: 0.20                                # 保留为最近尾部的阈值比例
  protect_last_n: 20                                # 保留不压缩的最近消息最小数量
  hygiene_hard_message_limit: 400                   # 网关安全阀——见下文

# 摘要模型/提供商在 auxiliary 下配置：
auxiliary:
  compression:
    model: "google/gemini-3-flash-preview"          # 用于摘要的模型
    provider: "auto"                                # 提供商："auto"、"openrouter"、"nous"、"codex"、"main" 等
    base_url: null                                  # 自定义 OpenAI 兼容端点（覆盖提供商）
```

<a id="legacy-config-migration"></a>
:::info 旧配置迁移
旧配置中的 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 会在首次加载时自动迁移到 `auxiliary.compression.*`（配置版本 17）。无需手动操作。
:::

`hygiene_hard_message_limit` 是仅用于网关的**压缩前安全阀**。当会话失控，消息数量达到数千条时，可能会在常规的百分比阈值触发之前就达到模型上下文限制；当消息数量超过此上限时，Hermes 会强制压缩，无论 token 使用量如何。默认值为 `400`——如果平台通常允许非常长的会话，可以调高此值；如果需要更激进的压缩，可以调低。在运行中的网关上编辑此值，会在下一条消息时生效（见下文）。

<a id="gateway-hot-reload-of-compression-and-context-length"></a>
:::tip 网关热重载压缩与上下文长度
从近期版本开始，在运行中的网关上编辑 `config.yaml` 中的 `model.context_length` 或任何 `compression.*` 键，会在下一条消息时生效——无需重启网关、无需 `/reset`、无需轮换会话。缓存的 Agent 签名包含这些键，因此网关在检测到变化时会透明地重建 Agent。API 密钥和工具/技能配置仍需要常规的重载路径。
:::
### 常见配置 {#common-setups}

**默认（自动检测）——无需配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
使用你的主提供商和主模型。如果你想在比主聊天模型更便宜的模型上进行压缩，可以按任务覆盖（例如 `auxiliary.compression.provider: openrouter` + `model: google/gemini-2.5-flash`）。

**强制指定特定提供商**（基于 OAuth 或 API 密钥）：
```yaml
auxiliary:
  compression:
    provider: nous
    model: gemini-3-flash
```
适用于任何提供商：`nous`、`openrouter`、`codex`、`anthropic`、`main` 等。

**自定义端点**（自托管、Ollama、zai、DeepSeek 等）：
```yaml
auxiliary:
  compression:
    model: glm-4.7
    base_url: https://api.z.ai/api/coding/paas/v4
```
指向一个自定义的 OpenAI 兼容端点。使用 `OPENAI_API_KEY` 进行身份验证。

### 三个旋钮如何交互 {#how-the-three-knobs-interact}

| `auxiliary.compression.provider` | `auxiliary.compression.base_url` | 结果 |
|---------------------|---------------------|--------|
| `auto`（默认） | 未设置 | 自动检测最佳可用提供商 |
| `nous` / `openrouter` / 等 | 未设置 | 强制使用该提供商及其身份验证 |
| 任意 | 已设置 | 直接使用自定义端点（忽略提供商） |

:::warning 摘要模型上下文长度要求
摘要模型**必须**拥有至少与主 Agent 模型一样大的上下文窗口。压缩器会将对话的中间部分完整发送给摘要模型——如果该模型的上下文窗口小于主模型，则摘要调用将因上下文长度错误而失败。发生这种情况时，中间轮次会被**直接丢弃而不生成摘要**，从而静默丢失对话上下文。如果你覆盖了模型，请验证其上下文长度是否达到或超过主模型。
<a id="summary-model-context-length-requirement"></a>
:::

## 上下文引擎 {#context-engine}

上下文引擎控制当接近模型的 token 限制时如何管理对话。内置的 `compressor` 引擎使用有损摘要（参见[上下文压缩](/developer-guide/context-compression-and-caching)）。插件引擎可以用其他策略替换它。

```yaml
context:
  engine: "compressor"    # 默认——内置有损摘要
```

要使用插件引擎（例如，用于无损上下文管理的 LCM）：

```yaml
context:
  engine: "lcm"          # 必须与插件名称匹配
```

插件引擎**永远不会自动激活**——你必须显式地将 `context.engine` 设置为插件名称。可以通过 `hermes plugins` → Provider Plugins → Context Engine 浏览和选择可用的引擎。

有关内存插件的类似单选系统，请参见[内存提供商](/user-guide/features/memory-providers)。

## 迭代预算压力 {#iteration-budget-pressure}

当 Agent 正在处理一个包含许多工具调用的复杂任务时，它可能会在不知不觉中消耗完其迭代预算（默认：90 轮）。预算压力会在模型接近限制时自动发出警告：

| 阈值 | 级别 | 模型看到的内容 |
|-----------|-------|---------------------|
| **70%** | 注意 | `[BUDGET: 63/90. 27 iterations left. Start consolidating.]` |
| **90%** | 警告 | `[BUDGET WARNING: 81/90. Only 9 left. Respond NOW.]` |
警告信息会被注入到最后一条工具结果的 JSON 中（作为 `_budget_warning` 字段），而不是作为独立消息发送——这样既能保留提示缓存，又不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # 每轮对话的最大迭代次数（默认：90）
  api_max_retries: 2           # 在触发回退前，每个提供者的重试次数（默认：2）
```

预算压力默认开启。Agent 会自然地在工具结果中看到警告，从而促使其整合工作，在迭代次数耗尽前给出响应。

当迭代预算完全耗尽时，CLI 会向用户显示一条通知：`⚠ 迭代预算已用尽 (90/90) —— 响应可能不完整`。如果预算在活跃工作期间耗尽，Agent 会在停止前生成一份已完成工作的摘要。

`agent.api_max_retries` 控制 Hermes 在遇到临时错误（速率限制、连接断开、5xx）时，**在**触发回退提供者切换之前，对提供者 API 调用重试的次数。默认值为 `2` —— 总共尝试三次，与 OpenAI SDK 默认值一致。如果你配置了[回退提供者](/user-guide/features/fallback-providers)并希望更快地切换，请将此值设为 `0`，这样主提供者上的第一个临时错误就会立即交给回退提供者，而不是在故障端点上反复重试。

### API 超时 {#api-timeouts}

Hermes 对流式调用有独立的超时层，并为非流式调用设置了陈旧检测器。只有当你在隐式默认值上不做修改时，陈旧检测器才会自动针对本地提供者进行调整。

| 超时类型 | 默认值 | 本地提供者 | 配置 / 环境变量 |
|---------|---------|----------------|--------------|
| Socket 读取超时 | 120s | 自动提升至 1800s | `HERMES_STREAM_READ_TIMEOUT` |
| 流式陈旧检测 | 180s | 自动禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| 非流式陈旧检测 | 300s | 隐式默认时自动禁用 | `providers.&lt;id&gt;.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT` |
| API 调用（非流式） | 1800s | 不变 | `providers.&lt;id&gt;.request_timeout_seconds` / `timeout_seconds` 或 `HERMES_API_TIMEOUT` |

**Socket 读取超时**控制 httpx 等待提供者返回下一个数据块的时间。本地 LLM 在处理大上下文时，预填充可能需要数分钟才能产生第一个 token，因此 Hermes 在检测到本地端点时会将其提升至 30 分钟。如果你显式设置了 `HERMES_STREAM_READ_TIMEOUT`，则无论端点检测结果如何，都会使用该值。

**流式陈旧检测**会终止那些收到 SSE 保活 ping 但没有实际内容的连接。对于本地提供者，此功能完全禁用，因为它们在预填充期间不会发送保活 ping。

**非流式陈旧检测**会终止长时间没有响应的非流式调用。默认情况下，Hermes 在本地端点上禁用此功能，以避免在长时间预填充期间出现误报。如果你显式设置了 `providers.&lt;id&gt;.stale_timeout_seconds`、`providers.&lt;id&gt;.models.&lt;model&gt;.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT`，则即使在本地端点上也会使用该显式值。
## 上下文压力警告 {#context-pressure-warnings}

与迭代预算压力不同，上下文压力追踪对话距离**压缩阈值**的接近程度——即上下文压缩触发以总结较早消息的临界点。这有助于你和 Agent 了解对话何时变得过长。

| 进度 | 级别 | 发生什么 |
|----------|-------|-------------|
| **≥ 60%** 阈值 | 信息 | CLI 显示青色进度条；网关发送信息性通知 |
| **≥ 85%** 阈值 | 警告 | CLI 显示粗体黄色条；网关警告压缩即将发生 |

在 CLI 中，上下文压力以工具输出流中的进度条形式显示：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台上，会发送纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果自动压缩被禁用，警告会告诉你上下文可能会被截断。

上下文压力是自动的——无需配置。它纯粹作为面向用户的通知触发，不会修改消息流或向模型上下文注入任何内容。

## 凭证池策略 {#credential-pool-strategies}

当你有多个同一提供商的 API 密钥或 OAuth 令牌时，配置轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # 均匀循环使用密钥
  anthropic: least_used      # 始终选择使用最少的密钥
```

选项：`fill_first`（默认）、`round_robin`、`least_used`、`random`。完整文档请参阅[凭证池](/user-guide/features/credential-pools)。

## 辅助模型 {#auxiliary-models}

Hermes 使用“辅助”模型处理图像分析、网页摘要、浏览器截图分析、会话标题生成和上下文压缩等辅助任务。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 会将所有辅助任务路由到你的**主聊天模型**——即你在 `hermes model` 中选择的同一提供商/模型。你无需任何配置即可开始使用，但请注意，在昂贵的推理模型（Opus、MiniMax M2.7 等）上，辅助任务会增加显著的成本。如果你希望无论主模型如何，辅助任务都快速且廉价，请显式设置 `auxiliary.&lt;task&gt;.provider` 和 `auxiliary.&lt;task&gt;.model`（例如，在 OpenRouter 上使用 Gemini Flash 进行视觉和网页提取）。

:::note 为什么“auto”使用你的主模型
<a id="why-auto-uses-your-main-model"></a>
早期版本将聚合器用户（OpenRouter、Nous Portal）分流到便宜的提供商侧默认模型。这令人惊讶——付费订阅聚合器的用户会看到不同的模型处理他们的辅助流量。现在 `auto` 为所有人使用主模型，并且 `config.yaml` 中的每个任务覆盖仍然有效（请参阅下面的[完整辅助配置参考](#full-auxiliary-config-reference)）。
:::

### 交互式配置辅助模型 {#configuring-auxiliary-models-interactively}

无需手动编辑 YAML，运行 `hermes model` 并从菜单中选择 **“配置辅助模型”**。你将获得一个交互式的每个任务选择器：
```
$ hermes model
→ 配置辅助模型

[ ] vision               当前：auto / 主模型
[ ] web_extract          当前：auto / 主模型
[ ] session_search       当前：openrouter / google/gemini-2.5-flash
[ ] title_generation     当前：openrouter / google/gemini-3-flash-preview
[ ] compression          当前：auto / 主模型
[ ] approval             当前：auto / 主模型
```

选择一个任务，挑选一个提供商（OAuth 流程会打开浏览器；API 密钥提供商会弹出输入框），再选择一个模型。更改会持久化到 `config.yaml` 中的 `auxiliary.&lt;task&gt;.*` 配置项。操作方式与主模型选择器完全一致——无需学习额外语法。

### 视频教程 {#video-tutorial}

<div style={{position: 'relative', width: '100%', aspectRatio: '16 / 9', marginBottom: '1.5rem'}}>
  <iframe
    src="https://www.youtube.com/embed/NoF-YajElIM"
    title="Hermes Agent — 辅助模型教程"
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0}}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

### 通用配置模式 {#the-universal-config-pattern}

Hermes 中的每个模型槽位——辅助任务、压缩、回退——都使用相同的三个配置项：

| 键 | 作用 | 默认值 |
|-----|-------------|---------|
| `provider` | 用于认证和路由的提供商 | `"auto"` |
| `model` | 要请求的模型 | 提供商的默认模型 |
| `base_url` | 自定义 OpenAI 兼容端点（会覆盖提供商） | 未设置 |

当设置了 `base_url` 时，Hermes 会忽略提供商，直接调用该端点（使用 `api_key` 或 `OPENAI_API_KEY` 进行认证）。当只设置了 `provider` 时，Hermes 会使用该提供商内置的认证和基础 URL。

辅助任务可用的提供商：`auto`、`main`，以及[提供商注册表](/reference/environment-variables)中的任何提供商——`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`ollama-cloud`、`alibaba`、`bedrock`、`huggingface`、`arcee`、`xiaomi`、`kilocode`、`opencode-zen`、`opencode-go`、`ai-gateway`、`azure-foundry`——或者来自 `custom_providers` 列表的任何自定义提供商（例如 `provider: "beans"`）。

:::tip MiniMax OAuth
`minimax-oauth` 通过浏览器 OAuth 登录（无需 API 密钥）。运行 `hermes model` 并选择 **MiniMax (OAuth)** 进行认证。辅助任务会自动使用 `MiniMax-M2.7-highspeed`。请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。
:::

<a id="main-is-for-auxiliary-tasks-only"></a>
:::warning `"main"` 仅用于辅助任务
`"main"` 提供商选项的意思是“使用我的主 Agent 当前使用的任何提供商”——它仅在 `auxiliary:`、`compression:` 和 `fallback_model:` 配置中有效。它**不是**顶层 `model.provider` 设置的有效值。如果你使用自定义的 OpenAI 兼容端点，请在 `model:` 部分设置 `provider: custom`。有关所有主模型提供商选项，请参阅 [AI 提供商](/integrations/providers)。
:::
### 完整辅助配置参考 {#full-auxiliary-config-reference}

```yaml
auxiliary:
  # 图像分析（vision_analyze 工具 + 浏览器截图）
  vision:
    provider: "auto"           # "auto"、"openrouter"、"nous"、"codex"、"main" 等
    model: ""                  # 例如 "openai/gpt-4o"、"google/gemini-2.5-flash"
    base_url: ""               # 自定义 OpenAI 兼容端点（覆盖 provider）
    api_key: ""                # base_url 对应的 API 密钥（回退到 OPENAI_API_KEY）
    timeout: 120               # 秒 — LLM API 调用超时；视觉负载需要较大的超时时间
    download_timeout: 30       # 秒 — 图片 HTTP 下载；网络慢时可增大

  # 网页摘要 + 浏览器页面文本提取
  web_extract:
    provider: "auto"
    model: ""                  # 例如 "google/gemini-2.5-flash"
    base_url: ""
    api_key: ""
    timeout: 360               # 秒（6分钟）— 每次尝试的 LLM 摘要超时

  # 危险命令审批分类器
  approval:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30                # 秒

  # 上下文压缩超时（与 compression.* 配置分开）
  compression:
    timeout: 120               # 秒 — 压缩会总结长对话，需要更多时间

  # 会话搜索 — 总结过去匹配的会话
  session_search:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
    max_concurrency: 3       # 限制并行摘要数量，减少请求突发导致的 429 错误
    extra_body: {}           # 提供商特定的 OpenAI 兼容请求字段

  # 技能中心 — 技能匹配与搜索
  skills_hub:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # MCP 工具分发
  mcp:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
```

:::tip
每个辅助任务都有一个可配置的 `timeout`（以秒为单位）。默认值：vision 120 秒，web_extract 360 秒，approval 30 秒，compression 120 秒。如果辅助任务使用较慢的本地模型，请增大这些值。Vision 还有一个单独的 `download_timeout`（默认 30 秒）用于 HTTP 图片下载——如果网络连接较慢或使用自托管图片服务器，请增大此值。
:::

:::info
上下文压缩有自己的 `compression:` 块用于阈值设置，以及一个 `auxiliary.compression:` 块用于模型/提供商设置——请参见上面的[上下文压缩](#context-compression)。回退模型使用 `fallback_model:` 块——请参见[回退模型](/integrations/providers#fallback-model)。三者都遵循相同的 provider/model/base_url 模式。
:::

### 会话搜索调优 {#session-search-tuning}

如果你为 `auxiliary.session_search` 使用一个推理密集型模型，Hermes 现在提供两个内置控制：

- `auxiliary.session_search.max_concurrency`：限制 Hermes 同时总结的匹配会话数量
- `auxiliary.session_search.extra_body`：在摘要调用中转发提供商特定的 OpenAI 兼容请求字段

示例：
```yaml
auxiliary:
  session_search:
    provider: "main"
    model: "glm-4.5-air"
    timeout: 60
    max_concurrency: 2
    extra_body:
      enable_thinking: false
```

当您的提供商对请求爆发速率有限制，并且您希望 `session_search` 牺牲一些并行性来换取稳定性时，请使用 `max_concurrency`。

仅当您的提供商文档中包含您希望 Hermes 为该项任务透传的、与 OpenAI 兼容的请求体字段时，才使用 `extra_body`。Hermes 会原样转发该对象。

:::warning
`extra_body` 仅在您的提供商实际支持您发送的字段时才有效。如果提供商没有提供原生的、与 OpenAI 兼容的推理关闭标志，Hermes 无法代其合成一个。
:::

### 更换视觉模型 {#changing-the-vision-model}

要用 GPT-4o 替代 Gemini Flash 进行图像分析：

```yaml
auxiliary:
  vision:
    model: "openai/gpt-4o"
```

或者通过环境变量（在 `~/.hermes/.env` 中）：

```bash
AUXILIARY_VISION_MODEL=openai/gpt-4o
```

### 提供商选项 {#provider-options}

以下选项适用于**辅助任务配置**（`auxiliary:`、`compression:`、`fallback_model:`），不适用于您的主要 `model.provider` 设置。

| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 自动选择最佳可用（默认）。视觉任务会依次尝试 OpenRouter → Nous → Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter — 路由到任何模型（Gemini、GPT-4o、Claude 等） | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth（ChatGPT 账户）。支持视觉（gpt-5.3-codex）。 | `hermes model` → Codex |
| `"minimax-oauth"` | 强制使用 MiniMax OAuth（浏览器登录，无需 API 密钥）。辅助任务使用 MiniMax-M2.7-highspeed。 | `hermes model` → MiniMax（OAuth） |
| `"main"` | 使用您当前激活的自定义/主端点。可以来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY`，也可以来自通过 `hermes model` / `config.yaml` 保存的自定义端点。适用于 OpenAI、本地模型或任何兼容 OpenAI 的 API。**仅限辅助任务 — 不能用于 `model.provider`。** | 自定义端点凭据 + 基础 URL |

当您希望旁路任务绕过默认路由器时，主提供商目录中的直接 API 密钥提供商也同样适用。配置 `GMI_API_KEY` 后，`gmi` 是有效的：

```yaml
auxiliary:
  compression:
    provider: "gmi"
    model: "anthropic/claude-opus-4.6"
```

对于 GMI 辅助路由，请使用 GMI 的 `/v1/models` 端点返回的确切模型 ID。

### 常见配置 {#common-setups}

**使用直接自定义端点**（对于本地/自托管 API，这比 `provider: "main"` 更清晰）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`，因此这是将辅助任务路由到特定端点最明确的方式。对于直接端点覆盖，Hermes 会使用配置的 `api_key`，否则回退到 `OPENAI_API_KEY`；它不会为该自定义端点复用 `OPENROUTER_API_KEY`。

**使用 OpenAI API 密钥进行视觉分析：**
```yaml
# 在 ~/.hermes/.env 中：
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # 或者用 "gpt-4o-mini" 更便宜
```
**使用 OpenRouter 实现视觉功能**（路由到任意模型）：
```yaml
auxiliary:
  vision:
    provider: "openrouter"
    model: "openai/gpt-4o"      # 或 "google/gemini-2.5-flash" 等
```

**使用 Codex OAuth**（ChatGPT Pro/Plus 账户 — 无需 API 密钥）：
```yaml
auxiliary:
  vision:
    provider: "codex"     # 使用你的 ChatGPT OAuth 令牌
    # 模型默认为 gpt-5.3-codex（支持视觉）
```

**使用 MiniMax OAuth**（浏览器登录，无需 API 密钥）：
```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-oauth
  base_url: https://api.minimax.io/anthropic
```
运行 `hermes model` 并选择 **MiniMax (OAuth)** 即可登录并自动设置。对于中国区域，base URL 将为 `https://api.minimaxi.com/anthropic`。完整操作指南请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。

**使用本地/自托管模型**：
```yaml
auxiliary:
  vision:
    provider: "main"      # 使用你当前的自定义端点
    model: "my-local-model"
```

`provider: "main"` 会使用 Hermes 用于普通聊天的任何提供商——无论是命名的自定义提供商（例如 `beans`）、内置提供商（如 `openrouter`），还是传统的 `OPENAI_BASE_URL` 端点。

:::tip
如果你使用 Codex OAuth 作为主要模型提供商，视觉功能会自动生效——无需额外配置。Codex 已包含在视觉功能的自动检测链中。
:::

:::warning
**视觉功能需要多模态模型。** 如果你设置了 `provider: "main"`，请确保你的端点支持多模态/视觉——否则图像分析将失败。
:::

### 环境变量（传统方式） {#environment-variables-legacy}

辅助模型也可以通过环境变量进行配置。不过，`config.yaml` 是更推荐的方式——它更易于管理，并且支持所有选项，包括 `base_url` 和 `api_key`。

| 设置项 | 环境变量 |
|---------|---------|
| 视觉提供商 | `AUXILIARY_VISION_PROVIDER` |
| 视觉模型 | `AUXILIARY_VISION_MODEL` |
| 视觉端点 | `AUXILIARY_VISION_BASE_URL` |
| 视觉 API 密钥 | `AUXILIARY_VISION_API_KEY` |
| 网页提取提供商 | `AUXILIARY_WEB_EXTRACT_PROVIDER` |
| 网页提取模型 | `AUXILIARY_WEB_EXTRACT_MODEL` |
| 网页提取端点 | `AUXILIARY_WEB_EXTRACT_BASE_URL` |
| 网页提取 API 密钥 | `AUXILIARY_WEB_EXTRACT_API_KEY` |

压缩和回退模型设置仅支持 config.yaml 配置。

:::tip
运行 `hermes config` 查看你当前的辅助模型设置。覆盖项仅在它们与默认值不同时才会显示。
:::

## 推理力度 {#reasoning-effort}

控制模型在响应前进行“思考”的程度：

```yaml
agent:
  reasoning_effort: ""   # 空 = 中等（默认）。选项：none, minimal, low, medium, high, xhigh（最大）
```

当未设置（默认）时，推理力度默认为“medium”——这是一个平衡的水平，适用于大多数任务。设置一个值会覆盖默认值——更高的推理力度在复杂任务上能获得更好的结果，但会消耗更多令牌并增加延迟。

你也可以在运行时使用 `/reasoning` 命令更改推理力度：
```
/reasoning           # 显示当前推理努力级别和状态
/reasoning high      # 将推理努力设置为高
/reasoning none      # 禁用推理
/reasoning show      # 在每个回复上方显示模型思考过程
/reasoning hide      # 隐藏模型思考过程
```

## 工具使用强制 {#tool-use-enforcement}

有些模型偶尔会以文本形式描述预期操作，而不是实际调用工具（例如说“我会运行测试……”而不是实际调用终端）。工具使用强制会在系统提示中注入引导，促使模型重新实际调用工具。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["模型子串", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"`（默认） | 对匹配以下模型启用：`gpt`, `codex`, `gemini`, `gemma`, `grok`。其他模型（Claude, DeepSeek, Qwen 等）禁用。 |
| `true` | 始终启用，无论模型是什么。如果你发现当前模型描述操作而不是执行操作时很有用。 |
| `false` | 始终禁用，无论模型是什么。 |
| `["gpt", "codex", "qwen", "llama"]` | 仅当模型名称包含列出的子串之一时启用（不区分大小写）。 |

### 注入的内容 {#what-it-injects}

启用后，系统提示中可能会添加三层指导：

1. **通用工具使用强制**（所有匹配的模型）—— 指示模型立即进行工具调用，而不是描述意图，持续工作直到任务完成，并且永远不要以承诺未来行动结束一轮。
2. **OpenAI 执行纪律**（仅限 GPT 和 Codex 模型）—— 针对 GPT 特定失败模式的额外指导：在部分结果上放弃工作、跳过先决条件查找、幻觉而不是使用工具、以及未经验证就声明“完成”。
3. **Google 操作指导**（仅限 Gemini 和 Gemma 模型）—— 简洁性、绝对路径、并行工具调用以及先验证后编辑的模式。

这些对用户是透明的，只影响系统提示。已经可靠使用工具的模型（如 Claude）不需要此指导，这就是为什么 `"auto"` 排除了它们。

### 何时启用 {#when-to-turn-it-on}

如果你使用的模型不在默认的自动列表中，并且注意到它经常描述它*将要*做什么而不是实际去做，请设置 `tool_use_enforcement: true` 或将模型子串添加到列表中：

```yaml
agent:
  tool_use_enforcement: ["gpt", "codex", "gemini", "grok", "my-custom-model"]
```

## TTS 配置 {#tts-configuration}

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts"
  speed: 1.0                    # 全局速度倍率（所有提供商的回退）
  edge:
    voice: "en-US-AriaNeural"   # 322 种声音，74 种语言
    speed: 1.0                  # 速度倍率（转换为速率百分比，例如 1.5 → +50%）
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0                  # 速度倍率（API 限制在 0.25–4.0 之间）
    base_url: "https://api.openai.com/v1"  # 覆盖 OpenAI 兼容的 TTS 端点
  minimax:
    speed: 1.0                  # 语音速度倍率
    # base_url: ""              # 可选：覆盖 OpenAI 兼容的 TTS 端点
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - 中性（默认）
  gemini:
    model: "gemini-2.5-flash-preview-tts"   # 或 gemini-2.5-pro-preview-tts
    voice: "Kore"               # 30 种预置声音：Zephyr, Puck, Kore, Enceladus 等
  xai:
    voice_id: "eve"             # xAI TTS 声音
    language: "en"              # ISO 639-1
    sample_rate: 24000
    bit_rate: 128000            # MP3 比特率
    # base_url: "https://api.x.ai/v1"
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```
这同时控制 `text_to_speech` 工具和语音模式下的语音回复（CLI 或消息网关中的 `/voice tts`）。

**速度回退层级：** 特定提供者的速度（例如 `tts.edge.speed`）→ 全局 `tts.speed` → 默认值 `1.0`。设置全局 `tts.speed` 可对所有提供者应用统一速度，或按提供者单独覆盖以实现精细控制。

## 显示设置 {#display-settings}

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # 在消息网关中启用 /verbose 斜杠命令
  platforms: {}           # 按平台覆盖显示设置（见下文）
  tool_progress_overrides: {}  # 已弃用 — 改用 display.platforms
  interim_assistant_messages: true  # 网关：将自然的中途助手更新作为独立消息发送
  skin: default           # 内置或自定义 CLI 皮肤（参见 user-guide/features/skins）
  personality: "kawaii"  # 遗留的装饰性字段，仍会在某些摘要中显示
  compact: false          # 紧凑输出模式（减少空白）
  resume_display: full    # full（恢复时显示之前消息）| minimal（仅一行）
  bell_on_complete: false # Agent 完成时播放终端提示音（适合长时间任务）
  show_reasoning: false   # 在每条回复上方显示模型推理/思考过程（通过 /reasoning show|hide 切换）
  streaming: false        # 将 token 实时流式传输到终端（实时输出）
  show_cost: false        # 在 CLI 状态栏中显示预估美元成本
  tool_preview_length: 0  # 工具调用预览的最大字符数（0 = 无限制，显示完整路径/命令）
  runtime_metadata_footer: false  # 网关：在最终回复末尾追加运行时上下文页脚
```

| 模式 | 显示内容 |
|------|----------|
| `off` | 静默 — 仅显示最终回复 |
| `new` | 仅当工具切换时显示工具指示器 |
| `all` | 每次工具调用都显示简短预览（默认） |
| `verbose` | 显示完整参数、结果和调试日志 |

在 CLI 中，可通过 `/verbose` 循环切换这些模式。要在消息平台（Telegram、Discord、Slack 等）中使用 `/verbose`，请在上方 `display` 部分设置 `tool_progress_command: true`。该命令随后会循环切换模式并保存到配置中。

### 运行时元数据页脚（仅限网关） {#runtime-metadata-footer-gateway-only}

当 `display.runtime_metadata_footer: true` 时，Hermes 会在每个网关回合的**最终**消息末尾追加一个小的运行时上下文页脚 — 与 CLI 状态栏显示的信息相同（模型、会话时长、token、成本）。默认关闭；如果你的团队希望每条回复都包含来源信息，可按网关选择启用。

```yaml
display:
  runtime_metadata_footer: true
```

追加到 Telegram/Discord/Slack 回复中的示例页脚：

```
— claude-opus-4.7 · 12 次工具调用 · 2m 14s · $0.042
```

只有回合的**最终**消息会带有页脚；中途更新保持干净。

### 按平台覆盖进度显示 {#per-platform-progress-overrides}

不同平台对详细程度的需求不同。例如，Signal 无法编辑消息，因此每次进度更新都会变成独立消息 — 很嘈杂。使用 `display.platforms` 设置按平台模式：
```yaml
display:
  tool_progress: all          # 全局默认值
  platforms:
    signal:
      tool_progress: 'off'    # 在 Signal 上静默进度
    telegram:
      tool_progress: verbose  # 在 Telegram 上显示详细进度
    slack:
      tool_progress: 'off'    # 在共享 Slack 工作区中保持安静
```

没有单独覆盖的平台会回退到全局的 `tool_progress` 值。有效的平台键：`telegram`、`discord`、`slack`、`signal`、`whatsapp`、`matrix`、`mattermost`、`email`、`sms`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot`。为了向后兼容，旧的 `display.tool_progress_overrides` 键仍然会被加载，但已弃用，并在首次加载时迁移到 `display.platforms` 中。

`interim_assistant_messages` 仅适用于网关。启用后，Hermes 会将完成的中间轮次助手更新作为单独的聊天消息发送。这与 `tool_progress` 无关，且不需要网关流式传输。

## 隐私 {#privacy}

```yaml
privacy:
  redact_pii: false  # 从 LLM 上下文中剥离 PII（仅限网关）
```

当 `redact_pii` 为 `true` 时，网关会在将系统提示发送给 LLM 之前，从支持的平台上剥离个人身份信息：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 上的用户 ID） | 哈希为 `user_<12-char-sha256>` |
| 用户 ID | 哈希为 `user_<12-char-sha256>` |
| 聊天 ID | 数字部分哈希，平台前缀保留（`telegram:&lt;hash&gt;`） |
| 主频道 ID | 数字部分哈希 |
| 用户名 / 用户昵称 | **不受影响**（用户自选，公开可见） |

**平台支持：** 脱敏适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 被排除，因为它们的提及系统（`<@user_id>`）需要在 LLM 上下文中使用真实 ID。

哈希是确定性的——同一用户始终映射到同一哈希，因此模型仍然可以在群聊中区分不同用户。路由和投递在内部使用原始值。

## 语音转文字（STT） {#speech-to-text-stt}

```yaml
stt:
  provider: "local"            # "local" | "groq" | "openai" | "mistral"
  local:
    model: "base"              # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe
  # model: "whisper-1"         # 旧版回退键仍然有效
```

各提供商的行为：

- `local` 使用在你的机器上运行的 `faster-whisper`。请单独安装：`pip install faster-whisper`。
- `groq` 使用 Groq 的 Whisper 兼容端点，并读取 `GROQ_API_KEY`。
- `openai` 使用 OpenAI 语音 API，并读取 `VOICE_TOOLS_OPENAI_KEY`。

如果请求的提供商不可用，Hermes 会按以下顺序自动回退：`local` → `groq` → `openai`。

Groq 和 OpenAI 的模型覆盖由环境变量驱动：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

## 语音模式（CLI） {#voice-mode-cli}
```yaml
voice:
  record_key: "ctrl+b"         # CLI 中的按键通话键
  max_recording_seconds: 120    # 长录音的硬性停止时间
  auto_tts: false               # 当 /voice on 时自动启用语音回复
  beep_enabled: true            # 在 CLI 语音模式下播放录音开始/结束提示音
  silence_threshold: 200        # 语音检测的 RMS 阈值
  silence_duration: 3.0         # 自动停止前的静音秒数
```

在 CLI 中使用 `/voice on` 启用麦克风模式，使用 `record_key` 开始/停止录音，使用 `/voice tts` 切换语音回复。有关端到端设置和平台特定行为，请参阅[语音模式](/user-guide/features/voice-mode)。

## 流式输出 {#streaming}

将令牌实时流式传输到终端或消息平台，而不是等待完整响应。

### CLI 流式输出 {#cli-streaming}

```yaml
display:
  streaming: true         # 实时将令牌流式传输到终端
  show_reasoning: true    # 同时流式传输推理/思考令牌（可选）
```

启用后，响应会逐令牌显示在流式输出框中。工具调用仍然静默捕获。如果提供商不支持流式输出，则会自动回退到正常显示。

### 网关流式输出（Telegram、Discord、Slack） {#gateway-streaming-telegram-discord-slack}

```yaml
streaming:
  enabled: true           # 启用渐进式消息编辑
  transport: edit         # "edit"（渐进式消息编辑）或 "off"
  edit_interval: 0.3      # 消息编辑之间的秒数
  buffer_threshold: 40    # 强制刷新编辑前的字符数
  cursor: " ▉"            # 流式输出期间显示的光标
  fresh_final_after_seconds: 60   # 当预览超过此时间时发送全新最终消息（Telegram）；0 = 始终原地编辑
```

启用后，机器人会在第一个令牌到达时发送一条消息，然后随着更多令牌到达逐步编辑该消息。不支持消息编辑的平台（Signal、Email、Home Assistant）会在首次尝试时自动检测——流式输出会在该会话中被优雅地禁用，不会产生消息洪流。

如果需要独立的自然中间助手更新（不进行渐进式令牌编辑），请设置 `display.interim_assistant_messages: true`。

**溢出处理：** 如果流式文本超过平台的消息长度限制（约 4096 字符），当前消息会被最终确定，并自动开始一条新消息。

**全新最终消息（Telegram）：** Telegram 的 `editMessageText` 会保留原始消息的时间戳，因此长时间运行的流式回复即使完成后也会保留第一个令牌的时间戳。当 `fresh_final_after_seconds > 0`（默认 `60`）时，完成的回复会作为一条全新消息发送（旧预览会尽力删除），这样 Telegram 的可见时间戳就反映了完成时间。短预览仍然原地最终确定。设置为 `0` 则始终原地编辑。

:::note
流式输出默认关闭。在 `~/.hermes/config.yaml` 中启用它以体验流式输出界面。
:::

## 群聊会话隔离 {#group-chat-session-isolation}

控制共享聊天是按房间保持一个对话还是按参与者保持一个对话：
```yaml
group_sessions_per_user: true  # true = 在群组/频道中按用户隔离会话，false = 每个聊天共享一个会话
```

- `true` 是默认值，也是推荐设置。在 Discord 频道、Telegram 群组、Slack 频道等共享上下文中，当平台提供用户 ID 时，每个发送者都会获得自己的会话。
- `false` 则恢复为旧的共享房间行为。如果你明确希望 Hermes 将频道视为一个协作对话，这个选项可能有用，但这也意味着用户共享上下文、token 成本和中断状态。
- 私聊不受影响。Hermes 仍然像往常一样通过聊天/DM ID 来标识私聊。
- 无论哪种设置，线程都与父频道隔离；当设置为 `true` 时，线程内的每个参与者也会获得自己的会话。

有关行为细节和示例，请参阅[会话](/user-guide/sessions)和[Discord 指南](/user-guide/messaging/discord)。

## 未授权私聊行为 {#unauthorized-dm-behavior}

控制当未知用户发送私聊时 Hermes 的行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。Hermes 拒绝访问，但会在私聊中回复一个一次性配对码。
- `ignore` 静默丢弃未授权的私聊。
- 平台配置段会覆盖全局默认值，因此你可以在大多数平台上保持配对启用，同时让某个平台更安静。

## 快速命令 {#quick-commands}

定义自定义命令，这些命令要么在不调用 LLM 的情况下运行 shell 命令，要么将一个斜杠命令别名到另一个。执行型快速命令不消耗 token，适用于从消息平台（Telegram、Discord 等）快速执行服务器检查或实用脚本。

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  disk:
    type: exec
    command: df -h /
  update:
    type: exec
    command: cd ~/.hermes/hermes-agent && git pull && pip install -e .
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader
  restart:
    type: alias
    target: /gateway restart
```

用法：在 CLI 或任何消息平台中输入 `/status`、`/disk`、`/update`、`/gpu` 或 `/restart`。`exec` 命令在主机本地运行并直接返回输出——不调用 LLM，不消耗 token。`alias` 命令会重写为配置的斜杠命令目标。

- **30 秒超时**——长时间运行的命令会被终止并显示错误消息
- **优先级**——快速命令在技能命令之前被检查，因此你可以覆盖技能名称
- **自动补全**——快速命令在分派时解析，不会显示在内置的斜杠命令自动补全表中
- **类型**——支持的类型是 `exec` 和 `alias`；其他类型会显示错误
- **随处可用**——CLI、Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant

纯字符串的提示快捷方式不是有效的快速命令。对于可重用的提示工作流，请创建一个技能或别名到现有的斜杠命令。

## 人工延迟 {#human-delay}
在消息平台中模拟类人响应节奏：

```yaml
human_delay:
  mode: "off"                  # off | natural | custom
  min_ms: 800                  # 最小延迟（custom 模式）
  max_ms: 2500                 # 最大延迟（custom 模式）
```

## 代码执行 {#code-execution}

配置 `execute_code` 工具：

```yaml
code_execution:
  mode: project                # project（默认）| strict
  timeout: 300                 # 最大执行时间（秒）
  max_tool_calls: 50           # 代码执行内的最大工具调用次数
```

**`mode`** 控制脚本的工作目录和 Python 解释器：

- **`project`**（默认）——脚本在会话的工作目录中运行，使用当前激活的 virtualenv/conda 环境的 python。项目依赖（`pandas`、`torch`、项目包）和相对路径（`.env`、`./data.csv`）自然解析，与 `terminal()` 看到的一致。
- **`strict`**——脚本在临时暂存目录中运行，使用 `sys.executable`（Hermes 自身的 python）。可重现性最高，但项目依赖和相对路径无法解析。

环境变量清理（移除 `*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_PASSWORD`、`*_CREDENTIAL`、`*_PASSWD`、`*_AUTH`）和工具白名单在两种模式下完全相同——切换模式不会改变安全态势。

## 网络搜索后端 {#web-search-backends}

`web_search`、`web_extract` 和 `web_crawl` 工具支持四个后端提供商。在 `config.yaml` 或通过 `hermes tools` 配置后端：

```yaml
web:
  backend: firecrawl    # firecrawl | parallel | tavily | exa
```

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |

**后端选择：** 如果未设置 `web.backend`，则根据可用的 API 密钥自动检测后端。如果只设置了 `EXA_API_KEY`，则使用 Exa。如果只设置了 `TAVILY_API_KEY`，则使用 Tavily。如果只设置了 `PARALLEL_API_KEY`，则使用 Parallel。否则默认使用 Firecrawl。

**自托管 Firecrawl：** 设置 `FIRECRAWL_API_URL` 指向你自己的实例。当设置了自定义 URL 时，API 密钥变为可选（在服务器上设置 `USE_DB_AUTHENTICATION=false` 以禁用认证）。

**Parallel 搜索模式：** 设置 `PARALLEL_SEARCH_MODE` 控制搜索行为——`fast`、`one-shot` 或 `agentic`（默认：`agentic`）。

**Exa：** 在 `~/.hermes/.env` 中设置 `EXA_API_KEY`。支持 `category` 过滤（`company`、`research paper`、`news`、`people`、`personal site`、`pdf`）以及域名/日期过滤器。

## 浏览器 {#browser}

配置浏览器自动化行为：

```yaml
browser:
  inactivity_timeout: 120        # 空闲会话自动关闭前的等待秒数
  command_timeout: 30             # 浏览器命令（截图、导航等）的超时秒数
  record_sessions: false         # 自动将浏览器会话录制为 WebM 视频，保存到 ~/.hermes/browser_recordings/
  # 可选的 CDP 覆盖——设置后，Hermes 直接附加到你自己的
  # Chrome（通过 /browser connect），而不是启动无头浏览器。
  cdp_url: ""
  # 对话框监督器——控制当附加了 CDP 后端（Browserbase、通过 /browser connect 连接的本地 Chrome）
  # 时如何处理原生 JS 对话框（alert / confirm / prompt）。
  # 在 Camofox 和默认的本地 Agent 浏览器模式下忽略。
  dialog_policy: must_respond    # must_respond | auto_dismiss | auto_accept
  dialog_timeout_s: 300          # must_respond 模式下的安全自动关闭（秒）
  camofox:
    managed_persistence: false   # 为 true 时，Camofox 会话在重启后保留 cookie/登录状态
```
**对话框策略：**

- `must_respond`（默认）— 捕获对话框，将其展示在 `browser_snapshot.pending_dialogs` 中，并等待 Agent 调用 `browser_dialog(action=...)`。如果在 `dialog_timeout_s` 秒内没有响应，对话框会自动关闭，以防止页面的 JS 线程无限挂起。
- `auto_dismiss` — 捕获后立即关闭。Agent 事后仍可在 `browser_snapshot.recent_dialogs` 中看到该对话框记录，其中 `closed_by="auto_policy"`。
- `auto_accept` — 捕获后立即接受。适用于带有激进 `beforeunload` 提示的页面。

完整的对话框工作流程请参见[浏览器功能页面](./features/browser.md#browser_dialog)。

浏览器工具集支持多个提供商。有关 Browserbase、Browser Use 和本地 Chrome CDP 设置的详细信息，请参见[浏览器功能页面](/user-guide/features/browser)。

## 时区 {#timezone}

使用 IANA 时区字符串覆盖服务器本地时区。影响日志中的时间戳、cron 调度和系统提示中的时间注入。

```yaml
timezone: "America/New_York"   # IANA 时区（默认："" = 服务器本地时间）
```

支持的值：任何 IANA 时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。留空或省略则使用服务器本地时间。

## Discord {#discord}

配置消息网关的 Discord 特定行为：

```yaml
discord:
  require_mention: true          # 在服务器频道中需要 @提及 才能回复
  free_response_channels: ""     # 逗号分隔的频道 ID，机器人无需 @提及 即可回复
  auto_thread: true              # 在频道中 @提及 时自动创建线程
```

- `require_mention` — 当为 `true`（默认）时，机器人仅在服务器频道中被 `@BotName` 提及时才回复。私信始终无需提及即可工作。
- `free_response_channels` — 逗号分隔的频道 ID 列表，机器人无需提及即可回复每条消息。
- `auto_thread` — 当为 `true`（默认）时，频道中的提及会自动为对话创建线程，保持频道整洁（类似于 Slack 的线程功能）。

## 安全 {#security}

执行前的安全扫描和机密信息脱敏：

```yaml
security:
  redact_secrets: false          # 在工具输出和日志中脱敏 API 密钥模式（默认关闭）
  tirith_enabled: true           # 启用 Tirith 安全扫描终端命令
  tirith_path: "tirith"          # tirith 二进制文件的路径（默认：$PATH 中的 "tirith"）
  tirith_timeout: 5              # 等待 tirith 扫描的超时秒数
  tirith_fail_open: true         # 如果 tirith 不可用，允许执行命令
  website_blocklist:             # 参见下方网站黑名单部分
    enabled: false
    domains: []
    shared_files: []
```

- `redact_secrets` — 当为 `true` 时，自动检测并脱敏工具输出中看起来像 API 密钥、令牌和密码的模式，然后再进入对话上下文和日志。**默认关闭** — 如果你经常在工具输出中使用真实凭据并希望有一个安全网，请启用。显式设置为 `true` 以开启。
- `tirith_enabled` — 当为 `true` 时，终端命令在执行前会由 [Tirith](https://github.com/StackGuardian/tirith) 扫描，以检测潜在的危险操作。
- `tirith_path` — tirith 二进制文件的路径。如果 tirith 安装在非标准位置，请设置此项。
- `tirith_timeout` — 等待 tirith 扫描的最大秒数。如果扫描超时，命令将继续执行。
- `tirith_fail_open` — 当为 `true`（默认）时，如果 tirith 不可用或失败，允许执行命令。设置为 `false` 可在 tirith 无法验证时阻止命令执行。
## 网站黑名单 {#website-blocklist}

阻止 Agent 的网页和浏览器工具访问特定域名：

```yaml
security:
  website_blocklist:
    enabled: false               # 启用 URL 拦截（默认：false）
    domains:                     # 被拦截的域名模式列表
      - "*.internal.company.com"
      - "admin.example.com"
      - "*.local"
    shared_files:                # 从外部文件加载额外规则
      - "/etc/hermes/blocked-sites.txt"
```

启用后，任何匹配黑名单域名模式的 URL 都会在网页或浏览器工具执行前被拒绝。这适用于 `web_search`、`web_extract`、`browser_navigate` 以及任何访问 URL 的工具。

域名规则支持：
- 精确域名：`admin.example.com`
- 通配符子域名：`*.internal.company.com`（拦截所有子域名）
- TLD 通配符：`*.local`

共享文件中每行一个域名规则（空行和 `#` 注释会被忽略）。文件缺失或无法读取时会记录警告，但不会禁用其他网页工具。

该策略会缓存 30 秒，因此配置更改无需重启即可快速生效。

## 智能审批 {#smart-approvals}

控制 Hermes 如何处理潜在危险命令：

```yaml
approvals:
  mode: manual   # manual | smart | off
```

| 模式 | 行为 |
|------|------|
| `manual`（默认） | 在执行任何被标记的命令前提示用户。在 CLI 中显示交互式审批对话框。在消息中，会排队等待审批请求。 |
| `smart` | 使用辅助 LLM 评估被标记的命令是否真正危险。低风险命令会自动批准，并在会话级别持久化。真正危险的命令会升级给用户处理。 |
| `off` | 跳过所有审批检查。等同于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

智能模式特别有助于减少审批疲劳——它让 Agent 在安全操作上更自主地工作，同时仍能捕获真正具有破坏性的命令。

:::warning
将 `approvals.mode` 设置为 `off` 会禁用终端命令的所有安全检查。仅在受信任的沙盒环境中使用。
:::

## 检查点 {#checkpoints}

在执行破坏性文件操作前自动创建文件系统快照。详见[检查点与回滚](/user-guide/checkpoints-and-rollback)。

```yaml
checkpoints:
  enabled: true                  # 启用自动检查点（也可用：hermes --checkpoints）
  max_snapshots: 50              # 每个目录保留的最大检查点数量
```

## 委派 {#delegation}

配置子 Agent 的委派工具行为：

```yaml
delegation:
  # model: "google/gemini-3-flash-preview"  # 覆盖模型（留空则继承父级）
  # provider: "openrouter"                  # 覆盖提供商（留空则继承父级）
  # base_url: "http://localhost:1234/v1"    # 直接使用 OpenAI 兼容端点（优先级高于 provider）
  # api_key: "local-key"                    # base_url 的 API 密钥（回退到 OPENAI_API_KEY）
  max_concurrent_children: 3                # 每批并行子 Agent 数量（最小 1，无上限）。也可通过 DELEGATION_MAX_CONCURRENT_CHILDREN 环境变量设置。
  max_spawn_depth: 1                        # 委派树深度上限（1-3，自动钳制）。1 = 扁平（默认）：父级生成叶子节点，叶子节点不能继续委派。2 = 编排器子级可以生成叶子孙级。3 = 三级。
  orchestrator_enabled: true                # 全局开关。设为 false 时，role="orchestrator" 被忽略，所有子级强制为叶子节点，忽略 max_spawn_depth。
```
**子 Agent 的 provider/model 覆盖：** 默认情况下，子 Agent 会继承父 Agent 的 provider 和 model。设置 `delegation.provider` 和 `delegation.model` 可以将子 Agent 路由到不同的 provider:model 组合——例如，让主 Agent 运行昂贵的推理模型，同时为范围狭窄的子任务使用便宜/快速的模型。

**直接端点覆盖：** 如果你想要明显的自定义端点路径，可以设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这样会将子 Agent 直接发送到该 OpenAI 兼容端点，并且优先级高于 `delegation.provider`。如果省略了 `delegation.api_key`，Hermes 只会回退到 `OPENAI_API_KEY`。

委托 provider 使用与 CLI/网关启动相同的凭据解析方式。所有配置的 provider 都受支持：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。当设置了 provider 时，系统会自动解析正确的 base URL、API key 和 API 模式——无需手动配置凭据。

**优先级：** 配置中的 `delegation.base_url` → 配置中的 `delegation.provider` → 父 provider（继承）。配置中的 `delegation.model` → 父 model（继承）。仅设置 `model` 而不设置 `provider` 只会更改模型名称，同时保留父级的凭据（适用于在同一 provider（如 OpenRouter）内切换模型）。

**宽度和深度：** `max_concurrent_children` 限制每批并行运行的子 Agent 数量（默认 `3`，最小值为 1，无上限）。也可以通过 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量设置。当模型提交的 `tasks` 数组长度超过上限时，`delegate_task` 会返回一个工具错误，说明限制原因，而不是静默截断。`max_spawn_depth` 控制委托树的深度（限制在 1-3 之间）。默认值为 `1` 时，委托是扁平的：子 Agent 不能生成孙 Agent，并且传递 `role="orchestrator"` 会静默降级为 `leaf`。提升到 `2` 后，编排器子 Agent 可以生成叶子孙 Agent；`3` 则支持三层树。Agent 通过每次调用中的 `role="orchestrator"` 选择加入编排；`orchestrator_enabled: false` 会强制所有子 Agent 恢复为叶子，无论其他设置如何。成本会成倍增长——当 `max_spawn_depth: 3` 且 `max_concurrent_children: 3` 时，树可以达到 3×3×3 = 27 个并发叶子 Agent。有关使用模式，请参阅 [子 Agent 委托 → 深度限制与嵌套编排](features/delegation.md#depth-limit-and-nested-orchestration)。

## Clarify {#clarify}

配置澄清提示行为：

```yaml
clarify:
  timeout: 120                 # 等待用户澄清响应的秒数
```

## 上下文文件（SOUL.md、AGENTS.md） {#context-files-soul-md-agents-md}

Hermes 使用两种不同的上下文范围：

| 文件 | 用途 | 范围 |
|------|---------|-------|
| `SOUL.md` | **主 Agent 身份**——定义 Agent 是谁（系统提示中的第 1 个插槽） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定指令（最高优先级） | 向上遍历到 git 根目录 |
| `AGENTS.md` | 项目特定指令、编码约定 | 递归目录遍历 |
| `CLAUDE.md` | Claude Code 上下文文件（也会被检测到） | 仅工作目录 |
| `.cursorrules` | Cursor IDE 规则（也会被检测到） | 仅工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被检测到） | 仅工作目录 |
- **SOUL.md** 是 Agent 的主要身份标识。它占据系统提示中的 1 号插槽，完全取代内置的默认身份。编辑它即可完全自定义 Agent 的身份。
- 如果 SOUL.md 缺失、为空或无法加载，Hermes 会回退到内置的默认身份。
- **项目上下文文件使用优先级系统**——仅加载一种类型（优先匹配第一个）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。SOUL.md 始终独立加载。
- **AGENTS.md** 是分层的：如果子目录也有 AGENTS.md，则所有内容会合并。
- 如果 SOUL.md 尚不存在，Hermes 会自动生成一个默认的 SOUL.md。
- 所有加载的上下文文件限制为 20,000 个字符，并会智能截断。

另请参阅：
- [个性与 SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)

## 工作目录 {#working-directory}

| 上下文 | 默认值 |
|---------|---------|
| **CLI（`hermes`）** | 运行命令的当前目录 |
| **消息网关** | 主目录 `~`（可通过 `MESSAGING_CWD` 覆盖） |
| **Docker / Singularity / Modal / SSH** | 容器或远程机器内的用户主目录 |

覆盖工作目录：
```bash
# 在 ~/.hermes/.env 或 ~/.hermes/config.yaml 中：
MESSAGING_CWD=/home/myuser/projects    # 网关会话
TERMINAL_CWD=/workspace                # 所有终端会话
```
