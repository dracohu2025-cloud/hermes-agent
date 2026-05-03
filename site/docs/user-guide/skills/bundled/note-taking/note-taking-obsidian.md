---
title: "Obsidian — 在 Obsidian 仓库中读取、搜索和创建笔记"
sidebar_label: "Obsidian"
description: "在 Obsidian 仓库中读取、搜索和创建笔记"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Obsidian {#obsidian}

在 Obsidian 仓库中读取、搜索和创建笔记。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/note-taking/obsidian` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# Obsidian 仓库 {#obsidian-vault}

**位置：** 通过 `OBSIDIAN_VAULT_PATH` 环境变量设置（例如在 `~/.hermes/.env` 中）。

如果未设置，默认路径为 `~/Documents/Obsidian Vault`。

注意：仓库路径可能包含空格——请始终用引号括起来。

## 读取笔记 {#read-a-note}

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat "$VAULT/Note Name.md"
```

## 列出笔记 {#list-notes}

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# 所有笔记
find "$VAULT" -name "*.md" -type f

# 在特定文件夹中
ls "$VAULT/Subfolder/"
```

## 搜索 {#search}

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# 按文件名搜索
find "$VAULT" -name "*.md" -iname "*keyword*"

# 按内容搜索
grep -rli "keyword" "$VAULT" --include="*.md"
```

## 创建笔记 {#create-a-note}

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat > "$VAULT/New Note.md" << 'ENDNOTE'
# 标题

此处填写内容。
ENDNOTE
```

## 追加内容到笔记 {#append-to-a-note}

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
echo "
此处填写新内容。" >> "$VAULT/Existing Note.md"
```

## Wikilinks {#wikilinks}

Obsidian 使用 `[[笔记名称]]` 语法链接笔记。创建笔记时，请使用此语法关联相关内容。
