---
sidebar_position: 1
title: "CLI 命令参考"
description: "Hermes 终端命令及命令族的权威参考指南"
---

# CLI 命令参考

本页面涵盖了你在终端中运行的 **终端命令**。

关于聊天中的斜杠命令（slash commands），请参阅 [斜杠命令参考](./slash-commands.md)。

## 全局入口点

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项

| 选项 | 描述 |
|--------|-------------|
| `--version`, `-V` | 显示版本并退出。 |
| `--profile <name>`, `-p <name>` | 选择本次调用要使用的 Hermes 配置文件（profile）。这会覆盖由 `hermes profile use` 设置的默认值。 |
| `--resume <session>`, `-r <session>` | 通过 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近的会话，或恢复标题匹配的最近会话。 |
| `--worktree`, `-w` | 在隔离的 git 工作树中启动，用于并行 Agent 工作流。 |
| `--yolo` | 绕过危险命令的审批提示。 |
| `--pass-session-id` | 在 Agent 的系统提示词中包含会话 ID。 |

## 顶级命令

| 命令 | 用途 |
|---------|---------|
| `hermes chat` | 与 Agent 进行交互式或单次聊天。 |
| `hermes model` | 交互式选择默认的服务商和模型。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes setup` | 交互式设置向导，用于配置全部或部分选项。 |
| `hermes whatsapp` | 配置并配对 WhatsApp 桥接。 |
| `hermes auth` | 管理凭据 —— 添加、列出、移除、重置、设置策略。处理 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已弃用** —— 请改用 `hermes auth`。 |
| `hermes status` | 显示 Agent、认证和平台状态。 |
| `hermes cron` | 检查并触发 cron 调度器。 |
| `hermes webhook` | 管理用于事件驱动激活的动态 webhook 订阅。 |
| `hermes doctor` | 诊断配置和依赖问题。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置技能（skills）。 |
| `hermes honcho` | 管理 Honcho 跨会话记忆集成。 |
| `hermes memory` | 配置外部记忆服务商。 |
| `hermes acp` | 将 Hermes 作为 ACP 服务器运行，用于编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置并将 Hermes 作为 MCP 服务器运行。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、移除）。 |
| `hermes tools` | 按平台配置已启用的工具。 |
| `hermes sessions` | 浏览、导出、清理、重命名和删除会话。 |
| `hermes insights` | 显示 Token/成本/活动分析。 |
| `hermes claw` | OpenClaw 迁移助手。 |
| `hermes profile` | 管理配置文件 —— 多个隔离的 Hermes 实例。 |
| `hermes completion` | 打印终端补全脚本 (bash/zsh)。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖。 |
| `hermes uninstall` | 从系统中移除 Hermes。 |

## `hermes chat`

```bash
hermes chat [options]
```

常用选项：

| 选项 | 描述 |
|--------|-------------|
| `-q`, `--query "..."` | 单次、非交互式提示词。 |
| `-m`, `--model <model>` | 覆盖本次运行的模型。 |
| `-t`, `--toolsets <csv>` | 启用以逗号分隔的一组工具集。 |
| `--provider <provider>` | 强制指定服务商：`auto`, `openrouter`, `nous`, `openai-codex`, `copilot-acp`, `copilot`, `anthropic`, `huggingface`, `zai`, `kimi-coding`, `minimax`, `minimax-cn`, `deepseek`, `ai-gateway`, `opencode-zen`, `opencode-go`, `kilocode`, `alibaba`。 |
| `-s`, `--skills <name>` | 为会话预加载一个或多个技能（可以重复使用该参数或使用逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 程序化模式：隐藏横幅、加载动画和工具预览。 |
| `--resume <session>` / `--continue [name]` | 直接从 `chat` 命令恢复会话。 |
| `--worktree` | 为本次运行创建一个隔离的 git 工作树。 |
| `--checkpoints` | 在执行破坏性文件更改前启用文件系统检查点。 |
| `--yolo` | 跳过审批提示。 |
| `--pass-session-id` | 将会话 ID 传递到系统提示词中。 |
| `--source <tag>` | 用于过滤的会话来源标签（默认：`cli`）。对于不应出现在用户会话列表中的第三方集成，请使用 `tool`。 |
| `--max-turns <N>` | 每一轮对话中工具调用的最大迭代次数（默认：90，或配置中的 `agent.max_turns`）。 |

示例：

```bash
hermes
hermes chat -q "总结最近的 PR"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "仅返回 JSON"
hermes chat --worktree -q "审查此仓库并开启一个 PR"
```

## `hermes model`

交互式服务商和模型选择器。

```bash
hermes model
```

在以下场景使用此命令：
- 切换默认服务商
- 在模型选择期间登录支持 OAuth 的服务商
- 从特定服务商的模型列表中进行挑选
- 配置自定义/自托管端点
- 将新的默认设置保存到配置中

### `/model` 斜杠命令（会话中）

在不离开会话的情况下切换模型：

```
/model                              # 显示当前模型和可用选项
/model claude-sonnet-4              # 切换模型（自动检测服务商）
/model zai:glm-5                    # 切换服务商和模型
/model custom:qwen-2.5              # 使用自定义端点上的模型
/model custom                       # 从自定义端点自动检测模型
/model custom:local:qwen-2.5        # 使用命名的自定义服务商
/model openrouter:anthropic/claude-sonnet-4  # 切换回云端
```

服务商和基础 URL 的更改会自动持久化到 `config.yaml`。当从自定义端点切换走时，过期的基础 URL 会被清除，以防止泄露到其他服务商配置中。

## `hermes gateway`

```bash
hermes gateway <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `run` | 在前台运行网关。 |
| `start` | 启动已安装的网关服务。 |
| `stop` | 停止服务。 |
| `restart` | 重启服务。 |
| `status` | 显示服务状态。 |
| `install` | 作为用户服务安装（Linux 上使用 `systemd`，macOS 上使用 `launchd`）。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |

## `hermes setup`

```bash
hermes setup [model|terminal|gateway|tools|agent] [--non-interactive] [--reset]
```

使用完整向导或直接进入某个部分：

| 部分 | 描述 |
|---------|-------------|
| `model` | 服务商和模型设置。 |
| `terminal` | 终端后端和沙箱设置。 |
| `gateway` | 消息平台设置。 |
| `tools` | 按平台启用/禁用工具。 |
| `agent` | Agent 行为设置。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--non-interactive` | 使用默认值/环境变量，不进行提示。 |
| `--reset` | 在设置前将配置重置为默认值。 |

## `hermes whatsapp`

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

## `hermes login` / `hermes logout` *(已弃用)*

:::caution
`hermes login` 已被移除。请使用 `hermes auth` 管理 OAuth 凭据，使用 `hermes model` 选择服务商，或使用 `hermes setup` 进行完整的交互式设置。
:::

## `hermes auth`

管理凭据池以实现同一服务商的密钥轮换。详见 [凭据池](/user-guide/features/credential-pools) 完整文档。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有凭据池
hermes auth list openrouter                              # 显示特定服务商
hermes auth add openrouter --api-key sk-or-v1-xxx        # 添加 API 密钥
hermes auth add anthropic --type oauth                   # 添加 OAuth 凭据
hermes auth remove openrouter 2                          # 按索引移除
hermes auth reset openrouter                             # 清除冷却时间
```
子命令：`add`、`list`、`remove`、`reset`。如果不带子命令调用，将启动交互式管理向导。

## `hermes status`

```bash
hermes status [--all] [--deep]
```

| 选项 | 描述 |
|--------|-------------|
| `--all` | 以可分享的脱敏格式显示所有详细信息。 |
| `--deep` | 运行可能耗时较长的深度检查。 |

## `hermes cron`

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示已排期的任务。 |
| `create` / `add` | 根据 prompt 创建排期任务，可选通过重复使用 `--skill` 挂载一个或多个 skill。 |
| `edit` | 更新任务的排期、prompt、名称、交付方式、重复次数或挂载的 skill。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务而不删除它。 |
| `resume` | 恢复已暂停的任务并计算其下次运行时间。 |
| `run` | 在下一次调度器 tick 时触发任务。 |
| `remove` | 删除排期任务。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 运行一次到期的任务并退出。 |

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

管理用于事件驱动型 Agent 激活的动态 webhook 订阅。需要在配置中启用 webhook 平台 —— 如果未配置，将打印设置说明。

| 子命令 | 描述 |
|------------|-------------|
| `subscribe` / `add` | 创建 webhook 路由。返回要在你的服务上配置的 URL 和 HMAC 密钥。 |
| `list` / `ls` | 显示所有由 Agent 创建的订阅。 |
| `remove` / `rm` | 删除动态订阅。来自 `config.yaml` 的静态路由不受影响。 |
| `test` | 发送测试 POST 以验证订阅是否正常工作。 |

### `hermes webhook subscribe`

```bash
hermes webhook subscribe <name> [options]
```

| 选项 | 描述 |
|--------|-------------|
| `--prompt` | 带有 `{dot.notation}` payload 引用的 prompt 模板。 |
| `--events` | 要接收的事件类型，以逗号分隔（例如 `issues,pull_request`）。留空表示接收所有。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 为 Agent 运行加载的 skill 名称，以逗号分隔。 |
| `--deliver` | 交付目标：`log`（默认）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台交付的目标聊天/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。如果省略则自动生成。 |

订阅会持久化到 `~/.hermes/webhook_subscriptions.json`，并由 webhook 适配器热加载，无需重启网关。

## `hermes doctor`

```bash
hermes doctor [--fix]
```

| 选项 | 描述 |
|--------|-------------|
| `--fix` | 尝试在可能的情况下进行自动修复。 |

## `hermes config`

```bash
hermes config <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `show` | 显示当前的配置值。 |
| `edit` | 在编辑器中打开 `config.yaml`。 |
| `set <key> <value>` | 设置配置值。 |
| `path` | 打印配置文件路径。 |
| `env-path` | 打印 `.env` 文件路径。 |
| `check` | 检查缺失或过时的配置。 |
| `migrate` | 以交互方式添加新引入的选项。 |

## `hermes pairing`

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示待处理和已批准的用户。 |
| `approve <platform> <code>` | 批准配对码。 |
| `revoke <platform> <user-id>` | 撤销用户的访问权限。 |
| `clear-pending` | 清除待处理的配对码。 |

## `hermes skills`

```bash
hermes skills <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `browse` | 分页浏览 skill 注册表。 |
| `search` | 搜索 skill 注册表。 |
| `install` | 安装一个 skill。 |
| `inspect` | 在不安装的情况下预览 skill。 |
| `list` | 列出已安装的 skill。 |
| `check` | 检查已安装的 hub skill 是否有上游更新。 |
| `update` | 当有可用更新时，重新安装带有上游更改的 hub skill。 |
| `audit` | 重新扫描已安装的 hub skill。 |
| `uninstall` | 移除通过 hub 安装的 skill。 |
| `publish` | 将 skill 发布到注册表。 |
| `snapshot` | 导出/导入 skill 配置。 |
| `tap` | 管理自定义 skill 源。 |
| `config` | 按平台交互式启用/禁用 skill 配置。 |

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

注意：
- `--force` 可以覆盖针对第三方/社区 skill 的非危险策略阻断。
- `--force` 不能覆盖“危险（dangerous）”级别的扫描判定。
- `--source skills-sh` 搜索公开的 `skills.sh` 目录。
- `--source well-known` 允许你将 Hermes 指向暴露了 `/.well-known/skills/index.json` 的站点。

## `hermes honcho`

```bash
hermes honcho [--target-profile NAME] <subcommand>
```

管理 Honcho 跨会话记忆集成。此命令由 Honcho 记忆提供商插件提供，仅当配置中的 `memory.provider` 设置为 `honcho` 时可用。

`--target-profile` 标志允许你在不切换 Profile 的情况下管理另一个 Profile 的 Honcho 配置。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 重定向到 `hermes memory setup`（统一设置路径）。 |
| `status [--all]` | 显示当前的 Honcho 配置和连接状态。`--all` 显示跨 Profile 概览。 |
| `peers` | 显示所有 Profile 的 Peer 身份。 |
| `sessions` | 列出已知的 Honcho 会话映射。 |
| `map [name]` | 将当前目录映射到 Honcho 会话名称。省略 `name` 则列出当前映射。 |
| `peer` | 显示或更新 Peer 名称和辩证推理（dialectic reasoning）级别。选项：`--user NAME`、`--ai NAME`、`--reasoning LEVEL`。 |
| `mode [mode]` | 显示或设置召回模式：`hybrid`、`context` 或 `tools`。省略则显示当前模式。 |
| `tokens` | 显示或设置 context 和 dialectic 的 token 预算。选项：`--context N`、`--dialectic N`。 |
| `identity [file] [--show]` | 播种或显示 AI Peer 的身份表示。 |
| `enable` | 为当前活跃的 Profile 启用 Honcho。 |
| `disable` | 为当前活跃的 Profile 禁用 Honcho。 |
| `sync` | 将 Honcho 配置同步到所有现有 Profile（创建缺失的 host 块）。 |
| `migrate` | 从 openclaw-honcho 到 Hermes Honcho 的逐步迁移指南。 |

## `hermes memory`

```bash
hermes memory <subcommand>
```

设置和管理外部记忆提供商插件。可用提供商：honcho, openviking, mem0, hindsight, holographic, retaindb, byterover, supermemory。同一时间只能激活一个外部提供商。内置记忆（MEMORY.md/USER.md）始终处于激活状态。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式提供商选择与配置。 |
| `status` | 显示当前记忆提供商配置。 |
| `off` | 禁用外部提供商（仅使用内置）。 |

## `hermes acp`

```bash
hermes acp
```

将 Hermes 作为 ACP (Agent Client Protocol) stdio 服务器启动，用于编辑器集成。

相关入口点：

```bash
hermes-acp
python -m acp_adapter
```

请先安装支持库：

```bash
pip install -e '.[acp]'
```

参见 [ACP 编辑器集成](../user-guide/features/acp.md) 和 [ACP 内部原理](../developer-guide/acp-internals.md)。

## `hermes mcp`

```bash
hermes mcp <subcommand>
```

管理 MCP (Model Context Protocol) 服务器配置，并将 Hermes 作为 MCP 服务器运行。

| 子命令 | 描述 |
|------------|-------------|
| `serve [-v\|--verbose]` | 将 Hermes 作为 MCP 服务器运行 —— 向其他 Agent 暴露对话。 |
| `add <name> [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加一个具有自动工具发现功能的 MCP 服务器。 |
| `remove <name>` (别名: `rm`) | 从配置中移除一个 MCP 服务器。 |
| `list` (别名: `ls`) | 列出已配置的 MCP 服务器。 |
| `test <name>` | 测试与 MCP 服务器的连接。 |
| `configure <name>` (别名: `config`) | 切换服务器的工具选择。 |
请参阅 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 以及 [MCP 服务模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins`

```bash
hermes plugins [subcommand]
```

管理 Hermes Agent 插件。在不带子命令的情况下运行 `hermes plugins` 会启动一个交互式的 curses 复选框界面，用于启用/禁用已安装的插件。

| 子命令 | 描述 |
|------------|-------------|
| *(无)* | 交互式切换 UI —— 使用方向键和空格键启用/禁用插件。 |
| `install <identifier> [--force]` | 从 Git URL 或 `owner/repo` 安装插件。 |
| `update <name>` | 拉取已安装插件的最新更改。 |
| `remove <name>` (别名: `rm`, `uninstall`) | 移除已安装的插件。 |
| `enable <name>` | 启用一个已禁用的插件。 |
| `disable <name>` | 禁用一个插件但不移除它。 |
| `list` (别名: `ls`) | 列出已安装的插件及其启用/禁用状态。 |

禁用的插件会存储在 `config.yaml` 的 `plugins.disabled` 下，并在加载时跳过。

请参阅 [Plugins](../user-guide/features/plugins.md) 和 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。

## `hermes tools`

```bash
hermes tools [--summary]
```

| 选项 | 描述 |
|--------|-------------|
| `--summary` | 打印当前已启用工具的摘要并退出。 |

如果不带 `--summary`，该命令将启动交互式的逐平台工具配置 UI。

## `hermes sessions`

```bash
hermes sessions <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出最近的会话。 |
| `browse` | 带有搜索和恢复功能的交互式会话选择器。 |
| `export <output> [--session-id ID]` | 将会话导出为 JSONL。 |
| `delete <session-id>` | 删除单个会话。 |
| `prune` | 删除旧会话。 |
| `stats` | 显示会话存储统计信息。 |
| `rename <session-id> <title>` | 设置或更改会话标题。 |

## `hermes insights`

```bash
hermes insights [--days N] [--source platform]
```

| 选项 | 描述 |
|--------|-------------|
| `--days <n>` | 分析过去 `n` 天的数据（默认值：30）。 |
| `--source <platform>` | 按来源过滤，例如 `cli`、`telegram` 或 `discord`。 |

## `hermes claw`

```bash
hermes claw migrate [options]
```

将你的 OpenClaw 配置迁移到 Hermes。从 `~/.openclaw`（或自定义路径）读取并写入到 `~/.hermes`。自动检测旧版目录名称（`~/.clawdbot`、`~/.moldbot`）和配置文件名（`clawdbot.json`、`moldbot.json`）。

| 选项 | 描述 |
|--------|-------------|
| `--dry-run` | 预览将要迁移的内容而不进行实际写入。 |
| `--preset <name>` | 迁移预设：`full`（默认，包含密钥）或 `user-data`（不含 API 密钥）。 |
| `--overwrite` | 发生冲突时覆盖现有的 Hermes 文件（默认：跳过）。 |
| `--migrate-secrets` | 在迁移中包含 API 密钥（使用 `--preset full` 时默认启用）。 |
| `--source <path>` | 自定义 OpenClaw 目录（默认：`~/.openclaw`）。 |
| `--workspace-target <path>` | 工作区指令（AGENTS.md）的目标目录。 |
| `--skill-conflict <mode>` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

### 迁移内容

迁移涵盖了人格（persona）、记忆、技能、模型提供商、消息平台、Agent 行为、会话策略、MCP 服务器、TTS 等 30 多个类别。条目会被**直接导入**到 Hermes 的对应项中，或者被**归档**以供手动检查。

**直接导入：** SOUL.md、MEMORY.md、USER.md、AGENTS.md、技能（4 个源目录）、默认模型、自定义提供商、MCP 服务器、消息平台令牌和白名单（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、Agent 默认设置（推理力度、压缩、人工延迟、时区、沙箱）、会话重置策略、审批规则、TTS 配置、浏览器设置、工具设置、执行超时、命令白名单、网关配置以及来自 3 个来源的 API 密钥。

**归档供手动检查：** 定时任务（Cron jobs）、插件、钩子/Webhooks、记忆后端（QMD）、技能注册配置、UI/身份、日志、多 Agent 设置、频道绑定、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md。

**API 密钥解析**按优先级检查三个来源：配置值 → `~/.openclaw/.env` → `auth-profiles.json`。所有令牌字段均支持纯字符串、环境变量模板（`${VAR}`）和 SecretRef 对象。

有关完整的配置键映射、SecretRef 处理详情以及迁移后检查清单，请参阅**[完整迁移指南](../guides/migrate-from-openclaw.md)**。

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

管理 Profile —— 多个隔离的 Hermes 实例，每个实例都有自己的配置、会话、技能和主目录。

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出所有 Profile。 |
| `use <name>` | 设置一个固定的默认 Profile。 |
| `create <name> [--clone] [--clone-all] [--clone-from <source>] [--no-alias]` | 创建一个新 Profile。`--clone` 会从当前活动的 Profile 复制配置、`.env` 和 `SOUL.md`。`--clone-all` 会复制所有状态。`--clone-from` 指定源 Profile。 |
| `delete <name> [-y]` | 删除一个 Profile。 |
| `show <name>` | 显示 Profile 详情（主目录、配置等）。 |
| `alias <name> [--remove] [--name NAME]` | 管理用于快速访问 Profile 的包装脚本。 |
| `rename <old> <new>` | 重命名 Profile。 |
| `export <name> [-o FILE]` | 将 Profile 导出为 `.tar.gz` 归档文件。 |
| `import <archive> [--name NAME]` | 从 `.tar.gz` 归档文件导入 Profile。 |

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

将 Shell 补全脚本打印到标准输出。在你的 Shell 配置文件中加载该输出，即可实现 Hermes 命令、子命令和 Profile 名称的 Tab 键补全。

示例：

```bash
# Bash
hermes completion bash >> ~/.bashrc

# Zsh
hermes completion zsh >> ~/.zshrc
```

## 维护命令

| 命令 | 描述 |
|---------|-------------|
| `hermes version` | 打印版本信息。 |
| `hermes update` | 拉取最新更改并重新安装依赖。 |
| `hermes uninstall [--full] [--yes]` | 卸载 Hermes，可选删除所有配置/数据。 |

## 另请参阅

- [斜杠命令参考](./slash-commands.md)
- [CLI 界面](../user-guide/cli.md)
- [会话](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)
