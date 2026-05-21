---
title: "Nous 工具网关"
description: "一次订阅，所有工具。网络搜索、图片生成、TTS 和云端浏览器——全部通过 Nous Portal 路由，无需额外 API 密钥。"
sidebar_label: "工具网关"
sidebar_position: 2
---

<a id="nous-tool-gateway"></a>
# Nous 工具网关

**一次订阅，所有工具内置。**

工具网关包含在所有付费版 [Nous Portal](https://portal.nousresearch.com) 订阅中。它通过 Nous 已经运行的基础设施来路由 Hermes 的工具调用——网络搜索、图片生成、文本转语音和云端浏览器自动化——这样你就不必为了让你的 Agent 变得有用而再去注册 Firecrawl、FAL、OpenAI、Browser Use 或其他服务了。

<div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap', margin: '1.5rem 0'}}>
  <a href="https://portal.nousresearch.com/manage-subscription" style={{background: 'var(--ifm-color-primary)', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '6px', textDecoration: 'none', fontWeight: 'bold'}}>开始或管理订阅 →</a>
</div>

<a id="what-s-included"></a>
## 包含哪些内容

| | 工具 | 你获得的功能 |
|---|---|---|
| 🔍 | **网络搜索与提取** | 通过 Firecrawl 进行符合 Agent 级别的网络搜索和整页提取。无需担心速率限制——网关会处理好扩展问题。 |
| 🎨 | **图片生成** | 一个端点下九款模型：**FLUX 2 Klein 9B**、**FLUX 2 Pro**、**Z-Image Turbo**、**Nano Banana Pro**（Gemini 3 Pro Image）、**GPT Image 1.5**、**GPT Image 2**、**Ideogram V3**、**Recraft V4 Pro**、**Qwen Image**。每次生成可通过标记选择，或让 Hermes 默认使用 FLUX 2 Klein。 |
| 🔊 | **文本转语音** | OpenAI TTS 语音已接入 `text_to_speech` 工具。可将语音笔记发送到 Telegram、为管线生成音频、朗读任何内容。 |
| 🌐 | **云端浏览器自动化** | 通过 Browser Use 提供无头 Chromium 会话。`browser_navigate`、`browser_click`、`browser_type`、`browser_vision`——所有驱动 Agent 的基础操作，无需 Browserbase 账户。 |

所有四项均按使用量计费，计入你的 Nous 订阅。你可以使用任意组合——例如，通过网关使用网络和图片，同时保留你自己的 ElevenLabs 密钥用于 TTS，或者将所有内容都通过 Nous 路由。

<a id="why-it-s-here"></a>
## 为什么存在这个

构建一个真正能 *做事* 的 Agent 意味着要拼凑 5 个以上的 API 订阅——每个都有独立的注册、速率限制、计费和怪癖。工具网关将它缩减为一个账户：

- **一张账单。** 付给 Nous；我们处理其他所有。
- **一次注册。** 无需管理 Firecrawl、FAL、Browser Use 或 OpenAI 音频账户。
- **一个密钥。** 你的 Nous Portal OAuth 覆盖所有工具。
- **同样质量。** 和直接使用密钥路由时相同的后端——只是由我们前置。

任何时候你都可以自带密钥——按工具，随时可以。网关不是锁定，而是一个捷径。

<a id="get-started"></a>
## 开始使用

```bash
hermes model          # 选择 Nous Portal 作为你的提供商
```

当你选择 Nous Portal 时，Hermes 会询问是否开启工具网关。接受，然后你就完成了——下次运行时所有支持的工具都会生效。

随时检查当前已启用的内容：

```bash
hermes status
```

你会看到类似下面的部分：

```
◆ Nous 工具网关
  Nous Portal     ✓ 通过 Nous 订阅提供托管的工具
  网络工具        ✓ 通过 Nous 订阅激活
  图片生成        ✓ 通过 Nous 订阅激活
  TTS             ✓ 通过 Nous 订阅激活
  浏览器          ○ 通过 Browser Use 密钥激活
```
标记为"通过 Nous 订阅激活"的工具会走网关。其他工具则使用你自己的密钥。

<a id="eligibility"></a>
## 资格要求

工具网关是一项**付费订阅**功能。免费版 Nous 账户可以使用 Portal 进行推理，但不包含托管工具——[升级你的套餐](https://portal.nousresearch.com/manage-subscription)即可解锁网关。

<a id="mix-and-match"></a>
## 自由组合

网关是按工具启用的。只为你需要的工具开启：

- **所有工具都走 Nous** — 最简单；一次订阅，全部搞定。
- **网页 + 图片走网关，TTS 用自己的** — 保留你的 ElevenLabs 语音，其余交给 Nous 处理。
- **只为你没有密钥的工具开启网关** — "我已经付了 Browserbase 的钱，但不想再开一个 Firecrawl 账户"，这样完全没问题。

随时通过以下命令切换任意工具：

```bash
hermes tools          # 每个工具类别的交互式选择器
```

选择工具，然后选择 **Nous Subscription** 作为提供商（或你偏好的任何直接提供商）。无需编辑配置文件。

<a id="using-individual-image-models"></a>
## 使用单个图片模型

图片生成默认使用 FLUX 2 Klein 9B 以保证速度。每次调用时，可以通过向 `image_generate` 工具传递模型 ID 来覆盖默认设置：

| 模型 | ID | 最佳用途 |
|---|---|---|
| FLUX 2 Klein 9B | `fal-ai/flux-2/klein/9b` | 快速，良好的默认选择 |
| FLUX 2 Pro | `fal-ai/flux-2/pro` | 更高保真度的 FLUX |
| Z-Image Turbo | `fal-ai/z-image/turbo` | 风格化，快速 |
| Nano Banana Pro | `fal-ai/gemini-3-pro-image` | Google Gemini 3 Pro Image |
| GPT Image 1.5 | `fal-ai/gpt-image-1/5` | OpenAI 图片生成，文本+图片 |
| GPT Image 2 | `fal-ai/gpt-image-2` | OpenAI 最新版 |
| Ideogram V3 | `fal-ai/ideogram/v3` | 强提示遵循 + 排版 |
| Recraft V4 Pro | `fal-ai/recraft/v4/pro` | 矢量风格，平面设计 |
| Qwen Image | `fal-ai/qwen-image` | 阿里巴巴多模态 |

模型列表会不断更新——运行 `hermes tools` → Image Generation 可查看当前实时列表。

---

<a id="configuration-reference"></a>
## 配置参考

大多数用户无需触碰这里——`hermes model` 和 `hermes tools` 已交互式覆盖所有工作流程。本节适用于直接编写 config.yaml 或脚本化配置。

<a id="per-tool-usegateway-flag"></a>
### 每个工具的 `use_gateway` 标志

每个工具的配置块都接受一个 `use_gateway` 布尔值：

```yaml
web:
  backend: firecrawl
  use_gateway: true

image_gen:
  use_gateway: true

tts:
  provider: openai
  use_gateway: true

browser:
  cloud_provider: browser-use
  use_gateway: true
```

优先级：`use_gateway: true` 会绕过 `.env` 中的任何直接密钥，直接走 Nous 路由。`use_gateway: false`（或未设置）则优先使用直接密钥，仅在无密钥时回退到网关。

<a id="disabling-the-gateway"></a>
### 禁用网关

```yaml
web:
  use_gateway: false   # Hermes 现在使用 .env 中的 FIRECRAWL_API_KEY
```

当你选择非网关提供商时，`hermes tools` 会自动清除该标志，因此通常无需手动操作。

<a id="self-hosted-gateway-advanced"></a>
### 自托管网关（高级）

想运行自己的兼容 Nous 的网关？在 `~/.hermes/.env` 中覆盖端点：

```bash
TOOL_GATEWAY_DOMAIN=your-domain.example.com
TOOL_GATEWAY_SCHEME=https
TOOL_GATEWAY_USER_TOKEN=your-token        # 通常从 Portal 登录自动填充
FIRECRAWL_GATEWAY_URL=https://...         # 单独覆盖某个端点
```
这些调节项仅适用于自定义基础设施环境（企业部署、开发环境）。普通用户无需设置。

<a id="faq"></a>
## 常见问题

<a id="does-it-work-with-telegram-discord-the-other-messaging-gateways"></a>
### 适用于 Telegram / Discord 或其他消息网关吗？

适用。工具网关在工具调用层面工作，与 CLI 无关。所有能调用工具的接口——CLI、Telegram、Discord、Slack、IRC、Teams、API 服务器等——都能透明地从中受益。

<a id="what-happens-if-my-subscription-expires"></a>
### 订阅过期会怎样？

通过网关路由的工具会停止工作，直到你续费，或者通过 `hermes tools` 换回直接 API 密钥。Hermes 会显示明确的错误消息，指向门户网站。

<a id="can-i-see-usage-or-costs-per-tool"></a>
### 能看到每个工具的使用量或费用吗？

可以——[Nous Portal 仪表盘](https://portal.nousresearch.com) 会按工具细分用量，方便你了解哪些工具产生了费用。

<a id="is-modal-serverless-terminal-included"></a>
### 包含 Modal（无服务器终端）吗？

Modal 作为 Nous 订阅的**可选附加项**提供，不属于默认工具网关包的一部分。当你需要远程沙盒来执行 Shell 命令时，可通过 `hermes setup terminal` 或直接在 `config.yaml` 中进行配置。

<a id="do-i-need-to-delete-my-existing-api-keys-when-i-enable-the-gateway"></a>
### 启用网关后需要删除现有的 API 密钥吗？

不需要——把它们留在 `.env` 中。当 `use_gateway: true` 时，Hermes 会跳过直接密钥，使用网关。把标志改回 `false` 后，你的密钥又会成为来源。工具网关不会把你锁死。
