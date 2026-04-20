---
sidebar_position: 5
title: "Prompt 组装"
description: "Hermes 如何构建系统 Prompt、保持缓存稳定性以及注入临时层"
---

# Prompt 组装 {#prompt-assembly}

Hermes 有意识地将以下内容分开：

- **缓存的系统 Prompt 状态**
- **API 调用时的临时增量内容**

这是本项目中最重要的设计决策之一，因为它会影响：

- Token 使用量
- Prompt 缓存（Prompt Caching）的有效性
- 会话连贯性
- 记忆的准确性

主要文件：

- `run_agent.py`
- `agent/prompt_builder.py`
- `tools/memory_tool.py`

## 缓存的系统 Prompt 层 {#cached-system-prompt-layers}

缓存的系统 Prompt 大致按以下顺序组装：

1. Agent 身份 —— 优先使用 `HERMES_HOME` 中的 `SOUL.md`，如果不存在，则回退到 `prompt_builder.py` 中的 `DEFAULT_AGENT_IDENTITY`
2. 工具感知行为指南
3. Honcho 静态块（激活时）
4. 可选的系统消息
5. 固化的 MEMORY（记忆）快照
6. 固化的 USER（用户）档案快照
7. 技能索引
8. 上下文文件（`AGENTS.md`、`.cursorrules`、`.cursor/rules/*.mdc`）—— 如果 `SOUL.md` 已在步骤 1 中作为身份加载，则**不**包含在此处
9. 时间戳 / 可选的会话 ID
10. 平台提示

当设置了 `skip_context_files` 时（例如子 Agent 委派），不会加载 `SOUL.md`，而是使用硬编码的 `DEFAULT_AGENT_IDENTITY`。

### 具体示例：组装后的系统 Prompt {#concrete-example-assembled-system-prompt}

以下是当所有层都存在时，最终系统 Prompt 的简化视图（注释显示了每个部分的来源）：

```
# 第 1 层：Agent 身份 (来自 ~/.hermes/SOUL.md)
You are Hermes, an AI assistant created by Nous Research.
You are an expert software engineer and researcher.
You value correctness, clarity, and efficiency.
...

# 第 2 层：工具感知行为指南
You have persistent memory across sessions. Save durable facts using
the memory tool: user preferences, environment details, tool quirks,
and stable conventions. Memory is injected into every turn, so keep
it compact and focused on facts that will still matter later.
...
When the user references something from a past conversation or you
suspect relevant cross-session context exists, use session_search
to recall it before asking them to repeat themselves.

# 工具使用强制执行 (仅针对 GPT/Codex 模型)
You MUST use your tools to take action — do not describe what you
would do or plan to do without actually doing it.
...

# 第 3 层：Honcho 静态块 (激活时)
[Honcho personality/context data]

# 第 4 层：可选系统消息 (来自配置或 API)
[User-configured system message override]

# 第 5 层：固化的 MEMORY 快照
## Persistent Memory
- User prefers Python 3.12, uses pyproject.toml
- Default editor is nvim
- Working on project "atlas" in ~/code/atlas
- Timezone: US/Pacific

# 第 6 层：固化的 USER 档案快照
## User Profile
- Name: Alice
- GitHub: alice-dev

# 第 7 层：技能索引
## Skills (mandatory)
Before replying, scan the skills below. If one clearly matches
your task, load it with skill_view(name) and follow its instructions.
...
<available_skills>
  software-development:
    - code-review: Structured code review workflow
    - test-driven-development: TDD methodology
  research:
    - arxiv: Search and summarize arXiv papers
</available_skills>

# 第 8 层：上下文文件 (来自项目目录)
# Project Context
The following project context files have been loaded and should be followed:

## AGENTS.md
This is the atlas project. Use pytest for testing. The main
entry point is src/atlas/main.py. Always run `make lint` before
committing.

# 第 9 层：时间戳 + 会话
Current time: 2026-03-30T14:30:00-07:00
Session: abc123

# 第 10 层：平台提示
You are a CLI AI Agent. Try not to use markdown but simple text
renderable inside a terminal.
```

## SOUL.md 如何出现在 Prompt 中 {#how-soul-md-appears-in-the-prompt}

`SOUL.md` 位于 `~/.hermes/SOUL.md`，作为 Agent 的身份 —— 即系统 Prompt 的第一部分。`prompt_builder.py` 中的加载逻辑如下：

```python
# 来自 agent/prompt_builder.py (简化版)
def load_soul_md() -> Optional[str]:
    soul_path = get_hermes_home() / "SOUL.md"
    if not soul_path.exists():
        return None
    content = soul_path.read_text(encoding="utf-8").strip()
    content = _scan_context_content(content, "SOUL.md")  # 安全扫描
    content = _truncate_content(content, "SOUL.md")       # 限制在 20k 字符以内
    return content
```

当 `load_soul_md()` 返回内容时，它会替换硬编码的 `DEFAULT_AGENT_IDENTITY`。随后调用 `build_context_files_prompt()` 时会带上 `skip_soul=True` 参数，以防止 `SOUL.md` 出现两次（一次作为身份，一次作为上下文文件）。

如果 `SOUL.md` 不存在，系统将回退到：

```
You are Hermes Agent, an intelligent AI assistant created by Nous Research.
You are helpful, knowledgeable, and direct. You assist users with a wide
range of tasks including answering questions, writing and editing code,
analyzing information, creative work, and executing actions via your tools.
You communicate clearly, admit uncertainty when appropriate, and prioritize
being genuinely useful over being verbose unless otherwise directed below.
Be targeted and efficient in your exploration and investigations.
```

## 上下文文件如何注入 {#how-context-files-are-injected}

`build_context_files_prompt()` 使用**优先级系统** —— 仅加载一种项目上下文类型（匹配到第一个即停止）：

```python
# 来自 agent/prompt_builder.py (简化版)
def build_context_files_prompt(cwd=None, skip_soul=False):
    cwd_path = Path(cwd).resolve()

    # 优先级：匹配到第一个即停止 —— 仅加载一个项目上下文
    project_context = (
        _load_hermes_md(cwd_path)       # 1. .hermes.md / HERMES.md (向上查找至 git 根目录)
        or _load_agents_md(cwd_path)    # 2. AGENTS.md (仅限当前工作目录)
        or _load_claude_md(cwd_path)    # 3. CLAUDE.md (仅限当前工作目录)
        or _load_cursorrules(cwd_path)  # 4. .cursorrules / .cursor/rules/*.mdc
    )

    sections = []
    if project_context:
        sections.append(project_context)

    # 来自 HERMES_HOME 的 SOUL.md (独立于项目上下文)
    if not skip_soul:
        soul_content = load_soul_md()
        if soul_content:
            sections.append(soul_content)

    if not sections:
        return ""

    return (
        "# Project Context\n\n"
        "The following project context files have been loaded "
        "and should be followed:\n\n"
        + "\n".join(sections)
    )
```

### 上下文文件查找详情 {#context-file-discovery-details}

| 优先级 | 文件 | 搜索范围 | 备注 |
|----------|-------|-------------|-------|
| 1 | `.hermes.md`, `HERMES.md` | 当前目录向上至 git 根目录 | Hermes 原生项目配置 |
| 2 | `AGENTS.md` | 仅限当前目录 | 通用的 Agent 指令文件 |
| 3 | `CLAUDE.md` | 仅限当前目录 | 兼容 Claude Code |
| 4 | `.cursorrules`, `.cursor/rules/*.mdc` | 仅限当前目录 | 兼容 Cursor |

所有上下文文件都会经过：
- **安全扫描** —— 检查 Prompt 注入模式（不可见 Unicode、“忽略之前的指令”、凭据窃取尝试等）
- **截断** —— 限制在 20,000 字符以内，使用 70/20 的头尾保留比例并添加截断标记
- **剥离 YAML frontmatter** —— `.hermes.md` 的 frontmatter 会被移除（保留用于未来的配置覆盖）

## 仅限 API 调用时的层 {#api-call-time-only-layers}

这些内容有意识地*不*作为缓存系统 Prompt 的一部分进行持久化：

- `ephemeral_system_prompt`（临时系统 Prompt）
- Prefill 消息（预填消息）
- 网关衍生的会话上下文覆盖
- 在后续轮次中注入到当前轮次用户消息中的 Honcho 召回内容

这种分离保持了稳定前缀的稳定性，从而利于缓存。

## 记忆快照 {#memory-snapshots}

本地记忆和用户档案数据在会话开始时作为固化快照注入。会话期间的写入会更新磁盘状态，但在开启新会话或强制重建之前，不会改变已经构建好的系统 Prompt。

## 上下文文件 {#context-files}

`agent/prompt_builder.py` 使用**优先级系统**扫描并清理项目上下文文件 —— 仅加载一种类型（匹配到第一个即停止）：

1. `.hermes.md` / `HERMES.md`（向上查找至 git 根目录）
2. `AGENTS.md`（启动时的当前目录；子目录在会话期间通过 `agent/subdirectory_hints.py` 逐步发现）
3. `CLAUDE.md`（仅限当前目录）
4. `.cursorrules` / `.cursor/rules/*.mdc`（仅限当前目录）
`SOUL.md` 通过 `load_soul_md()` 单独加载到 identity 插槽中。当它加载成功后，`build_context_files_prompt(skip_soul=True)` 会防止它重复出现。

较长的文件在注入前会被截断。

## Skills 索引 {#skills-index}

当 Skills 工具可用时，Skills 系统会向 Prompt 中贡献一个紧凑的 Skills 索引。

## 为什么 Prompt 组装要这样拆分 {#why-prompt-assembly-is-split-this-way}

该架构经过专门优化，旨在：

- 保留模型提供商端的 Prompt 缓存（Prompt Caching）
- 避免不必要的历史记录变更
- 保持内存语义易于理解
- 允许 Gateway/ACP/CLI 添加上下文，而不会污染持久化的 Prompt 状态

## 相关文档 {#related-docs}

- [上下文压缩与 Prompt 缓存](./context-compression-and-caching.md)
- [会话存储](./session-storage.md)
- [Gateway 内部原理](./gateway-internals.md)
