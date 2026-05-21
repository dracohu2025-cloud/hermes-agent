---
sidebar_position: 5
title: "提示词组装"
description: "Hermes 如何构建系统提示词、保持缓存稳定性以及注入临时层"
---

<a id="prompt-assembly"></a>
# 提示词组装

Hermes 明确区分以下两部分：

- **缓存系统提示词状态**
- **API 调用时临时追加的内容**

这是该项目最重要的设计决策之一，因为它影响：

- token 用量
- 提示词缓存效果
- 会话连续性
- 记忆正确性

主要文件：

- `run_agent.py`
- `agent/prompt_builder.py`
- `tools/memory_tool.py`

<a id="cached-system-prompt-layers"></a>
## 缓存的系统提示词层

缓存的系统提示词大致按以下顺序组装：

1. Agent 身份 —— 当 `HERMES_HOME` 中存在 `SOUL.md` 时使用，否则回退到 `prompt_builder.py` 中的 `DEFAULT_AGENT_IDENTITY`
2. 工具感知行为指导
3. Honcho 静态块（启用时）
4. 可选系统消息
5. 冻结的 MEMORY 快照
6. 冻结的 USER 个人资料快照
7. 技能索引
8. 上下文文件（`AGENTS.md`、`.cursorrules`、`.cursor/rules/*.mdc`）—— 如果 SOUL.md 已经在步骤 1 中作为身份被加载，则此处**不再包含**
9. 时间戳 / 可选会话 ID
10. 平台提示

当设置了 `skip_context_files`（例如子 Agent 委托）时，不加载 SOUL.md，而是使用硬编码的 `DEFAULT_AGENT_IDENTITY`。

<a id="concrete-example-assembled-system-prompt"></a>
### 具体示例：组装后的系统提示词

以下是所有层都存在时最终系统提示词的简化视图（注释显示了每个部分的来源）：

```
# Layer 1: Agent Identity (from ~/.hermes/SOUL.md)
You are Hermes, an AI assistant created by Nous Research.
You are an expert software engineer and researcher.
You value correctness, clarity, and efficiency.
...

# Layer 2: Tool-aware behavior guidance
You have persistent memory across sessions. Save durable facts using
the memory tool: user preferences, environment details, tool quirks,
and stable conventions. Memory is injected into every turn, so keep
it compact and focused on facts that will still matter later.
...
When the user references something from a past conversation or you
suspect relevant cross-session context exists, use session_search
to recall it before asking them to repeat themselves.

# Tool-use enforcement (for GPT/Codex models only)
You MUST use your tools to take action — do not describe what you
would do or plan to do without actually doing it.
...

# Layer 3: Honcho static block (when active)
[Honcho personality/context data]

# Layer 4: Optional system message (from config or API)
[User-configured system message override]

# Layer 5: Frozen MEMORY snapshot
## Persistent Memory
- User prefers Python 3.12, uses pyproject.toml
- Default editor is nvim
- Working on project "atlas" in ~/code/atlas
- Timezone: US/Pacific

# Layer 6: Frozen USER profile snapshot
## User Profile
- Name: Alice
- GitHub: alice-dev

# Layer 7: Skills index
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

# Layer 8: Context files (from project directory)
# Project Context
The following project context files have been loaded and should be followed:

## AGENTS.md
This is the atlas project. Use pytest for testing. The main
entry point is src/atlas/main.py. Always run `make lint` before
committing.

# Layer 9: Timestamp + session
Current time: 2026-03-30T14:30:00-07:00
Session: abc123

# Layer 10: Platform hint
You are a CLI AI Agent. Try not to use markdown but simple text
renderable inside a terminal.
```
<a id="how-soul-md-appears-in-the-prompt"></a>
## SOUL.md 在提示词中的呈现方式

`SOUL.md` 文件位于 `~/.hermes/SOUL.md`，作为 Agent 的身份标识——它是系统提示词的第一部分。`prompt_builder.py` 中的加载逻辑如下：

```python
# 来自 agent/prompt_builder.py（简化版）
def load_soul_md() -> Optional[str]:
    soul_path = get_hermes_home() / "SOUL.md"
    if not soul_path.exists():
        return None
    content = soul_path.read_text(encoding="utf-8").strip()
    content = _scan_context_content(content, "SOUL.md")  # 安全扫描
    content = _truncate_content(content, "SOUL.md")       # 限制最多 20k 字符
    return content
```

当 `load_soul_md()` 返回内容时，它会替换硬编码的 `DEFAULT_AGENT_IDENTITY`。随后调用 `build_context_files_prompt()` 函数时，会传入 `skip_soul=True`，以防止 SOUL.md 出现两次（一次作为身份标识，一次作为上下文文件）。

如果 `SOUL.md` 不存在，系统会回退到以下默认内容：

```
你是 Hermes Agent，由 Nous Research 创建的智能 AI 助手。
你乐于助人、知识渊博且直截了当。你协助用户完成各种任务，
包括回答问题、编写和编辑代码、分析信息、创意工作以及通过工具执行操作。
你沟通清晰，在适当的时候承认不确定性，除非另有指示，否则优先做到真正有用，
而不是啰嗦。在探索和调查中要目标明确、高效。
```

<a id="how-context-files-are-injected"></a>
## 上下文文件如何注入

`build_context_files_prompt()` 使用**优先级系统**——只加载一种项目上下文类型（优先匹配第一个）：

```python
# 来自 agent/prompt_builder.py（简化版）
def build_context_files_prompt(cwd=None, skip_soul=False):
    cwd_path = Path(cwd).resolve()

    # 优先级：优先匹配第一个——只加载一个项目上下文
    project_context = (
        _load_hermes_md(cwd_path)       # 1. .hermes.md / HERMES.md（向上遍历到 git 根目录）
        or _load_agents_md(cwd_path)    # 2. AGENTS.md（仅当前工作目录）
        or _load_claude_md(cwd_path)    # 3. CLAUDE.md（仅当前工作目录）
        or _load_cursorrules(cwd_path)  # 4. .cursorrules / .cursor/rules/*.mdc
    )

    sections = []
    if project_context:
        sections.append(project_context)

    # 来自 HERMES_HOME 的 SOUL.md（独立于项目上下文）
    if not skip_soul:
        soul_content = load_soul_md()
        if soul_content:
            sections.append(soul_content)

    if not sections:
        return ""

    return (
        "# 项目上下文\n\n"
        "以下项目上下文文件已加载，"
        "应遵循其中的内容：\n\n"
        + "\n".join(sections)
    )
```

<a id="context-file-discovery-details"></a>
### 上下文文件发现详情

| 优先级 | 文件 | 搜索范围 | 说明 |
|----------|-------|-------------|-------|
| 1 | `.hermes.md`, `HERMES.md` | 从当前工作目录到 git 根目录 | Hermes 原生项目配置 |
| 2 | `AGENTS.md` | 仅当前工作目录 | 通用 Agent 指令文件 |
| 3 | `CLAUDE.md` | 仅当前工作目录 | Claude Code 兼容性 |
| 4 | `.cursorrules`, `.cursor/rules/*.mdc` | 仅当前工作目录 | Cursor 兼容性 |
所有上下文文件均经过以下处理：

- **安全扫描**——检查是否存在提示注入模式（不可见Unicode字符、“忽略之前的指令”、凭据窃取尝试）
- **截断**——以70/20的头尾比例截断至20,000字符，并附上截断标记
- **YAML前置元数据剥离**——移除 `.hermes.md` 的前置元数据（保留用于未来的配置覆盖）

<a id="api-call-time-only-layers"></a>
## 仅API调用时的分层

这些内容刻意**不**保留为缓存系统提示的一部分：

- `ephemeral_system_prompt`
- 预填充消息
- 网关推导的会话上下文覆盖层
- 后期Honcho回忆注入到当前轮次用户消息中

这种分离使得稳定前缀能够保持稳定以便缓存。

<a id="memory-snapshots"></a>
## 内存快照

本地内存和用户资料数据会在会话启动时以冻结快照的形式注入。会话期间的写入会更新磁盘状态，但不会修改已构建的系统提示，直到新会话或强制重新构建发生。

<a id="context-files"></a>
## 上下文文件

`agent/prompt_builder.py` 使用**优先级系统**扫描并清理项目上下文文件——仅加载一种类型（第一个匹配项胜出）：

1. `.hermes.md` / `HERMES.md`（遍历到git根目录）
2. `AGENTS.md`（启动时的当前工作目录；在会话期间通过 `agent/subdirectory_hints.py` 逐步发现子目录）
3. `CLAUDE.md`（仅当前工作目录）
4. `.cursorrules` / `.cursor/rules/*.mdc`（仅当前工作目录）

`SOUL.md` 通过 `load_soul_md()` 单独加载，用于身份槽。成功加载后，`build_context_files_prompt(skip_soul=True)` 会防止它出现两次。

长文件在注入前会被截断。

<a id="skills-index"></a>
## 技能索引

当技能工具可用时，技能系统会向提示中提供一个简洁的技能索引。

<a id="supported-prompt-customization-surfaces"></a>
## 支持的提示自定义表面

大多数用户应将 `agent/prompt_builder.py` 视为实现代码，而不是配置表面。支持的自定义路径是修改Hermes已加载的提示输入，而不是直接编辑Python模板。

<a id="use-these-surfaces-first"></a>
### 优先使用这些表面

- `~/.hermes/SOUL.md` — 用你自己的Agent角色和固定行为替换内置的默认身份块。
- `~/.hermes/MEMORY.md` 和 `~/.hermes/USER.md` — 提供跨会话持久的事实和用户资料数据，这些数据应快照到新会话中。
- 项目上下文文件，如 `.hermes.md`、`HERMES.md`、`AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` — 注入仓库特定的工作规则。
- 技能 — 打包可重用的工作流和参考，无需编辑核心提示代码。
- 可选的系统提示配置/API覆盖 — 添加部署特定的指令文本，无需派生Hermes。
- 临时覆盖层，如 `HERMES_EPHEMERAL_SYSTEM_PROMOT` 或预填充消息 — 添加轮次范围的指导，不应成为缓存提示前缀的一部分。

<a id="when-to-edit-code-instead"></a>
### 何时编辑代码

仅当你有意维护一个分支或向上游贡献行为变更时，才编辑 `agent/prompt_builder.py`。该文件为每个会话组装提示管道、缓存边界和注入顺序。直接在此编辑属于全局产品变更，而非每个用户的提示自定义。
换句话说：

- 如果你想换一个不同的助手身份，请编辑 `SOUL.md`
- 如果你想设置不同的仓库规则，请编辑项目上下文文件
- 如果你想要可复用的操作流程，请添加或修改技能（skills）
- 如果你想改变 Hermes 为所有人组装 prompt 的方式，请修改 Python 代码，并将其视为代码贡献

<a id="why-prompt-assembly-is-split-this-way"></a>
## 为什么 prompt 要这样拆解组装

该架构特意针对以下目标进行了优化：

- 保留服务端的 prompt 缓存能力
- 避免不必要地修改历史记录
- 让内存语义更容易理解
- 让 gateway / ACP / CLI 能够添加上下文，同时不会污染持久化的 prompt 状态

<a id="related-docs"></a>
## 相关文档

- [上下文压缩与 Prompt 缓存](./context-compression-and-caching.md)
- [会话存储](./session-storage.md)
- [Gateway 内部机制](./gateway-internals.md)
