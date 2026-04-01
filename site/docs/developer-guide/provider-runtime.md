---
sidebar_position: 4
title: "Provider 运行时解析"
description: "Hermes 如何在运行时解析 provider、凭证、API 模式以及辅助模型"
---

# Provider 运行时解析

Hermes 使用一个共享的 provider 运行时解析器，应用于：

- CLI
- gateway
- cron 任务
- ACP
- 辅助模型调用

主要实现位于：

- `hermes_cli/runtime_provider.py` — 凭证解析，`_resolve_custom_runtime()`
- `hermes_cli/auth.py` — provider 注册表，`resolve_provider()`
- `hermes_cli/model_switch.py` — 共享的 `/model` 切换管道（CLI + gateway）
- `agent/auxiliary_client.py` — 辅助模型路由

如果你正在尝试添加一个新的第一方推理 provider，请结合本页阅读[添加 Providers](./adding-providers.md)。

## 解析优先级

从高层次看，provider 解析使用以下顺序：

1.  显式的 CLI/运行时请求
2.  `config.yaml` 中的模型/provider 配置
3.  环境变量
4.  provider 特定的默认值或自动解析

这个顺序很重要，因为 Hermes 将保存的模型/provider 选择视为常规运行的唯一真实来源。这可以防止一个过时的 shell 环境变量在用户不知情的情况下覆盖其在 `hermes model` 中最后选择的端点。

## Providers

当前的 provider 系列包括：

- AI Gateway (Vercel)
- OpenRouter
- Nous Portal
- OpenAI Codex
- Anthropic (原生)
- Z.AI
- Kimi / Moonshot
- MiniMax
- MiniMax China
- 自定义 (`provider: custom`) — 用于任何 OpenAI 兼容端点的第一方 provider
- 命名的自定义 provider（`config.yaml` 中的 `custom_providers` 列表）

## 运行时解析的输出

运行时解析器返回的数据包括：

- `provider`
- `api_mode`
- `base_url`
- `api_key`
- `source`
- 特定于 provider 的元数据，如过期/刷新信息

## 为什么这很重要

这个解析器是 Hermes 能够在以下组件之间共享认证/运行时逻辑的主要原因：

- `hermes chat`
- gateway 消息处理
- 在新会话中运行的 cron 任务
- ACP 编辑器会话
- 辅助模型任务

## AI Gateway

在 `~/.hermes/.env` 中设置 `AI_GATEWAY_API_KEY` 并使用 `--provider ai-gateway` 运行。Hermes 从 gateway 的 `/models` 端点获取可用模型，并筛选出支持工具使用的语言模型。

## OpenRouter、AI Gateway 和自定义的 OpenAI 兼容基础 URL

当存在多个 provider 密钥时（例如 `OPENROUTER_API_KEY`、`AI_GATEWAY_API_KEY` 和 `OPENAI_API_KEY`），Hermes 包含逻辑以避免将错误的 API 密钥泄露给自定义端点。

每个 provider 的 API 密钥都限定在其自己的基础 URL：

- `OPENROUTER_API_KEY` 仅发送到 `openrouter.ai` 端点
- `AI_GATEWAY_API_KEY` 仅发送到 `ai-gateway.vercel.sh` 端点
- `OPENAI_API_KEY` 用于自定义端点，并作为后备方案

Hermes 还会区分：

-   用户选择的真实自定义端点
-   当没有配置自定义端点时使用的 OpenRouter 后备路径

这种区分对于以下情况尤为重要：

-   本地模型服务器
-   非 OpenRouter/非 AI Gateway 的 OpenAI 兼容 API
-   无需重新运行设置即可切换 provider
-   即使当前 shell 中没有导出 `OPENAI_BASE_URL`，也应继续工作的、保存在配置中的自定义端点

## 原生 Anthropic 路径

Anthropic 不再仅仅是“通过 OpenRouter”了。

当 provider 解析选择 `anthropic` 时，Hermes 使用：

- `api_mode = anthropic_messages`
- 原生的 Anthropic Messages API
- `agent/anthropic_adapter.py` 进行转换

对于原生 Anthropic 的凭证解析，现在当两者都存在时，优先选择可刷新的 Claude Code 凭证，而不是复制的环境变量令牌。实际上这意味着：

-   当 Claude Code 凭证文件包含可刷新的认证信息时，它们被视为首选来源
-   手动的 `ANTHROPIC_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` 值仍然可以作为显式覆盖项使用
-   Hermes 在调用原生 Messages API 之前会预检 Anthropic 凭证刷新
-   Hermes 在重建 Anthropic 客户端后，仍会在 401 错误时重试一次，作为后备路径

## OpenAI Codex 路径

Codex 使用一个独立的 Responses API 路径：

- `api_mode = codex_responses`
- 专用的凭证解析和认证存储支持

## 辅助模型路由

辅助任务，例如：

-   视觉
-   网页提取摘要
-   上下文压缩摘要
-   会话搜索摘要
-   技能中心操作
-   MCP 助手操作
-   内存刷新

可以使用它们自己的 provider/模型路由，而不是主要的对话模型。

当辅助任务配置为使用 `main` provider 时，Hermes 会通过与普通聊天相同的共享运行时路径来解析它。实际上这意味着：

-   由环境变量驱动的自定义端点仍然有效
-   通过 `hermes model` / `config.yaml` 保存的自定义端点也有效
-   辅助路由可以区分真实保存的自定义端点和 OpenRouter 后备方案

## 后备模型

Hermes 支持配置一个后备模型/provider 对，允许在主模型遇到错误时进行运行时故障转移。

### 内部工作原理

1.  **存储**：`AIAgent.__init__` 存储 `fallback_model` 字典并设置 `_fallback_activated = False`。

2.  **触发点**：在 `run_agent.py` 的主重试循环中，从三个地方调用 `_try_activate_fallback()`：
    -   在无效 API 响应（空选择、缺少内容）达到最大重试次数后
    -   在不可重试的客户端错误（HTTP 401、403、404）时
    -   在瞬时错误（HTTP 429、500、502、503）达到最大重试次数后

3.  **激活流程** (`_try_activate_fallback`)：
    -   如果已激活或未配置，立即返回 `False`
    -   调用 `auxiliary_client.py` 中的 `resolve_provider_client()` 以构建具有正确认证的新客户端
    -   确定 `api_mode`：对于 openai-codex 为 `codex_responses`，对于 anthropic 为 `anthropic_messages`，其他情况为 `chat_completions`
    -   就地交换：`self.model`、`self.provider`、`self.base_url`、`self.api_mode`、`self.client`、`self._client_kwargs`
    -   对于 anthropic 后备：构建原生 Anthropic 客户端，而不是 OpenAI 兼容的客户端
    -   重新评估提示词缓存（对 OpenRouter 上的 Claude 模型启用）
    -   设置 `_fallback_activated = True` — 防止再次触发
    -   将重试计数重置为 0 并继续循环

4.  **配置流程**：
    -   CLI：`cli.py` 读取 `CLI_CONFIG["fallback_model"]` → 传递给 `AIAgent(fallback_model=...)`
    -   Gateway：`gateway/run.py._load_fallback_model()` 读取 `config.yaml` → 传递给 `AIAgent`
    -   验证：`provider` 和 `model` 键都必须非空，否则禁用后备功能

### 不支持后备的情况

-   **子 Agent 委托** (`tools/delegate_tool.py`)：子 Agent 继承父级的 provider，但不继承后备配置
-   **Cron 任务** (`cron/`)：使用固定的 provider 运行，无后备机制
-   **辅助任务**：使用其自身独立的 provider 自动检测链（参见上文的辅助模型路由）

### 测试覆盖

有关涵盖所有支持的 provider、一次性语义和边缘情况的全面测试，请参阅 `tests/test_fallback_model.py`。

## 相关文档

-   [Agent 循环内部原理](./agent-loop.md)
-   [ACP 内部原理](./acp-internals.md)
-   [上下文压缩与提示词缓存](./context-compression-and-caching.md)
