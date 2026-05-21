---
title: "测试驱动开发 — TDD：遵循 RED-GREEN-REFACTOR，先写测试再写代码"
sidebar_label: "测试驱动开发"
description: "TDD：遵循 RED-GREEN-REFACTOR，先写测试再写代码"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="test-driven-development"></a>
# 测试驱动开发

TDD：遵循 RED-GREEN-REFACTOR，先写测试再写代码。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内建（默认安装） |
| 路径 | `skills/software-development/test-driven-development` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `testing`, `tdd`, `development`, `quality`, `red-green-refactor` |
| 相关技能 | [`systematic-debugging`](/user-guide/skills/bundled/software-development/software-development-systematic-debugging)、[`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans)、[`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在该技能被触发时加载的完整技能定义。技能激活时，Agent 会以此作为指令。
:::

<a id="test-driven-development-tdd"></a>
# 测试驱动开发（TDD）

<a id="overview"></a>
## 概述

先写测试。看着它失败。再写最少的代码让它通过。

**核心原则：** 如果你没有亲眼看到测试失败，你就不知道它是否在测试正确的东西。

**违背规则的文字就是违背规则的精神。**

<a id="when-to-use"></a>
## 何时使用

**总是：**
- 新功能
- 错误修复
- 重构
- 行为变更

**例外情况（先询问用户）：**
- 一次性原型
- 生成的代码
- 配置文件

想着“就这一次跳过 TDD”？停下。那是自我合理化。

<a id="the-iron-law"></a>
## 铁律

```
没有先失败的测试，就不写生产代码
```

先写代码后写测试？删掉。重来。

**没有例外：**
- 不要把它当作“参考”保留
- 不要在写测试时“调整”它
- 不要看它
- 删掉就是删掉

根据测试重新实现。就这样。

<a id="red-green-refactor-cycle"></a>
## 红-绿-重构循环

<a id="red-write-failing-test"></a>
### 红 — 编写失败的测试

编写一个最小测试，展示应该发生什么。

**好的测试：**
```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception('fail')
        return 'success'

    result = retry_operation(operation)

    assert result == 'success'
    assert attempts == 3
```
清晰的名字，测试真实行为，只测一件事。

**糟糕的测试：**
```python
def test_retry_works():
    mock = MagicMock()
    mock.side_effect = [Exception(), Exception(), 'success']
    result = retry_operation(mock)
    assert result == 'success'  # What about retry count? Timing?
```
名字模糊，测试的是 mock 而不是真实代码。

**要求：**
- 每个测试只测一种行为
- 清晰描述的名字（名字里有“and”？拆开）
- 用真实代码，不用 mock（除非真的无法避免）
- 名字描述行为，而不是实现

<a id="verify-red-watch-it-fail"></a>
### 验证红 — 看着它失败
**MANDATORY. 不可跳过。**

```bash
# 使用终端工具运行指定测试
pytest tests/test_feature.py::test_specific_behavior -v
```

确认：
- 测试失败（不是由于拼写错误导致的报错）
- 失败信息符合预期
- 失败原因是功能缺失

**测试立刻通过？** 说明你测试的是已有行为。修改测试。

**测试报错？** 先修复错误，重新运行直到它正确失败。

<a id="green-minimal-code"></a>
### GREEN — 最简代码

写出能通过测试的最简单代码。不做多余的事。

**好的写法：**
```python
def add(a, b):
    return a + b  # 不多不少
```

**不好的写法：**
```python
def add(a, b):
    result = a + b
    logging.info(f"Adding {a} + {b} = {result}")  # 多余！
    return result
```

不要添加功能、重构其他代码，或者“优化”超出测试范围的内容。

**在 GREEN 阶段作弊是允许的：**
- 硬编码返回值
- 复制粘贴
- 重复代码
- 跳过边界情况

我们会在 REFACTOR 阶段修复。

<a id="verify-green-watch-it-pass"></a>
### 验证 GREEN — 观察它通过

**MANDATORY.**

```bash
# 运行指定测试
pytest tests/test_feature.py::test_specific_behavior -v

# 然后运行所有测试，检查回归问题
pytest tests/ -q
```

确认：
- 测试通过
- 其他测试依然通过
- 输出干净（无错误、无警告）

**测试失败？** 修复代码，而不是修改测试。

**其他测试失败？** 立即修复回归问题。

<a id="refactor-clean-up"></a>
### REFACTOR — 清理代码

仅在绿灯通过后：
- 消除重复
- 改进命名
- 提取辅助函数
- 简化表达式

保持测试一直通过。不要增加行为。

**如果重构过程中测试失败：** 立即撤销。采取更小的步骤。

<a id="repeat"></a>
### 重复循环

下一个行为的失败测试。一次一个循环。

<a id="why-order-matters"></a>
## 为什么顺序很重要

**“我会在写代码之后写测试来验证它是否能工作”**

开发之后写的测试会立刻通过。立刻通过证明不了什么：
- 可能测试了错误的东西
- 可能测试了实现而非行为
- 可能遗漏了你忘记的边界情况
- 你从未见过它捕获到 Bug

测试优先迫使你看到测试失败，证明它确实在测试某些东西。

**“我已经手动测试了所有边界情况”**

手动测试是临时性的。你以为自己测试了所有情况，但实际上：
- 没有记录测试了哪些内容
- 代码变更后无法重新运行
- 压力下容易忘记用例
- “我试过它没问题” ≠ 全面

自动化测试是系统性的。它们每次都按相同的方式运行。

**“删掉 X 小时的工作太浪费了”**

这是沉没成本谬误。时间已经过去了。你现在面临的选择：
- 删掉并用 TDD 重写（高置信度）
- 保留并在之后添加测试（低置信度，很可能有 bug）

所谓的“浪费”是保留那些你无法信任的代码。

**“TDD 太教条了，务实就是学会变通”**

TDD 本身就很务实：
- 在提交前发现 bug（比提交后再调试要快）
- 防止回归（测试能立即捕获破坏）
- 文档化行为（测试展示了如何使用代码）
- 支持重构（自由修改，测试会捕获破坏）

所谓的“务实”捷径 = 在生产环境调试 = 更慢。

**“事后写测试也能达到同样目标——重要的是精神而不是仪式”**

不对。事后测试回答的是“这段代码做了什么？”而测试优先回答的是“这段代码应该做什么？”
事后测试会受你的实现影响。你测试的是你构建的内容，而不是真正需要的内容。测试先行强制你在实现之前发现边界情况。

<a id="common-rationalizations"></a>
## 常见的合理化借口

| 借口 | 现实 |
|--------|---------|
| “太简单了，不用测试” | 简单的代码也会出问题。测试只需 30 秒。 |
| “我之后会测试” | 立即通过的测试说明不了任何问题。 |
| “事后测试能达到同样的目的” | 事后测试 = “这代码是干什么的？”；测试先行 = “这代码应该干什么？” |
| “已经手动测试过了” | 临时测试 ≠ 系统性测试。没有记录，无法重跑。 |
| “删掉 X 小时的工作太浪费了” | 沉没成本谬误。保留未经验证的代码就是技术债。 |
| “先留着作参考，之后再写测试” | 你会去修改它，那还是事后测试。要删就彻底删除。 |
| “需要先探索一下” | 可以。探索完就弃掉，从头开始 TDD。 |
| “测试难写 = 设计不清晰” | 倾听测试的声音。难以测试 = 难以使用。 |
| “TDD 会拖慢我的速度” | TDD 比调试更快。务实做法 = 测试先行。 |
| “手动测试更快” | 手动测试无法验证边界情况。每次改动都要重新测。 |
| “现有代码没有测试” | 你正在改进它。为你接触到的代码添加测试。 |

<a id="red-flags-stop-and-start-over"></a>
## 危险信号 —— 立即停止并重新开始

如果你发现自己做了以下任何一件事，删除代码并用 TDD 重启：

- 先写代码再写测试
- 实现之后才测试
- 测试第一次运行就通过
- 无法解释测试为什么失败
- 测试“之后”再添加
- 找借口说“就这一次”
- “我已经手动测试过了”
- “事后测试能达到同样的目的”
- “先留着作参考”或“复用现有代码”
- “已经花了 X 小时，删掉太浪费了”
- “TDD 太教条了，我这样才务实”
- “这次情况不同，因为……”

**所有这些都意味着：删除代码。用 TDD 重新开始。**

<a id="verification-checklist"></a>
## 验证清单

在标记工作完成之前：

- [ ] 每个新函数/方法都有对应的测试
- [ ] 在实现之前观察了每个测试的失败
- [ ] 每个测试的失败原因符合预期（功能缺失，而非拼写错误）
- [ ] 编写了最少量的代码来通过每个测试
- [ ] 所有测试均通过
- [ ] 输出干净（无错误、无警告）
- [ ] 测试使用真实代码（仅在无法避免时才使用 mock）
- [ ] 覆盖了边界情况和错误

无法勾选所有项目？那你跳过了 TDD。重新开始。

<a id="when-stuck"></a>
## 卡住时怎么办

| 问题 | 解决方案 |
|---------|----------|
| 不知道如何测试 | 先写出期望的 API。先写断言。向用户提问。 |
| 测试太复杂 | 设计太复杂。简化接口。 |
| 必须 mock 所有东西 | 代码耦合度过高。使用依赖注入。 |
| 测试设置过于庞大 | 提取辅助方法。依然复杂？简化设计。 |

<a id="hermes-agent-integration"></a>
## Hermes Agent 集成

<a id="running-tests"></a>
### 运行测试

使用 `terminal` 工具在每一步运行测试：

```python
# RED — 验证失败
terminal("pytest tests/test_feature.py::test_name -v")

# GREEN — 验证通过
terminal("pytest tests/test_feature.py::test_name -v")

# 全量套件 — 验证无回归
terminal("pytest tests/ -q")
```

<a id="with-delegatetask"></a>
### 配合 delegate_task

当派发子 Agent 进行实现时，在目标中强制使用 TDD：
```python
delegate_task(
    goal="使用严格的 TDD 实现 [功能]",
    context="""
    遵循测试驱动开发技能：
    1. 先编写会失败的测试
    2. 运行测试，确认它失败
    3. 编写最简代码使其通过
    4. 运行测试，确认它通过
    5. 如有需要，进行重构
    6. 提交

    项目测试命令：pytest tests/ -q
    项目结构：[描述相关文件]
    """,
    toolsets=['terminal', 'file']
)
```

<a id="with-systematic-debugging"></a>
### 结合 systematic-debugging

发现 Bug？先编写能复现它的失败测试。遵循 TDD 循环。该测试既能证明修复有效，也能防止回归。

永远不要在无测试的情况下修复 Bug。

<a id="testing-anti-patterns"></a>
## 测试反模式

- **测试模拟行为而非真实行为** —— 模拟应验证交互，而非替代被测系统
- **测试实现细节** —— 测试行为/结果，而非内部方法调用
- **只测快乐路径** —— 始终测试边界情况、错误和边界
- **脆弱的测试** —— 测试应验证行为，而非结构；重构不应破坏它们

<a id="final-rule"></a>
## 最终规则

```
生产代码 → 测试已存在且先失败
否则 → 不是 TDD
```

未经用户明确许可，不得例外。
