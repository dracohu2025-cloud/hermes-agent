---
sidebar_position: 4
title: "记忆提供者"
description: "外部记忆提供者插件——Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover、Supermemory"
---

<a id="memory-providers"></a>
# 记忆提供者

Hermes Agent 内置了 8 个外部记忆提供者插件，使 Agent 能拥有跨会话的持久性知识，而不仅仅依赖内置的 MEMORY.md 和 USER.md。同一时间只能激活**一个**外部提供者——内置记忆始终同时生效。

<a id="quick-start"></a>
## 快速开始

```bash
hermes memory setup      # 交互式选择 + 配置
hermes memory status     # 查看当前激活的提供者
hermes memory off        # 禁用外部提供者
```

你也可以通过 `hermes plugins` → Provider Plugins → Memory Provider 来激活记忆提供者。

或者手动在 `~/.hermes/config.yaml` 中设置：

```yaml
memory:
  provider: openviking   # 或 honcho、mem0、hindsight、holographic、retaindb、byterover、supermemory
```

<a id="how-it-works"></a>
## 工作原理

当记忆提供者被激活时，Hermes 会自动执行以下操作：

1. **将提供者上下文注入**到系统提示中（提供者所知的内容）
2. **在每次对话前预取相关记忆**（后台执行，不阻塞）
3. **每次回复后将对话轮次同步**到提供者
4. **在会话结束时提取记忆**（对于支持该功能的提供者）
5. **将内置记忆的写入操作镜像**到外部提供者
6. **添加提供者专属工具**，使 Agent 能够搜索、存储和管理记忆

内置记忆（MEMORY.md / USER.md）仍然像以前一样正常工作，外部提供者起到补充作用。

<a id="available-providers"></a>
## 可用提供者

<a id="honcho"></a>
### Honcho

AI 原生的跨会话用户建模，支持辩证推理、会话作用域上下文注入、语义搜索以及持久化结论。基础上下文现在包括会话摘要、用户表征和同行卡片，使 Agent 能够感知已经讨论过的内容。

| | |
|---|---|
| **适用场景** | 需要跨会话上下文的多 Agent 系统、用户与 Agent 的一致性对齐 |
| **依赖要求** | `pip install honcho-ai` + [API 密钥](https://app.honcho.dev) 或自托管实例 |
| **数据存储** | Honcho 云服务或自托管 |
| **费用** | Honcho 定价（云服务）/ 免费（自托管） |

**工具（5 个）：** `honcho_profile`（读取/更新同行卡片）、`honcho_search`（语义搜索）、`honcho_context`（会话上下文——摘要、表征、卡片、消息）、`honcho_reasoning`（LLM 合成）、`honcho_conclude`（创建/删除结论）

**架构：** 两层上下文注入——基础层（会话摘要 + 表征 + 同行卡片，按 `contextCadence` 刷新）加上辩证补充层（LLM 推理，按 `dialecticCadence` 刷新）。辩证机制会根据基础上下文是否存在，自动选择冷启动提示（常规用户事实）或热启动提示（会话作用域上下文）。

**三个正交配置旋钮** 独立控制成本和深度：

- `contextCadence` —— 基础层刷新频率（API 调用频率）
- `dialecticCadence` —— 辩证 LLM 触发频率（LLM 调用频率）
- `dialecticDepth` —— 每次辩证调用中 `.chat()` 的轮次数（1–3，推理深度）
**安装向导：**
```bash
hermes memory setup        # 选择 "honcho" — 运行 Honcho 专用后置设置
```

旧版 `hermes honcho setup` 命令仍然有效（现在会重定向到 `hermes memory setup`），但只有在 Honcho 被选为活动记忆提供者后才会注册。

**配置：** `$HERMES_HOME/honcho.json`（配置文件本地）或 `~/.honcho/config.json`（全局）。解析顺序：`$HERMES_HOME/honcho.json` > `~/.hermes/honcho.json` > `~/.honcho/config.json`。请参阅[配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md)和[Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

<details>
<summary>完整配置参考</summary>

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | 来自 [app.honcho.dev](https://app.honcho.dev) 的 API 密钥 |
| `baseUrl` | -- | 自托管 Honcho 的基础 URL |
| `peerName` | -- | 用户对等身份 |
| `aiPeer` | 主机密钥 | AI 对等身份（每个配置文件一个） |
| `workspace` | 主机密钥 | 共享工作区 ID |
| `contextTokens` | `null`（无上限） | 每轮自动注入上下文的令牌预算。在单词边界处截断 |
| `contextCadence` | `1` | 两次 `context()` API 调用之间的最小轮数（基础层刷新） |
| `dialecticCadence` | `2` | 两次 `peer.chat()` LLM 调用之间的最小轮数。推荐 1–5。仅适用于 `hybrid`/`context` 模式 |
| `dialecticDepth` | `1` | 每次辩证调用中的 `.chat()` 传递次数。限制在 1–3。传递 0：冷/热提示；传递 1：自我审计；传递 2：协调 |
| `dialecticDepthLevels` | `null` | 可选数组，每个传递的推理级别，例如 `["minimal", "low", "medium"]`。覆盖比例默认值 |
| `dialecticReasoningLevel` | `'low'` | 基础推理级别：`minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 当为 `true` 时，模型可以通过工具参数覆盖每次调用的推理级别 |
| `dialecticMaxChars` | `600` | 注入到系统提示中的辩证结果的最大字符数 |
| `recallMode` | `'hybrid'` | `hybrid`（自动注入 + 工具）、`context`（仅注入）、`tools`（仅工具） |
| `writeFrequency` | `'async'` | 何时刷新消息：`async`（后台线程）、`turn`（同步）、`session`（结束时批量处理）或整数 N |
| `saveMessages` | `true` | 是否将消息持久化到 Honcho API |
| `observationMode` | `'directional'` | `directional`（全部开启）或 `unified`（共享池）。可通过 `observation` 对象覆盖 |
| `messageMaxChars` | `25000` | 每条消息的最大字符数（超出则分块） |
| `dialecticMaxInputChars` | `10000` | 辩证查询输入到 `peer.chat()` 的最大字符数 |
| `sessionStrategy` | `'per-directory'` | `per-directory`、`per-repo`、`per-session`、`global` |

</details>

<details>
<summary>最小化 honcho.json（云端）</summary>

```json
{
  "apiKey": "your-key-from-app.honcho.dev",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "peerName": "your-name",
      "workspace": "hermes"
    }
  }
}
```

--- END DOCUMENT CHUNK ---
</details>

<details>
<summary>最小化的 honcho.json（自托管）</summary>

```json
{
  "baseUrl": "http://localhost:8000",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "peerName": "your-name",
      "workspace": "hermes"
    }
  }
}
```

</details>

:::tip 从 `hermes honcho` 迁移
如果你之前使用过 `hermes honcho setup`，你的配置和所有服务端数据都完好无损。只需通过设置向导重新启用，或手动设置 `memory.provider: honcho` 来通过新系统重新激活。
:::
<a id="migrating-from-hermes-honcho"></a>

**多对等体设置：**

Honcho 将对等体之间的消息交换建模为会话——每个 Hermes 配置文件有一个用户对等体和一个 AI 对等体，它们共享一个工作区。工作区是共享环境：用户对等体在所有配置文件中是全局的，每个 AI 对等体有自己的身份。每个 AI 对等体根据其自身观察构建独立的表示/卡片，因此 `coder` 配置文件保持面向代码，而 `writer` 配置文件面对同一用户保持面向编辑。

映射关系：

| 概念 | 说明 |
|---------|-----------|
| **工作区** | 共享环境。同一工作区下的所有 Hermes 配置文件看到相同的用户身份。 |
| **用户对等体**（`peerName`） | 人类用户。在工作区的所有配置文件中共享。 |
| **AI 对等体**（`aiPeer`） | 每个 Hermes 配置文件一个。主机键 `hermes` → 默认；其他使用 `hermes.&lt;profile&gt;`。 |
| **观察** | 按对等体切换的选项，控制 Honcho 从谁的消息中建模。`directional`（默认，四个都开启）或 `unified`（单一观察者池）。 |

<a id="new-profile-fresh-honcho-peer"></a>
### 新建配置文件，创建全新的 Honcho 对等体

```bash
hermes profile create coder --clone
```

`--clone` 在 `honcho.json` 中创建一个 `hermes.coder` 主机块，包含 `aiPeer: "coder"`、共享 `workspace`、继承 `peerName`、`recallMode`、`writeFrequency`、`observation` 等。AI 对等体会在 Honcho 中主动创建，以便它在第一条消息之前就存在。

<a id="existing-profiles-backfill-honcho-peers"></a>
### 现有配置文件，回填 Honcho 对等体

```bash
hermes honcho sync
```

扫描每个 Hermes 配置文件，为没有任何主机块的配置文件创建主机块，从默认的 `hermes` 块继承设置，并主动创建新的 AI 对等体。幂等——跳过已存在主机块的配置文件。

<a id="per-profile-observation"></a>
### 按配置文件观察

每个主机块可以独立覆盖观察配置。示例：一个专注于代码的配置文件，其 AI 对等体观察用户但不自我建模：

```json
"hermes.coder": {
  "aiPeer": "coder",
  "observation": {
    "user": { "observeMe": true, "observeOthers": true },
    "ai":   { "observeMe": false, "observeOthers": true }
  }
}
```

**观察切换（每组对等体一组）：**

| 切换项 | 效果 |
|--------|--------|
| `observeMe` | Honcho 根据该对等体的自身消息构建其表示 |
| `observeOthers` | 该对等体观察其他对等体的消息（为跨对等体推理提供输入） |

通过 `observationMode` 预设：

- **`"directional"`**（默认）——全部四个标志开启。完全相互观察；启用跨对等体辩证。
- **`"unified"`** ——用户 `observeMe: true`，AI `observeOthers: true`，其余 false。单一观察者池；AI 对用户建模但不自建模，用户对等体仅自建模。
通过 [Honcho 仪表盘](https://app.honcho.dev) 设置的服务端开关会覆盖本地默认值——并在会话初始化时同步回来。

完整的观测参考请查看 [Honcho 页面](./honcho.md#observation-directional-vs-unified)。

<details>
<summary>完整的 honcho.json 示例（多配置文件）</summary>

```json
{
  "apiKey": "your-key",
  "workspace": "hermes",
  "peerName": "eri",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "workspace": "hermes",
      "peerName": "eri",
      "recallMode": "hybrid",
      "writeFrequency": "async",
      "sessionStrategy": "per-directory",
      "observation": {
        "user": { "observeMe": true, "observeOthers": true },
        "ai": { "observeMe": true, "observeOthers": true }
      },
      "dialecticReasoningLevel": "low",
      "dialecticDynamic": true,
      "dialecticCadence": 2,
      "dialecticDepth": 1,
      "dialecticMaxChars": 600,
      "contextCadence": 1,
      "messageMaxChars": 25000,
      "saveMessages": true
    },
    "hermes.coder": {
      "enabled": true,
      "aiPeer": "coder",
      "workspace": "hermes",
      "peerName": "eri",
      "recallMode": "tools",
      "observation": {
        "user": { "observeMe": true, "observeOthers": false },
        "ai": { "observeMe": true, "observeOthers": true }
      }
    },
    "hermes.writer": {
      "enabled": true,
      "aiPeer": "writer",
      "workspace": "hermes",
      "peerName": "eri"
    }
  },
  "sessions": {
    "/home/user/myproject": "myproject-main"
  }
}
```

</details>

请参考 [配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md) 和 [Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

---

<a id="openviking"></a>
### OpenViking

火山引擎（字节跳动）的上下文数据库，采用文件系统风格的知识层级、分层检索，并自动将记忆提取到 6 个类别中。

| | |
|---|---|
| **适用场景** | 自托管知识管理，支持结构化浏览 |
| **依赖** | `pip install openviking` + 运行中的服务器 |
| **数据存储** | 自托管（本地或云端） |
| **费用** | 免费（开源，AGPL-3.0） |

**工具：** `viking_search`（语义搜索）、`viking_read`（分层：摘要/概览/全文）、`viking_browse`（文件系统导航）、`viking_remember`（存储事实）、`viking_add_resource`（导入 URL/文档）

**设置：**
```bash
# 先启动 OpenViking 服务器
pip install openviking
openviking-server

# 然后配置 Hermes
hermes memory setup    # 选择 "openviking"
# 或者手动配置：
hermes config set memory.provider openviking
echo "OPENVIKING_ENDPOINT=http://localhost:1933" >> ~/.hermes/.env
```

**主要特性：**
- 分层上下文加载：L0（约 100 个 token）→ L1（约 2k）→ L2（完整）
- 会话提交时自动提取记忆（个人资料、偏好、实体、事件、案例、模式）
- `viking://` URI 方案，支持层级化知识浏览

---

<a id="mem0"></a>
### Mem0

服务端 LLM 事实提取，支持语义搜索、重排序和自动去重。
| | |
|---|---|
| **最佳适用场景** | 无需手动管理内存 — Mem0 自动提取 |
| **需要** | `pip install mem0ai` + API 密钥 |
| **数据存储** | Mem0 云服务 |
| **费用** | Mem0 定价 |

**工具：** `mem0_profile`（所有已存储的记忆）、`mem0_search`（语义搜索 + 重新排序）、`mem0_conclude`（存储逐字事实）

**设置：**
```bash
hermes memory setup    # 选择 "mem0"
# 或手动设置：
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

**配置：** `$HERMES_HOME/mem0.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `user_id` | `hermes-user` | 用户标识符 |
| `agent_id` | `hermes` | Agent 标识符 |

---

<a id="hindsight"></a>
### Hindsight

长时记忆，支持知识图谱、实体解析和多策略检索。`hindsight_reflect` 工具提供跨记忆综合能力，这是其他提供商所不具备的。自动保留完整的对话轮次（包括工具调用），并附带会话级别的文档追踪。

| | |
|---|---|
| **最佳适用场景** | 基于知识图谱的实体关系回忆 |
| **需要** | 云端：从 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 获取 API 密钥。本地：LLM API 密钥（OpenAI、Groq、OpenRouter 等） |
| **数据存储** | Hindsight 云服务或本地嵌入式 PostgreSQL |
| **费用** | Hindsight 定价（云端）或免费（本地） |

**工具：** `hindsight_retain`（存储并提取实体）、`hindsight_recall`（多策略搜索）、`hindsight_reflect`（跨记忆综合）

**设置：**
```bash
hermes memory setup    # 选择 "hindsight"
# 或手动设置：
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

设置向导会自动安装依赖项，并且只安装所选模式所需的组件（`hindsight-client` 用于云端，`hindsight-all` 用于本地）。需要 `hindsight-client >= 0.4.22`（如果版本过旧，会在会话启动时自动升级）。

**本地模式 UI：** `hindsight-embed -p hermes ui start`

**配置：** `$HERMES_HOME/hindsight/config.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `mode` | `cloud` | `cloud` 或 `local` |
| `bank_id` | `hermes` | 记忆库标识符 |
| `recall_budget` | `mid` | 回忆详尽程度：`low` / `mid` / `high` |
| `memory_mode` | `hybrid` | `hybrid`（上下文 + 工具）、`context`（仅自动注入）、`tools`（仅工具） |
| `auto_retain` | `true` | 自动保留对话轮次 |
| `auto_recall` | `true` | 在每次轮次前自动回忆记忆 |
| `retain_async` | `true` | 在服务器上异步处理保留操作 |
| `retain_context` | `conversation between Hermes Agent and the User` | 保留记忆的上下文标签 |
| `retain_tags` | — | 应用于保留记忆的默认标签；与每次调用的工具标签合并 |
| `retain_source` | — | 可选，附加到保留记忆的 `metadata.source` |
| `retain_user_prefix` | `User` | 自动保留的转录中用户轮次前的标签 |
| `retain_assistant_prefix` | `Assistant` | 自动保留的转录中助手轮次前的标签 |
| `recall_tags` | — | 回忆时用于过滤的标签 |
请参阅 [插件自述文件](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/hindsight/README.md) 获取完整配置参考。

---

<a id="holographic"></a>
### Holographic

基于 SQLite 的本地事实存储，支持 FTS5 全文搜索、信任评分，以及用于组合代数查询的 HRR（全息简化表示）。

| | |
|---|---|
| **适用场景** | 需要高级检索、无外部依赖的纯本地记忆 |
| **前置条件** | 无（SQLite 始终可用）。NumPy 可选，用于 HRR 代数运算。 |
| **数据存储** | 本地 SQLite |
| **费用** | 免费 |

**工具：** `fact_store`（9 种操作：添加、搜索、探测、关联、推理、矛盾、更新、删除、列出），`fact_feedback`（有用/无用评分，用于训练信任分数）

**设置：**
```bash
hermes memory setup    # 选择 "holographic"
# 或手动设置：
hermes config set memory.provider holographic
```

**配置：** `config.yaml` 文件，位于 `plugins.hermes-memory-store` 下

| 键 | 默认值 | 说明 |
|-----|---------|-------------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite 数据库路径 |
| `auto_extract` | `false` | 会话结束时自动提取事实 |
| `default_trust` | `0.5` | 默认信任分数（0.0–1.0） |

**独特能力：**
- `probe` — 基于实体的代数召回（关于某人/某物的所有事实）
- `reason` — 跨多个实体的组合 AND 查询
- `contradict` — 自动检测矛盾事实
- 非对称反馈的信任评分（有用 +0.05 / 无用 -0.10）

---

<a id="retaindb"></a>
### RetainDB

云端记忆 API，支持混合搜索（向量 + BM25 + 重排序）、7 种记忆类型和增量压缩。

| | |
|---|---|
| **适用场景** | 已在使用 RetainDB 基础设施的团队 |
| **前置条件** | RetainDB 账户 + API 密钥 |
| **数据存储** | RetainDB 云端 |
| **费用** | $20/月 |

**工具：** `retaindb_profile`（用户画像）、`retaindb_search`（语义搜索）、`retaindb_context`（任务相关上下文）、`retaindb_remember`（按类型+重要性存储）、`retaindb_forget`（删除记忆）

**设置：**
```bash
hermes memory setup    # 选择 "retaindb"
# 或手动设置：
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```

---

<a id="byterover"></a>
### ByteRover

通过 `brv` CLI 实现的持久化记忆——层级化知识树，支持分层检索（模糊文本 → LLM 驱动搜索）。本地优先，可选云同步。

| | |
|---|---|
| **适用场景** | 想要便携、本地优先且带 CLI 的记忆功能的开发者 |
| **前置条件** | ByteRover CLI（`npm install -g byterover-cli` 或[安装脚本](https://byterover.dev)） |
| **数据存储** | 本地（默认）或 ByteRover 云端（可选同步） |
| **费用** | 免费（本地）/ ByteRover 定价（云端） |

**工具：** `brv_query`（搜索知识树）、`brv_curate`（存储事实/决策/模式）、`brv_status`（CLI 版本 + 树状统计）

**设置：**
```bash
# 先安装 CLI
curl -fsSL https://byterover.dev/install.sh | sh

# 然后配置 Hermes
hermes memory setup    # 选择 "byterover"
# 或手动设置：
hermes config set memory.provider byterover
```
**主要特性：**
- 自动预压缩提取（在上下文压缩丢弃之前保存洞察）
- 知识树存储于 `$HERMES_HOME/byterover/`（按配置文件隔离）
- SOC2 Type II 认证的云同步（可选）

---

<a id="supermemory"></a>
### Supermemory

利用 Supermemory 图 API 实现具有配置文件召回、语义搜索、显式记忆工具和会话结束时对话摄入的语义长期记忆。

| | |
|---|---|
| **适用场景** | 通过用户画像和会话级图构建进行语义召回 |
| **依赖** | `pip install supermemory` + [API 密钥](https://supermemory.ai) |
| **数据存储** | Supermemory Cloud |
| **成本** | Supermemory 定价 |

**工具：** `supermemory_store`（保存显式记忆），`supermemory_search`（语义相似度搜索），`supermemory_forget`（按 ID 或最佳匹配查询遗忘），`supermemory_profile`（持久画像 + 近期上下文）

**设置：**
```bash
hermes memory setup    # 选择 "supermemory"
# 或手动：
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

**配置：** `$HERMES_HOME/supermemory.json`

| 键 | 默认值 | 说明 |
|-----|---------|-------------|
| `container_tag` | `hermes` | 用于搜索和写入的容器标签。支持 `{identity}` 模板以实现配置文件级别的作用域标签。 |
| `auto_recall` | `true` | 在对话轮次前注入相关记忆上下文 |
| `auto_capture` | `true` | 每次响应后存储清理后的用户-助手对话轮次 |
| `max_recall_results` | `10` | 最大召回条目数以格式化到上下文中 |
| `profile_frequency` | `50` | 在第一次对话及每 N 次后注入画像事实 |
| `capture_mode` | `all` | 默认跳过过短或无关紧要的对话轮次 |
| `search_mode` | `hybrid` | 搜索模式：`hybrid`、`memories` 或 `documents` |
| `api_timeout` | `5.0` | SDK 和摄取请求的超时时间 |

**环境变量：** `SUPERMEMORY_API_KEY`（必需），`SUPERMEMORY_CONTAINER_TAG`（覆盖配置）。

**主要特性：**
- 自动上下文隔离——从被捕获的对话轮次中剥离已召回的记忆，防止递归记忆污染
- 会话结束时对话摄入，用于更丰富的图级知识构建
- 在第一次对话轮次和可配置间隔处注入画像事实
- 琐碎消息过滤（跳过“好的”、“谢谢”等）
- **按配置文件隔离的容器**——在 `container_tag` 中使用 `{identity}`（例如 `hermes-{identity}` → `hermes-coder`）以隔离每个 Hermes 配置文件的记忆
- **多容器模式**——启用 `enable_custom_container_tags` 并配合 `custom_containers` 列表，让 Agent 可跨命名容器读写。自动操作（同步、预取）保持在主容器上。

<details>
<summary>多容器示例</summary>

```json
{
  "container_tag": "hermes",
  "enable_custom_container_tags": true,
  "custom_containers": ["project-alpha", "shared-knowledge"],
  "custom_container_instructions": "为编程上下文使用 project-alpha。"
}
```

</details>

**支持：** [Discord](https://supermemory.link/discord) · [support@supermemory.com](mailto:support@supermemory.com)
---

<a id="provider-comparison"></a>
## 提供商对比

| 提供商 | 存储方式 | 费用 | 工具数量 | 依赖项 | 特色功能 |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | 云端 | 付费 | 5 | `honcho-ai` | 辩证法用户建模 + 会话级上下文 |
| **OpenViking** | 自托管 | 免费 | 5 | `openviking` + 服务器 | 文件系统层级 + 分层加载 |
| **Mem0** | 云端 | 付费 | 3 | `mem0ai` | 服务端LLM提取 |
| **Hindsight** | 云端/本地 | 免费/付费 | 3 | `hindsight-client` | 知识图谱 + 反射综合 |
| **Holographic** | 本地 | 免费 | 2 | 无 | HRR代数 + 信任评分 |
| **RetainDB** | 云端 | $20/月 | 5 | `requests` | 增量压缩 |
| **ByteRover** | 本地/云端 | 免费/付费 | 3 | `brv` CLI | 预压缩提取 |
| **Supermemory** | 云端 | 付费 | 4 | `supermemory` | 上下文隔离 + 会话图摄入 + 多容器 |

<a id="profile-isolation"></a>
## 配置文件隔离

每个提供商的数据按[配置文件](/user-guide/profiles)隔离：

- **本地存储提供商**（Holographic、ByteRover）使用 `$HERMES_HOME/` 路径，每个配置文件路径不同
- **配置文件提供商**（Honcho、Mem0、Hindsight、Supermemory）将配置存储在 `$HERMES_HOME/` 中，因此每个配置文件拥有独立的凭据
- **云端提供商**（RetainDB）自动生成配置文件作用域内的项目名称
- **环境变量提供商**（OpenViking）通过每个配置文件的 `.env` 文件进行配置

<a id="building-a-memory-provider"></a>
## 构建内存提供商

请参阅[开发者指南：内存提供商插件](/developer-guide/memory-provider-plugin)了解如何创建自己的提供商。
