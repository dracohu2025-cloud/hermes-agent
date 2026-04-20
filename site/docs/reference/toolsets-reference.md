---
sidebar_position: 4
title: "Toolsets 参考"
description: "Hermes 核心、复合、平台和动态 Toolsets 参考"
---

# Toolsets 参考 {#toolsets-reference}

Toolsets 是工具的命名集合，用来控制 Agent 能做什么。它们是按平台、按会话或按任务配置工具可用性的主要机制。

## Toolsets 的工作原理 {#how-toolsets-work}

每个工具恰好属于一个 Toolset。启用某个 Toolset 后，该集合中的所有工具都会对 Agent 可用。Toolsets 分为三种类型：

- **Core（核心）** — 单个逻辑相关的工具组（例如 `file` 包含 `read_file`、`write_file`、`patch`、`search_files`）
- **Composite（复合）** — 将多个核心 Toolset 组合起来应对常见场景（例如 `debugging` 包含 file、terminal 和 web 工具）
- **Platform（平台）** — 针对特定部署场景的完整工具配置（例如 `hermes-cli` 是交互式 CLI 会话的默认配置）

## 配置 Toolsets {#configuring-toolsets}

### 按会话配置（CLI） {#per-session-cli}

```bash
hermes chat --toolsets web,file,terminal
hermes chat --toolsets debugging        # 复合 Toolset — 展开为 file + terminal + web
hermes chat --toolsets all              # 启用所有工具
```

### 按平台配置（config.yaml） {#per-platform-config-yaml}

```yaml
toolsets:
  - hermes-cli          # CLI 的默认配置
  # - hermes-telegram   # Telegram 网关的覆盖配置
```

### 交互式管理 {#interactive-management}

```bash
hermes tools                            # curses 界面，可按平台启用/禁用工具
```

或在会话中：

```
/tools list
/tools disable browser
/tools enable rl
```

## 核心 Toolsets {#core-toolsets}

| Toolset | 工具 | 用途 |
|---------|------|------|
| `browser` | `browser_back`, `browser_cdp`, `browser_click`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `web_search` | 完整的浏览器自动化。包含 `web_search` 作为快速查询的兜底方案。`browser_cdp` 是原始 CDP 透传，需要可访问的 CDP 端点才能使用 —— 仅在 `/browser connect` 处于活动状态或设置了 `browser.cdp_url` 时才会出现。 |
| `clarify` | `clarify` | 当 Agent 需要澄清时向用户提问。 |
| `code_execution` | `execute_code` | 运行以编程方式调用 Hermes 工具的 Python 脚本。 |
| `cronjob` | `cronjob` | 调度和管理周期性任务。 |
| `delegation` | `delegate_task` | 生成隔离的 sub-agent 实例以并行处理工作。 |
| `feishu_doc` | `feishu_doc_read` | 读取飞书/ Lark 文档内容。由飞书文档评论智能回复处理器使用。 |
| `feishu_drive` | `feishu_drive_add_comment`, `feishu_drive_list_comments`, `feishu_drive_list_comment_replies`, `feishu_drive_reply_comment` | 飞书/ Lark 云盘评论操作。仅限评论 Agent 使用；不在 `hermes-cli` 或其他消息类 Toolset 上暴露。 |
| `file` | `patch`, `read_file`, `search_files`, `write_file` | 文件的读取、写入、搜索和编辑。 |
| `homeassistant` | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` | 通过 Home Assistant 控制智能家居。仅在设置了 `HASS_TOKEN` 时可用。 |
| `image_gen` | `image_generate` | 通过 FAL.ai 进行文生图生成。 |
| `memory` | `memory` | 跨会话的持久化记忆管理。 |
| `messaging` | `send_message` | 在会话内向其他平台（Telegram、Discord 等）发送消息。 |
| `moa` | `mixture_of_agents` | 通过 Mixture of Agents 实现多模型共识。 |
| `rl` | `rl_check_status`, `rl_edit_config`, `rl_get_current_config`, `rl_get_results`, `rl_list_environments`, `rl_list_runs`, `rl_select_environment`, `rl_start_training`, `rl_stop_training`, `rl_test_inference` | RL 训练环境管理（Atropos）。 |
| `search` | `web_search` | 仅网页搜索（不含提取功能）。 |
| `session_search` | `session_search` | 搜索过往对话会话。 |
| `skills` | `skill_manage`, `skill_view`, `skills_list` | Skill 的增删改查和浏览。 |
| `terminal` | `process`, `terminal` | Shell 命令执行和后台进程管理。 |
| `todo` | `todo` | 会话内的任务列表管理。 |
| `tts` | `text_to_speech` | 文本转语音音频生成。 |
| `vision` | `vision_analyze` | 通过具备视觉能力的模型进行图像分析。 |
| `web` | `web_extract`, `web_search` | 网页搜索和页面内容提取。 |
## 组合 Toolset {#composite-toolsets}

这些会展开为多个核心 toolset，为常见场景提供便捷的简写方式：

| Toolset | 展开为 | 使用场景 |
|---------|-----------|----------|
| `debugging` | `web` + `file` + `process`，通过 `includes` 包含 `terminal` —— 实际效果为 `patch`、`process`、`read_file`、`search_files`、`terminal`、`web_extract`、`web_search`、`write_file` | 调试会话 —— 文件访问、终端和网页调研，无需浏览器或委派开销。 |
| `safe` | `image_generate`、`vision_analyze`、`web_extract`、`web_search` | 只读调研和媒体生成。无文件写入、无终端访问、无代码执行。适合不受信任或受限环境。 |

## 平台 Toolset {#platform-toolsets}

平台 toolset 定义了部署目标的完整工具配置。大多数消息平台使用的 toolset 与 `hermes-cli` 相同：

| Toolset | 与 `hermes-cli` 的差异 |
|---------|-------------------------------|
| `hermes-cli` | 完整 toolset —— 包含 `clarify` 在内的全部 36 个核心工具。交互式 CLI 会话的默认配置。 |
| `hermes-acp` | 移除 `clarify`、`cronjob`、`image_generate`、`send_message`、`text_to_speech`、homeassistant 工具。专注于 IDE 场景下的编码任务。 |
| `hermes-api-server` | 移除 `clarify`、`send_message` 和 `text_to_speech`。保留其他所有工具 —— 适合无法与用户交互的编程访问场景。 |
| `hermes-telegram` | 与 `hermes-cli` 相同。 |
| `hermes-discord` | 与 `hermes-cli` 相同。 |
| `hermes-slack` | 与 `hermes-cli` 相同。 |
| `hermes-whatsapp` | 与 `hermes-cli` 相同。 |
| `hermes-signal` | 与 `hermes-cli` 相同。 |
| `hermes-matrix` | 与 `hermes-cli` 相同。 |
| `hermes-mattermost` | 与 `hermes-cli` 相同。 |
| `hermes-email` | 与 `hermes-cli` 相同。 |
| `hermes-sms` | 与 `hermes-cli` 相同。 |
| `hermes-bluebubbles` | 与 `hermes-cli` 相同。 |
| `hermes-dingtalk` | 与 `hermes-cli` 相同。 |
| `hermes-feishu` | 与 `hermes-cli` 相同。注意：`feishu_doc` / `feishu_drive` toolset 仅由文档评论处理器使用，普通的飞书聊天适配器不会使用。 |
| `hermes-qqbot` | 与 `hermes-cli` 相同。 |
| `hermes-wecom` | 与 `hermes-cli` 相同。 |
| `hermes-wecom-callback` | 与 `hermes-cli` 相同。 |
| `hermes-weixin` | 与 `hermes-cli` 相同。 |
| `hermes-homeassistant` | 与 `hermes-cli` 相同，且 `homeassistant` toolset 始终开启。 |
| `hermes-webhook` | 与 `hermes-cli` 相同。 |
| `hermes-gateway` | 内部网关编排器 toolset —— 当网关需要接受任意消息来源时，取最广泛可能的工具集合的并集。 |

## 动态 Toolset {#dynamic-toolsets}

### MCP 服务器 Toolset {#mcp-server-toolsets}

每个配置的 MCP 服务器会在运行时生成一个 `mcp-&lt;server&gt;` toolset。例如，如果你配置了一个 `github` MCP 服务器，就会创建一个 `mcp-github` toolset，包含该服务器暴露的所有工具。

```yaml
# config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
```

这会创建一个 `mcp-github` toolset，你可以在 `--toolsets` 或平台配置中引用它。

### 插件 Toolset {#plugin-toolsets}

插件可以在初始化期间通过 `ctx.register_tool()` 注册自己的 toolset。这些 toolset 会与内置 toolset 一起显示，并且可以用同样的方式启用或禁用。

### 自定义 Toolset {#custom-toolsets}

在 `config.yaml` 中定义自定义 toolset，以创建项目特定的工具包：

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

- `all` 或 `*` —— 展开为所有已注册的 toolset（内置 + 动态 + 插件）

## 与 `hermes tools` 的关系 {#relationship-to-hermes-tools}

`hermes tools` 命令提供一个基于 curses 的 UI，用于按平台单独开启或关闭工具。这操作在工具层面（比 toolset 更细粒度），并持久化到 `config.yaml`。即使某个 toolset 已启用，其中被禁用的工具也会被过滤掉。

另请参阅：[工具参考](./tools-reference.md)，获取完整工具列表及其参数。
