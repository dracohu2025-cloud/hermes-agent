---
title: "Pretext"
sidebar_label: "Pretext"
description: "在构建创意浏览器演示时使用 @chenglou/pretext — 无 DOM 文本布局，适用于 ASCII 艺术、绕障碍物的排版流、文本即几何的游戏、动态排版以及文本驱动的生成艺术。默认生成单文件 HTML 演示。"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Pretext {#pretext}

在构建创意浏览器演示时使用 @chenglou/pretext — 无 DOM 文本布局，适用于 ASCII 艺术、绕障碍物的排版流、文本即几何的游戏、动态排版以及文本驱动的生成艺术。默认生成单文件 HTML 演示。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/pretext` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `creative-coding`, `typography`, `pretext`, `ascii-art`, `canvas`, `generative`, `text-layout`, `kinetic-typography` |
| 相关技能 | [`p5js`](/user-guide/skills/bundled/creative/creative-p5js), [`claude-design`](/user-guide/skills/bundled/creative/creative-claude-design), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw), [`architecture-diagram`](/user-guide/skills/bundled/creative/creative-architecture-diagram) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Pretext 创意演示 {#pretext-creative-demos}

## 概述 {#overview}

[`@chenglou/pretext`](https://github.com/chenglou/pretext) 是一个 15KB 零依赖的 TypeScript 库，由 Cheng Lou（React 核心成员、ReasonML、Midjourney）开发，用于**无 DOM 的多行文本测量与布局**。它只做一件事：给定 `(text, font, width)`，返回换行、每行宽度、每个字素的位置以及总高度——全部通过 canvas 测量，无需重排。

听起来像是底层工具。但并非如此。因为它快速且几何化，所以它是一个**创意原语**：你可以让段落以 60fps 的速度围绕移动的精灵重排，构建关卡几何体由真实单词构成的游戏，通过散文驱动 ASCII 标志，将文本粉碎成具有精确字素起始位置的粒子，或者在不触发 `getBoundingClientRect` 的情况下打包紧凑的多行 UI。

此技能的存在是为了让 Hermes 能够用它制作**酷炫的演示**——就是人们发到 X 上的那种。请参阅 `pretext.cool` 和 `chenglou.me/pretext` 查看社区演示合集。

## 何时使用 {#when-to-use}

当用户要求以下内容时使用：
- “一个 pretext 演示” / “酷炫的 pretext 东西” / “文本即 X”
- 文本围绕移动形状流动（英雄区、编辑布局、动画长页面）
- 使用**真实单词或散文**的 ASCII 艺术效果，而非等宽光栅
- 游戏场地/障碍物/砖块由文本构成的游戏（字母版俄罗斯方块、散文版打砖块）
- 具有逐字形物理效果的动态排版（粉碎、散开、聚集、流动）
- 排版生成艺术，尤其是非拉丁文字或混合文字
- 多行“紧凑”UI（能容纳文本的最小容器宽度）
- 任何需要在渲染*之前*知道换行的情况

不要用于：
- 静态 SVG/HTML 页面，CSS 已解决布局问题——直接用 CSS
- 富文本编辑器、通用内联格式化引擎（pretext 有意保持狭窄）
- 图像转文本（使用 `ascii-art` / `ascii-video` 技能）
- 纯 canvas 生成艺术，没有文本角色——使用 `p5js`
## Creative Standard {#creative-standard}

这是在浏览器中呈现的视觉艺术。Pretext 返回数字；**你**负责绘制图形。

- **不要交付一个“hello world”演示。** `hello-orb-flow.html` 模板只是*起点*。每个交付的演示都必须包含有意的色彩、动态、构图，以及一个用户没有要求但会欣赏的视觉细节。
- **深色背景、温暖核心、考究的配色。** 经典的琥珀色背景配黑色文字（CRT/终端）可行，但冷白配炭灰（编辑风格）或低饱和粉彩（risograph）也都可以。选一种配色并坚持使用。
- **比例字体是重点。** Pretext 的整体氛围是“非等宽”——尽情发挥。使用 Iowan Old Style、Inter、JetBrains Mono、Helvetica Neue 或可变字体。永远不要用无衬线默认字体。
- **真实的文本/内容，而不是 lorem ipsum。** 语料应该有意义。短篇宣言、诗歌、真实代码、发现的文本、库本身的 README —— 永远不要用 `lorem ipsum`。
- **首次渲染即完美。** 没有加载状态，没有空白帧。演示必须一打开就看起来可以交付。

## Stack {#stack}

每个演示为一个独立的 HTML 文件，无需构建步骤。

| 层 | 工具 | 用途 |
|-------|------|---------|
| 核心 | 通过 `esm.sh` CDN 提供的 `@chenglou/pretext` | 文本测量 + 行布局 |
| 渲染 | HTML5 Canvas 2D | 字形渲染、逐帧合成 |
| 分段 | `Intl.Segmenter`（内置） | 用于表情符号/中日韩/组合标记的字素分割 |
| 交互 | 原始 DOM 事件 | 鼠标/触摸/滚轮 — 无框架 |

```html
<script type="module">
import {
  prepare, layout,                   // 用例 1：简单高度
  prepareWithSegments, layoutWithLines,  // 用例 2a：固定宽度行
  layoutNextLineRange, materializeLineRange, // 用例 2b：流式/可变宽度
  measureLineStats, walkLineRanges,  // 无需字符串分配的统计
} from "https://esm.sh/@chenglou/pretext@0.0.6";
</script>
```

固定版本号。写作时为 `@0.0.6` —— 如果演示行为异常，请查看 [npm](https://www.npmjs.com/package/@chenglou/pretext) 获取最新版本。

## 两种用例 {#the-two-use-cases}

几乎所有情况都归结为以下两种模式之一。学会这两种。

### 用例 1 — 测量，然后用 CSS/DOM 渲染 {#use-case-1-measure-then-render-with-css-dom}

```js
const prepared = prepare(text, "16px Inter");
const { height, lineCount } = layout(prepared, 320, 20);
```

你仍然让浏览器绘制文本。Pretext 只是告诉你给定宽度下盒子会有多高，**无需**读取 DOM。适用于：
- 包含换行文本的虚拟列表行
- 精确卡片高度的瀑布流
- “这个标签能放下吗？”开发时检查
- 防止远程文本加载时的布局偏移

**确保 `font` 和 `letterSpacing` 与你的 CSS 完全同步。** Canvas 的 `ctx.font` 格式（例如 `"16px Inter"`、`"500 17px 'JetBrains Mono'"`）必须与渲染的 CSS 匹配，否则测量会偏离。

### 用例 2 — 自己测量*并*渲染 {#use-case-2-measure-and-render-yourself}

```js
const prepared = prepareWithSegments(text, FONT);
const { lines } = layoutWithLines(prepared, 320, 26);
for (let i = 0; i < lines.length; i++) {
  ctx.fillText(lines[i].text, 0, i * 26);
}
```
这就是创意工作的核心所在。你掌控绘图，因此你可以：
- 渲染到 canvas、SVG、WebGL 或任何坐标系
- 替换每个字形的变换（旋转、抖动、缩放、透明度）
- 将线条元数据（宽度、字素位置）用作几何数据

对于**每行可变宽度**的流动（文本环绕形状、文本在环形带内、文本在非矩形列中）：

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

这是整个库中最重要的模式。它解锁了“文本围绕拖拽精灵流动”的能力——那个在 X 上爆火的演示。

### 值得了解的辅助工具 {#helpers-worth-knowing}

- `measureLineStats(prepared, maxWidth)` → `{ lineCount, maxLineWidth }` — 最宽的行，即多行收缩包裹宽度。
- `walkLineRanges(prepared, maxWidth, callback)` — 迭代行而不分配字符串。当你不需要字符时，用于对字素进行统计/物理计算。
- `@chenglou/pretext/rich-inline` — 相同的系统，但用于混合字体/标签/提及的段落。从子路径导入。

## 演示配方模式 {#demo-recipe-patterns}

社区语料库（参见 `references/patterns.md`）汇聚成少数几个强模式。选择一个并即兴发挥——除非被要求，否则不要发明新类别。

| 模式 | 关键 API | 示例想法 |
|---|---|---|
| **绕障碍物重排** | `layoutNextLineRange` + 每行宽度函数 | 编辑段落，围绕拖拽光标精灵展开 |
| **文本即几何游戏** | `layoutWithLines` + 每行碰撞矩形 | 打砖块游戏，每个砖块是一个测量过的单词 |
| **破碎/粒子** | `walkLineRanges` → 每个字素 (x,y) → 物理 | 点击时句子爆炸成字母 |
| **ASCII 障碍排版** | `layoutNextLineRange` + 测量过的每行障碍跨度 | 位图 ASCII 标志、形状变形、可拖拽线框物体，使文本围绕其实际几何形状展开 |
| **编辑多栏** | 每栏 `layoutNextLineRange` + 共享光标 | 带拉引文的动画杂志跨页 |
| **动态文字** | `layoutWithLines` + 每行随时间变换 | 星球大战滚动、波浪、弹跳、故障 |
| **多行收缩包裹** | `measureLineStats` | 自动适应最紧凑容器的引用卡片 |

参见 `templates/donut-orbit.html` 和 `templates/hello-orb-flow.html` 获取可运行的单个文件入门示例。

## 工作流程 {#workflow}

1. **从上方表格中选取一个模式**，基于用户的简要说明。
2. **从模板开始**：
   - `templates/hello-orb-flow.html` — 文本围绕移动球体重排（绕障碍物重排模式）
   - `templates/donut-orbit.html` — 高级示例：测量过的 ASCII 标志障碍物、可拖拽线框球体/立方体、变形形状场、可选择的 DOM 文本以及仅限开发者的控制
   - 使用 `write_file` 写入 `/tmp/` 或用户工作区中的新 `.html` 文件。
3. **替换语料库**为与简要说明相关的实际内容。真实散文，10-100 句，不要用 lorem。
4. **调整美学**——字体、调色板、构图、交互。这是核心工作，不要跳过。
5. **本地验证**：
   ```sh
   cd <包含html的目录> && python3 -m http.server 8765
   # 然后打开 http://localhost:8765/<文件名>.html
   ```
6. **检查控制台**——如果 `prepareWithSegments` 使用了错误的字体字符串，pretext 会抛出错误；`Intl.Segmenter` 在所有现代浏览器中可用。
7. **向用户展示文件路径**，而不仅仅是代码——他们想要打开它。
## 性能说明 {#performance-notes}

- `prepare()` / `prepareWithSegments()` 是开销较大的调用。每个文本+字体对**只调用一次**，并缓存返回的句柄。
- 调整大小时，只需重新运行 `layout()` / `layoutWithLines()` —— 永远不要重新 prepare。
- 对于每帧动画，如果文本不变但几何形状变化，在紧密循环中使用 `layoutNextLineRange` 对于正常长度的段落来说足够轻量，可以在 60fps 下每帧执行。
- 当每帧渲染 ASCII 遮罩时，保留一个单元格缓冲区（`Uint8Array`/类型数组），从单元格或投影几何中推导出每行的障碍物跨度，合并跨度，然后在绘制文本前将这些跨度输入 `layoutNextLineRange`。
- 保持视觉动画和布局动画耦合。如果一个球体变形为立方体，使用相同的值对渲染的单元格缓冲区和障碍物跨度进行补间；否则演示看起来像是贴上去的，而不是物理重排的。
- 对于淡入淡出，优先使用图层透明度，而不是改变字形强度或障碍物缩放。将瞬态 ASCII 精灵放在自己的画布上，用 CSS/GSAP 透明度淡出画布，这样几何形状就不会显得缩小。
- Canvas `ctx.font` 设置出奇地慢；如果字体不变，**每帧只设置一次**，而不是每次 `fillText` 调用都设置。

## 常见陷阱 {#common-pitfalls}

1. **CSS/canvas 字体字符串不一致。** `ctx.font = "16px Inter"` 测量时使用，但 CSS 中写的是 `font-family: Inter, sans-serif; font-size: 16px`。如果 Inter 加载成功则没问题。但如果 Inter 返回 404，CSS 会回退到 sans-serif，测量结果会偏差 5-20%。始终 `preload` 字体或使用 web-safe 字体族。

2. **在动画循环内重新 prepare。** 只有 `layout*` 是轻量的。每帧都重新调用 `prepare` 会严重影响性能。将准备好的句柄保存在模块作用域中。

3. **忘记使用 `Intl.Segmenter` 进行字素分割。** 表情符号、组合标记、中日韩文字 —— `"é".split("")` 会得到两个字符。在采样单个可见字形时，请使用 `new Intl.Segmenter(undefined, { granularity: "grapheme" })`。

4. **`break: 'never'` 的 chip 没有 `extraWidth`。** 在 `rich-inline` 中，如果对原子 chip/mention 使用 `break: 'never'`，则必须同时为 pill 内边距提供 `extraWidth` —— 否则 chip 的边框会溢出容器。

5. **从 `unpkg` 使用 `@chenglou/pretext`，但入口是 TypeScript 专用。** 请使用 `esm.sh` —— 它会自动将 TS 导出编译为浏览器可用的 ESM。`unpkg` 会返回 404 或提供原始 TS。

6. **等宽字体回退悄悄毁掉整个效果。** 用户看到类似等宽字体的输出时，通常是因为 CSS `font-family` 回退到了 `monospace`。通过 DevTools 验证实际渲染的字体。

7. **绕形状流动时跳过行 vs 调整宽度。** 如果当前行的通道太窄无法容纳一行，*跳过该行*（`y += lineHeight; continue;`），而不是将很小的 maxWidth 传递给 `layoutNextLineRange` —— pretext 会返回单字素行，看起来像断裂了。

8. **发布一个冷冰冰的演示。** 默认的首次绘制看起来像教程级别。请添加：暗角、微弱的扫描线、空闲自动运动、一个精心选择的交互响应（拖拽、悬停、滚动、点击）。没有这些，“酷炫的 pretext 演示”就会沦为“实习生复现 README”。
## 验证清单 {#verification-checklist}

- [ ] 演示是一个独立的 `.html` 文件——双击或通过 `python3 -m http.server` 即可打开
- [ ] `@chenglou/pretext` 通过 `esm.sh` 导入，并固定了版本号
- [ ] 语料库是真实的散文，不是 lorem ipsum，并且与演示的概念相匹配
- [ ] 传递给 `prepare` 的字体字符串与 CSS 字体完全一致
- [ ] `prepare()` / `prepareWithSegments()` 只调用一次，而不是每帧调用
- [ ] 深色背景 + 精心设计的调色板——不是默认的白色画布
- [ ] 至少一种交互式响应（拖拽 / 悬停 / 滚动 / 点击）或空闲时的自动动画
- [ ] 已通过 `python3 -m http.server` 在本地测试，并确认无控制台错误
- [ ] 在中端笔记本电脑上达到 60fps（或记录了优雅降级方案）
- [ ] 一个用户未要求的“额外加分”细节

## 参考：社区演示 {#reference-community-demos}

克隆这些以获取灵感 / 模式（均为 MIT 许可，链接自 [pretext.cool](https://www.pretext.cool/)）：

- **Pretext Breaker** — 用单词砖块玩打砖块 — `github.com/rinesh/pretext-breaker`
- **俄罗斯方块 × Pretext** — `github.com/shinichimochizuki/tetris-pretext`
- **龙动画** — `github.com/qtakmalay/PreTextExperiments`
- **Somnai 编辑引擎** — `github.com/somnai-dreams/pretext-demos`
- **Bad Apple!! ASCII** — `github.com/frmlinn/bad-apple-pretext`
- **拖拽精灵重排** — `github.com/dokobot/pretext-demo`
- **Alarmy 编辑时钟** — `github.com/SmisLee/alarmy-pretext-demo`

官方游乐场：[chenglou.me/pretext](https://chenglou.me/pretext/) — 手风琴、气泡、动态布局、编辑引擎、对齐比较、瀑布流、Markdown 聊天、富笔记。
