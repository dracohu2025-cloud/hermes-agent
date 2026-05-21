---
title: "Audiocraft 音频生成 — AudioCraft：MusicGen 文本生成音乐，AudioGen 文本生成声音"
sidebar_label: "Audiocraft 音频生成"
description: "AudioCraft：MusicGen 文本生成音乐，AudioGen 文本生成声音"
---

{/* 此页面由脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，不要编辑此页面。 */}

<a id="audiocraft-audio-generation"></a>
# Audiocraft 音频生成

AudioCraft：MusicGen 文本生成音乐，AudioGen 文本生成声音。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 捆绑（默认安装） |
| 路径 | `skills/mlops/models/audiocraft` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `audiocraft`, `torch>=2.0.0`, `transformers>=4.30.0` |
| 平台 | linux, macos |
| 标签 | `多模态`, `音频生成`, `文本生成音乐`, `文本生成音频`, `MusicGen` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。技能激活时，Agent 将看到这些指令。
:::

# AudioCraft：音频生成

使用 Meta 的 AudioCraft 进行文本生成音乐和文本生成音频的全面指南，支持 MusicGen、AudioGen 和 EnCodec。

<a id="when-to-use-audiocraft"></a>
## 何时使用 AudioCraft

**使用 AudioCraft 的场景：**
- 需要根据文本描述生成音乐
- 创建音效和环境音频
- 构建音乐生成应用
- 需要基于旋律条件的音乐生成
- 想要立体声音频输出
- 需要可控制的音乐生成及风格迁移

**主要特性：**
- **MusicGen**：带旋律条件的文本生成音乐
- **AudioGen**：文本生成音效
- **EnCodec**：高保真神经音频编解码器
- **多模型大小**：小（300M）到大（3.3B）
- **立体声支持**：完整立体声音频生成
- **风格条件**：MusicGen-Style 基于参考的生成

**备选方案：**
- **Stable Audio**：用于更长的商业音乐生成
- **Bark**：用于带音乐/音效的文本转语音
- **Riffusion**：基于频谱图的音乐生成
- **OpenAI Jukebox**：带歌词的原始音频生成

<a id="quick-start"></a>
## 快速开始

<a id="installation"></a>
### 安装

```bash
# From PyPI
pip install audiocraft

# From GitHub (latest)
pip install git+https://github.com/facebookresearch/audiocraft.git

# Or use HuggingFace Transformers
pip install transformers torch torchaudio
```

<a id="basic-text-to-music-audiocraft"></a>
### 基础文本生成音乐（AudioCraft）

```python
import torchaudio
from audiocraft.models import MusicGen

# Load model
model = MusicGen.get_pretrained('facebook/musicgen-small')

# Set generation parameters
model.set_generation_params(
    duration=8,  # seconds
    top_k=250,
    temperature=1.0
)

# Generate from text
descriptions = ["happy upbeat electronic dance music with synths"]
wav = model.generate(descriptions)

# Save audio
torchaudio.save("output.wav", wav[0].cpu(), sample_rate=32000)
```

<a id="using-huggingface-transformers"></a>
### 使用 HuggingFace Transformers

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy

# Load model and processor
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
model.to("cuda")

# Generate music
inputs = processor(
    text=["80s pop track with bassy drums and synth"],
    padding=True,
    return_tensors="pt"
).to("cuda")

audio_values = model.generate(
    **inputs,
    do_sample=True,
    guidance_scale=3,
    max_new_tokens=256
)

# Save
sampling_rate = model.config.audio_encoder.sampling_rate
scipy.io.wavfile.write("output.wav", rate=sampling_rate, data=audio_values[0, 0].cpu().numpy())
```
<a id="text-to-sound-with-audiogen"></a>
### 使用 AudioGen 进行文本到声音生成

```python
from audiocraft.models import AudioGen

# Load AudioGen
model = AudioGen.get_pretrained('facebook/audiogen-medium')

model.set_generation_params(duration=5)

# Generate sound effects
descriptions = ["dog barking in a park with birds chirping"]
wav = model.generate(descriptions)

torchaudio.save("sound.wav", wav[0].cpu(), sample_rate=16000)
```

<a id="core-concepts"></a>
## 核心概念

<a id="architecture-overview"></a>
### 架构概览

<!-- ascii-guard-ignore -->
```
AudioCraft Architecture:
┌──────────────────────────────────────────────────────────────┐
│                    Text Encoder (T5)                          │
│                         │                                     │
│                    Text Embeddings                            │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│              Transformer Decoder (LM)                         │
│     Auto-regressively generates audio tokens                  │
│     Using efficient token interleaving patterns               │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                EnCodec Audio Decoder                          │
│        Converts tokens back to audio waveform                 │
└──────────────────────────────────────────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

<a id="model-variants"></a>
### 模型变体

| Model | Size | Description | Use Case |
|-------|------|-------------|----------|
| `musicgen-small` | 300M | 文本到音乐 | 快速生成 |
| `musicgen-medium` | 1.5B | 文本到音乐 | 平衡 |
| `musicgen-large` | 3.3B | 文本到音乐 | 最佳质量 |
| `musicgen-melody` | 1.5B | 文本 + 旋律 | 旋律控制 |
| `musicgen-melody-large` | 3.3B | 文本 + 旋律 | 最佳旋律 |
| `musicgen-stereo-*` | 可变 | 立体声输出 | 立体声生成 |
| `musicgen-style` | 1.5B | 风格迁移 | 基于参考 |
| `audiogen-medium` | 1.5B | 文本到声音 | 音效 |

<a id="generation-parameters"></a>
### 生成参数

| Parameter | Default | Description |
|-----------|---------|-------------|
| `duration` | 8.0 | 时长（秒，范围为1-120） |
| `top_k` | 250 | top-k采样 |
| `top_p` | 0.0 | 核采样（0表示禁用） |
| `temperature` | 1.0 | 采样温度 |
| `cfg_coef` | 3.0 | 无分类器引导系数 |

<a id="musicgen-usage"></a>
## MusicGen 使用方法

<a id="text-to-music-generation"></a>
### 文本到音乐生成

```python
from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained('facebook/musicgen-medium')

# Configure generation
model.set_generation_params(
    duration=30,          # Up to 30 seconds
    top_k=250,            # Sampling diversity
    top_p=0.0,            # 0 = use top_k only
    temperature=1.0,      # Creativity (higher = more varied)
    cfg_coef=3.0          # Text adherence (higher = stricter)
)

# Generate multiple samples
descriptions = [
    "epic orchestral soundtrack with strings and brass",
    "chill lo-fi hip hop beat with jazzy piano",
    "energetic rock song with electric guitar"
]

# Generate (returns [batch, channels, samples])
wav = model.generate(descriptions)

# Save each
for i, audio in enumerate(wav):
    torchaudio.save(f"music_{i}.wav", audio.cpu(), sample_rate=32000)
```
<a id="melody-conditioned-generation"></a>
### 旋律条件生成

```python
from audiocraft.models import MusicGen
import torchaudio

# 加载旋律模型
model = MusicGen.get_pretrained('facebook/musicgen-melody')
model.set_generation_params(duration=30)

# 加载旋律音频
melody, sr = torchaudio.load("melody.wav")

# 使用旋律条件生成
descriptions = ["acoustic guitar folk song"]
wav = model.generate_with_chroma(descriptions, melody, sr)

torchaudio.save("melody_conditioned.wav", wav[0].cpu(), sample_rate=32000)
```

<a id="stereo-generation"></a>
### 立体声生成

```python
from audiocraft.models import MusicGen

# 加载立体声模型
model = MusicGen.get_pretrained('facebook/musicgen-stereo-medium')
model.set_generation_params(duration=15)

descriptions = ["ambient electronic music with wide stereo panning"]
wav = model.generate(descriptions)

# wav 形状：[batch, 2, samples] 对应立体声
print(f"Stereo shape: {wav.shape}")  # [1, 2, 480000]
torchaudio.save("stereo.wav", wav[0].cpu(), sample_rate=32000)
```

<a id="audio-continuation"></a>
### 音频续写

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration

processor = AutoProcessor.from_pretrained("facebook/musicgen-medium")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium")

# 加载要续写的音频
import torchaudio
audio, sr = torchaudio.load("intro.wav")

# 结合文本和音频进行处理
inputs = processor(
    audio=audio.squeeze().numpy(),
    sampling_rate=sr,
    text=["continue with a epic chorus"],
    padding=True,
    return_tensors="pt"
)

# 生成续写内容
audio_values = model.generate(**inputs, do_sample=True, guidance_scale=3, max_new_tokens=512)
```

<a id="musicgen-style-usage"></a>
## MusicGen-Style 用法

<a id="style-conditioned-generation"></a>
### 风格条件生成

```python
from audiocraft.models import MusicGen

# 加载风格模型
model = MusicGen.get_pretrained('facebook/musicgen-style')

# 配置生成参数，设定风格
model.set_generation_params(
    duration=30,
    cfg_coef=3.0,
    cfg_coef_beta=5.0  # 风格影响程度
)

# 配置风格调节器
model.set_style_conditioner_params(
    eval_q=3,          # RVQ 量化器数量（1-6）
    excerpt_length=3.0  # 风格片段长度
)

# 加载风格参考
style_audio, sr = torchaudio.load("reference_style.wav")

# 基于文本 + 风格生成
descriptions = ["upbeat dance track"]
wav = model.generate_with_style(descriptions, style_audio, sr)
```

<a id="style-only-generation-no-text"></a>
### 纯风格生成（无文本）

```python
# 不提供文本提示，直接生成与风格匹配的内容
model.set_generation_params(
    duration=30,
    cfg_coef=3.0,
    cfg_coef_beta=None  # 纯风格模式禁用双 CFG
)

wav = model.generate_with_style([None], style_audio, sr)
```

<a id="audiogen-usage"></a>
## AudioGen 用法

<a id="sound-effect-generation"></a>
### 音效生成

```python
from audiocraft.models import AudioGen
import torchaudio

model = AudioGen.get_pretrained('facebook/audiogen-medium')
model.set_generation_params(duration=10)

# 生成多种声音
descriptions = [
    "thunderstorm with heavy rain and lightning",
    "busy city traffic with car horns",
    "ocean waves crashing on rocks",
    "crackling campfire in forest"
]

wav = model.generate(descriptions)

for i, audio in enumerate(wav):
    torchaudio.save(f"sound_{i}.wav", audio.cpu(), sample_rate=16000)
```
<a id="encodec-usage"></a>
## EnCodec 用法

<a id="audio-compression"></a>
### 音频压缩

```python
from audiocraft.models import CompressionModel
import torch
import torchaudio

# 加载 EnCodec
model = CompressionModel.get_pretrained('facebook/encodec_32khz')

# 加载音频
wav, sr = torchaudio.load("audio.wav")

# 确保采样率正确
if sr != 32000:
    resampler = torchaudio.transforms.Resample(sr, 32000)
    wav = resampler(wav)

# 编码为 token
with torch.no_grad():
    encoded = model.encode(wav.unsqueeze(0))
    codes = encoded[0]  # 音频编码

# 解码回音频
with torch.no_grad():
    decoded = model.decode(codes)

torchaudio.save("reconstructed.wav", decoded[0].cpu(), sample_rate=32000)
```

<a id="common-workflows"></a>
## 常见工作流程

<a id="workflow-1-music-generation-pipeline"></a>
### 工作流程 1：音乐生成管道

```python
import torch
import torchaudio
from audiocraft.models import MusicGen

class MusicGenerator:
    def __init__(self, model_name="facebook/musicgen-medium"):
        self.model = MusicGen.get_pretrained(model_name)
        self.sample_rate = 32000

    def generate(self, prompt, duration=30, temperature=1.0, cfg=3.0):
        self.model.set_generation_params(
            duration=duration,
            top_k=250,
            temperature=temperature,
            cfg_coef=cfg
        )

        with torch.no_grad():
            wav = self.model.generate([prompt])

        return wav[0].cpu()

    def generate_batch(self, prompts, duration=30):
        self.model.set_generation_params(duration=duration)

        with torch.no_grad():
            wav = self.model.generate(prompts)

        return wav.cpu()

    def save(self, audio, path):
        torchaudio.save(path, audio, sample_rate=self.sample_rate)

# 用法示例
generator = MusicGenerator()
audio = generator.generate(
    "epic cinematic orchestral music",
    duration=30,
    temperature=1.0
)
generator.save(audio, "epic_music.wav")
```

<a id="workflow-2-sound-design-batch-processing"></a>
### 工作流程 2：音效批量处理

```python
import json
from pathlib import Path
from audiocraft.models import AudioGen
import torchaudio

def batch_generate_sounds(sound_specs, output_dir):
    """
    根据规格批量生成音效。

    参数：
        sound_specs: 列表，元素为 {"name": str, "description": str, "duration": float}
        output_dir: 输出目录路径
    """
    model = AudioGen.get_pretrained('facebook/audiogen-medium')
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    results = []

    for spec in sound_specs:
        model.set_generation_params(duration=spec.get("duration", 5))

        wav = model.generate([spec["description"]])

        output_path = output_dir / f"{spec['name']}.wav"
        torchaudio.save(str(output_path), wav[0].cpu(), sample_rate=16000)

        results.append({
            "name": spec["name"],
            "path": str(output_path),
            "description": spec["description"]
        })

    return results

# 用法示例
sounds = [
    {"name": "explosion", "description": "massive explosion with debris", "duration": 3},
    {"name": "footsteps", "description": "footsteps on wooden floor", "duration": 5},
    {"name": "door", "description": "wooden door creaking and closing", "duration": 2}
]

results = batch_generate_sounds(sounds, "sound_effects/")
```
<a id="workflow-3-gradio-demo"></a>
### 工作流 3：Gradio 演示

```python
import gradio as gr
import torch
import torchaudio
from audiocraft.models import MusicGen

model = MusicGen.get_pretrained('facebook/musicgen-small')

def generate_music(prompt, duration, temperature, cfg_coef):
    model.set_generation_params(
        duration=duration,
        temperature=temperature,
        cfg_coef=cfg_coef
    )

    with torch.no_grad():
        wav = model.generate([prompt])

    # 保存到临时文件
    path = "temp_output.wav"
    torchaudio.save(path, wav[0].cpu(), sample_rate=32000)
    return path

demo = gr.Interface(
    fn=generate_music,
    inputs=[
        gr.Textbox(label="音乐描述", placeholder="欢快的电子舞曲"),
        gr.Slider(1, 30, value=8, label="时长（秒）"),
        gr.Slider(0.5, 2.0, value=1.0, label="温度"),
        gr.Slider(1.0, 10.0, value=3.0, label="CFG 系数")
    ],
    outputs=gr.Audio(label="生成的音乐"),
    title="MusicGen 演示"
)

demo.launch()
```

<a id="performance-optimization"></a>
## 性能优化

<a id="memory-optimization"></a>
### 内存优化

```python
# 使用更小的模型
model = MusicGen.get_pretrained('facebook/musicgen-small')

# 在每次生成后清除缓存
torch.cuda.empty_cache()

# 生成更短的时长
model.set_generation_params(duration=10)  # 代替 30

# 使用半精度
model = model.half()
```

<a id="batch-processing-efficiency"></a>
### 批处理效率

```python
# 一次处理多个提示（更高效）
descriptions = ["prompt1", "prompt2", "prompt3", "prompt4"]
wav = model.generate(descriptions)  # 单次批处理

# 而不是：
for desc in descriptions:
    wav = model.generate([desc])  # 多次批处理（较慢）
```

<a id="gpu-memory-requirements"></a>
### GPU 内存需求

| 模型 | FP32 VRAM | FP16 VRAM |
|-------|-----------|-----------|
| musicgen-small | ~4GB | ~2GB |
| musicgen-medium | ~8GB | ~4GB |
| musicgen-large | ~16GB | ~8GB |

<a id="common-issues"></a>
## 常见问题

| 问题 | 解决方案 |
|-------|----------|
| CUDA 内存不足 | 使用更小的模型，减少时长 |
| 质量差 | 增加 cfg_coef，优化提示词 |
| 生成太短 | 检查最大时长设置 |
| 音频伪影 | 尝试不同的温度值 |
| 立体声无法工作 | 使用立体声模型变体 |

<a id="references"></a>
## 参考

- **[进阶用法](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/models/audiocraft/references/advanced-usage.md)** - 训练、微调、部署
- **[故障排除](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/models/audiocraft/references/troubleshooting.md)** - 常见问题及解决方案

<a id="resources"></a>
## 资源

- **GitHub**: https://github.com/facebookresearch/audiocraft
- **论文（MusicGen）**: https://arxiv.org/abs/2306.05284
- **论文（AudioGen）**: https://arxiv.org/abs/2209.15352
- **HuggingFace**: https://huggingface.co/facebook/musicgen-small
- **演示**: https://huggingface.co/spaces/facebook/MusicGen
