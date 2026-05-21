---
sidebar_position: 5
title: "定时任务 (Cron)"
description: "用自然语言安排自动化任务，通过一个 cron 工具进行管理，并可附加一个或多个技能"
---

<a id="scheduled-tasks-cron"></a>
# 定时任务 (Cron)

使用自然语言或 cron 表达式安排自动运行的任务。Hermes 通过单个 `cronjob` 工具（采用 action 风格的操作，而非分散的 schedule/list/remove 工具）来暴露 cron 管理功能。

<a id="what-cron-can-do-now"></a>
## 当前 cron 能做什么

Cron 任务可以：

- 安排一次性或重复性任务
- 暂停、恢复、编辑、触发和删除任务
- 为任务附加零个、一个或多个技能
- 将结果送回原始聊天、本地文件，或配置的平台目标
- 使用常规静态工具列表在新的 Agent 会话中运行
- 在 **无 Agent 模式** 下运行——按计划执行的脚本，直接输出 stdout，完全不涉及 LLM（参见下文[无 Agent 模式](#no-agent-mode-script-only-jobs)章节）

所有这些都可以通过 `cronjob` 工具供 Hermes 自身使用，因此你可以用通俗语言来创建、暂停、编辑和删除任务——无需 CLI。

:::warning
Cron 运行的会话不能递归创建更多 cron 任务。Hermes 会在 cron 执行内部禁用 cron 管理工具，以防止失控的调度循环。
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
### 在独立 CLI 中

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

直接向 Hermes 提问：

```text
每天早上9点，检查 Hacker News 上的 AI 新闻，并通过 Telegram 给我发送摘要。
```

Hermes 会在内部使用统一的 `cronjob` 工具。

<a id="skill-backed-cron-jobs"></a>
## 带技能的 cron 任务

cron 任务可以在运行提示词之前加载一个或多个技能。

<a id="single-skill"></a>
### 单个技能

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="检查配置的订阅源，并总结任何新内容。",
    schedule="0 9 * * *",
    name="早晨订阅",
)
```

<a id="multiple-skills"></a>
### 多个技能

技能按顺序加载。提示词成为叠加在这些技能之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="查找新的本地活动和有趣的附近地点，然后将它们整合成一份简短简报。",
    schedule="every 6h",
    name="本地简报",
)
```

当你希望一个定时 Agent 继承可复用的工作流，而无需将完整技能文本塞进 cron 提示词时，这非常有用。

<a id="running-a-job-inside-a-project-directory"></a>
## 在项目目录内运行任务

默认情况下，cron 任务与任何仓库分离运行——不会加载 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules`，终端/文件/代码执行工具从网关启动时的工作目录运行。通过 `--workdir`（CLI）或 `workdir=`（工具调用）参数可以更改此行为：
```bash
# 独立 CLI（schedule 和 prompt 为位置参数）
hermes cron create "every 1d at 09:00" \
  "审查开放的 PR，总结 CI 健康状态，并发布到 #eng" \
  --workdir /home/me/projects/acme
```

```python
# 通过聊天中的 cronjob 工具调用
cronjob(
    action="create",
    schedule="every 1d at 09:00",
    workdir="/home/me/projects/acme",
    prompt="审查开放的 PR，总结 CI 健康状态，并发布到 #eng",
)
```

当设置 `workdir` 时：

- 该目录下的 `AGENTS.md`、`CLAUDE.md` 和 `.cursorrules` 会被注入到系统提示词中（发现顺序与交互式 CLI 相同）
- `terminal`、`read_file`、`write_file`、`patch`、`search_files` 和 `execute_code` 都会将该目录作为工作目录（通过 `TERMINAL_CWD`）
- 路径必须是存在的绝对目录——相对路径和不存在的目录在创建/更新时会拒绝
- 在编辑时传入 `--workdir ""`（或通过工具传入 `workdir=""`）可清除此设置，恢复旧行为

:::note 序列化
带有 `workdir` 的任务在调度器时钟节拍上顺序执行，而非在并行池中运行。这是有意为之——`TERMINAL_CWD` 是进程全局的，所以两个设置了工作目录的任务若同时运行会互相破坏对方的 cwd。没有工作目录的任务仍像以前一样并行运行。
<a id="serialization"></a>
:::

<a id="running-cron-jobs-in-a-specific-profile"></a>
## 在特定配置文件中运行 cron 任务

默认情况下，cron 任务会继承创建它的网关/CLI 所属的 Hermes 配置文件。通过 `--profile &lt;name&gt;`（CLI）或 `profile=`（cronjob 工具）可以将任务重定向到另一个配置文件——调度器会解析该配置文件的 `HERMES_HOME`，在运行期间临时切换进去，加载其 `.env` + `config.yaml`，并在其中执行任务：

```bash
# 将任务固定到 `night-ops` 配置文件，无论它在哪里被调度
hermes cron create "every 1d at 03:00" \
  "追踪安全日志并标记异常" \
  --profile night-ops
```

```python
# 通过聊天中的 cronjob 工具调用
cronjob(
    action="create",
    schedule="every 1d at 03:00",
    prompt="追踪安全日志并标记异常",
    profile="night-ops",
)
```

使用 `--profile default` 可以明确固定到根 Hermes 配置文件。指定的配置文件必须已存在；调度器拒绝动态创建配置文件。要在 `cron edit` 期间清除配置文件固定，传入空字符串（`--profile ""` 或 `profile=""`）——任务会恢复为在调度器自身所在的配置文件中运行。

如果之后删除了固定引用的配置文件，调度器会记录一条警告并回退到在当前配置文件中运行该任务，而不是崩溃——因此过期的 `profile` 引用永远不会卡死一个任务。

:::note 序列化
设置了 `profile` 的任务也会顺序执行，原因与固定了 `workdir` 的任务相同：切换 `HERMES_HOME` 是进程全局的变更，因此两个固定配置文件的任务并行运行时会相互竞争。未固定的任务仍然在正常的并行池中运行。
:::

<a id="editing-jobs"></a>
## 编辑任务

你不需要为了修改任务而删除并重新创建它。
:::tip 任务引用
下面的 `&lt;job_id&gt;` 占位符（以及[生命周期操作](#lifecycle-actions)中的）也接受任务的名称（不区分大小写）——当你记得 `morning-digest` 但记不住十六进制 ID 时非常方便。精确的任务 ID 优先于名称匹配；如果引用不是 ID 且名称匹配了多个任务，命令会拒绝执行并打印候选 ID 列表，方便你区分。
:::

<a id="chat"></a>
### 聊天界面
<a id="job-reference"></a>

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "Use the revised task"
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

说明：

- 重复的 `--skill` 会替换任务附带的技能列表
- `--add-skill` 会在现有列表后追加，不会替换
- `--remove-skill` 会移除指定的技能
- `--clear-skills` 会移除所有技能

<a id="lifecycle-actions"></a>
## 生命周期操作

Cron 任务现在拥有比仅创建/删除更完整的生命周期。

### 聊天界面

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

各命令的作用：

- `pause` — 保留任务，但停止调度它
- `resume` — 重新启用任务，并计算下一次运行时间
- `run` — 在调度器下一次 tick 时立即触发任务
- `remove` — 彻底删除任务

<a id="how-it-works"></a>
## 工作原理

**Cron 的执行由 gateway 守护进程处理。** Gateway 每 60 秒触发一次调度器，在独立的 Agent 会话中运行所有到期的任务。

```bash
hermes gateway install     # 安装为用户服务
sudo hermes gateway install --system   # Linux：作为开机系统服务（服务器环境）
hermes gateway             # 或者在前台运行

hermes cron list
hermes cron status
```

<a id="gateway-scheduler-behavior"></a>
### Gateway 调度器行为

每次 tick 时，Hermes 会：

1. 从 `~/.hermes/cron/jobs.json` 加载任务
2. 将 `next_run_at` 与当前时间进行比对
3. 为每个到期的任务启动一个新的 `AIAgent` 会话
4. 可选地将一个或多个技能注入到该新会话中
5. 运行提示词直到完成
6. 交付最终响应
7. 更新运行元数据和下一次调度时间

位于 `~/.hermes/cron/.tick.lock` 的文件锁可以防止重叠的调度器 tick 重复运行同一批任务。

<a id="delivery-options"></a>
## 交付选项

在调度任务时，可以指定输出发往何处：

| 选项 | 描述 | 示例 |
|--------|-------------|---------|
| `"origin"` | 返回到任务创建的地方 | 消息平台默认值 |
| `"local"` | 仅保存到本地文件（`~/.hermes/cron/output/`） | CLI 默认值 |
| `"telegram"` | Telegram 主频道 | 使用 `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | 通过 ID 指定 Telegram 聊天 | 直接交付 |
| `"telegram:-100123:17585"` | 指定 Telegram 话题 | `chat_id:thread_id` 格式 |
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
| `"qqbot"` | QQ 机器人 (腾讯QQ) | |
| `"all"` | 分发到所有已连接的主频道 | 在触发时解析 |
| `"telegram,discord"` | 分发到指定的一组频道 | 逗号分隔列表 |
| `"origin,all"` | 分发到原始位置**以及**所有其他已连接的频道 | 可组合任何令牌 |
Agent 的最终响应会自动投递。你不需要在 cron 提示词中调用 `send_message`。

<a id="routing-intent-all"></a>
### 路由意图（`all`）

`all` 允许你将一个 cron 任务发送到你配置的每个消息通道，而无需逐一列举它们的名称。它**在触发时解析**，因此在你连接 Telegram 之前创建的任务，会在你设置 `TELEGRAM_HOME_CHANNEL` 后的下一次触发时自动接入 Telegram。

语义：`all` 会扩展到每个配置了主通道的平台。零个平台也没问题；该任务只会产生零个投递目标，并在上游记录为投递失败。

`all` 可以与显式目标组合使用。`origin,all` 会投递到原始聊天 *以及* 每个其他已连接的主通道，并按 `(platform, chat_id, thread_id)` 去重。

<a id="telegram-cron-topic-telegramcronthreadid"></a>
### Telegram cron 话题（`TELEGRAM_CRON_THREAD_ID`）

当启用 Telegram 话题模式时，根 DM 被保留为系统大厅——发送到那里的回复会被大厅提醒拒绝，并且 `reply_to_message_id` 会被丢弃，因此你无法回复落在主聊天中的 cron 消息。

请将 cron 指向一个专门的论坛话题：

1. 在 Telegram 中，打开机器人 DM 并创建一个名为 `Cron` 的话题。长按话题标题 → **复制链接**；末尾的整数就是该话题的 `message_thread_id`。
2. 在你的 `.env` 中设置 `TELEGRAM_CRON_THREAD_ID=<那个 id>`。

这仅适用于 cron 投递。`TELEGRAM_HOME_CHANNEL_THREAD_ID`（用于其他地方，例如重启通知）保持不变。显式的 `deliver="telegram:chat_id:thread_id"` 目标会继续覆盖环境变量。对 cron 消息的回复现在会到达现有的话题会话中，因此你可以直接对它们进行操作。

<a id="response-wrapping"></a>
### 响应包装

默认情况下，投递的 cron 输出会带有页眉和页脚，以便接收者知道它来自一个计划任务：

```
Cronjob 响应：Morning feeds
-------------

<agent 输出在此>

注意：Agent 无法看到此消息，因此无法回复它。

```

要投递不带包装的原始 Agent 输出，请将 `cron.wrap_response` 设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

<a id="silent-suppression"></a>
### 静默抑制

如果 Agent 的最终响应以 `[SILENT]` 开头，则完全抑制投递。输出仍会本地保存以供审计（在 `~/.hermes/cron/output/` 中），但不会向投递目标发送任何消息。

这对于只应在出现问题时报告的监控任务非常有用：

```text
检查 nginx 是否正在运行。如果一切正常，仅回复 [SILENT]。
否则，报告问题。
```

失败的任务始终会投递，无论 `[SILENT]` 标记如何——只有成功的运行可以被静默。

<a id="script-timeout"></a>
## 脚本超时

预运行脚本（通过 `script` 参数附加）的默认超时时间为 120 秒。如果你的脚本需要更长时间——例如，包含随机延迟以避免类似机器人的定时模式——你可以增加此值：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 分钟
```
或者设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。解析顺序为：环境变量 → config.yaml → 默认值 120 秒。

<a id="no-agent-mode-script-only-jobs"></a>
## 无 Agent 模式（纯脚本作业）

对于不需要 LLM 推理的定期作业——经典看门狗、磁盘/内存告警、心跳检测、CI 通知——在创建时传入 `no_agent=True`。调度器会按计划运行你的脚本，并将其 stdout 直接传递出去，完全跳过 Agent：

```bash
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"
```

语义说明：

- 脚本 stdout（经修剪）→ 直接作为消息原样传递。
- **空 stdout → 静默滴答**，不发送消息。这是看门狗模式：“只在有异常时发声”。
- 非零退出或超时 → 发送错误告警，因此损坏的看门狗不会无声失效。
- 最后一行输出 `{"wakeAgent": false}` → 静默滴答（与 LLM 作业使用的控制机制相同）。
- 不消耗 token，不涉及模型，无 provider 回退——该作业从不触碰推理层。

`.sh` / `.bash` 文件在 `/bin/bash` 下运行；其他文件在当前 Python 解释器（`sys.executable`）下运行。脚本必须存放在 `~/.hermes/scripts/` 中（与预运行脚本门控相同的沙盒规则）。

<a id="the-agent-sets-these-up-for-you"></a>
### Agent 会帮你设置这些

`cronjob` 工具的 schema 直接将 `no_agent` 暴露给 Hermes，因此你可以在聊天中描述一个看门狗，然后让 Agent 将其配置好：

```
Ping me on Telegram if RAM is over 85%, every 5 minutes.
```

Hermes 会通过 `write_file` 将检查脚本写入 `~/.hermes/scripts/`，然后调用：

```python
cronjob(action="create", schedule="every 5m",
        script="memory-watchdog.sh", no_agent=True,
        deliver="telegram", name="memory-watchdog")
```

当消息内容完全由脚本决定时（看门狗、阈值告警、心跳检测），Hermes 会自动选择 `no_agent=True`。同样的工具也让 Agent 能够暂停、恢复、编辑和删除作业——因此整个生命周期都由聊天驱动，无需任何人接触 CLI。

参见 [纯脚本定时任务指南](/guides/cron-script-only) 查看具体示例。

<a id="chaining-jobs-with-contextfrom"></a>
## 使用 `context_from` 链式作业

Cron 作业在隔离的会话中运行，不会记忆之前的运行结果。但有时一个作业的输出恰好是下一个作业所需的内容。`context_from` 参数会自动建立这种连接——作业 B 的提示会在运行时被附加作业 A 的最新输出作为上下文。

```python
# Job 1: Collect raw data
cronjob(
    action="create",
    prompt="Fetch the top 10 AI/ML stories from Hacker News. Save them to ~/.hermes/data/briefs/raw.md in markdown format with title, URL, and score.",
    schedule="0 7 * * *",
    name="AI News Collector",
)

# Job 2: Triage — receives Job 1's output as context
# Get Job 1's ID from: cronjob(action="list")
cronjob(
    action="create",
    prompt="Read ~/.hermes/data/briefs/raw.md. Score each story 1–10 for engagement potential and novelty. Output the top 5 to ~/.hermes/data/briefs/ranked.md.",
    schedule="30 7 * * *",
    context_from="<job1_id>",
    name="AI News Triage",
)

# Job 3: Ship — receives Job 2's output as context
cronjob(
    action="create",
    prompt="Read ~/.hermes/data/briefs/ranked.md. Write 3 tweet drafts (hook + body + hashtags). Deliver to telegram:7976161601.",
    schedule="0 8 * * *",
    context_from="<job2_id>",
    name="AI News Brief",
)
```
**工作原理：**

- 当 Job 2 触发时，Hermes 从 `~/.hermes/cron/output/{job1_id}/*.md` 读取 Job 1 的最新输出
- 该输出会自动附加到 Job 2 的提示词前面
- Job 2 无需硬编码“读取这个文件”——它直接把内容作为上下文接收
- 链可以是任意长度：Job 1 → Job 2 → Job 3 → ...

**`context_from` 接受的格式：**

| 格式 | 示例 |
|--------|---------|
| 单个 Job ID（字符串） | `context_from="a1b2c3d4"` |
| 多个 Job ID（列表） | `context_from=["job_a", "job_b"]` |

输出按列出的顺序拼接。

**何时使用：**

- 多阶段流水线（采集 → 过滤 → 格式化 → 投递）
- 依赖任务，其中步骤 N 的工作依赖于步骤 N−1 的输出
- 扇出/扇入模式：一个 Job 聚合多个其他 Job 的结果

<a id="provider-recovery"></a>
## Provider 恢复

Cron 作业会继承你配置的回退 provider 和凭据池轮换。如果主 API 密钥被限流或 provider 返回错误，cron Agent 可以：

- **回退到备用 provider**（如果你在 `config.yaml` 中配置了 `fallback_providers` 或旧的 `fallback_model`）
- **轮换到同 provider 的下一个凭据**（在你的[凭据池](/user-guide/configuration#credential-pool-strategies)中）

这意味着高频运行或高峰时段运行的 cron 作业更具弹性——单个被限流的密钥不会导致整个运行失败。

<a id="schedule-formats"></a>
## 调度格式

Agent 的最终响应会自动投递——你**不需要**在 cron 提示词中包含 `send_message` 来发送到同一目标。如果 cron 运行调用了 `send_message` 到调度器将要投递的精确目标，Hermes 会跳过这个重复发送，并告诉模型将面向用户的内容放在最终响应中。仅当需要发送到额外或不同目标时才使用 `send_message`。

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
every 30m    → 每 30 分钟运行一次
every 2h     → 每 2 小时运行一次
every 1d     → 每天运行一次
```

<a id="cron-expressions"></a>
### Cron 表达式

```text
0 9 * * *       → 每天早上 9:00
0 9 * * 1-5     → 工作日早上 9:00
0 */6 * * *     → 每 6 小时
30 8 1 * *      → 每月 1 日上午 8:30
0 0 * * 0       → 每周日午夜
```

<a id="iso-timestamps"></a>
### ISO 时间戳

```text
2026-03-15T09:00:00    → 在 2026 年 3 月 15 日上午 9:00 执行一次
```

<a id="repeat-behavior"></a>
## 重复行为

| 调度类型 | 默认重复次数 | 行为 |
|--------------|----------------|----------|
| 一次性（`30m`、时间戳） | 1 | 运行一次 |
| 间隔（`every 2h`） | 无限 | 一直运行直到被移除 |
| Cron 表达式 | 无限 | 一直运行直到被移除 |

你可以覆盖它：

```python
cronjob(
    action="create",
    prompt="...",
    schedule="every 2h",
    repeat=5,
)
```

<a id="managing-jobs-programmatically"></a>
## 以编程方式管理作业

Agent 的 API 是一个工具：

```python
cronjob(action="create", ...)
cronjob(action="list")
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```
对于 `update`，传递 `skills=[]` 可移除所有已附加的技能。

<a id="toolsets-available-to-cron-jobs"></a>
## Cron 作业可用的工具集

Cron 在每个新的 agent 会话中运行每个作业，且不附加任何聊天平台。默认情况下，cron agent 会获得**你在 `hermes tools` 中为 `cron` 平台配置的工具集**——而不是 CLI 默认项，也不是所有工具。

```bash
hermes tools
# → 在 curses 界面中选择 "cron" 平台
# → 像为 Telegram/Discord 等平台一样，开关工具集
```

通过 `cronjob.create` 的 `enabled_toolsets` 字段（或通过 `cronjob.update` 更新已有作业），可以实现更精细的按作业控制：

```text
cronjob(action="create", name="weekly-news-summary",
        schedule="every sunday 9am",
        enabled_toolsets=["web", "file"],      # 仅 web + file，不含 terminal/browser 等
        prompt="Summarize this week's AI news: ...")
```

当某个作业设置了 `enabled_toolsets` 时，以该作业为准；否则以 `hermes tools` 中 cron 平台的配置为准；再否则 Hermes 会回退到内置默认值。这一点对成本控制很重要：如果每个微小的 "fetch news" 作业都携带 `moa`、`browser`、`delegation`，会使得每次 LLM 调用的工具模式提示词变得臃肿。

<a id="skipping-the-agent-entirely-wakeagent"></a>
### 完全绕过 agent：`wakeAgent`

如果你的 cron 作业附加了预检查脚本（通过 `script=`），该脚本可以在运行时决定 Hermes 是否应该调用 agent。在标准输出的最后一行输出如下格式的内容：

```text
{"wakeAgent": false}
```

……这样 cron 就会在该次触发时完全跳过 agent 运行。适用于频繁的轮询（每 1-5 分钟一次），这种场景下仅当状态实际发生变化时才需要唤醒 LLM——否则你会白白为不含任何内容的 agent 轮次付费。

```python
# pre-check script
import json, sys
latest = fetch_latest_issue_count()
prev = read_state("issue_count")
if latest == prev:
    print(json.dumps({"wakeAgent": False}))   # 跳过此次触发
    sys.exit(0)
write_state("issue_count", latest)
print(json.dumps({"wakeAgent": True, "context": {"new_issues": latest - prev}}))
```

当省略 `wakeAgent` 时，默认值为 `true`（照常唤醒 agent）。

<a id="recipes-cheap-pre-run-gates"></a>
#### 技巧：低成本预执行门控

`wakeAgent` 门控为你提供了一种零成本的方式，来决定一个计划中的作业是否应该花费任何 LLM token。以下三种模式覆盖了大多数用例。

**文件变更门控**——仅当被监视的文件自上次成功触发后有了新内容时才运行。调度器会记录每个作业的 `last_run_at`，将其与文件的 mtime 进行比较。

```bash
#!/bin/bash
# ~/.hermes/scripts/feed-changed.sh
FEED="$HOME/data/feed.json"
STATE="$HOME/.hermes/scripts/.feed-changed.last"
test -f "$FEED" || { echo '{"wakeAgent": false}'; exit 0; }
mtime=$(stat -c %Y "$FEED")
last=$(cat "$STATE" 2>/dev/null || echo 0)
if [ "$mtime" -le "$last" ]; then
  echo '{"wakeAgent": false}'
else
  echo "$mtime" > "$STATE"
  echo '{"wakeAgent": true}'
fi
```

```text
cronjob(action="create", name="process-feed",
        schedule="every 30m",
        script="feed-changed.sh",
        prompt="A new ~/data/feed.json has landed. Summarize what changed.")
```
**外部标志门控** — 仅当其他进程发出就绪信号时才运行（例如部署钩子放下一个文件、CI 作业在你的状态存储中设置一个值）。

```bash
#!/bin/bash
# ~/.hermes/scripts/flag-ready.sh
if test -f /tmp/new-data-ready; then
  rm -f /tmp/new-data-ready
  echo '{"wakeAgent": true}'
else
  echo '{"wakeAgent": false}'
fi
```

```text
cronjob(action="create", name="nightly-analysis",
        schedule="0 9 * * *",
        script="flag-ready.sh",
        prompt="对今天的数据批次执行夜间分析。")
```

**SQL 计数门控** — 仅当数据库中有新行需要处理时才运行。脚本还可以通过 `context` 将计数传递给 Agent，这样 Agent 无需重新查询就能知道要处理多少数据。

```python
#!/usr/bin/env python
# ~/.hermes/scripts/new-rows.py
import json, sqlite3
conn = sqlite3.connect("/home/me/data/app.db")
n = conn.execute(
    "SELECT COUNT(*) FROM messages WHERE ts > strftime('%s','now','-2 hours')"
).fetchone()[0]
if n < 1:
    print(json.dumps({"wakeAgent": False}))
else:
    print(json.dumps({"wakeAgent": True, "context": {"new_rows": n}}))
```

```text
cronjob(action="create", name="summarize-new-msgs",
        schedule="every 2h",
        script="new-rows.py",
        prompt="总结过去 2 小时内的新消息。")
```

同样的模式适用于任何你能通过脚本查询的数据源——Postgres、HTTP API、你自己的状态存储——无需在 cron 子系统中内置 SQL 求值器。

:::tip
Hermes 自己的 `~/.hermes/state.db` 是一个内部模式，会在不同版本之间发生变化。不要从预运行门控中查询它——请指向你自己的数据库或数据源。
:::

致谢：这套方案由 @iankar8 在 [#2654](https://github.com/NousResearch/hermes-agent/pull/2654) 中的探索启发，该 PR 提议添加 sql/文件/命令触发器作为并行机制。`script` + `wakeAgent` 门控已经以零成本覆盖了所有三种情况，因此相关工作最终以文档形式落地。

<a id="chaining-jobs-contextfrom"></a>
### 链式作业：`context_from`

一个 cron 作业可以通过在 `context_from` 中列出其他作业的名称（或 ID）来消费它们最近一次成功的输出：

```text
cronjob(action="create", name="daily-digest",
        schedule="every day 7am",
        context_from=["ai-news-fetch", "github-prs-fetch"],
        prompt="使用上述输出编写每日摘要。")
```

被引用作业最近一次完成的输出会被注入到提示词上方，作为本次运行的上下文。每个上游条目必须是一个有效的作业 ID 或名称（参见 `cronjob action="list"`）。注意：链式读取的是*最近一次完成的*输出——它不会等待同一周期内正在运行的上游作业。

<a id="job-storage"></a>
## 作业存储

作业存储在 `~/.hermes/cron/jobs.json` 中。作业运行的输出保存到 `~/.hermes/cron/output/{job_id}/{timestamp}.md`。

作业可以将 `model` 和 `provider` 存储为 `null`。当这些字段被省略时，Hermes 会在执行时从全局配置中解析它们。它们仅当设置了每个作业的覆盖值时才会出现在作业记录中。
存储使用原子文件写入，因此中断的写入不会留下部分写入的作业文件。

<a id="self-contained-prompts-still-matter"></a>
## 自包含的提示仍然重要

:::warning 重要
<a id="important"></a>
Cron 作业在完全全新的 Agent 会话中运行。提示必须包含 Agent 所需的所有内容，这些内容尚未由附加的技能提供。
:::

**BAD:** `"Check on that server issue"`

**GOOD:** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`

<a id="security"></a>
## 安全性

在创建和更新时，会扫描计划任务提示中的提示注入和凭据泄露模式。包含不可见 Unicode 技巧、SSH 后门尝试或明显秘密泄露载荷的提示将被阻止。
