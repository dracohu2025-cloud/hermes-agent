---
sidebar_position: 5
title: "定时任务 (Cron)"
description: "使用自然语言安排自动化任务，通过一个 cron 工具进行管理，并可附加一个或多个技能"
---

<a id="scheduled-tasks-cron"></a>
# 定时任务 (Cron)

使用自然语言或 cron 表达式安排任务自动运行。Hermes 通过一个统一的 `cronjob` 工具来管理 cron，它采用动作风格的操作，而不是独立的 schedule/list/remove 工具。

<a id="what-cron-can-do-now"></a>
## 当前 cron 的功能

Cron 任务可以：

- 安排一次性或重复性任务
- 暂停、恢复、编辑、触发和删除任务
- 为零个、一个或多个任务附加技能
- 将结果发送回原始聊天、本地文件或配置的平台目标
- 在全新的 Agent 会话中运行，并拥有正常的静态工具列表

:::warning
Cron 运行的会话不能递归创建更多 cron 任务。Hermes 在 cron 执行过程中禁用了 cron 管理工具，以防止失控的调度循环。
:::

<a id="creating-scheduled-tasks"></a>
## 创建定时任务

<a id="in-chat-with-cron"></a>
### 在聊天中使用 `/cron`

```bash
/cron add 30m "提醒我检查构建"
/cron add "every 2h" "检查服务器状态"
/cron add "every 1h" "总结新的订阅项" --skill blogwatcher
/cron add "every 1h" "使用两个技能并合并结果" --skill blogwatcher --skill maps
```

<a id="from-the-standalone-cli"></a>
### 从独立 CLI

```bash
hermes cron create "every 2h" "检查服务器状态"
hermes cron create "every 1h" "总结新的订阅项" --skill blogwatcher
hermes cron create "every 1h" "使用两个技能并合并结果" \
  --skill blogwatcher \
  --skill maps \
  --name "技能组合"
```

<a id="through-natural-conversation"></a>
### 通过自然对话

像平常一样询问 Hermes：

```text
每天早上 9 点，检查 Hacker News 上的 AI 新闻，并通过 Telegram 给我发送摘要。
```

Hermes 会在内部使用统一的 `cronjob` 工具。

<a id="skill-backed-cron-jobs"></a>
## 基于技能的 Cron 任务

Cron 任务可以在运行提示词之前加载一个或多个技能。

<a id="single-skill"></a>
### 单个技能

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="检查配置的订阅源并总结任何新内容。",
    schedule="0 9 * * *",
    name="Morning feeds",
)
```

<a id="multiple-skills"></a>
### 多个技能

技能按顺序加载。提示词将成为叠加在这些技能之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="查找新的本地事件和附近有趣的地方，然后将它们合并成一份简短的简报。",
    schedule="every 6h",
    name="Local brief",
)
```

当你希望一个定时 Agent 继承可重用的工作流，而不必将完整的技能文本塞进 cron 提示词本身时，这非常有用。

<a id="editing-jobs"></a>
## 编辑任务

你不需要为了修改任务而删除并重新创建它们。

<a id="chat"></a>
### 聊天

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "使用修订后的任务"
/cron edit <job_id> --skill blogwatcher --skill maps
/cron edit <job_id> --remove-skill blogwatcher
/cron edit <job_id> --clear-skills
```
<a id="standalone-cli"></a>
### 独立 CLI

```bash
hermes cron edit <job_id> --schedule "every 4h"
hermes cron edit <job_id> --prompt "Use the revised task"
hermes cron edit <job_id> --skill blogwatcher --skill maps
hermes cron edit <job_id> --add-skill maps
hermes cron edit <job_id> --remove-skill blogwatcher
hermes cron edit <job_id> --clear-skills
```

注意：

- 重复使用 `--skill` 会替换任务关联的技能列表
- `--add-skill` 会追加到现有列表，不会替换它
- `--remove-skill` 会移除指定的关联技能
- `--clear-skills` 会移除所有关联的技能

<a id="lifecycle-actions"></a>
## 生命周期操作

Cron 任务现在拥有比简单的创建/删除更完整的生命周期。

<a id="chat"></a>
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

它们的作用：

- `pause` — 保留任务但停止调度它
- `resume` — 重新启用任务并计算下一次运行时间
- `run` — 在调度器下一次 tick 时触发任务
- `remove` — 完全删除任务

<a id="how-it-works"></a>
## 工作原理

**Cron 执行由网关守护进程处理。** 网关每 60 秒触发一次调度器，在独立的 Agent 会话中运行所有到期的任务。

```bash
hermes gateway install     # 安装为用户服务
sudo hermes gateway install --system   # Linux：为服务器安装开机自启的系统服务
hermes gateway             # 或者在前台运行

hermes cron list
hermes cron status
```

<a id="gateway-scheduler-behavior"></a>
### 网关调度器行为

每次 tick 时，Hermes 会：

1.  从 `~/.hermes/cron/jobs.json` 加载任务
2.  根据当前时间检查 `next_run_at`
3.  为每个到期任务启动一个新的 `AIAgent` 会话
4.  （可选）将一个或多个关联技能注入到该新会话中
5.  运行提示词直至完成
6.  交付最终响应
7.  更新运行元数据和下一次计划时间

`~/.hermes/cron/.tick.lock` 处的文件锁可以防止重叠的调度器 tick 重复运行同一批任务。

<a id="delivery-options"></a>
## 交付选项

在调度任务时，你需要指定输出发送到哪里：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 发送回任务创建的地方 | 消息平台的默认选项 |
| `"local"` | 仅保存到本地文件 (`~/.hermes/cron/output/`) | CLI 的默认选项 |
| `"telegram"` | Telegram 主频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定特定的 Telegram 聊天 | 直接交付 |
| `"telegram:-100123:17585"` | 特定的 Telegram 话题 | `chat_id:thread_id` 格式 |
| `"discord"` | Discord 主频道 | 使用 `DISCORD_HOME_CHANNEL` |
| `"discord:#engineering"` | 特定的 Discord 频道 | 通过频道名称 |
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
| `"qqbot"` | QQ 机器人 (腾讯 QQ) | |
Agent 的最终响应会自动发送。你无需在 cron 提示中调用 `send_message`。

<a id="response-wrapping"></a>
### 响应包装

默认情况下，发送的 cron 输出会附带页眉和页脚包装，以便接收者知道它来自计划任务：

```
Cronjob Response: Morning feeds
-------------

<agent output here>

Note: The agent cannot see this message, and therefore cannot respond to it.
```

要发送未经包装的原始 agent 输出，请将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

<a id="silent-suppression"></a>
### 静默抑制

如果 agent 的最终响应以 `[SILENT]` 开头，则会完全抑制发送。输出仍会本地保存以供审计（在 `~/.hermes/cron/output/` 目录下），但不会向发送目标发送任何消息。

这对于仅应在出现问题时才报告的监控任务很有用：

```text
检查 nginx 是否在运行。如果一切正常，请仅用 [SILENT] 响应。
否则，报告问题。
```

失败的任务无论 `[SILENT]` 标记如何都会发送——只有成功的运行才能被静默。

<a id="script-timeout"></a>
## 脚本超时

预运行脚本（通过 `script` 参数附加）的默认超时时间为 120 秒。如果你的脚本需要更长时间——例如，为了包含随机延迟以避免类似机器人的时间模式——你可以增加此值：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 分钟
```

或者设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。优先级顺序是：环境变量 → config.yaml → 120 秒默认值。

<a id="provider-recovery"></a>
## 供应商恢复

Cron 任务继承你配置的备用供应商和凭据池轮换。如果主 API 密钥被限速或供应商返回错误，cron agent 可以：

- **回退到备用供应商**，如果你在 `config.yaml` 中配置了 `fallback_providers`（或旧的 `fallback_model`）
- **轮换到同一供应商的 [凭据池](/user-guide/configuration#credential-pool-strategies) 中的下一个凭据**

这意味着高频率运行或在高峰时段运行的 cron 任务更具弹性——单个被限速的密钥不会导致整个运行失败。

<a id="schedule-formats"></a>
## 调度格式

Agent 的最终响应会自动发送——你**无需**在 cron 提示中为同一目标包含 `send_message`。如果 cron 运行调用 `send_message` 到调度器已经要发送的精确目标，Hermes 会跳过该重复发送，并指示模型将面向用户的内容放在最终响应中。仅对额外或不同的目标使用 `send_message`。
<a id="relative-delays-one-shot"></a>
### 相对延迟（一次性）

```text
30m     → 30 分钟后运行一次
2h      → 2 小时后运行一次
1d      → 1 天后运行一次
```

<a id="intervals-recurring"></a>
### 间隔（重复）

```text
every 30m    → 每 30 分钟
every 2h     → 每 2 小时
every 1d     → 每天
```

<a id="cron-expressions"></a>
### Cron 表达式

```text
0 9 * * *       → 每天上午 9:00
0 9 * * 1-5     → 工作日（周一至周五）上午 9:00
0 */6 * * *     → 每 6 小时
30 8 1 * *      → 每月 1 日上午 8:30
0 0 * * 0       → 每周日午夜
```

<a id="iso-timestamps"></a>
### ISO 时间戳

```text
2026-03-15T09:00:00    → 2026 年 3 月 15 日上午 9:00 运行一次
```

<a id="repeat-behavior"></a>
## 重复行为

| 计划类型 | 默认重复次数 | 行为 |
|--------------|----------------|----------|
| 一次性 (`30m`, 时间戳) | 1 | 运行一次 |
| 间隔 (`every 2h`) | forever | 持续运行，直到被移除 |
| Cron 表达式 | forever | 持续运行，直到被移除 |

你可以覆盖默认行为：

```python
cronjob(
    action="create",
    prompt="...",
    schedule="every 2h",
    repeat=5,
)
```

<a id="managing-jobs-programmatically"></a>
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

对于 `update` 操作，传递 `skills=[]` 可以移除所有附加的技能。

<a id="job-storage"></a>
## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出保存在 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

存储使用原子文件写入，因此中断的写入不会留下部分写入的任务文件。

<a id="self-contained-prompts-still-matter"></a>
## 自包含的提示词仍然很重要

:::warning 重要
<a id="important"></a>
Cron 任务在一个全新的 Agent 会话中运行。提示词必须包含 Agent 所需的一切，除了已附加技能提供的内容。
:::

**不好的例子：** `"Check on that server issue"`

**好的例子：** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`

<a id="security"></a>
## 安全性

在创建和更新时，计划任务的提示词会被扫描，以检测提示词注入和凭据泄露的模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显秘密泄露负载的提示词会被阻止。
