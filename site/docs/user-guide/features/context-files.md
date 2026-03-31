---
sidebar_position: 8
title: "上下文文件"
description: "项目上下文文件 — .hermes.md、AGENTS.md、CLAUDE.md、全局 SOUL.md 和 .cursorrules — 会自动注入到每次对话中"
---

# 上下文文件

Hermes Agent 会自动发现并加载用于塑造其行为的上下文文件。有些是项目本地的，从你的工作目录中发现。`SOUL.md` 现在对 Hermes 实例是全局的，并且只从 `HERMES_HOME` 加载。

## 支持的上下文文件

| 文件 | 用途 | 发现方式 |
|------|---------|-----------|
| **.hermes.md** / **HERMES.md** | 项目指令（最高优先级） | 向上遍历到 git 根目录 |
| **AGENTS.md** | 项目指令、约定、架构 | 递归（遍历子目录） |
| **CLAUDE.md** | Claude Code 上下文文件（也会被检测） | 仅当前工作目录 |
| **SOUL.md** | 此 Hermes 实例的全局个性和语气自定义 | 仅 `HERMES_HOME/SOUL.md` |
| **.cursorrules** | Cursor IDE 编码约定 | 仅当前工作目录 |
| **.cursor/rules/*.mdc** | Cursor IDE 规则模块 | 仅当前工作目录 |

:::info 优先级系统
每个会话只加载**一种**项目上下文类型（首次匹配优先）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。**SOUL.md** 总是作为代理身份（槽位 #1）独立加载。
:::

## AGENTS.md

`AGENTS.md` 是主要的项目上下文文件。它告诉代理你的项目结构如何、应遵循哪些约定以及任何特殊指令。

### 分层发现

Hermes 从工作目录开始遍历目录树，并加载找到的**所有** `AGENTS.md` 文件，按深度排序。这支持 monorepo 风格的设置：

```
my-project/
├── AGENTS.md              ← 顶级项目上下文
├── frontend/
│   └── AGENTS.md          ← 前端特定指令
├── backend/
│   └── AGENTS.md          ← 后端特定指令
└── shared/
    └── AGENTS.md          ← 共享库约定
```

所有四个文件会被拼接成一个单独的上下文块，并带有相对路径标题。

:::info
遍历过程中跳过的目录：以 `.` 开头的目录、`node_modules`、`__pycache__`、`venv`、`.venv`。
:::

### AGENTS.md 示例

```markdown
# 项目上下文

这是一个使用 Python FastAPI 后端的 Next.js 14 Web 应用程序。

## 架构
- 前端：Next.js 14，使用 App Router，位于 `/frontend`
- 后端：FastAPI，位于 `/backend`，使用 SQLAlchemy ORM
- 数据库：PostgreSQL 16
- 部署：在 Hetzner VPS 上使用 Docker Compose

## 约定
- 所有前端代码使用 TypeScript 严格模式
- Python 代码遵循 PEP 8，到处使用类型提示
- 所有 API 端点返回 JSON，格式为 `{data, error, meta}`
- 测试放在 `__tests__/` 目录（前端）或 `tests/`（后端）

## 重要说明
- 切勿直接修改迁移文件 — 使用 Alembic 命令
- `.env.local` 文件包含真实的 API 密钥，不要提交它
- 前端端口是 3000，后端是 8000，数据库是 5432
```

## SOUL.md

`SOUL.md` 控制代理的个性、语气和沟通风格。完整细节请参阅[个性](/docs/user-guide/features/personality)页面。

**位置：**

- `~/.hermes/SOUL.md`
- 或者，如果你使用自定义主目录运行 Hermes，则为 `$HERMES_HOME/SOUL.md`

重要细节：

- 如果 `SOUL.md` 尚不存在，Hermes 会自动植入一个默认的 `SOUL.md`
- Hermes 只从 `HERMES_HOME` 加载 `SOUL.md`
- Hermes 不会在工作目录中探测 `SOUL.md`
- 如果文件为空，则不会向提示词添加任何来自 `SOUL.md` 的内容
- 如果文件有内容，内容会在扫描和截断后逐字注入

## .cursorrules

Hermes 兼容 Cursor IDE 的 `.cursorrules` 文件和 `.cursor/rules/*.mdc` 规则模块。如果这些文件存在于你的项目根目录，并且没有找到更高优先级的上下文文件（`.hermes.md`、`AGENTS.md` 或 `CLAUDE.md`），它们将作为项目上下文被加载。

这意味着你现有的 Cursor 约定在使用 Hermes 时会自动应用。

## 上下文文件如何加载

上下文文件由 `agent/prompt_builder.py` 中的 `build_context_files_prompt()` 加载：

1.  **会话开始时** — 函数扫描工作目录
2.  **读取内容** — 每个文件被读取为 UTF-8 文本
3.  **安全扫描** — 内容被检查是否存在提示词注入模式
4.  **截断** — 超过 20,000 个字符的文件会被头/尾截断（70% 头部，20% 尾部，中间有标记）
5.  **组装** — 所有部分在 `# 项目上下文` 标题下组合
6.  **注入** — 组装好的内容被添加到系统提示词中

最终的提示词部分大致如下：

```text
# 项目上下文

以下项目上下文文件已被加载，应予以遵循：

## AGENTS.md

[你的 AGENTS.md 内容在这里]

## .cursorrules

[你的 .cursorrules 内容在这里]

[你的 SOUL.md 内容在这里]
```

注意，SOUL 内容是直接插入的，没有额外的包装文本。

## 安全：提示词注入防护

所有上下文文件在被包含之前都会扫描潜在的提示词注入。扫描器检查：

-   **指令覆盖尝试**："ignore previous instructions"、"disregard your rules"
-   **欺骗模式**："do not tell the user"
-   **系统提示词覆盖**："system prompt override"
-   **隐藏的 HTML 注释**：`<!-- ignore instructions -->`
-   **隐藏的 div 元素**：`<div style="display:none">`
-   **凭据泄露**：`curl ... $API_KEY`
-   **秘密文件访问**：`cat .env`、`cat credentials`
-   **不可见字符**：零宽空格、双向覆盖符、连接符

如果检测到任何威胁模式，文件会被阻止：

```
[已阻止：AGENTS.md 包含潜在的提示词注入 (prompt_injection)。内容未加载。]
```

:::warning
此扫描器可防护常见的注入模式，但它不能替代审查共享仓库中的上下文文件。对于非你本人创建的项目，请务必验证 AGENTS.md 的内容。
:::

## 大小限制

| 限制 | 值 |
|-------|-------|
| 每个文件最大字符数 | 20,000 (~7,000 tokens) |
| 头部截断比例 | 70% |
| 尾部截断比例 | 20% |
| 截断标记 | 10%（显示字符数并建议使用文件工具） |

当文件超过 20,000 个字符时，截断消息显示为：

```
[...已截断 AGENTS.md：保留了 25000 个字符中的 14000+4000 个。使用文件工具读取完整文件。]
```

## 高效上下文文件的技巧

:::tip AGENTS.md 最佳实践
1.  **保持简洁** — 远低于 20K 字符；代理每轮都会读取它
2.  **使用标题结构化** — 使用 `##` 部分表示架构、约定、重要说明
3.  **包含具体示例** — 展示首选的代码模式、API 结构、命名约定
4.  **提及不应做的事** — "切勿直接修改迁移文件"
5.  **列出关键路径和端口** — 代理在终端命令中使用这些信息
6.  **随项目发展而更新** — 过时的上下文比没有上下文更糟
:::

### 每个子目录的上下文

对于 monorepo，将子目录特定的指令放在嵌套的 AGENTS.md 文件中：

```markdown
<!-- frontend/AGENTS.md -->
# 前端上下文

- 使用 `pnpm` 而非 `npm` 进行包管理
- 组件放在 `src/components/`，页面放在 `src/app/`
- 使用 Tailwind CSS，切勿使用内联样式
- 使用 `pnpm test` 运行测试
```

```markdown
<!-- backend/AGENTS.md -->
# 后端上下文

- 使用 `poetry` 进行依赖管理
- 使用 `poetry run uvicorn main:app --reload` 运行开发服务器
- 所有端点都需要 OpenAPI 文档字符串
- 数据库模型在 `models/` 中，模式在 `schemas/` 中
```
