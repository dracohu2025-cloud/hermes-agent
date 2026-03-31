---
sidebar_position: 2
title: "斜杠命令参考"
description: "交互式 CLI 和消息平台斜杠命令的完整参考"
---

# 斜杠命令参考

Hermes 有两套斜杠命令界面，均由 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI 斜杠命令** — 由 `cli.py` 分发，注册表提供自动补全
- **消息平台斜杠命令** — 由 `gateway/run.py` 分发，帮助文本和平台菜单由注册表生成

已安装的技能也会作为动态斜杠命令在这两个界面上暴露。这包括捆绑的技能，例如 `/plan`，它会打开计划模式并将 Markdown 计划保存在相对于活动工作空间/后端工作目录的 `.hermes/plans/` 目录下。

## 交互式 CLI 斜杠命令

在 CLI 中输入 `/` 可打开自动补全菜单。内置命令不区分大小写。

### 会话

| 命令 | 描述 |
|---------|-------------|
| `/new` (别名: `/reset`) | 开始一个新会话（新的会话 ID + 历史记录） |
| `/clear` | 清屏并开始新会话 |
| `/history` | 显示对话历史 |
| `/save` | 保存当前对话 |
| `/retry` | 重试上一条消息（重新发送给智能体） |
| `/undo` | 移除最后一组用户/助手对话轮次 |
| `/title` | 为当前会话设置标题（用法：/title 我的会话名称） |
| `/compress` | 手动压缩对话上下文（清空记忆 + 总结） |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [数字]） |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue <prompt>` (别名: `/q`) | 为下一轮排队一个提示（不中断当前智能体响应） |
| `/resume [name]` | 恢复一个之前命名的会话 |
| `/statusbar` (别名: `/sb`) | 切换上下文/模型状态栏的开关 |
| `/background <prompt>` | 在单独的后台会话中运行一个提示。智能体独立处理你的提示——你当前的会话可以自由处理其他工作。任务完成后，结果会以面板形式显示。参见 [CLI 后台会话](/docs/user-guide/cli#background-sessions)。 |
| `/plan [request]` | 加载捆绑的 `plan` 技能来编写 Markdown 计划，而不是执行工作。计划保存在相对于活动工作空间/后端工作目录的 `.hermes/plans/` 目录下。 |

### 配置

| 命令 | 描述 |
|---------|-------------|
| `/config` | 显示当前配置 |
| `/model [model-name]` | 显示或更改当前模型。支持：`/model claude-sonnet-4`、`/model provider:model`（切换提供商）、`/model custom:model`（自定义端点）、`/model custom:name:model`（命名的自定义提供商）、`/model custom`（从端点自动检测） |
| `/provider` | 显示可用提供商和当前提供商 |
| `/prompt` | 查看/设置自定义系统提示词 |
| `/personality` | 设置预定义的性格 |
| `/verbose` | 循环切换工具进度显示：关闭 → 仅新任务 → 全部 → 详细模式。可以通过配置[为消息平台启用](#notes)。 |
| `/reasoning` | 管理推理力度和显示（用法：/reasoning [级别\|显示\|隐藏]） |
| `/skin` | 显示或更改显示皮肤/主题 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式和语音播放。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |

### 工具与技能

| 命令 | 描述 |
|---------|-------------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或为当前会话禁用/启用特定工具。禁用工具会将其从智能体的工具集中移除并触发会话重置。 |
| `/toolsets` | 列出可用的工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chrome CDP 连接。`connect` 将浏览器工具附加到正在运行的 Chrome 实例（默认：`ws://localhost:9222`）。`disconnect` 断开连接。`status` 显示当前连接状态。如果未检测到调试器，则自动启动 Chrome。 |
| `/skills` | 从在线注册表搜索、安装、检查或管理技能 |
| `/cron` | 管理计划任务（列出、添加/创建、编辑、暂停、恢复、运行、移除） |
| `/reload-mcp` | 从 config.yaml 重新加载 MCP 服务器 |
| `/plugins` | 列出已安装的插件及其状态 |

### 信息

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示此帮助信息 |
| `/usage` | 显示令牌使用量、成本细分和会话时长 |
| `/insights` | 显示使用情况洞察和分析（最近 30 天） |
| `/platforms` | 显示网关/消息平台状态 |
| `/paste` | 检查剪贴板中是否有图像并附加它 |

### 退出

| 命令 | 描述 |
|---------|-------------|
| `/quit` | 退出 CLI（也支持：/exit, /q） |

### 动态 CLI 斜杠命令

| 命令 | 描述 |
|---------|-------------|
| `/<skill-name>` | 将任何已安装的技能加载为按需命令。例如：`/gif-search`、`/github-pr-workflow`、`/excalidraw`。 |
| `/skills ...` | 从注册表和官方的可选技能目录中搜索、浏览、检查、安装、审核、发布和配置技能。 |

### 快捷命令

来自 `~/.hermes/config.yaml` 中 `quick_commands` 的用户自定义快捷命令也可作为斜杠命令使用。这些命令在分发时解析，不会显示在内置的自动补全/帮助表中。

## 消息平台斜杠命令

消息网关在 Telegram、Discord、Slack、WhatsApp、Signal、Email 和 Home Assistant 聊天中支持以下内置命令：

| 命令 | 描述 |
|---------|-------------|
| `/new` | 开始新对话。 |
| `/reset` | 重置对话历史。 |
| `/status` | 显示会话信息。 |
| `/stop` | 终止所有正在运行的后台进程并中断正在运行的智能体。 |
| `/model [provider:model]` | 显示或更改模型。支持切换提供商（`/model zai:glm-5`）、自定义端点（`/model custom:model`）、命名的自定义提供商（`/model custom:local:qwen`）和自动检测（`/model custom`）。 |
| `/provider` | 显示提供商可用性和认证状态。 |
| `/personality [name]` | 为会话设置性格叠加层。 |
| `/retry` | 重试上一条消息。 |
| `/undo` | 移除最后一组对话轮次。 |
| `/sethome` | 将当前聊天标记为平台的主频道，用于接收交付内容。 |
| `/compress` | 手动压缩对话上下文。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复一个之前命名的会话。 |
| `/usage` | 显示令牌使用量、估计成本细分（输入/输出）、上下文窗口状态和会话时长。 |
| `/insights [days]` | 显示使用情况分析。 |
| `/reasoning [level\|show\|hide]` | 更改推理力度或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 管理 Discord 语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/background <prompt>` | 在单独的后台会话中运行一个提示。任务完成后，结果会发送回同一个聊天。参见[消息平台后台会话](/docs/user-guide/messaging/#background-sessions)。 |
| `/plan [request]` | 加载捆绑的 `plan` 技能来编写 Markdown 计划，而不是执行工作。计划保存在相对于活动工作空间/后端工作目录的 `.hermes/plans/` 目录下。 |
| `/reload-mcp` | 从配置重新加载 MCP 服务器。 |
| `/approve [session\|always]` | 批准并执行一个待定的危险命令。`session` 仅批准此会话；`always` 添加到永久允许列表。 |
| `/deny` | 拒绝一个待定的危险命令。 |
| `/update` | 将 Hermes Agent 更新到最新版本。 |
| `/help` | 显示消息平台帮助。 |
| `/<skill-name>` | 按名称调用任何已安装的技能。 |

## 注意事项 {#notes}

- `/skin`、`/tools`、`/toolsets`、`/browser`、`/config`、`/prompt`、`/cron`、`/skills`、`/platforms`、`/paste`、`/statusbar` 和 `/plugins` 是 **仅限 CLI** 的命令。
- `/verbose` **默认仅限 CLI**，但可以通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 为消息平台启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置。
- `/status`、`/sethome`、`/update`、`/approve` 和 `/deny` 是 **仅限消息平台** 的命令。
- `/background`、`/voice`、`/reload-mcp` 和 `/rollback` 在 **CLI 和消息网关** 中都有效。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。
