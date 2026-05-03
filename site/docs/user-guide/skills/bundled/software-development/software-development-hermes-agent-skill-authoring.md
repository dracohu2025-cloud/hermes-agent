---
title: "Hermes Agent 技能编写 — 编写仓库内 SKILL"
sidebar_label: "Hermes Agent 技能编写"
description: "编写仓库内 SKILL"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Hermes Agent 技能编写 {#hermes-agent-skill-authoring}

编写仓库内 SKILL.md：frontmatter、验证器、结构。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/hermes-agent-skill-authoring` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `skills`, `authoring`, `hermes-agent`, `conventions`, `skill-md` |
| 相关技能 | [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans), [`requesting-code-review`](/user-guide/skills/bundled/software-development/software-development-requesting-code-review) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# 编写 Hermes-Agent 技能（仓库内） {#authoring-hermes-agent-skills-in-repo}

## 概述 {#overview}

SKILL.md 可以存在于两个位置：

1. **用户本地：** `~/.hermes/skills/&lt;maybe-category&gt;/&lt;name&gt;/SKILL.md` — 个人使用，不共享。通过 `skill_manage(action='create')` 创建。
2. **仓库内（本技能针对此情况）：** `/home/bb/hermes-agent/skills/&lt;category&gt;/&lt;name&gt;/SKILL.md` — 提交到仓库，随包发布。使用 `write_file` + `git add`。`skill_manage(action='create')` 不会操作此目录树。

## 何时使用 {#when-to-use}

- 用户要求你“在此分支/仓库/提交中”添加一个技能
- 你正在提交一个可复用的工作流，该工作流应随 hermes-agent 一起发布
- 你正在编辑 `/home/bb/hermes-agent/skills/` 下的现有技能（小改动用 `patch`，重写用 `write_file`；`skill_manage` 仍可用于仓库内技能的补丁，但不能用于 `create`）

## 必需的 Frontmatter {#required-frontmatter}

验证依据：`tools/skill_manager_tool.py::_validate_frontmatter`。硬性要求：

- 以 `---` 作为文件开头（前面不能有空行）。
- 以 `\n---\n` 结束，之后才是正文。
- 解析为 YAML 映射。
- 必须包含 `name` 字段。
- 必须包含 `description` 字段，且长度 ≤ **1024 字符**（`MAX_DESCRIPTION_LENGTH`）。
- 结束 `---` 之后必须有非空正文。

`skills/software-development/` 下所有技能遵循的通用格式：

```yaml
---
name: my-skill-name               # 小写，连字符，≤64 字符（MAX_NAME_LENGTH）
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

验证器不强制要求 `version` / `author` / `license` / `metadata`，但所有同类技能都包含它们——省略会让你的技能显得突兀。

## 大小限制 {#size-limits}

- 描述：≤ 1024 字符（强制）。
- 完整 SKILL.md：≤ 100,000 字符（强制，`MAX_SKILL_CONTENT_CHARS`，约 36k tokens）。
- `software-development/` 下的同类技能通常在 **8-14k 字符**。尽量保持在这个范围。如果超过 20k，请拆分为 `references/*.md` 并在 SKILL.md 中引用它们。
## 对等结构 {#peer-matched-structure}

仓库内的每个技能大致遵循以下结构：

```
# <标题>

## 概述
一两段：是什么以及为什么。

## 何时使用
- 触发条件列表
- “不要用于：”反触发条件

## <技能特有的主题章节>
- 常见快速参考表
- 包含精确命令的代码块
- Hermes 专属配方（通过 scripts/run_tests.sh 运行测试、ui-tui 路径等）

## 常见陷阱
错误及其修复的编号列表。

## 验证清单
- [ ] 操作后验证的复选框列表

## 一次性配方（可选）
命名场景 → 具体的命令序列。
```

并非每个章节都是强制性的，但 `概述` + `何时使用` + 可操作的主体 + 陷阱是让技能感觉像是对等体的最低要求。

## 目录放置 {#directory-placement}

```
skills/<类别>/<技能名称>/SKILL.md
```

当前仓库中的类别（通过 `ls skills/` 确认）：`autonomous-ai-agents`、`creative`、`data-science`、`devops`、`dogfood`、`email`、`gaming`、`github`、`leisure`、`mcp`、`media`、`mlops/*`、`note-taking`、`productivity`、`red-teaming`、`research`、`smart-home`、`social-media`、`software-development`。

选择最接近的现有类别。不要随意创建新的顶级类别。

## 工作流程 {#workflow}

1. **调查目标类别中的对等技能**：
   ```
   ls skills/<类别>/
   ```
   阅读 2-3 个对等 SKILL.md 文件以匹配语气和结构。
2. **如果不确定，检查验证器约束**：在 `tools/skill_manager_tool.py` 中。
3. **起草**：使用 `write_file` 写入 `skills/<类别>/<名称>/SKILL.md`。
4. **本地验证**：
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<类别>/<名称>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **Git add + commit** 到当前分支。
6. **注意：** 当前会话的技能加载器是缓存的——`skill_view` / `skills_list` 在新会话之前不会看到新技能。这是预期行为，不是 bug。

## 交叉引用其他技能 {#cross-referencing-other-skills}

`metadata.hermes.related_skills` 在加载时会合并两个树（仓库内的 `skills/` 和 `~/.hermes/skills/`）。你可以从仓库内技能引用用户本地技能，但对于其他克隆仓库的新用户来说，该引用将无法解析。优先从仓库内技能仅引用仓库内技能。如果一个经常被引用的技能只存在于 `~/.hermes/skills/` 中，考虑将其提升到仓库中。

## 编辑现有仓库内技能 {#editing-existing-in-repo-skills}

- **小修复（拼写错误、添加陷阱、收紧触发条件）：** `skill_manage(action='patch', name=..., old_string=..., new_string=...)` 对仓库内技能有效。
- **重大重写：** 使用 `write_file` 写入整个 SKILL.md。`skill_manage(action='edit')` 也有效，但需要提供完整的新内容。
- **添加支持文件：** 使用 `write_file` 写入 `skills/<类别>/<名称>/references/&lt;file&gt;.md`、`templates/&lt;file&gt;` 或 `scripts/&lt;file&gt;`。`skill_manage(action='write_file')` 也有效，并强制使用 references/templates/scripts/assets 子目录白名单。
- **始终提交** 编辑——仓库内技能是源代码，而不是运行时状态。
## 常见陷阱 {#common-pitfalls}

1. **对仓库内的技能使用 `skill_manage(action='create')`。** 该命令会写入 `~/.hermes/skills/`，而不是仓库目录。仓库内创建应使用 `write_file`。

2. **`---` 前有前导空白。** 验证器会检查 `content.startswith("---")`；任何前导空行或 BOM 都会导致验证失败。

3. **描述过于笼统。** 同伴技能的描述以“Use when ...”开头，描述的是*触发类*，而不是单个任务。“Use when debugging X”优于“Debug X”。

4. **忘记作者/许可证/元数据块。** 验证器不强制要求，但每个同伴技能都有；缺少会让技能看起来半成品。

5. **编写与已有同伴技能重复的技能。** 创建前，先 `ls skills/&lt;category&gt;/` 并打开 2-3 个同伴技能。优先扩展现有技能，而不是创建狭窄的同类技能。

6. **期望当前会话能看到新技能。** 不会。技能加载器在会话启动时初始化。请在新会话中验证，或通过 `skill_view` 使用精确路径验证。

7. **链接到仓库中不存在的技能。** `related_skills: [some-user-local-skill]` 对你有效，但会破坏其他克隆。建议只链接仓库内的技能。

## 验证清单 {#verification-checklist}

- [ ] 文件位于 `skills/&lt;category&gt;/&lt;name&gt;/SKILL.md`（不在 `~/.hermes/skills/`）
- [ ] Frontmatter 从字节 0 开始以 `---` 开头，以 `\n---\n` 结束
- [ ] `name`、`description`、`version`、`author`、`license`、`metadata.hermes.{tags, related_skills}` 均存在
- [ ] 名称 ≤ 64 个字符，小写 + 连字符
- [ ] 描述 ≤ 1024 个字符，并以“Use when ...”开头
- [ ] 文件总字符 ≤ 100,000（建议 8-15k）
- [ ] 结构：`# Title` → `## Overview` → `## When to Use` → 正文 → `## Common Pitfalls` → `## Verification Checklist`
- [ ] `related_skills` 引用在仓库内可解析（或明确允许为用户本地）
- [ ] 已在目标分支上完成 `git add skills/&lt;category&gt;/&lt;name&gt;/ && git commit`
