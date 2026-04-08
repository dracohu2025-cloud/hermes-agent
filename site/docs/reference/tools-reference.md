---
sidebar_position: 3
title: "内置工具参考"
description: "Hermes 内置工具的权威参考，按工具集分组"
---

# 内置工具参考

本页面记录了 Hermes 工具注册表中的所有 47 个内置工具，并按工具集进行了分组。可用性取决于平台、凭据以及已启用的工具集。

**快速统计：** 10 个浏览器工具、4 个文件工具、10 个 RL 工具、4 个 Home Assistant 工具、2 个终端工具、2 个 Web 工具，以及其他工具集中的 15 个独立工具。

:::tip MCP 工具
除了内置工具外，Hermes 还可以从 MCP 服务器动态加载工具。MCP 工具会带有服务器名称前缀（例如，`github` MCP 服务器的工具显示为 `github_create_issue`）。有关配置请参阅 [MCP 集成](/user-guide/features/mcp)。
:::

## `browser` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `browser_back` | 在浏览器历史记录中后退到上一页。需要先调用 browser_navigate。 | — |
| `browser_click` | 点击快照中通过 ref ID 标识的元素（例如 '@e5'）。ref ID 显示在快照输出的方括号中。需要先调用 browser_navigate 和 browser_snapshot。 | — |
| `browser_console` | 获取当前页面的浏览器控制台输出和 JavaScript 错误。返回 console.log/warn/error/info 消息和未捕获的 JS 异常。用于检测静默的 JavaScript 错误、失败的 API 调用和应用程序警告。需要… | — |
| `browser_get_images` | 获取当前页面上所有图片的列表及其 URL 和 alt 文本。适用于查找要使用 vision 工具分析的图片。需要先调用 browser_navigate。 | — |
| `browser_navigate` | 在浏览器中导航到某个 URL。初始化会话并加载页面。必须在其他浏览器工具之前调用。对于简单的信息检索，优先使用 web_search 或 web_extract（更快、更便宜）。当需要…时使用浏览器工具。 | — |
| `browser_press` | 按下键盘按键。适用于提交表单 (Enter)、导航 (Tab) 或键盘快捷键。需要先调用 browser_navigate。 | — |
| `browser_scroll` | 向某个方向滚动页面。使用此工具可以显示当前视口下方或上方的更多内容。需要先调用 browser_navigate。 | — |
| `browser_snapshot` | 获取当前页面无障碍树（accessibility tree）的文本快照。返回带有 ref ID（如 @e1, @e2）的交互式元素，用于 browser_click 和 browser_type。full=false（默认）：包含交互元素的紧凑视图。full=true：完整… | — |
| `browser_type` | 在通过 ref ID 标识的输入框中输入文本。先清空字段，然后输入新文本。需要先调用 browser_navigate 和 browser_snapshot。 | — |
| `browser_vision` | 对当前页面进行截图并使用 vision AI 进行分析。当你需要从视觉上理解页面内容时使用——特别适用于验证码（CAPTCHA）、视觉验证挑战、复杂布局或当文本快照…时。 | — |

## `clarify` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `clarify` | 在继续操作前，当你需要澄清、反馈或决策时向用户提问。支持两种模式：1. **多选题** —— 提供最多 4 个选项。用户选择一个或通过第 5 个“其他”选项输入自己的答案。2.… | — |

## `code_execution` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `execute_code` | 运行一个可以以编程方式调用 Hermes 工具的 Python 脚本。当你需要在 3 个以上的工具调用之间加入处理逻辑、需要在大型工具输出进入上下文之前对其进行过滤/缩减、需要条件分支（…）时使用。 | — |

## `cronjob` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `cronjob` | 统一的定时任务管理器。使用 `action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"` 或 `"remove"` 来管理任务。支持由 skill 支持的任务，可以附加一个或多个 skill，在更新时使用 `skills=[]` 会清除已附加的 skill。Cron 运行发生在没有当前聊天上下文的新会话中。 | — |

## `delegation` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `delegate_task` | 产生一个或多个 sub-agents 在隔离的上下文中处理任务。每个 sub-agent 都有自己的对话、终端会话和工具集。仅返回最终摘要 —— 中间工具结果永远不会进入你的上下文窗口。两种… | — |

## `file` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `patch` | 对文件进行针对性的查找替换编辑。在终端中用它代替 sed/awk。使用模糊匹配（9 种策略），因此微小的空格/缩进差异不会导致失败。返回 unified diff。编辑后自动运行语法检查… | — |
| `read_file` | 读取带有行号和分页的文本文件。在终端中用它代替 cat/head/tail。输出格式：'LINE_NUM\|CONTENT'。如果未找到文件，会建议类似的文件名。对于大文件请使用 offset 和 limit。注意：无法读取图片或… | — |
| `search_files` | 搜索文件内容或按名称查找文件。在终端中用它代替 grep/rg/find/ls。基于 Ripgrep，比 shell 等效命令更快。内容搜索 (target='content')：在文件内部进行正则搜索。输出模式：带行号的完整匹配… | — |
| `write_file` | 将内容写入文件，完全替换现有内容。在终端中用它代替 echo/cat heredoc。自动创建父目录。会覆盖整个文件 —— 针对性编辑请使用 'patch'。 | — |

## `homeassistant` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `ha_call_service` | 调用 Home Assistant 服务来控制设备。使用 ha_list_services 来发现每个域的可用服务及其参数。 | — |
| `ha_get_state` | 获取单个 Home Assistant 实体的详细状态，包括所有属性（亮度、颜色、温度设定点、传感器读数等）。 | — |
| `ha_list_entities` | 列出 Home Assistant 实体。可选按域（light, switch, climate, sensor, binary_sensor, cover, fan 等）或区域名称（客厅、厨房、卧室等）进行过滤。 | — |
| `ha_list_services` | 列出用于设备控制的可用 Home Assistant 服务（动作）。显示可以在每种设备类型上执行的操作以及它们接受的参数。使用此工具来发现如何控制通过 ha_list_entities 找到的设备。 | — |

:::note
**Honcho 工具** (`honcho_conclude`, `honcho_context`, `honcho_profile`, `honcho_search`) 不再是内置工具。它们通过 Honcho 记忆提供者插件提供，位于 `plugins/memory/honcho/`。有关安装和使用请参阅 [插件](../user-guide/features/plugins.md)。
:::

## `image_gen` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `image_generate` | 使用 FLUX 2 Pro 模型根据文本提示生成高质量图像，并自动进行 2 倍放大。创建精细的艺术图像，并自动放大以获得高分辨率结果。返回单个放大后的图像 URL。使用…显示它。 | FAL_KEY |

## `memory` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `memory` | 将重要信息保存到持久记忆中，以便跨会话保存。你的记忆会在会话开始时出现在系统提示词中 —— 这是你在对话之间记住用户和环境信息的方式。何时保存… | — |

## `messaging` 工具集

| 工具 | 描述 | 需要环境变量 |
|------|-------------|----------------------|
| `send_message` | 向连接的消息平台发送消息，或列出可用目标。重要提示：当用户要求发送到特定频道或个人（而不仅仅是简单的平台名称）时，请先调用 send_message(action='list') 以查看可用目标… | — |
## `moa` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `mixture_of_agents` | 通过多个前沿 LLM 协作路由并解决难题。该工具会发起 5 次 API 调用（4 个参考模型 + 1 个聚合模型），并投入最大的推理算力 —— 请谨慎将其用于真正困难的问题。最适用于：复杂数学、高级算法等。 | OPENROUTER_API_KEY |

## `rl` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `rl_check_status` | 获取训练运行的状态和指标。受速率限制：对同一运行的检查强制执行 30 分钟的最小间隔。返回 WandB 指标：step、state、reward_mean、loss、percent_correct。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_edit_config` | 更新配置字段。请先使用 rl_get_current_config() 查看所选环境的所有可用字段。每个环境都有不同的可配置选项。基础设施设置（tokenizer、URLs、lora_rank、learning_ra… | TINKER_API_KEY, WANDB_API_KEY |
| `rl_get_current_config` | 获取当前环境配置。仅返回可修改的字段：group_size、max_token_length、total_steps、steps_per_eval、use_wandb、wandb_name、max_num_workers。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_get_results` | 获取已完成训练运行的最终结果和指标。返回最终指标和训练权重的路径。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_list_environments` | 列出所有可用的 RL 环境。返回环境名称、路径和描述。提示：使用文件工具读取 file_path，以了解每个环境的工作原理（验证器、数据加载、奖励）。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_list_runs` | 列出所有训练运行（进行中和已完成）及其状态。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_select_environment` | 选择一个用于训练的 RL 环境。加载环境的默认配置。选择后，使用 rl_get_current_config() 查看设置，使用 rl_edit_config() 进行修改。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_start_training` | 使用当前环境和配置开始新的 RL 训练运行。大多数训练参数（lora_rank、learning_rate 等）是固定的。开始前使用 rl_edit_config() 设置 group_size、batch_size、wandb_project。警告：训练… | TINKER_API_KEY, WANDB_API_KEY |
| `rl_stop_training` | 停止正在运行的训练任务。如果指标表现不佳、训练停滞或你想尝试不同的设置，请使用此工具。 | TINKER_API_KEY, WANDB_API_KEY |
| `rl_test_inference` | 对任何环境进行快速推理测试。使用 OpenRouter 运行几步推理 + 评分。默认：3 步 x 16 次生成 = 每个模型 48 次 rollout，测试 3 个模型 = 总计 144 次。测试环境加载、提示词构建、推理… | TINKER_API_KEY, WANDB_API_KEY |

## `session_search` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `session_search` | 搜索你关于过去对话的长期记忆。这是你的回忆能力 —— 每一个过去的会话都是可搜索的，该工具会总结发生过的事情。在以下情况请主动使用：- 用户说“我们以前做过这个”、“记得当时”、“上次… | — |

## `skills` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能是你的程序性记忆 —— 针对重复性任务类型的可重用方法。新技能保存在 ~/.hermes/skills/；现有技能可以在其所在地进行修改。操作：create (完整的 SKILL.m… | — |
| `skill_view` | 技能允许加载有关特定任务和工作流的信息，以及脚本和模板。加载技能的完整内容或访问其链接的文件（参考资料、模板、脚本）。第一次调用返回 SKILL.md 内容以及… | — |
| `skills_list` | 列出可用技能（名称 + 描述）。使用 skill_view(name) 加载完整内容。 | — |

## `terminal` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `process` | 管理通过 terminal(background=true) 启动的后台进程。操作：'list'（显示所有）、'poll'（检查状态 + 新输出）、'log'（带分页的完整输出）、'wait'（阻塞直到完成或超时）、'kill'（终止）、'write'（发送… | — |
| `terminal` | 在 Linux 环境中执行 shell 命令。文件系统在调用之间持久化。对于长时间运行的服务器，请设置 `background=true`。设置 `notify_on_complete=true`（配合 `background=true`）可在进程结束时获得自动通知 —— 无需轮询。不要使用 cat/head/tail —— 请使用 read_file。不要使用 grep/rg/find —— 请使用 search_files。 | — |

## `todo` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `todo` | 管理当前会话的任务列表。适用于步骤超过 3 步的复杂任务，或用户提供多个任务时。不带参数调用可读取当前列表。写入操作：- 提供 'todos' 数组以创建/更新项目 - merge=… | — |

## `vision` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `vision_analyze` | 使用 AI 视觉分析图像。提供全面的描述并回答有关图像内容的特定问题。 | — |

## `web` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `web_search` | 在网上搜索任何主题的信息。返回最多 5 条包含标题、URL 和描述的相关结果。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |
| `web_extract` | 从网页 URL 提取内容。以 markdown 格式返回页面内容。也适用于 PDF URL —— 直接传递 PDF 链接，它会转换为 markdown 文本。少于 5000 字符的页面返回完整 markdown；较大的页面由 LLM 进行总结。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |

## `tts` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `text_to_speech` | 将文本转换为语音音频。返回一个 MEDIA: 路径，平台将其作为语音消息发送。在 Telegram 上以语音气泡播放，在 Discord/WhatsApp 上作为音频附件。在 CLI 模式下，保存到 ~/voice-memos/。语音和提供商… | — |
