---
sidebar_position: 5
title: "添加提供商"
description: "如何为 Hermes Agent 添加新的推理提供商 — 认证、运行时解析、CLI 流程、适配器、测试和文档"
---

<a id="adding-providers"></a>
# 添加提供商

Hermes 已经能够通过自定义提供商路径与任何兼容 OpenAI 的端点通信。除非你希望为该服务提供一流的用户体验，否则不要添加内置提供商：

- 提供商特定的认证或令牌刷新
- 精心策划的模型目录
- 设置 / `hermes model` 菜单条目
- 用于 `provider:model` 语法的提供商别名
- 需要适配器的非 OpenAI API 形态

如果提供商只是“另一个兼容 OpenAI 的基础 URL 和 API 密钥”，那么一个命名的自定义提供商可能就足够了。

<a id="the-mental-model"></a>
## 心智模型

一个内置提供商需要在多个层面协调一致：

1. `hermes_cli/auth.py` 决定如何查找凭据。
2. `hermes_cli/runtime_provider.py` 将其转换为运行时数据：
   - `provider`
   - `api_mode`
   - `base_url`
   - `api_key`
   - `source`
3. `run_agent.py` 使用 `api_mode` 来决定如何构建和发送请求。
4. `hermes_cli/models.py` 和 `hermes_cli/main.py` 让提供商出现在 CLI 中。（`hermes_cli/setup.py` 自动委托给 `main.py` — 那里不需要更改。）
5. `agent/auxiliary_client.py` 和 `agent/model_metadata.py` 保持辅助任务和令牌预算的正常工作。

重要的抽象是 `api_mode`。

- 大多数提供商使用 `chat_completions`。
- Codex 使用 `codex_responses`。
- Anthropic 使用 `anthropic_messages`。
- 一个新的非 OpenAI 协议通常意味着添加一个新的适配器和一个新的 `api_mode` 分支。

<a id="choose-the-implementation-path-first"></a>
## 首先选择实现路径

<a id="path-a-openai-compatible-provider"></a>
### 路径 A — 兼容 OpenAI 的提供商

当提供商接受标准的聊天补全风格请求时使用此路径。

典型工作：

- 添加认证元数据
- 添加模型目录 / 别名
- 添加运行时解析
- 添加 CLI 菜单布线
- 添加辅助模型默认值
- 添加测试和用户文档

通常不需要新的适配器或新的 `api_mode`。

<a id="path-b-native-provider"></a>
### 路径 B — 原生提供商

当提供商的行为不同于 OpenAI 聊天补全时使用此路径。

当前树中的示例：

- `codex_responses`
- `anthropic_messages`

此路径包括路径 A 的所有内容，外加：

- `agent/` 中的提供商适配器
- `run_agent.py` 中用于请求构建、调度、用量提取、中断处理和响应规范化的分支
- 适配器测试

<a id="file-checklist"></a>
## 文件清单

<a id="required-for-every-built-in-provider"></a>
### 每个内置提供商必需

1. `hermes_cli/auth.py`
2. `hermes_cli/models.py`
3. `hermes_cli/runtime_provider.py`
4. `hermes_cli/main.py`
5. `agent/auxiliary_client.py`
6. `agent/model_metadata.py`
7. 测试
8. `website/docs/` 下的面向用户的文档

:::tip
`hermes_cli/setup.py` **不需要**修改。设置向导将提供/模型选择委托给 `main.py` 中的 `select_provider_and_model()` — 那里添加的任何提供商都会自动在 `hermes setup` 中可用。
:::

<a id="additional-for-native-non-openai-providers"></a>
### 原生/非 OpenAI 提供商额外需要

10. `agent/&lt;provider&gt;_adapter.py`
11. `run_agent.py`
12. 如果提供商需要 SDK，则 `pyproject.toml`

<a id="fast-path-simple-api-key-providers"></a>
## 快速路径：简单的 API 密钥提供商

如果你的提供商只是一个使用单一 API 密钥进行认证的兼容 OpenAI 的端点，则无需修改 `auth.py`、`runtime_provider.py`、`main.py` 或下方完整清单中的任何其他文件。
你只需要做到：

1. 在 `plugins/model-providers/&lt;your-provider&gt;/` 下创建一个插件目录，里面包含：
   - `__init__.py` — 在模块级别调用 `register_provider(profile)`
   - `plugin.yaml` — 清单文件（名称、kind: model-provider、版本、描述）
2. 仅此而已。当任何代码第一次调用 `get_provider_profile()` 或 `list_providers()` 时，Provider 插件会自动加载——本仓库内建的插件和位于 `$HERMES_HOME/plugins/model-providers/` 的用户插件都会被识别。

当你添加一个插件并调用 `register_provider()` 后，以下内容会自动衔接：

1. `auth.py` 中的 `PROVIDER_REGISTRY` 条目（凭据解析、环境变量查找）
2. `api_mode` 设置为 `chat_completions`
3. `base_url` 从配置或声明的环境变量中获取
4. `env_vars` 按优先级顺序检查 API 密钥
5. 为该 Provider 注册 `fallback_models` 列表
6. CLI 的 `--provider` 参数接受该 Provider 的 ID
7. `hermes model` 菜单中包含该 Provider
8. `hermes setup` 向导自动委托给 `main.py`
9. `provider:model` 别名语法生效
10. 运行时解析器返回正确的 `base_url` 和 `api_key`
11. `HERMES_INFERENCE_PROVIDER` 环境变量覆盖接受该 Provider ID
12. 后备模型激活可以无缝切换到该 Provider

位于 `$HERMES_HOME/plugins/model-providers/&lt;name&gt;/` 的用户插件会覆盖同名的内建插件（`register_provider()` 中后写者胜出）——因此第三方无需修改本仓库即可对任何内建 profile 进行猴子补丁或替换。

请参考 `plugins/model-providers/nvidia/` 或 `plugins/model-providers/gmi/` 作为模板，并查阅完整的 [Model Provider 插件指南](/developer-guide/model-provider-plugin) 了解字段参考、钩子惯用法和端到端示例。

<a id="full-path-oauth-and-complex-providers"></a>
## 完整路径：OAuth 和复杂 Provider

当你的 Provider 需要以下任何功能时，请使用下面的完整清单：

- OAuth 或令牌刷新（Nous Portal、Codex、Google Gemini、Qwen Portal、Copilot）
- 非 OpenAI API 形状，需要新的适配器（Anthropic Messages、Codex Responses）
- 自定义端点检测或多区域探测（z.ai、Kimi）
- 精心策划的静态模型目录或实时 `/models` 获取
- 具有专属认证流程的 Provider 特定 `hermes model` 菜单条目

<a id="step-1-pick-one-canonical-provider-id"></a>
## 步骤 1：选择一个规范的 Provider ID

选择一个单一的 Provider ID，并在所有地方使用它。

仓库中的示例：

- `openai-codex`
- `kimi-coding`
- `minimax-cn`

同样的 ID 应出现在以下位置：

- `hermes_cli/auth.py` 中的 `PROVIDER_REGISTRY`
- `hermes_cli/models.py` 中的 `_PROVIDER_LABELS`
- `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中的 `_PROVIDER_ALIASES`
- CLI `--provider` 选项（在 `hermes_cli/main.py` 中）
- 设置/模型选择分支
- 辅助模型默认值
- 测试

如果该 ID 在这些文件中不一致，Provider 会感觉像是半连接：认证可能工作，但 `/model`、setup 或运行时解析会静默遗漏。

<a id="step-2-add-auth-metadata-in-hermescli-auth-py"></a>
## 步骤 2：在 `hermes_cli/auth.py` 中添加认证元数据

对于 API 密钥 Provider，向 `PROVIDER_REGISTRY` 添加一个 `ProviderConfig` 条目，其中包含：
- `id`
- `name`
- `auth_type="api_key"`
- `inference_base_url`
- `api_key_env_vars`
- 可选的 `base_url_env_var`

同时将别名添加到 `_PROVIDER_ALIASES`。

以现有提供商为模板：

- 简单 API-key 路径：Z.AI、MiniMax
- 带端点检测的 API-key 路径：Kimi、Z.AI
- 原生令牌解析：Anthropic
- OAuth / 身份验证存储路径：Nous、OpenAI Codex

这里需要回答的问题：

- Hermes 应检查哪些环境变量，以及优先级顺序是什么？
- 该提供商是否需要 base-URL 覆盖？
- 是否需要端点探测或令牌刷新？
- 凭据缺失时，身份验证错误信息应如何提示？

如果提供商需要的不仅仅是“查找 API 密钥”，则应添加专门的凭据解析器，而不是将逻辑塞入不相关的分支。

<a id="step-3-add-model-catalog-and-aliases-in-hermescli-models-py"></a>
## 第三步：在 `hermes_cli/models.py` 中添加模型目录和别名

更新提供商目录，使提供商在菜单和 `provider:model` 语法中生效。

典型编辑：

- `_PROVIDER_MODELS`
- `_PROVIDER_LABELS`
- `_PROVIDER_ALIASES`
- `list_available_providers()` 内部的提供商显示顺序
- 若提供商支持实时 `/models` 获取，则使用 `provider_model_ids()`

如果提供商公开了实时模型列表，优先使用该列表，并将 `_PROVIDER_MODELS` 作为静态后备。

正是此文件使以下输入得以正常工作：

```text
anthropic:claude-sonnet-4-6
kimi:model-name
```

如果此处缺少别名，提供商可能成功进行身份验证，但仍在 `/model` 解析中失败。

<a id="step-4-resolve-runtime-data-in-hermescli-runtimeprovider-py"></a>
## 第四步：在 `hermes_cli/runtime_provider.py` 中解析运行时数据

`resolve_runtime_provider()` 是 CLI、网关、cron、ACP 和辅助客户端的共享路径。

添加一个分支，返回至少包含以下字段的字典：

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

如果提供商兼容 OpenAI，`api_mode` 通常应保持为 `chat_completions`。

注意 API 密钥的优先级。Hermes 已包含避免将 OpenRouter 密钥泄露到无关端点的逻辑。新提供商也应同样明确指定哪个密钥对应哪个 base URL。

<a id="step-5-wire-the-cli-in-hermescli-main-py"></a>
## 第五步：在 `hermes_cli/main.py` 中连接 CLI

提供商在交互式 `hermes model` 流程中出现之前是不可发现的。

在 `hermes_cli/main.py` 中更新以下内容：

- `provider_labels` 字典
- `select_provider_and_model()` 中的 `providers` 列表
- 提供商分派（`if selected_provider == ...`）
- `--provider` 参数选项
- 若提供商支持登录/注销流程，则添加相应选项
- 一个 `_model_flow_&lt;provider&gt;()` 函数，或若适用则复用 `_model_flow_api_key_provider()`

:::tip
`hermes_cli/setup.py` 无需更改——它从 `main.py` 调用 `select_provider_and_model()`，因此你的新提供商会自动出现在 `hermes model` 和 `hermes setup` 中。
:::

<a id="step-6-keep-auxiliary-calls-working"></a>
## 第六步：保持辅助调用正常运作

这里有两个关键文件：
<a id="agent-auxiliaryclient-py"></a>
### `agent/auxiliary_client.py`

如果这是一个直接的 API 密钥提供方，请将廉价 / 快速的默认辅助模型添加到 `_API_KEY_PROVIDER_AUX_MODELS`。

辅助任务包括：

- 视觉摘要
- 网页抽取摘要
- 上下文压缩摘要
- 会话搜索摘要
- 内存刷新

如果该提供方没有合理的辅助默认模型，辅助任务可能会严重降级，或者意外地使用昂贵的主模型。

<a id="agent-modelmetadata-py"></a>
### `agent/model_metadata.py`

为提供方的模型添加上下文长度，以便 token 预算、压缩阈值和限制保持合理。

<a id="step-7-if-the-provider-is-native-add-an-adapter-and-runagent-py-support"></a>
## 第 7 步：如果提供方是原生（native）的，添加适配器并支持 `run_agent.py`

如果提供方不是简单的对话补全（chat completions），请将特定于提供方的逻辑隔离在 `agent/&lt;provider&gt;_adapter.py` 中。

让 `run_agent.py` 专注于编排。它应调用适配器辅助函数，而不是在文件中到处内联构建提供方负载。

原生提供方通常需要在以下地方进行工作：

<a id="new-adapter-file"></a>
### 新的适配器文件

典型职责：

- 构建 SDK / HTTP 客户端
- 解析 token
- 将 OpenAI 风格的对话消息转换为提供方的请求格式
- 如有需要，转换工具模式（tool schemas）
- 将提供方响应标准化为 `run_agent.py` 所期望的格式
- 提取使用量和终止原因数据

<a id="runagent-py"></a>
### `run_agent.py`

搜索 `api_mode` 并审计每个切换点。至少验证以下内容：

- `__init__` 选择了新的 `api_mode`
- 客户端构造对提供方有效
- `_build_api_kwargs()` 知道如何格式化请求
- `_interruptible_api_call()` 分派到正确的客户端调用
- 中断 / 客户端重建路径正常工作
- 响应验证接受提供方的数据格式
- 终止原因提取正确
- token 使用量提取正确
- 回退模型激活可以干净地切换到新的提供方
- 摘要生成和内存刷新路径仍然正常工作

同时搜索 `run_agent.py` 中的 `self.client.`。任何假设标准 OpenAI 客户端存在的代码路径，在原生提供方使用不同的客户端对象或 `self.client = None` 时都可能出错。

<a id="prompt-caching-and-provider-specific-request-fields"></a>
### 提示缓存和提供方特定的请求字段

提示缓存和提供方特定的旋钮（knobs）很容易退化。

现有代码库中的示例：

- Anthropic 有一条原生的提示缓存路径
- OpenRouter 获得提供方路由字段
- 并非每个提供方都应接收每个请求端选项

当你添加一个新的原生提供方时，请仔细检查 Hermes 是否只发送该提供方实际理解的字段。

<a id="step-8-tests"></a>
## 第 8 步：测试

至少需要触及那些保护提供方接线的测试。

常见位置：

- `tests/test_runtime_provider_resolution.py`
- `tests/test_cli_provider_resolution.py`
- `tests/test_cli_model_command.py`
- `tests/test_setup_model_selection.py`
- `tests/test_provider_parity.py`
- `tests/test_run_agent.py`
- `tests/test_&lt;provider&gt;_adapter.py`（针对原生提供方）

对于仅文档的示例，确切的文件集可能有所不同。关键是要涵盖：

- 认证解析
- CLI 菜单 / 提供方选择
- 运行时提供方解析
- Agent 执行路径
- 提供方：模型解析
- 任何适配器特定的消息转换
禁用 xdist 运行测试：

```bash
source venv/bin/activate
python -m pytest tests/test_runtime_provider_resolution.py tests/test_cli_provider_resolution.py tests/test_cli_model_command.py tests/test_setup_model_selection.py -n0 -q
```

对于更深入的改动，请在推送前运行完整测试套件：

```bash
source venv/bin/activate
python -m pytest tests/ -n0 -q
```

<a id="step-9-live-verification"></a>
## 第九步：实机验证

测试通过后，运行一个真正的冒烟测试。

```bash
source venv/bin/activate
python -m hermes_cli.main chat -q "Say hello" --provider your-provider --model your-model
```

如果你修改过菜单，也测试一下交互式流程：

```bash
source venv/bin/activate
python -m hermes_cli.main model
python -m hermes_cli.main setup
```

对于原生 Provider，请务必验证至少一次工具调用，而不仅仅是纯文本响应。

<a id="step-10-update-user-facing-docs"></a>
## 第十步：更新面向用户的文档

如果该 Provider 打算作为一等公民选项发布，请同时更新用户文档：

- `website/docs/getting-started/quickstart.md`
- `website/docs/user-guide/configuration.md`
- `website/docs/reference/environment-variables.md`

开发者可以完美地接通 Provider，却仍然导致用户无法发现所需的环境变量或设置流程。

<a id="openai-compatible-provider-checklist"></a>
## 兼容 OpenAI 的 Provider 检查清单

当 Provider 是标准聊天补全接口时使用此清单。

- [ ] 在 `hermes_cli/auth.py` 中添加了 `ProviderConfig`
- [ ] 在 `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中添加了别名
- [ ] 在 `hermes_cli/models.py` 中添加了模型目录
- [ ] 在 `hermes_cli/runtime_provider.py` 中添加了运行时分支
- [ ] 在 `hermes_cli/main.py` 中添加了 CLI 接线（`setup.py` 自动继承）
- [ ] 在 `agent/auxiliary_client.py` 中添加了辅助模型
- [ ] 在 `agent/model_metadata.py` 中添加了上下文长度
- [ ] 更新了运行时/CLI 测试
- [ ] 更新了用户文档

<a id="native-provider-checklist"></a>
## 原生 Provider 检查清单

当 Provider 需要新的协议路径时使用此清单。

- [ ] 完成兼容 OpenAI 的检查清单中的所有项目
- [ ] 在 `agent/&lt;provider&gt;_adapter.py` 中添加了适配器
- [ ] 在 `run_agent.py` 中支持了新的 `api_mode`
- [ ] 中断/重建路径正常工作
- [ ] 用量和结束原因提取正常工作
- [ ] 回退路径正常工作
- [ ] 添加了适配器测试
- [ ] 实时冒烟测试通过

<a id="common-pitfalls"></a>
## 常见陷阱

<a id="1-adding-the-provider-to-auth-but-not-to-model-parsing"></a>
### 1. 将 Provider 添加到了认证模块，但未添加到模型解析模块

这会导致凭证解析正确，而 `/model` 和 `provider:model` 输入却失败。

<a id="2-forgetting-that-config-model-can-be-a-string-or-a-dict"></a>
### 2. 忘记 `config["model"]` 可以是字符串或字典

许多 Provider 选择代码必须对两种形式进行归一化处理。

<a id="3-assuming-a-built-in-provider-is-required"></a>
### 3. 假设内置 Provider 是必须的

如果服务仅仅是兼容 OpenAI，那么自定义 Provider 可能已经能用更少的维护代价解决用户问题。

<a id="4-forgetting-auxiliary-paths"></a>
### 4. 忘记辅助路径

主聊天路径可以正常工作，但摘要、内存刷新或视觉辅助功能却可能因为辅助路由从未更新而失败。

<a id="5-native-provider-branches-hiding-in-runagent-py"></a>
### 5. 原生 Provider 分支隐藏在 `run_agent.py` 中

搜索 `api_mode` 和 `self.client.`。不要以为显而易见的请求路径是唯一的。

<a id="6-sending-openrouter-only-knobs-to-other-providers"></a>
### 6. 将 OpenRouter 专用的参数发送给其他 Provider
像 provider 路由这样的字段仅属于支持它们的 provider。

<a id="7-updating-hermes-model-but-not-hermes-setup"></a>
### 7. 更新 `hermes model` 但不更新 `hermes setup`

两个流程都需要知道这个 provider。

<a id="good-search-targets-while-implementing"></a>
## 实现时的良好搜索目标

如果你在寻找一个 provider 触及的所有位置，搜索以下符号：

- `PROVIDER_REGISTRY`
- `_PROVIDER_ALIASES`
- `_PROVIDER_MODELS`
- `resolve_runtime_provider`
- `_model_flow_`
- `select_provider_and_model`
- `api_mode`
- `_API_KEY_PROVIDER_AUX_MODELS`
- `self.client.`

<a id="related-docs"></a>
## 相关文档

- [Provider 运行时解析](./provider-runtime.md)
- [架构](./architecture.md)
- [贡献指南](./contributing.md)
