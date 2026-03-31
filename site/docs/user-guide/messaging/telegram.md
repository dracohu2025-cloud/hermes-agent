---
sidebar_position: 1
title: "Telegram 设置"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

# Telegram 设置

Hermes Agent 与 Telegram 集成，成为一个功能完整的对话机器人。连接后，你可以在任何设备上与你的智能体聊天，发送会自动转录的语音备忘录，接收定时任务结果，并在群聊中使用智能体。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/)，支持文本、语音、图片和文件附件。

## 步骤 1：通过 BotFather 创建机器人

每个 Telegram 机器人都需要一个由 Telegram 官方机器人管理工具 [@BotFather](https://t.me/BotFather) 颁发的 API 令牌。

1.  打开 Telegram，搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2.  发送 `/newbot`
3.  选择一个**显示名称**（例如，“Hermes Agent”）—— 可以是任何名称
4.  选择一个**用户名** —— 必须是唯一的，并以 `bot` 结尾（例如，`my_hermes_bot`）
5.  BotFather 会回复你的 **API 令牌**。它看起来像这样：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请保管好你的机器人令牌。任何拥有此令牌的人都可以控制你的机器人。如果泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。
:::

## 步骤 2：自定义你的机器人（可选）

这些 BotFather 命令可以改善用户体验。给 @BotFather 发消息并使用：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始聊天前显示的“这个机器人能做什么？”文本 |
| `/setabouttext` | 机器人个人资料页面上的简短文本 |
| `/setuserpic` | 为你的机器人上传头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否能看到所有群组消息（见步骤 3） |

:::tip
对于 `/setcommands`，一个有用的初始集合：

```
help - 显示帮助信息
new - 开始新对话
sethome - 将此聊天设置为家庭频道
```
:::

## 步骤 3：隐私模式（群组使用关键） {#step-3-privacy-mode-critical-for-groups}

Telegram 机器人有一个**隐私模式**，**默认是启用的**。这是在群组中使用机器人时最常见的困惑来源。

**隐私模式开启时**，你的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自身消息的消息
- 服务消息（成员加入/离开、置顶消息等）
- 机器人是管理员的频道中的消息

**隐私模式关闭时**，机器人会接收群组中的每一条消息。

### 如何禁用隐私模式

1.  给 **@BotFather** 发消息
2.  发送 `/mybots`
3.  选择你的机器人
4.  进入 **Bot Settings → Group Privacy → Turn off**

:::warning
**更改隐私设置后，你必须从任何群组中移除并重新添加机器人**。Telegram 在机器人加入群组时会缓存隐私状态，直到机器人被移除并重新添加才会更新。
:::

:::tip
禁用隐私模式的替代方案：将机器人提升为**群组管理员**。管理员机器人无论隐私设置如何，总是能接收所有消息，这样就无需切换全局隐私模式。
:::

## 步骤 4：找到你的用户 ID

Hermes Agent 使用数字形式的 Telegram 用户 ID 来控制访问权限。你的用户 ID **不是**你的用户名 —— 它是一个像 `123456789` 这样的数字。

**方法 1（推荐）：** 给 [@userinfobot](https://t.me/userinfobot) 发消息 —— 它会立即回复你的用户 ID。

**方法 2：** 给 [@get_id_bot](https://t.me/get_id_bot) 发消息 —— 另一个可靠的选择。

保存这个数字；下一步你会需要它。

## 步骤 5：配置 Hermes

### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

提示时选择 **Telegram**。向导会询问你的机器人令牌和允许的用户 ID，然后为你写入配置。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # 多个用户用逗号分隔
```

### 启动网关

```bash
hermes gateway
```

机器人应在几秒钟内上线。在 Telegram 上给它发条消息来验证。

## 家庭频道

在任何 Telegram 聊天（私聊或群组）中使用 `/sethome` 命令，将其指定为**家庭频道**。定时任务（cron 作业）会将结果发送到此频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="我的笔记"
```

:::tip
群组聊天 ID 是负数（例如，`-1001234567890`）。你的个人私聊 ID 与你的用户 ID 相同。
:::

## 语音消息

### 接收语音（语音转文本）

你在 Telegram 上发送的语音消息会被 Hermes 配置的 STT 提供商自动转录，并以文本形式注入到对话中。

- `local` 使用运行 Hermes 的机器上的 `faster-whisper` —— 无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

### 发送语音（文本转语音）

当智能体通过 TTS 生成音频时，它会以 Telegram 原生的**语音气泡**形式发送 —— 那种圆形的、可内联播放的类型。

- **OpenAI 和 ElevenLabs** 原生生成 Opus —— 无需额外设置
- **Edge TTS**（默认的免费提供商）输出 MP3，需要 **ffmpeg** 来转换为 Opus：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

没有 ffmpeg，Edge TTS 音频会作为普通音频文件发送（仍然可播放，但使用矩形播放器而不是语音气泡）。

在你的 `config.yaml` 中的 `tts.provider` 键下配置 TTS 提供商。

## 群聊使用

Hermes Agent 可以在 Telegram 群聊中工作，但需注意以下几点：

- **隐私模式**决定了机器人能看到哪些消息（见[步骤 3](#step-3-privacy-mode-critical-for-groups)）
- `TELEGRAM_ALLOWED_USERS` 仍然适用 —— 即使在群组中，也只有授权用户才能触发机器人
- 你可以通过 `telegram.require_mention: true` 来防止机器人响应普通的群聊闲聊
- 当 `telegram.require_mention: true` 时，群组消息在以下情况下会被接受：
  - 斜杠命令
  - 回复机器人消息之一
  - `@botusername` 提及
  - 匹配你在 `telegram.mention_patterns` 中配置的正则表达式唤醒词之一
- 如果 `telegram.require_mention` 未设置或为 false，Hermes 会保持之前的开放群组行为，并响应它能看到的普通群组消息

### 群组触发配置示例

将此添加到 `~/.hermes/config.yaml`：

```yaml
telegram:
  require_mention: true
  mention_patterns:
    - "^\\s*chompy\\b"
```

这个示例允许所有通常的直接触发方式，以及以 `chompy` 开头的消息，即使它们没有使用 `@提及`。

### 关于 `mention_patterns` 的说明

- 模式使用 Python 正则表达式
- 匹配不区分大小写
- 模式会同时检查文本消息和媒体标题
- 无效的正则表达式模式会被忽略，并在网关日志中发出警告，而不是使机器人崩溃
- 如果你希望模式只在消息开头匹配，请用 `^` 锚定它

## 私聊话题（Bot API 9.4） {#private-chat-topics-bot-api-94}

Telegram Bot API 9.4（2026 年 2 月）引入了**私聊话题** —— 机器人可以直接在 1 对 1 私聊中创建论坛风格的话题线程，无需超级群组。这让你可以在与 Hermes 的现有私聊中运行多个独立的工作空间。

### 使用场景

如果你同时处理几个长期项目，话题可以保持它们的上下文分离：

- **话题“网站”** —— 处理你的生产网络服务
- **话题“研究”** —— 文献综述和论文探索
- **话题“通用”** —— 杂项任务和快速问题

每个话题都有自己的对话会话、历史和上下文 —— 与其他话题完全隔离。

### 配置

在 `~/.hermes/config.yaml` 的 `platforms.telegram.extra.dm_topics` 下添加话题：

```yaml
platforms:
  telegram:
    extra:
      dm_topics:
      - chat_id: 123456789        # 你的 Telegram 用户 ID
        topics:
        - name: General
          icon_color: 7322096
        - name: Website
          icon_color: 9367192
        - name: Research
          icon_color: 16766590
          skill: arxiv              # 在此话题中自动加载一个技能
```

**字段：**

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 话题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 话题图标的自定义表情符号 ID |
| `skill` | 否 | 在此话题中开始新会话时自动加载的技能 |
| `thread_id` | 否 | 话题创建后自动填充 —— 不要手动设置 |

### 工作原理

1.  网关启动时，Hermes 为每个还没有 `thread_id` 的话题调用 `createForumTopic`
2.  `thread_id` 会自动保存回 `config.yaml` —— 后续重启会跳过 API 调用
3.  每个话题映射到一个独立的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4.  每个话题中的消息都有自己的对话历史、内存刷新和上下文窗口

### 技能绑定

带有 `skill` 字段的话题，在该话题中开始新会话时会自动加载该技能。这完全像在对话开始时输入 `/skill-name` 一样 —— 技能内容被注入到第一条消息中，后续消息会在对话历史中看到它。

例如，一个带有 `skill: arxiv` 的话题，每当其会话重置时（由于空闲超时、每日重置或手动 `/reset`），都会预加载 arxiv 技能。

:::tip
在配置之外创建的话题（例如，通过手动调用 Telegram API）会在 `forum_topic_created` 服务消息到达时自动被发现。你也可以在网关运行时将话题添加到配置中 —— 它们会在下一次缓存未命中时被拾取。
:::

## 近期 Bot API 功能

- **Bot API 9.4（2026 年 2 月）：** 私聊话题 —— 机器人可以通过 `createForumTopic` 在 1 对 1 私聊中创建论坛话题。见上文[私聊话题](#private-chat-topics-bot-api-94)。
- **隐私政策：** Telegram 现在要求机器人有隐私政策。通过 BotFather 的 `/setprivacy_policy` 设置一个，否则 Telegram 可能会自动生成一个占位符。如果你的机器人是面向公众的，这一点尤其重要。
- **消息流式传输：** Bot API 9.x 增加了对长响应流式传输的支持，这可以改善冗长智能体回复的感知延迟。

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 机器人完全不响应 | 验证 `TELEGRAM_BOT_TOKEN` 是否正确。检查 `hermes gateway` 日志中的错误。 |
| 机器人回复“未授权” | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。用 @userinfobot 再次确认。 |
| 机器人忽略群组消息 | 隐私模式很可能开启了。禁用它（步骤 3）或将机器人设为群组管理员。**记住更改隐私后要移除并重新添加机器人。** |
| 语音消息未转录 | 验证 STT 是否可用：为本地转录安装 `faster-whisper`，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件，不是气泡 | 安装 `ffmpeg`（Edge TTS Opus 转换所需）。 |
| 机器人令牌被撤销/无效 | 通过 BotFather 的 `/revoke` 然后 `/newbot` 或 `/token` 生成新令牌。更新你的 `.env` 文件。 |

## 执行批准

当智能体尝试运行一个可能危险的命令时，它会在聊天中向你请求批准：

> ⚠️ 此命令可能危险（递归删除）。回复“yes”以批准。

回复“yes”/“y”批准或“no”/“n”拒绝。

## 安全

:::warning
始终设置 `TELEGRAM_ALLOWED_USERS` 以限制谁可以与你的机器人交互。如果没有设置，网关会默认拒绝所有用户，作为一种安全措施。
:::

切勿公开分享你的机器人令牌。如果泄露，请立即通过 BotFather 的 `/revoke` 命令撤销它。

更多详情，请参阅[安全文档](/user-guide/security)。你也可以使用[私聊配对](/user-guide/messaging#dm-pairing-alternative-to-allowlists)来实现更动态的用户授权方法。
