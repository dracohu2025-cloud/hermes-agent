---
title: "Powerpoint — 创建、读取、编辑"
sidebar_label: "Powerpoint"
description: "创建、读取、编辑"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Powerpoint {#powerpoint}

创建、读取、编辑 .pptx 演示文稿、幻灯片、备注、模板。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/powerpoint` |
| 许可证 | 专有。完整条款见 LICENSE.txt |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这就是 Agent 在技能激活时看到的指令。
:::

# Powerpoint 技能 {#powerpoint-skill}

## 使用场景 {#when-to-use}

只要 .pptx 文件以任何方式作为输入、输出或两者兼具时，都应使用此技能。这包括：创建幻灯片、演示文稿；读取、解析或提取任何 .pptx 文件中的文本（即使提取的内容将用于其他地方，如电子邮件或摘要）；编辑、修改或更新现有演示文稿；合并或拆分幻灯片文件；处理模板、布局、演讲者备注或评论。当用户提到“deck”、“slides”、“presentation”或引用 .pptx 文件名时，无论他们随后打算如何处理内容，都应触发此技能。如果需要打开、创建或触碰 .pptx 文件，请使用此技能。
## 快速参考 {#quick-reference}

| 任务 | 指南 |
|------|------|
| 读取/分析内容 | `python -m markitdown presentation.pptx` |
| 从模板编辑或创建 | 阅读 [editing.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/powerpoint/editing.md) |
| 从头创建 | 阅读 [pptxgenjs.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/powerpoint/pptxgenjs.md) |

---

## 读取内容 {#reading-content}

```bash
# 文本提取
python -m markitdown presentation.pptx

# 视觉概览
python scripts/thumbnail.py presentation.pptx

# 原始 XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## 编辑工作流 {#editing-workflow}

**阅读 [editing.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/powerpoint/editing.md) 获取完整详情。**

1. 使用 `thumbnail.py` 分析模板
2. 解包 → 操作幻灯片 → 编辑内容 → 清理 → 打包

---

## 从头创建 {#creating-from-scratch}

**阅读 [pptxgenjs.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/powerpoint/pptxgenjs.md) 获取完整详情。**
在没有模板或参考演示文稿时使用。

---

## 设计思路 {#design-ideas}

**不要制作无聊的幻灯片。** 白底黑字的简单项目符号不会给任何人留下印象。请针对每张幻灯片考虑此列表中的创意。

### 开始之前 {#before-starting}

- **选择大胆且贴合内容的配色方案**：配色方案应让人感觉是为当前主题专门设计的。如果把你的颜色套用到另一个完全不同的演示文稿中仍然“适用”，说明你的选择还不够具体。
- **主次分明，而非均等**：一种颜色应占主导（60-70% 的视觉权重），搭配 1-2 种辅助色调和一种醒目的强调色。绝不要让所有颜色权重相等。
- **深色/浅色对比**：标题和结论幻灯片使用深色背景，内容幻灯片使用浅色背景（“三明治”结构）。或者全程使用深色背景，营造高级感。
- **确定一个视觉主题**：挑选一个独特的元素并重复使用——圆角图片框、彩色圆圈中的图标、粗的单侧边框。让它在每张幻灯片中贯穿始终。

### 配色方案 {#color-palettes}
选择与主题匹配的颜色——不要默认使用通用的蓝色。以下调色板可供参考：

| 主题 | 主色 | 辅色 | 强调色 |
|-------|---------|-----------|--------|
| **午夜商务** | `1E2761`（海军蓝） | `CADCFC`（冰蓝） | `FFFFFF`（白色） |
| **森林与苔藓** | `2C5F2D`（森林绿） | `97BC62`（苔藓绿） | `F5F5F5`（奶油色） |
| **珊瑚能量** | `F96167`（珊瑚红） | `F9E795`（金色） | `2F3C7E`（海军蓝） |
| **暖陶土** | `B85042`（陶土红） | `E7E8D1`（沙色） | `A7BEAE`（鼠尾草绿） |
| **海洋渐变** | `065A82`（深蓝） | `1C7293`（蓝绿色） | `21295C`（午夜蓝） |
| **炭黑极简** | `36454F`（炭灰色） | `F2F2F2`（米白色） | `212121`（黑色） |
| **青绿信任** | `028090`（青绿色） | `00A896`（海沫绿） | `02C39A`（薄荷绿） |
| **浆果与奶油** | `6D2E46`（浆果红） | `A26769`（灰玫瑰） | `ECE2D0`（奶油色） |
| **鼠尾草宁静** | `84B59F`（鼠尾草绿） | `69A297`（桉树绿） | `50808E`（石板灰） |
| **樱桃大胆** | `990011`（樱桃红） | `FCF6F5`（米白色） | `2F3C7E`（海军蓝） |
### 每张幻灯片 {#for-each-slide}

**每张幻灯片都需要一个视觉元素**——图片、图表、图标或形状。纯文本的幻灯片容易被遗忘。

**布局选项：**
- 两栏（左侧文字，右侧插图）
- 图标 + 文字行（彩色圆圈中的图标，粗体标题，下方描述）
- 2x2 或 2x3 网格（一侧图片，另一侧内容块网格）
- 半出血图片（占据整左或整右侧）并叠加内容

**数据展示：**
- 大号数据标注（60-72pt 的大数字，下方带小标签）
- 对比列（前后对比、优缺点、并排选项）
- 时间线或流程（编号步骤、箭头）

**视觉润色：**
- 章节标题旁的小彩色圆圈中的图标
- 关键数据或标语使用斜体强调文字

### 字体排版 {#typography}

**选择一组有趣的字体搭配**——不要默认使用 Arial。选一个有特色的标题字体，再搭配一个干净的正文字体。

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
| 幻灯片标题 | 36-44pt 粗体 |
| 章节标题 | 20-24pt 粗体 |
| 正文 | 14-16pt |
| 说明文字 | 10-12pt 浅色 |

### 间距 {#spacing}

- 最小边距 0.5 英寸
- 内容块之间 0.3-0.5 英寸
- 留出呼吸空间——不要填满每一寸

### 避免（常见错误） {#avoid-common-mistakes}

- **不要重复使用相同的布局** —— 在不同幻灯片中交替使用分栏、卡片和标注框
- **不要将正文居中** —— 段落和列表左对齐；仅标题可居中
- **不要忽视字号对比** —— 标题需要 36pt 以上才能与 14-16pt 的正文形成区分
- **不要默认使用蓝色** —— 选择能反映具体主题的颜色
- **不要随意混用间距** —— 选择 0.3 英寸或 0.5 英寸的间距并保持一致使用
- **不要只给一张幻灯片设计样式而其他保持朴素** —— 要么全面投入，要么全程保持简洁
- **不要创建纯文本幻灯片** —— 添加图片、图标、图表或视觉元素；避免纯标题加项目符号
- **不要忘记文本框内边距** —— 当将线条或形状与文本边缘对齐时，在文本框上设置 `margin: 0` 或偏移形状以考虑内边距
- **不要使用低对比度元素** —— 图标和文字都需要与背景形成强烈对比；避免浅色背景上的浅色文字或深色背景上的深色文字
- **绝对不要在标题下方使用强调线** —— 这是 AI 生成幻灯片的标志；改用空白或背景色
---

## QA（必需） {#qa-required}

**假设存在问题。你的任务是找出它们。**

你的第一次渲染几乎不可能正确。把 QA 当作一次找 bug 的过程，而不是确认步骤。如果你第一次检查没发现任何问题，那说明你检查得不够仔细。

### 内容 QA {#content-qa}

```bash
python -m markitdown output.pptx
```

检查缺失内容、拼写错误、顺序错误。

**使用模板时，检查是否有残留的占位文本：**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

如果 grep 返回了结果，先修复它们再宣布成功。

### 视觉 QA {#visual-qa}

**⚠️ 使用 SUBAGENTS** —— 即使只有 2-3 张幻灯片。你一直盯着代码，会看到你期望看到的，而不是实际存在的。Subagents 有全新的视角。

将幻灯片转换为图片（参见[转换为图片](#converting-to-images)），然后使用以下提示：

```
视觉检查这些幻灯片。假设存在问题——找出它们。

检查：
- 重叠元素（文字穿过形状、线条穿过文字、堆叠的元素）
- 文本溢出或超出边缘/框边界被截断
- 装饰性线条针对单行文字定位，但标题换行成了两行
- 来源引用或页脚与上方内容碰撞
- 元素间距过近（< 0.3 英寸）或卡片/部分几乎接触
- 间距不均匀（一处有大片空白，另一处拥挤）
- 距离幻灯片边缘的边距不足（< 0.5 英寸）
- 列或类似元素未对齐一致
- 低对比度文字（例如，浅灰色文字在米色背景上）
- 低对比度图标（例如，深色图标在深色背景上，没有对比色圆圈）
- 文本框过窄导致过度换行
- 残留的占位内容

对于每张幻灯片，列出问题或关注点，即使很小。

阅读并分析这些图片：
1. /path/to/slide-01.jpg（预期：[简要描述]）
2. /path/to/slide-02.jpg（预期：[简要描述]）

报告发现的所有问题，包括小问题。
```
### 验证循环 {#verification-loop}

1. 生成幻灯片 → 转换为图片 → 检查
2. **列出发现的问题**（如果未发现问题，则更严格地重新检查）
3. 修复问题
4. **重新验证受影响的幻灯片**——一次修复常常会引发另一个问题
5. 重复，直到完整一轮检查未发现新问题

**在完成至少一次修复并验证的循环之前，不要宣布成功。**

---

## 转换为图片 {#converting-to-images}

将演示文稿转换为单张幻灯片图片，以便进行视觉检查：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

这会生成 `slide-01.jpg`、`slide-02.jpg` 等文件。

修复后重新渲染特定幻灯片：

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## 依赖项 {#dependencies}

- `pip install "markitdown[pptx]"` - 文本提取
- `pip install Pillow` - 缩略图网格
- `npm install -g pptxgenjs` - 从头创建演示文稿
- LibreOffice（`soffice`）- PDF 转换（通过 `scripts/office/soffice.py` 自动配置沙箱环境）
- Poppler（`pdftoppm`）- PDF 转图片
