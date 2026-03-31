---
sidebar_position: 10
title: "语音模式"
description: "与 Hermes Agent 进行实时语音对话 — 支持 CLI、Telegram、Discord（私信、文字频道和语音频道）"
---

# 语音模式

Hermes Agent 在 CLI 和消息平台上支持完整的语音交互。你可以使用麦克风与智能体对话，收听语音回复，并在 Discord 语音频道中进行实时语音对话。

如果你想了解包含推荐配置和实际使用模式的完整设置步骤，请参阅[《使用 Hermes 的语音模式》](/guides/use-voice-mode-with-hermes)。

## 先决条件

在使用语音功能之前，请确保你已具备：

1.  **已安装 Hermes Agent** — `pip install hermes-agent`（参见[安装指南](/getting-started/installation)）
2.  **已配置 LLM 提供商** — 运行 `hermes model` 或在 `~/.hermes/.env` 中设置你偏好的提供商凭据
3.  **基础设置正常工作** — 运行 `hermes` 以验证在启用语音前智能体能响应文本

:::tip
`~/.hermes/` 目录和默认的 `config.yaml` 会在你首次运行 `hermes` 时自动创建。你只需要手动创建 `~/.hermes/.env` 来存放 API 密钥。
:::

## 概览

| 功能 | 平台 | 描述 |
|---------|----------|-------------|
| **交互式语音** | CLI | 按 Ctrl+B 开始录音，智能体自动检测静默并响应 |
| **自动语音回复** | Telegram, Discord | 智能体在发送文本回复的同时发送语音音频 |
| **语音频道** | Discord | 机器人加入语音频道，听取用户发言，并语音回复 |

## 要求

### Python 包

```bash
# CLI 语音模式（麦克风 + 音频播放）
pip install "hermes-agent[voice]"

# Discord + Telegram 消息功能（包含 discord.py[voice] 以支持语音频道）
pip install "hermes-agent[messaging]"

# 高级 TTS (ElevenLabs)
pip install "hermes-agent[tts-premium]"

# 本地 TTS (NeuTTS，可选)
python -m pip install -U neutts[all]

# 一次性安装所有功能
pip install "hermes-agent[all]"
```

| 额外功能 | 包含的包 | 所需用途 |
|-------|----------|-------------|
| `voice` | `sounddevice`, `numpy` | CLI 语音模式 |
| `messaging` | `discord.py[voice]`, `python-telegram-bot`, `aiohttp` | Discord 和 Telegram 机器人 |
| `tts-premium` | `elevenlabs` | ElevenLabs TTS 提供商 |

可选的本地 TTS 提供商：使用 `python -m pip install -U neutts[all]` 单独安装 `neutts`。首次使用时它会自动下载模型。

:::info
`discord.py[voice]` 会自动安装 **PyNaCl**（用于语音加密）和 **opus 绑定**。这是支持 Discord 语音频道所必需的。
:::

### 系统依赖

```bash
# macOS
brew install portaudio ffmpeg opus
brew install espeak-ng   # 用于 NeuTTS

# Ubuntu/Debian
sudo apt install portaudio19-dev ffmpeg libopus0
sudo apt install espeak-ng   # 用于 NeuTTS
```

| 依赖项 | 用途 | 所需场景 |
|-----------|---------|-------------|
| **PortAudio** | 麦克风输入和音频播放 | CLI 语音模式 |
| **ffmpeg** | 音频格式转换 (MP3 → Opus, PCM → WAV) | 所有平台 |
| **Opus** | Discord 语音编解码器 | Discord 语音频道 |
| **espeak-ng** | 音素化后端 | 本地 NeuTTS 提供商 |

### API 密钥

添加到 `~/.hermes/.env`：

```bash
# 语音转文字 — 本地提供商完全不需要密钥
# pip install faster-whisper          # 免费，本地运行，推荐
GROQ_API_KEY=your-key                 # Groq Whisper — 快速，有免费额度（云端）
VOICE_TOOLS_OPENAI_KEY=your-key       # OpenAI Whisper — 付费（云端）

# 文字转语音（可选 — Edge TTS 和 NeuTTS 无需任何密钥即可工作）
ELEVENLABS_API_KEY=***           # ElevenLabs — 高品质
# 上面的 VOICE_TOOLS_OPENAI_KEY 也可启用 OpenAI TTS
```

:::tip
如果安装了 `faster-whisper`，语音模式进行 STT 时**无需任何 API 密钥**。模型（`base` 约 150 MB）会在首次使用时自动下载。
:::

---

## CLI 语音模式

### 快速开始

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

### 工作原理

1.  使用 `hermes` 启动 CLI，并用 `/voice on` 启用语音模式
2.  **按下 Ctrl+B** — 播放一声提示音（880Hz），开始录音
3.  **说话** — 显示实时音频电平条：`● [▁▂▃▅▇▇▅▂] ❯`
4.  **停止说话** — 静默 3 秒后，录音自动停止
5.  播放**两声提示音**（660Hz）确认录音结束
6.  音频通过 Whisper 转录并发送给智能体
7.  如果启用了 TTS，智能体的回复会被朗读出来
8.  录音**自动重新开始** — 无需按任何键即可再次说话

此循环将持续进行，直到你在录音期间按下 **Ctrl+B**（退出连续模式）或连续 3 次录音未检测到语音。

:::tip
录音键可通过 `~/.hermes/config.yaml` 中的 `voice.record_key` 配置（默认：`ctrl+b`）。
:::

### 静默检测

两阶段算法检测你何时说完：

1.  **语音确认** — 等待音频超过 RMS 阈值（200）至少 0.3 秒，容忍音节间的短暂停顿
2.  **结束检测** — 一旦确认有语音，在连续静默 3.0 秒后触发
如果连续 15 秒未检测到任何语音，录音将自动停止。

`silence_threshold` 和 `silence_duration` 都可以在 `config.yaml` 中配置。

### 流式 TTS

当 TTS 启用时，智能体会在生成文本时**逐句**说出它的回复——你无需等待完整的响应：

1.  将文本增量缓冲成完整的句子（至少 20 个字符）
2.  去除 Markdown 格式和 `
### 启动网关

```bash
hermes gateway        # 使用现有配置启动
```

机器人应在几秒内于 Discord 中上线。

### 命令

在机器人所在的 Discord 文本频道中使用以下命令：

```
/voice join      机器人加入你当前的语音频道
/voice channel   /voice join 的别名
/voice leave     机器人断开与语音频道的连接
/voice status    显示语音模式及连接的频道
```

:::info
运行 `/voice join` 前，你必须在一个语音频道中。机器人会加入你所在的同一个语音频道。
:::

### 工作原理

当机器人加入语音频道时，它会：

1.  **独立监听** 每个用户的音频流
2.  **检测静音** — 至少 0.5 秒语音后出现 1.5 秒静音即触发处理
3.  **转录** 音频（通过 Whisper STT，本地、Groq 或 OpenAI）
4.  **通过完整的智能体流水线处理**（会话、工具、记忆）
5.  **通过 TTS 在语音频道中说出**回复

### 文本频道集成

当机器人在语音频道时：

- 转录文本会出现在文本频道中：`[语音] @用户: 你说的话`
- 智能体的回复会以文本形式发送到频道，**同时**在语音频道中说出
- 文本频道是指发出 `/voice join` 命令的那个频道

### 回声预防

机器人在播放 TTS 回复时会自动暂停其音频监听器，防止它听到并重新处理自己的输出。

### 访问控制

只有列在 `DISCORD_ALLOWED_USERS` 中的用户才能通过语音交互。其他用户的音频会被静默忽略。

```bash
# ~/.hermes/.env
DISCORD_ALLOWED_USERS=284102345871466496
```

---

## 配置参考

### config.yaml

```yaml
# 语音录制 (CLI)
voice:
  record_key: "ctrl+b"            # 开始/停止录制的按键
  max_recording_seconds: 120       # 最大录制时长（秒）
  auto_tts: false                  # 语音模式启动时自动启用 TTS
  silence_threshold: 200           # RMS 电平（0-32767），低于此值视为静音
  silence_duration: 3.0            # 自动停止前的静音时长（秒）

# 语音转文本
stt:
  provider: "local"                  # "local" (免费) | "groq" | "openai"
  local:
    model: "base"                    # tiny, base, small, medium, large-v3
  # model: "whisper-1"              # 旧版：当 provider 未设置时使用

# 文本转语音
tts:
  provider: "edge"                 # "edge" (免费) | "elevenlabs" | "openai" | "neutts"
  edge:
    voice: "en-US-AriaNeural"      # 322 种声音，74 种语言
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"    # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"                 # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 可选：用于自托管或 OpenAI 兼容端点的覆盖
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

### 环境变量

```bash
# 语音转文本提供商（本地无需密钥）
# pip install faster-whisper        # 免费本地 STT — 无需 API 密钥
GROQ_API_KEY=...                    # Groq Whisper（快速，有免费额度）
VOICE_TOOLS_OPENAI_KEY=...         # OpenAI Whisper（付费）

# STT 高级覆盖（可选）
STT_GROQ_MODEL=whisper-large-v3-turbo    # 覆盖默认 Groq STT 模型
STT_OPENAI_MODEL=whisper-1               # 覆盖默认 OpenAI STT 模型
GROQ_BASE_URL=https://api.groq.com/openai/v1     # 自定义 Groq 端点
STT_OPENAI_BASE_URL=https://api.openai.com/v1    # 自定义 OpenAI STT 端点

# 文本转语音提供商（Edge TTS 和 NeuTTS 无需密钥）
ELEVENLABS_API_KEY=***             # ElevenLabs（高品质）
# 上面的 VOICE_TOOLS_OPENAI_KEY 也用于启用 OpenAI TTS

# Discord 语音频道
DISCORD_BOT_TOKEN=...
DISCORD_ALLOWED_USERS=...
```
### STT 提供商对比

| 提供商 | 模型 | 速度 | 质量 | 成本 | 需要 API 密钥 |
|----------|-------|-------|---------|------|---------|
| **本地** | `base` | 快（取决于 CPU/GPU） | 良好 | 免费 | 否 |
| **本地** | `small` | 中等 | 更好 | 免费 | 否 |
| **本地** | `large-v3` | 慢 | 最佳 | 免费 | 否 |
| **Groq** | `whisper-large-v3-turbo` | 非常快 (~0.5秒) | 良好 | 免费额度 | 是 |
| **Groq** | `whisper-large-v3` | 快 (~1秒) | 更好 | 免费额度 | 是 |
| **OpenAI** | `whisper-1` | 快 (~1秒) | 良好 | 付费 | 是 |
| **OpenAI** | `gpt-4o-transcribe` | 中等 (~2秒) | 最佳 | 付费 | 是 |

提供商优先级（自动回退）：**本地** > **groq** > **openai**

### TTS 提供商对比

| 提供商 | 质量 | 成本 | 延迟 | 需要密钥 |
|----------|---------|------|---------|-------------|
| **Edge TTS** | 良好 | 免费 | ~1秒 | 否 |
| **ElevenLabs** | 优秀 | 付费 | ~2秒 | 是 |
| **OpenAI TTS** | 良好 | 付费 | ~1.5秒 | 是 |
| **NeuTTS** | 良好 | 免费 | 取决于 CPU/GPU | 否 |

NeuTTS 使用上面配置块中的 `tts.neutts`。

---

## 故障排除

### "未找到音频设备" (CLI)

未安装 PortAudio：

```bash
brew install portaudio    # macOS
sudo apt install portaudio19-dev  # Ubuntu
```

### 机器人在 Discord 服务器频道中不响应

默认情况下，机器人在服务器频道中需要被 @提及。请确保：

1. 输入 `@` 并选择**机器人用户**（带有 #数字标识符），而不是同名的**角色**
2. 或者改用私信（DM）—— 无需提及
3. 或者在 `~/.hermes/.env` 中设置 `DISCORD_REQUIRE_MENTION=false`

### 机器人加入了语音频道但听不到我说话

- 检查你的 Discord 用户 ID 是否在 `DISCORD_ALLOWED_USERS` 中
- 确保你在 Discord 中没有静音
- 机器人需要收到 Discord 的 SPEAKING 事件才能映射你的音频 —— 请在加入频道后几秒内开始说话

### 机器人能听到我说话但不响应

- 确认 STT 可用：安装 `faster-whisper`（无需密钥）或设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`
- 检查 LLM 模型是否已配置且可访问
- 查看网关日志：`tail -f ~/.hermes/logs/gateway.log`

---
### 机器人以文本形式响应但不在语音频道中说话

- TTS 提供商可能出现故障 —— 请检查 API 密钥和配额
- Edge TTS（免费且无需密钥）是默认的备用方案
- 查看日志中是否有 TTS 错误信息

### Whisper 返回乱码文本

幻觉过滤器会自动拦截大多数情况。如果你仍然收到错误的转录文本：

- 尽量在更安静的环境中使用
- 调整配置中的 `silence_threshold`（数值越高，灵敏度越低）
- 尝试使用不同的 STT 模型
