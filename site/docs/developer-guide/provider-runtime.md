---
sidebar_position: 4
title: "Provider 运行时解析"
description: "Hermes 如何在运行时解析 provider、凭据、API 模式以及辅助模型"
---

# Provider 运行时解析 {#provider-runtime-resolution}

Hermes 有一个共享的 provider 运行时解析器，用于以下场景：

- CLI
- gateway
- cron 任务
- ACP
- 辅助模型调用

主要实现：

- `hermes_cli/runtime_provider.py` — 凭据解析，`_resolve_custom_runtime()`
- `hermes_cli/auth.py` — provider 注册表，`resolve_provider()`
- `hermes_cli/model_switch.py` — 共享的 `/model` 切换管道（CLI + gateway）
- `agent/auxiliary_client.py` — 辅助模型路由

如果你正在尝试添加一个新的第一方推理 provider，请同时阅读[添加 Provider](./adding-providers.md) 和本页。

## 解析优先级 {#resolution-precedence}

从高层来看，provider 解析使用以下顺序：

1. 显式的 CLI / 运行时请求
2. `config.yaml` 中的模型 / provider 配置
3. 环境变量
4. provider 特定的默认值或自动解析

这个顺序很重要，因为 Hermes 将保存的模型 / provider 选择视为正常运行的真相来源。这可以防止过时的 shell 导出变量静默覆盖用户上次在 `hermes model` 中选择的端点。

## Providers {#providers}

当前的 provider 系列包括：

- AI Gateway (Vercel)
- OpenRouter
- Nous Portal
- OpenAI Codex
- Copilot / Copilot ACP
- Anthropic (原生)
- Google / Gemini
- Alibaba / DashScope
- DeepSeek
- Z.AI
- Kimi / Moonshot
- MiniMax
- MiniMax China
- Kilo Code
- Hugging Face
- OpenCode Zen / OpenCode Go
- 自定义 (`provider: custom`) — 任何兼容 OpenAI 的端点的第一方 provider
- 命名自定义 provider（`config.yaml` 中的 `custom_providers` 列表）

## 运行时解析的输出 {#output-of-runtime-resolution}

运行时解析器返回的数据包括：

- `provider`
- `api_mode`
- `base_url`
- `api_key`
- `source`
- provider 特定的元数据，如过期 / 刷新信息

## 为什么这很重要 {#why-this-matters}

这个解析器是 Hermes 能够在以下场景之间共享认证 / 运行时逻辑的主要原因：

- `hermes chat`
- gateway 消息处理
- 在新会话中运行的 cron 任务
- ACP 编辑器会话
- 辅助模型任务

## AI Gateway {#ai-gateway}

在 `~/.hermes/.env` 中设置 `AI_GATEWAY_API_KEY`，并使用 `--provider ai-gateway` 运行。Hermes 从 gateway 的 `/models` 端点获取可用模型，并过滤出支持工具使用的语言模型。

## OpenRouter、AI Gateway 和自定义兼容 OpenAI 的 base URL {#openrouter-ai-gateway-and-custom-openai-compatible-base-urls}

Hermes 包含逻辑，以避免在存在多个 provider 密钥（例如 `OPENROUTER_API_KEY`、`AI_GATEWAY_API_KEY` 和 `OPENAI_API_KEY`）时将错误的 API 密钥泄露给自定义端点。

每个 provider 的 API 密钥都限定在其自己的 base URL 范围内：

- `OPENROUTER_API_KEY` 仅发送到 `openrouter.ai` 端点
- `AI_GATEWAY_API_KEY` 仅发送到 `ai-gateway.vercel.sh` 端点
- `OPENAI_API_KEY` 用于自定义端点，并作为回退

Hermes 还区分以下情况：

- 用户选择的真实自定义端点
- 未配置自定义端点时使用的 OpenRouter 回退路径

这种区分对于以下场景尤其重要：

- 本地模型服务器
- 非 OpenRouter / 非 AI Gateway 的兼容 OpenAI 的 API
- 无需重新运行设置即可切换 provider
- 配置中保存的自定义端点，即使当前 shell 中没有导出 `OPENAI_BASE_URL`，也应保持正常工作
## 原生 Anthropic 路径 {#native-anthropic-path}

Anthropic 不再只是“通过 OpenRouter”了。

当 provider 解析选择 `anthropic` 时，Hermes 会使用：

- `api_mode = anthropic_messages`
- 原生 Anthropic Messages API
- `agent/anthropic_adapter.py` 进行转换

原生 Anthropic 的凭据解析现在优先使用可刷新的 Claude Code 凭据，而不是复制的环境变量 token（当两者都存在时）。实际意味着：

- Claude Code 凭据文件在包含可刷新认证时被视为首选来源
- 手动设置的 `ANTHROPIC_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` 值仍然可以作为显式覆盖
- Hermes 在调用原生 Messages API 之前会预检 Anthropic 凭据刷新
- Hermes 在重建 Anthropic 客户端后，如果遇到 401 错误，仍会重试一次作为回退

## OpenAI Codex 路径 {#openai-codex-path}

Codex 使用独立的 Responses API 路径：

- `api_mode = codex_responses`
- 专用的凭据解析和认证存储支持

## 辅助模型路由 {#auxiliary-model-routing}

辅助任务，例如：

- 视觉
- 网页提取摘要
- 上下文压缩摘要
- 会话搜索摘要
- 技能中心操作
- MCP 辅助操作
- 内存刷新

可以使用它们自己的 provider/模型路由，而不是主对话模型。

当辅助任务配置了 provider `main` 时，Hermes 会通过与普通聊天相同的共享运行时路径来解析。实际意味着：

- 环境变量驱动的自定义端点仍然有效
- 通过 `hermes model` / `config.yaml` 保存的自定义端点也有效
- 辅助路由可以区分真正保存的自定义端点和 OpenRouter 回退

## 回退模型 {#fallback-models}

Hermes 支持配置的回退模型/provider 对，允许在主模型遇到错误时进行运行时故障转移。

### 内部工作原理 {#how-it-works-internally}

1. **存储**：`AIAgent.__init__` 存储 `fallback_model` 字典，并设置 `_fallback_activated = False`。

2. **触发点**：`_try_activate_fallback()` 在 `run_agent.py` 的主重试循环中的三个位置被调用：
   - 在 API 响应无效（None choices、缺少内容）达到最大重试次数后
   - 在不可重试的客户端错误（HTTP 401、403、404）上
   - 在临时错误（HTTP 429、500、502、503）达到最大重试次数后

3. **激活流程**（`_try_activate_fallback`）：
   - 如果已经激活或未配置，立即返回 `False`
   - 调用 `auxiliary_client.py` 中的 `resolve_provider_client()` 来构建一个带有正确认证的新客户端
   - 确定 `api_mode`：`codex_responses` 用于 openai-codex，`anthropic_messages` 用于 anthropic，其他情况使用 `chat_completions`
   - 原地替换：`self.model`、`self.provider`、`self.base_url`、`self.api_mode`、`self.client`、`self._client_kwargs`
   - 对于 anthropic 回退：构建原生 Anthropic 客户端，而不是 OpenAI 兼容客户端
   - 重新评估提示缓存（在 OpenRouter 上为 Claude 模型启用）
   - 设置 `_fallback_activated = True` — 防止再次触发
   - 将重试计数重置为 0 并继续循环
4. **配置流程**：
   - CLI：`cli.py` 读取 `CLI_CONFIG["fallback_model"]` → 传递给 `AIAgent(fallback_model=...)`
   - 网关：`gateway/run.py._load_fallback_model()` 读取 `config.yaml` → 传递给 `AIAgent`
   - 校验：`provider` 和 `model` 两个键都必须非空，否则回退功能被禁用

### 不支持回退的情况 {#what-does-not-support-fallback}

- **子 Agent 委托**（`tools/delegate_tool.py`）：子 Agent 继承父级的 provider，但不继承回退配置
- **辅助任务**：使用自己独立的 provider 自动检测链（参见上方的辅助模型路由）

Cron 任务**支持**回退：`run_job()` 从 `config.yaml` 读取 `fallback_providers`（或旧版 `fallback_model`），并将其传递给 `AIAgent(fallback_model=...)`，与网关的 `_load_fallback_model()` 模式一致。参见 [Cron 内部机制](./cron-internals.md)。

### 测试覆盖 {#test-coverage}

参见 `tests/test_fallback_model.py`，其中包含针对所有支持的 provider、一次性语义和边界情况的全面测试。

## 相关文档 {#related-docs}

- [Agent 循环内部机制](./agent-loop.md)
- [ACP 内部机制](./acp-internals.md)
- [上下文压缩与提示缓存](./context-compression-and-caching.md)
