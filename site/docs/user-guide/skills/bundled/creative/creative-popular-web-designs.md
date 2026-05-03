---
title: "热门网页设计 — 54 套真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS 实现"
sidebar_label: "热门网页设计"
description: "54 套真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS 实现"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 热门网页设计 {#popular-web-designs}

54 套真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS 实现。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/popular-web-designs` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Teknium（设计系统来源于 VoltAgent/awesome-design-md） |
| 许可证 | MIT |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

<a id="popular-web-designs"></a>
# 热门网页设计

54 套真实世界的设计系统，可直接用于生成 HTML/CSS。每个模板都捕捉了网站的完整视觉语言：调色板、排版层级、组件样式、间距系统、阴影、响应式行为，以及包含精确 CSS 值的实用 Agent 提示。

## 相关设计技能 {#related-design-skills}

- **`claude-design`** — 用于设计的*流程与品味*（确定需求范围、生成变体、验证本地 HTML 产物、避免 AI 设计中的粗糙感）。当用户希望页面经过深思熟虑的设计，并模仿某个知名品牌风格时，可将此技能与 `claude-design` 搭配使用：`claude-design` 驱动工作流程，此技能提供视觉词汇。
- **`design-md`** — 当交付物是正式的 DESIGN.md 令牌规范文件，而非渲染产物时使用。

## 使用方法 {#how-to-use}

1. 从下方目录中选择一个设计
2. 加载它：`skill_view(name="popular-web-designs", file_path="templates/&lt;site&gt;.md")`
3. 在生成 HTML 时使用设计令牌和组件规范
4. 搭配 `generative-widgets` 技能，通过 cloudflared 隧道提供结果

每个模板顶部都包含一个 **Hermes 实现说明** 区块，其中包含：
- CDN 字体替代方案和 Google Fonts `&lt;link&gt;` 标签（可直接粘贴）
- 主要字体和等宽字体的 CSS font-family 堆栈
- 使用 `write_file` 创建 HTML 和使用 `browser_vision` 进行验证的提醒

## HTML 生成模式 {#html-generation-pattern}

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>页面标题</title>
  <!-- 从模板的 Hermes 说明中粘贴 Google Fonts 的 <link> 标签 -->
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>
    /* 将模板的调色板应用为 CSS 自定义属性 */
    :root {
      --color-bg: #ffffff;
      --color-text: #171717;
      --color-accent: #533afd;
      /* ... 更多来自模板第 2 节的内容 */
    }
    /* 应用模板第 3 节的排版 */
    body {
      font-family: 'Inter', system-ui, sans-serif;
      color: var(--color-text);
      background: var(--color-bg);
    }
    /* 应用模板第 4 节的组件样式 */
    /* 应用模板第 5 节的布局 */
    /* 应用模板第 6 节的阴影 */
  </style>
</head>
<body>
  <!-- 使用模板中的组件规范进行构建 -->
</body>
</html>
```
使用 `write_file` 写入文件，通过 `generative-widgets` 工作流（cloudflared 隧道）提供服务，并用 `browser_vision` 验证结果，确保视觉准确。

## 字体替换参考 {#font-substitution-reference}

大多数网站使用专有字体，无法通过 CDN 获取。每个模板都映射了一个 Google Fonts 替代字体，以保留设计风格。常见映射如下：

| 专有字体 | CDN 替代字体 | 风格特征 |
|---|---|---|
| Geist / Geist Sans | Geist（在 Google Fonts 上） | 几何风格，紧凑字间距 |
| Geist Mono | Geist Mono（在 Google Fonts 上） | 干净等宽，连字 |
| sohne-var（Stripe） | Source Sans 3 | 轻量优雅 |
| Berkeley Mono | JetBrains Mono | 技术等宽 |
| Airbnb Cereal VF | DM Sans | 圆润友好几何体 |
| Circular（Spotify） | DM Sans | 几何，温暖 |
| figmaSans | Inter | 干净人文主义 |
| Pin Sans（Pinterest） | DM Sans | 友好，圆润 |
| NVIDIA-EMEA | Inter（或 Arial 系统） | 工业感，干净 |
| CoinbaseDisplay/Sans | DM Sans | 几何，可信赖 |
| UberMove | DM Sans | 粗体，紧凑 |
| HashiCorp Sans | Inter | 企业级，中性 |
| waldenburgNormal（Sanity） | Space Grotesk | 几何，略微压缩 |
| IBM Plex Sans/Mono | IBM Plex Sans/Mono | 可在 Google Fonts 上获取 |
| Rubik（Sentry） | Rubik | 可在 Google Fonts 上获取 |

当模板的 CDN 字体与原始字体一致（Inter、IBM Plex、Rubik、Geist）时，不会产生替换损失。当使用替代字体时（如用 DM Sans 替代 Circular，用 Source Sans 3 替代 sohne-var），请严格遵循模板的字重、字号和字间距值——这些比具体字体更能体现视觉特征。

## 设计目录 {#design-catalog}

### AI 与机器学习 {#ai-machine-learning}

| 模板 | 站点 | 风格 |
|---|---|---|
| `claude.md` | Anthropic Claude | 温暖陶土色强调，干净编辑布局 |
| `cohere.md` | Cohere | 鲜艳渐变，数据丰富的仪表盘美学 |
| `elevenlabs.md` | ElevenLabs | 深色电影感 UI，音频波形美学 |
| `minimax.md` | Minimax | 大胆深色界面，霓虹强调 |
| `mistral.ai.md` | Mistral AI | 法式极简主义，紫色调 |
| `ollama.md` | Ollama | 终端优先，单色简洁 |
| `opencode.ai.md` | OpenCode AI | 开发者导向深色主题，全等宽 |
| `replicate.md` | Replicate | 干净白色画布，代码优先 |
| `runwayml.md` | RunwayML | 电影感深色 UI，媒体丰富布局 |
| `together.ai.md` | Together AI | 技术感，蓝图风格设计 |
| `voltagent.md` | VoltAgent | 虚空黑画布，翡翠绿强调，终端原生 |
| `x.ai.md` | xAI | 鲜明单色，未来主义极简，全等宽 |

### 开发者工具与平台 {#developer-tools-platforms}

| 模板 | 站点 | 风格 |
|---|---|---|
| `cursor.md` | Cursor | 流畅深色界面，渐变强调 |
| `expo.md` | Expo | 深色主题，紧凑字间距，代码中心 |
| `linear.app.md` | Linear | 超极简深色模式，精准，紫色强调 |
| `lovable.md` | Lovable | 俏皮渐变，友好开发者美学 |
| `mintlify.md` | Mintlify | 干净，绿色强调，阅读优化 |
| `posthog.md` | PostHog | 俏皮品牌，开发者友好深色 UI |
| `raycast.md` | Raycast | 流畅深色镀铬，鲜艳渐变强调 |
| `resend.md` | Resend | 极简深色主题，等宽强调 |
| `sentry.md` | Sentry | 深色仪表盘，数据密集，粉紫强调 |
| `supabase.md` | Supabase | 深翡翠绿主题，代码优先开发者工具 |
| `superhuman.md` | Superhuman | 高级深色 UI，键盘优先，紫色光晕 |
| `vercel.md` | Vercel | 黑白精准，Geist 字体系统 |
| `warp.md` | Warp | 深色 IDE 风格界面，基于块的命令 UI |
| `zapier.md` | Zapier | 温暖橙色，友好插画驱动 |
### 基础设施与云服务 {#infrastructure-cloud}

| 模板 | 站点 | 风格 |
|---|---|---|
| `clickhouse.md` | ClickHouse | 黄色强调色，技术文档风格 |
| `composio.md` | Composio | 现代深色搭配彩色集成图标 |
| `hashicorp.md` | HashiCorp | 企业级简洁，黑白配色 |
| `mongodb.md` | MongoDB | 绿叶品牌标识，专注开发者文档 |
| `sanity.md` | Sanity | 红色强调色，内容优先的编辑布局 |
| `stripe.md` | Stripe | 标志性紫色渐变，300字重优雅感 |

### 设计与生产力 {#design-productivity}

| 模板 | 站点 | 风格 |
|---|---|---|
| `airtable.md` | Airtable | 色彩丰富、友好，结构化数据美学 |
| `cal.md` | Cal.com | 干净中性UI，面向开发者的简洁性 |
| `clay.md` | Clay | 有机形状，柔和渐变，艺术导向布局 |
| `figma.md` | Figma | 鲜艳多彩，有趣又专业 |
| `framer.md` | Framer | 大胆黑蓝配色，动效优先，设计前沿 |
| `intercom.md` | Intercom | 友好蓝色调，对话式UI模式 |
| `miro.md` | Miro | 亮黄色强调色，无限画布美学 |
| `notion.md` | Notion | 温暖极简主义，衬线标题，柔和表面 |
| `pinterest.md` | Pinterest | 红色强调色，瀑布流网格，图片优先布局 |
| `webflow.md` | Webflow | 蓝色强调色，精致营销网站美学 |

### 金融科技与加密货币 {#fintech-crypto}

| 模板 | 站点 | 风格 |
|---|---|---|
| `coinbase.md` | Coinbase | 干净蓝色品牌形象，注重信任，机构感 |
| `kraken.md` | Kraken | 紫色强调的深色UI，数据密集仪表盘 |
| `revolut.md` | Revolut | 时尚深色界面，渐变卡片，金融科技精准感 |
| `wise.md` | Wise | 亮绿色强调色，友好清晰 |

### 企业级与消费级 {#enterprise-consumer}

| 模板 | 站点 | 风格 |
|---|---|---|
| `airbnb.md` | Airbnb | 温暖珊瑚色强调，摄影驱动，圆角UI |
| `apple.md` | Apple | 高级留白，SF Pro字体，电影感图像 |
| `bmw.md` | BMW | 深色高级表面，精密工程美学 |
| `ibm.md` | IBM | Carbon设计系统，结构化蓝色调 |
| `nvidia.md` | NVIDIA | 绿黑能量感，技术力量美学 |
| `spacex.md` | SpaceX | 极致黑白，全出血图像，未来感 |
| `spotify.md` | Spotify | 深色背景上的鲜艳绿色，粗体字体，专辑封面驱动 |
| `uber.md` | Uber | 大胆黑白，紧凑字体，都市活力 |

## 选择设计 {#choosing-a-design}

根据内容匹配设计：

- **开发者工具 / 仪表盘：** Linear、Vercel、Supabase、Raycast、Sentry
- **文档 / 内容站点：** Mintlify、Notion、Sanity、MongoDB
- **营销 / 落地页：** Stripe、Framer、Apple、SpaceX
- **深色模式UI：** Linear、Cursor、ElevenLabs、Warp、Superhuman
- **浅色 / 干净UI：** Vercel、Stripe、Notion、Cal.com、Replicate
- **有趣 / 友好：** PostHog、Figma、Lovable、Zapier、Miro
- **高级 / 奢华：** Apple、BMW、Stripe、Superhuman、Revolut
- **数据密集 / 仪表盘：** Sentry、Kraken、Cohere、ClickHouse
- **等宽字体 / 终端美学：** Ollama、OpenCode、x.ai、VoltAgent
