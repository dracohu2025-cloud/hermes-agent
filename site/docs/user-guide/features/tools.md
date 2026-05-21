---
sidebar_position: 1
title: "工具与工具集"
description: "Hermes Agent 工具概览——哪些可用、工具集如何工作以及终端后端"
---

<a id="tools-toolsets"></a>
# 工具与工具集

工具是扩展 Agent 能力的函数。它们被组织成逻辑上的**工具集**，可以按平台启用或禁用。

<a id="available-tools"></a>
## 可用工具

Hermes 内置了丰富的工具注册表，涵盖网页搜索、浏览器自动化、终端执行、文件编辑、记忆、委派、RL 训练、消息投递、Home Assistant 等。

:::note
**Honcho 跨会话记忆** 作为内存提供者插件（`plugins/memory/honcho/`）提供，而非内置工具集。安装方法请参见[插件](./plugins.md)。
:::

高层分类：

| 类别 | 示例 | 描述 |
|----------|----------|-------------|
| **Web** | `web_search`, `web_extract` | 搜索网页并提取页面内容。 |
| **X 搜索** | `x_search` | 通过 xAI 内置的 `x_search` 响应工具搜索 X（Twitter）帖子和线程——需要 xAI 凭证（SuperGrok OAuth 或 `XAI_API_KEY`）；默认关闭，通过 `hermes tools` → 🐦 X (Twitter) Search 选择启用。 |
| **终端与文件** | `terminal`, `process`, `read_file`, `patch` | 执行命令和操作文件。 |
| **浏览器** | `browser_navigate`, `browser_snapshot`, `browser_vision` | 交互式浏览器自动化，支持文本和视觉。 |
| **媒体** | `vision_analyze`, `image_generate`, `video_generate`, `video_analyze`, `text_to_speech` | 多模态分析和生成。`video_generate` 和 `video_analyze` 需要选择启用（通过 `hermes tools` 或 `--toolsets` 添加 `video_gen` / `video` 工具集）。 |
| **Agent 编排** | `todo`, `clarify`, `execute_code`, `delegate_task` | 计划、澄清、代码执行和子 Agent 委派。 |
| **记忆与回顾** | `memory`, `session_search` | 持久记忆和会话搜索。 |
| **自动化与投递** | `cronjob`, `send_message` | 定时任务（支持创建/列出/更新/暂停/恢复/运行/删除操作），以及出站消息投递。 |
| **集成** | `ha_*`, MCP 服务器工具, `rl_*` | Home Assistant、MCP、RL 训练及其他集成。 |

权威的代码生成注册表，请参见[内置工具参考](/reference/tools-reference)和[工具集参考](/reference/toolsets-reference)。

:::tip Nous 工具网关
<a id="nous-tool-gateway"></a>
付费的 [Nous Portal](https://portal.nousresearch.com) 用户可以通过 **[Tool Gateway](tool-gateway.md)** 使用网页搜索、图片生成、TTS 和浏览器自动化——无需单独 API 密钥。运行 `hermes model` 启用它，或通过 `hermes tools` 配置单个工具。
:::

<a id="using-toolsets"></a>
## 使用工具集

```bash
# 使用特定的工具集
hermes chat --toolsets "web,terminal"

# 查看所有可用工具
hermes tools

# 按平台配置工具（交互式）
hermes tools
```

常见的工具集包括：`web`、`search`、`terminal`、`file`、`browser`、`vision`、`image_gen`、`moa`、`skills`、`tts`、`todo`、`memory`、`session_search`、`cronjob`、`code_execution`、`delegation`、`clarify`、`homeassistant`、`messaging`、`spotify`、`discord`、`discord_admin`、`debugging`、`safe` 和 `rl`。
请参见[工具集参考](/reference/toolsets-reference)获取完整列表，包括 `hermes-cli`、`hermes-telegram` 等平台预设，以及 `mcp-&lt;server&gt;` 等动态 MCP 工具集。

<a id="terminal-backends"></a>
## 终端后端

终端工具可以在不同环境中执行命令：

| 后端 | 描述 | 使用场景 |
|---------|-------------|----------|
| `local` | 在你的机器上运行（默认） | 开发、受信任的任务 |
| `docker` | 隔离的容器 | 安全性、可复现性 |
| `ssh` | 远程服务器 | 沙箱化，防止 Agent 修改自身代码 |
| `singularity` | HPC 容器 | 集群计算、无根模式 |
| `modal` | 云端执行 | 无服务器、弹性扩展 |
| `daytona` | 云端沙箱工作区 | 持久化远程开发环境 |
| `vercel_sandbox` | Vercel Sandbox 云端微虚拟机 | 云端执行，支持快照持久化文件系统 |

<a id="configuration"></a>
### 配置

```yaml
# 在 ~/.hermes/config.yaml 中
terminal:
  backend: local    # 或: docker, ssh, singularity, modal, daytona, vercel_sandbox
  cwd: "."          # 工作目录
  timeout: 180      # 命令超时时间（秒）
```

<a id="docker-backend"></a>
### Docker 后端

```yaml
terminal:
  backend: docker
  docker_image: python:3.11-slim
```

**整个进程共用一个持久化容器。** Hermes 在首次使用时启动一个长期运行的容器（`docker run -d ... sleep 2h`），然后通过 `docker exec` 将所有终端、文件和 `execute_code` 调用路由到同一个容器中。工作目录变更、已安装的软件包、环境调整以及写入 `/workspace` 的文件，在 Hermes 进程的整个生命周期内（包括跨越 `/new`、`/reset` 和 `delegate_task` 子 Agents 的调用）都会持续保留。Hermes 关闭时容器会被停止并移除。

这意味着 Docker 后端的行为类似于一个持久化的沙箱虚拟机，而不是每条命令都重新创建一个新容器。如果你执行了一次 `pip install foo`，那么在本次会话的剩余时间内它都可用。如果你执行了 `cd /workspace/project`，后续的 `ls` 调用都能看到该目录。完整的生命周期详情以及控制 `/workspace` 和 `/root` 在 Hermes 重启后是否保留的 `container_persistent` 标志，请参见[配置 → Docker 后端](../configuration.md#docker-backend)。

<a id="ssh-backend"></a>
### SSH 后端

推荐用于安全性——Agent 无法修改自身代码：

```yaml
terminal:
  backend: ssh
```
```bash
# 在 ~/.hermes/.env 中设置凭据
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=myuser
TERMINAL_SSH_KEY=~/.ssh/id_rsa
```

<a id="singularity-apptainer"></a>
### Singularity/Apptainer

```bash
# 为并行工作器预构建 SIF
apptainer build ~/python.sif docker://python:3.11-slim

# 配置
hermes config set terminal.backend singularity
hermes config set terminal.singularity_image ~/python.sif
```

<a id="modal-serverless-cloud"></a>
### Modal（无服务器云端）

```bash
uv pip install modal
modal setup
hermes config set terminal.backend modal
```

<a id="vercel-sandbox"></a>
### Vercel Sandbox

```bash
pip install 'hermes-agent[vercel]'
hermes config set terminal.backend vercel_sandbox
hermes config set terminal.vercel_runtime node24
```
请使用 `VERCEL_TOKEN`、`VERCEL_PROJECT_ID` 和 `VERCEL_TEAM_ID` 三个环境变量进行身份验证。这种访问令牌配置是 Hermes 在 Render、Railway、Docker 及类似主机上进行部署和常规长时间运行进程的推荐方式。支持的运行时环境包括 `node24`、`node22` 和 `python3.13`；Hermes 默认使用 `/vercel/sandbox` 作为远程工作区根目录。

对于一次性本地开发，Hermes 也接受短期有效的 Vercel OIDC 令牌：

```bash
VERCEL_OIDC_TOKEN="$(vc project token <project-name>)" hermes chat
```

在已关联的 Vercel 项目目录中：

```bash
VERCEL_OIDC_TOKEN="$(vc project token)" hermes chat
```

当 `container_persistent: true` 时，Hermes 会使用 Vercel 快照来保留同一任务中沙箱重建时的文件系统状态。这可以包括沙箱内由 Hermes 同步的凭据、技能和缓存文件。快照不会保留正在运行的进程、PID 空间或相同的实时沙箱标识。

后台终端命令使用 Hermes 通用的非本地进程流程：在沙箱存活期间，通过常规进程工具执行生成、轮询、等待、日志记录和终止操作，但 Hermes 在清理或重启后不提供原生的 Vercel 分离进程恢复功能。

请将 `container_disk` 保持未设置状态，或使用共享默认值 `51200`；Vercel Sandbox 不支持自定义磁盘大小，否则会导致诊断/后端创建失败。

<a id="container-resources"></a>
### 容器资源

为所有容器后端配置 CPU、内存、磁盘和持久化：

```yaml
terminal:
  backend: docker  # 或 singularity、modal、daytona、vercel_sandbox
  container_cpu: 1              # CPU 核心数（默认：1）
  container_memory: 5120        # 内存，单位 MB（默认：5GB）
  container_disk: 51200         # 磁盘，单位 MB（默认：50GB）
  container_persistent: true    # 跨会话持久化文件系统（默认：true）
```

当 `container_persistent: true` 时，已安装的包、文件和配置会在会话之间保留。

<a id="container-security"></a>
### 容器安全

所有容器后端都启用了安全加固：

- 只读根文件系统（Docker）
- 丢弃所有 Linux 能力
- 无权限提升
- PID 限制（256 个进程）
- 完全命名空间隔离
- 通过卷实现持久化工作区，而非可写根层

Docker 可以选择通过 `terminal.docker_forward_env` 接收显式的环境变量允许列表，但转发的变量对容器内的命令可见，应视为已暴露给该会话。

<a id="background-process-management"></a>
## 后台进程管理

启动后台进程并进行管理：

```python
terminal(command="pytest -v tests/", background=true)
# 返回：{"session_id": "proc_abc123", "pid": 12345}

# 然后使用进程工具进行管理：
process(action="list")       # 显示所有正在运行的进程
process(action="poll", session_id="proc_abc123")   # 检查状态
process(action="wait", session_id="proc_abc123")   # 阻塞直到完成
process(action="log", session_id="proc_abc123")    # 完整输出
process(action="kill", session_id="proc_abc123")   # 终止
process(action="write", session_id="proc_abc123", data="y")  # 发送输入
```
PTY 模式（`pty=true`）支持 Codex 和 Claude Code 等交互式 CLI 工具。

<a id="sudo-support"></a>
## Sudo 支持

如果命令需要 sudo，系统会提示你输入密码（在会话期间会缓存）。或者，你也可以在 `~/.hermes/.env` 中设置 `SUDO_PASSWORD`。

:::warning
在消息平台上，如果 sudo 执行失败，输出中会包含一条提示，建议将 `SUDO_PASSWORD` 添加到 `~/.hermes/.env` 中。
:::
