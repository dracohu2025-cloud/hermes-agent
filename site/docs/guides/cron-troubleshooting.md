---
sidebar_position: 12
title: "Cron 故障排查"
description: "诊断并修复常见的 Hermes cron 问题 —— 任务不触发、投递失败、技能加载错误和性能问题"
---

# Cron 故障排查 {#cron-troubleshooting}

当 cron 任务没有按预期运行时，请按顺序检查以下内容。大多数问题都可以归为四类：定时、投递、权限或技能加载。

---

## 任务不触发 {#jobs-not-firing}

### 检查 1：确认任务存在且处于活跃状态 {#check-1-verify-the-job-exists-and-is-active}

```bash
hermes cron list
```

查找该任务并确认其状态为 `[active]`（不是 `[paused]` 或 `[completed]`）。如果显示 `[completed]`，说明重复次数可能已耗尽 —— 编辑任务以重置它。

### 检查 2：确认定时设置正确 {#check-2-confirm-the-schedule-is-correct}

格式错误的定时表达式会静默地默认为一次性任务，或完全被拒绝。测试你的表达式：

| 你的表达式 | 应该解析为 |
|-----------|-----------|
| `0 9 * * *` | 每天上午 9:00 |
| `0 9 * * 1` | 每周一上午 9:00 |
| `every 2h` | 从当前时间起每 2 小时 |
| `30m` | 30 分钟后 |
| `2025-06-01T09:00:00` | 2025 年 6 月 1 日上午 9:00 UTC |

如果任务触发一次后从列表中消失，说明这是一次性定时设置（`30m`、`1d` 或 ISO 时间戳）—— 这是预期行为。

### 检查 3：gateway 是否在运行？ {#check-3-is-the-gateway-running}

Cron 任务由 gateway 的后台 ticker 线程触发，该线程每 60 秒 tick 一次。普通的 CLI 聊天会话**不会**自动触发 cron 任务。

如果你希望任务自动触发，需要有一个正在运行的 gateway（`hermes gateway` 或 `hermes serve`）。如需一次性调试，可以手动触发一次 tick：`hermes cron tick`。

### 检查 4：检查系统时钟和时区 {#check-4-check-the-system-clock-and-timezone}

任务使用本地时区。如果你的机器时钟错误，或者时区与预期不符，任务将在错误的时间触发。请验证：

```bash
date
hermes cron list   # 将 next_run 时间与本地时间对比
```

---

## 投递失败 {#delivery-failures}

### 检查 1：确认投递目标正确 {#check-1-verify-the-deliver-target-is-correct}

投递目标区分大小写，且需要正确配置对应的平台。配置错误的目标会静默丢弃响应。

| 目标 | 需要 |
|------|------|
| `telegram` | `TELEGRAM_BOT_TOKEN` 配置在 `~/.hermes/.env` 中 |
| `discord` | `DISCORD_BOT_TOKEN` 配置在 `~/.hermes/.env` 中 |
| `slack` | `SLACK_BOT_TOKEN` 配置在 `~/.hermes/.env` 中 |
| `whatsapp` | WhatsApp gateway 已配置 |
| `signal` | Signal gateway 已配置 |
| `matrix` | Matrix homeserver 已配置 |
| `email` | SMTP 已在 `config.yaml` 中配置 |
| `sms` | SMS 提供商已配置 |
| `local` | 对 `~/.hermes/cron/output/` 有写入权限 |
| `origin` | 投递到创建该任务的聊天会话中 |
其他支持的平台包括 `mattermost`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot` 和 `webhook`。你也可以用 `platform:chat_id` 的格式指定具体聊天（例如 `telegram:-1001234567890`）。

如果投递失败，任务仍会运行——只是不会发送到任何地方。用 `hermes cron list` 查看更新的 `last_error` 字段（如果有的话）。

### 检查 2：检查 `[SILENT]` 的使用 {#check-2-check-silent-usage}

如果你的定时任务没有输出，或者 Agent 回复了 `[SILENT]`，投递就会被抑制。这对监控类任务是预期行为——但要确认你的提示词没有意外地把所有内容都压掉。

提示词里写"如果没变化就回复 [SILENT]"，也会把非空响应默默吞掉。检查一下你的条件逻辑。

### 检查 3：平台 Token 权限 {#check-3-platform-token-permissions}

每个消息平台的机器人需要特定权限才能接收消息。如果投递静默失败：

- **Telegram**：机器人必须是目标群组/频道的管理员
- **Discord**：机器人必须有权限在目标频道发送消息
- **Slack**：机器人必须已加入工作区，并拥有 `chat:write` 权限

### 检查 4：响应包装 {#check-4-response-wrapping}

默认情况下，定时任务响应会加上头部和尾部包装（`config.yaml` 中 `cron.wrap_response: true`）。某些平台或集成可能处理不好这个。要关闭：

```yaml
cron:
  wrap_response: false
```

---

## Skill 加载失败 {#skill-loading-failures}

### 检查 1：确认 Skill 已安装 {#check-1-verify-skills-are-installed}

```bash
hermes skills list
```

Skill 必须先安装才能绑定到定时任务。如果缺少某个 Skill，先用 `hermes skills install &lt;skill-name&gt;` 安装，或者在 CLI 里通过 `/skills` 安装。

### 检查 2：检查 Skill 名称与文件夹名称 {#check-2-check-skill-name-vs-skill-folder-name}

Skill 名称区分大小写，必须与已安装 Skill 的文件夹名称一致。如果你的任务写的是 `ai-funding-daily-report`，但 Skill 文件夹是 `ai-funding-daily-report`，那就从 `hermes skills list` 里确认准确名称。

### 检查 3：需要交互式工具的 Skill {#check-3-skills-that-require-interactive-tools}
Cron 作业运行时，`cronjob`、`messaging` 和 `clarify` 工具集会被禁用。这样可以防止递归创建 Cron、直接发送消息（调度器会负责投递），以及交互式提示。如果某个 Skill 依赖这些工具集，它在 Cron 场景下就无法工作。

请查看该 Skill 的文档，确认它支持非交互式（headless）模式。

### 检查 4：多 Skill 的加载顺序 {#check-4-multi-skill-ordering}

使用多个 Skill 时，它们会按顺序加载。如果 Skill A 依赖 Skill B 的上下文，要确保 B 先加载：

```bash
/cron add "0 9 * * *" "..." --skill context-skill --skill target-skill
```

这个例子中，`context-skill` 会在 `target-skill` 之前加载。

---

## 作业错误与失败 {#job-errors-and-failures}

### 检查 1：查看近期作业输出 {#check-1-review-recent-job-output}

如果作业运行后失败了，你可以在以下位置找到错误上下文：

1. 作业投递的聊天窗口（如果投递成功）
2. `~/.hermes/logs/agent.log` 中的调度器消息（或者 `errors.log` 中的警告）
3. 通过 `hermes cron list` 查看作业的 `last_run` 元数据

### 检查 2：常见错误模式 {#check-2-common-error-patterns}

**脚本提示 "No such file or directory"**
`script` 路径必须是绝对路径（或相对于 Hermes 配置目录的相对路径）。请确认：
```bash
ls ~/.hermes/scripts/your-script.py   # 文件必须存在
hermes cron edit <job_id> --script ~/.hermes/scripts/your-script.py
```

**作业执行时提示 "Skill not found"**
Skill 必须安装在运行调度器的机器上。如果你换了机器，Skill 不会自动同步——需要用 `hermes skills install &lt;skill-name&gt;` 重新安装。

**作业运行了，但没有投递任何内容**
很可能是投递目标出了问题（见上文"投递失败"部分），或者响应被静默抑制了（`[SILENT]`）。

**作业卡住或超时**
调度器采用基于无活动的超时机制（默认 600 秒，可通过 `HERMES_CRON_TIMEOUT` 环境变量配置，设为 `0` 表示无限制）。只要 Agent 在积极调用工具，它就可以一直运行——计时器只在持续无活动后才会触发。长时间运行的作业应该使用脚本来处理数据收集，只投递最终结果。
### 检查 3：锁竞争 {#check-3-lock-contention}

调度器使用基于文件的锁来防止 tick 重叠。如果两个 gateway 实例在同时运行（或 CLI 会话与 gateway 冲突），作业可能会被延迟或跳过。

终止重复的 gateway 进程：
```bash
ps aux | grep hermes
# 终止重复进程，只保留一个
```

### 检查 4：jobs.json 的权限 {#check-4-permissions-on-jobs-json}

作业存储在 `~/.hermes/cron/jobs.json` 中。如果该文件对当前用户不可读/不可写，调度器会静默失败：

```bash
ls -la ~/.hermes/cron/jobs.json
chmod 600 ~/.hermes/cron/jobs.json   # 该文件应由你的用户所有
```

---

## 性能问题 {#performance-issues}

### 作业启动慢 {#slow-job-startup}

每个 cron 作业都会创建一个全新的 AIAgent 会话，这可能涉及 provider 认证和模型加载。对于时间敏感的调度，请预留缓冲时间（例如用 `0 8 * * *` 而不是 `0 9 * * *`）。

### 重叠作业过多 {#too-many-overlapping-jobs}

调度器在每个 tick 内按顺序执行作业。如果多个作业在同一时间到期，它们会依次运行。考虑错开调度时间（例如用 `0 9 * * *` 和 `5 9 * * *`，而不是两个都用 `0 9 * * *`）以避免延迟。

### 脚本输出过大 {#large-script-output}

输出数兆字节的脚本会拖慢 Agent，并可能触及 token 上限。在脚本层面做好过滤/汇总——只输出 Agent 推理所需的内容。

---

## 诊断命令 {#diagnostic-commands}

```bash
hermes cron list                    # 显示所有作业、状态、下次运行时间
hermes cron run <job_id>            # 安排到下一个 tick 执行（用于测试）
hermes cron edit <job_id>           # 修复配置问题
hermes logs                         # 查看最近的 Hermes 日志
hermes skills list                  # 确认已安装的技能
```

---

## 获取更多帮助 {#getting-more-help}

如果你已经按本指南排查过，但问题仍然存在：

1. 用 `hermes cron run &lt;job_id&gt;` 运行作业（会在下一个 gateway tick 触发），观察聊天输出中的错误
2. 检查 `~/.hermes/logs/agent.log` 中的调度器消息，以及 `~/.hermes/logs/errors.log` 中的警告
3. 在 [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 提交 issue，附上：
   - 作业 ID 和调度表达式
   - 投递目标
   - 预期行为与实际发生的情况
   - 日志中的相关错误信息
---

*完整的 cron 参考请见 [使用 Cron 实现自动化](/guides/automate-with-cron) 和 [定时任务 (Cron)](/user-guide/features/cron)。*
