---
title: "编写计划 — 编写实现计划：小任务、路径、代码"
sidebar_label: "编写计划"
description: "编写实现计划：小任务、路径、代码"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 编写计划 {#writing-plans}

编写实现计划：小任务、路径、代码。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/writing-plans` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可证 | MIT |
| 标签 | `planning`, `design`, `implementation`, `workflow`, `documentation` |
| 相关技能 | [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development), [`test-driven-development`](/user-guide/skills/bundled/software-development/software-development-test-driven-development), [`requesting-code-review`](/user-guide/skills/bundled/software-development/software-development-requesting-code-review) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 编写实现计划 {#writing-implementation-plans}

## 概述 {#overview}

编写全面的实现计划，假设实现者对代码库零上下文，且品味存疑。记录他们需要的一切：要修改哪些文件、完整代码、测试命令、要查阅的文档、如何验证。给他们小任务。DRY。YAGNI。TDD。频繁提交。

假设实现者是一位熟练的开发者，但对工具集或问题领域几乎一无所知。假设他们不太擅长设计好的测试。

**核心原则：** 好的计划让实现变得显而易见。如果有人需要猜测，说明计划不完整。

## 何时使用 {#when-to-use}

**在以下情况前始终使用：**
- 实现多步骤功能
- 分解复杂需求
- 通过 subagent-driven-development 将任务委托给子 Agent

**不要跳过的情况：**
- 功能看似简单（假设会导致 bug）
- 你打算自己实现（未来的你需要指导）
- 独自工作（文档很重要）

## 小任务的粒度 {#bite-sized-task-granularity}

**每个任务 = 2-5 分钟的专注工作。**

每一步都是一个动作：
- "编写失败的测试" — 步骤
- "运行测试确保它失败" — 步骤
- "实现让测试通过的最小代码" — 步骤
- "运行测试确保它们通过" — 步骤
- "提交" — 步骤

**太大：**
```markdown
### 任务 1：构建认证系统
[跨 5 个文件的 50 行代码]
```

**合适的大小：**
```markdown
### 任务 1：创建带 email 字段的 User 模型
[10 行，1 个文件]

### 任务 2：为 User 添加密码哈希字段
[8 行，1 个文件]

### 任务 3：创建密码哈希工具
[15 行，1 个文件]
```

## 计划文档结构 {#plan-document-structure}

### 头部（必需） {#header-required}

每个计划必须以以下内容开头：

```markdown
# [功能名称] 实现计划

> **给 Hermes：** 使用 subagent-driven-development 技能逐任务实现此计划。

**目标：** [一句话描述此构建的内容]

**架构：** [2-3 句话描述方法]

**技术栈：** [关键技术/库]

---
```
### 任务结构 {#task-structure}

每个任务遵循以下格式：

````markdown
### 任务 N：[描述性名称]

**目标：** 该任务完成什么（一句话）

**文件：**
- 创建：`exact/path/to/new_file.py`
- 修改：`exact/path/to/existing.py:45-67`（如果知道行号）
- 测试：`tests/path/to/test_file.py`

**步骤 1：编写会失败的测试**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**步骤 2：运行测试以验证失败**

运行：`pytest tests/path/test.py::test_specific_behavior -v`
预期：FAIL — "function not defined"

**步骤 3：编写最小实现**

```python
def function(input):
    return expected
```

**步骤 4：运行测试以验证通过**

运行：`pytest tests/path/test.py::test_specific_behavior -v`
预期：PASS

**步骤 5：提交**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 编写流程 {#writing-process}

### 步骤 1：理解需求 {#step-1-understand-requirements}

阅读并理解：
- 功能需求
- 设计文档或用户描述
- 验收标准
- 约束条件

### 步骤 2：探索代码库 {#step-2-explore-the-codebase}

使用 Hermes 工具了解项目：

```python
# 了解项目结构
search_files("*.py", target="files", path="src/")

# 查看类似功能
search_files("similar_pattern", path="src/", file_glob="*.py")

# 检查现有测试
search_files("*.py", target="files", path="tests/")

# 读取关键文件
read_file("src/app.py")
```

### 步骤 3：设计方案 {#step-3-design-approach}

决定：
- 架构模式
- 文件组织
- 所需依赖
- 测试策略

### 步骤 4：编写任务 {#step-4-write-tasks}

按顺序创建任务：
1. 搭建/基础设施
2. 核心功能（每个都采用 TDD）
3. 边界情况
4. 集成
5. 清理/文档

### 步骤 5：添加完整细节 {#step-5-add-complete-details}

每个任务需包含：
- **精确的文件路径**（不是“配置文件”，而是 `src/config/settings.py`）
- **完整的代码示例**（不是“添加验证”，而是实际代码）
- **精确的命令**及预期输出
- **验证步骤**，证明任务生效

### 步骤 6：审查计划 {#step-6-review-the-plan}

检查：
- [ ] 任务顺序合理、逻辑连贯
- [ ] 每个任务小而精（2-5 分钟）
- [ ] 文件路径精确
- [ ] 代码示例完整（可复制粘贴）
- [ ] 命令精确且包含预期输出
- [ ] 没有遗漏上下文
- [ ] 遵循 DRY、YAGNI、TDD 原则

### 步骤 7：保存计划 {#step-7-save-the-plan}

```bash
mkdir -p docs/plans
# 将计划保存到 docs/plans/YYYY-MM-DD-feature-name.md
git add docs/plans/
git commit -m "docs: add implementation plan for [feature]"
```

## 原则 {#principles}

### DRY（不要重复自己） {#dry-don-t-repeat-yourself}

**糟糕：** 在 3 个地方复制粘贴验证逻辑
**良好：** 提取验证函数，到处使用

### YAGNI（你不会需要它） {#yagni-you-aren-t-gonna-need-it}

**糟糕：** 为未来需求添加“灵活性”
**良好：** 只实现当前需要的功能

```python
# 糟糕 — 违反 YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # 现在不需要！
        self.metadata = {}     # 现在不需要！

# 良好 — 遵循 YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```
### TDD（测试驱动开发） {#tdd-test-driven-development}

每个生成代码的任务都应包含完整的 TDD 循环：
1. 编写会失败的测试
2. 运行以验证失败
3. 编写最简代码
4. 运行以验证通过

详见 `test-driven-development` 技能。

### 频繁提交 {#frequent-commits}

每完成一个任务后提交：
```bash
git add [files]
git commit -m "type: description"
```

## 常见错误 {#common-mistakes}

### 任务描述模糊 {#vague-tasks}

**错误：** "添加认证"
**正确：** "创建包含 email 和 password_hash 字段的 User 模型"

### 代码不完整 {#incomplete-code}

**错误：** "步骤 1：添加验证函数"
**正确：** "步骤 1：添加验证函数" 后跟完整的函数代码

### 缺少验证 {#missing-verification}

**错误：** "步骤 3：测试它是否工作"
**正确：** "步骤 3：运行 `pytest tests/test_auth.py -v`，预期：3 个通过"

### 缺少文件路径 {#missing-file-paths}

**错误：** "创建模型文件"
**正确：** "创建：`src/models/user.py`"

## 执行交接 {#execution-handoff}

保存计划后，提供执行方式：

**"计划已完成并保存。准备好使用 subagent-driven-development 执行——我将为每个任务分派一个全新的 subagent，进行两阶段审查（先规范合规，再代码质量）。是否继续？"**

执行时，使用 `subagent-driven-development` 技能：
- 每个任务使用全新的 `delegate_task`，附带完整上下文
- 每个任务后进行规范合规审查
- 规范通过后进行代码质量审查
- 仅当两个审查都通过时才继续

## 记住 {#remember}

```
小粒度任务（每个 2-5 分钟）
精确的文件路径
完整的代码（可复制粘贴）
精确的命令及预期输出
验证步骤
DRY、YAGNI、TDD
频繁提交
```

**好的计划让实现变得显而易见。**
