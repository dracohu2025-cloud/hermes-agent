---
sidebar_position: 12
title: "Cron 故障排查"
description: "诊断并修复常见的 Hermes Cron 问题——任务未触发、投递失败、技能加载错误以及性能问题"
---

<a id="cron-troubleshooting"></a>
# Cron 故障排查

当 cron 任务的行为不符合预期时，请按顺序进行以下检查。大多数问题可归为四类：时间、投递、权限或技能加载。

---

<a id="jobs-not-firing"></a>
## 任务未触发

<a id="check-1-verify-the-job-exists-and-is-active"></a>
### 检查 1：确认任务存在且处于活跃状态

```bash
hermes cron list
```

查找该任务，并确认其状态为 `[active]`（而非 `[paused]` 或 `[completed]`）。如果显示为 `[completed]`，则可能是重复次数已用尽——编辑任务以重置它。

<a id="check-2-confirm-the-schedule-is-correct"></a>
### 检查 2：确认调度表达式正确

格式错误的调度表达式会静默地默认为一次性任务，或直接被拒绝。测试你的表达式：

| 你的表达式 | 应计算为 |
|----------------|-------------------|
| `0 9 * * *` | 每天上午 9:00 |
| `0 9 * * 1` | 每周一上午 9:00 |
| `every 2h` | 从现在起每 2 小时 |
| `30m` | 从现在起 30 分钟后 |
| `2025-06-01T09:00:00` | 2025 年 6 月 1 日上午 9:00 UTC |

如果任务触发一次后从列表中消失，说明这是一个一次性调度（`30m`、`1d` 或 ISO 时间戳）——这是预期行为。

<a id="check-3-is-the-gateway-running"></a>
### 检查 3：网关是否在运行？

Cron 任务由网关的后台 ticker 线程触发，该线程每 60 秒触发一次。常规的 CLI 聊天会话**不会**自动触发 cron 任务。

如果你希望任务自动触发，你需要一个正在运行的网关（前台使用 `hermes gateway`，或作为已安装服务使用 `hermes gateway start`）。对于一次性调试，你可以使用 `hermes cron tick` 手动触发一次 tick。

<a id="check-4-check-the-system-clock-and-timezone"></a>
### 检查 4：检查系统时钟和时区

任务使用本地时区。如果你的机器时钟错误或处于非预期的时区，任务将在错误的时间触发。验证：

```bash
date
hermes cron list   # 将 next_run 时间与本地时间进行比较
```

---

<a id="delivery-failures"></a>
## 投递失败

<a id="check-1-verify-the-deliver-target-is-correct"></a>
### 检查 1：确认投递目标正确

投递目标区分大小写，并且需要配置正确的平台。配置错误的目标会静默地丢弃响应。

| 目标 | 需要配置 |
|--------|----------|
| `telegram` | `~/.hermes/.env` 中的 `TELEGRAM_BOT_TOKEN` |
| `discord` | `~/.hermes/.env` 中的 `DISCORD_BOT_TOKEN` |
| `slack` | `~/.hermes/.env` 中的 `SLACK_BOT_TOKEN` |
| `whatsapp` | 已配置 WhatsApp 网关 |
| `signal` | 已配置 Signal 网关 |
| `matrix` | 已配置 Matrix 家服务器 |
| `email` | 在 `config.yaml` 中配置了 SMTP |
| `sms` | 已配置短信提供商 |
| `local` | 对 `~/.hermes/cron/output/` 的写入权限 |
| `origin` | 投递到创建该任务的聊天 |

其他支持的平台包括 `mattermost`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot` 和 `webhook`。你也可以使用 `platform:chat_id` 语法（例如 `telegram:-1001234567890`）定位到特定聊天。

如果投递失败，任务仍会运行——只是不会发送到任何地方。检查 `hermes cron list` 中更新的 `last_error` 字段（如果可用）。

<a id="check-2-check-silent-usage"></a>
### 检查 2：检查 `[SILENT]` 的使用

如果你的 cron 任务没有产生任何输出，或者 Agent 以 `[SILENT]` 响应，则投递被抑制。这对于监控任务来说是故意的——但请确保你的提示词没有意外地抑制所有内容。
提示“如果没有任何变化，请回复[SILENT]”也会静默吞掉非空响应。请检查你的条件逻辑。

<a id="check-3-platform-token-permissions"></a>
### 检查点 3：平台令牌权限

每个消息平台机器人需要特定的权限才能接收消息。如果投递静默失败：

- **Telegram**：机器人必须是目标群组/频道的管理员
- **Discord**：机器人必须有在目标频道发送消息的权限
- **Slack**：机器人必须被添加到工作区，并拥有 `chat:write` 作用域

<a id="check-4-response-wrapping"></a>
### 检查点 4：响应包装

默认情况下，cron 响应会包裹头部和尾部（`config.yaml` 中的 `cron.wrap_response: true`）。某些平台或集成可能无法很好地处理这种情况。若要禁用：

```yaml
cron:
  wrap_response: false
```

---

<a id="skill-loading-failures"></a>
## 技能加载失败

<a id="check-1-verify-skills-are-installed"></a>
### 检查点 1：确认技能已安装

```bash
hermes skills list
```

技能必须先安装，才能附加到 cron 作业。如果缺少某个技能，先通过 `hermes skills install &lt;skill-name&gt;` 或 CLI 中的 `/skills` 安装它。

<a id="check-2-check-skill-name-vs-skill-folder-name"></a>
### 检查点 2：检查技能名称与技能文件夹名称

技能名称区分大小写，必须与已安装技能的文件夹名称一致。如果你的作业指定了 `ai-funding-daily-report`，但技能文件夹也是 `ai-funding-daily-report`，请通过 `hermes skills list` 确认确切的名称。

<a id="check-3-skills-that-require-interactive-tools"></a>
### 检查点 3：需要交互式工具的技能

Cron 作业运行时禁用了 `cronjob`、`messaging` 和 `clarify` 工具集。这可以防止递归创建 cron、直接发送消息（投递由调度器处理）以及交互式提示。如果某个技能依赖这些工具集，那么它在 cron 上下文中将无法工作。

请查阅技能文档，确认它能在非交互式（无头）模式下正常工作。

<a id="check-4-multi-skill-ordering"></a>
### 检查点 4：多技能排序

当使用多个技能时，它们按顺序加载。如果技能 A 依赖于来自技能 B 的上下文，请确保 B 先加载：

```bash
/cron add "0 9 * * *" "..." --skill context-skill --skill target-skill
```

在此示例中，`context-skill` 在 `target-skill` 之前加载。

---

<a id="job-errors-and-failures"></a>
## 作业错误与失败

<a id="check-1-review-recent-job-output"></a>
### 检查点 1：查看最近的作业输出

如果某个作业运行但失败了，你可以在以下位置看到错误上下文：

1. 作业投递的聊天中（如果投递成功）
2. `~/.hermes/logs/agent.log` 中的调度器消息（或 `errors.log` 中的警告）
3. 通过 `hermes cron list` 查看作业的 `last_run` 元数据

<a id="check-2-common-error-patterns"></a>
### 检查点 2：常见错误模式

**脚本出现“No such file or directory”**
`script` 路径必须是绝对路径（或相对于 Hermes 配置目录的路径）。验证：
```bash
ls ~/.hermes/scripts/your-script.py   # 必须存在
hermes cron edit <job_id> --script ~/.hermes/scripts/your-script.py
```

**执行作业时出现“Skill not found”**
技能必须安装在运行调度器的机器上。如果你在机器之间切换，技能不会自动同步——请使用 `hermes skills install &lt;skill-name&gt;` 重新安装。

**作业运行但未投递任何内容**
很可能是投递目标问题（参见上面的投递失败）或静默抑制的响应（`[SILENT]`）。
**任务挂起或超时**  
调度器使用基于不活动超时（默认 600 秒，可通过 `HERMES_CRON_TIMEOUT` 环境变量配置，`0` 表示无限制）。只要 Agent 在持续调用工具，它就可以一直运行——计时器仅在持续不活动后触发。长时间运行的任务应使用脚本来处理数据收集，只交付结果。

<a id="check-3-lock-contention"></a>
### 检查 3：锁竞争

调度器使用基于文件的锁定来防止重叠的滴答。如果有两个网关实例在运行（或 CLI 会话与网关冲突），任务可能被延迟或跳过。

杀死重复的网关进程：
```bash
ps aux | grep hermes
# 杀死重复进程，只保留一个
```

<a id="check-4-permissions-on-jobs-json"></a>
### 检查 4：jobs.json 的权限

任务存储在 `~/.hermes/cron/jobs.json`。如果该文件不能被您的用户读取/写入，调度器会静默失败：

```bash
ls -la ~/.hermes/cron/jobs.json
chmod 600 ~/.hermes/cron/jobs.json   # 您的用户应该拥有它
```

---

<a id="performance-issues"></a>
## 性能问题

<a id="slow-job-startup"></a>
### 任务启动慢

每个 cron 任务都会创建一个全新的 AIAgent 会话，可能涉及提供者身份验证和模型加载。对于时间敏感的计划，增加缓冲区时间（例如，使用 `0 8 * * *` 而非 `0 9 * * *`）。

<a id="too-many-overlapping-jobs"></a>
### 过多重叠的任务

调度器在每个滴答内顺序执行任务。如果多个任务同时到期，它们会一个接一个地运行。考虑错开计划（例如，使用 `0 9 * * *` 和 `5 9 * * *`，而不是都在 `0 9 * * *`），以避免延迟。

<a id="large-script-output"></a>
### 大量脚本输出

转储数兆字节输出的脚本会降低 Agent 速度，并可能触及令牌限制。在脚本层面进行过滤/汇总——只输出 Agent 需要推理的内容。

---

<a id="diagnostic-commands"></a>
## 诊断命令

```bash
hermes cron list                    # 显示所有任务、状态、下次运行时间
hermes cron run <job_id>            # 安排下一次滴答时运行（用于测试）
hermes cron edit <job_id>           # 修复配置问题
hermes logs                         # 查看最近的 Hermes 日志
hermes skills list                  # 验证已安装的技能
```

---

<a id="getting-more-help"></a>
## 获取更多帮助

如果您已查阅本指南但问题仍然存在：

1. 使用 `hermes cron run &lt;job_id&gt;` 运行任务（在下一次网关滴答时触发）并查看聊天输出中的错误
2. 检查 `~/.hermes/logs/agent.log` 中的调度器消息和 `~/.hermes/logs/errors.log` 中的警告
3. 在 [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 打开问题，附带：
   - 任务 ID 和计划
   - 交付目标
   - 您期望的结果与实际结果
   - 日志中的相关错误消息

---

*有关完整的 cron 参考，请参阅[使用 Cron 自动化任何任务](/guides/automate-with-cron)和[计划任务（Cron）](/user-guide/features/cron)。*
