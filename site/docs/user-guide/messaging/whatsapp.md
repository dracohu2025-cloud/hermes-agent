---
sidebar_position: 5
title: "WhatsApp"
description: "通过内置的 Baileys 桥接器将 Hermes Agent 设置为 WhatsApp 机器人"
---

# WhatsApp 设置

Hermes 通过基于 **Baileys** 的内置桥接器连接到 WhatsApp。其工作原理是模拟 WhatsApp Web 会话 —— **并非**通过官方的 WhatsApp Business API。因此不需要 Meta 开发者账号或商业认证。

:::warning 非官方 API —— 封号风险
WhatsApp 官方并不支持 Business API 之外的第三方机器人。使用第三方桥接器存在账号受限的小风险。为了降低风险：
- **为机器人使用专用电话号码**（不要使用你的个人号码）
- **不要发送群发/垃圾消息** —— 保持对话式使用
- **不要向未主动给你发消息的人自动发送外发消息**
:::

:::warning WhatsApp Web 协议更新
WhatsApp 会定期更新其 Web 协议，这可能会暂时破坏与第三方桥接器的兼容性。发生这种情况时，Hermes 会更新桥接器依赖。如果 WhatsApp 更新后机器人停止工作，请拉取最新的 Hermes 版本并重新配对。
:::

## 两种模式

| 模式 | 工作原理 | 适用场景 |
|------|-------------|----------|
| **独立机器人号码** (推荐) | 为机器人分配一个专用电话号码。用户直接给该号码发消息。 | 体验更佳、支持多用户、封号风险较低 |
| **个人自聊 (Self-chat)** | 使用你自己的 WhatsApp。你通过给自己发消息来与 Agent 对话。 | 快速设置、单用户、测试 |

---

## 前置条件

- **Node.js v18+** 和 **npm** —— WhatsApp 桥接器作为一个 Node.js 进程运行
- **安装了 WhatsApp 的手机**（用于扫描二维码）

与旧的浏览器驱动型桥接器不同，当前基于 Baileys 的桥接器**不需要**本地 Chromium 或 Puppeteer 依赖栈。

---

## 第 1 步：运行设置向导

```bash
hermes whatsapp
```

向导将执行以下操作：

1. 询问你想要哪种模式（**bot** 或 **self-chat**）
2. 如果需要，安装桥接器依赖
3. 在终端显示一个**二维码**
4. 等待你扫描

**扫描二维码的方法：**

1. 在手机上打开 WhatsApp
2. 进入 **设置 → 已链接设备 (Linked Devices)**
3. 点击 **链接设备 (Link a Device)**
4. 将摄像头对准终端的二维码

配对成功后，向导会确认连接并退出。你的会话将自动保存。

:::tip
如果二维码看起来是乱码，请确保你的终端宽度至少为 60 列并支持 Unicode。你也可以尝试换一个终端模拟器。
:::

---

## 第 2 步：获取第二个电话号码（机器人模式）

对于机器人模式，你需要一个尚未在 WhatsApp 注册的电话号码。有三种选择：

| 选项 | 成本 | 备注 |
|--------|------|-------|
| **Google Voice** | 免费 | 仅限美国。在 [voice.google.com](https://voice.google.com) 获取号码。通过 Google Voice 应用接收短信验证 WhatsApp。 |
| **预付费 SIM 卡** | $5–15 一次性 | 任何运营商。激活并验证 WhatsApp 后，SIM 卡可以放进抽屉。号码必须保持活跃（每 90 天打一次电话）。 |
| **VoIP 服务** | 免费–$5/月 | TextNow、TextFree 或类似服务。部分 VoIP 号码会被 WhatsApp 屏蔽 —— 如果第一个不行，多试几个。 |

获取号码后：

1. 在手机上安装 WhatsApp（或使用支持双卡的 WhatsApp Business 应用）
2. 用新号码注册 WhatsApp
3. 运行 `hermes whatsapp` 并使用该 WhatsApp 账号扫描二维码

---

## 第 3 步：配置 Hermes

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必填
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot                          # "bot" 或 "self-chat"

# 访问控制 —— 选择以下选项之一：
WHATSAPP_ALLOWED_USERS=15551234567         # 逗号分隔的电话号码（带国家代码，不带 +）
# WHATSAPP_ALLOWED_USERS=*                 # 或使用 * 允许所有人
# WHATSAPP_ALLOW_ALL_USERS=true            # 或设置此标志（效果等同于 *）
```

:::tip 允许所有人的简写
设置 `WHATSAPP_ALLOWED_USERS=*` 会允许**所有**发送者（等同于 `WHATSAPP_ALLOW_ALL_USERS=true`）。
这与 [Signal 群组白名单](/reference/environment-variables) 保持一致。
如果你想改用配对流程，请移除这两个变量，并依赖 [DM 配对系统](/user-guide/security#dm-pairing-system)。
:::

在 `~/.hermes/config.yaml` 中可选的行为设置：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `unauthorized_dm_behavior: pair` 是全局默认设置。未知的 DM 发送者会收到配对码。
- `whatsapp.unauthorized_dm_behavior: ignore` 让 WhatsApp 对未授权的 DM 保持静默，这通常是私人号码更好的选择。

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 作为用户服务安装
sudo hermes gateway install --system   # 仅限 Linux：开机自启系统服务
```

网关会自动使用保存的会话启动 WhatsApp 桥接器。

---

## 会话持久化

Baileys 桥接器将其会话保存在 `~/.hermes/platforms/whatsapp/session` 下。这意味着：

- **会话在重启后依然有效** —— 你不需要每次都重新扫描二维码
- 会话数据包含加密密钥和设备凭据
- **不要分享或提交此会话目录** —— 它拥有对该 WhatsApp 账号的完整访问权限

---

## 重新配对

如果会话失效（手机重置、WhatsApp 更新、手动取消链接），你会在网关日志中看到连接错误。修复方法：

```bash
hermes whatsapp
```

这将生成一个新的二维码。再次扫描即可重新建立会话。网关会自动通过重连逻辑处理**临时**断开连接（网络波动、手机短暂离线）。

---

## 语音消息

Hermes 在 WhatsApp 上支持语音：

- **接收：** 语音消息 (`.ogg` opus) 会使用配置的 STT 提供商自动转录：本地 `faster-whisper`、Groq Whisper (`GROQ_API_KEY`) 或 OpenAI Whisper (`VOICE_TOOLS_OPENAI_KEY`)
- **发送：** TTS 响应将作为 MP3 音频文件附件发送
- 默认情况下，Agent 的回复会带有前缀 "⚕ **Hermes Agent**"。你可以在 `config.yaml` 中自定义或禁用它：

```yaml
# ~/.hermes/config.yaml
whatsapp:
  reply_prefix: ""                          # 空字符串禁用页眉
  # reply_prefix: "🤖 *My Bot*\n──────\n"  # 自定义前缀（支持 \n 换行）
```

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| **二维码无法扫描** | 确保终端足够宽（60+ 列）。尝试更换终端。确保你扫描的是正确的 WhatsApp 账号（机器人号码，而非个人号码）。 |
| **二维码过期** | 二维码每约 20 秒刷新一次。如果超时，请重启 `hermes whatsapp`。 |
| **会话无法持久化** | 检查 `~/.hermes/platforms/whatsapp/session` 是否存在且可写。如果是容器化部署，请将其挂载为持久卷。 |
| **意外登出** | WhatsApp 会在长期不活动后取消设备链接。保持手机开启并连接网络，必要时使用 `hermes whatsapp` 重新配对。 |
| **桥接器崩溃或循环重连** | 重启网关，更新 Hermes，如果会话因 WhatsApp 协议更改而失效，请重新配对。 |
| **WhatsApp 更新后机器人停止工作** | 更新 Hermes 以获取最新的桥接器版本，然后重新配对。 |
| **macOS: 提示 "Node.js not installed" 但 node 在终端可用** | launchd 服务不会继承你的 shell PATH。运行 `hermes gateway install` 将当前的 PATH 重新快照到 plist 中，然后运行 `hermes gateway start`。详见 [网关服务文档](./index.md#macos-launchd)。 |
| **收不到消息** | 确认 `WHATSAPP_ALLOWED_USERS` 包含发送者的号码（带国家代码，不带 `+` 或空格），或将其设置为 `*` 以允许所有人。在 `.env` 中设置 `WHATSAPP_DEBUG=true` 并重启网关，在 `bridge.log` 中查看原始消息事件。 |
| **机器人向陌生人回复配对码** | 如果你希望静默忽略未授权的 DM，请在 `~/.hermes/config.yaml` 中设置 `whatsapp.unauthorized_dm_behavior: ignore`。 |
---

## 安全性

:::warning
**在正式上线前请务必配置访问控制**。通过 `WHATSAPP_ALLOWED_USERS` 设置特定的电话号码（包含国家代码，但不带 `+` 号），或者使用 `*` 允许所有人，也可以设置 `WHATSAPP_ALLOW_ALL_USERS=true`。作为安全保护措施，如果没有进行上述任何配置，网关将**拒绝所有传入消息**。
:::

默认情况下，未授权的私聊（DM）仍会收到包含配对码的回复。如果你希望私人的 WhatsApp 号码对陌生人保持完全静默，请设置：

```yaml
whatsapp:
  unauthorized_dm_behavior: ignore
```

- `~/.hermes/platforms/whatsapp/session` 目录包含完整的会话凭据 —— 请像保护密码一样保护它。
- 设置文件权限：`chmod 700 ~/.hermes/platforms/whatsapp/session`。
- 为 Bot 使用**专用电话号码**，以隔离个人账号的风险。
- 如果怀疑账号被盗，请通过 WhatsApp → 设置 → 已链接的设备（Linked Devices）取消设备关联。
- 日志中的电话号码会被部分脱敏，但仍请检查你的日志保留策略。
