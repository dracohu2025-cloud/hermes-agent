---
sidebar_position: 4
title: "工具集参考"
description: "Hermes 核心、复合、平台及动态工具集参考"
---

# 工具集参考 {#toolsets-reference}

工具集是命名的工具包，用于控制 Agent 能做什么。它们是按平台、按会话或按任务配置工具可用性的主要机制。

## 工具集的工作原理 {#how-toolsets-work}

每个工具恰好属于一个工具集。当你启用一个工具集后，该包中的所有工具都对 Agent 可用。工具集分为三种类型：

- **核心** — 相关工具的单个逻辑组（例如，`file` 打包了 `read_file`、`write_file`、`patch`、`search_files`）
- **复合** — 为常见场景组合多个核心工具集（例如，`debugging` 打包了文件、终端和 Web 工具）
- **平台** — 针对特定部署上下文的完整工具配置（例如，`hermes-cli` 是交互式 CLI 会话的默认工具集）

## 配置工具集 {#configuring-toolsets}

### 按会话（CLI） {#per-session-cli}

```bash
hermes chat --toolsets web,file,terminal
hermes chat --toolsets debugging        # 复合 — 展开为 file + terminal + web
hermes chat --toolsets all              # 全部
```

### 按平台（config.yaml） {#per-platform-config-yaml}

```yaml
toolsets:
  - hermes-cli          # CLI 默认
  # - hermes-telegram   # 为 Telegram 网关覆盖
```

### 交互式管理 {#interactive-management}

```bash
hermes tools                            # 基于 curses 的 UI，用于按平台启用/禁用
```

或在会话中：

```
/tools list
/tools disable browser
/tools enable rl
```

## 核心工具集 {#core-toolsets}

| 工具集 | 工具 | 用途 |
|---------|-------|------|
| `browser` | `browser_back`, `browser_click`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `web_search` | 核心浏览器自动化。包含 `web_search` 作为快速查找的备用。`browser_cdp` 和 `browser_dialog` 位于独立的 `browser-cdp` 工具集中，仅当会话启动时可访问 CDP 端点时才注册——通过 `/browser connect`、`browser.cdp_url` 配置、Browserbase 或 Camofox。`browser_dialog` 与 `pending_dialogs` 和 `frame_tree` 字段协同工作，这些字段在附加了 CDP 监管者（supervisor）后由 `browser_snapshot` 添加。 |
| `clarify` | `clarify` | 当 Agent 需要澄清时向用户提问。 |
| `code_execution` | `execute_code` | 运行可通过编程方式调用 Hermes 工具的 Python 脚本。 |
| `cronjob` | `cronjob` | 调度和管理重复性任务。 |
| `debugging` | 复合（`file` + `terminal` + `web`） | 调试包——文件、进程/终端、Web 提取/搜索。 |
| `delegation` | `delegate_task` | 生成独立的子 Agent 实例以并行工作。 |
| `discord` | `discord` | 核心 Discord 文本/嵌入/私信操作（仅限网关）。在 `hermes-discord` 工具集上激活。 |
| `discord_admin` | `discord_admin` | Discord 管理（封禁、角色变更、频道管理）。在 `hermes-discord` 工具集上激活；需要机器人持有相关的 Discord 权限。 |
| `feishu_doc` | `feishu_doc_read` | 读取飞书文档内容。由飞书文档评论智能回复处理程序使用。 |
| `feishu_drive` | `feishu_drive_add_comment`, `feishu_drive_list_comments`, `feishu_drive_list_comment_replies`, `feishu_drive_reply_comment` | 飞书云盘评论操作。仅限于评论 Agent；不在 `hermes-cli` 或其他消息工具集上暴露。 |
| `file` | `patch`, `read_file`, `search_files`, `write_file` | 文件读取、写入、搜索和编辑。 |
| `homeassistant` | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` | 通过 Home Assistant 实现智能家居控制。仅在设置了 `HASS_TOKEN` 时可用。 |
| `image_gen` | `image_generate` | 通过 FAL.ai（可选 OpenAI / xAI 后端）进行文生图。 |
| `memory` | `memory` | 持久化跨会话记忆管理。 |
| `messaging` | `send_message` | 在会话内向其他平台（Telegram、Discord 等）发送消息。 |
| `moa` | `mixture_of_agents` | 通过 Agent 混合实现多模型共识。 |
| `rl` | `rl_check_status`, `rl_edit_config`, `rl_get_current_config`, `rl_get_results`, `rl_list_environments`, `rl_list_runs`, `rl_select_environment`, `rl_start_training`, `rl_stop_training`, `rl_test_inference` | 强化学习训练环境管理（Atropos）。 |
| `safe` | `image_generate`, `vision_analyze`, `web_extract`, `web_search`（通过 `includes`） | 只读研究 + 媒体生成。无文件写入，无终端，无代码执行。 |
| `search` | `web_search` | 仅网页搜索（无提取）。 |
| `session_search` | `session_search` | 搜索历史对话会话。 |
| `skills` | `skill_manage`, `skill_view`, `skills_list` | 技能的增删改查与浏览。 |
| `spotify` | `spotify_albums`, `spotify_devices`, `spotify_library`, `spotify_playback`, `spotify_playlists`, `spotify_queue`, `spotify_search` | 原生 Spotify 控制（播放、队列、搜索、播放列表、专辑、库）。由捆绑的 `spotify` 插件注册。 |
| `terminal` | `process`, `terminal` | Shell 命令执行和后台进程管理。 |
| `todo` | `todo` | 会话内的任务列表管理。 |
| `tts` | `text_to_speech` | 文本转语音音频生成。 |
| `vision` | `vision_analyze` | 通过视觉模型进行图像分析。 |
| `web` | `web_extract`, `web_search` | 网页搜索和页面内容提取。 |
| `yuanbao` | `yb_query_group_info`, `yb_query_group_members`, `yb_search_sticker`, `yb_send_dm`, `yb_send_sticker` | 元宝私信/群组操作和贴纸搜索。仅在 `hermes-yuanbao` 上注册。 |
## 平台工具集 {#platform-toolsets}

平台工具集为部署目标定义了完整的工具配置。大多数消息平台使用与 `hermes-cli` 相同的工具集：

| 工具集 | 与 `hermes-cli` 的差异 |
|---------|-------------------------------|
| `hermes-cli` | 完整工具集 — 38 个工具。交互式 CLI 会话的默认配置。 |
| `hermes-acp` | 移除了 `clarify`、`cronjob`、`image_generate`、`send_message`、`text_to_speech` 以及所有四个 Home Assistant 工具。专注于 IDE 环境中的编码任务。 |
| `hermes-api-server` | 移除了 `clarify`、`send_message` 和 `text_to_speech`。保留其余所有工具——适用于无法进行用户交互的程序化访问场景。 |
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
| `hermes-feishu` | 增加了五个 `feishu_doc_*` / `feishu_drive_*` 工具（仅文档评论处理使用，常规聊天适配器不使用）。 |
| `hermes-qqbot` | 与 `hermes-cli` 相同。 |
| `hermes-wecom` | 与 `hermes-cli` 相同。 |
| `hermes-wecom-callback` | 与 `hermes-cli` 相同。 |
| `hermes-weixin` | 与 `hermes-cli` 相同。 |
| `hermes-yuanbao` | 在 `hermes-cli` 基础上增加了五个 `yb_*` 工具（私信/群组/贴纸）。 |
| `hermes-homeassistant` | 与 `hermes-cli` 相同（Home Assistant 工具默认已存在，并在设置 `HASS_TOKEN` 时激活）。 |
| `hermes-webhook` | 与 `hermes-cli` 相同。 |
| `hermes-gateway` | 内部网关编排器工具集——所有 `hermes-<平台>` 工具集的并集；用于网关需要接受任意消息源的场景。 |

## 动态工具集 {#dynamic-toolsets}

### MCP 服务器工具集 {#mcp-server-toolsets}

每个配置的 MCP 服务器会在运行时生成一个 `mcp-<服务器>` 工具集。例如，如果你配置了一个 `github` MCP 服务器，则会创建一个 `mcp-github` 工具集，包含该服务器暴露的所有工具。

```yaml
# config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
```

这创建了一个 `mcp-github` 工具集，你可以在 `--toolsets` 或平台配置中引用它。

### 插件工具集 {#plugin-toolsets}

插件可以在初始化期间通过 `ctx.register_tool()` 注册自己的工具集。这些工具集会出现在内置工具集旁边，并且可以用相同的方式启用/禁用。

### 自定义工具集 {#custom-toolsets}

在 `config.yaml` 中定义自定义工具集，以创建项目特定的工具包：

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

### 通配符 {#wildcards}

- `all` 或 `*` — 展开为所有已注册的工具集（内置 + 动态 + 插件）
## 与 `hermes tools` 的关系 {#relationship-to-hermes-tools}

`hermes tools` 命令提供了一个基于 curses 的界面，用于按平台单独启用或禁用某个工具。它在工具级别（比工具集更细粒度）上操作，并将设置持久化到 `config.yaml` 中。即使工具集已启用，被禁用的工具也会被过滤掉。

另请参阅：[工具参考](./tools-reference.md) 以获取所有单个工具及其参数的完整列表。
