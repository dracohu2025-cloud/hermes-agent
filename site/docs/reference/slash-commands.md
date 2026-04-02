---
sidebar_position: 2
title: "斜杠命令参考"
description: "交互式 CLI 和消息斜杠命令的完整参考"
---

# 斜杠命令参考

Hermes 有两个斜杠命令入口，均由 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI 斜杠命令** — 由 `cli.py` 分发，自动补全来自注册表
- **消息斜杠命令** — 由 `gateway/run.py` 分发，帮助文本和平台菜单由注册表生成

已安装的技能也会作为动态斜杠命令暴露在两个入口上。其中包括内置技能如 `/plan`，它会打开计划模式，并将 Markdown 格式的计划保存到相对于当前工作区/后端工作目录的 `.hermes/plans/` 下。

## 交互式 CLI 斜杠命令

在 CLI 中输入 `/` 可打开自动补全菜单。内置命令不区分大小写。

### 会话

| 命令 | 说明 |
|---------|-------------|
| `/new`（别名：`/reset`） | 开始一个新会话（全新会话 ID + 历史） |
| `/clear` | 清屏并开始新会话 |
| `/history` | 显示对话历史 |
| `/save` | 保存当前对话 |
| `/retry` | 重试上一条消息（重新发送给 Agent） |
| `/undo` | 删除最后一次用户/助手的交流 |
| `/title` | 设置当前会话标题（用法：/title 我的会话名称） |
| `/compress` | 手动压缩对话上下文（刷新记忆 + 摘要） |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [数字]） |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue <prompt>`（别名：`/q`） | 将提示排队到下一轮（不会中断当前 Agent 响应）。**注意：** `/q` 被 `/queue` 和 `/quit` 同时占用，后注册的生效，因此实际 `/q` 解析为 `/quit`。请显式使用 `/queue`。 |
| `/resume [name]` | 恢复之前命名的会话 |
| `/statusbar`（别名：`/sb`） | 切换上下文/模型状态栏开关 |
| `/background <prompt>`（别名：`/bg`） | 在独立后台会话中运行提示。Agent 独立处理你的提示，当前会话保持空闲以便其他工作。任务完成后结果会以面板形式显示。详见 [CLI 后台会话](/user-guide/cli#background-sessions)。 |
| `/plan [request]` | 加载内置 `plan` 技能，编写 Markdown 计划而非执行任务。计划保存在相对于当前工作区/后端工作目录的 `.hermes/plans/` 下。 |

### 配置

| 命令 | 说明 |
|---------|-------------|
| `/config` | 显示当前配置 |
| `/model [model-name]` | 显示或切换当前模型。支持：`/model claude-sonnet-4`，`/model provider:model`（切换提供商），`/model custom:model`（自定义端点），`/model custom:name:model`（命名自定义提供商），`/model custom`（自动检测端点） |
| `/provider` | 显示可用提供商及当前提供商 |
| `/prompt` | 查看/设置自定义系统提示 |
| `/personality` | 设置预定义人格 |
| `/verbose` | 循环切换工具进度显示：关闭 → 新 → 全部 → 详细。可通过配置[为消息启用](#notes)。 |
| `/reasoning` | 管理推理强度和显示（用法：/reasoning [level\|show\|hide]） |
| `/skin` | 显示或切换显示皮肤/主题 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式和语音播放。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令确认提示。 |

### 工具与技能

| 命令 | 说明 |
|---------|-------------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或禁用/启用当前会话的特定工具。禁用工具会从 Agent 的工具集移除并触发会话重置。 |
| `/toolsets` | 列出可用工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chrome CDP 连接。`connect` 连接到运行中的 Chrome 实例（默认：`ws://localhost:9222`），`disconnect` 断开连接，`status` 显示当前连接状态。若未检测到调试器则自动启动 Chrome。 |
| `/skills` | 搜索、安装、查看或管理在线注册表中的技能 |
| `/cron` | 管理定时任务（列出、添加/创建、编辑、暂停、恢复、运行、删除） |
| `/reload-mcp`（别名：`/reload_mcp`） | 从 config.yaml 重新加载 MCP 服务器 |
| `/plugins` | 列出已安装插件及其状态 |

### 信息

| 命令 | 说明 |
|---------|-------------|
| `/help` | 显示此帮助信息 |
| `/usage` | 显示令牌使用情况、费用明细和会话时长 |
| `/insights` | 显示使用洞察和分析（最近 30 天） |
| `/platforms`（别名：`/gateway`） | 显示网关/消息平台状态 |
| `/paste` | 检查剪贴板中的图片并附加 |
| `/profile` | 显示当前配置文件名称和主目录 |

### 退出

| 命令 | 说明 |
|---------|-------------|
| `/quit` | 退出 CLI（同 `/exit`）。关于 `/q` 的说明见上文 `/queue` 部分。 |

### 动态 CLI 斜杠命令

| 命令 | 说明 |
|---------|-------------|
| `/<skill-name>` | 以按需命令加载任何已安装技能。例如：`/gif-search`、`/github-pr-workflow`、`/excalidraw`。 |
| `/skills ...` | 从注册表和官方可选技能目录搜索、浏览、查看、安装、审计、发布和配置技能。 |

### 快速命令

用户定义的快速命令来自 `~/.hermes/config.yaml` 中的 `quick_commands`，也可作为斜杠命令使用。这些命令在分发时解析，不会显示在内置自动补全/帮助表中。

## 消息斜杠命令

消息网关支持在 Telegram、Discord、Slack、WhatsApp、Signal、Email 和 Home Assistant 聊天中使用以下内置命令：

| 命令 | 说明 |
|---------|-------------|
| `/new` | 开始新对话。 |
| `/reset` | 重置对话历史。 |
| `/status` | 显示会话信息。 |
| `/stop` | 终止所有后台进程并中断正在运行的 Agent。 |
| `/model [provider:model]` | 显示或切换模型。支持提供商切换（`/model zai:glm-5`）、自定义端点（`/model custom:model`）、命名自定义提供商（`/model custom:local:qwen`）和自动检测（`/model custom`）。 |
| `/provider` | 显示提供商可用性和认证状态。 |
| `/personality [name]` | 为会话设置人格覆盖。 |
| `/retry` | 重试上一条消息。 |
| `/undo` | 删除最后一次交流。 |
| `/sethome`（别名：`/set-home`） | 将当前聊天标记为平台主频道，用于消息投递。 |
| `/compress` | 手动压缩对话上下文。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复之前命名的会话。 |
| `/usage` | 显示令牌使用、估算费用明细（输入/输出）、上下文窗口状态和会话时长。 |
| `/insights [days]` | 显示使用分析。 |
| `/reasoning [level\|show\|hide]` | 更改推理强度或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 管理 Discord 语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/background <prompt>` | 在独立后台会话中运行提示。任务完成后结果会返回同一聊天。详见 [消息后台会话](/user-guide/messaging/#background-sessions)。 |
| `/plan [request]` | 加载内置 `plan` 技能，编写 Markdown 计划而非执行任务。计划保存在相对于当前工作区/后端工作目录的 `.hermes/plans/` 下。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 从配置重新加载 MCP 服务器。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令确认提示。 |
| `/commands [page]` | 浏览所有命令和技能（分页显示）。 |
| `/approve [session\|always]` | 批准并执行待处理的危险命令。`session` 仅本会话批准；`always` 加入永久允许列表。 |
| `/deny` | 拒绝待处理的危险命令。 |
| `/update` | 更新 Hermes Agent 到最新版本。 |
| `/help` | 显示消息帮助。 |
| `/<skill-name>` | 按名称调用任何已安装技能。 |
## 说明 {#notes}

- `/skin`、`/tools`、`/toolsets`、`/browser`、`/config`、`/prompt`、`/cron`、`/skills`、`/platforms`、`/paste`、`/statusbar` 和 `/plugins` 是 **仅限 CLI** 的命令。
- `/verbose` 默认是 **仅限 CLI**，但可以通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 来为消息平台启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置中。
- `/status`、`/sethome`、`/update`、`/approve`、`/deny` 和 `/commands` 是 **仅限消息平台** 的命令。
- `/background`、`/voice`、`/reload-mcp`、`/rollback` 和 `/yolo` 在 CLI 和消息网关中都可用。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。
