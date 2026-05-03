---
title: "Guidance"
sidebar_label: "Guidance"
description: "使用正则表达式和语法控制 LLM 输出，保证有效的 JSON/XML/代码生成，强制结构化格式，并通过 Guidance 构建多步骤工作流..."
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Guidance {#guidance}

使用正则表达式和语法控制 LLM 输出，保证有效的 JSON/XML/代码生成，强制结构化格式，并通过 Guidance（微软研究院的约束生成框架）构建多步骤工作流。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/guidance` 安装 |
| 路径 | `optional-skills/mlops/guidance` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `guidance`, `transformers` |
| 标签 | `Prompt Engineering`, `Guidance`, `Constrained Generation`, `Structured Output`, `JSON Validation`, `Grammar`, `Microsoft Research`, `Format Enforcement`, `Multi-Step Workflows` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Guidance：约束 LLM 生成 {#guidance-constrained-llm-generation}

## 何时使用此技能 {#when-to-use-this-skill}

在以下场景中，请使用 Guidance：
- **使用正则表达式或语法控制 LLM 输出语法**
- **保证有效的 JSON/XML/代码生成**
- **相比传统提示方法降低延迟**
- **强制结构化格式**（日期、电子邮件、ID 等）
- **使用 Pythonic 控制流构建多步骤工作流**
- **通过语法约束防止无效输出**

**GitHub Stars**：18,000+ | **来自**：微软研究院

## 安装 {#installation}

```bash
# 基础安装
pip install guidance

# 使用特定后端
pip install guidance[transformers]  # Hugging Face 模型
pip install guidance[llama_cpp]     # llama.cpp 模型
```

## 快速开始 {#quick-start}

### 基本示例：结构化生成 {#basic-example-structured-generation}

```python
from guidance import models, gen

# 加载模型（支持 OpenAI、Transformers、llama.cpp）
lm = models.OpenAI("gpt-4")

# 带约束的生成
result = lm + "法国的首都是 " + gen("capital", max_tokens=5)

print(result["capital"])  # "巴黎"
```

### 使用 Anthropic Claude {#with-anthropic-claude}

```python
from guidance import models, gen, system, user, assistant

# 配置 Claude
lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 使用上下文管理器实现聊天格式
with system():
    lm += "你是一个乐于助人的助手。"

with user():
    lm += "法国的首都是什么？"

with assistant():
    lm += gen(max_tokens=20)
```

## 核心概念 {#core-concepts}

### 1. 上下文管理器 {#1-context-managers}

Guidance 使用 Pythonic 的上下文管理器实现聊天风格的交互。

```python
from guidance import system, user, assistant, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 系统消息
with system():
    lm += "你是一个 JSON 生成专家。"

# 用户消息
with user():
    lm += "生成一个包含姓名和年龄的人物对象。"

# 助手回复
with assistant():
    lm += gen("response", max_tokens=100)

print(lm["response"])
```

**优点：**
- 自然的聊天流程
- 清晰的角色分离
- 易于阅读和维护
### 2. 约束生成 {#2-constrained-generation}

Guidance 通过正则表达式或语法规则，确保输出符合指定的模式。

#### 正则约束 {#regex-constraints}

```python
from guidance import models, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 约束为有效的电子邮件格式
lm += "Email: " + gen("email", regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# 约束为日期格式 (YYYY-MM-DD)
lm += "Date: " + gen("date", regex=r"\d{4}-\d{2}-\d{2}")

# 约束为电话号码
lm += "Phone: " + gen("phone", regex=r"\d{3}-\d{3}-\d{4}")

print(lm["email"])  # 保证是有效的电子邮件
print(lm["date"])   # 保证是 YYYY-MM-DD 格式
```

**工作原理：**
- 正则表达式在 token 级别被转换为语法规则
- 生成过程中会过滤掉无效的 token
- 模型只能生成匹配的输出

#### 选择约束 {#selection-constraints}

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

print(lm["sentiment"])  # 结果之一：positive, negative, neutral
print(lm["answer"])     # 结果之一：A, B, C, 或 D
```

### 3. Token 修复 {#3-token-healing}

Guidance 会自动“修复”提示词和生成内容之间的 token 边界问题。

**问题：** Token 化会创建不自然的边界。

```python
# 没有 token 修复
prompt = "The capital of France is "
# 最后一个 token: " is "
# 第一个生成的 token 可能是 " Par"（带前导空格）
# 结果："The capital of France is  Paris"（多了一个空格！）
```

**解决方案：** Guidance 会回退一个 token 并重新生成。

```python
from guidance import models, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# Token 修复默认启用
lm += "The capital of France is " + gen("capital", max_tokens=5)
# 结果："The capital of France is Paris"（空格正确）
```

**优点：**
- 自然的文本边界
- 没有尴尬的空格问题
- 更好的模型性能（模型看到的是自然的 token 序列）

### 4. 基于语法的生成 {#4-grammar-based-generation}

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

print(lm["person"])  # 保证是有效的 JSON 结构
```

**使用场景：**
- 复杂的结构化输出
- 嵌套数据结构
- 编程语言语法
- 领域特定语言

### 5. Guidance 函数 {#5-guidance-functions}

使用 `@guidance` 装饰器创建可复用的生成模式。

```python
from guidance import guidance, gen, models

@guidance
def generate_person(lm):
    """生成一个包含姓名和年龄的人。"""
    lm += "Name: " + gen("name", max_tokens=20, stop="\n")
    lm += "\nAge: " + gen("age", regex=r"[0-9]+", max_tokens=3)
    return lm

# 使用该函数
lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = generate_person(lm)

print(lm["name"])
print(lm["age"])
```
**有状态函数：**

```python
@guidance(stateless=False)
def react_agent(lm, question, tools, max_rounds=5):
    """带工具使用的 ReAct Agent。"""
    lm += f"Question: {question}\n\n"

    for i in range(max_rounds):
        # 思考
        lm += f"Thought {i+1}: " + gen("thought", stop="\n")

        # 行动
        lm += "\nAction: " + select(list(tools.keys()), name="action")

        # 执行工具
        tool_result = tools[lm["action"]]()
        lm += f"\nObservation: {tool_result}\n\n"

        # 检查是否完成
        lm += "Done? " + select(["Yes", "No"], name="done")
        if lm["done"] == "Yes":
            break

    # 最终答案
    lm += "\nFinal Answer: " + gen("answer", max_tokens=100)
    return lm
```

## 后端配置 {#backend-configuration}

### Anthropic Claude {#anthropic-claude}

```python
from guidance import models

lm = models.Anthropic(
    model="claude-sonnet-4-5-20250929",
    api_key="your-api-key"  # 或设置 ANTHROPIC_API_KEY 环境变量
)
```

### OpenAI {#openai}

```python
lm = models.OpenAI(
    model="gpt-4o-mini",
    api_key="your-api-key"  # 或设置 OPENAI_API_KEY 环境变量
)
```

### 本地模型（Transformers） {#local-models-transformers}

```python
from guidance.models import Transformers

lm = Transformers(
    "microsoft/Phi-4-mini-instruct",
    device="cuda"  # 或 "cpu"
)
```

### 本地模型（llama.cpp） {#local-models-llama-cpp}

```python
from guidance.models import LlamaCpp

lm = LlamaCpp(
    model_path="/path/to/model.gguf",
    n_ctx=4096,
    n_gpu_layers=35
)
```

## 常见模式 {#common-patterns}

### 模式 1：JSON 生成 {#pattern-1-json-generation}

```python
from guidance import models, gen, system, user, assistant

lm = models.Anthropic("claude-sonnet-4-5-20250929")

with system():
    lm += "你生成有效的 JSON。"

with user():
    lm += "生成一个包含姓名、年龄和邮箱的用户资料。"

with assistant():
    lm += """{
    "name": """ + gen("name", regex=r'"[A-Za-z ]+"', max_tokens=30) + """,
    "age": """ + gen("age", regex=r"[0-9]+", max_tokens=3) + """,
    "email": """ + gen("email", regex=r'"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"', max_tokens=50) + """
}"""

print(lm)  # 保证生成有效的 JSON
```

### 模式 2：分类 {#pattern-2-classification}

```python
from guidance import models, gen, select

lm = models.Anthropic("claude-sonnet-4-5-20250929")

text = "这个产品太棒了！我很喜欢。"

lm += f"Text: {text}\n"
lm += "Sentiment: " + select(["positive", "negative", "neutral"], name="sentiment")
lm += "\nConfidence: " + gen("confidence", regex=r"[0-9]+", max_tokens=3) + "%"

print(f"Sentiment: {lm['sentiment']}")
print(f"Confidence: {lm['confidence']}%")
```

### 模式 3：多步推理 {#pattern-3-multi-step-reasoning}

```python
from guidance import models, gen, guidance

@guidance
def chain_of_thought(lm, question):
    """通过逐步推理生成答案。"""
    lm += f"Question: {question}\n\n"

    # 生成多个推理步骤
    for i in range(3):
        lm += f"Step {i+1}: " + gen(f"step_{i+1}", stop="\n", max_tokens=100) + "\n"

    # 最终答案
    lm += "\nTherefore, the answer is: " + gen("answer", max_tokens=50)

    return lm

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = chain_of_thought(lm, "200 的 15% 是多少？")

print(lm["answer"])
```
### Pattern 4：ReAct Agent {#pattern-4-react-agent}

```python
from guidance import models, gen, select, guidance

@guidance(stateless=False)
def react_agent(lm, question):
    """具备工具使用的 ReAct Agent。"""
    tools = {
        "calculator": lambda expr: eval(expr),
        "search": lambda query: f"搜索结果为：{query}",
    }

    lm += f"问题：{question}\n\n"

    for round in range(5):
        # 思考
        lm += "思考：" + gen("thought", stop="\n") + "\n"

        # 选择动作
        lm += "动作：" + select(["calculator", "search", "answer"], name="action")

        if lm["action"] == "answer":
            lm += "\n最终答案：" + gen("answer", max_tokens=100)
            break

        # 动作输入
        lm += "\n动作输入：" + gen("action_input", stop="\n") + "\n"

        # 执行工具
        if lm["action"] in tools:
            result = tools[lm["action"]](lm["action_input"])
            lm += f"观察结果：{result}\n\n"

    return lm

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = react_agent(lm, "25 * 4 + 10 是多少？")
print(lm["answer"])
```

### Pattern 5：数据提取 {#pattern-5-data-extraction}

```python
from guidance import models, gen, guidance

@guidance
def extract_entities(lm, text):
    """从文本中提取结构化实体。"""
    lm += f"文本：{text}\n\n"

    # 提取人名
    lm += "人名：" + gen("person", stop="\n", max_tokens=30) + "\n"

    # 提取组织名
    lm += "组织名：" + gen("organization", stop="\n", max_tokens=30) + "\n"

    # 提取日期
    lm += "日期：" + gen("date", regex=r"\d{4}-\d{2}-\d{2}", max_tokens=10) + "\n"

    # 提取地点
    lm += "地点：" + gen("location", stop="\n", max_tokens=30) + "\n"

    return lm

text = "Tim Cook 于 2024-09-15 在 Apple Park 库比蒂诺宣布。"

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = extract_entities(lm, text)

print(f"人名：{lm['person']}")
print(f"组织名：{lm['organization']}")
print(f"日期：{lm['date']}")
print(f"地点：{lm['location']}")
```

## 最佳实践 {#best-practices}

### 1. 使用正则表达式验证格式 {#1-use-regex-for-format-validation}

```python
# ✅ 好：正则表达式确保格式正确
lm += "邮箱：" + gen("email", regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# ❌ 差：自由生成可能产生无效邮箱
lm += "邮箱：" + gen("email", max_tokens=50)
```

### 2. 对固定分类使用 select() {#2-use-select-for-fixed-categories}

```python
# ✅ 好：保证得到有效的分类值
lm += "状态：" + select(["pending", "approved", "rejected"], name="status")

# ❌ 差：可能产生拼写错误或无效值
lm += "状态：" + gen("status", max_tokens=20)
```

### 3. 善用 Token Healing {#3-leverage-token-healing}

```python
# Token healing 默认启用
# 无需特殊操作 —— 自然拼接即可
lm += "首都是 " + gen("capital")  # 自动 healing
```

### 4. 使用停止序列 {#4-use-stop-sequences}

```python
# ✅ 好：单行输出时在新行处停止
lm += "姓名：" + gen("name", stop="\n")

# ❌ 差：可能会生成多行
lm += "姓名：" + gen("name", max_tokens=50)
```
### 5. 创建可复用的函数 {#5-create-reusable-functions}

```python
# ✅ 好的：可复用模式
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

### 6. 平衡约束 {#6-balance-constraints}

```python
# ✅ 好的：合理的约束
lm += gen("name", regex=r"[A-Za-z ]+", max_tokens=30)

# ❌ 太严格：可能失败或非常慢
lm += gen("name", regex=r"^(John|Jane)$", max_tokens=10)
```

## 与其他方案的对比 {#comparison-to-alternatives}

| 特性 | Guidance | Instructor | Outlines | LMQL |
|---------|----------|------------|----------|------|
| 正则约束 | ✅ 是 | ❌ 否 | ✅ 是 | ✅ 是 |
| 语法支持 | ✅ CFG | ❌ 否 | ✅ CFG | ✅ CFG |
| Pydantic 验证 | ❌ 否 | ✅ 是 | ✅ 是 | ❌ 否 |
| Token 修复 | ✅ 是 | ❌ 否 | ✅ 是 | ❌ 否 |
| 本地模型 | ✅ 是 | ⚠️ 有限 | ✅ 是 | ✅ 是 |
| API 模型 | ✅ 是 | ✅ 是 | ⚠️ 有限 | ✅ 是 |
| Pythonic 语法 | ✅ 是 | ✅ 是 | ✅ 是 | ❌ SQL-like |
| 学习曲线 | 低 | 低 | 中等 | 高 |

**何时选择 Guidance：**
- 需要正则/语法约束
- 需要 Token 修复
- 构建带有控制流的复杂工作流
- 使用本地模型（Transformers, llama.cpp）
- 偏好 Pythonic 语法

**何时选择其他方案：**
- Instructor：需要 Pydantic 验证与自动重试
- Outlines：需要 JSON Schema 验证
- LMQL：偏好声明式查询语法

## 性能特性 {#performance-characteristics}

**延迟降低：**
- 对于受约束的输出，比传统提示快 30-50%
- Token 修复减少不必要的重新生成
- 语法约束阻止无效 token 的生成

**内存占用：**
- 与非约束生成相比，开销极小
- 语法编译在首次使用后缓存
- 推理时高效的 token 过滤

**Token 效率：**
- 防止在无效输出上浪费 token
- 无需重试循环
- 直达有效输出的路径

## 资源 {#resources}

- **文档**：https://guidance.readthedocs.io
- **GitHub**：https://github.com/guidance-ai/guidance （18k+ 星标）
- **Notebooks**：https://github.com/guidance-ai/guidance/tree/main/notebooks
- **Discord**：可获取社区支持

## 参见 {#see-also}

- `references/constraints.md` - 全面的正则和语法模式
- `references/backends.md` - 后端特定配置
- `references/examples.md` - 生产环境示例
