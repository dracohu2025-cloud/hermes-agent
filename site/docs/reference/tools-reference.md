---
sidebar_position: 3
title: "内置工具参考"
description: "Hermes 内置工具的权威参考，按工具集分组"
---

# 内置工具参考 {#built-in-tools-reference}

本页面记录了 Hermes 工具注册表中所有 68 个内置工具，按工具集分组。可用性因平台、凭据和已启用的工具集而异。

**快速统计：** 10 个浏览器工具（核心）+ 2 个 browser-cdp 工具、4 个文件工具、10 个 RL 工具、4 个 Home Assistant 工具、2 个终端工具、2 个 Web 工具、5 个飞书工具、7 个 Spotify 工具、5 个元宝工具、2 个 Discord 工具，以及跨其他工具集的 15 个独立工具。

:::tip MCP 工具
<a id="mcp-tools"></a>
除了内置工具，Hermes 还可以从 MCP 服务器动态加载工具。MCP 工具会带有服务器名称前缀（例如，`github` MCP 服务器的工具显示为 `github_create_issue`）。配置请参见 [MCP 集成](/user-guide/features/mcp)。
:::

## `browser` 工具集 {#browser-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `browser_back` | 导航回浏览器历史记录中的上一页。需要先调用 browser_navigate。 | — |
| `browser_click` | 点击由快照中 ref ID 标识的元素（例如 '@e5'）。ref ID 在快照输出中以方括号显示。需要先调用 browser_navigate 和 browser_snapshot。 | — |
| `browser_console` | 获取当前页面的浏览器控制台输出和 JavaScript 错误。返回 console.log/warn/error/info 消息和未捕获的 JS 异常。用于检测静默的 JavaScript 错误、失败的 API 调用和应用程序警告。需要先调用 browser_navigate。 | — |
| `browser_get_images` | 获取当前页面上所有图片的列表，包含其 URL 和替代文本。用于查找需要借助视觉工具分析的图片。需要先调用 browser_navigate。 | — |
| `browser_navigate` | 在浏览器中导航到某个 URL。初始化会话并加载页面。必须在使用其他浏览器工具之前调用。对于简单的信息检索，建议优先使用 web_search 或 web_extract（更快、更便宜）。当需要交互式操作或处理复杂页面时，再使用浏览器工具。 | — |
| `browser_press` | 按下键盘按键。适用于提交表单（Enter）、导航（Tab）或键盘快捷键。需要先调用 browser_navigate。 | — |
| `browser_scroll` | 按方向滚动页面。用于显示当前视口下方或上方可能隐藏的更多内容。需要先调用 browser_navigate。 | — |
| `browser_snapshot` | 获取当前页面无障碍树的文本快照。返回带有 ref ID（如 @e1、@e2）的交互元素，供 browser_click 和 browser_type 使用。full=false（默认）：紧凑视图，仅显示交互元素。full=true：完整视图，包含更多细节。 | — |
| `browser_type` | 在由 ref ID 标识的输入字段中键入文本。会先清空字段，然后输入新文本。需要先调用 browser_navigate 和 browser_snapshot。 | — |
| `browser_vision` | 截取当前页面的屏幕截图，并使用视觉 AI 进行分析。当你需要直观理解页面内容时使用——特别适用于验证码、视觉验证挑战、复杂布局，或当文本快照无法提供足够信息时。 | — |
## `browser-cdp` 工具集 {#browser-cdp-toolset}

仅在会话启动时可通过 Chrome DevTools Protocol 端点访问时注册——通过 `/browser connect`、`browser.cdp_url` 配置、Browserbase 会话或 Camofox。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `browser_cdp` | 发送原始 Chrome DevTools Protocol 命令。用于执行高级 `browser_*` 工具未覆盖的浏览器操作的逃生口。参见 https://chromedevtools.github.io/devtools-protocol/ | CDP 端点 |
| `browser_dialog` | 响应原生 JavaScript 对话框（alert / confirm / prompt / beforeunload）。先调用 `browser_snapshot` — 待处理的对话框会出现在其 `pending_dialogs` 字段中。然后调用 `browser_dialog(action='accept'\|'dismiss')`。 | CDP 端点 |

## `clarify` 工具集 {#clarify-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `clarify` | 当你在继续之前需要澄清、反馈或决策时，向用户提问。支持两种模式：1. **多项选择** — 最多提供 4 个选项。用户选择一个，或通过第 5 个“其他”选项输入自己的答案。2.… | — |

## `code_execution` 工具集 {#codeexecution-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `execute_code` | 运行一个可以编程调用 Hermes 工具的 Python 脚本。当你需要 3 次以上工具调用且之间包含处理逻辑、需要在工具输出进入上下文之前过滤/缩减大量输出、需要条件分支（… | — |

## `cronjob` 工具集 {#cronjob-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `cronjob` | 统一的任务调度管理器。使用 `action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"` 或 `"remove"` 来管理任务。支持绑定一个或多个技能的任务，更新时传入 `skills=[]` 会清除已绑定的技能。Cron 任务在全新的会话中执行，不携带当前聊天上下文。 | — |

## `delegation` 工具集 {#delegation-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `delegate_task` | 生成一个或多个子 Agent，在隔离的上下文中处理任务。每个子 Agent 拥有自己的对话、终端会话和工具集。只返回最终摘要——中间工具结果不会进入你的上下文窗口。两种… | — |

## `feishu_doc` 工具集 {#feishudoc-toolset}

仅用于飞书文档评论智能回复处理器（`gateway/platforms/feishu_comment.py`）。不在 `hermes-cli` 或常规飞书聊天适配器上暴露。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `feishu_doc_read` | 根据给定的 file_type 和 token，读取飞书/Lark 文档（Docx、Doc 或 Sheet）的全文内容。 | 飞书应用凭证 |

## `feishu_drive` 工具集 {#feishudrive-toolset}

仅用于飞书文档评论处理器。驱动对云盘文件的评论读写操作。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `feishu_drive_add_comment` | 在飞书/Lark 文档或文件上添加顶级评论。 | 飞书应用凭证 |
| `feishu_drive_list_comments` | 列出飞书/Lark 文件上的整篇文档评论，按最新时间排序。 | 飞书应用凭证 |
| `feishu_drive_list_comment_replies` | 列出特定飞书评论线程（整篇文档或局部选择）的回复。 | 飞书应用凭证 |
| `feishu_drive_reply_comment` | 在飞书评论线程上发布回复，可选的 `@` 提及。 | 飞书应用凭证 |
## `file` 工具集 {#file-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `patch` | 对文件进行精准的查找替换编辑。请用此工具替代终端中的 sed/awk。采用模糊匹配（9 种策略），因此细微的空格/缩进差异不会影响使用。返回统一差异格式（unified diff）。编辑后自动运行语法检查… | — |
| `read_file` | 读取带行号和分页功能的文本文件。请用此工具替代终端中的 cat/head/tail。输出格式：'LINE_NUM\|CONTENT'。如果未找到文件，会建议相似文件名。对于大文件可使用 offset 和 limit 参数。注意：无法读取图像… | — |
| `search_files` | 搜索文件内容或按名称查找文件。请用此工具替代终端中的 grep/rg/find/ls。基于 Ripgrep，比 shell 中的同类工具更快。内容搜索（target='content'）：在文件中进行正则表达式搜索。输出模式：完整匹配并显示行… | — |
| `write_file` | 将内容写入文件，完全替换现有内容。请用此工具替代终端中的 echo/cat heredoc。自动创建父目录。会**覆盖**整个文件——如需精准编辑请使用 'patch'。 | — |

## `homeassistant` 工具集 {#homeassistant-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `ha_call_service` | 调用 Home Assistant 服务来控制设备。使用 ha_list_services 来发现每个域可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个 Home Assistant 实体的详细状态，包括所有属性（亮度、颜色、温度设定点、传感器读数等）。 | — |
| `ha_list_entities` | 列出 Home Assistant 实体。可按域（light、switch、climate、sensor、binary_sensor、cover、fan 等）或按区域名称（living room、kitchen、bedroom 等）进行过滤。 | — |
| `ha_list_services` | 列出可用于设备控制的 Home Assistant 服务（操作）。显示每种设备类型可执行的操作及其接受的参数。使用此工具来发现如何控制通过 ha_list_entities 找到的设备。 | — |

:::note
**Honcho 工具**（`honcho_profile`、`honcho_search`、`honcho_context`、`honcho_reasoning`、`honcho_conclude`）不再是内置工具。它们可通过 Honcho 记忆提供者插件在 `plugins/memory/honcho/` 路径下获取。安装和使用方法请参见[记忆提供者](../user-guide/features/memory-providers.md)。
:::

## `image_gen` 工具集 {#imagegen-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `image_generate` | 使用 FAL.ai 根据文本提示生成高质量图像。底层模型由用户配置（默认：FLUX 2 Klein 9B，生成时间低于 1 秒），Agent 无法选择。返回单个图像 URL。可使用…显示 | FAL_KEY |

## `memory` 工具集 {#memory-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `memory` | 将重要信息保存到跨会话持久化的记忆中。你的记忆会在会话开始时出现在系统提示中——这是你在不同对话之间记住用户和环境信息的方式。何时保存… | — |
## `messaging` 工具集 {#messaging-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `send_message` | 向已连接的消息平台发送消息，或列出可用的目标。重要提示：当用户要求发送给特定频道或个人（不仅仅是平台名称）时，请先调用 send_message(action='list') 查看可用的目标…… | — |

## `moa` 工具集 {#moa-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `mixture_of_agents` | 通过多个前沿大语言模型协作处理难题。会发起 5 次 API 调用（4 个参考模型 + 1 个聚合器），并采用最大推理力度——请谨慎用于真正困难的问题。最适合：复杂数学、高级算法…… | OPENROUTER_API_KEY |

## `rl` 工具集 {#rl-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `rl_check_status` | 获取训练运行的状态和指标。有速率限制：同一运行两次检查之间至少间隔 30 分钟。返回 WandB 指标：step、state、reward_mean、loss、percent_correct。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_edit_config` | 更新配置字段。请先使用 rl_get_current_config() 查看所选环境的所有可用字段。每个环境都有不同的可配置选项。基础设施设置（tokenizer、URLs、lora_rank、learning_ra……） | TINKER_API_KEY, WANDB_API_KEY |
| `rl_get_current_config` | 获取当前环境配置。仅返回可修改的字段：group_size、max_token_length、total_steps、steps_per_eval、use_wandb、wandb_name、max_num_workers。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_get_results` | 获取已完成训练运行的最终结果和指标。返回最终指标和训练权重的路径。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_list_environments` | 列出所有可用的 RL 环境。返回环境名称、路径和描述。提示：使用文件工具读取 file_path，了解每个环境的工作原理（验证器、数据加载、奖励）。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_list_runs` | 列出所有训练运行（活跃和已完成）及其状态。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_select_environment` | 选择用于训练的 RL 环境。加载环境的默认配置。选择后，使用 rl_get_current_config() 查看设置，使用 rl_edit_config() 修改它们。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_start_training` | 使用当前环境和配置启动新的 RL 训练运行。大多数训练参数（lora_rank、learning_rate 等）是固定的。在启动前使用 rl_edit_config() 设置 group_size、batch_size、wandb_project。警告：训练…… | TINKER_API_KEY, WANDB_API_KEY |
| `rl_stop_training` | 停止正在运行的训练任务。如果指标看起来不好、训练停滞不前，或者想尝试不同的设置时使用。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_test_inference` | 对任何环境进行快速推理测试。使用 OpenRouter 运行几步推理 + 评分。默认：3 步 x 16 次补全 = 每个模型 48 次 rollout，测试 3 个模型 = 总共 144 次。测试环境加载、提示构建、推理…… | TINKER_API_KEY, WANDB_API_KEY |
## `session_search` 工具集 {#sessionsearch-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `session_search` | 搜索你过去对话的长期记忆。这是你的回忆——每个过去的会话都可搜索，此工具会总结发生了什么。**主动使用**此工具的场景：用户说“我们之前做过这个”、“还记得吗”、“上次……”等。 | — |

## `skills` 工具集 {#skills-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能是你的程序性记忆——针对重复任务类型的可复用方法。新技能存放在 `~/.hermes/skills/`；已有技能可在其所在位置修改。操作：create（完整 SKILL.m… | — |
| `skill_view` | 技能允许加载特定任务和工作流的信息，以及脚本和模板。加载技能的完整内容或访问其关联文件（参考资料、模板、脚本）。首次调用返回 SKILL.md 内容及… | — |
| `skills_list` | 列出可用技能（名称 + 描述）。使用 `skill_view(name)` 加载完整内容。 | — |

## `terminal` 工具集 {#terminal-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `process` | 管理通过 `terminal(background=true)` 启动的后台进程。操作：'list'（列出所有）、'poll'（检查状态 + 新输出）、'log'（完整输出，支持分页）、'wait'（阻塞直到完成或超时）、'kill'（终止）、'write'（发送… | — |
| `terminal` | 在 Linux 环境中执行 shell 命令。文件系统在多次调用间持久化。对于长时间运行的服务器，设置 `background=true`。设置 `notify_on_complete=true`（配合 `background=true`）可在进程完成时自动收到通知——无需轮询。**不要**使用 cat/head/tail——请使用 read_file。**不要**使用 grep/rg/find——请使用 search_files。 | — |

## `todo` 工具集 {#todo-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `todo` | 管理当前会话的任务列表。用于包含 3 个以上步骤的复杂任务，或用户提供多个任务时。无参数调用可读取当前列表。写入：- 提供 'todos' 数组来创建/更新项目 - merge=… | — |

## `vision` 工具集 {#vision-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `vision_analyze` | 使用 AI 视觉分析图像。提供全面的描述，并回答关于图像内容的特定问题。 | — |

## `web` 工具集 {#web-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `web_search` | 搜索网络信息。默认返回最多 5 条结果，包含标题、URL 和描述。接受可选参数 `limit`（1-100，默认 5）。查询会传递给配置的后端，因此当后端支持时，诸如 `site:domain`、`filetype:pdf`、`intitle:word`、`-term` 和 `"exact phrase"` 等操作符可能有效。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |
| `web_extract` | 从网页 URL 提取内容。以 Markdown 格式返回页面内容。也支持 PDF URL——直接传入 PDF 链接，它会转换为 Markdown 文本。小于 5000 字符的页面返回完整 Markdown；更大的页面由 LLM 总结。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |
## `tts` 工具集 {#tts-toolset}

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `text_to_speech` | 将文本转换为语音音频。返回一个 `MEDIA:` 路径，平台会将其作为语音消息投递。在 Telegram 上以语音气泡播放，在 Discord/WhatsApp 上作为音频附件播放。在 CLI 模式下，保存到 `~/voice-memos/`。语音和提供商… | — |

## `discord` 工具集 {#discord-toolset}

注册在 `hermes-discord` 平台工具集上（仅限网关）。使用与消息适配器相同的机器人令牌。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord` | 读取并参与 Discord 服务器。操作包括 `search_members`、`fetch_messages`、`send_message`、`react`、`fetch_channel`、`list_channels` 等。 | `DISCORD_BOT_TOKEN` |

## `discord_admin` 工具集 {#discordadmin-toolset}

注册在 `hermes-discord` 平台工具集上。审核操作要求机器人拥有匹配的 Discord 权限。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord_admin` | 通过 REST API 管理 Discord 服务器：列出服务器/频道/角色、创建/编辑/删除频道、管理角色授权、超时、踢出和封禁。 | `DISCORD_BOT_TOKEN` + 机器人权限 |

## `spotify` 工具集 {#spotify-toolset}

由捆绑的 `spotify` 插件注册。需要 OAuth 令牌——运行 `hermes spotify setup` 一次以授权。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `spotify_playback` | 控制 Spotify 播放、检查当前播放状态或获取最近播放的曲目。 | Spotify OAuth |
| `spotify_devices` | 列出 Spotify Connect 设备或将播放转移到其他设备。 | Spotify OAuth |
| `spotify_queue` | 检查用户的 Spotify 队列或向其中添加项目。 | Spotify OAuth |
| `spotify_search` | 搜索 Spotify 目录中的曲目、专辑、艺术家、播放列表、节目或单集。 | Spotify OAuth |
| `spotify_playlists` | 列出、查看、创建、更新和修改 Spotify 播放列表。 | Spotify OAuth |
| `spotify_albums` | 获取 Spotify 专辑元数据或专辑曲目。 | Spotify OAuth |
| `spotify_library` | 列出、保存或删除用户已保存的 Spotify 曲目或专辑。 | Spotify OAuth |

## `hermes-yuanbao` 工具集 {#hermes-yuanbao-toolset}

仅注册在 `hermes-yuanbao` 平台工具集上。Yuanbao 是腾讯的聊天应用；这些工具驱动其私信/群组/贴纸 API。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `yb_query_group_info` | 查询群组（应用中称为“派/Pai”）的基本信息：名称、群主、成员数量。 | Yuanbao 凭据 |
| `yb_query_group_members` | 查询群组成员（用于 `@` 提及、按名称查找用户、列出机器人）。 | Yuanbao 凭据 |
| `yb_send_dm` | 向群组中的用户发送私信/直接消息，可附带媒体文件。 | Yuanbao 凭据 |
| `yb_search_sticker` | 按关键词搜索内置的 Yuanbao 贴纸（TIM 表情）目录。 | Yuanbao 凭据 |
| `yb_send_sticker` | 向当前 Yuanbao 聊天发送内置贴纸。 | Yuanbao 凭据 |

