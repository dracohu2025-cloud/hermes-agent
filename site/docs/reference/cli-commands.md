---
sidebar_position: 1
title: "CLI 命令参考"
description: "Hermes 终端命令及命令族的权威参考"
---

<a id="cli-commands-reference"></a>
# CLI 命令参考

本页介绍的是你在 shell 中运行的**终端命令**。

关于聊天中的斜杠命令，请参见[斜杠命令参考](./slash-commands.md)。

<a id="global-entrypoint"></a>
## 全局入口点

```bash
hermes [global-options] <command> [subcommand/options]
```

<a id="global-options"></a>
### 全局选项

| 选项 | 说明 |
|--------|-------------|
| `--version`, `-V` | 显示版本并退出。 |
| `--profile &lt;name&gt;`, `-p &lt;name&gt;` | 选择本次调用使用的 Hermes 配置文件。会覆盖 `hermes profile use` 设置的粘性默认值。 |
| `--resume &lt;session&gt;`, `-r &lt;session&gt;` | 通过 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近的会话，或恢复标题匹配的最近会话。 |
| `--worktree`, `-w` | 在隔离的 git worktree 中启动，用于并行 Agent 工作流。 |
| `--yolo` | 绕过危险命令的批准提示。 |
| `--pass-session-id` | 将会话 ID 包含在 Agent 的系统提示中。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml`，回退到内置默认值。`.env` 中的凭据仍会加载。 |
| `--ignore-rules` | 跳过 `AGENTS.md`、`SOUL.md`、`.cursorrules`、记忆和预加载技能的自动注入。 |
| `--tui` | 启动 [TUI](../user-guide/tui.md) 而非经典 CLI。等同于 `HERMES_TUI=1`。 |
| `--dev` | 与 `--tui` 一起使用：通过 `tsx` 直接运行 TypeScript 源码，而非预构建的包（适用于 TUI 贡献者）。 |

<a id="top-level-commands"></a>
## 顶层命令

| 命令 | 用途 |
|---------|---------|
| `hermes chat` | 与 Agent 进行交互式或一次性聊天。 |
| `hermes model` | 交互式选择默认提供商和模型。 |
| `hermes fallback` | 管理主模型出错时尝试的备用提供商。 |
| `hermes gateway` | 运行或管理消息网关服务。 |
| `hermes proxy` | 本地 OpenAI 兼容代理，用于附加 OAuth 提供商凭据。参见[订阅代理](../user-guide/features/subscription-proxy.md)。 |
| `hermes lsp` | 管理语言服务器协议集成（write_file/patch 的语义诊断）。 |
| `hermes setup` | 全部或部分配置的交互式设置向导。 |
| `hermes whatsapp` | 配置并配对 WhatsApp 桥接。 |
| `hermes slack` | Slack 辅助工具（当前：生成应用清单，使每个命令成为原生斜杠命令）。 |
| `hermes auth` | 管理凭据——添加、列出、删除、重置、设置策略。处理 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已弃用**——请改用 `hermes auth`。 |
| `hermes status` | 显示 Agent、认证和平台状态。 |
| `hermes cron` | 检查并触发 cron 调度器。 |
| `hermes kanban` | 多配置文件协作看板（任务、链接、调度器）。 |
| `hermes webhook` | 管理用于事件驱动激活的动态 webhook 订阅。 |
| `hermes hooks` | 检查、批准或删除 `config.yaml` 中声明的 shell 脚本钩子。 |
| `hermes doctor` | 诊断配置和依赖问题。 |
| `hermes dump` | 生成可复制粘贴的设置摘要，用于支持/调试。 |
| `hermes debug` | 调试工具——上传日志和系统信息以获取支持。 |
| `hermes backup` | 将 Hermes 主目录备份为 zip 文件。 |
| `hermes checkpoints` | 检查/修剪/清理 `~/.hermes/checkpoints/`（`/rollback` 使用的影子存储）。无参数运行可查看状态概览。 |
| `hermes import` | 从 zip 文件恢复 Hermes 备份。 |
| `hermes logs` | 查看、跟踪和过滤 Agent/网关/错误日志文件。 |
| `hermes config` | 显示、编辑、迁移和查询配置文件。 |
| `hermes pairing` | 批准或撤销消息配对码。 |
| `hermes skills` | 浏览、安装、发布、审计和配置技能。 |
| `hermes bundles` | 将多个技能分组到单个 `/&lt;name&gt;` 斜杠命令下。参见[技能包](../user-guide/features/skills.md#skill-bundles)。 |
| `hermes curator` | 后台技能维护——状态、运行、暂停、固定。参见[策展人](../user-guide/features/curator.md)。 |
| `hermes memory` | 配置外部记忆提供商。插件特定的子命令（例如 `hermes honcho`）在其提供商激活时自动注册。 |
| `hermes acp` | 将 Hermes 作为 ACP 服务器运行，用于编辑器集成。 |
| `hermes mcp` | 管理 MCP 服务器配置，并将 Hermes 作为 MCP 服务器运行。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、移除）。 |
| `hermes tools` | 按平台配置启用的工具。 |
| `hermes computer-use` | 安装或检查 cua-driver 后端（macOS 计算机使用）。 |
| `hermes sessions` | 浏览、导出、修剪、重命名和删除会话。 |
| `hermes insights` | 显示令牌/成本/活动分析。 |
| `hermes claw` | OpenClaw 迁移辅助工具。 |
| `hermes dashboard` | 启动 Web 仪表板，用于管理配置、API 密钥和会话。 |
| `hermes profile` | 管理配置文件——多个隔离的 Hermes 实例。 |
| `hermes completion` | 打印 shell 补全脚本（bash/zsh/fish）。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新代码并重新安装依赖（git 安装），或检查 PyPI 并执行 `pip install --upgrade`（pip 安装）。`--check` 预览但不安装；`--backup` 在拉取前创建 `HERMES_HOME` 快照。 |
| `hermes uninstall` | 从系统中移除 Hermes。 |
<a id="hermes-chat"></a>
## `hermes chat`

```bash
hermes chat [options]
```

常用选项：

| 选项 | 说明 |
|------|------|
| `-q`, `--query "..."` | 单次、非交互式提示。 |
| `-m`, `--model &lt;model&gt;` | 覆盖本次运行的模型。 |
| `-t`, `--toolsets &lt;csv&gt;` | 启用一组以逗号分隔的工具集。 |
| `--provider &lt;provider&gt;` | 强制指定提供商：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot-acp`、`copilot`、`anthropic`、`gemini`、`google-gemini-cli`、`huggingface`、`novita`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`alibaba`、`alibaba-coding-plan`（别名 `alibaba_coding`）、`deepseek`、`nvidia`、`ollama-cloud`、`xai`（别名 `grok`）、`xai-oauth`（别名 `grok-oauth`）、`qwen-oauth`、`bedrock`、`opencode-zen`、`opencode-go`、`ai-gateway`、`azure-foundry`、`lmstudio`、`stepfun`、`tencent-tokenhub`（别名 `tencent`、`tokenhub`）。 |
| `-s`, `--skills &lt;name&gt;` | 预加载一个或多个技能到会话中（可重复使用或逗号分隔）。 |
| `-v`, `--verbose` | 详细输出。 |
| `-Q`, `--quiet` | 编程模式：隐藏横幅/加载动画/工具预览。 |
| `--image &lt;path&gt;` | 将本地图片附加到单次查询中。 |
| `--resume &lt;session&gt;` / `--continue [name]` | 直接从 `chat` 恢复一个会话。 |
| `--worktree` | 为本次运行创建一个隔离的 git 工作树。 |
| `--checkpoints` | 在破坏性文件更改前启用文件系统检查点。 |
| `--yolo` | 跳过审批提示。 |
| `--pass-session-id` | 将会话 ID 传入系统提示。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml`，使用内置默认值。`.env` 中的凭据仍会加载。适用于隔离的 CI 运行、可重现的 bug 报告以及第三方集成。 |
| `--ignore-rules` | 跳过 `AGENTS.md`、`SOUL.md`、`.cursorrules`、持久记忆和预加载技能的自动注入。结合 `--ignore-user-config` 可实现完全隔离运行。 |
| `--source &lt;tag&gt;` | 会话源标签，用于过滤（默认：`cli`）。第三方集成使用 `tool`，以免出现在用户会话列表中。 |
| `--max-turns &lt;N&gt;` | 每个对话轮次的最大工具调用迭代次数（默认：90，或配置中的 `agent.max_turns`）。 |

示例：

```bash
hermes
hermes chat -q "总结最新的 PR"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "仅返回 JSON"
hermes chat --worktree -q "审查此仓库并提 PR"
hermes chat --ignore-user-config --ignore-rules -q "在不使用个人配置的情况下复现"
```

<a id="hermes-z-scripted-one-shot"></a>
### `hermes -z &lt;prompt&gt;` — 脚本式单次执行

对于编程调用者（Shell 脚本、CI、cron、通过管道传入提示的父进程），`hermes -z` 是最纯粹的单次执行入口：**输入单一提示，输出最终响应文本，stdout 和 stderr 上无其他内容。** 没有横幅、没有加载动画、没有工具预览、没有 `Session:` 行——只有 Agent 的最终回复，以纯文本形式呈现。
```bash
hermes -z "法国的首都是什么？"
# → 巴黎。

# 父脚本可以干净地捕获响应：
answer=$(hermes -z "总结一下" < /path/to/file.txt)
```

单次运行覆盖（不会修改 `~/.hermes/config.yaml`）：

| 标志 | 等效环境变量 | 用途 |
|---|---|---|
| `-m` / `--model &lt;model&gt;` | `HERMES_INFERENCE_MODEL` | 覆盖本次运行的模型 |
| `--provider &lt;provider&gt;` | `HERMES_INFERENCE_PROVIDER` | 覆盖本次运行的提供商 |

```bash
hermes -z "…" --provider openrouter --model openai/gpt-5.5
# 或者：
HERMES_INFERENCE_MODEL=anthropic/claude-sonnet-4.6 hermes -z "…"
```

相同的 Agent、相同的工具、相同的技能——只是去掉了所有交互/外观层。如果你也需要在转录中看到工具输出，请改用 `hermes chat -q`；`-z` 明确用于“我只想要最终答案”。

<a id="hermes-model"></a>
## `hermes model`

交互式提供商 + 模型选择器。**这是用于添加新提供商、设置 API 密钥和运行 OAuth 流程的命令。** 在终端中运行它——而不是在活跃的 Hermes 聊天会话内部。

```bash
hermes model
```

当你想要以下操作时使用此命令：
- **添加新提供商**（OpenRouter、Anthropic、Copilot、DeepSeek、自定义等）
- 登录支持 OAuth 的提供商（Anthropic、Copilot、Codex、Nous Portal）
- 输入或更新 API 密钥
- 从提供商特定的模型列表中选择
- 配置自定义/自托管端点
- 将新的默认设置保存到配置中

:::warning hermes model 与 /model 的区别
<a id="hermes-model-vs-model-know-the-difference"></a>
**`hermes model`**（在终端中运行，不在任何 Hermes 会话内）是**完整的提供商设置向导**。它可以添加新提供商、运行 OAuth 流程、提示输入 API 密钥以及配置端点。

**`/model`**（在活跃的 Hermes 聊天会话内输入）只能**在已设置好的提供商和模型之间切换**。它无法添加新提供商、运行 OAuth 或提示输入 API 密钥。

**如果你需要添加新提供商：** 先退出 Hermes 会话（`Ctrl+C` 或 `/quit`），然后在终端提示符下运行 `hermes model`。
:::

<a id="model-slash-command-mid-session"></a>
### `/model` 斜杠命令（会话中）

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
/model claude-sonnet-4 --global     # 切换并保存为新的默认设置
```

<a id="what-if-i-only-see-openrouter-models"></a>
:::info 为什么我只看到 OpenRouter 模型？
如果你只配置了 OpenRouter，`/model` 将只显示 OpenRouter 模型。要添加其他提供商（Anthropic、DeepSeek、Copilot 等），请退出会话并在终端中运行 `hermes model`。
:::
Provider 和 base URL 的更改会自动持久化到 `config.yaml` 中。当切换离开自定义端点时，过时的 base URL 会被清除，以防止它泄漏到其他 provider 中。

<a id="hermes-gateway"></a>
## `hermes gateway`

```bash
hermes gateway <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `run` | 在前台运行 gateway。推荐用于 WSL、Docker 和 Termux。 |
| `start` | 启动已安装的 systemd/launchd 后台服务。 |
| `stop` | 停止服务（或前台进程）。 |
| `restart` | 重启服务。 |
| `status` | 显示服务状态。 |
| `list` | 列出**所有配置文件**以及每个配置文件的 gateway 当前是否正在运行（有 PID 时显示）。当你同时运行多个配置文件并想一览全局时非常方便。 |
| `install` | 安装为 systemd（Linux）或 launchd（macOS）后台服务。 |
| `uninstall` | 移除已安装的服务。 |
| `setup` | 交互式消息平台设置。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--all` | 在 `start` / `restart` / `stop` 时：作用于**每个配置文件的** gateway，而不仅仅是当前激活的 `HERMES_HOME`。如果你同时运行多个配置文件并想在 `hermes update` 后全部重启，这个选项很有用。 |

:::tip WSL 用户
使用 `hermes gateway run` 而不是 `hermes gateway start`——WSL 的 systemd 支持不可靠。将其包装在 tmux 中以保持持久性：`tmux new -s hermes 'hermes gateway run'`。详情请参阅 [WSL 常见问题](/reference/faq#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails)。
<a id="wsl-users"></a>
:::

<a id="hermes-lsp"></a>
## `hermes lsp`

```bash
hermes lsp <子命令>
```

管理语言服务器协议集成。LSP 在后台运行真实的语言服务器（pyright、gopls、rust-analyzer 等），并将其诊断结果输入到 `write_file` 和 `patch` 使用的写入后检查中。受 git 工作区检测限制——LSP 仅在当前工作目录或编辑的文件位于 git 工作树内时运行。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `status` | 显示服务状态、已配置的服务器、安装状态。 |
| `list` | 打印受支持服务器的注册表。传递 `--installed-only` 可跳过缺失的服务器。 |
| `install &lt;id&gt;` | 主动安装一个服务器的二进制文件。 |
| `install-all` | 安装所有具有已知自动安装方法的服务器。 |
| `restart` | 拆除正在运行的客户端，以便下次编辑时重新启动。 |
| `which &lt;id&gt;` | 打印一个服务器的已解析二进制路径。 |

请参阅 [LSP — 语义诊断](/user-guide/features/lsp) 获取完整指南、支持的语言和配置选项。

<a id="hermes-setup"></a>
## `hermes setup`

```bash
hermes setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset] [--quick] [--reconfigure]
```

**首次运行：** 启动首次使用向导。

**回头用户（已配置）：** 直接进入完整的重新配置向导——每个提示都会显示你当前的值作为默认值，按 Enter 键保留或输入新值。没有菜单。

跳转到某个部分而不是完整的向导：
| 章节 | 描述 |
|---------|-------------|
| `model` | 提供商和模型设置。 |
| `terminal` | 终端后端和沙箱设置。 |
| `gateway` | 消息平台设置。 |
| `tools` | 按平台启用/禁用工具。 |
| `agent` | Agent 行为设置。 |

选项：

| 选项 | 描述 |
|--------|-------------|
| `--quick` | 对于回访用户：仅提示缺失或未设置的项目。跳过已配置好的项目。 |
| `--non-interactive` | 使用默认值/环境变量，无需提示。 |
| `--reset` | 设置前将配置重置为默认值。 |
| `--reconfigure` | 向后兼容的别名——现在在已有安装上直接运行 `hermes setup` 默认执行此操作。 |

<a id="hermes-whatsapp"></a>
## `hermes whatsapp`

```bash
hermes whatsapp
```

运行 WhatsApp 配对/设置流程，包括模式选择和二维码配对。

<a id="hermes-slack"></a>
## `hermes slack`

```bash
hermes slack manifest              # 打印清单到标准输出
hermes slack manifest --write      # 写入 ~/.hermes/slack-manifest.json
hermes slack manifest --slashes-only  # 仅输出 features.slash_commands 数组
```

生成一个 Slack 应用清单，将 `COMMAND_REGISTRY` 中的每个网关命令（`/btw`、`/stop`、`/model` 等）注册为一级 Slack 斜杠命令——与 Discord 和 Telegram 保持一致。将输出粘贴到你的 Slack 应用配置中，位置在 [https://api.slack.com/apps](https://api.slack.com/apps) → 你的应用 → **Features → App Manifest → Edit**，然后 **Save**。如果作用域或斜杠命令发生变化，Slack 会提示重新安装。

| 标志 | 默认值 | 用途 |
|------|---------|---------|
| `--write [PATH]` | stdout | 写入文件而不是标准输出。裸 `--write` 写入 `$HERMES_HOME/slack-manifest.json`。 |
| `--name NAME` | `Hermes` | Slack 中的机器人显示名称。 |
| `--description DESC` | 默认简介 | Slack 应用目录中显示的机器人描述。 |
| `--slashes-only` | 关闭 | 仅输出 `features.slash_commands`，用于合并到手动维护的清单中。 |

运行 `hermes slack manifest --write` 之后，如果执行了 `hermes update`，请再次运行以获取任何新命令。

<a id="hermes-login-hermes-logout-deprecated"></a>
## `hermes login` / `hermes logout` *(已弃用)*

:::caution
`hermes login` 已移除。请使用 `hermes auth` 管理 OAuth 凭据，使用 `hermes model` 选择提供商，或者使用 `hermes setup` 进行完整的交互式设置。
:::

<a id="hermes-auth"></a>
## `hermes auth`

管理同一提供商的密钥轮换凭据池。完整文档请参阅 [凭据池](/user-guide/features/credential-pools)。

```bash
hermes auth                                              # 交互式向导
hermes auth list                                         # 显示所有池
hermes auth list openrouter                              # 显示特定提供商
hermes auth add openrouter --api-key sk-or-v1-xxx        # 添加 API 密钥
hermes auth add anthropic --type oauth                   # 添加 OAuth 凭据
hermes auth remove openrouter 2                          # 按索引移除
hermes auth reset openrouter                             # 清除冷却时间
hermes auth status anthropic                             # 显示提供商的认证状态
hermes auth logout anthropic                             # 登出并清除存储的认证状态
hermes auth spotify                                      # 通过 PKCE 认证 Hermes 与 Spotify
```
子命令：`add`、`list`、`remove`、`reset`、`status`、`logout`、`spotify`。在不带子命令调用时，会启动交互式管理向导。

<a id="hermes-status"></a>
## `hermes status`

```bash
hermes status [--all] [--deep]
```

| 选项 | 描述 |
|--------|-------------|
| `--all` | 以可分享的脱敏格式显示所有详情。 |
| `--deep` | 执行更深入的检查，可能需要更长时间。 |

<a id="hermes-cron"></a>
## `hermes cron`

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示计划任务。 |
| `create` / `add` | 根据提示创建计划任务，可选择通过重复 `--skill` 参数附加一项或多项技能。 |
| `edit` | 更新任务的计划时间、提示、名称、投递方式、重复次数或附加的技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill`。 |
| `pause` | 暂停任务而不删除。 |
| `resume` | 恢复暂停的任务并计算其下一次运行时间。 |
| `run` | 在下一个调度器 tick 触发任务。 |
| `remove` | 删除计划任务。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 执行到期任务一次并退出。 |

<a id="hermes-kanban"></a>
## `hermes kanban`

```bash
hermes kanban [--board <slug>] <action> [options]
```

多用户、多项目协作看板。每个安装实例可以托管多个看板（每个项目、仓库或域一个）；每个看板是一个独立的队列，拥有自己的 SQLite 数据库和调度器作用域。新安装实例默认有一个名为 `default` 的看板，其数据库为 `~/.hermes/kanban.db`（为了向后兼容）；其他看板位于 `~/.hermes/kanban/boards/&lt;slug&gt;/kanban.db`。嵌入式网关调度器在每个 tick 中遍历所有看板。

**全局标志（适用于以下所有操作）：**

| 标志 | 用途 |
|------|---------|
| `--board &lt;slug&gt;` | 针对特定看板进行操作。默认为当前看板（通过 `hermes kanban boards switch` 设置、`HERMES_KANBAN_BOARD` 环境变量或 `default` 确定）。 |

**这是人类/脚本交互界面。** 由调度器生成的 Agent 工作进程通过专用的 `kanban_*` [工具集](/user-guide/features/kanban#how-workers-interact-with-the-board)（`kanban_show`、`kanban_complete`、`kanban_block`、`kanban_create`、`kanban_link`、`kanban_comment`、`kanban_heartbeat`；编排器配置文件还会获得 `kanban_list` 和 `kanban_unblock`）来驱动看板，而不是通过 `hermes kanban` 命令。工作进程的环境变量中锁定了 `HERMES_KANBAN_BOARD`，因此它们物理上无法看到其他看板。

| 操作 | 用途 |
|--------|---------|
| `init` | 如果 `kanban.db` 不存在则创建。幂等操作。 |
| `boards list` / `boards ls` | 列出所有看板及其任务计数。`--json`、`--all`（包含已归档的）。 |
| `boards create &lt;slug&gt;` | 创建新看板。标志：`--name`、`--description`、`--icon`、`--color`、`--switch`（设为当前看板）。`slug` 使用短横线命名，自动转换为小写。 |
| `boards switch &lt;slug&gt;` / `boards use` | 将 `&lt;slug&gt;` 持久化为当前看板（写入 `~/.hermes/kanban/current`）。 |
| `boards show` / `boards current` | 打印当前看板的名称、数据库路径和任务计数。 |
| `boards rename &lt;slug&gt; "&lt;name&gt;"` | 更改看板的显示名称。`slug` 不可变。 |
| `boards rm &lt;slug&gt;` | 归档（默认）或硬删除看板。`--delete` 跳过归档步骤。归档后的看板移动到 `boards/_archived/&lt;slug&gt;-&lt;ts&gt;/`。不允许对 `default` 执行此操作。 |
| `create "&lt;title&gt;"` | 在当前看板上创建新任务。标志：`--body`、`--assignee`、`--parent`（可重复）、`--workspace scratch\|worktree\|dir:&lt;path&gt;`、`--tenant`、`--priority`、`--triage`、`--idempotency-key`、`--max-runtime`、`--max-retries`、`--skill`（可重复）。 |
| `list` / `ls` | 列出当前看板上的任务。可通过 `--mine`、`--assignee`、`--status`、`--tenant`、`--archived`、`--json` 进行过滤。 |
| `show &lt;id&gt;` | 显示任务及其评论和事件。`--json` 提供机器可读输出。 |
| `assign &lt;id&gt; &lt;profile&gt;` | 分配或重新分配。使用 `none` 取消分配。任务运行中时拒绝操作。 |
| `link &lt;parent&gt; &lt;child&gt;` | 添加依赖关系。会检测循环依赖。两个任务必须在同一个看板上。 |
| `unlink &lt;parent&gt; &lt;child&gt;` | 移除依赖关系。 |
| `claim &lt;id&gt;` | 原子地声明一个就绪任务。打印解析后的工作区路径。 |
| `comment &lt;id&gt; "&lt;text&gt;"` | 追加评论。下一个声明该任务的工作进程将在其 `kanban_show()` 响应中读取该评论。 |
| `complete &lt;id&gt;` | 将任务标记为完成。标志：`--result`、`--summary`、`--metadata`。 |
| `block &lt;id&gt; "&lt;reason&gt;"` | 将任务标记为因需要人工输入而受阻。同时将原因作为评论追加。 |
| `schedule &lt;id&gt; "&lt;reason&gt;"` | 将时间延迟/后续工作存放在 `scheduled` 状态，使其不显示为人为阻塞项。 |
| `unblock &lt;id&gt;` | 将受阻或已调度的任务返回到就绪状态（如果依赖关系仍处于未关闭状态，则返回 `todo`）。 |
| `archive &lt;id&gt;` | 从默认列表中隐藏。`gc` 将移除临时工作区。 |
| `tail &lt;id&gt;` | 跟踪任务的事件流。 |
| `dispatch` | 对当前看板执行一次调度器遍历。标志：`--dry-run`、`--max N`、`--failure-limit N`、`--json`。 |
| `context &lt;id&gt;` | 打印工作进程将看到的完整上下文（标题 + 正文 + 父任务结果 + 评论）。 |
| `specify &lt;id&gt;` / `specify --all` | 通过辅助 LLM 将分诊列中的任务完善为具体规格（包含目标、方法、验收标准的标题和正文），然后将其提升为 `todo`。标志：`--tenant`（将 `--all` 限定到特定租户）、`--author`、`--json`。在 `config.yaml` 的 `auxiliary.triage_specifier` 下配置模型。 |
| `decompose &lt;id&gt;` / `decompose --all` | 将分诊列中的任务展开为子任务图，根据描述路由到专家配置文件（编排器驱动路径）。当 LLM 判断任务不适合展开时，回退到 specify 风格的单任务提升。标志与 `specify` 相同。在 `config.yaml` 的 `auxiliary.kanban_decomposer` 下配置模型。当 `kanban.auto_decompose: true`（默认值）时，也会在每个调度器 tick 自动运行。参见[自动与手动编排](/user-guide/features/kanban#auto-vs-manual-orchestration)。 |
| `gc` | 移除已归档任务的临时工作区。 |
示例：

```bash
# 创建第二个看板，并在不切换当前看板的情况下将任务添加到其中。
hermes kanban boards create atm10-server --name "ATM10 Server" --icon 🎮
hermes kanban --board atm10-server create "Restart server" --assignee ops

# 切换当前活跃看板以供后续调用。
hermes kanban boards switch atm10-server
hermes kanban list                  # 显示 atm10-server 的任务

# 归档看板（可恢复）或永久删除。
hermes kanban boards rm atm10-server
hermes kanban boards rm atm10-server --delete
```

看板解析顺序（优先级从高到低）：`--board &lt;slug&gt;` 标志 → `HERMES_KANBAN_BOARD` 环境变量 → `~/.hermes/kanban/current` 文件 → `default`。

所有操作也可以在网关中通过斜杠命令（`/kanban …`）执行，参数接口相同——包括 `boards` 子命令和 `--board` 标志。

关于完整设计——与 Cline Kanban / Paperclip / NanoClaw / Gemini Enterprise 的对比、八种协作模式、四个用户故事、并发正确性证明——请参见仓库中的 `docs/hermes-kanban-v1-spec.pdf` 或 [Kanban 用户指南](/user-guide/features/kanban)。

<a id="hermes-webhook"></a>
## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

管理用于事件驱动 Agent 激活的动态 webhook 订阅。需要在配置中启用 webhook 平台——如果未配置，将打印设置说明。

| 子命令 | 描述 |
|------------|-------------|
| `subscribe` / `add` | 创建 webhook 路由。返回 URL 和 HMAC 密钥，供你的服务配置使用。 |
| `list` / `ls` | 显示所有由 Agent 创建的订阅。 |
| `remove` / `rm` | 删除动态订阅。不会影响来自 config.yaml 的静态路由。 |
| `test` | 发送测试 POST 以验证订阅是否正常工作。 |

<a id="hermes-webhook-subscribe"></a>
### `hermes webhook subscribe`

```bash
hermes webhook subscribe <name> [options]
```

| 选项 | 描述 |
|--------|-------------|
| `--prompt` | 包含 `{dot.notation}` 负载引用的提示模板。 |
| `--events` | 接受的事件类型，逗号分隔（例如 `issues,pull_request`）。空值表示接受所有事件。 |
| `--description` | 人类可读的描述。 |
| `--skills` | 逗号分隔的技能名称列表，用于 Agent 运行。 |
| `--deliver` | 投递目标：`log`（默认）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台投递的目标聊天/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。如果省略，则自动生成。 |
| `--deliver-only` | 跳过 Agent——直接将渲染后的 `--prompt` 作为字面消息投递。零 LLM 成本，亚秒级投递。需要 `--deliver` 为实际目标（不能是 `log`）。 |

订阅持久化到 `~/.hermes/webhook_subscriptions.json` 文件中，webhook 适配器会热加载，无需重启网关。

<a id="hermes-doctor"></a>
## `hermes doctor`

```bash
hermes doctor [--fix]
```

| 选项 | 描述 |
|--------|-------------|
| `--fix` | 尽可能尝试自动修复。 |

<a id="hermes-dump"></a>
## `hermes dump`

```bash
hermes dump [--show-keys]
```
输出整个 Hermes 设置的紧凑纯文本摘要。专为复制粘贴到 Discord、GitHub Issue 或 Telegram 寻求支持而设计——没有 ANSI 颜色，没有特殊格式，只有数据。

| 选项 | 描述 |
|--------|-------------|
| `--show-keys` | 显示脱敏后的 API 密钥前缀（首尾各 4 个字符），而不是仅显示 `set`/`not set`。 |

<a id="what-it-includes"></a>
### 包含内容

| 部分 | 详情 |
|---------|---------|
| **头部** | Hermes 版本、发布日期、Git 提交哈希 |
| **环境** | 操作系统、Python 版本、OpenAI SDK 版本 |
| **身份** | 当前使用的配置文件名称、HERMES_HOME 路径 |
| **模型** | 配置的默认模型和提供商 |
| **终端** | 后端类型（local、docker、ssh 等） |
| **API 密钥** | 检查所有 22 个提供商/工具 API 密钥是否存在 |
| **功能** | 启用的工具集、MCP 服务器数量、内存提供商 |
| **服务** | 网关状态、已配置的消息平台 |
| **工作负载** | Cron 任务数量、已安装的技能数量 |
| **配置覆盖** | 与默认值不同的任何配置值 |

<a id="example-output"></a>
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

<a id="when-to-use"></a>
### 使用场景

- 在 GitHub 上报告 Bug —— 将 dump 粘贴到你的 Issue 中
- 在 Discord 中寻求帮助 —— 在代码块中分享
- 将自己的设置与他人进行比较
- 当某些功能不正常时进行快速检查

:::tip
`hermes dump` 专为分享而设计。如需交互式诊断，请使用 `hermes doctor`。如需可视化概览，请使用 `hermes status`。
:::

<a id="hermes-debug"></a>
## `hermes debug`

```bash
hermes debug share [options]
```

将调试报告（系统信息 + 最近的日志）上传到粘贴服务，并获取一个可分享的 URL。适用于快速支持请求 —— 包含帮助者诊断问题所需的一切信息。

| 选项 | 描述 |
|--------|-------------|
| `--lines &lt;N&gt;` | 每个日志文件包含的日志行数（默认：200）。 |
| `--expire &lt;days&gt;` | 粘贴内容的过期天数（默认：7）。 |
| `--local` | 在本地打印报告，而不是上传。 |

报告包含系统信息（操作系统、Python 版本、Hermes 版本）、最近的 Agent 和网关日志（每个文件限制 512 KB）以及脱敏后的 API 密钥状态。密钥始终会被脱敏 —— 不会上传任何机密信息。
尝试按顺序使用了粘贴服务：paste.rs、dpaste.com。

<a id="examples"></a>
### 示例

```bash
hermes debug share              # Upload debug report, print URL
hermes debug share --lines 500  # Include more log lines
hermes debug share --expire 30  # Keep paste for 30 days
hermes debug share --local      # Print report to terminal (no upload)
```

<a id="hermes-backup"></a>
## `hermes backup`

```bash
hermes backup [options]
```

创建一个包含 Hermes 配置、技能、会话和数据的 zip 归档。备份不包含 hermes-agent 代码库本身。

| 选项 | 描述 |
|--------|-------------|
| `-o`, `--output <路径>` | zip 文件的输出路径（默认：`~/hermes-backup-<时间戳>.zip`）。 |
| `-q`, `--quick` | 快速快照：仅包含关键状态文件（config.yaml、state.db、.env、auth、cron 任务）。比完整备份快得多。 |
| `-l`, `--label <名称>` | 快照的标签（仅与 `--quick` 一起使用）。 |

备份使用 SQLite 的 `backup()` API 进行安全拷贝，因此在 Hermes 运行时也能正常工作（WAL 模式安全）。

**zip 中排除的内容：**

- `*.db-wal`、`*.db-shm`、`*.db-journal` — SQLite 的 WAL / 共享内存 / 日志侧边文件。`*.db` 文件已通过 `sqlite3.backup()` 获得了一致快照；将正在运行的侧边文件一同打包会导致还原时看到半提交状态。
- `checkpoints/` — 每个会话的轨迹缓存。以哈希键存储并按会话重新生成；无论如何都无法干净地移植到另一个安装。
- `hermes-agent` 代码本身（这是用户数据备份，不是仓库快照）。

### 示例

```bash
hermes backup                           # Full backup to ~/hermes-backup-*.zip
hermes backup -o /tmp/hermes.zip        # Full backup to specific path
hermes backup --quick                   # Quick state-only snapshot
hermes backup --quick --label "pre-upgrade"  # Quick snapshot with label
```

<a id="hermes-checkpoints"></a>
## `hermes checkpoints`

```bash
hermes checkpoints [COMMAND]
```

检查和管理 `~/.hermes/checkpoints/` 下的影子 git 存储——即会话内 `/rollback` 命令背后的存储层。任何时候运行都是安全的；不需要 Agent 正在运行。

| 子命令 | 描述 |
|------------|-------------|
| `status`（默认） | 显示总大小、项目数以及每个项目的细分信息。单独的 `hermes checkpoints` 等效于该命令。 |
| `list` | `status` 的别名。 |
| `prune` | 强制清理——删除孤立和陈旧的项目，对存储进行垃圾回收，强制执行大小上限。忽略 24 小时幂等标记。 |
| `clear` | 删除整个检查点基础。不可逆；除非使用 `-f`，否则会要求确认。 |
| `clear-legacy` | 仅删除由 v1→v2 迁移产生的 `legacy-&lt;timestamp&gt;/` 归档。 |

<a id="options"></a>
### 选项

| 选项 | 子命令 | 描述 |
|--------|------------|-------------|
| `--limit N` | `status`、`list` | 最多列出的项目数（默认 20）。 |
| `--retention-days N` | `prune` | 删除 `last_touch` 早于 N 天的项目（默认 7）。 |
| `--max-size-mb N` | `prune` | 在清理孤立/陈旧项目后，删除每个项目中最旧的提交，直到总存储大小 ≤ N MB（默认 500）。 |
| `--keep-orphans` | `prune` | 跳过删除工作目录不再存在的项目。 |
| `-f`, `--force` | `clear`、`clear-legacy` | 跳过确认提示。 |
<a id="examples"></a>
### 示例

```bash
hermes checkpoints                                  # 状态概览
hermes checkpoints prune --retention-days 3         # 激进清理
hermes checkpoints prune --max-size-mb 200          # 一次性收紧大小限制
hermes checkpoints clear-legacy -f                  # 删除 v1 存档目录
hermes checkpoints clear -f                         # 清除所有内容
```

有关完整架构和会话内命令，请参阅 [检查点与 `/rollback`](../user-guide/checkpoints-and-rollback.md)。

<a id="hermes-import"></a>
## `hermes import`

```bash
hermes import <zipfile> [options]
```

将之前创建的 Hermes 备份恢复到你的 Hermes 主目录中。存档中的所有文件会覆盖 Hermes 主目录中的现有文件；`--force` 仅跳过当目标已存在 Hermes 安装时弹出的确认提示。

| 选项 | 描述 |
|--------|-------------|
| `-f`, `--force` | 跳过已存在安装的确认提示。 |

:::warning
在导入前停止网关，以避免与正在运行的进程发生冲突。
:::

### 示例
```bash
hermes import ~/hermes-backup-20260423.zip           # 覆盖现有配置前会提示确认
hermes import ~/hermes-backup-20260423.zip --force   # 直接覆盖，不提示
```

<a id="hermes-logs"></a>
## `hermes logs`

```bash
hermes logs [log_name] [options]
```

查看、跟踪和过滤 Hermes 日志文件。所有日志都存储在 `~/.hermes/logs/` 中（对于非默认配置文件，则为 `&lt;profile&gt;/logs/`）。

<a id="log-files"></a>
### 日志文件

| 名称 | 文件 | 捕获内容 |
|------|------|-----------------|
| `agent`（默认） | `agent.log` | 所有 Agent 活动 — API 调用、工具分发、会话生命周期（INFO 及以上级别） |
| `errors` | `errors.log` | 仅警告和错误 — agent.log 的过滤子集 |
| `gateway` | `gateway.log` | 消息网关活动 — 平台连接、消息分发、Webhook 事件 |

<a id="options"></a>
### 选项

| 选项 | 描述 |
|--------|-------------|
| `log_name` | 要查看的日志：`agent`（默认）、`errors`、`gateway`，或 `list` 以显示可用文件及其大小。 |
| `-n`, `--lines &lt;N&gt;` | 显示的行数（默认：50）。 |
| `-f`, `--follow` | 实时跟踪日志，类似 `tail -f`。按 Ctrl+C 停止。 |
| `--level &lt;LEVEL&gt;` | 显示的最低日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。 |
| `--session &lt;ID&gt;` | 过滤包含会话 ID 子串的行。 |
| `--since &lt;TIME&gt;` | 显示从某个相对时间点开始的行：`30m`、`1h`、`2d` 等。支持 `s`（秒）、`m`（分钟）、`h`（小时）、`d`（天）。 |
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

# 实时跟踪 errors.log，从 30 分钟前开始
hermes logs errors --since 30m -f

# 列出所有日志文件及其大小
hermes logs list
```
<a id="filtering"></a>
### 过滤

过滤器可以组合使用。当多个过滤器同时生效时，一条日志必须**全部**通过才会显示：

```bash
# 最近2小时内包含会话 "tg-12345" 的 WARNING+ 级别日志
hermes logs --level WARNING --since 2h --session tg-12345
```

当使用 `--since` 时，没有可解析时间戳的行也会被包含（它们可能是多行日志条目的续行）。当使用 `--level` 时，没有可检测级别的行也会被包含。

<a id="log-rotation"></a>
### 日志轮转

Hermes 使用 Python 的 `RotatingFileHandler`。旧日志会自动轮转——你会看到 `agent.log.1`、`agent.log.2` 等文件。`hermes logs list` 子命令会显示所有日志文件，包括已轮转的文件。

<a id="hermes-config"></a>
## `hermes config`

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
| `check` | 检查缺失或过时的配置。 |
| `migrate` | 交互式添加新引入的选项。 |

<a id="hermes-pairing"></a>
## `hermes pairing`

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示待处理和已批准的用户。 |
| `approve &lt;platform&gt; &lt;code&gt;` | 批准一个配对码。 |
| `revoke &lt;platform&gt; &lt;user-id&gt;` | 撤销某个用户的访问权限。 |
| `clear-pending` | 清除待处理的配对码。 |

<a id="hermes-skills"></a>
## `hermes skills`

```bash
hermes skills <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `browse` | 分页浏览技能注册表。 |
| `search` | 搜索技能注册表。 |
| `install` | 安装一个技能。 |
| `inspect` | 预览一个技能而不安装它。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 hub 技能是否有上游更新。 |
| `update` | 当上游有变更时重新安装 hub 技能。 |
| `audit` | 重新扫描已安装的 hub 技能。 |
| `reset` | 通过清除清单条目，解除被标记为 `user_modified` 的内置技能的卡住状态。使用 `--restore` 时，还会用内置版本替换用户副本。 |
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
hermes skills reset google-workspace
hermes skills reset google-workspace --restore --yes
```
Notes:
- `--force` 可以覆盖第三方/社区技能的非危险策略块。
- `--force` 不能覆盖 `dangerous` 扫描判定结果。
- `--source skills-sh` 搜索公共的 `skills.sh` 目录。
- `--source well-known` 让 Hermes 指向一个暴露了 `/.well-known/skills/index.json` 的站点。
- `--source browse-sh` 搜索 [browse.sh](https://browse.sh) 目录中 200 多个特定于浏览器的自动化技能。标识符格式如 `browse-sh/airbnb.com/search-listings-ddgioa`。
- 传入 `http(s)://…/*.md` 格式的 URL 会直接安装一个单文件 SKILL.md。当 frontmatter 中没有 `name:` 且 URL 的 slug 不是一个有效的标识符时，会通过交互式终端提示输入名称；非交互式界面（TUI 中的 `/skills install`、网关平台）则需要使用 `--name &lt;x&gt;` 代替。

<a id="hermes-bundles"></a>
## `hermes bundles`

```bash
hermes bundles <子命令>
```

技能包将多个技能组合在一个 `/<包名>` 斜杠命令下。调用技能包会将所有引用的技能加载到一条合并的用户消息中。存储位置：`~/.hermes/skill-bundles/&lt;slug&gt;.yaml`。关于 YAML 结构及行为，请参阅[技能包](../user-guide/features/skills.md#skill-bundles)。

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `list` | 列出已安装的技能包（未指定子命令时的默认操作） |
| `show &lt;name&gt;` | 显示指定技能包的名称、描述、技能列表及文件路径 |
| `create &lt;name&gt;` | 创建一个新技能包。可通过重复传递 `--skill &lt;id&gt;` 指定，也可省略参数进入交互式输入。可用选项：`--description`、`--instruction`、`--force`。 |
| `delete &lt;name&gt;` | 删除一个技能包文件 |
| `reload` | 重新扫描 `~/.hermes/skill-bundles/` 并报告新增/移除的技能包 |

示例：

```bash
hermes bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "后端功能工作"

hermes bundles list
hermes bundles show backend-dev
hermes bundles delete backend-dev
```

在聊天会话中，`/bundles` 列出已安装的技能包，`/<包名>` 则加载一个技能包。

<a id="hermes-curator"></a>
## `hermes curator`

```bash
hermes curator <子命令>
```

策展人（curator）是一个辅助模型的后台任务，它会定期审查 Agent 创建的技能，清理过时的技能，合并重复的技能，并归档废弃的技能。打包的技能和从中心安装的技能不会被修改。归档的技能是可恢复的；永远不会自动删除。

| 子命令 | 描述 |
|------------|-------------|
| `status` | 显示策展人状态及技能统计信息 |
| `run` | 立即触发一次策展人审查（会阻塞直到 LLM 处理完成） |
| `run --background` | 在后台线程中启动 LLM 处理，并立即返回 |
| `run --dry-run` | 仅预览——生成审查报告但不执行任何修改 |
| `backup` | 手动创建 `~/.hermes/skills/` 的 tar.gz 快照（策展人每次实际运行前也会自动创建快照） |
| `rollback` | 从快照恢复 `~/.hermes/skills/`（默认使用最新的快照） |
| `rollback --list` | 列出可用的快照 |
| `rollback --id &lt;ts&gt;` | 按 ID 恢复指定的快照 |
| `rollback -y` | 跳过确认提示 |
| `pause` | 暂停策展人，直到恢复 |
| `resume` | 恢复已暂停的策展人 |
| `pin &lt;skill&gt;` | 固定一个技能，使策展人永远不会自动将其转换 |
| `unpin &lt;skill&gt;` | 取消固定一个技能 |
| `restore &lt;skill&gt;` | 恢复一个归档的技能 |
| `archive &lt;skill&gt;` | 手动归档一个技能 |
| `prune` | 手动清理策展人通常会清理的技能 |
| `list-archived` | 列出已归档的技能（可通过 `restore` 恢复） |
全新安装后，第一次定时任务执行会推迟一个完整的 `interval_hours`（默认 7 天）——网关不会在 `hermes update` 后的第一个心跳周期立即执行整理操作。如果需要在此之前预览，可使用 `hermes curator run --dry-run`。

有关行为与配置，请参见 [Curator](../user-guide/features/curator.md)。

<a id="hermes-fallback"></a>
## `hermes fallback`

```bash
hermes fallback <subcommand>
```

管理回退（Fallback）提供者链。当主模型因速率限制、过载或连接错误而失败时，系统会按顺序尝试回退提供者。

| 子命令 | 说明 |
|------------|-------------|
| `list`（别名：`ls`） | 显示当前回退链（未指定子命令时的默认行为） |
| `add` | 选择一个提供者 + 模型（与 `hermes model` 相同的选择器），并追加到链中 |
| `remove`（别名：`rm`） | 选择要从链中删除的条目 |
| `clear` | 移除所有回退条目 |

请参见 [回退提供者](../user-guide/features/fallback-providers.md)。

<a id="hermes-hooks"></a>
## `hermes hooks`

```bash
hermes hooks <subcommand>
```

检查在 `~/.hermes/config.yaml` 中声明的 Shell 脚本钩子，对合成测试载荷进行验证，并管理位于 `~/.hermes/shell-hooks-allowlist.json` 的首次使用同意白名单。

| 子命令 | 说明 |
|------------|-------------|
| `list`（别名：`ls`） | 列出已配置的钩子，包含匹配器、超时时间和同意状态 |
| `test &lt;event&gt;` | 对所有匹配 `&lt;event&gt;` 的钩子触发一次合成载荷测试 |
| `revoke`（别名：`remove`、`rm`） | 移除某个命令的白名单条目（下次重启后生效） |
| `doctor` | 检查每个已配置的钩子：可执行权限、白名单、mtime 漂移、JSON 有效性以及合成执行计时 |

关于事件签名与载荷格式，请参见 [Hooks](../user-guide/features/hooks.md)。

<a id="hermes-memory"></a>
## `hermes memory`

```bash
hermes memory <subcommand>
```

设置并管理外部记忆提供者插件。可用的提供者：honcho、openviking、mem0、hindsight、holographic、retaindb、byterover、supermemory。同时只能激活一个外部提供者。内置记忆（MEMORY.md/USER.md）始终处于激活状态。

子命令：

| 子命令 | 说明 |
|------------|-------------|
| `setup` | 交互式提供者选择与配置。 |
| `status` | 显示当前记忆提供者配置。 |
| `off` | 禁用外部提供者（仅使用内置记忆）。 |

:::info 提供者专属子命令
<a id="provider-specific-subcommands"></a>
当一个外部记忆提供者被激活时，它可能会注册自己的顶层 `hermes &lt;provider&gt;` 命令，用于该提供者特有的管理（例如，当 Honcho 激活时会出现 `hermes honcho`）。未激活的提供者不会暴露其子命令。运行 `hermes --help` 可以查看当前已接入的命令。
:::

<a id="hermes-acp"></a>
## `hermes acp`

```bash
hermes acp
```

以 ACP（Agent Client Protocol）stdio 服务器模式启动 Hermes，用于编辑器集成。

相关的入口点：

```bash
hermes-acp
python -m acp_adapter
```

首先安装支持：

```bash
pip install -e '.[acp]'
```

请参见 [ACP 编辑器集成](../user-guide/features/acp.md) 和 [ACP 内部机制](../developer-guide/acp-internals.md)。
<a id="hermes-mcp"></a>
## `hermes mcp`

```bash
hermes mcp <子命令>
```

管理 MCP（模型上下文协议）服务器配置，并将 Hermes 作为 MCP 服务器运行。

| 子命令 | 描述 |
|------------|-------------|
| `serve [-v\|--verbose]` | 将 Hermes 作为 MCP 服务器运行 — 向其他 Agent 暴露对话。 |
| `add &lt;name&gt; [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | 添加 MCP 服务器，并自动发现工具。 |
| `remove &lt;name&gt;`（别名：`rm`） | 从配置中移除 MCP 服务器。 |
| `list`（别名：`ls`） | 列出已配置的 MCP 服务器。 |
| `test &lt;name&gt;` | 测试到 MCP 服务器的连接。 |
| `configure &lt;name&gt;`（别名：`config`） | 切换服务器的工具选择。 |
| `login &lt;name&gt;` | 强制重新认证基于 OAuth 的 MCP 服务器。 |

请参阅 [MCP 配置参考](./mcp-config-reference.md)、[使用 Hermes 与 MCP](../guides/use-mcp-with-hermes.md) 以及 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

<a id="hermes-plugins"></a>
## `hermes plugins`

```bash
hermes plugins [子命令]
```

统一的插件管理 — 通用插件、记忆提供者与上下文引擎集中管理。运行 `hermes plugins` 而不带子命令会打开一个包含两个部分的组合交互界面：

- **通用插件** — 多选复选框，用于启用/禁用已安装的插件
- **提供者插件** — 单选配置，用于记忆提供者与上下文引擎。在某个类别上按 ENTER 键可打开单选选择器。

| 子命令 | 描述 |
|------------|-------------|
| *(无)* | 组合交互 UI — 通用插件开关 + 提供者插件配置。 |
| `install &lt;identifier&gt; [--force]` | 从 Git URL 或 `owner/repo` 安装插件。 |
| `update &lt;name&gt;` | 拉取已安装插件的最新变更。 |
| `remove &lt;name&gt;`（别名：`rm`、`uninstall`） | 移除已安装的插件。 |
| `enable &lt;name&gt;` | 启用已禁用的插件。 |
| `disable &lt;name&gt;` | 禁用插件但不移除。 |
| `list`（别名：`ls`） | 列出已安装的插件及其启用/禁用状态。 |

提供者插件的选择保存在 `config.yaml` 中：
- `memory.provider` — 活动的记忆提供者（空值 = 仅内置）
- `context.engine` — 活动的上下文引擎（`"compressor"` = 内置默认值）

通用插件的禁用列表存储在 `config.yaml` 的 `plugins.disabled` 下。

请参阅 [插件](../user-guide/features/plugins.md) 与 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md)。

<a id="hermes-tools"></a>
## `hermes tools`

```bash
hermes tools [--summary]
```

| 选项 | 描述 |
|--------|-------------|
| `--summary` | 打印当前已启用工具的摘要并退出。 |

不带 `--summary` 时，此命令会启动交互式按平台配置工具 UI。

<a id="hermes-computer-use"></a>
## `hermes computer-use`

```bash
hermes computer-use <子命令>
```

子命令：

| 子命令 | 描述 |
|------------|-------------|
| `install` | 运行上游的 cua-driver 安装程序（仅 macOS）。 |
| `install --upgrade` | 即使 cua-driver 已经在 PATH 中，也重新运行安装程序。上游脚本始终拉取最新版本，因此这会执行就地升级。 |
| `status` | 打印 `cua-driver` 是否在 `$PATH` 中以及安装的版本。 |
`hermes computer-use install` 是安装 `computer_use` 工具集所依赖的 [cua-driver](https://github.com/trycua/cua) 二进制文件的稳定入口点。它执行与首次启用 Computer Use 时 `hermes tools` 调用的同一上游安装程序，因此如果工具集开关未触发安装（例如，在回访用户的设置中），可以安全地使用它重新运行安装。

`hermes update` 会在更新结束时自动重新运行上游安装程序（如果 cua-driver 在 PATH 中），因此大多数用户无需手动调用 `--upgrade`。当上游发布了你希望立即使用、但又不想等待下一个 Hermes 更新的修复程序时，可以使用此选项。

<a id="hermes-sessions"></a>
## `hermes sessions`

```bash
hermes sessions <subcommand>
```

子命令：

| 子命令 | 描述 |
|--------|------|
| `list` | 列出最近的会话。 |
| `browse` | 交互式会话选择器，支持搜索和恢复。 |
| `export &lt;output&gt; [--session-id ID]` | 将会话导出为 JSONL。 |
| `delete &lt;session-id&gt;` | 删除一个会话。 |
| `prune` | 删除旧会话。 |
| `stats` | 显示会话存储的统计信息。 |
| `rename &lt;session-id&gt; &lt;title&gt;` | 设置或更改会话标题。 |

<a id="hermes-insights"></a>
## `hermes insights`

```bash
hermes insights [--days N] [--source platform]
```

| 选项 | 描述 |
|------|------|
| `--days &lt;n&gt;` | 分析最近 `n` 天（默认：30）。 |
| `--source &lt;platform&gt;` | 按来源（如 `cli`、`telegram` 或 `discord`）过滤。 |

<a id="hermes-claw"></a>
## `hermes claw`

```bash
hermes claw migrate [options]
```

将你的 OpenClaw 设置迁移到 Hermes。从 `~/.openclaw`（或自定义路径）读取，并写入 `~/.hermes`。自动检测遗留的目录名称（`~/.clawdbot`、`~/.moltbot`）和配置文件名称（`clawdbot.json`、`moltbot.json`）。

| 选项 | 描述 |
|------|------|
| `--dry-run` | 预览将要迁移的内容，但不执行任何写入操作。 |
| `--preset &lt;name&gt;` | 迁移预设：`full`（所有兼容设置）或 `user-data`（排除基础设施配置）。两种预设均不导入密钥——需要显式传递 `--migrate-secrets`。 |
| `--overwrite` | 在冲突时覆盖现有的 Hermes 文件（默认：当计划存在冲突时拒绝应用）。 |
| `--migrate-secrets` | 在迁移中包含 API 密钥。即使在 `--preset full` 下也需要此选项。 |
| `--no-backup` | 跳过迁移前对 `~/.hermes/` 的 zip 快照（默认情况下，在应用前会向 `~/.hermes/backups/pre-migration-*.zip` 写入一个单独的恢复点存档；可通过 `hermes import` 恢复）。 |
| `--source &lt;path&gt;` | 自定义 OpenClaw 目录（默认：`~/.openclaw`）。 |
| `--workspace-target &lt;path&gt;` | 工作区指令（AGENTS.md）的目标目录。 |
| `--skill-conflict &lt;mode&gt;` | 处理技能名称冲突：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

<a id="what-gets-migrated"></a>
### 迁移内容

迁移涵盖 30 多个类别，包括身份、记忆、技能、模型提供商、消息平台、Agent 行为、会话策略、MCP 服务器、TTS 等。项目要么直接导入到 Hermes 等效项中，要么存档以供人工审核。
**直接导入：** SOUL.md、MEMORY.md、USER.md、AGENTS.md、技能（4 个源目录）、默认模型、自定义提供商、MCP 服务器、消息平台令牌和允许列表（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、Agent 默认设置（推理努力度、压缩、人工延迟、时区、沙箱）、会话重置策略、审批规则、TTS 配置、浏览器设置、工具设置、执行超时、命令允许列表、网关配置以及来自 3 个来源的 API 密钥。

**归档供手动审查：** Cron 任务、插件、钩子/Webhook、内存后端（QMD）、技能注册表配置、UI/身份、日志、多 Agent 设置、频道绑定、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md。

**API 密钥解析**按优先级顺序检查三个来源：配置值 → `~/.openclaw/.env` → `auth-profiles.json`。所有令牌字段均处理纯字符串、环境模板（`${VAR}`）和 SecretRef 对象。

有关完整的配置键映射、SecretRef 处理细节以及迁移后检查清单，请参阅 **[完整迁移指南](../guides/migrate-from-openclaw.md)**。

<a id="examples"></a>
### 示例

```bash
# 预览将要迁移的内容
hermes claw migrate --dry-run

# 完整迁移（所有兼容设置，不含密钥）
hermes claw migrate --preset full

# 完整迁移，包含 API 密钥
hermes claw migrate --preset full --migrate-secrets

# 仅迁移用户数据（不含密钥），覆盖冲突
hermes claw migrate --preset user-data --overwrite

# 从自定义 OpenClaw 路径迁移
hermes claw migrate --source /home/user/old-openclaw
```

<a id="hermes-dashboard"></a>
## `hermes dashboard`

```bash
hermes dashboard [options]
```

启动 Web 仪表盘——一个基于浏览器的 UI，用于管理配置、API 密钥和监控会话。需要 `pip install hermes-agent[web]`（FastAPI + Uvicorn）。嵌入式浏览器聊天选项卡需要 `--tui` 以及 `pty` 附加组件。完整文档请参阅 [Web 仪表盘](/user-guide/features/web-dashboard)。

| 选项 | 默认值 | 描述 |
|--------|---------|-------------|
| `--port` | `9119` | 运行 Web 服务器的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--tui` | 关闭 | 通过在 PTY/WebSocket 桥接后运行 `hermes --tui` 来启用浏览器内的聊天选项卡。需要 `pip install 'hermes-agent[web,pty]'` 以及 POSIX PTY 环境（如 Linux、macOS 或 WSL2）。 |
| `--insecure` | 关闭 | 允许绑定到非 localhost 主机。会将仪表盘凭据暴露到网络上；仅在受信任的网络控制后方可使用。 |
| `--stop` | — | 停止正在运行的 `hermes dashboard` 进程并退出。 |
| `--status` | — | 列出正在运行的 `hermes dashboard` 进程并退出。 |

```bash
# 默认——打开浏览器访问 http://127.0.0.1:9119
hermes dashboard

# 自定义端口，不打开浏览器
hermes dashboard --port 8080 --no-open

# 启用浏览器聊天选项卡
hermes dashboard --tui
```

<a id="hermes-profile"></a>
## `hermes profile`

```bash
hermes profile <subcommand>
```

管理配置文件——多个隔离的 Hermes 实例，每个实例拥有自己的配置、会话、技能和主目录。
| 子命令 | 描述 |
|--------|------|
| `list` | 列出所有配置。 |
| `use &lt;name&gt;` | 设置一个粘性默认配置。 |
| `create &lt;name&gt; [--clone] [--clone-all] [--clone-from &lt;source&gt;] [--no-alias]` | 创建一个新配置。`--clone` 从当前激活配置复制 config、`.env` 和 `SOUL.md`。`--clone-all` 复制所有状态。`--clone-from` 指定源配置。 |
| `delete &lt;name&gt; [-y]` | 删除一个配置。 |
| `show &lt;name&gt;` | 显示配置详情（主目录、配置等）。 |
| `alias &lt;name&gt; [--remove] [--name NAME]` | 管理用于快速访问配置的包装脚本。 |
| `rename &lt;old&gt; &lt;new&gt;` | 重命名一个配置。 |
| `export &lt;name&gt; [-o FILE]` | 将配置导出为 `.tar.gz` 归档文件（本地备份）。 |
| `import &lt;archive&gt; [--name NAME]` | 从 `.tar.gz` 归档文件导入配置（本地恢复）。 |
| `install &lt;source&gt; [--name N] [--alias] [--force] [-y]` | 从 git URL 或本地目录安装配置分发。 |
| `update &lt;name&gt; [--force-config] [-y]` | 重新拉取分发；保留用户数据（记忆、会话、认证）。 |
| `info &lt;name&gt;` | 显示配置的分发清单（版本、要求、来源）。 |

示例：

```bash
hermes profile list
hermes profile create work --clone
hermes profile use work
hermes profile alias work --name h-work
hermes profile export work -o work-backup.tar.gz
hermes profile import work-backup.tar.gz --name restored
hermes profile install github.com/user/my-distro --alias
hermes profile update work
hermes -p work chat -q "Hello from work profile"
```

<a id="hermes-completion"></a>
## `hermes completion`

```bash
hermes completion [bash|zsh|fish]
```

将 Shell 补全脚本输出到标准输出。在 Shell 配置文件中执行此输出，即可获得 Hermes 命令、子命令和配置名的 Tab 补全功能。

示例：

```bash
# Bash
hermes completion bash >> ~/.bashrc

# Zsh
hermes completion zsh >> ~/.zshrc

# Fish
hermes completion fish > ~/.config/fish/completions/hermes.fish
```

<a id="hermes-update"></a>
## `hermes update`

```bash
hermes update [--check] [--backup] [--restart-gateway]
```

拉取最新的 `hermes-agent` 代码并重新安装依赖到你的虚拟环境（venv）中，然后重新运行安装后钩子（MCP 服务器、技能同步、补全安装）。可在运行中的安装上安全执行。

**pip 安装：** `hermes update` 会自动检测基于 pip 的安装方式——它会向 PyPI 查询最新版本，然后运行 `pip install --upgrade hermes-agent` 而不是 `git pull`。PyPI 版本追踪的是已标记的版本（主/次版本），而非 `main` 分支上的每次提交。使用 `--check` 可以在不安装的情况下检查是否有更新的 PyPI 版本可用。

| 选项 | 描述 |
|------|------|
| `--check` | 并列显示当前 commit 和最新的 `origin/main` commit，若同步则退出码为 0，落后则为 1。不拉取、安装或重启任何内容。 |
| `--backup` | 在拉取前创建带标签的 `HERMES_HOME` 快照（配置、认证、会话、技能、配对数据）。默认**关闭**——之前总是备份的行为会在大型 home 上每次更新增加几分钟时间。可通过在 `config.yaml` 中设置 `update.backup: true` 永久启用。 |
| `--restart-gateway` | 更新成功后重启正在运行的网关服务。如果安装了多个配置，则隐式包含 `--all` 语义。 |
附加行为：

- **配对数据快照。** 即使关闭了 `--backup`，`hermes update` 仍然会在 `git pull` 之前对 `~/.hermes/pairing/` 和飞书评论规则进行轻量级快照。如果 `git pull` 覆盖了你正在编辑的文件，你可以通过 `hermes backup restore --state pre-update` 回滚。

- **旧版 `hermes.service` 警告。** 如果 Hermes 检测到重命名前的 `hermes.service` systemd 单元（而非当前的 `hermes-gateway.service`），它会打印一次迁移提示，以帮助你避免 flap-loop 问题。

- **退出码。** `0` 表示成功，`1` 表示拉取/安装/安装后过程出错，`2` 表示工作树出现意外变更导致 `git pull` 被阻塞。

<a id="maintenance-commands"></a>
## 维护命令

| 命令 | 说明 |
|---------|-------------|
| `hermes version` | 打印版本信息。 |
| `hermes update` | 拉取最新变更并重新安装依赖。 |
| `hermes uninstall [--full] [--yes]` | 移除 Hermes，可选删除所有配置/数据。 |

<a id="see-also"></a>
## 参见

- [斜线命令参考](./slash-commands.md)
- [CLI 接口](../user-guide/cli.md)
- [会话](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)
