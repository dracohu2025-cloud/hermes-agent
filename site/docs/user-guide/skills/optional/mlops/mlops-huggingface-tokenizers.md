---
title: "Huggingface Tokenizers — 为研究和生产优化的快速分词器"
sidebar_label: "Huggingface Tokenizers"
description: "为研究和生产优化的快速分词器"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="huggingface-tokenizers"></a>
# Huggingface Tokenizers

为研究和生产优化的快速分词器。基于 Rust 的实现，可在 &lt;20 秒内处理 1GB 文本。支持 BPE、WordPiece 和 Unigram 算法。可训练自定义词表、跟踪对齐、处理填充/截断。与 transformers 无缝集成。在需要高性能分词或自定义分词器训练时使用。

<a id="skill-metadata"></a>
## Skill metadata

| | |
|---|---|
| Source | 可选 — 使用 `hermes skills install official/mlops/huggingface-tokenizers` 安装 |
| Path | `optional-skills/mlops/huggingface-tokenizers` |
| Version | `1.0.0` |
| Author | Orchestra Research |
| License | MIT |
| Dependencies | `tokenizers`, `transformers`, `datasets` |
| Platforms | linux, macos, windows |
| Tags | `Tokenization`, `HuggingFace`, `BPE`, `WordPiece`, `Unigram`, `Fast Tokenization`, `Rust`, `Custom Tokenizer`, `Alignment Tracking`, `Production` |

<a id="reference-full-skill-md"></a>
## Reference: full SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="huggingface-tokenizers-fast-tokenization-for-nlp"></a>
# HuggingFace Tokenizers - 面向 NLP 的快速分词

快速、生产就绪的分词器，兼具 Rust 的性能和 Python 的易用性。

<a id="when-to-use-huggingface-tokenizers"></a>
## When to use HuggingFace Tokenizers

**在以下情况下使用 HuggingFace Tokenizers：**
- 需要极快的分词速度（每 GB 文本 &lt;20 秒）
- 从零训练自定义分词器
- 需要对齐跟踪（词元 → 原始文本位置）
- 构建生产级 NLP 流水线
- 需要高效分词大规模语料

**性能：**
- **速度**：CPU 上每 &lt;20 秒处理 1GB
- **实现**：Rust 核心，带有 Python/Node.js 绑定
- **效率**：比纯 Python 实现快 10-100 倍

**可考虑替代方案：**
- **SentencePiece**：语言无关，被 T5/ALBERT 使用
- **tiktoken**：OpenAI 的 BPE 分词器，用于 GPT 模型
- **transformers AutoTokenizer**：仅加载预训练模型（内部使用此库）

<a id="quick-start"></a>
## Quick start

<a id="installation"></a>
### 安装

```bash
# Install tokenizers
pip install tokenizers

# With transformers integration
pip install tokenizers transformers
```

<a id="load-pretrained-tokenizer"></a>
### 加载预训练分词器

```python
from tokenizers import Tokenizer

# Load from HuggingFace Hub
tokenizer = Tokenizer.from_pretrained("bert-base-uncased")

# Encode text
output = tokenizer.encode("Hello, how are you?")
print(output.tokens)  # ['hello', ',', 'how', 'are', 'you', '?']
print(output.ids)     # [7592, 1010, 2129, 2024, 2017, 1029]

# Decode back
text = tokenizer.decode(output.ids)
print(text)  # "hello, how are you?"
```

<a id="train-custom-bpe-tokenizer"></a>
### 训练自定义 BPE 分词器

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

# Initialize tokenizer with BPE model
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
tokenizer.pre_tokenizer = Whitespace()

# Configure trainer
trainer = BpeTrainer(
    vocab_size=30000,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    min_frequency=2
)

# Train on files
files = ["train.txt", "validation.txt"]
tokenizer.train(files, trainer)

# Save
tokenizer.save("my-tokenizer.json")
```
**训练时间**：100MB 语料约需 1–2 分钟，1GB 约需 10–20 分钟

<a id="batch-encoding-with-padding"></a>
### 带填充的批量编码

```python
# Enable padding
tokenizer.enable_padding(pad_id=3, pad_token="[PAD]")

# Encode batch
texts = ["Hello world", "This is a longer sentence"]
encodings = tokenizer.encode_batch(texts)

for encoding in encodings:
    print(encoding.ids)
# [101, 7592, 2088, 102, 3, 3, 3]
# [101, 2023, 2003, 1037, 2936, 6251, 102]
```

<a id="tokenization-algorithms"></a>
## 分词算法

<a id="bpe-byte-pair-encoding"></a>
### BPE（字节对编码）

**工作原理**：
1. 从字符级词表开始
2. 找到出现最频繁的字符对
3. 合并为新 token，加入词表
4. 重复直到达到目标词表大小

**使用该算法的模型**：GPT-2、GPT-3、RoBERTa、BART、DeBERTa

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel

tokenizer = Tokenizer(BPE(unk_token="<|endoftext|>"))
tokenizer.pre_tokenizer = ByteLevel()

trainer = BpeTrainer(
    vocab_size=50257,
    special_tokens=["<|endoftext|>"],
    min_frequency=2
)

tokenizer.train(files=["data.txt"], trainer=trainer)
```

**优点**：
- 能较好地处理未登录词（拆分为子词）
- 词表大小灵活
- 对形态丰富的语言友好

**权衡**：
- 分词结果依赖于合并顺序
- 有时会意外拆分常见词

<a id="wordpiece"></a>
### WordPiece

**工作原理**：
1. 从字符级词表开始
2. 为合并对打分：`frequency(pair) / (frequency(first) × frequency(second))`
3. 合并得分最高的对
4. 重复直到达到目标词表大小

**使用该算法的模型**：BERT、DistilBERT、MobileBERT

```python
from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.trainers import WordPieceTrainer
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.normalizers import BertNormalizer

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))
tokenizer.normalizer = BertNormalizer(lowercase=True)
tokenizer.pre_tokenizer = Whitespace()

trainer = WordPieceTrainer(
    vocab_size=30522,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    continuing_subword_prefix="##"
)

tokenizer.train(files=["corpus.txt"], trainer=trainer)
```

**优点**：
- 优先合并有意义的组合（高分 = 语义相关）
- 在 BERT 上成功应用（达到 SOTA 效果）

**权衡**：
- 若无子词匹配，未知词会变成 `[UNK]`
- 只保存词表而非合并规则（文件较大）

<a id="unigram"></a>
### Unigram

**工作原理**：
1. 从大词表开始（所有子串）
2. 使用当前词表计算语料损失
3. 移除对损失影响最小的 token
4. 重复直到达到目标词表大小

**使用该算法的模型**：ALBERT、T5、mBART、XLNet（通过 SentencePiece）

```python
from tokenizers import Tokenizer
from tokenizers.models import Unigram
from tokenizers.trainers import UnigramTrainer

tokenizer = Tokenizer(Unigram())

trainer = UnigramTrainer(
    vocab_size=8000,
    special_tokens=["<unk>", "<s>", "</s>"],
    unk_token="<unk>"
)

tokenizer.train(files=["data.txt"], trainer=trainer)
```
**优势**：
- 概率性（找到最可能的 tokenization）
- 对没有词边界的语言效果良好
- 处理多样化的语言上下文

**权衡**：
- 训练计算成本高
- 需要调整更多超参数

<a id="tokenization-pipeline"></a>
## Tokenization 流水线

完整流水线：**Normalization → Pre-tokenization → Model → Post-processing**

<a id="normalization"></a>
### Normalization

清洗并标准化文本：

```python
from tokenizers.normalizers import NFD, StripAccents, Lowercase, Sequence

tokenizer.normalizer = Sequence([
    NFD(),           # Unicode 标准化（分解）
    Lowercase(),     # 转换为小写
    StripAccents()   # 去除重音符号
])

# 输入："Héllo WORLD"
# 标准化后："hello world"
```

**常用 normalizer**：
- `NFD`、`NFC`、`NFKD`、`NFKC` - Unicode 标准化形式
- `Lowercase()` - 转换为小写
- `StripAccents()` - 去除重音符号（é → e）
- `Strip()` - 去除空白字符
- `Replace(pattern, content)` - 正则替换

<a id="pre-tokenization"></a>
### Pre-tokenization

将文本拆分为类似单词的单元：

```python
from tokenizers.pre_tokenizers import Whitespace, Punctuation, Sequence, ByteLevel

# 按空白和标点拆分
tokenizer.pre_tokenizer = Sequence([
    Whitespace(),
    Punctuation()
])

# 输入："Hello, world!"
# pre-tokenization 后：["Hello", ",", "world", "!"]
```

**常用 pre-tokenizer**：
- `Whitespace()` - 按空格、制表符、换行符拆分
- `ByteLevel()` - GPT-2 风格的字节级拆分
- `Punctuation()` - 分离标点符号
- `Digits(individual_digits=True)` - 单独拆分数字
- `Metaspace()` - 用 ▁ 替换空格（SentencePiece 风格）

<a id="post-processing"></a>
### Post-processing

为模型输入添加特殊 token：

```python
from tokenizers.processors import TemplateProcessing

# BERT 风格：[CLS] 句子 [SEP]
tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B [SEP]",
    special_tokens=[
        ("[CLS]", 1),
        ("[SEP]", 2),
    ],
)
```

**常见模式**：
```python
# GPT-2：句子 <|endoftext|>
TemplateProcessing(
    single="$A <|endoftext|>",
    special_tokens=[("<|endoftext|>", 50256)]
)

# RoBERTa：<s> 句子 </s>
TemplateProcessing(
    single="<s> $A </s>",
    pair="<s> $A </s> </s> $B </s>",
    special_tokens=[("<s>", 0), ("</s>", 2)]
)
```

<a id="alignment-tracking"></a>
## 对齐追踪

追踪 token 在原始文本中的位置：

```python
output = tokenizer.encode("Hello, world!")

# 获取 token 偏移量
for token, offset in zip(output.tokens, output.offsets):
    start, end = offset
    print(f"{token:10} → [{start:2}, {end:2}): {text[start:end]!r}")

# 输出：
# hello      → [ 0,  5): 'Hello'
# ,          → [ 5,  6): ','
# world      → [ 7, 12): 'world'
# !          → [12, 13): '!'
```

**使用场景**：
- 命名实体识别（将预测映射回文本）
- 问答（提取答案片段）
- Token 分类（将标签对齐到原始位置）

<a id="integration-with-transformers"></a>
## 与 transformers 集成

<a id="load-with-autotokenizer"></a>
### 使用 AutoTokenizer 加载

```python
from transformers import AutoTokenizer

# AutoTokenizer 自动使用 fast tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# 检查是否使用 fast tokenizer
print(tokenizer.is_fast)  # True

# 访问底层的 tokenizers.Tokenizer
fast_tokenizer = tokenizer.backend_tokenizer
print(type(fast_tokenizer))  # <class 'tokenizers.Tokenizer'>
```
<a id="convert-custom-tokenizer-to-transformers"></a>
### 将自定义分词器转换为 transformers 格式

```python
from tokenizers import Tokenizer
from transformers import PreTrainedTokenizerFast

# 训练自定义分词器
tokenizer = Tokenizer(BPE())
# ... 训练分词器 ...
tokenizer.save("my-tokenizer.json")

# 包装为 transformers 格式
transformers_tokenizer = PreTrainedTokenizerFast(
    tokenizer_file="my-tokenizer.json",
    unk_token="[UNK]",
    pad_token="[PAD]",
    cls_token="[CLS]",
    sep_token="[SEP]",
    mask_token="[MASK]"
)

# 像使用任何 transformers 分词器一样使用
outputs = transformers_tokenizer(
    "Hello world",
    padding=True,
    truncation=True,
    max_length=512,
    return_tensors="pt"
)
```

<a id="common-patterns"></a>
## 常见模式

<a id="train-from-iterator-large-datasets"></a>
### 从迭代器训练（大型数据集）

```python
from datasets import load_dataset

# 加载数据集
dataset = load_dataset("wikitext", "wikitext-103-raw-v1", split="train")

# 创建批次迭代器
def batch_iterator(batch_size=1000):
    for i in range(0, len(dataset), batch_size):
        yield dataset[i:i + batch_size]["text"]

# 训练分词器
tokenizer.train_from_iterator(
    batch_iterator(),
    trainer=trainer,
    length=len(dataset)  # 用于显示进度条
)
```

**性能**：处理 1GB 数据约需 10-20 分钟

<a id="enable-truncation-and-padding"></a>
### 启用截断和填充

```python
# 启用截断
tokenizer.enable_truncation(max_length=512)

# 启用填充
tokenizer.enable_padding(
    pad_id=tokenizer.token_to_id("[PAD]"),
    pad_token="[PAD]",
    length=512  # 固定长度，或设为 None 以使用批次最大长度
)

# 同时使用两者进行编码
output = tokenizer.encode("This is a long sentence that will be truncated...")
print(len(output.ids))  # 512
```

<a id="multi-processing"></a>
### 多进程处理

```python
from tokenizers import Tokenizer
from multiprocessing import Pool

# 加载分词器
tokenizer = Tokenizer.from_file("tokenizer.json")

def encode_batch(texts):
    return tokenizer.encode_batch(texts)

# 并行处理大型语料库
with Pool(8) as pool:
    # 将语料库分块
    chunk_size = 1000
    chunks = [corpus[i:i+chunk_size] for i in range(0, len(corpus), chunk_size)]

    # 并行编码
    results = pool.map(encode_batch, chunks)
```

**加速比**：8 核下可达 5-8 倍

<a id="performance-benchmarks"></a>
## 性能基准测试

<a id="training-speed"></a>
### 训练速度

| 语料库大小 | BPE（30k 词表） | WordPiece（30k） | Unigram（8k） |
|------------|-----------------|------------------|---------------|
| 10 MB      | 15 秒           | 18 秒            | 25 秒         |
| 100 MB     | 1.5 分钟        | 2 分钟           | 4 分钟        |
| 1 GB       | 15 分钟         | 20 分钟          | 40 分钟       |

**硬件**：16 核 CPU，测试于英文维基百科

<a id="tokenization-speed"></a>
### 分词速度

| 实现方式       | 1 GB 语料库 | 吞吐量       |
|----------------|-------------|--------------|
| 纯 Python      | ~20 分钟    | ~50 MB/分钟  |
| HF Tokenizers  | ~15 秒      | ~4 GB/分钟   |
| **加速比**     | **80 倍**   | **80 倍**    |

**测试**：英文文本，平均句子长度 20 词

<a id="memory-usage"></a>
### 内存使用

| 任务                     | 内存    |
|--------------------------|---------|
| 加载分词器               | ~10 MB  |
| 训练 BPE（30k 词表）     | ~200 MB |
| 编码 100 万条句子        | ~500 MB |
<a id="supported-models"></a>
## 支持的模型

通过 `from_pretrained()` 可用的预训练分词器：

**BERT 系列**：
- `bert-base-uncased`、`bert-large-cased`
- `distilbert-base-uncased`
- `roberta-base`、`roberta-large`

**GPT 系列**：
- `gpt2`、`gpt2-medium`、`gpt2-large`
- `distilgpt2`

**T5 系列**：
- `t5-small`、`t5-base`、`t5-large`
- `google/flan-t5-xxl`

**其他**：
- `facebook/bart-base`、`facebook/mbart-large-cc25`
- `albert-base-v2`、`albert-xlarge-v2`
- `xlm-roberta-base`、`xlm-roberta-large`

浏览全部：https://huggingface.co/models?library=tokenizers

<a id="references"></a>
## 参考资料

- **[训练指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/huggingface-tokenizers/references/training.md)** - 训练自定义分词器、配置训练器、处理大型数据集
- **[算法深入解析](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/huggingface-tokenizers/references/algorithms.md)** - 详细解释 BPE、WordPiece、Unigram
- **[流水线组件](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/huggingface-tokenizers/references/pipeline.md)** - 归一化器、预分词器、后处理器、解码器
- **[Transformers 集成](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/huggingface-tokenizers/references/integration.md)** - AutoTokenizer、PreTrainedTokenizerFast、特殊标记

<a id="resources"></a>
## 资源

- **文档**：https://huggingface.co/docs/tokenizers
- **GitHub**：https://github.com/huggingface/tokenizers ⭐ 9,000+
- **版本**：0.20.0+
- **课程**：https://huggingface.co/learn/nlp-course/chapter6/1
- **论文**：BPE（Sennrich 等人，2016）、WordPiece（Schuster & Nakajima，2012）
