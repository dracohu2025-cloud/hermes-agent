---
title: "Instructor"
sidebar_label: "Instructor"
description: "从 LLM 响应中提取结构化数据，提供 Pydantic 验证、自动重试失败提取、类型安全解析复杂 JSON，以及流式传输部分结果。"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="instructor"></a>
# Instructor

从 LLM 响应中提取结构化数据，提供 Pydantic 验证、自动重试失败提取、类型安全解析复杂 JSON，以及流式传输部分结果 —— 使用久经考验的结构化输出库 Instructor。

<a id="skill-metadata"></a>
## Skill metadata

| | |
|---|---|
| Source | 可选 — 安装命令：`hermes skills install official/mlops/instructor` |
| Path | `optional-skills/mlops/instructor` |
| Version | `1.0.0` |
| Author | Orchestra Research |
| License | MIT |
| Dependencies | `instructor`, `pydantic`, `openai`, `anthropic` |
| Platforms | linux, macos, windows |
| Tags | `Prompt Engineering`, `Instructor`, `Structured Output`, `Pydantic`, `Data Extraction`, `JSON Parsing`, `Type Safety`, `Validation`, `Streaming`, `OpenAI`, `Anthropic` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在该技能触发时加载的完整技能定义。这就是技能激活时 Agent 看到的指令。
:::

<a id="instructor-structured-llm-outputs"></a>
# Instructor：结构化 LLM 输出

<a id="when-to-use-this-skill"></a>
## 何时使用该技能

当您需要以下功能时，请使用 Instructor：
- **从 LLM 响应中可靠地提取结构化数据**
- **根据 Pydantic 模式自动验证输出**
- **通过自动错误处理重试失败的提取**
- **以类型安全的方式解析复杂 JSON**
- **流式传输部分结果以实现实时处理**
- **支持多个 LLM 提供商，API 保持一致**

**GitHub Stars**: 15,000+ | **久经考验**：100,000 多名开发者

<a id="installation"></a>
## 安装

```bash
# 基础安装
pip install instructor

# 搭配特定提供商安装
pip install "instructor[anthropic]"  # Anthropic Claude
pip install "instructor[openai]"     # OpenAI
pip install "instructor[all]"        # 所有提供商
```

<a id="quick-start"></a>
## 快速开始

<a id="basic-example-extract-user-data"></a>
### 基本示例：提取用户数据

```python
import instructor
from pydantic import BaseModel
from anthropic import Anthropic

# 定义输出结构
class User(BaseModel):
    name: str
    age: int
    email: str

# 创建 instructor 客户端
client = instructor.from_anthropic(Anthropic())

# 提取结构化数据
user = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "John Doe is 30 years old. His email is john@example.com"
    }],
    response_model=User
)

print(user.name)   # "John Doe"
print(user.age)    # 30
print(user.email)  # "john@example.com"
```

<a id="with-openai"></a>
### 搭配 OpenAI 使用

```python
from openai import OpenAI

client = instructor.from_openai(OpenAI())

user = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=User,
    messages=[{"role": "user", "content": "Extract: Alice, 25, alice@email.com"}]
)
```

<a id="core-concepts"></a>
## 核心概念

<a id="1-response-models-pydantic"></a>
### 1. 响应模型（Pydantic）

响应模型定义了 LLM 输出的结构和验证规则。

<a id="basic-model"></a>
#### 基本模型
```python
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="Article title")
    author: str = Field(description="Author name")
    word_count: int = Field(description="Number of words", gt=0)
    tags: list[str] = Field(description="List of relevant tags")

article = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Analyze this article: [article text]"
    }],
    response_model=Article
)
```

**优势：**
- 借助 Python 类型提示获得类型安全
- 自动校验（word_count > 0）
- 通过 Field 描述实现自文档化
- IDE 自动补全支持

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

person = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "John lives at 123 Main St, Boston, USA"
    }],
    response_model=Person
)

print(person.address.city)  # "Boston"
```

<a id="optional-fields"></a>
#### 可选字段

```python
from typing import Optional

class Product(BaseModel):
    name: str
    price: float
    discount: Optional[float] = None  # Optional
    description: str = Field(default="No description")  # Default value

# LLM doesn't need to provide discount or description
```

<a id="enums-for-constraints"></a>
#### 枚举约束

```python
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Review(BaseModel):
    text: str
    sentiment: Sentiment  # Only these 3 values allowed

review = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "This product is amazing!"
    }],
    response_model=Review
)

print(review.sentiment)  # Sentiment.POSITIVE
```

<a id="2-validation"></a>
### 2. 校验

Pydantic 会自动校验 LLM 的输出。如果校验失败，Instructor 会重试。

<a id="built-in-validators"></a>
#### 内置校验器

```python
from pydantic import Field, EmailStr, HttpUrl

class Contact(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=120)  # 0 <= age <= 120
    email: EmailStr  # Validates email format
    website: HttpUrl  # Validates URL format

# If LLM provides invalid data, Instructor retries automatically
```

<a id="custom-validators"></a>
#### 自定义校验器

```python
from pydantic import field_validator

class Event(BaseModel):
    name: str
    date: str
    attendees: int

    @field_validator('date')
    def validate_date(cls, v):
        """Ensure date is in YYYY-MM-DD format."""
        import re
        if not re.match(r'\d{4}-\d{2}-\d{2}', v):
            raise ValueError('Date must be YYYY-MM-DD format')
        return v

    @field_validator('attendees')
    def validate_attendees(cls, v):
        """Ensure positive attendees."""
        if v < 1:
            raise ValueError('Must have at least 1 attendee')
        return v
```
<a id="model-level-validation"></a>
#### 模型级别验证

```python
from pydantic import model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode='after')
    def check_dates(self):
        """Ensure end_date is after start_date."""
        from datetime import datetime
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')

        if end < start:
            raise ValueError('end_date must be after start_date')
        return self
```

<a id="3-automatic-retrying"></a>
### 3. 自动重试

当验证失败时，Instructor 会自动重试，并向 LLM 提供错误反馈。

```python
# Retries up to 3 times if validation fails
user = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Extract user from: John, age unknown"
    }],
    response_model=User,
    max_retries=3  # Default is 3
)

# If age can't be extracted, Instructor tells the LLM:
# "Validation error: age - field required"
# LLM tries again with better extraction
```

**工作原理：**
1. LLM 生成输出
2. Pydantic 进行验证
3. 如果无效：将错误信息发送回 LLM
4. LLM 根据错误反馈重新尝试
5. 重复直到达到 max_retries

<a id="4-streaming"></a>
### 4. 流式处理

流式输出部分结果，用于实时处理。

<a id="streaming-partial-objects"></a>
#### 流式输出部分对象

```python
from instructor import Partial

class Story(BaseModel):
    title: str
    content: str
    tags: list[str]

# Stream partial updates as LLM generates
for partial_story in client.messages.create_partial(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Write a short sci-fi story"
    }],
    response_model=Story
):
    print(f"Title: {partial_story.title}")
    print(f"Content so far: {partial_story.content[:100]}...")
    # Update UI in real-time
```

<a id="streaming-iterables"></a>
#### 流式输出可迭代对象

```python
class Task(BaseModel):
    title: str
    priority: str

# Stream list items as they're generated
tasks = client.messages.create_iterable(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Generate 10 project tasks"
    }],
    response_model=Task
)

for task in tasks:
    print(f"- {task.title} ({task.priority})")
    # Process each task as it arrives
```

<a id="provider-configuration"></a>
## 提供者配置

<a id="anthropic-claude"></a>
### Anthropic Claude

```python
import instructor
from anthropic import Anthropic

client = instructor.from_anthropic(
    Anthropic(api_key="your-api-key")
)

# Use with Claude models
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[...],
    response_model=YourModel
)
```

<a id="openai"></a>
### OpenAI

```python
from openai import OpenAI

client = instructor.from_openai(
    OpenAI(api_key="your-api-key")
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=YourModel,
    messages=[...]
)
```
<a id="local-models-ollama"></a>
### 本地模型 (Ollama)

```python
from openai import OpenAI

# Point to local Ollama server
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"  # Required but ignored
    ),
    mode=instructor.Mode.JSON
)

response = client.chat.completions.create(
    model="llama3.1",
    response_model=YourModel,
    messages=[...]
)
```

<a id="common-patterns"></a>
## 常见模式

<a id="pattern-1-data-extraction-from-text"></a>
### 模式一：从文本中提取数据

```python
class CompanyInfo(BaseModel):
    name: str
    founded_year: int
    industry: str
    employees: int
    headquarters: str

text = """
Tesla, Inc. was founded in 2003. It operates in the automotive and energy
industry with approximately 140,000 employees. The company is headquartered
in Austin, Texas.
"""

company = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Extract company information from: {text}"
    }],
    response_model=CompanyInfo
)
```

<a id="pattern-2-classification"></a>
### 模式二：分类

```python
class Category(str, Enum):
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    OTHER = "other"

class ArticleClassification(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    keywords: list[str]

classification = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Classify this article: [article text]"
    }],
    response_model=ArticleClassification
)
```

<a id="pattern-3-multi-entity-extraction"></a>
### 模式三：多实体提取

```python
class Person(BaseModel):
    name: str
    role: str

class Organization(BaseModel):
    name: str
    industry: str

class Entities(BaseModel):
    people: list[Person]
    organizations: list[Organization]
    locations: list[str]

text = "Tim Cook, CEO of Apple, announced at the event in Cupertino..."

entities = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Extract all entities from: {text}"
    }],
    response_model=Entities
)

for person in entities.people:
    print(f"{person.name} - {person.role}")
```

<a id="pattern-4-structured-analysis"></a>
### 模式四：结构化分析

```python
class SentimentAnalysis(BaseModel):
    overall_sentiment: Sentiment
    positive_aspects: list[str]
    negative_aspects: list[str]
    suggestions: list[str]
    score: float = Field(ge=-1.0, le=1.0)

review = "The product works well but setup was confusing..."

analysis = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Analyze this review: {review}"
    }],
    response_model=SentimentAnalysis
)
```

<a id="pattern-5-batch-processing"></a>
### 模式五：批量处理

```python
def extract_person(text: str) -> Person:
    return client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Extract person from: {text}"
        }],
        response_model=Person
    )

texts = [
    "John Doe is a 30-year-old engineer",
    "Jane Smith, 25, works in marketing",
    "Bob Johnson, age 40, software developer"
]

people = [extract_person(text) for text in texts]
```
<a id="advanced-features"></a>
## 高级功能

<a id="union-types"></a>
### 联合类型

```python
from typing import Union

class TextContent(BaseModel):
    type: str = "text"
    content: str

class ImageContent(BaseModel):
    type: str = "image"
    url: HttpUrl
    caption: str

class Post(BaseModel):
    title: str
    content: Union[TextContent, ImageContent]  # 两种类型均可

# LLM 会根据内容自动选择合适的类型
```

<a id="dynamic-models"></a>
### 动态模型

```python
from pydantic import create_model

# 在运行时创建模型
DynamicUser = create_model(
    'User',
    name=(str, ...),
    age=(int, Field(ge=0)),
    email=(EmailStr, ...)
)

user = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[...],
    response_model=DynamicUser
)
```

<a id="custom-modes"></a>
### 自定义模式

```python
# 对于不支持原生结构化输出的提供商
client = instructor.from_anthropic(
    Anthropic(),
    mode=instructor.Mode.JSON  # JSON 模式
)

# 可用模式：
# - Mode.ANTHROPIC_TOOLS（推荐用于 Claude）
# - Mode.JSON（回退方案）
# - Mode.TOOLS（OpenAI 工具）
```

<a id="context-management"></a>
### 上下文管理

```python
# 单次使用客户端
with instructor.from_anthropic(Anthropic()) as client:
    result = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[...],
        response_model=YourModel
    )
    # 客户端自动关闭
```

<a id="error-handling"></a>
## 错误处理

<a id="handling-validation-errors"></a>
### 处理验证错误

```python
from pydantic import ValidationError

try:
    user = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[...],
        response_model=User,
        max_retries=3
    )
except ValidationError as e:
    print(f"重试后仍然失败：{e}")
    # 优雅处理

except Exception as e:
    print(f"API 错误：{e}")
```

<a id="custom-error-messages"></a>
### 自定义错误消息

```python
class ValidatedUser(BaseModel):
    name: str = Field(description="全名，2-100 个字符")
    age: int = Field(description="年龄在 0 到 120 之间", ge=0, le=120)
    email: EmailStr = Field(description="有效的电子邮件地址")

    class Config:
        # 自定义错误消息
        json_schema_extra = {
            "examples": [
                {
                    "name": "张三",
                    "age": 30,
                    "email": "zhangsan@example.com"
                }
            ]
        }
```

<a id="best-practices"></a>
## 最佳实践

<a id="1-clear-field-descriptions"></a>
### 1. 清晰的字段描述

```python
# ❌ 不好：描述模糊
class Product(BaseModel):
    name: str
    price: float

# ✅ 好：描述清晰
class Product(BaseModel):
    name: str = Field(description="从文本中提取的产品名称")
    price: float = Field(description="美元价格，不含货币符号")
```

<a id="2-use-appropriate-validation"></a>
### 2. 使用合适的验证

```python
# ✅ 好：约束值范围
class Rating(BaseModel):
    score: int = Field(ge=1, le=5, description="1 到 5 星的评分")
    review: str = Field(min_length=10, description="评论内容，至少 10 个字符")
```

<a id="3-provide-examples-in-prompts"></a>
### 3. 在提示词中提供示例

```python
messages = [{
    "role": "user",
    "content": """从以下内容中提取个人信息："张三，30岁，工程师"

示例格式：
{
  "name": "张三",
  "age": 30,
  "occupation": "工程师"
}"""
}]
```
<a id="4-use-enums-for-fixed-categories"></a>
### 4. 使用枚举定义固定类别

```python
# ✅ Good: Enum ensures valid values
class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Application(BaseModel):
    status: Status  # LLM must choose from enum
```

<a id="5-handle-missing-data-gracefully"></a>
### 5. 优雅处理缺失数据

```python
class PartialData(BaseModel):
    required_field: str
    optional_field: Optional[str] = None
    default_field: str = "default_value"

# LLM only needs to provide required_field
```

<a id="comparison-to-alternatives"></a>
## 与其他方案对比

| 特性 | Instructor | 手动 JSON | LangChain | DSPy |
|---------|------------|-------------|-----------|------|
| 类型安全 | ✅ 是 | ❌ 否 | ⚠️ 部分支持 | ✅ 是 |
| 自动验证 | ✅ 是 | ❌ 否 | ❌ 否 | ⚠️ 有限 |
| 自动重试 | ✅ 是 | ❌ 否 | ❌ 否 | ✅ 是 |
| 流式输出 | ✅ 是 | ❌ 否 | ✅ 是 | ❌ 否 |
| 多提供商支持 | ✅ 是 | ⚠️ 手动 | ✅ 是 | ✅ 是 |
| 学习曲线 | 低 | 低 | 中等 | 高 |

**何时选择 Instructor：**
- 需要结构化、经过验证的输出
- 希望获得类型安全和 IDE 支持
- 需要自动重试
- 构建数据提取系统

**何时选择其他方案：**
- DSPy：需要提示优化
- LangChain：构建复杂链式操作
- 手动：简单、一次性的提取

<a id="resources"></a>
## 资源

- **文档**：https://python.useinstructor.com
- **GitHub**：https://github.com/jxnl/instructor（15k+ Star）
- **示例手册**：https://python.useinstructor.com/examples
- **Discord**：提供社区支持

<a id="see-also"></a>
## 相关参考

- `references/validation.md` - 高级验证模式
- `references/providers.md` - 特定提供商的配置
- `references/examples.md` - 真实世界用例
