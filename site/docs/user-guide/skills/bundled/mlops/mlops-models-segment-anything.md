---
title: "Segment Anything Model — SAM：通过点、框、掩码进行零样本图像分割"
sidebar_label: "Segment Anything Model"
description: "SAM：通过点、框、掩码进行零样本图像分割"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是本页面。 */}

<a id="segment-anything-model"></a>
# Segment Anything Model

SAM：通过点、框、掩码进行零样本图像分割。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/models/segment-anything` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `segment-anything`、`transformers>=4.30.0`、`torch>=1.7.0` |
| 平台 | linux、macos、windows |
| 标签 | `Multimodal`、`Image Segmentation`、`Computer Vision`、`SAM`、`Zero-Shot` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。Agent 在技能处于活动状态时看到的指令就是这些内容。
:::

<a id="segment-anything-model-sam"></a>
# Segment Anything Model (SAM)

详细指南：使用 Meta AI 的 Segment Anything Model 进行零样本图像分割。

<a id="when-to-use-sam"></a>
## 何时使用 SAM

**适合使用 SAM 的场景：**
- 需要对图像中的任意对象进行分割，且无需针对特定任务训练
- 构建带有点/框提示的交互式标注工具
- 为其他视觉模型生成训练数据
- 需要零样本迁移到新的图像领域
- 构建目标检测/分割流水线
- 处理医学、卫星或特定领域的图像

**主要特性：**
- **零样本分割**：无需微调即可处理任何图像领域
- **灵活的提示**：可提供点、边界框或前一次生成的掩码
- **自动分割**：自动生成所有对象掩码
- **高质量**：基于 1100 万张图像、11 亿个掩码训练而成
- **多种模型尺寸**：ViT-B（最快）、ViT-L、ViT-H（最准确）
- **ONNX 导出**：可部署到浏览器和边缘设备

**替代方案（应优先考虑的情况）：**
- **YOLO / Detectron2**：需要分类的实时目标检测
- **Mask2Former**：需要分类的语义/全景分割
- **GroundingDINO + SAM**：基于文本提示的分割
- **SAM 2**：视频分割任务

<a id="quick-start"></a>
## 快速入门

<a id="installation"></a>
### 安装

```bash
# 从 GitHub 安装
pip install git+https://github.com/facebookresearch/segment-anything.git

# 可选依赖
pip install opencv-python pycocotools matplotlib

# 或者使用 HuggingFace transformers
pip install transformers
```

<a id="download-checkpoints"></a>
### 下载检查点

```bash
# ViT-H（最大、最准确）— 2.4GB
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

# ViT-L（中等）— 1.2GB
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth

# ViT-B（最小、最快）— 375MB
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
```

<a id="basic-usage-with-sampredictor"></a>
### SamPredictor 的基本用法

```python
import numpy as np
from segment_anything import sam_model_registry, SamPredictor

# 加载模型
sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
sam.to(device="cuda")

# 创建预测器
predictor = SamPredictor(sam)

# 设置图像（一次性计算嵌入）
image = cv2.imread("image.jpg")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
predictor.set_image(image)

# 使用点提示进行预测
input_point = np.array([[500, 375]])  # (x, y) 坐标
input_label = np.array([1])  # 1 = 前景，0 = 背景

masks, scores, logits = predictor.predict(
    point_coords=input_point,
    point_labels=input_label,
    multimask_output=True  # 返回 3 个掩码选项
)

# 选择最优掩码
best_mask = masks[np.argmax(scores)]
```
<a id="huggingface-transformers"></a>
### HuggingFace Transformers

```python
import torch
from PIL import Image
from transformers import SamModel, SamProcessor

# Load model and processor
model = SamModel.from_pretrained("facebook/sam-vit-huge")
processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")
model.to("cuda")

# Process image with point prompt
image = Image.open("image.jpg")
input_points = [[[450, 600]]]  # Batch of points

inputs = processor(image, input_points=input_points, return_tensors="pt")
inputs = {k: v.to("cuda") for k, v in inputs.items()}

# Generate masks
with torch.no_grad():
    outputs = model(**inputs)

# Post-process masks to original size
masks = processor.image_processor.post_process_masks(
    outputs.pred_masks.cpu(),
    inputs["original_sizes"].cpu(),
    inputs["reshaped_input_sizes"].cpu()
)
```

<a id="core-concepts"></a>
## 核心概念

<a id="model-architecture"></a>
### 模型架构

<!-- ascii-guard-ignore -->
<!-- ascii-guard-ignore -->
```
SAM Architecture:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Image Encoder  │────▶│ Prompt Encoder  │────▶│  Mask Decoder   │
│     (ViT)       │     │ (Points/Boxes)  │     │ (Transformer)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
   Image Embeddings      Prompt Embeddings         Masks + IoU
   (computed once)       (per prompt)             predictions
```
<!-- ascii-guard-ignore-end -->
<!-- ascii-guard-ignore-end -->

<a id="model-variants"></a>
### 模型变体

| 模型 | 检查点 | 大小 | 速度 | 准确率 |
|-------|------------|------|-------|----------|
| ViT-H | `vit_h` | 2.4 GB | 最慢 | 最佳 |
| ViT-L | `vit_l` | 1.2 GB | 中等 | 良好 |
| ViT-B | `vit_b` | 375 MB | 最快 | 良好 |

<a id="prompt-types"></a>
### 提示类型

| 提示类型 | 描述 | 使用场景 |
|--------|-------------|----------|
| 点（前景） | 点击物体 | 选择单个物体 |
| 点（背景） | 点击物体外部 | 排除区域 |
| 边界框 | 物体周围的矩形 | 较大物体 |
| 之前的掩码 | 低分辨率掩码输入 | 迭代优化 |

<a id="interactive-segmentation"></a>
## 交互式分割

<a id="point-prompts"></a>
### 点提示

```python
# Single foreground point
input_point = np.array([[500, 375]])
input_label = np.array([1])

masks, scores, logits = predictor.predict(
    point_coords=input_point,
    point_labels=input_label,
    multimask_output=True
)

# Multiple points (foreground + background)
input_points = np.array([[500, 375], [600, 400], [450, 300]])
input_labels = np.array([1, 1, 0])  # 2 foreground, 1 background

masks, scores, logits = predictor.predict(
    point_coords=input_points,
    point_labels=input_labels,
    multimask_output=False  # Single mask when prompts are clear
)
```

<a id="box-prompts"></a>
### 框提示

```python
# Bounding box [x1, y1, x2, y2]
input_box = np.array([425, 600, 700, 875])

masks, scores, logits = predictor.predict(
    box=input_box,
    multimask_output=False
)
```

<a id="combined-prompts"></a>
### 组合提示

```python
# Box + points for precise control
masks, scores, logits = predictor.predict(
    point_coords=np.array([[500, 375]]),
    point_labels=np.array([1]),
    box=np.array([400, 300, 700, 600]),
    multimask_output=False
)
```
<a id="iterative-refinement"></a>
### 迭代细化

```python
# 初始预测
masks, scores, logits = predictor.predict(
    point_coords=np.array([[500, 375]]),
    point_labels=np.array([1]),
    multimask_output=True
)

# 使用额外点与上一轮掩码进行细化
masks, scores, logits = predictor.predict(
    point_coords=np.array([[500, 375], [550, 400]]),
    point_labels=np.array([1, 0]),  # 添加背景点
    mask_input=logits[np.argmax(scores)][None, :, :],  # 使用最佳掩码
    multimask_output=False
)
```

<a id="automatic-mask-generation"></a>
## 自动掩码生成

<a id="basic-automatic-segmentation"></a>
### 基础自动分割

```python
from segment_anything import SamAutomaticMaskGenerator

# 创建生成器
mask_generator = SamAutomaticMaskGenerator(sam)

# 生成所有掩码
masks = mask_generator.generate(image)

# 每个掩码包含：
# - segmentation: 二值掩码
# - bbox: [x, y, w, h]
# - area: 像素数量
# - predicted_iou: 质量评分
# - stability_score: 稳定性评分
# - point_coords: 生成点
```

<a id="customized-generation"></a>
### 自定义生成

```python
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=32,          # 网格密度（越大，掩码越多）
    pred_iou_thresh=0.88,        # 质量阈值
    stability_score_thresh=0.95,  # 稳定性阈值
    crop_n_layers=1,             # 多尺度裁剪
    crop_n_points_downscale_factor=2,
    min_mask_region_area=100,    # 移除微小掩码
)

masks = mask_generator.generate(image)
```

<a id="filtering-masks"></a>
### 过滤掩码

```python
# 按面积排序（从大到小）
masks = sorted(masks, key=lambda x: x['area'], reverse=True)

# 按预测 IoU 过滤
high_quality = [m for m in masks if m['predicted_iou'] > 0.9]

# 按稳定性评分过滤
stable_masks = [m for m in masks if m['stability_score'] > 0.95]
```

<a id="batched-inference"></a>
## 批量推理

<a id="multiple-images"></a>
### 多张图片

```python
# 高效处理多张图片
images = [cv2.imread(f"image_{i}.jpg") for i in range(10)]

all_masks = []
for image in images:
    predictor.set_image(image)
    masks, _, _ = predictor.predict(
        point_coords=np.array([[500, 375]]),
        point_labels=np.array([1]),
        multimask_output=True
    )
    all_masks.append(masks)
```

<a id="multiple-prompts-per-image"></a>
### 单张图片多个提示

```python
# 高效处理多个提示（只编码一次图片）
predictor.set_image(image)

# 批量点提示
points = [
    np.array([[100, 100]]),
    np.array([[200, 200]]),
    np.array([[300, 300]])
]

all_masks = []
for point in points:
    masks, scores, _ = predictor.predict(
        point_coords=point,
        point_labels=np.array([1]),
        multimask_output=True
    )
    all_masks.append(masks[np.argmax(scores)])
```

<a id="onnx-deployment"></a>
## ONNX 部署

<a id="export-model"></a>
### 导出模型

```bash
python scripts/export_onnx_model.py \
    --checkpoint sam_vit_h_4b8939.pth \
    --model-type vit_h \
    --output sam_onnx.onnx \
    --return-single-mask
```

<a id="use-onnx-model"></a>
### 使用 ONNX 模型

```python
import onnxruntime

# 加载 ONNX 模型
ort_session = onnxruntime.InferenceSession("sam_onnx.onnx")

# 运行推理（图片嵌入已单独计算）
masks = ort_session.run(
    None,
    {
        "image_embeddings": image_embeddings,
        "point_coords": point_coords,
        "point_labels": point_labels,
        "mask_input": np.zeros((1, 1, 256, 256), dtype=np.float32),
        "has_mask_input": np.array([0], dtype=np.float32),
        "orig_im_size": np.array([h, w], dtype=np.float32)
    }
)
```
<a id="common-workflows"></a>
## 常见工作流

<a id="workflow-1-annotation-tool"></a>
### 工作流 1：标注工具

```python
import cv2

# Load model
predictor = SamPredictor(sam)
predictor.set_image(image)

def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Foreground point
        masks, scores, _ = predictor.predict(
            point_coords=np.array([[x, y]]),
            point_labels=np.array([1]),
            multimask_output=True
        )
        # Display best mask
        display_mask(masks[np.argmax(scores)])
```

<a id="workflow-2-object-extraction"></a>
### 工作流 2：对象提取

```python
def extract_object(image, point):
    """Extract object at point with transparent background."""
    predictor.set_image(image)

    masks, scores, _ = predictor.predict(
        point_coords=np.array([point]),
        point_labels=np.array([1]),
        multimask_output=True
    )

    best_mask = masks[np.argmax(scores)]

    # Create RGBA output
    rgba = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
    rgba[:, :, :3] = image
    rgba[:, :, 3] = best_mask * 255

    return rgba
```

<a id="workflow-3-medical-image-segmentation"></a>
### 工作流 3：医学图像分割

```python
# Process medical images (grayscale to RGB)
medical_image = cv2.imread("scan.png", cv2.IMREAD_GRAYSCALE)
rgb_image = cv2.cvtColor(medical_image, cv2.COLOR_GRAY2RGB)

predictor.set_image(rgb_image)

# Segment region of interest
masks, scores, _ = predictor.predict(
    box=np.array([x1, y1, x2, y2]),  # ROI bounding box
    multimask_output=True
)
```

<a id="output-format"></a>
## 输出格式

<a id="mask-data-structure"></a>
### 掩码数据结构

```python
# SamAutomaticMaskGenerator output
{
    "segmentation": np.ndarray,  # H×W binary mask
    "bbox": [x, y, w, h],        # Bounding box
    "area": int,                 # Pixel count
    "predicted_iou": float,      # 0-1 quality score
    "stability_score": float,    # 0-1 robustness score
    "crop_box": [x, y, w, h],    # Generation crop region
    "point_coords": [[x, y]],    # Input point
}
```

<a id="coco-rle-format"></a>
### COCO RLE 格式

```python
from pycocotools import mask as mask_utils

# Encode mask to RLE
rle = mask_utils.encode(np.asfortranarray(mask.astype(np.uint8)))
rle["counts"] = rle["counts"].decode("utf-8")

# Decode RLE to mask
decoded_mask = mask_utils.decode(rle)
```

<a id="performance-optimization"></a>
## 性能优化

<a id="gpu-memory"></a>
### GPU 内存

```python
# Use smaller model for limited VRAM
sam = sam_model_registry["vit_b"](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/models/segment-anything/checkpoint="sam_vit_b_01ec64.pth")

# Process images in batches
# Clear CUDA cache between large batches
torch.cuda.empty_cache()
```

<a id="speed-optimization"></a>
### 速度优化

```python
# Use half precision
sam = sam.half()

# Reduce points for automatic generation
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=16,  # Default is 32
)

# Use ONNX for deployment
# Export with --return-single-mask for faster inference
```

<a id="common-issues"></a>
## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 内存不足 | 使用 ViT-B 模型，缩小图像尺寸 |
| 推理速度慢 | 使用 ViT-B，减少 points_per_side |
| 掩码质量差 | 尝试不同的提示词，结合使用框和点 |
| 边缘伪影 | 使用 stability_score 过滤 |
| 小物体漏检 | 增加 points_per_side |
<a id="references"></a>
## 参考文献

- **[高级用法](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/models/segment-anything/references/advanced-usage.md)** — 批处理、微调、集成
- **[故障排查](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/models/segment-anything/references/troubleshooting.md)** — 常见问题及解决方案

<a id="resources"></a>
## 资源

- **GitHub**：https://github.com/facebookresearch/segment-anything
- **论文**：https://arxiv.org/abs/2304.02643
- **演示**：https://segment-anything.com
- **SAM 2（视频）**：https://github.com/facebookresearch/segment-anything-2
- **HuggingFace**：https://huggingface.co/facebook/sam-vit-huge
