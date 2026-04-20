---
sidebar_position: 3
title: "创建 Skill"
description: "如何为 Hermes Agent 创建 Skill —— SKILL.md 格式、编写指南与发布方式"
---

# 创建 Skill {#creating-skills}

Skill 是为 Hermes Agent 添加新能力的首选方式。它比 Tool 更容易创建，不需要修改 Agent 的代码，还能与社区分享。

## 应该做成 Skill 还是 Tool？ {#should-it-be-a-skill-or-a-tool}

做成 **Skill** 的情况：
- 能力可以通过指令 + shell 命令 + 现有 Tool 来表达
- 它封装了一个外部 CLI 或 API，Agent 可以通过 `terminal` 或 `web_extract` 调用
- 不需要在 Agent 内部集成自定义 Python 代码或管理 API 密钥
- 例如：arXiv 搜索、git 工作流、Docker 管理、PDF 处理、通过 CLI 工具发送邮件

做成 **Tool** 的情况：
- 需要端到端集成 API 密钥、认证流程或多组件配置
- 需要每次精确执行的自定义处理逻辑
- 涉及二进制数据、流式传输或实时事件
- 例如：浏览器自动化、TTS、视觉分析

## Skill 目录结构 {#skill-directory-structure}

内置 Skill 放在 `skills/` 目录下，按类别组织。官方可选 Skill 在 `optional-skills/` 中使用相同的结构：

```text
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md              # 必需：主指令文件
│       └── scripts/              # 可选：辅助脚本
│           └── search_arxiv.py
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── ...
```

## SKILL.md 格式 {#skill-md-format}

```markdown
---
name: my-skill
description: 简要描述（显示在 Skill 搜索结果中）
version: 1.0.0
author: Your Name
license: MIT
platforms: [macos, linux]          # 可选 —— 限制特定操作系统平台
                                   #   有效值：macos, linux, windows
                                   #   省略则在所有平台加载（默认）
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    requires_toolsets: [web]            # 可选 —— 仅当这些 Toolset 激活时显示
    requires_tools: [web_search]        # 可选 —— 仅当这些 Tool 可用时显示
    fallback_for_toolsets: [browser]    # 可选 —— 当这些 Toolset 激活时隐藏
    fallback_for_tools: [browser_navigate]  # 可选 —— 当这些 Tool 存在时隐藏
    config:                              # 可选 —— Skill 需要的 config.yaml 设置
      - key: my.setting
        description: "此设置控制什么"
        default: "合理默认值"
        prompt: "设置时显示的提示"
required_environment_variables:          # 可选 —— Skill 需要的环境变量
  - name: MY_API_KEY
    prompt: "输入你的 API 密钥"
    help: "在 https://example.com 获取"
    required_for: "API 访问"
---

# Skill 标题

简要介绍。

## 何时使用
触发条件 —— Agent 应该在什么时候加载这个 Skill？

## 速查表
常用命令或 API 调用的表格。

## 操作流程
Agent 遵循的分步指令。

## 常见陷阱
已知的失败模式及处理方法。

## 验证方式
Agent 如何确认操作成功。
```

### 平台专属 Skill {#platform-specific-skills}

Skill 可以通过 `platforms` 字段限制特定操作系统：

```yaml
platforms: [macos]            # 仅限 macOS（例如：iMessage、Apple 提醒事项）
platforms: [macos, linux]     # macOS 和 Linux
platforms: [windows]          # 仅限 Windows
```

设置后，Skill 会在不兼容的平台上自动从系统提示词、`skills_list()` 和斜杠命令中隐藏。如果省略或留空，Skill 会在所有平台加载（向后兼容）。

### 条件激活 Skill {#conditional-skill-activation}

Skill 可以声明对特定 Tool 或 Toolset 的依赖。这控制 Skill 是否出现在当前会话的系统提示词中。

```yaml
metadata:
  hermes:
    requires_toolsets: [web]           # 如果 web Toolset 未激活则隐藏
    requires_tools: [web_search]       # 如果 web_search Tool 不可用则隐藏
    fallback_for_toolsets: [browser]   # 如果 browser Toolset 已激活则隐藏
    fallback_for_tools: [browser_navigate]  # 如果 browser_navigate 可用则隐藏
```
| 字段 | 行为 |
|-------|----------|
| `requires_toolsets` | 当列出的**任一** toolset **不可用时**，Skill **隐藏** |
| `requires_tools` | 当列出的**任一** tool **不可用时**，Skill **隐藏** |
| `fallback_for_toolsets` | 当列出的**任一** toolset **可用时**，Skill **隐藏** |
| `fallback_for_tools` | 当列出的**任一** tool **可用时**，Skill **隐藏** |

**`fallback_for_*` 的用例：** 创建一个在主工具不可用时作为替代方案的 Skill。例如，一个带有 `fallback_for_tools: [web_search]` 的 `duckduckgo-search` Skill，只在网页搜索工具（需要 API key）未配置时才显示。

**`requires_*` 的用例：** 创建只在特定工具存在时才有意义的 Skill。例如，一个带有 `requires_toolsets: [web]` 的网页抓取工作流 Skill，在网页工具禁用时不会出现在提示中，避免干扰。

### 环境变量要求 {#environment-variable-requirements}

Skill 可以声明所需的环境变量。当 Skill 通过 `skill_view` 加载时，其必需的变量会自动注册，透传到沙箱执行环境（terminal、execute_code）。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: "Tenor API key"               # 询问用户时显示的提示
    help: "Get your key at https://tenor.com"  # 帮助文本或 URL
    required_for: "GIF search functionality"   # 哪个功能需要该变量
```

每个条目支持：
- `name`（必需）—— 环境变量名称
- `prompt`（可选）—— 向用户询问值时的提示文本
- `help`（可选）—— 获取该值的帮助文本或 URL
- `required_for`（可选）—— 描述哪个功能需要此变量

用户也可以在 `config.yaml` 中手动配置透传变量：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_VAR
    - ANOTHER_VAR
```

参见 `skills/apple/` 目录，了解仅限 macOS 的 Skill 示例。

## 加载时的安全设置 {#secure-setup-on-load}

当 Skill 需要 API key 或 token 时，使用 `required_environment_variables`。缺失的值**不会**让 Skill 从发现列表中隐藏。相反，Hermes 会在 Skill 于本地 CLI 加载时，安全地提示用户输入。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

用户可以跳过设置并继续加载 Skill。Hermes 绝不会将原始密钥值暴露给模型。Gateway 和消息会话会显示本地设置指引，而不是在通信过程中收集密钥。

:::tip 沙箱透传
<a id="sandbox-passthrough"></a>
当 Skill 加载时，任何已设置的 `required_environment_variables` 都会**自动透传**到 `execute_code` 和 `terminal` 沙箱 —— 包括 Docker 和 Modal 等远程后端。Skill 的脚本可以直接访问 `$TENOR_API_KEY`（或 Python 中的 `os.environ["TENOR_API_KEY"]`），无需用户额外配置。详见[环境变量透传](/user-guide/security#environment-variable-passthrough)。
:::

旧的 `prerequisites.env_vars` 仍作为向后兼容的别名受支持。

<a id="config-settings-config-yaml"></a>
### 配置项（config.yaml） {#config-settings-configyaml}

Skill 可以声明非密钥类设置，这些设置存储在 `config.yaml` 的 `skills.config` 命名空间下。与环境变量（存储在 `.env` 中的密钥）不同，配置项用于路径、偏好设置和其他非敏感值。

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
      - key: myplugin.domain
        description: Domain the plugin operates on
        default: ""
        prompt: Plugin domain (e.g., AI/ML research)
```

每个条目支持：
- `key`（必需）—— 设置的点分路径（例如 `myplugin.path`）
- `description`（必需）—— 说明该设置控制什么
- `default`（可选）—— 用户未配置时的默认值
- `prompt`（可选）—— `hermes config migrate` 时显示的提示文本；未指定时回退到 `description`
**工作原理：**

1. **存储：** 数值写入 `config.yaml` 的 `skills.config.&lt;key&gt;` 下：
   ```yaml
   skills:
     config:
       myplugin:
         path: ~/my-data
   ```

2. **发现：** `hermes config migrate` 会扫描所有已启用的技能，找到未配置的设置，并提示用户。设置也会显示在 `hermes config show` 的 "Skill Settings" 下。

3. **运行时注入：** 技能加载时，其配置值会被解析并附加到技能消息中：
   ```
   [Skill config (from ~/.hermes/config.yaml):
     myplugin.path = /home/user/my-data
   ]
   ```
   Agent 可以直接看到配置值，无需自己读取 `config.yaml`。

4. **手动设置：** 用户也可以直接设置数值：
   ```bash
   hermes config set skills.config.myplugin.path ~/my-data
   ```

:::tip 什么时候用哪个
用 `required_environment_variables` 存 API key、token 等**敏感信息**（存在 `~/.hermes/.env`，永远不会展示给模型）。用 `config` 存**路径、偏好和非敏感设置**（存在 `config.yaml`，config show 里可见）。
:::

### 凭证文件要求（OAuth token 等） {#credential-file-requirements-oauth-tokens-etc}

使用 OAuth 或基于文件的凭证的技能，可以声明需要挂载到远程沙箱的文件。这针对以**文件**形式存储的凭证（不是环境变量）—— 通常是 setup 脚本生成的 OAuth token 文件。

<a id="when-to-use-which"></a>
```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials
```

每个条目支持：
- `path`（必填）—— 相对于 `~/.hermes/` 的文件路径
- `description`（可选）—— 说明文件是什么以及如何创建

加载时，Hermes 会检查这些文件是否存在。缺失的文件会触发 `setup_needed`。已有文件会自动：
- 以只读 bind mount 形式**挂载到 Docker** 容器
- **同步到 Modal** 沙箱（创建时 + 每条命令前，因此 mid-session OAuth 可用）
- 在**本地**后端无需特殊处理即可使用

:::tip 什么时候用哪个
用 `required_environment_variables` 存简单的 API key 和 token（字符串，存在 `~/.hermes/.env`）。用 `required_credential_files` 存 OAuth token 文件、client secret、service account JSON、证书，或任何磁盘上的凭证文件。
:::

完整示例请见 `skills/productivity/google-workspace/SKILL.md`，其中同时使用了两种方式。

## 技能编写指南 {#skill-guidelines}

### 不要依赖外部库 {#no-external-dependencies}

优先使用 Python 标准库、curl 和现有的 Hermes 工具（`web_extract`、`terminal`、`read_file`）。如果确实需要依赖，在技能中写明安装步骤。

### 渐进式披露 {#progressive-disclosure}

把最常见的流程放前面。边缘情况和高级用法放底部。这样常见任务的 token 消耗更低。

### 包含辅助脚本 {#include-helper-scripts}

对于 XML/JSON 解析或复杂逻辑，把辅助脚本放在 `scripts/` 里 —— 别让 LLM 每次都在线写解析器。

### 测试一下 {#test-it}

运行技能，验证 Agent 是否按说明正确执行：

```bash
hermes chat --toolsets skills -q "Use the X skill to do Y"
```

## 技能应该放在哪里？ {#where-should-the-skill-live}

捆绑技能（放在 `skills/`）会随每次 Hermes 安装一起分发。它们应该**对大多数用户都有广泛用处**：

- 文档处理、网页调研、常见开发工作流、系统管理
- 被各类人群定期使用

如果你的技能是官方技能且有用，但并非人人需要（例如付费服务集成、重量级依赖），把它放到 **`optional-skills/`** —— 它会随仓库一起分发，可通过 `hermes skills browse` 发现（标记为 "official"），安装时自带信任。

如果你的技能很专业、由社区贡献或比较小众，更适合放到 **Skills Hub** —— 上传到注册中心，通过 `hermes skills install` 分享。

## 发布技能 {#publishing-skills}

### 发布到 Skills Hub {#to-the-skills-hub}

```bash
hermes skills publish skills/my-skill --to github --repo owner/repo
```
### 添加到自定义仓库 {#to-a-custom-repository}

把你的仓库添加为一个 tap：

```bash
hermes skills tap add owner/repo
```

之后用户就可以从你的仓库搜索和安装技能了。

## 安全扫描 {#security-scanning}

所有通过 Hub 安装的技能都会经过安全扫描，检查内容包括：

- 数据外泄模式
- 提示注入尝试
- 破坏性命令
- Shell 注入

信任等级：
- `builtin` — 随 Hermes 一起发布（始终信任）
- `official` — 来自仓库中的 `optional-skills/`（等同于 builtin 信任，无第三方警告）
- `trusted` — 来自 openai/skills、anthropics/skills
- `community` — 非危险发现可以用 `--force` 覆盖；`dangerous` 判定仍然会被阻止

Hermes 现在可以通过多种外部发现模型消费第三方技能：
- 直接的 GitHub 标识符（例如 `openai/skills/k8s`）
- `skills.sh` 标识符（例如 `skills-sh/vercel-labs/json-render/json-render-react`）
- 从 `/.well-known/skills/index.json` 提供的 well-known 端点

如果你希望技能在不依赖 GitHub 专属安装器的情况下也能被发现，可以考虑除了发布到仓库或市场之外，再通过 well-known 端点提供服务。
