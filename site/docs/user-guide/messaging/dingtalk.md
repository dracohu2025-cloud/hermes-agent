---
sidebar_position: 10
title: "DingTalk"
description: "将 Hermes Agent 配置为钉钉聊天机器人"
---

# DingTalk 配置 {#dingtalk-setup}

Hermes Agent 可以集成到钉钉中作为聊天机器人，让你通过私聊或群聊与你的 AI 助手对话。机器人通过钉钉的 Stream 模式（一种长连接 WebSocket 连接，无需公网地址或 webhook 服务器）进行连接，并通过钉钉的会话 webhook API 以 Markdown 格式回复消息。

在开始配置之前，这里是你最关心的部分：Hermes 进入你的钉钉工作空间后的表现。

## Hermes 的行为表现 {#how-hermes-behaves}

| 上下文 | 行为 |
|---------|----------|
| **私聊（1对1聊天）** | Hermes 会回复每一条消息。无需 `@提及`。每个私聊拥有独立的会话。 |
| **群聊** | 当你 `@提及` Hermes 时，它会回复。没有提及则忽略消息。 |
| **多人共享群聊** | 默认情况下，Hermes 在群内按用户隔离会话历史。同一群聊中两人对话不会共享同一份记录，除非你明确禁用此功能。 |

### 钉钉中的会话模型 {#session-model-in-dingtalk}

默认情况下：

- 每个私聊拥有自己的会话
- 共享群聊中的每个用户在群内拥有自己的会话

通过 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个群聊共享一个会话时才将其设为 `false`：

```yaml
group_sessions_per_user: false
```

本指南将引导你完成完整配置过程——从创建钉钉机器人到发送第一条消息。

## 前提条件 {#prerequisites}

安装所需的 Python 包：

```bash
pip install "hermes-agent[dingtalk]"
```

或单独安装：

```bash
pip install dingtalk-stream httpx alibabacloud-dingtalk
```

- `dingtalk-stream` — 钉钉官方 Stream 模式 SDK（基于 WebSocket 的实时消息）
- `httpx` — 用于通过会话 webhook 发送回复的异步 HTTP 客户端
- `alibabacloud-dingtalk` — 钉钉 OpenAPI SDK，用于 AI 卡片、表情回应和媒体下载

## 第一步：创建钉钉应用 {#step-1-create-a-dingtalk-app}

1. 前往 [钉钉开发者后台](https://open-dev.dingtalk.com/)。
2. 使用钉钉管理员账号登录。
3. 点击 **应用开发** → **自定义应用** → **创建 H5 微应用**（或根据后台版本选择 **机器人**）。
4. 填写：
   - **应用名称**：例如 `Hermes Agent`
   - **描述**：可选
5. 创建后，进入 **凭证与基础信息** 找到你的 **Client ID**（AppKey）和 **Client Secret**（AppSecret），复制两者。

:::warning[凭证仅显示一次]
Client Secret 仅在创建应用时显示一次。如果丢失，需要重新生成。切勿公开分享这些凭证或将其提交到 Git。
:::

## 第二步：启用机器人能力 {#step-2-enable-the-robot-capability}

1. 在应用设置页面，进入 **添加能力** → **机器人**。
2. 启用机器人能力。
3. 在 **消息接收模式** 下选择 **Stream 模式**（推荐——无需公网地址）。

:::tip
Stream 模式是推荐配置。它使用从你的机器发起的长连接 WebSocket 连接，因此无需公网 IP、域名或 webhook 端点。它可以在 NAT、防火墙后面以及本地机器上工作。
:::
--- END DOCUMENT CHUNK ---
## 第三步：找到你的 DingTalk 用户 ID {#step-3-find-your-dingtalk-user-id}

Hermes Agent 使用你的 DingTalk 用户 ID 来控制谁能与机器人交互。DingTalk 用户 ID 是由你所在组织的管理员设置的字母数字字符串。

要找到你的 ID：

1. 询问你的 DingTalk 组织管理员——用户 ID 在 DingTalk 管理后台的 **通讯录** → **成员** 中配置。
2. 或者，机器人会记录每条传入消息的 `sender_id`。启动网关，给机器人发一条消息，然后在日志中查找你的 ID。

## 第四步：配置 Hermes Agent {#step-4-configure-hermes-agent}

### 选项 A：交互式设置（推荐） {#option-a-interactive-setup-recommended}

运行引导式设置命令：

```bash
hermes gateway setup
```

在提示时选择 **DingTalk**。设置向导可以通过以下两种路径之一进行授权：

- **二维码设备流（推荐）。** 使用 DingTalk 手机应用扫描终端中打印的二维码——你的 Client ID 和 Client Secret 会自动返回并写入 `~/.hermes/.env`。无需访问开发者控制台。
- **手动粘贴。** 如果你已有凭据（或扫码不方便），在提示时粘贴你的 Client ID、Client Secret 和允许的用户 ID。

:::note openClaw 品牌披露
<a id="openclaw-branding-disclosure"></a>
由于 DingTalk 的 `verification_uri_complete` 在 API 层硬编码为 openClaw 身份，二维码目前会在 `openClaw` 源字符串下进行授权，直到阿里巴巴 / DingTalk-Real-AI 在服务端注册一个 Hermes 专用的模板。这纯粹是 DingTalk 展示同意屏幕的方式——你创建的机器人完全属于你，并且对你的租户私有。
:::

### 选项 B：手动配置 {#option-b-manual-configuration}

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必填
DINGTALK_CLIENT_ID=your-app-key
DINGTALK_CLIENT_SECRET=your-app-secret

# 安全：限制谁能与机器人交互
DINGTALK_ALLOWED_USERS=user-id-1

# 多个允许的用户（逗号分隔）
# DINGTALK_ALLOWED_USERS=user-id-1,user-id-2

# 可选：群聊门控（与 Slack/Telegram/Discord/WhatsApp 类似）
# DINGTALK_REQUIRE_MENTION=true
# DINGTALK_FREE_RESPONSE_CHATS=cidABC==,cidDEF==
# DINGTALK_MENTION_PATTERNS=^小马
# DINGTALK_HOME_CHANNEL=cidXXXX==
# DINGTALK_ALLOW_ALL_USERS=true
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true

gateway:
  platforms:
    dingtalk:
      extra:
        # 在群组中要求 @提及 后机器人再回复（与 Slack/Telegram/Discord 一致）。
        # 私聊忽略此设置——机器人始终在 1:1 聊天中回复。
        require_mention: true

        # 按平台的白名单。设置后，只有这些 DingTalk 用户 ID 可以与机器人交互
        # （语义与 DINGTALK_ALLOWED_USERS 相同，但作用域在此处而非 .env 中）。
        allowed_users:
          - user-id-1
          - user-id-2
```

- `group_sessions_per_user: true` 保持每个参与者在共享群聊中的上下文隔离
- `require_mention: true` 防止机器人回复每条群消息——它只在有人 @提及 时回答
- `dingtalk.extra` 下的 `allowed_users` 是 `DINGTALK_ALLOWED_USERS` 的替代方案；如果两者都设置，则会合并
### 启动网关 {#start-the-gateway}

配置完成后，启动钉钉网关：

```bash
hermes gateway
```

机器人应在几秒内连接到钉钉的 Stream 模式。给它发送一条消息（私聊或已添加的群聊均可）进行测试。

:::tip
你可以将 `hermes gateway` 放在后台运行，或作为 systemd 服务以实现持久运行。详情请参阅部署文档。
:::

## 功能特性 {#features}

### AI 卡片 {#ai-cards}

Hermes 可以使用钉钉 AI 卡片回复，而非纯 Markdown 消息。卡片提供更丰富、更结构化的展示方式，并支持在 Agent 生成回复时进行流式更新。

要启用 AI 卡片，请在 `config.yaml` 中配置卡片模板 ID：

```yaml
platforms:
  dingtalk:
    enabled: true
    extra:
      card_template_id: "your-card-template-id"
```

你可以在钉钉开发者控制台的应用 AI 卡片设置中找到你的卡片模板 ID。启用 AI 卡片后，所有回复都会以卡片形式发送，并支持流式文本更新。

### Emoji 反应 {#emoji-reactions}

Hermes 会自动为你的消息添加 emoji 反应，以显示处理状态：

- 🤔思考中 — 机器人开始处理你的消息时添加
- 🥳完成 — 回复完成时添加（替换思考中的反应）

这些反应在私聊和群聊中均有效。

### 显示设置 {#display-settings}

你可以独立于其他平台自定义钉钉的显示行为：

```yaml
display:
  platforms:
    dingtalk:
      show_reasoning: false   # 在回复中显示模型推理/思考过程
      streaming: true         # 启用流式响应（与 AI 卡片配合使用）
      tool_progress: all      # 显示工具执行进度（all/new/off）
      interim_assistant_messages: true  # 显示中间评论消息
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

### 机器人未响应消息 {#bot-is-not-responding-to-messages}

**原因**：机器人能力未启用，或 `DINGTALK_ALLOWED_USERS` 中未包含你的用户 ID。

**修复**：确认在应用设置中已启用机器人能力，并选择了 Stream 模式。检查你的用户 ID 是否在 `DINGTALK_ALLOWED_USERS` 中。重启网关。

### "dingtalk-stream not installed" 错误 {#dingtalk-stream-not-installed-error}

**原因**：未安装 `dingtalk-stream` Python 包。

**修复**：安装它：

```bash
pip install dingtalk-stream httpx
```

### "DINGTALK_CLIENT_ID and DINGTALK_CLIENT_SECRET required" 错误 {#dingtalkclientid-and-dingtalkclientsecret-required}

**原因**：环境变量或 `.env` 文件中未设置凭证。

**修复**：确认 `~/.hermes/.env` 中正确设置了 `DINGTALK_CLIENT_ID` 和 `DINGTALK_CLIENT_SECRET`。Client ID 是你的 AppKey，Client Secret 是你的 AppSecret（来自钉钉开发者控制台）。

### 流断开 / 重连循环 {#stream-disconnects-reconnection-loops}

**原因**：网络不稳定、钉钉平台维护或凭证问题。

**修复**：适配器会自动以指数退避方式重连（2秒 → 5秒 → 10秒 → 30秒 → 60秒）。检查你的凭证是否有效，应用是否未被停用。确认你的网络允许出站 WebSocket 连接。
### 机器人离线 {#bot-is-offline}

**原因**：Hermes 网关未运行，或连接失败。

**修复**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误信息。常见问题：凭据错误、应用被停用、未安装 `dingtalk-stream` 或 `httpx`。

### "No session_webhook available"（无可用会话 Webhook） {#no-sessionwebhook-available}

**原因**：机器人尝试回复，但没有会话 Webhook URL。这通常发生在 Webhook 过期，或机器人在接收消息和发送回复之间被重启时。

**修复**：向机器人发送一条新消息——每条传入消息都会提供一个全新的会话 Webhook 用于回复。这是钉钉的正常限制；机器人只能回复最近收到的消息。

## 安全性 {#security}

:::warning
务必设置 `DINGTALK_ALLOWED_USERS` 来限制哪些用户可以与机器人交互。如果不设置，网关默认会拒绝所有用户，这是一种安全措施。只添加你信任的用户 ID——授权用户拥有对 Agent 能力的完全访问权限，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 备注 {#notes}

- **流模式**：无需公网 URL、域名或 Webhook 服务器。连接从你的机器通过 WebSocket 发起，因此可以在 NAT 和防火墙后面工作。
- **AI 卡片**：可选择使用丰富的 AI 卡片代替纯 Markdown 进行回复。通过 `card_template_id` 配置。
- **表情反应**：自动添加 🤔思考中/🥳已完成 反应来表示处理状态。
- **Markdown 响应**：回复以钉钉的 Markdown 格式呈现，支持富文本显示。
- **媒体支持**：传入消息中的图片和文件会自动解析，并可由视觉工具处理。
- **消息去重**：适配器在 5 分钟窗口内对消息进行去重，防止重复处理同一条消息。
- **自动重连**：如果流连接断开，适配器会自动以指数退避策略重新连接。
- **消息长度限制**：每条消息的响应限制为 20,000 个字符。更长的响应会被截断。
