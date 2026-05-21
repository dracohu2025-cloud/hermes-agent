---
title: "Excel Author"
sidebar_label: "Excel 作者"
description: "使用 openpyxl 从头构建可审计的 Excel 工作簿——蓝色/黑色/绿色单元格约定、公式优先于硬编码、命名范围、平衡检查、敏感性表格..."
---

{/* 此页面由技能目录下的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="excel-author"></a>
# Excel Author

使用 openpyxl 从头构建可审计的 Excel 工作簿——蓝色/黑色/绿色单元格约定、公式优先于硬编码、命名范围、平衡检查、敏感性表格。适用于财务模型、审计输出、对账。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选——使用 `hermes skills install official/finance/excel-author` 安装 |
| 路径 | `optional-skills/finance/excel-author` |
| 版本 | `1.0.0` |
| 作者 | Anthropic（由 Nous Research 改编） |
| 许可证 | Apache-2.0 |
| 平台 | linux, macos, windows |
| 标签 | `excel`, `openpyxl`, `finance`, `spreadsheet`, `modeling` |
| 相关技能 | [`pptx-author`](/user-guide/skills/optional/finance/finance-pptx-author), [`dcf-model`](/user-guide/skills/optional/finance/finance-dcf-model), [`comps-analysis`](/user-guide/skills/optional/finance/finance-comps-analysis), [`lbo-model`](/user-guide/skills/optional/finance/finance-lbo-model), [`3-statement-model`](/user-guide/skills/optional/finance/finance-3-statement-model) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是当该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# excel-author

使用 `openpyxl` 在磁盘上生成一个 `.xlsx` 文件。遵循以下银行级约定，使模型具备可审计性、灵活性，并且能够被非构建者审阅。

改编自 [anthropics/financial-services](https://github.com/anthropics/financial-services) 仓库中 Anthropic 的 `xlsx-author` 和 `audit-xls` 技能。原始版本中与 MCP / Office-JS / Cowork 相关的分支已被移除——本技能假定为无头 Python 环境。

<a id="output-contract"></a>
## 输出约定

- 写入到 `./out/&lt;name&gt;.xlsx`。如果 `./out/` 目录不存在，则创建它。
- 在最终消息中返回相对路径，以便下游工具能够获取。
- 每个文件只包含一个逻辑模型。除非明确要求，否则不要追加到现有工作簿。

<a id="setup"></a>
## 设置

```bash
pip install "openpyxl>=3.0"
```

<a id="core-conventions-non-negotiable"></a>
## 核心约定（不可协商）

<a id="blue-black-green-cell-color"></a>
### 蓝色/黑色/绿色单元格颜色
- **蓝色**（`Font(color="0000FF")`）——人工输入的硬编码输入。例如收入驱动因素、WACC 输入、终值增长率、市场数据。
- **黑色**（默认）——公式。每个推导出的单元格都是实时的 Excel 公式。
- **绿色**（`Font(color="006100")`）——指向其他工作表或外部文件的链接。

审阅者可以快速扫描工作表，立即看出哪些是假设，哪些是计算值。

<a id="formulas-over-hardcodes"></a>
### 公式优先于硬编码
每个计算单元格**必须**是公式字符串，绝不能是 Python 中计算后粘贴为值的数字。

```python
# 错误——可能引发静默错误
ws["D20"] = revenue_prior_year * (1 + growth)

# 正确——当用户更改假设时可以灵活调整
ws["D20"] = "=D19*(1+$B$8)"
```

允许的硬编码数字仅限于：
1. 原始历史输入（实际收入、报告 EBITDA 等）
2. 用户需要调整的驱动假设（增长率、WACC 输入、终值 g）
3. 当前市场数据（股价、债务余额）——需附带单元格注释，注明来源和日期
如果你发现自己正在用 Python 计算某个值并把结果写进去，请停下来。

<a id="named-ranges-for-cross-sheet-references"></a>
### 跨表引用的命名区域
对于从其他工作表、演示文稿或备忘录中引用的任何数字，请使用命名区域。

```python
from openpyxl.workbook.defined_name import DefinedName
wb.defined_names["WACC"] = DefinedName("WACC", attr_text="Inputs!$C$8")
# 然后在其他地方：
calc["D30"] = "=D29/WACC"
```

<a id="balance-checks-tab"></a>
### 勾稽检查工作表
添加一个 `Checks` 工作表，将所有内容关联起来并显示 TRUE/FALSE：
- 资产负债表平衡（资产 = 负债 + 权益）
- 现金流量表与资产负债表上现金的期间变动勾稽一致
- 各部分之和与合并总数勾稽一致
- 计算范围内没有隐藏的硬编码

示例：
```python
checks = wb.create_sheet("Checks")
checks["A2"] = "BS balances"
checks["B2"] = "=IS!D20-IS!D21-IS!D22"
checks["C2"] = "=ABS(B2)<0.01"  # TRUE/FALSE
```

<a id="cell-comments-on-every-hardcoded-input"></a>
### 每个硬编码输入都添加单元格批注
在创建单元格的同时添加批注，不要事后补。

```python
from openpyxl.comments import Comment
ws["C2"] = 1_250_000_000
ws["C2"].font = Font(color="0000FF")
ws["C2"].comment = Comment("Source: 10-K FY2024, p.47, revenue line", "analyst")
```

格式：`Source: [系统/文档], [日期], [参考], [URL（如适用）]`。

永远不要推迟标注来源。永远不要写 `TODO: add source`。

<a id="skeleton-typical-financial-model"></a>
## 骨架：典型财务模型

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
from pathlib import Path

BLUE = Font(color="0000FF")
BLACK = Font(color="000000")
GREEN = Font(color="006100")
BOLD = Font(bold=True)
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)

wb = Workbook()

# --- 输入工作表 ---
inp = wb.active
inp.title = "Inputs"
inp["A1"] = "MARKET DATA & KEY INPUTS"
inp["A1"].font = HEADER_FONT
inp["A1"].fill = HEADER_FILL
inp.merge_cells("A1:C1")

inp["B3"] = "Revenue FY2024"
inp["C3"] = 1_250_000_000
inp["C3"].font = BLUE
inp["C3"].comment = Comment("Source: 10-K FY2024 p.47", "model")

inp["B4"] = "Growth Rate"
inp["C4"] = 0.12
inp["C4"].font = BLUE

# --- 计算工作表 ---
calc = wb.create_sheet("DCF")
calc["B2"] = "Projected Revenue"
calc["C2"] = "=Inputs!C3*(1+Inputs!C4)"   # 公式，黑色

# --- 检查工作表 ---
chk = wb.create_sheet("Checks")
chk["A2"] = "BS balances"
chk["B2"] = "=ABS(BS!D20-BS!D21-BS!D22)<0.01"

Path("./out").mkdir(exist_ok=True)
wb.save("./out/model.xlsx")
```

<a id="section-headers-with-merged-cells"></a>
## 带合并单元格的节标题

openpyxl 的一个小特性：合并时，在左上角单元格设置值，并单独设置整个范围的样式。

```python
ws["A7"] = "CASH FLOW PROJECTION"
ws["A7"].font = HEADER_FONT
ws.merge_cells("A7:H7")
for col in range(1, 9):  # A..H
    ws.cell(row=7, column=col).fill = HEADER_FILL
```

<a id="sensitivity-tables"></a>
## 敏感性分析表

用循环构建，不要在每个单元格硬编码公式。规则：

- **行/列数为奇数**（5×5 或 7×7）—— 保证有一个真正的中心单元格。
- **中心单元格 = 基准情形。** 中间行/列的标题必须等于模型实际的 WACC 和终值增长率，这样中心输出就等于基准情形的隐含股价。这是合理性检查。
- **用中蓝色填充（`"BDD7EE"`）加粗突出显示中心单元格。**
- 每个单元格都填入完整的重新计算公式——绝不用近似值。
```python
# 5x5 WACC（行）x 终值增长率（列）敏感性分析
wacc_axis = [0.08, 0.085, 0.09, 0.095, 0.10]        # 中心行 = 基准 9.0%
term_axis = [0.02, 0.025, 0.03, 0.035, 0.04]        # 中心列 = 基准 3.0%

start_row = 40
ws.cell(row=start_row, column=1).value = "隐含股价（美元）"
ws.cell(row=start_row, column=1).font = BOLD

for j, g in enumerate(term_axis):
    ws.cell(row=start_row+1, column=2+j).value = g
    ws.cell(row=start_row+1, column=2+j).font = BLUE

for i, w in enumerate(wacc_axis):
    r = start_row + 2 + i
    ws.cell(row=r, column=1).value = w
    ws.cell(row=r, column=1).font = BLUE
    for j, g in enumerate(term_axis):
        c = 2 + j
        # 完整的 DCF 重新计算公式（为示意简化）。
        # 在实际模型中，该公式会引用完整的预测区域。
        ws.cell(row=r, column=c).value = (
            f"=SUMPRODUCT(FCF_range,1/(1+{w})^year_offset) + "
            f"FCF_terminal*(1+{g})/({w}-{g})/(1+{w})^terminal_year"
        )

# 高亮中心单元格（基准情况）
center = ws.cell(row=start_row+2+len(wacc_axis)//2,
                 column=2+len(term_axis)//2)
center.fill = PatternFill("solid", fgColor="BDD7EE")
center.font = BOLD
```

<a id="recalculating-before-delivery"></a>
## 交付前重新计算

openpyxl 写入的是公式字符串，但不会执行计算。Excel 在打开时会重新计算，但下游消费者（自动检查脚本、CI）需要计算后的值。

在交付前运行 LibreOffice 或专门的重新计算步骤：

```bash
# LibreOffice 无头重新计算
libreoffice --headless --calc --convert-to xlsx ./out/model.xlsx --outdir ./out/
```

或者使用 Python 重新计算辅助脚本（参见本 skill 中的 `scripts/recalc.py`）。

<a id="model-layout-planning"></a>
## 模型布局规划

在编写任何公式之前：
1. 定义所有部分的起始行位置
2. 写入所有表头和标签
3. 写入所有区域分隔线和空行
4. **然后** 使用锁定的行位置写入公式

这可以避免级联公式断裂问题——如果在公式写完后再插入表头行，会导致所有下游引用偏移。

<a id="verify-step-by-step-with-the-user"></a>
## 与用户逐步验证

对于大型模型（DCF、三表联动、LBO），在继续之前停下来向用户展示中间结果。在构建下游敏感性表格之前发现错误的利润率假设，可以节省一个小时。

检查点模式：
- 输入区域之后 → 展示原始输入，确认后开始预测
- 收入预测之后 → 确认营收和增长率
- FCF 构建之后 → 确认完整的自由现金流表
- WACC 之后 → 确认输入
- 估值之后 → 确认权益桥
- **然后** 构建敏感性表格

<a id="when-not-to-use-this-skill"></a>
## 何时不使用本技能

- 用户正在与 Office MCP 配合进行实时 Excel 操作时 — 请直接操作他们的实时工作簿。
- 纯表格数据导出，不涉及公式时 — 使用 `csv` 或 `pandas.to_excel` 更简单。
- 需要大量交互的仪表盘/图表时 — 使用真正的 BI 工具。

<a id="attribution"></a>
## 归属

本技能中使用的约定（蓝色/黑色/绿色、公式优先于硬编码、命名区域、敏感性规则）改编自 Anthropic 的 Claude for Financial Services 插件套件，采用 Apache-2.0 许可。原文：https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/xlsx-author
