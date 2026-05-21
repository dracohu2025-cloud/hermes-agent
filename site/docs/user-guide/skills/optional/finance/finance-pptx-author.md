---
title: "Pptx Author — 使用 python-pptx 无头生成 PowerPoint 演示文稿"
sidebar_label: "Pptx Author"
description: "使用 python-pptx 无头生成 PowerPoint 演示文稿"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="pptx-author"></a>
# Pptx Author

使用 python-pptx 无头生成 PowerPoint 演示文稿。与 excel-author 配合使用，可构建每个数字都来自工作簿单元格的模型驱动型演示文稿。适用于推介 deck、IC 备忘录、财报笔记。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/finance/pptx-author` 安装 |
| 路径 | `optional-skills/finance/pptx-author` |
| 版本 | `1.0.0` |
| 作者 | Anthropic（由 Nous Research 改编） |
| 许可协议 | Apache-2.0 |
| 平台 | linux, macos, windows |
| 标签 | `powerpoint`, `pptx`, `python-pptx`, `presentation`, `finance` |
| 相关技能 | [`excel-author`](/user-guide/skills/optional/finance/finance-excel-author), [`powerpoint`](/user-guide/skills/bundled/productivity/productivity-powerpoint) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在该技能被触发时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# pptx-author

使用 `python-pptx` 在磁盘上生成一个 .pptx 文件。适用于需要将演示文稿作为文件产物交付，而非驱动实时 PowerPoint 会话的场景。

改编自 [anthropics/financial-services](https://github.com/anthropics/financial-services) 中 Anthropic 的 `pptx-author` 和 `pitch-deck` 技能。原技能中的 MCP / Office-JS 分支已被移除——本技能假设无头 Python 环境。

关于更全面的、已发布的 PowerPoint 创作技能（支持幻灯片、演讲者备注、嵌入、多媒体），请参阅内置的 `powerpoint` 技能。本技能是一种更轻量的模式，专为模型驱动型演示文稿（推介 deck、IC 备忘录、财报笔记）优化，其中每个数字都必须追溯到源工作簿。

<a id="output-contract"></a>
## 输出约定

- 写入 `./out/<名称>.pptx`。如果 `./out/` 目录不存在则创建。
- 在最终消息中返回相对路径。

<a id="setup"></a>
## 环境设置

```bash
pip install "python-pptx>=0.6"
```

<a id="core-conventions"></a>
## 核心约定

<a id="one-idea-per-slide"></a>
### 每张幻灯片一个观点
标题陈述关键结论；正文支持该结论。标题为“Q3 营收”的幻灯片较弱；而“Q3 营收同比增长加速至 14%”则更强。

<a id="every-number-traces-to-the-model"></a>
### 每个数字都能追溯到模型
如果幻灯片上的某个数字来自 `./out/model.xlsx`，请标注来源的工作表和单元格。

```
营收：1,250 百万美元（来源：model.xlsx, Inputs!C3）
```

切勿凭记忆或摘要转录数字——打开工作簿，读取命名区域，并在可能的情况下以编程方式将 deck 中的值绑定到该区域。

<a id="use-the-firm-template-when-one-is-mounted"></a>
### 使用挂载的公司模板
如果存在 `./templates/firm-template.pptx`，则加载该模板，使演示文稿继承品牌颜色、字体和母版布局。

```python
from pptx import Presentation
from pathlib import Path

template = Path("./templates/firm-template.pptx")
prs = Presentation(str(template)) if template.exists() else Presentation()
```

<a id="charts-png-from-model-beats-native-pptx-charts"></a>
### 图表：模型导出的 PNG 优于原生 pptx 图表
当保真度很重要时（模型的图表样式必须与演示文稿完全匹配），从源工作簿中将图表渲染为 PNG 并嵌入图片。原生的 `pptx.chart` 图表很脆弱，且通常不符合公司惯例。
```python
from pptx.util import Inches
slide.shapes.add_picture("./out/charts/football_field.png",
                         Inches(1), Inches(2),
                         width=Inches(8))
```

<a id="no-external-sends"></a>
### 无外部发送
该技能（Skill）仅写入文件。它不会发送电子邮件、上传或发布内容。交付由编排层处理。

<a id="skeleton"></a>
## 骨架

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pathlib import Path

template = Path("./templates/firm-template.pptx")
prs = Presentation(str(template)) if template.exists() else Presentation()

# Title slide
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Project Aurora — Strategic Alternatives"
slide.placeholders[1].text = "Preliminary Discussion Materials"

# Valuation summary slide (title-only layout)
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Valuation implies $38–$52 per share across methodologies"

# Add a table bound to model outputs
rows, cols = 5, 4
tbl_shape = slide.shapes.add_table(rows, cols,
                                   Inches(0.5), Inches(1.5),
                                   Inches(9), Inches(3))
tbl = tbl_shape.table
headers = ["Methodology", "Low ($)", "Mid ($)", "High ($)"]
for c, h in enumerate(headers):
    tbl.cell(0, c).text = h

# In a real deck, read these from the model workbook with openpyxl
data = [
    ("Trading comps",     "35", "41", "48"),
    ("Precedent M&A",     "39", "45", "52"),
    ("DCF (base)",        "36", "43", "51"),
    ("LBO (10% IRR)",     "33", "38", "44"),
]
for r, row in enumerate(data, start=1):
    for c, val in enumerate(row):
        tbl.cell(r, c).text = val

# Embed a chart rendered from the model
slide = prs.slides.add_slide(prs.slide_layouts[5])
slide.shapes.title.text = "Football field — current price $42"
slide.shapes.add_picture("./out/charts/football_field.png",
                         Inches(1), Inches(1.8), width=Inches(8))

Path("./out").mkdir(exist_ok=True)
prs.save("./out/pitch-aurora.pptx")
```

<a id="binding-deck-numbers-to-the-source-workbook"></a>
## 将报告编号绑定到源工作簿

从Excel模型中读取命名区域或特定单元格，以确保报告编号永不漂移。

```python
from openpyxl import load_workbook

wb = load_workbook("./out/model.xlsx", data_only=True)
def nr(name):
    """Resolve a named range to its current computed value."""
    rng = wb.defined_names[name]
    sheet, coord = next(rng.destinations)
    return wb[sheet][coord].value

revenue_fy24 = nr("RevenueFY24")
implied_mid  = nr("ImpliedSharePriceBase")
```

然后使用这些值构建报告内容：
```python
slide.shapes.title.text = f"Implied share price of ${implied_mid:.2f} (base case)"
```

请记得在读取之前重新计算工作簿——只有当工作表已被计算时，openpyxl才能看到计算后的值。先运行`excel-author`技能中的重新计算辅助函数，或者通过真实的Excel会话打开/保存。

<a id="slide-type-checklist-for-pitch-decks"></a>
## 投行报告幻灯片类型检查清单

典型的银行投行报告遵循此结构。不是规定性的，但作为起始骨架很有用：
1. 封面 / 标题
2. 免责声明
3. 目录
4. 情况概览
5. 公司概览（目标公司）
6. 市场 / 行业背景
7. 估值总结（足球场图）—— 核心亮点
8. 可比交易详细
9. 先例交易详细
10. DCF 摘要
11. 演示性 LBO / 赞助方案例分析
12. 流程考量
13. 附录

<a id="when-not-to-use-this-skill"></a>
## 何时不应使用此技能

- 用户在实时 PowerPoint 会话中且已有 Office MCP 可用时——请直接驱动其实时文档。
- 非金融类幻灯片（全体季度大会、营销演示）——请使用更通用的 `powerpoint` 技能。
- 包含大量动画、转场或演讲者备注的演示文稿——请使用更通用的 `powerpoint` 技能。

<a id="attribution"></a>
## 归属

本约定改编自 Anthropic 的 Claude for Financial Services 插件套件，基于 Apache-2.0 许可。原始地址：https://github.com/anthropics/financial-services/tree/main/plugins/agent-plugins/pitch-agent/skills/pptx-author
