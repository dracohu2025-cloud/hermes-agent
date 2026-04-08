---
sidebar_position: 9
title: "语音与 TTS"
description: "跨平台文本转语音及语音消息转录功能"
---

# 语音与 TTS

Hermes Agent 支持在所有消息平台上进行文本转语音（TTS）输出和语音消息转录（STT）。

## 文本转语音 (Text-to-Speech)

支持通过以下五种服务商将文本转换为语音：

| 服务商 | 质量 | 成本 | API Key |
|----------|---------|------|---------|
| **Edge TTS** (默认) | 良好 | 免费 | 无需 |
| **ElevenLabs** | 极佳 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax TTS** | 极佳 | 付费 | `MINIMAX_API_KEY` |
| **NeuTTS** | 良好 | 免费 | 无需 |

### 平台交付方式

| 平台 | 交付形式 | 格式 |
|----------|----------|--------|
| Telegram | 语音气泡 (行内播放) | Opus `.ogg` |
| Discord | 语音气泡 (Opus/OGG)，失败则回退为文件附件 | Opus/MP3 |
| WhatsApp | 音频文件附件 | MP3 |
| CLI | 保存至 `~/.hermes/audio_cache/` | MP3 |

### 配置

```yaml
# 位于 ~/.hermes/config.yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "neutts"
  edge:
    voice: "en-US-AriaNeural"   # 322 种声音，74 种语言
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 用于覆盖 OpenAI 兼容的 TTS 端点
  minimax:
    model: "speech-2.8-hd"     # speech-2.8-hd (默认), speech-2.8-turbo
    voice_id: "English_Graceful_Lady"  # 详见 https://platform.minimax.io/faq/system-voice-id
    speed: 1                    # 0.5 - 2.0
    vol: 1                      # 0 - 10
    pitch: 0                    # -12 - 12
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

### Telegram 语音气泡与 ffmpeg

Telegram 语音气泡需要 Opus/OGG 音频格式：

- **OpenAI 和 ElevenLabs** 原生生成 Opus 格式 —— 无需额外设置。
- **Edge TTS** (默认) 输出 MP3，需要 **ffmpeg** 进行转换。
- **MiniMax TTS** 输出 MP3，在 Telegram 中显示为语音气泡时需要 **ffmpeg** 转换。
- **NeuTTS** 输出 WAV，在 Telegram 中显示为语音气泡时也需要 **ffmpeg** 转换。

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

如果没有安装 ffmpeg，Edge TTS、MiniMax TTS 和 NeuTTS 的音频将作为普通音频文件发送（可以播放，但显示为矩形播放器而非语音气泡）。

:::tip 提示
如果你想在不安装 ffmpeg 的情况下使用语音气泡，请切换到 OpenAI 或 ElevenLabs 服务商。
:::

## 语音消息转录 (STT)

在 Telegram、Discord、WhatsApp、Slack 或 Signal 上发送的语音消息会被自动转录，并作为文本注入对话。Agent 会将转录内容视为普通文本。

| 服务商 | 质量 | 成本 | API Key |
|----------|---------|------|---------| 
| **本地 Whisper** (默认) | 良好 | 免费 | 无需 |
| **Groq Whisper API** | 良好至极佳 | 免费层级 | `GROQ_API_KEY` |
| **OpenAI Whisper API** | 良好至极佳 | 付费 | `VOICE_TOOLS_OPENAI_KEY` 或 `OPENAI_API_KEY` |

:::info 零配置
只要安装了 `faster-whisper`，本地转录功能即可开箱即用。如果不可用，Hermes 也可以使用常见安装路径（如 `/opt/homebrew/bin`）下的本地 `whisper` CLI，或者通过 `HERMES_LOCAL_STT_COMMAND` 使用自定义命令。
:::

### 配置

```yaml
# 位于 ~/.hermes/config.yaml
stt:
  provider: "local"           # "local" | "groq" | "openai"
  local:
    model: "base"             # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"        # whisper-1, gpt-4o-mini-transcribe, gpt-4o-transcribe
```

### 服务商详情

**本地 (faster-whisper)** — 通过 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在本地运行 Whisper。默认使用 CPU，如有 GPU 则使用 GPU。模型大小如下：

| 模型 | 大小 | 速度 | 质量 |
|-------|------|-------|---------|
| `tiny` | ~75 MB | 最快 | 基础 |
| `base` | ~150 MB | 快 | 良好 (默认) |
| `small` | ~500 MB | 中等 | 较好 |
| `medium` | ~1.5 GB | 较慢 | 优秀 |
| `large-v3` | ~3 GB | 最慢 | 最佳 |

**Groq API** — 需要 `GROQ_API_KEY`。当你需要免费的云端托管 STT 选项时，这是一个很好的备选方案。

**OpenAI API** — 优先使用 `VOICE_TOOLS_OPENAI_KEY`，若无则回退到 `OPENAI_API_KEY`。支持 `whisper-1`、`gpt-4o-mini-transcribe` 和 `gpt-4o-transcribe`。

**自定义本地 CLI 回退** — 如果你想让 Hermes 直接调用本地转录命令，请设置 `HERMES_LOCAL_STT_COMMAND`。该命令模板支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符。

### 回退行为

如果配置的服务商不可用，Hermes 会自动进行回退：
- **本地 faster-whisper 不可用** → 在尝试云端服务商之前，先尝试本地 `whisper` CLI 或 `HERMES_LOCAL_STT_COMMAND`。
- **未设置 Groq key** → 回退到本地转录，然后是 OpenAI。
- **未设置 OpenAI key** → 回退到本地转录，然后是 Groq。
- **全部不可用** → 语音消息将直接透传，并向用户发送一条准确的提示说明。
