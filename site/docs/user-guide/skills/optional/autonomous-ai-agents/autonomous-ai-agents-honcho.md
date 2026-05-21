---
title: "Honcho"
sidebar_label: "Honcho"
description: "使用 Hermes 配置和运用 Honcho 记忆——跨会话用户建模、多配置文件对等隔离、观察配置、辩证推理、会话摘要以及上下文预算管理。"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="honcho"></a>
# Honcho

使用 Hermes 配置和运用 Honcho 记忆——跨会话用户建模、多配置文件对等隔离、观察配置、辩证推理、会话摘要以及上下文预算管理。适用于设置 Honcho、排查记忆问题、管理带有 Honcho 对等体的配置文件、或调整观察、回忆和辩证设置。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/honcho` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/honcho` |
| 版本 | `2.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Honcho`, `Memory`, `Profiles`, `Observation`, `Dialectic`, `User-Modeling`, `Session-Summary` |
| 相关技能 | [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是当此技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="honcho-memory-for-hermes"></a>
# Hermes 的 Honcho 记忆

Honcho 提供 AI 原生的跨会话用户建模。它能在多次对话中学习用户身份，并为每个 Hermes 配置文件赋予独立的对等身份，同时共享统一的用户视图。

<a id="when-to-use"></a>
## 何时使用

- 设置 Honcho（云端或自托管）
- 排查记忆不工作 / 对等体不同步的问题
- 创建多配置文件设置，使每个 Agent 拥有自己的 Honcho 对等体
- 调整观察、回忆、辩证深度或写入频率设置
- 理解 5 个 Honcho 工具的作用及使用时机
- 配置上下文预算和会话摘要注入

<a id="setup"></a>
## 设置

<a id="cloud-app-honcho-dev"></a>
### 云端（app.honcho.dev）

```bash
hermes honcho setup
# 选择 "cloud"，粘贴来自 https://app.honcho.dev 的 API 密钥
```

<a id="self-hosted"></a>
### 自托管

```bash
hermes honcho setup
# 选择 "local"，输入基础 URL（例如 http://localhost:8000）
```

参见：https://docs.honcho.dev/v3/guides/integrations/hermes#running-honcho-locally-with-hermes

<a id="verify"></a>
### 验证

```bash
hermes honcho status    # 显示已解析的配置、连接测试、对等体信息
```

<a id="architecture"></a>
## 架构

<a id="base-context-injection"></a>
### 基础上下文注入

当 Honcho 将上下文注入系统提示（在 `hybrid` 或 `context` 回忆模式下）时，它会按以下顺序组装基础上下文块：

1. **会话摘要** —— 当前会话到目前为止的简短摘要（放在首位，以便模型立即获得对话连续性）
2. **用户表示** —— Honcho 积累的用户模型（偏好、事实、模式）
3. **AI 对等体卡片** —— 此 Hermes 配置文件的 AI 对等体身份卡

会话摘要由 Honcho 在每个回合开始时自动生成（当存在先前会话时）。它让模型无需重放完整历史即可获得热启动。

<a id="cold-warm-prompt-selection"></a>
### 冷 / 热提示选择
Honcho 会自动在两种提示策略之间选择：

| 条件 | 策略 | 行为 |
|-----------|----------|--------------|
| 没有之前的会话或空表征 | **冷启动** | 轻量级介绍提示；跳过摘要注入；鼓励模型了解用户 |
| 存在表征和/或会话历史 | **热启动** | 完整的基础上下文注入（摘要 → 表征 → 卡片）；更丰富的系统提示 |

您无需配置——它基于会话状态自动进行。

<a id="peers"></a>
### 对等方（Peers）

Honcho 将对等方之间的交互建模为**对等体**之间的交互。Hermes 为每个会话创建两个对等体：

- **用户对等体**（`peerName`）：代表人类。Honcho 根据观察到的消息构建用户表征。
- **AI 对等体**（`aiPeer`）：代表此 Hermes 实例。每个配置文件都有自己独立的 AI 对等体，从而使 Agents 形成独立的视角。

<a id="observation"></a>
### 观察（Observation）

每个对等体有两个观察开关，用于控制 Honcho 从什么中学习：

| 开关 | 作用 |
|--------|-------------|
| `observeMe` | 观察对等体自身的消息（构建自我表征） |
| `observeOthers` | 观察其他对等体的消息（构建跨对等体理解） |

默认：四个开关全部**开启**（全双向观察）。

在 `honcho.json` 中按对等体配置：

```json
{
  "observation": {
    "user": { "observeMe": true, "observeOthers": true },
    "ai":   { "observeMe": true, "observeOthers": true }
  }
}
```

或使用简写预设：

| 预设 | 用户 | AI | 使用场景 |
|--------|------|----|----------|
| `"directional"`（默认） | me:on, others:on | me:on, others:on | 多 Agent，完整记忆 |
| `"unified"` | me:on, others:off | me:off, others:on | 单 Agent，仅对用户建模 |

在 [Honcho 仪表盘](https://app.honcho.dev) 中更改的设置会在会话初始化时同步回来——服务端配置覆盖本地默认值。

<a id="sessions"></a>
### 会话（Sessions）

Honcho 会话限定了消息和观察的放置范围。策略选项：

| 策略 | 行为 |
|----------|----------|
| `per-directory`（默认） | 每个工作目录一个会话 |
| `per-repo` | 每个 git 仓库根目录一个会话 |
| `per-session` | 每次 Hermes 运行创建一个新 Honcho 会话 |
| `global` | 所有目录共享一个会话 |

手动覆盖：`hermes honcho map my-project-name`

<a id="recall-modes"></a>
### 回忆模式（Recall Modes）

Agent 访问 Honcho 记忆的方式：

| 模式 | 自动注入上下文？ | 工具可用？ | 使用场景 |
|------|---------------------|-----------------|----------|
| `hybrid`（默认） | 是 | 是 | Agent 决定何时使用工具 vs 自动上下文 |
| `context` | 是 | 否（隐藏） | 最小化 token 消耗，无工具调用 |
| `tools` | 否 | 是 | Agent 明确控制所有记忆访问 |

<a id="three-orthogonal-knobs"></a>
## 三个正交旋钮

Honcho 的辩证法行为由三个独立的维度控制。每个维度可以独立调节，不影响其他维度：

<a id="cadence-when"></a>
### 节奏（Cadence）（何时）

控制**多频繁**进行辩证法和上下文调用。

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextCadence` | `1` | 上下文 API 调用之间的最小轮次 |
| `dialecticCadence` | `2` | 辩证法 API 调用之间的最小轮次。建议 1–5 |
| `injectionFrequency` | `every-turn` | 基础上下文注入的频率：`every-turn` 或 `first-turn` |
较高的 cadence 值会减少辩证 LLM 的触发频率。`dialecticCadence: 2` 表示引擎每隔一轮触发一次。设为 `1` 则每轮都触发。

<a id="depth-how-many"></a>
### Depth（轮数）

控制 Honcho 每次查询执行**多少轮**辩证推理。

| 键名 | 默认值 | 范围 | 描述 |
|------|--------|------|------|
| `dialecticDepth` | `1` | 1-3 | 每次查询的辩证推理轮数 |
| `dialecticDepthLevels` | -- | 数组 | 可选的每轮深度级别覆盖（见下文） |

`dialecticDepth: 2` 表示 Honcho 运行两轮辩证综合。第一轮产生初步答案；第二轮进行优化。

`dialecticDepthLevels` 允许你独立设置每轮的推理级别：

```json
{
  "dialecticDepth": 3,
  "dialecticDepthLevels": ["low", "medium", "high"]
}
```

如果省略 `dialecticDepthLevels`，轮次将使用基于 `dialecticReasoningLevel`（基础级别）推导的**比例级别**：

| Depth（深度） | Pass levels（传递级别） |
|-------|-------------|
| 1 | [base] |
| 2 | [minimal, base] |
| 3 | [minimal, base, low] |

这样可以在早期轮次保持低成本，同时在最终综合时使用完整深度。

**会话开始时的深度。** 会话开始前的预热会在第1轮之前，在后台运行完整的 `dialecticDepth`。在冷对等节点上，单次预热往往返回浅薄输出——多轮深度会在用户发言前执行审计/协调循环。第1轮直接消耗预热结果；如果预热未及时完成，第1轮将回退到带有限时超时的同步调用。

<a id="level-how-hard"></a>
### Level（强度）

控制每轮辩证推理的**强度**。

| 键名 | 默认值 | 描述 |
|------|---------|-------------|
| `dialecticReasoningLevel` | `low` | `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | 当为 `true` 时，模型可以传递 `reasoning_level` 给 `honcho_reasoning`，以覆盖默认的每次调用设置。`false` = 始终使用 `dialecticReasoningLevel`，忽略模型覆盖 |

更高的级别产生更丰富的综合，但在 Honcho 后端消耗更多 token。

<a id="multi-profile-setup"></a>
## 多 Profile 设置

每个 Hermes profile 都有自己的 Honcho AI 对等节点，同时共享同一个 workspace（用户上下文）。这意味着：

- 所有 profile 看到相同的用户表示
- 每个 profile 构建自己的 AI 身份和观察
- 一个 profile 写入的结论通过共享 workspace 对其他 profile 可见

<a id="create-a-profile-with-honcho-peer"></a>
### 创建带 Honcho 对等节点的 profile

```bash
hermes profile create coder --clone
# 创建 host 块 hermes.coder，AI 对等节点 "coder"，继承自默认配置
```

`--clone` 对 Honcho 的作用：
1. 在 `honcho.json` 中创建 `hermes.coder` host 块
2. 设置 `aiPeer: "coder"`（profile 名称）
3. 从默认配置继承 `workspace`、`peerName`、`writeFrequency`、`recallMode` 等
4. 立即在 Honcho 中创建对等节点，使其在第一条消息之前就已存在

<a id="backfill-existing-profiles"></a>
### 回填现有 profile

```bash
hermes honcho sync    # 为所有尚未拥有 host 块的 profile 创建 host 块
```
<a id="per-profile-config"></a>
### 按用户维度配置

覆盖 host 块中的任意设置项：

```json
{
  "hosts": {
    "hermes.coder": {
      "aiPeer": "coder",
      "recallMode": "tools",
      "dialecticDepth": 2,
      "observation": {
        "user": { "observeMe": true, "observeOthers": false },
        "ai": { "observeMe": true, "observeOthers": true }
      }
    }
  }
}
```

<a id="tools"></a>
## 工具

Agent 拥有 5 个双向 Honcho 工具（在 `context` 回忆模式下隐藏）：

| 工具 | 调用LLM？ | 成本 | 使用场景 |
|------|-----------|------|----------|
| `honcho_profile` | 否 | 最低 | 对话开始时快速获取事实快照，或快速查找名称/角色/偏好 |
| `honcho_search` | 否 | 低 | 拉取具体历史事实供自行推理——原始摘要，无综合结果 |
| `honcho_context` | 否 | 低 | 全会话上下文快照：摘要、表示、卡片、最近消息 |
| `honcho_reasoning` | 是 | 中到高 | 由 Honcho 的辩证法引擎综合生成的自然语言问题 |
| `honcho_conclude` | 否 | 最低 | 写入或删除持久结论；传入 `peer: "ai"` 用于 AI 自我认知 |

<a id="honchoprofile"></a>
### `honcho_profile`
读取或更新参与者卡片——精选的关键事实（姓名、角色、偏好、沟通风格）。传入 `card: [...]` 进行更新；省略则为读取。无需调用LLM。

<a id="honchosearch"></a>
### `honcho_search`
对指定参与者的已存储上下文进行语义搜索。返回按相关性排序的原始摘要，不进行综合。默认 800 令牌，最大 2000。当你需要具体历史事实来自行推理，而非得到综合答案时使用。

<a id="honchocontext"></a>
### `honcho_context`
来自 Honcho 的全会话上下文快照——会话摘要、参与者表示、参与者卡片以及最近消息。无需调用LLM。当你希望一次性查看 Honcho 对当前会话和参与者所知道的所有信息时使用。

<a id="honchoreasoning"></a>
### `honcho_reasoning`
由 Honcho 的辩证法推理引擎（Honcho 后端调用 LLM）回答的自然语言问题。成本更高，质量更高。传入 `reasoning_level` 控制深度：`minimal`（快/便宜）→ `low` → `medium` → `high` → `max`（彻底）。省略则使用配置的默认值（`low`）。用于综合理解用户的模式、目标或当前状态。

<a id="honchoconclude"></a>
### `honcho_conclude`
写入或删除关于某参与者的持久结论。传入 `conclusion: "..."` 来创建。传入 `delete_id: "..."` 来删除结论（用于移除个人身份信息— Honcho 会随时间自动修正错误的结论，因此仅在需要移除个人身份信息时才需手动删除）。你必须且只能传入两参数中的一个。

<a id="bidirectional-peer-targeting"></a>
### 双向参与者定位

所有 5 个工具都接受可选的 `peer` 参数：
- `peer: "user"`（默认）— 作用于用户参与者
- `peer: "ai"` — 作用于当前配置文件的 AI 参与者
- `peer: "&lt;explicit-id&gt;"` — 工作空间中的任意参与者 ID

示例：
```
honcho_profile                        # 读取用户的卡片
honcho_profile peer="ai"              # 读取 AI 参与者卡片
honcho_reasoning query="这个用户最关心什么？"
honcho_reasoning query="我的交互模式是什么？" peer="ai" reasoning_level="medium"
honcho_conclude conclusion="偏好简短回答"
honcho_conclude conclusion="我倾向于过度解释代码" peer="ai"
honcho_conclude delete_id="abc123"    # 移除个人身份信息
```
<a id="agent-usage-patterns"></a>
## Agent 使用模式

Hermes 在 Honcho 记忆激活时的使用指南。

<a id="on-conversation-start"></a>
### 对话开始时

```
1. honcho_profile                  → 快速预热，无 LLM 成本
2. 如果上下文看起来单薄 → honcho_context（完整快照，仍无 LLM）
3. 如果需要深度综合 → honcho_reasoning（LLM 调用，谨慎使用）
```

不要在每一轮都调用 `honcho_reasoning`。自动注入已经处理了持续的上下文刷新。仅当基础上下文无法提供你真正需要的综合洞察时，才使用推理工具。

<a id="when-the-user-shares-something-to-remember"></a>
### 当用户分享需要记住的信息时

```
honcho_conclude conclusion="<具体、可执行的事实>"
```

好结论示例："更喜欢代码示例而非文字解释"，"正在开发一个 Rust 异步项目，持续到 2026 年 4 月"
差结论示例："用户说了一些关于 Rust 的话"（太模糊），"用户看起来懂技术"（已经在表征中）

<a id="when-the-user-asks-about-past-context-you-need-to-recall-specifics"></a>
### 当用户询问过去的上下文 / 你需要回忆具体信息时

```
honcho_search query="<主题>"        → 快速，无 LLM，适用于具体事实
honcho_context                      → 包含摘要和消息的完整快照
honcho_reasoning query="<问题>"     → 综合答案，当搜索不够用时使用
```

<a id="when-to-use-peer-ai"></a>
### 何时使用 `peer: "ai"`

使用 AI peer 定位来构建和查询 Agent 自身的自我认知：
- `honcho_conclude conclusion="I tend to be verbose when explaining architecture" peer="ai"` — 自我纠正
- `honcho_reasoning query="How do I typically handle ambiguous requests?" peer="ai"` — 自我审查
- `honcho_profile peer="ai"` — 查看自己的身份卡片

<a id="when-not-to-call-tools"></a>
### 何时不调用工具

在 `hybrid` 和 `context` 模式下，基础上下文（用户表征 + 卡片 + 会话摘要）会在每一轮前自动注入。不要重新获取已经注入的内容。仅在以下情况调用工具：
- 你需要注入的上下文没有包含的内容
- 用户明确要求你回忆或检查记忆
- 你正在为某件新事物写下结论

<a id="cadence-awareness"></a>
### 节奏感知

工具侧的 `honcho_reasoning` 与自动注入的辩证成本相同。在显式工具调用后，自动注入的节奏会重置 —— 避免对同一轮重复计费。

<a id="config-reference"></a>
## 配置参考

配置文件：`$HERMES_HOME/honcho.json`（本地配置）或 `~/.honcho/config.json`（全局配置）。

<a id="key-settings"></a>
### 关键设置

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | API 密钥（[获取地址](https://app.honcho.dev)） |
| `baseUrl` | -- | 自托管 Honcho 的基础 URL |
| `peerName` | -- | 用户 Peer 身份 |
| `aiPeer` | 主机密钥 | AI Peer 身份 |
| `workspace` | 主机密钥 | 共享工作空间 ID |
| `recallMode` | `hybrid` | `hybrid`、`context` 或 `tools` |
| `observation` | 全部开启 | 每个 Peer 的 `observeMe`/`observeOthers` 布尔值 |
| `writeFrequency` | `async` | `async`、`turn`、`session` 或整数 N |
| `sessionStrategy` | `per-directory` | `per-directory`、`per-repo`、`per-session`、`global` |
| `messageMaxChars` | `25000` | 每条消息的最大字符数（超出则分块） |
<a id="dialectic-settings"></a>
### 辩证设置

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `dialecticReasoningLevel` | `low` | `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | 根据查询复杂度自动提升推理级别。`false` = 固定级别 |
| `dialecticDepth` | `1` | 每次查询的辩证轮数（1-3） |
| `dialecticDepthLevels` | -- | 可选数组，表示每轮级别，例如 `["low", "high"]` |
| `dialecticMaxInputChars` | `10000` | 辩证查询输入的最大字符数 |

<a id="context-budget-and-injection"></a>
### 上下文预算与注入

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextTokens` | 不设上限 | 合并后的基础上下文注入（摘要+表示+卡片）的最大 token 数。可选上限——省略则不设上限，设置为整数以限定注入大小。 |
| `injectionFrequency` | `every-turn` | `every-turn` 或 `first-turn` |
| `contextCadence` | `1` | 上下文 API 调用之间的最少轮数间隔 |
| `dialecticCadence` | `2` | 辩证 LLM 调用之间的最少轮数间隔（推荐 1–5） |

`contextTokens` 预算在注入时强制执行。如果会话摘要 + 表示 + 卡片超出预算，Honcho 会先修剪摘要，然后是表示，保留卡片。这可以防止长时间会话中的上下文膨胀。

<a id="memory-context-sanitization"></a>
### 内存上下文清理

Honcho 在注入前会对 `memory-context` 块进行清理，以防止提示注入和格式错误的内容：

- 去除用户编写的结论中的 XML/HTML 标签
- 规范化空白字符和控制字符
- 截断超过 `messageMaxChars` 的单个结论
- 转义可能破坏系统提示结构的分隔符序列

此修复解决了原始用户结论中包含标记或特殊字符可能破坏注入上下文块的边界情况。

<a id="troubleshooting"></a>
## 故障排查

<a id="honcho-not-configured"></a>
### "Honcho not configured"
运行 `hermes honcho setup`。确保 `~/.hermes/config.yaml` 中有 `memory.provider: honcho`。

<a id="memory-not-persisting-across-sessions"></a>
### 跨会话内存不持久
检查 `hermes honcho status` —— 确认 `saveMessages: true` 并且 `writeFrequency` 不是 `session`（session 仅在退出时写入）。

<a id="profile-not-getting-its-own-peer"></a>
### 配置文件没有自己的对等体
创建时使用 `--clone`：`hermes profile create &lt;name&gt; --clone`。对于已有配置文件：`hermes honcho sync`。

<a id="observation-changes-in-dashboard-not-reflected"></a>
### 仪表板中的观察更改未生效
每次会话初始化时，观察配置都会从服务器同步。在 Honcho UI 中更改设置后，请启动新会话。

<a id="messages-truncated"></a>
### 消息被截断
超过 `messageMaxChars`（默认 25k）的消息会自动分块并添加 `[continued]` 标记。如果频繁遇到此问题，请检查工具结果或技能内容是否导致消息膨胀。

<a id="context-injection-too-large"></a>
### 上下文注入过大
如果看到关于超出上下文预算的警告，降低 `contextTokens` 或减少 `dialecticDepth`。预算紧张时会先修剪会话摘要。

<a id="session-summary-missing"></a>
### 会话摘要缺失
会话摘要要求当前 Honcho 会话中至少有一轮先前的对话。在冷启动（新会话，无历史记录）时，摘要会被省略，Honcho 会使用冷启动提示策略。
<a id="cli-commands"></a>
## CLI 命令

| 命令 | 描述 |
|---------|-------------|
| `hermes honcho setup` | 交互式设置向导（云端/本地、身份、观察、回忆、会话） |
| `hermes honcho status` | 显示已解析的配置、连接测试、活动配置文件的同伴信息 |
| `hermes honcho enable` | 为活动配置文件启用 Honcho（必要时创建主机块） |
| `hermes honcho disable` | 禁用活动配置文件的 Honcho |
| `hermes honcho peer` | 显示或更新同伴名称（`--user &lt;name&gt;`、`--ai &lt;name&gt;`、`--reasoning &lt;level&gt;`） |
| `hermes honcho peers` | 显示所有配置文件的同伴身份 |
| `hermes honcho mode` | 显示或设置召回模式（`hybrid`、`context`、`tools`） |
| `hermes honcho tokens` | 显示或设置 Token 预算（`--context &lt;N&gt;`、`--dialectic &lt;N&gt;`） |
| `hermes honcho sessions` | 列出已知的目录到会话名称映射 |
| `hermes honcho map &lt;name&gt;` | 将当前工作目录映射到 Honcho 会话名称 |
| `hermes honcho identity` | 种下 AI 同伴身份或显示两个同伴表示 |
| `hermes honcho sync` | 为所有尚未拥有主机块的 Hermes 配置文件创建主机块 |
| `hermes honcho migrate` | 从 OpenClaw 原生内存到 Hermes + Honcho 的分步迁移指南 |
| `hermes memory setup` | 通用内存提供程序选择器（选择 "honcho" 运行相同的向导） |
| `hermes memory status` | 显示活动的内存提供程序和配置 |
| `hermes memory off` | 禁用外部内存提供程序 |
