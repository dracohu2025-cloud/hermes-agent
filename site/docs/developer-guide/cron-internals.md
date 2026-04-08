---
sidebar_position: 11
title: "Cron 内部机制"
description: "Hermes 如何存储、调度、编辑、暂停、加载 Skill 以及交付 Cron 任务"
---

# Cron 内部机制

Cron 子系统提供定时任务执行功能——从简单的单次延迟任务到带有 Skill 注入和跨平台交付的循环 Cron 表达式任务。

## 核心文件

| 文件 | 用途 |
|------|---------|
| `cron/jobs.py` | 任务模型、存储，以及对 `jobs.json` 的原子读写 |
| `cron/scheduler.py` | 调度器循环——到期任务检测、执行、重复状态追踪 |
| `tools/cronjob_tools.py` | 面向模型的 `cronjob` 工具注册与处理器 |
| `gateway/run.py` | Gateway 集成——在长期运行的循环中进行 Cron 滴答（ticking） |
| `hermes_cli/cron.py` | CLI `hermes cron` 子命令 |

## 调度模型

支持四种调度格式：

| 格式 | 示例 | 行为 |
|--------|---------|----------|
| **相对延迟** | `30m`, `2h`, `1d` | 单次触发，在指定时长后执行 |
| **间隔** | `every 2h`, `every 30m` | 循环触发，按固定间隔执行 |
| **Cron 表达式** | `0 9 * * *` | 标准 5 字段 Cron 语法（分、时、日、月、周） |
| **ISO 时间戳** | `2025-01-15T09:00:00` | 单次触发，在精确的时间点执行 |

面向模型的接口是一个单一的 `cronjob` 工具，包含动作风格的操作：`create`、`list`、`update`、`pause`、`resume`、`run`、`remove`。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中，采用原子写语义（先写入临时文件，然后重命名）。每个任务记录包含：

```json
{
  "id": "job_abc123",
  "name": "Daily briefing",
  "prompt": "Summarize today's AI news and funding rounds",
  "schedule": "0 9 * * *",
  "skills": ["ai-funding-daily-report"],
  "deliver": "telegram:-1001234567890",
  "repeat": null,
  "state": "scheduled",
  "next_run": "2025-01-16T09:00:00Z",
  "run_count": 42,
  "created_at": "2025-01-01T00:00:00Z",
  "model": null,
  "provider": null,
  "script": null
}
```

### 任务生命周期状态

| 状态 | 含义 |
|-------|---------|
| `scheduled` | 激活状态，将在下一个预定时间触发 |
| `paused` | 已暂停——在恢复前不会触发 |
| `completed` | 重复次数已耗尽，或已触发过的单次任务 |
| `running` | 正在执行（瞬时状态） |

### 向后兼容性

旧版任务可能使用单个 `skill` 字段而不是 `skills` 数组。调度器在加载时会对其进行归一化处理——单个 `skill` 会被提升为 `skills: [skill]`。

## 调度器运行时

### 滴答周期（Tick Cycle）

调度器按周期性滴答运行（默认：每 60 秒）：

```text
tick()
  1. 获取调度器锁（防止滴答重叠）
  2. 从 jobs.json 加载所有任务
  3. 过滤出到期任务 (next_run <= now 且 state == "scheduled")
  4. 对于每个到期任务：
     a. 将状态设为 "running"
     b. 创建全新的 AIAgent 会话（无对话历史）
     c. 按顺序加载关联的 Skill（作为用户消息注入）
     d. 通过 Agent 运行任务 Prompt
     e. 将响应交付至配置的目标
     f. 更新 run_count，计算 next_run
     g. 如果重复次数耗尽 → state = "completed"
     h. 否则 → state = "scheduled"
  5. 将更新后的任务写回 jobs.json
  6. 释放调度器锁
```

### Gateway 集成

在 Gateway 模式下，调度器滴答被集成到 Gateway 的主事件循环中。Gateway 在其周期性维护循环中调用 `scheduler.tick()`，该循环与消息处理并行运行。

在 CLI 模式下，Cron 任务仅在运行 `hermes cron` 命令或处于活跃 CLI 会话期间触发。

### 全新会话隔离

每个 Cron 任务都在一个完全全新的 Agent 会话中运行：

- 没有来自之前运行的对话历史
- 没有对之前 Cron 执行的记忆（除非持久化到记忆/文件中）
- Prompt 必须是自包含的——Cron 任务无法提出澄清性问题
- `cronjob` 工具集被禁用（递归保护）

## 基于 Skill 的任务

Cron 任务可以通过 `skills` 字段关联一个或多个 Skill。执行时：

1. 按指定顺序加载 Skill
2. 每个 Skill 的 SKILL.md 内容作为上下文注入
3. 任务的 Prompt 作为任务指令附加在后
4. Agent 处理组合后的 Skill 上下文 + Prompt

这实现了可复用、经过测试的工作流，而无需将完整指令粘贴到 Cron Prompt 中。例如：

```
创建每日融资报告 → 关联 "ai-funding-daily-report" Skill
```

### 基于脚本的任务

任务还可以通过 `script` 字段关联一个 Python 脚本。该脚本在每次 Agent 轮次*之前*运行，其标准输出（stdout）作为上下文注入到 Prompt 中。这支持了数据采集和变更检测模式：

```python
# ~/.hermes/scripts/check_competitors.py
import requests, json
# 获取竞争对手的发布日志，与上次运行进行对比
# 将摘要打印到 stdout —— Agent 进行分析并报告
```

## 交付模型

Cron 任务结果可以交付到任何受支持的平台：

| 目标 | 语法 | 示例 |
|--------|--------|---------|
| 原始聊天 | `origin` | 交付到创建该任务的聊天中 |
| 本地文件 | `local` | 保存到 `~/.hermes/cron/output/` |
| Telegram | `telegram` 或 `telegram:<chat_id>` | `telegram:-1001234567890` |
| Discord | `discord` 或 `discord:#channel` | `discord:#engineering` |
| Slack | `slack` | 交付到 Slack 主频道 |
| WhatsApp | `whatsapp` | 交付到 WhatsApp 主账号 |
| Signal | `signal` | 交付到 Signal |
| Matrix | `matrix` | 交付到 Matrix 主房间 |
| Mattermost | `mattermost` | 交付到 Mattermost 主站 |
| Email | `email` | 通过电子邮件交付 |
| SMS | `sms` | 通过短信交付 |
| Home Assistant | `homeassistant` | 交付到 HA 对话 |
| DingTalk | `dingtalk` | 交付到钉钉 |
| Feishu | `feishu` | 交付到飞书 |
| WeCom | `wecom` | 交付到企业微信 |

对于 Telegram 话题（topics），使用格式 `telegram:<chat_id>:<thread_id>`（例如：`telegram:-1001234567890:17585`）。

### 响应包装

默认情况下（`cron.wrap_response: true`），Cron 交付内容会被包装：
- 包含标识 Cron 任务名称和任务的页眉
- 包含说明 Agent 无法在对话中看到已交付消息的页脚

Cron 响应中的 `[SILENT]` 前缀会完全抑制交付——这对于只需要写入文件或执行副作用的任务非常有用。

### 会话隔离

Cron 交付内容**不会**镜像到 Gateway 会话的对话历史中。它们仅存在于 Cron 任务自身的会话中。这防止了在目标聊天的对话中出现消息交替违规。

## 递归保护

由 Cron 运行的会话会禁用 `cronjob` 工具集。这可以防止：
- 预定任务创建新的 Cron 任务
- 可能导致 Token 使用量爆炸的递归调度
- 在任务内部意外修改任务调度表

## 锁定机制

调度器使用基于文件的锁定，以防止重叠的滴答重复执行同一批到期任务。这在 Gateway 模式下非常重要，因为如果前一个滴答的执行时间超过了滴答间隔，多个维护循环可能会发生重叠。

## CLI 接口

`hermes cron` CLI 提供了直接的任务管理功能：

```bash
hermes cron list                    # 显示所有任务
hermes cron create                  # 交互式创建任务 (别名: add)
hermes cron edit <job_id>           # 编辑任务配置
hermes cron pause <job_id>          # 暂停运行中的任务
hermes cron resume <job_id>         # 恢复已暂停的任务
hermes cron run <job_id>            # 立即触发执行
hermes cron remove <job_id>         # 删除任务
```

## 相关文档

- [Cron 功能指南](/user-guide/features/cron)
- [Gateway 内部机制](./gateway-internals.md)
- [Agent 循环内部机制](./agent-loop.md)
