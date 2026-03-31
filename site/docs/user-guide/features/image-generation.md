---
title: 图像生成
description: 使用 FLUX 2 Pro 模型生成高质量图像，并通过 FAL.ai 自动进行超分辨率放大。
sidebar_label: 图像生成
sidebar_position: 6
---

# 图像生成

Hermes Agent 可以使用 FAL.ai 的 **FLUX 2 Pro** 模型根据文本提示生成图像，并通过 **Clarity Upscaler** 自动进行 2 倍超分辨率放大以提升画质。

## 设置

### 获取 FAL API 密钥

1.  在 [fal.ai](https://fal.ai/) 注册账号
2.  从你的控制台生成一个 API 密钥

### 配置密钥

```bash
# 添加到 ~/.hermes/.env 文件中
FAL_KEY=your-fal-api-key-here
```

### 安装客户端库

```bash
pip install fal-client
```

:::info
当设置了 `FAL_KEY` 环境变量后，图像生成工具会自动启用。无需额外的工具集配置。
:::

## 工作原理

当你要求 Hermes 生成图像时：

1.  **生成** — 你的提示词会被发送到 FLUX 2 Pro 模型 (`fal-ai/flux-2-pro`)
2.  **放大** — 生成的图像会自动使用 Clarity Upscaler (`fal-ai/clarity-upscaler`) 进行 2 倍放大
3.  **交付** — 返回放大后的图像 URL

如果因任何原因放大失败，则会返回原始图像作为备选方案。

## 使用方法

直接让 Hermes 创建图像即可：

```
生成一幅宁静的山景，点缀着樱花
```

```
创作一幅栖息在古老树枝上的智慧老猫头鹰的肖像画
```

```
为我制作一幅未来主义城市景观，要有飞行汽车和霓虹灯
```

## 参数

`image_generate_tool` 接受以下参数：

| 参数 | 默认值 | 范围 | 描述 |
|-----------|---------|-------|-------------|
| `prompt` | *(必填)* | — | 期望图像的文本描述 |
| `aspect_ratio` | `"landscape"` | `landscape`, `square`, `portrait` | 图像宽高比 |
| `num_inference_steps` | `50` | 1–100 | 去噪步数（数值越大质量越高，速度越慢） |
| `guidance_scale` | `4.5` | 0.1–20.0 | 遵循提示词的严格程度 |
| `num_images` | `1` | 1–4 | 要生成的图像数量 |
| `output_format` | `"png"` | `png`, `jpeg` | 图像文件格式 |
| `seed` | *(随机)* | 任意整数 | 用于生成可重复结果的随机种子 |

## 宽高比

该工具使用简化的宽高比名称，它们会映射到 FLUX 2 Pro 的图像尺寸：

| 宽高比 | 映射到 | 最适合 |
|-------------|---------|----------|
| `landscape` | `landscape_16_9` | 壁纸、横幅、场景 |
| `square` | `square_hd` | 个人资料图片、社交媒体帖子 |
| `portrait` | `portrait_16_9` | 角色艺术、手机壁纸 |

:::tip
你也可以直接使用 FLUX 2 Pro 的原始尺寸预设：`square_hd`, `square`, `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9`。同时支持最大 2048x2048 的自定义尺寸。
:::

## 自动超分辨率放大

每张生成的图像都会使用 FAL.ai 的 Clarity Upscaler 自动进行 2 倍放大，设置如下：

| 设置项 | 值 |
|---------|-------|
| 放大倍数 | 2x |
| 创造力 | 0.35 |
| 相似度 | 0.6 |
| 引导尺度 | 4 |
| 推理步数 | 18 |
| 正向提示词 | `"masterpiece, best quality, highres"` + 你的原始提示词 |
| 负向提示词 | `"(worst quality, low quality, normal quality:2)"` |

超分放大器在保持原始构图的同时增强了细节和分辨率。如果放大失败（网络问题、速率限制），则会自动返回原始分辨率的图像。

## 示例提示词

以下是一些可以尝试的有效提示词：

```
一张抓拍的街头照片，一位粉色波波头、眼线大胆的女性
```

```
具有玻璃幕墙的现代建筑，日落光线
```

```
色彩鲜艳、带有几何图案的抽象艺术
```

```
栖息在古老树枝上的智慧老猫头鹰的肖像
```

```
拥有飞行汽车和霓虹灯的未来主义城市景观
```

## 调试

启用图像生成的调试日志：

```bash
export IMAGE_TOOLS_DEBUG=true
```

调试日志会保存到 `./logs/image_tools_debug_<session_id>.json` 文件中，其中包含每个生成请求的详细信息、参数、时间以及任何错误。

## 安全设置

图像生成工具默认在禁用安全检查的情况下运行（`safety_tolerance: 5`，最宽松的设置）。这是在代码级别配置的，用户无法调整。

## 限制

-   **需要 FAL API 密钥** — 图像生成会在你的 FAL.ai 账户上产生 API 费用
-   **不支持图像编辑** — 仅支持文生图，不支持局部重绘或图生图
-   **基于 URL 的交付** — 图像以临时的 FAL.ai URL 形式返回，不会本地保存
-   **超分放大增加延迟** — 自动 2 倍放大步骤会增加处理时间
-   **每次请求最多 4 张图像** — `num_images` 上限为 4
