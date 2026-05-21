---
sidebar_position: 11
title: "图像生成供应商插件"
description: "如何为 Hermes Agent 构建图像生成后端插件"
---

<a id="building-an-image-generation-provider-plugin"></a>
# 构建图像生成供应商插件

图像生成供应商插件注册一个后端，用于服务每次 `image_generate` 工具调用——DALL·E、gpt-image、Grok、Flux、Imagen、Stable Diffusion、fal、Replicate、本地的 ComfyUI 环境，以及其他任何服务。内置供应商（OpenAI、OpenAI-Codex、xAI）均以插件形式发布。您可以通过在 `plugins/image_gen/&lt;name&gt;/` 下放入一个目录来添加新插件或覆盖已有的插件。

:::tip
图像生成是 Hermes 支持的**后端插件**之一。其他后端插件（使用更专门的抽象基类）包括[内存供应商插件](/developer-guide/memory-provider-plugin)、[上下文引擎插件](/developer-guide/context-engine-plugin)和[模型供应商插件](/developer-guide/model-provider-plugin)。通用的工具/钩子/CLI 插件位于[构建 Hermes 插件](/guides/build-a-hermes-plugin)中。
:::

<a id="how-discovery-works"></a>
## 发现机制

Hermes 在三个位置扫描图像生成后端：

1. **内置** — `&lt;repo&gt;/plugins/image_gen/&lt;name&gt;/`（自动加载，类型为 `backend`，始终可用）
2. **用户** — `~/.hermes/plugins/image_gen/&lt;name&gt;/`（通过 `plugins.enabled` 选择启用）
3. **Pip** — 声明了 `hermes_agent.plugins` 入口点的包

每个插件的 `register(ctx)` 函数会调用 `ctx.register_image_gen_provider(...)`，将该插件注册到 `agent/image_gen_registry.py` 的注册表中。活动供应商由 `config.yaml` 中的 `image_gen.provider` 指定；`hermes tools` 会引导用户完成选择。

`image_generate` 工具包装器向注册表查询活动供应商并分派请求。如果没有注册任何供应商，该工具会显示一条有用的错误信息，引导用户查看 `hermes tools`。

<a id="directory-structure"></a>
## 目录结构

```
plugins/image_gen/my-backend/
├── __init__.py      # ImageGenProvider 子类 + register()
└── plugin.yaml      # 清单文件，类型为 backend
```

内置插件到此就完整了。位于 `~/.hermes/plugins/image_gen/&lt;name&gt;/` 的用户插件需要添加到 `config.yaml` 的 `plugins.enabled` 中（或运行 `hermes plugins enable &lt;name&gt;`）。

<a id="the-imagegenprovider-abc"></a>
## ImageGenProvider 抽象基类

子类化 `agent.image_gen_provider.ImageGenProvider`。唯一必需的成员是 `name` 属性和 `generate()` 方法——其他所有成员都有合理的默认值：

```python
# plugins/image_gen/my-backend/__init__.py
from typing import Any, Dict, List, Optional
import os

from agent.image_gen_provider import (
    DEFAULT_ASPECT_RATIO,
    ImageGenProvider,
    error_response,
    resolve_aspect_ratio,
    save_b64_image,
    success_response,
)


class MyBackendImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        # Stable id used in image_gen.provider config. Lowercase, no spaces.
        return "my-backend"

    @property
    def display_name(self) -> str:
        # Human label shown in `hermes tools`. Defaults to name.title() if omitted.
        return "My Backend"

    def is_available(self) -> bool:
        # Return False if credentials or deps are missing.
        # The tool's availability gate calls this before dispatch.
        if not os.environ.get("MY_BACKEND_API_KEY"):
            return False
        try:
            import my_backend_sdk  # noqa: F401
        except ImportError:
            return False
        return True

    def list_models(self) -> List[Dict[str, Any]]:
        # Catalog shown in `hermes tools` model picker.
        return [
            {
                "id": "my-model-fast",
                "display": "My Model (Fast)",
                "speed": "~5s",
                "strengths": "Quick iteration",
                "price": "$0.01/image",
            },
            {
                "id": "my-model-hq",
                "display": "My Model (HQ)",
                "speed": "~30s",
                "strengths": "Highest fidelity",
                "price": "$0.04/image",
            },
        ]

    def default_model(self) -> Optional[str]:
        return "my-model-fast"

    def get_setup_schema(self) -> Dict[str, Any]:
        # Metadata for the `hermes tools` picker — keys to prompt for at setup.
        return {
            "name": "My Backend",
            "badge": "paid",        # optional; shown as a short tag in the picker
            "tag": "One-line description shown under the name",
            "env_vars": [
                {
                    "key": "MY_BACKEND_API_KEY",
                    "prompt": "My Backend API key",
                    "url": "https://my-backend.example.com/api-keys",
                },
            ],
        }

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        prompt = (prompt or "").strip()
        aspect_ratio = resolve_aspect_ratio(aspect_ratio)

        if not prompt:
            return error_response(
                error="Prompt is required",
                error_type="invalid_input",
                provider=self.name,
                prompt="",
                aspect_ratio=aspect_ratio,
            )

        # Model selection precedence: env var → config → default. The helper
        # _resolve_model() in the built-in openai plugin is a good reference.
        model_id = kwargs.get("model") or self.default_model() or "my-model-fast"

        try:
            import my_backend_sdk
            client = my_backend_sdk.Client(api_key=os.environ["MY_BACKEND_API_KEY"])
            result = client.generate(
                prompt=prompt,
                model=model_id,
                aspect_ratio=aspect_ratio,
            )

            # Two shapes supported:
            #   - URL string: return it as `image`
            #   - base64 data: save under $HERMES_HOME/cache/images/ via save_b64_image()
            if result.get("image_b64"):
                path = save_b64_image(
                    result["image_b64"],
                    prefix=self.name,
                    extension="png",
                )
                image = str(path)
            else:
                image = result["image_url"]

            return success_response(
                image=image,
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                provider=self.name,
            )
        except Exception as exc:
            return error_response(
                error=str(exc),
                error_type=type(exc).__name__,
                provider=self.name,
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
            )


def register(ctx) -> None:
    """Plugin entry point — called once at load time."""
    ctx.register_image_gen_provider(MyBackendImageGenProvider())
```
<a id="plugin-yaml"></a>
## plugin.yaml

```yaml
name: my-backend
version: 1.0.0
description: 我的图片后端 — 通过 My Backend SDK 实现文生图
author: 你的名字
kind: backend
requires_env:
  - MY_BACKEND_API_KEY
```

`kind: backend` 用于将该插件路由到图片生成注册路径。`requires_env` 在执行 `hermes plugins install` 时会提示用户填写。

<a id="abc-reference"></a>
## ABC 参考

完整合约在 `agent/image_gen_provider.py` 中。你通常需要覆写以下方法：

| 成员 | 是否必需 | 默认值 | 说明 |
|---|---|---|---|
| `name` | ✅ | — | 用于 `image_gen.provider` 配置的稳定标识 |
| `display_name` | — | `name.title()` | 在 `hermes tools` 中显示的标签 |
| `is_available()` | — | `True` | 用于检查凭据或依赖项是否缺失 |
| `list_models()` | — | `[]` | 供 `hermes tools` 模型选择器使用的目录 |
| `default_model()` | — | `list_models()` 的第一个值 | 未配置模型时的回退 |
| `get_setup_schema()` | — | 最小化 | 选择器元数据 + 环境变量提示 |
| `generate(prompt, aspect_ratio, **kwargs)` | ✅ | — | 实际调用 |

<a id="response-format"></a>
## 响应格式

`generate()` 必须返回通过 `success_response()` 或 `error_response()` 构建的字典。这两个函数都在 `agent/image_gen_provider.py` 中。

**成功响应：**
```python
success_response(
    image=<url-或-绝对路径>,
    model=<模型-id>,
    prompt=<回显的-prompt>,
    aspect_ratio="landscape" | "square" | "portrait",
    provider=<你的-provider-名称>,
    extra={...},  # 可选的后端特定字段
)
```

**错误响应：**
```python
error_response(
    error="人类可读的消息",
    error_type="provider_error" | "invalid_input" | "<异常类名>",
    provider=<你的-provider-名称>,
    model=<模型-id>,
    prompt=<prompt>,
    aspect_ratio=<解析后的宽高比>,
)
```

工具包装器会将字典 JSON 序列化，并交给 LLM。错误会作为工具结果返回；LLM 会决定如何向用户解释这些错误。

<a id="handling-base64-vs-url-output"></a>
## 处理 base64 与 URL 输出

有些后端返回图片 URL（fal、Replicate），有些返回 base64 载荷（OpenAI gpt-image-2）。对于 base64 的情况，请使用 `save_b64_image()` —— 它会将图片写入 `$HERMES_HOME/cache/images/&lt;prefix&gt;_&lt;timestamp&gt;_&lt;uuid&gt;.&lt;ext&gt;` 并返回绝对路径的 `Path`。将该路径（作为 `str`）以 `image=` 参数传入 `success_response()`。交付网关（Telegram 图片气泡、Discord 附件）会同时识别 URL 和绝对路径。

<a id="user-overrides"></a>
## 用户覆盖

将用户插件放在 `~/.hermes/plugins/image_gen/&lt;name&gt;/` 目录下，使用与内置插件相同的 `name` 属性，然后通过 `hermes plugins enable &lt;name&gt;` 启用——注册表采取“最后写入者获胜”原则，因此你的版本会替换内置版本。适用于将 `openai` 插件指向私有代理，或替换自定义模型目录。

<a id="testing"></a>
## 测试

```bash
export HERMES_HOME=/tmp/hermes-imggen-test
mkdir -p $HERMES_HOME/plugins/image_gen/my-backend
# …将 __init__.py 和 plugin.yaml 复制到该目录…

export MY_BACKEND_API_KEY=your-test-key
hermes plugins enable my-backend

# 将其选为当前使用的提供商
echo "image_gen:" >> $HERMES_HOME/config.yaml
echo "  provider: my-backend" >> $HERMES_HOME/config.yaml

# 测试运行
hermes -z "生成一张穿着太空服的柯基犬图片"
```
或以交互方式：`hermes tools` → “Image Generation” → 选择 `my-backend` → 如有提示则输入 API Key。

<a id="reference-implementations"></a>
## 参考实现

- **`plugins/image_gen/openai/__init__.py`** — gpt-image-2 以低/中/高三档作为三个虚拟模型 ID，共享同一个 API 模型，但使用不同的 `quality` 参数。这是单后端下分层模型 + config.yaml 优先级链的良好示例。
- **`plugins/image_gen/xai/__init__.py`** — 通过 xAI 实现的 Grok Imagine。形状不同（URL 输出，目录更简洁）。
- **`plugins/image_gen/openai-codex/__init__.py`** — 采用 Codex 风格的 Responses API 变体，复用 OpenAI SDK，但使用不同的路由基础 URL。

<a id="distribute-via-pip"></a>
## 通过 pip 分发

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-backend-imggen = "my_backend_imggen_package"
```

`my_backend_imggen_package` 必须暴露一个顶层 `register` 函数。有关完整设置，请参阅通用插件指南中的[通过 pip 分发](/guides/build-a-hermes-plugin#distribute-via-pip)。

<a id="related-pages"></a>
## 相关页面

- [图像生成](/user-guide/features/image-generation) — 面向用户的功能文档
- [插件概览](/user-guide/features/plugins) — 所有插件类型一览
- [构建 Hermes 插件](/guides/build-a-hermes-plugin) — 通用工具/钩子/斜杠命令指南
