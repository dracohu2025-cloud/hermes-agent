---
sidebar_position: 15
title: "Azure AI Foundry"
description: "将 Hermes Agent 与 Azure AI Foundry 配合使用 — 支持 OpenAI 风格和 Anthropic 风格的端点，自动检测传输方式和已部署模型"
---

# Azure AI Foundry {#azure-ai-foundry}

Hermes Agent 将 Azure AI Foundry（以及 Azure OpenAI）作为一等提供商进行支持。单个 Azure 资源可以托管使用两种不同线路格式的模型：

- **OpenAI 风格** — 在类似 `https://&lt;resource&gt;.openai.azure.com/openai/v1` 的端点上使用 `POST /v1/chat/completions`。适用于 GPT-4.x、GPT-5.x、Llama、Mistral 以及大多数开放权重模型。
- **Anthropic 风格** — 在类似 `https://&lt;resource&gt;.services.ai.azure.com/anthropic` 的端点上使用 `POST /v1/messages`。当 Azure Foundry 通过 Anthropic Messages API 格式提供 Claude 模型时使用。

设置向导会探测你的端点，并自动检测它使用的传输方式、可用的部署以及每个模型的上下文长度。

## 前提条件 {#prerequisites}

- 一个 Azure AI Foundry 或 Azure OpenAI 资源，至少包含一个部署
- 该资源的 API 密钥（可在 Azure 门户的“密钥和端点”下找到）
- 部署的端点 URL

## 快速开始 {#quick-start}

```bash
hermes model
# → 选择 "Azure Foundry"
# → 输入你的端点 URL
# → 输入你的 API 密钥
# Hermes 探测端点并自动检测传输方式 + 模型
# → 从列表中选择一个模型（或手动输入部署名称）
```

向导将执行以下操作：

1. **嗅探 URL 路径** — 以 `/anthropic` 结尾的 URL 会被识别为 Azure Foundry Claude 路由。
2. **探测 `GET &lt;base&gt;/models`** — 如果端点返回 OpenAI 形状的模型列表，Hermes 会切换到 `chat_completions` 并预填充一个选择器，其中包含返回的部署 ID。
3. **探测 Anthropic Messages 形状** — 对于不暴露 `/models` 但接受 Anthropic Messages 格式的端点，作为回退方案。
4. **回退到手动输入** — 拒绝所有探测的私有/受限端点仍然可用；你可以手动选择 API 模式并输入部署名称。

所选模型的上下文长度通过 Hermes 的标准元数据链（`models.dev`、提供商元数据以及硬编码的系列回退）解析，并存储在 `config.yaml` 中，以便模型能够正确调整其上下文窗口大小。

## 配置（写入 `config.yaml`） {#configuration-written-to-config-yaml}

运行向导后，你会看到类似这样的内容：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions         # 或 "anthropic_messages"
  default: gpt-5.4-mini              # 你的部署 / 模型名称
  context_length: 400000             # 自动检测
```

以及在 `~/.hermes/.env` 中：

```
AZURE_FOUNDRY_API_KEY=<your-azure-key>
```

## OpenAI 风格端点（GPT、Llama 等） {#openai-style-endpoints-gpt-llama-etc}

Azure OpenAI 的 v1 GA 端点接受标准的 `openai` Python 客户端，只需进行最小更改：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  default: gpt-5.4
```

重要行为：

- **GPT-5.x、codex 和 o 系列自动路由到 Responses API。** Azure Foundry 将 GPT-5 / codex / o1 / o3 / o4 模型部署为仅支持 Responses API — 对这些模型调用 `/chat/completions` 会返回 `400 "The requested operation is unsupported."`。Hermes 通过名称检测这些模型系列，并透明地将 `api_mode` 升级为 `codex_responses`，即使 `config.yaml` 中仍然写着 `api_mode: chat_completions`。GPT-4、GPT-4o、Llama、Mistral 和其他部署则继续使用 `/chat/completions`。
- **自动使用 `max_completion_tokens`。** Azure OpenAI（与直接 OpenAI 一样）要求对 gpt-4o、o 系列和 gpt-5.x 模型使用 `max_completion_tokens`。Hermes 会根据端点发送正确的参数。
- **需要 `api-version` 的 v1 之前端点。** 如果你有一个旧版基础 URL，例如 `https://&lt;resource&gt;.openai.azure.com/openai?api-version=2025-04-01-preview`，Hermes 会提取查询字符串并通过 `default_query` 在每个请求中转发（否则 OpenAI SDK 在拼接路径时会丢弃它）。
## Anthropic 风格端点（通过 Azure Foundry 使用 Claude） {#anthropic-style-endpoints-claude-via-azure-foundry}

对于 Claude 部署，请使用 Anthropic 风格的路由：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.services.ai.azure.com/anthropic
  api_mode: anthropic_messages
  default: claude-sonnet-4-6
```

重要行为：

- **`/v1` 会从 base URL 中剥离。** Anthropic SDK 会在每个请求 URL 后追加 `/v1/messages`——Hermes 会在将 URL 交给 SDK 之前移除末尾的 `/v1`，以避免出现双重 `/v1` 路径。
- **`api-version` 通过 `default_query` 发送，而不是追加到 URL 中。** Azure Anthropic 要求一个 `api-version` 查询字符串。如果将其硬编码到 base URL 中，会产生类似 `/anthropic?api-version=.../v1/messages` 的错误路径，并返回 404。Hermes 改为通过 Anthropic SDK 的 `default_query` 传递 `api-version=2025-04-15`。
- **OAuth 令牌刷新已禁用。** Azure 部署使用静态 API 密钥。对于 Azure 端点，会显式跳过适用于 Anthropic Console 的 `~/.claude/.credentials.json` OAuth 令牌刷新循环，以防止 Claude Code OAuth 令牌在会话中途覆盖你的 Azure 密钥。

## 替代方案：`provider: anthropic` + Azure base URL {#alternative-provider-anthropic-azure-base-url}

如果你已经配置了 `provider: anthropic`，只想将其指向 Azure AI Foundry 以使用 Claude，你可以完全跳过 `azure-foundry` provider：

```yaml
model:
  provider: anthropic
  base_url: https://my-resource.services.ai.azure.com/anthropic
  key_env: AZURE_ANTHROPIC_KEY
  default: claude-sonnet-4-6
```

并在 `~/.hermes/.env` 中设置 `AZURE_ANTHROPIC_KEY`。Hermes 会在 base URL 中检测到 `azure.com`，并绕过 Claude Code OAuth 令牌链，从而直接使用 Azure 密钥进行 `x-api-key` 认证。

`key_env` 是规范的 snake_case 字段名；`api_key_env`（以及驼峰式 `keyEnv` / `apiKeyEnv`）可作为别名接受。如果同时设置了 `key_env` 和 `AZURE_ANTHROPIC_KEY`/`ANTHROPIC_API_KEY`，则以 `key_env` 命名的环境变量优先。

## 模型发现 {#model-discovery}

Azure **不**提供纯 API 密钥端点来列出你*已部署*的模型部署。部署枚举需要 Azure Resource Manager 认证（`az cognitiveservices account deployment list`）并配合 Azure AD 主体，而不是推理 API 密钥。

Hermes 可以做到的是：

- Azure OpenAI v1 端点（`&lt;resource&gt;.openai.azure.com/openai/v1`）会暴露 `GET /models`，返回该资源的**可用**模型目录。Hermes 使用此列表预填充模型选择器。
- Azure Foundry `/anthropic` 路由：通过 URL 路径检测，模型名称手动输入。
- 私有/防火墙端点：手动输入，并显示友好的“无法探测”消息。

你可以直接输入部署名称——Hermes 不会对返回的列表进行验证。

## 环境变量 {#environment-variables}

| 变量 | 用途 |
|----------|---------|
| `AZURE_FOUNDRY_API_KEY` | Azure AI Foundry / Azure OpenAI 的主要 API 密钥 |
| `AZURE_FOUNDRY_BASE_URL` | 端点 URL（通过 `hermes model` 设置；环境变量作为后备） |
| `AZURE_ANTHROPIC_KEY` | 由 `provider: anthropic` + Azure base URL 使用（`ANTHROPIC_API_KEY` 的替代方案） |
## 故障排除 {#troubleshooting}

**gpt-5.x 部署返回 401 Unauthorized。**
Azure 上 gpt-5.x 的访问路径是 `/chat/completions`，而不是 `/responses`。当 URL 中包含 `openai.azure.com` 时，Hermes 会自动处理；但如果看到 401 错误并提示 `Invalid API key`，请检查 `config.yaml` 中的 `api_mode` 是否为 `chat_completions`。

**访问 `/v1/messages?api-version=.../v1/messages` 返回 404。**
这是修复前 Azure Anthropic 配置中常见的格式错误 URL 问题。升级 Hermes 即可——`api-version` 参数现在通过 `default_query` 传递，而不像之前那样直接拼接到 base URL 中，因此 SDK 在拼接 URL 时不会导致参数错乱。

**向导提示“自动检测不完整”。**
端点拒绝了 `/models` 探测以及 Anthropic Messages 探测。对于位于防火墙后或设置了 IP 白名单的私有端点，这属于正常现象。请回退到手动选择 API 模式，并输入你的部署名称——其他一切仍能正常工作，只是 Hermes 无法预填选择器。

**选择了错误的传输方式。**
再次运行 `hermes model`，向导会重新探测。如果探测结果仍然不正确，可以直接编辑 `config.yaml`：

```yaml
model:
  provider: azure-foundry
  api_mode: anthropic_messages   # 或使用 chat_completions
```

## 相关 {#related}

- [环境变量](/reference/environment-variables)
- [配置项](/user-guide/configuration)
- [AWS Bedrock](/guides/aws-bedrock) —— 另一家主流云服务商集成
