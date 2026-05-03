---
title: 图像生成
description: 通过 FAL.ai 生成图像 — 支持 9 种模型，包括 FLUX 2、GPT Image（1.5 和 2）、Nano Banana Pro、Ideogram、Recraft V4 Pro 等，可通过 `hermes tools` 选择。
sidebar_label: 图像生成
sidebar_position: 6
---

# 图像生成 {#image-generation}

Hermes Agent 通过 FAL.ai 根据文本提示生成图像。内置支持九种模型，每种模型在速度、质量和成本上各有取舍。用户可通过 `hermes tools` 配置当前使用的模型，配置会持久化保存在 `config.yaml` 中。

## 支持的模型 {#supported-models}

| 模型 | 速度 | 优势 | 价格 |
|---|---|---|---|
| `fal-ai/flux-2/klein/9b` *(默认)* | `<1s` | 快速、文字清晰 | $0.006/MP |
| `fal-ai/flux-2-pro` | ~6s | 工作室级照片真实感 | $0.03/MP |
| `fal-ai/z-image/turbo` | ~2s | 中英双语，6B 参数 | $0.005/MP |
| `fal-ai/nano-banana-pro` | ~8s | Gemini 3 Pro，推理深度，文字渲染 | $0.15/张（1K） |
| `fal-ai/gpt-image-1.5` | ~15s | 提示遵循度 | $0.034/张 |
| `fal-ai/gpt-image-2` | ~20s | 最先进的文字渲染 + 中日韩文字，世界感知照片真实感 | $0.04–0.06/张 |
| `fal-ai/ideogram/v3` | ~5s | 最佳排版 | $0.03–0.09/张 |
| `fal-ai/recraft/v4/pro/text-to-image` | ~8s | 设计、品牌系统、生产就绪 | $0.25/张 |
| `fal-ai/qwen-image` | ~12s | 基于 LLM，复杂文字 | $0.02/MP |

价格为撰写时的 FAL 定价；请查看 [fal.ai](https://fal.ai/) 获取最新价格。

## 设置 {#setup}

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，您可以通过 **[工具网关](tool-gateway.md)** 使用图像生成功能，无需 FAL API 密钥。您的模型选择在两个路径中都会持久保留。

<a id="nous-subscribers"></a>
如果托管网关对某个特定模型返回 `HTTP 4xx`，说明该模型尚未在门户端代理——Agent 会告知您并提供修复步骤（设置 `FAL_KEY` 以直接访问，或选择其他模型）。
:::

### 获取 FAL API 密钥 {#get-a-fal-api-key}

1. 在 [fal.ai](https://fal.ai/) 注册
2. 在控制面板中生成 API 密钥

### 配置并选择模型 {#configure-and-pick-a-model}

运行工具命令：

```bash
hermes tools
```

导航到 **🎨 图像生成**，选择后端（Nous 订阅或 FAL.ai），然后选择器会以列对齐表格的形式显示所有支持的模型——使用方向键导航，按 Enter 选择：

```
  Model                          Speed    Strengths                    Price
  fal-ai/flux-2/klein/9b         <1s      Fast, crisp text             $0.006/MP   ← currently in use
  fal-ai/flux-2-pro              ~6s      Studio photorealism          $0.03/MP
  fal-ai/z-image/turbo           ~2s      Bilingual EN/CN, 6B          $0.005/MP
  ...
```

您的选择会保存到 `config.yaml`：

```yaml
image_gen:
  model: fal-ai/flux-2/klein/9b
  use_gateway: false            # true if using Nous Subscription
```

### GPT-Image 质量 {#gpt-image-quality}

`fal-ai/gpt-image-1.5` 和 `fal-ai/gpt-image-2` 的请求质量固定为 `medium`（1024×1024 时约 $0.034–$0.06/张）。我们不将 `low` / `high` 等级作为用户可选项暴露，以便所有用户的 Nous Portal 计费保持一致——不同等级之间的成本差异为 3–22 倍。如果您想要更便宜的选项，请选择 Klein 9B 或 Z-Image Turbo；如果您想要更高质量，请使用 Nano Banana Pro 或 Recraft V4 Pro。
## 使用方式 {#usage}

面向 Agent 的接口设计得非常精简——模型会自动识别你配置的内容：

```
Generate an image of a serene mountain landscape with cherry blossoms
```

```
Create a square portrait of a wise old owl — use the typography model
```

```
Make me a futuristic cityscape, landscape orientation
```

## 宽高比 {#aspect-ratios}

从 Agent 的角度看，所有模型都接受相同的三种宽高比。在内部，每个模型的原生尺寸规格会自动填充：

| Agent 输入 | image_size (flux/z-image/qwen/recraft/ideogram) | aspect_ratio (nano-banana-pro) | image_size (gpt-image-1.5) | image_size (gpt-image-2) |
|---|---|---|---|---|
| `landscape` | `landscape_16_9` | `16:9` | `1536x1024` | `landscape_4_3` (1024×768) |
| `square` | `square_hd` | `1:1` | `1024x1024` | `square_hd` (1024×1024) |
| `portrait` | `portrait_16_9` | `9:16` | `1024x1536` | `portrait_4_3` (768×1024) |

GPT Image 2 映射到 4:3 预设而非 16:9，因为它的最小像素数为 655,360——`landscape_16_9` 预设（1024×576 = 589,824）会被拒绝。

这个转换发生在 `_build_fal_payload()` 中——Agent 代码永远不需要知道不同模型的 schema 差异。

## 自动放大 {#automatic-upscaling}

通过 FAL 的 **Clarity Upscaler** 进行放大，按模型分别控制：

| 模型 | 是否放大？ | 原因 |
|---|---|---|
| `fal-ai/flux-2-pro` | ✓ | 向后兼容（曾是预选器默认值） |
| 其他所有模型 | ✗ | 快速模型会失去其亚秒级价值；高分辨率模型不需要 |

当执行放大时，使用以下设置：

| 设置项 | 值 |
|---|---|
| 放大倍数 | 2× |
| 创造力 | 0.35 |
| 相似度 | 0.6 |
| 引导尺度 | 4 |
| 推理步数 | 18 |

如果放大失败（网络问题、速率限制），会自动返回原始图片。

## 内部工作原理 {#how-it-works-internally}

1. **模型解析** — `_resolve_fal_model()` 从 `config.yaml` 读取 `image_gen.model`，回退到 `FAL_IMAGE_MODEL` 环境变量，最后回退到 `fal-ai/flux-2/klein/9b`。
2. **载荷构建** — `_build_fal_payload()` 将你的 `aspect_ratio` 转换为模型的原生格式（预设枚举、宽高比枚举或 GPT 字面量），合并模型的默认参数，应用调用方的覆盖值，然后过滤到模型支持的 `supports` 白名单，确保不会发送不支持的键。
3. **提交** — `_submit_fal_request()` 通过直接 FAL 凭据或托管的 Nous 网关进行路由。
4. **放大** — 仅当模型的元数据中 `upscale: True` 时执行。
5. **交付** — 最终图片 URL 返回给 Agent，Agent 会发出一个 `MEDIA:&lt;url&gt;` 标签，平台适配器将其转换为原生媒体。

## 调试 {#debugging}

启用调试日志：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志会写入 `./logs/image_tools_debug_&lt;session_id&gt;.json`，包含每次调用的详细信息（模型、参数、耗时、错误）。

## 平台交付 {#platform-delivery}

| 平台 | 交付方式 |
|---|---|
| **CLI** | 图片 URL 以 markdown 格式 `![](url)` 打印——点击即可打开 |
| **Telegram** | 以提示词作为标题的图片消息 |
| **Discord** | 嵌入在消息中 |
| **Slack** | 由 Slack 展开 URL |
| **WhatsApp** | 媒体消息 |
| **其他** | 纯文本 URL |
## 限制 {#limitations}

- **需要 FAL 凭据**（直接使用 `FAL_KEY` 或 Nous 订阅）
- **仅支持文本生成图像** — 不支持通过此工具进行图像修复（inpainting）、图像到图像（img2img）或编辑
- **临时 URL** — FAL 返回托管的 URL，这些 URL 会在数小时/天后过期；如有需要请本地保存
- **按模型约束** — 某些模型不支持 `seed`、`num_inference_steps` 等参数。`supports` 过滤器会静默丢弃不支持的参数；这是预期行为
