---
title: 图像生成
description: 通过 FAL.ai 生成图像 —— 支持 8 种模型，包括 FLUX 2、GPT-Image、Nano Banana Pro、Ideogram、Recraft V4 Pro 等，可通过 `hermes tools` 选择。
sidebar_label: 图像生成
sidebar_position: 6
---

# 图像生成 {#image-generation}

Hermes Agent 通过 FAL.ai 从文本提示词生成图像。默认支持八种模型，每种在速度、质量和成本之间有不同的权衡。用户可以通过 `hermes tools` 配置活动模型，该设置会持久保存在 `config.yaml` 中。

## 支持的模型 {#supported-models}

| 模型 | 速度 | 优势 | 价格 |
|---|---|---|---|
| `fal-ai/flux-2/klein/9b` *(默认)* | `&lt;1s` | 快速，文字清晰 | $0.006/MP |
| `fal-ai/flux-2-pro` | ~6s | 影棚级照片真实感 | $0.03/MP |
| `fal-ai/z-image/turbo` | ~2s | 双语（英/中），60亿参数 | $0.005/MP |
| `fal-ai/nano-banana-pro` | ~8s | Gemini 3 Pro，推理深度，文字渲染 | $0.15/张 (1K) |
| `fal-ai/gpt-image-1.5` | ~15s | 提示词遵循度高 | $0.034/张 |
| `fal-ai/ideogram/v3` | ~5s | 最佳字体排版 | $0.03–0.09/张 |
| `fal-ai/recraft/v4/pro/text-to-image` | ~8s | 设计，品牌系统，生产就绪 | $0.25/张 |
| `fal-ai/qwen-image` | ~12s | 基于 LLM，复杂文本 | $0.02/MP |

价格为撰写本文时 FAL 的定价；请查看 [fal.ai](https://fal.ai/) 获取最新价格。

## 设置 {#setup}

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，可以通过 **[工具网关](tool-gateway.md)** 使用图像生成功能，无需 FAL API 密钥。您的模型选择在两种路径下都会保持。

如果托管网关针对特定模型返回 `HTTP 4xx` 错误，表示该模型尚未在门户端代理 —— Agent 会告知您此情况，并提供补救步骤（设置 `FAL_KEY` 以直接访问，或选择其他模型）。
:::

<a id="nous-subscribers"></a>
### 获取 FAL API 密钥 {#get-a-fal-api-key}

1.  在 [fal.ai](https://fal.ai/) 注册
2.  从您的控制面板生成 API 密钥

### 配置并选择模型 {#configure-and-pick-a-model}

运行工具命令：

```bash
hermes tools
```

导航到 **🎨 图像生成**，选择您的后端（Nous 订阅或 FAL.ai），然后选择器会以列对齐的表格显示所有支持的模型 —— 使用方向键导航，按 Enter 键选择：

```
  Model                          Speed    Strengths                    Price
  fal-ai/flux-2/klein/9b         &lt;1s      Fast, crisp text             $0.006/MP   ← currently in use
  fal-ai/flux-2-pro              ~6s      Studio photorealism          $0.03/MP
  fal-ai/z-image/turbo           ~2s      Bilingual EN/CN, 6B          $0.005/MP
  ...
```

您的选择将保存到 `config.yaml`：

```yaml
image_gen:
  model: fal-ai/flux-2/klein/9b
  use_gateway: false            # 如果使用 Nous 订阅则为 true
```

### GPT-Image 质量 {#gpt-image-quality}

`fal-ai/gpt-image-1.5` 的请求质量固定为 `medium`（约 $0.034/张，1024×1024）。我们没有将 `low` / `high` 等级作为面向用户的选项公开，以便 Nous Portal 的计费对所有用户保持可预测性 —— 不同等级之间的成本差异约为 22 倍。如果您想要更便宜的 GPT-Image 选项，请选择其他模型；如果您想要更高质量，请使用 Klein 9B 或 Imagen 级别的模型。

## 使用方式 {#usage}

面向 Agent 的接口模式有意设计得非常简洁 —— 模型会直接使用您配置好的设置：

```
生成一幅宁静的山景，带有樱花
```

```
创建一张方形肖像，描绘一只睿智的老猫头鹰 —— 使用字体排版模型
```

```
为我制作一幅未来主义城市景观，横向构图
```

## 宽高比 {#aspect-ratios}

从 Agent 的角度看，每个模型都接受相同的三种宽高比。在内部，每个模型的原生尺寸规格会自动填充：

| Agent 输入 | image_size (flux/z-image/qwen/recraft/ideogram) | aspect_ratio (nano-banana-pro) | image_size (gpt-image) |
|---|---|---|---|
| `landscape` | `landscape_16_9` | `16:9` | `1536x1024` |
| `square` | `square_hd` | `1:1` | `1024x1024` |
| `portrait` | `portrait_16_9` | `9:16` | `1024x1536` |

这个转换过程在 `_build_fal_payload()` 中完成 —— Agent 代码无需了解每个模型的模式差异。

## 自动超分辨率 {#automatic-upscaling}

通过 FAL 的 **Clarity Upscaler** 进行超分辨率是按模型控制的：

| 模型 | 是否超分？ | 原因 |
|---|---|---|
| `fal-ai/flux-2-pro` | ✓ | 向后兼容（曾是选择器出现前的默认设置） |
| 所有其他模型 | ✗ | 快速模型会失去其亚秒级的价值主张；高分辨率模型不需要它 |
当执行放大时，会使用以下设置：

| 设置项 | 值 |
|---|---|
| 放大倍数 | 2× |
| 创意度 | 0.35 |
| 相似度 | 0.6 |
| 引导尺度 | 4 |
| 推理步数 | 18 |

如果放大失败（网络问题、速率限制），系统会自动返回原始图像。

## 内部工作原理 {#how-it-works-internally}

1.  **模型解析** — `_resolve_fal_model()` 从 `config.yaml` 读取 `image_gen.model`，回退到 `FAL_IMAGE_MODEL` 环境变量，最后回退到 `fal-ai/flux-2/klein/9b`。
2.  **载荷构建** — `_build_fal_payload()` 将你的 `aspect_ratio` 转换为模型的原生格式（预设枚举、宽高比枚举或 GPT 字面量），合并模型的默认参数，应用调用方的任何覆盖，然后根据模型的 `supports` 白名单进行过滤，确保不支持的键不会被发送。
3.  **提交** — `_submit_fal_request()` 通过直接的 FAL 凭证或托管的 Nous 网关进行路由。
4.  **放大** — 仅当模型的元数据包含 `upscale: True` 时才会运行。
5.  **交付** — 最终图像 URL 返回给 Agent，Agent 会发出一个 `MEDIA:&lt;url&gt;` 标签，平台适配器会将其转换为原生媒体。

## 调试 {#debugging}

启用调试日志：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志会输出到 `./logs/image_tools_debug_&lt;session_id&gt;.json`，包含每次调用的详细信息（模型、参数、耗时、错误）。

## 平台交付 {#platform-delivery}

| 平台 | 交付方式 |
|---|---|
| **CLI** | 图像 URL 以 Markdown `![](url)` 格式打印 — 点击即可打开 |
| **Telegram** | 以提示词为标题的图片消息 |
| **Discord** | 嵌入在消息中 |
| **Slack** | 由 Slack 展开 URL |
| **WhatsApp** | 媒体消息 |
| **其他** | 纯文本 URL |

## 限制 {#limitations}

-   **需要 FAL 凭证**（直接的 `FAL_KEY` 或 Nous 订阅）
-   **仅限文生图** — 此工具不支持修复、图生图或编辑
-   **临时 URL** — FAL 返回的托管 URL 会在数小时/数天后过期；如有需要请保存到本地
-   **模型特定约束** — 某些模型不支持 `seed`、`num_inference_steps` 等参数。`supports` 过滤器会静默丢弃不支持的参数；这是预期行为
