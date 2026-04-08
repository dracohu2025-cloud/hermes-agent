---
sidebar_position: 12
title: "使用 Skills"
description: "查找、安装、使用和创建 Skills —— 教会 Hermes 新工作流的按需知识库"
---

# 使用 Skills

Skills 是按需加载的知识文档，用于教会 Hermes 如何处理特定任务 —— 从生成 ASCII 艺术到管理 GitHub PR。本指南将带你了解如何在日常工作中使用它们。

如需完整的技术参考，请参阅 [Skills 系统](/user-guide/features/skills)。

---

## 查找 Skills

每个 Hermes 安装包都自带了一些内置 Skills。查看可用内容：

```bash
# 在任何聊天会话中：
/skills

# 或者通过 CLI：
hermes skills list
```

这将显示一个包含名称和描述的精简列表：

```
ascii-art         使用 pyfiglet, cowsay, boxes 生成 ASCII 艺术...
arxiv             从 arXiv 搜索并检索学术论文...
github-pr-workflow 完整的 PR 生命周期 —— 创建分支、提交...
plan              计划模式 —— 检查上下文，编写 markdown...
excalidraw        使用 Excalidraw 创建手绘风格的图表...
```

### 搜索 Skill

```bash
# 按关键词搜索
/skills search docker
/skills search music
```

### Skills Hub

官方可选 Skills（默认未激活的较重或小众 Skills）可以通过 Hub 获取：

```bash
# 浏览官方可选 Skills
/skills browse

# 搜索 Hub
/skills search blockchain
```

---

## 使用 Skill

每个安装好的 Skill 都会自动成为一个斜杠命令。只需输入它的名称：

```bash
# 加载一个 Skill 并分配任务
/ascii-art Make a banner that says "HELLO WORLD"
/plan Design a REST API for a todo app
/github-pr-workflow Create a PR for the auth refactor

# 仅输入 Skill 名称（不带任务）会加载它并让你描述需求
/excalidraw
```

你也可以通过自然对话触发 Skills —— 要求 Hermes 使用特定的 Skill，它会通过 `skill_view` 工具进行加载。

### 渐进式披露

Skills 使用一种节省 Token 的加载模式。Agent 不会一次性加载所有内容：

1. **`skills_list()`** —— 所有 Skills 的精简列表（约 3k tokens）。在会话开始时加载。
2. **`skill_view(name)`** —— 单个 Skill 的完整 `SKILL.md` 内容。当 Agent 决定需要该 Skill 时加载。
3. **`skill_view(name, file_path)`** —— Skill 内部的特定参考文件。仅在需要时加载。

这意味着 Skills 在实际使用之前不会消耗 Token。

---

## 从 Hub 安装

官方可选 Skills 随 Hermes 一起发布，但默认不激活。需要显式安装它们：

```bash
# 安装官方可选 Skill
hermes skills install official/research/arxiv

# 在聊天会话中从 Hub 安装
/skills install official/creative/songwriting-and-ai-music
```

安装过程如下：
1. Skill 目录被复制到 `~/.hermes/skills/`
2. 它会出现在你的 `skills_list` 输出中
3. 它变得可以作为斜杠命令使用

:::tip
安装的 Skills 在新会话中生效。如果你想在当前会话中使用，请使用 `/reset` 重新开始，或者添加 `--now` 参数立即失效 Prompt 缓存（下次对话会消耗更多 Token）。
:::

### 验证安装

```bash
# 检查是否存在
hermes skills list | grep arxiv

# 或在聊天中
/skills search arxiv
```

---

## 配置 Skill 设置

某些 Skills 在其 frontmatter 中声明了所需的配置：

```yaml
metadata:
  hermes:
    config:
      - key: tenor.api_key
        description: "用于 GIF 搜索的 Tenor API 密钥"
        prompt: "请输入您的 Tenor API 密钥"
        url: "https://developers.google.com/tenor/guides/quickstart"
```

当带有配置要求的 Skill 第一次被加载时，Hermes 会提示你输入这些值。它们存储在 `config.yaml` 的 `skills.config.*` 下。

通过 CLI 管理 Skill 配置：

```bash
# 交互式配置特定 Skill
hermes skills config gif-search

# 查看所有 Skill 配置
hermes config get skills.config
```

---

## 创建你自己的 Skill

Skills 只是带有 YAML frontmatter 的 Markdown 文件。创建一个只需不到五分钟。

### 1. 创建目录

```bash
mkdir -p ~/.hermes/skills/my-category/my-skill
```

### 2. 编写 SKILL.md

```markdown title="~/.hermes/skills/my-category/my-skill/SKILL.md"
---
name: my-skill
description: 简要描述这个 skill 的作用
version: 1.0.0
metadata:
  hermes:
    tags: [my-tag, automation]
    category: my-category
---

# My Skill

## 何时使用
当用户询问 [特定主题] 或需要 [特定任务] 时使用此 skill。

## 流程
1. 首先，检查 [前提条件] 是否可用
2. 运行 `command --with-flags`
3. 解析输出并展示结果

## 常见陷阱
- 常见失败：[描述]。修复方法：[解决方案]
- 注意 [边缘情况]

## 验证
运行 `check-command` 以确认结果正确。
```

### 3. 添加参考文件（可选）

Skills 可以包含 Agent 按需加载的辅助文件：

```
my-skill/
├── SKILL.md                    # 主 Skill 文档
├── references/
│   ├── api-docs.md             # Agent 可以查阅的 API 参考
│   └── examples.md             # 示例输入/输出
├── templates/
│   └── config.yaml             # Agent 可以使用的模板文件
└── scripts/
    └── setup.sh                # Agent 可以执行的脚本
```

在你的 `SKILL.md` 中引用这些文件：

```markdown
有关 API 详情，请加载参考文档：`skill_view("my-skill", "references/api-docs.md")`
```

### 4. 测试

开启一个新会话并尝试你的 Skill：

```bash
hermes chat -q "/my-skill help me with the thing"
```

该 Skill 会自动出现 —— 无需注册。只需将其放入 `~/.hermes/skills/` 即可生效。

:::info
Agent 也可以使用 `skill_manage` 自行创建和更新 Skills。在解决一个复杂问题后，Hermes 可能会提议将该方法保存为 Skill，以便下次使用。
:::

---

## 按平台管理 Skill

控制哪些 Skills 在哪些平台上可用：

```bash
hermes skills
```

这将打开一个交互式 TUI，你可以按平台（CLI、Telegram、Discord 等）启用或禁用 Skills。当你希望某些 Skills 仅在特定上下文中使用时非常有用 —— 例如，不在 Telegram 上开启开发相关的 Skills。

---

## Skills vs Memory（记忆）

两者在会话之间都是持久的，但用途不同：

| | Skills | Memory |
|---|---|---|
| **内容** | 过程性知识 —— 如何做事 | 事实性知识 —— 事情是什么 |
| **时机** | 按需加载，仅在相关时加载 | 自动注入到每个会话中 |
| **大小** | 可以很大（数百行） | 应当精简（仅限关键事实） |
| **成本** | 加载前零 Token 消耗 | 虽小但持续的 Token 成本 |
| **示例** | "如何部署到 Kubernetes" | "用户偏好深色模式，居住在 PST 时区" |
| **创建者** | 你、Agent 或从 Hub 安装 | Agent 根据对话内容生成 |

**经验法则：** 如果你会把它放在参考文档里，它就是一个 Skill。如果你会把它写在便利贴上，它就是 Memory。

---

## 提示

**保持 Skill 聚焦。** 一个试图涵盖“所有 DevOps”的 Skill 会太长且太笼统。一个涵盖“将 Python 应用部署到 Fly.io”的 Skill 则足够具体，能产生真正的价值。

**让 Agent 创建 Skills。** 在完成一项复杂的多步骤任务后，Hermes 通常会提议将该方法保存为 Skill。请接受建议 —— 这些由 Agent 编写的 Skill 捕捉了准确的工作流，包括在过程中发现的陷阱。

**使用分类。** 将 Skills 组织到子目录中（如 `~/.hermes/skills/devops/`、`~/.hermes/skills/research/` 等）。这能保持列表整洁，并帮助 Agent 更快找到相关的 Skills。

**在 Skill 过时时进行更新。** 如果你在使用某个 Skill 时遇到了它未涵盖的问题，请告诉 Hermes 根据你学到的新知识更新该 Skill。不维护的 Skills 会变成负担。

---

*如需完整的 Skills 参考 —— 包括 frontmatter 字段、条件激活、外部目录等 —— 请参阅 [Skills 系统](/user-guide/features/skills)。*
