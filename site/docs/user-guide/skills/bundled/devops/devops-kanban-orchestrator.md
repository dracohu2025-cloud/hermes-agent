---
title: "看板编排器"
sidebar_label: "看板编排器"
description: "分解剧本 + 专家名册约定 + 反诱惑规则，用于编排器角色通过看板路由工作"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 看板编排器 {#kanban-orchestrator}

分解剧本 + 专家名册约定 + 反诱惑规则，用于编排器角色通过看板路由工作。“不要自己动手做”规则和基本生命周期会自动注入到每个看板工作者的系统提示中；当你专门扮演编排器角色时，本技能是更深入的剧本。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/kanban-orchestrator` |
| 版本 | `2.0.0` |
| 标签 | `kanban`、`multi-agent`、`orchestration`、`routing` |
| 相关技能 | [`kanban-worker`](/user-guide/skills/bundled/devops/devops-kanban-worker) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 看板编排器 — 分解剧本 {#kanban-orchestrator-decomposition-playbook}

> **核心工作者生命周期**（包括 `kanban_create` 扇出模式以及“分解，不执行”规则）通过 `KANBAN_GUIDANCE` 系统提示块自动注入到每个看板流程中。本技能是当你作为编排器角色、全部工作就是路由时的更深入剧本。

## 何时使用看板（而不是直接干活） {#when-to-use-the-board-vs-just-doing-the-work}

当以下任一条件成立时，创建看板任务：

1. **需要多个专家。** 研究 + 分析 + 写作是三个角色。
2. **工作应能在崩溃或重启后存活。** 长时间运行、重复或重要的工作。
3. **用户可能想中途插话。** 任何步骤都支持人在回路。
4. **多个子任务可以并行执行。** 扇出以提高速度。
5. **预期需要审查/迭代。** 审查者角色对起草者输出进行循环。
6. **审计轨迹很重要。** 看板行永久保存在 SQLite 中。

如果*以上都不适用*——这是一个小型的一次性推理任务——请改用 `delegate_task` 或直接回答用户。

## 反诱惑规则 {#the-anti-temptation-rules}

你的工作描述是“路由，不执行”。强制执行该描述的规则：

- **不要自己动手执行工作。** 你的受限工具集通常甚至不包含用于实现的终端/文件/代码/网络。如果你发现自己“只是快速修复一下”——停下来，为合适的专家创建一个任务。
- **对于任何具体任务，创建一个看板任务并分配它。** 每次都这样做。
- **如果没有合适的专家，询问用户要创建哪个角色。** 不要默认自己动手，认为“差不多就行”。
- **分解、路由、总结——这就是全部工作。**

## 标准专家名册（约定） {#the-standard-specialist-roster-convention}

除非用户的设置中有自定义角色，否则假定存在以下角色。根据用户实际拥有的进行调整——如果不确定，请询问。

| 角色 | 职责 | 典型工作空间 |
|---|---|---|
| `researcher` | 阅读资料、收集事实、撰写发现 | `scratch` |
| `analyst` | 综合、排序、去重。消费多个 `researcher` 的输出 | `scratch` |
| `writer` | 以用户的语气起草散文 | `scratch` 或 `dir:` 进入他们的 Obsidian 仓库 |
| `reviewer` | 阅读输出、留下发现、把关批准 | `scratch` |
| `backend-eng` | 编写服务端代码 | `worktree` |
| `frontend-eng` | 编写客户端代码 | `worktree` |
| `ops` | 运行脚本、管理服务、处理部署 | `dir:` 进入运维脚本仓库 |
| `pm` | 编写规格说明、验收标准 | `scratch` |
## 分解剧本 {#decomposition-playbook}

### 步骤 1 — 理解目标 {#step-1-understand-the-goal}

如果目标不明确，请提出澄清性问题。提问成本很低，但派错舰队代价高昂。

### 步骤 2 — 勾勒任务图 {#step-2-sketch-the-task-graph}

在创建任何内容之前，先大声（在给用户的回复中）草拟任务图。例如，针对“分析我们是否应该迁移到 Postgres”：

```
T1  researcher        research: Postgres cost vs current
T2  researcher        research: Postgres performance vs current
T3  analyst           synthesize migration recommendation       parents: T1, T2
T4  writer            draft decision memo                       parents: T3
```

向用户展示此图。在创建任何内容之前，让他们纠正。

### 步骤 3 — 创建任务并建立关联 {#step-3-create-tasks-and-link}

```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="researcher",
    body="Compare estimated infrastructure costs, migration costs, and ongoing ops costs over a 3-year window. Sources: AWS/GCP pricing, team time estimates, current Postgres bills from peers.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="researcher",
    body="Compare query latency, throughput, and scaling characteristics at our expected data volume (~500GB, 10k QPS peak). Sources: benchmark papers, public case studies, pgbench results if easy.",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="analyst",
    body="Read the findings from T1 (cost) and T2 (performance). Produce a 1-page recommendation with explicit trade-offs and a go/no-go call.",
    parents=[t1, t2],
)["task_id"]

t4 = kanban_create(
    title="draft decision memo",
    assignee="writer",
    body="Turn the analyst's recommendation into a 2-page memo for the CTO. Match the tone of previous decision memos in the team's knowledge base.",
    parents=[t3],
)["task_id"]
```

`parents=[...]` 控制任务晋升——子任务会一直停留在 `todo` 状态，直到所有父任务都达到 `done` 状态，然后自动晋升为 `ready`。无需手动协调；调度器和依赖引擎会处理这一切。

### 步骤 4 — 完成你自己的任务 {#step-4-complete-your-own-task}

如果你自己作为一个任务被创建（例如，`planner` 角色被分配了 `T0: "investigate Postgres migration"`），请用你创建的内容摘要将其标记为完成：

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 researchers parallel, 1 analyst on their outputs, 1 writer on the recommendation",
    metadata={
        "task_graph": {
            "T1": {"assignee": "researcher", "parents": []},
            "T2": {"assignee": "researcher", "parents": []},
            "T3": {"assignee": "analyst", "parents": ["T1", "T2"]},
            "T4": {"assignee": "writer", "parents": ["T3"]},
        },
    },
)
```

### 步骤 5 — 向用户报告 {#step-5-report-back-to-the-user}

用通俗的语言告诉他们你创建了什么：

> 我已排入 4 个任务：
> - **T1**（研究员）：成本对比
> - **T2**（研究员）：性能对比，与 T1 并行
> - **T3**（分析师）：综合 T1 + T2 形成建议
> - **T4**（写手）：将 T3 转化为 CTO 备忘录
>
> 调度器现在会开始处理 T1 和 T2。T3 会在两者都完成后启动。T4 完成后你会收到一个网关通知。使用仪表盘或 `hermes kanban tail &lt;id&gt;` 来跟踪进度。
## 常见模式 {#common-patterns}

**扇出 + 扇入（研究 → 综合）：** N 个 `researcher` 任务（无父任务），一个 `analyst` 任务（以所有 researcher 为父任务）。

**带门控的流水线：** `pm → backend-eng → reviewer`。每个阶段的 `parents=[previous_task]`。Reviewer 可以阻塞或完成；如果 reviewer 阻塞，操作员通过反馈和重新生成来解除阻塞。

**同角色队列：** 50 个任务，全部分配给 `translator`，彼此无依赖关系。调度器串行处理——translator 按优先级顺序处理，在自己的记忆中积累经验。

**人在回路：** 任何任务都可以调用 `kanban_block()` 等待输入。调度器在 `/unblock` 后重新生成。评论线程携带完整的上下文。

## 常见陷阱 {#pitfalls}

**重新分配 vs. 新建任务。** 如果 reviewer 阻塞并提示“需要修改”，请从 reviewer 的任务创建一个新任务并链接——不要用严厉的眼神重新运行同一个任务。新任务会分配给原始实现者的角色。

**链接的参数顺序。** `kanban_link(parent_id=..., child_id=...)` —— 父任务在前。顺序搞反会把错误的任务降级为 `todo`。

**如果图的形状取决于中间结果，不要预先创建整个图。** 如果 T3 的结构取决于 T1 和 T2 的发现，让 T3 作为一个“综合发现”的任务存在，其第一步是读取父任务的交接信息并规划剩余部分。编排器可以生成编排器。

**租户继承。** 如果环境中设置了 `HERMES_TENANT`，请在每次 `kanban_create` 调用时传入 `tenant=os.environ.get("HERMES_TENANT")`，以便子任务保持在同一个命名空间中。
