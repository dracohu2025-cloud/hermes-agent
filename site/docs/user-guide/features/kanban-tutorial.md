# Kanban 教程 {#kanban-tutorial}

本教程将介绍 Hermes Kanban 系统设计的四个使用场景，并在浏览器中打开仪表盘进行操作。如果你还没有阅读 [Kanban 概览](./kanban)，建议先从那里开始——本篇假设你已经知道任务、执行单元、负责人和调度器是什么。

## 准备工作 {#setup}

```bash
hermes kanban init           # 可选；首次运行 `hermes kanban <任何命令>` 会自动初始化
hermes dashboard             # 在浏览器中打开 http://127.0.0.1:9119
# 点击左侧导航栏中的 Kanban
```

仪表盘是最适合学习该系统的环境。你在仪表盘上看到的所有内容，也可以通过 CLI 的 `hermes kanban <动词>` 命令获得——两个界面共享同一个 SQLite 数据库，位于 `~/.hermes/kanban.db`。

## 看板概览 {#the-board-at-a-glance}

![看板概览](/img/kanban-tutorial/01-board-overview.png)

共六列，从左到右依次是：

- **Triage（待分类）** —— 原始思路，描述者会在有人处理之前完善规格说明。
- **Todo（待办）** —— 已创建但等待依赖项，或尚未分配。
- **Ready（就绪）** —— 已分配并等待调度器认领。
- **In progress（进行中）** —— 正在由工作者执行任务。当启用“按负责人分组”（默认开启）时，该列会按负责人进行子分组，让你一眼看清每个工作者正在做什么。
- **Blocked（受阻）** —— 工作者请求人工输入，或断路器触发。
- **Done（已完成）** —— 任务已完成。

顶栏提供搜索、租户和负责人的筛选器，以及“按负责人分组”的切换开关和“催促调度器”按钮（点击后会立即执行一次调度，而不是等待守护进程的下一个间隔）。点击任意卡片会在右侧打开其详情栏。

### 平铺视图 {#flat-view}

如果按负责人分组显得杂乱，关闭“按负责人分组”开关后，“进行中”列会折叠成一个按认领时间排序的平铺列表：

![关闭按负责人分组的看板](/img/kanban-tutorial/02-board-flat.png)

## 场景 1——单人开发者交付一个功能 {#story-1-solo-dev-shipping-a-feature}

你正在开发一个功能。经典流程：设计数据库模型、实现 API、编写测试。三个任务之间存在父子依赖关系。

```bash
SCHEMA=$(hermes kanban create "Design auth schema" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --body "设计认证模块的用户/会话/令牌数据模型。" \
    --json | jq -r .id)

API=$(hermes kanban create "Implement auth API endpoints" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --parent $SCHEMA \
    --body "POST /register, POST /login, POST /refresh, POST /logout。" \
    --json | jq -r .id)

hermes kanban create "Write auth integration tests" \
    --assignee qa-dev --tenant auth-project --priority 2 \
    --parent $API \
    --body "覆盖正常流程、密码错误、令牌过期、并发刷新等场景。"
```

由于 `API` 的父任务是 `SCHEMA`，而 `tests` 的父任务是 `API`，因此只有 `SCHEMA` 最初处于 `ready` 状态。另外两个则处于 `todo` 状态，直到它们的父任务完成。这就是依赖提升引擎的运作方式——在有可测试的 API 之前，不会有其他工作者接手编写测试。
认领 schema 任务，完成工作，然后交接：

```bash
hermes kanban claim $SCHEMA

# (你设计 schema、提交等)

hermes kanban complete $SCHEMA \
    --summary "users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); refresh tokens stored as sessions with type='refresh'" \
    --metadata '{
        "changed_files": ["migrations/001_users.sql", "migrations/002_sessions.sql"],
        "decisions": ["bcrypt for hashing", "JWT for session tokens", "7-day refresh, 15-min access"]
    }'
```

当 `SCHEMA` 进入 `done` 状态时，依赖引擎会自动将 `API` 提升为 `ready`。API 工作者在接手任务时，会从上下文中读取 `SCHEMA` 的摘要和元数据——这样它就能直接了解 schema 的决策，无需重新阅读冗长的设计文档。

在看板上点击已完成的 schema 任务，抽屉面板会展示所有信息：

![单人开发——已完成的 schema 任务抽屉](/img/kanban-tutorial/03-drawer-schema-task.png)

底部的“运行历史”部分是关键新增内容。一次尝试：结果 `completed`，工作者 `@backend-dev`，耗时、时间戳，以及完整的交接摘要。元数据块（`changed_files`、`decisions`）也存储在本次运行中，并会展示给任何读取该父任务的下游工作者。

在 CLI 上：

```bash
hermes kanban show $SCHEMA
hermes kanban runs $SCHEMA
# #  OUTCOME       PROFILE       ELAPSED  STARTED
# 1  completed     backend-dev        0s  2026-04-27 19:34
#     → users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); refresh tokens ...
```

## 故事2——批量任务处理 {#story-2-fleet-farming}

你有三个工作者（一个翻译、一个转录员、一个文案），以及一堆独立任务。你希望三个工作者并行拉取任务，并让进度清晰可见。这是最简单的看板用例，也是最初设计所优化的场景。

创建工作项：

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

启动网关，然后放手不管——它托管了嵌入式调度器，该调度器会在同一个 kanban.db 上拾取所有三个专业角色的任务：

```bash
hermes gateway start
```

现在将看板过滤到 `content-ops`（或者直接搜索“Transcribe”），你会看到：

![过滤到转录任务的舰队视图](/img/kanban-tutorial/07-fleet-transcribes.png)

两个转录任务已完成，一个正在运行，两个就绪等待下一次调度器触发。“进行中”列默认按角色分组（“按角色分道”），这样你就能看到每个工作者的活跃任务，而无需在混合列表中逐一查找。调度器会在当前任务完成后立即将下一个就绪任务提升为运行中。三个守护进程并行处理三个任务分配池，整个内容队列无需人工干预即可排空。
**故事 1 中关于结构化交接的描述在这里仍然适用。** 完成调用的翻译工作进程可以传入 `--summary "translated 4 pages, style matched existing marketing voice"` 和 `--metadata '{"duration_seconds": 720, "tokens_used": 2100}'` —— 这对分析以及任何依赖于此的下游任务都很有用。

## 故事 3 — 带重试的角色管道 {#story-3-role-pipeline-with-retry}

这正是看板优于扁平 TODO 列表的地方。产品经理撰写规格。工程师实现它。审查者拒绝第一次尝试。工程师根据修改再次尝试。审查者批准。

按 `auth-project` 过滤后的看板视图：

![多角色功能的管道视图](/img/kanban-tutorial/08-pipeline-auth.png)

三个阶段的链条一目了然：`规格：密码重置流程`（完成，产品经理）、`实现密码重置流程`（完成，后端开发）、`审查密码重置 PR`（就绪，审查者）。每个任务底部都有绿色父任务，子任务作为依赖项。

有趣的是实现任务，因为它曾被阻塞并重试：

```bash
# PM 完成规格，验收标准放在 metadata 中
hermes kanban complete $SPEC \
    --summary "规格已批准；POST /forgot-password 发送邮件，GET /reset/:token 渲染表单，POST /reset 应用新密码" \
    --metadata '{"acceptance": [
        "过期 token 返回 410",
        "重复使用最近 3 个密码返回 400 并附带消息",
        "成功重置会失效所有活跃会话"
    ]}'

# 工程师认领并实现，但审查因缺少强度检查而阻塞
hermes kanban claim $IMPL
hermes kanban block $IMPL "审查：缺少密码强度检查，重置链接不是一次性使用（30分钟内可重放）"

# 工程师迭代、解决、完成
hermes kanban unblock $IMPL
hermes kanban claim $IMPL
hermes kanban complete $IMPL \
    --summary "添加了 zxcvbn 强度检查，重置 token 现在是一次性使用（存储并在成功后删除）" \
    --metadata '{
        "changed_files": ["auth/reset.py", "auth/tests/test_reset.py", "migrations/003_single_use_reset_tokens.sql"],
        "tests_run": 11,
        "review_iteration": 2
    }'
```

点击实现任务。抽屉会显示 **两次尝试**：

![实现任务两次运行——先被阻塞后完成](/img/kanban-tutorial/04b-drawer-retry-history-scrolled.png)

- **运行 1** —— 被 `@backend-dev` 阻塞。审查反馈直接显示在结果下方：“密码强度检查缺失，重置链接不是一次性使用（30分钟内可重放）”。
- **运行 2** —— 被 `@backend-dev` 完成。新的摘要，新的元数据。

每次运行都是 `task_runs` 表中的一行，拥有自己的结果、摘要和元数据。重试历史并不是在“最新状态”任务之上附加的概念性事后补充——它是首要表示形式。当重试的工作进程打开任务时，`build_worker_context` 会向它展示之前的尝试，这样第二次尝试的工作进程就能看到第一次被阻塞的原因，并针对那些具体发现进行处理，而不是从头开始重新运行。
审核人接下来接手。当他们打开"审核密码重置 PR"时，会看到：

![审核人看到的流水线抽屉视图](/img/kanban-tutorial/09-drawer-pipeline-review.png)

父链接是已完成实现。当审核人的 worker 调用 `build_worker_context` 时，它会拉取父任务最近一次完成的运行摘要和元数据——这样审核人在查看 diff 之前就能读到"添加了 zxcvbn 强度检查，重置令牌现在是一次性的"并看到已更改文件的列表。

## 故事 4 — 熔断器与崩溃恢复 {#story-4-circuit-breaker-and-crash-recovery}

真实的 worker 会失败。缺少凭据、OOM 杀死、临时网络错误。调度器有两道防线：**熔断器**在连续 N 次失败后自动阻止任务，这样看板就不会永远空转；以及**崩溃检测**，它会回收那些 worker PID 在 TTL 过期前就消失的任务。

### 熔断器 — 看起来永久性的失败 {#circuit-breaker-permanent-looking-failure}

一个部署任务，因为配置文件的运行环境中没有设置 `AWS_ACCESS_KEY_ID` 而无法生成 worker：

```bash
hermes kanban create "部署到预发布环境（缺少凭据）" \
    --assignee deploy-bot --tenant ops
```

调度器尝试生成 worker。生成失败（`RuntimeError: AWS_ACCESS_KEY_ID not set`）。调度器释放认领，增加失败计数器，并在下一个 tick 重试。连续三次失败（默认的 `failure_limit`）后，熔断器触发：任务进入 `blocked` 状态，结果为 `gave_up`。在有人手动解除阻塞之前，不再重试。

点击被阻塞的任务：

![熔断器 — 2 次 spawn_failed + 1 次 gave_up](/img/kanban-tutorial/11-drawer-gave-up.png)

三次运行，`error` 字段都是相同的错误。前两次是 `spawn_failed`（可重试），第三次是 `gave_up`（终态）。上方的日志显示了完整序列：`created → claimed → spawn_failed → claimed → spawn_failed → claimed → gave_up`。

在终端中：

```bash
hermes kanban runs t_ef5d
# #   结果            配置文件        耗时  开始时间
# 1   spawn_failed   deploy-bot          0s  2026-04-27 19:34
#       ! deploy-bot 环境中未设置 AWS_ACCESS_KEY_ID
# 2   spawn_failed   deploy-bot          0s  2026-04-27 19:34
#       ! deploy-bot 环境中未设置 AWS_ACCESS_KEY_ID
# 3   gave_up        deploy-bot          0s  2026-04-27 19:34
#       ! deploy-bot 环境中未设置 AWS_ACCESS_KEY_ID
```

如果接入了 Telegram / Discord / Slack，网关会在 `gave_up` 事件时发送通知，这样你无需查看看板就能知道故障。

### 崩溃恢复 — worker 中途死亡 {#crash-recovery-worker-dies-mid-flight}

有时生成成功，但 worker 进程稍后死亡——段错误、OOM、`systemctl stop`。调度器轮询 `kill(pid, 0)` 并检测到死掉的 pid；认领被释放，任务回到 `ready` 状态，下一个 tick 会交给一个新的 worker。

种子数据中的示例是一个因内存不足而失败的迁移：

```bash
# Worker 认领任务，开始扫描 240 万行，在扫描到约 230 万行时 OOM 杀死
# 调度器检测到死掉的 pid，释放认领，增加尝试计数器
# 使用分块策略重试成功
```
抽屉面板展示了完整的两次尝试历史记录：

![崩溃与恢复——1次崩溃 + 1次完成](/img/kanban-tutorial/06-drawer-crash-recovery.png)

运行 1 — `crashed`，错误信息为 `OOM kill at row 2.3M (process 99999 gone)`。运行 2 — `completed`，元数据中包含 `"strategy": "chunked with LIMIT + WHERE id > last_id"`。重试的 worker 在其上下文中看到了运行 1 的崩溃情况，并选择了更安全的策略；元数据让未来的观察者（或事后分析人员）能清楚了解发生了什么变化。

## 结构化交接——为什么 `--summary` 和 `--metadata` 很重要 {#structured-handoff-why-summary-and-metadata-matter}

在上述每个故事中，worker 在完成时都传递了 `--summary` 和 `--metadata`。这并非装饰——它是工作流各阶段之间的主要交接通道。

当任务 B 上的 worker 读取其上下文时，它会获得：

- B 的**先前尝试**（之前的运行：结果、摘要、错误、元数据），这样重试的 worker 就不会重复失败的路径。
- **父任务结果**——对于每个父任务，最近一次完成的运行的摘要和元数据——这样下游 worker 就能看到上游工作的原因和方式。

这取代了困扰扁平看板系统的"翻查评论和工作输出"的繁琐操作。项目经理在规范的元数据中编写验收标准，工程师的 worker 能结构化地看到它们。工程师记录他们运行了哪些测试以及通过了多少，审阅者的 worker 在打开差异之前就已经掌握了这些列表。

批量关闭保护的存在是因为这些数据是按运行划分的。`hermes kanban complete a b c --summary X` 会被拒绝——将相同的摘要复制粘贴到三个任务上几乎总是错误的。不带交接标志的批量关闭仍然适用于常见的"我完成了一堆管理任务"的情况。

## 检查当前正在运行的任务 {#inspecting-a-task-currently-running}

为了完整性——这里是一个仍在进行中的任务的抽屉面板（来自故事 1 的 API 实现，被 `backend-dev` 认领但尚未完成）：

![已认领，进行中的任务](/img/kanban-tutorial/10-drawer-in-flight.png)

状态为 `Running`。活跃的运行出现在运行历史部分，结果为 `active` 且没有 `ended_at`。如果此 worker 崩溃或超时，调度器会以适当的结果关闭此运行，并在下次认领时开启新的运行——尝试行永远不会消失。

## 后续步骤 {#next-steps}

- [看板概述](./kanban) — 完整的数据模型、事件词汇表和 CLI 参考。
- `hermes kanban --help` — 每个子命令、每个标志。
- `hermes kanban watch --kinds completed,gave_up,timed_out` — 实时流式传输整个看板上的终端事件。
- `hermes kanban notify-subscribe &lt;task&gt; --platform telegram --chat-id &lt;id&gt;` — 当特定任务完成时接收网关通知。
