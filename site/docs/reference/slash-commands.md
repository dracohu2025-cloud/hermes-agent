---
sidebar_position: 2
title: "斜杠命令参考"
description: "交互式 CLI 和消息斜杠命令的完整参考"
---

# 斜杠命令参考 {#slash-commands-reference}

Hermes 有两处斜杠命令入口，都由 `hermes_cli/commands.py` 中的核心 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI 斜杠命令** — 由 `cli.py` 分发，支持注册表的自动补全
- **消息斜杠命令** — 由 `gateway/run.py` 分发，帮助文本和平台菜单均从注册表生成

已安装的技能也会作为动态斜杠命令暴露在两处入口上。这包括内置技能如 `/plan`，它会进入计划模式，并将 Markdown 计划保存到当前工作区/后端工作目录下的 `.hermes/plans/` 中。

## 交互式 CLI 斜杠命令 {#interactive-cli-slash-commands}

在 CLI 中输入 `/` 打开自动补全菜单。内置命令不区分大小写。

### 会话 {#session}

| 命令 | 说明 |
|---------|-------------|
| `/new`（别名：`/reset`） | 开始新会话（新的会话 ID + 历史记录） |
| `/clear` | 清屏并开始新会话 |
| `/history` | 显示对话历史 |
| `/save` | 保存当前对话 |
| `/retry` | 重试上一条消息（重新发送给 Agent） |
| `/undo` | 删除最后一轮用户/助手对话 |
| `/title` | 为当前会话设置标题（用法：/title 我的会话名称） |
| `/compress [聚焦主题]` | 手动压缩对话上下文（刷新记忆 + 总结）。可选的聚焦主题可限定总结保留的内容范围。 |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [编号]） |
| `/snapshot [create\|restore &lt;id&gt;\|prune]`（别名：`/snap`） | 创建或恢复 Hermes 配置/状态的快照。`create [标签]` 保存快照，`restore &lt;id&gt;` 回退到该快照，`prune [N]` 删除旧快照，或不传参数列出所有快照。 |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue &lt;prompt&gt;`（别名：`/q`） | 将提示词排队到下一轮（不会打断当前 Agent 的响应）。**注意：** `/q` 同时被 `/queue` 和 `/quit` 注册；后注册的生效，因此实际使用中 `/q` 会解析为 `/quit`。请显式使用 `/queue`。 |
| `/resume [name]` | 恢复之前命名的会话 |
| `/status` | 显示会话信息 |
| `/agents`（别名：`/tasks`） | 显示当前会话中的活跃 Agent 和正在运行的任务。 |
| `/background &lt;prompt&gt;`（别名：`/bg`） | 在独立的背景会话中运行提示词。Agent 独立处理你的提示词 —— 当前会话保持空闲，可以做其他事情。任务完成后结果会以面板形式显示。详见 [CLI 背景会话](/user-guide/cli#background-sessions)。 |
| `/btw &lt;question&gt;` | 使用会话上下文进行临时侧问（不使用工具，不持久化）。适合快速澄清问题，而不会影响对话历史。 |
| `/plan [request]` | 加载内置的 `plan` 技能来编写 Markdown 计划，而不是直接执行工作。计划会保存到当前工作区/后端工作目录下的 `.hermes/plans/` 中。 |
| `/branch [name]`（别名：`/fork`） | 从当前会话分支出新会话（探索不同路径） |

### 配置 {#configuration}

| 命令 | 说明 |
|---------|-------------|
| `/config` | 显示当前配置 |
| `/model [model-name]` | 显示或切换当前模型。支持：`/model claude-sonnet-4`、`/model provider:model`（切换提供商）、`/model custom:model`（自定义端点）、`/model custom:name:model`（命名自定义提供商）、`/model custom`（从端点自动检测）。使用 `--global` 可将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的提供商之间切换。要添加新提供商，请退出会话后在终端运行 `hermes model`。 |
| `/provider` | 显示可用提供商和当前提供商 |
| `/personality` | 设置预定义的个性 |
| `/verbose` | 循环切换工具进度显示：关闭 → 新增 → 全部 → 详细。可通过配置[为消息模式启用](#notes)。 |
| `/fast [normal\|fast\|status]` | 切换快速模式 —— OpenAI 优先处理 / Anthropic 快速模式。选项：`normal`、`fast`、`status`。 |
| `/reasoning` | 管理推理努力和显示（用法：/reasoning [level\|show\|hide]） |
| `/skin` | 显示或切换显示皮肤/主题 |
| `/statusbar`（别名：`/sb`） | 打开或关闭上下文/模型状态栏 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式和语音播报。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式 —— 跳过所有危险命令的确认提示。 |
### 工具与技能 {#tools-skills}

| 命令 | 说明 |
|---------|-------------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或禁用/启用当前会话的特定工具。禁用工具会将其从 Agent 的工具集中移除，并触发会话重置。 |
| `/toolsets` | 列出可用工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chrome CDP 连接。`connect` 将浏览器工具附加到正在运行的 Chrome 实例（默认：`ws://localhost:9222`）。`disconnect` 断开连接。`status` 显示当前连接状态。如果未检测到调试器，会自动启动 Chrome。 |
| `/skills` | 搜索、安装、检查或管理在线注册表中的技能 |
| `/cron` | 管理定时任务（列出、添加/创建、编辑、暂停、恢复、运行、删除） |
| `/reload-mcp`（别名：`/reload_mcp`） | 从 config.yaml 重新加载 MCP 服务器 |
| `/reload` | 将 `.env` 变量重新加载到运行中的会话（无需重启即可获取新的 API 密钥） |
| `/plugins` | 列出已安装的插件及其状态 |

### 信息 {#info}

| 命令 | 说明 |
|---------|-------------|
| `/help` | 显示此帮助信息 |
| `/usage` | 显示 token 使用量、成本明细和会话时长 |
| `/insights` | 显示使用洞察和分析（最近 30 天） |
| `/platforms`（别名：`/gateway`） | 显示网关/消息平台状态 |
| `/paste` | 检查剪贴板中的图片并附加 |
| `/copy [number]` | 将最后一次助手回复复制到剪贴板（或用数字指定倒数第 N 次）。仅 CLI 可用。 |
| `/image &lt;path&gt;` | 附加本地图片文件，用于下一次提示。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享链接。在消息中也可用。 |
| `/profile` | 显示当前配置文件名和主目录 |
| `/gquota` | 显示 Google Gemini Code Assist 配额使用情况（带进度条）（仅在 `google-gemini-cli` provider 激活时可用）。 |

### 退出 {#exit}

| 命令 | 说明 |
|---------|-------------|
| `/quit` | 退出 CLI（也可用：`/exit`）。关于 `/q` 的说明见上文 `/queue` 部分。 |

### 动态 CLI 斜杠命令 {#dynamic-cli-slash-commands}

| 命令 | 说明 |
|---------|-------------|
| `/&lt;skill-name&gt;` | 将任何已安装的技能作为按需命令加载。例如：`/gif-search`、`/github-pr-workflow`、`/excalidraw`。 |
| `/skills ...` | 从注册表和官方可选技能目录中搜索、浏览、检查、安装、审计、发布和配置技能。 |

### 快捷命令 {#quick-commands}

用户定义的快捷命令可以将短别名映射到更长的提示。在 `~/.hermes/config.yaml` 中配置：

```yaml
quick_commands:
  review: "Review my latest git diff and suggest improvements"
  deploy: "Run the deployment script at scripts/deploy.sh and verify the output"
  morning: "Check my calendar, unread emails, and summarize today's priorities"
```

然后在 CLI 中输入 `/review`、`/deploy` 或 `/morning`。快捷命令在分派时解析，不会显示在内置的自动补全/帮助表格中。

### 别名解析 {#alias-resolution}

命令支持前缀匹配：输入 `/h` 会解析为 `/help`，`/mod` 会解析为 `/model`。当前缀有歧义（匹配多个命令）时，注册表顺序中的第一个匹配胜出。完整命令名和已注册的别名始终优先于前缀匹配。

## 消息斜杠命令 {#messaging-slash-commands}

消息网关支持在 Telegram、Discord、Slack、WhatsApp、Signal、Email 和 Home Assistant 聊天中使用以下内置命令：

| 命令 | 说明 |
|---------|-------------|
| `/new` | 开始新对话。 |
| `/reset` | 重置对话历史。 |
| `/status` | 显示会话信息。 |
| `/stop` | 终止所有正在运行的后台进程，并中断正在运行的 Agent。 |
| `/model [provider:model]` | 显示或更改模型。支持切换 provider（`/model zai:glm-5`）、自定义端点（`/model custom:model`）、命名自定义 provider（`/model custom:local:qwen`）和自动检测（`/model custom`）。使用 `--global` 可将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的 provider 之间切换。要添加新 provider 或设置 API 密钥，请在终端中使用 `hermes model`（在聊天会话外）。 |
| `/provider` | 显示 provider 可用性和认证状态。 |
| `/personality [name]` | 为会话设置个性覆盖。 |
| `/fast [normal\|fast\|status]` | 切换快速模式 —— OpenAI 优先处理 / Anthropic 快速模式。 |
| `/retry` | 重试上一条消息。 |
| `/undo` | 删除最后一次对话。 |
| `/sethome`（别名：`/set-home`） | 将当前聊天标记为投递的平台主频道。 |
| `/compress [focus topic]` | 手动压缩对话上下文。可选的聚焦主题可缩小摘要保留的范围。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复之前命名的会话。 |
| `/usage` | 显示 token 使用量、预估成本明细（输入/输出）、上下文窗口状态和会话时长。 |
| `/insights [days]` | 显示使用分析。 |
| `/reasoning [level\|show\|hide]` | 更改推理强度或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 管理 Discord 语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/snapshot [create\|restore &lt;id&gt;\|prune]`（别名：`/snap`） | 创建或恢复 Hermes 配置/状态的快照。 |
| `/background &lt;prompt&gt;` | 在独立的背景会话中运行提示。任务完成后，结果会返回到同一聊天中。详见 [消息后台会话](/user-guide/messaging/#background-sessions)。 |
| `/plan [request]` | 加载内置的 `plan` 技能来编写 markdown 计划，而不是直接执行工作。计划保存在活动工作区/后端工作目录下的 `.hermes/plans/` 中。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 从配置重新加载 MCP 服务器。 |
| `/reload` | 将 `.env` 变量重新加载到运行中的会话。 |
| `/yolo` | 切换 YOLO 模式 —— 跳过所有危险命令的确认提示。 |
| `/commands [page]` | 浏览所有命令和技能（分页）。 |
| `/approve [session\|always]` | 批准并执行待处理的危险命令。`session` 仅批准当前会话；`always` 添加到永久允许列表。 |
| `/deny` | 拒绝待处理的危险命令。 |
| `/update` | 将 Hermes Agent 更新到最新版本。 |
| `/restart` | 在完成活跃运行后优雅地重启网关。网关重新上线后，会向请求者的聊天/线程发送确认。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享链接。 |
| `/help` | 显示消息帮助。 |
| `/&lt;skill-name&gt;` | 按名称调用任何已安装的技能。 |
## 说明 {#notes}

- `/skin`、`/tools`、`/toolsets`、`/browser`、`/config`、`/cron`、`/skills`、`/platforms`、`/paste`、`/image`、`/statusbar` 和 `/plugins` 是 **仅 CLI 可用** 的命令。
- `/verbose` **默认仅 CLI 可用**，但可以通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 来在消息平台中启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置中。
- `/sethome`、`/update`、`/restart`、`/approve`、`/deny` 和 `/commands` 是 **仅消息平台可用** 的命令。
- `/status`、`/background`、`/voice`、`/reload-mcp`、`/rollback`、`/snapshot`、`/debug`、`/fast` 和 `/yolo` 在 **CLI 和消息网关两者中均可使用**。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。
