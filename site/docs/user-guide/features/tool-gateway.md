---
title: "Nous Tool Gateway"
description: "通过您的 Nous 订阅路由网络搜索、图像生成、文本转语音和浏览器自动化——无需额外的 API 密钥"
sidebar_label: "Tool Gateway"
sidebar_position: 2
---

# Nous Tool Gateway {#nous-tool-gateway}

:::tip 开始使用
Tool Gateway 包含在付费的 Nous Portal 订阅中。**[管理您的订阅 →](https://portal.nousresearch.com/manage-subscription)**
:::

**Tool Gateway** 让付费的 [Nous Portal](https://portal.nousresearch.com) 订阅用户能够通过其现有订阅使用网络搜索、图像生成、文本转语音和浏览器自动化——无需再为 Firecrawl、FAL、OpenAI 或 Browser Use 单独注册 API 密钥。

## 包含内容 {#what-s-included}
<a id="get-started"></a>

| 工具 | 功能 | 直接替代方案 |
|------|--------------|--------------------|
| **网络搜索与提取** | 通过 Firecrawl 搜索网络并提取页面内容 | `FIRECRAWL_API_KEY`, `EXA_API_KEY`, `PARALLEL_API_KEY`, `TAVILY_API_KEY` |
| **图像生成** | 通过 FAL 生成图像（8 个模型：FLUX 2 Klein/Pro, GPT-Image, Nano Banana Pro, Ideogram, Recraft V4 Pro, Qwen, Z-Image） | `FAL_KEY` |
| **文本转语音** | 通过 OpenAI TTS 将文本转换为语音 | `VOICE_TOOLS_OPENAI_KEY`, `ELEVENLABS_API_KEY` |
| **浏览器自动化** | 通过 Browser Use 控制云浏览器 | `BROWSER_USE_API_KEY`, `BROWSERBASE_API_KEY` |

所有四个工具的费用都计入您的 Nous 订阅。您可以启用任意组合——例如，使用网关进行网络搜索和图像生成，同时保留您自己的 ElevenLabs 密钥用于 TTS。

## 资格 {#eligibility}

Tool Gateway 适用于**付费**的 [Nous Portal](https://portal.nousresearch.com/manage-subscription) 订阅用户。免费层级账户无法访问——[升级您的订阅](https://portal.nousresearch.com/manage-subscription)以解锁此功能。

要检查您的状态：

```bash
hermes status
```

查找 **Nous Tool Gateway** 部分。它会显示哪些工具通过网关处于活动状态，哪些使用直接密钥，以及哪些尚未配置。

## 启用 Tool Gateway {#enabling-the-tool-gateway}

### 在模型设置期间 {#during-model-setup}

当您运行 `hermes model` 并选择 Nous Portal 作为您的提供商时，Hermes 会自动提供启用 Tool Gateway 的选项：

```
您的 Nous 订阅包含 Tool Gateway。

  Tool Gateway 让您能够通过您的 Nous 订阅使用网络搜索、图像生成、
  文本转语音和浏览器自动化。
  无需注册单独的 API 密钥——只需选择您想要使用的工具。

  ○ 网络搜索与提取 (Firecrawl) — 未配置
  ○ 图像生成 (FAL) — 未配置
  ○ 文本转语音 (OpenAI TTS) — 未配置
  ○ 浏览器自动化 (Browser Use) — 未配置

  ● 启用 Tool Gateway
  ○ 跳过
```

选择 **启用 Tool Gateway** 即可完成。

如果您已经为某些工具配置了直接的 API 密钥，提示信息会相应调整——您可以为所有工具启用网关（您现有的密钥会保留在 `.env` 中，但运行时不会使用），仅为未配置的工具启用，或者完全跳过。

### 通过 `hermes tools` {#via-hermes-tools}

您也可以通过交互式工具配置逐个启用网关工具：

```bash
hermes tools
```

选择一个工具类别（Web、Browser、Image Generation 或 TTS），然后选择 **Nous Subscription** 作为提供商。这将在您的配置中为该工具设置 `use_gateway: true`。

### 手动配置 {#manual-configuration}

直接在 `~/.hermes/config.yaml` 中设置 `use_gateway` 标志：

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

## 工作原理 {#how-it-works}

当为某个工具设置 `use_gateway: true` 时，运行时会通过 Nous Tool Gateway 路由 API 调用，而不是使用直接的 API 密钥：

1.  **Web 工具** — `web_search` 和 `web_extract` 使用网关的 Firecrawl 端点
2.  **图像生成** — `image_generate` 使用网关的 FAL 端点
3.  **TTS** — `text_to_speech` 使用网关的 OpenAI Audio 端点
4.  **浏览器** — `browser_navigate` 和其他浏览器工具使用网关的 Browser Use 端点

网关使用您的 Nous Portal 凭据（在 `hermes model` 后存储在 `~/.hermes/auth.json` 中）进行身份验证。

### 优先级 {#precedence}
每个工具会先检查 `use_gateway`：

- **`use_gateway: true`** → 通过网关路由，即使 `.env` 中存在直接 API 密钥
- **`use_gateway: false`**（或未设置）→ 如果有直接 API 密钥则使用，仅当没有直接密钥时才回退到网关

这意味着你可以随时在网关和直接密钥之间切换，而无需删除 `.env` 中的凭证。

## 切换回直接密钥 {#switching-back-to-direct-keys}

要停止对特定工具使用网关：

```bash
hermes tools    # 选择工具 → 选择一个直接提供商
```

或在配置中设置 `use_gateway: false`：

```yaml
web:
  backend: firecrawl
  use_gateway: false  # 现在使用 .env 中的 FIRECRAWL_API_KEY
```

当你在 `hermes tools` 中选择非网关提供商时，`use_gateway` 标志会自动设置为 `false`，以防止配置冲突。

## 检查状态 {#checking-status}

```bash
hermes status
```

**Nous Tool Gateway** 部分显示：

```
◆ Nous Tool Gateway
  Nous Portal   ✓ managed tools available
  Web tools       ✓ active via Nous subscription
  Image gen       ✓ active via Nous subscription
  TTS             ✓ active via Nous subscription
  Browser         ○ active via Browser Use key
  Modal           ○ available via subscription (optional)
```

标记为 “active via Nous subscription” 的工具通过网关路由。拥有自己密钥的工具会显示哪个提供商处于活动状态。

## 高级：自托管网关 {#advanced-self-hosted-gateway}

对于自托管或自定义网关部署，你可以通过 `~/.hermes/.env` 中的环境变量覆盖网关端点：

```bash
TOOL_GATEWAY_DOMAIN=nousresearch.com     # 网关路由的基础域名
TOOL_GATEWAY_SCHEME=https                 # HTTP 或 HTTPS（默认：https）
TOOL_GATEWAY_USER_TOKEN=your-token        # 认证令牌（通常自动填充）
FIRECRAWL_GATEWAY_URL=https://...         # 专门用于 Firecrawl 端点的覆盖
```

无论订阅状态如何，这些环境变量在配置中始终可见——它们对于自定义基础设施设置很有用。

## 常见问题 {#faq}

### 我需要删除现有的 API 密钥吗？ {#do-i-need-to-delete-my-existing-api-keys}

不需要。当设置了 `use_gateway: true` 时，运行时会跳过直接 API 密钥并通过网关路由。你的密钥会保留在 `.env` 中不受影响。如果你之后禁用网关，它们会自动再次被使用。

### 我可以对某些工具使用网关，对其他工具使用直接密钥吗？ {#can-i-use-the-gateway-for-some-tools-and-direct-keys-for-others}

可以。`use_gateway` 标志是按工具设置的。你可以混合搭配——例如，网络和图像生成使用网关，TTS 使用你自己的 ElevenLabs 密钥，浏览器自动化使用 Browserbase。

### 如果我的订阅过期了怎么办？ {#what-if-my-subscription-expires}

通过网关路由的工具将停止工作，直到你[续订订阅](https://portal.nousresearch.com/manage-subscription)或通过 `hermes tools` 切换到直接 API 密钥。

### 网关与消息网关兼容吗？ {#does-the-gateway-work-with-the-messaging-gateway}

兼容。Tool Gateway 路由工具 API 调用，无论你使用的是 CLI、Telegram、Discord 还是任何其他消息平台。它在工具运行时级别运行，而不是在入口点级别。

### Modal 包含在内吗？ {#is-modal-included}

Modal（无服务器终端后端）可通过 Nous 订阅作为可选附加组件使用。它不会通过 Tool Gateway 提示启用——请通过 `hermes setup terminal` 或在 `config.yaml` 中单独配置。
