<a id="kanban-worker-lanes"></a>
# 看板工作通道

**工作通道**是看板调度器可以将任务路由到的一类进程。每条通道都有一个身份（assignee 字符串）、一个生成机制以及一个契约，规定了生成后必须对任务执行的操作。

本文档即该契约。它面向两类读者：

- **运维人员**——选择将哪些通道接入看板（创建哪些配置项、使用哪些 assignee）。
- **插件/集成开发者**——希望添加新的通道形态（封装 Codex / Claude Code / OpenCode 的 CLI 工作者、容器化的审查工作者、通过 API 拉取任务的非 Hermes 服务）。

如果您正在编写工作者（worker）代码本身——即运行在通道*内部*的 agent——请参考 [`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) 技能文档，其中包含更详细的过程细节。

<a id="the-hierarchy"></a>
## 层级结构

```text
Hermes Kanban  =  规范的任务生命周期 + 审计跟踪
Worker lane    =  为某张指派卡执行的实现者
Reviewer       =  把关“完成”状态的人类或人类代理
GitHub PR      =  可上游推送的产物（可选，用于代码类通道）
```

Hermes Kanban 拥有生命周期真相——`ready` → `running` → `blocked` / `done` / `archived`。工作通道执行工作，但从不拥有真相；它们所做的一切都通过 `kanban_*` 工具（对于非 Hermes 的外部工作通道，则通过 API）流回看板内核。审查者把关从“代码变更已写入”到“任务完成”的过渡。

<a id="what-a-lane-provides"></a>
## 通道需要提供什么

要成为一个看板工作通道，集成必须提供三样东西：

<a id="1-an-assignee-string"></a>
### 1. assignee 字符串

调度器将 `task.assignee` 与 Hermes 配置项名称（默认通道形状）或已注册的非可生成标识符（插件通道形状——请参见下面的[添加外部 CLI 工作通道](#adding-an-external-cli-worker-lane)）进行匹配。如果 assignee 无法解析，任务会停留在 `ready` 状态并记录一个 `skipped_nonspawnable` 事件，以便看板运维人员修复；不会静默丢弃它们，也不会由任何备用机制执行。

<a id="2-a-spawn-mechanism"></a>
### 2. 生成机制

对于 Hermes 配置项通道，调度器的 `_default_spawn` 在任务的固定工作区内运行 `hermes -p &lt;assignee&gt; chat -q &lt;prompt&gt;`（如果 `hermes` shim 不在 `$PATH` 上，则使用等效的模块形式），并设置以下环境变量：

| 变量 | 携带内容 |
|---|---|
| `HERMES_KANBAN_TASK` | 工作者正在处理的任务 ID |
| `HERMES_KANBAN_DB` | 每个看板 SQLite 文件的绝对路径 |
| `HERMES_KANBAN_BOARD` | 看板 slug |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 看板工作区树的根目录 |
| `HERMES_KANBAN_WORKSPACE` | *此*任务工作区的绝对路径 |
| `HERMES_KANBAN_RUN_ID` | 当前运行 ID（用于生命周期门控） |
| `HERMES_KANBAN_CLAIM_LOCK` | 声明锁字符串（`&lt;host&gt;:&lt;pid&gt;:&lt;uuid&gt;`） |
| `HERMES_PROFILE` | 工作者自身的配置项名称（用于 `kanban_comment` 的署名） |
| `HERMES_TENANT` | 租户命名空间（如果任务有） |

对于非 Hermes 通道（通过插件注册），插件提供自己的 `spawn_fn` 可调用对象，该对象接收 `task`、`workspace` 和 `board`，并返回一个可选的进程 ID 用于崩溃检测。
<a id="3-a-lifecycle-terminator"></a>
### 3. 生命周期终结器

每个 claim 必须以且仅以下列方式之一结束：

- `kanban_complete(summary=..., metadata=...)` —— 任务成功，状态变为 `done`。
- `kanban_block(reason=...)` —— 任务等待人工输入，状态变为 `blocked`。当执行 `kanban_unblock` 时，调度器会重新启动。
- 工作进程退出时未调用任何工具。内核将其回收并标记为 `crashed`（进程死亡）、`gave_up`（连续失败断路器触发）或 `timed_out`（超过 max_runtime）。这是失败路径；健康的工作进程不会在此结束。

kanban 内核强制每次运行必须且仅有一个终结器。如果工作进程既未调用任何终结器又正常退出，则视为 crashed。

<a id="outputs-and-the-review-required-convention"></a>
## 输出与 review-required 约定

对于大多数修改代码的任务，工作进程完成时并不意味着真正 *完成* —— 还需要人工审核。kanban 内核并不强制区分这一点（“修改代码的任务”这个定义很模糊，如果对每个代码工作进程都强制 block 而非 complete，会破坏那些不需要审核的流程）。这是一个附加在之上的约定：

- **使用 block 而非 complete**，其 `reason` 前缀加上 `review-required: `，这样仪表盘 / `hermes kanban show` 会将此行标记为等待审核。
- **首先将结构化元数据放入 `kanban_comment`**，因为 `kanban_block` 只携带人类可读的 `reason`。评论是持久的注释通道——所有与审计相关的字段（changed_files、tests_run、diff_path 或 PR url、决策）都应放在这里。
- **审核者要么批准并取消阻塞**，这将重新启动工作进程并附带评论线程以供后续跟进；要么通过另一条评论要求修改，下个工作进程运行时会作为 `kanban_show` 上下文的一部分看到这些评论。

[`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) 技能中有关于 `kanban_complete`（真正的终端任务——修复错字、文档修改、研究报告）和 `review-required` 阻塞模式的工作示例。

<a id="logs-and-audit-trail"></a>
## 日志与审计追踪

调度器将每个任务的 worker stdout/stderr 写入 `&lt;board-root&gt;/logs/&lt;task_id&gt;.log`。可从 kanban 元数据中审计日志：

- `task_runs` 行包含 `log_path`、退出码（可用时）、摘要和元数据。
- `task_events` 行包含每个状态转换（`promoted`、`claimed`、`heartbeat`、`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`、`reclaimed`、`claim_extended`）。
- `kanban_show` 返回两者，因此读取任务的审核者（或后续工作进程）无需仪表盘访问权限即可获取完整历史记录。

仪表盘会渲染运行历史，包括摘要、元数据块和退出状态徽章。CLI 用户可使用 `hermes kanban tail &lt;task_id&gt;` 实时追踪，或使用 `hermes kanban runs &lt;task_id&gt;` 查看历史尝试列表。

<a id="existing-lane-shapes"></a>
## 现有泳道形态

<a id="hermes-profile-lane-default"></a>
### Hermes 配置档案泳道（默认）

当前每个 kanban worker 的形态：任务负责人是配置档案名称，调度器启动 `hermes -p &lt;profile&gt;`，worker 自动加载 [`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) 技能以及 `KANBAN_GUIDANCE` 系统提示块，并使用 `kanban_*` 工具结束运行。除定义档案外无需其他设置。
当你为你的集群创建配置文件时，请选择与编排器要路由到的*角色*相匹配的名称。编排器（如果有的话）通过 `hermes profile list` 发现你的配置文件名称——系统没有预设的固定名单（关于编排器端的合约，请参阅 [`kanban-orchestrator`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-orchestrator/SKILL.md) 技能）。

<a id="orchestrator-profile-lane"></a>
### 编排器配置文件通道

配置文件通道的一个特化：编排器是一个 Hermes 配置文件，其工具集包含 `kanban`，但为了执行任务而排除了 `terminal` / `file` / `code` / `web`。它的工作是通过 `kanban_create` + `kanban_link` 将高级目标分解为子任务，然后退后一步。编排器技能编码了反诱惑规则。

<a id="adding-an-external-cli-worker-lane"></a>
## 添加外部 CLI 工作通道

将非 Hermes CLI 工具（Codex CLI、Claude Code CLI、OpenCode CLI、本地编码模型运行器等）作为看板工作通道接入，*还不是一条铺好的路*。调度器的 spawn 函数是可插拔的（`spawn_fn` 是 `dispatch_once` 的一个参数），并且插件可以为非 Hermes 的被分配者注册自己的 `spawn_fn`，但周围的集成工作——将 CLI 的退出码包装到 `kanban_complete` / `kanban_block` 调用中，将 CLI 的工作区/沙箱约定映射到调度器的 `HERMES_KANBAN_WORKSPACE` 环境变量，处理认证和每个 CLI 的策略——仍然是每个集成单独的设计工作。

如果你正在考虑添加一个 CLI 通道，请创建一个 issue，描述具体的 CLI 以及你想要启用的工作流程。上面的合约是任何此类通道必须满足的约束；实现形式（每个 CLI 一个插件 vs 一个由配置参数化的通用 CLI 运行器插件）是开放的。

与此相关的历史 issue 是 [#19931](https://github.com/NousResearch/hermes-agent/issues/19931) 以及已关闭但未合并的 Codex 特定 PR [#19924](https://github.com/NousResearch/hermes-agent/pull/19924)——它们描述了最初的架构提案，但并未落地一个运行器。

<a id="failure-modes-the-dispatcher-handles"></a>
## 调度器处理的故障模式

这样通道作者就不必重新实现这些：

- **过期的声明 TTL** — 一个声明了任务但从未心跳/完成/阻塞的工作进程，在 `DEFAULT_CLAIM_TTL_SECONDS`（默认 15 分钟）之后会被回收——但仅当工作进程实际已死亡时。一个存活的工作进程（慢模型在一次无工具的 LLM 调用中花费 20 分钟以上）会*延长*声明时间而不是被杀死；只有已死亡的 PID 才会被回收。
- **崩溃的工作进程** — 一个主机本地 PID 已消失的工作进程会被 `detect_crashed_workers` 检测到并清理；任务会增加 `consecutive_failures` 计数，并且当断路器跳闸时可能会自动阻塞。
- **运行级别重试** — 当任务被重试时（阻塞后、崩溃后、回收后），工作进程可以在终止工具上使用 `expected_run_id` 参数，以便在其自身的运行已被取代时快速失败。
- **每个任务的最大运行时间** — `task.max_runtime_seconds` 对每次运行的挂钟时间设置了硬性上限，无论 PID 是否存活。这可以捕获那些本应被存活 PID 扩展机制继续运行，但实际上已死锁的工作进程。
- **滞留任务检测** — 一个就绪任务，其被分配者在 `kanban.stranded_threshold_seconds`（默认 30 分钟）内从未产生声明，会在 `hermes kanban diagnostics` 中显示为 `stranded_in_ready` 警告。严重级别在达到阈值 2 倍时升级为错误，在 6 倍时升级为严重。这可以通过一个信号捕获拼写错误的被分配者、已删除的配置文件以及宕机的外部工作进程池——与身份无关，无需维护每个看板的允许列表。
<a id="related"></a>
## 相关

- [看板概览](./kanban) — 面向用户的介绍。
- [看板教程](./kanban-tutorial) — 配合仪表盘逐步操作。
- [`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) — Worker 进程加载的技能。
- [`kanban-orchestrator`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-orchestrator/SKILL.md) — 编排端。
