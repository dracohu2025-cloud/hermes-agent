---
sidebar_position: 2
title: "技能系统"
description: "按需知识文档——渐进式披露、Agent 管理的技能以及技能中心"
---

# 技能系统 {#skills-system}

技能是 Agent 在需要时可以按需加载的知识文档。它们遵循**渐进式披露**模式，以最小化 token 使用量，并且兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。

所有技能都存放在 **`~/.hermes/skills/`** —— 这是主目录和数据源。首次安装时，内置技能会从仓库复制过来。通过技能中心安装以及 Agent 自己创建的技能也会放在这里。Agent 可以修改或删除任何技能。

你也可以让 Hermes 指向**外部技能目录** —— 这些额外的文件夹会与本地目录一起被扫描。请参见下方的[外部技能目录](#external-skill-directories)。

另请参阅：

- [内置技能目录](/reference/skills-catalog)
- [官方可选技能目录](/reference/optional-skills-catalog)

## 使用技能 {#using-skills}

每个已安装的技能都会自动作为斜杠命令可用：

```bash
# 在 CLI 或任何消息平台中：
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor
/plan design a rollout for migrating our auth provider

# 仅输入技能名称即可加载它，并让 Agent 询问你需要什么：
/excalidraw
```

内置的 `plan` 技能是一个很好的例子。运行 `/plan [request]` 会加载该技能的指令，告诉 Hermes 在需要时检查上下文，编写一个 Markdown 实现计划而不是直接执行任务，并将结果保存在相对于当前工作区/后端工作目录的 `.hermes/plans/` 下。

你也可以通过自然对话与技能交互：

```bash
hermes chat --toolsets skills -q "What skills do you have?"
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

## 渐进式披露 {#progressive-disclosure}

技能使用一种 token 高效的加载模式：

```
Level 0: skills_list()           → [{name, description, category}, ...]   (~3k tokens)
Level 1: skill_view(name)        → Full content + metadata       (varies)
Level 2: skill_view(name, path)  → Specific reference file       (varies)
```

Agent 只在真正需要时才加载完整的技能内容。

## SKILL.md 格式 {#skill-md-format}

```markdown
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
platforms: [macos, linux]     # 可选 —— 限制在特定操作系统平台
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]    # 可选 —— 条件激活（见下文）
    requires_toolsets: [terminal]   # 可选 —— 条件激活（见下文）
    config:                          # 可选 —— config.yaml 设置
      - key: my.setting
        description: "What this controls"
        default: "value"
        prompt: "Prompt for setup"
---

# 技能标题

## 何时使用
该技能的触发条件。

## 步骤
1. 第一步
2. 第二步

## 常见陷阱
- 已知的失败模式及修复方法

## 验证
如何确认它已生效。
```

### 平台特定技能 {#platform-specific-skills}
Skills 可以使用 `platforms` 字段限制自身仅在特定操作系统上运行：

| 值 | 匹配 |
|-------|---------|
| `macos` | macOS (Darwin) |
| `linux` | Linux |
| `windows` | Windows |

```yaml
platforms: [macos]            # 仅 macOS（例如 iMessage、Apple Reminders、FindMy）
platforms: [macos, linux]     # macOS 和 Linux
```

设置后，该 skill 在不兼容的平台上会自动从系统提示、`skills_list()` 和斜杠命令中隐藏。如果省略该字段，则 skill 在所有平台上加载。

### 条件激活（回退 Skills） {#conditional-activation-fallback-skills}

Skills 可以根据当前会话中可用的工具自动显示或隐藏自身。这对于**回退 skills** 最为有用——即仅在高级工具不可用时才出现的免费或本地替代方案。

```yaml
metadata:
  hermes:
    fallback_for_toolsets: [web]      # 仅当这些工具集不可用时显示
    requires_toolsets: [terminal]     # 仅当这些工具集可用时显示
    fallback_for_tools: [web_search]  # 仅当这些特定工具不可用时显示
    requires_tools: [terminal]        # 仅当这些特定工具可用时显示
```

| 字段 | 行为 |
|-------|----------|
| `fallback_for_toolsets` | 当列出的工具集可用时，skill **隐藏**；当它们缺失时显示。 |
| `fallback_for_tools` | 同上，但检查的是单个工具而非工具集。 |
| `requires_toolsets` | 当列出的工具集不可用时，skill **隐藏**；当它们存在时显示。 |
| `requires_tools` | 同上，但检查的是单个工具。 |

**示例：** 内置的 `duckduckgo-search` skill 使用了 `fallback_for_toolsets: [web]`。当你设置了 `FIRECRAWL_API_KEY` 时，web 工具集可用，agent 会使用 `web_search`——DuckDuckGo skill 保持隐藏。如果 API 密钥缺失，web 工具集不可用，DuckDuckGo skill 会自动作为回退出现。

没有任何条件字段的 skills 行为与之前完全一致——它们始终显示。

## 加载时的安全设置 {#secure-setup-on-load}

Skills 可以声明所需的环境变量，而不会从发现中消失：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API 密钥
    help: 从 https://developers.google.com/tenor 获取密钥
    required_for: 完整功能
```

当遇到缺失的值时，Hermes 仅在本地 CLI 中实际加载该 skill 时才会安全地询问。你可以跳过设置并继续使用该 skill。消息界面永远不会在聊天中询问密钥——它们会告诉你改用 `hermes setup` 或 `~/.hermes/.env` 在本地设置。

一旦设置，声明的环境变量会自动**传递**给 `execute_code` 和 `terminal` 沙箱——该 skill 的脚本可以直接使用 `$TENOR_API_KEY`。对于非 skill 的环境变量，请使用 `terminal.env_passthrough` 配置选项。详情请参阅[环境变量传递](/user-guide/security#environment-variable-passthrough)。
### 技能配置设置 {#skill-config-settings}

技能还可以在 `config.yaml` 中声明非机密配置设置（路径、偏好）：

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: 插件数据目录的路径
        default: "~/myplugin-data"
        prompt: 插件数据目录路径
```

这些设置存储在 config.yaml 的 `skills.config` 下。`hermes config migrate` 会提示未配置的设置，`hermes config show` 会显示它们。当技能加载时，其解析后的配置值会被注入到上下文中，这样 Agent 就能自动知道已配置的值。

详情请参阅 [技能设置](/user-guide/configuration#skill-settings) 和 [创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

## 技能目录结构 {#skill-directory-structure}

```text
~/.hermes/skills/                  # 唯一真实来源
├── mlops/                         # 分类目录
│   ├── axolotl/
│   │   ├── SKILL.md               # 主指令（必需）
│   │   ├── references/            # 附加文档
│   │   ├── templates/             # 输出格式
│   │   ├── scripts/               # 可从技能调用的辅助脚本
│   │   └── assets/                # 补充文件
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # Agent 创建的技能
│       ├── SKILL.md
│       └── references/
├── .hub/                          # Skills Hub 状态
│   ├── lock.json
│   ├── quarantine/
│   └── audit.log
└── .bundled_manifest              # 跟踪已预装的捆绑技能
```

## 外部技能目录 {#external-skill-directories}

如果你在 Hermes 之外维护技能——例如，一个由多个 AI 工具共享的 `~/.agents/skills/` 目录——你可以告诉 Hermes 也扫描这些目录。

在 `~/.hermes/config.yaml` 的 `skills` 部分添加 `external_dirs`：

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills
```

路径支持 `~` 展开和 `${VAR}` 环境变量替换。

### 工作原理 {#how-it-works}

- **只读**：外部目录仅用于技能发现。当 Agent 创建或编辑技能时，始终写入 `~/.hermes/skills/`。
- **本地优先**：如果本地目录和外部目录中存在同名的技能，则本地版本优先。
- **完全集成**：外部技能会出现在系统提示索引、`skills_list`、`skill_view` 以及 `/skill-name` 斜杠命令中——与本地技能无异。
- **不存在的路径会被静默跳过**：如果配置的目录不存在，Hermes 会忽略它而不报错。这对于某些可能不在每台机器上都存在的可选共享目录很有用。

### 示例 {#example}

```text
~/.hermes/skills/               # 本地（主目录，可读写）
├── devops/deploy-k8s/
│   └── SKILL.md
└── mlops/axolotl/
    └── SKILL.md

~/.agents/skills/               # 外部（只读，共享）
├── my-custom-workflow/
│   └── SKILL.md
└── team-conventions/
    └── SKILL.md
```
所有四个技能都会出现在你的技能索引中。如果你在本地创建了一个名为 `my-custom-workflow` 的新技能，它会覆盖外部版本。

<a id="agent-managed-skills-skillmanage-tool"></a>
## Agent 管理的技能（skill_manage 工具） {#agent-managed-skills-skill_manage-tool}

Agent 可以通过 `skill_manage` 工具创建、更新和删除自己的技能。这是 Agent 的**程序性记忆**——当它发现一个不简单的工作流程时，会将这个方法保存为技能，以便将来复用。

### Agent 何时创建技能 {#when-the-agent-creates-skills}

- 成功完成复杂任务（5 次以上工具调用）后
- 遇到错误或死胡同并找到可行路径时
- 用户纠正了它的方法时
- 发现一个不简单的工作流程时

### 操作 {#actions}

| 操作 | 用途 | 关键参数 |
|--------|---------|------------|
| `create` | 从头创建新技能 | `name`、`content`（完整 SKILL.md）、可选 `category` |
| `patch` | 针对性修复（推荐） | `name`、`old_string`、`new_string` |
| `edit` | 重大结构重写 | `name`、`content`（替换完整 SKILL.md） |
| `delete` | 完全删除一个技能 | `name` |
| `write_file` | 添加/更新支持文件 | `name`、`file_path`、`file_content` |
| `remove_file` | 删除一个支持文件 | `name`、`file_path` |

:::tip
`patch` 操作是更新的首选——它比 `edit` 更节省 token，因为只有更改的文本会出现在工具调用中。
:::

## 技能中心 {#skills-hub}

浏览、搜索、安装和管理来自在线注册表、`skills.sh`、直接知名技能端点以及官方可选技能的技能。

### 常用命令 {#common-commands}

```bash
hermes skills browse                              # 浏览所有中心技能（官方优先）
hermes skills browse --source official            # 仅浏览官方可选技能
hermes skills search kubernetes                   # 搜索所有来源
hermes skills search react --source skills-sh     # 搜索 skills.sh 目录
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect openai/skills/k8s           # 安装前预览
hermes skills install openai/skills/k8s           # 安装并执行安全扫描
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install https://sharethis.chat/SKILL.md              # 直接 URL（单文件 SKILL.md）
hermes skills install https://example.com/SKILL.md --name my-skill # 当 frontmatter 中没有名称时覆盖名称
hermes skills list --source hub                   # 列出中心安装的技能
hermes skills check                               # 检查已安装的中心技能是否有上游更新
hermes skills update                              # 必要时重新安装有上游变更的中心技能
hermes skills audit                               # 重新扫描所有中心技能的安全性
hermes skills uninstall k8s                       # 移除一个中心技能
hermes skills reset google-workspace              # 将捆绑技能从“用户修改”状态解除（见下文）
hermes skills reset google-workspace --restore    # 同时恢复捆绑版本，删除你的本地编辑
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json          # 导出技能配置
hermes skills tap add myorg/skills-repo           # 添加自定义 GitHub 源
```
### 支持的源站 {#supported-hub-sources}

| 源站 | 示例 | 说明 |
|--------|---------|-------|
| `official` | `official/security/1password` | Hermes 附带的可选技能。 |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | 可通过 `hermes skills search &lt;query&gt; --source skills-sh` 搜索。当 skills.sh 的 slug 与仓库文件夹不同时，Hermes 会解析别名风格的技能。 |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | 直接从网站的 `/.well-known/skills/index.json` 提供的技能。使用站点或文档 URL 进行搜索。 |
| `url` | `https://sharethis.chat/SKILL.md` | 指向单文件 `SKILL.md` 的直接 HTTP(S) URL。名称解析顺序：frontmatter → URL slug → 交互式提示 → `--name` 标志。 |
| `github` | `openai/skills/k8s` | 直接通过 GitHub 仓库/路径安装以及自定义 tap。 |
| `clawhub`、`lobehub`、`claude-marketplace` | 源站特定标识符 | 社区或市场集成。 |

### 集成的中心与注册表 {#integrated-hubs-and-registries}

Hermes 目前与以下技能生态系统和发现源集成：

#### 1. 官方可选技能（`official`） {#1-official-optional-skills-official}

这些技能维护在 Hermes 仓库本身中，安装时具有内置信任。

- 目录：[官方可选技能目录](../../reference/optional-skills-catalog)
- 仓库中的源：`optional-skills/`
- 示例：

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

#### 2. skills.sh（`skills-sh`） {#2-skills-sh-skills-sh}

这是 Vercel 的公共技能目录。Hermes 可以直接搜索它、查看技能详情页面、解析别名风格的 slug，并从底层源仓库安装。

- 目录：[skills.sh](https://skills.sh/)
- CLI/工具仓库：[vercel-labs/skills](https://github.com/vercel-labs/skills)
- 官方 Vercel 技能仓库：[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- 示例：

```bash
hermes skills search react --source skills-sh
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

#### 3. 知名技能端点（`well-known`） {#3-well-known-skill-endpoints-well-known}

这是基于 URL 的发现方式，来自发布 `/.well-known/skills/index.json` 的站点。它不是一个集中的中心——而是一种网络发现约定。

- 示例实时端点：[Mintlify 文档技能索引](https://mintlify.com/docs/.well-known/skills/index.json)
- 参考服务器实现：[vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- 示例：

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

#### 4. 直接 GitHub 技能（`github`） {#4-direct-github-skills-github}

Hermes 可以直接从 GitHub 仓库和基于 GitHub 的 tap 安装。当你已经知道仓库/路径或想添加自己的自定义源仓库时，这很有用。
默认源（无需任何设置即可浏览）：
- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [garrytan/gstack](https://github.com/garrytan/gstack)

- 示例：

```bash
hermes skills install openai/skills/k8s
hermes skills tap add myorg/skills-repo
```

#### 5. ClawHub（`clawhub`） {#5-clawhub-clawhub}

一个集成为社区源的第三方技能市场。

- 网站：[clawhub.ai](https://clawhub.ai/)
- Hermes 源标识：`clawhub`

#### 6. Claude 市场风格仓库（`claude-marketplace`） {#6-claude-marketplace-style-repos-claude-marketplace}

Hermes 支持发布兼容 Claude 的插件/市场清单的市场仓库。

已知集成的源包括：
- [anthropics/skills](https://github.com/anthropics/skills)
- [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)

Hermes 源标识：`claude-marketplace`

#### 7. LobeHub（`lobehub`） {#7-lobehub-lobehub}

Hermes 可以从 LobeHub 的公开目录中搜索 Agent 条目，并将其转换为可安装的 Hermes 技能。

- 网站：[LobeHub](https://lobehub.com/)
- 公开 Agent 索引：[chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- 后端仓库：[lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes 源标识：`lobehub`

#### 8. 直接 URL（`url`） {#8-direct-url-url}

直接从任何 HTTP(S) URL 安装单文件 `SKILL.md`——当作者在自己的网站上托管技能时非常有用（无需在中心市场列出，也无需输入 GitHub 路径）。Hermes 会获取该 URL，解析 YAML 前置元数据，进行安全扫描，然后安装。

- Hermes 源标识：`url`
- 标识符：URL 本身（无需前缀）
- 范围：仅限**单文件 `SKILL.md`**。包含 `references/` 或 `scripts/` 的多文件技能需要清单，并应通过上述其他源之一发布。

```bash
hermes skills install https://sharethis.chat/SKILL.md
hermes skills install https://example.com/my-skill/SKILL.md --category productivity
```

名称解析顺序：
1. `name:` 字段（位于 SKILL.md 的 YAML 前置元数据中，推荐——每个格式良好的技能都应包含此字段）。
2. URL 路径中的父目录名称（例如 `.../my-skill/SKILL.md` → `my-skill`，或 `.../my-skill.md` → `my-skill`），前提是该名称是有效的标识符（`^[a-z][a-z0-9_-]*$`）。
3. 在带有 TTY 的终端上交互式提示。
4. 在非交互式界面（TUI 中的 `/skills install` 斜杠命令、网关平台、脚本）上，会给出一个清晰的错误，提示使用 `--name` 覆盖。

```bash
# Frontmatter has no name and the URL slug is unhelpful — supply one:
hermes skills install https://example.com/SKILL.md --name sharethis-chat

# Or inside a chat session:
/skills install https://example.com/SKILL.md --name sharethis-chat
```

信任级别始终为 `community`——与所有其他源运行相同的安全扫描。URL 被存储为安装标识符，因此当你想要刷新时，`hermes skills update` 会自动从同一 URL 重新获取。

### 安全扫描与 `--force` {#security-scanning-and-force}
所有从中心仓库安装的技能都会经过**安全扫描器**检查，该扫描器会检测数据泄露、提示注入、破坏性命令、供应链信号以及其他威胁。

`hermes skills inspect ...` 现在还会在可用时显示上游元数据：
- 仓库 URL
- skills.sh 详情页 URL
- 安装命令
- 周安装量
- 上游安全审计状态
- 知名索引/端点 URL

当你审查过第三方技能并希望覆盖非危险策略阻止时，使用 `--force`：

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

重要行为：
- `--force` 可以覆盖针对警告/提醒类发现的策略阻止。
- `--force` **不能**覆盖 `dangerous` 扫描判定。
- 官方可选技能（`official/...`）被视为内置信任，不会显示第三方警告面板。

### 信任级别 {#trust-levels}

| 级别 | 来源 | 策略 |
|-------|--------|--------|
| `builtin` | 随 Hermes 自带 | 始终信任 |
| `official` | 仓库中的 `optional-skills/` | 内置信任，无第三方警告 |
| `trusted` | 受信任的注册表/仓库，如 `openai/skills`、`anthropics/skills` | 比社区来源更宽松的策略 |
| `community` | 其他所有来源（`skills.sh`、知名端点、自定义 GitHub 仓库、大多数市场） | 非危险发现可用 `--force` 覆盖；`dangerous` 判定保持阻止 |

### 更新生命周期 {#update-lifecycle}

中心仓库现在会跟踪足够的来源信息，以便重新检查已安装技能的上游副本：

```bash
hermes skills check          # 报告哪些已安装的中心仓库技能在上游发生了变化
hermes skills update         # 仅重新安装有可用更新的技能
hermes skills update react   # 更新一个特定的已安装中心仓库技能
```

这使用存储的源标识符加上当前上游包内容哈希来检测差异。

:::tip GitHub 速率限制
<a id="github-rate-limits"></a>
技能中心操作使用 GitHub API，对于未认证用户，速率限制为 60 次请求/小时。如果在安装或搜索过程中遇到速率限制错误，请在 `.env` 文件中设置 `GITHUB_TOKEN`，将限制提高到 5,000 次请求/小时。发生这种情况时，错误消息会包含可操作提示。
:::

## 捆绑技能更新（`hermes skills reset`） {#bundled-skill-updates-hermes-skills-reset}

Hermes 在仓库的 `skills/` 目录中附带了一组捆绑技能。在安装时以及每次执行 `hermes update` 时，同步过程会将这些技能复制到 `~/.hermes/skills/`，并在 `~/.hermes/skills/.bundled_manifest` 中记录一个清单，将每个技能名称映射到同步时的内容哈希（**原始哈希**）。

每次同步时，Hermes 会重新计算本地副本的哈希值，并与原始哈希值进行比较：

- **未更改** → 可以安全拉取上游更改，复制新的捆绑版本，并记录新的原始哈希。
- **已更改** → 被视为**用户修改**并永久跳过，因此你的编辑永远不会被覆盖。

这种保护机制很好，但有一个尖锐的边缘情况。如果你编辑了一个捆绑技能，后来又想放弃更改，通过从 `~/.hermes/hermes-agent/skills/` 复制粘贴回到捆绑版本，清单仍然保留着上次成功同步时的*旧*原始哈希。你新复制粘贴的内容（当前捆绑哈希）不会匹配那个过时的原始哈希，因此同步会继续将其标记为用户修改。
`hermes skills reset` 是逃生出口：

```bash
# Safe: clears the manifest entry for this skill. Your current copy is preserved,
# but the next sync re-baselines against it so future updates work normally.
hermes skills reset google-workspace

# Full restore: also deletes your local copy and re-copies the current bundled
# version. Use this when you want the pristine upstream skill back.
hermes skills reset google-workspace --restore

# Non-interactive (e.g. in scripts or TUI mode) — skip the --restore confirmation.
hermes skills reset google-workspace --restore --yes
```

同样的命令在聊天中作为斜杠命令使用：

```text
/skills reset google-workspace
/skills reset google-workspace --restore
```

:::note 配置文件
<a id="profiles"></a>
每个配置文件在其自己的 `HERMES_HOME` 下都有自己的 `.bundled_manifest`，因此 `hermes -p coder skills reset &lt;name&gt;` 仅影响该配置文件。
:::

### 斜杠命令（聊天内） {#slash-commands-inside-chat}

所有相同的命令都可以使用 `/skills`：

```text
/skills browse
/skills search react --source skills-sh
/skills search https://mintlify.com/docs --source well-known
/skills inspect skills-sh/vercel-labs/json-render/json-render-react
/skills install openai/skills/skill-creator --force
/skills check
/skills update
/skills reset google-workspace
/skills list
```

官方可选技能仍然使用诸如 `official/security/1password` 和 `official/migration/openclaw-migration` 之类的标识符。
