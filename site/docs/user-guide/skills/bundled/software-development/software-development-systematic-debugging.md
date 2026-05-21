---
title: "Systematic Debugging — 4-phase root cause debugging: understand bugs before fixing"
sidebar_label: "Systematic Debugging"
description: "4-phase root cause debugging: understand bugs before fixing"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="systematic-debugging"></a>
# Systematic Debugging

4-phase root cause debugging: understand bugs before fixing.

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/systematic-debugging` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `debugging`, `troubleshooting`, `problem-solving`, `root-cause`, `investigation` |
| 相关技能 | [`test-driven-development`](/user-guide/skills/bundled/software-development/software-development-test-driven-development), [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans), [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# Systematic Debugging

<a id="overview"></a>
## 概述

随机修复既浪费时间，又会引入新 Bug。快速补丁只会掩盖根本问题。

**核心原则：** 在尝试修复之前，务必先找到根本原因。只治标不治本，就是失败。

**违反本流程的字面要求，就是违背调试的精神。**

<a id="the-iron-law"></a>
## 铁律

```
不先调查根本原因，就不准修复
```

如果你还没有完成第一阶段，就不能提出修复方案。

<a id="when-to-use"></a>
## 何时使用

适用于任何技术问题：
- 测试失败
- 生产环境中的 Bug
- 意外行为
- 性能问题
- 构建失败
- 集成问题

**特别在以下情况使用：**
- 时间紧迫时（紧急情况容易让人想猜答案）
- “就快速修一下”看起来很明显时
- 你已经尝试过多次修复
- 之前的修复没有生效
- 你还没有完全理解问题

**不要跳过的情况：**
- 问题看起来很简单（简单的 Bug 也有根本原因）
- 你很赶时间（越急越容易返工）
- 有人要求立刻修好（系统化比乱试更快）

<a id="the-four-phases"></a>
## 四个阶段

你必须完成每个阶段后，才能进入下一个阶段。

---

<a id="phase-1-root-cause-investigation"></a>
## 第一阶段：根本原因调查

**在尝试任何修复之前：**

<a id="1-read-error-messages-carefully"></a>
### 1. 仔细阅读错误信息

- 不要跳过错误或警告
- 它们通常包含确切的解决方案
- 完整阅读堆栈跟踪
- 注意行号、文件路径、错误代码

**操作：** 使用 `read_file` 读取相关源文件。使用 `search_files` 在代码库中查找错误字符串。

<a id="2-reproduce-consistently"></a>
### 2. 稳定复现

- 你能可靠地触发它吗？
- 确切的步骤是什么？
- 每次都会发生吗？
- 如果不能复现 → 收集更多数据，不要猜测

**操作：** 使用 `terminal` 工具运行失败的测试或触发 Bug：

```bash
# 运行特定的失败测试
pytest tests/test_module.py::test_name -v

# 运行并输出详细信息
pytest tests/test_module.py -v --tb=long
```
<a id="3-check-recent-changes"></a>
### 3. 检查近期变更

- 哪些改动可能导致这个问题？
- Git diff、最近的提交
- 新增依赖、配置变更

**操作：**

```bash
# 最近的提交
git log --oneline -10

# 未提交的变更
git diff

# 特定文件的变更历史
git log -p --follow src/problematic_file.py | head -100
```

<a id="4-gather-evidence-in-multi-component-systems"></a>
### 4. 在多组件系统中收集证据

**当系统包含多个组件时（API → 服务 → 数据库，CI → 构建 → 部署）：**

**在提出修复方案之前，先添加诊断工具：**

对于每个组件边界：
- 记录进入组件的数据
- 记录离开组件的数据
- 验证环境/配置的传递
- 检查每一层的状态

运行一次以收集证据，找出问题出在哪里。
然后分析证据，确定出故障的组件。
然后深入调查该特定组件。

<a id="5-trace-data-flow"></a>
### 5. 追踪数据流

**当错误出现在调用栈深处时：**

- 错误的值从何而来？
- 是谁用这个错误的值调用了该函数？
- 持续向上游追踪，直到找到源头
- 在源头修复，而不是在症状处修复

**操作：** 使用 `search_files` 追踪引用：

```python
# 查找函数被调用的位置
search_files("function_name(", path="src/", file_glob="*.py")

# 查找变量被赋值的位置
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

<a id="phase-1-completion-checklist"></a>
### 第一阶段完成检查清单

- [ ] 错误信息已完整阅读并理解
- [ ] 问题已稳定复现
- [ ] 近期变更已识别并审查
- [ ] 证据已收集（日志、状态、数据流）
- [ ] 问题已定位到特定组件/代码
- [ ] 已形成根因假设

**停止：** 在理解问题发生的原因之前，不要进入第二阶段。

---

<a id="phase-2-pattern-analysis"></a>
## 第二阶段：模式分析

**在修复之前先找到模式：**

<a id="1-find-working-examples"></a>
### 1. 寻找工作正常的示例

- 在同一代码库中找到类似的工作代码
- 哪些正常工作的代码与出问题的代码相似？

**操作：** 使用 `search_files` 查找可比较的模式：

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

<a id="2-compare-against-references"></a>
### 2. 对照参考实现

- 如果要实现某个模式，请完整阅读参考实现
- 不要略读——逐行阅读
- 在应用之前充分理解该模式

<a id="3-identify-differences"></a>
### 3. 找出差异

- 工作代码与出问题代码之间有什么不同？
- 列出所有差异，无论多小
- 不要假设“那个不可能有影响”

<a id="4-understand-dependencies"></a>
### 4. 理解依赖关系

- 这需要哪些其他组件？
- 需要哪些设置、配置、环境？
- 它做了哪些假设？

---

<a id="phase-3-hypothesis-and-testing"></a>
## 第三阶段：假设与测试

**科学方法：**

<a id="1-form-a-single-hypothesis"></a>
### 1. 形成单一假设

- 明确陈述：“我认为 X 是根因，因为 Y”
- 写下来
- 要具体，不要模糊

<a id="2-test-minimally"></a>
### 2. 最小化测试

- 做出**最小**的改动来测试假设
- 一次只改变一个变量
- 不要同时修复多个问题

<a id="3-verify-before-continuing"></a>
### 3. 验证后再继续

- 有效？→ 进入第四阶段
- 无效？→ 形成新的假设
- **不要**在已有修复上叠加更多修复
<a id="4-when-you-don-t-know"></a>
### 4. 当你不确定时

- 说“我不理解 X”
- 不要假装懂
- 向用户求助
- 再多研究一下

---

<a id="phase-4-implementation"></a>
## 阶段 4：实施

**修复根本原因，而不是表面症状：**

<a id="1-create-failing-test-case"></a>
### 1. 创建会失败的测试用例

- 最简单的可复现方式
- 尽可能用自动化测试
- 修复之前**必须**有
- 使用 `test-driven-development` 技能

<a id="2-implement-single-fix"></a>
### 2. 实施单一修复

- 针对已识别出的根本原因
- **一次只改一处**
- 不做“顺便改进”
- 不捆绑重构

<a id="3-verify-fix"></a>
### 3. 验证修复

```bash
# 运行特定的回归测试
pytest tests/test_module.py::test_regression -v

# 运行全套测试——无回归
pytest tests/ -q
```

<a id="4-if-fix-doesn-t-work-the-rule-of-three"></a>
### 4. 如果修复无效——三击规则

- **停止。**
- 数一数：你尝试了几次修复？
- 如果 < 3：回到阶段 1，用新信息重新分析
- **如果 ≥ 3：停止并质疑架构（下面的第 5 步）**
- **不要在没有架构讨论的情况下尝试第 4 次修复**

<a id="5-if-3-fixes-failed-question-architecture"></a>
### 5. 如果 3 次以上修复都失败：质疑架构

**表明存在架构问题的模式：**
- 每次修复都会在不同地方暴露新的共享状态/耦合
- 修复需要“大规模重构”才能实现
- 每次修复都会在其他地方引发新症状

**停下来质疑基础：**
- 这个模式从根本上来说合理吗？
- 我们是不是“纯粹因为惯性而坚持它”？
- 我们应该重构架构，还是继续修复症状？

**在尝试更多修复之前，先与用户讨论。**

这不是一个失败的假设——这是一个错误的架构。

---

<a id="red-flags-stop-and-follow-process"></a>
## 危险信号——停下来并遵循流程

如果你发现自己有这样的想法：
- “先快速修一下，以后再来调查”
- “试着改改 X，看看能不能行”
- “同时改多处，然后跑测试”
- “跳过测试，我手动验证就行”
- “大概是 X 的问题，我来修它”
- “我虽然没有完全理解，但这样可能管用”
- “模式说用 X，但我要按自己的方式调整一下”
- “主要问题如下：[列出修复方案，但没有经过调查]”
- 在追踪数据流之前就提出解决方案
- **“再试一次修复”（当已经尝试过 2 次以上时）**
- **每次修复都在不同地方暴露出新问题**

**所有这些都意味着：停止。回到阶段 1。**

**如果 3 次以上修复失败：** 质疑架构（阶段 4 的第 5 步）。

<a id="common-rationalizations"></a>
## 常见借口

| 借口 | 现实 |
|--------|---------|
| “问题很简单，不需要流程” | 简单问题也有根本原因。对简单 bug 来说流程也很快。 |
| “紧急情况，没时间走流程” | 系统性调试比瞎猜乱试要**更快**。 |
| “先试试这个，然后再调查” | 第一次修复就定了调子。从一开始就做对。 |
| “等确认修复有效再写测试” | 没经过测试的修复不牢靠。先测试才能证明。 |
| “一次改多处能节省时间” | 无法隔离到底是哪一步起作用，还会引入新 bug。 |
| “参考文档太长了，我按模式自己改改” | 部分理解必然会带来 bug。请完整阅读。 |
| “我看到问题了，我来修” | 看到症状 ≠ 理解根本原因。 |
| “再试一次修复”（已经失败 2 次以上） | 3 次以上失败 = 架构问题。质疑模式，别再修了。 |
<a id="quick-reference"></a>
## 快速参考

| 阶段 | 关键活动 | 成功标准 |
|-------|---------------|------------------|
| **1. 根本原因** | 读取错误、复现、检查变更、收集证据、追踪数据流 | 理解是什么和为什么 |
| **2. 模式** | 寻找可工作的示例、对比、找出差异 | 知道哪里不同 |
| **3. 假设** | 形成理论、最小化测试、一次只变一个变量 | 假设被证实或形成新假设 |
| **4. 实施** | 创建回归测试、修复根本原因、验证 | Bug 已解决，全部测试通过 |

<a id="hermes-agent-integration"></a>
## Hermes Agent 集成

<a id="investigation-tools"></a>
### 调查工具

在阶段1中使用以下 Hermes 工具：

- **`search_files`** — 查找错误字符串、追踪函数调用、定位模式
- **`read_file`** — 按行号读取源代码进行精确分析
- **`terminal`** — 运行测试、检查 Git 历史、复现 Bug
- **`web_search`/`web_extract`** — 调研错误信息和库文档

<a id="with-delegatetask"></a>
### 使用 delegate_task

对于复杂的多组件调试，分发调查 subagents：

```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging skill:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

<a id="with-test-driven-development"></a>
### 结合测试驱动开发

修复 Bug 时：
1. 编写复现 Bug 的测试（RED）
2. 系统调试以找到根本原因
3. 修复根本原因（GREEN）
4. 测试验证修复并防止回归

<a id="real-world-impact"></a>
## 实际影响

来自调试会话：
- 系统方法：15-30 分钟修复
- 随机修复方法：2-3 小时的折腾
- 首次修复率：95% vs 40%
- 引入的新 Bug：几乎为零 vs 常见

**不走捷径。不做猜测。系统方法永远获胜。**
