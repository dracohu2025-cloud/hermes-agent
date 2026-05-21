---
sidebar_position: 3
title: "内置工具参考"
description: "权威的 Hermes 内置工具参考，按工具集分组"
---

<a id="built-in-tools-reference"></a>
# 内置工具参考

本页面记录了 Hermes 的内置工具，按工具集分组。可用性因平台、凭证和启用的工具集而异。

**快速数量统计（当前注册表）：** 约 70 个工具 — 10 个浏览器工具（核心）+ 2 个 CDP 门控浏览器工具、4 个文件工具、10 个 RL 工具、4 个 Home Assistant 工具、2 个终端工具、2 个 Web 工具、5 个飞书工具、7 个 Spotify 工具（由捆绑的 `spotify` 插件注册）、5 个元宝工具、7 个看板工具（在看板调度器生成 Agent 时注册）、2 个 Discord 工具，以及少数独立工具（`memory`、`clarify`、`delegate_task`、`execute_code`、`cronjob`、`session_search`、`skill_view`/`skill_manage`/`skills_list`、`text_to_speech`、`image_generate`、`video_generate`、`vision_analyze`、`video_analyze`、`mixture_of_agents`、`send_message`、`todo`、`computer_use`、`process`）。

:::tip MCP 工具
<a id="mcp-tools"></a>
除了内置工具外，Hermes 还可以从 MCP 服务器动态加载工具。MCP 工具带有前缀 `mcp_&lt;server&gt;_`（例如，`mcp_github_create_issue` 对应 `github` MCP 服务器）。请参阅 [MCP 集成](/user-guide/features/mcp) 了解配置方法。
:::

<a id="browser-toolset"></a>
## `browser` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|---------|
| `browser_back` | 在浏览器历史记录中导航到上一页。需要先调用 browser_navigate。 | — |
| `browser_click` | 点击由快照中的 ref ID（例如 '@e5'）标识的元素。ref ID 会以方括号形式显示在快照输出中。需要先调用 browser_navigate 和 browser_snapshot。 | — |
| `browser_console` | 获取当前页面的浏览器控制台输出和 JavaScript 错误。返回 console.log/warn/error/info 消息以及未捕获的 JS 异常。用于检测静默的 JavaScript 错误、失败的 API 调用和应用警告。Requi… | — |
| `browser_get_images` | 获取当前页面上所有图片的列表，包含它们的 URL 和 alt 文本。适用于查找要使用 vision 工具分析的图片。需要先调用 browser_navigate。 | — |
| `browser_navigate` | 在浏览器中导航到某个 URL。初始化会话并加载页面。必须在其他浏览器工具之前调用。对于简单的信息检索，建议优先使用 web_search 或 web_extract（更快、更便宜）。当你需要…时使用浏览器工具。 | — |
| `browser_press` | 按下键盘按键。适用于提交表单（Enter）、导航（Tab）或键盘快捷键。需要先调用 browser_navigate。 | — |
| `browser_scroll` | 按方向滚动页面。用于显示当前视口下方或上方可能存在的更多内容。需要先调用 browser_navigate。 | — |
| `browser_snapshot` | 获取当前页面无障碍树的文本化快照。返回带有 ref ID（如 @e1、@e2）的交互元素，供 browser_click 和 browser_type 使用。full=false（默认）：交互元素的紧凑视图。full=true: comp… | — |
| `browser_type` | 在由 ref ID 标识的输入字段中键入文本。先清空字段，然后键入新文本。需要先调用 browser_navigate 和 browser_snapshot。 | — |
| `browser_vision` | 截取当前页面的屏幕截图，并使用视觉 AI 进行分析。当你需要直观理解页面内容时使用——特别适用于验证码、视觉验证挑战、复杂布局，或者当文本快照不完整时。 | — |
<a id="browser-toolset-cdp-gated-tools"></a>
## `browser` 工具集（CDP 门控工具）

以下两个工具属于 `browser` 工具集，但仅在会话启动时可以通过 `/browser connect`、`browser.cdp_url` 配置、Browserbase 会话或 Camofox 访问 Chrome DevTools Protocol 端点时才注册。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `browser_cdp` | 发送原始的 Chrome DevTools Protocol 命令。当高级 `browser_*` 工具无法覆盖浏览器操作时，作为后备手段使用。参见 https://chromedevtools.github.io/devtools-protocol/ | CDP 端点 |
| `browser_dialog` | 响应原生的 JavaScript 对话框（alert / confirm / prompt / beforeunload）。先调用 `browser_snapshot`——待处理的对话框会出现在其 `pending_dialogs` 字段中。然后调用 `browser_dialog(action='accept'\|'dismiss')`。 | CDP 端点 |

<a id="clarify-toolset"></a>
## `clarify` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `clarify` | 当你需要澄清、反馈或决策才能继续时，向用户提问。支持两种模式：1. **多项选择**——最多提供 4 个选项。用户选择一个，或通过第 5 个“其他”选项自行输入答案。2.… | — |

<a id="codeexecution-toolset"></a>
## `code_execution` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `execute_code` | 运行一个 Python 脚本，该脚本可以编程方式调用 Hermes 工具。当你需要连续 3 次以上调用工具并在调用之间添加处理逻辑，需要过滤/缩减大量工具输出以避免占用上下文，需要条件分支（… | — |

<a id="cronjob-toolset"></a>
## `cronjob` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `cronjob` | 统一的任务调度管理器。使用 `action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"` 或 `"remove"` 来管理任务。支持绑定一个或多个技能的任务，使用 `skills=[]` 更新任务会清除已绑定的技能。Cron 运行会在全新的会话中执行，不附带当前聊天上下文。 | — |

<a id="delegation-toolset"></a>
## `delegation` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `delegate_task` | 生成一个或多个子 Agent，在隔离的上下文中处理任务。每个子 Agent 拥有自己的对话、终端会话和工具集。只返回最终的摘要——中间工具结果不会进入你的上下文窗口。两… | — |

<a id="feishudoc-toolset"></a>
## `feishu_doc` 工具集

范围限定在飞书文档评论智能回复处理器（`gateway/platforms/feishu_comment.py`）中。不会暴露在 `hermes-cli` 或常规的飞书聊天适配器上。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `feishu_doc_read` | 根据给定的 file_type 和 token，读取飞书/Lark 文档（Docx、Doc 或 Sheet）的全部文本内容。 | 飞书应用凭证 |

<a id="feishudrive-toolset"></a>
## `feishu_drive` 工具集

范围限定在飞书文档评论处理器中。驱动对云盘文件的评论读写操作。
| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `feishu_drive_add_comment` | 在飞书/Lark 文档或文件上添加顶级评论。 | 飞书应用凭证 |
| `feishu_drive_list_comments` | 列出飞书/Lark 文件上的整篇文档评论，最近优先。 | 飞书应用凭证 |
| `feishu_drive_list_comment_replies` | 列出特定飞书/Lark 评论线程（整篇文档或局部选区）中的回复。 | 飞书应用凭证 |
| `feishu_drive_reply_comment` | 在飞书/Lark 评论线程中发布回复，可附带 `@` 提及。 | 飞书应用凭证 |

<a id="file-toolset"></a>
## `file` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `patch` | 在文件中进行精确的查找替换编辑。建议在终端中替代 sed/awk 使用。它采用模糊匹配（9 种策略），因此微小的空白/缩进差异不会破坏匹配。返回统一差异格式（unified diff）。编辑后自动运行语法检查…… | — |
| `read_file` | 读取文本文件，显示行号并分页。建议在终端中替代 cat/head/tail 使用。输出格式：`LINE_NUM\|CONTENT`。如果未找到文件，会提示相似文件名。对大文件可以使用偏移量和限制。注意：无法读取图像…… | — |
| `search_files` | 搜索文件内容或按文件名查找文件。建议在终端中替代 grep/rg/find/ls 使用。基于 Ripgrep，速度比 shell 等价工具更快。内容搜索（target='content'）：对文件进行正则搜索。输出模式：完整匹配并显示行号…… | — |
| `write_file` | 将内容写入文件，完全替换已有内容。建议在终端中替代 echo/cat heredoc 使用。自动创建父目录。会**覆盖**整个文件——如需精确编辑请使用 'patch'。 | — |

<a id="homeassistant-toolset"></a>
## `homeassistant` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `ha_call_service` | 调用 Home Assistant 服务来控制设备。使用 `ha_list_services` 来发现每个域可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个 Home Assistant 实体的详细状态，包括所有属性（亮度、颜色、温度设定点、传感器读数等）。 | — |
| `ha_list_entities` | 列出 Home Assistant 实体。可按域（light、switch、climate、sensor、binary_sensor、cover、fan 等）或按区域名称（living room、kitchen、bedroom 等）过滤。 | — |
| `ha_list_services` | 列出可用于设备控制的 Home Assistant 服务（动作）。显示每种设备类型可执行的操作及其接受的参数。使用此工具来发现如何控制通过 `ha_list_entities` 找到的设备。 | — |

<a id="computeruse-toolset"></a>
## `computer_use` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `computer_use` | 通过 cua-driver 在后台进行 macOS 桌面控制——截图（SOM / 视觉 / AX）、点击、拖拽、滚动、输入、按键、等待、列出应用、聚焦应用。**不会**夺取用户的光标或键盘焦点。支持任何具备工具调用能力的模型。仅限 macOS。 | `cua-driver` 位于 `$PATH`（通过 `hermes tools` 安装）。 |
:::note
**Honcho 工具**（`honcho_profile`、`honcho_search`、`honcho_context`、`honcho_reasoning`、`honcho_conclude`）不再是内置工具。它们可通过 Honcho 记忆提供者插件在 `plugins/memory/honcho/` 路径下获取。安装和使用方法请参见[记忆提供者](../user-guide/features/memory-providers.md)。
:::

<a id="imagegen-toolset"></a>
## `image_gen` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `image_generate` | 使用 FAL.ai 根据文本提示生成高质量图片。底层模型由用户配置（默认：FLUX 2 Klein 9B，生成时间低于1秒），Agent 无法选择。返回单个图片 URL。可通过……显示。 | FAL_KEY |

<a id="kanban-toolset"></a>
## `kanban` 工具集

当 Agent 满足以下任一条件时注册该工具集：(a) 由看板调度器生成（设置了 `HERMES_KANBAN_TASK` 环境变量），或 (b) 在显式启用 `kanban` 工具集的配置文件中运行。任务级工作线程使用生命周期工具处理其分配的任务；编排器配置文件额外获得看板路由工具，如 `kanban_list` 和 `kanban_unblock`。完整工作流程请参见[看板多 Agent](/user-guide/features/kanban)。

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `kanban_show` | 显示分配给该工作线程的当前看板任务（标题、描述、评论、依赖项）。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_list` | 使用筛选条件列出看板任务。仅编排器可用；对调度器生成的任务工作线程隐藏。 | 启用了 `kanban` 工具集的配置文件 |
| `kanban_complete` | 使用结构化的交接负载（结果、工件、后续事项）将当前任务标记为完成。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_block` | 因用户问题阻塞当前任务——调度器暂停，展示问题，待人类回复后继续。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_heartbeat` | 在长时间运行的操作期间发送进度心跳，以便调度器知道工作线程仍在运行。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_comment` | 向任务线程添加评论而不改变其状态——适用于展示中间发现。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_create` | 从当前任务派生出子任务。由编排器和生成后续任务的工作线程使用。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_link` | 使用父→子依赖关系链接任务。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_unblock` | 将阻塞的任务恢复为 `ready` 状态。仅编排器可用；对调度器生成的任务工作线程隐藏。 | 启用了 `kanban` 工具集的配置文件 |

<a id="memory-toolset"></a>
## `memory` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `memory` | 将重要信息保存到跨会话持久化的记忆中。你的记忆会在会话开始时出现在系统提示中——这就是你如何在对话之间记住用户和环境信息的方式。何时保存…… | — |
<a id="messaging-toolset"></a>
## `messaging` 工具集

| 工具 | 描述 | 需要环境 |
|------|-------------|----------------------|
| `send_message` | 向已连接的消息平台发送消息，或列出可用目标。重要提示：当用户要求发送到特定频道或个人（不仅仅是平台名称）时，请先调用 send_message(action='list') 查看可用的目标… | — |

<a id="moa-toolset"></a>
## `moa` 工具集

| 工具 | 描述 | 需要环境 |
|------|-------------|----------------------|
| `mixture_of_agents` | 通过多个前沿LLM协作路由难题。进行5次API调用（4个参考模型+1个聚合器），使用最大推理能力——仅在真正困难的问题上谨慎使用。最适用于：复杂数学、高级算法… | OPENROUTER_API_KEY |

<a id="sessionsearch-toolset"></a>
## `session_search` 工具集

| 工具 | 描述 | 需要环境 |
|------|-------------|----------------------|
| `session_search` | 搜索存储在本地会话数据库中的历史会话，或在一个会话中滚动。基于FTS5的检索；返回数据库中的实际消息（无LLM调用）。三种形式：发现（传递`query`）、滚动（传递`session_id` + `around_message_id`）、浏览（无参数）。 | — |

<a id="skills-toolset"></a>
## `skills` 工具集

| 工具 | 描述 | 需要环境 |
|------|-------------|----------------------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能是你的程序性记忆——针对重复任务类型的可重用方法。新技能存放在 ~/.hermes/skills/；现有技能可以在其所在位置修改。操作：创建（完整的 SKILL.m…） | — |
| `skill_view` | 技能允许加载特定任务和工作流的信息，以及脚本和模板。加载技能的完整内容或访问其关联文件（引用、模板、脚本）。首次调用返回 SKILL.md 内容以及一个… | — |
| `skills_list` | 列出可用技能（名称+描述）。使用 skill_view(name) 加载完整内容。 | — |

<a id="terminal-toolset"></a>
## `terminal` 工具集

| 工具 | 描述 | 需要环境 |
|------|-------------|----------------------|
| `process` | 管理通过 terminal(background=true) 启动的后台进程。操作：'list'（列出所有）、'poll'（检查状态+新输出）、'log'（完整输出带分页）、'wait'（阻塞直到完成或超时）、'kill'（终止）、'write'（发送…） | — |
| `terminal` | 在 Linux 环境中执行 shell 命令。文件系统在调用之间持久化。对于长时间运行的服务器，设置 `background=true`。设置 `notify_on_complete=true`（与 `background=true` 一起）可以在进程完成时自动获得通知——无需轮询。不要使用 cat/head/tail —— 请使用 read_file。不要使用 grep/rg/find —— 请使用 search_files。 | — |

<a id="todo-toolset"></a>
## `todo` 工具集

| 工具 | 描述 | 需要环境 |
|------|-------------|----------------------|
| `todo` | 管理当前会话的任务列表。用于包含3个以上步骤的复杂任务，或当用户提供多个任务时。无参数调用可读取当前列表。写入：- 提供 'todos' 数组以创建/更新项目 - merge=… | — |
<a id="vision-toolset"></a>
## `vision` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `vision_analyze` | 利用 AI 视觉分析图像。在支持视觉的主流模型上，会以多模态工具结果的形式返回原始图像像素，让模型在下一轮直接原生看到它们。在纯文本模型上，则回退到辅助视觉模型，由该模型描述图像并将描述以文本形式返回。无论哪种情况，工具签名都完全相同。 | — |

<a id="video-toolset"></a>
## `video` 工具集

选择性加入的工具集（默认 `hermes-cli` 集中不加载）。通过 `--toolsets video` 添加，或在 `toolsets:` 配置中包含 `video`。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `video_analyze` | 分析来自 URL 或文件路径的视频内容——包括字幕、场景分解、关键时间戳和视觉描述。 | — |

<a id="videogen-toolset"></a>
## `video_gen` 工具集

选择性加入的工具集（默认 `hermes-cli` 集中不加载）。通过 `--toolsets video_gen` 添加，或在 `hermes tools` → Video Generation 中启用，该选项还会引导您选择后端。

后端以插件形式放置在 `plugins/video_gen/&lt;name&gt;/` 目录下：

- **xAI Grok-Imagine** — 文本到视频和图像到视频（SuperGrok OAuth 或 `XAI_API_KEY`）。
- **FAL.ai** — Veo 3.1、Pixverse v6、Kling O3（需要 `FAL_KEY`）。

单个 `video_generate` 工具涵盖两种模式——传入 `image_url` 可对静态图像进行动画化，省略该参数则仅从文本生成。活动后端会自动路由到正确的端点。该工具的描述会在会话启动时重建，以反映活动后端的实际能力（模式、宽高比、分辨率、时长范围、最大参考图像数、音频支持）。后端编写请参阅 [视频生成提供者插件](/developer-guide/video-gen-provider-plugin)。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `video_generate` | 根据文本提示生成视频（文本到视频），或对静态图像进行动画化（图像到视频），使用用户配置的视频生成后端。传入 `image_url` 可对该图像进行动画化；省略该参数则仅从文本生成。后端会自动路由到正确的端点。在 `video` 字段中返回 HTTP URL 或绝对文件路径。 | 活动的 `video_gen` 插件及其凭证（例如 `XAI_API_KEY`、`FAL_KEY`） |

<a id="web-toolset"></a>
## `web` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `web_search` | 搜索互联网以获取信息。默认返回最多 5 条结果，包含标题、URL 和描述。可接受可选的 `limit` 参数（1-100，默认 5）。查询会传递给配置的后端，因此后端支持时，诸如 `site:域名`、`filetype:pdf`、`intitle:关键词`、`-术语` 和 `"精确短语"` 等操作符可能有效。 | `EXA_API_KEY` 或 `PARALLEL_API_KEY` 或 `FIRECRAWL_API_KEY` 或 `TAVILY_API_KEY` |
| `web_extract` | 从网页 URL 提取内容。以 Markdown 格式返回页面内容。也支持 PDF URL——直接传入 PDF 链接即可转换为 Markdown 文本。小于 5000 字符的页面返回完整 Markdown；较大的页面会由 LLM 进行摘要。 | `EXA_API_KEY` 或 `PARALLEL_API_KEY` 或 `FIRECRAWL_API_KEY` 或 `TAVILY_API_KEY` |
<a id="xsearch-toolset"></a>
## `x_search` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `x_search` | 使用 xAI 内置的 `x_search` 响应工具搜索 X（Twitter）上的帖子、个人资料和话题串。适合查找 X 上的当前讨论、反应或言论，而非通用网页。默认关闭——通过 `hermes tools` → 🐦 X（Twitter）搜索 选入启用。仅当配置了 xAI 凭证时才会注册 Schema（通过 check_fn 门控）。 | XAI_API_KEY **或** xAI Grok OAuth（SuperGrok 订阅）登录 |

<a id="tts-toolset"></a>
## `tts` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `text_to_speech` | 将文本转换为语音音频。返回一个 MEDIA: 路径，平台会将其作为语音消息发送。在 Telegram 上以语音气泡形式播放，在 Discord/WhatsApp 上作为音频附件播放。在 CLI 模式下，保存到 ~/voice-memos/。语音和提供方… | — |

<a id="discord-toolset"></a>
## `discord` 工具集

注册在 `hermes-discord` 平台工具集上（仅网关）。使用与消息适配器相同的机器人令牌。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord` | 读取并参与 Discord 服务器。操作包括 `search_members`、`fetch_messages`、`send_message`、`react`、`fetch_channel`、`list_channels` 等。 | `DISCORD_BOT_TOKEN` |

<a id="discordadmin-toolset"></a>
## `discord_admin` 工具集

注册在 `hermes-discord` 平台工具集上。审核操作需要机器人持有相应的 Discord 权限。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord_admin` | 通过 REST API 管理 Discord 服务器：列出 guilds/channels/roles，创建/编辑/删除频道，管理角色授权、超时、踢出和封禁。 | `DISCORD_BOT_TOKEN` + 机器人权限 |

<a id="spotify-toolset"></a>
## `spotify` 工具集

由捆绑的 `spotify` 插件注册。需要 OAuth 令牌——运行 `hermes spotify setup` 一次进行授权。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `spotify_playback` | 控制 Spotify 播放，检查当前播放状态，或获取最近播放的曲目。 | Spotify OAuth |
| `spotify_devices` | 列出 Spotify Connect 设备或将播放转移到其他设备。 | Spotify OAuth |
| `spotify_queue` | 查看用户的 Spotify 队列或向其中添加项目。 | Spotify OAuth |
| `spotify_search` | 在 Spotify 目录中搜索曲目、专辑、艺术家、播放列表、节目或单集。 | Spotify OAuth |
| `spotify_playlists` | 列出、查看、创建、更新和修改 Spotify 播放列表。 | Spotify OAuth |
| `spotify_albums` | 获取 Spotify 专辑元数据或专辑曲目。 | Spotify OAuth |
| `spotify_library` | 列出、保存或删除用户已保存的 Spotify 曲目或专辑。 | Spotify OAuth |

<a id="hermes-yuanbao-toolset"></a>
## `hermes-yuanbao` 工具集

仅注册在 `hermes-yuanbao` 平台工具集上。Yuanbao（元宝）是腾讯的聊天应用；这些工具驱动其私信/群组/贴纸 API。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `yb_query_group_info` | 查询群组（在应用中称为“派/Pai”）的基本信息：名称、群主、成员数。 | Yuanbao 凭证 |
| `yb_query_group_members` | 查询群组成员（用于 `@` 提及、按名称查找用户、列出机器人）。 | Yuanbao 凭证 |
| `yb_send_dm` | 向群组中的用户发送私信/直接消息，可选附带媒体文件。 | Yuanbao 凭证 |
| `yb_search_sticker` | 按关键词搜索内置的 Yuanbao 贴纸（TIM 表情）目录。 | Yuanbao 凭证 |
| `yb_send_sticker` | 向当前 Yuanbao 聊天发送内置贴纸。 | Yuanbao 凭证 |
--- BEGIN DOCUMENT CHUNK ---

--- END DOCUMENT CHUNK ---
