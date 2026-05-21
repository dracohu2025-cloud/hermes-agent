---
title: "Guidance"
sidebar_label: "Guidance"
description: "使用正则表达式和语法控制 LLM 输出，保证生成有效的 JSON/XML/代码，强制结构化格式，并借助 Microsoft Research 的受限生成框架 Guidance 构建多步工作流。"
---

{/* 此页面由网站/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="guidance"></a>
# Guidance

使用正则表达式和语法控制 LLM 输出，保证生成有效的 JSON/XML/代码，强制结构化格式，并借助 Microsoft Research 的受限生成框架 Guidance 构建多步工作流。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 用 `hermes skills install official/mlops/guidance` 安装 |
| 路径 | `optional-skills/mlops/guidance` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖 | `guidance`, `transformers` |
| 平台 | linux, macos, windows |
| 标签 | `提示工程`, `Guidance`, `受限生成`, `结构化输出`, `JSON 验证`, `语法`, `Microsoft Research`, `格式强制`, `多步工作流` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

<a id="guidance-constrained-llm-generation"></a>
# Guidance：受限的 LLM 生成

<a id="when-to-use-this-skill"></a>
## 何时使用此技能

在以下场景使用 Guidance：
- **通过正则表达式或语法控制 LLM 输出语法**
- **保证生成有效的 JSON/XML/代码**
- **相比传统提示方法降低延迟**
- **强制结构化格式**（日期、电子邮件、ID 等）
- **使用 Python 风格的控制流构建多步工作流**
- **通过语法约束防止无效输出**

**GitHub 星标**: 18,000+ | **来自**: Microsoft Research

<a id="installation"></a>
## 安装

```bash
# 基础安装
pip install guidance

# 使用特定后端
pip install guidance[transformers]  # Hugging Face 模型
pip install guidance[llama_cpp]     # llama.cpp 模型
```

<a id="quick-start"></a>
## 快速开始

<a id="basic-example-structured-generation"></a>
### 基础示例：结构化生成

```python
from guidance import models, gen

# Load model (supports OpenAI, Transformers, llama.cpp)
lm = models.OpenAI("gpt-4")

# Generate with constraints
result = lm + "The capital of France is " + gen("capital", max_tokens=5)

print(result["capital"])  # "Paris"
```

<a id="with-anthropic-claude"></a>
### 使用 Anthropic Claude

```python
from guidance import models, gen, system, user, assistant

# Configure Claude
lm = models.Anthropic("claude-sonnet-4-5-20250929")

# Use context managers for chat format
with system():
    lm += "You are a helpful assistant."

with user():
    lm += "What is the capital of France?"

with assistant():
    lm += gen(max_tokens=20)
```

<a id="core-concepts"></a>
## 核心概念

<a id="1-context-managers"></a>
### 1. 上下文管理器

Guidance 使用 Python 风格的上下文管理器实现聊天式交互。

```python
from guidance import system, user, assistant, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# System message
with system():
    lm += "You are a JSON generation expert."

# User message
with user():
    lm += "Generate a person object with name and age."

# Assistant response
with assistant():
    lm += gen("response", max_tokens=100)

print(lm["response"])
```
**好处：**
- 自然的对话流程
- 清晰的角色分离
- 易于阅读和维护

<a id="2-constrained-generation"></a>
### 2. 约束生成（Constrained Generation）

Guidance 通过正则表达式或语法确保输出匹配指定的模式。

<a id="regex-constraints"></a>
#### 正则约束

```python
from guidance import models, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 约束为有效的电子邮件格式
lm += "Email: " + gen("email", regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# 约束为日期格式（YYYY-MM-DD）
lm += "Date: " + gen("date", regex=r"\d{4}-\d{2}-\d{2}")

# 约束为电话号码
lm += "Phone: " + gen("phone", regex=r"\d{3}-\d{3}-\d{4}")

print(lm["email"])  # 一定是有效的电子邮件
print(lm["date"])   # 一定是 YYYY-MM-DD 格式
```

**工作原理：**
- 正则表达式在词元级别转换为语法
- 生成过程中过滤掉无效词元
- 模型只能产生符合规则的输出

<a id="selection-constraints"></a>
#### 选择约束

```python
from guidance import models, gen, select

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 约束为特定选项
lm += "Sentiment: " + select(["positive", "negative", "neutral"], name="sentiment")

# 多项选择
lm += "Best answer: " + select(
    ["A) Paris", "B) London", "C) Berlin", "D) Madrid"],
    name="answer"
)

print(lm["sentiment"])  # 其中之一：positive, negative, neutral
print(lm["answer"])     # 其中之一：A, B, C 或 D
```

<a id="3-token-healing"></a>
### 3. 词元修复（Token Healing）

Guidance 自动“修复”提示词与生成内容之间的词元边界。

**问题：** 分词会创建不自然的边界。

```python
# 没有词元修复的情况
prompt = "The capital of France is "
# 最后一个词元：" is "
# 第一个生成的词元可能是 " Par"（带前导空格）
# 结果："The capital of France is  Paris"（两个空格！）
```

**解决方案：** Guidance 回退一个词元并重新生成。

```python
from guidance import models, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 默认启用词元修复
lm += "The capital of France is " + gen("capital", max_tokens=5)
# 结果："The capital of France is Paris"（正确的空格）
```

**好处：**
- 自然的文本边界
- 没有尴尬的空格问题
- 更好的模型表现（模型看到自然的词元序列）

<a id="4-grammar-based-generation"></a>
### 4. 基于语法的生成

使用上下文无关语法定义复杂结构。

```python
from guidance import models, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# JSON 语法（简化版）
json_grammar = """
{
    "name": <gen name regex="[A-Za-z ]+" max_tokens=20>,
    "age": <gen age regex="[0-9]+" max_tokens=3>,
    "email": <gen email regex="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}" max_tokens=50>
}
"""

# 生成有效的 JSON
lm += gen("person", grammar=json_grammar)

print(lm["person"])  # 一定是有效的 JSON 结构
```

**使用场景：**
- 复杂的结构化输出
- 嵌套数据结构
- 编程语言语法
- 领域特定语言

<a id="5-guidance-functions"></a>
### 5. Guidance 函数

使用 `@guidance` 装饰器创建可复用的生成模式。

```python
from guidance import guidance, gen, models

@guidance
def generate_person(lm):
    """生成带姓名和年龄的人物信息。"""
    lm += "Name: " + gen("name", max_tokens=20, stop="\n")
    lm += "\nAge: " + gen("age", regex=r"[0-9]+", max_tokens=3)
    return lm

# 使用函数
lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = generate_person(lm)

print(lm["name"])
print(lm["age"])
```
**有状态函数：**

```python
@guidance(stateless=False)
def react_agent(lm, question, tools, max_rounds=5):
    """ReAct agent with tool use."""
    lm += f"Question: {question}\n\n"

    for i in range(max_rounds):
        # Thought
        lm += f"Thought {i+1}: " + gen("thought", stop="\n")

        # Action
        lm += "\nAction: " + select(list(tools.keys()), name="action")

        # Execute tool
        tool_result = tools[lm["action"]]()
        lm += f"\nObservation: {tool_result}\n\n"

        # Check if done
        lm += "Done? " + select(["Yes", "No"], name="done")
        if lm["done"] == "Yes":
            break

    # Final answer
    lm += "\nFinal Answer: " + gen("answer", max_tokens=100)
    return lm
```

<a id="backend-configuration"></a>
## 后端配置

<a id="anthropic-claude"></a>
### Anthropic Claude

```python
from guidance import models

lm = models.Anthropic(
    model="claude-sonnet-4-5-20250929",
    api_key="your-api-key"  # Or set ANTHROPIC_API_KEY env var
)
```

<a id="openai"></a>
### OpenAI

```python
lm = models.OpenAI(
    model="gpt-4o-mini",
    api_key="your-api-key"  # Or set OPENAI_API_KEY env var
)
```

<a id="local-models-transformers"></a>
### 本地模型（Transformers）

```python
from guidance.models import Transformers

lm = Transformers(
    "microsoft/Phi-4-mini-instruct",
    device="cuda"  # Or "cpu"
)
```

<a id="local-models-llama-cpp"></a>
### 本地模型（llama.cpp）

```python
from guidance.models import LlamaCpp

lm = LlamaCpp(
    model_path="/path/to/model.gguf",
    n_ctx=4096,
    n_gpu_layers=35
)
```

<a id="common-patterns"></a>
## 常见模式

<a id="pattern-1-json-generation"></a>
### 模式1：JSON生成

```python
from guidance import models, gen, system, user, assistant

lm = models.Anthropic("claude-sonnet-4-5-20250929")

with system():
    lm += "You generate valid JSON."

with user():
    lm += "Generate a user profile with name, age, and email."

with assistant():
    lm += """{
    "name": """ + gen("name", regex=r'"[A-Za-z ]+"', max_tokens=30) + """,
    "age": """ + gen("age", regex=r"[0-9]+", max_tokens=3) + """,
    "email": """ + gen("email", regex=r'"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"', max_tokens=50) + """
}"""

print(lm)  # Valid JSON guaranteed
```

<a id="pattern-2-classification"></a>
### 模式2：分类

```python
from guidance import models, gen, select

lm = models.Anthropic("claude-sonnet-4-5-20250929")

text = "This product is amazing! I love it."

lm += f"Text: {text}\n"
lm += "Sentiment: " + select(["positive", "negative", "neutral"], name="sentiment")
lm += "\nConfidence: " + gen("confidence", regex=r"[0-9]+", max_tokens=3) + "%"

print(f"Sentiment: {lm['sentiment']}")
print(f"Confidence: {lm['confidence']}%")
```

<a id="pattern-3-multi-step-reasoning"></a>
### 模式3：多步推理

```python
from guidance import models, gen, guidance

@guidance
def chain_of_thought(lm, question):
    """Generate answer with step-by-step reasoning."""
    lm += f"Question: {question}\n\n"

    # Generate multiple reasoning steps
    for i in range(3):
        lm += f"Step {i+1}: " + gen(f"step_{i+1}", stop="\n", max_tokens=100) + "\n"

    # Final answer
    lm += "\nTherefore, the answer is: " + gen("answer", max_tokens=50)

    return lm

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = chain_of_thought(lm, "What is 15% of 200?")

print(lm["answer"])
```
<a id="pattern-4-react-agent"></a>
### 模式 4：ReAct Agent

```python
from guidance import models, gen, select, guidance

@guidance(stateless=False)
def react_agent(lm, question):
    """支持工具使用的 ReAct Agent。"""
    tools = {
        "calculator": lambda expr: eval(expr),
        "search": lambda query: f"Search results for: {query}",
    }

    lm += f"Question: {question}\n\n"

    for round in range(5):
        # 思考
        lm += f"Thought: " + gen("thought", stop="\n") + "\n"

        # 选择动作
        lm += "Action: " + select(["calculator", "search", "answer"], name="action")

        if lm["action"] == "answer":
            lm += "\nFinal Answer: " + gen("answer", max_tokens=100)
            break

        # 动作输入
        lm += "\nAction Input: " + gen("action_input", stop="\n") + "\n"

        # 执行工具
        if lm["action"] in tools:
            result = tools[lm["action"]](lm["action_input"])
            lm += f"Observation: {result}\n\n"

    return lm

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = react_agent(lm, "What is 25 * 4 + 10?")
print(lm["answer"])
```

<a id="pattern-5-data-extraction"></a>
### 模式 5：数据提取

```python
from guidance import models, gen, guidance

@guidance
def extract_entities(lm, text):
    """从文本中提取结构化实体。"""
    lm += f"Text: {text}\n\n"

    # 提取人物
    lm += "Person: " + gen("person", stop="\n", max_tokens=30) + "\n"

    # 提取组织
    lm += "Organization: " + gen("organization", stop="\n", max_tokens=30) + "\n"

    # 提取日期
    lm += "Date: " + gen("date", regex=r"\d{4}-\d{2}-\d{2}", max_tokens=10) + "\n"

    # 提取地点
    lm += "Location: " + gen("location", stop="\n", max_tokens=30) + "\n"

    return lm

text = "Tim Cook announced at Apple Park on 2024-09-15 in Cupertino."

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = extract_entities(lm, text)

print(f"Person: {lm['person']}")
print(f"Organization: {lm['organization']}")
print(f"Date: {lm['date']}")
print(f"Location: {lm['location']}")
```

<a id="best-practices"></a>
## 最佳实践

<a id="1-use-regex-for-format-validation"></a>
### 1. 使用正则表达式进行格式校验

```python
# ✅ 好：正则表达式确保格式有效
lm += "Email: " + gen("email", regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# ❌ 差：自由生成可能产生无效邮箱
lm += "Email: " + gen("email", max_tokens=50)
```

<a id="2-use-select-for-fixed-categories"></a>
### 2. 对固定类别使用 select()

```python
# ✅ 好：保证类别有效
lm += "Status: " + select(["pending", "approved", "rejected"], name="status")

# ❌ 差：可能产生拼写错误或无效值
lm += "Status: " + gen("status", max_tokens=20)
```

<a id="3-leverage-token-healing"></a>
### 3. 利用 Token Healing

```python
# Token healing 默认启用
# 无需特殊操作——只需自然拼接即可
lm += "The capital is " + gen("capital")  # 自动修复
```

<a id="4-use-stop-sequences"></a>
### 4. 使用停止序列

```python
# ✅ 好：单行输出时在换行处停止
lm += "Name: " + gen("name", stop="\n")

# ❌ 差：可能生成多行
lm += "Name: " + gen("name", max_tokens=50)
```
<a id="5-create-reusable-functions"></a>
### 5. 创建可复用的函数

```python
# ✅ 好：可复用的模式
@guidance
def generate_person(lm):
    lm += "Name: " + gen("name", stop="\n")
    lm += "\nAge: " + gen("age", regex=r"[0-9]+")
    return lm

# 多次使用
lm = generate_person(lm)
lm += "\n\n"
lm = generate_person(lm)
```

<a id="6-balance-constraints"></a>
### 6. 平衡约束

```python
# ✅ 好：合理的约束
lm += gen("name", regex=r"[A-Za-z ]+", max_tokens=30)

# ❌ 过于严格：可能失败或非常缓慢
lm += gen("name", regex=r"^(John|Jane)$", max_tokens=10)
```

<a id="comparison-to-alternatives"></a>
## 与其他方案的对比

| 特性 | Guidance | Instructor | Outlines | LMQL |
|---------|----------|------------|----------|------|
| 正则约束 | ✅ 是 | ❌ 否 | ✅ 是 | ✅ 是 |
| 语法支持 | ✅ CFG | ❌ 否 | ✅ CFG | ✅ CFG |
| Pydantic 验证 | ❌ 否 | ✅ 是 | ✅ 是 | ❌ 否 |
| Token 修复 | ✅ 是 | ❌ 否 | ✅ 是 | ❌ 否 |
| 本地模型 | ✅ 是 | ⚠️ 有限制 | ✅ 是 | ✅ 是 |
| API 模型 | ✅ 是 | ✅ 是 | ⚠️ 有限制 | ✅ 是 |
| Pythonic 语法 | ✅ 是 | ✅ 是 | ✅ 是 | ❌ 类 SQL |
| 学习曲线 | 低 | 低 | 中 | 高 |

**何时选择 Guidance：**
- 需要正则/语法约束
- 需要 Token 修复
- 构建带有控制流的复杂工作流
- 使用本地模型（Transformers，llama.cpp）
- 偏好 Pythonic 语法

**何时选择其他方案：**
- Instructor：需要自动重试的 Pydantic 验证
- Outlines：需要 JSON schema 验证
- LMQL：偏好声明式查询语法

<a id="performance-characteristics"></a>
## 性能特点

**延迟降低：**
- 对于受限输出，比传统提示词快 30-50%
- Token 修复减少了不必要的重新生成
- 语法约束阻止生成无效 token

**内存使用：**
- 相比无约束生成，开销极小
- 语法编译在首次使用后缓存
- 推理时的高效 token 过滤

**Token 效率：**
- 防止 token 浪费在无效输出上
- 无需重试循环
- 直达有效输出的路径

<a id="resources"></a>
## 资源

- **文档**: https://guidance.readthedocs.io
- **GitHub**: https://github.com/guidance-ai/guidance (18k+ 星标)
- **Notebooks**: https://github.com/guidance-ai/guidance/tree/main/notebooks
- **Discord**: 社区支持可用

<a id="see-also"></a>
## 参见

- `references/constraints.md` - 全面的正则与语法模式
- `references/backends.md` - 后端特定配置
- `references/examples.md` - 生产级示例
