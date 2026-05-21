---
title: "Clip — OpenAI 连接视觉与语言的模型"
sidebar_label: "Clip"
description: "OpenAI 连接视觉与语言的模型"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="clip"></a>
# Clip

OpenAI 连接视觉与语言的模型。支持零样本图像分类、图像-文本匹配以及跨模态检索。基于 4 亿对图像-文本对训练而成。可用于图像搜索、内容审核或视觉-语言任务，无需微调。最适合通用图像理解。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/clip` 安装 |
| 路径 | `optional-skills/mlops/clip` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖 | `transformers`, `torch`, `pillow` |
| 平台 | linux, macos, windows |
| 标签 | `Multimodal`, `CLIP`, `Vision-Language`, `Zero-Shot`, `Image Classification`, `OpenAI`, `Image Search`, `Cross-Modal Retrieval`, `Content Moderation` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="clip-contrastive-language-image-pre-training"></a>
# CLIP - 对比语言-图像预训练

OpenAI 的模型，能够通过自然语言理解图像。

<a id="when-to-use-clip"></a>
## 何时使用 CLIP

**适用场景：**
- 零样本图像分类（无需训练数据）
- 图像-文本相似度/匹配
- 语义图像搜索
- 内容审核（检测 NSFW、暴力内容）
- 视觉问答
- 跨模态检索（图像→文本，文本→图像）

**指标**：
- **25,300+ GitHub 星标**
- 基于 4 亿对图像-文本对训练
- 在 ImageNet 上零样本达到 ResNet-50 水平
- MIT 许可证

**替代方案**：
- **BLIP-2**：更好的图像描述生成
- **LLaVA**：视觉-语言对话
- **Segment Anything**：图像分割

<a id="quick-start"></a>
## 快速开始

<a id="installation"></a>
### 安装

```bash
pip install git+https://github.com/openai/CLIP.git
pip install torch torchvision ftfy regex tqdm
```

<a id="zero-shot-classification"></a>
### 零样本分类

```python
import torch
import clip
from PIL import Image

# 加载模型
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# 加载图像
image = preprocess(Image.open("photo.jpg")).unsqueeze(0).to(device)

# 定义可能的标签
text = clip.tokenize(["a dog", "a cat", "a bird", "a car"]).to(device)

# 计算相似度
with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)

    # 余弦相似度
    logits_per_image, logits_per_text = model(image, text)
    probs = logits_per_image.softmax(dim=-1).cpu().numpy()

# 打印结果
labels = ["a dog", "a cat", "a bird", "a car"]
for label, prob in zip(labels, probs[0]):
    print(f"{label}: {prob:.2%}")
```

<a id="available-models"></a>
## 可用模型

```python
# 模型（按大小排序）
models = [
    "RN50",           # ResNet-50
    "RN101",          # ResNet-101
    "ViT-B/32",       # Vision Transformer（推荐）
    "ViT-B/16",       # 质量更好，速度更慢
    "ViT-L/14",       # 质量最好，速度最慢
]

model, preprocess = clip.load("ViT-B/32")
```
| 模型 | 参数量 | 速度 | 质量 |
|-------|------------|-------|---------|
| RN50 | 102M | 快 | 好 |
| ViT-B/32 | 151M | 中等 | 更好 |
| ViT-L/14 | 428M | 慢 | 最佳 |

<a id="image-text-similarity"></a>
## 图像-文本相似度

```python
# 计算嵌入向量
image_features = model.encode_image(image)
text_features = model.encode_text(text)

# 归一化
image_features /= image_features.norm(dim=-1, keepdim=True)
text_features /= text_features.norm(dim=-1, keepdim=True)

# 余弦相似度
similarity = (image_features @ text_features.T).item()
print(f"相似度: {similarity:.4f}")
```

<a id="semantic-image-search"></a>
## 语义图像搜索

```python
# 索引图像
image_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
image_embeddings = []

for img_path in image_paths:
    image = preprocess(Image.open(img_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image)
        embedding /= embedding.norm(dim=-1, keepdim=True)
    image_embeddings.append(embedding)

image_embeddings = torch.cat(image_embeddings)

# 使用文本查询进行搜索
query = "海上的日落"
text_input = clip.tokenize([query]).to(device)
with torch.no_grad():
    text_embedding = model.encode_text(text_input)
    text_embedding /= text_embedding.norm(dim=-1, keepdim=True)

# 找到最相似的图像
similarities = (text_embedding @ image_embeddings.T).squeeze(0)
top_k = similarities.topk(3)

for idx, score in zip(top_k.indices, top_k.values):
    print(f"{image_paths[idx]}: {score:.3f}")
```

<a id="content-moderation"></a>
## 内容审核

```python
# 定义类别
categories = [
    "适合工作场合",
    "不适合工作场合",
    "暴力内容",
    "露骨内容"
]

text = clip.tokenize(categories).to(device)

# 检查图像
with torch.no_grad():
    logits_per_image, _ = model(image, text)
    probs = logits_per_image.softmax(dim=-1)

# 获取分类结果
max_idx = probs.argmax().item()
max_prob = probs[0, max_idx].item()

print(f"类别: {categories[max_idx]} ({max_prob:.2%})")
```

<a id="batch-processing"></a>
## 批量处理

```python
# 处理多张图像
images = [preprocess(Image.open(f"img{i}.jpg")) for i in range(10)]
images = torch.stack(images).to(device)

with torch.no_grad():
    image_features = model.encode_image(images)
    image_features /= image_features.norm(dim=-1, keepdim=True)

# 批量文本
texts = ["一只狗", "一只猫", "一只鸟"]
text_tokens = clip.tokenize(texts).to(device)

with torch.no_grad():
    text_features = model.encode_text(text_tokens)
    text_features /= text_features.norm(dim=-1, keepdim=True)

# 相似度矩阵（10张图像 × 3段文本）
similarities = image_features @ text_features.T
print(similarities.shape)  # (10, 3)
```

<a id="integration-with-vector-databases"></a>
## 与向量数据库集成

```python
# 将 CLIP 嵌入向量存储到 Chroma/FAISS
import chromadb

client = chromadb.Client()
collection = client.create_collection("image_embeddings")

# 添加图像嵌入向量
for img_path, embedding in zip(image_paths, image_embeddings):
    collection.add(
        embeddings=[embedding.cpu().numpy().tolist()],
        metadatas=[{"path": img_path}],
        ids=[img_path]
    )

# 使用文本进行查询
query = "日落"
text_embedding = model.encode_text(clip.tokenize([query]))
results = collection.query(
    query_embeddings=[text_embedding.cpu().numpy().tolist()],
    n_results=5
)
```
<a id="best-practices"></a>
## Best practices

1. **大多数情况使用 ViT-B/32** - 平衡性好
2. **归一化嵌入** - 余弦相似度必需
3. **批处理** - 效率更高
4. **缓存嵌入** - 重新计算代价高
5. **使用描述性标签** - 零样本性能更佳
6. **建议使用 GPU** - 快10-50倍
7. **预处理图像** - 使用提供的预处理函数

<a id="performance"></a>
## 性能

| 操作 | CPU | GPU (V100) |
|-----------|-----|------------|
| 图像编码 | ~200ms | ~20ms |
| 文本编码 | ~50ms | ~5ms |
| 相似度计算 | &lt;1ms | &lt;1ms |

<a id="limitations"></a>
## 限制

1. **不适用于细粒度任务** - 最适合广泛类别
2. **需要描述性文本** - 模糊标签效果差
3. **基于网络数据有偏差** - 可能存在数据集偏差
4. **无边界框** - 仅适用于整张图像
5. **空间理解有限** - 位置/计数能力弱

<a id="resources"></a>
## 资源

- **GitHub**: https://github.com/openai/CLIP ⭐ 25,300+
- **论文**: https://arxiv.org/abs/2103.00020
- **Colab**: https://colab.research.google.com/github/openai/clip/
- **许可证**: MIT
