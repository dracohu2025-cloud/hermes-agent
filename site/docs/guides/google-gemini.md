---
sidebar_position: 16
title: "Google Gemini"
description: "使用 Hermes Agent 搭配 Google Gemini — 原生 AI Studio API、API 密钥配置、OAuth 选项、工具调用、流式输出及配额指引"
---

<a id="google-gemini"></a>
# Google Gemini

Hermes Agent 支持将 Google Gemini 作为原生提供商，使用的是 **Google AI Studio / Gemini API**，而非兼容 OpenAI 的端点。这使得 Hermes 能够将其内部基于 OpenAI 格式的消息和工具循环转换为 Gemini 原生的 `generateContent` API，同时保留工具调用、流式输出、多模态输入以及 Gemini 特有的响应元数据。

此外，Hermes 还支持独立的 **Google Gemini (OAuth)** 提供商，其使用与 Google Gemini CLI 相同的 Cloud Code Assist 后端。建议使用 API 密钥提供商（`gemini`），这是风险最低的官方 API 路径。

<a id="prerequisites"></a>
## 前提条件

- **Google AI Studio API 密钥** — 在 [aistudio.google.com/apikey](https://aistudio.google.com/apikey) 创建一个
- **已启用结算功能的 Google Cloud 项目** — 推荐用于 Agent 场景。Gemini 的免费额度对于长时间运行的 Agent 会话来说太小了，因为 Hermes 在每个用户轮次中可能需要多次调用模型。
- **已安装 Hermes** — 原生 Gemini 提供商不需要额外的 Python 包。

:::tip API 密钥路径
设置 `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`。Hermes 会同时检查这两个名称以用于 `gemini` 提供商。
:::

<a id="api-key-path"></a>
<a id="quick-start"></a>
## 快速开始

```bash
# 添加你的 Gemini API 密钥
echo "GOOGLE_API_KEY=..." >> ~/.hermes/.env

# 选择 Gemini 作为你的提供商
hermes model
# → 选择 "更多提供商..." → "Google AI Studio"
# → Hermes 会检查你的密钥层级并显示 Gemini 模型
# → 选择一个模型

# 开始聊天
hermes chat
```

如果你更倾向于直接编辑配置，请使用原生 Gemini API 的基础 URL：

```yaml
model:
  default: gemini-3-flash-preview
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

<a id="configuration"></a>
## 配置

运行 `hermes model` 后，你的 `~/.hermes/config.yaml` 将包含：

```yaml
model:
  default: gemini-3-flash-preview
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

而在 `~/.hermes/.env` 中：

```bash
GOOGLE_API_KEY=...
```

<a id="native-gemini-api"></a>
### 原生 Gemini API

推荐的端点是：

```text
https://generativelanguage.googleapis.com/v1beta
```

Hermes 检测到此端点后会创建其原生 Gemini 适配器。在内部，Hermes 仍然保持 Agent 循环使用 OpenAI 格式的消息，然后将每个请求转换为 Gemini 的原生 schema：

- `messages[]` → Gemini `contents[]`
- 系统提示 → Gemini `systemInstruction`
- 工具 schema → Gemini `functionDeclarations`
- 工具结果 → Gemini `functionResponse` 部分
- 流式响应 → 转换为 OpenAI 格式的流式块，供 Hermes 循环使用

:::note Gemini 3 思考签名
<a id="gemini-3-thought-signatures"></a>
对于 Gemini 3 的工具使用，Hermes 会保留附加在函数调用部分上的 `thoughtSignature` 值，并在下一次工具轮次中重新发送。这覆盖了多步骤 Agent 工作流中关键的验证路径。

Gemini 3 也可能将思考签名附加到其他响应部分。Hermes 的原生适配器目前针对 Agent 工具循环进行了优化，因此尚不会以完整的分片级别保真度重新发送每一个非工具调用的签名。
:::

<a id="prefer-the-native-endpoint"></a>
### 优先使用原生端点

Google 也提供了一个兼容 OpenAI 的端点：
```text
https://generativelanguage.googleapis.com/v1beta/openai/
```

对于 Hermes Agent 会话，建议优先使用上述原生 Gemini 端点。Hermes 内置了原生 Gemini 适配器，可以直接将多轮工具调用、工具调用结果、流式传输、多模态输入以及 Gemini 响应元数据映射到 Gemini 的 `generateContent` API 上。当你特别需要 OpenAI API 兼容性时，OpenAI 兼容端点仍然有用。

如果你之前将 `GEMINI_BASE_URL` 设置为 `/openai` 的 URL，请将其移除或修改：

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

<a id="oauth-provider"></a>
### OAuth 提供商

Hermes 还提供了一个 `google-gemini-cli` 提供商：

```bash
hermes model
# → 选择 "Google Gemini (OAuth)"
```

该提供商使用浏览器 PKCE 登录和 Cloud Code Assist 后端。对于希望使用 Gemini CLI 风格 OAuth 的用户来说，这可能很有用，但 Hermes 会显示明确的警告，因为 Google 可能会将第三方软件使用 Gemini CLI OAuth 客户端视为违反政策。对于生产环境或风险最低的使用场景，建议优先使用上述 API 密钥提供商。

<a id="available-models"></a>
## 可用模型

`hermes model` 选择器会显示 Hermes 提供商注册表中维护的 Gemini 模型。常见选择包括：

| 模型 | ID | 说明 |
|-------|----|-------|
| Gemini 3.1 Pro Preview | `gemini-3.1-pro-preview` | 可用时功能最强大的预览模型 |
| Gemini 3 Pro Preview | `gemini-3-pro-preview` | 强大的推理和编码模型 |
| Gemini 3 Flash Preview | `gemini-3-flash-preview` | 推荐的速度与能力平衡默认模型 |
| Gemini 3.1 Flash Lite Preview | `gemini-3.1-flash-lite-preview` | 可用时速度最快/成本最低的选项 |

模型可用性会随时间变化。如果某个模型消失或未对你的密钥启用，请再次运行 `hermes model` 并从当前列表中选择一个。

:::info 模型 ID
当使用 `provider: gemini` 时，请使用 Gemini 的原生模型 ID，例如 `gemini-3-flash-preview`，而不是 OpenRouter 风格的 ID，如 `google/gemini-3-flash-preview`。
<a id="model-ids"></a>
:::

<a id="latest-aliases"></a>
### 最新别名

Google 为 Pro 和 Flash 系列 Gemini 模型发布了动态别名。当你希望 Google 自动更新模型而无需更改 Hermes 配置时，`gemini-pro-latest` 和 `gemini-flash-latest` 非常有用。

| 别名 | 当前跟踪的模型 | 说明 |
|-------|------------------|-------|
| `gemini-pro-latest` | 最新的 Gemini Pro 模型 | 当你希望使用 Google 当前默认的 Pro 模型时最佳 |
| `gemini-flash-latest` | 最新的 Gemini Flash 模型 | 当你希望使用 Google 当前默认的 Flash 模型时最佳 |

```yaml
model:
  default: gemini-pro-latest
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

如果你需要严格的可复现性，建议使用明确的模型 ID，例如 `gemini-3.1-pro-preview` 或 `gemini-3-flash-preview`。

<a id="gemma-via-the-gemini-api"></a>
### 通过 Gemini API 使用 Gemma

Google 还通过 Gemini API 公开了 Gemma 模型。Hermes 将这些识别为 Google 模型，但会从默认模型选择器中隐藏吞吐量极低的 Gemma 条目，以免新用户意外为长时间运行的 Agent 会话选择评估级别的模型。
有用的评估 ID 包括：

| 模型 | ID | 说明 |
|-------|----|-------|
| Gemma 4 31B IT | `gemma-4-31b-it` | 较大的 Gemma 模型；适用于兼容性和质量评估 |
| Gemma 4 26B A4B IT | `gemma-4-26b-a4b-it` | 较小的可用参数活跃变体（当可用时）|

这些模型最好作为 Gemini API 密钥上的评估选项使用。Google 的 Gemma API 定价仅限免费层，与生产级 Gemini 模型相比，使用上限较低，因此持续运行的 Hermes Agent 通常应迁移到付费 Gemini 模型、自托管部署或具有适当配额的其他提供商。

若要使用在选取器中隐藏的 Gemma 模型，请直接设置：

```yaml
model:
  default: gemma-4-31b-it
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

<a id="switching-models-mid-session"></a>
## 在会话中切换模型

在对话期间使用 `/model` 命令：

```text
/model gemini-3-flash-preview
/model gemini-flash-latest
/model gemini-3-pro-preview
/model gemini-pro-latest
/model gemma-4-31b-it
/model gemini-3.1-flash-lite-preview
```

如果你尚未配置 Gemini，请退出会话并先运行 `hermes model`。`/model` 在已配置的提供商和模型之间切换；它不会收集新的 API 密钥。

<a id="diagnostics"></a>
## 诊断

```bash
hermes doctor
```

诊断工具检查：

- `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` 是否可用
- 是否存在用于 `google-gemini-cli` 的 Gemini OAuth 凭据
- 配置的提供商凭据是否可以被解析

如需查看 OAuth 配额使用情况，请在 Hermes 会话内运行：

```text
/gquota
```

`/gquota` 适用于 `google-gemini-cli` OAuth 提供商，而非 AI Studio API 密钥提供商。

<a id="gateway-messaging-platforms"></a>
## 网关（消息平台）

Gemini 适用于所有 Hermes 网关平台（Telegram、Discord、Slack、WhatsApp、LINE、飞书等）。将 Gemini 配置为提供商，然后正常启动网关：

```bash
hermes gateway setup
hermes gateway start
```

网关读取 `config.yaml` 并使用相同的 Gemini 提供商配置。

<a id="troubleshooting"></a>
## 故障排除

<a id="gemini-native-client-requires-an-api-key"></a>
### “Gemini 原生客户端需要 API 密钥”

Hermes 找不到可用的 API 密钥。请将以下之一添加到 `~/.hermes/.env`：

```bash
GOOGLE_API_KEY=...
# or
GEMINI_API_KEY=...
```

然后重新运行 `hermes model`。

<a id="this-google-api-key-is-on-the-free-tier"></a>
### “此 Google API 密钥处于免费层”

Hermes 在设置期间探测 Gemini API 密钥。免费层的配额在几次 Agent 轮次后可能耗尽，因为工具使用、重试、压缩和辅助任务可能需要多次模型调用。

在密钥关联的 Google Cloud 项目上启用结算，如果需要，重新生成密钥，然后运行：

```bash
hermes model
```

<a id="404-model-not-found"></a>
### “404 模型未找到”

所选模型在你的账户、区域或密钥下不可用。请重新运行 `hermes model` 并从当前列表中选取另一个 Gemini 模型。

<a id="gemma-model-is-not-shown-in-hermes-model"></a>
### Gemma 模型未在 `hermes model` 中显示

默认情况下，Hermes 可能会从选取器中隐藏低吞吐量的 Gemma 模型。如果你有意评估其中一个，请在 `~/.hermes/config.yaml` 中直接设置模型 ID。
<a id="429-quota-exceeded-on-gemma"></a>
### 在 Gemma 上遇到“429 配额超限”

通过 Gemini API 暴露的 Gemma 模型适合用于评估，但其 Gemini API 免费层的配额较低。建议先使用它们进行兼容性测试，然后切换到付费的 Gemini 模型或其他提供商，以支持持续的 Agent 会话。

<a id="openai-compatible-endpoint-is-configured"></a>
### 已配置 OpenAI 兼容端点

检查 `~/.hermes/.env` 文件：

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

将其改为原生端点，或移除该覆盖设置：

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

<a id="oauth-login-warning"></a>
### OAuth 登录警告

`google-gemini-cli` 提供商使用 Gemini CLI / Cloud Code Assist 的 OAuth 流程。Hermes 在启动前会发出警告，因为这不同于官方的 AI Studio API 密钥路径。如需使用官方的 API 密钥集成，请使用 `provider: gemini` 并配合 `GOOGLE_API_KEY`。

<a id="tool-calling-fails-with-schema-errors"></a>
### 工具调用因 schema 错误失败

请升级 Hermes 并重新运行 `hermes model`。原生的 Gemini 适配器会清理工具 schema，以适配 Gemini 更严格的函数声明格式；旧版本或自定义端点可能无法做到这一点。

<a id="related"></a>
## 相关

- [AI 提供商](/integrations/providers)
- [配置](/user-guide/configuration)
- [备用提供商](/user-guide/features/fallback-providers)
- [AWS Bedrock](/guides/aws-bedrock) — 使用 AWS 凭证的原生云提供商集成
