---
sidebar_position: 5
title: "WhatsApp"
description: "通过内置的 Baileys 桥接将 Hermes Agent 设置为 WhatsApp 机器人"
---

# WhatsApp 设置

Hermes 通过基于 **Baileys** 的内置桥接连接到 WhatsApp。它通过模拟 WhatsApp Web 会话来工作——**不是**通过官方的 WhatsApp Business API。无需 Meta 开发者账号或企业验证。

:::warning 非官方 API — 封号风险
WhatsApp **不**官方支持 Business API 以外的第三方机器人。使用第三方桥接存在账号被限制的风险。为降低风险：
- **使用专用的电话号码** 作为机器人号码（不要用个人号码）
- **不要发送群发/垃圾消息** — 保持对话式使用
- **不要自动向未先发消息的人发送消息**
:::

:::warning WhatsApp Web 协议更新
WhatsApp 会定期更新其 Web 协议，这可能会暂时导致第三方桥接不兼容。
遇到这种情况时，Hermes 会更新桥接依赖。如果 WhatsApp 更新后机器人停止工作，请拉取最新 Hermes 版本并重新配对。
:::

## 两种模式

| 模式 | 工作方式 | 适用场景 |
|------|----------|----------|
| **独立机器人号码**（推荐） | 给机器人专门分配一个电话号码。用户直接给该号码发消息。 | 用户体验干净，支持多用户，封号风险较低 |
| **个人自聊** | 使用你自己的 WhatsApp。你给自己发消息与 Agent 对话。 | 快速设置，单用户，测试用途 |

---

## 前置条件

- **Node.js v18+** 和 **npm** — WhatsApp 桥接作为 Node.js 进程运行
- **安装了 WhatsApp 的手机**（用于扫描二维码）

与旧版基于浏览器的桥接不同，当前基于 Baileys 的桥接**不**需要本地 Chromium 或 Puppeteer 依赖。

---

## 第 1 步：运行设置向导

```bash
hermes whatsapp
```

向导会：

1. 询问你想用哪种模式（**bot** 或 **self-chat**）
2. 如有需要，安装桥接依赖
3. 在终端显示一个 **二维码**
4. 等待你扫码

**扫码步骤：**

1. 打开手机上的 WhatsApp
2. 进入 **设置 → 已连接的设备**
3. 点击 **连接设备**
4. 用手机摄像头对准终端上的二维码

配对成功后，向导会确认连接并退出。会话会自动保存。

:::tip
如果二维码显示乱码，确保你的终端宽度至少 60 列且支持 Unicode。也可以尝试换个终端模拟器。
:::

---

## 第 2 步：获取第二个电话号码（机器人模式）

机器人模式需要一个未注册 WhatsApp 的电话号码。三种选择：

| 选项 | 费用 | 说明 |
|--------|------|-------|
| **Google Voice** | 免费 | 仅限美国。可在 [voice.google.com](https://voice.google.com) 获取号码。通过 Google Voice 应用接收短信验证 WhatsApp。 |
| **预付费 SIM 卡** | 一次性 5–15 美元 | 任何运营商。激活后验证 WhatsApp，之后 SIM 卡可以放着不用。号码必须保持活跃（每 90 天打一次电话）。 |
| **VoIP 服务** | 免费–每月 5 美元 | TextNow、TextFree 等。有些 VoIP 号码会被 WhatsApp 屏蔽——如果第一个不行，可以试几个。 |

拿到号码后：

1. 在手机上安装 WhatsApp（或使用支持双 SIM 的 WhatsApp Business 应用）
2. 用新号码注册 WhatsApp
3. 运行 `hermes whatsapp` 并用该 WhatsApp 账号扫码

---

## 第 3 步：配置 Hermes

在你的 `~/.hermes/.env` 文件中添加：

```bash
# 必填
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot                          # "bot" 或 "self-chat"

# 访问控制 — 选择以下之一：
WHATSAPP_ALLOWED_USERS=15551234567         # 逗号分隔的电话号码（带国家码，不带+号）
# WHATSAPP_ALLOWED_USERS=*                 # 或使用 * 允许所有人
# WHATSAPP_ALLOW_ALL_USERS=true            # 或设置此标志（效果同上）
```

:::tip 允许所有人的简写
设置 `WHATSAPP_ALLOWED_USERS=*` 允许**所有**发送者（等同于 `WHATSAPP_ALLOW_ALL_USERS=true`）。
这与 [Signal 群组白名单](/reference/environment-variables) 保持一致。
如果想用配对流程，删除这两个变量，改用
[私信配对系统](/user-guide/security#dm-pairing-system)。
:::

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `unauthorized_dm_behavior: pair` 是全局默认。未知私信发送者会收到配对码。
- `whatsapp.unauthorized_dm_behavior: ignore` 让 WhatsApp 对未授权私信保持沉默，通常对私人号码更合适。

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅限 Linux：开机启动系统服务
```

网关会自动使用保存的会话启动 WhatsApp 桥接。

---

## 会话持久化

Baileys 桥接会话保存在 `~/.hermes/whatsapp/session`。这意味着：

- **会话可跨重启保存** — 不用每次都重新扫码
- 会话数据包含加密密钥和设备凭证
- **不要分享或提交此会话目录** — 它能完全访问 WhatsApp 账号

---

## 重新配对

如果会话失效（手机重置、WhatsApp 更新、手动解绑），网关日志会显示连接错误。解决方法：

```bash
hermes whatsapp
```

这会生成新的二维码。重新扫码即可恢复会话。网关会自动处理**临时**断线（网络波动、手机短暂离线）并自动重连。

---

## 语音消息

Hermes 支持 WhatsApp 语音：

- **接收：** 语音消息（`.ogg` opus 格式）会自动用配置的语音识别服务转录：本地 `faster-whisper`、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）
- **发送：** TTS 回复会以 MP3 音频文件附件形式发送
- Agent 回复默认带有前缀 "⚕ **Hermes Agent**"。你可以在 `config.yaml` 中自定义或关闭：

```yaml
# ~/.hermes/config.yaml
whatsapp:
  reply_prefix: ""                          # 设为空字符串关闭前缀
  # reply_prefix: "🤖 *My Bot*\n──────\n"  # 自定义前缀（支持 \n 换行）
```

---

## 故障排查

| 问题 | 解决方案 |
|---------|----------|
| **二维码无法扫描** | 确保终端宽度足够（60 列以上）。尝试换终端。确认扫码的是正确的 WhatsApp 账号（机器人号码，不是个人号）。 |
| **二维码过期** | 二维码大约每 20 秒刷新一次。超时后重启 `hermes whatsapp`。 |
| **会话无法保存** | 检查 `~/.hermes/whatsapp/session` 是否存在且可写。如果在容器中运行，挂载为持久卷。 |
| **意外登出** | WhatsApp 长时间不活跃会解绑设备。保持手机开机并联网，必要时重新配对 `hermes whatsapp`。 |
| **桥接崩溃或重连循环** | 重启网关，更新 Hermes，若会话因 WhatsApp 协议变更失效，重新配对。 |
| **WhatsApp 更新后机器人停止工作** | 更新 Hermes 以获取最新桥接版本，然后重新配对。 |
| **macOS：提示“未安装 Node.js”但终端能用 node** | launchd 服务不会继承你的 shell PATH。运行 `hermes gateway install` 重新快照当前 PATH 到 plist，然后 `hermes gateway start`。详见 [网关服务文档](./index.md#macos-launchd)。 |
| **消息未收到** | 确认 `WHATSAPP_ALLOWED_USERS` 包含发送者号码（带国家码，无 `+` 或空格），或设置为 `*` 允许所有人。设置 `.env` 中 `WHATSAPP_DEBUG=true` 并重启网关，可在 `bridge.log` 查看原始消息事件。 |
| **机器人回复陌生人配对码** | 如果想让未授权私信静默忽略，设置 `whatsapp.unauthorized_dm_behavior: ignore` 于 `~/.hermes/config.yaml`。 |

---

## 安全
:::warning
**上线前请配置访问控制**。设置 `WHATSAPP_ALLOWED_USERS`，指定具体的电话号码（包含国家码，不带 `+`），也可以用 `*` 允许所有人，或者设置 `WHATSAPP_ALLOW_ALL_USERS=true`。如果没有设置这些，网关会出于安全考虑**拒绝所有传入消息**。
:::

默认情况下，未授权的私信仍会收到配对码回复。如果你希望 WhatsApp 号码对陌生人完全保持静默，请设置：

```yaml
whatsapp:
  unauthorized_dm_behavior: ignore
```

- `~/.hermes/whatsapp/session` 目录包含完整的会话凭证——请像保护密码一样保护它
- 设置文件权限：`chmod 700 ~/.hermes/whatsapp/session`
- 使用**专用电话号码**给机器人，避免影响你的个人账号
- 如果怀疑账号被泄露，去 WhatsApp → 设置 → 已连接设备，解除设备绑定
- 日志中的电话号码会部分脱敏，但请审查你的日志保留策略
