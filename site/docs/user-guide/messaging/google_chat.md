---
sidebar_position: 12
title: "Google Chat"
description: "使用 Cloud Pub/Sub 将 Hermes Agent 设置为 Google Chat 机器人"
---

<a id="google-chat-setup"></a>
# Google Chat 设置

将 Hermes Agent 作为机器人连接到 Google Chat。该集成使用 Cloud Pub/Sub
拉取订阅处理入站事件，并通过 Chat REST API 发送出站消息。
其工作方式与 Slack Socket 模式或 Telegram 长轮询类似：你的 Hermes
进程无需公网 URL、隧道或 TLS 证书。它只需连接、认证，然后监听订阅——就像 Telegram 机器人监听 token 一样。

:::note Workspace 版本
<a id="workspace-edition"></a>
Google Chat 是 Google Workspace 的一部分。你可以使用个人 Workspace（通过 Google 注册的 `@yourdomain.com`）或拥有发布应用管理员权限的工作 Workspace 来使用此集成。仅限 Gmail 的账户无法托管 Chat 应用。
:::

<a id="overview"></a>
## 概览

| 组件 | 值 |
|-----------|-------|
| **库** | `google-cloud-pubsub`、`google-api-python-client`、`google-auth` |
| **入站传输** | Cloud Pub/Sub 拉取订阅（无需公网端点） |
| **出站传输** | Chat REST API（`chat.googleapis.com`） |
| **认证** | 服务账号 JSON，在订阅上具有 `roles/pubsub.subscriber` 角色 |
| **用户标识** | Chat 资源名称（`users/{id}`）+ 电子邮件 |

## 第二步：启用两个 API

在控制台中，依次进入 **API 和服务 → 库**，然后启用：

- **Google Chat API**
- **Cloud Pub/Sub API**

对于个人机器人产生的流量，这两个 API 都是免费的。

---

## 第三步：创建一个服务账号

**IAM 与管理 → 服务账号 → 创建服务账号。**

- 名称：`hermes-chat-bot`
- 跳过“授予此服务账号对项目的访问权限”这一步。你只需对特定订阅设置 IAM 即可——**不要**授予项目级别的 Pub/Sub 角色。

创建完成后，打开该服务账号，进入 **密钥 → 添加密钥 → 创建新密钥 → JSON**，然后下载文件。将其保存在只有 Hermes 能读取的位置（例如 `~/.hermes/google-chat-sa.json`，并执行 `chmod 600`）。
:::caution 没有“聊天机器人调用者”角色
一个常见的错误是搜索聊天专用的 IAM 角色并将其授予项目级别。该角色不存在。聊天机器人的权限来自被安装到空间中，而不是来自 IAM。您的服务账号只需要对您在下一步创建的订阅具有 Pub/Sub 订阅者权限。
<a id="there-is-no-chat-bot-caller-role"></a>
:::

---

<a id="step-4-create-the-pub-sub-topic-and-subscription"></a>
## 步骤 4：创建 Pub/Sub 主题和订阅

**Pub/Sub → 主题 → 创建主题。**

- 主题 ID：`hermes-chat-events`
- 其他所有内容保留默认设置。

创建后，主题详情页上有一个**订阅**选项卡。创建一个订阅：

- 订阅 ID：`hermes-chat-events-sub`
- 投递类型：**Pull**
- 消息留存期：**7 天**（这样积压的消息在 Hermes 重启后仍然存在）
- 其余保留默认值。

---

<a id="step-5-iam-binding-on-the-topic-critical"></a>
## 步骤 5：在主题上绑定 IAM（关键）

在**主题**（而不是订阅）上添加一个 IAM 主体：

- 主体：`chat-api-push@system.gserviceaccount.com`
- 角色：`Pub/Sub Publisher`

没有这一步，Google Chat 无法将事件发布到您的主题，您的机器人将永远收不到任何消息。

## 第 7 步：配置 Chat 应用

进入 **API 与服务 → Google Chat API → 配置**。

- **应用名称**：你希望用户看到的名称（"Hermes" 是合理的）。
- **头像 URL**：任意公开的 PNG 图片（Google 提供了一些默认头像）。
- **描述**：在应用目录中显示的简短说明。
- **功能**：启用**接收一对一消息**和**加入空间与群聊**。
- **连接设置**：选择 **Cloud Pub/Sub**，输入主题名称 `projects/&lt;your-project&gt;/topics/hermes-chat-events`。
- **可见性**：限制在你的工作空间（或特定用户）——测试期间不要对所有人公开。

保存。

## 第 9 步：配置 Hermes

将 Google Chat 相关配置添加到 `~/.hermes/.env`：

```bash
# 必填项
GOOGLE_CHAT_PROJECT_ID=my-chat-bot-123
GOOGLE_CHAT_SUBSCRIPTION_NAME=projects/my-chat-bot-123/subscriptions/hermes-chat-events-sub
GOOGLE_CHAT_SERVICE_ACCOUNT_JSON=/home/you/.hermes/google-chat-sa.json

# 授权 — 粘贴允许与机器人对话的人员邮箱
GOOGLE_CHAT_ALLOWED_USERS=you@yourdomain.com,coworker@yourdomain.com

# 可选项
GOOGLE_CHAT_HOME_CHANNEL=spaces/AAAA...         # cron 任务的默认投递目标
GOOGLE_CHAT_MAX_MESSAGES=1                      # Pub/Sub FlowControl；1 表示每个会话串行化命令
GOOGLE_CHAT_MAX_BYTES=16777216                  # 16 MiB — 消息在途字节数上限
```
项目 ID 也会回退到 `GOOGLE_CLOUD_PROJECT`，SA 路径则会回退到 `GOOGLE_APPLICATION_CREDENTIALS` —— 选择你喜欢的惯例即可。

为 Google Chat 适配器安装依赖项（目前没有已发布的 Hermes 扩展包——直接安装它们）：

```bash
pip install google-cloud-pubsub google-api-python-client google-auth google-auth-oauthlib
```

启动网关：

```bash
hermes gateway
```

你应该会看到类似下面这样的日志行：

```
[GoogleChat] Connected; project=my-chat-bot-123, subscription=<redacted>,
             bot_user_id=users/XXXX, flow_control(msgs=1, bytes=16777216)
```

在测试私信中发送 "hola"。机器人会先发布一条 "Hermes 正在思考……" 的标记消息，然后将同一条消息原地编辑成真正的回复——不会出现 "消息已删除" 的墓碑记录。

---

<a id="formatting-and-capabilities"></a>
## 格式与功能

Google Chat 渲染有限的 Markdown 子集：

| 支持 | 不支持 |
|-----------|---------------|
| `*加粗*`、`_斜体_`、`~删除线~`、`` `代码` `` | 标题、列表 |
| 通过 URL 的内联图片 | 交互式卡片 v2 按钮（此网关的 v1 版本） |
| 原生文件附件（在 `/setup-files` 之后——参见第 10 步） | 原生语音笔记 / 圆形视频笔记 |
Agent 的系统提示中包含一条 Google Chat 专用的提示，使其了解这些限制，避免使用无法渲染的格式。

消息大小限制：每条消息最多 4000 个字符。Agent 较长的回复会自动拆分为多条消息。

线程支持：当用户在某个线程中回复时，Hermes 会检测到 `thread.name` 并在同一线程中发布回复，因此每个线程都会获得一个独立的 Hermes 会话。

---

<a id="step-10-native-attachment-delivery-optional"></a>
## 第 10 步：原生附件投递（可选）

该 Bot 在开箱状态下可以发送文本、通过 URL 嵌入的图片，以及音频/视频/文档的下载卡片。若要投递 **原生** Chat 附件（即当用户拖放文件时看到的那个文件组件），每个用户需要通过一次性的 OAuth 流程单独授权该 Bot。

<a id="why-a-separate-flow"></a>
### 为什么需要单独的流程

Google Chat 的 `media.upload` 端点会硬性拒绝服务账户认证：

> 此方法不支持使用服务账户进行应用认证。请使用用户账户进行认证。

没有 IAM 角色或权限范围可以解决这个问题。该端点只接受用户凭据。因此，Bot 在每次上传文件时必须*以用户身份*进行操作——具体来说，是以请求该文件的用户身份。
<a id="one-time-host-setup"></a>
### 一次性主机设置

1. 在同一个 GCP 项目中，进入 **API 和服务 → 凭据**。
2. **创建凭据 → OAuth 客户端 ID → 桌面应用**。
3. 下载 JSON 文件，将其移动到运行 Hermes 的主机上。
4. 在主机上，向 Hermes 注册该客户端：

```bash
python -m gateway.platforms.google_chat_user_oauth \
    --client-secret /path/to/client_secret.json
```

这会写入 `~/.hermes/google_chat_user_client_secret.json`。这是共享的基础设施——它标识的是 OAuth 应用本身，而非某个具体用户。无论之后有多少用户进行授权，每台主机只需一个此文件即可。

<a id="per-user-authorization-in-chat"></a>
### 每个用户的授权（在聊天中）

每个用户在自己的机器人私聊中执行一次以下流程：

1. 用户向机器人发送 `/setup-files`。机器人回复当前状态及下一步操作。
2. 用户发送 `/setup-files start`。机器人回复一个 OAuth 链接。
3. 用户打开该链接，点击 **允许**，然后浏览器会加载失败，地址栏显示 `http://localhost:1/?...&code=...`。这个失败是预期行为——认证码就在 URL 中。
4. 用户复制失败的 URL（或仅复制 `code=...` 的值），作为 `/setup-files &lt;PASTED_URL&gt;` 粘贴回聊天中。机器人会用该值换取一个刷新令牌。
token 存放在 `~/.hermes/google_chat_user_tokens/&lt;sanitized_email&gt;.json`。  
该用户的私信（DM）中后续的文件请求会使用*他们的* token，因此机器人会以他们的身份上传，消息也会落入他们的空间。

后续撤销：`/setup-files revoke` 仅删除该用户的 token，其他用户的 token 不受影响。

<a id="scope"></a>
### 权限范围

该流程只请求一个权限范围：`chat.messages.create`。这涵盖了 `media.upload` 和引用上传的 `attachmentDataRef` 的 `messages.create`。没有 Drive，没有更广泛的 Chat 权限——这是刻意遵循最小权限原则。

<a id="multi-user-behavior"></a>
### 多用户行为

当提问者还没有个人 token 时，机器人会回退到 `~/.hermes/google_chat_user_token.json` 处的旧版单用户 token（如果存在来自安装多用户之前的旧版本）。如果两者都不可用，机器人会发布一条清晰的文字提示，告知提问者运行 `/setup-files`。

用户撤销仅清除自己的 slot。来自某个用户的 token 的 401/403 错误只会清除该用户的缓存。用户之间互不干扰。
---

<a id="troubleshooting"></a>
## 故障排除

**发送“hola.”后机器人没有任何响应。**

1. 在控制台中检查 Pub/Sub 订阅是否有未送达的消息。  
   如果有，说明 Hermes 未通过身份验证——请检查 `GOOGLE_CHAT_SERVICE_ACCOUNT_JSON`，  
   并确保该服务账号在订阅上被列为 `Pub/Sub Subscriber`（Pub/Sub 订阅者）。
2. 如果订阅的消息数为零，说明 Google Chat 没有发布消息。  
   请仔细检查 **主题** 上的 IAM 绑定：  
   `chat-api-push@system.gserviceaccount.com` 必须拥有 `Pub/Sub Publisher`（Pub/Sub 发布者）角色。
3. 检查 `hermes gateway` 日志中是否包含 `[GoogleChat] Connected`。如果看到  
   `[GoogleChat] Config validation failed`，错误消息会告诉你需要修复哪个环境变量。

**机器人回复了，但显示的是错误消息，而不是 Agent 的回答。**

检查日志中是否有 `[GoogleChat] Pub/Sub stream died` —— 如果重复出现，说明你的服务账号凭据可能已被轮换或订阅被删除。重试 10 次后，适配器会将其自身标记为致命错误。

**每次发送出站消息时都出现“403 Forbidden”。**

机器人在空间中被移除了，或者你在 Chat API 控制台中撤销了该机器人。请重新在空间中安装它（下一次 `ADDED_TO_SPACE` 事件会自动重新启用消息发送功能）。
**"Rate limit hit" 警告过多。**

Chat API 的默认配额是每个空间每分钟 60 条消息。如果你的 Agent 生成了超过该限制的长流式响应，适配器会以指数退避方式重试——但你仍然会看到用户可见的延迟。建议考虑使用简洁的响应，或在 GCP 控制台中提升配额。

**Bot 不断发布 "/setup-files" 通知而不是文件。**

提问者没有每用户 OAuth 令牌，也没有传统的回退方案。请在其 DM 中运行 `/setup-files` 并遵循步骤 10。交换完成后，下一次文件请求将本地上传，无需重启网关。

**`/setup-files start` 显示“主机上未存储客户端凭据。”**

一次性主机设置未完成。在运行 Hermes 的主机的终端中执行：

```bash
python -m gateway.platforms.google_chat_user_oauth \
    --client-secret /path/to/client_secret.json
```

然后再次发送 `/setup-files start`。

**`/setup-files &lt;PASTED_URL&gt;` 显示“令牌交换失败。”**

授权码是一次性的且有效期很短（通常几分钟）。请发送 `/setup-files start` 获取新的 URL 并重试。
---

<a id="security-notes"></a>
## 安全注意事项

- **服务账号范围**：适配器请求 `chat.bot` 和 `pubsub` 范围。IAM 应是实际控制手段——给你的服务账号授予最低权限（订阅上的 `roles/pubsub.subscriber` + `roles/pubsub.viewer`），而不是项目级或组织级的 Pub/Sub 角色。
- **附件下载保护**：Hermes 仅会将其服务账号的 Bearer 令牌附加到主机名与一份简短 Google 自有域名白名单（`googleapis.com`、`drive.google.com`、`lh[3-6].googleusercontent.com` 等）匹配的 URL 上。任何其他主机名在 HTTP 请求发出前就会被拒绝，以此防范 SSRF 场景下恶意构造的事件可能将 Bearer 令牌重定向到 GCE metadata 服务。
- **脱敏处理**：服务账号邮箱、订阅路径和主题路径会通过 `agent/redact.py` 从日志输出中剥离。调试信封转储（`GOOGLE_CHAT_DEBUG_RAW=1`）会经过相同的脱敏过滤器，并以 DEBUG 级别记录。
- **合规要求**：如果你计划将该机器人连接到受监管的工作空间（任何有数据驻留或 AI 治理策略的环境），请在首次安装前获得相关审批。
- **用户 OAuth 范围**：按用户的附件流程仅请求 `chat.messages.create`——这是涵盖 `media.upload` 及后续 `messages.create` 所需的最小范围。令牌以纯 JSON 形式持久化存储在 `~/.hermes/google_chat_user_tokens/&lt;sanitized_email&gt;.json`（文件系统权限即为保护措施，与服务账号密钥文件模型相同）。每个令牌仅归一个用户所有；撤销操作也限定在该用户范围内。
