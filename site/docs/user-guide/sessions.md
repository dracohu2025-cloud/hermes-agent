---
sidebar_position: 7
title: "Sessions"
description: "Session 持久化、恢复、搜索、管理以及跨平台 Session 追踪"
---

# Sessions

Hermes Agent 会自动将每一次对话保存为一个 Session。Session 实现了对话恢复、跨 Session 搜索以及完整的对话历史管理。

## Session 工作原理

每一场对话——无论是来自 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix 还是任何其他消息平台——都会作为一个带有完整消息历史记录的 Session 进行存储。Session 在两个互补的系统中进行追踪：

1. **SQLite 数据库** (`~/.hermes/state.db`) —— 结构化的 Session 元数据，支持 FTS5 全文搜索。
2. **JSONL 转录文件** (`~/.hermes/sessions/`) —— 原始对话转录，包括工具调用（网关）。

SQLite 数据库存储以下内容：
- Session ID、来源平台、用户 ID
- **Session 标题**（唯一的、易于阅读的名称）
- 模型名称和配置
- 系统提示词（System Prompt）快照
- 完整消息历史（角色、内容、工具调用、工具结果）
- Token 计数（输入/输出）
- 时间戳（started_at, ended_at）
- 父级 Session ID（用于压缩触发的 Session 拆分）

### Session 来源

每个 Session 都会标记其来源平台：

| 来源 | 描述 |
|--------|-------------|
| `cli` | 交互式 CLI (`hermes` 或 `hermes chat`) |
| `telegram` | Telegram 聊天软件 |
| `discord` | Discord 服务器/私聊 |
| `slack` | Slack 工作区 |
| `whatsapp` | WhatsApp 聊天软件 |
| `signal` | Signal 聊天软件 |
| `matrix` | Matrix 房间和私聊 |
| `mattermost` | Mattermost 频道 |
| `email` | 电子邮件 (IMAP/SMTP) |
| `sms` | 通过 Twilio 发送的短信 |
| `dingtalk` | 钉钉 |
| `feishu` | 飞书/Lark |
| `wecom` | 企业微信 |
| `homeassistant` | Home Assistant 对话 |
| `webhook` | 传入的 Webhooks |
| `api-server` | API 服务器请求 |
| `acp` | ACP 编辑器集成 |
| `cron` | 定时任务 (Cron jobs) |
| `batch` | 批处理运行 |

## CLI Session 恢复

使用 `--continue` 或 `--resume` 在 CLI 中恢复之前的对话：

### 继续上次 Session

```bash
# 恢复最近一次 CLI Session
hermes --continue
hermes -c

# 或者使用 chat 子命令
hermes chat --continue
hermes chat -c
```

这将从 SQLite 数据库中查找最近的 `cli` Session 并加载其完整的对话历史。

### 按名称恢复

如果你给 Session 起了标题（见下文 [Session 命名](#session-naming)），你可以按名称恢复它：

```bash
# 恢复一个命名的 Session
hermes -c "my project"

# 如果存在系列变体（my project, my project #2, my project #3），
# 这会自动恢复最近的一个
hermes -c "my project"   # → 恢复 "my project #3"
```

### 恢复特定 Session

```bash
# 通过 ID 恢复特定 Session
hermes --resume 20250305_091523_a1b2c3d4
hermes -r 20250305_091523_a1b2c3d4

# 通过标题恢复
hermes --resume "refactoring auth"

# 或者使用 chat 子命令
hermes chat --resume 20250305_091523_a1b2c3d4
```

Session ID 会在你退出 CLI Session 时显示，也可以通过 `hermes sessions list` 找到。

### 恢复时的对话回顾

当你恢复一个 Session 时，Hermes 会在输入提示符之前，在一个样式面板中显示先前对话的简要回顾：

<img className="docs-terminal-figure" src="/img/docs/session-recap.svg" alt="恢复 Hermes Session 时显示的先前对话回顾面板的样式预览。" />
<p className="docs-figure-caption">恢复模式在返回实时提示符之前，会显示一个包含近期用户和助手往来的紧凑回顾面板。</p>

回顾功能：
- 显示 **用户消息**（金色 `●`）和 **助手响应**（绿色 `◆`）
- **截断** 过长的消息（用户消息 300 字符，助手消息 200 字符 / 3 行）
- **折叠工具调用** 为带有工具名称的计数（例如：`[3 tool calls: terminal, web_search]`）
- **隐藏** 系统消息、工具结果和内部推理过程
- **上限** 为最后 10 次交流，并带有 "... N earlier messages ..." 指示器
- 使用 **暗淡样式** 以区别于当前活跃的对话

如需禁用回顾并保持极简的单行行为，请在 `~/.hermes/config.yaml` 中设置：

```yaml
display:
  resume_display: minimal   # 默认值: full
```

:::tip
Session ID 遵循 `YYYYMMDD_HHMMSS_<8位十六进制>` 格式，例如 `20250305_091523_a1b2c3d4`。你可以通过 ID 或标题恢复——`-c` 和 `-r` 都支持这两种方式。
:::

## Session 命名

为 Session 提供易于理解的标题，以便你轻松查找和恢复它们。

### 自动生成标题

Hermes 会在第一次交流后自动为每个 Session 生成一个简短的描述性标题（3-7 个词）。这在后台线程中使用快速的辅助模型运行，因此不会增加延迟。当你使用 `hermes sessions list` 或 `hermes sessions browse` 浏览 Session 时，会看到自动生成的标题。

自动命名每个 Session 只触发一次，如果你已经手动设置了标题，则会跳过。

### 手动设置标题

在任何聊天 Session（CLI 或网关）中使用 `/title` 斜杠命令：

```
/title my research project
```

标题会立即生效。如果 Session 尚未在数据库中创建（例如，你在发送第一条消息之前运行 `/title`），它会被加入队列并在 Session 开始后应用。

你也可以从命令行重命名现有的 Session：

```bash
hermes sessions rename 20250305_091523_a1b2c3d4 "refactoring auth module"
```

### 标题规则

- **唯一性** —— 没有两个 Session 可以共享相同的标题
- **最大 100 个字符** —— 保持列表输出整洁
- **自动清理** —— 控制字符、零宽字符和 RTL 覆盖字符会被自动剔除
- **支持标准 Unicode** —— 表情符号、中日韩文字（CJK）、带重音符号的字符均可正常使用

### 压缩时的自动继承

当 Session 的上下文被压缩时（通过 `/compress` 手动压缩或自动压缩），Hermes 会创建一个新的后续 Session。如果原始 Session 有标题，新 Session 会自动获得一个带编号的标题：

```
"my project" → "my project #2" → "my project #3"
```

当你按名称恢复（`hermes -c "my project"`）时，它会自动选择该系列中最近的一个 Session。

### 消息平台中的 /title

`/title` 命令在所有网关平台（Telegram, Discord, Slack, WhatsApp）中均有效：

- `/title My Research` — 设置 Session 标题
- `/title` — 显示当前标题

## Session 管理命令

Hermes 通过 `hermes sessions` 提供了一套完整的 Session 管理命令：

### 列出 Session

```bash
# 列出最近的 Session（默认：最后 20 个）
hermes sessions list

# 按平台过滤
hermes sessions list --source telegram

# 显示更多 Session
hermes sessions list --limit 50
```

当 Session 拥有标题时，输出会显示标题、预览和相对时间戳：

```
Title                  Preview                                  Last Active   ID
────────────────────────────────────────────────────────────────────────────────────────────────
refactoring auth       Help me refactor the auth module please   2h ago        20250305_091523_a
my project #3          Can you check the test failures?          yesterday     20250304_143022_e
—                      What's the weather in Las Vegas?          3d ago        20250303_101500_f
```

当 Session 没有标题时，会使用更简单的格式：

```
Preview                                            Last Active   Src    ID
──────────────────────────────────────────────────────────────────────────────────────
Help me refactor the auth module please             2h ago        cli    20250305_091523_a
What's the weather in Las Vegas?                    3d ago        tele   20250303_101500_f
```

### 导出 Session

```bash
# 将所有 Session 导出到 JSONL 文件
hermes sessions export backup.jsonl

# 导出特定平台的 Session
hermes sessions export telegram-history.jsonl --source telegram

# 导出单个 Session
hermes sessions export session.jsonl --session-id 20250305_091523_a1b2c3d4
```

导出的文件每行包含一个 JSON 对象，其中包含完整的 Session 元数据和所有消息。

### 删除 Session

```bash
# 删除特定 Session（需确认）
hermes sessions delete 20250305_091523_a1b2c3d4

# 无需确认直接删除
hermes sessions delete 20250305_091523_a1b2c3d4 --yes
```
### 重命名 Session

```bash
# 设置或更改 Session 的标题
hermes sessions rename 20250305_091523_a1b2c3d4 "debugging auth flow"

# 在 CLI 中，多单词标题不需要加引号
hermes sessions rename 20250305_091523_a1b2c3d4 debugging auth flow
```

如果该标题已被另一个 Session 使用，系统将显示错误。

### 清理旧 Session

```bash
# 删除超过 90 天（默认值）的已结束 Session
hermes sessions prune

# 自定义时间阈值
hermes sessions prune --older-than 30

# 仅清理特定平台的 Session
hermes sessions prune --source telegram --older-than 60

# 跳过确认步骤
hermes sessions prune --older-than 30 --yes
```

:::info
清理操作只会删除**已结束**的 Session（即已被明确结束或自动重置的 Session）。活跃的 Session 永远不会被清理。
:::

### Session 统计信息

```bash
hermes sessions stats
```

输出示例：

```
Total sessions: 142
Total messages: 3847
  cli: 89 sessions
  telegram: 38 sessions
  discord: 15 sessions
Database size: 12.4 MB
```

如需更深入的分析（如 Token 使用量、成本预估、工具使用明细和活动模式），请使用 [`hermes insights`](/reference/cli-commands#hermes-insights)。

## Session 搜索工具

Agent 内置了 `session_search` 工具，利用 SQLite 的 FTS5 引擎对所有历史对话进行全文搜索。

### 工作原理

1. FTS5 搜索匹配的消息，并按相关性排序。
2. 按 Session 对结果进行分组，取前 N 个唯一的 Session（默认为 3 个）。
3. 加载每个 Session 的对话内容，以匹配项为中心截取约 100K 字符。
4. 发送给快速总结模型进行针对性摘要。
5. 返回每个 Session 的摘要，包含元数据和上下文背景。

### FTS5 查询语法

搜索支持标准的 FTS5 查询语法：

- 简单关键词：`docker deployment`
- 短语：`"exact phrase"`
- 布尔逻辑：`docker OR kubernetes`，`python NOT java`
- 前缀匹配：`deploy*`

### 使用场景

Agent 会在以下情况下被提示自动使用 Session 搜索：

> *"当用户提到过去对话中的内容，或者你怀疑存在相关的历史上下文时，请在要求用户重复之前，先使用 session_search 进行回溯。"*

## 各平台 Session 追踪

### 网关 Session

在即时通讯平台上，Session 是通过根据消息来源生成的确定性 Session Key 来标识的：

| 聊天类型 | 默认 Key 格式 | 行为 |
|-----------|--------------------|----------|
| Telegram 私聊 | `agent:main:telegram:dm:<chat_id>` | 每个私聊窗口一个 Session |
| Discord 私聊 | `agent:main:discord:dm:<chat_id>` | 每个私聊窗口一个 Session |
| WhatsApp 私聊 | `agent:main:whatsapp:dm:<chat_id>` | 每个私聊窗口一个 Session |
| 群聊 | `agent:main:<platform>:group:<chat_id>:<user_id>` | 当平台提供用户 ID 时，群组内按用户区分 |
| 群聊话题/帖子 | `agent:main:<platform>:group:<chat_id>:<thread_id>:<user_id>` | 该话题/帖子内按用户区分 |
| 频道 | `agent:main:<platform>:channel:<chat_id>:<user_id>` | 当平台提供用户 ID 时，频道内按用户区分 |

当 Hermes 无法获取共享聊天中的参与者标识符时，它会回退到该聊天室共享同一个 Session。

### 共享 vs 隔离的群组 Session

默认情况下，Hermes 在 `config.yaml` 中使用 `group_sessions_per_user: true`。这意味着：

- Alice 和 Bob 可以在同一个 Discord 频道中与 Hermes 交流，而不会共享对话历史。
- 一个用户长时间且占用大量工具的任务不会污染另一个用户的上下文窗口。
- 中断处理也保持按用户区分，因为运行中的 Agent Key 与隔离的 Session Key 相匹配。

如果你希望使用共享的“群组大脑”，请设置：

```yaml
group_sessions_per_user: false
```

这将使群组/频道恢复为每个聊天室单个共享 Session，这保留了共享的对话上下文，但也会共享 Token 成本、中断状态和上下文增长。

### Session 重置策略

网关 Session 会根据可配置的策略自动重置：

- **idle** — 在闲置 N 分钟后重置。
- **daily** — 每天在特定小时重置。
- **both** — 闲置或到达每日时间，以先到者为准。
- **none** — 永不自动重置。

在 Session 自动重置之前，Agent 会获得一次机会来保存对话中任何重要的记忆或技能。

拥有**活跃后台进程**的 Session 无论采用何种策略，都永远不会被自动重置。

## 存储位置

| 内容 | 路径 | 描述 |
|------|------|-------------|
| SQLite 数据库 | `~/.hermes/state.db` | 所有 Session 元数据 + 支持 FTS5 的消息内容 |
| 网关对话记录 | `~/.hermes/sessions/` | 每个 Session 的 JSONL 记录 + sessions.json 索引 |
| 网关索引 | `~/.hermes/sessions/sessions.json` | 将 Session Key 映射到活跃的 Session ID |

SQLite 数据库使用 WAL 模式以支持并发读取和单写操作，这非常适合网关的多平台架构。

### 数据库 Schema

`state.db` 中的关键表：

- **sessions** — Session 元数据（id、来源、user_id、模型、标题、时间戳、Token 计数）。标题拥有唯一索引（允许 NULL 标题，但非 NULL 的标题必须唯一）。
- **messages** — 完整的消息历史（角色、内容、tool_calls、tool_name、token_count）。
- **messages_fts** — 用于对消息内容进行全文搜索的 FTS5 虚表。

## Session 过期与清理

### 自动清理

- 网关 Session 根据配置的重置策略自动重置。
- 在重置前，Agent 会从即将过期的 Session 中保存记忆和技能。
- 已结束的 Session 会保留在数据库中，直到被手动清理。

### 手动清理

```bash
# 清理超过 90 天的 Session
hermes sessions prune

# 删除特定的 Session
hermes sessions delete <session_id>

# 在清理前导出（备份）
hermes sessions export backup.jsonl
hermes sessions prune --older-than 30 --yes
```

:::tip
数据库增长缓慢（典型情况：数百个 Session 约占 10-15 MB）。清理的主要作用是移除那些你不再需要用于搜索回溯的旧对话。
:::
