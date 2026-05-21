---
title: "子Agent驱动开发——通过 delegate_task 子Agent执行计划（两阶段审查）"
sidebar_label: "子Agent驱动开发"
description: "通过 delegate_task 子Agent执行计划（两阶段审查）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="subagent-driven-development"></a>
# 子Agent驱动开发

通过 delegate_task 子Agent执行计划（两阶段审查）。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/subagent-driven-development` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `delegation`, `subagent`, `implementation`, `workflow`, `parallel` |
| 相关技能 | [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans), [`requesting-code-review`](/user-guide/skills/bundled/software-development/software-development-requesting-code-review), [`test-driven-development`](/user-guide/skills/bundled/software-development/software-development-test-driven-development) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 触发此技能时加载的完整技能定义。这是技能激活时Agent看到的指令。
:::

# 子Agent驱动开发

<a id="overview"></a>
## 概览

通过为每个任务调度全新的子Agent，并配合系统的两阶段审查，来执行实施计划。

**核心原则：** 每个任务使用新的子Agent + 两阶段审查（先规范后质量）= 高质量、快速迭代。

<a id="when-to-use"></a>
## 何时使用

在以下情况使用此技能：
- 你已拥有实施计划（来自 writing-plans 技能或用户需求）
- 任务基本相互独立
- 质量和规范遵从性很重要
- 你希望在任务之间进行自动审查

**与手动执行的对比：**
- 每个任务有新的上下文（避免累积状态的混乱）
- 自动审查过程能尽早发现问题
- 对所有任务进行一致的质量检查
- 子Agent可以在开始工作前提问

<a id="the-process"></a>
## 流程

<a id="1-read-and-parse-plan"></a>
### 1. 读取并解析计划

读取计划文件。提前提取所有任务的完整文本和上下文。创建待办列表：

```python
# Read the plan
read_file("docs/plans/feature-plan.md")

# Create todo list with all tasks
todo([
    {"id": "task-1", "content": "Create User model with email field", "status": "pending"},
    {"id": "task-2", "content": "Add password hashing utility", "status": "pending"},
    {"id": "task-3", "content": "Create login endpoint", "status": "pending"},
])
```

**要点：** 只读取计划一次。提取所有内容。不要让子Agent读取计划文件——直接在上下文中提供完整的任务文本。

<a id="2-per-task-workflow"></a>
### 2. 每个任务的工作流

对于计划中的每个任务：

<a id="step-1-dispatch-implementer-subagent"></a>
#### 步骤 1：调度执行子Agent

使用 `delegate_task` 并提供完整的上下文：

```python
delegate_task(
    goal="Implement Task 1: Create User model with email and password_hash fields",
    context="""
    TASK FROM PLAN:
    - Create: src/models/user.py
    - Add User class with email (str) and password_hash (str) fields
    - Use bcrypt for password hashing
    - Include __repr__ for debugging

    FOLLOW TDD:
    1. Write failing test in tests/models/test_user.py
    2. Run: pytest tests/models/test_user.py -v (verify FAIL)
    3. Write minimal implementation
    4. Run: pytest tests/models/test_user.py -v (verify PASS)
    5. Run: pytest tests/ -q (verify no regressions)
    6. Commit: git add -A && git commit -m "feat: add User model with password hashing"

    PROJECT CONTEXT:
    - Python 3.11, Flask app in src/app.py
    - Existing models in src/models/
    - Tests use pytest, run from project root
    - bcrypt already in requirements.txt
    """,
    toolsets=['terminal', 'file']
)
```
<a id="step-2-dispatch-spec-compliance-reviewer"></a>
#### 步骤 2：分派规范符合性审查者

实现者完成后，对照原始规范进行验证：

```python
delegate_task(
    goal="Review if implementation matches the spec from the plan",
    context="""
    ORIGINAL TASK SPEC:
    - Create src/models/user.py with User class
    - Fields: email (str), password_hash (str)
    - Use bcrypt for password hashing
    - Include __repr__

    CHECK:
    - [ ] All requirements from spec implemented?
    - [ ] File paths match spec?
    - [ ] Function signatures match spec?
    - [ ] Behavior matches expected?
    - [ ] Nothing extra added (no scope creep)?

    OUTPUT: PASS or list of specific spec gaps to fix.
    """,
    toolsets=['file']
)
```

**如果发现规范问题：** 修复差距，然后重新运行规范审查。只有符合规范后才能继续。

<a id="step-3-dispatch-code-quality-reviewer"></a>
#### 步骤 3：分派代码质量审查者

规范符合性通过后：

```python
delegate_task(
    goal="Review code quality for Task 1 implementation",
    context="""
    FILES TO REVIEW:
    - src/models/user.py
    - tests/models/test_user.py

    CHECK:
    - [ ] Follows project conventions and style?
    - [ ] Proper error handling?
    - [ ] Clear variable/function names?
    - [ ] Adequate test coverage?
    - [ ] No obvious bugs or missed edge cases?
    - [ ] No security issues?

    OUTPUT FORMAT:
    - Critical Issues: [must fix before proceeding]
    - Important Issues: [should fix]
    - Minor Issues: [optional]
    - Verdict: APPROVED or REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**如果发现质量问题：** 修复问题，重新审查。只有批准后才能继续。

<a id="step-4-mark-complete"></a>
#### 步骤 4：标记完成

```python
todo([{"id": "task-1", "content": "Create User model with email field", "status": "completed"}], merge=True)
```

<a id="3-final-review"></a>
### 3. 最终审查

所有任务完成后，分派最终集成审查者：

```python
delegate_task(
    goal="Review the entire implementation for consistency and integration issues",
    context="""
    All tasks from the plan are complete. Review the full implementation:
    - Do all components work together?
    - Any inconsistencies between tasks?
    - All tests passing?
    - Ready for merge?
    """,
    toolsets=['terminal', 'file']
)
```

<a id="4-verify-and-commit"></a>
### 4. 验证并提交

```bash
# Run full test suite
pytest tests/ -q

# Review all changes
git diff --stat

# Final commit if needed
git add -A && git commit -m "feat: complete [feature name] implementation"
```

<a id="task-granularity"></a>
## 任务粒度

**每个任务 = 2–5 分钟的专注工作。**

**太大：**
- "实现用户认证系统"

**合适大小：**
- "创建包含 email 和 password 字段的 User 模型"
- "添加密码哈希函数"
- "创建登录端点"
- "添加 JWT 令牌生成"
- "创建注册端点"

<a id="red-flags-never-do-these"></a>
## 红旗——绝不要做这些事

- 在没有计划的情况下开始实现
- 跳过审查（规范符合性审查或代码质量审查）
- 带着未修复的关键/重要问题继续
- 为操作相同文件的任务分派多个实现子 Agent
- 让子 Agent 读取计划文件（应改为在 context 中提供完整文本）
- 跳过场景设置上下文（子 Agent 需要理解任务所处的位置）
- 忽略子 Agent 的问题（在让它们继续之前先回答）
- 对规范符合性接受“差不多就行”
- 跳过审查循环（审查者发现问题→实现者修复→再次审查）
- 让实现者自我审查替代实际审查（两者都需要）
- **在规范符合性未通过之前就开始代码质量审查**（顺序错误）
- 在任一审查仍有未解决问题时移到下一个任务
<a id="handling-issues"></a>
## 处理问题

<a id="if-subagent-asks-questions"></a>
### 如果子 Agent 提问

- 清晰完整地回答
- 必要时提供额外上下文
- 不要催促他们直接实现

<a id="if-reviewer-finds-issues"></a>
### 如果审查者发现问题

- 实现子 Agent（或新启用的一个）修复问题
- 审查者再次审查
- 重复直到通过
- 不要跳过重新审查

<a id="if-subagent-fails-a-task"></a>
### 如果子 Agent 任务失败

- 派遣一个新的修复子 Agent，并明确说明哪里出了问题
- 不要尝试在主控会话中手动修复（会导致上下文污染）

<a id="efficiency-notes"></a>
## 效率说明

**为什么每个任务使用全新的子 Agent：**
- 防止累积状态导致的上下文污染
- 每个子 Agent 获得干净、聚焦的上下文
- 避免因先前任务的代码或推理而产生混淆

**为什么采用两阶段审查：**
- 规格审查尽早发现过度/不足构建
- 质量审查确保实现质量良好
- 在问题跨任务叠加前就发现它们

**成本权衡：**
- 子 Agent 调用次数更多（每个任务有一个实现者 + 两个审查者）
- 但能尽早发现错误（比后期调试叠加的问题更便宜）

<a id="integration-with-other-skills"></a>
## 与其他技能的集成

<a id="with-writing-plans"></a>
### 与 writing-plans 配合

本技能**执行**由 writing-plans 技能生成的计划：
1. 用户需求 → writing-plans → 实现计划
2. 实现计划 → subagent-driven-development → 可运行代码

<a id="with-test-driven-development"></a>
### 与 test-driven-development 配合

实现子 Agent 应遵循 TDD：
1. 先编写会失败的测试
2. 实现最小代码
3. 验证测试通过
4. 提交

在每个实现者的上下文中包含 TDD 指令。

<a id="with-requesting-code-review"></a>
### 与 requesting-code-review 配合

两阶段审查过程本身就是代码审查。对于最终集成审查，使用 requesting-code-review 技能的审查维度。

<a id="with-systematic-debugging"></a>
### 与 systematic-debugging 配合

如果子 Agent 在实现过程中遇到 bug：
1. 遵循 systematic-debugging 流程
2. 修复前先找到根本原因
3. 编写回归测试
4. 继续实现

<a id="example-workflow"></a>
## 示例工作流

```
[读取计划: docs/plans/auth-feature.md]
[创建包含 5 个任务的待办列表]

--- 任务 1: 创建 User 模型 ---
[派遣实现子 Agent]
  实现者: "邮箱是否应该唯一？"
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
  规格审查者: ❌ 缺少：密码强度验证（规格要求"至少 8 个字符"）

[实现者修复]
  实现者: 添加了验证，7/7 测试通过。

[再次派遣规格审查者]
  规格审查者: ✅ 通过

[派遣质量审查者]
  质量审查者: 重要：魔法数字 8，应提取为常量
  实现者: 提取了 MIN_PASSWORD_LENGTH 常量
  质量审查者: ✅ 批准

[标记任务 2 完成]

... (继续对所有任务执行)

[所有任务完成后：派遣最终集成审查者]
[运行完整测试套件：全部通过]
[完成！]
```
<a id="remember"></a>
## Remember

```
Fresh subagent per task
Two-stage review every time
Spec compliance FIRST
Code quality SECOND
Never skip reviews
Catch issues early
```

**质量不是偶然的。它是系统化过程的结果。**

<a id="further-reading-load-when-relevant"></a>
## Further reading (load when relevant)

当编排涉及大量上下文使用、长审查循环或复杂验证检查点时，请按具体场景加载以下参考资料：

- **`references/context-budget-discipline.md`** — 四级上下文降级模型（PEAK / GOOD / DEGRADING / POOR），随上下文窗口大小调整的读取深度规则，以及静默降级的早期预警信号。当某个运行会明显消耗大量上下文（多阶段计划、多个 subagent、大型产物）时加载。
- **`references/gates-taxonomy.md`** — 四种标准关卡类型（Pre-flight、Revision、Escalation、Abort），包含行为、恢复方式和示例。当设计或审查任何含有验证检查点的工作流时加载——明确使用该术语，使每个关卡都有定义的进入条件、失败行为和恢复规则。

两个参考资料均改编自 gsd-build/get-shit-done（MIT © 2025 Lex Christopherson）。
