---
sidebar_position: 3
title: "持久记忆"
description: "Hermes Agent 如何跨会话记忆——MEMORY.md、USER.md 以及会话搜索"
---

<a id="persistent-memory"></a>
# 持久记忆

Hermes Agent 拥有有限、经过整理的记忆，能够跨会话持久存在。这使得它可以记住你的偏好、项目、环境以及学到的东西。

<a id="how-it-works"></a>
## 工作原理

两个文件构成了 Agent 的记忆：

| 文件 | 用途 | 字符限制 |
|------|------|----------|
| **MEMORY.md** | Agent 的个人笔记——环境事实、约定、学到的东西 | 2,200 字符（约 800 tokens） |
| **USER.md** | 用户档案——你的偏好、沟通风格、期望 | 1,375 字符（约 500 tokens） |

两者都存储在 `~/.hermes/memories/` 中，并在会话开始时以冻结快照的形式注入到系统提示中。Agent 通过 `memory` 工具管理自己的记忆——它可以添加、替换或删除条目。

:::info
字符限制让记忆保持聚焦。当记忆满了，Agent 会合并或替换条目，为新的信息腾出空间。
:::

<a id="how-memory-appears-in-the-system-prompt"></a>
## 记忆在系统提示中如何呈现

在每个会话开始时，记忆条目从磁盘加载，并以冻结块的形式渲染到系统提示中：

```
══════════════════════════════════════════════
记忆（你的个人笔记）[67% — 1,474/2,200 字符]
══════════════════════════════════════════════
用户的项目是一个位于 ~/code/myapi 的 Rust Web 服务，使用 Axum + SQLx
§
这台机器运行 Ubuntu 22.04，已安装 Docker 和 Podman
§
用户偏好简洁的回复，不喜欢冗长的解释
```

格式包括：
- 头部显示存储类型（MEMORY 或 USER PROFILE）
- 使用百分比和字符数，以便 Agent 知道容量
- 单个条目之间用 `§`（节号）分隔符隔开
- 条目可以是多行的

**冻结快照模式：** 系统提示注入仅在会话开始时捕获一次，在会话过程中不会改变。这是有意为之——它保留了 LLM 的前缀缓存以提高性能。当 Agent 在会话中添加/删除记忆条目时，更改会立即持久化到磁盘，但直到下一个会话开始才会出现在系统提示中。工具响应始终显示实时状态。

<a id="memory-tool-actions"></a>
## 记忆工具操作

Agent 使用 `memory` 工具执行以下操作：

- **add** — 添加新的记忆条目
- **replace** — 用更新后的内容替换现有条目（通过 `old_text` 进行子串匹配）
- **remove** — 删除不再相关的条目（通过 `old_text` 进行子串匹配）

没有 `read` 操作——记忆内容在会话开始时自动注入到系统提示中。Agent 将它的记忆视为对话上下文的一部分。

<a id="substring-matching"></a>
### 子串匹配

`replace` 和 `remove` 操作使用简短的唯一子串匹配——你不需要提供完整的条目文本。`old_text` 参数只需要是一个能唯一标识一个条目的子串：

```python
# 如果记忆包含 "User prefers dark mode in all editors"
memory(action="replace", target="memory",
       old_text="dark mode",
       content="User prefers light mode in VS Code, dark mode in terminal")
```
如果子字符串匹配多个条目，会返回错误，提示需要更精确的匹配。

<a id="two-targets-explained"></a>
## 两个存储目标详解

<a id="memory-agent-s-personal-notes"></a>
### `memory` — Agent 的个人便签

Agent 需要记住的环境、工作流程和经验教训等信息：

- 环境事实（操作系统、工具、项目结构）
- 项目约定和配置
- 发现的工具怪癖和变通方法
- 已完成任务的日记条目
- 有效的方法和技巧

<a id="user-user-profile"></a>
### `user` — 用户画像

关于用户身份、偏好和沟通风格的信息：

- 姓名、角色、时区
- 沟通偏好（简洁还是详细、格式偏好）
- 用户在意的事项和要避免的内容
- 工作流习惯
- 技术熟练程度

<a id="what-to-save-vs-skip"></a>
## 保存 vs 跳过什么

<a id="save-these-proactively"></a>
### 这些要保存（主动式）

Agent 会自动保存——你无需提出请求。当它学到以下内容时会保存：

- **用户偏好：**“我喜欢 TypeScript 胜过 JavaScript” → 保存至 `user`
- **环境事实：**“这台服务器运行的是 Debian 12 和 PostgreSQL 16” → 保存至 `memory`
- **纠正：**“不要在 Docker 命令中使用 `sudo`，用户已在 docker 组中” → 保存至 `memory`
- **约定：**“项目使用 Tab 缩进，120 字符行宽，Google 风格文档字符串” → 保存至 `memory`
- **已完成的工作：**“2026-01-15 将数据库从 MySQL 迁移到 PostgreSQL” → 保存至 `memory`
- **明确请求：**“记住我的 API 密钥每月轮换一次” → 保存至 `memory`

<a id="skip-these"></a>
### 这些要跳过

- **琐碎/明显的信息：**“用户问了关于 Python 的问题”——过于模糊，没有用处
- **容易重新发现的事实：**“Python 3.12 支持 f-string 嵌套”——可以通过网络搜索
- **原始数据转储：**大型代码块、日志文件、数据表——对于记忆来说太大
- **会话特定的临时信息：**临时文件路径、一次性调试上下文
- **上下文文件中已有的信息：**`SOUL.md` 和 `AGENTS.md` 的内容

<a id="capacity-management"></a>
## 容量管理

记忆有严格的字符数限制，以保持系统提示的规模可控：

| 存储目标 | 限制 | 典型条目数 |
|-------|-------|----------------|
| memory | 2,200 字符 | 8-15 条 |
| user | 1,375 字符 | 5-10 条 |

<a id="what-happens-when-memory-is-full"></a>
### 记忆满时会发生什么

当你尝试添加超过限制的条目时，工具会返回错误：

```json
{
  "success": false,
  "error": "记忆已使用 2,100/2,200 字符。添加此条目（250 字符）会超出限制。请先替换或移除现有条目。",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

Agent 随后应执行以下操作：
1. 读取当前条目（显示在错误响应中）
2. 确定可以移除或合并的条目
3. 使用 `replace` 将相关条目合并为较短的版本
4. 然后 `add` 新条目

**最佳实践：** 当记忆使用超过 80% 容量（可在系统提示头部看到）时，先合并条目，再添加新条目。例如，将三个独立的“项目使用 X”条目合并成一个全面的项目描述条目。

<a id="practical-examples-of-good-memory-entries"></a>
### 良好的记忆条目实际案例
**紧凑、信息密集的条目效果最好：**

```
# 好：包含多个相关事实
用户运行 macOS 14 Sonoma，使用 Homebrew，有 Docker Desktop 和 Podman。Shell：zsh with oh-my-zsh。编辑器：VS Code with Vim keybindings。

# 好：具体、可操作的约定
项目 ~/code/api 使用 Go 1.22、sqlc 进行数据库查询、chi 路由器。运行测试用 'make test'。CI 通过 GitHub Actions。

# 好：带有上下文的学习经验
staging 服务器（10.0.1.50）需要 SSH 端口 2222，而不是 22。密钥位于 ~/.ssh/staging_ed25519。

# 差：过于模糊
用户有一个项目。

# 差：过于冗长
2026 年 1 月 5 日，用户让我查看他们的项目，该项目位于 ~/code/api。我发现它使用的是 Go 版本 1.22 以及……
```

<a id="duplicate-prevention"></a>
## 重复预防

内存系统会自动拒绝完全相同的重复条目。如果你试图添加已存在的内容，它会以“未添加重复项”的消息返回成功。

<a id="security-scanning"></a>
## 安全扫描

内存条目在被接受之前会进行注入和泄露模式扫描，因为它们会被注入到系统提示中。匹配威胁模式（提示注入、凭据泄露、SSH 后门）或包含不可见 Unicode 字符的内容会被拦截。

<a id="session-search"></a>
## 会话搜索

除了 MEMORY.md 和 USER.md，Agent 还可以使用 `session_search` 工具搜索其过去的对话：

- 所有 CLI 和消息会话都存储在 SQLite（`~/.hermes/state.db`）中，支持 FTS5 全文搜索
- 搜索查询直接从数据库返回实际消息——没有 LLM 摘要，没有截断
- Agent 可以找到几周前讨论过的事情，即使它们不在活动记忆中
- Agent 还可以在其找到的任何会话中向前/向后滚动

```bash
hermes sessions list    # 浏览过去的会话
```

有关三种调用形态（发现 / 滚动 / 浏览）以及响应格式，请参阅[会话搜索工具](/user-guide/sessions#session-search-tool)。

<a id="sessionsearch-vs-memory"></a>
### session_search 与 memory 对比

| 功能 | 持久记忆 | 会话搜索 |
|---------|------------------|----------------|
| **容量** | 总计约 1,300 令牌 | 无限制（所有会话） |
| **速度** | 即时（在系统提示中） | ~20ms FTS5 查询，~1ms 滚动 |
| **成本** | 每次提示都有令牌成本 | 免费——无 LLM 调用 |
| **用例** | 关键事实始终可用 | 查找特定的过去对话 |
| **管理** | 由 Agent 手动整理 | 自动——所有会话都存储 |
| **令牌成本** | 每次会话固定（约 1,300 令牌） | 按需（需要时搜索） |

**记忆**用于应始终处于上下文中的关键事实。**会话搜索**用于“我们上周讨论过 X 吗？”这类查询，Agent 需要回忆过去对话中的具体细节。

<a id="configuration"></a>
## 配置

```yaml
# 在 ~/.hermes/config.yaml 中
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 令牌
  user_char_limit: 1375     # ~500 令牌
```

<a id="external-memory-providers"></a>
## 外部记忆提供商

为了实现超越 MEMORY.md 和 USER.md 的更深层次、持久化的记忆，Hermes 提供了 8 个外部记忆提供商插件——包括 Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover 和 Supermemory。
外部 Provider **与内建记忆并行**运行（绝不会替代它），并提供知识图谱、语义搜索、自动事实提取、跨会话用户建模等增强能力。

```bash
hermes memory setup      # 选择一个 Provider 并进行配置
hermes memory status     # 查看当前激活的 Provider
```

关于各个 Provider 的详细信息、设置步骤和对比，请参阅[记忆 Provider](./memory-providers.md)指南。
