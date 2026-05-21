---
sidebar_position: 3
title: "创建技能"
description: "如何为 Hermes Agent 创建技能 —— SKILL.md 格式、指南与发布"
---

<a id="creating-skills"></a>
# 创建技能

技能是向 Hermes Agent 添加新能力的首选方式。它们比工具更容易创建，无需修改 Agent 代码，并且可以与社区共享。

<a id="should-it-be-a-skill-or-a-tool"></a>
## 该做成技能还是工具？

遇到以下情况时，做成**技能**：
- 能力可以通过指令 + shell 命令 + 现有工具来表达
- 它封装了一个外部 CLI 或 API，Agent 可以通过 `terminal` 或 `web_extract` 调用
- 它不需要将自定义 Python 集成或 API 密钥管理硬编码到 Agent 中
- 例如：arXiv 搜索、git 工作流、Docker 管理、PDF 处理、通过 CLI 工具发送邮件

遇到以下情况时，做成**工具**：
- 需要端到端集成 API 密钥、认证流程或多组件配置
- 需要每次精确执行的自定义处理逻辑
- 处理二进制数据、流式数据或实时事件
- 例如：浏览器自动化、TTS、视觉分析

<a id="skill-directory-structure"></a>
## 技能目录结构

捆绑的技能放在 `skills/` 下，按类别组织。官方可选技能使用相同的结构放在 `optional-skills/` 中：

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

<a id="skill-md-format"></a>
## SKILL.md 格式

```markdown
---
name: my-skill
description: 简短描述（在技能搜索结果中显示）
version: 1.0.0
author: 您的名字
license: MIT
platforms: [macos, linux]          # 可选 —— 限制到特定操作系统平台
                                   #   有效值：macos, linux, windows
                                   #   省略则在所有平台上加载（默认）
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    requires_toolsets: [web]            # 可选 —— 仅当这些工具集激活时显示
    requires_tools: [web_search]        # 可选 —— 仅当这些工具可用时显示
    fallback_for_toolsets: [browser]    # 可选 —— 当这些工具集激活时隐藏
    fallback_for_tools: [browser_navigate]  # 可选 —— 当这些工具存在时隐藏
    config:                              # 可选 —— 技能所需的 config.yaml 设置
      - key: my.setting
        description: "此设置控制的内容"
        default: "sensible-default"
        prompt: "用于设置的显示提示"
required_environment_variables:          # 可选 —— 技能所需的环境变量
  - name: MY_API_KEY
    prompt: "输入您的 API 密钥"
    help: "在 https://example.com 获取"
    required_for: "API 访问"
---

# 技能标题

简短介绍。

## 何时使用
触发条件 —— 什么时候 Agent 应该加载这个技能？

## 快速参考
常用命令或 API 调用的表格。

## 操作步骤
Agent 遵循的逐步说明。

## 常见陷阱
已知的失败模式及如何处理它们。

## 验证
Agent 如何确认操作成功。
```
<a id="platform-specific-skills"></a>
### 平台特定的技能

技能可以使用 `platforms` 字段限制自身只在特定操作系统上运行：

```yaml
platforms: [macos]            # 仅 macOS（如 iMessage、Apple Reminders）
platforms: [macos, linux]     # macOS 和 Linux
platforms: [windows]          # 仅 Windows
```

当设置了该字段后，技能在不兼容的平台上会自动从系统提示、`skills_list()` 和斜杠命令中隐藏。如果省略或留空，技能则会在所有平台上加载（向后兼容）。

<a id="conditional-skill-activation"></a>
### 条件性的技能激活

技能可以声明对特定工具或工具集的依赖。这控制着技能是否会出现在给定会话的系统提示中。

```yaml
metadata:
  hermes:
    requires_toolsets: [web]           # 如果 web 工具集未激活，则隐藏
    requires_tools: [web_search]       # 如果 web_search 工具不可用，则隐藏
    fallback_for_toolsets: [browser]   # 如果 browser 工具集已激活，则隐藏
    fallback_for_tools: [browser_navigate]  # 如果 browser_navigate 工具可用，则隐藏
```

| 字段 | 行为 |
|-------|----------|
| `requires_toolsets` | 当**任何**列出的工具集**不可用**时，技能被**隐藏** |
| `requires_tools` | 当**任何**列出的工具**不可用**时，技能被**隐藏** |
| `fallback_for_toolsets` | 当**任何**列出的工具集**可用**时，技能被**隐藏** |
| `fallback_for_tools` | 当**任何**列出的工具**可用**时，技能被**隐藏** |

**`fallback_for_*` 的使用场景：** 创建一个当主工具不可用时的替代技能。例如，一个 `duckduckgo-search` 技能设置了 `fallback_for_tools: [web_search]`，只有当网络搜索工具（需要 API 密钥）未配置时才显示。

**`requires_*` 的使用场景：** 创建一个只有某些工具存在时才有效的技能。例如，一个网页抓取工作流技能设置了 `requires_toolsets: [web]`，当网页工具被禁用时就不会杂乱地出现在提示中。

<a id="environment-variable-requirements"></a>
### 环境变量要求

技能可以声明其所需的环境变量。当通过 `skill_view` 加载技能时，其所需的变量会自动注册，以便透传至沙箱执行环境（终端、execute_code）。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: "Tenor API key"               # 提示用户时显示
    help: "Get your key at https://tenor.com"  # 帮助文本或 URL
    required_for: "GIF search functionality"   # 需要此变量的功能
```

每个条目支持：
- `name`（必填）— 环境变量名称
- `prompt`（可选）— 向用户请求值时显示的提示文本
- `help`（可选）— 获取该值的帮助文本或 URL
- `required_for`（可选）— 描述需要此变量的功能

用户也可以在 `config.yaml` 中手动配置透传变量：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_VAR
    - ANOTHER_VAR
```

有关仅适用于 macOS 的技能示例，请参见 `skills/apple/`。

<a id="secure-setup-on-load"></a>
## 加载时的安全设置
当技能需要 API 密钥或令牌时，使用 `required_environment_variables`。缺失的值**不会**隐藏技能使其不被发现。相反，Hermes 会在本地 CLI 加载技能时安全地提示输入这些值。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

用户可以跳过设置并继续加载技能。Hermes 永远不会将原始秘密值暴露给模型。网关和消息会话会显示本地设置指南，而不是带内收集密钥。

:::tip 沙箱传递
<a id="sandbox-passthrough"></a>
您的技能加载后，任何已设置的已声明的 `required_environment_variables` 都会被**自动传递**到 `execute_code` 和 `terminal` 沙箱——包括远程后端（如 Docker 和 Modal）。您的技能脚本可以访问 `$TENOR_API_KEY`（或 Python 中的 `os.environ["TENOR_API_KEY"]`），而无需用户额外配置。详情请参阅[环境变量传递](/user-guide/security#environment-variable-passthrough)。
:::

遗留的 `prerequisites.env_vars` 仍然作为向后兼容的别名得到支持。

<a id="config-settings-config-yaml"></a>
### 配置设置 (config.yaml) {#config-settings-configyaml}

技能可以声明非秘密的设置，这些设置存储在 `config.yaml` 中的 `skills.config` 命名空间下。与环境变量（存储于 `.env` 中的秘密）不同，配置设置用于路径、偏好设置和其他非敏感值。

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
- `key`（必需）——设置的 dotpath（例如 `myplugin.path`）
- `description`（必需）——解释该设置控制什么
- `default`（可选）——如果用户未配置，则使用默认值
- `prompt`（可选）——在 `hermes config migrate` 期间显示的提示文本；回退到 `description`

**工作原理：**

1. **存储：** 值被写入 `config.yaml` 中的 `skills.config.&lt;key&gt;` 下：
   ```yaml
   skills:
     config:
       myplugin:
         path: ~/my-data
   ```

2. **发现：** `hermes config migrate` 扫描所有启用的技能，找到未配置的设置，并提示用户。设置也会出现在 `hermes config show` 的“Skill Settings”下。

3. **运行时注入：** 当技能加载时，其配置值被解析并附加到技能消息中：
   ```
   [Skill config (from ~/.hermes/config.yaml):
     myplugin.path = /home/user/my-data
   ]
   ```
   Agent 看到配置的值，而无需自己读取 `config.yaml`。

4. **手动设置：** 用户也可以直接设置值：
   ```bash
   hermes config set skills.config.myplugin.path ~/my-data
   ```

<a id="when-to-use-which"></a>
:::tip 何时使用哪种方式
使用 `required_environment_variables` 来存储 API 密钥、令牌和其他**秘密**（存储在 `~/.hermes/.env` 中，永远不会展示给模型）。使用 `config` 来存储**路径、偏好设置和非敏感设置**（存储在 `config.yaml` 中，可在 `config show` 中查看）。
:::
<a id="credential-file-requirements-oauth-tokens-etc"></a>
### 凭据文件要求（OAuth 令牌等）

使用 OAuth 或文件型凭据的技能可以声明需要挂载到远程沙箱中的文件。这适用于以**文件**形式存储的凭据（而不是环境变量）——通常是设置脚本生成的 OAuth 令牌文件。

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 令牌（由设置脚本创建）
  - path: google_client_secret.json
    description: Google OAuth2 客户端凭据
```

每个条目支持以下属性：
- `path`（必需）——相对于 `~/.hermes/` 的文件路径
- `description`（可选）——说明该文件是什么以及如何创建

加载时，Hermes 会检查这些文件是否存在。缺失的文件会触发 `setup_needed`。已有的文件会自动：
- **挂载到 Docker** 容器中，作为只读绑定挂载
- **同步到 Modal** 沙箱中（在创建时 + 每条命令之前，以便在会话期间 OAuth 正常工作）
- **本地**后端下无需特殊处理即可使用

:::tip 何时使用哪种方式
简单的 API 密钥和令牌（存储在 `~/.hermes/.env` 中的字符串）请使用 `required_environment_variables`。OAuth 令牌文件、客户端密钥、服务账号 JSON、证书等磁盘上的文件型凭据，请使用 `required_credential_files`。
:::

完整的示例（同时使用了这两种方式）请参见 `skills/productivity/google-workspace/SKILL.md`。

<a id="when-to-use-which"></a>
<a id="skill-guidelines"></a>
## 技能指南

<a id="no-external-dependencies"></a>
### 不依赖外部资源

优先使用 stdlib 的 Python、curl 以及已有的 Hermes 工具（`web_extract`、`terminal`、`read_file`）。如果确实需要依赖，请在技能中记录安装步骤。

<a id="progressive-disclosure"></a>
### 渐进式呈现

将最常见的操作流程放在最前面。边缘情况和高级用法放在底部。这样可以减少常见任务的令牌消耗。

<a id="include-helper-scripts"></a>
### 包含辅助脚本

对于 XML/JSON 解析或复杂逻辑，请将辅助脚本放在 `scripts/` 目录中——不要期望 LLM 每次内联编写解析器。

<a id="deliver-media-as-documents-asdocument"></a>
### 以文档形式交付媒体（`[[as_document]]`）

如果你的技能生成了高分辨率截图、图表或任何有损预览压缩会损害质量的图像——请在响应的某个位置（通常是最后一行）输出字面指令 `[[as_document]]`。网关会去掉该指令，并将该响应中提取的每个媒体路径作为可下载的文件附件交付，而不是内联图像气泡。完整语义请参见[技能输出与媒体交付](../user-guide/features/skills.md#skill-output-and-media-delivery)。

<a id="referencing-bundled-scripts-from-skill-md"></a>
#### 从 SKILL.md 中引用捆绑脚本

当技能加载时，激活消息会将技能目录的绝对路径暴露为 `[Skill directory: /abs/path]`，并在 SKILL.md 正文中的任意位置替换两个模板令牌：

| 令牌 | 替换为 |
|---|---|
| `${HERMES_SKILL_DIR}` | 技能目录的绝对路径 |
| `${HERMES_SESSION_ID}` | 当前会话 ID（如果没有会话则保留原位） |

因此，SKILL.md 可以通过以下方式告诉 Agent 直接运行捆绑脚本：

```markdown
要分析输入，请运行：

    node ${HERMES_SKILL_DIR}/scripts/analyse.js <input>
```
Agent 看到替换后的绝对路径，并调用 `terminal` 工具，传入一个可直接运行的命令——无需路径计算，无需额外的 `skill_view` 往返。如果要全局禁用替换，在 `config.yaml` 中设置 `skills.template_vars: false`。

<a id="inline-shell-snippets-opt-in"></a>
#### 内联 Shell 代码片段（可选）

技能还可以在 SKILL.md 正文中嵌入以 `` !`cmd` `` 形式编写的内联 Shell 代码片段。启用后，每个代码片段的 stdout 会在 Agent 读取消息之前内联到消息中，因此技能可以注入动态上下文：

```markdown
当前日期: !`date -u +%Y-%m-%d`
Git 分支: !`git -C ${HERMES_SKILL_DIR} rev-parse --abbrev-ref HEAD`
```

**默认关闭**——SKILL.md 中的任何代码片段都会不经审批在主机上运行，因此请只为你信任的技能来源启用：

```yaml
# config.yaml
skills:
  inline_shell: true
  inline_shell_timeout: 10   # 每个代码片段的超时秒数
```

代码片段以技能目录作为工作目录运行，输出限制为 4000 个字符。出现故障（超时、非零退出）时，会显示简短的 `[inline-shell error: ...]` 标记，而不会破坏整个技能。

<a id="test-it"></a>
### 测试

运行技能并验证 Agent 是否正确遵循指令：

```bash
hermes chat --toolsets skills -q "使用 X 技能执行 Y 操作"
```

<a id="where-should-the-skill-live"></a>
## 技能应该放在哪里？

内置技能（`skills/` 目录下）随每次 Hermes 安装一起提供。它们应该**对大多数用户具有广泛实用性**：

- 文档处理、网络研究、常见开发工作流、系统管理
- 被大量用户定期使用

如果你的技能是官方且有用的，但并非普遍需要（例如付费服务集成、重型依赖），请将其放在 **`optional-skills/`** 目录下——它会随仓库一起发布，可通过 `hermes skills browse` 发现（标记为“官方”），并且安装时拥有内置信任。

如果你的技能是专业化的、社区贡献的或小众的，它更适合放在 **Skills Hub** 中——将其上传到注册表，并通过 `hermes skills install` 分享。

<a id="publishing-skills"></a>
## 发布技能

<a id="to-the-skills-hub"></a>
### 发布到 Skills Hub

```bash
hermes skills publish skills/my-skill --to github --repo owner/repo
```

<a id="to-a-custom-repository"></a>
### 发布到自定义仓库

将你的仓库添加为 tap：

```bash
hermes skills tap add owner/repo
```

用户随后可以从你的仓库搜索并安装。

<a id="security-scanning"></a>
## 安全扫描

所有从 hub 安装的技能都会经过安全扫描器检查以下内容：

- 数据外泄模式
- 提示注入尝试
- 破坏性命令
- Shell 注入

信任级别：
- `builtin` — 随 Hermes 一起提供（始终受信任）
- `official` — 来自仓库中的 `optional-skills/`（内置信任，无第三方警告）
- `trusted` — 来自 openai/skills、anthropics/skills、huggingface/skills
- `community` — 非危险发现可通过 `--force` 覆盖；`dangerous` 判定仍被阻止

Hermes 现在可以从多种外部发现模型消费第三方技能：
- 直接 GitHub 标识符（例如 `openai/skills/k8s`）
- `skills.sh` 标识符（例如 `skills-sh/vercel-labs/json-render/json-render-react`）
- 从 `/.well-known/skills/index.json` 提供的知名端点
如果你希望你的技能无需特定于 GitHub 的安装程序即可被发现，可以考虑除了在仓库或市场发布它们之外，还从一个众所周知的端点提供它们。
