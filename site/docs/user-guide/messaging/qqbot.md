<a id="qq-bot"></a>
# QQ 机器人

通过 **官方 QQ 开放平台 API (v2)** 将 Hermes 连接到 QQ——支持私聊（C2C）、群 @ 提及、频道和私信，并具备语音转文字功能。

<a id="overview"></a>
## 概述

QQ 机器人适配器使用 [官方 QQ 开放平台 API](https://bot.q.qq.com/wiki/develop/api-v2/) 实现：

- 通过 **WebSocket** 长连接接收 QQ 网关消息
- 通过 **REST API** 发送文字和 Markdown 回复
- 下载并处理图片、语音消息和文件附件
- 使用腾讯内置 ASR 或可配置的 STT 服务对语音消息进行转写

<a id="prerequisites"></a>
## 前提条件

1. **QQ 机器人应用** — 在 [q.qq.com](https://q.qq.com) 注册：
   - 创建一个新应用，记下你的 **App ID** 和 **App Secret**
   - 开启所需的 intents：C2C 消息、群 @ 消息、频道消息
   - 将机器人配置为沙箱模式用于测试，或发布到生产环境

2. **依赖** — 适配器需要 `aiohttp` 和 `httpx`：
   ```bash
   pip install aiohttp httpx
   ```

<a id="configuration"></a>
## 配置

<a id="interactive-setup"></a>
### 交互式设置

```bash
hermes gateway setup
```

从平台列表中选择 **QQ 机器人**，然后按照提示操作。

<a id="manual-configuration"></a>
### 手动配置

在 `~/.hermes/.env` 中设置所需的环境变量：

```bash
QQ_APP_ID=your-app-id
QQ_CLIENT_SECRET=your-app-secret
```

<a id="environment-variables"></a>
## 环境变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `QQ_APP_ID` | QQ 机器人 App ID（必填） | — |
| `QQ_CLIENT_SECRET` | QQ 机器人 App Secret（必填） | — |
| `QQBOT_HOME_CHANNEL` | 用于定时任务/通知投递的 OpenID | — |
| `QQBOT_HOME_CHANNEL_NAME` | 首页频道的显示名称 | `Home` |
| `QQ_ALLOWED_USERS` | 允许私聊的用户 OpenID，用逗号分隔 | open（所有用户） |
| `QQ_GROUP_ALLOWED_USERS` | 允许群聊的群 OpenID，用逗号分隔 | — |
| `QQ_ALLOW_ALL_USERS` | 设置为 `true` 以允许所有私聊 | `false` |
| `QQ_PORTAL_HOST` | 覆盖 QQ 门户主机地址（设为 `sandbox.q.qq.com` 可启用沙箱路由） | `q.qq.com` |
| `QQ_STT_API_KEY` | 语音转文字服务的 API 密钥 | — |
| `QQ_STT_BASE_URL` | （不直接读取——请在 `config.yaml` 中设置 `platforms.qqbot.extra.stt.baseUrl`） | n/a |
| `QQ_STT_MODEL` | STT 模型名称 | `glm-asr` |

<a id="advanced-configuration"></a>
## 高级配置

如需更精细的控制，请在 `~/.hermes/config.yaml` 中添加平台设置：

```yaml
platforms:
  qqbot:
    enabled: true
    extra:
      app_id: "your-app-id"
      client_secret: "your-secret"
      markdown_support: true       # 启用 QQ 的 Markdown 支持（msg_type 2）。仅支持配置文件，无环境变量对应项。
      dm_policy: "open"          # open | allowlist | disabled
      allow_from:
        - "user_openid_1"
      group_policy: "open"       # open | allowlist | disabled
      group_allow_from:
        - "group_openid_1"
      stt:
        provider: "zai"          # zai（GLM-ASR）、openai（Whisper）等
        baseUrl: "https://open.bigmodel.cn/api/coding/paas/v4"
        apiKey: "your-stt-key"
        model: "glm-asr"
```

<a id="voice-messages-stt"></a>
## 语音消息（STT）

语音转文字分为两个阶段：
1. **QQ 内置语音识别**（免费，会优先尝试）—— QQ 会在语音消息附件中提供 `asr_refer_text`，使用腾讯自家的语音识别服务
2. **已配置的 STT 提供商**（降级方案）—— 若 QQ 的语音识别未能返回文本，适配器会调用兼容 OpenAI 接口的 STT API：

   - **智谱/GLM (zai)**：默认提供商，使用 `glm-asr` 模型
   - **OpenAI Whisper**：设置 `QQ_STT_BASE_URL` 和 `QQ_STT_MODEL`
   - 任意兼容 OpenAI 接口的 STT 端点

<a id="troubleshooting"></a>
## 故障排查

<a id="bot-disconnects-immediately-quick-disconnect"></a>
### 机器人连接后立即断开

这通常意味着：
- **App ID / Secret 错误** —— 请在 q.qq.com 重新核对凭证
- **缺少权限** —— 确保机器人已开启所需的意图（intents）
- **仅沙箱模式** —— 若机器人处于沙箱模式，则只能接收 QQ 沙箱测试频道中的消息

<a id="voice-messages-not-transcribed"></a>
### 语音消息无法转写

1. 检查附件数据中是否包含 QQ 内置的 `asr_refer_text`
2. 若使用自定义 STT 提供商，确认 `QQ_STT_API_KEY` 已正确设置
3. 查看网关日志中的 STT 错误信息

<a id="messages-not-delivered"></a>
### 消息未被送达

- 确保在 q.qq.com 上已开启机器人的**意图（intents）**
- 若私信访问受限，检查 `QQ_ALLOWED_USERS` 设置
- 对于群消息，确保机器人已被 **@提及**（群策略可能要求加白名单）
- 检查 `QQBOT_HOME_CHANNEL` 用于定时/通知消息的投递

<a id="connection-errors"></a>
### 连接错误

- 确保已安装 `aiohttp` 和 `httpx`：`pip install aiohttp httpx`
- 检查网络能否连接到 `api.sgroup.qq.com` 及 WebSocket 网关
- 查看网关日志，了解详细的错误信息及重连行为
