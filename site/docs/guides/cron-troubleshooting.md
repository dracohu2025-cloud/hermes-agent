---
sidebar_position: 12
title: "Cron 故障排查"
description: "诊断并修复常见的 Hermes cron 问题——任务未触发、投递失败、技能加载错误以及性能问题"
---

# Cron 故障排查

当 cron 任务的表现不如预期时，请按顺序执行以下检查。大多数问题都属于以下四类之一：时间安排、投递、权限或技能加载。

---

## 任务未触发

### 检查 1：验证任务是否存在且处于活动状态

```bash
hermes cron list
```

找到该任务并确认其状态为 `[active]`（而不是 `[paused]` 或 `[completed]`）。如果显示为 `[completed]`，则可能是重复次数已用尽——请编辑该任务以重置次数。

### 检查 2：确认时间表是否正确

格式错误的时间表会静默地默认为单次执行或被完全拒绝。测试您的表达式：

| 您的表达式 | 预期评估结果 |
|----------------|-------------------|
| `0 9 * * *` | 每天上午 9:00 |
| `0 9 * * 1` | 每周一上午 9:00 |
| `every 2h` | 从现在起每 2 小时 |
| `30m` | 从现在起 30 分钟后 |
| `2025-06-01T09:00:00` | 2025 年 6 月 1 日上午 9:00 UTC |

如果任务执行一次后从列表中消失，说明这是一个单次执行的时间表（`30m`、`1d` 或 ISO 时间戳）——这是预期行为。

### 检查 3：网关是否在运行？

Cron 任务由网关的后台计时器线程触发，该线程每 60 秒跳动一次。常规的 CLI 聊天会话**不会**自动触发 cron 任务。

如果您希望任务自动触发，则需要运行网关（`hermes gateway` 或 `hermes serve`）。对于一次性调试，您可以使用 `hermes cron tick` 手动触发一次跳动。

### 检查 4：检查系统时钟和时区

任务使用本地时区。如果您的机器时钟不准确，或者处于与预期不同的时区，任务将在错误的时间触发。请验证：

```bash
date
hermes cron list   # 将 next_run 时间与本地时间进行比较
```

---

## 投递失败

### 检查 1：验证投递目标是否正确

投递目标区分大小写，并且需要配置正确的平台。配置错误的目标会静默丢弃响应。

| 目标 | 要求 |
|--------|----------|
| `telegram` | `~/.hermes/.env` 中的 `TELEGRAM_BOT_TOKEN` |
| `discord` | `~/.hermes/.env` 中的 `DISCORD_BOT_TOKEN` |
| `slack` | `~/.hermes/.env` 中的 `SLACK_BOT_TOKEN` |
| `whatsapp` | 已配置 WhatsApp 网关 |
| `signal` | 已配置 Signal 网关 |
| `matrix` | 已配置 Matrix 家庭服务器 |
| `email` | 在 `config.yaml` 中配置了 SMTP |
| `sms` | 已配置 SMS 提供商 |
| `local` | 对 `~/.hermes/cron/output/` 的写入权限 |
| `origin` | 投递到创建任务时的聊天窗口 |

其他支持的平台包括 `mattermost`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles` 和 `webhook`。您还可以使用 `platform:chat_id` 语法（例如 `telegram:-1001234567890`）指定特定的聊天窗口。

如果投递失败，任务仍会运行——只是不会发送到任何地方。请检查 `hermes cron list` 以查看更新后的 `last_error` 字段（如果可用）。

### 检查 2：检查 `[SILENT]` 的使用

如果您的 cron 任务没有产生输出，或者 Agent 响应了 `[SILENT]`，则投递会被抑制。这对于监控任务是有意为之的——但请确保您的提示词（prompt）没有意外地抑制了所有内容。

如果提示词写着“如果没有任何变化，请回复 [SILENT]”，那么它也会静默吞掉非空的响应。请检查您的条件逻辑。

### 检查 3：平台令牌权限

每个消息平台机器人都需要特定的权限才能接收消息。如果投递静默失败：

- **Telegram**：机器人必须是目标群组/频道中的管理员
- **Discord**：机器人必须拥有在目标频道发送消息的权限
- **Slack**：机器人必须已添加到工作区并拥有 `chat:write` 作用域

### 检查 4：响应包装

默认情况下，cron 响应会带有页眉和页脚（`config.yaml` 中的 `cron.wrap_response: true`）。某些平台或集成可能无法很好地处理此格式。若要禁用：

```yaml
cron:
  wrap_response: false
```

---

## 技能加载失败

### 检查 1：验证技能是否已安装

```bash
hermes skills list
```

技能必须先安装，然后才能附加到 cron 任务中。如果缺少某个技能，请先使用 `hermes skills install <skill-name>` 或通过 CLI 中的 `/skills` 进行安装。

### 检查 2：检查技能名称与技能文件夹名称

技能名称区分大小写，且必须与已安装技能的文件夹名称匹配。如果您的任务指定了 `ai-funding-daily-report`，但技能文件夹是 `ai-funding-daily-report`，请从 `hermes skills list` 中确认确切名称。

### 检查 3：需要交互式工具的技能

Cron 任务在禁用 `cronjob`、`messaging` 和 `clarify` 工具集的情况下运行。这可以防止递归创建 cron、直接发送消息（投递由调度程序处理）以及交互式提示。如果某个技能依赖于这些工具集，它将无法在 cron 上下文中工作。

请查看技能的文档，确认它是否可以在非交互式（无头）模式下工作。

### 检查 4：多技能排序

使用多个技能时，它们会按顺序加载。如果技能 A 依赖于技能 B 的上下文，请确保 B 先加载：

```bash
/cron add "0 9 * * *" "..." --skill context-skill --skill target-skill
```

在此示例中，`context-skill` 会在 `target-skill` 之前加载。

---

## 任务错误与失败

### 检查 1：查看最近的任务输出

如果任务运行并失败，您可以在以下位置查看错误上下文：

1. 任务投递的聊天窗口（如果投递成功）
2. `~/.hermes/logs/agent.log`（调度程序消息）或 `errors.log`（警告）
3. 通过 `hermes cron list` 查看任务的 `last_run` 元数据

### 检查 2：常见错误模式

**脚本提示 "No such file or directory"**
`script` 路径必须是绝对路径（或相对于 Hermes 配置目录的路径）。请验证：
```bash
ls ~/.hermes/scripts/your-script.py   # 必须存在
hermes cron edit <job_id> --script ~/.hermes/scripts/your-script.py
```

**任务执行时提示 "Skill not found"**
技能必须安装在运行调度程序的机器上。如果您在不同机器间切换，技能不会自动同步——请使用 `hermes skills install <skill-name>` 重新安装。

**任务运行但未投递任何内容**
很可能是投递目标问题（见上文“投递失败”）或响应被静默抑制（`[SILENT]`）。

**任务挂起或超时**
调度程序使用基于不活动的超时机制（默认 600 秒，可通过 `HERMES_CRON_TIMEOUT` 环境变量配置，`0` 表示无限制）。只要 Agent 在主动调用工具，它就可以一直运行——计时器仅在持续不活动后才会触发。长时间运行的任务应使用脚本来处理数据收集，并仅投递结果。

### 检查 3：锁竞争

调度程序使用基于文件的锁来防止重叠的跳动。如果运行了两个网关实例（或者 CLI 会话与网关冲突），任务可能会被延迟或跳过。

终止重复的网关进程：
```bash
ps aux | grep hermes
# 终止重复进程，仅保留一个
```

### 检查 4：jobs.json 的权限

任务存储在 `~/.hermes/cron/jobs.json` 中。如果您的用户无法读取/写入此文件，调度程序将静默失败：

```bash
ls -la ~/.hermes/cron/jobs.json
chmod 600 ~/.hermes/cron/jobs.json   # 应由您的用户拥有
```

---

## 性能问题

### 任务启动缓慢

每个 cron 任务都会创建一个全新的 AIAgent 会话，这可能涉及提供商身份验证和模型加载。对于时间敏感的任务，请增加缓冲时间（例如，使用 `0 8 * * *` 而不是 `0 9 * * *`）。

### 重叠任务过多

调度程序在每次跳动时按顺序执行任务。如果多个任务在同一时间到期，它们会依次运行。考虑错开时间表（例如，使用 `0 9 * * *` 和 `5 9 * * *`，而不是都设在 `0 9 * * *`）以避免延迟。

### 脚本输出过大

输出数兆字节数据的脚本会拖慢 Agent 的速度，并可能触及令牌限制。请在脚本层面进行过滤/总结——仅输出 Agent 需要推理的内容。

---

## 诊断命令

```bash
hermes cron list                    # 显示所有任务、状态、next_run 时间
hermes cron run <job_id>            # 安排在下一次跳动时执行（用于测试）
hermes cron edit <job_id>           # 修复配置问题
hermes logs                         # 查看最近的 Hermes 日志
hermes skills list                  # 验证已安装的技能
```
---

## 获取更多帮助

如果你已经按照本指南排查但问题依然存在：

1. 使用 `hermes cron run <job_id>` 运行任务（在下一次网关触发时执行），并观察聊天输出中的错误信息。
2. 检查 `~/.hermes/logs/agent.log` 中的调度程序消息，以及 `~/.hermes/logs/errors.log` 中的警告信息。
3. 在 [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 提交 Issue，并提供以下信息：
   - 任务 ID 和调度计划
   - 交付目标
   - 你的预期结果与实际发生的情况
   - 日志中相关的错误信息

---

*如需完整的 cron 参考，请参阅 [使用 Cron 实现自动化](/guides/automate-with-cron) 和 [定时任务 (Cron)](/user-guide/features/cron)。*
