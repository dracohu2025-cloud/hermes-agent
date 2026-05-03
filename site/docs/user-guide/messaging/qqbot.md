# QQ Bot {#qq-bot}

通过 **官方 QQ 机器人 API (v2)** 将 Hermes 连接到 QQ — 支持私聊 (C2C)、群 @提及、频道和带语音转文字的直接消息。

## 概述 {#overview}

QQ Bot 适配器使用 [官方 QQ 机器人 API](https://bot.q.qq.com/wiki/develop/api-v2/) 实现以下功能：

- 通过持久 **WebSocket** 连接接收来自 QQ 网关的消息
- 通过 **REST API** 发送文本和 Markdown 回复
- 下载并处理图片、语音消息和文件附件
- 使用腾讯内置 ASR 或可配置的 STT 提供商转写语音消息

## 前置条件 {#prerequisites}

1. **QQ 机器人应用** — 在 [q.qq.com](https://q.qq.com) 注册：
   - 创建一个新应用，记下你的 **App ID** 和 **App Secret**
   - 启用所需的意图：C2C 消息、群 @消息、频道消息
   - 在沙箱模式下配置机器人进行测试，或发布到生产环境

2. **依赖项** — 适配器需要 `aiohttp` 和 `httpx`：
   ```bash
   pip install aiohttp httpx
   ```

## 配置 {#configuration}

### 交互式设置 {#interactive-setup}

```bash
hermes gateway setup
```

从平台列表中选择 **QQ Bot** 并按照提示操作。

### 手动配置 {#manual-configuration}

在 `~/.hermes/.env` 中设置所需的环境变量：

```bash
QQ_APP_ID=your-app-id
QQ_CLIENT_SECRET=your-app-secret
```

## 环境变量 {#environment-variables}

| 变量 | 描述 | 默认值 |
|---|---|---|
| `QQ_APP_ID` | QQ 机器人 App ID（必填） | — |
| `QQ_CLIENT_SECRET` | QQ 机器人 App Secret（必填） | — |
| `QQBOT_HOME_CHANNEL` | 用于定时任务/通知投递的 OpenID | — |
| `QQBOT_HOME_CHANNEL_NAME` | 主频道的显示名称 | `Home` |
| `QQ_ALLOWED_USERS` | 允许私信访问的用户 OpenID，逗号分隔 | open（所有用户） |
| `QQ_GROUP_ALLOWED_USERS` | 允许群访问的群 OpenID，逗号分隔 | — |
| `QQ_ALLOW_ALL_USERS` | 设置为 `true` 允许所有私信 | `false` |
| `QQ_PORTAL_HOST` | 覆盖 QQ 门户主机（设置为 `sandbox.q.qq.com` 用于沙箱路由） | `q.qq.com` |
| `QQ_STT_API_KEY` | 语音转文字提供商的 API 密钥 | — |
| `QQ_STT_BASE_URL` | STT 提供商的基础 URL | `https://open.bigmodel.cn/api/coding/paas/v4` |
| `QQ_STT_MODEL` | STT 模型名称 | `glm-asr` |

## 高级配置 {#advanced-configuration}

如需精细控制，可将平台设置添加到 `~/.hermes/config.yaml`：

```yaml
platforms:
  qq:
    enabled: true
    extra:
      app_id: "your-app-id"
      client_secret: "your-secret"
      markdown_support: true       # 启用 QQ markdown（msg_type 2）。仅配置项，无对应环境变量。
      dm_policy: "open"          # open | allowlist | disabled
      allow_from:
        - "user_openid_1"
      group_policy: "open"       # open | allowlist | disabled
      group_allow_from:
        - "group_openid_1"
      stt:
        provider: "zai"          # zai (GLM-ASR), openai (Whisper) 等
        baseUrl: "https://open.bigmodel.cn/api/coding/paas/v4"
        apiKey: "your-stt-key"
        model: "glm-asr"
```

## 语音消息 (STT) {#voice-messages-stt}

语音转文字分两个阶段进行：
1. **QQ 内置 ASR**（免费，始终优先尝试）——QQ 在语音消息附件中提供 `asr_refer_text`，使用腾讯自有的语音识别
2. **配置的 STT 提供商**（回退）——如果 QQ 的 ASR 未返回文本，适配器会调用兼容 OpenAI 的 STT API：

   - **智谱/GLM (zai)**：默认提供商，使用 `glm-asr` 模型
   - **OpenAI Whisper**：设置 `QQ_STT_BASE_URL` 和 `QQ_STT_MODEL`
   - 任何兼容 OpenAI 的 STT 端点

## 故障排除 {#troubleshooting}

### Bot 立即断开连接（快速断开） {#bot-disconnects-immediately-quick-disconnect}

这通常意味着：
- **App ID / Secret 无效**——请在 q.qq.com 上仔细核对你的凭证
- **缺少权限**——确保 Bot 已启用所需的 intents
- **仅沙箱模式的 Bot**——如果 Bot 处于沙箱模式，它只能接收来自 QQ 沙箱测试频道的消息

### 语音消息未转写 {#voice-messages-not-transcribed}

1. 检查附件数据中是否包含 QQ 内置的 `asr_refer_text`
2. 如果使用自定义 STT 提供商，请确认 `QQ_STT_API_KEY` 已正确设置
3. 查看网关日志中的 STT 错误信息

### 消息未送达 {#messages-not-delivered}

- 在 q.qq.com 上确认 Bot 的 **intents** 已启用
- 如果私信访问受限，请检查 `QQ_ALLOWED_USERS`
- 对于群消息，确保 Bot 被 **@提及**（群策略可能要求白名单）
- 检查 `QQBOT_HOME_CHANNEL` 用于定时任务/通知投递

### 连接错误 {#connection-errors}

- 确保已安装 `aiohttp` 和 `httpx`：`pip install aiohttp httpx`
- 检查到 `api.sgroup.qq.com` 和 WebSocket 网关的网络连通性
- 查看网关日志以获取详细的错误信息和重连行为
