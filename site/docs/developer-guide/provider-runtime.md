---
sidebar_position: 4
title: "Provider 运行时解析"
description: "Hermes 如何在运行时解析 provider、凭证、API 模式及辅助模型"
---

<a id="provider-runtime-resolution"></a>
# Provider 运行时解析

Hermes 有一个共享的 provider 运行时解析器，用于以下场景：

- CLI
- 网关（gateway）
- 定时任务
- ACP
- 辅助模型调用

主要实现：

- `hermes_cli/runtime_provider.py` — 凭证解析，`_resolve_custom_runtime()`
- `hermes_cli/auth.py` — provider 注册表，`resolve_provider()`
- `hermes_cli/model_switch.py` — 共享的 `/model` 切换流水线（CLI + 网关）
- `agent/auxiliary_client.py` — 辅助模型路由
- `providers/` — ABC 及注册入口（`ProviderProfile`, `register_provider`, `get_provider_profile`, `list_providers`）
- `plugins/model-providers/&lt;name&gt;/` — 每个 provider 的插件（内置），声明 `api_mode`、`base_url`、`env_vars`、`fallback_models`，并在首次访问时自动注册到注册表。用户放置在 `$HERMES_HOME/plugins/model-providers/&lt;name&gt;/` 下的插件会覆盖同名的内置插件。

`providers/` 中的 `get_provider_profile()` 根据给定的 provider id 返回一个 `ProviderProfile`。`runtime_provider.py` 在解析时调用它来获取规范的 `base_url`、`env_vars` 优先级列表、`api_mode` 和 `fallback_models`，从而无需在多个文件中重复这些数据。只需在 `plugins/model-providers/&lt;your-provider&gt;/`（或 `$HERMES_HOME/plugins/model-providers/&lt;your-provider&gt;/`）下新建一个插件并调用 `register_provider()`，`runtime_provider.py` 就能识别它——解析器本身无需添加分支。

如果你想添加一个新的一等推理 provider，请先阅读[添加 Provider](./adding-providers.md) 和[模型 Provider 插件指南](./model-provider-plugin.md)，再结合本页一起理解。

<a id="resolution-precedence"></a>
## 解析优先级

从高层来看，provider 的解析顺序是：

1. 显式的 CLI/运行时请求
2. `config.yaml` 中的模型/provider 配置
3. 环境变量
4. provider 特定的默认值或自动解析

这个顺序很重要，因为 Hermes 将保存的模型/provider 选择视为正常运行的唯一可信来源。这样可以防止过时的 shell 导出变量静默覆盖用户上次在 `hermes model` 中选择的端点。

<a id="providers"></a>
## Providers

当前的 provider 系列包括（完整的内置集合见 `plugins/model-providers/`）：

- AI Gateway (Vercel)
- OpenRouter
- Nous Portal
- OpenAI Codex
- Copilot / Copilot ACP
- Anthropic（原生）
- Google / Gemini（`gemini`, `google-gemini-cli`）
- Alibaba / DashScope（`alibaba`, `alibaba-coding-plan`）
- DeepSeek
- Z.AI
- Kimi / Moonshot（`kimi-coding`, `kimi-coding-cn`）
- MiniMax（`minimax`, `minimax-cn`, `minimax-oauth`）
- Kilo Code
- Hugging Face
- OpenCode Zen / OpenCode Go
- AWS Bedrock
- Azure Foundry
- NVIDIA NIM
- xAI (Grok)
- Arcee
- GMI Cloud
- StepFun
- Qwen OAuth
- Xiaomi
- Ollama Cloud
- LM Studio
- Tencent TokenHub
- 自定义（`provider: custom`）—— 针对任何兼容 OpenAI 的端点的第一等 provider
- 命名自定义 provider（`config.yaml` 中的 `custom_providers` 列表）

<a id="output-of-runtime-resolution"></a>
## 运行时解析的输出

运行时解析器返回的数据包括：

- `provider`
- `api_mode`
- `base_url`
- `api_key`
- `source`
- provider 特定的元数据，如过期/刷新信息
<a id="why-this-matters"></a>
## 为什么这一点很重要

这个解析器是 Hermes 能够在以下场景之间共享认证/运行时逻辑的主要原因：

- `hermes chat`
- 网关消息处理
- 在新会话中运行的 cron 任务
- ACP 编辑器会话
- 辅助模型任务

<a id="ai-gateway"></a>
## AI 网关

在 `~/.hermes/.env` 中设置 `AI_GATEWAY_API_KEY`，并附带 `--provider ai-gateway` 参数启动。Hermes 会从网关的 `/models` 端点获取可用模型，并过滤出支持工具使用的语言模型。

<a id="openrouter-ai-gateway-and-custom-openai-compatible-base-urls"></a>
## OpenRouter、AI 网关和自定义 OpenAI 兼容的 base URL

Hermes 包含避免在存在多个 Provider 密钥（例如 `OPENROUTER_API_KEY`、`AI_GATEWAY_API_KEY` 和 `OPENAI_API_KEY`）时将错误的 API 密钥泄漏到自定义端点的逻辑。

每个 Provider 的 API 密钥都限定在其自己的 base URL 范围内：

- `OPENROUTER_API_KEY` 仅发送给 `openrouter.ai` 端点
- `AI_GATEWAY_API_KEY` 仅发送给 `ai-gateway.vercel.sh` 端点
- `OPENAI_API_KEY` 用于自定义端点，并作为后备方案

Hermes 还会区分：

- 用户选择的真实自定义端点
- 当未配置自定义端点时使用的 OpenRouter 后备路径

这一区别对于以下情况尤其重要：

- 本地模型服务器
- 非 OpenRouter/非 AI 网关的 OpenAI 兼容 API
- 无需重新运行设置即可切换 Provider
- 配置保存的自定义端点，即使当前 shell 未导出 `OPENAI_BASE_URL` 也应继续工作

<a id="native-anthropic-path"></a>
## 原生 Anthropic 路径

Anthropic 不再仅仅是“通过 OpenRouter”使用。

当 Provider 解析选择 `anthropic` 时，Hermes 会使用：

- `api_mode = anthropic_messages`
- 原生 Anthropic Messages API
- `agent/anthropic_adapter.py` 进行转换

对于原生 Anthropic 的凭据解析，现在在同时存在可刷新 Claude Code 凭据和复制的环境令牌时，会优先使用可刷新的 Claude Code 凭据。实际操作中这意味着：

- 当 Claude Code 凭据文件包含可刷新的认证信息时，它会被视为首选来源
- 手动设置的 `ANTHROPIC_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` 值仍然可以作为显式覆盖生效
- Hermes 在调用原生 Messages API 之前，会预先刷新 Anthropic 凭据
- Hermes 在重建 Anthropic 客户端后，如果遇到 401 错误，仍然会重试一次，作为后备路径

<a id="openai-codex-path"></a>
## OpenAI Codex 路径

Codex 使用单独的 Responses API 路径：

- `api_mode = codex_responses`
- 专用的凭据解析和认证存储支持

<a id="auxiliary-model-routing"></a>
## 辅助模型路由

辅助任务，例如：

- 视觉
- 网页提取摘要
- 上下文压缩摘要
- Skills Hub 操作
- MCP 辅助操作
- 内存刷新

可以使用它们自己的 Provider/模型路由，而不是使用主要的对话模型。

当辅助任务配置为 Provider `main` 时，Hermes 会通过与正常聊天相同的共享运行时路径来解析。实际操作中这意味着：

- 环境变量驱动的自定义端点仍然有效
- 通过 `hermes model` / `config.yaml` 保存的自定义端点也有效
- 辅助路由能够区分真实保存的自定义端点和 OpenRouter 后备路径
<a id="fallback-models"></a>
## Fallback models

Hermes 支持配置一个降级提供商链——即一个由 `(provider, model)` 条目组成的列表，当主模型遇到错误时，会按顺序依次尝试。为了向后兼容，旧的单对 `fallback_model` 字典仍然被接受（并在首次写入时进行迁移）。

<a id="how-it-works-internally"></a>
### 内部工作方式

1. **存储**：`AIAgent.__init__` 存储 `fallback_model` 字典，并将 `_fallback_activated` 设为 `False`。

2. **触发点**：`_try_activate_fallback()` 会在 `run_agent.py` 的主重试循环中的三个地方被调用：
   - API 响应无效（choices 为空、content 缺失）且达到最大重试次数后
   - 遇到不可重试的客户端错误（HTTP 401、403、404）时
   - 瞬时错误（HTTP 429、500、502、503）达到最大重试次数后

3. **激活流程**（`_try_activate_fallback`）：
   - 如果已经激活或未配置，立即返回 `False`
   - 调用 `auxiliary_client.py` 中的 `resolve_provider_client()` 来构建一个带有正确认证信息的新客户端
   - 确定 `api_mode`：对于 openai-codex 使用 `codex_responses`，对于 anthropic 使用 `anthropic_messages`，其余情况使用 `chat_completions`
   - 原地替换：`self.model`、`self.provider`、`self.base_url`、`self.api_mode`、`self.client`、`self._client_kwargs`
   - 对于 Anthropic 降级：构建一个原生的 Anthropic 客户端，而不是兼容 OpenAI 的客户端
   - 重新评估提示缓存（对 OpenRouter 上的 Claude 模型启用）
   - 将 `_fallback_activated` 设为 `True`——阻止再次触发
   - 将重试计数重置为 0，继续循环

4. **配置流程**：
   - CLI：`cli.py` 读取 `CLI_CONFIG["fallback_model"]` → 传递给 `AIAgent(fallback_model=...)`
   - 网关：`gateway/run.py._load_fallback_model()` 读取 `config.yaml` → 传递给 `AIAgent`
   - 验证：`provider` 和 `model` 键都必须非空，否则降级功能被禁用

<a id="what-does-not-support-fallback"></a>
### 不支持降级的情况

- **子 Agent 委托**（`tools/delegate_tool.py`）：子 Agent 继承父 Provider，但不继承降级配置
- **辅助任务**：使用自己独立的提供商自动检测链（详见上面的辅助模型路由）

Cron 任务**支持**降级：`run_job()` 从 `config.yaml` 读取 `fallback_providers`（或旧的 `fallback_model`），并传递给 `AIAgent(fallback_model=...)`，与网关的 `_load_fallback_model()` 模式一致。参见 [Cron 内部机制](./cron-internals.md)。

<a id="test-coverage"></a>
### 测试覆盖

关于所有支持提供商、一次性语义和边界情况的全面测试，请参见 `tests/test_fallback_model.py`。

<a id="related-docs"></a>
## 相关文档

- [Agent 循环内部机制](./agent-loop.md)
- [ACP 内部机制](./acp-internals.md)
- [上下文压缩与提示缓存](./context-compression-and-caching.md)
