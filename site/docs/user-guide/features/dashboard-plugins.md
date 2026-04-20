---
sidebar_position: 16
title: "仪表板插件"
description: "为 Hermes 网页仪表板构建自定义标签页和扩展功能"
---

# 仪表板插件 {#dashboard-plugins}

仪表板插件允许你向网页仪表板添加自定义标签页。一个插件可以显示自己的用户界面、调用 Hermes API，并且可以选择性地注册后端端点——所有这些都无需修改仪表板的源代码。

## 快速开始 {#quick-start}

创建一个包含清单文件和 JS 文件的插件目录：

```bash
mkdir -p ~/.hermes/plugins/my-plugin/dashboard/dist
```

**manifest.json:**

```json
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

**dist/index.js:**

```javascript
(function () {
  var SDK = window.__HERMES_PLUGIN_SDK__;
  var React = SDK.React;
  var Card = SDK.components.Card;
  var CardHeader = SDK.components.CardHeader;
  var CardTitle = SDK.components.CardTitle;
  var CardContent = SDK.components.CardContent;

  function MyPage() {
    return React.createElement(Card, null,
      React.createElement(CardHeader, null,
        React.createElement(CardTitle, null, "My Plugin")
      ),
      React.createElement(CardContent, null,
        React.createElement("p", { className: "text-sm text-muted-foreground" },
          "Hello from my custom dashboard tab!"
        )
      )
    );
  }

  window.__HERMES_PLUGINS__.register("my-plugin", MyPage);
})();
```

刷新仪表板——你的标签页就会出现在导航栏中。

## 插件结构 {#plugin-structure}

插件位于标准的 `~/.hermes/plugins/` 目录内。仪表板扩展是一个 `dashboard/` 子文件夹：

```
~/.hermes/plugins/my-plugin/
  plugin.yaml              # 可选 — 现有的 CLI/网关插件清单
  __init__.py              # 可选 — 现有的 CLI/网关钩子
  dashboard/               # 仪表板扩展
    manifest.json          # 必需 — 标签页配置、图标、入口点
    dist/
      index.js             # 必需 — 预构建的 JS 包
      style.css            # 可选 — 自定义 CSS
    plugin_api.py          # 可选 — 后端 API 路由
```

一个插件可以同时从一个目录扩展 CLI/网关（通过 `plugin.yaml` + `__init__.py`）和仪表板（通过 `dashboard/`）。

## 清单参考 {#manifest-reference}

`manifest.json` 文件向仪表板描述你的插件：

```json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "description": "What this plugin does",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:skills"
  },
  "entry": "dist/index.js",
  "css": "dist/style.css",
  "api": "plugin_api.py"
}
```

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 唯一的插件标识符（小写，允许使用连字符） |
| `label` | 是 | 导航标签页中显示的展示名称 |
| `description` | 否 | 简短描述 |
| `icon` | 否 | Lucide 图标名称（默认：`Puzzle`） |
| `version` | 否 | Semver 版本字符串 |
| `tab.path` | 是 | 标签页的 URL 路径（例如 `/my-plugin`） |
| `tab.position` | 否 | 插入标签页的位置：`end`（默认）、`after:&lt;tab&gt;`、`before:&lt;tab&gt;` |
| `entry` | 是 | 相对于 `dashboard/` 的 JS 包路径 |
| `css` | 否 | 要注入的 CSS 文件路径 |
| `api` | 否 | 包含 FastAPI 路由的 Python 文件路径 |

### 标签页位置 {#tab-position}

`position` 字段控制你的标签页在导航栏中的显示位置：

- `"end"` — 在所有内置标签页之后（默认）
- `"after:skills"` — 在 Skills 标签页之后
- `"before:config"` — 在 Config 标签页之前
- `"after:cron"` — 在 Cron 标签页之后

冒号后面的值是目标标签页的路径片段（不带前导斜杠）。

### 可用图标 {#available-icons}

插件可以使用以下任意 Lucide 图标名称：

`Activity`, `BarChart3`, `Clock`, `Code`, `Database`, `Eye`, `FileText`, `Globe`, `Heart`, `KeyRound`, `MessageSquare`, `Package`, `Puzzle`, `Settings`, `Shield`, `Sparkles`, `Star`, `Terminal`, `Wrench`, `Zap`

无法识别的图标名称将回退到 `Puzzle`。

## 插件 SDK {#plugin-sdk}

插件不捆绑 React 或 UI 组件——它们使用 `window.__HERMES_PLUGIN_SDK__` 上暴露的 SDK。这避免了版本冲突，并保持插件包体积小巧。
### SDK 内容 {#sdk-contents}

```javascript
var SDK = window.__HERMES_PLUGIN_SDK__;

// React
SDK.React              // React 实例
SDK.hooks.useState     // React hooks
SDK.hooks.useEffect
SDK.hooks.useCallback
SDK.hooks.useMemo
SDK.hooks.useRef
SDK.hooks.useContext
SDK.hooks.createContext

// API
SDK.api                // Hermes API 客户端 (getStatus, getSessions 等)
SDK.fetchJSON          // 用于自定义端点的原始 fetch — 自动处理认证

// UI 组件 (shadcn/ui 风格)
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

// 工具函数
SDK.utils.cn           // Tailwind 类合并器 (clsx + twMerge)
SDK.utils.timeAgo      // 从 Unix 时间戳生成 "5分钟前"
SDK.utils.isoTimeAgo   // 从 ISO 字符串生成 "5分钟前"

// Hooks
SDK.useI18n            // i18n 翻译
SDK.useTheme           // 当前主题信息
```

### 使用 SDK.fetchJSON {#using-sdk-fetchjson}

用于调用你插件的后端 API 端点：

```javascript
SDK.fetchJSON("/api/plugins/my-plugin/data")
  .then(function (result) {
    console.log(result);
  })
  .catch(function (err) {
    console.error("API 调用失败:", err);
  });
```

`fetchJSON` 会自动注入会话认证令牌、处理错误并解析 JSON。

### 使用现有的 API 方法 {#using-existing-api-methods}

`SDK.api` 对象包含了所有内置 Hermes 端点的方法：

```javascript
// 获取 Agent 状态
SDK.api.getStatus().then(function (status) {
  console.log("版本:", status.version);
});

// 列出会话
SDK.api.getSessions(10).then(function (resp) {
  console.log("会话数量:", resp.sessions.length);
});
```

## 后端 API 路由 {#backend-api-routes}

插件可以通过在清单中设置 `api` 字段来注册 FastAPI 路由。创建一个导出 `router` 的 Python 文件：

```python
# plugin_api.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/data")
async def get_data():
    return {"items": ["one", "two", "three"]}

@router.post("/action")
async def do_action(body: dict):
    return {"ok": True, "received": body}
```

路由会被挂载到 `/api/plugins/&lt;name&gt;/` 下，因此上面的例子会变成：
- `GET /api/plugins/my-plugin/data`
- `POST /api/plugins/my-plugin/action`

插件 API 路由会绕过会话令牌认证，因为仪表板服务器只绑定到 localhost。

### 访问 Hermes 内部组件 {#accessing-hermes-internals}

后端路由可以从 hermes-agent 代码库中导入：

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
```

## 自定义 CSS {#custom-css}

如果你的插件需要自定义样式，可以添加一个 CSS 文件并在清单中引用它：

```json
{
  "css": "dist/style.css"
}
```

CSS 文件会在插件加载时作为 `&lt;link&gt;` 标签注入。请使用特定的类名，以避免与仪表板现有样式冲突。

```css
/* dist/style.css */
.my-plugin-chart {
  border: 1px solid var(--color-border);
  background: var(--color-card);
  padding: 1rem;
}
```

你可以使用仪表板的 CSS 自定义属性（例如 `--color-border`、`--color-foreground`）来匹配当前主题。

## 插件加载流程 {#plugin-loading-flow}

1.  仪表板加载 — `main.tsx` 将 SDK 暴露在 `window.__HERMES_PLUGIN_SDK__` 上
2.  `App.tsx` 调用 `usePlugins()`，该函数会获取 `GET /api/dashboard/plugins`
3.  对于每个插件：注入 CSS `&lt;link&gt;`（如果已声明），加载 JS `&lt;script&gt;`
4.  插件 JS 调用 `window.__HERMES_PLUGINS__.register(name, Component)`
5.  仪表板将标签页添加到导航栏，并将组件作为路由挂载

插件在其脚本加载后有最多 2 秒的时间进行注册。如果插件加载失败，仪表板会继续运行而不加载它。
## 插件发现 {#plugin-discovery}

仪表盘会扫描以下目录中的 `dashboard/manifest.json` 文件：

1.  **用户插件：** `~/.hermes/plugins/&lt;name&gt;/dashboard/manifest.json`
2.  **内置插件：** `&lt;repo&gt;/plugins/&lt;name&gt;/dashboard/manifest.json`
3.  **项目插件：** `./.hermes/plugins/&lt;name&gt;/dashboard/manifest.json`（仅在设置了 `HERMES_ENABLE_PROJECT_PLUGINS` 环境变量时生效）

用户插件具有最高优先级——如果同一个插件名称出现在多个来源中，以用户版本为准。

在添加新插件后，若想在不重启服务器的情况下强制重新扫描，可以执行：

```bash
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

## 插件 API 端点 {#plugin-api-endpoints}

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/plugins` | GET | 列出已发现的插件 |
| `/api/dashboard/plugins/rescan` | GET | 强制重新扫描新插件 |
| `/dashboard-plugins/&lt;name&gt;/&lt;path&gt;` | GET | 提供插件的静态资源 |
| `/api/plugins/&lt;name&gt;/*` | * | 插件注册的 API 路由 |

## 示例插件 {#example-plugin}

代码仓库中包含一个示例插件，位于 `plugins/example-dashboard/`，它演示了：

- 使用 SDK 组件（Card、Badge、Button）
- 调用后端 API 路由
- 通过 `window.__HERMES_PLUGINS__.register()` 进行注册

要尝试它，请运行 `hermes dashboard` —— 在 Skills 标签页之后会出现一个 "Example" 标签页。

## 提示 {#tips}

- **无需构建步骤** —— 编写纯 JavaScript IIFE 即可。如果你更喜欢 JSX，可以使用任何打包工具（如 esbuild、Vite、webpack），将 React 作为外部依赖，并输出 IIFE 格式。
- **保持包体积小巧** —— React 和所有 UI 组件都由 SDK 提供。你的包应该只包含插件自身的逻辑。
- **使用主题变量** —— 在 CSS 中引用 `var(--color-*)` 变量，可以自动匹配用户选择的任何主题。
- **本地测试** —— 运行 `hermes dashboard --no-open`，并使用浏览器开发者工具来验证你的插件是否正确加载和注册。
