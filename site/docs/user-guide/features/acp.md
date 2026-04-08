---
sidebar_position: 11
title: "ACP 编辑器集成"
description: "在 VS Code、Zed 和 JetBrains 等兼容 ACP 的编辑器中使用 Hermes Agent"
---

# ACP 编辑器集成

Hermes Agent 可以作为 ACP 服务端运行，让兼容 ACP 的编辑器通过 stdio 与 Hermes 通信并渲染：

- 聊天消息
- 工具活动
- 文件差异（diffs）
- 终端命令
- 审批提示
- 流式思考 / 响应分块

如果你希望 Hermes 表现得像一个编辑器原生的编程 Agent，而不是独立的 CLI 或消息机器人，那么 ACP 是一个很好的选择。

## Hermes 在 ACP 模式下公开的内容

Hermes 运行一套专为编辑器工作流设计的精选 `hermes-acp` 工具集。它包括：

- 文件工具：`read_file`、`write_file`、`patch`、`search_files`
- 终端工具：`terminal`、`process`
- 网页/浏览器工具
- 记忆、待办事项（todo）、会话搜索
- 技能（skills）
- `execute_code` 和 `delegate_task`
- 视觉能力（vision）

它特意排除了不符合典型编辑器 UX 的功能，例如消息投递和 cronjob 任务管理。

## 安装

正常安装 Hermes，然后添加 ACP 额外依赖：

```bash
pip install -e '.[acp]'
```

这将安装 `agent-client-protocol` 依赖并启用以下命令：

- `hermes acp`
- `hermes-acp`
- `python -m acp_adapter`

## 启动 ACP 服务端

以下任何命令都可以启动 ACP 模式下的 Hermes：

```bash
hermes acp
```

```bash
hermes-acp
```

```bash
python -m acp_adapter
```

Hermes 会将日志输出到 stderr，以便 stdout 专门用于 ACP JSON-RPC 流量。

## 编辑器设置

### VS Code

安装 ACP 客户端扩展，然后将其指向仓库的 `acp_registry/` 目录。

设置代码片段示例：

```json
{
  "acpClient.agents": [
    {
      "name": "hermes-agent",
      "registryDir": "/path/to/hermes-agent/acp_registry"
    }
  ]
}
```

### Zed

设置代码片段示例：

```json
{
  "agent_servers": {
    "hermes-agent": {
      "type": "custom",
      "command": "hermes",
      "args": ["acp"],
    },
  },
}
```

### JetBrains

使用兼容 ACP 的插件并将其指向：

```text
/path/to/hermes-agent/acp_registry
```

## 注册清单 (Registry manifest)

ACP 注册清单位于：

```text
acp_registry/agent.json
```

它声明了一个基于命令的 Agent，其启动命令为：

```text
hermes acp
```

## 配置与凭据

ACP 模式使用与 CLI 相同的 Hermes 配置：

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/skills/`
- `~/.hermes/state.db`

模型提供商（Provider）的解析使用 Hermes 正常的运行时解析器，因此 ACP 会继承当前配置的提供商和凭据。

## 会话行为

在服务端运行期间，ACP 会话由 ACP 适配器的内存会话管理器跟踪。

每个会话存储：

- 会话 ID
- 工作目录
- 选定的模型
- 当前对话历史
- 取消事件

底层的 `AIAgent` 仍然使用 Hermes 正常的持久化/日志路径，但 ACP 的 `list/load/resume/fork` 操作范围仅限于当前运行的 ACP 服务端进程。

## 工作目录行为

ACP 会话将编辑器的当前工作目录（cwd）与 Hermes 任务 ID 绑定，因此文件和终端工具运行的相对路径是基于编辑器工作区的，而不是服务端进程的 cwd。

## 审批

危险的终端命令可以路由回编辑器作为审批提示。ACP 的审批选项比 CLI 流程更简单：

- 允许一次 (allow once)
- 总是允许 (allow always)
- 拒绝 (deny)

在超时或出错时，审批桥接器会拒绝该请求。

## 故障排除

### ACP Agent 未出现在编辑器中

检查：

- 编辑器是否指向了正确的 `acp_registry/` 路径
- Hermes 已安装且在你的 PATH 环境变量中
- 已安装 ACP 额外依赖 (`pip install -e '.[acp]'`)

### ACP 启动但立即报错

尝试以下检查：

```bash
hermes doctor
hermes status
hermes acp
```

### 缺少凭据

ACP 模式没有自己的登录流程。它使用 Hermes 现有的提供商设置。通过以下方式配置凭据：

```bash
hermes model
```

或者编辑 `~/.hermes/.env` 文件。

## 另请参阅

- [ACP 内部原理](../../developer-guide/acp-internals.md)
- [提供商运行时解析](../../developer-guide/provider-runtime.md)
- [工具运行时](../../developer-guide/tools-runtime.md)
