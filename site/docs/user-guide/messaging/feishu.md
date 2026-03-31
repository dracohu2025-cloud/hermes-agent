---
sidebar_position: 11
title: "飞书 / Lark"
description: "将 Hermes Agent 设置为飞书或 Lark 机器人"
---

# 飞书 / Lark 设置

Hermes Agent 可以作为功能完整的机器人集成到飞书和 Lark 中。连接后，你可以在私聊或群聊中与智能体对话，在家庭聊天中接收定时任务结果，并通过常规网关流程发送文本、图片、音频和文件附件。

该集成支持两种连接模式：

- `websocket` — 推荐使用；Hermes 建立出站连接，你无需提供公共的 webhook 端点。
- `webhook` — 当你希望飞书/Lark 通过 HTTP 将事件推送到你的网关时有用。

## Hermes 的行为方式

| 场景 | 行为 |
|---------|----------|
| 私聊消息 | Hermes 会响应每一条消息。 |
| 群聊 | 当在聊天中提及机器人时，Hermes 会响应。 |
| 共享群聊 | 默认情况下，在共享聊天中，每个用户的会话历史是隔离的。 |

这种共享聊天的行为由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望每个聊天共享一个对话时，才将其设置为 `false`。

## 步骤 1：创建飞书 / Lark 应用

1.  打开飞书或 Lark 开发者控制台：
    - 飞书：[open.feishu.cn](https://open.feishu.cn/)
    - Lark：[open.larksuite.com](https://open.larksuite.com/)
2.  创建一个新应用。
3.  在 **凭证与基础信息** 中，复制 **App ID** 和 **App Secret**。
4.  为应用启用 **机器人** 能力。

:::warning
请妥善保管 App Secret。任何拥有它的人都可以冒充你的应用。
:::

## 步骤 2：选择连接模式

### 推荐：WebSocket 模式

当 Hermes 运行在你的笔记本电脑、工作站或私有服务器上时，使用 WebSocket 模式。无需公共 URL。

```bash
FEISHU_CONNECTION_MODE=websocket
```

### 可选：Webhook 模式

仅当你已经在可访问的 HTTP 端点后运行 Hermes 时，才使用 webhook 模式。

```bash
FEISHU_CONNECTION_MODE=webhook
```

在 webhook 模式下，Hermes 在以下路径提供飞书端点：

```text
/feishu/webhook
```

## 步骤 3：配置 Hermes

### 选项 A：交互式设置

```bash
hermes gateway setup
```

选择 **飞书 / Lark** 并填写提示信息。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret_xxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket

# 可选但强烈推荐
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
FEISHU_HOME_CHANNEL=oc_xxx
```

`FEISHU_DOMAIN` 接受以下值：

- `feishu` 用于飞书（中国）
- `lark` 用于 Lark（国际版）

## 步骤 4：启动网关

```bash
hermes gateway
```

然后从飞书/Lark 向机器人发送消息，以确认连接已激活。

## 家庭聊天

在飞书/Lark 聊天中使用 `/set-home` 命令，将其标记为用于接收定时任务结果和跨平台通知的家庭频道。

你也可以预先配置它：

```bash
FEISHU_HOME_CHANNEL=oc_xxx
```

## 安全性

对于生产环境，请设置一个允许列表：

```bash
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
```

如果你将允许列表留空，任何能接触到该机器人都可能使用它。

## 工具集

飞书 / Lark 使用 `hermes-feishu` 平台预设，其中包含与 Telegram 和其他基于网关的消息平台相同的核心工具集。
