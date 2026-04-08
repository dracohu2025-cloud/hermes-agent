---
sidebar_position: 1
title: "工具与工具集"
description: "Hermes Agent 工具概览 —— 可用工具、工具集工作原理以及终端后端"
---

# 工具与工具集

工具是扩展 Agent 能力的函数。它们被组织成逻辑上的**工具集 (toolsets)**，可以根据不同平台进行启用或禁用。

## 可用工具

Hermes 内置了一个广泛的工具注册表，涵盖了网页搜索、浏览器自动化、终端执行、文件编辑、记忆、任务委派、强化学习（RL）训练、消息投递、Home Assistant 等。

:::note
**Honcho 跨会话记忆**是作为记忆提供者插件 (`plugins/memory/honcho/`) 提供的，而不是内置工具集。安装方法请参阅 [Plugins](./plugins.md)。
:::

高级分类：

| 分类 | 示例 | 描述 |
|----------|----------|-------------|
| **Web** | `web_search`, `web_extract` | 搜索网页并提取页面内容。 |
| **终端与文件** | `terminal`, `process`, `read_file`, `patch` | 执行命令和操作文件。 |
| **浏览器** | `browser_navigate`, `browser_snapshot`, `browser_vision` | 支持文本和视觉的交互式浏览器自动化。 |
| **多媒体** | `vision_analyze`, `image_generate`, `text_to_speech` | 多模态分析与生成。 |
| **Agent 编排** | `todo`, `clarify`, `execute_code`, `delegate_task` | 规划、澄清、代码执行和 sub-agents 委派。 |
| **记忆与回溯** | `memory`, `session_search` | 持久化记忆和会话搜索。 |
| **自动化与投递** | `cronjob`, `send_message` | 带有创建/列表/更新/暂停/恢复/运行/删除操作的定时任务，以及外发消息投递。 |
| **集成** | `ha_*`, MCP server tools, `rl_*` | Home Assistant、MCP、RL 训练及其他集成。 |

有关基于代码生成的权威注册表，请参阅 [Built-in Tools Reference](/reference/tools-reference) 和 [Toolsets Reference](/reference/toolsets-reference)。

## 使用工具集

```bash
# 使用特定的工具集
hermes chat --toolsets "web,terminal"

# 查看所有可用工具
hermes tools

# 为每个平台配置工具（交互式）
hermes tools
```

常见的工具集包括 `web`, `terminal`, `file`, `browser`, `vision`, `image_gen`, `moa`, `skills`, `tts`, `todo`, `memory`, `session_search`, `cronjob`, `code_execution`, `delegation`, `clarify`, `homeassistant`, 和 `rl`。

请参阅 [Toolsets Reference](/reference/toolsets-reference) 获取完整列表，包括 `hermes-cli`、`hermes-telegram` 等平台预设，以及像 `mcp-<server>` 这样的动态 MCP 工具集。

## 终端后端

`terminal` 工具可以在不同的环境中执行命令：

| 后端 | 描述 | 使用场景 |
|---------|-------------|----------|
| `local` | 在你的机器上运行（默认） | 开发、受信任的任务 |
| `docker` | 隔离的容器 | 安全性、可复现性 |
| `ssh` | 远程服务器 | 沙箱隔离，防止 Agent 修改自身代码 |
| `singularity` | HPC 容器 | 集群计算、无根（rootless）环境 |
| `modal` | 云端执行 | 无服务器（Serverless）、扩展性 |
| `daytona` | 云端沙箱工作区 | 持久化的远程开发环境 |

### 配置

```yaml
# 在 ~/.hermes/config.yaml 中
terminal:
  backend: local    # 或: docker, ssh, singularity, modal, daytona
  cwd: "."          # 工作目录
  timeout: 180      # 命令超时时间（秒）
```

### Docker 后端

```yaml
terminal:
  backend: docker
  docker_image: python:3.11-slim
```

### SSH 后端

出于安全考虑推荐使用 —— Agent 无法修改其自身的代码：

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

### Singularity/Apptainer

```bash
# 为并行 worker 预构建 SIF
apptainer build ~/python.sif docker://python:3.11-slim

# 配置
hermes config set terminal.backend singularity
hermes config set terminal.singularity_image ~/python.sif
```

### Modal (Serverless 云端)

```bash
uv pip install modal
modal setup
hermes config set terminal.backend modal
```

### 容器资源

为所有容器后端配置 CPU、内存、磁盘和持久化：

```yaml
terminal:
  backend: docker  # 或 singularity, modal, daytona
  container_cpu: 1              # CPU 核心数 (默认: 1)
  container_memory: 5120        # 内存 MB (默认: 5GB)
  container_disk: 51200         # 磁盘 MB (默认: 50GB)
  container_persistent: true    # 跨会话持久化文件系统 (默认: true)
```

当 `container_persistent: true` 时，安装的包、文件和配置将在不同会话间保留。

### 容器安全

所有容器后端运行时都经过了安全加固：

- 只读根文件系统 (Docker)
- 丢弃所有 Linux capabilities
- 禁止权限提升
- PID 限制 (256 个进程)
- 完全的命名空间隔离
- 通过卷（volumes）实现持久化工作区，而非可写的根层

Docker 可以选择性地通过 `terminal.docker_forward_env` 接收显式的环境变量白名单，但转发的变量对容器内的命令是可见的，应视为在该会话中已暴露。

## 后台进程管理

启动并管理后台进程：

```python
terminal(command="pytest -v tests/", background=true)
# 返回: {"session_id": "proc_abc123", "pid": 12345}

# 然后使用 process 工具进行管理：
process(action="list")       # 显示所有运行中的进程
process(action="poll", session_id="proc_abc123")   # 检查状态
process(action="wait", session_id="proc_abc123")   # 阻塞直到完成
process(action="log", session_id="proc_abc123")    # 获取完整输出
process(action="kill", session_id="proc_abc123")   # 终止进程
process(action="write", session_id="proc_abc123", data="y")  # 发送输入
```

PTY 模式 (`pty=true`) 支持交互式 CLI 工具，如 Codex 和 Claude Code。

## Sudo 支持

如果命令需要 sudo，系统会提示你输入密码（在该会话中会缓存）。或者在 `~/.hermes/.env` 中设置 `SUDO_PASSWORD`。

:::warning
在消息平台上，如果 sudo 失败，输出会包含一个提示，建议将 `SUDO_PASSWORD` 添加到 `~/.hermes/.env`。
:::
