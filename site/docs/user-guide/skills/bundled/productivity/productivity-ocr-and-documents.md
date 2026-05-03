---
title: "OCR 与文档 — 从 PDF/扫描件中提取文本 (pymupdf, marker-pdf)"
sidebar_label: "OCR 与文档"
description: "从 PDF/扫描件中提取文本 (pymupdf, marker-pdf)"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# OCR 与文档 {#ocr-and-documents}

从 PDF/扫描件中提取文本 (pymupdf, marker-pdf)。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/ocr-and-documents` |
| 版本 | `2.3.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `PDF`, `Documents`, `Research`, `Arxiv`, `Text-Extraction`, `OCR` |
| 相关技能 | [`powerpoint`](/user-guide/skills/bundled/productivity/productivity-powerpoint) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# PDF 与文档提取 {#pdf-document-extraction}

对于 DOCX：使用 `python-docx`（解析实际文档结构，远优于 OCR）。
对于 PPTX：请参见 `powerpoint` 技能（使用 `python-pptx`，支持完整幻灯片/备注）。
本技能涵盖 **PDF 和扫描文档**。

## 步骤 1：是否有远程 URL？ {#step-1-remote-url-available}

如果文档有 URL，**始终优先尝试 `web_extract`**：

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

此方法通过 Firecrawl 将 PDF 转换为 Markdown，无需本地依赖。

仅在以下情况下使用本地提取：文件是本地文件、`web_extract` 失败，或需要批量处理。

## 步骤 2：选择本地提取器 {#step-2-choose-local-extractor}

| 特性 | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **基于文本的 PDF** | ✅ | ✅ |
| **扫描 PDF（OCR）** | ❌ | ✅（90+ 种语言） |
| **表格** | ✅（基础） | ✅（高精度） |
| **公式 / LaTeX** | ❌ | ✅ |
| **代码块** | ❌ | ✅ |
| **表单** | ❌ | ✅ |
| **页眉/页脚移除** | ❌ | ✅ |
| **阅读顺序检测** | ❌ | ✅ |
| **图片提取** | ✅（嵌入） | ✅（带上下文） |
| **图片 → 文本（OCR）** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown 输出** | ✅（通过 pymupdf4llm） | ✅（原生，质量更高） |
| **安装体积** | ~25MB | ~3-5GB（PyTorch + 模型） |
| **速度** | 即时 | ~1-14 秒/页（CPU），~0.2 秒/页（GPU） |

**决策**：除非需要 OCR、公式、表单或复杂布局分析，否则使用 pymupdf。

如果用户需要 marker 功能但系统缺少约 5GB 可用磁盘空间：
> “此文档需要 OCR/高级提取（marker-pdf），这需要约 5GB 空间用于 PyTorch 和模型。您的系统有 [X]GB 可用空间。选项：释放空间、提供 URL 以便使用 web_extract，或者我可以尝试 pymupdf（适用于基于文本的 PDF，但不适用于扫描文档或公式）。”

---

## pymupdf（轻量级） {#pymupdf-lightweight}

```bash
pip install pymupdf pymupdf4llm
```

**通过辅助脚本**：
```bash
python scripts/extract_pymupdf.py document.pdf              # 纯文本
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # 表格
python scripts/extract_pymupdf.py document.pdf --images out/ # 提取图片
python scripts/extract_pymupdf.py document.pdf --metadata    # 标题、作者、页数
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # 指定页面
```
**内联方式**：
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf（高质量 OCR） {#marker-pdf-high-quality-ocr}

```bash
# 先检查磁盘空间
python scripts/extract_marker.py --check

pip install marker-pdf
```

**通过辅助脚本**：
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # 带元数据的 JSON
python scripts/extract_marker.py document.pdf --output_dir out/  # 保存图片
python scripts/extract_marker.py scanned.pdf                 # 扫描版 PDF（OCR）
python scripts/extract_marker.py document.pdf --use_llm      # 用 LLM 提升准确率
```

**CLI**（随 marker-pdf 安装）：
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # 批量处理
```

---

## Arxiv 论文 {#arxiv-papers}

```
# 仅摘要（快速）
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# 全文
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# 搜索
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## 拆分、合并与搜索 {#split-merge-search}

pymupdf 原生支持这些操作——使用 `execute_code` 或内联 Python：

```python
# 拆分：提取第 1-5 页到新 PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# 合并多个 PDF
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# 在所有页面中搜索文本
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"第 {i+1} 页：{len(results)} 处匹配")
        print(page.get_text("text"))
```

无需额外依赖——pymupdf 一个包就能搞定拆分、合并、搜索和文本提取。

---

## 注意事项 {#notes}

- `web_extract` 始终是处理 URL 的首选
- pymupdf 是安全默认项——即时运行、无需模型、随处可用
- marker-pdf 用于 OCR、扫描文档、公式、复杂布局——仅在需要时安装
- 两个辅助脚本都支持 `--help` 查看完整用法
- marker-pdf 首次使用时会下载约 2.5GB 模型到 `~/.cache/huggingface/`
- 处理 Word 文档：`pip install python-docx`（比 OCR 更好——能解析实际结构）
- 处理 PowerPoint：参见 `powerpoint` 技能（使用 python-pptx）
