---
sidebar_position: 13
title: "纯脚本 Cron 任务（无 LLM）"
description: "经典看门狗 cron 任务，完全跳过 LLM——脚本按计划运行，其 stdout 直接送达你的消息平台。内存告警、磁盘告警、CI 通知、定期健康检查。"
---

<a id="script-only-cron-jobs"></a>
# 纯脚本 Cron 任务

有时候你已经确切知道要发送什么消息。你不需要 Agent 来思考——你只需要一个脚本按定时运行，它的输出（如果有的话）直接落到 Telegram / Discord / Slack / Signal 中。

Hermes 称之为**无 Agent 模式**。这是去掉了 LLM 的 cron 系统。

<!-- ascii-guard-ignore -->
```
   ┌──────────────────┐          ┌──────────────────┐
   │ 调度器触发       │  每 N 分钟  │ 运行脚本         │
   │ (every N minutes)│ ──────▶ │ (bash or python) │
   └──────────────────┘          └──────────────────┘
                                          │
                                          │ stdout
                                          ▼
                                 ┌──────────────────┐
                                 │ 投递路由器       │
                                 │ (telegram/disc…) │
                                 └──────────────────┘
```
<!-- ascii-guard-ignore-end -->

- **无 LLM 调用。** 零 token、零 agent 循环、零模型开销。
- **脚本即任务。** 脚本决定是否告警。有输出 → 消息被发送。无输出 → 静默触发。
- **Bash 或 Python。** `.sh` / `.bash` 文件在 `/bin/bash` 下运行；其他扩展名在当前 Python 解释器下运行。`~/.hermes/scripts/` 中的任何文件都可接受。
- **相同的调度器。** 与 LLM 任务共同存在于 `cronjob` 中——暂停、恢复、列出、日志和投递目标设置的工作方式完全一样。

<a id="when-to-use-it"></a>
## 何时使用

在以下场景使用无 Agent 模式：

- **内存 / 磁盘 / GPU 看门狗。** 每 5 分钟运行一次，仅在阈值被突破时告警。
- **CI 钩子。** 部署完成 → 推送 commit SHA。构建失败 → 发送最后 100 行日志。
- **定期指标。** “每天上午 9 点获取 Stripe 收入”作为一个简单的 API 调用 + 美化打印。
- **外部事件轮询器。** 检查某个 API，状态变化时告警。
- **心跳。** 每隔 N 分钟向仪表盘发送信号，证明主机仍在运行。

当你需要 Agent **决定**说什么时——比如总结一篇长文档、从 feed 中挑选有趣的内容、撰写人性化的消息——使用正常的（LLM 驱动的）cron 任务。无 Agent 路径适用于脚本的 stdout 本身**就是**消息的情况。

<a id="create-one-from-chat"></a>
## 通过对话创建

无 Agent 模式真正的亮点在于：Agent 自己就能为你设置好看门狗——无需编辑器、无需终端、无需记住 CLI 参数。你描述你想要什么，Hermes 编写脚本、安排执行，并告诉你它将在何时触发。

<a id="example-transcript"></a>
### 示例对话

> **你：** 如果 RAM 超过 85%，每 5 分钟在 telegram 上 ping 我
>
> **Hermes：** *(编写 `~/.hermes/scripts/memory-watchdog.sh`，然后调用 `cronjob(...)` 并设置 `no_agent=true`)*
>
> 已设置。每 5 分钟运行一次，仅在 RAM 超过 85% 时在 Telegram 上告警。脚本：`memory-watchdog.sh`。任务 ID：`abc123`。

在底层，Agent 做了两个工具调用：

```python
# 1. 编写检查脚本
write_file(
    path="~/.hermes/scripts/memory-watchdog.sh",
    content='''#!/usr/bin/env bash
ram_pct=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$ram_pct" -ge 85 ]; then
  echo "RAM ${ram_pct}% on $(hostname)"
fi
# 空的 stdout = 静默触发；不发送消息。
''',
)

# 2. 安排运行——no_agent=True 跳过每次触发时的 LLM
cronjob(
    action="create",
    schedule="every 5m",
    script="memory-watchdog.sh",
    no_agent=True,
    deliver="telegram",
    name="memory-watchdog",
)
```
从那之后，每次触发都是免费的：调度器运行脚本，如果 stdout 非空则将其通过管道发送到 Telegram，并且不调用任何模型。

<a id="what-the-agent-decides-for-you"></a>
### Agent 为你决定什么

当你提出类似“当 X 时提醒我”或“每 N 分钟检查 Y 并在发生 Z 时告诉我”这样的请求时，Hermes 的 `cronjob` 工具描述会告诉它：只要消息内容完全由脚本决定，就使用 `no_agent=True`。当请求需要推理（*“总结新 issue”*、*“选出最有趣的标题”*、*“起草一条友好的提醒”*）时，它会回退到正常的 LLM 驱动路径。

你无需自己指定 `--no-agent`，只需描述行为即可。

<a id="managing-watchdogs-from-chat"></a>
### 在聊天中管理 watchdog

Agent 可以像创建任务一样暂停、恢复、编辑和删除任务：

> **你：** 今晚暂停内存 watchdog
>
> **Hermes：** *(调用 `cronjob(action='pause', job_id='abc123')`)*
>
> 已暂停。通过“把它再打开”或 `hermes cron resume abc123` 恢复。

> **你：** 改成每 15 分钟执行一次
>
> **Hermes：** *(调用 `cronjob(action='update', job_id='abc123', schedule='every 15m')`)*

完整的生命周期（创建 / 列表 / 更新 / 暂停 / 恢复 / 立即执行 / 删除）对 Agent 可用，你无需学习任何 CLI 命令。

<a id="create-one-from-the-cli"></a>
## 从 CLI 创建一个

更喜欢命令行？通过 CLI 路径可以用三条命令达到同样效果：

```bash
# 1. 编写你的脚本
cat > ~/.hermes/scripts/memory-watchdog.sh <<'EOF'
#!/usr/bin/env bash
# 当 RAM 使用率超过 85% 时发出告警，否则保持静默。
RAM_PCT=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$RAM_PCT" -ge 85 ]; then
  echo "⚠ RAM ${RAM_PCT}% on $(hostname)"
fi
# 空的 stdout = 静默运行；不发送消息。
EOF
chmod +x ~/.hermes/scripts/memory-watchdog.sh

# 2. 调度它
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"

# 3. 验证
hermes cron list
hermes cron run <job_id>    # 触发一次以测试
```

就这些。不需要提示词、技能或模型。

<a id="how-script-output-maps-to-delivery"></a>
## 脚本输出到交付的映射关系

| 脚本行为 | 结果 |
|-----------------|--------|
| 退出码 0，stdout 非空 | stdout 原样交付 |
| 退出码 0，stdout 为空 | 静默触发——不交付 |
| 退出码 0，stdout 最后一行包含 `{"wakeAgent": false}` | 静默触发（与 LLM 任务共享的闸门） |
| 退出码非零 | 交付错误告警（这样 watchdoc 坏了也不会静默失败） |
| 脚本超时 | 交付错误告警 |

“为空时静默”的行为是经典 watchdog 模式的关键：脚本可以每分钟运行一次，但通道仅在真正需要关注时才显示消息。

<a id="script-rules"></a>
## 脚本规则

脚本必须存放在 `~/.hermes/scripts/` 目录下。这在创建任务和运行时都会强制检查——绝对路径、`~/` 扩展和路径遍历模式（`../`）都会被拒绝。该目录与 LLM 任务使用的预检查脚本闸门共享。

解释器选择依据文件扩展名：
| 扩展名 | 解释器 |
|--------|--------|
| `.sh`, `.bash` | `/bin/bash` |
| 其他所有 | `sys.executable`（当前 Python） |

我们刻意不尊重 `#!/...` shebang —— 保持解释器显式且小范围可以降低调度器信任的攻击面。

<a id="schedule-syntax"></a>
## 调度语法

与其他所有 cron 任务相同：

```bash
hermes cron create "every 5m"        # 间隔
hermes cron create "every 2h"
hermes cron create "0 9 * * *"       # 标准 cron：每天上午 9 点
hermes cron create "30m"             # 一次性：30 分钟后运行一次
```

完整语法见 [cron 功能参考](/user-guide/features/cron)。

<a id="delivery-targets"></a>
## 投递目标

`--deliver` 接受网关已知的所有内容。一些常见形式：

```bash
--deliver telegram                       # 平台主频道
--deliver telegram:-1001234567890        # 特定聊天
--deliver telegram:-1001234567890:17585  # 特定 Telegram 论坛主题
--deliver discord:#ops
--deliver slack:#engineering
--deliver signal:+15551234567
--deliver local                          # 仅保存到 ~/.hermes/cron/output/
```

对于基于机器人令牌的平台（Telegram、Discord、Slack、Signal、SMS、WhatsApp），在脚本运行时无需运行网关 —— 该工具会直接使用 `~/.hermes/.env` / `~/.hermes/config.yaml` 中已有的凭据调用每个平台的 REST 端点。

<a id="editing-and-lifecycle"></a>
## 编辑与生命周期

```bash
hermes cron list                                    # 查看所有任务
hermes cron pause <job_id>                          # 停止触发，保留定义
hermes cron resume <job_id>
hermes cron edit <job_id> --schedule "every 10m"    # 调整频率
hermes cron edit <job_id> --agent                   # 切换为 LLM 模式
hermes cron edit <job_id> --no-agent --script …     # 切回
hermes cron remove <job_id>                         # 删除
```

所有适用于 LLM 任务的操作（暂停、恢复、手动触发、更改投递目标）同样适用于无 Agent 任务。

<a id="worked-example-disk-space-alert"></a>
## 示例：磁盘空间警报

```bash
cat > ~/.hermes/scripts/disk-alert.sh <<'EOF'
#!/usr/bin/env bash
# 当 / 或 /home 超过 90% 时发出警报
THRESHOLD=90
df -h / /home 2>/dev/null | awk -v t="$THRESHOLD" '
  NR > 1 && $5+0 >= t {
    printf "⚠ 磁盘 %s 在 %s 上已满\n", $5, $6
  }
'
EOF
chmod +x ~/.hermes/scripts/disk-alert.sh

hermes cron create "*/15 * * * *" \
  --no-agent \
  --script disk-alert.sh \
  --deliver telegram \
  --name "disk-alert"
```

当两个文件系统均低于 90% 时静默；当某个文件系统超过阈值时，每超出一个文件系统触发一行输出。

<a id="comparison-with-other-patterns"></a>
## 与其他模式的比较

| 方式 | 运行内容 | 何时使用 |
|------|----------|----------|
| `cronjob --no-agent`（本页） | 你的脚本按 Hermes 的调度执行 | 周期性看门狗/警报/指标，不需要推理时 |
| `cronjob`（默认，LLM） | Agent 带可选预检脚本 | 消息内容需要对数据进行推理时 |
| OS cron + `curl` 到 [webhook 订阅](/user-guide/messaging/webhooks) | 你的脚本按 OS 调度执行 | Hermes 可能不健康时（你正在监控的东西） |
对于必须*即使在网关宕机时*也能触发的关键系统健康看门狗，请使用操作系统级别的 cron，配合简单的 `curl` 调用 Hermes webhook 订阅（或任何外部告警端点）——这些作为独立的操作系统进程运行，不依赖 Hermes 是否在线。当被监控的对象是外部系统时，网关内的调度器才是正确的选择。

<a id="related"></a>
## 相关文档

- [使用 Cron 实现一切自动化](/guides/automate-with-cron) — 基于 LLM 驱动的 cron 模式。
- [计划任务（Cron）参考](/user-guide/features/cron) — 完整的调度语法、生命周期、投递路由。
- [Webhook 订阅](/user-guide/messaging/webhooks) — 供外部调度器使用的即发即忘 HTTP 入口点。
- [网关内部机制](/developer-guide/gateway-internals) — 投递路由器的内部实现。
