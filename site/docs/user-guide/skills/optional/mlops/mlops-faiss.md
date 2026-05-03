---
title: "Faiss — Facebook 的高效向量相似度搜索与聚类库"
sidebar_label: "Faiss"
description: "Facebook 的高效向量相似度搜索与聚类库"
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 从技能所在目录的 SKILL.md 自动生成。如需编辑，请修改 SKILL.md 源文件，而非此页面。 */}

# Faiss {#faiss}

Facebook 开发的高效密集向量相似度搜索与聚类库。支持数十亿向量、GPU 加速以及多种索引类型（Flat、IVF、HNSW）。适用于快速 k 近邻搜索、大规模向量检索，或无需元数据过滤的纯相似度搜索场景。最适合高性能应用。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/faiss` 安装 |
| 路径 | `optional-skills/mlops/faiss` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖 | `faiss-cpu`、`faiss-gpu`、`numpy` |
| 标签 | `RAG`、`FAISS`、`相似度搜索`、`向量搜索`、`Facebook AI`、`GPU 加速`、`亿级规模`、`K-NN`、`HNSW`、`高性能`、`大规模` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。即技能激活时 agent 看到的指令内容。
:::

# FAISS — 高效相似度搜索 {#faiss-efficient-similarity-search}

Facebook AI 面向十亿级向量相似度搜索的库。

## 何时使用 FAISS {#when-to-use-faiss}

**使用 FAISS 的场景：**
- 需要对大规模向量数据集（百万级 / 十亿级）进行快速相似度搜索
- 需要 GPU 加速
- 纯向量相似度搜索（无需元数据过滤）
- 对高吞吐、低延迟有严格要求
- 离线或批量处理 Embedding

**指标**：
- **GitHub 星标 31,700+**
- Meta / Facebook AI Research
- **可处理十亿级向量**
- **C++** 实现，提供 Python 绑定

**可替代方案**：
- **Chroma/Pinecone**：需要元数据过滤时使用
- **Weaviate**：需要完整数据库功能时使用
- **Annoy**：更简单但功能较少

## 快速开始 {#quick-start}

### 安装 {#installation}

```bash
# 仅 CPU
pip install faiss-cpu

# GPU 支持
pip install faiss-gpu
```

### 基本用法 {#basic-usage}

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
k = 5  # 找出 5 个最近邻
query = np.random.random((1, d)).astype('float32')
distances, indices = index.search(query, k)

print(f"最近邻索引: {indices}")
print(f"距离: {distances}")
```

## 索引类型 {#index-types}

### 1. 平面索引（精确搜索） {#1-flat-exact-search}

```python
# L2（欧几里得）距离
index = faiss.IndexFlatL2(d)

# 内积（若向量已归一化则等价于余弦相似度）
index = faiss.IndexFlatIP(d)

# 速度最慢，精度最高
```

### 2. IVF（倒排文件）— 快速近似索引 {#2-ivf-inverted-file-fast-approximate}

```python
# 创建量化器
quantizer = faiss.IndexFlatL2(d)

# IVF 索引，100 个聚类
nlist = 100
index = faiss.IndexIVFFlat(quantizer, d, nlist)

# 在数据上训练
index.train(vectors)

# 添加向量
index.add(vectors)

# 搜索（nprobe = 搜索的聚类数量）
index.nprobe = 10
distances, indices = index.search(query, k)
```
### 3. HNSW (Hierarchical NSW) - 最佳质量/速度 {#3-hnsw-hierarchical-nsw-best-quality-speed}

```python
# HNSW index
M = 32  # 每层连接数
index = faiss.IndexHNSWFlat(d, M)

# 无需训练
index.add(vectors)

# 搜索
distances, indices = index.search(query, k)
```

### 4. 乘积量化 - 节省内存 {#4-product-quantization-memory-efficient}

```python
# PQ 将内存降低 16-32 倍
m = 8   # 子量化器数量
nbits = 8
index = faiss.IndexPQ(d, m, nbits)

# 训练并添加
index.train(vectors)
index.add(vectors)
```

## 保存与加载 {#save-and-load}

```python
# 保存索引
faiss.write_index(index, "large.index")

# 加载索引
index = faiss.read_index("large.index")

# 继续使用
distances, indices = index.search(query, k)
```

## GPU 加速 {#gpu-acceleration}

```python
# 单 GPU
res = faiss.StandardGpuResources()
index_cpu = faiss.IndexFlatL2(d)
index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)  # GPU 0

# 多 GPU
index_gpu = faiss.index_cpu_to_all_gpus(index_cpu)

# 比 CPU 快 10-100 倍
```

## LangChain 集成 {#langchain-integration}

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# 创建 FAISS 向量库
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

## LlamaIndex 集成 {#llamaindex-integration}

```python
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss

# 创建 FAISS 索引
d = 1536
faiss_index = faiss.IndexFlatL2(d)

vector_store = FaissVectorStore(faiss_index=faiss_index)
```

## 最佳实践 {#best-practices}

1. **选择合适的索引类型** — 小于 10K 用 Flat，10K-1M 用 IVF，追求质量用 HNSW
2. **对余弦相似度做归一化** — 使用归一化向量配合 IndexFlatIP
3. **大数据集用 GPU** — 快 10-100 倍
4. **保存训练好的索引** — 训练成本高昂
5. **调优 nprobe/ef_search** — 平衡速度与精度
6. **监控内存** — 大数据集用 PQ
7. **批量查询** — 更好地利用 GPU

## 性能对比 {#performance}

| 索引类型 | 构建时间 | 搜索时间 | 内存 | 精度 |
|----------|----------|----------|------|------|
| Flat     | 快       | 慢       | 高   | 100% |
| IVF      | 中等     | 快       | 中等 | 95-99% |
| HNSW     | 慢       | 最快     | 高   | 99% |
| PQ       | 中等     | 快       | 低   | 90-95% |

## 资源 {#resources}

- **GitHub**: https://github.com/facebookresearch/faiss ⭐ 31,700+
- **Wiki**: https://github.com/facebookresearch/faiss/wiki
- **许可证**: MIT
