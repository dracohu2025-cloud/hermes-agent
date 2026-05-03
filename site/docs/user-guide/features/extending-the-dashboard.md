---
sidebar_position: 17
title: "扩展仪表盘"
description: "为 Hermes Web 仪表盘构建主题和插件——调色板、排版、布局、自定义标签页、Shell 插槽、页面级插槽和后端 API 路由"
---

# 扩展仪表盘 {#extending-the-dashboard}

Hermes Web 仪表盘（`hermes dashboard`）的设计初衷是无需复刻代码库即可换肤和扩展。它暴露了三个层次：

1. **主题** —— YAML 文件，用于重新绘制仪表盘的调色板、排版、布局以及每个组件的界面装饰。将文件放入 `~/.hermes/dashboard-themes/` 目录后，它就会出现在主题切换器中。
2. **UI 插件** —— 一个包含 `manifest.json` 和 JavaScript 包的目录，用于注册标签页、替换内置页面、通过页面级插槽增强页面，或将组件注入到命名的 Shell 插槽中。
3. **后端插件** —— 该插件目录内的一个 Python 文件，暴露了一个 FastAPI `router`；路由会被挂载到 `/api/plugins/&lt;name&gt;/` 下，并从插件的 UI 中调用。

三者都是**运行时即插即用**的：无需克隆仓库、无需执行 `npm run build`、无需修改仪表盘源码。本页面是这三者的权威参考。

如果你只想使用仪表盘，请参阅 [Web 仪表盘](./web-dashboard)。如果你想为终端 CLI（而非 Web 仪表盘）换肤，请参阅 [皮肤与主题](./skins) —— CLI 皮肤系统与仪表盘主题无关。

:::note 各部分如何组合
主题和插件是独立但协同的。主题可以独立存在（仅一个 YAML 文件）。插件也可以独立存在（仅一个标签页）。两者结合，你可以构建一个带有自定义 HUD 的完整视觉换肤方案——捆绑的 `strike-freedom-cockpit` 演示正是如此。请参阅 [组合主题 + 插件演示](#combined-theme--plugin-demo)。
<a id="how-the-pieces-compose"></a>
:::

---

## 目录 {#table-of-contents}

- [主题](#themes)
  - [快速入门 —— 你的第一个主题](#quick-start--your-first-theme)
  - [调色板、排版、布局](#palette-typography-layout)
  - [布局变体](#layout-variants)
  - [主题资源（作为 CSS 变量的图片）](#theme-assets-images-as-css-vars)
  - [组件界面装饰覆盖](#component-chrome-overrides)
  - [颜色覆盖](#color-overrides)
  - [原始 `customCSS`](#raw-customcss)
  - [内置主题](#built-in-themes)
  - [完整主题 YAML 参考](#full-theme-yaml-reference)
- [插件](#plugins)
  - [快速入门 —— 你的第一个插件](#quick-start--your-first-plugin)
  - [目录布局](#directory-layout)
  - [清单参考](#manifest-reference)
  - [插件 SDK](#the-plugin-sdk)
  - [Shell 插槽](#shell-slots)
  - [替换内置页面（`tab.override`）](#replacing-built-in-pages-taboverride)
  - [增强内置页面（页面级插槽）](#augmenting-built-in-pages-page-scoped-slots)
  - [仅插槽插件（`tab.hidden`）](#slot-only-plugins-tabhidden)
  - [后端 API 路由](#backend-api-routes)
  - [每个插件的自定义 CSS](#custom-css-per-plugin)
  - [插件发现与重载](#plugin-discovery--reload)
- [组合主题 + 插件演示](#combined-theme--plugin-demo)
- [API 参考](#api-reference)
- [故障排除](#troubleshooting)

---

## 主题 {#themes}

主题是存储在 `~/.hermes/dashboard-themes/` 目录下的 YAML 文件。文件名无关紧要（系统使用的是主题的 `name:` 字段），但惯例是 `&lt;name&gt;.yaml`。每个字段都是可选的——缺失的键会回退到内置的 `default` 主题，因此一个主题可以小到只包含一种颜色。
<a id="quick-start-your-first-theme"></a>
### 快速上手 — 你的第一个主题 {#quick-start--your-first-theme}

```bash
mkdir -p ~/.hermes/dashboard-themes
```

```yaml
# ~/.hermes/dashboard-themes/neon.yaml
name: neon
label: Neon
description: 纯品红配黑色

palette:
  background: "#000000"
  midground: "#ff00ff"
```

刷新仪表盘。点击顶栏中的调色板图标，选择 **Neon**。背景变为黑色，文字和强调色变为品红，所有衍生颜色（卡片、边框、柔和色、环形等）都会通过 CSS 的 `color-mix()` 从这 2 色三元组重新计算。

这就是完整的入门流程：一个文件，两种颜色。以下内容均为可选的进阶调整。

### 调色板、排版、布局 {#palette-typography-layout}

这三个模块是主题的核心。每个模块相互独立——你可以只覆盖其中一个，其他保持不变。

#### 调色板（三层结构） {#palette-3-layer}

调色板由三层颜色加上一个暖光晕颜色和一个噪点纹理乘数组成。仪表盘的设计系统级联会通过 CSS 的 `color-mix()` 从这个三元组推导出所有 shadcn 兼容的令牌（卡片、弹出框、柔和色、边框、主色、破坏性、环形等）。覆盖这三种颜色会级联影响到整个 UI。

| 键 | 描述 |
|-----|-------------|
| `palette.background` | 最深的画布颜色——通常接近黑色。驱动页面背景和卡片填充色。 |
| `palette.midground` | 主要文字和强调色。大多数 UI 元素（前景文字、按钮轮廓、焦点环）都使用此颜色。 |
| `palette.foreground` | 顶层高亮色。默认主题将其设置为白色且 alpha 为 0（不可见）；需要在上层使用明亮强调色的主题可以提高其 alpha 值。 |
| `palette.warmGlow` | `rgba(...)` 字符串，用作 `&lt;Backdrop /&gt;` 组件的晕影颜色。 |
| `palette.noiseOpacity` | 0–1.2 的乘数，控制噪点纹理的透明度。数值越低越柔和，越高越粗糙。 |

每一层颜色可以接受 `{hex: "#RRGGBB", alpha: 0.0–1.0}` 格式，也可以直接使用十六进制字符串（alpha 默认为 1.0）。

```yaml
palette:
  background:
    hex: "#05091a"
    alpha: 1.0
  midground: "#d8f0ff"          # 直接十六进制，alpha = 1.0
  foreground:
    hex: "#ffffff"
    alpha: 0                    # 不可见的顶层
  warmGlow: "rgba(255, 199, 55, 0.24)"
  noiseOpacity: 0.7
```

#### 排版 {#typography}

| 键 | 类型 | 描述 |
|-----|------|-------------|
| `fontSans` | string | 正文的 CSS font-family 堆栈（应用于 `html`、`body`）。 |
| `fontMono` | string | 代码块、`&lt;code&gt;`、`.font-mono` 工具类的 CSS font-family 堆栈。 |
| `fontDisplay` | string | 可选的标题/展示字体堆栈。如果未设置，则回退到 `fontSans`。 |
| `fontUrl` | string | 可选的外部样式表 URL。在切换主题时，会以 `&lt;link rel="stylesheet"&gt;` 的形式注入到 `&lt;head&gt;` 中。相同的 URL 不会重复注入。适用于 Google Fonts、Bunny Fonts、自托管的 `@font-face` 样式表——任何可链接的字体资源。 |
| `baseSize` | string | 根字体大小——控制 rem 缩放比例。例如 `"14px"`、`"16px"`。 |
| `lineHeight` | string | 默认行高。例如 `"1.5"`、`"1.65"`。 |
| `letterSpacing` | string | 默认字间距。例如 `"0"`、`"0.01em"`、`"-0.01em"`。 |

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
#### 布局 {#layout}

| 键 | 值 | 描述 |
|-----|--------|-------------|
| `radius` | 任意 CSS 长度（`"0"`、`"0.25rem"`、`"0.5rem"`、`"1rem"` 等） | 圆角令牌。映射到 `--radius`，并级联到 `--radius-sm/md/lg/xl`——所有圆角元素会同步变化。 |
| `density` | `compact` \| `comfortable` \| `spacious` | 间距乘数，作为 CSS 变量 `--spacing-mul` 应用。`compact = 0.85×`，`comfortable = 1.0×`（默认），`spacious = 1.2×`。缩放 Tailwind 的基础间距，因此 padding、gap 和 space-between 工具类都会按比例变化。 |

```yaml
layout:
  radius: "0"
  density: compact
```

### 布局变体 {#layout-variants}

`layoutVariant` 选择整体外壳布局。未设置时默认为 `"standard"`。

| 变体 | 行为 |
|---------|-----------|
| `standard` | 单列，最大宽度 1600px（默认）。 |
| `cockpit` | 左侧边栏轨道（260px）+ 主内容。由插件通过 `sidebar` 插槽填充——参见 [外壳插槽](#shell-slots)。如果没有插件，轨道会显示占位符。 |
| `tiled` | 移除最大宽度限制，使页面可以使用整个视口宽度。 |

```yaml
layoutVariant: cockpit
```

当前变体会暴露为 `document.documentElement.dataset.layoutVariant`，因此 `customCSS` 中的原始 CSS 可以通过 `:root[data-layout-variant="cockpit"] ...` 来定位它。

### 主题资产（作为 CSS 变量的图片） {#theme-assets-images-as-css-vars}

将图片 URL 与主题一起提供。每个命名的插槽都会成为一个 CSS 变量（`--theme-asset-&lt;name&gt;`），内置外壳和任何插件都可以读取。`bg` 插槽会自动接入背景；其他插槽供插件使用。

```yaml
assets:
  bg: "https://example.com/hero-bg.jpg"           # 自动接入 <Backdrop />
  hero: "/my-images/strike-freedom.png"           # 用于插件侧边栏
  crest: "/my-images/crest.svg"                   # 用于头部左侧插件
  logo: "/my-images/logo.png"
  sidebar: "/my-images/rail.png"
  header: "/my-images/header-art.png"
  custom:
    scanLines: "/my-images/scanlines.png"         # → --theme-asset-custom-scanLines
```

值支持：

- 裸 URL——自动包裹在 `url(...)` 中。
- 预包裹的 `url(...)`、`linear-gradient(...)`、`radial-gradient(...)` 表达式——原样使用。
- `"none"`——显式退出。

每个资产还会作为 `--theme-asset-&lt;name&gt;-raw`（未包裹的 URL）发出，以便插件需要将其传递给 `&lt;img src&gt;` 而不是 `background-image` 时使用。

插件通过普通 CSS 或 JS 读取这些变量：

```javascript
// 在插件插槽中
const hero = getComputedStyle(document.documentElement)
  .getPropertyValue("--theme-asset-hero").trim();
```

### 组件外观覆盖 {#component-chrome-overrides}

`componentStyles` 可以重新设置单个外壳组件的样式，而无需编写 CSS 选择器。每个桶的条目会成为 CSS 变量（`--component-&lt;bucket&gt;-&lt;kebab-property&gt;`），外壳的共享组件会读取这些变量。因此 `card:` 的覆盖会应用于每个 `&lt;Card&gt;`，`header:` 应用于应用栏，等等。

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
支持的存储桶：`card`、`header`、`footer`、`sidebar`、`tab`、`progress`、`badge`、`backdrop`、`page`。

属性名使用驼峰命名法（`clipPath`），输出时转换为连字符命名（`clip-path`）。值使用纯 CSS 字符串——CSS 支持的任何值都可以（`clip-path`、`border-image`、`background`、`box-shadow`、`animation`……）。

### 颜色覆盖 {#color-overrides}

大多数主题不需要这个——三层调色板已经派生了所有 shadcn 令牌。当你想要一个派生无法产生的特定强调色时（例如浅色主题中更柔和的破坏性红色，或品牌特定的成功绿色），可以使用 `colorOverrides`。

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

每个键与 `--color-<连字符命名>` CSS 变量一一对应（例如 `primaryForeground` → `--color-primary-foreground`）。在此设置的任何键仅在当前活动主题中覆盖调色板级联——切换到其他主题会清除这些覆盖。

### 原始 `customCSS` {#raw-customcss}

对于 `componentStyles` 无法表达的选择器级样式——伪元素、动画、媒体查询、主题作用域覆盖——可以将原始 CSS 放入 `customCSS`：

```yaml
customCSS: |
  /* 扫描线叠加层——仅在驾驶舱变体激活时可见。 */
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

CSS 在应用主题时作为单个作用域 `&lt;style data-hermes-theme-css&gt;` 标签注入，并在切换主题时清理。**每个主题限制为 32 KiB。**

### 内置主题 {#built-in-themes}

每个内置主题都自带调色板、排版和布局——切换主题会产生超出颜色变化的可见差异。

| 主题 | 调色板 | 排版 | 布局 |
|-------|---------|------------|--------|
| **Hermes Teal**（`default`） | 深青色 + 奶油色 | 系统字体栈，15px | 0.5rem 圆角，舒适 |
| **Midnight**（`midnight`） | 深蓝紫色 | Inter + JetBrains Mono，14px | 0.75rem 圆角，舒适 |
| **Ember**（`ember`） | 暖深红 + 青铜色 | Spectral（衬线体）+ IBM Plex Mono，15px | 0.25rem 圆角，舒适 |
| **Mono**（`mono`） | 灰度 | IBM Plex Sans + IBM Plex Mono，13px | 0 圆角，紧凑 |
| **Cyberpunk**（`cyberpunk`） | 黑色背景上的霓虹绿 | 全用 Share Tech Mono，14px | 0 圆角，紧凑 |
| **Rosé**（`rose`） | 粉色 + 象牙色 | Fraunces（衬线体）+ DM Mono，16px | 1rem 圆角，宽敞 |

引用 Google Fonts 的主题（除 Hermes Teal 外所有主题）会在需要时加载样式表——当你第一次切换到它们时，一个 `&lt;link&gt;` 标签会被注入到 `&lt;head&gt;` 中。
### 完整主题 YAML 参考 {#full-theme-yaml-reference}

所有可调参数都在一个文件中——复制并删减你不需要的部分：

```yaml
# ~/.hermes/dashboard-themes/ocean.yaml
name: ocean
label: Ocean Deep
description: 深海蓝搭配珊瑚色点缀

# 3 层调色板（支持 {hex, alpha} 或纯 hex）
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
  /* 任何额外的选择器级别调整 */
```

创建文件后刷新仪表盘。从顶部栏实时切换主题——点击调色板图标。选择会持久化到 `config.yaml` 的 `dashboard.theme` 下，并在重新加载时恢复。

---

## 插件 {#plugins}

仪表盘插件是一个包含 `manifest.json`、预构建 JS 包，以及可选 CSS 文件和带 FastAPI 路由的 Python 文件的目录。插件位于 `~/.hermes/plugins/&lt;name&gt;/` 中，与其他 Hermes 插件并列——仪表盘扩展是该插件目录下的 `dashboard/` 子文件夹，因此一个插件可以通过一次安装同时扩展 CLI/网关和仪表盘。

插件不捆绑 React 或 UI 组件。它们使用暴露在 `window.__HERMES_PLUGIN_SDK__` 上的 **Plugin SDK**。这使插件包保持小巧（通常只有几 KB）并避免版本冲突。

<a id="quick-start-your-first-plugin"></a>
### 快速开始——你的第一个插件 {#quick-start--your-first-plugin}

创建目录结构：

```bash
mkdir -p ~/.hermes/plugins/my-plugin/dashboard/dist
```

编写清单文件：

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
刷新仪表盘 — 你的标签页会出现在导航栏中，位于 **Skills** 之后。

:::tip 跳过 React.createElement
如果你更喜欢 JSX，可以使用任何打包工具（esbuild、Vite、rollup），将 React 设为外部依赖并输出 IIFE 格式。唯一硬性要求是最终文件是一个可通过 `&lt;script&gt;` 加载的单个 JS 文件。React 不会被打包，它来自 `SDK.React`。
<a id="skip-react-createelement"></a>
:::

### 目录结构 {#directory-layout}

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml              # 可选 — 已有的 CLI/gateway 插件清单
├── __init__.py              # 可选 — 已有的 CLI/gateway 钩子
└── dashboard/               # 仪表盘扩展
    ├── manifest.json        # 必需 — 标签页配置、图标、入口点
    ├── dist/
    │   ├── index.js         # 必需 — 预构建的 JS 包（IIFE）
    │   └── style.css        # 可选 — 自定义 CSS
    └── plugin_api.py        # 可选 — 后端 API 路由（FastAPI）
```

单个插件目录可以承载三种正交的扩展：

- `plugin.yaml` + `__init__.py` — CLI/gateway 插件（参见 [插件页面](./plugins)）。
- `dashboard/manifest.json` + `dashboard/dist/index.js` — 仪表盘 UI 插件。
- `dashboard/plugin_api.py` — 仪表盘后端路由。

它们都不是必需的；只包含你需要的部分即可。

### 清单参考 {#manifest-reference}

```json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "description": "What this plugin does",
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
| `name` | 是 | 唯一的插件标识符。小写，允许连字符。用于 URL 和注册。 |
| `label` | 是 | 导航标签页中显示的展示名称。 |
| `description` | 否 | 简短描述（显示在仪表盘管理界面中）。 |
| `icon` | 否 | Lucide 图标名称。默认为 `Puzzle`。未知名称会回退到 `Puzzle`。 |
| `version` | 否 | Semver 字符串。默认为 `0.0.0`。 |
| `tab.path` | 是 | 标签页的 URL 路径（例如 `/my-plugin`）。 |
| `tab.position` | 否 | 标签页的插入位置。`"end"`（默认）、`"after:&lt;path&gt;"` 或 `"before:&lt;path&gt;"` — 冒号后的值是目标标签页的 **路径段**（不带前导斜杠）。示例：`"after:skills"`、`"before:config"`。 |
| `tab.override` | 否 | 设置为内置路由路径（`"/"`、`"/sessions"`、`"/config"` 等）以 **替换** 该页面，而不是添加新标签页。参见 [替换内置页面](#replacing-built-in-pages-taboverride)。 |
| `tab.hidden` | 否 | 为 true 时，注册组件和任何插槽，但不在导航中添加标签页。用于仅插槽插件。参见 [仅插槽插件](#slot-only-plugins-tabhidden)。 |
| `slots` | 否 | 此插件填充的命名外壳插槽。**仅用于文档辅助** — 实际注册通过 JS 包中的 `registerSlot()` 完成。在此列出插槽可使发现界面信息更丰富。 |
| `entry` | 是 | 相对于 `dashboard/` 的 JS 包路径。默认为 `dist/index.js`。 |
| `css` | 否 | 要作为 `&lt;link&gt;` 标签注入的 CSS 文件路径。 |
| `api` | 否 | 包含 FastAPI 路由的 Python 文件路径。挂载在 `/api/plugins/&lt;name&gt;/` 下。 |
#### 可用图标 {#available-icons}

插件使用 Lucide 图标名称。仪表盘通过名称映射这些图标——未知名称会静默回退到 `Puzzle`。

当前已映射的图标：`Activity`、`BarChart3`、`Clock`、`Code`、`Database`、`Eye`、`FileText`、`Globe`、`Heart`、`KeyRound`、`MessageSquare`、`Package`、`Puzzle`、`Settings`、`Shield`、`Sparkles`、`Star`、`Terminal`、`Wrench`、`Zap`。

需要其他图标？请向 `web/src/App.tsx` 的 `ICON_MAP` 提交 PR——这纯粹是增量修改。

### 插件 SDK {#the-plugin-sdk}

插件所需的一切都挂在 `window.__HERMES_PLUGIN_SDK__` 上。插件不应直接导入 React。

```javascript
const SDK = window.__HERMES_PLUGIN_SDK__;

// React + 钩子
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
SDK.components.PluginSlot    // 渲染命名插槽（用于嵌套插件 UI）

// Hermes API 客户端 + 原始请求器
SDK.api                      // 类型化客户端 — getStatus、getSessions、getConfig 等
SDK.fetchJSON                // 用于自定义端点（插件注册的路由）的原始请求

// 工具函数
SDK.utils.cn                 // Tailwind 类合并器（clsx + twMerge）
SDK.utils.timeAgo            // 从 Unix 时间戳生成“5 分钟前”
SDK.utils.isoTimeAgo         // 从 ISO 字符串生成“5 分钟前”

// 钩子
SDK.useI18n                  // 用于多语言插件的国际化钩子
```

#### 调用插件后端 {#calling-your-plugin-s-backend}

```javascript
SDK.fetchJSON("/api/plugins/my-plugin/data")
  .then((data) => console.log(data))
  .catch((err) => console.error("API 调用失败：", err));
```

`fetchJSON` 会注入会话认证令牌，将错误作为抛出的异常呈现，并自动解析 JSON。

#### 调用内置 Hermes 端点 {#calling-built-in-hermes-endpoints}

```javascript
// Agent 状态
SDK.api.getStatus().then((s) => console.log("版本：", s.version));

// 最近会话
SDK.api.getSessions(10).then((resp) => console.log(resp.sessions.length));
```

完整列表请参见 [Web 仪表盘 → REST API](./web-dashboard#rest-api)。

### 外壳插槽 {#shell-slots}

插槽允许插件将组件注入应用外壳的指定位置——驾驶舱侧边栏、页眉、页脚、覆盖层——而无需占用整个标签页。多个插件可以填充同一个插槽；它们按注册顺序堆叠渲染。

在插件包内部注册：

```javascript
window.__HERMES_PLUGINS__.registerSlot("my-plugin", "sidebar", MySidebar);
window.__HERMES_PLUGINS__.registerSlot("my-plugin", "header-left", MyCrest);
```

#### 插槽目录 {#slot-catalogue}

**外壳级插槽**（在应用框架的任何位置渲染）：
| 插槽 | 位置 |
|------|----------|
| `backdrop` | 在 `&lt;Backdrop /&gt;` 层叠结构内部，位于噪点层之上。 |
| `header-left` | 在顶部栏的 Hermes 品牌标识之前。 |
| `header-right` | 在顶部栏的主题/语言切换器之前。 |
| `header-banner` | 导航栏下方的全宽横幅条。 |
| `sidebar` | 驾驶舱侧边栏轨道 — **仅在 `layoutVariant === "cockpit"` 时渲染**。 |
| `pre-main` | 路由出口上方（位于 `&lt;main&gt;` 内部）。 |
| `post-main` | 路由出口下方（位于 `&lt;main&gt;` 内部）。 |
| `footer-left` | 页脚单元格内容（替换默认内容）。 |
| `footer-right` | 页脚单元格内容（替换默认内容）。 |
| `overlay` | 固定定位层，位于所有内容之上。适用于 `customCSS` 无法单独实现的装饰效果（如扫描线、暗角）。 |

**页面级插槽**（仅在指定的内置页面上渲染 — 使用这些插槽可在现有页面中注入小部件、卡片或工具栏，而无需覆盖整个路由）：

| 插槽 | 渲染位置 |
|------|------------------|
| `sessions:top` / `sessions:bottom` | `/sessions` 页面的顶部/底部。 |
| `analytics:top` / `analytics:bottom` | `/analytics` 页面的顶部/底部。 |
| `logs:top` / `logs:bottom` | `/logs` 页面的顶部（筛选工具栏上方）/底部（日志查看器下方）。 |
| `cron:top` / `cron:bottom` | `/cron` 页面的顶部/底部。 |
| `skills:top` / `skills:bottom` | `/skills` 页面的顶部/底部。 |
| `config:top` / `config:bottom` | `/config` 页面的顶部/底部。 |
| `env:top` / `env:bottom` | `/env`（密钥）页面的顶部/底部。 |
| `docs:top` / `docs:bottom` | `/docs` 页面的顶部（iframe 上方）/底部。 |
| `chat:top` / `chat:bottom` | `/chat` 页面的顶部/底部（仅在启用嵌入式聊天时生效）。 |

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

如果插件仅用于增强现有页面，不需要自己的侧边栏标签，可以将页面级插槽与 `tab.hidden: true` 结合使用。

外壳仅会为上述插槽渲染 `&lt;PluginSlot name="..." /&gt;`。注册表会接受其他名称用于嵌套插件 UI — 插件可以通过 `SDK.components.PluginSlot` 暴露自己的插槽。

#### 重新注册与 HMR {#re-registration-and-hmr}

如果同一个 `(plugin, slot)` 对注册了两次，后一次调用会替换前一次 — 这与 React HMR 期望的插件重新挂载行为一致。

<a id="replacing-built-in-pages-tab-override"></a>
### 替换内置页面（`tab.override`） {#replacing-built-in-pages-taboverride}

将 `tab.override` 设置为内置路由路径，会使插件的组件替换该页面，而不是添加新标签。当主题想要自定义首页（`/`）但保持仪表盘其余部分不变时，这很有用。

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
当设置了 `override`：

- 位于 `/` 的原始页面组件会从路由中移除。
- 你的插件会在 `/` 处渲染。
- 不会为 `tab.path` 添加导航标签（因为 override 本身就是目的）。

每个路径只能被一个插件覆盖。如果两个插件声明了相同的 override，第一个生效，第二个会被忽略并在开发模式下给出警告。

如果你只需要在现有页面上添加一个卡片或工具栏，而不想完全接管该页面，请改用[页面级插槽](#augmenting-built-in-pages-page-scoped-slots)。

### 增强内置页面（页面级插槽） {#augmenting-built-in-pages-page-scoped-slots}

通过 `tab.override` 进行完全替换是一种重量级操作——你的插件现在拥有整个页面，包括我们未来对该页面的任何更新。大多数时候，你只是想在一个现有页面上添加一个横幅、卡片或工具栏。这就是**页面级插槽**的用途。

每个内置页面都会暴露 `&lt;page&gt;:top` 和 `&lt;page&gt;:bottom` 插槽，分别渲染在内容区域的顶部和底部。你的插件通过调用 `registerSlot()` 来填充这些插槽——内置页面保持正常工作，你的组件会与它一起渲染。

可用插槽：`sessions:*`、`analytics:*`、`logs:*`、`cron:*`、`skills:*`、`config:*`、`env:*`、`docs:*`、`chat:*`（每个都有 `:top` 和 `:bottom`）。完整目录请参见 [Shell 插槽 → 插槽目录](#slot-catalogue)。

最小示例——在 Sessions 页面顶部固定一个横幅：

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

  // 隐藏标签的占位符。
  window.__HERMES_PLUGINS__.register("session-notes", function () { return null; });

  // 真正的工作。
  window.__HERMES_PLUGINS__.registerSlot("session-notes", "sessions:top", Banner);
})();
```

关键点：

- `tab.hidden: true` 使插件不出现在侧边栏中——它没有独立的页面。
- `slots` 清单字段仅用于文档说明。实际的绑定发生在 JS 包中，通过 `registerSlot()` 完成。
- 多个插件可以声明同一个页面级插槽。它们会按照注册顺序堆叠渲染。
- 当没有插件注册时，零影响：内置页面完全像之前一样渲染。

捆绑的 `example-dashboard` 插件提供了一个实时演示，它会向 `sessions:top` 注入一个横幅——安装它即可端到端地看到这个模式。

<a id="slot-only-plugins-tab-hidden"></a>
### 仅插槽插件（`tab.hidden`） {#slot-only-plugins-tabhidden}

当 `tab.hidden: true` 时，插件会注册其组件（用于直接 URL 访问）以及任何插槽，但永远不会在导航中添加标签。用于那些仅为了注入到插槽而存在的插件——例如头部徽章、侧边栏 HUD、覆盖层。
```json
{
  "name": "header-crest",
  "label": "头部徽章",
  "tab": {
    "path": "/header-crest",
    "position": "end",
    "hidden": true
  },
  "slots": ["header-left"],
  "entry": "dist/index.js"
}
```

该 bundle 仍然使用占位组件调用 `register()`（以防有人直接访问 URL 的良好实践），然后调用 `registerSlot()` 完成实际工作。

### 后端 API 路由 {#backend-api-routes}

插件可以通过在 manifest 中设置 `api` 来注册 FastAPI 路由。创建文件并导出一个 `router`：

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

路由会被挂载到 `/api/plugins/&lt;name&gt;/` 下，因此上述路由变为：

- `GET  /api/plugins/my-plugin/data`
- `POST /api/plugins/my-plugin/action`

插件 API 路由会绕过会话令牌认证，因为仪表盘服务器默认绑定到 localhost。**如果你运行不受信任的插件，请不要使用 `--host 0.0.0.0` 将仪表盘暴露在公共接口上**——这些插件的路由也会变得可访问。

#### 访问 Hermes 内部 {#accessing-hermes-internals}

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

### 每个插件的自定义 CSS {#custom-css-per-plugin}

如果你的插件需要超出 Tailwind 类和内联 `style=` 的样式，可以添加一个 CSS 文件并在 manifest 中引用它：

```json
{
  "css": "dist/style.css"
}
```

该文件会在插件加载时以 `&lt;link&gt;` 标签的形式注入。使用特定的类名以避免与仪表盘样式冲突，并引用仪表盘的 CSS 变量以保持主题感知：

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

仪表盘暴露了所有 shadcn 令牌作为 `--color-*`，以及主题扩展（`--theme-asset-*`、`--component-&lt;bucket&gt;-*`、`--radius`、`--spacing-mul`）。引用这些变量，你的插件就会自动根据当前主题重新调整样式。

<a id="plugin-discovery-reload"></a>
### 插件发现与重载 {#plugin-discovery--reload}

仪表盘会扫描以下三个目录中的 `dashboard/manifest.json`：

| 优先级 | 目录 | 来源标签 |
|--------|------|----------|
| 1（冲突时优先） | `~/.hermes/plugins/&lt;name&gt;/dashboard/` | `user` |
| 2 | `&lt;repo&gt;/plugins/memory/&lt;name&gt;/dashboard/` | `bundled` |
| 2 | `&lt;repo&gt;/plugins/&lt;name&gt;/dashboard/` | `bundled` |
| 3 | `./.hermes/plugins/&lt;name&gt;/dashboard/` | `project` — 仅在设置了 `HERMES_ENABLE_PROJECT_PLUGINS` 时生效 |
发现结果会按仪表盘进程进行缓存。添加新插件后，请执行以下任一操作：

```bash
# 强制重新扫描，无需重启
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

……或重启 `hermes dashboard`。

#### 插件加载生命周期 {#plugin-load-lifecycle}

1. 仪表盘加载。`main.tsx` 将 SDK 暴露在 `window.__HERMES_PLUGIN_SDK__` 上，将注册表暴露在 `window.__HERMES_PLUGINS__` 上。
2. `App.tsx` 调用 `usePlugins()` → 获取 `GET /api/dashboard/plugins`。
3. 对于每个清单：注入 CSS `&lt;link&gt;`（如果声明），然后通过 `&lt;script&gt;` 标签加载 JS 包。
4. 插件的 IIFE 运行并调用 `window.__HERMES_PLUGINS__.register(name, Component)`，并可选择为每个插槽调用 `.registerSlot(name, slot, Component)`。
5. 仪表盘根据清单解析已注册的组件，将标签页添加到导航（除非 `hidden`），并将组件挂载为路由。

插件在其脚本加载后有 **2 秒** 时间来调用 `register()`。之后仪表盘停止等待并完成初始渲染。如果插件稍后注册，它仍然会显示——导航是响应式的。

如果插件的脚本加载失败（404、语法错误、IIFE 期间异常），仪表盘会在浏览器控制台记录警告并继续运行，忽略该插件。

---

<a id="combined-theme-plugin-demo"></a>
## 组合主题 + 插件演示 {#combined-theme--plugin-demo}

仓库中提供了 `plugins/strike-freedom-cockpit/` 作为完整的重新换肤演示。它将一个主题 YAML 与一个仅含插槽的插件配对，生成一个驾驶舱风格的 HUD，而无需分叉仪表盘。

**演示内容：**

- 一个完整的主题，使用了调色板、排版、`fontUrl`、`layoutVariant: cockpit`、`assets`、`componentStyles`（带缺口的卡片角、渐变背景）、`colorOverrides` 和 `customCSS`（扫描线叠加）。
- 一个仅含插槽的插件（`tab.hidden: true`），注册到三个插槽：
  - `sidebar` —— 一个 MS-STATUS 面板，带有由 `SDK.api.getStatus()` 驱动的实时遥测条。
  - `header-left` —— 一个派系徽章，从当前主题读取 `--theme-asset-crest`。
  - `footer-right` —— 一个自定义标语，替换默认的组织行。
- 该插件通过 CSS 变量读取主题提供的艺术作品，因此切换主题会更改英雄/徽章，而无需修改插件代码。

**安装：**

```bash
# 主题
cp plugins/strike-freedom-cockpit/theme/strike-freedom.yaml \
   ~/.hermes/dashboard-themes/

# 插件
cp -r plugins/strike-freedom-cockpit ~/.hermes/plugins/
```

打开仪表盘，从主题切换器中选择 **Strike Freedom**。驾驶舱侧边栏出现，徽章显示在页眉中，标语替换了页脚。切换回 **Hermes Teal**，插件仍然安装但不可见（`sidebar` 插槽仅在 `cockpit` 布局变体下渲染）。

阅读插件源代码（`plugins/strike-freedom-cockpit/dashboard/dist/index.js`），了解它如何读取 CSS 变量、如何防范不支持插槽的旧版仪表盘，以及如何从一个包中注册三个插槽。

---

## API 参考 {#api-reference}

### 主题端点 {#theme-endpoints}

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/themes` | GET | 列出可用主题 + 当前活动主题名称。内置主题返回 `{name, label, description}`；用户主题还包含一个 `definition` 字段，其中包含完整的规范化主题对象。 |
| `/api/dashboard/theme` | PUT | 设置活动主题。请求体：`{"name": "midnight"}`。持久化到 `config.yaml` 中的 `dashboard.theme` 下。 |
### 插件端点 {#plugin-endpoints}

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/plugins` | GET | 列出已发现的插件（包含清单，但排除内部字段）。 |
| `/api/dashboard/plugins/rescan` | GET | 强制重新扫描插件目录，无需重启。 |
| `/dashboard-plugins/&lt;name&gt;/&lt;path&gt;` | GET | 提供插件 `dashboard/` 目录中的静态资源。路径遍历已被阻止。 |
| `/api/plugins/&lt;name&gt;/*` | * | 插件注册的后端路由。 |

### `window` 上的 SDK {#sdk-on-window}

| 全局变量 | 类型 | 提供者 |
|--------|------|----------|
| `window.__HERMES_PLUGIN_SDK__` | object | `registry.ts` — React、hooks、UI 组件、API 客户端、工具函数。 |
| `window.__HERMES_PLUGINS__.register(name, Component)` | function | 注册插件的主组件。 |
| `window.__HERMES_PLUGINS__.registerSlot(name, slot, Component)` | function | 注册到指定的外壳插槽中。 |

---

## 故障排除 {#troubleshooting}

**我的主题没有出现在选择器中。**
检查文件是否位于 `~/.hermes/dashboard-themes/` 并且以 `.yaml` 或 `.yml` 结尾。刷新页面。运行 `curl http://127.0.0.1:9119/api/dashboard/themes` — 你的主题应该出现在响应中。如果 YAML 存在解析错误，仪表盘会将日志记录到 `~/.hermes/logs/` 下的 `errors.log` 中。

**我的插件标签页没有显示。**
1. 检查清单是否位于 `~/.hermes/plugins/&lt;name&gt;/dashboard/manifest.json`（注意 `dashboard/` 子目录）。
2. 运行 `curl http://127.0.0.1:9119/api/dashboard/plugins/rescan` 强制重新发现。
3. 打开浏览器开发者工具 → 网络 — 确认 `manifest.json`、`index.js` 以及任何 CSS 都已加载且没有 404 错误。
4. 打开浏览器开发者工具 → 控制台 — 查找 IIFE 期间的错误或 `window.__HERMES_PLUGINS__ is undefined`（表示 SDK 未初始化，通常是由于之前的 React 渲染崩溃）。
5. 验证你的打包文件是否使用与 `manifest.json:name` **相同的名称** 调用了 `window.__HERMES_PLUGINS__.register(...)`。

**插槽注册的组件没有渲染。**
`sidebar` 插槽仅在当前主题具有 `layoutVariant: cockpit` 时渲染。其他插槽始终渲染。如果你注册到一个没有命中的插槽，请在 `registerSlot` 内部添加 `console.log` 以确认插件打包文件确实运行了。

**插件后端路由返回 404。**
1. 确认清单中的 `"api": "plugin_api.py"` 指向 `dashboard/` 内的一个现有文件。
2. 重启 `hermes dashboard` — 插件 API 路由在启动时挂载一次，**不会**在重新扫描时挂载。
3. 检查 `plugin_api.py` 是否导出了一个模块级别的 `router = APIRouter()`。其他导出名称不会被识别。
4. 跟踪 `~/.hermes/logs/errors.log` 中的 `Failed to load plugin &lt;name&gt; API routes` — 导入错误会记录在那里。

**切换主题会清除我的颜色覆盖。**
`colorOverrides` 的作用域是当前主题，并在主题切换时被清除 — 这是设计使然。如果你希望覆盖持久化，请将它们放在主题的 YAML 中，而不是放在实时切换器中。

**主题 customCSS 被截断。**
每个主题的 `customCSS` 块大小限制为 32 KiB。将大型样式表拆分为多个主题，或者切换到通过其 `css` 字段注入完整样式表的插件（无大小限制）。
**我想在 PyPI 上发布一个插件。**  
Dashboard 插件是通过目录结构安装的，而不是通过 pip 入口点。目前最干净的发布方式是提供一个 git 仓库，让用户克隆到 `~/.hermes/plugins/` 目录下。目前尚未实现基于 pip 的 Dashboard 插件安装器。
