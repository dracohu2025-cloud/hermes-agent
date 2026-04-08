---
sidebar_position: 5
title: "定时任务 (Cron)"
description: "使用自然语言安排自动化任务，通过统一的 cron 工具进行管理，并可附加一个或多个 skill"
---

# 定时任务 (Cron)

使用自然语言或 cron 表达式安排任务自动运行。Hermes 通过单一的 `cronjob` 工具公开 cron 管理功能，采用动作式（action-style）操作，而不是分成独立的 schedule/list/remove 工具。

## Cron 目前的功能

Cron 任务可以：

- 安排一次性或周期性任务
- 暂停、恢复、编辑、触发和删除任务
- 为任务附加零个、一个或多个 skill
- 将结果发送回原始会话、本地文件或配置的平台目标
- 在全新的 Agent 会话中运行，并带有标准的静态工具列表

:::warning
由 Cron 运行的会话不能递归创建更多 cron 任务。Hermes 在 cron 执行期间会禁用 cron 管理工具，以防止出现失控的调度循环。
:::

## 创建定时任务

### 在聊天中使用 `/cron`

```bash
/cron add 30m "提醒我检查构建情况"
/cron add "every 2h" "检查服务器状态"
/cron add "every 1h" "总结新的 feed 条目" --skill blogwatcher
/cron add "every 1h" "同时使用两个 skill 并合并结果" --skill blogwatcher --skill find-nearby
```

### 通过独立 CLI

```bash
hermes cron create "every 2h" "检查服务器状态"
hermes cron create "every 1h" "总结新的 feed 条目" --skill blogwatcher
hermes cron create "every 1h" "同时使用两个 skill 并合并结果" \
  --skill blogwatcher \
  --skill find-nearby \
  --name "Skill combo"
```

### 通过自然语言对话

正常询问 Hermes：

```text
每天早上 9 点，检查 Hacker News 上的 AI 新闻并给我发送一份 Telegram 摘要。
```

Hermes 会在内部使用统一的 `cronjob` 工具。

## 由 Skill 支持的 Cron 任务

Cron 任务可以在运行 prompt 之前加载一个或多个 skill。

### 单个 Skill

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="检查配置的 feed 并总结任何新内容。",
    schedule="0 9 * * *",
    name="Morning feeds",
)
```

### 多个 Skill

Skill 按顺序加载。Prompt 成为叠加在这些 skill 之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "find-nearby"],
    prompt="寻找新的本地活动和有趣的附近地点，然后将它们合并成一份简短的简报。",
    schedule="every 6h",
    name="Local brief",
)
```

当你希望定时 Agent 继承可重用的工作流，而又不想将完整的 skill 文本塞进 cron prompt 本身时，这非常有用。

## 编辑任务

你不需要为了修改任务而删除并重新创建它们。

### 聊天

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "使用修改后的任务"
/cron edit <job_id> --skill blogwatcher --skill find-nearby
/cron edit <job_id> --remove-skill blogwatcher
/cron edit <job_id> --clear-skills
```

### 独立 CLI

```bash
hermes cron edit <job_id> --schedule "every 4h"
hermes cron edit <job_id> --prompt "使用修改后的任务"
hermes cron edit <job_id> --skill blogwatcher --skill find-nearby
hermes cron edit <job_id> --add-skill find-nearby
hermes cron edit <job_id> --remove-skill blogwatcher
hermes cron edit <job_id> --clear-skills
```

注意：

- 重复使用 `--skill` 会替换该任务已附加的 skill 列表
- `--add-skill` 会追加到现有列表，而不是替换
- `--remove-skill` 移除特定的已附加 skill
- `--clear-skills` 移除所有已附加的 skill

## 生命周期操作

Cron 任务现在拥有比单纯的创建/删除更完整的生命周期。

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

功能说明：

- `pause` — 保留任务但停止调度
- `resume` — 重新启用任务并计算下次运行时间
- `run` — 在下一次调度器 tick 时触发任务
- `remove` — 彻底删除任务

## 工作原理

**Cron 的执行由 gateway 守护进程处理。** Gateway 每 60 秒 tick 一次调度器，在隔离的 Agent 会话中运行任何到期的任务。

```bash
hermes gateway install     # 作为用户服务安装
sudo hermes gateway install --system   # Linux：为服务器安装开机自启的系统服务
hermes gateway             # 或者在前台运行

hermes cron list
hermes cron status
```

### Gateway 调度器行为

在每次 tick 时，Hermes 会：

1. 从 `~/.hermes/cron/jobs.json` 加载任务
2. 根据当前时间检查 `next_run_at`
3. 为每个到期的任务启动一个新的 `AIAgent` 会话
4. （可选）将一个或多个附加的 skill 注入到该新会话中
5. 运行 prompt 直至完成
6. 交付最终响应
7. 更新运行元数据和下次调度时间

位于 `~/.hermes/cron/.tick.lock` 的文件锁可防止重叠的调度器 tick 重复运行同一批任务。

## 交付选项

在安排任务时，你可以指定输出的去向：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 回到创建任务的地方 | 消息平台上的默认值 |
| `"local"` | 仅保存到本地文件 (`~/.hermes/cron/output/`) | CLI 上的默认值 |
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
| `"feishu"` | 飞书 | |
| `"wecom"` | 企业微信 | |

Agent 的最终响应会自动交付。你不需要在 cron prompt 中调用 `send_message`。

### 响应包装

默认情况下，交付的 cron 输出会包装页眉和页脚，以便接收者知道它来自定时任务：

```
Cronjob Response: Morning feeds
-------------

<此处为 Agent 输出>

注意：Agent 无法看到此消息，因此无法对其进行回复。
```

如果要交付不带包装的原始 Agent 输出，请将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### 静默抑制

如果 Agent 的最终响应以 `[SILENT]` 开头，则会完全抑制交付。输出仍会保存在本地以供审计（在 `~/.hermes/cron/output/` 中），但不会向交付目标发送任何消息。

这对于仅在出现问题时才需要报告的监控任务非常有用：

```text
检查 nginx 是否正在运行。如果一切正常，仅回复 [SILENT]。
否则，报告问题。
```

失败的任务总是会交付，无论是否有 `[SILENT]` 标记 —— 只有成功的运行才能被静默。

## 调度格式

Agent 的最终响应会自动交付 —— 你**不需要**在发往同一目的地的 cron prompt 中包含 `send_message`。如果一次 cron 运行调用 `send_message` 发往调度器已经要交付的目标，Hermes 会跳过该重复发送，并告诉模型将面向用户的内容放在最终响应中。仅在需要发送到额外或不同的目标时才使用 `send_message`。

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
0 9 * * *       → 每天早上 9:00
0 9 * * 1-5     → 工作日早上 9:00
0 */6 * * *     → 每 6 小时一次
30 8 1 * *      → 每月 1 号早上 8:30
0 0 * * 0       → 每周日午夜
```

### ISO 时间戳
```text
2026-03-15T09:00:00    → 2026年3月15日上午9:00执行一次
```

## 重复行为

| 调度类型 | 默认重复次数 | 行为 |
|--------------|----------------|----------|
| 单次执行 (`30m`, 时间戳) | 1 | 运行一次 |
| 间隔执行 (`every 2h`) | 永久 | 持续运行直到被移除 |
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

## 通过编程管理任务

面向 Agent 的 API 是一项核心工具：

```python
cronjob(action="create", ...)
cronjob(action="list")
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```

对于 `update` 操作，传入 `skills=[]` 可以移除所有关联的技能。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出结果保存在 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

存储采用原子文件写入方式，因此中断的写入操作不会留下损坏的任务文件。

## 提示词（Prompt）的自包含性依然重要

:::warning 重要
Cron 任务在完全全新的 Agent 会话中运行。提示词必须包含 Agent 所需的所有信息（关联技能已提供的信息除外）。
:::

**错误示例：** `"检查那个服务器问题"`

**正确示例：** `"以 'deploy' 用户身份 SSH 登录服务器 192.168.1.100，使用 'systemctl status nginx' 检查 nginx 是否正在运行，并验证 https://example.com 是否返回 HTTP 200。"`

## 安全性

在创建和更新定时任务时，系统会扫描提示词是否存在提示词注入（prompt-injection）和凭据外泄模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显的机密外泄负载的提示词将被拦截。
