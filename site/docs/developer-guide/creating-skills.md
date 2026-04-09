---
sidebar_position: 3
title: "创建 Skill"
description: "如何为 Hermes Agent 创建 Skill —— SKILL.md 格式、指南及发布"
---

# 创建 Skill

Skill 是为 Hermes Agent 添加新能力的首选方式。它们比 Tool（工具）更容易创建，不需要对 Agent 进行代码修改，并且可以与社区分享。

## 应该是 Skill 还是 Tool？

在以下情况下将其设为 **Skill**：
- 该能力可以通过指令 + Shell 命令 + 现有工具来表达。
- 它封装了一个外部 CLI 或 API，Agent 可以通过 `terminal` 或 `web_extract` 调用。
- 它不需要在 Agent 内部集成自定义 Python 逻辑或 API 密钥管理。
- 示例：arXiv 搜索、git 工作流、Docker 管理、PDF 处理、通过 CLI 工具发送邮件。

在以下情况下将其设为 **Tool**：
- 它需要与 API 密钥、认证流程或多组件配置进行端到端集成。
- 它需要自定义处理逻辑，且每次必须精确执行。
- 它处理二进制数据、流式传输或实时事件。
- 示例：浏览器自动化、TTS（语音合成）、视觉分析。

## Skill 目录结构

内置 Skill 存放在 `skills/` 目录下，按类别组织。官方可选 Skill 在 `optional-skills/` 中使用相同的结构：

```text
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md              # 必需：主要指令
│       └── scripts/              # 可选：辅助脚本
│           └── search_arxiv.py
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── ...
```

## SKILL.md 格式

```markdown
---
name: my-skill
description: 简短描述（显示在 Skill 搜索结果中）
version: 1.0.0
author: Your Name
license: MIT
platforms: [macos, linux]          # 可选 — 限制在特定的操作系统平台
                                   #   有效值：macos, linux, windows
                                   #   省略则在所有平台加载（默认）
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    requires_toolsets: [web]            # 可选 — 仅当这些 toolsets 激活时显示
    requires_tools: [web_search]        # 可选 — 仅当这些 tools 可用时显示
    fallback_for_toolsets: [browser]    # 可选 — 当这些 toolsets 激活时隐藏
    fallback_for_tools: [browser_navigate]  # 可选 — 当这些 tools 存在时隐藏
    config:                              # 可选 — Skill 需要的 config.yaml 设置
      - key: my.setting
        description: "此设置控制的内容"
        default: "sensible-default"
        prompt: "设置时的显示提示"
required_environment_variables:          # 可选 — Skill 需要的环境变量
  - name: MY_API_KEY
    prompt: "输入你的 API 密钥"
    help: "在 https://example.com 获取"
    required_for: "API 访问"
---

# Skill 标题

简短介绍。

## When to Use
触发条件 — Agent 应该在什么时候加载此 Skill？

## Quick Reference
常用命令或 API 调用的表格。

## Procedure
Agent 遵循的逐步指令。

## Pitfalls
已知的失败模式及处理方法。

## Verification
Agent 如何确认操作已成功。
```

### 平台特定 Skill

Skill 可以使用 `platforms` 字段将自己限制在特定的操作系统：

```yaml
platforms: [macos]            # 仅限 macOS (例如 iMessage, Apple Reminders)
platforms: [macos, linux]     # macOS 和 Linux
platforms: [windows]          # 仅限 Windows
```

设置后，该 Skill 在不兼容的平台上会自动从系统提示词、`skills_list()` 和斜杠命令中隐藏。如果省略或为空，则 Skill 在所有平台上加载（向后兼容）。

### 条件式 Skill 激活

Skill 可以声明对特定 Tool 或 Toolset 的依赖。这控制了该 Skill 是否出现在给定会话的系统提示词中。

```yaml
metadata:
  hermes:
    requires_toolsets: [web]           # 如果 web toolset 未激活则隐藏
    requires_tools: [web_search]       # 如果 web_search tool 不可用则隐藏
    fallback_for_toolsets: [browser]   # 如果 browser toolset 已激活则隐藏
    fallback_for_tools: [browser_navigate]  # 如果 browser_navigate 可用则隐藏
```

| 字段 | 行为 |
|-------|----------|
| `requires_toolsets` | 当列表中的**任何** toolset 不可用时，Skill 会被**隐藏** |
| `requires_tools` | 当列表中的**任何** tool 不可用时，Skill 会被**隐藏** |
| `fallback_for_toolsets` | 当列表中的**任何** toolset 可用时，Skill 会被**隐藏** |
| `fallback_for_tools` | 当列表中的**任何** tool 可用时，Skill 会被**隐藏** |

**`fallback_for_*` 的使用场景：** 创建一个在主要 Tool 不可用时作为替代方案的 Skill。例如，一个带有 `fallback_for_tools: [web_search]` 的 `duckduckgo-search` Skill 仅在未配置 Web 搜索工具（需要 API 密钥）时显示。

**`requires_*` 的使用场景：** 创建一个仅在某些 Tool 存在时才有意义的 Skill。例如，一个带有 `requires_toolsets: [web]` 的网页抓取工作流 Skill 在禁用 Web 工具时不会干扰提示词。

### 环境变量要求

Skill 可以声明它们需要的环境变量。当通过 `skill_view` 加载 Skill 时，其要求的变量会自动注册，以便透传到沙箱执行环境（terminal, execute_code）中。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: "Tenor API key"               # 提示用户时显示
    help: "在 https://tenor.com 获取密钥"  # 帮助文本或 URL
    required_for: "GIF 搜索功能"           # 哪个功能需要此变量
```

每个条目支持：
- `name` (必需) — 环境变量名称
- `prompt` (可选) — 向用户询问值时的提示文本
- `help` (可选) — 获取该值的帮助文本或 URL
- `required_for` (可选) — 描述哪个功能需要此变量

用户也可以在 `config.yaml` 中手动配置透传变量：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_VAR
    - ANOTHER_VAR
```

参考 `skills/apple/` 获取仅限 macOS 的 Skill 示例。

## 加载时的安全设置

当 Skill 需要 API 密钥或 Token 时，请使用 `required_environment_variables`。缺失这些值**不会**在搜索中隐藏该 Skill。相反，当 Skill 在本地 CLI 中加载时，Hermes 会安全地提示用户输入。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: 从 https://developers.google.com/tenor 获取密钥
    required_for: 完整功能
```

用户可以跳过设置并继续加载 Skill。Hermes 永远不会向模型暴露原始机密值。Gateway 和消息会话会显示本地设置指南，而不是在线收集机密信息。

:::tip 沙箱透传
当你的 Skill 被加载时，任何已设置的声明变量 `required_environment_variables` 都会**自动透传**到 `execute_code` 和 `terminal` 沙箱中 —— 包括 Docker 和 Modal 等远程后端。你的 Skill 脚本可以直接访问 `$TENOR_API_KEY`（或 Python 中的 `os.environ["TENOR_API_KEY"]`），无需用户进行额外配置。详见 [环境变量透传](/user-guide/security#environment-variable-passthrough)。
:::

旧版的 `prerequisites.env_vars` 仍作为向后兼容的别名受支持。

### 配置设置 (config.yaml) {#config-settings-configyaml}

Skill 可以声明非机密设置，这些设置存储在 `config.yaml` 的 `skills.config` 命名空间下。与环境变量（存储在 `.env` 中的机密信息）不同，配置设置用于路径、偏好和其他非敏感值。

```yaml
metadata:
  hermes:
    config:
      - key: wiki.path
        description: LLM Wiki 知识库目录路径
        default: "~/wiki"
        prompt: Wiki 目录路径
      - key: wiki.domain
        description: Wiki 涵盖的领域
        default: ""
        prompt: Wiki 领域 (例如 AI/ML 研究)
```

每个条目支持：
- `key` (必需) — 设置的点路径（例如 `wiki.path`）
- `description` (必需) — 解释该设置控制的内容
- `default` (可选) — 如果用户未配置时的默认值
- `prompt` (可选) — 在执行 `hermes config migrate` 时显示的提示文本；若未提供则回退到 `description`
**工作原理：**

1. **存储：** 配置值会被写入 `config.yaml` 中的 `skills.config.<key>` 路径下：
   ```yaml
   skills:
     config:
       wiki:
         path: ~/my-research
   ```

2. **发现：** `hermes config migrate` 会扫描所有已启用的技能，发现未配置的设置并提示用户。这些设置也会出现在 `hermes config show` 的 "Skill Settings" 栏目下。

3. **运行时注入：** 当技能加载时，其配置值会被解析并附加到技能消息中：
   ```
   [Skill config (from ~/.hermes/config.yaml):
     wiki.path = /home/user/my-research
   ]
   ```
   Agent 可以直接看到配置好的值，而无需自行读取 `config.yaml`。

4. **手动设置：** 用户也可以直接设置这些值：
   ```bash
   hermes config set skills.config.wiki.path ~/my-wiki
   ```

:::tip 应该使用哪种方式
对于 API 密钥、Token 和其他**敏感信息**（存储在 `~/.hermes/.env` 中，永远不会展示给模型），请使用 `required_environment_variables`。对于**路径、偏好设置和非敏感设置**（存储在 `config.yaml` 中，在 config show 中可见），请使用 `config`。
:::

### 凭据文件要求（OAuth Token 等）

使用 OAuth 或基于文件的凭据的技能可以声明需要挂载到远程沙箱中的文件。这适用于以**文件**形式存储的凭据（而非环境变量）—— 通常是由设置脚本生成的 OAuth Token 文件。

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials
```

每个条目支持：
- `path`（必填）— 相对于 `~/.hermes/` 的文件路径
- `description`（可选）— 说明该文件是什么以及它是如何创建的

加载时，Hermes 会检查这些文件是否存在。缺失文件会触发 `setup_needed`。存在的文件会自动：
- 以只读绑定挂载（bind mounts）的方式**挂载到 Docker** 容器中
- **同步到 Modal** 沙箱中（在创建时以及每个命令执行前同步，因此会话中途的 OAuth 也能正常工作）
- 在**本地（local）**后端直接可用，无需特殊处理

:::tip 应该使用哪种方式
对于简单的 API 密钥和 Token（存储在 `~/.hermes/.env` 中的字符串），请使用 `required_environment_variables`。对于 OAuth Token 文件、客户端密钥（client secrets）、服务账号 JSON、证书或磁盘上的任何凭据文件，请使用 `required_credential_files`。
:::

请参考 `skills/productivity/google-workspace/SKILL.md` 查看同时使用这两者的完整示例。

## 技能准则

### 无外部依赖

优先使用 Python 标准库、curl 和现有的 Hermes 工具（`web_extract`、`terminal`、`read_file`）。如果必须使用某个依赖项，请在技能文档中说明安装步骤。

### 渐进式披露

将最常用的工作流放在最前面。边缘情况和高级用法放在底部。这可以降低常用任务的 Token 消耗。

### 包含辅助脚本

对于 XML/JSON 解析或复杂的逻辑，请在 `scripts/` 中包含辅助脚本 —— 不要指望 LLM 每次都能在行内写出解析器。

### 进行测试

运行技能并验证 Agent 是否正确遵循了指令：

```bash
hermes chat --toolsets skills -q "Use the X skill to do Y"
```

## 技能应该放在哪里？

内置技能（位于 `skills/` 目录下）随每个 Hermes 版本一同发布。它们应该是**对大多数用户都有广泛用途**的：

- 文档处理、网页调研、常用开发工作流、系统管理
- 被广泛人群定期使用

如果你的技能是官方提供的且很有用，但并非普遍需要（例如：付费服务集成、带有沉重依赖项的工具），请将其放在 **`optional-skills/`** 中 —— 它随仓库一同提供，可以通过 `hermes skills browse` 发现（标记为 "official"），并带有内置信任进行安装。

如果你的技能是专业化的、社区贡献的或小众的，它更适合放在 **Skills Hub** —— 将其上传到注册表并通过 `hermes skills install` 分享。

## 发布技能

### 发布到 Skills Hub

```bash
hermes skills publish skills/my-skill --to github --repo owner/repo
```

### 发布到自定义仓库

将你的仓库添加为 tap：

```bash
hermes skills tap add owner/repo
```

之后用户就可以从你的仓库中搜索并安装技能。

## 安全扫描

所有通过 Hub 安装的技能都会经过安全扫描器，检查是否存在以下情况：

- 数据外泄模式
- Prompt 注入尝试
- 破坏性命令
- Shell 注入

信任等级：
- `builtin` — 随 Hermes 内置（始终信任）
- `official` — 来自仓库中的 `optional-skills/`（内置信任，无第三方警告）
- `trusted` — 来自 openai/skills, anthropics/skills
- `community` — 非危险发现可以使用 `--force` 覆盖；判定为 `dangerous`（危险）的项将保持阻断状态

Hermes 现在可以从多个外部发现模型中获取第三方技能：
- 直接使用 GitHub 标识符（例如 `openai/skills/k8s`）
- `skills.sh` 标识符（例如 `skills-sh/vercel-labs/json-render/json-render-react`）
- 通过 `/.well-known/skills/index.json` 提供的已知端点

如果你希望你的技能在没有 GitHub 特定安装程序的情况下也能被发现，可以考虑除了在仓库或市场发布外，再通过已知端点（well-known endpoint）提供服务。
