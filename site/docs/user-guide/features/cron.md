---
sidebar_position: 5
title: "定时任务 (Cron)"
description: "使用自然语言安排自动化任务，通过一个 cron 工具进行管理，并可附加一个或多个技能"
---

# 定时任务 (Cron)

使用自然语言或 cron 表达式安排任务自动运行。Hermes 通过一个统一的 `cronjob` 工具来管理 cron，它采用动作风格的操作，而不是独立的 schedule/list/remove 工具。

## Cron 当前能做什么

Cron 任务可以：

- 安排一次性或重复性任务
- 暂停、恢复、编辑、触发和移除任务
- 为零个、一个或多个任务附加技能
- 将结果发送回原始聊天、本地文件或配置的平台目标
- 在全新的代理会话中运行，并拥有正常的静态工具列表

:::warning
由 Cron 运行的会话不能递归创建更多 cron 任务。Hermes 在 cron 执行过程中禁用了 cron 管理工具，以防止无限循环的调度。
:::

## 创建定时任务

### 在聊天中使用 `/cron`

```bash
/cron add 30m "提醒我检查构建"
/cron add "every 2h" "检查服务器状态"
/cron add "every 1h" "总结新的订阅源内容" --skill blogwatcher
/cron add "every 1h" "同时使用两个技能并合并结果" --skill blogwatcher --skill find-nearby
```

### 通过独立 CLI

```bash
hermes cron create "every 2h" "检查服务器状态"
hermes cron create "every 1h" "总结新的订阅源内容" --skill blogwatcher
hermes cron create "every 1h" "同时使用两个技能并合并结果" \
  --skill blogwatcher \
  --skill find-nearby \
  --name "技能组合"
```

### 通过自然对话

像平常一样询问 Hermes：

```text
每天早上 9 点，检查 Hacker News 上的 AI 新闻，并通过 Telegram 给我发送摘要。
```

Hermes 将在内部使用统一的 `cronjob` 工具。

## 基于技能的 Cron 任务

Cron 任务可以在运行提示词之前加载一个或多个技能。

### 单个技能

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="检查配置的订阅源，并总结任何新内容。",
    schedule="0 9 * * *",
    name="早晨订阅源",
)
```

### 多个技能

技能按顺序加载。提示词将成为叠加在这些技能之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "find-nearby"],
    prompt="查找新的本地事件和附近有趣的地方，然后将它们合并成一份简短的简报。",
    schedule="every 6h",
    name="本地简报",
)
```

当你希望一个定时代理继承可重用的工作流，而不必将完整的技能文本塞进 cron 提示词本身时，这很有用。

## 编辑任务

你不需要为了修改任务而删除并重新创建它们。

### 聊天

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "使用修订后的任务"
/cron edit <job_id> --skill blogwatcher --skill find-nearby
/cron edit <job_id> --remove-skill blogwatcher
/cron edit <job_id> --clear-skills
```

### 独立 CLI

```bash
hermes cron edit <job_id> --schedule "every 4h"
hermes cron edit <job_id> --prompt "使用修订后的任务"
hermes cron edit <job_id> --skill blogwatcher --skill find-nearby
hermes cron edit <job_id> --add-skill find-nearby
hermes cron edit <job_id> --remove-skill blogwatcher
hermes cron edit <job_id> --clear-skills
```

注意：

- 重复使用 `--skill` 会替换任务已附加的技能列表
- `--add-skill` 会追加到现有列表，而不替换它
- `--remove-skill` 会移除特定的已附加技能
- `--clear-skills` 会移除所有已附加技能

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

它们的作用：

- `pause` — 保留任务但停止调度它
- `resume` — 重新启用任务并计算下一次运行时间
- `run` — 在下一个调度器周期触发任务
- `remove` — 完全删除任务

## 工作原理

**Cron 执行由网关守护进程处理。** 网关每 60 秒触发一次调度器，在隔离的代理会话中运行所有到期的任务。

```bash
hermes gateway install     # 安装为用户服务
sudo hermes gateway install --system   # Linux：为服务器安装开机启动的系统服务
hermes gateway             # 或者在前台运行

hermes cron list
hermes cron status
```

### 网关调度器行为

每次触发时，Hermes 会：

1.  从 `~/.hermes/cron/jobs.json` 加载任务
2.  根据当前时间检查 `next_run_at`
3.  为每个到期任务启动一个全新的 `AIAgent` 会话
4.  可选地将一个或多个附加技能注入到该新会话中
5.  运行提示词直至完成
6.  交付最终响应
7.  更新运行元数据和下一次计划时间

位于 `~/.hermes/cron/.tick.lock` 的文件锁可以防止重叠的调度器触发导致同一批任务被重复运行。

## 交付选项

安排任务时，你需要指定输出发送到哪里：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 发送回任务创建的地方 | 在消息平台上的默认选项 |
| `"local"` | 仅保存到本地文件 (`~/.hermes/cron/output/`) | 在 CLI 上的默认选项 |
| `"telegram"` | Telegram 主频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"discord"` | Discord 主频道 | 使用 `DISCORD_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定的特定 Telegram 聊天 | 直接交付 |
| `"discord:987654"` | 通过 ID 指定的特定 Discord 频道 | 直接交付 |

代理的最终响应会自动交付。你不需要在 cron 提示词中调用 `send_message`。

## 调度格式

代理的最终响应会自动交付 — 你**不**需要为了同一个目的地而在 cron 提示词中包含 `send_message`。如果 cron 运行调用了 `send_message` 到调度器已经要交付的完全相同的目标，Hermes 会跳过那个重复的发送，并告诉模型将面向用户的内容放在最终响应中。仅在需要发送到额外或不同目标时才使用 `send_message`。

### 相对延迟（一次性）

```text
30m     → 30 分钟后运行一次
2h      → 2 小时后运行一次
1d      → 1 天后运行一次
```

### 间隔（重复性）

```text
every 30m    → 每 30 分钟
every 2h     → 每 2 小时
every 1d     → 每天
```

### Cron 表达式

```text
0 9 * * *       → 每天上午 9:00
0 9 * * 1-5     → 工作日上午 9:00
0 */6 * * *     → 每 6 小时
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
| 间隔 (`every 2h`) | 永远 | 运行直到被移除 |
| Cron 表达式 | 永远 | 运行直到被移除 |

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

面向代理的 API 是一个工具：

```python
cronjob(action="create", ...)
cronjob(action="list")
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```

对于 `update`，传递 `skills=[]` 可以移除所有附加技能。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出保存在 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

存储使用原子文件写入，因此中断的写入不会留下部分写入的任务文件。

## 自包含的提示词仍然重要

:::warning 重要
Cron 任务在完全全新的代理会话中运行。提示词必须包含代理所需的一切，除了已附加技能提供的内容。
:::

**不好：** `"检查那个服务器问题"`

**好：** `"以用户 'deploy' 身份 SSH 登录服务器 192.168.1.100，使用 'systemctl status nginx' 检查 nginx 是否在运行，并验证 https://example.com 返回 HTTP 200。"`

## 安全性

定时任务的提示词在创建和更新时会进行扫描，以检测提示词注入和凭证泄露的模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显秘密泄露载荷的提示词会被阻止。
