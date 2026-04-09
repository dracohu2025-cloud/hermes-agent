---
sidebar_position: 2
title: "配置"
description: "配置 Hermes Agent — config.yaml、提供商、模型、API 密钥等"
---

# 配置

所有设置均存储在 `~/.hermes/` 目录下，方便访问。

## 目录结构

```text
~/.hermes/
├── config.yaml     # 设置（模型、终端、TTS、压缩等）
├── .env            # API 密钥和机密信息
├── auth.json       # OAuth 提供商凭据（Nous Portal 等）
├── SOUL.md         # 主要 Agent 身份（系统提示词中的第 1 个槽位）
├── memories/       # 持久化记忆（MEMORY.md, USER.md）
├── skills/         # Agent 创建的技能（通过 skill_manage 工具管理）
├── cron/           # 定时任务
├── sessions/       # 网关会话
└── logs/           # 日志（errors.log, gateway.log — 机密信息会自动脱敏）
```

## 管理配置

```bash
hermes config              # 查看当前配置
hermes config edit         # 在编辑器中打开 config.yaml
hermes config set KEY VAL  # 设置特定值
hermes config check        # 检查缺失的选项（更新后使用）
hermes config migrate      # 以交互方式添加缺失的选项

# 示例：
hermes config set model anthropic/claude-opus-4
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...  # 保存到 .env
```

:::tip
`hermes config set` 命令会自动将值路由到正确的文件中 —— API 密钥会保存到 `.env`，其他所有内容则保存到 `config.yaml`。
:::

## 配置优先级

设置按以下顺序解析（优先级从高到低）：

1. **CLI 参数** — 例如 `hermes chat --model anthropic/claude-sonnet-4`（单次调用覆盖）
2. **`~/.hermes/config.yaml`** — 所有非机密设置的主要配置文件
3. **`~/.hermes/.env`** — 环境变量的后备方案；**必须**用于机密信息（API 密钥、令牌、密码）
4. **内置默认值** — 当未设置其他内容时使用的硬编码安全默认值

:::info 经验法则
机密信息（API 密钥、机器人令牌、密码）放入 `.env`。其他所有内容（模型、终端后端、压缩设置、内存限制、工具集）放入 `config.yaml`。当两者同时设置时，对于非机密设置，`config.yaml` 具有最高优先级。
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

支持在单个值中进行多次引用：`url: "${HOST}:${PORT}"`。如果引用的变量未设置，占位符将保持原样（`${UNDEFINED_VAR}` 会原样保留）。仅支持 `${VAR}` 语法 —— 不支持直接使用 `$VAR`。

有关 AI 提供商设置（OpenRouter、Anthropic、Copilot、自定义端点、自托管 LLM、后备模型等），请参阅 [AI 提供商](/integrations/providers)。

## 终端后端配置

Hermes 支持六种终端后端。每种后端决定了 Agent 的 shell 命令实际执行的位置 —— 你的本地机器、Docker 容器、通过 SSH 连接的远程服务器、Modal 云沙箱、Daytona 工作区或 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | singularity
  cwd: "."          # 工作目录 ("." = 本地的当前目录，"/root" = 容器内)
  timeout: 180      # 单条命令超时时间（秒）
  env_passthrough: []  # 转发到沙箱执行的环境变量名（终端 + execute_code）
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Singularity 后端的容器镜像
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Modal 后端的容器镜像
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Daytona 后端的容器镜像
```

对于 Modal 和 Daytona 等云沙箱，`container_persistent: true` 意味着 Hermes 将尝试在沙箱重建后保留文件系统状态。它不保证同一个实时沙箱、PID 空间或后台进程在稍后仍然运行。

### 后端概览

| 后端 | 命令运行位置 | 隔离性 | 适用场景 |
|---------|-------------------|-----------|----------|
| **local** | 直接在你的机器上 | 无 | 开发、个人使用 |
| **docker** | Docker 容器 | 完全（命名空间、cap-drop） | 安全沙箱、CI/CD |
| **ssh** | 通过 SSH 连接的远程服务器 | 网络边界 | 远程开发、高性能硬件 |
| **modal** | Modal 云沙箱 | 完全（云虚拟机） | 临时云计算、评估 |
| **daytona** | Daytona 工作区 | 完全（云容器） | 托管云开发环境 |
| **singularity** | Singularity/Apptainer 容器 | 命名空间 (--containall) | HPC 集群、共享机器 |

### Local 后端

默认后端。命令直接在你的机器上运行，没有任何隔离。无需特殊设置。

```yaml
terminal:
  backend: local
```

:::warning
Agent 拥有与你的用户账户相同的文件系统访问权限。请使用 `hermes tools` 禁用你不希望使用的工具，或切换到 Docker 进行沙箱隔离。
:::

### Docker 后端

在启用了安全加固（丢弃所有 capabilities、禁止权限提升、PID 限制）的 Docker 容器内运行命令。

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # 将启动目录挂载到 /workspace
  docker_forward_env:              # 转发到容器内的环境变量
    - "GITHUB_TOKEN"
  docker_volumes:                  # 主机目录挂载
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"   # :ro 表示只读

  # 资源限制
  container_cpu: 1                 # CPU 核心数 (0 = 不限制)
  container_memory: 5120           # MB (0 = 不限制)
  container_disk: 51200            # MB (需要 XFS+pquota 上的 overlay2)
  container_persistent: true       # 在会话间持久化 /workspace 和 /root
```

**要求：** 已安装并运行 Docker Desktop 或 Docker Engine。Hermes 会探测 `$PATH` 以及常见的 macOS 安装位置（`/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用包）。

**容器生命周期：** 每个会话都会启动一个长寿命容器（`docker run -d ... sleep 2h`）。命令通过带有登录 shell 的 `docker exec` 运行。清理时，容器会被停止并移除。

**安全加固：**
- `--cap-drop ALL`，仅重新添加 `DAC_OVERRIDE`、`CHOWN`、`FOWNER`
- `--security-opt no-new-privileges`
- `--pids-limit 256`
- 为 `/tmp` (512MB)、`/var/tmp` (256MB)、`/run` (64MB) 设置大小限制的 tmpfs

**凭据转发：** `docker_forward_env` 中列出的环境变量首先从你的 shell 环境中解析，然后从 `~/.hermes/.env` 中解析。技能也可以声明 `required_environment_variables`，这些变量会自动合并。

### SSH 后端

通过 SSH 在远程服务器上运行命令。使用 ControlMaster 进行连接复用（5 分钟空闲保持连接）。默认启用持久化 shell —— 状态（工作目录、环境变量）在命令间保持不变。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # 保持长寿命的 bash 会话（默认：true）
```

**所需环境变量：**

```bash
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=ubuntu
```

**可选：**

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `TERMINAL_SSH_PORT` | `22` | SSH 端口 |
| `TERMINAL_SSH_KEY` | (系统默认) | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | `true` | 启用持久化 shell |

**工作原理：** 在初始化时使用 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 进行连接。持久化 shell 在远程主机上保持一个 `bash -l` 进程存活，并通过临时文件进行通信。需要 `stdin_data` 或 `sudo` 的命令会自动回退到单次执行模式。

### Modal 后端

在 [Modal](https://modal.com) 云沙箱中运行命令。每个任务都会获得一个具有可配置 CPU、内存和磁盘的隔离虚拟机。文件系统可以在会话间进行快照/恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB (5GB)
  container_disk: 51200            # MB (50GB)
  container_persistent: true       # 快照/恢复文件系统
```
**必需项：** `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` 环境变量，或 `~/.modal.toml` 配置文件。

**持久化：** 启用后，沙盒文件系统会在清理时进行快照，并在下次会话时恢复。快照记录在 `~/.hermes/modal_snapshots.json` 中。这仅保留文件系统状态，不保留实时进程、PID 空间或后台作业。

**凭据文件：** 会自动从 `~/.hermes/` 挂载（如 OAuth 令牌等），并在每次命令执行前同步。

### Daytona 后端

在 [Daytona](https://daytona.io) 管理的工作区中运行命令。支持停止/恢复以实现持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB → 转换为 GiB
  container_disk: 10240            # MB → 转换为 GiB（最大 10 GiB）
  container_persistent: true       # 停止/恢复而非删除
```

**必需项：** `DAYTONA_API_KEY` 环境变量。

**持久化：** 启用后，沙盒在清理时会停止（而非删除），并在下次会话时恢复。沙盒名称遵循 `hermes-{task_id}` 的模式。

**磁盘限制：** Daytona 强制执行 10 GiB 的上限。超过此限制的请求会被截断并发出警告。

### Singularity/Apptainer 后端

在 [Singularity/Apptainer](https://apptainer.org) 容器中运行命令。专为无法使用 Docker 的 HPC 集群和共享机器设计。

```yaml
terminal:
  backend: singularity
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"
  container_cpu: 1                 # CPU 核心数
  container_memory: 5120           # MB
  container_persistent: true       # 可写覆盖层在会话间持久存在
```

**要求：** `$PATH` 中必须包含 `apptainer` 或 `singularity` 二进制文件。

**镜像处理：** Docker URL (`docker://...`) 会自动转换为 SIF 文件并缓存。现有的 `.sif` 文件会被直接使用。

**暂存目录：** 解析顺序为：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent`（HPC 惯例）→ `~/.hermes/sandboxes/singularity`。

**隔离性：** 使用 `--containall --no-home` 实现完全的命名空间隔离，且不会挂载宿主机的 home 目录。

### 常见终端后端问题

如果终端命令立即失败，或者终端工具被报告为已禁用：

- **Local** — 无特殊要求。入门时最安全的默认选项。
- **Docker** — 运行 `docker version` 验证 Docker 是否正常工作。如果失败，请修复 Docker 或执行 `hermes config set terminal.backend local`。
- **SSH** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER`。如果缺少其中任何一个，Hermes 会记录明确的错误。
- **Modal** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml`。运行 `hermes doctor` 进行检查。
- **Daytona** — 需要 `DAYTONA_API_KEY`。Daytona SDK 会处理服务器 URL 配置。
- **Singularity** — 需要 `$PATH` 中有 `apptainer` 或 `singularity`。这在 HPC 集群中很常见。

如有疑问，请将 `terminal.backend` 改回 `local`，并先验证命令是否能在本地运行。

### Docker 卷挂载

使用 Docker 后端时，`docker_volumes` 允许你与容器共享宿主机目录。每个条目使用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # 读写（默认）
    - "/home/user/datasets:/data:ro"              # 只读
    - "/home/user/outputs:/outputs"               # Agent 写入，你读取
```

这适用于：
- **向 Agent 提供文件**（数据集、配置、参考代码）
- **从 Agent 接收文件**（生成的代码、报告、导出内容）
- **共享工作区**，你和 Agent 可以访问相同的文件

也可以通过环境变量设置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组）。

### Docker 凭据转发

默认情况下，Docker 终端会话不会继承任意宿主机凭据。如果你需要在容器内使用特定令牌，请将其添加到 `terminal.docker_forward_env`。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 会首先从你当前的 shell 解析列出的每个变量，如果之前通过 `hermes config set` 保存过，则会回退到 `~/.hermes/.env`。

:::warning
`docker_forward_env` 中列出的任何内容对容器内运行的命令都是可见的。请仅转发你认为可以暴露给终端会话的凭据。
:::

### 可选：将启动目录挂载到 `/workspace`

Docker 沙盒默认保持隔离。除非你明确选择，否则 Hermes **不会**将你当前的宿主机工作目录传递到容器中。

在 `config.yaml` 中启用它：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用后：
- 如果你从 `~/projects/my-app` 启动 Hermes，该宿主机目录会被绑定挂载到 `/workspace`
- Docker 后端会在 `/workspace` 中启动
- 文件工具和终端命令都能看到同一个挂载的项目

禁用时，`/workspace` 保持为沙盒所有，除非你通过 `docker_volumes` 明确挂载。

安全权衡：
- `false` 保留了沙盒边界
- `true` 让沙盒可以直接访问你启动 Hermes 的目录

仅当你确实希望容器处理实时宿主机文件时才使用此选项。

### 持久化 Shell

默认情况下，每个终端命令都在其自己的子进程中运行——工作目录、环境变量和 shell 变量在命令之间会重置。当启用**持久化 shell** 时，单个长生命周期的 bash 进程会在 `execute()` 调用之间保持活跃，以便状态在命令之间得以保留。

这对于 **SSH 后端**最有用，因为它还消除了每个命令的连接开销。持久化 shell 在 **SSH 中默认启用**，在本地后端中默认禁用。

```yaml
terminal:
  persistent_shell: true   # 默认值 — 为 SSH 启用持久化 shell
```

禁用方法：

```bash
hermes config set terminal.persistent_shell false
```

**在命令间持久化的内容：**
- 工作目录（`cd /tmp` 对下一条命令依然有效）
- 导出的环境变量（`export FOO=bar`）
- Shell 变量（`MY_VAR=hello`）

**优先级：**

| 层级 | 变量 | 默认值 |
|-------|----------|---------|
| 配置 | `terminal.persistent_shell` | `true` |
| SSH 覆盖 | `TERMINAL_SSH_PERSISTENT` | 遵循配置 |
| 本地覆盖 | `TERMINAL_LOCAL_PERSISTENT` | `false` |

各后端的环境变量具有最高优先级。如果你也想在本地后端使用持久化 shell：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
需要 `stdin_data` 或 sudo 的命令会自动回退到一次性模式，因为持久化 shell 的 stdin 已经被 IPC 协议占用。
:::

有关各后端的详细信息，请参阅 [代码执行](features/code-execution.md) 和 [README 的终端部分](features/tools.md)。

## 技能设置 {#skill-settings}

技能可以通过其 `SKILL.md` 的 frontmatter 声明自己的配置设置。这些是非敏感值（路径、偏好设置、域设置），存储在 `config.yaml` 的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    wiki:
      path: ~/wiki          # 由 llm-wiki 技能使用
```

**技能设置的工作原理：**

- `hermes config migrate` 会扫描所有已启用的技能，查找未配置的设置，并提示你进行配置
- `hermes config show` 会在“Skill Settings”下显示所有技能设置及其所属的技能
- 当技能加载时，其解析后的配置值会自动注入到技能上下文中

**手动设置值：**

```bash
hermes config set skills.config.wiki.path ~/my-research-wiki
```

有关在自己的技能中声明配置设置的详细信息，请参阅 [创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

## 内存配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
```
## 文件读取安全性

控制单次 `read_file` 调用可以返回的内容量。如果读取内容超过限制，系统会拒绝该请求，并提示 Agent 使用 `offset` 和 `limit` 来指定更小的范围。这可以防止单次读取压缩后的 JS 包或大型数据文件时，导致上下文窗口溢出。

```yaml
file_read_max_chars: 100000  # 默认值 — 约 25-35K tokens
```

如果你使用的模型拥有较大的上下文窗口，且经常需要读取大文件，可以调高此值。对于小上下文模型，可以调低此值以保持读取效率：

```yaml
# 大上下文模型 (200K+)
file_read_max_chars: 200000

# 小型本地模型 (16K 上下文)
file_read_max_chars: 30000
```

Agent 还会自动对文件读取进行去重——如果同一文件区域被读取两次且文件未发生更改，系统会返回一个轻量级的存根（stub），而不是重新发送内容。此机制会在上下文压缩时重置，以便 Agent 在内容被总结归纳后能够重新读取文件。

## Git 工作树隔离

启用隔离的 git 工作树，以便在同一个仓库中并行运行多个 Agent：

```yaml
worktree: true    # 始终创建工作树（等同于 hermes -w）
# worktree: false # 默认值 — 仅在传入 -w 标志时创建
```

启用后，每个 CLI 会话都会在 `.worktrees/` 下创建一个带有独立分支的全新工作树。Agent 可以编辑文件、提交、推送和创建 PR，而不会相互干扰。干净的工作树会在退出时被移除；脏工作树则会保留以供手动恢复。

你还可以通过仓库根目录下的 `.worktreeinclude` 文件列出需要复制到工作树中的被 git 忽略的文件：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩 {#context-compression}

Hermes 会自动压缩长对话，以确保其保持在模型的上下文窗口内。压缩总结器是一个独立的 LLM 调用——你可以将其指向任何提供商或端点。

所有压缩设置均位于 `config.yaml` 中（不支持环境变量）。

### 完整参考

```yaml
compression:
  enabled: true                                     # 开启/关闭压缩
  threshold: 0.50                                   # 在达到上下文限制的此百分比时进行压缩
  target_ratio: 0.20                                # 保留作为近期尾部信息的阈值比例
  protect_last_n: 20                                # 保持不压缩的最少近期消息数
  summary_model: "google/gemini-3-flash-preview"    # 用于总结的模型
  summary_provider: "auto"                          # 提供商: "auto", "openrouter", "nous", "codex", "main" 等
  summary_base_url: null                            # 自定义 OpenAI 兼容端点（会覆盖提供商设置）
```

### 常见配置

**默认（自动检测）——无需配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
使用第一个可用的提供商（OpenRouter → Nous → Codex）配合 Gemini Flash。

**强制指定特定提供商**（基于 OAuth 或 API-key）：
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

### 三个参数的交互方式

| `summary_provider` | `summary_base_url` | 结果 |
|---------------------|---------------------|--------|
| `auto` (默认) | 未设置 | 自动检测最佳可用提供商 |
| `nous` / `openrouter` / 等 | 未设置 | 强制使用该提供商，并使用其认证 |
| 任意值 | 已设置 | 直接使用自定义端点（忽略提供商） |

`summary_model` 必须支持至少与主模型一样大的上下文长度，因为它接收的是对话的完整中间部分进行压缩。

## 迭代预算压力

当 Agent 正在处理包含大量工具调用的复杂任务时，它可能会在不知不觉中耗尽迭代预算（默认：90 次）。预算压力功能会在模型接近限制时自动发出警告：

| 阈值 | 等级 | 模型看到的内容 |
|-----------|-------|---------------------|
| **70%** | 提醒 | `[BUDGET: 63/90. 27 iterations left. Start consolidating.]` |
| **90%** | 警告 | `[BUDGET WARNING: 81/90. Only 9 left. Respond NOW.]` |

警告会被注入到最后一个工具结果的 JSON 中（作为 `_budget_warning` 字段），而不是作为单独的消息——这可以保留提示词缓存，且不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # 每个对话轮次的最大迭代次数（默认：90）
```

预算压力功能默认开启。Agent 会自然地将警告视为工具结果的一部分，从而促使其在迭代次数耗尽前整合工作并给出响应。

## 上下文压力警告

与迭代预算压力不同，上下文压力用于跟踪对话距离**压缩阈值**（即触发上下文压缩以总结旧消息的点）还有多近。这有助于你和 Agent 了解对话何时变得过长。

| 进度 | 等级 | 发生的情况 |
|----------|-------|-------------|
| 达到阈值的 **≥ 60%** | 信息 | CLI 显示青色进度条；网关发送通知 |
| 达到阈值的 **≥ 85%** | 警告 | CLI 显示加粗黄色进度条；网关警告即将进行压缩 |

在 CLI 中，上下文压力显示为工具输出流中的进度条：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台上，会发送纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果禁用了自动压缩，警告会提示你上下文可能会被截断。

上下文压力是自动触发的——无需配置。它仅作为面向用户的通知，不会修改消息流，也不会向模型的上下文中注入任何内容。

## 凭据池策略

当你拥有同一提供商的多个 API 密钥或 OAuth 令牌时，可以配置轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # 均匀轮询密钥
  anthropic: least_used      # 始终选择使用次数最少的密钥
```

选项包括：`fill_first`（默认）、`round_robin`、`least_used`、`random`。完整文档请参阅 [凭据池](/user-guide/features/credential-pools)。

## 辅助模型 {#auxiliary-models}

Hermes 使用轻量级的“辅助”模型来处理图像分析、网页总结和浏览器截图分析等辅助任务。默认情况下，这些任务通过自动检测使用 **Gemini Flash**——你无需进行任何配置。

### 通用配置模式

Hermes 中的每个模型槽位——辅助任务、压缩、回退——都使用相同的三个参数：

| 键 | 作用 | 默认值 |
|-----|-------------|---------|
| `provider` | 用于认证和路由的提供商 | `"auto"` |
| `model` | 要请求的模型 | 提供商的默认值 |
| `base_url` | 自定义 OpenAI 兼容端点（覆盖提供商） | 未设置 |

当设置了 `base_url` 时，Hermes 会忽略提供商并直接调用该端点（使用 `api_key` 或 `OPENAI_API_KEY` 进行认证）。当仅设置 `provider` 时，Hermes 会使用该提供商内置的认证和基础 URL。

辅助任务可用的提供商包括：`auto`、`openrouter`、`nous`、`codex`、`copilot`、`anthropic`、`main`、`zai`、`kimi-coding`、`minimax`，以及在 [提供商注册表](/reference/environment-variables) 中注册的任何提供商，或 `custom_providers` 列表中定义的任何自定义提供商（例如 `provider: "beans"`）。

:::warning `"main"` 仅用于辅助任务
`"main"` 提供商选项的意思是“使用我的主 Agent 所使用的任何提供商”——它仅在 `auxiliary:`、`compression:` 和 `fallback_model:` 配置中有效。它**不是**顶级 `model.provider` 设置的有效值。如果你使用自定义的 OpenAI 兼容端点，请在 `model:` 部分设置 `provider: custom`。有关所有主模型提供商选项，请参阅 [AI 提供商](/integrations/providers)。
:::
### 辅助配置完整参考

```yaml
auxiliary:
  # 图像分析 (vision_analyze 工具 + 浏览器截图)
  vision:
    provider: "auto"           # "auto", "openrouter", "nous", "codex", "main" 等
    model: ""                  # 例如 "openai/gpt-4o", "google/gemini-2.5-flash"
    base_url: ""               # 自定义 OpenAI 兼容端点 (会覆盖 provider)
    api_key: ""                # base_url 对应的 API 密钥 (若留空则回退使用 OPENAI_API_KEY)
    timeout: 30                # 秒 — LLM API 调用超时；若使用较慢的本地视觉模型，请调大此值
    download_timeout: 30       # 秒 — 图像 HTTP 下载超时；若网络较慢，请调大此值

  # 网页摘要 + 浏览器页面文本提取
  web_extract:
    provider: "auto"
    model: ""                  # 例如 "google/gemini-2.5-flash"
    base_url: ""
    api_key: ""
    timeout: 360               # 秒 (6分钟) — 每次尝试 LLM 摘要的超时时间

  # 危险命令审批分类器
  approval:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30                # 秒

  # 上下文压缩超时 (与 compression.* 配置分开)
  compression:
    timeout: 120               # 秒 — 压缩过程会对长对话进行摘要，需要更多时间

  # 会话搜索 — 摘要过往会话匹配结果
  session_search:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # 技能中心 — 技能匹配与搜索
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

  # 内存刷新 — 为持久化内存摘要对话内容
  flush_memories:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
```

:::tip
每个辅助任务都有一个可配置的 `timeout`（单位为秒）。默认值：vision 为 30 秒，web_extract 为 360 秒，approval 为 30 秒，compression 为 120 秒。如果你在辅助任务中使用较慢的本地模型，请调大这些值。Vision 还有一个单独的 `download_timeout`（默认 30 秒）用于 HTTP 图像下载——如果网络连接较慢或使用自托管图像服务器，请调大此值。
:::

:::info
上下文压缩有其独立的顶级 `compression:` 块，包含 `summary_provider`、`summary_model` 和 `summary_base_url` ——请参阅上方的 [Context Compression](#context-compression)。回退模型使用 `fallback_model:` 块 ——请参阅 [Fallback Model](/integrations/providers#fallback-model)。这三者都遵循相同的 provider/model/base_url 模式。
:::

### 更改视觉模型

若要使用 GPT-4o 而不是 Gemini Flash 进行图像分析：

```yaml
auxiliary:
  vision:
    model: "openai/gpt-4o"
```

或者通过环境变量（在 `~/.hermes/.env` 中）：

```bash
AUXILIARY_VISION_MODEL=openai/gpt-4o
```

### 提供商选项

这些选项适用于**辅助任务配置**（`auxiliary:`、`compression:`、`fallback_model:`），而不适用于你的主 `model.provider` 设置。

| 提供商 | 描述 | 要求 |
|----------|-------------|-------------|
| `"auto"` | 可用的最佳选项（默认）。Vision 会尝试 OpenRouter → Nous → Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter — 路由到任何模型（Gemini、GPT-4o、Claude 等） | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth (ChatGPT 账号)。支持视觉 (gpt-5.3-codex)。 | `hermes model` → Codex |
| `"main"` | 使用你当前激活的自定义/主端点。这可以来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY`，或者通过 `hermes model` / `config.yaml` 保存的自定义端点。适用于 OpenAI、本地模型或任何 OpenAI 兼容的 API。**仅限辅助任务 — 不适用于 `model.provider`。** | 自定义端点凭据 + base URL |

### 常见设置

**使用直接自定义端点**（对于本地/自托管 API，这比 `provider: "main"` 更清晰）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`，因此这是将辅助任务路由到特定端点最明确的方式。对于直接端点覆盖，Hermes 会使用配置的 `api_key` 或回退到 `OPENAI_API_KEY`；它不会为该自定义端点复用 `OPENROUTER_API_KEY`。

**使用 OpenAI API 密钥进行视觉分析：**
```yaml
# 在 ~/.hermes/.env 中:
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # 或者使用 "gpt-4o-mini" 以降低成本
```

**使用 OpenRouter 进行视觉分析**（路由到任何模型）：
```yaml
auxiliary:
  vision:
    provider: "openrouter"
    model: "openai/gpt-4o"      # 或者 "google/gemini-2.5-flash" 等
```

**使用 Codex OAuth**（ChatGPT Pro/Plus 账号 — 无需 API 密钥）：
```yaml
auxiliary:
  vision:
    provider: "codex"     # 使用你的 ChatGPT OAuth 令牌
    # model 默认为 gpt-5.3-codex (支持视觉)
```

**使用本地/自托管模型：**
```yaml
auxiliary:
  vision:
    provider: "main"      # 使用你当前激活的自定义端点
    model: "my-local-model"
```

`provider: "main"` 会使用 Hermes 用于常规对话的任何提供商——无论是已命名的自定义提供商（例如 `beans`）、内置提供商（如 `openrouter`），还是旧版的 `OPENAI_BASE_URL` 端点。

:::tip
如果你将 Codex OAuth 用作主模型提供商，视觉功能会自动生效——无需额外配置。Codex 已包含在视觉功能的自动检测链中。
:::

:::warning
**视觉功能需要多模态模型。** 如果你设置了 `provider: "main"`，请确保你的端点支持多模态/视觉——否则图像分析将会失败。
:::

### 环境变量（旧版）

辅助模型也可以通过环境变量进行配置。不过，`config.yaml` 是首选方法——它更易于管理，并支持包括 `base_url` 和 `api_key` 在内的所有选项。

| 设置 | 环境变量 |
|---------|---------------------|
| Vision 提供商 | `AUXILIARY_VISION_PROVIDER` |
| Vision 模型 | `AUXILIARY_VISION_MODEL` |
| Vision 端点 | `AUXILIARY_VISION_BASE_URL` |
| Vision API 密钥 | `AUXILIARY_VISION_API_KEY` |
| Web extract 提供商 | `AUXILIARY_WEB_EXTRACT_PROVIDER` |
| Web extract 模型 | `AUXILIARY_WEB_EXTRACT_MODEL` |
| Web extract 端点 | `AUXILIARY_WEB_EXTRACT_BASE_URL` |
| Web extract API 密钥 | `AUXILIARY_WEB_EXTRACT_API_KEY` |

压缩和回退模型设置仅支持在 `config.yaml` 中配置。

:::tip
运行 `hermes config` 查看你当前的辅助模型设置。只有与默认值不同的覆盖项才会显示。
:::

## 推理强度 (Reasoning Effort)

控制模型在响应前进行多少“思考”：

```yaml
agent:
  reasoning_effort: ""   # 空值 = 中等 (默认)。选项: xhigh (最大), high, medium, low, minimal, none
```

当未设置时（默认），推理强度默认为“中等”——这是一个在大多数任务中表现良好的平衡水平。设置一个值会覆盖默认值——更高的推理强度在复杂任务上能提供更好的结果，但会消耗更多的 token 并增加延迟。

你也可以在运行时通过 `/reasoning` 命令更改推理强度：

```
/reasoning           # 显示当前的强度级别和显示状态
/reasoning high      # 将推理强度设置为高
/reasoning none      # 禁用推理
/reasoning show      # 在每次响应上方显示模型思考过程
/reasoning hide      # 隐藏模型思考过程
```

## 工具使用强制 (Tool-Use Enforcement)

某些模型（尤其是 GPT 系列）有时会将预期的操作描述为文本，而不是进行工具调用。工具使用强制功能会注入引导信息，将模型拉回实际调用工具的轨道上。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"` (默认) | 对 GPT 模型 (`gpt-`, `openai/gpt-`) 启用，对所有其他模型禁用。 |
| `true` | 对所有模型始终启用。 |
| `false` | 始终禁用。 |
| `["gpt-", "o1-", "custom-model"]` | 仅对名称包含所列子字符串的模型启用。 |
启用后，系统提示词会包含引导信息，提醒模型执行实际的工具调用，而不是描述它打算做什么。这对用户是透明的，且对已经能可靠使用工具的模型没有影响。

## TTS 配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "neutts"
  edge:
    voice: "en-US-AriaNeural"   # 322 种音色，74 种语言
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 覆盖 OpenAI 兼容的 TTS 端点
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

此配置同时控制 `text_to_speech` 工具以及语音模式下的口述回复（通过 CLI 或消息网关中的 `/voice tts` 命令）。

## 显示设置 {#display-settings}

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # 在消息网关中启用 /verbose 斜杠命令
  tool_progress_overrides: {}  # 各平台的覆盖设置（见下文）
  skin: default           # 内置或自定义 CLI 皮肤（见 user-guide/features/skins）
  personality: "kawaii"  # 旧版装饰性字段，仍会在某些摘要中显示
  compact: false          # 紧凑输出模式（减少空白）
  resume_display: full    # full（恢复时显示之前的消息） | minimal（仅显示一行）
  bell_on_complete: false # 当 Agent 完成任务时播放终端提示音（适合长任务）
  show_reasoning: false   # 在每次回复上方显示模型的推理/思考过程（通过 /reasoning show|hide 切换）
  streaming: false        # 实时将 token 流式传输到终端（实时输出）
  show_cost: false        # 在 CLI 状态栏显示预估的 $ 成本
  tool_preview_length: 0  # 工具调用预览的最大字符数（0 = 无限制，显示完整路径/命令）
```

| 模式 | 显示内容 |
|------|-------------|
| `off` | 静默 — 仅显示最终回复 |
| `new` | 仅在工具变更时显示工具指示器 |
| `all` | 显示每次工具调用及简短预览（默认） |
| `verbose` | 显示完整参数、结果和调试日志 |

在 CLI 中，可以使用 `/verbose` 在这些模式间循环切换。若要在消息平台（Telegram、Discord、Slack 等）中使用 `/verbose`，请在上述 `display` 部分设置 `tool_progress_command: true`。该命令随后会循环切换模式并保存到配置中。

### 各平台进度覆盖设置

不同平台对详细程度的需求不同。例如，Signal 无法编辑消息，因此每次进度更新都会变成一条独立的消息，显得非常嘈杂。使用 `tool_progress_overrides` 可以设置各平台的特定模式：

```yaml
display:
  tool_progress: all          # 全局默认值
  tool_progress_overrides:
    signal: 'off'             # 在 Signal 上关闭进度显示
    telegram: verbose         # 在 Telegram 上显示详细进度
    slack: 'off'              # 在共享的 Slack 工作区保持安静
```

未设置覆盖的平台将回退到全局 `tool_progress` 值。有效的平台键名包括：`telegram`, `discord`, `slack`, `signal`, `whatsapp`, `matrix`, `mattermost`, `email`, `sms`, `homeassistant`, `dingtalk`, `feishu`, `wecom`, `bluebubbles`。

## 隐私

```yaml
privacy:
  redact_pii: false  # 从 LLM 上下文中剥离 PII（仅限网关）
```

当 `redact_pii` 为 `true` 时，网关会在将系统提示词发送给 LLM 之前，在支持的平台上对个人身份信息（PII）进行脱敏处理：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 上的用户 ID） | 哈希处理为 `user_<12-char-sha256>` |
| 用户 ID | 哈希处理为 `user_<12-char-sha256>` |
| 聊天 ID | 数字部分哈希处理，保留平台前缀 (`telegram:<hash>`) |
| 家庭频道 ID | 数字部分哈希处理 |
| 用户名 / 昵称 | **不受影响**（用户自选，公开可见） |

**平台支持：** 脱敏适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 被排除在外，因为它们的提及系统（`<@user_id>`）需要在 LLM 上下文中保留真实 ID。

哈希是确定性的——同一用户始终映射到同一哈希，因此模型仍然可以在群聊中区分不同用户。路由和投递在内部使用原始值。

## 语音转文字 (STT)

```yaml
stt:
  provider: "local"            # "local" | "groq" | "openai"
  local:
    model: "base"              # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe
  # model: "whisper-1"         # 旧版回退键，仍可使用
```

提供商行为：

- `local` 使用运行在你机器上的 `faster-whisper`。请通过 `pip install faster-whisper` 单独安装。
- `groq` 使用 Groq 的 Whisper 兼容端点，并读取 `GROQ_API_KEY`。
- `openai` 使用 OpenAI 语音 API，并读取 `VOICE_TOOLS_OPENAI_KEY`。

如果请求的提供商不可用，Hermes 会按以下顺序自动回退：`local` → `groq` → `openai`。

Groq 和 OpenAI 的模型覆盖通过环境变量设置：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

## 语音模式 (CLI)

```yaml
voice:
  record_key: "ctrl+b"         # CLI 内的按键通话快捷键
  max_recording_seconds: 120    # 长录音的强制停止时间
  auto_tts: false               # 当 /voice on 时自动启用口述回复
  silence_threshold: 200        # 用于语音检测的 RMS 阈值
  silence_duration: 3.0         # 自动停止前的静音时长（秒）
```

在 CLI 中使用 `/voice on` 启用麦克风模式，使用 `record_key` 开始/停止录音，使用 `/voice tts` 切换口述回复。有关端到端设置和各平台特定行为，请参阅 [语音模式](/user-guide/features/voice-mode)。

## 流式传输

在 token 到达时将其流式传输到终端或消息平台，而不是等待完整回复。

### CLI 流式传输

```yaml
display:
  streaming: true         # 实时将 token 流式传输到终端
  show_reasoning: true    # 同时流式传输推理/思考过程的 token（可选）
```

启用后，回复会以逐个 token 的形式出现在流式传输框中。工具调用仍会静默捕获。如果提供商不支持流式传输，它会自动回退到正常显示模式。

### 网关流式传输 (Telegram, Discord, Slack)

```yaml
streaming:
  enabled: true           # 启用渐进式消息编辑
  transport: edit         # "edit"（渐进式消息编辑）或 "off"
  edit_interval: 0.3      # 消息编辑之间的间隔（秒）
  buffer_threshold: 40    # 强制刷新编辑前的字符数
  cursor: " ▉"            # 流式传输期间显示的游标
```

启用后，机器人会在第一个 token 到达时发送一条消息，并随着更多 token 的到达逐步编辑该消息。不支持消息编辑的平台（Signal、Email、Home Assistant）会在首次尝试时被自动检测到——该会话的流式传输将被优雅地禁用，且不会产生消息洪流。

**溢出处理：** 如果流式传输的文本超过了平台的单条消息长度限制（约 4096 字符），当前消息将结束，并自动开始一条新消息。

:::note
流式传输默认处于禁用状态。请在 `~/.hermes/config.yaml` 中启用它以体验流式传输效果。
:::

## 群聊会话隔离

控制共享聊天是保持每个房间一个对话，还是每个参与者一个对话：

```yaml
group_sessions_per_user: true  # true = 群组/频道中按用户隔离，false = 每个聊天一个共享会话
```

- `true` 是默认且推荐的设置。在 Discord 频道、Telegram 群组、Slack 频道及类似的共享上下文中，当平台提供用户 ID 时，每个发送者都会获得自己的会话。
- `false` 会恢复为旧的共享房间行为。如果你明确希望 Hermes 将频道视为一个协作对话，这会很有用，但这也意味着用户会共享上下文、token 成本和中断状态。
- 私聊不受影响。Hermes 仍会像往常一样按聊天/私聊 ID 对私聊进行区分。
- 无论哪种设置，线程都会与父频道保持隔离；设置为 `true` 时，每个参与者在线程内也会拥有自己的会话。
有关行为详情和示例，请参阅 [Sessions](/user-guide/sessions) 和 [Discord 指南](/user-guide/messaging/discord)。

## 未经授权的 DM 行为

控制当未知用户发送私信（DM）时 Hermes 的行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `pair` 是默认值。Hermes 会拒绝访问，但在私信中回复一个一次性配对码。
- `ignore` 会静默丢弃未经授权的私信。
- 平台配置会覆盖全局默认值，因此你可以保持大范围的配对功能，同时让某个特定平台保持安静。

## 快捷命令 {#quick-commands}

定义自定义命令，无需调用 LLM 即可运行 Shell 命令——零 Token 消耗，即时执行。这在消息平台（Telegram、Discord 等）中进行快速服务器检查或运行实用脚本时特别有用。

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

用法：在 CLI 或任何消息平台中输入 `/status`、`/disk`、`/update` 或 `/gpu`。命令会在主机上本地运行并直接返回输出——无需 LLM 调用，不消耗 Token。

- **30 秒超时** — 长时间运行的命令会被终止并返回错误消息
- **优先级** — 快捷命令的检查优先级高于技能命令，因此你可以覆盖技能名称
- **自动补全** — 快捷命令在分发时解析，不会显示在内置的斜杠命令自动补全表中
- **类型** — 仅支持 `exec`（运行 Shell 命令）；其他类型会显示错误
- **随处可用** — CLI、Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant

## 人类延迟

在消息平台中模拟类似人类的响应节奏：

```yaml
human_delay:
  mode: "off"                  # off | natural | custom
  min_ms: 800                  # 最小延迟（自定义模式）
  max_ms: 2500                 # 最大延迟（自定义模式）
```

## 代码执行

配置沙盒 Python 代码执行工具：

```yaml
code_execution:
  timeout: 300                 # 最大执行时间（秒）
  max_tool_calls: 50           # 代码执行内的最大工具调用次数
```

## 网络搜索后端

`web_search`、`web_extract` 和 `web_crawl` 工具支持四种后端提供商。在 `config.yaml` 中或通过 `hermes tools` 配置后端：

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

**后端选择：** 如果未设置 `web.backend`，后端将根据可用的 API 密钥自动检测。如果仅设置了 `EXA_API_KEY`，则使用 Exa。如果仅设置了 `TAVILY_API_KEY`，则使用 Tavily。如果仅设置了 `PARALLEL_API_KEY`，则使用 Parallel。否则默认使用 Firecrawl。

**自托管 Firecrawl：** 设置 `FIRECRAWL_API_URL` 指向你自己的实例。设置自定义 URL 后，API 密钥变为可选（在服务器上设置 `USE_DB_AUTHENTICATION=false` 以禁用身份验证）。

**Parallel 搜索模式：** 设置 `PARALLEL_SEARCH_MODE` 以控制搜索行为 — `fast`、`one-shot` 或 `agentic`（默认：`agentic`）。

## 浏览器

配置浏览器自动化行为：

```yaml
browser:
  inactivity_timeout: 120        # 空闲会话自动关闭前的秒数
  command_timeout: 30             # 浏览器命令（截图、导航等）的超时秒数
  record_sessions: false         # 将浏览器会话自动录制为 WebM 视频并保存至 ~/.hermes/browser_recordings/
  camofox:
    managed_persistence: false   # 若为 true，Camofox 会话将在重启后保留 Cookie/登录状态
```

浏览器工具集支持多个提供商。有关 Browserbase、Browser Use 和本地 Chrome CDP 设置的详细信息，请参阅 [浏览器功能页面](/user-guide/features/browser)。

## 时区

使用 IANA 时区字符串覆盖服务器本地时区。这会影响日志中的时间戳、Cron 调度以及系统提示词中的时间注入。

```yaml
timezone: "America/New_York"   # IANA 时区（默认："" = 服务器本地时间）
```

支持的值：任何 IANA 时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。留空或省略则使用服务器本地时间。

## Discord

为消息网关配置 Discord 特定的行为：

```yaml
discord:
  require_mention: true          # 在服务器频道中响应时是否需要 @mention
  free_response_channels: ""     # 机器人无需 @mention 即可响应的频道 ID（逗号分隔）
  auto_thread: true              # 在频道中被 @mention 时自动创建线程
```

- `require_mention` — 当为 `true`（默认）时，机器人仅在被 `@BotName` 提及的情况下才会在服务器频道中响应。私信始终无需提及即可工作。
- `free_response_channels` — 机器人对每条消息都进行响应且无需提及的频道 ID 列表（逗号分隔）。
- `auto_thread` — 当为 `true`（默认）时，在频道中提及机器人会自动为对话创建线程，从而保持频道整洁（类似于 Slack 的线程功能）。

## 安全性

执行前的安全扫描和敏感信息脱敏：

```yaml
security:
  redact_secrets: true           # 在工具输出和日志中脱敏 API 密钥模式
  tirith_enabled: true           # 启用 Tirith 安全扫描以检查终端命令
  tirith_path: "tirith"          # tirith 二进制文件路径（默认：$PATH 中的 "tirith"）
  tirith_timeout: 5              # 等待 tirith 扫描超时的秒数
  tirith_fail_open: true         # 如果 tirith 不可用，允许执行命令
  website_blocklist:             # 见下方的“网站黑名单”部分
    enabled: false
    domains: []
    shared_files: []
```

- `redact_secrets` — 在工具输出进入对话上下文和日志之前，自动检测并脱敏看起来像 API 密钥、Token 和密码的模式。
- `tirith_enabled` — 当为 `true` 时，终端命令在执行前会由 [Tirith](https://github.com/StackGuardian/tirith) 进行扫描，以检测潜在的危险操作。
- `tirith_path` — tirith 二进制文件的路径。如果 tirith 安装在非标准位置，请设置此项。
- `tirith_timeout` — 等待 tirith 扫描的最长秒数。如果扫描超时，命令将继续执行。
- `tirith_fail_open` — 当为 `true`（默认）时，如果 tirith 不可用或失败，命令仍可执行。设置为 `false` 可在 tirith 无法验证命令时阻止其执行。

## 网站黑名单 {#website-blocklist}

阻止 Agent 的 Web 和浏览器工具访问特定域名：

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

启用后，任何匹配被阻止域名模式的 URL 在 Web 或浏览器工具执行前都会被拒绝。这适用于 `web_search`、`web_extract`、`browser_navigate` 以及任何访问 URL 的工具。

域名规则支持：
- 精确域名：`admin.example.com`
- 通配符子域名：`*.internal.company.com`（阻止所有子域名）
- TLD 通配符：`*.local`

共享文件每行包含一条域名规则（空行和 `#` 注释会被忽略）。缺失或不可读的文件会记录警告，但不会禁用其他 Web 工具。

策略会缓存 30 秒，因此配置更改无需重启即可生效。

## 智能审批
控制 Hermes 处理潜在危险命令的方式：

```yaml
approvals:
  mode: manual   # manual | smart | off
```

| 模式 | 行为 |
|------|----------|
| `manual` (默认) | 在执行任何被标记的命令前提示用户。在 CLI 中，显示交互式批准对话框。在消息传递中，将批准请求加入队列。 |
| `smart` | 使用辅助 LLM 评估被标记的命令是否真的危险。低风险命令会自动批准，并在会话级别保持持久化。真正有风险的命令会升级给用户处理。 |
| `off` | 跳过所有批准检查。等同于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

Smart 模式对于减少“批准疲劳”特别有用——它让 Agent 在执行安全操作时更加自主，同时仍能拦截真正具有破坏性的命令。

:::warning
设置 `approvals.mode: off` 会禁用所有终端命令的安全检查。仅在受信任的沙盒环境中使用此设置。
:::

## Checkpoints (检查点)

在执行破坏性文件操作前自动进行文件系统快照。详情请参阅 [Checkpoints & Rollback](/user-guide/checkpoints-and-rollback)。

```yaml
checkpoints:
  enabled: true                  # 启用自动检查点 (也可使用: hermes --checkpoints)
  max_snapshots: 50              # 每个目录保留的最大检查点数量
```


## Delegation (委派)

配置 delegate 工具的 subagent 行为：

```yaml
delegation:
  # model: "google/gemini-3-flash-preview"  # 覆盖模型 (留空 = 继承父级)
  # provider: "openrouter"                  # 覆盖提供商 (留空 = 继承父级)
  # base_url: "http://localhost:1234/v1"    # 直接使用兼容 OpenAI 的端点 (优先级高于 provider)
  # api_key: "local-key"                    # base_url 的 API 密钥 (回退至 OPENAI_API_KEY)
```

**Subagent 的 provider:model 覆盖：** 默认情况下，subagent 会继承父 Agent 的 provider 和 model。设置 `delegation.provider` 和 `delegation.model` 可以将 subagent 路由到不同的 provider:model 对——例如，在主 Agent 运行昂贵的推理模型时，为范围较小的子任务使用廉价/快速的模型。

**直接端点覆盖：** 如果你需要使用自定义端点，请设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这会将 subagent 直接发送到该兼容 OpenAI 的端点，且优先级高于 `delegation.provider`。如果省略 `delegation.api_key`，Hermes 将仅回退至 `OPENAI_API_KEY`。

委派提供商使用与 CLI/网关启动时相同的凭据解析方式。支持所有已配置的提供商：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。设置提供商后，系统会自动解析正确的 base URL、API 密钥和 API 模式——无需手动配置凭据。

**优先级：** 配置中的 `delegation.base_url` → 配置中的 `delegation.provider` → 父级提供商（继承）。配置中的 `delegation.model` → 父级模型（继承）。仅设置 `model` 而不设置 `provider` 只会更改模型名称，同时保留父级的凭据（这在同一提供商内切换模型时非常有用，例如 OpenRouter）。

## Clarify (澄清)

配置澄清提示的行为：

```yaml
clarify:
  timeout: 120                 # 等待用户澄清响应的秒数
```

## Context Files (上下文文件：SOUL.md, AGENTS.md)

Hermes 使用两种不同的上下文范围：

| 文件 | 用途 | 范围 |
|------|---------|-------|
| `SOUL.md` | **主 Agent 身份** — 定义 Agent 是谁（系统提示词中的第 1 位） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定指令（最高优先级） | 遍历至 git 根目录 |
| `AGENTS.md` | 项目特定指令、编码规范 | 递归目录遍历 |
| `CLAUDE.md` | Claude Code 上下文文件（也会被检测） | 仅工作目录 |
| `.cursorrules` | Cursor IDE 规则（也会被检测） | 仅工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被检测） | 仅工作目录 |

- **SOUL.md** 是 Agent 的主要身份。它占据系统提示词中的第 1 位，完全替换内置的默认身份。编辑它可以完全自定义 Agent 的角色。
- 如果 SOUL.md 缺失、为空或无法加载，Hermes 将回退至内置的默认身份。
- **项目上下文文件使用优先级系统** — 仅加载一种类型（先匹配者胜）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。SOUL.md 始终独立加载。
- **AGENTS.md** 是分层的：如果子目录中也有 AGENTS.md，它们会被合并。
- 如果不存在 `SOUL.md`，Hermes 会自动生成一个默认文件。
- 所有加载的上下文文件均限制在 20,000 字符以内，并进行智能截断。

另请参阅：
- [Personality & SOUL.md](/user-guide/features/personality)
- [Context Files](/user-guide/features/context-files)

## Working Directory (工作目录)

| 上下文 | 默认值 |
|---------|---------|
| **CLI (`hermes`)** | 运行命令所在的当前目录 |
| **消息传递网关** | 主目录 `~` (可通过 `MESSAGING_CWD` 覆盖) |
| **Docker / Singularity / Modal / SSH** | 容器或远程机器内的用户主目录 |

覆盖工作目录：
```bash
# 在 ~/.hermes/.env 或 ~/.hermes/config.yaml 中：
MESSAGING_CWD=/home/myuser/projects    # 网关会话
TERMINAL_CWD=/workspace                # 所有终端会话
```
