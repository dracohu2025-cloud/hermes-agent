---
sidebar_position: 99
title: "Honcho 记忆"
description: "通过 Honcho 实现 AI 原生持久记忆——辩证推理、多 Agent 用户建模与深度个性化"
---

<a id="honcho-memory"></a>
# Honcho 记忆

[Honcho](https://github.com/plastic-labs/honcho) 是一个 AI 原生记忆后端，它在 Hermes 内置记忆系统之上增加了辩证推理和深度用户建模。与简单的键值存储不同，Honcho 在对话发生后通过对对话进行推理，维护了一个关于用户是谁的动态模型——包括他们的偏好、沟通风格、目标和模式。

:::info Honcho 是记忆提供者插件
Honcho 已集成到[记忆提供者](./memory-providers.md)系统中。以下所有功能均可通过统一的记忆提供者接口使用。
:::

<a id="honcho-is-a-memory-provider-plugin"></a>
<a id="what-honcho-adds"></a>
## Honcho 新增的能力

| 能力 | 内置记忆 | Honcho |
|-----------|----------------|--------|
| 跨会话持久化 | ✔ 基于文件的 MEMORY.md/USER.md | ✔ 服务端 + API |
| 用户画像 | ✔ 手动 Agent 管理 | ✔ 自动辩证推理 |
| 会话摘要 | — | ✔ 会话级上下文注入 |
| 多 Agent 隔离 | — | ✔ 按对话方隔离画像 |
| 观测模式 | — | ✔ 统一或定向观测 |
| 结论（派生洞察） | — | ✔ 服务端模式推理 |
| 跨历史搜索 | ✔ FTS5 会话搜索 | ✔ 结论语义搜索 |

**辩证推理**：在每轮对话之后（由 `dialecticCadence` 控制），Honcho 分析对话内容并推导出关于用户偏好、习惯和目标的洞察。这些洞察随时间累积，使 Agent 能够获得超出用户明确陈述的深层理解。辩证支持多轮深度（1–3 轮），并自动选择冷/热提示——冷启动查询聚焦于用户的一般事实，而热查询则优先使用会话级别的上下文。

**会话级上下文**：基础上下文现在包含会话摘要以及用户表征和对话方卡片。这使得 Agent 能够了解当前会话中已经讨论过的内容，减少重复并实现连贯性。

**多 Agent 画像**：当多个 Hermes 实例与同一用户对话时（例如一个编码助手和一个个人助手），Honcho 会维护独立的“对话方”画像。每个对话方只能看到自己的观测和结论，从而防止上下文交叉污染。

<a id="setup"></a>
## 设置

```bash
hermes memory setup    # 从提供者列表中选择 "honcho"
```

或手动配置：

```yaml
# ~/.hermes/config.yaml
memory:
  provider: honcho
```

```bash
echo 'HONCHO_API_KEY=***' >> ~/.hermes/.env
```

在 [honcho.dev](https://honcho.dev) 获取 API 密钥。

<a id="architecture"></a>
## 架构

<a id="two-layer-context-injection"></a>
### 两层上下文注入

在每轮对话（`hybrid` 或 `context` 模式）中，Honcho 将两层上下文注入系统提示：

1. **基础上下文**——会话摘要、用户表征、用户对话方卡片、AI 自表征和 AI 身份卡片。由 `contextCadence` 刷新。这是“用户是谁”层。
2. **辩证补充**——LLM 合成的关于用户当前状态和需求的推理。由 `dialecticCadence` 刷新。这是“当前什么重要”层。
两个层会合并并截断到 `contextTokens` 预算内（如果设置了的话）。

<a id="cold-warm-prompt-selection"></a>
### 冷/热提示选择

dialectic 会自动在两种提示策略之间选择：

- **冷启动**（尚无基本上下文）：通用查询 —— “此人是谁？其偏好、目标和工作风格是什么？”
- **热会话**（已有基本上下文）：会话范围查询 —— “基于本会话已讨论的内容，与此用户最相关的上下文是什么？”

这一步根据基本上下文是否已填充自动完成。

<a id="three-orthogonal-config-knobs"></a>
### 三个正交配置旋钮

成本和深度由三个独立的旋钮控制：

| 旋钮 | 控制项 | 默认值 |
|------|--------|--------|
| `contextCadence` | 调用 `context()` API 的回合间隔（基本层刷新） | `1` |
| `dialecticCadence` | 调用 `peer.chat()` LLM 的回合间隔（dialectic 层刷新） | `2`（推荐 1–5） |
| `dialecticDepth` | 每次 dialectic 调用中 `.chat()` 的轮数（1–3） | `1` |

这些旋钮是正交的 —— 你可以频繁刷新上下文但少用 dialectic，也可以低频使用深层多轮 dialectic。例如：`contextCadence: 1, dialecticCadence: 5, dialecticDepth: 2` 表示每回合刷新基本上下文，每 5 回合运行一次 dialectic，每次 dialectic 运行执行 2 轮。

<a id="dialectic-depth-multi-pass"></a>
### Dialectic 深度（多轮）

当 `dialecticDepth` > 1 时，每次 dialectic 调用会运行多轮 `.chat()`：

- **第 0 轮**：冷提示或热提示（见上文）
- **第 1 轮**：自我审计 —— 识别初始评估中的漏洞，并从最近会话中综合证据
- **第 2 轮**：调和 —— 检查之前轮次之间的矛盾，产生最终综合结果

每轮使用成比例的推理级别（早期轮次较轻，主轮次使用基础级别）。通过 `dialecticDepthLevels` 覆盖每轮的级别 —— 例如深度 3 的运行可用 `["minimal", "medium", "high"]`。

如果前一轮返回了强信号（长结构化输出），后续轮次会提前退出，因此深度 3 并不总是意味着 3 次 LLM 调用。

<a id="session-start-prewarm"></a>
### 会话启动预热

在会话初始化时，Honcho 会在后台以完全配置的 `dialecticDepth` 触发一次 dialectic 调用，并将结果直接交给第 1 轮的上下文组装。在冷 peer 上进行单轮预热通常返回单薄输出 —— 多轮深度会在用户说话之前就运行审计/调和周期。如果预热在第 1 轮之前尚未完成，第 1 轮会降级为带有限时超时的同步调用。

<a id="query-adaptive-reasoning-level"></a>
### 查询自适应推理级别

自动注入的 dialectic 会根据查询长度缩放 `dialecticReasoningLevel`：字符数 ≥120 时 +1 级别，≥400 时 +2，上限为 `reasoningLevelCap`（默认 `"high"`）。通过 `reasoningHeuristic: false` 禁用，让每次自动调用固定为 `dialecticReasoningLevel`。可用级别：`minimal`、`low`、`medium`、`high`、`max`。

<a id="configuration-options"></a>
## 配置选项

Honcho 在 `~/.honcho/config.json`（全局）或 `$HERMES_HOME/honcho.json`（配置文件本地）中配置。设置向导会帮你完成这一步。
<a id="full-config-reference"></a>
### 完整配置参考

| Key | 默认值 | 描述 |
|-----|---------|-------------|
| `contextTokens` | `null`（无上限） | 每轮自动注入上下文的 Token 预算。设为整数（如 1200）即可限制上限。会在单词边界截断 |
| `contextCadence` | `1` | `context()` API 调用（基础层刷新）之间的最小轮数 |
| `dialecticCadence` | `2` | `peer.chat()` LLM 调用（辩证层）之间的最小轮数。推荐值 1–5。在 `tools` 模式下不相关——模型显式调用 |
| `dialecticDepth` | `1` | 每次辩证调用的 `.chat()` 传递次数。限制在 1–3 之间 |
| `dialecticDepthLevels` | `null` | 可选数组，每次传递的推理级别，例如 `["minimal", "low", "medium"]`。会覆盖按比例分配的默认值 |
| `dialecticReasoningLevel` | `'low'` | 基础推理级别：`minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 当为 `true` 时，模型可以通过工具参数在每次调用中覆盖推理级别 |
| `dialecticMaxChars` | `600` | 注入到系统提示中的辩证结果最大字符数 |
| `recallMode` | `'hybrid'` | `hybrid`（自动注入 + 工具）、`context`（仅注入）、`tools`（仅工具） |
| `writeFrequency` | `'async'` | 何时刷新消息：`async`（后台线程）、`turn`（同步）、`session`（结束时批量写入）或整数 N |
| `saveMessages` | `true` | 是否将消息持久化到 Honcho API |
| `observationMode` | `'directional'` | `directional`（全部开启）或 `unified`（共享池）。可用 `observation` 对象进行精细控制 |
| `messageMaxChars` | `25000` | 通过 `add_messages()` 发送的每条消息的最大字符数。超出时会分块 |
| `dialecticMaxInputChars` | `10000` | 作为辩证查询输入到 `peer.chat()` 的最大字符数 |
| `sessionStrategy` | `'per-directory'` | `per-directory`、`per-repo`、`per-session` 或 `global` |

**会话策略**控制 Honcho 会话如何映射到你的工作：
- `per-session` — 每次运行 `hermes` 都会获得一个新的会话。从头开始，通过工具保持记忆。推荐新用户使用。
- `per-directory` — 每个工作目录对应一个 Honcho 会话。上下文跨运行累积。
- `per-repo` — 每个 git 仓库一个会话。
- `global` — 所有目录共享一个会话。

**召回模式**控制记忆如何流入对话：
- `hybrid` — 上下文自动注入到系统提示中，并且工具可用（模型决定何时查询）。
- `context` — 仅自动注入，工具隐藏。
- `tools` — 仅工具，无自动注入。Agent 必须显式调用 `honcho_reasoning`、`honcho_search` 等。

**各召回模式的设置：**

| 设置 | `hybrid` | `context` | `tools` |
|---------|----------|-----------|---------|
| `writeFrequency` | 刷新消息 | 刷新消息 | 刷新消息 |
| `contextCadence` | 控制基础上下文刷新频率 | 控制基础上下文刷新频率 | 不相关——无注入 |
| `dialecticCadence` | 控制自动 LLM 调用 | 控制自动 LLM 调用 | 不相关——模型显式调用 |
| `dialecticDepth` | 每次调用多次传递 | 每次调用多次传递 | 不相关——模型显式调用 |
| `contextTokens` | 限制注入 | 限制注入 | 不相关——无注入 |
| `dialecticDynamic` | 控制模型覆盖 | 不适用（无工具） | 控制模型覆盖 |
在 `tools` 模式下，模型完全掌控——它可以在自己选择的 `reasoning_level` 下，随时调用 `honcho_reasoning`。节奏和预算设置仅适用于自动注入模式（`hybrid` 和 `context`）。

<a id="observation-directional-vs-unified"></a>
## 观察（方向性 vs. 统一性）

Honcho 将会话建模为对等方之间交换消息。每个对等方有两个观察开关，与 Honcho 的 `SessionPeerConfig` 一一对应：

| 开关 | 效果 |
|--------|--------|
| `observeMe` | Honcho 根据该对等方自己的消息构建其表示 |
| `observeOthers` | 该对等方观察其他对等方的消息（提供跨对等方推理） |

两个对等方 × 两个开关 = 四个标志。`observationMode` 是一个简写预设：

| 预设 | 用户标志 | AI 标志 | 语义 |
|--------|-----------|----------|-----------|
| `"directional"`（默认） | me: 开, others: 开 | me: 开, others: 开 | 完全相互观察。启用跨对等方辩证——"AI 基于用户所说和 AI 的回复，对用户了解什么。" |
| `"unified"` | me: 开, others: 关 | me: 关, others: 开 | 共享池语义——AI 仅观察用户的消息，用户对等方仅自我建模。单观察者池。 |

使用显式的 `observation` 块覆盖预设，以实现每个对等方的控制：

```json
"observation": {
  "user": { "observeMe": true,  "observeOthers": true },
  "ai":   { "observeMe": true,  "observeOthers": false }
}
```

常见模式：

| 意图 | 配置 |
|--------|--------|
| 完全观察（大多数用户） | `"observationMode": "directional"` |
| AI 不应根据自身回复重新建模用户 | `"ai": {"observeMe": true, "observeOthers": false}` |
| 强人格设定，AI 对等方不应从自我观察中更新 | `"ai": {"observeMe": false, "observeOthers": true}` |

通过 [Honcho 仪表盘](https://app.honcho.dev) 设置的服务器端开关会覆盖本地默认值——Hermes 在会话初始化时会同步回来。

<a id="tools"></a>
## 工具

当 Honcho 作为记忆提供者激活时，五个工具变得可用：

| 工具 | 用途 |
|------|---------|
| `honcho_profile` | 读取或更新对等方卡片——传递 `card`（事实列表）进行更新，省略则读取 |
| `honcho_search` | 对上下文进行语义搜索——原始摘录，无 LLM 综合 |
| `honcho_context` | 完整会话上下文——摘要、表示、卡片、最近消息 |
| `honcho_reasoning` | 来自 Honcho 的 LLM 的综合答案——传递 `reasoning_level`（minimal/low/medium/high/max）以控制深度 |
| `honcho_conclude` | 创建或删除结论——传递 `conclusion` 创建，传递 `delete_id` 删除（仅限 PII） |

<a id="cli-commands"></a>
## CLI 命令

`hermes honcho` 子命令**仅在 Honcho 是活动记忆提供者时注册**（`config.yaml` 中的 `memory.provider: honcho`）。先运行 `hermes memory setup` 并选择 Honcho；该子命令会在下次调用时出现。

```bash
hermes honcho status          # 连接状态、配置和关键设置
hermes honcho setup           # 重定向到 `hermes memory setup`
hermes honcho strategy        # 显示或设置会话策略（per-session/per-directory/per-repo/global）
hermes honcho peer            # 显示或更新对等方名称 + 辩证推理级别
hermes honcho mode            # 显示或设置召回模式（hybrid/context/tools）
hermes honcho tokens          # 显示或设置上下文和辩证的令牌预算
hermes honcho identity        # 种子化或显示 AI 对等方的 Honcho 身份
hermes honcho sync            # 将 Honcho 配置同步到所有现有配置文件
hermes honcho peers           # 显示所有配置文件中的对等方身份
hermes honcho sessions        # 列出已知的 Honcho 会话映射
hermes honcho map             # 将当前目录映射到 Honcho 会话名称
hermes honcho enable          # 为活动配置文件启用 Honcho
hermes honcho disable         # 为活动配置文件禁用 Honcho
hermes honcho migrate         # 从 openclaw-honcho 逐步迁移指南
```
<a id="migrating-from-hermes-honcho"></a>
## 从 `hermes honcho` 迁移

如果你以前使用过独立的 `hermes honcho setup`：

1. 你现有的配置（`honcho.json` 或 `~/.honcho/config.json`）会被保留
2. 你的服务端数据（记忆、结论、用户画像）完整无缺
3. 在 config.yaml 中设置 `memory.provider: honcho` 即可重新激活

无需重新登录或重新设置。运行 `hermes memory setup` 并选择 "honcho" —— 向导会自动检测你的现有配置。

<a id="full-documentation"></a>
## 完整文档

参见 [Memory Providers — Honcho](./memory-providers.md#honcho) 获取完整参考。
