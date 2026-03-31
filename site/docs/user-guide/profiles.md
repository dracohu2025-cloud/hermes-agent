---
sidebar_position: 2
---

# 配置文件：运行多个智能体

在同一台机器上运行多个独立的 Hermes 智能体——每个智能体都有自己的配置、API 密钥、记忆、会话、技能和网关。

## 什么是配置文件？

配置文件是一个完全隔离的 Hermes 环境。每个配置文件都有自己的目录，包含其专属的 `config.yaml`、`.env`、`SOUL.md`、记忆、会话、技能、定时任务和状态数据库。配置文件让你可以为不同目的运行独立的智能体——例如一个编程助手、一个个人机器人、一个研究助手——而不会产生任何交叉干扰。

当你创建一个配置文件时，它会自动成为一个独立的命令。创建一个名为 `coder` 的配置文件，你立刻就会拥有 `coder chat`、`coder setup`、`coder gateway start` 等命令。

## 快速开始

```bash
hermes profile create coder       # 创建配置文件 + "coder" 命令别名
coder setup                       # 配置 API 密钥和模型
coder chat                        # 开始聊天
```

就这样。`coder` 现在是一个完全独立的智能体。它有自己的配置、自己的记忆、自己的一切。

## 创建配置文件

### 空白配置文件

```bash
hermes profile create mybot
```

创建一个全新的配置文件，并预置了捆绑的技能。运行 `mybot setup` 来配置 API 密钥、模型和网关令牌。

### 仅克隆配置 (`--clone`)

```bash
hermes profile create work --clone
```

将你当前配置文件的 `config.yaml`、`.env` 和 `SOUL.md` 复制到新的配置文件中。使用相同的 API 密钥和模型，但会话和记忆是全新的。编辑 `~/.hermes/profiles/work/.env` 以使用不同的 API 密钥，或编辑 `~/.hermes/profiles/work/SOUL.md` 以赋予不同的个性。

### 克隆所有内容 (`--clone-all`)

```bash
hermes profile create backup --clone-all
```

复制**所有内容**——配置、API 密钥、个性、所有记忆、完整的会话历史、技能、定时任务、插件。一个完整的快照。适用于备份或分叉一个已有上下文的智能体。

### 从特定配置文件克隆

```bash
hermes profile create work --clone --clone-from coder
```

## 使用配置文件

### 命令别名

每个配置文件都会自动在 `~/.local/bin/<name>` 处获得一个命令别名：

```bash
coder chat                    # 与 coder 智能体聊天
coder setup                   # 配置 coder 的设置
coder gateway start           # 启动 coder 的网关
coder doctor                  # 检查 coder 的健康状况
coder skills list             # 列出 coder 的技能
coder config set model.model anthropic/claude-sonnet-4
```

该别名适用于所有 hermes 子命令——其底层原理就是 `hermes -p <name>`。

### `-p` 标志

你也可以在任何命令中显式指定目标配置文件：

```bash
hermes -p coder chat
hermes --profile=coder doctor
hermes chat -p coder -q "hello"    # 在任何位置都有效
```

### 粘性默认值 (`hermes profile use`)

```bash
hermes profile use coder
hermes chat                   # 现在目标指向 coder
hermes tools                  # 配置 coder 的工具
hermes profile use default    # 切换回默认配置
```

设置一个默认配置文件，这样普通的 `hermes` 命令就会指向该配置文件。类似于 `kubectl config use-context`。

### 了解当前状态

CLI 始终显示哪个配置文件是活跃的：

- **提示符**：显示 `coder ❯` 而不是 `❯`
- **横幅**：启动时显示 `Profile: coder`
- **`hermes profile`**：显示当前配置文件的名称、路径、模型、网关状态

## 运行网关

每个配置文件都将其网关作为一个独立的进程运行，并拥有自己的机器人令牌：

```bash
coder gateway start           # 启动 coder 的网关
assistant gateway start       # 启动 assistant 的网关（独立进程）
```

### 不同的机器人令牌

每个配置文件都有自己的 `.env` 文件。可以在其中配置不同的 Telegram/Discord/Slack 机器人令牌：

```bash
# 编辑 coder 的令牌
nano ~/.hermes/profiles/coder/.env

# 编辑 assistant 的令牌
nano ~/.hermes/profiles/assistant/.env
```

### 安全性：令牌锁定

如果两个配置文件意外使用了相同的机器人令牌，第二个网关将被阻止，并显示一个清晰的错误信息，指出冲突的配置文件名称。此功能支持 Telegram、Discord、Slack、WhatsApp 和 Signal。

### 持久化服务

```bash
coder gateway install         # 创建 hermes-gateway-coder systemd/launchd 服务
assistant gateway install     # 创建 hermes-gateway-assistant 服务
```

每个配置文件都有自己的服务名称。它们独立运行。

## 配置配置文件

每个配置文件都有自己的：

- **`config.yaml`** — 模型、提供商、工具集、所有设置
- **`.env`** — API 密钥、机器人令牌
- **`SOUL.md`** — 个性和指令

```bash
coder config set model.model anthropic/claude-sonnet-4
echo "你是一个专注的编程助手。" > ~/.hermes/profiles/coder/SOUL.md
```

## 更新

`hermes update` 会拉取一次代码（共享），并自动将新的捆绑技能同步到**所有**配置文件：

```bash
hermes update
# → 代码已更新 (12 次提交)
# → 技能已同步：default (已是最新), coder (+2 个新技能), assistant (+2 个新技能)
```

用户修改过的技能永远不会被覆盖。

## 管理配置文件
```bash
hermes profile list           # 显示所有配置文件及其状态
hermes profile show coder     # 查看单个配置文件的详细信息
hermes profile rename coder dev-bot   # 重命名（同时更新别名和服务）
hermes profile export coder   # 导出到 coder.tar.gz
hermes profile import coder.tar.gz   # 从归档文件导入
```

## 删除配置文件

```bash
hermes profile delete coder
```

此操作会停止网关、移除 systemd/launchd 服务、移除命令别名，并删除所有配置文件数据。系统会要求你输入配置文件名以确认。

使用 `--yes` 参数可跳过确认：`hermes profile delete coder --yes`

:::note
你不能删除默认配置文件 (`~/.hermes`)。若要移除所有内容，请使用 `hermes uninstall`。
:::

## 命令补全

```bash
# Bash
eval "$(hermes completion bash)"

# Zsh
eval "$(hermes completion zsh)"
```

将对应行添加到你的 `~/.bashrc` 或 `~/.zshrc` 文件中以实现持久化补全。支持在 `-p` 后补全配置文件名、配置文件子命令以及顶级命令。

## 工作原理

配置文件使用 `HERMES_HOME` 环境变量。当你运行 `coder chat` 时，包装脚本会在启动 hermes 之前设置 `HERMES_HOME=~/.hermes/profiles/coder`。由于代码库中有 119+ 个文件通过 `get_hermes_home()` 函数解析路径，所有内容都会自动限定在配置文件的目录下——包括配置、会话、记忆、技能、状态数据库、网关 PID、日志和定时任务。
默认配置文件就是 `~/.hermes` 本身。无需迁移——现有的安装以完全相同的方式工作。
