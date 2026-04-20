# Session Storage {#session-storage}

Hermes Agent 使用 SQLite 数据库 (`~/.hermes/state.db`) 来持久化存储跨 CLI 和 gateway 会话的 Session 元数据、完整消息历史以及模型配置。这取代了早期每个 Session 使用独立 JSONL 文件的方法。

源文件：`hermes_state.py`


## 架构概览 {#architecture-overview}

```
~/.hermes/state.db (SQLite, WAL 模式)
├── sessions          — Session 元数据、Token 计数、计费信息
├── messages          — 每个 Session 的完整消息历史
├── messages_fts      — 用于全文搜索的 FTS5 虚拟表
└── schema_version    — 记录迁移状态的单行表
```

关键设计决策：
- **WAL 模式**：支持并发读取 + 单个写入者（适用于 gateway 多平台场景）。
- **FTS5 虚拟表**：用于在所有 Session 消息中进行快速文本搜索。
- **Session 血缘**：通过 `parent_session_id` 链条实现（由压缩触发的分片）。
- **来源标记**（`cli`、`telegram`、`discord` 等）：用于平台过滤。
- Batch runner 和 RL 轨迹**不**存储在这里（由独立系统处理）。


## SQLite Schema {#sqlite-schema}

### Sessions 表 {#sessions-table}

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    user_id TEXT,
    model TEXT,
    model_config TEXT,
    system_prompt TEXT,
    parent_session_id TEXT,
    started_at REAL NOT NULL,
    ended_at REAL,
    end_reason TEXT,
    message_count INTEGER DEFAULT 0,
    tool_call_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_write_tokens INTEGER DEFAULT 0,
    reasoning_tokens INTEGER DEFAULT 0,
    billing_provider TEXT,
    billing_base_url TEXT,
    billing_mode TEXT,
    estimated_cost_usd REAL,
    actual_cost_usd REAL,
    cost_status TEXT,
    cost_source TEXT,
    pricing_version TEXT,
    title TEXT,
    FOREIGN KEY (parent_session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_source ON sessions(source);
CREATE INDEX IF NOT EXISTS idx_sessions_parent ON sessions(parent_session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_title_unique
    ON sessions(title) WHERE title IS NOT NULL;
```

### Messages 表 {#messages-table}

```sql
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    role TEXT NOT NULL,
    content TEXT,
    tool_call_id TEXT,
    tool_calls TEXT,
    tool_name TEXT,
    timestamp REAL NOT NULL,
    token_count INTEGER,
    finish_reason TEXT,
    reasoning TEXT,
    reasoning_details TEXT,
    codex_reasoning_items TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, timestamp);
```

说明：
- `tool_calls` 以 JSON 字符串形式存储（序列化的 tool call 对象列表）。
- `reasoning_details` 和 `codex_reasoning_items` 以 JSON 字符串形式存储。
- `reasoning` 存储那些暴露了原始推理文本的提供商所返回的内容。
- 时间戳使用 Unix epoch 浮点数 (`time.time()`)。

### FTS5 全文搜索 {#fts5-full-text-search}

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content,
    content=messages,
    content_rowid=id
);
```

FTS5 表通过三个触发器保持同步，这些触发器在 `messages` 表发生 INSERT、UPDATE 和 DELETE 时触发：

```sql
CREATE TRIGGER IF NOT EXISTS messages_fts_insert AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_fts_delete AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content)
        VALUES('delete', old.id, old.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_fts_update AFTER UPDATE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content)
        VALUES('delete', old.id, old.content);
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;
```


## Schema 版本与迁移 {#schema-version-and-migrations}

当前 Schema 版本：**6**

`schema_version` 表存储一个整数。在初始化时，`_init_schema()` 会检查当前版本并按顺序执行迁移：

| 版本 | 变更内容 |
|---------|--------|
| 1 | 初始 Schema（sessions, messages, FTS5） |
| 2 | 在 messages 表中添加 `finish_reason` 列 |
| 3 | 在 sessions 表中添加 `title` 列 |
| 4 | 在 `title` 上添加唯一索引（允许 NULL，非 NULL 必须唯一） |
| 5 | 添加计费相关列：`cache_read_tokens`, `cache_write_tokens`, `reasoning_tokens`, `billing_provider`, `billing_base_url`, `billing_mode`, `estimated_cost_usd`, `actual_cost_usd`, `cost_status`, `cost_source`, `pricing_version` |
| 6 | 在 messages 表中添加推理相关列：`reasoning`, `reasoning_details`, `codex_reasoning_items` |

每次迁移都使用包裹在 try/except 中的 `ALTER TABLE ADD COLUMN` 来处理“列已存在”的情况（幂等性）。每个迁移块成功执行后，版本号都会递增。


## 写入竞争处理 {#write-contention-handling}

多个 hermes 进程（gateway + CLI 会话 + worktree Agents）共享同一个 `state.db`。`SessionDB` 类通过以下方式处理写入竞争：

- **短 SQLite 超时**：使用 1 秒超时，而非默认的 30 秒。
- **应用层重试**：带有随机抖动（Jitter）的重试机制（20-150ms，最多重试 15 次）。
- **BEGIN IMMEDIATE 事务**：在事务开始时就暴露锁竞争。
- **定期 WAL 检查点**：每 50 次成功写入执行一次（PASSIVE 模式）。

这避免了“车队效应”（convoy effect），即 SQLite 确定性的内部退避机制导致所有竞争的写入者在相同的间隔进行重试。

```
_WRITE_MAX_RETRIES = 15
_WRITE_RETRY_MIN_S = 0.020   # 20ms
_WRITE_RETRY_MAX_S = 0.150   # 150ms
_CHECKPOINT_EVERY_N_WRITES = 50
```


## 常用操作 {#common-operations}

### 初始化 {#initialize}

```python
from hermes_state import SessionDB

db = SessionDB()                           # 默认路径：~/.hermes/state.db
db = SessionDB(db_path=Path("/tmp/test.db"))  # 自定义路径
```

### 创建与管理 Session {#create-and-manage-sessions}

```python
# 创建一个新 Session
db.create_session(
    session_id="sess_abc123",
    source="cli",
    model="anthropic/claude-sonnet-4.6",
    user_id="user_1",
    parent_session_id=None,  # 或者传入前一个 Session ID 以建立血缘关系
)

# 结束一个 Session
db.end_session("sess_abc123", end_reason="user_exit")

# 重新开启一个 Session (清除 ended_at/end_reason)
db.reopen_session("sess_abc123")
```

### 存储消息 {#store-messages}

```python
msg_id = db.append_message(
    session_id="sess_abc123",
    role="assistant",
    content="Here's the answer...",
    tool_calls=[{"id": "call_1", "function": {"name": "terminal", "arguments": "{}"}}],
    token_count=150,
    finish_reason="stop",
    reasoning="Let me think about this...",
)
```

### 获取消息 {#retrieve-messages}

```python
# 获取包含所有元数据的原始消息
messages = db.get_messages("sess_abc123")

# 获取 OpenAI 对话格式（用于 API 回放）
conversation = db.get_messages_as_conversation("sess_abc123")
# 返回：[{"role": "user", "content": "..."}, {"role": "assistant", ...}]
```

### Session 标题 {#session-titles}

```python
# 设置标题（在非 NULL 标题中必须唯一）
db.set_session_title("sess_abc123", "Fix Docker Build")

# 通过标题解析（返回血缘关系中最晚的一个）
session_id = db.resolve_session_by_title("Fix Docker Build")

# 自动生成血缘中的下一个标题
next_title = db.get_next_title_in_lineage("Fix Docker Build")
# 返回："Fix Docker Build #2"
```


## 全文搜索 {#full-text-search}

`search_messages()` 方法支持 FTS5 查询语法，并会自动对用户输入进行清理。

### 基础搜索 {#basic-search}

```python
results = db.search_messages("docker deployment")
```

### FTS5 查询语法 {#fts5-query-syntax}

| 语法 | 示例 | 含义 |
|--------|---------|---------|
| 关键词 | `docker deployment` | 包含两个词（隐式 AND） |
| 引号短语 | `"exact phrase"` | 精确短语匹配 |
| 布尔 OR | `docker OR kubernetes` | 包含其中任一词 |
| 布尔 NOT | `python NOT java` | 排除特定词 |
| 前缀 | `deploy*` | 前缀匹配 |

### 过滤搜索 {#filtered-search}

```python
# 仅搜索 CLI 会话
results = db.search_messages("error", source_filter=["cli"])

# 排除 gateway 会话
results = db.search_messages("bug", exclude_sources=["telegram", "discord"])

# 仅搜索用户消息
results = db.search_messages("help", role_filter=["user"])
```
### 搜索结果格式 {#search-results-format}

每个结果包含：
- `id`, `session_id`, `role`, `timestamp`
- `snippet` — 由 FTS5 生成的片段，带有 `>>>match<<<` 标记
- `context` — 匹配项前后各 1 条消息（内容截断至 200 字符）
- `source`, `model`, `session_started` — 来自父级 Session

`_sanitize_fts5_query()` 方法处理边缘情况：
- 去除未闭合的引号和特殊字符
- 将带连字符的术语用引号包裹（`chat-send` → `"chat-send"`）
- 移除悬空的布尔运算符（`hello AND` → `hello`）


## Session 血缘关系 (Lineage) {#session-lineage}

Session 可以通过 `parent_session_id` 形成链条。这通常发生在网关触发上下文压缩并导致 Session 拆分时。

### 查询：查找 Session 血缘 {#query-find-session-lineage}

```sql
-- 查找一个 Session 的所有祖先
WITH RECURSIVE lineage AS (
    SELECT * FROM sessions WHERE id = ?
    UNION ALL
    SELECT s.* FROM sessions s
    JOIN lineage l ON s.id = l.parent_session_id
)
SELECT id, title, started_at, parent_session_id FROM lineage;

-- 查找一个 Session 的所有后代
WITH RECURSIVE descendants AS (
    SELECT * FROM sessions WHERE id = ?
    UNION ALL
    SELECT s.* FROM sessions s
    JOIN descendants d ON s.parent_session_id = d.id
)
SELECT id, title, started_at FROM descendants;
```

### 查询：带有预览的最近 Session {#query-recent-sessions-with-preview}

```sql
SELECT s.*,
    COALESCE(
        (SELECT SUBSTR(m.content, 1, 63)
         FROM messages m
         WHERE m.session_id = s.id AND m.role = 'user' AND m.content IS NOT NULL
         ORDER BY m.timestamp, m.id LIMIT 1),
        ''
    ) AS preview,
    COALESCE(
        (SELECT MAX(m2.timestamp) FROM messages m2 WHERE m2.session_id = s.id),
        s.started_at
    ) AS last_active
FROM sessions s
ORDER BY s.started_at DESC
LIMIT 20;
```

### 查询：Token 使用统计 {#query-token-usage-statistics}

```sql
-- 按模型统计总 Token
SELECT model,
       COUNT(*) as session_count,
       SUM(input_tokens) as total_input,
       SUM(output_tokens) as total_output,
       SUM(estimated_cost_usd) as total_cost
FROM sessions
WHERE model IS NOT NULL
GROUP BY model
ORDER BY total_cost DESC;

-- Token 使用量最高的 Session
SELECT id, title, model, input_tokens + output_tokens AS total_tokens,
       estimated_cost_usd
FROM sessions
ORDER BY total_tokens DESC
LIMIT 10;
```


## 导出与清理 {#export-and-cleanup}

```python
# 导出单个 Session 及其消息
data = db.export_session("sess_abc123")

# 将所有 Session（含消息）导出为字典列表
all_data = db.export_all(source="cli")

# 删除旧 Session（仅限已结束的 Session）
deleted_count = db.prune_sessions(older_than_days=90)
deleted_count = db.prune_sessions(older_than_days=30, source="telegram")

# 清空消息但保留 Session 记录
db.clear_messages("sess_abc123")

# 删除 Session 及其所有消息
db.delete_session("sess_abc123")
```


## 数据库位置 {#database-location}

默认路径：`~/.hermes/state.db`

该路径派生自 `hermes_constants.get_hermes_home()`，默认解析为 `~/.hermes/`，或环境变量 `HERMES_HOME` 的值。

数据库文件、WAL 文件 (`state.db-wal`) 和共享内存文件 (`state.db-shm`) 均在同一目录下创建。
