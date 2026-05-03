---
title: "Outlines — Outlines：结构化 JSON/regex/Pydantic LLM 生成"
sidebar_label: "Outlines"
description: "Outlines：结构化 JSON/regex/Pydantic LLM 生成"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Outlines {#outlines}

Outlines：结构化 JSON/regex/Pydantic LLM 生成。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/mlops/inference/outlines` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `outlines`, `transformers`, `vllm`, `pydantic` |
| 标签 | `Prompt Engineering`, `Outlines`, `Structured Generation`, `JSON Schema`, `Pydantic`, `Local Models`, `Grammar-Based Generation`, `vLLM`, `Transformers`, `Type Safety` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Outlines：结构化文本生成 {#outlines-structured-text-generation}

## 何时使用此技能 {#when-to-use-this-skill}

在以下场景中，你应该使用 Outlines：
- **保证生成过程中 JSON/XML/代码** 的结构正确
- **使用 Pydantic 模型** 实现类型安全的输出
- **支持本地模型**（Transformers、llama.cpp、vLLM）
- **最大化推理速度**，实现零开销的结构化生成
- **自动根据 JSON schema 生成**
- **在语法层面控制 token 采样**

**GitHub Stars**：8,000+ | **来自**：dottxt.ai（原 .txt）

## 安装 {#installation}

```bash
# 基础安装
pip install outlines

# 使用特定后端
pip install outlines transformers  # Hugging Face 模型
pip install outlines llama-cpp-python  # llama.cpp
pip install outlines vllm  # vLLM 高吞吐量
```

## 快速开始 {#quick-start}

### 基本示例：分类 {#basic-example-classification}

```python
import outlines
from typing import Literal

# 加载模型
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 使用类型约束生成
prompt = "情感分析：'这个产品太棒了！'："
generator = outlines.generate.choice(model, ["positive", "negative", "neutral"])
sentiment = generator(prompt)

print(sentiment)  # "positive"（保证是其中之一）
```

### 使用 Pydantic 模型 {#with-pydantic-models}

```python
from pydantic import BaseModel
import outlines

class User(BaseModel):
    name: str
    age: int
    email: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 生成结构化输出
prompt = "提取用户信息：John Doe，30岁，john@example.com"
generator = outlines.generate.json(model, User)
user = generator(prompt)

print(user.name)   # "John Doe"
print(user.age)    # 30
print(user.email)  # "john@example.com"
```

## 核心概念 {#core-concepts}

### 1. 受限 Token 采样 {#1-constrained-token-sampling}

Outlines 使用有限状态机（FSM）在 logit 层面约束 token 生成。

**工作原理：**
1. 将 schema（JSON/Pydantic/regex）转换为上下文无关文法（CFG）
2. 将 CFG 转换为有限状态机（FSM）
3. 在生成过程中每一步过滤无效 token
4. 当只有一个有效 token 时快速前进

**优势：**
- **零开销**：过滤在 token 级别进行
- **速度提升**：通过确定性路径快速前进
- **保证有效性**：不可能产生无效输出
```python
import outlines

# Pydantic 模型 → JSON 模式 → CFG → FSM
class Person(BaseModel):
    name: str
    age: int

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 幕后机制：
# 1. Person → JSON 模式
# 2. JSON 模式 → CFG
# 3. CFG → FSM
# 4. FSM 在生成时过滤 token

generator = outlines.generate.json(model, Person)
result = generator("Generate person: Alice, 25")
```

### 2. 结构化生成器 {#2-structured-generators}

Outlines 为不同的输出类型提供了专门的生成器。

#### 选择生成器 {#choice-generator}

```python
# 从多个候选中选择
generator = outlines.generate.choice(
    model,
    ["positive", "negative", "neutral"]
)

sentiment = generator("Review: This is great!")
# 结果：三个选项之一
```

#### JSON 生成器 {#json-generator}

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

# 生成符合模式的合法 JSON
generator = outlines.generate.json(model, Product)
product = generator("Extract: iPhone 15, $999, available")

# 保证返回合法的 Product 实例
print(type(product))  # <class '__main__.Product'>
```

#### 正则生成器 {#regex-generator}

```python
# 生成匹配正则表达式的文本
generator = outlines.generate.regex(
    model,
    r"[0-9]{3}-[0-9]{3}-[0-9]{4}"  # 电话号码格式
)

phone = generator("Generate phone number:")
# 结果："555-123-4567"（保证匹配模式）
```

#### 整数/浮点数生成器 {#integer-float-generators}

```python
# 生成特定数值类型
int_generator = outlines.generate.integer(model)
age = int_generator("Person's age:")  # 保证返回整数

float_generator = outlines.generate.float(model)
price = float_generator("Product price:")  # 保证返回浮点数
```

### 3. 模型后端 {#3-model-backends}

Outlines 支持多种本地和基于 API 的后端。

#### Transformers（Hugging Face） {#transformers-hugging-face}

```python
import outlines

# 从 Hugging Face 加载
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda"  # 或 "cpu"
)

# 与任何生成器配合使用
generator = outlines.generate.json(model, YourModel)
```

#### llama.cpp {#llama-cpp}

```python
# 加载 GGUF 模型
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35
)

generator = outlines.generate.json(model, YourModel)
```

#### vLLM（高吞吐量） {#vllm-high-throughput}

```python
# 用于生产部署
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=2  # 多 GPU
)

generator = outlines.generate.json(model, YourModel)
```

#### OpenAI（有限支持） {#openai-limited-support}

```python
# 基础的 OpenAI 支持
model = outlines.models.openai(
    "gpt-4o-mini",
    api_key="your-api-key"
)

# 注意：API 模型的某些功能有限
generator = outlines.generate.json(model, YourModel)
```

### 4. Pydantic 集成 {#4-pydantic-integration}

Outlines 对 Pydantic 提供了一流的支持，可以自动翻译模式。

#### 基础模型 {#basic-models}

```python
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="文章标题")
    author: str = Field(description="作者姓名")
    word_count: int = Field(description="字数", gt=0)
    tags: list[str] = Field(description="标签列表")

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, Article)

article = generator("Generate article about AI")
print(article.title)
print(article.word_count)  # 保证大于 0
```
#### 嵌套模型 {#nested-models}

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    age: int
    address: Address  # 嵌套模型

generator = outlines.generate.json(model, Person)
person = generator("生成一个在纽约的人")

print(person.address.city)  # "New York"
```

#### 枚举与字面量 {#enums-and-literals}

```python
from enum import Enum
from typing import Literal

class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Application(BaseModel):
    applicant: str
    status: Status  # 必须是枚举值之一
    priority: Literal["low", "medium", "high"]  # 必须是字面量之一

generator = outlines.generate.json(model, Application)
app = generator("生成一个申请")

print(app.status)  # Status.PENDING（或 APPROVED/REJECTED）
```

## 常见模式 {#common-patterns}

### 模式1：数据提取 {#pattern-1-data-extraction}

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
Apple Inc. 成立于1976年，属于科技行业。
该公司全球约有164,000名员工。
"""

prompt = f"提取公司信息：\n{text}\n\n公司："
company = generator(prompt)

print(f"名称：{company.name}")
print(f"成立年份：{company.founded_year}")
print(f"行业：{company.industry}")
print(f"员工数：{company.employees}")
```

### 模式2：分类 {#pattern-2-classification}

```python
from typing import Literal
import outlines

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 二分类
generator = outlines.generate.choice(model, ["spam", "not_spam"])
result = generator("邮件：立即购买！五折优惠！")

# 多分类
categories = ["technology", "business", "sports", "entertainment"]
category_gen = outlines.generate.choice(model, categories)
category = category_gen("文章：苹果发布新款iPhone……")

# 带置信度
class Classification(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    confidence: float

classifier = outlines.generate.json(model, Classification)
result = classifier("评价：这个产品还行，没什么特别的")
```

### 模式3：结构化表单 {#pattern-3-structured-forms}

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
从以下信息提取用户资料：
姓名：Alice Johnson
年龄：28
邮箱：alice@example.com
电话：555-0123
国家：美国
兴趣：徒步、摄影、烹饪
"""

profile = generator(prompt)
print(profile.full_name)
print(profile.interests)  # ["hiking", "photography", "cooking"]
```

### 模式4：多实体提取 {#pattern-4-multi-entity-extraction}
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

### 模式 5：代码生成 {#pattern-5-code-generation}

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

### 模式 6：批量处理 {#pattern-6-batch-processing}

```python
def batch_extract(texts: list[str], schema: type[BaseModel]):
    """从多个文本中提取结构化数据。"""
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

## 后端配置 {#backend-configuration}

### Transformers {#transformers}

```python
import outlines

# 基本用法
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# GPU 配置
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda",
    model_kwargs={"torch_dtype": "float16"}
)

# 常用模型
model = outlines.models.transformers("meta-llama/Llama-3.1-8B-Instruct")
model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.3")
model = outlines.models.transformers("Qwen/Qwen2.5-7B-Instruct")
```

### llama.cpp {#llama-cpp}

```python
# 加载 GGUF 模型
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b.Q4_K_M.gguf",
    n_ctx=4096,         # 上下文窗口
    n_gpu_layers=35,    # GPU 层数
    n_threads=8         # CPU 线程数
)

# 完全 GPU 卸载
model = outlines.models.llamacpp(
    "./models/model.gguf",
    n_gpu_layers=-1  # 所有层都在 GPU 上
)
```

### vLLM（生产环境） {#vllm-production}

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
## 最佳实践 {#best-practices}

### 1. 使用具体类型 {#1-use-specific-types}

```python
# ✅ Good: Specific types
class Product(BaseModel):
    name: str
    price: float  # Not str
    quantity: int  # Not str
    in_stock: bool  # Not str

# ❌ Bad: Everything as string
class Product(BaseModel):
    name: str
    price: str  # Should be float
    quantity: str  # Should be int
```

### 2. 添加约束 {#2-add-constraints}

```python
from pydantic import Field

# ✅ Good: With constraints
class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=120)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

# ❌ Bad: No constraints
class User(BaseModel):
    name: str
    age: int
    email: str
```

### 3. 对分类使用枚举 {#3-use-enums-for-categories}

```python
# ✅ Good: Enum for fixed set
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    title: str
    priority: Priority

# ❌ Bad: Free-form string
class Task(BaseModel):
    title: str
    priority: str  # Can be anything
```

### 4. 在提示词中提供上下文 {#4-provide-context-in-prompts}

```python
# ✅ Good: Clear context
prompt = """
Extract product information from the following text.
Text: iPhone 15 Pro costs $999 and is currently in stock.
Product:
"""

# ❌ Bad: Minimal context
prompt = "iPhone 15 Pro costs $999 and is currently in stock."
```

### 5. 处理可选字段 {#5-handle-optional-fields}

```python
from typing import Optional

# ✅ Good: Optional fields for incomplete data
class Article(BaseModel):
    title: str  # Required
    author: Optional[str] = None  # Optional
    date: Optional[str] = None  # Optional
    tags: list[str] = []  # Default empty list

# Can succeed even if author/date missing
```

## 与替代方案的对比 {#comparison-to-alternatives}

| 特性 | Outlines | Instructor | Guidance | LMQL |
|---------|----------|------------|----------|------|
| Pydantic 支持 | ✅ 原生 | ✅ 原生 | ❌ 否 | ❌ 否 |
| JSON Schema | ✅ 是 | ✅ 是 | ⚠️ 有限 | ✅ 是 |
| 正则约束 | ✅ 是 | ❌ 否 | ✅ 是 | ✅ 是 |
| 本地模型 | ✅ 完整 | ⚠️ 有限 | ✅ 完整 | ✅ 完整 |
| API 模型 | ⚠️ 有限 | ✅ 完整 | ✅ 完整 | ✅ 完整 |
| 零开销 | ✅ 是 | ❌ 否 | ⚠️ 部分 | ✅ 是 |
| 自动重试 | ❌ 否 | ✅ 是 | ❌ 否 | ❌ 否 |
| 学习曲线 | 低 | 低 | 低 | 高 |

**何时选择 Outlines：**
- 使用本地模型（Transformers、llama.cpp、vLLM）
- 需要最大推理速度
- 希望支持 Pydantic 模型
- 需要零开销的结构化生成
- 控制 token 采样过程

**何时选择替代方案：**
- Instructor：需要 API 模型并支持自动重试
- Guidance：需要 token 修复和复杂工作流
- LMQL：偏好声明式查询语法

## 性能特征 {#performance-characteristics}

**速度：**
- **零开销**：结构化生成与无约束生成一样快
- **快速前向优化**：跳过确定性 token
- 比生成后验证方法**快 1.2-2 倍**

**内存：**
- FSM 每个 schema 编译一次（缓存）
- 运行时开销极小
- 与 vLLM 配合实现高吞吐量
**准确性：**
- **100% 有效输出**（由 FSM 保证）
- 无需重试循环
- 确定性令牌过滤

## 资源 {#resources}

- **文档**：https://outlines-dev.github.io/outlines
- **GitHub**：https://github.com/outlines-dev/outlines（8000+ 星标）
- **Discord**：https://discord.gg/R9DSu34mGd
- **博客**：https://blog.dottxt.co

## 另请参阅 {#see-also}

- `references/json_generation.md` - 全面的 JSON 和 Pydantic 模式
- `references/backends.md` - 后端特定配置
- `references/examples.md` - 生产就绪示例
