---
title: "Sketch — 一次性 HTML 原型：2-3 个设计变体供比较"
sidebar_label: "Sketch"
description: "一次性 HTML 原型：2-3 个设计变体供比较"
---

{/* 本页由脚本从技能的 SKILL.md 自动生成（website/scripts/generate-skill-docs.py）。请编辑源文件 SKILL.md，而不是本页。 */}

<a id="sketch"></a>
# Sketch

一次性 HTML 原型：2-3 个设计变体供比较。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/sketch` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent（改编自 gsd-build/get-shit-done） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `sketch`, `mockup`, `design`, `ui`, `prototype`, `html`, `variants`, `exploration`, `wireframe`, `comparison` |
| 相关技能 | [`spike`](/user-guide/skills/bundled/software-development/software-development-spike), [`claude-design`](/user-guide/skills/bundled/creative/creative-claude-design), [`popular-web-designs`](/user-guide/skills/bundled/creative/creative-popular-web-designs), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是在触发此技能时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Sketch

当用户想要**在确定一个设计方向之前先“看一看”** 时使用此技能——探索 UI/UX 想法，制作可丢弃的 HTML 原型。关键在于生成 2-3 个可交互的变体，让用户能并排比较视觉方向，而不是生成可交付的代码。

当用户说出类似“草图这个屏幕”、“展示一下 X 可能的样子”、“比较布局 A 和 B”、“给我这个 UI 的 2-3 个方案”、“让我看看几个变体”、“在我开始做之前先原型搞一下”时，加载此技能。

<a id="when-not-to-use-this"></a>
## 什么时候不该用

- 用户想要一个生产级组件——使用 `claude-design` 或正确构建
- 用户想要一个打磨好的单次 HTML 产物（落地页、演示文稿）——使用 `claude-design`
- 用户想要一个图表——使用 `excalidraw`、`architecture-diagram`
- 设计已经确定——直接构建即可

<a id="if-the-user-has-the-full-gsd-system-installed"></a>
## 如果用户安装了完整的 GSD 系统

如果 `gsd-sketch` 作为兄弟技能出现（通过 `npx get-shit-done-cc --hermes` 安装），建议使用 **`gsd-sketch`** 以获得完整工作流：持久的 `.planning/sketches/` 目录包含 MANIFEST、前沿模式分析、跨过去草图的一致性审计，以及与 GSD 其他部分的集成。本技能是轻量级的独立版本——不含状态机制的一次性草图。

<a id="core-method"></a>
## 核心方法

```
接收  →  变体  →  正面交锋  →  选出优胜（或迭代）
```

<a id="1-intake-skip-if-the-user-already-gave-you-enough"></a>
### 1. 接收（如果用户已经提供足够信息可跳过）

在生成变体之前，获取三样东西——一次只问一个问题，不要一次性全问：

1. **感觉**。“这个应该给人什么感觉？形容词、情绪、某种氛围。” —— *“平静、编辑感、像 Linear 那样”* 比 *“极简”* 更有用。
2. **参考**。“有哪些应用、网站或产品捕捉到了你想象中的感觉？” —— 真实的参考比抽象描述更有用。
3. **核心操作**。“用户在这个屏幕上做的唯一最重要的事情是什么？” —— 所有变体都应该很好地服务于这个操作；如果不这样，它们就只是装饰。
在每个问题之前简要反思每个答案。如果用户已经提前给出了全部三个答案，直接跳到变体部分。

<a id="2-variants-2-3-never-1-rarely-4"></a>
### 2. 变体（2-3个，不要1个，很少用4个以上）

一次性生成 **2-3 个变体**。每个变体是一个完整、独立的 HTML 文件。不要描述变体——而是构建它们。重点是进行对比。

每个变体应采用 **不同的设计立场**，而不是不同的像素值。三个好的变体轴：

- **密度：** 紧凑 / 透气 / 超密集（选择两个对比极）
- **重点：** 内容优先 / 操作优先 / 工具优先
- **美学：** 编辑风格 / 实用主义 / 有趣
- **布局：** 单栏 / 侧边栏 / 分屏
- **基础：** 卡片式 / 裸内容 / 文档风格

选择一个轴并从中拉开距离。仅强调色不同的两个变体是浪费精力——用户无法区分它们。

**变体命名：** 描述立场，而不是数字。

<!-- ascii-guard-ignore -->
```
sketches/
├── 001-calm-editorial/
│   ├── index.html
│   └── README.md
├── 001-utilitarian-dense/
│   ├── index.html
│   └── README.md
└── 001-playful-split/
    ├── index.html
    └── README.md
```
<!-- ascii-guard-ignore-end -->

<a id="3-make-them-real-html"></a>
### 3. 制作真正的 HTML

每个变体是一个 **单独自包含的 HTML 文件**：

- 内联 `&lt;style&gt;` — 无需构建步骤，无需外部 CSS
- 系统字体或通过 `&lt;link&gt;` 引用一个 Google Font
- 通过 CDN 使用 Tailwind（`&lt;script src="https://cdn.tailwindcss.com"&gt;</script>`）是可以的
- 真实的伪内容 — 实际句子、实际名称，不要用 "Lorem ipsum"
- **可交互的**：链接可点击，悬停有效，至少有一个状态转换（打开/关闭、过滤、切换）。一个冻结的静态图像比一个粗糙的动画更糟糕。

在浏览器中打开它。如果看起来有问题，在展示给用户之前修复它。

**视觉验证变体——使用 Hermes 的浏览器工具。** 不要只是编写 HTML 并希望它能渲染；加载每个变体并查看它：

```
browser_navigate(url="file:///absolute/path/to/sketches/001-calm-editorial/index.html")
browser_vision(question="Does this layout look clean and readable? Any visible bugs (overlapping text, unstyled elements, broken images)?")
```

`browser_vision` 返回页面上实际内容的 AI 描述以及截图路径——捕获纯源代码检查遗漏的布局错误（例如，静默失败的字体导入、折叠的 flex 容器）。修复并重新导航，直到每个变体看起来正确。

**默认 CSS reset + 系统字体栈**，以便快速启动：

```html
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #1a1a1a;
    background: #fafafa;
    line-height: 1.5;
  }
</style>
```

<a id="4-variant-readme"></a>
### 4. 变体 README

每个变体的 `README.md` 回答以下内容：

```markdown
## 变体：{立场名称}

### 设计立场
一句话描述驱动该变体的原则。

### 关键选择
- 布局：...
- 排版：...
- 颜色：...
- 交互：...

### 权衡
- 擅长：...
- 弱点：...

### 最适合
- 该变体实际服务的用户或用例类型
```
<a id="5-head-to-head"></a>
### 5. 逐项对比

所有变体完成后，将它们作为对比展示出来。不要仅仅是列出——要给出**有观点**的评价：

```markdown
## 首页的三种方案

| 维度           | 平静编辑风 | 实用密集风 | 活泼分栏风 |
|----------------|------------|------------|------------|
| 密度           | 低         | 高         | 中等       |
| 主操作可见性   | 低         | 高         | 中等       |
| 可扫读性       | 高         | 中等       | 低         |
| 感受           | 平静、可信 | 锐利、工具感 | 吸引人、有活力 |

**我的判断：** 实用密集风适合重度用户，平静编辑风适合内容优先的受众。活泼分栏风最弱——试图两者兼顾却哪个都没做好。
```

让用户选出一个最优方案，或者将两个融合成混合体，再或者要求再来一轮。

<a id="theming-when-the-project-has-a-visual-identity"></a>
## 主题化（当项目已有视觉风格时）

如果用户已有主题（颜色、字体、设计变量），将公共变量放在 `sketches/themes/tokens.css` 中，并在每个变体里通过 `@import` 引入。保持变量最小化：

```css
/* sketches/themes/tokens.css */
:root {
  --color-bg: #fafafa;
  --color-fg: #1a1a1a;
  --color-accent: #0066ff;
  --color-muted: #666;
  --radius: 8px;
  --font-display: "Inter", sans-serif;
  --font-body: -apple-system, BlinkMacSystemFont, sans-serif;
}
```

不要为一个用完即弃的草图过度设计变量——三种颜色和一种字体通常就够了。

<a id="interactivity-bar"></a>
## 交互度条

当用户能够做到以下三点时，草图才算具备足够的交互性：

1. **点击一个主要操作**后有可见变化（状态切换、弹窗、轻提示、导航模拟）
2. **能看到一个有意义的转场**（筛选列表、切换模式、打开/关闭面板）
3. **可以悬停在可识别控件上**（按钮、行、标签页）

超过这些就是过度工程化，低于这些就只是一张截图。

<a id="frontier-mode-picking-what-to-sketch-next"></a>
## 前沿模式（决定下一步画什么）

如果已经存在草图，用户问“接下来应该画什么”，这时要考虑：

- **一致性缺口**——来自不同草图的优胜变体，各自做了独立选择，还没有被组合在一起
- **未画界面**——被提及但没有探索过的页面
- **状态覆盖**——正常路径画了，但空状态/加载/错误/1000 条数据的状态还没画
- **响应式缺口**——在某个视口验证过，但在移动端/超宽屏上能否撑住？
- **交互模式**——已有静态布局，但动画、拖拽、滚动行为还没有

提出 2-4 个有命名的候选方案让用户选择。

<a id="output"></a>
## 输出

- 在仓库根目录创建 `sketches/`（如果用户使用 GSD 约定，则创建 `.planning/sketches/`）
- 每个变体一个子目录：`NNN-姿态名称/index.html` + `README.md`
- 告诉用户如何打开它们：macOS 上用 `open sketches/001-calm-editorial/index.html`，Linux 上用 `xdg-open`，Windows 上用 `start`
- 保持变体的一次性——如果你觉得某个草图需要珍藏，就应当提升为真正的项目代码，而不是作为资产被保留

**一个变体的典型工具流程：**

```
terminal("mkdir -p sketches/001-calm-editorial")
write_file("sketches/001-calm-editorial/index.html", "<!doctype html>...")
write_file("sketches/001-calm-editorial/README.md", "## 变体：平静编辑风\n...")
browser_navigate(url="file://$(pwd)/sketches/001-calm-editorial/index.html")
browser_vision(question="这个看起来如何？有没有明显的布局问题？")
```
对每个变体重复上述步骤，然后呈现对比表格。

<a id="attribution"></a>
## 出处

改编自 GSD（Get Shit Done）项目的 `/gsd-sketch` 工作流——MIT © 2025 Lex Christopherson（[gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)）。完整的 GSD 系统包含了持久化素描状态、主题/变体模式引用以及一致性审计工作流；使用 `npx get-shit-done-cc --hermes --global` 安装。
