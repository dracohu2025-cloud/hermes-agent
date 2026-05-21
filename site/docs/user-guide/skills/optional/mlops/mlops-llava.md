---
title: "Llava — 大型语言与视觉助手"
sidebar_label: "Llava"
description: "大型语言与视觉助手"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="llava"></a>
# Llava

大型语言与视觉助手。支持视觉指令微调和基于图像的对话。将 CLIP 视觉编码器与 Vicuna/LLaMA 语言模型结合。支持多轮图像聊天、视觉问答和指令跟随。适用于视觉-语言聊天机器人或图像理解任务。最适合对话式图像分析。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/llava` 安装 |
| 路径 | `optional-skills/mlops/llava` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖 | `transformers`、`torch`、`pillow` |
| 平台 | linux、macos、windows |
| 标签 | `LLaVA`、`Vision-Language`、`Multimodal`、`Visual Question Answering`、`Image Chat`、`CLIP`、`Vicuna`、`Conversational AI`、`Instruction Tuning`、`VQA` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。技能激活时，Agent 会将其作为指令。
:::

<a id="llava-large-language-and-vision-assistant"></a>
# LLaVA - 大型语言与视觉助手

用于对话式图像理解的开源视觉-语言模型。

<a id="when-to-use-llava"></a>
## 何时使用 LLaVA

**使用场景：**
- 构建视觉-语言聊天机器人
- 视觉问答（VQA）
- 图像描述与字幕生成
- 多轮图像对话
- 视觉指令跟随
- 文档理解（含图像）

**指标**：
- **GitHub 星标 23,000+**
- 具备 GPT-4V 级别能力（目标）
- Apache 2.0 许可证
- 多种模型规模（7B-34B 参数）

**替代方案**：
- **GPT-4V**：质量最高，基于 API
- **CLIP**：简单的零样本分类
- **BLIP-2**：仅适用于字幕生成
- **Flamingo**：研究用途，非开源

<a id="quick-start"></a>
## 快速开始

<a id="installation"></a>
### 安装

```bash
# Clone repository
git clone https://github.com/haotian-liu/LLaVA
cd LLaVA

# Install
pip install -e .
```

<a id="basic-usage"></a>
### 基本用法

```python
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path, process_images, tokenizer_image_token
from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
from llava.conversation import conv_templates
from PIL import Image
import torch

# Load model
model_path = "liuhaotian/llava-v1.5-7b"
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path=model_path,
    model_base=None,
    model_name=get_model_name_from_path(model_path)
)

# Load image
image = Image.open("image.jpg")
image_tensor = process_images([image], image_processor, model.config)
image_tensor = image_tensor.to(model.device, dtype=torch.float16)

# Create conversation
conv = conv_templates["llava_v1"].copy()
conv.append_message(conv.roles[0], DEFAULT_IMAGE_TOKEN + "\nWhat is in this image?")
conv.append_message(conv.roles[1], None)
prompt = conv.get_prompt()

# Generate response
input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).to(model.device)

with torch.inference_mode():
    output_ids = model.generate(
        input_ids,
        images=image_tensor,
        do_sample=True,
        temperature=0.2,
        max_new_tokens=512
    )

response = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
print(response)
```
<a id="available-models"></a>
## 可用模型

| 模型 | 参数量 | 显存 | 质量 |
|-------|------------|------|---------|
| LLaVA-v1.5-7B | 7B | ~14 GB | 良好 |
| LLaVA-v1.5-13B | 13B | ~28 GB | 更好 |
| LLaVA-v1.6-34B | 34B | ~70 GB | 最佳 |

```python
# 加载不同模型
model_7b = "liuhaotian/llava-v1.5-7b"
model_13b = "liuhaotian/llava-v1.5-13b"
model_34b = "liuhaotian/llava-v1.6-34b"

# 4-bit 量化以减少显存占用
load_4bit = True  # 显存降低约 4 倍
```

<a id="cli-usage"></a>
## CLI 用法

```bash
# 单张图片查询
python -m llava.serve.cli \
    --model-path liuhaotian/llava-v1.5-7b \
    --image-file image.jpg \
    --query "这张图片里有什么？"

# 多轮对话
python -m llava.serve.cli \
    --model-path liuhaotian/llava-v1.5-7b \
    --image-file image.jpg
# 然后交互式输入问题
```

<a id="web-ui-gradio"></a>
## Web UI（Gradio）

```bash
# 启动 Gradio 界面
python -m llava.serve.gradio_web_server \
    --model-path liuhaotian/llava-v1.5-7b \
    --load-4bit  # 可选：降低显存占用

# 访问地址 http://localhost:7860
```

<a id="multi-turn-conversations"></a>
## 多轮对话

```python
# 初始化对话
conv = conv_templates["llava_v1"].copy()

# 第一轮
conv.append_message(conv.roles[0], DEFAULT_IMAGE_TOKEN + "\n这张图片里有什么？")
conv.append_message(conv.roles[1], None)
response1 = generate(conv, model, image)  # "一只狗在公园里玩耍"

# 第二轮
conv.messages[-1][1] = response1  # 添加上一轮的回答
conv.append_message(conv.roles[0], "这只狗是什么品种？")
conv.append_message(conv.roles[1], None)
response2 = generate(conv, model, image)  # "金毛寻回犬"

# 第三轮
conv.messages[-1][1] = response2
conv.append_message(conv.roles[0], "现在是一天中的什么时间？")
conv.append_message(conv.roles[1], None)
response3 = generate(conv, model, image)
```

<a id="common-tasks"></a>
## 常见任务

<a id="image-captioning"></a>
### 图像描述

```python
question = "请详细描述这张图片。"
response = ask(model, image, question)
```

<a id="visual-question-answering"></a>
### 视觉问答

```python
question = "图片中有多少人？"
response = ask(model, image, question)
```

<a id="object-detection-textual"></a>
### 物体检测（文字形式）

```python
question = "列出你能在这张图片中看到的所有物体。"
response = ask(model, image, question)
```

<a id="scene-understanding"></a>
### 场景理解

```python
question = "这个场景在发生什么？"
response = ask(model, image, question)
```

<a id="document-understanding"></a>
### 文档理解

```python
question = "这份文档的主要主题是什么？"
response = ask(model, document_image, question)
```

<a id="training-custom-model"></a>
## 训练自定义模型

```bash
# 阶段 1：特征对齐（558K 图像-文本对）
bash scripts/v1_5/pretrain.sh

# 阶段 2：视觉指令微调（150K 指令数据）
bash scripts/v1_5/finetune.sh
```

<a id="quantization-reduce-vram"></a>
## 量化（降低显存占用）

```python
# 4-bit 量化
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path="liuhaotian/llava-v1.5-13b",
    model_base=None,
    model_name=get_model_name_from_path("liuhaotian/llava-v1.5-13b"),
    load_4bit=True  # 显存降低约 4 倍
)

# 8-bit 量化
load_8bit=True  # 显存降低约 2 倍
```
<a id="best-practices"></a>
## 最佳实践

1. **从 7B 模型开始** – 质量好，显存可控
2. **使用 4-bit 量化** – 大幅降低显存占用
3. **需要 GPU** – CPU 推理极慢
4. **清晰的提示** – 具体问题能得到更好的答案
5. **多轮对话** – 保持对话上下文
6. **Temperature 0.2–0.7** – 平衡创造性与一致性
7. **max_new_tokens 512–1024** – 用于生成详细回复
8. **批量处理** – 依次处理多张图片

<a id="performance"></a>
## 性能

| 模型 | 显存（FP16） | 显存（4-bit） | 速度（tokens/s） |
|------|-------------|--------------|------------------|
| 7B   | ~14 GB      | ~4 GB        | ~20              |
| 13B  | ~28 GB      | ~8 GB        | ~12              |
| 34B  | ~70 GB      | ~18 GB       | ~5               |

*在 A100 GPU 上*

<a id="benchmarks"></a>
## 基准测试

LLaVA 在以下评估中取得了有竞争力的分数：
- **VQAv2**：78.5%
- **GQA**：62.0%
- **MM-Vet**：35.4%
- **MMBench**：64.3%

<a id="limitations"></a>
## 局限性

1. **幻觉** – 可能会描述图片中不存在的内容
2. **空间推理** – 难以处理精确位置
3. **小文字** – 难以阅读细小字体
4. **物体计数** – 对多个物体的统计不精确
5. **显存需求** – 需要强大的 GPU
6. **推理速度** – 比 CLIP 慢

<a id="integration-with-frameworks"></a>
## 与框架集成

<a id="langchain"></a>
### LangChain

```python
from langchain.llms.base import LLM

class LLaVALLM(LLM):
    def _call(self, prompt, stop=None):
        # 自定义 LLaVA 推理
        return response

llm = LLaVALLM()
```

<a id="gradio-app"></a>
### Gradio 应用

```python
import gradio as gr

def chat(image, text, history):
    response = ask_llava(model, image, text)
    return response

demo = gr.ChatInterface(
    chat,
    additional_inputs=[gr.Image(type="pil")],
    title="LLaVA Chat"
)
demo.launch()
```

<a id="resources"></a>
## 资源

- **GitHub**：https://github.com/haotian-liu/LLaVA ⭐ 23,000+
- **论文**：https://arxiv.org/abs/2304.08485
- **演示**：https://llava.hliu.cc
- **模型**：https://huggingface.co/liuhaotian
- **许可证**：Apache 2.0
