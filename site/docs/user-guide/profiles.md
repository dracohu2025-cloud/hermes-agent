---
sidebar_position: 2
---

<a id="profiles-running-multiple-agents"></a>
# 配置文件：运行多个 Agent

在同一台机器上运行多个独立的 Hermes Agent —— 每个 Agent 都有自己的配置、API 密钥、记忆、会话、技能和网关状态。

<a id="what-are-profiles"></a>
## 什么是配置文件？

配置文件是一个独立的 Hermes 主目录。每个配置文件都有自己的目录，包含其专属的 `config.yaml`、`.env`、`SOUL.md`、记忆、会话、技能、定时任务和状态数据库。配置文件让你可以为不同目的运行独立的 Agent —— 例如一个编程助手、一个个人机器人、一个研究 Agent —— 而不会混淆 Hermes 的状态。

当你创建一个配置文件时，它会自动成为一个独立的命令。创建一个名为 `coder` 的配置文件，你立即就拥有了 `coder chat`、`coder setup`、`coder gateway start` 等命令。

<a id="quick-start"></a>
## 快速开始

```bash
hermes profile create coder       # 创建配置文件 + "coder" 命令别名
coder setup                       # 配置 API 密钥和模型
coder chat                        # 开始聊天
```

就这样。`coder` 现在就是一个拥有自己配置、记忆和状态的 Hermes 配置文件。

<a id="creating-a-profile"></a>
## 创建配置文件

<a id="blank-profile"></a>
### 空白配置文件

```bash
hermes profile create mybot
```

创建一个全新的配置文件，并预置了捆绑的技能。运行 `mybot setup` 来配置 API 密钥、模型和网关令牌。

<a id="clone-config-only-clone"></a>
### 仅克隆配置 (`--clone`)

```bash
hermes profile create work --clone
```

将当前配置文件的 `config.yaml`、`.env` 和 `SOUL.md` 复制到新配置文件中。使用相同的 API 密钥和模型，但会话和记忆是全新的。编辑 `~/.hermes/profiles/work/.env` 以使用不同的 API 密钥，或编辑 `~/.hermes/profiles/work/SOUL.md` 以设定不同的人格。

<a id="clone-everything-clone-all"></a>
### 克隆所有内容 (`--clone-all`)

```bash
hermes profile create backup --clone-all
```

复制**所有内容** —— 配置、API 密钥、人格、所有记忆、完整的会话历史、技能、定时任务、插件。一个完整的快照。适用于备份或分叉一个已有上下文的 Agent。

<a id="clone-from-a-specific-profile"></a>
### 从特定配置文件克隆

```bash
hermes profile create work --clone --clone-from coder
```

:::tip Honcho 记忆 + 配置文件
启用 Honcho 后，`--clone` 会自动为新配置文件创建一个专用的 AI 对等体，同时共享同一个用户工作空间。每个配置文件都会建立自己的观察和身份。详见 [Honcho -- 多 Agent / 配置文件](./features/memory-providers.md#honcho)。
<a id="honcho-memory-profiles"></a>
:::

<a id="using-profiles"></a>
## 使用配置文件

<a id="command-aliases"></a>
### 命令别名

每个配置文件都会在 `~/.local/bin/&lt;name&gt;` 自动获得一个命令别名：

```bash
coder chat                    # 与 coder agent 聊天
coder setup                   # 配置 coder 的设置
coder gateway start           # 启动 coder 的网关
coder doctor                  # 检查 coder 的健康状况
coder skills list             # 列出 coder 的技能
coder config set model.model anthropic/claude-sonnet-4
```
别名适用于所有 Hermes 子命令——本质上就是 `hermes -p <名称>`。

<a id="the-p-flag"></a>
### `-p` 标志

你也可以在任何命令中显式指定目标 profile：

```bash
hermes -p coder chat
hermes --profile=coder doctor
hermes chat -p coder -q "hello"    # 可在任意位置使用
```

<a id="sticky-default-hermes-profile-use"></a>
### 黏性默认值 (`hermes profile use`)

```bash
hermes profile use coder
hermes chat                   # 现在会指向 coder
hermes tools                  # 配置 coder 的工具
hermes profile use default    # 切换回默认
```

设置默认值，使普通的 `hermes` 命令指向该 profile。类似于 `kubectl config use-context`。

<a id="knowing-where-you-are"></a>
### 了解当前状态

CLI 总是会显示哪个 profile 处于激活状态：

- **提示符**：显示 `coder ❯` 而不是 `❯`
- **横幅**：启动时显示 `Profile: coder`
- **`hermes profile`**：显示当前 profile 的名称、路径、模型、gateway 状态

<a id="profiles-vs-workspaces-vs-sandboxing"></a>
## Profiles vs 工作空间 vs 沙盒

Profiles 常常与工作空间或沙盒混淆，但它们是不同的概念：

- **profile** 为 Hermes 提供了自己的状态目录：`config.yaml`、`.env`、`SOUL.md`、会话、记忆、日志、定时作业和 gateway 状态。
- **工作空间**或**工作目录**是终端命令启动的位置。这由 `terminal.cwd` 单独控制。
- **沙盒**是限制文件系统访问的机制。Profiles **不**会沙盒化 Agent。

在默认的 `local` 终端后端，Agent 仍然拥有与你用户账户相同的文件系统访问权限。Profile 不会阻止它访问 profile 目录之外的文件夹。

如果你希望 profile 在特定的项目文件夹中启动，请在该 profile 的 `config.yaml` 中设置一个明确的绝对路径 `terminal.cwd`：

```yaml
terminal:
  backend: local
  cwd: /absolute/path/to/project
```

在 local 后端上使用 `cwd: "."` 意味着“Hermes 启动时的目录”，而不是“profile 目录”。

还要注意：

- `SOUL.md` 可以指导模型，但它不强制执行工作空间边界。
- 对 `SOUL.md` 的更改会在新会话中干净地生效。现有会话可能仍在使用旧的提示状态。
- 询问模型“你在哪个目录里？”并不是一个可靠的隔离测试。如果你需要为工具提供一个可预测的起始目录，请显式设置 `terminal.cwd`。

<a id="running-gateways"></a>
## 运行 gateways

每个 profile 都会运行自己的 gateway，作为一个独立的进程，拥有自己的 bot token：

```bash
coder gateway start           # 启动 coder 的 gateway
assistant gateway start       # 启动 assistant 的 gateway（独立进程）
```
<a id="different-bot-tokens"></a>
### 不同的机器人令牌

每个配置文件都有自己的 `.env` 文件。请在每个文件中配置不同的 Telegram/Discord/Slack 机器人令牌：

```bash
# 编辑 coder 的令牌
nano ~/.hermes/profiles/coder/.env

# 编辑 assistant 的令牌
nano ~/.hermes/profiles/assistant/.env
```

<a id="safety-token-locks"></a>
### 安全性：令牌锁

如果两个配置文件意外使用了相同的机器人令牌，第二个网关将被阻止，并显示一个明确指出冲突配置文件的清晰错误。此功能支持 Telegram、Discord、Slack、WhatsApp 和 Signal。

<a id="persistent-services"></a>
### 持久化服务

```bash
coder gateway install         # 创建 hermes-gateway-coder systemd/launchd 服务
assistant gateway install     # 创建 hermes-gateway-assistant 服务
```

每个配置文件都有自己的服务名称。它们独立运行。

<a id="configuring-profiles"></a>
## 配置配置文件

每个配置文件都有自己的：

- **`config.yaml`** — 模型、提供商、工具集、所有设置
- **`.env`** — API 密钥、机器人令牌
- **`SOUL.md`** — 个性和指令

```bash
coder config set model.model anthropic/claude-sonnet-4
echo "你是一个专注的编程助手。" > ~/.hermes/profiles/coder/SOUL.md
```

如果你希望此配置文件默认在特定项目中工作，还需设置其自己的 `terminal.cwd`：

```bash
coder config set terminal.cwd /absolute/path/to/project
```

<a id="updating"></a>
## 更新

`hermes update` 会拉取一次代码（共享）并自动将新的捆绑技能同步到**所有**配置文件：

```bash
hermes update
# → 代码已更新 (12 次提交)
# → 技能已同步：default (已是最新), coder (+2 个新), assistant (+2 个新)
```

用户修改过的技能永远不会被覆盖。

<a id="managing-profiles"></a>
## 管理配置文件

```bash
hermes profile list           # 显示所有配置文件及其状态
hermes profile show coder     # 显示单个配置文件的详细信息
hermes profile rename coder dev-bot   # 重命名（更新别名和服务）
hermes profile export coder   # 导出到 coder.tar.gz
hermes profile import coder.tar.gz   # 从归档文件导入
```

<a id="deleting-a-profile"></a>
## 删除配置文件

```bash
hermes profile delete coder
```

这会停止网关、移除 systemd/launchd 服务、移除命令别名并删除所有配置文件数据。系统会要求你输入配置文件名称以进行确认。

使用 `--yes` 跳过确认：`hermes profile delete coder --yes`

:::note
你不能删除默认配置文件 (`~/.hermes`)。要移除所有内容，请使用 `hermes uninstall`。
:::

<a id="tab-completion"></a>
## Tab 补全

```bash
# Bash
eval "$(hermes completion bash)"

# Zsh
eval "$(hermes completion zsh)"
```

将相应行添加到你的 `~/.bashrc` 或 `~/.zshrc` 中以获得持久的补全功能。支持在 `-p` 后补全配置文件名称、配置文件子命令以及顶级命令。
<a id="how-it-works"></a>
## 工作原理

配置文件使用 `HERMES_HOME` 环境变量。当你运行 `coder chat` 时，包装脚本会在启动 hermes 之前设置 `HERMES_HOME=~/.hermes/profiles/coder`。由于代码库中有 119+ 个文件通过 `get_hermes_home()` 来解析路径，Hermes 的状态（配置、会话、记忆、技能、状态数据库、网关 PID、日志和定时任务）会自动限定在配置文件的目录下。

这与终端的工作目录是分开的。工具执行从 `terminal.cwd`（或在本地后端上使用 `cwd: "."` 时的启动目录）开始，而不是自动从 `HERMES_HOME` 开始。

默认配置文件就是 `~/.hermes` 目录本身。无需迁移——现有的安装可以完全照常工作。
