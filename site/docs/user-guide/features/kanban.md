---
sidebar_position: 12
title: "看板（多 Agent 协作面板）"
description: "基于 SQLite 的持久化任务面板，用于协调多个 Hermes 配置文件"
---

# 看板 — 多 Agent 配置文件协作 {#kanban-multi-agent-profile-collaboration}

> **想要实操演示？** 请阅读[看板教程](./kanban-tutorial) — 包含四个用户故事（独立开发者、集群农场、带重试的角色流水线、断路器），每个都配有仪表盘截图。本页是参考文档；教程才是叙事主线。

Hermes 看板是一个持久化任务面板，在所有 Hermes 配置文件之间共享，让多个命名的 Agent 能够协作完成工作，而无需依赖脆弱的进程内子 Agent 集群。每个任务都是 `~/.hermes/kanban.db` 中的一行；每次交接都是一行任何人都能读写的数据；每个 Worker 都是一个拥有自己身份的完整操作系统进程。

这种形态覆盖了 `delegate_task` 无法应对的工作负载：

- **研究分类** — 并行研究员 + 分析师 + 写手，人工参与。
- **定时运维** — 每日重复的简报，在数周内积累成日志。
- **数字孪生** — 持久的命名助手（`inbox-triage`、`ops-review`），随时间积累记忆。
- **工程流水线** — 分解 → 在并行工作树中实现 → 审查 → 迭代 → 提交 PR。
- **集群工作** — 一个专家管理 N 个主体（50 个社交账号、12 个监控服务）。

关于完整的设计原理、与 Cline Kanban / Paperclip / NanoClaw / Google Gemini Enterprise 的对比分析，以及八种经典协作模式，请参见仓库中的 `docs/hermes-kanban-v1-spec.pdf`。

## 看板 vs. `delegate_task` {#kanban-vs-delegatetask}

它们看起来很相似，但并非同一类原语。

| | `delegate_task` | 看板 |
|---|---|---|
| 形态 | RPC 调用（分叉 → 合并） | 持久化消息队列 + 状态机 |
| 父任务 | 阻塞直到子任务返回 | 创建后即触发并遗忘 |
| 子任务身份 | 匿名子 Agent | 具有持久记忆的命名配置文件 |
| 可恢复性 | 无 — 失败即失败 | 阻塞 → 解除阻塞 → 重新运行；崩溃 → 回收 |
| 人工参与 | 不支持 | 可在任意时刻评论 / 解除阻塞 |
| 每个任务的 Agent 数 | 一次调用 = 一个子 Agent | 任务生命周期内 N 个 Agent（重试、审查、跟进） |
| 审计追踪 | 上下文压缩后丢失 | SQLite 中持久化行，永久保留 |
| 协调方式 | 层级式（调用者 → 被调用者） | 对等 — 任何配置文件可读写任何任务 |

**一句话区分：** `delegate_task` 是一个函数调用；看板是一个工作队列，其中每次交接都是一行数据，任何配置文件（或人）都能看到并编辑。

**何时使用 `delegate_task`：** 当父 Agent 在继续之前需要一个简短推理答案，不涉及人工，结果会回到父 Agent 的上下文中。

**何时使用看板：** 当工作跨越 Agent 边界、需要能在重启后存活、可能需要人工输入、可能被不同角色接手、或者需要在事后可被发现时。

它们可以共存：看板 Worker 在其运行过程中内部也可以调用 `delegate_task`。

## 核心概念 {#core-concepts}

- **任务** — 包含标题、可选正文、一个负责人（配置文件名称）、状态（`triage | todo | ready | running | blocked | done | archived`）、可选的租户命名空间、可选的幂等键（用于重试自动化的去重）。
- **链接** — `task_links` 行，记录父 → 子依赖关系。当所有父任务都变为 `done` 状态时，调度器会将 `todo` 提升为 `ready`。
- **评论** — Agent 间的通信协议。Agent 和人类都可以追加评论；当 Worker 被（重新）启动时，它会读取完整的评论线程作为其上下文的一部分。
- **工作区** — Worker 操作的目录。有三种类型：
  - `scratch`（默认）— `~/.hermes/kanban/workspaces/&lt;id&gt;/` 下的临时目录。
  - `dir:&lt;path&gt;` — 一个已有的共享目录（Obsidian 仓库、邮件操作目录、每个账号的文件夹）。**必须是绝对路径。** 像 `dir:../tenants/foo/` 这样的相对路径在调度时会被拒绝，因为它们会相对于调度器当时的当前工作目录来解析，这会产生歧义并成为混淆代理的逃逸向量。除此之外，该路径是受信任的 — 这是你自己的机器、你自己的文件系统，Worker 以你的用户 ID 运行。这是受信任本地用户威胁模型；看板设计为单主机运行。
  - `worktree` — 用于编码任务的 `.worktrees/&lt;id&gt;/` 下的 git 工作树。Worker 端通过 `git worktree add` 创建。
- **调度器** — 一个长时间运行的循环，每隔 N 秒（默认 60 秒）执行以下操作：回收过期的认领、回收崩溃的 Worker（进程 ID 已消失但 TTL 尚未过期）、提升就绪任务、原子性地认领任务、启动分配的配置文件。默认**在网关内部**运行（`kanban.dispatch_in_gateway: true`）。如果同一任务连续约 5 次启动失败，调度器会自动将其阻塞，并将最后一次错误作为原因 — 这可以防止因配置文件不存在、工作区无法挂载等原因导致的任务反复抖动。
- **租户** — 可选的字符串命名空间。一个专家集群可以通过工作区路径和记忆键前缀实现数据隔离，为多个业务提供服务（`--tenant business-a`）。
## 快速开始 {#quick-start}

```bash
# 1. 创建看板
hermes kanban init

# 2. 启动网关（托管嵌入式调度器）
hermes gateway start

# 3. 创建任务
hermes kanban create "研究AI融资格局" --assignee researcher

# 4. 实时查看活动
hermes kanban watch

# 5. 查看看板
hermes kanban list
hermes kanban stats
```

### 网关嵌入式调度器（默认） {#gateway-embedded-dispatcher-default}

调度器运行在网关进程内部。无需安装，无需管理独立服务——只要网关在运行，就绪的任务会在下一个调度周期（默认60秒）被拾取。

```yaml
# config.yaml
kanban:
  dispatch_in_gateway: true        # 默认值
  dispatch_interval_seconds: 60    # 默认值
```

可通过运行时环境变量 `HERMES_KANBAN_DISPATCH_IN_GATEWAY=0` 覆盖配置标志以进行调试。标准网关监管机制适用：直接运行 `hermes gateway start`，或将网关配置为 systemd 用户单元（参见网关文档）。如果没有运行中的网关，`ready` 状态的任务会保持原样，直到网关启动——`hermes kanban create` 会在创建时对此发出警告。

将 `hermes kanban daemon` 作为独立进程运行的方式已**弃用**；请改用网关。如果你确实无法运行网关（例如无头主机策略禁止长期运行服务等），可以使用 `--force` 逃生口让旧的独立守护进程再存活一个发布周期，但在同一个 `kanban.db` 上同时运行网关嵌入式调度器和独立守护进程会导致任务认领冲突，不受支持。

### 幂等创建（适用于自动化/Webhooks） {#idempotent-create-for-automation-webhooks}

```bash
# 第一次调用创建任务。后续使用相同键的调用会返回已有任务ID，不会重复创建。
hermes kanban create "夜间运维审查" \
    --assignee ops \
    --idempotency-key "nightly-ops-$(date -u +%Y-%m-%d)" \
    --json
```

### 批量CLI动词 {#bulk-cli-verbs}

所有生命周期动词都支持多个ID，因此你可以用一个命令清理一批任务：

```bash
hermes kanban complete t_abc t_def t_hij --result "批量收尾"
hermes kanban archive  t_abc t_def t_hij
hermes kanban unblock  t_abc t_def
hermes kanban block    t_abc "需要输入" --ids t_def t_hij
```

## Worker如何与看板交互 {#how-workers-interact-with-the-board}

当调度器生成一个worker时，它会在子进程的环境变量中设置 `HERMES_KANBAN_TASK`。该环境变量是专用**看板工具集**的入口——普通Agent模式中从未出现的7个工具：

| 工具 | 用途 |
|---|---|
| `kanban_show` | 读取当前任务（标题、正文、之前的尝试、父任务交接、评论、完整的 `worker_context`）。默认使用环境变量中的任务ID。 |
| `kanban_complete` | 通过 `summary` + `metadata` 结构化交接完成。 |
| `kanban_block` | 升级为需要人工输入。 |
| `kanban_heartbeat` | 在长时间操作期间发送存活信号。 |
| `kanban_comment` | 追加到任务线程。 |
| `kanban_create` | （编排器）展开为子任务。 |
| `kanban_link` | （编排器）事后添加依赖关系。 |

**为什么用工具而不是直接调用 `hermes kanban`？** 三个原因：
1. **后端可移植性。** 终端工具指向远程后端（Docker / Modal / Singularity / SSH）的 Worker，会在容器内执行 `hermes kanban complete`，但容器中既未安装 `hermes`，也未挂载数据库。看板工具在 Agent 自身的 Python 进程中运行，无论终端后端是什么，始终访问 `~/.hermes/kanban.db`。
2. **无 Shell 引号脆弱性。** 通过 `shlex` + `argparse` 传递 `--metadata '{"files": [...]}'` 是潜在的隐患。结构化的工具参数绕过了这个问题。
3. **更好的错误信息。** 工具返回的是模型可以推理的结构化 JSON，而不是需要它去解析的 stderr 字符串。

**对普通会话零模式占用。** 常规的 `hermes chat` 会话的模式中没有任何 `kanban_*` 工具。每个工具的 `check_fn` 仅在设置了 `HERMES_KANBAN_TASK` 时返回 `True`，而该变量只有调度器生成此进程时才会设置。对于从未接触看板的用户，不会产生工具膨胀。

`kanban-worker` 和 `kanban-orchestrator` 技能教会模型在何时调用哪个工具以及调用顺序。

### Worker 技能 {#the-worker-skill}

任何需要处理看板任务的配置文件都必须加载 `kanban-worker` 技能。它教会 Worker 完整的生命周期：

1. 启动时，调用 `kanban_show()` 读取标题、正文、父级交接、先前尝试以及完整评论线程。
2. `cd $HERMES_KANBAN_WORKSPACE` 并在该目录下执行工作。
3. 在长时间操作期间，每隔几分钟调用 `kanban_heartbeat(note="...")`。
4. 完成时调用 `kanban_complete(summary="...", metadata={...})`，如果卡住则调用 `kanban_block(reason="...")`。

使用以下命令加载：

```bash
hermes skills install devops/kanban-worker
```

调度器在生成每个 Worker 时也会自动传递 `--skills kanban-worker`，因此即使配置文件的默认技能配置不包含该技能，Worker 也始终拥有该模式库。

### 为特定任务固定额外技能 {#pinning-extra-skills-to-a-specific-task}

有时单个任务需要被分配者配置文件默认不携带的专业上下文——需要 `translation` 技能的翻译任务、需要 `github-code-review` 的审查任务、需要 `security-pr-audit` 的安全审计。无需每次编辑被分配者的配置文件，而是直接将技能附加到任务上：

```bash
# CLI — 每个额外技能重复 --skill
hermes kanban create "translate README to Japanese" \
    --assignee linguist \
    --skill translation

# 多个技能
hermes kanban create "audit auth flow" \
    --assignee reviewer \
    --skill security-pr-audit \
    --skill github-code-review
```

从仪表盘的内联创建表单中，在 **skills** 字段中以逗号分隔输入技能。从另一个 Agent（编排器模式）中，使用 `kanban_create(skills=[...])`：

```
kanban_create(
    title="translate README to Japanese",
    assignee="linguist",
    skills=["translation"],
)
```

这些技能是**附加**到内置的 `kanban-worker` 之上的——调度器为每个技能（以及内置技能）发出一个 `--skills &lt;name&gt;` 标志，因此 Worker 启动时会加载所有这些技能。技能名称必须与被分配者配置文件上实际安装的技能匹配（运行 `hermes skills list` 查看可用技能）；没有运行时安装。
### 编排器技能 {#the-orchestrator-skill}

一个**行为良好的编排器不会自己动手干活。** 它会将用户的目标分解为任务，将它们关联起来，分配给各个专家，然后退居幕后。`kanban-orchestrator` 技能就体现了这一点：包含反诱惑规则、标准专家名单（`researcher`、`writer`、`analyst`、`backend-eng`、`reviewer`、`ops`）以及一个分解剧本。

将其加载到你的编排器配置文件中：

```bash
hermes skills install devops/kanban-orchestrator
```

为了获得最佳效果，请将其与一个工具集仅限于看板操作（`kanban`、`gateway`、`memory`）的配置文件配对使用，这样编排器即使想尝试，也无法执行具体的实现任务。

## 仪表盘（图形界面） {#dashboard-gui}

`/kanban` 命令行和斜杠命令足以无头运行看板，但对于需要人工介入的场景——如分类、跨配置文件监督、阅读评论线程以及在列之间拖拽卡片——可视化看板通常是更合适的界面。Hermes 将其作为一个**捆绑的仪表盘插件**提供，位于 `plugins/kanban/` 目录下——它既不是核心功能，也不是独立服务——遵循 [扩展仪表盘](./extending-the-dashboard) 中阐述的模型。

使用以下命令打开它：

```bash
hermes kanban init      # 一次性操作：如果 kanban.db 不存在则创建
hermes dashboard        # 导航栏中会出现 "Kanban" 标签页，位于 "Skills" 之后
```

### 插件提供的功能 {#what-the-plugin-gives-you}

- 一个 **Kanban** 标签页，每个状态对应一列：`triage`、`todo`、`ready`、`running`、`blocked`、`done`（以及开启切换开关后的 `archived`）。
  - `triage` 是用于存放粗略想法的暂存列，等待细化者来完善。通过 `hermes kanban create --triage`（或通过 Triage 列的内联创建）创建的任务会落在这里，调度器会忽略它们，直到人工或细化者将其提升到 `todo` / `ready`。
- 卡片显示任务 ID、标题、优先级徽章、租户标签、分配的配置文件、评论/链接数量、一个**进度药丸**（当任务有依赖项时，显示 `N/M` 子任务完成情况），以及“创建于 N 前”。每张卡片都有一个复选框，支持多选。
- **Running 列内的按配置文件分道**——工具栏复选框可切换 Running 列按分配者进行子分组。
- **通过 WebSocket 实时更新**——插件以短轮询间隔追踪仅追加的 `task_events` 表；任何配置文件（CLI、网关或其他仪表盘标签页）执行操作后，看板会立即反映变化。重新加载会进行防抖处理，因此事件突发只会触发一次重新获取。
- **拖拽**卡片到不同列以更改状态。拖放操作会发送 `PATCH /api/plugins/kanban/tasks/:id` 请求，该请求会通过 CLI 使用的相同 `kanban_db` 代码路由——三个界面永远不会出现不一致。移动到破坏性状态（`done`、`archived`、`blocked`）会提示确认。触摸设备使用基于指针的降级方案，因此看板在平板上也可用。
- **内联创建**——点击任何列标题上的 `+` 按钮，输入标题、分配者、优先级，并（可选地）从下拉列表中选择一个现有任务作为父任务。从 Triage 列创建会自动将新任务停放在 triage 中。
- **多选与批量操作**——按住 Shift/Ctrl 点击卡片或勾选其复选框，将其添加到选择中。顶部会出现一个批量操作栏，提供批量状态转换、归档和重新分配（通过配置文件下拉列表，或“取消分配”）。破坏性批量操作会先确认。部分失败的 ID 会报告，但不会中止其余操作。
- **点击一张卡片**（不按 Shift/Ctrl）会打开一个侧边抽屉（按 Escape 或点击外部关闭），其中包含：
  - **可编辑标题**——点击标题进行重命名。
  - **可编辑分配者/优先级**——点击元数据行进行重写。
  - **可编辑描述**——默认以 Markdown 渲染（标题、粗体、斜体、行内代码、围栏代码、`http(s)` / `mailto:` 链接、项目符号列表），并带有一个“编辑”按钮，可切换为文本区域。Markdown 渲染器是一个小巧、XSS 安全的渲染器——每次替换都在 HTML 转义的输入上运行，只有 `http(s)` / `mailto:` 链接会通过，并且始终设置 `target="_blank"` + `rel="noopener noreferrer"`。
  - **依赖编辑器**——父任务和子任务的标签列表，每个标签带有一个 `×` 用于取消链接，以及一个下拉列表（包含所有其他任务）用于添加新的父任务或子任务。循环依赖尝试会在服务器端被拒绝，并附带清晰的消息。
  - **状态操作行**（→ triage / → ready / → running / block / unblock / complete / archive），对破坏性转换有确认提示。
  - 结果部分（同样以 Markdown 渲染）、评论线程（按 Enter 提交）、最近 20 个事件。
- **工具栏过滤器**——自由文本搜索、租户下拉列表（默认为 `config.yaml` 中的 `dashboard.kanban.default_tenant`）、分配者下拉列表、“显示已归档”切换开关、“按配置文件分道”切换开关，以及一个**提醒调度器**按钮，这样你就不必等待下一个 60 秒的滴答了。
视觉上，目标就是大家熟悉的 Linear / Fusion 布局：深色主题、带计数的列标题、彩色状态圆点、优先级和租户的药丸标签。该插件只读取主题 CSS 变量（`--color-*`、`--radius`、`--font-mono` 等），因此它会根据当前激活的仪表盘主题自动换肤。

### 架构 {#architecture}

GUI 严格来说是一个**直读数据库 + 直写 kanban_db** 的层，本身不包含任何领域逻辑：

```
┌────────────────────────┐      WebSocket（监听 task_events）
│   React SPA (插件)     │ ◀──────────────────────────────────┐
│   HTML5 拖放           │                                    │
└──────────┬─────────────┘                                    │
           │ 通过 fetchJSON 进行 REST 调用                     │
           ▼                                                  │
┌────────────────────────┐     写入调用 kanban_db.*           │
│  FastAPI 路由          │     直接使用——与 CLI /kanban       │
│  plugins/kanban/       │     命令相同的代码路径              │
│  dashboard/plugin_api.py                                    │
└──────────┬─────────────┘                                    │
           │                                                  │
           ▼                                                  │
┌────────────────────────┐                                    │
│  ~/.hermes/kanban.db   │ ───── 追加 task_events ────────────┘
│  (WAL, 共享)           │
└────────────────────────┘
```

### REST 接口 {#rest-surface}

所有路由都挂载在 `/api/plugins/kanban/` 下，并由仪表盘的临时会话令牌保护：

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/board?tenant=<名称>&include_archived=…` | 按状态列分组的完整看板，以及用于筛选下拉框的租户和分配者 |
| `GET` | `/tasks/:id` | 任务 + 评论 + 事件 + 链接 |
| `POST` | `/tasks` | 创建（包装 `kanban_db.create_task`，接受 `triage: bool` 和 `parents: [id, …]`） |
| `PATCH` | `/tasks/:id` | 状态 / 分配者 / 优先级 / 标题 / 正文 / 结果 |
| `POST` | `/tasks/bulk` | 对 `ids` 中的每个 ID 应用相同的补丁（状态 / 归档 / 分配者 / 优先级）。单个 ID 失败不会中断其他操作 |
| `POST` | `/tasks/:id/comments` | 添加评论 |
| `POST` | `/links` | 添加依赖关系（`parent_id` → `child_id`） |
| `DELETE` | `/links?parent_id=…&child_id=…` | 移除依赖关系 |
| `POST` | `/dispatch?max=…&dry_run=…` | 触发调度器——跳过 60 秒等待 |
| `GET` | `/config` | 从 `config.yaml` 读取 `dashboard.kanban` 偏好设置——`default_tenant`、`lane_by_profile`、`include_archived_by_default`、`render_markdown` |
| `WS` | `/events?since=&lt;event_id&gt;` | `task_events` 行的实时流 |

每个处理器都是一个轻量包装——该插件大约 700 行 Python 代码（路由 + WebSocket 监听 + 批量处理器 + 配置读取器），不添加任何新的业务逻辑。一个微小的 `_conn()` 辅助函数会在每次读写时自动初始化 `kanban.db`，因此无论是用户先打开仪表盘、直接调用 REST API，还是运行 `hermes kanban init`，全新安装都能正常工作。
### Dashboard 配置 {#dashboard-config}

在 `~/.hermes/config.yaml` 中，`dashboard.kanban` 下的任何键都会改变该标签页的默认行为——插件在加载时通过 `GET /config` 读取它们：

```yaml
dashboard:
  kanban:
    default_tenant: acme              # 预选租户过滤器
    lane_by_profile: true             # “按 profile 分组”开关的默认值
    include_archived_by_default: false
    render_markdown: true             # 设为 false 则使用纯 <pre> 渲染
```

每个键都是可选的，默认值如上所示。

### 安全模型 {#security-model}

Dashboard 的 HTTP 认证中间件[显式跳过 `/api/plugins/`](./extending-the-dashboard#backend-api-routes)——插件路由默认不进行认证，因为 dashboard 默认绑定到 localhost。这意味着主机上的任何进程都可以访问 kanban 的 REST 接口。

WebSocket 多了一步：它要求将 dashboard 的临时会话令牌作为 `?token=…` 查询参数传递（浏览器无法在升级请求中设置 `Authorization`），这与浏览器内 PTY 桥接使用的模式一致。

如果你运行 `hermes dashboard --host 0.0.0.0`，那么所有插件路由（包括 kanban）都会从网络可达。**不要在共享主机上这样做。** 看板包含任务正文、评论和工作区路径；攻击者如果访问这些路由，就能读取你的整个协作界面，还可以创建/重新分配/归档任务。

`~/.hermes/kanban.db` 中的任务故意与 profile 无关（这是协调原语）。如果你使用 `hermes -p &lt;profile&gt; dashboard` 打开 dashboard，看板仍然会显示主机上其他 profile 创建的任务。同一个用户拥有所有 profile，但如果多个身份共存，这一点值得注意。

### 实时更新 {#live-updates}

`task_events` 是一个仅追加的 SQLite 表，具有单调递增的 `id`。WebSocket 端点会记录每个客户端最后看到的事件 id，并在新行出现时推送它们。当事件突发时，前端会重新加载（非常轻量的）看板端点——这比尝试从每种事件类型修补本地状态更简单、更正确。WAL 模式意味着读取循环永远不会阻塞调度器的 `BEGIN IMMEDIATE` 声明事务。

### 扩展它 {#extending-it}

该插件使用标准的 Hermes dashboard 插件契约——请参阅[扩展 Dashboard](./extending-the-dashboard) 了解完整的清单参考、shell 插槽、页面级插槽以及 Plugin SDK。额外的列、自定义卡片外观、按租户过滤的布局或完整的 `tab.override` 替换都可以在不 fork 此插件的情况下实现。

要禁用而不删除：在 `config.yaml` 中添加 `dashboard.plugins.kanban.enabled: false`（或删除 `plugins/kanban/dashboard/manifest.json`）。

### 范围边界 {#scope-boundary}

GUI 故意保持轻量。插件所做的所有事情都可以通过 CLI 完成；插件只是让人类使用起来更舒适。自动分配、预算、治理门控和组织架构图视图仍然属于用户空间——一个 router profile、另一个插件或对 `tools/approval.py` 的复用——正如设计规范中“超出范围”部分所列出的那样。
## CLI 命令参考 {#cli-command-reference}

```
hermes kanban init                                     # 创建 kanban.db + 打印守护进程提示
hermes kanban create "<title>" [--body ...] [--assignee <profile>]
                                [--parent <id>]... [--tenant <name>]
                                [--workspace scratch|worktree|dir:<path>]
                                [--priority N] [--triage] [--idempotency-key KEY]
                                [--max-runtime 30m|2h|1d|<seconds>]
                                [--skill <name>]...
                                [--json]
hermes kanban list [--mine] [--assignee P] [--status S] [--tenant T] [--archived] [--json]
hermes kanban show <id> [--json]
hermes kanban assign <id> <profile>                    # 或使用 'none' 取消分配
hermes kanban link <parent_id> <child_id>
hermes kanban unlink <parent_id> <child_id>
hermes kanban claim <id> [--ttl SECONDS]
hermes kanban comment <id> "<text>" [--author NAME]

# 批量操作 — 接受多个 id：
hermes kanban complete <id>... [--result "..."]
hermes kanban block <id> "<reason>" [--ids <id>...]
hermes kanban unblock <id>...
hermes kanban archive <id>...

hermes kanban tail <id>                                # 跟踪单个任务的事件流
hermes kanban watch [--assignee P] [--tenant T]        # 实时流式输出所有事件到终端
        [--kinds completed,blocked,…] [--interval SECS]
hermes kanban heartbeat <id> [--note "..."]            # 长时间操作的工作进程存活信号
hermes kanban runs <id> [--json]                       # 尝试历史记录（每次运行一行）
hermes kanban assignees [--json]                       # 磁盘上的配置文件 + 每个分配者的任务计数
hermes kanban dispatch [--dry-run] [--max N]           # 单次调度
        [--failure-limit N] [--json]
hermes kanban daemon --force                           # 已弃用 — 独立调度器（改用 `hermes gateway start`）
        [--failure-limit N] [--pidfile PATH] [-v]
hermes kanban stats [--json]                           # 按状态 + 按分配者的计数
hermes kanban log <id> [--tail BYTES]                  # 来自 ~/.hermes/kanban/logs/ 的工作进程日志
hermes kanban notify-subscribe <id>                    # 网关桥接钩子（由网关中的 /kanban 使用）
        --platform <name> --chat-id <id> [--thread-id <id>] [--user-id <id>]
hermes kanban notify-list [<id>] [--json]
hermes kanban notify-unsubscribe <id>
        --platform <name> --chat-id <id> [--thread-id <id>]
hermes kanban context <id>                             # 工作进程看到的内容
hermes kanban gc [--event-retention-days N]            # 工作区 + 旧事件 + 旧日志
        [--log-retention-days N]
```

所有命令也可在网关中以斜杠命令形式使用（`/kanban list`、`/kanban comment t_abc "need docs"` 等）。斜杠命令会绕过运行中的 Agent 守卫，因此当主 Agent 仍在聊天时，你可以使用 `/kanban unblock` 来解除卡住的工作进程。

## 协作模式 {#collaboration-patterns}

看板支持以下八种模式，无需任何新的原语：
| 模式 | 形态 | 示例 |
|---|---|---|---|
| **P1 扇出** | N 个同级，同一角色 | "并行研究 5 个角度" |
| **P2 流水线** | 角色链：侦察员 → 编辑 → 写手 | 每日简报汇编 |
| **P3 投票/法定人数** | N 个同级 + 1 个聚合器 | 3 个研究员 → 1 个评审员挑选 |
| **P4 长期日志** | 相同配置 + 共享目录 + 定时任务 | Obsidian 知识库 |
| **P5 人在回路** | 工作者阻塞 → 用户评论 → 解除阻塞 | 模糊决策 |
| **P6 `@提及`** | 从文本中内联路由 | `@reviewer 看看这个` |
| **P7 线程级工作区** | 在线程中执行 `/kanban here` | 每个项目的网关线程 |
| **P8 批量养殖** | 一个配置，N 个主题 | 50 个社交账号 |
| **P9 分类细化器** | 粗略想法 → `triage` → 细化器展开正文 → `todo` | "把这个一行描述变成规范任务" |

每个模式的详细示例，请参见 `docs/hermes-kanban-v1-spec.pdf`。

## 多租户使用 {#multi-tenant-usage}

当一个专家集群服务于多个业务时，用租户标签标记每个任务：

```bash
hermes kanban create "月度报告" \
    --assignee researcher \
    --tenant business-a \
    --workspace dir:~/tenants/business-a/data/
```

工作者会收到 `$HERMES_TENANT` 环境变量，并通过前缀来命名空间化其内存写入。看板、调度器和配置定义都是共享的；只有数据是隔离的。

## 网关通知 {#gateway-notifications}

当你从网关（Telegram、Discord、Slack 等）执行 `/kanban create …` 时，发起聊天的会话会自动订阅该新任务。网关的后台通知器每隔几秒轮询 `task_events`，并在每个终端事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）发生时向该聊天发送一条消息。已完成的任务还会发送工作者 `--result` 的第一行，这样你无需执行 `/kanban show` 就能看到结果。

你可以通过 CLI 显式管理订阅——当脚本或定时任务想要通知一个非其发起的聊天时，这很有用：

```bash
hermes kanban notify-subscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
hermes kanban notify-list
hermes kanban notify-unsubscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
```

一旦任务达到 `done` 或 `archived` 状态，订阅会自动移除；无需清理。

## 运行记录——每次尝试一行 {#runs-one-row-per-attempt}

一个任务是一个逻辑工作单元；**运行**是执行该任务的一次尝试。当调度器认领一个就绪任务时，它会在 `task_runs` 中创建一行，并将 `tasks.current_run_id` 指向该行。当该次尝试结束时——无论是完成、阻塞、崩溃、超时、生成失败还是被回收——运行行会以 `outcome` 结束，任务的指针也会清除。一个被尝试过三次的任务会有三行 `task_runs` 记录。

为什么需要两个表而不是直接修改任务：你需要**完整的尝试历史**来进行真实的事后分析（"第二次评审尝试批准了，第三次合并了"），并且你需要一个干净的地方来挂载每次尝试的元数据——哪些文件被修改了，哪些测试运行了，评审员记录了哪些发现。这些是运行事实，而不是任务事实。
运行（Runs）也是**结构化交接（structured handoff）**的载体。当某个 worker 完成任务时，它可以传递：

- `--result "<简短日志行>"` — 像以前一样放在任务行上（向后兼容）。
- `--summary "<人工交接>"` — 放在该运行上；下游子任务在其 `build_worker_context` 中看到它。
- `--metadata '{"changed_files": [...], "tests_run": 12}'` — 运行上的 JSON 字典；子任务会与摘要一起看到序列化后的内容。

下游子任务读取每个父任务最近一次完成的运行的摘要 + 元数据。重试的 worker 会读取自己任务上之前的尝试（结果、摘要、错误），这样就不会重复已经失败的路径。

```bash
# Worker 完成并附带结构化交接：
hermes kanban complete t_abcd \
    --result "rate limiter shipped" \
    --summary "implemented token bucket, keys on user_id with IP fallback, all tests pass" \
    --metadata '{"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14}'

# 查看重试任务的尝试历史：
hermes kanban runs t_abcd
#   #  OUTCOME       PROFILE           ELAPSED  STARTED
#   1  blocked       worker               12s  2026-04-27 14:02
#        → BLOCKED: need decision on rate-limit key
#   2  completed     worker                8m  2026-04-27 15:18
#        → implemented token bucket, keys on user_id with IP fallback
```

运行信息会展示在仪表盘上（抽屉中的“运行历史”部分，每次尝试一行彩色记录），也会通过 REST API 暴露（`GET /api/plugins/kanban/tasks/:id` 返回一个 `runs[]` 数组）。`PATCH /api/plugins/kanban/tasks/:id` 配合 `{status: "done", summary, metadata}` 会将两者转发给内核，因此仪表盘上的“标记完成”按钮与 CLI 等效。`task_events` 行携带它们所属的 `run_id`，以便 UI 按尝试分组，而 `completed` 事件在其负载中嵌入第一行摘要（最多 400 字符），这样网关通知器无需第二次 SQL 查询就能渲染结构化交接。

**批量关闭的注意事项。** `hermes kanban complete a b c --summary X` 会被拒绝——结构化交接是按运行进行的，因此将相同的摘要复制粘贴到 N 个任务上几乎总是错误的。不带 `--summary` / `--metadata` 的批量关闭仍然适用于常见的“我完成了一堆管理任务”的情况。

**状态变更导致的回收运行。** 如果你在仪表盘上将正在运行的任务拖离 `running`（回到 `ready`，或直接拖到 `todo`），或者归档一个仍在运行的任务，那么正在进行的运行会以 `outcome='reclaimed'` 关闭，而不会被孤立。当 `tasks.current_run_id` 为 `NULL` 时，`task_runs` 行始终处于终止状态，反之亦然——这个不变性在 CLI、仪表盘、调度器和通知器中都成立。

**从未认领的完成的合成运行。** 完成或阻塞一个从未被认领的任务（例如，人类从仪表盘上关闭一个 `ready` 任务并附带摘要，或者 CLI 用户运行 `hermes kanban complete &lt;ready-task&gt; --summary X`）否则会丢失交接。相反，内核会插入一条持续时间为零的运行行（`started_at == ended_at`），携带摘要/元数据/原因，以便尝试历史保持完整。`completed` / `blocked` 事件的 `run_id` 指向该行。
**实时抽屉刷新。** 当仪表盘的 WebSocket 事件流报告用户当前正在查看的任务有新事件时，抽屉会自动重新加载（通过一个嵌入到 `useEffect` 依赖列表中的按任务计数的计数器）。不再需要关闭再打开才能看到某个运行的新行或更新后的结果。

### 向前兼容 {#forward-compatibility}

`tasks` 表上的两个可空列是为 v2 工作流路由预留的：`workflow_template_id`（此任务所属的模板）和 `current_step_key`（该模板中当前激活的步骤）。v1 内核在路由时会忽略它们，但允许客户端写入，这样 v2 版本就可以在不进行另一次 schema 迁移的情况下添加路由机制。

## 事件参考 {#event-reference}

每次状态转换都会在 `task_events` 表中追加一行。每行带有一个可选的 `run_id`，以便 UI 可以按尝试对事件进行分组。种类分为三个集群，方便过滤（`hermes kanban watch --kinds completed,gave_up,timed_out`）：

**生命周期**（任务作为逻辑单元发生的变化）：

| 种类 | 载荷 | 时机 |
|---|---|---|
| `created` | `{assignee, status, parents, tenant}` | 任务被插入。`run_id` 为 `NULL`。 |
| `promoted` | — | `todo → ready`，因为所有父任务都达到了 `done`。`run_id` 为 `NULL`。 |
| `claimed` | `{lock, expires, run_id}` | 调度器原子性地认领了一个 `ready` 任务用于生成。 |
| `completed` | `{result_len, summary?}` | 工作进程写入了 `--result` / `--summary`，任务达到 `done`。`summary` 是第一行交接信息（最多 400 字符）；完整版本保存在运行行中。如果对从未被认领的任务调用 `complete_task` 并带有交接字段，则会合成一个零持续时间的运行，这样 `run_id` 仍然指向某个东西。 |
| `blocked` | `{reason}` | 工作进程或人工将任务翻转为 `blocked`。当对从未被认领的任务调用并带有 `--reason` 时，会合成一个零持续时间的运行。 |
| `unblocked` | — | `blocked → ready`，手动或通过 `/unblock`。`run_id` 为 `NULL`。 |
| `archived` | — | 从默认看板中隐藏。如果任务仍在运行，则携带作为副作用被回收的运行的 `run_id`。 |

**编辑**（非状态转换的人工驱动更改）：

| 种类 | 载荷 | 时机 |
|---|---|---|
| `assigned` | `{assignee}` | 负责人变更（包括取消分配）。 |
| `edited` | `{fields}` | 标题或正文更新。 |
| `reprioritized` | `{priority}` | 优先级变更。 |
| `status` | `{status}` | 仪表盘拖放直接写入状态（例如 `todo → ready`）。当从 `running` 拖离时，携带被回收的运行的 `run_id`；否则 `run_id` 为 NULL。 |

**工作进程遥测**（关于执行过程，而非逻辑任务）：

| 种类 | 载荷 | 时机 |
|---|---|---|
| `spawned` | `{pid}` | 调度器成功启动了一个工作进程。 |
| `heartbeat` | `{note?}` | 工作进程调用 `hermes kanban heartbeat $TASK` 以在长时间操作期间表明活跃。 |
| `reclaimed` | `{stale_lock}` | 认领 TTL 到期但未完成；任务回到 `ready`。 |
| `crashed` | `{pid, claimer}` | 工作进程 PID 不再存活但 TTL 尚未到期。 |
| `timed_out` | `{pid, elapsed_seconds, limit_seconds, sigkill}` | 超过 `max_runtime_seconds`；调度器发送 SIGTERM（5 秒宽限期后发送 SIGKILL）并重新排队。 |
| `spawn_failed` | `{error, failures}` | 一次生成尝试失败（缺少 PATH、工作空间无法挂载等）。计数器递增；任务返回 `ready` 以重试。 |
| `gave_up` | `{failures, error}` | 连续 N 次 `spawn_failed` 后断路器触发。任务自动阻塞并附带最后一次错误。默认 N = 5；可通过 `--failure-limit` 覆盖。 |
`hermes kanban tail &lt;id&gt;` 显示单个任务的这些信息。`hermes kanban watch` 则在整个看板上实时流式输出。

## 超出范围 {#out-of-scope}

Kanban 被设计为单主机运行。`~/.hermes/kanban.db` 是一个本地 SQLite 文件，调度器在同一台机器上启动工作进程。不支持在两台主机之间共享同一个看板——没有用于“主机 A 上的工作进程 X，主机 B 上的工作进程 Y”的协调原语，并且崩溃检测路径假定 PID 是主机本地的。如果你需要多主机支持，请在每个主机上运行独立的看板，并使用 `delegate_task` / 消息队列来桥接它们。

## 设计规范 {#design-spec}

完整的设计——架构、并发正确性、与其他系统的比较、实现计划、风险、未解决的问题——都记录在 `docs/hermes-kanban-v1-spec.pdf` 中。在提交任何改变行为的 PR 之前，请先阅读该文档。
