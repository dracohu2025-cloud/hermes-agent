---
sidebar_position: 5
title: "WhatsApp 设置"
description: "通过内置的 Baileys 桥接器设置 Hermes Agent 为 WhatsApp 机器人"
---

# WhatsApp 设置

Hermes 通过一个基于 **Baileys** 的内置桥接器连接到 WhatsApp。这种方式模拟了一个 WhatsApp Web 会话，**不**通过官方的 WhatsApp Business API。无需 Meta 开发者账号或商业认证。

:::warning 非官方 API – 封号风险
WhatsApp **不**官方支持 Business API 之外的第三方机器人。使用第三方桥接器存在账号受限的小风险。为降低风险：
- **为机器人使用一个专用电话号码**（不要用你的个人号码）
- **不要发送批量/垃圾消息** – 保持使用方式是对话式的
- **不要自动化发送消息给未主动发消息的人**
:::

:::warning WhatsApp Web 协议更新
WhatsApp 会定期更新其 Web 协议，这可能暂时破坏与第三方桥接器的兼容性。当这种情况发生时，Hermes 会更新桥接器依赖。如果机器人因 WhatsApp 更新而停止工作，请拉取最新的 Hermes 版本并重新配对。
:::

## 两种模式

| 模式 | 工作原理 | 适用场景 |
|------|-------------|----------|
| **独立的机器人号码** (推荐) | 为机器人分配一个电话号码。人们直接向该号码发送消息。 | 用户体验清晰，多用户，封号风险较低 |
| **个人自聊天** | 使用你自己的 WhatsApp。你向自己发送消息来与 Agent 对话。 | 快速设置，单用户，测试 |

---

## 前提条件

- **Node.js v18+** 和 **npm** – WhatsApp 桥接器作为一个 Node.js 进程运行
- **一部安装了 WhatsApp 的手机**（用于扫描二维码）

与旧版基于浏览器的桥接器不同，当前基于 Baileys 的桥接器**不**需要本地 Chromium 或 Puppeteer 依赖栈。

---

## 步骤 1：运行设置向导

```bash
hermes whatsapp
```

向导将：

1. 询问你想要哪种模式 (**bot** 或 **self-chat**)
2. 如果需要则安装桥接器依赖
3. 在你的终端显示一个**二维码**
4. 等待你扫描它

**扫描二维码：**

1. 在你的手机上打开 WhatsApp
2. 进入 **Settings → Linked Devices**
3. 点击 **Link a Device**
4. 将你的摄像头对准终端上的二维码

一旦配对成功，向导会确认连接并退出。你的会话会自动保存。

:::tip
如果二维码看起来错乱，确保你的终端至少有 60 列宽并且支持 Unicode。你也可以尝试使用不同的终端模拟器。
:::

---

## 步骤 2：获取第二个电话号码 (Bot 模式)

对于 bot 模式，你需要一个尚未注册 WhatsApp 的电话号码。三个选项：

| 选项 | 成本 | 备注 |
|--------|------|-------|
| **Google Voice** | 免费 | 仅限美国。在 [voice.google.com](https://voice.google.com) 获取一个号码。通过 Google Voice 应用以短信方式验证 WhatsApp。 |
| **预付费 SIM 卡** | 一次性 $5–15 | 任何运营商。激活、验证 WhatsApp，然后 SIM 卡可以放在抽屉里。号码必须保持活跃状态（每 90 天打个电话）。 |
| **VoIP 服务** | 免费–$5/月 | TextNow, TextFree 或类似服务。一些 VoIP 号码被 WhatsApp 屏蔽 – 如果第一个不行就多试几个。 |

获取号码后：

1. 在一部手机上安装 WhatsApp (或在双 SIM 卡手机上使用 WhatsApp Business 应用)
2. 用这个新号码注册 WhatsApp
3. 运行 `hermes whatsapp` 并从那个 WhatsApp 账户扫描二维码

---

## 步骤 3：配置 Hermes

在你的 `~/.hermes/.env` 文件中添加以下内容：

```bash
# 必填项
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot                          # "bot" 或 "self-chat"
WHATSAPP_ALLOWED_USERS=15551234567         # 逗号分隔的电话号码 (带国家代码，不带 +)
```

在 `~/.hermes/config.yaml` 中的可选行为设置：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `unauthorized_dm_behavior: pair` 是全局默认值。未知的私聊发送者会收到一个配对码。
- `whatsapp.unauthorized_dm_behavior: ignore` 让 WhatsApp 对未经授权的私聊保持静默，这对于私用号码通常是更好的选择。

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅 Linux：开机启动的系统服务
```

网关会自动使用保存的会话启动 WhatsApp 桥接器。

---

## 会话持久性

Baileys 桥接器将其会话保存在 `~/.hermes/whatsapp/session` 下。这意味着：

- **会话在重启后保留** – 你不需要每次都重新扫描二维码
- 会话数据包括加密密钥和设备凭证
- **不要共享或提交此会话目录** – 它会授予对该 WhatsApp 账户的完全访问权

---

## 重新配对

如果会话中断（手机重置、WhatsApp 更新、手动取消关联），你将在网关日志中看到连接错误。修复方法：

```bash
hermes whatsapp
```

这会生成一个新的二维码。再次扫描它，会话就会被重新建立。网关会自动处理**临时**断开连接（网络波动、手机短暂离线）并通过重连逻辑恢复。

---

## 语音消息

Hermes 支持 WhatsApp 语音：

- **接收：** 语音消息 (`.ogg` opus) 会自动使用配置的 STT 提供商进行转录：本地 `faster-whisper`、Groq Whisper (`GROQ_API_KEY`) 或 OpenAI Whisper (`VOICE_TOOLS_OPENAI_KEY`)
- **发送：** TTS 回复作为 MP3 音频文件附件发送
- Agent 回复默认以 "⚕ **Hermes Agent**" 开头。你可以在 `config.yaml` 中自定义或禁用这个前缀：

```yaml
# ~/.hermes/config.yaml
whatsapp:
  reply_prefix: ""                          # 空字符串禁用头部
  # reply_prefix: "🤖 *My Bot*\n──────\n"  # 自定义前缀 (支持 \n 换行)
```

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| **二维码无法扫描** | 确保终端足够宽 (60+ 列)。尝试不同的终端。确保你从正确的 WhatsApp 账户（机器人号码，而非个人号码）扫描。 |
| **二维码过期** | 二维码约每 20 秒刷新一次。如果超时，重启 `hermes whatsapp`。 |
| **会话不持久化** | 检查 `~/.hermes/whatsapp/session` 是否存在且可写。如果容器化，将其作为持久化卷挂载。 |
| **意外退出登录** | WhatsApp 会在长时间不活动后取消关联设备。保持手机在线并连接到网络，如果需要则用 `hermes whatsapp` 重新配对。 |
| **桥接器崩溃或重连循环** | 重启网关，更新 Hermes，如果会话因 WhatsApp 协议更改而失效则重新配对。 |
| **WhatsApp 更新后机器人停止工作** | 更新 Hermes 以获得最新的桥接器版本，然后重新配对。 |
| **macOS: "Node.js not installed" 但终端中 node 正常工作** | launchd 服务不会继承你的 shell PATH。运行 `hermes gateway install` 将你当前的 PATH 重新快照到 plist 中，然后运行 `hermes gateway start`。详情请参阅 [Gateway Service 文档](./index.md#macos-launchd)。 |
| **消息未被接收** | 验证 `WHATSAPP_ALLOWED_USERS` 包含发送者的号码（带国家代码，不带 `+` 或空格）。 |
| **机器人向陌生人回复配对码** | 如果你希望未经授权的私聊被静默忽略，请在 `~/.hermes/config.yaml` 中设置 `whatsapp.unauthorized_dm_behavior: ignore`。 |

---

## 安全性

:::warning
**务必设置 `WHATSAPP_ALLOWED_USERS`** 包含授权用户的电话号码（包括国家代码，不带 `+`）。没有此设置，网关将**拒绝所有接收的消息**作为一种安全措施。
:::

默认情况下，未经授权的私聊仍然会收到配对码回复。如果你想让私用的 WhatsApp 号码对陌生人保持完全静默，请设置：

```yaml
whatsapp:
  unauthorized_dm_behavior: ignore
```

- `~/.hermes/whatsapp/session` 目录包含完整的会话凭证 – 要像密码一样保护它
- 设置文件权限： `chmod 700 ~/.hermes/whatsapp/session`
- 为机器人使用一个**专用电话号码**，以将风险与你的个人账户隔离
- 如果你怀疑被入侵，请在 WhatsApp → Settings → Linked Devices 中取消关联设备
- 日志中的电话号码会被部分遮蔽，但请检查你的日志保留策略
