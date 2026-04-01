---
sidebar_position: 1
title: "CLI 命令参考"
description: "Hermes 终端命令及命令族的权威参考"
---

# CLI 命令参考

本页涵盖从你的 shell 中运行的**终端命令**。

关于聊天中的斜杠命令，请参阅[斜杠命令参考](./slash-commands.md)。

## 全局入口点

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项

| 选项 | 描述 |
|--------|-------------|
| `--version`, `-V` | 显示版本信息并退出。 |
| `--resume <session>`, `-r <session>` | 通过 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近的会话，或恢复标题匹配的最近会话。 |
| `--worktree`, `-w` | 在隔离的 git 工作树中启动，用于并行 Agent 工作流。 |
| `--yolo` | 绕过危险命令的确认提示。 |
| `--pass-session-id` | 在 Agent 的系统提示中包含会话 ID。 |

## 顶级命令

| 命令 | 用途 |
|---------|---------|
| `hermes chat` | 与 Agent 进行交互式或一次性聊天。 |
| `hermes model` | 交互式选择默认的提供商和模型。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes setup` | 针对全部或部分配置的交互式设置向导。 |
| `hermes whatsapp` | 配置和配对 WhatsApp 桥接。 |
| `hermes login` / `logout` | 使用 OAuth 支持的提供商进行身份验证。 |
| `hermes status` | 显示 Agent、认证和平台状态。 |
| `hermes cron` | 检查并触发 cron 调度器。 |
| `hermes webhook` | 管理用于事件驱动激活的动态 webhook 订阅。 |
| `hermes doctor` | 诊断配置和依赖项问题。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置技能。 |
| `hermes honcho` | 管理 Honcho 跨会话记忆集成。 |
| `hermes acp` | 将 Hermes 作为 ACP 服务器运行，用于编辑器集成。 |
| `hermes tools` | 按平台配置启用的工具。 |
| `hermes sessions` | 浏览、导出、清理、重命名和删除会话。 |
| `hermes insights` | 显示令牌/成本/活动分析。 |
| `hermes claw` | OpenClaw 迁移助手。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖项。 |
| `hermes uninstall` | 从系统中移除 Hermes。 |

## `hermes chat`

```bash
hermes chat [options]
```

常用选项：

| 选项 | 描述 |
|--------|-------------|
| `-q`, `--query "..."` | 一次性、非交互式提示。 |
| `-m`, `--model <model>` | 为此运行覆盖模型。 |
| `-t`, `--toolsets <csv>` | 启用一个逗号分隔的工具集集合。 |
| `--provider <provider>` | 强制指定提供商：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`huggingface`、`alibaba`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`、`kilocode`。 |
| `-s`, `--skills <name>` | 为会话预加载一个或多个技能（可重复使用或逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 编程模式：抑制横幅/旋转器/工具预览。 |
| `--resume <session>` / `--continue [name]` | 直接从 `chat` 恢复会话。 |
| `--worktree` | 为此运行创建一个隔离的 git 工作树。 |
| `--checkpoints` | 在破坏性文件更改前启用文件系统检查点。 |
| `--yolo` | 跳过确认提示。 |
| `--pass-session-id` | 将会话 ID 传递到系统提示中。 |

示例：

```bash
hermes
hermes chat -q "Summarize the latest PRs"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "Return only JSON"
hermes chat --worktree -q "Review this repo and open a PR"
```

## `hermes model`

交互式提供商 + 模型选择器。

```bash
hermes model
```

在以下情况时使用此命令：
- 切换默认提供商
- 在模型选择期间登录 OAuth 支持的提供商
- 从提供商特定的模型列表中选择
- 配置自定义/自托管端点
- 将新的默认设置保存到配置中

### `/model` 斜杠命令（会话中）

无需离开会话即可切换模型：

```
/model                              # 显示当前模型和可用选项
/model claude-sonnet-4              # 切换模型（自动检测提供商）
/model zai:glm-5                    # 切换提供商和模型
/model custom:qwen-2.5              # 在你的自定义端点上使用模型
/model custom                       # 从自定义端点自动检测模型
/model custom:local:qwen-2.5        # 使用一个命名的自定义提供商
/model openrouter:anthropic/claude-sonnet-4  # 切换回云端
```

提供商和基础 URL 的更改会自动持久化到 `config.yaml`。当从自定义端点切换走时，过时的基础 URL 会被清除，以防止其泄漏到其他提供商。

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
| `install` | 安装为用户服务（Linux 上为 `systemd`，macOS 上为 `launchd`）。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |

## `hermes setup`

```bash
hermes setup [model|terminal|gateway|tools|agent] [--non-interactive] [--reset]
```

使用完整向导或跳转到某个部分：

| 部分 | 描述 |
|---------|-------------|
| `model` | 提供商和模型设置。 |
| `terminal` | 终端后端和沙箱设置。 |
| `gateway` | 消息平台设置。 |
| `tools` | 按平台启用/禁用工具。 |
| `agent` | Agent 行为设置。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--non-interactive` | 使用默认值/环境变量，无需提示。 |
| `--reset` | 在设置前将配置重置为默认值。 |

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

`login` 的有用选项：
- `--no-browser`
- `--timeout <seconds>`
- `--ca-bundle <pem>`
- `--insecure`

## `hermes status`

```bash
hermes status [--all] [--deep]
```

| 选项 | 描述 |
|--------|-------------|
| `--all` | 以可共享的脱敏格式显示所有详细信息。 |
| `--deep` | 运行可能需要更长时间的深度检查。 |

## `hermes cron`

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示已调度的作业。 |
| `create` / `add` | 根据提示创建调度作业，可选地通过重复的 `--skill` 附加一个或多个技能。 |
| `edit` | 更新作业的调度、提示、名称、交付方式、重复次数或附加的技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停作业而不删除它。 |
| `resume` | 恢复暂停的作业并计算其下一次未来运行时间。 |
| `run` | 在调度器下一次触发时运行作业。 |
| `remove` | 删除已调度的作业。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 运行到期的作业一次并退出。 |

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

管理用于事件驱动 Agent 激活的动态 webhook 订阅。需要在配置中启用 webhook 平台——如果未配置，则打印设置说明。

| 子命令 | 描述 |
|------------|-------------|
| `subscribe` / `add` | 创建 webhook 路由。返回 URL 和 HMAC 密钥，以便在你的服务上配置。 |
| `list` / `ls` | 显示所有 Agent 创建的订阅。 |
| `remove` / `rm` | 删除动态订阅。来自 config.yaml 的静态路由不受影响。 |
| `test` | 发送测试 POST 请求以验证订阅是否正常工作。 |

### `hermes webhook subscribe`

```bash
hermes webhook subscribe <name> [options]
```

| 选项 | 描述 |
|--------|-------------|
| `--prompt` | 提示模板，包含 `{dot.notation}` 负载引用。 |
| `--events` | 要接受的逗号分隔的事件类型（例如 `issues,pull_request`）。空 = 全部。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 为 Agent 运行加载的逗号分隔的技能名称。 |
| `--deliver` | 交付目标：`log`（默认）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台交付的目标聊天/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。如果省略则自动生成。 |

订阅持久化到 `~/.hermes/webhook_subscriptions.json`，并由 webhook 适配器热重载，无需重启网关。

## `hermes doctor`

```bash
hermes doctor [--fix]
```

| 选项 | 描述 |
|--------|-------------|
| `--fix` | 在可能的情况下尝试自动修复。 |

## `hermes config`

```bash
hermes config <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `show` | 显示当前配置值。 |
| `edit` | 在你的编辑器中打开 `config.yaml`。 |
| `set <key> <value>` | 设置配置值。 |
| `path` | 打印配置文件路径。 |
| `env-path` | 打印 `.env` 文件路径。 |
| `check` | 检查缺失或过时的配置。 |
| `migrate` | 交互式添加新引入的选项。 |

## `hermes pairing`

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示待处理和已批准的用户。 |
| `approve <platform> <code>` | 批准一个配对码。 |
| `revoke <platform> <user-id>` | 撤销用户的访问权限。 |
| `clear-pending` | 清除待处理的配对码。 |

## `hermes skills`

```bash
hermes skills <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `browse` | 技能注册表的分页浏览器。 |
| `search` | 搜索技能注册表。 |
| `install` | 安装一个技能。 |
| `inspect` | 预览技能而不安装它。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 hub 技能是否有上游更新。 |
| `update` | 在有可用更新时，重新安装有上游更改的 hub 技能。 |
| `audit` | 重新扫描已安装的 hub 技能。 |
| `uninstall` | 移除一个 hub 安装的技能。 |
| `publish` | 将技能发布到注册表。 |
| `snapshot` | 导出/导入技能配置。 |
| `tap` | 管理自定义技能源。 |
| `config` | 按平台交互式启用/禁用技能配置。 |

常见示例：

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
- `--force` 可以覆盖第三方/社区技能的非危险策略阻止。
- `--force` 不会覆盖 `dangerous` 扫描结果。
- `--source skills-sh` 搜索公共的 `skills.sh` 目录。
- `--source well-known` 允许你将 Hermes 指向暴露 `/.well-known/skills/index.json` 的站点。

## `hermes honcho`

```bash
hermes honcho <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式 Honcho 设置向导。 |
| `status` | 显示当前 Honcho 配置和连接状态。 |
| `sessions` | 列出已知的 Honcho 会话映射。 |
| `map` | 将当前目录映射到 Honcho 会话名称。 |
| `peer` | 显示或更新对等体名称和辩证推理级别。 |
| `mode` | 显示或设置记忆模式：`hybrid`、`honcho` 或 `local`。 |
| `tokens` | 显示或设置上下文和辩证推理的令牌预算。 |
| `identity` | 植入或显示 AI 对等体身份表示。 |
| `migrate` | 从 openclaw-honcho 迁移到 Hermes Honcho 的指南。 |
## `hermes acp`

```bash
hermes acp
```

以 ACP（Agent Client Protocol）标准输入输出服务器模式启动 Hermes，用于编辑器集成。

相关入口点：

```bash
hermes-acp
python -m acp_adapter
```

请先安装支持：

```bash
pip install -e '.[acp]'
```

参见 [ACP 编辑器集成](../user-guide/features/acp.md) 和 [ACP 内部原理](../developer-guide/acp-internals.md)。

## `hermes mcp`

```bash
hermes mcp <子命令>
```

管理 MCP（Model Context Protocol）服务器配置，并以 MCP 服务器模式运行 Hermes。

| 子命令 | 描述 |
|------------|-------------|
| `serve [-v\|--verbose]` | 以 MCP 服务器模式运行 Hermes —— 将会话暴露给其他智能体。 |
| `add <名称> [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加一个 MCP 服务器，并自动发现工具。 |
| `remove <名称>` (别名：`rm`) | 从配置中移除一个 MCP 服务器。 |
| `list` (别名：`ls`) | 列出已配置的 MCP 服务器。 |
| `test <名称>` | 测试与 MCP 服务器的连接。 |
| `configure <名称>` (别名：`config`) | 切换服务器的工具选择。 |

参见 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 和 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins`

```bash
hermes plugins [子命令]
```

管理 Hermes Agent 插件。不带子命令运行 `hermes plugins` 会启动一个交互式的 curses 复选框界面来启用/禁用已安装的插件。

| 子命令 | 描述 |
|------------|-------------|
| *(无)* | 交互式切换界面 —— 使用方向键和空格键启用/禁用插件。 |
| `install <标识符> [--force]` | 从 Git URL 或 `owner/repo` 安装插件。 |
| `update <名称>` | 为已安装的插件拉取最新更改。 |
| `remove <名称>` (别名：`rm`, `uninstall`) | 移除已安装的插件。 |
| `enable <名称>` | 启用一个已禁用的插件。 |
| `disable <名称>` | 禁用一个插件但不移除它。 |
| `list` (别名：`ls`) | 列出已安装的插件及其启用/禁用状态。 |

已禁用的插件存储在 `config.yaml` 的 `plugins.disabled` 下，并在加载时跳过。

参见 [插件](../user-guide/features/plugins.md) 和 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。

## `hermes tools`

```bash
hermes tools [--summary]
```

| 选项 | 描述 |
|--------|-------------|
| `--summary` | 打印当前已启用工具的摘要并退出。 |

不带 `--summary` 选项时，此命令会启动针对当前平台的交互式工具配置界面。

## `hermes sessions`

```bash
hermes sessions <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出最近的会话。 |
| `browse` | 交互式会话选择器，支持搜索和恢复。 |
| `export <输出路径> [--session-id ID]` | 将会话导出为 JSONL 格式。 |
| `delete <会话ID>` | 删除一个会话。 |
| `prune` | 删除旧的会话。 |
| `stats` | 显示会话存储的统计信息。 |
| `rename <会话ID> <标题>` | 设置或更改会话标题。 |

## `hermes insights`

```bash
hermes insights [--days N] [--source 平台]
```

| 选项 | 描述 |
|--------|-------------|
| `--days <n>` | 分析最近 `n` 天的数据（默认：30）。 |
| `--source <平台>` | 按来源过滤，例如 `cli`、`telegram` 或 `discord`。 |

## `hermes claw`

```bash
hermes claw migrate [选项]
```

将你的 OpenClaw 设置迁移到 Hermes。从 `~/.openclaw`（或自定义路径）读取，并写入到 `~/.hermes`。自动检测旧的目录名（`~/.clawdbot`、`~/.moldbot`）和配置文件名（`clawdbot.json`、`moldbot.json`）。

| 选项 | 描述 |
|--------|-------------|
| `--dry-run` | 预览将要迁移的内容，但不实际写入任何内容。 |
| `--preset <名称>` | 迁移预设：`full`（默认，包含密钥）或 `user-data`（排除 API 密钥）。 |
| `--overwrite` | 冲突时覆盖现有的 Hermes 文件（默认：跳过）。 |
| `--migrate-secrets` | 在迁移中包含 API 密钥（使用 `--preset full` 时默认启用）。 |
| `--source <路径>` | 自定义 OpenClaw 目录（默认：`~/.openclaw`）。 |
| `--workspace-target <路径>` | 工作空间指令（AGENTS.md）的目标目录。 |
| `--skill-conflict <模式>` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

### 迁移内容

迁移涵盖你的整个 OpenClaw 足迹。项目要么被**直接导入**到 Hermes 的对应部分，要么在无法直接映射时被**归档**以供手动审查。

#### 直接导入

| 类别 | OpenClaw 来源 | Hermes 目标 |
|----------|----------------|-------------------|
| **角色设定** | `SOUL.md` | `~/.hermes/SOUL.md` |
| **工作空间指令** | `AGENTS.md` | 目标工作空间中的 `AGENTS.md` |
| **长期记忆** | `MEMORY.md` | `~/.hermes/MEMORY.md`（与现有条目合并） |
| **用户档案** | `USER.md` | `~/.hermes/USER.md`（与现有条目合并） |
| **每日记忆文件** | `workspace/memory/` | 合并到 `~/.hermes/MEMORY.md` |
| **默认模型** | 配置中的模型设置 | `config.yaml` 的 model 部分 |
| **自定义提供商** | 提供商定义（baseUrl, apiType, headers） | `config.yaml` 的 custom\_providers |
| **MCP 服务器** | MCP 服务器定义 | `config.yaml` 的 mcp\_servers |
| **用户技能** | 工作空间技能 | `~/.hermes/skills/openclaw-imports/` |
| **共享技能** | `~/.openclaw/skills/` | `~/.hermes/skills/openclaw-imports/` |
| **个人技能** | `~/.agents/skills/`（跨项目） | `~/.hermes/skills/openclaw-imports/` |
| **项目技能** | `workspace/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |
| **命令允许列表** | 执行批准模式 | `config.yaml` 的 command\_allowlist |
| **消息设置** | 允许列表、工作目录 | `config.yaml` 的 messaging 部分 |
| **会话策略** | 每日/空闲重置策略 | `config.yaml` 的 session\_reset |
| **智能体默认设置** | 压缩、上下文、思考设置 | `config.yaml` 的 agent 部分 |
| **浏览器设置** | 浏览器自动化配置 | `config.yaml` 的 browser 部分 |
| **工具设置** | 执行超时、沙箱、网络搜索 | `config.yaml` 的 tools 部分 |
| **批准规则** | 批准模式和规则 | `config.yaml` 的 approvals 部分 |
| **TTS 配置** | TTS 提供商和语音 | `config.yaml` 的 tts 部分 |
| **TTS 资源** | 工作空间 TTS 文件 | `~/.hermes/tts/` |
| **网关配置** | 网关端口和认证 | `config.yaml` 的 gateway 部分 |
| **Telegram 设置** | 机器人令牌、允许列表 | `~/.hermes/.env` |
| **Discord 设置** | 机器人令牌、允许列表 | `~/.hermes/.env` |
| **Slack 设置** | 机器人/应用令牌、允许列表 | `~/.hermes/.env` |
| **WhatsApp 设置** | 允许列表 | `~/.hermes/.env` |
| **Signal 设置** | 账户、HTTP URL、允许列表 | `~/.hermes/.env` |
| **频道配置** | Matrix、Mattermost、IRC、群组设置 | `config.yaml` + 归档 |
| **提供商 API 密钥** | 配置、`~/.openclaw/.env` 和 `auth-profiles.json` | `~/.hermes/.env`（需要 `--migrate-secrets`） |

#### 归档以供手动审查

这些 OpenClaw 功能在 Hermes 中没有直接对应项。它们会被保存到一个归档目录中，供你审查并手动重新创建。

| 类别 | 归档内容 | 如何在 Hermes 中重新创建 |
|----------|----------------|--------------------------|
| **Cron / 计划任务** | 任务定义 | 使用 `hermes cron create` 重新创建 |
| **插件** | 插件配置、已安装的扩展 | 查看 [插件指南](../user-guide/features/hooks.md) |
| **钩子和 Webhook** | 内部钩子、Webhook、Gmail 集成 | 使用 `hermes webhook` 或网关钩子 |
| **记忆后端** | QMD、向量搜索、引用设置 | 通过 `hermes honcho` 配置 Honcho |
| **技能注册表** | 每个技能的启用/配置/环境设置 | 使用 `hermes skills config` |
| **UI 和身份** | 主题、助手身份、显示偏好 | 使用 `/skin` 命令或 `config.yaml` |
| **日志记录** | 诊断配置 | 在 `config.yaml` 的 logging 部分设置 |

### 安全性

API 密钥**默认不迁移**。`--preset full` 预设会启用密钥迁移。密钥从三个来源收集（配置值优先，然后是 `.env`，最后是 `auth-profiles.json`），针对以下目标：`OPENROUTER_API_KEY`、`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`DEEPSEEK_API_KEY`、`GEMINI_API_KEY`、`ZAI_API_KEY`、`MINIMAX_API_KEY`、`ELEVENLABS_API_KEY`、`TELEGRAM_BOT_TOKEN` 和 `VOICE_TOOLS_OPENAI_KEY`。所有其他密钥将被跳过。

### 示例

```bash
# 预览将要迁移的内容
hermes claw migrate --dry-run

# 完整迁移，包括 API 密钥
hermes claw migrate --preset full

# 仅迁移用户数据（无密钥），覆盖冲突
hermes claw migrate --preset user-data --overwrite

# 从自定义 OpenClaw 路径迁移
hermes claw migrate --source /home/user/old-openclaw

# 迁移并将 AGENTS.md 放置到特定项目中
hermes claw migrate --workspace-target /home/user/my-project
```

## 维护命令

| 命令 | 描述 |
|---------|-------------|
| `hermes version` | 打印版本信息。 |
| `hermes update` | 拉取最新更改并重新安装依赖项。 |
| `hermes uninstall [--full] [--yes]` | 移除 Hermes，可选择删除所有配置/数据。 |

## 另请参阅

- [斜杠命令参考](./slash-commands.md)
- [CLI 界面](../user-guide/cli.md)
- [会话](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)
