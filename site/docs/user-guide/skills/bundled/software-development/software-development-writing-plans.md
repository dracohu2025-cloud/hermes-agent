---
title: "编写计划 — 编写实现计划：小任务、路径、代码"
sidebar_label: "编写计划"
description: "编写实现计划：小任务、路径、代码"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="writing-plans"></a>
# 编写计划

编写实现计划：小任务、路径、代码。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/writing-plans` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `planning`, `design`, `implementation`, `workflow`, `documentation` |
| 相关技能 | [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development), [`test-driven-development`](/user-guide/skills/bundled/software-development/software-development-test-driven-development), [`requesting-code-review`](/user-guide/skills/bundled/software-development/software-development-requesting-code-review) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="writing-implementation-plans"></a>
# 编写实现计划

<a id="overview"></a>
## 概述

编写全面的实现计划，假设实现者对代码库一无所知，且品味存疑。记录他们所需的一切：要修改哪些文件、完整代码、测试命令、要检查的文档、如何验证。给他们小任务。DRY。YAGNI。TDD。频繁提交。

假设实现者是一名熟练的开发者，但对工具集或问题领域几乎一无所知。假设他们不太擅长设计好的测试。

**核心原则：** 好的计划能让实现变得显而易见。如果有人需要猜测，说明计划不完整。

<a id="when-to-use"></a>
## 何时使用

**始终在以下情况前使用：**
- 实现多步骤功能
- 分解复杂需求
- 通过 subagent-driven-development 将任务委托给子 Agent

**不要跳过的情况：**
- 功能看似简单（假设会导致错误）
- 你打算自己实现（未来的你需要指导）
- 独自工作（文档很重要）

<a id="bite-sized-task-granularity"></a>
## 小任务的粒度

**每个任务 = 2-5 分钟的专注工作。**

每一步都是一个操作：
- "编写失败的测试" — 步骤
- "运行测试确保它失败" — 步骤
- "实现最简代码使测试通过" — 步骤
- "运行测试确保通过" — 步骤
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

<a id="plan-document-structure"></a>
## 计划文档结构

<a id="header-required"></a>
### 头部（必需）

每个计划必须以以下内容开头：

```markdown
# [功能名称] 实现计划

> **给 Hermes 的提示：** 使用 subagent-driven-development 技能逐个任务实现此计划。

**目标：** [一句话描述此计划构建的内容]

**架构：** [2-3 句话描述方法]

**技术栈：** [关键技术/库]

---
```
<a id="task-structure"></a>
### Task Structure

每个任务遵循以下格式：

````markdown
### Task N: [Descriptive Name]

**Objective:** 此任务要完成什么（一句话）

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67`（已知行号的情况下）
- Test: `tests/path/to/test_file.py`

**Step 1: 编写失败的测试**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: 运行测试以验证失败**

运行：`pytest tests/path/test.py::test_specific_behavior -v`
预期：FAIL — "function not defined"

**Step 3: 编写最小实现**

```python
def function(input):
    return expected
```

**Step 4: 运行测试以验证通过**

运行：`pytest tests/path/test.py::test_specific_behavior -v`
预期：PASS

**Step 5: 提交**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

<a id="writing-process"></a>
## 编写流程

<a id="step-1-understand-requirements"></a>
### Step 1: 理解需求

阅读并理解：
- 功能需求
- 设计文档或用户描述
- 验收标准
- 约束条件

<a id="step-2-explore-the-codebase"></a>
### Step 2: 探索代码库

使用 Hermes 工具了解项目：

```python
# 理解项目结构
search_files("*.py", target="files", path="src/")

# 查看类似功能
search_files("similar_pattern", path="src/", file_glob="*.py")

# 检查现有测试
search_files("*.py", target="files", path="tests/")

# 阅读关键文件
read_file("src/app.py")
```

<a id="step-3-design-approach"></a>
### Step 3: 设计方案

确定：
- 架构模式
- 文件组织
- 所需依赖
- 测试策略

<a id="step-4-write-tasks"></a>
### Step 4: 编写任务

按顺序创建任务：
1. 设置/基础设施
2. 核心功能（每个都采用 TDD）
3. 边界情况
4. 集成
5. 清理/文档

<a id="step-5-add-complete-details"></a>
### Step 5: 添加完整细节

对于每个任务，包含：
- **确切的文件路径**（不写 "config 文件"，而是 `src/config/settings.py`）
- **完整的代码示例**（不写 "添加验证"，而是实际代码）
- **确切的命令**及预期输出
- **验证步骤**，证明任务可行

<a id="step-6-review-the-plan"></a>
### Step 6: 审查计划

检查：
- [ ] 任务具有顺序性和逻辑性
- [ ] 每个任务都是适中的（2-5 分钟）
- [ ] 文件路径准确无误
- [ ] 代码示例完整（可复制粘贴）
- [ ] 命令精确，且包含预期输出
- [ ] 没有缺失的上下文
- [ ] 应用了 DRY、YAGNI、TDD 原则

<a id="step-7-save-the-plan"></a>
### Step 7: 保存计划

```bash
mkdir -p docs/plans
# 将计划保存到 docs/plans/YYYY-MM-DD-feature-name.md
git add docs/plans/
git commit -m "docs: add implementation plan for [feature]"
```

<a id="principles"></a>
## 原则

<a id="dry-don-t-repeat-yourself"></a>
### DRY（Don't Repeat Yourself，不要重复自己）

**糟糕：** 在 3 个地方复制粘贴验证逻辑
**好：** 提取验证函数，到处复用

<a id="yagni-you-aren-t-gonna-need-it"></a>
### YAGNI（You Aren't Gonna Need It，你不会用到它）

**糟糕：** 为未来的需求添加“灵活性”
**好：** 只实现当前需要的

```python
# 糟糕 — 违反 YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # 现在不需要！
        self.metadata = {}     # 现在不需要！

# 好 — 符合 YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```
<a id="tdd-test-driven-development"></a>
### TDD（测试驱动开发）

每个生成代码的任务都应包含完整的 TDD 循环：
1. 编写会失败的测试
2. 运行以验证失败
3. 编写最简代码
4. 运行以验证通过

详情请参阅 `test-driven-development` 技能。

<a id="frequent-commits"></a>
### 频繁提交

每完成一个任务后提交：
```bash
git add [文件]
git commit -m "类型: 描述"
```

<a id="common-mistakes"></a>
## 常见错误

<a id="vague-tasks"></a>
### 任务描述模糊

**错误：** "添加认证功能"
**正确：** "创建包含 email 和 password_hash 字段的 User 模型"

<a id="incomplete-code"></a>
### 代码不完整

**错误：** "步骤 1：添加验证函数"
**正确：** "步骤 1：添加验证函数" 后跟完整的函数代码

<a id="missing-verification"></a>
### 缺少验证步骤

**错误：** "步骤 3：测试是否正常"
**正确：** "步骤 3：运行 `pytest tests/test_auth.py -v`，预期结果：3 个测试通过"

<a id="missing-file-paths"></a>
### 缺少文件路径

**错误：** "创建模型文件"
**正确：** "创建：`src/models/user.py`"

<a id="execution-handoff"></a>
## 执行交接

保存计划后，提供执行方案：

**"计划已完成并保存。准备使用 subagent-driven-development 执行——我将为每个任务分派一个全新的 subagent，并进行两阶段审查（规范合规性审查，然后代码质量审查）。是否继续？"**

执行时，使用 `subagent-driven-development` 技能：
- 每个任务使用全新的 `delegate_task`，并附带完整上下文
- 每个任务完成后进行规范合规性审查
- 规范审查通过后进行代码质量审查
- 仅当两项审查均通过时才继续

<a id="remember"></a>
## 记住

```
小粒度任务（每个 2-5 分钟）
精确的文件路径
完整的代码（可直接复制粘贴）
包含预期输出的精确命令
验证步骤
DRY、YAGNI、TDD
频繁提交
```

**好的计划能让实现变得显而易见。**
