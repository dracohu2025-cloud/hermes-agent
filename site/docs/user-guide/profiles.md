---
sidebar_position: 2
---

# 配置文件：运行多个 Agent {#profiles-running-multiple-agents}

在同一台机器上运行多个独立的 Hermes Agent——每个 Agent 拥有自己的配置、API 密钥、记忆、会话、技能和网关状态。

## 什么是配置文件？ {#what-are-profiles}

配置文件是一个独立的 Hermes 主目录。每个配置文件拥有自己的目录，其中包含独立的 `config.yaml`、`.env`、`SOUL.md`、记忆、会话、技能、定时任务和状态数据库。配置文件让你可以为不同用途运行独立的 Agent——比如一个编码助手、一个个人机器人、一个研究 Agent——而不会混淆 Hermes 的状态。

当你创建一个配置文件时，它会自动成为一条独立的命令。创建一个名为 `coder` 的配置文件，你立即就能使用 `coder chat`、`coder setup`、`coder gateway start` 等命令。

## 快速开始 {#quick-start}

```bash
hermes profile create coder       # 创建配置文件 + "coder" 命令别名
coder setup                       # 配置 API 密钥和模型
coder chat                        # 开始聊天
```

就这样。`coder` 现在是一个独立的 Hermes 配置文件，拥有自己的配置、记忆和状态。

## 创建配置文件 {#creating-a-profile}

### 空白配置文件 {#blank-profile}

```bash
hermes profile create mybot
```

创建一个全新的配置文件，并预置了内置技能。运行 `mybot setup` 来配置 API 密钥、模型和网关令牌。

### 仅克隆配置（`--clone`） {#clone-config-only-clone}

```bash
hermes profile create work --clone
```

将当前配置文件的 `config.yaml`、`.env` 和 `SOUL.md` 复制到新配置文件中。API 密钥和模型相同，但会话和记忆是全新的。编辑 `~/.hermes/profiles/work/.env` 以使用不同的 API 密钥，或编辑 `~/.hermes/profiles/work/SOUL.md` 以设置不同的个性。

### 克隆全部（`--clone-all`） {#clone-everything-clone-all}

```bash
hermes profile create backup --clone-all
```

复制**所有内容**——配置、API 密钥、个性、全部记忆、完整会话历史、技能、定时任务、插件。一个完整的快照。适用于备份或派生一个已经拥有上下文的 Agent。

### 从特定配置文件克隆 {#clone-from-a-specific-profile}

```bash
hermes profile create work --clone --clone-from coder
```

:::tip Honcho 记忆 + 配置文件
当启用 Honcho 时，`--clone` 会自动为新配置文件创建一个专用的 AI 对等体，同时共享同一个用户工作空间。每个配置文件会构建自己的观察和身份。详情请参见 [Honcho——多 Agent / 配置文件](./features/memory-providers.md#honcho)。
:::
<a id="honcho-memory-profiles"></a>

## 使用配置文件 {#using-profiles}

### 命令别名 {#command-aliases}

每个配置文件都会自动在 `~/.local/bin/&lt;name&gt;` 获得一个命令别名：

```bash
coder chat                    # 与 coder Agent 聊天
coder setup                   # 配置 coder 的设置
coder gateway start           # 启动 coder 的网关
coder doctor                  # 检查 coder 的健康状态
coder skills list             # 列出 coder 的技能
coder config set model.default anthropic/claude-sonnet-4
```

该别名适用于所有 hermes 子命令——底层其实就是 `hermes -p &lt;name&gt;`。

### `-p` 标志 {#the-p-flag}

你也可以在任何命令中显式指定一个配置文件：

```bash
hermes -p coder chat
hermes --profile=coder doctor
hermes chat -p coder -q "hello"    # 可以放在任何位置
```
### 固定默认（`hermes profile use`） {#sticky-default-hermes-profile-use}

```bash
hermes profile use coder
hermes chat                   # 现在目标为 coder
hermes tools                  # 配置 coder 的工具
hermes profile use default    # 切换回去
```

设置一个默认值，这样不带参数的 `hermes` 命令就会指向该 profile。类似于 `kubectl config use-context`。

### 了解当前所在位置 {#knowing-where-you-are}

CLI 始终显示当前激活的是哪个 profile：

- **提示符**：显示 `coder ❯` 而不是 `❯`
- **横幅**：启动时显示 `Profile: coder`
- **`hermes profile`**：显示当前 profile 名称、路径、模型、网关状态

## Profiles vs 工作区 vs 沙箱 {#profiles-vs-workspaces-vs-sandboxing}

Profiles 经常与工作区或沙箱混淆，但它们是不同的概念：

- **profile** 为 Hermes 提供自己的状态目录：`config.yaml`、`.env`、`SOUL.md`、会话、内存、日志、cron 作业和网关状态。
- **工作区**或**工作目录**是终端命令启动的地方。这由 `terminal.cwd` 单独控制。
- **沙箱**是限制文件系统访问的东西。Profiles **不会**对 agent 进行沙箱化。

在默认的 `local` 终端后端上，agent 仍然拥有与你的用户账户相同的文件系统访问权限。一个 profile 不会阻止它访问 profile 目录之外的文件夹。

如果你希望某个 profile 在特定的项目文件夹中启动，请在该 profile 的 `config.yaml` 中设置一个明确的绝对路径 `terminal.cwd`：

```yaml
terminal:
  backend: local
  cwd: /absolute/path/to/project
```

在 local 后端上使用 `cwd: "."` 表示“Hermes 启动时的目录”，而不是“profile 目录”。

另请注意：

- `SOUL.md` 可以指导模型，但它不会强制限定工作区边界。
- 对 `SOUL.md` 的修改会在新会话中干净地生效。现有会话可能仍在使用旧的提示状态。
- 询问模型“你在哪个目录？”并不是一个可靠的隔离测试。如果你需要为工具提供一个可预测的起始目录，请显式设置 `terminal.cwd`。

## 运行网关 {#running-gateways}

每个 profile 都运行自己的网关，作为独立的进程，拥有自己的机器人令牌：

```bash
coder gateway start           # 启动 coder 的网关
assistant gateway start       # 启动 assistant 的网关（独立进程）
```

### 不同的机器人令牌 {#different-bot-tokens}

每个 profile 都有自己的 `.env` 文件。在每个文件中配置不同的 Telegram/Discord/Slack 机器人令牌：

```bash
# 编辑 coder 的令牌
nano ~/.hermes/profiles/coder/.env

# 编辑 assistant 的令牌
nano ~/.hermes/profiles/assistant/.env
```

### 安全性：令牌锁定 {#safety-token-locks}

如果两个 profile 意外使用了相同的机器人令牌，第二个网关将被阻止，并显示一条明确的错误信息，指出冲突的 profile 名称。支持 Telegram、Discord、Slack、WhatsApp 和 Signal。

### 持久化服务 {#persistent-services}

```bash
coder gateway install         # 创建 hermes-gateway-coder 的 systemd/launchd 服务
assistant gateway install     # 创建 hermes-gateway-assistant 服务
```

每个 profile 都有自己的服务名称。它们独立运行。

## 配置 profiles {#configuring-profiles}

每个 profile 都有自己的：
- **`config.yaml`** — 模型、提供商、工具集、所有设置
- **`.env`** — API 密钥、机器人令牌
- **`SOUL.md`** — 个性与指令

```bash
coder config set model.default anthropic/claude-sonnet-4
echo "You are a focused coding assistant." > ~/.hermes/profiles/coder/SOUL.md
```

如果你希望这个 profile 默认在某个特定项目下工作，还可以设置它自己的 `terminal.cwd`：

```bash
coder config set terminal.cwd /absolute/path/to/project
```

## 更新 {#updating}

`hermes update` 会拉取一次代码（共享），并将新的捆绑技能自动同步到 **所有** profile：

```bash
hermes update
# → Code updated (12 commits)
# → Skills synced: default (up to date), coder (+2 new), assistant (+2 new)
```

用户修改过的技能不会被覆盖。

## 管理 profiles {#managing-profiles}

```bash
hermes profile list           # 显示所有 profile 及其状态
hermes profile show coder     # 查看某个 profile 的详细信息
hermes profile rename coder dev-bot   # 重命名（更新别名和服务）
hermes profile export coder   # 导出为 coder.tar.gz
hermes profile import coder.tar.gz   # 从归档文件导入
```

## 删除 profile {#deleting-a-profile}

```bash
hermes profile delete coder
```

这会停止网关、移除 systemd/launchd 服务、删除命令别名，并清除所有 profile 数据。你需要输入 profile 名称来确认。

使用 `--yes` 跳过确认：`hermes profile delete coder --yes`

:::note
你不能删除默认 profile（`~/.hermes`）。要彻底移除所有内容，请使用 `hermes uninstall`。
:::

## Tab 补全 {#tab-completion}

```bash
# Bash
eval "$(hermes completion bash)"

# Zsh
eval "$(hermes completion zsh)"
```

将对应行添加到你的 `~/.bashrc` 或 `~/.zshrc` 中，即可持久化补全功能。补全支持 `-p` 后的 profile 名称、profile 子命令以及顶层命令。

## 工作原理 {#how-it-works}

Profiles 使用 `HERMES_HOME` 环境变量。当你运行 `coder chat` 时，包装脚本会在启动 hermes 之前将 `HERMES_HOME` 设置为 `~/.hermes/profiles/coder`。由于代码库中 119+ 个文件都通过 `get_hermes_home()` 解析路径，Hermes 的状态会自动限定到该 profile 的目录——包括配置、会话、记忆、技能、状态数据库、网关 PID、日志和 cron 任务。

这与终端工作目录是分开的。工具执行从 `terminal.cwd` 开始（或者在本地后端上使用 `cwd: "."` 时从启动目录开始），而不是自动从 `HERMES_HOME` 开始。

默认 profile 就是 `~/.hermes` 本身。无需迁移——现有安装可以照常工作。
