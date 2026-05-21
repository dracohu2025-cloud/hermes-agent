<a id="kanban-tutorial"></a>
# Kanban 教程

本教程将带你了解 Hermes Kanban 系统设计的四种使用场景，并在浏览器中打开仪表盘进行操作。如果你还没有阅读 [Kanban 概述](./kanban)，建议先阅读该文档——本教程假设你已经了解任务、运行、执行者和调度器的概念。

<a id="setup"></a>
## 环境准备

```bash
hermes kanban init           # 可选；首次运行 `hermes kanban <任意命令>` 会自动初始化
hermes dashboard             # 在浏览器中打开 http://127.0.0.1:9119
# 点击左侧导航栏中的 Kanban
```

仪表盘是**你**观察系统最舒适的地方。调度器生成的 Agent 工作进程永远不会看到仪表盘或 CLI——它们通过专用的 `kanban_*` [工具集](./kanban#how-workers-interact-with-the-board)（`kanban_show`、`kanban_list`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`、`kanban_unblock`）来驱动看板。所有三种界面——仪表盘、CLI、工作进程工具——都通过同一个基于看板的 SQLite 数据库（默认看板为 `~/.hermes/kanban.db`，之后创建的看板为 `~/.hermes/kanban/boards/&lt;slug&gt;/kanban.db`）进行路由，因此无论变更来自哪一端，每个看板都是一致的。

本教程全程使用 `default` 看板。如果你需要多个隔离的队列（每个项目/仓库/领域一个），请参阅概述中的 [看板（多项目）](./kanban#boards-multi-project)——相同的 CLI / 仪表盘 / 工作进程流程适用于每个看板，且工作进程在物理上无法看到其他看板上的任务。

在本教程中，**标记为 `bash` 的代码块是*你*需要运行的命令。** 标记为 `# worker tool calls` 的代码块是生成的工作进程模型发出的工具调用——这里展示它们是为了让你看到完整的循环过程，而不是让你自己运行它们。

<a id="the-board-at-a-glance"></a>
## 看板概览

![Kanban 看板概览](/img/kanban-tutorial/01-board-overview.png)

从左到右共六列：

- **待分类** — 原始想法。默认情况下，调度器会自动在此列对任务执行**分解器**（编排器驱动的扇出）：它会读取你的配置文件清单和描述，生成一个子任务图，并将这些子任务路由到最合适的专家，同时原始任务作为父任务保持活跃状态，以便编排器在所有子任务完成后重新唤醒并判断完成情况。点击 Kanban 页面顶部的 **编排：自动/手动** 开关可以切换模式。在手动模式下（或对于没有编排器配置文件的设置），点击卡片上的 **⚗ 分解**，或运行 `hermes kanban decompose &lt;id&gt;` / `/kanban decompose &lt;id&gt;`。对于不需要扇出的单个任务，**✨ 细化** 会进行一次性的规格重写（目标、方法、验收标准），并将其提升到 `todo` 列。在 `config.yaml` 的 `auxiliary.kanban_decomposer` 和 `auxiliary.triage_specifier` 下配置模型。请参阅 Kanban 主指南中的 [自动与手动编排](./kanban#auto-vs-manual-orchestration)。
- **待办** — 已创建但正在等待依赖项，或尚未分配。
- **就绪** — 已分配并等待调度器认领。
- **进行中** — 工作进程正在积极执行任务。在开启"按配置文件分列"（默认）的情况下，此列会按执行者进行子分组，让你一目了然地看到每个工作进程正在做什么。
- **阻塞** — 工作进程请求人工输入，或断路器跳闸。
- **完成** — 已完成。
顶部栏包含搜索、租户和经办人过滤器，以及一个“Lanes by profile”（按特性分列）切换开关和一个“Nudge dispatcher”（推送调度器）按钮，点击该按钮会立即执行一次调度滴答，而不是等待后台守护进程的下一个间隔。点击任意卡片将在右侧打开其抽屉。

<a id="flat-view"></a>
### 平铺视图

如果特性列过于杂乱，关闭“Lanes by profile”开关，“进行中”列将折叠为按认领时间排序的单一平铺列表：

![关闭了按特性分列的展示板](/img/kanban-tutorial/02-board-flat.png)

<a id="story-1-solo-dev-shipping-a-feature"></a>
## 故事 1 —— 独立开发者交付一个功能

你正在开发一个功能。经典流程：设计模式、实现 API、编写测试。三个任务，具有父→子依赖关系。

```bash
SCHEMA=$(hermes kanban create "Design auth schema" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --body "Design the user/session/token schema for the auth module." \
    --json | jq -r .id)

API=$(hermes kanban create "Implement auth API endpoints" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --parent $SCHEMA \
    --body "POST /register, POST /login, POST /refresh, POST /logout." \
    --json | jq -r .id)

hermes kanban create "Write auth integration tests" \
    --assignee qa-dev --tenant auth-project --priority 2 \
    --parent $API \
    --body "Cover happy path, wrong password, expired token, concurrent refresh."
```

因为 `API` 的父任务是 `SCHEMA`，而 `tests` 的父任务是 `API`，所以只有 `SCHEMA` 一开始处于 `ready` 状态。其他两个任务停留在 `todo` 状态，直到它们的父任务完成。这就是依赖提升引擎的作用——在准备好可测试的 API 之前，不会有其他 worker 接手测试的编写。

在下一个调度器滴答（默认 60 秒，或者如果你点击了 **Nudge dispatcher** 则立即生效），`backend-dev` 特性将产生一个 worker，其环境变量中带有 `HERMES_KANBAN_TASK=$SCHEMA`。以下是该 worker 在 agent 内部的工具调用循环：

```python
# worker tool calls — NOT commands you run
kanban_show()
# → returns title, body, worker_context, parents, prior attempts, comments

# (worker reads worker_context, uses terminal/file tools to design the schema,
#  write migrations, run its own checks, commit — the real work happens here)

kanban_heartbeat(note="schema drafted, writing migrations now")

kanban_complete(
    summary="users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); "
            "refresh tokens stored as sessions with type='refresh'",
    metadata={
        "changed_files": ["migrations/001_users.sql", "migrations/002_sessions.sql"],
        "decisions": ["bcrypt for hashing", "JWT for session tokens",
                      "7-day refresh, 15-min access"],
    },
)
```

`kanban_show` 默认使用 `$HERMES_KANBAN_TASK` 作为 `task_id`，因此 worker 无需知道自己的 ID。`kanban_complete` 将摘要 + 元数据写入当前 `task_runs` 行，关闭该运行，并将任务状态转换为 `done` —— 所有这些操作通过 `kanban_db` 在一个原子步骤中完成。

当 `SCHEMA` 进入 `done` 状态时，依赖引擎自动将 `API` 提升至 `ready` 状态。API worker 在接手时，会调用 `kanban_show()` 并看到父任务交接中附带的 `SCHEMA` 的摘要和元数据 —— 这样它就知道模式设计的决策，无需重新阅读冗长的设计文档。
点击看板上已完成的结构任务，抽屉面板会展示所有信息：

![独立开发者 —— 已完成结构任务抽屉](/img/kanban-tutorial/03-drawer-schema-task.png)

底部的“运行历史”部分是新增加的关键功能。一次尝试包括：结果 `completed`、工作者 `@backend-dev`、耗时、时间戳以及完整的交接摘要。元数据块（`changed_files`、`decisions`）也存储在运行记录中，并暴露给任何读取此父任务的下游工作者。

你可以随时从终端查看相同的数据 —— 这些命令是**你**在偷看看板，而不是工作者：

```bash
hermes kanban show $SCHEMA
hermes kanban runs $SCHEMA
# #  OUTCOME       PROFILE       ELAPSED  STARTED
# 1  completed     backend-dev        0s  2026-04-27 19:34
#     → users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); refresh tokens ...
```

<a id="story-2-fleet-farming"></a>
## 故事 2 —— 舰队式并行作业

你拥有三个工作者（翻译者、转录者、文案撰写者）和一堆独立任务。你想让三者并行工作并能看到进度。这是最简单的 Kanban 用例，也是最初设计所优化的场景。

创建工作：

```bash
for lang in Spanish French German; do
    hermes kanban create "Translate homepage to $lang" \
        --assignee translator --tenant content-ops
done
for i in 1 2 3 4 5; do
    hermes kanban create "Transcribe Q3 customer call #$i" \
        --assignee transcriber --tenant content-ops
done
for sku in 1001 1002 1003 1004; do
    hermes kanban create "Generate product description: SKU-$sku" \
        --assignee copywriter --tenant content-ops
done
```

启动网关然后离开 —— 它托管着嵌入式调度器，该调度器会从同一个 kanban.db 中拾取所有三个专业配置的任务：

```bash
hermes gateway start
```

现在将看板过滤到 `content-ops`（或直接搜索“Transcribe”），你会看到：

![舰队视图，过滤到转录任务](/img/kanban-tutorial/07-fleet-transcribes.png)

两个转录已完成，一个正在运行，两个已就绪等待下一次调度器激活。进行中列按配置分组（默认的“按配置分泳道”），这样你就能看到每个工作者的活动任务，无需扫描混合列表。调度器会在当前任务完成后立即将下一个就绪任务提升为运行中状态。三个守护进程并行处理三个分派人池，整个内容队列将在无需人工进一步干预的情况下消耗完毕。

**故事 1 中关于结构化交接的所有内容仍然适用。** 翻译者工作者在完成一次调用时会发出 `kanban_complete(summary="translated 4 pages, style matched existing marketing voice", metadata={"duration_seconds": 720, "tokens_used": 2100})` —— 这对分析以及任何依赖此任务的下游任务都很有用。

<a id="story-3-role-pipeline-with-retry"></a>
## 故事 3 —— 带重试的角色流水线

这就是 Kanban 相比于平坦的 TODO 列表更胜一筹的地方。PM 编写规范，工程师实现，评审人拒绝第一次尝试，工程师修改后再次尝试，评审人批准。
仪表盘视图（已按 `auth-project` 过滤）：

![多角色功能的流水线视图](/img/kanban-tutorial/08-pipeline-auth.png)

三级链路一目了然：`规格：密码重置流程`（已完成，pm）、`实现密码重置流程`（已完成，backend-dev）、`审查密码重置 PR`（准备就绪，reviewer）。每个任务底部都有绿色的父任务，子任务则显示为依赖项。

其中实现任务比较特殊，因为它曾被阻塞并重试。下面是完整的三个 Agent 编排过程，以每个 worker 的模型调用的工具来描述：

```python
# --- PM worker 在 $SPEC 上被触发，编写验收标准 ---
# worker 工具调用
kanban_show()
kanban_complete(
    summary="规格已批准；POST /forgot-password 发送邮件，"
            "GET /reset/:token 渲染表单，POST /reset 应用新密码",
    metadata={"acceptance": [
        "过期的 token 返回 410",
        "重复使用最近 3 个密码返回 400 并附带说明",
        "成功重置会使所有活跃会话失效",
    ]},
)
# → $SPEC 完成；$IMPL 自动从待办提升为准备就绪

# --- 工程师 worker 在 $IMPL 上被触发（第一次尝试） ---
# worker 工具调用
kanban_show()   # 读取 worker_context 中的 $SPEC 的摘要和验收元数据
# (工程师编写代码、运行测试、发起 PR)
# 审查反馈到达——工程师认为意见合理，于是阻塞任务
kanban_block(
    reason="审查反馈：缺少密码强度检查，重置链接不是一次性使用（可在30分钟内重复使用）",
)
# → $IMPL 转为阻塞状态；运行 1 结束，结果为 'blocked'
```

现在您（人类，或另一个独立的审查配置文件）阅读阻塞原因，判断修复方向明确，然后通过仪表盘上的“解除阻塞”按钮解除——或者通过 CLI / 斜杠命令：

```bash
hermes kanban unblock $IMPL
# 或在聊天中使用: /kanban unblock $IMPL
```

调度器将 `$IMPL` 提升回 `ready` 状态，并在下一个 tick 上重新生成 `backend-dev` worker。这第二次生成是对同一任务的**新运行**：

```python
# --- 工程师 worker 在 $IMPL 上被触发（第二次尝试） ---
# worker 工具调用
kanban_show()
# → worker_context 现在包含运行 1 的阻塞原因，因此该 worker 知道需要修复哪两件事，而无需重新阅读整个规格
# (工程师添加 zxcvbn 检查，使重置令牌变为一次性使用，重新运行测试)
kanban_complete(
    summary="添加了 zxcvbn 强度检查，重置令牌现在是一次性使用"
            "(存储并在成功后删除)",
    metadata={
        "changed_files": [
            "auth/reset.py",
            "auth/tests/test_reset.py",
            "migrations/003_single_use_reset_tokens.sql",
        ],
        "tests_run": 11,
        "review_iteration": 2,
    },
)
```

点击实现任务。侧边面板显示**两次尝试**：

![实现任务有两次运行——先阻塞后完成](/img/kanban-tutorial/04b-drawer-retry-history-scrolled.png)

- **运行 1** — 被 `@backend-dev` 阻塞。审查反馈紧跟在结果下方：“缺少密码强度检查，重置链接不是一次性使用（可在30分钟内重复使用）”。
- **运行 2** — 由 `@backend-dev` 完成。新的摘要，新的元数据。
每次运行都是 `task_runs` 表中的一行，包含自己的结果、摘要和元数据。重试历史并不是在“最新状态”任务之上附加的概念性事后补充——它是主要的表现形式。当重试中的 worker 打开任务时，`build_worker_context` 会向其展示之前的尝试，因此第二次执行的 worker 能够看到第一次被阻塞的原因，并针对这些具体发现进行处理，而不是从头重新运行。

接下来由审核者接手。当他们打开 `Review password reset PR` 时，会看到：

![审核者的抽屉视图，展示流水线](/img/kanban-tutorial/09-drawer-pipeline-review.png)

父链接是已完成的实现。当审核者的 worker 在 `Review password reset PR` 上生成并调用 `kanban_show()` 时，返回的 `worker_context` 包含父任务最近一次完成运行的摘要和元数据——因此审核者在查看 diff 之前就能读到“添加了 zxcvbn 强度检查，重置令牌现在为一次性使用”的信息，并掌握已更改文件的列表。

<a id="story-4-circuit-breaker-and-crash-recovery"></a>
## 故事 4 — 熔断器与崩溃恢复

真实的 worker 会失败。缺少凭据、OOM 杀死、瞬时网络错误。调度器有两道防线：**熔断器**，在连续 N 次失败后自动阻止任务，避免看板无限震荡；以及**崩溃检测**，当 worker 的 PID 在其 TTL 过期前消失时，回收该任务。

<a id="circuit-breaker-permanent-looking-failure"></a>
### 熔断器 — 看似永久性的失败

一个部署任务，因为配置文件的运行环境中未设置 `AWS_ACCESS_KEY_ID` 而无法生成 worker：

```bash
hermes kanban create "Deploy to staging (missing creds)" \
    --assignee deploy-bot --tenant ops \
    --max-retries 3
```

调度器尝试生成 worker。生成失败（`RuntimeError: AWS_ACCESS_KEY_ID not set`）。调度器释放任务认领，增加失败计数器，并在下一个 tick 再次尝试。由于此示例设置了 `--max-retries 3`，熔断器在连续三次失败后触发：任务进入 `blocked` 状态，结果为 `gave_up`。如果省略该标志，Hermes 会使用 `kanban.failure_limit`（默认值：2）。在有人手动解除阻塞之前，不会再有重试。

点击被阻塞的任务：

![熔断器 — 2 次 spawn_failed + 1 次 gave_up](/img/kanban-tutorial/11-drawer-gave-up.png)

三次运行，`error` 字段都显示相同的错误。前两次是 `spawn_failed`（可重试），第三次是 `gave_up`（终止状态）。上方的事件日志显示了完整序列：`created → claimed → spawn_failed → claimed → spawn_failed → claimed → gave_up`。

在终端中：

```bash
hermes kanban runs t_ef5d
# #   OUTCOME        PROFILE        ELAPSED  STARTED
# 1   spawn_failed   deploy-bot          0s  2026-04-27 19:34
#       ! AWS_ACCESS_KEY_ID not set in deploy-bot env
# 2   spawn_failed   deploy-bot          0s  2026-04-27 19:34
#       ! AWS_ACCESS_KEY_ID not set in deploy-bot env
# 3   gave_up        deploy-bot          0s  2026-04-27 19:34
#       ! AWS_ACCESS_KEY_ID not set in deploy-bot env
```

如果接入了 Telegram / Discord / Slack，网关会在 `gave_up` 事件发生时发送通知，这样你无需查看看板就能得知故障情况。
<a id="crash-recovery-worker-dies-mid-flight"></a>
### 崩溃恢复 — Worker 在半路挂掉

有时 spawn 成功了，但 worker 进程后来挂了——比如段错误、OOM、`systemctl stop`。dispatcher 定期执行 `kill(pid, 0)` 探测，发现 pid 已死；claim 释放，任务回到 `ready` 状态，下一个 tick 就会把它交给一个新的 worker。

种子数据里的例子是一个因内存不足而失败的迁移：

```bash
# Worker 认领任务，开始扫描 240 万行数据，扫描到约 230 万行时 OOM 将其杀死
# Dispatcher 检测到死 pid，释放 claim，递增尝试次数
# 使用分块策略重试，最终成功
```

抽屉面板展示了完整的两次尝试历史记录：

![崩溃与恢复 — 1 次崩溃 + 1 次完成](/img/kanban-tutorial/06-drawer-crash-recovery.png)

运行 1 — `crashed`，错误信息为 `OOM kill at row 2.3M (process 99999 gone)`。运行 2 — `completed`，元数据中包含 `"strategy": "chunked with LIMIT + WHERE id > last_id"`。重试的 worker 在其上下文中看到了运行 1 的崩溃信息，因此选择了更安全的策略；元数据让后来的观察者（或事后复盘人员）能清楚地知道发生了什么变化。

<a id="structured-handoff-why-summary-and-metadata-matter"></a>
## 结构化交接 — 为什么 `summary` 和 `metadata` 很重要

前面所有的故事里，worker 最后都调用了 `kanban_complete(summary=..., metadata=...)`。这可不是装饰——而是工作流各阶段之间主要的交接渠道。

当某个任务 B 的 worker 被 spawn 并调用 `kanban_show()` 时，它拿到的 `worker_context` 包含：

- B 的 **prior attempts**（之前的运行：结果、summary、错误、元数据），这样重试的 worker 就不会重复走失败的路径。
- **Parent task results** — 对每个父任务，最近一次成功运行的 summary 和元数据 — 这样下游 worker 就能知道上游任务为何以及如何完成。

这取代了传统平面 kanban 系统中那种“翻评论和输出结果”的繁琐操作。产品经理可以在 spec 的元数据中写入验收标准，工程师的 worker 通过父任务交接就能结构化地看到这些信息。工程师记录自己运行了哪些测试、通过数量，而评审者的 worker 在打开 diff 之前就已经拿到了这份列表。

批量完成的保护机制之所以存在，是因为这些数据是每次运行独有的。`hermes kanban complete a b c --summary X`（你在命令行中执行）会被拒绝——把同样的 summary 复制粘贴到三个任务上几乎总是错的。对于常见的“我完成了一堆管理任务”的情况，不含交接标志的批量关闭仍然有效。工具界面上根本没有暴露批量变体；`kanban_complete` 始终一次只处理一个任务，原因同上。

<a id="inspecting-a-task-currently-running"></a>
## 检查当前正在运行的任务

作为补充——这里是一个仍在运行中的任务的抽屉面板（来自故事 1 中的 API 实现，已被 `backend-dev` 认领，但尚未完成）：

![已认领、正在运行的任务](/img/kanban-tutorial/10-drawer-in-flight.png)

状态为 `Running`。活跃运行出现在运行历史部分，结果列为 `active`，且没有 `ended_at`。如果此 worker 挂掉或超时，dispatcher 会以相应的结果关闭这次运行，并在下一次认领时打开新的运行——尝试记录行永远不会消失。
<a id="next-steps"></a>
## 后续步骤

- [看板总览](./kanban) — 完整的数据模型、事件词汇表和 CLI 参考。
- `hermes kanban --help` — 每个子命令和每个标志。
- `hermes kanban watch --kinds completed,gave_up,timed_out` — 实时监控整个看板上的终端事件流。
- `hermes kanban notify-subscribe &lt;task&gt; --platform telegram --chat-id &lt;id&gt;` — 在特定任务完成时通过网关接收通知。
