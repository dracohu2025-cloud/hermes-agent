---
sidebar_position: 1
title: "CLI 命令参考"
description: "Hermes 终端命令及命令族的权威参考"
---

# CLI 命令参考

本页面涵盖了你在 shell 中运行的**终端命令**。

关于聊天内的斜杠命令，请参阅 [Slash Commands Reference](./slash-commands.md)。

## 全局入口

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项

| 选项 | 描述 |
|--------|-------------|
| `--version`, `-V` | 显示版本并退出。 |
| `--profile <name>`, `-p <name>` | 选择本次调用所使用的 Hermes 配置方案（profile）。会覆盖通过 `hermes profile use` 设置的固定默认值。 |
| `--resume <session>`, `-r <session>` | 通过 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近一次会话，或恢复标题匹配的最近一次会话。 |
| `--worktree`, `-w` | 在隔离的 git worktree 中启动，用于并行 Agent 工作流。 |
| `--yolo` | 跳过危险命令的确认提示。 |
| `--pass-session-id` | 将会话 ID 包含在 Agent 的系统提示词中。 |

## 顶级命令

| 命令 | 用途 |
|---------|---------|
| `hermes chat` | 与 Agent 进行交互式或单次对话。 |
| `hermes model` | 交互式选择默认提供商和模型。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes setup` | 用于全部或部分配置的交互式设置向导。 |
| `hermes whatsapp` | 配置并配对 WhatsApp 网桥。 |
| `hermes auth` | 管理凭据——添加、列出、移除、重置、设置策略。处理 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已弃用** — 请改用 `hermes auth`。 |
| `hermes status` | 显示 Agent、认证及平台状态。 |
| `hermes cron` | 检查并触发 cron 调度器。 |
| `hermes webhook` | 管理用于事件驱动激活的动态 webhook 订阅。 |
| `hermes doctor` | 诊断配置和依赖项问题。 |
| `hermes dump` | 为支持/调试提供可复制粘贴的设置摘要。 |
| `hermes logs` | 查看、追踪（tail）并过滤 Agent/网关/错误日志文件。 |
| `hermes config` | 显示、编辑、迁移及查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计及配置技能（skills）。 |
| `hermes honcho` | 管理 Honcho 跨会话记忆集成。 |
| `hermes memory` | 配置外部记忆提供商。 |
| `hermes acp` | 将 Hermes 作为 ACP 服务器运行，用于编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置并将 Hermes 作为 MCP 服务器运行。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、移除）。 |
| `hermes tools` | 按平台配置已启用的工具。 |
| `hermes sessions` | 浏览、导出、修剪、重命名及删除会话。 |
| `hermes insights` | 显示 Token/成本/活动分析。 |
| `hermes claw` | OpenClaw 迁移辅助工具。 |
| `hermes profile` | 管理配置方案（profile）——多个隔离的 Hermes 实例。 |
| `hermes completion` | 打印 shell 自动补全脚本（bash/zsh）。 |
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
| `-q`, `--query "..."` | 单次、非交互式提示。 |
| `-m`, `--model <model>` | 覆盖本次运行的模型。 |
| `-t`, `--toolsets <csv>` | 启用一组以逗号分隔的工具集。 |
| `--provider <provider>` | 强制指定提供商：`auto`, `openrouter`, `nous`, `openai-codex`, `copilot-acp`, `copilot`, `anthropic`, `huggingface`, `zai`, `kimi-coding`, `minimax`, `minimax-cn`, `deepseek`, `ai-gateway`, `opencode-zen`, `opencode-go`, `kilocode`, `alibaba`。 |
| `-s`, `--skills <name>` | 为会话预加载一个或多个技能（可重复使用或以逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 程序化模式：抑制横幅/加载动画/工具预览。 |
| `--resume <session>` / `--continue [name]` | 直接从 `chat` 恢复会话。 |
| `--worktree` | 为本次运行创建隔离的 git worktree。 |
| `--checkpoints` | 在破坏性文件更改前启用文件系统检查点。 |
| `--yolo` | 跳过确认提示。 |
| `--pass-session-id` | 将会话 ID 传入系统提示词。 |
| `--source <tag>` | 用于过滤的会话来源标签（默认：`cli`）。对于不应出现在用户会话列表中的第三方集成，请使用 `tool`。 |
| `--max-turns <N>` | 每个对话轮次的最大工具调用迭代次数（默认：90，或配置中的 `agent.max_turns`）。 |

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

当你想要执行以下操作时使用：
- 切换默认提供商
- 在模型选择期间登录 OAuth 支持的提供商
- 从特定提供商的模型列表中进行选择
- 配置自定义/自托管的端点
- 将新的默认值保存到配置中

### `/model` 斜杠命令（会话中）

在不离开会话的情况下切换模型：

```
/model                              # 显示当前模型及可用选项
/model claude-sonnet-4              # 切换模型（自动检测提供商）
/model zai:glm-5                    # 切换提供商和模型
/model custom:qwen-2.5              # 在自定义端点上使用模型
/model custom                       # 从自定义端点自动检测模型
/model custom:local:qwen-2.5        # 使用已命名的自定义提供商
/model openrouter:anthropic/claude-sonnet-4  # 切换回云端
```

提供商和基础 URL 的更改会自动持久化到 `config.yaml`。当从自定义端点切换离开时，旧的基础 URL 会被清除，以防止其泄露给其他提供商。

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

使用完整向导或跳转到特定部分：

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
| `--non-interactive` | 使用默认值/环境变量而不进行提示。 |
| `--reset` | 在设置前将配置重置为默认值。 |

## `hermes whatsapp`

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

## `hermes login` / `hermes logout` *(已弃用)*

:::caution
`hermes login` 已被移除。请使用 `hermes auth` 管理 OAuth 凭据，使用 `hermes model` 选择提供商，或使用 `hermes setup` 进行完整的交互式设置。
:::

## `hermes auth`

管理凭据池以实现同提供商的密钥轮换。完整文档请参阅 [Credential Pools](/user-guide/features/credential-pools)。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有凭据池
hermes auth list openrouter                              # 显示特定提供商
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
| `--all` | 以可共享的脱敏格式显示所有详细信息。 |
| `--deep` | 运行可能耗时较长的深度检查。 |

## `hermes cron`

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示已计划的任务。 |
| `create` / `add` | 根据提示词创建计划任务，可通过多次使用 `--skill` 附加一个或多个技能。 |
| `edit` | 更新任务的计划时间、提示词、名称、交付方式、重复次数或附加技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务而不删除它。 |
| `resume` | 恢复已暂停的任务并计算其下一次运行时间。 |
| `run` | 在下一个调度程序周期触发任务。 |
| `remove` | 删除已计划的任务。 |
| `status` | 检查 cron 调度程序是否正在运行。 |
| `tick` | 运行一次到期的任务并退出。 |

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

管理用于事件驱动型 Agent 激活的动态 Webhook 订阅。要求在配置中启用 Webhook 平台——如果未配置，将打印设置说明。

| 子命令 | 描述 |
|------------|-------------|
| `subscribe` / `add` | 创建 Webhook 路由。返回用于在您的服务上进行配置的 URL 和 HMAC 密钥。 |
| `list` / `ls` | 显示所有由 Agent 创建的订阅。 |
| `remove` / `rm` | 删除动态订阅。不会影响 `config.yaml` 中的静态路由。 |
| `test` | 发送测试 POST 请求以验证订阅是否正常工作。 |

### `hermes webhook subscribe`

```bash
hermes webhook subscribe <name> [options]
```

| 选项 | 描述 |
|--------|-------------|
| `--prompt` | 带有 `{dot.notation}` 有效负载引用的提示词模板。 |
| `--events` | 以逗号分隔的接受事件类型（例如 `issues,pull_request`）。留空表示全部。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 以逗号分隔的 Agent 运行所需加载的技能名称。 |
| `--deliver` | 交付目标：`log`（默认）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 用于跨平台交付的目标聊天/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。如果省略，则自动生成。 |

订阅会持久化到 `~/.hermes/webhook_subscriptions.json`，并由 Webhook 适配器热加载，无需重启网关。

## `hermes doctor`

```bash
hermes doctor [--fix]
```

| 选项 | 描述 |
|--------|-------------|
| `--fix` | 尽可能尝试自动修复。 |

## `hermes dump`

```bash
hermes dump [--show-keys]
```

输出整个 Hermes 设置的紧凑纯文本摘要。专为在寻求支持时粘贴到 Discord、GitHub issues 或 Telegram 中而设计——没有 ANSI 颜色，没有特殊格式，只有数据。

| 选项 | 描述 |
|--------|-------------|
| `--show-keys` | 显示脱敏后的 API 密钥前缀（前 4 位和后 4 位），而不是仅显示 `set`（已设置）/`not set`（未设置）。 |

### 包含内容

| 部分 | 详情 |
|---------|---------|
| **Header** | Hermes 版本、发布日期、git 提交哈希 |
| **Environment** | 操作系统、Python 版本、OpenAI SDK 版本 |
| **Identity** | 活动配置文件名称、HERMES_HOME 路径 |
| **Model** | 配置的默认模型和提供商 |
| **Terminal** | 后端类型（local、docker、ssh 等） |
| **API keys** | 所有 22 个提供商/工具 API 密钥的存在性检查 |
| **Features** | 已启用的工具集、MCP 服务器数量、内存提供商 |
| **Services** | 网关状态、已配置的消息传递平台 |
| **Workload** | Cron 任务数量、已安装的技能数量 |
| **Config overrides** | 任何与默认值不同的配置项 |

### 输出示例

```
--- hermes dump ---
version:          0.8.0 (2026.4.8) [af4abd2f]
os:               Linux 6.14.0-37-generic x86_64
python:           3.11.14
openai_sdk:       2.24.0
profile:          default
hermes_home:      ~/.hermes
model:            anthropic/claude-opus-4.6
provider:         openrouter
terminal:         local

api_keys:
  openrouter           set
  openai               not set
  anthropic            set
  nous                 not set
  firecrawl            set
  ...

features:
  toolsets:           all
  mcp_servers:        0
  memory_provider:    built-in
  gateway:            running (systemd)
  platforms:          telegram, discord
  cron_jobs:          3 active / 5 total
  skills:             42

config_overrides:
  agent.max_turns: 250
  compression.threshold: 0.85
  display.streaming: True
--- end dump ---
```

### 使用场景

- 在 GitHub 上报告 Bug 时 — 将 dump 内容粘贴到 issue 中
- 在 Discord 中寻求帮助时 — 在代码块中分享它
- 将您的设置与他人进行比较时
- 当某些功能无法正常工作时进行快速健康检查

:::tip
`hermes dump` 专为分享而设计。如需交互式诊断，请使用 `hermes doctor`。如需可视化概览，请使用 `hermes status`。
:::

## `hermes logs`

```bash
hermes logs [log_name] [options]
```

查看、追踪和过滤 Hermes 日志文件。所有日志都存储在 `~/.hermes/logs/`（非默认配置文件则在 `<profile>/logs/`）中。

### 日志文件

| 名称 | 文件 | 捕获内容 |
|------|------|-----------------|
| `agent` (默认) | `agent.log` | 所有 Agent 活动 — API 调用、工具调度、会话生命周期（INFO 及以上级别） |
| `errors` | `errors.log` | 仅警告和错误 — agent.log 的过滤子集 |
| `gateway` | `gateway.log` | 消息网关活动 — 平台连接、消息分发、Webhook 事件 |

### 选项

| 选项 | 描述 |
|--------|-------------|
| `log_name` | 要查看的日志：`agent`（默认）、`errors`、`gateway`，或使用 `list` 显示可用文件及其大小。 |
| `-n`, `--lines <N>` | 显示的行数（默认：50）。 |
| `-f`, `--follow` | 实时追踪日志，类似于 `tail -f`。按 Ctrl+C 停止。 |
| `--level <LEVEL>` | 显示的最低日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。 |
| `--session <ID>` | 过滤包含会话 ID 子字符串的行。 |
| `--since <TIME>` | 显示从相对时间点开始的行：`30m`、`1h`、`2d` 等。支持 `s`（秒）、`m`（分钟）、`h`（小时）、`d`（天）。 |

### 示例

```bash
# 查看 agent.log（默认）的最后 50 行
hermes logs

# 实时追踪 agent.log
hermes logs -f

# 查看 gateway.log 的最后 100 行
hermes logs gateway -n 100

# 仅显示过去一小时内的警告和错误
hermes logs --level WARNING --since 1h

# 按特定会话过滤
hermes logs --session abc123

# 追踪 errors.log，从 30 分钟前开始
hermes logs errors --since 30m -f

# 列出所有日志文件及其大小
hermes logs list
```

### 过滤

过滤器可以组合使用。当多个过滤器同时激活时，日志行必须通过**所有**过滤器才能显示：

```bash
# 显示过去 2 小时内包含会话 "tg-12345" 的 WARNING 及以上级别的日志行
hermes logs --level WARNING --since 2h --session tg-12345
```

当 `--since` 激活时，不带可解析时间戳的行也会被包含（它们可能是多行日志条目的后续行）。当 `--level` 激活时，不带可检测级别的行也会被包含。

### 日志轮转

Hermes 使用 Python 的 `RotatingFileHandler`。旧日志会自动轮转 — 请查找 `agent.log.1`、`agent.log.2` 等。`hermes logs list` 子命令会显示所有日志文件，包括已轮转的文件。

## `hermes config`

```bash
hermes config <subcommand>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `show` | 显示当前配置值。 |
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
| `install` | 安装技能。 |
| `inspect` | 在不安装的情况下预览技能。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 Hub 技能是否有上游更新。 |
| `update` | 在有可用更新时，重新安装带有上游变更的 Hub 技能。 |
| `audit` | 重新扫描已安装的 Hub 技能。 |
| `uninstall` | 移除通过 Hub 安装的技能。 |
| `publish` | 将技能发布到注册表。 |
| `snapshot` | 导出/导入技能配置。 |
| `tap` | 管理自定义技能源。 |
| `config` | 针对不同平台交互式地启用/禁用技能配置。 |

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
- `--force` 可以覆盖针对第三方/社区技能的非危险策略拦截。
- `--force` 不会覆盖 `dangerous`（危险）扫描判定。
- `--source skills-sh` 会搜索公共的 `skills.sh` 目录。
- `--source well-known` 允许你将 Hermes 指向一个暴露了 `/.well-known/skills/index.json` 的站点。

## `hermes honcho`

```bash
hermes honcho [--target-profile NAME] <subcommand>
```

管理 Honcho 跨会话记忆集成。此命令由 Honcho 记忆提供程序插件提供，仅当配置中 `memory.provider` 设置为 `honcho` 时可用。

`--target-profile` 标志允许你在不切换配置文件的状态下管理另一个配置文件的 Honcho 设置。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 重定向至 `hermes memory setup`（统一设置路径）。 |
| `status [--all]` | 显示当前的 Honcho 配置和连接状态。`--all` 显示跨配置文件的概览。 |
| `peers` | 显示所有配置文件中的对等方身份。 |
| `sessions` | 列出已知的 Honcho 会话映射。 |
| `map [name]` | 将当前目录映射到某个 Honcho 会话名称。省略 `name` 可列出当前映射。 |
| `peer` | 显示或更新对等方名称及辩证推理级别。选项：`--user NAME`，`--ai NAME`，`--reasoning LEVEL`。 |
| `mode [mode]` | 显示或设置回溯模式：`hybrid`、`context` 或 `tools`。省略则显示当前模式。 |
| `tokens` | 显示或设置上下文和辩证法的 Token 配额。选项：`--context N`，`--dialectic N`。 |
| `identity [file] [--show]` | 植入或显示 AI 对等方身份表示。 |
| `enable` | 为当前活动配置文件启用 Honcho。 |
| `disable` | 为当前活动配置文件禁用 Honcho。 |
| `sync` | 将 Honcho 配置同步到所有现有配置文件（创建缺失的 host 块）。 |
| `migrate` | 从 openclaw-honcho 迁移到 Hermes Honcho 的分步指南。 |

## `hermes memory`

```bash
hermes memory <subcommand>
```

设置并管理外部记忆提供程序插件。可用提供程序：honcho, openviking, mem0, hindsight, holographic, retaindb, byterover, supermemory。同一时间只能激活一个外部提供程序。内置记忆（MEMORY.md/USER.md）始终处于激活状态。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式提供程序选择与配置。 |
| `status` | 显示当前记忆提供程序配置。 |
| `off` | 禁用外部提供程序（仅使用内置记忆）。 |

## `hermes acp`

```bash
hermes acp
```

启动 Hermes 作为 ACP (Agent Client Protocol) stdio 服务器，用于编辑器集成。

相关入口点：

```bash
hermes-acp
python -m acp_adapter
```

首先安装支持：

```bash
pip install -e '.[acp]'
```

请参阅 [ACP 编辑器集成](../user-guide/features/acp.md) 和 [ACP 内部原理](../developer-guide/acp-internals.md)。

## `hermes mcp`

```bash
hermes mcp <subcommand>
```

管理 MCP (Model Context Protocol) 服务器配置并以 MCP 服务器模式运行 Hermes。

| 子命令 | 描述 |
|------------|-------------|
| `serve [-v\|--verbose]` | 以 MCP 服务器模式运行 Hermes — 向其他 Agent 暴露对话。 |
| `add <name> [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加一个具有自动工具发现功能的 MCP 服务器。 |
| `remove <name>` (别名: `rm`) | 从配置中移除 MCP 服务器。 |
| `list` (别名: `ls`) | 列出已配置的 MCP 服务器。 |
| `test <name>` | 测试与 MCP 服务器的连接。 |
| `configure <name>` (别名: `config`) | 切换服务器的工具选择。 |

请参阅 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 以及 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins`

```bash
hermes plugins [subcommand]
```

管理 Hermes Agent 插件。不带子命令运行 `hermes plugins` 将启动一个交互式 curses 检查列表，用于启用/禁用已安装的插件。

| 子命令 | 描述 |
|------------|-------------|
| *(无)* | 交互式切换 UI — 使用方向键和空格键启用/禁用插件。 |
| `install <identifier> [--force]` | 从 Git URL 或 `owner/repo` 安装插件。 |
| `update <name>` | 拉取已安装插件的最新变更。 |
| `remove <name>` (别名: `rm`, `uninstall`) | 移除已安装的插件。 |
| `enable <name>` | 启用已禁用的插件。 |
| `disable <name>` | 禁用插件而不将其移除。 |
| `list` (别名: `ls`) | 列出已安装插件及其启用/禁用状态。 |

禁用的插件存储在 `config.yaml` 的 `plugins.disabled` 下，并在加载过程中被跳过。

请参阅 [插件](../user-guide/features/plugins.md) 和 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。

## `hermes tools`

```bash
hermes tools [--summary]
```

| 选项 | 描述 |
|--------|-------------|
| `--summary` | 打印当前已启用工具的摘要并退出。 |

如果不带 `--summary`，此命令将启动交互式的各平台工具配置 UI。

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
| `--days <n>` | 分析过去 `n` 天的数据（默认：30）。 |
| `--source <platform>` | 按来源过滤，例如 `cli`、`telegram` 或 `discord`。 |

## `hermes claw`

```bash
hermes claw migrate [options]
```

将你的 OpenClaw 设置迁移到 Hermes。从 `~/.openclaw`（或自定义路径）读取并写入 `~/.hermes`。自动检测旧版目录名称（`~/.clawdbot`、`~/.moldbot`）和配置文件名（`clawdbot.json`、`moldbot.json`）。

| 选项 | 描述 |
|--------|-------------|
| `--dry-run` | 预览迁移内容而不进行实际写入。 |
| `--preset <name>` | 迁移预设：`full`（默认，包含密钥）或 `user-data`（排除 API 密钥）。 |
| `--overwrite` | 冲突时覆盖现有的 Hermes 文件（默认：跳过）。 |
| `--migrate-secrets` | 在迁移中包含 API 密钥（使用 `--preset full` 时默认启用）。 |
| `--source <path>` | 自定义 OpenClaw 目录（默认：`~/.openclaw`）。 |
| `--workspace-target <path>` | 工作区指令的目标目录 (AGENTS.md)。 |
| `--skill-conflict <mode>` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |
### 迁移内容

迁移涵盖了 persona、memory、skills、模型提供商、消息平台、Agent 行为、会话策略、MCP 服务器、TTS 等 30 多个类别。项目要么被**直接导入**为 Hermes 的等效项，要么被**归档**以供手动检查。

**直接导入：** SOUL.md、MEMORY.md、USER.md、AGENTS.md、skills（4 个源目录）、默认模型、自定义提供商、MCP 服务器、消息平台令牌和允许列表（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、Agent 默认设置（推理工作量、压缩、人工延迟、时区、沙盒）、会话重置策略、批准规则、TTS 配置、浏览器设置、工具设置、执行超时、命令允许列表、网关配置以及来自 3 个来源的 API 密钥。

**归档以供手动检查：** Cron 任务、插件、钩子/Webhooks、内存后端 (QMD)、skills 注册表配置、UI/身份、日志记录、多 Agent 设置、频道绑定、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md。

**API 密钥解析**按优先级检查三个来源：配置值 → `~/.openclaw/.env` → `auth-profiles.json`。所有令牌字段均处理纯字符串、环境变量模板 (`${VAR}`) 和 SecretRef 对象。

有关完整的配置键映射、SecretRef 处理细节以及迁移后检查清单，请参阅 **[完整迁移指南](../guides/migrate-from-openclaw.md)**。

### 示例

```bash
# 预览将要迁移的内容
hermes claw migrate --dry-run

# 执行完整迁移，包括 API 密钥
hermes claw migrate --preset full

# 仅迁移用户数据（不含密钥），覆盖冲突项
hermes claw migrate --preset user-data --overwrite

# 从自定义 OpenClaw 路径迁移
hermes claw migrate --source /home/user/old-openclaw
```

## `hermes profile`

```bash
hermes profile <subcommand>
```

管理配置文件——即多个相互隔离的 Hermes 实例，每个实例都有自己的配置、会话、skills 和主目录。

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出所有配置文件。 |
| `use <name>` | 设置一个固定的默认配置文件。 |
| `create <name> [--clone] [--clone-all] [--clone-from <source>] [--no-alias]` | 创建新配置文件。`--clone` 从当前活动配置文件复制配置、`.env` 和 `SOUL.md`。`--clone-all` 复制所有状态。`--clone-from` 指定源配置文件。 |
| `delete <name> [-y]` | 删除配置文件。 |
| `show <name>` | 显示配置文件详情（主目录、配置等）。 |
| `alias <name> [--remove] [--name NAME]` | 管理用于快速访问配置文件的包装脚本。 |
| `rename <old> <new>` | 重命名配置文件。 |
| `export <name> [-o FILE]` | 将配置文件导出为 `.tar.gz` 压缩包。 |
| `import <archive> [--name NAME]` | 从 `.tar.gz` 压缩包导入配置文件。 |

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

将 shell 补全脚本打印到标准输出。在你的 shell 配置文件中 source 该输出，即可实现 Hermes 命令、子命令和配置文件名的 Tab 键补全。

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
| `hermes update` | 拉取最新更改并重新安装依赖项。 |
| `hermes uninstall [--full] [--yes]` | 卸载 Hermes，可选择删除所有配置/数据。 |

## 另请参阅

- [斜杠命令参考](./slash-commands.md)
- [CLI 接口](../user-guide/cli.md)
- [会话](../user-guide/sessions.md)
- [Skills 系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)
