---
sidebar_position: 7
title: "会话 (Sessions)"
description: "会话持久化、恢复、搜索、管理以及各平台的会话追踪"
---

# 会话 (Sessions)

Hermes Agent 会自动将每次对话保存为会话。会话功能支持对话恢复、跨会话搜索以及完整的对话历史管理。

## 会话的工作原理

每一次对话——无论是来自 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix 还是其他任何消息平台——都会作为包含完整消息历史的会话进行存储。会话通过两个互补的系统进行追踪：

1. **SQLite 数据库** (`~/.hermes/state.db`) —— 结构化的会话元数据，支持 FTS5 全文搜索
2. **JSONL 转录文件** (`~/.hermes/sessions/`) —— 原始对话转录，包含工具调用 (gateway)

SQLite 数据库存储的内容包括：
- 会话 ID、来源平台、用户 ID
- **会话标题**（唯一且易于阅读的名称）
- 模型名称及配置
- 系统提示词快照
- 完整的消息历史（角色、内容、工具调用、工具结果）
- Token 计数（输入/输出）
- 时间戳（开始时间、结束时间）
- 父会话 ID（用于压缩触发的会话拆分）

### 会话来源

每个会话都会标记其来源平台：

| 来源 | 描述 |
|--------|-------------|
| `cli` | 交互式 CLI (`hermes` 或 `hermes chat`) |
| `telegram` | Telegram 消息应用 |
| `discord` | Discord 服务器/私信 |
| `slack` | Slack 工作区 |
| `whatsapp` | WhatsApp 消息应用 |
| `signal` | Signal 消息应用 |
| `matrix` | Matrix 房间和私信 |
| `mattermost` | Mattermost 频道 |
| `email` | 电子邮件 (IMAP/SMTP) |
| `sms` | 通过 Twilio 发送的短信 |
| `dingtalk` | 钉钉消息应用 |
| `feishu` | 飞书消息应用 |
| `wecom` | 企业微信 |
| `weixin` | 微信（个人版） |
| `bluebubbles` | 通过 BlueBubbles macOS 服务器连接的 Apple iMessage |
| `homeassistant` | Home Assistant 对话 |
| `webhook` | 传入的 Webhook |
| `api-server` | API 服务器请求 |
| `acp` | ACP 编辑器集成 |
| `cron` | 定时任务 (cron jobs) |
| `batch` | 批处理任务 |

## CLI 会话恢复

使用 `--continue` 或 `--resume` 从 CLI 恢复之前的对话：

### 继续上一个会话

```bash
# 恢复最近的一个 CLI 会话
hermes --continue
hermes -c

# 或者使用 chat 子命令
hermes chat --continue
hermes chat -c
```

这会从 SQLite 数据库中查找最近的 `cli` 会话并加载其完整的对话历史。

### 按名称恢复

如果你已经为会话设置了标题（请参阅下方的 [会话命名](#session-naming)），则可以按名称恢复它：

```bash
# 恢复已命名的会话
hermes -c "my project"

# 如果存在多个版本（my project, my project #2, my project #3），
# 这会自动恢复最近的一个
hermes -c "my project"   # → 恢复 "my project #3"
```

### 恢复特定会话

```bash
# 通过 ID 恢复特定会话
hermes --resume 20250305_091523_a1b2c3d4
hermes -r 20250305_091523_a1b2c3d4

# 通过标题恢复
hermes --resume "refactoring auth"

# 或者使用 chat 子命令
hermes chat --resume 20250305_091523_a1b2c3d4
```

会话 ID 会在你退出 CLI 会话时显示，也可以通过 `hermes sessions list` 查看。

### 恢复时的对话回顾 {#conversation-recap-on-resume}

当你恢复会话时，Hermes 会在输入提示符之前，以样式化的面板显示之前对话的简要回顾：

<img className="docs-terminal-figure" src="/img/docs/session-recap.svg" alt="恢复 Hermes 会话时显示的“之前对话”回顾面板的样式化预览。" />
<p className="docs-figure-caption">恢复模式会在返回实时提示符之前，显示一个包含最近用户和助手交互的紧凑回顾面板。</p>

回顾内容：
- 显示 **用户消息**（金色 `●`）和 **助手回复**（绿色 `◆`）
- **截断**长消息（用户消息 300 字符，助手消息 200 字符/3 行）
- **折叠**工具调用，仅显示计数和工具名称（例如 `[3 tool calls: terminal, web_search]`）
- **隐藏**系统消息、工具结果和内部推理过程
- **限制**在最近 10 次交互，并带有“... N earlier messages ...”提示
- 使用 **暗色样式** 以区别于当前正在进行的对话

若要禁用此回顾并保持极简的一行式行为，请在 `~/.hermes/config.yaml` 中设置：

```yaml
display:
  resume_display: minimal   # 默认值: full
```

:::tip
会话 ID 遵循 `YYYYMMDD_HHMMSS_<8-char-hex>` 格式，例如 `20250305_091523_a1b2c3d4`。你可以通过 ID 或标题进行恢复 —— 两者均支持 `-c` 和 `-r` 参数。
:::

## 会话命名 {#session-naming}

为会话设置易于阅读的标题，以便轻松查找和恢复。

### 自动生成标题

Hermes 会在第一次交互后自动为每个会话生成一个简短的描述性标题（3–7 个单词）。此过程在后台线程中使用快速辅助模型运行，因此不会增加延迟。当你使用 `hermes sessions list` 或 `hermes sessions browse` 浏览会话时，会看到自动生成的标题。

自动命名功能每个会话仅触发一次，如果你已经手动设置了标题，则会跳过此步骤。

### 手动设置标题

在任何聊天会话（CLI 或网关）中使用 `/title` 斜杠命令：

```
/title my research project
```

标题会立即生效。如果会话尚未在数据库中创建（例如，你在发送第一条消息之前运行 `/title`），它会被排队并在会话开始时应用。

你也可以从命令行重命名现有会话：

```bash
hermes sessions rename 20250305_091523_a1b2c3d4 "refactoring auth module"
```

### 标题规则

- **唯一性** — 两个会话不能共享同一个标题
- **最大 100 字符** — 保持列表输出整洁
- **已清理** — 控制字符、零宽字符和 RTL 覆盖字符会被自动剥离
- **支持普通 Unicode** — 支持 Emoji、CJK（中日韩文字）、带重音的字符等

### 压缩时的自动谱系

当会话上下文被压缩时（通过 `/compress` 手动触发或自动触发），Hermes 会创建一个新的延续会话。如果原始会话有标题，新会话会自动获得一个带编号的标题：

```
"my project" → "my project #2" → "my project #3"
```

当你按名称恢复 (`hermes -c "my project"`) 时，它会自动选择该谱系中最近的一个会话。

### 消息平台中的 /title

`/title` 命令适用于所有网关平台（Telegram、Discord、Slack、WhatsApp）：

- `/title My Research` — 设置会话标题
- `/title` — 显示当前标题

## 会话管理命令

Hermes 通过 `hermes sessions` 提供了一整套会话管理命令：

### 列出会话

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
Title                  Preview                                  Last Active   ID
────────────────────────────────────────────────────────────────────────────────────────────────
refactoring auth       Help me refactor the auth module please   2h ago        20250305_091523_a
my project #3          Can you check the test failures?          yesterday     20250304_143022_e
—                      What's the weather in Las Vegas?          3d ago        20250303_101500_f
```

当会话没有标题时，使用更简单的格式：

```
Preview                                            Last Active   Src    ID
──────────────────────────────────────────────────────────────────────────────────────
Help me refactor the auth module please             2h ago        cli    20250305_091523_a
What's the weather in Las Vegas?                    3d ago        tele   20250303_101500_f
```

### 导出会话

```bash
# 将所有会话导出为 JSONL 文件
hermes sessions export backup.jsonl

# 导出特定平台的会话
hermes sessions export telegram-history.jsonl --source telegram

# 导出单个会话
hermes sessions export session.jsonl --session-id 20250305_091523_a1b2c3d4
```

导出的文件每行包含一个 JSON 对象，其中包含完整的会话元数据和所有消息。
### 删除会话

```bash
# 删除特定会话（需确认）
hermes sessions delete 20250305_091523_a1b2c3d4

# 直接删除，无需确认
hermes sessions delete 20250305_091523_a1b2c3d4 --yes
```

### 重命名会话

```bash
# 设置或更改会话标题
hermes sessions rename 20250305_091523_a1b2c3d4 "debugging auth flow"

# 多单词标题在 CLI 中无需引号
hermes sessions rename 20250305_091523_a1b2c3d4 debugging auth flow
```

如果该标题已被其他会话使用，系统会报错。

### 清理旧会话

```bash
# 删除超过 90 天（默认值）的已结束会话
hermes sessions prune

# 自定义时间阈值
hermes sessions prune --older-than 30

# 仅清理特定平台的会话
hermes sessions prune --source telegram --older-than 60

# 跳过确认
hermes sessions prune --older-than 30 --yes
```

:::info
清理操作仅删除**已结束**的会话（即已明确结束或自动重置的会话）。活跃会话永远不会被清理。
:::

### 会话统计

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

如需更深入的分析（如 Token 使用量、成本估算、工具调用明细和活跃度模式），请使用 [`hermes insights`](/reference/cli-commands#hermes-insights)。

## 会话搜索工具

Agent 内置了 `session_search` 工具，利用 SQLite 的 FTS5 引擎对所有历史对话进行全文搜索。

### 工作原理

1. FTS5 根据相关性对匹配的消息进行排序
2. 按会话对结果进行分组，取前 N 个唯一会话（默认为 3 个）
3. 加载每个会话的对话内容，截取匹配项周围约 10 万字符的内容
4. 发送给快速摘要模型进行重点总结
5. 返回包含元数据和上下文的会话摘要

### FTS5 查询语法

搜索支持标准的 FTS5 查询语法：

- 简单关键词：`docker deployment`
- 短语：`"exact phrase"`
- 布尔逻辑：`docker OR kubernetes`, `python NOT java`
- 前缀：`deploy*`

### 使用场景

Agent 会被自动提示使用会话搜索：

> *“当用户引用过去对话中的内容，或者你怀疑存在相关的先前上下文时，请在要求用户重复之前使用 session_search 进行回顾。”*

## 各平台会话追踪

### 网关会话

在消息平台上，会话由根据消息来源生成的确定性会话键（Session Key）标识：

| 聊天类型 | 默认键格式 | 行为 |
|-----------|--------------------|----------|
| Telegram 私聊 | `agent:main:telegram:dm:<chat_id>` | 每个私聊窗口一个会话 |
| Discord 私聊 | `agent:main:discord:dm:<chat_id>` | 每个私聊窗口一个会话 |
| WhatsApp 私聊 | `agent:main:whatsapp:dm:<chat_id>` | 每个私聊窗口一个会话 |
| 群聊 | `agent:main:<platform>:group:<chat_id>:<user_id>` | 当平台暴露用户 ID 时，群内每个用户一个会话 |
| 群组话题/主题 | `agent:main:<platform>:group:<chat_id>:<thread_id>:<user_id>` | 该话题/主题内每个用户一个会话 |
| 频道 | `agent:main:<platform>:channel:<chat_id>:<user_id>` | 当平台暴露用户 ID 时，频道内每个用户一个会话 |

当 Hermes 无法获取共享聊天中的参与者标识符时，它会退回到该聊天室共享一个会话。

### 共享与隔离的群组会话

默认情况下，Hermes 在 `config.yaml` 中使用 `group_sessions_per_user: true`。这意味着：

- Alice 和 Bob 可以在同一个 Discord 频道中与 Hermes 对话，而不会共享对话记录
- 一个用户的长耗时工具任务不会污染另一个用户的上下文窗口
- 中断处理也保持在用户级别，因为运行中的 Agent 键与隔离的会话键匹配

如果你希望拥有一个共享的“房间大脑”，请设置：

```yaml
group_sessions_per_user: false
```

这将使群组/频道恢复为每个房间一个共享会话，从而保留共享的对话上下文，但也会共享 Token 成本、中断状态和上下文增长。

### 会话重置策略

网关会话会根据可配置的策略自动重置：

- **idle** — 在 N 分钟不活动后重置
- **daily** — 每天在特定时间重置
- **both** — 满足其中任一条件（空闲或每日）即重置
- **none** — 从不自动重置

在会话自动重置之前，Agent 会获得一次机会，用于保存对话中重要的记忆或技能。

无论策略如何，带有**活跃后台进程**的会话永远不会被自动重置。

## 存储位置

| 内容 | 路径 | 描述 |
|------|------|-------------|
| SQLite 数据库 | `~/.hermes/state.db` | 所有会话元数据 + 带有 FTS5 的消息 |
| 网关记录 | `~/.hermes/sessions/` | 每个会话的 JSONL 记录 + sessions.json 索引 |
| 网关索引 | `~/.hermes/sessions/sessions.json` | 将会话键映射到活跃会话 ID |

SQLite 数据库使用 WAL 模式以支持并发读取和单写入，这非常适合网关的多平台架构。

### 数据库架构

`state.db` 中的关键表：

- **sessions** — 会话元数据（id、source、user_id、model、title、timestamps、token counts）。标题具有唯一索引（允许标题为 NULL，仅非 NULL 值必须唯一）。
- **messages** — 完整消息历史（role、content、tool_calls、tool_name、token_count）
- **messages_fts** — 用于消息内容全文搜索的 FTS5 虚拟表

## 会话过期与清理

### 自动清理

- 网关会话根据配置的重置策略自动重置
- 重置前，Agent 会保存过期会话中的记忆和技能
- 已结束的会话会保留在数据库中，直到被清理

### 手动清理

```bash
# 清理超过 90 天的会话
hermes sessions prune

# 删除特定会话
hermes sessions delete <session_id>

# 清理前导出（备份）
hermes sessions export backup.jsonl
hermes sessions prune --older-than 30 --yes
```

:::tip
数据库增长缓慢（通常数百个会话仅占用 10-15 MB）。清理主要用于移除你不再需要进行搜索回顾的旧对话。
:::
