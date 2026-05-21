---
sidebar_position: 12
title: "看板（多 Agent 任务板）"
description: "基于 SQLite 的持久化任务板，用于协调多个 Hermes 配置文件"
---

<a id="kanban-multi-agent-profile-collaboration"></a>
# 看板 — 多 Agent 配置文件协作

> **想要实操演示？** 请阅读[看板教程](./kanban-tutorial) —— 四个用户故事（独立开发者、批量农场、带重试的角色流水线、断路器），每个都配有仪表盘截图。本页是参考文档，教程才是叙事主线。

Hermes 看板是一个持久化任务板，在你所有的 Hermes 配置文件之间共享，让多个命名 Agent 能够协作完成任务，而无需依赖脆弱的进程内子 Agent 集群。每个任务对应 `~/.hermes/kanban.db` 中的一行；每次交接都是一行记录，任何人都可以读写；每个工人都是一个拥有独立身份的完整 OS 进程。

<a id="two-surfaces-the-model-talks-through-tools-you-talk-through-the-cli"></a>
### 两个交互面：模型通过工具对话，你通过 CLI 操作

看板有两个入口，背后都是同一个 `~/.hermes/kanban.db`：

- **Agent 通过专用的 `kanban_*` 工具集驱动看板** —— `kanban_show`、`kanban_list`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`、`kanban_unblock`。调度器在启动每个工人时，其 schema 中已经包含了这些工具；编排配置文件也可以显式启用 `kanban` 工具集。模型通过直接调用工具来读取和路由任务，*而不是*通过执行 `hermes kanban` 命令。详见下文[工人如何与看板交互](#how-workers-interact-with-the-board)。
- **你（以及脚本和 cron）通过 CLI 上的 `hermes kanban …`、以斜杠命令 `/kanban …` 或仪表盘来驱动看板。** 这些是为人类和自动化准备的 —— 那些没有调用模型工具的地方。

两个交互面都经过同一个 `kanban_db` 层路由，因此读取看到一致的视图，写入不会出现漂移。本页其余部分展示 CLI 示例，因为易于复制粘贴，但每个 CLI 动词都有一个模型使用的工具调用等价操作。

这种形态能够处理 `delegate_task` 无法应对的工作负载：

- **研究分诊** —— 并行研究员 + 分析师 + 写手，人机协同。
- **定时运维** —— 每天重复的简报，随时间累积成日志。
- **数字孪生** —— 持久的命名助手（如 `inbox-triage`、`ops-review`），长期积累记忆。
- **工程流水线** —— 分解 → 在并行工作目录中实现 → 审查 → 迭代 → 创建 PR。
- **批量工作** —— 一个专家管理 N 个主题（50 个社交媒体账号、12 个监控服务）。

关于完整的设计原理、与 Cline Kanban / Paperclip / NanoClaw / Google Gemini Enterprise 的对比分析，以及八种经典协作模式，请参阅仓库中的 `docs/hermes-kanban-v1-spec.pdf`。

<a id="kanban-vs-delegatetask"></a>
## 看板 vs. `delegate_task`

它们看起来很相似，但并非同一原语。

| 特性 | `delegate_task` | 看板 |
|---|---|---|
| 形态 | RPC 调用（派生 → 汇合） | 持久消息队列 + 状态机 |
| 父任务 | 在子任务返回前阻塞 | 创建后即发即忘 |
| 子任务身份 | 匿名子 Agent | 带持久记忆的命名配置文件 |
| 可恢复性 | 无 —— 失败即失败 | 阻塞 → 解除阻塞 → 重新运行；崩溃 → 回收 |
| 人机协同 | 不支持 | 随时评论/解除阻塞 |
| 每个任务的 Agent 数量 | 一次调用 = 一个子 Agent | 任务生命周期内可有多名 Agent（重试、审查、后续跟进） |
| 审计轨迹 | 上下文压缩后丢失 | SQLite 中的持久行，永久保留 |
| 协调方式 | 层级式（调用者 → 被调用者） | 对等式 —— 任何配置文件可读写任何任务 |
**一句话区分：** `delegate_task` 是一个函数调用；Kanban 是一个工作队列，每次交接都是一行记录，任何角色（或人类）都可以查看和编辑。

**何时使用 `delegate_task`：** 父 Agent 需要在继续之前得到一个简短推理答案，无需人工参与，结果会返回父 Agent 的上下文。

**何时使用 Kanban：** 工作跨 Agent 边界、需要重启后保留、可能需要人工介入、可能被不同角色接手，或者需要在事后可被发现时。

二者可以共存：Kanban 工作者在执行过程中也可以内部调用 `delegate_task`。

<a id="core-concepts"></a>
## 核心概念

- **看板（Board）** — 一个独立的任务队列，拥有自己的 SQLite 数据库、工作空间目录和调度器循环。同一安装实例可以有多个看板（例如每个项目、仓库或领域一个）；参见下文 [看板（多项目）](#boards-multi-project)。单项目用户使用 `default` 看板，除了本文档这一部分外，不会看到“看板”这个词。
- **任务（Task）** — 一行记录，包含标题、可选的正文、一个执行者（角色名称）、状态（`triage | todo | ready | running | blocked | done | archived`）、可选租户命名空间、可选幂等键（用于自动化重试时的去重）。
- **链接（Link）** — `task_links` 表记录，表示父→子依赖关系。当所有父任务都变为 `done` 状态时，调度器会将 `todo → ready`。
- **评论（Comment）** — 跨 Agent 的通信协议。Agent 和人类都可以追加评论；当工作者被（重新）启动时，它会读取完整的评论线程作为其上下文的一部分。
- **工作空间（Workspace）** — 工作者操作的目录。有三种类型：
  - `scratch`（默认） — 在 `~/.hermes/kanban/workspaces/&lt;id&gt;/` 下（或非默认看板下 `~/.hermes/kanban/boards/&lt;slug&gt;/workspaces/&lt;id&gt;/`）创建临时目录。
  - `dir:&lt;path&gt;` — 一个已有的共享目录（Obsidian 仓库、邮件操作目录、按账户划分的文件夹）。**必须是绝对路径。** 像 `dir:../tenants/foo/` 这样的相对路径会在调度时被拒绝，因为它们会相对于调度器当时的当前工作目录解析，这样具有歧义且是混淆代理的逃逸向量。否则路径是受信任的——这是你的机器、你的文件系统，工作者使用你的 UID 运行。这是可信本地用户威胁模型；Kanban 设计为单机运行。
  - `worktree` — 用于编码任务的 `.worktrees/&lt;id&gt;/` 下的 git 工作树。使用 `worktree:&lt;path&gt;` 来固定确切的目标路径。工作者端通过 `git worktree add` 创建，如果提供了 `--branch` 则使用该分支。
- **调度器（Dispatcher）** — 一个长期运行的循环，每隔 N 秒（默认 60）执行以下操作：回收过期的认领、回收崩溃的工作者（PID 已消失但 TTL 尚未过期）、升级就绪任务、原子认领并启动指定角色。默认在**网关内**运行（`kanban.dispatch_in_gateway: true`）。每个 tick 一个调度器扫描所有看板；启动工作者时设置了 `HERMES_KANBAN_BOARD` 环境变量，使其无法看到其他看板。如果同一任务连续启动失败次数达到 `kanban.failure_limit`（默认：2），调度器会自动阻止该任务，并将最后一次错误作为原因——这可以防止因角色不存在、工作空间无法挂载等原因导致任务反复失败。
- **租户（Tenant）** — 看板*内部*的可选字符串命名空间。一支专家团队可以通过工作空间路径和内存键前缀的数据隔离，为多个业务提供服务（`--tenant business-a`）。租户是软过滤；看板是硬隔离边界。
<a id="boards-multi-project"></a>
## 看板（多项目）

看板让您可以将不相关的工作流分开——每个项目、仓库或领域一个——放入独立的队列中。新安装时只有一个名为 `default` 的看板（为向后兼容，数据库位于 `~/.hermes/kanban.db`）。只需要一个工作流的用户完全不需要了解看板；此功能是可选加入的。

每个看板的隔离是绝对的：

- 每个看板有独立的 SQLite 数据库（`~/.hermes/kanban/boards/&lt;slug&gt;/kanban.db`）。
- 独立的 `workspaces/` 和 `logs/` 目录。
- 为某个任务生成的工作进程**只能**看到其所在看板的任务——调度器会在子进程环境中设置 `HERMES_KANBAN_BOARD`，工作进程可访问的每个 `kanban_*` 工具都会读取该变量。
- 不允许跨看板链接任务（保持模式简单；如果确实需要跨项目引用，请使用自由文本提及并手动按 ID 查找）。

<a id="managing-boards-from-the-cli"></a>
### 通过 CLI 管理看板

```bash
# 查看磁盘上的看板。全新安装只显示 "default"。
hermes kanban boards list

# 创建一个新看板。
hermes kanban boards create atm10-server \
    --name "ATM10 Server" \
    --description "Minecraft 模组服务器运维" \
    --icon 🎮 \
    --switch                   # 可选：将其设为当前活动看板

# 在不切换的情况下操作特定看板。
hermes kanban --board atm10-server list
hermes kanban --board atm10-server create "重启 ATM 服务器" --assignee ops

# 更改后续调用的"当前"看板。
hermes kanban boards switch atm10-server
hermes kanban boards show             # 当前哪个看板是活动的？

# 重命名显示名称（slug 是不可变的——它是目录名）。
hermes kanban boards rename atm10-server "ATM10 (生产环境)"

# 归档（默认）——将看板目录移动到 boards/_archived/<slug>-<ts>/。
# 可以通过将目录移回来恢复。
hermes kanban boards rm atm10-server

# 硬删除——`rm -rf` 看板目录。无法恢复。
hermes kanban boards rm atm10-server --delete
```

看板解析顺序（优先级从高到低）：

1. CLI 调用中显式指定的 `--board &lt;slug&gt;`。
2. `HERMES_KANBAN_BOARD` 环境变量（调度器在生成工作进程时设置，因此工作进程无法看到其他看板）。
3. `~/.hermes/kanban/current`——由 `hermes kanban boards switch` 持久化的 slug。
4. `default`。

Slug 的验证规则：小写字母数字 + 连字符 + 下划线，1-64 个字符，必须以字母数字开头。大写输入会自动转为小写。其他任何字符（斜杠、空格、点、`..`）都会在 CLI 层被拒绝，因此无法通过路径遍历技巧来命名看板。

<a id="managing-boards-from-the-dashboard"></a>
### 通过仪表盘管理看板

`hermes dashboard` → 当存在多个看板（或任何看板有任务）时，Kanban 标签页顶部会显示看板切换器。单看板用户只会看到一个小型的 `+ 新建看板` 按钮；切换器在需要时才会显示。

- **看板下拉菜单**——选择活动看板。您的选择会保存到浏览器的 `localStorage` 中，因此在重新加载时保持不变，而不会改变您可能仍在终端中打开的 CLI 的 `current` 指针。
- **+ 新建看板**——打开一个模态框，要求输入 slug、显示名称、描述和图标。可选择自动切换到新看板。
- **归档**——仅在非 `default` 看板上显示。确认后，将看板目录移动到 `boards/_archived/`。
所有仪表盘 API 端点都接受 `?board=&lt;slug&gt;` 参数用于限定看板范围。事件 WebSocket 在连接时固定到某个看板；在 UI 中切换看板会打开一个针对新看板的新 WebSocket 连接。

<a id="quick-start"></a>
## 快速开始

下面的命令是**你**（人类）在设置看板并创建任务。一旦任务被分配，调度器会以工作进程的形式启动指定的配置文件，然后**模型通过 `kanban_*` 工具调用来驱动任务，而不是通过 CLI 命令**——详见[工作进程如何与看板交互](#how-workers-interact-with-the-board)。

```bash
# 1. 创建看板（你操作）
hermes kanban init

# 2. 启动网关（托管嵌入式调度器）
hermes gateway start

# 3. 创建任务（你操作——或编排 Agent 通过 kanban_create 创建）
hermes kanban create "research AI funding landscape" --assignee researcher

# 4. 实时查看活动（你操作）
hermes kanban watch

# 5. 查看看板（你操作）
hermes kanban list
hermes kanban stats
```

当调度器拾取 `t_abcd` 并启动 `researcher` 配置文件时，该工作进程的模型做的第一件事就是调用 `kanban_show()` 来读取其任务。它不会运行 `hermes kanban show t_abcd`。

<a id="gateway-embedded-dispatcher-default"></a>
### 网关嵌入式调度器（默认）

调度器在网关进程内运行。无需安装任何东西，也无需管理独立服务——只要网关在运行，就绪的任务会在下一个调度周期（默认 60 秒）被拾取。

```yaml
# config.yaml
kanban:
  dispatch_in_gateway: true        # 默认值
  dispatch_interval_seconds: 60    # 默认值
```

可以通过运行时环境变量 `HERMES_KANBAN_DISPATCH_IN_GATEWAY=0` 覆盖配置标志以进行调试。标准网关监管适用：直接运行 `hermes gateway start`，或者将网关配置为 systemd 用户单元（参见网关文档）。如果没有运行中的网关，`ready` 状态的任务会保持原样，直到网关启动——`hermes kanban create` 在创建时会对此发出警告。

将 `hermes kanban daemon` 作为独立进程运行的方式已**弃用**；请使用网关。如果你确实无法运行网关（例如无头主机策略禁止长期运行的服务等），可以使用 `--force` 逃生口让旧的独立守护进程再维持一个发布周期，但同时对同一个 `kanban.db` 运行网关嵌入式调度器和独立守护进程会导致任务认领冲突，且不受支持。

<a id="idempotent-create-for-automation-webhooks"></a>
### 幂等创建（用于自动化/Webhook）

```bash
# 第一次调用创建任务。之后使用相同键的任何调用都会返回现有任务 ID，而不会重复创建。
hermes kanban create "nightly ops review" \
    --assignee ops \
    --idempotency-key "nightly-ops-$(date -u +%Y-%m-%d)" \
    --json
```

<a id="bulk-cli-verbs"></a>
### 批量 CLI 动词

所有生命周期动词都接受多个 ID，这样你可以用一个命令清理一批任务：

```bash
hermes kanban complete t_abc t_def t_hij --result "batch wrap"
hermes kanban archive  t_abc t_def t_hij
hermes kanban unblock  t_abc t_def
hermes kanban block    t_abc "need input" --ids t_def t_hij
```

<a id="how-workers-interact-with-the-board"></a>
## 工作进程如何与看板交互

**工作进程不会通过 shell 调用 `hermes kanban`。** 当调度器启动一个工作进程时，它会在子进程的环境中设置 `HERMES_KANBAN_TASK=t_abcd`，这个环境变量会在模型的 schema 中启用一套专用的**看板工具集**。同样的工具集也适用于在其工具集配置中启用了 `kanban` 的编排配置文件。这些工具通过 Python 的 `kanban_db` 层直接读取和修改看板，与 CLI 的方式相同。运行中的工作进程像调用其他工具一样调用这些工具；它永远不会看到或需要 `hermes kanban` CLI。
| 工具 | 用途 | 必需参数 |
|---|---|---|
| `kanban_show` | 读取当前任务（标题、正文、先前尝试、父级移交、评论、完整预格式化的 `worker_context`）。默认使用环境变量中的任务 ID。 | — |
| `kanban_list` | 列出任务摘要，支持按 `assignee`、`status`、`tenant`、归档可见性和数量限制进行过滤。适用于编排者发现看板上的工作。 | — |
| `kanban_complete` | 通过结构化的 `summary` + `metadata` 移交完成任务。 | 至少提供 `summary` / `result` 之一 |
| `kanban_block` | 向上级报告需要人工介入，同时附上 `reason`。 | `reason` |
| `kanban_heartbeat` | 在长时间操作中标识工作进程活跃。纯副作用。 | — |
| `kanban_comment` | 在任务线程中追加一条持久备注。 | `task_id`、`body` |
| `kanban_create` | （编排者）通过 assignee、可选的 parents、skills 等，向下派发子任务。 | `title`、`assignee` |
| `kanban_link` | （编排者）在创建后添加一条 `parent_id → child_id` 依赖边。 | `parent_id`、`child_id` |
| `kanban_unblock` | （编排者）将阻塞的任务移回 `ready` 状态。 | `task_id` |

一个典型的工作角色调用流程如下：

```
# 模型的工具调用，按顺序：
kanban_show()                                     # 无参数 —— 使用 HERMES_KANBAN_TASK
# (模型读取返回的 worker_context，通过终端/文件工具执行工作)
kanban_heartbeat(note="完成一半 —— 8 个文件已转换 4 个")
# (更多工作)
kanban_complete(
    summary="将 limiter.py 迁移至令牌桶；新增 14 个测试，全部通过",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
)
```

而**编排者**工作角色则是向下派发：

```
kanban_show()
kanban_create(
    title="调研 ICP 融资 2024-2026",
    assignee="researcher-a",
    body="聚焦种子轮 + A 轮，北美地区，AI 相关领域",
)
# → 返回 {"task_id": "t_r1", ...}
kanban_create(title="调研 ICP 融资 —— 欧洲视角", assignee="researcher-b", body="…")
# → 返回 {"task_id": "t_r2", ...}
kanban_create(
    title="整合发现并生成启动简报",
    assignee="writer",
    parents=["t_r1", "t_r2"],                     # 当两个子任务都完成时，自动变为 ready
    body="一页纸，300 字，中性语气",
)
kanban_complete(summary="已拆分为 2 个调研任务 + 1 个写作任务；并建立了依赖链接")
```

标注了“（编排者）”的工具 —— `kanban_list`、`kanban_create`、`kanban_link`、`kanban_unblock` 以及对外部任务的 `kanban_comment` —— 都是通过同一套工具集提供的；惯例（由 `kanban-orchestrator` skill 强制）是工作角色配置文件不会派发或路由无关的工作，而编排者配置文件不会执行实现工作。由调度器生成的工作角色仍然受任务范围的限制，不能执行破坏性的生命周期操作，也不能修改无关任务。

<a id="why-tools-instead-of-shelling-to-hermes-kanban"></a>
### 为什么使用工具而不是通过 shell 调用 `hermes kanban`

三个原因：

1. **后端可移植性。** 如果工作角色的终端工具指向远程后端（Docker / Modal / Singularity / SSH），那么它们会在容器*内部*执行 `hermes kanban complete`，而容器内既未安装 `hermes`，也未挂载 `~/.hermes/kanban.db`。看板工具在 Agent 自身的 Python 进程中运行，无论终端后端是什么，始终能访问 `~/.hermes/kanban.db`。
2. **没有 shell 引用的脆弱性。** 通过 shlex + argparse 传递 `--metadata '{"files": [...]}'` 是一个潜在的隐患。结构化工具参数完全绕过了这个问题。
3. **更好的错误处理。** 工具返回的是结构化的 JSON，模型可以直接理解，而不是需要解析的 stderr 字符串。
**普通会话零 schema 占用。** 一个常规的 `hermes chat` 会话在其 schema 中没有任何 `kanban_*` 工具，除非当前启用的配置文件明确为 orchestrator 工作启用了 `kanban` 工具集。由 Dispatcher 生成的任务 worker 会获得任务级别的作用域工具，因为设置环境变量 `HERMES_KANBAN_TASK`；orchestrator 配置文件则通过配置获得更宽的路由功能。对于从不接触 kanban 的用户，不会出现工具膨胀。

`kanban-worker` 和 `kanban-orchestrator` 技能教会模型何时以及按什么顺序调用哪个工具。

<a id="recommended-handoff-evidence"></a>
### 推荐的交接证据

`kanban_complete(summary=..., metadata={...})` 有意设计得灵活：
summary 是供人阅读的结案说明，而 `metadata` 是机器可读的交接数据，
下游 Agent、审查人员或仪表盘可以直接复用，无需解析自然语言。

对于工程和审查任务，建议使用以下可选的 metadata 结构：

```json
{
  "changed_files": ["path/to/file.py"],
  "verification": ["pytest tests/hermes_cli/test_kanban_db.py -q"],
  "dependencies": ["父任务 ID 或外部 issue（如果有）"],
  "blocked_reason": null,
  "retry_notes": "之前失败的原因（如果是重试）",
  "residual_risk": ["未测试或仍需人工审查的内容"]
}
```

这些键是约定，不是 schema 要求。有用的特性是每个 worker 都留下足够的证据，让下一个阅读者能快速回答四个问题：

1. 什么发生了变化？
2. 如何验证的？
3. 如果失败，什么可以解除阻塞或重试？
4. 还有哪些风险被故意保留未处理？

请将机密信息、原始日志、令牌、OAuth 材料以及无关的转录内容排除在 `metadata` 之外。改用指针和摘要。如果某个任务没有文件或测试，请在 `summary` 中明确说明，并使用 `metadata` 存放已有的证据，例如源 URL、issue ID 或人工审查步骤。

<a id="the-worker-skill"></a>
### Worker 技能

任何能够处理 kanban 任务的配置文件都必须加载 `kanban-worker` 技能。它教会 worker 通过**工具调用**（而非 CLI 命令）完成完整的生命周期：

1. 生成时，调用 `kanban_show()` 读取标题 + 正文 + 父任务交接信息 + 之前的尝试 + 完整评论线程。
2. `cd $HERMES_KANBAN_WORKSPACE`（通过终端工具）并在该目录下工作。
3. 在长时间操作期间每隔几分钟调用一次 `kanban_heartbeat(note="...")`。**如果工作可能运行超过 1 小时，请至少每小时调用一次 `kanban_heartbeat`** — Dispatcher 会回收那些运行时间超过 `kanban.dispatch_stale_timeout_seconds`（默认 4 小时）且在过去一小时内没有心跳的任务，假设 worker 崩溃了且未清理。回收是无害的（任务回到 `ready` 状态准备重新分发，不会增加失败计数器），但你会丢失当前运行的进度。
4. 完成时调用 `kanban_complete(summary="...", metadata={...})`，如果卡住则调用 `kanban_block(reason="...")`。

最后的 `kanban_complete` / `kanban_block` 调用是 worker 协议的一部分。如果 worker 进程以状态 0 退出时任务仍处于 `running` 状态，Dispatcher 会将其视为协议违规，触发 `protocol_violation` 事件，并在下一个 tick 自动阻塞该任务，而不是将其重新生成到同一个循环中。这通常意味着模型写了一段纯文本回答并直接退出，而没有使用 Kanban 工具接口。
`kanban-worker` 是一个内置技能，在安装和更新时会同步到每个配置（profile）中——**没有**单独的技能市场安装步骤。请验证你用于看板工作线程（kanban worker）的配置（`researcher`、`writer`、`ops` 等）中是否包含它：

```bash
hermes -p <your-worker-profile> skills list | grep kanban-worker
```

如果内置副本丢失，请为对应配置恢复：

```bash
hermes -p <your-worker-profile> skills reset kanban-worker --restore
```

调度器在生成每个工作线程时也会自动传递 `--skills kanban-worker`，因此即使某个配置的默认技能配置中不包含它，工作线程仍然可以使用该模式库。

<a id="pinning-extra-skills-to-a-specific-task"></a>
### 为特定任务固定额外的技能

有时，单个任务需要执行者配置默认不携带的专业上下文——例如需要 `translation` 技能的翻译工作、需要 `github-code-review` 的审查任务、需要 `security-pr-audit` 的安全审计。与其每次都修改执行者的配置，不如直接将技能附加到任务上。

**通过编排者 Agent（常见情况——一个 Agent 将工作路由给另一个 Agent）**，使用 `kanban_create` 工具的 `skills` 数组：

```
kanban_create(
    title="translate README to Japanese",
    assignee="linguist",
    skills=["translation"],
)

kanban_create(
    title="audit auth flow",
    assignee="reviewer",
    skills=["security-pr-audit", "github-code-review"],
)
```

**通过人类（CLI / 斜杠命令）**，重复 `--skill` 参数，每个技能一次：

```bash
hermes kanban create "translate README to Japanese" \
    --assignee linguist \
    --skill translation

hermes kanban create "audit auth flow" \
    --assignee reviewer \
    --skill security-pr-audit \
    --skill github-code-review
```

**通过仪表盘**，在“创建表单”内联的 **skills** 字段中，以逗号分隔输入技能。

这些技能是 **累加** 到内置的 `kanban-worker` 之上的——调度器为每个技能（以及内置技能）发出一个 `--skills &lt;name&gt;` 标志，因此工作线程启动时会加载所有技能。技能名称必须与执行者配置中实际安装的技能匹配（运行 `hermes skills list` 查看可用技能）；没有运行时安装机制。

<a id="the-orchestrator-skill"></a>
### 编排者技能

**行为恰当的编排者不会自行完成工作。** 它将用户的目标分解为任务，将它们关联起来，将每个任务分配给你设置的一个配置，然后退到后台。`kanban-orchestrator` 技能将这些编码为工具调用模式：反诱惑规则、第零步配置发现提示（调度器对未知执行者名称静默失败，因此编排者必须确保每个卡片都存在于你机器上的实际配置中），以及一个基于 `kanban_create` / `kanban_link` / `kanban_comment` 的分解操作手册。

一个典型的编排者回合（两个并行研究员交给一个写手）：

```
# 用户目标："起草一篇关于ICP融资格局的发布文章"
kanban_create(title="research ICP funding, NA angle",  assignee="researcher-a", body="…")  # → t_r1
kanban_create(title="research ICP funding, EU angle",  assignee="researcher-b", body="…")  # → t_r2
kanban_create(
    title="synthesize ICP funding research into launch post draft",
    assignee="writer",
    parents=["t_r1", "t_r2"],        # 当两位研究员都完成后，升级为'ready'状态
    body="one-pager, neutral tone, cite sources inline",
)                                     # → t_w1
# 可选：在不重新创建任务的情况下，添加后来发现的跨任务依赖
kanban_link(parent_id="t_r1", child_id="t_followup")
kanban_complete(
    summary="decomposed into 2 parallel research tasks → 1 synthesis task; writer starts when both researchers finish",
)
```
`kanban-orchestrator` 是一个内置技能。安装和更新时会同步到每个配置文件 (profile) 中，因此无需单独通过 Skills Hub 安装。请确认它已存在于你的 orchestrator 配置文件中：

```bash
hermes -p orchestrator skills list | grep kanban-orchestrator
```

如果内置副本丢失，可通过以下命令恢复该配置文件的副本：

```bash
hermes -p orchestrator skills reset kanban-orchestrator --restore
```

为获得最佳效果，请将其与一个工具集仅限于看板操作（`kanban`、`gateway`、`memory`）的配置文件搭配使用，这样协调器 (orchestrator) 即使尝试也无法执行实现任务。

<a id="dashboard-gui"></a>
## 仪表盘 (GUI)

`/kanban` CLI 和斜杠命令足以无头运行看板，但对于有人参与的流程（人工分类、跨配置文件监督、阅读评论线程、在列之间拖拽卡片），可视化看板通常是更合适的界面。Hermes 将其作为**内置仪表盘插件**提供，位于 `plugins/kanban/` 目录下——它不是核心功能，也不是独立服务——遵循 [扩展仪表盘](./extending-the-dashboard) 中列出的模式。

使用以下命令打开：

```bash
hermes kanban init      # 一次性操作：如果 kanban.db 不存在则创建
hermes dashboard        # 导航栏中会出现 "Kanban" 标签页，位于 "Skills" 之后
```

<a id="what-the-plugin-gives-you"></a>
### 该插件提供的功能

- **Kanban 标签页**：每个状态显示一列：`triage`、`todo`、`ready`、`running`、`blocked`、`done`（启用“显示归档”后还会显示 `archived` 列）。
  - `triage` 是存放粗略想法的待处理列。默认情况下（`kanban.auto_decompose: true`），调度器 (dispatcher) 会自动对进入此列的任务运行**分解器 (decomposer)**——orchestrator 配置文件会读取粗略想法，查看你的配置文件列表（包含描述），然后将任务分解为一个小型子任务图，并路由到最合适的专家配置文件。原始任务作为所有子任务的父任务保持存活，以便当所有子任务完成时，orchestrator 重新唤醒并判断完成情况。点击页面顶部的 **编排：自动/手动** 按钮（或设置 `kanban.auto_decompose: false`）可切换到手动模式，此时 triage 任务将保持不动，直到你点击卡片上的 **⚗ 分解** 按钮或运行 `hermes kanban decompose &lt;id&gt;`。对于不需要分解的任务（或没有 orchestrator 配置文件的设置），**✨ 细化** 按钮会通过相同的 LLM 机制对单个任务进行规格重写（标题 + 正文，包含目标、方法、验收标准）。参见下面的 [自动编排 vs 手动编排](#auto-vs-manual-orchestration)。
- 卡片显示任务 ID、标题、优先级徽章、租户标签、分配的配置文件、评论/链接数量、**进度标签**（当任务有依赖项时显示 `N/M 子任务完成`）以及“创建于 N 时间前”。每个卡片都有一个复选框用于多选。
- **Running 列内按配置文件分道**——工具栏复选框可切换按负责人对 Running 列进行子分组。
- **通过 WebSocket 实时更新**——插件以短轮询间隔追踪仅追加的 `task_events` 表；当任何配置文件（CLI、gateway 或另一个仪表盘标签页）执行操作时，看板会立即反映变化。重新加载带有防抖处理，因此事件突发只会触发一次重新获取。
- **拖拽**卡片到不同列以更改状态。拖拽操作会发送 `PATCH /api/plugins/kanban/tasks/:id` 请求，该请求会通过与 CLI 相同的 `kanban_db` 代码路由——三种界面永远不会出现差异。移动到破坏性状态（`done`、`archived`、`blocked`）时会提示确认。触摸设备使用基于指针的降级方案，因此看板可在平板上使用。
- **内联创建**——点击任意列标题上的 `+` 按钮，可输入标题、负责人、优先级，并可选择从下拉列表中选择一个父任务（包含所有现有任务）。按 Enter 创建任务，按 Shift+Enter 在标题字段中插入换行，按 Escape 取消。在 Triage 列创建时，新任务会自动归入 triage。
- **多选及批量操作**——按住 Shift/Ctrl 点击卡片或勾选其复选框可将其添加到选中集合。顶部会出现一个批量操作栏，提供批量状态转换、归档和重新分配（通过配置文件下拉列表，或“取消分配”）。破坏性批量操作会先确认。部分失败时，会按 ID 报告失败，而不会中止其余操作。
- **点击卡片**（不按 Shift/Ctrl）会打开一个侧边抽屉（按 Escape 或点击外部可关闭），其中包含：
  - **可编辑标题**——点击标题即可重命名。
  - **可编辑负责人/优先级**——点击元数据行即可重写。
  - **可编辑描述**——默认以 Markdown 渲染（标题、粗体、斜体、行内代码、围栏代码、`http(s)` / `mailto:` 链接、项目符号列表），并有一个“编辑”按钮可切换为文本区域。Markdown 渲染是一个小巧的、XSS 安全的渲染器——每个替换都在 HTML 转义后的输入上运行，仅允许 `http(s)` / `mailto:` 链接通过，且始终设置 `target="_blank"` 和 `rel="noopener noreferrer"`。
  - **依赖编辑器**——父任务和子任务的芯片列表，每个带有 `×` 用于取消链接，外加下拉列表（包含所有其他任务）用于添加新的父任务或子任务。循环依赖尝试会在服务端被拒绝，并给出明确提示。
  - **状态操作行**（→ triage / → ready / → running / 阻塞 / 解除阻塞 / 完成 / 归档），破坏性转换会弹出确认提示。对于 **Triage** 列中的卡片，该行还提供两个 LLM 驱动的操作：**⚗ 分解** 将任务分解为子任务图，根据描述路由到专家配置文件（orchestrator 驱动路径），**✨ 细化** 则对单个任务进行规格重写。当 LLM 认为任务不需要分解时，分解操作会回退到细化风格的提升，因此它是严格超集。这两个操作都可以通过 CLI（`hermes kanban decompose &lt;id&gt;` / `specify &lt;id&gt;` / `--all`）、任何 gateway 平台（`/kanban decompose &lt;id&gt;`）以及编程方式（`POST /api/plugins/kanban/tasks/:id/decompose` 和 `…/specify`）访问。在 `config.yaml` 中通过 `auxiliary.kanban_decomposer` 和 `auxiliary.triage_specifier` 配置模型。
  - 结果部分（同样以 Markdown 渲染）、评论线程（按 Enter 提交）、最近 20 条事件。
- **工具栏过滤器**——自由文本搜索、租户下拉列表（默认为 `config.yaml` 中的 `dashboard.kanban.default_tenant`）、负责人下拉列表、“显示归档”切换开关、“按配置文件分道”切换开关，以及一个 **Nudge 调度器** 按钮，这样你就不必等待下一个 60 秒的滴答周期。
视觉上，目标界面是大家熟悉的 Linear / Fusion 布局：深色主题、带计数的列标题、彩色状态点、以及用于优先级和租户的药丸标签。该插件只读取主题 CSS 变量（`--color-*`、`--radius`、`--font-mono` 等），因此它会根据当前激活的仪表板主题自动换肤。

<a id="auto-vs-manual-orchestration"></a>
### 自动编排 vs 手动编排

看板有两种方式处理你放入「分类（Triage）」列的任务：

**自动（默认）** — `kanban.auto_decompose: true`。网关内嵌的调度器在每个 tick 上运行**分解器**，上限由 `kanban.auto_decompose_per_tick` 控制（默认每个 tick 处理 3 个任务），这样批量载入分类任务时不会爆发式消耗辅助 LLM。分解器会读取粗略思路，查看你已安装的 Profile 及其描述，然后让 LLM 生成一个 JSON 任务图：要创建哪些任务、分配给谁、以及它们之间的依赖关系。原始的分类任务成为图中每个叶节点的父任务，因此它会一直存活到整个图完成——然后升级回 `ready` 状态，其负责人（编排 Profile）可以判断完成情况，如果工作未完成则添加更多任务。这就是“扔下一行描述，然后走人”的流程。

**手动** — `kanban.auto_decompose: false`。分类任务会一直留在分类列中，直到你主动操作。点击卡片上的 **⚗ 分解** 按钮，运行 `hermes kanban decompose &lt;id&gt;`（或 `--all`），或者在聊天中使用 `/kanban decompose &lt;id&gt;`。这与看板在分解器出现之前的行为一致，适合需要完全控制何时运行什么任务的场景。

可以通过看板页面顶部的 **编排：自动/手动** 药丸标签（翡翠色 = 自动，哑光灰 = 手动）在这两种模式之间切换，或者直接编辑 `config.yaml`。两种模式都与 `hermes kanban specify` 共存——当你不需要扇出时，它仍然可以作为单任务规格重写可用。

分解器的路由决策依赖于 Profile 描述，这是每个 Profile 的标签基础设置，你可以通过 `hermes profile create --description "..."`、`hermes profile describe &lt;name&gt; --text "..."`、`hermes profile describe &lt;name&gt; --auto`（LLM 从 Profile 已安装的技能和模型生成描述），或通过仪表板展开的 **编排设置** 面板中的每个 Profile 编辑器来设置。没有描述的 Profile 仍会出现在列表中——可以按名称路由，只是不够精确。分解器**绝不会**将子任务分配为 `assignee=None`：当 LLM 选择了未知的 Profile 时，子任务会被路由到 `kanban.default_assignee`（如果未设置，则路由到当前活动的默认 Profile）。

配置旋钮（全部位于 `~/.hermes/config.yaml` 中的 `kanban:` 下）：

| 键 | 默认值 | 用途 |
|---|---|---|
| `auto_decompose` | `true` | 调度器在每个 tick 上自动运行分解器。 |
| `auto_decompose_per_tick` | `3` | 每个调度器 tick 最多分解的任务数。超出部分推迟到下一个 tick。 |
| `orchestrator_profile` | `""` | 拥有分解操作的 Profile。空值 = 回退到当前活动的默认 Profile。 |
| `default_assignee` | `""` | 当 LLM 选择未知 Profile 时，子任务的落地方。空值 = 回退到当前活动的默认 Profile。 |
两个辅助 LLM 插槽：

| Key | 用途 |
|---|---|
| `auxiliary.kanban_decomposer` | 生成任务图的模型（由 Decompose 调用）。设置 `provider`/`model` 以覆盖主聊天模型。 |
| `auxiliary.profile_describer` | 自动生成配置文件描述的模型（由 `hermes profile describe --auto` 调用）。 |

<a id="architecture"></a>
### 架构

GUI 严格是一个**通过数据库读取 + 通过 kanban_db 写入**的层，本身不含任何领域逻辑：

<!-- ascii-guard-ignore -->
```
┌────────────────────────┐      WebSocket (跟踪 task_events)
│   React SPA (插件)    │ ◀──────────────────────────────────┐
│   HTML5 拖放          │                                    │
└──────────┬─────────────┘                                    │
           │ REST 通过 fetchJSON                              │
           ▼                                                  │
┌────────────────────────┐     写入调用 kanban_db.*          │
│  FastAPI 路由          │     直接使用——与 CLI /kanban      │
│  plugins/kanban/       │     动词相同的代码路径             │
│  dashboard/plugin_api.py                                    │
└──────────┬─────────────┘                                    │
           │                                                  │
           ▼                                                  │
┌────────────────────────┐                                    │
│  ~/.hermes/kanban.db   │ ───── 追加 task_events ────────────┘
│  (WAL, 共享)           │
└────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

<a id="rest-surface"></a>
### REST 接口

所有路由都挂载在 `/api/plugins/kanban/` 下，并通过仪表盘的临时会话令牌保护：

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/board?tenant=&lt;name&gt;&include_archived=…` | 按状态列分组的完整看板，外加用于筛选下拉框的租户和负责人 |
| `GET` | `/tasks/:id` | 任务 + 评论 + 事件 + 链接 |
| `POST` | `/tasks` | 创建（包装 `kanban_db.create_task`，接受 `triage: bool` 和 `parents: [id, …]`） |
| `PATCH` | `/tasks/:id` | 状态 / 负责人 / 优先级 / 标题 / 正文 / 结果 |
| `POST` | `/tasks/bulk` | 对 `ids` 中的每个 ID 应用相同的补丁（状态 / 归档 / 负责人 / 优先级）。单个 ID 失败不影响其他，会报告失败信息 |
| `POST` | `/tasks/:id/comments` | 追加一条评论 |
| `POST` | `/tasks/:id/specify` | 运行 triage 指定器——辅助 LLM 完善任务正文，并将其从 `triage` 提升为 `todo`。返回 `{ok, task_id, reason, new_title}`；如果“不在 triage”/无辅助客户端/LLM 错误，则 `ok=false` 并附带可读原因，返回 200，而非 4xx |
| `POST` | `/tasks/:id/decompose` | 运行看板分解器——辅助 LLM 生成任务图，然后辅助工具原子地创建子任务 + 链接根任务 + 将 `triage → todo`。返回 `{ok, task_id, reason, fanout, child_ids, new_title}`。与 `/specify` 一样，LLM 错误时返回 200。 |
| `GET` | `/profiles` | 列出已安装的配置文件及其描述（供仪表盘的配置文件描述编辑器和编排器选择器使用）。 |
| `PATCH` | `/profiles/:name` | 设置或清除配置文件的描述（用户编写——`description_auto: false`）。返回 `{ok, profile, description}`。 |
| `POST` | `/profiles/:name/describe-auto` | 通过 `auxiliary.profile_describer` 为配置文件生成描述。持久化时设置 `description_auto: true`，方便仪表盘显示“审核”徽章。 |
| `GET` | `/orchestration` | 读取看板编排设置（`orchestrator_profile`、`default_assignee`、`auto_decompose`）以及回退后的*解析*有效值。 |
| `PUT` | `/orchestration` | 更新 `config.yaml` 中三个编排键中的一个或多个。会验证非空配置文件名称是否存在。 |
| `POST` | `/links` | 添加依赖（`parent_id` → `child_id`） |
| `DELETE` | `/links?parent_id=…&child_id=…` | 移除依赖 |
| `POST` | `/dispatch?max=…&dry_run=…` | 触发调度器——跳过 60 秒等待 |
| `GET` | `/config` | 从 `config.yaml` 读取 `dashboard.kanban` 偏好设置——`default_tenant`、`lane_by_profile`、`include_archived_by_default`、`render_markdown` |
| `WS` | `/events?since=&lt;event_id&gt;` | `task_events` 行的实时流 |
每个处理程序都是一个薄封装层——该插件约700行Python代码（路由器+WebSocket尾部+批量处理器+配置读取器），且不添加新的业务逻辑。一个简单的`_conn()`助手会在每次读写时自动初始化`kanban.db`，因此无论是用户先打开仪表盘、直接调用REST API，还是运行`hermes kanban init`，全新安装都能正常工作。

<a id="dashboard-config"></a>
### 仪表盘配置

在`~/.hermes/config.yaml`中，`dashboard.kanban`下的任意键会更改选项卡的默认设置——插件会在加载时通过`GET /config`读取它们：

```yaml
dashboard:
  kanban:
    default_tenant: acme              # 预选租户过滤器
    lane_by_profile: true             # “按Profile分泳道”切换开关的默认值
    include_archived_by_default: false
    render_markdown: true             # 设为false则使用纯<pre>渲染
```

每个键都是可选的，若未设置则回退到显示的默认值。

<a id="security-model"></a>
### 安全模型

仪表盘的HTTP认证中间件[明确跳过`/api/plugins/`](./extending-the-dashboard#backend-api-routes)——插件路由默认无需认证，因为仪表盘默认绑定到localhost。这意味着主机上的任何进程都可以访问看板的REST接口。

WebSocket额外采取了一步：它要求将仪表盘的临时会话令牌作为`?token=…`查询参数传递（浏览器无法在升级请求中设置`Authorization`），这与浏览器内PTY桥接使用的模式一致。

如果运行`hermes dashboard --host 0.0.0.0`，每个插件路由（包括看板）都会从网络可达。**不要在共享主机上这样做。**看板包含任务正文、评论和工作区路径；攻击者若能访问这些路由，就能读取你的所有协作表面，还可以创建/重新分配/归档任务。

`~/.hermes/kanban.db`中的任务特意不区分profile（这是协调原语）。如果通过`hermes -p &lt;profile&gt; dashboard`打开仪表盘，看板仍会显示主机上任何其他profile创建的任务。同一用户拥有所有profile，但如果存在多个角色，这一点值得了解。

<a id="live-updates"></a>
### 实时更新

`task_events`是一个仅追加的SQLite表，带有单调递增的`id`。WebSocket端点持有每个客户端最后看到的事件ID，并在新行出现时推送它们。当事件批量到达时，前端会重新加载（非常便宜的）看板端点——这比尝试从每种事件类型修补本地状态更简单且更正确。WAL模式意味着读取循环永远不会阻塞分发器的`BEGIN IMMEDIATE`声明事务。

<a id="extending-it"></a>
### 扩展插件

该插件使用标准的Hermes仪表盘插件合约——完整的清单引用、Shell插槽、页面作用域插槽以及插件SDK，请参见[扩展仪表盘](./extending-the-dashboard)。额外的列、自定义卡片外观、按租户过滤的布局或完整的`tab.override`替换，都可以在不派生此插件的前提下实现。

要在不删除的情况下禁用：在`config.yaml`中添加`dashboard.plugins.kanban.enabled: false`（或删除`plugins/kanban/dashboard/manifest.json`）。
<a id="scope-boundary"></a>
### 范围边界

GUI 被故意做得简洁。插件所有功能都能通过 CLI 访问；插件只是让人类用起来更舒适。自动分配、预算、治理门禁和组织结构视图仍保留在用户空间——一个路由器配置、另一个插件，或者复用 `tools/approval.py`——正如设计规范中“范围之外”部分所列出的那样。

<a id="cli-command-reference"></a>
## CLI 命令参考

这是你（或脚本、cron、仪表板）驱动看板所使用的界面。在分发器内运行的工人使用 `kanban_*` [工具表面](#how-workers-interact-with-the-board)执行相同操作——这里的 CLI 和那里的工具都通过 `kanban_db` 路由，因此两个表面在结构上保持一致。

```
hermes kanban init                                     # 创建 kanban.db + 打印守护进程提示
hermes kanban create "<title>" [--body ...] [--assignee <profile>]
                                [--parent <id>]... [--tenant <name>]
                                [--workspace scratch|worktree|worktree:<path>|dir:<path>]
                                [--branch <name>]
                                [--priority N] [--triage] [--idempotency-key KEY]
                                [--max-runtime 30m|2h|1d|<seconds>]
                                [--max-retries N]
                                [--skill <name>]...
                                [--json]
hermes kanban list [--mine] [--assignee P] [--status S] [--tenant T] [--archived] [--json]
hermes kanban show <id> [--json]
hermes kanban assign <id> <profile>                    # 或 'none' 以取消分配
hermes kanban link <parent_id> <child_id>
hermes kanban unlink <parent_id> <child_id>
hermes kanban claim <id> [--ttl SECONDS]
hermes kanban comment <id> "<text>" [--author NAME]

# 批量动词——接受多个 id：
hermes kanban complete <id>... [--result "..."]
hermes kanban block <id> "<reason>" [--ids <id>...]
hermes kanban unblock <id>...
hermes kanban archive <id>...

hermes kanban tail <id>                                # 跟踪单个任务的事件流
hermes kanban watch [--assignee P] [--tenant T]        # 将 ALL 事件实时流式传输到终端
        [--kinds completed,blocked,…] [--interval SECS]
hermes kanban heartbeat <id> [--note "..."]            # 长时间操作的工人活跃信号
hermes kanban runs <id> [--json]                       # 尝试历史（每次运行一行）
hermes kanban assignees [--json]                       # 磁盘上的配置文件 + 每个受分配者的任务计数
hermes kanban dispatch [--dry-run] [--max N]           # 单次过滤
        [--failure-limit N] [--json]
hermes kanban daemon --force                           # 已弃用——独立分发器（请改用 `hermes gateway start`）
        [--failure-limit N] [--pidfile PATH] [-v]
hermes kanban stats [--json]                           # 每个状态 + 每个受分配者的计数
hermes kanban log <id> [--tail BYTES]                  # 来自 ~/.hermes/kanban/logs/ 的工人日志
hermes kanban notify-subscribe <id>                    # 网关桥接钩子（由网关中的 /kanban 使用）
        --platform <name> --chat-id <id> [--thread-id <id>] [--user-id <id>]
hermes kanban notify-list [<id>] [--json]
hermes kanban notify-unsubscribe <id>
        --platform <name> --chat-id <id> [--thread-id <id>]
hermes kanban context <id>                             # 工人看到的内容
hermes kanban specify [<id> | --all] [--tenant T]      # 充实分类列的想法
        [--author NAME] [--json]                       #   转化为完整规格并提升为待办
hermes kanban gc [--event-retention-days N]            # 工作区 + 旧事件 + 旧日志
        [--log-retention-days N]
```
所有命令也都可以在交互式 CLI 和消息网关中以斜杠命令的形式使用（参见下方的 [`/kanban` 斜杠命令](#kanban-slash-command)）。

`--max-retries` 是为调度器提供的每个任务的断路器覆盖选项。`--max-retries 1` 会在第一次尝试失败时阻塞任务，而 `--max-retries 3` 允许重试两次，并在第三次失败时阻塞。省略该参数会使用 `config.yaml` 中的 `kanban.failure_limit`，然后使用内置默认值。

## `/kanban` 斜杠命令 {#kanban-slash-command}

每个 `hermes kanban &lt;action&gt;` 动词也都可以通过 `/kanban &lt;action&gt;` 来调用——既可以在交互式 `hermes chat` 会话中，也可以在任何网关平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、电子邮件、短信）上使用。两者都会调用完全相同的 `hermes_cli.kanban.run_slash()` 入口点，该入口点复用了 `hermes kanban` 的 argparse 树，因此在 CLI、`/kanban` 和 `hermes kanban` 中，参数接口、标志和输出格式都是相同的。你无需离开聊天就能操作看板。

```
/kanban list
/kanban show t_abcd
/kanban create "write launch post" --assignee writer --parent t_research
/kanban comment t_abcd "looks good, ship it"
/kanban unblock t_abcd
/kanban dispatch --max 3
/kanban specify t_abcd                  # 将一个分类的一行描述扩展为完整规格
/kanban specify --all --tenant engineering  # 扫描一个租户下的所有分类任务
```

引用多词参数的方式与你之前在 shell 中的习惯相同——`run_slash` 使用 `shlex.split` 解析行中剩余部分，因此 `"..."` 和 `'...'` 都有效。

<a id="mid-run-usage-kanban-bypasses-the-running-agent-guard"></a>
### 运行中用法：`/kanban` 绕过正在运行的 Agent 守卫

网关通常会在 Agent 仍在思考时对斜杠命令和用户消息进行排队——这可以防止你在第一个回合还未结束时意外启动第二个回合。**`/kanban` 明确不受此守卫限制。** 看板存储在 `~/.hermes/kanban.db` 中，而不是正在运行的 Agent 的状态中，因此读取操作（`list`、`show`、`context`、`tail`、`watch`、`stats`、`runs`）和写入操作（`comment`、`unblock`、`block`、`assign`、`archive`、`create`、`link`……）即使是在回合进行中也能立即执行。

这正是分离的意义所在：

- 一个 Worker 因等待同伴而阻塞 → 你从手机上发送 `/kanban unblock t_abcd`，调度器在下一个 tick 中就会选中该同伴。被阻塞的 Worker 不会中断——它只是不再被阻塞。
- 你发现一张需要人工上下文的卡片 → `/kanban comment t_xyz "use the 2026 schema, not 2025"` 会出现在任务线程中，并且该任务的 *下一次* 运行会在 `kanban_show()` 中读取它。
- 你想在不停止编排器的情况下了解你的任务集群正在做什么 → `/kanban list --mine` 或 `/kanban stats` 会检查看板，而不会干扰你的主对话。

<a id="auto-subscribe-on-kanban-create-gateway-only"></a>
### 在 `/kanban create` 时自动订阅（仅限网关）

当你在网关中使用 `/kanban create "…"` 创建任务时，发起聊天的会话（平台 + 聊天 ID + 线程 ID）会自动订阅该任务的终结事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）。每个终结事件你会收到一条消息——包括在 `completed` 时 Worker 结果摘要的第一行——无需轮询或记住任务 ID。
```
you> /kanban create "transcribe today's podcast" --assignee transcriber
bot> Created t_9fc1a3  (ready, assignee=transcriber)
     (subscribed — you'll be notified when t_9fc1a3 completes or blocks)

… ~8 minutes later …

bot> ✓ t_9fc1a3 completed by transcriber
     transcribed 42 minutes, saved to podcast/2026-05-04.md
```

订阅会在任务到达 `done` 或 `archived` 状态后自动移除。如果你通过 `--json`（机器输出）编写创建脚本，自动订阅会被跳过——因为假设脚本调用者希望显式地通过 `/kanban notify-subscribe` 管理订阅。

<a id="output-truncation-in-messaging"></a>
### 消息平台的输出截断

网关平台有实际的消息长度限制。如果 `/kanban list`、`/kanban show` 或 `/kanban tail` 产生的输出超过约 3800 个字符，响应会被截断，并在末尾追加 `… (truncated; use \`hermes kanban …\` in your terminal for full output)` 提示。CLI 层面则没有此类限制。

<a id="autocomplete"></a>
### 自动补全

在交互式 CLI 中，输入 `/kanban ` 后按 Tab 键，会循环显示内置子命令列表（`list`、`ls`、`show`、`create`、`assign`、`link`、`unlink`、`claim`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`、`dispatch`、`context`、`init`、`gc`）。上述 CLI 参考中列出的其余动词（`watch`、`stats`、`runs`、`log`、`assignees`、`heartbeat`、`notify-subscribe`、`notify-list`、`notify-unsubscribe`、`daemon`）同样可用——只是尚未加入自动补全提示列表。

<a id="collaboration-patterns"></a>
## 协作模式

看板支持以下八种模式，无需新增任何原语：

| 模式 | 形态 | 示例 |
|---|---|---|
| **P1 扇出** | N 个兄弟任务，同一角色 | “从5个角度并行调研” |
| **P2 流水线** | 角色链：侦察员→编辑→撰稿 | 每日简报汇编 |
| **P3 投票/法定人数** | N 个兄弟任务 + 1 个汇聚任务 | 3 个研究员 → 1 个评审员挑选 |
| **P4 长期日志** | 相同画像 + 共享目录 + cron | Obsidian 知识库 |
| **P5 人机协同** | 工作者阻塞 → 用户评论 → 解除阻塞 | 模糊决策 |
| **P6 `@提及`** | 从文本中内联路由 | `@reviewer 看看这个` |
| **P7 线程作用域工作区** | 在线程中使用 `/kanban here` | 按项目的网关线程 |
| **P8 集群耕作** | 一个画像，N 个主体 | 50 个社交账号 |
| **P9 分诊说明** | 粗略想法 → `triage` → `hermes kanban specify` 展开主体 → `todo` | “把这一行描述变成一个规范的 task” |

每种模式的具体工作示例，请参见 `docs/hermes-kanban-v1-spec.pdf`。

<a id="multi-tenant-usage"></a>
## 多租户使用

当同一个专家集群为多个业务服务时，为每个任务打上租户标签：

```bash
hermes kanban create "月度报告" \
    --assignee researcher \
    --tenant business-a \
    --workspace dir:~/tenants/business-a/data/
```

工作者会收到 `$HERMES_TENANT` 环境变量，并通过前缀对记忆写操作进行命名空间隔离。看板、调度器和画像定义都是共享的；只有数据按作用域隔离。

<a id="gateway-notifications"></a>
## 网关通知

当你从网关（Telegram、Discord、Slack 等）运行 `/kanban create …` 时，发起会话会自动订阅新创建的任务。网关的后台通知器每隔几秒轮询 `task_events`，每当发生终端事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）时，会向该会话发送一条消息。已完成的任务还会附带工作者 `--result` 的第一行，这样你无需执行 `/kanban show` 就能看到结果。
你可以通过 CLI 显式管理订阅 —— 当脚本或 cron 任务需要向非其发出的聊天发送通知时，这很有用：

```bash
hermes kanban notify-subscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
hermes kanban notify-list
hermes kanban notify-unsubscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
```

一旦任务达到 `done` 或 `archived` 状态，订阅会自动移除；无需额外清理。

<a id="runs-one-row-per-attempt"></a>
## 运行记录 —— 每次尝试对应一行

任务是工作的逻辑单元；**运行** 是执行它的一次尝试。当调度器认领一个就绪任务时，它会在 `task_runs` 中创建一行，并将 `tasks.current_run_id` 指向该行。当该次尝试结束时 —— 无论结果是完成、阻塞、崩溃、超时、派生失败还是回收 —— 该运行行会记录一个 `outcome` 并关闭，同时任务的指针被清除。一个被尝试过三次的任务会有三个 `task_runs` 行。

为什么要用两张表而不是直接修改任务：你需要**完整的尝试历史**用于真实世界的事后分析（“第二次审查尝试进入了批准，第三次合并了”），并且你需要一个干净的地方来挂载每次尝试的元数据 —— 哪些文件被更改，哪些测试运行了，审查者注意到了哪些发现。这些是运行事实，而不是任务事实。

运行也是**结构化交接**的所在。当 worker 完成一个任务时（通过 `kanban_complete(...)`），它可以传递：

- `summary`（工具参数）/ `--summary`（CLI）—— 人类可读的交接；保存在运行上；下游子任务在其 `build_worker_context` 中可以看到它。
- `metadata`（工具参数）/ `--metadata`（CLI）—— 运行上的自由格式 JSON 字典；子任务在序列化后与 summary 一同看到它。
- `result`（工具参数）/ `--result`（CLI）—— 任务行上的简短日志行（遗留字段，为向后兼容保留）。

下游子任务读取每个父任务最近一次完成的运行的 summary 和 metadata。重试的 worker 会读取自己任务上的先前尝试（outcome、summary、错误），这样就不会重复已经失败过的路径。

```
# worker 实际做的事情 —— 来自 agent 循环内部的工具调用：
kanban_complete(
    summary="implemented token bucket, keys on user_id with IP fallback, all tests pass",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
    result="rate limiter shipped",
)
```

当作为人类需要关闭 worker 无法完成的任务时（例如被遗弃的任务，或者你通过仪表盘手动标记为完成的任务），也可以从 CLI 执行相同的交接：

```bash
hermes kanban complete t_abcd \
    --result "rate limiter shipped" \
    --summary "implemented token bucket, keys on user_id with IP fallback, all tests pass" \
    --metadata '{"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14}'

# 查看重试任务的尝试历史：
hermes kanban runs t_abcd
#   #  OUTCOME       PROFILE           ELAPSED  STARTED
#   1  blocked       worker               12s  2026-04-27 14:02
#        → BLOCKED: 需要决定速率限制的键
#   2  completed     worker                8m   2026-04-27 15:18
#        → implemented token bucket, keys on user_id with IP fallback
```
运行记录会显示在仪表盘上（抽屉中的“运行历史”区域，每次尝试对应一行彩色记录），同时也通过 REST API 暴露（`GET /api/plugins/kanban/tasks/:id` 返回一个 `runs[]` 数组）。`PATCH /api/plugins/kanban/tasks/:id` 配合 `{status: "done", summary, metadata}` 会将两者转发到内核，因此仪表盘的“标记完成”按钮与 CLI 等效。`task_events` 行携带其所属的 `run_id`，以便 UI 按尝试分组事件；`completed` 事件将第一行摘要嵌入其有效载荷（最长 400 字符），这样网关通知器无需二次 SQL 查询即可渲染结构化交接。

**批量关闭注意事项。** `hermes kanban complete a b c --summary X` 会被拒绝——结构化交接是按运行记录的，因此将相同摘要复制粘贴到 N 个任务几乎总是错误的。不带有 `--summary` / `--metadata` 的批量关闭仍然适用于常见的“我完成了一堆管理任务”场景。

**状态变更导致的回收运行。** 如果你在仪表盘中将一个正在运行的任务拖离 `running` 状态（拖回 `ready`，或者直接拖到 `todo`），或者归档了一个仍在运行的任务，则正在进行的运行记录将以 `outcome='reclaimed'` 关闭，而不是被孤立。当 `tasks.current_run_id` 为 `NULL` 时，`task_runs` 行始终处于终态，反之亦然——这个不变性在 CLI、仪表盘、调度器和通知器中均保持一致。

**从未认领的完成状态的合成运行。** 完成或阻塞一个从未被认领的任务（例如，用户从仪表盘关闭一个 `ready` 任务并附带摘要，或者 CLI 用户执行 `hermes kanban complete &lt;ready-task&gt; --summary X`）否则会丢失交接信息。相反，内核会插入一条持续时间为零的运行记录（`started_at == ended_at`），携带摘要/元数据/原因，以便尝试历史保持完整。`completed` / `blocked` 事件的 `run_id` 指向该行。

**实时抽屉刷新。** 当仪表盘的 WebSocket 事件流报告用户当前正在查看的任务有新事件时，抽屉会自动重新加载（通过一个按任务计数的计数器，该计数器被织入其 `useEffect` 依赖列表中）。不再需要关闭并重新打开抽屉才能看到运行记录的新行或更新后的结果。

<a id="forward-compatibility"></a>
### 前向兼容性

`tasks` 表上的两个可空列为 v2 工作流路由预留：`workflow_template_id`（该任务所属的模板）和 `current_step_key`（该模板中当前处于活动状态的步骤）。v1 内核在路由时忽略它们，但允许客户端写入，因此 v2 发布版可以在不进行额外模式迁移的情况下添加路由机制。

<a id="event-reference"></a>
## 事件参考

每次状态转换都会向 `task_events` 表追加一行。每一行都携带可选的 `run_id`，以便 UI 按尝试对事件进行分组。事件种类分为三个簇，方便过滤（`hermes kanban watch --kinds completed,gave_up,timed_out`）：

**生命周期**（任务作为逻辑单元发生的变化）：

| 种类 | 有效载荷 | 时机 |
|---|---|---|
| `created` | `{assignee, status, parents, tenant}` | 任务插入时。`run_id` 为 `NULL`。 |
| `promoted` | — | 因为所有父任务都已 `done`，任务从 `todo` 变为 `ready`。`run_id` 为 `NULL`。 |
| `claimed` | `{lock, expires, run_id}` | 调度器原子性地认领了一个 `ready` 任务以进行衍生。 |
| `completed` | `{result_len, summary?}` | 工作进程写入了 `--result` / `--summary`，且任务变为 `done`。`summary` 是第一行交接摘要（400 字符上限）；完整版本存在于运行记录行中。如果在从未认领的任务上调用了 `complete_task` 并带有交接字段，则会合成一条持续时间为零的运行记录，以便 `run_id` 仍然指向某个内容。 |
| `blocked` | `{reason}` | 工作进程或用户将任务翻转为 `blocked`。在对从未认领的任务调用且带有 `--reason` 时，会合成一条持续时间为零的运行记录。 |
| `unblocked` | — | 任务从 `blocked` 变回 `ready`，可以是手动操作或通过 `/unblock`。`run_id` 为 `NULL`。 |
| `archived` | — | 从默认看板中隐藏。如果任务仍在运行，则携带因回收操作而被回收的运行记录的 `run_id`。 |
**编辑**（非转换类、由人类驱动的变更）：

| 类型 | 数据载荷 | 触发时机 |
|---|---|---|
| `assigned` | `{assignee}` | 负责人变更（包括取消分配）。 |
| `edited` | `{fields}` | 标题或正文更新。 |
| `reprioritized` | `{priority}` | 优先级变更。 |
| `status` | `{status}` | 看板拖拽直接写入状态（例如 `todo → ready`）。当从 `running` 拖走时，会携带被回收运行的 `run_id`；否则 `run_id` 为 NULL。 |

**工作进程遥测**（关于执行过程，而非逻辑任务）：

| 类型 | 数据载荷 | 触发时机 |
|---|---|---|
| `spawned` | `{pid}` | 调度器成功启动了一个工作进程。 |
| `heartbeat` | `{note?}` | 工作进程调用 `hermes kanban heartbeat $TASK` 以在长操作期间表明存活状态。 |
| `reclaimed` | `{stale_lock}` | 声明 TTL 到期但未完成；任务回到 `ready` 状态。 |
| `crashed` | `{pid, claimer}` | 工作进程 PID 已不存在但 TTL 尚未到期。 |
| `timed_out` | `{pid, elapsed_seconds, limit_seconds, sigkill}` | 超过 `max_runtime_seconds`；调度器发送 SIGTERM（5 秒宽限期后发送 SIGKILL）并重新入队。 |
| `stale` | `{elapsed_seconds, last_heartbeat_at, heartbeat_age_seconds, timeout_seconds, pid, terminated}` | 任务运行时间超过 `kanban.dispatch_stale_timeout_seconds`（默认 4 小时）且在过去一小时内未收到 `kanban_heartbeat`。调度器向本机工作进程（如果有）发送 SIGTERM，将任务重置为 `ready` 状态以便重新调度。此操作不会增加失败计数器（stale 是调度器侧的缺席检测，不是工作进程故障）。运行长操作的工作进程应至少每小时调用一次 `kanban_heartbeat` 以避免此情况。 |
| `respawn_guarded` | `{reason}` | 调度器拒绝在本轮中重新生成此 ready 任务。原因：`blocker_auth`（上次失败是配额/认证/429 错误——等待速率窗口重置）、`recent_success`（过去一小时内发生过一次成功的运行——等待审查后再重新运行）、`active_pr`（近期评论中出现了 GitHub PR 链接——之前的工作进程已打开了 PR）。任务保持在 `ready` 状态；下一轮会再次尝试生成。如果底层条件持续存在，在 `failure_limit` 次失败后，正常的 `consecutive_failures` 断路器会通过 `gave_up` 自动阻止。 |
| `spawn_failed` | `{error, failures}` | 一次生成尝试失败（PATH 缺失、工作区无法挂载等）。计数器递增；任务返回 `ready` 状态以重试。 |
| `protocol_violation` | `{pid, claimer, exit_code}` | 工作进程已成功退出但任务仍处于 `running` 状态，通常是因为它做出了应答但没有调用 `kanban_complete` 或 `kanban_block`。调度器同时发出 `gave_up` 并立即自动阻止，不再重试。 |
| `gave_up` | `{failures, effective_limit, limit_source, error}` | 连续 N 次非成功尝试后断路器触发。任务以最后一次错误自动阻止。有效限制的解析顺序为：任务 `max_retries`，然后是调度器 `failure_limit` / `kanban.failure_limit`，最后是内置默认值。 |
`hermes kanban tail &lt;id&gt;` 会针对单个任务显示这些信息。`hermes kanban watch` 则会在整个看板范围内实时流式输出这些信息。

<a id="out-of-scope"></a>
## 超出范围

看板设计为单主机运行。`~/.hermes/kanban.db` 是一个本地 SQLite 文件，调度器会在同一台机器上启动工作进程。不支持在两台主机上运行共享看板——没有用于“主机 A 上的工作进程 X，主机 B 上的工作进程 Y”的协调原语，并且崩溃检测路径假设 PID 是主机本地的。如果你需要多主机支持，请在每个主机上运行独立的看板，并使用 `delegate_task` / 消息队列来桥接它们。

<a id="design-spec"></a>
## 设计规范

完整的设计——包括架构、并发正确性、与其他系统的比较、实现计划、风险、未解决的问题——都记录在 `docs/hermes-kanban-v1-spec.pdf` 中。在提交任何改变行为的 PR 之前，请先阅读该文档。
