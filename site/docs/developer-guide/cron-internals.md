---
sidebar_position: 11
title: "Cron 内部机制"
description: "Hermes 如何存储、调度、编辑、暂停、加载技能以及投递 cron 任务"
---

# Cron 内部机制 {#cron-internals}

cron 子系统提供定时任务执行——从简单的单次延迟到带有技能注入和跨平台投递的重复 cron 表达式任务。

## 关键文件 {#key-files}

| 文件 | 用途 |
|------|------|
| `cron/jobs.py` | 任务模型、存储、对 `jobs.json` 的原子读写 |
| `cron/scheduler.py` | 调度器循环——到期任务检测、执行、重复跟踪 |
| `tools/cronjob_tools.py` | 面向模型的 `cronjob` 工具注册与处理器 |
| `gateway/run.py` | 网关集成——在长运行循环中执行 cron 滴答 |
| `hermes_cli/cron.py` | CLI `hermes cron` 子命令 |

## 调度模型 {#scheduling-model}

支持四种调度格式：

| 格式 | 示例 | 行为 |
|--------|---------|----------|
| **相对延迟** | `30m`, `2h`, `1d` | 单次，在指定时长后触发 |
| **间隔** | `every 2h`, `every 30m` | 重复，按固定间隔触发 |
| **Cron 表达式** | `0 9 * * *` | 标准 5 字段 cron 语法（分钟、小时、日、月、星期） |
| **ISO 时间戳** | `2025-01-15T09:00:00` | 单次，在精确时间触发 |

面向模型的接口是一个单一的 `cronjob` 工具，支持操作风格的动作：`create`、`list`、`update`、`pause`、`resume`、`run`、`remove`。

## 任务存储 {#job-storage}

任务存储在 `~/.hermes/cron/jobs.json` 中，采用原子写入语义（先写入临时文件，再重命名）。每个任务记录包含：

```json
{
  "id": "a1b2c3d4e5f6",
  "name": "每日简报",
  "prompt": "总结今天的 AI 新闻和融资轮次",
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
| `scheduled` | 活跃，将在下次调度时间触发 |
| `paused` | 暂停——恢复前不会触发 |
| `completed` | 重复次数耗尽，或单次任务已触发 |
| `running` | 正在执行（瞬态状态） |

### 向后兼容 {#backward-compatibility}

旧任务可能使用单个 `skill` 字段而非 `skills` 数组。调度器在加载时会进行归一化——单个 `skill` 会被提升为 `skills: [skill]`。

## 调度器运行时 {#scheduler-runtime}

### 滴答周期 {#tick-cycle}

调度器按固定周期运行（默认：每 60 秒）：

```text
tick()
  1. 获取调度器锁（防止滴答重叠）
  2. 从 jobs.json 加载所有任务
  3. 过滤出到期任务（next_run <= now 且 state == "scheduled"）
  4. 对每个到期任务：
     a. 将状态设为 "running"
     b. 创建新的 AIAgent 会话（无对话历史）
     c. 按顺序加载附加的技能（以用户消息形式注入）
     d. 通过 Agent 运行任务提示词
     e. 将响应投递到配置的目标
     f. 更新运行次数，计算下次运行时间
     g. 如果重复次数耗尽 → 状态设为 "completed"
     h. 否则 → 状态设为 "scheduled"
  5. 将更新后的任务写回 jobs.json
  6. 释放调度器锁
```
### 网关集成 {#gateway-integration}

在网关模式下，调度器运行在一个专用的后台线程中（`gateway/run.py` 中的 `_start_cron_ticker`），该线程在消息处理的同时每 60 秒调用一次 `scheduler.tick()`。

在 CLI 模式下，cron 任务仅在运行 `hermes cron` 命令或处于活跃的 CLI 会话期间触发。

### 全新会话隔离 {#fresh-session-isolation}

每个 cron 任务都在一个全新的 Agent 会话中运行：

- 没有之前运行的对话历史
- 没有之前 cron 执行的记忆（除非持久化到内存/文件）
- 提示必须自包含——cron 任务不能提出澄清性问题
- `cronjob` 工具集被禁用（递归保护）

## 技能支持的任务 {#skill-backed-jobs}

cron 任务可以通过 `skills` 字段附加一个或多个技能。在执行时：

1. 按指定顺序加载技能
2. 每个技能的 SKILL.md 内容作为上下文注入
3. 任务的提示作为任务指令附加
4. Agent 处理组合的技能上下文 + 提示

这使得无需将完整指令粘贴到 cron 提示中即可实现可复用、经过测试的工作流。例如：

```
创建每日资金报告 → 附加 "ai-funding-daily-report" 技能
```

### 脚本支持的任务 {#script-backed-jobs}

任务还可以通过 `script` 字段附加一个 Python 脚本。该脚本在每次 Agent 轮次*之前*运行，其标准输出作为上下文注入到提示中。这支持数据收集和变更检测模式：

```python
# ~/.hermes/scripts/check_competitors.py
import requests, json
# 获取竞争对手发布说明，与上次运行进行差异比较
# 将摘要打印到标准输出——Agent 进行分析和报告
```

脚本超时默认为 120 秒。`_get_script_timeout()` 通过三层链解析限制：

1. **模块级覆盖** — `_SCRIPT_TIMEOUT`（用于测试/猴子补丁）。仅当与默认值不同时使用。
2. **环境变量** — `HERMES_CRON_SCRIPT_TIMEOUT`
3. **配置** — `config.yaml` 中的 `cron.script_timeout_seconds`（通过 `load_config()` 读取）
4. **默认值** — 120 秒

### 提供商恢复 {#provider-recovery}

`run_job()` 将用户配置的回退提供商和凭据池传递给 `AIAgent` 实例：

- **回退提供商** — 从 `config.yaml` 读取 `fallback_providers`（列表）或 `fallback_model`（旧版字典），匹配网关的 `_load_fallback_model()` 模式。作为 `fallback_model=` 传递给 `AIAgent.__init__`，该方法将两种格式规范化为回退链。
- **凭据池** — 通过 `load_pool(provider)` 从 `agent.credential_pool` 加载，使用解析后的运行时提供商名称。仅当池中有凭据时（`pool.has_credentials()`）才传递。支持在 429/速率限制错误时进行同提供商密钥轮换。

这镜像了网关的行为——如果没有它，cron Agent 会在遇到速率限制时失败而不尝试恢复。

## 投递模型 {#delivery-model}

cron 任务的结果可以投递到任何支持的平台：

| 目标 | 语法 | 示例 |
|--------|--------|---------|
| 原始聊天 | `origin` | 投递到创建任务的聊天 |
| 本地文件 | `local` | 保存到 `~/.hermes/cron/output/` |
| Telegram | `telegram` 或 `telegram:&lt;chat_id&gt;` | `telegram:-1001234567890` |
| Discord | `discord` 或 `discord:#channel` | `discord:#engineering` |
| Slack | `slack` | 投递到 Slack 首页频道 |
| WhatsApp | `whatsapp` | 投递到 WhatsApp 首页 |
| Signal | `signal` | 投递到 Signal |
| Matrix | `matrix` | 投递到 Matrix 首页房间 |
| Mattermost | `mattermost` | 投递到 Mattermost 首页 |
| 电子邮件 | `email` | 通过电子邮件投递 |
| 短信 | `sms` | 通过短信投递 |
| Home Assistant | `homeassistant` | 投递到 HA 对话 |
| 钉钉 | `dingtalk` | 投递到钉钉 |
| 飞书 | `feishu` | 投递到飞书 |
| 企业微信 | `wecom` | 投递到企业微信 |
| 微信 | `weixin` | 投递到微信 |
| BlueBubbles | `bluebubbles` | 通过 BlueBubbles 投递到 iMessage |
| QQ 机器人 | `qqbot` | 通过官方 API v2 投递到 QQ |
对于 Telegram 话题，请使用格式 `telegram:&lt;chat_id&gt;:&lt;thread_id&gt;`（例如 `telegram:-1001234567890:17585`）。

### 响应包装 {#response-wrapping}

默认情况下（`cron.wrap_response: true`），cron 投递会附带以下内容：
- 一个头部，标明 cron 任务名称和任务
- 一个尾部，说明 Agent 无法在对话中看到投递的消息

cron 响应中的 `[SILENT]` 前缀会完全抑制投递——适用于只需要写入文件或执行副作用的任务。

### 会话隔离 {#session-isolation}

Cron 投递**不会**镜像到网关会话的对话历史中。它们只存在于 cron 任务自身的会话中。这可以防止目标聊天对话中出现消息交替违规。

## 递归防护 {#recursion-guard}

Cron 运行的会话禁用了 `cronjob` 工具集。这可以防止：
- 定时任务创建新的 cron 任务
- 递归调度导致 token 用量激增
- 任务内部意外修改任务调度

## 锁定 {#locking}

调度器使用基于文件的跨进程锁定（Unix 上为 `fcntl.flock`，Windows 上为 `msvcrt.locking`），以防止重叠的 tick 重复执行同一批到期任务——即使是在网关的进程内 ticker 与独立的 `hermes cron` / 手动 `tick()` 调用之间。如果无法获取锁，`tick()` 会立即返回 0。

## CLI 接口 {#cli-interface}

`hermes cron` CLI 提供直接的任务管理：

```bash
hermes cron list                    # 显示所有任务
hermes cron create                  # 交互式创建任务（别名：add）
hermes cron edit <job_id>           # 编辑任务配置
hermes cron pause <job_id>          # 暂停运行中的任务
hermes cron resume <job_id>         # 恢复暂停的任务
hermes cron run <job_id>            # 立即触发执行
hermes cron remove <job_id>         # 删除任务
```

## 相关文档 {#related-docs}

- [Cron 功能指南](/user-guide/features/cron)
- [网关内部机制](./gateway-internals.md)
- [Agent 循环内部机制](./agent-loop.md)
