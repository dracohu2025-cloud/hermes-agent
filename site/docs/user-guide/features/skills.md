---
sidebar_position: 2
title: "技能系统"
description: "按需知识文档——渐进式加载、Agent 管理的技能，以及技能中心"
---

<a id="skills-system"></a>
# 技能系统

技能是 Agent 在需要时可以按需加载的知识文档。它们遵循**渐进式加载**模式，以最小化 token 消耗，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。

所有技能都存放在 **`~/.hermes/skills/`** 中——这是主目录和唯一事实来源。首次安装时，捆绑的技能会从仓库复制过来。从技能中心安装的和 Agent 自己创建的技能也会存放于此。Agent 可以修改或删除任何技能。

你也可以让 Hermes 指向**外部技能目录**——这些额外的文件夹会与本地目录一起被扫描。请参阅下方的[外部技能目录](#external-skill-directories)。

另请参阅：

- [捆绑技能目录](/reference/skills-catalog)
- [官方可选技能目录](/reference/optional-skills-catalog)

<a id="using-skills"></a>
## 使用技能

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

捆绑的 `plan` 技能是一个很好的例子。运行 `/plan [请求]` 会加载技能指令，告诉 Hermes 在需要时检查上下文，编写一个 Markdown 实现计划而不是直接执行任务，并将结果保存在相对于活动工作区/后端工作目录的 `.hermes/plans/` 下。

你还可以通过自然对话与技能交互：

```bash
hermes chat --toolsets skills -q "你有哪些技能？"
hermes chat --toolsets skills -q "显示 axolotl 技能"
```

<a id="progressive-disclosure"></a>
## 渐进式加载

技能采用一种节省 token 的加载模式：

```
第 0 层：skills_list()           → [{name, description, category}, ...]   （约 3k tokens）
第 1 层：skill_view(name)        → 完整内容 + 元数据       （不定）
第 2 层：skill_view(name, path)  → 特定引用文件            （不定）
```

Agent 只会在实际需要时加载完整的技能内容。

<a id="skill-md-format"></a>
## SKILL.md 格式

```markdown
---
name: my-skill
description: 简要描述该技能的功能
version: 1.0.0
platforms: [macos, linux]     # 可选——限制为特定的操作系统平台
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]    # 可选——条件激活（见下文）
    requires_toolsets: [terminal]   # 可选——条件激活（见下文）
    config:                          # 可选——config.yaml 设置
      - key: my.setting
        description: "该项控制什么"
        default: "value"
        prompt: "设置提示"
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
如何确认操作成功。
```

<a id="platform-specific-skills"></a>
### 平台特定的技能
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

<a id="skill-output-and-media-delivery"></a>
## Skill 输出与媒体投递

当 skill 响应（或任何 agent 响应）包含媒体文件的裸绝对路径时——例如 `/home/user/screenshots/diagram.png`——网关会自动检测该路径，将其从可见文本中剥离，并以原生方式将文件投递到用户的聊天中（Telegram 图片、Discord 附件等），而不是在消息中保留原始路径。

对于音频，`[[audio_as_voice]]` 指令会将音频文件提升为支持该功能的平台（Telegram、WhatsApp）上的原生语音消息气泡。

<a id="forcing-document-style-delivery-asdocument"></a>
### 强制文档式投递：`[[as_document]]`

有时你需要**与内联预览相反**的效果：希望文件作为可下载的附件投递，而不是重新压缩后的图片气泡。典型的例子是高分辨率截图或图表——Telegram 的 `sendPhoto` 会将其重新压缩到约 200 KB、1280 像素，破坏可读性。通过 `sendDocument` 发送的 1-2 MB PNG 文件则能保持原始字节不变。

如果响应（或其中的任何文本——通常是最后一行）包含字面指令 `[[as_document]]`，则从该响应中提取的每个媒体路径都会作为文档/文件附件投递，而不是图片气泡：

```
这是您渲染的图表：

/home/user/.hermes/cache/chart-q4-2025.png

[[as_document]]
```

该指令在投递前会被剥离，因此用户永远不会看到它。粒度有意设计为每个响应全有或全无：只需发出一次 `[[as_document]]`，同一响应中的所有图片路径都会作为文档投递。这与 `[[audio_as_voice]]` 的作用范围一致。

在以下情况下从 skill 中使用它：

- 您生成的截图或图表需要用户作为文件使用（用于在其他工具中编辑、存档、完整共享）。
- 默认的有损预览会模糊细节（小文本、像素级精确的图表、对颜色敏感的渲染）。

没有独立文档路径的平台（例如 SMS）会回退到它们拥有的任何附件机制。

<a id="conditional-activation-fallback-skills"></a>
### 条件激活（回退 Skills）

Skills 可以根据当前会话中可用的工具自动显示或隐藏自身。这对于**回退 skills** 最为有用——当高级工具不可用时，仅显示免费或本地替代方案。

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
| `fallback_for_toolsets` | 当列出的工具集可用时，技能**隐藏**；当工具集缺失时显示。 |
| `fallback_for_tools` | 同上，但检查的是单个工具而非工具集。 |
| `requires_toolsets` | 当列出的工具集不可用时，技能**隐藏**；当工具集存在时显示。 |
| `requires_tools` | 同上，但检查的是单个工具。 |

**示例：** 内置的 `duckduckgo-search` 技能使用了 `fallback_for_toolsets: [web]`。当您设置了 `FIRECRAWL_API_KEY` 时，web 工具集可用，Agent 会使用 `web_search`——此时 DuckDuckGo 技能保持隐藏。如果 API 密钥缺失，web 工具集不可用，DuckDuckGo 技能会自动作为回退出现。

没有任何条件字段的技能表现和之前完全一样——它们始终显示。

<a id="secure-setup-on-load"></a>
## 加载时的安全设置

技能可以声明所需的环境变量，而不会从发现中消失：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

遇到缺失的值时，Hermes 仅在技能实际加载到本地 CLI 时才会安全地请求该值。您可以跳过设置并继续使用该技能。消息界面永远不会在聊天中询问密钥——而是提示您在本地使用 `hermes setup` 或 `~/.hermes/.env`。

一旦设置，声明的环境变量会自动**传递给** `execute_code` 和 `terminal` 沙箱——技能脚本可以直接使用 `$TENOR_API_KEY`。对于非技能环境变量，请使用 `terminal.env_passthrough` 配置选项。详情请参见[环境变量传递](/user-guide/security#environment-variable-passthrough)。

<a id="skill-config-settings"></a>
### 技能配置设置

技能还可以声明存储在 `config.yaml` 中的非秘密配置设置（路径、偏好）：

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
```

设置存储在 config.yaml 的 `skills.config` 下。`hermes config migrate` 会提示您配置未设置的设置，`hermes config show` 会显示它们。当技能加载时，其解析后的配置值会被注入上下文中，以便 Agent 自动知晓已配置的值。

详情请参见[技能设置](/user-guide/configuration#skill-settings)和[创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

<a id="skill-directory-structure"></a>
## 技能目录结构

```text
~/.hermes/skills/                  # Single source of truth
├── mlops/                         # Category directory
│   ├── axolotl/
│   │   ├── SKILL.md               # Main instructions (required)
│   │   ├── references/            # Additional docs
│   │   ├── templates/             # Output formats
│   │   ├── scripts/               # Helper scripts callable from the skill
│   │   └── assets/                # Supplementary files
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # Agent-created skill
│       ├── SKILL.md
│       └── references/
├── .hub/                          # Skills Hub state
│   ├── lock.json
│   ├── quarantine/
│   └── audit.log
└── .bundled_manifest              # Tracks seeded bundled skills
```
<a id="external-skill-directories"></a>
## 外部技能目录 {#external-skill-directories}

如果你在 Hermes 外部维护了一些技能——例如多个 AI 工具共享的 `~/.agents/skills/` 目录——可以告诉 Hermes 也扫描这些目录。

在 `~/.hermes/config.yaml` 的 `skills` 段中添加 `external_dirs`：

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills
```

路径支持 `~` 展开和 `${VAR}` 环境变量替换。

<a id="how-it-works"></a>
### 工作原理

- **本地创建，原地更新**：Agent 创建的新技能会写入 `~/.hermes/skills/`。当 Agent 使用 `skill_manage` 动作（如 `patch`、`edit`、`write_file`、`remove_file` 或 `delete`）时，已有技能会在其所在位置（包括 `external_dirs` 下的技能）被修改。
- **外部目录不是写保护边界**：如果外部技能目录对 Hermes 进程可写，Agent 管理的技能更新可以修改该目录中的文件。若需要保持共享的外部技能只读，请使用文件系统权限或单独的工具集/配置文件设置。
- **本地优先级**：如果本地目录和外部目录中存在同名的技能，本地版本优先。
- **完全集成**：外部技能会出现在系统提示索引、`skills_list`、`skill_view` 以及 `/skill-name` 斜杠命令中——与本地技能无异。
- **不存在的路径会被静默跳过**：如果配置的目录不存在，Hermes 会忽略它且不报错。对于可能并非每台机器上都有的可选共享目录，这很有用。

<a id="example"></a>
### 示例

```text
~/.hermes/skills/               # 本地（主要，可读写）
├── devops/deploy-k8s/
│   └── SKILL.md
└── mlops/axolotl/
    └── SKILL.md

~/.agents/skills/               # 外部（共享，若可写则可修改）
├── my-custom-workflow/
│   └── SKILL.md
└── team-conventions/
    └── SKILL.md
```

所有四个技能都会出现在你的技能索引中。如果你在本地创建了一个名为 `my-custom-workflow` 的新技能，它将覆盖外部版本。

<a id="skill-bundles"></a>
## 技能包

技能包是极小的 YAML 文件，将多个技能组合到单个斜杠命令下。当你运行 `/&lt;bundle-name&gt;` 时，包中列出的每个技能都会同时加载——当某个特定任务总是需要同一套技能时，这非常有用。

<a id="quick-example"></a>
### 快速示例

```bash
# 为后端功能工作创建技能包
hermes bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "后端功能工作——审查、测试、PR 工作流"
```

然后在 CLI 或任何网关平台中：

```
/backend-dev 重构 auth 中间件
```

Agent 会在一条用户消息中收到所有三个技能，斜杠命令后的任何文本会作为用户指令附加。

<a id="yaml-schema"></a>
### YAML 模式

技能包存放在 **`~/.hermes/skill-bundles/&lt;slug&gt;.yaml`**，格式如下：

```yaml
name: backend-dev
description: 后端功能工作——审查、测试、PR 工作流。
skills:
  - github-code-review
  - test-driven-development
  - github-pr-workflow
instruction: |
  始终从编写失败测试开始，然后实现。
  通过标准工作流创建 PR，并添加共同作者标签。
```
字段：
- `name`（可选，默认取文件名的主干）— 包的显示名称。斜杠命令中会将其标准化为连字符式短横线格式（例如 `Backend Dev` → `/backend-dev`）。
- `description`（可选）— 在 `/bundles` 和 `hermes bundles list` 中显示的简短说明。
- `skills`（必需，非空列表）— 技能名称，或相对于技能目录的路径。使用与传递给 `/&lt;skill-name&gt;` 相同的标识符。
- `instruction`（可选）— 附加的指引，会预置到加载的技能内容之前。适合用来规定“我们通常如何组合使用这些技能”。

<a id="managing-bundles"></a>
### 管理 bundles

```bash
# 列出所有已安装的 bundle
hermes bundles list

# 查看某个 bundle 的详情
hermes bundles show backend-dev

# 交互式创建 bundle（省略 --skill 标志即可逐行输入技能）
hermes bundles create research

# 覆盖已有的 bundle
hermes bundles create backend-dev --skill ... --force

# 删除 bundle
hermes bundles delete backend-dev

# 重新扫描 ~/.hermes/skill-bundles/ 并报告变更
hermes bundles reload
```

在聊天会话中输入 `/bundles` 即可列出所有已安装的 bundle 及其技能。

<a id="behavior"></a>
### 行为

- **当 slug 冲突时，bundle 优先级高于单个技能。** 如果你把一个 bundle 命名为 `research`，并且你还有一个名为 `research` 的技能，那么 `/research` 会调用 bundle。这是有意为之——你通过命名选择了使用这个 bundle。
- **缺失的技能会被跳过，不会导致错误。** 如果某个 bundle 中列出了 `skill-foo`，但你尚未安装它，bundle 仍然会加载其他可解析的技能，并且 Agent 会收到一条通知，列出哪些技能被跳过了。
- **Bundle 在所有界面中都能工作**——交互式 CLI、TUI、仪表板聊天以及所有网关平台（Telegram、Discord、Slack 等），因为调度机制与单个技能命令的调度机制一致。
- **Bundle 不会使提示缓存失效。** 它们在调用时会生成新的用户消息，与 `/&lt;skill-name&gt;` 的方式一样——不会修改系统提示。

<a id="when-bundles-beat-installing-each-skill-manually"></a>
### 什么时候 bundle 比手动逐个安装技能更好？

在以下场景中使用 bundle：
- 你经常为某个反复出现的任务组合使用相同的技能（例如 `/backend-dev`、`/release-prep`、`/incident-response`）。
- 你希望使用比连续输入多个 `/skill` 调用更简洁的心智模型。
- 你想通过将 bundle 的 YAML 文件检入到共享的 dotfiles 仓库，并创建符号链接到 `~/.hermes/skill-bundles/`，来分发团队级的“任务配置文件”。

Bundle 只是一个 YAML 别名——它不会替你安装技能。技能本身必须已经存在（在 `~/.hermes/skills/` 或外部技能目录中）。否则，bundle 调用时只会跳过缺失的技能。

<a id="agent-managed-skills-skillmanage-tool"></a>
## 由 Agent 管理的技能（skill_manage 工具）

Agent 可以通过 `skill_manage` 工具自行创建、更新和删除技能。这是 Agent 的**程序记忆**——当它发现一个复杂的工作流时，会将方法保存为技能，以供将来复用。

<a id="when-the-agent-creates-skills"></a>
### Agent 何时创建技能

- 成功完成一个复杂任务（涉及 5 次以上工具调用）后
- 当它遇到错误或死胡同，并找到了可行的路径时
- 当用户纠正了它的方法时
- 当它发现了一个复杂的工作流时
<a id="actions"></a>
### Actions

| Action | Use for | Key params |
|--------|---------|------------|
| `create` | 从头创建新技能 | `name`、`content`（完整 SKILL.md）、可选 `category` |
| `patch` | 针对性修复（推荐） | `name`、`old_string`、`new_string` |
| `edit` | 重大结构重写 | `name`、`content`（替换完整 SKILL.md） |
| `delete` | 完全删除技能 | `name` |
| `write_file` | 添加/更新辅助文件 | `name`、`file_path`、`file_content` |
| `remove_file` | 删除辅助文件 | `name`、`file_path` |

:::tip
`patch` 操作是更新的首选方式——它比 `edit` 更节省 token，因为工具调用中只包含更改的文本。
:::

<a id="skills-hub"></a>
## Skills Hub

浏览、搜索、安装和管理来自在线注册表、`skills.sh`、直接知名技能端点以及官方可选技能的技能。

<a id="common-commands"></a>
### 常用命令

```bash
hermes skills browse                              # 浏览所有 hub 技能（官方优先）
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
hermes skills install https://example.com/SKILL.md --name my-skill # 当 frontmatter 没有名称时覆盖名称
hermes skills list --source hub                   # 列出已安装的 hub 技能
hermes skills check                               # 检查已安装的 hub 技能是否有上游更新
hermes skills update                              # 当上游有变更时重新安装 hub 技能
hermes skills audit                               # 重新扫描所有 hub 技能的安全性
hermes skills uninstall k8s                       # 移除一个 hub 技能
hermes skills reset google-workspace              # 将捆绑技能从“用户修改”状态解除（见下文）
hermes skills reset google-workspace --restore    # 同时恢复捆绑版本，删除你的本地编辑
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json          # 导出技能配置
hermes skills tap add myorg/skills-repo           # 添加自定义 GitHub 源
```

<a id="supported-hub-sources"></a>
### 支持的 hub 源

| 源 | 示例 | 说明 |
|--------|---------|-------|
| `official` | `official/security/1password` | Hermes 附带的可选技能。 |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | 可通过 `hermes skills search &lt;query&gt; --source skills-sh` 搜索。当 skills.sh 的 slug 与仓库文件夹不同时，Hermes 会解析别名风格的技能。 |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | 直接从网站 `/.well-known/skills/index.json` 提供的技能。使用站点或文档 URL 进行搜索。 |
| `url` | `https://sharethis.chat/SKILL.md` | 指向单文件 `SKILL.md` 的直接 HTTP(S) URL。名称解析顺序：frontmatter → URL slug → 交互式提示 → `--name` 标志。 |
| `github` | `openai/skills/k8s` | 直接 GitHub 仓库/路径安装和自定义 tap。 |
| `clawhub`、`lobehub`、`browse-sh`、`claude-marketplace` | 特定来源标识符 | 社区或市场集成。 |
<a id="integrated-hubs-and-registries"></a>
### 集成中心与注册源

Hermes 目前集成了以下技能生态与发现源：

<a id="1-official-optional-skills-official"></a>
#### 1. 官方可选技能（`official`）

这些技能维护在 Hermes 仓库本身中，安装时自带内置信任。

- 目录：[官方可选技能目录](../../reference/optional-skills-catalog)
- 仓库中的源：`optional-skills/`
- 示例：

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

<a id="2-skills-sh-skills-sh"></a>
#### 2. skills.sh（`skills-sh`）

这是 Vercel 的公开技能目录。Hermes 可以直接搜索、查看技能详情页、解析别名式的 slug，并从底层源码仓库进行安装。

- 目录：[skills.sh](https://skills.sh/)
- CLI/工具仓库：[vercel-labs/skills](https://github.com/vercel-labs/skills)
- Vercel 官方技能仓库：[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- 示例：

```bash
hermes skills search react --source skills-sh
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

<a id="3-well-known-skill-endpoints-well-known"></a>
#### 3. 知名技能端点（`well-known`）

这是基于 URL 的发现方式，从发布 `/.well-known/skills/index.json` 的站点获取。它不是单个中心化的中心——而是一种网络发现约定。

- 示例在线端点：[Mintlify 文档技能索引](https://mintlify.com/docs/.well-known/skills/index.json)
- 参考服务端实现：[vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- 示例：

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

<a id="4-direct-github-skills-github"></a>
#### 4. 直接 GitHub 技能（`github`）

Hermes 可以直接从 GitHub 仓库和基于 GitHub 的 tap 安装技能。当你知道仓库/路径或想添加自己的自定义源仓库时，这非常有用。

默认 tap（无需任何设置即可浏览）：
- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [huggingface/skills](https://github.com/huggingface/skills)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [garrytan/gstack](https://github.com/garrytan/gstack)

- 示例：

```bash
hermes skills install openai/skills/k8s
hermes skills tap add myorg/skills-repo
```

<a id="5-clawhub-clawhub"></a>
#### 5. ClawHub（`clawhub`）

一个第三方技能市场，作为社区源集成。

- 站点：[clawhub.ai](https://clawhub.ai/)
- Hermes 源 id：`clawhub`

<a id="6-claude-marketplace-style-repos-claude-marketplace"></a>
#### 6. Claude 市场风格仓库（`claude-marketplace`）

Hermes 支持那些发布 Claude 兼容的插件/市场清单的市场仓库。

已知的集成源包括：
- [anthropics/skills](https://github.com/anthropics/skills)
- [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)
<a id="7-lobehub-lobehub"></a>
#### 7. LobeHub（`lobehub`）

Hermes 可以搜索 LobeHub 公开目录中的 Agent 条目，并将其转换为可安装的 Hermes Skills。

- 网站：[LobeHub](https://lobehub.com/)
- 公共 Agent 索引：[chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- 后端仓库：[lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes 源 ID：`lobehub`

<a id="8-browse-sh-browse-sh"></a>
#### 8. browse.sh（`browse-sh`）

Hermes 集成了 [browse.sh](https://browse.sh)，这是 Browserbase 的目录，包含 200 多个针对特定站点的浏览器自动化 SKILL.md 文件（包括 Airbnb、Amazon、arXiv、12306.cn、Etsy、Xero 等）。每个 Skill 都描述了如何端到端地驱动一个网站，适合与 Hermes 的浏览器工具以及你已安装的任何浏览器自动化技能配合使用。

- 网站：[browse.sh](https://browse.sh/)
- 目录 API：`https://browse.sh/api/skills`
- Hermes 源 ID：`browse-sh`
- 信任等级：`community`

```bash
hermes skills search airbnb --source browse-sh
hermes skills inspect browse-sh/airbnb.com/search-listings-ddgioa
hermes skills install browse-sh/airbnb.com/search-listings-ddgioa
```

标识符格式为 `browse-sh/&lt;hostname&gt;/&lt;task-id&gt;`，与 browse.sh 目录暴露的 slug 匹配。内容通过每个技能对应的详情接口（`/api/skills/&lt;slug&gt;` → `skillMdUrl`）解析，而不是通过目录的 GitHub `sourceUrl`。

<a id="9-direct-url-url"></a>
#### 9. 直接 URL（`url`）

直接从任何 HTTP(S) URL 安装单个 `SKILL.md` 文件 —— 当作者在自己的网站上托管技能时（没有中心目录，也没有要输入的 GitHub 路径），这种方式非常有用。Hermes 会获取该 URL，解析 YAML frontmatter，进行安全扫描，然后安装。

- Hermes 源 ID：`url`
- 标识符：URL 本身（无需前缀）
- 适用范围：**仅限单个 `SKILL.md` 文件**。包含 `references/` 或 `scripts/` 的多文件技能需要清单文件，并应通过上述其他源之一发布。

```bash
hermes skills install https://sharethis.chat/SKILL.md
hermes skills install https://example.com/my-skill/SKILL.md --category productivity
```

名称解析顺序：
1. SKILL.md YAML frontmatter 中的 `name:` 字段（推荐 —— 每个格式良好的技能都有）。
2. URL 路径中的父目录名（例如 `.../my-skill/SKILL.md` → `my-skill`，或 `.../my-skill.md` → `my-skill`），前提是该名称是有效的标识符（`^[a-z][a-z0-9_-]*$`）。
3. 在带有 TTY 的终端上交互式提示。
4. 在非交互式界面（TUI 内的 `/skills install` 斜杠命令、网关平台、脚本）上，会显示一个明确的错误，提示使用 `--name` 覆盖。

```bash
# Frontmatter 中没有名称，且 URL slug 没有帮助 —— 提供一个：
hermes skills install https://example.com/SKILL.md --name sharethis-chat

# 或者在聊天会话中：
/skills install https://example.com/SKILL.md --name sharethis-chat
```

信任等级始终为 `community` —— 与其他所有源一样会执行相同的安全扫描。该 URL 会作为安装标识符存储，因此当你想要刷新时，`hermes skills update` 会自动从同一 URL 重新获取。
<a id="security-scanning-and-force"></a>
### Security scanning and `--force`

所有从中心安装的技能都经过一个**安全扫描器**，用于检查数据外泄、提示注入、破坏性命令、供应链信号及其他威胁。

`hermes skills inspect ...` 现在也会在可用时显示上游元数据：
- 仓库 URL
- skills.sh 详情页面 URL
- 安装命令
- 每周安装次数
- 上游安全审计状态
- 知名索引/端点 URL

当你审查过第三方技能并希望覆盖非危险策略阻止时，使用 `--force`：

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

重要行为：
- `--force` 可以覆盖对谨慎/警告类发现的策略阻止。
- `--force` 并**不能**覆盖 `dangerous` 扫描判定。
- 官方可选技能（`official/...`）被视为内置信任，不会显示第三方警告面板。

<a id="trust-levels"></a>
### Trust levels

| 等级 | 来源 | 策略 |
|-------|--------|--------|
| `builtin` | 随 Hermes 一同发布 | 始终信任 |
| `official` | 仓库中的 `optional-skills/` 目录 | 内置信任，无第三方警告 |
| `trusted` | 受信任的注册表/仓库，如 `openai/skills`、`anthropics/skills`、`huggingface/skills` | 比社区来源更宽松的策略 |
| `community` | 其他来源（`skills.sh`、知名端点、自定义 GitHub 仓库、大多数市场） | 非危险发现可以用 `--force` 覆盖；`dangerous` 判定保持阻止 |

<a id="update-lifecycle"></a>
### Update lifecycle

Hub 现在追踪足够的上游信息，可以重新检查已安装技能的源头副本：

```bash
hermes skills check          # 报告哪些已安装的 hub 技能在源头发生了变化
hermes skills update         # 只重新安装有可用更新的技能
hermes skills update react   # 更新一个特定的已安装 hub 技能
```

它使用存储的源标识符加上当前上游 bundle 内容的哈希来检测漂移。

:::tip GitHub 速率限制
技能 hub 操作使用 GitHub API，未经身份验证的用户有 60 次/小时的速率限制。如果在安装或搜索时遇到速率限制错误，请在 `.env` 文件中设置 `GITHUB_TOKEN`，将限制提高到 5,000 次/小时。发生此情况时，错误消息会包含可操作提示。
<a id="github-rate-limits"></a>
:::

<a id="publishing-a-custom-skill-tap"></a>
### Publishing a custom skill tap

如果你想分享一套精心编排的技能——为你的团队、你的组织或公开——你可以将它们发布为一个 **tap**：一个其他 Hermes 用户通过 `hermes skills tap add &lt;owner/repo&gt;` 添加的 GitHub 仓库。不需要服务器、注册表注册或发布管道。只需一个包含 `SKILL.md` 文件的目录。

<a id="repo-layout"></a>
#### Repo layout

一个 tap 是任何 GitHub 仓库（公开或私有——私有的需要 `GITHUB_TOKEN`），布局如下：

```
owner/repo
├── skills/                       # 默认路径；每个 tap 可配置
│   ├── my-workflow/
│   │   ├── SKILL.md              # 必需
│   │   ├── references/           # 可选的辅助文件
│   │   ├── templates/
│   │   └── scripts/
│   ├── another-skill/
│   │   └── SKILL.md
│   └── third-skill/
│       └── SKILL.md
└── README.md                     # 可选但推荐
```
规则：
- 每个技能都位于 tap 根路径（默认为 `skills/`）下自己的目录中。
- 目录名即为该技能的安装 slug。
- 每个技能目录必须包含一个 `SKILL.md`，该文件需符合标准的 [SKILL.md frontmatter](#skillmd-format) 格式（包含 `name`、`description`，以及可选的 `metadata.hermes.tags`、`version`、`author`、`platforms`、`metadata.hermes.config`）。
- 子目录（如 `references/`、`templates/`、`scripts/`、`assets/`）会在安装时与 `SKILL.md` 一起被下载。
- 目录名以 `.` 或 `_` 开头的技能会被忽略。

Hermes 通过列出 tap 路径下的每个子目录并探测其中是否存在 `SKILL.md` 来发现技能。

<a id="minimal-tap-example"></a>
#### 最小 tap 示例

```
my-org/hermes-skills
└── skills/
    └── deploy-runbook/
        └── SKILL.md
```

`skills/deploy-runbook/SKILL.md`：

```markdown
---
name: deploy-runbook
description: 我们的部署手册——服务、回滚、Slack 频道
version: 1.0.0
author: My Org Platform Team
metadata:
  hermes:
    tags: [deployment, runbook, internal]
---

# 部署手册

步骤 1：...
```

推送到 GitHub 后，任何 Hermes 用户都可以订阅并安装：

```bash
hermes skills tap add my-org/hermes-skills
hermes skills search deploy
hermes skills install my-org/hermes-skills/deploy-runbook
```

<a id="non-default-paths"></a>
#### 非默认路径

如果你的技能不在 `skills/` 目录下（常见于将 `skills/` 子树添加到已有项目中时），请编辑 `~/.hermes/.hub/taps.json` 中的 tap 条目：

```json
{
  "taps": [
    {"repo": "my-org/platform-docs", "path": "internal/skills/"}
  ]
}
```

`hermes skills tap add` CLI 默认将新 tap 的路径设置为 `path: "skills/"`；如果需要不同路径，请直接编辑该文件。`hermes skills tap list` 会显示每个 tap 的实际生效路径。

<a id="installing-individual-skills-directly-without-adding-a-tap"></a>
#### 直接安装单个技能（不添加 tap）

用户也可以从任何公开的 GitHub 仓库直接安装单个技能，而无需将整个仓库添加为 tap：

```bash
hermes skills install owner/repo/skills/my-workflow
```

当你只想分享一个技能而不要求用户订阅整个注册表时，这个功能非常有用。

<a id="trust-levels-for-taps"></a>
#### tap 的可信等级

新添加的 tap 默认被分配 `community`（社区）可信等级。从这些 tap 安装的技能会通过标准安全扫描，并在首次安装时显示第三方警告面板。如果你的组织或广泛信任的来源应该获得更高的可信等级，请将其仓库添加到 `tools/skills_hub.py` 中的 `TRUSTED_REPOS` 中（需要 Hermes 核心 PR）。

<a id="tap-management"></a>
#### tap 管理

```bash
hermes skills tap list                                # 显示所有已配置的 tap
hermes skills tap add myorg/skills-repo               # 添加（默认路径：skills/）
hermes skills tap remove myorg/skills-repo            # 删除
```

在运行的会话中：

```
/skills tap list
/skills tap add myorg/skills-repo
/skills tap remove myorg/skills-repo
```

tap 存储在 `~/.hermes/.hub/taps.json` 中（按需创建）。

<a id="bundled-skill-updates-hermes-skills-reset"></a>
## 捆绑技能更新（`hermes skills reset`）

Hermes 附带一组捆绑技能，位于仓库内的 `skills/` 目录中。在安装时以及每次 `hermes update` 时，同步过程会将这些技能复制到 `~/.hermes/skills/` 中，并在 `~/.hermes/skills/.bundled_manifest` 中记录一个清单，该清单将每个技能名称映射到同步时对应的内容哈希值（**原始哈希值**）。
每次同步时，Hermes 会重新计算本地副本的哈希值并与原始哈希值进行比较：

- **未改变** → 可以安全拉取上游更改，复制新的捆绑版本，并记录新的原始哈希值。
- **已更改** → 被视为**用户修改**并永久跳过，因此你的编辑永远不会被覆盖。

这种保护机制很好，但有一个需要注意的陷阱。如果你编辑了一个捆绑技能，后来又想放弃更改，通过从 `~/.hermes/hermes-agent/skills/` 复制粘贴回到捆绑版本，那么 manifest 中仍然保存着上次成功同步时的*旧*原始哈希值。你新复制粘贴的内容（当前捆绑哈希值）与那个旧的原始哈希值不匹配，因此同步会继续将其标记为用户修改。

`hermes skills reset` 是逃生舱口：

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

相同的命令在聊天中也可以作为斜杠命令使用：

```text
/skills reset google-workspace
/skills reset google-workspace --restore
```

:::note 配置文件
<a id="profiles"></a>
每个配置文件在其各自的 `HERMES_HOME` 下都有自己的 `.bundled_manifest`，因此 `hermes -p coder skills reset &lt;name&gt;` 只会影响该配置文件。
:::

<a id="slash-commands-inside-chat"></a>
### 斜杠命令（聊天内）

所有相同的命令都可以通过 `/skills` 使用：

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

官方可选技能仍然使用类似 `official/security/1password` 和 `official/migration/openclaw-migration` 的标识符。
