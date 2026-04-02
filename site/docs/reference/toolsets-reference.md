---
sidebar_position: 4
title: "工具集参考"
description: "Hermes 核心、组合、平台和动态工具集的参考文档"
---

# 工具集参考

工具集是具名的工具集合，你可以通过 `hermes chat --toolsets ...` 启用它们，按平台配置，或在 Agent 运行时解析。

| 工具集 | 类型 | 解析为 |
|---------|------|-------------|
| `browser` | core | `browser_back`, `browser_click`, `browser_close`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `web_search` |
| `clarify` | core | `clarify` |
| `code_execution` | core | `execute_code` |
| `cronjob` | core | `cronjob` |
| `debugging` | composite | `patch`, `process`, `read_file`, `search_files`, `terminal`, `web_extract`, `web_search`, `write_file` |
| `delegation` | core | `delegate_task` |
| `file` | core | `patch`, `read_file`, `search_files`, `write_file` |
| `hermes-acp` | platform | `browser_back`, `browser_click`, `browser_close`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `delegate_task`, `execute_code`, `memory`, `patch`, `process`, `read_file`, `search_files`, `session_search`, `skill_manage`, `skill_view`, `skills_list`, `terminal`, `todo`, `vision_analyze`, `web_extract`, `web_search`, `write_file` |
| `hermes-cli` | platform | `browser_back`, `browser_click`, `browser_close`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `clarify`, `cronjob`, `delegate_task`, `execute_code`, `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services`, `honcho_conclude`, `honcho_context`, `honcho_profile`, `honcho_search`, `image_generate`, `memory`, `mixture_of_agents`, `patch`, `process`, `read_file`, `search_files`, `send_message`, `session_search`, `skill_manage`, `skill_view`, `skills_list`, `terminal`, `text_to_speech`, `todo`, `vision_analyze`, `web_extract`, `web_search`, `write_file` |
| `hermes-api-server` | platform | `browser_back`, `browser_click`, `browser_close`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `cronjob`, `delegate_task`, `execute_code`, `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services`, `honcho_conclude`, `honcho_context`, `honcho_profile`, `honcho_search`, `image_generate`, `memory`, `mixture_of_agents`, `patch`, `process`, `read_file`, `search_files`, `session_search`, `skill_manage`, `skill_view`, `skills_list`, `terminal`, `todo`, `vision_analyze`, `web_extract`, `web_search`, `write_file` |
| `hermes-dingtalk` | platform | _(同 hermes-cli)_ |
| `hermes-feishu` | platform | _(同 hermes-cli)_ |
| `hermes-wecom` | platform | _(同 hermes-cli)_ |
| `hermes-discord` | platform | _(同 hermes-cli)_ |
| `hermes-email` | platform | _(同 hermes-cli)_ |
| `hermes-gateway` | composite | 所有消息平台工具集的集合 |
| `hermes-homeassistant` | platform | _(同 hermes-cli)_ |
| `hermes-matrix` | platform | _(同 hermes-cli)_ |
| `hermes-mattermost` | platform | _(同 hermes-cli)_ |
| `hermes-signal` | platform | _(同 hermes-cli)_ |
| `hermes-slack` | platform | _(同 hermes-cli)_ |
| `hermes-sms` | platform | _(同 hermes-cli)_ |
| `hermes-telegram` | platform | _(同 hermes-cli)_ |
| `hermes-whatsapp` | platform | _(同 hermes-cli)_ |
| `homeassistant` | core | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` |
| `honcho` | core | `honcho_conclude`, `honcho_context`, `honcho_profile`, `honcho_search` |
| `image_gen` | core | `image_generate` |
| `memory` | core | `memory` |
| `messaging` | core | `send_message` |
| `moa` | core | `mixture_of_agents` |
| `rl` | core | `rl_check_status`, `rl_edit_config`, `rl_get_current_config`, `rl_get_results`, `rl_list_environments`, `rl_list_runs`, `rl_select_environment`, `rl_start_training`, `rl_stop_training`, `rl_test_inference` |
| `safe` | composite | `image_generate`, `mixture_of_agents`, `vision_analyze`, `web_extract`, `web_search` |
| `search` | core | `web_search` |
| `session_search` | core | `session_search` |
| `skills` | core | `skill_manage`, `skill_view`, `skills_list` |
| `terminal` | core | `process`, `terminal` |
| `todo` | core | `todo` |
| `tts` | core | `text_to_speech` |
| `vision` | core | `vision_analyze` |
| `web` | core | `web_extract`, `web_search` |

## 动态工具集

- `mcp-<server>` — 运行时为每个配置的 MCP 服务器生成。
- 自定义工具集可在配置中创建，并在启动时解析。
- 通配符：`all` 和 `*` 扩展为所有已注册的工具集。