---
sidebar_position: 10
title: "语音模式"
description: "与 Hermes Agent 进行实时语音对话 —— 支持 CLI、Telegram、Discord（私聊、文本频道和语音频道）"
---

# 语音模式 {#voice-mode}

Hermes Agent 支持在 CLI 和即时通讯平台进行全方位的语音交互。你可以通过麦克风与 Agent 交谈，听取语音回复，并在 Discord 语音频道中进行实时语音对话。

如果你需要包含推荐配置和实际使用模式的实用设置指南，请参阅 [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)。

## 前提条件 {#prerequisites}

在使用语音功能之前，请确保你已完成以下准备：

1. **安装 Hermes Agent** —— `pip install hermes-agent`（参见 [安装指南](/getting-started/installation)）
2. **配置 LLM 提供商** —— 运行 `hermes model` 或在 `~/.hermes/.env` 中设置你偏好的提供商凭据
3. **基础环境运行正常** —— 在启用语音前，运行 `hermes` 验证 Agent 是否能正常响应文本

:::tip
`~/.hermes/` 目录和默认的 `config.yaml` 会在首次运行 `hermes` 时自动创建。你只需要手动创建 `~/.hermes/.env` 来存放 API 密钥。
:::

## 概览 {#overview}

| 功能 | 平台 | 描述 |
|---------|----------|-------------|
| **交互式语音** | CLI | 按 Ctrl+B 开始录音，Agent 自动检测停顿并回复 |
| **自动语音回复** | Telegram, Discord | Agent 在发送文本回复的同时发送语音音频 |
| **语音频道** | Discord | Bot 加入语音频道（VC），倾听用户说话并以语音回传答复 |

## 需求 {#requirements}

### Python 包 {#python-packages}

```bash
# CLI 语音模式（麦克风 + 音频播放）
pip install "hermes-agent[voice]"

# Discord + Telegram 消息（包含支持语音频道的 discord.py[voice]）
pip install "hermes-agent[messaging]"

# 高级 TTS (ElevenLabs)
pip install "hermes-agent[tts-premium]"

# 本地 TTS (NeuTTS, 可选)
python -m pip install -U neutts[all]

# 一键安装所有依赖
pip install "hermes-agent[all]"
```

| 额外选项 | 包含的包 | 适用场景 |
|-------|----------|-------------|
| `voice` | `sounddevice`, `numpy` | CLI 语音模式 |
| `messaging` | `discord.py[voice]`, `python-telegram-bot`, `aiohttp` | Discord 和 Telegram Bot |
| `tts-premium` | `elevenlabs` | ElevenLabs TTS 提供商 |

可选的本地 TTS 提供商：通过 `python -m pip install -U neutts[all]` 单独安装 `neutts`。首次使用时它会自动下载模型。

:::info
`discord.py[voice]` 会自动安装 **PyNaCl**（用于语音加密）和 **opus 绑定**。这是支持 Discord 语音频道所必需的。
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

| 依赖项 | 用途 | 适用场景 |
|-----------|---------|-------------|
| **PortAudio** | 麦克风输入和音频播放 | CLI 语音模式 |
| **ffmpeg** | 音频格式转换（MP3 → Opus, PCM → WAV） | 所有平台 |
| **Opus** | Discord 语音编解码器 | Discord 语音频道 |
| **espeak-ng** | 音位器（Phonemizer）后端 | 本地 NeuTTS 提供商 |

### API 密钥 {#api-keys}

添加到 `~/.hermes/.env`：

```bash
# 语音转文本 (STT) —— 本地提供商完全不需要密钥
# pip install faster-whisper          # 免费，本地运行，推荐
GROQ_API_KEY=your-key                 # Groq Whisper —— 极速，有免费额度（云端）
VOICE_TOOLS_OPENAI_KEY=your-key       # OpenAI Whisper —— 付费（云端）

# 文本转语音 (TTS) (可选 —— Edge TTS 和 NeuTTS 无需密钥即可工作)
ELEVENLABS_API_KEY=***           # ElevenLabs —— 顶级音质
# 上方的 VOICE_TOOLS_OPENAI_KEY 同样可以启用 OpenAI TTS
```

:::tip
如果安装了 `faster-whisper`，语音模式可以在 **零 API 密钥** 的情况下实现 STT。模型（`base` 版本约 150 MB）会在首次使用时自动下载。
:::

---

## CLI 语音模式 {#cli-voice-mode}

### 快速开始 {#quick-start}

启动 CLI 并启用语音模式：

```bash
hermes                # 启动交互式 CLI
```

然后在 CLI 内部使用以下命令：

```
/voice          切换语音模式开启/关闭
/voice on       启用语音模式
/voice off      禁用语音模式
/voice tts      切换 TTS 输出
/voice status   显示当前状态
```

### 工作原理 {#how-it-works}

1. 使用 `hermes` 启动 CLI，并通过 `/voice on` 启用语音模式。
2. **按下 Ctrl+B** —— 播放提示音（880Hz），开始录音。
3. **说话** —— 实时音量条会显示你的输入：`● [▁▂▃▅▇▇▅▂] ❯`。
4. **停止说话** —— 静默 3 秒后，录音会自动停止。
5. **播放两声提示音**（660Hz），确认录音结束。
6. 音频通过 Whisper 转录并发送给 Agent。
7. 如果启用了 TTS，Agent 的回复将以语音形式朗读。
8. 录音会 **自动重新开始** —— 无需按任何键即可再次说话。

这个循环会一直持续，直到你在录音期间按下 **Ctrl+B**（退出持续模式）或连续 3 次录音未检测到语音。

:::tip
录音键可以通过 `~/.hermes/config.yaml` 中的 `voice.record_key` 进行配置（默认：`ctrl+b`）。
:::

### 静默检测 {#silence-detection}

采用两阶段算法检测你是否说完：

1. **语音确认** —— 等待音频超过 RMS 阈值（200）并持续至少 0.3 秒，允许音节之间有短暂的起伏。
2. **结束检测** —— 一旦确认正在说话，在连续静默 3.0 秒后触发停止。

如果 15 秒内完全没有检测到语音，录音将自动停止。

`silence_threshold`（静默阈值）和 `silence_duration`（静默时长）均可在 `config.yaml` 中配置。

### 流式 TTS {#streaming-tts}

启用 TTS 后，Agent 会在生成文本的同时 **逐句** 朗读回复 —— 你无需等待完整响应生成完毕：

1. 将文本增量缓冲为完整的句子（最少 20 个字符）。
2. 去除 Markdown 格式和 `<think>` 思考块。
3. 实时生成并播放每一句的音频。

### 幻听过滤器 {#hallucination-filter}

Whisper 有时会从静默或背景噪音中生成虚假文本（如 "Thank you for watching", "Subscribe" 等）。Agent 使用一套包含多种语言的 26 个已知幻听短语库以及一个捕获重复变体的正则模式来过滤这些内容。

---

## 网关语音回复 (Telegram & Discord) {#gateway-voice-reply-telegram-discord}

如果你还没有设置消息 Bot，请参阅特定平台的指南：
- [Telegram 设置指南](../messaging/telegram.md)
- [Discord 设置指南](../messaging/discord.md)

启动网关以连接到你的消息平台：

```bash
hermes gateway        # 启动网关（连接到已配置的平台）
hermes gateway setup  # 首次配置的交互式设置向导
```

### Discord：频道 vs 私聊 {#discord-channels-vs-dms}

Bot 在 Discord 上支持两种交互模式：

| 模式 | 如何交流 | 是否需要提及 (@) | 设置 |
|------|------------|-----------------|-------|
| **私聊 (DM)** | 打开 Bot 的个人资料 → “发消息” | 否 | 立即生效 |
| **服务器频道** | 在 Bot 所在的文本频道中输入 | 是 (`@botname`) | 必须先将 Bot 邀请至服务器 |

**私聊（推荐个人使用）：** 只需打开与 Bot 的私聊窗口并输入即可 —— 无需 @提及。语音回复和所有命令在私聊中的工作方式与频道相同。

**服务器频道：** Bot 仅在你 @提及它时才会响应（例如 `@hermesbyt4 你好`）。请确保从提及弹出框中选择 **Bot 用户**，而不是同名的角色。

:::tip
若要在服务器频道中禁用“必须提及”的要求，请在 `~/.hermes/.env` 中添加：
```bash
DISCORD_REQUIRE_MENTION=false
```
或者将特定频道设置为自由响应（无需提及）：
```bash
DISCORD_FREE_RESPONSE_CHANNELS=123456789,987654321
```
:::

### 命令 {#commands}

这些命令在 Telegram 和 Discord（私聊和文本频道）中均有效：

```
/voice          切换语音模式开启/关闭
/voice on       仅当你发送语音消息时才进行语音回复
/voice tts      对所有消息进行语音回复
/voice off      禁用语音回复
/voice status   显示当前设置
```

### 模式 {#modes}

| 模式 | 命令 | 行为 |
|------|---------|----------|
| `off` | `/voice off` | 仅文本（默认） |
| `voice_only` | `/voice on` | 仅当你发送语音消息时才朗读回复 |
| `all` | `/voice tts` | 对每一条消息都朗读回复 |

语音模式设置在网关重启后依然有效。
### 平台交付 {#platform-delivery}

| 平台 | 格式 | 备注 |
|----------|--------|-------|
| **Telegram** | 语音气泡 (Opus/OGG) | 在聊天中内联播放。如果需要，ffmpeg 会将 MP3 转换为 Opus |
| **Discord** | 原生语音气泡 (Opus/OGG) | 像用户语音消息一样内联播放。如果语音气泡 API 失败，则回退到文件附件 |

---

## Discord 语音频道 {#discord-voice-channels}

最沉浸式的语音功能：机器人加入 Discord 语音频道，监听用户说话，转录他们的语音，通过 Agent 进行处理，并在语音频道中播报回复。

### 设置 {#setup}

#### 1. Discord 机器人权限 {#1-discord-bot-permissions}

如果你已经为文本功能设置了 Discord 机器人（参见 [Discord 设置指南](../messaging/discord.md)），你需要添加语音权限。

前往 [Discord Developer Portal](https://discord.com/developers/applications) → 你的应用 → **Installation** → **Default Install Settings** → **Guild Install**：

**在现有的文本权限中添加以下权限：**

| 权限 | 用途 | 必选 |
|-----------|---------|----------|
| **Connect** | 加入语音频道 | 是 |
| **Speak** | 在语音频道中播放 TTS 音频 | 是 |
| **Use Voice Activity** | 检测用户何时在说话 | 推荐 |

**更新后的权限整数（Permissions Integer）：**

| 级别 | 整数值 | 包含内容 |
|-------|---------|----------------|
| 仅文本 | `274878286912` | 查看频道、发送消息、读取历史记录、嵌入链接、附件、线程、反应 |
| 文本 + 语音 | `274881432640` | 以上所有权限 + 连接、发言 |

使用更新后的权限 URL **重新邀请机器人**：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274881432640
```

将 `YOUR_APP_ID` 替换为开发者门户中的 Application ID。

:::warning
将机器人重新邀请到它已存在的服务器会更新其权限，而不会将其移除。你不会丢失任何数据或配置。
:::

#### 2. 特权网关意图 (Privileged Gateway Intents) {#2-privileged-gateway-intents}

在 [Developer Portal](https://discord.com/developers/applications) → 你的应用 → **Bot** → **Privileged Gateway Intents** 中，启用以下全部三项：

| 意图 | 用途 |
|--------|---------|
| **Presence Intent** | 检测用户在线/离线状态 |
| **Server Members Intent** | 将语音 SSRC 标识符映射到 Discord 用户 ID |
| **Message Content Intent** | 读取频道中的文本消息内容 |

这三项对于完整的语音频道功能都是必需的。**Server Members Intent** 尤为关键 —— 如果没有它，机器人将无法识别语音频道中是谁在说话。

#### 3. Opus 编解码器 {#3-opus-codec}

运行 gateway 的机器上必须安装 Opus 编解码器库：

```bash
# macOS (Homebrew)
brew install opus

# Ubuntu/Debian
sudo apt install libopus0
```

机器人会自动从以下路径加载编解码器：
- **macOS:** `/opt/homebrew/lib/libopus.dylib`
- **Linux:** `libopus.so.0`

#### 4. 环境变量 {#4-environment-variables}

```bash
# ~/.hermes/.env

# Discord 机器人（已配置文本功能）
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-user-id

# STT — 本地提供商不需要密钥 (pip install faster-whisper)
# GROQ_API_KEY=your-key            # 备选：基于云端，速度快，有免费额度

# TTS — 可选。Edge TTS 和 NeuTTS 不需要密钥。
# ELEVENLABS_API_KEY=***      # 高级音质
# VOICE_TOOLS_OPENAI_KEY=***  # OpenAI TTS / Whisper
```

### 启动 Gateway {#start-the-gateway}

```bash
hermes gateway        # 使用现有配置启动
```

机器人应该会在几秒钟内在 Discord 中上线。

<a id="commands"></a>
### 命令

在机器人所在的 Discord 文本频道中使用这些命令：

```
/voice join      机器人加入你当前的语音频道
/voice channel   /voice join 的别名
/voice leave     机器人断开语音频道连接
/voice status    显示语音模式和已连接的频道
```

:::info
在运行 `/voice join` 之前，你必须先进入一个语音频道。机器人会加入你所在的同一个语音频道。
:::

<a id="how-it-works"></a>
### 工作原理

当机器人加入语音频道后，它会：

1. 独立**监听**每个用户的音频流
2. **检测静音** —— 在至少 0.5 秒的说话后出现 1.5 秒的静音将触发处理
3. 通过 Whisper STT（本地、Groq 或 OpenAI）**转录**音频
4. 通过完整的 Agent 流水线（会话、工具、记忆）进行**处理**
5. 通过 TTS 在语音频道中**播报**回复

### 文本频道集成 {#text-channel-integration}

当机器人在语音频道中时：

- 转录文本会出现在文本频道中：`[Voice] @user: what you said`
- Agent 的响应会作为文本发送到频道，并在语音频道中播报
- 文本频道是指发出 `/voice join` 命令的那个频道

### 回声消除 {#echo-prevention}

机器人在播放 TTS 回复时会自动暂停其音频监听器，防止它听到并重新处理自己的输出。

### 访问控制 {#access-control}

只有 `DISCORD_ALLOWED_USERS` 中列出的用户可以通过语音进行交互。其他用户的音频将被静默忽略。

```bash
# ~/.hermes/.env
DISCORD_ALLOWED_USERS=284102345871466496
```

---

## 配置参考 {#configuration-reference}

### config.yaml {#config-yaml}

```yaml
# 语音录制 (CLI)
voice:
  record_key: "ctrl+b"            # 开始/停止录制的按键
  max_recording_seconds: 120       # 最大录制时长
  auto_tts: false                  # 语音模式启动时自动开启 TTS
  silence_threshold: 200           # 低于此 RMS 级别 (0-32767) 视为静音
  silence_duration: 3.0            # 自动停止前的静音秒数

# 语音转文本 (STT)
stt:
  provider: "local"                  # "local" (免费) | "groq" | "openai"
  local:
    model: "base"                    # tiny, base, small, medium, large-v3
  # model: "whisper-1"              # 遗留配置：当未设置 provider 时使用

# 文本转语音 (TTS)
tts:
  provider: "edge"                 # "edge" (免费) | "elevenlabs" | "openai" | "neutts" | "minimax"
  edge:
    voice: "en-US-AriaNeural"      # 322 种声音，74 种语言
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"    # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"                 # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 可选：覆盖自托管或兼容 OpenAI 的端点
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

### 环境变量 {#environment-variables}

```bash
# 语音转文本 (STT) 提供商（本地模式不需要密钥）
# pip install faster-whisper        # 免费本地 STT — 无需 API 密钥
GROQ_API_KEY=...                    # Groq Whisper (快，有免费额度)
VOICE_TOOLS_OPENAI_KEY=...         # OpenAI Whisper (付费)

# STT 高级覆盖选项（可选）
STT_GROQ_MODEL=whisper-large-v3-turbo    # 覆盖默认 Groq STT 模型
STT_OPENAI_MODEL=whisper-1               # 覆盖默认 OpenAI STT 模型
GROQ_BASE_URL=https://api.groq.com/openai/v1     # 自定义 Groq 端点
STT_OPENAI_BASE_URL=https://api.openai.com/v1    # 自定义 OpenAI STT 端点

# 文本转语音 (TTS) 提供商（Edge TTS 和 NeuTTS 不需要密钥）
ELEVENLABS_API_KEY=***             # ElevenLabs (顶级音质)
# 上方的 VOICE_TOOLS_OPENAI_KEY 同样可以启用 OpenAI TTS

# Discord 语音频道
DISCORD_BOT_TOKEN=...
DISCORD_ALLOWED_USERS=...
```

### STT 提供商对比 {#stt-provider-comparison}

| 提供商 | 模型 | 速度 | 质量 | 成本 | 需要密钥 |
|----------|-------|-------|---------|------|---------|
| **Local** | `base` | 快 (取决于 CPU/GPU) | 良好 | 免费 | 否 |
| **Local** | `small` | 中等 | 较好 | 免费 | 否 |
| **Local** | `large-v3` | 慢 | 最好 | 免费 | 否 |
| **Groq** | `whisper-large-v3-turbo` | 极快 (~0.5s) | 良好 | 免费额度 | 是 |
| **Groq** | `whisper-large-v3` | 快 (~1s) | 较好 | 免费额度 | 是 |
| **OpenAI** | `whisper-1` | 快 (~1s) | 良好 | 付费 | 是 |
| **OpenAI** | `gpt-4o-transcribe` | 中等 (~2s) | 最好 | 付费 | 是 |

提供商优先级（自动回退）：**local** > **groq** > **openai**

### TTS 提供商对比 {#tts-provider-comparison}

| 提供商 | 质量 | 成本 | 延迟 | 需要密钥 |
|----------|---------|------|---------|-------------|
| **Edge TTS** | 良好 | 免费 | ~1s | 否 |
| **ElevenLabs** | 极佳 | 付费 | ~2s | 是 |
| **OpenAI TTS** | 良好 | 付费 | ~1.5s | 是 |
| **NeuTTS** | 良好 | 免费 | 取决于 CPU/GPU | 否 |
NeuTTS 使用上方配置中的 `tts.neutts` 配置块。

---

## 故障排除 {#troubleshooting}

### "No audio device found" (CLI) {#no-audio-device-found-cli}

PortAudio 未安装：

```bash
brew install portaudio    # macOS
sudo apt install portaudio19-dev  # Ubuntu
```

### Bot 在 Discord 服务器频道中不响应 {#bot-doesn-t-respond-in-discord-server-channels}

在服务器频道中，Bot 默认需要被 @mention（提及）。请确保：

1. 输入 `@` 并选择 **Bot 用户**（带有 #数字编号），而不是同名的 **Role（身份组）**
2. 或者改用私聊（DM）—— 不需要 @mention
3. 或者在 `~/.hermes/.env` 中设置 `DISCORD_REQUIRE_MENTION=false`

### Bot 加入了语音频道（VC）但听不到我说话 {#bot-joins-vc-but-doesn-t-hear-me}

- 检查你的 Discord 用户 ID 是否在 `DISCORD_ALLOWED_USERS` 中
- 确保你在 Discord 中没有被静音
- Bot 需要从 Discord 接收到一个 SPEAKING 事件才能映射你的音频 —— 请在加入后的几秒钟内开始说话

### Bot 能听到我说话但不响应 {#bot-hears-me-but-doesn-t-respond}

- 验证 STT 是否可用：安装 `faster-whisper`（无需 Key）或设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`
- 检查 LLM 模型是否已配置且可访问
- 查看 Gateway 日志：`tail -f ~/.hermes/logs/gateway.log`

### Bot 在文本中回复但在语音频道中不说话 {#bot-responds-in-text-but-not-in-voice-channel}

- TTS 提供商可能调用失败 —— 检查 API Key 和配额
- Edge TTS（免费，无需 Key）是默认的备用方案
- 检查日志中的 TTS 错误

### Whisper 返回乱码或无关文本 {#whisper-returns-garbage-text}

幻觉过滤器会自动处理大部分情况。如果你仍然遇到虚假的转录内容：

- 使用更安静的环境
- 调整配置中的 `silence_threshold`（调高 = 降低灵敏度）
- 尝试使用不同的 STT 模型
