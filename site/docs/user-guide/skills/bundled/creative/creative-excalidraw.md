---
title: "Excalidraw — 手绘风格 Excalidraw JSON 图表（架构图、流程图、时序图）"
sidebar_label: "Excalidraw"
description: "手绘风格 Excalidraw JSON 图表（架构图、流程图、时序图）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="excalidraw"></a>
# Excalidraw

手绘风格 Excalidraw JSON 图表（架构图、流程图、时序图）。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/excalidraw` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Excalidraw`、`图表`、`流程图`、`架构`、`可视化`、`JSON` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="excalidraw-diagram-skill"></a>
# Excalidraw 图表技能

通过编写标准 Excalidraw 元素 JSON 并保存为 `.excalidraw` 文件来创建图表。这些文件可以直接拖放到 [excalidraw.com](https://excalidraw.com) 上进行查看和编辑。无需账户、无需 API 密钥、无需渲染库——只需 JSON。

<a id="when-to-use"></a>
## 何时使用

为架构图、流程图、时序图、概念图等生成 `.excalidraw` 文件。文件可以在 excalidraw.com 上打开，或上传以获取可分享的链接。

<a id="workflow"></a>
## 工作流程

1. **加载此技能**（您已加载）
2. **编写元素 JSON**——一个 Excalidraw 元素对象数组
3. **保存文件**：使用 `write_file` 创建一个 `.excalidraw` 文件
4. **（可选）上传**：通过 `terminal` 使用 `scripts/upload.py` 获取可分享链接

<a id="saving-a-diagram"></a>
### 保存图表

将元素数组包裹在标准的 `.excalidraw` 信封结构中，并使用 `write_file` 保存：

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "hermes-agent",
  "elements": [ ...您的元素数组在此... ],
  "appState": {
    "viewBackgroundColor": "#ffffff"
  }
}
```

保存到任意路径，例如 `~/diagrams/my_diagram.excalidraw`。

<a id="uploading-for-a-shareable-link"></a>
### 上传以获取可分享链接

通过终端运行上传脚本（位于此技能的 `scripts/` 目录中）：

```bash
python skills/diagramming/excalidraw/scripts/upload.py ~/diagrams/my_diagram.excalidraw
```

此操作将文件上传到 excalidraw.com（无需账户）并打印一个可分享的 URL。需要 `cryptography` pip 包（`pip install cryptography`）。

---

<a id="element-format-reference"></a>
## 元素格式参考

<a id="required-fields-all-elements"></a>
### 必填字段（所有元素）
`type`、`id`（唯一字符串）、`x`、`y`、`width`、`height`

<a id="defaults-skip-these-they-re-applied-automatically"></a>
### 默认值（可省略——它们会自动应用）
- `strokeColor`：`"#1e1e1e"`
- `backgroundColor`：`"transparent"`
- `fillStyle`：`"solid"`
- `strokeWidth`：`2`
- `roughness`：`1`（手绘风格）
- `opacity`：`100`

画布背景为白色。

<a id="element-types"></a>
### 元素类型

**矩形**：
```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 100 }
```
- `roundness: { "type": 3 }` 用于圆角
- `backgroundColor: "#a5d8ff"`、`fillStyle: "solid"` 用于填充

**椭圆**：
```json
{ "type": "ellipse", "id": "e1", "x": 100, "y": 100, "width": 150, "height": 150 }
```

**菱形**：
```json
{ "type": "diamond", "id": "d1", "x": 100, "y": 100, "width": 150, "height": 150 }
```
**带标签的形状（容器绑定）** —— 创建一个绑定到形状的文本元素：

> **警告：** 不要在形状上使用 `"label": { "text": "..." }`。这不是有效的 Excalidraw 属性，会被静默忽略，产生空白形状。**必须**使用下面的容器绑定方法。

该形状需要列出文本的 `boundElements`，文本需要指向回形状的 `containerId`：
```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 80,
  "roundness": { "type": 3 }, "backgroundColor": "#a5d8ff", "fillStyle": "solid",
  "boundElements": [{ "id": "t_r1", "type": "text" }] },
{ "type": "text", "id": "t_r1", "x": 105, "y": 110, "width": 190, "height": 25,
  "text": "Hello", "fontSize": 20, "fontFamily": 1, "strokeColor": "#1e1e1e",
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "r1", "originalText": "Hello", "autoResize": true }
```
- 适用于矩形、椭圆、菱形
- 当设置了 `containerId` 时，文本会被 Excalidraw 自动居中
- 文本的 `x`/`y`/`width`/`height` 是近似值——Excalidraw 在加载时会重新计算
- `originalText` 应与 `text` 保持一致
- 始终包含 `fontFamily: 1`（Virgil/手绘字体）

**带标签的箭头** —— 同样的容器绑定方法：
```json
{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 200, "height": 0,
  "points": [[0,0],[200,0]], "endArrowhead": "arrow",
  "boundElements": [{ "id": "t_a1", "type": "text" }] },
{ "type": "text", "id": "t_a1", "x": 370, "y": 130, "width": 60, "height": 20,
  "text": "connects", "fontSize": 16, "fontFamily": 1, "strokeColor": "#1e1e1e",
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "a1", "originalText": "connects", "autoResize": true }
```

**独立文本**（仅用于标题和注释——无容器）：
```json
{ "type": "text", "id": "t1", "x": 150, "y": 138, "text": "Hello", "fontSize": 20,
  "fontFamily": 1, "strokeColor": "#1e1e1e", "originalText": "Hello", "autoResize": true }
```
- `x` 是左边距。要使其在位置 `cx` 处居中：`x = cx - (text.length * fontSize * 0.5) / 2`
- 不要依赖 `textAlign` 或 `width` 来定位

**箭头**：
```json
{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 200, "height": 0,
  "points": [[0,0],[200,0]], "endArrowhead": "arrow" }
```
- `points`：相对于元素 `x`、`y` 的 `[dx, dy]` 偏移
- `endArrowhead`：`null` | `"arrow"` | `"bar"` | `"dot"` | `"triangle"`
- `strokeStyle`：`"solid"`（默认）| `"dashed"` | `"dotted"`

<a id="arrow-bindings-connect-arrows-to-shapes"></a>
### 箭头绑定（将箭头连接到形状）

```json
{
  "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 150, "height": 0,
  "points": [[0,0],[150,0]], "endArrowhead": "arrow",
  "startBinding": { "elementId": "r1", "fixedPoint": [1, 0.5] },
  "endBinding": { "elementId": "r2", "fixedPoint": [0, 0.5] }
}
```

`fixedPoint` 坐标：`top=[0.5,0]`、`bottom=[0.5,1]`、`left=[0,0.5]`、`right=[1,0.5]`

<a id="drawing-order-z-order"></a>
### 绘制顺序（z-order）
- 数组顺序 = z-order（第一个 = 最底层，最后一个 = 最顶层）
- 逐步发出：背景区域 → 形状 → 其绑定的文本 → 其箭头 → 下一个形状
- 错误：先所有矩形，然后所有文本，然后所有箭头
- 正确：bg_zone → shape1 → text_for_shape1 → arrow1 → arrow_label_text → shape2 → text_for_shape2 → ...
- 始终将绑定的文本元素紧跟在它的容器形状之后
<a id="sizing-guidelines"></a>
### 尺寸指南

**字号：**
- 正文、标签、描述的最小 `fontSize`：**16**
- 标题和标头的最小 `fontSize`：**20**
- 仅次要注释最小 `fontSize`：**14**（尽量少用）
- 不得使用 `fontSize` 低于 14

**元素尺寸：**
- 带标签的矩形/椭圆的最小形状尺寸：120x60
- 元素之间至少保留 20-30 像素间距
- 优先使用更少但更大的元素，避免大量微小元素

<a id="color-palette"></a>
### 色板

完整颜色表格见 `references/colors.md`。快速参考：

| 用途 | 填充色 | 十六进制 |
|-----|--------|----------|
| 主要/输入 | 浅蓝 | `#a5d8ff` |
| 成功/输出 | 浅绿 | `#b2f2bb` |
| 警告/外部 | 浅橙 | `#ffd8a8` |
| 处理/特殊 | 浅紫 | `#d0bfff` |
| 错误/关键 | 浅红 | `#ffc9c9` |
| 备注/决策 | 浅黄 | `#fff3bf` |
| 存储/数据 | 浅青绿 | `#c3fae8` |

<a id="tips"></a>
### 提示
- 在整个图表中一致使用色板
- **文本对比度至关重要**——切勿在白色背景上使用浅灰色。白色背景上的最小文本颜色：`#757575`
- 文本中不要使用表情符号——它们在 Excalidraw 的字体中无法正确渲染
- 深色模式图表见 `references/dark-mode.md`
- 更多示例见 `references/examples.md`
