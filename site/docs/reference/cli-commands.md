---
sidebar_position: 1
title: "CLI 命令参考"
description: "Hermes 终端命令及命令族的权威参考"
---

# CLI 命令参考 {#cli-commands-reference}

本页涵盖你在 shell 中运行的**终端命令**。

关于聊天内斜杠命令，请参阅[斜杠命令参考](./slash-commands.md)。

## 全局入口点 {#global-entrypoint}

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项 {#global-options}

| 选项 | 描述 |
|--------|-------------|
| `--version`, `-V` | 显示版本并退出。 |
| `--profile &lt;name&gt;`, `-p &lt;name&gt;` | 选择本次调用使用的 Hermes 配置文件。覆盖由 `hermes profile use` 设置的粘性默认值。 |
| `--resume &lt;session&gt;`, `-r &lt;session&gt;` | 通过 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近的会话，或匹配标题的最近会话。 |
| `--worktree`, `-w` | 在隔离的 git worktree 中启动，用于并行 Agent 工作流。 |
| `--yolo` | 绕过危险命令的批准提示。 |
| `--pass-session-id` | 在 Agent 的系统提示中包含会话 ID。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml`，回退到内置默认值。`.env` 中的凭据仍会加载。 |
| `--ignore-rules` | 跳过自动注入 `AGENTS.md`、`SOUL.md`、`.cursorrules`、记忆和预加载技能。 |
| `--tui` | 启动 [TUI](../user-guide/tui.md) 而非经典 CLI。等同于 `HERMES_TUI=1`。 |
| `--dev` | 与 `--tui` 一起使用：通过 `tsx` 直接运行 TypeScript 源码，而非预构建包（适用于 TUI 贡献者）。 |

## 顶层命令 {#top-level-commands}

| 命令 | 用途 |
|---------|-------------|
| `hermes chat` | 与 Agent 进行交互式或一次性聊天。 |
| `hermes model` | 交互式选择默认提供商和模型。 |
| `hermes fallback` | 管理主模型出错时尝试的备用提供商。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes setup` | 交互式设置向导，用于全部或部分配置。 |
| `hermes whatsapp` | 配置并配对 WhatsApp 桥接。 |
| `hermes slack` | Slack 辅助工具（当前：生成应用清单，将每个命令作为原生斜杠命令）。 |
| `hermes auth` | 管理凭据——添加、列出、删除、重置、设置策略。处理 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已弃用**——请改用 `hermes auth`。 |
| `hermes status` | 显示 Agent、认证和平台状态。 |
| `hermes cron` | 检查并触发 cron 调度器。 |
| `hermes kanban` | 多配置文件协作面板（任务、链接、调度器）。 |
| `hermes webhook` | 管理动态 webhook 订阅，用于事件驱动激活。 |
| `hermes hooks` | 检查、批准或删除 `config.yaml` 中声明的 shell 脚本钩子。 |
| `hermes doctor` | 诊断配置和依赖问题。 |
| `hermes dump` | 可复制粘贴的设置摘要，用于支持/调试。 |
| `hermes debug` | 调试工具——上传日志和系统信息以获取支持。 |
| `hermes backup` | 将 Hermes 主目录备份为 zip 文件。 |
| `hermes import` | 从 zip 文件恢复 Hermes 备份。 |
| `hermes logs` | 查看、跟踪和过滤 Agent/网关/错误日志文件。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置技能。 |
| `hermes curator` | 后台技能维护——状态、运行、暂停、固定。参见[Curator](../user-guide/features/curator.md)。 |
| `hermes memory` | 配置外部内存提供商。插件特定的子命令（例如 `hermes honcho`）在其提供商激活时自动注册。 |
| `hermes acp` | 将 Hermes 作为 ACP 服务器运行，用于编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置，并将 Hermes 作为 MCP 服务器运行。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、移除）。 |
| `hermes tools` | 按平台配置启用的工具。 |
| `hermes sessions` | 浏览、导出、清理、重命名和删除会话。 |
| `hermes insights` | 显示 token/成本/活动分析。 |
| `hermes fallback` | 备用提供商链的交互式管理器。 |
| `hermes claw` | OpenClaw 迁移辅助工具。 |
| `hermes dashboard` | 启动 Web 仪表板，用于管理配置、API 密钥和会话。 |
| `hermes profile` | 管理配置文件——多个隔离的 Hermes 实例。 |
| `hermes completion` | 打印 shell 补全脚本（bash/zsh/fish）。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖。`--check` 打印提交差异而不拉取；`--backup` 在拉取前创建 `HERMES_HOME` 快照。 |
| `hermes uninstall` | 从系统中移除 Hermes。 |
## `hermes chat` {#hermes-chat}

```bash
hermes chat [options]
```

常用选项：

| 选项 | 说明 |
|------|------|
| `-q`, `--query "..."` | 一次性非交互式提示。 |
| `-m`, `--model &lt;model&gt;` | 覆盖本次运行的模型。 |
| `-t`, `--toolsets &lt;csv&gt;` | 启用一组逗号分隔的工具集。 |
| `--provider &lt;provider&gt;` | 强制指定提供商：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot-acp`、`copilot`、`anthropic`、`gemini`、`google-gemini-cli`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`alibaba`、`alibaba-coding-plan`（别名 `alibaba_coding`）、`deepseek`、`nvidia`、`ollama-cloud`、`xai`（别名 `grok`）、`qwen-oauth`、`bedrock`、`opencode-zen`、`opencode-go`、`ai-gateway`、`azure-foundry`、`tencent-tokenhub`（别名 `tencent`、`tokenhub`）。 |
| `-s`, `--skills &lt;name&gt;` | 为会话预加载一个或多个技能（可重复或逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 程序化模式：隐藏横幅/旋转动画/工具预览。 |
| `--image &lt;path&gt;` | 将本地图片附加到单次查询中。 |
| `--resume &lt;session&gt;` / `--continue [name]` | 直接从 `chat` 恢复会话。 |
| `--worktree` | 为此运行创建一个隔离的 git worktree。 |
| `--checkpoints` | 在破坏性文件更改之前启用文件系统检查点。 |
| `--yolo` | 跳过审批提示。 |
| `--pass-session-id` | 将会话 ID 传入系统提示。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml`，使用内置默认值。`.env` 中的凭据仍会加载。适用于隔离的 CI 运行、可复现的 bug 报告以及第三方集成。 |
| `--ignore-rules` | 跳过自动注入 `AGENTS.md`、`SOUL.md`、`.cursorrules`、持久记忆和预加载技能。与 `--ignore-user-config` 结合使用可实现完全隔离运行。 |
| `--source &lt;tag&gt;` | 用于过滤的会话来源标签（默认：`cli`）。对于不应出现在用户会话列表中的第三方集成，请使用 `tool`。 |
| `--max-turns &lt;N&gt;` | 每次对话轮次的最大工具调用迭代次数（默认：90，或配置中的 `agent.max_turns`）。 |

示例：

```bash
hermes
hermes chat -q "Summarize the latest PRs"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "Return only JSON"
hermes chat --worktree -q "Review this repo and open a PR"
hermes chat --ignore-user-config --ignore-rules -q "Repro without my personal setup"
```

### `hermes -z &lt;prompt&gt;` — 脚本化一次性调用 {#hermes-z-scripted-one-shot}

对于程序化调用者（shell 脚本、CI、cron、通过管道传入提示的父进程），`hermes -z` 是最纯粹的一次性入口点：**单次提示输入，最终响应文本输出，stdout 和 stderr 上无其他内容。** 没有横幅、没有旋转动画、没有工具预览、没有 `Session:` 行——只有 Agent 的最终回复作为纯文本。

```bash
hermes -z "What's the capital of France?"
# → Paris.

# 父脚本可以干净地捕获响应：
answer=$(hermes -z "summarize this" < /path/to/file.txt)
```
每次运行的覆盖（不会修改 `~/.hermes/config.yaml`）：

| 标志 | 对应的环境变量 | 用途 |
|---|---|---|
| `-m` / `--model &lt;model&gt;` | `HERMES_INFERENCE_MODEL` | 覆盖本次运行的模型 |
| `--provider &lt;provider&gt;` | `HERMES_INFERENCE_PROVIDER` | 覆盖本次运行的提供商 |

```bash
hermes -z "…" --provider openrouter --model openai/gpt-5.5
# 或者：
HERMES_INFERENCE_MODEL=anthropic/claude-sonnet-4.6 hermes -z "…"
```

相同的 Agent、相同的工具、相同的技能——只是去掉了所有交互/装饰层。如果你也需要在记录中看到工具输出，请改用 `hermes chat -q`；`-z` 明确用于“我只想要最终答案”。

## `hermes model` {#hermes-model}

交互式提供商 + 模型选择器。**这是用于添加新提供商、设置 API 密钥以及运行 OAuth 流程的命令。** 从终端运行它——而不是在活跃的 Hermes 聊天会话内部。

```bash
hermes model
```

在以下情况下使用此命令：
- **添加新提供商**（OpenRouter、Anthropic、Copilot、DeepSeek、自定义等）
- 登录到支持 OAuth 的提供商（Anthropic、Copilot、Codex、Nous Portal）
- 输入或更新 API 密钥
- 从提供商特定的模型列表中选择
- 配置自定义/自托管端点
- 将新的默认设置保存到配置中

:::warning hermes model 与 /model 的区别
<a id="hermes-model-vs-model-know-the-difference"></a>
**`hermes model`**（从终端运行，在任何 Hermes 会话之外）是**完整的提供商设置向导**。它可以添加新提供商、运行 OAuth 流程、提示输入 API 密钥以及配置端点。

**`/model`**（在活跃的 Hermes 聊天会话内输入）只能**在已设置好的提供商和模型之间切换**。它无法添加新提供商、运行 OAuth 或提示输入 API 密钥。

**如果你需要添加新提供商：** 先退出 Hermes 会话（`Ctrl+C` 或 `/quit`），然后在终端提示符下运行 `hermes model`。
:::

### `/model` 斜杠命令（会话中） {#model-slash-command-mid-session}

在不离开会话的情况下切换已配置好的模型：

```
/model                              # 显示当前模型和可用选项
/model claude-sonnet-4              # 切换模型（自动检测提供商）
/model zai:glm-5                    # 切换提供商和模型
/model custom:qwen-2.5              # 在你的自定义端点上使用模型
/model custom                       # 从自定义端点自动检测模型
/model custom:local:qwen-2.5        # 使用命名的自定义提供商
/model openrouter:anthropic/claude-sonnet-4  # 切换回云端
```

默认情况下，`/model` 的更改**仅适用于当前会话**。添加 `--global` 可将更改持久化到 `config.yaml`：

```
/model claude-sonnet-4 --global     # 切换并保存为新默认值
```

<a id="what-if-i-only-see-openrouter-models"></a>
:::info 如果我只看到 OpenRouter 模型怎么办？
如果你只配置了 OpenRouter，`/model` 将只显示 OpenRouter 模型。要添加其他提供商（Anthropic、DeepSeek、Copilot 等），请退出会话并在终端运行 `hermes model`。
:::

提供商和基础 URL 的更改会自动持久化到 `config.yaml`。当从自定义端点切换出去时，过时的基础 URL 会被清除，以防止它泄漏到其他提供商中。
## `hermes gateway` {#hermes-gateway}

```bash
hermes gateway <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `run` | 在前台运行网关。推荐用于 WSL、Docker 和 Termux。 |
| `start` | 启动已安装的 systemd/launchd 后台服务。 |
| `stop` | 停止服务（或前台进程）。 |
| `restart` | 重启服务。 |
| `status` | 显示服务状态。 |
| `install` | 安装为 systemd（Linux）或 launchd（macOS）后台服务。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--all` | 在 `start` / `restart` / `stop` 时：作用于**每个配置文件的**网关，而不仅仅是当前激活的 `HERMES_HOME`。如果你同时运行多个配置文件并希望在 `hermes update` 后全部重启，这个选项很有用。 |

:::tip WSL 用户
请使用 `hermes gateway run` 而不是 `hermes gateway start`——WSL 的 systemd 支持不可靠。可以将其包装在 tmux 中以保持持久运行：`tmux new -s hermes 'hermes gateway run'`。详情请参阅 [WSL 常见问题](/reference/faq#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails)。
:::
<a id="wsl-users"></a>

## `hermes setup` {#hermes-setup}

```bash
hermes setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset] [--quick] [--reconfigure]
```

**首次运行：** 启动首次使用向导。

**老用户（已配置过）：** 直接进入完整的重新配置向导——每个提示都会显示你当前的值作为默认值，按 Enter 保留或输入新值。没有菜单。

直接跳转到某个部分而不是完整的向导：

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
| `--quick` | 对于老用户运行：仅提示缺失或未设置的项目。跳过你已经配置好的项目。 |
| `--non-interactive` | 使用默认值/环境变量值，不进行交互式提示。 |
| `--reset` | 在设置前将配置重置为默认值。 |
| `--reconfigure` | 向后兼容的别名——现在在已有安装上直接运行 `hermes setup` 默认会执行此操作。 |

## `hermes whatsapp` {#hermes-whatsapp}

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

## `hermes slack` {#hermes-slack}

```bash
hermes slack manifest              # 将清单打印到标准输出
hermes slack manifest --write      # 写入 ~/.hermes/slack-manifest.json
hermes slack manifest --slashes-only  # 仅输出 features.slash_commands 数组
```

生成一个 Slack 应用清单，将 `COMMAND_REGISTRY` 中的每个网关命令（`/btw`、`/stop`、`/model` 等）注册为一等 Slack 斜杠命令——与 Discord 和 Telegram 保持一致。将输出粘贴到你的 Slack 应用配置中，位置在 [https://api.slack.com/apps](https://api.slack.com/apps) → 你的应用 → **Features → App Manifest → Edit**，然后点击 **Save**。如果作用域或斜杠命令发生变化，Slack 会提示重新安装。
| 标志 | 默认值 | 用途 |
|------|---------|------|
| `--write [PATH]` | stdout | 写入文件而非标准输出。仅用 `--write` 会写入 `$HERMES_HOME/slack-manifest.json`。 |
| `--name NAME` | `Hermes` | Slack 中的机器人显示名称。 |
| `--description DESC` | 默认简介 | Slack 应用目录中显示的机器人描述。 |
| `--slashes-only` | 关闭 | 仅输出 `features.slash_commands`，用于合并到手动维护的 manifest 中。 |

在 `hermes update` 之后再次运行 `hermes slack manifest --write`，以获取任何新命令。

## `hermes login` / `hermes logout` *(已弃用)* {#hermes-login-hermes-logout-deprecated}

:::caution
`hermes login` 已被移除。请使用 `hermes auth` 管理 OAuth 凭据，使用 `hermes model` 选择提供商，或使用 `hermes setup` 进行完整的交互式设置。
:::

## `hermes auth` {#hermes-auth}

管理同一提供商的凭据池，用于密钥轮换。完整文档请参见[凭据池](/user-guide/features/credential-pools)。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有池
hermes auth list openrouter                              # 显示特定提供商
hermes auth add openrouter --api-key sk-or-v1-xxx        # 添加 API 密钥
hermes auth add anthropic --type oauth                   # 添加 OAuth 凭据
hermes auth remove openrouter 2                          # 按索引移除
hermes auth reset openrouter                             # 清除冷却状态
```

子命令：`add`、`list`、`remove`、`reset`。不带子命令调用时，启动交互式管理向导。

## `hermes status` {#hermes-status}

```bash
hermes status [--all] [--deep]
```

| 选项 | 描述 |
|--------|-------------|
| `--all` | 以可分享的脱敏格式显示所有详细信息。 |
| `--deep` | 执行更深入的检查，可能需要更长时间。 |

## `hermes cron` {#hermes-cron}

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示已计划的任务。 |
| `create` / `add` | 根据提示创建计划任务，可通过重复 `--skill` 附加一个或多个技能。 |
| `edit` | 更新任务的计划、提示、名称、投递方式、重复次数或附加的技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务而不删除。 |
| `resume` | 恢复已暂停的任务并计算下一次运行时间。 |
| `run` | 在下一个调度器 tick 时触发任务。 |
| `remove` | 删除计划任务。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 运行一次到期任务后退出。 |

## `hermes kanban` {#hermes-kanban}

```bash
hermes kanban <action> [options]
```

多配置文件协作看板。任务存储在 `~/.hermes/kanban.db`（WAL 模式 SQLite）；所有配置文件读写同一个看板。由 `cron` 驱动的调度器（`hermes kanban dispatch`）原子性地认领就绪任务，并将分配的配置文件作为独立进程启动，拥有隔离的工作空间。

| 操作 | 用途 |
|--------|---------|
| `init` | 创建 `kanban.db`（如果不存在）。幂等操作。 |
| `create "&lt;title&gt;"` | 创建新任务。标志：`--body`、`--assignee`、`--parent`（可重复）、`--workspace scratch\|worktree\|dir:&lt;path&gt;`、`--tenant`、`--priority`。 |
| `list` / `ls` | 列出任务。可使用 `--mine`、`--assignee`、`--status`、`--tenant`、`--archived`、`--json` 过滤。 |
| `show &lt;id&gt;` | 显示任务及其评论和事件。`--json` 用于机器输出。 |
| `assign &lt;id&gt; &lt;profile&gt;` | 分配或重新分配。使用 `none` 取消分配。任务运行中时拒绝操作。 |
| `link &lt;parent&gt; &lt;child&gt;` | 添加依赖关系。会检测循环依赖。 |
| `unlink &lt;parent&gt; &lt;child&gt;` | 移除依赖关系。 |
| `claim &lt;id&gt;` | 原子性地认领一个就绪任务。打印解析后的工作空间路径。 |
| `comment &lt;id&gt; "&lt;text&gt;"` | 添加评论。对下一个运行该任务的工作者可见。 |
| `complete &lt;id&gt;` | 标记任务完成。标志：`--result "&lt;summary&gt;"`（会进入子任务的父结果上下文）。 |
| `block &lt;id&gt; "&lt;reason&gt;"` | 标记任务阻塞。同时将原因作为评论添加。 |
| `unblock &lt;id&gt;` | 将阻塞的任务恢复为就绪状态。 |
| `archive &lt;id&gt;` | 从默认列表中隐藏。`gc` 会移除暂存工作空间。 |
| `tail &lt;id&gt;` | 跟踪任务的事件流。 |
| `dispatch` | 执行一次调度器传递。标志：`--dry-run`、`--max N`、`--json`。 |
| `context &lt;id&gt;` | 打印工作者将看到的完整上下文（标题 + 正文 + 父结果 + 评论）。 |
| `gc` | 移除已归档任务的暂存工作空间。 |
所有操作也都可通过网关内的斜杠命令（`/kanban …`）使用，参数接口完全相同。

完整设计（包括与 Cline Kanban / Paperclip / NanoClaw / Gemini Enterprise 的对比、八种协作模式、四个用户故事、并发正确性证明）请参见仓库中的 `docs/hermes-kanban-v1-spec.pdf` 或 [Kanban 用户指南](/user-guide/features/kanban)。

## `hermes webhook` {#hermes-webhook}

```bash
hermes webhook <subscribe|list|remove|test>
```

管理动态 webhook 订阅，用于事件驱动的 Agent 激活。需要在配置中启用 webhook 平台——若未配置，则会打印设置指引。

| 子命令 | 描述 |
|------------|-------------|
| `subscribe` / `add` | 创建一个 webhook 路由。返回要在你的服务上配置的 URL 和 HMAC 密钥。 |
| `list` / `ls` | 显示所有由 Agent 创建的订阅。 |
| `remove` / `rm` | 删除一个动态订阅。`config.yaml` 中的静态路由不受影响。 |
| `test` | 发送一个测试 POST 请求以验证订阅是否正常工作。 |

### `hermes webhook subscribe` {#hermes-webhook-subscribe}

```bash
hermes webhook subscribe <name> [options]
```

| 选项 | 描述 |
|--------|-------------|
| `--prompt` | 提示模板，支持 `{dot.notation}` 格式的载荷引用。 |
| `--events` | 接受的事件类型（逗号分隔），例如 `issues,pull_request`。留空表示接受所有。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 为 Agent 运行加载的技能名称，逗号分隔。 |
| `--deliver` | 投递目标：`log`（默认）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台投递的目标聊天/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。留空则自动生成。 |

订阅持久化存储在 `~/.hermes/webhook_subscriptions.json` 中，webhook 适配器会热加载这些变更，无需重启网关。

## `hermes doctor` {#hermes-doctor}

```bash
hermes doctor [--fix]
```

| 选项 | 描述 |
|--------|-------------|
| `--fix` | 尽可能尝试自动修复。 |

## `hermes dump` {#hermes-dump}

```bash
hermes dump [--show-keys]
```

输出整个 Hermes 设置的紧凑纯文本摘要。旨在方便你直接复制粘贴到 Discord、GitHub issue 或 Telegram 中寻求支持——不含 ANSI 颜色或特殊格式，仅输出数据。

| 选项 | 描述 |
|--------|-------------|
| `--show-keys` | 显示脱敏的 API 密钥前缀（前 4 个和后 4 个字符），而不是仅显示 `set`/`not set`。 |

### 包含内容 {#what-it-includes}

| 章节 | 详情 |
|---------|---------|
| **Header** | Hermes 版本、发布日期、Git 提交哈希 |
| **Environment** | 操作系统、Python 版本、OpenAI SDK 版本 |
| **Identity** | 当前激活的配置文件名称、`HERMES_HOME` 路径 |
| **Model** | 配置的默认模型和提供商 |
| **Terminal** | 后端类型（local、docker、ssh 等） |
| **API keys** | 所有 22 个提供商/工具 API 密钥的存在性检查 |
| **Features** | 已启用的工具集、MCP 服务器数量、内存提供商 |
| **Services** | 网关状态、已配置的消息平台 |
| **Workload** | 定时任务数量、已安装的技能数量 |
| **Config overrides** | 与默认值不同的任何配置值 |
### 示例输出 {#example-output}

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

### 何时使用 {#when-to-use}

- 在 GitHub 上报告 bug —— 将 dump 粘贴到你的 issue 中
- 在 Discord 上请求帮助 —— 用代码块分享出去
- 将自己的配置与其他人进行对比
- 当某个功能不工作时快速做一次健康检查

:::tip
`hermes dump` 是专为分享而设计的。如需交互式诊断，请使用 `hermes doctor`。如需可视化概览，请使用 `hermes status`。
:::

## `hermes debug` {#hermes-debug}

```bash
hermes debug share [options]
```

将调试报告（系统信息 + 近期日志）上传到粘贴服务，并获取一个可分享的 URL。适用于快速支持请求 —— 包含助手诊断你的问题所需的一切信息。

| 选项 | 描述 |
|--------|-------------|
| `--lines &lt;N&gt;` | 每个日志文件包含的行数（默认：200）。 |
| `--expire &lt;days&gt;` | 粘贴的过期天数（默认：7）。 |
| `--local` | 在本地打印报告，不上传。 |

报告包含系统信息（操作系统、Python 版本、Hermes 版本）、最近的 agent 和 gateway 日志（每个文件限制 512 KB），以及脱敏后的 API 密钥状态。密钥始终会被脱敏 —— 不会上传任何秘密信息。

粘贴服务按顺序尝试：paste.rs、dpaste.com。

### 示例 {#examples}

```bash
hermes debug share              # 上传调试报告，打印 URL
hermes debug share --lines 500  # 包含更多日志行
hermes debug share --expire 30  # 让粘贴保留 30 天
hermes debug share --local      # 在终端打印报告（不上传）
```

## `hermes backup` {#hermes-backup}

```bash
hermes backup [options]
```

将你的 Hermes 配置、技能、会话和数据创建成一个 zip 归档。备份不包含 hermes-agent 的代码库本身。

| 选项 | 描述 |
|--------|-------------|
| `-o`, `--output &lt;path&gt;` | zip 文件的输出路径（默认：`~/hermes-backup-&lt;timestamp&gt;.zip`）。 |
| `-q`, `--quick` | 快速快照：仅备份关键状态文件（config.yaml、state.db、.env、auth、cron 作业）。比完整备份快得多。 |
| `-l`, `--label &lt;name&gt;` | 快照的标签（仅与 `--quick` 一起使用）。 |

备份使用 SQLite 的 `backup()` API 进行安全复制，因此即使在 Hermes 运行时也能正常工作（WAL 模式安全）。

**zip 中排除的内容：**
- `*.db-wal`、`*.db-shm`、`*.db-journal` — SQLite 的 WAL / 共享内存 / 日志附属文件。`*.db` 文件已通过 `sqlite3.backup()` 获得了一致性快照；如果同时附带这些活跃的附属文件，恢复时可能会看到半提交状态。
- `checkpoints/` — 每个会话的轨迹缓存。按哈希键存储，每个会话重新生成；换到其他安装环境也无法直接移植。
- `hermes-agent` 代码本身（这是用户数据备份，不是仓库快照）。

### 示例 {#examples}

```bash
hermes backup                           # 完整备份到 ~/hermes-backup-*.zip
hermes backup -o /tmp/hermes.zip        # 完整备份到指定路径
hermes backup --quick                   # 仅快速状态快照
hermes backup --quick --label "pre-upgrade"  # 带标签的快速快照
```

## `hermes import` {#hermes-import}

```bash
hermes import <zipfile> [options]
```

将之前创建的 Hermes 备份恢复到你的 Hermes 主目录中。

| 选项 | 描述 |
|------|------|
| `-f`, `--force` | 覆盖已有文件，无需确认。 |

## `hermes logs` {#hermes-logs}

```bash
hermes logs [log_name] [options]
```

查看、跟踪和过滤 Hermes 日志文件。所有日志都存储在 `~/.hermes/logs/` 中（对于非默认配置文件，则为 `&lt;profile&gt;/logs/`）。

### 日志文件 {#log-files}

| 名称 | 文件 | 捕获内容 |
|------|------|---------|
| `agent`（默认） | `agent.log` | 所有 Agent 活动 — API 调用、工具分发、会话生命周期（INFO 及以上级别） |
| `errors` | `errors.log` | 仅警告和错误 — `agent.log` 的过滤子集 |
| `gateway` | `gateway.log` | 消息网关活动 — 平台连接、消息分发、Webhook 事件 |

### 选项 {#options}

| 选项 | 描述 |
|------|------|
| `log_name` | 要查看的日志：`agent`（默认）、`errors`、`gateway`，或 `list` 显示可用文件及其大小。 |
| `-n`, `--lines &lt;N&gt;` | 显示的行数（默认：50）。 |
| `-f`, `--follow` | 实时跟踪日志，类似 `tail -f`。按 Ctrl+C 停止。 |
| `--level &lt;LEVEL&gt;` | 显示的最低日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。 |
| `--session &lt;ID&gt;` | 过滤包含会话 ID 子串的行。 |
| `--since &lt;TIME&gt;` | 显示从相对时间之前开始的行：`30m`、`1h`、`2d` 等。支持 `s`（秒）、`m`（分钟）、`h`（小时）、`d`（天）。 |
| `--component &lt;NAME&gt;` | 按组件过滤：`gateway`、`agent`、`tools`、`cli`、`cron`。 |

### 示例

```bash
# 查看 agent.log 的最后 50 行（默认）
hermes logs

# 实时跟踪 agent.log
hermes logs -f

# 查看 gateway.log 的最后 100 行
hermes logs gateway -n 100

# 仅显示过去一小时的警告和错误
hermes logs --level WARNING --since 1h

# 按特定会话过滤
hermes logs --session abc123

# 跟踪 errors.log，从 30 分钟前开始
hermes logs errors --since 30m -f

# 列出所有日志文件及其大小
hermes logs list
```

### 过滤 {#filtering}

过滤器可以组合使用。当多个过滤器同时生效时，日志行必须通过**所有**过滤器才会显示：
```bash
# 最近2小时内包含会话 "tg-12345" 的 WARNING+ 级别日志
hermes logs --level WARNING --since 2h --session tg-12345
```

当使用 `--since` 时，没有可解析时间戳的行也会被包含（它们可能是多行日志条目的续行）。当使用 `--level` 时，没有可检测级别的行也会被包含。

### 日志轮转 {#log-rotation}

Hermes 使用 Python 的 `RotatingFileHandler`。旧日志会自动轮转——你会看到 `agent.log.1`、`agent.log.2` 等文件。`hermes logs list` 子命令会显示所有日志文件，包括已轮转的文件。

## `hermes config` {#hermes-config}

```bash
hermes config <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `show` | 显示当前配置值。 |
| `edit` | 在编辑器中打开 `config.yaml`。 |
| `set &lt;key&gt; &lt;value&gt;` | 设置一个配置值。 |
| `path` | 打印配置文件路径。 |
| `env-path` | 打印 `.env` 文件路径。 |
| `check` | 检查缺失或过期的配置。 |
| `migrate` | 交互式添加新引入的选项。 |

## `hermes pairing` {#hermes-pairing}

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示待处理和已批准的用户。 |
| `approve &lt;platform&gt; &lt;code&gt;` | 批准一个配对码。 |
| `revoke &lt;platform&gt; &lt;user-id&gt;` | 撤销某个用户的访问权限。 |
| `clear-pending` | 清除待处理的配对码。 |

## `hermes skills` {#hermes-skills}

```bash
hermes skills <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `browse` | 技能注册表的分页浏览器。 |
| `search` | 搜索技能注册表。 |
| `install` | 安装一个技能。 |
| `inspect` | 预览一个技能而不安装它。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 hub 技能是否有上游更新。 |
| `update` | 当有上游变更时重新安装 hub 技能。 |
| `audit` | 重新扫描已安装的 hub 技能。 |
| `uninstall` | 移除一个通过 hub 安装的技能。 |
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
hermes skills install https://sharethis.chat/SKILL.md                     # 直接 URL（单文件 SKILL.md）
hermes skills install https://example.com/SKILL.md --name my-skill        # 当 frontmatter 中没有名称时覆盖名称
hermes skills check
hermes skills update
hermes skills config
```

注意：
- `--force` 可以覆盖第三方/社区技能的非危险策略块。
- `--force` 不能覆盖 `dangerous` 扫描结果。
- `--source skills-sh` 搜索公共的 `skills.sh` 目录。
- `--source well-known` 让你将 Hermes 指向一个暴露 `/.well-known/skills/index.json` 的站点。
- 传入 `http(s)://…/*.md` URL 会直接安装一个单文件 SKILL.md。当 frontmatter 没有 `name:` 且 URL slug 不是有效标识符时，交互式终端会提示输入名称；非交互式界面（TUI 内的 `/skills install`、网关平台）则需要使用 `--name &lt;x&gt;`。
## `hermes curator` {#hermes-curator}

```bash
hermes curator <子命令>
```

策展人是一个辅助模型后台任务，它会定期审查 Agent 创建的技能、清理过时的技能、合并重叠的技能，并归档废弃的技能。捆绑安装和从中心安装的技能永远不会被触及。归档的技能可以恢复，不会自动删除。

| 子命令 | 描述 |
|--------|------|
| `status` | 显示策展人状态和技能统计 |
| `run` | 立即触发一次策展人审查 |
| `run --sync` | 阻塞直到 LLM 处理完成 |
| `run --dry-run` | 仅预览——生成审查报告但不做任何修改 |
| `backup` | 手动创建 `~/.hermes/skills/` 的 tar.gz 快照（策展人在每次实际运行前也会自动创建快照） |
| `rollback` | 从快照恢复 `~/.hermes/skills/`（默认使用最新的快照） |
| `rollback --list` | 列出可用的快照 |
| `rollback --id &lt;ts&gt;` | 按 ID 恢复指定的快照 |
| `rollback -y` | 跳过确认提示 |
| `pause` | 暂停策展人，直到恢复 |
| `resume` | 恢复已暂停的策展人 |
| `pin &lt;skill&gt;` | 固定某个技能，使策展人永远不会自动转换它 |
| `unpin &lt;skill&gt;` | 取消固定某个技能 |
| `restore &lt;skill&gt;` | 恢复一个已归档的技能 |

在全新安装时，第一次计划执行会延迟一个完整的 `interval_hours`（默认 7 天）——网关不会在 `hermes update` 后的第一个 tick 立即执行策展。在此之前，可以使用 `hermes curator run --dry-run` 进行预览。

有关行为和配置，请参见[策展人](../user-guide/features/curator.md)。

## `hermes fallback` {#hermes-fallback}

```bash
hermes fallback <子命令>
```

管理回退提供者链。当主模型因速率限制、过载或连接错误而失败时，会按顺序尝试回退提供者。

| 子命令 | 描述 |
|--------|------|
| `list`（别名：`ls`） | 显示当前的回退链（未指定子命令时的默认行为） |
| `add` | 选择一个提供者 + 模型（与 `hermes model` 相同的选择器）并追加到链中 |
| `remove`（别名：`rm`） | 从链中选择一个条目删除 |
| `clear` | 删除所有回退条目 |

请参见[回退提供者](../user-guide/features/fallback-providers.md)。

## `hermes hooks` {#hermes-hooks}

```bash
hermes hooks <子命令>
```

检查在 `~/.hermes/config.yaml` 中声明的 shell 脚本钩子，用模拟负载测试它们，并管理位于 `~/.hermes/shell-hooks-allowlist.json` 的首次使用同意白名单。

| 子命令 | 描述 |
|--------|------|
| `list`（别名：`ls`） | 列出已配置的钩子，包括匹配器、超时和同意状态 |
| `test &lt;event&gt;` | 针对模拟负载触发所有匹配 `&lt;event&gt;` 的钩子 |
| `revoke`（别名：`remove`、`rm`） | 移除某个命令的白名单条目（下次重启生效） |
| `doctor` | 检查每个已配置的钩子：可执行位、白名单、mtime 漂移、JSON 有效性以及模拟运行时间 |

有关事件签名和负载格式，请参见[钩子](../user-guide/features/hooks.md)。
## `hermes memory` {#hermes-memory}

```bash
hermes memory <子命令>
```

设置和管理外部记忆提供者插件。可用的提供者：honcho、openviking、mem0、hindsight、holographic、retaindb、byterover、supermemory。一次只能激活一个外部提供者。内置记忆（MEMORY.md/USER.md）始终处于激活状态。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `setup` | 交互式提供者选择和配置。 |
| `status` | 显示当前记忆提供者配置。 |
| `off` | 禁用外部提供者（仅使用内置）。 |

:::info 提供者专属子命令
当外部记忆提供者处于激活状态时，它可能会注册自己的顶级 `hermes &lt;provider&gt;` 命令，用于提供者专属管理（例如，当 Honcho 激活时使用 `hermes honcho`）。未激活的提供者不会暴露其子命令。运行 `hermes --help` 查看当前已接入的命令。
:::
<a id="provider-specific-subcommands"></a>

## `hermes acp` {#hermes-acp}

```bash
hermes acp
```

将 Hermes 作为 ACP（Agent 客户端协议）stdio 服务器启动，用于编辑器集成。

相关入口点：

```bash
hermes-acp
python -m acp_adapter
```

首先安装支持：

```bash
pip install -e '.[acp]'
```

参见 [ACP 编辑器集成](../user-guide/features/acp.md) 和 [ACP 内部机制](../developer-guide/acp-internals.md)。

## `hermes mcp` {#hermes-mcp}

```bash
hermes mcp <子命令>
```

管理 MCP（模型上下文协议）服务器配置，并将 Hermes 作为 MCP 服务器运行。

| 子命令 | 描述 |
|------------|-------------|
| `serve [-v\|--verbose]` | 将 Hermes 作为 MCP 服务器运行——向其他 Agent 暴露对话。 |
| `add &lt;name&gt; [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加一个 MCP 服务器，并自动发现工具。 |
| `remove &lt;name&gt;`（别名：`rm`） | 从配置中移除一个 MCP 服务器。 |
| `list`（别名：`ls`） | 列出已配置的 MCP 服务器。 |
| `test &lt;name&gt;` | 测试与 MCP 服务器的连接。 |
| `configure &lt;name&gt;`（别名：`config`） | 切换服务器的工具选择。 |

参见 [MCP 配置参考](./mcp-config-reference.md)、[将 MCP 与 Hermes 结合使用](../guides/use-mcp-with-hermes.md) 和 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins` {#hermes-plugins}

```bash
hermes plugins [子命令]
```

统一插件管理——通用插件、记忆提供者和上下文引擎集中管理。运行 `hermes plugins` 而不带子命令会打开一个复合交互式屏幕，包含两个部分：

- **通用插件** — 多选复选框，用于启用/禁用已安装的插件
- **提供者插件** — 用于记忆提供者和上下文引擎的单选配置。在一个类别上按 ENTER 键可打开单选选择器。

| 子命令 | 描述 |
|------------|-------------|
| *(无)* | 复合交互式 UI——通用插件开关 + 提供者插件配置。 |
| `install &lt;identifier&gt; [--force]` | 从 Git URL 或 `owner/repo` 安装插件。 |
| `update &lt;name&gt;` | 拉取已安装插件的最新更改。 |
| `remove &lt;name&gt;`（别名：`rm`、`uninstall`） | 移除已安装的插件。 |
| `enable &lt;name&gt;` | 启用一个已禁用的插件。 |
| `disable &lt;name&gt;` | 禁用一个插件而不移除它。 |
| `list`（别名：`ls`） | 列出已安装的插件及其启用/禁用状态。 |
Provider 插件选择会保存到 `config.yaml`：
- `memory.provider` — 当前使用的 memory provider（空值表示仅使用内置）
- `context.engine` — 当前使用的 context engine（`"compressor"` 为内置默认值）

通用插件禁用列表存储在 `config.yaml` 的 `plugins.disabled` 下。

参见 [插件](../user-guide/features/plugins.md) 和 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。

## `hermes tools` {#hermes-tools}

```bash
hermes tools [--summary]
```

| 选项 | 说明 |
|--------|-------------|
| `--summary` | 打印当前已启用的工具摘要并退出。 |

不带 `--summary` 时，会启动交互式按平台工具配置界面。

## `hermes sessions` {#hermes-sessions}

```bash
hermes sessions <子命令>
```

子命令：

| 子命令 | 说明 |
|------------|-------------|
| `list` | 列出最近的会话。 |
| `browse` | 交互式会话选择器，支持搜索和恢复。 |
| `export <输出路径> [--session-id ID]` | 将会话导出为 JSONL 格式。 |
| `delete <会话ID>` | 删除一个会话。 |
| `prune` | 删除旧会话。 |
| `stats` | 显示会话存储统计信息。 |
| `rename <会话ID> <标题>` | 设置或更改会话标题。 |

## `hermes insights` {#hermes-insights}

```bash
hermes insights [--days N] [--source 平台]
```

| 选项 | 说明 |
|--------|-------------|
| `--days &lt;n&gt;` | 分析最近 `n` 天（默认：30）。 |
| `--source <平台>` | 按来源过滤，例如 `cli`、`telegram` 或 `discord`。 |

## `hermes claw` {#hermes-claw}

```bash
hermes claw migrate [选项]
```

将你的 OpenClaw 配置迁移到 Hermes。从 `~/.openclaw`（或自定义路径）读取，并写入 `~/.hermes`。自动检测旧版目录名（`~/.clawdbot`、`~/.moltbot`）和配置文件名称（`clawdbot.json`、`moltbot.json`）。

| 选项 | 说明 |
|--------|-------------|
| `--dry-run` | 预览将要迁移的内容，不实际写入任何文件。 |
| `--preset <名称>` | 迁移预设：`full`（所有兼容设置）或 `user-data`（排除基础设施配置）。两种预设均不导入密钥——需显式传递 `--migrate-secrets`。 |
| `--overwrite` | 冲突时覆盖现有 Hermes 文件（默认：当计划存在冲突时拒绝执行）。 |
| `--migrate-secrets` | 在迁移中包含 API 密钥。即使在 `--preset full` 下也需要。 |
| `--no-backup` | 跳过迁移前对 `~/.hermes/` 的 zip 快照（默认情况下，在应用迁移前会将一个恢复点归档写入 `~/.hermes/backups/pre-migration-*.zip`；可通过 `hermes import` 恢复）。 |
| `--source <路径>` | 自定义 OpenClaw 目录（默认：`~/.openclaw`）。 |
| `--workspace-target <路径>` | 工作区指令（AGENTS.md）的目标目录。 |
| `--skill-conflict <模式>` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

### 迁移内容 {#what-gets-migrated}

迁移涵盖 30 多个类别，包括角色、记忆、技能、模型提供商、消息平台、Agent 行为、会话策略、MCP 服务器、TTS 等。项目要么**直接导入**到 Hermes 的对应项中，要么**归档**以供手动审查。
**直接导入：** SOUL.md, MEMORY.md, USER.md, AGENTS.md, skills（4个源代码目录），默认模型，自定义提供者，MCP服务器，消息平台令牌和允许列表（Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost），agent 默认值（reasoning effort、compression、human delay、timezone、sandbox），会话重置策略，审批规则，TTS配置，浏览器设置，工具设置，执行超时，命令允许列表，网关配置以及来自3个来源的API密钥。

**归档供手动审查：** Cron任务，插件，hooks/webhooks，记忆后端（QMD），技能注册表配置，UI/身份，日志记录，多 Agent 设置，频道绑定，IDENTITY.md，TOOLS.md，HEARTBEAT.md，BOOTSTRAP.md。

**API 密钥解析** 按优先级顺序检查三个来源：config 值 → `~/.openclaw/.env` → `auth-profiles.json`。所有令牌字段支持纯字符串、环境变量模板（`${VAR}`）和 SecretRef 对象。

有关完整的配置键映射、SecretRef 处理细节以及迁移后检查清单，请参阅 **[完整迁移指南](../guides/migrate-from-openclaw.md)**。

<a id="examples"></a>
### 示例

```bash
# Preview what would be migrated
hermes claw migrate --dry-run

# Full migration (all compatible settings, no secrets)
hermes claw migrate --preset full

# Full migration including API keys
hermes claw migrate --preset full --migrate-secrets

# Migrate user data only (no secrets), overwrite conflicts
hermes claw migrate --preset user-data --overwrite

# Migrate from a custom OpenClaw path
hermes claw migrate --source /home/user/old-openclaw
```

## `hermes dashboard` {#hermes-dashboard}

```bash
hermes dashboard [options]
```

启动 Web 仪表盘——一个基于浏览器的用户界面，用于管理配置、API 密钥和监控会话。需要 `pip install hermes-agent[web]`（FastAPI + Uvicorn）。完整文档请参见 [Web Dashboard](/user-guide/features/web-dashboard)。

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--port` | `9119` | Web 服务器运行端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |

```bash
# 默认——打开浏览器到 http://127.0.0.1:9119
hermes dashboard

# 自定义端口，不打开浏览器
hermes dashboard --port 8080 --no-open
```

## `hermes profile` {#hermes-profile}

```bash
hermes profile <subcommand>
```

管理配置文件——多个独立的 Hermes 实例，每个实例有自己的配置、会话、技能和主目录。

| 子命令 | 说明 |
|--------|------|
| `list` | 列出所有配置文件。 |
| `use &lt;name&gt;` | 设置一个固定的默认配置文件。 |
| `create &lt;name&gt; [--clone] [--clone-all] [--clone-from &lt;source&gt;] [--no-alias]` | 创建一个新的配置文件。`--clone` 从活动配置文件复制 config、`.env` 和 `SOUL.md`。`--clone-all` 复制所有状态。`--clone-from` 指定源配置文件。 |
| `delete &lt;name&gt; [-y]` | 删除一个配置文件。 |
| `show &lt;name&gt;` | 显示配置文件的详细信息（主目录、配置等）。 |
| `alias &lt;name&gt; [--remove] [--name NAME]` | 管理包装脚本以便快速访问配置文件。 |
| `rename &lt;old&gt; &lt;new&gt;` | 重命名一个配置文件。 |
| `export &lt;name&gt; [-o FILE]` | 将配置文件导出为 `.tar.gz` 存档。 |
| `import &lt;archive&gt; [--name NAME]` | 从 `.tar.gz` 存档导入配置文件。 |
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
hermes completion [bash|zsh|fish]
```

将 shell 补全脚本输出到标准输出。将输出内容 source 到你的 shell 配置文件中，即可为 Hermes 命令、子命令和配置文件名称启用 Tab 补全。

示例：

```bash
# Bash
hermes completion bash >> ~/.bashrc

# Zsh
hermes completion zsh >> ~/.zshrc

# Fish
hermes completion fish > ~/.config/fish/completions/hermes.fish
```

## `hermes update` {#hermes-update}

```bash
hermes update [--check] [--backup] [--restart-gateway]
```

拉取最新的 `hermes-agent` 代码，并在你的 venv 中重新安装依赖，然后重新运行安装后钩子（MCP 服务器、技能同步、补全安装）。可以在正在运行的安装上安全执行。

| 选项 | 描述 |
|--------|-------------|
| `--check` | 并排打印当前提交和最新的 `origin/main` 提交，如果同步则退出码为 0，如果落后则退出码为 1。不会拉取、安装或重启任何内容。 |
| `--backup` | 在拉取之前，创建 `HERMES_HOME`（配置、认证、会话、技能、配对数据）的带标签的预更新快照。默认**关闭**——之前的始终备份行为会在大型 home 目录上每次更新增加几分钟。可以通过在 `config.yaml` 中设置 `update.backup: true` 永久开启。 |
| `--restart-gateway` | 成功更新后，重启正在运行的网关服务。如果安装了多个配置文件，则隐含 `--all` 语义。 |

额外行为：

- **配对数据快照。** 即使 `--backup` 关闭，`hermes update` 也会在 `git pull` 之前对 `~/.hermes/pairing/` 和飞书评论规则进行轻量级快照。如果拉取覆盖了你正在编辑的文件，可以使用 `hermes backup restore --state pre-update` 回滚。
- **旧版 `hermes.service` 警告。** 如果 Hermes 检测到重命名前的 `hermes.service` systemd 单元（而不是当前的 `hermes-gateway.service`），它会打印一次迁移提示，以便你避免 flap-loop 问题。
- **退出码。** `0` 表示成功，`1` 表示拉取/安装/安装后错误，`2` 表示阻止 `git pull` 的意外工作树更改。

## `hermes fallback` {#hermes-fallback}

```bash
hermes fallback           # 交互式管理器
```

管理回退提供商链（当你的主要提供商遇到速率限制或返回致命错误时使用），无需手动编辑 `config.yaml`。复用 `hermes model` 中的提供商选择器——相同的提供商列表、相同的凭据提示、相同的验证。

典型会话：

1. 按 `a` 添加回退 → 选择一个提供商（基于 OAuth 的提供商将打开浏览器；API 密钥提供商将提示输入密钥），然后选择具体模型。
2. 使用 `↑`/`↓` 重新排序回退（列表中的第一个会首先被尝试）。
3. 按 `d` 移除一个。

所有更改都会持久化到 `config.yaml` 中 `model:` 下的 `fallback_providers:`。与[凭据池](/user-guide/features/credential-pools)交互：凭据池在*一个*提供商内部轮换密钥，回退则完全切换到*另一个*提供商。
关于行为细节以及与 `fallback_model`（旧版单回退键）的交互，请参见[回退提供者](/user-guide/features/fallback-providers)。

## 维护命令 {#maintenance-commands}

| 命令 | 描述 |
|---------|-------------|
| `hermes version` | 打印版本信息。 |
| `hermes update` | 拉取最新更改并重新安装依赖。 |
| `hermes uninstall [--full] [--yes]` | 移除 Hermes，可选择删除所有配置/数据。 |

## 另请参阅 {#see-also}

- [斜杠命令参考](./slash-commands.md)
- [CLI 接口](../user-guide/cli.md)
- [会话](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)
