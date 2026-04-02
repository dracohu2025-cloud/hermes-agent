---
title: 备用 Providers
description: 当主模型不可用时，配置自动切换到备用 LLM Providers。
sidebar_label: 备用 Providers
sidebar_position: 8
---

# 备用 Providers

Hermes Agent 有三层容错机制，确保当 Providers 出现问题时你的会话依然能继续：

1. **[凭证池](./credential-pools.md)** — 在*同一* Provider 的多个 API Key 之间轮换（优先尝试）
2. **主模型备用** — 当主模型失败时，自动切换到*不同*的 provider:model
3. **辅助任务备用** — 针对视觉、压缩、网页提取等辅助任务，独立的 Provider 解析

凭证池负责同一 Provider 的轮换（例如多个 OpenRouter Key）。本页介绍跨 Provider 的备用机制。两者都是可选且独立工作的。

## 主模型备用

当你的主 LLM Provider 遇到错误——限流、服务器过载、认证失败、连接中断——Hermes 可以在会话中途自动切换到备用的 provider:model，且不会丢失对话内容。

### 配置

在 `~/.hermes/config.yaml` 中添加 `fallback_model` 部分：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

`provider` 和 `model` 都是**必填**，缺一则禁用备用。

### 支持的 Providers

| Provider | 值 | 需求 |
|----------|----|------|
| AI Gateway | `ai-gateway` | `AI_GATEWAY_API_KEY` |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` |
| Nous Portal | `nous` | `hermes login`（OAuth） |
| OpenAI Codex | `openai-codex` | `hermes model`（ChatGPT OAuth） |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` 或 Claude Code 凭证 |
| z.ai / GLM | `zai` | `GLM_API_KEY` |
| Kimi / Moonshot | `kimi-coding` | `KIMI_API_KEY` |
| MiniMax | `minimax` | `MINIMAX_API_KEY` |
| MiniMax (中国) | `minimax-cn` | `MINIMAX_CN_API_KEY` |
| Kilo Code | `kilocode` | `KILOCODE_API_KEY` |
| 阿里巴巴 / DashScope | `alibaba` | `DASHSCOPE_API_KEY` |
| Hugging Face | `huggingface` | `HF_TOKEN` |
| 自定义端点 | `custom` | `base_url` + `api_key_env`（见下文） |

### 自定义端点备用

对于自定义的 OpenAI 兼容端点，添加 `base_url` 和可选的 `api_key_env`：

```yaml
fallback_model:
  provider: custom
  model: my-local-model
  base_url: http://localhost:8000/v1
  api_key_env: MY_LOCAL_KEY          # 包含 API Key 的环境变量名
```

### 备用触发时机

当主模型出现以下情况时，备用会自动启用：

- **限流**（HTTP 429）— 重试用尽后
- **服务器错误**（HTTP 500、502、503）— 重试用尽后
- **认证失败**（HTTP 401、403）— 立即切换（重试无意义）
- **未找到**（HTTP 404）— 立即切换
- **无效响应** — API 连续返回格式错误或空响应

触发时，Hermes 会：

1. 解析备用 Provider 的凭证
2. 创建新的 API 客户端
3. 就地替换模型、Provider 和客户端
4. 重置重试计数，继续会话

切换过程无缝——你的对话历史、工具调用和上下文都会保留。Agent 会从断点继续，只是换了模型。

:::info 一次性触发
备用每个会话**最多触发一次**。如果备用 Provider 也失败，正常错误处理接管（重试，然后报错）。这样避免了连锁故障循环。
:::

### 示例

**OpenRouter 作为 Anthropic native 的备用：**
```yaml
model:
  provider: anthropic
  default: claude-sonnet-4-6

fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

**Nous Portal 作为 OpenRouter 的备用：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4

fallback_model:
  provider: nous
  model: nous-hermes-3
```

**本地模型作为云端的备用：**
```yaml
fallback_model:
  provider: custom
  model: llama-3.1-70b
  base_url: http://localhost:8000/v1
  api_key_env: LOCAL_API_KEY
```

**Codex OAuth 作为备用：**
```yaml
fallback_model:
  provider: openai-codex
  model: gpt-5.3-codex
```

### 备用适用场景

| 场景 | 支持备用 |
|------|----------|
| CLI 会话 | ✔ |
| 消息网关（Telegram、Discord 等） | ✔ |
| 子 Agent 委托 | ✘（子 Agents 不继承备用配置） |
| 定时任务 | ✘（固定 Provider 运行） |
| 辅助任务（视觉、压缩） | ✘（使用独立 Provider 链，见下文） |

:::tip
`fallback_model` 没有环境变量，只能通过 `config.yaml` 配置。这是有意为之：备用配置是有意识的选择，不应被过时的 shell 导出覆盖。
:::

---

## 辅助任务备用

Hermes 为辅助任务使用独立的轻量模型。每个任务有自己的 Provider 解析链，内置备用机制。

### 独立 Provider 解析的任务

| 任务 | 功能 | 配置键 |
|------|------|--------|
| 视觉 | 图像分析、浏览器截图 | `auxiliary.vision` |
| 网页提取 | 网页摘要 | `auxiliary.web_extract` |
| 压缩 | 上下文压缩摘要 | `auxiliary.compression` 或 `compression.summary_provider` |
| 会话搜索 | 过去会话摘要 | `auxiliary.session_search` |
| 技能中心 | 技能搜索与发现 | `auxiliary.skills_hub` |
| MCP | MCP 辅助操作 | `auxiliary.mcp` |
| 内存清理 | 内存整合 | `auxiliary.flush_memories` |

### 自动检测链

当任务的 Provider 设置为 `"auto"`（默认）时，Hermes 会按顺序尝试 Providers，直到成功：

**文本任务（压缩、网页提取等）：**

```text
OpenRouter → Nous Portal → 自定义端点 → Codex OAuth →
API Key Providers（z.ai、Kimi、MiniMax、Hugging Face、Anthropic）→ 放弃
```

**视觉任务：**

```text
主 Provider（如果支持视觉）→ OpenRouter → Nous Portal →
Codex OAuth → Anthropic → 自定义端点 → 放弃
```

如果调用时解析的 Provider 失败，Hermes 还有内部重试：如果 Provider 不是 OpenRouter 且未设置显式 `base_url`，会尝试用 OpenRouter 作为最后的备用。

### 配置辅助 Providers

每个任务可在 `config.yaml` 中独立配置：

```yaml
auxiliary:
  vision:
    provider: "auto"              # auto | openrouter | nous | codex | main | anthropic
    model: ""                     # 例如 "openai/gpt-4o"
    base_url: ""                  # 直接端点（优先于 provider）
    api_key: ""                   # base_url 的 API Key

  web_extract:
    provider: "auto"
    model: ""

  compression:
    provider: "auto"
    model: ""

  session_search:
    provider: "auto"
    model: ""

  skills_hub:
    provider: "auto"
    model: ""

  mcp:
    provider: "auto"
    model: ""

  flush_memories:
    provider: "auto"
    model: ""
```

以上任务都遵循相同的 **provider / model / base_url** 模式。上下文压缩有自己的顶层配置块：

```yaml
compression:
  summary_provider: main                             # 与辅助任务相同的 Provider 选项
  summary_model: google/gemini-3-flash-preview
  summary_base_url: null                             # 自定义 OpenAI 兼容端点
```

备用模型使用：

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
  # base_url: http://localhost:8000/v1               # 可选自定义端点
```

辅助、压缩、备用三者工作方式相同：设置 `provider` 选择请求处理者，`model` 选择模型，`base_url` 指向自定义端点（覆盖 provider）。

### 辅助任务的 Provider 选项

| Provider | 说明 | 需求 |
|----------|------|------|
| `"auto"` | 按顺序尝试 Providers，直到成功（默认） | 至少配置一个 Provider |
| `"openrouter"` | 强制使用 OpenRouter | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | `hermes login` |
| `"codex"` | 强制使用 Codex OAuth | `hermes model` → Codex |
| `"main"` | 使用主 Agent 当前的 Provider | 主 Provider 已配置 |
| `"anthropic"` | 强制使用 Anthropic native | `ANTHROPIC_API_KEY` 或 Claude Code 凭证 |

---
### 直接端点覆盖

对于任何辅助任务，设置 `base_url` 会完全绕过提供者解析，直接将请求发送到该端点：

```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 优先于 `provider`。Hermes 使用配置的 `api_key` 进行认证，如果未设置则回退到 `OPENAI_API_KEY`。它**不会**为自定义端点重用 `OPENROUTER_API_KEY`。

---

## 上下文压缩回退

上下文压缩除了辅助系统外，还有一个遗留的配置路径：

```yaml
compression:
  summary_provider: "auto"                    # auto | openrouter | nous | main
  summary_model: "google/gemini-3-flash-preview"
```

这相当于配置了 `auxiliary.compression.provider` 和 `auxiliary.compression.model`。如果两者都设置了，`auxiliary.compression` 的值优先。

如果没有可用的压缩提供者，Hermes 会丢弃中间的对话轮次而不生成摘要，而不是让会话失败。

---

## 委派提供者覆盖

通过 `delegate_task` 生成的子 Agent **不会**使用主回退模型。但它们可以被路由到不同的 provider:model 组合以优化成本：

```yaml
delegation:
  provider: "openrouter"                      # 覆盖所有子 Agent 的提供者
  model: "google/gemini-3-flash-preview"      # 覆盖模型
  # base_url: "http://localhost:1234/v1"      # 或使用直接端点
  # api_key: "local-key"
```

完整配置详情请参见 [Subagent Delegation](/user-guide/features/delegation)。

---

## 定时任务提供者

定时任务运行时使用执行时配置的提供者。它们不支持回退模型。若要为定时任务使用不同的提供者，请在定时任务本身配置 `provider` 和 `model` 覆盖：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

完整配置详情请参见 [Scheduled Tasks (Cron)](/user-guide/features/cron)。

---

## 总结

| 功能           | 回退机制                                   | 配置位置                          |
|----------------|--------------------------------------------|----------------------------------|
| 主 Agent 模型  | config.yaml 中的 `fallback_model` — 出错时一次性切换 | 顶层 `fallback_model:`            |
| 视觉           | 自动检测链 + 内部 OpenRouter 重试           | `auxiliary.vision`                |
| 网页提取       | 自动检测链 + 内部 OpenRouter 重试           | `auxiliary.web_extract`           |
| 上下文压缩     | 自动检测链，若不可用则降级为无摘要           | `auxiliary.compression` 或 `compression.summary_provider` |
| 会话搜索       | 自动检测链                                 | `auxiliary.session_search`        |
| 技能中心       | 自动检测链                                 | `auxiliary.skills_hub`            |
| MCP 辅助       | 自动检测链                                 | `auxiliary.mcp`                   |
| 内存刷新       | 自动检测链                                 | `auxiliary.flush_memories`        |
| 委派           | 仅提供者覆盖（无自动回退）                   | `delegation.provider` / `delegation.model` |
| 定时任务       | 仅单个任务的提供者覆盖（无自动回退）           | 单个任务的 `provider` / `model`  |

---
