---
title: "Outlines — Outlines：结构化 JSON/正则/Pydantic LLM 生成"
sidebar_label: "Outlines"
description: "Outlines：结构化 JSON/正则/Pydantic LLM 生成"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="outlines"></a>
# Outlines

Outlines：结构化 JSON/正则/Pydantic LLM 生成。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/outlines` 安装 |
| 路径 | `optional-skills/mlops/inference/outlines` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `outlines`, `transformers`, `vllm`, `pydantic` |
| 平台 | linux, macos, windows |
| 标签 | `Prompt Engineering`, `Outlines`, `Structured Generation`, `JSON Schema`, `Pydantic`, `Local Models`, `Grammar-Based Generation`, `vLLM`, `Transformers`, `Type Safety` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="outlines-structured-text-generation"></a>
# Outlines：结构化文本生成

<a id="when-to-use-this-skill"></a>
## 何时使用此技能

在以下场景下，你应该使用 Outlines：
- **保证生成的 JSON/XML/代码结构有效**
- **使用 Pydantic 模型** 实现类型安全的输出
- **支持本地模型**（Transformers、llama.cpp、vLLM）
- **通过零开销的结构化生成最大化推理速度**
- **自动根据 JSON 模式生成**
- **在语法层面控制 token 采样**

**GitHub Stars**: 8000+ | **来自**: dottxt.ai（原 .txt）

<a id="installation"></a>
## 安装

```bash
# 基础安装
pip install outlines

# 使用特定后端
pip install outlines transformers  # Hugging Face 模型
pip install outlines llama-cpp-python  # llama.cpp
pip install outlines vllm  # 高吞吐量 vLLM
```

<a id="quick-start"></a>
## 快速开始

<a id="basic-example-classification"></a>
### 基本示例：分类

```python
import outlines
from typing import Literal

# 加载模型
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 使用类型约束生成
prompt = "情感分析：'这个产品太棒了！'："
generator = outlines.generate.choice(model, ["positive", "negative", "neutral"])
sentiment = generator(prompt)

print(sentiment)  # "positive"（保证是这些值之一）
```

<a id="with-pydantic-models"></a>
### 使用 Pydantic 模型

```python
from pydantic import BaseModel
import outlines

class User(BaseModel):
    name: str
    age: int
    email: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 生成结构化输出
prompt = "提取用户：John Doe, 30岁, john@example.com"
generator = outlines.generate.json(model, User)
user = generator(prompt)

print(user.name)   # "John Doe"
print(user.age)    # 30
print(user.email)  # "john@example.com"
```

<a id="core-concepts"></a>
## 核心概念

<a id="1-constrained-token-sampling"></a>
### 1. 受限 Token 采样

Outlines 使用有限状态机（FSM）在 logit 级别约束 token 生成。

**工作原理：**
1. 将模式（JSON/Pydantic/正则）转换为上下文无关文法（CFG）
2. 将 CFG 转换为有限状态机（FSM）
3. 在生成过程中每一步过滤无效 token
4. 当只有一个有效 token 时快速前进
**优势：**
- **零开销**：在 token 级别进行过滤
- **速度提升**：快速跳过确定性路径
- **保证有效性**：不可能产生无效输出

```python
import outlines

# Pydantic 模型 -> JSON 模式 -> CFG -> FSM
class Person(BaseModel):
    name: str
    age: int

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 幕后过程：
# 1. Person -> JSON 模式
# 2. JSON 模式 -> CFG
# 3. CFG -> FSM
# 4. FSM 在生成过程中过滤 token

generator = outlines.generate.json(model, Person)
result = generator("生成人员：Alice, 25")
```

<a id="2-structured-generators"></a>
### 2. 结构化生成器

Outlines 为不同的输出类型提供了专门的生成器。

<a id="choice-generator"></a>
#### 选择生成器

```python
# 多项选择
generator = outlines.generate.choice(
    model,
    ["positive", "negative", "neutral"]
)

sentiment = generator("评论：这个很好！")
# 结果：三个选项之一
```

<a id="json-generator"></a>
#### JSON 生成器

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

# 生成匹配模式的合法 JSON
generator = outlines.generate.json(model, Product)
product = generator("提取：iPhone 15, $999, 有货")

# 保证是合法的 Product 实例
print(type(product))  # <class '__main__.Product'>
```

<a id="regex-generator"></a>
#### 正则表达式生成器

```python
# 生成匹配正则表达式的文本
generator = outlines.generate.regex(
    model,
    r"[0-9]{3}-[0-9]{3}-[0-9]{4}"  # 电话号码模式
)

phone = generator("生成电话号码：")
# 结果："555-123-4567"（保证符合模式）
```

<a id="integer-float-generators"></a>
#### 整数/浮点数生成器

```python
# 生成特定数值类型
int_generator = outlines.generate.integer(model)
age = int_generator("人员年龄：")  # 保证是整数

float_generator = outlines.generate.float(model)
price = float_generator("产品价格：")  # 保证是浮点数
```

<a id="3-model-backends"></a>
### 3. 模型后端

Outlines 支持多种本地和基于 API 的后端。

<a id="transformers-hugging-face"></a>
#### Transformers（Hugging Face）

```python
import outlines

# 从 Hugging Face 加载
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda"  # 或 "cpu"
)

# 搭配任何生成器使用
generator = outlines.generate.json(model, YourModel)
```

<a id="llama-cpp"></a>
#### llama.cpp

```python
# 加载 GGUF 模型
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35
)

generator = outlines.generate.json(model, YourModel)
```

<a id="vllm-high-throughput"></a>
#### vLLM（高吞吐量）

```python
# 用于生产部署
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=2  # 多 GPU
)

generator = outlines.generate.json(model, YourModel)
```

<a id="openai-limited-support"></a>
#### OpenAI（有限支持）

```python
# 基础 OpenAI 支持
model = outlines.models.openai(
    "gpt-4o-mini",
    api_key="your-api-key"
)

# 注意：部分功能在 API 模型上受限
generator = outlines.generate.json(model, YourModel)
```

<a id="4-pydantic-integration"></a>
### 4. Pydantic 集成
Outlines 为 Pydantic 提供了一流的支持，能够自动进行 Schema 转换。

<a id="basic-models"></a>
#### 基础模型

```python
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="Article title")
    author: str = Field(description="Author name")
    word_count: int = Field(description="Number of words", gt=0)
    tags: list[str] = Field(description="List of tags")

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, Article)

article = generator("Generate article about AI")
print(article.title)
print(article.word_count)  # Guaranteed > 0
```

<a id="nested-models"></a>
#### 嵌套模型

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    age: int
    address: Address  # Nested model

generator = outlines.generate.json(model, Person)
person = generator("Generate person in New York")

print(person.address.city)  # "New York"
```

<a id="enums-and-literals"></a>
#### 枚举与字面量

```python
from enum import Enum
from typing import Literal

class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Application(BaseModel):
    applicant: str
    status: Status  # Must be one of enum values
    priority: Literal["low", "medium", "high"]  # Must be one of literals

generator = outlines.generate.json(model, Application)
app = generator("Generate application")

print(app.status)  # Status.PENDING (or APPROVED/REJECTED)
```

<a id="common-patterns"></a>
## 常见模式

<a id="pattern-1-data-extraction"></a>
### 模式一：数据提取

```python
from pydantic import BaseModel
import outlines

class CompanyInfo(BaseModel):
    name: str
    founded_year: int
    industry: str
    employees: int

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, CompanyInfo)

text = """
Apple Inc. was founded in 1976 in the technology industry.
The company employs approximately 164,000 people worldwide.
"""

prompt = f"Extract company information:\n{text}\n\nCompany:"
company = generator(prompt)

print(f"Name: {company.name}")
print(f"Founded: {company.founded_year}")
print(f"Industry: {company.industry}")
print(f"Employees: {company.employees}")
```

<a id="pattern-2-classification"></a>
### 模式二：分类

```python
from typing import Literal
import outlines

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Binary classification
generator = outlines.generate.choice(model, ["spam", "not_spam"])
result = generator("Email: Buy now! 50% off!")

# Multi-class classification
categories = ["technology", "business", "sports", "entertainment"]
category_gen = outlines.generate.choice(model, categories)
category = category_gen("Article: Apple announces new iPhone...")

# With confidence
class Classification(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    confidence: float

classifier = outlines.generate.json(model, Classification)
result = classifier("Review: This product is okay, nothing special")
```
<a id="pattern-3-structured-forms"></a>
### 模式 3：结构化表单

```python
class UserProfile(BaseModel):
    full_name: str
    age: int
    email: str
    phone: str
    country: str
    interests: list[str]

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, UserProfile)

prompt = """
Extract user profile from:
Name: Alice Johnson
Age: 28
Email: alice@example.com
Phone: 555-0123
Country: USA
Interests: hiking, photography, cooking
"""

profile = generator(prompt)
print(profile.full_name)
print(profile.interests)  # ["hiking", "photography", "cooking"]
```

<a id="pattern-4-multi-entity-extraction"></a>
### 模式 4：多实体抽取

```python
class Entity(BaseModel):
    name: str
    type: Literal["PERSON", "ORGANIZATION", "LOCATION"]

class DocumentEntities(BaseModel):
    entities: list[Entity]

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, DocumentEntities)

text = "Tim Cook met with Satya Nadella at Microsoft headquarters in Redmond."
prompt = f"Extract entities from: {text}"

result = generator(prompt)
for entity in result.entities:
    print(f"{entity.name} ({entity.type})")
```

<a id="pattern-5-code-generation"></a>
### 模式 5：代码生成

```python
class PythonFunction(BaseModel):
    function_name: str
    parameters: list[str]
    docstring: str
    body: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, PythonFunction)

prompt = "Generate a Python function to calculate factorial"
func = generator(prompt)

print(f"def {func.function_name}({', '.join(func.parameters)}):")
print(f'    """{func.docstring}"""')
print(f"    {func.body}")
```

<a id="pattern-6-batch-processing"></a>
### 模式 6：批量处理

```python
def batch_extract(texts: list[str], schema: type[BaseModel]):
    """Extract structured data from multiple texts."""
    model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
    generator = outlines.generate.json(model, schema)

    results = []
    for text in texts:
        result = generator(f"Extract from: {text}")
        results.append(result)

    return results

class Person(BaseModel):
    name: str
    age: int

texts = [
    "John is 30 years old",
    "Alice is 25 years old",
    "Bob is 40 years old"
]

people = batch_extract(texts, Person)
for person in people:
    print(f"{person.name}: {person.age}")
```

<a id="backend-configuration"></a>
## 后端配置

<a id="transformers"></a>
### Transformers

```python
import outlines

# Basic usage
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# GPU configuration
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda",
    model_kwargs={"torch_dtype": "float16"}
)

# Popular models
model = outlines.models.transformers("meta-llama/Llama-3.1-8B-Instruct")
model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.3")
model = outlines.models.transformers("Qwen/Qwen2.5-7B-Instruct")
```

<a id="llama-cpp"></a>
### llama.cpp

```python
# Load GGUF model
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b.Q4_K_M.gguf",
    n_ctx=4096,         # Context window
    n_gpu_layers=35,    # GPU layers
    n_threads=8         # CPU threads
)

# Full GPU offload
model = outlines.models.llamacpp(
    "./models/model.gguf",
    n_gpu_layers=-1  # All layers on GPU
)
```
<a id="vllm-production"></a>
### vLLM（生产环境）

```python
# 单 GPU
model = outlines.models.vllm("meta-llama/Llama-3.1-8B-Instruct")

# 多 GPU
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=4  # 4 块 GPU
)

# 带量化
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization="awq"  # 或 "gptq"
)
```

<a id="best-practices"></a>
## 最佳实践

<a id="1-use-specific-types"></a>
### 1. 使用具体类型

```python
# ✅ 好：具体类型
class Product(BaseModel):
    name: str
    price: float  # 不要用 str
    quantity: int  # 不要用 str
    in_stock: bool  # 不要用 str

# ❌ 差：全部用字符串
class Product(BaseModel):
    name: str
    price: str  # 应该是 float
    quantity: str  # 应该是 int
```

<a id="2-add-constraints"></a>
### 2. 添加约束

```python
from pydantic import Field

# ✅ 好：带约束
class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=120)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

# ❌ 差：无约束
class User(BaseModel):
    name: str
    age: int
    email: str
```

<a id="3-use-enums-for-categories"></a>
### 3. 使用枚举管理分类

```python
# ✅ 好：固定集合用枚举
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    title: str
    priority: Priority

# ❌ 差：自由字符串
class Task(BaseModel):
    title: str
    priority: str  # 可以是任意值
```

<a id="4-provide-context-in-prompts"></a>
### 4. 在提示词中提供上下文

```python
# ✅ 好：清晰的上下文
prompt = """
从以下文本中提取产品信息。
文本：iPhone 15 Pro 售价 999 美元，目前有货。
产品：
"""

# ❌ 差：上下文太少
prompt = "iPhone 15 Pro 售价 999 美元，目前有货。"
```

<a id="5-handle-optional-fields"></a>
### 5. 处理可选字段

```python
from typing import Optional

# ✅ 好：对不完整数据使用可选字段
class Article(BaseModel):
    title: str  # 必填
    author: Optional[str] = None  # 可选
    date: Optional[str] = None  # 可选
    tags: list[str] = []  # 默认空列表

# 即使缺少作者/日期也能成功
```

<a id="comparison-to-alternatives"></a>
## 与替代方案对比

| 特性 | Outlines | Instructor | Guidance | LMQL |
|------|----------|------------|----------|------|
| Pydantic 支持 | ✅ 原生 | ✅ 原生 | ❌ 否 | ❌ 否 |
| JSON Schema | ✅ 是 | ✅ 是 | ⚠️ 有限 | ✅ 是 |
| 正则约束 | ✅ 是 | ❌ 否 | ✅ 是 | ✅ 是 |
| 本地模型 | ✅ 完全 | ⚠️ 有限 | ✅ 完全 | ✅ 完全 |
| API 模型 | ⚠️ 有限 | ✅ 完全 | ✅ 完全 | ✅ 完全 |
| 零开销 | ✅ 是 | ❌ 否 | ⚠️ 部分 | ✅ 是 |
| 自动重试 | ❌ 否 | ✅ 是 | ❌ 否 | ❌ 否 |
| 学习曲线 | 低 | 低 | 低 | 高 |

**何时选择 Outlines：**
- 使用本地模型（Transformers、llama.cpp、vLLM）
- 需要最大推理速度
- 需要 Pydantic 模型支持
- 要求零开销的结构化生成
- 控制 token 采样过程

**何时选择替代方案：**
- Instructor：需要支持自动重试的 API 模型
- Guidance：需要 token 修复和复杂工作流
- LMQL：偏好声明式查询语法
<a id="performance-characteristics"></a>
## 性能特性

**速度：**
- **零开销**：结构化生成速度与无约束生成一样快
- **快进优化**：跳过确定性 token
- **比后生成验证方法快 1.2-2 倍**

**内存：**
- FSM 为每个 schema 编译一次（可缓存）
- 运行时开销极小
- 配合 vLLM 实现高吞吐量

**准确性：**
- **100% 有效输出**（由 FSM 保证）
- 无需重试循环
- 确定性 token 过滤

<a id="resources"></a>
## 资源

- **文档**：https://outlines-dev.github.io/outlines
- **GitHub**：https://github.com/outlines-dev/outlines（8k+ star）
- **Discord**：https://discord.gg/R9DSu34mGd
- **博客**：https://blog.dottxt.co

<a id="see-also"></a>
## 另请参阅

- `references/json_generation.md` - 完整的 JSON 和 Pydantic 模式
- `references/backends.md` - 后端特定配置
- `references/examples.md` - 生产就绪示例
