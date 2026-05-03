---
title: "Sketch — 一次性 HTML 线框图：2-3 个设计变体用于对比"
sidebar_label: "Sketch"
description: "一次性 HTML 线框图：2-3 个设计变体用于对比"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑原始的 SKILL.md，而非本页面。 */}

# Sketch {#sketch}

一次性 HTML 线框图：2-3 个设计变体用于对比。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/sketch` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent（改编自 gsd-build/get-shit-done） |
| 许可协议 | MIT |
| 标签 | `sketch`, `mockup`, `设计`, `ui`, `原型`, `html`, `变体`, `探索`, `线框图`, `对比` |
| 相关技能 | [`spike`](/user-guide/skills/bundled/software-development/software-development-spike), [`claude-design`](/user-guide/skills/bundled/creative/creative-claude-design), [`popular-web-designs`](/user-guide/skills/bundled/creative/creative-popular-web-designs), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw) |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是当此技能触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="sketch"></a>
# Sketch

当用户想要**在确定方向之前先看看设计方向**时使用此技能——以一次性 HTML 线框图的形式探索 UI/UX 想法。其目的在于生成 2-3 个交互式变体，让用户可以并排比较视觉方向，而不是生成可交付的代码。

在用户说出类似“画个这个屏幕的草图”、“让我看看 X 大概长什么样”、“比较布局 A 和 B”、“给我这个 UI 的 2-3 个版本”、“让我看一些变体”、“在开始构建之前先画个线框图”等话语时加载此技能。

## 何时不应使用此技能 {#when-not-to-use-this}

- 用户想要一个生产级组件——请使用 `claude-design` 或直接构建
- 用户想要一个精致的一次性 HTML 成果（落地页、演示文稿）——请使用 `claude-design`
- 用户想要一个图表——请使用 `excalidraw`、`architecture-diagram`
- 设计已经确定——直接构建即可

## 如果用户安装了完整的 GSD 系统 {#if-the-user-has-the-full-gsd-system-installed}

如果 `gsd-sketch` 作为同级技能出现（通过 `npx get-shit-done-cc --hermes` 安装），请优先使用 **`gsd-sketch`** 来完成完整工作流：持久化的 `.planning/sketches/` 目录（含 MANIFEST）、前沿模式分析、跨历史草稿的一致性审计，以及与 GSD 其余部分的集成。本技能是轻量级的独立版本——无需状态机制的一次性草稿。

## 核心方法 {#core-method}

```
输入  →  变体  →  正面交锋  →  选出赢家（或迭代）
```

### 1. 输入（如果用户已经提供了足够信息，可跳过） {#1-intake-skip-if-the-user-already-gave-you-enough}

在生成变体之前，需要获取三件事——一次只问一个问题，不要一股脑全问：

1. **感觉。** “这个界面应该给人什么感觉？形容词、情绪、某种氛围。” —— “平静、编辑风、像 Linear 那样” 比 “简约” 更有参考价值。
2. **参考。** “有哪些应用、网站或产品能捕捉到你想象中的感觉？” —— 具体参考比抽象描述更有效。
3. **核心操作。** “用户在这个屏幕上做的最重要的一件事是什么？” —— 所有变体都应该很好地服务于这一点；如果不能，那就只是装饰。
在每个问题之前简要反思上一个答案。如果用户已经一次性给出了全部三个答案，则直接跳到变体部分。

### 2. 变体（2-3个，不要1个，很少需要4个以上） {#2-variants-2-3-never-1-rarely-4}

一次性生成 **2-3 个变体**。每个变体都是一个完整的、独立的 HTML 文件。不要描述变体——直接构建它们。关键在于对比。

每个变体应采取**不同的设计立场**，而不是不同的像素值。三个好的变体轴：

- **密度：** 紧凑 / 通透 / 超密集（选取两个对比极端）
- **重点：** 内容优先 / 操作优先 / 工具优先
- **美学：** 编辑风格 / 实用主义 / 趣味性
- **布局：** 单栏 / 侧边栏 / 分屏
- **基础：** 卡片式 / 纯内容 / 文档风格

选取一个轴并从中展开。两个仅在强调色上不同的变体是浪费精力——用户无法区分它们。

**变体命名：** 描述立场，而不是编号。

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

### 3. 让它们成为真正的 HTML {#3-make-them-real-html}

每个变体是一个**独立的 HTML 文件**：

- 内联 `&lt;style&gt;` — 无需构建步骤，无需外部 CSS
- 系统字体或通过 `&lt;link&gt;` 引入一个 Google Font
- 通过 CDN 使用 Tailwind（`&lt;script src="https://cdn.tailwindcss.com"&gt;</script>`）是可以的
- 真实的假内容——真实的句子、真实的名字，而不是“Lorem ipsum”
- **可交互**：链接可点击，悬停效果真实，至少有一个状态切换（打开/关闭、筛选、切换）。一个冻结的静态图像比一个粗糙的动画更糟糕。

在浏览器中打开它。如果看起来有问题，在展示给用户之前修复它。

**视觉上验证变体——使用 Hermes 的浏览器工具。** 不要只是编写 HTML 并希望它能渲染；加载每个变体并查看它：

```
browser_navigate(url="file:///absolute/path/to/sketches/001-calm-editorial/index.html")
browser_vision(question="这个布局看起来干净可读吗？有没有可见的 bug（文本重叠、未样式化的元素、损坏的图片）？")
```

`browser_vision` 返回页面上实际内容的 AI 描述以及截图路径——能捕捉到纯源码检查遗漏的布局 bug（例如字体导入静默失败、flex 容器折叠）。修复并重新导航，直到每个变体看起来正确。

**默认 CSS 重置 + 系统字体栈** 用于快速启动：

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

### 4. 变体 README {#4-variant-readme}

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
- 强项：...
- 弱项：...

### 最佳适用场景
- 该变体实际服务的用户或用例类型
```
### 5. 横向对比 {#5-head-to-head}

所有变体构建完成后，将它们作为对比展示出来。不要只是罗列——要给出**有观点的评价**：

```markdown
## 首页的三种方案

| 维度 | 平静编辑风 | 实用密集风 | 活泼分栏风 |
|-----------|----------------|-------------------|---------------|
| 密度   | 低            | 高              | 中等        |
| 主要操作可见性 | 低 | 高 | 中等 |
| 可扫描性 | 高 | 中等 | 低 |
| 感觉 | 平静、可信 | 锐利、工具感 | 亲切、有活力 |

**我的看法：** 实用密集风适合高级用户，平静编辑风适合内容优先的受众。活泼分栏风最弱——试图兼顾两者却两头不讨好。
```

让用户选择一个优胜方案，或者将两个方案合并成一个混合方案，也可以要求再来一轮。

## 主题化（当项目有视觉标识时） {#theming-when-the-project-has-a-visual-identity}

如果用户已有现有主题（颜色、字体、令牌），将共享令牌放在 `sketches/themes/tokens.css` 中，并在每个变体中用 `@import` 引入。保持令牌最小化：

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

不要对一次性草图过度令牌化——三种颜色和一种字体通常就足够了。

## 交互性要求 {#interactivity-bar}

当用户能够做到以下几点时，草图才算具有足够的交互性：

1. **点击一个主要操作**，并且能看到可见的变化（状态变化、弹窗、提示、导航模拟）
2. **看到一次有意义的状态转换**（过滤列表、切换模式、打开/关闭面板）
3. **悬停在可识别的交互元素上**（按钮、行、标签页）

超过这些就是过度工程化一次性草图。少于这些就只是一张截图。

## 前沿模式（选择下一步要画什么） {#frontier-mode-picking-what-to-sketch-next}

如果草图已经存在，用户问“接下来应该画什么？”：

- **一致性缺口**——来自不同草图的两种优胜变体做出了独立选择，但尚未组合在一起
- **未草图的页面**——被引用但从未探索过
- **状态覆盖**——快乐路径已草图，但空状态/加载状态/错误状态/1000条数据状态未覆盖
- **响应式缺口**——在某个视口下已验证，但在移动端/超宽屏上是否仍然成立？
- **交互模式**——静态布局已存在，但过渡、拖拽、滚动行为尚未实现

提出 2-4 个命名的候选方案。让用户选择。

## 输出 {#output}

- 在仓库根目录创建 `sketches/`（如果用户使用 GSD 约定，则创建 `.planning/sketches/`）
- 每个变体一个子目录：`NNN-立场名称/index.html` + `README.md`
- 告诉用户如何打开它们：macOS 上用 `open sketches/001-calm-editorial/index.html`，Linux 上用 `xdg-open`，Windows 上用 `start`
- 保持变体可丢弃——如果你觉得需要保留的草图，应该提升为真正的项目代码，而不是作为资产来整理

**一个变体的典型工具序列：**

```
terminal("mkdir -p sketches/001-calm-editorial")
write_file("sketches/001-calm-editorial/index.html", "<!doctype html>...")
write_file("sketches/001-calm-editorial/README.md", "## 变体：平静编辑风\n...")
browser_navigate(url="file://$(pwd)/sketches/001-calm-editorial/index.html")
browser_vision(question="这个看起来怎么样？有没有明显的布局问题？")
```
对每个变体重复上述步骤，然后呈现对比表格。

## 归属说明 {#attribution}

改编自 GSD（Get Shit Done）项目的 `/gsd-sketch` 工作流 — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))。完整的 GSD 系统包含持久化草图状态、主题/变体模式参考以及一致性审计工作流；使用 `npx get-shit-done-cc --hermes --global` 安装。
