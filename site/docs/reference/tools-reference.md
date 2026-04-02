---
sidebar_position: 3
title: "内置工具参考"
description: "Hermes 内置工具集的权威参考，按工具集分组"
---

# 内置工具参考

本文档记录了代码中现有的 Hermes 内置工具注册表。具体可用性仍可能因平台、凭证和启用的工具集而异。

## `browser` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `browser_back` | 在浏览器历史记录中导航回上一页。需要先调用 `browser_navigate`。 | — |
| `browser_click` | 点击快照中通过其引用 ID 标识的元素（例如 `@e5`）。引用 ID 在快照输出中以方括号显示。需要先调用 `browser_navigate` 和 `browser_snapshot`。 | — |
| `browser_close` | 关闭浏览器会话并释放资源。完成浏览器任务后调用此工具以释放 Browserbase 会话配额。 | — |
| `browser_console` | 从当前页面获取浏览器控制台输出和 JavaScript 错误。返回 `console.log`/`warn`/`error`/`info` 消息和未捕获的 JS 异常。使用此工具来检测静默的 JavaScript 错误、失败的 API 调用和应用程序警告。需要… | — |
| `browser_get_images` | 获取当前页面上所有图片的列表及其 URL 和替代文本。对于需要结合视觉工具分析的图片查找很有用。需要先调用 `browser_navigate`。 | — |
| `browser_navigate` | 在浏览器中导航到指定 URL。初始化会话并加载页面。必须在调用其他浏览器工具之前调用。对于简单的信息检索，建议优先使用 `web_search` 或 `web_extract`（更快、更便宜）。当需要…时，才使用浏览器工具。 | — |
| `browser_press` | 按下键盘按键。对于提交表单（Enter）、导航（Tab）或使用键盘快捷键很有用。需要先调用 `browser_navigate`。 | — |
| `browser_scroll` | 沿指定方向滚动页面。使用此工具来显示当前视口上方或下方可能存在的更多内容。需要先调用 `browser_navigate`。 | — |
| `browser_snapshot` | 获取当前页面无障碍树的基于文本的快照。返回带有引用 ID（如 `@e1`、`@e2`）的交互式元素，供 `browser_click` 和 `browser_type` 使用。`full=false`（默认）：包含交互式元素的紧凑视图。`full=true`：包含…的完整视图。 | — |
| `browser_type` | 向由其引用 ID 标识的输入字段键入文本。先清除字段，然后键入新文本。需要先调用 `browser_navigate` 和 `browser_snapshot`。 | — |
| `browser_vision` | 截取当前页面的屏幕截图，并使用视觉 AI 进行分析。当你需要视觉上理解页面内容时使用此工具——特别适用于验证码、视觉验证挑战、复杂布局，或者当文本快照…时。 | — |

## `clarify` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `clarify` | 当你需要澄清、反馈或在继续之前需要用户做出决定时，向用户提问。支持两种模式：1. **多项选择** — 提供最多 4 个选项。用户选择一个或通过第 5 个“其他”选项输入自己的答案。2.… | — |

## `code_execution` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `execute_code` | 运行一个可以编程式调用 Hermes 工具的 Python 脚本。当你需要 3 次以上的工具调用并在其间有处理逻辑时，需要在工具输出进入你的上下文之前对其进行过滤/缩减时，需要条件分支（…）时，使用此工具。 | — |

## `cronjob` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `cronjob` | 统一的计划任务管理器。使用 `action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"` 或 `"remove"` 来管理任务。支持带有一个或多个附加技能（skill）的技能支持型任务，更新时使用 `skills=[]` 可清除附加的技能。Cron 任务在全新的会话中运行，没有当前聊天上下文。 | — |

## `delegation` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `delegate_task` | 生成一个或多个子 Agent 在隔离的上下文中处理任务。每个子 Agent 拥有自己的对话、终端会话和工具集。仅返回最终摘要——中间的工具结果永远不会进入你的上下文窗口。两种… | — |

## `file` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `patch` | 在文件中进行有针对性的查找和替换编辑。在终端中请使用此工具代替 `sed`/`awk`。使用模糊匹配（9 种策略），因此微小的空格/缩进差异不会导致失败。返回统一的差异（diff）。编辑后自动运行语法检查… | — |
| `read_file` | 读取带有行号和分页的文本文件。在终端中请使用此工具代替 `cat`/`head`/`tail`。输出格式：`LINE_NUM\|CONTENT`。如果未找到文件，会建议相似的文件名。对于大文件，请使用 `offset` 和 `limit` 参数。注意：无法读取图像或… | — |
| `search_files` | 搜索文件内容或按名称查找文件。在终端中请使用此工具代替 `grep`/`rg`/`find`/`ls`。基于 Ripgrep，比 shell 等效命令更快。内容搜索（`target='content'`）：在文件内部进行正则表达式搜索。输出模式：包含行…的完整匹配。 | — |
| `write_file` | 将内容写入文件，完全替换现有内容。在终端中请使用此工具代替 `echo`/`cat` heredoc。自动创建父目录。**覆盖**整个文件——进行针对性编辑时请使用 `patch`。 | — |

## `homeassistant` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `ha_call_service` | 调用 Home Assistant 服务以控制设备。使用 `ha_list_services` 来发现每个域（domain）可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个 Home Assistant 实体的详细状态，包括所有属性（亮度、颜色、温度设定点、传感器读数等）。 | — |
| `ha_list_entities` | 列出 Home Assistant 实体。可按域（`light`、`switch`、`climate`、`sensor`、`binary_sensor`、`cover`、`fan` 等）或区域名称（客厅、厨房、卧室等）进行筛选。 | — |
| `ha_list_services` | 列出可用于设备控制的 Home Assistant 服务（操作）。显示可以在每种设备类型上执行的操作以及它们接受的参数。使用此工具来发现如何控制通过 `ha_list_entities` 找到的设备。 | — |

## `honcho` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `honcho_conclude` | 将关于用户的结论写回 Honcho 的记忆中。结论是构建用户档案的持久事实——偏好、更正、澄清、项目上下文，或者用户告诉你的任何应该被记住…的事情。 | — |
| `honcho_context` | 向 Honcho 提出自然语言问题并获取综合答案。使用 Honcho 的 LLM（辩证推理）——成本高于 `honcho_profile` 或 `honcho_search`。可以查询任何对等体（peer）：用户（默认）、AI 助手或任何命名的对等体… | — |
| `honcho_profile` | 从 Honcho 检索用户的“对等体卡片”——关于他们的关键事实（姓名、角色、偏好、沟通风格、模式）的精选列表。快速，无需 LLM 推理，成本最低。在对话开始时或当你需要快速了解…时使用。 | — |
| `honcho_search` | 对 Honcho 存储的关于用户的上下文进行语义搜索。返回根据查询相关性排序的原始摘录——无 LLM 综合。比 `honcho_context` 更便宜、更快。当你想查找特定的过去事实并基于…进行推理时很有用。 | — |

## `image_gen` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `image_generate` | 使用 FLUX 2 Pro 模型从文本提示生成高质量图像，并自动进行 2 倍超分辨率。创建详细、艺术化的图像，并自动放大以获得高分辨率结果。返回单个放大后的图像 URL。使用…显示它。 | FAL_KEY |

## `memory` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `memory` | 将重要信息保存到持久化记忆中，该记忆在会话之间持续存在。你的记忆会在会话开始时出现在你的系统提示中——这是你在对话之间记住关于用户和环境信息的方式。何时保存… | — |
## `messaging` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `send_message` | 向已连接的消息平台发送消息，或列出可用的发送目标。重要提示：当用户要求发送到特定频道或人（而不仅仅是平台名称）时，请先调用 `send_message(action='list')` 以查看可用的目标… | — |

## `moa` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `mixture_of_agents` | 通过多个前沿 LLM 协作处理难题。会进行 5 次 API 调用（4 个参考模型 + 1 个聚合器），并投入最大推理努力——请仅在处理真正困难的问题时酌情使用。最适合：复杂数学、高级算法… | `OPENROUTER_API_KEY` |

## `rl` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `rl_check_status` | 获取训练运行的状态和指标。速率限制：对同一运行进行检查的最小间隔为 30 分钟。返回 WandB 指标：步数、状态、平均奖励、损失、正确率百分比。 | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_edit_config` | 更新配置字段。请先使用 `rl_get_current_config()` 查看所选环境的所有可用字段。每个环境都有不同的可配置选项。基础设施设置（分词器、URL、lora_rank、学习率…） | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_get_current_config` | 获取当前环境配置。仅返回可修改的字段：`group_size`、`max_token_length`、`total_steps`、`steps_per_eval`、`use_wandb`、`wandb_name`、`max_num_workers`。 | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_get_results` | 获取已完成的训练运行的最终结果和指标。返回最终指标和训练权重的路径。 | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_list_environments` | 列出所有可用的 RL 环境。返回环境名称、路径和描述。提示：使用文件工具读取 `file_path` 以了解每个环境的工作原理（验证器、数据加载、奖励）。 | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_list_runs` | 列出所有训练运行（活跃和已完成）及其状态。 | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_select_environment` | 为训练选择一个 RL 环境。加载该环境的默认配置。选择后，使用 `rl_get_current_config()` 查看设置，使用 `rl_edit_config()` 修改它们。 | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_start_training` | 使用当前环境和配置启动一个新的 RL 训练运行。大多数训练参数（`lora_rank`、`learning_rate` 等）是固定的。在开始前使用 `rl_edit_config()` 设置 `group_size`、`batch_size`、`wandb_project`。警告：训练… | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_stop_training` | 停止正在运行的训练任务。如果指标看起来不佳、训练停滞或你想尝试不同设置时使用。 | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_test_inference` | 对任何环境进行快速推理测试。使用 OpenRouter 运行几步推理 + 评分。默认：3 步 x 16 次补全 = 每个模型 48 次 rollout，测试 3 个模型 = 总计 144 次。测试环境加载、提示构建、推理… | `TINKER_API_KEY`, `WANDB_API_KEY` |

## `session_search` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `session_search` | 搜索你对过去对话的长期记忆。这是你的回忆功能——每个过去的会话都是可搜索的，此工具会总结发生了什么。在以下情况下主动使用此工具：- 用户说“我们之前做过这个”、“记得当…”、“上次… | — |

## `skills` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能是你的程序性记忆——针对重复任务类型的可重用方法。新技能保存到 `~/.hermes/skills/`；现有技能可以在其所在位置修改。操作：`create`（完整的 `SKILL.md`… | — |
| `skill_view` | 技能允许加载有关特定任务和工作流的信息，以及脚本和模板。加载技能的完整内容或访问其链接的文件（参考资料、模板、脚本）。首次调用返回 `SKILL.md` 内容以及… | — |
| `skills_list` | 列出可用技能（名称 + 描述）。使用 `skill_view(name)` 加载完整内容。 | — |

## `terminal` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `process` | 管理通过 `terminal(background=true)` 启动的后台进程。操作：`list`（显示所有）、`poll`（检查状态 + 新输出）、`log`（带分页的完整输出）、`wait`（阻塞直到完成或超时）、`kill`（终止）、`write`（发送… | — |
| `terminal` | 在 Linux 环境中执行 shell 命令。文件系统在调用之间持久存在。不要使用 `cat`/`head`/`tail` 来读取文件——请改用 `read_file`。不要使用 `grep`/`rg`/`find` 来搜索——请改用 `search_files`。不要使用 `ls` 来列出目录… | — |

## `todo` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `todo` | 管理当前会话的任务列表。适用于包含 3 个以上步骤的复杂任务或用户提供多个任务时。不带参数调用以读取当前列表。写入：- 提供 `todos` 数组以创建/更新项目 - `merge=…` | — |

## `vision` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `vision_analyze` | 使用 AI 视觉分析图像。提供全面的描述并回答关于图像内容的特定问题。 | — |

## `web` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `web_search` | 在网络上搜索任何主题的信息。返回最多 5 个相关结果，包含标题、URL 和描述。 | `EXA_API_KEY` 或 `PARALLEL_API_KEY` 或 `FIRECRAWL_API_KEY` 或 `TAVILY_API_KEY` |
| `web_extract` | 从网页 URL 提取内容。以 Markdown 格式返回页面内容。也适用于 PDF URL——直接传递 PDF 链接，它会转换为 Markdown 文本。小于 5000 字符的页面返回完整 Markdown；更大的页面则由 LLM 进行摘要。 | `EXA_API_KEY` 或 `PARALLEL_API_KEY` 或 `FIRECRAWL_API_KEY` 或 `TAVILY_API_KEY` |

## `tts` 工具集

| 工具 | 描述 | 所需环境变量 |
|------|-------------|----------------------|
| `text_to_speech` | 将文本转换为语音音频。返回一个 `MEDIA:` 路径，平台会将其作为语音消息传递。在 Telegram 上以语音气泡播放，在 Discord/WhatsApp 上作为音频附件。在 CLI 模式下，保存到 `~/voice-memos/`。语音和提供商… | — |
