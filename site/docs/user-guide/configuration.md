---
sidebar_position: 2
title: "配置"
description: "配置 Hermes Agent — config.yaml、提供方、模型、API 密钥等"
---

# 配置

所有设置都存储在 `~/.hermes/` 目录中，便于访问。

## 目录结构

```text
~/.hermes/
├── config.yaml     # 设置（模型、终端、TTS、压缩等）
├── .env            # API 密钥和机密信息
├── auth.json       # OAuth 提供方凭据（Nous Portal 等）
├── SOUL.md         # 主要 Agent 身份（系统提示词中的槽位 #1）
├── memories/       # 持久化记忆（MEMORY.md, USER.md）
├── skills/         # Agent 创建的技能（通过 skill_manage 工具管理）
├── cron/           # 计划任务
├── sessions/       # 网关会话
└── logs/           # 日志（errors.log, gateway.log — 机密信息自动脱敏）
```

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

## 配置优先级

设置按以下顺序解析（优先级从高到低）：

1.  **CLI 参数** — 例如 `hermes chat --model anthropic/claude-sonnet-4`（每次调用时覆盖）
2.  **`~/.hermes/config.yaml`** — 所有非机密设置的主要配置文件
3.  **`~/.hermes/.env`** — 环境变量的后备；**必需**用于机密信息（API 密钥、令牌、密码）
4.  **内置默认值** — 当没有其他设置时，硬编码的安全默认值

:::info 经验法则
机密信息（API 密钥、机器人令牌、密码）放在 `.env` 中。其他所有内容（模型、终端后端、压缩设置、内存限制、工具集）放在 `config.yaml` 中。当两者都设置时，对于非机密设置，`config.yaml` 优先。
:::

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

单个值中支持多个引用：`url: "${HOST}:${PORT}"`。如果引用的变量未设置，占位符将按字面保留（`${UNDEFINED_VAR}` 保持不变）。仅支持 `${VAR}` 语法 — 裸 `$VAR` 不会被展开。

关于 AI 提供方设置（OpenRouter、Anthropic、Copilot、自定义端点、自托管 LLM、后备模型等），请参阅 [AI 提供方](/integrations/providers)。

## 终端后端配置

Hermes 支持六种终端后端。每种决定了 Agent 的 shell 命令实际执行的位置 — 你的本地机器、Docker 容器、通过 SSH 连接的远程服务器、Modal 云沙箱、Daytona 工作区，或 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | singularity
  cwd: "."          # 工作目录（"." = 本地的当前目录，容器的 "/root"）
  timeout: 180      # 每条命令的超时时间（秒）
  env_passthrough: []  # 要转发到沙箱化执行的环境变量名称（terminal + execute_code）
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Singularity 后端的容器镜像
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Modal 后端的容器镜像
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Daytona 后端的容器镜像
```

对于 Modal 和 Daytona 等云沙箱，`container_persistent: true` 意味着 Hermes 将尝试在沙箱重建过程中保留文件系统状态。它并不保证同一个活动的沙箱、PID 空间或后台进程稍后仍在运行。

### 后端概览

| 后端 | 命令运行位置 | 隔离性 | 最适合 |
|---------|-------------------|-----------|----------|
| **local** | 直接在你的机器上 | 无 | 开发、个人使用 |
| **docker** | Docker 容器 | 完全（命名空间、cap-drop） | 安全沙箱化、CI/CD |
| **ssh** | 通过 SSH 连接的远程服务器 | 网络边界 | 远程开发、强大硬件 |
| **modal** | Modal 云沙箱 | 完全（云虚拟机） | 临时云计算、评估 |
| **daytona** | Daytona 工作区 | 完全（云容器） | 托管的云开发环境 |
| **singularity** | Singularity/Apptainer 容器 | 命名空间（--containall） | HPC 集群、共享机器 |

### 本地后端

默认后端。命令直接在您的机器上运行，没有隔离。无需特殊设置。

```yaml
terminal:
  backend: local
```

:::warning
Agent 拥有与您的用户账户相同的文件系统访问权限。使用 `hermes tools` 来禁用您不想要的工具，或者切换到 Docker 以进行沙箱化。
:::

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
  container_cpu: 1                 # CPU 核心数（0 = 无限制）
  container_memory: 5120           # MB（0 = 无限制）
  container_disk: 51200            # MB（需要在 XFS+pquota 上使用 overlay2）
  container_persistent: true       # 在会话间持久化 /workspace 和 /root
```

**要求：** Docker Desktop 或 Docker Engine 已安装并正在运行。Hermes 会探测 `$PATH` 以及常见的 macOS 安装位置（`/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用程序包）。

**容器生命周期：** 每个会话启动一个长期运行的容器（`docker run -d ... sleep 2h`）。命令通过 `docker exec` 使用登录 shell 运行。清理时，容器会被停止并移除。

**安全加固：**
- `--cap-drop ALL`，仅重新添加 `DAC_OVERRIDE`、`CHOWN`、`FOWNER`
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- 为 `/tmp`（512MB）、`/var/tmp`（256MB）、`/run`（64MB）设置大小限制的 tmpfs

**凭据转发：** `docker_forward_env` 中列出的环境变量首先从你的 shell 环境解析，然后从 `~/.hermes/.env` 解析。技能也可以声明 `required_environment_variables`，这些变量会自动合并。

### SSH 后端

通过 SSH 在远程服务器上运行命令。使用 ControlMaster 进行连接复用（5 分钟空闲保活）。默认启用持久化 shell — 状态（cwd、环境变量）在命令间保持。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # 保持一个长期存活的 bash 会话（默认：true）
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

**工作原理：** 在初始化时使用 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 连接。持久化 shell 在远程主机上保持一个 `bash -l` 进程存活，通过临时文件进行通信。需要 `stdin_data` 或 `sudo` 的命令会自动回退到一次性模式。

### Modal 后端

在 [Modal](https://modal.com) 云沙箱中运行命令。每个任务获得一个隔离的虚拟机，可配置 CPU、内存和磁盘。文件系统可以在会话间进行快照/恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB（5GB）
  container_disk: 51200            # MB（50GB）
  container_persistent: true       # 快照/恢复文件系统
```
**必需：** 设置 `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` 环境变量，或提供 `~/.modal.toml` 配置文件。

**持久化：** 启用后，沙盒文件系统会在清理时创建快照，并在下次会话时恢复。快照记录在 `~/.hermes/modal_snapshots.json` 中。这仅保留文件系统状态，不保留活动进程、PID 空间或后台作业。

**凭证文件：** 自动从 `~/.hermes/` 挂载（OAuth 令牌等），并在每次命令执行前同步。

### Daytona 后端

在 [Daytona](https://daytona.io) 管理的工作区中运行命令。支持停止/恢复以实现持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB → 转换为 GiB
  container_disk: 10240            # MB → 转换为 GiB (最大 10 GiB)
  container_persistent: true       # 停止/恢复而非删除
```

**必需：** `DAYTONA_API_KEY` 环境变量。

**持久化：** 启用后，沙盒在清理时会被停止（而非删除），并在下次会话时恢复。沙盒名称遵循 `hermes-{task_id}` 模式。

**磁盘限制：** Daytona 强制最大 10 GiB。超过此限制的请求会被截断并发出警告。

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

**镜像处理：** Docker URL (`docker://...`) 会自动转换为 SIF 文件并缓存。现有的 `.sif` 文件直接使用。

**临时目录：** 按顺序解析：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent` (HPC 惯例) → `~/.hermes/sandboxes/singularity`。

**隔离：** 使用 `--containall --no-home` 实现完整的命名空间隔离，不挂载宿主机家目录。

### 常见终端后端问题

如果终端命令立即失败或报告终端工具被禁用：

- **Local** — 无特殊要求。入门时最安全的默认选项。
- **Docker** — 运行 `docker version` 验证 Docker 是否正常工作。如果失败，请修复 Docker 或执行 `hermes config set terminal.backend local`。
- **SSH** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER`。如果缺少任一，Hermes 会记录明确的错误。
- **Modal** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml`。运行 `hermes doctor` 检查。
- **Daytona** — 需要 `DAYTONA_API_KEY`。Daytona SDK 处理服务器 URL 配置。
- **Singularity** — 需要 `$PATH` 中存在 `apptainer` 或 `singularity`。在 HPC 集群上常见。

如有疑问，请将 `terminal.backend` 设置回 `local`，并先验证命令能否在那里运行。

### Docker 卷挂载

使用 Docker 后端时，`docker_volumes` 允许你将宿主机目录与容器共享。每个条目使用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # 读写 (默认)
    - "/home/user/datasets:/data:ro"              # 只读
    - "/home/user/outputs:/outputs"               # Agent 写入，你读取
```

这适用于：
- **向 Agent 提供文件**（数据集、配置、参考代码）
- **从 Agent 接收文件**（生成的代码、报告、导出文件）
- **共享工作区**，你和 Agent 都能访问相同的文件

也可以通过环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'` (JSON 数组)。

### Docker 凭证转发

默认情况下，Docker 终端会话不会继承任意的宿主机凭证。如果你需要在容器内使用特定令牌，请将其添加到 `terminal.docker_forward_env`。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 首先从当前 shell 解析每个列出的变量，如果变量已通过 `hermes config set` 保存，则回退到 `~/.hermes/.env`。

:::warning
`docker_forward_env` 中列出的任何内容都会对容器内运行的命令可见。只转发你愿意暴露给终端会话的凭证。
:::

### 可选：将启动目录挂载到 `/workspace`

默认情况下，Docker 沙盒保持隔离。除非你明确选择加入，否则 Hermes **不会**将你当前的宿主机工作目录传递到容器中。

在 `config.yaml` 中启用：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用后：
- 如果你从 `~/projects/my-app` 启动 Hermes，该宿主机目录将被绑定挂载到 `/workspace`
- Docker 后端在 `/workspace` 中启动
- 文件工具和终端命令都能看到相同的已挂载项目

禁用时，除非你通过 `docker_volumes` 显式挂载内容，否则 `/workspace` 仍归沙盒所有。

安全权衡：
- `false` 保持沙盒边界
- `true` 让沙盒直接访问你启动 Hermes 的目录

仅当你确实希望容器处理宿主机上的实时文件时，才使用此选择加入功能。

### 持久化 Shell

默认情况下，每个终端命令都在其自己的子进程中运行——工作目录、环境变量和 shell 变量在命令之间重置。当启用**持久化 shell** 时，会在多个 `execute()` 调用之间保持一个长期存活的 bash 进程，使得状态在命令之间得以保留。

这对于 **SSH 后端** 最有用，因为它还能消除每次命令的连接开销。持久化 shell **默认对 SSH 启用**，对本地后端禁用。

```yaml
terminal:
  persistent_shell: true   # 默认 — 为 SSH 启用持久化 shell
```

要禁用：

```bash
hermes config set terminal.persistent_shell false
```

**在命令间持久化的内容：**
- 工作目录 (`cd /tmp` 对下一条命令生效)
- 导出的环境变量 (`export FOO=bar`)
- Shell 变量 (`MY_VAR=hello`)

**优先级：**

| 层级 | 变量 | 默认值 |
|-------|----------|---------|
| 配置 | `terminal.persistent_shell` | `true` |
| SSH 覆盖 | `TERMINAL_SSH_PERSISTENT` | 遵循配置 |
| 本地覆盖 | `TERMINAL_LOCAL_PERSISTENT` | `false` |

每个后端的特定环境变量具有最高优先级。如果你也想在本地后端启用持久化 shell：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
需要 `stdin_data` 或 sudo 的命令会自动回退到一次性模式，因为持久化 shell 的 stdin 已被 IPC 协议占用。
:::

有关每个后端的详细信息，请参阅[代码执行](features/code-execution.md)和 README 的[终端部分](features/tools.md)。

## 技能设置 {#skill-settings}

技能可以通过其 SKILL.md 文件的 frontmatter 声明自己的配置设置。这些是非机密值（路径、偏好、域设置），存储在 `config.yaml` 的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    wiki:
      path: ~/wiki          # 由 llm-wiki 技能使用
```

**技能设置的工作原理：**

- `hermes config migrate` 扫描所有已启用的技能，查找未配置的设置，并提示你进行配置
- `hermes config show` 在“技能设置”下显示所有技能设置及其所属技能
- 当技能加载时，其解析后的配置值会自动注入到技能上下文中

**手动设置值：**

```bash
hermes config set skills.config.wiki.path ~/my-research-wiki
```

有关在你自己的技能中声明配置设置的详细信息，请参阅[创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

## 记忆配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 个词元
  user_char_limit: 1375     # ~500 个词元
```
## 文件读取安全

控制单次 `read_file` 调用能返回多少内容。超过限制的读取会被拒绝，并返回错误，提示 Agent 使用 `offset` 和 `limit` 来读取更小的范围。这可以防止因读取一个压缩的 JS 包或大型数据文件而淹没上下文窗口。

```yaml
file_read_max_chars: 100000  # 默认值 — 约 25-35K tokens
```

如果你使用的是具有大上下文窗口的模型，并且经常读取大文件，可以提高此值。对于小上下文模型，则降低此值以保持读取效率：

```yaml
# 大上下文模型 (200K+)
file_read_max_chars: 200000

# 小型本地模型 (16K 上下文)
file_read_max_chars: 30000
```

Agent 还会自动对文件读取进行去重——如果同一文件区域被读取两次且文件未更改，则会返回一个轻量级的存根，而不是重新发送内容。这会在上下文压缩时重置，以便 Agent 在其内容被摘要化后可以重新读取文件。

## Git 工作树隔离

启用隔离的 git 工作树，以便在同一仓库上并行运行多个 Agent：

```yaml
worktree: true    # 始终创建工作树（与 hermes -w 相同）
# worktree: false # 默认值 — 仅在传递 -w 标志时创建
```

启用后，每个 CLI 会话都会在 `.worktrees/` 下创建一个带有自己分支的新工作树。Agent 可以编辑文件、提交、推送和创建 PR，而不会相互干扰。干净的工作树会在退出时被移除；脏的工作树会被保留以供手动恢复。

你也可以通过在仓库根目录下的 `.worktreeinclude` 文件中列出要复制到工作树中的 git 忽略文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩 {#context-compression}

Hermes 会自动压缩长对话，以保持在你的模型上下文窗口内。压缩摘要器是一个独立的 LLM 调用——你可以将其指向任何提供商或端点。

所有压缩设置都位于 `config.yaml` 中（没有环境变量）。

### 完整参考

```yaml
compression:
  enabled: true                                     # 开启/关闭压缩
  threshold: 0.50                                   # 在达到上下文限制的此百分比时触发压缩
  target_ratio: 0.20                                # 作为最近尾部保留的阈值比例
  protect_last_n: 20                                # 保持未压缩的最小最近消息数
  summary_model: "google/gemini-3-flash-preview"    # 用于摘要的模型
  summary_provider: "auto"                          # 提供商："auto"、"openrouter"、"nous"、"codex"、"main" 等
  summary_base_url: null                            # 自定义 OpenAI 兼容端点（覆盖提供商）
```

### 常见设置

**默认（自动检测）——无需配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
使用第一个可用的提供商（OpenRouter → Nous → Codex）和 Gemini Flash。

**强制使用特定提供商**（基于 OAuth 或 API 密钥）：
```yaml
compression:
  summary_provider: nous
  summary_model: gemini-3-flash
```
适用于任何提供商：`nous`、`openrouter`、`codex`、`anthropic`、`main` 等。

**自定义端点**（自托管、Ollama、zai、DeepSeek 等）：
```yaml
compression:
  summary_model: glm-4.7
  summary_base_url: https://api.z.ai/api/coding/paas/v4
```
指向自定义的 OpenAI 兼容端点。使用 `OPENAI_API_KEY` 进行身份验证。

### 三个旋钮如何交互

| `summary_provider` | `summary_base_url` | 结果 |
|---------------------|---------------------|--------|
| `auto` (默认) | 未设置 | 自动检测最佳可用提供商 |
| `nous` / `openrouter` / 等 | 未设置 | 强制使用该提供商，使用其身份验证 |
| 任意值 | 已设置 | 直接使用自定义端点（忽略提供商） |

:::warning 摘要模型上下文长度要求
`summary_model` **必须** 拥有至少与你的主 Agent 模型一样大的上下文窗口。压缩器会将对话的整个中间部分发送给摘要模型——如果该模型的上下文窗口小于主模型的，摘要调用将因上下文长度错误而失败。发生这种情况时，中间轮次的对话将被**丢弃而不进行摘要**，从而静默地丢失对话上下文。如果你覆盖了 `summary_model`，请验证其上下文长度是否达到或超过你的主模型。
:::

## 上下文引擎

上下文引擎控制在接近模型 token 限制时如何管理对话。内置的 `compressor` 引擎使用有损摘要（参见[上下文压缩](/developer-guide/context-compression-and-caching)）。插件引擎可以用其他策略替换它。

```yaml
context:
  engine: "compressor"    # 默认值 — 内置有损摘要
```

要使用插件引擎（例如，用于无损上下文管理的 LCM）：

```yaml
context:
  engine: "lcm"          # 必须与插件名称匹配
```

插件引擎**永远不会自动激活**——你必须显式地将 `context.engine` 设置为插件名称。可用的引擎可以通过 `hermes plugins` → Provider Plugins → Context Engine 浏览和选择。

有关内存插件的类似单选系统，请参阅[内存提供者](/user-guide/features/memory-providers)。

## 迭代预算压力

当 Agent 处理具有许多工具调用的复杂任务时，它可能会在不知不觉中耗尽迭代预算（默认值：90 轮）。预算压力会在接近限制时自动警告模型：

| 阈值 | 级别 | 模型看到的内容 |
|-----------|-------|---------------------|
| **70%** | 注意 | `[BUDGET: 63/90. 27 iterations left. Start consolidating.]` |
| **90%** | 警告 | `[BUDGET WARNING: 81/90. Only 9 left. Respond NOW.]` |

警告被注入到最后一个工具结果的 JSON 中（作为 `_budget_warning` 字段），而不是作为单独的消息——这保留了提示缓存，并且不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # 每次对话轮次的最大迭代次数（默认值：90）
```

预算压力默认启用。Agent 会自然地看到警告，作为工具结果的一部分，鼓励它在迭代次数用完之前整合工作并给出响应。

### 流式超时

LLM 流式连接有两层超时。两者都会为本地提供商（localhost、LAN IP）自动调整——大多数设置无需配置。

| 超时 | 默认值 | 本地提供商 | 环境变量 |
|---------|---------|----------------|---------|
| Socket 读取超时 | 120s | 自动提升至 1800s | `HERMES_STREAM_READ_TIMEOUT` |
| 陈旧流检测 | 180s | 自动禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| API 调用（非流式） | 1800s | 不变 | `HERMES_API_TIMEOUT` |

**Socket 读取超时** 控制 httpx 等待来自提供商的下一个数据块的时间。本地 LLM 在产生第一个 token 之前，可能需要几分钟的时间在大上下文上进行预填充，因此当 Hermes 检测到本地端点时，会将此值提高到 30 分钟。如果你显式设置了 `HERMES_STREAM_READ_TIMEOUT`，则无论端点检测如何，都将始终使用该值。

**陈旧流检测** 会终止那些接收 SSE 保持活动 ping 但没有实际内容的连接。对于本地提供商，这会被完全禁用，因为它们在预填充期间不发送保持活动 ping。

## 上下文压力警告

与迭代预算压力不同，上下文压力跟踪对话距离**压缩阈值**有多近——即触发上下文压缩以摘要旧消息的点。这有助于你和 Agent 了解对话何时变长。

| 进度 | 级别 | 发生的情况 |
|----------|-------|-------------|
| 距离阈值 **≥ 60%** | 信息 | CLI 显示青色进度条；网关发送信息通知 |
| 距离阈值 **≥ 85%** | 警告 | CLI 显示粗体黄色进度条；网关警告压缩即将发生 |

在 CLI 中，上下文压力显示为工具输出反馈中的进度条：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```
在消息平台上，会发送一条纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果自动压缩被禁用，警告会提示你上下文可能会被截断。

上下文压力是自动的——无需配置。它纯粹是作为一个面向用户的通知触发，不会修改消息流或向模型的上下文中注入任何内容。

## 凭证池策略

当你为同一个提供商拥有多个 API 密钥或 OAuth 令牌时，可以配置轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # 均匀轮换密钥
  anthropic: least_used      # 总是选择使用最少的密钥
```

选项：`fill_first`（默认）、`round_robin`、`least_used`、`random`。完整文档请参阅[凭证池](/user-guide/features/credential-pools)。

## 辅助模型 {#auxiliary-models}

Hermes 使用轻量级的“辅助”模型来处理图像分析、网页摘要和浏览器截图分析等辅助任务。默认情况下，这些任务通过自动检测使用 **Gemini Flash**——你不需要配置任何东西。

### 通用配置模式

Hermes 中的每个模型槽位——辅助任务、压缩、后备模型——都使用相同的三个旋钮：

| 键名 | 作用 | 默认值 |
|-----|-------------|---------|
| `provider` | 使用哪个提供商进行认证和路由 | `"auto"` |
| `model` | 请求哪个模型 | 提供商的默认模型 |
| `base_url` | 自定义的 OpenAI 兼容端点（覆盖 provider） | 未设置 |

当设置了 `base_url` 时，Hermes 会忽略 provider 并直接调用该端点（使用 `api_key` 或 `OPENAI_API_KEY` 进行认证）。当只设置了 `provider` 时，Hermes 会使用该提供商内置的认证和基础 URL。

辅助任务可用的提供商：`auto`、`openrouter`、`nous`、`codex`、`copilot`、`anthropic`、`main`、`zai`、`kimi-coding`、`minimax`、[提供商注册表](/reference/environment-variables)中注册的任何提供商，或你 `custom_providers` 列表中的任何命名自定义提供商（例如 `provider: "beans"`）。

:::warning `"main"` 仅用于辅助任务
`"main"` 提供商选项意味着“使用我的主 Agent 使用的任何提供商”——它仅在 `auxiliary:`、`compression:` 和 `fallback_model:` 配置内部有效。它**不是**顶层 `model.provider` 设置的有效值。如果你使用自定义的 OpenAI 兼容端点，请在 `model:` 部分设置 `provider: custom`。所有主模型提供商选项请参阅[AI 提供商](/integrations/providers)。
:::

### 完整的辅助配置参考

```yaml
auxiliary:
  # 图像分析 (vision_analyze 工具 + 浏览器截图)
  vision:
    provider: "auto"           # "auto", "openrouter", "nous", "codex", "main" 等
    model: ""                  # 例如 "openai/gpt-4o", "google/gemini-2.5-flash"
    base_url: ""               # 自定义 OpenAI 兼容端点（覆盖 provider）
    api_key: ""                # base_url 的 API 密钥（回退到 OPENAI_API_KEY）
    timeout: 30                # 秒 — LLM API 调用；对于慢速本地视觉模型可增加
    download_timeout: 30       # 秒 — 图像 HTTP 下载；对于慢速连接可增加

  # 网页摘要 + 浏览器页面文本提取
  web_extract:
    provider: "auto"
    model: ""                  # 例如 "google/gemini-2.5-flash"
    base_url: ""
    api_key: ""
    timeout: 360               # 秒 (6分钟) — 每次尝试的 LLM 摘要

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

  # 内存刷新 — 为持久化内存总结对话
  flush_memories:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
```

:::tip
每个辅助任务都有一个可配置的 `timeout`（以秒为单位）。默认值：vision 30秒，web_extract 360秒，approval 30秒，compression 120秒。如果你为辅助任务使用慢速本地模型，请增加这些值。Vision 还有一个单独的 `download_timeout`（默认 30秒）用于 HTTP 图像下载——对于慢速连接或自托管的图像服务器，请增加此值。
:::

:::info
上下文压缩有自己的顶层 `compression:` 块，包含 `summary_provider`、`summary_model` 和 `summary_base_url`——请参阅上面的[上下文压缩](#context-compression)。后备模型使用 `fallback_model:` 块——请参阅[后备模型](/integrations/providers#fallback-model)。这三者都遵循相同的 provider/model/base_url 模式。
:::

### 更改视觉模型

要使用 GPT-4o 而不是 Gemini Flash 进行图像分析：

```yaml
auxiliary:
  vision:
    model: "openai/gpt-4o"
```

或通过环境变量（在 `~/.hermes/.env` 中）：

```bash
AUXILIARY_VISION_MODEL=openai/gpt-4o
```

### 提供商选项

这些选项适用于**辅助任务配置**（`auxiliary:`、`compression:`、`fallback_model:`），不适用于你的主 `model.provider` 设置。

| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 最佳可用（默认）。Vision 尝试 OpenRouter → Nous → Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter — 路由到任何模型（Gemini、GPT-4o、Claude 等） | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth（ChatGPT 账户）。支持视觉（gpt-5.3-codex）。 | `hermes model` → Codex |
| `"main"` | 使用你活动的自定义/主端点。这可以来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY` 或通过 `hermes model` / `config.yaml` 保存的自定义端点。适用于 OpenAI、本地模型或任何 OpenAI 兼容的 API。**仅限辅助任务 — 对 `model.provider` 无效。** | 自定义端点凭证 + 基础 URL |

### 常见设置

**使用直接自定义端点**（对于本地/自托管 API，比 `provider: "main"` 更清晰）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 优先于 `provider`，因此这是将辅助任务路由到特定端点的最明确方式。对于直接端点覆盖，Hermes 使用配置的 `api_key` 或回退到 `OPENAI_API_KEY`；它不会为该自定义端点重用 `OPENROUTER_API_KEY`。

**使用 OpenAI API 密钥进行视觉分析：**
```yaml
# 在 ~/.hermes/.env 中：
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # 或 "gpt-4o-mini" 更便宜
```

**使用 OpenRouter 进行视觉分析**（路由到任何模型）：
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
    # model 默认为 gpt-5.3-codex（支持视觉）
```

**使用本地/自托管模型：**
```yaml
auxiliary:
  vision:
    provider: "main"      # 使用你活动的自定义端点
    model: "my-local-model"
```

`provider: "main"` 使用 Hermes 用于正常聊天的任何提供商——无论是命名的自定义提供商（例如 `beans`）、内置提供商如 `openrouter`，还是遗留的 `OPENAI_BASE_URL` 端点。

:::tip
如果你使用 Codex OAuth 作为主模型提供商，视觉功能会自动工作——无需额外配置。Codex 已包含在视觉的自动检测链中。
:::
:::warning
**视觉功能需要多模态模型支持。** 如果你设置了 `provider: "main"`，请确保你的端点支持多模态/视觉功能——否则图像分析将会失败。
:::

### 环境变量（旧版）

辅助模型也可以通过环境变量进行配置。不过，`config.yaml` 是首选方法——它更容易管理，并且支持包括 `base_url` 和 `api_key` 在内的所有选项。

| 配置项 | 环境变量 |
|---------|---------------------|
| Vision provider | `AUXILIARY_VISION_PROVIDER` |
| Vision model | `AUXILIARY_VISION_MODEL` |
| Vision endpoint | `AUXILIARY_VISION_BASE_URL` |
| Vision API key | `AUXILIARY_VISION_API_KEY` |
| Web extract provider | `AUXILIARY_WEB_EXTRACT_PROVIDER` |
| Web extract model | `AUXILIARY_WEB_EXTRACT_MODEL` |
| Web extract endpoint | `AUXILIARY_WEB_EXTRACT_BASE_URL` |
| Web extract API key | `AUXILIARY_WEB_EXTRACT_API_KEY` |

压缩和后备模型设置仅在 config.yaml 中配置。

:::tip
运行 `hermes config` 来查看你当前的辅助模型设置。只有当配置项的值与默认值不同时，才会显示覆盖的配置。
:::

## 推理努力程度

控制模型在回复前需要“思考”多少：

```yaml
agent:
  reasoning_effort: ""   # 空 = 中等（默认）。选项：none, minimal, low, medium, high, xhigh (最大)
```

当未设置（默认）时，推理努力程度默认为“中等”——一个适用于大多数任务的平衡级别。设置一个值会覆盖它——更高的推理努力程度会在复杂任务上提供更好的结果，但代价是消耗更多 token 和增加延迟。

你也可以通过 `/reasoning` 命令在运行时改变推理努力程度：

```
/reasoning           # 显示当前努力程度级别和显示状态
/reasoning high      # 将推理努力程度设置为 high
/reasoning none      # 禁用推理
/reasoning show      # 在每个回复上方显示模型思考过程
/reasoning hide      # 隐藏模型思考过程
```

## 工具使用强制执行

有些模型偶尔会用文本描述预期的动作，而不是实际调用工具（说“我会运行测试……”，而不是实际调用终端）。工具使用强制执行会注入系统提示词引导，让模型回归到实际调用工具的行为。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"` (默认) | 对匹配以下字符串的模型启用：`gpt`, `codex`, `gemini`, `gemma`, `grok`。对其他所有模型（Claude, DeepSeek, Qwen 等）禁用。 |
| `true` | 始终启用，不论模型。当你注意到当前模型只描述动作而不执行时很有用。 |
| `false` | 始终禁用，不论模型。 |
| `["gpt", "codex", "qwen", "llama"]` | 仅在模型名称包含所列出的任意子字符串（大小写不敏感）时启用。 |

### 它注入什么

当启用时，系统提示词中可能会添加三层引导：

1. **通用工具使用强制执行**（所有匹配的模型）——指示模型立即进行工具调用而不是描述意图，持续工作直到任务完成，并且绝不在一轮结束时承诺未来的动作。

2. **OpenAI 执行纪律**（仅 GPT 和 Codex 模型）——额外的引导，针对 GPT 特定的故障模式：放弃部分结果的工作，跳过必需的预查询步骤，凭空想象而不使用工具，以及在未验证的情况下宣告“完成”。

3. **Google 操作指导**（仅 Gemini 和 Gemma 模型）——简洁性、绝对路径、并行工具调用，以及编辑前验证模式。

这些对用户是透明的，只影响系统提示词。那些已经可靠使用工具的模型（如 Claude）不需要这种引导，所以 `"auto"` 会排除它们。

### 何时开启

如果你使用的模型不在默认的自动列表中，并且注意到它经常描述它*会*做什么而不是实际去做，请设置 `tool_use_enforcement: true` 或将模型子字符串添加到列表中：

```yaml
agent:
  tool_use_enforcement: ["gpt", "codex", "gemini", "grok", "my-custom-model"]
```

## TTS 配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "neutts"
  edge:
    voice: "en-US-AriaNeural"   # 322 种声音，74 种语言
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 用于覆盖 OpenAI 兼容的 TTS 端点
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

这同时控制着 `text_to_speech` 工具和语音模式中的语音回复（CLI 或消息网关中的 `/voice tts`）。

## 显示设置 {#display-settings}

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # 在消息网关中启用 `/verbose` 斜杠命令
  tool_progress_overrides: {}  # 按平台覆盖（见下文）
  interim_assistant_messages: true  # 网关：将中途完成的助手更新作为独立消息发送
  skin: default           # 内置或自定义 CLI 皮肤（参见 user-guide/features/skins）
  personality: "kawaii"  # 遗留的装饰性字段，在某些摘要中仍会显示
  compact: false          # 紧凑输出模式（更少的空白）
  resume_display: full    # full（恢复时显示之前的消息）| minimal（仅显示一行）
  bell_on_complete: false # Agent 完成时播放终端铃声（适用于长任务）
  show_reasoning: false   # 在每个回复上方显示模型推理/思考过程（可通过 /reasoning show|hide 切换）
  streaming: false        # 令牌到达时实时流式输出到终端（实时输出）
  show_cost: false        # 在 CLI 状态栏显示估算的美元成本
  tool_preview_length: 0  # 工具调用预览的最大字符数（0 = 无限制，显示完整路径/命令）
```

| 模式 | 你看到什么 |
|------|-------------|
| `off` | 静默——仅最终回复 |
| `new` | 仅当工具变更时显示工具指示 |
| `all` | 每个工具调用带有简短预览（默认） |
| `verbose` | 完整的参数、结果和调试日志 |

在 CLI 中，可以使用 `/verbose` 循环切换这些模式。要在消息平台（Telegram、Discord、Slack 等）中使用 `/verbose`，请在上面的 `display` 部分设置 `tool_progress_command: true`。该命令将循环切换模式并保存到配置。

### 按平台的进度覆盖

不同平台对详细程度有不同的需求。例如，Signal 无法编辑消息，所以每个进度更新都变成一条独立的消息——会很嘈杂。使用 `tool_progress_overrides` 来设置每个平台的模式：

```yaml
display:
  tool_progress: all          # 全局默认
  tool_progress_overrides:
    signal: 'off'             # Signal 上静默进度
    telegram: verbose         # Telegram 上详细进度
    slack: 'off'              # 共享 Slack 工作区中保持安静
```

没有覆盖的平台回退到全局 `tool_progress` 值。有效的平台键：`telegram`, `discord`, `slack`, `signal`, `whatsapp`, `matrix`, `mattermost`, `email`, `sms`, `homeassistant`, `dingtalk`, `feishu`, `wecom`, `weixin`, `bluebubbles`.

`interim_assistant_messages` 仅用于网关。启用后，Hermes 会将中途完成的助手更新作为独立的聊天消息发送。这独立于 `tool_progress`，并且不需要网关流式传输。

## 隐私

```yaml
privacy:
  redact_pii: false  # 从 LLM 上下文中去除个人可识别信息（仅限网关）
```

当 `redact_pii` 为 `true` 时，网关会在将系统提示词发送给 LLM 之前，在支持的平台上将个人可识别信息去除：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 上的用户 ID） | 哈希化为 `user_<12-char-sha256>` |
| 用户 ID | 哈希化为 `user_<12-char-sha256>` |
| 聊天 ID | 数字部分被哈希化，平台前缀保留（`telegram:<hash>`） |
| Home 频道 ID | 数字部分被哈希化 |
| 用户名称 / 用户名 | **不受影响**（用户选择，公开可见） |
**平台支持：** 用户信息脱敏适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 被排除在外，因为它们的提及系统（`<@user_id>`）需要在 LLM 上下文中使用真实 ID。

哈希值是确定性的——同一个用户总是映射到同一个哈希值，因此模型在群聊中仍然可以区分不同用户。路由和交付在内部使用原始值。

## 语音转文字 (STT)

```yaml
stt:
  provider: "local"            # "local" | "groq" | "openai"
  local:
    model: "base"              # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe
  # model: "whisper-1"         # 旧的备用键名仍然有效
```

提供商行为：

- `local` 使用在你机器上运行的 `faster-whisper`。请单独安装：`pip install faster-whisper`。
- `groq` 使用 Groq 的 Whisper 兼容端点，并读取 `GROQ_API_KEY`。
- `openai` 使用 OpenAI 语音 API，并读取 `VOICE_TOOLS_OPENAI_KEY`。

如果请求的提供商不可用，Hermes 会自动按以下顺序回退：`local` → `groq` → `openai`。

Groq 和 OpenAI 的模型覆盖由环境变量驱动：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

## 语音模式 (CLI)

```yaml
voice:
  record_key: "ctrl+b"         # CLI 内的按键通话键
  max_recording_seconds: 120    # 长时间录音的硬性停止限制
  auto_tts: false               # 当 `/voice on` 时自动启用语音回复
  silence_threshold: 200        # 语音检测的 RMS 阈值
  silence_duration: 3.0         # 自动停止前的静音持续时间（秒）
```

在 CLI 中使用 `/voice on` 启用麦克风模式，使用 `record_key` 开始/停止录音，使用 `/voice tts` 切换语音回复。有关端到端设置和平台特定行为，请参阅[语音模式](/user-guide/features/voice-mode)。

## 流式输出

将 token 实时流式传输到终端或消息平台，而不是等待完整响应。

### CLI 流式输出

```yaml
display:
  streaming: true         # 实时将 token 流式传输到终端
  show_reasoning: true    # 同时流式传输推理/思考 token（可选）
```

启用后，响应将在流式输出框中逐个 token 出现。工具调用仍会被静默捕获。如果提供商不支持流式输出，它会自动回退到正常显示。

### Gateway 流式输出 (Telegram, Discord, Slack)

```yaml
streaming:
  enabled: true           # 启用渐进式消息编辑
  transport: edit         # "edit"（渐进式消息编辑）或 "off"
  edit_interval: 0.3      # 消息编辑之间的间隔（秒）
  buffer_threshold: 40    # 强制触发编辑刷新前的字符数
  cursor: " ▉"            # 流式输出期间显示的光标
```

启用后，机器人会在第一个 token 到达时发送一条消息，然后随着更多 token 到达渐进式地编辑它。不支持消息编辑的平台（Signal、Email、Home Assistant）会在首次尝试时自动检测——流式输出会为该会话优雅地禁用，不会导致消息泛滥。

对于独立的自然中途助理更新（无需渐进式 token 编辑），请设置 `display.interim_assistant_messages: true`。

**溢出处理：** 如果流式输出的文本超出平台的消息长度限制（约 4096 字符），当前消息将被最终化，并自动开始一条新消息。

:::note
流式输出默认禁用。请在 `~/.hermes/config.yaml` 中启用它以尝试流式输出体验。
:::

## 群聊会话隔离

控制共享聊天是每个房间保持一个会话，还是每个参与者保持一个会话：

```yaml
group_sessions_per_user: true  # true = 在群组/频道中按用户隔离会话，false = 每个聊天一个共享会话
```

- `true` 是默认且推荐的设置。在 Discord 频道、Telegram 群组、Slack 频道等类似的共享环境中，当平台提供用户 ID 时，每个发送者都会获得自己的会话。
- `false` 恢复为旧的共享房间行为。如果你明确希望 Hermes 将一个频道视为一个协作对话，这可能很有用，但这也意味着用户共享上下文、token 成本和中断状态。
- 私聊不受影响。Hermes 仍会按聊天/DM ID 作为通常方式处理私聊。
- 子讨论无论如何都与其父频道隔离；使用 `true` 时，每个参与者也在子讨论中获得自己的会话。

有关行为细节和示例，请参阅[会话](/user-guide/sessions)和[Discord 指南](/user-guide/messaging/discord)。

## 未经授权的私聊行为

控制当未知用户发送私聊时 Hermes 的行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。Hermes 拒绝访问，但在私聊中回复一次性配对码。
- `ignore` 静默丢弃未经授权的私聊。
- 平台部分会覆盖全局默认值，因此你可以广泛保持配对启用，同时让某个平台更安静。

## 快捷命令 {#quick-commands}

定义自定义命令，这些命令运行 shell 命令而不调用 LLM——零 token 使用，即时执行。特别适用于消息平台（Telegram、Discord 等）进行快速服务器检查或实用脚本。

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

用法：在 CLI 或任何消息平台中输入 `/status`、`/disk`、`/update` 或 `/gpu`。命令在主机本地运行并直接返回输出——无需 LLM 调用，不消耗 token。

- **30 秒超时**——长时间运行的命令会被杀死并返回错误消息
- **优先级**——快捷命令在技能命令之前检查，因此你可以覆盖技能名称
- **自动补全**——快捷命令在调度时解析，不会显示在内置的斜杠命令自动补全表中
- **类型**——仅支持 `exec`（运行 shell 命令）；其他类型会显示错误
- **随处可用**——CLI、Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant

## 人为延迟

模拟消息平台中人机般的响应节奏：

```yaml
human_delay:
  mode: "off"                  # off | natural | custom
  min_ms: 800                  # 最小延迟（自定义模式）
  max_ms: 2500                 # 最大延迟（自定义模式）
```

## 代码执行

配置沙盒化的 Python 代码执行工具：

```yaml
code_execution:
  timeout: 300                 # 最大执行时间（秒）
  max_tool_calls: 50           # 代码执行内的最大工具调用次数
```

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

**后端选择：** 如果 `web.backend` 未设置，后端会根据可用的 API 密钥自动检测。如果只设置了 `EXA_API_KEY`，则使用 Exa。如果只设置了 `TAVILY_API_KEY`，则使用 Tavily。如果只设置了 `PARALLEL_API_KEY`，则使用 Parallel。否则 Firecrawl 是默认值。

**自托管 Firecrawl：** 设置 `FIRECRAWL_API_URL` 指向你自己的实例。设置自定义 URL 时，API 密钥变为可选（在服务器上设置 `USE_DB_AUTHENTICATION=false` 以禁用身份验证）。
**并行搜索模式：** 设置 `PARALLEL_SEARCH_MODE` 来控制搜索行为 — `fast`、`one-shot` 或 `agentic`（默认：`agentic`）。

## 浏览器

配置浏览器自动化行为：

```yaml
browser:
  inactivity_timeout: 120        # 空闲会话自动关闭前的秒数
  command_timeout: 30             # 浏览器命令（截图、导航等）的超时时间（秒）
  record_sessions: false         # 自动将浏览器会话录制为 WebM 视频到 ~/.hermes/browser_recordings/
  camofox:
    managed_persistence: false   # 为 true 时，Camofox 会话会在重启后保持 cookies/登录状态
```

浏览器工具集支持多个提供商。有关 Browserbase、Browser Use 和本地 Chrome CDP 设置的详细信息，请参阅[浏览器功能页面](/user-guide/features/browser)。

## 时区

使用 IANA 时区字符串覆盖服务器本地时区。影响日志中的时间戳、cron 调度和系统提示中的时间注入。

```yaml
timezone: "America/New_York"   # IANA 时区（默认："" = 服务器本地时间）
```

支持的值：任何 IANA 时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。留空或省略则使用服务器本地时间。

## Discord

为消息网关配置 Discord 特定行为：

```yaml
discord:
  require_mention: true          # 在服务器频道中需要 @提及 才响应
  free_response_channels: ""     # 逗号分隔的频道 ID 列表，在这些频道中机器人无需 @提及 即可响应每条消息
  auto_thread: true              # 在频道中被 @提及 时自动创建线程
```

- `require_mention` — 当为 `true`（默认）时，机器人仅在服务器频道中被 `@BotName` 提及时才响应。私信始终无需提及即可工作。
- `free_response_channels` — 逗号分隔的频道 ID 列表，在这些频道中机器人会响应每条消息，无需提及。
- `auto_thread` — 当为 `true`（默认）时，在频道中被提及会自动为对话创建一个线程，保持频道整洁（类似于 Slack 的线程功能）。

## 安全

执行前的安全扫描和密钥脱敏：

```yaml
security:
  redact_secrets: true           # 在工具输出和日志中对 API 密钥模式进行脱敏
  tirith_enabled: true           # 为终端命令启用 Tirith 安全扫描
  tirith_path: "tirith"          # tirith 二进制文件的路径（默认：$PATH 中的 "tirith"）
  tirith_timeout: 5              # 等待 tirith 扫描的超时时间（秒）
  tirith_fail_open: true         # 如果 tirith 不可用，则允许命令执行
  website_blocklist:             # 参见下面的网站阻止列表部分
    enabled: false
    domains: []
    shared_files: []
```

- `redact_secrets` — 在工具输出进入对话上下文和日志之前，自动检测并脱敏看起来像 API 密钥、令牌和密码的模式。
- `tirith_enabled` — 当为 `true` 时，终端命令在执行前会由 [Tirith](https://github.com/StackGuardian/tirith) 扫描，以检测潜在的危险操作。
- `tirith_path` — tirith 二进制文件的路径。如果 tirith 安装在非标准位置，请设置此项。
- `tirith_timeout` — 等待 tirith 扫描的最大秒数。如果扫描超时，命令将继续执行。
- `tirith_fail_open` — 当为 `true`（默认）时，如果 tirith 不可用或失败，则允许命令执行。设置为 `false` 可在 tirith 无法验证命令时阻止命令。

## 网站阻止列表

阻止 Agent 的网页和浏览器工具访问特定域名：

```yaml
security:
  website_blocklist:
    enabled: false               # 启用 URL 阻止（默认：false）
    domains:                     # 被阻止的域名模式列表
      - "*.internal.company.com"
      - "admin.example.com"
      - "*.local"
    shared_files:                # 从外部文件加载额外的规则
      - "/etc/hermes/blocked-sites.txt"
```

启用后，任何匹配被阻止域名模式的 URL 都会在网页或浏览器工具执行前被拒绝。这适用于 `web_search`、`web_extract`、`browser_navigate` 以及任何访问 URL 的工具。

域名规则支持：
- 精确域名：`admin.example.com`
- 通配符子域名：`*.internal.company.com`（阻止所有子域名）
- TLD 通配符：`*.local`

共享文件每行包含一个域名规则（空行和以 `#` 开头的注释行会被忽略）。缺失或无法读取的文件会记录警告，但不会禁用其他网页工具。

策略会缓存 30 秒，因此配置更改无需重启即可快速生效。

## 智能审批

控制 Hermes 如何处理潜在危险的命令：

```yaml
approvals:
  mode: manual   # manual | smart | off
```

| 模式 | 行为 |
|------|----------|
| `manual`（默认） | 在执行任何被标记的命令之前提示用户。在 CLI 中，显示交互式审批对话框。在消息传递中，排队等待待处理的审批请求。 |
| `smart` | 使用辅助 LLM 来评估被标记的命令是否真的危险。低风险命令会自动批准，并在会话级别保持持久性。真正有风险的命令会升级给用户处理。 |
| `off` | 跳过所有审批检查。相当于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

智能模式对于减少审批疲劳特别有用 — 它允许 Agent 在安全操作上更自主地工作，同时仍能捕获真正具有破坏性的命令。

:::warning
设置 `approvals.mode: off` 会禁用所有终端命令的安全检查。仅在受信任的沙盒环境中使用此设置。
:::

## 检查点

在执行破坏性文件操作之前自动创建文件系统快照。详情请参阅[检查点与回滚](/user-guide/checkpoints-and-rollback)。

```yaml
checkpoints:
  enabled: true                  # 启用自动检查点（也可用：hermes --checkpoints）
  max_snapshots: 50              # 每个目录保留的最大检查点数量
```

## 委托

为委托工具配置子 Agent 行为：

```yaml
delegation:
  # model: "google/gemini-3-flash-preview"  # 覆盖模型（空 = 继承父级）
  # provider: "openrouter"                  # 覆盖提供商（空 = 继承父级）
  # base_url: "http://localhost:1234/v1"    # 直接的 OpenAI 兼容端点（优先级高于 provider）
  # api_key: "local-key"                    # base_url 的 API 密钥（回退到 OPENAI_API_KEY）
```

**子 Agent 提供商:模型覆盖：** 默认情况下，子 Agent 继承父 Agent 的提供商和模型。设置 `delegation.provider` 和 `delegation.model` 可以将子 Agent 路由到不同的提供商:模型对 — 例如，当你的主 Agent 运行昂贵的推理模型时，为范围狭窄的子任务使用便宜/快速的模型。

**直接端点覆盖：** 如果你想要明显的自定义端点路径，请设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这将直接把子 Agent 发送到该 OpenAI 兼容端点，并且优先级高于 `delegation.provider`。如果省略 `delegation.api_key`，Hermes 仅回退到 `OPENAI_API_KEY`。

委托提供商使用与 CLI/网关启动相同的凭据解析机制。支持所有已配置的提供商：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。设置提供商后，系统会自动解析正确的基础 URL、API 密钥和 API 模式 — 无需手动配置凭据。

**优先级：** 配置中的 `delegation.base_url` → 配置中的 `delegation.provider` → 父级提供商（继承）。配置中的 `delegation.model` → 父级模型（继承）。仅设置 `model` 而不设置 `provider` 只会更改模型名称，同时保留父级的凭据（对于在同一提供商内切换模型，如 OpenRouter，很有用）。

## 澄清

配置澄清提示行为：

```yaml
clarify:
  timeout: 120                 # 等待用户澄清响应的秒数
```

## 上下文文件 (SOUL.md, AGENTS.md)

Hermes 使用两种不同的上下文作用域：

| 文件 | 用途 | 作用域 |
|------|---------|-------|
| `SOUL.md` | **主 Agent 身份** — 定义 Agent 是谁（系统提示中的槽位 #1） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定指令（最高优先级） | 向上遍历到 git 根目录 |
| `AGENTS.md` | 项目特定指令，编码规范 | 递归目录遍历 |
| `CLAUDE.md` | Claude Code 上下文文件（也会被检测） | 仅工作目录 |
| `.cursorrules` | Cursor IDE 规则（也会被检测） | 仅工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被检测） | 仅工作目录 |
- **SOUL.md** 是 Agent 的核心身份文件。它占据系统提示词中的第 1 个位置，完全替代内置的默认身份。编辑此文件可以完全自定义 Agent 的身份。
- 如果 SOUL.md 缺失、为空或无法加载，Hermes 将回退到内置的默认身份。
- **项目上下文文件采用优先级系统** —— 只加载一种类型（首次匹配优先）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。SOUL.md 始终独立加载。
- **AGENTS.md** 是层级式的：如果子目录也有 AGENTS.md 文件，所有文件的内容会被合并。
- 如果 `SOUL.md` 不存在，Hermes 会自动生成一个默认版本。
- 所有加载的上下文文件总字符数上限为 20,000，并采用智能截断。

另请参阅：
- [个性与 SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)

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
