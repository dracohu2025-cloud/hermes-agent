---
sidebar_position: 1
title: "工具与工具集"
description: "Hermes Agent 工具概览——可用工具、工具集工作原理以及终端后端"
---

# 工具与工具集 {#tools-toolsets}

工具是扩展 Agent 能力的函数。它们按逻辑组织成**工具集**，可根据平台启用或禁用。

## 可用工具 {#available-tools}

Hermes 自带一个庞大的内置工具注册表，涵盖网络搜索、浏览器自动化、终端执行、文件编辑、记忆、委托、RL 训练、消息投递、Home Assistant 等。

:::note
**Honcho 跨会话记忆**作为记忆提供者插件（`plugins/memory/honcho/`）提供，而非内置工具集。安装请参考[插件](./plugins.md)。
:::

高层次类别：

| 类别 | 示例 | 描述 |
|----------|----------|-------------|
| **Web** | `web_search`、`web_extract` | 搜索网络并提取页面内容。 |
| **终端与文件** | `terminal`、`process`、`read_file`、`patch` | 执行命令并操作文件。 |
| **浏览器** | `browser_navigate`、`browser_snapshot`、`browser_vision` | 支持文本和视觉的交互式浏览器自动化。 |
| **媒体** | `vision_analyze`、`image_generate`、`text_to_speech` | 多模态分析与生成。 |
| **Agent 编排** | `todo`、`clarify`、`execute_code`、`delegate_task` | 规划、澄清、代码执行以及子 Agent 委托。 |
| **记忆与回忆** | `memory`、`session_search` | 持久化记忆与会话搜索。 |
| **自动化与投递** | `cronjob`、`send_message` | 带有创建/列出/更新/暂停/恢复/运行/删除操作的定时任务，以及外发消息投递。 |
| **集成** | `ha_*`、MCP 服务器工具、`rl_*` | Home Assistant、MCP、RL 训练及其他集成。 |

关于权威的代码派生注册表，请参见[内置工具参考](/reference/tools-reference)和[工具集参考](/reference/toolsets-reference)。

:::tip Nous 工具网关
付费的 [Nous Portal](https://portal.nousresearch.com) 用户可以通过 **[工具网关](tool-gateway.md)** 使用网络搜索、图像生成、TTS 和浏览器自动化——无需额外 API 密钥。运行 `hermes model` 启用，或用 `hermes tools` 单独配置每个工具。
<a id="nous-tool-gateway"></a>
:::

## 使用工具集 {#using-toolsets}

```bash
# 使用指定的工具集
hermes chat --toolsets "web,terminal"

# 查看所有可用工具
hermes tools

# 按平台配置工具（交互式）
hermes tools
```

常见的工具集包括 `web`、`search`、`terminal`、`file`、`browser`、`vision`、`image_gen`、`moa`、`skills`、`tts`、`todo`、`memory`、`session_search`、`cronjob`、`code_execution`、`delegation`、`clarify`、`homeassistant`、`messaging`、`spotify`、`discord`、`discord_admin`、`debugging`、`safe` 和 `rl`。

完整列表请参见[工具集参考](/reference/toolsets-reference)，包括平台预设（如 `hermes-cli`、`hermes-telegram`）以及动态 MCP 工具集（如 `mcp-&lt;server&gt;`）。

## 终端后端 {#terminal-backends}

终端工具可以在不同环境中执行命令：

| 后端 | 描述 | 使用场景 |
|---------|-------------|----------|
| `local` | 在本地机器上运行（默认） | 开发、受信任的任务 |
| `docker` | 隔离容器 | 安全、可重现 |
| `ssh` | 远程服务器 | 沙箱化、让 Agent 远离自身代码 |
| `singularity` | HPC 容器 | 集群计算、无 root |
| `modal` | 云端执行 | 无服务器、可扩展 |
| `daytona` | 云端沙箱工作区 | 持久化远程开发环境 |
| `vercel_sandbox` | Vercel Sandbox 云端微虚拟机 | 云端执行，支持基于快照的文件系统持久化 |
### 配置 {#configuration}

```yaml
# In ~/.hermes/config.yaml
terminal:
  backend: local    # 或: docker, ssh, singularity, modal, daytona, vercel_sandbox
  cwd: "."          # 工作目录
  timeout: 180      # 命令超时时间（秒）
```

### Docker 后端 {#docker-backend}

```yaml
terminal:
  backend: docker
  docker_image: python:3.11-slim
```

### SSH 后端 {#ssh-backend}

推荐用于安全场景——Agent 无法修改自身代码：

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

### Singularity/Apptainer {#singularity-apptainer}

```bash
# 为并行工作器预构建 SIF
apptainer build ~/python.sif docker://python:3.11-slim

# 配置
hermes config set terminal.backend singularity
hermes config set terminal.singularity_image ~/python.sif
```

### Modal（无服务器云） {#modal-serverless-cloud}

```bash
uv pip install modal
modal setup
hermes config set terminal.backend modal
```

### Vercel Sandbox {#vercel-sandbox}

```bash
pip install 'hermes-agent[vercel]'
hermes config set terminal.backend vercel_sandbox
hermes config set terminal.vercel_runtime node24
```

使用 `VERCEL_TOKEN`、`VERCEL_PROJECT_ID` 和 `VERCEL_TEAM_ID` 三个环境变量进行身份验证。这种访问令牌设置是部署以及在 Render、Railway、Docker 及类似主机上运行长时间 Hermes 进程的推荐方式。支持的运行时为 `node24`、`node22` 和 `python3.13`；Hermes 默认将 `/vercel/sandbox` 作为远程工作区根目录。

对于一次性本地开发，Hermes 也接受短期有效的 Vercel OIDC 令牌：

```bash
VERCEL_OIDC_TOKEN="$(vc project token <project-name>)" hermes chat
```

从已关联的 Vercel 项目目录中：

```bash
VERCEL_OIDC_TOKEN="$(vc project token)" hermes chat
```

当 `container_persistent: true` 时，Hermes 使用 Vercel 快照来保留同一任务中沙箱重建之间的文件系统状态。这可以包括沙箱内 Hermes 同步的凭据、技能和缓存文件。快照不会保留活动进程、PID 空间或相同的活动沙箱标识。

后台终端命令使用 Hermes 的通用非本地进程流程：在沙箱存活期间，通过常规进程工具执行 spawn、poll、wait、log 和 kill 操作，但 Hermes 在清理或重启后不提供原生的 Vercel 分离进程恢复功能。

请将 `container_disk` 保持未设置或使用共享默认值 `51200`；Vercel Sandbox 不支持自定义磁盘大小，否则会导致诊断/后端创建失败。

### 容器资源 {#container-resources}

为所有容器后端配置 CPU、内存、磁盘和持久性：

```yaml
terminal:
  backend: docker  # 或 singularity, modal, daytona, vercel_sandbox
  container_cpu: 1              # CPU 核心数（默认：1）
  container_memory: 5120        # 内存（MB，默认：5GB）
  container_disk: 51200         # 磁盘（MB，默认：50GB）
  container_persistent: true    # 跨会话持久化文件系统（默认：true）
```

当 `container_persistent: true` 时，已安装的包、文件和配置会在会话之间保留。
### 容器安全 {#container-security}

所有容器后端均通过安全加固运行：

- 只读根文件系统（Docker）
- 已删除所有 Linux 能力
- 无权限提升
- PID 限制（256 个进程）
- 完全命名空间隔离
- 通过卷实现持久化工作空间，而非可写根层

Docker 可以选择通过 `terminal.docker_forward_env` 接收显式的环境变量允许列表，但转发的变量对容器内的命令可见，应视为已暴露给该会话。

## 后台进程管理 {#background-process-management}

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

## Sudo 支持 {#sudo-support}

如果命令需要 sudo，系统会提示您输入密码（在会话期间缓存）。或者，在 `~/.hermes/.env` 中设置 `SUDO_PASSWORD`。

:::warning
在消息平台上，如果 sudo 失败，输出中会包含一条提示，建议将 `SUDO_PASSWORD` 添加到 `~/.hermes/.env` 中。
:::
