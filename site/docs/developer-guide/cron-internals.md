---
sidebar_position: 11
title: "Cron 内部机制"
description: "Hermes 如何存储、调度、编辑、暂停、加载技能以及交付 cron 任务"
---

# Cron 内部机制

Cron 子系统提供定时任务执行功能——从简单的单次延迟任务到带有技能注入和跨平台交付的循环 cron 表达式任务。

## 关键文件

| 文件 | 用途 |
|------|---------|
| `cron/jobs.py` | 任务模型、存储、对 `jobs.json` 的原子读写 |
| `cron/scheduler.py` | 调度器循环——检测到期任务、执行、重复跟踪 |
| `tools/cronjob_tools.py` | 面向模型的 `cronjob` 工具注册与处理器 |
| `gateway/run.py` | 网关集成——在长驻循环中进行 cron 计时 |
| `hermes_cli/cron.py` | CLI `hermes cron` 子命令 |

## 调度模型

支持四种调度格式：

| 格式 | 示例 | 行为 |
|--------|---------|----------|
| **相对延迟** | `30m`, `2h`, `1d` | 单次执行，在指定时长后触发 |
| **间隔** | `every 2h`, `every 30m` | 循环执行，按固定间隔触发 |
| **Cron 表达式** | `0 9 * * *` | 标准 5 字段 cron 语法（分、时、日、月、周） |
| **ISO 时间戳** | `2025-01-15T09:00:00` | 单次执行，在指定时间点触发 |

面向模型的交互界面是一个单一的 `cronjob` 工具，支持以下操作：`create`、`list`、`update`、`pause`、`resume`、`run`、`remove`。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 中，并采用原子写入语义（写入临时文件，然后重命名）。每个任务记录包含：

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
| `scheduled` | 已激活，将在下次预定时间触发 |
| `paused` | 已挂起——除非恢复，否则不会触发 |
| `completed` | 重复次数已用尽或单次任务已执行完毕 |
| `running` | 当前正在执行（瞬态） |

### 向后兼容性

旧任务可能只有一个 `skill` 字段，而不是 `skills` 数组。调度器会在加载时进行标准化处理——单个 `skill` 会被提升为 `skills: [skill]`。

## 调度器运行时

### 计时周期

调度器按周期性计时运行（默认：每 60 秒一次）：

```text
tick()
  1. 获取调度器锁（防止计时重叠）
  2. 从 jobs.json 加载所有任务
  3. 筛选到期任务（next_run <= 当前时间 且 状态 == "scheduled"）
  4. 对每个到期任务：
     a. 将状态设置为 "running"
     b. 创建全新的 AIAgent 会话（无对话历史）
     c. 按顺序加载附加技能（作为用户消息注入）
     d. 通过 Agent 运行任务提示词
     e. 将响应交付到配置的目标
     f. 更新 run_count，计算 next_run
     g. 如果重复次数用尽 → 状态 = "completed"
     h. 否则 → 状态 = "scheduled"
  5. 将更新后的任务写回 jobs.json
  6. 释放调度器锁
```

### 网关集成

在网关模式下，调度器计时集成在网关的主事件循环中。网关在其周期性维护周期内调用 `scheduler.tick()`，该过程与消息处理并行运行。

在 CLI 模式下，cron 任务仅在运行 `hermes cron` 命令或处于活跃 CLI 会话期间触发。

### 全新会话隔离

每个 cron 任务都在一个全新的 Agent 会话中运行：

- 没有之前的对话历史
- 没有之前 cron 执行的记忆（除非持久化到内存/文件）
- 提示词必须是自包含的——cron 任务无法提出澄清问题
- `cronjob` 工具集被禁用（递归防护）

## 技能支持的任务

Cron 任务可以通过 `skills` 字段附加一个或多个技能。在执行时：

1. 技能按指定顺序加载
2. 每个技能的 `SKILL.md` 内容作为上下文注入
3. 任务的提示词作为任务指令附加在后面
4. Agent 处理组合后的技能上下文 + 提示词

这使得无需将完整指令粘贴到 cron 提示词中即可实现可复用、经过测试的工作流。例如：

```
创建每日融资报告 → 附加 "ai-funding-daily-report" 技能
```

### 脚本支持的任务

任务还可以通过 `script` 字段附加 Python 脚本。脚本在每次 Agent 轮次*之前*运行，其标准输出（stdout）会被注入到提示词中作为上下文。这支持数据收集和变更检测模式：

```python
# ~/.hermes/scripts/check_competitors.py
import requests, json
# 获取竞争对手发布说明，与上次运行进行对比
# 将摘要打印到 stdout — Agent 进行分析并报告
```

脚本超时默认值为 120 秒。`_get_script_timeout()` 通过三层链条解析限制：

1. **模块级覆盖** — `_SCRIPT_TIMEOUT`（用于测试/猴子补丁）。仅在与默认值不同时使用。
2. **环境变量** — `HERMES_CRON_SCRIPT_TIMEOUT`
3. **配置** — `config.yaml` 中的 `cron.script_timeout_seconds`（通过 `load_config()` 读取）
4. **默认值** — 120 秒

### 提供商恢复

`run_job()` 将用户配置的后备提供商和凭据池传入 `AIAgent` 实例：

- **后备提供商** — 从 `config.yaml` 读取 `fallback_providers`（列表）或 `fallback_model`（旧版字典），匹配网关的 `_load_fallback_model()` 模式。作为 `fallback_model=` 传递给 `AIAgent.__init__`，后者将两种格式标准化为后备链。
- **凭据池** — 使用解析后的运行时提供商名称，通过 `agent.credential_pool` 中的 `load_pool(provider)` 加载。仅在池拥有凭据时传递（`pool.has_credentials()`）。支持在遇到 429/速率限制错误时进行同提供商的密钥轮换。

这反映了网关的行为——如果没有它，cron Agent 在遇到速率限制时会失败，而不会尝试恢复。

## 交付模型

Cron 任务结果可以交付到任何支持的平台：

| 目标 | 语法 | 示例 |
|--------|--------|---------|
| 原始聊天 | `origin` | 交付到创建任务的聊天中 |
| 本地文件 | `local` | 保存到 `~/.hermes/cron/output/` |
| Telegram | `telegram` 或 `telegram:<chat_id>` | `telegram:-1001234567890` |
| Discord | `discord` 或 `discord:#channel` | `discord:#engineering` |
| Slack | `slack` | 交付到 Slack 主频道 |
| WhatsApp | `whatsapp` | 交付到 WhatsApp 主页 |
| Signal | `signal` | 交付到 Signal |
| Matrix | `matrix` | 交付到 Matrix 主房间 |
| Mattermost | `mattermost` | 交付到 Mattermost 主页 |
| 电子邮件 | `email` | 通过电子邮件交付 |
| 短信 | `sms` | 通过短信交付 |
| Home Assistant | `homeassistant` | 交付到 HA 对话 |
| 钉钉 | `dingtalk` | 交付到钉钉 |
| 飞书 | `feishu` | 交付到飞书 |
| 企业微信 | `wecom` | 交付到企业微信 |
| 微信 | `weixin` | 交付到微信 |
| BlueBubbles | `bluebubbles` | 通过 BlueBubbles 交付到 iMessage |

对于 Telegram 主题，请使用格式 `telegram:<chat_id>:<thread_id>`（例如 `telegram:-1001234567890:17585`）。

### 响应包装

默认情况下（`cron.wrap_response: true`），cron 交付内容会包含：
- 一个标识 cron 任务名称和任务内容的页眉
- 一个注明 Agent 无法在对话中看到已交付消息的页脚

Cron 响应中的 `[SILENT]` 前缀会完全抑制交付——适用于仅需写入文件或执行副作用的任务。

### 会话隔离

Cron 交付内容不会被镜像到网关会话的对话历史中。它们仅存在于 cron 任务自己的会话中。这防止了目标聊天对话中的消息交替违规。

## 递归防护

Cron 运行的会话禁用了 `cronjob` 工具集。这防止了：
- 预定任务创建新的 cron 任务
- 可能导致 Token 使用量爆炸的递归调度
- 在任务内部意外修改任务调度

## 锁定

调度器使用基于文件的锁定来防止重叠的计时周期两次执行同一个到期任务批次。这在网关模式下非常重要，因为如果上一个计时周期耗时超过了计时间隔，多个维护周期可能会重叠。
## CLI 接口

`hermes cron` CLI 提供了直接的任务管理功能：

```bash
hermes cron list                    # 列出所有任务
hermes cron create                  # 交互式创建任务（别名：add）
hermes cron edit <job_id>           # 编辑任务配置
hermes cron pause <job_id>          # 暂停正在运行的任务
hermes cron resume <job_id>         # 恢复已暂停的任务
hermes cron run <job_id>            # 立即触发执行
hermes cron remove <job_id>         # 删除任务
```

## 相关文档

- [Cron 功能指南](/user-guide/features/cron)
- [Gateway 内部原理](./gateway-internals.md)
- [Agent Loop 内部原理](./agent-loop.md)
