---
sidebar_position: 4
title: "工具集参考 (Toolsets Reference)"
description: "Hermes 核心、复合、平台及动态工具集参考"
---

# 工具集参考 (Toolsets Reference)

工具集（Toolsets）是具名的工具捆绑包，用于控制 Agent 的能力范围。它们是按平台、按会话或按任务配置工具可用性的主要机制。

## 工具集的工作原理

每个工具都恰好属于一个工具集。当你启用一个工具集时，该捆绑包中的所有工具都会对 Agent 可用。工具集分为三种类型：

- **核心 (Core)** — 相关工具的单一逻辑组（例如，`file` 捆绑了 `read_file`、`write_file`、`patch`、`search_files`）。
- **复合 (Composite)** — 为常见场景组合了多个核心工具集（例如，`debugging` 捆绑了文件、终端和 Web 工具）。
- **平台 (Platform)** — 针对特定部署上下文的完整工具配置（例如，`hermes-cli` 是交互式 CLI 会话的默认配置）。

## 配置工具集

### 按会话配置 (CLI)

```bash
hermes chat --toolsets web,file,terminal
hermes chat --toolsets debugging        # 复合工具集 — 展开为 file + terminal + web
hermes chat --toolsets all              # 启用所有工具
```

### 按平台配置 (config.yaml)

```yaml
toolsets:
  - hermes-cli          # CLI 的默认配置
  # - hermes-telegram   # 覆盖 Telegram 网关的配置
```

### 交互式管理

```bash
hermes tools                            # 启动 curses UI 以按平台启用/禁用工具
```

或者在会话中：

```
/tools list
/tools disable browser
/tools enable rl
```

## 核心工具集 (Core Toolsets)

| 工具集 | 工具列表 | 用途 |
|---------|-------|---------|
| `browser` | `browser_back`, `browser_click`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `web_search` | 完整的浏览器自动化。包含 `web_search` 作为快速查询的备选方案。 |
| `clarify` | `clarify` | 当 Agent 需要澄清时向用户提问。 |
| `code_execution` | `execute_code` | 运行以编程方式调用 Hermes 工具的 Python 脚本。 |
| `cronjob` | `cronjob` | 调度和管理周期性任务。 |
| `delegation` | `delegate_task` | 生成隔离的 subagent 实例以进行并行工作。 |
| `file` | `patch`, `read_file`, `search_files`, `write_file` | 文件的读取、写入、搜索和编辑。 |
| `homeassistant` | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` | 通过 Home Assistant 控制智能家居。仅在设置了 `HASS_TOKEN` 时可用。 |
| `image_gen` | `image_generate` | 通过 FAL.ai 进行文本生成图像。 |
| `memory` | `memory` | 持久化的跨会话记忆管理。 |
| `messaging` | `send_message` | 在会话中向其他平台（Telegram、Discord 等）发送消息。 |
| `moa` | `mixture_of_agents` | 通过 Mixture of Agents 实现多模型共识。 |
| `rl` | `rl_check_status`, `rl_edit_config`, `rl_get_current_config`, `rl_get_results`, `rl_list_environments`, `rl_list_runs`, `rl_select_environment`, `rl_start_training`, `rl_stop_training`, `rl_test_inference` | 强化学习（RL）训练环境管理 (Atropos)。 |
| `search` | `web_search` | 仅限 Web 搜索（不包含内容提取）。 |
| `session_search` | `session_search` | 搜索过去的对话会话。 |
| `skills` | `skill_manage`, `skill_view`, `skills_list` | 技能（Skill）的增删改查与浏览。 |
| `terminal` | `process`, `terminal` | Shell 命令执行和后台进程管理。 |
| `todo` | `todo` | 会话内的任务列表管理。 |
| `tts` | `text_to_speech` | 文本转语音音频生成。 |
| `vision` | `vision_analyze` | 通过具备视觉能力的模型进行图像分析。 |
| `web` | `web_extract`, `web_search` | Web 搜索和网页内容提取。 |

## 复合工具集 (Composite Toolsets)

这些工具集会展开为多个核心工具集，为常见场景提供便捷的缩写：

| 工具集 | 展开为 | 使用场景 |
|---------|-----------|----------|
| `debugging` | `patch`, `process`, `read_file`, `search_files`, `terminal`, `web_extract`, `web_search`, `write_file` | 调试会话 — 提供文件访问、终端和 Web 调研能力，且没有浏览器或任务委派的开销。 |
| `safe` | `image_generate`, `mixture_of_agents`, `vision_analyze`, `web_extract`, `web_search` | 只读调研和媒体生成。禁止文件写入、终端访问和代码执行。适用于不可信或受限的环境。 |

## 平台工具集 (Platform Toolsets)

平台工具集定义了特定部署目标的完整工具配置。大多数消息平台使用与 `hermes-cli` 相同的配置：

| 工具集 | 与 `hermes-cli` 的区别 |
|---------|-------------------------------|
| `hermes-cli` | 全量工具集 — 包含 `clarify` 在内的全部 38 个工具。交互式 CLI 会话的默认值。 |
| `hermes-acp` | 移除了 `clarify`, `cronjob`, `image_generate`, `mixture_of_agents`, `send_message`, `text_to_speech` 以及 homeassistant 工具。专注于 IDE 上下文中的编程任务。 |
| `hermes-api-server` | 移除了 `clarify`, `send_message` 和 `text_to_speech`。保留其他所有工具 — 适用于无法进行用户交互的编程访问场景。 |
| `hermes-telegram` | 与 `hermes-cli` 相同。 |
| `hermes-discord` | 与 `hermes-cli` 相同。 |
| `hermes-slack` | 与 `hermes-cli` 相同。 |
| `hermes-whatsapp` | 与 `hermes-cli` 相同。 |
| `hermes-signal` | 与 `hermes-cli` 相同。 |
| `hermes-matrix` | 与 `hermes-cli` 相同。 |
| `hermes-mattermost` | 与 `hermes-cli` 相同。 |
| `hermes-email` | 与 `hermes-cli` 相同。 |
| `hermes-sms` | 与 `hermes-cli` 相同。 |
| `hermes-dingtalk` | 与 `hermes-cli` 相同。 |
| `hermes-feishu` | 与 `hermes-cli` 相同。 |
| `hermes-wecom` | 与 `hermes-cli` 相同。 |
| `hermes-homeassistant` | 与 `hermes-cli` 相同。 |
| `hermes-webhook` | 与 `hermes-cli` 相同。 |
| `hermes-gateway` | 所有消息平台工具集的并集。当网关需要最广泛的工具支持时在内部使用。 |

## 动态工具集 (Dynamic Toolsets)

### MCP 服务器工具集

每个配置好的 MCP 服务器都会在运行时生成一个 `mcp-<server>` 工具集。例如，如果你配置了一个 `github` MCP 服务器，系统会创建一个 `mcp-github` 工具集，其中包含该服务器暴露的所有工具。

```yaml
# config.yaml
mcp:
  servers:
    github:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-github"]
```

这将创建一个 `mcp-github` 工具集，你可以在 `--toolsets` 或平台配置中引用它。

### 插件工具集

插件可以在初始化期间通过 `ctx.register_tool()` 注册自己的工具集。这些工具集会与内置工具集并列显示，并可以按同样的方式启用/禁用。

### 自定义工具集

在 `config.yaml` 中定义自定义工具集，以创建特定于项目的捆绑包：

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

### 通配符

- `all` 或 `*` — 展开为每一个已注册的工具集（内置 + 动态 + 插件）。

## 与 `hermes tools` 的关系

`hermes tools` 命令提供了一个基于 curses 的 UI，用于按平台开启或关闭单个工具。这在工具级别（比工具集更细粒度）操作，并持久化到 `config.yaml`。即使某个工具集已启用，被禁用的工具仍会被过滤掉。

另请参阅：[工具参考 (Tools Reference)](./tools-reference.md) 以获取单个工具及其参数的完整列表。
