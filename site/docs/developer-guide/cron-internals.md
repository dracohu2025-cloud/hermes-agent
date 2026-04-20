---
sidebar_position: 11
title: "Cron 内部机制"
description: "Hermes 如何存储、调度、编辑、暂停、加载 Skill 和投递 Cron 任务"
---

# Cron 内部机制 {#cron-internals}

Cron 子系统提供定时任务执行功能——从简单的单次延迟任务，到支持 Skill 注入和跨平台投递的周期性 Cron 表达式任务。

## 关键文件 {#key-files}

| 文件 | 用途 |
|------|---------|
| `cron/jobs.py` | 任务模型、存储、对 `jobs.json` 的原子读写 |
| `cron/scheduler.py` | 调度器循环——到期任务检测、执行、重复次数追踪 |
| `tools/cronjob_tools.py` | 面向模型的 `cronjob` 工具注册与处理程序 |
| `gateway/run.py` | Gateway 集成——在常驻循环中驱动 Cron 滴答 |
| `hermes_cli/cron.py` | CLI `hermes cron` 子命令 |

## 调度模型 {#scheduling-model}

支持四种调度格式：

| 格式 | 示例 | 行为 |
|--------|---------|----------|
| **相对延迟** | `30m`, `2h`, `1d` | 单次执行，在指定时长后触发 |
| **间隔周期** | `every 2h`, `every 30m` | 周期性执行，按固定间隔触发 |
| **Cron 表达式** | `0 9 * * *` | 标准 5 字段 Cron 语法（分、时、日、月、星期） |
| **ISO 时间戳** | `2025-01-15T09:00:00` | 单次执行，在精确时间点触发 |

面向模型的接口是一个单独的 `cronjob` 工具，采用动作式操作：`create`、`list`、`update`、`pause`、`resume`、`run`、`remove`。

## 任务存储 {#job-storage}

任务存储在 `~/.hermes/cron/jobs.json` 中，采用原子写入语义（先写入临时文件，再重命名）。每条任务记录包含：

```json
{
  "id": "a1b2c3d4e5f6",
  "name": "Daily briefing",
  "prompt": "Summarize today's AI news and funding rounds",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",
    "display": "0 9 * * *"
  },
  "skills": ["ai-funding-daily-report"],
  "deliver": "telegram:-1001234567890",
  "repeat": {
    "times": null,
    "completed": 42
  },
  "state": "scheduled",
  "enabled": true,
  "next_run_at": "2025-01-16T09:00:00Z",
  "last_run_at": "2025-01-15T09:00:00Z",
  "last_status": "ok",
  "created_at": "2025-01-01T00:00:00Z",
  "model": null,
  "provider": null,
  "script": null
}
```

### 任务生命周期状态 {#job-lifecycle-states}

| 状态 | 含义 |
|-------|---------|
| `scheduled` | 活跃状态，将在下次预定时间触发 |
| `paused` | 已暂停——恢复前不会触发 |
| `completed` | 重复次数已耗尽，或单次任务已执行完毕 |
| `running` | 正在执行中（临时状态） |

### 向后兼容 {#backward-compatibility}

旧版任务可能使用单独的 `skill` 字段而非 `skills` 数组。调度器在加载时会自动规范化——将单个 `skill` 提升为 `skills: [skill]`。

## 调度器运行时 {#scheduler-runtime}

### 滴答周期 {#tick-cycle}

调度器以周期性滴答运行（默认每 60 秒）：

```text
tick()
  1. 获取调度器锁（防止滴答重叠）
  2. 从 jobs.json 加载所有任务
  3. 筛选到期任务（next_run <= now 且 state == "scheduled"）
  4. 对每个到期任务：
     a. 将状态设为 "running"
     b. 创建全新的 AIAgent 会话（无对话历史）
     c. 按顺序加载附加的 Skill（作为用户消息注入）
     d. 通过 Agent 运行任务提示词
     e. 将响应投递到配置的目标
     f. 更新 run_count，计算 next_run
     g. 若重复次数耗尽 → state = "completed"
     h. 否则 → state = "scheduled"
  5. 将更新后的任务写回 jobs.json
  6. 释放调度器锁
```

### Gateway 集成 {#gateway-integration}

在 Gateway 模式下，调度器滴答被集成到 Gateway 的主事件循环中。Gateway 在其周期性维护周期中调用 `scheduler.tick()`，与消息处理并行运行。

在 CLI 模式下，Cron 任务仅在运行 `hermes cron` 命令或处于活跃的 CLI 会话期间才会触发。

### 全新会话隔离 {#fresh-session-isolation}

每个 Cron 任务都在完全全新的 Agent 会话中运行：

- 不保留之前运行的对话历史
- 不保留之前 Cron 执行的记忆（除非已持久化到记忆/文件中）
- 提示词必须自包含——Cron 任务无法提出澄清问题
- `cronjob` 工具集被禁用（防止递归）

## Skill 驱动任务 {#skill-backed-jobs}

Cron 任务可以通过 `skills` 字段附加一个或多个 Skill。在执行时：
1. Skills 按指定顺序加载
2. 每个 skill 的 SKILL.md 内容作为上下文注入
3. 任务的 prompt 追加为任务指令
4. Agent 处理合并后的 skill 上下文 + prompt

这样无需把完整指令粘贴到 cron prompt 中，就能实现可复用、可测试的工作流。例如：

```
Create a daily funding report → attach "ai-funding-daily-report" skill
```

### Script-Backed Jobs {#script-backed-jobs}

任务也可以通过 `script` 字段附加 Python 脚本。脚本在每次 Agent 轮次之前运行，其 stdout 作为上下文注入 prompt。这支持数据收集和变更检测模式：

```python
# ~/.hermes/scripts/check_competitors.py
import requests, json
# Fetch competitor release notes, diff against last run
# Print summary to stdout — agent analyzes and reports
```

脚本超时默认为 120 秒。`_get_script_timeout()` 通过三层链路解析限制：

1. **模块级覆盖** — `_SCRIPT_TIMEOUT`（用于测试/ monkeypatching）。仅在与默认值不同时使用。
2. **环境变量** — `HERMES_CRON_SCRIPT_TIMEOUT`
3. **配置** — `config.yaml` 中的 `cron.script_timeout_seconds`（通过 `load_config()` 读取）
4. **默认值** — 120 秒

### Provider Recovery {#provider-recovery}

`run_job()` 将用户配置的 fallback providers 和 credential pool 传入 `AIAgent` 实例：

- **Fallback providers** — 从 `config.yaml` 读取 `fallback_providers`（列表）或 `fallback_model`（旧版字典），匹配 gateway 的 `_load_fallback_model()` 模式。作为 `fallback_model=` 传给 `AIAgent.__init__`，将两种格式统一归一化为 fallback 链。
- **Credential pool** — 通过 `agent.credential_pool` 的 `load_pool(provider)` 加载，使用解析后的运行时 provider 名称。仅在 pool 有凭证时传入（`pool.has_credentials()`）。在 429/限流错误时实现同 provider 的 key 轮换。

这与 gateway 的行为一致 —— 没有它，cron Agent 会在限流时直接失败，不会尝试恢复。

## Delivery Model {#delivery-model}

Cron 任务结果可以投递到任意支持的平台：

| Target | Syntax | Example |
|--------|--------|---------|
| Origin chat | `origin` | 投递到创建任务的聊天 |
| Local file | `local` | 保存到 `~/.hermes/cron/output/` |
| Telegram | `telegram` 或 `telegram:&lt;chat_id&gt;` | `telegram:-1001234567890` |
| Discord | `discord` 或 `discord:#channel` | `discord:#engineering` |
| Slack | `slack` | 投递到 Slack 主频道 |
| WhatsApp | `whatsapp` | 投递到 WhatsApp 主频道 |
| Signal | `signal` | 投递到 Signal |
| Matrix | `matrix` | 投递到 Matrix 主房间 |
| Mattermost | `mattermost` | 投递到 Mattermost 主频道 |
| Email | `email` | 通过邮件投递 |
| SMS | `sms` | 通过短信投递 |
| Home Assistant | `homeassistant` | 投递到 HA 对话 |
| DingTalk | `dingtalk` | 投递到钉钉 |
| Feishu | `feishu` | 投递到飞书 |
| WeCom | `wecom` | 投递到企业微信 |
| Weixin | `weixin` | 投递到微信 |
| BlueBubbles | `bluebubbles` | 通过 BlueBubbles 投递到 iMessage |
| QQ Bot | `qqbot` | 通过官方 API v2 投递到 QQ |

Telegram 话题使用格式 `telegram:&lt;chat_id&gt;:&lt;thread_id&gt;`（例如 `telegram:-1001234567890:17585`）。

### Response Wrapping {#response-wrapping}

默认情况下（`cron.wrap_response: true`），cron 投递会包装：
- 头部标识 cron 任务名称和任务内容
- 尾部注明 Agent 在对话中看不到已投递的消息

cron 响应中的 `[SILENT]` 前缀会完全抑制投递 —— 适用于只需要写入文件或执行副作用的任务。

### Session Isolation {#session-isolation}

Cron 投递不会镜像到 gateway 会话的对话历史中。它们只存在于 cron 任务自己的会话中。这避免了目标聊天对话中的消息交替违规。

## Recursion Guard {#recursion-guard}

Cron 运行的会话禁用了 `cronjob` 工具集。这防止了：
- 定时任务创建新的 cron 任务
- 递归调度导致 token 使用量爆炸
- 任务内部意外修改任务调度
## 锁机制 {#locking}

调度器使用基于文件的锁来防止重叠的 tick 重复执行同一批到期任务。这在网关模式下尤为重要，因为如果前一次 tick 的执行时间超过了 tick 间隔，多个维护周期可能会发生重叠。

## CLI 接口 {#cli-interface}

`hermes cron` CLI 提供了直接的作业管理功能：

```bash
hermes cron list                    # 显示所有作业
hermes cron create                  # 交互式创建作业（别名：add）
hermes cron edit <job_id>           # 编辑作业配置
hermes cron pause <job_id>          # 暂停运行中的作业
hermes cron resume <job_id>         # 恢复已暂停的作业
hermes cron run <job_id>            # 立即触发执行
hermes cron remove <job_id>         # 删除作业
```

## 相关文档 {#related-docs}

- [Cron 功能指南](/user-guide/features/cron)
- [网关内部机制](./gateway-internals.md)
- [Agent Loop 内部机制](./agent-loop.md)
