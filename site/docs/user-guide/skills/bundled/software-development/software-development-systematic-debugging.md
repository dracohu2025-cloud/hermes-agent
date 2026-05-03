---
title: "系统性调试 — 4 阶段根因调试：修复前先理解 Bug"
sidebar_label: "系统性调试"
description: "4 阶段根因调试：修复前先理解 Bug"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 系统性调试 {#systematic-debugging}

4 阶段根因调试：修复前先理解 Bug。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/systematic-debugging` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可证 | MIT |
| 标签 | `debugging`, `troubleshooting`, `problem-solving`, `root-cause`, `investigation` |
| 相关技能 | [`test-driven-development`](/user-guide/skills/bundled/software-development/software-development-test-driven-development), [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans), [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="systematic-debugging"></a>
# 系统性调试

## 概述 {#overview}

随机修复浪费了时间，还会引入新 Bug。快速补丁掩盖了根本问题。

**核心原则：** 在尝试修复之前，**始终**先找到根因。只治标不治本就是失败。

**违反本流程的字面规定，就是违背调试的精神。**

## 铁律 {#the-iron-law}

```
没有根因调查，就不允许修复
```

如果你还没有完成阶段 1，就不能提出修复方案。

## 何时使用 {#when-to-use}

适用于任何技术问题：
- 测试失败
- 生产环境中的 Bug
- 意外行为
- 性能问题
- 构建失败
- 集成问题

**特别在以下情况使用：**
- 时间紧迫（紧急情况容易让人想猜）
- “就快速修一下”看起来很明显
- 你已经尝试过多次修复
- 之前的修复没有生效
- 你还没有完全理解问题

**不要跳过的情况：**
- 问题看起来很简单（简单的 Bug 也有根因）
- 你很着急（匆忙必然导致返工）
- 有人要求立刻修好（系统化比乱撞更快）

## 四个阶段 {#the-four-phases}

你必须完成每个阶段后才能进入下一个阶段。

---

## 阶段 1：根因调查 {#phase-1-root-cause-investigation}

**在尝试任何修复之前：**

### 1. 仔细阅读错误信息 {#1-read-error-messages-carefully}

- 不要跳过错误或警告
- 它们通常包含确切的解决方案
- 完整阅读堆栈跟踪
- 注意行号、文件路径、错误代码

**操作：** 使用 `read_file` 读取相关源文件。使用 `search_files` 在代码库中查找错误字符串。

### 2. 稳定复现 {#2-reproduce-consistently}

- 你能可靠地触发它吗？
- 确切的步骤是什么？
- 每次都会发生吗？
- 如果无法复现 → 收集更多数据，不要猜测

**操作：** 使用 `terminal` 工具运行失败的测试或触发 Bug：

```bash
# 运行特定的失败测试
pytest tests/test_module.py::test_name -v

# 运行并输出详细信息
pytest tests/test_module.py -v --tb=long
```
### 3. 检查最近的变更 {#3-check-recent-changes}

- 哪些变更可能导致此问题？
- Git diff、最近的提交
- 新的依赖项、配置变更

**操作：**

```bash
# 最近的提交
git log --oneline -10

# 未提交的变更
git diff

# 特定文件的变更
git log -p --follow src/problematic_file.py | head -100
```

### 4. 在多组件系统中收集证据 {#4-gather-evidence-in-multi-component-systems}

**当系统包含多个组件时（API → 服务 → 数据库，CI → 构建 → 部署）：**

**在提出修复方案之前，先添加诊断工具：**

对于每个组件边界：
- 记录进入组件的数据
- 记录离开组件的数据
- 验证环境/配置的传递
- 检查每一层的状态

运行一次以收集证据，显示问题出在哪里。
然后分析证据，找出有问题的组件。
然后调查该特定组件。

### 5. 追踪数据流 {#5-trace-data-flow}

**当错误出现在调用栈深处时：**

- 错误值从何而来？
- 是谁用这个错误值调用了该函数？
- 持续向上游追踪，直到找到源头
- 在源头修复，而不是在症状处修复

**操作：** 使用 `search_files` 追踪引用：

```python
# 查找函数被调用的位置
search_files("function_name(", path="src/", file_glob="*.py")

# 查找变量被赋值的位置
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

### 第一阶段完成检查清单 {#phase-1-completion-checklist}

- [ ] 错误信息已完整阅读并理解
- [ ] 问题已可稳定复现
- [ ] 最近的变更已识别并审查
- [ ] 证据已收集（日志、状态、数据流）
- [ ] 问题已定位到特定组件/代码
- [ ] 已形成根因假设

**停止：** 在理解问题发生的原因之前，不要进入第二阶段。

---

## 第二阶段：模式分析 {#phase-2-pattern-analysis}

**在修复之前先找到模式：**

### 1. 寻找工作正常的示例 {#1-find-working-examples}

- 在同一个代码库中找到类似的工作代码
- 哪些工作正常的代码与出问题的代码相似？

**操作：** 使用 `search_files` 查找可比较的模式：

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

### 2. 与参考实现对比 {#2-compare-against-references}

- 如果正在实现某个模式，请完整阅读参考实现
- 不要略读——逐行阅读
- 在应用之前完全理解该模式

### 3. 识别差异 {#3-identify-differences}

- 工作正常的代码与出问题的代码之间有什么不同？
- 列出每一个差异，无论多小
- 不要假设“那个不重要”

### 4. 理解依赖关系 {#4-understand-dependencies}

- 这需要哪些其他组件？
- 需要哪些设置、配置、环境？
- 它做了哪些假设？

---

## 第三阶段：假设与测试 {#phase-3-hypothesis-and-testing}

**科学方法：**

### 1. 形成单一假设 {#1-form-a-single-hypothesis}

- 明确陈述：“我认为 X 是根因，因为 Y”
- 写下来
- 要具体，不要模糊

### 2. 最小化测试 {#2-test-minimally}

- 做出尽可能小的变更来测试假设
- 一次只改变一个变量
- 不要同时修复多个问题

### 3. 继续前先验证 {#3-verify-before-continuing}

- 有效了吗？→ 进入第四阶段
- 没效果？→ 形成新的假设
- 不要在此基础上添加更多修复
### 4. 当你不知道时 {#4-when-you-don-t-know}

- 说“我不理解 X”
- 不要假装知道
- 向用户寻求帮助
- 进一步研究

---

## 阶段 4：实施 {#phase-4-implementation}

**修复根本原因，而非表面症状：**

### 1. 创建失败测试用例 {#1-create-failing-test-case}

- 最简单的可复现方式
- 尽可能自动化测试
- 修复前**必须**有
- 使用 `test-driven-development` 技能

### 2. 实施单一修复 {#2-implement-single-fix}

- 针对已识别的根本原因
- 一次只改**一处**
- 不做“顺手”改进
- 不捆绑重构

### 3. 验证修复 {#3-verify-fix}

```bash
# 运行特定的回归测试
pytest tests/test_module.py::test_regression -v

# 运行完整测试套件——确保无回归
pytest tests/ -q
```

### 4. 如果修复无效——三法则 {#4-if-fix-doesn-t-work-the-rule-of-three}

- **停止。**
- 计数：你已经尝试了多少次修复？
- 如果 < 3：返回阶段 1，用新信息重新分析
- **如果 ≥ 3：停止并质疑架构（下面的步骤 5）**
- 未经架构讨论，不要尝试第 4 次修复

### 5. 如果 3 次以上修复失败：质疑架构 {#5-if-3-fixes-failed-question-architecture}

**表明存在架构问题的模式：**
- 每次修复都在不同位置暴露出新的共享状态/耦合
- 修复需要“大规模重构”才能实施
- 每次修复都会在其他地方引发新症状

**停止并质疑根本问题：**
- 这个模式从根本上合理吗？
- 我们是否“纯粹因为惯性而坚持它”？
- 我们应该重构架构，还是继续修复症状？

**在尝试更多修复之前，先与用户讨论。**

这不是假设失败——这是架构错误。

---

## 红旗警示——停止并遵循流程 {#red-flags-stop-and-follow-process}

如果你发现自己正在想：
- “先快速修复，以后再调查”
- “试试改 X 看看行不行”
- “做多处修改，然后跑测试”
- “跳过测试，我手动验证”
- “可能是 X，让我修复它”
- “我不完全理解，但这可能有效”
- “模式说是 X，但我会用不同方式适配”
- “主要问题是：[列出修复方案而不做调查]”
- 在追踪数据流之前就提出解决方案
- **“再试一次修复”（当已经尝试过 2 次以上时）**
- **每次修复都在不同位置暴露出新问题**

**所有这些都意味着：停止。返回阶段 1。**

**如果 3 次以上修复失败：** 质疑架构（阶段 4 步骤 5）。

## 常见借口 {#common-rationalizations}

| 借口 | 现实 |
|--------|---------|
| “问题很简单，不需要流程” | 简单问题也有根本原因。流程对简单 bug 也很快。 |
| “紧急情况，没时间走流程” | 系统化调试比瞎猜乱试**更快**。 |
| “先试试这个，然后再调查” | 第一次修复就定下了基调。从一开始就做对。 |
| “确认修复有效后再写测试” | 未经测试的修复不牢靠。先测试才能证明。 |
| “一次做多个修复节省时间” | 无法隔离哪个有效。还会引入新 bug。 |
| “参考太长，我改一下模式” | 部分理解必然导致 bug。完整阅读。 |
| “我看到问题了，让我修复它” | 看到症状 ≠ 理解根本原因。 |
| “再试一次修复”（失败 2 次以上后） | 3 次以上失败 = 架构问题。质疑模式，不要继续修复。 |
## 快速参考 {#quick-reference}

| 阶段 | 关键活动 | 成功标准 |
|-------|---------------|------------------|
| **1. 根因** | 阅读错误、复现、检查变更、收集证据、追踪数据流 | 理解“是什么”和“为什么” |
| **2. 模式** | 找到正常示例、对比、识别差异 | 知道哪里不同 |
| **3. 假设** | 形成理论、最小化测试、每次只变一个变量 | 确认假设或提出新假设 |
| **4. 实现** | 创建回归测试、修复根因、验证 | Bug 解决，所有测试通过 |

## Hermes Agent 集成 {#hermes-agent-integration}

### 调查工具 {#investigation-tools}

在阶段 1 中使用以下 Hermes 工具：

- **`search_files`** — 查找错误字符串、追踪函数调用、定位模式
- **`read_file`** — 读取带行号的源代码，便于精确分析
- **`terminal`** — 运行测试、查看 git 历史、复现 bug
- **`web_search`/`web_extract`** — 研究错误信息、库文档

### 配合 delegate_task {#with-delegatetask}

对于复杂的多组件调试，可以派发调查子 Agent：

```python
delegate_task(
    goal="调查为什么 [具体测试/行为] 失败",
    context="""
    遵循系统性调试技能：
    1. 仔细阅读错误信息
    2. 复现问题
    3. 追踪数据流以找到根因
    4. 报告发现——暂不修复

    错误：[粘贴完整错误]
    文件：[失败代码的路径]
    测试命令：[精确命令]
    """,
    toolsets=['terminal', 'file']
)
```

### 配合 test-driven-development {#with-test-driven-development}

修复 bug 时：
1. 编写一个能复现 bug 的测试（RED）
2. 系统性地调试以找到根因
3. 修复根因（GREEN）
4. 该测试证明修复有效并防止回归

## 实际效果 {#real-world-impact}

来自调试会话的数据：
- 系统性方法：15-30 分钟修复
- 随机修复方法：2-3 小时反复折腾
- 首次修复率：95% vs 40%
- 引入新 bug：几乎为零 vs 常见

**没有捷径。没有猜测。系统性方法永远胜出。**
