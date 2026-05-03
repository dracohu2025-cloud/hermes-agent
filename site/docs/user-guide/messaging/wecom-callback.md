---
sidebar_position: 15
---

# 企业微信回调（自建应用） {#wecom-callback-self-built-app}

通过回调/Webhook 模式，将 Hermes 作为自建企业应用接入企业微信。

<a id="wecom-bot-vs-wecom-callback"></a>
:::info 企业微信 Bot 与 企业微信回调 的区别
Hermes 支持两种企业微信集成模式：
- **[企业微信 Bot](wecom.md)** — Bot 模式，通过 WebSocket 连接。设置更简单，可在群聊中使用。
- **企业微信回调**（本页）— 自建应用，接收加密的 XML 回调。在用户的企业微信侧边栏中显示为一级应用。支持多企业路由。
:::

## 工作原理 {#how-it-works}

1. 在企业微信管理后台注册一个自建应用
2. 企业微信将加密的 XML 推送到你的 HTTP 回调端点
3. Hermes 解密消息，将其加入 Agent 队列
4. 立即确认（静默处理——用户无感知）
5. Agent 处理请求（通常需要 3–30 分钟）
6. 通过企业微信 `message/send` API 主动发送回复

## 前置条件 {#prerequisites}

- 一个拥有管理员权限的企业微信企业账号
- `aiohttp` 和 `httpx` Python 包（默认安装中已包含）
- 一个可公开访问的回调 URL 服务器（或使用 ngrok 等隧道工具）

## 设置步骤 {#setup}

### 1. 在企业微信中创建自建应用 {#1-create-a-self-built-app-in-wecom}

1. 前往 [企业微信管理后台](https://work.weixin.qq.com/) → **应用管理** → **创建应用**
2. 记下你的 **企业 ID**（显示在管理后台顶部）
3. 在应用设置中，创建一个 **企业 Secret**
4. 从应用概览页面记下 **Agent ID**
5. 在 **接收消息** 中，配置回调 URL：
   - URL：`http://YOUR_PUBLIC_IP:8645/wecom/callback`
   - Token：生成一个随机 Token（企业微信会提供一个）
   - EncodingAESKey：生成一个密钥（企业微信会提供一个）

### 2. 配置环境变量 {#2-configure-environment-variables}

在 `.env` 文件中添加：

```bash
WECOM_CALLBACK_CORP_ID=your-corp-id
WECOM_CALLBACK_CORP_SECRET=your-corp-secret
WECOM_CALLBACK_AGENT_ID=1000002
WECOM_CALLBACK_TOKEN=your-callback-token
WECOM_CALLBACK_ENCODING_AES_KEY=your-43-char-aes-key

# 可选
WECOM_CALLBACK_HOST=0.0.0.0
WECOM_CALLBACK_PORT=8645
WECOM_CALLBACK_ALLOWED_USERS=user1,user2
```

### 3. 启动网关 {#3-start-the-gateway}

```bash
hermes gateway
```

（只有在 `hermes gateway install` 注册了 systemd/launchd 服务后，才使用 `hermes gateway start`。）

回调适配器会在配置的端口上启动一个 HTTP 服务器。企业微信会通过 GET 请求验证回调 URL，然后开始通过 POST 发送消息。

## 配置参考 {#configuration-reference}

在 `config.yaml` 的 `platforms.wecom_callback.extra` 下设置，或使用环境变量：

| 设置项 | 默认值 | 描述 |
|---------|---------|-------------|
| `corp_id` | — | 企业微信企业 ID（必填） |
| `corp_secret` | — | 自建应用的企业 Secret（必填） |
| `agent_id` | — | 自建应用的 Agent ID（必填） |
| `token` | — | 回调验证 Token（必填） |
| `encoding_aes_key` | — | 回调加密用的 43 字符 AES 密钥（必填） |
| `host` | `0.0.0.0` | HTTP 回调服务器的绑定地址 |
| `port` | `8645` | HTTP 回调服务器的端口 |
| `path` | `/wecom/callback` | 回调端点的 URL 路径 |
## 多应用路由 {#multi-app-routing}

对于运行多个自建应用的企业（例如跨不同部门或子公司），在 `config.yaml` 中配置 `apps` 列表：

```yaml
platforms:
  wecom_callback:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8645
      apps:
        - name: "dept-a"
          corp_id: "ww_corp_a"
          corp_secret: "secret-a"
          agent_id: "1000002"
          token: "token-a"
          encoding_aes_key: "key-a-43-chars..."
        - name: "dept-b"
          corp_id: "ww_corp_b"
          corp_secret: "secret-b"
          agent_id: "1000003"
          token: "token-b"
          encoding_aes_key: "key-b-43-chars..."
```

用户通过 `corp_id:user_id` 进行作用域隔离，以防止跨企业冲突。当用户发送消息时，适配器会记录他们所属的应用（企业），并通过对应应用的访问令牌路由回复。

## 访问控制 {#access-control}

限制哪些用户可以与应用交互：

```bash
# 允许特定用户
WECOM_CALLBACK_ALLOWED_USERS=zhangsan,lisi,wangwu

# 或允许所有用户
WECOM_CALLBACK_ALLOW_ALL_USERS=true
```

## 端点 {#endpoints}

适配器暴露以下端点：

| 方法 | 路径 | 用途 |
|--------|------|---------|
| GET | `/wecom/callback` | URL 验证握手（企业微信在设置期间发送） |
| POST | `/wecom/callback` | 加密消息回调（企业微信在此处发送用户消息） |
| GET | `/health` | 健康检查 — 返回 `{"status": "ok"}` |

## 加密 {#encryption}

所有回调负载均使用 EncodingAESKey 通过 AES-CBC 加密。适配器处理：

- **入站**：解密 XML 负载，验证 SHA1 签名
- **出站**：通过主动 API 发送回复（非加密回调响应）

加密实现与腾讯官方的 WXBizMsgCrypt SDK 兼容。

## 限制 {#limitations}

- **不支持流式输出** — 回复在 Agent 完成后以完整消息形式到达
- **无输入状态指示** — 回调模型不支持输入状态
- **仅支持文本** — 目前仅支持文本消息输入；图片/文件/语音输入尚未实现。Agent 通过企业微信平台提示了解出站媒体能力（图片、文档、视频、语音）。
- **响应延迟** — Agent 会话需要 3–30 分钟；用户在处理完成后看到回复
