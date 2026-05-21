---
title: "热门网页设计 — 54 个真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS"
sidebar_label: "热门网页设计"
description: "54 个真实设计系统（Stripe、Linear、Vercel）以 HTML/CSS 形式提供"
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="popular-web-designs"></a>
# 热门网页设计

54 个真实设计系统（Stripe、Linear、Vercel）以 HTML/CSS 形式提供。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/popular-web-designs` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Teknium（设计系统来源于 VoltAgent/awesome-design-md） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下为 Hermes 在该技能被触发时加载的完整技能定义。当技能激活时，Agent 将看到这些指令。
:::

# 热门网页设计

54 个真实世界的设计系统，可用于生成 HTML/CSS。每个模板捕获了一个网站完整的视觉语言：调色板、排版层级、组件样式、间距系统、阴影、响应式行为，以及包含精确 CSS 值的实用 Agent 提示。

<a id="related-design-skills"></a>
## 相关设计技能

- **`claude-design`** — 用于设计*流程与品味*（范围界定 brief、生成变体、验证本地 HTML 制品、避免 AI 设计的“垃圾味”）。当用户希望按照某个知名品牌风格精心设计页面时，可将此技能与 `claude-design` 搭配使用：`claude-design` 驱动工作流程，本技能提供视觉词汇。
- **`design-md`** — 当交付物是正式的 DESIGN.md 令牌规范文件而非渲染后的制品时使用。

<a id="how-to-use"></a>
## 如何使用

1. 从下方目录中选择一个设计
2. 加载它：`skill_view(name="popular-web-designs", file_path="templates/&lt;site&gt;.md")`
3. 生成 HTML 时使用设计令牌和组件规范
4. 搭配 `generative-widgets` 技能，通过 cloudflared 隧道提供结果

每个模板顶部都包含一个 **Hermes 实现说明** 区块，其中包含：
- CDN 字体替代方案和 Google Fonts `&lt;link&gt;` 标签（可直接粘贴）
- 主字体和等宽字体的 CSS font-family 堆叠
- 使用 `write_file` 创建 HTML 以及使用 `browser_vision` 进行验证的提醒

<a id="html-generation-pattern"></a>
## HTML 生成模式

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
  <!-- 从模板的 Hermes 说明中粘贴 Google Fonts <link> -->
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>
    /* 将模板的调色板应用为 CSS 自定义属性 */
    :root {
      --color-bg: #ffffff;
      --color-text: #171717;
      --color-accent: #533afd;
      /* ... 更多来自模板第2节的内容 */
    }
    /* 应用来自模板第3节的排版 */
    body {
      font-family: 'Inter', system-ui, sans-serif;
      color: var(--color-text);
      background: var(--color-bg);
    }
    /* 应用来自模板第4节的组件样式 */
    /* 应用来自模板第5节的布局 */
    /* 应用来自模板第6节的阴影 */
  </style>
</head>
<body>
  <!-- 根据模板中的组件规格构建 -->
</body>
</html>
```
用 `write_file` 写入文件，通过 `generative-widgets` 工作流（cloudflared 隧道）提供服务，并用 `browser_vision` 验证结果以确保视觉准确性。

<a id="font-substitution-reference"></a>
## 字体替代参考

大多数网站使用专有字体，无法通过 CDN 获取。每个模板都会映射到一个 Google Fonts 替代字体，以保持设计风格。常见映射如下：

| 专有字体 | CDN 替代字体 | 风格特征 |
|---|---|---|
| Geist / Geist Sans | Geist（在 Google Fonts 上） | 几何风格，压缩字距 |
| Geist Mono | Geist Mono（在 Google Fonts 上） | 清晰等宽，连字 |
| sohne-var (Stripe) | Source Sans 3 | 轻量优雅 |
| Berkeley Mono | JetBrains Mono | 技术等宽 |
| Airbnb Cereal VF | DM Sans | 圆润友好几何体 |
| Circular (Spotify) | DM Sans | 几何风格，温暖 |
| figmaSans | Inter | 清晰人文主义 |
| Pin Sans (Pinterest) | DM Sans | 友好，圆润 |
| NVIDIA-EMEA | Inter（或 Arial 系统） | 工业感，清晰 |
| CoinbaseDisplay/Sans | DM Sans | 几何风格，可信赖 |
| UberMove | DM Sans | 粗体，紧凑 |
| HashiCorp Sans | Inter | 企业级，中性 |
| waldenburgNormal (Sanity) | Space Grotesk | 几何风格，略紧凑 |
| IBM Plex Sans/Mono | IBM Plex Sans/Mono | 可在 Google Fonts 上获取 |
| Rubik (Sentry) | Rubik | 可在 Google Fonts 上获取 |

当模板的 CDN 字体与原始字体匹配时（Inter、IBM Plex、Rubik、Geist），不存在替代损失。当使用替代字体时（DM Sans 替代 Circular，Source Sans 3 替代 sohne-var），请严格遵循模板的字重、字号和字间距值——这些比具体的字体更能体现视觉风格。

<a id="design-catalog"></a>
## 设计目录

<a id="ai-machine-learning"></a>
### AI 与机器学习

| 模板 | 网站 | 风格 |
|---|---|---|
| `claude.md` | Anthropic Claude | 暖色陶土强调，干净编辑布局 |
| `cohere.md` | Cohere | 鲜艳渐变，数据丰富的仪表盘美学 |
| `elevenlabs.md` | ElevenLabs | 暗色调电影化 UI，音频波形美学 |
| `minimax.md` | Minimax | 粗体暗色界面，霓虹点缀 |
| `mistral.ai.md` | Mistral AI | 法式工程极简主义，紫色调 |
| `ollama.md` | Ollama | 终端优先，单色简洁 |
| `opencode.ai.md` | OpenCode AI | 面向开发者的暗色主题，全等宽 |
| `replicate.md` | Replicate | 清爽白色画布，代码优先 |
| `runwayml.md` | RunwayML | 电影化暗色 UI，多媒体丰富布局 |
| `together.ai.md` | Together AI | 技术型，蓝图风格设计 |
| `voltagent.md` | VoltAgent | 虚无黑画布，翡翠绿强调，终端原生态 |
| `x.ai.md` | xAI | 鲜明单色，未来极简，全等宽 |

<a id="developer-tools-platforms"></a>
### 开发者工具与平台

| 模板 | 网站 | 风格 |
|---|---|---|
| `cursor.md` | Cursor | 光滑暗色界面，渐变点缀 |
| `expo.md` | Expo | 暗色主题，紧凑字距，以代码为中心 |
| `linear.app.md` | Linear | 超极小暗色模式，精确，紫色强调 |
| `lovable.md` | Lovable | 俏皮渐变，友好开发美学 |
| `mintlify.md` | Mintlify | 清爽，绿色强调，优化阅读 |
| `posthog.md` | PostHog | 俏皮品牌，开发者友好暗色 UI |
| `raycast.md` | Raycast | 光滑暗色铬质，鲜艳渐变点缀 |
| `resend.md` | Resend | 极小暗色主题，等宽强调 |
| `sentry.md` | Sentry | 暗色仪表盘，数据密集，粉紫强调 |
| `supabase.md` | Supabase | 暗色翡翠主题，代码优先开发者工具 |
| `superhuman.md` | Superhuman | 高级暗色 UI，键盘优先，紫色辉光 |
| `vercel.md` | Vercel | 黑白精确，Geist 字体系统 |
| `warp.md` | Warp | 暗色 IDE 风格界面，基于块的命令 UI |
| `zapier.md` | Zapier | 温暖橙色，友好插画驱动 |
<a id="infrastructure-cloud"></a>
### 基础设施与云服务

| 模板 | 网站 | 风格 |
|---|---|---|
| `clickhouse.md` | ClickHouse | 黄色强调色，技术文档风格 |
| `composio.md` | Composio | 现代深色搭配彩色集成图标 |
| `hashicorp.md` | HashiCorp | 企业级简洁，黑白配色 |
| `mongodb.md` | MongoDB | 绿叶品牌标识，侧重开发者文档 |
| `sanity.md` | Sanity | 红色强调，内容优先的编辑布局 |
| `stripe.md` | Stripe | 标志性紫色渐变，300字重优雅感 |

<a id="design-productivity"></a>
### 设计与效率

| 模板 | 网站 | 风格 |
|---|---|---|
| `airtable.md` | Airtable | 色彩丰富、友好，结构化数据美学 |
| `cal.md` | Cal.com | 干净中性 UI，面向开发者的简洁 |
| `clay.md` | Clay | 有机形状、柔和渐变、艺术指导型布局 |
| `figma.md` | Figma | 多彩活泼，专业又俏皮 |
| `framer.md` | Framer | 大胆黑蓝配色，动效优先，设计前卫 |
| `intercom.md` | Intercom | 友好蓝色调，对话式 UI 模式 |
| `miro.md` | Miro | 亮黄色强调色，无限画布美学 |
| `notion.md` | Notion | 温暖极简主义，衬线标题，柔和表面 |
| `pinterest.md` | Pinterest | 红色强调色，瀑布流网格，图片优先布局 |
| `webflow.md` | Webflow | 蓝色强调色，精致的营销网站美学 |

<a id="fintech-crypto"></a>
### 金融科技与加密货币

| 模板 | 网站 | 风格 |
|---|---|---|
| `coinbase.md` | Coinbase | 干净蓝色形象，专注信任，机构感 |
| `kraken.md` | Kraken | 紫色强调的深色 UI，数据密集仪表盘 |
| `revolut.md` | Revolut | 时尚深色界面，渐变卡片，金融科技精准度 |
| `wise.md` | Wise | 亮绿色强调色，友好清晰 |

<a id="enterprise-consumer"></a>
### 企业与消费

| 模板 | 网站 | 风格 |
|---|---|---|
| `airbnb.md` | Airbnb | 暖珊瑚强调色，摄影驱动，圆角 UI |
| `apple.md` | Apple | 高级留白，SF Pro 字体，电影感图像 |
| `bmw.md` | BMW | 深色高级表面，精密工程美学 |
| `ibm.md` | IBM | Carbon 设计系统，结构化的蓝色调 |
| `nvidia.md` | NVIDIA | 绿黑能量，技术力量美学 |
| `spacex.md` | SpaceX | 鲜明黑白，出血图像，未来感 |
| `spotify.md` | Spotify | 深色背景上的鲜艳绿，粗体字体，专辑封面驱动 |
| `uber.md` | Uber | 大胆黑白，紧凑字体，都市能量 |

<a id="choosing-a-design"></a>
## 如何选择设计

根据内容匹配设计：

- **开发者工具 / 仪表盘：** Linear、Vercel、Supabase、Raycast、Sentry
- **文档 / 内容站点：** Mintlify、Notion、Sanity、MongoDB
- **营销 / 落地页：** Stripe、Framer、Apple、SpaceX
- **深色模式 UI：** Linear、Cursor、ElevenLabs、Warp、Superhuman
- **明亮 / 干净 UI：** Vercel、Stripe、Notion、Cal.com、Replicate
- **俏皮 / 友好：** PostHog、Figma、Lovable、Zapier、Miro
- **高级 / 奢华：** Apple、BMW、Stripe、Superhuman、Revolut
- **数据密集 / 仪表盘：** Sentry、Kraken、Cohere、ClickHouse
- **等宽 / 终端美学：** Ollama、OpenCode、x.ai、VoltAgent
