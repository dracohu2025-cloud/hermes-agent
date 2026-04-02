---
sidebar_position: 1
title: "CLI 命令参考"
description: "Hermes 终端命令及命令族的权威参考"
---

# CLI 命令参考

本页介绍你在 shell 中运行的**终端命令**。

有关聊天内的斜杠命令，请参见 [斜杠命令参考](./slash-commands.md)。

## 全局入口

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项

| 选项 | 说明 |
|--------|-------------|
| `--version`, `-V` | 显示版本并退出。 |
| `--profile <name>`, `-p <name>` | 选择本次调用使用的 Hermes 配置文件。会覆盖通过 `hermes profile use` 设置的默认配置。 |
| `--resume <session>`, `-r <session>` | 通过 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近的会话，或匹配标题的最近会话。 |
| `--worktree`, `-w` | 在隔离的 git worktree 中启动，用于并行 Agent 工作流。 |
| `--yolo` | 跳过危险命令的确认提示。 |
| `--pass-session-id` | 在 Agent 的系统提示中包含会话 ID。 |

## 顶层命令

| 命令 | 作用 |
|---------|---------|
| `hermes chat` | 与 Agent 进行交互式或一次性聊天。 |
| `hermes model` | 交互式选择默认提供商和模型。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes setup` | 交互式设置向导，配置全部或部分内容。 |
| `hermes whatsapp` | 配置并配对 WhatsApp 桥接。 |
| `hermes login` / `logout` | 使用 OAuth 支持的提供商进行身份验证。 |
| `hermes auth` | 管理凭证池 — 添加、列出、移除、重置、设置策略。 |
| `hermes status` | 显示 Agent、认证和平台状态。 |
| `hermes cron` | 检查和触发定时任务调度器。 |
| `hermes webhook` | 管理动态 webhook 订阅，实现事件驱动激活。 |
| `hermes doctor` | 诊断配置和依赖问题。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 审批或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置技能。 |
| `hermes honcho` | 管理 Honcho 跨会话记忆集成。 |
| `hermes acp` | 以 ACP 服务器模式运行 Hermes，支持编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置并以 MCP 服务器模式运行 Hermes。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、移除）。 |
| `hermes tools` | 配置各平台启用的工具。 |
| `hermes sessions` | 浏览、导出、清理、重命名和删除会话。 |
| `hermes insights` | 显示令牌/成本/活动分析。 |
| `hermes claw` | OpenClaw 迁移辅助工具。 |
| `hermes profile` | 管理配置文件 — 多个隔离的 Hermes 实例。 |
| `hermes completion` | 打印 shell 补全脚本（bash/zsh）。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖。 |
| `hermes uninstall` | 从系统中移除 Hermes。 |

## `hermes chat`

```bash
hermes chat [options]
```

常用选项：

| 选项 | 说明 |
|--------|-------------|
| `-q`, `--query "..."` | 一次性非交互式提示。 |
| `-m`, `--model <model>` | 覆盖本次运行使用的模型。 |
| `-t`, `--toolsets <csv>` | 启用逗号分隔的工具集。 |
| `--provider <provider>` | 强制指定提供商：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot-acp`、`copilot`、`anthropic`、`huggingface`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`、`kilocode`。 |
| `-s`, `--skills <name>` | 预加载一个或多个技能（可重复或逗号分隔）。 |
| `-v`, `--verbose` | 输出详细信息。 |
| `-Q`, `--quiet` | 程序化模式：抑制横幅/加载动画/工具预览。 |
| `--resume <session>` / `--continue [name]` | 直接从 `chat` 恢复会话。 |
| `--worktree` | 为本次运行创建隔离的 git worktree。 |
| `--checkpoints` | 在破坏性文件更改前启用文件系统检查点。 |
| `--yolo` | 跳过确认提示。 |
| `--pass-session-id` | 将会话 ID 传入系统提示。 |
| `--source <tag>` | 会话来源标签，用于过滤（默认：`cli`）。第三方集成请用 `tool`，避免出现在用户会话列表中。 |

示例：

```bash
hermes
hermes chat -q "总结最新的 PR"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "只返回 JSON"
hermes chat --worktree -q "审查此仓库并打开 PR"
```

## `hermes model`

交互式提供商 + 模型选择器。

```bash
hermes model
```

适用于你想要：
- 切换默认提供商
- 在模型选择时登录 OAuth 支持的提供商
- 从提供商特定的模型列表中选择
- 配置自定义/自托管端点
- 将新默认保存到配置中

### `/model` 斜杠命令（会话中途）

无需离开会话即可切换模型：

```
/model                              # 显示当前模型和可用选项
/model claude-sonnet-4              # 切换模型（自动检测提供商）
/model zai:glm-5                    # 切换提供商和模型
/model custom:qwen-2.5              # 使用自定义端点上的模型
/model custom                       # 从自定义端点自动检测模型
/model custom:local:qwen-2.5        # 使用命名的自定义提供商
/model openrouter:anthropic/claude-sonnet-4  # 切换回云端
```

提供商和基础 URL 的更改会自动保存到 `config.yaml`。切换离开自定义端点时，会清除过时的基础 URL，防止泄漏到其他提供商。

## `hermes gateway`

```bash
hermes gateway <subcommand>
```

子命令：

| 子命令 | 说明 |
|------------|-------------|
| `run` | 在前台运行网关。 |
| `start` | 启动已安装的网关服务。 |
| `stop` | 停止服务。 |
| `restart` | 重启服务。 |
| `status` | 显示服务状态。 |
| `install` | 安装为用户服务（Linux 上为 `systemd`，macOS 上为 `launchd`）。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |

## `hermes setup`

```bash
hermes setup [model|terminal|gateway|tools|agent] [--non-interactive] [--reset]
```

使用完整向导或直接进入某个部分：

| 部分 | 说明 |
|---------|-------------|
| `model` | 提供商和模型设置。 |
| `terminal` | 终端后端和沙箱设置。 |
| `gateway` | 消息平台设置。 |
| `tools` | 启用/禁用各平台工具。 |
| `agent` | Agent 行为设置。 |

选项：

| 选项 | 说明 |
|--------|-------------|
| `--non-interactive` | 使用默认值/环境变量，无需提示。 |
| `--reset` | 在设置前重置配置为默认。 |

## `hermes whatsapp`

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

## `hermes login` / `hermes logout`

```bash
hermes login [--provider nous|openai-codex] [--portal-url ...] [--inference-url ...]
hermes logout [--provider nous|openai-codex]
```

`login` 支持：
- Nous Portal OAuth/设备流程
- OpenAI Codex OAuth/设备流程

`login` 的常用选项：
- `--no-browser`
- `--timeout <seconds>`
- `--ca-bundle <pem>`
- `--insecure`

## `hermes auth`

管理同一提供商的凭证池以实现密钥轮换。完整文档见 [Credential Pools](/user-guide/features/credential-pools)。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有凭证池
hermes auth list openrouter                              # 显示指定提供商
hermes auth add openrouter --api-key sk-or-v1-xxx        # 添加 API 密钥
hermes auth add anthropic --type oauth                   # 添加 OAuth 凭证
hermes auth remove openrouter 2                          # 按索引移除
hermes auth reset openrouter                             # 清除冷却时间
```

子命令：`add`、`list`、`remove`、`reset`。无子命令时启动交互式管理向导。
## `hermes status`

```bash
hermes status [--all] [--deep]
```

| 选项 | 说明 |
|--------|-------------|
| `--all` | 以可分享的脱敏格式显示所有详情。 |
| `--deep` | 运行更深入的检查，可能需要更长时间。 |

## `hermes cron`

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 说明 |
|------------|-------------|
| `list` | 显示计划任务。 |
| `create` / `add` | 从提示创建计划任务，可通过重复使用 `--skill` 附加一个或多个技能。 |
| `edit` | 更新任务的计划、提示、名称、交付方式、重复次数或附加技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务但不删除。 |
| `resume` | 恢复暂停的任务并计算下一次运行时间。 |
| `run` | 触发任务在下一个调度器时刻执行。 |
| `remove` | 删除计划任务。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 运行到期任务一次后退出。 |

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

管理动态 webhook 订阅，用于事件驱动的 Agent 激活。需要在配置中启用 webhook 平台——如果未配置，会打印设置说明。

| 子命令 | 说明 |
|------------|-------------|
| `subscribe` / `add` | 创建 webhook 路由。返回用于配置服务的 URL 和 HMAC 密钥。 |
| `list` / `ls` | 显示所有 Agent 创建的订阅。 |
| `remove` / `rm` | 删除动态订阅。不会影响 config.yaml 中的静态路由。 |
| `test` | 发送测试 POST 请求以验证订阅是否正常。 |

### `hermes webhook subscribe`

```bash
hermes webhook subscribe <name> [options]
```

| 选项 | 说明 |
|--------|-------------|
| `--prompt` | 带有 `{dot.notation}` 负载引用的提示模板。 |
| `--events` | 逗号分隔的事件类型列表（例如 `issues,pull_request`）。为空表示全部。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 逗号分隔的技能名称，用于 Agent 运行时加载。 |
| `--deliver` | 交付目标：`log`（默认）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台交付的目标聊天/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。省略时自动生成。 |

订阅信息会保存在 `~/.hermes/webhook_subscriptions.json`，webhook 适配器会热加载，无需重启网关。

## `hermes doctor`

```bash
hermes doctor [--fix]
```

| 选项 | 说明 |
|--------|-------------|
| `--fix` | 尽可能尝试自动修复。 |

## `hermes config`

```bash
hermes config <subcommand>
```

子命令：

| 子命令 | 说明 |
|------------|-------------|
| `show` | 显示当前配置值。 |
| `edit` | 在编辑器中打开 `config.yaml`。 |
| `set <key> <value>` | 设置配置项。 |
| `path` | 打印配置文件路径。 |
| `env-path` | 打印 `.env` 文件路径。 |
| `check` | 检查缺失或过期的配置。 |
| `migrate` | 交互式添加新引入的配置选项。 |

## `hermes pairing`

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 说明 |
|------------|-------------|
| `list` | 显示待处理和已批准的用户。 |
| `approve <platform> <code>` | 批准配对码。 |
| `revoke <platform> <user-id>` | 撤销用户访问权限。 |
| `clear-pending` | 清除待处理的配对码。 |

## `hermes skills`

```bash
hermes skills <subcommand>
```

子命令：

| 子命令 | 说明 |
|------------|-------------|
| `browse` | 分页浏览技能注册表。 |
| `search` | 搜索技能注册表。 |
| `install` | 安装技能。 |
| `inspect` | 预览技能，无需安装。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 hub 技能是否有上游更新。 |
| `update` | 当有上游更新时，重新安装 hub 技能。 |
| `audit` | 重新扫描已安装的 hub 技能。 |
| `uninstall` | 移除 hub 安装的技能。 |
| `publish` | 发布技能到注册表。 |
| `snapshot` | 导出/导入技能配置。 |
| `tap` | 管理自定义技能源。 |
| `config` | 交互式按平台启用/禁用技能配置。 |

常用示例：

```bash
hermes skills browse
hermes skills browse --source official
hermes skills search react --source skills-sh
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect official/security/1password
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install official/migration/openclaw-migration
hermes skills install skills-sh/anthropics/skills/pdf --force
hermes skills check
hermes skills update
hermes skills config
```

注意事项：
- `--force` 可以覆盖非危险策略阻止的第三方/社区技能安装。
- `--force` 不会覆盖被判定为 `dangerous` 的扫描结果。
- `--source skills-sh` 搜索公共的 `skills.sh` 目录。
- `--source well-known` 允许你指定一个暴露 `/.well-known/skills/index.json` 的站点给 Hermes 使用。

## `hermes honcho`

```bash
hermes honcho <subcommand>
```

子命令：

| 子命令 | 说明 |
|------------|-------------|
| `setup` | 交互式 Honcho 设置向导。 |
| `status` | 显示当前 Honcho 配置和连接状态。 |
| `sessions` | 列出已知的 Honcho 会话映射。 |
| `map` | 将当前目录映射到 Honcho 会话名称。 |
| `peer` | 显示或更新对等名称和辩证推理级别。 |
| `mode` | 显示或设置内存模式：`hybrid`、`honcho` 或 `local`。 |
| `tokens` | 显示或设置上下文和辩证推理的令牌预算。 |
| `identity` | 生成或显示 AI 对等身份表示。 |
| `migrate` | 从 openclaw-honcho 迁移到 Hermes Honcho 的指南。 |

## `hermes acp`

```bash
hermes acp
```

以 ACP（Agent Client Protocol）stdio 服务器模式启动 Hermes，用于编辑器集成。

相关入口：

```bash
hermes-acp
python -m acp_adapter
```

先安装支持：

```bash
pip install -e '.[acp]'
```

详见 [ACP 编辑器集成](../user-guide/features/acp.md) 和 [ACP 内部机制](../developer-guide/acp-internals.md)。

## `hermes mcp`

```bash
hermes mcp <subcommand>
```

管理 MCP（Model Context Protocol）服务器配置，并以 MCP 服务器模式运行 Hermes。

| 子命令 | 说明 |
|------------|-------------|
| `serve [-v\|--verbose]` | 以 MCP 服务器模式运行 Hermes——向其他 Agents 暴露对话。 |
| `add <name> [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加 MCP 服务器，支持自动工具发现。 |
| `remove <name>`（别名：`rm`） | 从配置中移除 MCP 服务器。 |
| `list`（别名：`ls`） | 列出已配置的 MCP 服务器。 |
| `test <name>` | 测试与 MCP 服务器的连接。 |
| `configure <name>`（别名：`config`） | 切换服务器的工具选择。 |

详见 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 和 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins`

```bash
hermes plugins [subcommand]
```

管理 Hermes Agent 插件。无子命令时运行交互式 curses 列表界面，可启用/禁用已安装插件。

| 子命令 | 说明 |
|------------|-------------|
| *(无)* | 交互式切换界面——用方向键和空格键启用/禁用插件。 |
| `install <identifier> [--force]` | 从 Git URL 或 `owner/repo` 安装插件。 |
| `update <name>` | 拉取已安装插件的最新更新。 |
| `remove <name>`（别名：`rm`、`uninstall`） | 移除已安装插件。 |
| `enable <name>` | 启用已禁用的插件。 |
| `disable <name>` | 禁用插件但不移除。 |
| `list`（别名：`ls`） | 列出已安装插件及其启用/禁用状态。 |

禁用的插件会存储在 `config.yaml` 的 `plugins.disabled` 下，加载时会跳过。

详见 [插件](../user-guide/features/plugins.md) 和 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。
## `hermes tools`

```bash
hermes tools [--summary]
```

| 选项 | 说明 |
|--------|-------------|
| `--summary` | 打印当前启用的工具摘要并退出。 |

不带 `--summary` 时，会启动交互式的按平台工具配置界面。

## `hermes sessions`

```bash
hermes sessions <subcommand>
```

子命令：

| 子命令 | 说明 |
|------------|-------------|
| `list` | 列出最近的会话。 |
| `browse` | 交互式会话选择器，支持搜索和恢复。 |
| `export <output> [--session-id ID]` | 导出会话为 JSONL 格式。 |
| `delete <session-id>` | 删除一个会话。 |
| `prune` | 删除旧会话。 |
| `stats` | 显示会话存储统计信息。 |
| `rename <session-id> <title>` | 设置或更改会话标题。 |

## `hermes insights`

```bash
hermes insights [--days N] [--source platform]
```

| 选项 | 说明 |
|--------|-------------|
| `--days <n>` | 分析最近 `n` 天的数据（默认：30 天）。 |
| `--source <platform>` | 按来源过滤，如 `cli`、`telegram` 或 `discord`。 |

## `hermes claw`

```bash
hermes claw migrate [options]
```

将你的 OpenClaw 配置迁移到 Hermes。读取 `~/.openclaw`（或自定义路径），写入 `~/.hermes`。自动检测旧版目录名（`~/.clawdbot`、`~/.moldbot`）和配置文件名（`clawdbot.json`、`moldbot.json`）。

| 选项 | 说明 |
|--------|-------------|
| `--dry-run` | 预览将要迁移的内容，但不写入任何文件。 |
| `--preset <name>` | 迁移预设：`full`（默认，包含密钥）或 `user-data`（不包含 API 密钥）。 |
| `--overwrite` | 遇到冲突时覆盖已有的 Hermes 文件（默认跳过）。 |
| `--migrate-secrets` | 迁移时包含 API 密钥（`--preset full` 默认启用）。 |
| `--source <path>` | 自定义 OpenClaw 目录（默认：`~/.openclaw`）。 |
| `--workspace-target <path>` | 工作区指令目标目录（AGENTS.md）。 |
| `--skill-conflict <mode>` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

### 迁移内容

迁移涵盖 30 多个类别，包括角色、记忆、技能、模型提供商、消息平台、Agent 行为、会话策略、MCP 服务器、TTS 等。项目要么**直接导入**到 Hermes 对应项，要么**归档**以供手动检查。

**直接导入：** SOUL.md、MEMORY.md、USER.md、AGENTS.md、技能（4 个源目录）、默认模型、自定义提供商、MCP 服务器、消息平台令牌和白名单（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、Agent 默认设置（推理努力、压缩、人类延迟、时区、沙箱）、会话重置策略、审批规则、TTS 配置、浏览器设置、工具设置、执行超时、命令白名单、网关配置，以及来自 3 个来源的 API 密钥。

**归档以供手动检查：** 定时任务、插件、钩子/网络钩子、记忆后端（QMD）、技能注册配置、UI/身份、日志、多 Agent 设置、频道绑定、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md。

**API 密钥解析** 按优先级检查三个来源：配置值 → `~/.openclaw/.env` → `auth-profiles.json`。所有令牌字段支持纯字符串、环境变量模板（`${VAR}`）和 SecretRef 对象。

完整的配置键映射、SecretRef 处理细节和迁移后检查清单，请参见 **[完整迁移指南](../guides/migrate-from-openclaw.md)**。

### 示例

```bash
# 预览将要迁移的内容
hermes claw migrate --dry-run

# 完整迁移，包括 API 密钥
hermes claw migrate --preset full

# 仅迁移用户数据（不含密钥），覆盖冲突
hermes claw migrate --preset user-data --overwrite

# 从自定义 OpenClaw 路径迁移
hermes claw migrate --source /home/user/old-openclaw
```

## `hermes profile`

```bash
hermes profile <subcommand>
```

管理配置文件 —— 多个独立的 Hermes 实例，每个实例有自己的配置、会话、技能和主目录。

| 子命令 | 说明 |
|------------|-------------|
| `list` | 列出所有配置文件。 |
| `use <name>` | 设置默认的固定配置文件。 |
| `create <name> [--clone] [--no-alias]` | 创建新配置文件。`--clone` 会复制当前激活配置文件的配置、`.env` 和 `SOUL.md`。 |
| `delete <name> [-y]` | 删除配置文件。 |
| `show <name>` | 显示配置文件详情（主目录、配置等）。 |
| `alias <name> [--remove] [--name NAME]` | 管理快速访问配置文件的包装脚本。 |
| `rename <old> <new>` | 重命名配置文件。 |
| `export <name> [-o FILE]` | 导出配置文件为 `.tar.gz` 归档。 |
| `import <archive> [--name NAME]` | 从 `.tar.gz` 归档导入配置文件。 |

示例：

```bash
hermes profile list
hermes profile create work --clone
hermes profile use work
hermes profile alias work --name h-work
hermes profile export work -o work-backup.tar.gz
hermes profile import work-backup.tar.gz --name restored
hermes -p work chat -q "Hello from work profile"
```

## `hermes completion`

```bash
hermes completion [bash|zsh]
```

打印 shell 补全脚本到标准输出。在你的 shell 配置文件中引用该输出，即可实现 Hermes 命令、子命令和配置文件名的 Tab 补全。

示例：

```bash
# Bash
hermes completion bash >> ~/.bashrc

# Zsh
hermes completion zsh >> ~/.zshrc
```

## 维护命令

| 命令 | 说明 |
|---------|-------------|
| `hermes version` | 打印版本信息。 |
| `hermes update` | 拉取最新更新并重新安装依赖。 |
| `hermes uninstall [--full] [--yes]` | 卸载 Hermes，可选择删除所有配置和数据。 |

## 参见

- [Slash Commands Reference](./slash-commands.md)
- [CLI Interface](../user-guide/cli.md)
- [Sessions](../user-guide/sessions.md)
- [Skills System](../user-guide/features/skills.md)
- [Skins & Themes](../user-guide/features/skins.md)
