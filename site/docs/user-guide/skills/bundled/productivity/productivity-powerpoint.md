---
title: "Powerpoint — 创建、读取、编辑"
sidebar_label: "Powerpoint"
description: "创建、读取、编辑"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="powerpoint"></a>
# Powerpoint

创建、读取、编辑 .pptx 演示文稿、幻灯片、备注、模板。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/powerpoint` |
| 许可证 | 专有。完整条款见 LICENSE.txt |
| 支持平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="powerpoint-skill"></a>
# Powerpoint 技能

<a id="when-to-use"></a>
## 何时使用

只要 .pptx 文件以任何方式参与（作为输入、输出或两者兼有），就应使用此技能。这包括：创建幻灯片组、推介演示文稿或演示文稿；读取、解析或提取任何 .pptx 文件中的文本（即使提取的内容将用于其他地方，如邮件或摘要）；编辑、修改或更新现有演示文稿；合并或拆分幻灯片文件；使用模板、布局、演讲者备注或批注。当用户提到“演示文稿”、“幻灯片”、“展示”或引用 .pptx 文件名时，无论他们之后打算如何处理内容，都应触发此技能。如果需要打开、创建或处理 .pptx 文件，请使用此技能。
<a id="quick-reference"></a>
## 快速参考

| 任务 | 指导 |
|------|------|
| 读取/分析内容 | `python -m markitdown presentation.pptx` |
| 从模板编辑或创建 | 阅读 [editing.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/powerpoint/editing.md) |
| 从零创建 | 阅读 [pptxgenjs.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/powerpoint/pptxgenjs.md) |

---

<a id="reading-content"></a>
## 读取内容

```bash
# 文本提取
python -m markitdown presentation.pptx

# 视觉概览
python scripts/thumbnail.py presentation.pptx

# 原始 XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

<a id="editing-workflow"></a>
## 编辑工作流

**阅读 [editing.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/powerpoint/editing.md) 了解全部详情。**

1. 使用 `thumbnail.py` 分析模板
2. 解包 → 操作幻灯片 → 编辑内容 → 清理 → 打包

---

<a id="creating-from-scratch"></a>
## 从零创建

**阅读 [pptxgenjs.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/powerpoint/pptxgenjs.md) 了解全部详情。**
在没有可用模板或参考演示文稿时使用。

---

<a id="design-ideas"></a>
## 设计创意

**不要制作乏味的幻灯片。** 白底黑字、平铺直叙的要点不会给人留下任何印象。请考虑为每张幻灯片运用以下列表中的创意。

<a id="before-starting"></a>
### 开始之前

- **选择大胆且与内容相符的配色方案**：配色方案应让人感觉是为当前主题专门设计的。如果把你选择的颜色换到另一个完全不同的演示文稿中，看起来依然“合适”，那说明你的选择还不够有针对性。
- **主次分明，而非均衡**：一种颜色应占主导地位（60-70% 的视觉权重），搭配 1-2 种辅助色调和一种鲜明的强调色。切勿让所有颜色权重相等。
- **深色/浅色对比**：标题和结论幻灯片使用深色背景，内容幻灯片使用浅色背景（“三明治”结构）。或者，全程使用深色背景以营造高级感。
- **确定一个视觉主题**：挑选一个独特元素并重复使用——例如圆角图片框、彩色圆圈内的图标、粗大单侧边框。让这个元素贯穿每一张幻灯片。

<a id="color-palettes"></a>
### 配色方案
选择与主题匹配的颜色——不要默认使用通用的蓝色。以下调色板可供参考：

| 主题 | 主色 | 辅色 | 强调色 |
|-------|---------|-----------|--------|
| **午夜商务** | `1E2761`（海军蓝） | `CADCFC`（冰蓝） | `FFFFFF`（白色） |
| **森林与苔藓** | `2C5F2D`（森林绿） | `97BC62`（苔藓绿） | `F5F5F5`（奶油色） |
| **珊瑚能量** | `F96167`（珊瑚红） | `F9E795`（金色） | `2F3C7E`（海军蓝） |
| **暖陶土** | `B85042`（陶土红） | `E7E8D1`（沙色） | `A7BEAE`（鼠尾草绿） |
| **海洋渐变** | `065A82`（深蓝） | `1C7293`（蓝绿色） | `21295C`（午夜蓝） |
| **炭黑极简** | `36454F`（炭灰色） | `F2F2F2`（米白色） | `212121`（黑色） |
| **蓝绿信任** | `028090`（蓝绿色） | `00A896`（海沫绿） | `02C39A`（薄荷绿） |
| **浆果与奶油** | `6D2E46`（浆果红） | `A26769`（灰玫瑰色） | `ECE2D0`（奶油色） |
| **鼠尾草宁静** | `84B59F`（鼠尾草绿） | `69A297`（桉树绿） | `50808E`（石板灰） |
| **樱桃醒目** | `990011`（樱桃红） | `FCF6F5`（米白色） | `2F3C7E`（海军蓝） |
<a id="for-each-slide"></a>
### 针对每张幻灯片

**每张幻灯片都需要有一个视觉元素**——图片、图表、图标或形状。纯文本的幻灯片容易被遗忘。

**布局选项：**
- 两列布局（左侧文字，右侧插图）
- 图标 + 文字行（彩色圆圈内放置图标，粗体标题，下方描述）
- 2x2 或 2x3 网格布局（一侧为图片，另一侧为内容块网格）
- 半出血图片（占满左侧或右侧）并叠加内容

**数据展示：**
- 大号数据标注（大号数字 60-72pt，下方配小号标签）
- 对比栏（前后对比、优缺点、并排选项）
- 时间线或流程（带编号的步骤、箭头）

**视觉润色：**
- 章节标题旁的小彩色圆圈内放置图标
- 关键数据或标语使用斜体强调文本

<a id="typography"></a>
### 字体排版

**选择一套有趣的字体组合** —— 不要默认使用 Arial。选择一套有特色的标题字体，并搭配一套简洁的正文字体。

| 标题字体 | 正文字体 |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |
| 元素 | 字号 |
|---------|------|
| 幻灯片标题 | 36-44pt 加粗 |
| 章节标题 | 20-24pt 加粗 |
| 正文 | 14-16pt |
| 说明文字 | 10-12pt 灰色 |

<a id="spacing"></a>
### 间距

- 最小页边距 0.5 英寸
- 内容块之间 0.3–0.5 英寸
- 留出呼吸空间，不要填满每一寸

<a id="avoid-common-mistakes"></a>
### 避免（常见错误）

- **不要重复使用相同的布局**——在不同幻灯片上交替使用列、卡片和突出区块
- **不要将正文居中**——段落和列表左对齐；只有标题可以居中
- **不要吝啬字号对比**——标题需要 36pt 以上，才能从 14–16pt 的正文中脱颖而出
- **不要默认使用蓝色**——选择能反映特定主题的颜色
- **不要随意混合间距**——统一使用 0.3 英寸或 0.5 英寸的间隙，并保持一致
- **不要只美化一张幻灯片，其他保持空白**——要么全面执行，要么全程保持简洁
- **不要创建纯文本的幻灯片**——添加图片、图标、图表或视觉元素；避免纯标题加项目符号
- **不要忘记文本框的内边距**——当对齐线条或形状与文本边缘时，将文本框的 `margin` 设置为 0，或偏移形状以补偿内边距
- **不要使用低对比度的元素**——图标和文本都需要与背景形成强烈对比；避免浅色背景上的浅色文字或深色背景上的深色文字
- **绝对不要在标题下方使用装饰线**——这是 AI 生成的幻灯片的一个特征；改用空白区域或背景色来代替
---

<a id="qa-required"></a>
## QA（必需）

**假设存在问题。你的任务是找出它们。**

你的第一次渲染几乎永远不正确。将 QA 视为一次 Bug 排查，而不是确认步骤。如果第一次检查时你发现零问题，那说明你检查得不够仔细。

<a id="content-qa"></a>
### 内容 QA

```bash
python -m markitdown output.pptx
```

检查缺失内容、拼写错误、顺序错误。

**使用模板时，检查是否有残留的占位文本：**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

如果 grep 返回结果，请在宣布成功之前修复它们。

<a id="visual-qa"></a>
### 视觉 QA

**⚠️ 使用 subagents** — 即使只有 2-3 张幻灯片。你一直盯着代码，会看到你期望看到的东西，而不是实际存在的东西。Subagents 拥有全新的视角。

将幻灯片转换为图片（参见 [转换为图片](#converting-to-images)），然后使用以下提示：

```
视觉检查这些幻灯片。假设存在问题——找出它们。

检查：
- 元素重叠（文字穿过形状、线条穿过文字、堆叠的元素）
- 文本溢出或截断在边缘/框边界处
- 装饰性线条针对单行文本定位，但标题换行为两行
- 来源引用或页脚与上方内容碰撞
- 元素间距过近（间隙 < 0.3 英寸）或卡片/部分几乎接触
- 间隙不均匀（一处有大片空白，另一处拥挤）
- 距离幻灯片边缘的边距不足（< 0.5 英寸）
- 列或类似元素未对齐一致
- 低对比度文本（例如，浅灰色文本在米色背景上）
- 低对比度图标（例如，深色图标在深色背景上，没有对比色圆圈）
- 文本框过窄导致过度换行
- 残留的占位内容

对于每张幻灯片，列出问题或关注区域，即使很小。

阅读并分析这些图片：
1. /path/to/slide-01.jpg（预期：[简要描述]）
2. /path/to/slide-02.jpg（预期：[简要描述]）

报告发现的所有问题，包括小问题。
```
<a id="verification-loop"></a>
### 验证循环

1. 生成幻灯片 → 转换为图片 → 检查
2. **列出发现的问题**（如果未发现问题，则更仔细地再次检查）
3. 修复问题
4. **重新验证受影响的幻灯片**——一次修复往往会产生另一个问题
5. 重复，直到完整检查后没有新问题

**在完成至少一个修复并验证的循环之前，不要宣告成功。**

---

<a id="converting-to-images"></a>
## 转换为图片

将演示文稿转换为单张幻灯片图片，以便进行视觉检查：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

这将创建 `slide-01.jpg`、`slide-02.jpg` 等文件。

修复后重新渲染特定幻灯片：

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

<a id="dependencies"></a>
## 依赖项

- `pip install "markitdown[pptx]"` - 文本提取
- `pip install Pillow` - 缩略图网格
- `npm install -g pptxgenjs` - 从头创建
- LibreOffice (`soffice`) - PDF 转换（通过 `scripts/office/soffice.py` 为沙盒环境自动配置）
- Poppler (`pdftoppm`) - PDF 转图片
