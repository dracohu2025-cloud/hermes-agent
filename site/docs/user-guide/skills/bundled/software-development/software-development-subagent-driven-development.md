---
title: "Subagent Driven Development — 通过 delegate_task 子 Agent 执行计划（两阶段审查）"
sidebar_label: "Subagent Driven Development"
description: "通过 delegate_task 子 Agent 执行计划（两阶段审查）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Subagent Driven Development {#subagent-driven-development}

通过 delegate_task 子 Agent 执行计划（两阶段审查）。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/subagent-driven-development` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可证 | MIT |
| 标签 | `delegation`, `subagent`, `implementation`, `workflow`, `parallel` |
| 相关技能 | [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans), [`requesting-code-review`](/user-guide/skills/bundled/software-development/software-development-requesting-code-review), [`test-driven-development`](/user-guide/skills/bundled/software-development/software-development-test-driven-development) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="subagent-driven-development"></a>
# Subagent-Driven Development

## 概述 {#overview}

通过为每个任务分配全新的子 Agent 并执行系统性的两阶段审查，来执行实现计划。

**核心原则：** 每个任务使用全新的子 Agent + 两阶段审查（先规范后质量）= 高质量、快速迭代。

## 何时使用 {#when-to-use}

在以下情况下使用此技能：
- 你有一个实现计划（来自 writing-plans 技能或用户需求）
- 任务大多是独立的
- 质量和规范合规性很重要
- 你希望在任务之间进行自动审查

**与手动执行相比：**
- 每个任务都有全新的上下文（不会因累积状态而产生混淆）
- 自动审查流程能及早发现问题
- 对所有任务进行一致的质量检查
- 子 Agent 可以在开始工作前提问

## 流程 {#the-process}

### 1. 读取并解析计划 {#1-read-and-parse-plan}

读取计划文件。预先提取所有任务及其完整文本和上下文。创建一个待办事项列表：

```python
# 读取计划
read_file("docs/plans/feature-plan.md")

# 创建包含所有任务的待办事项列表
todo([
    {"id": "task-1", "content": "创建包含 email 字段的 User 模型", "status": "pending"},
    {"id": "task-2", "content": "添加密码哈希工具", "status": "pending"},
    {"id": "task-3", "content": "创建登录端点", "status": "pending"},
])
```

**关键点：** 只读取计划一次。提取所有内容。不要让子 Agent 读取计划文件——直接将完整的任务文本提供在上下文中。

### 2. 每个任务的工作流程 {#2-per-task-workflow}

对于计划中的每个任务：

#### 步骤 1：调度实现子 Agent {#step-1-dispatch-implementer-subagent}

使用完整的上下文调用 `delegate_task`：

```python
delegate_task(
    goal="实现任务 1：创建包含 email 和 password_hash 字段的 User 模型",
    context="""
    计划中的任务：
    - 创建：src/models/user.py
    - 添加 User 类，包含 email (str) 和 password_hash (str) 字段
    - 使用 bcrypt 进行密码哈希
    - 包含 __repr__ 用于调试

    遵循 TDD：
    1. 在 tests/models/test_user.py 中编写失败的测试
    2. 运行：pytest tests/models/test_user.py -v（验证失败）
    3. 编写最小实现
    4. 运行：pytest tests/models/test_user.py -v（验证通过）
    5. 运行：pytest tests/ -q（验证无回归）
    6. 提交：git add -A && git commit -m "feat: add User model with password hashing"

    项目上下文：
    - Python 3.11，Flask 应用位于 src/app.py
    - 现有模型位于 src/models/
    - 测试使用 pytest，从项目根目录运行
    - bcrypt 已在 requirements.txt 中
    """,
    toolsets=['terminal', 'file']
)
```
#### 步骤 2：分派规范合规审查员 {#step-2-dispatch-spec-compliance-reviewer}

实现者完成后，对照原始规范进行验证：

```python
delegate_task(
    goal="审查实现是否与计划中的规范一致",
    context="""
    原始任务规范：
    - 创建 src/models/user.py，包含 User 类
    - 字段：email (str), password_hash (str)
    - 使用 bcrypt 进行密码哈希
    - 包含 __repr__

    检查项：
    - [ ] 规范中的所有需求都已实现？
    - [ ] 文件路径与规范一致？
    - [ ] 函数签名与规范一致？
    - [ ] 行为符合预期？
    - [ ] 没有添加额外内容（无范围蔓延）？

    输出：PASS 或列出需要修复的具体规范差距。
    """,
    toolsets=['file']
)
```

**如果发现规范问题：** 修复差距，然后重新运行规范审查。仅在符合规范时继续。

#### 步骤 3：分派代码质量审查员 {#step-3-dispatch-code-quality-reviewer}

规范合规通过后：

```python
delegate_task(
    goal="审查任务 1 实现的代码质量",
    context="""
    待审查文件：
    - src/models/user.py
    - tests/models/test_user.py

    检查项：
    - [ ] 遵循项目约定和风格？
    - [ ] 适当的错误处理？
    - [ ] 变量/函数命名清晰？
    - [ ] 充分的测试覆盖？
    - [ ] 没有明显的 bug 或遗漏的边界情况？
    - [ ] 没有安全问题？

    输出格式：
    - 关键问题：[必须修复后才能继续]
    - 重要问题：[应该修复]
    - 次要问题：[可选]
    - 结论：APPROVED 或 REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**如果发现质量问题：** 修复问题，重新审查。仅在批准后继续。

#### 步骤 4：标记完成 {#step-4-mark-complete}

```python
todo([{"id": "task-1", "content": "创建包含 email 字段的 User 模型", "status": "completed"}], merge=True)
```

### 3. 最终审查 {#3-final-review}

所有任务完成后，分派一个最终集成审查员：

```python
delegate_task(
    goal="审查整个实现的一致性和集成问题",
    context="""
    计划中的所有任务已完成。审查完整实现：
    - 所有组件是否协同工作？
    - 任务之间是否存在不一致？
    - 所有测试是否通过？
    - 是否准备好合并？
    """,
    toolsets=['terminal', 'file']
)
```

### 4. 验证并提交 {#4-verify-and-commit}

```bash
# 运行完整测试套件
pytest tests/ -q

# 审查所有更改
git diff --stat

# 如果需要，最终提交
git add -A && git commit -m "feat: 完成 [功能名称] 实现"
```

## 任务粒度 {#task-granularity}

**每个任务 = 2-5 分钟的专注工作。**

**太大：**
- "实现用户认证系统"

**合适大小：**
- "创建包含 email 和 password 字段的 User 模型"
- "添加密码哈希函数"
- "创建登录端点"
- "添加 JWT 令牌生成"
- "创建注册端点"

## 红线——绝不要做这些事 {#red-flags-never-do-these}

- 没有计划就开始实现
- 跳过审查（规范合规或代码质量）
- 带着未修复的关键/重要问题继续
- 为操作相同文件的任务分派多个实现子 Agent
- 让子 Agent 读取计划文件（改为在上下文中提供完整文本）
- 跳过场景设置上下文（子 Agent 需要理解任务所处的位置）
- 忽略子 Agent 的问题（在让他们继续之前先回答）
- 在规范合规上接受"差不多就行"
- 跳过审查循环（审查员发现问题 → 实现者修复 → 再次审查）
- 让实现者自我审查替代实际审查（两者都需要）
- **在规范合规未通过 PASS 之前开始代码质量审查**（顺序错误）
- 在任一审查仍有未解决问题时移动到下一个任务
## 处理问题 {#handling-issues}

### 如果子 Agent 提问 {#if-subagent-asks-questions}

- 清晰完整地回答
- 必要时提供额外上下文
- 不要催促它们直接进入实现

### 如果审查者发现问题 {#if-reviewer-finds-issues}

- 实现子 Agent（或新子 Agent）修复问题
- 审查者再次审查
- 重复直到通过
- 不要跳过重新审查

### 如果子 Agent 任务失败 {#if-subagent-fails-a-task}

- 派遣一个新的修复子 Agent，并附带关于哪里出错的明确指示
- 不要在控制器会话中手动修复（上下文污染）

## 效率说明 {#efficiency-notes}

**为什么每个任务使用全新的子 Agent：**
- 防止累积状态导致的上下文污染
- 每个子 Agent 获得干净、聚焦的上下文
- 不会因先前任务的代码或推理而产生混淆

**为什么采用两阶段审查：**
- 规格审查尽早发现过度/不足构建
- 质量审查确保实现质量良好
- 在问题跨任务累积之前就将其捕获

**成本权衡：**
- 更多子 Agent 调用（每个任务：实现者 + 2 个审查者）
- 但能尽早发现问题（比后期调试累积问题更便宜）

## 与其他技能的集成 {#integration-with-other-skills}

### 与 writing-plans 集成 {#with-writing-plans}

本技能执行由 writing-plans 技能创建的计划：
1. 用户需求 → writing-plans → 实现计划
2. 实现计划 → subagent-driven-development → 可工作代码

### 与 test-driven-development 集成 {#with-test-driven-development}

实现子 Agent 应遵循 TDD：
1. 先编写会失败的测试
2. 实现最简代码
3. 验证测试通过
4. 提交

在每个实现者上下文中包含 TDD 指令。

### 与 requesting-code-review 集成 {#with-requesting-code-review}

两阶段审查过程本身就是代码审查。对于最终集成审查，使用 requesting-code-review 技能的审查维度。

### 与 systematic-debugging 集成 {#with-systematic-debugging}

如果子 Agent 在实现过程中遇到错误：
1. 遵循 systematic-debugging 流程
2. 修复前先找到根本原因
3. 编写回归测试
4. 继续实现

## 示例工作流 {#example-workflow}

```
[读取计划: docs/plans/auth-feature.md]
[创建包含 5 个任务的待办列表]

--- 任务 1: 创建用户模型 ---
[派遣实现子 Agent]
  实现者: "邮箱需要唯一吗？"
  你: "是的，邮箱必须唯一"
  实现者: 已实现，3/3 测试通过，已提交。

[派遣规格审查者]
  规格审查者: ✅ 通过 — 所有需求均已满足

[派遣质量审查者]
  质量审查者: ✅ 批准 — 代码整洁，测试良好

[标记任务 1 完成]

--- 任务 2: 密码哈希 ---
[派遣实现子 Agent]
  实现者: 无问题，已实现，5/5 测试通过。

[派遣规格审查者]
  规格审查者: ❌ 缺失: 密码强度验证（规格要求"至少 8 个字符"）

[实现者修复]
  实现者: 已添加验证，7/7 测试通过。

[再次派遣规格审查者]
  规格审查者: ✅ 通过

[派遣质量审查者]
  质量审查者: 重要: 魔法数字 8，应提取为常量
  实现者: 已提取 MIN_PASSWORD_LENGTH 常量
  质量审查者: ✅ 批准

[标记任务 2 完成]

...（对所有任务继续）

[所有任务完成后: 派遣最终集成审查者]
[运行完整测试套件: 全部通过]
[完成!]
```
## 记住 {#remember}

```
每个任务使用新的子 Agent
每次都要进行两阶段审查
规范优先
代码质量第二
绝不跳过审查
尽早发现问题
```

**质量不是偶然的。它是系统化流程的结果。**

## 延伸阅读（相关时加载） {#further-reading-load-when-relevant}

当编排涉及大量上下文使用、长审查循环或复杂验证检查点时，请加载这些参考资料以获取具体指导：

- **`references/context-budget-discipline.md`** — 四级上下文退化模型（PEAK / GOOD / DEGRADING / POOR）、随上下文窗口大小调整的读取深度规则，以及静默退化的早期预警信号。当运行会明显消耗大量上下文时（多阶段计划、多个子 Agent、大型工件），请加载此文档。
- **`references/gates-taxonomy.md`** — 四种标准门类型（预检、修订、升级、中止），包含行为、恢复方式和示例。在设计或审查任何具有验证检查点的工作流时加载此文档——明确使用这些术语，使每个门都有定义的入口、失败行为和恢复规则。

两份参考资料均改编自 gsd-build/get-shit-done（MIT © 2025 Lex Christopherson）。
