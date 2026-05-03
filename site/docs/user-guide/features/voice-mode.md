---
sidebar_position: 10
title: "语音模式"
description: "与 Hermes Agent 进行实时语音对话 — CLI、Telegram、Discord（私信、文字频道和语音频道）"
---

# 语音模式 {#voice-mode}

Hermes Agent 支持在 CLI 和消息平台上的完整语音交互。使用麦克风与 Agent 对话，收听语音回复，并在 Discord 语音频道中进行实时语音对话。

如果你想要一个包含推荐配置和实际使用模式的实用设置指南，请参阅[与 Hermes 一起使用语音模式](/guides/use-voice-mode-with-hermes)。

## 前提条件 {#prerequisites}

在使用语音功能之前，请确保你已具备以下条件：

1. **已安装 Hermes Agent** — `pip install hermes-agent`（参见[安装](/getting-started/installation)）
2. **已配置 LLM 提供商** — 运行 `hermes model` 或在 `~/.hermes/.env` 中设置首选提供商的凭据
3. **基础设置可正常工作** — 在启用语音之前，运行 `hermes` 验证 Agent 能响应文本

:::tip
`~/.hermes/` 目录和默认的 `config.yaml` 会在你首次运行 `hermes` 时自动创建。你只需手动创建 `~/.hermes/.env` 来存放 API 密钥。
:::

## 概览 {#overview}

| 功能 | 平台 | 描述 |
|---------|----------|-------------|
| **交互式语音** | CLI | 按 Ctrl+B 开始录音，Agent 自动检测静音并回复 |
| **自动语音回复** | Telegram、Discord | Agent 在发送文本回复的同时发送语音音频 |
| **语音频道** | Discord | 机器人加入语音频道，监听用户说话，并语音回复 |

## 要求 {#requirements}

### Python 包 {#python-packages}

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

| 附加组件 | 包含的包 | 用于 |
|-------|----------|-------------|
| `voice` | `sounddevice`、`numpy` | CLI 语音模式 |
| `messaging` | `discord.py[voice]`、`python-telegram-bot`、`aiohttp` | Discord 和 Telegram 机器人 |
| `tts-premium` | `elevenlabs` | ElevenLabs TTS 提供商 |

可选的本地 TTS 提供商：单独安装 `neutts`，使用 `python -m pip install -U neutts[all]`。首次使用时会自动下载模型。

:::info
`discord.py[voice]` 会自动安装 **PyNaCl**（用于语音加密）和 **opus 绑定**。这是 Discord 语音频道支持所必需的。
:::

### 系统依赖 {#system-dependencies}

```bash
# macOS
brew install portaudio ffmpeg opus
brew install espeak-ng   # 用于 NeuTTS

# Ubuntu/Debian
sudo apt install portaudio19-dev ffmpeg libopus0
sudo apt install espeak-ng   # 用于 NeuTTS
```

| 依赖 | 用途 | 用于 |
|-----------|---------|-------------|
| **PortAudio** | 麦克风输入和音频播放 | CLI 语音模式 |
| **ffmpeg** | 音频格式转换（MP3 → Opus、PCM → WAV） | 所有平台 |
| **Opus** | Discord 语音编解码器 | Discord 语音频道 |
| **espeak-ng** | 音素化后端 | 本地 NeuTTS 提供商 |

### API 密钥 {#api-keys}
添加至 `~/.hermes/.env`：

```bash
# 语音转文字 — 本地提供商完全不需要密钥
# pip install faster-whisper          # 免费，本地运行，推荐
GROQ_API_KEY=your-key                 # Groq Whisper — 快速，免费套餐（云端）
VOICE_TOOLS_OPENAI_KEY=your-key       # OpenAI Whisper — 付费（云端）

# 文字转语音（可选 — Edge TTS 和 NeuTTS 无需任何密钥即可工作）
ELEVENLABS_API_KEY=***           # ElevenLabs — 高品质
# 上面的 VOICE_TOOLS_OPENAI_KEY 也启用了 OpenAI TTS
```

:::tip
如果安装了 `faster-whisper`，语音模式在 STT 方面**无需任何 API 密钥**即可工作。模型（`base` 版本约 150 MB）会在首次使用时自动下载。
:::

---

## CLI 语音模式 {#cli-voice-mode}

语音模式在**经典 CLI**（`hermes chat`）和 **TUI**（`hermes --tui`）中均可使用。两者的行为完全一致——相同的斜杠命令、相同的 VAD 静音检测、相同的流式 TTS、相同的幻觉过滤器。TUI 额外将崩溃取证日志转发到 `~/.hermes/logs/`，因此当在特殊音频后端上出现按键通话失败时，可以附带完整的堆栈跟踪进行报告，而不会无声无息地消失。

### 快速开始 {#quick-start}

启动 CLI 并启用语音模式：

```bash
hermes                # 启动交互式 CLI
```

然后在 CLI 中使用以下命令：

```
/voice          切换语音模式开/关
/voice on       启用语音模式
/voice off      禁用语音模式
/voice tts      切换 TTS 输出
/voice status   显示当前状态
```

### 工作原理 {#how-it-works}

1. 使用 `hermes` 启动 CLI，并通过 `/voice on` 启用语音模式
2. **按下 Ctrl+B** — 会播放一声提示音（880Hz），开始录音
3. **说话** — 实时音频电平条会显示你的输入：`● [▁▂▃▅▇▇▅▂] ❯`
4. **停止说话** — 静音 3 秒后，录音自动停止
5. **两声提示音**（660Hz）确认录音结束
6. 音频通过 Whisper 转录并发送给 Agent
7. 如果启用了 TTS，Agent 的回复会被朗读出来
8. 录音**自动重新开始** — 无需按任何键即可再次说话

这个循环会持续进行，直到你在录音期间按下 **Ctrl+B**（退出连续模式），或者连续 3 次录音未检测到语音。

:::tip
录音键可通过 `~/.hermes/config.yaml` 中的 `voice.record_key` 配置（默认值：`ctrl+b`）。
:::

### 静音检测 {#silence-detection}

两阶段算法检测你何时说完：

1. **语音确认** — 等待音频超过 RMS 阈值（200）至少 0.3 秒，容忍音节之间的短暂下降
2. **结束检测** — 一旦确认语音，在连续静音 3.0 秒后触发

如果 15 秒内完全没有检测到语音，录音会自动停止。

`silence_threshold` 和 `silence_duration` 都可以在 `config.yaml` 中配置。你也可以通过 `voice.beep_enabled: false` 禁用录音开始/结束提示音。

### 流式 TTS {#streaming-tts}

当 TTS 启用时，Agent 会在生成文本的同时**逐句**朗读回复——你无需等待完整响应：

1. 将文本增量缓冲成完整的句子（最少 20 个字符）
2. 去除 Markdown 格式和 ` 思考` 块
3. 实时生成并播放每句的音频
### 幻觉过滤器 {#hallucination-filter}

Whisper 有时会从静音或背景噪音中生成幻影文本（例如“感谢观看”、“订阅”等）。Agent 会使用一组包含 26 条已知幻觉短语（涵盖多种语言）以及一个用于捕获重复变体的正则表达式模式来过滤掉这些内容。

---

## 网关语音回复（Telegram 和 Discord） {#gateway-voice-reply-telegram-discord}

如果你还没有设置消息机器人，请参考对应平台的指南：
- [Telegram 设置指南](../messaging/telegram.md)
- [Discord 设置指南](../messaging/discord.md)

启动网关以连接到你的消息平台：

```bash
hermes gateway        # 启动网关（连接到已配置的平台）
hermes gateway setup  # 首次配置的交互式设置向导
```

### Discord：频道 vs 私信 {#discord-channels-vs-dms}

该机器人在 Discord 上支持两种交互模式：

| 模式 | 如何对话 | 是否需要提及 | 设置 |
|------|----------|-------------|------|
| **私信（DM）** | 打开机器人资料 → “发送消息” | 否 | 立即生效 |
| **服务器频道** | 在机器人所在的文字频道中打字 | 是（`@机器人名`） | 机器人必须被邀请到服务器 |

**私信（推荐个人使用）：** 直接打开与机器人的私信并输入文字即可——无需 @提及。语音回复和所有命令与频道中的行为相同。

**服务器频道：** 机器人仅在你 @提及它时才会响应（例如 `@hermesbyt4 你好`）。请确保在提及弹出窗口中选择的是 **机器人用户**，而不是同名的角色。

:::tip
要禁用服务器频道中的提及要求，请在 `~/.hermes/.env` 中添加：
```bash
DISCORD_REQUIRE_MENTION=false
```
或者将特定频道设置为自由回复（无需提及）：
```bash
DISCORD_FREE_RESPONSE_CHANNELS=123456789,987654321
```
:::

### 命令 {#commands}

以下命令在 Telegram 和 Discord（私信和文字频道）中均有效：

```
/voice          切换语音模式开/关
/voice on       仅当你发送语音消息时，才以语音回复
/voice tts      对所有消息都以语音回复
/voice off      禁用语音回复
/voice status   显示当前设置
```

### 模式 {#modes}

| 模式 | 命令 | 行为 |
|------|------|------|
| `off` | `/voice off` | 仅文本（默认） |
| `voice_only` | `/voice on` | 仅当你发送语音消息时，才以语音回复 |
| `all` | `/voice tts` | 对每条消息都以语音回复 |

语音模式设置在网关重启后仍然保留。

### 平台投递 {#platform-delivery}

| 平台 | 格式 | 备注 |
|------|------|------|
| **Telegram** | 语音气泡（Opus/OGG） | 在聊天中内联播放。如有需要，ffmpeg 会将 MP3 转换为 Opus |
| **Discord** | 原生语音气泡（Opus/OGG） | 像用户语音消息一样内联播放。如果语音气泡 API 失败，则回退为文件附件 |

---

## Discord 语音频道 {#discord-voice-channels}

最具沉浸感的语音功能：机器人加入 Discord 语音频道，聆听用户说话，转录语音，通过 Agent 处理，然后在语音频道中说出回复。

### 设置 {#setup}

#### 1. Discord 机器人权限 {#1-discord-bot-permissions}
如果你已经为文本功能设置了一个 Discord 机器人（参见 [Discord 设置指南](../messaging/discord.md)），你需要添加语音权限。

前往 [Discord 开发者门户](https://discord.com/developers/applications) → 你的应用 → **Installation** → **Default Install Settings** → **Guild Install**：

**在现有文本权限基础上添加以下权限：**

| 权限 | 用途 | 必需 |
|-----------|---------|----------|
| **Connect** | 加入语音频道 | 是 |
| **Speak** | 在语音频道中播放 TTS 音频 | 是 |
| **Use Voice Activity** | 检测用户是否在说话 | 推荐 |

**更新后的权限整数：**

| 级别 | 整数 | 包含内容 |
|-------|---------|----------------|
| 仅文本 | `274878286912` | 查看频道、发送消息、阅读历史、嵌入、附件、线程、反应 |
| 文本 + 语音 | `274881432640` | 以上所有 + Connect、Speak |

**使用更新后的权限 URL 重新邀请机器人**：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274881432640
```

将 `YOUR_APP_ID` 替换为开发者门户中的应用程序 ID。

:::warning
将机器人重新邀请到它已在的服务器会更新其权限，而不会移除它。你不会丢失任何数据或配置。
:::

#### 2. 特权网关意图 {#2-privileged-gateway-intents}

在 [开发者门户](https://discord.com/developers/applications) → 你的应用 → **Bot** → **Privileged Gateway Intents** 中，启用所有三个：

| 意图 | 用途 |
|--------|---------|
| **Presence Intent** | 检测用户在线/离线状态 |
| **Server Members Intent** | 将语音 SSRC 标识符映射到 Discord 用户 ID |
| **Message Content Intent** | 读取频道中的文本消息内容 |

全部三个对于完整的语音频道功能都是必需的。**Server Members Intent** 尤其关键——没有它，机器人无法识别语音频道中谁在说话。

#### 3. Opus 编解码器 {#3-opus-codec}

必须在运行网关的机器上安装 Opus 编解码器库：

```bash
# macOS (Homebrew)
brew install opus

# Ubuntu/Debian
sudo apt install libopus0
```

机器人会自动从以下位置加载编解码器：
- **macOS:** `/opt/homebrew/lib/libopus.dylib`
- **Linux:** `libopus.so.0`

#### 4. 环境变量 {#4-environment-variables}

```bash
# ~/.hermes/.env

# Discord 机器人（已为文本配置）
DISCORD_BOT_TOKEN=你的机器人令牌
DISCORD_ALLOWED_USERS=你的用户 ID

# STT — 本地提供者无需密钥（pip install faster-whisper）
# GROQ_API_KEY=你的密钥            # 替代方案：基于云，快速，免费层

# TTS — 可选。Edge TTS 和 NeuTTS 无需密钥。
# ELEVENLABS_API_KEY=***      # 高级质量
# VOICE_TOOLS_OPENAI_KEY=***  # OpenAI TTS / Whisper
```

### 启动网关 {#start-the-gateway}

```bash
hermes gateway        # 使用现有配置启动
```

机器人应在几秒钟内上线 Discord。

### 命令 {#commands}

在机器人所在的 Discord 文本频道中使用以下命令：

```
/voice join      机器人加入你当前的语音频道
/voice channel   /voice join 的别名
/voice leave     机器人断开语音频道连接
/voice status    显示语音模式和已连接的频道
```
:::info
你必须在运行 `/voice join` 之前先加入一个语音频道。机器人会加入你所在的同一个语音频道。
:::

### 工作原理 {#how-it-works}

当机器人加入语音频道后，它会：

1. **监听** 每个用户的音频流（独立处理）
2. **检测静音** — 在至少 0.5 秒的语音后，若出现 1.5 秒静音则触发处理
3. **转写** 音频（通过 Whisper STT：本地、Groq 或 OpenAI）
4. **处理** 完整的 Agent 流水线（会话、工具、记忆）
5. **回复** 通过 TTS 在语音频道中朗读回复

### 文本频道集成 {#text-channel-integration}

当机器人在语音频道中时：

- 转写内容会出现在文本频道中：`[Voice] @user: 你说的话`
- Agent 的回复会同时以文本形式发送到频道，并在语音频道中朗读
- 文本频道就是执行 `/voice join` 命令的那个频道

### 回声防止 {#echo-prevention}

机器人在播放 TTS 回复时会自动暂停音频监听，避免听到并重新处理自己的输出。

### 访问控制 {#access-control}

只有 `DISCORD_ALLOWED_USERS` 中列出的用户才能通过语音交互。其他用户的音频会被静默忽略。

```bash
# ~/.hermes/.env
DISCORD_ALLOWED_USERS=284102345871466496
```

---

## 配置参考 {#configuration-reference}

### config.yaml {#config-yaml}

```yaml
# 语音录制（CLI）
voice:
  record_key: "ctrl+b"            # 开始/停止录制的按键
  max_recording_seconds: 120       # 最大录制时长
  auto_tts: false                  # 语音模式启动时自动启用 TTS
  beep_enabled: true               # 播放录制开始/停止提示音
  silence_threshold: 200           # RMS 电平（0-32767），低于此值视为静音
  silence_duration: 3.0            # 自动停止前的静音秒数

# 语音转文字（STT）
stt:
  provider: "local"                  # "local"（免费）| "groq" | "openai"
  local:
    model: "base"                    # tiny, base, small, medium, large-v3
  # model: "whisper-1"              # 旧版：当未设置 provider 时使用

# 文字转语音（TTS）
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
    base_url: "https://api.openai.com/v1"  # 可选：覆盖为自托管或兼容 OpenAI 的端点
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

### 环境变量 {#environment-variables}

```bash
# 语音转文字提供商（本地无需密钥）
# pip install faster-whisper        # 免费本地 STT — 无需 API 密钥
GROQ_API_KEY=...                    # Groq Whisper（快速，免费额度）
VOICE_TOOLS_OPENAI_KEY=...         # OpenAI Whisper（付费）

# STT 高级覆盖（可选）
STT_GROQ_MODEL=whisper-large-v3-turbo    # 覆盖默认 Groq STT 模型
STT_OPENAI_MODEL=whisper-1               # 覆盖默认 OpenAI STT 模型
GROQ_BASE_URL=https://api.groq.com/openai/v1     # 自定义 Groq 端点
STT_OPENAI_BASE_URL=https://api.openai.com/v1    # 自定义 OpenAI STT 端点

# 文字转语音提供商（Edge TTS 和 NeuTTS 无需密钥）
ELEVENLABS_API_KEY=***             # ElevenLabs（优质音质）
# 上面的 VOICE_TOOLS_OPENAI_KEY 也启用了 OpenAI TTS

# Discord 语音频道
DISCORD_BOT_TOKEN=...
DISCORD_ALLOWED_USERS=...
```
### STT 提供商对比 {#stt-provider-comparison}

| 提供商 | 模型 | 速度 | 质量 | 成本 | API 密钥 |
|--------|------|------|------|------|----------|
| **Local** | `base` | 快（取决于 CPU/GPU） | 良好 | 免费 | 否 |
| **Local** | `small` | 中等 | 更好 | 免费 | 否 |
| **Local** | `large-v3` | 慢 | 最佳 | 免费 | 否 |
| **Groq** | `whisper-large-v3-turbo` | 非常快（约 0.5 秒） | 良好 | 免费层 | 是 |
| **Groq** | `whisper-large-v3` | 快（约 1 秒） | 更好 | 免费层 | 是 |
| **OpenAI** | `whisper-1` | 快（约 1 秒） | 良好 | 付费 | 是 |
| **OpenAI** | `gpt-4o-transcribe` | 中等（约 2 秒） | 最佳 | 付费 | 是 |

提供商优先级（自动回退）：**local** > **groq** > **openai**

### TTS 提供商对比 {#tts-provider-comparison}

| 提供商 | 质量 | 成本 | 延迟 | 需要密钥 |
|--------|------|------|------|----------|
| **Edge TTS** | 良好 | 免费 | 约 1 秒 | 否 |
| **ElevenLabs** | 优秀 | 付费 | 约 2 秒 | 是 |
| **OpenAI TTS** | 良好 | 付费 | 约 1.5 秒 | 是 |
| **NeuTTS** | 良好 | 免费 | 取决于 CPU/GPU | 否 |

NeuTTS 使用上面 `tts.neutts` 配置块。

---

## 故障排除 {#troubleshooting}

### “未找到音频设备”（CLI） {#no-audio-device-found-cli}

未安装 PortAudio：

```bash
brew install portaudio    # macOS
sudo apt install portaudio19-dev  # Ubuntu
```

### 机器人在 Discord 服务器频道中没有响应 {#bot-doesn-t-respond-in-discord-server-channels}

默认情况下，机器人在服务器频道中需要 @提及。请确保：

1. 输入 `@` 并选择 **机器人用户**（带有 #discriminator），而不是同名的 **角色**
2. 或者改用私信——无需提及
3. 或者将 `DISCORD_REQUIRE_MENTION=false` 设置到 `~/.hermes/.env` 中

### 机器人加入语音频道但听不到我说话 {#bot-joins-vc-but-doesn-t-hear-me}

- 检查你的 Discord 用户 ID 是否在 `DISCORD_ALLOWED_USERS` 中
- 确保你在 Discord 中没有被静音
- 机器人需要从 Discord 收到一个 SPEAKING 事件才能映射你的音频——加入后几秒内开始说话

### 机器人能听到我说话但没有回应 {#bot-hears-me-but-doesn-t-respond}

- 确认 STT 可用：安装 `faster-whisper`（无需密钥）或设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`
- 检查 LLM 模型是否已配置并可访问
- 查看网关日志：`tail -f ~/.hermes/logs/gateway.log`

### 机器人以文本回复但不在语音频道中说话 {#bot-responds-in-text-but-not-in-voice-channel}

- TTS 提供商可能失败——检查 API 密钥和配额
- Edge TTS（免费，无需密钥）是默认回退
- 检查日志中的 TTS 错误

### Whisper 返回乱码文本 {#whisper-returns-garbage-text}

幻觉过滤器会自动捕获大多数情况。如果你仍然得到虚假转录：

- 使用更安静的环境
- 调整配置中的 `silence_threshold`（值越大 = 越不敏感）
- 尝试不同的 STT 模型
