---
title: "Page Agent"
sidebar_label: "Page Agent"
description: "将 alibaba/page-agent 嵌入你自己的 Web 应用程序——这是一个纯 JavaScript 的页面内 GUI Agent，以单个 &lt;script&gt; 标签或 npm 包的形式发布，让你的网站最终用户能够用自然语言驱动界面（例如“点击登录，在用户名处填入 John”）。无需 Python、无头浏览器或扩展。当用户是希望为其 SaaS / 管理面板 / B2B 工具添加 AI 协同助手、让旧版 Web 应用支持自然语言交互、或者想用本地（Ollama）或云端（Qwen / OpenAI / OpenRouter）LLM 评估 page-agent 的 Web 开发者时，可使用此技能。不适用于服务端浏览器自动化——这类需求请引导用户使用 Hermes 内置的浏览器工具。"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，不要编辑本页面。 */}

<a id="page-agent"></a>
# Page Agent

将 alibaba/page-agent 嵌入你自己的 Web 应用程序——这是一个纯 JavaScript 的页面内 GUI Agent，以单个 &lt;script&gt; 标签或 npm 包的形式发布，让你的网站最终用户能够用自然语言驱动界面（例如“点击登录，在用户名处填入 John”）。无需 Python、无头浏览器或扩展。当用户是希望为其 SaaS / 管理面板 / B2B 工具添加 AI 协同助手、让旧版 Web 应用支持自然语言交互、或者想用本地（Ollama）或云端（Qwen / OpenAI / OpenRouter）LLM 评估 page-agent 的 Web 开发者时，可使用此技能。不适用于服务端浏览器自动化——这类需求请引导用户使用 Hermes 内置的浏览器工具。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选——使用 `hermes skills install official/web-development/page-agent` 安装 |
| 路径 | `optional-skills/web-development/page-agent` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `web`, `javascript`, `agent`, `browser`, `gui`, `alibaba`, `embed`, `copilot`, `saas` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# page-agent

alibaba/page-agent（https://github.com/alibaba/page-agent，17k+ 星，MIT 许可证）是一个用 TypeScript 编写的页面内 GUI Agent。它位于网页内部，以文本形式读取 DOM（无需截图，无需多模态 LLM），并根据当前页面执行自然语言指令，例如“点击登录按钮，然后在用户名处填入 John”。纯客户端——宿主网站只需包含一个脚本并传递一个兼容 OpenAI 的 LLM 端点即可。

<a id="when-to-use-this-skill"></a>
## 何时使用此技能

当用户想要以下内容时加载此技能：

- **在自己的 Web 应用中交付 AI 协同助手**（SaaS、管理面板、B2B 工具、ERP、CRM）——“我的仪表盘用户应该能够输入‘为 Acme Corp 创建发票并发送邮件’，而不是点击五个屏幕”
- **在不重写前端的情况下现代化旧版 Web 应用**——page-agent 直接覆盖在现有 DOM 之上
- **通过自然语言增强无障碍性**——语音/屏幕阅读器用户通过描述他们想要的内容来驱动界面
- **使用本地（Ollama）或托管（Qwen、OpenAI、OpenRouter）LLM 演示或评估 page-agent**
- **构建交互式培训/产品演示**——让 AI 在真实界面中实时引导用户“如何提交费用报告”

<a id="when-not-to-use-this-skill"></a>
## 何时不使用此技能

- 用户希望 **Hermes 本身来驱动浏览器** → 使用 Hermes 内置的浏览器工具（Browserbase / Camofox）。page-agent 是*相反*的方向。
- 用户希望 **跨标签页自动化而不嵌入** → 使用 Playwright、browser-use 或 page-agent Chrome 扩展
- 用户需要 **视觉定位/截图** → page-agent 仅支持文本 DOM；请改用多模态浏览器 Agent
<a id="prerequisites"></a>
## 前提条件

- Node 22.13+ 或 24+, npm 10+（官方文档说需要 11+，但 10.9 也能正常工作）
- 兼容 OpenAI 的 LLM 端点：Qwen（DashScope）、OpenAI、Ollama、OpenRouter，或任何能使用 `/v1/chat/completions` 接口的服务
- 带有开发者工具的浏览器（用于调试）

<a id="path-1-30-second-demo-via-cdn-no-install"></a>
## 路径 1 — 通过 CDN 实现 30 秒演示（无需安装）

体验效果的最快方式。使用阿里巴巴的免费测试 LLM 代理——**仅用于评估**，需遵守其条款。

添加到任意 HTML 页面（或作为书签小工具粘贴到开发者工具控制台中）：

```html
<script src="https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js" crossorigin="true"></script>
```

随后会出现一个面板。输入指令即可运行。

书签小工具形式（拖到书签栏，在任意页面上点击即可使用）：

```javascript
javascript:(function(){var s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js';document.head.appendChild(s);})();
```

<a id="path-2-npm-install-into-your-own-web-app-production-use"></a>
## 路径 2 — 通过 npm 安装到自己的 Web 应用（生产环境使用）

在已有的 Web 项目（React / Vue / Svelte / 普通 HTML）中：

```bash
npm install page-agent
```

搭配你自己的 LLM 端点——**千万不要将演示 CDN 发送给真实用户**：

```javascript
import { PageAgent } from 'page-agent'

const agent = new PageAgent({
    model: 'qwen3.5-plus',
    baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    apiKey: process.env.LLM_API_KEY,   // 切勿硬编码
    language: 'en-US',
})

// 向最终用户显示面板：
agent.panel.show()

// 或者以编程方式驱动：
await agent.execute('点击提交按钮，然后将用户名填写为 John')
```

提供商示例（任何兼容 OpenAI 的端点均可使用）：

| 提供商 | `baseURL` | `model` |
|----------|-----------|---------|
| Qwen / DashScope | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen3.5-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| Ollama（本地） | `http://localhost:11434/v1` | `qwen3:14b` |
| OpenRouter | `https://openrouter.ai/api/v1` | `anthropic/claude-sonnet-4.6` |

**关键配置字段**（通过 `new PageAgent({...})` 传入）：

- `model`, `baseURL`, `apiKey` — LLM 连接
- `language` — UI 语言（`en-US`、`zh-CN` 等）
- 允许列表和数据遮盖钩子用于限制 Agent 可操作的范围——完整选项列表请参见 https://alibaba.github.io/page-agent/

**安全性。** 在生产部署中，切勿在客户端代码中放置 `apiKey`——应通过后端代理 LLM 请求，并将 `baseURL` 指向你的代理。演示 CDN 之所以存在，是因为阿里巴巴运行了该代理用于评估。

<a id="path-3-clone-the-source-repo-contributing-or-hacking-on-it"></a>
## 路径 3 — 克隆源代码仓库（贡献或自行修改）

当用户想要修改 page-agent 本身、通过本地 IIFE 包针对任意站点进行测试，或开发浏览器扩展时，可以使用此方式。

```bash
git clone https://github.com/alibaba/page-agent.git
cd page-agent
npm ci              # 使用精确的 lockfile 安装（或使用 `npm i` 允许更新）
```

在仓库根目录下创建 `.env` 文件，填入 LLM 端点信息。示例：

```
LLM_MODEL_NAME=gpt-4o-mini
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.openai.com/v1
```
Ollama 版本：

```
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=NA
LLM_MODEL_NAME=qwen3:14b
```

常用命令：

```bash
npm start           # docs/website 开发服务器
npm run build       # 构建所有包
npm run dev:demo    # 在 http://localhost:5174/page-agent.demo.js 提供 IIFE 捆绑包
npm run dev:ext     # 开发浏览器扩展（WXT + React）
npm run build:ext   # 构建扩展
```

**在任何网站上测试**，使用本地 IIFE 捆绑包。添加这个书签小工具：

```javascript
javascript:(function(){var s=document.createElement('script');s.src=`http://localhost:5174/page-agent.demo.js?t=${Math.random()}`;s.onload=()=>console.log('PageAgent ready!');document.head.appendChild(s);})();
```

然后：运行 `npm run dev:demo`，在任何页面上点击书签小工具，本地构建就会注入。保存时自动重新构建。

**警告：** 开发构建期间，你的 `.env` 中的 `LLM_API_KEY` 会被内联到 IIFE 捆绑包里。不要分享这个捆绑包。不要提交它。不要将 URL 粘贴到 Slack 中。（已验证：对公开开发包进行 grep 搜索会返回 `.env` 中的字面值。）

<a id="repo-layout-path-3"></a>
## 仓库结构（路径 3）

使用 npm workspaces 的单仓库。关键包：

| 包 | 路径 | 用途 |
|---------|------|------|
| `page-agent` | `packages/page-agent/` | 主入口，带 UI 面板 |
| `@page-agent/core` | `packages/core/` | 核心 Agent 逻辑，无 UI |
| `@page-agent/mcp` | `packages/mcp/` | MCP 服务器（beta） |
| — | `packages/llms/` | LLM 客户端 |
| — | `packages/page-controller/` | DOM 操作 + 视觉反馈 |
| — | `packages/ui/` | 面板 + 国际化 |
| — | `packages/extension/` | Chrome/Firefox 扩展 |
| — | `packages/website/` | 文档 + 落地页 |

<a id="verifying-it-works"></a>
## 验证是否生效

路径 1 或路径 2 之后：
1. 在浏览器中打开页面，同时打开开发者工具
2. 你应该会看到一个悬浮面板。如果没有，检查控制台是否有错误（最常见的是：LLM 端点的 CORS 问题、`baseURL` 错误、或者 API 密钥无效）
3. 输入一条简单指令，匹配页面上可见的内容（例如“点击 Login 链接”）
4. 观察 Network 选项卡——你应该能看到一个发往 `baseURL` 的请求

路径 3 之后：
1. `npm run dev:demo` 会输出 `Accepting connections at http://localhost:5174`
2. `curl -I http://localhost:5174/page-agent.demo.js` 返回 `HTTP/1.1 200 OK` 和 `Content-Type: application/javascript`
3. 在任何网页上点击书签小工具，面板就会出现

<a id="pitfalls"></a>
## 常见陷阱

- **生产环境使用演示 CDN**——不要这样做。它有速率限制，使用了阿里的免费代理，而且他们的条款禁止用于生产。
- **API 密钥泄露**——任何传递给 `new PageAgent({apiKey: ...})` 的密钥都会被打包到 JS 包中。实际部署时一定要通过你自己的后端代理。
- **非 OpenAI 兼容的端点**会静默失败或抛出难以理解的错误。如果你的提供商需要原生的 Anthropic/Gemini 格式，在前面放一个 OpenAI 兼容的代理（如 LiteLLM、OpenRouter）。
- **CSP 限制**——具有严格内容安全策略的网站可能会拒绝加载 CDN 脚本，或禁止内联 eval。这种情况下，请从你自己的源站自行托管。
- **修改 `.env` 后需要重新启动开发服务器**（路径 3）——Vite 只在启动时读取环境变量。
- **Node 版本**——仓库声明了 `^22.13.0 || >=24`。Node 20 执行 `npm ci` 时会报引擎错误。
- **npm 10 与 npm 11**——文档说需要 npm 11+；但实际上 npm 10.9 也能正常工作。
<a id="reference"></a>
## 参考资料

- 仓库：https://github.com/alibaba/page-agent
- 文档：https://alibaba.github.io/page-agent/
- 许可证：MIT（基于 browser-use 的 DOM 处理内部实现，版权所有 2024 Gregor Zunic）
