---
sidebar_position: 2
title: "在 Mac 上运行本地 LLM"
description: "在 macOS 上使用 llama.cpp 或 MLX 搭建兼容 OpenAI 的本地 LLM 服务器，涵盖模型选择、内存优化以及 Apple Silicon 上的真实基准测试"
---

# 在 Mac 上运行本地 LLM

本指南将带你通过兼容 OpenAI 的 API 在 macOS 上运行本地 LLM 服务器。你将获得完全的隐私保护、零 API 成本，以及在 Apple Silicon 上出人意料的优秀性能。

我们涵盖了两种后端：

| 后端 | 安装方式 | 擅长领域 | 格式 |
|---------|---------|---------|--------|
| **llama.cpp** | `brew install llama.cpp` | 最快的前首字时间 (TTFT)，量化 KV 缓存节省内存 | GGUF |
| **omlx** | [omlx.ai](https://omlx.ai) | 最快的 Token 生成速度，原生 Metal 优化 | MLX (safetensors) |

两者都提供兼容 OpenAI 的 `/v1/chat/completions` 接口。Hermes 可以与其中任何一个配合使用 —— 只需将其指向 `http://localhost:8080` 或 `http://localhost:8000` 即可。

:::info 仅限 Apple Silicon
本指南针对搭载 Apple Silicon（M1 及更高版本）的 Mac。Intel 芯片的 Mac 可以运行 llama.cpp，但没有 GPU 加速 —— 性能会明显变慢。
:::

---

## 选择模型

入门阶段，我们推荐 **Qwen3.5-9B** —— 这是一个强大的推理模型，通过量化后可以轻松放入 8GB 以上的统一内存中。

| 变体 | 磁盘占用 | 所需 RAM (128K 上下文) | 后端 |
|---------|-------------|---------------------------|---------|
| Qwen3.5-9B-Q4_K_M (GGUF) | 5.3 GB | 使用量化 KV 缓存约 10 GB | llama.cpp |
| Qwen3.5-9B-mlx-lm-mxfp4 (MLX) | ~5 GB | 约 12 GB | omlx |

**内存估算经验法则：** 模型大小 + KV 缓存。一个 9B Q4 模型约为 5 GB。在 128K 上下文下，使用 Q4 量化的 KV 缓存会增加约 4-5 GB。如果使用默认的 (f16) KV 缓存，这个数字会激增到约 16 GB。llama.cpp 中的量化 KV 缓存参数是内存受限系统的关键技巧。

对于更大的模型（27B, 35B），你需要 32 GB 以上的统一内存。对于 8-16 GB 的机器，9B 模型是最佳平衡点。

---

## 选项 A：llama.cpp

llama.cpp 是移植性最强的本地 LLM 运行时。在 macOS 上，它开箱即用地使用 Metal 进行 GPU 加速。

### 安装

```bash
brew install llama.cpp
```

这将在全局提供 `llama-server` 命令。

### 下载模型

你需要 GGUF 格式的模型。最简单的来源是通过 `huggingface-cli` 从 Hugging Face 获取：

```bash
brew install huggingface-cli
```

然后下载：

```bash
huggingface-cli download unsloth/Qwen3.5-9B-GGUF Qwen3.5-9B-Q4_K_M.gguf --local-dir ~/models
```

:::tip 受限模型
Hugging Face 上的某些模型需要身份验证。如果遇到 401 或 404 错误，请先运行 `huggingface-cli login`。
:::

### 启动服务器

```bash
llama-server -m ~/models/Qwen3.5-9B-Q4_K_M.gguf \
  -ngl 99 \
  -c 131072 \
  -np 1 \
  -fa on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --host 0.0.0.0
```

以下是各参数的作用：

| 参数 | 用途 |
|------|---------|
| `-ngl 99` | 将所有层卸载到 GPU (Metal)。使用一个较大的数字确保没有任何层留在 CPU 上。 |
| `-c 131072` | 上下文窗口大小（128K tokens）。如果内存不足，请调小此值。 |
| `-np 1` | 并行槽位数量。单人使用请保持为 1 —— 更多槽位会瓜分你的内存预算。 |
| `-fa on` | Flash attention。减少内存占用并加速长上下文推理。 |
| `--cache-type-k q4_0` | 将 Key 缓存量化为 4-bit。**这是节省内存的大招。** |
| `--cache-type-v q4_0` | 将 Value 缓存量化为 4-bit。配合上述参数，相比 f16 可减少约 75% 的 KV 缓存内存占用。 |
| `--host 0.0.0.0` | 监听所有接口。如果不需要网络访问，请使用 `127.0.0.1`。 |

当你看到以下内容时，服务器就准备就绪了：

```
main: server is listening on http://0.0.0.0:8080
srv  update_slots: all slots are idle
```

### 针对受限系统的内存优化

`--cache-type-k q4_0 --cache-type-v q4_0` 参数是内存有限系统最重要的优化手段。以下是 128K 上下文下的影响：

| KV 缓存类型 | KV 缓存内存占用 (128K 上下文, 9B 模型) |
|---------------|--------------------------------------|
| f16 (默认) | ~16 GB |
| q8_0 | ~8 GB |
| **q4_0** | **~4 GB** |

在 8 GB 的 Mac 上，请使用 `q4_0` KV 缓存并将上下文减少到 `-c 32768` (32K)。在 16 GB 的机器上，你可以从容运行 128K 上下文。在 32 GB 以上的机器上，你可以运行更大的模型或多个并行槽位。

如果仍然内存不足，请先减小上下文大小 (`-c`)，然后尝试更小的量化版本（例如 Q3_K_M 而非 Q4_K_M）。

### 测试

```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-Q4_K_M.gguf",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }' | jq .choices[0].message.content
```

### 获取模型名称

如果你忘记了模型名称，可以查询 models 接口：

```bash
curl -s http://localhost:8080/v1/models | jq '.data[].id'
```

---

## 选项 B：通过 omlx 使用 MLX

[omlx](https://omlx.ai) 是一个管理和运行 MLX 模型的 macOS 原生应用。MLX 是 Apple 自己的机器学习框架，专门针对 Apple Silicon 的统一内存架构进行了优化。

### 安装

从 [omlx.ai](https://omlx.ai) 下载并安装。它提供了一个用于模型管理的 GUI 和一个内置服务器。

### 下载模型

使用 omlx 应用浏览并下载模型。搜索 `Qwen3.5-9B-mlx-lm-mxfp4` 并下载。模型存储在本地（通常在 `~/.omlx/models/`）。

### 启动服务器

omlx 默认在 `http://127.0.0.1:8000` 提供服务。通过应用界面启动服务，或者使用 CLI（如果可用）。

### 测试

```bash
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-mlx-lm-mxfp4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }' | jq .choices[0].message.content
```

### 列出可用模型

omlx 可以同时提供多个模型：

```bash
curl -s http://127.0.0.1:8000/v1/models | jq '.data[].id'
```

---

## 基准测试：llama.cpp vs MLX

两个后端在同一台机器（Apple M5 Max，128 GB 统一内存）上运行相同的模型 (Qwen3.5-9B)，并采用相当的量化水平（GGUF 为 Q4_K_M，MLX 为 mxfp4）。测试包含五个不同的提示词，每个运行三次，后端按顺序测试以避免资源竞争。

### 结果

| 指标 | llama.cpp (Q4_K_M) | MLX (mxfp4) | 胜出者 |
|--------|-------------------|-------------|--------|
| **TTFT (平均)** | **67 ms** | 289 ms | llama.cpp (快 4.3 倍) |
| **TTFT (p50)** | **66 ms** | 286 ms | llama.cpp (快 4.3 倍) |
| **生成速度 (平均)** | 70 tok/s | **96 tok/s** | MLX (快 37%) |
| **生成速度 (p50)** | 70 tok/s | **96 tok/s** | MLX (快 37%) |
| **总耗时 (512 tokens)** | 7.3s | **5.5s** | MLX (快 25%) |

### 结果分析

- **llama.cpp** 在提示词处理方面表现出色 —— 其 flash attention + 量化 KV 缓存流水线让你在约 66ms 内就能获得第一个 token。如果你正在构建对感知响应速度要求较高的交互式应用（聊天机器人、自动补全），这是一个显著的优势。

- **MLX** 一旦开始生成，速度会快约 37%。对于批处理任务、长文本生成或任何总完成时间比初始延迟更重要的任务，MLX 完成得更快。

- 两个后端都**极其稳定** —— 不同运行之间的差异微乎其微。你可以信赖这些数据。

### 你该选哪一个？

| 使用场景 | 推荐 |
|----------|---------------|
| 交互式聊天、低延迟工具 | llama.cpp |
| 长文本生成、批量处理 | MLX (omlx) |
| 内存受限 (8-16 GB) | llama.cpp (量化 KV 缓存无可匹敌) |
| 同时运行多个模型 | omlx (内置多模型支持) |
| 最大兼容性 (也支持 Linux) | llama.cpp |

---

## 连接到 Hermes

本地服务器运行后：

```bash
hermes model
```

选择 **Custom endpoint** 并按照提示操作。它会询问 Base URL 和模型名称 —— 请使用你上面配置的后端对应的值。
