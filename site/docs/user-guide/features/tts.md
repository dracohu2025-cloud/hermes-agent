---
sidebar_position: 9
title: "语音与 TTS"
description: "跨所有平台的文本转语音与语音消息转录"
---

# 语音与 TTS {#voice-tts}

Hermes Agent 在所有消息平台上均支持文本转语音输出和语音消息转录。

:::tip Nous 订阅用户
如果你拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，则可以通过 **[工具网关](tool-gateway.md)** 使用 OpenAI TTS，无需单独的 OpenAI API 密钥。运行 `hermes model` 或 `hermes tools` 即可启用。
:::
<a id="nous-subscribers"></a>

## 文本转语音 {#text-to-speech}

支持通过十个提供商将文本转换为语音：

| 提供商 | 质量 | 费用 | API 密钥 |
|----------|---------|------|---------|
| **Edge TTS**（默认） | 良好 | 免费 | 无需 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax TTS** | 优秀 | 付费 | `MINIMAX_API_KEY` |
| **Mistral（Voxtral TTS）** | 优秀 | 付费 | `MISTRAL_API_KEY` |
| **Google Gemini TTS** | 优秀 | 免费额度 | `GEMINI_API_KEY` |
| **xAI TTS** | 优秀 | 付费 | `XAI_API_KEY` |
| **NeuTTS** | 良好 | 免费（本地） | 无需 |
| **KittenTTS** | 良好 | 免费（本地） | 无需 |
| **Piper** | 良好 | 免费（本地） | 无需 |

### 平台投递 {#platform-delivery}

| 平台 | 投递方式 | 格式 |
|----------|----------|--------|
| Telegram | 语音气泡（内联播放） | Opus `.ogg` |
| Discord | 语音气泡（Opus/OGG），回退为文件附件 | Opus/MP3 |
| WhatsApp | 音频文件附件 | MP3 |
| CLI | 保存至 `~/.hermes/audio_cache/` | MP3 |

### 配置 {#configuration}

```yaml
# 在 ~/.hermes/config.yaml 中
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts" | "kittentts" | "piper"
  speed: 1.0                    # 全局速度倍率（各提供商的特定设置会覆盖此值）
  edge:
    voice: "en-US-AriaNeural"   # 322 种语音，74 种语言
    speed: 1.0                  # 转换为速率百分比（+/-%）
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 覆盖 OpenAI 兼容 TTS 端点
    speed: 1.0                  # 0.25 - 4.0
  minimax:
    model: "speech-2.8-hd"     # speech-2.8-hd（默认），speech-2.8-turbo
    voice_id: "English_Graceful_Lady"  # 参见 https://platform.minimax.io/faq/system-voice-id
    speed: 1                    # 0.5 - 2.0
    vol: 1                      # 0 - 10
    pitch: 0                    # -12 - 12
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - 中性（默认）
  gemini:
    model: "gemini-2.5-flash-preview-tts"  # 或 gemini-2.5-pro-preview-tts
    voice: "Kore"               # 30 种预置语音：Zephyr, Puck, Kore, Enceladus, Gacrux 等
  xai:
    voice_id: "eve"             # 或自定义语音 ID — 参见下方文档
    language: "en"              # ISO 639-1 代码
    sample_rate: 24000          # 22050 / 24000（默认）/ 44100 / 48000
    bit_rate: 128000            # MP3 比特率；仅当 codec=mp3 时生效
    # base_url: "https://api.x.ai/v1"   # 通过 XAI_BASE_URL 环境变量覆盖
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
  kittentts:
    model: KittenML/kitten-tts-nano-0.8-int8   # 25MB int8；另有：kitten-tts-micro-0.8（41MB），kitten-tts-mini-0.8（80MB）
    voice: Jasper                               # Jasper, Bella, Luna, Bruno, Rosie, Hugo, Kiki, Leo
    speed: 1.0                                  # 0.5 - 2.0
    clean_text: true                            # 展开数字、货币、单位
  piper:
    voice: en_US-lessac-medium                  # 语音名称（自动下载）或 .onnx 文件的绝对路径
    # voices_dir: ''                            # 默认：~/.hermes/cache/piper-voices/
    # use_cuda: false                           # 需要 onnxruntime-gpu
    # length_scale: 1.0                         # 2.0 = 慢两倍
    # noise_scale: 0.667
    # noise_w_scale: 0.8
    # volume: 1.0                               # 0.5 = 音量减半
    # normalize_audio: true
```
**速度控制**：全局 `tts.speed` 值默认适用于所有提供商。每个提供商可以通过自己的 `speed` 设置覆盖（例如 `tts.openai.speed: 1.5`）。提供商特定的速度优先级高于全局值。默认值为 `1.0`（正常速度）。

### Telegram 语音气泡与 ffmpeg {#telegram-voice-bubbles-ffmpeg}

Telegram 语音气泡需要 Opus/OGG 音频格式：

- **OpenAI、ElevenLabs 和 Mistral** 原生输出 Opus — 无需额外设置
- **Edge TTS**（默认）输出 MP3，需要 **ffmpeg** 进行转换：
- **MiniMax TTS** 输出 MP3，需要 **ffmpeg** 转换为 Telegram 语音气泡
- **Google Gemini TTS** 输出原始 PCM，使用 **ffmpeg** 直接编码为 Opus 用于 Telegram 语音气泡
- **xAI TTS** 输出 MP3，需要 **ffmpeg** 转换为 Telegram 语音气泡
- **NeuTTS** 输出 WAV，也需要 **ffmpeg** 转换为 Telegram 语音气泡
- **KittenTTS** 输出 WAV，也需要 **ffmpeg** 转换为 Telegram 语音气泡
- **Piper** 输出 WAV，也需要 **ffmpeg** 转换为 Telegram 语音气泡

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

如果没有 ffmpeg，Edge TTS、MiniMax TTS、NeuTTS、KittenTTS 和 Piper 的音频会作为普通音频文件发送（可播放，但显示为矩形播放器而非语音气泡）。

:::tip
如果你希望在不安装 ffmpeg 的情况下使用语音气泡，请切换到 OpenAI、ElevenLabs 或 Mistral 提供商。
:::

### xAI 自定义语音（语音克隆） {#xai-custom-voices-voice-cloning}

xAI 支持克隆你的声音并将其用于 TTS。在 [xAI 控制台](https://console.x.ai/team/default/voice/voice-library) 中创建自定义语音，然后在配置中设置生成的 `voice_id`：

```yaml
tts:
  provider: xai
  xai:
    voice_id: "nlbqfwie"   # 你的自定义语音 ID
```

有关录音、支持的格式和限制的详细信息，请参阅 [xAI 自定义语音文档](https://docs.x.ai/developers/model-capabilities/audio/custom-voices)。

### Piper（本地，44 种语言） {#piper-local-44-languages}

Piper 是 Open Home Foundation（Home Assistant 维护者）开发的一款快速、本地的神经 TTS 引擎。它完全在 CPU 上运行，支持 **44 种语言** 的预训练语音，无需 API 密钥。

**通过 `hermes tools` 安装** → 语音与 TTS → Piper — Hermes 会为你运行 `pip install piper-tts`。或者手动安装：`pip install piper-tts`。

**切换到 Piper：**

```yaml
tts:
  provider: piper
  piper:
    voice: en_US-lessac-medium
```

在首次调用本地未缓存的语音时，Hermes 会运行 `python -m piper.download_voices &lt;name&gt;` 并下载模型（根据质量等级约 20-90MB）到 `~/.hermes/cache/piper-voices/`。后续调用会复用缓存的模型。

**选择语音。** [完整语音目录](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md) 涵盖英语、西班牙语、法语、德语、意大利语、荷兰语、葡萄牙语、俄语、波兰语、土耳其语、中文、阿拉伯语、印地语等 — 每种都有 `x_low` / `low` / `medium` / `high` 质量等级。在 [rhasspy.github.io/piper-samples](https://rhasspy.github.io/piper-samples/) 试听语音样本。
**使用预下载的语音。** 将 `tts.piper.voice` 设置为以 `.onnx` 结尾的绝对路径：

```yaml
tts:
  piper:
    voice: /path/to/my-custom-voice.onnx
```

**高级参数**（`tts.piper.length_scale` / `noise_scale` / `noise_w_scale` / `volume` / `normalize_audio`、`use_cuda`）与 Piper 的 `SynthesisConfig` 一一对应。在较旧的 `piper-tts` 版本中，这些参数会被忽略。

### 自定义命令提供程序 {#custom-command-providers}

如果你想要的 TTS 引擎（如 VoxCPM、MLX-Kokoro、XTTS CLI、语音克隆脚本，或任何其他提供 CLI 的工具）未得到原生支持，你可以将其作为**命令类型提供程序**接入，而无需编写任何 Python 代码。Hermes 会将输入文本写入一个临时的 UTF-8 文件，运行你的 shell 命令，然后读取该命令生成的音频文件。

在 `tts.providers.&lt;name&gt;` 下声明一个或多个提供程序，并使用 `tts.provider: &lt;name&gt;` 在它们之间切换——这与你在 `edge` 和 `openai` 等内置提供程序之间切换的方式相同。

```yaml
tts:
  provider: voxcpm                 # 选择 tts.providers 下的任意名称
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      timeout: 180
      voice_compatible: true       # 尝试以 Telegram 语音气泡形式发送

    mlx-kokoro:
      type: command
      command: "python -m mlx_kokoro --in {input_path} --out {output_path} --voice {voice}"
      voice: af_sky
      output_format: wav

    piper-custom:                  # 原生 Piper 也通过 tts.piper.voice 支持自定义 .onnx
      type: command
      command: "piper -m /path/to/custom.onnx -f {output_path} < {input_path}"
      output_format: wav
```

#### 占位符 {#placeholders}

你的命令模板可以引用这些占位符。Hermes 会在渲染时替换它们，并根据上下文（裸引号、单引号、双引号）对每个值进行 shell 引用，因此包含空格和其他 shell 敏感字符的路径是安全的。

| 占位符            | 含义                                                |
|-------------------|-----------------------------------------------------|
| `{input_path}`    | Hermes 写入的临时 UTF-8 文本文件的路径               |
| `{text_path}`     | `{input_path}` 的别名                               |
| `{output_path}`   | 命令必须写入音频的路径                              |
| `{format}`        | `mp3` / `wav` / `ogg` / `flac`                     |
| `{voice}`         | `tts.providers.&lt;name&gt;.voice`，未设置时为空          |
| `{model}`         | `tts.providers.&lt;name&gt;.model`                       |
| `{speed}`         | 解析后的速度倍率（提供程序或全局）                  |

使用 `{{` 和 `}}` 表示字面花括号。

#### 可选键 {#optional-keys}

| 键                   | 默认值   | 含义                                                                                                    |
|----------------------|----------|--------------------------------------------------------------------------------------------------------|
| `timeout`            | `120`    | 秒；超时后进程树将被终止（Unix 使用 `killpg`，Windows 使用 `taskkill /T`）。                            |
| `output_format`      | `mp3`    | 可选值：`mp3` / `wav` / `ogg` / `flac`。如果 Hermes 选择路径，则会从输出扩展名自动推断。               |
| `voice_compatible`   | `false`  | 当为 `true` 时，Hermes 会通过 ffmpeg 将 MP3/WAV 输出转换为 Opus/OGG，以便 Telegram 渲染语音气泡。      |
| `max_text_length`    | `5000`   | 在渲染命令之前，输入会被截断到此长度。                                                                 |
| `voice` / `model`    | 空       | 仅作为占位符值传递给命令。                                                                             |
#### 行为说明 {#behavior-notes}

- **内置名称始终优先。** `tts.providers.openai` 条目不会覆盖原生 OpenAI 提供商，因此用户配置无法静默替换内置项。
- **默认交付方式为文档。** 命令提供商在所有平台上以常规音频附件形式交付。如需按提供商启用语音气泡交付，请设置 `voice_compatible: true`。
- **命令失败会反馈给 Agent。** 非零退出、空输出或超时都会返回错误，其中包含命令的 stderr/stdout，方便你从对话中调试提供商。
- **当设置了 `command:` 时，`type: command` 为默认值。** 显式编写 `type: command` 是良好实践，但非必需；包含非空 `command` 字符串的条目会被视为命令提供商。
- **`{input_path}` 与 `{text_path}` 可互换。** 在命令中使用哪个更易读就用哪个。

#### 安全性 {#security}

命令类型的提供商以你的用户权限运行你配置的任何 shell 命令。Hermes 会对占位符值进行引用并强制执行配置的超时时间，但命令模板本身是受信任的本地输入——请像对待 PATH 中的 shell 脚本一样对待它。

## 语音消息转录（STT） {#voice-message-transcription-stt}

在 Telegram、Discord、WhatsApp、Slack 或 Signal 上发送的语音消息会自动转录并作为文本注入对话中。Agent 会将转录内容视为普通文本。

| 提供商 | 质量 | 费用 | API 密钥 |
|----------|---------|------|---------| 
| **本地 Whisper**（默认） | 良好 | 免费 | 无需 |
| **Groq Whisper API** | 良好–最佳 | 免费额度 | `GROQ_API_KEY` |
| **OpenAI Whisper API** | 良好–最佳 | 付费 | `VOICE_TOOLS_OPENAI_KEY` 或 `OPENAI_API_KEY` |

:::info 零配置
当安装了 `faster-whisper` 时，本地转录开箱即用。如果不可用，Hermes 也可以使用常见安装路径（如 `/opt/homebrew/bin`）中的本地 `whisper` CLI，或通过 `HERMES_LOCAL_STT_COMMAND` 自定义命令。
<a id="zero-config"></a>
:::

### 配置 {#configuration}

```yaml
# 在 ~/.hermes/config.yaml 中
stt:
  provider: "local"           # "local" | "groq" | "openai" | "mistral" | "xai"
  local:
    model: "base"             # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"        # whisper-1, gpt-4o-mini-transcribe, gpt-4o-transcribe
  mistral:
    model: "voxtral-mini-latest"  # voxtral-mini-latest, voxtral-mini-2602
  xai:
    model: "grok-stt"         # xAI Grok STT
```

### 提供商详情 {#provider-details}

**本地（faster-whisper）** — 通过 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在本地运行 Whisper。默认使用 CPU，如果可用则使用 GPU。模型大小：

| 模型 | 大小 | 速度 | 质量 |
|-------|------|-------|---------|
| `tiny` | ~75 MB | 最快 | 基础 |
| `base` | ~150 MB | 快 | 良好（默认） |
| `small` | ~500 MB | 中等 | 较好 |
| `medium` | ~1.5 GB | 较慢 | 优秀 |
| `large-v3` | ~3 GB | 最慢 | 最佳 |

**Groq API** — 需要 `GROQ_API_KEY`。当你想要一个免费的托管 STT 选项时，这是一个不错的云端备选方案。
**OpenAI API** — 优先使用 `VOICE_TOOLS_OPENAI_KEY`，若未设置则回退到 `OPENAI_API_KEY`。支持 `whisper-1`、`gpt-4o-mini-transcribe` 和 `gpt-4o-transcribe`。

**Mistral API (Voxtral Transcribe)** — 需要 `MISTRAL_API_KEY`。使用 Mistral 的 [Voxtral Transcribe](https://docs.mistral.ai/capabilities/audio/speech_to_text/) 模型。支持 13 种语言、说话人分离和词级时间戳。安装方式：`pip install hermes-agent[mistral]`。

**xAI Grok STT** — 需要 `XAI_API_KEY`。以 multipart/form-data 格式向 `https://api.x.ai/v1/stt` 发送请求。如果你已经在使用 xAI 进行聊天或 TTS，并希望用一个 API 密钥搞定所有事情，这是个不错的选择。自动检测顺序将其排在 Groq 之后——显式设置 `stt.provider: xai` 可强制使用。

**自定义本地 CLI 回退** — 如果你希望 Hermes 直接调用本地转录命令，请设置 `HERMES_LOCAL_STT_COMMAND`。命令模板支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符。

### 回退行为 {#fallback-behavior}

如果配置的提供商不可用，Hermes 会自动回退：
- **本地 faster-whisper 不可用** → 在尝试云提供商之前，先尝试本地 `whisper` CLI 或 `HERMES_LOCAL_STT_COMMAND`
- **Groq 密钥未设置** → 回退到本地转录，然后 OpenAI
- **OpenAI 密钥未设置** → 回退到本地转录，然后 Groq
- **Mistral 密钥/SDK 未设置** → 在自动检测中跳过；继续尝试下一个可用提供商
- **没有任何可用** → 语音消息会原样传递，并附带一条准确的说明给用户
