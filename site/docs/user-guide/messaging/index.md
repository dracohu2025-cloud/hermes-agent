---
sidebar_position: 1
title: "消息网关"
description: "通过 Telegram、Discord、Slack、WhatsApp、Signal、SMS、Email、Home Assistant、Mattermost、Matrix、DingTalk、Webhooks 或任何 OpenAI 兼容的前端与 Hermes 聊天——架构与设置概述"
---

# 消息网关

通过 Telegram、Discord、Slack、WhatsApp、Signal、SMS、Email、Home Assistant、Mattermost、Matrix、DingTalk、飞书/Lark、企业微信或你的浏览器与 Hermes 聊天。网关是一个单一的后台进程，连接到所有你配置的平台，处理会话，运行定时任务，并传递语音消息。

要使用完整的语音功能集——包括 CLI 麦克风模式、消息中的语音回复以及 Discord 语音频道对话——请参阅[语音模式](/docs/user-guide/features/voice-mode)和[使用 Hermes 的语音模式](/docs/guides/use-voice-mode-with-hermes)。

## 架构

```mermaid
flowchart TB
    subgraph Gateway["Hermes Gateway"]
        subgraph Adapters["平台适配器"]
            tg[Telegram]
            dc[Discord]
            wa[WhatsApp]
            sl[Slack]
            sig[Signal]
            sms[SMS]
            em[Email]
            ha[Home Assistant]
            mm[Mattermost]
            mx[Matrix]
            dt[DingTalk]
    fs[Feishu/Lark]
    wc[WeCom]
            api["API Server<br/>(OpenAI-compatible)"]
            wh[Webhooks]
        end

        store["Session store<br/>per chat"]
        agent["AIAgent<br/>run_agent.py"]
        cron["Cron scheduler<br/>ticks every 60s"]
    end

    tg --> store
    dc --> store
    wa --> store
    sl --> store
    sig --> store
    sms --> store
    em --> store
    ha --> store
    mm --> store
    mx --> store
    dt --> store
    api --> store
    wh --> store
    store --> agent
    cron --> store
```

每个平台适配器接收消息，通过每个聊天的会话存储路由它们，并将它们分派给 AIAgent 进行处理。网关还运行定时任务调度器，每 60 秒触发一次以执行任何到期的任务。

## 快速设置

配置消息平台最简单的方法是使用交互式向导：

```bash
hermes gateway setup        # 交互式设置所有消息平台
```

这将引导你使用方向键选择来配置每个平台，显示哪些平台已配置，并在完成后提供启动/重启网关的选项。

## 网关命令

```bash
hermes gateway              # 在前台运行
hermes gateway setup        # 交互式配置消息平台
hermes gateway install      # 安装为用户服务 (Linux) / launchd 服务 (macOS)
sudo hermes gateway install --system   # 仅限 Linux：安装启动时系统服务
hermes gateway start        # 启动默认服务
hermes gateway stop         # 停止默认服务
hermes gateway status       # 检查默认服务状态
hermes gateway status --system         # 仅限 Linux：显式检查系统服务状态
```

## 聊天命令（在消息平台内）

| 命令 | 描述 |
|---------|-------------|
| `/new` 或 `/reset` | 开始一个新的对话 |
| `/model [provider:model]` | 显示或更改模型（支持 `provider:model` 语法） |
| `/provider` | 显示可用的提供商及其认证状态 |
| `/personality [name]` | 设置一个个性 |
| `/retry` | 重试上一条消息 |
| `/undo` | 移除最后一次交互 |
| `/status` | 显示会话信息 |
| `/stop` | 停止正在运行的智能体 |
| `/approve` | 批准一个待处理的危险命令 |
| `/deny` | 拒绝一个待处理的危险命令 |
| `/sethome` | 将此聊天设置为家庭频道 |
| `/compress` | 手动压缩对话上下文 |
| `/title [name]` | 设置或显示会话标题 |
| `/resume [name]` | 恢复一个之前命名的会话 |
| `/usage` | 显示此会话的令牌使用情况 |
| `/insights [days]` | 显示使用洞察和分析 |
| `/reasoning [level\|show\|hide]` | 更改推理努力程度或切换推理显示 |
| `/voice [on\|off\|tts\|join\|leave\|status]` | 控制消息语音回复和 Discord 语音频道行为 |
| `/rollback [number]` | 列出或恢复文件系统检查点 |
| `/background <prompt>` | 在单独的背景会话中运行一个提示 |
| `/reload-mcp` | 从配置重新加载 MCP 服务器 |
| `/update` | 将 Hermes Agent 更新到最新版本 |
| `/help` | 显示可用命令 |
| `/<skill-name>` | 调用任何已安装的技能 |

## 会话管理

### 会话持久化

会话在消息之间持续存在，直到被重置。智能体会记住你的对话上下文。

### 重置策略

会话根据可配置的策略重置：

| 策略 | 默认值 | 描述 |
|--------|---------|-------------|
| 每日 | 凌晨 4:00 | 每天在特定小时重置 |
| 闲置 | 1440 分钟 | 在 N 分钟不活动后重置 |
| 两者 | (组合) | 任一条件先触发则重置 |

在 `~/.hermes/gateway.json` 中配置每个平台的覆盖设置：

```json
{
  "reset_by_platform": {
    "telegram": { "mode": "idle", "idle_minutes": 240 },
    "discord": { "mode": "idle", "idle_minutes": 60 }
  }
}
```

## 安全性

**默认情况下，网关会拒绝所有不在允许列表中或未通过私信配对的用户。** 对于具有终端访问权限的机器人来说，这是安全的默认设置。

```bash
# 限制为特定用户（推荐）：
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=123456789012345678
SIGNAL_ALLOWED_USERS=+155****4567,+155****6543
SMS_ALLOWED_USERS=+155****4567,+155****6543
EMAIL_ALLOWED_USERS=trusted@example.com,colleague@work.com
MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c
MATRIX_ALLOWED_USERS=@alice:matrix.org
DINGTALK_ALLOWED_USERS=user-id-1

# 或者全局允许
GATEWAY_ALLOWED_USERS=123456789,987654321

# 或者显式允许所有用户（对于具有终端访问权限的机器人不推荐）：
GATEWAY_ALLOW_ALL_USERS=true
```

### 私信配对（替代允许列表） {#dm-pairing-alternative-to-allowlists}

无需手动配置用户 ID，未知用户向机器人发送私信时会收到一个一次性配对码：

```bash
# 用户看到："配对码：XKGH5N7P"
# 你可以通过以下命令批准他们：
hermes pairing approve telegram XKGH5N7P

# 其他配对命令：
hermes pairing list          # 查看待处理和已批准的用户
hermes pairing revoke telegram 123456789  # 移除访问权限
```

配对码在 1 小时后过期，有速率限制，并使用加密随机数生成。

## 中断智能体

在智能体工作时发送任何消息即可中断它。关键行为：

- **正在进行的终端命令会立即被终止**（SIGTERM，1 秒后 SIGKILL）
- **工具调用被取消**——只有当前正在执行的那个会运行，其余的被跳过
- **多条消息被合并**——中断期间发送的消息会被合并成一个提示
- **`/stop` 命令**——中断但不排队后续消息

## 工具进度通知

在 `~/.hermes/config.yaml` 中控制工具活动的显示程度：

```yaml
display:
  tool_progress: all    # off | new | all | verbose
  tool_progress_command: false  # 设置为 true 以在消息中启用 /verbose 命令
```

启用后，机器人会在工作时发送状态消息：

```text
💻 `ls -la`...
🔍 web_search...
📄 web_extract...
🐍 execute_code...
```

## 背景会话 {#background-sessions}

在单独的背景会话中运行一个提示，这样智能体可以独立处理它，而你的主聊天保持响应：

```
/background 检查集群中的所有服务器并报告任何宕机的服务器
```

Hermes 会立即确认：

```
🔄 后台任务已启动："检查集群中的所有服务器..."
   任务 ID：bg_143022_a1b2c3
```

### 工作原理

每个 `/background` 提示都会生成一个**单独的智能体实例**，该实例异步运行：

- **隔离的会话**——后台智能体拥有自己的会话和自己的对话历史。它不知道你当前的聊天上下文，只接收你提供的提示。
- **相同的配置**——继承你当前的模型、提供商、工具集、推理设置以及来自当前网关设置的提供商路由。
- **非阻塞**——你的主聊天保持完全交互性。在它工作时，你可以发送消息、运行其他命令或启动更多后台任务。
- **结果传递**——当任务完成时，结果会发送回你发出命令的**同一个聊天或频道**，并带有“✅ 后台任务完成”前缀。如果失败，你会看到“❌ 后台任务失败”以及错误信息。

### 后台进程通知

当运行后台会话的智能体使用 `terminal(background=true)` 启动长时间运行的进程（服务器、构建等）时，网关可以向你的聊天推送状态更新。通过 `~/.hermes/config.yaml` 中的 `display.background_process_notifications` 来控制此行为：

```yaml
display:
  background_process_notifications: all    # all | result | error | off
```

| 模式 | 你收到的内容 |
|------|-----------------|
| `all` | 运行输出更新**以及**最终完成消息（默认） |
| `result` | 仅最终完成消息（无论退出代码如何） |
| `error` | 仅当退出代码非零时的最终消息 |
| `off` | 完全不接收进程监视器消息 |

你也可以通过环境变量设置：

```bash
HERMES_BACKGROUND_NOTIFICATIONS=result
```

### 使用场景

- **服务器监控**——"/background 检查所有服务的健康状况，如果有任何服务宕机就提醒我"
- **长时间构建**——"/background 构建并部署预发布环境"，同时你可以继续聊天
- **研究任务**——"/background 研究竞争对手定价并用表格总结"
- **文件操作**——"/background 按日期将 ~/Downloads 中的照片整理到文件夹中"

:::tip
消息平台上的后台任务是即发即弃的——你不需要等待或检查它们。任务完成后，结果会自动到达同一个聊天中。
:::

## 服务管理

### Linux (systemd)

```bash
hermes gateway install               # 安装为用户服务
hermes gateway start                 # 启动服务
hermes gateway stop                  # 停止服务
hermes gateway status                # 检查状态
journalctl --user -u hermes-gateway -f  # 查看日志

# 启用 linger（注销后保持运行）
sudo loginctl enable-linger $USER

# 或者安装一个启动时系统服务，但仍以你的用户身份运行
sudo hermes gateway install --system
sudo hermes gateway start --system
sudo hermes gateway status --system
journalctl -u hermes-gateway -f
```

在笔记本电脑和开发机上使用用户服务。在 VPS 或无头主机上使用系统服务，这些主机应在启动时恢复，而不依赖 systemd linger。

除非你确实需要，否则避免同时安装用户和系统网关单元。如果 Hermes 检测到两者，它会发出警告，因为启动/停止/状态行为会变得不明确。

:::info 多个安装
如果你在同一台机器上运行多个 Hermes 安装（使用不同的 `HERMES_HOME` 目录），每个都有自己的 systemd 服务名称。默认的 `~/.hermes` 使用 `hermes-gateway`；其他安装使用 `hermes-gateway-<hash>`。`hermes gateway` 命令会自动针对你当前 `HERMES_HOME` 的正确服务。
:::

### macOS (launchd)

```bash
hermes gateway install               # 安装为 launchd 代理
hermes gateway start                 # 启动服务
hermes gateway stop                  # 停止服务
hermes gateway status                # 检查状态
tail -f ~/.hermes/logs/gateway.log   # 查看日志
```

生成的 plist 位于 `~/Library/LaunchAgents/ai.hermes.gateway.plist`。它包含三个环境变量：

- **PATH**——安装时你的完整 shell PATH，并预置了 venv 的 `bin/` 和 `node_modules/.bin`。这确保用户安装的工具（Node.js、ffmpeg 等）对网关子进程（如 WhatsApp 桥接器）可用。
- **VIRTUAL_ENV**——指向 Python 虚拟环境，以便工具可以正确解析包。
- **HERMES_HOME**——将网关范围限定到你的 Hermes 安装。

:::tip 安装后的 PATH 变更
launchd plist 是静态的——如果你在设置网关后安装了新工具（例如通过 nvm 安装新的 Node.js 版本，或通过 Homebrew 安装 ffmpeg），请再次运行 `hermes gateway install` 以捕获更新后的 PATH。网关会检测到过时的 plist 并自动重新加载。
:::
:::info 多个安装实例
与 Linux 的 systemd 服务类似，每个 `HERMES_HOME` 目录都有其自己的 launchd 标签。默认的 `~/.hermes` 使用 `ai.hermes.gateway`；其他安装实例则使用 `ai.hermes.gateway-<后缀>`。
:::

## 平台特定工具集

每个平台都有其对应的工具集：

| 平台 | 工具集 | 能力 |
|----------|---------|--------------|
| CLI | `hermes-cli` | 完全访问权限 |
| Telegram | `hermes-telegram` | 完整工具集，包括终端 |
| Discord | `hermes-discord` | 完整工具集，包括终端 |
| WhatsApp | `hermes-whatsapp` | 完整工具集，包括终端 |
| Slack | `hermes-slack` | 完整工具集，包括终端 |
| Signal | `hermes-signal` | 完整工具集，包括终端 |
| SMS | `hermes-sms` | 完整工具集，包括终端 |
| Email | `hermes-email` | 完整工具集，包括终端 |
| Home Assistant | `hermes-homeassistant` | 完整工具集 + HA 设备控制 (ha_list_entities, ha_get_state, ha_call_service, ha_list_services) |
| Mattermost | `hermes-mattermost` | 完整工具集，包括终端 |
| Matrix | `hermes-matrix` | 完整工具集，包括终端 |
| 钉钉 (DingTalk) | `hermes-dingtalk` | 完整工具集，包括终端 |
| 飞书/ Lark | `hermes-feishu` | 完整工具集，包括终端 |
| 企业微信 (WeCom) | `hermes-wecom` | 完整工具集，包括终端 |
| API 服务器 | `hermes` (默认) | 完整工具集，包括终端 |
| Webhooks | `hermes-webhook` | 完整工具集，包括终端 |

## 后续步骤

- [Telegram 设置](telegram.md)
- [Discord 设置](discord.md)
- [Slack 设置](slack.md)
- [WhatsApp 设置](whatsapp.md)
- [Signal 设置](signal.md)
- [SMS 设置 (Twilio)](sms.md)
- [Email 设置](email.md)
- [Home Assistant 集成](homeassistant.md)
- [Mattermost 设置](mattermost.md)
- [Matrix 设置](matrix.md)
- [钉钉 (DingTalk) 设置](dingtalk.md)
- [飞书/ Lark 设置](feishu.md)
- [企业微信 (WeCom) 设置](wecom.md)
- [Open WebUI + API 服务器](open-webui.md)
- [Webhooks](webhooks.md)
