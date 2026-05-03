---
title: "Chroma — 面向 AI 应用的开源嵌入数据库"
sidebar_label: "Chroma"
description: "面向 AI 应用的开源嵌入数据库"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Chroma {#chroma}

面向 AI 应用的开源嵌入数据库。存储嵌入向量和元数据，执行向量搜索和全文搜索，按元数据过滤。提供简单的 4 函数 API。可从笔记本扩展到生产集群。适用于语义搜索、RAG 应用或文档检索。最适合本地开发和开源项目。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/chroma` 安装 |
| 路径 | `optional-skills/mlops/chroma` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `chromadb`, `sentence-transformers` |
| 标签 | `RAG`, `Chroma`, `Vector Database`, `Embeddings`, `Semantic Search`, `Open Source`, `Self-Hosted`, `Document Retrieval`, `Metadata Filtering` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Chroma - 开源嵌入数据库 {#chroma-open-source-embedding-database}

用于构建带记忆的 LLM 应用的 AI 原生数据库。

## 何时使用 Chroma {#when-to-use-chroma}

**在以下情况下使用 Chroma：**
- 构建 RAG（检索增强生成）应用
- 需要本地/自托管向量数据库
- 想要开源解决方案（Apache 2.0）
- 在笔记本中做原型开发
- 对文档进行语义搜索
- 存储带元数据的嵌入向量

**指标**：
- **24,300+ GitHub 星标**
- **1,900+ 分支**
- **v1.3.3**（稳定版，每周发布）
- **Apache 2.0 许可证**

**改用其他替代方案**：
- **Pinecone**：托管云服务，自动扩缩
- **FAISS**：纯相似度搜索，无元数据
- **Weaviate**：生产级 ML 原生数据库
- **Qdrant**：高性能，基于 Rust

## 快速开始 {#quick-start}

### 安装 {#installation}

```bash
# Python
pip install chromadb

# JavaScript/TypeScript
npm install chromadb @chroma-core/default-embed
```

### 基本用法（Python） {#basic-usage-python}

```python
import chromadb

# 创建客户端
client = chromadb.Client()

# 创建集合
collection = client.create_collection(name="my_collection")

# 添加文档
collection.add(
    documents=["这是文档 1", "这是文档 2"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# 查询
results = collection.query(
    query_texts=["关于某个主题的文档"],
    n_results=2
)

print(results)
```

## 核心操作 {#core-operations}

### 1. 创建集合 {#1-create-collection}

```python
# 简单集合
collection = client.create_collection("my_docs")

# 使用自定义嵌入函数
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="my_docs",
    embedding_function=openai_ef
)

# 获取已有集合
collection = client.get_collection("my_docs")

# 删除集合
client.delete_collection("my_docs")
```
### 2. 添加文档 {#2-add-documents}

```python
# Add with auto-generated IDs
collection.add(
    documents=["Doc 1", "Doc 2", "Doc 3"],
    metadatas=[
        {"source": "web", "category": "tutorial"},
        {"source": "pdf", "page": 5},
        {"source": "api", "timestamp": "2025-01-01"}
    ],
    ids=["id1", "id2", "id3"]
)

# Add with custom embeddings
collection.add(
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    documents=["Doc 1", "Doc 2"],
    ids=["id1", "id2"]
)
```

### 3. 查询（相似度搜索） {#3-query-similarity-search}

```python
# Basic query
results = collection.query(
    query_texts=["machine learning tutorial"],
    n_results=5
)

# Query with filters
results = collection.query(
    query_texts=["Python programming"],
    n_results=3,
    where={"source": "web"}
)

# Query with metadata filters
results = collection.query(
    query_texts=["advanced topics"],
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$gte": 3}}
        ]
    }
)

# Access results
print(results["documents"])      # List of matching documents
print(results["metadatas"])      # Metadata for each doc
print(results["distances"])      # Similarity scores
print(results["ids"])            # Document IDs
```

### 4. 获取文档 {#4-get-documents}

```python
# Get by IDs
docs = collection.get(
    ids=["id1", "id2"]
)

# Get with filters
docs = collection.get(
    where={"category": "tutorial"},
    limit=10
)

# Get all documents
docs = collection.get()
```

### 5. 更新文档 {#5-update-documents}

```python
# Update document content
collection.update(
    ids=["id1"],
    documents=["Updated content"],
    metadatas=[{"source": "updated"}]
)
```

### 6. 删除文档 {#6-delete-documents}

```python
# Delete by IDs
collection.delete(ids=["id1", "id2"])

# Delete with filter
collection.delete(
    where={"source": "outdated"}
)
```

## 持久化存储 {#persistent-storage}

```python
# Persist to disk
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.create_collection("my_docs")
collection.add(documents=["Doc 1"], ids=["id1"])

# Data persisted automatically
# Reload later with same path
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_docs")
```

## 嵌入函数 {#embedding-functions}

### 默认（Sentence Transformers） {#default-sentence-transformers}

```python
# Uses sentence-transformers by default
collection = client.create_collection("my_docs")
# Default model: all-MiniLM-L6-v2
```

### OpenAI {#openai}

```python
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="openai_docs",
    embedding_function=openai_ef
)
```

### HuggingFace {#huggingface}

```python
huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
    api_key="your-key",
    model_name="sentence-transformers/all-mpnet-base-v2"
)

collection = client.create_collection(
    name="hf_docs",
    embedding_function=huggingface_ef
)
```

### 自定义嵌入函数 {#custom-embedding-function}

```python
from chromadb import Documents, EmbeddingFunction, Embeddings

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # Your embedding logic
        return embeddings

my_ef = MyEmbeddingFunction()
collection = client.create_collection(
    name="custom_docs",
    embedding_function=my_ef
)
```
## 元数据过滤 {#metadata-filtering}

```python
# 精确匹配
results = collection.query(
    query_texts=["query"],
    where={"category": "tutorial"}
)

# 比较运算符
results = collection.query(
    query_texts=["query"],
    where={"page": {"$gt": 10}}  # $gt, $gte, $lt, $lte, $ne
)

# 逻辑运算符
results = collection.query(
    query_texts=["query"],
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$lte": 3}}
        ]
    }  # 也支持：$or
)

# 包含关系
results = collection.query(
    query_texts=["query"],
    where={"tags": {"$in": ["python", "ml"]}}
)
```

## LangChain 集成 {#langchain-integration}

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 拆分文档
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(documents)

# 创建 Chroma 向量存储
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)

# 查询
results = vectorstore.similarity_search("machine learning", k=3)

# 作为检索器使用
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

## LlamaIndex 集成 {#llamaindex-integration}

```python
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
import chromadb

# 初始化 Chroma
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("my_collection")

# 创建向量存储
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 创建索引
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)

# 查询
query_engine = index.as_query_engine()
response = query_engine.query("What is machine learning?")
```

## 服务端模式 {#server-mode}

```python
# 运行 Chroma 服务端
# 终端：chroma run --path ./chroma_db --port 8000

# 连接到服务端
import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host="localhost",
    port=8000,
    settings=Settings(anonymized_telemetry=False)
)

# 正常使用
collection = client.get_or_create_collection("my_docs")
```

## 最佳实践 {#best-practices}

1. **使用持久化客户端** - 重启后数据不丢失
2. **添加元数据** - 支持过滤和追踪
3. **批量操作** - 一次性添加多个文档
4. **选择合适的嵌入模型** - 平衡速度与质量
5. **使用过滤器** - 缩小搜索范围
6. **使用唯一 ID** - 避免冲突
7. **定期备份** - 复制 chroma_db 目录
8. **监控集合大小** - 必要时扩容
9. **测试嵌入函数** - 确保质量
10. **生产环境使用服务端模式** - 更适合多用户场景

## 性能 {#performance}

| 操作 | 延迟 | 说明 |
|-----------|---------|-------|
| 添加 100 个文档 | ~1-3 秒 | 包含嵌入计算 |
| 查询（前 10 条） | ~50-200 毫秒 | 取决于集合大小 |
| 元数据过滤 | ~10-50 毫秒 | 正确索引后速度很快 |
## 资源 {#resources}

- **GitHub**: https://github.com/chroma-core/chroma ⭐ 24,300+
- **文档**: https://docs.trychroma.com
- **Discord**: https://discord.gg/MMeYNTmh3x
- **版本**: 1.3.3+
- **许可证**: Apache 2.0
