---
title: "Teams 会议流水线"
sidebar_label: "Teams 会议流水线"
description: "通过 Hermes CLI 操作 Teams 会议摘要流水线——总结会议、检查流水线状态、重放任务、管理 Microsoft Graph 订阅"
---

{/* 此页面由 skills/SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="teams-meeting-pipeline"></a>
# Teams 会议流水线

通过 Hermes CLI 操作 Teams 会议摘要流水线——总结会议、检查流水线状态、重放任务、管理 Microsoft Graph 订阅。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/teams-meeting-pipeline` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 标签 | `Teams`， `Microsoft Graph`， `Meetings`， `Productivity`， `Operations` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Teams 会议流水线

当用户询问有关 Microsoft Teams 会议摘要、转录、录制、行动项、Graph 订阅或任何关于 Teams 会议流水线的操作问题时，使用此技能。适用于任何语言——以下触发词仅为示例，并非完整列表。

所有面向操作者的内容都是通过终端工具运行的 `hermes teams-pipeline` 子命令。此流水线没有新的模型工具——CLI 就是交互界面。

<a id="when-to-use-this-skill"></a>
## 何时使用此技能

用户正在要求：
- 总结 Teams 会议 / 提取行动项 / 获取会议笔记
- 检查流水线状态，查看已存储的会议任务，或查看最近的会议
- 重放 / 重新运行已失败或需要新摘要的存储任务
- 在更改环境或配置后验证 Microsoft Graph 设置
- 排查“会议摘要未到达”或“没有新会议被摄入”的问题
- 管理 Graph webhook 订阅（创建、续订、删除、检查）
- 设置自动订阅续订（参见下方的陷阱）

多语言触发词示例（非完整列表）：
- 英语: "summarize the Teams meeting", "pipeline status", "replay job X"
- 土耳其语: "Teams meeting özetle", "action item çıkar", "toplantı notu", "pipeline durumu", "replay job"

<a id="prerequisites"></a>
## 先决条件

在使用流水线之前，请确保在 `~/.hermes/.env` 中设置了以下内容：

```bash
MSGRAPH_TENANT_ID=...
MSGRAPH_CLIENT_ID=...
MSGRAPH_CLIENT_SECRET=...
```

如果缺少任何一项，请引导用户参考位于 `/docs/guides/microsoft-graph-app-registration` 的 Azure 应用注册指南——他们需要一个具有管理员同意的 Graph 应用程序权限的 Azure AD 应用注册，流水线才能正常工作。

<a id="command-reference"></a>
## 命令参考

<a id="status-and-inspection-start-here"></a>
### 状态与检查（从这里开始）

```bash
hermes teams-pipeline validate              # 配置快照——每次变更后先运行此命令
hermes teams-pipeline token-health          # Graph 令牌状态
hermes teams-pipeline token-health --force-refresh   # 强制获取新令牌
hermes teams-pipeline list                  # 最近的会议任务
hermes teams-pipeline list --status failed  # 仅显示失败的任务
hermes teams-pipeline show <job-id>         # 单个任务的详细信息
hermes teams-pipeline subscriptions         # 当前的 Graph webhook 订阅
```
<a id="re-running-debugging"></a>
### 重新运行 / 调试

```bash
hermes teams-pipeline run <job-id>          # 重放已存储的任务（重新总结、重新投递）
hermes teams-pipeline fetch --meeting-id <id>   # 试运行：解析会议 + 转录但不持久化
hermes teams-pipeline fetch --join-web-url "<url>"   # 通过加入链接试运行
```

<a id="subscription-management"></a>
### 订阅管理

```bash
hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllTranscripts \
  --notification-url https://<your-public-host>/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"

hermes teams-pipeline renew-subscription <sub-id> --expiration <iso-8601>
hermes teams-pipeline delete-subscription <sub-id>
hermes teams-pipeline maintain-subscriptions            # 续订即将过期的订阅
hermes teams-pipeline maintain-subscriptions --dry-run  # 显示将被续订的内容
```

<a id="decision-tree-for-common-asks"></a>
## 常见问题的决策树

- 用户问“为什么我没有收到今天会议的摘要？” → 从 `list --status failed` 开始，然后在相关行上 `show &lt;job-id&gt;`。如果该任务根本不存在，检查 `subscriptions` —— webhook 可能已经过期（见下面的陷阱）。
- 用户问“配置是否正常工作？” → `validate`，然后 `token-health`，然后 `subscriptions`。如果全部通过，请求一个测试会议并检查 `list` 中是否有新的行。
- 用户问“重新运行会议 X 的摘要” → 用 `list` 找到任务 ID，用 `run &lt;job-id&gt;` 重放。如果再次失败，用 `show &lt;job-id&gt;` 检查错误，用 `fetch --meeting-id` 试运行解析制品。
- 用户问“将会议 X 添加到管线” → 通常不需要 —— 管线是基于订阅驱动的，不是按会议驱动的。如果用户想对某个过去的会议生成摘要，使用 `fetch` 拉取转录，然后在任务创建后使用 `run`。

<a id="critical-pitfall-graph-subscriptions-expire-in-72-hours"></a>
## 关键陷阱：Graph 订阅在 72 小时后过期

Microsoft Graph 将 webhook 订阅上限设为 72 小时，并且**不会自动续订**。如果没有安排 `maintain-subscriptions`，会议通知会在手动创建订阅后 3 天静默停止到达。

当用户报告“管线昨天还能工作，但今天什么也没到”时：
1. 运行 `hermes teams-pipeline subscriptions` —— 如果列表为空或所有条目的 `expirationDateTime` 都显示为过去时间，那就是原因。
2. 像上面展示的那样用 `subscribe` 重新创建。
3. **立即通过 `hermes cron add`、systemd 定时器或普通 crontab 设置自动续订**。操作员手册在 `/docs/guides/operate-teams-meeting-pipeline#automating-subscription-renewal-required-for-production` 中提供了所有三种选项。12 小时间隔是安全的（相对于 72 小时限制有 6 倍的余量）。

<a id="other-pitfalls"></a>
## 其他陷阱

- **转录尚未可用。** 会议结束后，Teams 需要一些时间来生成转录制品。对刚结束的会议执行 `fetch --meeting-id` 可能会返回空结果。等待 2-5 分钟后再试，或者让 Graph webhook 自然驱动数据摄取。
- **投递模式不匹配。** 如果摘要已生成（`list` 显示成功）但内容未出现在 Teams 中，请检查 `platforms.teams.extra.delivery_mode` 以及对应的目标配置（`incoming_webhook_url` 或 `chat_id` 或 `team_id`+`channel_id`）。写入器从 `config.yaml` 或 `TEAMS_*` 环境变量读取这些值。
- **Graph 应用权限。** 令牌正常获取（`token-health` 通过）但 Graph API 调用返回 401/403，原因是权限已添加但管理员同意未重新授予。请用户回到 Azure 门户中的应用注册，再次点击“Grant admin consent”。
<a id="related-docs"></a>
## 相关文档

当用户需要比此技能更深入的内容时，可引导他们参阅以下文档：
- Azure 应用注册指南：`/docs/guides/microsoft-graph-app-registration`
- 完整流水线设置：`/docs/user-guide/messaging/teams-meetings`
- 运维手册（续期自动化、故障排查、上线检查清单）：`/docs/guides/operate-teams-meeting-pipeline`
- Webhook 侦听器设置：`/docs/user-guide/messaging/msgraph-webhook`
