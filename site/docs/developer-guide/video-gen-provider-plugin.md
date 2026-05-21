---
sidebar_position: 12
title: "视频生成提供者插件"
description: "如何为 Hermes Agent 构建视频生成后端插件"
---

<a id="building-a-video-generation-provider-plugin"></a>
# 构建视频生成提供者插件

视频生成提供者插件注册一个后端，用于处理所有 `video_generate` 工具调用。内置提供者（xAI、FAL）作为插件提供。通过将目录放入 `plugins/video_gen/&lt;name&gt;/`，可以添加新插件或覆盖已有插件。

:::tip
视频生成插件几乎逐行镜像[图像生成提供者插件](/developer-guide/image-gen-provider-plugin)——如果你已经构建过图像生成后端，你已经知道结构。主要区别在于：一个 `capabilities()` 方法用于声明模态/宽高比/时长，以及一个路由约定（传递 `image_url` 使用图像到视频，省略则使用文本到视频——提供者在内部选择正确的端点）。
:::

<a id="the-unified-surface-one-tool-two-modalities"></a>
## 统一表面（一个工具，两种模态）

`video_generate` 工具通过一个参数暴露两种模态：

- **文本到视频** — 仅使用 `prompt` 调用。提供者路由到其文本到视频端点。
- **图像到视频** — 使用 `prompt` + `image_url` 调用。提供者路由到其图像到视频端点。

编辑和扩展明确不在此范围内。大多数后端不支持它们，不一致性会迫使将每个后端的描述性文本嵌入到 Agent 的工具描述中。

<a id="how-discovery-works"></a>
## 发现机制

Hermes 在三个位置扫描视频生成后端：

1. **内置** — `&lt;repo&gt;/plugins/video_gen/&lt;name&gt;/`（自动加载，带有 `kind: backend`）
2. **用户** — `~/.hermes/plugins/video_gen/&lt;name&gt;/`（通过 `plugins.enabled` 选择加入）
3. **Pip** — 声明了 `hermes_agent.plugins` 入口点的包

每个插件的 `register(ctx)` 函数调用 `ctx.register_video_gen_provider(...)`。通过 `config.yaml` 中的 `video_gen.provider` 选择激活的提供者；`hermes tools` → 视频生成会引导用户完成选择。与 `image_generate` 不同，没有树内遗留后端——每个提供者都是一个插件。

<a id="directory-structure"></a>
## 目录结构

```
plugins/video_gen/my-backend/
├── __init__.py      # VideoGenProvider 子类 + register()
└── plugin.yaml      # 清单，带有 kind: backend
```

<a id="the-videogenprovider-abc"></a>
## VideoGenProvider 抽象基类

继承 `agent.video_gen_provider.VideoGenProvider`。必需：`name` 属性和 `generate()` 方法。

```python
# plugins/video_gen/my-backend/__init__.py
from typing import Any, Dict, List, Optional
import os

from agent.video_gen_provider import (
    VideoGenProvider,
    error_response,
    success_response,
)


class MyVideoGenProvider(VideoGenProvider):
    @property
    def name(self) -> str:
        return "my-backend"

    @property
    def display_name(self) -> str:
        return "My Backend"

    def is_available(self) -> bool:
        return bool(os.environ.get("MY_API_KEY"))

    def list_models(self) -> List[Dict[str, Any]]:
        # 每个条目是一个模型系列——用户一次选择的名称。
        # 你的提供者的 generate() 根据是否传递了 image_url 在系列内路由。
        return [
            {
                "id": "fast",
                "display": "Fast",
                "speed": "~30s",
                "strengths": "Cheapest tier",
                "price": "$0.05/s",
                "modalities": ["text", "image"],  # 参考性
            },
        ]

    def default_model(self) -> Optional[str]:
        return "fast"

    def capabilities(self) -> Dict[str, Any]:
        return {
            "modalities": ["text", "image"],
            "aspect_ratios": ["16:9", "9:16"],
            "resolutions": ["720p", "1080p"],
            "min_duration": 1,
            "max_duration": 10,
            "supports_audio": False,
            "supports_negative_prompt": True,
            "max_reference_images": 0,
        }

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "My Backend",
            "badge": "paid",
            "tag": "Short description shown in `hermes tools`",
            "env_vars": [
                {
                    "key": "MY_API_KEY",
                    "prompt": "My Backend API key",
                    "url": "https://mybackend.example.com/keys",
                },
            ],
        }

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        image_url: Optional[str] = None,
        reference_image_urls: Optional[List[str]] = None,
        duration: Optional[int] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        negative_prompt: Optional[str] = None,
        audio: Optional[bool] = None,
        seed: Optional[int] = None,
        **kwargs: Any,  # 始终忽略未知参数以保持向前兼容
    ) -> Dict[str, Any]:
        # 路由：image_url 的存在决定端点。
        if image_url:
            endpoint = "my-backend/image-to-video"
            modality_used = "image"
        else:
            endpoint = "my-backend/text-to-video"
            modality_used = "text"

        # ... 调用你的 API ...

        return success_response(
            video="https://your-cdn/output.mp4",
            model=model or "fast",
            prompt=prompt,
            modality=modality_used,
            aspect_ratio=aspect_ratio,
            duration=duration or 5,
            provider=self.name,
        )


def register(ctx) -> None:
    ctx.register_video_gen_provider(MyVideoGenProvider())
```
<a id="the-plugin-manifest"></a>
## 插件清单

```yaml
# plugins/video_gen/my-backend/plugin.yaml
name: my-backend
version: 1.0.0
description: "我的视频生成后端"
author: Your Name
kind: backend
requires_env:
  - MY_API_KEY
```

<a id="the-videogenerate-schema"></a>
## `video_generate` 模式

该工具在所有后端上暴露同一个模式。供应商会忽略它们不支持的参数。

| 参数 | 作用 |
|---|---|
| `prompt` | 文本指令（必填） |
| `image_url` | 当设置时 → 图生视频；当省略时 → 文生视频 |
| `reference_image_urls` | 风格/角色参考（取决于供应商） |
| `duration` | 秒数——供应商会做裁剪 |
| `aspect_ratio` | `"16:9"`、`"9:16"`、`"1:1"`……供应商会做裁剪 |
| `resolution` | `"480p"` / `"540p"` / `"720p"` / `"1080p"`——供应商会做裁剪 |
| `negative_prompt` | 要避免的内容（仅限 Pixverse/Kling） |
| `audio` | 原生音频（Veo3 / Pixverse 定价层级） |
| `seed` | 可复现性 |
| `model` | 覆盖当前激活的模型/系列 |

供应商的 `capabilities()` 会告知哪些参数被支持。Agent 在工具描述中可以看到当前后端的能力，当用户通过 `hermes tools` 切换后端时，这些能力也会动态重建。

<a id="model-families-and-endpoint-routing-the-fal-pattern"></a>
## 模型系列与端点路由（FAL 模式）

当你的后端对单个“模型”有多个端点时——例如 FAL，每个系列（Veo 3.1、Pixverse v6、Kling O3）都有 `/text-to-video` 和 `/image-to-video` 两个 URL——此时应将每个**系列**表示为一个目录条目。你的 `generate()` 会根据是否传入了 `image_url` 来选择正确的端点：

```python
FAMILIES = {
    "veo3.1": {
        "text_endpoint": "fal-ai/veo3.1",
        "image_endpoint": "fal-ai/veo3.1/image-to-video",
        # ... 系列特定的能力标志 ...
    },
}

def generate(self, prompt, *, image_url=None, model=None, **kwargs):
    family_id, family = _resolve_family(model)
    endpoint = family["image_endpoint"] if image_url else family["text_endpoint"]
    # ... 根据声明的能力标志构建载荷，调用端点 ...
```

用户在 `hermes tools` 中一次性选择 `veo3.1`。Agent 从不关心端点——它只需要传入（或不传入）`image_url`。

<a id="selection-precedence"></a>
## 选择优先级

对于每个实例的模型旋钮（参见 `plugins/video_gen/fal/__init__.py`）：

1. 工具调用中的 `model=` 关键字
2. `&lt;PROVIDER&gt;_VIDEO_MODEL` 环境变量
3. `config.yaml` 中的 `video_gen.&lt;provider&gt;.model`
4. `config.yaml` 中的 `video_gen.model`（当它是你的 ID 之一时）
5. 供应商的 `default_model()`

<a id="response-shape"></a>
## 响应形状

`success_response()` 和 `error_response()` 会生成每个后端返回的字典形状。请使用它们——不要手动拼字典。

成功键：`success`、`video`（URL 或绝对路径）、`model`、`prompt`、`modality`（`"text"` 或 `"image"`）、`aspect_ratio`、`duration`、`provider`，以及 `extra`。

错误键：`success`、`video`（None）、`error`、`error_type`、`model`、`prompt`、`aspect_ratio`、`provider`。

<a id="where-to-save-artifacts"></a>
## 制品保存位置

如果你的后端返回 base64，使用 `save_b64_video()` 将文件写入 `$HERMES_HOME/cache/videos/`。如果是后续 HTTP 获取得到的原始字节，使用 `save_bytes_video()`。否则，直接返回上游 URL——网关会在交付时解析远程 URL。
<a id="testing"></a>
## 测试

在 `tests/plugins/video_gen/test_&lt;name&gt;_plugin.py` 下放置一个冒烟测试。xAI 和 FAL 的测试展示了基本模式——注册、验证目录、在有/无 `image_url` 的情况下执行路由、在缺少认证时断言清晰的错误响应。
