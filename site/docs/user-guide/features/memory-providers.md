---
sidebar_position: 4
title: "Memory Providers"
description: "外部 Memory Provider 插件 — Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory"
---

# Memory Providers

Hermes Agent 内置了 8 个外部 Memory Provider 插件，除了内置的 MEMORY.md 和 USER.md 之外，这些插件还能为 Agent 提供持久的、跨会话的知识。同一时间只能激活 **一个** 外部 Provider —— 内置 Memory 则始终与其并行保持激活状态。

## 快速开始

```bash
hermes memory setup      # 交互式选择 + 配置
hermes memory status     # 检查当前激活项
hermes memory off        # 禁用外部 Provider
```

或者在 `~/.hermes/config.yaml` 中手动设置：

```yaml
memory:
  provider: openviking   # 或 honcho, mem0, hindsight, holographic, retaindb, byterover, supermemory
```

## 工作原理

当一个 Memory Provider 处于激活状态时，Hermes 会自动执行以下操作：

1. **注入 Provider 上下文**到系统提示词中（即 Provider 已知的知识）
2. **在每轮对话前预取相关记忆**（后台运行，非阻塞）
3. **在每次响应后同步对话轮次**到 Provider
4. **在会话结束时提取记忆**（针对支持该功能的 Provider）
5. **将内置 Memory 的写入操作镜像同步**到外部 Provider
6. **添加 Provider 专属工具**，以便 Agent 可以搜索、存储和管理记忆

内置 Memory (MEMORY.md / USER.md) 将继续像以前一样工作。外部 Provider 是作为补充增强。

## 可用 Provider

### Honcho

AI 原生的跨会话用户建模，支持辩证式问答、语义搜索和持久化结论。

| | |
|---|---|
| **最适合** | 具有跨会话上下文的多 Agent 系统、用户与 Agent 的对齐 |
| **需求** | `pip install honcho-ai` + [API key](https://app.honcho.dev) 或私有化部署实例 |
| **数据存储** | Honcho Cloud 或私有化部署 |
| **费用** | Honcho 定价 (Cloud) / 免费 (私有化部署) |

**工具：** `honcho_profile` (同行卡片), `honcho_search` (语义搜索), `honcho_context` (LLM 综合信息), `honcho_conclude` (存储事实)

**设置向导：**
```bash
hermes honcho setup        # (旧版命令) 
# 或
hermes memory setup        # 选择 "honcho"
```

**配置：** `$HERMES_HOME/honcho.json` (Profile 局部) 或 `~/.honcho/config.json` (全局)。解析优先级：`$HERMES_HOME/honcho.json` > `~/.hermes/honcho.json` > `~/.honcho/config.json`。请参阅 [配置参考](https://github.com/hermes-ai/hermes-agent/blob/main/plugins/memory/honcho/README.md) 和 [Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

<details>
<summary>关键配置选项</summary>

| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `apiKey` | -- | 来自 [app.honcho.dev](https://app.honcho.dev) 的 API key |
| `baseUrl` | -- | 私有化部署 Honcho 的基础 URL |
| `peerName` | -- | 用户 Peer 身份 |
| `aiPeer` | host key | AI Peer 身份 (每个 Profile 一个) |
| `workspace` | host key | 共享工作区 ID |
| `recallMode` | `hybrid` | `hybrid` (自动注入 + 工具), `context` (仅注入), `tools` (仅工具) |
| `observation` | 全部开启 | 每个 Peer 的 `observeMe`/`observeOthers` 布尔值 |
| `writeFrequency` | `async` | `async`, `turn`, `session`, 或整数 N |
| `sessionStrategy` | `per-directory` | `per-directory`, `per-repo`, `per-session`, `global` |
| `dialecticReasoningLevel` | `low` | `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | 根据查询长度自动提升推理等级 |
| `messageMaxChars` | `25000` | 每条消息最大字符数 (超过则分块) |

</details>

<details>
<summary>最小化 honcho.json (Cloud)</summary>

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
<summary>最小化 honcho.json (私有化部署)</summary>

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
如果你之前使用过 `hermes honcho setup`，你的配置和所有服务器端数据都是完好的。只需再次通过设置向导启用，或手动设置 `memory.provider: honcho` 即可通过新系统重新激活。
:::

**多 Agent / Profiles：**

每个 Hermes Profile 都会获得自己的 Honcho AI Peer，同时共享同一个工作区 —— 所有 Profile 都能看到相同的用户画像，但每个 Agent 都会建立自己的身份和观察。

```bash
hermes profile create coder --clone   # 创建名为 "coder" 的 Honcho Peer，继承默认配置
```

`--clone` 的作用：在 `honcho.json` 中创建一个 `hermes.coder` 主机块，设置 `aiPeer: "coder"`，共享 `workspace`，继承 `peerName`、`recallMode`、`writeFrequency`、`observation` 等。该 Peer 会在 Honcho 中预先创建，以便在发送第一条消息前就已存在。

对于在设置 Honcho 之前创建的 Profile：

```bash
hermes honcho sync   # 扫描所有 Profile，为缺失的 Profile 创建主机块
```

这将继承默认 `hermes` 主机块的设置，并为每个 Profile 创建新的 AI Peer。该操作是幂等的 —— 会跳过已经拥有主机块的 Profile。

<details>
<summary>完整 honcho.json 示例 (多 Profile)</summary>

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

由火山引擎 (字节跳动) 提供的上下文数据库，具有文件系统式的知识层级、分层检索以及自动将记忆提取为 6 个类别。

| | |
|---|---|
| **最适合** | 具有结构化浏览功能的私有化知识管理 |
| **需求** | `pip install openviking` + 运行中的服务器 |
| **数据存储** | 私有化部署 (本地或云端) |
| **费用** | 免费 (开源, AGPL-3.0) |

**工具：** `viking_search` (语义搜索), `viking_read` (分层：摘要/概览/全文), `viking_browse` (文件系统导航), `viking_remember` (存储事实), `viking_add_resource` (摄取 URL/文档)

**设置：**
```bash
# 先启动 OpenViking 服务器
pip install openviking
openviking-server

# 然后配置 Hermes
hermes memory setup    # 选择 "openviking"
# 或手动设置：
hermes config set memory.provider openviking
echo "OPENVIKING_ENDPOINT=http://localhost:1933" >> ~/.hermes/.env
```

**核心特性：**
- 分层上下文加载：L0 (~100 tokens) → L1 (~2k) → L2 (全文)
- 会话提交时自动提取记忆 (Profile、偏好、实体、事件、案例、模式)
- 用于层级知识浏览的 `viking://` URI 方案

---

### Mem0

服务器端 LLM 事实提取，支持语义搜索、重排序和自动去重。

| | |
|---|---|
| **最适合** | 无需干预的记忆管理 —— Mem0 会自动处理提取 |
| **需求** | `pip install mem0ai` + API key |
| **数据存储** | Mem0 Cloud |
| **费用** | Mem0 定价 |
**Tools:** `mem0_profile` (所有存储的记忆), `mem0_search` (语义搜索 + 重排序), `mem0_conclude` (存储逐字事实)

**安装设置:**
```bash
hermes memory setup    # 选择 "mem0"
# 或者手动设置:
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

**配置:** `$HERMES_HOME/mem0.json`

| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `user_id` | `hermes-user` | 用户标识符 |
| `agent_id` | `hermes` | Agent 标识符 |

---

### Hindsight

具备知识图谱、实体解析和多策略检索能力的长期记忆。`hindsight_reflect` 工具提供了其他 Provider 无法提供的跨记忆综合分析能力。

| | |
|---|---|
| **最适合** | 基于知识图谱和实体关系的记忆回溯 |
| **依赖项** | 云端：`pip install hindsight-client` + API 密钥。本地：`pip install hindsight` + LLM 密钥 |
| **数据存储** | Hindsight 云端或本地嵌入式 PostgreSQL |
| **费用** | Hindsight 定价（云端）或免费（本地） |

**Tools:** `hindsight_retain` (带实体提取的存储), `hindsight_recall` (多策略搜索), `hindsight_reflect` (跨记忆综合分析)

**安装设置:**
```bash
hermes memory setup    # 选择 "hindsight"
# 或者手动设置:
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

**配置:** `$HERMES_HOME/hindsight/config.json`

| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `mode` | `cloud` | `cloud` (云端) 或 `local` (本地) |
| `bank_id` | `hermes` | 记忆库标识符 |
| `budget` | `mid` | 回溯彻底程度：`low` / `mid` / `high` |

---

### Holographic

本地 SQLite 事实存储，支持 FTS5 全文搜索、信任评分，以及用于组合代数查询的 HRR (Holographic Reduced Representations)。

| | |
|---|---|
| **最适合** | 纯本地记忆，需要高级检索且无外部依赖 |
| **依赖项** | 无（SQLite 始终可用）。NumPy 可选，用于 HRR 代数运算。 |
| **数据存储** | 本地 SQLite |
| **费用** | 免费 |

**Tools:** `fact_store` (9 种操作：add, search, probe, related, reason, contradict, update, remove, list), `fact_feedback` (有用/无用评分，用于训练信任分数)

**安装设置:**
```bash
hermes memory setup    # 选择 "holographic"
# 或者手动设置:
hermes config set memory.provider holographic
```

**配置:** `plugins.hermes-memory-store` 下的 `config.yaml`

| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite 数据库路径 |
| `auto_extract` | `false` | 会话结束时自动提取事实 |
| `default_trust` | `0.5` | 默认信任分数 (0.0–1.0) |

**独特能力:**
- `probe` — 针对特定实体的代数回溯（关于某人/某事的所有事实）
- `reason` — 跨多个实体的组合 AND 查询
- `contradict` — 自动检测冲突的事实
- 信任评分系统，采用非对称反馈（+0.05 有用 / -0.10 无用）

---

### RetainDB

云端记忆 API，支持混合搜索（向量 + BM25 + 重排序）、7 种记忆类型和增量压缩。

| | |
|---|---|
| **最适合** | 已经在使用 RetainDB 基础设施的团队 |
| **依赖项** | RetainDB 账号 + API 密钥 |
| **数据存储** | RetainDB 云端 |
| **费用** | $20/月 |

**Tools:** `retaindb_profile` (用户画像), `retaindb_search` (语义搜索), `retaindb_context` (任务相关上下文), `retaindb_remember` (带类型和重要性的存储), `retaindb_forget` (删除记忆)

**安装设置:**
```bash
hermes memory setup    # 选择 "retaindb"
# 或者手动设置:
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```

---

### ByteRover

通过 `brv` CLI 实现的持久化记忆 —— 具有分层检索（模糊文本 → LLM 驱动搜索）的层级化知识树。本地优先，可选云端同步。

| | |
|---|---|
| **最适合** | 想要通过 CLI 管理便携、本地优先记忆的开发者 |
| **依赖项** | ByteRover CLI (`npm install -g byterover-cli` 或 [安装脚本](https://byterover.dev)) |
| **数据存储** | 本地（默认）或 ByteRover 云端（可选同步） |
| **费用** | 免费（本地）或 ByteRover 定价（云端） |

**Tools:** `brv_query` (搜索知识树), `brv_curate` (存储事实/决策/模式), `brv_status` (CLI 版本 + 树统计信息)

**安装设置:**
```bash
# 先安装 CLI
curl -fsSL https://byterover.dev/install.sh | sh

# 然后配置 Hermes
hermes memory setup    # 选择 "byterover"
# 或者手动设置:
hermes config set memory.provider byterover
```

**核心特性:**
- 自动预压缩提取（在上下文压缩丢弃信息前保存洞察）
- 知识树存储在 `$HERMES_HOME/byterover/`（按 Profile 隔离）
- 通过 SOC2 Type II 认证的云端同步（可选）

---

### Supermemory

语义长期记忆，支持画像回溯、语义搜索、显式记忆工具，并通过 Supermemory 图谱 API 在会话结束时摄取对话。

| | |
|---|---|
| **最适合** | 需要用户画像和会话级图谱构建的语义回溯 |
| **依赖项** | `pip install supermemory` + [API 密钥](https://supermemory.ai) |
| **数据存储** | Supermemory 云端 |
| **费用** | Supermemory 定价 |

**Tools:** `supermemory_store` (保存显式记忆), `supermemory_search` (语义相似度搜索), `supermemory_forget` (通过 ID 或最佳匹配查询进行遗忘), `supermemory_profile` (持久化画像 + 最近上下文)

**安装设置:**
```bash
hermes memory setup    # 选择 "supermemory"
# 或者手动设置:
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

**配置:** `$HERMES_HOME/supermemory.json`

| 键名 | 默认值 | 描述 |
|-----|---------|-------------|
| `container_tag` | `hermes` | 用于搜索和写入的容器标签。支持 `{identity}` 模板以实现 Profile 隔离的标签。 |
| `auto_recall` | `true` | 在轮次开始前注入相关的记忆上下文 |
| `auto_capture` | `true` | 在每次响应后存储清理后的用户-助手对话轮次 |
| `max_recall_results` | `10` | 格式化到上下文中的最大回溯条目数 |
| `profile_frequency` | `50` | 在第一轮以及每隔 N 轮包含画像事实 |
| `capture_mode` | `all` | 默认跳过极短或琐碎的轮次 |
| `search_mode` | `hybrid` | 搜索模式：`hybrid` (混合), `memories` (记忆), 或 `documents` (文档) |
| `api_timeout` | `5.0` | SDK 和摄取请求的超时时间 |

**环境变量:** `SUPERMEMORY_API_KEY` (必填), `SUPERMEMORY_CONTAINER_TAG` (覆盖配置)。

**核心特性:**
- 自动上下文隔离 (Context fencing) —— 从捕获的轮次中剥离回溯的记忆，防止递归记忆污染
- 会话结束对话摄取，用于构建更丰富的图谱级知识
- 在第一轮和可配置的间隔注入画像事实
- 琐碎消息过滤（跳过 "ok", "thanks" 等）
- **Profile 隔离容器** —— 在 `container_tag` 中使用 `{identity}`（例如 `hermes-{identity}` → `hermes-coder`）来隔离每个 Hermes Profile 的记忆
- **多容器模式** —— 启用 `enable_custom_container_tags` 并设置 `custom_containers` 列表，允许 Agent 在多个命名容器间进行读写。自动操作（同步、预取）仍保留在主容器中。

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

## Provider 对比

| Provider | 存储方式 | 费用 | 工具数量 | 依赖项 | 独特功能 |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | 云端 | 付费 | 4 | `honcho-ai` | 辩证用户建模 |
| **OpenViking** | 自托管 | 免费 | 5 | `openviking` + server | 文件系统层级 + 分层加载 |
| **Mem0** | 云端 | 付费 | 3 | `mem0ai` | 服务端 LLM 提取 |
| **Hindsight** | 云端/本地 | 免费/付费 | 3 | `hindsight-client` | 知识图谱 + 反思综合 |
| **Holographic** | 本地 | 免费 | 2 | 无 | HRR 代数 + 信任评分 |
| **RetainDB** | 云端 | $20/月 | 5 | `requests` | 增量压缩 |
| **ByteRover** | 本地/云端 | 免费/付费 | 3 | `brv` CLI | 预压缩提取 |
| **Supermemory** | 云端 | 付费 | 4 | `supermemory` | 上下文隔离 + 会话图谱摄取 + 多容器 |
## Profile 隔离

每个 Provider 的数据都按 [Profile](/user-guide/profiles) 进行隔离：

- **本地存储 Provider** (Holographic, ByteRover) 使用 `$HERMES_HOME/` 路径，该路径随 Profile 的不同而变化
- **配置文件 Provider** (Honcho, Mem0, Hindsight, Supermemory) 将配置存储在 `$HERMES_HOME/` 中，因此每个 Profile 都有自己的凭据
- **云端 Provider** (RetainDB) 会自动派生 Profile 作用域的项目名称
- **环境变量 Provider** (OpenViking) 通过每个 Profile 的 `.env` 文件进行配置

## 构建 Memory Provider

请参阅 [开发者指南：Memory Provider 插件](/developer-guide/memory-provider-plugin) 了解如何创建你自己的 Provider。
