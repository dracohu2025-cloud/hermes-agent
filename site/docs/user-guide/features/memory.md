---
sidebar_position: 3
title: "持久化记忆"
description: "Hermes Agent 如何跨会话进行记忆 —— MEMORY.md、USER.md 以及会话搜索"
---

# 持久化记忆 {#persistent-memory}

Hermes Agent 拥有受限且经过精选的记忆，这些记忆可以跨会话持久存在。这使得它能够记住你的偏好、你的项目、你的环境以及它所学到的知识。

## 工作原理 {#how-it-works}

Agent 的记忆由两个文件组成：

| 文件 | 用途 | 字符限制 |
|------|---------|------------|
| **MEMORY.md** | Agent 的个人笔记 —— 环境事实、约定、学到的知识 | 2,200 字符 (约 800 tokens) |
| **USER.md** | 用户画像 —— 你的偏好、沟通风格、期望 | 1,375 字符 (约 500 tokens) |

这两个文件都存储在 `~/.hermes/memories/` 中，并在会话开始时作为冻结快照注入到系统提示词（system prompt）中。Agent 通过 `memory` 工具管理自己的记忆 —— 它可以添加、替换或删除条目。

:::info
字符限制是为了保持记忆的聚焦。当记忆存满时，Agent 会合并或替换条目，以为新信息腾出空间。
:::

## 记忆如何出现在系统提示词中 {#how-memory-appears-in-the-system-prompt}

在每个会话开始时，记忆条目会从磁盘加载，并作为冻结块渲染到系统提示词中：

```
══════════════════════════════════════════════
MEMORY (your personal notes) [67% — 1,474/2,200 chars]
══════════════════════════════════════════════
User's project is a Rust web service at ~/code/myapi using Axum + SQLx
§
This machine runs Ubuntu 22.04, has Docker and Podman installed
§
User prefers concise responses, dislikes verbose explanations
```

该格式包括：
- 显示存储库类型的页眉（MEMORY 或 USER PROFILE）
- 使用百分比和字符计数，以便 Agent 了解容量情况
- 使用 `§`（分节符）分隔的单个条目
- 条目可以是多行的

**冻结快照模式：** 系统提示词的注入在会话开始时捕获一次，且在会话中途绝不改变。这是有意为之的 —— 它可以保留 LLM 的前缀缓存（prefix cache）以提高性能。当 Agent 在会话期间添加/删除记忆条目时，更改会立即持久化到磁盘，但直到下次会话开始才会出现在系统提示词中。工具的响应始终显示实时状态。

## Memory 工具操作 {#memory-tool-actions}

Agent 使用 `memory` 工具执行以下操作：

- **add** — 添加新的记忆条目
- **replace** — 用更新的内容替换现有条目（通过 `old_text` 进行子字符串匹配）
- **remove** — 删除不再相关的条目（通过 `old_text` 进行子字符串匹配）

没有 `read` 操作 —— 记忆内容在会话开始时会自动注入到系统提示词中。Agent 将其记忆视为对话上下文的一部分。

### 子字符串匹配 {#substring-matching}

`replace` 和 `remove` 操作使用简短的唯一子字符串匹配 —— 你不需要提供完整的条目文本。`old_text` 参数只需要是一个能唯一标识该条目的子字符串：

```python
# 如果记忆包含 "User prefers dark mode in all editors"
memory(action="replace", target="memory",
       old_text="dark mode",
       content="User prefers light mode in VS Code, dark mode in terminal")
```

如果子字符串匹配到多个条目，则会返回错误，要求提供更具体的匹配项。

## 两个目标的解释 {#two-targets-explained}

### `memory` — Agent 的个人笔记 {#memory-agent-s-personal-notes}

用于记录 Agent 需要记住的关于环境、工作流和经验教训的信息：

- 环境事实（操作系统、工具、项目结构）
- 项目约定和配置
- 发现的工具特性和变通方法
- 已完成任务的日志条目
- 行之有效的技能和技术

### `user` — 用户画像 {#user-user-profile}

用于记录关于用户的身份、偏好和沟通风格的信息：

- 姓名、角色、时区
- 沟通偏好（简洁 vs 详细，格式偏好）
- 厌恶的事项和需要避免的事项
- 工作流习惯
- 技术水平

## 哪些该存，哪些不该存 {#what-to-save-vs-skip}

### 存这些（主动存储） {#save-these-proactively}

Agent 会自动保存 —— 你不需要特意要求。当它学到以下内容时会进行保存：

- **用户偏好：** “我更喜欢 TypeScript 而不是 JavaScript” → 保存到 `user`
- **环境事实：** “这台服务器运行 Debian 12 和 PostgreSQL 16” → 保存到 `memory`
- **修正：** “不要对 Docker 命令使用 `sudo`，用户已在 docker 组中” → 保存到 `memory`
- **约定：** “项目使用 tabs 缩进，120 字符行宽，Google 风格的 docstrings” → 保存到 `memory`
- **已完成的工作：** “2026-01-15 将数据库从 MySQL 迁移到了 PostgreSQL” → 保存到 `memory`
- **明确的要求：** “记住我的 API 密钥每月轮换一次” → 保存到 `memory`

### 跳过这些 {#skip-these}

- **琐碎/显而易见的信息：** “用户询问了关于 Python 的问题” —— 太模糊，没用
- **容易重新发现的事实：** “Python 3.12 支持 f-string 嵌套” —— 可以通过网页搜索找到
- **原始数据转储：** 大型代码块、日志文件、数据表 —— 对记忆来说太大了
- **会话特定的临时信息：** 临时文件路径、一次性的调试上下文
- **已存在于上下文文件中的信息：** SOUL.md 和 AGENTS.md 中的内容

## 容量管理 {#capacity-management}

记忆有严格的字符限制，以保持系统提示词的大小受控：

| 存储库 | 限制 | 典型条目数 |
|-------|-------|----------------|
| memory | 2,200 字符 | 8-15 条 |
| user | 1,375 字符 | 5-10 条 |

### 当记忆存满时会发生什么 {#what-happens-when-memory-is-full}

当你尝试添加一个会超过限制的条目时，工具会返回错误：

```json
{
  "success": false,
  "error": "Memory at 2,100/2,200 chars. Adding this entry (250 chars) would exceed the limit. Replace or remove existing entries first.",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

此时 Agent 应该：
1. 读取当前条目（显示在错误响应中）
2. 识别可以删除或合并的条目
3. 使用 `replace` 将相关的条目合并为更短的版本
4. 然后 `add` 新条目

**最佳实践：** 当记忆容量超过 80% 时（在系统提示词页眉可见），在添加新条目之前先合并条目。例如，将三个独立的“项目使用 X”条目合并为一个综合的项目描述条目。

### 优质记忆条目的实际案例 {#practical-examples-of-good-memory-entries}

**紧凑、信息密集的条目效果最好：**

```
# 优：打包了多个相关事实
User runs macOS 14 Sonoma, uses Homebrew, has Docker Desktop and Podman. Shell: zsh with oh-my-zsh. Editor: VS Code with Vim keybindings.

# 优：具体、可操作的约定
Project ~/code/api uses Go 1.22, sqlc for DB queries, chi router. Run tests with 'make test'. CI via GitHub Actions.

# 优：带有上下文的经验教训
The staging server (10.0.1.50) needs SSH port 2222, not 22. Key is at ~/.ssh/staging_ed25519.

# 劣：太模糊
User has a project.

# 劣：太啰嗦
On January 5th, 2026, the user asked me to look at their project which is
located at ~/code/api. I discovered it uses Go version 1.22 and...
```

## 重复预防 {#duplicate-prevention}

记忆系统会自动拒绝完全重复的条目。如果你尝试添加已经存在的内容，它会返回成功并提示“未添加重复项”。

## 安全扫描 {#security-scanning}

由于记忆条目会被注入到系统提示词中，因此在接受之前会扫描是否存在注入和外泄模式。匹配威胁模式（提示词注入、凭据外泄、SSH 后门）或包含不可见 Unicode 字符的内容将被拦截。

## 会话搜索 {#session-search}

除了 MEMORY.md 和 USER.md 之外，Agent 还可以使用 `session_search` 工具搜索其过去的对话：

- 所有 CLI 和消息会话都存储在 SQLite (`~/.hermes/state.db`) 中，支持 FTS5 全文搜索
- 搜索查询会返回相关的历史对话，并使用 Gemini Flash 进行总结
- Agent 可以找到几周前讨论过的内容，即使这些内容不在其活跃记忆中

```bash
hermes sessions list    # 浏览历史会话
```

### session_search vs memory {#sessionsearch-vs-memory}

| 特性 | 持久化记忆 | 会话搜索 |
|---------|------------------|----------------|
| **容量** | 总计约 1,300 tokens | 无限制（所有会话） |
| **速度** | 即时（在系统提示词中） | 需要搜索 + LLM 总结 |
| **用例** | 关键事实始终可用 | 查找特定的历史对话 |
| **管理** | 由 Agent 手动精选 | 自动 —— 存储所有会话 |
| **Token 成本** | 每个会话固定（约 1,300 tokens） | 按需（仅在搜索时产生） |
**Memory** 用于存储那些应该始终处于上下文中的关键事实。**Session search** 则用于处理类似“我们上周讨论过 X 吗？”这类查询，此时 Agent 需要从过去的对话中召回具体细节。

## Configuration {#configuration}

```yaml
# 在 ~/.hermes/config.yaml 中
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # 约 800 tokens
  user_char_limit: 1375     # 约 500 tokens
```

## External Memory Providers {#external-memory-providers}

为了实现超越 MEMORY.md 和 USER.md 的更深层、持久化的记忆，Hermes 内置了 8 个外部 Memory Provider 插件 —— 包括 Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover 和 Supermemory。

外部 Provider 与内置 Memory **并行**运行（绝非替代关系），并增加了诸如知识图谱、语义搜索、自动事实提取以及跨会话用户建模等功能。

```bash
hermes memory setup      # 选择一个 Provider 并进行配置
hermes memory status     # 检查当前激活的状态
```

有关每个 Provider 的详细信息、设置说明及对比，请参阅 [Memory Providers](./memory-providers.md) 指南。
