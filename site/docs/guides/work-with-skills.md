---
sidebar_position: 12
title: "使用技能"
description: "查找、安装、使用和创建技能——按需知识文档，教会 Hermes 新的工作流程"
---

# 使用技能 {#working-with-skills}

技能是按需知识文档，教会 Hermes 如何处理特定任务——从生成 ASCII 艺术到管理 GitHub PR。本指南将带你了解日常使用方法。

完整的技术参考请参见 [技能系统](/user-guide/features/skills)。

---

## 查找技能 {#finding-skills}

每个 Hermes 安装都自带捆绑技能。查看可用的技能：

```bash
# 在任何聊天会话中：
/skills

# 或者从 CLI：
hermes skills list
```

这会显示一个紧凑的列表，包含名称和描述：

```
ascii-art         使用 pyfiglet、cowsay、boxes 等生成 ASCII 艺术
arxiv             搜索并获取 arXiv 上的学术论文...
github-pr-workflow 完整的 PR 生命周期——创建分支、提交...
plan              计划模式——检查上下文、编写 Markdown...
excalidraw        使用 Excalidraw 创建手绘风格图表...
```

### 搜索技能 {#searching-for-a-skill}

```bash
# 按关键词搜索
/skills search docker
/skills search music
```

### 技能中心 {#the-skills-hub}

官方可选技能（默认未激活的较重或小众技能）可通过中心获取：

```bash
# 浏览官方可选技能
/skills browse

# 搜索中心
/skills search blockchain
```

---

## 使用技能 {#using-a-skill}

每个已安装的技能自动成为一个斜杠命令。直接输入其名称即可：

```bash
# 加载一个技能并分配任务
/ascii-art 制作一个写着“HELLO WORLD”的横幅
/plan 为待办事项应用设计一个 REST API
/github-pr-workflow 为认证重构创建一个 PR

# 仅输入技能名称（不带任务）会加载它，然后你可以描述需求
/excalidraw
```

你也可以通过自然对话触发技能——让 Hermes 使用某个特定技能，它会通过 `skill_view` 工具加载该技能。

### 渐进式加载 {#progressive-disclosure}

技能使用一种 token 高效的加载模式。Agent 不会一次性加载所有内容：

1. **`skills_list()`** ——所有技能的紧凑列表（约 3k tokens）。在会话开始时加载。
2. **`skill_view(name)`** ——单个技能的完整 SKILL.md 内容。当 Agent 决定需要该技能时加载。
3. **`skill_view(name, file_path)`** ——技能内的特定参考文件。仅在需要时加载。

这意味着技能在真正使用之前不会消耗 tokens。

---

## 从中心安装 {#installing-from-the-hub}

官方可选技能随 Hermes 一起提供，但默认未激活。需要显式安装：

```bash
# 安装一个官方可选技能
hermes skills install official/research/arxiv

# 在聊天会话中从中心安装
/skills install official/creative/songwriting-and-ai-music

# 直接从任何 HTTP(S) URL 安装单个 SKILL.md 文件
hermes skills install https://sharethis.chat/SKILL.md
/skills install https://example.com/SKILL.md --name my-skill
```

安装过程：
1. 技能目录被复制到 `~/.hermes/skills/`
2. 它会出现在你的 `skills_list` 输出中
3. 它成为一个可用的斜杠命令

:::tip
已安装的技能在新会话中生效。如果希望它在当前会话中可用，请使用 `/reset` 重新开始，或者添加 `--now` 立即使提示缓存失效（下一次对话会消耗更多 tokens）。
:::
### 验证安装 {#verifying-installation}

```bash
# 检查是否已安装
hermes skills list | grep arxiv

# 或在聊天中
/skills search arxiv
```

---

## 插件提供的技能 {#plugin-provided-skills}

插件可以使用带命名空间的名字（`plugin:skill`）来捆绑自己的技能。这可以避免与内置技能发生名称冲突。

```bash
# 通过限定名加载插件技能
skill_view("superpowers:writing-plans")

# 同名的内置技能不受影响
skill_view("writing-plans")
```

插件技能**不会**列在系统提示中，也不会出现在 `skills_list` 中。它们是可选加入的——当你确定某个插件提供了技能时，再显式加载。加载后，agent 会看到一个横幅，列出同一插件中的其他兄弟技能。

关于如何在自己的插件中发布技能，请参阅[构建 Hermes 插件 → 捆绑技能](/guides/build-a-hermes-plugin#bundle-skills)。

---

## 配置技能设置 {#configuring-skill-settings}

有些技能会在其 frontmatter 中声明所需的配置：

```yaml
metadata:
  hermes:
    config:
      - key: tenor.api_key
        description: "用于 GIF 搜索的 Tenor API 密钥"
        prompt: "请输入您的 Tenor API 密钥"
        url: "https://developers.google.com/tenor/guides/quickstart"
```

当首次加载带有配置的技能时，Hermes 会提示你输入这些值。它们会存储在 `config.yaml` 的 `skills.config.*` 下。

通过 CLI 管理技能配置：

```bash
# 交互式配置特定技能
hermes skills config gif-search

# 查看所有技能配置
hermes config get skills.config
```

---

## 创建你自己的技能 {#creating-your-own-skill}

技能其实就是带有 YAML frontmatter 的 Markdown 文件。创建一条技能只需不到五分钟。

### 1. 创建目录 {#1-create-the-directory}

```bash
mkdir -p ~/.hermes/skills/my-category/my-skill
```

### 2. 编写 SKILL.md {#2-write-skill-md}

```markdown title="~/.hermes/skills/my-category/my-skill/SKILL.md"
---
name: my-skill
description: 简要描述此技能的功能
version: 1.0.0
metadata:
  hermes:
    tags: [my-tag, automation]
    category: my-category
---

# 我的技能

## 何时使用
当用户询问 [特定主题] 或需要 [特定任务] 时，使用此技能。

## 操作步骤
1. 首先，检查 [前提条件] 是否可用
2. 运行 `command --with-flags`
3. 解析输出并呈现结果

## 常见陷阱
- 常见失败：[描述]。修复方法：[解决方案]
- 注意 [边界情况]

## 验证
运行 `check-command` 以确认结果正确。
```

### 3. 添加参考文件（可选） {#3-add-reference-files-optional}

技能可以包含 agent 按需加载的支持文件：

```
my-skill/
├── SKILL.md                    # 主技能文档
├── references/
│   ├── api-docs.md             # agent 可查阅的 API 参考
│   └── examples.md             # 示例输入/输出
├── templates/
│   └── config.yaml             # agent 可使用的模板文件
└── scripts/
    └── setup.sh                # agent 可执行的脚本
```

在 SKILL.md 中引用这些文件：

```markdown
如需 API 详情，请加载参考文件：`skill_view("my-skill", "references/api-docs.md")`
```
### 4. 测试 {#4-test-it}

启动一个新会话并尝试你的技能：

```bash
hermes chat -q "/my-skill help me with the thing"
```

技能会自动出现——无需注册。放到 `~/.hermes/skills/` 目录下即可直接使用。

:::info
Agent 也可以使用 `skill_manage` 自行创建和更新技能。在解决一个复杂问题后，Hermes 可能会主动提出将当前方案保存为技能，供下次使用。
:::

---

## 按平台管理技能 {#per-platform-skill-management}

控制哪些技能在哪些平台上可用：

```bash
hermes skills
```

这会打开一个交互式 TUI，你可以在其中针对每个平台（CLI、Telegram、Discord 等）启用或禁用技能。当你希望某些技能只在特定场景下可用时非常有用——例如，不让开发技能出现在 Telegram 上。

---

## 技能 vs 记忆 {#skills-vs-memory}

两者都会跨会话持久化，但用途不同：

| | 技能 | 记忆 |
|---|---|---|
| **内容** | 过程性知识——如何做某事 | 事实性知识——某事是什么 |
| **加载时机** | 按需加载，只在相关时触发 | 自动注入到每次会话中 |
| **大小** | 可以很大（数百行） | 应保持精简（仅关键事实） |
| **成本** | 加载前零 token 消耗 | 持续消耗少量 token |
| **示例** | “如何部署到 Kubernetes” | “用户偏好深色模式，居住于 PST 时区” |
| **创建者** | 你、Agent，或从 Hub 安装 | Agent，基于对话生成 |

**经验法则：** 如果要放在参考文档里，那就是技能；如果只是写个便签贴，那就是记忆。

---

## 小贴士 {#tips}

**保持技能聚焦。** 一个试图覆盖“全部 DevOps”的技能会过于冗长且模糊。而一个覆盖“将 Python 应用部署到 Fly.io”的技能则足够具体，真正有用。

**让 Agent 创建技能。** 在执行完一个复杂的多步骤任务后，Hermes 通常会主动提议将方案保存为技能。同意即可——这些由 Agent 编写的技能精确涵盖了整个工作流，包括过程中发现的陷阱。

**使用分类。** 将技能组织到子目录中（例如 `~/.hermes/skills/devops/`、`~/.hermes/skills/research/` 等）。这样可以让列表更清晰，并帮助 Agent 更快地找到相关技能。

**技能过时后及时更新。** 如果你使用某个技能时遇到了未涵盖的问题，请告诉 Hermes 根据你的新经验更新该技能。未经维护的技能会变成累赘。

---

*完整的技能参考文档——包括 frontmatter 字段、条件激活、外部目录等——请参见 [技能系统](/user-guide/features/skills)。*
