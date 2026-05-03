---
sidebar_position: 16
title: "持久目标"
description: "设定一个持续目标，让 Hermes 跨轮次持续工作直到完成。我们对 Ralph 循环的实现。"
---

# 持久目标（`/goal`） {#persistent-goals-goal}

`/goal` 为 Hermes 设定一个跨轮次持续存在的目标。每轮结束后，一个轻量级评判模型会检查助手的最新回复是否满足目标。如果不满足，Hermes 会自动将延续提示重新注入同一会话并继续工作——直到目标达成、你暂停或清除目标、或者轮次预算耗尽。

这是我们对 **Ralph 循环** 的实现，直接受 Eric Traut（OpenAI）在 [Codex CLI 0.128.0 的 `/goal`](https://github.com/openai/codex) 启发。核心思想——让目标跨轮次存活，不达成不停止——来自他们。这里的实现是独立的，并适配了 Hermes 的架构。

## 何时使用 {#when-to-use-it}

当你希望 Hermes 自行迭代，而无需每轮都重新提示时，使用 `/goal`：

- "修复 `src/` 中所有 lint 错误，并验证 `ruff check` 通过"
- "将仓库 Y 中的功能 X 移植过来，包括测试，并让 CI 变绿"
- "调查为什么会话 ID 在运行中压缩时偶尔漂移，并撰写一份报告"
- "构建一个小型 CLI，根据 EXIF 日期重命名文件，然后针对 photos/ 文件夹进行测试"

那些 Agent 只做一轮就停下的任务不需要 `/goal`。那些 *你本来需要说“继续”三次* 的任务，正是 `/goal` 大显身手的地方。

## 快速开始 {#quick-start}

```
/goal 修复 tests/hermes_cli/ 中所有失败的测试，并确保 scripts/run_tests.sh 对该目录通过
```

你会看到：

1. **目标已接受** — `⊙ 目标已设定（20 轮预算）：<你的目标>`
2. **第 1 轮运行** — Hermes 开始工作，就像你把目标作为普通消息发送一样。
3. **评判运行** — 本轮结束后，评判模型决定 `done` 或 `continue`。
4. **必要时循环触发** — 如果是 `continue`，你会看到 `↻ 继续向目标前进（1/20）：<评判理由>`，然后 Hermes 自动进行下一步。
5. **终止** — 最终你会看到 `✓ 目标达成：<理由>` 或 `⏸ 目标暂停 — 已使用 N/20 轮`。

## 命令 {#commands}

| 命令 | 作用 |
|---|---|
| `/goal <文本>` | 设定（或替换）持续目标。立即启动第一轮，这样你就不需要再单独发送一条消息。 |
| `/goal` 或 `/goal status` | 显示当前目标、状态和已使用轮次。 |
| `/goal pause` | 停止自动延续循环，但不清除目标。 |
| `/goal resume` | 恢复循环（将轮次计数器重置为零）。 |
| `/goal clear` | 完全删除目标。 |

在 CLI 和所有网关平台（Telegram、Discord、Slack、Matrix、Signal、WhatsApp、SMS、iMessage、Webhook、API 服务器以及 Web 仪表盘）上行为一致。

## 行为细节 {#behavior-details}

### 评判模型 {#the-judge}

每轮结束后，Hermes 会调用一个辅助模型，输入：

- 持续目标的文本
- Agent 最近一次最终回复（最后约 4 KB 文本）
- 一条系统提示，要求评判模型以严格 JSON 格式回复：`{"done": &lt;bool&gt;, "reason": "<一句话理由>"}`

评判模型刻意保守：只有当回复 **明确** 确认目标已完成、最终交付物已清晰产出、或者目标无法达成/受阻（视为 DONE 并附带受阻理由，以免在不可能的任务上浪费预算）时，才标记目标为 `done`。
### 容错语义（Fail-open semantics） {#fail-open-semantics}

如果裁判出错（网络抖动、响应格式异常、辅助客户端不可用），Hermes 会将判定结果视为 `continue`——一个出错的裁判不会阻塞进度。真正的兜底机制是 **轮次预算（turn budget）**。

### 轮次预算（Turn budget） {#turn-budget}

默认值为 20 个连续轮次（`config.yaml` 中的 `goals.max_turns`）。当预算耗尽时，Hermes 会自动暂停并明确告知你如何继续：

```
⏸ 目标已暂停 — 已使用 20/20 轮次。使用 /goal resume 继续，或使用 /goal clear 停止。
```

`/goal resume` 会将计数器重置为零，这样你就可以按可控的块继续执行。

### 用户消息始终优先 {#user-messages-always-preempt}

当目标处于激活状态时，你发送的任何真实消息都会优先于连续循环。在 CLI 上，你的消息会进入 `_pending_input`，排在排队的连续消息之前；在网关中，它会以相同的方式通过适配器 FIFO。在你的一轮之后，裁判会再次运行——所以如果你的消息恰好完成了目标，裁判会捕捉到并停止。

### 运行中的安全性（网关） {#mid-run-safety-gateway}

当 Agent 正在运行时，`/goal status`、`/goal pause` 和 `/goal clear` 可以安全执行——它们只触及控制平面状态，不会中断当前轮次。在运行中设置**新**目标（`/goal <新文本>`）会被拒绝，并提示你先 `/stop`，这样旧的连续任务就不会与新的冲突。

### 持久化 {#persistence}

目标状态存储在 `SessionDB.state_meta` 中，键为 `goal:&lt;session_id&gt;`。这意味着 `/resume` 会从你离开的地方继续——设置一个目标，合上笔记本电脑，第二天回来，执行 `/resume`，目标仍然保持在你离开时的状态（激活、暂停或完成）。

### 提示缓存 {#prompt-cache}

连续提示是一个附加到历史记录中的普通用户角色消息。它**不会**修改系统提示、切换工具集或以任何会使 Hermes 的提示缓存失效的方式接触对话。运行一个 20 轮的目标，在缓存方面的成本与 20 轮正常对话相同。

## 配置 {#configuration}

添加到 `~/.hermes/config.yaml`：

```yaml
goals:
  # 在 Hermes 自动暂停并提示你 /goal resume 之前的最大连续轮次。
  # 默认 20。如果你想要更紧凑的循环，可以降低此值；
  # 对于长时间运行的重构，可以调高。
  max_turns: 20
```

### 选择裁判模型 {#choosing-the-judge-model}

裁判使用 `goal_judge` 辅助任务。默认情况下，它会解析为你的主模型（参见[辅助模型](/user-guide/configuration#auxiliary-models)）。如果你想将裁判路由到廉价快速的模型以降低成本，可以添加覆盖：

```yaml
auxiliary:
  goal_judge:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

裁判调用很小（约 200 个输出 token），每轮运行一次，因此通常选择廉价快速的模型是正确的做法。

## 示例演练 {#example-walkthrough}

```
你: /goal 创建四个文件 /tmp/note_{1..4}.txt，每轮一个，每个文件内容为其编号文本

  ⊙ 目标已设置（20 轮预算）：创建四个文件 /tmp/note_{1..4}.txt，每轮一个，每个文件内容为其编号文本

Hermes: 现在创建 /tmp/note_1.txt。
  💻 echo "1" > /tmp/note_1.txt   (0.1s)
  我已创建 /tmp/note_1.txt，内容为 "1"。我将在下一轮继续创建剩余文件，如你所指定。

  ↻ 继续执行目标（1/20）：4 个文件中只创建了 1 个；还剩 3 个文件。

Hermes: [继续执行你的既定目标]
  💻 echo "2" > /tmp/note_2.txt   (0.1s)
  已创建 /tmp/note_2.txt。还有两个。

  ↻ 继续执行目标（2/20）：4 个文件中已创建 2 个；还剩 2 个。

Hermes: [继续执行你的既定目标]
  💻 echo "3" > /tmp/note_3.txt   (0.1s)
  已创建 /tmp/note_3.txt。

  ↻ 继续执行目标（3/20）：4 个文件中已创建 3 个；还剩 1 个。

Hermes: [继续执行你的既定目标]
  💻 echo "4" > /tmp/note_4.txt   (0.1s)
  所有四个文件已创建：/tmp/note_1.txt 到 /tmp/note_4.txt，每个文件包含其编号。

  ✓ 目标达成：所有四个文件已按指定内容创建，目标完成。

你: _
```
四个回合，一次 `/goal` 调用，零次来自你的“继续”提示。

## 当裁判判断错误时 {#when-the-judge-gets-it-wrong}

没有裁判是完美的。需要注意两种失败模式：

**假阴性——裁判认为应该继续，但实际上目标已经完成。** 回合预算会捕捉到这种情况。你会看到 `⏸ Goal paused`，然后可以执行 `/goal clear` 或直接发送一条新消息。

**假阳性——裁判认为已完成，但实际工作尚未完成。** 你会看到 `✓ Goal achieved`，但你知道并非如此。发送一条后续消息继续，或者更精确地重新设置目标：`/goal <更具体的文本>`。裁判的系统提示故意保守，以使假阳性比假阴性更少见。

如果你觉得裁判的判决不可信，`↻ Continuing toward goal` 或 `✓ Goal achieved` 行中的原因文本会准确告诉你裁判看到了什么。这通常足以诊断是目标文本有歧义还是模型的响应有问题。

## 致谢 {#attribution}

`/goal` 是 Hermes 对 **Ralph 循环**模式的实现。面向用户的设计——在多个回合中保持目标活跃，直到实现才停止，并提供创建/暂停/恢复/清除控制——由 OpenAI Codex 团队的 Eric Traut 在 [Codex CLI 0.128.0](https://github.com/openai/codex) 中推广并发布。我们的实现是独立的（中央 `CommandDef` 注册表、`SessionDB.state_meta` 持久化、辅助客户端裁判、网关侧的适配器-FIFO 延续），但想法是他们的。功劳归功于应得之人。
