---
sidebar_position: 8
title: "使用 Hermes 的语音模式"
description: "一份关于在 CLI、Telegram、Discord 以及 Discord 语音频道中设置和使用 Hermes 语音模式的实用指南"
---

# 使用 Hermes 的语音模式 {#use-voice-mode-with-hermes}

本指南是[语音模式功能参考](/user-guide/features/voice-mode)的实用伴侣。

如果说功能页面解释了语音模式能做什么，那么本指南则展示如何实际用好它。

## 语音模式适合什么场景 {#what-voice-mode-is-good-for}

语音模式在以下场景中特别有用：
- 你想要免手操作的 CLI 工作流
- 你希望在 Telegram 或 Discord 中获得语音回复
- 你希望 Hermes 驻留在 Discord 语音频道中进行实时对话
- 你想在走动时快速捕捉想法、调试或进行来回交流，而不是打字

## 选择你的语音模式设置 {#choose-your-voice-mode-setup}

Hermes 中实际上有三种不同的语音体验。

| 模式 | 最适合 | 平台 |
|---|---|---|
| 交互式麦克风循环 | 编码或研究时个人免手使用 | CLI |
| 聊天中的语音回复 | 在普通消息旁提供语音回复 | Telegram, Discord |
| 实时语音频道机器人 | 在语音频道中进行群组或个人实时对话 | Discord 语音频道 |

一个好的路径是：
1. 先让文本模式正常工作
2. 其次启用语音回复
3. 如果你想要完整体验，最后再转向 Discord 语音频道

## 步骤 1：首先确保普通 Hermes 正常工作 {#step-1-make-sure-normal-hermes-works-first}

在接触语音模式之前，请验证：
- Hermes 能启动
- 你的提供商已配置
- Agent 能正常回答文本提示

```bash
hermes
```

问一些简单的问题：

```text
What tools do you have available?
```

如果这还不稳定，请先修复文本模式。

## 步骤 2：安装正确的额外组件 {#step-2-install-the-right-extras}

### CLI 麦克风 + 播放 {#cli-microphone-playback}

```bash
pip install "hermes-agent[voice]"
```

### 消息平台 {#messaging-platforms}

```bash
pip install "hermes-agent[messaging]"
```

### 高级 ElevenLabs TTS {#premium-elevenlabs-tts}

```bash
pip install "hermes-agent[tts-premium]"
```

### 本地 NeuTTS（可选） {#local-neutts-optional}

```bash
python -m pip install -U neutts[all]
```

### 全部安装 {#everything}

```bash
pip install "hermes-agent[all]"
```

## 步骤 3：安装系统依赖 {#step-3-install-system-dependencies}

### macOS {#macos}

```bash
brew install portaudio ffmpeg opus
brew install espeak-ng
```

### Ubuntu / Debian {#ubuntu-debian}

```bash
sudo apt install portaudio19-dev ffmpeg libopus0
sudo apt install espeak-ng
```

为什么这些很重要：
- `portaudio` → CLI 语音模式的麦克风输入/播放
- `ffmpeg` → TTS 和消息传递的音频转换
- `opus` → Discord 语音编解码器支持
- `espeak-ng` → NeuTTS 的音素化后端

## 步骤 4：选择 STT 和 TTS 提供商 {#step-4-choose-stt-and-tts-providers}

Hermes 支持本地和云端两种语音栈。

### 最简单/最便宜的设置 {#easiest-cheapest-setup}

使用本地 STT 和免费的 Edge TTS：
- STT 提供商：`local`
- TTS 提供商：`edge`

这通常是开始的最佳选择。

### 环境文件示例 {#environment-file-example}

添加到 `~/.hermes/.env`：

```bash
# 云端 STT 选项（本地无需密钥）
GROQ_API_KEY=***
VOICE_TOOLS_OPENAI_KEY=***

# 高级 TTS（可选）
ELEVENLABS_API_KEY=***
```

### 提供商推荐 {#provider-recommendations}

#### 语音转文本 {#speech-to-text}

- `local` → 隐私和零成本使用的最佳默认选择
- `groq` → 非常快的云端转录
- `openai` → 不错的付费备选方案

#### 文本转语音 {#text-to-speech}

- `edge` → 免费，对大多数用户来说足够好
- `neutts` → 免费的本地/设备上 TTS
- `elevenlabs` → 最佳质量
- `openai` → 不错的中间选择
- `mistral` → 多语言，原生 Opus

### 如果你使用 `hermes setup` {#if-you-use-hermes-setup}

如果你在设置向导中选择 NeuTTS，Hermes 会检查 `neutts` 是否已安装。如果缺失，向导会告诉你 NeuTTS 需要 Python 包 `neutts` 和系统包 `espeak-ng`，并为你提供安装选项，用你的平台包管理器安装 `espeak-ng`，然后运行：

```bash
python -m pip install -U neutts[all]
```

如果你跳过安装或安装失败，向导将回退到 Edge TTS。

## 步骤 5：推荐配置 {#step-5-recommended-config}

```yaml
voice:
  record_key: "ctrl+b"
  max_recording_seconds: 120
  auto_tts: false
  silence_threshold: 200
  silence_duration: 3.0

stt:
  provider: "local"
  local:
    model: "base"

tts:
  provider: "edge"
  edge:
    voice: "en-US-AriaNeural"
```

这对大多数人来说是一个不错的保守默认设置。

如果你想要本地 TTS，请将 `tts` 块切换为：

```yaml
tts:
  provider: "neutts"
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

## 用例 1：CLI 语音模式 {#use-case-1-cli-voice-mode}

## 开启它 {#turn-it-on}

启动 Hermes：

```bash
hermes
```

在 CLI 内部：

```text
/voice on
```

### 录音流程 {#recording-flow}

默认按键：
- `Ctrl+B`

工作流程：
1. 按下 `Ctrl+B`
2. 说话
3. 等待静音检测自动停止录音
4. Hermes 转录并回复
5. 如果 TTS 开启，它会说出答案
6. 循环可以自动重启以持续使用

### 有用的命令 {#useful-commands}

```text
/voice
/voice on
/voice off
/voice tts
/voice status
```

### 好的 CLI 工作流 {#good-cli-workflows}

#### 即时调试 {#walk-up-debugging}

说：

```text
I keep getting a docker permission error. Help me debug it.
```

然后继续免手操作：
- "Read the last error again"
- "Explain the root cause in simpler terms"
- "Now give me the exact fix"

#### 研究/头脑风暴 {#research-brainstorming}

非常适合：
- 边走动边思考
- 口述不成熟的想法
- 让 Hermes 实时组织你的思路

#### 无障碍/低打字场景 {#accessibility-low-typing-sessions}

如果打字不方便，语音模式是保持完整 Hermes 循环的最快方式之一。

## 调整 CLI 行为 {#tuning-cli-behavior}

### 静音阈值 {#silence-threshold}

如果 Hermes 开始/停止过于敏感，调整：

```yaml
voice:
  silence_threshold: 250
```

阈值越高 = 越不敏感。

### 静音持续时间 {#silence-duration}

如果你在句子间停顿较多，增加：

```yaml
voice:
  silence_duration: 4.0
```

### 录音键 {#record-key}

如果 `Ctrl+B` 与你的终端或 tmux 习惯冲突：

```yaml
voice:
  record_key: "ctrl+space"
```

## 用例 2：Telegram 或 Discord 中的语音回复 {#use-case-2-voice-replies-in-telegram-or-discord}

此模式比完整的语音频道更简单。

Hermes 保持为普通聊天机器人，但可以说出回复。

### 启动网关 {#start-the-gateway}

```bash
hermes gateway
```

### 开启语音回复 {#turn-on-voice-replies}

在 Telegram 或 Discord 内部：

```text
/voice on
```

或

```text
/voice tts
```

### 模式 {#modes}

| 模式 | 含义 |
|---|---|
| `off` | 仅文本 |
| `voice_only` | 仅当用户发送语音时才说话 |
| `all` | 每次回复都说话 |

### 何时使用哪种模式 {#when-to-use-which-mode}

- `/voice on` 如果你只希望针对源自语音的消息进行语音回复
- `/voice tts` 如果你希望始终拥有一个全语音助手

### 好的消息工作流 {#good-messaging-workflows}

#### 手机上的 Telegram 助手 {#telegram-assistant-on-your-phone}

在以下情况使用：
- 你不在机器旁
- 你想发送语音笔记并获得快速的语音回复
- 你希望 Hermes 像一个便携的研究或运维助手

#### 带有语音输出的 Discord 私信 {#discord-dms-with-spoken-output}

当你想要私密互动，而不涉及服务器频道的提及行为时很有用。

## 用例 3：Discord 语音频道 {#use-case-3-discord-voice-channels}

这是最先进的模式。

Hermes 加入 Discord 语音频道，监听用户语音，转录它，运行正常的 Agent 流程，并将语音回复说回频道中。

## 必需的 Discord 权限 {#required-discord-permissions}

除了普通的文本机器人设置外，请确保机器人拥有：
- 连接
- 说话
- 最好有“使用语音活动”权限

同时，在开发者门户中启用特权意图：
- Presence Intent
- Server Members Intent
- Message Content Intent

## 加入和离开 {#join-and-leave}

在机器人所在的 Discord 文本频道中：

```text
/voice join
/voice leave
/voice status
```

### 加入后会发生什么 {#what-happens-when-joined}

- 用户在语音频道中说话
- Hermes 检测语音边界
- 转录文本会发布在关联的文本频道中
- Hermes 以文本和音频形式回复
- 文本频道是发出 `/voice join` 命令的那个

### Discord 语音频道使用的最佳实践 {#best-practices-for-discord-vc-use}

- 保持 `DISCORD_ALLOWED_USERS` 限制严格
- 开始时使用专用的机器人/测试频道
- 在尝试语音频道模式之前，先在普通文本聊天的语音模式中验证 STT 和 TTS 是否工作

## 语音质量推荐 {#voice-quality-recommendations}

### 最佳质量设置 {#best-quality-setup}

- STT：本地 `large-v3` 或 Groq `whisper-large-v3`
- TTS：ElevenLabs

### 最佳速度/便利性设置 {#best-speed-convenience-setup}

- STT：本地 `base` 或 Groq
- TTS：Edge

### 最佳零成本设置 {#best-zero-cost-setup}

- STT：本地
- TTS：Edge

## 常见故障模式 {#common-failure-modes}

### "No audio device found" {#no-audio-device-found}
安装 `portaudio`。

### “Bot 加入了但什么也听不到” {#bot-joins-but-hears-nothing}

检查：
- 你的 Discord 用户 ID 在 `DISCORD_ALLOWED_USERS` 中
- 你没有静音
- 特权意图已启用
- bot 具有 Connect/Speak 权限

### “它能转录但不说话” {#it-transcribes-but-does-not-speak}

检查：
- TTS 提供商配置
- ElevenLabs 或 OpenAI 的 API 密钥 / 配额
- `ffmpeg` 安装（用于 Edge 转换路径）

### “Whisper 输出乱七八糟的内容” {#whisper-outputs-garbage}

尝试：
- 更安静的环境
- 更高的 `silence_threshold`
- 不同的 STT 提供商/模型
- 更短、更清晰的语音

### “它在 DM 中工作但在服务器频道里不行” {#it-works-in-dms-but-not-in-server-channels}

这通常是提及政策问题。

默认情况下，在 Discord 服务器文本频道中，bot 需要被 `@mention`，除非另有配置。

## 建议的第一周设置 {#suggested-first-week-setup}

如果你想最快获得成功：

1. 让文本 Hermes 正常工作
2. 安装 `hermes-agent[voice]`
3. 在 CLI 语音模式下使用本地 STT + Edge TTS
4. 然后在 Telegram 或 Discord 中启用 `/voice on`
5. 最后，再尝试 Discord VC 模式

这样循序渐进可以保持调试范围最小。

## 接下来读什么 {#where-to-read-next}

- [语音模式功能参考](/user-guide/features/voice-mode)
- [消息网关](/user-guide/messaging)
- [Discord 设置](/user-guide/messaging/discord)
- [Telegram 设置](/user-guide/messaging/telegram)
- [配置](/user-guide/configuration)
