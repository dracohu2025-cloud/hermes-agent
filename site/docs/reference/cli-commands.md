---
sidebar_position: 1
title: "CLI 命令参考"
description: "Hermes 终端命令及命令族的权威参考"
---

# CLI 命令参考 {#cli-commands-reference}

本页介绍你在 shell 中运行的**终端命令**。

聊天中的斜杠命令，请参见[斜杠命令参考](./slash-commands.md)。

## 全局入口 {#global-entrypoint}

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项 {#global-options}

| 选项 | 说明 |
|--------|-------------|
| `--version`, `-V` | 显示版本并退出。 |
| `--profile &lt;name&gt;`, `-p &lt;name&gt;` | 选择本次调用使用的 Hermes profile。会覆盖 `hermes profile use` 设置的粘性默认值。 |
| `--resume &lt;session&gt;`, `-r &lt;session&gt;` | 按 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近的会话，或恢复标题匹配的最近会话。 |
| `--worktree`, `-w` | 在独立的 git worktree 中启动，用于并行 Agent 工作流。 |
| `--yolo` | 跳过危险命令的确认提示。 |
| `--pass-session-id` | 将会话 ID 包含在 Agent 的系统提示词中。 |
| `--tui` | 启动 [TUI](../user-guide/tui.md) 而非经典 CLI。等价于 `HERMES_TUI=1`。 |
| `--dev` | 配合 `--tui` 使用：通过 `tsx` 直接运行 TypeScript 源码，而非预构建的 bundle（供 TUI 贡献者使用）。 |

## 顶层命令 {#top-level-commands}

| 命令 | 用途 |
|---------|---------|
| `hermes chat` | 与 Agent 进行交互式或一次性聊天。 |
| `hermes model` | 交互式选择默认提供商和模型。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes setup` | 交互式设置向导，可配置全部或部分配置项。 |
| `hermes whatsapp` | 配置并配对 WhatsApp 桥接。 |
| `hermes auth` | 管理凭据 —— 添加、列出、删除、重置、设置策略。处理 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已弃用** —— 请改用 `hermes auth`。 |
| `hermes status` | 显示 Agent、认证和平台状态。 |
| `hermes cron` | 查看并触发 cron 调度器。 |
| `hermes webhook` | 管理动态 webhook 订阅，用于事件驱动激活。 |
| `hermes doctor` | 诊断配置和依赖问题。 |
| `hermes dump` | 生成可复制粘贴的设置摘要，用于支持/调试。 |
| `hermes debug` | 调试工具 —— 上传日志和系统信息以获取支持。 |
| `hermes backup` | 将 Hermes 主目录备份为 zip 文件。 |
| `hermes import` | 从 zip 文件恢复 Hermes 备份。 |
| `hermes logs` | 查看、追踪和过滤 Agent/网关/错误日志文件。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置 skills。 |
| `hermes honcho` | 管理 Honcho 跨会话记忆集成。 |
| `hermes memory` | 配置外部记忆提供商。 |
| `hermes acp` | 以 ACP 服务器模式运行 Hermes，用于编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置，并以 MCP 服务器模式运行 Hermes。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、删除）。 |
| `hermes tools` | 按平台配置已启用的工具。 |
| `hermes sessions` | 浏览、导出、清理、重命名和删除会话。 |
| `hermes insights` | 显示 token/成本/活动分析数据。 |
| `hermes claw` | OpenClaw 迁移辅助工具。 |
| `hermes dashboard` | 启动网页仪表盘，用于管理配置、API 密钥和会话。 |
| `hermes profile` | 管理 profile —— 多个相互隔离的 Hermes 实例。 |
| `hermes completion` | 打印 shell 补全脚本（bash/zsh）。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖。 |
| `hermes uninstall` | 从系统中移除 Hermes。 |

## `hermes chat` {#hermes-chat}

```bash
hermes chat [options]
```

常用选项：

| 选项 | 说明 |
|--------|-------------|
| `-q`, `--query "..."` | 一次性、非交互式提示。 |
| `-m`, `--model &lt;model&gt;` | 本次运行临时覆盖模型。 |
| `-t`, `--toolsets &lt;csv&gt;` | 启用一组逗号分隔的 toolsets。 |
| `--provider &lt;provider&gt;` | 强制指定提供商：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot-acp`、`copilot`、`anthropic`、`gemini`、`google-gemini-cli`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`kilocode`、`xiaomi`、`arcee`、`alibaba`、`deepseek`、`nvidia`、`ollama-cloud`、`xai`（别名 `grok`）、`qwen-oauth`、`bedrock`、`opencode-zen`、`opencode-go`、`ai-gateway`。 |
| `-s`, `--skills &lt;name&gt;` | 为会话预加载一个或多个 skills（可重复指定或用逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 编程模式：隐藏 banner/转圈动画/工具预览。 |
| `--image &lt;path&gt;` | 为单次查询附加本地图片。 |
| `--resume &lt;session&gt;` / `--continue [name]` | 直接从 `chat` 恢复会话。 |
| `--worktree` | 为本次运行创建独立的 git worktree。 |
| `--checkpoints` | 在破坏性文件更改前启用文件系统检查点。 |
| `--yolo` | 跳过确认提示。 |
| `--pass-session-id` | 将会话 ID 传入系统提示词。 |
| `--source &lt;tag&gt;` | 会话来源标签，用于过滤（默认：`cli`）。第三方集成请使用 `tool`，避免出现在用户会话列表中。 |
| `--max-turns &lt;N&gt;` | 每轮对话的最大工具调用迭代次数（默认：90，或取配置中的 `agent.max_turns`）。 |
示例：

```bash
hermes
hermes chat -q "Summarize the latest PRs"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "Return only JSON"
hermes chat --worktree -q "Review this repo and open a PR"
```

## `hermes model` {#hermes-model}

交互式 provider + model 选择器。**这是添加新 provider、设置 API key 和运行 OAuth 流程的命令。** 请从终端运行，不要在活跃的 Hermes 聊天会话内部执行。

```bash
hermes model
```

在以下场景使用：
- **添加新 provider**（OpenRouter、Anthropic、Copilot、DeepSeek、自定义等）
- 登录 OAuth 支持的 provider（Anthropic、Copilot、Codex、Nous Portal）
- 输入或更新 API key
- 从 provider 专属的模型列表中选择
- 配置自定义/自托管端点
- 将新的默认值保存到配置

:::warning hermes model 与 /model — 注意区别
**`hermes model`**（从终端运行，在任何 Hermes 会话之外）是**完整的 provider 设置向导**。它可以添加新 provider、运行 OAuth 流程、提示输入 API key、配置端点。

<a id="hermes-model-vs-model-know-the-difference"></a>
**`/model`**（在活跃的 Hermes 聊天会话中输入）只能**在已设置好的 provider 和 model 之间切换**。它无法添加新 provider、运行 OAuth 或提示输入 API key。

**如果需要添加新 provider：** 先退出 Hermes 会话（`Ctrl+C` 或 `/quit`），然后从终端提示符运行 `hermes model`。
:::

### `/model` 斜杠命令（会话中） {#model-slash-command-mid-session}

无需离开会话即可在已配置的 model 之间切换：

```
/model                              # 显示当前 model 和可用选项
/model claude-sonnet-4              # 切换 model（自动识别 provider）
/model zai:glm-5                    # 切换 provider 和 model
/model custom:qwen-2.5              # 使用自定义端点上的 model
/model custom                       # 从自定义端点自动识别 model
/model custom:local:qwen-2.5        # 使用命名的自定义 provider
/model openrouter:anthropic/claude-sonnet-4  # 切回云端
```

默认情况下，`/model` 的更改**仅对当前会话生效**。添加 `--global` 可将更改持久化到 `config.yaml`：

```
/model claude-sonnet-4 --global     # 切换并保存为新的默认值
```

:::info 如果只看到 OpenRouter 的 model 怎么办？
如果你只配置了 OpenRouter，`/model` 就只会显示 OpenRouter 的 model。要添加其他 provider（Anthropic、DeepSeek、Copilot 等），请退出会话并从终端运行 `hermes model`。
<a id="what-if-i-only-see-openrouter-models"></a>
:::

Provider 和 base URL 的变更会自动持久化到 `config.yaml`。当从自定义端点切换离开时，过期的 base URL 会被清除，防止泄漏到其他 provider。

## `hermes gateway` {#hermes-gateway}

```bash
hermes gateway <subcommand>
```

子命令：

| 子命令 | 说明 |
|--------|------|
| `run` | 前台运行 gateway。WSL、Docker 和 Termux 推荐使用。 |
| `start` | 启动已安装的 systemd/launchd 后台服务。 |
| `stop` | 停止服务（或前台进程）。 |
| `restart` | 重启服务。 |
| `status` | 显示服务状态。 |
| `install` | 安装为 systemd（Linux）或 launchd（macOS）后台服务。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |

:::tip WSL 用户
<a id="wsl-users"></a>
请用 `hermes gateway run` 代替 `hermes gateway start` —— WSL 的 systemd 支持不太稳定。用 tmux 保持持久运行：`tmux new -s hermes 'hermes gateway run'`。详情见 [WSL FAQ](/reference/faq#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails)。
:::

## `hermes setup` {#hermes-setup}

```bash
hermes setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset]
```

使用完整向导，或直接跳到某一节：

| 章节 | 说明 |
|------|------|
| `model` | Provider 和 model 设置。 |
| `terminal` | 终端后端和沙箱设置。 |
| `gateway` | 消息平台设置。 |
| `tools` | 按平台启用/禁用工具。 |
| `agent` | Agent 行为设置。 |
Options:

| Option | Description |
|--------|-------------|
| `--non-interactive` | 使用默认值 / 环境变量值，不再提示输入。 |
| `--reset` | 在设置前将配置重置为默认值。 |

## `hermes whatsapp` {#hermes-whatsapp}

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

## `hermes login` / `hermes logout` *(已废弃)* {#hermes-login-hermes-logout-deprecated}

:::caution
`hermes login` 已被移除。请使用 `hermes auth` 管理 OAuth 凭证，`hermes model` 选择提供商，或 `hermes setup` 进行完整的交互式设置。
:::

## `hermes auth` {#hermes-auth}

管理同提供商密钥轮换的凭证池。完整文档请参见[凭证池](/user-guide/features/credential-pools)。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有池
hermes auth list openrouter                              # 显示指定提供商
hermes auth add openrouter --api-key sk-or-v1-xxx        # 添加 API 密钥
hermes auth add anthropic --type oauth                   # 添加 OAuth 凭证
hermes auth remove openrouter 2                          # 按索引移除
hermes auth reset openrouter                             # 清除冷却时间
```

子命令：`add`、`list`、`remove`、`reset`。不带子命令调用时，启动交互式管理向导。

## `hermes status` {#hermes-status}

```bash
hermes status [--all] [--deep]
```

| Option | Description |
|--------|-------------|
| `--all` | 以可分享的脱敏格式显示所有详情。 |
| `--deep` | 运行更深入的检查，可能需要更长时间。 |

## `hermes cron` {#hermes-cron}

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| Subcommand | Description |
|------------|-------------|
| `list` | 显示定时任务。 |
| `create` / `add` | 根据提示词创建定时任务，可通过重复指定 `--skill` 附加一个或多个技能。 |
| `edit` | 更新任务的调度规则、提示词、名称、投递方式、重复次数或附加技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务，但不删除。 |
| `resume` | 恢复已暂停的任务，并计算其下次运行时间。 |
| `run` | 在下次调度 tick 时触发任务。 |
| `remove` | 删除定时任务。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 执行一次到期任务后退出。 |

## `hermes webhook` {#hermes-webhook}

```bash
hermes webhook <subscribe|list|remove|test>
```

管理动态 webhook 订阅，用于事件驱动的 Agent 激活。需要在配置中启用 webhook 平台 —— 如未配置，将打印设置说明。

| Subcommand | Description |
|------------|-------------|
| `subscribe` / `add` | 创建 webhook 路由。返回 URL 和 HMAC 密钥，用于在你的服务上配置。 |
| `list` / `ls` | 显示所有 Agent 创建的订阅。 |
| `remove` / `rm` | 删除动态订阅。config.yaml 中的静态路由不受影响。 |
| `test` | 发送测试 POST 请求，验证订阅是否正常工作。 |

### `hermes webhook subscribe` {#hermes-webhook-subscribe}

```bash
hermes webhook subscribe <name> [options]
```

| Option | Description |
|--------|-------------|
| `--prompt` | 提示词模板，支持 `{dot.notation}` 形式的 payload 引用。 |
| `--events` | 接受的事件类型，逗号分隔（例如 `issues,pull_request`）。留空 = 全部接受。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 加载的技能名称，逗号分隔，用于 Agent 运行。 |
| `--deliver` | 投递目标：`log`（默认）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台投递的目标聊天/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。省略则自动生成。 |

订阅持久化到 `~/.hermes/webhook_subscriptions.json`，webhook 适配器会热重载这些配置，无需重启网关。

## `hermes doctor` {#hermes-doctor}

```bash
hermes doctor [--fix]
```

| Option | Description |
|--------|-------------|
| `--fix` | 尽可能尝试自动修复。 |
## `hermes dump` {#hermes-dump}

```bash
hermes dump [--show-keys]
```

输出整个 Hermes 设置的紧凑纯文本摘要。设计用于在 Discord、GitHub issue 或 Telegram 求助时直接复制粘贴——没有 ANSI 颜色，没有特殊格式，只有数据。

| Option | Description |
|--------|-------------|
| `--show-keys` | 显示脱敏后的 API key 前缀（首尾各 4 个字符），而不是只显示 `set`/`not set`。 |

### What it includes {#what-it-includes}

| Section | Details |
|---------|---------|
| **Header** | Hermes 版本、发布日期、git commit hash |
| **Environment** | 操作系统、Python 版本、OpenAI SDK 版本 |
| **Identity** | 当前 profile 名称、HERMES_HOME 路径 |
| **Model** | 配置的默认模型和 provider |
| **Terminal** | 后端类型（local、docker、ssh 等） |
| **API keys** | 全部 22 个 provider/tool API key 的存在性检查 |
| **Features** | 已启用的 toolset、MCP server 数量、memory provider |
| **Services** | Gateway 状态、已配置的消息平台 |
| **Workload** | Cron job 数量、已安装 skill 数量 |
| **Config overrides** | 任何与默认值不同的配置项 |

### Example output {#example-output}

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

### When to use {#when-to-use}

- 在 GitHub 上报 bug —— 把 dump 贴进 issue
- 在 Discord 求助 —— 用代码块分享
- 和别人对比配置
- 出问题时快速自查

:::tip
`hermes dump` 专为分享设计。如需交互式诊断，用 `hermes doctor`。如需可视化概览，用 `hermes status`。
:::

## `hermes debug` {#hermes-debug}

```bash
hermes debug share [options]
```

上传调试报告（系统信息 + 近期日志）到粘贴服务，获取可分享的 URL。适合快速求助——包含协助者诊断问题所需的全部信息。

| Option | Description |
|--------|-------------|
| `--lines &lt;N&gt;` | 每个日志文件包含的行数（默认：200）。 |
| `--expire &lt;days&gt;` | 粘贴有效期，单位为天（默认：7）。 |
| `--local` | 仅在本地输出报告，不上传。 |

报告包含系统信息（操作系统、Python 版本、Hermes 版本）、近期 Agent 和 Gateway 日志（每个文件 512 KB 上限），以及脱敏后的 API key 状态。Key 始终脱敏——不会上传任何密钥。

按顺序尝试的粘贴服务：paste.rs、dpaste.com。

### Examples {#examples}

```bash
hermes debug share              # 上传调试报告，输出 URL
hermes debug share --lines 500  # 包含更多日志行
hermes debug share --expire 30  # 粘贴保留 30 天
hermes debug share --local      # 输出报告到终端（不上传）
```

## `hermes backup` {#hermes-backup}

```bash
hermes backup [options]
```

创建 Hermes 配置、skill、会话和数据的 zip 压缩包。备份不包含 hermes-agent 代码库本身。

| Option | Description |
|--------|-------------|
| `-o`, `--output &lt;path&gt;` | zip 文件的输出路径（默认：`~/hermes-backup-&lt;timestamp&gt;.zip`）。 |
| `-q`, `--quick` | 快速快照：仅包含关键状态文件（config.yaml、state.db、.env、auth、cron job）。比完整备份快很多。 |
| `-l`, `--label &lt;name&gt;` | 快照标签（仅与 `--quick` 一起使用）。 |

备份使用 SQLite 的 `backup()` API 进行安全复制，因此即使 Hermes 正在运行也能正常工作（WAL 模式安全）。
### 示例 {#examples}

```bash
hermes backup                           # 完整备份到 ~/hermes-backup-*.zip
hermes backup -o /tmp/hermes.zip        # 完整备份到指定路径
hermes backup --quick                   # 仅状态快速快照
hermes backup --quick --label "pre-upgrade"  # 带标签的快速快照
```

## `hermes import` {#hermes-import}

```bash
hermes import <zipfile> [options]
```

将之前创建的 Hermes 备份恢复到 Hermes 主目录。

| 选项 | 说明 |
|--------|-------------|
| `-f`, `--force` | 覆盖已有文件，不提示确认。 |

## `hermes logs` {#hermes-logs}

```bash
hermes logs [log_name] [options]
```

查看、追踪和过滤 Hermes 日志文件。所有日志存放在 `~/.hermes/logs/`（非默认 profile 则为 `&lt;profile&gt;/logs/`）。

### 日志文件 {#log-files}

| 名称 | 文件 | 记录内容 |
|------|------|-----------------|
| `agent`（默认） | `agent.log` | 所有 Agent 活动 —— API 调用、工具分发、会话生命周期（INFO 及以上级别） |
| `errors` | `errors.log` | 仅警告和错误 —— agent.log 的过滤子集 |
| `gateway` | `gateway.log` | 消息网关活动 —— 平台连接、消息分发、webhook 事件 |

### 选项 {#options}

| 选项 | 说明 |
|--------|-------------|
| `log_name` | 要查看的日志：`agent`（默认）、`errors`、`gateway`，或 `list` 显示可用文件及大小。 |
| `-n`, `--lines &lt;N&gt;` | 显示行数（默认：50）。 |
| `-f`, `--follow` | 实时追踪日志，类似 `tail -f`。按 Ctrl+C 停止。 |
| `--level &lt;LEVEL&gt;` | 最低日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。 |
| `--session &lt;ID&gt;` | 过滤包含会话 ID 子串的行。 |
| `--since &lt;TIME&gt;` | 显示相对时间之前的行：`30m`、`1h`、`2d` 等。支持 `s`（秒）、`m`（分钟）、`h`（小时）、`d`（天）。 |
| `--component &lt;NAME&gt;` | 按组件过滤：`gateway`、`agent`、`tools`、`cli`、`cron`。 |

### 示例

```bash
# 查看 agent.log 最后 50 行（默认）
hermes logs

# 实时追踪 agent.log
hermes logs -f

# 查看 gateway.log 最后 100 行
hermes logs gateway -n 100

# 仅显示最近一小时的警告和错误
hermes logs --level WARNING --since 1h

# 按特定会话过滤
hermes logs --session abc123

# 从 30 分钟前开始追踪 errors.log
hermes logs errors --since 30m -f

# 列出所有日志文件及其大小
hermes logs list
```

### 过滤 {#filtering}

过滤条件可以组合使用。多个过滤条件同时生效时，日志行必须**全部**满足才会显示：

```bash
# 最近 2 小时内包含会话 "tg-12345" 的 WARNING 及以上级别行
hermes logs --level WARNING --since 2h --session tg-12345
```

当 `--since` 生效时，没有可解析时间戳的行也会被包含（它们可能是多行日志条目的续行）。当 `--level` 生效时，没有检测到级别的行也会被包含。

### 日志轮转 {#log-rotation}

Hermes 使用 Python 的 `RotatingFileHandler`。旧日志会自动轮转 —— 留意 `agent.log.1`、`agent.log.2` 等文件。`hermes logs list` 子命令会显示所有日志文件，包括已轮转的。

## `hermes config` {#hermes-config}

```bash
hermes config <subcommand>
```

子命令：

| 子命令 | 说明 |
|------------|-------------|
| `show` | 显示当前配置值。 |
| `edit` | 在编辑器中打开 `config.yaml`。 |
| `set &lt;key&gt; &lt;value&gt;` | 设置配置值。 |
| `path` | 打印配置文件路径。 |
| `env-path` | 打印 `.env` 文件路径。 |
| `check` | 检查缺失或过时的配置。 |
| `migrate` | 交互式添加新引入的选项。 |

## `hermes pairing` {#hermes-pairing}

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 说明 |
|------------|-------------|
| `list` | 显示待处理和已批准的用户。 |
| `approve &lt;platform&gt; &lt;code&gt;` | 批准配对码。 |
| `revoke &lt;platform&gt; &lt;user-id&gt;` | 撤销用户访问权限。 |
| `clear-pending` | 清除待处理的配对码。 |

## `hermes skills` {#hermes-skills}

```bash
hermes skills <subcommand>
```
Subcommands:

| Subcommand | Description |
|------------|-------------|
| `browse` | 分页浏览技能注册表。 |
| `search` | 搜索技能注册表。 |
| `install` | 安装技能。 |
| `inspect` | 预览技能而不安装。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 hub 技能是否有上游更新。 |
| `update` | 当上游有变更时，重新安装 hub 技能。 |
| `audit` | 重新扫描已安装的 hub 技能。 |
| `uninstall` | 移除通过 hub 安装的技能。 |
| `publish` | 将技能发布到注册表。 |
| `snapshot` | 导出/导入技能配置。 |
| `tap` | 管理自定义技能源。 |
| `config` | 按平台交互式启用/禁用技能配置。 |

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
- `--force` 可以覆盖第三方/社区技能的非危险策略拦截。
- `--force` 不会覆盖 `dangerous` 扫描判定。
- `--source skills-sh` 搜索公共的 `skills.sh` 目录。
- `--source well-known` 让 Hermes 指向暴露 `/.well-known/skills/index.json` 的网站。

## `hermes honcho` {#hermes-honcho}

```bash
hermes honcho [--target-profile NAME] <subcommand>
```

管理 Honcho 跨会话记忆集成。该命令由 Honcho 记忆提供方插件提供，仅当配置中 `memory.provider` 设为 `honcho` 时可用。

`--target-profile` 标志让你无需切换到其他 profile 就能管理它的 Honcho 配置。

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `setup` | 重定向到 `hermes memory setup`（统一设置路径）。 |
| `status [--all]` | 显示当前 Honcho 配置和连接状态。`--all` 显示跨 profile 概览。 |
| `peers` | 显示所有 profile 中的对等身份。 |
| `sessions` | 列出已知的 Honcho 会话映射。 |
| `map [name]` | 将当前目录映射到 Honcho 会话名。省略 `name` 则列出当前映射。 |
| `peer` | 显示或更新对等方名称和辩证推理级别。选项：`--user NAME`、`--ai NAME`、`--reasoning LEVEL`。 |
| `mode [mode]` | 显示或设置回忆模式：`hybrid`、`context` 或 `tools`。省略则显示当前模式。 |
| `tokens` | 显示或设置上下文和辩证的 token 预算。选项：`--context N`、`--dialectic N`。 |
| `identity [file] [--show]` | 设置或显示 AI 对等方身份表示。 |
| `enable` | 为当前 profile 启用 Honcho。 |
| `disable` | 为当前 profile 禁用 Honcho。 |
| `sync` | 将 Honcho 配置同步到所有现有 profile（创建缺失的 host 块）。 |
| `migrate` | 从 openclaw-honcho 迁移到 Hermes Honcho 的分步指南。 |

## `hermes memory` {#hermes-memory}

```bash
hermes memory <subcommand>
```

设置和管理外部记忆提供方插件。可用提供方：honcho、openviking、mem0、hindsight、holographic、retaindb、byterover、supermemory。同一时间只能激活一个外部提供方。内置记忆（MEMORY.md/USER.md）始终处于激活状态。

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `setup` | 交互式选择提供方并进行配置。 |
| `status` | 显示当前记忆提供方配置。 |
| `off` | 禁用外部提供方（仅使用内置）。 |

## `hermes acp` {#hermes-acp}

```bash
hermes acp
```

将 Hermes 作为 ACP（Agent Client Protocol）stdio 服务器启动，用于编辑器集成。

相关入口点：

```bash
hermes-acp
python -m acp_adapter
```

先安装支持：

```bash
pip install -e '.[acp]'
```

参见 [ACP 编辑器集成](../user-guide/features/acp.md) 和 [ACP 内部机制](../developer-guide/acp-internals.md)。
## `hermes mcp` {#hermes-mcp}

```bash
hermes mcp <subcommand>
```

管理 MCP（Model Context Protocol）服务器配置，或将 Hermes 作为 MCP 服务器运行。

| 子命令 | 说明 |
|------------|-------------|
| `serve [-v\|--verbose]` | 将 Hermes 作为 MCP 服务器运行 —— 向其他 Agent 暴露对话能力。 |
| `add &lt;name&gt; [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加 MCP 服务器，自动发现工具。 |
| `remove &lt;name&gt;`（别名：`rm`） | 从配置中移除 MCP 服务器。 |
| `list`（别名：`ls`） | 列出已配置的 MCP 服务器。 |
| `test &lt;name&gt;` | 测试与 MCP 服务器的连接。 |
| `configure &lt;name&gt;`（别名：`config`） | 为服务器切换工具选择。 |

参见 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 以及 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins` {#hermes-plugins}

```bash
hermes plugins [subcommand]
```

统一的插件管理 —— 通用插件、记忆提供者和上下文引擎都在一个地方管理。不带子命令运行 `hermes plugins` 会打开一个组合式交互界面，包含两个区域：

- **通用插件** —— 多选复选框，用于启用/禁用已安装的插件
- **提供者插件** —— 记忆提供者和上下文引擎的单选配置。在分类上按 ENTER 打开单选选择器。

| 子命令 | 说明 |
|------------|-------------|
| *(无)* | 组合式交互界面 —— 通用插件开关 + 提供者插件配置。 |
| `install &lt;identifier&gt; [--force]` | 从 Git URL 或 `owner/repo` 安装插件。 |
| `update &lt;name&gt;` | 拉取已安装插件的最新更改。 |
| `remove &lt;name&gt;`（别名：`rm`、`uninstall`） | 移除已安装的插件。 |
| `enable &lt;name&gt;` | 启用已禁用的插件。 |
| `disable &lt;name&gt;` | 禁用插件，但不移除。 |
| `list`（别名：`ls`） | 列出已安装的插件及其启用/禁用状态。 |

提供者插件的选择会保存到 `config.yaml`：
- `memory.provider` —— 当前记忆提供者（留空 = 仅使用内置）
- `context.engine` —— 当前上下文引擎（`"compressor"` = 内置默认值）

通用插件的禁用列表保存在 `config.yaml` 的 `plugins.disabled` 下。

参见 [插件](../user-guide/features/plugins.md) 和 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。

## `hermes tools` {#hermes-tools}

```bash
hermes tools [--summary]
```

| 选项 | 说明 |
|--------|-------------|
| `--summary` | 打印当前已启用工具的摘要并退出。 |

不带 `--summary` 时，会启动按平台划分的交互式工具配置界面。

## `hermes sessions` {#hermes-sessions}

```bash
hermes sessions <subcommand>
```

子命令：

| 子命令 | 说明 |
|------------|-------------|
| `list` | 列出最近的会话。 |
| `browse` | 交互式会话选择器，支持搜索和恢复。 |
| `export &lt;output&gt; [--session-id ID]` | 将会话导出为 JSONL。 |
| `delete &lt;session-id&gt;` | 删除单个会话。 |
| `prune` | 删除旧会话。 |
| `stats` | 显示会话存储统计信息。 |
| `rename &lt;session-id&gt; &lt;title&gt;` | 设置或修改会话标题。 |

## `hermes insights` {#hermes-insights}

```bash
hermes insights [--days N] [--source platform]
```

| 选项 | 说明 |
|--------|-------------|
| `--days &lt;n&gt;` | 分析最近 `n` 天的数据（默认：30）。 |
| `--source &lt;platform&gt;` | 按来源过滤，例如 `cli`、`telegram` 或 `discord`。 |

## `hermes claw` {#hermes-claw}

```bash
hermes claw migrate [options]
```

将 OpenClaw 配置迁移到 Hermes。从 `~/.openclaw`（或自定义路径）读取，写入到 `~/.hermes`。自动检测旧版目录名（`~/.clawdbot`、`~/.moltbot`）和配置文件名（`clawdbot.json`、`moltbot.json`）。

| 选项 | 说明 |
|--------|-------------|
| `--dry-run` | 预览将要迁移的内容，不实际写入。 |
| `--preset &lt;name&gt;` | 迁移预设：`full`（默认，包含密钥）或 `user-data`（排除 API 密钥）。 |
| `--overwrite` | 冲突时覆盖现有 Hermes 文件（默认：跳过）。 |
| `--migrate-secrets` | 迁移时包含 API 密钥（使用 `--preset full` 时默认启用）。 |
| `--source &lt;path&gt;` | 自定义 OpenClaw 目录（默认：`~/.openclaw`）。 |
| `--workspace-target &lt;path&gt;` | 工作区指令的目标目录（AGENTS.md）。 |
| `--skill-conflict &lt;mode&gt;` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |
### 迁移内容 {#what-gets-migrated}

迁移涵盖 30 多个类别，涉及 persona、memory、skills、模型提供商、消息平台、Agent 行为、session 策略、MCP 服务器、TTS 等。各项内容要么**直接导入**到 Hermes 的对应模块，要么**归档**供手动审查。

**直接导入：** SOUL.md、MEMORY.md、USER.md、AGENTS.md、skills（4 个源目录）、默认模型、自定义提供商、MCP 服务器、消息平台令牌和允许列表（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、Agent 默认值（推理 effort、compression、human delay、时区、sandbox）、session 重置策略、审批规则、TTS 配置、浏览器设置、工具设置、exec 超时、命令允许列表、gateway 配置，以及 3 个来源的 API key。

**归档供手动审查：** Cron jobs、plugins、hooks/webhooks、memory 后端（QMD）、skills registry 配置、UI/identity、日志、多 Agent 设置、channel bindings、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md。

**API key 解析**按优先级顺序检查三个来源：config 值 → `~/.openclaw/.env` → `auth-profiles.json`。所有 token 字段都支持纯字符串、环境变量模板（`${VAR}`）和 SecretRef 对象。

完整的 config key 映射、SecretRef 处理细节和迁移后检查清单，参见 **[完整迁移指南](../guides/migrate-from-openclaw.md)**。

<a id="examples"></a>
### 示例

```bash
# 预览将要迁移的内容
hermes claw migrate --dry-run

# 完整迁移，包括 API keys
hermes claw migrate --preset full

# 仅迁移用户数据（不含 secrets），覆盖冲突项
hermes claw migrate --preset user-data --overwrite

# 从自定义 OpenClaw 路径迁移
hermes claw migrate --source /home/user/old-openclaw
```

## `hermes dashboard` {#hermes-dashboard}

```bash
hermes dashboard [options]
```

启动 Web 仪表盘——一个基于浏览器的 UI，用于管理配置、API key 和监控 session。需要 `pip install hermes-agent[web]`（FastAPI + Uvicorn）。完整文档参见 [Web 仪表盘](/user-guide/features/web-dashboard)。

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--port` | `9119` | Web 服务器运行端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |

```bash
# 默认行为 — 打开浏览器访问 http://127.0.0.1:9119
hermes dashboard

# 自定义端口，不打开浏览器
hermes dashboard --port 8080 --no-open
```

## `hermes profile` {#hermes-profile}

```bash
hermes profile <subcommand>
```

管理 profile——多个相互隔离的 Hermes 实例，每个实例拥有独立的配置、session、skill 和 home 目录。

| 子命令 | 说明 |
|--------|------|
| `list` | 列出所有 profile。 |
| `use &lt;name&gt;` | 设置默认的粘性 profile。 |
| `create &lt;name&gt; [--clone] [--clone-all] [--clone-from &lt;source&gt;] [--no-alias]` | 创建新 profile。`--clone` 从当前活跃 profile 复制 config、`.env` 和 `SOUL.md`。`--clone-all` 复制所有状态。`--clone-from` 指定来源 profile。 |
| `delete &lt;name&gt; [-y]` | 删除 profile。 |
| `show &lt;name&gt;` | 显示 profile 详情（home 目录、config 等）。 |
| `alias &lt;name&gt; [--remove] [--name NAME]` | 管理快速访问 profile 的 wrapper 脚本。 |
| `rename &lt;old&gt; &lt;new&gt;` | 重命名 profile。 |
| `export &lt;name&gt; [-o FILE]` | 导出 profile 为 `.tar.gz` 归档。 |
| `import &lt;archive&gt; [--name NAME]` | 从 `.tar.gz` 归档导入 profile。 |

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

## `hermes completion` {#hermes-completion}

```bash
hermes completion [bash|zsh]
```

将 shell 补全脚本输出到 stdout。在 shell profile 中 source 该输出，即可对 Hermes 命令、子命令和 profile 名称使用 tab 补全。

示例：

```bash
# Bash
hermes completion bash >> ~/.bashrc

# Zsh
hermes completion zsh >> ~/.zshrc
```
## 维护命令 {#maintenance-commands}

| 命令 | 说明 |
|---------|-------------|
| `hermes version` | 打印版本信息。 |
| `hermes update` | 拉取最新更改并重新安装依赖。 |
| `hermes uninstall [--full] [--yes]` | 卸载 Hermes，可选择删除所有配置/数据。 |

## 另请参阅 {#see-also}

- [斜杠命令参考](./slash-commands.md)
- [CLI 界面](../user-guide/cli.md)
- [会话](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)
