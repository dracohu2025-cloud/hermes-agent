---
sidebar_position: 6
title: "Teams 会议"
description: "使用 Microsoft Graph Webhook 设置 Microsoft Teams 会议摘要流水线"
---

<a id="microsoft-teams-meetings"></a>
# Microsoft Teams 会议

当你希望 Hermes 接收 Microsoft Graph 会议事件、优先获取会议转录、在必要时回退到录音加语音转文字（STT），并将结构化摘要投递到下游目标时，请使用 Teams 会议流水线。

本页重点介绍设置与启用：
- Graph 凭据
- Webhook 监听器配置
- Teams 投递模式
- 流水线配置结构

关于日常运维、上线检查以及操作员工作表，请参考专门指南：[运营 Teams 会议流水线](/guides/operate-teams-meeting-pipeline)。

<a id="what-this-feature-does"></a>
## 功能说明

该流水线：
1. 接收 Microsoft Graph Webhook 事件
2. 解析会议信息，优先获取转录文件
3. 当没有可用转录时，回退到下载录音并执行语音转文字（STT）
4. 在本地持久化存储任务状态和投递记录
5. 可将摘要写入 Notion、Linear 和 Microsoft Teams

操作员通过 CLI 执行操作（`teams-pipeline` 子命令由 `teams_pipeline` 插件注册——通过 `hermes plugins enable teams_pipeline` 启用，或在 `config.yaml` 中设置 `plugins.enabled: [teams_pipeline]`）：

```bash
hermes teams-pipeline validate
hermes teams-pipeline list
hermes teams-pipeline maintain-subscriptions
```

<a id="prerequisites"></a>
## 前提条件

在启用会议流水线之前，请确保你已具备：

- 一个正常运行的 Hermes 安装
- 已有的 [Microsoft Teams 机器人设置](/user-guide/messaging/teams)（如果你需要 Teams 出站投递）
- 拥有所需权限的 Microsoft Graph 应用程序凭据，用于订阅你计划使用的会议资源
- 一个可供 Microsoft Graph 调用以投递 Webhook 的公共 HTTPS URL
- 已安装 `ffmpeg`（如果你需要录音加语音转文字的回退方案）

<a id="step-1-add-microsoft-graph-credentials"></a>
## 步骤 1：添加 Microsoft Graph 凭据

将 Graph 应用专用凭据添加到 `~/.hermes/.env`：

```bash
MSGRAPH_TENANT_ID=<租户ID>
MSGRAPH_CLIENT_ID=<客户端ID>
MSGRAPH_CLIENT_SECRET=<客户端密钥>
```

这些凭据用于：
- Graph 客户端基础库
- 订阅维护命令
- 会议解析和文件获取
- 基于 Graph 的 Teams 出站投递（当你没有提供专用的 Teams 访问令牌时）

<a id="step-2-enable-the-graph-webhook-listener"></a>
## 步骤 2：启用 Graph Webhook 监听器

Webhook 监听器是一个名为 `msgraph_webhook` 的网关平台。至少需要启用它并设置一个客户端状态值：

```bash
MSGRAPH_WEBHOOK_ENABLED=true
MSGRAPH_WEBHOOK_PORT=8646
MSGRAPH_WEBHOOK_CLIENT_STATE=<随机共享密钥>
MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES=communications/onlineMeetings
```

监听器暴露以下端点：
- `/msgraph/webhook` 用于接收 Graph 通知
- `/health` 用于简单的健康检查

你需要将公共 HTTPS 端点路由到该监听器。例如，如果你的公共域名为 `https://ops.example.com`，那么你的 Graph 通知 URL 通常为：

```text
https://ops.example.com/msgraph/webhook
```

<a id="step-3-configure-teams-delivery-and-pipeline-behavior"></a>
## 步骤 3：配置 Teams 投递与流水线行为

会议流水线从现有的 `teams` 平台条目中读取其运行时配置。流水线专用的配置项位于 `teams.extra.meeting_pipeline` 下。Teams 出站投递则沿用常规的 Teams 平台配置。
示例 `~/.hermes/config.yaml`:

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      port: 8646
      client_state: "replace-me"
      accepted_resources:
        - "communications/onlineMeetings"

  teams:
    enabled: true
    extra:
      client_id: "your-teams-client-id"
      client_secret: "your-teams-client-secret"
      tenant_id: "your-teams-tenant-id"

      # outbound summary delivery
      delivery_mode: "graph" # or incoming_webhook
      team_id: "team-id"
      channel_id: "channel-id"
      # incoming_webhook_url: "https://..."

      meeting_pipeline:
        transcript_min_chars: 80
        transcript_required: false
        transcription_fallback: true
        ffmpeg_extract_audio: true
        notion:
          enabled: false
        linear:
          enabled: false
```

<a id="teams-delivery-modes"></a>
## Teams 交付模式

该管道在现有的 Teams 插件内支持两种 Teams 摘要交付模式。

<a id="incomingwebhook"></a>
### `incoming_webhook`

当你仅希望向 Teams 发送简单的 webhook 消息，而不通过 Graph 创建频道消息时，使用此模式。

必需配置：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      delivery_mode: "incoming_webhook"
      incoming_webhook_url: "https://..."
```

<a id="graph"></a>
### `graph`

当你希望 Hermes 通过 Microsoft Graph 将摘要发布到 Teams 聊天或频道时，使用此模式。

支持的目标：
- `chat_id`
- `team_id` + `channel_id`
- `team_id` + `home_channel` 作为现有 Teams 平台的回退

示例：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      delivery_mode: "graph"
      team_id: "team-id"
      channel_id: "channel-id"
```

<a id="step-4-start-the-gateway"></a>
## 第 4 步：启动网关

更新配置后，正常启动 Hermes：

```bash
hermes gateway run
```

或者，如果你在 Docker 中运行 Hermes，请以与部署相同的方式启动网关。

检查监听器：

```bash
curl http://localhost:8646/health
```

<a id="step-5-create-graph-subscriptions"></a>
## 第 5 步：创建 Graph 订阅

使用插件 CLI 创建和检查订阅。

示例：

```bash
hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllTranscripts \
  --notification-url https://ops.example.com/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"

hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllRecordings \
  --notification-url https://ops.example.com/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"
```

<a id="graph-subscriptions-expire-in-72-hours"></a>
:::warning Graph 订阅在 72 小时后过期

Microsoft Graph 将 webhook 订阅限制为 72 小时，并且不会自动续订。在上线之前，你必须安排 `hermes teams-pipeline maintain-subscriptions`，否则任何手动创建的订阅将在三天后静默停止通知。请参阅操作手册中的[自动化订阅续订](/guides/operate-teams-meeting-pipeline#automating-subscription-renewal-required-for-production)——三个选项（Hermes cron、systemd 定时器、普通 crontab）。

:::

关于订阅维护和后续运营流程，请继续阅读指南：[操作 Teams 会议管道](/guides/operate-teams-meeting-pipeline)。
<a id="validation"></a>
## 验证

运行内置验证快照：

```bash
hermes teams-pipeline validate
```

有用的辅助检查：

```bash
hermes teams-pipeline token-health
hermes teams-pipeline subscriptions
```

<a id="troubleshooting"></a>
## 故障排查

| 问题 | 检查点 |
|---------|---------------|
| Graph webhook 验证失败 | 确认公网 URL 正确且可达，并且 Graph 正在调用正确的 `/msgraph/webhook` 路径 |
| 在 `hermes teams-pipeline list` 中未显示任务 | 确认已启用 `msgraph_webhook`，并且订阅指向正确的通知 URL |
| Transcript-first 始终不成功 | 检查 Graph 对转录资源的权限，以及该会议是否存在转录产物 |
| 录制回退失败 | 确认已安装 `ffmpeg`，并且 Graph 应用能够访问录制产物 |
| Teams 摘要投递失败 | 重新检查 `delivery_mode`、目标 ID 以及 Teams 认证配置 |

<a id="related-docs"></a>
## 相关文档

- [Microsoft Teams 机器人设置](/user-guide/messaging/teams)
- [运营 Teams 会议管道](/guides/operate-teams-meeting-pipeline)
