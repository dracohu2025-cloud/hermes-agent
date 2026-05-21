---
sidebar_position: 9
title: "语音与 TTS"
description: "跨所有平台的文本转语音与语音消息转录"
---

<a id="voice-tts"></a>
# 语音与 TTS

Hermes Agent 支持在所有消息平台上进行文本转语音输出和语音消息转录。

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，则可通过 **[Tool Gateway](tool-gateway.md)** 使用 OpenAI TTS，无需单独的 OpenAI API 密钥。运行 `hermes model` 或 `hermes tools` 即可启用。
:::
<a id="nous-subscribers"></a>

<a id="text-to-speech"></a>
## 文本转语音

通过十个提供商将文本转换为语音：

| 提供商 | 质量 | 费用 | API 密钥 |
|----------|---------|------|---------|
| **Edge TTS**（默认） | 良好 | 免费 | 无需 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax TTS** | 优秀 | 付费 | `MINIMAX_API_KEY` |
| **Mistral (Voxtral TTS)** | 优秀 | 付费 | `MISTRAL_API_KEY` |
| **Google Gemini TTS** | 优秀 | 免费额度 | `GEMINI_API_KEY` |
| **xAI TTS** | 优秀 | 付费 | `XAI_API_KEY` |
| **NeuTTS** | 良好 | 免费（本地） | 无需 |
| **KittenTTS** | 良好 | 免费（本地） | 无需 |
| **Piper** | 良好 | 免费（本地） | 无需 |

<a id="platform-delivery"></a>
### 平台投递

| 平台 | 投递方式 | 格式 |
|----------|----------|--------|
| Telegram | 语音气泡（内联播放） | Opus `.ogg` |
| Discord | 语音气泡（Opus/OGG），回退为文件附件 | Opus/MP3 |
| WhatsApp | 音频文件附件 | MP3 |
| CLI | 保存至 `~/.hermes/audio_cache/` | MP3 |

<a id="configuration"></a>
### 配置

```yaml
# In ~/.hermes/config.yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts" | "kittentts" | "piper"
  speed: 1.0                    # Global speed multiplier (provider-specific settings override this)
  edge:
    voice: "en-US-AriaNeural"   # 322 voices, 74 languages
    speed: 1.0                  # Converted to rate percentage (+/-%)
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # Override for OpenAI-compatible TTS endpoints
    speed: 1.0                  # 0.25 - 4.0
  minimax:
    model: "speech-2.8-hd"     # speech-2.8-hd (default), speech-2.8-turbo
    voice_id: "English_Graceful_Lady"  # See https://platform.minimax.io/faq/system-voice-id
    speed: 1                    # 0.5 - 2.0
    vol: 1                      # 0 - 10
    pitch: 0                    # -12 - 12
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - Neutral (default)
  gemini:
    model: "gemini-2.5-flash-preview-tts"  # or gemini-2.5-pro-preview-tts
    voice: "Kore"               # 30 prebuilt voices: Zephyr, Puck, Kore, Enceladus, Gacrux, etc.
  xai:
    voice_id: "eve"             # or a custom voice ID — see docs below
    language: "en"              # ISO 639-1 code
    sample_rate: 24000          # 22050 / 24000 (default) / 44100 / 48000
    bit_rate: 128000            # MP3 bitrate; only applies when codec=mp3
    # base_url: "https://api.x.ai/v1"   # Override via XAI_BASE_URL env var
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
  kittentts:
    model: KittenML/kitten-tts-nano-0.8-int8   # 25MB int8; also: kitten-tts-micro-0.8 (41MB), kitten-tts-mini-0.8 (80MB)
    voice: Jasper                               # Jasper, Bella, Luna, Bruno, Rosie, Hugo, Kiki, Leo
    speed: 1.0                                  # 0.5 - 2.0
    clean_text: true                            # Expand numbers, currencies, units
  piper:
    voice: en_US-lessac-medium                  # voice name (auto-downloaded) OR absolute path to .onnx
    # voices_dir: ''                            # default: ~/.hermes/cache/piper-voices/
    # use_cuda: false                           # requires onnxruntime-gpu
    # length_scale: 1.0                         # 2.0 = twice as slow
    # noise_scale: 0.667
    # noise_w_scale: 0.8
    # volume: 1.0                               # 0.5 = half as loud
    # normalize_audio: true
```
**速度控制**：全局的 `tts.speed` 值默认适用于所有提供商。每个提供商可以通过自己的 `speed` 设置覆盖（例如 `tts.openai.speed: 1.5`）。提供商特定的速度优先级高于全局值。默认值为 `1.0`（正常速度）。

<a id="input-length-limits"></a>
### 输入长度限制

每个提供商都有文档记录的每次请求输入字符上限。Hermes 在调用提供商之前会截断文本，确保请求不会因长度错误而失败：

| 提供商 | 默认上限（字符数） |
|----------|---------------------|
| Edge TTS | 5000 |
| OpenAI | 4096 |
| xAI | 15000 |
| MiniMax | 10000 |
| Mistral | 4000 |
| Google Gemini | 5000 |
| ElevenLabs | 取决于模型（见下方） |
| NeuTTS | 2000 |
| KittenTTS | 2000 |

**ElevenLabs** 根据配置的 `model_id` 选取上限：

| `model_id` | 上限（字符数） |
|------------|----------------|
| `eleven_flash_v2_5` | 40000 |
| `eleven_flash_v2` | 30000 |
| `eleven_multilingual_v2`（默认）、`eleven_multilingual_v1`、`eleven_english_sts_v2`、`eleven_english_sts_v1` | 10000 |
| `eleven_v3`、`eleven_ttv_v3` | 5000 |
| 未知模型 | 回退至提供商默认值（10000） |

**按提供商覆盖**：在 TTS 配置的提供商部分下使用 `max_text_length:`：

```yaml
tts:
  openai:
    max_text_length: 8192   # 提高或降低提供商上限
```

仅接受正整数。零、负数、非数字或布尔值将回退至提供商默认值，因此错误的配置不会意外禁用截断。

<a id="telegram-voice-bubbles-ffmpeg"></a>
### Telegram 语音气泡与 ffmpeg

Telegram 语音气泡需要 Opus/OGG 音频格式：

- **OpenAI、ElevenLabs 和 Mistral** 原生输出 Opus——无需额外设置
- **Edge TTS**（默认）输出 MP3，需要 **ffmpeg** 进行转换
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

如果没有 ffmpeg，Edge TTS、MiniMax TTS、NeuTTS、KittenTTS 和 Piper 的音频将作为普通音频文件发送（可播放，但会显示为矩形播放器而非语音气泡）。

:::tip
如果你希望在不安装 ffmpeg 的情况下使用语音气泡，可以切换到 OpenAI、ElevenLabs 或 Mistral 提供商。
:::

<a id="xai-custom-voices-voice-cloning"></a>
### xAI 自定义声音（声音克隆）

xAI 支持克隆你的声音并用于 TTS。在 [xAI 控制台](https://console.x.ai/team/default/voice/voice-library) 中创建自定义声音，然后将生成的 `voice_id` 配置到你的配置中：

```yaml
tts:
  provider: xai
  xai:
    voice_id: "nlbqfwie"   # 你的自定义声音 ID
```
关于录音、支持的格式和限制，请参阅 [xAI 自定义语音文档](https://docs.x.ai/developers/model-capabilities/audio/custom-voices)。

<a id="piper-local-44-languages"></a>
### Piper（本地，44 种语言）

Piper 是来自 Open Home Foundation（Home Assistant 维护者）的一个快速、本地的神经 TTS 引擎。它完全在 CPU 上运行，支持 **44 种语言**的预训练语音，并且不需要 API 密钥。

**通过 `hermes tools` 安装** → 语音和 TTS → Piper — Hermes 会为你运行 `pip install piper-tts`。或者手动安装：`pip install piper-tts`。

**切换到 Piper：**

```yaml
tts:
  provider: piper
  piper:
    voice: en_US-lessac-medium
```

在首次调用本地未缓存的语音时，Hermes 会运行 `python -m piper.download_voices &lt;name&gt;` 并将模型（约 20-90MB，取决于质量等级）下载到 `~/.hermes/cache/piper-voices/`。后续调用会复用缓存的模型。

**选择语音。** [完整的语音目录](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md)涵盖了英语、西班牙语、法语、德语、意大利语、荷兰语、葡萄牙语、俄语、波兰语、土耳其语、中文、阿拉伯语、印地语等——每种语言都有 `x_low` / `low` / `medium` / `high` 质量等级。可以在 [rhasspy.github.io/piper-samples](https://rhasspy.github.io/piper-samples/) 试听语音样本。

**使用预下载的语音。** 将 `tts.piper.voice` 设置为以 `.onnx` 结尾的绝对路径：

```yaml
tts:
  piper:
    voice: /path/to/my-custom-voice.onnx
```

**高级参数**（`tts.piper.length_scale` / `noise_scale` / `noise_w_scale` / `volume` / `normalize_audio`、`use_cuda`）与 Piper 的 `SynthesisConfig` 一一对应。在较旧的 `piper-tts` 版本上会被忽略。

<a id="custom-command-providers"></a>
### 自定义命令提供程序

如果你想要的 TTS 引擎（如 VoxCPM、MLX-Kokoro、XTTS CLI、语音克隆脚本，或任何其他提供 CLI 的工具）没有原生支持，你可以将其作为**命令类型提供程序**接入，而无需编写任何 Python 代码。Hermes 会将输入文本写入一个临时的 UTF-8 文件，运行你的 shell 命令，然后读取命令生成的音频文件。

在 `tts.providers.&lt;name&gt;` 下声明一个或多个提供程序，并使用 `tts.provider: &lt;name&gt;` 在它们之间切换——这与你在 `edge` 和 `openai` 等内置提供程序之间切换的方式相同。

```yaml
tts:
  provider: voxcpm                 # 在 tts.providers 下选择任意名称
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

<a id="example-doubao-chinese-seed-tts-2-0"></a>
#### 示例：豆包（中文 seed-tts-2.0）
对于通过字节跳动的 [seed-tts-2.0](https://www.volcengine.com/docs/6561/1257544) 双向流式 API 实现高质量中文 TTS，请安装 [`doubao-speech`](https://pypi.org/project/doubao-speech/) PyPI 包，并将其作为命令提供者接入：

```bash
pip install doubao-speech
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_TOKEN="your-access-token"
```

```yaml
tts:
  provider: doubao
  providers:
    doubao:
      type: command
      command: "doubao-speech say --text-file {input_path} --out {output_path}"
      output_format: mp3
      max_text_length: 1024
      timeout: 30
```

凭据来自你的 shell 环境（`VOLCENGINE_APP_ID` / `VOLCENGINE_ACCESS_TOKEN`）或 `~/.doubao-speech/config.yaml`。通过在命令中添加 `--voice zh-female-warm`（或 `doubao-speech list-voices` 中的其他别名）选择音色。`doubao-speech` 还捆绑了流式 ASR——关于 Hermes 集成，请参见 [下方的 STT 部分](#example-doubao--volcengine-asr)。源码和完整文档：[github.com/Hypnus-Yuan/doubao-speech](https://github.com/Hypnus-Yuan/doubao-speech)。

<a id="placeholders"></a>
#### 占位符

你的命令模板可以引用这些占位符。Hermes 在渲染时替换它们，并根据上下文（裸 / 单引号 / 双引号）对每个值进行 shell 引用，因此包含空格和其他 shell 敏感字符的路径是安全的。

| 占位符            | 含义                                                    |
|------------------|--------------------------------------------------------|
| `{input_path}`   | Hermes 写入的临时 UTF-8 文本文件的路径                     |
| `{text_path}`    | `{input_path}` 的别名                                   |
| `{output_path}`  | 命令必须将音频写入的路径                                   |
| `{format}`       | `mp3` / `wav` / `ogg` / `flac`                         |
| `{voice}`        | `tts.providers.&lt;name&gt;.voice`，未设置时为空                |
| `{model}`        | `tts.providers.&lt;name&gt;.model`                           |
| `{speed}`        | 解析后的速度倍率（提供者或全局）                             |

使用 `{{` 和 `}}` 表示字面花括号。

<a id="optional-keys"></a>
#### 可选键

| 键                  | 默认值   | 含义                                                                                           |
|--------------------|---------|------------------------------------------------------------------------------------------------|
| `timeout`          | `120`   | 秒；到期后进程树会被杀死（Unix `killpg`，Windows `taskkill /T`）。                               |
| `output_format`    | `mp3`   | 可选值：`mp3` / `wav` / `ogg` / `flac`。如果 Hermes 选择路径，则从输出扩展名自动推断。            |
| `voice_compatible` | `false` | 为 `true` 时，Hermes 通过 ffmpeg 将 MP3/WAV 输出转换为 Opus/OGG，以便 Telegram 渲染语音气泡。    |
| `max_text_length`  | `5000`  | 输入将被截断到此长度后再渲染命令。                                                               |
| `voice` / `model`  | 空      | 仅作为占位符值传递给命令。                                                                       |
<a id="behavior-notes"></a>
#### 行为说明

- **内置名称始终优先。** `tts.providers.openai` 条目永远不会覆盖原生的 OpenAI 提供商，因此用户配置无法静默替换内置项。
- **默认交付方式为文档。** 命令提供商在所有平台上都以常规音频附件形式交付。如需为特定提供商启用语音气泡交付，请设置 `voice_compatible: true`。
- **命令失败会反馈给 Agent。** 非零退出码、空输出或超时都会返回错误，其中包含命令的 stderr/stdout，方便你从对话中调试该提供商。
- **当设置了 `command:` 时，`type: command` 为默认值。** 显式编写 `type: command` 是良好实践，但非必需；包含非空 `command` 字符串的条目会被视为命令提供商。
- **`{input_path}` 和 `{text_path}` 可互换使用。** 选择在命令中读起来更顺眼的那一个即可。

<a id="security"></a>
#### 安全性

命令类型的提供商以你的用户权限运行你配置的任何 shell 命令。Hermes 会对占位符值进行引号处理并强制执行配置的超时时间，但命令模板本身是受信任的本地输入——请像对待 PATH 中的 shell 脚本一样对待它。

<a id="voice-message-transcription-stt"></a>
## 语音消息转录（STT）

在 Telegram、Discord、WhatsApp、Slack 或 Signal 上发送的语音消息会自动转录并作为文本注入对话中。Agent 会将转录内容视为普通文本。

| 提供商 | 质量 | 费用 | API 密钥 |
|----------|---------|------|---------| 
| **本地 Whisper**（默认） | 良好 | 免费 | 无需 |
| **Groq Whisper API** | 良好–最佳 | 免费额度 | `GROQ_API_KEY` |
| **OpenAI Whisper API** | 良好–最佳 | 付费 | `VOICE_TOOLS_OPENAI_KEY` 或 `OPENAI_API_KEY` |

:::info 零配置
当安装了 `faster-whisper` 时，本地转录开箱即用。如果该库不可用，Hermes 也可以使用来自常见安装路径（如 `/opt/homebrew/bin`）的本地 `whisper` CLI，或通过 `HERMES_LOCAL_STT_COMMAND` 使用自定义命令。
<a id="zero-config"></a>
:::

<a id="configuration"></a>
### 配置

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

<a id="provider-details"></a>
### 提供商详情

**本地（faster-whisper）** — 通过 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在本地运行 Whisper。默认使用 CPU，如果可用则使用 GPU。模型大小：

| 模型 | 大小 | 速度 | 质量 |
|-------|------|-------|---------|
| `tiny` | 约 75 MB | 最快 | 基础 |
| `base` | 约 150 MB | 快 | 良好（默认） |
| `small` | 约 500 MB | 中等 | 较好 |
| `medium` | 约 1.5 GB | 较慢 | 优秀 |
| `large-v3` | 约 3 GB | 最慢 | 最佳 |

**Groq API** — 需要 `GROQ_API_KEY`。当你想要一个免费的托管 STT 选项时，这是一个不错的云端备选方案。
**OpenAI API** — 首先读取 `VOICE_TOOLS_OPENAI_KEY`，若未设置则回退到 `OPENAI_API_KEY`。支持 `whisper-1`、`gpt-4o-mini-transcribe` 和 `gpt-4o-transcribe`。

**Mistral API (Voxtral Transcribe)** — 需要 `MISTRAL_API_KEY`。使用 Mistral 的 [Voxtral Transcribe](https://docs.mistral.ai/capabilities/audio/speech_to_text/) 模型。支持 13 种语言、说话人分离和词级时间戳。通过 `pip install hermes-agent[mistral]` 安装。

**xAI Grok STT** — 需要 `XAI_API_KEY`。以 multipart/form-data 形式发送请求到 `https://api.x.ai/v1/stt`。如果你已经在使用 xAI 进行聊天或 TTS，并希望用一个 API Key 搞定所有功能，这是个好选择。自动检测顺序将其置于 Groq 之后——可显式设置 `stt.provider: xai` 强制使用。

**自定义本地 CLI 回退** — 设置 `HERMES_LOCAL_STT_COMMAND` 可以让 Hermes 直接调用本地转录命令。命令模板支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符。你的命令必须将 `.txt` 转录结果写入 `{output_dir}` 下的某个位置。

<a id="example-doubao-volcengine-asr"></a>
#### 示例：豆包 / 火山引擎 ASR

如果你使用 [`doubao-speech`](https://pypi.org/project/doubao-speech/) 进行豆包 TTS（参见[上文](#example-doubao-chinese-seed-tts-20)），同一个包也能通过本地命令 STT 接口处理语音转文字：

```bash
pip install doubao-speech
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_TOKEN="your-access-token"
export HERMES_LOCAL_STT_COMMAND='doubao-speech transcribe {input_path} --out {output_dir}/transcript.txt'
```

```yaml
stt:
  provider: local_command
```

Hermes 会将接收到的语音消息写入 `{input_path}`，运行该命令，然后读取 `{output_dir}` 下生成的 `.txt` 文件。语言由火山引擎大模型端点自动检测。

<a id="fallback-behavior"></a>
### 回退行为

如果配置的提供商不可用，Hermes 会自动回退：
- **本地 faster-whisper 不可用** → 在尝试云提供商之前，先尝试本地 `whisper` CLI 或 `HERMES_LOCAL_STT_COMMAND`
- **Groq key 未设置** → 回退到本地转录，再回退到 OpenAI
- **OpenAI key 未设置** → 回退到本地转录，再回退到 Groq
- **Mistral key/SDK 未设置** → 在自动检测中被跳过；继续尝试下一个可用的提供商
- **全都不可用** → 语音消息直接透传，并附上准确提示告知用户
