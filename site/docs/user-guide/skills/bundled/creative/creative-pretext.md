---
title: "Pretext"
sidebar_label: "Pretext"
description: "在结合 @chenglou/pretext 构建创意浏览器演示时使用——用于 ASCII 艺术的无 DOM 文本布局、绕障排版、文本即几何的游戏、动态排版以及文本驱动的生成艺术。默认生成单文件 HTML 演示。"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="pretext"></a>
# Pretext

在结合 @chenglou/pretext 构建创意浏览器演示时使用——用于 ASCII 艺术的无 DOM 文本布局、绕障排版、文本即几何的游戏、动态排版以及文本驱动的生成艺术。默认生成单文件 HTML 演示。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/pretext` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `creative-coding`, `typography`, `pretext`, `ascii-art`, `canvas`, `generative`, `text-layout`, `kinetic-typography` |
| 相关技能 | [`p5js`](/user-guide/skills/bundled/creative/creative-p5js), [`claude-design`](/user-guide/skills/bundled/creative/creative-claude-design), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw), [`architecture-diagram`](/user-guide/skills/bundled/creative/creative-architecture-diagram) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="pretext-creative-demos"></a>
# Pretext 创意演示

<a id="overview"></a>
## 概述

[`@chenglou/pretext`](https://github.com/chenglou/pretext) 是一个 15KB 零依赖的 TypeScript 库，由 Cheng Lou（React 核心成员、ReasonML、Midjourney）开发，用于**无 DOM 的多行文本测量与布局**。它只做一件事：给定 `(text, font, width)`，返回换行位置、每行宽度、每个字素的位置以及总高度——全部通过 canvas 测量，无需重排。

听起来像是底层工具。但并非如此。因为它速度快且具有几何特性，所以它是一个**创意原语**：你可以以 60fps 的速度让段落围绕移动的精灵重排，构建关卡几何由真实单词构成的游戏，通过散文驱动 ASCII 标志，将文本粉碎成具有精确字素起始位置的粒子，或者打包收缩包裹的多行 UI，而无需任何 `getBoundingClientRect` 的抖动。

这个技能的存在是为了让 Hermes 能用它制作**酷炫的演示**——那种人们会发到 X 上的东西。请参阅 `pretext.cool` 和 `chenglou.me/pretext` 查看社区演示集合。

<a id="when-to-use"></a>
## 何时使用

当用户要求以下内容时使用：
- 一个“pretext 演示”/“酷炫的 pretext 东西”/“文本即 X”
- 文本围绕移动形状流动（英雄区、编辑布局、动画长页面）
- 使用**真实单词或散文**的 ASCII 艺术效果，而非等宽光栅
- 游戏场地/障碍物/砖块由文本构成的游戏（字母版俄罗斯方块、散文版打砖块）
- 具有逐字素物理效果的动态排版（粉碎、散开、聚集、流动）
- 排版生成艺术，尤其是非拉丁文字或混合文字
- 多行“收缩包裹”UI（能容纳文本的最小容器宽度）
- 任何需要在渲染*之前*知道换行位置的情况

以下情况不要使用：
- 静态 SVG/HTML 页面，CSS 已能解决布局——直接使用 CSS
- 富文本编辑器、通用内联格式化引擎（pretext 故意设计得很窄）
- 图像转文本（使用 `ascii-art` / `ascii-video` 技能）
- 纯 canvas 生成艺术，没有文本角色——使用 `p5js`
<a id="creative-standard"></a>
## Creative Standard

这是在浏览器中渲染的可视艺术作品。Pretext 返回数字；**你**负责绘制。

- **不要交付一个"hello world"示例。** `hello-orb-flow.html` 模板只是 *起点*。每个交付的示例必须加入有意的颜色、动态、构图，以及一个用户没有要求但会喜欢的视觉细节。
- **深色背景、暖色核心、考究的配色方案。** 经典的琥珀色底黑字（CRT/终端）可行，但炭灰色底冷白字（编辑风格）和低饱和度粉彩（Risograph）也同样可行。选一种并坚持使用。
- **比例字体是关键。** Pretext 的整体氛围是"非等宽"——请充分利用它。使用 Iowan Old Style、Inter、JetBrains Mono、Helvetica Neue 或可变字体。永远不要使用默认无衬线字体。
- **真实来源/文本，而不是 Lorem Ipsum。** 语料应有实际意义。简短宣言、诗歌、真实源代码、找到的文本、库自身的 README——永远不要用 `lorem ipsum`。
- **首次绘制即完美。** 没有加载状态，没有空白帧。示例必须在打开的瞬间看起来即可交付。

<a id="stack"></a>
## Stack

每个示例是单个自包含的 HTML 文件。无需构建步骤。

| 层级 | 工具 | 用途 |
|------|------|------|
| 核心 | `@chenglou/pretext` 通过 `esm.sh` CDN | 文本测量 + 行布局 |
| 渲染 | HTML5 Canvas 2D | 字形渲染、逐帧合成 |
| 分割 | `Intl.Segmenter`（内置） | 针对 emoji / CJK / 组合标记的语素分割 |
| 交互 | 原始 DOM 事件 | 鼠标 / 触摸 / 滚轮——无框架 |

```html
<script type="module">
import {
  prepare, layout,                   // use-case 1: 简单高度
  prepareWithSegments, layoutWithLines,  // use-case 2a: 固定宽度的行
  layoutNextLineRange, materializeLineRange, // use-case 2b: 流式 / 可变宽度
  measureLineStats, walkLineRanges,  // 统计而不分配字符串
} from "https://esm.sh/@chenglou/pretext@0.0.6";
</script>
```

固定版本。截止编写时为 `@0.0.6`——如果示例行为异常，请检查 [npm](https://www.npmjs.com/package/@chenglou/pretext) 以获取最新版本。

<a id="the-two-use-cases"></a>
## 两种使用场景

几乎所有需求都可以归为这两种形式之一。请掌握两者。

<a id="use-case-1-measure-then-render-with-css-dom"></a>
### 使用场景 1 — 测量，然后用 CSS/DOM 渲染

```js
const prepared = prepare(text, "16px Inter");
const { height, lineCount } = layout(prepared, 320, 20);
```

你仍然让浏览器绘制文本。Pretext 只是告诉你给定宽度下盒子会有多高，**无需** DOM 读取。适用于：
- 行包含换行文本的虚拟列表
- 需要精确卡片高度的瀑布流
- "这个标签是否合适？"的开发时检查
- 防止远程文本加载时的布局偏移

**确保 `font` 和 `letterSpacing` 与你的 CSS 完全同步。** Canvas `ctx.font` 格式（例如 `"16px Inter"`、`"500 17px 'JetBrains Mono'"`）必须与渲染的 CSS 匹配，否则测量会偏移。

<a id="use-case-2-measure-and-render-yourself"></a>
### 使用场景 2 — 自行测量 *并* 渲染

```js
const prepared = prepareWithSegments(text, FONT);
const { lines } = layoutWithLines(prepared, 320, 26);
for (let i = 0; i < lines.length; i++) {
  ctx.fillText(lines[i].text, 0, i * 26);
}
```
这是创意工作的核心所在。你拥有绘图的控制权，因此可以：
- 渲染到 canvas、SVG、WebGL 或任何坐标系
- 对每个字形进行变换（旋转、抖动、缩放、透明度）
- 将线条元数据（宽度、字素位置）用作几何数据

对于**每行可变宽度**的流动（文本绕排形状、文本在环形带中、文本在非矩形列中）：

```js
let cursor = { segmentIndex: 0, graphemeIndex: 0 };
let y = 0;
while (true) {
  const lineWidth = widthAtY(y);  // 你的函数：在这个 y 位置，通道有多宽？
  const range = layoutNextLineRange(prepared, cursor, lineWidth);
  if (!range) break;
  const line = materializeLineRange(prepared, range);
  ctx.fillText(line.text, leftEdgeAtY(y), y);
  cursor = range.end;
  y += lineHeight;
}
```

这是整个库中最重要的模式。它实现了“文本绕排拖拽精灵”的效果——那个在 X 上爆火的演示。

<a id="helpers-worth-knowing"></a>
### 值得了解的辅助工具

- `measureLineStats(prepared, maxWidth)` → `{ lineCount, maxLineWidth }` — 最宽的行，即多行收缩包裹宽度。
- `walkLineRanges(prepared, maxWidth, callback)` — 遍历行而不分配字符串。当你不需要字符，只想要字素的统计/物理数据时使用。
- `@chenglou/pretext/rich-inline` — 同样的系统，但用于混合字体/标签/提及的段落。从子路径导入。

<a id="demo-recipe-patterns"></a>
## 演示配方模式

社区语料库（参见 `references/patterns.md`）可归纳为几种强模式。选择一种并即兴发挥——除非有要求，否则不要发明新类别。

| 模式 | 关键 API | 示例想法 |
|---|---|---|
| **绕障碍物重排** | `layoutNextLineRange` + 每行宽度函数 | 编辑段落，围绕拖拽光标精灵展开 |
| **文本即几何游戏** | `layoutWithLines` + 每行碰撞矩形 | 打砖块游戏，每个砖块是一个测量过的单词 |
| **碎裂/粒子** | `walkLineRanges` → 每个字素 (x,y) → 物理 | 点击后句子爆炸成字母 |
| **ASCII 障碍排版** | `layoutNextLineRange` + 每行测量过的障碍跨度 | 位图 ASCII 标志、形状变形、可拖拽线框物体，使文本围绕其实际几何形状展开 |
| **编辑多栏** | 每栏 `layoutNextLineRange` + 共享光标 | 带引文的动画杂志跨页 |
| **动态文字** | `layoutWithLines` + 每行随时间变换 | 星球大战滚动、波浪、弹跳、故障效果 |
| **多行收缩包裹** | `measureLineStats` | 自动适应最紧凑容器的引用卡片 |

参见 `templates/donut-orbit.html` 和 `templates/hello-orb-flow.html` 获取可运行的单文件入门示例。

<a id="workflow"></a>
## 工作流程

1. **从上方表格中选取一个模式**，基于用户的需求。
2. **从模板开始**：
   - `templates/hello-orb-flow.html` — 文本绕排移动球体（绕障碍物重排模式）
   - `templates/donut-orbit.html` — 高级示例：测量过的 ASCII 标志障碍物、可拖拽线框球体/立方体、变形形状场、可选择的 DOM 文本以及仅开发模式的控制
   - 使用 `write_file` 将新 `.html` 写入 `/tmp/` 或用户的工作区。
3. **将语料库替换为与需求相关的内容**。真实散文，10-100 句，不要用 lorem ipsum。
4. **调整美学**——字体、调色板、构图、交互。这是核心工作，不要跳过。
5. **本地验证**：
   ```sh
   cd <dir-with-html> && python3 -m http.server 8765
   # 然后打开 http://localhost:8765/<file>.html
   ```
6. **检查控制台**——如果 `prepareWithSegments` 使用了错误的字体字符串，pretext 会抛出错误；`Intl.Segmenter` 在所有现代浏览器中可用。
7. **向用户展示文件路径**，而不仅仅是代码——他们需要打开它。
<a id="performance-notes"></a>
## 性能说明

- `prepare()` / `prepareWithSegments()` 是开销较大的调用。每个文本+字体组合**只调用一次**，然后缓存 handle。
- 调整大小时，只重新运行 `layout()` / `layoutWithLines()` —— 不要重新 prepare。
- 对于每帧动画，如果文本不变但几何变化，在紧密循环中使用 `layoutNextLineRange` 对于正常长度的段落来说，在 60fps 下每帧执行是足够轻量的。
- 当每帧渲染 ASCII 蒙版时，保留一个单元格缓冲区（`Uint8Array`/类型数组），从单元格或投影几何中导出每行测量的障碍物跨度，合并跨度，然后在绘制文本之前将这些跨度送入 `layoutNextLineRange`。
- 保持视觉动画和布局动画耦合。如果球体变形为立方体，使用相同的值对渲染的单元格缓冲区和障碍物跨度进行补间；否则演示看起来像是贴上去的，而不是物理重新流动。
- 对于淡入淡出，优先使用图层不透明度，而不是改变字形强度或障碍物尺度。将暂时的 ASCII 精灵放在自己的画布上，使用 CSS/GSAP 不透明度淡出画布，这样几何体看起来不会缩小。
- 画布 `ctx.font` 设置出奇地慢；如果字体不变，每帧**只设置一次**，而不是每次 `fillText` 调用都设置。

<a id="common-pitfalls"></a>
## 常见陷阱

1. **CSS/canvas 字体字符串漂移。** `ctx.font = "16px Inter"` 测量正常，但 CSS 设置 `font-family: Inter, sans-serif; font-size: 16px`。如果 Inter 加载成功则没问题。但如果 Inter 404，CSS 回退到 sans-serif，测量结果漂移 5-20%。始终 `preload` 字体或使用 web-safe 字体族。

2. **在动画循环中重复 prepare。** 只有 `layout*` 是轻量的。每帧都重新调用 `prepare` 会严重影响性能。将准备好的 handle 保存在模块作用域中。

3. **忘记使用 `Intl.Segmenter` 进行字素分割。** Emoji、组合标记、中日韩文字 —— `"é".split("")` 会得到两个字符。在采样单个可见字形时，使用 `new Intl.Segmenter(undefined, { granularity: "grapheme" })`。

4. **使用 `break: 'never'` 的芯片未设置 `extraWidth`。** 在 `rich-inline` 中，如果对原子芯片/提及使用 `break: 'never'`，还必须为胶囊内边距提供 `extraWidth` —— 否则芯片边框会溢出容器。

5. **从 `unpkg` 使用仅 TypeScript 入口的 `@chenglou/pretext`。** 改用 `esm.sh` —— 它会自动将 TS 导出编译为浏览器可用的 ESM。`unpkg` 会返回 404 或原始 TS。

6. **等宽字体回退默默破坏了整个要点。** 如果用户看到等宽效果输出，通常是因为 CSS `font-family` 回退到了 `monospace`。通过 DevTools 验证实际渲染的字体。

7. **在围绕形状流动时跳过行 vs 调整宽度。** 如果当前行的通道太窄无法容纳一行，*跳过该行*（`y += lineHeight; continue;`），而不是传递一个很小的 maxWidth 给 `layoutNextLineRange` —— pretext 会返回单字素行，看起来破碎。

8. **交付一个冷淡的演示。** 默认的首次绘制看起来像是教程级别。添加：暗角、细微扫描线、空闲自动运动、一个精心选择的交互响应（拖拽、悬停、滚动、点击）。缺少这些，“酷的 pretext 演示”就会变成“实习生复现 README”。
<a id="verification-checklist"></a>
## 验证清单

- [ ] 演示是一个独立的 `.html` 文件 — 双击或通过 `python3 -m http.server` 即可打开
- [ ] 通过 `esm.sh` 导入 `@chenglou/pretext`，并固定版本号
- [ ] 语料库是真实的散文，不是 lorem ipsum，且与演示的概念匹配
- [ ] 传递给 `prepare` 的字体字符串与 CSS 字体完全一致
- [ ] `prepare()` / `prepareWithSegments()` 只调用一次，而不是每帧调用
- [ ] 深色背景 + 经过考量的调色板 — 不是默认的白色画布
- [ ] 至少一个交互式响应（拖拽 / 悬停 / 滚动 / 点击）或空闲时的自动动画
- [ ] 已通过 `python3 -m http.server` 在本地测试，并确认无控制台错误
- [ ] 在中端笔记本电脑上达到 60fps（或记录了优雅降级方案）
- [ ] 一个用户未要求的“额外加分”细节

<a id="reference-community-demos"></a>
## 参考：社区演示

克隆这些项目以获取灵感 / 模式（均为 MIT 许可，链接自 [pretext.cool](https://www.pretext.cool/)）：

- **Pretext Breaker** — 用单词砖块打砖块 — `github.com/rinesh/pretext-breaker`
- **Tetris × Pretext** — `github.com/shinichimochizuki/tetris-pretext`
- **Dragon animation** — `github.com/qtakmalay/PreTextExperiments`
- **Somnai editorial engine** — `github.com/somnai-dreams/pretext-demos`
- **Bad Apple!! ASCII** — `github.com/frmlinn/bad-apple-pretext`
- **Drag-sprite reflow** — `github.com/dokobot/pretext-demo`
- **Alarmy editorial clock** — `github.com/SmisLee/alarmy-pretext-demo`

官方游乐场：[chenglou.me/pretext](https://chenglou.me/pretext/) — 手风琴、气泡、动态布局、编辑引擎、对齐比较、瀑布流、Markdown 聊天、富笔记。
