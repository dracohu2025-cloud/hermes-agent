---
sidebar_position: 2
---

# Profiles：运行多个 Agent

在同一台机器上运行多个独立的 Hermes Agent —— 每个 Agent 都有自己独立的配置、API 密钥、记忆、会话、技能和 Gateway。

## 什么是 Profiles？

Profile 是一个完全隔离的 Hermes 环境。每个 Profile 都有自己的目录，包含独立的 `config.yaml`、`.env`、`SOUL.md`、记忆、会话、技能、定时任务（cron jobs）和状态数据库。通过 Profile，你可以为不同的用途运行独立的 Agent —— 比如一个编程助手、一个私人机器人、一个研究 Agent —— 且彼此之间互不干扰。

当你创建一个 Profile 时，它会自动变成一个独立的命令。创建一个名为 `coder` 的 Profile，你立即就能使用 `coder chat`、`coder setup`、`coder gateway start` 等命令。

## 快速上手

```bash
hermes profile create coder       # 创建 profile 并生成 "coder" 命令别名
coder setup                       # 配置 API 密钥和模型
coder chat                        # 开始聊天
```

就这样。`coder` 现在是一个完全独立的 Agent。它拥有自己的配置、记忆以及一切。

## 创建 Profile

### 空白 Profile

```bash
hermes profile create mybot
```

创建一个全新的 Profile，并预置内置技能。运行 `mybot setup` 来配置 API 密钥、模型和 Gateway 令牌。

### 仅克隆配置 (`--clone`)

```bash
hermes profile create work --clone
```

将当前 Profile 的 `config.yaml`、`.env` 和 `SOUL.md` 复制到新 Profile 中。使用相同的 API 密钥和模型，但拥有全新的会话和记忆。你可以编辑 `~/.hermes/profiles/work/.env` 来使用不同的 API 密钥，或者编辑 `~/.hermes/profiles/work/SOUL.md` 来设定不同的性格。

### 克隆全部内容 (`--clone-all`)

```bash
hermes profile create backup --clone-all
```

复制**所有内容** —— 包括配置、API 密钥、性格、所有记忆、完整的会话历史、技能、定时任务和插件。这是一个完整的快照。适用于备份或为一个已经拥有上下文的 Agent 创建分支。

### 从特定 Profile 克隆

```bash
hermes profile create work --clone --clone-from coder
```

:::tip Honcho 记忆 + Profiles
当启用 Honcho 时，`--clone` 会自动为新 Profile 创建一个专用的 AI Peer，同时共享同一个用户工作区。每个 Profile 都会建立自己的观察结果和身份。详情请参阅 [Honcho -- 多 Agent / Profiles](./features/memory-providers.md#honcho)。
:::

## 使用 Profiles

### 命令别名

每个 Profile 都会在 `~/.local/bin/<name>` 自动获得一个命令别名：

```bash
coder chat                    # 与 coder Agent 聊天
coder setup                   # 配置 coder 的设置
coder gateway start           # 启动 coder 的 gateway
coder doctor                  # 检查 coder 的健康状况
coder skills list             # 列出 coder 的技能
coder config set model.model anthropic/claude-sonnet-4
```

该别名适用于每一个 hermes 子命令 —— 它的底层原理就是 `hermes -p <name>`。

### `-p` 标志

你也可以在任何命令中显式指定 Profile：

```bash
hermes -p coder chat
hermes --profile=coder doctor
hermes chat -p coder -q "hello"    # 放在任何位置都有效
```

### 粘性默认设置 (`hermes profile use`)

```bash
hermes profile use coder
hermes chat                   # 现在默认指向 coder
hermes tools                  # 配置 coder 的工具
hermes profile use default    # 切换回默认
```

设置一个默认 Profile，使得普通的 `hermes` 命令都指向该 Profile。类似于 `kubectl config use-context`。

### 确认当前位置

CLI 始终会显示当前处于哪个 Profile：

- **提示符**：显示 `coder ❯` 而不是 `❯`
- **横幅**：启动时显示 `Profile: coder`
- **`hermes profile`**：显示当前 Profile 的名称、路径、模型和 Gateway 状态

## 运行 Gateways

每个 Profile 作为一个独立的进程运行自己的 Gateway，并拥有自己的机器人令牌：

```bash
coder gateway start           # 启动 coder 的 gateway
assistant gateway start       # 启动 assistant 的 gateway（独立进程）
```

### 不同的机器人令牌

每个 Profile 都有自己的 `.env` 文件。在每个文件中配置不同的 Telegram/Discord/Slack 机器人令牌：

```bash
# 编辑 coder 的令牌
nano ~/.hermes/profiles/coder/.env

# 编辑 assistant 的令牌
nano ~/.hermes/profiles/assistant/.env
```

### 安全性：令牌锁定

如果两个 Profile 意外使用了相同的机器人令牌，第二个 Gateway 将被阻止启动，并显示明确的错误信息，指出冲突的 Profile 名称。支持 Telegram、Discord、Slack、WhatsApp 和 Signal。

### 持久化服务

```bash
coder gateway install         # 创建 hermes-gateway-coder systemd/launchd 服务
assistant gateway install     # 创建 hermes-gateway-assistant 服务
```

每个 Profile 都有自己的服务名称。它们独立运行。

## 配置 Profiles

每个 Profile 都有自己的：

- **`config.yaml`** —— 模型、提供商、工具集及所有设置
- **`.env`** —— API 密钥、机器人令牌
- **`SOUL.md`** —— 性格和指令

```bash
coder config set model.model anthropic/claude-sonnet-4
echo "You are a focused coding assistant." > ~/.hermes/profiles/coder/SOUL.md
```

## 更新

`hermes update` 会拉取一次代码（共享），并自动将新的内置技能同步到**所有** Profile：

```bash
hermes update
# → 代码已更新 (12 commits)
# → 技能已同步：default (已是最新), coder (+2 new), assistant (+2 new)
```

用户修改过的技能永远不会被覆盖。

## 管理 Profiles

```bash
hermes profile list           # 显示所有 Profile 及其状态
hermes profile show coder     # 显示单个 Profile 的详细信息
hermes profile rename coder dev-bot   # 重命名（更新别名和服务）
hermes profile export coder   # 导出为 coder.tar.gz
hermes profile import coder.tar.gz   # 从压缩包导入
```

## 删除 Profile

```bash
hermes profile delete coder
```

这将停止 Gateway，移除 systemd/launchd 服务，删除命令别名，并删除所有 Profile 数据。系统会要求你输入 Profile 名称以确认。

使用 `--yes` 跳过确认：`hermes profile delete coder --yes`

:::note
你不能删除默认 Profile (`~/.hermes`)。要移除所有内容，请使用 `hermes uninstall`。
:::

## Tab 补全

```bash
# Bash
eval "$(hermes completion bash)"

# Zsh
eval "$(hermes completion zsh)"
```

将上述行添加到你的 `~/.bashrc` 或 `~/.zshrc` 中以实现持久补全。它支持补全 `-p` 后的 Profile 名称、Profile 子命令以及顶级命令。

## 工作原理

Profiles 使用 `HERMES_HOME` 环境变量。当你运行 `coder chat` 时，包装脚本会在启动 hermes 之前设置 `HERMES_HOME=~/.hermes/profiles/coder`。由于代码库中有 119 多个文件通过 `get_hermes_home()` 解析路径，因此所有内容都会自动定位到该 Profile 的目录 —— 包括配置、会话、记忆、技能、状态数据库、Gateway PID、日志和定时任务。

默认 Profile 就是 `~/.hermes` 本身。无需迁移 —— 现有的安装可以完全照常工作。
