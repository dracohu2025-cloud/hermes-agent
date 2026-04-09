---
sidebar_position: 2
title: "技能系统 (Skills System)"
description: "按需调用的知识文档 —— 渐进式披露、Agent 管理的技能以及技能中心 (Skills Hub)"
---

# 技能系统 (Skills System)

技能是 Agent 在需要时可以加载的按需知识文档。它们遵循**渐进式披露 (progressive disclosure)** 模式以最小化 Token 消耗，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。

所有技能都存放在 **`~/.hermes/skills/`** —— 这是主要目录和唯一事实来源。在全新安装时，内置技能会从仓库复制到此处。通过 Hub 安装的技能和 Agent 创建的技能也会存放在这里。Agent 可以修改或删除任何技能。

你也可以让 Hermes 指向**外部技能目录** —— 即在扫描本地文件夹的同时扫描其他文件夹。请参阅下文的[外部技能目录](#external-skill-directories)。

另请参阅：

- [内置技能目录](/reference/skills-catalog)
- [官方可选技能目录](/reference/optional-skills-catalog)

## 使用技能

每个安装的技能都会自动作为一个斜杠命令 (slash command) 可供使用：

```bash
# 在 CLI 或任何消息平台中：
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor
/plan design a rollout for migrating our auth provider

# 仅输入技能名称会加载它，并让 Agent 询问你的需求：
/excalidraw
```

内置的 `plan` 技能是一个带有自定义行为的技能驱动斜杠命令的典型例子。运行 `/plan [request]` 会告诉 Hermes 在需要时检查上下文，编写一个 Markdown 格式的实施计划（而不是直接执行任务），并将结果保存到当前工作区/后端工作目录相关的 `.hermes/plans/` 下。

你也可以通过自然语言对话与技能交互：

```bash
hermes chat --toolsets skills -q "What skills do you have?"
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

## 渐进式披露

技能使用一种节省 Token 的加载模式：

```
Level 0: skills_list()           → [{name, description, category}, ...]   (约 3k tokens)
Level 1: skill_view(name)        → 完整内容 + 元数据                       (大小不一)
Level 2: skill_view(name, path)  → 特定的参考文件                         (大小不一)
```

Agent 只有在真正需要时才会加载完整的技能内容。

## SKILL.md 格式

```markdown
---
name: my-skill
description: 简要描述该技能的作用
version: 1.0.0
platforms: [macos, linux]     # 可选 — 限制在特定的操作系统平台
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]    # 可选 — 条件激活（见下文）
    requires_toolsets: [terminal]   # 可选 — 条件激活（见下文）
    config:                          # 可选 — config.yaml 设置
      - key: my.setting
        description: "此项控制的内容"
        default: "value"
        prompt: "设置时的提示语"
---

# 技能标题

## 何时使用
此技能的触发条件。

## 流程步骤
1. 第一步
2. 第二步

## 常见陷阱
- 已知的失败模式及修复方法

## 验证
如何确认操作已生效。
```

### 平台特定技能

技能可以使用 `platforms` 字段将自己限制在特定的操作系统中：

| 值 | 匹配项 |
|-------|---------|
| `macos` | macOS (Darwin) |
| `linux` | Linux |
| `windows` | Windows |

```yaml
platforms: [macos]            # 仅限 macOS (例如：iMessage, Apple Reminders, FindMy)
platforms: [macos, linux]     # macOS 和 Linux
```

设置后，该技能在不兼容的平台上会自动从系统提示词、`skills_list()` 和斜杠命令中隐藏。如果省略，该技能将在所有平台上加载。

### 条件激活（回退技能）

技能可以根据当前会话中哪些工具可用，自动显示或隐藏自己。这对于**回退技能 (fallback skills)** 非常有用 —— 即只有在高级工具不可用时才显示的免费或本地替代方案。

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
| `fallback_for_toolsets` | 当列出的工具集可用时，技能被**隐藏**。缺失时显示。 |
| `fallback_for_tools` | 同上，但检查单个工具而不是工具集。 |
| `requires_toolsets` | 当列出的工具集不可用时，技能被**隐藏**。存在时显示。 |
| `requires_tools` | 同上，但检查单个工具。 |

**示例：** 内置的 `duckduckgo-search` 技能使用了 `fallback_for_toolsets: [web]`。当你设置了 `FIRECRAWL_API_KEY` 时，`web` 工具集可用，Agent 会使用 `web_search` —— 此时 DuckDuckGo 技能保持隐藏。如果 API Key 缺失，`web` 工具集不可用，DuckDuckGo 技能会自动作为回退方案出现。

没有任何条件字段的技能行为与以前完全一致 —— 它们始终显示。

## 加载时的安全设置

技能可以声明所需的环境变量，而不会从发现列表中消失：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: 从 https://developers.google.com/tenor 获取 Key
    required_for: 完整功能
```

当遇到缺失的值时，只有在本地 CLI 中实际加载该技能时，Hermes 才会安全地询问该值。你可以跳过设置并继续使用该技能。消息界面永远不会在聊天中询问敏感信息 —— 它们会提示你在本地使用 `hermes setup` 或修改 `~/.hermes/.env`。

一旦设置，声明的环境变量将**自动透传**到 `execute_code` 和 `terminal` 沙箱中 —— 技能的脚本可以直接使用 `$TENOR_API_KEY`。对于非技能环境变量，请使用 `terminal.env_passthrough` 配置选项。详见[环境变量透传](/user-guide/security#environment-variable-passthrough)。

### 技能配置设置

技能还可以声明存储在 `config.yaml` 中的非敏感配置设置（路径、偏好）：

```yaml
metadata:
  hermes:
    config:
      - key: wiki.path
        description: Wiki 目录路径
        default: "~/wiki"
        prompt: Wiki 目录路径
```

设置项存储在 config.yaml 的 `skills.config` 下。`hermes config migrate` 会提示未配置的设置，`hermes config show` 则会显示它们。当技能加载时，其解析后的配置值会被注入到上下文中，以便 Agent 自动了解配置的值。

详见[技能设置](/user-guide/configuration#skill-settings)和[创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

## 技能目录结构

```text
~/.hermes/skills/                  # 唯一事实来源
├── mlops/                         # 分类目录
│   ├── axolotl/
│   │   ├── SKILL.md               # 主要指令 (必填)
│   │   ├── references/            # 额外文档
│   │   ├── templates/             # 输出格式
│   │   ├── scripts/               # 可从技能调用的辅助脚本
│   │   └── assets/                # 补充文件
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # Agent 创建的技能
│       ├── SKILL.md
│       └── references/
├── .hub/                          # 技能中心 (Skills Hub) 状态
│   ├── lock.json
│   ├── quarantine/
│   └── audit.log
└── .bundled_manifest              # 跟踪预装的内置技能
```

## 外部技能目录 {#external-skill-directories}

如果你在 Hermes 之外维护技能 —— 例如，多个 AI 工具共用的 `~/.agents/skills/` 目录 —— 你可以告诉 Hermes 也扫描这些目录。

在 `~/.hermes/config.yaml` 的 `skills` 部分下添加 `external_dirs`：

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills
```
路径支持 `~` 扩展和 `${VAR}` 环境变量替换。

### 工作原理

- **只读**：外部目录仅用于扫描以发现技能。当 Agent 创建或编辑技能时，始终写入到 `~/.hermes/skills/`。
- **本地优先**：如果本地目录和外部目录中存在同名技能，以本地版本为准。
- **完全集成**：外部技能会出现在系统提示词索引、`skills_list`、`skill_view` 以及 `/skill-name` 斜杠命令中 —— 与本地技能没有区别。
- **静默跳过不存在的路径**：如果配置的目录不存在，Hermes 会忽略它而不报错。这对于在不同机器上可能不存在的可选共享目录非常有用。

### 示例

```text
~/.hermes/skills/               # 本地 (主要，可读写)
├── devops/deploy-k8s/
│   └── SKILL.md
└── mlops/axolotl/
    └── SKILL.md

~/.agents/skills/               # 外部 (只读，共享)
├── my-custom-workflow/
│   └── SKILL.md
└── team-conventions/
    └── SKILL.md
```

所有四个技能都会出现在你的技能索引中。如果你在本地创建一个名为 `my-custom-workflow` 的新技能，它将覆盖（shadow）外部版本。

## Agent 管理的技能 (skill_manage 工具)

Agent 可以通过 `skill_manage` 工具创建、更新和删除自己的技能。这是 Agent 的**程序化记忆** —— 当它摸索出一套复杂的 workflow 时，会将该方法保存为技能，以便将来复用。

### Agent 何时创建技能

- 成功完成一项复杂任务（调用工具 5 次以上）后
- 在遇到错误或死胡同并找到可行路径后
- 在用户纠正了它的方法后
- 在它发现了一套非平凡的 workflow 后

### 操作

| 操作 | 用途 | 关键参数 |
|--------|---------|------------|
| `create` | 从头开始创建新技能 | `name`, `content` (完整的 SKILL.md), 可选 `category` |
| `patch` | 有针对性的修复（推荐） | `name`, `old_string`, `new_string` |
| `edit` | 重大的结构性重写 | `name`, `content` (替换完整的 SKILL.md) |
| `delete` | 完全移除一个技能 | `name` |
| `write_file` | 添加/更新辅助文件 | `name`, `file_path`, `file_content` |
| `remove_file` | 移除辅助文件 | `name`, `file_path` |

:::tip
更新时推荐使用 `patch` 操作 —— 它比 `edit` 更节省 token，因为工具调用中只会出现修改过的文本。
:::

## 技能中心 (Skills Hub)

从在线注册表、`skills.sh`、直接的 well-known 技能端点以及官方可选技能中浏览、搜索、安装和管理技能。

### 常用命令

```bash
hermes skills browse                              # 浏览所有 hub 技能 (官方优先)
hermes skills browse --source official            # 仅浏览官方可选技能
hermes skills search kubernetes                   # 搜索所有来源
hermes skills search react --source skills-sh     # 搜索 skills.sh 目录
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect openai/skills/k8s           # 安装前预览
hermes skills install openai/skills/k8s           # 安装并进行安全扫描
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills list --source hub                   # 列出从 hub 安装的技能
hermes skills check                               # 检查已安装的 hub 技能是否有上游更新
hermes skills update                              # 必要时根据上游更改重新安装 hub 技能
hermes skills audit                               # 重新扫描所有 hub 技能的安全性
hermes skills uninstall k8s                       # 移除一个 hub 技能
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json          # 导出技能配置
hermes skills tap add myorg/skills-repo           # 添加自定义 GitHub 源
```

### 支持的 Hub 来源

| 来源 | 示例 | 备注 |
|--------|---------|-------|
| `official` | `official/security/1password` | Hermes 附带的可选技能。 |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | 可通过 `hermes skills search <query> --source skills-sh` 搜索。当 skills.sh 的 slug 与仓库文件夹不同时，Hermes 会解析别名风格的技能。 |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | 直接从网站上的 `/.well-known/skills/index.json` 提供的技能。使用站点或文档 URL 进行搜索。 |
| `github` | `openai/skills/k8s` | 直接从 GitHub 仓库/路径安装以及自定义 tap。 |
| `clawhub`, `lobehub`, `claude-marketplace` | 特定来源的标识符 | 社区或市场集成。 |

### 集成的 Hub 和注册表

Hermes 目前集成了以下技能生态系统和发现源：

#### 1. 官方可选技能 (`official`)

这些技能在 Hermes 仓库本身中维护，安装时具有内置信任。

- 目录：[官方可选技能目录](../../reference/optional-skills-catalog)
- 仓库中的源码：`optional-skills/`
- 示例：

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

#### 2. skills.sh (`skills-sh`)

这是 Vercel 的公共技能目录。Hermes 可以直接搜索它、检查技能详情页、解析别名风格的 slug，并从底层源码仓库安装。

- 目录：[skills.sh](https://skills.sh/)
- CLI/工具仓库：[vercel-labs/skills](https://github.com/vercel-labs/skills)
- Vercel 官方技能仓库：[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- 示例：

```bash
hermes skills search react --source skills-sh
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

#### 3. Well-known 技能端点 (`well-known`)

这是一种基于 URL 的发现方式，适用于发布了 `/.well-known/skills/index.json` 的站点。它不是一个单一的中心化 hub，而是一种 Web 发现规范。

- 实时端点示例：[Mintlify 文档技能索引](https://mintlify.com/docs/.well-known/skills/index.json)
- 参考服务器实现：[vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- 示例：

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

#### 4. 直接 GitHub 技能 (`github`)

Hermes 可以直接从 GitHub 仓库和基于 GitHub 的 tap 安装。当你已经知道仓库/路径或想要添加自己的自定义源仓库时，这非常有用。

默认 tap（无需任何设置即可浏览）：
- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [garrytan/gstack](https://github.com/garrytan/gstack)

- 示例：

```bash
hermes skills install openai/skills/k8s
hermes skills tap add myorg/skills-repo
```

#### 5. ClawHub (`clawhub`)

作为一个社区源集成的第三方技能市场。

- 站点：[clawhub.ai](https://clawhub.ai/)
- Hermes 来源 ID：`clawhub`

#### 6. Claude 市场风格的仓库 (`claude-marketplace`)

Hermes 支持发布了 Claude 兼容插件/市场清单的仓库。

已知的集成来源包括：
- [anthropics/skills](https://github.com/anthropics/skills)
- [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)

Hermes 来源 ID：`claude-marketplace`

#### 7. LobeHub (`lobehub`)

Hermes 可以搜索 LobeHub 公共目录中的 Agent 条目，并将其转换为可安装的 Hermes 技能。

- 站点：[LobeHub](https://lobehub.com/)
- 公共 Agent 索引：[chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- 后端仓库：[lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes 来源 ID：`lobehub`
### 安全扫描与 `--force` 参数

所有通过 hub 安装的 Skill 都会经过 **安全扫描器（security scanner）**，检查是否存在数据外泄、提示词注入（prompt injection）、破坏性命令、供应链风险以及其他威胁。

`hermes skills inspect ...` 现在也会在可用时显示上游元数据：
- 仓库 URL
- skills.sh 详情页 URL
- 安装命令
- 每周安装量
- 上游安全审计状态
- 众所周知的 index/endpoint URL

当你已经审查过第三方 Skill 并希望覆盖非危险级别的策略拦截时，请使用 `--force`：

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

重要行为说明：
- `--force` 可以覆盖针对“谨慎/警告（caution/warn）”类发现的策略拦截。
- `--force` **不能** 覆盖“危险（dangerous）”级别的扫描结论。
- 官方可选 Skill（`official/...`）被视为内置信任，不会显示第三方警告面板。

### 信任等级

| 等级 | 来源 | 策略 |
|-------|--------|--------|
| `builtin` | 随 Hermes 附带 | 始终信任 |
| `official` | 仓库中的 `optional-skills/` | 内置信任，无第三方警告 |
| `trusted` | 信任的注册表/仓库，如 `openai/skills`、`anthropics/skills` | 比社区来源更宽松的策略 |
| `community` | 其他所有来源（`skills.sh`、已知端点、自定义 GitHub 仓库、大多数市场） | 非危险类发现可用 `--force` 覆盖；“危险”结论保持拦截状态 |

### 更新生命周期

Hub 现在会追踪足够的溯源信息，以便重新检查已安装 Skill 的上游副本：

```bash
hermes skills check          # 报告哪些已安装的 hub Skill 在上游发生了变化
hermes skills update         # 仅重新安装有可用更新的 Skill
hermes skills update react   # 更新某个特定的已安装 hub Skill
```

这通过存储的源标识符加上当前上游 bundle 的内容哈希值来检测差异。

### 斜杠命令（聊天界面内）

所有相同的命令都可以在聊天中使用 `/skills` 执行：

```text
/skills browse
/skills search react --source skills-sh
/skills search https://mintlify.com/docs --source well-known
/skills inspect skills-sh/vercel-labs/json-render/json-render-react
/skills install openai/skills/skill-creator --force
/skills check
/skills update
/skills list
```

官方可选 Skill 仍使用类似 `official/security/1password` 和 `official/migration/openclaw-migration` 的标识符。
