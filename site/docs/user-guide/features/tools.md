---
sidebar_position: 1
title: "工具与工具集"
description: "Hermes Agent 工具概览 —— 可用工具有哪些、工具集如何工作，以及终端后端"
---

# 工具与工具集

工具是扩展智能体能力的函数。它们被组织成逻辑上的**工具集**，可以按平台启用或禁用。

## 可用工具

Hermes 内置了广泛的工具注册表，涵盖网络搜索、浏览器自动化、终端执行、文件编辑、记忆、任务委派、强化学习训练、消息传递、Home Assistant、Honcho 记忆等。

高级分类：

| 类别 | 示例 | 描述 |
|----------|----------|-------------|
| **网络** | `web_search`, `web_extract` | 搜索网络并提取页面内容。 |
| **终端与文件** | `terminal`, `process`, `read_file`, `patch` | 执行命令和操作文件。 |
| **浏览器** | `browser_navigate`, `browser_snapshot`, `browser_vision` | 支持文本和视觉的交互式浏览器自动化。 |
| **媒体** | `vision_analyze`, `image_generate`, `text_to_speech` | 多模态分析与生成。 |
| **智能体编排** | `todo`, `clarify`, `execute_code`, `delegate_task` | 规划、澄清、代码执行和子智能体委派。 |
| **记忆与回忆** | `memory`, `session_search`, `honcho_*` | 持久化记忆、会话搜索和 Honcho 跨会话上下文。 |
| **自动化与交付** | `cronjob`, `send_message` | 支持创建/列出/更新/暂停/恢复/运行/删除操作的定时任务，以及外发消息传递。 |
| **集成** | `ha_*`, MCP 服务器工具, `rl_*` | Home Assistant、MCP、强化学习训练和其他集成。 |

关于权威的代码派生注册表，请参阅[内置工具参考](/reference/tools-reference)和[工具集参考](/reference/toolsets-reference)。

## 使用工具集

```bash
# 使用特定的工具集
hermes chat --toolsets "web,terminal"

# 查看所有可用工具
hermes tools

# 按平台配置工具（交互式）
hermes tools
```

常见的工具集包括 `web`、`terminal`、`file`、`browser`、`vision`、`image_gen`、`moa`、`skills`、`tts`、`todo`、`memory`、`session_search`、`cronjob`、`code_execution`、`delegation`、`clarify`、`honcho`、`homeassistant` 和 `rl`。

完整列表请参阅[工具集参考](/reference/toolsets-reference)，其中包括平台预设（如 `hermes-cli`、`hermes-telegram`）和动态 MCP 工具集（如 `mcp-<server>`）。

## 终端后端

终端工具可以在不同的环境中执行命令：

| 后端 | 描述 | 使用场景 |
|---------|-------------|----------|
| `local` | 在你的机器上运行（默认） | 开发、可信任务 |
| `docker` | 隔离的容器 | 安全性、可复现性 |
| `ssh` | 远程服务器 | 沙箱化、使智能体远离其自身代码 |
| `singularity` | HPC 容器 | 集群计算、无 root 权限 |
| `modal` | 云端执行 | 无服务器、可扩展 |
| `daytona` | 云端沙箱工作空间 | 持久的远程开发环境 |

### 配置

```yaml
# 在 ~/.hermes/config.yaml 中
terminal:
  backend: local    # 或：docker, ssh, singularity, modal, daytona
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

推荐用于安全性 —— 智能体无法修改其自身代码：

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
# 为并行工作器预构建 SIF
apptainer build ~/python.sif docker://python:3.11-slim

# 配置
hermes config set terminal.backend singularity
hermes config set terminal.singularity_image ~/python.sif
```

### Modal（无服务器云）

```bash
uv pip install modal
modal setup
hermes config set terminal.backend modal
```

### 容器资源

为所有容器后端配置 CPU、内存、磁盘和持久性：

```yaml
terminal:
  backend: docker  # 或 singularity, modal, daytona
  container_cpu: 1              # CPU 核心数（默认：1）
  container_memory: 5120        # 内存大小（MB）（默认：5GB）
  container_disk: 51200         # 磁盘大小（MB）（默认：50GB）
  container_persistent: true    # 跨会话持久化文件系统（默认：true）
```

当 `container_persistent: true` 时，安装的软件包、文件和配置会在会话间保留。

### 容器安全性

所有容器后端都运行在安全加固的环境中：

- 只读的根文件系统（Docker）
- 丢弃所有 Linux 能力
- 无权限提升
- PID 限制（256 个进程）
- 完整的命名空间隔离
- 通过卷实现持久化工作空间，而非可写的根层

Docker 可以选择性地通过 `terminal.docker_forward_env` 接收明确的环境变量允许列表，但转发的变量对容器内的命令可见，应视为已暴露给该会话。

## 后台进程管理

启动后台进程并管理它们：

```python
terminal(command="pytest -v tests/", background=true)
# 返回：{"session_id": "proc_abc123", "pid": 12345}

# 然后使用 process 工具进行管理：
process(action="list")       # 显示所有正在运行的进程
process(action="poll", session_id="proc_abc123")   # 检查状态
process(action="wait", session_id="proc_abc123")   # 阻塞直到完成
process(action="log", session_id="proc_abc123")    # 完整输出
process(action="kill", session_id="proc_abc123")   # 终止
process(action="write", session_id="proc_abc123", data="y")  # 发送输入
```

PTY 模式 (`pty=true`) 支持交互式 CLI 工具，如 Codex 和 Claude Code。

## Sudo 支持

如果命令需要 sudo，系统会提示你输入密码（密码在会话期间会被缓存）。或者，在 `~/.hermes/.env` 中设置 `SUDO_PASSWORD`。

:::warning
在消息传递平台上，如果 sudo 失败，输出会包含提示，建议将 `SUDO_PASSWORD` 添加到 `~/.hermes/.env`。
:::
