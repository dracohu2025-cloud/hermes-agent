---
sidebar_position: 9
title: "语音与 TTS"
description: "跨平台的文本转语音及语音消息转录功能"
---

# 语音与 TTS

Hermes Agent 支持在所有消息平台上进行文本转语音（TTS）输出和语音消息转录（STT）。

## 文本转语音 (Text-to-Speech)

通过以下五种提供商将文本转换为语音：

| 提供商 | 质量 | 费用 | API Key |
|----------|---------|------|---------|
| **Edge TTS** (默认) | 良好 | 免费 | 无需 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax TTS** | 优秀 | 付费 | `MINIMAX_API_KEY` |
| **NeuTTS** | 良好 | 免费 | 无需 |

### 平台交付方式

| 平台 | 交付形式 | 格式 |
|----------|----------|--------|
| Telegram | 语音气泡（可内嵌播放） | Opus `.ogg` |
| Discord | 语音气泡（Opus/OGG），回退为文件附件 | Opus/MP3 |
| WhatsApp | 音频文件附件 | MP3 |
| CLI | 保存至 `~/.hermes/audio_cache/` | MP3 |

### 配置

```yaml
# 在 ~/.hermes/config.yaml 中
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "neutts"
  edge:
    voice: "en-US-AriaNeural"   # 322 种音色，74 种语言
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 用于覆盖兼容 OpenAI 的 TTS 端点
  minimax:
    model: "speech-2.8-hd"     # speech-2.8-hd (默认), speech-2.8-turbo
    voice_id: "English_Graceful_Lady"  # 详见 https://platform.minimax.io/faq/system-voice-id
    speed: 1                    # 0.5 - 2.0
    vol: 1                      # 0 - 1
    pitch: 0                    # -12 - 12
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

### Telegram 语音气泡与 ffmpeg

Telegram 语音气泡要求音频格式为 Opus/OGG：

- **OpenAI 和 ElevenLabs** 原生生成 Opus 格式 — 无需额外设置
- **Edge TTS** (默认) 输出 MP3，需要 **ffmpeg** 进行转换
- **MiniMax TTS** 输出 MP3，需要 **ffmpeg** 转换为 Telegram 语音气泡格式
- **NeuTTS** 输出 WAV，同样需要 **ffmpeg** 转换为 Telegram 语音气泡格式

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

如果没有 ffmpeg，Edge TTS、MiniMax TTS 和 NeuTTS 的音频将作为普通音频文件发送（可以播放，但显示为矩形播放器而非语音气泡）。

:::tip
如果你想使用语音气泡功能但不想安装 ffmpeg，请切换到 OpenAI 或 ElevenLabs 提供商。
:::

## 语音消息转录 (STT)

在 Telegram、Discord、WhatsApp、Slack 或 Signal 上发送的语音消息会自动转录并作为文本注入到对话中。Agent 会将转录内容视为普通文本处理。

| 提供商 | 质量 | 费用 | API Key |
|----------|---------|------|---------| 
| **Local Whisper** (默认) | 良好 | 免费 | 无需 |
| **Groq Whisper API** | 良好至最佳 | 免费额度 | `GROQ_API_KEY` |
| **OpenAI Whisper API** | 良好至最佳 | 付费 | `VOICE_TOOLS_OPENAI_KEY` 或 `OPENAI_API_KEY` |

:::info 开箱即用
安装 `faster-whisper` 后，本地转录功能即可直接使用。如果不可用，Hermes 也可以使用常见安装路径（如 `/opt/homebrew/bin`）下的本地 `whisper` CLI，或通过 `HERMES_LOCAL_STT_COMMAND` 使用自定义命令。
:::

### 配置

```yaml
# 在 ~/.hermes/config.yaml 中
stt:
  provider: "local"           # "local" | "groq" | "openai" | "mistral"
  local:
    model: "base"             # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"        # whisper-1, gpt-4o-mini-transcribe, gpt-4o-transcribe
  mistral:
    model: "voxtral-mini-latest"  # voxtral-mini-latest, voxtral-mini-2602
```

### 提供商详情

**Local (faster-whisper)** — 通过 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在本地运行 Whisper。默认使用 CPU，如果可用则使用 GPU。模型大小：

| 模型 | 大小 | 速度 | 质量 |
|-------|------|-------|---------|
| `tiny` | ~75 MB | 最快 | 基础 |
| `base` | ~150 MB | 快 | 良好 (默认) |
| `small` | ~500 MB | 中等 | 更好 |
| `medium` | ~1.5 GB | 较慢 | 优秀 |
| `large-v3` | ~3 GB | 最慢 | 最佳 |

**Groq API** — 需要 `GROQ_API_KEY`。当你需要免费的托管式 STT 选项时，这是一个很好的云端回退方案。

**OpenAI API** — 优先使用 `VOICE_TOOLS_OPENAI_KEY`，如果未设置则回退到 `OPENAI_API_KEY`。支持 `whisper-1`、`gpt-4o-mini-transcribe` 和 `gpt-4o-transcribe`。

**Mistral API (Voxtral Transcribe)** — 需要 `MISTRAL_API_KEY`。使用 Mistral 的 [Voxtral Transcribe](https://docs.mistral.ai/capabilities/audio/speech_to_text/) 模型。支持 13 种语言、说话人区分（diarization）和单词级时间戳。请使用 `pip install hermes-agent[mistral]` 安装。

**自定义本地 CLI 回退** — 如果希望 Hermes 直接调用本地转录命令，请设置 `HERMES_LOCAL_STT_COMMAND`。命令模板支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符。

### 回退行为

如果配置的提供商不可用，Hermes 会自动执行以下回退逻辑：
- **Local faster-whisper 不可用** → 在云端提供商之前，尝试本地 `whisper` CLI 或 `HERMES_LOCAL_STT_COMMAND`
- **未设置 Groq Key** → 回退到本地转录，然后是 OpenAI
- **未设置 OpenAI Key** → 回退到本地转录，然后是 Groq
- **未设置 Mistral Key/SDK** → 在自动检测中跳过；继续尝试下一个可用提供商
- **均不可用** → 语音消息将直接透传，并向用户发送一条准确的提示说明
