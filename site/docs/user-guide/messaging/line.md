---
sidebar_position: 17
title: "LINE"
description: "将 Hermes Agent 设置为 LINE Messaging API 机器人"
---

<a id="line-setup"></a>
# LINE 设置

通过 LINE Messaging API 将 Hermes Agent 作为 [LINE](https://line.me/) 机器人运行。该适配器作为一个捆版平台插件位于 `plugins/platforms/line/` 下——无需修改核心，只需像其他平台一样启用即可。

LINE 是日本、台湾和泰国最主流的即时通讯应用。如果你的用户在这些地区，他们会通过 LINE 联系你。

<a id="how-the-bot-responds"></a>
## 机器人的响应方式

| 场景 | 行为 |
|---------|----------|
| **一对一聊天**（`U` ID） | 回复每一条消息 |
| **群聊**（`C` ID） | 当群聊在白名单中时回复 |
| **多人房间**（`R` ID） | 当房间在白名单中时回复 |

支持接收文本、图片、音频、视频、文件、贴纸和位置信息。发送消息时，优先使用 **免费回复令牌**（一次性，约 60 秒有效期），令牌过期后回退到按量计费的 Push API。

---

<a id="step-1-create-a-line-messaging-api-channel"></a>
## 第一步：创建 LINE Messaging API 频道

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)。
2. 创建一个 Provider（服务提供方），然后在其下创建一个 **Messaging API** 频道。
3. 在频道的 **Basic settings**（基本设置）标签页中，复制 **Channel secret**（频道密钥）。
4. 在 **Messaging API** 标签页中，滚动到 **Channel access token (long-lived)**（长期有效的频道访问令牌）并点击 **Issue**（签发）。复制该令牌。
5. 同样在 **Messaging API** 标签页中，关闭 **Auto-reply messages**（自动回复消息）和 **Greeting messages**（问候消息），以免它们与机器人的回复冲突。

## 第三步：配置 Hermes

添加到 `~/.hermes/.env`：

```env
LINE_CHANNEL_ACCESS_TOKEN=YOUR_LONG_LIVED_TOKEN
LINE_CHANNEL_SECRET=YOUR_CHANNEL_SECRET

# 白名单 —— 至少需要以下之一（开发环境可使用 LINE_ALLOW_ALL_USERS=true）
LINE_ALLOWED_USERS=U1234567890abcdef...           # 以 U 为前缀的 ID，用逗号分隔
LINE_ALLOWED_GROUPS=C1234567890abcdef...          # 可选：群组 ID
LINE_ALLOWED_ROOMS=R1234567890abcdef...           # 可选：房间 ID

# 发送图片/音频/视频所需 —— 隧道解析到的公共 HTTPS 基础 URL
# 如果没有此项，send_image/voice/video 将拒绝执行。
LINE_PUBLIC_URL=https://my-tunnel.example.com
```
然后在 `~/.hermes/config.yaml` 中：

```yaml
gateway:
  platforms:
    line:
      enabled: true
```

这就够了——`gateway/config.py` 中的内置插件扫描会自动发现 `plugins/platforms/line/`。无需编辑 `Platform.LINE` 枚举，也无需注册 `_create_adapter`。

---

<a id="step-4-set-the-webhook-url"></a>
## 第 4 步：设置 Webhook URL

返回 LINE 控制台：

1. 打开你的渠道 → **Messaging API** 选项卡。
2. 在 **Webhook 设置** → **Webhook URL** 中，粘贴 `https://<你的隧道>/line/webhook`（注意 `/line/webhook` 路径——适配器会在这个路径上监听）。
3. 点击 **验证**。LINE 会 ping 这个网址；你应该看到 200 响应。
4. 将 **使用 Webhook** 切换为 **开**。

---

<a id="step-5-run-the-gateway"></a>
## 第 5 步：运行网关

```bash
hermes gateway
```

Agent 日志会显示：

```
LINE: webhook listening on 0.0.0.0:8646/line/webhook (public: https://my-tunnel.example.com)
```

在 LINE 应用中将该机器人添加为好友（扫描渠道 **Messaging API** 选项卡中的二维码），然后发送一条消息给它。

---

<a id="slow-llm-responses"></a>
## LLM 响应缓慢

LINE 的回复令牌是一次性的，大约在入站事件后 60 秒过期。缓慢的 LLM 无法及时回复，正常情况下这会迫使你使用付费的 Push API 调用。
当 LLM 的运行时间超过 `LINE_SLOW_RESPONSE_THRESHOLD` 秒（默认 `45`）时，适配器会消耗原始回复令牌，发送一个 **模板按钮** 气泡：

> 🤔 还在思考。准备好后点击下方获取答案。
>
> [ 获取答案 ]

用户在方便时点击 **获取答案**——该回传会提供一个*新的*回复令牌，适配器用它将缓存的答案发送出去（仍然免费）。

状态机：`PENDING → READY → DELIVERED`，外加 `ERROR` 表示已取消的运行（孤儿态 `PENDING` 会在 `/stop` 后解析为“运行在完成前被中断。”，从而避免持久按钮陷入循环）。

要禁用回传按钮并始终使用 Push 回退，请使用：

```env
LINE_SLOW_RESPONSE_THRESHOLD=0
```

为了可靠地触发回传流程，应抑制在阈值之前消耗回复令牌的干扰性消息：

```yaml
# ~/.hermes/config.yaml
display:
  interim_assistant_messages: false
  platforms:
    line:
      tool_progress: off
```

---

<a id="cron-notification-delivery"></a>
## Cron / 通知投递
```env
LINE_HOME_CHANNEL=Uxxxxxxxxxxxxxxxxxxxx     # 默认投递目标
```

带有 `deliver: line` 路由的 cron 作业会投递到 `LINE_HOME_CHANNEL`。该适配器内置了一个独立的仅推送发送器，因此即使 cron 在与网关不同的进程中运行，作业也能正常工作。

---

<a id="environment-variable-reference"></a>
## 环境变量参考

| 变量 | 必需 | 默认值 | 说明 |
|---|---|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | 是 | — | 长期有效的频道访问令牌 |
| `LINE_CHANNEL_SECRET` | 是 | — | 频道密钥（HMAC-SHA256 Webhook 验证） |
| `LINE_HOST` | 否 | `0.0.0.0` | Webhook 绑定主机 |
| `LINE_PORT` | 否 | `8646` | Webhook 绑定端口 |
| `LINE_PUBLIC_URL` | 仅媒体相关 | — | 公共 HTTPS 基础 URL；发送图片/语音/视频时必需 |
| `LINE_ALLOWED_USERS` | 必须指定其一 | — | 逗号分隔的用户 ID（以 U 开头） |
| `LINE_ALLOWED_GROUPS` | 必须指定其一 | — | 逗号分隔的群组 ID（以 C 开头） |
| `LINE_ALLOWED_ROOMS` | 必须指定其一 | — | 逗号分隔的聊天室 ID（以 R 开头） |
| `LINE_ALLOW_ALL_USERS` | 仅开发环境 | `false` | 完全跳过白名单 |
| `LINE_HOME_CHANNEL` | 否 | — | 默认的 cron / 通知投递目标 |
| `LINE_SLOW_RESPONSE_THRESHOLD` | 否 | `45` | 回传按钮触发前的等待秒数（`0` = 禁用） |
| `LINE_PENDING_TEXT` | 否 | "🤔 仍在思考…" | 回传按钮旁显示的提示文字 |
| `LINE_BUTTON_LABEL` | 否 | "获取答案" | 按钮标签 |
| `LINE_DELIVERED_TEXT` | 否 | "已回复 ✅" | 当已投递的按钮被再次点击时的回复 |
| `LINE_INTERRUPTED_TEXT` | 否 | "运行在完成前被中断。" | 当 `/stop` 孤立按钮被点击时的回复 |
---

<a id="troubleshooting"></a>
## 故障排查

**Webhook 验证时出现“invalid signature”。** `Channel secret` 填写错误，或者你的隧道重写了请求体。先通过 `curl -i https://&lt;tunnel&gt;/line/webhook/health` 验证——该请求应该返回 `{"status":"ok","platform":"line"}`。

**机器人在群组内收不到任何消息。** 检查 `LINE_ALLOWED_GROUPS` 是否包含了 `C...` 格式的群组 ID。要查找群组 ID，可以先发送一条测试消息，然后从 `~/.hermes/logs/gateway.log` 中 grep `LINE: rejecting unauthorized source`——被拒绝的来源字典里包含这些 ID。

**`send_image` 失败并提示“LINE_PUBLIC_URL must be set”。** LINE 的 Messaging API 不接受二进制上传——图片、音频和视频必须通过可访问的 HTTPS URL 提供。设置 `LINE_PUBLIC_URL` 为隧道的公共主机名，适配器会自动从 `/line/media/&lt;token&gt;/&lt;filename&gt;` 提供文件服务。

**Postback 按钮始终不出现。** 可能是 LLM 响应速度快于 `LINE_SLOW_RESPONSE_THRESHOLD` 阈值，或者是其他气泡（tool-progress、streaming）优先消耗了回复令牌。详见“Slow LLM responses”下的抑制说明。
**"已被其他档案使用"。** 同一个频道访问令牌已绑定到另一个正在运行的 Hermes 配置文件。请停止另一个 gateway，或使用独立的频道。

---

<a id="limitations"></a>
## 限制

* **每次仅一个气泡。** 每个 LINE 文本气泡限制为 5000 字符，每次 Reply/Push 调用最多发送 5 个气泡。较长的响应会被截断并追加省略号。
* **没有原生消息编辑。** LINE 没有编辑消息的 API——流式响应总是发送全新的气泡，从不修改已有的气泡。
* **不支持 Markdown 渲染。** 粗体（`**`）、斜体（`*`）、代码块和标题会以原始字符形式呈现。适配器会在发送前去除这些标记；URL 会保留（`[label](url)` 变为 `label (url)`）。
* **加载指示器仅限私聊。** LINE 拒绝在群组和聊天室使用 chat/loading API，因此打字指示器只在 1:1 对话中显示。
