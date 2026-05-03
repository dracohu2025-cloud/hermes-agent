---
title: "Apple Notes — 通过 memo CLI 管理 Apple Notes：创建、搜索、编辑"
sidebar_label: "Apple Notes"
description: "通过 memo CLI 管理 Apple Notes：创建、搜索、编辑"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Apple Notes {#apple-notes}

通过 memo CLI 管理 Apple Notes：创建、搜索、编辑。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/apple/apple-notes` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | macos |
| 标签 | `Notes`、`Apple`、`macOS`、`note-taking` |
| 相关技能 | [`obsidian`](/user-guide/skills/bundled/note-taking/note-taking-obsidian) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="apple-notes"></a>
# Apple Notes

使用 `memo` 直接从终端管理 Apple Notes。笔记通过 iCloud 在所有 Apple 设备间同步。

## 前提条件 {#prerequisites}

- 安装了 Notes.app 的 **macOS**
- 安装：`brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- 在提示时授予 Notes.app 自动化访问权限（系统设置 → 隐私与安全性 → 自动化）

## 何时使用 {#when-to-use}

- 用户要求创建、查看或搜索 Apple Notes
- 将信息保存到 Notes.app 以实现跨设备访问
- 将笔记整理到文件夹中
- 将笔记导出为 Markdown/HTML

## 何时不使用 {#when-not-to-use}

- Obsidian 知识库管理 → 使用 `obsidian` 技能
- Bear Notes → 独立应用（此处不支持）
- 仅 Agent 使用的快速笔记 → 改用 `memory` 工具

## 快速参考 {#quick-reference}

### 查看笔记 {#view-notes}

```bash
memo notes                        # 列出所有笔记
memo notes -f "文件夹名称"        # 按文件夹筛选
memo notes -s "查询"              # 搜索笔记（模糊匹配）
```

### 创建笔记 {#create-notes}

```bash
memo notes -a                     # 交互式编辑器
memo notes -a "笔记标题"          # 快速添加并指定标题
```

### 编辑笔记 {#edit-notes}

```bash
memo notes -e                     # 交互式选择要编辑的笔记
```

### 删除笔记 {#delete-notes}

```bash
memo notes -d                     # 交互式选择要删除的笔记
```

### 移动笔记 {#move-notes}

```bash
memo notes -m                     # 将笔记移动到文件夹（交互式）
```

### 导出笔记 {#export-notes}

```bash
memo notes -ex                    # 导出为 HTML/Markdown
```

## 限制 {#limitations}

- 无法编辑包含图片或附件的笔记
- 交互式提示需要终端访问（如需，请使用 pty=true）
- 仅限 macOS — 需要 Apple Notes.app

## 规则 {#rules}

1. 当用户需要跨设备同步（iPhone/iPad/Mac）时，优先使用 Apple Notes
2. 对于不需要同步的 Agent 内部笔记，使用 `memory` 工具
3. 对于 Markdown 原生的知识管理，使用 `obsidian` 技能
