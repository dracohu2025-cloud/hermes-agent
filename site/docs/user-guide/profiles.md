---
sidebar_position: 2
---

<a id="profiles-running-multiple-agents"></a>
# 配置文件（Profiles）：运行多个 Agent

在同一台机器上运行多个独立的 Hermes Agent——每个 Agent 拥有自己的配置、API 密钥、记忆、会话、技能和网关状态。

<a id="what-are-profiles"></a>
## 什么是配置文件？

配置文件是一个独立的 Hermes 主目录。每个配置文件都有自己的目录，其中包含自己的 `config.yaml`、`.env`、`SOUL.md`、记忆、会话、技能、定时任务和状态数据库。配置文件让你可以为不同目的运行独立的 Agent——比如一个编码助手、一个个人机器人、一个研究 Agent——而不会混淆 Hermes 状态。

当你创建一个配置文件时，它会自动变成自己的命令。创建一个名为 `coder` 的配置文件后，你立即就能使用 `coder chat`、`coder setup`、`coder gateway start` 等命令。

<a id="quick-start"></a>
## 快速开始

```bash
hermes profile create coder       # 创建配置文件 + "coder" 命令别名
coder setup                       # 配置 API 密钥和模型
coder chat                        # 开始聊天
```

就这样。`coder` 现在成了独立的 Hermes 配置文件，拥有自己的配置、记忆和状态。

<a id="creating-a-profile"></a>
## 创建配置文件

<a id="blank-profile"></a>
### 空白配置文件

```bash
hermes profile create mybot
```

创建一个全新的配置文件，并预置了捆绑技能。运行 `mybot setup` 来配置 API 密钥、模型和网关令牌。

如果你打算把这个配置文件用作看板工作节点（或希望看板编排器将任务路由给它），可以在创建时传入 `--description "<角色>"`，这样编排器就知道它擅长什么：

```bash
hermes profile create researcher --description "阅读源代码和外部文档，撰写发现。"
```

你也可以稍后用 `hermes profile describe` 来设置或自动生成描述——完整的路由模型请参阅[看板指南](./features/kanban#auto-vs-manual-orchestration)。

<a id="clone-config-only-clone"></a>
### 仅克隆配置（`--clone`）

```bash
hermes profile create work --clone
```

将当前配置文件的 `config.yaml`、`.env` 和 `SOUL.md` 复制到新配置文件中。API 密钥和模型相同，但会话和记忆是全新的。若要使用不同的 API 密钥，编辑 `~/.hermes/profiles/work/.env`；若要改变个性，编辑 `~/.hermes/profiles/work/SOUL.md`。

<a id="clone-everything-clone-all"></a>
### 克隆全部（`--clone-all`）

```bash
hermes profile create backup --clone-all
```

复制**所有内容**——配置、API 密钥、个性、全部记忆、完整会话历史、技能、定时任务、插件。一个完整的快照。用于备份或分叉一个已有上下文的 Agent。

<a id="clone-from-a-specific-profile"></a>
### 从指定配置文件克隆

```bash
hermes profile create work --clone --clone-from coder
```

:::tip Honcho 记忆 + 配置文件
启用 Honcho 时，`--clone` 会自动为新配置文件创建一个专用的 AI 同伴，同时共享同一个用户工作空间。每个配置文件都会建立自己的观察和身份。详情参见 [Honcho——多 Agent / 配置文件](./features/memory-providers.md#honcho)。
<a id="honcho-memory-profiles"></a>
:::

<a id="using-profiles"></a>
## 使用配置文件

<a id="command-aliases"></a>
### 命令别名

每个配置文件都会自动在 `~/.local/bin/&lt;name&gt;` 获得一个命令别名：

```bash
coder chat                    # 与 coder Agent 聊天
coder setup                   # 配置 coder 的设置
coder gateway start           # 启动 coder 的网关
coder doctor                  # 检查 coder 的健康状况
coder skills list             # 列出 coder 的技能
coder config set model.default anthropic/claude-sonnet-4
```
别名适用于每个 hermes 子命令——底层其实就是 `hermes -p &lt;name&gt;`。

<a id="the-p-flag"></a>
### `-p` 标志

你也可以在任何命令中显式指定一个 Profile：

```bash
hermes -p coder chat
hermes --profile=coder doctor
hermes chat -p coder -q "hello"    # 可放在任意位置
```

<a id="sticky-default-hermes-profile-use"></a>
### 设置默认 Profile（`hermes profile use`）

```bash
hermes profile use coder
hermes chat                   # 现在默认使用 coder
hermes tools                  # 配置 coder 的工具
hermes profile use default    # 切换回默认
```

设置一个默认值，这样不带参数的 `hermes` 命令就会使用该 Profile。类似于 `kubectl config use-context`。

<a id="knowing-where-you-are"></a>
### 了解当前所在位置

CLI 始终会显示当前激活的 Profile：

- **提示符**：显示为 `coder ❯` 而不是 `❯`
- **启动横幅**：启动时显示 `Profile: coder`
- **`hermes profile`**：显示当前 Profile 名称、路径、模型、网关状态

<a id="profiles-vs-workspaces-vs-sandboxing"></a>
## Profiles 与 workspaces 和 sandboxing 的区别

Profiles 常常与 workspaces 或 sandboxes 混淆，但它们是不同的概念：

- **Profile** 为 Hermes 提供独立的状态目录：`config.yaml`、`.env`、`SOUL.md`、会话、记忆、日志、定时任务以及网关状态。
- **Workspace** 或 **工作目录** 是终端命令启动的目录。这由 `terminal.cwd` 单独控制。
- **Sandbox** 用于限制文件系统访问。Profiles **不会**对 Agent 进行沙盒限制。

在默认的 `local` 终端后端下，Agent 仍然拥有与你用户账户相同的文件系统访问权限。Profile 不会阻止它访问 Profile 目录以外的文件夹。

如果你希望某个 Profile 在特定的项目文件夹中启动，请在该 Profile 的 `config.yaml` 中设置显式的绝对路径 `terminal.cwd`：

```yaml
terminal:
  backend: local
  cwd: /absolute/path/to/project
```

在 local 后端使用 `cwd: "."` 表示“Hermes 启动时的目录”，而不是“Profile 目录”。

另请注意：

- `SOUL.md` 可以引导模型，但不会强制限定工作空间边界。
- 修改 `SOUL.md` 后，新会话会干净地生效。已有的会话可能仍然使用旧的提示状态。
- 向模型询问“你在哪个目录？”不是可靠的隔离测试。如果你需要为工具提供可预测的起始目录，请显式设置 `terminal.cwd`。

<a id="running-gateways"></a>
## 运行网关

每个 Profile 都会运行自己的网关，作为独立进程，并使用各自的机器人令牌：

```bash
coder gateway start           # 启动 coder 的网关
assistant gateway start       # 启动 assistant 的网关（独立进程）
```

<a id="different-bot-tokens"></a>
### 不同的机器人令牌

每个 Profile 都有自己的 `.env` 文件。可以在其中配置不同的 Telegram/Discord/Slack 机器人令牌：

```bash
# 编辑 coder 的令牌
nano ~/.hermes/profiles/coder/.env

# 编辑 assistant 的令牌
nano ~/.hermes/profiles/assistant/.env
```

<a id="safety-token-locks"></a>
### 安全：令牌锁定

如果两个 Profile 意外使用了同一个机器人令牌，第二个网关将被阻止，并显示明确的错误消息，指出冲突的 Profile。支持 Telegram、Discord、Slack、WhatsApp 和 Signal。

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
coder config set model.default anthropic/claude-sonnet-4
echo "你是一个专注的编码助手。" > ~/.hermes/profiles/coder/SOUL.md
```

如果你希望此配置文件默认在特定项目中工作，还需要设置自己的 `terminal.cwd`：

```bash
coder config set terminal.cwd /absolute/path/to/project
```

<a id="updating"></a>
## 更新

`hermes update` 拉取一次代码（共享）并自动将新的捆绑技能同步到**所有**配置文件：

```bash
hermes update
# → 代码已更新（12 次提交）
# → 技能已同步：default（最新），coder（+2 个新技能），assistant（+2 个新技能）
```

用户修改过的技能永远不会被覆盖。

<a id="managing-profiles"></a>
## 管理配置文件

```bash
hermes profile list           # 显示所有配置文件及其状态
hermes profile show coder     # 显示一个配置文件的详细信息
hermes profile rename coder dev-bot   # 重命名（更新别名和服务）
hermes profile export coder   # 导出为 coder.tar.gz
hermes profile import coder.tar.gz   # 从归档文件导入
```

<a id="deleting-a-profile"></a>
## 删除配置文件

```bash
hermes profile delete coder
```

这会停止网关、移除 systemd/launchd 服务、删除命令别名，并删除所有配置文件数据。系统会要求你输入配置文件名称以确认。

使用 `--yes` 跳过确认：`hermes profile delete coder --yes`

:::note
你不能删除默认配置文件（`~/.hermes`）。要删除所有内容，请使用 `hermes uninstall`。
:::

<a id="tab-completion"></a>
## Tab 补全

```bash
# Bash
eval "$(hermes completion bash)"

# Zsh
eval "$(hermes completion zsh)"
```

将这一行添加到你的 `~/.bashrc` 或 `~/.zshrc` 中以实现持久补全。可以补全 `-p` 后的配置文件名称、配置文件子命令以及顶级命令。

<a id="how-it-works"></a>
## 工作原理

配置文件使用 `HERMES_HOME` 环境变量。当你运行 `coder chat` 时，包装脚本会在启动 hermes 之前将 `HERMES_HOME` 设置为 `~/.hermes/profiles/coder`。由于代码库中 119+ 个文件通过 `get_hermes_home()` 解析路径，Hermes 状态会自动限定到配置文件的目录——包括配置、会话、记忆、技能、状态数据库、网关 PID、日志和定时任务。

这与终端工作目录是分开的。工具执行从 `terminal.cwd` 开始（或者在本地后端上 `cwd: "."` 时从启动目录开始），而不是自动从 `HERMES_HOME` 开始。

默认配置文件就是 `~/.hermes` 本身。无需迁移——现有安装可以正常工作。

<a id="sharing-profiles-as-distributions"></a>
## 将配置文件作为发行版共享

你在某台机器上构建的配置文件可以打包为 **git 仓库**，并通过一条命令在另一台机器上安装——无论是你自己的工作站、队友的笔记本电脑，还是社区用户的环境。共享包包括 SOUL、配置、技能、定时任务和 MCP 连接。凭据、记忆和会话则保留在每台机器上。
```bash
# Install a whole agent from a git repo
hermes profile install github.com/you/research-bot --alias

# Update later when the author ships a new version (keeps your memories + .env)
hermes profile update research-bot
```

参见 **[Profile 分发：分享整个 Agent](./profile-distributions.md)** 获取完整指南——包括创作、发布、更新语义、安全模型及使用场景。
