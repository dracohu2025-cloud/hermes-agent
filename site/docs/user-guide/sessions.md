---
sidebar_position: 7
title: "会话"
description: "会话持久化、恢复、搜索、管理以及按平台追踪会话"
---

# 会话 {#sessions}

Hermes Agent 会自动将每次对话保存为一个会话。会话支持对话恢复、跨会话搜索以及完整的对话历史管理。

## 会话如何工作 {#how-sessions-work}

每次对话——无论是来自 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix 还是其他任何消息平台——都会作为包含完整消息历史的会话存储。会话通过两个互补的系统进行追踪：

1. **SQLite 数据库**（`~/.hermes/state.db`）——结构化的会话元数据，支持 FTS5 全文搜索
2. **JSONL 转录文件**（`~/.hermes/sessions/`）——原始对话转录，包括工具调用（网关）

SQLite 数据库存储：
- 会话 ID、来源平台、用户 ID
- **会话标题**（唯一的、人类可读的名称）
- 模型名称和配置
- 系统提示快照
- 完整消息历史（角色、内容、工具调用、工具结果）
- Token 计数（输入/输出）
- 时间戳（开始时间、结束时间）
- 父会话 ID（用于压缩触发的会话拆分）

### 会话来源 {#session-sources}

每个会话都会标记其来源平台：

| 来源 | 描述 |
|--------|-------------|
| `cli` | 交互式 CLI（`hermes` 或 `hermes chat`） |
| `telegram` | Telegram 即时通讯 |
| `discord` | Discord 服务器/私信 |
| `slack` | Slack 工作区 |
| `whatsapp` | WhatsApp 即时通讯 |
| `signal` | Signal 即时通讯 |
| `matrix` | Matrix 房间和私信 |
| `mattermost` | Mattermost 频道 |
| `email` | 电子邮件（IMAP/SMTP） |
| `sms` | 通过 Twilio 发送的短信 |
| `dingtalk` | 钉钉即时通讯 |
| `feishu` | 飞书/Lark 即时通讯 |
| `wecom` | 企业微信 |
| `weixin` | 微信（个人版） |
| `bluebubbles` | 通过 BlueBubbles macOS 服务器的 Apple iMessage |
| `qqbot` | QQ 机器人（腾讯 QQ）通过官方 API v2 |
| `homeassistant` | Home Assistant 对话 |
| `webhook` | 传入的 Webhook |
| `api-server` | API 服务器请求 |
| `acp` | ACP 编辑器集成 |
| `cron` | 定时 Cron 任务 |
| `batch` | 批量处理运行 |

## CLI 会话恢复 {#cli-session-resume}

使用 `--continue` 或 `--resume` 从 CLI 恢复之前的对话：

### 继续上次会话 {#continue-last-session}

```bash
# 恢复最近的 CLI 会话
hermes --continue
hermes -c

# 或者使用 chat 子命令
hermes chat --continue
hermes chat -c
```

这会从 SQLite 数据库中查找最近的 `cli` 会话，并加载其完整的对话历史。

### 按名称恢复 {#resume-by-name}

如果你给会话设置了标题（参见下方的[会话命名](#session-naming)），可以按名称恢复：

```bash
# 恢复一个已命名的会话
hermes -c "my project"

# 如果存在变体（my project、my project #2、my project #3），
# 这会自动恢复最近的一个
hermes -c "my project"   # → 恢复 "my project #3"
```

### 恢复特定会话 {#resume-specific-session}

```bash
# 按 ID 恢复特定会话
hermes --resume 20250305_091523_a1b2c3d4
hermes -r 20250305_091523_a1b2c3d4

# 按标题恢复
hermes --resume "refactoring auth"

# 或者使用 chat 子命令
hermes chat --resume 20250305_091523_a1b2c3d4
```
Session IDs are shown when you exit a CLI session, and can be found with `hermes sessions list`.

### Conversation Recap on Resume {#conversation-recap-on-resume}

When you resume a session, Hermes displays a compact recap of the previous conversation in a styled panel before the input prompt:

<img className="docs-terminal-figure" src="/img/docs/session-recap.svg" alt="Stylized preview of the Previous Conversation recap panel shown when resuming a Hermes session." />
<p className="docs-figure-caption">Resume mode shows a compact recap panel with recent user and assistant turns before returning you to the live prompt.</p>

The recap:
- Shows **user messages** (gold `●`) and **assistant responses** (green `◆`)
- **Truncates** long messages (300 chars for user, 200 chars / 3 lines for assistant)
- **Collapses tool calls** to a count with tool names (e.g., `[3 tool calls: terminal, web_search]`)
- **Hides** system messages, tool results, and internal reasoning
- **Caps** at the last 10 exchanges with a "... N earlier messages ..." indicator
- Uses **dim styling** to distinguish from the active conversation

To disable the recap and keep the minimal one-liner behavior, set in `~/.hermes/config.yaml`:

```yaml
display:
  resume_display: minimal   # default: full
```

:::tip
Session IDs follow the format `YYYYMMDD_HHMMSS_&lt;hex&gt;` — CLI/TUI sessions use a 6-char hex suffix (e.g. `20250305_091523_a1b2c3`), gateway sessions use an 8-char suffix (e.g. `20250305_091523_a1b2c3d4`). You can resume by ID (full or unique prefix) or by title — both work with `-c` and `-r`.
:::

## Session Naming {#session-naming}

Give sessions human-readable titles so you can find and resume them easily.

### Auto-Generated Titles {#auto-generated-titles}

Hermes automatically generates a short descriptive title (3–7 words) for each session after the first exchange. This runs in a background thread using a fast auxiliary model, so it adds no latency. You'll see auto-generated titles when browsing sessions with `hermes sessions list` or `hermes sessions browse`.

Auto-titling only fires once per session and is skipped if you've already set a title manually.

### Setting a Title Manually {#setting-a-title-manually}

Use the `/title` slash command inside any chat session (CLI or gateway):

```
/title my research project
```

The title is applied immediately. If the session hasn't been created in the database yet (e.g., you run `/title` before sending your first message), it's queued and applied once the session starts.

You can also rename existing sessions from the command line:

```bash
hermes sessions rename 20250305_091523_a1b2c3d4 "refactoring auth module"
```

### Title Rules {#title-rules}

- **Unique** — no two sessions can share the same title
- **Max 100 characters** — keeps listing output clean
- **Sanitized** — control characters, zero-width chars, and RTL overrides are stripped automatically
- **Normal Unicode is fine** — emoji, CJK, accented characters all work

### Auto-Lineage on Compression {#auto-lineage-on-compression}

When a session's context is compressed (manually via `/compress` or automatically), Hermes creates a new continuation session. If the original had a title, the new session automatically gets a numbered title:

--- END DOCUMENT CHUNK ---
```
"my project" → "my project #2" → "my project #3"
```

当你按名称恢复会话时（`hermes -c "my project"`），它会自动选择该会话链中最新的一个。

### 消息平台中的 /title 命令 {#title-in-messaging-platforms}

`/title` 命令在所有网关平台（Telegram、Discord、Slack、WhatsApp）中均可使用：

- `/title My Research` — 设置会话标题
- `/title` — 显示当前标题

## 会话管理命令 {#session-management-commands}

Hermes 通过 `hermes sessions` 提供了一整套会话管理命令：

### 列出会话 {#list-sessions}

```bash
# 列出最近的会话（默认：最近 20 个）
hermes sessions list

# 按平台过滤
hermes sessions list --source telegram

# 显示更多会话
hermes sessions list --limit 50
```

当会话有标题时，输出会显示标题、预览和相对时间戳：

```
标题                   预览                                    最后活跃时间  ID
────────────────────────────────────────────────────────────────────────────────────────────────
重构认证模块           请帮我重构认证模块                          2小时前      20250305_091523_a
我的项目 #3            你能检查一下测试失败的原因吗？              昨天         20250304_143022_e
—                      拉斯维加斯天气怎么样？                      3天前        20250303_101500_f
```

当会话没有标题时，会使用更简洁的格式：

```
预览                                           最后活跃时间  来源   ID
──────────────────────────────────────────────────────────────────────────────────────
请帮我重构认证模块                               2小时前       cli    20250305_091523_a
拉斯维加斯天气怎么样？                            3天前        tele   20250303_101500_f
```

### 导出会话 {#export-sessions}

```bash
# 将所有会话导出到 JSONL 文件
hermes sessions export backup.jsonl

# 导出特定平台的会话
hermes sessions export telegram-history.jsonl --source telegram

# 导出单个会话
hermes sessions export session.jsonl --session-id 20250305_091523_a1b2c3d4
```

导出的文件中每行包含一个 JSON 对象，包含完整的会话元数据和所有消息。

### 删除会话 {#delete-a-session}

```bash
# 删除特定会话（需要确认）
hermes sessions delete 20250305_091523_a1b2c3d4

# 无需确认直接删除
hermes sessions delete 20250305_091523_a1b2c3d4 --yes
```

### 重命名会话 {#rename-a-session}

```bash
# 设置或更改会话标题
hermes sessions rename 20250305_091523_a1b2c3d4 "调试认证流程"

# 多词标题在 CLI 中不需要引号
hermes sessions rename 20250305_091523_a1b2c3d4 调试认证流程
```

如果该标题已被其他会话使用，则会显示错误。

### 清理旧会话 {#prune-old-sessions}

```bash
# 删除超过 90 天（默认）的已结束会话
hermes sessions prune

# 自定义时间阈值
hermes sessions prune --older-than 30

# 仅清理特定平台的会话
hermes sessions prune --source telegram --older-than 60

# 跳过确认
hermes sessions prune --older-than 30 --yes
```

:::info
清理仅删除**已结束**的会话（即已明确结束或自动重置的会话）。活跃会话永远不会被清理。
:::
### 会话统计 {#session-statistics}

```bash
hermes sessions stats
```

输出：

```
总会话数：142
总消息数：3847
  cli：89 个会话
  telegram：38 个会话
  discord：15 个会话
数据库大小：12.4 MB
```

如需更深入的分析—— Token 用量、费用估算、工具拆解和活动模式，请使用 [`hermes insights`](/reference/cli-commands#hermes-insights)。

## 会话搜索工具 {#session-search-tool}

Agent 内置了一个 `session_search` 工具，可以利用 SQLite 的 FTS5 引擎对所有历史对话进行全文搜索。

### 工作原理 {#how-it-works}

1. FTS5 搜索匹配消息，按相关性排序
2. 按会话分组结果，取前 N 个唯一会话（默认 3 个）
3. 加载每个会话的对话，截取以匹配内容为中心的约 100K 字符
4. 发送给快速摘要模型生成聚焦摘要
5. 返回每个会话的摘要，包含元数据和周围上下文

### FTS5 查询语法 {#fts5-query-syntax}

搜索支持标准 FTS5 查询语法：

- 简单关键词：`docker deployment`
- 短语：`"exact phrase"`
- 布尔运算符：`docker OR kubernetes`、`python NOT java`
- 前缀：`deploy*`

### 何时使用 {#when-it-s-used}

Agent 会被提示自动使用会话搜索：

> *“当用户提到过去某个会话中的内容，或者你怀疑存在相关上下文时，请使用 session_search 来回忆，而不是要求用户重复说明。”*

## 各平台会话追踪 {#per-platform-session-tracking}

### 网关会话 {#gateway-sessions}

在消息平台上，会话由基于消息来源的确定性会话键来标识：

| 聊天类型 | 默认键格式 | 行为 |
|-----------|------------|------|
| Telegram 私聊 | `agent:main:telegram:dm:&lt;chat_id&gt;` | 每个私聊对应一个会话 |
| Discord 私聊 | `agent:main:discord:dm:&lt;chat_id&gt;` | 每个私聊对应一个会话 |
| WhatsApp 私聊 | `agent:main:whatsapp:dm:&lt;canonical_identifier&gt;` | 每个私聊用户对应一个会话（当存在映射时，LID/电话别名会合并为一个身份） |
| 群聊 | `agent:main:&lt;platform&gt;:group:&lt;chat_id&gt;:&lt;user_id&gt;` | 当平台暴露用户 ID 时，群内按用户 |
| 群组话题/主题 | `agent:main:&lt;platform&gt;:group:&lt;chat_id&gt;:&lt;thread_id&gt;` | 所有话题参与者共享一个会话（默认）。若 `thread_sessions_per_user: true`，则每个用户独立会话。 |
| 频道 | `agent:main:&lt;platform&gt;:channel:&lt;chat_id&gt;:&lt;user_id&gt;` | 当平台暴露用户 ID 时，频道内按用户 |

当 Hermes 无法从共享聊天中获取参与者标识时，它将退而使用该房间的一个共享会话。

### 共享 vs 隔离的群组会话 {#shared-vs-isolated-group-sessions}

默认情况下，Hermes 在 `config.yaml` 中设置了 `group_sessions_per_user: true`。这意味着：

- Alice 和 Bob 可以在同一个 Discord 频道中各自与 Hermes 对话，而不会共享对话历史
- 一个用户长时间的工具密集型任务不会污染另一个用户的上下文窗口
- 中断处理也保持按用户进行，因为正在运行的 Agent 键与隔离的会话键匹配

如果你希望使用共享的“房间大脑”，可以设置：

```yaml
group_sessions_per_user: false
```
这将群组/频道恢复为每个房间一个共享会话，这样保留了共享的对话上下文，但也共享了 token 成本、中断状态和上下文增长。

### 会话重置策略 {#session-reset-policies}

Gateway 会话会根据可配置的策略自动重置：

- **idle** — 在 N 分钟无活动后重置
- **daily** — 每天在特定小时重置
- **both** — 以先到者为准（空闲或每日）重置
- **none** — 从不自动重置

在会话自动重置之前，Agent 会获得一次机会来保存对话中的重要记忆或技能。

具有**活跃后台进程**的会话永远不会自动重置，无论策略如何。

## 存储位置 {#storage-locations}

| 内容 | 路径 | 描述 |
|------|------|-------------|
| SQLite 数据库 | `~/.hermes/state.db` | 所有会话元数据 + 带 FTS5 的消息 |
| Gateway 转录 | `~/.hermes/sessions/` | 每个会话的 JSONL 转录 + sessions.json 索引 |
| Gateway 索引 | `~/.hermes/sessions/sessions.json` | 将会话键映射到活跃会话 ID |

SQLite 数据库使用 WAL 模式，支持并发读取和单写入，这很适合 Gateway 的多平台架构。

### 数据库模式 {#database-schema}

`state.db` 中的关键表：

- **sessions** — 会话元数据（id, source, user_id, model, title, timestamps, token counts）。标题具有唯一索引（允许 NULL 标题，只有非 NULL 必须唯一）。
- **messages** — 完整消息历史（role, content, tool_calls, tool_name, token_count）
- **messages_fts** — 用于跨消息内容进行全文搜索的 FTS5 虚拟表

## 会话过期与清理 {#session-expiry-and-cleanup}

### 自动清理 {#automatic-cleanup}

- Gateway 会话根据配置的重置策略自动重置
- 在重置之前，Agent 会保存即将过期会话中的记忆和技能
- 可选自动修剪：当 `sessions.auto_prune` 为 `true` 时，在 CLI/Gateway 启动时，会修剪早于 `sessions.retention_days`（默认 90 天）的已结束会话
- 在真正删除行的修剪之后，`state.db` 会执行 `VACUUM` 以回收磁盘空间（SQLite 在普通 DELETE 时不会缩小文件）
- 修剪最多每 `sessions.min_interval_hours`（默认 24 小时）运行一次；上次运行的时间戳记录在 `state.db` 自身中，因此同一 `HERMES_HOME` 下的所有 Hermes 进程共享该信息

默认是**关闭**的——会话历史对于 `session_search` 回忆很有价值，静默删除可能会让用户感到意外。在 `~/.hermes/config.yaml` 中启用：

```yaml
sessions:
  auto_prune: true          # 选择加入 — 默认为 false
  retention_days: 90        # 保留已结束会话的天数
  vacuum_after_prune: true  # 修剪后回收磁盘空间
  min_interval_hours: 24    # 不要比这个频率更频繁地重新运行修剪
```

活跃会话永远不会被自动修剪，无论其存在时间多长。

### 手动清理 {#manual-cleanup}

```bash
# 修剪超过 90 天的会话
hermes sessions prune

# 删除特定会话
hermes sessions delete <session_id>

# 在修剪前导出（备份）
hermes sessions export backup.jsonl
hermes sessions prune --older-than 30 --yes
```
:::tip
数据库增长缓慢（典型情况：数百个会话约 10-15 MB），会话历史为跨历史对话的 `session_search` 召回提供支持，因此自动清理功能默认关闭。如果你运行的是高负载的网关/定时任务工作负载，且 `state.db` 显著影响性能（已知故障模式：约 1000 个会话导致 384 MB 的 state.db 拖慢 FTS5 插入和 `/resume` 列表），可以启用该功能。如需一次性清理而不开启自动清理，请使用 `hermes sessions prune`。
:::
