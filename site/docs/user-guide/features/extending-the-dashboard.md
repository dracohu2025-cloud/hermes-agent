---
sidebar_position: 17
title: "扩展仪表盘"
description: "为 Hermes Web 仪表盘构建主题和插件——调色板、排版、布局、自定义标签页、外壳插槽、页面级插槽和后端 API 路由"
---

<a id="extending-the-dashboard"></a>
# 扩展仪表盘

Hermes Web 仪表盘（`hermes dashboard`）设计为无需派生代码库即可重新换肤和扩展。公开了三个层次：

1. **主题（Themes）** —— 用于重新绘制仪表盘调色板、排版、布局以及每个组件外观的 YAML 文件。将文件放入 `~/.hermes/dashboard-themes/` 目录后，它就会出现在主题切换器中。
2. **UI 插件（UI plugins）** —— 一个目录，包含 `manifest.json` 加上一个 JavaScript 包（bundle）。该包可以注册一个标签页、替换内置页面、通过页面级插槽扩展现有页面，或将组件注入到命名的外壳插槽中。
3. **后端插件（Backend plugins）** —— 该插件目录内的一个 Python 文件，暴露了一个 FastAPI `router`；路由挂载在 `/api/plugins/&lt;name&gt;/` 下，并从插件 UI 调用。

以上三者都是**运行时即插即用**的：无需克隆仓库、无需运行 `npm run build`、无需修改仪表盘源码。本页面是这三种方式的权威参考。

如果你只想使用仪表盘，请参阅 [Web 仪表盘](./web-dashboard)。如果你想重新换肤终端 CLI（而非 Web 仪表盘），请参阅 [外观与主题](./skins) —— CLI 皮肤系统与仪表盘主题无关。
:::note 各组件如何搭配
<a id="how-the-pieces-compose"></a>
主题和插件相互独立但协同工作。主题可以独立使用（仅需要一个 YAML 文件）。插件也可以独立使用（仅提供一个标签页）。两者结合可以让你构建完整的视觉改造，并附带自定义 HUD——附带的 `strike-freedom-cockpit` 示例正是如此。参见 [组合主题 + 插件示例](#combined-theme--plugin-demo)。
:::

---

<a id="table-of-contents"></a>
## 目录

- [主题](#themes)
  - [快速上手——你的第一个主题](#quick-start--your-first-theme)
  - [调色板、字体排印、布局](#palette-typography-layout)
  - [布局变体](#layout-variants)
  - [主题资源（通过 CSS 变量使用图片）](#theme-assets-images-as-css-vars)
  - [组件边框覆盖](#component-chrome-overrides)
  - [颜色覆盖](#color-overrides)
  - [原始 `customCSS`](#raw-customcss)
  - [内置主题](#built-in-themes)
  - [完整主题 YAML 参考](#full-theme-yaml-reference)
- [插件](#plugins)
  - [快速上手——你的第一个插件](#quick-start--your-first-plugin)
  - [目录结构](#directory-layout)
  - [清单参考](#manifest-reference)
  - [插件 SDK](#the-plugin-sdk)
  - [Shell 插槽](#shell-slots)
  - [替换内置页面（`tab.override`）](#replacing-built-in-pages-taboverride)
  - [增强内置页面（页面级插槽）](#augmenting-built-in-pages-page-scoped-slots)
  - [纯插槽插件（`tab.hidden`）](#slot-only-plugins-tabhidden)
  - [后端 API 路由](#backend-api-routes)
  - [每个插件的自定义 CSS](#custom-css-per-plugin)
  - [插件发现与重载](#plugin-discovery--reload)
- [组合主题 + 插件示例](#combined-theme--plugin-demo)
- [API 参考](#api-reference)
- [故障排除](#troubleshooting)
---

<a id="themes"></a>
## 主题

主题是存储在 `~/.hermes/dashboard-themes/` 目录下的 YAML 文件。文件名无关紧要（系统使用的是主题的 `name:` 字段），但惯例是命名为 `<名称>.yaml`。每个字段都是可选的——缺失的键会回退到内置的 `default` 主题，因此一个主题可以只包含一种颜色。

<a id="quick-start-your-first-theme"></a>
### 快速上手——你的第一个主题

```bash
mkdir -p ~/.hermes/dashboard-themes
```

```yaml
# ~/.hermes/dashboard-themes/neon.yaml
name: neon
label: Neon
description: Pure magenta on black

palette:
  background: "#000000"
  midground: "#ff00ff"
```

刷新仪表盘。点击顶部的调色板图标，选择 **Neon**。背景变为黑色，文字和强调色变为洋红色，所有衍生颜色（卡片、边框、弱化、光环等）都会通过 CSS 的 `color-mix()` 从这 2 种颜色的组合中重新计算。

这就是完整的入门流程：一个文件，两种颜色。以下内容都是可选的细化。

<a id="palette-typography-layout"></a>
### 调色板、排版、布局

这三个模块是主题的核心。每个模块都是独立的——你可以只覆盖其中一个，而保留其他模块。
<a id="palette-3-layer"></a>
#### 调色板（三层）

调色板由三层颜色加上暖光渐晕色和噪点颗粒乘数组成。控制面板的设计系统级联通过 CSS `color-mix()` 从这个三元组推导出所有shadcn兼容的令牌（card、popover、muted、border、primary、destructive、ring等）。覆盖这三个颜色会级联影响到整个UI。

| 键 | 描述 |
|---|---|
| `palette.background` | 最深的画布底色——通常接近黑色。影响页面背景和卡片填充色。 |
| `palette.midground` | 主要文字和强调色。大多数UI元素（前景文字、按钮轮廓、聚焦环）读取此颜色。 |
| `palette.foreground` | 顶层高亮色。默认主题将其设为白色且 Alpha 为 0（不可见）；希望在上方有明亮强调色的主题可以提高其 Alpha 值。 |
| `palette.warmGlow` | 由 `&lt;Backdrop /&gt;` 用作渐晕颜色的 `rgba(...)` 字符串。 |
| `palette.noiseOpacity` | 颗粒覆盖层的 0–1.2 倍乘数。值越低越柔和，越高越粗糙。 |
每个图层接受 `{hex: "#RRGGBB", alpha: 0.0–1.0}` 或纯十六进制字符串（alpha 默认为 1.0）。

```yaml
palette:
  background:
    hex: "#05091a"
    alpha: 1.0
  midground: "#d8f0ff"          # 纯十六进制，alpha = 1.0
  foreground:
    hex: "#ffffff"
    alpha: 0                    # 不可见的顶层
  warmGlow: "rgba(255, 199, 55, 0.24)"
  noiseOpacity: 0.7
```

<a id="typography"></a>
#### 排版

| 键 | 类型 | 描述 |
|-----|------|-------------|
| `fontSans` | 字符串 | 正文的 CSS font-family 堆栈（应用于 `html`、`body`）。 |
| `fontMono` | 字符串 | 代码块、`&lt;code&gt;`、`.font-mono` 工具类的 CSS font-family 堆栈。 |
| `fontDisplay` | 字符串 | 可选的标题/展示字体堆栈。回退到 `fontSans`。 |
| `fontUrl` | 字符串 | 可选的外部样式表 URL。在主题切换时作为 `&lt;link rel="stylesheet"&gt;` 注入到 `&lt;head&gt;` 中。相同的 URL 不会重复注入。支持 Google Fonts、Bunny Fonts、自托管的 `@font-face` 样式表——任何可链接的地址均可。 |
| `baseSize` | 字符串 | 根字体大小——控制 rem 比例。例如 `"14px"`、`"16px"`。 |
| `lineHeight` | 字符串 | 默认行高。例如 `"1.5"`、`"1.65"`。 |
| `letterSpacing` | 字符串 | 默认字间距。例如 `"0"`、`"0.01em"`、`"-0.01em"`。 |
```yaml
typography:
  fontSans: '"Orbitron", "Eurostile", "Impact", sans-serif'
  fontMono: '"Share Tech Mono", ui-monospace, monospace'
  fontDisplay: '"Orbitron", "Eurostile", sans-serif'
  fontUrl: "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Share+Tech+Mono&display=swap"
  baseSize: "14px"
  lineHeight: "1.5"
  letterSpacing: "0.04em"
```

<a id="layout"></a>
#### 布局

| 键 | 值 | 描述 |
|-----|--------|-------------|
| `radius` | 任意 CSS 长度（`"0"`, `"0.25rem"`, `"0.5rem"`, `"1rem"`, ...） | 圆角标记。映射到 `--radius`，并级联到 `--radius-sm/md/lg/xl` —— 所有带圆角的元素会统一变化。 |
| `density` | `compact` \| `comfortable` \| `spacious` | 间距倍数，以 CSS 变量 `--spacing-mul` 形式应用。`compact = 0.85×`，`comfortable = 1.0×`（默认），`spacious = 1.2×`。作用于 Tailwind 的基础间距，因此 padding、gap、space-between 等工具类都会按比例缩放。 |

```yaml
layout:
  radius: "0"
  density: compact
```
<a id="layout-variants"></a>
### 布局变体

`layoutVariant` 选择整体外壳布局。未指定时默认值为 `"standard"`。

| 变体 | 行为 |
|---------|-----------|
| `standard` | 单栏，最大宽度 1600px（默认）。 |
| `cockpit` | 左侧边栏轨道（260px）+ 主内容区域。通过插件的 `sidebar` 插槽填充 — 请参见 [Shell 插槽](#shell-slots)。若无插件，则轨道显示占位符。 |
| `tiled` | 去掉最大宽度限制，使页面可以使用全视口宽度。 |

```yaml
layoutVariant: cockpit
```

当前变体暴露为 `document.documentElement.dataset.layoutVariant`，因此 `customCSS` 中的原始 CSS 可以通过 `:root[data-layout-variant="cockpit"] ...` 定位它。

<a id="theme-assets-images-as-css-vars"></a>
### 主题资源（图片作为 CSS 变量）

为主题附带艺术作品 URL。每个命名插槽变成一个 CSS 变量（`--theme-asset-&lt;name&gt;`），内置外壳和任何插件都可以读取。`bg` 插槽会自动接入背景；其他插槽面向插件。

```yaml
assets:
  bg: "https://example.com/hero-bg.jpg"           # auto-wired into <Backdrop />
  hero: "/my-images/strike-freedom.png"           # for plugin sidebars
  crest: "/my-images/crest.svg"                   # for header-left plugins
  logo: "/my-images/logo.png"
  sidebar: "/my-images/rail.png"
  header: "/my-images/header-art.png"
  custom:
    scanLines: "/my-images/scanlines.png"         # → --theme-asset-custom-scanLines
```
值接受：

- 裸 URL — 会自动包裹在 `url(...)` 中。
- 预包裹的 `url(...)`、`linear-gradient(...)`、`radial-gradient(...)` 表达式 — 按原样使用。
- `"none"` — 显式选择不使用。

每个资源也会作为 `--theme-asset-&lt;name&gt;-raw`（未包裹的 URL）输出，以便插件在需要将其传递给 `&lt;img src&gt;` 而不是 `background-image` 时使用。

插件通过纯 CSS 或 JS 读取这些值：

```javascript
// 在插件插槽中
const hero = getComputedStyle(document.documentElement)
  .getPropertyValue("--theme-asset-hero").trim();
```

<a id="component-chrome-overrides"></a>
### 组件外观覆盖

`componentStyles` 无需编写 CSS 选择器即可重新设置各个 shell 组件的外观。每个分组的条目会成为 CSS 变量（`--component-<分组>-<短横线分隔的属性>`），shell 的共享组件会读取这些变量。因此，`card:` 的覆盖会应用到每个 `&lt;Card&gt;`，`header:` 会应用到应用栏，以此类推。

```yaml
componentStyles:
  card:
    clipPath: "polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px)"
    background: "linear-gradient(180deg, rgba(10, 22, 52, 0.85), rgba(5, 9, 26, 0.92))"
    boxShadow: "inset 0 0 0 1px rgba(64, 200, 255, 0.28)"
  header:
    background: "linear-gradient(180deg, rgba(16, 32, 72, 0.95), rgba(5, 9, 26, 0.9))"
  tab:
    clipPath: "polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)"
  sidebar: {}
  backdrop: {}
  footer: {}
  progress: {}
  badge: {}
  page: {}
```
支持的桶（buckets）：`card`、`header`、`footer`、`sidebar`、`tab`、`progress`、`badge`、`backdrop`、`page`。

属性名称使用驼峰式命名（如 `clipPath`），输出时会转为 kebab 式（`clip-path`）。值则为普通 CSS 字符串——CSS 支持的任何内容都可以（如 `clip-path`、`border-image`、`background`、`box-shadow`、`animation`……）。

<a id="color-overrides"></a>
### 颜色覆盖

大部分主题不需要这个——3 层调色板会自动派生所有 shadcn 令牌。当你需要某个派生无法生成的特定强调色时（比如柔和主题中更柔和的破坏红，或者为某个品牌指定的特定成功绿），可以使用 `colorOverrides`。

```yaml
colorOverrides:
  primary: "#ffce3a"
  primaryForeground: "#05091a"
  accent: "#3fd3ff"
  ring: "#3fd3ff"
  destructive: "#ff3a5e"
  border: "rgba(64, 200, 255, 0.28)"
```

支持的键：`card`、`cardForeground`、`popover`、`popoverForeground`、`primary`、`primaryForeground`、`secondary`、`secondaryForeground`、`muted`、`mutedForeground`、`accent`、`accentForeground`、`destructive`、`destructiveForeground`、`success`、`warning`、`border`、`input`、`ring`。
每个键与 `--color-&lt;kebab&gt;` CSS 变量一一对应（例如 `primaryForeground` → `--color-primary-foreground`）。此处设置的任何键仅覆盖当前主题的调色板级联——切换到其他主题将清除这些覆盖。

<a id="raw-customcss"></a>
### 原始 `customCSS`

对于 `componentStyles` 无法表达的选择器级别装饰（如伪元素、动画、媒体查询、主题范围覆盖），可将原始 CSS 放入 `customCSS`：

```yaml
customCSS: |
  /* Scanline overlay — only visible when cockpit variant is active. */
  :root[data-layout-variant="cockpit"] body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 100;
    background: repeating-linear-gradient(to bottom,
      transparent 0px, transparent 2px,
      rgba(64, 200, 255, 0.035) 3px, rgba(64, 200, 255, 0.035) 4px);
    mix-blend-mode: screen;
  }
```

CSS 在应用主题时以单个作用域 `&lt;style data-hermes-theme-css&gt;` 标签注入，并在切换主题时清理。**每个主题上限为 32 KiB。**
<a id="built-in-themes"></a>
### 内置主题

每个内置主题都自带独立的调色板、排版和布局——切换主题会带来超越颜色变化的可见改动。

| 主题 | 调色板 | 排版 | 布局 |
|-------|---------|------------|--------|
| **Hermes Teal**（`default`） | 深青色 + 奶油色 | 系统字体栈，15px | 0.5rem 圆角，舒适 |
| **Hermes Teal（大号）**（`default-large`） | 与默认相同 | 系统字体栈，18px，行高 1.65 | 0.5rem 圆角，宽敞 |
| **Midnight**（`midnight`） | 深紫蓝色 | Inter + JetBrains Mono，14px | 0.75rem 圆角，舒适 |
| **Ember**（`ember`） | 暖红 + 铜色 | Spectral（衬线）+ IBM Plex Mono，15px | 0.25rem 圆角，舒适 |
| **Mono**（`mono`） | 灰度 | IBM Plex Sans + IBM Plex Mono，13px | 0 圆角，紧凑 |
| **Cyberpunk**（`cyberpunk`） | 黑色背景上的霓虹绿 | 全用 Share Tech Mono，14px | 0 圆角，紧凑 |
| **Rosé**（`rose`） | 粉色 + 象牙色 | Fraunces（衬线）+ DM Mono，16px | 1rem 圆角，宽敞 |

引用 Google Fonts 的主题（除了 Hermes Teal 以外的所有主题）会按需加载样式表——当你第一次切换到它们时，一个 `&lt;link&gt;` 标签会被注入到 `&lt;head&gt;` 中。
<a id="full-theme-yaml-reference"></a>
### 完整主题 YAML 参考

所有可调参数集中在一个文件中——按需复制和精简：

```yaml
# ~/.hermes/dashboard-themes/ocean.yaml
name: ocean
label: 深海蓝
description: 深海蓝色搭配珊瑚色点缀

# 三层色板（支持 {hex, alpha} 或裸 hex）
palette:
  background:
    hex: "#0a1628"
    alpha: 1.0
  midground:
    hex: "#a8d0ff"
    alpha: 1.0
  foreground:
    hex: "#ffffff"
    alpha: 0.0
  warmGlow: "rgba(255, 107, 107, 0.35)"
  noiseOpacity: 0.7

typography:
  fontSans: "Poppins, system-ui, sans-serif"
  fontMono: "Fira Code, ui-monospace, monospace"
  fontDisplay: "Poppins, system-ui, sans-serif"   # 可选
  fontUrl: "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Fira+Code:wght@400;500&display=swap"
  baseSize: "15px"
  lineHeight: "1.6"
  letterSpacing: "-0.003em"

layout:
  radius: "0.75rem"
  density: comfortable

layoutVariant: standard        # standard | cockpit | tiled

assets:
  bg: "https://example.com/ocean-bg.jpg"
  hero: "/my-images/kraken.png"
  crest: "/my-images/anchor.svg"
  logo: "/my-images/logo.png"
  custom:
    pattern: "/my-images/waves.svg"

componentStyles:
  card:
    boxShadow: "inset 0 0 0 1px rgba(168, 208, 255, 0.18)"
  header:
    background: "linear-gradient(180deg, rgba(10, 22, 40, 0.95), rgba(5, 9, 26, 0.9))"

colorOverrides:
  destructive: "#ff6b6b"
  ring: "#ff6b6b"

customCSS: |
  /* 任意其他选择器级别的微调 */
```
创建文件后刷新仪表盘。从顶部标题栏实时切换主题——点击调色板图标。所选主题会持久化到 `config.yaml` 的 `dashboard.theme` 中，并在重新加载后恢复。

---

<a id="plugins"></a>
## 插件

一个仪表盘插件是一个包含 `manifest.json`、一个预构建的 JS 包以及可选的一个 CSS 文件和一个带 FastAPI 路由的 Python 文件的目录。插件存放在 `~/.hermes/plugins/&lt;name&gt;/` 中，与其他 Hermes 插件并列——仪表盘扩展是该插件目录内的 `dashboard/` 子文件夹，因此一个插件可以通过一次安装同时扩展 CLI/网关和仪表盘。

插件不打包 React 或 UI 组件。它们使用暴露在 `window.__HERMES_PLUGIN_SDK__` 上的 **Plugin SDK**。这使插件包保持小巧（通常只有几 KB），并避免版本冲突。

<a id="quick-start-your-first-plugin"></a>
### 快速开始——你的第一个插件 {#quick-start--your-first-plugin}

创建目录结构：

```bash
mkdir -p ~/.hermes/plugins/my-plugin/dashboard/dist
```

编写 manifest：

```json
// ~/.hermes/plugins/my-plugin/dashboard/manifest.json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:skills"
  },
  "entry": "dist/index.js"
}
```
编写 JS 包（一个简单的 IIFE——无需构建步骤）：

```javascript
// ~/.hermes/plugins/my-plugin/dashboard/dist/index.js
(function () {
  "use strict";

  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { Card, CardHeader, CardTitle, CardContent } = SDK.components;

  function MyPage() {
    return React.createElement(Card, null,
      React.createElement(CardHeader, null,
        React.createElement(CardTitle, null, "My Plugin"),
      ),
      React.createElement(CardContent, null,
        React.createElement("p", { className: "text-sm text-muted-foreground" },
          "Hello from my custom dashboard tab.",
        ),
      ),
    );
  }

  window.__HERMES_PLUGINS__.register("my-plugin", MyPage);
})();
```

刷新仪表盘——你的标签页会出现在导航栏中，位于 **Skills** 之后。

<a id="skip-react-createelement"></a>
:::tip 跳过 React.createElement
如果你喜欢 JSX，可以使用任何打包工具（esbuild、Vite、rollup），将 React 标记为外部依赖并输出 IIFE。唯一的硬性要求是最终文件是一个可通过 `&lt;script&gt;` 加载的单个 JS 文件。React 不会被打包；它来自 `SDK.React`。
:::
<a id="directory-layout"></a>
### 目录布局

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml              # 可选 — 现有 CLI/网关插件清单
├── __init__.py              # 可选 — 现有 CLI/网关钩子
└── dashboard/               # 仪表盘扩展
    ├── manifest.json        # 必选 — 标签页配置、图标、入口点
    ├── dist/
    │   ├── index.js         # 必选 — 预构建的 JS 包 (IIFE)
    │   └── style.css        # 可选 — 自定义 CSS
    └── plugin_api.py        # 可选 — 后端 API 路由 (FastAPI)
```

单个插件目录可以包含三种正交扩展：

- `plugin.yaml` + `__init__.py` — CLI/网关插件（参见 [插件页面](./plugins)）。
- `dashboard/manifest.json` + `dashboard/dist/index.js` — 仪表盘 UI 插件。
- `dashboard/plugin_api.py` — 仪表盘后端路由。

以上都不是必需的；只需包含你需要的部分。

<a id="manifest-reference"></a>
### 清单参考

```json
{
  "name": "my-plugin",
  "label": "我的插件",
  "description": "该插件的作用",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:skills",
    "override": "/",
    "hidden": false
  },
  "slots": ["sidebar", "header-left"],
  "entry": "dist/index.js",
  "css": "dist/style.css",
  "api": "plugin_api.py"
}
```
| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 唯一的插件标识符。使用小写字母，允许连字符。用于URL和注册。 |
| `label` | 是 | 显示在导航标签中的名称。 |
| `description` | 否 | 简短描述（显示在仪表盘管理界面中）。 |
| `icon` | 否 | Lucide 图标名称。默认值为 `Puzzle`。无法识别的名称会回退为 `Puzzle`。 |
| `version` | 否 | Semver 版本字符串。默认值为 `0.0.0`。 |
| `tab.path` | 是 | 标签页的URL路径（例如 `/my-plugin`）。 |
| `tab.position` | 否 | 标签页的插入位置。`"end"`（默认）、`"after:&lt;path&gt;"` 或 `"before:&lt;path&gt;"`——冒号后的值是目标标签页的**路径片段**（不含开头的斜杠）。示例：`"after:skills"`、`"before:config"`。 |
| `tab.override` | 否 | 设置为内置路由路径（`"/"`、`"/sessions"`、`"/config"` 等）以**替换**该页面，而不是添加新标签页。请参阅[替换内置页面](#replacing-built-in-pages-taboverride)。 |
| `tab.hidden` | 否 | 若为 true，则注册组件及所有插槽，但不在导航中添加标签页。由仅使用插槽的插件使用。请参阅[仅插槽插件](#slot-only-plugins-tabhidden)。 |
| `slots` | 否 | 该插件填充的命名外壳插槽。**仅作为文档辅助**——实际注册通过 JS 包中的 `registerSlot()` 完成。在此列出插槽可使发现界面信息更丰富。 |
| `entry` | 是 | 相对于 `dashboard/` 的 JS 包路径。默认值为 `dist/index.js`。 |
| `css` | 否 | 要作为 `&lt;link&gt;` 标签插入的 CSS 文件路径。 |
| `api` | 否 | 包含 FastAPI 路由的 Python 文件路径。挂载在 `/api/plugins/&lt;name&gt;/`。 |
<a id="available-icons"></a>
#### 可用图标

插件使用 Lucide 图标名称。控制面板通过名称映射这些图标——未知的名称静默回退到 `Puzzle`。

当前已映射的图标：`Activity`、`BarChart3`、`Clock`、`Code`、`Database`、`Eye`、`FileText`、`Globe`、`Heart`、`KeyRound`、`MessageSquare`、`Package`、`Puzzle`、`Settings`、`Shield`、`Sparkles`、`Star`、`Terminal`、`Wrench`、`Zap`。

需要其他图标？请向 `web/src/App.tsx` 的 `ICON_MAP` 提交 PR——纯新增改动。

<a id="the-plugin-sdk"></a>
### 插件 SDK

插件所需的一切都位于 `window.__HERMES_PLUGIN_SDK__` 上。插件不应直接导入 React。

```javascript
const SDK = window.__HERMES_PLUGIN_SDK__;

// React + hooks
SDK.React                    // React 实例
SDK.hooks.useState
SDK.hooks.useEffect
SDK.hooks.useCallback
SDK.hooks.useMemo
SDK.hooks.useRef
SDK.hooks.useContext
SDK.hooks.createContext

// UI 组件（shadcn/ui 原语）
SDK.components.Card
SDK.components.CardHeader
SDK.components.CardTitle
SDK.components.CardContent
SDK.components.Badge
SDK.components.Button
SDK.components.Input
SDK.components.Label
SDK.components.Select
SDK.components.SelectOption
SDK.components.Separator
SDK.components.Tabs
SDK.components.TabsList
SDK.components.TabsTrigger
SDK.components.PluginSlot    // 渲染一个命名插槽（用于嵌套插件 UI）

// Hermes API 客户端 + 原生 fetcher
SDK.api                      // 类型化客户端 — getStatus、getSessions、getConfig 等
SDK.fetchJSON                // 用于自定义端点（插件注册的路由）的原生 fetch

// 工具函数
SDK.utils.cn                 // Tailwind 类名合并器（clsx + twMerge）
SDK.utils.timeAgo            // 从 Unix 时间戳得出 "5m ago"
SDK.utils.isoTimeAgo         // 从 ISO 字符串得出 "5m ago"

// Hooks
SDK.useI18n                  // 用于多语言插件的 i18n hook
```
<a id="calling-your-plugin-s-backend"></a>
#### 调用插件的后端

```javascript
SDK.fetchJSON("/api/plugins/my-plugin/data")
  .then((data) => console.log(data))
  .catch((err) => console.error("API call failed:", err));
```

`fetchJSON` 会注入会话认证令牌，将错误以抛出异常的方式呈现，并自动解析 JSON。

<a id="calling-built-in-hermes-endpoints"></a>
#### 调用内置的 Hermes 端点

```javascript
// Agent 状态
SDK.api.getStatus().then((s) => console.log("版本:", s.version));

// 最近的会话
SDK.api.getSessions(10).then((resp) => console.log(resp.sessions.length));
```

完整列表请参见 [Web 仪表盘 → REST API](./web-dashboard#rest-api)。

<a id="shell-slots"></a>
### Shell 插槽

插槽（Slot）允许插件将组件注入到应用外壳的命名位置——例如驾驶舱侧边栏、页眉、页脚、覆盖层——而无需占用整个标签页。多个插件可以填充同一个插槽；它们按照注册顺序堆叠渲染。

从插件包内部注册：

```javascript
window.__HERMES_PLUGINS__.registerSlot("my-plugin", "sidebar", MySidebar);
window.__HERMES_PLUGINS__.registerSlot("my-plugin", "header-left", MyCrest);
```
<a id="slot-catalogue"></a>
#### 插槽目录

**Shell 级插槽**（可在应用界面的任何位置渲染）：

| 插槽 | 位置 |
|------|----------|
| `backdrop` | 在 `&lt;Backdrop /&gt;` 层级堆栈内部，位于噪点层之上。 |
| `header-left` | 顶部栏中 Hermes 品牌标识之前。 |
| `header-right` | 顶部栏中主题/语言切换器之前。 |
| `header-banner` | 导航下方的一条全宽横幅。 |
| `sidebar` | Cockpit 侧边栏轨道——**仅当 `layoutVariant === "cockpit"` 时渲染**。 |
| `pre-main` | 路由出口之上（在 `&lt;main&gt;` 内部）。 |
| `post-main` | 路由出口之下（在 `&lt;main&gt;` 内部）。 |
| `footer-left` | 页脚单元格内容（替换默认内容）。 |
| `footer-right` | 页脚单元格内容（替换默认内容）。 |
| `overlay` | 位于所有内容之上的固定定位层。用于实现 `customCSS` 单独无法完成的效果（扫描线、装饰边框等）。 |

**页面级插槽**（仅在指定的内置页面上渲染 —— 使用这些插槽可在现有页面中注入组件、卡片或工具栏，而无需覆盖整个路由）：
| 插槽位置 | 渲染位置 |
|----------|----------|
| `sessions:top` / `sessions:bottom` | `/sessions` 页面的顶部 / 底部。 |
| `analytics:top` / `analytics:bottom` | `/analytics` 页面的顶部 / 底部。 |
| `logs:top` / `logs:bottom` | `/logs` 页面的顶部（过滤器工具栏上方）/ 底部（日志查看器下方）。 |
| `cron:top` / `cron:bottom` | `/cron` 页面的顶部 / 底部。 |
| `skills:top` / `skills:bottom` | `/skills` 页面的顶部 / 底部。 |
| `config:top` / `config:bottom` | `/config` 页面的顶部 / 底部。 |
| `env:top` / `env:bottom` | `/env`（Keys）页面的顶部 / 底部。 |
| `docs:top` / `docs:bottom` | `/docs` 页面的顶部（iframe 上方）/ 底部。 |
| `chat:top` / `chat:bottom` | `/chat` 页面的顶部 / 底部（仅在嵌入式聊天启用时生效）。 |

示例 — 在 Sessions 页面顶部添加一个横幅卡片：

```javascript
function PinnedSessionsBanner() {
  return React.createElement(Card, null,
    React.createElement(CardContent, { className: "py-2 text-xs" },
      "由 my-plugin 注入的固定笔记"),
  );
}

window.__HERMES_PLUGINS__.registerSlot("my-plugin", "sessions:top", PinnedSessionsBanner);
```
如果你的插件只增强现有页面，且不需要自己的侧边栏标签，可以将页面级插槽与 `tab.hidden: true` 结合使用。

Shell 只会为上述插槽渲染 `&lt;PluginSlot name="..." /&gt;`。注册表还接受其他名称，用于嵌套插件 UI — 插件可以通过 `SDK.components.PluginSlot` 暴露自己的插槽。

<a id="re-registration-and-hmr"></a>
#### 重新注册与 HMR

如果相同的 `(plugin, slot)` 对注册了两次，后一次调用会替换前一次 — 这与 React HMR 期望插件重新挂载的行为一致。

<a id="replacing-built-in-pages-tab-override"></a>
### 替换内置页面（`tab.override`） {#replacing-built-in-pages-taboverride}

将 `tab.override` 设置为内置路由路径，会使插件的组件替换该页面，而不是添加新标签。当主题想要自定义主页（`/`）但保持仪表盘其余部分不变时，这非常有用。

```json
{
  "name": "my-home",
  "label": "Home",
  "tab": {
    "path": "/my-home",
    "override": "/",
    "position": "end"
  },
  "entry": "dist/index.js"
}
```

设置了 `override` 后：
- `/` 处的原始页面组件已从路由中移除。
- 你的插件改为在 `/` 处渲染。
- 不会为 `tab.path` 添加导航选项卡（覆盖本身就是目的）。

只有一个插件可以覆盖给定的路径。如果两个插件声称覆盖同一路径，第一个生效，第二个会被忽略并在开发模式下显示警告。

如果你只需要在现有页面上添加卡片或工具栏，而无需完全接管页面，请改用[页面作用域插槽](#augmenting-built-in-pages-page-scoped-slots)。

<a id="augmenting-built-in-pages-page-scoped-slots"></a>
### 增强内置页面（页面作用域插槽）

通过 `tab.override` 进行完全替换是一种重量级做法——你的插件现在拥有整个页面，包括我们未来对该页面所做的任何更新。大多数情况下，你只是想在现有页面上添加横幅、卡片或工具栏。这正是**页面作用域插槽**的用途。

每个内置页面都会在其内容区域的顶部和底部暴露 `&lt;page&gt;:top` 和 `&lt;page&gt;:bottom` 插槽。你的插件通过调用 `registerSlot()` 来填充这些插槽——内置页面会正常运行，而你的组件则会与它一起渲染。
可用插槽：`sessions:*`、`analytics:*`、`logs:*`、`cron:*`、`skills:*`、`config:*`、`env:*`、`docs:*`、`chat:*`（每个都有 `:top` 和 `:bottom`）。完整目录请参阅 [Shell 插槽 → 插槽目录](#slot-catalogue)。

最小示例 — 在 Sessions 页面顶部固定一个横幅：

```json
// ~/.hermes/plugins/session-notes/dashboard/manifest.json
{
  "name": "session-notes",
  "label": "Session Notes",
  "tab": { "path": "/session-notes", "hidden": true },
  "slots": ["sessions:top"],
  "entry": "dist/index.js"
}
```

```javascript
// ~/.hermes/plugins/session-notes/dashboard/dist/index.js
(function () {
  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { Card, CardContent } = SDK.components;

  function Banner() {
    return React.createElement(Card, null,
      React.createElement(CardContent, { className: "py-2 text-xs" },
        "Remember to label important sessions before archiving."),
    );
  }

  // Placeholder for the hidden tab.
  window.__HERMES_PLUGINS__.register("session-notes", function () { return null; });

  // The real work.
  window.__HERMES_PLUGINS__.registerSlot("session-notes", "sessions:top", Banner);
})();
```
关键点：

- `tab.hidden: true` 使插件不出现在侧边栏中——它没有独立的页面。
- `slots` 清单字段仅用于文档说明。实际的绑定通过 JS 包中的 `registerSlot()` 完成。
- 多个插件可以声明同一个页面作用域的插槽。它们按注册顺序堆叠渲染。
- 当没有插件注册时，零占用：内置页面完全按原样渲染。

一个参考插件（[`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins/tree/main/example-dashboard) 中的 `example-dashboard`）提供了一个实时演示，将横幅注入到 `sessions:top` 中——安装它即可端到端地查看该模式。

<a id="slot-only-plugins-tab-hidden"></a>
### 仅插槽插件（`tab.hidden`） {#slot-only-plugins-tabhidden}

当 `tab.hidden: true` 时，插件会注册其组件（用于直接 URL 访问）和任何插槽，但不会向导航添加标签页。用于仅存在于注入插槽的插件——头部徽章、侧边栏 HUD、覆盖层。

```json
{
  "name": "header-crest",
  "label": "Header Crest",
  "tab": {
    "path": "/header-crest",
    "position": "end",
    "hidden": true
  },
  "slots": ["header-left"],
  "entry": "dist/index.js"
}
```
该 bundle 仍然用占位组件调用 `register()`（这样其他用户直接访问这个 URL 时也不会出错），然后再调用 `registerSlot()` 来完成实际注册。

<a id="backend-api-routes"></a>
### 后端 API 路由

插件可以在 manifest 中通过设置 `api` 来注册 FastAPI 路由。创建一个文件并导出 `router`：

```python
# ~/.hermes/plugins/my-plugin/dashboard/plugin_api.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/data")
async def get_data():
    return {"items": ["one", "two", "three"]}

@router.post("/action")
async def do_action(body: dict):
    return {"ok": True, "received": body}
```

路由会被挂载到 `/api/plugins/&lt;name&gt;/` 下，因此上面的路由就变成了：

- `GET  /api/plugins/my-plugin/data`
- `POST /api/plugins/my-plugin/action`

由于 dashboard 服务器默认绑定到 localhost，插件 API 路由会绕过 session-token 认证。**如果你运行了不受信任的插件，请千万不要用 `--host 0.0.0.0` 把 dashboard 暴露在公网接口上**——因为这些插件的路由也会变得可访问。
<a id="accessing-hermes-internals"></a>
#### 访问 Hermes 内部组件

后端路由在仪表盘进程内运行，因此可以直接从 hermes-agent 代码库导入：

```python
from fastapi import APIRouter
from hermes_state import SessionDB
from hermes_cli.config import load_config

router = APIRouter()

@router.get("/session-count")
async def session_count():
    db = SessionDB()
    try:
        count = len(db.list_sessions(limit=9999))
        return {"count": count}
    finally:
        db.close()

@router.get("/config-snapshot")
async def config_snapshot():
    cfg = load_config()
    return {"model": cfg.get("model", {})}
```

<a id="custom-css-per-plugin"></a>
### 为每个插件自定义 CSS

如果你的插件需要超出 Tailwind 类和内联 `style=` 之外样式，可以添加一个 CSS 文件并在 manifest 中引用它：

```json
{
  "css": "dist/style.css"
}
```

该文件会在插件加载时作为 `&lt;link&gt;` 标签注入。使用特定的类名以避免与仪表盘样式冲突，并引用仪表盘的 CSS 变量以保持主题感知：
```css
/* dist/style.css */
.my-plugin-chart {
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-card-foreground);
  padding: 1rem;
}
.my-plugin-chart:hover {
  border-color: var(--color-ring);
}
```

仪表盘将所有 shadcn 令牌暴露为 `--color-*` 以及主题扩展（`--theme-asset-*`、`--component-&lt;bucket&gt;-*`、`--radius`、`--spacing-mul`）。引用这些令牌，你的插件将随当前主题自动换肤。

<a id="plugin-discovery-reload"></a>
### 插件发现与重载 {#plugin-discovery--reload}

仪表盘会在以下三个目录中扫描 `dashboard/manifest.json`：

| 优先级 | 目录 | 来源标签 |
|--------|------|----------|
| 1（冲突时优先） | `~/.hermes/plugins/&lt;name&gt;/dashboard/` | `user` |
| 2 | `&lt;repo&gt;/plugins/memory/&lt;name&gt;/dashboard/` | `bundled` |
| 2 | `&lt;repo&gt;/plugins/&lt;name&gt;/dashboard/` | `bundled` |
| 3 | `./.hermes/plugins/&lt;name&gt;/dashboard/` | `project` — 仅当设置了 `HERMES_ENABLE_PROJECT_PLUGINS` 时生效 |

发现结果在每个仪表盘进程中缓存。添加新插件后，请执行以下任一操作：
```bash
# 强制重新扫描而无需重启
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

……或重启 `hermes dashboard`。

<a id="plugin-load-lifecycle"></a>
#### 插件加载生命周期

1. 仪表盘加载。`main.tsx` 在 `window.__HERMES_PLUGIN_SDK__` 上暴露 SDK，在 `window.__HERMES_PLUGINS__` 上暴露注册表。
2. `App.tsx` 调用 `usePlugins()` → 获取 `GET /api/dashboard/plugins`。
3. 对于每个清单：如果声明了 CSS `&lt;link&gt;` 则注入，然后加载对应 JS 包的 `&lt;script&gt;` 标签。
4. 插件的 IIFE 执行并调用 `window.__HERMES_PLUGINS__.register(name, Component)` —— 同时可以选择为每个插槽调用 `.registerSlot(name, slot, Component)`。
5. 仪表盘根据清单解析注册的组件，将对应标签页添加到导航中（除非 `hidden`），并将该组件作为路由挂载。

插件在其脚本加载后有最多 **2 秒** 的时间调用 `register()`。之后仪表盘将停止等待并完成初始渲染。如果某个插件稍后注册，它仍会显示——导航是响应式的。
如果某个插件的脚本加载失败（404、语法错误、IIFE 执行异常），仪表盘会在浏览器控制台输出一条警告日志，然后跳过该插件继续运行。

---

<a id="combined-theme-plugin-demo"></a>
## 主题 + 插件组合演示

[`strike-freedom-cockpit`](https://github.com/NousResearch/hermes-example-plugins/tree/main/strike-freedom-cockpit) 插件（位于配套仓库 `hermes-example-plugins` 中）是一个完整的界面换肤演示。它将一个主题 YAML 与一个纯插槽插件配对，无需分叉仪表盘即可生成座舱风格的 HUD。

**演示内容：**

- 一个完整的主题，使用了调色板、排版、`fontUrl`、`layoutVariant: cockpit`、`assets`、`componentStyles`（带圆角的卡片、渐变背景）、`colorOverrides` 和 `customCSS`（扫描线叠加效果）。
- 一个纯插槽插件（`tab.hidden: true`），注册到三个插槽中：
  - `sidebar` — 一个 MS-STATUS 面板，通过 `SDK.api.getStatus()` 驱动实时遥测条。
  - `header-left` — 一个派系徽章，从当前主题中读取 `--theme-asset-crest`。
  - `footer-right` — 自定义标语，替换默认的组织行。
- 该插件通过 CSS 变量读取主题提供的素材，因此切换主题即可更换英雄图/徽章，无需修改插件代码。
**安装：**

```bash
git clone https://github.com/NousResearch/hermes-example-plugins.git

# 主题
cp hermes-example-plugins/strike-freedom-cockpit/theme/strike-freedom.yaml \
   ~/.hermes/dashboard-themes/

# 插件
cp -r hermes-example-plugins/strike-freedom-cockpit ~/.hermes/plugins/
```

打开仪表盘，从主题选择器中选择 **Strike Freedom**。驾驶舱侧边栏出现，徽章显示在页眉中，标语替换了页脚。切换回 **Hermes Teal**，插件仍然安装但不可见（`sidebar` 插槽仅在 `cockpit` 布局变体下渲染）。

阅读插件源代码（配套仓库中的 `strike-freedom-cockpit/dashboard/dist/index.js`），了解它如何读取 CSS 变量、如何防范不支持插槽的旧版仪表盘，以及如何从一个包中注册三个插槽。

---

<a id="api-reference"></a>
## API 参考

<a id="theme-endpoints"></a>
### 主题端点

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/themes` | GET | 列出可用主题及当前激活的主题名称。内置主题返回 `{name, label, description}`；用户主题还包括一个 `definition` 字段，包含完整的规范化主题对象。 |
| `/api/dashboard/theme` | PUT | 设置当前主题。请求体：`{"name": "midnight"}`。持久化到 `config.yaml` 中的 `dashboard.theme` 下。 |
<a id="plugin-endpoints"></a>
### 插件端点

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/plugins` | GET | 列出已发现的插件（包含清单，但排除内部字段）。 |
| `/api/dashboard/plugins/rescan` | GET | 强制重新扫描插件目录，无需重启。 |
| `/dashboard-plugins/&lt;name&gt;/&lt;path&gt;` | GET | 提供插件 `dashboard/` 目录中的静态资源。路径遍历攻击已被阻止。 |
| `/api/plugins/&lt;name&gt;/*` | * | 插件注册的后端路由。 |

<a id="sdk-on-window"></a>
### `window` 上的 SDK

| 全局变量 | 类型 | 提供方 |
|--------|------|----------|
| `window.__HERMES_PLUGIN_SDK__` | object | `registry.ts` — React、hooks、UI 组件、API 客户端、工具函数。 |
| `window.__HERMES_PLUGINS__.register(name, Component)` | function | 注册插件的核心组件。 |
| `window.__HERMES_PLUGINS__.registerSlot(name, slot, Component)` | function | 注册到指定的壳（shell）插槽中。 |

---

<a id="troubleshooting"></a>
## 故障排除

**我的主题没有出现在选择器中。**
检查文件是否位于 `~/.hermes/dashboard-themes/` 并且以 `.yaml` 或 `.yml` 结尾。刷新页面。运行 `curl http://127.0.0.1:9119/api/dashboard/themes` — 你的主题应当出现在响应中。如果 YAML 存在解析错误，仪表板会记录到 `~/.hermes/logs/` 下的 `errors.log` 文件中。
**我的插件标签页没有显示。**
1. 检查清单文件是否位于 `~/.hermes/plugins/&lt;name&gt;/dashboard/manifest.json`（注意 `dashboard/` 子目录）。
2. 执行 `curl http://127.0.0.1:9119/api/dashboard/plugins/rescan` 强制重新发现。
3. 打开浏览器开发者工具 → 网络 — 确认 `manifest.json`、`index.js` 以及任何 CSS 文件都已加载且没有 404 错误。
4. 打开浏览器开发者工具 → 控制台 — 查找 IIFE 执行期间的错误，或 `window.__HERMES_PLUGINS__ is undefined`（这表示 SDK 未初始化，通常是由于之前的 React 渲染崩溃导致）。
5. 验证你的打包文件调用了 `window.__HERMES_PLUGINS__.register(...)`，并且使用的**名称**与 `manifest.json:name` 中的**名称**一致。

**注册到插槽的组件没有渲染。**
`sidebar` 插槽仅在当前主题的 `layoutVariant` 为 `cockpit` 时才会渲染。其他插槽始终会渲染。如果你注册到一个没有命中的插槽，可以在 `registerSlot` 内部添加 `console.log` 来确认插件打包文件是否确实执行了。

**插件后端路由返回 404。**
1. 确认清单文件中 `"api": "plugin_api.py"` 指向的是 `dashboard/` 目录下的一个现有文件。
2. 重启 `hermes dashboard` — 插件 API 路由只在启动时挂载一次，**不会**在重新扫描时挂载。
3. 检查 `plugin_api.py` 是否在模块级别导出了 `router = APIRouter()`。其他导出名称不会被识别。
4. 查看 `~/.hermes/logs/errors.log` 的末尾，查找 `Failed to load plugin &lt;name&gt; API routes` — 导入错误会记录在那里。
**主题切换后我的颜色覆盖设置丢失了。**
`colorOverrides` 的作用域限定于当前激活的主题，切换主题时会被清除——这是设计如此。如果你希望覆盖设置持久生效，请将它们放在主题的 YAML 文件中，而不是放在实时切换器里。

**主题的 customCSS 被截断了。**
每个主题的 `customCSS` 块大小限制为 32 KiB。如果样式表较大，可以将其拆分到多个主题中，或者改用通过 `css` 字段注入完整样式表的插件（无大小限制）。

**我想在 PyPI 上发布一个插件。**
仪表盘插件是通过目录布局安装的，而不是通过 pip 入口点。目前最干净的发布方式是提供一个 git 仓库，让用户克隆到 `~/.hermes/plugins/` 目录下。目前尚未实现基于 pip 的仪表盘插件安装程序。
