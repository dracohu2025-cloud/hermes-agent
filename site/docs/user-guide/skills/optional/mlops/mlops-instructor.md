---
title: "Instructor"
sidebar_label: "Instructor"
description: "使用 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，安全地解析复杂 JSON，并通过 Instructor（久经考验的结构化输出库）流式传输部分结果。"
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Instructor {#instructor}

使用 Pydantic 验证从 LLM 响应中提取结构化数据，自动重试失败的提取，安全地解析复杂 JSON，并通过 Instructor（久经考验的结构化输出库）流式传输部分结果。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/instructor` 安装 |
| 路径 | `optional-skills/mlops/instructor` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `instructor`, `pydantic`, `openai`, `anthropic` |
| 标签 | `Prompt Engineering`, `Instructor`, `Structured Output`, `Pydantic`, `Data Extraction`, `JSON Parsing`, `Type Safety`, `Validation`, `Streaming`, `OpenAI`, `Anthropic` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# Instructor：结构化 LLM 输出 {#instructor-structured-llm-outputs}

## 何时使用此技能 {#when-to-use-this-skill}

在以下场景使用 Instructor：
- **可靠地从 LLM 响应中提取结构化数据**
- **根据 Pydantic 模式自动验证输出**
- **自动重试失败的提取**，并带有错误处理
- **安全地解析复杂 JSON**，具备类型安全和验证
- **流式传输部分结果**，用于实时处理
- **支持多个 LLM 提供商**，API 保持一致

**GitHub Stars**：15,000+ | **久经考验**：100,000+ 开发者

## 安装 {#installation}

```bash
# 基础安装
pip install instructor

# 使用特定提供商
pip install "instructor[anthropic]"  # Anthropic Claude
pip install "instructor[openai]"     # OpenAI
pip install "instructor[all]"        # 所有提供商
```

## 快速开始 {#quick-start}

### 基本示例：提取用户数据 {#basic-example-extract-user-data}

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

### 使用 OpenAI {#with-openai}

```python
from openai import OpenAI

client = instructor.from_openai(OpenAI())

user = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=User,
    messages=[{"role": "user", "content": "Extract: Alice, 25, alice@email.com"}]
)
```

## 核心概念 {#core-concepts}

### 1. 响应模型（Pydantic） {#1-response-models-pydantic}

响应模型定义了 LLM 输出的结构和验证规则。

#### 基本模型 {#basic-model}

```python
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="文章标题")
    author: str = Field(description="作者姓名")
    word_count: int = Field(description="字数", gt=0)
    tags: list[str] = Field(description="相关标签列表")

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
**好处：**
- 通过 Python 类型提示实现类型安全
- 自动验证（`word_count > 0`）
- 借助 Field 描述实现自文档化
- IDE 自动补全支持

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

#### 可选字段 {#optional-fields}

```python
from typing import Optional

class Product(BaseModel):
    name: str
    price: float
    discount: Optional[float] = None  # 可选字段
    description: str = Field(default="No description")  # 默认值

# 大模型无需提供 discount 或 description
```

#### 使用枚举限定取值 {#enums-for-constraints}

```python
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Review(BaseModel):
    text: str
    sentiment: Sentiment  # 仅允许这 3 个值

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

### 2. 验证 {#2-validation}

Pydantic 会自动验证大模型输出。如果验证失败，Instructor 会自动重试。

#### 内置验证器 {#built-in-validators}

```python
from pydantic import Field, EmailStr, HttpUrl

class Contact(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=120)  # 0 <= age <= 120
    email: EmailStr  # 验证邮箱格式
    website: HttpUrl  # 验证 URL 格式

# 如果大模型提供了无效数据，Instructor 会自动重试
```

#### 自定义验证器 {#custom-validators}

```python
from pydantic import field_validator

class Event(BaseModel):
    name: str
    date: str
    attendees: int

    @field_validator('date')
    def validate_date(cls, v):
        """确保日期格式为 YYYY-MM-DD"""
        import re
        if not re.match(r'\d{4}-\d{2}-\d{2}', v):
            raise ValueError('日期必须为 YYYY-MM-DD 格式')
        return v

    @field_validator('attendees')
    def validate_attendees(cls, v):
        """确保参会人数为正数"""
        if v < 1:
            raise ValueError('参会人数至少为 1')
        return v
```

#### 模型级别验证 {#model-level-validation}

```python
from pydantic import model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode='after')
    def check_dates(self):
        """确保 end_date 在 start_date 之后"""
        from datetime import datetime
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')

        if end < start:
            raise ValueError('end_date 必须在 start_date 之后')
        return self
```
### 3. 自动重试 {#3-automatic-retrying}

当验证失败时，Instructor 会自动重试，并向 LLM 提供错误反馈。

```python
# 如果验证失败，最多重试 3 次
user = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Extract user from: John, age unknown"
    }],
    response_model=User,
    max_retries=3  # 默认值为 3
)

# 如果无法提取年龄，Instructor 会告诉 LLM：
# "Validation error: age - field required"
# LLM 会带着错误反馈再次尝试提取
```

**工作原理：**
1. LLM 生成输出
2. Pydantic 进行验证
3. 如果无效：将错误信息发送回 LLM
4. LLM 根据错误反馈再次尝试
5. 重复直到达到 max_retries 上限

### 4. 流式处理 {#4-streaming}

流式输出部分结果，实现实时处理。

#### 流式输出部分对象 {#streaming-partial-objects}

```python
from instructor import Partial

class Story(BaseModel):
    title: str
    content: str
    tags: list[str]

# 随着 LLM 生成，流式输出部分更新
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
    # 实时更新 UI
```

#### 流式输出可迭代对象 {#streaming-iterables}

```python
class Task(BaseModel):
    title: str
    priority: str

# 随着生成，流式输出列表项
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
    # 每项到达时立即处理
```

## 提供商配置 {#provider-configuration}

### Anthropic Claude {#anthropic-claude}

```python
import instructor
from anthropic import Anthropic

client = instructor.from_anthropic(
    Anthropic(api_key="your-api-key")
)

# 与 Claude 模型一起使用
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[...],
    response_model=YourModel
)
```

### OpenAI {#openai}

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

### 本地模型（Ollama） {#local-models-ollama}

```python
from openai import OpenAI

# 指向本地 Ollama 服务器
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"  # 必填但会被忽略
    ),
    mode=instructor.Mode.JSON
)

response = client.chat.completions.create(
    model="llama3.1",
    response_model=YourModel,
    messages=[...]
)
```

## 常见模式 {#common-patterns}

### 模式 1：从文本中提取数据 {#pattern-1-data-extraction-from-text}

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
### 模式 2：分类 {#pattern-2-classification}

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

### 模式 3：多实体提取 {#pattern-3-multi-entity-extraction}

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

### 模式 4：结构化分析 {#pattern-4-structured-analysis}

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

### 模式 5：批量处理 {#pattern-5-batch-processing}

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

## 高级特性 {#advanced-features}

### 联合类型 {#union-types}

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
    content: Union[TextContent, ImageContent]  # Either type

# LLM chooses appropriate type based on content
```

### 动态模型 {#dynamic-models}

```python
from pydantic import create_model

# Create model at runtime
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
### 自定义模式 {#custom-modes}

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

### 上下文管理 {#context-management}

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

## 错误处理 {#error-handling}

### 处理验证错误 {#handling-validation-errors}

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
    print(f"重试后仍失败: {e}")
    # 优雅处理

except Exception as e:
    print(f"API 错误: {e}")
```

### 自定义错误消息 {#custom-error-messages}

```python
class ValidatedUser(BaseModel):
    name: str = Field(description="全名，2-100 个字符")
    age: int = Field(description="年龄，0 到 120 之间", ge=0, le=120)
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

## 最佳实践 {#best-practices}

### 1. 清晰的字段描述 {#1-clear-field-descriptions}

```python
# ❌ 不好：模糊
class Product(BaseModel):
    name: str
    price: float

# ✅ 好：描述清晰
class Product(BaseModel):
    name: str = Field(description="文本中的产品名称")
    price: float = Field(description="价格（美元，不含货币符号）")
```

### 2. 使用合适的验证 {#2-use-appropriate-validation}

```python
# ✅ 好：约束值范围
class Rating(BaseModel):
    score: int = Field(ge=1, le=5, description="1 到 5 星的评分")
    review: str = Field(min_length=10, description="评价文本，至少 10 个字符")
```

### 3. 在提示中提供示例 {#3-provide-examples-in-prompts}

```python
messages = [{
    "role": "user",
    "content": """从以下内容提取人员信息："张三，30岁，工程师"

示例格式：
{
  "name": "张三",
  "age": 30,
  "occupation": "工程师"
}"""
}]
```

### 4. 对固定类别使用枚举 {#4-use-enums-for-fixed-categories}

```python
# ✅ 好：枚举确保有效值
class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Application(BaseModel):
    status: Status  # LLM 必须从枚举中选择
```

### 5. 优雅处理缺失数据 {#5-handle-missing-data-gracefully}

```python
class PartialData(BaseModel):
    required_field: str
    optional_field: Optional[str] = None
    default_field: str = "default_value"

# LLM 只需要提供 required_field
```

## 与替代方案的对比 {#comparison-to-alternatives}

| 特性 | Instructor | 手动 JSON | LangChain | DSPy |
|---------|------------|-------------|-----------|------|
| 类型安全 | ✅ 是 | ❌ 否 | ⚠️ 部分 | ✅ 是 |
| 自动验证 | ✅ 是 | ❌ 否 | ❌ 否 | ⚠️ 有限 |
| 自动重试 | ✅ 是 | ❌ 否 | ❌ 否 | ✅ 是 |
| 流式输出 | ✅ 是 | ❌ 否 | ✅ 是 | ❌ 否 |
| 多提供商 | ✅ 是 | ⚠️ 手动 | ✅ 是 | ✅ 是 |
| 学习曲线 | 低 | 低 | 中 | 高 |
**何时选择 Instructor：**
- 需要结构化、可验证的输出
- 想要类型安全与 IDE 支持
- 需要自动重试机制
- 构建数据提取系统

**何时选择其他方案：**
- DSPy：需要提示词优化
- LangChain：构建复杂链式流程
- 手动方式：简单、一次性提取

## 资源 {#resources}

- **文档**：https://python.useinstructor.com
- **GitHub**：https://github.com/jxnl/instructor（15k+ 星标）
- **示例手册**：https://python.useinstructor.com/examples
- **Discord**：提供社区支持

## 参见 {#see-also}

- `references/validation.md` - 高级验证模式
- `references/providers.md` - 特定提供商的配置
- `references/examples.md` - 真实使用案例
