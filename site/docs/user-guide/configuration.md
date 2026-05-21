---
sidebar_position: 2
title: "配置"
description: "配置 Hermes Agent — config.yaml、提供商、模型、API 密钥等"
---

<a id="configuration"></a>
# 配置

所有设置都存储在 `~/.hermes/` 目录中，便于访问。

<a id="directory-structure"></a>
## 目录结构

```text
~/.hermes/
├── config.yaml     # 设置（模型、终端、TTS、压缩等）
├── .env            # API 密钥和机密信息
├── auth.json       # OAuth 提供商凭据（Nous Portal 等）
├── SOUL.md         # 主要 Agent 身份（系统提示词中的 #1 槽位）
├── memories/       # 持久记忆（MEMORY.md、USER.md）
├── skills/         # Agent 创建的技能（通过 skill_manage 工具管理）
├── cron/           # 定时任务
├── sessions/       # 网关会话
└── logs/           # 日志（errors.log、gateway.log — 机密信息会自动涂改）
```

<a id="managing-configuration"></a>
## 管理配置

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
`hermes config set` 命令会自动将值路由到正确的文件——API 密钥保存到 `.env`，其他所有内容保存到 `config.yaml`。
:::

<a id="configuration-precedence"></a>
## 配置优先级

设置按以下顺序解析（优先级从高到低）：

1. **CLI 参数** — 例如 `hermes chat --model anthropic/claude-sonnet-4`（单次调用覆盖）
2. **`~/.hermes/config.yaml`** — 所有非机密设置的主配置文件
3. **`~/.hermes/.env`** — 环境变量的后备；**必须**用于机密信息（API 密钥、令牌、密码）
4. **内置默认值** — 当没有其他设置时硬编码的安全默认值

:::info 经验法则
机密信息（API 密钥、机器人令牌、密码）放在 `.env` 中。其他所有内容（模型、终端后端、压缩设置、记忆限制、工具集）放在 `config.yaml` 中。当两者都设置时，非机密设置以 `config.yaml` 为准。
<a id="rule-of-thumb"></a>
:::

<a id="environment-variable-substitution"></a>
## 环境变量替换

你可以在 `config.yaml` 中使用 `${VAR_NAME}` 语法引用环境变量：

```yaml
auxiliary:
  vision:
    api_key: ${GOOGLE_API_KEY}
    base_url: ${CUSTOM_VISION_URL}

delegation:
  api_key: ${DELEGATION_KEY}
```

单个值中可包含多个引用：`url: "${HOST}:${PORT}"`。如果引用的变量未设置，占位符将原样保留（`${UNDEFINED_VAR}` 保持不变）。仅支持 `${VAR}` 语法——单纯的 `$VAR` 不会展开。

关于 AI 提供商设置（OpenRouter、Anthropic、Copilot、自定义端点、自托管 LLM、后备模型等），请参阅 [AI 提供商](/integrations/providers)。

<a id="provider-timeouts"></a>
### 提供商超时

你可以通过 `providers.&lt;id&gt;.request_timeout_seconds` 设置提供商级别的请求超时，另外通过 `providers.&lt;id&gt;.models.&lt;model&gt;.timeout_seconds` 设置特定模型的超时覆盖。这适用于每个传输方式（OpenAI-wire、原生 Anthropic、Anthropic 兼容）上的主轮次客户端、后备链、凭据轮换后的重建，以及（对于 OpenAI-wire）每个请求的超时 kwargs——因此配置值会覆盖传统的 `HERMES_API_TIMEOUT` 环境变量。
你也可以为非流式超时调用检测器设置 `providers.&lt;id&gt;.stale_timeout_seconds`，同时还可以通过 `providers.&lt;id&gt;.models.&lt;model&gt;.stale_timeout_seconds` 为特定模型单独设置超时时间。这些设置会覆盖旧的 `HERMES_API_CALL_STALE_TIMEOUT` 环境变量。

如果保持未设置状态，则会使用旧的默认值（`HERMES_API_TIMEOUT=1800`秒，`HERMES_API_CALL_STALE_TIMEOUT=300`秒，Anthropic 原生 900 秒）。目前尚未支持 AWS Bedrock（`bedrock_converse` 和 AnthropicBedrock SDK 路径都使用 boto3，其超时配置由 boto3 自身管理）。请参考 [`cli-config.yaml.example`](https://github.com/NousResearch/hermes-agent/blob/main/cli-config.yaml.example) 中的注释示例。

<a id="terminal-backend-configuration"></a>
## 终端后端配置

Hermes 支持七种终端后端。每种后端决定了 Agent 的 shell 命令实际在哪里执行——你的本地机器、Docker 容器、通过 SSH 连接的远程服务器、Modal 云沙箱（直接或通过 Nous 管理的网关）、Daytona 工作区、Vercel Sandbox，或 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | vercel_sandbox | singularity
  cwd: "."          # 网关/定时任务的工作目录（CLI 始终使用启动目录）
  timeout: 180      # 每条命令的超时时间（秒）
  env_passthrough: []  # 需要传递给沙箱执行环境的环境变量名称（terminal + execute_code）
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Singularity 后端的容器镜像
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Modal 后端的容器镜像
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Daytona 后端的容器镜像
```

对于 Modal、Daytona 和 Vercel Sandbox 这类云沙箱，`container_persistent: true` 表示 Hermes 会尝试在沙箱重建时保留文件系统状态。但这并不保证同一个活跃沙箱、PID 空间或后台进程在后续仍然可用。

<a id="backend-overview"></a>
### 后端概览

| 后端 | 命令执行位置 | 隔离性 | 适用场景 |
|---------|-------------------|-----------|----------|
| **local** | 直接在你的机器上 | 无 | 开发、个人使用 |
| **docker** | 单个持久化 Docker 容器（跨会话、`/new`、子 Agent 共享） | 完全隔离（命名空间、cap-drop） | 安全沙箱、CI/CD |
| **ssh** | 通过 SSH 连接远程服务器 | 网络边界 | 远程开发、使用高性能硬件 |
| **modal** | Modal 云沙箱 | 完全隔离（云虚拟机） | 临时云计算、评估 |
| **daytona** | Daytona 工作区 | 完全隔离（云容器） | 托管云开发环境 |
| **vercel_sandbox** | Vercel Sandbox | 完全隔离（云微虚拟机） | 基于快照持久化文件系统的云执行 |
| **singularity** | Singularity/Apptainer 容器 | 命名空间（--containall） | HPC 集群、共享机器 |

<a id="local-backend"></a>
### Local 后端

默认选项。命令直接在你的机器上执行，没有任何隔离。无需特殊配置。

```yaml
terminal:
  backend: local
```
:::warning
Agent 对文件系统的访问权限与您的用户账户相同。使用 `hermes tools` 禁用不需要的工具，或切换到 Docker 以实现沙箱隔离。
:::

<a id="docker-backend"></a>
### Docker 后端

在具有安全加固功能的 Docker 容器中运行命令（所有能力已被剥夺，无特权升级，有 PID 限制）。

**单个持久化容器，而非每个命令一个容器。** Hermes 在首次使用时启动一个长期运行的容器，并在 Hermes 进程的整个生命周期内，将所有终端、文件和 `execute_code` 调用通过 `docker exec` 路由到同一个容器中——跨会话、`/new`、`/reset` 以及 `delegate_task` subagents。工作目录的变更、安装的包以及 `/workspace` 中的文件会在工具调用之间延续，就像本地 shell 一样。容器在关闭时停止并删除。详见下方的 **容器生命周期**。

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # 将启动目录挂载到 /workspace
  docker_run_as_host_user: false   # 见下方“以主机用户身份运行容器”
  docker_forward_env:              # 转发到容器中的环境变量
    - "GITHUB_TOKEN"
  docker_volumes:                  # 主机目录挂载
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"   # :ro 表示只读
  docker_extra_args:               # 额外标志，逐字追加到 `docker run`
    - "--gpus=all"
    - "--network=host"

  # 资源限制
  container_cpu: 1                 # CPU 核心数（0 = 无限制）
  container_memory: 5120           # MB（0 = 无限制）
  container_disk: 51200            # MB（需要 XFS+pquota 上的 overlay2）
  container_persistent: true       # 跨会话持久化 /workspace 和 /root
```

**`terminal.docker_extra_args`**（也可通过 `TERMINAL_DOCKER_EXTRA_ARGS='["--gpus=all"]'` 覆盖）允许您传递 Hermes 未作为一等键暴露的任何 `docker run` 标志——`--gpus`、`--network`、`--add-host`、替代的 `--security-opt` 覆盖等。每个条目必须是字符串；该列表会被追加到组装的 `docker run` 调用的最后，因此如有必要可覆盖 Hermes 的默认值。请谨慎使用——与沙箱加固（能力剥夺、`--user`、工作区绑定挂载）冲突的标志会悄悄削弱隔离性。

**要求：** 已安装并运行 Docker Desktop 或 Docker Engine。Hermes 会搜索 `$PATH` 以及常见的 macOS 安装位置（`/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用包）。Podman 开箱即用：当两者都安装时，设置 `HERMES_DOCKER_BINARY=podman`（或完整路径）以强制使用。

**容器生命周期：** Hermes 在 Hermes 进程的整个生命周期内，为每次终端和文件工具调用重复使用一个长期运行的容器（`docker run -d ... sleep 2h`），跨会话、`/new`、`/reset` 以及 `delegate_task` subagents。命令通过 `docker exec` 使用登录 shell 运行，因此工作目录变更、已安装的包和 `/workspace` 中的文件都会在工具调用之间持续存在。容器在 Hermes 关闭时（或当空闲回收器回收它时）停止并删除。
通过 `delegate_task(tasks=[...])` 生成的并行子 Agent 共享同一个容器——并发的 `cd`、环境变量修改以及对同一路径的写入会产生冲突。如果某个子 Agent 需要隔离沙箱，它必须通过 `register_task_env_overrides()` 注册按任务定制的镜像覆盖，RL 和基准测试环境（TerminalBench2、HermesSweEnv 等）会自动为其按任务划分的 Docker 镜像执行此操作。

**安全加固：**
- `--cap-drop ALL`，仅恢复添加 `DAC_OVERRIDE`、`CHOWN`、`FOWNER`
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- `/tmp`（512MB）、`/var/tmp`（256MB）、`/run`（64MB）使用大小受限的 tmpfs

**凭证转发：** 在 `docker_forward_env` 中列出的环境变量，会先从你的 shell 环境解析，然后从 `~/.hermes/.env` 解析。技能也可以声明 `required_environment_variables`，这些变量会自动合并。

<a id="ssh-backend"></a>
### SSH 后端

通过 SSH 在远程服务器上运行命令。使用 ControlMaster 复用连接（5 分钟空闲保活）。默认启用持久化 shell —— 状态（当前目录、环境变量）跨命令保持。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # 保持一个长生存的 bash 会话（默认值：true）
```

**必需的环境变量：**

```bash
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=ubuntu
```

**可选参数：**

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `TERMINAL_SSH_PORT` | `22` | SSH 端口 |
| `TERMINAL_SSH_KEY` | （系统默认） | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | `true` | 启用持久 shell |

**工作原理：** 在初始化时使用 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 连接。持久 shell 在远程主机上保持一个 `bash -l` 进程存活，通过临时文件通信。需要 `stdin_data` 或 `sudo` 的命令会自动回退到一次性模式。

<a id="modal-backend"></a>
### Modal 后端

在 [Modal](https://modal.com) 云端沙箱中运行命令。每个任务获得一个独立的虚拟机，可配置 CPU、内存和磁盘。文件系统可以在会话之间快照/恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU 核数
  container_memory: 5120           # MB（5GB）
  container_disk: 51200            # MB（50GB）
  container_persistent: true       # 快照/恢复文件系统
```

**必需：** 环境变量 `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET`，或者 `~/.modal.toml` 配置文件。

**持久化：** 启用后，沙箱文件系统会在清理时快照，并在下一次会话时恢复。快照记录在 `~/.hermes/modal_snapshots.json` 中。这会保留文件系统状态，而不是活动进程、PID 空间或后台作业。

**凭证文件：** 自动从 `~/.hermes/`（OAuth 令牌等）挂载，并在每条命令执行前同步。

<a id="daytona-backend"></a>
### Daytona 后端

在 [Daytona](https://daytona.io) 管理的工作空间中运行命令。支持停止/恢复以实现持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU 核数
  container_memory: 5120           # MB → 转换为 GiB
  container_disk: 10240            # MB → 转换为 GiB（最大 10 GiB）
  container_persistent: true       # 停止/恢复而不是删除
```
**必需：** `DAYTONA_API_KEY` 环境变量。

**持久化：** 启用后，沙箱在清理时会被停止（而非删除），并在下次会话时恢复。沙箱名称遵循 `hermes-{task_id}` 的命名模式。

**磁盘限制：** Daytona 强制限制最大 10 GiB。超出此限制的请求会被截断并发出警告。

<a id="vercel-sandbox-backend"></a>
### Vercel Sandbox 后端

在 [Vercel Sandbox](https://vercel.com/docs/vercel-sandbox) 云微虚拟机中运行命令。Hermes 使用标准的终端和文件工具接口；没有面向模型的 Vercel 特定工具。

```yaml
terminal:
  backend: vercel_sandbox
  vercel_runtime: node24          # node24 | node22 | python3.13
  cwd: /vercel/sandbox            # 默认工作区根目录
  container_persistent: true      # 快照/恢复文件系统
  container_disk: 51200           # 仅共享默认值；不支持自定义磁盘
```

**必需安装：** 安装可选的 SDK 附加组件：

```bash
pip install 'hermes-agent[vercel]'
```

**必需认证：** 使用 `VERCEL_TOKEN`、`VERCEL_PROJECT_ID` 和 `VERCEL_TEAM_ID` 这三个环境变量配置访问令牌认证。这是部署以及在 Render、Railway、Docker 及类似主机上运行常规长时间 Hermes 进程时支持的设置。

对于一次性本地开发，Hermes 也接受短期有效的 Vercel OIDC 令牌：

```bash
VERCEL_OIDC_TOKEN="$(vc project token <project-name>)" hermes chat
```

在已关联的 Vercel 项目目录中，可以省略项目名称：

```bash
VERCEL_OIDC_TOKEN="$(vc project token)" hermes chat
```

OIDC 令牌有效期短，不应作为文档中描述的部署路径使用。

**运行时：** `terminal.vercel_runtime` 支持 `node24`、`node22` 和 `python3.13`。如果未设置，Hermes 默认使用 `node24`。

**持久化：** 当 `container_persistent: true` 时，Hermes 会在清理期间对沙箱文件系统进行快照，并在后续为同一任务恢复沙箱时从该快照恢复。快照内容可以包括 Hermes 同步到沙箱中的凭据、技能和缓存文件。这仅保留文件系统状态；不会保留实时沙箱身份、PID 空间、Shell 状态或正在运行的后台进程。

**后台命令：** `terminal(background=true)` 使用 Hermes 的通用非本地后台进程流程。在沙箱存活期间，您可以通过常规进程工具生成、轮询、等待、查看日志和终止进程。Hermes 在清理或重启后不提供原生的 Vercel 分离进程恢复功能。

**磁盘大小：** Vercel Sandbox 目前不支持 Hermes 的 `container_disk` 资源控制参数。请将 `container_disk` 保持未设置状态或使用共享默认值 `51200`；非默认值会导致诊断和后端创建失败，而不会静默忽略。

<a id="singularity-apptainer-backend"></a>
### Singularity/Apptainer 后端

在 [Singularity/Apptainer](https://apptainer.org) 容器中运行命令。专为无法使用 Docker 的 HPC 集群和共享机器设计。

```yaml
terminal:
  backend: singularity
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB
  container_persistent: true       # 可写覆盖层在会话间持久化
```
**要求：** `$PATH` 中需包含 `apptainer` 或 `singularity` 二进制文件。

**镜像处理：** Docker 地址（`docker://...`）会自动转换为 SIF 文件并缓存。现有的 `.sif` 文件会直接使用。

**临时目录：** 按以下顺序解析：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent`（HPC 约定） → `~/.hermes/sandboxes/singularity`。

**隔离机制：** 使用 `--containall --no-home` 实现完整的命名空间隔离，不挂载宿主主目录。

<a id="common-terminal-backend-issues"></a>
### 常见终端后端问题

如果终端命令立即失败，或终端工具被报告为不可用：

- **Local** — 无特殊要求。入门时最安全的默认选项。
- **Docker** — 运行 `docker version` 验证 Docker 是否正常工作。如果失败，修复 Docker 或执行 `hermes config set terminal.backend local`。
- **SSH** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER`。如果缺少任一变量，Hermes 会记录清晰的错误信息。
- **Modal** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml` 文件。运行 `hermes doctor` 检查。
- **Daytona** — 需要 `DAYTONA_API_KEY`。Daytona SDK 会处理服务器 URL 配置。
- **Singularity** — 需要 `$PATH` 中包含 `apptainer` 或 `singularity`。常见于 HPC 集群。

如有疑问，先将 `terminal.backend` 改回 `local`，确认命令能在本地运行后再排查。

<a id="remote-to-host-file-sync-on-teardown"></a>
### 会话结束时的远程到宿主文件同步

对于 **SSH**、**Modal** 和 **Daytona** 后端（Agent 的工作树与运行 Hermes 的宿主不在同一台机器上的情况），Hermes 会跟踪 Agent 在远程沙箱中操作过的文件，并在会话结束/沙箱清理时，**将修改过的文件同步回宿主**，存放在 `~/.hermes/cache/remote-syncs/&lt;session-id&gt;/` 目录下。

- 触发时机：会话关闭、`/new`、`/reset`、网关消息超时、`delegate_task` 子 Agent 完成时（如果子 Agent 使用了远程后端）。
- 覆盖范围：Agent 修改过的整个树状结构，而不仅仅是它显式打开的文件。新增、编辑和删除操作都会被记录。
- 当你回头查看时，远程沙箱可能已被销毁；本地的 `~/.hermes/cache/remote-syncs/…` 副本是 Agent 所做更改的权威记录。
- 大型二进制输出（模型检查点、原始数据集）有大小限制——同步会跳过超过 `file_sync_max_mb`（默认 `100`）的文件。如果你预期会有更大的产物返回，请调高此值。

```yaml
terminal:
  file_sync_max_mb: 100     # 默认值——同步每个最大 100 MB 的文件
  file_sync_enabled: true   # 默认值——设为 false 可完全跳过同步
```

这就是从临时云沙箱恢复结果的方法——这些沙箱在会话结束后会被销毁，你无需让 Agent 显式执行 `scp` 或 `modal volume put` 来获取每个产物。

<a id="docker-volume-mounts"></a>
### Docker 卷挂载

使用 Docker 后端时，`docker_volumes` 允许你将宿主目录共享到容器中。每个条目使用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # 读写（默认）
    - "/home/user/datasets:/data:ro"              # 只读
    - "/home/user/.hermes/cache/documents:/output" # 网关可见的导出目录
```
这对以下场景很有用：
- **向 Agent 提供文件**（数据集、配置、参考代码）
- **从 Agent 接收文件**（生成的代码、报告、导出文件）
- **共享工作空间**，你和 Agent 都可以访问同一批文件

如果你使用消息网关并希望 Agent 通过 `MEDIA:/...` 发送生成的文件，建议使用专用的宿主机可见导出挂载点，例如 `/home/user/.hermes/cache/documents:/output`。

- 在 Docker 内将文件写入 `/output/...`
- 在 `MEDIA:` 中填写 **宿主机路径**，例如：`MEDIA:/home/user/.hermes/cache/documents/report.txt`
- **不要**填写 `/workspace/...` 或 `/output/...`，除非该路径在宿主机上的网关进程也能访问

:::warning
YAML 重复键会静默覆盖前面的键。如果你已经有 `docker_volumes:` 块，请将新的挂载点合并到同一个列表中，而不是在文件后面再加一个 `docker_volumes:` 键。
:::

也可以通过环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组）。

<a id="docker-credential-forwarding"></a>
### Docker 凭证转发

默认情况下，Docker 终端会话不会继承任意宿主机凭证。如果你需要在容器内使用特定令牌，请将其添加到 `terminal.docker_forward_env` 中。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 会先从你当前的 shell 中解析列出的每个变量，如果该变量曾通过 `hermes config set` 保存到 `~/.hermes/.env`，则会回退到该文件。

:::warning
`docker_forward_env` 中列出的任何内容对容器内执行的命令都是可见的。只转发你愿意暴露给终端会话的凭证。
:::

<a id="running-the-container-as-your-host-user"></a>
### 以宿主机用户身份运行容器

默认情况下，Docker 容器以 `root`（UID 0）身份运行。在 `/workspace` 或其他绑定挂载目录中创建的文件在宿主机上会归 root 所有，因此会话结束后，你需要使用 `sudo chown` 才能从宿主机编辑器编辑它们。`terminal.docker_run_as_host_user` 标志可以解决这个问题：

```yaml
terminal:
  backend: docker
  docker_run_as_host_user: true   # 默认值: false
```

启用后，Hermes 会在 `docker run` 命令后追加 `--user $(id -u):$(id -g)`，这样写入绑定挂载目录（`/workspace`、`/root` 及 `docker_volumes` 中的任何路径）的文件将归宿主机用户所有，而不是 root。代价是：容器将无法执行 `apt install` 或向 root 拥有的路径（如 `/root/.npm`）写入文件。如果两全其美，请使用 `HOME` 归非 root 用户所有的基础镜像（或在构建镜像时添加所需工具）。

保持 `false`（默认值）可实现向后兼容。当你的工作流程主要是“编辑挂载的宿主机文件”并且你已厌倦 `sudo chown -R` 时，可以启用它。

<a id="optional-mount-the-launch-directory-into-workspace"></a>
### 可选：将启动目录挂载到 `/workspace`

Docker 沙箱默认保持隔离。除非你明确选择，否则 Hermes **不会**将你当前的宿主机工作目录传入容器。

在 `config.yaml` 中启用：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```
启用时：
- 如果你从 `~/projects/my-app` 启动 Hermes，该主机目录会被绑定挂载到 `/workspace`
- Docker 后端会在 `/workspace` 中启动
- 文件工具和终端命令都能看到同一个已挂载的项目

禁用时，`/workspace` 仍是沙箱私有目录，除非你通过 `docker_volumes` 显式挂载了其他内容。

安全性权衡：
- `false` 保留沙箱边界
- `true` 让沙箱直接访问你启动 Hermes 时所处的目录

仅在你确实希望容器操作宿主机上的实时文件时，才选择启用。

<a id="persistent-shell"></a>
### 持久化 Shell

默认情况下，每条终端命令都在独立的子进程中运行——工作目录、环境变量和 Shell 变量会在命令之间重置。启用 **持久化 Shell** 后，一个长期存活的 bash 进程会在多次 `execute()` 调用之间保持运行，因此状态可以在命令间持久保留。

这对 **SSH 后端** 最为有用，因为它还能消除每条命令的连接开销。持久化 Shell 在 **SSH 后端中默认启用**，在本地后端中默认禁用。

```yaml
terminal:
  persistent_shell: true   # 默认值——为 SSH 启用持久化 Shell
```

要禁用：

```bash
hermes config set terminal.persistent_shell false
```

**哪些内容会在命令间持久保留：**
- 工作目录（`cd /tmp` 对下一条命令仍然有效）
- 导出的环境变量（`export FOO=bar`）
- Shell 变量（`MY_VAR=hello`）

**优先级：**

| 层级 | 变量 | 默认值 |
|-------|----------|---------|
| 配置 | `terminal.persistent_shell` | `true` |
| SSH 覆盖 | `TERMINAL_SSH_PERSISTENT` | 跟随配置 |
| 本地覆盖 | `TERMINAL_LOCAL_PERSISTENT` | `false` |

每种后端的环境变量优先级最高。如果你也想在本地后端启用持久化 Shell：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
需要 `stdin_data` 或 sudo 的命令会自动回退到一次性模式，因为持久化 Shell 的 stdin 已被 IPC 协议占用。
:::

关于各后端的详细信息，请参见[代码执行](features/code-execution.md) 和 [README 的终端部分](features/tools.md)。

<a id="skill-settings"></a>
## 技能设置 {#skill-settings}

技能可以通过其 SKILL.md 的 frontmatter 声明自己的配置项。这些是非机密值（路径、偏好、领域设置），存储在 `config.yaml` 的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    myplugin:
      path: ~/myplugin-data   # 示例——每个技能定义自己的键
```

**技能设置的工作方式：**

- `hermes config migrate` 会扫描所有已启用的技能，找到未配置的设置，并提示你进行配置
- `hermes config show` 会在“技能设置”下显示所有技能设置及所属技能
- 当技能加载时，其解析后的配置值会自动注入到技能上下文中

**手动设置值：**

```bash
hermes config set skills.config.myplugin.path ~/myplugin-data
```

关于在你的技能中声明配置设置的详细信息，请参见[创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。
<a id="guard-on-agent-created-skill-writes"></a>
### Guard on agent-created skill writes

当 Agent 使用 `skill_manage` 创建、编辑、修补或删除技能时，Hermes 可以选择扫描新/更新内容中是否存在危险关键词模式（凭证窃取、明显的提示注入、外发指令）。扫描器默认**关闭** —— 因为合法的 Agent 工作流确实会触及 `~/.ssh/` 或提到 `$OPENAI_API_KEY`，这在启发式规则下会频繁触发误报。如果你希望扫描器在 Agent 的技能写入生效前提示你，可以将其开启：

```yaml
skills:
  guard_agent_created: true   # 默认: false
```

开启后，任何被标记的 `skill_manage` 写入操作都会显示为审批提示，同时附上扫描器的判断理由。通过的写入会生效；被拒绝的写入则会向 Agent 返回一条说明错误的提示。

<a id="memory-configuration"></a>
## 内存配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
```

<a id="file-read-safety"></a>
## 文件读取安全

控制单次 `read_file` 调用所能返回的最大内容量。超出此限制的读取会被拒绝，并返回一条错误，提示 Agent 使用 `offset` 和 `limit` 来请求更小的范围。这样可以防止一次性读取一个压缩后的 JS 文件或大数据文件时冲垮上下文窗口。

```yaml
file_read_max_chars: 100000  # 默认值 —— 约 25-35K tokens
```

如果你使用的是大上下文窗口的模型，且经常读取大文件，可以调高此值。对于小上下文模型，则调低此值，让读取保持在较低的开销：

```yaml
# 大上下文模型（200K+）
file_read_max_chars: 200000

# 小本地模型（16K 上下文）
file_read_max_chars: 30000
```

Agent 还会自动对文件读取进行去重 —— 如果同一文件区域被读取两次，且文件没有发生变化，则会返回一个轻量级的桩数据，而不是重新发送内容。在上下文压缩后，这个去重机制会重置，这样 Agent 就可以在内容被总结压缩后重新读取文件。

<a id="tool-output-truncation-limits"></a>
## 工具输出截断限制

三个相关的上限控制了 Hermes 在截断工具输出之前的原始输出量：

```yaml
tool_output:
  max_bytes: 50000        # 终端输出上限（字符数）
  max_lines: 2000         # read_file 分页上限
  max_line_length: 2000   # read_file 行号视图中的每行上限
```

- **`max_bytes`** —— 当 `terminal` 命令产生的标准输出和标准错误总字符数超过此值时，Hermes 会保留前 40% 和后 60%，并在中间插入一条 `[OUTPUT TRUNCATED]` 提示。默认值为 `50000`（在常见的分词器下约等于 12-15K tokens）。
- **`max_lines`** —— 单次 `read_file` 调用中 `limit` 参数的上限。超出此范围的请求会被静默截断，以防止单次读取冲垮上下文窗口。默认值为 `2000`。
- **`max_line_length`** —— 当 `read_file` 输出行号视图时，每行的长度上限。超过此长度的行会被截断为这么多字符，并在后面加上 `... [truncated]`。默认值为 `2000`。

对于大上下文窗口的模型，可以调高这些限制，因为它们能够承受每次调用更多的原始输出。对于小上下文模型，则调低它们，以保持工具结果紧凑：
```yaml
# 大上下文模型（200K+）
tool_output:
  max_bytes: 150000
  max_lines: 5000

# 小型本地模型（16K 上下文）
tool_output:
  max_bytes: 20000
  max_lines: 500
```

<a id="global-toolset-disable"></a>
## 全局工具集禁用

要统一禁用 CLI 及所有网关平台上的特定工具集，可以在 `agent.disabled_toolsets` 下列出它们的名称：

```yaml
agent:
  disabled_toolsets:
    - memory       # 隐藏 memory 工具 + MEMORY_GUIDANCE 注入
    - web          # 禁止任何地方的 web_search / web_extract
```

该设置在**各平台工具配置**（通过 `hermes tools` 写入的 `platform_toolsets`）之后生效，因此这里列出的工具集一定会被移除——即使某个平台保存的配置中仍然保留它。当你想要一个统一的开关来“在所有地方关闭 X”，而不用在 `hermes tools` 界面中编辑 15 个以上的平台行时，可以使用此功能。

若列表为空或省略该键，则不产生任何影响。

<a id="git-worktree-isolation"></a>
## Git 工作树隔离

启用隔离的 Git 工作树，以便在同一仓库上并行运行多个 Agent：

```yaml
worktree: true    # 总是创建工作树（等同于 hermes -w）
# worktree: false # 默认行为——仅在传递 -w 标志时创建
```

启用后，每个 CLI 会话都会在 `.worktrees/` 下创建一个新的工作树，并带有独立的分支。Agent 可以编辑文件、提交、推送和创建 PR，而不会互相干扰。干净的工作树在退出时会被删除；脏的工作树会保留下来供手动恢复。

你还可以在仓库根目录下通过 `.worktreeinclude` 文件列出要复制到工作树中的 gitignore 文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

<a id="context-compression"></a>
## 上下文压缩 {#context-compression}

Hermes 会自动压缩长对话，使其保持在模型上下文窗口内。压缩摘要器是一个独立的 LLM 调用——你可以将其指向任何提供商或端点。

所有压缩设置都位于 `config.yaml` 中（无环境变量）。

<a id="full-reference"></a>
### 完整参考

```yaml
compression:
  enabled: true                                     # 启用/禁用压缩
  threshold: 0.50                                   # 达到上下文限制的此百分比时进行压缩
  target_ratio: 0.20                                # 保留为最近尾部的阈值百分比
  protect_last_n: 20                                # 保留未压缩的最近消息最小数量
  hygiene_hard_message_limit: 400                   # 网关安全阀——参见下方说明

# 摘要模型/提供商在 auxiliary 下配置：
auxiliary:
  compression:
    model: ""                                       # 空值 = 使用主聊天模型。可覆盖为例如 "google/gemini-3-flash-preview" 以获得更便宜/更快的压缩。
    provider: "auto"                                # 提供商："auto"、"openrouter"、"nous"、"codex"、"main" 等
    base_url: null                                  # 自定义兼容 OpenAI 的端点（覆盖 provider）
```

<a id="legacy-config-migration"></a>
:::info 旧配置迁移
旧配置中的 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 会在首次加载时自动迁移到 `auxiliary.compression.*`（配置版本 17）。无需手动操作。
:::
`hygiene_hard_message_limit` 是一个仅作用于网关的 **压缩前安全阀门**。当会话中消息数量达到数千条时，可能会在常规基于上下文百分比的阈值触发之前就撞上模型上下文限制；当消息数量超过这个上限时，Hermes 会强制进行压缩（无论当前 token 用量如何）。默认值 `400` —— 如果平台通常有非常长的会话，可以调高此值；如果需要更激进的压缩，则调低。在运行中的网关上修改此值后，将在下一条消息生效（见下文）。

:::tip 网关热重载压缩与上下文长度
自近期版本起，在运行中的网关中修改 `model.context_length` 或 `config.yaml` 中任何 `compression.*` 键值，都会在下一条消息生效——无需重启网关、执行 `/reset` 或轮换会话。缓存代理的签名中包含这些键，因此网关在检测到变化时会透明地重建 Agent。API 密钥和工具/技能配置仍需要通过常规重载路径更新。
:::
<a id="gateway-hot-reload-of-compression-and-context-length"></a>

<a id="common-setups"></a>
### 常见配置

**默认（自动检测）——无需配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
使用您的主提供商和主模型。如果您希望压缩使用比主聊天模型更便宜的模型，可以按任务覆写（例如 `auxiliary.compression.provider: openrouter` + `model: google/gemini-2.5-flash`）。

**强制指定提供商**（基于 OAuth 或 API 密钥）：
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
指向一个自定义的兼容 OpenAI 的端点。使用 `OPENAI_API_KEY` 进行身份验证。

<a id="how-the-three-knobs-interact"></a>
### 三个旋钮如何相互作用

| `auxiliary.compression.provider` | `auxiliary.compression.base_url` | 结果 |
|---------------------|---------------------|--------|
| `auto`（默认） | 未设置 | 自动检测最佳可用提供商 |
| `nous` / `openrouter` 等 | 未设置 | 强制使用该提供商，使用其身份认证 |
| 任意值 | 已设置 | 直接使用自定义端点（忽略提供商） |

:::warning 摘要模型的上下文长度要求
<a id="summary-model-context-length-requirement"></a>
摘要模型**必须**拥有至少与您的主 Agent 模型一样大的上下文窗口。压缩器会将对话的完整中间部分发送给摘要模型——如果该模型的上下文窗口小于主模型，摘要调用将因上下文长度错误而失败。发生这种情况时，中间轮次将被**丢弃而不产生摘要**，从而导致对话上下文静默丢失。如果您覆写了模型，请验证其上下文长度是否达到或超过您的主模型。
:::

<a id="context-engine"></a>
## 上下文引擎

上下文引擎控制当接近模型的 token 限制时如何管理对话。内置的 `compressor` 引擎使用有损摘要（见[上下文压缩](/developer-guide/context-compression-and-caching)）。插件引擎可以用替代策略替换它。
```yaml
context:
  engine: "compressor"    # 默认 — 内置有损摘要
```

要使用插件引擎（例如，用于无损上下文管理的 LCM）：

```yaml
context:
  engine: "lcm"          # 必须与插件名称匹配
```

插件引擎**永远不会自动激活** — 你必须显式地将 `context.engine` 设置为插件名称。可用引擎可以通过 `hermes plugins` → Provider Plugins → Context Engine 浏览和选择。

关于内存插件的类似单选系统，请参阅[内存提供者](/user-guide/features/memory-providers)。

<a id="iteration-budget-pressure"></a>
## 迭代预算压力

当 Agent 处理包含大量工具调用的复杂任务时，可能会在不知不觉中耗尽迭代预算（默认：90 轮）。预算压力会在接近限制时自动向模型发出警告：

| 阈值 | 级别 | 模型看到的内容 |
|-----------|-------|---------------------|
| **70%** | 注意 | `[BUDGET: 63/90. 27 iterations left. Start consolidating.]` |
| **90%** | 警告 | `[BUDGET WARNING: 81/90. Only 9 left. Respond NOW.]` |

警告会被注入到最后一个工具结果的 JSON 中（作为 `_budget_warning` 字段），而不是作为单独的消息 — 这样可以保留提示缓存，并且不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # 每次对话轮次的最大迭代次数（默认：90）
  api_max_retries: 3           # 在启用回退之前每个提供者的重试次数（默认：3）
```

预算压力默认启用。Agent 会自然地将警告视为工具结果的一部分，鼓励它在迭代耗尽之前整合工作并给出响应。

当迭代预算完全耗尽时，CLI 会向用户显示通知：`⚠ Iteration budget reached (90/90) — response may be incomplete`。如果在工作过程中预算耗尽，Agent 会在停止前生成已完成工作的摘要。

`agent.api_max_retries` 控制 Hermes 在**启用**回退提供者切换之前，对临时错误（速率限制、连接断开、5xx）重试提供者 API 调用的次数。默认值为 `3` — 总共四次尝试。如果你配置了[回退提供者](/user-guide/features/fallback-providers)并希望更快地故障转移，请将其设置为 `0`，这样主提供者上的第一个临时错误会立即交给回退，而不是对不稳定的端点进行多次重试。

<a id="api-timeouts"></a>
### API 超时

Hermes 为流式调用设置了独立的超时层，并为非流式调用设置了陈旧检测器。仅当你将本地提供者保留在隐式默认值时，陈旧检测器才会自动调整。

| 超时类型 | 默认值 | 本地提供者 | 配置/环境变量 |
|---------|---------|----------------|--------------|
| Socket 读取超时 | 120s | 自动提升至 1800s | `HERMES_STREAM_READ_TIMEOUT` |
| 流式陈旧检测 | 180s | 自动禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| 非流式陈旧检测 | 300s | 隐式保留时自动禁用 | `providers.&lt;id&gt;.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT` |
| API 调用（非流式） | 1800s | 不变 | `providers.&lt;id&gt;.request_timeout_seconds` / `timeout_seconds` 或 `HERMES_API_TIMEOUT` |
**Socket 读取超时** 控制 httpx 等待从提供商获取下一块数据的时间。本地 LLM 在处理大型上下文时，预填充阶段可能需要几分钟才能产生第一个 token，因此 Hermes 在检测到本地端点时会将其提高到 30 分钟。如果你显式设置了 `HERMES_STREAM_READ_TIMEOUT`，则无论端点检测结果如何，都会使用该值。

**陈旧流检测** 会关闭那些收到 SSE 心跳包但没有实际内容的连接。对于本地提供商，此功能完全禁用，因为它们在预填充期间不会发送心跳包。

**陈旧非流检测** 会关闭长时间没有响应的非流式调用。默认情况下，Hermes 在本地端点上禁用此功能，以避免在长时间预填充期间出现误报。如果你显式设置了 `providers.&lt;id&gt;.stale_timeout_seconds`、`providers.&lt;id&gt;.models.&lt;model&gt;.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT`，即使在本地端点上也会使用该显式值。

<a id="context-pressure-warnings"></a>
## 上下文压力警告

与迭代预算压力不同，上下文压力跟踪对话距离**压缩阈值**有多近——即触发上下文压缩以总结较早消息的点。这有助于你和 Agent 了解对话何时变长。

| 进度 | 级别 | 发生什么 |
|----------|-------|-------------|
| **≥ 60%** 到阈值 | 信息 | CLI 显示青色进度条；网关发送信息性通知 |
| **≥ 85%** 到阈值 | 警告 | CLI 显示粗体黄色条；网关警告压缩即将发生 |

在 CLI 中，上下文压力在工具输出流中显示为进度条：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台上，会发送纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果自动压缩被禁用，警告会告诉你上下文可能会被截断。

上下文压力是自动的——无需配置。它纯粹作为面向用户的通知触发，不会修改消息流或将任何内容注入模型的上下文。

<a id="credential-pool-strategies"></a>
## 凭证池策略 {#credential-pool-strategies}

当你有多个 API 密钥或 OAuth 令牌用于同一提供商时，配置轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # 均匀循环使用密钥
  anthropic: least_used      # 始终选择使用最少的密钥
```

选项：`fill_first`（默认）、`round_robin`、`least_used`、`random`。完整文档请参阅[凭证池](/user-guide/features/credential-pools)。

<a id="prompt-caching"></a>
## 提示缓存

当活跃提供商支持时，Hermes 会自动开启跨会话提示缓存——无需用户配置。

对于 **原生 Anthropic**、**OpenRouter** 和 **Nous Portal** 上的 Claude，Hermes 会在系统提示和技能块上附加 `cache_control` 断点，TTL 为 1 小时（`ttl: "1h"`）。在新的一小时内首次发送按完整输入费率付费；同一小时内跨任何会话的后续发送则从缓存中以折扣后的缓存读取费率拉取。这意味着系统提示、加载的技能内容以及任何长上下文包含的早期部分会在 `hermes` 会话之间以及分叉的子 Agent 之间重复使用，持续一小时。
通义千问（阿里云 DashScope）上游将缓存 TTL 限制在 5 分钟，因此 Hermes 在那里使用 5 分钟的断点 TTL。其他通过第三方使用 Claude 的路径（AWS Bedrock、Azure Foundry）则回退到提供商自身的缓存默认值。xAI Grok 使用独立的会话固定 conversation-id 机制——参见 [xAI 提示缓存](/integrations/providers#xai-grok--responses-api--prompt-caching)。

没有开关可以禁用此功能——缓存始终开启，即使在单轮对话中也能省钱，因为仅系统提示就占了输入 token 数的相当一部分。

<a id="auxiliary-models"></a>
## 辅助模型 {#auxiliary-models}

Hermes 使用“辅助”模型处理图像分析、网页摘要、浏览器截图分析、会话标题生成和上下文压缩等辅助任务。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 会将所有辅助任务路由到你的**主聊天模型**——即你在 `hermes model` 中选择的同一个提供商/模型。你无需任何配置即可开始使用，但请注意，在昂贵的推理模型（Opus、MiniMax M2.7 等）上，辅助任务会增加可观的成本。如果你希望无论主模型如何，辅助任务都使用廉价且快速的模型，请显式设置 `auxiliary.&lt;task&gt;.provider` 和 `auxiliary.&lt;task&gt;.model`（例如，在 OpenRouter 上使用 Gemini Flash 处理视觉和网页提取）。

:::note 为什么“auto”会使用你的主模型
早期版本将聚合器用户（OpenRouter、Nous Portal）分流到廉价的提供商侧默认模型。这令人意外——购买了聚合器订阅的用户会发现处理其辅助流量的模型不同。现在 `auto` 对所有用户都使用主模型，而 `config.yaml` 中的按任务覆盖仍然生效（参见下面的[完整辅助配置参考](#full-auxiliary-config-reference)）。
<a id="why-auto-uses-your-main-model"></a>
:::

<a id="configuring-auxiliary-models-interactively"></a>
### 交互式配置辅助模型

无需手动编辑 YAML，运行 `hermes model` 并从菜单中选择 **“Configure auxiliary models”**。你将看到一个交互式的按任务选择器：

```
$ hermes model
→ Configure auxiliary models

[ ] vision               currently: auto / main model
[ ] web_extract          currently: auto / main model
[ ] title_generation     currently: openrouter / google/gemini-3-flash-preview
[ ] compression          currently: auto / main model
[ ] approval             currently: auto / main model
[ ] triage_specifier     currently: auto / main model
[ ] kanban_decomposer    currently: auto / main model
[ ] profile_describer    currently: auto / main model
```

选择一个任务，选择一个提供商（OAuth 流程会打开浏览器；API 密钥提供商会提示输入），然后选择一个模型。更改会持久化到 `config.yaml` 中的 `auxiliary.&lt;task&gt;.*`。与主模型选择器相同的机制——无需学习额外语法。

<a id="video-tutorial"></a>
### 视频教程

<div style={{position: 'relative', width: '100%', aspectRatio: '16 / 9', marginBottom: '1.5rem'}}>
  <iframe
    src="https://www.youtube.com/embed/NoF-YajElIM"
    title="Hermes Agent — 辅助模型教程"
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0}}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>
<a id="the-universal-config-pattern"></a>
### 通用配置模式

Hermes 中的每个模型槽位——辅助任务、压缩、回退——都使用相同的三个参数：

| 键 | 作用 | 默认值 |
|-----|-------------|---------|
| `provider` | 用于认证和路由的提供商 | `"auto"` |
| `model` | 请求的模型 | 提供商的默认模型 |
| `base_url` | 自定义 OpenAI 兼容端点（覆盖提供商） | 未设置 |

当设置了 `base_url` 时，Hermes 会忽略提供商，直接调用该端点（使用 `api_key` 或 `OPENAI_API_KEY` 进行认证）。当只设置了 `provider` 时，Hermes 会使用该提供商内置的认证和基础 URL。

辅助任务可用的提供商：`auto`、`main`，以及 [提供商注册表](/reference/environment-variables) 中的任何提供商——`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`alibaba`、`bedrock`、`huggingface`、`arcee`、`xiaomi`、`kilocode`、`opencode-zen`、`opencode-go`、`ai-gateway`、`azure-foundry`——或者来自 `custom_providers` 列表的任何命名自定义提供商（例如 `provider: "beans"`）。

:::tip MiniMax OAuth
`minimax-oauth` 通过浏览器 OAuth 登录（无需 API 密钥）。运行 `hermes model` 并选择 **MiniMax (OAuth)** 进行认证。辅助任务会自动使用 `MiniMax-M2.7-highspeed`。请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。
:::

:::tip xAI Grok OAuth
`xai-oauth` 为 SuperGrok 和 X Premium+ 订阅用户提供浏览器 OAuth 登录（无需 API 密钥）。运行 `hermes model` 并选择 **xAI Grok OAuth (SuperGrok Subscription)** 进行认证。同一个 OAuth 令牌会复用于所有直接面向 xAI 的界面（聊天、辅助任务、TTS、图像生成、视频生成、转录）。请参阅 [xAI Grok OAuth 指南](../guides/xai-grok-oauth.md)，如果 Hermes 在远程主机上，请参阅 [通过 SSH / 远程主机的 OAuth](../guides/oauth-over-ssh.md)。
:::

:::warning `"main"` 仅用于辅助任务
<a id="main-is-for-auxiliary-tasks-only"></a>
`"main"` 提供商选项的意思是“使用我的主 Agent 所使用的任何提供商”——它仅在 `auxiliary:`、`compression:` 和 `fallback_model:` 配置中有效。它**不是**顶层 `model.provider` 设置的有效值。如果你使用自定义的 OpenAI 兼容端点，请在 `model:` 部分设置 `provider: custom`。有关所有主模型提供商选项，请参阅 [AI 提供商](/integrations/providers)。
:::

<a id="full-auxiliary-config-reference"></a>
### 完整辅助配置参考

```yaml
auxiliary:
  # 图像分析（vision_analyze 工具 + 浏览器截图）
  vision:
    provider: "auto"           # "auto", "openrouter", "nous", "codex", "main" 等
    model: ""                  # 例如 "openai/gpt-4o", "google/gemini-2.5-flash"
    base_url: ""               # 自定义 OpenAI 兼容端点（覆盖提供商）
    api_key: ""                # base_url 的 API 密钥（回退到 OPENAI_API_KEY）
    timeout: 120               # 秒 — LLM API 调用超时；视觉负载需要较大的超时时间
    download_timeout: 30       # 秒 — 图片 HTTP 下载；慢速连接时增加此值

  # 网页摘要 + 浏览器页面文本提取
  web_extract:
    provider: "auto"
    model: ""                  # 例如 "google/gemini-2.5-flash"
    base_url: ""
    api_key: ""
    timeout: 360               # 秒（6分钟）— 每次尝试的 LLM 摘要超时

  # 危险命令批准分类器
  approval:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30                # 秒

  # 上下文压缩超时（与 compression.* 配置分开）
  compression:
    timeout: 120               # 秒 — 压缩会总结长对话，需要更多时间

  # 技能中心 — 技能匹配和搜索
  skills_hub:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # MCP 工具调度
  mcp:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # 看板分类说明器 — `hermes kanban specify &lt;id&gt;`（或仪表板上 Triage 列卡片的 ✨ Specify 按钮）使用此槽位将一行描述扩展为具体说明，并将任务提升为 `todo`。便宜快速的模型在这里效果很好；说明扩展内容短，不需要推理深度。
  triage_specifier:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 120
```
:::tip
每个辅助任务都有一个可配置的 `timeout`（单位：秒）。默认值：vision 120 秒、web_extract 360 秒、approval 30 秒、compression 120 秒。如果你在辅助任务中使用较慢的本地模型，请适当增加这些超时值。Vision 还有一个单独的 `download_timeout`（默认 30 秒）用于 HTTP 图片下载——如果网速慢或使用自托管图片服务器，请增大该值。
:::

:::info
上下文压缩有自己的 `compression:` 块来配置阈值，以及一个 `auxiliary.compression:` 块来设置模型/提供者参数——详见上文[上下文压缩](#context-compression)。回退模型使用 `fallback_model:` 块——详见[回退模型](/integrations/providers#fallback-model)。这三者都遵循相同的 provider/model/base_url 模式。
:::

<a id="openrouter-routing-pareto-code-for-auxiliary-tasks"></a>
### 辅助任务的 OpenRouter 路由与 Pareto Code

当某个辅助任务解析到 OpenRouter（明确指定或通过 `provider: "main"` 且在 OpenRouter 上使用主 Agent）时，主 Agent 的 `provider_routing` 和 `openrouter.min_coding_score` 设置**不会继承**——这是有意设计的，每个辅助任务都是独立的。要为某个辅助任务设置 OpenRouter 的提供者偏好或使用 [Pareto Code 路由器](/integrations/providers#openrouter-pareto-code-router)，请通过 `extra_body` 按任务设置：

```yaml
auxiliary:
  compression:
    provider: openrouter
    model: openrouter/pareto-code         # 为此任务使用 Pareto Code 路由器
    extra_body:
      provider:                            # OpenRouter 提供者路由偏好
        order: [anthropic, google]         # 按顺序尝试这些提供者
        sort: throughput                   # 或 "price" | "latency"
        # only: [anthropic]                # 限制为特定提供者
        # ignore: [deepinfra]              # 排除特定提供者
      plugins:                             # OpenRouter Pareto Code 路由器旋钮
        - id: pareto-router
          min_coding_score: 0.5            # 0.0–1.0；值越高表示编码能力越强
```

其结构与 OpenRouter 在聊天补全请求体中接受的格式一致。Hermes 会将整个 `extra_body` 原样转发，因此 [openrouter.ai/docs](https://openrouter.ai/docs) 中记录的任何其他 OpenRouter 请求体字段都以相同方式生效。

<a id="changing-the-vision-model"></a>
### 切换视觉模型

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

<a id="provider-options"></a>
### 提供者选项

以下选项适用于**辅助任务配置**（`auxiliary:`、`compression:`、`fallback_model:`），而不是主 `model.provider` 设置。

| Provider | 描述 | 要求 |
|----------|------|------|
| `"auto"` | 最佳可用提供者（默认）。Vision 依次尝试 OpenRouter → Nous → Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter——可路由到任何模型（Gemini、GPT-4o、Claude 等） | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth（ChatGPT 账号）。支持视觉（gpt-5.3-codex）。 | `hermes model` → Codex |
| `"minimax-oauth"` | 强制使用 MiniMax OAuth（浏览器登录，无需 API 密钥）。辅助任务使用 MiniMax-M2.7-highspeed。 | `hermes model` → MiniMax（OAuth） |
| `"xai-oauth"` | 强制使用 xAI Grok OAuth（SuperGrok 或 X Premium+ 订阅用户的浏览器登录，无需 API 密钥）。同一个 OAuth 令牌同时覆盖聊天、TTS、图像、视频和转录。 | `hermes model` → xAI Grok OAuth（SuperGrok 订阅） |
| `"main"` | 使用你当前激活的自定义主端点。该端点可以来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY`，或通过 `hermes model` / `config.yaml` 保存的自定义端点。可配合 OpenAI、本地模型或任何兼容 OpenAI 的 API 使用。**仅限辅助任务——不能用于 `model.provider`。** | 自定义端点凭证 + 基础 URL |
当辅助任务希望绕过默认路由器时，主提供商目录中的直接 API 密钥提供商同样适用。配置 `GMI_API_KEY` 后，`gmi` 即可使用：

```yaml
auxiliary:
  compression:
    provider: "gmi"
    model: "anthropic/claude-opus-4.6"
```

对于 GMI 辅助路由，请使用 GMI 的 `/v1/models` 端点返回的精确模型 ID。

<a id="common-setups"></a>
### 常见配置

**使用直接自定义端点**（对于本地/自托管 API，比 `provider: "main"` 更清晰）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 优先级高于 `provider`，因此这是将辅助任务路由到特定端点最明确的方式。对于直接端点覆盖，Hermes 使用配置的 `api_key`，或回退到 `OPENAI_API_KEY`；它不会为该自定义端点复用 `OPENROUTER_API_KEY`。

**使用 OpenAI API 密钥进行视觉理解：**
```yaml
# 在 ~/.hermes/.env 中：
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # 或使用 "gpt-4o-mini" 更便宜
```

**使用 OpenRouter 进行视觉理解**（路由到任意模型）：
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
运行 `hermes model` 并选择 **MiniMax (OAuth)** 来登录并自动设置。对于中国区域，base URL 将为 `https://api.minimaxi.com/anthropic`。完整指南请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。

**使用本地/自托管模型：**
```yaml
auxiliary:
  vision:
    provider: "main"      # 使用你当前激活的自定义端点
    model: "my-local-model"
```

`provider: "main"` 使用 Hermes 用于正常聊天的任何提供商——无论是命名自定义提供商（例如 `beans`）、内置提供商（如 `openrouter`），还是旧的 `OPENAI_BASE_URL` 端点。

:::tip
如果你使用 Codex OAuth 作为主模型提供商，视觉功能会自动生效——无需额外配置。Codex 已包含在视觉自动检测链中。
:::

:::warning
**视觉需要多模态模型。** 如果设置 `provider: "main"`，请确保你的端点支持多模态/视觉——否则图像分析将失败。
:::

<a id="environment-variables-legacy"></a>
### 环境变量（旧方式）

辅助模型也可以通过环境变量配置。但 `config.yaml` 是推荐方式——更易管理，且支持包括 `base_url` 和 `api_key` 在内的所有选项。

| 设置项 | 环境变量 |
|---------|---------------------|
| 视觉提供商 | `AUXILIARY_VISION_PROVIDER` |
| 视觉模型 | `AUXILIARY_VISION_MODEL` |
| 视觉端点 | `AUXILIARY_VISION_BASE_URL` |
| 视觉 API 密钥 | `AUXILIARY_VISION_API_KEY` |
| 网页提取提供商 | `AUXILIARY_WEB_EXTRACT_PROVIDER` |
| 网页提取模型 | `AUXILIARY_WEB_EXTRACT_MODEL` |
| 网页提取端点 | `AUXILIARY_WEB_EXTRACT_BASE_URL` |
| 网页提取 API 密钥 | `AUXILIARY_WEB_EXTRACT_API_KEY` |
压缩和后备模型设置仅限 config.yaml。

:::tip
运行 `hermes config` 查看当前的辅助模型设置。覆盖值只有与默认值不同时才会显示。
:::

<a id="reasoning-effort"></a>
## 推理努力

控制模型在响应前进行多少“思考”：

```yaml
agent:
  reasoning_effort: ""   # 空值 = medium（默认）。可选值：none、minimal、low、medium、high、xhigh（最大）
```

当未设置（默认）时，推理努力默认为“medium”——这是一种适合大多数任务的平衡级别。设置某个值将覆盖默认值——更高的推理努力在复杂任务上能带来更好的结果，但会消耗更多 token 并增加延迟。

你也可以在运行时通过 `/reasoning` 命令更改推理努力：

```
/reasoning           # 显示当前努力级别和显示状态
/reasoning high      # 将推理努力设置为 high
/reasoning none      # 禁用推理
/reasoning show      # 在每个响应上方显示模型思考
/reasoning hide      # 隐藏模型思考
```

<a id="tool-use-enforcement"></a>
## 工具使用强制

有些模型偶尔会以文本形式描述预期操作，而不是实际发起工具调用（例如说“我会运行测试……”而不是实际调用终端）。工具使用强制功能会注入系统提示指导，引导模型回到实际调用工具的轨道上。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["模型子串", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"`（默认） | 对匹配 `gpt`、`codex`、`gemini`、`gemma`、`grok` 的模型启用。对其他所有模型禁用（Claude、DeepSeek、Qwen 等）。 |
| `true` | 始终启用，与模型无关。如果你发现当前模型描述操作而不是执行操作，这个设置很有用。 |
| `false` | 始终禁用，与模型无关。 |
| `["gpt", "codex", "qwen", "llama"]` | 仅在模型名称包含所列子串之一时启用（不区分大小写）。 |

<a id="what-it-injects"></a>
### 注入的内容

启用后，可能会向系统提示添加三层指导：

1. **通用工具使用强制**（所有匹配的模型）——指示模型立即进行工具调用，而不是描述意图；持续工作直到任务完成；永远不要以承诺未来行动来结束一个回合。

2. **OpenAI 执行纪律**（仅 GPT 和 Codex 模型）——针对 GPT 特定失败模式的额外指导：在部分结果上放弃工作、跳过前置查询、产生幻觉而不是使用工具、以及未验证就声明“完成”。

3. **Google 操作指导**（仅 Gemini 和 Gemma 模型）——简洁性、绝对路径、并行工具调用以及先验证后编辑的模式。

这些对用户透明，仅影响系统提示。已经可靠使用工具的模型（如 Claude）不需要这种指导，这就是为什么 `"auto"` 排除了它们。

<a id="when-to-turn-it-on"></a>
### 何时启用

如果你使用的模型不在默认的 auto 列表中，并且注意到它经常描述它*会*做什么而不是实际去做，请设置 `tool_use_enforcement: true` 或将模型子串添加到列表中：
```yaml
agent:
  tool_use_enforcement: ["gpt", "codex", "gemini", "grok", "my-custom-model"]
```

<a id="tts-configuration"></a>
## TTS 配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts"
  speed: 1.0                    # 全局语速倍率（所有提供商的回退值）
  edge:
    voice: "en-US-AriaNeural"   # 322 种语音，74 种语言
    speed: 1.0                  # 语速倍率（转换为百分比，例：1.5 → +50%）
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0                  # 语速倍率（API 限制在 0.25–4.0 之间）
    base_url: "https://api.openai.com/v1"  # 用于兼容 OpenAI 的 TTS 端点的覆盖地址
  minimax:
    speed: 1.0                  # 语音语速倍率
    # base_url: ""              # 可选：覆盖用于兼容 OpenAI 的 TTS 端点
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - 中性（默认）
  gemini:
    model: "gemini-2.5-flash-preview-tts"   # 或 gemini-2.5-pro-preview-tts
    voice: "Kore"               # 30 种预制语音：Zephyr, Puck, Kore, Enceladus 等
  xai:
    voice_id: "eve"             # xAI TTS 语音
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

此配置同时控制 `text_to_speech` 工具和语音模式下的语音回复（CLI 或消息网关中的 `/voice tts`）。

**语速回退层级：** 提供商特定语速（例如 `tts.edge.speed`）→ 全局 `tts.speed` → `1.0` 默认值。设置全局 `tts.speed` 可对所有提供商应用统一语速，或针对每个提供商单独覆盖以实现精细控制。

<a id="display-settings"></a>
## 显示设置 {#display-settings}

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # 在消息网关中启用 /verbose 斜杠命令
  platforms: {}           # 按平台覆盖显示设置（见下文）
  tool_progress_overrides: {}  # 已弃用 — 请使用 display.platforms
  interim_assistant_messages: true  # 网关：将自然的中途助手更新作为独立消息发送
  skin: default           # 内置或自定义 CLI 皮肤（参见 user-guide/features/skins）
  personality: "kawaii"  # 遗留的装饰性字段，仍会在某些摘要中显示
  compact: false          # 紧凑输出模式（减少空白）
  resume_display: full    # full（恢复时显示之前消息）| minimal（仅一行）
  bell_on_complete: false # Agent 完成时播放终端提示音（适合长任务）
  show_reasoning: false   # 在每个回复上方显示模型推理/思考过程（使用 /reasoning show|hide 切换）
  streaming: false        # 实时流式输出 token 到终端
  show_cost: false        # 在 CLI 状态栏显示预估费用（美元）
  timestamps: false       # 为 true 时，在 CLI/TUI 转录中给用户和助手标签添加 [HH:MM] 时间戳前缀
  tool_preview_length: 0  # 工具调用预览的最大字符数（0 = 不限制，显示完整路径/命令）
  runtime_footer:         # 网关：在最终回复后附加运行时上下文页脚
    enabled: false
    fields: ["model", "context_pct", "cwd"]
  file_mutation_verifier: true    # 当本轮 write_file/patch 调用失败时，附加建议性页脚
  language: en            # 静态消息的 UI 语言（审批提示、部分网关回复）。支持 en | zh | zh-hant | ja | de | es | fr | tr | uk | af | ko | it | ga | pt | ru | hu
```
<a id="file-mutation-verifier"></a>
### 文件变更校验器

当 `display.file_mutation_verifier` 设置为 `true`（默认值）时，Hermes 会在助手最终响应末尾附加一行提示，提醒你本轮对话中 `write_file` 或 `patch` 调用失败、且随后未对同一路径成功写入的情况。这能捕捉到“一批并行 patch，一半静默失败，模型却总结说全部成功”这类夸大问题，无需你每次编辑后手动运行 `git status`。

示例页脚：

```
⚠️ 文件变更校验器：本轮对话中有 3 个文件未被修改，尽管上文可能暗示已修改。请运行 `git status` 或 `read_file` 确认。
  • concepts/automatic-organization.md — [patch] 未找到匹配的 old_string
  • concepts/lora.md — [patch] 未找到匹配的 old_string
  • concepts/rag-pipeline.md — [patch] 未找到匹配的 old_string
```

将 `file_mutation_verifier: false` 或设置 `HERMES_FILE_MUTATION_VERIFIER=0` 可屏蔽该页脚。校验器仅在本轮结束时存在真实失败时才会触发——如果模型在同一轮中重试失败的 patch 并成功，则该文件不会触发。

<a id="ui-language-for-static-messages"></a>
### 静态消息的 UI 语言

`display.language` 设置可翻译一小部分静态的面向用户消息：CLI 批准提示、部分网关斜杠命令回复（例如重启-排空通知、“批准已过期”、“目标已清除”）。它 **不会** 翻译 Agent 回复、日志行、工具输出、错误回溯或斜杠命令描述——这些保持英文。如果你希望 Agent 本身用其他语言回复，只需在提示词或系统消息中告诉它即可。

支持的值：`en`（默认）、`zh`（简体中文）、`ja`（日语）、`de`（德语）、`es`（西班牙语）、`fr`（法语）、`tr`（土耳其语）、`uk`（乌克兰语）。未知值会回退到英语。

你也可以通过 `HERMES_LANGUAGE` 环境变量为每个会话单独设置，该变量会覆盖配置文件中的值。

```yaml
display:
  language: zh   # CLI 批准提示以中文显示
```

| 模式 | 你看到的内容 |
|------|-------------|
| `off` | 静默——仅最终响应 |
| `new` | 仅工具变更时显示工具指示符 |
| `all` | 每次工具调用都显示简短预览（默认） |
| `verbose` | 完整参数、结果和调试日志 |

在 CLI 中，可通过 `/verbose` 循环切换这些模式。要在消息平台（Telegram、Discord、Slack 等）中使用 `/verbose`，请在上方 `display` 部分设置 `tool_progress_command: true`。随后该命令将循环切换模式并保存到配置中。

<a id="runtime-metadata-footer-gateway-only"></a>
### 运行时元数据页脚（仅限网关）

当 `display.runtime_footer.enabled: true` 时，Hermes 会在每个网关回合的 **最终** 消息末尾附加一个运行时上下文页脚——与 CLI 状态栏显示的信息相同（模型、上下文百分比、当前工作目录、会话持续时间、令牌数、费用）。默认关闭；如果你的团队希望每条回复都包含来源信息，请在网关中按需启用。

```yaml
display:
  runtime_footer:
    enabled: true
    fields: ["model", "context_pct", "cwd"]   # 可选字段：model, context_pct, cwd, duration, tokens, cost
```
`/footer` 斜杠命令可在任何会话中运行时切换此功能。

追加到 Telegram/Discord/Slack 回复中的示例页脚：

```
— claude-opus-4.7 · 12 次工具调用 · 2分14秒 · $0.042
```

只有**最终**消息会附带页脚；中间更新保持干净。

<a id="per-platform-progress-overrides"></a>
### 按平台的进度显示覆盖

不同平台对详细程度的需求不同。例如，Signal 无法编辑消息，因此每次进度更新都会变成一条独立消息——很嘈杂。使用 `display.platforms` 设置按平台模式：

```yaml
display:
  tool_progress: all          # 全局默认
  platforms:
    signal:
      tool_progress: 'off'    # 在 Signal 上静默进度
    telegram:
      tool_progress: verbose  # 在 Telegram 上显示详细进度
    slack:
      tool_progress: 'off'    # 在共享 Slack 工作区中保持安静
```

没有覆盖设置的平台会回退到全局 `tool_progress` 值。有效的平台键：`telegram`、`discord`、`slack`、`signal`、`whatsapp`、`matrix`、`mattermost`、`email`、`sms`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot`。旧的 `display.tool_progress_overrides` 键仍会加载以保持向后兼容，但已弃用，并在首次加载时迁移到 `display.platforms` 中。

`interim_assistant_messages` 仅限 gateway 使用。启用后，Hermes 会将完成的中间回合助手更新作为单独的聊天消息发送。这与 `tool_progress` 无关，且不需要 gateway 流式传输。

<a id="privacy"></a>
## 隐私

```yaml
privacy:
  redact_pii: false  # 从 LLM 上下文中剥离 PII（仅限 gateway）
```

当 `redact_pii` 为 `true` 时，gateway 会在将系统提示发送到受支持平台上的 LLM 之前，从中剥离个人身份信息：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 上的用户 ID） | 哈希为 `user_<12-char-sha256>` |
| 用户 ID | 哈希为 `user_<12-char-sha256>` |
| 聊天 ID | 数字部分被哈希，平台前缀保留（`telegram:&lt;hash&gt;`） |
| 主频道 ID | 数字部分被哈希 |
| 用户名/用户昵称 | **不受影响**（用户自选，公开可见） |

**平台支持：** 脱敏适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 被排除，因为它们的提及系统（`<@user_id>`）需要在 LLM 上下文中使用真实 ID。

哈希是确定性的——同一用户始终映射到同一哈希，因此模型仍能在群聊中区分不同用户。路由和投递在内部使用原始值。

<a id="speech-to-text-stt"></a>
## 语音转文本 (STT)

```yaml
stt:
  provider: "local"            # "local" | "groq" | "openai" | "mistral"
  local:
    model: "base"              # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe
  # model: "whisper-1"         # 旧版回退键仍被支持
```

提供商行为：

- `local` 使用运行在您机器上的 `faster-whisper`。请使用 `pip install faster-whisper` 单独安装。
- `groq` 使用 Groq 的 Whisper 兼容端点，并读取 `GROQ_API_KEY`。
- `openai` 使用 OpenAI 语音 API，并读取 `VOICE_TOOLS_OPENAI_KEY`。
如果请求的 provider 不可用，Hermes 会自动按以下顺序回退：`local` → `groq` → `openai`。

Groq 和 OpenAI 的模型覆写由环境变量驱动：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

<a id="voice-mode-cli"></a>
## 语音模式（CLI）

```yaml
voice:
  record_key: "ctrl+b"         # CLI 内的按键通话键
  max_recording_seconds: 120    # 长时间录音的硬性停止
  auto_tts: false               # 启用 /voice 时自动开启语音回复
  beep_enabled: true            # CLI 语音模式下播放录音开始/结束提示音
  silence_threshold: 200        # 语音检测的 RMS 阈值
  silence_duration: 3.0         # 自动停止前的静音秒数
```

在 CLI 中使用 `/voice on` 启用麦克风模式，使用 `record_key` 开始/停止录音，使用 `/voice tts` 切换语音回复。完整设置及各平台差异请参考[语音模式](/user-guide/features/voice-mode)。

<a id="streaming"></a>
## 流式输出

将 token 实时流式输出到终端或消息平台，而非等待完整响应。

<a id="cli-streaming"></a>
### CLI 流式输出

```yaml
display:
  streaming: true         # 实时 stream token 到终端
  show_reasoning: true    # 同时 stream 推理/思考 token（可选）
```

启用后，响应会在一个流式盒子中逐 token 显示。工具调用仍会静默捕获。如果 provider 不支持流式输出，会自动回退到普通显示。

<a id="gateway-streaming-telegram-discord-slack"></a>
### 网关流式输出（Telegram、Discord、Slack）

```yaml
streaming:
  enabled: true           # 启用渐进式消息编辑
  transport: edit         # "edit"（渐进式消息编辑）或 "off"
  edit_interval: 0.3      # 消息编辑之间的秒数
  buffer_threshold: 40    # 强制编辑刷新的字符数
  cursor: " ▉"            # 流式输出期间显示的光标
  fresh_final_after_seconds: 60   # 当预览过期多少秒后发送全新最终消息（Telegram）；0 = 始终原地编辑
```

启用后，机器人会在收到第一个 token 时发送一条消息，然后随着更多 token 到达逐步编辑该消息。不支持消息编辑的平台（Signal、Email、Home Assistant）会在第一次尝试时自动检测到——该会话会优雅地禁用流式输出，不会产生消息洪流。

如需在无需渐进式 token 编辑的情况下进行独立的自然中场助手更新，请设置 `display.interim_assistant_messages: true`。

**溢出处理：** 如果流式文本超过平台消息长度限制（约 4096 字符），当前消息会被定稿，并自动开始一条新消息。

**全新最终消息（Telegram）：** Telegram 的 `editMessageText` 会保留原始消息的时间戳，因此长时间运行的流式回复即使在完成后也会保留第一个 token 的时间戳。当 `fresh_final_after_seconds > 0`（默认 `60`）时，完成的回复会作为一条全新消息发送（会尽力删除过时的预览），这样 Telegram 显示的可见时间戳就能反映完成时间。较短的预览仍会原地定稿。设置为 `0` 可始终原地编辑。
:::note
默认情况下，流式传输是关闭的。在 `~/.hermes/config.yaml` 中启用它，即可体验流式传输的用户界面。
:::

<a id="group-chat-session-isolation"></a>
## 群聊会话隔离

控制共享聊天是按房间还是按参与者维护独立的对话：

```yaml
group_sessions_per_user: true  # true = 在群组/频道中按用户隔离，false = 每个聊天使用一个共享会话
```

- `true` 是默认值，也是推荐设置。在 Discord 频道、Telegram 群组、Slack 频道等共享上下文中，当平台提供用户 ID 时，每个发送者将拥有自己的会话。
- `false` 则恢复为旧的共享房间行为。如果你明确希望 Hermes 将某个频道视为一个协作式对话，这种模式可能有用，但这意味着用户们会共享上下文、token 消耗和中断状态。
- 私聊不受影响。Hermes 仍然像往常一样通过聊天/DM ID 来区分私聊。
- 无论如何，子线程与父频道保持隔离；当 `true` 时，子线程内的每个参与者也会拥有自己的会话。

有关行为细节和示例，请参阅[会话](/user-guide/sessions)和[Discord 指南](/user-guide/messaging/discord)。

<a id="unauthorized-dm-behavior"></a>
## 未授权私聊行为

控制当未知用户发送私聊时 Hermes 的行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。Hermes 会拒绝访问，但会在私聊中回复一个一次性配对码。
- `ignore` 会静默丢弃未授权的私聊。
- 平台配置段会覆盖全局默认值，因此你可以让大多数平台保持配对模式，同时让某个平台更安静。

<a id="quick-commands"></a>
## 快速命令

定义自定义命令，这些命令可以不调用 LLM 直接运行 shell 命令，或者将一个斜杠命令别名到另一个。Exec 快速命令消耗零 token，在消息平台（Telegram、Discord 等）上用于快速服务器检查或实用脚本非常方便。

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
- **自动补全**——快速命令在调度时解析，不会显示在内置的斜杠命令自动补全表中
- **类型**——支持的类型是 `exec` 和 `alias`；其他类型会显示错误
- **随处可用**——CLI、Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant
纯字符串的提示快捷方式不是有效的快速命令。如需可复用的提示词工作流，请创建技能（skill）或为现有斜杠命令设置别名（alias）。

<a id="human-delay"></a>
## 人类延迟

在消息平台中模拟类人的响应节奏：

```yaml
human_delay:
  mode: "off"                  # 关闭 | 自然 | 自定义
  min_ms: 800                  # 最小延迟（自定义模式）
  max_ms: 2500                 # 最大延迟（自定义模式）
```

<a id="code-execution"></a>
## 代码执行

配置 `execute_code` 工具：

```yaml
code_execution:
  mode: project                # project（默认） | strict
  timeout: 300                 # 最大执行时间（秒）
  max_tool_calls: 50           # 代码执行中最大工具调用次数
```

**`mode`** 控制脚本的工作目录和 Python 解释器：

- **`project`**（默认）—— 脚本在会话的工作目录下运行，使用当前 virtualenv/conda 环境的 python。项目依赖（`pandas`、`torch`、项目包）和相对路径（`.env`、`./data.csv`）自然解析，与 `terminal()` 看到的结果一致。
- **`strict`** —— 脚本在临时暂存目录下运行，使用 `sys.executable`（Hermes 自身的 python）。可重现性最高，但项目依赖和相对路径无法解析。

环境清理（移除 `*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_PASSWORD`、`*_CREDENTIAL`、`*_PASSWD`、`*_AUTH`）以及工具白名单在两种模式下完全一致——切换模式不会改变安全态势。

<a id="web-search-backends"></a>
## 网页搜索后端

`web_search`、`web_extract` 和 `web_crawl` 工具支持五种后端提供商。在 `config.yaml` 或通过 `hermes tools` 配置后端：

```yaml
web:
  backend: firecrawl    # firecrawl | searxng | parallel | tavily | exa

  # 或者使用按能力键混合提供商（例如免费搜索 + 付费提取）：
  search_backend: "searxng"
  extract_backend: "firecrawl"
```

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **SearXNG** | `SEARXNG_URL` | ✔ | — | — |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |

**后端选择：** 如果未设置 `web.backend`，则会根据可用的 API 密钥自动检测后端。如果只设置了 `SEARXNG_URL`，则使用 SearXNG。如果只设置了 `EXA_API_KEY`，则使用 Exa。如果只设置了 `TAVILY_API_KEY`，则使用 Tavily。如果只设置了 `PARALLEL_API_KEY`，则使用 Parallel。否则默认使用 Firecrawl。

**SearXNG** 是一个免费、自托管、尊重隐私的元搜索引擎，可查询 70+ 个搜索引擎。无需 API 密钥——只需将 `SEARXNG_URL` 设置为你的实例（例如 `http://localhost:8080`）。SearXNG 仅支持搜索；`web_extract` 和 `web_crawl` 需要单独的提取提供商（设置 `web.extract_backend`）。有关 Docker 配置说明，请参阅[网页搜索设置指南](/user-guide/features/web-search)。

**自托管 Firecrawl：** 设置 `FIRECRAWL_API_URL` 指向你自己的实例。当设置了自定义 URL 时，API 密钥变为可选（在服务器上设置 `USE_DB_AUTHENTICATION=***` 可禁用认证）。
**并行搜索模式：** 设置 `PARALLEL_SEARCH_MODE` 以控制搜索行为 — `fast`、`one-shot` 或 `agentic`（默认值：`agentic`）。

**Exa：** 在 `~/.hermes/.env` 中设置 `EXA_API_KEY`。支持 `category` 过滤（`company`、`research paper`、`news`、`people`、`personal site`、`pdf`）以及域名/日期过滤器。

<a id="browser"></a>
## 浏览器

配置浏览器自动化行为：

```yaml
browser:
  inactivity_timeout: 120        # 空闲会话自动关闭前的等待秒数
  command_timeout: 30             # 浏览器命令（截图、导航等）的超时秒数
  record_sessions: false         # 是否自动将浏览器会话录制为 WebM 视频，保存到 ~/.hermes/browser_recordings/
  # 可选 CDP 覆盖 — 设置后，Hermes 会直接附加到你自己的 Chromium 系列浏览器上（通过 /browser connect），而不是启动无头浏览器。
  cdp_url: ""
  # 对话框主管 — 控制附加了 CDP 后端（Browserbase、通过 /browser connect 连接的本地 Chromium 系列浏览器）时如何处理原生 JS 对话框（alert / confirm / prompt）。在 Camofox 和默认的本地 agent-browser 模式下忽略。
  dialog_policy: must_respond    # must_respond | auto_dismiss | auto_accept
  dialog_timeout_s: 300          # 在 must_respond 模式下安全自动关闭的超时秒数
  camofox:
    managed_persistence: false   # 为 true 时，Camofox 会话会在重启后保持 cookie/登录状态
    user_id: ""                  # 可选的外部管理的 Camofox userId
    session_key: ""              # 可选，Hermes 创建标签页时发送的会话密钥
    adopt_existing_tab: false    # 在创建新标签页前，是否先重用该身份的现有标签页
```

**对话框策略：**

- `must_respond`（默认）— 捕获对话框，将其展示在 `browser_snapshot.pending_dialogs` 中，并等待 Agent 调用 `browser_dialog(action=...)`。如果在 `dialog_timeout_s` 秒内没有响应，则自动关闭对话框，防止页面 JS 线程无限期停滞。
- `auto_dismiss` — 捕获后立即关闭。Agent 仍然会在 `browser_snapshot.recent_dialogs` 中看到对话框记录，其中 `closed_by` 字段为 `"auto_policy"`。
- `auto_accept` — 捕获后立即接受。适用于包含激进 `beforeunload` 提示的页面。

完整的对话框工作流程请参见[浏览器功能页面](./features/browser.md#browser_dialog)。

浏览器工具集支持多个提供商。关于 Browserbase、Browser Use 以及本地 Chromium 系列 CDP 的详细设置，请参见[浏览器功能页面](/user-guide/features/browser)。

<a id="timezone"></a>
## 时区

使用 IANA 时区字符串覆盖服务器本地时区。影响日志时间戳、cron 调度以及系统提示中的时间注入。

```yaml
timezone: "America/New_York"   # IANA 时区（默认值："" = 服务器本地时间）
```

支持的值：任何 IANA 时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。留空或省略则使用服务器本地时间。

<a id="discord"></a>
## Discord

配置消息网关的 Discord 特定行为：
```yaml
discord:
  require_mention: true          # 在服务器频道中需要 @提及 才会回复
  free_response_channels: ""     # 无需 @提及 即可回复的频道 ID，用逗号分隔
  auto_thread: true              # 在频道中被 @提及 时自动创建子线程
```

- `require_mention` — 当设为 `true`（默认值）时，机器人仅在服务器频道中被 `@BotName` 提及时才回复。私信始终无需提及即可工作。
- `free_response_channels` — 用逗号分隔的频道 ID 列表，在这些频道中机器人会回复每条消息，无需提及。
- `auto_thread` — 当设为 `true`（默认值）时，在频道中被提及会自动为对话创建子线程，保持频道整洁（类似于 Slack 的线程功能）。

<a id="security"></a>
## 安全

执行前的安全扫描和机密信息编辑：

```yaml
security:
  redact_secrets: false          # 在工具输出和日志中编辑 API 密钥模式（默认关闭）
  tirith_enabled: true           # 为终端命令启用 Tirith 安全扫描
  tirith_path: "tirith"          # tirith 二进制文件的路径（默认：$PATH 中的 "tirith"）
  tirith_timeout: 5              # 等待 tirith 扫描的超时秒数
  tirith_fail_open: true         # 如果 tirith 不可用，允许执行命令
  website_blocklist:             # 参见下方网站黑名单部分
    enabled: false
    domains: []
    shared_files: []
```

- `redact_secrets` — 当设为 `true` 时，在工具输出进入对话上下文和日志之前，自动检测并编辑看起来像 API 密钥、令牌和密码的模式。**默认关闭** — 如果你经常在工具输出中使用真实凭据并希望增加一层安全保障，请启用。显式设为 `true` 以开启。
- `tirith_enabled` — 当设为 `true` 时，终端命令在执行前会由 [Tirith](https://github.com/sheeki03/tirith) 扫描，以检测潜在的危险操作。
- `tirith_path` — tirith 二进制文件的路径。如果 tirith 安装在非标准位置，请设置此项。
- `tirith_timeout` — 等待 tirith 扫描的最大秒数。如果扫描超时，命令将继续执行。
- `tirith_fail_open` — 当设为 `true`（默认值）时，如果 tirith 不可用或失败，命令允许执行。设为 `false` 可在 tirith 无法验证时阻止命令执行。

<a id="website-blocklist"></a>
## 网站黑名单 {#website-blocklist}

阻止 Agent 的网页和浏览器工具访问特定域名：

```yaml
security:
  website_blocklist:
    enabled: false               # 启用 URL 阻止（默认：false）
    domains:                     # 被阻止的域名模式列表
      - "*.internal.company.com"
      - "admin.example.com"
      - "*.local"
    shared_files:                # 从外部文件加载额外规则
      - "/etc/hermes/blocked-sites.txt"
```

启用后，任何匹配被阻止域名模式的 URL 都会在网页或浏览器工具执行前被拒绝。这适用于 `web_search`、`web_extract`、`browser_navigate` 以及任何访问 URL 的工具。

域名规则支持：
- 精确域名：`admin.example.com`
- 通配符子域名：`*.internal.company.com`（阻止所有子域名）
- TLD 通配符：`*.local`
共享文件每行包含一条域名规则（空行和以 `#` 开头的注释会被忽略）。缺失或不可读的文件会记录警告，但不会禁用其他网络工具。

策略缓存30秒，因此配置更改无需重启即可快速生效。

<a id="smart-approvals"></a>
## 智能审批

控制 Hermes 如何处理潜在危险命令：

```yaml
approvals:
  mode: manual   # manual | smart | off
```

| 模式 | 行为 |
|------|----------|
| `manual`（默认） | 在执行任何被标记的命令前提示用户。在 CLI 中，显示交互式审批对话框。在消息中，将待审批请求加入队列。 |
| `smart` | 使用辅助 LLM 评估标记的命令是否确实危险。低风险命令会自动批准并具有会话级持久性。真正危险的命令会升级给用户。 |
| `off` | 跳过所有审批检查。等同于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

智能模式特别有助于减少审批疲劳——它让 Agent 在安全操作上更自主地工作，同时仍能捕获真正具有破坏性的命令。

:::warning
设置 `approvals.mode: off` 会禁用终端命令的所有安全检查。仅在受信任的沙盒环境中使用。
:::

<a id="checkpoints"></a>
## 检查点

在执行破坏性文件操作前自动进行文件系统快照。详见[检查点与回滚](/user-guide/checkpoints-and-rollback)。

```yaml
checkpoints:
  enabled: false                 # Enable automatic checkpoints (also: hermes chat --checkpoints). Default: false (opt-in).
  max_snapshots: 20              # Max checkpoints to keep per directory (default: 20)
```

<a id="delegation"></a>
## 委派

配置子 Agent 的委托工具行为：

```yaml
delegation:
  # model: "google/gemini-3-flash-preview"  # Override model (empty = inherit parent)
  # provider: "openrouter"                  # Override provider (empty = inherit parent)
  # base_url: "http://localhost:1234/v1"    # Direct OpenAI-compatible endpoint (takes precedence over provider)
  # api_key: "local-key"                    # API key for base_url (falls back to OPENAI_API_KEY)
  # api_mode: ""                            # Wire protocol for base_url: "chat_completions", "codex_responses", or "anthropic_messages". Empty = auto-detect from URL (e.g. /anthropic suffix → anthropic_messages). Set explicitly for non-standard endpoints the heuristic can't detect.
  max_concurrent_children: 3                # Parallel children per batch (floor 1, no ceiling). Also via DELEGATION_MAX_CONCURRENT_CHILDREN env var.
  max_spawn_depth: 1                        # Delegation tree depth cap (1-3, clamped). 1 = flat (default): parent spawns leaves that cannot delegate. 2 = orchestrator children can spawn leaf grandchildren. 3 = three levels.
  orchestrator_enabled: true                # Global kill switch. When false, role="orchestrator" is ignored and every child is forced to leaf regardless of max_spawn_depth.
```

**子 Agent 的 provider:model 覆盖：** 默认情况下，子 Agent 继承父 Agent 的 provider 和 model。设置 `delegation.provider` 和 `delegation.model` 可将子 Agent 路由到不同的 provider:model 对——例如，为范围狭窄的子任务使用廉价/快速模型，而您的主 Agent 运行昂贵的推理模型。
**直接端点覆盖：** 如果你想要明确的自定义端点路径，请设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这将子 Agent 直接发送到该兼容 OpenAI 的端点，并优先于 `delegation.provider`。如果省略了 `delegation.api_key`，Hermes 仅回退到 `OPENAI_API_KEY`。

**传输协议（`api_mode`）：** Hermes 会根据 `delegation.base_url` 自动检测传输协议（例如，以 `/anthropic` 结尾的路径 → `anthropic_messages`；Codex / 原生 Anthropic / Kimi-coding 主机名保持其现有检测）。对于启发式方法无法分类的端点——例如 Azure AI Foundry、MiniMax、智谱 GLM 或前端使用 Anthropic 风格后端的 LiteLLM 代理——请将 `delegation.api_mode` 显式设置为 `chat_completions`、`codex_responses` 或 `anthropic_messages` 之一。将其留空（默认值）以保持自动检测。

委托提供者使用与 CLI/网关启动相同的凭证解析方式。所有配置的提供者都受支持：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。当设置了提供者时，系统会自动解析正确的 base URL、API key 和 API 模式——无需手动配置凭证。

**优先级：** 配置文件中的 `delegation.base_url` → 配置文件中的 `delegation.provider` → 父提供者（继承）。配置文件中的 `delegation.model` → 父模型（继承）。仅设置 `model` 而不设置 `provider` 只会更改模型名称，同时保留父级的凭证（对于在同一提供者内切换模型很有用，例如 OpenRouter）。

**宽度与深度：** `max_concurrent_children` 限制每批并行运行的子 Agent 数量（默认 `3`，最低为 1，无上限）。也可以通过 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量设置。当模型提交的 `tasks` 数组长度超过上限时，`delegate_task` 会返回一个工具错误，解释该限制，而不是静默截断。`max_spawn_depth` 控制委托树的深度（限制在 1-3）。默认值 `1` 时，委托是扁平的：子 Agent 无法生成孙 Agent，并且传递 `role="orchestrator"` 会静默降级为 `leaf`。将其提高到 `2`，以使 orchestrator 子 Agent 可以生成叶子孙 Agent；`3` 用于三级树。Agent 通过每次调用中的 `role="orchestrator"` 选择加入编排；`orchestrator_enabled: false` 会强制所有子 Agent 恢复为叶子节点。代价是乘法增长的——在 `max_spawn_depth: 3` 和 `max_concurrent_children: 3` 的情况下，树可以达到 3×3×3 = 27 个并发叶子 Agent。请参阅 [子 Agent 委托 → 深度限制与嵌套编排](features/delegation.md#depth-limit-and-nested-orchestration) 了解使用模式。

<a id="clarify"></a>
## Clarify

配置澄清提示的行为：

```yaml
clarify:
  timeout: 120                 # 等待用户澄清回复的秒数
```

<a id="context-files-soul-md-agents-md"></a>
## 上下文文件 (SOUL.md, AGENTS.md)

Hermes 使用两个不同的上下文范围：

| 文件 | 用途 | 范围 |
|------|---------|-------|
| `SOUL.md` | **主要 Agent 身份** — 定义 Agent 是谁（系统提示中的第 1 位） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定指令（最高优先级） | 向上查找到 git 根目录 |
| `AGENTS.md` | 项目特定指令、编码规范 | 递归目录遍历 |
| `CLAUDE.md` | Claude Code 上下文文件（也会被检测） | 仅限工作目录 |
| `.cursorrules` | Cursor IDE 规则（也会被检测） | 仅限工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被检测） | 仅限工作目录 |
- **SOUL.md** 是 Agent 的主要身份文件。它占据系统提示中的 1 号插槽，完全取代内置的默认身份。编辑此文件即可全面自定义 Agent 的身份。
- 如果 SOUL.md 缺失、为空或无法加载，Hermes 会回退到内置的默认身份。
- **项目上下文文件采用优先级系统**——仅加载一种类型（优先匹配第一个）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。SOUL.md 始终独立加载。
- **AGENTS.md** 具有层级结构：如果子目录也包含 AGENTS.md，则所有内容会合并。
- 如果 SOUL.md 尚不存在，Hermes 会自动生成一个默认的 SOUL.md。
- 所有加载的上下文文件限制为 20,000 个字符，并会智能截断。

另请参阅：
- [个性与 SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)

<a id="working-directory"></a>
## 工作目录

| 上下文 | 默认值 |
|---------|--------|
| **CLI (`hermes`)** | 运行命令的当前目录 |
| **消息网关** | 主目录 `~`（可通过 `MESSAGING_CWD` 覆盖） |
| **Docker / Singularity / Modal / SSH** | 容器或远程机器内的用户主目录 |

覆盖工作目录：
```bash
# 在 ~/.hermes/.env 或 ~/.hermes/config.yaml 中：
MESSAGING_CWD=/home/myuser/projects    # 网关会话
TERMINAL_CWD=/workspace                # 所有终端会话
```
