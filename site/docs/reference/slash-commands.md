---
sidebar_position: 2
title: "斜杠命令参考"
description: "交互式 CLI 和消息斜杠命令的完整参考"
---

<a id="slash-commands-reference"></a>
# 斜杠命令参考

Hermes 有两个斜杠命令界面，均由 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 驱动：

- **交互式 CLI 斜杠命令** — 由 `cli.py` 分发，支持从注册表自动补全
- **消息斜杠命令** — 由 `gateway/run.py` 分发，其帮助文本和平台菜单由注册表生成

已安装的技能也会作为动态斜杠命令暴露在两个界面上。这包括内置技能，如 `/plan`，它会打开计划模式并在 `.hermes/plans/` 目录下（相对于活动工作区/后端工作目录）保存 Markdown 计划。

<a id="permissions-and-admin-user-split"></a>
## 权限与管理员/普通用户划分

每个支持按用户白名单的消息平台（Telegram、Discord、Slack、Matrix、Mattermost、Signal 等）也支持两级斜杠命令划分：**管理员**可以使用所有已注册的命令，**普通用户**只能使用你列在 `user_allowed_commands` 中的命令（加上始终允许的 `/help` 和 `/whoami`）。在 `~/.hermes/gateway-config.yaml` 中该平台的 `extra:` 块内配置 `allow_admin_from` 和 `user_allowed_commands`（以及按组的等价项 `group_allow_admin_from` / `group_user_allowed_commands`）。

各平台的文档示例 —— 结构在所有平台上是一致的：

- [Telegram](../user-guide/messaging/telegram.md#slash-command-access-control)
- [Discord](../user-guide/messaging/discord.md)
- [Slack](../user-guide/messaging/slack.md)
- [Matrix](../user-guide/messaging/matrix.md)
- [Mattermost](../user-guide/messaging/mattermost.md)
- [Signal](../user-guide/messaging/signal.md)

如果某个作用域的 `allow_admin_from` 未设置，则该作用域保持无限制的向后兼容模式 —— 所有允许的用户都可以运行任何命令。

<a id="interactive-cli-slash-commands"></a>
## 交互式 CLI 斜杠命令

在 CLI 中输入 `/` 打开自动补全菜单。内置命令不区分大小写。

<a id="session"></a>
### 会话

| 命令 | 描述 |
|---------|-------------|
| `/new [name]`（别名：`/reset`） | 开始一个新会话（新的会话 ID + 历史记录）。可选的 `[name]` 设置初始会话标题 —— 例如 `/new my-experiment` 会打开一个标题已设为 `my-experiment` 的新会话，这样稍后通过 `/resume` 或 `/sessions` 更容易找到。 |
| `/clear` | 清屏并开始一个新会话 |
| `/history` | 显示对话历史 |
| `/save` | 保存当前对话 |
| `/retry` | 重试最后一条消息（重新发送给 Agent） |
| `/undo` | 移除最后一次用户/助手的对话轮次 |
| `/title` | 为当前会话设置标题（用法：/title 我的会话名称） |
| `/compress [关注主题]` | 手动压缩对话上下文（刷新记忆 + 总结）。可选的关注主题会限制总结保留的内容范围。 |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [数字]） |
| `/snapshot [create\|restore &lt;id&gt;\|prune]`（别名：`/snap`） | 创建或恢复 Hermes 配置/状态的状态快照。`create [标签]` 保存快照，`restore &lt;id&gt;` 恢复到该快照，`prune [N]` 移除旧快照，不带参数则列出所有快照。 |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue <提示>`（别名：`/q`） | 将提示排入下一轮队列（不会中断当前 Agent 的响应）。 |
| `/steer <提示>` | 注入一条中间运行时的提示，该提示会在**下一个工具调用之后**到达 Agent —— 不中断，不新增用户轮次。在当前工具完成后，文本会追加到最后一次工具结果的内容中，从而在不打断当前工具调用循环的前提下为 Agent 提供新上下文。可在任务中途调整方向（例如，Agent 正在运行测试时，提示“专注于 auth 模块”）。 |
| `/goal <文本>` | 设置一个 Hermes 在多个轮次中一直努力完成的长期目标 —— 相当于 Ralph 循环的实现。每轮之后，一个辅助判断模型会决定目标是否完成；如果未完成，Hermes 会自动继续。子命令：`/goal status`、`/goal pause`、`/goal resume`、`/goal clear`。预算默认 20 轮（`goals.max_turns`）；任何真实的用户消息会抢占继续循环，状态在 `/resume` 后得以保留。完整教程请参阅[持久目标](/user-guide/features/goals)。 |
| `/subgoal <文本>` | 在循环过程中追加一条用户提供的标准到当前目标。继续提示会逐字向 Agent 展示所有子目标，判断模型会将其纳入 DONE/CONTINUE 的判断中 —— 因此直到原始目标**和**每个子目标都满足时，目标才被视为完成。子命令：`/subgoal`（列出）、`/subgoal remove &lt;N&gt;`、`/subgoal clear`。需要有一个活跃的 `/goal`。 |
| `/resume [名称]` | 恢复一个之前命名的会话 |
| `/sessions` | 在交互式选择器中浏览并恢复之前的会话 |
| `/redraw` | 强制重绘整个 UI（可恢复因 tmux 调整大小、鼠标选择残留等导致的终端偏移问题） |
| `/status` | 显示会话信息 —— 模型、提供商、配置文件、会话 ID、工作目录、标题、创建/更新时间戳、token 总数、Agent 运行状态 —— 随后是一个本地**会话摘要**块（最近用户/助手轮次数、工具结果数、使用的顶级工具、最近触及的几个文件、最新的用户提示、以及最新的助手回复）。该摘要是从内存中的对话本地计算的，无需 LLM 调用，不影响提示缓存。 |
| `/agents`（别名：`/tasks`） | 显示当前会话中的活跃 Agent 和正在运行的任务。 |
| `/background <提示>`（别名：`/bg`、`/btw`） | 在单独的后台会话中运行提示。Agent 独立处理你的提示 —— 当前会话保持空闲可做其他事情。任务完成后结果以面板形式显示。参见 [CLI 后台会话](/user-guide/cli#background-sessions)。 |
| `/branch [名称]`（别名：`/fork`） | 分支当前会话（探索另一条路径） |
| `/handoff <平台>` | **仅限 CLI。** 将当前会话交接到消息平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix）。网关会立即接手，在平台支持线程的情况下创建一个新线程（Telegram 主题、Discord 文本频道线程、Slack 消息锚定线程），将目标重新绑定到你的 CLI session_id，以便完整的角色感知对话记录得以重放，并伪造一个合成用户轮次，使 Agent 确认它在新的地方工作。成功时 CLI 会干净退出，并给出 `/resume` 提示；可随时通过 `/resume <标题>` 在本地恢复。在轮次中拒绝执行。要求网关正在运行，并且目标平台已配置主频道（从目标聊天中使用 `/sethome`）。参见[跨平台交接](/user-guide/sessions#cross-platform-handoff)。 |
<a id="configuration"></a>
### 配置

| 命令 | 描述 |
|------|------|
| `/config` | 显示当前配置 |
| `/model [model-name]` | 显示或切换当前模型。支持：`/model claude-sonnet-4`、`/model provider:model`（切换提供商）、`/model custom:model`（自定义端点）、`/model custom:name:model`（命名自定义提供商）、`/model custom`（从端点自动检测）以及用户定义的别名（`/model fav`、`/model grok`——参见[自定义模型别名](#custom-model-aliases)）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的提供商之间切换。要添加新提供商，请退出会话并在终端中运行 `hermes model`。 |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | 切换针对 OpenAI/Codex 模型的可选 [Codex app-server 运行时](../user-guide/features/codex-app-server-runtime)。`auto`（默认）使用 Hermes 的标准聊天补全；`codex_app_server` 将任务移交给 `codex app-server` 子进程，以支持原生 shell、apply_patch、ChatGPT 订阅认证以及迁移后的 Codex 插件。下次会话生效。 |
| `/personality` | 设置预定义人格 |
| `/verbose` | 循环切换工具进度显示：关闭 → 新的 → 全部 → 详细。可通过配置[为消息启用](#notes)。 |
| `/fast [normal\|fast\|status]` | 切换快速模式——OpenAI 优先处理 / Anthropic 快速模式。选项：`normal`、`fast`、`status`。 |
| `/reasoning` | 管理推理力度与显示（用法：/reasoning [level\|show\|hide]） |
| `/skin` | 显示或切换显示皮肤/主题 |
| `/statusbar`（别名：`/sb`） | 打开或关闭上下文/模型状态栏 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 语音模式与语音播放。录音使用 `voice.record_key`（默认：`Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式——跳过所有危险命令的确认提示。 |
| `/footer [on\|off\|status]` | 在最终回复中切换网关运行时元数据页脚（显示模型、工具数量、耗时）。 |
| `/busy [queue\|steer\|interrupt\|status]` | 仅 CLI：控制 Hermes 工作时按下 Enter 的行为——将新消息排队、中途引导或立即中断。 |
| `/indicator [kaomoji\|emoji\|unicode\|ascii]` | 仅 CLI：选择 TUI 忙碌指示器样式。 |

<a id="tools-skills"></a>
### 工具与技能

| 命令 | 描述 |
|------|------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或为当前会话禁用/启用特定工具。禁用工具会将其从 Agent 的工具集中移除，并触发会话重置。 |
| `/toolsets` | 列出可用工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地 Chromium 系列 CDP 连接。`connect` 将浏览器工具附加到正在运行的 Chrome、Brave、Chromium 或 Edge 实例（默认：`http://127.0.0.1:9222`）。`disconnect` 断开连接。`status` 显示当前连接状态。如果未检测到调试器，则自动启动受支持的 Chromium 系列浏览器。 |
| `/skills` | 从在线注册表搜索、安装、检查或管理技能 |
| `/cron` | 管理计划任务（列出、添加/创建、编辑、暂停、恢复、运行、移除） |
| `/curator` | 后台技能维护——`status`、`run`、`pin`、`archive`。参见 [Curator](/user-guide/features/curator)。 |
| `/kanban <动作>` | 无需离开聊天即可驱动多配置、多项目协作面板。完整的 `hermes kanban` 功能均可用：`/kanban list`、`/kanban show t_abc`、`/kanban create "标题" --assignee X`、`/kanban comment t_abc "文本"`、`/kanban unblock t_abc`、`/kanban dispatch` 等。支持多面板：`/kanban boards list`、`/kanban boards create &lt;slug&gt;`、`/kanban boards switch &lt;slug&gt;`、`/kanban --board &lt;slug&gt; <动作>`。参见 [Kanban 斜杠命令](/user-guide/features/kanban#kanban-slash-command)。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 从 config.yaml 重新加载 MCP 服务器 |
| `/reload-skills`（别名：`/reload_skills`） | 重新扫描 `~/.hermes/skills/` 以检测新安装或移除的技能 |
| `/reload` | 将 `.env` 变量重新加载到正在运行的会话中（无需重启即可获取新的 API 密钥） |
| `/plugins` | 列出已安装的插件及其状态 |
<a id="info"></a>
### 信息

| 命令 | 描述 |
|------|------|
| `/help` | 显示此帮助信息 |
| `/usage` | 显示 Token 用量、费用明细、会话时长，以及——当活跃提供商支持时——一个 **账户限制** 部分，其中包含从提供商 API 实时拉取的剩余配额/积分/套餐用量。 |
| `/insights` | 显示使用洞察与分析（最近 30 天） |
| `/platforms`（别名：`/gateway`） | 显示网关/消息平台状态（仅 CLI 摘要视图）。 |
| `/platform &lt;list\|pause\|resume&gt; [name]` | 操作正在运行的网关平台。`/platform list` 列出所有适配器及其状态（运行中、断路器暂停、手动暂停）；`/platform pause &lt;name&gt;` 停止向该适配器分发新消息但不卸载它；`/platform resume &lt;name&gt;` 重新启用它。当适配器的断路器因重复的可重试失败（网络/速率限制/5xx）而跳闸时，网关也会自动暂停该适配器——一旦上游恢复正常，使用 `/platform resume &lt;name&gt;` 清除断路器。在网关可访问的任何地方（CLI 会话、Telegram、Discord 等）均可使用。 |
| `/paste` | 附加剪贴板图片 |
| `/copy [number]` | 将最后一条助手回复复制到剪贴板（或指定数字，复制倒数第 N 条）。仅 CLI。 |
| `/image &lt;path&gt;` | 为下一条提示附加本地图片文件。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享链接。消息平台中也可用。 |
| `/profile` | 显示当前配置文件名及主目录 |
| `/gquota` | 显示 Google Gemini Code Assist 配额使用情况及进度条（仅当 `google-gemini-cli` 提供商激活时可用）。 |

<a id="exit"></a>
### 退出

| 命令 | 描述 |
|------|------|
| `/quit` | 退出 CLI（也可用 `/exit`）。关于 `/q` 的说明请参见上方 `/queue` 部分。传递 `--delete`（或 `-d`）——例如 `/exit --delete`——可在退出前永久删除当前会话的 SQLite 历史记录和磁盘上的对话记录。适用于隐私敏感或一次性任务。 |

<a id="dynamic-cli-slash-commands"></a>
### 动态 CLI 斜杠命令

| 命令 | 描述 |
|------|------|
| `/&lt;skill-name&gt;` | 将任何已安装的技能作为按需命令加载。示例：`/gif-search`、`/github-pr-workflow`、`/excalidraw`。 |
| `/skills ...` | 从注册表和官方可选技能目录中搜索、浏览、检查、安装、审计、发布和配置技能。 |

<a id="quick-commands"></a>
### 快速命令

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

然后在 CLI 或消息平台中输入 `/status`、`/deploy` 或 `/inbox`。快速命令在分发时解析，可能不会出现在每个内置的自动补全/帮助表中。

仅字符串的提示快捷方式不支持作为快速命令。将较长的可复用提示放入技能中，或使用 `type: alias` 指向现有的斜杠命令。
<a id="custom-model-aliases"></a>
### 自定义模型别名

为你常用的模型定义简短名称，然后在 CLI 或任何消息平台中使用 `/model <别名>` 来调用它们。别名在会话专属（默认）和 `--global` 开关下的工作方式完全相同。

支持两种配置格式：

**完整格式** — 固定一个确切的模型、提供商，以及可选的 base URL。将其放入 `~/.hermes/config.yaml`：

```yaml
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
  ollama-qwen:
    model: qwen3-coder:30b
    provider: custom
    base_url: http://localhost:11434/v1
```

**简短格式** — 在一个字符串中使用 `provider/model`。无需编辑 YAML，直接从 shell 设置：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

然后在聊天中使用：

```
/model fav            # 仅当前会话
/model grok --global  # 同时将当前模型更改持久化到 config.yaml
```

用户定义的别名优先级高于内置的简短名称，因此将别名命名为 `sonnet`、`kimi`、`opus` 等会覆盖内置名称。别名名称不区分大小写。

<a id="alias-resolution"></a>
### 别名解析

命令支持前缀匹配：输入 `/h` 解析为 `/help`，`/mod` 解析为 `/model`。当前缀有歧义（匹配多个命令）时，按注册顺序第一个匹配的胜出。完整的命令名称和已注册的别名始终优先于前缀匹配。

<a id="messaging-slash-commands"></a>
## 消息斜杠命令

消息网关在 Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant 和 Teams 聊天中支持以下内置命令：

| 命令 | 描述 |
|---------|-------------|
| `/new` | 开始一个新的对话。 |
| `/reset` | 重置对话历史。 |
| `/status` | 显示会话信息，后跟一个本地的 **会话摘要** 块（最近的轮次计数、最常用的工具、接触过的文件、最新的提示词和回复）。 |
| `/stop` | 终止所有正在运行的后台进程并中断正在运行的 Agent。 |
| `/model [provider:model]` | 显示或更改模型。支持提供商切换（`/model zai:glm-5`）、自定义端点（`/model custom:model`）、命名自定义提供商（`/model custom:local:qwen`）、自动检测（`/model custom`）以及用户定义的别名（`/model fav`、`/model grok` — 参见[自定义模型别名](#custom-model-aliases)）。使用 `--global` 将更改持久化到 config.yaml。**注意：** `/model` 只能在已配置的提供商之间切换。要添加新提供商或设置 API 密钥，请从终端（聊天会话外部）使用 `hermes model`。 |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | 切换可选的 [Codex 应用服务器运行时](../user-guide/features/codex-app-server-runtime)。持久化到 config.yaml 中的 `model.openai_runtime`，并驱逐缓存的 Agent，以便下一条消息使用新的运行时。在下一次会话中生效。 |
| `/personality [name]` | 为会话设置个性叠加层。 |
| `/fast [normal\|fast\|status]` | 切换快速模式 — OpenAI 优先级处理 / Anthropic 快速模式。 |
| `/retry` | 重试上一条消息。 |
| `/undo` | 移除上一次交互。 |
| `/sethome` (别名: `/set-home`) | 将当前聊天标记为平台的主频道，用于消息投递。 |
| `/compress [focus topic]` | 手动压缩对话上下文。可选的焦点主题可以缩小摘要保留的范围。 |
| `/topic [off\|help\|session-id]` | **仅限 Telegram 私聊。** 管理用户管理的多会话主题模式。`/topic` 启用它或显示状态；`/topic off` 禁用它并清除绑定；`/topic help` 显示用法；在主题内使用 `/topic &lt;session-id&gt;` 恢复之前的会话。参见[多会话私聊模式](/user-guide/messaging/telegram#multi-session-dm-mode-topic)。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复一个之前命名的会话。 |
| `/usage` | 显示 Token 用量、预估成本明细（输入/输出）、上下文窗口状态、会话时长，以及 — 当活跃提供商支持时 — 一个 **账户限制** 部分，其中包含从提供商 API 实时拉取的剩余配额/积分。 |
| `/insights [days]` | 显示使用分析。 |
| `/reasoning [level\|show\|hide]` | 更改推理努力程度或切换推理显示。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复。`join`/`channel`/`leave` 管理 Discord 语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/background &lt;prompt&gt;` | 在单独的后台会话中运行一个提示词。任务完成后，结果会投递回同一个聊天。参见[消息后台会话](/user-guide/messaging/#background-sessions)。 |
| `/queue &lt;prompt&gt;` (别名: `/q`) | 将提示词排队到下一轮，而不中断当前轮次。 |
| `/steer &lt;prompt&gt;` | 在下一次工具调用后注入一条消息而不中断 — 模型会在其下一次迭代中获取它，而不是作为新的一轮。 |
| `/goal &lt;text&gt;` | 设置一个 Hermes 在多个轮次中持续追求的长期目标 — 这是我们对 Ralph 循环的实现。一个评判模型会在每一轮后检查；如果未完成，Hermes 会自动继续，直到完成、你暂停/清除它，或者达到轮次预算（默认 20）。子命令：`/goal status`、`/goal pause`、`/goal resume`、`/goal clear`。在 Agent 运行中执行 status/pause/clear 是安全的；设置新目标需要先执行 `/stop`。参见[持久化目标](/user-guide/features/goals)。 |
| `/footer [on\|off\|status]` | 切换最终回复上的运行时元数据页脚（显示模型、工具计数、计时）。 |
| `/curator [status\|run\|pin\|archive]` | 后台技能维护控制。 |
| `/kanban &lt;action&gt;` | 从聊天驱动多配置文件、多项目协作看板 — 参数接口与 CLI 相同。绕过运行中 Agent 的防护，因此 `/kanban unblock t_abc`、`/kanban comment t_abc "…"`、`/kanban list --mine`、`/kanban boards switch &lt;slug&gt;` 等操作可以在轮次中间执行。`/kanban create …` 会自动将发起聊天下签到新任务的终端事件。参见[看板斜杠命令](/user-guide/features/kanban#kanban-slash-command)。 |
| `/reload-mcp` (别名: `/reload_mcp`) | 从配置重新加载 MCP 服务器。 |
| `/yolo` | 切换 YOLO 模式 — 跳过所有危险命令的批准提示。 |
| `/commands [page]` | 浏览所有命令和技能（分页）。 |
| `/approve [session\|always]` | 批准并执行一个待处理的危险命令。`session` 仅批准本次会话；`always` 将其添加到永久白名单。 |
| `/deny` | 拒绝一个待处理的危险命令。 |
| `/update` | 将 Hermes Agent 更新到最新版本。 |
| `/restart` | 在排空正在运行的进程后优雅地重启网关。当网关重新上线时，它会向请求者的聊天/线程发送确认。 |
| `/debug` | 上传调试报告（系统信息 + 日志）并获取可分享的链接。 |
| `/help` | 显示消息帮助。 |
| `/&lt;skill-name&gt;` | 按名称调用任何已安装的技能。 |
<a id="notes"></a>
## 注意事项

- `/skin`、`/snapshot`、`/gquota`、`/reload`、`/tools`、`/toolsets`、`/browser`、`/config`、`/cron`、`/skills`、`/platforms`、`/paste`、`/image`、`/statusbar`、`/plugins`、`/busy`、`/indicator`、`/redraw`、`/clear`、`/history`、`/save`、`/copy`、`/handoff` 和 `/quit` 是**仅限 CLI** 的命令。
- `/verbose` **默认仅限 CLI**，但可以通过在 `config.yaml` 中设置 `display.tool_progress_command: true` 来为消息平台启用。启用后，它会循环切换 `display.tool_progress` 模式并保存到配置中。
- `/sethome`、`/update`、`/restart`、`/approve`、`/deny`、`/topic` 和 `/commands` 是**仅限消息平台**的命令。
- `/status`、`/background`、`/queue`、`/steer`、`/voice`、`/reload-mcp`、`/reload-skills`、`/rollback`、`/debug`、`/fast`、`/footer`、`/curator`、`/kanban`、`/sessions` 和 `/yolo` 在 **CLI 和消息网关中均可使用**。
- `/voice join`、`/voice channel` 和 `/voice leave` 仅在 Discord 上有意义。

<a id="confirmation-prompts-for-destructive-commands"></a>
## 破坏性命令的确认提示

CLI 在执行会丢弃未保存会话状态的斜杠命令之前会进行提示。当前的破坏性命令集如下：

| 命令 | 破坏的内容 |
|---------|------------------|
| `/clear` | 清屏并开始新会话 — 当前会话 ID 和内存中的历史记录都会丢失。 |
| `/new` / `/reset` | 开始新会话（新会话 ID + 空历史记录）。 |
| `/undo` | 从历史记录中移除最后一次用户/助手的对话。 |
| `/exit --delete` / `/quit --delete` | 退出**并**永久删除当前会话的 SQLite 历史记录和磁盘上的对话记录。 |

对于每个命令，CLI 会打开一个三选一弹窗：**批准一次**（本次继续执行）、**始终批准**（继续执行并持久化 `approvals.destructive_slash_confirm: false`，这样未来的破坏性命令无需提示即可执行）或**取消**。

在 `~/.hermes/config.yaml` 中设置 `approvals.destructive_slash_confirm: false` 可全局禁用提示；将其设置回 `true` 可重新启用。有关详细信息，请参阅[安全 — 破坏性斜杠命令确认](../user-guide/security.md#dangerous-command-approval)。
