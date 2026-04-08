---
sidebar_position: 5
title: "添加 Provider"
description: "如何为 Hermes Agent 添加新的推理 Provider —— 涵盖认证、运行时解析、CLI 流程、适配器、测试和文档"
---

# 添加 Provider

Hermes 已经可以通过自定义 Provider 路径与任何兼容 OpenAI 的端点进行通信。除非你想为该服务提供一流的 UX，否则不要添加内置 Provider：

- 特定于 Provider 的认证或令牌刷新
- 精选的模型目录
- 设置 / `hermes model` 菜单条目
- 用于 `provider:model` 语法的 Provider 别名
- 需要适配器的非 OpenAI API 格式

如果该 Provider 只是“另一个 OpenAI 兼容的基准 URL 和 API 密钥”，那么一个命名的自定义 Provider 可能就足够了。

## 心理模型

一个内置的 Provider 必须在以下几个层级保持一致：

1. `hermes_cli/auth.py` 决定如何查找凭据。
2. `hermes_cli/runtime_provider.py` 将其转换为运行时数据：
   - `provider`
   - `api_mode`
   - `base_url`
   - `api_key`
   - `source`
3. `run_agent.py` 使用 `api_mode` 来决定如何构建和发送请求。
4. `hermes_cli/models.py` 和 `hermes_cli/main.py` 让 Provider 显示在 CLI 中。（`hermes_cli/setup.py` 会自动委托给 `main.py` —— 那里不需要改动。）
5. `agent/auxiliary_client.py` 和 `agent/model_metadata.py` 确保辅助任务和 Token 预算正常工作。

最重要的抽象是 `api_mode`。

- 大多数 Provider 使用 `chat_completions`。
- Codex 使用 `codex_responses`。
- Anthropic 使用 `anthropic_messages`。
- 一个新的非 OpenAI 协议通常意味着需要添加一个新的适配器和一个新的 `api_mode` 分支。

## 首先选择实现路径

### 路径 A — 兼容 OpenAI 的 Provider

当 Provider 接受标准的 chat-completions 风格请求时使用此路径。

典型工作：

- 添加认证元数据
- 添加模型目录 / 别名
- 添加运行时解析
- 添加 CLI 菜单关联
- 添加辅助模型（aux-model）默认值
- 添加测试和用户文档

你通常不需要新的适配器或新的 `api_mode`。

### 路径 B — 原生 Provider

当 Provider 的行为不像 OpenAI chat completions 时使用此路径。

目前代码库中的例子：

- `codex_responses`
- `anthropic_messages`

此路径包括路径 A 的所有内容，外加：

- 在 `agent/` 中添加 Provider 适配器
- 在 `run_agent.py` 中为请求构建、分发、用量提取、中断处理和响应归一化添加分支
- 适配器测试

## 文件清单

### 每个内置 Provider 必选

1. `hermes_cli/auth.py`
2. `hermes_cli/models.py`
3. `hermes_cli/runtime_provider.py`
4. `hermes_cli/main.py`
5. `agent/auxiliary_client.py`
6. `agent/model_metadata.py`
7. 测试
8. `website/docs/` 下的用户文档

:::tip
`hermes_cli/setup.py` **不需要**修改。设置向导会将 Provider/模型选择委托给 `main.py` 中的 `select_provider_and_model()` —— 在那里添加的任何 Provider 都会自动在 `hermes setup` 中可用。
:::

### 原生 / 非 OpenAI Provider 额外必选

10. `agent/<provider>_adapter.py`
11. `run_agent.py`
12. 如果需要 Provider SDK，则需修改 `pyproject.toml`

## 第 1 步：选择一个规范的 Provider ID

选择一个唯一的 Provider ID 并处处使用它。

代码库中的例子：

- `openai-codex`
- `kimi-coding`
- `minimax-cn`

同一个 ID 应该出现在：

- `hermes_cli/auth.py` 中的 `PROVIDER_REGISTRY`
- `hermes_cli/models.py` 中的 `_PROVIDER_LABELS`
- `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中的 `_PROVIDER_ALIASES`
- `hermes_cli/main.py` 中的 CLI `--provider` 选项
- 设置 / 模型选择分支
- 辅助模型默认值
- 测试

如果 ID 在这些文件之间不一致，Provider 会感觉只连接了一半：认证可能正常，但 `/model`、设置或运行时解析会静默失效。

## 第 2 步：在 `hermes_cli/auth.py` 中添加认证元数据

对于使用 API 密钥的 Provider，在 `PROVIDER_REGISTRY` 中添加一个 `ProviderConfig` 条目，包含：

- `id`
- `name`
- `auth_type="api_key"`
- `inference_base_url`
- `api_key_env_vars`
- 可选的 `base_url_env_var`

同时在 `_PROVIDER_ALIASES` 中添加别名。

参考现有的 Provider 作为模板：

- 简单的 API 密钥路径：Z.AI, MiniMax
- 带有端点检测的 API 密钥路径：Kimi, Z.AI
- 原生令牌解析：Anthropic
- OAuth / 认证存储路径：Nous, OpenAI Codex

这里需要回答的问题：

- Hermes 应该检查哪些环境变量，优先级顺序是什么？
- 该 Provider 是否需要覆盖基准 URL？
- 是否需要端点探测或令牌刷新？
- 缺少凭据时，认证错误应该显示什么？

如果 Provider 需要的不仅仅是“查找 API 密钥”，请添加专门的凭据解析器，而不是将逻辑塞进无关的分支。

## 第 3 步：在 `hermes_cli/models.py` 中添加模型目录和别名

更新 Provider 目录，使 Provider 在菜单和 `provider:model` 语法中生效。

典型的编辑内容：

- `_PROVIDER_MODELS`
- `_PROVIDER_LABELS`
- `_PROVIDER_ALIASES`
- `list_available_providers()` 内部的 Provider 显示顺序
- 如果 Provider 支持实时 `/models` 获取，则修改 `provider_model_ids()`

如果 Provider 暴露了实时模型列表，请优先使用它，并将 `_PROVIDER_MODELS` 作为静态备选。

该文件也是让如下输入生效的关键：

```text
anthropic:claude-sonnet-4-6
kimi:model-name
```

如果这里缺少别名，Provider 可能认证成功，但在解析 `/model` 时仍会失败。

## 第 4 步：在 `hermes_cli/runtime_provider.py` 中解析运行时数据

`resolve_runtime_provider()` 是 CLI、网关、cron、ACP 和辅助客户端使用的共享路径。

添加一个分支，返回一个至少包含以下内容的字典：

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

如果 Provider 兼容 OpenAI，`api_mode` 通常应保持为 `chat_completions`。

注意 API 密钥的优先级。Hermes 已经包含了防止将 OpenRouter 密钥泄露到无关端点的逻辑。新 Provider 应该同样明确哪个密钥对应哪个基准 URL。

## 第 5 步：在 `hermes_cli/main.py` 中关联 CLI

在交互式的 `hermes model` 流程中显示之前，Provider 是不可发现的。

在 `hermes_cli/main.py` 中更新以下内容：

- `provider_labels` 字典
- `select_provider_and_model()` 中的 `providers` 列表
- Provider 分发逻辑 (`if selected_provider == ...`)
- `--provider` 参数选项
- 如果 Provider 支持登录/注销流程，更新相关选项
- 一个 `_model_flow_<provider>()` 函数，或者如果适用，复用 `_model_flow_api_key_provider()`

:::tip
`hermes_cli/setup.py` 不需要修改 —— 它调用 `main.py` 中的 `select_provider_and_model()`，因此你的新 Provider 会自动出现在 `hermes model` 和 `hermes setup` 中。
:::

## 第 6 步：保持辅助调用正常工作

这里涉及两个文件：

### `agent/auxiliary_client.py`

如果这是一个直接的 API 密钥 Provider，请在 `_API_KEY_PROVIDER_AUX_MODELS` 中添加一个廉价/快速的默认辅助模型。

辅助任务包括：

- 视觉摘要
- 网页提取摘要
- 上下文压缩摘要
- 会话搜索摘要
- 内存刷新

如果 Provider 没有合理的辅助默认值，侧边任务可能会回退失败，或者意外使用昂贵的主模型。

### `agent/model_metadata.py`

添加该 Provider 模型的上下文长度，以便 Token 预算、压缩阈值和限制保持正常。

## 第 7 步：如果 Provider 是原生的，添加适配器和 `run_agent.py` 支持

如果 Provider 不是纯粹的 chat completions，请将特定于 Provider 的逻辑隔离在 `agent/<provider>_adapter.py` 中。

让 `run_agent.py` 专注于编排。它应该调用适配器助手，而不是在文件各处内联手动构建 Provider 的 Payload。

原生 Provider 通常需要在以下地方进行工作：

### 新适配器文件

典型职责：

- 构建 SDK / HTTP 客户端
- 解析令牌
- 将 OpenAI 风格的对话消息转换为 Provider 的请求格式
- 如果需要，转换工具（tool） Schema
- 将 Provider 响应归一化为 `run_agent.py` 预期的格式
- 提取用量（usage）和结束原因（finish-reason）数据

### `run_agent.py`

搜索 `api_mode` 并审计每个切换点。至少要验证：
- `__init__` 选择了新的 `api_mode`
- 客户端构建对该提供商有效
- `_build_api_kwargs()` 知道如何格式化请求
- `_api_call_with_interrupt()` 调度到了正确的客户端调用
- 中断 / 客户端重建路径正常工作
- 响应验证接受该提供商的数据结构
- 结束原因（finish-reason）提取正确
- Token 使用量提取正确
- 备用模型（fallback-model）激活可以平滑切换到新提供商
- 摘要生成和内存刷新路径仍然有效

同时在 `run_agent.py` 中搜索 `self.client.`。任何假设存在标准 OpenAI 客户端的代码路径，在原生提供商使用不同的客户端对象或 `self.client = None` 时都可能崩溃。

### Prompt 缓存和提供商特定的请求字段

Prompt 缓存和提供商特定的调节参数很容易出现回归问题。

代码库中已有的例子：

- Anthropic 有原生的 Prompt 缓存路径
- OpenRouter 拥有提供商路由字段
- 并非每个提供商都应该接收每个请求侧选项

当你添加原生提供商时，请仔细检查 Hermes 是否只发送了该提供商真正理解的字段。

## 第 8 步：测试

至少要修改负责提供商连接（wiring）的测试。

常见位置：

- `tests/test_runtime_provider_resolution.py`
- `tests/test_cli_provider_resolution.py`
- `tests/test_cli_model_command.py`
- `tests/test_setup_model_selection.py`
- `tests/test_provider_parity.py`
- `tests/test_run_agent.py`
- 如果是原生提供商，还有 `tests/test_<provider>_adapter.py`

对于仅包含文档的示例，确切的文件集可能会有所不同。重点是要覆盖：

- 身份验证解析
- CLI 菜单 / 提供商选择
- 运行时提供商解析
- Agent 执行路径
- provider:model 解析
- 任何适配器特定的消息转换

在禁用 xdist 的情况下运行测试：

```bash
source venv/bin/activate
python -m pytest tests/test_runtime_provider_resolution.py tests/test_cli_provider_resolution.py tests/test_cli_model_command.py tests/test_setup_model_selection.py -n0 -q
```

对于更深层的更改，在推送前运行完整测试套件：

```bash
source venv/bin/activate
python -m pytest tests/ -n0 -q
```

## 第 9 步：实机验证

测试完成后，进行一次真实的冒烟测试。

```bash
source venv/bin/activate
python -m hermes_cli.main chat -q "Say hello" --provider your-provider --model your-model
```

如果你修改了菜单，也要测试交互流程：

```bash
source venv/bin/activate
python -m hermes_cli.main model
python -m hermes_cli.main setup
```

对于原生提供商，至少验证一次工具调用（tool call），而不仅仅是纯文本响应。

## 第 10 步：更新面向用户的文档

如果该提供商打算作为一级选项发布，也要更新用户文档：

- `website/docs/getting-started/quickstart.md`
- `website/docs/user-guide/configuration.md`
- `website/docs/reference/environment-variables.md`

开发者可能完美地连接了提供商，但如果没更新文档，用户仍然无法发现所需的各种环境变量或设置流程。

## OpenAI 兼容提供商检查清单

如果提供商使用标准的 chat completions 接口，请使用此清单。

- [ ] 在 `hermes_cli/auth.py` 中添加了 `ProviderConfig`
- [ ] 在 `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中添加了别名
- [ ] 在 `hermes_cli/models.py` 中添加了模型目录
- [ ] 在 `hermes_cli/runtime_provider.py` 中添加了运行时分支
- [ ] 在 `hermes_cli/main.py` 中添加了 CLI 连接（setup.py 会自动继承）
- [ ] 在 `agent/auxiliary_client.py` 中添加了辅助模型
- [ ] 在 `agent/model_metadata.py` 中添加了上下文长度
- [ ] 更新了运行时 / CLI 测试
- [ ] 更新了用户文档

## 原生提供商检查清单

当提供商需要新的协议路径时，请使用此清单。

- [ ] OpenAI 兼容检查清单中的所有项
- [ ] 在 `agent/<provider>_adapter.py` 中添加了适配器
- [ ] `run_agent.py` 支持新的 `api_mode`
- [ ] 中断 / 重建路径正常工作
- [ ] 使用量和结束原因提取正常工作
- [ ] 备用路径正常工作
- [ ] 添加了适配器测试
- [ ] 实机冒烟测试通过

## 常见陷阱

### 1. 将提供商添加到 auth 但未添加到模型解析

这会导致凭据解析正确，但 `/model` 和 `provider:model` 输入失败。

### 2. 忘记 `config["model"]` 可以是字符串或字典

许多提供商选择代码必须对这两种形式进行归一化。

### 3. 假设必须添加内置提供商

如果服务只是 OpenAI 兼容的，自定义提供商可能已经解决了用户问题，且维护成本更低。

### 4. 忘记辅助路径

主聊天路径可能工作正常，但摘要生成、内存刷新或视觉辅助工具可能会失败，因为辅助路由从未更新。

### 5. 隐藏在 `run_agent.py` 中的原生提供商分支

搜索 `api_mode` 和 `self.client.`。不要假设显式的请求路径是唯一的路径。

### 6. 向其他提供商发送仅限 OpenRouter 的参数

像提供商路由（provider routing）之类的字段仅属于支持它们的提供商。

### 7. 更新了 `hermes model` 但未更新 `hermes setup`

这两个流程都需要了解该提供商。

## 实现时的良好搜索目标

如果你正在寻找提供商涉及的所有位置，请搜索这些符号：

- `PROVIDER_REGISTRY`
- `_PROVIDER_ALIASES`
- `_PROVIDER_MODELS`
- `resolve_runtime_provider`
- `_model_flow_`
- `select_provider_and_model`
- `api_mode`
- `_API_KEY_PROVIDER_AUX_MODELS`
- `self.client.`

## 相关文档

- [提供商运行时解析](./provider-runtime.md)
- [架构](./architecture.md)
- [贡献指南](./contributing.md)
