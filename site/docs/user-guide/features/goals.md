---
sidebar_position: 16
title: "持久目标"
description: "设定一个长期目标，让 Hermes 跨轮次持续工作，直到目标完成。这是我们对 Ralph 循环的实现。"
---

<a id="persistent-goals-goal"></a>
# 持久目标 (`/goal`)

`/goal` 为 Hermes 设定一个跨轮次持续存在的长期目标。每轮结束后，一个轻量级评判模型会检查助手的最新回复是否满足了该目标。如果未满足，Hermes 会自动将延续提示重新注入同一会话并继续工作——直到目标达成、你暂停或清除目标，或者轮次预算耗尽。

这是我们对 **Ralph 循环** 的实现，直接受 Eric Traut (OpenAI) 在 [Codex CLI 0.128.0 的 `/goal`](https://github.com/openai/codex) 启发。其核心思想——让目标跨轮次保持活跃，不达目的不罢休——归功于他们。这里的实现是独立的，并针对 Hermes 的架构进行了适配。

<a id="when-to-use-it"></a>
## 何时使用

当你希望 Hermes 自行迭代，而无需你在每轮都重新提示时，请使用 `/goal`：

- "修复 `src/` 中的所有 lint 错误，并验证 `ruff check` 通过"
- "将功能 X 从仓库 Y 移植过来，包括测试，并让 CI 变绿"
- "调查为什么会话 ID 在运行中压缩时偶尔会漂移，并撰写一份报告"
- "构建一个小型 CLI，根据 EXIF 日期重命名文件，然后针对 photos/ 文件夹进行测试"

Agent 只执行一轮就停止的任务不需要 `/goal`。那些*你本来需要说三次“继续”*的任务，才是这个功能大放异彩的地方。

<a id="quick-start"></a>
## 快速开始

```
/goal 修复 tests/hermes_cli/ 中所有失败的测试，并确保 scripts/run_tests.sh 对该目录执行通过
```

你会看到：

1. **目标已接受** — `⊙ 目标已设定 (20 轮预算): <你的目标>`
2. **第 1 轮运行** — Hermes 开始工作，就像你把目标作为普通消息发送一样。
3. **评判运行** — 本轮结束后，评判模型决定是 `完成` 还是 `继续`。
4. **必要时触发循环** — 如果是 `继续`，你会看到 `↻ 继续向目标前进 (1/20): <评判原因>`，然后 Hermes 自动执行下一步。
5. **终止** — 最终你会看到 `✓ 目标达成: <原因>` 或 `⏸ 目标已暂停 — 已使用 N/20 轮`。

<a id="commands"></a>
## 命令

| 命令 | 功能 |
|---|---|
| `/goal <文本>` | 设定（或替换）长期目标。立即启动第一轮，因此你无需再单独发送消息。 |
| `/goal` 或 `/goal status` | 显示当前目标、其状态以及已使用的轮次。 |
| `/goal pause` | 停止自动延续循环，但不清除目标。 |
| `/goal resume` | 恢复循环（将轮次计数器重置为零）。 |
| `/goal clear` | 完全清除目标。 |

在 CLI 和所有网关平台（Telegram、Discord、Slack、Matrix、Signal、WhatsApp、SMS、iMessage、Webhook、API 服务器以及 Web 仪表盘）上工作方式完全相同。

<a id="adding-criteria-mid-goal-subgoal"></a>
## 在目标进行中添加标准：`/subgoal`

当目标处于激活状态时，你可以使用 `/subgoal <文本>` 附加额外的验收标准，而无需重置循环。每次调用都会向目标的子目标列表中添加一个编号项；Agent 在下一轮看到的**延续提示**包含原始目标以及一个“用户在中途添加的额外标准”块，并且**评判提示**会被重写，使得判定必须考虑每个子目标——只有当原始目标**和**每个子目标都满足时，目标才会被标记为完成。
| 命令 | 作用 |
|---|---|
| `/subgoal &lt;text&gt;` | 为当前活跃的目标追加一个新标准。需要一个活跃的 `/goal`。 |
| `/subgoal`（无参数） | 显示当前编号的子目标列表。 |
| `/subgoal remove &lt;N&gt;` | 移除第 N 个子目标（从 1 开始编号）。 |
| `/subgoal clear` | 清除所有子目标，但保留原始目标不变。 |

子目标与目标一起持久化存储在 `SessionDB.state_meta` 中，因此在 `/resume` 后它们仍然存在。设置一个新的 `/goal &lt;text&gt;` 会替换目标并清除子目标列表；`/goal clear` 作用相同。

当您开始一个循环（例如“修复失败的测试”）并在中途注意到您还希望它“为刚刚修补的 bug 添加回归测试”时，可以使用此命令 —— `/subgoal add a regression test` 可以收紧成功标准而不会破坏正在运行的循环。

<a id="behavior-details"></a>
## 行为细节

<a id="the-judge"></a>
### 评判器（judge）

每轮交互后，Hermes 会调用一个辅助模型，附带以下信息：

- 当前的目标文本
- Agent 最近的最终响应（最近约 4KB 的文本）
- 一条系统提示，要求评判器以严格的 JSON 格式回复：`{"done": &lt;bool&gt;, "reason": "&lt;one-sentence rationale&gt;"}`

评判器刻意保持保守：仅当响应**明确**确认目标已完成、最终产物已清晰生成，或目标无法实现/被阻塞时（视为 DONE 并附上阻塞原因，以免在不可能的任务上浪费预算），它才会将目标标记为 `done`。

<a id="fail-open-semantics"></a>
### 故障开放语义（Fail-open semantics）

如果评判器出错（网络波动、格式错误的响应、辅助客户端不可用），Hermes 会将结果视为 `continue` —— 一个出错的评判器绝不会卡住进度。真正的兜底机制是**轮次预算**。

<a id="turn-budget"></a>
### 轮次预算

默认 20 个连续轮次（位于 `config.yaml` 中的 `goals.max_turns`）。当预算用尽时，Hermes 会自动暂停并明确告知您如何继续：

```
⏸ Goal paused — 20/20 turns used. Use /goal resume to keep going, or /goal clear to stop.
```

`/goal resume` 将计数器重置为零，因此您可以在可控的分段中继续执行。

<a id="user-messages-always-preempt"></a>
### 用户消息始终抢占

在目标处于活跃状态时，您发送的任何实际消息都会优先于连续循环。在 CLI 上，您的消息会排在队列连续任务之前，进入 `_pending_input`；在 gateway 上，它同样会通过适配器 FIFO。您的轮次结束后评判器会再次运行 —— 因此，如果您的消息恰好完成了目标，评判器会捕捉到并停止。

<a id="mid-run-safety-gateway"></a>
### 运行中安全（gateway）

当 Agent 已经在运行时，`/goal status`、`/goal pause` 和 `/goal clear` 可以安全执行 —— 它们只影响控制平面状态，不会中断当前轮次。在运行中设置**新**目标（`/goal &lt;new text&gt;`）会被拒绝，并提示您先执行 `/stop`，这样旧的连续任务就不会与新的发生冲突。

<a id="persistence"></a>
### 持久化

目标状态存储在 `SessionDB.state_meta` 中，键为 `goal:&lt;session_id&gt;`。这意味着 `/resume` 可以直接从您离开的地方继续 —— 设置一个目标，合上笔记本电脑，明天回来，执行 `/resume`，目标仍然保持您离开时的精确状态（活跃、暂停或已完成）。
<a id="prompt-cache"></a>
### 提示缓存

延续提示是一个追加到历史记录中的普通用户角色消息。它**不会**修改系统提示、更换工具集，或以任何会使 Hermes 的提示缓存失效的方式影响对话。运行一个 20 轮的目标，其缓存消耗与 20 轮普通对话相同。

<a id="configuration"></a>
## 配置

添加到 `~/.hermes/config.yaml`：

```yaml
goals:
  # 在 Hermes 自动暂停并提示你使用
  # /goal resume 之前，最大延续轮数。默认 20。
  # 如果你希望循环更紧凑，可以调低此值；
  # 对于长时间运行的重构，可以调高此值。
  max_turns: 20
```

<a id="choosing-the-judge-model"></a>
### 选择评判模型

评判模型使用 `goal_judge` 辅助任务。默认情况下，它会解析为你使用的主模型（参见[辅助模型](/user-guide/configuration#auxiliary-models)）。如果你想将评判任务路由到一个廉价快速的模型以降低成本，可以添加一个覆盖配置：

```yaml
auxiliary:
  goal_judge:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

评判调用很小（约 200 个输出 token），并且每轮运行一次，因此使用廉价快速的模型通常是正确的选择。

<a id="example-walkthrough"></a>
## 示例演练

```
你: /goal 创建四个文件 /tmp/note_{1..4}.txt，每轮一个，每个文件内容为其编号文本

  ⊙ 目标已设定（20 轮预算）：创建四个文件 /tmp/note_{1..4}.txt，每轮一个，每个文件内容为其编号文本

Hermes: 现在创建 /tmp/note_1.txt。
  💻 echo "1" > /tmp/note_1.txt   (0.1s)
  我已创建 /tmp/note_1.txt，内容为 "1"。按照你的要求，我将在下一轮继续创建剩余文件。

  ↻ 继续执行目标（1/20）：仅创建了 4 个文件中的 1 个；还剩 3 个文件。

Hermes: [继续执行你的待办目标]
  💻 echo "2" > /tmp/note_2.txt   (0.1s)
  已创建 /tmp/note_2.txt。还剩两个。

  ↻ 继续执行目标（2/20）：已创建 4 个文件中的 2 个；还剩 2 个。

Hermes: [继续执行你的待办目标]
  💻 echo "3" > /tmp/note_3.txt   (0.1s)
  已创建 /tmp/note_3.txt。

  ↻ 继续执行目标（3/20）：已创建 4 个文件中的 3 个；还剩 1 个。

Hermes: [继续执行你的待办目标]
  💻 echo "4" > /tmp/note_4.txt   (0.1s)
  所有四个文件已创建：/tmp/note_1.txt 到 /tmp/note_4.txt，每个文件内容为其编号。

  ✓ 目标达成：所有四个文件已按指定内容创建，目标完成。

你: _
```

四轮，一次 `/goal` 调用，你不需要输入任何“继续”提示。

<a id="when-the-judge-gets-it-wrong"></a>
## 当评判模型出错时

没有完美的评判模型。需要注意两种失败模式：

**假阴性——评判模型认为目标尚未完成，但实际上已完成。** 轮数预算会捕获这种情况。你会看到 `⏸ 目标已暂停`，然后可以执行 `/goal clear` 或直接发送一条新消息。

**假阳性——评判模型认为目标已完成，但实际上还有工作未完成。** 你会看到 `✓ 目标已达成`，但你知道并非如此。发送一条后续消息继续，或者更精确地重新设定目标：`/goal <更具体的文本>`。评判模型的系统提示故意设计得比较保守，以使假阳性比假阴性更少见。

如果你觉得评判结果不可信，`↻ 继续执行目标` 或 `✓ 目标已达成` 行中的原因文本会准确告诉你评判模型看到了什么。这通常足以诊断是目标文本表述模糊，还是模型的响应有问题。
<a id="attribution"></a>
## 归属

`/goal` 是 Hermes 对 **Ralph loop** 模式的实现。面向用户的设计——跨轮对话保持目标活跃，直到达成才停止，并提供创建/暂停/恢复/清除控制——由 OpenAI Codex 团队的 Eric Traut 在 [Codex CLI 0.128.0](https://github.com/openai/codex) 中推广并实际发布。我们的实现是独立的（中心化的 `CommandDef` 注册表、`SessionDB.state_meta` 持久化、辅助客户端 judge、网关侧的适配器-FIFO 续传），但思路源于他们。功劳归功于应得之人。
