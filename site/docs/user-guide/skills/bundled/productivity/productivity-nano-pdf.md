---
title: "Nano Pdf — 通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/拼写/标题"
sidebar_label: "Nano Pdf"
description: "通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/拼写/标题"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Nano Pdf {#nano-pdf}

通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/拼写/标题。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/nano-pdf` |
| 版本 | `1.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 标签 | `PDF`、`文档`、`编辑`、`NLP`、`生产力` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="nano-pdf"></a>
# nano-pdf

使用自然语言指令编辑 PDF。指定页面并描述要修改的内容。

## 前提条件 {#prerequisites}

```bash
# 使用 uv 安装（推荐——Hermes 中已可用）
uv pip install nano-pdf

# 或使用 pip
pip install nano-pdf
```

## 用法 {#usage}

```bash
nano-pdf edit <file.pdf> <page_number> "<instruction>"
```

## 示例 {#examples}

```bash
# 修改第 1 页的标题
nano-pdf edit deck.pdf 1 "将标题改为 'Q3 结果'，并修正副标题中的拼写错误"

# 更新指定页面的日期
nano-pdf edit report.pdf 3 "将日期从 2026 年 1 月更新为 2026 年 2 月"

# 修正内容
nano-pdf edit contract.pdf 2 "将客户名称从 'Acme Corp' 改为 'Acme Industries'"
```

## 注意事项 {#notes}

- 页码可能基于 0 或 1（取决于版本）——如果编辑到了错误的页面，请尝试 ±1 重试
- 编辑后务必验证输出的 PDF（使用 `read_file` 检查文件大小，或直接打开）
- 该工具底层使用 LLM——需要 API 密钥（查看 `nano-pdf --help` 了解配置）
- 适用于文本修改；复杂的布局调整可能需要其他方法
