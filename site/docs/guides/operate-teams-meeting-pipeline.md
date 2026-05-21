---
title: "运营 Teams 会议管道"
description: "Microsoft Teams 会议管道的 Runbook、上线检查清单和运维人员工作表"
---

<a id="operate-the-teams-meeting-pipeline"></a>
# 运营 Teams 会议管道

在已从 [Teams Meetings](/user-guide/messaging/teams-meetings) 启用该功能后，请使用本指南。

本页涵盖：
- 操作员 CLI 流程
- 常规订阅维护
- 故障排查
- 上线检查
- 推出工作表

<a id="core-operator-commands"></a>
## 核心操作员命令

<a id="validate-the-config-snapshot"></a>
### 验证配置快照

```bash
hermes teams-pipeline validate
```

在任何配置更改后首先使用此命令。

<a id="inspect-token-health"></a>
### 检查令牌健康状态

```bash
hermes teams-pipeline token-health
hermes teams-pipeline token-health --force-refresh
```

当你怀疑认证状态过时时，请使用 `--force-refresh`。

<a id="inspect-subscriptions"></a>
### 检查订阅

```bash
hermes teams-pipeline subscriptions
```

<a id="renew-near-expiry-subscriptions"></a>
### 续约为期将至的订阅

```bash
hermes teams-pipeline maintain-subscriptions
hermes teams-pipeline maintain-subscriptions --dry-run
```

<a id="automating-subscription-renewal-required-for-production"></a>
### 自动化订阅续期（生产环境必需）

**Microsoft Graph 订阅最长在 72 小时内过期。** 如果没有续期操作，会议通知会在 3 天后静默停止，管道会显示为“损坏”。这是基于 Graph 的集成最常见的运维故障模式。

你必须按计划运行 `maintain-subscriptions`。从以下三个选项中选择一个：

<a id="option-1-hermes-cron-recommended-if-you-already-run-the-hermes-gateway"></a>
#### 选项 1：Hermes cron（如果你已经在运行 Hermes 网关，推荐使用）

Hermes 内置了 cron 调度器。`--no-agent` 模式将脚本作为作业运行（而不使用 LLM），并且 `--script` 必须指向 `~/.hermes/scripts/` 下的文件。首先创建脚本：

```bash
mkdir -p ~/.hermes/scripts
cat > ~/.hermes/scripts/maintain-teams-subscriptions.sh <<'EOF'
#!/usr/bin/env bash
exec hermes teams-pipeline maintain-subscriptions
EOF
chmod +x ~/.hermes/scripts/maintain-teams-subscriptions.sh
```

然后注册一个纯脚本的 cron 作业，每 12 小时运行一次（为 72 小时过期窗口留出 6 倍的缓冲时间）：

```bash
hermes cron create "0 */12 * * *" \
  --name "teams-pipeline-maintain-subscriptions" \
  --no-agent \
  --script maintain-teams-subscriptions.sh \
  --deliver local
```

验证注册情况并检查下次运行时间：

```bash
hermes cron list
hermes cron status        # 调度器状态
```

<a id="option-2-systemd-timer-recommended-for-linux-production-deployments"></a>
#### 选项 2：systemd 定时器（推荐用于 Linux 生产环境部署）

创建 `/etc/systemd/system/hermes-teams-pipeline-maintain.service`：

```ini
[Unit]
Description=Hermes Teams 管道订阅维护
After=network-online.target

[Service]
Type=oneshot
User=hermes
EnvironmentFile=/etc/hermes/env
ExecStart=/usr/local/bin/hermes teams-pipeline maintain-subscriptions
```

以及 `/etc/systemd/system/hermes-teams-pipeline-maintain.timer`：

```ini
[Unit]
Description=每 12 小时运行 Hermes Teams 管道订阅维护

[Timer]
OnBootSec=5min
OnUnitActiveSec=12h
Persistent=true

[Install]
WantedBy=timers.target
```

启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-teams-pipeline-maintain.timer
systemctl list-timers hermes-teams-pipeline-maintain.timer
```
<a id="option-3-plain-crontab"></a>
#### 选项 3：纯 crontab

```cron
0 */12 * * * /usr/local/bin/hermes teams-pipeline maintain-subscriptions >> /var/log/hermes/teams-pipeline-maintain.log 2>&1
```

确保 cron 环境包含 `MSGRAPH_*` 凭据。最简单的修复方法：在 crontab 调用的包装脚本顶部 source `~/.hermes/.env`。

<a id="verifying-renewal-is-working"></a>
#### 验证续订是否生效

设置好计划后，在第一次计划运行后检查续订活动：

```bash
hermes teams-pipeline subscriptions   # 应显示 expirationDateTime 已更新
hermes teams-pipeline maintain-subscriptions --dry-run   # 大多数情况下应显示 "0 expiring soon"
```

如果你发现 Graph webhook 在大约 72 小时后神秘地“停止工作”，首先要检查的是：续订任务是否真的运行了？

<a id="inspect-recent-jobs"></a>
### 检查最近的任务

```bash
hermes teams-pipeline list
hermes teams-pipeline list --status failed
hermes teams-pipeline show <job-id>
```

<a id="replay-a-stored-job"></a>
### 重放已存储的任务

```bash
hermes teams-pipeline run <job-id>
```

<a id="dry-run-meeting-artifact-fetches"></a>
### 模拟获取会议制品

```bash
hermes teams-pipeline fetch --meeting-id <meeting-id>
hermes teams-pipeline fetch --join-web-url "<join-url>"
```

<a id="routine-runbook"></a>
## 日常操作手册

<a id="after-first-setup"></a>
### 首次设置后

按顺序运行以下命令：

```bash
hermes teams-pipeline validate
hermes teams-pipeline token-health --force-refresh
hermes teams-pipeline subscriptions
```

然后触发或等待一个真实的会议事件，并确认：

```bash
hermes teams-pipeline list
hermes teams-pipeline show <job-id>
```

<a id="daily-or-periodic-checks"></a>
### 每日或定期检查

- 运行 `hermes teams-pipeline maintain-subscriptions --dry-run`
- 检查 `hermes teams-pipeline list --status failed`
- 验证 Teams 投递目标仍然是正确的聊天或频道

<a id="before-changing-webhook-urls-or-delivery-targets"></a>
### 更改 webhook URL 或投递目标前

- 更新公共通知 URL 或 Teams 目标配置
- 运行 `hermes teams-pipeline validate`
- 续订或重新创建受影响的订阅
- 确认新事件到达预期的接收端

<a id="failure-triage"></a>
## 故障排查

<a id="no-jobs-are-being-created"></a>
### 没有任务被创建

检查：
- `msgraph_webhook` 是否已启用
- 公共通知 URL 是否指向 `/msgraph/webhook`
- 订阅中的客户端状态是否与 `MSGRAPH_WEBHOOK_CLIENT_STATE` 匹配
- 订阅在远程端是否仍然存在且未过期

<a id="jobs-stay-in-retry-or-fail-before-summarization"></a>
### 任务停留在重试状态或在汇总前失败

检查：
- 转录权限和可用性
- 录制权限和制品可用性
- 如果启用了录制回退，检查 `ffmpeg` 是否可用
- Graph 令牌健康状态

<a id="summaries-are-produced-but-not-delivered-to-teams"></a>
### 摘要已生成但未投递到 Teams

检查：
- `platforms.teams.enabled: true`
- `delivery_mode`
- webhook 模式下的 `incoming_webhook_url`
- Graph 模式下的 `chat_id` 或 `team_id` 加 `channel_id`
- 如果使用 Graph 发布，检查 Teams 认证配置

<a id="duplicate-or-unexpected-replays"></a>
### 重复或意外的重放

检查：
- 是否使用 `hermes teams-pipeline run` 手动重放了任务
- 该会议的接收端记录是否已存在
- 是否在本地配置中故意启用了重新发送路径

<a id="go-live-checklist"></a>
## 上线检查清单
- [ ] Graph 凭据存在且正确
- [ ] `msgraph_webhook` 已启用且可从公网访问
- [ ] `MSGRAPH_WEBHOOK_CLIENT_STATE` 已设置并与订阅匹配
- [ ] 转录订阅已创建
- [ ] 如果需要使用 STT 回退，则录制订阅已创建
- [ ] 如果启用了录制回退，则 `ffmpeg` 已安装
- [ ] Teams 出站交付目标已配置并验证
- [ ] Notion 和 Linear 接收器仅在实际需要时配置
- [ ] `hermes teams-pipeline validate` 返回 OK 快照
- [ ] `hermes teams-pipeline token-health --force-refresh` 执行成功
- [ ] **`maintain-subscriptions` 已调度**（Hermes 定时任务、systemd 定时器或 crontab —— 请参见[自动化订阅续订](#automating-subscription-renewal-required-for-production)）。否则，Graph 订阅会在 72 小时内静默过期。
- [ ] 一次真实的端到端会议事件已产生存储的任务
- [ ] 至少一份摘要已到达预期的交付接收器

<a id="delivery-mode-decision-guide"></a>
## 交付模式决策指南

| 模式 | 使用时机 | 权衡 |
|------|----------|------|
| `incoming_webhook` | 只需简单投递到 Teams 时 | 设置最简单，控制力较低 |
| `graph` | 需要通过 Graph 进行频道或聊天投递时 | 控制力更强，需要更多身份认证和目标配置 |

<a id="operator-worksheet"></a>
## 操作员工作表

在部署前填写此表：

| 项目 | 值 |
|------|-------|
| 公共通知 URL | |
| Graph 租户 ID | |
| Graph 客户端 ID | |
| Webhook 客户端状态 | |
| 转录资源订阅 | |
| 录制资源订阅 | |
| Teams 交付模式 | |
| Teams 聊天 ID 或团队/频道 | |
| Notion 数据库 ID | |
| Linear 团队 ID | |
| 存储路径覆盖（如有） | |
| 每日检查负责人 | |

<a id="change-review-worksheet"></a>
## 变更审查工作表

在变更部署前使用此表：

| 问题 | 答案 |
|----------|--------|
| 我们是否要更改公共 Webhook URL？ | |
| 我们是否要轮换 Graph 凭据？ | |
| 我们是否要更改 Teams 交付模式？ | |
| 我们是否要迁移到新的 Teams 聊天或频道？ | |
| 订阅是否需要重新创建或续订？ | |
| 是否需要一次全新的端到端验证运行？ | |

<a id="related-docs"></a>
## 相关文档

- [Teams 会议设置](/user-guide/messaging/teams-meetings)
- [Microsoft Teams 机器人设置](/user-guide/messaging/teams)
