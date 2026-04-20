---
sidebar_position: 10
title: "钉钉"
description: "将 Hermes Agent 设置为钉钉聊天机器人"
---

# 钉钉设置 {#dingtalk-setup}

Hermes Agent 可与钉钉集成，作为一个聊天机器人，让你通过私聊或群聊与你的 AI 助手对话。该机器人通过钉钉的 Stream Mode 连接——这是一种长连接的 WebSocket 连接，无需公网 URL 或 Webhook 服务器——并通过钉钉的会话 Webhook API 使用 Markdown 格式的消息进行回复。

在开始设置之前，这里是你可能最想知道的部分：Hermes 进入你的钉钉工作空间后会如何表现。

## Hermes 的行为表现 {#how-hermes-behaves}

| 场景 | 行为 |
|---------|----------|
| **私聊 (1对1聊天)** | Hermes 会回复每一条消息。无需 `@提及`。每个私聊都有其独立的会话。 |
| **群聊** | 当你 `@提及` Hermes 时，它才会回复。如果没有提及，Hermes 会忽略该消息。 |
| **多用户共享的群组** | 默认情况下，Hermes 会在群组内为每个用户隔离会话历史。除非你明确禁用此功能，否则两个人在同一个群组中的对话不会共享一个记录。 |

### 钉钉中的会话模型 {#session-model-in-dingtalk}

默认情况下：
- 每个私聊拥有独立的会话
- 共享群聊中的每个用户在该群组内拥有自己的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个群组共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

本指南将引导你完成完整的设置过程——从创建钉钉机器人到发送第一条消息。

## 前提条件 {#prerequisites}

安装所需的 Python 包：

```bash
pip install "hermes-agent[dingtalk]"
```

或者单独安装：

```bash
pip install dingtalk-stream httpx alibabacloud-dingtalk
```

- `dingtalk-stream` — 钉钉官方的 Stream Mode SDK（基于 WebSocket 的实时消息传递）
- `httpx` — 用于通过会话 Webhook 发送回复的异步 HTTP 客户端
- `alibabacloud-dingtalk` — 钉钉 OpenAPI SDK，用于 AI 卡片、表情回应和媒体下载

## 步骤 1：创建钉钉应用 {#step-1-create-a-dingtalk-app}

1.  前往 [钉钉开发者后台](https://open-dev.dingtalk.com/)。
2.  使用你的钉钉管理员账号登录。
3.  点击 **应用开发** → **企业内部开发** → **H5微应用**（或 **机器人**，具体取决于你的后台版本）→ **创建应用**。
4.  填写：
    - **应用名称**：例如，`Hermes Agent`
    - **应用描述**：可选
5.  创建后，导航到 **凭证与基础信息** 以找到你的 **Client ID** (AppKey) 和 **Client Secret** (AppSecret)。复制两者。

:::warning[凭证仅显示一次]
Client Secret 仅在创建应用时显示一次。如果丢失，你需要重新生成。切勿公开分享这些凭证或将它们提交到 Git。
:::

## 步骤 2：启用机器人能力 {#step-2-enable-the-robot-capability}

1.  在你的应用设置页面，进入 **添加能力** → **机器人**。
2.  启用机器人能力。
3.  在 **消息接收模式** 下，选择 **Stream Mode**（推荐——无需公网 URL）。

:::tip
Stream Mode 是推荐的设置。它使用从你的机器发起的长期 WebSocket 连接，因此你不需要公网 IP、域名或 Webhook 端点。这可以在 NAT、防火墙后以及本地机器上工作。
:::

## 步骤 3：找到你的钉钉用户 ID {#step-3-find-your-dingtalk-user-id}

Hermes Agent 使用你的钉钉用户 ID 来控制谁可以与机器人交互。钉钉用户 ID 是由你组织的管理员设置的字母数字字符串。

要找到你的用户 ID：

1.  询问你的钉钉组织管理员——用户 ID 在钉钉管理后台的 **通讯录** → **成员** 下配置。
2.  或者，机器人会记录每条接收消息的 `sender_id`。启动网关，向机器人发送一条消息，然后在日志中查看你的 ID。

## 步骤 4：配置 Hermes Agent {#step-4-configure-hermes-agent}

### 选项 A：交互式设置（推荐） {#option-a-interactive-setup-recommended}

运行引导式设置命令：

```bash
hermes gateway setup
```

出现提示时选择 **DingTalk**。设置向导可以通过以下两种方式之一进行授权：

- **二维码设备流（推荐）。** 使用钉钉手机应用扫描终端中打印的二维码——你的 Client ID 和 Client Secret 会自动返回并写入 `~/.hermes/.env`。无需访问开发者后台。
- **手动粘贴。** 如果你已有凭证（或扫描二维码不方便），请在提示时粘贴你的 Client ID、Client Secret 和允许的用户 ID。
:::note openClaw 品牌信息披露
由于钉钉在 API 层将 `verification_uri_complete` 硬编码为 openClaw 身份，目前二维码授权界面的来源字符串会显示为 `openClaw`，直到阿里巴巴/钉钉-真-AI 在服务端注册一个 Hermes 专用的模板。这只是钉钉展示授权界面时的呈现方式——你创建的机器人完全属于你，且仅对你的租户可见。
:::

### 选项 B：手动配置 {#option-b-manual-configuration}

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必填项
<a id="openclaw-branding-disclosure"></a>
DINGTALK_CLIENT_ID=你的应用密钥
DINGTALK_CLIENT_SECRET=你的应用密钥

# 安全性：限制哪些用户可以与机器人交互
DINGTALK_ALLOWED_USERS=用户ID-1

# 允许多个用户（逗号分隔）
# DINGTALK_ALLOWED_USERS=用户ID-1,用户ID-2
```

在 `~/.hermes/config.yaml` 中配置可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 在共享群聊中隔离每个参与者的上下文

### 启动网关 {#start-the-gateway}

配置完成后，启动钉钉网关：

```bash
hermes gateway
```

机器人应在几秒内连接到钉钉的 Stream 模式。发送一条消息给它——无论是私聊还是在已添加它的群聊中——以进行测试。

:::tip
你可以将 `hermes gateway` 在后台运行或设为 systemd 服务以实现持久运行。详见部署文档。
:::

## 功能特性 {#features}

### AI 卡片 {#ai-cards}

Hermes 可以使用钉钉 AI 卡片进行回复，而不是发送纯 Markdown 消息。卡片提供了更丰富、结构化的展示效果，并支持在 Agent 生成回复时进行流式更新。

要启用 AI 卡片，请在 `config.yaml` 中配置卡片模板 ID：

```yaml
platforms:
  dingtalk:
    enabled: true
    extra:
      card_template_id: "你的卡片模板ID"
```

你可以在钉钉开发者控制台中，在你的应用 AI 卡片设置下找到你的卡片模板 ID。启用 AI 卡片后，所有回复都将以卡片形式发送，并伴有流式文本更新。

### 表情回复 {#emoji-reactions}

Hermes 会自动给你的消息添加表情回复以显示处理状态：

- 🤔思考 —— 机器人开始处理你的消息时添加
- 🥳完成 —— 回复完成时添加（替换思考表情）

这些表情回复在私聊和群聊中均有效。

### 展示设置 {#display-settings}

你可以独立于其他平台自定义钉钉的展示行为：

```yaml
display:
  platforms:
    dingtalk:
      show_reasoning: false   # 在回复中展示模型推理/思考过程
      streaming: true         # 启用流式回复（与 AI 卡片配合工作）
      tool_progress: all      # 展示工具执行进度（all/new/off）
      interim_assistant_messages: true  # 展示中间解说消息
```

若要禁用工具进度和中间消息以获得更简洁的体验：

```yaml
display:
  platforms:
    dingtalk:
      tool_progress: off
      interim_assistant_messages: false
```

## 故障排除 {#troubleshooting}

### 机器人不回复消息 {#bot-is-not-responding-to-messages}

**原因**：机器人能力未启用，或 `DINGTALK_ALLOWED_USERS` 未包含你的用户 ID。

**解决**：在你的应用设置中确认机器人能力已启用，并且选择了 Stream 模式。检查你的用户 ID 是否在 `DINGTALK_ALLOWED_USERS` 中。重启网关。

### “dingtalk-stream 未安装”错误 {#dingtalk-stream-not-installed-error}

**原因**：未安装 `dingtalk-stream` Python 包。

**解决**：安装它：

```bash
pip install dingtalk-stream httpx
```

### “需要 DINGTALK_CLIENT_ID 和 DINGTALK_CLIENT_SECRET” {#dingtalkclientid-and-dingtalkclientsecret-required}

**原因**：环境变量或 `.env` 文件中未设置凭证。

**解决**：在 `~/.hermes/.env` 中确认 `DINGTALK_CLIENT_ID` 和 `DINGTALK_CLIENT_SECRET` 已正确设置。Client ID 是你的 AppKey，Client Secret 是你从钉钉开发者控制台获取的 AppSecret。

### Stream 断开连接/重连循环 {#stream-disconnects-reconnection-loops}

**原因**：网络不稳定、钉钉平台维护或凭证问题。

**解决**：适配器会自动以指数退避策略进行重连（2s → 5s → 10s → 30s → 60s）。检查你的凭证是否有效，以及你的应用是否未被停用。确认你的网络允许出站 WebSocket 连接。
### Bot 离线 {#bot-is-offline}

**原因**：Hermes 网关未运行，或连接失败。

**解决方法**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误信息。常见问题包括：凭据错误、应用被停用、未安装 `dingtalk-stream` 或 `httpx`。

### “没有可用的 session_webhook” {#no-sessionwebhook-available}

**原因**：Bot 尝试回复，但没有会话 webhook URL。这通常发生在 webhook 已过期，或者在接收消息和发送回复之间 Bot 被重启的情况下。

**解决方法**：向 Bot 发送一条新消息——每条传入的消息都会为回复提供一个全新的会话 webhook。这是钉钉平台的正常限制；Bot 只能回复它最近收到的消息。

## 安全 {#security}

:::warning
务必设置 `DINGTALK_ALLOWED_USERS` 以限制可以与 Bot 交互的人员。如果不设置，作为安全措施，网关默认会拒绝所有用户。只添加你信任的用户 ID——授权用户可以完全访问 Agent 的能力，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 注意事项 {#notes}

- **流模式**：无需公共 URL、域名或 webhook 服务器。连接通过 WebSocket 从你的机器发起，因此可以在 NAT 和防火墙后工作。
- **AI 卡片**：可以选择使用丰富的 AI 卡片进行回复，而不是纯 Markdown。通过 `card_template_id` 配置。
- **表情反应**：处理状态自动显示 🤔思考中/🥳已完成 表情。
- **Markdown 回复**：回复采用钉钉的 Markdown 格式，用于富文本显示。
- **媒体支持**：传入消息中的图片和文件会自动解析，并可由视觉工具处理。
- **消息去重**：适配器会进行消息去重，窗口期为 5 分钟，以防止重复处理同一条消息。
- **自动重连**：如果流连接断开，适配器会自动以指数退避方式重新连接。
- **消息长度限制**：每条消息的回复内容限制在 20,000 个字符以内。更长的回复会被截断。
