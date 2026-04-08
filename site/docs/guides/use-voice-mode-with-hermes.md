---
sidebar_position: 8
title: "在 Hermes 中使用语音模式"
description: "关于在 CLI、Telegram、Discord 以及 Discord 语音频道中设置和使用 Hermes 语音模式的实用指南"
---

# 在 Hermes 中使用语音模式

本指南是 [语音模式功能参考](/user-guide/features/voice-mode) 的实用配套文档。

如果说功能页面解释了语音模式能做什么，那么本指南将展示如何真正用好它。

## 语音模式的适用场景

语音模式在以下情况下特别有用：
- 你想要解放双手的 CLI 工作流
- 你希望在 Telegram 或 Discord 中获得语音回复
- 你希望 Hermes 待在 Discord 语音频道中进行实时对话
- 你想在走动时快速捕捉想法、调试或进行反复讨论，而不是打字

## 选择你的语音模式设置

Hermes 实际上提供了三种不同的语音体验。

| 模式 | 最适合 | 平台 |
|---|---|---|
| 交互式麦克风循环 | 编码或研究时的个人免提使用 | CLI |
| 聊天中的语音回复 | 随普通消息一起发送的语音响应 | Telegram, Discord |
| 实时语音频道机器人 | 在语音频道（VC）中进行小组或个人实时对话 | Discord 语音频道 |

一个推荐的路径是：
1. 先让文本模式正常工作
2. 其次启用语音回复
3. 如果你想要完整体验，最后再尝试 Discord 语音频道

## 第 1 步：确保普通 Hermes 运行正常

在接触语音模式之前，请确认：
- Hermes 能启动
- 你的 Provider 已配置
- Agent 可以正常回答文本提示词

```bash
hermes
```

问一个简单的问题：

```text
What tools do you have available?
```

如果这还不稳定，请先修复文本模式。

## 第 2 步：安装正确的额外组件

### CLI 麦克风 + 播放

```bash
pip install "hermes-agent[voice]"
```

### 消息平台

```bash
pip install "hermes-agent[messaging]"
```

### 高级 ElevenLabs TTS

```bash
pip install "hermes-agent[tts-premium]"
```

### 本地 NeuTTS（可选）

```bash
python -m pip install -U neutts[all]
```

### 全选

```bash
pip install "hermes-agent[all]"
```

## 第 3 步：安装系统依赖

### macOS

```bash
brew install portaudio ffmpeg opus
brew install espeak-ng
```

### Ubuntu / Debian

```bash
sudo apt install portaudio19-dev ffmpeg libopus0
sudo apt install espeak-ng
```

为什么这些很重要：
- `portaudio` → CLI 语音模式的麦克风输入/播放
- `ffmpeg` → 用于 TTS 和消息传输的音频转换
- `opus` → Discord 语音编解码器支持
- `espeak-ng` → NeuTTS 的音素器后端

## 第 4 步：选择 STT 和 TTS Provider

Hermes 同时支持本地和云端语音技术栈。

### 最简单/最便宜的设置

使用本地 STT 和免费的 Edge TTS：
- STT provider: `local`
- TTS provider: `edge`

这通常是最好的入门选择。

### 环境变量文件示例

添加到 `~/.hermes/.env`：

```bash
# 云端 STT 选项（本地模式不需要 Key）
GROQ_API_KEY=***
VOICE_TOOLS_OPENAI_KEY=***

# 高级 TTS（可选）
ELEVENLABS_API_KEY=***
```

### Provider 推荐

#### 语音转文本 (STT)

- `local` → 隐私和零成本使用的最佳默认选择
- `groq` → 非常快速的云端转录
- `openai` → 良好的付费备选方案

#### 文本转语音 (TTS)

- `edge` → 免费且对大多数用户来说足够好
- `neutts` → 免费的本地/设备端 TTS
- `elevenlabs` → 质量最好
- `openai` → 良好的折中方案

### 如果你使用 `hermes setup`

如果你在设置向导中选择 NeuTTS，Hermes 会检查是否已安装 `neutts`。如果缺失，向导会告知你 NeuTTS 需要 Python 包 `neutts` 和系统包 `espeak-ng`，并询问是否为你安装。它会通过你的平台包管理器安装 `espeak-ng`，然后运行：

```bash
python -m pip install -U neutts[all]
```

如果你跳过安装或安装失败，向导将回退到 Edge TTS。

## 第 5 步：推荐配置

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

对于大多数人来说，这是一个很好的保守默认设置。

如果你想改用本地 TTS，请将 `tts` 块切换为：

```yaml
tts:
  provider: "neutts"
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

## 使用场景 1：CLI 语音模式

### 开启它

启动 Hermes：

```bash
hermes
```

在 CLI 内部输入：

```text
/voice on
```

### 录音流程

默认按键：
- `Ctrl+B`

工作流：
1. 按下 `Ctrl+B`
2. 说话
3. 等待静音检测自动停止录音
4. Hermes 进行转录并响应
5. 如果开启了 TTS，它会读出答案
6. 循环可以自动重新开始以实现连续使用

### 常用命令

```text
/voice
/voice on
/voice off
/voice tts
/voice status
```

### 优秀的 CLI 工作流

#### 边走边调试

说：

```text
I keep getting a docker permission error. Help me debug it.
```

然后继续免提操作：
- "Read the last error again"（再次阅读最后一个错误）
- "Explain the root cause in simpler terms"（用更简单的术语解释根本原因）
- "Now give me the exact fix"（现在给我确切的修复方法）

#### 研究 / 头脑风暴

非常适合：
- 边走边思考
- 口述尚未成型的想法
- 让 Hermes 实时梳理你的思路

#### 无障碍 / 低打字需求时段

如果打字不方便，语音模式是保持完整 Hermes 循环的最快方式之一。

## 调整 CLI 行为

### 静音阈值 (Silence threshold)

如果 Hermes 启动/停止过于灵敏，请调整：

```yaml
voice:
  silence_threshold: 250
```

阈值越高 = 越不灵敏。

### 静音持续时间 (Silence duration)

如果你在句子之间停顿较多，请增加：

```yaml
voice:
  silence_duration: 4.0
```

### 录音键 (Record key)

如果 `Ctrl+B` 与你的终端或 tmux 习惯冲突：

```yaml
voice:
  record_key: "ctrl+space"
```

## 使用场景 2：Telegram 或 Discord 中的语音回复

这种模式比完整的语音频道更简单。

Hermes 保持普通的聊天机器人状态，但可以语音回复。

### 启动网关

```bash
hermes gateway
```

### 开启语音回复

在 Telegram 或 Discord 内部输入：

```text
/voice on
```

或

```text
/voice tts
```

### 模式

| 模式 | 含义 |
|---|---|
| `off` | 仅限文本 |
| `voice_only` | 仅当用户发送语音时才语音回复 |
| `all` | 语音回复每一条消息 |

### 何时使用哪种模式

- 如果你只想针对语音消息获得语音回复，使用 `/voice on`
- 如果你想要一个全天候的完整语音助手，使用 `/voice tts`

### 优秀的消息工作流

#### 手机上的 Telegram 助手

适用于：
- 你不在电脑旁
- 你想发送语音便签并获得快速的语音回复
- 你希望 Hermes 充当便携式研究或运维助手

#### 带有语音输出的 Discord 私聊

当你想要私密交互且不希望有服务器频道的提及（mention）行为时非常有用。

## 使用场景 3：Discord 语音频道

这是最高级的模式。

Hermes 加入 Discord 语音频道（VC），听取用户说话，将其转录，运行正常的 Agent 流水线，并将回复以语音形式播报回频道。

## 必要的 Discord 权限

除了正常的文本机器人设置外，请确保机器人拥有：
- Connect（连接）
- Speak（发言）
- 最好有 Use Voice Activity（使用语音活动检测）

同时在 Developer Portal 中启用特权意图（Privileged Intents）：
- Presence Intent
- Server Members Intent
- Message Content Intent

## 加入与离开

在机器人所在的 Discord 文本频道中：

```text
/voice join
/voice leave
/voice status
```

### 加入后会发生什么

- 用户在语音频道中说话
- Hermes 检测语音边界
- 转录文本会发布在关联的文本频道中
- Hermes 以文本和音频形式做出响应
- 文本频道即为你发出 `/voice join` 命令的那个频道

### Discord 语音频道使用最佳实践

- 严格限制 `DISCORD_ALLOWED_USERS`
- 起初使用专门的机器人/测试频道
- 在尝试语音频道模式之前，先验证 STT 和 TTS 在普通文本聊天语音模式下是否正常工作

## 语音质量建议

### 最高质量设置

- STT: 本地 `large-v3` 或 Groq `whisper-large-v3`
- TTS: ElevenLabs

### 最佳速度/便捷性设置

- STT: 本地 `base` 或 Groq
- TTS: Edge

### 最佳零成本设置

- STT: 本地
- TTS: Edge

## 常见故障模式

### "No audio device found"（未找到音频设备）

安装 `portaudio`。

### "Bot joins but hears nothing"（机器人加入了但听不到声音）
检查以下几点：
- 你的 Discord 用户 ID 是否在 `DISCORD_ALLOWED_USERS` 中
- 你是否处于静音状态
- 是否启用了特权意图（privileged intents）
- 机器人是否拥有连接（Connect）和发言（Speak）权限

### “有转录文字但不说话”

检查以下几点：
- TTS 服务商配置
- ElevenLabs 或 OpenAI 的 API 密钥/额度
- 用于 Edge 转换路径的 `ffmpeg` 是否已安装

### “Whisper 输出乱码/胡言乱语”

尝试：
- 更安静的环境
- 调高 `silence_threshold`（静音阈值）
- 更换 STT 服务商或模型
- 说话更短促、清晰一些

### “在私聊中正常，但在服务器频道中无效”

这通常与提及（mention）策略有关。

默认情况下，除非另有配置，否则在 Discord 服务器文本频道中，机器人需要被 `@mention` 才能响应。

## 建议的首周配置流程

如果你想以最快路径跑通：

1. 先让文本模式的 Hermes 正常工作
2. 安装 `hermes-agent[voice]`
3. 使用 CLI 语音模式，配合本地 STT + Edge TTS
4. 然后在 Telegram 或 Discord 中开启 `/voice on`
5. 只有在上述步骤都成功后，再尝试 Discord 语音频道（VC）模式

这种循序渐进的方式可以缩小调试范围。

## 延伸阅读

- [语音模式功能参考](/user-guide/features/voice-mode)
- [消息网关](/user-guide/messaging)
- [Discord 设置](/user-guide/messaging/discord)
- [Telegram 设置](/user-guide/messaging/telegram)
- [配置指南](/user-guide/configuration)
