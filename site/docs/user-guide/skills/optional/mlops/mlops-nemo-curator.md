---
title: "Nemo Curator — 面向 LLM 训练的 GPU 加速数据整理"
sidebar_label: "Nemo Curator"
description: "用于 LLM 训练的 GPU 加速数据整理"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Nemo Curator {#nemo-curator}

用于 LLM 训练的 GPU 加速数据整理。支持文本/图像/视频/音频。具备模糊去重（速度提升 16 倍）、质量过滤（30+ 启发式规则）、语义去重、PII 脱敏、NSFW 检测等功能。借助 RAPIDS 跨 GPU 扩展。适用于准备高质量训练数据集、清洗网络数据或对大型语料库进行去重。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/nemo-curator` 安装 |
| 路径 | `optional-skills/mlops/nemo-curator` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖 | `nemo-curator`, `cudf`, `dask`, `rapids` |
| 标签 | `Data Processing`, `NeMo Curator`, `Data Curation`, `GPU Acceleration`, `Deduplication`, `Quality Filtering`, `NVIDIA`, `RAPIDS`, `PII Redaction`, `Multimodal`, `LLM Training Data` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# NeMo Curator - GPU 加速数据整理 {#nemo-curator-gpu-accelerated-data-curation}

NVIDIA 的工具包，用于为 LLM 准备高质量训练数据。

## 何时使用 NeMo Curator {#when-to-use-nemo-curator}

**在以下场景使用 NeMo Curator：**
- 从网络抓取（如 Common Crawl）准备 LLM 训练数据
- 需要快速去重（比 CPU 快 16 倍）
- 整理多模态数据集（文本、图像、视频、音频）
- 过滤低质量或有毒内容
- 跨 GPU 集群扩展数据处理

**性能**：
- **模糊去重速度提升 16 倍**（8TB RedPajama v2）
- **总拥有成本比 CPU 方案低 40%**
- **跨 GPU 节点近乎线性扩展**

**替代方案**：
- **datatrove**：基于 CPU 的开源数据处理
- **dolma**：Allen AI 的数据工具包
- **Ray Data**：通用 ML 数据处理（无数据整理功能）

## 快速开始 {#quick-start}

### 安装 {#installation}

```bash
# Text curation (CUDA 12)
uv pip install "nemo-curator[text_cuda12]"

# All modalities
uv pip install "nemo-curator[all_cuda12]"

# CPU-only (slower)
uv pip install "nemo-curator[cpu]"
```

### 基本文本整理流程 {#basic-text-curation-pipeline}

```python
from nemo_curator import ScoreFilter, Modify
from nemo_curator.datasets import DocumentDataset
import pandas as pd

# Load data
df = pd.DataFrame({"text": ["Good document", "Bad doc", "Excellent text"]})
dataset = DocumentDataset(df)

# Quality filtering
def quality_score(doc):
    return len(doc["text"].split()) > 5  # Filter short docs

filtered = ScoreFilter(quality_score)(dataset)

# Deduplication
from nemo_curator.modules import ExactDuplicates
deduped = ExactDuplicates()(filtered)

# Save
deduped.to_parquet("curated_data/")
```

## 数据整理流程 {#data-curation-pipeline}

### 阶段 1：质量过滤 {#stage-1-quality-filtering}

```python
from nemo_curator.filters import (
    WordCountFilter,
    RepeatedLinesFilter,
    UrlRatioFilter,
    NonAlphaNumericFilter
)

# Apply 30+ heuristic filters
from nemo_curator import ScoreFilter

# Word count filter
dataset = dataset.filter(WordCountFilter(min_words=50, max_words=100000))

# Remove repetitive content
dataset = dataset.filter(RepeatedLinesFilter(max_repeated_line_fraction=0.3))

# URL ratio filter
dataset = dataset.filter(UrlRatioFilter(max_url_ratio=0.2))
```
### 阶段 2：去重 {#stage-2-deduplication}

**精确去重**：
```python
from nemo_curator.modules import ExactDuplicates

# 移除完全重复的文档
deduped = ExactDuplicates(id_field="id", text_field="text")(dataset)
```

**模糊去重**（在 GPU 上快 16 倍）：
```python
from nemo_curator.modules import FuzzyDuplicates

# MinHash + LSH 去重
fuzzy_dedup = FuzzyDuplicates(
    id_field="id",
    text_field="text",
    num_hashes=260,      # MinHash 参数
    num_buckets=20,
    hash_method="md5"
)

deduped = fuzzy_dedup(dataset)
```

**语义去重**：
```python
from nemo_curator.modules import SemanticDuplicates

# 基于嵌入向量的去重
semantic_dedup = SemanticDuplicates(
    id_field="id",
    text_field="text",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    threshold=0.8  # 余弦相似度阈值
)

deduped = semantic_dedup(dataset)
```

### 阶段 3：PII 脱敏 {#stage-3-pii-redaction}

```python
from nemo_curator.modules import Modify
from nemo_curator.modifiers import PIIRedactor

# 脱敏个人身份信息
pii_redactor = PIIRedactor(
    supported_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "LOCATION"],
    anonymize_action="replace"  # 或 "redact"
)

redacted = Modify(pii_redactor)(dataset)
```

### 阶段 4：分类器过滤 {#stage-4-classifier-filtering}

```python
from nemo_curator.classifiers import QualityClassifier

# 质量分类
quality_clf = QualityClassifier(
    model_path="nvidia/quality-classifier-deberta",
    batch_size=256,
    device="cuda"
)

# 过滤低质量文档
high_quality = dataset.filter(lambda doc: quality_clf(doc["text"]) > 0.5)
```

## GPU 加速 {#gpu-acceleration}

### GPU 与 CPU 性能对比 {#gpu-vs-cpu-performance}

| 操作 | CPU（16 核） | GPU（A100） | 加速比 |
|-----------|----------------|------------|---------|
| 模糊去重（8TB） | 120 小时 | 7.5 小时 | 16× |
| 精确去重（1TB） | 8 小时 | 0.5 小时 | 16× |
| 质量过滤 | 2 小时 | 0.2 小时 | 10× |

### 多 GPU 扩展 {#multi-gpu-scaling}

```python
from nemo_curator import get_client
import dask_cuda

# 初始化 GPU 集群
client = get_client(cluster_type="gpu", n_workers=8)

# 使用 8 个 GPU 处理
deduped = FuzzyDuplicates(...)(dataset)
```

## 多模态整理 {#multi-modal-curation}

### 图像整理 {#image-curation}

```python
from nemo_curator.image import (
    AestheticFilter,
    NSFWFilter,
    CLIPEmbedder
)

# 美学评分
aesthetic_filter = AestheticFilter(threshold=5.0)
filtered_images = aesthetic_filter(image_dataset)

# NSFW 检测
nsfw_filter = NSFWFilter(threshold=0.9)
safe_images = nsfw_filter(filtered_images)

# 生成 CLIP 嵌入向量
clip_embedder = CLIPEmbedder(model="openai/clip-vit-base-patch32")
image_embeddings = clip_embedder(safe_images)
```

### 视频整理 {#video-curation}

```python
from nemo_curator.video import (
    SceneDetector,
    ClipExtractor,
    InternVideo2Embedder
)

# 检测场景
scene_detector = SceneDetector(threshold=27.0)
scenes = scene_detector(video_dataset)

# 提取片段
clip_extractor = ClipExtractor(min_duration=2.0, max_duration=10.0)
clips = clip_extractor(scenes)

# 生成嵌入向量
video_embedder = InternVideo2Embedder()
video_embeddings = video_embedder(clips)
```
### 音频数据清洗 {#audio-curation}

```python
from nemo_curator.audio import (
    ASRInference,
    WERFilter,
    DurationFilter
)

# ASR 转录
asr = ASRInference(model="nvidia/stt_en_fastconformer_hybrid_large_pc")
transcribed = asr(audio_dataset)

# 按 WER（词错误率）过滤
wer_filter = WERFilter(max_wer=0.3)
high_quality_audio = wer_filter(transcribed)

# 时长过滤
duration_filter = DurationFilter(min_duration=1.0, max_duration=30.0)
filtered_audio = duration_filter(high_quality_audio)
```

## 常见模式 {#common-patterns}

### 网页抓取数据清洗（Common Crawl） {#web-scrape-curation-common-crawl}

```python
from nemo_curator import ScoreFilter, Modify
from nemo_curator.filters import *
from nemo_curator.modules import *
from nemo_curator.datasets import DocumentDataset

# 加载 Common Crawl 数据
dataset = DocumentDataset.read_parquet("common_crawl/*.parquet")

# 流水线
pipeline = [
    # 1. 质量过滤
    WordCountFilter(min_words=100, max_words=50000),
    RepeatedLinesFilter(max_repeated_line_fraction=0.2),
    SymbolToWordRatioFilter(max_symbol_to_word_ratio=0.3),
    UrlRatioFilter(max_url_ratio=0.3),

    # 2. 语言过滤
    LanguageIdentificationFilter(target_languages=["en"]),

    # 3. 去重
    ExactDuplicates(id_field="id", text_field="text"),
    FuzzyDuplicates(id_field="id", text_field="text", num_hashes=260),

    # 4. PII 脱敏
    PIIRedactor(),

    # 5. NSFW 过滤
    NSFWClassifier(threshold=0.8)
]

# 执行
for stage in pipeline:
    dataset = stage(dataset)

# 保存
dataset.to_parquet("curated_common_crawl/")
```

### 分布式处理 {#distributed-processing}

```python
from nemo_curator import get_client
from dask_cuda import LocalCUDACluster

# 多 GPU 集群
cluster = LocalCUDACluster(n_workers=8)
client = get_client(cluster=cluster)

# 处理大规模数据集
dataset = DocumentDataset.read_parquet("s3://large_dataset/*.parquet")
deduped = FuzzyDuplicates(...)(dataset)

# 清理
client.close()
cluster.close()
```

## 性能基准 {#performance-benchmarks}

### 模糊去重（8TB RedPajama v2） {#fuzzy-deduplication-8tb-redpajama-v2}

- **CPU（256 核）**：120 小时
- **GPU（8× A100）**：7.5 小时
- **加速比**：16×

### 精确去重（1TB） {#exact-deduplication-1tb}

- **CPU（64 核）**：8 小时
- **GPU（4× A100）**：0.5 小时
- **加速比**：16×

### 质量过滤（100GB） {#quality-filtering-100gb}

- **CPU（32 核）**：2 小时
- **GPU（2× A100）**：0.2 小时
- **加速比**：10×

## 成本对比 {#cost-comparison}

**基于 CPU 的数据清洗**（AWS c5.18xlarge × 10）：
- 成本：$3.60/小时 × 10 = $36/小时
- 处理 8TB 耗时：120 小时
- **总计**：$4,320

**基于 GPU 的数据清洗**（AWS p4d.24xlarge × 2）：
- 成本：$32.77/小时 × 2 = $65.54/小时
- 处理 8TB 耗时：7.5 小时
- **总计**：$491.55

**节省**：降低 89%（节省 $3,828）

## 支持的数据格式 {#supported-data-formats}

- **输入**：Parquet、JSONL、CSV
- **输出**：Parquet（推荐）、JSONL
- **WebDataset**：多模态数据的 TAR 归档

## 使用场景 {#use-cases}

**生产部署**：
- NVIDIA 使用 NeMo Curator 准备 Nemotron-4 训练数据
- 已清洗的开源数据集：RedPajama v2、The Pile

## 参考文档 {#references}

- **[过滤指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/nemo-curator/references/filtering.md)** - 30 多种质量过滤器与启发式规则
- **[去重指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/nemo-curator/references/deduplication.md)** - 精确、模糊、语义去重方法
## 资源 {#resources}

- **GitHub**: https://github.com/NVIDIA/NeMo-Curator ⭐ 500+
- **文档**: https://docs.nvidia.com/nemo-framework/user-guide/latest/datacuration/
- **版本**: 0.4.0+
- **许可证**: Apache 2.0
