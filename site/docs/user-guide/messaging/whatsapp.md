---
sidebar_position: 5
title: "WhatsApp"
description: "通过内置的 Baileys 桥接，将 Hermes Agent 设置为 WhatsApp 机器人"
---

# WhatsApp 设置

Hermes 通过一个基于 **Baileys** 的内置桥接连接到 WhatsApp。其工作原理是模拟一个 WhatsApp Web 会话 —— **并非**通过官方的 WhatsApp Business API。不需要 Meta 开发者账户或商业验证。

:::warning 非官方 API —— 封号风险
WhatsApp **并不**正式支持 Business API 之外的第三方机器人。使用第三方桥接存在一定的账户限制风险。为降低风险：
- 为机器人使用一个**专用的电话号码**（不要使用你的个人号码）
- **不要发送批量/垃圾消息** —— 保持使用方式为对话性质
- **不要主动向未先发送消息的人自动化发送消息**
:::

:::warning WhatsApp Web 协议更新
WhatsApp 会定期更新其 Web 协议，这可能会暂时破坏与第三方桥接的兼容性。
当这种情况发生时，Hermes 会更新桥接依赖项。如果机器人
在 WhatsApp 更新后停止工作，请拉取最新的 Hermes 版本并重新配对。
:::

## 两种模式

| 模式 | 工作原理 | 最适合 |
|------|-------------|----------|
| **独立的机器人号码**（推荐） | 将一个电话号码专用于机器人。用户直接向该号码发送消息。 | 用户体验干净，多用户使用，降低封号风险 |
| **个人自聊模式** | 使用你自己的 WhatsApp。你给自己发送消息以与 Agent 对话。 | 快速设置，单用户使用，测试 |

---

## 前提条件

- **Node.js v18+** 和 **npm** —— WhatsApp 桥接作为一个 Node.js 进程运行
- **一部安装了 WhatsApp** 的手机（用于扫描二维码）

与旧版基于浏览器的桥接不同，当前的基于 Baileys 的桥接**不需要**本地 Chromium 或 Puppeteer 依赖栈。

---

## 步骤 1: 运行设置向导

```bash
hermes whatsapp
```

向导将会：

1. 询问你想要哪种模式（**机器人**或**自聊**）
2. 如果需要，安装桥接依赖项
3. 在你的终端中显示一个**二维码**
4. 等待你扫描它

**扫描二维码：**

1. 在你的手机上打开 WhatsApp
2. 进入 **设置 → 已连接的设备**
3. 点击 **连接设备**
4. 将你的摄像头对准终端中的二维码

配对成功后，向导会确认连接并退出。你的会话会自动保存。

:::tip
如果二维码显示混乱，请确保你的终端至少 60 列宽并支持
Unicode。你也可以尝试使用不同的终端模拟器。
:::

---

## 步骤 2: 获取第二个电话号码（机器人模式）

对于机器人模式，你需要一个尚未注册 WhatsApp 的电话号码。有三种选择：

| 选项 | 成本 | 备注 |
|--------|------|-------|
| **Google Voice** | 免费 | 仅限美国。在 [voice.google.com](https://voice.google.com) 获取号码。通过 Google Voice 应用程序接收短信验证 WhatsApp。 |
| **预付 SIM 卡** | $5–15 一次性 | 任何运营商。激活，验证 WhatsApp，然后 SIM 卡可以闲置在抽屉里。号码必须保持活跃状态（每 90 天打个电话）。 |
| **VoIP 服务** | 免费–$5/月 | TextNow、TextFree 或类似服务。一些 VoIP 号码被 WhatsApp 屏蔽 —— 如果第一个不行，可以试几个。 |

获取号码后：

1. 在手机上安装 WhatsApp（或使用支持双 SIM 卡的 WhatsApp Business 应用程序）
2. 用 WhatsApp 注册新号码
3. 运行 `hermes whatsapp` 并从该 WhatsApp 账户扫描二维码

---

## 步骤 3: 配置 Hermes

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot                          # "bot" 或 "self-chat"

# 访问控制 —— 选择以下**一种**选项：
WHATSAPP_ALLOWED_USERS=15551234567         # 逗号分隔的电话号码（带国家代码，不加 +）
# WHATSAPP_ALLOWED_USERS=*                 # 或者使用 * 允许所有人
# WHATSAPP_ALLOW_ALL_USERS=true            # 或者设置此标志（效果与 * 相同）
```

:::tip 允许所有人的快捷方式
设置 `WHATSAPP_ALLOWED_USERS=*` 允许**所有**发送者（等同于 `WHATSAPP_ALLOW_ALL_USERS=true`）。
这与 [Signal 群组允许列表](/reference/environment-variables) 保持一致。
要使用配对流程代替，请移除这两个变量并依赖
[DM 配对系统](/user-guide/security#dm-pairing-system)。
:::

可选的行为设置在 `~/.hermes/config.yaml` 中：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- `unauthorized_dm_behavior: pair` 是全局默认设置。未知的 DM 发送者会收到配对码。
- `whatsapp.unauthorized_dm_behavior: ignore` 会让 WhatsApp 对未经授权的 DM 保持静默，这对于一个私人号码通常是更好的选择。

然后启动网关：

```bash
hermes gateway              # 前台运行
hermes gateway install      # 安装为用户服务
sudo hermes gateway install --system   # 仅限 Linux：开机启动的系统服务
```

网关会自动使用保存的会话启动 WhatsApp 桥接。

---

## 会话持久性

Baileys 桥接将其会话保存在 `~/.hermes/platforms/whatsapp/session` 下。这意味着：

- **会话在重启后保留** —— 你不需要每次都重新扫描二维码
- 会话数据包含加密密钥和设备凭证
- **不要分享或提交此会话目录** —— 它授予对 WhatsApp 账户的完全访问权限

---

## 重新配对

如果会话中断（手机重置、WhatsApp 更新、手动断开连接），你会在网关日志中看到连接
错误。修复方法：

```bash
hermes whatsapp
```

这将生成一个新的二维码。再次扫描它，会话将被重新建立。网关
通过重连逻辑自动处理**临时**断开连接（网络波动、手机短暂离线）。

---

## 语音消息

Hermes 支持 WhatsApp 的语音功能：

- **接收：** 语音消息（`.ogg` opus）会自动使用配置的 STT 提供商转录：本地 `faster-whisper`、Groq Whisper（`GROQ_API_KEY`）或 OpenAI Whisper（`VOICE_TOOLS_OPENAI_KEY`）
- **发送：** TTS 回复以 MP3 音频文件附件的形式发送
- Agent 回复默认前缀为 "⚕ **Hermes Agent**"。你可以在 `config.yaml` 中自定义或禁用此功能：

```yaml
# ~/.hermes/config.yaml
whatsapp:
  reply_prefix: ""                          # 空字符串禁用标题
  # reply_prefix: "🤖 *My Bot*\n──────\n"  # 自定义前缀（支持 \n 换行）
```

---

## 消息格式与发送

WhatsApp 支持**流式（渐进式）回复** —— 机器人会在 AI 生成文本时实时编辑其消息，就像 Discord 和 Telegram 一样。在内部，WhatsApp 被归类为 TIER_MEDIUM 平台，以衡量其发送能力。

### 分块

长回复会自动按每块 **4,096 字符**（WhatsApp 的实际显示限制）拆分为多条消息。你不需要配置任何东西 —— 网关会处理拆分并顺序发送块。

### WhatsApp 兼容的 Markdown

AI 回复中的标准 Markdown 会自动转换为 WhatsApp 的原生格式：

| Markdown | WhatsApp | 渲染结果 |
|----------|----------|------------|
| `**bold**` | `*bold*` | **bold** |
| `~~strikethrough~~` | `~strikethrough~` | ~~strikethrough~~ |
| `# Heading` | `*Heading*` | 粗体文本（没有原生标题） |
| `[link text](url)` | `link text (url)` | 内联 URL |

代码块和内联代码会原样保留，因为 WhatsApp 原生支持三重反引号格式。

### 工具进度

当 Agent 调用工具（网络搜索、文件操作等）时，WhatsApp 会显示实时进度指示器，显示正在运行的工具。默认启用 —— 无需配置。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| **二维码无法扫描** | 确保终端足够宽（60+列）。尝试不同的终端。确保你从正确的 WhatsApp 账户（机器人号码，而非个人号码）扫描。 |
| **二维码过期** | 二维码大约每 20 秒刷新一次。如果超时，重启 `hermes whatsapp`。 |
| **会话无法持久化** | 检查 `~/.hermes/platforms/whatsapp/session` 是否存在并可写。如果是容器化环境，将其作为持久卷挂载。 |
| **意外注销** | WhatsApp 在长时间不活动后会断开设备连接。保持手机开机并连接到网络，如果需要则用 `hermes whatsapp` 重新配对。 |
| **桥接崩溃或重连循环** | 重启网关，更新 Hermes，如果会话因 WhatsApp 协议变更而失效则重新配对。 |
| **WhatsApp 更新后机器人停止工作** | 更新 Hermes 以获得最新的桥接版本，然后重新配对。 |
| **macOS: “Node.js 未安装” 但终端中 node 正常工作** | launchd 服务不继承你的 shell PATH。运行 `hermes gateway install` 将你当前的 PATH 重新快照到 plist 中，然后 `hermes gateway start`。详情参见 [Gateway Service 文档](./index.md#macos-launchd)。 |
| **消息未被接收** | 验证 `WHATSAPP_ALLOWED_USERS` 包含发送者的号码（带国家代码，不加 `+` 或空格），或将其设置为 `*` 允许所有人。在 `.env` 中设置 `WHATSAPP_DEBUG=true` 并重启网关，在 `bridge.log` 中查看原始消息事件。 |
| **机器人向陌生人回复配对码** | 如果你想未经授权的 DM 被静默忽略，请在 `~/.hermes/config.yaml` 中设置 `whatsapp.unauthorized_dm_behavior: ignore`。 |
---

## 安全

:::warning
上线前请务必**配置访问控制**。设置 `WHATSAPP_ALLOWED_USERS` 为特定的电话号码（包含国家代码，不带 `+`），使用 `*` 允许所有人，或者设置 `WHATSAPP_ALLOW_ALL_USERS=true`。如果以上均未设置，网关将**拒绝所有传入消息**，这是一项安全措施。
:::

默认情况下，未经授权的私信仍会收到配对码回复。如果你希望私人的 WhatsApp 号码对陌生人完全保持静默，请设置：

```yaml
whatsapp:
  unauthorized_dm_behavior: ignore
```

- `~/.hermes/platforms/whatsapp/session` 目录包含完整的会话凭据——请像保护密码一样保护它
- 设置文件权限：`chmod 700 ~/.hermes/platforms/whatsapp/session`
- 为机器人使用一个**专用的电话号码**，以隔离与你个人账户相关的风险
- 如果怀疑账户已泄露，请在 WhatsApp 的“设置” → “已链接的设备”中取消链接该设备
- 日志中的电话号码会被部分隐藏，但仍需审查你的日志保留策略
