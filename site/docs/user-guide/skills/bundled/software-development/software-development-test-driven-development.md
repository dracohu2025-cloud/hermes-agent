---
title: "测试驱动开发 — TDD：强制 RED-GREEN-REFACTOR，先写测试再写代码"
sidebar_label: "测试驱动开发"
description: "TDD：强制 RED-GREEN-REFACTOR，先写测试再写代码"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 测试驱动开发 {#test-driven-development}

TDD：强制 RED-GREEN-REFACTOR，先写测试再写代码。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/test-driven-development` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可证 | MIT |
| 标签 | `testing`, `tdd`, `development`, `quality`, `red-green-refactor` |
| 相关技能 | [`systematic-debugging`](/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans), [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会看到这些指令。
:::

# 测试驱动开发（TDD） {#test-driven-development-tdd}

## 概述 {#overview}

先写测试。看着它失败。再写最少的代码让它通过。

**核心原则：** 如果你没有看到测试失败，你就不知道它是否测试了正确的东西。

**违反规则的文字，就是违反规则的精神。**

## 何时使用 {#when-to-use}

**始终使用：**
- 新功能
- Bug 修复
- 重构
- 行为变更

**例外情况（先询问用户）：**
- 一次性原型
- 生成的代码
- 配置文件

心里想“就这一次跳过 TDD”？打住。那是在找借口。

## 铁律 {#the-iron-law}

```
没有先写一个会失败的测试，就不准写生产代码
```

先写了代码？删掉。重新开始。

**没有例外：**
- 不要留着当“参考”
- 不要在写测试时“改编”它
- 不要看它
- 删就是删

从测试开始全新实现。没有商量余地。

## 红-绿-重构循环 {#red-green-refactor-cycle}

### 红色 — 编写会失败的测试 {#red-write-failing-test}

写一个最小的测试，展示应该发生什么。

**好测试：**
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
名称清晰，测试真实行为，只测一件事。

**坏测试：**
```python
def test_retry_works():
    mock = MagicMock()
    mock.side_effect = [Exception(), Exception(), 'success']
    result = retry_operation(mock)
    assert result == 'success'  # 重试次数呢？时机呢？
```
名称模糊，测试的是 mock 而非真实代码。

**要求：**
- 每个测试只测一个行为
- 名称清晰描述性（名称里出现“和”？拆开）
- 用真实代码，不用 mock（除非实在无法避免）
- 名称描述行为，而非实现

### 验证红色 — 看着它失败 {#verify-red-watch-it-fail}

**必须执行。绝不可跳过。**
```bash
# 使用终端工具运行特定的测试
pytest tests/test_feature.py::test_specific_behavior -v
```

确认：
- 测试失败（而不是因拼写错误导致的错误）
- 失败信息符合预期
- 因为功能缺失而失败

**测试立即通过了？** 你测试的是已有行为。修复测试。

**测试报错？** 修复错误，重新运行直到正确失败。

### GREEN — 最简代码 {#green-minimal-code}

编写最简单的代码使测试通过。不要多余。

**好：**
```python
def add(a, b):
    return a + b  # 不要多余
```

**坏：**
```python
def add(a, b):
    result = a + b
    logging.info(f"Adding {a} + {b} = {result}")  # 多余！
    return result
```

不要添加功能、重构其他代码或在测试之外进行"改进"。

**在 GREEN 阶段，作弊是允许的：**
- 硬编码返回值
- 复制粘贴
- 重复代码
- 跳过边缘情况

我们会在 REFACTOR 阶段修复。

### 验证 GREEN — 确保测试通过 {#verify-green-watch-it-pass}

**必须执行。**

```bash
# 运行特定的测试
pytest tests/test_feature.py::test_specific_behavior -v

# 然后运行所有测试以检查回归
pytest tests/ -q
```

确认：
- 测试通过
- 其他测试仍能通过
- 输出干净（无错误、无警告）

**测试失败？** 修复代码，而不是测试。

**其他测试失败？** 立即修复回归。

### REFACTOR — 清理 {#refactor-clean-up}

仅在通过绿色后：
- 消除重复
- 改进命名
- 抽取辅助函数
- 简化表达式

全程保持测试通过。不要添加行为。

**如果在重构过程中测试失败：** 立即撤销。采取更小的步骤。

### 重复 {#repeat}

下一个失败测试对应下一个行为。一次一个周期。

## 为什么顺序重要 {#why-order-matters}

**"我会先写代码，再写测试来验证它是否工作"**

代码之后编写的测试会立即通过。立即通过证明不了什么：
- 可能测试的是错误的东西
- 可能测试的是实现，而非行为
- 可能遗漏了你忘记的边缘情况
- 你从未见过它抓到 bug

测试优先迫使你看到测试失败，证明它确实在测试某些东西。

**"我已经手动测试了所有边缘情况"**

手动测试是临时的。你以为测试了所有情况，但：
- 没有记录测试了什么
- 代码变更后无法重新运行
- 在压力下容易忘记情况
- "我试的时候能工作" ≠ 全面

自动化测试是系统化的。它们每次都以相同方式运行。

**"删掉 X 小时的工作是浪费"**

沉没成本谬误。时间已经过去了。你现在的选择：
- 删除并用 TDD 重写（高信心）
- 保留它并在之后添加测试（低信心，很可能有 bug）

"浪费"是保留你不能信任的代码。

**"TDD 是教条主义的，务实意味着适应调整"**

TDD 恰恰是务实的：
- 在提交前发现 bug（比事后调试更快）
- 防止回归（测试立即捕捉破坏）
- 记录行为（测试展示如何使用代码）
- 支持重构（自由更改，测试捕捉破坏）

"务实"的捷径 = 在生产中调试 = 更慢。

**"之后测试达到相同目标——这是精神而非仪式"**

不。后写测试回答"这段代码做什么？"测试优先回答"这段代码应该做什么？"
后置测试会受到你实现方式的影响。你测试的是你构建的东西，而不是真正需要的东西。先写测试则能迫使你在实现之前发现边界情况。

## 常见借口 {#common-rationalizations}

| 借口 | 现实 |
|--------|---------|
| “太简单了，不用测” | 简单代码也会出问题。写个测试只需30秒。 |
| “我之后再测” | 测试立即通过说明不了任何问题。 |
| “后写测试也能达到同样目的” | 后写测试 = “这段代码是干什么的？” 先写测试 = “这段代码应该干什么？” |
| “已经手动测过了” | 临时测试 ≠ 系统测试。没有记录，无法重跑。 |
| “删掉X小时的工作太浪费了” | 沉没成本谬误。保留未经验证的代码就是技术债。 |
| “先留着当参考，再写测试” | 你会去改它。那还是后写测试。删掉就是删掉。 |
| “需要先探索一下” | 可以。探索完扔掉，从TDD开始。 |
| “测试难写 = 设计不清晰” | 听测试的。难测 = 难用。 |
| “TDD会拖慢我” | TDD比调试快。务实 = 先写测试。 |
| “手动测试更快” | 手动测试无法验证边界情况。每次改动你都得重新测。 |
| “现有代码没有测试” | 你正在改进它。为你改动的代码添加测试。 |

## 危险信号 —— 停下并重来 {#red-flags-stop-and-start-over}

如果你发现自己做了以下任何一件事，删掉代码，用TDD重新开始：

- 先写代码，后写测试
- 实现之后才写测试
- 测试第一次运行就通过
- 无法解释测试为什么失败
- 测试“之后”再补
- 找借口“就这一次”
- “我已经手动测过了”
- “后写测试也能达到同样目的”
- “先留着当参考”或“改改现有代码”
- “已经花了X小时，删掉太浪费”
- “TDD太教条，我这是务实”
- “这次不一样，因为……”

**所有这些都意味着：删掉代码，用TDD重来。**

## 验证清单 {#verification-checklist}

在标记工作完成之前：

- [ ] 每个新函数/方法都有测试
- [ ] 在实现之前，亲眼看到每个测试失败
- [ ] 每个测试因预期原因失败（功能缺失，而非拼写错误）
- [ ] 编写最简代码使每个测试通过
- [ ] 所有测试通过
- [ ] 输出干净（无错误、无警告）
- [ ] 测试使用真实代码（仅当无法避免时才用mock）
- [ ] 覆盖了边界情况和错误

不能勾选所有项？你跳过了TDD。重来。

## 卡住时怎么办 {#when-stuck}

| 问题 | 解决方案 |
|---------|----------|
| 不知道如何测试 | 写出你期望的API。先写断言。问用户。 |
| 测试太复杂 | 设计太复杂。简化接口。 |
| 必须mock一切 | 代码耦合太紧。使用依赖注入。 |
| 测试设置太庞大 | 提取辅助函数。还是复杂？简化设计。 |

## Hermes Agent 集成 {#hermes-agent-integration}

### 运行测试 {#running-tests}

使用 `terminal` 工具在每一步运行测试：

```python
# RED — 验证失败
terminal("pytest tests/test_feature.py::test_name -v")

# GREEN — 验证通过
terminal("pytest tests/test_feature.py::test_name -v")

# 完整套件 — 验证无回归
terminal("pytest tests/ -q")
```

### 配合 delegate_task {#with-delegatetask}

当派发子Agent进行实现时，在目标中强制使用TDD：
```python
delegate_task(
    goal="使用严格的 TDD 实现 [功能]",
    context="""
    遵循测试驱动开发技能：
    1. 首先编写会失败的测试
    2. 运行测试，确认它失败
    3. 编写最简代码使其通过
    4. 运行测试，确认它通过
    5. 如有需要则重构
    6. 提交

    项目测试命令：pytest tests/ -q
    项目结构：[描述相关文件]
    """,
    toolsets=['terminal', 'file']
)
```

### 配合 systematic-debugging {#with-systematic-debugging}

发现 Bug？先编写能复现它的失败测试。遵循 TDD 循环。该测试既证明修复有效，又防止回归。

永远不要在无测试的情况下修复 Bug。

## 测试反模式 {#testing-anti-patterns}

- **测试 mock 行为而非真实行为** —— mock 应验证交互，而非替代被测系统
- **测试实现细节** —— 测试行为/结果，而非内部方法调用
- **只测快乐路径** —— 始终测试边界情况、错误和边界值
- **脆弱的测试** —— 测试应验证行为，而非结构；重构不应破坏它们

## 最终规则 {#final-rule}

```
生产代码 → 测试已存在且先失败
否则 → 不是 TDD
```

未经用户明确许可，不得例外。
