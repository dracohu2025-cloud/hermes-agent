---
title: "Ocr And Documents — 从 PDF/扫描件中提取文本 (pymupdf, marker-pdf)"
sidebar_label: "Ocr And Documents"
description: "从 PDF/扫描件中提取文本 (pymupdf, marker-pdf)"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能目录下的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="ocr-and-documents"></a>
# Ocr And Documents

从 PDF/扫描件中提取文本 (pymupdf, marker-pdf)。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/ocr-and-documents` |
| 版本 | `2.3.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `PDF`, `Documents`, `Research`, `Arxiv`, `Text-Extraction`, `OCR` |
| 相关技能 | [`powerpoint`](/user-guide/skills/bundled/productivity/productivity-powerpoint) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令内容。
:::

<a id="pdf-document-extraction"></a>
# PDF 与文档提取

对于 DOCX：使用 `python-docx`（解析实际文档结构，远优于 OCR）。
对于 PPTX：参见 `powerpoint` 技能（使用 `python-pptx`，支持完整幻灯片/笔记）。
本技能涵盖 **PDF 和扫描文档**。

<a id="step-1-remote-url-available"></a>
## 第 1 步：是否有远程 URL？

如果文档有 URL，**始终优先尝试 `web_extract`**：

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

该方法通过 Firecrawl 将 PDF 转为 Markdown，无需本地依赖。

仅在以下情况下使用本地提取：文件是本地文件、web_extract 失败、或需要批量处理。

<a id="step-2-choose-local-extractor"></a>
## 第 2 步：选择本地提取器

| 特性 | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **基于文本的 PDF** | ✅ | ✅ |
| **扫描 PDF（OCR）** | ❌ | ✅（支持 90+ 种语言） |
| **表格** | ✅（基础） | ✅（高精度） |
| **公式 / LaTeX** | ❌ | ✅ |
| **代码块** | ❌ | ✅ |
| **表单** | ❌ | ✅ |
| **去除页眉/页脚** | ❌ | ✅ |
| **阅读顺序检测** | ❌ | ✅ |
| **图片提取** | ✅（嵌入式） | ✅（带上下文） |
| **图片 → 文本（OCR）** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown 输出** | ✅（基于 pymupdf4llm） | ✅（原生，质量更高） |
| **安装体积** | ~25MB | ~3-5GB（PyTorch + 模型） |
| **速度** | 即时 | ~1-14 秒/页（CPU），~0.2 秒/页（GPU） |

**决策**：除非需要 OCR、公式、表单或复杂布局分析，否则使用 pymupdf。

如果用户需要 marker 功能但系统剩余磁盘空间不足 ~5GB：
> “此文档需要 OCR/高级提取（marker-pdf），该操作需要约 5GB 空间用于 PyTorch 和模型。您的系统当前可用空间为 [X]GB。可选方案：释放空间、提供一个 URL 以便使用 web_extract，或我可以尝试使用 pymupdf（适用于基于文本的 PDF，但不支持扫描文档或公式）。”

---

<a id="pymupdf-lightweight"></a>
## pymupdf（轻量级）

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
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # 指定页码范围
```
**内联**：
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

<a id="marker-pdf-high-quality-ocr"></a>
## marker-pdf（高质量 OCR）

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**通过辅助脚本**：
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # 带元数据的 JSON
python scripts/extract_marker.py document.pdf --output_dir out/  # 保存图片
python scripts/extract_marker.py scanned.pdf                 # 扫描版 PDF（OCR）
python scripts/extract_marker.py document.pdf --use_llm      # 使用 LLM 提升精度
```

**CLI**（marker-pdf 安装后可用）：
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # 批量处理
```

---

<a id="arxiv-papers"></a>
## Arxiv 论文

```
# 仅摘要（快速）
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# 全文
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# 搜索
web_search(query="arxiv GRPO reinforcement learning 2026")
```

<a id="split-merge-search"></a>
## 拆分、合并与搜索

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
        print(f"第 {i+1} 页：{len(results)} 个匹配")
        print(page.get_text("text"))
```

无需额外依赖——pymupdf 一个包就能完成拆分、合并、搜索和文本提取。

---

<a id="notes"></a>
## 注意事项

- `web_extract` 始终是处理 URL 的首选
- pymupdf 是安全的默认方案——即时运行、无需模型、随处可用
- marker-pdf 用于 OCR、扫描文档、公式、复杂布局——仅在需要时安装
- 两个辅助脚本都支持 `--help` 查看完整用法
- marker-pdf 首次使用会下载约 2.5GB 模型到 `~/.cache/huggingface/`
- 处理 Word 文档：`pip install python-docx`（比 OCR 更好——解析实际结构）
- 处理 PowerPoint：请参考 `powerpoint` 技能（使用 python-pptx）
