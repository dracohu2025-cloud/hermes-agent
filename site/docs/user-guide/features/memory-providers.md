---
sidebar_position: 4
title: "Memory Providers"
description: "外部内存提供程序插件 — Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory"
---

# Memory Providers

Hermes Agent 附带了 8 个外部内存提供程序插件，这些插件为 Agent 提供了超越内置 `MEMORY.md` 和 `USER.md` 的持久化、跨会话知识。同一时间只能激活**一个**外部提供程序，但内置内存始终会与其同时处于活动状态。

## 快速开始

```bash
hermes memory setup      # 交互式选择器 + 配置
hermes memory status     # 检查当前激活的程序
hermes memory off        # 禁用外部提供程序
```

或者在 `~/.hermes/config.yaml` 中手动设置：

```yaml
memory:
  provider: openviking   # 或 honcho, mem0, hindsight, holographic, retaindb, byterover, supermemory
```

## 工作原理

当内存提供程序处于活动状态时，Hermes 会自动执行以下操作：

1. **注入提供程序上下文**到系统提示词中（提供程序已知的内容）
2. **预取相关记忆**（在每轮对话前，后台异步执行，不阻塞）
3. **同步对话轮次**到提供程序（在每次响应后）
4. **在会话结束时提取记忆**（针对支持此功能的提供程序）
5. **镜像内置内存写入**到外部提供程序
6. **添加特定于提供程序的工具**，以便 Agent 可以搜索、存储和管理记忆

内置内存（`MEMORY.md` / `USER.md`）的工作方式与之前完全相同。外部提供程序是附加的。

## 可用提供程序

### Honcho

AI 原生跨会话用户建模，支持辩证问答、语义搜索和持久化结论。

| | |
|---|---|
| **适用场景** | 具有跨会话上下文的多 Agent 系统，用户与 Agent 对齐 |
| **要求** | `pip install honcho-ai` + [API key](https://app.honcho.dev) 或自托管实例 |
| **数据存储** | Honcho Cloud 或自托管 |
| **费用** | Honcho 定价（云端）/ 免费（自托管） |

**工具：** `honcho_profile` (个人卡片), `honcho_search` (语义搜索), `honcho_context` (LLM 合成), `honcho_conclude` (存储事实)

**设置向导：**
```bash
hermes honcho setup        # (旧版命令) 
# 或
hermes memory setup        # 选择 "honcho"
```

**配置：** `$HERMES_HOME/honcho.json` (配置项本地) 或 `~/.honcho/config.json` (全局)。解析顺序：`$HERMES_HOME/honcho.json` > `~/.hermes/honcho.json` > `~/.honcho/config.json`。请参阅 [配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md) 和 [Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

<details>
<summary>关键配置选项</summary>

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | 来自 [app.honcho.dev](https://app.honcho.dev) 的 API key |
| `baseUrl` | -- | 自托管 Honcho 的基础 URL |
| `peerName` | -- | 用户对等身份 |
| `aiPeer` | host key | AI 对等身份（每个配置项一个） |
| `workspace` | host key | 共享工作区 ID |
| `recallMode` | `hybrid` | `hybrid` (自动注入 + 工具), `context` (仅注入), `tools` (仅工具) |
| `observation` | all on | 每个对等方的 `observeMe`/`observeOthers` 布尔值 |
| `writeFrequency` | `async` | `async`, `turn`, `session`, 或整数 N |
| `sessionStrategy` | `per-directory` | `per-directory`, `per-repo`, `per-session`, `global` |
| `dialecticReasoningLevel` | `low` | `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | 根据查询长度自动提升推理级别 |
| `messageMaxChars` | `25000` | 每条消息的最大字符数（超出则分块） |

</details>

<details>
<summary>最小化 honcho.json (云端)</summary>

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
<summary>最小化 honcho.json (自托管)</summary>

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
如果您之前使用过 `hermes honcho setup`，您的配置和所有服务器端数据都保持完整。只需通过设置向导重新启用，或手动设置 `memory.provider: honcho` 即可通过新系统重新激活。
:::

**多 Agent / 配置项：**

每个 Hermes 配置项都会获得其自己的 Honcho AI 对等方，同时共享同一个工作区 —— 所有配置项都能看到相同的用户表示，但每个 Agent 都会建立自己的身份和观察结果。

```bash
hermes profile create coder --clone   # 创建 honcho 对等方 "coder"，从默认配置继承
```

`--clone` 的作用：在 `honcho.json` 中创建一个 `hermes.coder` 主机块，包含 `aiPeer: "coder"`、共享的 `workspace`、继承的 `peerName`、`recallMode`、`writeFrequency`、`observation` 等。该对等方会在 Honcho 中被预先创建，以便在第一条消息发送前就已存在。

对于在 Honcho 设置之前创建的配置项：

```bash
hermes honcho sync   # 扫描所有配置项，为缺失的配置项创建主机块
```

这将从默认的 `hermes` 主机块继承设置，并为每个配置项创建新的 AI 对等方。该操作是幂等的 —— 会跳过已经拥有主机块的配置项。

<details>
<summary>完整的 honcho.json 示例 (多配置项)</summary>

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
      "dialecticMaxChars": 600,
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

### OpenViking

由 Volcengine (字节跳动) 开发的上下文数据库，具有文件系统风格的知识层级、分层检索以及自动将记忆提取为 6 个类别的功能。

| | |
|---|---|
| **适用场景** | 带有结构化浏览功能的自托管知识管理 |
| **要求** | `pip install openviking` + 运行服务器 |
| **数据存储** | 自托管（本地或云端） |
| **费用** | 免费 (开源, AGPL-3.0) |

**工具：** `viking_search` (语义搜索), `viking_read` (分层：摘要/概览/全文), `viking_browse` (文件系统导航), `viking_remember` (存储事实), `viking_add_resource` (摄入 URL/文档)

**设置：**
```bash
# 首先启动 OpenViking 服务器
pip install openviking
openviking-server

# 然后配置 Hermes
hermes memory setup    # 选择 "openviking"
# 或手动设置：
hermes config set memory.provider openviking
echo "OPENVIKING_ENDPOINT=http://localhost:1933" >> ~/.hermes/.env
```

**主要功能：**
- 分层上下文加载：L0 (~100 tokens) → L1 (~2k) → L2 (全文)
- 会话提交时自动提取记忆（配置项、偏好、实体、事件、案例、模式）
- 用于层级知识浏览的 `viking://` URI 方案

---

### Mem0

服务器端 LLM 事实提取，支持语义搜索、重排序和自动去重。

| | |
|---|---|
| **适用场景** | 无需人工干预的记忆管理 — Mem0 自动处理提取 |
| **要求** | `pip install mem0ai` + API key |
| **数据存储** | Mem0 Cloud |
| **费用** | Mem0 定价 |
**Tools:** `mem0_profile` (所有已存储的记忆), `mem0_search` (语义搜索 + 重排序), `mem0_conclude` (存储逐字事实)

**设置:**
```bash
hermes memory setup    # 选择 "mem0"
# 或手动设置:
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

**配置:** `$HERMES_HOME/mem0.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `user_id` | `hermes-user` | 用户标识符 |
| `agent_id` | `hermes` | Agent 标识符 |

---

### Hindsight

具备知识图谱、实体解析和多策略检索功能的长期记忆系统。`hindsight_reflect` 工具提供了其他提供商所不具备的跨记忆综合能力。能够自动保留完整的对话轮次（包括工具调用），并支持会话级文档追踪。

| | |
|---|---|
| **适用场景** | 基于知识图谱的召回及实体关系分析 |
| **要求** | 云端：从 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 获取 API 密钥。本地：LLM API 密钥（OpenAI、Groq、OpenRouter 等） |
| **数据存储** | Hindsight 云端或本地嵌入式 PostgreSQL |
| **成本** | Hindsight 定价（云端）或免费（本地） |

**Tools:** `hindsight_retain` (带实体提取的存储), `hindsight_recall` (多策略搜索), `hindsight_reflect` (跨记忆综合)

**设置:**
```bash
hermes memory setup    # 选择 "hindsight"
# 或手动设置:
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

设置向导会自动安装依赖项，且仅安装所选模式所需的组件（云端模式安装 `hindsight-client`，本地模式安装 `hindsight-all`）。要求 `hindsight-client >= 0.4.22`（若版本过旧，会在会话启动时自动升级）。

**本地模式 UI:** `hindsight-embed -p hermes ui start`

**配置:** `$HERMES_HOME/hindsight/config.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `mode` | `cloud` | `cloud` 或 `local` |
| `bank_id` | `hermes` | 记忆库标识符 |
| `recall_budget` | `mid` | 召回彻底程度：`low` / `mid` / `high` |
| `memory_mode` | `hybrid` | `hybrid` (上下文 + 工具), `context` (仅自动注入), `tools` (仅工具) |
| `auto_retain` | `true` | 自动保留对话轮次 |
| `auto_recall` | `true` | 在每轮对话前自动召回记忆 |
| `retain_async` | `true` | 在服务器端异步处理保留任务 |
| `tags` | — | 存储记忆时应用的标签 |
| `recall_tags` | — | 召回时用于过滤的标签 |

完整的配置参考请参阅 [插件 README](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/hindsight/README.md)。

---

### Holographic

基于本地 SQLite 的事实存储，支持 FTS5 全文搜索、信任评分以及用于组合代数查询的 HRR（全息缩减表示）。

| | |
|---|---|
| **适用场景** | 仅限本地的记忆系统，具备高级检索功能，无外部依赖 |
| **要求** | 无（SQLite 始终可用）。HRR 代数运算可选配 NumPy。 |
| **数据存储** | 本地 SQLite |
| **成本** | 免费 |

**Tools:** `fact_store` (9 个操作：添加、搜索、探查、关联、推理、矛盾检测、更新、移除、列表), `fact_feedback` (用于训练信任评分的有用/无用评价)

**设置:**
```bash
hermes memory setup    # 选择 "holographic"
# 或手动设置:
hermes config set memory.provider holographic
```

**配置:** `plugins.hermes-memory-store` 下的 `config.yaml`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite 数据库路径 |
| `auto_extract` | `false` | 在会话结束时自动提取事实 |
| `default_trust` | `0.5` | 默认信任评分 (0.0–1.0) |

**独特功能:**
- `probe` — 特定实体的代数召回（关于某人/某事的所有事实）
- `reason` — 跨多个实体的组合 AND 查询
- `contradict` — 自动检测冲突事实
- 具备非对称反馈的信任评分（有用 +0.05 / 无用 -0.10）

---

### RetainDB

云端记忆 API，支持混合搜索（向量 + BM25 + 重排序）、7 种记忆类型及增量压缩。

| | |
|---|---|
| **适用场景** | 已在使用 RetainDB 基础设施的团队 |
| **要求** | RetainDB 账户 + API 密钥 |
| **数据存储** | RetainDB 云端 |
| **成本** | $20/月 |

**Tools:** `retaindb_profile` (用户资料), `retaindb_search` (语义搜索), `retaindb_context` (任务相关上下文), `retaindb_remember` (带类型和重要性的存储), `retaindb_forget` (删除记忆)

**设置:**
```bash
hermes memory setup    # 选择 "retaindb"
# 或手动设置:
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```

---

### ByteRover

通过 `brv` CLI 实现的持久化记忆——分层知识树，支持分级检索（模糊文本 → LLM 驱动的搜索）。以本地优先，支持可选的云端同步。

| | |
|---|---|
| **适用场景** | 希望拥有便携、本地优先且带 CLI 记忆功能的开发者 |
| **要求** | ByteRover CLI (`npm install -g byterover-cli` 或 [安装脚本](https://byterover.dev)) |
| **数据存储** | 本地（默认）或 ByteRover 云端（可选同步） |
| **成本** | 免费（本地）或 ByteRover 定价（云端） |

**Tools:** `brv_query` (搜索知识树), `brv_curate` (存储事实/决策/模式), `brv_status` (CLI 版本 + 树统计信息)

**设置:**
```bash
# 首先安装 CLI
curl -fsSL https://byterover.dev/install.sh | sh

# 然后配置 Hermes
hermes memory setup    # 选择 "byterover"
# 或手动设置:
hermes config set memory.provider byterover
```

**关键特性:**
- 自动预压缩提取（在上下文压缩丢弃见解之前将其保存）
- 知识树存储在 `$HERMES_HOME/byterover/`（按配置文件作用域）
- SOC2 Type II 认证的云端同步（可选）

---

### Supermemory

语义长期记忆系统，支持资料召回、语义搜索、显式记忆工具，并通过 Supermemory 图 API 进行会话结束后的对话摄入。

| | |
|---|---|
| **适用场景** | 需要用户画像和会话级图谱构建的语义召回 |
| **要求** | `pip install supermemory` + [API 密钥](https://supermemory.ai) |
| **数据存储** | Supermemory 云端 |
| **成本** | Supermemory 定价 |

**Tools:** `supermemory_store` (保存显式记忆), `supermemory_search` (语义相似度搜索), `supermemory_forget` (按 ID 或最佳匹配查询删除), `supermemory_profile` (持久化资料 + 最近上下文)

**设置:**
```bash
hermes memory setup    # 选择 "supermemory"
# 或手动设置:
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

**配置:** `$HERMES_HOME/supermemory.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `container_tag` | `hermes` | 用于搜索和写入的容器标签。支持 `{identity}` 模板以实现按资料作用域的标签。 |
| `auto_recall` | `true` | 在对话轮次前注入相关记忆上下文 |
| `auto_capture` | `true` | 在每次响应后存储清理过的用户-助手对话轮次 |
| `max_recall_results` | `10` | 格式化到上下文中的最大召回条目数 |
| `profile_frequency` | `50` | 在第一轮及每 N 轮对话时包含资料事实 |
| `capture_mode` | `all` | 默认跳过微小或琐碎的对话轮次 |
| `search_mode` | `hybrid` | 搜索模式：`hybrid`、`memories` 或 `documents` |
| `api_timeout` | `5.0` | SDK 和摄入请求的超时时间 |

**环境变量:** `SUPERMEMORY_API_KEY` (必需), `SUPERMEMORY_CONTAINER_TAG` (覆盖配置)。

**关键特性:**
- 自动上下文隔离 — 从捕获的对话轮次中剥离已召回的记忆，防止递归记忆污染
- 会话结束后的对话摄入，用于构建更丰富的图谱级知识
- 在第一轮及可配置的间隔注入资料事实
- 琐碎消息过滤（跳过“好的”、“谢谢”等）
- **资料作用域容器** — 在 `container_tag` 中使用 `{identity}`（例如 `hermes-{identity}` → `hermes-coder`）以隔离每个 Hermes 配置文件的记忆
- **多容器模式** — 启用 `enable_custom_container_tags` 并配合 `custom_containers` 列表，允许 Agent 在命名容器之间进行读写。自动操作（同步、预取）仍保留在主容器上。
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

## 提供商对比

| 提供商 | 存储方式 | 费用 | 工具数量 | 依赖项 | 独特功能 |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | 云端 | 付费 | 4 | `honcho-ai` | 辩证用户建模 |
| **OpenViking** | 自托管 | 免费 | 5 | `openviking` + 服务器 | 文件系统层级 + 分层加载 |
| **Mem0** | 云端 | 付费 | 3 | `mem0ai` | 服务端 LLM 提取 |
| **Hindsight** | 云端/本地 | 免费/付费 | 3 | `hindsight-client` | 知识图谱 + 反思综合 |
| **Holographic** | 本地 | 免费 | 2 | 无 | HRR 代数 + 信任评分 |
| **RetainDB** | 云端 | $20/月 | 5 | `requests` | 增量压缩 |
| **ByteRover** | 本地/云端 | 免费/付费 | 3 | `brv` CLI | 预压缩提取 |
| **Supermemory** | 云端 | 付费 | 4 | `supermemory` | 上下文隔离 + 会话图谱摄入 + 多容器 |

## 配置文件隔离

每个提供商的数据都会按 [profile](/user-guide/profiles) 进行隔离：

- **本地存储提供商**（Holographic, ByteRover）使用 `$HERMES_HOME/` 路径，该路径在不同 profile 下各不相同
- **配置文件提供商**（Honcho, Mem0, Hindsight, Supermemory）将配置存储在 `$HERMES_HOME/` 中，因此每个 profile 都有各自的凭据
- **云端提供商**（RetainDB）会自动派生出 profile 作用域的项目名称
- **环境变量提供商**（OpenViking）通过每个 profile 的 `.env` 文件进行配置

## 构建 Memory Provider

请参阅 [开发者指南：Memory Provider 插件](/developer-guide/memory-provider-plugin) 以了解如何创建你自己的插件。
