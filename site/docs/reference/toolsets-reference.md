---
sidebar_position: 4
title: "工具集参考"
description: "Hermes 核心、组合、平台及动态工具集的参考"
---

# 工具集参考

工具集是具名的工具包，你可以通过 `hermes chat --toolsets ...` 启用，按平台配置，或在智能体运行时解析。

| 工具集 | 类型 | 解析为 |
|---------|------|-------------|
| `browser` | 核心 | `browser_back`, `browser_click`, `browser_close`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `web_search` |
| `clarify` | 核心 | `clarify` |
| `code_execution` | 核心 | `execute_code` |
| `cronjob` | 核心 | `cronjob` |
| `debugging` | 组合 | `patch`, `process`, `read_file`, `search_files`, `terminal`, `web_extract`, `web_search`, `write_file` |
| `delegation` | 核心 | `delegate_task` |
| `file` | 核心 | `patch`, `read_file`, `search_files`, `write_file` |
| `hermes-acp` | 平台 | `browser_back`, `browser_click`, `browser_close`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `delegate_task`, `execute_code`, `memory`, `patch`, `process`, `read_file`, `search_files`, `session_search`, `skill_manage`, `skill_view`, `skills_list`, `terminal`, `todo`, `vision_analyze`, `web_extract`, `web_search`, `write_file` |
| `hermes-cli` | 平台 | `browser_back`, `browser_click`, `browser_close`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `clarify`, `cronjob`, `delegate_task`, `execute_code`, `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services`, `honcho_conclude`, `honcho_context`, `honcho_profile`, `honcho_search`, `image_generate`, `memory`, `mixture_of_agents`, `patch`, `process`, `read_file`, `search_files`, `send_message`, `session_search`, `skill_manage`, `skill_view`, `skills_list`, `terminal`, `text_to_speech`, `todo`, `vision_analyze`, `web_extract`, `web_search`, `write_file` |
| `hermes-api-server` | 平台 | _(同 hermes-cli)_ |
| `hermes-dingtalk` | 平台 | _(同 hermes-cli)_ |
| `hermes-feishu` | 平台 | _(同 hermes-cli)_ |
| `hermes-wecom` | 平台 | _(同 hermes-cli)_ |
| `hermes-discord` | 平台 | _(同 hermes-cli)_ |
| `hermes-email` | 平台 | _(同 hermes-cli)_ |
| `hermes-gateway` | 组合 | 所有消息平台工具集的并集 |
| `hermes-homeassistant` | 平台 | _(同 hermes-cli)_ |
| `hermes-matrix` | 平台 | _(同 hermes-cli)_ |
| `hermes-mattermost` | 平台 | _(同 hermes-cli)_ |
| `hermes-signal` | 平台 | _(同 hermes-cli)_ |
| `hermes-slack` | 平台 | _(同 hermes-cli)_ |
| `hermes-sms` | 平台 | _(同 hermes-cli)_ |
| `hermes-telegram` | 平台 | _(同 hermes-cli)_ |
| `hermes-whatsapp` | 平台 | _(同 hermes-cli)_ |
| `homeassistant` | 核心 | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` |
| `honcho` | 核心 | `honcho_conclude`, `honcho_context`, `honcho_profile`, `honcho_search` |
| `image_gen` | 核心 | `image_generate` |
| `memory` | 核心 | `memory` |
| `messaging` | 核心 | `send_message` |
| `moa` | 核心 | `mixture_of_agents` |
| `rl` | 核心 | `rl_check_status`, `rl_edit_config`, `rl_get_current_config`, `rl_get_results`, `rl_list_environments`, `rl_list_runs`, `rl_select_environment`, `rl_start_training`, `rl_stop_training`, `rl_test_inference` |
| `safe` | 组合 | `image_generate`, `mixture_of_agents`, `vision_analyze`, `web_extract`, `web_search` |
| `search` | 核心 | `web_search` |
| `session_search` | 核心 | `session_search` |
| `skills` | 核心 | `skill_manage`, `skill_view`, `skills_list` |
| `terminal` | 核心 | `process`, `terminal` |
| `todo` | 核心 | `todo` |
| `tts` | 核心 | `text_to_speech` |
| `vision` | 核心 | `vision_analyze` |
| `web` | 核心 | `web_extract`, `web_search` |

## 动态工具集

- `mcp-<server>` — 在运行时为每个已配置的 MCP 服务器生成。
- 可以在配置中创建自定义工具集，并在启动时解析。
- 通配符：`all` 和 `*` 会扩展为所有已注册的工具集。