---
sidebar_position: 2
title: "斜杠命令参考"
description: "交互式 CLI 和消息平台斜杠命令的完整参考指南"
---

# 斜杠命令参考

Hermes 拥有两个斜杠命令界面，均由 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI 斜杠命令** —— 由 `cli.py` 调度，支持来自注册表的自动补全
- **消息平台斜杠命令** —— 由 `gateway/run.py` 调度，其帮助文本和平台菜单根据注册表生成

已安装的技能（Skills）也会在两个界面上作为动态斜杠命令公开。这包括像 `/plan` 这样的内置技能，它会开启计划模式，并将 Markdown 格式的计划保存在相对于当前工作区/后端工作目录的 `.hermes/plans/` 下。

## 交互式 CLI 斜杠命令

在 CLI 中输入 `/` 即可打开自动补全菜单。内置命令不区分大小写。

### 会话 (Session)

| 命令 | 描述 |
|---------|-------------|
| `/new` (别名: `/reset`) | 开始新会话（全新的会话 ID + 历史记录） |
| `/clear` | 清屏并开始新会话 |
| `/history` | 显示对话历史 |
| `/save` | 保存当前对话 |
| `/retry` | 重试最后一条消息（重新发送给 Agent） |
| `/undo` | 移除最后一次用户/助手的对话往返 |
| `/title` | 为当前会话设置标题（用法：/title 我的会话名称） |
| `/compress` | 手动压缩对话上下文（清空记忆 + 总结） |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [数字]） |
| `/stop` | 杀死所有正在运行的后台进程 |
| `/queue <prompt>` (别名: `/q`) | 为下一轮对话排队一个提示词（不会中断当前的 Agent 响应）。**注意：** `/q` 同时被 `/queue` 和 `/quit` 占用；以最后注册的为准，因此在实践中 `/q` 会解析为 `/quit`。请明确使用 `/queue`。 |
| `/resume [name]` | 恢复之前命名的会话 |
| `/statusbar` (别名: `/sb`) | 切换上下文/模型状态栏的开启或关闭 |
| `/background <prompt>` (别名: `/bg`) | 在独立的后台会话中运行提示词。Agent 会独立处理您的提示词 —— 您当前的会话可以继续进行其他工作。任务完成后，结果将以面板形式出现。参见 [CLI 后台会话](/user-guide/cli#background-sessions)。 |
| `/btw <question>` | 使用会话上下文的临时侧边提问（不使用工具，不持久化）。适用于在不影响对话历史的情况下进行快速澄清。 |
| `/plan [request]` | 加载内置的 `plan` 技能来编写 Markdown 计划而不是直接执行工作。计划保存在相对于当前工作区/后端工作目录的 `.hermes/plans/` 下。 |
| `/branch [name]` (别名: `/fork`) | 分叉当前会话（探索不同的路径） |

### 配置 (Configuration)

| 命令 | 描述 |
|---------|-------------|
| `/config` | 显示当前配置 |
| `/model [model-name]` | 显示或更改当前模型。支持：`/model claude-sonnet-4`，`/model provider:model`（切换提供商），`/model custom:model`（自定义端点），`/model custom:name:model`（命名的自定义提供商），`/model custom`（从端点自动检测） |
| `/provider` | 显示可用提供商和当前提供商 |
| `/prompt` | 查看/设置自定义系统提示词 (System Prompt) |
| `/personality` | 设置预定义的个性 |
| `/verbose` | 循环切换工具进度显示：关闭 → 新增 → 全部 → 详细。可以通过配置为[消息平台开启](#notes)。 |
| `/reasoning` | 管理推理强度和显示（用法：/reasoning [level\|show\|hide]） |
| `/skin` | 显示或更改显示皮肤/主题 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式和语音播放。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式 —— 跳过所有危险命令的审批提示。 |

### 工具与技能 (Tools & Skills)

| 命令 | 描述 |
|---------|-------------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或为当前会话禁用/启用特定工具。禁用工具会将其从 Agent 的工具集中移除并触发会话重置。 |
| `/toolsets` | 列出可用的工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chrome CDP 连接。`connect` 将浏览器工具附加到运行中的 Chrome 实例（默认：`ws://localhost:9222`）。`disconnect` 断开连接。`status` 显示当前连接。如果未检测到调试器，将自动启动 Chrome。 |
| `/skills` | 从在线注册表搜索、安装、检查或管理技能 |
| `/cron` | 管理定时任务（列出、添加/创建、编辑、暂停、恢复、运行、移除） |
| `/reload-mcp` (别名: `/reload_mcp`) | 从 config.yaml 重新加载 MCP 服务器 |
| `/plugins` | 列出已安装的插件及其状态 |

### 信息 (Info)

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示此帮助消息 |
| `/usage` | 显示 Token 使用情况、费用明细和会话时长 |
| `/insights` | 显示使用洞察和分析（最近 30 天） |
| `/platforms` (别名: `/gateway`) | 显示网关/消息平台状态 |
| `/paste` | 检查剪贴板中的图像并附加它 |
| `/profile` | 显示活动配置文件名称和主目录 |

### 退出 (Exit)

| 命令 | 描述 |
|---------|-------------|
| `/quit` | 退出 CLI（同：`/exit`）。请参阅上方 `/queue` 下关于 `/q` 的说明。 |

### 动态 CLI 斜杠命令

| 命令 | 描述 |
|---------|-------------|
| `/<skill-name>` | 将任何已安装的技能作为按需命令加载。例如：`/gif-search`，`/github-pr-workflow`，`/excalidraw`。 |
| `/skills ...` | 从注册表和官方可选技能目录中搜索、浏览、检查、安装、审计、发布和配置技能。 |

### 快速命令 (Quick Commands)

用户定义的快速命令可以将短别名映射到较长的提示词。在 `~/.hermes/config.yaml` 中配置它们：

```yaml
quick_commands:
  review: "Review my latest git diff and suggest improvements"
  deploy: "Run the deployment script at scripts/deploy.sh and verify the output"
  morning: "Check my calendar, unread emails, and summarize today's priorities"
```

然后在 CLI 中输入 `/review`、`/deploy` 或 `/morning`。快速命令在调度时解析，不会显示在内置的自动补全/帮助表格中。

### 别名解析

命令支持前缀匹配：输入 `/h` 解析为 `/help`，`/mod` 解析为 `/model`。当前缀有歧义（匹配多个命令）时，注册表顺序中的第一个匹配项胜出。完整命令名称和注册别名始终优先于前缀匹配。

## 消息平台斜杠命令

消息网关支持在 Telegram、Discord、Slack、WhatsApp、Signal、Email 和 Home Assistant 聊天中使用以下内置命令：

| 命令 | 描述 |
|---------|-------------|
| `/new` | 开始新对话。 |
| `/reset` | 重置对话历史。 |
| `/status` | 显示会话信息。 |
| `/stop` | 杀死所有运行中的后台进程并中断正在运行的 Agent。 |
| `/model [provider:model]` | 显示或更改模型。支持切换提供商 (`/model zai:glm-5`)、自定义端点 (`/model custom:model`)、命名的自定义提供商 (`/model custom:local:qwen`) 以及自动检测 (`/model custom`)。 |
| `/provider` | 显示提供商可用性和身份验证状态。 |
| `/personality [name]` | 为会话设置个性叠加。 |
| `/retry` | 重试最后一条消息。 |
| `/undo` | 移除最后一次对话往返。 |
| `/sethome` (别名: `/set-home`) | 将当前聊天标记为该平台的交付主频道。 |
| `/compress` | 手动压缩对话上下文。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复之前命名的会话。 |
| `/usage` | 显示 Token 使用情况、预估费用明细（输入/输出）、上下文窗口状态和会话时长。 |
| `/insights [days]` | 显示使用分析。 |
| `/reasoning [level\|show\|hide]` | 更改推理强度或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 用于管理 Discord 语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/background <prompt>` | 在独立的后台会话中运行提示词。任务完成后，结果将发回同一个聊天窗口。参见 [消息平台后台会话](/user-guide/messaging/#background-sessions)。 |
| `/plan [request]` | 加载内置的 `plan` 技能来编写 Markdown 计划而不是直接执行工作。计划保存在相对于当前工作区/后端工作目录的 `.hermes/plans/` 下。 |
| `/reload-mcp` (别名: `/reload_mcp`) | 从配置中重新加载 MCP 服务器。 |
| `/yolo` | 切换 YOLO 模式 —— 跳过所有危险命令的审批提示。 |
| `/commands [page]` | 浏览所有命令和技能（分页）。 |
| `/approve [session\|always]` | 批准并执行待处理的危险命令。`session` 仅针对本次会话批准；`always` 将其添加到永久白名单。 |
| `/deny` | 拒绝待处理的危险命令。 |
| `/update` | 将 Hermes Agent 更新到最新版本。 |
| `/help` | 显示消息平台帮助。 |
| `/<skill-name>` | 通过名称调用任何已安装的技能。 |
## 注意事项 {#notes}

- `/skin`、`/tools`、`/toolsets`、`/browser`、`/config`、`/prompt`、`/cron`、`/skills`、`/platforms`、`/paste`、`/statusbar` 以及 `/plugins` 是 **仅限 CLI** 的命令。
- `/verbose` **默认仅限 CLI**，但可以通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 来为即时通讯平台启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置中。
- `/status`、`/sethome`、`/update`、`/approve`、`/deny` 以及 `/commands` 是 **仅限即时通讯平台** 的命令。
- `/background`、`/voice`、`/reload-mcp`、`/rollback` 以及 `/yolo` 在 **CLI 和即时通讯网关中均可使用**。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。
