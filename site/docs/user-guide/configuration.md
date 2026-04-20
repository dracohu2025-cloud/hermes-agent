---
sidebar_position: 2
title: "配置"
description: "配置 Hermes Agent — config.yaml、提供方、模型、API 密钥等"
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
├── auth.json       # OAuth 提供方凭据（Nous Portal 等）
├── SOUL.md         # 主要 Agent 身份（系统提示中的槽位 #1）
├── memories/       # 持久化记忆（MEMORY.md, USER.md）
├── skills/         # Agent 创建的技能（通过 skill_manage 工具管理）
├── cron/           # 计划任务
├── sessions/       # Gateway 会话
└── logs/           # 日志（errors.log, gateway.log — 机密信息自动脱敏）
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
`hermes config set` 命令会自动将值路由到正确的文件 — API 密钥保存到 `.env`，其他所有内容保存到 `config.yaml`。
:::

<a id="configuration-precedence"></a>
## 配置优先级

设置按以下顺序解析（优先级从高到低）：

1.  **CLI 参数** — 例如 `hermes chat --model anthropic/claude-sonnet-4`（每次调用时覆盖）
2.  **`~/.hermes/config.yaml`** — 所有非机密设置的主要配置文件
3.  **`~/.hermes/.env`** — 环境变量的后备来源；**必须**用于机密信息（API 密钥、令牌、密码）
4.  **内置默认值** — 当没有其他设置时，硬编码的安全默认值

<a id="rule-of-thumb"></a>
:::info 经验法则
机密信息（API 密钥、机器人令牌、密码）放在 `.env` 中。其他所有内容（模型、终端后端、压缩设置、内存限制、工具集）放在 `config.yaml` 中。当两者都设置时，对于非机密设置，`config.yaml` 优先。
:::
<a id="environment-variable-substitution"></a>
## 环境变量替换

你可以在 `config.yaml` 中使用 `${VAR_NAME}` 语法来引用环境变量：

```yaml
auxiliary:
  vision:
    api_key: ${GOOGLE_API_KEY}
    base_url: ${CUSTOM_VISION_URL}

delegation:
  api_key: ${DELEGATION_KEY}
```

单个值中支持多个引用：`url: "${HOST}:${PORT}"`。如果引用的变量未设置，占位符将保持原样（`${UNDEFINED_VAR}` 保持不变）。仅支持 `${VAR}` 语法 —— 裸写的 `$VAR` 不会被展开。

关于 AI 服务提供商设置（OpenRouter、Anthropic、Copilot、自定义端点、自托管 LLM、备用模型等），请参阅 [AI 提供商](/integrations/providers)。

<a id="terminal-backend-configuration"></a>
## 终端后端配置

Hermes 支持六种终端后端。每种后端决定了 Agent 的 shell 命令实际在哪里执行 —— 你的本地机器、Docker 容器、通过 SSH 连接的远程服务器、Modal 云沙箱、Daytona 工作区，或是 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | singularity
  cwd: "."          # 工作目录（"." 对于 local 后端是当前目录，对于容器是 "/root"）
  timeout: 180      # 每条命令的超时时间（秒）
  env_passthrough: []  # 要传递到沙箱化执行环境（terminal + execute_code）的环境变量名
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Singularity 后端的容器镜像
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Modal 后端的容器镜像
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Daytona 后端的容器镜像
```

对于 Modal 和 Daytona 这类云沙箱，`container_persistent: true` 意味着 Hermes 会尝试在沙箱重建时保留文件系统状态。但这并不保证同一个活动的沙箱、PID 空间或后台进程在之后仍然运行。

<a id="backend-overview"></a>
### 后端概览

| 后端 | 命令运行位置 | 隔离性 | 最佳适用场景 |
|---------|-------------------|-----------|----------|
| **local** | 直接在你的机器上 | 无 | 开发、个人使用 |
| **docker** | Docker 容器 | 完全（命名空间、cap-drop） | 安全沙箱、CI/CD |
| **ssh** | 通过 SSH 连接的远程服务器 | 网络边界 | 远程开发、强大硬件 |
| **modal** | Modal 云沙箱 | 完全（云虚拟机） | 临时云计算、评估 |
| **daytona** | Daytona 工作区 | 完全（云容器） | 托管的云开发环境 |
| **singularity** | Singularity/Apptainer 容器 | 命名空间（--containall） | HPC 集群、共享机器 |
<a id="local-backend"></a>
### 本地后端

默认选项。命令直接在您的机器上运行，没有隔离。无需特殊设置。

```yaml
terminal:
  backend: local
```

:::warning
Agent 拥有与您的用户账户相同的文件系统访问权限。使用 `hermes tools` 来禁用您不需要的工具，或者切换到 Docker 后端以实现沙箱隔离。
:::

<a id="docker-backend"></a>
### Docker 后端

在 Docker 容器内运行命令，并进行了安全加固（所有能力被丢弃，无权限提升，PID 限制）。

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # 将启动目录挂载到 /workspace
  docker_forward_env:              # 要转发到容器内的环境变量
    - "GITHUB_TOKEN"
  docker_volumes:                  # 主机目录挂载
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"   # :ro 表示只读

  # 资源限制
  container_cpu: 1                 # CPU 核心数 (0 = 无限制)
  container_memory: 5120           # MB (0 = 无限制)
  container_disk: 51200            # MB (需要在 XFS+pquota 上启用 overlay2)
  container_persistent: true       # 在会话间持久化 /workspace 和 /root
```

**要求：** 已安装并运行 Docker Desktop 或 Docker Engine。Hermes 会探测 `$PATH` 以及常见的 macOS 安装位置（`/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用程序包）。

**容器生命周期：** 每个会话会启动一个长期运行的容器（`docker run -d ... sleep 2h`）。命令通过 `docker exec` 使用登录 shell 运行。在清理时，容器会被停止并移除。

**安全加固：**
- `--cap-drop ALL`，仅重新添加了 `DAC_OVERRIDE`、`CHOWN`、`FOWNER`
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- 为 `/tmp` (512MB)、`/var/tmp` (256MB)、`/run` (64MB) 设置了大小限制的 tmpfs

**凭证转发：** `docker_forward_env` 中列出的环境变量首先从您的 shell 环境解析，然后从 `~/.hermes/.env` 解析。技能也可以声明 `required_environment_variables`，这些变量会自动合并。
<a id="ssh-backend"></a>
### SSH 后端

通过 SSH 在远程服务器上执行命令。使用 ControlMaster 实现连接复用（5分钟空闲保活）。默认启用持久化 shell——状态（当前工作目录、环境变量）在多个命令之间保持不变。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # 保持一个长期存在的 bash 会话（默认：true）
```

**必需的环境变量：**

```bash
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=ubuntu
```

**可选：**

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `TERMINAL_SSH_PORT` | `22` | SSH 端口 |
| `TERMINAL_SSH_KEY` | （系统默认） | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | `true` | 启用持久化 shell |

**工作原理：** 初始化时以 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 参数连接。持久化 shell 会在远程主机上保持一个 `bash -l` 进程存活，通过临时文件进行通信。需要 `stdin_data` 或使用 `sudo` 的命令会自动回退到一次性模式。

<a id="modal-backend"></a>
### Modal 后端

在 [Modal](https://modal.com) 云端沙箱中执行命令。每个任务会获得一个独立的虚拟机，可配置 CPU、内存和磁盘。文件系统可以在会话之间进行快照/恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB (5GB)
  container_disk: 51200            # MB (50GB)
  container_persistent: true       # 快照/恢复文件系统
```

**必需条件：** 环境变量 `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET`，或配置文件 `~/.modal.toml`。

**持久性：** 启用后，沙箱文件系统会在清理时进行快照，并在下次会话时恢复。快照记录在 `~/.hermes/modal_snapshots.json` 中。这保留了文件系统状态，而不是活跃进程、PID 空间或后台作业。

**凭证文件：** 自动从 `~/.hermes/` 目录（OAuth 令牌等）挂载并在每次命令前同步。

<a id="daytona-backend"></a>
### Daytona 后端

在 [Daytona](https://daytona.io) 管理的工作空间中执行命令。支持停止/恢复以实现持久性。
```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB → 转换为 GiB
  container_disk: 10240            # MB → 转换为 GiB (最大 10 GiB)
  container_persistent: true       # 停止/恢复而非删除
```

**必需：** `DAYTONA_API_KEY` 环境变量。

**持久化：** 启用后，清理时沙盒会被停止（而非删除），并在下次会话时恢复。沙盒名称遵循 `hermes-{task_id}` 模式。

**磁盘限制：** Daytona 强制最大 10 GiB。超过此限制的请求会被截断并发出警告。

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

**要求：** `$PATH` 中存在 `apptainer` 或 `singularity` 二进制文件。

**镜像处理：** Docker URL (`docker://...`) 会自动转换为 SIF 文件并缓存。现有的 `.sif` 文件会直接使用。

**临时目录：** 按以下顺序解析：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent` (HPC 惯例) → `~/.hermes/sandboxes/singularity`。

**隔离：** 使用 `--containall --no-home` 实现完全的命名空间隔离，不挂载宿主机家目录。

<a id="common-terminal-backend-issues"></a>
### 常见终端后端问题

如果终端命令立即失败或报告终端工具被禁用：

- **Local** — 无特殊要求。入门时最安全的默认选项。
- **Docker** — 运行 `docker version` 验证 Docker 是否正常工作。如果失败，请修复 Docker 或执行 `hermes config set terminal.backend local`。
- **SSH** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER`。如果缺少任一，Hermes 会记录明确的错误信息。
- **Modal** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml`。运行 `hermes doctor` 进行检查。
- **Daytona** — 需要 `DAYTONA_API_KEY`。Daytona SDK 处理服务器 URL 配置。
- **Singularity** — 需要 `$PATH` 中存在 `apptainer` 或 `singularity`。在 HPC 集群上常见。
不确定时，请将 `terminal.backend` 设回 `local`，并验证命令能否首先在那里运行。

<a id="docker-volume-mounts"></a>
### Docker 卷挂载

使用 Docker 后端时，`docker_volumes` 允许你将主机目录与容器共享。每个条目都使用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # 读写（默认）
    - "/home/user/datasets:/data:ro"              # 只读
    - "/home/user/.hermes/cache/documents:/output" # 网关可见的导出目录
```

这在以下场景中很有用：
- **向 Agent 提供文件**（数据集、配置文件、参考代码）
- **接收 Agent 生成的文件**（生成的代码、报告、导出文件）
- **共享工作区**，让你和 Agent 都能访问相同的文件

如果你使用消息网关，并希望 Agent 通过 `MEDIA:/...` 发送生成的文件，建议使用一个专用的、主机可见的导出挂载点，例如 `/home/user/.hermes/cache/documents:/output`。

- 在 Docker 内部将文件写入 `/output/...`
- 在 `MEDIA:` 中发出**主机路径**，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`
- **不要**发出 `/workspace/...` 或 `/output/...`，除非该确切路径也存在于主机上的网关进程中

:::warning
YAML 中的重复键会静默覆盖较早的键。如果你已经有一个 `docker_volumes:` 块，请将新的挂载项合并到同一个列表中，而不是在文件后面再添加另一个 `docker_volumes:` 键。
:::

也可以通过环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组）。

<a id="docker-credential-forwarding"></a>
### Docker 凭证转发

默认情况下，Docker 终端会话不会继承主机的任意凭证。如果你需要在容器内使用特定的令牌，请将其添加到 `terminal.docker_forward_env`。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 会首先从你当前的 shell 解析每个列出的变量，如果变量已通过 `hermes config set` 保存，则会回退到 `~/.hermes/.env` 文件。
:::warning
`docker_forward_env` 中列出的任何内容都会对容器内运行的命令可见。只转发你愿意暴露给终端会话的凭据。
:::

<a id="optional-mount-the-launch-directory-into-workspace"></a>
### 可选：将启动目录挂载到 `/workspace`

Docker 沙盒默认保持隔离。除非你明确选择启用，否则 Hermes **不会**将当前主机工作目录传入容器。

在 `config.yaml` 中启用：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用后：
- 如果你从 `~/projects/my-app` 启动 Hermes，该主机目录将被绑定挂载到 `/workspace`
- Docker 后端将在 `/workspace` 中启动
- 文件工具和终端命令都能看到同一个已挂载的项目

禁用时，除非你通过 `docker_volumes` 显式挂载内容，否则 `/workspace` 将保持为沙盒自有目录。

安全权衡：
- `false` 保持沙盒边界
- `true` 让沙盒能直接访问你启动 Hermes 的目录

仅当你确实希望容器处理主机上的实时文件时，才选择启用此选项。

<a id="persistent-shell"></a>
### 持久化 Shell

默认情况下，每个终端命令都在其自己的子进程中运行——工作目录、环境变量和 shell 变量在命令之间会重置。当启用**持久化 shell** 时，会在多个 `execute()` 调用之间保持一个长期存活的 bash 进程，以便状态在命令之间得以保留。

这对于 **SSH 后端** 最为有用，因为它还能消除每次命令的连接开销。持久化 shell **默认对 SSH 启用**，对本地后端禁用。

```yaml
terminal:
  persistent_shell: true   # 默认值 — 为 SSH 启用持久化 shell
```

要禁用它：

```bash
hermes config set terminal.persistent_shell false
```

**在命令之间保持的内容：**
- 工作目录（`cd /tmp` 对下一条命令持续有效）
- 导出的环境变量（`export FOO=bar`）
- Shell 变量（`MY_VAR=hello`）

**优先级：**

| 层级 | 变量 | 默认值 |
|-------|----------|---------|
| 配置 | `terminal.persistent_shell` | `true` |
| SSH 覆盖 | `TERMINAL_SSH_PERSISTENT` | 遵循配置 |
| 本地覆盖 | `TERMINAL_LOCAL_PERSISTENT` | `false` |
每个后端的专属环境变量具有最高优先级。如果你想在本地后端也启用持久化 shell：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
需要 `stdin_data` 或 sudo 权限的命令会自动回退到一次性模式，因为持久化 shell 的标准输入已被 IPC 协议占用。
:::

关于每个后端的详细信息，请参阅[代码执行](features/code-execution.md)和 README 中的[终端部分](features/tools.md)。

<a id="skill-settings"></a>
## 技能设置 {#skill-settings}

技能可以通过其 SKILL.md 文件的 frontmatter 声明自己的配置设置。这些是非敏感值（路径、偏好、域名设置），存储在 `config.yaml` 文件的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    myplugin:
      path: ~/myplugin-data   # 示例 — 每个技能定义自己的键
```

**技能设置如何工作：**

- `hermes config migrate` 会扫描所有已启用的技能，查找未配置的设置，并提示你进行配置
- `hermes config show` 会在“技能设置”下显示所有技能设置及其所属的技能
- 当技能加载时，其解析后的配置值会自动注入到技能上下文中

**手动设置值：**

```bash
hermes config set skills.config.myplugin.path ~/myplugin-data
```

关于在你自己的技能中声明配置设置的详细信息，请参阅[创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

<a id="memory-configuration"></a>
## 记忆配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # 约 800 个 token
  user_char_limit: 1375     # 约 500 个 token
```

<a id="file-read-safety"></a>
## 文件读取安全

控制单次 `read_file` 调用可以返回多少内容。超过限制的读取操作会被拒绝，并返回一个错误，提示 Agent 使用 `offset` 和 `limit` 来读取更小的范围。这可以防止单次读取压缩的 JS 包或大型数据文件时淹没上下文窗口。

```yaml
file_read_max_chars: 100000  # 默认值 — 约 25-35K 个 token
```
如果你使用的模型上下文窗口很大，并且经常读取大文件，可以提高这个值。对于小上下文模型，则降低它以保持读取效率：

```yaml
# 大上下文模型 (200K+)
file_read_max_chars: 200000

# 小型本地模型 (16K 上下文)
file_read_max_chars: 30000
```

Agent 还会自动对文件读取进行去重——如果同一个文件区域被读取了两次，并且文件没有变化，则会返回一个轻量级的存根，而不是重新发送内容。这在上下文压缩后会重置，以便 Agent 在文件内容被摘要化后可以重新读取文件。

<a id="git-worktree-isolation"></a>
## Git Worktree 隔离

启用隔离的 git worktree，以便在同一仓库上并行运行多个 Agent：

```yaml
worktree: true    # 始终创建一个 worktree (与 hermes -w 相同)
# worktree: false # 默认值 — 仅在传递 -w 标志时创建
```

启用后，每个 CLI 会话都会在 `.worktrees/` 下创建一个带有自己分支的新 worktree。Agent 可以编辑文件、提交、推送和创建 PR，而不会相互干扰。干净的 worktree 会在退出时被移除；有未提交更改的 worktree 会被保留以供手动恢复。

你也可以通过在仓库根目录创建 `.worktreeinclude` 文件，列出要复制到 worktree 中的 git 忽略文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

<a id="context-compression"></a>
## 上下文压缩 {#context-compression}

Hermes 会自动压缩长对话，以保持在你的模型上下文窗口限制内。压缩摘要器是一个独立的 LLM 调用——你可以将其指向任何提供商或端点。

所有压缩设置都位于 `config.yaml` 中（没有环境变量）。

<a id="full-reference"></a>
### 完整参考

```yaml
compression:
  enabled: true                                     # 启用/禁用压缩
  threshold: 0.50                                   # 在达到上下文限制的此百分比时触发压缩
  target_ratio: 0.20                                # 作为最近尾部保留的阈值比例
  protect_last_n: 20                                # 保持未压缩的最小最近消息数

# 摘要模型/提供商在 auxiliary 下配置：
auxiliary:
  compression:
    model: "google/gemini-3-flash-preview"          # 用于摘要的模型
    provider: "auto"                                # 提供商："auto", "openrouter", "nous", "codex", "main" 等
    base_url: null                                  # 自定义的 OpenAI 兼容端点 (覆盖 provider)
```
:::info 旧配置迁移
旧配置中的 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 会在首次加载时（配置版本 17）自动迁移到 `auxiliary.compression.*`。无需手动操作。
:::
<a id="legacy-config-migration"></a>

<a id="common-setups"></a>
### 常见设置

**默认（自动检测） — 无需配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
使用第一个可用的提供商（OpenRouter → Nous → Codex）和 Gemini Flash 模型。

**强制使用特定提供商**（基于 OAuth 或 API 密钥）：
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

<a id="how-the-three-knobs-interact"></a>
### 三个配置项如何交互

| `auxiliary.compression.provider` | `auxiliary.compression.base_url` | 结果 |
|---------------------|---------------------|--------|
| `auto` (默认) | 未设置 | 自动检测最佳可用提供商 |
| `nous` / `openrouter` / 等 | 未设置 | 强制使用该提供商，并使用其认证方式 |
| 任意值 | 已设置 | 直接使用自定义端点（忽略提供商） |

:::warning 摘要模型上下文长度要求
<a id="summary-model-context-length-requirement"></a>
摘要模型的上下文窗口**必须**至少与你的主 Agent 模型一样大。压缩器会将对话的完整中间部分发送给摘要模型——如果该模型的上下文窗口小于主模型，摘要调用将因上下文长度错误而失败。发生这种情况时，中间轮次的对话会**被丢弃且不生成摘要**，从而静默地丢失对话上下文。如果你覆盖了模型，请确认其上下文长度满足或超过主模型的要求。
:::

<a id="context-engine"></a>
## 上下文引擎

上下文引擎控制在接近模型令牌限制时如何管理对话。内置的 `compressor` 引擎使用有损摘要（参见[上下文压缩](/developer-guide/context-compression-and-caching)）。插件引擎可以用其他策略来替换它。
```yaml
context:
  engine: "compressor"    # 默认值 — 内置有损摘要引擎
```

要使用插件引擎（例如，用于无损上下文管理的 LCM）：

```yaml
context:
  engine: "lcm"          # 必须与插件名称匹配
```

插件引擎**永远不会自动激活**——你必须明确地将 `context.engine` 设置为插件名称。可用的引擎可以通过 `hermes plugins` → Provider Plugins → Context Engine 来浏览和选择。

关于内存插件的类似单选系统，请参阅 [Memory Providers](/user-guide/features/memory-providers)。

<a id="iteration-budget-pressure"></a>
## 迭代预算压力

当 Agent 处理涉及大量工具调用的复杂任务时，可能会在不知不觉中快速消耗其迭代预算（默认值：90 轮）。预算压力会在接近限制时自动警告模型：

| 阈值 | 级别 | 模型看到的内容 |
|-----------|-------|---------------------|
| **70%** | 注意 | `[BUDGET: 63/90. 27 iterations left. Start consolidating.]` |
| **90%** | 警告 | `[BUDGET WARNING: 81/90. Only 9 left. Respond NOW.]` |

警告会被注入到最后一个工具结果的 JSON 中（作为一个 `_budget_warning` 字段），而不是作为单独的消息——这可以保持提示缓存，并且不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # 每次对话轮次的最大迭代次数（默认值：90）
```

预算压力默认启用。Agent 会自然地看到作为工具结果一部分的警告，从而鼓励它在迭代次数用完之前整合工作并给出响应。

当迭代预算完全耗尽时，CLI 会向用户显示通知：`⚠ Iteration budget reached (90/90) — response may be incomplete`。如果预算在活动工作中耗尽，Agent 会在停止前生成已完成工作的摘要。

<a id="streaming-timeouts"></a>
### 流式传输超时

LLM 流式传输连接有两层超时。两者都会针对本地提供者（localhost，局域网 IP）自动调整——大多数设置无需配置。
| 超时设置 | 默认值 | 本地提供商 | 环境变量 |
|---------|---------|----------------|---------|
| Socket 读取超时 | 120s | 自动提升至 1800s | `HERMES_STREAM_READ_TIMEOUT` |
| 陈旧流检测 | 180s | 自动禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| API 调用（非流式） | 1800s | 保持不变 | `HERMES_API_TIMEOUT` |

**Socket 读取超时** 控制 httpx 等待从提供商获取下一个数据块的时间。本地 LLM 在处理大上下文时，可能在生成第一个 token 前需要数分钟进行预填充，因此当 Hermes 检测到本地端点时，会将此超时提升至 30 分钟。如果你显式设置了 `HERMES_STREAM_READ_TIMEOUT`，则无论端点检测结果如何，都将始终使用该值。

**陈旧流检测** 会终止那些接收到 SSE 保活 ping 但没有实际内容的连接。对于本地提供商，此功能会被完全禁用，因为它们在预填充期间不会发送保活 ping。

<a id="context-pressure-warnings"></a>
## 上下文压力警告

与迭代预算压力不同，上下文压力跟踪的是对话距离**压缩阈值**有多近——即触发上下文压缩以总结旧消息的临界点。这有助于你和 Agent 了解对话何时变得过长。

| 进度 | 级别 | 发生的情况 |
|----------|-------|-------------|
| 距离阈值 **≥ 60%** | 信息 | CLI 显示青色进度条；网关发送信息性通知 |
| 距离阈值 **≥ 85%** | 警告 | CLI 显示加粗的黄色进度条；网关警告压缩即将发生 |

在 CLI 中，上下文压力以工具输出流中的进度条形式显示：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台上，会发送纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果自动压缩被禁用，警告会提示你上下文可能会被截断。

上下文压力是自动触发的——无需配置。它纯粹作为一个面向用户的通知，不会修改消息流，也不会向模型的上下文中注入任何内容。
<a id="credential-pool-strategies"></a>
## 凭证池策略 {#credential-pool-strategies}

当您为同一服务商拥有多个 API 密钥或 OAuth 令牌时，可以配置轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # 均匀轮换使用密钥
  anthropic: least_used      # 总是选择使用次数最少的密钥
```

可选策略：`fill_first`（默认）、`round_robin`、`least_used`、`random`。完整文档请参阅[凭证池](/user-guide/features/credential-pools)。

<a id="auxiliary-models"></a>
## 辅助模型 {#auxiliary-models}

Hermes 使用轻量级的“辅助”模型来处理图像分析、网页摘要和浏览器截图分析等次要任务。默认情况下，这些任务通过自动检测使用 **Gemini Flash** —— 您无需进行任何配置。

<a id="the-universal-config-pattern"></a>
### 通用配置模式

Hermes 中的每个模型槽位 —— 辅助任务、压缩、后备模型 —— 都使用相同的三个配置项：

| 键名 | 作用 | 默认值 |
|-----|-------------|---------|
| `provider` | 用于认证和路由的服务商 | `"auto"` |
| `model` | 请求使用的模型 | 服务商的默认模型 |
| `base_url` | 自定义的 OpenAI 兼容端点（会覆盖 provider） | 未设置 |

当设置了 `base_url` 时，Hermes 会忽略 provider 并直接调用该端点（使用 `api_key` 或 `OPENAI_API_KEY` 进行认证）。当只设置了 `provider` 时，Hermes 会使用该服务商内置的认证和基础 URL。

辅助任务可用的服务商：`auto`、`main`，以及[服务商注册表](/reference/environment-variables)中的任何服务商 —— `openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`deepseek`、`nvidia`、`xai`、`ollama-cloud`、`alibaba`、`bedrock`、`huggingface`、`arcee`、`xiaomi`、`kilocode`、`opencode-zen`、`opencode-go`、`ai-gateway` —— 或者您 `custom_providers` 列表中的任何命名自定义服务商（例如 `provider: "beans"`）。

<a id="main-is-for-auxiliary-tasks-only"></a>
:::warning `"main"` 仅用于辅助任务
`"main"` 这个 provider 选项意味着“使用我的主 Agent 所用的服务商”——它仅在 `auxiliary:`、`compression:` 和 `fallback_model:` 配置内部有效。它**不是**顶层 `model.provider` 设置的有效值。如果您使用自定义的 OpenAI 兼容端点，请在您的 `model:` 部分设置 `provider: custom`。所有主模型服务商选项请参阅[AI 服务商](/integrations/providers)。
:::
<a id="full-auxiliary-config-reference"></a>
### 完整的辅助配置参考

```yaml
auxiliary:
  # 图像分析 (vision_analyze 工具 + 浏览器截图)
  vision:
    provider: "auto"           # "auto", "openrouter", "nous", "codex", "main" 等
    model: ""                  # 例如 "openai/gpt-4o", "google/gemini-2.5-flash"
    base_url: ""               # 自定义 OpenAI 兼容的端点 (会覆盖 provider)
    api_key: ""                # base_url 的 API 密钥 (回退到 OPENAI_API_KEY)
    timeout: 120               # 秒 — LLM API 调用超时；视觉负载需要较长的超时时间
    download_timeout: 30       # 秒 — 图像 HTTP 下载超时；网络慢时可增加此值

  # 网页摘要 + 浏览器页面文本提取
  web_extract:
    provider: "auto"
    model: ""                  # 例如 "google/gemini-2.5-flash"
    base_url: ""
    api_key: ""
    timeout: 360               # 秒 (6分钟) — 每次尝试的 LLM 摘要超时

  # 危险命令批准分类器
  approval:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30                # 秒

  # 上下文压缩超时 (与 compression.* 配置分开)
  compression:
    timeout: 120               # 秒 — 压缩功能用于总结长对话，需要更多时间

  # 会话搜索 — 总结过去的会话匹配项
  session_search:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # 技能中心 — 技能匹配和搜索
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

  # 记忆刷新 — 为持久化记忆总结对话
  flush_memories:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
```

:::tip
每个辅助任务都有一个可配置的 `timeout` (单位：秒)。默认值：vision 120秒，web_extract 360秒，approval 30秒，compression 120秒。如果你为辅助任务使用速度较慢的本地模型，请增加这些值。Vision 还有一个单独的 `download_timeout` (默认 30秒) 用于 HTTP 图像下载 — 如果网络连接慢或使用自托管的图像服务器，请增加此值。
:::
:::info
上下文压缩有独立的 `compression:` 块用于设置阈值，以及 `auxiliary.compression:` 块用于模型/提供商设置——请参阅上文的[上下文压缩](#context-compression)。回退模型使用 `fallback_model:` 块——请参阅[回退模型](/integrations/providers#fallback-model)。这三者都遵循相同的提供商/模型/base_url 模式。
:::

<a id="changing-the-vision-model"></a>
### 更改视觉模型

要使用 GPT-4o 而非 Gemini Flash 进行图像分析：

```yaml
auxiliary:
  vision:
    model: "openai/gpt-4o"
```

或通过环境变量（在 `~/.hermes/.env` 中）：

```bash
AUXILIARY_VISION_MODEL=openai/gpt-4o
```

<a id="provider-options"></a>
### 提供商选项

这些选项适用于**辅助任务配置**（`auxiliary:`、`compression:`、`fallback_model:`），不适用于您的主 `model.provider` 设置。

| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 最佳可用选项（默认）。视觉任务会依次尝试 OpenRouter → Nous → Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter —— 可路由到任何模型（Gemini、GPT-4o、Claude 等） | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth（ChatGPT 账户）。支持视觉（gpt-5.3-codex）。 | `hermes model` → Codex |
| `"main"` | 使用您当前活动的自定义/主端点。这可以来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY`，或来自通过 `hermes model` / `config.yaml` 保存的自定义端点。适用于 OpenAI、本地模型或任何 OpenAI 兼容的 API。**仅限辅助任务 —— 对 `model.provider` 无效。** | 自定义端点凭证 + base URL |

<a id="common-setups"></a>
### 常见设置

**使用直接的自定义端点**（对于本地/自托管 API，比 `provider: "main"` 更清晰）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`，因此这是将辅助任务路由到特定端点最明确的方式。对于直接端点覆盖，Hermes 使用配置的 `api_key` 或回退到 `OPENAI_API_KEY`；它不会为该自定义端点复用 `OPENROUTER_API_KEY`。
**使用 OpenAI API 密钥进行视觉识别：**
```yaml
# 在 ~/.hermes/.env 文件中：
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # 或者用更便宜的 "gpt-4o-mini"
```

**使用 OpenRouter 进行视觉识别**（可路由到任何模型）：
```yaml
auxiliary:
  vision:
    provider: "openrouter"
    model: "openai/gpt-4o"      # 或者 "google/gemini-2.5-flash" 等
```

**使用 Codex OAuth**（ChatGPT Pro/Plus 账户 — 无需 API 密钥）：
```yaml
auxiliary:
  vision:
    provider: "codex"     # 使用你的 ChatGPT OAuth 令牌
    # model 默认为 gpt-5.3-codex（支持视觉）
```

**使用本地/自托管模型：**
```yaml
auxiliary:
  vision:
    provider: "main"      # 使用你为正常聊天配置的活跃自定义端点
    model: "my-local-model"
```

`provider: "main"` 会使用 Hermes 用于正常聊天的任何提供方 — 无论是命名的自定义提供方（例如 `beans`）、内置提供方如 `openrouter`，还是遗留的 `OPENAI_BASE_URL` 端点。

:::tip
如果你使用 Codex OAuth 作为主要模型提供方，视觉功能会自动生效 — 无需额外配置。Codex 已包含在视觉功能的自动检测链中。
:::

:::warning
**视觉功能需要多模态模型。** 如果你设置 `provider: "main"`，请确保你的端点支持多模态/视觉识别 — 否则图像分析会失败。
:::

<a id="environment-variables-legacy"></a>
### 环境变量（遗留方式）

辅助模型也可以通过环境变量配置。但是，`config.yaml` 是首选方法 — 它更易于管理，并且支持所有选项，包括 `base_url` 和 `api_key`。

| 设置项 | 环境变量 |
|---------|---------------------|
| 视觉提供方 | `AUXILIARY_VISION_PROVIDER` |
| 视觉模型 | `AUXILIARY_VISION_MODEL` |
| 视觉端点 | `AUXILIARY_VISION_BASE_URL` |
| 视觉 API 密钥 | `AUXILIARY_VISION_API_KEY` |
| 网页提取提供方 | `AUXILIARY_WEB_EXTRACT_PROVIDER` |
| 网页提取模型 | `AUXILIARY_WEB_EXTRACT_MODEL` |
| 网页提取端点 | `AUXILIARY_WEB_EXTRACT_BASE_URL` |
| 网页提取 API 密钥 | `AUXILIARY_WEB_EXTRACT_API_KEY` |
压缩和备用模型设置仅在 config.yaml 中配置。

:::tip
运行 `hermes config` 查看你当前的辅助模型设置。只有当覆盖项与默认值不同时才会显示。
:::

<a id="reasoning-effort"></a>
## 推理强度

控制模型在回应前“思考”的程度：

```yaml
agent:
  reasoning_effort: ""   # 空 = 中等（默认）。选项：none, minimal, low, medium, high, xhigh (max)
```

当未设置时（默认），推理强度默认为“medium”——一个适用于大多数任务的平衡级别。设置一个值会覆盖它——更高的推理强度在复杂任务上能提供更好的结果，但代价是消耗更多 token 和增加延迟。

你也可以在运行时使用 `/reasoning` 命令更改推理强度：

```
/reasoning           # 显示当前强度级别和显示状态
/reasoning high      # 将推理强度设置为 high
/reasoning none      # 禁用推理
/reasoning show      # 在每个回应上方显示模型思考过程
/reasoning hide      # 隐藏模型思考过程
```

<a id="tool-use-enforcement"></a>
## 工具使用强制

某些模型偶尔会以文本形式描述预期操作，而不是进行工具调用（例如“我会运行测试……”而不是实际调用终端）。工具使用强制功能会注入系统提示指导，引导模型回到实际调用工具的行为。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"` (默认) | 对匹配以下子串的模型启用：`gpt`, `codex`, `gemini`, `gemma`, `grok`。对所有其他模型（Claude, DeepSeek, Qwen 等）禁用。 |
| `true` | 无论模型如何，始终启用。如果你发现当前模型在描述操作而不是执行它们，这很有用。 |
| `false` | 无论模型如何，始终禁用。 |
| `["gpt", "codex", "qwen", "llama"]` | 仅当模型名称包含所列出的子串之一时启用（不区分大小写）。 |

<a id="what-it-injects"></a>
### 它注入什么

启用后，可能会向系统提示添加三层指导：
1.  **通用工具使用强制**（所有匹配的模型）——指示模型立即调用工具，而不是描述意图；持续工作直到任务完成，并且永远不要以承诺未来行动来结束一个回合。

2.  **OpenAI 执行纪律**（仅限 GPT 和 Codex 模型）——额外的指导，针对 GPT 特有的失败模式：放弃处理部分结果、跳过先决条件查找、产生幻觉而不使用工具，以及未经核实就宣布“完成”。

3.  **Google 操作指南**（仅限 Gemini 和 Gemma 模型）——简洁性、绝对路径、并行工具调用以及编辑前验证模式。

这些对用户是透明的，只影响系统提示。那些已经能可靠使用工具的模型（如 Claude）不需要此指导，这就是为什么 `"auto"` 会排除它们。

<a id="when-to-turn-it-on"></a>
### 何时开启

如果你使用的模型不在默认的自动列表中，并且注意到它经常描述它*将要*做什么而不是实际去做，请设置 `tool_use_enforcement: true` 或将模型子字符串添加到列表中：

```yaml
agent:
  tool_use_enforcement: ["gpt", "codex", "gemini", "grok", "my-custom-model"]
```

<a id="tts-configuration"></a>
## TTS 配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts"
  speed: 1.0                    # 全局语速乘数（所有提供商的回退值）
  edge:
    voice: "en-US-AriaNeural"   # 322 种语音，74 种语言
    speed: 1.0                  # 语速乘数（转换为速率百分比，例如 1.5 → +50%）
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0                  # 语速乘数（API 会将其限制在 0.25–4.0 之间）
    base_url: "https://api.openai.com/v1"  # 用于覆盖 OpenAI 兼容的 TTS 端点
  minimax:
    speed: 1.0                  # 语音语速乘数
    # base_url: ""              # 可选：用于覆盖 OpenAI 兼容的 TTS 端点
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - Neutral (默认)
  gemini:
    model: "gemini-2.5-flash-preview-tts"   # 或 gemini-2.5-pro-preview-tts
    voice: "Kore"               # 30 种预置语音：Zephyr, Puck, Kore, Enceladus 等。
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
这同时控制着 `text_to_speech` 工具和语音模式下的语音回复（CLI 或消息网关中的 `/voice tts` 命令）。

**语速回退层级：** 特定提供商的语速（例如 `tts.edge.speed`）→ 全局 `tts.speed` → 默认值 `1.0`。设置全局 `tts.speed` 可对所有提供商应用统一的语速，或按提供商覆盖以进行细粒度控制。

<a id="display-settings"></a>
## 显示设置 {#display-settings}

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # 在消息网关中启用 /verbose 斜杠命令
  tool_progress_overrides: {}  # 按平台覆盖设置（见下文）
  interim_assistant_messages: true  # 网关：将对话中自然的助手更新作为独立消息发送
  skin: default           # 内置或自定义 CLI 皮肤（见 user-guide/features/skins）
  personality: "kawaii"  # 遗留的装饰性字段，仍在某些摘要中显示
  compact: false          # 紧凑输出模式（减少空白）
  resume_display: full    # full（恢复时显示之前的消息）| minimal（仅显示一行摘要）
  bell_on_complete: false # Agent 完成任务时播放终端提示音（适用于长任务）
  show_reasoning: false   # 在每个响应上方显示模型推理/思考过程（用 /reasoning show|hide 切换）
  streaming: false        # 令牌到达时实时流式输出到终端
  show_cost: false        # 在 CLI 状态栏显示估算的 $ 成本
  tool_preview_length: 0  # 工具调用预览的最大字符数（0 = 无限制，显示完整路径/命令）
```

| 模式 | 你将看到的内容 |
|------|-------------|
| `off` | 静默 — 仅显示最终响应 |
| `new` | 仅在工具变更时显示工具指示器 |
| `all` | 每次工具调用都附带简短预览（默认） |
| `verbose` | 完整的参数、结果和调试日志 |

在 CLI 中，使用 `/verbose` 命令在这些模式间循环切换。要在消息平台（Telegram、Discord、Slack 等）中使用 `/verbose` 命令，请在上方的 `display` 部分设置 `tool_progress_command: true`。该命令随后将循环切换模式并保存到配置中。
<a id="per-platform-progress-overrides"></a>
### 按平台覆盖进度显示设置

不同平台对详细程度的需求不同。例如，Signal 无法编辑消息，因此每个进度更新都会成为一条独立的消息——这很嘈杂。使用 `tool_progress_overrides` 来设置每个平台的模式：

```yaml
display:
  tool_progress: all          # 全局默认值
  tool_progress_overrides:
    signal: 'off'             # 在 Signal 上静默进度
    telegram: verbose         # 在 Telegram 上显示详细进度
    slack: 'off'              # 在共享的 Slack 工作区中保持安静
```

没有覆盖设置的平台将回退到全局的 `tool_progress` 值。有效的平台键包括：`telegram`、`discord`、`slack`、`signal`、`whatsapp`、`matrix`、`mattermost`、`email`、`sms`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot`。

`interim_assistant_messages` 仅适用于网关。启用后，Hermes 会将对话过程中已完成的助手更新作为单独的聊天消息发送。这与 `tool_progress` 无关，也不需要网关流式传输。

<a id="privacy"></a>
## 隐私

```yaml
privacy:
  redact_pii: false  # 从 LLM 上下文中剥离个人身份信息（仅限网关）
```

当 `redact_pii` 为 `true` 时，网关会在将系统提示发送给 LLM 之前，从支持的平台中删除个人身份信息：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 上的用户 ID） | 哈希化为 `user_<12-char-sha256>` |
| 用户 ID | 哈希化为 `user_<12-char-sha256>` |
| 聊天 ID | 数字部分被哈希化，平台前缀保留（例如 `telegram:&lt;hash&gt;`） |
| 主频道 ID | 数字部分被哈希化 |
| 用户姓名 / 用户名 | **不受影响**（用户选择，公开可见） |

**平台支持：** 去标识化适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 被排除在外，因为它们的提及系统（`<@user_id>`）需要在 LLM 上下文中使用真实的 ID。

哈希值是确定性的——同一用户始终映射到相同的哈希值，因此模型仍然可以区分群聊中的不同用户。路由和投递在内部使用原始值。
<a id="speech-to-text-stt"></a>
## 语音转文字 (STT)

```yaml
stt:
  provider: "local"            # "local" | "groq" | "openai" | "mistral"
  local:
    model: "base"              # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe
  # model: "whisper-1"         # 旧版后备键名，仍被支持
```

各提供商的行为：

- `local` 使用在你机器上运行的 `faster-whisper`。请单独安装：`pip install faster-whisper`。
- `groq` 使用 Groq 的 Whisper 兼容端点，并读取 `GROQ_API_KEY`。
- `openai` 使用 OpenAI 的语音 API，并读取 `VOICE_TOOLS_OPENAI_KEY`。

如果请求的提供商不可用，Hermes 会按以下顺序自动回退：`local` → `groq` → `openai`。

Groq 和 OpenAI 的模型覆盖由环境变量驱动：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

<a id="voice-mode-cli"></a>
## 语音模式 (CLI)

```yaml
voice:
  record_key: "ctrl+b"         # CLI 内的按键通话键
  max_recording_seconds: 120    # 长录音的强制停止时间
  auto_tts: false               # 当启用 `/voice on` 时，自动启用语音回复
  silence_threshold: 200        # 语音检测的 RMS 阈值
  silence_duration: 3.0         # 自动停止前的静音时长（秒）
```

在 CLI 中使用 `/voice on` 启用麦克风模式，使用 `record_key` 开始/停止录音，使用 `/voice tts` 切换语音回复。完整的设置步骤和平台特定行为，请参阅[语音模式](/user-guide/features/voice-mode)。

<a id="streaming"></a>
## 流式传输

将令牌实时传输到终端或消息平台，而不是等待完整响应。

<a id="cli-streaming"></a>
### CLI 流式传输

```yaml
display:
  streaming: true         # 实时将令牌流式传输到终端
  show_reasoning: true    # 同时流式传输推理/思考令牌（可选）
```

启用后，响应会在一个流式传输框内逐个令牌显示。工具调用仍会被静默捕获。如果提供商不支持流式传输，系统会自动回退到正常显示模式。
<a id="gateway-streaming-telegram-discord-slack"></a>
### 网关流式传输（Telegram、Discord、Slack）

```yaml
streaming:
  enabled: true           # 启用渐进式消息编辑
  transport: edit         # "edit"（渐进式消息编辑）或 "off"
  edit_interval: 0.3      # 消息编辑间隔秒数
  buffer_threshold: 40    # 强制刷新编辑前的字符数阈值
  cursor: " ▉"            # 流式传输期间显示的光标
```

启用后，机器人会在收到第一个 token 时发送一条消息，然后随着更多 token 的到来逐步编辑该消息。对于不支持消息编辑的平台（Signal、Email、Home Assistant），系统会在首次尝试时自动检测——流式传输会在该会话中被优雅地禁用，而不会导致消息泛滥。

如果希望在不进行渐进式 token 编辑的情况下，获得独立、自然的对话中途助手更新，请设置 `display.interim_assistant_messages: true`。

**溢出处理：** 如果流式传输的文本超过了平台的消息长度限制（约 4096 个字符），当前消息将被最终确定，并自动开始一条新消息。

:::note
流式传输默认是禁用的。请在 `~/.hermes/config.yaml` 中启用它以体验流式传输的用户体验。
:::

<a id="group-chat-session-isolation"></a>
## 群聊会话隔离

控制共享聊天是每个房间保持一个对话，还是每个参与者保持一个对话：

```yaml
group_sessions_per_user: true  # true = 在群组/频道中实现按用户隔离，false = 每个聊天一个共享会话
```

- `true` 是默认且推荐的设置。在 Discord 频道、Telegram 群组、Slack 频道等共享上下文中，当平台提供用户 ID 时，每个发送者都会获得自己的会话。
- `false` 会恢复到旧的共享房间行为。如果你明确希望 Hermes 将频道视为一个协作对话，这可能很有用，但这也意味着用户将共享上下文、token 成本和中断状态。
- 私信不受影响。Hermes 仍会像往常一样按聊天/私信 ID 来区分私信。
- 无论哪种设置，线程都与其父频道保持隔离；当设置为 `true` 时，每个参与者在线程内部也会获得自己的会话。
有关行为详情和示例，请参阅 [会话](/user-guide/sessions) 和 [Discord 指南](/user-guide/messaging/discord)。

<a id="unauthorized-dm-behavior"></a>
## 未授权的私信行为

控制 Hermes 在陌生用户发送私信时的行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。Hermes 拒绝访问，但在私信中回复一个一次性配对码。
- `ignore` 会静默忽略未授权的私信。
- 各平台的配置节会覆盖全局默认值，因此你可以保持广泛的配对启用，同时让某个平台更安静。

<a id="quick-commands"></a>
## 快捷命令 {#quick-commands}

定义自定义命令来运行 shell 命令，无需调用 LLM —— 零令牌消耗，即时执行。特别适用于从消息平台（Telegram、Discord 等）快速检查服务器或运行实用脚本。

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
```

用法：在 CLI 或任何消息平台中输入 `/status`、`/disk`、`/update` 或 `/gpu`。命令在主机本地运行并直接返回输出 —— 不调用 LLM，不消耗令牌。

- **30 秒超时** —— 长时间运行的命令会被终止并返回错误消息
- **优先级** —— 快捷命令在技能命令之前被检查，因此你可以覆盖技能名称
- **自动补全** —— 快捷命令在调度时解析，不会显示在内置的 slash 命令自动补全表格中
- **类型** —— 仅支持 `exec`（运行 shell 命令）；其他类型会显示错误
- **随处可用** —— CLI、Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant

<a id="human-delay"></a>
## 人类延迟

在消息平台中模拟类似人类的响应节奏：

```yaml
human_delay:
  mode: "off"                  # off | natural | custom
  min_ms: 800                  # 最小延迟（自定义模式）
  max_ms: 2500                 # 最大延迟（自定义模式）
```
<a id="code-execution"></a>
## 代码执行

配置 `execute_code` 工具：

```yaml
code_execution:
  mode: project                # project (默认) | strict
  timeout: 300                 # 最大执行时间（秒）
  max_tool_calls: 50           # 代码执行期间的最大工具调用次数
```

**`mode`** 控制脚本的工作目录和 Python 解释器：

- **`project`** (默认) — 脚本在会话的工作目录中运行，并使用当前激活的 virtualenv/conda 环境的 python。项目依赖（`pandas`、`torch`、项目包）和相对路径（`.env`、`./data.csv`）会自然解析，与 `terminal()` 工具看到的环境一致。
- **`strict`** — 脚本在一个临时暂存目录中运行，并使用 `sys.executable`（Hermes 自身的 python）。这提供了最大的可复现性，但项目依赖和相对路径将无法解析。

环境变量清理（清除 `*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_PASSWORD`、`*_CREDENTIAL`、`*_PASSWD`、`*_AUTH`）以及工具白名单在这两种模式下同样适用——切换模式不会改变安全态势。

<a id="web-search-backends"></a>
## 网络搜索后端

`web_search`、`web_extract` 和 `web_crawl` 工具支持四个后端提供商。在 `config.yaml` 中或通过 `hermes tools` 配置后端：

```yaml
web:
  backend: firecrawl    # firecrawl | parallel | tavily | exa
```

| 后端 | 环境变量 | 搜索 | 提取 | 爬取 |
|---------|---------|--------|---------|-------|
| **Firecrawl** (默认) | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |

**后端选择：** 如果未设置 `web.backend`，则根据可用的 API 密钥自动检测后端。如果只设置了 `EXA_API_KEY`，则使用 Exa。如果只设置了 `TAVILY_API_KEY`，则使用 Tavily。如果只设置了 `PARALLEL_API_KEY`，则使用 Parallel。否则，Firecrawl 是默认后端。

**自托管 Firecrawl：** 设置 `FIRECRAWL_API_URL` 指向你自己的实例。当设置了自定义 URL 时，API 密钥变为可选（在服务器上设置 `USE_DB_AUTHENTICATION=false` 以禁用身份验证）。
**并行搜索模式：** 设置 `PARALLEL_SEARCH_MODE` 以控制搜索行为 — `fast`、`one-shot` 或 `agentic`（默认：`agentic`）。

<a id="browser"></a>
## 浏览器

配置浏览器自动化行为：

```yaml
browser:
  inactivity_timeout: 120        # 自动关闭空闲会话前的等待秒数
  command_timeout: 30             # 浏览器命令（截图、导航等）的超时时间（秒）
  record_sessions: false         # 自动将浏览器会话录制为 WebM 视频到 ~/.hermes/browser_recordings/
  camofox:
    managed_persistence: false   # 为 true 时，Camofox 会话会在重启后持久化 cookies/登录状态
```

浏览器工具集支持多个提供商。有关 Browserbase、Browser Use 和本地 Chrome CDP 设置的详细信息，请参阅[浏览器功能页面](/user-guide/features/browser)。

<a id="timezone"></a>
## 时区

使用 IANA 时区字符串覆盖服务器本地时区。影响日志中的时间戳、cron 调度和系统提示中的时间注入。

```yaml
timezone: "America/New_York"   # IANA 时区（默认："" = 服务器本地时间）
```

支持的值：任何 IANA 时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。留空或省略则使用服务器本地时间。

<a id="discord"></a>
## Discord

为消息网关配置 Discord 特定行为：

```yaml
discord:
  require_mention: true          # 在服务器频道中需要 @提及 才响应
  free_response_channels: ""     # 逗号分隔的频道 ID 列表，在此类频道中机器人无需 @提及 即可响应
  auto_thread: true              # 在频道中被 @提及 时自动创建线程
```

- `require_mention` — 当为 `true`（默认）时，机器人仅在服务器频道中被 `@BotName` 提及时才响应。私信始终无需提及即可工作。
- `free_response_channels` — 逗号分隔的频道 ID 列表，在此类频道中机器人会响应每条消息，无需提及。
- `auto_thread` — 当为 `true`（默认）时，在频道中被提及会自动为该对话创建一个线程，以保持频道整洁（类似于 Slack 的线程功能）。
<a id="security"></a>
## 安全

执行前的安全扫描与密钥脱敏：

```yaml
security:
  redact_secrets: true           # 在工具输出和日志中脱敏 API 密钥模式
  tirith_enabled: true           # 为终端命令启用 Tirith 安全扫描
  tirith_path: "tirith"          # tirith 二进制文件路径（默认：$PATH 中的 "tirith"）
  tirith_timeout: 5              # 等待 Tirith 扫描的超时时间（秒）
  tirith_fail_open: true         # 如果 Tirith 不可用，仍允许执行命令
  website_blocklist:             # 参见下方的网站阻止列表部分
    enabled: false
    domains: []
    shared_files: []
```

- `redact_secrets` — 在工具输出进入对话上下文和日志之前，自动检测并脱敏其中类似 API 密钥、令牌和密码的模式。
- `tirith_enabled` — 当设为 `true` 时，终端命令在执行前会由 [Tirith](https://github.com/StackGuardian/tirith) 进行扫描，以检测潜在的危险操作。
- `tirith_path` — tirith 二进制文件的路径。如果 tirith 安装在非标准位置，请设置此项。
- `tirith_timeout` — 等待 Tirith 扫描的最大秒数。如果扫描超时，命令将继续执行。
- `tirith_fail_open` — 当设为 `true`（默认）时，如果 Tirith 不可用或失败，仍允许执行命令。设为 `false` 则会在 Tirith 无法验证命令时阻止其执行。

## 网站阻止列表 {#website-blocklist}

阻止 Agent 的网络和浏览器工具访问特定域名：

```yaml
security:
  website_blocklist:
    enabled: false               # 启用 URL 阻止功能（默认：false）
    domains:                     # 被阻止的域名模式列表
      - "*.internal.company.com"
      - "admin.example.com"
      - "*.local"
    shared_files:                # 从外部文件加载额外的规则
      - "/etc/hermes/blocked-sites.txt"
```

启用后，任何匹配被阻止域名模式的 URL 都会在网络或浏览器工具执行前被拒绝。这适用于 `web_search`、`web_extract`、`browser_navigate` 以及任何访问 URL 的工具。
域名规则支持：
- 精确域名：`admin.example.com`
- 通配符子域名：`*.internal.company.com`（阻止所有子域名）
- 顶级域通配符：`*.local`

共享文件每行包含一个域名规则（空行和以 `#` 开头的注释会被忽略）。缺失或无法读取的文件会记录警告，但不会禁用其他 Web 工具。

策略会缓存 30 秒，因此配置更改无需重启即可快速生效。

<a id="smart-approvals"></a>
## 智能审批

控制 Hermes 如何处理潜在危险的命令：

```yaml
approvals:
  mode: manual   # manual | smart | off
```

| 模式 | 行为 |
|------|----------|
| `manual` (默认) | 在执行任何被标记的命令之前提示用户。在 CLI 中，显示交互式审批对话框。在消息传递中，将待处理的审批请求加入队列。 |
| `smart` | 使用辅助 LLM 来评估被标记的命令是否真正危险。低风险命令会自动批准，并在会话级别持久化。真正有风险的命令会升级给用户处理。 |
| `off` | 跳过所有审批检查。相当于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

智能模式对于减少审批疲劳特别有用——它让 Agent 在安全操作上更自主地工作，同时仍能捕获真正具有破坏性的命令。

:::warning
设置 `approvals.mode: off` 会禁用所有终端命令的安全检查。仅在受信任的沙盒环境中使用此设置。
:::

<a id="checkpoints"></a>
## 检查点

在执行破坏性文件操作之前自动创建文件系统快照。详情请参阅[检查点与回滚](/user-guide/checkpoints-and-rollback)。

```yaml
checkpoints:
  enabled: true                  # 启用自动检查点 (也可使用：hermes --checkpoints)
  max_snapshots: 50              # 每个目录保留的最大检查点数量
```

<a id="delegation"></a>
## 委派

为委托工具配置子 Agent 行为：

```yaml
delegation:
  # model: "google/gemini-3-flash-preview"  # 覆盖模型 (空 = 继承父级)
  # provider: "openrouter"                  # 覆盖提供商 (空 = 继承父级)
  # base_url: "http://localhost:1234/v1"    # 直接的 OpenAI 兼容端点 (优先级高于 provider)
  # api_key: "local-key"                    # base_url 的 API 密钥 (回退到 OPENAI_API_KEY)
```
**子 Agent 的 provider:model 覆盖：** 默认情况下，子 Agent 会继承父 Agent 的 provider 和 model。设置 `delegation.provider` 和 `delegation.model` 可以将子 Agent 路由到不同的 provider:model 组合 —— 例如，当你的主 Agent 运行一个昂贵的推理模型时，让子 Agent 使用一个廉价/快速的模型来处理范围狭窄的子任务。

**直接端点覆盖：** 如果你想要更明显的自定义端点路径，可以设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这会将子 Agent 直接发送到该 OpenAI 兼容端点，并且优先级高于 `delegation.provider`。如果省略了 `delegation.api_key`，Hermes 将仅回退到 `OPENAI_API_KEY`。

委托 provider 使用与 CLI/网关启动时相同的凭据解析机制。支持所有已配置的 provider：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。当设置了 provider 时，系统会自动解析正确的 base URL、API key 和 API 模式 —— 无需手动配置凭据。

**优先级：** 配置中的 `delegation.base_url` → 配置中的 `delegation.provider` → 父 provider（继承）。配置中的 `delegation.model` → 父 model（继承）。仅设置 `model` 而不设置 `provider` 只会更改模型名称，同时保留父级的凭据（适用于在同一 provider 内切换模型，例如 OpenRouter）。

<a id="clarify"></a>
## Clarify

配置澄清提示行为：

```yaml
clarify:
  timeout: 120                 # 等待用户澄清响应的秒数
```

<a id="context-files-soul-md-agents-md"></a>
## 上下文文件 (SOUL.md, AGENTS.md)

Hermes 使用两种不同的上下文作用域：

| 文件 | 用途 | 作用域 |
|------|---------|-------|
| `SOUL.md` | **主 Agent 身份** —— 定义 Agent 是谁（系统提示中的槽位 #1） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定指令（最高优先级） | 向上遍历到 git 根目录 |
| `AGENTS.md` | 项目特定指令，编码规范 | 递归遍历目录 |
| `CLAUDE.md` | Claude Code 上下文文件（也会被检测） | 仅工作目录 |
| `.cursorrules` | Cursor IDE 规则（也会被检测） | 仅工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被检测） | 仅工作目录 |
- **SOUL.md** 是 Agent 的核心身份文件。它占据系统提示词中的第 1 个位置，完全替代内置的默认身份。编辑此文件可以完全自定义 Agent 的身份。
- 如果 SOUL.md 缺失、为空或无法加载，Hermes 将回退到内置的默认身份。
- **项目上下文文件采用优先级系统** —— 只加载一种类型（首次匹配优先）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。SOUL.md 始终独立加载。
- **AGENTS.md** 是层级式的：如果子目录也有 AGENTS.md，所有文件的内容会被合并。
- 如果 `SOUL.md` 不存在，Hermes 会自动创建一个默认版本。
- 所有加载的上下文文件都有 20,000 个字符的限制，并会进行智能截断。

另请参阅：
- [个性与 SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)

<a id="working-directory"></a>
## 工作目录

| 上下文 | 默认值 |
|---------|---------|
| **CLI (`hermes`)** | 运行命令时的当前目录 |
| **消息网关** | 主目录 `~` (可通过 `MESSAGING_CWD` 覆盖) |
| **Docker / Singularity / Modal / SSH** | 容器或远程机器内的用户主目录 |

覆盖工作目录：
```bash
# 在 ~/.hermes/.env 或 ~/.hermes/config.yaml 中：
MESSAGING_CWD=/home/myuser/projects    # 网关会话
TERMINAL_CWD=/workspace                # 所有终端会话
```
