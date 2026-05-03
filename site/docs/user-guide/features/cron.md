---
sidebar_position: 5
title: "定时任务 (Cron)"
description: "用自然语言调度自动化任务，通过一个 cron 工具统一管理，并可附加一个或多个技能"
---

# 定时任务 (Cron) {#scheduled-tasks-cron}

使用自然语言或 cron 表达式来调度自动运行的任务。Hermes 通过一个统一的 `cronjob` 工具来管理 cron，采用动作式操作，而不是分开的 schedule/list/remove 工具。

## 当前 cron 能做什么 {#what-cron-can-do-now}

Cron 任务可以：

- 调度一次性或重复性任务
- 暂停、恢复、编辑、触发和删除任务
- 为任务附加零个、一个或多个技能
- 将结果返回给原始聊天、本地文件或配置的平台目标
- 在带有常规静态工具列表的新 Agent 会话中运行

:::warning
Cron 运行的会话不能递归创建更多 cron 任务。Hermes 在 cron 执行过程中禁用了 cron 管理工具，以防止失控的调度循环。
:::

## 创建定时任务 {#creating-scheduled-tasks}

### 在聊天中使用 `/cron` {#in-chat-with-cron}

```bash
/cron add 30m "Remind me to check the build"
/cron add "every 2h" "Check server status"
/cron add "every 1h" "Summarize new feed items" --skill blogwatcher
/cron add "every 1h" "Use both skills and combine the result" --skill blogwatcher --skill maps
```

### 从独立 CLI 创建 {#from-the-standalone-cli}

```bash
hermes cron create "every 2h" "Check server status"
hermes cron create "every 1h" "Summarize new feed items" --skill blogwatcher
hermes cron create "every 1h" "Use both skills and combine the result" \
  --skill blogwatcher \
  --skill maps \
  --name "Skill combo"
```

### 通过自然对话创建 {#through-natural-conversation}

直接向 Hermes 提出要求：

```text
Every morning at 9am, check Hacker News for AI news and send me a summary on Telegram.
```

Hermes 会在内部使用统一的 `cronjob` 工具。

## 带技能的 Cron 任务 {#skill-backed-cron-jobs}

Cron 任务可以在运行提示词之前加载一个或多个技能。

### 单个技能 {#single-skill}

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="Check the configured feeds and summarize anything new.",
    schedule="0 9 * * *",
    name="Morning feeds",
)
```

### 多个技能 {#multiple-skills}

技能按顺序加载。提示词成为叠加在这些技能之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="Look for new local events and interesting nearby places, then combine them into one short brief.",
    schedule="every 6h",
    name="Local brief",
)
```

当你希望一个定时 Agent 继承可复用的工作流，而又不想把完整的技能文本塞进 cron 提示词中时，这非常有用。

## 在项目目录内运行任务 {#running-a-job-inside-a-project-directory}

Cron 任务默认在脱离任何仓库的状态下运行——不会加载 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules`，终端/文件/代码执行工具从网关启动时的工作目录开始运行。通过 `--workdir`（CLI）或 `workdir=`（工具调用）可以改变这一点：

```bash
# 独立 CLI（schedule 和 prompt 是位置参数）
hermes cron create "every 1d at 09:00" \
  "Audit open PRs, summarize CI health, and post to #eng" \
  --workdir /home/me/projects/acme
```

```python
# 从聊天中，通过 cronjob 工具
cronjob(
    action="create",
    schedule="every 1d at 09:00",
    workdir="/home/me/projects/acme",
    prompt="Audit open PRs, summarize CI health, and post to #eng",
)
```
当设置了 `workdir` 时：

- 该目录下的 `AGENTS.md`、`CLAUDE.md` 和 `.cursorrules` 会被注入到系统提示中（发现顺序与交互式 CLI 相同）
- `terminal`、`read_file`、`write_file`、`patch`、`search_files` 和 `execute_code` 都会将该目录作为工作目录（通过 `TERMINAL_CWD`）
- 路径必须是存在的绝对目录——相对路径和不存在的目录会在创建/更新时被拒绝
- 在编辑时传入 `--workdir ""`（或通过工具传入 `workdir=""`）可清除该设置并恢复旧行为

:::note 序列化
设置了 `workdir` 的任务会在调度器 tick 上顺序执行，而不是在并行池中运行。这是有意为之——`TERMINAL_CWD` 是进程全局的，因此两个 workdir 任务同时运行会互相破坏对方的 cwd。没有 workdir 的任务仍然像以前一样并行运行。
:::

## 编辑任务 {#editing-jobs}
<a id="serialization"></a>

你不需要为了修改任务而删除并重新创建。

### 聊天 {#chat}

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "Use the revised task"
/cron edit <job_id> --skill blogwatcher --skill maps
/cron edit <job_id> --remove-skill blogwatcher
/cron edit <job_id> --clear-skills
```

### 独立 CLI {#standalone-cli}

```bash
hermes cron edit <job_id> --schedule "every 4h"
hermes cron edit <job_id> --prompt "Use the revised task"
hermes cron edit <job_id> --skill blogwatcher --skill maps
hermes cron edit <job_id> --add-skill maps
hermes cron edit <job_id> --remove-skill blogwatcher
hermes cron edit <job_id> --clear-skills
```

注意：

- 重复的 `--skill` 会替换任务附带的技能列表
- `--add-skill` 会追加到现有列表，而不是替换
- `--remove-skill` 会移除特定的附带技能
- `--clear-skills` 会移除所有附带技能

## 生命周期操作 {#lifecycle-actions}

Cron 任务现在拥有比仅创建/删除更完整的生命周期。

<a id="chat"></a>
### 聊天

```bash
/cron list
/cron pause <job_id>
/cron resume <job_id>
/cron run <job_id>
/cron remove <job_id>
```

<a id="standalone-cli"></a>
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
- `run` — 在下一个调度器 tick 时触发任务
- `remove` — 完全删除任务

## 工作原理 {#how-it-works}

**Cron 执行由网关守护进程处理。** 网关每 60 秒触发一次调度器，在隔离的 Agent 会话中运行所有到期的任务。

```bash
hermes gateway install     # 安装为用户服务
sudo hermes gateway install --system   # Linux：服务器开机自启系统服务
hermes gateway             # 或在前台运行

hermes cron list
hermes cron status
```

### 网关调度器行为 {#gateway-scheduler-behavior}

每次 tick 时，Hermes 会：

1. 从 `~/.hermes/cron/jobs.json` 加载任务
2. 将 `next_run_at` 与当前时间进行比较
3. 为每个到期的任务启动一个新的 `AIAgent` 会话
4. 可选地将一个或多个附带的技能注入到该新会话中
5. 运行提示直到完成
6. 交付最终响应
7. 更新运行元数据和下一次调度时间
`~/.hermes/cron/.tick.lock` 文件锁可防止调度器滴答重叠导致同一任务批次被重复执行。

## 投递选项 {#delivery-options}

调度任务时，你需要指定输出投递到哪里：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 回到任务创建处 | 消息平台默认 |
| `"local"` | 仅保存到本地文件（`~/.hermes/cron/output/`） | CLI 默认 |
| `"telegram"` | Telegram 主页频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 按 ID 指定 Telegram 聊天 | 直接投递 |
| `"telegram:-100123:17585"` | 指定 Telegram 话题 | `chat_id:thread_id` 格式 |
| `"discord"` | Discord 主页频道 | 使用 `DISCORD_HOME_CHANNEL` |
| `"discord:#engineering"` | 指定 Discord 频道 | 按频道名称 |
| `"slack"` | Slack 主页频道 | |
| `"whatsapp"` | WhatsApp 主页 | |
| `"signal"` | Signal | |
| `"matrix"` | Matrix 主页房间 | |
| `"mattermost"` | Mattermost 主页频道 | |
| `"email"` | 电子邮件 | |
| `"sms"` | 通过 Twilio 发送短信 | |
| `"homeassistant"` | Home Assistant | |
| `"dingtalk"` | 钉钉 | |
| `"feishu"` | 飞书/Lark | |
| `"wecom"` | 企业微信 | |
| `"weixin"` | 微信 | |
| `"bluebubbles"` | BlueBubbles（iMessage） | |
| `"qqbot"` | QQ 机器人（腾讯 QQ） | |

Agent 的最终响应会自动投递。你无需在 cron 提示词中调用 `send_message`。

### 响应包装 {#response-wrapping}

默认情况下，投递的 cron 输出会带有页眉和页脚，以便接收者知道它来自定时任务：

```
Cronjob Response: Morning feeds
-------------

<agent output here>

Note: The agent cannot see this message, and therefore cannot respond to it.
```

若要投递原始 Agent 输出而不带包装，请将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### 静默抑制 {#silent-suppression}

如果 Agent 的最终响应以 `[SILENT]` 开头，则完全抑制投递。输出仍会本地保存以供审计（位于 `~/.hermes/cron/output/`），但不会向投递目标发送任何消息。

这对于仅应在出现问题时才报告的监控任务非常有用：

```text
Check if nginx is running. If everything is healthy, respond with only [SILENT].
Otherwise, report the issue.
```

失败的任务无论是否带有 `[SILENT]` 标记都会投递——只有成功运行的任务可以被静默。

## 脚本超时 {#script-timeout}

预运行脚本（通过 `script` 参数附加）的默认超时时间为 120 秒。如果你的脚本需要更长时间——例如，为了包含随机延迟以避免类似机器人的定时模式——你可以增加此值：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 分钟
```

或者设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。解析顺序为：环境变量 → config.yaml → 默认 120 秒。

## 提供商恢复 {#provider-recovery}

Cron 任务会继承你配置的回退提供商和凭据池轮换。如果主 API 密钥被限流或提供商返回错误，cron Agent 可以：
- **回退到备用提供商**：如果你在 `config.yaml` 中配置了 `fallback_providers`（或旧版 `fallback_model`）
- **轮换到下一个凭证**：针对同一提供商，在你的[凭证池](/user-guide/configuration#credential-pool-strategies)中轮换到下一个凭证

这意味着高频运行或高峰时段运行的 cron 任务更具弹性——单个被限速的密钥不会导致整个运行失败。

## 调度格式 {#schedule-formats}

Agent 的最终响应会自动投递——你**不需要**在 cron 提示词中为同一目标包含 `send_message`。如果 cron 运行调用 `send_message` 到调度器已经会投递的精确目标，Hermes 会跳过重复发送，并告诉模型将面向用户的内容放在最终响应中。仅当需要额外或不同目标时才使用 `send_message`。

### 相对延迟（一次性） {#relative-delays-one-shot}

```text
30m     → 30 分钟后运行一次
2h      → 2 小时后运行一次
1d      → 1 天后运行一次
```

### 间隔（重复） {#intervals-recurring}

```text
every 30m    → 每 30 分钟
every 2h     → 每 2 小时
every 1d     → 每天
```

### Cron 表达式 {#cron-expressions}

```text
0 9 * * *       → 每天上午 9:00
0 9 * * 1-5     → 工作日每天上午 9:00
0 */6 * * *     → 每 6 小时
30 8 1 * *      → 每月第一天上午 8:30
0 0 * * 0       → 每周日午夜
```

### ISO 时间戳 {#iso-timestamps}

```text
2026-03-15T09:00:00    → 一次性：2026 年 3 月 15 日上午 9:00
```

## 重复行为 {#repeat-behavior}

| 调度类型 | 默认重复次数 | 行为 |
|---------|-------------|------|
| 一次性（`30m`、时间戳） | 1 | 运行一次 |
| 间隔（`every 2h`） | 永久 | 运行直到被移除 |
| Cron 表达式 | 永久 | 运行直到被移除 |

你可以覆盖它：

```python
cronjob(
    action="create",
    prompt="...",
    schedule="every 2h",
    repeat=5,
)
```

## 以编程方式管理任务 {#managing-jobs-programmatically}

面向 Agent 的 API 是一个工具：

```python
cronjob(action="create", ...)
cronjob(action="list", ...)
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```

对于 `update`，传递 `skills=[]` 以移除所有附加的技能。

## Cron 任务可用的工具集 {#toolsets-available-to-cron-jobs}

Cron 在每个任务运行时都会启动一个全新的 Agent 会话，不附加任何聊天平台。默认情况下，cron Agent 会获得**你在 `hermes tools` 中为 `cron` 平台配置的工具集**——而不是 CLI 默认值，也不是所有可用的工具。

```bash
hermes tools
# → 在 curses UI 中选择 "cron" 平台
# → 像为 Telegram/Discord 等平台一样切换工具集的开关
```

通过 `cronjob.create` 上的 `enabled_toolsets` 字段（或通过 `cronjob.update` 对现有任务进行设置），可以实现更精细的按任务控制：

```text
cronjob(action="create", name="weekly-news-summary",
        schedule="every sunday 9am",
        enabled_toolsets=["web", "file"],      # just web + file, no terminal/browser/etc.
        prompt="Summarize this week's AI news: ...")
```
当任务设置了 `enabled_toolsets` 时，以此为准；否则使用 `hermes tools` cron 平台配置；再否则 Hermes 会回退到内置默认值。这对成本控制很重要：将 `moa`、`browser`、`delegation` 带入每个微小的“获取新闻”任务，会导致每次 LLM 调用的工具 schema prompt 过于臃肿。

### 完全跳过 Agent：`wakeAgent` {#skipping-the-agent-entirely-wakeagent}

如果你的 cron 任务附加了预检查脚本（通过 `script=`），该脚本可以在运行时决定 Hermes 是否应该调用 agent。输出一行标准输出，格式如下：

```text
{"wakeAgent": false}
```

……cron 会完全跳过此 tick 的 agent 运行。对于频繁的轮询（每 1-5 分钟）很有用，这些轮询只在状态实际发生变化时才需要唤醒 LLM——否则你会为一次次空内容的 agent 轮次付费。

```python
# pre-check script
import json, sys
latest = fetch_latest_issue_count()
prev = read_state("issue_count")
if latest == prev:
    print(json.dumps({"wakeAgent": False}))   # skip this tick
    sys.exit(0)
write_state("issue_count", latest)
print(json.dumps({"wakeAgent": True, "context": {"new_issues": latest - prev}}))
```

当省略 `wakeAgent` 时，默认值为 `true`（正常唤醒 agent）。

### 任务链：`context_from` {#chaining-jobs-contextfrom}

cron 任务可以通过在 `context_from` 中列出其他任务的名字（或 ID）来消费它们最近一次成功运行的输出：

```text
cronjob(action="create", name="daily-digest",
        schedule="every day 7am",
        context_from=["ai-news-fetch", "github-prs-fetch"],
        prompt="Write the daily digest using the outputs above.")
```

被引用任务的最新完成输出会被注入到 prompt 上方，作为本次运行的上下文。每个上游条目必须是一个有效的任务 ID 或名称（参见 `cronjob action="list"`）。注意：任务链读取的是*最近一次已完成*的输出——它不会等待在同一 tick 中正在运行的上游任务。

## 任务存储 {#job-storage}

任务存储在 `~/.hermes/cron/jobs.json` 中。任务运行的输出保存在 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

任务可能将 `model` 和 `provider` 存储为 `null`。当这些字段被省略时，Hermes 在执行时从全局配置中解析它们。它们仅在设置了每个任务的覆盖时才会出现在任务记录中。

存储使用原子文件写入，因此中断的写入不会留下部分写入的任务文件。

## 自包含的 prompt 仍然重要 {#self-contained-prompts-still-matter}

:::warning 重要
<a id="important"></a>
Cron 任务在一个全新的 agent 会话中运行。prompt 必须包含 agent 所需的一切，这些信息不能由附加的技能提供。
:::

**不好的例子：** `"Check on that server issue"`

**好的例子：** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`

## 安全性 {#security}

在创建和更新时，会扫描计划任务 prompt 以检测提示注入和凭证泄露模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显秘密泄露载荷的 prompt 会被阻止。
