---
title: "Llava — 大型语言与视觉助手"
sidebar_label: "Llava"
description: "大型语言与视觉助手"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Llava {#llava}

大型语言与视觉助手。支持视觉指令微调和基于图像的对话。将 CLIP 视觉编码器与 Vicuna/LLaMA 语言模型相结合。支持多轮图像聊天、视觉问答和指令遵循。适用于视觉语言聊天机器人或图像理解任务。最适合对话式图像分析。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/llava` 安装 |
| 路径 | `optional-skills/mlops/llava` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `transformers`, `torch`, `pillow` |
| 标签 | `LLaVA`, `Vision-Language`, `Multimodal`, `Visual Question Answering`, `Image Chat`, `CLIP`, `Vicuna`, `Conversational AI`, `Instruction Tuning`, `VQA` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# LLaVA - 大型语言与视觉助手 {#llava-large-language-and-vision-assistant}

用于对话式图像理解的开源视觉语言模型。

## 何时使用 LLaVA {#when-to-use-llava}

**适用场景：**
- 构建视觉语言聊天机器人
- 视觉问答（VQA）
- 图像描述和字幕生成
- 多轮图像对话
- 视觉指令遵循
- 带图像的文档理解

**指标**：
- **23,000+ GitHub 星标**
- GPT-4V 级别能力（目标）
- Apache 2.0 许可证
- 多种模型规模（7B-34B 参数）

**替代方案**：
- **GPT-4V**：最高质量，基于 API
- **CLIP**：简单的零样本分类
- **BLIP-2**：仅适用于字幕生成
- **Flamingo**：研究用途，非开源

## 快速开始 {#quick-start}

### 安装 {#installation}

```bash
# 克隆仓库
git clone https://github.com/haotian-liu/LLaVA
cd LLaVA

# 安装
pip install -e .
```

### 基本用法 {#basic-usage}

```python
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path, process_images, tokenizer_image_token
from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
from llava.conversation import conv_templates
from PIL import Image
import torch

# 加载模型
model_path = "liuhaotian/llava-v1.5-7b"
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path=model_path,
    model_base=None,
    model_name=get_model_name_from_path(model_path)
)

# 加载图像
image = Image.open("image.jpg")
image_tensor = process_images([image], image_processor, model.config)
image_tensor = image_tensor.to(model.device, dtype=torch.float16)

# 创建对话
conv = conv_templates["llava_v1"].copy()
conv.append_message(conv.roles[0], DEFAULT_IMAGE_TOKEN + "\n这张图片里有什么？")
conv.append_message(conv.roles[1], None)
prompt = conv.get_prompt()

# 生成回复
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
## 可用模型 {#available-models}

| 模型 | 参数量 | 显存占用 | 质量 |
|-------|------------|------|---------|
| LLaVA-v1.5-7B | 7B | ~14 GB | 良好 |
| LLaVA-v1.5-13B | 13B | ~28 GB | 较好 |
| LLaVA-v1.6-34B | 34B | ~70 GB | 最佳 |

```python
# 加载不同模型
model_7b = "liuhaotian/llava-v1.5-7b"
model_13b = "liuhaotian/llava-v1.5-13b"
model_34b = "liuhaotian/llava-v1.6-34b"

# 4-bit 量化以降低显存占用
load_4bit = True  # 显存占用减少约 4 倍
```

## CLI 用法 {#cli-usage}

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

## Web UI（Gradio） {#web-ui-gradio}

```bash
# 启动 Gradio 界面
python -m llava.serve.gradio_web_server \
    --model-path liuhaotian/llava-v1.5-7b \
    --load-4bit  # 可选：降低显存占用

# 访问地址：http://localhost:7860
```

## 多轮对话 {#multi-turn-conversations}

```python
# 初始化对话
conv = conv_templates["llava_v1"].copy()

# 第1轮
conv.append_message(conv.roles[0], DEFAULT_IMAGE_TOKEN + "\n这张图片里有什么？")
conv.append_message(conv.roles[1], None)
response1 = generate(conv, model, image)  # "一只狗在公园里玩耍"

# 第2轮
conv.messages[-1][1] = response1  # 添加上一轮的回答
conv.append_message(conv.roles[0], "这只狗是什么品种？")
conv.append_message(conv.roles[1], None)
response2 = generate(conv, model, image)  # "金毛寻回犬"

# 第3轮
conv.messages[-1][1] = response2
conv.append_message(conv.roles[0], "现在是白天还是晚上？")
conv.append_message(conv.roles[1], None)
response3 = generate(conv, model, image)
```

## 常见任务 {#common-tasks}

### 图像描述 {#image-captioning}

```python
question = "请详细描述这张图片。"
response = ask(model, image, question)
```

### 视觉问答 {#visual-question-answering}

```python
question = "图片中有几个人？"
response = ask(model, image, question)
```

### 目标检测（文本形式） {#object-detection-textual}

```python
question = "列出你在图片中看到的所有物体。"
response = ask(model, image, question)
```

### 场景理解 {#scene-understanding}

```python
question = "这个场景中正在发生什么？"
response = ask(model, image, question)
```

### 文档理解 {#document-understanding}

```python
question = "这份文档的主要内容是什么？"
response = ask(model, document_image, question)
```

## 训练自定义模型 {#training-custom-model}

```bash
# 阶段 1：特征对齐（558K 图像-文本对）
bash scripts/v1_5/pretrain.sh

# 阶段 2：视觉指令微调（150K 指令数据）
bash scripts/v1_5/finetune.sh
```

## 量化（降低显存占用） {#quantization-reduce-vram}

```python
# 4-bit 量化
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path="liuhaotian/llava-v1.5-13b",
    model_base=None,
    model_name=get_model_name_from_path("liuhaotian/llava-v1.5-13b"),
    load_4bit=True  # 显存占用减少约 4 倍
)

# 8-bit 量化
load_8bit=True  # 显存占用减少约 2 倍
```
## 最佳实践 {#best-practices}

1. **从 7B 模型开始** - 质量不错，显存可控
2. **使用 4-bit 量化** - 大幅降低显存占用
3. **需要 GPU** - CPU 推理极慢
4. **提示词要清晰** - 具体的问题能得到更好的回答
5. **多轮对话** - 保持对话上下文
6. **温度设为 0.2-0.7** - 在创造性与一致性之间取得平衡
7. **max_new_tokens 设为 512-1024** - 用于生成详细回答
8. **批量处理** - 顺序处理多张图片

## 性能 {#performance}

| 模型 | 显存 (FP16) | 显存 (4-bit) | 速度 (tokens/s) |
|-------|-------------|--------------|------------------|
| 7B | ~14 GB | ~4 GB | ~20 |
| 13B | ~28 GB | ~8 GB | ~12 |
| 34B | ~70 GB | ~18 GB | ~5 |

*基于 A100 GPU*

## 基准测试 {#benchmarks}

LLaVA 在以下测试中取得了有竞争力的分数：
- **VQAv2**: 78.5%
- **GQA**: 62.0%
- **MM-Vet**: 35.4%
- **MMBench**: 64.3%

## 局限性 {#limitations}

1. **幻觉** - 可能会描述图片中不存在的内容
2. **空间推理** - 难以精确定位
3. **小文字** - 难以阅读细小文字
4. **物体计数** - 对多个物体的计数不精确
5. **显存需求** - 需要强大的 GPU
6. **推理速度** - 比 CLIP 慢

## 与框架集成 {#integration-with-frameworks}

### LangChain {#langchain}

```python
from langchain.llms.base import LLM

class LLaVALLM(LLM):
    def _call(self, prompt, stop=None):
        # 自定义 LLaVA 推理
        return response

llm = LLaVALLM()
```

### Gradio 应用 {#gradio-app}

```python
import gradio as gr

def chat(image, text, history):
    response = ask_llava(model, image, text)
    return response

demo = gr.ChatInterface(
    chat,
    additional_inputs=[gr.Image(type="pil")],
    title="LLaVA 聊天"
)
demo.launch()
```

## 资源 {#resources}

- **GitHub**: https://github.com/haotian-liu/LLaVA ⭐ 23,000+
- **论文**: https://arxiv.org/abs/2304.08485
- **演示**: https://llava.hliu.cc
- **模型**: https://huggingface.co/liuhaotian
- **许可证**: Apache 2.0
