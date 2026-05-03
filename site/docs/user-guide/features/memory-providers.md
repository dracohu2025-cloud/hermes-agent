---
sidebar_position: 4
title: "记忆提供者"
description: "外部记忆提供者插件 — Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover、Supermemory"
---

# 记忆提供者 {#memory-providers}

Hermes Agent 内置了 8 个外部记忆提供者插件，让 Agent 拥有超越内置 MEMORY.md 和 USER.md 的持久化跨会话知识。同一时间只能激活 **一个** 外部提供者——内置记忆始终与其同时激活。

## 快速开始 {#quick-start}

```bash
hermes memory setup      # 交互式选择器 + 配置
hermes memory status     # 检查当前激活状态
hermes memory off        # 禁用外部提供者
```

你也可以通过 `hermes plugins` → Provider Plugins → Memory Provider 选择激活的记忆提供者。

或者手动在 `~/.hermes/config.yaml` 中设置：

```yaml
memory:
  provider: openviking   # 或 honcho、mem0、hindsight、holographic、retaindb、byterover、supermemory
```

## 工作原理 {#how-it-works}

当记忆提供者激活时，Hermes 会自动：

1. **将提供者上下文注入**系统提示（提供者已知的信息）
2. **在每次交互前预取相关记忆**（后台非阻塞操作）
3. **每次响应后将对话轮次同步**到提供者
4. **在会话结束时提取记忆**（适用于支持该功能的提供者）
5. **将内置记忆写入操作镜像**到外部提供者
6. **添加提供者专属工具**，使 Agent 能够搜索、存储和管理记忆
内置内存（MEMORY.md / USER.md）继续像以前一样工作。外部提供者是附加的。

## 可用提供者 {#available-providers}

### Honcho {#honcho}

AI 原生的跨会话用户建模，具备辩证推理、会话范围上下文注入、语义搜索和持久结论。基础上下文现在包含会话摘要以及用户表示和同伴卡片，使 Agent 能够感知已经讨论过的内容。

| | |
|---|---|
| **最佳适用** | 具有跨会话上下文的 Multi-agent 系统，用户与 Agent 的对齐 |
| **需要** | `pip install honcho-ai` + [API key](https://app.honcho.dev) 或自托管实例 |
| **数据存储** | Honcho Cloud 或自托管 |
| **成本** | Honcho 定价（云）/ 免费（自托管） |

**工具（5个）：** `honcho_profile`（读取/更新同伴卡片），`honcho_search`（语义搜索），`honcho_context`（会话上下文——摘要、表示、卡片、消息），`honcho_reasoning`（LLM 合成），`honcho_conclude`（创建/删除结论）
**架构：** 双层上下文注入——基础层（会话摘要 + 表示 + 同伴卡片，按 `contextCadence` 刷新）加上辩证补充（LLM 推理，按 `dialecticCadence` 刷新）。辩证层会根据基础上下文是否存在，自动选择冷启动提示（通用用户事实）或热提示（会话范围上下文）。

**三个正交配置旋钮** 独立控制成本与深度：

- `contextCadence` — 基础层刷新频率（API 调用频率）
- `dialecticCadence` — 辩证 LLM 触发频率（LLM 调用频率）
- `dialecticDepth` — 每次辩证调用中 `.chat()` 的轮数（1–3，推理深度）

**设置向导：**
```bash
hermes honcho setup        # (旧版命令) 
# 或
hermes memory setup        # 选择 "honcho"
```

**配置：** `$HERMES_HOME/honcho.json`（配置文件本地）或 `~/.honcho/config.json`（全局）。解析顺序：`$HERMES_HOME/honcho.json` > `~/.hermes/honcho.json` > `~/.honcho/config.json`。参见[配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md)和[Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。
<details>
<summary>完整配置参考</summary>

| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | 来自 [app.honcho.dev](https://app.honcho.dev) 的 API 密钥 |
| `baseUrl` | -- | 自托管 Honcho 的基础 URL |
| `peerName` | -- | 用户对等身份标识 |
| `aiPeer` | 主机密钥 | AI 对等身份标识（每个配置文件一个） |
| `workspace` | 主机密钥 | 共享工作空间 ID |
| `contextTokens` | `null`（无上限） | 每轮自动注入上下文的 token 预算。在单词边界截断 |
| `contextCadence` | `1` | 两次 `context()` API 调用之间的最小轮数（基础层刷新） |
| `dialecticCadence` | `2` | 两次 `peer.chat()` LLM 调用之间的最小轮数。建议值 1-5。仅适用于 `hybrid`/`context` 模式 |
| `dialecticDepth` | `1` | 每次辩证调用执行的 `.chat()` 轮数。取值范围 1-3。第 0 轮：冷/热提示，第 1 轮：自我审计，第 2 轮：调和 |
| `dialecticDepthLevels` | `null` | 可选数组，指定每轮推理级别，例如 `["minimal", "low", "medium"]`。覆盖比例默认值 |
| `dialecticReasoningLevel` | `'low'` | 基础推理级别：`minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 若为 `true`，模型可通过工具参数在每次调用时覆盖推理级别 |
| `dialecticMaxChars` | `600` | 注入到系统提示中的辩证结果最大字符数 |
| `recallMode` | `'hybrid'` | `hybrid`（自动注入+工具）、`context`（仅注入）、`tools`（仅工具） |
| `writeFrequency` | `'async'` | 消息刷新时机：`async`（后台线程）、`turn`（同步）、`session`（结束时批量）或整数 N |
| `saveMessages` | `true` | 是否将消息持久化到 Honcho API |
| `observationMode` | `'directional'` | `directional`（全部开启）或 `unified`（共享池），可使用 `observation` 对象覆盖 |
| `messageMaxChars` | `25000` | 每条消息的最大字符数（超出则分块） |
| `dialecticMaxInputChars` | `10000` | `peer.chat()` 辩证查询输入的最大字符数 |
| `sessionStrategy` | `'per-directory'` | `per-directory`、`per-repo`、`per-session`、`global` |

--- END DOCUMENT CHUNK ---
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

</details>

<details>
<summary>最小化 honcho.json（自托管）</summary>

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

<a id="migrating-from-hermes-honcho"></a>
:::tip 从 `hermes honcho` 迁移
如果你之前使用过 `hermes honcho setup`，你的配置和所有服务端数据都完好无损。只需再次通过设置向导重新启用，或手动设置 `memory.provider: honcho` 即可通过新系统重新激活。
:::

**多 peer 设置：**

Honcho 将对话建模为 peer 之间交换消息——每个 Hermes 配置对应一个用户 peer 加一个 AI peer，所有 peer 共享同一个 workspace。workspace 是共享环境：用户 peer 在所有配置中全局存在，每个 AI peer 拥有自己的身份。每个 AI peer 根据自身的观察构建独立的表征/卡片，因此 `coder` 配置会保持代码导向，而 `writer` 配置则针对同一用户保持编辑风格。
映射关系：

| 概念 | 说明 |
|---------|-----------|
| **工作区（Workspace）** | 共享环境。同一工作区下的所有 Hermes 配置文件都看到相同的用户身份。 |
| **用户对等体（`peerName`）** | 人类用户。在工作区内的各配置文件间共享。 |
| **AI 对等体（`aiPeer`）** | 每个 Hermes 配置文件一个。主机键 `hermes` → 默认；其他使用 `hermes.&lt;profile&gt;`。 |
| **观察（Observation）** | 按对等体切换，控制 Honcho 从谁的消息中建模。`directional`（默认，四个方向全开）或 `unified`（单一观察者池）。 |

### 新建配置文件，创建全新的 Honcho 对等体 {#new-profile-fresh-honcho-peer}

```bash
hermes profile create coder --clone
```

`--clone` 会在 `honcho.json` 中创建一个 `hermes.coder` 主机块，包含 `aiPeer: "coder"`、共享的 `workspace`、继承的 `peerName`、`recallMode`、`writeFrequency`、`observation` 等。AI 对等体会在 Honcho 中立即创建，确保它在第一条消息发送前就已存在。

### 已有配置文件，回填 Honcho 对等体 {#existing-profiles-backfill-honcho-peers}

```bash
hermes honcho sync
```

扫描每个 Hermes 配置文件，为没有主机块的配置文件创建主机块，继承默认 `hermes` 块的设置，并立即创建新的 AI 对等体。该操作是幂等的——会跳过已有主机块的配置文件。
### 按 Profile 的观察配置 {#per-profile-observation}

每个 host 块可以独立覆盖观察配置。示例：一个以代码为中心的 profile，其中 AI 对等体观察用户但不进行自我建模：

```json
"hermes.coder": {
  "aiPeer": "coder",
  "observation": {
    "user": { "observeMe": true, "observeOthers": true },
    "ai":   { "observeMe": false, "observeOthers": true }
  }
}
```

**观察开关（每个对等体一组）：**

| 开关 | 效果 |
|--------|--------|
| `observeMe` | Honcho 根据该对等体自身的消息构建其表示 |
| `observeOthers` | 该对等体观察另一对等体的消息（驱动跨对等体推理） |

通过 `observationMode` 预设：

- **`"directional"`**（默认）—— 四个标志全部开启。完全相互观察；启用跨对等体辩证。
- **`"unified"`** —— 用户 `observeMe: true`，AI `observeOthers: true`，其余为 false。单一观察者池；AI 对用户建模但不自我建模，用户对等体仅自我建模。

通过 [Honcho 控制台](https://app.honcho.dev) 设置的服务器端开关会覆盖本地默认值 —— 在会话初始化时同步回来。
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

参见 [配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md) 和 [Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

---

### OpenViking {#openviking}

由火山引擎（字节跳动）开发的上下文数据库，具有文件系统风格的知识层次、分层检索，以及自动将记忆提取为6个类别的能力。

| | |
|---|---|
| **最佳适用场景** | 自托管知识管理，支持结构化浏览 |
| **要求** | `pip install openviking` + 运行服务器 |
| **数据存储** | 自托管（本地或云端） |
| **费用** | 免费（开源，AGPL-3.0） |

**工具：** `viking_search`（语义搜索）、`viking_read`（分层：摘要/概述/全文）、`viking_browse`（文件系统导航）、`viking_remember`（存储事实）、`viking_add_resource`（导入 URL/文档）

**设置：**
```bash
# Start the OpenViking server first
pip install openviking
openviking-server

# Then configure Hermes
hermes memory setup    # select "openviking"
# Or manually:
hermes config set memory.provider openviking
echo "OPENVIKING_ENDPOINT=http://localhost:1933" >> ~/.hermes/.env
```
**主要特性：**
- 分层上下文加载：L0（约 100 tokens）→ L1（约 2k）→ L2（完整）
- 会话提交时自动提取记忆（个人资料、偏好、实体、事件、案例、模式）
- `viking://` URI 方案，用于分层知识浏览

---

### Mem0 {#mem0}

服务端 LLM 事实提取，支持语义搜索、重排序和自动去重。

| | |
|---|---|
| **最佳适用场景** | 无需手动管理记忆 — Mem0 自动完成提取 |
| **需要** | `pip install mem0ai` + API 密钥 |
| **数据存储** | Mem0 云服务 |
| **费用** | Mem0 定价 |

**工具：** `mem0_profile`（所有已存储记忆）、`mem0_search`（语义搜索 + 重排序）、`mem0_conclude`（逐字存储事实）

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

### Hindsight {#hindsight}

基于知识图谱、实体解析和多策略检索的长期记忆。`hindsight_reflect` 工具提供了其他提供商没有的跨记忆综合能力。自动保留完整的对话轮次（包括工具调用），并支持会话级别的文档追踪。

| | |
|---|---|
| **最佳适用场景** | 基于知识图谱的实体关系回忆 |
| **所需条件** | 云端：从 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 获取 API 密钥。本地：LLM API 密钥（OpenAI、Groq、OpenRouter 等） |
| **数据存储** | Hindsight 云端或本地嵌入式 PostgreSQL |
| **费用** | Hindsight 定价（云端）或免费（本地） |

**工具：** `hindsight_retain`（存储并提取实体）、`hindsight_recall`（多策略搜索）、`hindsight_reflect`（跨记忆综合）

**设置：**
```bash
hermes memory setup    # 选择 "hindsight"
# 或手动设置：
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```
安装向导会自动安装依赖项，并且只安装所选模式所需的依赖项（`cloud` 模式安装 `hindsight-client`，`local` 模式安装 `hindsight-all`）。需要 `hindsight-client >= 0.4.22`（如果版本过旧，会在会话启动时自动升级）。

**本地模式 UI：** `hindsight-embed -p hermes ui start`

**配置：** `$HERMES_HOME/hindsight/config.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `mode` | `cloud` | `cloud` 或 `local` |
| `bank_id` | `hermes` | 记忆库标识符 |
| `recall_budget` | `mid` | 召回详尽程度：`low` / `mid` / `high` |
| `memory_mode` | `hybrid` | `hybrid`（上下文 + 工具）、`context`（仅自动注入）、`tools`（仅工具） |
| `auto_retain` | `true` | 自动保留对话轮次 |
| `auto_recall` | `true` | 每轮对话前自动召回记忆 |
| `retain_async` | `true` | 在服务器上异步处理保留操作 |
| `retain_context` | `conversation between Hermes Agent and the User` | 保留记忆的上下文标签 |
| `retain_tags` | — | 应用于保留记忆的默认标签；与每次调用的工具标签合并 |
| `retain_source` | — | 可选，附加到保留记忆的 `metadata.source` |
| `retain_user_prefix` | `User` | 自动保留的对话记录中用户轮次前的标签 |
| `retain_assistant_prefix` | `Assistant` | 自动保留的对话记录中助手轮次前的标签 |
| `recall_tags` | — | 召回时用于过滤的标签 |
请参阅 [插件 README](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/hindsight/README.md) 获取完整的配置参考。

---

### Holographic {#holographic}

本地 SQLite 事实存储，支持 FTS5 全文搜索、信任评分以及用于组合代数查询的 HRR（全息简化表示）。

| | |
|---|---|
| **最佳适用场景** | 仅限本地内存，具备高级检索能力，无外部依赖 |
| **依赖要求** | 无（SQLite 始终可用）。HRR 代数运算可选 NumPy。 |
| **数据存储** | 本地 SQLite |
| **成本** | 免费 |

**工具：** `fact_store`（9 个操作：添加、搜索、探查、关联、推理、矛盾、更新、删除、列出），`fact_feedback`（有用/无用的评分，用于训练信任分数）

**设置：**
```bash
hermes memory setup    # 选择 "holographic"
# 或手动设置：
hermes config set memory.provider holographic
```

**配置：** `config.yaml` 文件，位于 `plugins.hermes-memory-store` 下

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite 数据库路径 |
| `auto_extract` | `false` | 在会话结束时自动提取事实 |
| `default_trust` | `0.5` | 默认信任分数（0.0–1.0） |
**独特能力：**
- `probe` — 针对实体的代数回忆（关于某个人/事物的所有事实）
- `reason` — 跨多个实体的组合 AND 查询
- `contradict` — 自动检测矛盾事实
- 基于非对称反馈的可信度评分（+0.05 有帮助 / -0.10 无帮助）

---

### RetainDB {#retaindb}

云端记忆 API，支持混合搜索（向量 + BM25 + 重排序）、7 种记忆类型以及增量压缩。

| | |
|---|---|
| **最佳适用场景** | 已在使用 RetainDB 基础设施的团队 |
| **前提条件** | RetainDB 账户 + API 密钥 |
| **数据存储** | RetainDB 云端 |
| **费用** | 20 美元/月 |

**工具：** `retaindb_profile`（用户画像）、`retaindb_search`（语义搜索）、`retaindb_context`（任务相关上下文）、`retaindb_remember`（按类型+重要性存储）、`retaindb_forget`（删除记忆）

**设置：**
```bash
hermes memory setup    # 选择 "retaindb"
# 或手动设置：
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```
---

### ByteRover {#byterover}

通过 `brv` CLI 实现持久化记忆——分层知识树，支持分级检索（模糊文本 → LLM 驱动搜索）。本地优先，可选云同步。

| | |
|---|---|
| **最佳适用场景** | 需要便携、本地优先且带 CLI 的记忆功能的开发者 |
| **依赖** | ByteRover CLI（`npm install -g byterover-cli` 或 [安装脚本](https://byterover.dev)） |
| **数据存储** | 本地（默认）或 ByteRover Cloud（可选同步） |
| **费用** | 免费（本地）或 ByteRover 定价（云端） |

**工具：** `brv_query`（搜索知识树）、`brv_curate`（存储事实/决策/模式）、`brv_status`（CLI 版本 + 知识树统计）

**设置：**
```bash
# 首先安装 CLI
curl -fsSL https://byterover.dev/install.sh | sh

# 然后配置 Hermes
hermes memory setup    # 选择 "byterover"
# 或手动配置：
hermes config set memory.provider byterover
```

**主要特性：**
- 自动预压缩提取（在上下文压缩丢弃之前保存关键洞察）
- 知识树存储在 `$HERMES_HOME/byterover/`（按配置文件作用域划分）
- SOC2 Type II 认证的云同步（可选）
---

### Supermemory {#supermemory}

基于语义的长期记忆，支持用户画像召回、语义搜索、显式记忆工具，以及通过 Supermemory 图 API 在会话结束时自动摄入对话内容。

| | |
|---|---|
| **适用场景** | 需要语义召回、用户画像构建和会话级图构建的场景 |
| **依赖** | `pip install supermemory` + [API 密钥](https://supermemory.ai) |
| **数据存储** | Supermemory 云端 |
| **费用** | 按 Supermemory 定价 |

**工具：** `supermemory_store`（保存显式记忆）、`supermemory_search`（语义相似度搜索）、`supermemory_forget`（按 ID 或最佳匹配查询遗忘）、`supermemory_profile`（持久化画像 + 近期上下文）

**设置：**
```bash
hermes memory setup    # 选择 "supermemory"
# 或手动设置：
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

**配置：** `$HERMES_HOME/supermemory.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `container_tag` | `hermes` | 用于搜索和写入的容器标签。支持 `{identity}` 模板以实现按画像作用域的标签。 |
| `auto_recall` | `true` | 在每次对话轮次前自动注入相关的记忆上下文 |
| `auto_capture` | `true` | 每次响应后自动存储清理后的用户-助手对话轮次 |
| `max_recall_results` | `10` | 最多召回多少条记忆并格式化为上下文 |
| `profile_frequency` | `50` | 在首次对话轮次及每 N 轮后包含画像事实 |
| `capture_mode` | `all` | 默认跳过过短或无关紧要的对话轮次 |
| `search_mode` | `hybrid` | 搜索模式：`hybrid`（混合）、`memories`（记忆）或 `documents`（文档） |
| `api_timeout` | `5.0` | SDK 和摄入请求的超时时间 |
**环境变量：** `SUPERMEMORY_API_KEY`（必需），`SUPERMEMORY_CONTAINER_TAG`（覆盖配置）。

**关键特性：**
- 自动上下文隔离——从捕获的对话轮次中剥离已回忆的记忆，防止递归记忆污染
- 会话结束时对话摄入，用于构建更丰富的图谱级知识
- 在首次对话轮次及可配置间隔注入个人资料事实
- 琐碎消息过滤（跳过“好的”、“谢谢”等）
- **按个人资料隔离容器**——在 `container_tag` 中使用 `{identity}`（例如 `hermes-{identity}` → `hermes-coder`），按 Hermes 个人资料隔离记忆
- **多容器模式**——启用 `enable_custom_container_tags` 并设置 `custom_containers` 列表，让 Agent 跨命名容器读写。自动操作（同步、预取）仍保留在主容器上。

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

**支持：** [Discord](https://supermemory.link/discord) · [support@supermemory.com](mailto:support@supermemory.com)

---

## 提供商对比 {#provider-comparison}

| 提供商 | 存储方式 | 费用 | 工具数量 | 依赖项 | 独特功能 |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | 云端 | 付费 | 5 | `honcho-ai` | 辩证用户建模 + 会话范围上下文 |
| **OpenViking** | 自托管 | 免费 | 5 | `openviking` + 服务器 | 文件系统层级 + 分层加载 |
| **Mem0** | 云端 | 付费 | 3 | `mem0ai` | 服务端 LLM 提取 |
| **Hindsight** | 云端/本地 | 免费/付费 | 3 | `hindsight-client` | 知识图谱 + 反思综合 |
| **Holographic** | 本地 | 免费 | 2 | 无 | HRR 代数 + 信任评分 |
| **RetainDB** | 云端 | 20美元/月 | 5 | `requests` | 增量压缩 |
| **ByteRover** | 本地/云端 | 免费/付费 | 3 | `brv` 命令行工具 | 预压缩提取 |
| **Supermemory** | 云端 | 付费 | 4 | `supermemory` | 上下文隔离 + 会话图摄取 + 多容器 |
## 配置文件隔离 {#profile-isolation}

每个提供者的数据根据[配置文件](/user-guide/profiles)进行隔离：

- **本地存储提供者**（Holographic、ByteRover）使用每个配置文件不同的 `$HERMES_HOME/` 路径
- **配置文件提供者**（Honcho、Mem0、Hindsight、Supermemory）将配置存储在 `$HERMES_HOME/` 中，因此每个配置文件拥有自己的凭据
- **云提供者**（RetainDB）自动推导出配置文件作用域下的项目名称
- **环境变量提供者**（OpenViking）通过每个配置文件的 `.env` 文件进行配置

## 构建记忆提供者 {#building-a-memory-provider}

请参阅[开发者指南：记忆提供者插件](/developer-guide/memory-provider-plugin)了解如何创建自己的提供者。
