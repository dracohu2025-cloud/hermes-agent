---
sidebar_position: 10
title: "语音模式"
description: "与 Hermes Agent 进行实时语音对话——CLI、Telegram、Discord（私聊、文本频道和语音频道）"
---

<a id="voice-mode"></a>
# 语音模式

Hermes Agent 支持在 CLI 和消息平台上进行完整的语音交互。通过麦克风与 Agent 对话，听取语音回复，并在 Discord 语音频道中进行实时语音对话。

如果你想要一份实用的设置指南，包含推荐配置和真实使用场景，请参阅 [使用 Hermes 的语音模式](/guides/use-voice-mode-with-hermes)。

<a id="prerequisites"></a>
## 前置条件

使用语音功能前，请确保你已完成以下步骤：

1. **已安装 Hermes Agent** — `pip install hermes-agent`（参见 [安装](/getting-started/installation)）
2. **已配置 LLM 提供商** — 运行 `hermes model`，或在 `~/.hermes/.env` 中设置首选提供商的凭证
3. **基础设置已正常工作** — 先运行 `hermes` 验证 Agent 能否以文本回复，之后再启用语音

:::tip
`~/.hermes/` 目录和默认的 `config.yaml` 会在你首次运行 `hermes` 时自动创建。只需手动创建 `~/.hermes/.env` 用于存放 API 密钥即可。
:::

<a id="overview"></a>
## 总览

| 功能 | 平台 | 描述 |
|------|------|------|
| **交互式语音** | CLI | 按 Ctrl+B 录音，Agent 自动检测静音并回复 |
| **自动语音回复** | Telegram, Discord | Agent 在文本回复的同时发送语音音频 |
| **语音频道** | Discord | Bot 加入语音频道，监听用户说话，并语音回复 |

<a id="requirements"></a>
## 要求

<a id="python-packages"></a>
### Python 包

```bash
# CLI 语音模式（麦克风 + 音频播放）
pip install "hermes-agent[voice]"

# Discord + Telegram 消息（包含 discord.py[voice] 以支持语音频道）
pip install "hermes-agent[messaging]"

# 高级 TTS（ElevenLabs）
pip install "hermes-agent[tts-premium]"

# 本地 TTS（NeuTTS，可选）
python -m pip install -U neutts[all]

# 一次性安装所有
pip install "hermes-agent[all]"
```

| 附加组件 | 包含的包 | 用途 |
|---------|----------|------|
| `voice` | `sounddevice`, `numpy` | CLI 语音模式 |
| `messaging` | `discord.py[voice]`, `python-telegram-bot`, `aiohttp` | Discord 和 Telegram Bot |
| `tts-premium` | `elevenlabs` | ElevenLabs TTS 提供商 |

可选的本地 TTS 提供商：单独使用 `python -m pip install -U neutts[all]` 安装 `neutts`。首次使用时会自动下载模型。

:::info
`discord.py[voice]` 会自动安装 **PyNaCl**（用于语音加密）和 **opus 绑定**。Discord 语音频道支持需要这些依赖。
:::

<a id="system-dependencies"></a>
### 系统依赖

```bash
# macOS
brew install portaudio ffmpeg opus
brew install espeak-ng   # 用于 NeuTTS

# Ubuntu/Debian
sudo apt install portaudio19-dev ffmpeg libopus0
sudo apt install espeak-ng   # 用于 NeuTTS
```

| 依赖项 | 用途 | 必须用于 |
|--------|------|----------|
| **PortAudio** | 麦克风输入和音频播放 | CLI 语音模式 |
| **ffmpeg** | 音频格式转换（MP3 → Opus, PCM → WAV） | 所有平台 |
| **Opus** | Discord 语音编解码器 | Discord 语音频道 |
| **espeak-ng** | 音素化后端 | 本地 NeuTTS 提供商 |

<a id="api-keys"></a>
### API 密钥

--- END TRANSLATED CHUNK ---
在 `~/.hermes/.env` 中添加：

```bash
# 语音转文字 — 本地提供程序完全不需要密钥
# pip install faster-whisper          # 免费，本地运行，推荐
GROQ_API_KEY=your-key                 # Groq Whisper — 快速，免费套餐（云端）
VOICE_TOOLS_OPENAI_KEY=your-key       # OpenAI Whisper — 付费（云端）

# 文字转语音（可选 — Edge TTS 和 NeuTTS 无需任何密钥即可工作）
ELEVENLABS_API_KEY=***           # ElevenLabs — 高品质
# 上面的 VOICE_TOOLS_OPENAI_KEY 也能启用 OpenAI TTS
```

:::tip
如果安装了 `faster-whisper`，语音模式在 STT 方面 **完全不需要任何 API 密钥**。模型（`base` 版本约 150 MB）会在首次使用时自动下载。
:::

---

<a id="cli-voice-mode"></a>
## CLI 语音模式

语音模式在**经典 CLI**（`hermes chat`）和**TUI**（`hermes --tui`）中均可使用。两者的行为完全一致——相同的斜杠命令、相同的 VAD 静音检测、相同的流式 TTS、相同的幻觉过滤器。TUI 还会额外将崩溃诊断日志转发到 `~/.hermes/logs/`，这样在异常音频后端上发生的按键通话失败，就可以附带完整堆栈信息报告，而不是静默消失。

<a id="quick-start"></a>
### 快速开始

启动 CLI 并启用语音模式：

```bash
hermes                # 启动交互式 CLI
```

然后在 CLI 内部使用这些命令：

```
/voice          切换语音模式开/关
/voice on       启用语音模式
/voice off      禁用语音模式
/voice tts      切换 TTS 输出
/voice status   显示当前状态
```

<a id="how-it-works"></a>
### 工作原理

1. 使用 `hermes` 启动 CLI，然后用 `/voice on` 启用语音模式
2. **按下 Ctrl+B** — 播放一声提示音（880Hz），开始录音
3. **说话** — 实时音频音量条会显示你的输入：`● [▁▂▃▅▇▇▅▂] ❯`
4. **停止说话** — 静默 3 秒后，录音自动停止
5. **两声提示音**（660Hz）确认录音结束
6. 音频通过 Whisper 转录并发送给 Agent
7. 如果启用了 TTS，Agent 的回复会被朗读出来
8. 录音**自动重新开始** — 无需按任何键即可再次说话

这个循环会持续进行，直到你在录音期间按下 **Ctrl+B**（退出连续模式）或连续 3 次录音未检测到语音。

:::tip
录音键可通过 `~/.hermes/config.yaml` 中的 `voice.record_key` 配置（默认：`ctrl+b`）。
:::

<a id="silence-detection"></a>
### 静音检测

两阶段算法检测你何时说完：

1. **语音确认** — 等待音频超过 RMS 阈值（200）至少 0.3 秒，容忍音节之间的短暂低谷
2. **结束检测** — 确认语音后，连续静默 3.0 秒触发结束

如果 15 秒内完全没有检测到语音，录音会自动停止。

`silence_threshold` 和 `silence_duration` 都可以在 `config.yaml` 中配置。你也可以用 `voice.beep_enabled: false` 禁用录音开始/结束提示音。

<a id="streaming-tts"></a>
### 流式 TTS

启用了 TTS 后，Agent 在生成文本时会**逐句**说出它的回复——你无需等待完整响应：

1. 将文本增量缓冲成完整句子（最少 20 个字符）
2. 去除 Markdown 格式和 `
<a id="hallucination-filter"></a>
### 幻觉过滤器

Whisper 有时会从静音或背景噪音中生成幻影文本（例如“感谢观看”、“订阅”等）。Agent 使用一组包含 26 种已知幻觉短语（涵盖多种语言）以及一个用于捕获重复变体的正则表达式模式来过滤掉这些内容。

---

<a id="gateway-voice-reply-telegram-discord"></a>
## 网关语音回复（Telegram 和 Discord）

如果你尚未设置消息机器人，请参阅特定平台的指南：
- [Telegram 设置指南](../messaging/telegram.md)
- [Discord 设置指南](../messaging/discord.md)

启动网关以连接到你的消息平台：

```bash
hermes gateway        # 启动网关（连接到已配置的平台）
hermes gateway setup  # 首次配置的交互式设置向导
```

<a id="discord-channels-vs-dms"></a>
### Discord：频道与私信

该机器人支持 Discord 上的两种交互模式：

| 模式 | 如何对话 | 是否需要提及 | 设置 |
|------|----------|-------------|------|
| **私信 (DM)** | 打开机器人资料 → “发送消息” | 否 | 立即可用 |
| **服务器频道** | 在机器人所在的文本频道中输入 | 是 (`@机器人名称`) | 机器人必须被邀请到服务器 |

**私信（推荐个人使用）：** 只需打开与机器人的私信并输入内容——无需 @提及。语音回复和所有命令与在频道中相同。

**服务器频道：** 机器人仅在你 @提及它时才会响应（例如 `@hermesbyt4 hello`）。请确保在提及弹出窗口中选择**机器人用户**，而不是同名的角色。

:::tip
要禁用服务器频道中的提及要求，请添加到 `~/.hermes/.env`：
```bash
DISCORD_REQUIRE_MENTION=false
```
或者将特定频道设置为自由回复（无需提及）：
```bash
DISCORD_FREE_RESPONSE_CHANNELS=123456789,987654321
```
:::

<a id="commands"></a>
### 命令

以下命令在 Telegram 和 Discord（私信和文本频道）中均有效：

```
/voice          切换语音模式开/关
/voice on       仅当你发送语音消息时进行语音回复
/voice tts      对所有消息进行语音回复
/voice off      禁用语音回复
/voice status   显示当前设置
```

<a id="modes"></a>
### 模式

| 模式 | 命令 | 行为 |
|------|------|------|
| `off` | `/voice off` | 仅文本（默认） |
| `voice_only` | `/voice on` | 仅当你发送语音消息时进行语音回复 |
| `all` | `/voice tts` | 对每条消息进行语音回复 |

语音模式设置会在网关重启后持久保留。

<a id="platform-delivery"></a>
### 平台投递

| 平台 | 格式 | 备注 |
|------|------|------|
| **Telegram** | 语音气泡 (Opus/OGG) | 在聊天中内联播放。如有需要，ffmpeg 会将 MP3 转换为 Opus |
| **Discord** | 原生语音气泡 (Opus/OGG) | 像用户语音消息一样内联播放。如果语音气泡 API 失败，则回退为文件附件 |

---

<a id="discord-voice-channels"></a>
## Discord 语音频道

最具沉浸感的语音功能：机器人加入 Discord 语音频道，监听用户说话，转录语音，通过 Agent 处理，然后在语音频道中回复语音。

<a id="setup"></a>
### 设置

<a id="1-discord-bot-permissions"></a>
#### 1. Discord 机器人权限

--- END DOCUMENT CHUNK ---
如果你已经为文字聊天设置好了一个 Discord 机器人（参见 [Discord 设置指南](../messaging/discord.md)），你需要添加语音权限。

前往 [Discord 开发者门户](https://discord.com/developers/applications) → 你的应用 → **安装** → **默认安装设置** → **公会安装**：

**在现有文字权限基础上添加以下权限：**

| 权限 | 用途 | 是否必需 |
|-----------|---------|----------|
| **连接** | 加入语音频道 | 是 |
| **说话** | 在语音频道中播放 TTS 音频 | 是 |
| **使用语音活动** | 检测用户是否在说话 | 推荐 |

**更新后的权限整数：**

| 级别 | 整数 | 包含内容 |
|-------|---------|----------|
| 仅文字 | `274878286912` | 查看频道、发送消息、阅读历史、嵌入、附件、线程、反应 |
| 文字 + 语音 | `274881432640` | 以上所有 + 连接、说话 |

**使用更新后的权限 URL 重新邀请机器人**：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274881432640
```

将 `YOUR_APP_ID` 替换为开发者门户中的应用程序 ID。

:::warning
将机器人重新邀请到它已经加入的服务器会更新其权限，而不会将其移除。你不会丢失任何数据或配置。
:::

<a id="2-privileged-gateway-intents"></a>
#### 2. 特权网关意图

在[开发者门户](https://discord.com/developers/applications) → 你的应用 → **机器人** → **特权网关意图**中，启用所有三个：

| 意图 | 用途 |
|--------|---------|
| **在线状态意图** | 检测用户在线/离线状态 |
| **服务器成员意图** | 将 `DISCORD_ALLOWED_USERS` 中的用户名解析为数字 ID（有条件） |
| **消息内容意图** | 读取频道中的文字消息内容 |

**消息内容意图**是必需的。**服务器成员意图**仅在 `DISCORD_ALLOWED_USERS` 列表使用用户名时才需要——如果你使用数字用户 ID，可以将其关闭。语音频道 SSRC → user_id 映射来自 Discord 语音 WebSocket 上的 SPEAKING 操作码，**不**需要服务器成员意图。

<a id="3-opus-codec"></a>
#### 3. Opus 编解码器

Opus 编解码器库必须安装在运行网关的机器上：

```bash
# macOS（Homebrew）
brew install opus

# Ubuntu/Debian
sudo apt install libopus0
```

机器人会自动从以下位置加载编解码器：
- **macOS：** `/opt/homebrew/lib/libopus.dylib`
- **Linux：** `libopus.so.0`

<a id="4-environment-variables"></a>
#### 4. 环境变量

```bash
# ~/.hermes/.env

# Discord 机器人（已为文字配置）
DISCORD_BOT_TOKEN=你的机器人令牌
DISCORD_ALLOWED_USERS=你的用户 ID

# STT — 本地提供者无需密钥（pip install faster-whisper）
# GROQ_API_KEY=你的密钥            # 替代方案：基于云，速度快，有免费层

# TTS — 可选。Edge TTS 和 NeuTTS 无需密钥。
# ELEVENLABS_API_KEY=***      # 高级质量
# VOICE_TOOLS_OPENAI_KEY=***  # OpenAI TTS / Whisper
```

<a id="start-the-gateway"></a>
### 启动网关

```bash
hermes gateway        # 使用现有配置启动
```

机器人应在几秒钟内上线 Discord。
<a id="commands"></a>
### 命令

在机器人所在的 Discord 文本频道中使用以下命令：

```
/voice join      机器人加入你当前的语音频道
/voice channel   /voice join 的别名
/voice leave     机器人断开语音频道连接
/voice status    显示语音模式及已连接的频道
```

:::info
运行 `/voice join` 之前，你必须先加入一个语音频道。机器人会加入与你相同的语音频道。
:::

<a id="how-it-works"></a>
### 工作原理

当机器人加入语音频道后，它会：

1. **听取** 每个用户的音频流，独立处理
2. **检测静音** — 至少 0.5 秒语音后跟随 1.5 秒静音，触发处理
3. **转录** 音频（通过 Whisper STT：本地、Groq 或 OpenAI）
4. **处理** 整个 Agent 管线（会话、工具、记忆）
5. **回复** 通过 TTS 在语音频道中朗读

<a id="text-channel-integration"></a>
### 文本频道集成

当机器人在语音频道中时：

- 转录内容会显示在文本频道中：`[Voice] @user: 你说了什么`
- Agent 的回复会以文本形式发送到频道，同时在语音频道中朗读
- 文本频道是执行 `/voice join` 的那个频道

<a id="echo-prevention"></a>
### 回声预防

机器人在播放 TTS 回复时会自动暂停音频监听，防止听到并重新处理自己的输出。

<a id="access-control"></a>
### 访问控制

只有列在 `DISCORD_ALLOWED_USERS` 中的用户才能通过语音交互。其他用户的音频会被静默忽略。

```bash
# ~/.hermes/.env
DISCORD_ALLOWED_USERS=284102345871466496
```

---

<a id="configuration-reference"></a>
## 配置参考

<a id="config-yaml"></a>
### config.yaml

```yaml
# 语音录制（CLI）
voice:
  record_key: "ctrl+b"            # 开始/停止录制的按键
  max_recording_seconds: 120       # 最大录制时长
  auto_tts: false                  # 语音模式启动时自动启用 TTS
  beep_enabled: true               # 录制开始/停止时播放提示音
  silence_threshold: 200           # RMS 电平（0-32767），低于此值视为静音
  silence_duration: 3.0            # 自动停止前的静音秒数

# 语音转文字
stt:
  enabled: true                     # 设为 false 可跳过自动转录 —
                                    # 网关仍会缓存音频文件，并将其路径作为入站消息的一部分传递给 Agent，
                                    # 适用于自定义管线（说话人分离、对齐、归档等）
  provider: "local"                  # "local"（免费）| "groq" | "openai"
  local:
    model: "base"                    # tiny, base, small, medium, large-v3
  # model: "whisper-1"              # 旧版：当 provider 未设置时使用

# 文字转语音
tts:
  provider: "edge"                 # "edge"（免费）| "elevenlabs" | "openai" | "neutts" | "minimax"
  edge:
    voice: "en-US-AriaNeural"      # 322 种语音，74 种语言
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"    # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"                 # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 可选：自托管或兼容 OpenAI 的端点时覆盖
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```
<a id="environment-variables"></a>
### 环境变量

```bash
# 语音转文字提供商（本地无需密钥）
# pip install faster-whisper        # 免费本地 STT — 无需 API 密钥
GROQ_API_KEY=...                    # Groq Whisper（快速，免费套餐）
VOICE_TOOLS_OPENAI_KEY=...         # OpenAI Whisper（付费）

# STT 高级覆盖设置（可选）
STT_GROQ_MODEL=whisper-large-v3-turbo    # 覆盖默认 Groq STT 模型
STT_OPENAI_MODEL=whisper-1               # 覆盖默认 OpenAI STT 模型
GROQ_BASE_URL=https://api.groq.com/openai/v1     # 自定义 Groq 端点
STT_OPENAI_BASE_URL=https://api.openai.com/v1    # 自定义 OpenAI STT 端点

# 文字转语音提供商（Edge TTS 和 NeuTTS 无需密钥）
ELEVENLABS_API_KEY=***             # ElevenLabs（顶级音质）
# 同时，上面的 VOICE_TOOLS_OPENAI_KEY 也为 OpenAI TTS 启用

# Discord 语音频道
DISCORD_BOT_TOKEN=...
DISCORD_ALLOWED_USERS=...
```

<a id="stt-provider-comparison"></a>
### STT 提供商对比

| 提供商 | 模型 | 速度 | 质量 | 费用 | API 密钥 |
|----------|-------|-------|---------|------|---------|
| **Local** | `base` | 快（取决于 CPU/GPU） | 好 | 免费 | 否 |
| **Local** | `small` | 中等 | 更好 | 免费 | 否 |
| **Local** | `large-v3` | 慢 | 最好 | 免费 | 否 |
| **Groq** | `whisper-large-v3-turbo` | 非常快（~0.5 秒） | 好 | 免费套餐 | 是 |
| **Groq** | `whisper-large-v3` | 快（~1 秒） | 更好 | 免费套餐 | 是 |
| **OpenAI** | `whisper-1` | 快（~1 秒） | 好 | 付费 | 是 |
| **OpenAI** | `gpt-4o-transcribe` | 中等（~2 秒） | 最好 | 付费 | 是 |

提供商优先级（自动回退）：**local** > **groq** > **openai**

<a id="tts-provider-comparison"></a>
### TTS 提供商对比

| 提供商 | 质量 | 费用 | 延迟 | 是否需要密钥 |
|----------|---------|------|---------|-------------|
| **Edge TTS** | 好 | 免费 | ~1 秒 | 否 |
| **ElevenLabs** | 优秀 | 付费 | ~2 秒 | 是 |
| **OpenAI TTS** | 好 | 付费 | ~1.5 秒 | 是 |
| **NeuTTS** | 好 | 免费 | 取决于 CPU/GPU | 否 |

NeuTTS 使用上方的 `tts.neutts` 配置块。

---

<a id="troubleshooting"></a>
## 故障排除

<a id="no-audio-device-found-cli"></a>
### "未找到音频设备"（CLI）

未安装 PortAudio：

```bash
brew install portaudio    # macOS
sudo apt install portaudio19-dev  # Ubuntu
```

<a id="bot-doesn-t-respond-in-discord-server-channels"></a>
### 机器人在 Discord 服务器频道中没有响应

默认情况下，机器人在服务器频道中需要 @提及。请确保：

1. 输入 `@` 并选择 **机器人用户**（带 #鉴别符），而不是同名 **角色**
2. 或者改用私信——无需提及
3. 或者将 `DISCORD_REQUIRE_MENTION=false` 设置在 `~/.hermes/.env` 中

<a id="bot-joins-vc-but-doesn-t-hear-me"></a>
### 机器人加入了语音频道但听不到我说话

- 检查你的 Discord 用户 ID 是否在 `DISCORD_ALLOWED_USERS` 中
- 确保你在 Discord 中没有被静音
- 机器人需要 Discord 提供 SPEAKING 事件后才能映射你的音频——请在加入后几秒内开始说话

<a id="bot-hears-me-but-doesn-t-respond"></a>
### 机器人能听到我说话但没有回应

- 验证 STT 是否可用：安装 `faster-whisper`（无需密钥）或设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`
- 检查 LLM 模型是否已配置并可访问
- 查看网关日志：`tail -f ~/.hermes/logs/gateway.log`

<a id="bot-responds-in-text-but-not-in-voice-channel"></a>
### 机器人回复了文字但未在语音频道中说话
- TTS 提供者可能出错 — 检查 API key 和配额
- Edge TTS（免费，无需 key）是默认的备用方案
- 检查日志中的 TTS 错误

<a id="whisper-returns-garbage-text"></a>
### Whisper 返回乱码文本

幻觉过滤器会自动处理大部分情况。如果仍然获取到错误的转录文本：

- 使用更安静的环境
- 调整配置中的 `silence_threshold`（数值越大越不敏感）
- 尝试不同的 STT 模型
