---
sidebar_position: 3
title: "内置工具参考"
description: "Hermes 内置工具的权威参考，按工具集分组"
---

# 内置工具参考 {#built-in-tools-reference}

本页记录了 Hermes 工具注册表中的全部 53 个内置工具，按工具集分组。具体可用性取决于平台、凭据和已启用的工具集。

**快速统计：** 11 个浏览器工具、4 个文件工具、10 个 RL 工具、4 个 Home Assistant 工具、2 个终端工具、2 个 Web 工具、5 个飞书工具，以及分布在其他工具集中的 15 个独立工具。

:::tip MCP 工具
除了内置工具，Hermes 还可以从 MCP 服务器动态加载工具。MCP 工具会带有服务器名称前缀（例如 `github` MCP 服务器的 `github_create_issue`）。配置方式请参阅 [MCP 集成](/user-guide/features/mcp)。
:::
<a id="mcp-tools"></a>

## `browser` 工具集 {#browser-toolset}

| 工具 | 描述 | 需要环境 |
|------|------|----------|
| `browser_back` | 返回浏览器历史中的上一页。需要先调用 browser_navigate。 | — |
| `browser_cdp` | 发送原始 Chrome DevTools Protocol (CDP) 命令。用于 browser_navigate、browser_click、browser_console 等未覆盖的浏览器操作的逃生舱。仅在会话启动时可访问 CDP 端点的情况下可用——通过 `/browser connect` 或 `browser.cdp_url` 配置。参见 https://chromedevtools.github.io/devtools-protocol/ | — |
| `browser_click` | 点击由快照中的 ref ID 标识的元素（例如 '@e5'）。ref ID 在快照输出中以方括号显示。需要先调用 browser_navigate 和 browser_snapshot。 | — |
| `browser_console` | 获取当前页面的浏览器控制台输出和 JavaScript 错误。返回 console.log/warn/error/info 消息和未捕获的 JS 异常。用于检测静默 JavaScript 错误、失败的 API 调用和应用警告。需… | — |
| `browser_get_images` | 获取当前页面上所有图片的列表，包括 URL 和 alt 文本。用于查找要通过 vision 工具分析的图片。需要先调用 browser_navigate。 | — |
| `browser_navigate` | 在浏览器中导航到指定 URL。初始化会话并加载页面。必须在其他浏览器工具之前调用。对于简单的信息检索，优先使用 web_search 或 web_extract（更快、更便宜）。仅在需要…时使用浏览器工具 | — |
| `browser_press` | 按下键盘按键。用于提交表单（Enter）、导航（Tab）或键盘快捷键。需要先调用 browser_navigate。 | — |
| `browser_scroll` | 向指定方向滚动页面。用于显示当前视口上方或下方的更多内容。需要先调用 browser_navigate。 | — |
| `browser_snapshot` | 获取当前页面可访问性树的文本快照。返回带有 ref ID（如 @e1、@e2）的交互元素，供 browser_click 和 browser_type 使用。full=false（默认）：紧凑视图，仅含交互元素。full=true：完整… | — |
| `browser_type` | 向由 ref ID 标识的输入框输入文本。先清空字段，再输入新文本。需要先调用 browser_navigate 和 browser_snapshot。 | — |
| `browser_vision` | 截取当前页面屏幕截图，并用视觉 AI 进行分析。当你需要直观理解页面内容时使用——特别适用于验证码、视觉验证挑战、复杂布局，或文本快照…时 | — |

## `clarify` 工具集 {#clarify-toolset}

| 工具 | 描述 | 需要环境 |
|------|------|----------|
| `clarify` | 当你需要澄清、反馈或决策后再继续时，向用户提问。支持两种模式：1. **多选**——提供最多 4 个选项，用户选择一个或通过第 5 个"其他"选项输入自己的答案。2.… | — |

## `code_execution` 工具集 {#codeexecution-toolset}

| 工具 | 描述 | 需要环境 |
|------|------|----------|
| `execute_code` | 运行可以编程方式调用 Hermes 工具的 Python 脚本。当你需要 3 个以上带中间处理逻辑的工具调用、需要在输出进入上下文前过滤/缩减大量工具输出、需要条件分支（…时使用 | — |
## `cronjob` 工具集 {#cronjob-toolset}

| 工具 | 说明 | 需要环境 |
|------|------|----------|
| `cronjob` | 统一的定时任务管理器。使用 `action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"` 或 `"remove"` 来管理任务。支持绑定一个或多个技能的技能驱动任务，更新时 `skills=[]` 会清除已绑定的技能。Cron 执行会在全新的会话中进行，不带当前聊天上下文。 | — |

## `delegation` 工具集 {#delegation-toolset}

| 工具 | 说明 | 需要环境 |
|------|------|----------|
| `delegate_task` | 生成一个或多个 sub-agent，在隔离上下文中处理任务。每个 sub-agent 拥有独立的对话、终端会话和工具集。只返回最终摘要 —— 中间工具结果不会进入你的上下文窗口。TWO… | — |

## `feishu_doc` 工具集 {#feishudoc-toolset}

仅用于飞书文档评论智能回复处理器（`gateway/platforms/feishu_comment.py`）。不在 `hermes-cli` 或常规飞书聊天适配器上暴露。

| 工具 | 说明 | 需要环境 |
|------|------|----------|
| `feishu_doc_read` | 根据 file_type 和 token 读取飞书/Lark 文档（Docx、Doc 或 Sheet）的完整文本内容。 | 飞书应用凭证 |

## `feishu_drive` 工具集 {#feishudrive-toolset}

仅用于飞书文档评论处理器。对云盘文件执行评论读写操作。

| 工具 | 说明 | 需要环境 |
|------|------|----------|
| `feishu_drive_add_comment` | 在飞书/Lark 文档或文件上添加顶层评论。 | 飞书应用凭证 |
| `feishu_drive_list_comments` | 列出飞书/Lark 文件的全文档评论，按时间倒序。 | 飞书应用凭证 |
| `feishu_drive_list_comment_replies` | 列出指定飞书评论串的回复（全文档或局部选中）。 | 飞书应用凭证 |
| `feishu_drive_reply_comment` | 在飞书评论串中发表回复，可选 `@` 提及。 | 飞书应用凭证 |

## `file` 工具集 {#file-toolset}

| 工具 | 说明 | 需要环境 |
|------|------|----------|
| `patch` | 对文件进行定向查找替换编辑。在终端中请用它代替 sed/awk。采用模糊匹配（9 种策略），因此轻微的空白/缩进差异不会导致失败。返回统一 diff。编辑后自动运行语法检查… | — |
| `read_file` | 带行号和分页地读取文本文件。在终端中请用它代替 cat/head/tail。输出格式：'LINE_NUM\|CONTENT'。找不到文件时会推荐相似文件名。大文件请使用 offset 和 limit。注意：无法读取图片 o… | — |
| `search_files` | 搜索文件内容或按名称查找文件。在终端中请用它代替 grep/rg/find/ls。底层使用 Ripgrep，比 shell 等效命令更快。内容搜索（target='content'）：在文件内部进行正则搜索。输出模式：完整匹配含行… | — |
| `write_file` | 将内容写入文件，完全替换已有内容。在终端中请用它代替 echo/cat heredoc。自动创建父目录。**会覆盖整个文件** —— 定向编辑请用 'patch'。 | — |

## `homeassistant` 工具集 {#homeassistant-toolset}

| 工具 | 说明 | 需要环境 |
|------|------|----------|
| `ha_call_service` | 调用 Home Assistant 服务来控制设备。先用 ha_list_services 发现每个域下可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个 Home Assistant 实体的详细状态，包括所有属性（亮度、颜色、温度设定点、传感器读数等）。 | — |
| `ha_list_entities` | 列出 Home Assistant 实体。可按域（light、switch、climate、sensor、binary_sensor、cover、fan 等）或按区域名称（living room、kitchen、bedroom 等）筛选。 | — |
| `ha_list_services` | 列出 Home Assistant 中可用于设备控制的服务（动作）。显示每种设备类型可执行的动作及其接受的参数。配合 ha_list_entities 发现设备后，用它来了解如何控制这些设备。 | — |
:::note
**Honcho tools** (`honcho_profile`, `honcho_search`, `honcho_context`, `honcho_reasoning`, `honcho_conclude`) 不再是内置功能。它们现在通过 Honcho 记忆提供插件提供，位于 `plugins/memory/honcho/`。安装和使用方法请参见 [Memory Providers](../user-guide/features/memory-providers.md)。
:::

## `image_gen` 工具集 {#imagegen-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|------|--------------|
| `image_generate` | 使用 FAL.ai 根据文本提示生成高质量图片。底层模型由用户配置（默认：FLUX 2 Klein 9B，生成时间低于 1 秒），Agent 无法自行选择。返回单个图片 URL。显示方式请使用… | FAL_KEY |

## `memory` 工具集 {#memory-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|------|--------------|
| `memory` | 将重要信息保存到持久化记忆中，跨会话保留。你的记忆会在会话开始时出现在系统提示里——这就是你在多次对话之间记住用户和环境信息的方式。何时保存… | — |

## `messaging` 工具集 {#messaging-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|------|--------------|
| `send_message` | 向已连接的消息平台发送消息，或列出可用目标。**重要**：当用户要求发送到特定频道或人（不只是平台名称）时，**先**调用 send_message(action='list') 查看可用目标… | — |

## `moa` 工具集 {#moa-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|------|--------------|
| `mixture_of_agents` | 将难题通过多个前沿大语言模型协作处理。会发起 5 次 API 调用（4 个参考模型 + 1 个聚合器），使用最大推理力度——请谨慎使用，仅用于真正困难的问题。最适合：复杂数学、高级算法… | OPENROUTER_API_KEY |

## `rl` 工具集 {#rl-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|------|--------------|
| `rl_check_status` | 获取训练运行的状态和指标。**速率限制**：同一运行两次检查之间至少间隔 30 分钟。返回 WandB 指标：step、state、reward_mean、loss、percent_correct。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_edit_config` | 更新配置字段。使用前请先调用 rl_get_current_config() 查看所选环境的全部可用字段。每个环境有不同的可配置选项。基础设施设置（tokenizer、URLs、lora_rank、learning_ra… | TINKER_API_KEY, WANDB_API_KEY |
| `rl_get_current_config` | 获取当前环境配置。仅返回可修改的字段：group_size、max_token_length、total_steps、steps_per_eval、use_wandb、wandb_name、max_num_workers。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_get_results` | 获取已完成训练运行的最终结果和指标。返回最终指标和训练权重路径。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_list_environments` | 列出所有可用的强化学习环境。返回环境名称、路径和描述。**提示**：用文件工具读取 file_path 来了解每个环境的工作原理（验证器、数据加载、奖励）。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_list_runs` | 列出所有训练运行（活跃和已完成）及其状态。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_select_environment` | 选择用于训练的强化学习环境。加载环境的默认配置。选择后，使用 rl_get_current_config() 查看设置，并用 rl_edit_config() 进行修改。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_start_training` | 使用当前环境和配置开始新的强化学习训练运行。大多数训练参数（lora_rank、learning_rate 等）是固定的。开始前请用 rl_edit_config() 设置 group_size、batch_size、wandb_project。**警告**：训练… | TINKER_API_KEY, WANDB_API_KEY |
| `rl_stop_training` | 停止正在运行的训练任务。当指标看起来不佳、训练停滞，或者你想尝试不同设置时使用。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_test_inference` | 对任意环境进行快速推理测试。使用 OpenRouter 运行少量推理 + 评分步骤。默认：3 步 × 16 次补全 = 每个模型 48 次 rollout，测试 3 个模型 = 总共 144 次。测试环境加载、提示构建、in… | TINKER_API_KEY, WANDB_API_KEY |
## `session_search` 工具集 {#sessionsearch-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `session_search` | 搜索你长期记忆中的过往对话。这就是你的回忆——每一次过去的会话都可以搜索，这个工具会总结当时发生了什么。在以下情况请**主动使用**：用户说"我们之前做过这个"、"还记得吗"、"上次……" | — |

## `skills` 工具集 {#skills-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能是你的程序性记忆——可复用的方法，用于处理重复出现的任务类型。新技能保存在 `~/.hermes/skills/`；已有技能可以在它们所在的位置修改。操作：create（完整 SKILL.m… | — |
| `skill_view` | 技能用于加载特定任务和工作流的信息，以及脚本和模板。加载技能的完整内容或访问其关联文件（参考、模板、脚本）。首次调用返回 SKILL.md 内容以及… | — |
| `skills_list` | 列出可用技能（名称 + 描述）。使用 `skill_view(name)` 加载完整内容。 | — |

## `terminal` 工具集 {#terminal-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `process` | 管理通过 `terminal(background=true)` 启动的后台进程。操作：'list'（显示全部）、'poll'（检查状态 + 新输出）、'log'（完整输出，支持分页）、'wait'（阻塞直到完成或超时）、'kill'（终止）、'write'（发… | — |
| `terminal` | 在 Linux 环境中执行 shell 命令。文件系统在多次调用之间持久化。长时间运行的服务请设置 `background=true`。设置 `notify_on_complete=true`（配合 `background=true`）可在进程结束时自动收到通知——无需轮询。不要 用 cat/head/tail——用 read_file。不要 用 grep/rg/find——用 search_files。 | — |

## `todo` 工具集 {#todo-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `todo` | 管理当前会话的任务列表。用于包含 3 个以上步骤的复杂任务，或用户提供多个任务时。不带参数调用可读取当前列表。写入：- 提供 'todos' 数组来创建/更新项目 - merge=… | — |

## `vision` 工具集 {#vision-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `vision_analyze` | 使用 AI 视觉分析图片。提供全面描述，并回答关于图片内容的具体问题。 | — |

## `web` 工具集 {#web-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `web_search` | 搜索网络上的任何主题信息。返回最多 5 条相关结果，包含标题、URL 和描述。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |
| `web_extract` | 从网页 URL 提取内容。以 markdown 格式返回页面内容。也支持 PDF URL——直接传入 PDF 链接即可转换为 markdown 文本。5000 字符以下的页面返回完整 markdown；更大的页面由 LLM 总结。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |

## `tts` 工具集 {#tts-toolset}

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `text_to_speech` | 将文本转换为语音音频。返回一个 MEDIA: 路径，平台会将其作为语音消息发送。在 Telegram 上播放为语音气泡，在 Discord/WhatsApp 上为音频附件。CLI 模式下保存到 `~/voice-memos/`。语音和提供商… | — |
