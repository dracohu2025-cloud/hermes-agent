---
title: "Codebase Inspection — 使用 pygount 检查代码库：代码行数、语言、比例"
sidebar_label: "Codebase Inspection"
description: "使用 pygount 检查代码库：代码行数、语言、比例"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="codebase-inspection"></a>
# Codebase Inspection

使用 pygount 检查代码库：代码行数、语言、比例。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/github/codebase-inspection` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `LOC`, `Code Analysis`, `pygount`, `Codebase`, `Metrics`, `Repository` |
| 相关技能 | [`github-repo-management`](/user-guide/skills/bundled/github/github-github-repo-management) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是完整的技能定义，当该技能被触发时 Hermes 会加载它。这就是 Agent 在技能激活时看到的指令。
:::

<a id="codebase-inspection-with-pygount"></a>
# 使用 pygount 进行代码库检查

使用 `pygount` 分析仓库的代码行数、语言分布、文件数量以及代码与注释的比例。

<a id="when-to-use"></a>
## 何时使用

- 用户询问 LOC（代码行数）统计
- 用户想要查看仓库的语言分布
- 用户询问代码库大小或组成
- 用户想要代码与注释的比例
- 一般的“这个仓库有多大”类问题

<a id="prerequisites"></a>
## 前置条件

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

<a id="1-basic-summary-most-common"></a>
## 1. 基础摘要（最常用）

获取完整的语言分布统计，包括文件数量、代码行数和注释行数：

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**重要：** 务必使用 `--folders-to-skip` 排除依赖/构建目录，否则 pygount 会遍历它们，导致耗时很长甚至卡死。

<a id="2-common-folder-exclusions"></a>
## 2. 常见文件夹排除项

根据项目类型进行调整：

```bash
# Python 项目
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript 项目
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# 通用兜底
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

<a id="3-filter-by-specific-language"></a>
## 3. 按特定语言过滤

```bash
# 仅统计 Python 文件
pygount --suffix=py --format=summary .

# 仅统计 Python 和 YAML 文件
pygount --suffix=py,yaml,yml --format=summary .
```

<a id="4-detailed-file-by-file-output"></a>
## 4. 逐文件详细输出

```bash
# 默认格式显示每个文件的明细
pygount --folders-to-skip=".git,node_modules,venv" .

# 按代码行数排序（通过管道传给 sort）
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

<a id="5-output-formats"></a>
## 5. 输出格式

```bash
# 摘要表（默认推荐）
pygount --format=summary .

# JSON 输出（适合程序化使用）
pygount --format=json .

# 管道友好输出：语言、文件数、代码、文档、空白、字符串
pygount --format=summary . 2>/dev/null
```

<a id="6-interpreting-results"></a>
## 6. 结果解读

摘要表的列含义：
- **Language** — 检测到的编程语言
- **Files** — 该语言的文件数量
- **Code** — 实际代码行数（可执行/声明性代码）
- **Comment** — 注释或文档行数
- **%** — 占总量的百分比
特殊的伪语言：
- `__empty__` — 空文件
- `__binary__` — 二进制文件（图片、编译文件等）
- `__generated__` — 自动生成的文件（通过启发式检测）
- `__duplicate__` — 内容完全相同的文件
- `__unknown__` — 无法识别的文件类型

<a id="pitfalls"></a>
## 注意事项

1. **始终排除 .git、node_modules、venv** — 如果不使用 `--folders-to-skip`，pygount 会遍历所有内容，可能在大型依赖树上花费数分钟甚至卡住。
2. **Markdown 显示 0 行代码** — pygount 会将所有 Markdown 内容归类为注释而非代码。这是预期行为。
3. **JSON 文件代码行数显示偏低** — pygount 对 JSON 行的统计可能较为保守。如需准确的 JSON 行数，请直接使用 `wc -l`。
4. **大型单仓库** — 对于非常大的仓库，建议使用 `--suffix` 只针对特定语言，而不是扫描所有内容。
