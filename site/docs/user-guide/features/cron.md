---
sidebar_position: 5
title: "定时任务 (Cron)"
description: "使用自然语言调度自动化任务，通过一个 cron 工具进行管理，并附加一个或多个技能"
---

# 定时任务 (Cron)

使用自然语言或 cron 表达式调度自动运行的任务。Hermes 通过单一的 `cronjob` 工具提供 cron 管理功能，采用操作风格的指令，而非分散的调度/列表/移除工具。

## Cron 目前的功能

Cron 任务可以：

- 调度单次或循环任务
- 暂停、恢复、编辑、触发和移除任务
- 为任务附加零个、一个或多个技能
- 将结果发送回原始聊天窗口、本地文件或配置的平台目标
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

### 从独立 CLI 创建

```bash
hermes cron create "every 2h" "Check server status"
hermes cron create "every 1h" "Summarize new feed items" --skill blogwatcher
hermes cron create "every 1h" "Use both skills and combine the result" \
  --skill blogwatcher \
  --skill find-nearby \
  --name "Skill combo"
```

### 通过自然对话创建

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

- 重复使用 `--skill` 会替换任务已附加的技能列表
- `--add-skill` 会在现有列表后追加，而不会替换
- `--remove-skill` 用于移除特定的已附加技能
- `--clear-skills` 用于移除所有已附加技能

## 生命周期操作

Cron 任务现在拥有比简单的创建/移除更完整的生命周期。

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
- `run` — 在下一次调度器触发时立即执行任务
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
4. 可选地将一个或多个附加技能注入到该新会话中
5. 运行提示词直到完成
6. 交付最终响应
7. 更新运行元数据和下一次调度时间

位于 `~/.hermes/cron/.tick.lock` 的文件锁可防止重叠的调度触发导致同一批任务被重复运行。

## 交付选项

在调度任务时，你可以指定输出的去向：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 返回任务创建的位置 | 消息平台上的默认值 |
| `"local"` | 仅保存到本地文件 (`~/.hermes/cron/output/`) | CLI 上的默认值 |
| `"telegram"` | Telegram 主频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定 Telegram 聊天 | 直接交付 |
| `"telegram:-100123:17585"` | 指定 Telegram 主题 | `chat_id:thread_id` 格式 |
| `"discord"` | Discord 主频道 | 使用 `DISCORD_HOME_CHANNEL` |
| `"discord:#engineering"` | 指定 Discord 频道 | 按频道名称 |
| `"slack"` | Slack 主频道 | |
| `"whatsapp"` | WhatsApp 主频道 | |
| `"signal"` | Signal | |
| `"matrix"` | Matrix 主房间 | |
| `"mattermost"` | Mattermost 主频道 | |
| `"email"` | 电子邮件 | |
| `"sms"` | 通过 Twilio 发送短信 | |
| `"homeassistant"` | Home Assistant | |
| `"dingtalk"` | 钉钉 | |
| `"feishu"` | 飞书/Lark | |
| `"wecom"` | 企业微信 | |
| `"weixin"` | 微信 | |
| `"bluebubbles"` | BlueBubbles (iMessage) | |

Agent 的最终响应会自动交付。你无需在 cron 提示词中调用 `send_message`。

### 响应包装

默认情况下，交付的 cron 输出会包含页眉和页脚，以便接收者知道它来自定时任务：

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

失败的任务无论是否有 `[SILENT]` 标记都会进行交付——只有成功的运行可以被静默。

## 脚本超时

预运行脚本（通过 `script` 参数附加）的默认超时时间为 120 秒。如果你的脚本需要更长时间（例如，为了包含随机延迟以避免类似机器人的定时模式），你可以增加此设置：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 分钟
```

或者设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。解析顺序为：环境变量 → config.yaml → 120秒默认值。

## 提供商恢复

Cron 任务会继承你配置的后备提供商和凭据池轮换策略。如果主 API 密钥达到速率限制或提供商返回错误，cron Agent 可以：

- **回退到备用提供商**（如果你在 `config.yaml` 中配置了 `fallback_providers` 或旧版的 `fallback_model`）
- **轮换到下一个凭据**（在你的 [凭据池](/user-guide/features/credential-pools) 中针对同一提供商）
这意味着高频或高峰时段运行的 cron 任务更具弹性——单个受限的速率键（rate-limited key）不会导致整个任务运行失败。

## 调度格式

Agent 的最终响应会自动发送——你**不需要**在 cron 提示词中为同一个目标包含 `send_message`。如果 cron 运行调用了 `send_message` 到调度程序已经要发送的目标，Hermes 会跳过该重复发送，并告知模型将面向用户的内容放入最终响应中。仅在需要发送到额外或不同目标时才使用 `send_message`。

### 相对延迟（一次性）

```text
30m     → 30 分钟后运行一次
2h      → 2 小时后运行一次
1d      → 1 天后运行一次
```

### 间隔（周期性）

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
2026-03-15T09:00:00    → 2026 年 3 月 15 日上午 9:00 运行一次
```

## 重复行为

| 调度类型 | 默认重复次数 | 行为 |
|--------------|----------------|----------|
| 一次性 (`30m`, 时间戳) | 1 | 运行一次 |
| 间隔 (`every 2h`) | 永久 | 持续运行直到被移除 |
| Cron 表达式 | 永久 | 持续运行直到被移除 |

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

面向 Agent 的 API 是一种工具：

```python
cronjob(action="create", ...)
cronjob(action="list")
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```

对于 `update`，传入 `skills=[]` 可移除所有关联的技能。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出保存到 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

存储使用原子文件写入，因此中断的写入不会留下部分写入的任务文件。

## 独立的提示词依然重要

:::warning 重要
Cron 任务在全新的 Agent 会话中运行。提示词必须包含 Agent 所需的一切信息，除非这些信息已由关联的技能提供。
:::

**错误示例：** `"检查那个服务器问题"`

**正确示例：** `"以用户 'deploy' SSH 登录到服务器 192.168.1.100，使用 'systemctl status nginx' 检查 nginx 是否正在运行，并验证 https://example.com 是否返回 HTTP 200。"`

## 安全性

在创建和更新时，会对计划任务的提示词进行扫描，以检测提示词注入（prompt-injection）和凭据泄露（credential-exfiltration）模式。包含不可见的 Unicode 技巧、SSH 后门尝试或明显的秘密泄露载荷的提示词将被拦截。
