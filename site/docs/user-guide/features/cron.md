---
sidebar_position: 5
title: "定时任务 (Cron)"
description: "使用自然语言调度自动化任务，通过一个 cron 工具进行管理，并可挂载一个或多个技能"
---

# 定时任务 (Cron)

你可以使用自然语言或 cron 表达式来调度自动运行的任务。Hermes 通过统一的 `cronjob` 工具提供 cron 管理功能，采用操作风格的指令，无需使用单独的调度、列表或删除工具。

## Cron 目前的功能

Cron 任务可以：

- 调度单次或循环任务
- 暂停、恢复、编辑、触发和删除任务
- 为任务挂载零个、一个或多个技能
- 将结果返回至原始聊天窗口、本地文件或配置的平台目标
- 在全新的 Agent 会话中运行，并使用常规的静态工具列表

:::warning
Cron 运行的会话无法递归创建更多的 cron 任务。Hermes 会在 cron 执行期间禁用 cron 管理工具，以防止出现失控的调度循环。
:::

## 创建定时任务

### 在聊天中使用 `/cron`

```bash
/cron add 30m "Remind me to check the build"
/cron add "every 2h" "Check server status"
/cron add "every 1h" "Summarize new feed items" --skill blogwatcher
/cron add "every 1h" "Use both skills and combine the result" --skill blogwatcher --skill find-nearby
```

### 通过独立 CLI

```bash
hermes cron create "every 2h" "Check server status"
hermes cron create "every 1h" "Summarize new feed items" --skill blogwatcher
hermes cron create "every 1h" "Use both skills and combine the result" \
  --skill blogwatcher \
  --skill find-nearby \
  --name "Skill combo"
```

### 通过自然对话

像平时一样询问 Hermes：

```text
Every morning at 9am, check Hacker News for AI news and send me a summary on Telegram.
```

Hermes 会在内部使用统一的 `cronjob` 工具。

## 基于技能的 Cron 任务

Cron 任务可以在运行提示词之前加载一个或多个技能。

### 单个技能

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="Check the configured feeds and summarize anything new.",
    schedule="0 9 * * *",
    name="Morning feeds",
)
```

### 多个技能

技能会按顺序加载。提示词将作为叠加在这些技能之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "find-nearby"],
    prompt="Look for new local events and interesting nearby places, then combine them into one short brief.",
    schedule="every 6h",
    name="Local brief",
)
```

当你希望定时运行的 Agent 继承可复用的工作流，而又不想把完整的技能文本塞进 cron 提示词本身时，这种方式非常有用。

## 编辑任务

你无需删除并重新创建任务即可进行修改。

### 聊天

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "Use the revised task"
/cron edit <job_id> --skill blogwatcher --skill find-nearby
/cron edit <job_id> --remove-skill blogwatcher
/cron edit <job_id> --clear-skills
```

### 独立 CLI

```bash
hermes cron edit <job_id> --schedule "every 4h"
hermes cron edit <job_id> --prompt "Use the revised task"
hermes cron edit <job_id> --skill blogwatcher --skill find-nearby
hermes cron edit <job_id> --add-skill find-nearby
hermes cron edit <job_id> --remove-skill blogwatcher
hermes cron edit <job_id> --clear-skills
```

注意：

- 重复使用 `--skill` 会替换任务已挂载的技能列表
- `--add-skill` 会在现有列表后追加，而不会替换
- `--remove-skill` 用于移除特定的已挂载技能
- `--clear-skills` 用于移除所有已挂载的技能

## 生命周期操作

Cron 任务现在拥有比简单的创建/删除更完整的生命周期。

### 聊天

```bash
/cron list
/cron pause <job_id>
/cron resume <job_id>
/cron run <job_id>
/cron remove <job_id>
```

### 独立 CLI

```bash
hermes cron list
hermes cron pause <job_id>
hermes cron resume <job_id>
hermes cron run <job_id>
hermes cron remove <job_id>
hermes cron status
hermes cron tick
```

操作说明：

- `pause` — 保留任务但停止调度
- `resume` — 重新启用任务并计算下一次运行时间
- `run` — 在下一次调度周期触发任务
- `remove` — 完全删除任务

## 工作原理

**Cron 执行由网关守护进程处理。** 网关每 60 秒触发一次调度器，在隔离的 Agent 会话中运行所有到期的任务。

```bash
hermes gateway install     # 作为用户服务安装
sudo hermes gateway install --system   # Linux: 为服务器安装开机自启的系统服务
hermes gateway             # 或在前台运行

hermes cron list
hermes cron status
```

### 网关调度器行为

在每次触发时，Hermes 会：

1. 从 `~/.hermes/cron/jobs.json` 加载任务
2. 将 `next_run_at` 与当前时间进行比对
3. 为每个到期任务启动一个全新的 `AIAgent` 会话
4. 可选地将一个或多个挂载的技能注入到该新会话中
5. 运行提示词直到完成
6. 交付最终响应
7. 更新运行元数据和下一次调度时间

位于 `~/.hermes/cron/.tick.lock` 的文件锁可防止重叠的调度周期重复运行同一批任务。

## 交付选项

在调度任务时，你可以指定输出的去向：

| 选项 | 说明 | 示例 |
|--------|-------------|---------|
| `"origin"` | 返回任务创建的位置 | 消息平台上的默认值 |
| `"local"` | 仅保存到本地文件 (`~/.hermes/cron/output/`) | CLI 上的默认值 |
| `"telegram"` | Telegram 主频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定 Telegram 聊天 | 直接交付 |
| `"telegram:-100123:17585"` | 指定 Telegram 主题 | `chat_id:thread_id` 格式 |
| `"discord"` | Discord 主频道 | 使用 `DISCORD_HOME_CHANNEL` |
| `"discord:#engineering"` | 指定 Discord 频道 | 按频道名称 |
| `"slack"` | Slack 主频道 | |
| `"whatsapp"` | WhatsApp 主页 | |
| `"signal"` | Signal | |
| `"matrix"` | Matrix 主房间 | |
| `"mattermost"` | Mattermost 主频道 | |
| `"email"` | 电子邮件 | |
| `"sms"` | 通过 Twilio 发送短信 | |
| `"homeassistant"` | Home Assistant | |
| `"dingtalk"` | 钉钉 | |
| `"feishu"` | 飞书/Lark | |
| `"wecom"` | 企业微信 | |
| `"bluebubbles"` | BlueBubbles (iMessage) | |

Agent 的最终响应会自动交付。你无需在 cron 提示词中调用 `send_message`。

### 响应包装

默认情况下，交付的 cron 输出会带有页眉和页脚，以便接收者知道它来自定时任务：

```
Cronjob Response: Morning feeds
-------------

<agent output here>

Note: The agent cannot see this message, and therefore cannot respond to it.
```

若要交付原始的 Agent 输出而不带包装，请将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### 静默抑制

如果 Agent 的最终响应以 `[SILENT]` 开头，交付将被完全抑制。输出仍会保存在本地以供审计（位于 `~/.hermes/cron/output/`），但不会向交付目标发送任何消息。

这对于监控那些仅在出现问题时才需要报告的任务非常有用：

```text
Check if nginx is running. If everything is healthy, respond with only [SILENT].
Otherwise, report the issue.
```

失败的任务无论是否有 `[SILENT]` 标记都会进行交付——只有成功的运行才会被静默。

## 调度格式

Agent 的最终响应会自动交付——你**无需**在 cron 提示词中包含 `send_message` 来发送到同一目的地。如果 cron 运行调用了 `send_message` 到调度器已经交付的目标，Hermes 会跳过该重复发送，并指示模型将面向用户的内容放入最终响应中。仅在需要发送到额外或不同目标时才使用 `send_message`。

### 相对延迟（单次）

```text
30m     → 30 分钟后运行一次
2h      → 2 小时后运行一次
1d      → 1 天后运行一次
```

### 间隔（循环）

```text
every 30m    → 每 30 分钟一次
every 2h     → 每 2 小时一次
every 1d     → 每天一次
```

### Cron 表达式

```text
0 9 * * *       → 每天上午 9:00
0 9 * * 1-5     → 工作日上午 9:00
0 */6 * * *     → 每 6 小时一次
30 8 1 * *      → 每月 1 日上午 8:30
0 0 * * 0       → 每周日午夜
```
### ISO 时间戳

```text
2026-03-15T09:00:00    → 在 2026 年 3 月 15 日上午 9:00 执行一次
```

## 重复行为

| 调度类型 | 默认重复次数 | 行为 |
|--------------|----------------|----------|
| 单次执行 (`30m`，时间戳) | 1 | 执行一次 |
| 间隔执行 (`every 2h`) | 永久 | 持续执行直到被移除 |
| Cron 表达式 | 永久 | 持续执行直到被移除 |

你可以覆盖默认设置：

```python
cronjob(
    action="create",
    prompt="...",
    schedule="every 2h",
    repeat=5,
)
```

## 以编程方式管理任务

面向 Agent 的 API 是一个工具：

```python
cronjob(action="create", ...)
cronjob(action="list")
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```

对于 `update` 操作，传入 `skills=[]` 即可移除所有已关联的技能。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出会保存到 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

存储过程使用原子文件写入，因此即使写入中断，也不会留下损坏的任务文件。

## 独立的 Prompt 依然至关重要

:::warning 重要
Cron 任务会在一个全新的 Agent 会话中运行。Prompt 必须包含 Agent 所需的一切信息，除非这些信息已由关联的技能提供。
:::

**错误示例：** `"Check on that server issue"`（检查一下那个服务器问题）

**正确示例：** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`（以 'deploy' 用户 SSH 登录到服务器 192.168.1.100，使用 'systemctl status nginx' 检查 nginx 是否在运行，并验证 https://example.com 是否返回 HTTP 200。）

## 安全性

在创建和更新任务时，系统会扫描定时任务的 Prompt，以检测是否存在 Prompt 注入和凭据泄露模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显的秘密泄露载荷的 Prompt 将被拦截。
