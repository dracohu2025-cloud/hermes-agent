---
sidebar_position: 4
title: "记忆提供者"
description: "外部记忆提供者插件 — Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover、Supermemory"
---

# 记忆提供者 {#memory-providers}

Hermes Agent 内置了 8 个外部记忆提供者插件，它们能为 Agent 提供超越内置 MEMORY.md 和 USER.md 的持久化、跨会话知识。一次只能激活**一个**外部提供者 —— 内置记忆始终与其同时处于激活状态。

## 快速开始 {#quick-start}

```bash
hermes memory setup      # 交互式选择器 + 配置
hermes memory status     # 检查当前激活的提供者
hermes memory off        # 禁用外部提供者
```

你也可以通过 `hermes plugins` → Provider Plugins → Memory Provider 来选择激活的记忆提供者。

或者在 `~/.hermes/config.yaml` 中手动设置：

```yaml
memory:
  provider: openviking   # 或 honcho, mem0, hindsight, holographic, retaindb, byterover, supermemory
```

## 工作原理 {#how-it-works}

当记忆提供者激活时，Hermes 会自动：

1.  **注入提供者上下文**到系统提示中（提供者知道的内容）
2.  **在每一轮对话前预取相关记忆**（后台、非阻塞）
3.  **在每次响应后将对话轮次同步**到提供者
4.  **在会话结束时提取记忆**（对于支持此功能的提供者）
5.  **将内置记忆的写入操作镜像**到外部提供者
6.  **添加提供者特定的工具**，以便 Agent 可以搜索、存储和管理记忆

内置记忆（MEMORY.md / USER.md）会像以前一样继续工作。外部提供者是附加功能。

## 可用提供者 {#available-providers}

### Honcho {#honcho}

具备辩证推理、会话范围上下文注入、语义搜索和持久化结论的 AI 原生跨会话用户建模。基础上下文现在包含会话摘要以及用户表征和同伴卡片，让 Agent 能够了解已经讨论过的内容。

| | |
|---|---|
| **最适合** | 需要跨会话上下文、用户-Agent 对齐的多 Agent 系统 |
| **要求** | `pip install honcho-ai` + [API 密钥](https://app.honcho.dev) 或自托管实例 |
| **数据存储** | Honcho 云或自托管 |
| **成本** | Honcho 定价（云）/ 免费（自托管） |

**工具 (5):** `honcho_profile`（读取/更新同伴卡片）、`honcho_search`（语义搜索）、`honcho_context`（会话上下文 —— 摘要、表征、卡片、消息）、`honcho_reasoning`（LLM 合成推理）、`honcho_conclude`（创建/删除结论）

**架构:** 两层上下文注入 —— 基础层（会话摘要 + 表征 + 同伴卡片，按 `contextCadence` 刷新）加上辩证补充层（LLM 推理，按 `dialecticCadence` 刷新）。辩证层会根据是否存在基础上下文，自动选择冷启动提示（通用用户事实）或热启动提示（会话范围的上下文）。

**三个独立的配置旋钮**可独立控制成本和深度：

- `contextCadence` —— 基础层刷新的频率（API 调用频率）
- `dialecticCadence` —— 辩证 LLM 触发的频率（LLM 调用频率）
- `dialecticDepth` —— 每次辩证调用中 `.chat()` 的轮次（1–3，推理深度）

**设置向导:**
```bash
hermes honcho setup        # (旧命令) 
# 或
hermes memory setup        # 选择 "honcho"
```

**配置:** `$HERMES_HOME/honcho.json`（配置文件本地）或 `~/.honcho/config.json`（全局）。解析顺序：`$HERMES_HOME/honcho.json` > `~/.hermes/honcho.json` > `~/.honcho/config.json`。请参阅 [配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md) 和 [Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

<details>
<summary>完整配置参考</summary>

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | 来自 [app.honcho.dev](https://app.honcho.dev) 的 API 密钥 |
| `baseUrl` | -- | 自托管 Honcho 的基础 URL |
| `peerName` | -- | 用户同伴身份 |
| `aiPeer` | host key | AI 同伴身份（每个配置文件一个） |
| `workspace` | host key | 共享工作区 ID |
| `contextTokens` | `null`（无上限） | 每轮自动注入上下文的令牌预算。在单词边界处截断 |
| `contextCadence` | `1` | `context()` API 调用（基础层刷新）之间的最小轮次数 |
| `dialecticCadence` | `2` | `peer.chat()` LLM 调用之间的最小轮次数。建议 1–5。仅适用于 `hybrid`/`context` 模式 |
| `dialecticDepth` | `1` | 每次辩证调用中 `.chat()` 的轮次数。限制在 1–3。第 0 轮：冷/热启动提示，第 1 轮：自我审核，第 2 轮：调和 |
| `dialecticDepthLevels` | `null` | 可选的每轮推理级别数组，例如 `["minimal", "low", "medium"]`。覆盖按比例分配的默认值 |
| `dialecticReasoningLevel` | `'low'` | 基础推理级别：`minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 为 `true` 时，模型可以通过工具参数在每次调用时覆盖推理级别 |
| `dialecticMaxChars` | `600` | 注入系统提示的辩证结果的最大字符数 |
| `recallMode` | `'hybrid'` | `hybrid`（自动注入 + 工具）、`context`（仅注入）、`tools`（仅工具） |
| `writeFrequency` | `'async'` | 何时刷新消息：`async`（后台线程）、`turn`（同步）、`session`（结束时批量），或整数 N |
| `saveMessages` | `true` | 是否将消息持久化到 Honcho API |
| `observationMode` | `'directional'` | `directional`（全部开启）或 `unified`（共享池）。可通过 `observation` 对象覆盖 |
| `messageMaxChars` | `25000` | 每条消息的最大字符数（超过则分块） |
| `dialecticMaxInputChars` | `10000` | 辩证查询输入到 `peer.chat()` 的最大字符数 |
| `sessionStrategy` | `'per-directory'` | `per-directory`、`per-repo`、`per-session`、`global` |
</details>

<details>
<summary>最小 honcho.json（云端）</summary>

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

</details>

<details>
<summary>最小 honcho.json（自托管）</summary>

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
如果你之前使用过 `hermes honcho setup`，你的配置和所有服务器端数据都完好无损。只需通过设置向导重新启用，或手动设置 `memory.provider: honcho` 即可通过新系统重新激活。
:::
<a id="migrating-from-hermes-honcho"></a>

**多 Peer 设置：**

Honcho 将对话建模为交换消息的 peer —— 每个 Hermes 配置文件对应一个用户 peer 加一个 AI peer，它们共享一个工作区。工作区是共享环境：用户 peer 在所有配置文件间是全局的，每个 AI peer 则是独立的身份。每个 AI peer 都基于自己的观察构建独立的表征/卡片，因此 `coder` 配置文件保持代码导向，而 `writer` 配置文件则保持编辑导向，面向的是同一个用户。

映射关系：

| 概念 | 说明 |
|---------|-----------|
| **工作区** | 共享环境。同一工作区下的所有 Hermes 配置文件都看到相同的用户身份。 |
| **用户 peer** (`peerName`) | 人类用户。在工作区内的所有配置文件间共享。 |
| **AI peer** (`aiPeer`) | 每个 Hermes 配置文件对应一个。主机键 `hermes` → 默认；`hermes.&lt;profile&gt;` 对应其他配置文件。 |
| **观察** | 每个 peer 的开关，控制 Honcho 从谁的消息中建模。`directional`（默认，四个开关全开）或 `unified`（单一观察者池）。 |

### 新建配置文件，创建新的 Honcho peer {#new-profile-fresh-honcho-peer}

```bash
hermes profile create coder --clone
```

`--clone` 会在 `honcho.json` 中创建一个 `hermes.coder` 主机块，其中 `aiPeer: "coder"`，共享 `workspace`，继承 `peerName`、`recallMode`、`writeFrequency`、`observation` 等设置。AI peer 会在 Honcho 中预先创建，以便在第一条消息发送前就已存在。

### 现有配置文件，回填 Honcho peer {#existing-profiles-backfill-honcho-peers}

```bash
hermes honcho sync
```

扫描每个 Hermes 配置文件，为任何没有主机块的配置文件创建主机块，从默认的 `hermes` 块继承设置，并预先创建新的 AI peer。此操作是幂等的 —— 会跳过已有主机块的配置文件。

### 每个配置文件的观察设置 {#per-profile-observation}

每个主机块可以独立覆盖观察配置。例如，一个专注于代码的配置文件，其 AI peer 观察用户但不进行自我建模：

```json
"hermes.coder": {
  "aiPeer": "coder",
  "observation": {
    "user": { "observeMe": true, "observeOthers": true },
    "ai":   { "observeMe": false, "observeOthers": true }
  }
}
```

**观察开关（每个 peer 一组）：**

| 开关 | 效果 |
|--------|--------|
| `observeMe` | Honcho 从该 peer 自己的消息中构建其表征 |
| `observeOthers` | 该 peer 观察另一个 peer 的消息（用于跨 peer 推理） |

通过 `observationMode` 预设：

- **`"directional"`**（默认）—— 所有四个开关打开。完全相互观察；启用跨 peer 辩证。
- **`"unified"`** —— 用户 `observeMe: true`，AI `observeOthers: true`，其余为 false。单一观察者池；AI 对用户建模但不自我建模，用户 peer 仅自我建模。

通过 [Honcho 仪表板](https://app.honcho.dev) 设置的服务器端开关优先级高于本地默认值 —— 在会话初始化时同步回来。

完整的观察参考请参见 [Honcho 页面](./honcho.md#observation-directional-vs-unified)。

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

请参阅 [配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md) 和 [Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

---

### OpenViking {#openviking}

由火山引擎（字节跳动）提供的上下文数据库，具有文件系统风格的知识层级、分层检索功能，并能自动将记忆提取为 6 个类别。

| | |
|---|---|
| **最适合** | 带有结构化浏览功能的自托管知识管理 |
| **要求** | `pip install openviking` + 运行服务器 |
| **数据存储** | 自托管（本地或云端） |
| **成本** | 免费（开源，AGPL-3.0 协议） |

**工具：** `viking_search`（语义搜索）、`viking_read`（分层：摘要/概览/全文）、`viking_browse`（文件系统导航）、`viking_remember`（存储事实）、`viking_add_resource`（摄取 URL/文档）

**设置：**
```bash
# 首先启动 OpenViking 服务器
pip install openviking
openviking-server

# 然后配置 Hermes
hermes memory setup    # 选择 "openviking"
# 或者手动配置：
hermes config set memory.provider openviking
echo "OPENVIKING_ENDPOINT=http://localhost:1933" >> ~/.hermes/.env
```

**主要特性：**
- 分层上下文加载：L0 (~100 tokens) → L1 (~2k) → L2 (全文)
- 在会话提交时自动提取记忆（个人资料、偏好、实体、事件、案例、模式）
- 用于分层知识浏览的 `viking://` URI 方案

---

### Mem0 {#mem0}

具有语义搜索、重排序和自动去重功能的服务器端 LLM 事实提取。

| | |
|---|---|
| **最适合** | 无需手动干预的记忆管理 — Mem0 自动处理提取 |
| **要求** | `pip install mem0ai` + API 密钥 |
| **数据存储** | Mem0 Cloud |
| **成本** | Mem0 定价 |

**工具：** `mem0_profile`（所有已存储的记忆）、`mem0_search`（语义搜索 + 重排序）、`mem0_conclude`（存储逐字事实）

**设置：**
```bash
hermes memory setup    # 选择 "mem0"
# 或者手动配置：
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

**配置：** `$HERMES_HOME/mem0.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `user_id` | `hermes-user` | 用户标识符 |
| `agent_id` | `hermes` | Agent 标识符 |

---

### Hindsight {#hindsight}

具有知识图谱、实体解析和多策略检索功能的长时记忆。`hindsight_reflect` 工具提供了其他提供者所不具备的跨记忆综合能力。自动保留完整的对话轮次（包括工具调用），并具有会话级别的文档跟踪。

| | |
|---|---|
| **最适合** | 基于知识图谱的、带有实体关系的记忆召回 |
| **要求** | 云端：来自 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 的 API 密钥。本地：LLM API 密钥（OpenAI、Groq、OpenRouter 等） |
| **数据存储** | Hindsight Cloud 或本地嵌入式 PostgreSQL |
| **成本** | Hindsight 定价（云端）或免费（本地） |

**工具：** `hindsight_retain`（存储并提取实体）、`hindsight_recall`（多策略搜索）、`hindsight_reflect`（跨记忆综合）

**设置：**
```bash
hermes memory setup    # 选择 "hindsight"
# 或者手动配置：
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

设置向导会自动安装依赖项，并且只安装所选模式所需的包（云端模式安装 `hindsight-client`，本地模式安装 `hindsight-all`）。要求 `hindsight-client >= 0.4.22`（如果版本过旧，会在会话启动时自动升级）。

**本地模式 UI：** `hindsight-embed -p hermes ui start`

**配置：** `$HERMES_HOME/hindsight/config.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `mode` | `cloud` | `cloud` 或 `local` |
| `bank_id` | `hermes` | 记忆库标识符 |
| `recall_budget` | `mid` | 召回详尽程度：`low` / `mid` / `high` |
| `memory_mode` | `hybrid` | `hybrid`（上下文 + 工具）、`context`（仅自动注入）、`tools`（仅工具） |
| `auto_retain` | `true` | 自动保留对话轮次 |
| `auto_recall` | `true` | 在每轮对话前自动召回记忆 |
| `retain_async` | `true` | 在服务器上异步处理保留操作 |
| `tags` | — | 存储记忆时应用的标签 |
| `recall_tags` | — | 召回时用于过滤的标签 |
完整配置参考请查阅 [插件 README](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/hindsight/README.md)。

---

### Holographic {#holographic}

带有 FTS5 全文搜索、信任评分和 HRR（全息缩减表示）的本地 SQLite 事实存储，用于组合代数查询。

| | |
|---|---|
| **最佳适用场景** | 具有高级检索功能的本地专属记忆，无需外部依赖 |
| **所需条件** | 无需任何额外条件（SQLite 始终可用）。NumPy 可选用于 HRR 代数运算。 |
| **数据存储** | 本地 SQLite |
| **成本** | 免费 |

**工具:** `fact_store` (9 个操作: add, search, probe, related, reason, contradict, update, remove, list), `fact_feedback` (用于训练信任评分的有帮助/无帮助评级)

**设置步骤:**
```bash
hermes memory setup    # 选择 "holographic"
# 或者手动设置:
hermes config set memory.provider holographic
```

**配置:** `config.yaml` 文件中 `plugins.hermes-memory-store` 下的配置项

| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite 数据库路径 |
| `auto_extract` | `false` | 会话结束时自动提取事实 |
| `default_trust` | `0.5` | 默认信任评分 (0.0–1.0) |

**独特能力:**
- `probe` — 针对特定实体的代数召回（关于一个人/事物的所有事实）
- `reason` — 跨多个实体的组合 AND 查询
- `contradict` — 自动检测冲突事实
- 带有不对称反馈的信任评分 (+0.05 有帮助 / -0.10 无帮助)

---

### RetainDB {#retaindb}

带有混合搜索（向量 + BM25 + 重排序）、7 种记忆类型和差异压缩的云端记忆 API。

| | |
|---|---|
| **最佳适用场景** | 已经在使用 RetainDB 基础设施的团队 |
| **所需条件** | RetainDB 账户 + API 密钥 |
| **数据存储** | RetainDB Cloud |
| **成本** | $20/月 |

**工具:** `retaindb_profile` (用户资料), `retaindb_search` (语义搜索), `retaindb_context` (任务相关上下文), `retaindb_remember` (按类型和重要性存储), `retaindb_forget` (删除记忆)

**设置步骤:**
```bash
hermes memory setup    # 选择 "retaindb"
# 或者手动设置:
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```

---

### ByteRover {#byterover}

通过 `brv` CLI 实现的持久记忆 — 带有分层检索（模糊文本 → LLM 驱动的搜索）的层级知识树。本地优先，可选云端同步。

| | |
|---|---|
| **最佳适用场景** | 希望拥有便携、本地优先的记忆且习惯使用 CLI 的开发者 |
| **所需条件** | ByteRover CLI (`npm install -g byterover-cli` 或 [安装脚本](https://byterover.dev)) |
| **数据存储** | 本地（默认）或 ByteRover Cloud（可选同步） |
| **成本** | 免费（本地）或 ByteRover 定价（云端） |

**工具:** `brv_query` (搜索知识树), `brv_curate` (存储事实/决策/模式), `brv_status` (CLI 版本 + 树状态统计)

**设置步骤:**
```bash
# 首先安装 CLI
curl -fsSL https://byterover.dev/install.sh | sh

# 然后配置 Hermes
hermes memory setup    # 选择 "byterover"
# 或者手动设置:
hermes config set memory.provider byterover
```

**关键特性:**
- 自动预压缩提取（在上下文压缩丢弃信息前保存洞察）
- 知识树存储在 `$HERMES_HOME/byterover/`（按用户资料划分）
- SOC2 Type II 认证的云端同步（可选）

---

### Supermemory {#supermemory}

带有用户资料召回、语义搜索、显性记忆工具和通过 Supermemory 图 API 会话结束时对话录入的语义长期记忆。

| | |
|---|---|
| **最佳适用场景** | 需要用户画像和会话级图谱构建的语义召回 |
| **所需条件** | `pip install supermemory` + [API 密钥](https://supermemory.ai) |
| **数据存储** | Supermemory Cloud |
| **成本** | Supermemory 定价 |

**工具:** `supermemory_store` (保存显性记忆), `supermemory_search` (语义相似性搜索), `supermemory_forget` (按 ID 或最佳匹配查询遗忘), `supermemory_profile` (持久化用户资料 + 近期上下文)

**设置步骤:**
```bash
hermes memory setup    # 选择 "supermemory"
# 或者手动设置:
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```
**配置文件:** `$HERMES_HOME/supermemory.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `container_tag` | `hermes` | 用于搜索和写入的容器标签。支持使用 `{identity}` 模板实现按 Profile 划分的标签。 |
| `auto_recall` | `true` | 在每个回合之前注入相关的记忆上下文 |
| `auto_capture` | `true` | 每次响应后存储清理后的用户-助手回合对话 |
| `max_recall_results` | `10` | 格式化到上下文中的最大召回条目数 |
| `profile_frequency` | `50` | 在第一个回合以及每隔 N 个回合包含 Profile 事实 |
| `capture_mode` | `all` | 默认跳过微小或琐碎的对话回合 |
| `search_mode` | `hybrid` | 搜索模式：`hybrid`、`memories` 或 `documents` |
| `api_timeout` | `5.0` | SDK 和摄入请求的超时时间 |

**环境变量:** `SUPERMEMORY_API_KEY` (必需), `SUPERMEMORY_CONTAINER_TAG` (覆盖配置)。

**关键特性:**
- **自动上下文隔离** — 从捕获的回合中剥离已召回的记忆，以防止递归记忆污染
- **会话结束时摄入对话**，用于构建更丰富的图谱级知识
- **Profile 事实**在第一个回合以及可配置的间隔时间被注入
- **琐碎消息过滤** (跳过 "ok", "thanks" 等)
- **Profile 范围的容器** — 在 `container_tag` 中使用 `{identity}` (例如 `hermes-{identity}` → `hermes-coder`) 来为每个 Hermes Profile 隔离记忆
- **多容器模式** — 启用 `enable_custom_container_tags` 并配合 `custom_containers` 列表，允许 Agent 在指定的容器之间进行读写。自动操作 (同步、预取) 保持在主容器上。

<details>
<summary>多容器示例</summary>

```json
{
  "container_tag": "hermes",
  "enable_custom_container_tags": true,
  "custom_containers": ["project-alpha", "shared-knowledge"],
  "custom_container_instructions": "Use project-alpha for coding context."
}
```

</details>

**支持:** [Discord](https://supermemory.link/discord) · [support@supermemory.com](mailto:support@supermemory.com)

---

## 提供商对比 {#provider-comparison}

| 提供商 | 存储方式 | 费用 | 工具数量 | 依赖 | 独特特性 |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | 云端 | 付费 | 5 | `honcho-ai` | 辩证法用户建模 + 会话范围上下文 |
| **OpenViking** | 自托管 | 免费 | 5 | `openviking` + 服务器 | 文件系统层次结构 + 分层加载 |
| **Mem0** | 云端 | 付费 | 3 | `mem0ai` | 服务器端 LLM 提取 |
| **Hindsight** | 云端/本地 | 免费/付费 | 3 | `hindsight-client` | 知识图谱 + 反思合成 |
| **Holographic** | 本地 | 免费 | 2 | 无 | HRR 代数 + 信任评分 |
| **RetainDB** | 云端 | $20/月 | 5 | `requests` | 增量压缩 |
| **ByteRover** | 本地/云端 | 免费/付费 | 3 | `brv` CLI | 预压缩提取 |
| **Supermemory** | 云端 | 付费 | 4 | `supermemory` | 上下文隔离 + 会话图谱摄入 + 多容器 |

## Profile 隔离 {#profile-isolation}

每个提供商的数据按 [Profile](/user-guide/profiles) 隔离：

- **本地存储提供商** (Holographic, ByteRover) 使用 `$HERMES_HOME/` 路径，该路径因 Profile 而异
- **配置文件提供商** (Honcho, Mem0, Hindsight, Supermemory) 将配置存储在 `$HERMES_HOME/` 中，因此每个 Profile 都有自己的凭证
- **云端提供商** (RetainDB) 自动派生出 Profile 范围的项目名称
- **环境变量提供商** (OpenViking) 通过每个 Profile 的 `.env` 文件配置

## 构建记忆提供商 {#building-a-memory-provider}

请参阅 [开发者指南：记忆提供商插件](/developer-guide/memory-provider-plugin) 了解如何创建你自己的提供商。
