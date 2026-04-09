---
sidebar_position: 1
title: "消息网关"
description: "通过 API 服务器，从 Telegram、Discord、Slack、WhatsApp、Signal、SMS、Email、Home Assistant、Mattermost、Matrix、DingTalk、Webhooks 或任何兼容 OpenAI 的前端与 Hermes 聊天 —— 架构与设置概览"
---

# 消息网关

你可以通过 Telegram、Discord、Slack、WhatsApp、Signal、SMS、Email、Home Assistant、Mattermost、Matrix、DingTalk、飞书/Lark、企业微信、BlueBubbles (iMessage) 或浏览器与 Hermes 聊天。网关是一个后台进程，它连接到你配置的所有平台，处理会话、运行定时任务并发送语音消息。

有关完整的语音功能集（包括 CLI 麦克风模式、消息中的语音回复以及 Discord 语音频道对话），请参阅 [语音模式](/user-guide/features/voice-mode) 和 [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)。

## 平台对比

| 平台 | 语音 | 图片 | 文件 | 线程 | 反应 | 输入状态 | 流式传输 |
|----------|:-----:|:------:|:-----:|:-------:|:---------:|:------:|:---------:|
| Telegram | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Discord | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Slack | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| WhatsApp | — | ✅ | ✅ | — | — | ✅ | ✅ |
| Signal | — | ✅ | ✅ | — | — | ✅ | ✅ |
| SMS | — | — | — | — | — | — | — |
| Email | — | ✅ | ✅ | ✅ | — | — | — |
| Home Assistant | — | — | — | — | — | — | — |
| Mattermost | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Matrix | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| DingTalk | — | — | — | — | — | ✅ | ✅ |
| Feishu/Lark | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| WeCom | ✅ | ✅ | ✅ | — | — | ✅ | ✅ |
| BlueBubbles | — | ✅ | ✅ | — | ✅ | ✅ | — |

**语音 (Voice)** = TTS 音频回复和/或语音消息转录。**图片 (Images)** = 发送/接收图片。**文件 (Files)** = 发送/接收文件附件。**线程 (Threads)** = 线程化对话。**反应 (Reactions)** = 消息上的表情符号反应。**输入状态 (Typing)** = 处理时的输入指示器。**流式传输 (Streaming)** = 通过编辑实现的消息渐进式更新。

## 架构

```mermaid
flowchart TB
    subgraph Gateway["Hermes 网关"]
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
    bb[BlueBubbles]
            api["API 服务器<br/>(兼容 OpenAI)"]
            wh[Webhooks]
        end

        store["会话存储<br/>(按聊天)"]
        agent["AIAgent<br/>run_agent.py"]
        cron["Cron 定时器<br/>每 60 秒触发"]
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

每个平台适配器接收消息，通过按聊天划分的会话存储进行路由，并将其分发给 AIAgent 进行处理。网关还运行 Cron 定时器，每 60 秒触发一次以执行到期的任务。

## 快速设置

配置消息平台最简单的方法是使用交互式向导：

```bash
hermes gateway setup        # 所有消息平台的交互式设置
```

它会引导你通过方向键选择来配置每个平台，显示已配置的平台，并在完成后提供启动/重启网关的选项。

## 网关命令

```bash
hermes gateway              # 在前台运行
hermes gateway setup        # 交互式配置消息平台
hermes gateway install      # 安装为用户服务 (Linux) / launchd 服务 (macOS)
sudo hermes gateway install --system   # 仅限 Linux：安装为开机自启的系统服务
hermes gateway start        # 启动默认服务
hermes gateway stop         # 停止默认服务
hermes gateway status       # 检查默认服务状态
hermes gateway status --system         # 仅限 Linux：显式检查系统服务
```

## 聊天命令（在消息应用内）

| 命令 | 描述 |
|---------|-------------|
| `/new` 或 `/reset` | 开始一段新的对话 |
| `/model [provider:model]` | 显示或更改模型（支持 `provider:model` 语法） |
| `/provider` | 显示可用提供商及其认证状态 |
| `/personality [name]` | 设置人格 |
| `/retry` | 重试上一条消息 |
| `/undo` | 撤销上一次交互 |
| `/status` | 显示会话信息 |
| `/stop` | 停止正在运行的 Agent |
| `/approve` | 批准待处理的危险命令 |
| `/deny` | 拒绝待处理的危险命令 |
| `/sethome` | 将此聊天设置为家庭频道 |
| `/compress` | 手动压缩对话上下文 |
| `/title [name]` | 设置或显示会话标题 |
| `/resume [name]` | 恢复之前命名的会话 |
| `/usage` | 显示此会话的 Token 使用量 |
| `/insights [days]` | 显示使用洞察和分析 |
| `/reasoning [level\|show\|hide]` | 更改推理力度或切换推理显示 |
| `/voice [on\|off\|tts\|join\|leave\|status]` | 控制消息语音回复和 Discord 语音频道行为 |
| `/rollback [number]` | 列出或恢复文件系统检查点 |
| `/background <prompt>` | 在独立的后台会话中运行提示词 |
| `/reload-mcp` | 从配置中重新加载 MCP 服务器 |
| `/update` | 将 Hermes Agent 更新到最新版本 |
| `/help` | 显示可用命令 |
| `/<skill-name>` | 调用任何已安装的技能 |
## 会话管理

### 会话持久化

会话会在消息之间持续存在，直到重置为止。Agent 会记住你的对话上下文。

### 重置策略

会话会根据可配置的策略进行重置：

| 策略 | 默认值 | 描述 |
|--------|---------|-------------|
| 每日 (Daily) | 凌晨 4:00 | 每天在特定时间重置 |
| 空闲 (Idle) | 1440 分钟 | 不活动 N 分钟后重置 |
| 两者 (Both) | (组合) | 触发条件满足其一即重置 |

在 `~/.hermes/gateway.json` 中配置各平台的覆盖设置：

```json
{
  "reset_by_platform": {
    "telegram": { "mode": "idle", "idle_minutes": 240 },
    "discord": { "mode": "idle", "idle_minutes": 60 }
  }
}
```

## 安全性

**默认情况下，网关会拒绝所有不在白名单中或未通过私信 (DM) 配对的用户。** 对于拥有终端访问权限的机器人来说，这是安全的默认设置。

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

# 或者允许
GATEWAY_ALLOWED_USERS=123456789,987654321

# 或者显式允许所有用户（对于拥有终端访问权限的机器人，不推荐这样做）：
GATEWAY_ALLOW_ALL_USERS=true
```

### 私信 (DM) 配对（白名单的替代方案） {#dm-pairing-alternative-to-allowlists}

无需手动配置用户 ID，未知用户在私信机器人时会收到一个一次性配对码：

```bash
# 用户会看到："Pairing code: XKGH5N7P"
# 你可以使用以下命令批准他们：
hermes pairing approve telegram XKGH5N7P

# 其他配对命令：
hermes pairing list          # 查看待处理和已批准的用户
hermes pairing revoke telegram 123456789  # 移除访问权限
```

配对码 1 小时后过期，受速率限制，并使用加密随机数生成。

## 中断 Agent

在 Agent 工作时发送任何消息即可中断它。关键行为如下：

- **正在进行的终端命令会被立即终止**（先发送 SIGTERM，1 秒后发送 SIGKILL）
- **工具调用会被取消** —— 只有当前正在执行的工具会运行，其余的会被跳过
- **多条消息会被合并** —— 中断期间发送的消息会被合并为一个提示词
- **`/stop` 命令** —— 中断执行且不会排队后续消息

## 工具进度通知

在 `~/.hermes/config.yaml` 中控制工具活动的显示程度：

```yaml
display:
  tool_progress: all    # off | new | all | verbose
  tool_progress_command: false  # 设置为 true 以在消息中启用 /verbose
```

启用后，机器人在工作时会发送状态消息：

```text
💻 `ls -la`...
🔍 web_search...
📄 web_extract...
🐍 execute_code...
```

## 后台会话 {#background-sessions}

在独立的后台会话中运行提示词，这样 Agent 就可以独立工作，同时保持你的主聊天窗口响应：

```
/background Check all servers in the cluster and report any that are down
```

Hermes 会立即确认：

```
🔄 Background task started: "Check all servers in the cluster..."
   Task ID: bg_143022_a1b2c3
```

### 工作原理

每个 `/background` 提示词都会生成一个**独立的 Agent 实例**，并异步运行：

- **隔离会话** —— 后台 Agent 拥有自己的会话和对话历史。它不知道你当前的聊天上下文，仅接收你提供的提示词。
- **相同配置** —— 继承当前网关设置中的模型、提供商、工具集、推理设置和提供商路由。
- **非阻塞** —— 你的主聊天窗口保持完全可交互。在它工作时，你可以发送消息、运行其他命令或启动更多后台任务。
- **结果交付** —— 任务完成后，结果会发送回你发出命令的**同一个聊天或频道**，并以 "✅ Background task complete" 为前缀。如果失败，你会看到 "❌ Background task failed" 以及错误信息。

### 后台进程通知
当运行后台会话的 Agent 使用 `terminal(background=true)` 启动长时间运行的进程（如服务器、构建任务等）时，网关可以将状态更新推送到你的聊天窗口。你可以通过 `~/.hermes/config.yaml` 中的 `display.background_process_notifications` 进行控制：

```yaml
display:
  background_process_notifications: all    # all | result | error | off
```

| 模式 | 你将收到的内容 |
|------|-----------------|
| `all` | 运行输出更新 **以及** 最终完成消息（默认） |
| `result` | 仅最终完成消息（无论退出代码为何） |
| `error` | 仅在退出代码非零时发送最终消息 |
| `off` | 不发送任何进程监控消息 |

你也可以通过环境变量进行设置：

```bash
HERMES_BACKGROUND_NOTIFICATIONS=result
```

### 使用场景

- **服务器监控** — "/background 检查所有服务的健康状况，如果有服务宕机请提醒我"
- **长时间构建** — "/background 构建并部署暂存环境"，同时你可以继续进行其他对话
- **研究任务** — "/background 研究竞争对手的定价并汇总成表格"
- **文件操作** — "/background 将 ~/Downloads 中的照片按日期整理到文件夹中"

:::tip
消息平台上的后台任务采用“即发即忘”模式——你无需等待或主动查看。任务完成后，结果会自动出现在同一个聊天窗口中。
:::

## 服务管理

### Linux (systemd)

```bash
hermes gateway install               # 安装为用户服务
hermes gateway start                 # 启动服务
hermes gateway stop                  # 停止服务
hermes gateway status                # 检查状态
journalctl --user -u hermes-gateway -f  # 查看日志

# 启用 lingering（注销后保持运行）
sudo loginctl enable-linger $USER

# 或者安装一个开机自启的系统服务，但仍以你的用户身份运行
sudo hermes gateway install --system
sudo hermes gateway start --system
sudo hermes gateway status --system
journalctl -u hermes-gateway -f
```

在笔记本电脑和开发机上使用用户服务。在 VPS 或无头主机（headless hosts）上使用系统服务，这样它们可以在开机时自动恢复，而无需依赖 systemd 的 linger 功能。

除非有特殊需求，否则请避免同时安装用户级和系统级网关单元。如果 Hermes 检测到两者同时存在，会发出警告，因为启动/停止/状态查询的行为会变得模糊不清。

:::info 多重安装
如果你在同一台机器上运行多个 Hermes 安装实例（使用不同的 `HERMES_HOME` 目录），每个实例都会拥有自己的 systemd 服务名称。默认的 `~/.hermes` 使用 `hermes-gateway`；其他安装实例使用 `hermes-gateway-<hash>`。`hermes gateway` 命令会自动定位到当前 `HERMES_HOME` 对应的正确服务。
:::

### macOS (launchd)

```bash
hermes gateway install               # 安装为 launchd agent
hermes gateway start                 # 启动服务
hermes gateway stop                  # 停止服务
hermes gateway status                # 检查状态
tail -f ~/.hermes/logs/gateway.log   # 查看日志
```

生成的 plist 文件位于 `~/Library/LaunchAgents/ai.hermes.gateway.plist`。它包含三个环境变量：

- **PATH** — 安装时的完整 shell PATH，并在开头添加了 venv 的 `bin/` 和 `node_modules/.bin`。这确保了用户安装的工具（如 Node.js、ffmpeg 等）可供网关子进程（如 WhatsApp 桥接器）使用。
- **VIRTUAL_ENV** — 指向 Python 虚拟环境，以便工具能正确解析包。
- **HERMES_HOME** — 将网关的作用域限定在你的 Hermes 安装目录。

:::tip 安装后的 PATH 变更
launchd 的 plist 是静态的——如果你在设置网关后安装了新工具（例如通过 nvm 安装了新的 Node.js 版本，或通过 Homebrew 安装了 ffmpeg），请再次运行 `hermes gateway install` 以捕获更新后的 PATH。网关会自动检测到过时的 plist 并重新加载。
:::

:::info 多重安装
与 Linux 的 systemd 服务一样，每个 `HERMES_HOME` 目录都会获得自己的 launchd 标签。默认的 `~/.hermes` 使用 `ai.hermes.gateway`；其他安装实例使用 `ai.hermes.gateway-<suffix>`。
:::
## 平台专属工具集

每个平台都有其对应的工具集：

| 平台 | 工具集 | 功能 |
|----------|---------|--------------|
| CLI | `hermes-cli` | 完全访问权限 |
| Telegram | `hermes-telegram` | 包含终端在内的完整工具 |
| Discord | `hermes-discord` | 包含终端在内的完整工具 |
| WhatsApp | `hermes-whatsapp` | 包含终端在内的完整工具 |
| Slack | `hermes-slack` | 包含终端在内的完整工具 |
| Signal | `hermes-signal` | 包含终端在内的完整工具 |
| SMS | `hermes-sms` | 包含终端在内的完整工具 |
| Email | `hermes-email` | 包含终端在内的完整工具 |
| Home Assistant | `hermes-homeassistant` | 完整工具 + HA 设备控制 (ha_list_entities, ha_get_state, ha_call_service, ha_list_services) |
| Mattermost | `hermes-mattermost` | 包含终端在内的完整工具 |
| Matrix | `hermes-matrix` | 包含终端在内的完整工具 |
| DingTalk | `hermes-dingtalk` | 包含终端在内的完整工具 |
| Feishu/Lark | `hermes-feishu` | 包含终端在内的完整工具 |
| WeCom | `hermes-wecom` | 包含终端在内的完整工具 |
| BlueBubbles | `hermes-bluebubbles` | 包含终端在内的完整工具 |
| API Server | `hermes` (默认) | 包含终端在内的完整工具 |
| Webhooks | `hermes-webhook` | 包含终端在内的完整工具 |

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
- [飞书 (Feishu/Lark) 设置](feishu.md)
- [企业微信 (WeCom) 设置](wecom.md)
- [BlueBubbles 设置 (iMessage)](bluebubbles.md)
- [Open WebUI + API Server](open-webui.md)
- [Webhooks](webhooks.md)
