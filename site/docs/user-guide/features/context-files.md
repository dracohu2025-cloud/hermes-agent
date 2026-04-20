---
sidebar_position: 8
title: "上下文文件 (Context Files)"
description: "项目上下文文件 — .hermes.md, AGENTS.md, CLAUDE.md, 全局 SOUL.md, 以及 .cursorrules — 自动注入到每一次对话中"
---

# 上下文文件 (Context Files) {#context-files}

Hermes Agent 会自动发现并加载决定其行为方式的上下文文件。其中一些是项目本地文件，从你的工作目录中发现。`SOUL.md` 现在是 Hermes 实例的全局文件，仅从 `HERMES_HOME` 加载。

## 支持的上下文文件 {#supported-context-files}

| 文件 | 用途 | 发现方式 |
|------|---------|-----------| 
| **.hermes.md** / **HERMES.md** | 项目指令（最高优先级） | 向上追溯至 git 根目录 |
| **AGENTS.md** | 项目指令、规范、架构 | 启动时的 CWD + 逐步发现子目录 |
| **CLAUDE.md** | Claude Code 上下文文件（同样可识别） | 启动时的 CWD + 逐步发现子目录 |
| **SOUL.md** | 此 Hermes 实例的全局性格和语气定制 | 仅限 `HERMES_HOME/SOUL.md` |
| **.cursorrules** | Cursor IDE 编码规范 | 仅限 CWD |
| **.cursor/rules/*.mdc** | Cursor IDE 规则模块 | 仅限 CWD |

:::info 优先级系统
每个会话仅加载 **一种** 项目上下文类型（先匹配者优先）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。**SOUL.md** 始终作为 Agent 身份（插槽 #1）独立加载。
:::

## AGENTS.md {#agents-md}

`AGENTS.md` 是主要的项目上下文文件。它告诉 Agent 你的项目是如何构成的、需要遵循哪些规范以及任何特殊指令。

### 逐步子目录发现 {#progressive-subdirectory-discovery}
<a id="priority-system"></a>

在会话开始时，Hermes 会将工作目录中的 `AGENTS.md` 加载到系统提示词中。当 Agent 在会话期间进入子目录时（通过 `read_file`、`terminal`、`search_files` 等工具），它会**逐步发现**这些目录中的上下文文件，并在它们变得相关的时刻将其注入到对话中。

```
my-project/
├── AGENTS.md              ← 启动时加载（系统提示词）
├── frontend/
│   └── AGENTS.md          ← 当 Agent 读取 frontend/ 文件时发现
├── backend/
│   └── AGENTS.md          ← 当 Agent 读取 backend/ 文件时发现
└── shared/
    └── AGENTS.md          ← 当 Agent 读取 shared/ 文件时发现
```

这种方法相比于启动时加载所有内容有两个优势：
- **避免系统提示词膨胀** — 子目录提示仅在需要时出现
- **保持提示词缓存** — 系统提示词在多轮对话中保持稳定

每个子目录在每个会话中最多检查一次。发现过程还会向上追溯父目录，因此读取 `backend/src/main.py` 会发现 `backend/AGENTS.md`，即使 `backend/src/` 本身没有上下文文件。

:::info
子目录上下文文件会经过与启动上下文文件相同的 [安全扫描](#security-prompt-injection-protection)。恶意文件将被拦截。
:::

### AGENTS.md 示例 {#example-agents-md}

```markdown
# 项目上下文 (Project Context)

这是一个使用 Python FastAPI 后端的 Next.js 14 Web 应用程序。

## 架构
- 前端：Next.js 14，使用 App Router，位于 `/frontend`
- 后端：FastAPI，位于 `/backend`，使用 SQLAlchemy ORM
- 数据库：PostgreSQL 16
- 部署：在 Hetzner VPS 上使用 Docker Compose

## 规范
- 所有前端代码使用 TypeScript 严格模式
- Python 代码遵循 PEP 8，随处使用类型提示 (type hints)
- 所有 API 端点返回 JSON，格式为 `{data, error, meta}`
- 测试文件放在 `__tests__/` 目录（前端）或 `tests/`（后端）

## 重要注意事项
- 永远不要直接修改迁移文件 — 请使用 Alembic 命令
- `.env.local` 文件包含真实的 API 密钥，请勿提交
- 前端端口为 3000，后端为 8000，数据库为 5432
```

## SOUL.md {#soul-md}

`SOUL.md` 控制 Agent 的性格、语气和沟通风格。详见 [性格 (Personality)](/user-guide/features/personality) 页面。

**位置：**

- `~/.hermes/SOUL.md`
- 或者如果你使用自定义主目录运行 Hermes，则为 `$HERMES_HOME/SOUL.md`

重要细节：

- 如果尚不存在 `SOUL.md`，Hermes 会自动生成一个默认文件
- Hermes 仅从 `HERMES_HOME` 加载 `SOUL.md`
- Hermes 不会在工作目录中探测 `SOUL.md`
- 如果文件为空，则不会向提示词中添加任何来自 `SOUL.md` 的内容
- 如果文件有内容，内容将在扫描和截断后原样注入

## .cursorrules {#cursorrules}

Hermes 兼容 Cursor IDE 的 `.cursorrules` 文件和 `.cursor/rules/*.mdc` 规则模块。如果你的项目根目录中存在这些文件，且未找到更高优先级的上下文文件（`.hermes.md`、`AGENTS.md` 或 `CLAUDE.md`），它们将被加载为项目上下文。

这意味着在使用 Hermes 时，你现有的 Cursor 规范会自动生效。

## 上下文文件是如何加载的 {#how-context-files-are-loaded}

### 启动时（系统提示词） {#at-startup-system-prompt}

上下文文件由 `agent/prompt_builder.py` 中的 `build_context_files_prompt()` 加载：

1. **扫描工作目录** — 检查 `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`（先匹配者优先）
2. **读取内容** — 每个文件以 UTF-8 文本形式读取
3. **安全扫描** — 检查内容是否存在提示词注入 (prompt injection) 模式
4. **截断** — 超过 20,000 字符的文件将被首尾截断（保留 70% 头部，20% 尾部，中间加标记）
5. **组装** — 所有部分合并在 `# Project Context` 标题下
6. **注入** — 组装后的内容被添加到系统提示词中

### 会话期间（逐步发现） {#during-the-session-progressive-discovery}

`agent/subdirectory_hints.py` 中的 `SubdirectoryHintTracker` 监视工具调用的文件路径参数：

1. **路径提取** — 每次工具调用后，从参数（`path`、`workdir`、shell 命令）中提取文件路径
2. **祖先追溯** — 检查该目录及最多 5 层父目录（在已访问过的目录处停止）
3. **提示加载** — 如果发现 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules`，则将其加载（每个目录先匹配者优先）
4. **安全扫描** — 与启动文件相同的提示词注入扫描
5. **截断** — 每个文件上限为 8,000 字符
6. **注入** — 附加到工具结果中，使模型能自然地在上下文中看到它

最终的提示词部分大致如下：

```text
# Project Context

The following project context files have been loaded and should be followed:

## AGENTS.md

[此处为你的 AGENTS.md 内容]

## .cursorrules

[此处为你的 .cursorrules 内容]

[此处为你的 SOUL.md 内容]
```

请注意，SOUL 内容是直接插入的，没有额外的包装文本。

## 安全：提示词注入保护 {#security-prompt-injection-protection}

所有上下文文件在包含之前都会经过潜在提示词注入扫描。扫描器检查以下内容：

- **指令覆盖尝试**："ignore previous instructions"（忽略之前的指令）、"disregard your rules"（无视你的规则）
- **欺骗模式**："do not tell the user"（不要告诉用户）
- **系统提示词覆盖**："system prompt override"
- **隐藏的 HTML 注释**：`<!-- ignore instructions -->`
- **隐藏的 div 元素**：`<div style="display:none">`
- **凭据窃取**：`curl ... $API_KEY`
- **秘密文件访问**：`cat .env`、`cat credentials`
- **不可见字符**：零宽空格、双向覆盖 (bidirectional overrides)、词语连接符

如果检测到任何威胁模式，该文件将被拦截：

```
[BLOCKED: AGENTS.md contained potential prompt injection (prompt_injection). Content not loaded.]
```

:::warning
此扫描器可以防御常见的注入模式，但不能替代对共享仓库中上下文文件的审查。在非你本人创建的项目中，请务必验证 AGENTS.md 的内容。
:::

## 大小限制 {#size-limits}

| 限制项 | 数值 |
|-------|-------|
| 每个文件最大字符数 | 20,000 (约 7,000 tokens) |
| 头部截断比例 | 70% |
| 尾部截断比例 | 20% |
| 截断标记 | 10% (显示字符数并建议使用文件工具) |

当文件超过 20,000 字符时，截断消息如下：

```
[...truncated AGENTS.md: kept 14000+4000 of 25000 chars. Use file tools to read the full file.]
```

## 高效编写上下文文件的技巧 {#tips-for-effective-context-files}

:::tip AGENTS.md 最佳实践
<a id="best-practices-for-agents-md"></a>
1. **保持简洁** — 尽量控制在 20K 字符以内；Agent 每一轮都会阅读它
2. **使用标题结构化** — 使用 `##` 分段说明架构、规范、重要事项
3. **包含具体示例** — 展示首选的代码模式、API 形状、命名规范
4. **提及“不要做什么”** — 例如“永远不要直接修改迁移文件”
5. **列出关键路径和端口** — Agent 会在终端命令中使用这些信息
6. **随项目演进更新** — 过时的上下文比没有上下文更糟糕
:::
### 按子目录配置上下文 {#per-subdirectory-context}

对于 Monorepo（单体大仓库），可以将特定于子目录的指令放在嵌套的 `AGENTS.md` 文件中：

```markdown
<!-- frontend/AGENTS.md -->
# Frontend Context

- 使用 `pnpm` 而不是 `npm` 进行包管理
- 组件放在 `src/components/`，页面放在 `src/app/`
- 使用 Tailwind CSS，严禁使用内联样式
- 使用 `pnpm test` 运行测试
```

```markdown
<!-- backend/AGENTS.md -->
# Backend Context

- 使用 `poetry` 进行依赖管理
- 使用 `poetry run uvicorn main:app --reload` 运行开发服务器
- 所有端点都需要 OpenAPI docstrings
- 数据库模型位于 `models/`，Schema 位于 `schemas/`
```
