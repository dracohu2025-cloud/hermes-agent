---
sidebar_position: 12
title: "使用 Skills"
description: "查找、安装、使用和创建 skills —— 按需加载的知识文档，教会 Hermes 新的工作流"
---

# 使用 Skills {#working-with-skills}

Skills 是按需加载的知识文档，用来教 Hermes 如何处理特定任务——从生成 ASCII 艺术到管理 GitHub PR。这篇指南带你了解日常使用方法。

完整技术参考请见 [Skills System](/user-guide/features/skills)。

---

## 查找 Skills {#finding-skills}

每次安装 Hermes 都会自带一批内置 skills。看看有哪些可用：

```bash
# 在任意聊天会话中：
/skills

# 或者通过 CLI：
hermes skills list
```

这会显示一个精简列表，包含名称和描述：

```
ascii-art         使用 pyfiglet、cowsay、boxes 生成 ASCII 艺术...
arxiv             从 arXiv 搜索并获取学术论文...
github-pr-workflow 完整的 PR 生命周期 —— 创建分支、提交...
plan              Plan 模式 —— 检查上下文、撰写 markdown...
excalidraw        使用 Excalidraw 创建手绘风格图表...
```

### 搜索 Skill {#searching-for-a-skill}

```bash
# 按关键词搜索
/skills search docker
/skills search music
```

### Skills Hub {#the-skills-hub}

官方可选 skills（较重或较冷门的 skills，默认不启用）可以通过 Hub 获取：

```bash
# 浏览官方可选 skills
/skills browse

# 在 hub 中搜索
/skills search blockchain
```

---

## 使用 Skill {#using-a-skill}

每个已安装的 skill 自动就是一个斜杠命令。直接输入它的名字就行：

```bash
# 加载 skill 并给它分配任务
/ascii-art 做一个写着 "HELLO WORLD" 的横幅
/plan 为一个待办应用设计 REST API
/github-pr-workflow 为 auth 重构创建一个 PR

# 只输入 skill 名（不带任务）会加载它，然后你可以描述需要什么
/excalidraw
```

你也可以通过自然对话触发 skills —— 让 Hermes 使用某个特定 skill，它会通过 `skill_view` 工具来加载。

### 渐进式加载 {#progressive-disclosure}

Skills 采用一种节省 token 的加载模式。Agent 不会一次性把所有内容都加载进来：

1. **`skills_list()`** —— 所有 skills 的精简列表（约 3k tokens）。会话开始时加载。
2. **`skill_view(name)`** —— 某个 skill 的完整 SKILL.md 内容。Agent 判断需要该 skill 时加载。
3. **`skill_view(name, file_path)`** —— skill 内的某个具体参考文件。仅在需要时加载。

这意味着 skills 在实际使用之前不会消耗 token。

---

## 从 Hub 安装 {#installing-from-the-hub}

官方可选 skills 随 Hermes 一起发布，但默认不启用。需要显式安装：

```bash
# 安装官方可选 skill
hermes skills install official/research/arxiv

# 在聊天会话中从 hub 安装
/skills install official/creative/songwriting-and-ai-music
```

安装过程：
1. Skill 目录被复制到 `~/.hermes/skills/`
2. 它会出现在你的 `skills_list` 输出中
3. 它变为可用的斜杠命令

:::tip
已安装的 skills 在新会话中生效。如果你想在当前会话中就用上，可以用 `/reset` 重新开始，或者加上 `--now` 立即让 prompt 缓存失效（下一轮会消耗更多 tokens）。
:::

### 验证安装 {#verifying-installation}

```bash
# 确认已安装
hermes skills list | grep arxiv

# 或者在聊天中
/skills search arxiv
```

---

## 插件提供的 Skills {#plugin-provided-skills}

插件可以用带命名空间的名称（`plugin:skill`）打包自己的 skills。这样可以避免与内置 skills 重名。

```bash
# 用完整名称加载插件 skill
skill_view("superpowers:writing-plans")

# 同名基础名称的内置 skill 不受影响
skill_view("writing-plans")
```

插件 skills **不会**出现在系统 prompt 中，也不会显示在 `skills_list` 里。它们是按需选用的——当你知道某个插件提供了 skill 时，显式加载即可。加载后，Agent 会看到一个横幅，列出同一插件的其他相关 skills。

关于如何在你自己的插件中打包 skills，请见 [Build a Hermes Plugin → Bundle skills](/guides/build-a-hermes-plugin#bundle-skills)。

---

## 配置 Skill 设置 {#configuring-skill-settings}

有些 skills 会在 frontmatter 中声明自己需要的配置：

```yaml
metadata:
  hermes:
    config:
      - key: tenor.api_key
        description: "Tenor API key for GIF search"
        prompt: "Enter your Tenor API key"
        url: "https://developers.google.com/tenor/guides/quickstart"
```
当带有配置的 Skill 首次加载时，Hermes 会提示你输入值。这些值存储在 `skills.config.*` 下的 `config.yaml` 中。

通过 CLI 管理 Skill 配置：

```bash
# 为特定 Skill 进行交互式配置
hermes skills config gif-search

# 查看所有 Skill 配置
hermes config get skills.config
```

---

## 创建你自己的 Skill {#creating-your-own-skill}

Skill 就是带有 YAML frontmatter 的 Markdown 文件。创建一个只需要不到五分钟。

### 1. 创建目录 {#1-create-the-directory}

```bash
mkdir -p ~/.hermes/skills/my-category/my-skill
```

### 2. 编写 SKILL.md {#2-write-skill-md}

```markdown title="~/.hermes/skills/my-category/my-skill/SKILL.md"
---
name: my-skill
description: 这个 Skill 的简要说明
version: 1.0.0
metadata:
  hermes:
    tags: [my-tag, automation]
    category: my-category
---

# My Skill

## 何时使用
当用户询问 [特定主题] 或需要 [特定任务] 时使用此 Skill。

## 操作步骤
1. 首先，检查 [前置条件] 是否可用
2. 运行 `command --with-flags`
3. 解析输出并展示结果

## 常见陷阱
- 常见失败：[描述]。修复方法：[解决方案]
- 注意 [边界情况]

## 验证
运行 `check-command` 确认结果是否正确。
```

### 3. 添加参考文件（可选） {#3-add-reference-files-optional}

Skill 可以包含 Agent 按需加载的辅助文件：

```
my-skill/
├── SKILL.md                    # 主 Skill 文档
├── references/
│   ├── api-docs.md             # Agent 可查阅的 API 参考
│   └── examples.md             # 示例输入/输出
├── templates/
│   └── config.yaml             # Agent 可使用的模板文件
└── scripts/
    └── setup.sh                # Agent 可执行的脚本
```

在 SKILL.md 中引用这些文件：

```markdown
如需 API 详情，加载参考文件：`skill_view("my-skill", "references/api-docs.md")`
```

### 4. 测试 {#4-test-it}

启动新会话并尝试你的 Skill：

```bash
hermes chat -q "/my-skill help me with the thing"
```

Skill 会自动出现——无需注册。把它放到 `~/.hermes/skills/` 里就生效了。

:::info
Agent 也可以使用 `skill_manage` 自己创建和更新 Skill。解决了一个复杂问题后，Hermes 可能会提议把解决方法保存为 Skill，以便下次使用。
:::

---

## 按平台管理 Skill {#per-platform-skill-management}

控制哪些 Skill 在哪些平台上可用：

```bash
hermes skills
```

这会打开一个交互式 TUI，你可以在其中按平台（CLI、Telegram、Discord 等）启用或禁用 Skill。当你希望某些 Skill 只在特定场景下可用时很有用——例如，不让开发相关的 Skill 出现在 Telegram 上。

---

## Skill 与 Memory 的对比 {#skills-vs-memory}

两者在会话间都是持久化的，但用途不同：

| | Skill | Memory |
|---|---|---|
| **是什么** | 程序性知识——怎么做 | 事实性知识——是什么 |
| **何时加载** | 按需加载，仅在相关时 | 自动注入每个会话 |
| **大小** | 可以很大（数百行） | 应该精简（仅关键事实） |
| **成本** | 加载前零 token | 持续产生少量 token 成本 |
| **示例** | "如何部署到 Kubernetes" | "用户喜欢深色模式，住在太平洋时区" |
| **由谁创建** | 你、Agent 或从 Hub 安装 | Agent，基于对话生成 |

**经验法则：** 如果你会把它放进参考文档，那就是 Skill。如果你会把它贴在便利贴上，那就是 Memory。

---

## 技巧 {#tips}

**保持 Skill 聚焦。** 试图涵盖"所有 DevOps"的 Skill 会太长、太模糊。而涵盖"将 Python 应用部署到 Fly.io"的 Skill 就足够具体，能真正派上用场。

**让 Agent 创建 Skill。** 完成一个复杂的多步骤任务后，Hermes 经常会提议把解决方法保存为 Skill。答应它——这些由 Agent 编写的 Skill 会捕捉到确切的工作流程，包括过程中发现的陷阱。

**使用分类。** 把 Skill 组织到子目录中（`~/.hermes/skills/devops/`、`~/.hermes/skills/research/` 等）。这能让列表保持可控，也能帮助 Agent 更快地找到相关 Skill。
**在技能过时后及时更新。** 如果你使用了某个技能，但遇到了技能没有覆盖到的问题，就告诉 Hermes 把学到的东西更新到技能里。不维护的技能会变成累赘。

---

*如需查看完整的技能参考——frontmatter 字段、条件激活、外部目录等——请参阅 [Skills System](/user-guide/features/skills)。*
