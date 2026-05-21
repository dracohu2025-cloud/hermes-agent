---
title: "Faiss — Facebook 的高效稠密向量相似性搜索与聚类库"
sidebar_label: "Faiss"
description: "Facebook 的高效稠密向量相似性搜索与聚类库"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="faiss"></a>
# Faiss

Facebook 的高效稠密向量相似性搜索与聚类库。支持数十亿向量、GPU 加速以及多种索引类型（Flat、IVF、HNSW）。适用于快速 k-NN 搜索、大规模向量检索，或当你需要纯相似性搜索而无需元数据过滤时。最适合高性能应用场景。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/faiss` 安装 |
| 路径 | `optional-skills/mlops/faiss` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `faiss-cpu`、`faiss-gpu`、`numpy` |
| 平台 | linux, macos |
| 标签 | `RAG`、`FAISS`、`相似性搜索`、`向量搜索`、`Facebook AI`、`GPU 加速`、`十亿级`、`K-NN`、`HNSW`、`高性能`、`大规模` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

<a id="faiss-efficient-similarity-search"></a>
# FAISS - 高效相似性搜索

Facebook AI 的十亿级向量相似性搜索库。

<a id="when-to-use-faiss"></a>
## 何时使用 FAISS

**在以下情况使用 FAISS：**
- 需要对大型向量数据集（百万/十亿级）进行快速相似性搜索
- 需要 GPU 加速
- 纯向量相似性（无需元数据过滤）
- 高吞吐量、低延迟是关键
- 对嵌入进行离线/批量处理

**指标**：
- **31,700+ GitHub 星标**
- Meta/Facebook AI Research
- **可处理数十亿向量**
- **C++** 并带有 Python 绑定

**改用其他替代方案**：
- **Chroma/Pinecone**：需要元数据过滤
- **Weaviate**：需要完整的数据库功能
- **Annoy**：更简单，功能更少

<a id="quick-start"></a>
## 快速入门

<a id="installation"></a>
### 安装

```bash
# 仅 CPU
pip install faiss-cpu

# GPU 支持
pip install faiss-gpu
```

<a id="basic-usage"></a>
### 基本用法

```python
import faiss
import numpy as np

# 创建示例数据（1000 个向量，128 维）
d = 128
nb = 1000
vectors = np.random.random((nb, d)).astype('float32')

# 创建索引
index = faiss.IndexFlatL2(d)  # L2 距离
index.add(vectors)             # 添加向量

# 搜索
k = 5  # 查找 5 个最近邻
query = np.random.random((1, d)).astype('float32')
distances, indices = index.search(query, k)

print(f"最近邻: {indices}")
print(f"距离: {distances}")
```

<a id="index-types"></a>
## 索引类型

<a id="1-flat-exact-search"></a>
### 1. Flat（精确搜索）

```python
# L2（欧几里得）距离
index = faiss.IndexFlatL2(d)

# 内积（如果向量已归一化，则相当于余弦相似度）
index = faiss.IndexFlatIP(d)

# 最慢，但最准确
```

<a id="2-ivf-inverted-file-fast-approximate"></a>
### 2. IVF（倒排文件）- 快速近似搜索

```python
# 创建量化器
quantizer = faiss.IndexFlatL2(d)

# 具有 100 个簇的 IVF 索引
nlist = 100
index = faiss.IndexIVFFlat(quantizer, d, nlist)

# 在数据上训练
index.train(vectors)

# 添加向量
index.add(vectors)

# 搜索（nprobe = 要搜索的簇数量）
index.nprobe = 10
distances, indices = index.search(query, k)
```
<a id="3-hnsw-hierarchical-nsw-best-quality-speed"></a>
### 3. HNSW（分层可导航小世界图）- 最佳质量/速度

```python
# HNSW 索引
M = 32  # 每层连接数
index = faiss.IndexHNSWFlat(d, M)

# 无需训练
index.add(vectors)

# 搜索
distances, indices = index.search(query, k)
```

<a id="4-product-quantization-memory-efficient"></a>
### 4. 乘积量化 - 内存高效

```python
# PQ 可将内存减少 16-32 倍
m = 8   # 子量化器数量
nbits = 8
index = faiss.IndexPQ(d, m, nbits)

# 训练并添加
index.train(vectors)
index.add(vectors)
```

<a id="save-and-load"></a>
## 保存与加载

```python
# 保存索引
faiss.write_index(index, "large.index")

# 加载索引
index = faiss.read_index("large.index")

# 继续使用
distances, indices = index.search(query, k)
```

<a id="gpu-acceleration"></a>
## GPU 加速

```python
# 单 GPU
res = faiss.StandardGpuResources()
index_cpu = faiss.IndexFlatL2(d)
index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)  # GPU 0

# 多 GPU
index_gpu = faiss.index_cpu_to_all_gpus(index_cpu)

# 比 CPU 快 10-100 倍
```

<a id="langchain-integration"></a>
## LangChain 集成

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# 创建 FAISS 向量存储
vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())

# 保存
vectorstore.save_local("faiss_index")

# 加载
vectorstore = FAISS.load_local(
    "faiss_index",
    OpenAIEmbeddings(),
    allow_dangerous_deserialization=True
)

# 搜索
results = vectorstore.similarity_search("query", k=5)
```

<a id="llamaindex-integration"></a>
## LlamaIndex 集成

```python
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss

# 创建 FAISS 索引
d = 1536
faiss_index = faiss.IndexFlatL2(d)

vector_store = FaissVectorStore(faiss_index=faiss_index)
```

<a id="best-practices"></a>
## 最佳实践

1. **选择合适的索引类型** - 数据量小于 10K 用 Flat，10K-1M 用 IVF，追求质量用 HNSW
2. **为余弦相似度做归一化** - 使用 IndexFlatIP 配合归一化向量
3. **大数据集用 GPU** - 速度快 10-100 倍
4. **保存训练好的索引** - 训练成本高
5. **调优 nprobe/ef_search** - 平衡速度与精度
6. **监控内存** - 大数据集用 PQ
7. **批量查询** - 更好利用 GPU

<a id="performance"></a>
## 性能对比

| 索引类型 | 构建时间 | 搜索时间 | 内存 | 准确率 |
|----------|----------|----------|------|--------|
| Flat | 快 | 慢 | 高 | 100% |
| IVF | 中等 | 快 | 中等 | 95-99% |
| HNSW | 慢 | 最快 | 高 | 99% |
| PQ | 中等 | 快 | 低 | 90-95% |

<a id="resources"></a>
## 资源

- **GitHub**: https://github.com/facebookresearch/faiss ⭐ 31,700+
- **Wiki**: https://github.com/facebookresearch/faiss/wiki
- **许可证**: MIT
