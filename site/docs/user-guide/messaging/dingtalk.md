---
sidebar_position: 10
title: "钉钉"
description: "将 Hermes Agent 设置为钉钉聊天机器人"
---

# 钉钉设置

Hermes Agent 可以作为聊天机器人与钉钉集成，让你通过私聊或群聊与你的 AI 助手对话。机器人通过钉钉的 Stream 模式连接——这是一种长连接的 WebSocket 连接，无需公网 URL 或 Webhook 服务器——并通过钉钉的会话 Webhook API 使用 Markdown 格式的消息进行回复。

在开始设置之前，以下是大多数人最想了解的部分：Hermes 进入你的钉钉工作空间后会如何表现。

## Hermes 的行为表现

| 场景 | 行为 |
|---------|----------|
| **私聊 (1对1聊天)** | Hermes 会回复每一条消息。无需 `@提及`。每个私聊都有自己独立的会话。 |
| **群聊** | 当你 `@提及` Hermes 时，它才会回复。如果没有提及，Hermes 会忽略该消息。 |
| **多用户共享的群聊** | 默认情况下，Hermes 会在群内为每个用户隔离会话历史。除非你明确禁用此功能，否则两个人在同一个群里的对话不会共享一个记录。 |

### 钉钉中的会话模型

默认情况下：
- 每个私聊拥有独立的会话
- 共享群聊中的每个用户在该群内拥有自己独立的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

只有当你明确希望整个群组共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

本指南将引导你完成完整的设置过程——从创建钉钉机器人到发送第一条消息。

## 前提条件

安装所需的 Python 包：

```bash
pip install dingtalk-stream httpx
```

- `dingtalk-stream` — 钉钉官方的 Stream 模式 SDK（基于 WebSocket 的实时消息传递）
- `httpx` — 用于通过会话 Webhook 发送回复的异步 HTTP 客户端

## 步骤 1：创建钉钉应用

1.  前往 [钉钉开发者后台](https://open-dev.dingtalk.com/)。
2.  使用你的钉钉管理员账号登录。
3.  点击 **应用开发** → **企业内部开发** → **H5微应用**（或 **机器人**，具体取决于你的控制台版本）→ **创建应用**。
4.  填写：
    - **应用名称**：例如，`Hermes Agent`
    - **应用描述**：可选
5.  创建后，导航到 **凭证与基础信息** 以找到你的 **Client ID** (AppKey) 和 **Client Secret** (AppSecret)。复制两者。

:::warning[凭证仅显示一次]
Client Secret 仅在创建应用时显示一次。如果丢失，你需要重新生成。切勿公开分享这些凭证或将其提交到 Git。
:::

## 步骤 2：启用机器人能力

1.  在你的应用设置页面，进入 **添加能力** → **机器人**。
2.  启用机器人能力。
3.  在 **消息接收模式** 下，选择 **Stream 模式**（推荐——无需公网 URL）。

:::tip
Stream 模式是推荐的设置。它使用从你的机器发起的长期 WebSocket 连接，因此你不需要公网 IP、域名或 Webhook 端点。这可以在 NAT、防火墙后以及本地机器上工作。
:::

## 步骤 3：查找你的钉钉用户 ID

Hermes Agent 使用你的钉钉用户 ID 来控制谁可以与机器人交互。钉钉用户 ID 是由你所在组织的管理员设置的数字字母字符串。

查找你的用户 ID：
1.  询问你的钉钉组织管理员——用户 ID 在钉钉管理后台的 **通讯录** → **成员** 下配置。
2.  或者，机器人会记录每条接收消息的 `sender_id`。启动网关，向机器人发送一条消息，然后在日志中查看你的 ID。

## 步骤 4：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

当提示时选择 **DingTalk**，然后在被要求时粘贴你的 Client ID、Client Secret 和允许的用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
DINGTALK_CLIENT_ID=your-app-key
DINGTALK_CLIENT_SECRET=your-app-secret

# 安全：限制谁可以与机器人交互
DINGTALK_ALLOWED_USERS=user-id-1

# 允许多个用户（逗号分隔）
# DINGTALK_ALLOWED_USERS=user-id-1,user-id-2
```

在 `~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 在共享群聊中保持每个参与者的上下文隔离

### 启动网关

配置完成后，启动钉钉网关：

```bash
hermes gateway
```

机器人应在几秒钟内连接到钉钉的 Stream 模式。发送一条消息——无论是私聊还是它被添加到的群聊——进行测试。

:::tip
你可以在后台或作为 systemd 服务运行 `hermes gateway` 以实现持久运行。详情请参阅部署文档。
:::

## 故障排除

### 机器人不回复消息

**原因**：机器人能力未启用，或者 `DINGTALK_ALLOWED_USERS` 未包含你的用户 ID。

**解决**：验证在你的应用设置中机器人能力已启用，并且选择了 Stream 模式。检查你的用户 ID 是否在 `DINGTALK_ALLOWED_USERS` 中。重启网关。

### "dingtalk-stream not installed" 错误

**原因**：未安装 `dingtalk-stream` Python 包。

**解决**：安装它：

```bash
pip install dingtalk-stream httpx
```

### "DINGTALK_CLIENT_ID and DINGTALK_CLIENT_SECRET required"

**原因**：凭证未在你的环境或 `.env` 文件中设置。

**解决**：验证 `DINGTALK_CLIENT_ID` 和 `DINGTALK_CLIENT_SECRET` 在 `~/.hermes/.env` 中是否正确设置。Client ID 是你的 AppKey，Client Secret 是来自钉钉开发者后台的 AppSecret。

### Stream 断开连接 / 重连循环

**原因**：网络不稳定、钉钉平台维护或凭证问题。

**解决**：适配器会自动以指数退避方式重连（2s → 5s → 10s → 30s → 60s）。检查你的凭证是否有效，以及你的应用是否未被停用。验证你的网络是否允许出站 WebSocket 连接。

### 机器人离线

**原因**：Hermes 网关未运行，或连接失败。

**解决**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误信息。常见问题：错误的凭证、应用被停用、未安装 `dingtalk-stream` 或 `httpx`。

### "No session_webhook available"

**原因**：机器人尝试回复但没有会话 Webhook URL。这通常发生在 Webhook 过期，或者在接收消息和发送回复之间机器人被重启的情况下。

**解决**：向机器人发送一条新消息——每条接收到的消息都会为回复提供一个全新的会话 Webhook。这是钉钉的一个正常限制；机器人只能回复它最近收到的消息。

## 安全

:::warning
务必设置 `DINGTALK_ALLOWED_USERS` 以限制谁可以与机器人交互。如果没有设置，作为安全措施，网关默认会拒绝所有用户。只添加你信任的用户 ID——授权用户可以完全访问代理的能力，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅 [安全指南](../security.md)。

## 注意事项

- **Stream 模式**：无需公网 URL、域名或 Webhook 服务器。连接通过 WebSocket 从你的机器发起，因此可以在 NAT 和防火墙后工作。
- **Markdown 回复**：回复以钉钉的 Markdown 格式进行格式化，以支持富文本显示。
- **消息去重**：适配器使用 5 分钟的时间窗口对消息进行去重，以防止重复处理同一条消息。
- **自动重连**：如果 Stream 连接断开，适配器会自动以指数退避方式重连。
- **消息长度限制**：每条回复的消息长度限制为 20,000 个字符。更长的回复会被截断。
