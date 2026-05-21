---
title: "Whisper — OpenAI 的通用语音识别模型"
sidebar_label: "Whisper"
description: "OpenAI 的通用语音识别模型"
---

{/* 此页面由网站/脚本/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="whisper"></a>
# Whisper

OpenAI 的通用语音识别模型。支持 99 种语言、转录、翻译成英语以及语言识别。提供六种模型大小，从 tiny（3900 万参数）到 large（15.5 亿参数）。适用于语音转文字、播客转录或多语言音频处理。最适合用于稳健的多语言 ASR。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/whisper` 安装 |
| 路径 | `optional-skills/mlops/whisper` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `openai-whisper`, `transformers`, `torch` |
| 平台 | linux, macos |
| 标签 | `Whisper`, `Speech Recognition`, `ASR`, `Multimodal`, `Multilingual`, `OpenAI`, `Speech-To-Text`, `Transcription`, `Translation`, `Audio Processing` |

<a id="reference-full-skill-md"></a>
## 参考资料：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="whisper-robust-speech-recognition"></a>
# Whisper - 稳健的语音识别

OpenAI 的多语言语音识别模型。

<a id="when-to-use-whisper"></a>
## 何时使用 Whisper

**适用场景：**
- 语音转文字转录（99 种语言）
- 播客/视频转录
- 会议笔记自动化
- 翻译成英语
- 嘈杂音频转录
- 多语言音频处理

**指标：**
- **72,900+ GitHub 星标**
- 支持 99 种语言
- 基于 68 万小时音频训练
- MIT 许可证

**替代方案：**
- **AssemblyAI**：托管 API，说话人分离
- **Deepgram**：实时流式 ASR
- **Google Speech-to-Text**：云端方案

<a id="quick-start"></a>
## 快速开始

<a id="installation"></a>
### 安装

```bash
# 需要 Python 3.8-3.11
pip install -U openai-whisper

# 需要 ffmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: choco install ffmpeg
```

<a id="basic-transcription"></a>
### 基础转录

```python
import whisper

# 加载模型
model = whisper.load_model("base")

# 转录
result = model.transcribe("audio.mp3")

# 打印文本
print(result["text"])

# 访问片段
for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

<a id="model-sizes"></a>
## 模型大小

```python
# 可用模型
models = ["tiny", "base", "small", "medium", "large", "turbo"]

# 加载特定模型
model = whisper.load_model("turbo")  # 最快，质量佳
```

| 模型 | 参数 | 仅英语 | 多语言 | 速度 | 显存 |
|-------|------------|--------------|--------------|-------|------|
| tiny | 39M | ✓ | ✓ | ~32x | ~1 GB |
| base | 74M | ✓ | ✓ | ~16x | ~1 GB |
| small | 244M | ✓ | ✓ | ~6x | ~2 GB |
| medium | 769M | ✓ | ✓ | ~2x | ~5 GB |
| large | 1550M | ✗ | ✓ | 1x | ~10 GB |
| turbo | 809M | ✗ | ✓ | ~8x | ~6 GB |

**建议**：追求速度与质量的最佳平衡用 `turbo`，原型开发用 `base`

<a id="transcription-options"></a>
## 转录选项

<a id="language-specification"></a>
### 语言指定
```python
# 自动检测语言
result = model.transcribe("audio.mp3")

# 指定语言（更快）
result = model.transcribe("audio.mp3", language="en")

# 支持的语言：en, es, fr, de, it, pt, ru, ja, ko, zh 以及另外 89 种
```

<a id="task-selection"></a>
### 任务选择

```python
# 转录（默认）
result = model.transcribe("audio.mp3", task="transcribe")

# 翻译成英文
result = model.transcribe("spanish.mp3", task="translate")
# 输入：西班牙语音频 → 输出：英文文本
```

<a id="initial-prompt"></a>
### 初始提示

```python
# 通过上下文提高准确率
result = model.transcribe(
    "audio.mp3",
    initial_prompt="这是一期关于机器学习和 AI 的技术播客。"
)

# 有助于：
# - 技术术语
# - 专有名词
# - 领域特定词汇
```

<a id="timestamps"></a>
### 时间戳

```python
# 词级时间戳
result = model.transcribe("audio.mp3", word_timestamps=True)

for segment in result["segments"]:
    for word in segment["words"]:
        print(f"{word['word']} ({word['start']:.2f}s - {word['end']:.2f}s)")
```

<a id="temperature-fallback"></a>
### 温度回退

```python
# 当置信度较低时，使用不同温度重试
result = model.transcribe(
    "audio.mp3",
    temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
)
```

<a id="command-line-usage"></a>
## 命令行使用

```bash
# 基础转录
whisper audio.mp3

# 指定模型
whisper audio.mp3 --model turbo

# 输出格式
whisper audio.mp3 --output_format txt     # 纯文本
whisper audio.mp3 --output_format srt     # 字幕
whisper audio.mp3 --output_format vtt     # WebVTT
whisper audio.mp3 --output_format json    # 带时间戳的 JSON

# 语言
whisper audio.mp3 --language Spanish

# 翻译
whisper spanish.mp3 --task translate
```

<a id="batch-processing"></a>
## 批量处理

```python
import os

audio_files = ["file1.mp3", "file2.mp3", "file3.mp3"]

for audio_file in audio_files:
    print(f"正在转录 {audio_file}...")
    result = model.transcribe(audio_file)

    # 保存到文件
    output_file = audio_file.replace(".mp3", ".txt")
    with open(output_file, "w") as f:
        f.write(result["text"])
```

<a id="real-time-transcription"></a>
## 实时转录

```python
# 对于流式音频，请使用 faster-whisper
# pip install faster-whisper

from faster_whisper import WhisperModel

model = WhisperModel("base", device="cuda", compute_type="float16")

# 流式转录
segments, info = model.transcribe("audio.mp3", beam_size=5)

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

<a id="gpu-acceleration"></a>
## GPU 加速

```python
import whisper

# 自动使用 GPU（如果可用）
model = whisper.load_model("turbo")

# 强制使用 CPU
model = whisper.load_model("turbo", device="cpu")

# 强制使用 GPU
model = whisper.load_model("turbo", device="cuda")

# 在 GPU 上快 10–20 倍
```

<a id="integration-with-other-tools"></a>
## 与其他工具集成

<a id="subtitle-generation"></a>
### 字幕生成

```bash
# 生成 SRT 字幕
whisper video.mp4 --output_format srt --language English

# 输出：video.srt
```

<a id="with-langchain"></a>
### 与 LangChain 配合使用

```python
from langchain.document_loaders import WhisperTranscriptionLoader

loader = WhisperTranscriptionLoader(file_path="audio.mp3")
docs = loader.load()

# 在 RAG 中使用转录结果
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())
```
<a id="extract-audio-from-video"></a>
### 从视频中提取音频

```bash
# 使用 ffmpeg 提取音频
ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav

# 然后进行转录
whisper audio.wav
```

<a id="best-practices"></a>
## 最佳实践

1. **使用 turbo 模型** - 英语的最佳速度/质量比
2. **指定语言** - 比自动检测更快
3. **添加初始提示** - 提升专业术语识别
4. **使用 GPU** - 快 10-20 倍
5. **批量处理** - 更高效
6. **转换为 WAV** - 兼容性更好
7. **分割长音频** - 每段少于 30 分钟
8. **检查语言支持** - 质量因语言而异
9. **使用 faster-whisper** - 比 openai-whisper 快 4 倍
10. **监控显存** - 根据硬件调整模型大小

<a id="performance"></a>
## 性能

| 模型 | 实时因子 (CPU) | 实时因子 (GPU) |
|-------|------------------------|------------------------|
| tiny | ~0.32 | ~0.01 |
| base | ~0.16 | ~0.01 |
| turbo | ~0.08 | ~0.01 |
| large | ~1.0 | ~0.05 |

*实时因子: 0.1 = 比实时快 10 倍*

<a id="language-support"></a>
## 语言支持

支持度最高的语言：
- 英语 (en)
- 西班牙语 (es)
- 法语 (fr)
- 德语 (de)
- 意大利语 (it)
- 葡萄牙语 (pt)
- 俄语 (ru)
- 日语 (ja)
- 韩语 (ko)
- 中文 (zh)

完整列表：共 99 种语言

<a id="limitations"></a>
## 局限性

1. **幻觉** - 可能重复或编造文本
2. **长音频准确度** - 超过 30 分钟的音频时下降
3. **说话人识别** - 不支持说话人区分
4. **口音** - 质量因口音而异
5. **背景噪音** - 可能影响准确性
6. **实时延迟** - 不适合实时字幕

<a id="resources"></a>
## 资源

- **GitHub**: https://github.com/openai/whisper ⭐ 72,900+
- **论文**: https://arxiv.org/abs/2212.04356
- **模型卡片**: https://github.com/openai/whisper/blob/main/model-card.md
- **Colab**: 可在仓库中找到
- **许可证**: MIT
