---
title: "Page Agent"
sidebar_label: "Page Agent"
description: "将 alibaba/page-agent 嵌入你自己的 Web 应用——一个纯 JavaScript 的页面内 GUI Agent，以单个 &lt;script> 标签或 npm 包的形式发布，让你的网站最终用户能够用自然语言驱动 UI（例如“点击登录，将用户名填写为 John”）。无需 Python、无头浏览器或扩展。当用户是希望为自己的 SaaS / 管理面板 / B2B 工具添加 AI 助手、让旧版 Web 应用支持自然语言操作，或想针对本地（Ollama）或云端（Qwen / OpenAI / OpenRouter）LLM 评估 page-agent 的 Web 开发者时，请使用此技能。**不**用于服务端浏览器自动化——这些需求请引导用户使用 Hermes 内置的浏览器工具。"
---

{/* 此页面由 skills 目录下的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，不要编辑此页面。 */}

# Page Agent {#page-agent}

将 alibaba/page-agent 嵌入你自己的 Web 应用——一个纯 JavaScript 的页面内 GUI Agent，以单个 &lt;script> 标签或 npm 包的形式发布，让你的网站最终用户能够用自然语言驱动 UI（例如“点击登录，将用户名填写为 John”）。无需 Python、无头浏览器或扩展。当用户是希望为自己的 SaaS / 管理面板 / B2B 工具添加 AI 助手、让旧版 Web 应用支持自然语言操作，或想针对本地（Ollama）或云端（Qwen / OpenAI / OpenRouter）LLM 评估 page-agent 的 Web 开发者时，请使用此技能。**不**用于服务端浏览器自动化——这些需求请引导用户使用 Hermes 内置的浏览器工具。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/web-development/page-agent` 安装 |
| 路径 | `optional-skills/web-development/page-agent` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `web`, `javascript`, `agent`, `browser`, `gui`, `alibaba`, `embed`, `copilot`, `saas` |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活后 Agent 看到的指令。
:::

<a id="page-agent"></a>
# page-agent

alibaba/page-agent（https://github.com/alibaba/page-agent，17000+ star，MIT 许可证）是一个用 TypeScript 编写的页面内 GUI Agent。它运行在网页内部，将 DOM 读取为文本（无需截图，无需多模态 LLM），并针对当前页面执行自然语言指令，例如“点击登录按钮，然后将用户名填写为 John”。纯客户端——宿主网站只需引入一个脚本，并传入一个兼容 OpenAI 的 LLM 端点即可。

## 何时使用此技能 {#when-to-use-this-skill}

当用户希望以下场景时，请加载此技能：

- **在自己的 Web 应用中嵌入 AI 助手**（SaaS、管理面板、B2B 工具、ERP、CRM）——“我希望我的仪表盘用户能够输入‘为 Acme Corp 创建发票并发送邮件’，而不是点击五个页面”
- **改造旧版 Web 应用**，无需重写前端——page-agent 直接叠加在现有 DOM 之上
- **通过自然语言增强无障碍性**——语音 / 屏幕阅读器用户通过描述他们想要的操作来驱动 UI
- **演示或评估 page-agent**，对比本地（Ollama）或托管（Qwen、OpenAI、OpenRouter）LLM
- **构建交互式培训 / 产品演示**——让 AI 在真实 UI 中实时引导用户“如何提交费用报告”

## 何时**不**使用此技能 {#when-not-to-use-this-skill}

- 用户希望 **Hermes 本身驱动浏览器** → 使用 Hermes 内置的浏览器工具（Browserbase / Camofox）。page-agent 是*相反*的方向。
- 用户希望 **无需嵌入即可跨标签页自动化** → 使用 Playwright、browser-use 或 page-agent Chrome 扩展
- 用户需要 **视觉定位 / 截图** → page-agent 仅处理文本 DOM；请改用多模态浏览器 Agent
## 前提条件 {#prerequisites}

- Node 22.13+ 或 24+，npm 10+（文档说需要 11+，但 10.9 也能正常工作）
- 兼容 OpenAI 的 LLM 端点：Qwen（DashScope）、OpenAI、Ollama、OpenRouter，或任何支持 `/v1/chat/completions` 的服务
- 带开发者工具的浏览器（用于调试）

## 路径 1 — 通过 CDN 的 30 秒演示（无需安装） {#path-1-30-second-demo-via-cdn-no-install}

最快看到效果的方式。使用阿里巴巴的免费测试 LLM 代理——**仅用于评估**，需遵守其条款。

添加到任意 HTML 页面（或粘贴到开发者工具控制台中作为书签小工具）：

```html
<script src="https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js" crossorigin="true"></script>
```

会出现一个面板。输入指令即可。

书签小工具形式（拖到书签栏，点击任意页面）：

```javascript
javascript:(function(){var s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js';document.head.appendChild(s);})();
```

## 路径 2 — 通过 npm 安装到自己的 Web 应用（生产环境使用） {#path-2-npm-install-into-your-own-web-app-production-use}

在已有的 Web 项目（React / Vue / Svelte / 纯 JS）中：

```bash
npm install page-agent
```

接入你自己的 LLM 端点——**切勿将演示 CDN 发给真实用户**：

```javascript
import { PageAgent } from 'page-agent'

const agent = new PageAgent({
    model: 'qwen3.5-plus',
    baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    apiKey: process.env.LLM_API_KEY,   // 切勿硬编码
    language: 'en-US',
})

// 为最终用户显示面板：
agent.panel.show()

// 或以编程方式驱动：
await agent.execute('点击提交按钮，然后将用户名填写为 John')
```

提供商示例（任何兼容 OpenAI 的端点均可）：

| 提供商 | `baseURL` | `model` |
|----------|-----------|---------|
| Qwen / DashScope | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen3.5-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| Ollama（本地） | `http://localhost:11434/v1` | `qwen3:14b` |
| OpenRouter | `https://openrouter.ai/api/v1` | `anthropic/claude-sonnet-4.6` |

**关键配置字段**（传递给 `new PageAgent({...})`）：

- `model`、`baseURL`、`apiKey` — LLM 连接
- `language` — UI 语言（`en-US`、`zh-CN` 等）
- 存在允许列表和数据脱敏钩子，用于限制 Agent 可操作的范围——完整选项列表见 https://alibaba.github.io/page-agent/

**安全性。** 在生产部署中，不要将 `apiKey` 放在客户端代码中——应通过后端代理 LLM 调用，并将 `baseURL` 指向你的代理。演示 CDN 之所以存在，是因为阿里巴巴运行该代理用于评估。

## 路径 3 — 克隆源码仓库（贡献代码或自行修改） {#path-3-clone-the-source-repo-contributing-or-hacking-on-it}

当用户想要修改 page-agent 本身、通过本地 IIFE 包在任意站点上测试，或开发浏览器扩展时，使用此方式。

```bash
git clone https://github.com/alibaba/page-agent.git
cd page-agent
npm ci              # 精确锁定文件安装（或使用 `npm i` 以允许更新）
```

在仓库根目录创建 `.env` 文件，填入 LLM 端点。示例：

```
LLM_MODEL_NAME=gpt-4o-mini
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.openai.com/v1
```
Ollama 配置：

```
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=NA
LLM_MODEL_NAME=qwen3:14b
```

常用命令：

```bash
npm start           # 启动 docs/website 开发服务器
npm run build       # 构建所有包
npm run dev:demo    # 在 http://localhost:5174/page-agent.demo.js 提供 IIFE 包
npm run dev:ext     # 开发浏览器扩展（WXT + React）
npm run build:ext   # 构建扩展
```

**在任何网站上测试**，使用本地 IIFE 包。添加这个书签小工具：

```javascript
javascript:(function(){var s=document.createElement('script');s.src=`http://localhost:5174/page-agent.demo.js?t=${Math.random()}`;s.onload=()=>console.log('PageAgent ready!');document.head.appendChild(s);})();
```

然后：运行 `npm run dev:demo`，在任何页面上点击书签小工具，本地构建就会注入。保存时自动重新构建。

**警告：** 在开发构建期间，你的 `.env` 文件中的 `LLM_API_KEY` 会被内联到 IIFE 包中。不要分享这个包。不要提交它。不要将 URL 粘贴到 Slack 中。（已验证：在公共开发包中搜索，会返回 `.env` 中的字面值。）

## 仓库布局（路径 3） {#repo-layout-path-3}

使用 npm workspaces 的 Monorepo。关键包：

| 包 | 路径 | 用途 |
|---------|------|---------|
| `page-agent` | `packages/page-agent/` | 主入口，包含 UI 面板 |
| `@page-agent/core` | `packages/core/` | 核心 Agent 逻辑，无 UI |
| `@page-agent/mcp` | `packages/mcp/` | MCP 服务器（beta） |
| — | `packages/llms/` | LLM 客户端 |
| — | `packages/page-controller/` | DOM 操作 + 视觉反馈 |
| — | `packages/ui/` | 面板 + 国际化 |
| — | `packages/extension/` | Chrome/Firefox 扩展 |
| — | `packages/website/` | 文档 + 落地页 |

## 验证是否正常工作 {#verifying-it-works}

完成路径 1 或路径 2 后：
1. 在浏览器中打开页面，并打开开发者工具
2. 你应该会看到一个浮动面板。如果没有，检查控制台中的错误（最常见的是：LLM 端点的 CORS 问题、错误的 `baseURL` 或无效的 API 密钥）
3. 输入一个与页面上可见内容匹配的简单指令（例如“点击 Login 链接”）
4. 观察 Network 标签页——你应该会看到向你的 `baseURL` 发出的请求

完成路径 3 后：
1. `npm run dev:demo` 会输出 `Accepting connections at http://localhost:5174`
2. `curl -I http://localhost:5174/page-agent.demo.js` 返回 `HTTP/1.1 200 OK` 且 `Content-Type: application/javascript`
3. 在任何网站上点击书签小工具；面板就会出现

## 常见陷阱 {#pitfalls}

- **在生产环境中使用演示 CDN**——不要这样做。它有速率限制，使用阿里的免费代理，并且他们的条款禁止生产环境使用。
- **API 密钥泄露**——任何传递给 `new PageAgent({apiKey: ...})` 的密钥都会被打包到你的 JS 包中。对于实际部署，始终通过你自己的后端进行代理。
- **非 OpenAI 兼容的端点**会静默失败或返回难以理解的错误。如果你的提供商需要原生的 Anthropic/Gemini 格式，请在前面使用一个 OpenAI 兼容性代理（LiteLLM、OpenRouter）。
- **CSP 限制**——具有严格 Content-Security-Policy 的网站可能会拒绝加载 CDN 脚本或禁止内联 eval。在这种情况下，请从你自己的源站自托管。
- **在路径 3 中编辑 `.env` 后需要重启开发服务器**——Vite 只在启动时读取环境变量。
- **Node 版本**——仓库声明了 `^22.13.0 || >=24`。Node 20 会在 `npm ci` 时因引擎错误而失败。
- **npm 10 与 11**——文档说需要 npm 11+；但实际上 npm 10.9 也能正常工作。
## 参考 {#reference}

- 仓库：https://github.com/alibaba/page-agent
- 文档：https://alibaba.github.io/page-agent/
- 许可证：MIT（基于 browser-use 的 DOM 处理内部实现，版权所有 2024 Gregor Zunic）
