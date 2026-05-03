---
title: "代码库检查 — 使用 pygount 检查代码库：代码行数、语言、比例"
sidebar_label: "代码库检查"
description: "使用 pygount 检查代码库：代码行数、语言、比例"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 代码库检查 {#codebase-inspection}

使用 pygount 检查代码库：代码行数、语言、比例。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/codebase-inspection` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `LOC`, `Code Analysis`, `pygount`, `Codebase`, `Metrics`, `Repository` |
| 相关技能 | [`github-repo-management`](/user-guide/skills/bundled/github/github-github-repo-management) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 使用 pygount 进行代码库检查 {#codebase-inspection-with-pygount}

使用 `pygount` 分析仓库的代码行数、语言分布、文件数量以及代码与注释的比例。

## 何时使用 {#when-to-use}

- 用户询问代码行数（LOC）
- 用户想要仓库的语言分布
- 用户询问代码库大小或组成
- 用户想要代码与注释的比例
- 一般性的“这个仓库有多大”问题

## 前置条件 {#prerequisites}

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. 基本摘要（最常用） {#1-basic-summary-most-common}

获取完整的语言分布，包括文件数量、代码行数和注释行数：

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**重要：** 始终使用 `--folders-to-skip` 排除依赖/构建目录，否则 pygount 会遍历它们，导致耗时很长或卡住。

## 2. 常见文件夹排除项 {#2-common-folder-exclusions}

根据项目类型调整：

```bash
# Python 项目
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript 项目
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# 通用全量排除
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. 按特定语言过滤 {#3-filter-by-specific-language}

```bash
# 仅统计 Python 文件
pygount --suffix=py --format=summary .

# 仅统计 Python 和 YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. 逐文件详细输出 {#4-detailed-file-by-file-output}

```bash
# 默认格式显示每个文件的统计
pygount --folders-to-skip=".git,node_modules,venv" .

# 按代码行数排序（通过管道传递给 sort）
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. 输出格式 {#5-output-formats}

```bash
# 摘要表格（默认推荐）
pygount --format=summary .

# JSON 输出，便于程序化使用
pygount --format=json .

# 管道友好：语言、文件数、代码、文档、空行、字符串
pygount --format=summary . 2>/dev/null
```

## 6. 解读结果 {#6-interpreting-results}

摘要表格的列含义：
- **Language** — 检测到的编程语言
- **Files** — 该语言的文件数量
- **Code** — 实际代码行数（可执行/声明式）
- **Comment** — 注释或文档行数
- **%** — 占总数的百分比
特殊伪语言：
- `__empty__` — 空文件
- `__binary__` — 二进制文件（图片、编译产物等）
- `__generated__` — 自动生成的文件（通过启发式检测）
- `__duplicate__` — 内容完全相同的文件
- `__unknown__` — 无法识别的文件类型

## 常见陷阱 {#pitfalls}

1. **务必排除 .git、node_modules、venv** — 如果不使用 `--folders-to-skip`，pygount 会爬取所有内容，在大规模依赖树上可能会耗时数分钟甚至卡死。
2. **Markdown 显示为 0 行代码** — pygount 默认将所有 Markdown 内容归类为注释而非代码，这是预期行为。
3. **JSON 文件代码行数偏低** — pygount 对 JSON 行的计数较为保守。如需精确的 JSON 行数，请直接使用 `wc -l`。
4. **大型单体仓库** — 对于非常大的仓库，建议使用 `--suffix` 来限定目标语言，而不是扫描所有内容。
