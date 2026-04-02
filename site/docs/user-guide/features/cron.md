---
sidebar_position: 5
title: "定时任务（Cron）"
description: "使用自然语言调度自动化任务，通过一个 cron 工具管理它们，并附加一个或多个技能"
---

# 定时任务（Cron）

使用自然语言或 cron 表达式自动调度任务。Hermes 通过一个统一的 `cronjob` 工具提供 cron 管理，采用动作式操作，而不是分开的 schedule/list/remove 工具。

## 目前 cron 能做什么

Cron 任务可以：

- 调度一次性或周期性任务
- 暂停、恢复、编辑、触发和删除任务
- 给任务附加零个、一个或多个技能
- 将结果发送回原始聊天、本地文件或配置的平台目标
- 在新的 Agent 会话中运行，使用正常的静态工具列表

:::warning
Cron 运行的会话不能递归创建更多的 cron 任务。Hermes 会在 cron 执行中禁用 cron 管理工具，以防止无限调度循环。
:::

## 创建定时任务

### 在聊天中使用 `/cron`

```bash
/cron add 30m "提醒我检查构建情况"
/cron add "every 2h" "检查服务器状态"
/cron add "every 1h" "总结新的订阅内容" --skill blogwatcher
/cron add "every 1h" "使用多个技能并合并结果" --skill blogwatcher --skill find-nearby
```

### 通过独立 CLI

```bash
hermes cron create "every 2h" "检查服务器状态"
hermes cron create "every 1h" "总结新的订阅内容" --skill blogwatcher
hermes cron create "every 1h" "使用多个技能并合并结果" \
  --skill blogwatcher \
  --skill find-nearby \
  --name "技能组合"
```

### 通过自然对话

正常向 Hermes 询问：

```text
每天早上9点，检查 Hacker News 上的 AI 新闻，并通过 Telegram 给我发送摘要。
```

Hermes 会在内部使用统一的 `cronjob` 工具。

## 支持技能的 cron 任务

一个 cron 任务可以在运行提示前加载一个或多个技能。

### 单个技能

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="检查配置的订阅源并总结任何新内容。",
    schedule="0 9 * * *",
    name="早间订阅",
)
```

### 多个技能

技能按顺序加载。提示成为叠加在这些技能上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "find-nearby"],
    prompt="查找新的本地活动和有趣的附近地点，然后合并成一份简短的摘要。",
    schedule="every 6h",
    name="本地简报",
)
```

当你希望定时 Agent 继承可复用的工作流，而不必把完整技能文本塞进 cron 提示时，这非常有用。

## 编辑任务

你不需要删除再重新创建任务来修改它们。

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

- 重复使用 `--skill` 会替换任务附加的技能列表
- `--add-skill` 会追加到现有列表，不替换
- `--remove-skill` 移除指定的附加技能
- `--clear-skills` 移除所有附加技能

## 生命周期操作

Cron 任务现在拥有比创建/删除更完整的生命周期。

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

- `pause` — 保留任务但停止调度
- `resume` — 重新启用任务并计算下一次运行时间
- `run` — 在下一个调度周期触发任务
- `remove` — 完全删除任务

## 工作原理

**Cron 执行由网关守护进程处理。** 网关每 60 秒触发一次调度器，运行所有到期任务，且在隔离的 Agent 会话中执行。

```bash
hermes gateway install     # 安装为用户服务
sudo hermes gateway install --system   # Linux：服务器启动时的系统服务
hermes gateway             # 或前台运行

hermes cron list
hermes cron status
```

### 网关调度器行为

每次触发时，Hermes 会：

1. 从 `~/.hermes/cron/jobs.json` 加载任务
2. 检查 `next_run_at` 是否已到
3. 为每个到期任务启动一个新的 `AIAgent` 会话
4. 可选地将一个或多个附加技能注入该新会话
5. 运行提示直到完成
6. 发送最终响应
7. 更新运行元数据和下一次调度时间

`~/.hermes/cron/.tick.lock` 文件锁防止调度器重叠触发，避免同一批任务被重复执行。

## 结果发送选项

调度任务时，你可以指定输出发送到哪里：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 发送回任务创建的地方 | 消息平台默认 |
| `"local"` | 仅保存到本地文件（`~/.hermes/cron/output/`） | CLI 默认 |
| `"telegram"` | Telegram 主页频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"discord"` | Discord 主页频道 | 使用 `DISCORD_HOME_CHANNEL` |
| `"telegram:123456"` | 指定 Telegram 聊天 ID | 直接发送 |
| `"discord:987654"` | 指定 Discord 频道 ID | 直接发送 |

Agent 的最终响应会自动发送。你不需要在 cron 提示中调用 `send_message`。

### 响应包装

默认情况下，发送的 cron 输出会带有头部和尾部，方便接收者知道这是定时任务的内容：

```
Cronjob Response: 早间订阅
-------------

<agent 输出内容>

注意：Agent 无法看到此消息，因此无法对此作出回应。
```

如果想发送原始 Agent 输出而不带包装，可以将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### 静默抑制

如果 Agent 的最终响应以 `[SILENT]` 开头，则完全不发送消息。输出仍会保存在本地以供审计（`~/.hermes/cron/output/`），但不会发送到任何目标。

这适合只在出现异常时才报告的监控任务：

```text
检查 nginx 是否运行正常。如果一切正常，只回复 [SILENT]。
否则，报告问题。
```

失败的任务无论是否带 `[SILENT]` 都会发送消息，只有成功运行的任务可以静默。

## 调度格式

Agent 的最终响应会自动发送——你**不需要**在 cron 提示中包含 `send_message` 来发送相同目标。如果 cron 运行调用了 `send_message` 发送到调度器已指定的目标，Hermes 会跳过重复发送，并告诉模型把面向用户的内容放在最终响应里。`send_message` 只用于额外或不同的目标。

### 相对延迟（一次性）

```text
30m     → 30 分钟后运行一次
2h      → 2 小时后运行一次
1d      → 1 天后运行一次
```

### 间隔（周期性）

```text
every 30m    → 每 30 分钟运行一次
every 2h     → 每 2 小时运行一次
every 1d     → 每天运行一次
```

### Cron 表达式

```text
0 9 * * *       → 每天上午9点
0 9 * * 1-5     → 工作日每天上午9点
0 */6 * * *     → 每6小时一次
30 8 1 * *      → 每月1日8:30
0 0 * * 0       → 每周日午夜
```

### ISO 时间戳

```text
2026-03-15T09:00:00    → 2026年3月15日上午9点一次性运行
```

## 重复行为

| 调度类型 | 默认重复次数 | 行为 |
|--------------|----------------|----------|
| 一次性（`30m`，时间戳） | 1 | 运行一次 |
| 间隔（`every 2h`） | 永久 | 运行直到删除 |
| Cron 表达式 | 永久 | 运行直到删除 |

你可以覆盖它：

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

对于 `update`，传入 `skills=[]` 可以移除所有附加的技能。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json`。任务运行的输出保存到 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

存储采用原子文件写入，因此中断写入不会留下部分写入的任务文件。

## 独立完整的提示依然重要

:::warning 重要
Cron 任务在一个全新的 Agent 会话中运行。提示必须包含 Agent 需要的所有信息，除了附加技能已经提供的内容。
:::

**错误示范：** `"Check on that server issue"`

**正确示范：** `"SSH 登录到服务器 192.168.1.100，用户为 'deploy'，用 'systemctl status nginx' 检查 nginx 是否运行，并确认 https://example.com 返回 HTTP 200。"`

## 安全性

计划任务的提示在创建和更新时会被扫描，检测提示注入和凭证泄露模式。包含隐形 Unicode 技巧、SSH 后门尝试或明显的秘密泄露载荷的提示会被阻止。
