---
title: "看板编排器"
sidebar_label: "看板编排器"
description: "针对通过看板路由工作的编排器角色的分解手册 + 抗诱惑规则"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能 SKILL.md 自动生成。请编辑源 SKILL.md，而非此页面。 */}

<a id="kanban-orchestrator"></a>
# 看板编排器

针对通过看板路由工作的编排器角色的分解手册 + 抗诱惑规则。其中“不要自己动手做”规则和基本生命周期会自动注入到每个看板工人的系统提示中；这个技能是你专门扮演编排器角色时的深度手册。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/devops/kanban-orchestrator` |
| 版本 | `3.0.0` |
| 平台 | linux, macos, windows |
| 标签 | `kanban`、`multi-agent`、`编排`、`路由` |
| 相关技能 | [`kanban-worker`](/user-guide/skills/bundled/devops/devops-kanban-worker) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是技能触发时 Hermes 加载的完整技能定义。这是技能处于活动状态时 agent 看到的指令。
:::

<a id="kanban-orchestrator-decomposition-playbook"></a>
# 看板编排器 — 分解手册

> **核心工人生命周期**（包括 `kanban_create` 扇出模式和“分解，不要执行”规则）会通过 `KANBAN_GUIDANCE` 系统提示块自动注入到每个看板过程中。这个技能是你作为编排器角色（其全部工作就是路由）时的深度手册。

<a id="profiles-are-user-configured-not-a-fixed-roster"></a>
## 配置文件是用户配置的——不是固定的名单

Hermes 的配置差异很大。有些用户运行一个包揽一切的单一配置文件；有些运行一个小型集群（`docker-worker`、`cron-worker`）；有些运行他们自己命名的精选专家团队。**没有默认的专家名单**——编排器技能不知道这台机器上存在哪些配置文件。

在扇出之前，你必须基于实际存在的配置文件进行分解。调度器会静默地失败，无法生成未知的分配者名称——它不会自动纠正，不会建议，也没有后备方案。因此，在一台只有 `docker-worker` 的机器上，分配给 `researcher` 的卡片永远只会停留在 `ready` 状态。

**第 0 步：在规划之前发现可用的配置文件。**

使用以下方法之一：

- `hermes profile list` — 打印这台机器上配置的配置文件表。如果你有终端工具，请通过它运行；否则询问用户。
- `kanban_list(assignee="&lt;some-name&gt;")` — 检查单个名称是否有效。对于未知的分配者，返回空列表（而不是错误），因此这只能确认你已经在考虑的名称。
- **直接问用户。** “你设置了哪些配置文件？”当目标需要一个以上的专家时，这是一个很好的第一个回合。

将结果缓存在你的工作记忆中，以便在对话的其余部分使用。每轮都重新询问会浪费一次工具调用。

<a id="when-to-use-the-board-vs-just-doing-the-work"></a>
## 何时使用看板（而不是直接干活）

满足以下任一条件时创建看板任务：

1. **需要多个专家。** 研究 + 分析 + 写作是三个配置文件。
2. **工作应该能在崩溃或重启后存活。** 长时间运行、重复或重要的工作。
3. **用户可能想插话。** 任何步骤中都可能存在人类参与。
4. **多个子任务可以并行运行。** 为了速度而扇出。
5. **需要审查 / 迭代。** 审查者配置文件会对起草者的输出进行循环检查。
6. **审计追踪很重要。** 看板行会永久保存在 SQLite 中。
如果*以上都不适用*——这是一次性的小型推理任务——那么改用 `delegate_task`，或直接回答用户。

<a id="the-anti-temptation-rules"></a>
## 反诱惑规则

你的工作描述是“路由，不执行。”以下是强制执行这一原则的规则：

- **不要自己执行工作。** 你的受限工具集通常甚至不包含用于实现的终端/文件/代码/网页。如果你发现自己“只是快速修复一下”——停下，并为合适的专家创建一个任务。
- **对于任何具体任务，创建一个看板任务并分配给它。** 每次都这样。
- **在创建卡片之前拆分多任务流程。** 用户提示可能包含多个独立的工作流。首先提取这些流程，然后为每个流程创建一个卡片，而不是将不相关的工作打包到一个执行者卡片中。
- **并行运行独立的流程。** 如果两张卡片不需要彼此的输出，则保持它们不关联，以便调度器可以分发它们。仅连接真正的数据依赖关系。
- **切勿将依赖的工作创建为独立的就绪卡片。** 如果某张卡片必须等待另一张卡片，则在原始 `kanban_create` 调用中传递 `parents=[...]`。不要先创建它再稍后关联，也不要依赖正文中诸如“等待 T1”之类的话。
- **如果没有专家符合可用的角色，询问用户要创建哪个角色或使用哪个现有角色。** 不要发明角色名称；调度器会静默地丢弃未知的分配对象。
- **分解、路由和总结——这就是全部工作。**

<a id="decomposition-playbook"></a>
## 分解操作手册

<a id="step-1-understand-the-goal"></a>
### 第一步 — 理解目标

如果目标不明确，就提出澄清性问题。提问成本低；弄错任务群的代价高昂。

<a id="step-2-sketch-the-task-graph"></a>
### 第二步 — 绘制任务图

在创建任何内容之前，大声描述任务图（在你的回复中呈现给用户）。把每个具体的工作流当作一个候选卡片：

1. 从请求中提取任务流。
2. 将每个任务流映射到你在第零步发现的角色之一。如果某个任务流不适合任何现有角色，询问用户要使用哪个或创建哪个。
3. 决定每个任务流是独立的还是受另一个任务流的门控。
4. 创建独立的任务流作为没有父级链接的并行卡片。
5. 创建综合/审查/集成卡片，并添加对它们所依赖的任务流的父级链接。带有未完成父任务创建的子卡片以 `todo` 状态开始；调度器只有在所有父任务完成后才将其提升为 `ready` 状态。

以下是一些应该分发出去的提示示例（使用占位符角色名称——请替换为用户设置中存在的任何角色）：

- "构建一个应用" → 一张卡片给面向设计的角色负责产品/UI方向，一张或两张卡片给工程角色负责实现，再加上稍后的一张集成/审查卡片（如果用户有审查者角色）。
- "修复阻塞项并检查模型变体" → 一张实现卡片用于修复阻塞项，加上一张发现/研究卡片用于配置/源代码验证。最终审查者卡片可以依赖两者。
- "研究文档并实现" → 文档研究卡片可以与代码库探索卡片并行运行；实现仅在确实需要这些发现时才等待。
- "分析这个截图并找到相关代码" → 一张卡片给具备视觉能力的角色进行视觉分析，同时另一张卡片搜索代码库。
像 `"also"`、`"finally"` 或 `"and"` 这样的词语并不自动意味着依赖关系。它们通常表示“在汇报之前，确保这一点已涵盖”。仅当一张卡片无法启动直到另一张卡片的输出存在时，才关联任务。

在创建卡片之前向用户展示该图。允许他们纠正——包括哪个实际配置文件名称应拥有哪个泳道。

<a id="step-3-create-tasks-and-link"></a>
### 步骤 3 — 创建任务并关联

使用步骤0中的配置文件名称。下面的示例使用了占位符 `&lt;profile-A&gt;`、`&lt;profile-B&gt;`、`&lt;profile-C&gt;`——将其替换为用户实际拥有的内容。

```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="<profile-A>",  # whichever profile handles research on this setup
    body="Compare estimated infrastructure costs, migration costs, and ongoing ops costs over a 3-year window. Sources: AWS/GCP pricing, team time estimates, current Postgres bills from peers.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="<profile-A>",  # same profile, run in parallel
    body="Compare query latency, throughput, and scaling characteristics at our expected data volume (~500GB, 10k QPS peak). Sources: benchmark papers, public case studies, pgbench results if easy.",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="<profile-B>",  # whichever profile does synthesis/analysis
    body="Read the findings from T1 (cost) and T2 (performance). Produce a 1-page recommendation with explicit trade-offs and a go/no-go call.",
    parents=[t1, t2],
)["task_id"]

t4 = kanban_create(
    title="draft decision memo",
    assignee="<profile-C>",  # whichever profile drafts user-facing prose
    body="Turn the analyst's recommendation into a 2-page memo for the CTO. Match the tone of previous decision memos in the team's knowledge base.",
    parents=[t3],
)["task_id"]
```

`parents=[...]` 控制提升——子任务保持在 `todo` 状态，直到每个父任务都达到 `done`，然后自动提升为 `ready`。无需手动协调；调度器和依赖引擎会处理。

如果任务图存在依赖关系，请先创建父卡片，捕获返回的ID，并在子卡片的 `kanban_create` 调用中将这些ID包含到 `parents` 列表中。避免并行创建所有卡片后再关联它们；这会造成窗口期，使得调度器可能在输入存在之前就领取子任务。

<a id="step-4-complete-your-own-task"></a>
### 步骤 4 — 完成自己的任务

如果你自己是作为一个任务生成的（例如，一个规划者配置文件被分配了 `T0: "investigate Postgres migration"`），请将其标记为完成，并附上你所创建内容的摘要：

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 research lanes in parallel, 1 synthesis on their outputs, 1 prose draft on the recommendation",
    metadata={
        "task_graph": {
            "T1": {"assignee": "<profile-A>", "parents": []},
            "T2": {"assignee": "<profile-A>", "parents": []},
            "T3": {"assignee": "<profile-B>", "parents": ["T1", "T2"]},
            "T4": {"assignee": "<profile-C>", "parents": ["T3"]},
        },
    },
)
```
<a id="step-5-report-back-to-the-user"></a>
### 步骤 5 — 向用户汇报

用平实的语言告诉用户你创建了什么，并说出你实际使用的角色名称：

> 我已将 4 个任务加入队列：
> - **T1** (`&lt;profile-A&gt;`): 成本比较
> - **T2** (`&lt;profile-A&gt;`): 性能比较，与 T1 并行
> - **T3** (`&lt;profile-B&gt;`): 综合 T1 + T2 生成推荐方案
> - **T4** (`&lt;profile-C&gt;`): 将 T3 转换为 CTO 备忘录
>
> 调度器现在会拾取 T1 和 T2。T3 在两者都完成后启动。当 T4 完成时，你会收到网关通知。使用仪表盘或 `hermes kanban tail &lt;id&gt;` 来跟踪进度。

<a id="common-patterns"></a>
## 常见模式

**扇出 + 扇入（研究 → 综合）：** N 个无父任务的研究型卡片，一个综合卡片将这些研究卡片作为父任务。

**并行实施 + 验证：** 一个实施者卡片进行更改，同时一个探索/研究员卡片验证配置、文档或源码映射。一个审查卡片可以依赖于两者。不要仅仅因为用户在一句话里同时提到了两者，就让实施者去承担不相关的验证工作。

**带门控的管道：** `计划者 → 实施者 → 审查者`。每个阶段的 `parents=[previous_task]`。审查者可以阻止或完成；如果审查者阻止，操作员会提供反馈并重新生成。

**相同角色队列：** N 个任务，全部分配给同一个角色，任务之间无依赖关系。调度器会序列化处理——该角色会按优先级顺序处理它们，并在其自身记忆中积累经验。

**人在回路：** 任何任务都可以通过 `kanban_block()` 等待输入。调度器在 `/unblock` 后重新生成。评论线程承载了完整的上下文。

<a id="pitfalls"></a>
## 常见陷阱

**编造不存在的角色名称。** 调度器会静默地无法生成未知的受让人——卡片会永远停留在 `ready` 状态。始终从步骤 0 发现的角色中分配；如果不确定，询问用户。

**将独立的工作流捆绑到一张卡片中。** 如果用户要求两个独立的结果，创建两张卡片。例如："修复阻塞并检查模型变体" 不是一个修复任务；为修复创建一张修复/工程师卡片，为变体检查创建一张探索/研究员卡片，然后（可选地）对两者进行门控审查。

**因为措辞而过度链接。** "最后检查 X" 可能仍然可以与实施并行，如果 X 是静态配置、文档或源码发现。仅当检查依赖于实施结果时，才将其链接在实施之后。

**忘记依赖链接。** 如果任务图是 `research -> implement -> review`，不要将所有任务创建为独立的 ready 卡片。使用父链接，以便实施/审查在其输入存在之前不能运行。

**重新分配 vs. 新任务。** 如果审查者以"需要更改"为由阻止，则创建一个与审查者任务关联的**新**任务——不要用严厉的表情重新运行相同的任务。新任务分配给原来的实施者角色。

**链接的参数顺序。** `kanban_link(parent_id=..., child_id=...)` ——父任务在前。搞混顺序会将错误的任务降级为 `todo`。

**如果任务的形状取决于中间发现，不要预先创建整个图。** 如果 T3 的结构取决于 T1 和 T2 的发现，让 T3 作为一个"综合发现"任务存在，其自身的第一步是读取父任务的交接内容并规划后续。编排者可以再生成编排者。
**租户继承。** 如果环境中设置了 `HERMES_TENANT`，请在每次调用 `kanban_create` 时传入 `tenant=os.environ.get("HERMES_TENANT")`，以便子任务保持在同一个命名空间中。

<a id="recovering-stuck-workers"></a>
## 恢复卡住的 Worker

当某个 worker 配置文件持续崩溃、产生幻觉，或因自身错误（通常是：模型错误、缺少技能、凭据损坏）而被阻塞时，看板仪表盘会为该任务标记一个 ⚠ 徽章，并在抽屉中打开一个**恢复**部分。提供三种主要操作：

1.  **回收**（或 `hermes kanban reclaim &lt;task_id&gt;`）—— 立即中止正在运行的 worker，并将任务重置为 `ready` 状态。现有的认领 TTL 约为 15 分钟；这是快速恢复路径。
2.  **重新分配**（或 `hermes kanban reassign &lt;task_id&gt; &lt;new-profile&gt; --reclaim`）—— 将任务切换到另一个配置文件（该配置在当前设置上存在），并让调度器使用新的 worker 来接手。
3.  **更改配置文件模型** —— 仪表盘会打印一个复制粘贴提示，内容为 `hermes -p &lt;profile&gt; model`，因为配置文件存储在磁盘上；在终端中编辑它，然后执行回收操作，以使用新模型重试。

当 worker 的 `kanban_complete(created_cards=[...])` 认领中包含不存在或并非由该 worker 配置文件创建的卡片 ID（门控会阻止完成），或者自由格式的摘要引用了无法解析的 `t_&lt;hex&gt;` ID（建议性文本扫描，非阻塞）时，任务上会出现幻觉警告。这两种情况都会产生审计事件，即使在执行恢复操作后这些事件仍然存在 —— 审计轨迹会保留下来，以便进行调试。
