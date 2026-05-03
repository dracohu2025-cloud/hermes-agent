---
sidebar_position: 5
title: "添加 Provider"
description: "如何为 Hermes Agent 添加新的推理 provider —— 认证、运行时解析、CLI 流程、适配器、测试和文档"
---

# 添加 Provider {#adding-providers}

Hermes 已经可以通过自定义 provider 路径与任何兼容 OpenAI 的端点通信。除非你希望为该服务提供一流的用户体验，否则不要添加内置 provider：

- provider 特定的认证或令牌刷新
- 精选的模型目录
- 设置 / `hermes model` 菜单项
- `provider:model` 语法的 provider 别名
- 需要适配器的非 OpenAI API 形态

如果该 provider 只是“另一个兼容 OpenAI 的基础 URL 和 API 密钥”，那么一个命名的自定义 provider 可能就足够了。

## 心智模型 {#the-mental-model}

一个内置 provider 需要在多个层面保持一致：

1. `hermes_cli/auth.py` 决定如何找到凭据。
2. `hermes_cli/runtime_provider.py` 将其转换为运行时数据：
   - `provider`
   - `api_mode`
   - `base_url`
   - `api_key`
   - `source`
3. `run_agent.py` 使用 `api_mode` 来决定如何构建和发送请求。
4. `hermes_cli/models.py` 和 `hermes_cli/main.py` 让 provider 出现在 CLI 中。（`hermes_cli/setup.py` 自动委托给 `main.py` —— 那里不需要修改。）
5. `agent/auxiliary_client.py` 和 `agent/model_metadata.py` 保持辅助任务和令牌预算正常工作。

重要的抽象是 `api_mode`。

- 大多数 provider 使用 `chat_completions`。
- Codex 使用 `codex_responses`。
- Anthropic 使用 `anthropic_messages`。
- 新的非 OpenAI 协议通常意味着添加一个新的适配器和一个新的 `api_mode` 分支。

## 首先选择实现路径 {#choose-the-implementation-path-first}

### 路径 A —— 兼容 OpenAI 的 provider {#path-a-openai-compatible-provider}

当 provider 接受标准的 chat-completions 风格请求时使用此路径。

典型工作：

- 添加认证元数据
- 添加模型目录 / 别名
- 添加运行时解析
- 添加 CLI 菜单连接
- 添加辅助模型默认值
- 添加测试和用户文档

通常不需要新的适配器或新的 `api_mode`。

### 路径 B —— 原生 provider {#path-b-native-provider}

当 provider 的行为不像 OpenAI chat completions 时使用此路径。

当前代码库中的示例：

- `codex_responses`
- `anthropic_messages`

此路径包含路径 A 的所有内容，外加：

- `agent/` 中的 provider 适配器
- `run_agent.py` 中的请求构建、分发、用量提取、中断处理和响应标准化分支
- 适配器测试

## 文件清单 {#file-checklist}

### 每个内置 provider 必需的文件 {#required-for-every-built-in-provider}

1. `hermes_cli/auth.py`
2. `hermes_cli/models.py`
3. `hermes_cli/runtime_provider.py`
4. `hermes_cli/main.py`
5. `agent/auxiliary_client.py`
6. `agent/model_metadata.py`
7. 测试
8. `website/docs/` 下的面向用户的文档

:::tip
`hermes_cli/setup.py` **不需要**修改。设置向导将 provider/model 选择委托给 `main.py` 中的 `select_provider_and_model()` —— 任何在那里添加的 provider 都会自动在 `hermes setup` 中可用。
:::

### 原生 / 非 OpenAI provider 额外需要的文件 {#additional-for-native-non-openai-providers}

10. `agent/&lt;provider&gt;_adapter.py`
11. `run_agent.py`
12. `pyproject.toml`（如果 provider SDK 是必需的）

## 步骤 1：选择一个规范的 provider id {#step-1-pick-one-canonical-provider-id}

选择一个单一的 provider id，并在所有地方使用它。

代码库中的示例：

- `openai-codex`
- `kimi-coding`
- `minimax-cn`
同一个 ID 应出现在以下位置：

- `hermes_cli/auth.py` 中的 `PROVIDER_REGISTRY`
- `hermes_cli/models.py` 中的 `_PROVIDER_LABELS`
- `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中的 `_PROVIDER_ALIASES`
- `hermes_cli/main.py` 中 CLI 的 `--provider` 选项
- setup / 模型选择分支
- 辅助模型的默认值
- 测试

如果这些文件中的 ID 不一致，该 provider 会感觉像半连接：认证可能正常，但 `/model`、setup 或运行时解析会静默地忽略它。

## 第 2 步：在 `hermes_cli/auth.py` 中添加认证元数据 {#step-2-add-auth-metadata-in-hermescli-auth-py}

对于 API 密钥类型的 provider，在 `PROVIDER_REGISTRY` 中添加一个 `ProviderConfig` 条目，包含：

- `id`
- `name`
- `auth_type="api_key"`
- `inference_base_url`
- `api_key_env_vars`
- 可选的 `base_url_env_var`

同时将别名添加到 `_PROVIDER_ALIASES`。

以现有 provider 为模板：

- 简单 API 密钥路径：Z.AI、MiniMax
- 带端点检测的 API 密钥路径：Kimi、Z.AI
- 原生令牌解析：Anthropic
- OAuth / 认证存储路径：Nous、OpenAI Codex

这里需要回答的问题：

- Hermes 应检查哪些环境变量，优先级顺序如何？
- provider 是否需要 base-URL 覆盖？
- 是否需要端点探测或令牌刷新？
- 当凭据缺失时，认证错误信息应如何表述？

如果 provider 需要的不仅仅是“查找一个 API 密钥”，请添加专门的凭据解析器，而不是将逻辑塞入不相关的分支。

## 第 3 步：在 `hermes_cli/models.py` 中添加模型目录和别名 {#step-3-add-model-catalog-and-aliases-in-hermescli-models-py}

更新 provider 目录，使该 provider 在菜单和 `provider:model` 语法中可用。

典型的修改：

- `_PROVIDER_MODELS`
- `_PROVIDER_LABELS`
- `_PROVIDER_ALIASES`
- `list_available_providers()` 中的 provider 显示顺序
- 如果 provider 支持实时 `/models` 获取，则修改 `provider_model_ids()`

如果 provider 暴露了实时模型列表，优先使用该列表，并将 `_PROVIDER_MODELS` 作为静态回退。

这个文件也是让以下输入生效的关键：

```text
anthropic:claude-sonnet-4-6
kimi:model-name
```

如果这里缺少别名，provider 可能认证成功，但在 `/model` 解析时仍然失败。

## 第 4 步：在 `hermes_cli/runtime_provider.py` 中解析运行时数据 {#step-4-resolve-runtime-data-in-hermescli-runtimeprovider-py}

`resolve_runtime_provider()` 是 CLI、网关、cron、ACP 和辅助客户端共享的路径。

添加一个分支，返回至少包含以下内容的字典：

```python
{
    "provider": "your-provider",
    "api_mode": "chat_completions",  # 或你的原生模式
    "base_url": "https://...",
    "api_key": "...",
    "source": "env|portal|auth-store|explicit",
    "requested_provider": requested_provider,
}
```

如果 provider 兼容 OpenAI，`api_mode` 通常应保持为 `chat_completions`。

注意 API 密钥的优先级。Hermes 已包含避免将 OpenRouter 密钥泄露到无关端点的逻辑。新 provider 应同样明确哪个密钥对应哪个 base URL。

## 第 5 步：在 `hermes_cli/main.py` 中接入 CLI {#step-5-wire-the-cli-in-hermescli-main-py}

一个 provider 只有在交互式 `hermes model` 流程中出现时才是可发现的。
在 `hermes_cli/main.py` 中更新以下内容：

- `provider_labels` 字典
- `select_provider_and_model()` 中的 `providers` 列表
- provider 分发逻辑（`if selected_provider == ...`）
- `--provider` 参数的选项列表
- 如果该 provider 支持登录/登出流程，则更新对应的选项
- 一个 `_model_flow_&lt;provider&gt;()` 函数，或者如果适用，复用 `_model_flow_api_key_provider()`

:::tip
`hermes_cli/setup.py` 不需要修改——它从 `main.py` 调用 `select_provider_and_model()`，因此你的新 provider 会自动出现在 `hermes model` 和 `hermes setup` 中。
:::

## 第 6 步：保持辅助调用正常工作 {#step-6-keep-auxiliary-calls-working}

这里涉及两个文件：

### `agent/auxiliary_client.py` {#agent-auxiliaryclient-py}

如果这是一个直接使用 API 密钥的 provider，请向 `_API_KEY_PROVIDER_AUX_MODELS` 添加一个廉价/快速的默认辅助模型。

辅助任务包括：

- 视觉摘要
- 网页提取摘要
- 上下文压缩摘要
- 会话搜索摘要
- 内存刷新

如果该 provider 没有合理的辅助默认模型，辅助任务可能会严重降级，或者意外地使用昂贵的主模型。

### `agent/model_metadata.py` {#agent-modelmetadata-py}

为 provider 的模型添加上下文长度，以便 token 预算、压缩阈值和限制保持合理。

## 第 7 步：如果 provider 是原生类型，添加适配器和 `run_agent.py` 支持 {#step-7-if-the-provider-is-native-add-an-adapter-and-runagent-py-support}

如果 provider 不是普通的聊天补全，请将 provider 特定的逻辑隔离到 `agent/&lt;provider&gt;_adapter.py` 中。

保持 `run_agent.py` 专注于编排。它应该调用适配器辅助函数，而不是在整个文件中内联构建 provider 的请求负载。

原生 provider 通常需要在以下地方进行工作：

### 新的适配器文件 {#new-adapter-file}

典型职责：

- 构建 SDK / HTTP 客户端
- 解析 token
- 将 OpenAI 风格的对话消息转换为 provider 的请求格式
- 如果需要，转换工具模式
- 将 provider 的响应标准化为 `run_agent.py` 期望的格式
- 提取使用量和完成原因数据

### `run_agent.py` {#runagent-py}

搜索 `api_mode` 并审计每个切换点。至少需要验证：

- `__init__` 选择了新的 `api_mode`
- 客户端构建对该 provider 有效
- `_build_api_kwargs()` 知道如何格式化请求
- `_interruptible_api_call()` 分发到正确的客户端调用
- 中断/客户端重建路径正常工作
- 响应验证接受 provider 的响应格式
- 完成原因提取正确
- token 使用量提取正确
- 回退模型激活可以干净地切换到新 provider
- 摘要生成和内存刷新路径仍然有效

同时搜索 `run_agent.py` 中的 `self.client.`。任何假设标准 OpenAI 客户端存在的代码路径，在原生 provider 使用不同的客户端对象或 `self.client = None` 时都可能出错。

### 提示缓存和 provider 特定的请求字段 {#prompt-caching-and-provider-specific-request-fields}

提示缓存和 provider 特定的配置项很容易退化。

代码库中已有的示例：

- Anthropic 有原生的提示缓存路径
- OpenRouter 获取 provider 路由字段
- 并非每个 provider 都应该接收所有请求端选项

当你添加原生 provider 时，请仔细检查 Hermes 是否只发送该 provider 实际能理解的字段。
## 步骤 8：测试 {#step-8-tests}

至少需要覆盖那些保护提供商（provider）接入的测试。

常见测试文件：

- `tests/test_runtime_provider_resolution.py`
- `tests/test_cli_provider_resolution.py`
- `tests/test_cli_model_command.py`
- `tests/test_setup_model_selection.py`
- `tests/test_provider_parity.py`
- `tests/test_run_agent.py`
- `tests/test_&lt;provider&gt;_adapter.py`（针对原生提供商）

对于仅文档示例，实际文件集可能有所不同。关键是要覆盖以下内容：

- 认证解析
- CLI 菜单 / 提供商选择
- 运行时提供商解析
- Agent 执行路径
- provider:model 解析
- 任何适配器特定的消息转换

使用禁用 xdist 的方式运行测试：

```bash
source venv/bin/activate
python -m pytest tests/test_runtime_provider_resolution.py tests/test_cli_provider_resolution.py tests/test_cli_model_command.py tests/test_setup_model_selection.py -n0 -q
```

对于更深入的改动，请在推送前运行完整测试套件：

```bash
source venv/bin/activate
python -m pytest tests/ -n0 -q
```

## 步骤 9：实时验证 {#step-9-live-verification}

测试通过后，运行一次真正的冒烟测试。

```bash
source venv/bin/activate
python -m hermes_cli.main chat -q "Say hello" --provider your-provider --model your-model
```

如果你修改了菜单，还需要测试交互式流程：

```bash
source venv/bin/activate
python -m hermes_cli.main model
python -m hermes_cli.main setup
```

对于原生提供商，除了纯文本响应外，还要验证至少一次工具调用。

## 步骤 10：更新面向用户的文档 {#step-10-update-user-facing-docs}

如果该提供商打算作为一等公民发布，请同时更新用户文档：

- `website/docs/getting-started/quickstart.md`
- `website/docs/user-guide/configuration.md`
- `website/docs/reference/environment-variables.md`

开发者可以完美地接入提供商，但仍然可能让用户无法发现所需的环境变量或设置流程。

## OpenAI 兼容提供商检查清单 {#openai-compatible-provider-checklist}

如果提供商是标准的聊天补全（chat completions），请使用此清单。

- [ ] 在 `hermes_cli/auth.py` 中添加 `ProviderConfig`
- [ ] 在 `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中添加别名
- [ ] 在 `hermes_cli/models.py` 中添加模型目录
- [ ] 在 `hermes_cli/runtime_provider.py` 中添加运行时分支
- [ ] 在 `hermes_cli/main.py` 中添加 CLI 接入（setup.py 会自动继承）
- [ ] 在 `agent/auxiliary_client.py` 中添加辅助模型
- [ ] 在 `agent/model_metadata.py` 中添加上下文长度
- [ ] 更新运行时 / CLI 测试
- [ ] 更新用户文档

## 原生提供商检查清单 {#native-provider-checklist}

当提供商需要新的协议路径时，请使用此清单。

- [ ] OpenAI 兼容检查清单中的所有项
- [ ] 在 `agent/&lt;provider&gt;_adapter.py` 中添加适配器
- [ ] 在 `run_agent.py` 中支持新的 `api_mode`
- [ ] 中断 / 重建路径正常工作
- [ ] 用量和结束原因提取正常工作
- [ ] 回退路径正常工作
- [ ] 添加适配器测试
- [ ] 实时冒烟测试通过

## 常见陷阱 {#common-pitfalls}

### 1. 将提供商添加到认证中，但未添加到模型解析中 {#1-adding-the-provider-to-auth-but-not-to-model-parsing}

这会导致凭据解析正确，但 `/model` 和 `provider:model` 输入失败。

### 2. 忘记 `config["model"]` 可以是字符串或字典 {#2-forgetting-that-config-model-can-be-a-string-or-a-dict}
许多提供商选择代码都需要对这两种形式进行归一化处理。

### 3. 假设内置提供商是必需的 {#3-assuming-a-built-in-provider-is-required}

如果服务只是兼容 OpenAI，自定义提供商可能已经能以更低的维护成本解决用户问题。

### 4. 忘记辅助路径 {#4-forgetting-auxiliary-paths}

主聊天路径可以正常工作，但摘要、内存刷新或视觉辅助功能可能因为辅助路由从未更新而失败。

### 5. 原生提供商分支隐藏在 `run_agent.py` 中 {#5-native-provider-branches-hiding-in-runagent-py}

搜索 `api_mode` 和 `self.client.`。不要假设显而易见的请求路径是唯一的。

### 6. 将仅适用于 OpenRouter 的参数发送给其他提供商 {#6-sending-openrouter-only-knobs-to-other-providers}

像 provider routing 这样的字段只应属于支持它们的提供商。

### 7. 更新了 `hermes model` 但没有更新 `hermes setup` {#7-updating-hermes-model-but-not-hermes-setup}

两个流程都需要了解该提供商。

## 实现时值得搜索的目标 {#good-search-targets-while-implementing}

如果你在查找提供商涉及的所有位置，请搜索以下符号：

- `PROVIDER_REGISTRY`
- `_PROVIDER_ALIASES`
- `_PROVIDER_MODELS`
- `resolve_runtime_provider`
- `_model_flow_`
- `select_provider_and_model`
- `api_mode`
- `_API_KEY_PROVIDER_AUX_MODELS`
- `self.client.`

## 相关文档 {#related-docs}

- [提供商运行时解析](./provider-runtime.md)
- [架构](./architecture.md)
- [贡献指南](./contributing.md)
