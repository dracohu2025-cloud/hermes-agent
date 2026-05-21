---
sidebar_position: 10
title: "模型提供商插件"
description: "如何为 Hermes Agent 构建模型提供商（推理后端）插件"
---

<a id="building-a-model-provider-plugin"></a>
# 构建模型提供商插件

模型提供商插件声明一个推理后端——一个兼容 OpenAI 的端点、一个 Anthropic Messages 服务器、一个 Codex 风格的 Responses API，或者一个 Bedrock 原生接口——Hermes 可以通过它路由 `AIAgent` 调用。每个内置提供商（OpenRouter、Anthropic、GMI、DeepSeek、Nvidia……）都以这些插件之一的形式提供。第三方可以在 `$HERMES_HOME/plugins/model-providers/` 下放置一个目录来添加自己的插件，无需对仓库做任何修改。

:::tip
模型提供商插件是第三种**提供商插件**。其他的是[记忆提供商插件](/developer-guide/memory-provider-plugin)（跨会话知识）和[上下文引擎插件](/developer-guide/context-engine-plugin)（上下文压缩策略）。三者都遵循同样的“放一个目录，声明一个配置文件，无需修改仓库”模式。
:::

<a id="how-discovery-works"></a>
## 发现机制

`providers/__init__.py._discover_providers()` 首次被调用时惰性执行，当任何代码调用 `get_provider_profile()` 或 `list_providers()` 时。发现顺序：

1. **捆绑插件** — `&lt;repo&gt;/plugins/model-providers/&lt;name&gt;/` — 随 Hermes 一起提供
2. **用户插件** — `$HERMES_HOME/plugins/model-providers/&lt;name&gt;/` — 放在任何目录中；后续会话无需重启
3. **遗留单文件** — `&lt;repo&gt;/providers/&lt;name&gt;.py` — 为外部可编辑安装提供向后兼容性

**用户插件会覆盖同名的捆绑插件**，因为 `register_provider()` 以最后写入者胜出。放置一个 `$HERMES_HOME/plugins/model-providers/gmi/` 目录即可替换内置的 GMI 配置文件，无需修改仓库。

<a id="directory-structure"></a>
## 目录结构

```
plugins/model-providers/my-provider/
├── __init__.py       # 在模块级别调用 register_provider(profile)
├── plugin.yaml       # kind: model-provider + 元数据（可选，但推荐）
└── README.md         # 安装说明（可选）
```

唯一必需的文件是 `__init__.py`。`plugin.yaml` 被 `hermes plugins` 用于内省，并被通用 PluginManager 用于将插件路由到正确的加载器；如果没有它，通用加载器会回退到源文本启发式方法。

<a id="minimal-example-a-simple-api-key-provider"></a>
## 最小示例——一个简单的 API 密钥提供商

```python
# plugins/model-providers/acme-inference/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

acme = ProviderProfile(
    name="acme-inference",
    aliases=("acme",),
    display_name="Acme Inference",
    description="Acme — OpenAI-compatible direct API",
    signup_url="https://acme.example.com/keys",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=(
        "acme-large-v3",
        "acme-medium-v3",
        "acme-small-fast",
    ),
)

register_provider(acme)
```

```yaml
# plugins/model-providers/acme-inference/plugin.yaml
name: acme-inference
kind: model-provider
version: 1.0.0
description: Acme Inference — OpenAI-compatible direct API
author: Your Name
```
只需放入这两个文件，无需其他修改，即可实现以下**自动装配**：

| 集成点 | 位置 | 作用 |
|---|---|---|
| 凭据解析 | `hermes_cli/auth.py` | 从配置文件中读取 `PROVIDER_REGISTRY["acme-inference"]` |
| `--provider` CLI 标志 | `hermes_cli/main.py` | 接受 `acme-inference` 作为参数 |
| `hermes model` 选择器 | `hermes_cli/models.py` | 出现在 `CANONICAL_PROVIDERS` 中，模型列表从 `{base_url}/models` 获取 |
| `hermes doctor` | `hermes_cli/doctor.py` | 对 `ACME_API_KEY` + `{base_url}/models` 进行健康检查 |
| `hermes setup` | `hermes_cli/config.py` | `ACME_API_KEY` 出现在 `OPTIONAL_ENV_VARS` 和设置向导中 |
| URL 反向映射 | `agent/model_metadata.py` | 主机名 → 提供商名称，用于自动检测 |
| 辅助模型 | `agent/auxiliary_client.py` | 使用 `default_aux_model` 进行压缩/摘要 |
| 运行时解析 | `hermes_cli/runtime_provider.py` | 返回正确的 `base_url`、`api_key`、`api_mode` |
| 传输层 | `agent/transports/chat_completions.py` | 配置文件路径通过 `prepare_messages` / `build_extra_body` / `build_api_kwargs_extras` 生成 kwargs |

<a id="providerprofile-fields"></a>
## ProviderProfile 字段

完整定义在 `providers/base.py` 中。最常用的字段如下：

| 字段 | 类型 | 用途 |
|---|---|---|
| `name` | str | 规范标识符 — 与 `--provider` 选项和 `HERMES_INFERENCE_PROVIDER` 匹配 |
| `aliases` | `tuple[str, ...]` | 由 `get_provider_profile()` 解析的替代名称（例如 `grok` → `xai`） |
| `api_mode` | str | `chat_completions` \| `codex_responses` \| `anthropic_messages` \| `bedrock_converse` |
| `display_name` | str | 在 `hermes model` 选择器中显示的人类可读标签 |
| `description` | str | 选择器副标题 |
| `signup_url` | str | 首次运行设置时显示（"在此处获取 API 密钥"） |
| `env_vars` | `tuple[str, ...]` | 按优先级排序的 API 密钥环境变量；最后一个 `*_BASE_URL` 条目用作自定义基础 URL 覆盖 |
| `base_url` | str | 默认推理端点 |
| `models_url` | str | 显式模型目录 URL（回退到 `{base_url}/models`） |
| `auth_type` | str | `api_key` \| `oauth_device_code` \| `oauth_external` \| `copilot` \| `aws_sdk` \| `external_process` |
| `fallback_models` | `tuple[str, ...]` | 当实时目录获取失败时显示的精选模型列表 |
| `default_headers` | `dict[str, str]` | 每次请求都会发送的默认请求头（例如 Copilot 的 `Editor-Version`） |
| `fixed_temperature` | Any | `None` = 使用调用者的值；`OMIT_TEMPERATURE` 哨兵值 = 不发送 temperature 参数（Kimi） |
| `default_max_tokens` | `int \| None` | 提供商级别的 max_tokens 上限（Nvidia：16384） |
| `default_aux_model` | str | 用于辅助任务（压缩、视觉、摘要）的廉价模型 |

<a id="overridable-hooks"></a>
## 可覆盖的钩子

对于非标准行为，可以继承 `ProviderProfile`：

```python
from typing import Any
from providers.base import ProviderProfile

class AcmeProfile(ProviderProfile):
    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """提供商特定的消息预处理。在 codex 清理之后、开发者角色交换之前执行。
        默认行为：透传。"""
        # 示例：Qwen 将纯文本内容规范化为多部分数组并注入 cache_control；
        # Kimi 重写 tool-call JSON
        return messages

    def build_extra_body(self, *, session_id=None, **context) -> dict:
        """提供商特定的 extra_body 字段，合并到 API 调用中。
        Context 包含：session_id、provider_preferences、model、base_url、
        reasoning_config。默认行为：空字典。"""
        # 示例：OpenRouter 的 provider-preferences 块，
        # Gemini 的 thinking_config 转换。
        return {}

    def build_api_kwargs_extras(self, *, reasoning_config=None, **context):
        """返回 (extra_body_additions, top_level_kwargs)。当某些字段需要放在
        顶层（Kimi 的 reasoning_effort）而另一些需要放在 extra_body 中
        （OpenRouter 的 reasoning dict）时使用。默认行为：({}, {})。"""
        return {}, {}

    def fetch_models(self, *, api_key=None, timeout=8.0) -> list[str] | None:
        """实时目录获取。默认使用 Bearer 认证访问 {models_url or base_url}/models。
        覆盖场景：自定义认证（Anthropic）、无 REST 端点（Bedrock → None）、
        或公共/无需认证的目录（OpenRouter）。"""
        return super().fetch_models(api_key=api_key, timeout=timeout)
```
<a id="hook-reference-examples"></a>
## 钩子参考示例

请查看这些内置插件以了解惯用写法：

| 插件 | 为何查看 |
|---|---|
| `plugins/model-providers/openrouter/` | 聚合器，支持提供商偏好、公共模型目录 |
| `plugins/model-providers/gemini/` | `thinking_config` 转换（原生 + OpenAI 兼容嵌套形式） |
| `plugins/model-providers/kimi-coding/` | `OMIT_TEMPERATURE`、`extra_body.thinking`、顶层 `reasoning_effort` |
| `plugins/model-providers/qwen-oauth/` | 消息标准化、`cache_control` 注入、VL 高分辨率 |
| `plugins/model-providers/nous/` | 归属标签、“禁用时省略推理” |
| `plugins/model-providers/custom/` | Ollama `num_ctx` + `think: false` 特殊行为 |
| `plugins/model-providers/bedrock/` | `api_mode="bedrock_converse"`、`fetch_models` 返回 None（无 REST 端点） |

<a id="user-overrides-replace-a-built-in-without-editing-the-repo"></a>
## 用户覆写 — 无需编辑仓库即可替换内置提供商

假设你想将 `gmi` 指向私有测试端点。创建 `~/.hermes/plugins/model-providers/gmi/__init__.py`：

```python
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="gmi",
    aliases=("gmi-cloud", "gmicloud"),
    env_vars=("GMI_API_KEY",),
    base_url="https://gmi-staging.internal.example.com/v1",
    auth_type="api_key",
    default_aux_model="google/gemini-3.1-flash-lite-preview",
))
```

下次会话时，`get_provider_profile("gmi").base_url` 将返回测试 URL。无需修补仓库，无需重新构建。因为用户插件在打包插件之后被发现，用户的 `register_provider()` 调用会胜出。

<a id="apimode-selection"></a>
## api_mode 选择

系统识别四种值。Hermes 根据以下规则选择其一：

1. 用户显式覆写（`config.yaml` 中的 `model.api_mode` 设置）
2. OpenCode 的按模型分发（Zen 和 Go 的 `opencode_model_api_mode`）
3. URL 自动检测 — `/anthropic` 后缀 → `anthropic_messages`、`api.openai.com` → `codex_responses`、`api.x.ai` → `codex_responses`、Kimi 域名的 `/coding` → `chat_completions`
4. **Profile 中的 `api_mode`** 作为 URL 检测失败时的回退
5. 默认 `chat_completions`

设置 `profile.api_mode` 以匹配提供商默认值 — 它作为提示。用户 URL 覆写仍然优先。

<a id="auth-types"></a>
## 认证类型

| `auth_type` | 含义 | 谁使用它 |
|---|---|---|
| `api_key` | 单个环境变量携带静态 API 密钥 | 大多数提供商 |
| `oauth_device_code` | 设备码 OAuth 流程 | — |
| `oauth_external` | 用户在其他地方登录，令牌存入 `auth.json` | Anthropic OAuth、MiniMax OAuth、Gemini Cloud Code、Qwen Portal、Nous Portal |
| `copilot` | GitHub Copilot 令牌刷新周期 | 仅 `copilot` 插件 |
| `aws_sdk` | AWS SDK 凭据链（IAM 角色、配置文件、环境变量） | 仅 `bedrock` 插件 |
| `external_process` | 由 Agent 生成的子进程处理认证 | 仅 `copilot-acp` 插件 |

`auth_type` 决定哪些代码路径将你的提供商视为“简单的 api-key 提供商” — 如果不是 `api_key`，PluginManager 仍会记录清单，但 Hermes 的 CLI 级自动化（医生检查、`--provider` 标志、设置向导委派）可能会跳过它。
<a id="discovery-timing"></a>
## 发现时机

Provider 发现是**懒加载**的——由进程中的第一次 `get_provider_profile()` 或 `list_providers()` 调用触发。实际运行时，这在启动初期就会发生（`auth.py` 模块加载时会主动扩展 `PROVIDER_REGISTRY`）。如果你需要验证插件是否已加载，可以运行：

```bash
hermes doctor
```

——如果成功，Provider Connectivity 部分下会出现一个 `auth_type="api_key"` 的 profile 条目，并附带 `/models` 探测结果。

通过编程方式检查：

```python
from providers import list_providers
for p in list_providers():
    print(p.name, p.base_url, p.api_mode)
```

<a id="testing-your-plugin"></a>
## 测试你的插件

将 `HERMES_HOME` 指向一个临时目录，这样就不会污染你的真实配置：

```bash
export HERMES_HOME=/tmp/hermes-plugin-test
mkdir -p $HERMES_HOME/plugins/model-providers/my-provider
cat > $HERMES_HOME/plugins/model-providers/my-provider/__init__.py <<'EOF'
from providers import register_provider
from providers.base import ProviderProfile
register_provider(ProviderProfile(
    name="my-provider",
    env_vars=("MY_API_KEY",),
    base_url="https://api.my-provider.example.com/v1",
    auth_type="api_key",
))
EOF

export MY_API_KEY=your-test-key
hermes -z "hello" --provider my-provider -m some-model
```

<a id="general-pluginmanager-integration"></a>
## 与通用 PluginManager 的集成

通用的 `PluginManager`（即 `hermes plugins` 操作的对象）**能看见**模型提供者插件，但不会导入它们——`providers/__init__.py` 负责管理它们的生命周期。管理器会记录清单以供内省，并按 `kind: model-provider` 分类。当你将一个未标记的用户插件放入 `$HERMES_HOME/plugins/`，并且该插件恰好调用了 `register_provider` 并传入 `ProviderProfile` 时，管理器会根据源码文本启发式地自动将其强制归类为 `kind: model-provider`——因此即使没有 `plugin.yaml`，插件也能正确路由。

<a id="distribute-via-pip"></a>
## 通过 pip 分发

像任何 Hermes 插件一样，模型提供者可以以 pip 包的形式发布。在 `pyproject.toml` 中添加一个入口点：

```toml
[project.entry-points."hermes.plugins"]
acme-inference = "acme_hermes_plugin:register"
```

……其中 `acme_hermes_plugin:register` 是一个调用 `register_provider(profile)` 的函数。通用 PluginManager 在 `discover_and_load()` 过程中会拾取入口点插件。对于 `kind: model-provider` 的 pip 插件，你仍然需要在清单中声明 kind（或者依赖源码文本启发式）。

完整的入口点配置请参见 [构建 Hermes 插件](/guides/build-a-hermes-plugin#distribute-via-pip)。

<a id="related-pages"></a>
## 相关页面

- [Provider 运行时](/developer-guide/provider-runtime) —— 解析优先级 + 每一层读取 profile 的位置
- [添加 Provider](/developer-guide/adding-providers) —— 新推理后端的端到端核对清单（涵盖快速插件路径和完整的 CLI/认证集成）
- [Memory Provider 插件](/developer-guide/memory-provider-plugin)
- [Context Engine 插件](/developer-guide/context-engine-plugin)
- [构建 Hermes 插件](/guides/build-a-hermes-plugin) —— 通用插件编写指南
