---
sidebar_position: 4
title: "Provider 运行时解析"
description: "Hermes 如何在运行时解析 Provider、凭据、API 模式和辅助模型"
---

# Provider 运行时解析 {#provider-runtime-resolution}

Hermes 拥有一套通用的 Provider 运行时解析器，用于以下场景：

- CLI
- Gateway
- Cron 任务
- ACP
- 辅助模型调用

核心实现：

- `hermes_cli/runtime_provider.py` — 凭据解析，`_resolve_custom_runtime()`
- `hermes_cli/auth.py` — Provider 注册表，`resolve_provider()`
- `hermes_cli/model_switch.py` — 通用的 `/model` 切换流水线（CLI + Gateway）
- `agent/auxiliary_client.py` — 辅助模型路由

如果你打算添加一个新的原生推理 Provider，请在阅读本页的同时参考 [添加 Provider](./adding-providers.md)。

## 解析优先级 {#resolution-precedence}

从高层级来看，Provider 解析遵循以下顺序：

1. 显式的 CLI/运行时请求
2. `config.yaml` 中的模型/Provider 配置
3. 环境变量
4. Provider 特定的默认值或自动解析

这个顺序非常重要，因为 Hermes 将保存的模型/Provider 选择视为常规运行的“单一真理来源”。这可以防止过时的 shell 环境变量静默覆盖用户上次在 `hermes model` 中选择的端点。

## Providers {#providers}

目前的 Provider 家族包括：

- AI Gateway (Vercel)
- OpenRouter
- Nous Portal
- OpenAI Codex
- Copilot / Copilot ACP
- Anthropic (原生)
- Google / Gemini
- Alibaba / DashScope (通义千问)
- DeepSeek
- Z.AI
- Kimi / Moonshot
- MiniMax
- MiniMax China
- Kilo Code
- Hugging Face
- OpenCode Zen / OpenCode Go
- Custom (`provider: custom`) — 适用于任何兼容 OpenAI 接口端点的原生 Provider
- 命名的自定义 Provider (`config.yaml` 中的 `custom_providers` 列表)

## 运行时解析的输出 {#output-of-runtime-resolution}

运行时解析器返回如下数据：

- `provider`
- `api_mode`
- `base_url`
- `api_key`
- `source`
- Provider 特定的元数据（如过期/刷新信息）

## 为什么这很重要 {#why-this-matters}

该解析器是 Hermes 能够在以下组件间共享认证/运行时逻辑的核心原因：

- `hermes chat`
- Gateway 消息处理
- 在新会话中运行的 Cron 任务
- ACP 编辑器会话
- 辅助模型任务

## AI Gateway {#ai-gateway}

在 `~/.hermes/.env` 中设置 `AI_GATEWAY_API_KEY` 并使用 `--provider ai-gateway` 运行。Hermes 会从 Gateway 的 `/models` 端点获取可用模型，并过滤出支持 Tool-use 的语言模型。

## OpenRouter, AI Gateway 以及自定义 OpenAI 兼容 Base URL {#openrouter-ai-gateway-and-custom-openai-compatible-base-urls}

Hermes 包含一套逻辑，用于在存在多个 Provider 密钥（例如 `OPENROUTER_API_KEY`、`AI_GATEWAY_API_KEY` 和 `OPENAI_API_KEY`）时，避免将错误的 API Key 泄露给自定义端点。

每个 Provider 的 API Key 都被限定在各自的 Base URL 范围内：

- `OPENROUTER_API_KEY` 仅发送至 `openrouter.ai` 端点
- `AI_GATEWAY_API_KEY` 仅发送至 `ai-gateway.vercel.sh` 端点
- `OPENAI_API_KEY` 用于自定义端点以及作为备选项

Hermes 还会区分：

- 用户选择的真实自定义端点
- 未配置自定义端点时使用的 OpenRouter 备选路径

这种区分对于以下场景尤为重要：

- 本地模型服务器
- 非 OpenRouter/非 AI Gateway 的 OpenAI 兼容 API
- 在不重新运行设置的情况下切换 Provider
- 即使当前 shell 中未导出 `OPENAI_BASE_URL`，也应保持有效的配置保存型自定义端点

## 原生 Anthropic 路径 {#native-anthropic-path}

Anthropic 不再仅仅通过 "OpenRouter" 访问。

当 Provider 解析选择 `anthropic` 时，Hermes 使用：

- `api_mode = anthropic_messages`
- 原生 Anthropic Messages API
- `agent/anthropic_adapter.py` 进行协议转换

对于原生 Anthropic 的凭据解析，当两者同时存在时，现在更倾向于使用可刷新的 Claude Code 凭据，而不是复制的环境变量 Token。在实践中这意味着：

- 当 Claude Code 凭据文件包含可刷新认证时，它们被视为首选来源
- 手动设置的 `ANTHROPIC_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` 仍可作为显式覆盖项生效
- Hermes 在调用原生 Messages API 之前会预检 Anthropic 凭据刷新
- 作为备选路径，Hermes 在重建 Anthropic 客户端后，遇到 401 错误仍会重试一次

## OpenAI Codex 路径 {#openai-codex-path}

Codex 使用独立的 Responses API 路径：

- `api_mode = codex_responses`
- 专用的凭据解析和认证存储支持

## 辅助模型路由 {#auxiliary-model-routing}

辅助任务如：

- 视觉 (Vision)
- 网页提取摘要
- 上下文压缩摘要
- 会话搜索摘要
- Skills Hub 操作
- MCP 辅助操作
- 内存刷新 (Memory flushes)

可以使用它们自己的 Provider/模型路由，而不是主对话模型。

当辅助任务配置为 Provider `main` 时，Hermes 会通过与普通聊天相同的共享运行时路径进行解析。在实践中这意味着：

- 环境变量驱动的自定义端点仍然有效
- 通过 `hermes model` / `config.yaml` 保存的自定义端点也有效
- 辅助路由可以区分真实的已保存自定义端点和 OpenRouter 备选项

## 备选模型 (Fallback models) {#fallback-models}

Hermes 支持配置备选模型/Provider 对，允许在主模型遇到错误时进行运行时故障转移。

### 内部工作原理 {#how-it-works-internally}

1. **存储**：`AIAgent.__init__` 存储 `fallback_model` 字典并设置 `_fallback_activated = False`。

2. **触发点**：`_try_activate_fallback()` 在 `run_agent.py` 主重试循环的三个位置被调用：
   - 在无效 API 响应（None 选择、内容缺失）达到最大重试次数后
   - 遇到不可重试的客户端错误（HTTP 401, 403, 404）时
   - 在瞬时错误（HTTP 429, 500, 502, 503）达到最大重试次数后

3. **激活流程** (`_try_activate_fallback`)：
   - 如果已激活或未配置，立即返回 `False`
   - 调用 `auxiliary_client.py` 中的 `resolve_provider_client()` 以构建带有正确认证的新客户端
   - 确定 `api_mode`：openai-codex 使用 `codex_responses`，anthropic 使用 `anthropic_messages`，其他使用 `chat_completions`
   - 原地替换：`self.model`, `self.provider`, `self.base_url`, `self.api_mode`, `self.client`, `self._client_kwargs`
   - 对于 Anthropic 备选：构建原生 Anthropic 客户端而非 OpenAI 兼容客户端
   - 重新评估 Prompt 缓存（在 OpenRouter 上为 Claude 模型启用）
   - 设置 `_fallback_activated = True` — 防止再次触发
   - 将重试计数重置为 0 并继续循环

4. **配置流程**：
   - CLI：`cli.py` 读取 `CLI_CONFIG["fallback_model"]` → 传递给 `AIAgent(fallback_model=...)`
   - Gateway：`gateway/run.py._load_fallback_model()` 读取 `config.yaml` → 传递给 `AIAgent`
   - 校验：`provider` 和 `model` 键都必须非空，否则禁用备选机制

### 不支持备选的情况 {#what-does-not-support-fallback}

- **Sub-agent 委派** (`tools/delegate_tool.py`)：Sub-agents 继承父级的 Provider，但不继承备选配置
- **Cron 任务** (`cron/`)：使用固定 Provider 运行，没有备选机制
- **辅助任务**：使用它们自己独立的 Provider 自动检测链（见上文“辅助模型路由”）

### 测试覆盖 {#test-coverage}

参见 `tests/test_fallback_model.py` 获取涵盖所有支持的 Provider、单次触发语义和边缘情况的全面测试。

## 相关文档 {#related-docs}

- [Agent 循环原理](./agent-loop.md)
- [ACP 原理](./acp-internals.md)
- [上下文压缩与 Prompt 缓存](./context-compression-and-caching.md)
