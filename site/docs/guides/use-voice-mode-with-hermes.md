---
sidebar_position: 8
title: "使用 Hermes 的语音模式"
description: "一份实用指南，介绍如何在 CLI、Telegram、Discord 以及 Discord 语音频道中设置和使用 Hermes 语音模式"
---

# 使用 Hermes 的语音模式 {#use-voice-mode-with-hermes}

本指南是 [语音模式功能参考](/user-guide/features/voice-mode) 的实践配套文档。

如果说功能页面解释了语音模式能做什么，那么本指南则展示了如何真正用好它。

## 语音模式适合做什么 {#what-voice-mode-is-good-for}

语音模式在以下场景中特别有用：
- 你想要免提的 CLI 工作流
- 你希望在 Telegram 或 Discord 中获得语音回复
- 你希望 Hermes 驻留在 Discord 语音频道中进行实时对话
- 你想快速捕捉想法、调试，或者在走动时进行来回交流，而不是打字

## 选择你的语音模式设置 {#choose-your-voice-mode-setup}

Hermes 实际上提供了三种不同的语音体验。

| 模式 | 最适合的场景 | 平台 |
|---|---|---|
| 交互式麦克风循环 | 编码或研究时个人免提使用 | CLI |
| 聊天中的语音回复 | 在正常消息旁附带语音回复 | Telegram, Discord |
| 实时语音频道机器人 | 在语音频道中进行群组或个人实时对话 | Discord 语音频道 |

一个不错的路径是：
1. 先让文本模式正常工作
2. 其次启用语音回复
3. 最后，如果你想要完整体验，再迁移到 Discord 语音频道

## 第一步：确保普通 Hermes 先正常工作 {#step-1-make-sure-normal-hermes-works-first}

在接触语音模式之前，请确认：
- Hermes 能启动
- 你的提供商已配置好
- Agent 能正常回答文本提示

```bash
hermes
```

问一些简单的问题：

```text
你有哪些可用的工具？
```

如果这一步还不稳定，请先修复文本模式。

## 第二步：安装正确的额外依赖 {#step-2-install-the-right-extras}

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

## 第三步：安装系统依赖 {#step-3-install-system-dependencies}

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

这些依赖的作用：
- `portaudio` → CLI 语音模式的麦克风输入/播放
- `ffmpeg` → TTS 和消息投递的音频转换
- `opus` → Discord 语音编解码器支持
- `espeak-ng` → NeuTTS 的音素化后端

## 第四步：选择 STT 和 TTS 提供商 {#step-4-choose-stt-and-tts-providers}

Hermes 同时支持本地和云端语音栈。

### 最简单/最便宜的设置 {#easiest-cheapest-setup}

使用本地 STT 和免费的 Edge TTS：
- STT 提供商：`local`
- TTS 提供商：`edge`

这通常是最好的起点。

### 环境文件示例 {#environment-file-example}

添加到 `~/.hermes/.env`：

```bash
# 云端 STT 选项（本地不需要密钥）
GROQ_API_KEY=***
VOICE_TOOLS_OPENAI_KEY=***

# 高级 TTS（可选）
ELEVENLABS_API_KEY=***
```

### 提供商推荐 {#provider-recommendations}

#### 语音转文字 {#speech-to-text}

- `local` → 隐私保护和零成本的最佳默认选择
- `groq` → 非常快速的云端转录
- `openai` → 不错的付费备选

#### 文字转语音 {#text-to-speech}

- `edge` → 免费且对大多数用户来说足够好
- `neutts` → 免费的本地/设备端 TTS
- `elevenlabs` → 最佳质量
- `openai` → 不错的折中选择
- `mistral` → 多语言，原生 Opus 支持
### 如果你使用 `hermes setup` {#if-you-use-hermes-setup}

如果在设置向导中选择 NeuTTS，Hermes 会检查 `neutts` 是否已安装。如果缺失，向导会提示 NeuTTS 需要 Python 包 `neutts` 和系统包 `espeak-ng`，并提供安装选项，通过你的平台包管理器安装 `espeak-ng`，然后运行：

```bash
python -m pip install -U neutts[all]
```

如果你跳过安装或安装失败，向导会回退到 Edge TTS。

## 步骤 5：推荐配置 {#step-5-recommended-config}

```yaml
voice:
  record_key: "ctrl+b"
  max_recording_seconds: 120
  auto_tts: false
  beep_enabled: true
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

这对大多数人来说是一个不错的保守默认配置。

如果你想要本地 TTS，可以将 `tts` 块切换为：

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

## 开启语音模式 {#turn-it-on}

启动 Hermes：

```bash
hermes
```

在 CLI 中：

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
5. 如果 TTS 开启，它会朗读回答
6. 循环可自动重启，实现连续使用

### 常用命令 {#useful-commands}

```text
/voice
/voice on
/voice off
/voice tts
/voice status
```

### 好用的 CLI 工作流 {#good-cli-workflows}

#### 快速调试 {#walk-up-debugging}

说：

```text
我老是遇到 Docker 权限错误。帮我调试一下。
```

然后免提继续：
- “再读一遍最后的错误”
- “用更简单的话解释根本原因”
- “现在给我确切的修复方法”

#### 研究 / 头脑风暴 {#research-brainstorming}

适合：
- 边走动边思考
- 口述不成熟的想法
- 让 Hermes 实时整理你的思路

#### 无障碍 / 少打字场景 {#accessibility-low-typing-sessions}

如果打字不方便，语音模式是保持完整 Hermes 循环的最快方式之一。

## 调整 CLI 行为 {#tuning-cli-behavior}

### 静音阈值 {#silence-threshold}

如果 Hermes 开始/停止过于激进，调整：

```yaml
voice:
  silence_threshold: 250
```

阈值越高 = 越不敏感。

### 静音持续时间 {#silence-duration}

如果你在句子之间停顿较多，增加：

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

Hermes 仍然是一个普通的聊天机器人，但可以朗读回复。

### 启动网关 {#start-the-gateway}

```bash
hermes gateway
```

### 开启语音回复 {#turn-on-voice-replies}

在 Telegram 或 Discord 中：

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
| `voice_only` | 仅当用户发送语音时回复语音 |
| `all` | 回复每条消息都语音 |

### 何时使用哪种模式 {#when-to-use-which-mode}

- 如果你只想对语音来源的消息进行语音回复，使用 `/voice on`
- 如果你想要一个始终朗读的完整语音助手，使用 `/voice tts`
### 良好的消息工作流 {#good-messaging-workflows}

#### 手机上的 Telegram 助手 {#telegram-assistant-on-your-phone}

适用场景：
- 你不在电脑前
- 你想发送语音消息并快速获得语音回复
- 你希望 Hermes 像一个便携式研究或运维助手一样工作

#### 带语音输出的 Discord 私信 {#discord-dms-with-spoken-output}

当你希望进行私密交互，避免服务器频道中的 @提及 行为时，这个模式很有用。

## 用例 3：Discord 语音频道 {#use-case-3-discord-voice-channels}

这是最先进的模式。

Hermes 加入 Discord 语音频道，监听用户语音，将其转录，运行正常的 Agent 流水线，然后将语音回复播回到频道中。

## 所需的 Discord 权限 {#required-discord-permissions}

除了常规的文本机器人设置外，请确保机器人拥有以下权限：
- 连接（Connect）
- 发言（Speak）
- 最好启用“语音活动检测”（Use Voice Activity）

另外，在开发者门户中启用特权意图（Privileged Intents）：
- 在线状态意图（Presence Intent）
- 服务器成员意图（Server Members Intent）
- 消息内容意图（Message Content Intent）

## 加入与离开 {#join-and-leave}

在机器人所在的 Discord 文本频道中：

```text
/voice join
/voice leave
/voice status
```

### 加入后会发生什么 {#what-happens-when-joined}

- 用户在语音频道中说话
- Hermes 检测语音边界
- 转录内容会发布到关联的文本频道中
- Hermes 以文本和音频形式回复
- 文本频道就是执行 `/voice join` 的那个频道

### Discord 语音频道使用最佳实践 {#best-practices-for-discord-vc-use}

- 严格限制 `DISCORD_ALLOWED_USERS`
- 一开始使用专用的机器人/测试频道
- 在尝试语音频道模式之前，先在普通文本聊天的语音模式下验证 STT 和 TTS 是否正常工作

## 语音质量建议 {#voice-quality-recommendations}

### 最佳质量配置 {#best-quality-setup}

- STT：本地 `large-v3` 或 Groq `whisper-large-v3`
- TTS：ElevenLabs

### 最佳速度/便利性配置 {#best-speed-convenience-setup}

- STT：本地 `base` 或 Groq
- TTS：Edge

### 最佳零成本配置 {#best-zero-cost-setup}

- STT：本地
- TTS：Edge

## 常见故障模式 {#common-failure-modes}

### “未找到音频设备” {#no-audio-device-found}

安装 `portaudio`。

### “机器人加入了但听不到声音” {#bot-joins-but-hears-nothing}

检查：
- 你的 Discord 用户 ID 是否在 `DISCORD_ALLOWED_USERS` 中
- 你是否处于静音状态
- 特权意图是否已启用
- 机器人是否拥有 Connect/Speak 权限

### “能转录但不说话” {#it-transcribes-but-does-not-speak}

检查：
- TTS 提供商的配置
- ElevenLabs 或 OpenAI 的 API 密钥/配额
- 是否安装了 `ffmpeg`（用于 Edge 转换路径）

### “Whisper 输出乱码” {#whisper-outputs-garbage}

尝试：
- 更安静的环境
- 提高 `silence_threshold`
- 更换 STT 提供商/模型
- 更短、更清晰的语音

### “私信能用，但在服务器频道中不行” {#it-works-in-dms-but-not-in-server-channels}

这通常是提及策略的问题。

默认情况下，除非另行配置，否则机器人在 Discord 服务器文本频道中需要被 `@提及`。

## 建议的第一周设置 {#suggested-first-week-setup}

如果你想以最短路径获得成功：

1. 让文本版 Hermes 正常工作
2. 安装 `hermes-agent[voice]`
3. 使用 CLI 语音模式（本地 STT + Edge TTS）
4. 然后在 Telegram 或 Discord 中启用 `/voice on`
5. 之后再尝试 Discord 语音频道模式

按这个顺序推进，可以保持调试范围较小。

## 下一步阅读 {#where-to-read-next}

- [语音模式功能参考](/user-guide/features/voice-mode)
- [消息网关](/user-guide/messaging)
- [Discord 设置](/user-guide/messaging/discord)
- [Telegram 设置](/user-guide/messaging/telegram)
- [配置](/user-guide/configuration)
