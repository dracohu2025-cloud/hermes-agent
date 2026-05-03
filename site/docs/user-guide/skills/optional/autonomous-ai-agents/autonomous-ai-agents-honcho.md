---
title: "Honcho"
sidebar_label: "Honcho"
description: "与 Hermes 一起配置和使用 Honcho 记忆——跨会话用户建模、多配置文件对等隔离、观察配置、辩证推理、会话摘要..."
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Honcho {#honcho}

与 Hermes 一起配置和使用 Honcho 记忆——跨会话用户建模、多配置文件对等隔离、观察配置、辩证推理、会话摘要以及上下文预算强制。在设置 Honcho、排查记忆问题、使用 Honcho 对等体管理配置文件、或者调整观察、回忆和辩证设置时使用。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 源 | 可选 — 使用 `hermes skills install official/autonomous-ai-agents/honcho` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents/honcho` |
| 版本 | `2.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `Honcho`、`Memory`、`Profiles`、`Observation`、`Dialectic`、`User-Modeling`、`Session-Summary` |
| 相关技能 | [`hermes-agent`](/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是当此技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Hermes 的 Honcho 记忆 {#honcho-memory-for-hermes}

Honcho 提供 AI 原生跨会话用户建模。它跨对话学习用户身份，并为每个 Hermes 配置文件赋予自己的对等体身份，同时共享统一的用户视图。

## 何时使用 {#when-to-use}

- 设置 Honcho（云端或自托管）
- 排查记忆无法工作 / 对等体未同步的问题
- 创建多配置文件设置，每个 Agent 拥有自己的 Honcho 对等体
- 调整观察、回忆、辩证深度或写入频率设置
- 理解 5 个 Honcho 工具的功能及何时使用
- 配置上下文预算和会话摘要注入

## 设置 {#setup}

### 云端 (app.honcho.dev) {#cloud-app-honcho-dev}

```bash
hermes honcho setup
# 选择 "cloud"，粘贴来自 https://app.honcho.dev 的 API 密钥
```

### 自托管 {#self-hosted}

```bash
hermes honcho setup
# 选择 "local"，输入基础 URL（例如 http://localhost:8000）
```

参见：https://docs.honcho.dev/v3/guides/integrations/hermes#running-honcho-locally-with-hermes

### 验证 {#verify}

```bash
hermes honcho status    # 显示已解析的配置、连接测试、对等体信息
```

## 架构 {#architecture}

### 基础上下文注入 {#base-context-injection}

当 Honcho 将上下文注入系统提示（在 `hybrid` 或 `context` 回忆模式下）时，它会按以下顺序组装基础上下文块：

1. **会话摘要** —— 到目前为止当前会话的简要摘要（放在最前面，以便模型立即获得对话连续性）
2. **用户表示** —— Honcho 积累的用户模型（偏好、事实、模式）
3. **AI 对等体卡片** —— 此 Hermes 配置文件的 AI 对等体身份卡片

会话摘要由 Honcho 在每一轮开始时自动生成（如果存在之前的会话）。它让模型能够以“热启动”方式开始，而无需重放完整历史。

### 冷 / 热提示选择 {#cold-warm-prompt-selection}

Honcho 自动在两种提示策略之间选择：
| 条件 | 策略 | 行为 |
|-----------|----------|--------------|
| 无先前会话或空表示 | **冷启动** | 轻量级开场提示；跳过摘要注入；鼓励模型了解用户 |
| 存在表示和/或会话历史 | **热启动** | 完整的基础上下文注入（摘要 → 表示 → 卡片）；更丰富的系统提示 |

您无需配置此功能——它会根据会话状态自动执行。

### 对等体 {#peers}

Honcho 将对话建模为**对等体**之间的交互。Hermes 在每个会话中创建两个对等体：

- **用户对等体**（`peerName`）：代表人类。Honcho 根据观察到的消息构建用户表示。
- **AI 对等体**（`aiPeer`）：代表此 Hermes 实例。每个配置文件都有自己的 AI 对等体，因此 Agent 可以形成独立的视角。

### 观察 {#observation}

每个对等体有两个观察开关，用于控制 Honcho 从哪些信息中学习：

| 开关 | 作用 |
|--------|-------------|
| `observeMe` | 观察对等体自身的消息（构建自我表示） |
| `observeOthers` | 观察其他对等体的消息（构建跨对等体理解） |

默认：所有四个开关**开启**（完全双向观察）。

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
| `"directional"`（默认） | 我:开, 其他:开 | 我:开, 其他:开 | 多 Agent，完整记忆 |
| `"unified"` | 我:开, 其他:关 | 我:关, 其他:开 | 单 Agent，仅用户建模 |

在 [Honcho 仪表盘](https://app.honcho.dev) 中更改的设置会在会话初始化时同步回来——服务端配置优先于本地默认值。

### 会话 {#sessions}

Honcho 会话限定了消息和观察结果的存放范围。策略选项：

| 策略 | 行为 |
|----------|----------|
| `per-directory`（默认） | 每个工作目录一个会话 |
| `per-repo` | 每个 git 仓库根目录一个会话 |
| `per-session` | 每次 Hermes 运行创建一个新 Honcho 会话 |
| `global` | 所有目录共享一个会话 |

手动覆盖：`hermes honcho map my-project-name`

### 召回模式 {#recall-modes}

Agent 访问 Honcho 记忆的方式：

| 模式 | 自动注入上下文？ | 工具可用？ | 使用场景 |
|------|---------------------|-----------------|----------|
| `hybrid`（默认） | 是 | 是 | Agent 决定何时使用工具或自动上下文 |
| `context` | 是 | 否（隐藏） | 最小 token 成本，无工具调用 |
| `tools` | 否 | 是 | Agent 完全显式控制所有记忆访问 |

## 三个正交旋钮 {#three-orthogonal-knobs}

Honcho 的辩证行为由三个独立维度控制。每个维度都可以独立调节，互不影响：

### 节奏（何时） {#cadence-when}

控制**多久**执行一次辩证和上下文调用。

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextCadence` | `1` | 上下文 API 调用之间的最小轮次间隔 |
| `dialecticCadence` | `2` | 辩证 API 调用之间的最小轮次间隔。建议值 1–5 |
| `injectionFrequency` | `every-turn` | 基础上下文注入的频率：`every-turn`（每轮）或 `first-turn`（首轮） |
较高的 cadence 值会降低辩证 LLM 的触发频率。`dialecticCadence: 2` 表示引擎每隔一轮触发一次。设置为 `1` 则每轮都触发。

### 深度（轮数） {#depth-how-many}

控制 Honcho 每次查询执行**多少轮**辩证推理。

| 键 | 默认值 | 范围 | 描述 |
|-----|---------|-------|-------------|
| `dialecticDepth` | `1` | 1-3 | 每次查询的辩证推理轮数 |
| `dialecticDepthLevels` | -- | 数组 | 可选的每轮深度级别覆盖（见下文） |

`dialecticDepth: 2` 表示 Honcho 运行两轮辩证综合。第一轮产生初始答案；第二轮对其进行优化。

`dialecticDepthLevels` 允许你独立设置每轮的推理级别：

```json
{
  "dialecticDepth": 3,
  "dialecticDepthLevels": ["low", "medium", "high"]
}
```

如果省略了 `dialecticDepthLevels`，各轮将使用从 `dialecticReasoningLevel`（基础级别）派生的**比例级别**：

| 深度 | 传递级别 |
|-------|-------------|
| 1 | [基础] |
| 2 | [最小, 基础] |
| 3 | [最小, 基础, 低] |

这样可以在早期传递中保持低成本，同时在最终综合时使用完整深度。

**会话开始时的深度。** 会话开始的预热会在第 1 轮之前，在后台运行完整配置的 `dialecticDepth`。在冷启动对等体上执行单次预热通常返回单薄的结果——多轮深度会在用户发言之前运行审计/协调循环。第 1 轮直接使用预热结果；如果预热未能及时完成，第 1 轮将回退到具有有限超时的同步调用。

### 级别（强度） {#level-how-hard}

控制每轮辩证推理的**强度**。

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `dialecticReasoningLevel` | `low` | `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | 当为 `true` 时，模型可以将 `reasoning_level` 传递给 `honcho_reasoning` 以覆盖每次调用的默认值。`false` = 始终使用 `dialecticReasoningLevel`，模型覆盖被忽略 |

更高的级别会产生更丰富的综合结果，但在 Honcho 后端会消耗更多 token。

## 多配置文件设置 {#multi-profile-setup}

每个 Hermes 配置文件在共享同一个工作空间（用户上下文）的同时，拥有自己独立的 Honcho AI 对等体。这意味着：

- 所有配置文件看到相同的用户表示
- 每个配置文件构建自己的 AI 身份和观察结果
- 一个配置文件写入的结论可以通过共享工作空间被其他配置文件看到

### 创建带有 Honcho 对等体的配置文件 {#create-a-profile-with-honcho-peer}

```bash
hermes profile create coder --clone
# 创建 host 块 hermes.coder，AI 对等体 "coder"，从 default 继承配置
```

`--clone` 对 Honcho 的作用：
1. 在 `honcho.json` 中创建一个 `hermes.coder` host 块
2. 设置 `aiPeer: "coder"`（配置文件名称）
3. 从 default 继承 `workspace`、`peerName`、`writeFrequency`、`recallMode` 等
4. 在 Honcho 中主动创建对等体，使其在第一条消息之前就已存在

### 回填现有配置文件 {#backfill-existing-profiles}

```bash
hermes honcho sync    # 为所有尚未拥有 host 块的配置文件创建 host 块
```
### 按用户配置 {#per-profile-config}

覆盖主机块中的任何设置：

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

## 工具 {#tools}

Agent 有 5 个双向 Honcho 工具（在 `context` 召回模式下隐藏）：

| 工具 | 是否调用 LLM？ | 成本 | 使用场景 |
|------|-----------|------|----------|
| `honcho_profile` | 否 | 极低 | 对话开始时快速获取事实快照，或快速查找名称/角色/偏好 |
| `honcho_search` | 否 | 低 | 获取特定的历史事实供自己推理——原始摘录，无综合 |
| `honcho_context` | 否 | 低 | 完整会话上下文快照：摘要、表示、卡片、最近消息 |
| `honcho_reasoning` | 是 | 中–高 | 由 Honcho 的辩证引擎综合生成的自然语言问题 |
| `honcho_conclude` | 否 | 极低 | 写入或删除持久化结论；传递 `peer: "ai"` 用于 AI 自我认知 |

### `honcho_profile` {#honchoprofile}
读取或更新同伴卡片——精选的关键事实（名称、角色、偏好、沟通风格）。传递 `card: [...]` 进行更新；省略则读取。不调用 LLM。

### `honcho_search` {#honchosearch}
对特定同伴的存储上下文进行语义搜索。返回按相关性排序的原始摘录，无综合。默认 800 个 token，最大 2000。当你需要特定的历史事实自己推理，而不是综合答案时使用。

### `honcho_context` {#honchocontext}
来自 Honcho 的完整会话上下文快照——会话摘要、同伴表示、同伴卡片和最近消息。不调用 LLM。当你希望一次性查看 Honcho 对当前会话和同伴的所有了解时使用。

### `honcho_reasoning` {#honchoreasoning}
由 Honcho 的辩证推理引擎回答的自然语言问题（在 Honcho 后端调用 LLM）。成本更高，质量更高。传递 `reasoning_level` 控制深度：`minimal`（快速/便宜）→ `low` → `medium` → `high` → `max`（全面）。省略则使用配置的默认值（`low`）。用于综合理解用户的模式、目标或当前状态。

### `honcho_conclude` {#honchoconclude}
写入或删除关于同伴的持久化结论。传递 `conclusion: "..."` 创建。传递 `delete_id: "..."` 删除结论（用于 PII 删除——Honcho 会随时间自我修正错误的结论，因此仅 PII 需要删除）。你必须且只能传递这两个参数中的一个。

### 双向同伴定位 {#bidirectional-peer-targeting}

所有 5 个工具都接受可选的 `peer` 参数：
- `peer: "user"`（默认）——对用户同伴操作
- `peer: "ai"`——对此配置文件的 AI 同伴操作
- `peer: "&lt;explicit-id&gt;"`——工作区中的任何同伴 ID

示例：
```
honcho_profile                        # 读取用户卡片
honcho_profile peer="ai"              # 读取 AI 同伴卡片
honcho_reasoning query="这个用户最关心什么？"
honcho_reasoning query="我的交互模式是什么？" peer="ai" reasoning_level="medium"
honcho_conclude conclusion="偏好简洁的回答"
honcho_conclude conclusion="我倾向于过度解释代码" peer="ai"
honcho_conclude delete_id="abc123"    # PII 删除
```
## Agent 使用模式 {#agent-usage-patterns}

当 Honcho 记忆激活时，Hermes 应遵循的指南。

### 会话开始时 {#on-conversation-start}

```
1. honcho_profile                  → 快速预热，无 LLM 开销
2. 若上下文看似单薄 → honcho_context  （全量快照，仍无 LLM 开销）
3. 若需深度综合 → honcho_reasoning  （调用 LLM，谨慎使用）
```

不要在每次轮次都调用 `honcho_reasoning`。自动注入已经处理了持续的上下文刷新。仅当基础上下文无法提供时，你才需要调用推理工具来获取综合洞察。

### 当用户分享需要记住的信息时 {#when-the-user-shares-something-to-remember}

```
honcho_conclude conclusion="<具体、可操作的事实>"
```

好的结论："偏好代码示例而非文字解释"，"正在开发一个 Rust 异步项目，预计持续到 2026 年 4 月"
不好的结论："用户说了些关于 Rust 的事情"（过于模糊），"用户看起来懂技术"（已存在于表征中）

### 当用户询问过去的上下文 / 你需要回忆具体信息时 {#when-the-user-asks-about-past-context-you-need-to-recall-specifics}

```
honcho_search query="<主题>"       → 快速，无 LLM，适合具体事实
honcho_context                       → 包含摘要+消息的全量快照
honcho_reasoning query="<问题>"  → 综合回答，当搜索不足以解决问题时使用
```

### 何时使用 `peer: "ai"` {#when-to-use-peer-ai}

使用 AI 对等目标来构建和查询 Agent 自身的自我认知：
- `honcho_conclude conclusion="我在解释架构时往往过于冗长" peer="ai"` — 自我修正
- `honcho_reasoning query="我通常如何处理模糊请求？" peer="ai"` — 自我审计
- `honcho_profile peer="ai"` — 审查自己的身份卡片

### 何时不应调用工具 {#when-not-to-call-tools}

在 `hybrid` 和 `context` 模式下，基础上下文（用户表征 + 卡片 + 会话摘要）会在每次轮次之前自动注入。不要重新获取已经注入的内容。仅在以下情况调用工具：
- 你需要注入的上下文中没有提供的内容
- 用户明确要求你回忆或检查记忆
- 你正在编写关于新内容的结论

### 节奏意识 {#cadence-awareness}

工具侧调用 `honcho_reasoning` 与自动注入的辩证操作具有相同的开销。在显式调用工具后，自动注入的节奏会重置——避免了同一轮次重复计费。

## 配置参考 {#config-reference}

配置文件：`$HERMES_HOME/honcho.json`（配置文件本地）或 `~/.honcho/config.json`（全局）。

### 关键设置 {#key-settings}

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | API 密钥（[获取一个](https://app.honcho.dev)） |
| `baseUrl` | -- | 自托管 Honcho 的基础 URL |
| `peerName` | -- | 用户对等身份 |
| `aiPeer` | 主机键 | AI 对等身份 |
| `workspace` | 主机键 | 共享工作区 ID |
| `recallMode` | `hybrid` | `hybrid`、`context` 或 `tools` |
| `observation` | 全部开启 | 每个对等体的 `observeMe`/`observeOthers` 布尔值 |
| `writeFrequency` | `async` | `async`、`turn`、`session` 或整数 N |
| `sessionStrategy` | `per-directory` | `per-directory`、`per-repo`、`per-session`、`global` |
| `messageMaxChars` | `25000` | 每条消息的最大字符数（超出则分块） |
### 辩证设置 {#dialectic-settings}

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `dialecticReasoningLevel` | `low` | `minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 根据查询复杂度自动提升推理级别。`false` = 固定级别 |
| `dialecticDepth` | `1` | 每次查询的辩证轮数（1-3） |
| `dialecticDepthLevels` | -- | 可选数组，指定每轮的级别，例如 `["low", "high"]` |
| `dialecticMaxInputChars` | `10000` | 辩证查询输入的最大字符数 |

### 上下文预算与注入 {#context-budget-and-injection}

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextTokens` | 无上限 | 组合基础上下文注入（摘要 + 表示 + 卡片）的最大 token 数。可选上限——省略则无上限，设置为整数可限制注入大小。 |
| `injectionFrequency` | `every-turn` | `every-turn` 或 `first-turn` |
| `contextCadence` | `1` | 上下文 API 调用之间的最小轮数 |
| `dialecticCadence` | `2` | 辩证 LLM 调用之间的最小轮数（建议 1–5） |

`contextTokens` 预算在注入时强制执行。如果会话摘要 + 表示 + 卡片超出预算，Honcho 会先裁剪摘要，然后是表示，保留卡片。这可以防止长时间会话中上下文膨胀。

### 内存上下文清理 {#memory-context-sanitization}

Honcho 在注入前会对 `memory-context` 块进行清理，以防止提示注入和格式错误的内容：

- 去除用户编写的结论中的 XML/HTML 标签
- 规范化空白字符和控制字符
- 截断超过 `messageMaxChars` 的单个结论
- 转义可能破坏系统提示结构的分隔符序列

此修复解决了原始用户结论中包含标记或特殊字符可能破坏注入上下文块的边缘情况。

## 故障排除 {#troubleshooting}

### "Honcho not configured" {#honcho-not-configured}
运行 `hermes honcho setup`。确保 `~/.hermes/config.yaml` 中包含 `memory.provider: honcho`。

### 记忆在会话间不持久 {#memory-not-persisting-across-sessions}
检查 `hermes honcho status` —— 确认 `saveMessages: true` 且 `writeFrequency` 不是 `session`（后者仅在退出时写入）。

### 配置文件没有自己的对等体 {#profile-not-getting-its-own-peer}
创建时使用 `--clone`：`hermes profile create &lt;name&gt; --clone`。对于现有配置文件：`hermes honcho sync`。

### 仪表盘中的观察更改未生效 {#observation-changes-in-dashboard-not-reflected}
观察配置在每次会话初始化时从服务器同步。在 Honcho UI 中更改设置后，启动新会话。

### 消息被截断 {#messages-truncated}
超过 `messageMaxChars`（默认 25k）的消息会自动分块，并添加 `[continued]` 标记。如果经常遇到此问题，请检查工具结果或技能内容是否导致消息大小膨胀。

### 上下文注入过大 {#context-injection-too-large}
如果看到上下文预算超出的警告，请降低 `contextTokens` 或减少 `dialecticDepth`。预算紧张时，会话摘要会首先被裁剪。

### 会话摘要缺失 {#session-summary-missing}
会话摘要要求当前 Honcho 会话中至少有一个先前的轮次。在冷启动（新会话，无历史记录）时，摘要会被省略，Honcho 会改用冷启动提示策略。
## CLI 命令 {#cli-commands}

| 命令 | 描述 |
|---------|-------------|
| `hermes honcho setup` | 交互式设置向导（云/本地、身份、观察、回忆、会话） |
| `hermes honcho status` | 显示已解析的配置、连接测试、当前配置文件的对等体信息 |
| `hermes honcho enable` | 为当前配置文件启用 Honcho（如有需要会创建 host 块） |
| `hermes honcho disable` | 为当前配置文件禁用 Honcho |
| `hermes honcho peer` | 显示或更新对等体名称（`--user &lt;name&gt;`、`--ai &lt;name&gt;`、`--reasoning &lt;level&gt;`） |
| `hermes honcho peers` | 显示所有配置文件中的对等体身份 |
| `hermes honcho mode` | 显示或设置回忆模式（`hybrid`、`context`、`tools`） |
| `hermes honcho tokens` | 显示或设置令牌预算（`--context &lt;N&gt;`、`--dialectic &lt;N&gt;`） |
| `hermes honcho sessions` | 列出已知的目录到会话名称的映射 |
| `hermes honcho map &lt;name&gt;` | 将当前工作目录映射到 Honcho 会话名称 |
| `hermes honcho identity` | 初始化 AI 对等体身份，或显示双方对等体表示 |
| `hermes honcho sync` | 为所有尚未拥有 host 块的 Hermes 配置文件创建 host 块 |
| `hermes honcho migrate` | 从 OpenClaw 原生内存迁移到 Hermes + Honcho 的分步指南 |
| `hermes memory setup` | 通用内存提供者选择器（选择 "honcho" 会运行相同的向导） |
| `hermes memory status` | 显示当前内存提供者及其配置 |
| `hermes memory off` | 禁用外部内存提供者 |
