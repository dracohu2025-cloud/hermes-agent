---
title: "Nano Pdf — 通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/拼写错误/标题"
sidebar_label: "Nano Pdf"
description: "通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/拼写错误/标题"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="nano-pdf"></a>
# Nano Pdf

通过 nano-pdf CLI（自然语言提示）编辑 PDF 文本/拼写错误/标题。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/nano-pdf` |
| 版本 | `1.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `PDF`, `文档`, `编辑`, `NLP`, `生产力` |

<a id="reference-full-skill-md"></a>
## 参考：完整版 SKILL.md

:::info
以下是技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# nano-pdf

使用自然语言指令编辑 PDF。指向某一页并描述要修改的内容。

<a id="prerequisites"></a>
## 前提条件

```bash
# 使用 uv 安装（推荐——Hermes 中已可用）
uv pip install nano-pdf

# 或者使用 pip
pip install nano-pdf
```

<a id="usage"></a>
## 用法

```bash
nano-pdf edit <文件.pdf> <页码> "<指令>"
```

<a id="examples"></a>
## 示例

```bash
# 修改第 1 页的标题
nano-pdf edit deck.pdf 1 "将标题改为'Q3 业绩'，并修复副标题中的拼写错误"

# 更新某页的日期
nano-pdf edit report.pdf 3 "将日期从 2026 年 1 月更新为 2026 年 2 月"

# 修正内容
nano-pdf edit contract.pdf 2 "将客户名称从'Acme Corp'改为'Acme Industries'"
```

<a id="notes"></a>
## 注意事项

- 页码根据版本可能从 0 或 1 开始计数——如果编辑错了页，请用 ±1 重试
- 编辑后务必验证输出 PDF（使用 `read_file` 检查文件大小，或直接打开）
- 该工具底层使用 LLM——需要 API 密钥（查看 `nano-pdf --help` 了解配置）
- 适用于文本更改；复杂的布局修改可能需要其他方法
