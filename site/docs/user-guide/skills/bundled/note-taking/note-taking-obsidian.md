---
title: "Obsidian — 在 Obsidian 仓库中读取、搜索、创建和编辑笔记"
sidebar_label: "Obsidian"
description: "在 Obsidian 仓库中读取、搜索、创建和编辑笔记"
---

{/* 此页面由技能目录下的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="obsidian"></a>
# Obsidian

在 Obsidian 仓库中读取、搜索、创建和编辑笔记。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/note-taking/obsidian` |
| 平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

<a id="obsidian-vault"></a>
# Obsidian 仓库

使用此技能进行基于文件系统的 Obsidian 仓库操作：读取笔记、列出笔记、搜索笔记文件、创建笔记、追加内容以及添加维基链接。

<a id="vault-path"></a>
## 仓库路径

在调用文件工具之前，请使用已知或已解析的仓库路径。

文档约定的仓库路径是 `OBSIDIAN_VAULT_PATH` 环境变量，例如来自 `~/.hermes/.env`。如果未设置，则使用 `~/Documents/Obsidian Vault`。

文件工具不会展开 shell 变量。不要将包含 `$OBSIDIAN_VAULT_PATH` 的路径传递给 `read_file`、`write_file`、`patch` 或 `search_files`；请先解析仓库路径，然后传递具体的绝对路径。仓库路径可能包含空格，这也是优先使用文件工具而非 shell 命令的另一个原因。

如果仓库路径未知，可以使用 `terminal` 来解析 `OBSIDIAN_VAULT_PATH` 或检查回退路径是否存在。一旦路径已知，请切换回文件工具。

<a id="read-a-note"></a>
## 读取笔记

使用 `read_file` 并传入已解析的笔记绝对路径。优先使用此方法而非 `cat`，因为它能提供行号和分页功能。

<a id="list-notes"></a>
## 列出笔记

使用 `search_files`，设置 `target: "files"` 和已解析的仓库路径。优先使用此方法而非 `find` 或 `ls`。

- 要列出所有 Markdown 笔记，请在仓库路径下使用 `pattern: "*.md"`。
- 要列出子文件夹，请在该子文件夹的绝对路径下进行搜索。

<a id="search"></a>
## 搜索

使用 `search_files` 进行文件名和内容搜索。优先使用此方法而非 `grep`、`find` 或 `ls`。

- 对于文件名，使用 `search_files` 并设置 `target: "files"` 和文件名 `pattern`。
- 对于笔记内容，使用 `search_files` 并设置 `target: "content"`，内容正则表达式作为 `pattern`，当你想将匹配限制在 Markdown 笔记中时，可以设置 `file_glob: "*.md"`。

<a id="create-a-note"></a>
## 创建笔记

使用 `write_file` 并传入已解析的绝对路径和完整的 Markdown 内容。优先使用此方法而非 shell 的 heredoc 或 `echo`，因为它能避免 shell 引号问题并返回结构化结果。

<a id="append-to-a-note"></a>
## 追加到笔记

当操作不复杂时，优先使用原生的文件工具工作流：

- 使用 `read_file` 读取目标笔记。
- 当有稳定的上下文时，使用 `patch` 进行锚定追加，例如在现有标题后添加章节，或在已知的尾部块之前追加。
- 当重写整个笔记比构建脆弱的补丁更清晰时，使用 `write_file`。

对于使用 `patch` 的锚定追加，请将锚点替换为锚点加上新内容。
对于没有稳定上下文的简单追加操作，如果 `terminal` 是最清晰的安全选项，那么它是可接受的。

<a id="targeted-edits"></a>
## 针对性编辑

当当前内容提供了稳定上下文时，使用 `patch` 进行重点笔记修改。优先选择此方式，而不是通过 shell 文本重写。

<a id="wikilinks"></a>
## Wikilinks

Obsidian 使用 `[[笔记名称]]` 语法链接笔记。在创建笔记时，使用这些链接来关联相关内容。
