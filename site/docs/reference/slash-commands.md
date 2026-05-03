---
sidebar_position: 2
title: "Slash 命令参考"
description: "完整的交互式 CLI 和消息斜杠命令参考"
---

# Slash 命令参考 {#slash-commands-reference}

Hermes 有两个斜杠命令界面，两者均由 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI Slash 命令** —— 由 `cli.py` 分发，支持注册表中的自动补全
- **消息 Slash 命令** —— 由 `gateway/run.py` 分发，帮助文本和平台菜单从注册表中生成

已安装的技能也会作为动态斜杠命令暴露在这两个界面上。这包括内置技能，如 `/plan`，它会打开计划模式并将 Markdown 计划保存在相对于当前工作区/后端工作目录的 `.hermes/plans/` 下。

## 交互式 CLI Slash 命令 {#interactive-cli-slash-commands}

在 CLI 中输入 `/` 即可打开自动补全菜单。内建命令不区分大小写。

### 会话（Session） {#session}

| 命令 | 描述 |
|---------|-------------|
| `/new`（别名：`/reset`） | 开始一个新会话（全新的会话 ID + 历史记录） |
| `/clear` | 清除屏幕并开始一个新会话 |
| `/history` | 显示对话历史 |
| `/save` | 保存当前对话 |
| `/retry` | 重试最后一条消息（重新发送给 Agent） |
| `/undo` | 移除最后一次用户/助手的交互 |
| `/title` | 为当前会话设置标题（用法：/title My Session Name） |
| `/compress [focus topic]` | 手动压缩对话上下文（清空记忆 + 摘要）。可选的 focus topic 缩小摘要保留的范围。 |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [number]） |
| `/snapshot [create\|restore &lt;id&gt;\|prune]`（别名：`/snap`） | 创建或恢复 Hermes 配置/状态的状态快照。`create [label]` 保存快照，`restore &lt;id&gt;` 恢复到该快照，`prune [N]` 移除旧快照，不带参数则列出所有快照。 |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue &lt;prompt&gt;`（别名：`/q`） | 将提示排入下一次轮次的队列（不会打断当前 Agent 的响应）。 |
| `/steer &lt;prompt&gt;` | 注入一个运行时提示，该提示会在**下一次工具调用之后**到达 Agent——不会中断，不会新增用户轮次。文本会在当前工具完成后附加到最后一次工具结果的内容中，为 Agent 提供新的上下文，而不中断当前工具调用循环。用于在任务执行中调整方向（例如，当 Agent 运行测试时，说“专注于认证模块”）。 |
| `/goal &lt;text&gt;` | 设置一个长期目标，Hermes 会在多个轮次中持续向该目标努力——这是我们实现 Ralph 循环的方式。每一轮后，一个辅助评判模型会判断目标是否已完成；如果未完成，Hermes 会自动继续。子命令：`/goal status`、`/goal pause`、`/goal resume`、`/goal clear`。默认预算为 20 轮（`goals.max_turns`）；任何真实用户消息都会抢占延续循环，状态在 `/resume` 后保留。完整讲解请参见[持久目标](/user-guide/features/goals)。 |
| `/resume [name]` | 恢复一个先前命名的会话 |
| `/redraw` | 强制重新绘制整个 UI（恢复 tmux 调整大小、鼠标选择伪影等导致的终端漂移） |
| `/status` | 显示会话信息 |
| `/agents`（别名：`/tasks`） | 显示当前会话中的活跃 Agent 和正在运行的任务。 |
| `/background &lt;prompt&gt;`（别名：`/bg`、`/btw`） | 在单独的后台会话中运行一个提示。Agent 独立处理你的提示——当前会话保持空闲，可以处理其他工作。任务完成时，结果会以面板形式显示。参见[CLI 后台会话](/user-guide/cli#background-sessions)。 |
| `/branch [name]`（别名：`/fork`） | 分叉当前会话（探索不同的路径） |
### 配置 {#configuration}

| 命令 | 描述 |
|------|------|
| `/config` | 显示当前配置 |
| `/model [model-name]` | 显示或更改当前模型。支持：`/model claude-sonnet-4`、`/model provider:model`（切换提供商）、`/model custom:model`（自定义端点）、`/model custom:name:model`（命名自定义提供商）、`/model custom`（从端点自动检测）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的提供商之间切换。要添加新提供商，请退出会话并在终端中运行 `hermes model`。 |
| `/personality` | 设置预定义人格 |
| `/verbose` | 循环切换工具进度显示：关闭 → 新 → 全部 → 详细。可通过配置[在消息中启用](#notes)。 |
| `/fast [normal\|fast\|status]` | 切换快速模式——OpenAI 优先处理 / Anthropic 快速模式。选项：`normal`、`fast`、`status`。 |
| `/reasoning` | 管理推理力度与显示（用法：/reasoning [level\|show\|hide]） |
| `/skin` | 显示或更改显示皮肤/主题 |
| `/statusbar`（别名：`/sb`） | 切换上下文/模型状态栏的显示或隐藏 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式和语音播放。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式——跳过所有危险命令的批准提示。 |
| `/footer [on\|off\|status]` | 在最终回复中切换网关运行时元数据页脚（显示模型、工具计数、耗时）。 |
| `/busy [queue\|steer\|interrupt\|status]` | 仅 CLI：控制 Hermes 工作时按 Enter 键的行为——将新消息排队、中途转向或立即中断。 |
| `/indicator [kaomoji\|emoji\|unicode\|ascii]` | 仅 CLI：选择 TUI 忙碌指示器样式。 |

### 工具与技能 {#tools-skills}

| 命令 | 描述 |
|------|------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或为当前会话禁用/启用特定工具。禁用某个工具会将其从 Agent 的工具集中移除并触发会话重置。 |
| `/toolsets` | 列出可用的工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chrome CDP 连接。`connect` 将浏览器工具附加到正在运行的 Chrome 实例（默认：`ws://localhost:9222`）。`disconnect` 断开连接。`status` 显示当前连接。如果未检测到调试器，则自动启动 Chrome。 |
| `/skills` | 从在线注册表中搜索、安装、检查或管理技能 |
| `/cron` | 管理定时任务（列出、添加/创建、编辑、暂停、恢复、运行、移除） |
| `/curator` | 后台技能维护——`status`、`run`、`pin`、`archive`。参见 [Curator](/user-guide/features/curator)。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 从 config.yaml 重新加载 MCP 服务器 |
| `/reload` | 将 `.env` 变量重新加载到运行中的会话（无需重启即可获取新的 API 密钥） |
| `/plugins` | 列出已安装的插件及其状态 |

### 信息 {#info}

| 命令 | 描述 |
|------|------|
| `/help` | 显示此帮助信息 |
| `/usage` | 显示 Token 用量、费用明细、会话时长，以及——当活跃提供商支持时——从提供商 API 实时拉取的**账户限制**部分（剩余配额/积分/套餐用量）。 |
| `/insights` | 显示用量洞察与分析（最近 30 天） |
| `/platforms`（别名：`/gateway`） | 显示网关/消息平台状态 |
| `/paste` | 附加剪贴板图片 |
| `/copy [number]` | 将最后一条助手回复复制到剪贴板（或带数字时复制倒数第 N 条）。仅 CLI。 |
| `/image &lt;path&gt;` | 为下一条提示附加本地图片文件。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享的链接。也可在消息中使用。 |
| `/profile` | 显示当前配置文件名称和主目录 |
| `/gquota` | 显示 Google Gemini Code Assist 配额用量（带进度条），仅在 `google-gemini-cli` 提供商激活时可用。 |
### 退出 {#exit}

| 命令 | 描述 |
|------|------|
| `/quit` | 退出 CLI（也可用 `/exit`）。 |

### 动态 CLI 斜杠命令 {#dynamic-cli-slash-commands}

| 命令 | 描述 |
|------|------|
| `/<技能名称>` | 将任何已安装的技能作为按需命令加载。示例：`/gif-search`、`/github-pr-workflow`、`/excalidraw`。 |
| `/skills ...` | 从注册表和官方可选技能目录中搜索、浏览、检查、安装、审计、发布和配置技能。 |

### 快速命令 {#quick-commands}

用户定义的快速命令将短斜杠命令映射到 shell 命令或其他斜杠命令。在 `~/.hermes/config.yaml` 中配置：

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  deploy:
    type: exec
    command: scripts/deploy.sh
  inbox:
    type: alias
    target: /gmail unread
```

然后在 CLI 或消息平台中输入 `/status`、`/deploy` 或 `/inbox`。快速命令在调度时解析，可能不会出现在每个内置的自动补全/帮助表中。

纯字符串的提示快捷方式不支持作为快速命令。将较长的可重用提示放入技能中，或使用 `type: alias` 指向现有的斜杠命令。

### 别名解析 {#alias-resolution}

命令支持前缀匹配：输入 `/h` 解析为 `/help`，`/mod` 解析为 `/model`。当前缀不明确（匹配多个命令）时，按注册顺序取第一个匹配项。完整命令名称和已注册的别名始终优先于前缀匹配。

## 消息斜杠命令 {#messaging-slash-commands}

消息网关在 Telegram、Discord、Slack、WhatsApp、Signal、Email 和 Home Assistant 聊天中支持以下内置命令：

| 命令 | 描述 |
|------|------|
| `/new` | 开始新对话。 |
| `/reset` | 重置对话历史。 |
| `/status` | 显示会话信息。 |
| `/stop` | 终止所有正在运行的后台进程并中断正在运行的 Agent。 |
| `/model [provider:model]` | 显示或更改模型。支持切换提供商（`/model zai:glm-5`）、自定义端点（`/model custom:model`）、命名自定义提供商（`/model custom:local:qwen`）和自动检测（`/model custom`）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的提供商之间切换。要添加新提供商或设置 API 密钥，请从终端（聊天会话之外）使用 `hermes model`。 |
| `/personality [name]` | 为会话设置个性覆盖。 |
| `/fast [normal\|fast\|status]` | 切换快速模式 — OpenAI Priority Processing / Anthropic Fast Mode。 |
| `/retry` | 重试上一条消息。 |
| `/undo` | 移除最后一次交换。 |
| `/sethome`（别名：`/set-home`） | 将当前聊天标记为平台的主频道，用于投递。 |
| `/compress [focus topic]` | 手动压缩对话上下文。可选的焦点主题可缩小摘要保留的范围。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复之前命名的会话。 |
| `/usage` | 显示 token 用量、预估成本明细（输入/输出）、上下文窗口状态、会话时长，以及——当活跃提供商支持时——从提供商 API 实时拉取的**账户限制**部分（剩余配额/积分）。 |
| `/insights [days]` | 显示使用分析。 |
| `/reasoning [level\|show\|hide]` | 更改推理努力或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 管理 Discord 语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/background &lt;prompt&gt;` | 在单独的后台会话中运行提示。任务完成后，结果会投递回同一聊天。参见 [消息后台会话](/user-guide/messaging/#background-sessions)。 |
| `/queue &lt;prompt&gt;`（别名：`/q`） | 将提示排入下一轮队列，而不中断当前轮。 |
| `/steer &lt;prompt&gt;` | 在下一次工具调用后注入一条消息，而不中断——模型会在下一次迭代中拾取它，而不是作为新的一轮。 |
| `/goal &lt;text&gt;` | 设置一个持续目标，Hermes 会在多轮中朝着它努力——这是我们对 Ralph loop 的实现。一个评判模型会在每轮后检查；如果未完成，Hermes 会自动继续，直到完成、你暂停/清除它，或达到轮次预算（默认 20）。子命令：`/goal status`、`/goal pause`、`/goal resume`、`/goal clear`。在 Agent 运行中安全地执行 status/pause/clear；设置新目标需要先执行 `/stop`。参见 [持续目标](/user-guide/features/goals)。 |
| `/footer [on\|off\|status]` | 切换最终回复上的运行时元数据页脚（显示模型、工具计数、计时）。 |
| `/curator [status\|run\|pin\|archive]` | 后台技能维护控制。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 从配置重新加载 MCP 服务器。 |
| `/yolo` | 切换 YOLO 模式——跳过所有危险命令的批准提示。 |
| `/commands [page]` | 浏览所有命令和技能（分页）。 |
| `/approve [session\|always]` | 批准并执行待处理的危险命令。`session` 仅在此会话中批准；`always` 添加到永久白名单。 |
| `/deny` | 拒绝待处理的危险命令。 |
| `/update` | 将 Hermes Agent 更新到最新版本。 |
| `/restart` | 在耗尽正在运行的活动后优雅地重启网关。当网关重新上线时，它会向请求者的聊天/线程发送确认。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享的链接。 |
| `/help` | 显示消息帮助。 |
| `/<技能名称>` | 按名称调用任何已安装的技能。 |
## 注意事项 {#notes}

- `/skin`、`/snapshot`、`/gquota`、`/reload`、`/tools`、`/toolsets`、`/browser`、`/config`、`/cron`、`/skills`、`/platforms`、`/paste`、`/image`、`/statusbar`、`/plugins`、`/busy`、`/indicator`、`/redraw`、`/clear`、`/history`、`/save`、`/copy` 和 `/quit` 是**仅限 CLI** 的命令。
- `/verbose` **默认仅限 CLI**，但可以通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 来为消息平台启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置中。
- `/sethome`、`/update`、`/restart`、`/approve`、`/deny` 和 `/commands` 是**仅限消息平台**的命令。
- `/status`、`/background`、`/queue`、`/steer`、`/voice`、`/reload-mcp`、`/rollback`、`/debug`、`/fast`、`/footer`、`/curator` 和 `/yolo` 在 **CLI 和消息网关中均可使用**。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。
