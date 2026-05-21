---
sidebar_position: 4
title: "工具集参考"
description: "Hermes 核心工具集、复合工具集、平台工具集和动态工具集参考"
---

<a id="toolsets-reference"></a>
# 工具集参考

工具集是已命名的工具包，用于控制 Agent 可以执行的操作。它们是按平台、会话或任务配置工具可用性的主要机制。

<a id="how-toolsets-work"></a>
## 工具集的工作原理

每个工具都恰好属于一个工具集。当你启用某个工具集时，该包中的所有工具都会对 Agent 可用。工具集分为三种类型：

- **核心工具集** — 单个逻辑分组的相关工具（例如，`file` 打包了 `read_file`、`write_file`、`patch`、`search_files`）
- **复合工具集** — 针对常见场景组合多个核心工具集（例如，`debugging` 打包了文件、终端和 web 工具）
- **平台工具集** — 针对特定部署上下文的完整工具配置（例如，`hermes-cli` 是交互式 CLI 会话的默认配置）

<a id="configuring-toolsets"></a>
## 配置工具集

<a id="per-session-cli"></a>
### 按会话（CLI）

```bash
hermes chat --toolsets web,file,terminal
hermes chat --toolsets debugging        # 复合工具集 — 展开为 file + terminal + web
hermes chat --toolsets all              # 全部
```

<a id="per-platform-config-yaml"></a>
### 按平台（config.yaml）

```yaml
toolsets:
  - hermes-cli          # CLI 默认
  # - hermes-telegram   # 覆盖 Telegram 网关的配置
```

<a id="interactive-management"></a>
### 交互式管理

```bash
hermes tools                            # curses UI，按平台启用/禁用
```

或者在会话中：

```
/tools list
/tools disable browser
/tools enable homeassistant
```

<a id="core-toolsets"></a>
## 核心工具集

| 工具集 | 工具 | 用途 |
|---------|-------|------|
| `browser` | `browser_back`、`browser_cdp`、`browser_click`、`browser_console`、`browser_dialog`、`browser_get_images`、`browser_navigate`、`browser_press`、`browser_scroll`、`browser_snapshot`、`browser_type`、`browser_vision`、`web_search` | 核心浏览器自动化。包含 `web_search` 作为快速查找的备选。`browser_cdp` 和 `browser_dialog` 在运行时受控——仅当会话启动时 CDP 端点可访问时才注册（通过 `/browser connect`、`browser.cdp_url` 配置、Browserbase 或 Camofox）。`browser_dialog` 与 `browser_snapshot` 在附加 CDP 监督器时添加的 `pending_dialogs` 和 `frame_tree` 字段配合使用。 |
| `clarify` | `clarify` | 当 Agent 需要澄清时向用户提问。 |
| `code_execution` | `execute_code` | 运行通过编程方式调用 Hermes 工具的 Python 脚本。 |
| `cronjob` | `cronjob` | 调度和管理重复任务。 |
| `debugging` | composite（`file` + `terminal` + `web`） | 调试包 — 文件、进程/终端、web 提取/搜索。 |
| `delegation` | `delegate_task` | 生成隔离的子 Agent 实例以进行并行工作。 |
| `discord` | `discord` | 核心 Discord 文本/嵌入/私信操作（仅限网关）。在 `hermes-discord` 工具集上激活。 |
| `discord_admin` | `discord_admin` | Discord 管理（封禁、角色更改、频道管理）。在 `hermes-discord` 工具集上激活；要求机器人持有相关的 Discord 权限。 |
| `feishu_doc` | `feishu_doc_read` | 读取飞书/ Lark 文档内容。由飞书文档评论智能回复处理器使用。 |
| `feishu_drive` | `feishu_drive_add_comment`、`feishu_drive_list_comments`、`feishu_drive_list_comment_replies`、`feishu_drive_reply_comment` | 飞书/ Lark 云盘评论操作。限定在评论 Agent 内；不在 `hermes-cli` 或其他消息工具集上暴露。 |
| `file` | `patch`、`read_file`、`search_files`、`write_file` | 文件读取、写入、搜索和编辑。 |
| `homeassistant` | `ha_call_service`、`ha_get_state`、`ha_list_entities`、`ha_list_services` | 通过 Home Assistant 进行智能家居控制。仅当设置了 `HASS_TOKEN` 时可用。 |
| `computer_use` | `computer_use` | 通过 cua-driver 进行后台 macOS 桌面控制 — 不窃取光标/焦点。与任何支持工具的模型配合使用。仅限 macOS；需要在 `$PATH` 中存在 `cua-driver`。 |
| `image_gen` | `image_generate` | 通过 FAL.ai 进行文生图（可选用 OpenAI / xAI 后端）。 |
| `video_gen` | `video_generate` | 通过插件注册的后端（xAI Grok-Imagine、FAL.ai Veo 3.1 / Pixverse v6 / Kling O3）进行文生视频和图生视频。传入 `image_url` 可为图像制作动画；省略则为文生视频。 |
| `kanban` | `kanban_block`、`kanban_comment`、`kanban_complete`、`kanban_create`、`kanban_heartbeat`、`kanban_link`、`kanban_list`、`kanban_show`、`kanban_unblock` | 多 Agent 协调工具。为调度器生成的任务工作器（`HERMES_KANBAN_TASK`）以及显式启用 `kanban` 工具集的配置文件注册。工作器标记任务完成、阻塞、心跳、评论以及创建/链接后续任务；编排器配置文件额外获得看板路由工具，如 list/unblock。 |
| `memory` | `memory` | 跨会话持久化记忆管理。 |
| `messaging` | `send_message` | 在会话内向其他平台（Telegram、Discord 等）发送消息。 |
| `moa` | `mixture_of_agents` | 通过 Mixture of Agents 实现多模型共识。 |
| `safe` | `image_generate`、`vision_analyze`、`web_extract`、`web_search`（通过 `includes`） | 只读研究 + 媒体生成。无文件写入、无终端、无代码执行。 |
| `search` | `web_search` | 仅网页搜索（不含提取）。 |
| `session_search` | `session_search` | 搜索过往会话记录。 |
| `skills` | `skill_manage`、`skill_view`、`skills_list` | 技能的增删改查与浏览。 |
| `spotify` | `spotify_albums`、`spotify_devices`、`spotify_library`、`spotify_playback`、`spotify_playlists`、`spotify_queue`、`spotify_search` | 原生 Spotify 控制（播放、队列、搜索、播放列表、专辑、库）。由捆绑的 `spotify` 插件注册。 |
| `terminal` | `process`、`terminal` | Shell 命令执行和后台进程管理。 |
| `todo` | `todo` | 会话内的任务列表管理。 |
| `tts` | `text_to_speech` | 文本转语音音频生成。 |
| `vision` | `vision_analyze` | 通过支持视觉的模型进行图像分析。 |
| `video` | `video_analyze` | 视频分析与理解工具（可选加入，不在默认工具集中 — 通过 `--toolsets` 显式添加）。 |
| `web` | `web_extract`、`web_search` | 网页搜索与页面内容提取。 |
| `x_search` | `x_search` | 通过 xAI 内置的 `x_search` Responses 工具搜索 X（Twitter）帖子和线程。默认关闭；通过 `hermes tools` 选择启用。仅当配置了 xAI 凭证（SuperGrok OAuth 或 `XAI_API_KEY`）时才注册模式。 |
| `yuanbao` | `yb_query_group_info`、`yb_query_group_members`、`yb_search_sticker`、`yb_send_dm`、`yb_send_sticker` | 元宝私信/群组操作和贴纸搜索。仅在 `hermes-yuanbao` 上注册。 |
<a id="platform-toolsets"></a>
## 平台工具集

平台工具集定义了部署目标所需的完整工具配置。大多数消息平台使用与 `hermes-cli` 相同的工具集：

| 工具集 | 与 `hermes-cli` 的差异 |
|---------|-------------------------------|
| `hermes-cli` | 完整工具集——交互式 CLI 会话的默认配置。包含文件、终端、网页、浏览器、记忆、技能、视觉、图像生成、待办事项、文本转语音、委托、代码执行、定时任务、会话搜索、澄清以及 `safe`（只读）捆绑包，再加上标准消息工具。 |
| `hermes-acp` | 去掉了 `clarify`、`cronjob`、`image_generate`、`send_message`、`text_to_speech` 以及所有四个 Home Assistant 工具。专注于 IDE 上下文中的编码任务。 |
| `hermes-api-server` | 去掉了 `clarify`、`send_message` 和 `text_to_speech`。保留其他所有工具——适用于无法进行用户交互的程序化访问场景。 |
| `hermes-cron` | 与 `hermes-cli` 相同。 |
| `hermes-telegram` | 与 `hermes-cli` 相同。 |
| `hermes-discord` | 在 `hermes-cli` 基础上增加了 `discord` 和 `discord_admin`。 |
| `hermes-slack` | 与 `hermes-cli` 相同。 |
| `hermes-whatsapp` | 与 `hermes-cli` 相同。 |
| `hermes-signal` | 与 `hermes-cli` 相同。 |
| `hermes-matrix` | 与 `hermes-cli` 相同。 |
| `hermes-mattermost` | 与 `hermes-cli` 相同。 |
| `hermes-email` | 与 `hermes-cli` 相同。 |
| `hermes-sms` | 与 `hermes-cli` 相同。 |
| `hermes-bluebubbles` | 与 `hermes-cli` 相同。 |
| `hermes-dingtalk` | 与 `hermes-cli` 相同。 |
| `hermes-feishu` | 增加了五个 `feishu_doc_*` / `feishu_drive_*` 工具（仅由文档评论处理器使用，不用于常规聊天适配器）。 |
| `hermes-qqbot` | 与 `hermes-cli` 相同。 |
| `hermes-wecom` | 与 `hermes-cli` 相同。 |
| `hermes-wecom-callback` | 与 `hermes-cli` 相同。 |
| `hermes-weixin` | 与 `hermes-cli` 相同。 |
| `hermes-yuanbao` | 在 `hermes-cli` 基础上增加了五个 `yb_*` 工具（私信/群组/贴纸）。 |
| `hermes-homeassistant` | 与 `hermes-cli` 相同（Home Assistant 工具默认已存在，当设置了 `HASS_TOKEN` 时激活）。 |
| `hermes-webhook` | 与 `hermes-cli` 相同。 |
| `hermes-gateway` | 内部网关编排器工具集——所有 `hermes-&lt;platform&gt;` 工具集的并集；用于网关需要接受任何消息源的场景。 |

<a id="dynamic-toolsets"></a>
## 动态工具集

<a id="mcp-server-toolsets"></a>
### MCP 服务器工具集

每个配置的 MCP 服务器会在运行时生成一个 `mcp-&lt;server&gt;` 工具集。例如，如果你配置了一个 `github` MCP 服务器，则会创建包含该服务器暴露的所有工具的 `mcp-github` 工具集。

```yaml
# config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
```

这会创建一个 `mcp-github` 工具集，你可以在 `--toolsets` 或平台配置中引用它。

<a id="plugin-toolsets"></a>
### 插件工具集

插件可以在初始化期间通过 `ctx.register_tool()` 注册自己的工具集。这些工具集会出现在内置工具集旁边，并且可以像内置工具集一样启用/禁用。

<a id="custom-toolsets"></a>
### 自定义工具集

在 `config.yaml` 中定义自定义工具集，以创建项目特定的捆绑包：
```yaml
toolsets:
  - hermes-cli
custom_toolsets:
  data-science:
    - file
    - terminal
    - code_execution
    - web
    - vision
```

<a id="wildcards"></a>
### 通配符

- `all` 或 `*` — 展开为所有已注册的工具集（内置 + 动态 + 插件）

<a id="relationship-to-hermes-tools"></a>
## 与 `hermes tools` 的关系

`hermes tools` 命令提供了一个基于 curses 的界面，用于按平台逐个启用或禁用单个工具。它在工具级别（比工具集更细粒度）上操作，并将设置持久化到 `config.yaml` 中。即使某个工具集已启用，被禁用的工具也会被过滤掉。

另请参阅：[工具参考](./tools-reference.md) 以获取完整的单个工具列表及其参数。
