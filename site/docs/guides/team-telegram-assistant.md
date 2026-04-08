---
sidebar_position: 4
title: "教程：团队 Telegram 助手"
description: "逐步指导你设置一个 Telegram 机器人，供整个团队用于代码辅助、研究、系统管理等"
---

# 设置团队 Telegram 助手

本教程将引导你设置一个由 Hermes Agent 驱动的 Telegram 机器人，供多名团队成员共同使用。完成本教程后，你的团队将拥有一个共享的 AI 助手，他们可以通过私聊获取代码、研究、系统管理以及任何其他方面的帮助——并受每用户授权机制的保护。

## 我们要构建什么

一个具备以下功能的 Telegram 机器人：

- **任何获得授权的团队成员**都可以通过私聊（DM）寻求帮助——代码审查、研究、Shell 命令、调试
- **运行在你的服务器上**并拥有完整的工具访问权限——终端、文件编辑、网页搜索、代码执行
- **每用户会话**——每个人都有自己独立的对话上下文
- **默认安全**——只有经过批准的用户才能交互，支持两种授权方式
- **定时任务**——将每日站报、健康检查和提醒发送到团队频道

---

## 前提条件

在开始之前，请确保你拥有：

- **已安装 Hermes Agent** 的服务器或 VPS（不要用你的笔记本电脑——机器人需要保持运行）。如果你还没有安装，请参考 [安装指南](/getting-started/installation)。
- **一个 Telegram 账号**（作为机器人所有者）
- **已配置 LLM 提供商**——至少在 `~/.hermes/.env` 中配置了 OpenAI、Anthropic 或其他受支持提供商的 API 密钥

:::tip 提示
一个每月 5 美元的 VPS 足以运行网关。Hermes 本身非常轻量——LLM API 调用才是产生费用的地方，而这些调用是远程发生的。
:::

---

## 第 1 步：创建一个 Telegram 机器人

每个 Telegram 机器人都要从 **@BotFather** 开始——这是 Telegram 官方用于创建机器人的机器人。

1. **打开 Telegram** 并搜索 `@BotFather`，或者访问 [t.me/BotFather](https://t.me/BotFather)

2. **发送 `/newbot`** —— BotFather 会询问你两件事：
   - **显示名称（Display name）** —— 用户看到的名称（例如：`Team Hermes Assistant`）
   - **用户名（Username）** —— 必须以 `bot` 结尾（例如：`myteam_hermes_bot`）

3. **复制机器人令牌（Bot Token）** —— BotFather 会回复类似以下内容：
   ```
   Use this token to access the HTTP API:
   7123456789:AAH1bGciOiJSUzI1NiIsInR5cCI6Ikp...
   ```
   保存这个令牌——你在下一步中会用到它。

4. **设置描述**（可选但推荐）：
   ```
   /setdescription
   ```
   选择你的机器人，然后输入类似：
   ```
   Team AI assistant powered by Hermes Agent. DM me for help with code, research, debugging, and more.
   ```

5. **设置机器人命令**（可选——为用户提供命令菜单）：
   ```
   /setcommands
   ```
   选择你的机器人，然后粘贴：
   ```
   new - Start a fresh conversation
   model - Show or change the AI model
   status - Show session info
   help - Show available commands
   stop - Stop the current task
   ```

:::warning 警告
请务必保密你的机器人令牌。任何拥有该令牌的人都可以控制该机器人。如果泄露，请在 BotFather 中使用 `/revoke` 生成新令牌。
:::

---

## 第 2 步：配置网关

你有两个选择：交互式设置向导（推荐）或手动配置。

### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

这将通过方向键选择引导你完成所有设置。选择 **Telegram**，粘贴你的机器人令牌，并在提示时输入你的用户 ID。

### 选项 B：手动配置

将以下行添加到 `~/.hermes/.env`：

```bash
# 来自 BotFather 的 Telegram 机器人令牌
TELEGRAM_BOT_TOKEN=7123456789:AAH1bGciOiJSUzI1NiIsInR5cCI6Ikp...

# 你的 Telegram 用户 ID（数字）
TELEGRAM_ALLOWED_USERS=123456789
```

### 查找你的用户 ID

你的 Telegram 用户 ID 是一个数字值（不是你的用户名）。查找方法如下：

1. 在 Telegram 上给 [@userinfobot](https://t.me/userinfobot) 发消息
2. 它会立即回复你的数字用户 ID
3. 将该数字复制到 `TELEGRAM_ALLOWED_USERS` 中

:::info 信息
Telegram 用户 ID 是永久性的数字，如 `123456789`。它们与你的 `@username` 不同，后者是可以更改的。在白名单中请务必使用数字 ID。
:::

---

## 第 3 步：启动网关

### 快速测试

先在前台运行网关以确保一切正常：

```bash
hermes gateway
```

你应该会看到类似以下的输出：

```
[Gateway] Starting Hermes Gateway...
[Gateway] Telegram adapter connected
[Gateway] Cron scheduler started (tick every 60s)
```

打开 Telegram，找到你的机器人，并给它发送一条消息。如果它回复了，说明配置成功。按 `Ctrl+C` 停止运行。

### 生产环境：作为服务安装

为了实现跨重启的持久化部署：

```bash
hermes gateway install
sudo hermes gateway install --system   # 仅限 Linux：开机启动的系统服务
```

这将创建一个后台服务：默认在 Linux 上是用户级 **systemd** 服务，在 macOS 上是 **launchd** 服务，如果你传递了 `--system` 参数，则是开机启动的 Linux 系统服务。

```bash
# Linux — 管理默认用户服务
hermes gateway start
hermes gateway stop
hermes gateway status

# 查看实时日志
journalctl --user -u hermes-gateway -f

# SSH 退出后保持运行
sudo loginctl enable-linger $USER

# Linux 服务器 — 显式的系统服务命令
sudo hermes gateway start --system
sudo hermes gateway status --system
journalctl -u hermes-gateway -f
```

```bash
# macOS — 管理服务
hermes gateway start
hermes gateway stop
tail -f ~/.hermes/logs/gateway.log
```

:::tip macOS PATH 提示
launchd plist 会在安装时捕获你的 shell PATH，以便网关子进程能找到 Node.js 和 ffmpeg 等工具。如果你以后安装了新工具，请重新运行 `hermes gateway install` 来更新 plist。
:::

### 验证运行状态

```bash
hermes gateway status
```

然后在 Telegram 上给你的机器人发送一条测试消息。你应该会在几秒钟内收到回复。

---

## 第 4 步：设置团队访问权限

现在让我们给你的队友授权。有两种方法。

### 方法 A：静态白名单

收集每个团队成员的 Telegram 用户 ID（让他们给 [@userinfobot](https://t.me/userinfobot) 发消息），并将它们添加为逗号分隔的列表：

```bash
# 在 ~/.hermes/.env 中
TELEGRAM_ALLOWED_USERS=123456789,987654321,555555555
```

修改后重启网关：

```bash
hermes gateway stop && hermes gateway start
```

### 方法 B：私聊配对（推荐团队使用）

私聊配对（DM pairing）更加灵活——你不需要预先收集用户 ID。其工作原理如下：

1. **队友私聊机器人** —— 由于他们不在白名单中，机器人会回复一个一次性配对码：
   ```
   🔐 Pairing code: XKGH5N7P
   Send this code to the bot owner for approval.
   ```

2. **队友将代码发送给你**（通过任何渠道——Slack、邮件、当面告知）

3. **你在服务器上批准它**：
   ```bash
   hermes pairing approve telegram XKGH5N7P
   ```

4. **他们已加入** —— 机器人会立即开始响应他们的消息

**管理已配对用户：**

```bash
# 查看所有待处理和已批准的用户
hermes pairing list

# 撤销某人的访问权限
hermes pairing revoke telegram 987654321

# 清除过期的待处理代码
hermes pairing clear-pending
```

:::tip 提示
私聊配对非常适合团队，因为在添加新用户时不需要重启网关。批准会立即生效。
:::

### 安全注意事项

- **切勿在具有终端访问权限的机器人上设置 `GATEWAY_ALLOW_ALL_USERS=true`** —— 任何发现你机器人的人都可以在你的服务器上运行命令
- 配对码在 **1 小时**后过期，并使用加密随机性
- 速率限制可防止暴力破解：每用户每 10 分钟 1 次请求，每个平台最多 3 个待处理代码
- 5 次批准尝试失败后，该平台将进入 1 小时的锁定状态
- 所有配对数据都以 `chmod 0600` 权限存储

---

## 第 5 步：配置机器人

### 设置主频道（Home Channel）

**主频道**是机器人交付定时任务（cron job）结果和主动消息的地方。如果没有主频道，定时任务将无法发送输出。

**选项 1：** 在机器人作为成员的任何 Telegram 群组或聊天中使用 `/sethome` 命令。

**选项 2：** 在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="Team Updates"
```

要查找频道 ID，请将 [@userinfobot](https://t.me/userinfobot) 添加到群组中——它会报告该群组的聊天 ID。
### 配置工具进度显示

控制 Bot 在使用工具时显示的细节程度。在 `~/.hermes/config.yaml` 中设置：

```yaml
display:
  tool_progress: new    # off | new | all | verbose
```

| 模式 | 显示内容 |
|------|-------------|
| `off` | 仅显示最终回复 —— 不显示工具活动 |
| `new` | 每个新工具调用显示简短状态（推荐用于即时通讯场景） |
| `all` | 显示每个工具调用的详细信息 |
| `verbose` | 完整的工具输出，包括命令执行结果 |

用户也可以在聊天中使用 `/verbose` 命令针对当前会话进行更改。

### 使用 SOUL.md 设置性格

通过编辑 `~/.hermes/SOUL.md` 来自定义 Bot 的沟通方式：

完整指南请参阅 [在 Hermes 中使用 SOUL.md](/guides/use-soul-with-hermes)。

```markdown
# Soul
你是一个得力的团队助手。回复要简洁且专业。
代码请使用代码块。跳过客套话 —— 团队看重直接。
在调试时，先索要错误日志，不要盲目猜测解决方案。
```

### 添加项目上下文

如果你的团队专注于特定项目，可以创建上下文文件让 Bot 了解你的技术栈：

```markdown
<!-- ~/.hermes/AGENTS.md -->
# Team Context
- 我们使用 Python 3.12，搭配 FastAPI 和 SQLAlchemy
- 前端使用 React 和 TypeScript
- CI/CD 在 GitHub Actions 上运行
- 生产环境部署到 AWS ECS
- 总是建议为新代码编写测试
```

:::info
上下文文件会被注入到每个会话的系统提示词（system prompt）中。请保持简洁 —— 每一个字符都会占用你的 token 预算。
:::

---

## 第 6 步：设置定时任务

Gateway 运行后，你可以安排定期执行的任务，并将结果发送到团队频道。

### 每日站会总结

在 Telegram 上给 Bot 发消息：

```
每个工作日上午 9 点，检查 GitHub 仓库 github.com/myorg/myproject 并查看：
1. 过去 24 小时内打开/合并的 Pull requests
2. 创建或关闭的 Issues
3. main 分支上任何失败的 CI/CD 任务
以简短的站会风格生成总结。
```

Agent 会自动创建一个 cron 任务，并将结果发送到你发起请求的聊天窗口（或主频道）。

### 服务器健康检查

```
每 6 小时检查一次磁盘占用（使用 'df -h'）、内存（使用 'free -h'）
以及 Docker 容器状态（使用 'docker ps'）。
报告任何异常情况 —— 比如分区占用超过 80%、容器重启或内存占用过高。
```

### 管理定时任务

```bash
# 通过 CLI
hermes cron list          # 查看所有定时任务
hermes cron status        # 检查调度器是否正在运行

# 通过 Telegram 聊天
/cron list                # 查看任务
/cron remove <job_id>     # 删除任务
```

:::warning
Cron 任务的提示词运行在完全独立的会话中，没有之前对话的记忆。请确保每个提示词都包含 Agent 所需的**所有**上下文 —— 包括文件路径、URL、服务器地址和明确的指令。
:::

---

## 生产环境建议

### 使用 Docker 确保安全

对于团队共享的 Bot，建议使用 Docker 作为终端后端，这样 Agent 的命令会在容器中运行，而不是在宿主机上：

```bash
# 在 ~/.hermes/.env 中
TERMINAL_BACKEND=docker
TERMINAL_DOCKER_IMAGE=nikolaik/python-nodejs:python3.11-nodejs20
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
terminal:
  backend: docker
  container_cpu: 1
  container_memory: 5120
  container_persistent: true
```

这样，即使有人让 Bot 运行具有破坏性的命令，你的宿主机系统也是受保护的。

### 监控 Gateway

```bash
# 检查 gateway 是否正在运行
hermes gateway status

# 查看实时日志 (Linux)
journalctl --user -u hermes-gateway -f

# 查看实时日志 (macOS)
tail -f ~/.hermes/logs/gateway.log
```

### 保持 Hermes 更新

在 Telegram 中向 Bot 发送 `/update` —— 它会拉取最新版本并重启。或者在服务器上操作：

```bash
hermes update
hermes gateway stop && hermes gateway start
```

### 日志位置

| 内容 | 位置 |
|------|----------|
| Gateway 日志 | `journalctl --user -u hermes-gateway` (Linux) 或 `~/.hermes/logs/gateway.log` (macOS) |
| Cron 任务输出 | `~/.hermes/cron/output/{job_id}/{timestamp}.md` |
| Cron 任务定义 | `~/.hermes/cron/jobs.json` |
| 配对数据 | `~/.hermes/pairing/` |
| 会话历史 | `~/.hermes/sessions/` |

---

## 深入探索

你已经拥有了一个可以工作的团队 Telegram 助手。以下是后续可以探索的方向：

- **[安全指南](/user-guide/security)** —— 深入了解授权、容器隔离和命令审批
- **[消息 Gateway](/user-guide/messaging)** —— Gateway 架构、会话管理和聊天命令的完整参考
- **[Telegram 设置](/user-guide/messaging/telegram)** —— 平台特定细节，包括语音消息和 TTS
- **[定时任务](/user-guide/features/cron)** —— 带有交付选项和 cron 表达式的高级定时调度
- **[上下文文件](/user-guide/features/context-files)** —— 用于注入项目知识的 AGENTS.md、SOUL.md 和 .cursorrules
- **[性格设置](/user-guide/features/personality)** —— 内置性格预设和自定义角色定义
- **添加更多平台** —— 同一个 Gateway 可以同时运行 [Discord](/user-guide/messaging/discord)、[Slack](/user-guide/messaging/slack) 和 [WhatsApp](/user-guide/messaging/whatsapp)

---

*有问题或建议？请在 GitHub 上提交 issue —— 欢迎贡献代码。*
