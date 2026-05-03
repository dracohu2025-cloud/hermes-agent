# 会话存储 {#session-storage}

Hermes Agent 使用 SQLite 数据库（`~/.hermes/state.db`）来持久化会话元数据、完整消息历史以及模型配置，这些数据在 CLI 和网关会话之间共享。这取代了之前每个会话使用 JSONL 文件的方式。

源文件：`hermes_state.py`

## 架构概览 {#architecture-overview}

```
~/.hermes/state.db (SQLite, WAL 模式)
├── sessions              — 会话元数据、Token 计数、计费
├── messages              — 每个会话的完整消息历史
├── messages_fts          — FTS5 虚拟表（content + tool_name + tool_calls）
├── messages_fts_trigram  — 使用三元组分词器的 FTS5 虚拟表（支持 CJK / 子串搜索）
├── state_meta            — 键/值元数据表
└── schema_version        — 单行表，跟踪迁移状态
```

关键设计决策：
- **WAL 模式**：支持并发读取 + 一个写入（网关多平台）
- **FTS5 虚拟表**：跨所有会话消息实现快速文本搜索
- **会话谱系**：通过 `parent_session_id` 链实现（压缩触发的拆分）
- **来源标记**（`cli`、`telegram`、`discord` 等）：用于平台过滤
- 批量运行器和强化学习轨迹不存储在此处（由其他系统处理）

## SQLite 模式 {#sqlite-schema}

### 会话表 {#sessions-table}

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
    api_call_count INTEGER DEFAULT 0,
    FOREIGN KEY (parent_session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_source ON sessions(source);
CREATE INDEX IF NOT EXISTS idx_sessions_parent ON sessions(parent_session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_title_unique
    ON sessions(title) WHERE title IS NOT NULL;
```

### 消息表 {#messages-table}

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
    reasoning_content TEXT,
    reasoning_details TEXT,
    codex_reasoning_items TEXT,
    codex_message_items TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, timestamp);
```
注意：
- `tool_calls` 以 JSON 字符串形式存储（序列化的工具调用对象列表）
- `reasoning_details`、`codex_reasoning_items` 和 `codex_message_items` 以 JSON 字符串形式存储
- `reasoning` 存储原始推理文本（针对暴露该信息的提供商）
- 时间戳为 Unix 纪元浮点数（`time.time()`）

### FTS5 全文搜索 {#fts5-full-text-search}

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content,
    content=messages,
    content_rowid=id
);
```

FTS5 表通过三个触发器保持同步，这些触发器在 `messages` 表的 INSERT、UPDATE 和 DELETE 操作时触发：

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

## 模式版本与迁移 {#schema-version-and-migrations}

当前模式版本：**11**

`schema_version` 表存储一个整数。简单的列添加通过 `_reconcile_columns()` 声明式处理（该方法对比当前列与 `SCHEMA_SQL`，并添加缺失的列）。版本门控链用于无法声明式表达的数据迁移和索引/FTS 变更：

| 版本 | 变更内容 |
|------|----------|
| 1 | 初始模式（sessions、messages、FTS5） |
| 2 | 向 messages 表添加 `finish_reason` 列 |
| 3 | 向 sessions 表添加 `title` 列 |
| 4 | 在 `title` 上添加唯一索引（允许 NULL，非 NULL 必须唯一） |
| 5 | 添加计费列：`cache_read_tokens`、`cache_write_tokens`、`reasoning_tokens`、`billing_provider`、`billing_base_url`、`billing_mode`、`estimated_cost_usd`、`actual_cost_usd`、`cost_status`、`cost_source`、`pricing_version` |
| 6 | 向 messages 表添加推理列：`reasoning`、`reasoning_details`、`codex_reasoning_items` |
| 7 | 向 messages 表添加 `reasoning_content` 列 |
| 8 | 向 sessions 表添加 `api_call_count` 列 |
| 9 | 向 messages 表添加 `codex_message_items` 列，用于 Codex Responses 消息 ID/阶段重放 |
| 10 | 添加 `messages_fts_trigram` 虚拟表（支持 CJK/子串搜索的 trigram 分词器）并回填现有行 |
| 11 | 重新索引 `messages_fts` 和 `messages_fts_trigram` 以覆盖 `tool_name` + `tool_calls`，并从外部内容模式切换到内联模式；删除旧触发器并回填每一行消息 |

声明式列添加使用 `ALTER TABLE ADD COLUMN` 并包裹在 try/except 中，以处理列已存在的情况（幂等）。每次成功执行迁移块后，版本号递增。

## 写冲突处理 {#write-contention-handling}

多个 hermes 进程（网关 + CLI 会话 + worktree Agents）共享同一个 `state.db`。`SessionDB` 类通过以下方式处理写冲突：
- **短 SQLite 超时**（1 秒），而非默认的 30 秒
- **应用层重试**，带随机抖动（20-150ms，最多重试 15 次）
- **BEGIN IMMEDIATE 事务**，在事务开始时暴露锁竞争
- **定期 WAL 检查点**，每成功写入 50 次执行一次（PASSIVE 模式）

这避免了“车队效应”，即 SQLite 确定性的内部退避会导致所有竞争写入者以相同间隔重试。

```
_WRITE_MAX_RETRIES = 15
_WRITE_RETRY_MIN_S = 0.020   # 20ms
_WRITE_RETRY_MAX_S = 0.150   # 150ms
_CHECKPOINT_EVERY_N_WRITES = 50
```

## 常见操作 {#common-operations}

### 初始化 {#initialize}

```python
from hermes_state import SessionDB

db = SessionDB()                           # 默认：~/.hermes/state.db
db = SessionDB(db_path=Path("/tmp/test.db"))  # 自定义路径
```

### 创建和管理会话 {#create-and-manage-sessions}

```python
# 创建新会话
db.create_session(
    session_id="sess_abc123",
    source="cli",
    model="anthropic/claude-sonnet-4.6",
    user_id="user_1",
    parent_session_id=None,  # 或用于追踪谱系的上一会话 ID
)

# 结束会话
db.end_session("sess_abc123", end_reason="user_exit")

# 重新打开会话（清除 ended_at/end_reason）
db.reopen_session("sess_abc123")
```

### 存储消息 {#store-messages}

```python
msg_id = db.append_message(
    session_id="sess_abc123",
    role="assistant",
    content="这是答案...",
    tool_calls=[{"id": "call_1", "function": {"name": "terminal", "arguments": "{}"}}],
    token_count=150,
    finish_reason="stop",
    reasoning="让我想想...",
)
```

### 检索消息 {#retrieve-messages}

```python
# 原始消息，包含所有元数据
messages = db.get_messages("sess_abc123")

# OpenAI 对话格式（用于 API 回放）
conversation = db.get_messages_as_conversation("sess_abc123")
# 返回：[{"role": "user", "content": "..."}, {"role": "assistant", ...}]
```

### 会话标题 {#session-titles}

```python
# 设置标题（在非 NULL 标题中必须唯一）
db.set_session_title("sess_abc123", "修复 Docker 构建")

# 按标题解析（返回谱系中最近的一个）
session_id = db.resolve_session_by_title("修复 Docker 构建")

# 自动生成谱系中的下一个标题
next_title = db.get_next_title_in_lineage("修复 Docker 构建")
# 返回："修复 Docker 构建 #2"
```

## 全文搜索 {#full-text-search}

`search_messages()` 方法支持 FTS5 查询语法，并自动对用户输入进行清理。

### 基本搜索 {#basic-search}

```python
results = db.search_messages("docker 部署")
```

### FTS5 查询语法 {#fts5-query-syntax}

| 语法 | 示例 | 含义 |
|--------|---------|---------|
| 关键词 | `docker 部署` | 两个词都匹配（隐式 AND） |
| 引号短语 | `"精确短语"` | 精确短语匹配 |
| 布尔 OR | `docker OR kubernetes` | 任一术语匹配 |
| 布尔 NOT | `python NOT java` | 排除术语 |
| 前缀 | `deploy*` | 前缀匹配 |

### 过滤搜索 {#filtered-search}

```python
# 仅搜索 CLI 会话
results = db.search_messages("错误", source_filter=["cli"])

# 排除 gateway 会话
results = db.search_messages("bug", exclude_sources=["telegram", "discord"])

# 仅搜索用户消息
results = db.search_messages("帮助", role_filter=["user"])
```
### 搜索结果格式 {#search-results-format}

每条结果包含：
- `id`、`session_id`、`role`、`timestamp`
- `snippet` — FTS5 生成的片段，带有 `>>>match<<<` 标记
- `context` — 匹配结果前后各 1 条消息（内容截断至 200 字符）
- `source`、`model`、`session_started` — 来自父级会话

`_sanitize_fts5_query()` 方法处理以下边界情况：
- 去除不匹配的引号和特殊字符
- 将带连字符的术语用引号包裹（`chat-send` → `"chat-send"`）
- 移除悬空的布尔运算符（`hello AND` → `hello`）

## 会话谱系 {#session-lineage}

会话可以通过 `parent_session_id` 形成链式结构。当网关中的上下文压缩触发会话拆分时，就会发生这种情况。

### 查询：查找会话谱系 {#query-find-session-lineage}

```sql
-- 查找某个会话的所有祖先
WITH RECURSIVE lineage AS (
    SELECT * FROM sessions WHERE id = ?
    UNION ALL
    SELECT s.* FROM sessions s
    JOIN lineage l ON s.id = l.parent_session_id
)
SELECT id, title, started_at, parent_session_id FROM lineage;

-- 查找某个会话的所有后代
WITH RECURSIVE descendants AS (
    SELECT * FROM sessions WHERE id = ?
    UNION ALL
    SELECT s.* FROM sessions s
    JOIN descendants d ON s.parent_session_id = d.id
)
SELECT id, title, started_at FROM descendants;
```

### 查询：带预览的最近会话 {#query-recent-sessions-with-preview}

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

### 查询：Token 用量统计 {#query-token-usage-statistics}

```sql
-- 按模型统计总 token 数
SELECT model,
       COUNT(*) as session_count,
       SUM(input_tokens) as total_input,
       SUM(output_tokens) as total_output,
       SUM(estimated_cost_usd) as total_cost
FROM sessions
WHERE model IS NOT NULL
GROUP BY model
ORDER BY total_cost DESC;

-- token 用量最高的会话
SELECT id, title, model, input_tokens + output_tokens AS total_tokens,
       estimated_cost_usd
FROM sessions
ORDER BY total_tokens DESC
LIMIT 10;
```

## 导出与清理 {#export-and-cleanup}

```python
# 导出单个会话及其消息
data = db.export_session("sess_abc123")

# 导出所有会话（含消息）为字典列表
all_data = db.export_all(source="cli")

# 删除旧会话（仅已结束的会话）
deleted_count = db.prune_sessions(older_than_days=90)
deleted_count = db.prune_sessions(older_than_days=30, source="telegram")

# 清除消息但保留会话记录
db.clear_messages("sess_abc123")

# 删除会话及其所有消息
db.delete_session("sess_abc123")
```

## 数据库位置 {#database-location}

默认路径：`~/.hermes/state.db`

该路径由 `hermes_constants.get_hermes_home()` 解析得出，默认解析为 `~/.hermes/`，或使用 `HERMES_HOME` 环境变量的值。
数据库文件、WAL 文件（`state.db-wal`）和共享内存文件（`state.db-shm`）都创建在同一个目录中。
