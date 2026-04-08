---
title: 图像生成
description: 使用 FLUX 2 Pro 生成高质量图像，并通过 FAL.ai 自动放大。
sidebar_label: 图像生成
sidebar_position: 6
---

# 图像生成

Hermes Agent 可以根据文本提示词生成图像。它使用 FAL.ai 的 **FLUX 2 Pro** 模型，并自动通过 **Clarity Upscaler** 进行 2 倍放大，以提升图像质量。

## 设置

### 获取 FAL API Key

1. 在 [fal.ai](https://fal.ai/) 注册账号
2. 从控制面板生成一个 API key

### 配置 Key

```bash
# 添加到 ~/.hermes/.env
FAL_KEY=your-fal-api-key-here
```

### 安装客户端库

```bash
pip install fal-client
```

:::info
只要设置了 `FAL_KEY`，图像生成工具就会自动启用。无需额外的工具集配置。
:::

## 工作原理

当你要求 Hermes 生成图像时：

1. **生成** — 你的提示词被发送到 FLUX 2 Pro 模型 (`fal-ai/flux-2-pro`)
2. **放大** — 生成的图像会自动使用 Clarity Upscaler (`fal-ai/clarity-upscaler`) 进行 2 倍放大
3. **交付** — 返回放大后的图像 URL

如果由于任何原因导致放大失败，系统将返回原始图像作为备选方案。

## 使用方法

只需直接要求 Hermes 创建图像：

```
生成一张带有樱花的宁静山水景观图
```

```
创作一张栖息在古老树枝上的智慧老猫头鹰肖像
```

```
给我画一个拥有飞行汽车和霓虹灯的未来主义城市景观
```

## 参数

`image_generate_tool` 接受以下参数：

| 参数 | 默认值 | 范围 | 描述 |
|-----------|---------|-------|-------------|
| `prompt` | *(必填)* | — | 所需图像的文本描述 |
| `aspect_ratio` | `"landscape"` | `landscape`, `square`, `portrait` | 图像纵横比 |
| `num_inference_steps` | `50` | 1–100 | 去噪步数（越多 = 质量越高，速度越慢） |
| `guidance_scale` | `4.5` | 0.1–20.0 | 遵循提示词的紧密程度 |
| `num_images` | `1` | 1–4 | 要生成的图像数量 |
| `output_format` | `"png"` | `png`, `jpeg` | 图像文件格式 |
| `seed` | *(随机)* | 任何整数 | 用于重现结果的随机种子 |

## 纵横比

该工具使用简化的纵横比名称，这些名称会映射到 FLUX 2 Pro 的图像尺寸：

| 纵横比 | 映射至 | 最佳用途 |
|-------------|---------|----------|
| `landscape` | `landscape_16_9` | 壁纸、横幅、场景 |
| `square` | `square_hd` | 头像、社交媒体帖子 |
| `portrait` | `portrait_16_9` | 角色艺术、手机壁纸 |

:::tip
你也可以直接使用原始的 FLUX 2 Pro 尺寸预设：`square_hd`、`square`、`portrait_4_3`、`portrait_16_9`、`landscape_4_3`、`landscape_16_9`。同时也支持最高 2048x2048 的自定义尺寸。
:::

## 自动放大

每张生成的图像都会使用 FAL.ai 的 Clarity Upscaler 自动放大 2 倍，设置如下：

| 设置项 | 数值 |
|---------|-------|
| 放大倍率 | 2x |
| 创造力 (Creativity) | 0.35 |
| 相似度 (Resemblance) | 0.6 |
| 引导比例 (Guidance Scale) | 4 |
| 推理步数 (Inference Steps) | 18 |
| 正向提示词 | `"masterpiece, best quality, highres"` + 你的原始提示词 |
| 反向提示词 | `"(worst quality, low quality, normal quality:2)"` |

放大器在保持原始构图的同时增强了细节和分辨率。如果放大器失败（网络问题、速率限制），则会自动返回原始分辨率的图像。

## 提示词示例

这里有一些可以尝试的有效提示词：

```
一张街拍照片，一位留着粉色波波头、画着大胆眼线的女性
```

```
带有玻璃幕墙的现代建筑，夕阳的光照效果
```

```
色彩鲜艳、带有几何图案的抽象艺术
```

```
栖息在古老树枝上的智慧老猫头鹰肖像
```

```
拥有飞行汽车和霓虹灯的未来主义城市景观
```

## 调试

为图像生成启用调试日志：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志将保存到 `./logs/image_tools_debug_<session_id>.json`，其中包含每个生成请求的详细信息、参数、耗时以及任何错误。

## 安全设置

图像生成工具默认在禁用安全检查的情况下运行（`safety_tolerance: 5`，最宽松的设置）。这是在代码层面配置的，用户不可调节。

## 平台交付

生成的图像根据平台的不同以不同方式交付：

| 平台 | 交付方式 |
|----------|----------------|
| **CLI** | 图像 URL 以 Markdown 格式打印 `![description](url)` — 点击可在浏览器中打开 |
| **Telegram** | 图像作为照片消息发送，提示词作为说明文字 |
| **Discord** | 图像嵌入在消息中 |
| **Slack** | 消息中的图像 URL（Slack 会自动展开预览） |
| **WhatsApp** | 图像作为媒体消息发送 |
| **其他平台** | 纯文本形式的图像 URL |

Agent 在响应中使用 `MEDIA:<url>` 语法，平台适配器会将其转换为相应的格式。

## 局限性

- **需要 FAL API key** — 图像生成会在你的 FAL.ai 账户中产生 API 费用
- **不支持图像编辑** — 仅支持文本生成图像（text-to-image），不支持局部重绘（inpainting）或图生图（img2img）
- **基于 URL 的交付** — 图像以临时的 FAL.ai URL 形式返回，不会保存在本地。URL 会在一段时间后（通常为几小时）失效
- **放大增加延迟** — 自动 2 倍放大步骤会增加处理时间
- **单次请求最多 4 张图像** — `num_images` 上限为 4
